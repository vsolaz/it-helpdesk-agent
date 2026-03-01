"""Session repository implementations (in-memory and abstract base)."""
import time
from abc import ABC, abstractmethod
from threading import Lock
from agent.models import ConversationState

_SESSION_TTL_SECONDS = 3600  # 1 hour


class AbstractSessionRepository(ABC):
    """Abstract base class for session storage."""

    @abstractmethod
    def get(self, session_id: str) -> ConversationState | None:
        """Retrieve a session by ID, or None if not found/expired."""
        ...

    @abstractmethod
    def save(self, state: ConversationState) -> None:
        """Persist a session state."""
        ...

    @abstractmethod
    def delete(self, session_id: str) -> None:
        """Delete a session by ID."""
        ...


class SessionRepository(AbstractSessionRepository):
    """Thread-safe in-memory session repository with TTL expiry."""

    def __init__(self, ttl_seconds: int = _SESSION_TTL_SECONDS) -> None:
        self._store: dict[str, ConversationState] = {}
        self._lock = Lock()
        self._ttl = ttl_seconds

    def get(self, session_id: str) -> ConversationState | None:
        """Return session if found and not expired."""
        with self._lock:
            state = self._store.get(session_id)
            if state is None:
                return None
            if time.time() - state.last_active > self._ttl:
                del self._store[session_id]
                return None
            return state

    def save(self, state: ConversationState) -> None:
        with self._lock:
            self._store[state.session_id] = state

    def delete(self, session_id: str) -> None:
        with self._lock:
            self._store.pop(session_id, None)

    def purge_expired(self) -> int:
        """Remove all expired sessions. Returns number purged."""
        now = time.time()
        with self._lock:
            expired = [sid for sid, s in self._store.items() if now - s.last_active > self._ttl]
            for sid in expired:
                del self._store[sid]
        return len(expired)
