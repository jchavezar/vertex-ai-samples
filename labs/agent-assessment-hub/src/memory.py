"""Context & Memory module for Agent Assessment Hub.

Provides persistent SQLite database storage for multi-turn sessions and messages,
context window management, and asynchronous background tasks for memory consolidation.
"""

import os
import json
import sqlite3
import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from src.observability import logger, trace_span


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
    summary: Optional[str] = None
    variables: Dict[str, Any] = Field(default_factory=dict)
    history: List[Message] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class PersistentMemoryStore:
    """Database-backed persistent session memory store with async consolidation."""

    def __init__(self, db_path: str = "sessions.db", max_history_turns: int = 20):
        self.db_path = db_path
        self.max_history_turns = max_history_turns
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        """Initializes persistent SQLite tables for sessions and message turns."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    environment TEXT,
                    active_incident_id TEXT,
                    summary TEXT,
                    variables TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp TEXT,
                    metadata TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            """)
            conn.commit()

    @trace_span("memory.get_or_create_session")
    def get_or_create_session(self, session_id: str, user_id: Optional[str] = None) -> SessionState:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, environment, active_incident_id, summary, variables, created_at, updated_at FROM sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()

            if not row:
                now = datetime.now(timezone.utc).isoformat()
                cursor.execute(
                    "INSERT INTO sessions (session_id, user_id, environment, variables, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (session_id, user_id or "default-user", "production", json.dumps({}), now, now)
                )
                conn.commit()
                return SessionState(session_id=session_id, user_id=user_id or "default-user")

            u_id, env, inc_id, summary, vars_json, created, updated = row
            cursor.execute("SELECT role, content, timestamp, metadata FROM messages WHERE session_id = ? ORDER BY id ASC", (session_id,))
            msg_rows = cursor.fetchall()
            history = [
                Message(
                    role=r[0],
                    content=r[1],
                    timestamp=r[2],
                    metadata=json.loads(r[3]) if r[3] else None
                )
                for r in msg_rows
            ]

            return SessionState(
                session_id=session_id,
                user_id=u_id,
                environment=env,
                active_incident_id=inc_id,
                summary=summary,
                variables=json.loads(vars_json) if vars_json else {},
                history=history,
                created_at=created,
                updated_at=updated,
            )

    @trace_span("memory.add_message")
    def add_message(self, session_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        self.get_or_create_session(session_id)
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (session_id, role, content, timestamp, metadata) VALUES (?, ?, ?, ?, ?)",
                (session_id, role, content, now, json.dumps(metadata) if metadata else None)
            )
            cursor.execute("UPDATE sessions SET updated_at = ? WHERE session_id = ?", (now, session_id))
            conn.commit()

        # Trigger background consolidation when history threshold is approached
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.consolidate_memory_background(session_id))
        except RuntimeError:
            pass

    async def consolidate_memory_background(self, session_id: str) -> None:
        """Asynchronous background worker consolidating session turns into structured summaries."""
        logger.info(f"Background memory consolidation started for session {session_id}")
        session = self.get_or_create_session(session_id)
        if len(session.history) > 10:
            # Consolidate older message turns into semantic incident summary
            recent_turns = session.history[-5:]
            summary_content = f"Active SRE Investigation summary: {len(session.history)} total interactions recorded. Focus on recent issues in {session.environment}."
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE sessions SET summary = ? WHERE session_id = ?", (summary_content, session_id))
                conn.commit()
            logger.info(f"Background memory consolidation completed for session {session_id}")

    def set_variable(self, session_id: str, key: str, value: Any) -> None:
        session = self.get_or_create_session(session_id)
        session.variables[key] = value
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE sessions SET variables = ?, updated_at = ? WHERE session_id = ?", (json.dumps(session.variables), now, session_id))
            conn.commit()

    def get_variable(self, session_id: str, key: str, default: Any = None) -> Any:
        session = self.get_or_create_session(session_id)
        return session.variables.get(key, default)

    def get_formatted_history(self, session_id: str) -> List[Dict[str, str]]:
        session = self.get_or_create_session(session_id)
        return [{"role": m.role, "content": m.content} for m in session.history]


# Global persistent database memory instance
memory_store = PersistentMemoryStore()
