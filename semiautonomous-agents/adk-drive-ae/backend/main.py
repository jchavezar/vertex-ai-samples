"""
FastAPI proxy between the Next.js UI and the deployed Vertex AI Agent Engine.

Responsibilities:
  1. Receive {message, access_token, [session_id], [user_id]} from the UI.
  2. (First request) Create an Agent Engine session with the access_token in
     `state["temp:drive_access_token"]` so the deployed agent's tools can read it.
  3. Stream the Agent Engine `stream_query` events back to the UI as
     Server-Sent Events.

Run:
    cd vertex-ai-samples/semiautonomous-agents/adk-drive-ae
    uv run uvicorn backend.main:app --port 8080 --reload
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

PROJECT = os.environ["GOOGLE_CLOUD_PROJECT"]
LOCATION = os.environ.get("DEPLOY_LOCATION", "us-central1")
AGENT_ENGINE_RESOURCE = os.environ.get("AGENT_ENGINE_RESOURCE", "").strip()
FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://localhost:3000")

if not AGENT_ENGINE_RESOURCE:
    log.warning("AGENT_ENGINE_RESOURCE not set — POST /api/chat will 503 until you add it to .env")

vertexai.init(project=PROJECT, location=LOCATION)

app = FastAPI(title="adk-drive-ae backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache the AgentEngine handle — get() is a network call, no need to repeat per request.
_engine_cache: object | None = None


def _engine():
    global _engine_cache
    if _engine_cache is None:
        if not AGENT_ENGINE_RESOURCE:
            raise HTTPException(503, "AGENT_ENGINE_RESOURCE not configured on backend")
        _engine_cache = agent_engines.get(AGENT_ENGINE_RESOURCE)
    return _engine_cache


class ChatRequest(BaseModel):
    message: str
    access_token: str
    user_id: str = Field(default="anon")
    session_id: str | None = None


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "agent_engine_configured": bool(AGENT_ENGINE_RESOURCE),
        "agent_engine_resource": AGENT_ENGINE_RESOURCE or None,
        "project": PROJECT,
        "location": LOCATION,
    }


@app.post("/api/session")
def create_session(body: ChatRequest):
    """Create a new Agent Engine session with the user's Drive token in state.

    The UI calls this once per chat (or whenever the token rotates) and then
    reuses the returned session_id for subsequent /api/chat calls.
    """
    engine = _engine()
    state = {"temp:drive_access_token": body.access_token, "drive_access_token": body.access_token}
    session = engine.create_session(user_id=body.user_id, state=state)
    sid = session.get("id") if isinstance(session, dict) else getattr(session, "id", None)
    log.info("created session %s for user=%s", sid, body.user_id)
    return {"session_id": sid, "user_id": body.user_id}


def _serialize_event(event) -> dict:
    """Normalize an Agent Engine stream_query event into a UI-friendly dict."""
    if isinstance(event, dict):
        ev = event
    else:
        try:
            ev = event.model_dump()
        except Exception:
            ev = {"raw": str(event)}

    out = {"type": "event", "raw": ev}
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
                # truncate to keep SSE payload small
                preview = json.dumps(resp, default=str)
                if len(preview) > 800:
                    preview = preview[:800] + "..."
                out["tool_result"] = {"name": fr.get("name"), "preview": preview}
    return out


async def _sse_stream(user_id: str, session_id: str, message: str) -> AsyncIterator[bytes]:
    engine = _engine()
    loop = asyncio.get_running_loop()

    # stream_query is sync + blocking — run iteration in a thread and bridge
    # results back via a queue so we can emit SSE chunks as they arrive.
    queue: asyncio.Queue = asyncio.Queue()
    SENTINEL = object()

    def producer():
        try:
            for event in engine.stream_query(user_id=user_id, session_id=session_id, message=message):
                loop.call_soon_threadsafe(queue.put_nowait, event)
        except Exception as e:  # surface to client
            loop.call_soon_threadsafe(queue.put_nowait, {"_error": str(e)})
        finally:
            loop.call_soon_threadsafe(queue.put_nowait, SENTINEL)

    asyncio.get_event_loop().run_in_executor(None, producer)

    while True:
        item = await queue.get()
        if item is SENTINEL:
            yield b"event: done\ndata: {}\n\n"
            return
        if isinstance(item, dict) and "_error" in item:
            payload = {"type": "error", "error": item["_error"]}
            yield f"data: {json.dumps(payload)}\n\n".encode()
            yield b"event: done\ndata: {}\n\n"
            return
        payload = _serialize_event(item)
        yield f"data: {json.dumps(payload)}\n\n".encode()


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
