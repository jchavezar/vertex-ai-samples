"""
FastAPI Server for ADK Enterprise Assistant (Port 8090)
Exposing SSE streaming endpoint, session lifecycle, tool inventory, and health telemetry.
"""
from __future__ import annotations

import os
import json
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Enforce override=True per agent rules
load_dotenv(override=True)

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field

from agent import engine, DEFAULT_MODEL, APP_NAME

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("adk-enterprise-api")

app = FastAPI(
    title="ADK Enterprise Assistant Backend",
    description="Enterprise Multi-Tool Reasoning Engine powered by Google ADK and Gemini 3.7",
    version="1.0.0"
)

# CORS setup
cors_origins_str = os.environ.get("CORS_ORIGINS", "http://localhost:5174,http://127.0.0.1:5174,http://localhost:3000")
allowed_origins = [o.strip() for o in cors_origins_str.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins + ["*"], # allow flexible local dev while supporting proxy
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str = Field(..., description="User query or enterprise prompt")
    user_id: str = Field(default="enterprise_user", description="Authenticated user ID")
    session_id: str = Field(default="session_default", description="Conversation session ID")


class SessionInitRequest(BaseModel):
    user_id: str = Field(default="enterprise_user")
    session_id: Optional[str] = None


@app.get("/health")
@app.get("/api/health")
async def health_check():
    """Returns runtime health and ADK configuration status."""
    return {
        "status": "healthy",
        "app_name": APP_NAME,
        "model": DEFAULT_MODEL,
        "runner": "InMemoryRunner",
        "adk_version": "2.7.1",
        "project": os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos"),
        "location": os.environ.get("GOOGLE_CLOUD_LOCATION", "global"),
        "active_sessions_count": len(engine.active_sessions),
        "capabilities": [
            "gemini_37_reasoning_tokens",
            "google_search_grounding",
            "enterprise_data_warehouse_query",
            "python_analytical_sandbox",
            "dcf_financial_modeling",
            "dynamic_interactive_visualizations"
        ]
    }


@app.get("/api/tools")
async def list_tools():
    """Lists registered enterprise tools and schemas."""
    return {
        "tools": [
            {
                "name": "search_enterprise_knowledge",
                "category": "Search",
                "badge": "Grounding",
                "description": "Performs enterprise-grounded knowledge base and web search for industry benchmarks and market trends.",
                "color": "cyan"
            },
            {
                "name": "query_enterprise_database",
                "category": "Database Query",
                "badge": "Data Warehouse",
                "description": "Queries corporate data warehouse for ARR, Cloud Infrastructure Spend, Churn, and EBITDA metrics.",
                "color": "indigo"
            },
            {
                "name": "execute_enterprise_code",
                "category": "Code Execution",
                "badge": "Python Sandbox",
                "description": "Executes sandboxed Python code for numerical algorithms, regression, and data transformations.",
                "color": "emerald"
            },
            {
                "name": "model_financial_projections",
                "category": "Financial Modeling",
                "badge": "DCF / NPV / ROI",
                "description": "Calculates Net Present Value (NPV), Payback Period, and multi-year discounted cash flow models.",
                "color": "amber"
            },
            {
                "name": "generate_visualization_artifact",
                "category": "Dynamic Visualization",
                "badge": "Artifact Generator",
                "description": "Generates interactive multi-series charts and KPI summary widgets for the executive preview panel.",
                "color": "violet"
            }
        ]
    }


@app.post("/api/session")
async def initialize_session(req: SessionInitRequest):
    """Initializes or resets an ADK session."""
    session_id = req.session_id or f"sess_{os.urandom(4).hex()}"
    await engine.ensure_session(user_id=req.user_id, session_id=session_id)
    return {
        "status": "initialized",
        "user_id": req.user_id,
        "session_id": session_id
    }


@app.post("/api/chat")
async def chat_stream(req: ChatRequest):
    """Streams agent reasoning, tool telemetry, content deltas, and artifact objects over SSE."""
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
        
    logger.info("Received chat request (session=%s, user=%s): %r", req.session_id, req.user_id, req.message[:80])
    
    stream_generator = engine.stream_chat(
        message=req.message,
        user_id=req.user_id,
        session_id=req.session_id
    )
    
    return StreamingResponse(
        stream_generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8090))
    host = os.environ.get("HOST", "0.0.0.0")
    logger.info("Starting ADK Enterprise Assistant server on %s:%d", host, port)
    uvicorn.run("main:app", host=host, port=port, reload=True)
