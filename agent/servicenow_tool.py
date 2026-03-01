import logging, os
from typing import Optional
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError, Timeout, RequestException
from agent.models import IncidentFields, IncidentResult

logger = logging.getLogger(__name__)
_HTTP_TIMEOUT = (10, 20)

def _get_credentials() -> tuple[str, str, str]:
    instance_url = os.environ.get("SERVICENOW_INSTANCE_URL", "").rstrip("/")
    username = os.environ.get("SERVICENOW_USERNAME", "")
    password = os.environ.get("SERVICENOW_PASSWORD", "")
    missing = [n for n, v in [("SERVICENOW_INSTANCE_URL", instance_url), ("SERVICENOW_USERNAME", username), ("SERVICENOW_PASSWORD", password)] if not v]
    if missing: raise EnvironmentError(f"Missing: {', '.join(missing)}")
    return instance_url, username, password

def create_incident(fields: IncidentFields) -> IncidentResult:
    try:
        instance_url, username, password = _get_credentials()
    except EnvironmentError as exc:
        return IncidentResult(success=False, ticket_number=None, error_message=str(exc))
    endpoint = f"{instance_url}/api/now/table/incident"
    payload = {"short_description": fields.short_description, "description": fields.description, "urgency": str(int(fields.urgency)), "category": fields.category}
    try:
        response = requests.post(endpoint, json=payload, auth=HTTPBasicAuth(username, password), headers={"Accept": "application/json"}, timeout=_HTTP_TIMEOUT)
    except Timeout:
        return IncidentResult(success=False, ticket_number=None, error_message="ServiceNow API timed out.")
    except ConnectionError:
        return IncidentResult(success=False, ticket_number=None, error_message="Could not connect to ServiceNow.")
    except RequestException as exc:
        return IncidentResult(success=False, ticket_number=None, error_message=f"Error: {type(exc).__name__}")
    if response.status_code == 201:
        data = response.json().get("result", {})
        return IncidentResult(success=True, ticket_number=data.get("number"), error_message=None)
    return IncidentResult(success=False, ticket_number=None, error_message=f"HTTP {response.status_code}")
