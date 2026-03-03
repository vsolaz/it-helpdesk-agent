"""AWS Lambda handler — proxies requests to AgentCore Runtime with session pinning."""

import json
import os
import boto3

AGENT_ARN = os.environ.get(
    "AGENTCORE_AGENT_ARN",
    "arn:aws:bedrock-agentcore:us-east-1:903026258626:runtime/musa_helpdesk_strands-KaU5kjAIQs",
)
REGION = os.environ.get("AWS_REGION", "us-east-1")
SESSIONS_TABLE = os.environ.get("SESSIONS_TABLE", "helpdesk-sessions")

_agentcore_client = None
_ddb = None

def _get_agentcore():
    global _agentcore_client
    if _agentcore_client is None:
        _agentcore_client = boto3.client("bedrock-agentcore", region_name=REGION)
    return _agentcore_client

def _get_ddb():
    global _ddb
    if _ddb is None:
        _ddb = boto3.resource("dynamodb", region_name=REGION).Table(SESSIONS_TABLE)
    return _ddb

def _get_runtime_session(session_id: str) -> str | None:
    try:
        resp = _get_ddb().get_item(Key={"session_id": session_id})
        return resp.get("Item", {}).get("runtime_session_id")
    except Exception:
        return None

def _save_runtime_session(session_id: str, runtime_session_id: str):
    try:
        import time
        _get_ddb().put_item(Item={"session_id": session_id, "runtime_session_id": runtime_session_id, "ttl": int(time.time()) + 3600})
    except Exception:
        pass

def _invoke_agentcore(session_id: str, message: str) -> str:
    client = _get_agentcore()
    payload = json.dumps({"prompt": message, "session_id": session_id})
    params = {"agentRuntimeArn": AGENT_ARN, "qualifier": "DEFAULT", "payload": payload}
    runtime_session_id = _get_runtime_session(session_id)
    if runtime_session_id:
        params["runtimeSessionId"] = runtime_session_id
    response = client.invoke_agent_runtime(**params)
    new_rsid = response.get("runtimeSessionId")
    if new_rsid:
        _save_runtime_session(session_id, new_rsid)
    content_type = response.get("contentType", "")
    if "text/event-stream" in content_type:
        parts = []
        for line in response["response"].iter_lines(chunk_size=1):
            if line:
                line = line.decode("utf-8")
                if line.startswith("data: "): parts.append(line[6:])
        return "".join(parts)
    else:
        events = [e for e in response.get("response", [])]
        if events: return json.loads(events[0].decode("utf-8"))
        return "No response from agent."

def handler(event, context):
    headers = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "Content-Type", "Access-Control-Allow-Methods": "POST,OPTIONS"}
    if event.get("httpMethod") == "OPTIONS":
        return {"statusCode": 200, "headers": headers, "body": ""}
    try:
        body = json.loads(event.get("body", "{}"))
    except (json.JSONDecodeError, TypeError):
        body = {}
    if event.get("path", "").endswith("/health"):
        return {"statusCode": 200, "headers": headers, "body": json.dumps({"status": "ok"})}
    session_id = body.get("session_id", "")
    message = body.get("message", "")
    if not session_id:
        return {"statusCode": 400, "headers": headers, "body": json.dumps({"error": "Missing: session_id"})}
    if not message:
        return {"statusCode": 400, "headers": headers, "body": json.dumps({"error": "Missing: message"})}
    try:
        reply = _invoke_agentcore(session_id, message)
        return {"statusCode": 200, "headers": headers, "body": json.dumps({"session_id": session_id, "reply": reply})}
    except Exception as e:
        return {"statusCode": 500, "headers": headers, "body": json.dumps({"error": str(e)})}
