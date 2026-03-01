import time
from typing import Any
from langgraph.graph import END, StateGraph
from agent.models import ConversationState
from agent.nodes import collect_info, confirm_ticket, handle_error, submit_ticket
from agent.session_repository import AbstractSessionRepository

def _route_collect(state: ConversationState) -> str:
    return "confirm_ticket" if state.stage == "confirm" else END

def _route_confirm(state: ConversationState) -> str:
    if state.stage == "submit": return "submit_ticket"
    if state.stage == "collect": return "collect_info"
    return END

def _route_submit(state: ConversationState) -> str:
    return "handle_error" if state.stage == "error" else END

def _route_error(state: ConversationState) -> str:
    return "submit_ticket" if state.stage == "submit" else END

def _build_graph() -> Any:
    g = StateGraph(ConversationState)
    g.add_node("collect_info", collect_info)
    g.add_node("confirm_ticket", confirm_ticket)
    g.add_node("submit_ticket", submit_ticket)
    g.add_node("handle_error", handle_error)
    g.set_entry_point("collect_info")
    g.add_conditional_edges("collect_info", _route_collect, {"confirm_ticket": "confirm_ticket", END: END})
    g.add_conditional_edges("confirm_ticket", _route_confirm, {"submit_ticket": "submit_ticket", "collect_info": "collect_info", END: END})
    g.add_conditional_edges("submit_ticket", _route_submit, {"handle_error": "handle_error", END: END})
    g.add_conditional_edges("handle_error", _route_error, {"submit_ticket": "submit_ticket", END: END})
    return g.compile()

compiled_graph = _build_graph()

def run_turn(session_id: str, user_message: str, repository: AbstractSessionRepository) -> str:
    state = repository.get(session_id)
    if state is None:
        state = ConversationState(session_id=session_id, history=[], collected={}, stage="collect", last_active=time.time())
    state.history.append({"role": "user", "content": user_message})
    result_state: ConversationState = compiled_graph.invoke(state)
    repository.save(result_state)
    for entry in reversed(result_state.history):
        if entry.get("role") == "assistant": return entry["content"]
    return ""
