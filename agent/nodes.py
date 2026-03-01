import json, os, time
from typing import Any
from agent.field_validation import validate_incident_fields
from agent.models import ConversationState, IncidentFields, Urgency
from agent.servicenow_tool import create_incident
from agent.urgency_mapper import map_urgency

def _build_llm() -> Any:
    provider = os.environ.get("LLM_PROVIDER", "bedrock").lower()
    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model="gpt-4o-mini", temperature=0)
    from langchain_aws import ChatBedrockConverse
    return ChatBedrockConverse(model="anthropic.claude-3-5-haiku-20241022-v1:0", temperature=0)

_llm = None
def _get_llm() -> Any:
    global _llm
    if _llm is None: _llm = _build_llm()
    return _llm

_COLLECT_INFO_SYSTEM_PROMPT = """You are an IT helpdesk assistant helping create a ServiceNow ticket.
Extract these fields: short_description, description, urgency, category.
Respond ONLY with JSON: {"extracted": {"short_description": "<val or null>", "description": "<val or null>", "urgency": "<val or null>", "category": "<val or null>"}, "reply": "<message>"}
Do NOT invent values. Ask for missing fields. Keep replies concise."""

def collect_info(state: ConversationState) -> ConversationState:
    llm = _get_llm()
    from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
    messages = [SystemMessage(content=_COLLECT_INFO_SYSTEM_PROMPT)]
    for entry in state.history:
        role, content = entry.get("role", "user"), entry.get("content", "")
        messages.append(AIMessage(content=content) if role == "assistant" else HumanMessage(content=content))
    if state.collected:
        messages.append(HumanMessage(content=f"[Fields so far: {json.dumps({k: str(v) for k, v in state.collected.items()})}]"))
    response = llm.invoke(messages)
    raw = response.content if hasattr(response, "content") else str(response)
    extracted, reply = {}, ""
    try:
        cleaned = raw.strip()
        if cleaned.startswith("```"): cleaned = cleaned.split("```")[1]; cleaned = cleaned[4:] if cleaned.startswith("json") else cleaned
        parsed = json.loads(cleaned.strip())
        extracted, reply = parsed.get("extracted", {}), parsed.get("reply", "")
    except (json.JSONDecodeError, ValueError): reply = raw
    for k, v in extracted.items():
        if v is not None and v != "": state.collected[k] = v
    if "urgency" in state.collected and not isinstance(state.collected["urgency"], Urgency):
        state.collected["urgency"] = map_urgency(str(state.collected["urgency"]))
    missing = validate_incident_fields(state.collected)
    if not missing:
        state.stage = "confirm"
        if not reply: reply = "I have all the info. Shall I submit this ticket?"
    else:
        state.stage = "collect"
        if not reply: reply = f"Could you provide: {', '.join(missing)}?"
    state.history.append({"role": "assistant", "content": reply})
    state.last_active = time.time()
    return state

_CONFIRM_KW = {"yes", "confirm", "submit", "ok", "okay", "go ahead", "proceed", "sure", "yep", "yup"}
_CHANGE_KW = {"no", "change", "edit", "update", "modify", "different", "wrong", "incorrect", "back"}

def confirm_ticket(state: ConversationState) -> ConversationState:
    last_msg = next((e.get("content", "").lower().strip() for e in reversed(state.history) if e.get("role") == "user"), "")
    confirmed = any(kw in last_msg for kw in _CONFIRM_KW)
    wants_change = any(kw in last_msg for kw in _CHANGE_KW)
    c = state.collected
    u = c.get("urgency")
    ud = u.name.capitalize() if isinstance(u, Urgency) else str(u) if u else "Not set"
    summary = f"Summary:\n  Short desc: {c.get('short_description', 'N/A')}\n  Description: {c.get('description', 'N/A')}\n  Urgency: {ud}\n  Category: {c.get('category', 'N/A')}"
    if confirmed and not wants_change:
        state.stage = "submit"; reply = f"{summary}\n\nSubmitting now..."
    elif wants_change:
        state.stage = "collect"; reply = "What would you like to change?"
    else:
        reply = f"{summary}\n\nSubmit this ticket? (yes/no)"
    state.history.append({"role": "assistant", "content": reply})
    state.last_active = time.time()
    return state

def submit_ticket(state: ConversationState) -> ConversationState:
    c = state.collected
    urgency = c.get("urgency")
    if not isinstance(urgency, Urgency): urgency = map_urgency(str(urgency)) if urgency else Urgency.MEDIUM
    fields = IncidentFields(short_description=c.get("short_description", ""), description=c.get("description", ""), urgency=urgency, category=c.get("category", ""))
    result = create_incident(fields)
    if result.success:
        state.stage = "done"
        reply = f"Ticket created! Number: {result.ticket_number or 'N/A'}\nAnything else?"
    else:
        state.stage = "error"; state.collected["_error"] = result.error_message or "Unknown error"
        reply = "Could not create ticket. Retry or cancel?"
    state.history.append({"role": "assistant", "content": reply})
    state.last_active = time.time()
    return state

_RETRY_KW = {"retry", "try again", "yes", "yep", "sure", "ok", "go ahead"}
_CANCEL_KW = {"cancel", "no", "nope", "stop", "quit", "forget it", "never mind"}

def handle_error(state: ConversationState) -> ConversationState:
    error_msg = state.collected.get("_error", "Unknown error")
    last_msg = next((e.get("content", "").lower().strip() for e in reversed(state.history) if e.get("role") == "user"), "")
    wants_retry = any(kw in last_msg for kw in _RETRY_KW)
    wants_cancel = any(kw in last_msg for kw in _CANCEL_KW)
    if wants_retry and not wants_cancel:
        state.stage = "submit"; reply = "Retrying..."
    elif wants_cancel:
        state.stage = "done"; reply = "Cancelled. Let me know if you need anything else."
    else:
        reply = f"Error: {error_msg}\nRetry or cancel?"
    state.history.append({"role": "assistant", "content": reply})
    state.last_active = time.time()
    return state
