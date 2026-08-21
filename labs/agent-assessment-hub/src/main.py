"""Interface and Application Server for Agent Assessment Hub.

Provides FastAPI REST endpoints, health probes, OpenTelemetry telemetry middleware,
and a CLI runner for interactive local testing.
"""

import sys
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from src.config import settings
from src.agent import orchestrator
from src.memory import memory_store
from src.tools import available_tools, query_cloud_run_logs, analyze_service_metrics, apply_service_remediation
from src.observability import logger, trace_span

app = FastAPI(
    title="Autonomous SRE Assessment Agent",
    description="Production-ready Agent built with Google ADK, Gemini 2.5 Flash, and Cloud Observability",
    version="0.1.0",
)


class ChatRequest(BaseModel):
    session_id: str = Field(default="default-session", description="Session identifier for multi-turn context")
    message: str = Field(..., description="User message or incident description")


class ChatResponse(BaseModel):
    session_id: str
    status: str
    model: str
    response: str
    history_turns: int


@app.get("/healthz")
def health_check() -> Dict[str, str]:
    """Kubernetes / Cloud Run liveness and readiness probe."""
    return {"status": "HEALTHY", "model": settings.model, "environment": "production"}


@app.get("/api/v1/tools")
def list_tools() -> Dict[str, Any]:
    """Returns available tools and their schema metadata."""
    tools_info = []
    for tool in available_tools:
        tools_info.append({
            "name": tool.__name__,
            "description": tool.__doc__.split("\n\n")[0] if tool.__doc__ else "Custom Tool",
        })
    return {"count": len(tools_info), "tools": tools_info}


@app.get("/api/v1/session/{session_id}")
def get_session_history(session_id: str) -> Dict[str, Any]:
    """Retrieves context memory and message history for a given session."""
    session = memory_store.get_or_create_session(session_id)
    return {
        "session_id": session.session_id,
        "turns": len(session.history),
        "history": [msg.model_dump() for msg in session.history],
        "variables": session.variables,
    }


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Main Agent Chat interface handling multi-turn orchestration."""
    try:
        result = await orchestrator.process_user_query(
            session_id=request.session_id,
            query=request.message,
        )
        return ChatResponse(**result)
    except Exception as e:
        logger.error(f"Failed to process chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def run_cli():
    """Interactive command-line interface for running the agent directly."""
    import asyncio
    print(f"==================================================")
    print(f"   Autonomous SRE Agent CLI (Model: {settings.model})")
    print(f"==================================================")
    
    session_id = "cli-interactive-session"
    print("Agent initialized. Type 'exit' to quit.\n")
    
    while True:
        try:
            user_input = input("User> ")
            if user_input.strip().lower() in ["exit", "quit"]:
                break
            if not user_input.strip():
                continue
            
            result = asyncio.run(orchestrator.process_user_query(session_id, user_input))
            print(f"\nAgent>\n{result['response']}\n")
        except (KeyboardInterrupt, EOFError):
            break


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        run_cli()
    else:
        logger.info(f"Starting Agent Assessment Server on port {settings.port}...")
        uvicorn.run("src.main:app", host="0.0.0.0", port=settings.port, reload=False)
