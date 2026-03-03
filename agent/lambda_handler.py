"""AWS Lambda handler — wraps the Flask app with Mangum."""
import os

def _load_secrets():
    secret_name = os.environ.get("SERVICENOW_SECRET_NAME")
    if not secret_name or os.environ.get("SERVICENOW_INSTANCE_URL"):
        return
    import boto3, json
    client = boto3.client("secretsmanager", region_name="us-east-1")
    try:
        resp = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(resp["SecretString"])
        os.environ["SERVICENOW_INSTANCE_URL"] = secret.get("instance_url", "")
        os.environ["SERVICENOW_USERNAME"] = secret.get("username", "")
        os.environ["SERVICENOW_PASSWORD"] = secret.get("password", "")
    except Exception:
        pass

_load_secrets()
if os.environ.get("SESSION_STORE") == "dynamodb":
    os.environ.setdefault("SESSIONS_TABLE", "helpdesk-sessions")

from mangum import Mangum
from agent.app import app
handler = Mangum(app, lifespan="off")
