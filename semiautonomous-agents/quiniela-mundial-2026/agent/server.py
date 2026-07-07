"""FastAPI wrapper exposing the ADK agent as a streaming HTTP endpoint."""
import os
import logging
from typing import Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from google.adk.runners import Runner
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory import InMemoryMemoryService
from google.genai import types as gx_types

from agent import root_agent
from firestore_session_service import FirestoreSessionService

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("quiniela-chat")

APP_NAME = "quiniela-chat-v3"
session_service = FirestoreSessionService()
runner = Runner(
    app_name=APP_NAME,
    agent=root_agent,
    session_service=session_service,
    artifact_service=InMemoryArtifactService(),
    memory_service=InMemoryMemoryService(),
)
app = FastAPI(title="Quiniela Chat Agent")


@app.get("/")
async def health():
    return {"ok": True, "service": APP_NAME, "model": root_agent.model}


@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    text: str = (body.get("message") or "").strip()
    # Stable per-player session: ignore client sessionId, use userId so the
    # same player has one canonical chat history across devices.
    user_id: Optional[str] = body.get("userId") or "guest"
    user_name: str = (body.get("userName") or "").strip() or "Charal"
    tone: str = "ava"
    session_id: str = user_id

    if not text:
        raise HTTPException(status_code=400, detail="message is required")

    identity_state = {"player_name": user_name, "player_id": user_id, "tone": tone}

    # Reuse session if it exists (in-memory or Firestore); otherwise create.
    session = await session_service.get_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )
    if session is None:
        session = await session_service.create_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id,
            state=identity_state,
        )
    else:
        # State is not persisted by FirestoreSessionService; refresh each turn
        # so the prompt always reflects the caller's real identity even after
        # container restarts or name changes.
        session.state["player_name"] = user_name
        session.state["player_id"] = user_id
        session.state["tone"] = tone

    msg = gx_types.Content(role="user", parts=[gx_types.Part(text=text)])

    async def stream():
        try:
            async for event in runner.run_async(
                user_id=user_id, session_id=session.id, new_message=msg
            ):
                if event.content and event.content.parts:
                    for p in event.content.parts:
                        chunk = getattr(p, "text", None)
                        if chunk:
                            yield chunk
        except Exception as exc:  # noqa: BLE001
            log.exception("chat stream failed")
            yield f"\n\n[Error: {exc}]"

    return StreamingResponse(
        stream(),
        media_type="text/plain; charset=utf-8",
        headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"},
    )


@app.exception_handler(HTTPException)
async def http_exc_handler(_: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
