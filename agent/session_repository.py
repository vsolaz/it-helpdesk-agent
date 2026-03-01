from abc import ABC, abstractmethod
from threading import Lock
from agent.models import ConversationState

class AbstractSessionRepository(ABC):
    @abstractmethod
    def get(self, session_id: str) -> ConversationState | None: ...
    @abstractmethod
    def save(self, state: ConversationState) -> None: ...
    @abstractmethod
    def delete(self, session_id: str) -> None: ...

class SessionRepository(AbstractSessionRepository):
    def __init__(self) -> None:
        self._store: dict[str, ConversationState] = {}
        self._lock = Lock()
    def get(self, session_id: str) -> ConversationState | None:
        with self._lock: return self._store.get(session_id)
    def save(self, state: ConversationState) -> None:
        with self._lock: self._store[state.session_id] = state
    def delete(self, session_id: str) -> None:
        with self._lock: self._store.pop(session_id, None)
