"""Context & Memory module for Agent Assessment Hub.

Manages conversational state, session context, persistent incident memory,
and context compaction/retrieval for multi-turn interactions.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Optional[Dict[str, Any]] = None


class SessionState(BaseModel):
    session_id: str
    user_id: Optional[str] = "default-user"
    environment: str = "production"
    active_incident_id: Optional[str] = None
    variables: Dict[str, Any] = Field(default_factory=dict)
    history: List[Message] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class MemoryManager:
    """In-memory and stateful session memory store for agent context retention."""

    def __init__(self, max_history_turns: int = 20):
        self.max_history_turns = max_history_turns
        self._sessions: Dict[str, SessionState] = {}

    def get_or_create_session(self, session_id: str, user_id: Optional[str] = None) -> SessionState:
        if session_id not in self._sessions:
            self._sessions[session_id] = SessionState(
                session_id=session_id,
                user_id=user_id or "default-user",
            )
        return self._sessions[session_id]

    def add_message(self, session_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        session = self.get_or_create_session(session_id)
        msg = Message(role=role, content=content, metadata=metadata)
        session.history.append(msg)
        session.updated_at = datetime.now(timezone.utc).isoformat()

        # Context pruning to maintain token economy
        if len(session.history) > self.max_history_turns:
            session.history = session.history[-self.max_history_turns:]

    def set_variable(self, session_id: str, key: str, value: Any) -> None:
        session = self.get_or_create_session(session_id)
        session.variables[key] = value
        session.updated_at = datetime.now(timezone.utc).isoformat()

    def get_variable(self, session_id: str, key: str, default: Any = None) -> Any:
        session = self.get_or_create_session(session_id)
        return session.variables.get(key, default)

    def get_formatted_history(self, session_id: str) -> List[Dict[str, str]]:
        session = self.get_or_create_session(session_id)
        return [{"role": m.role, "content": m.content} for m in session.history]

    def clear_session(self, session_id: str) -> None:
        if session_id in self._sessions:
            del self._sessions[session_id]


# Global memory manager instance
memory_store = MemoryManager()
