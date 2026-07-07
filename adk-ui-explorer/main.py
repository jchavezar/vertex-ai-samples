import os
import json
import asyncio
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from google.genai import types

from agent_config import create_adk_agent_runner, check_system_health

app = FastAPI(
    title="Google ADK + Gemini 3.1 Flash Lite UI/UX Explorer",
    description="Interactive Web Application showcasing Google ADK on VM jchavezar.c.googlers.com",
    version="1.0.0"
)

# Enable CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ADK Agent and Runner
agent, session_service, runner = create_adk_agent_runner()
active_sessions: Dict[str, dict] = {}

class ChatRequest(BaseModel):
    session_id: str
    prompt: str
    user_id: str = "default_user"

class CreateSessionRequest(BaseModel):
    user_id: str = "default_user"
    session_name: str = "New ADK Session"

@app.on_event("startup")
async def startup_event():
    # Pre-create a default session
    session = await session_service.create_session(user_id="default_user", app_name="adk_ui_explorer")
    active_sessions[session.id] = {
        "session_id": session.id,
        "name": "Default Explorer Session",
        "user_id": "default_user"
    }

@app.get("/api/system/info")
async def get_system_info():
    return {
        "hostname": "jchavezar.c.googlers.com",
        "port": 8000,
        "model": "gemini-3.1-flash-lite",
        "region": os.environ.get("GOOGLE_CLOUD_LOCATION", "global"),
        "framework": "Google ADK (Agent Development Kit)",
        "ssh_tunnel_command": "ssh -L 8000:localhost:8000 jesusarguelles@jchavezar.c.googlers.com",
        "health": check_system_health()
    }

@app.post("/api/sessions/create")
async def create_session(req: CreateSessionRequest):
    session = await session_service.create_session(user_id=req.user_id, app_name="adk_ui_explorer")
    active_sessions[session.id] = {
        "session_id": session.id,
        "name": req.session_name,
        "user_id": req.user_id
    }
    return {"session_id": session.id, "name": req.session_name}

@app.get("/api/sessions")
async def list_sessions():
    return list(active_sessions.values())

@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest):
    if not req.session_id:
        raise HTTPException(status_code=400, detail="session_id is required")
        
    async def event_generator():
        try:
            # Auto-ensure session exists in InMemorySessionService to prevent 'Session not found'
            session = await session_service.get_session(
                app_name="adk_ui_explorer",
                user_id=req.user_id,
                session_id=req.session_id
            )
            if not session:
                await session_service.create_session(
                    app_name="adk_ui_explorer",
                    user_id=req.user_id,
                    session_id=req.session_id
                )
                active_sessions[req.session_id] = {
                    "session_id": req.session_id,
                    "name": "Active Session",
                    "user_id": req.user_id
                }

            content = types.Content(
                role="user",
                parts=[types.Part.from_text(text=req.prompt)]
            )
            
            # Run ADK Runner asynchronously with auto-retry on transient overload
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    async for event in runner.run_async(
                        user_id=req.user_id,
                        session_id=req.session_id,
                        new_message=content
                    ):
                        if hasattr(event, "content") and event.content:
                            for part in event.content.parts:
                                # 1. Function Call
                                if hasattr(part, "function_call") and part.function_call:
                                    fc = part.function_call
                                    yield f"data: {json.dumps({'type': 'tool_call', 'name': fc.name, 'args': dict(fc.args)})}\n\n"
                                    
                                # 2. Function Response
                                elif hasattr(part, "function_response") and part.function_response:
                                    fr = part.function_response
                                    yield f"data: {json.dumps({'type': 'tool_response', 'name': fr.name, 'response': fr.response})}\n\n"
                                    
                                # 3. Text Delta
                                elif hasattr(part, "text") and part.text:
                                    yield f"data: {json.dumps({'type': 'text_delta', 'content': part.text})}\n\n"
                    break # Success, exit retry loop
                except Exception as ex:
                    if "PREFILL_QUEUE_PREEMPTED" in str(ex) or "503" in str(ex) or "unavailable" in str(ex).lower():
                        if attempt < max_retries - 1:
                            await asyncio.sleep(1.0 * (attempt + 1))
                            continue
                    raise ex

            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# Mount static directory for UI
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
