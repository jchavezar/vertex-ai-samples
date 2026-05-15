"""FastAPI backend — proxies the Next.js chat UI to the deployed Agent Engine.

Pattern: backend pre-injects the user's Entra access token into the AE session
state at `temp:sharepoint_3lo`, then streams `stream_query` events back as SSE.
This is the correct pattern for ADK + 3LO (`submit_auth_response` does NOT exist;
the agent's tools read the token from `tool_context.state`).

Adapted from adk-drive-ae/backend/main.py:1-179 — same shape, Entra-tokenised.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import AsyncIterator

import vertexai
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from vertexai import agent_engines

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("backend")

PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
LOCATION = os.environ.get("DEPLOY_LOCATION", "us-central1")
AGENT_ENGINE_RESOURCE = os.environ.get("AGENT_ENGINE_RESOURCE", "").strip()
SESSION_TOKEN_KEY = os.environ.get("SESSION_TOKEN_KEY", "temp:sharepoint_3lo")
FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://localhost:3000")

if not AGENT_ENGINE_RESOURCE:
    log.warning("AGENT_ENGINE_RESOURCE not set — /api/* will 503 until you add it to .env")

vertexai.init(project=PROJECT, location=LOCATION)

app = FastAPI(title="agent-gateway-demo backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN, "http://localhost:3000"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

_engine_cache: object | None = None


def _engine():
    global _engine_cache
    if _engine_cache is None:
        if not AGENT_ENGINE_RESOURCE:
            raise HTTPException(503, "AGENT_ENGINE_RESOURCE not configured on backend")
        _engine_cache = agent_engines.get(AGENT_ENGINE_RESOURCE)
    return _engine_cache


# ──────────────────────────────────────────────────────────────────────────
# Request models
# ──────────────────────────────────────────────────────────────────────────

class SessionRequest(BaseModel):
    access_token: str = Field(..., description="User's Entra access token (Graph audience)")
    user_id: str = Field(default="anon")


class ChatRequest(BaseModel):
    message: str
    session_id: str
    user_id: str = Field(default="anon")
    # Optional: refresh the token for an already-open session.
    access_token: str | None = None


# ──────────────────────────────────────────────────────────────────────────
# Health
# ──────────────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {
        "ok": True,
        "agent_engine_configured": bool(AGENT_ENGINE_RESOURCE),
        "agent_engine_resource": AGENT_ENGINE_RESOURCE or None,
        "session_token_key": SESSION_TOKEN_KEY,
        "project": PROJECT,
        "location": LOCATION,
    }


# ──────────────────────────────────────────────────────────────────────────
# Sessions — pre-inject the Entra token into AE session state
# ──────────────────────────────────────────────────────────────────────────

@app.post("/api/session")
def create_session(body: SessionRequest):
    """Create a new AE session with the user's Entra token in state.

    UI calls this once per chat (or on token refresh) and then reuses the
    returned `session_id` for /api/chat.
    """
    engine = _engine()
    state = {
        SESSION_TOKEN_KEY: body.access_token,
        # Mirror under the unprefixed key too, so tools that don't use the
        # `temp:` lifetime can still read it within the same session.
        SESSION_TOKEN_KEY.removeprefix("temp:"): body.access_token,
    }
    session = engine.create_session(user_id=body.user_id, state=state)
    sid = session.get("id") if isinstance(session, dict) else getattr(session, "id", None)
    log.info("created session %s for user=%s", sid, body.user_id)
    return {"session_id": sid, "user_id": body.user_id}


# ──────────────────────────────────────────────────────────────────────────
# Chat — stream the agent's events to the UI as SSE
# ──────────────────────────────────────────────────────────────────────────

def _serialize_event(event) -> dict:
    """Normalise an Agent Engine stream_query event into a UI-friendly dict."""
    if isinstance(event, dict):
        ev = event
    else:
        try:
            ev = event.model_dump()
        except Exception:  # noqa: BLE001
            ev = {"raw": str(event)}

    out = {"type": "event", "author": ev.get("author")}
    content = ev.get("content") if isinstance(ev, dict) else None
    if isinstance(content, dict):
        for part in content.get("parts", []) or []:
            if not isinstance(part, dict):
                continue
            if part.get("text"):
                out.setdefault("text", "")
                out["text"] += part["text"]
            if part.get("function_call"):
                out["tool_call"] = {
                    "name": part["function_call"].get("name"),
                    "args": part["function_call"].get("args"),
                }
            if part.get("function_response"):
                fr = part["function_response"]
                resp = fr.get("response", {})
                preview = json.dumps(resp, default=str)
                # No truncation — the UI chip is collapsible, full payload
                # is genuinely useful for debugging the auth + Graph wiring.
                out["tool_result"] = {"name": fr.get("name"), "preview": preview}
    return out


async def _sse_stream(user_id: str, session_id: str, message: str) -> AsyncIterator[bytes]:
    engine = _engine()
    loop = asyncio.get_running_loop()
    queue: asyncio.Queue = asyncio.Queue()
    SENTINEL = object()

    def producer():
        try:
            for event in engine.stream_query(user_id=user_id, session_id=session_id, message=message):
                loop.call_soon_threadsafe(queue.put_nowait, event)
        except Exception as e:  # noqa: BLE001
            loop.call_soon_threadsafe(queue.put_nowait, {"_error": str(e)})
        finally:
            loop.call_soon_threadsafe(queue.put_nowait, SENTINEL)

    loop.run_in_executor(None, producer)

    while True:
        item = await queue.get()
        if item is SENTINEL:
            yield b"event: done\ndata: {}\n\n"
            return
        if isinstance(item, dict) and "_error" in item:
            yield f"data: {json.dumps({'type': 'error', 'error': item['_error']})}\n\n".encode()
            yield b"event: done\ndata: {}\n\n"
            return
        yield f"data: {json.dumps(_serialize_event(item))}\n\n".encode()


@app.post("/api/chat")
async def chat(body: ChatRequest):
    if not body.session_id:
        raise HTTPException(400, "session_id is required — call POST /api/session first")
    log.info("chat session=%s user=%s msg=%r", body.session_id, body.user_id, body.message[:100])
    return StreamingResponse(
        _sse_stream(body.user_id, body.session_id, body.message),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
