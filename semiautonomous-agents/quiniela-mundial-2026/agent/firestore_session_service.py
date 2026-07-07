"""Firestore-backed ADK SessionService for persistent chat history.

Schema:
  quiniela_charales_chats/{user_id}                                 (parent doc)
    fields: { playerId, sessionId, lastMessageAt, messageCount, lastMessage }
    subcollection: events/{autoId}
      fields: { seq, ts, role, text, event_json (str) }

We use stable session_id == user_id (= playerId) so each player has exactly one
canonical session that survives container restarts and is reachable from any
device.

Writes happen in the background via asyncio.create_task — they do NOT block the
streaming response, so chat latency is unaffected.
"""
from __future__ import annotations

import asyncio
import logging
import os
from typing import Any, Optional

from google.cloud import firestore
from google.cloud.firestore_v1.async_client import AsyncClient
from google.adk.events.event import Event
from google.adk.sessions.base_session_service import GetSessionConfig, ListSessionsResponse
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.sessions.session import Session

log = logging.getLogger("quiniela-chat.firestore-sessions")

PARENT_COLLECTION = "quiniela_charales_chats"
EVENTS_SUBCOLLECTION = "events"


def _extract_role_text(event: Event) -> tuple[Optional[str], Optional[str]]:
    """Pull a flat (role, text) view from an ADK event for admin display."""
    role: Optional[str] = None
    text_parts: list[str] = []
    if event.content:
        role = event.content.role or None
        for p in event.content.parts or []:
            t = getattr(p, "text", None)
            if t:
                text_parts.append(t)
    return role, ("".join(text_parts) or None)


class FirestoreSessionService(InMemorySessionService):
    """In-memory cache + Firestore persistence.

    On get_session: if the in-memory session is empty, hydrate from Firestore.
    On append_event: super (updates RAM) + fire-and-forget Firestore write.
    """

    def __init__(self, project: Optional[str] = None):
        super().__init__()
        self._project = project or os.environ.get("GOOGLE_CLOUD_PROJECT")
        self._db: Optional[AsyncClient] = None

    def _client(self) -> AsyncClient:
        if self._db is None:
            self._db = firestore.AsyncClient(project=self._project)
        return self._db

    async def _hydrate_from_firestore(
        self, *, app_name: str, user_id: str, session_id: str
    ) -> Optional[Session]:
        """Load all events for this player from Firestore and replay into memory."""
        db = self._client()
        try:
            parent = db.collection(PARENT_COLLECTION).document(user_id)
            parent_snap = await parent.get()
            if not parent_snap.exists:
                return None
            events_q = parent.collection(EVENTS_SUBCOLLECTION).order_by("seq")
            event_docs = [d async for d in events_q.stream()]
            if not event_docs:
                # parent exists but no events yet — return a fresh session.
                return await super().create_session(
                    app_name=app_name, user_id=user_id, session_id=session_id
                )
        except Exception as e:  # noqa: BLE001
            log.warning("hydrate failed for %s: %s", user_id, e)
            return None

        # Create an empty in-memory session, then append rehydrated events.
        try:
            session = await super().create_session(
                app_name=app_name, user_id=user_id, session_id=session_id
            )
        except Exception:  # already exists
            session = await super().get_session(
                app_name=app_name, user_id=user_id, session_id=session_id
            )
            if session is None:
                return None

        for doc in event_docs:
            data = doc.to_dict() or {}
            raw = data.get("event_json")
            if not raw:
                continue
            try:
                ev = Event.model_validate_json(raw)
            except Exception as e:  # noqa: BLE001
                log.warning("skip malformed event %s: %s", doc.id, e)
                continue
            # Use the storage-level dict directly to avoid double-trim of state.
            storage = self.sessions.get(app_name, {}).get(user_id, {}).get(session_id)
            if storage is not None:
                storage.events.append(ev)
                storage.last_update_time = ev.timestamp

        return await super().get_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )

    async def get_session(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        config: Optional[GetSessionConfig] = None,
    ) -> Optional[Session]:
        existing = await super().get_session(
            app_name=app_name, user_id=user_id, session_id=session_id, config=config
        )
        if existing is not None:
            return existing
        # Cache miss → try Firestore.
        return await self._hydrate_from_firestore(
            app_name=app_name, user_id=user_id, session_id=session_id
        )

    async def append_event(self, session: Session, event: Event) -> Event:
        ev = await super().append_event(session=session, event=event)
        # Persist in background — do NOT await; chat latency must not depend on this.
        if not event.partial:
            role, text = _extract_role_text(event)
            asyncio.create_task(
                self._persist_event(
                    user_id=session.user_id,
                    session_id=session.id,
                    event=event,
                    role=role,
                    text=text,
                )
            )
        return ev

    async def _persist_event(
        self,
        *,
        user_id: str,
        session_id: str,
        event: Event,
        role: Optional[str],
        text: Optional[str],
    ) -> None:
        try:
            db = self._client()
            parent = db.collection(PARENT_COLLECTION).document(user_id)
            payload = {
                "seq": event.timestamp,
                "ts": firestore.SERVER_TIMESTAMP,
                "role": role,
                "text": text,
                "event_json": event.model_dump_json(),
                "sessionId": session_id,
            }
            # Write event + update parent in parallel.
            await asyncio.gather(
                parent.collection(EVENTS_SUBCOLLECTION).add(payload),
                parent.set(
                    {
                        "playerId": user_id,
                        "sessionId": session_id,
                        "lastMessageAt": firestore.SERVER_TIMESTAMP,
                        "lastMessage": (text or "")[:200],
                        "messageCount": firestore.Increment(1),
                    },
                    merge=True,
                ),
            )
        except Exception as e:  # noqa: BLE001
            log.warning("persist_event failed for %s: %s", user_id, e)

    async def delete_session(
        self, *, app_name: str, user_id: str, session_id: str
    ) -> None:
        await super().delete_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )
        try:
            db = self._client()
            parent = db.collection(PARENT_COLLECTION).document(user_id)
            events = parent.collection(EVENTS_SUBCOLLECTION)
            async for doc in events.stream():
                await doc.reference.delete()
            await parent.delete()
        except Exception as e:  # noqa: BLE001
            log.warning("delete_session firestore cleanup failed for %s: %s", user_id, e)

    async def list_sessions(
        self, *, app_name: str, user_id: Optional[str] = None
    ) -> ListSessionsResponse:
        # Combine in-memory + Firestore.
        mem = await super().list_sessions(app_name=app_name, user_id=user_id)
        known_ids = {(s.user_id, s.id) for s in mem.sessions}
        try:
            db = self._client()
            if user_id is None:
                async for doc in db.collection(PARENT_COLLECTION).stream():
                    data = doc.to_dict() or {}
                    uid = data.get("playerId") or doc.id
                    sid = data.get("sessionId") or doc.id
                    if (uid, sid) in known_ids:
                        continue
                    mem.sessions.append(
                        Session(app_name=app_name, user_id=uid, id=sid, state={}, last_update_time=0.0)
                    )
            else:
                snap = await db.collection(PARENT_COLLECTION).document(user_id).get()
                if snap.exists:
                    data = snap.to_dict() or {}
                    sid = data.get("sessionId") or user_id
                    if (user_id, sid) not in known_ids:
                        mem.sessions.append(
                            Session(app_name=app_name, user_id=user_id, id=sid, state={}, last_update_time=0.0)
                        )
        except Exception as e:  # noqa: BLE001
            log.warning("list_sessions firestore lookup failed: %s", e)
        return mem
