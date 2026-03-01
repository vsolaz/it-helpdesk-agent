import json, logging
from typing import Any
import boto3
from botocore.exceptions import ClientError
from agent.models import ConversationState
from agent.session_repository import AbstractSessionRepository

logger = logging.getLogger(__name__)

class DynamoSessionRepository(AbstractSessionRepository):
    def __init__(self, table_name: str, ttl_seconds: int = 3600, dynamodb_resource: Any = None) -> None:
        self._ttl_seconds = ttl_seconds
        resource = dynamodb_resource or boto3.resource("dynamodb")
        self._table = resource.Table(table_name)

    def get(self, session_id: str) -> ConversationState | None:
        try:
            response = self._table.get_item(Key={"session_id": session_id})
        except ClientError:
            logger.exception("DynamoDB get failed for %s", session_id)
            return None
        item = response.get("Item")
        return self._deserialize(item) if item else None

    def save(self, state: ConversationState) -> None:
        try:
            self._table.put_item(Item=self._serialize(state))
        except ClientError:
            logger.exception("DynamoDB put failed for %s", state.session_id)
            raise

    def delete(self, session_id: str) -> None:
        try:
            self._table.delete_item(Key={"session_id": session_id})
        except ClientError:
            logger.exception("DynamoDB delete failed for %s", session_id)
            raise

    def _serialize(self, state: ConversationState) -> dict:
        return {"session_id": state.session_id, "history": json.dumps(state.history), "collected": json.dumps(state.collected), "stage": state.stage, "last_active": str(state.last_active), "ttl": int(state.last_active) + self._ttl_seconds}

    @staticmethod
    def _deserialize(item: dict) -> ConversationState:
        return ConversationState(session_id=item["session_id"], history=json.loads(item["history"]), collected=json.loads(item["collected"]), stage=item["stage"], last_active=float(item["last_active"]))
