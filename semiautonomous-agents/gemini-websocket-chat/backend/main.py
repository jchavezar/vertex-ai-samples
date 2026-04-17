"""
SockAgent — FastAPI backend.
Terminal-aesthetic chat interface for Vertex AI Gemini.
"""

import uuid
import time
from pathlib import Path

from config import PROJECT_ID, LOCATION, MODEL, API_KEY

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional

from google import genai
from google.genai.types import GenerateContentConfig

app = FastAPI(title="SockAgent", description="Terminal chat interface for Vertex AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Auth ────────────────────────────────────────────────────────────────────

def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Simple API key auth. Skipped if API_KEY is not set."""
    if not API_KEY:
        return
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


# ─── Gemini Client ───────────────────────────────────────────────────────────

client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location=LOCATION,
)

AVAILABLE_MODELS = {
    "2.5-flash": "gemini-2.5-flash",
    "2.5-pro": "gemini-2.5-pro",
}

# ─── Session Store (in-memory for MVP) ───────────────────────────────────────

sessions: dict[str, dict] = {}


def get_or_create_session(session_id: str) -> dict:
    if session_id not in sessions:
        sessions[session_id] = {
            "id": session_id,
            "created_at": time.time(),
            "updated_at": time.time(),
            "title": "new session",
            "messages": [],
            "model": MODEL,
        }
    return sessions[session_id]


# ─── Request/Response Models ─────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    model: Optional[str] = None  # "2.5-flash" or "2.5-pro"


class ChatResponse(BaseModel):
    response: str
    session_id: str
    model: str


# ─── Endpoints ───────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "service": "sockagent",
        "project": PROJECT_ID,
        "model": MODEL,
    }


@app.get("/api/sessions", dependencies=[Depends(verify_api_key)])
async def list_sessions():
    """List all sessions, ls -la style."""
    result = []
    for sid, s in sorted(sessions.items(), key=lambda x: x[1]["updated_at"], reverse=True):
        result.append({
            "id": s["id"],
            "title": s["title"],
            "created_at": s["created_at"],
            "updated_at": s["updated_at"],
            "message_count": len(s["messages"]),
            "model": s["model"],
        })
    return result


@app.post("/api/chat", dependencies=[Depends(verify_api_key)], response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Non-streaming chat endpoint."""
    session_id = req.session_id or str(uuid.uuid4())
    session = get_or_create_session(session_id)

    model_key = req.model or "2.5-flash"
    model_name = AVAILABLE_MODELS.get(model_key, MODEL)
    session["model"] = model_name

    # Append user message
    session["messages"].append({"role": "user", "content": req.message})

    # Build contents for Gemini
    contents = [
        {"role": m["role"] if m["role"] != "assistant" else "model", "parts": [{"text": m["content"]}]}
        for m in session["messages"]
    ]

    response = await client.aio.models.generate_content(
        model=model_name,
        contents=contents,
        config=GenerateContentConfig(temperature=0.7),
    )

    reply = response.text or ""

    # Append assistant message
    session["messages"].append({"role": "assistant", "content": reply})
    session["updated_at"] = time.time()

    # Auto-title from first message
    if session["title"] == "new session" and len(session["messages"]) >= 2:
        session["title"] = req.message[:60]

    return ChatResponse(response=reply, session_id=session_id, model=model_name)


@app.delete("/api/sessions/{session_id}", dependencies=[Depends(verify_api_key)])
async def delete_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
        return {"deleted": session_id}
    raise HTTPException(status_code=404, detail="Session not found")


# ─── WebSocket (streaming) ──────────────────────────────────────────────────

@app.websocket("/ws/chat")
async def ws_chat(ws: WebSocket):
    await ws.accept()

    try:
        while True:
            data = await ws.receive_json()

            # Validate API key if set
            if API_KEY and data.get("api_key") != API_KEY:
                await ws.send_json({"type": "error", "content": "Invalid API key"})
                continue

            session_id = data.get("session_id") or str(uuid.uuid4())
            session = get_or_create_session(session_id)

            model_key = data.get("model", "2.5-flash")
            model_name = AVAILABLE_MODELS.get(model_key, MODEL)
            session["model"] = model_name

            user_msg = data.get("message", "")
            if not user_msg:
                continue

            session["messages"].append({"role": "user", "content": user_msg})

            # Build contents
            contents = [
                {"role": m["role"] if m["role"] != "assistant" else "model", "parts": [{"text": m["content"]}]}
                for m in session["messages"]
            ]

            # Send session_id immediately
            await ws.send_json({"type": "session", "session_id": session_id})

            # Stream response
            full_response = ""
            try:
                stream = await client.aio.models.generate_content_stream(
                    model=model_name,
                    contents=contents,
                    config=GenerateContentConfig(temperature=0.7),
                )
                async for chunk in stream:
                    if chunk.text:
                        full_response += chunk.text
                        await ws.send_json({
                            "type": "chunk",
                            "content": chunk.text,
                        })

                # Done
                session["messages"].append({"role": "assistant", "content": full_response})
                session["updated_at"] = time.time()

                if session["title"] == "new session" and len(session["messages"]) >= 2:
                    session["title"] = user_msg[:60]

                await ws.send_json({"type": "done", "session_id": session_id})

            except Exception as e:
                await ws.send_json({"type": "error", "content": str(e)})

    except WebSocketDisconnect:
        pass


# ─── Static file serving (production) ───────────────────────────────────────

dist_path = Path(__file__).parent.parent / "frontend" / "dist"
if dist_path.exists():
    app.mount("/assets", StaticFiles(directory=dist_path / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api") or full_path.startswith("ws"):
            return {"error": "Not found"}
        file_path = dist_path / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(dist_path / "index.html")


if __name__ == "__main__":
    import uvicorn
    port = 8080
    uvicorn.run(app, host="0.0.0.0", port=port)
