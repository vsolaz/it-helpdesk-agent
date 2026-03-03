"""AgentCore Runtime — IT Helpdesk Agent with ServiceNow integration."""

from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()
_agent = None
_sessions: dict[str, dict] = {}

REQUIRED_FIELDS = ("short_description", "description", "urgency", "category")
URGENCY_MAP = {
    "urgent": "1", "critical": "1", "asap": "1", "high": "1",
    "medium": "2", "normal": "2", "moderate": "2",
    "low": "3", "not urgent": "3", "whenever": "3",
}

def _map_urgency(text):
    for kw, val in URGENCY_MAP.items():
        if kw in text.lower().strip(): return val
    return "2"

def _get_missing(collected):
    return [f for f in REQUIRED_FIELDS if not collected.get(f)]

def _build_agent():
    import os, json
    from strands import Agent, tool
    from strands.models import BedrockModel

    @tool
    def check_ticket_fields(session_id: str) -> str:
        """Check which ticket fields are still missing."""
        collected = _sessions.get(session_id, {}).get("collected", {})
        missing = _get_missing(collected)
        if missing: return f"Missing: {', '.join(missing)}. Have: {json.dumps(collected)}"
        return f"All collected: {json.dumps(collected)}"

    @tool
    def save_ticket_field(session_id: str, field_name: str, field_value: str) -> str:
        """Save a ticket field. field_name: short_description, description, urgency, or category."""
        if field_name not in REQUIRED_FIELDS: return f"Invalid. Must be: {', '.join(REQUIRED_FIELDS)}"
        session = _sessions.setdefault(session_id, {"collected": {}})
        val = _map_urgency(field_value) if field_name == "urgency" else field_value
        session.setdefault("collected", {})[field_name] = val
        missing = _get_missing(session["collected"])
        if missing: return f"Saved {field_name}. Need: {', '.join(missing)}"
        return f"Saved. All ready: {json.dumps(session['collected'])}"

    @tool
    def create_servicenow_ticket(session_id: str) -> str:
        """Create a ServiceNow incident with collected fields."""
        import requests as req
        from requests.auth import HTTPBasicAuth
        collected = _sessions.get(session_id, {}).get("collected", {})
        missing = _get_missing(collected)
        if missing: return f"Cannot create. Missing: {', '.join(missing)}"
        inst = os.environ.get("SERVICENOW_INSTANCE_URL", "")
        user = os.environ.get("SERVICENOW_USERNAME", "")
        pwd = os.environ.get("SERVICENOW_PASSWORD", "")
        if not inst:
            try:
                import boto3
                sn = os.environ.get("SERVICENOW_SECRET_NAME", "helpdesk/servicenow")
                s = json.loads(boto3.client("secretsmanager", region_name="us-east-1").get_secret_value(SecretId=sn)["SecretString"])
                inst, user, pwd = s.get("instance_url",""), s.get("username",""), s.get("password","")
            except Exception as e: return f"Cred error: {e}"
        try:
            r = req.post(f"{inst.rstrip('/')}/api/now/table/incident", json={k: collected[k] for k in REQUIRED_FIELDS}, auth=HTTPBasicAuth(user, pwd), headers={"Accept": "application/json"}, timeout=(10, 20))
            if r.status_code == 201: return f"Ticket created! Number: {r.json().get('result',{}).get('number','N/A')}"
            return f"ServiceNow HTTP {r.status_code}"
        except Exception as e: return f"Failed: {e}"

    model_id = os.environ.get("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-6")
    return Agent(model=BedrockModel(model_id=model_id), tools=[check_ticket_fields, save_ticket_field, create_servicenow_ticket],
        system_prompt="You are an IT helpdesk assistant for Mapfre Insurance. Help users create ServiceNow tickets. Use check_ticket_fields, save_ticket_field, create_servicenow_ticket. Required: short_description, description, urgency (high/medium/low), category (hardware/software/network/access/email/other). Be conversational. Ask one question at a time. Confirm before creating.")

@app.entrypoint
def invoke(payload):
    global _agent
    if _agent is None: _agent = _build_agent()
    user_input = payload.get("prompt", "Hello")
    session_id = payload.get("session_id", "default")
    _sessions.setdefault(session_id, {"collected": {}})
    response = _agent(f"[Session: {session_id}] {user_input}")
    return response.message['content'][0]['text']

if __name__ == "__main__":
    app.run()
