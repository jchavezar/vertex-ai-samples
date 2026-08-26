"""
FastAPI Backend for Google ADK Light Chatbot
Provides REST & SSE Streaming endpoints for the TypeScript Frontend.
"""

import json
import os
from typing import Optional, Dict, Any
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from agent_engine import (
    ADKChatbotManager,
    SUPPORTED_MODELS,
    DEFAULT_MODEL,
    DEFAULT_INSTRUCTION
)

app = FastAPI(
    title="Google ADK Chatbot API",
    description="Backend API serving Google ADK agents to the TypeScript Light-Theme UI",
    version="2.1.0"
)

# Enable CORS for frontend development servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session managers cache
managers: Dict[str, ADKChatbotManager] = {}

class ChatRequest(BaseModel):
    message: str = Field(..., description="The user prompt text")
    session_id: str = Field(default="default_session", description="Conversation session ID")
    user_id: str = Field(default="default_user", description="Unique user ID")
    model: str = Field(default=DEFAULT_MODEL, description="Gemini model identifier")
    instruction: Optional[str] = Field(default=DEFAULT_INSTRUCTION, description="Custom system instruction")
    enable_search: bool = Field(default=False, description="Enable ADK Google Search grounding tool")

class ResetSessionRequest(BaseModel):
    session_id: str
    user_id: str

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "adk_version": "2.1.0",
        "project": os.getenv("GOOGLE_CLOUD_PROJECT", "vtxdemos"),
        "location": os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    }

@app.get("/api/models")
async def get_models():
    """Returns the list of supported Gemini models."""
    return {
        "default": DEFAULT_MODEL,
        "models": list(SUPPORTED_MODELS.values())
    }

def get_or_create_manager(user_id: str, model: str, instruction: str, enable_search: bool) -> ADKChatbotManager:
    if user_id not in managers:
        managers[user_id] = ADKChatbotManager(
            model=model,
            instruction=instruction,
            enable_search=enable_search,
            app_name="adk_ts_light_chatbot"
        )
    else:
        managers[user_id].update_configuration(
            model=model,
            instruction=instruction,
            enable_search=enable_search
        )
    return managers[user_id]

@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest):
    """
    Server-Sent Events (SSE) streaming endpoint for ADK agent responses.
    """
    manager = get_or_create_manager(
        user_id=req.user_id,
        model=req.model,
        instruction=req.instruction or DEFAULT_INSTRUCTION,
        enable_search=req.enable_search
    )

    async def event_generator():
        try:
            async for event in manager.stream_turn(
                user_id=req.user_id,
                session_id=req.session_id,
                user_message=req.message
            ):
                yield {
                    "event": "message",
                    "data": json.dumps(event, ensure_ascii=False)
                }
            
            # Send done event
            yield {
                "event": "done",
                "data": json.dumps({"type": "done"})
            }
        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"type": "error", "message": str(e)})
            }

    return EventSourceResponse(event_generator())

@app.post("/api/session/reset")
async def reset_session(req: ResetSessionRequest):
    if req.user_id in managers:
        del managers[req.user_id]
    return {"status": "ok", "message": "Session reset successfully"}

# Mount frontend build if available
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = frontend_dist / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dist / "index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8005, reload=True)
