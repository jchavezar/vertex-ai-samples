"""FastAPI Gateway for Legacy to AI-Native Modernization Hub."""

import asyncio
import json
import os
import time
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .agent_service import generate_board_memo, process_agent_query
from .bigquery_service import execute_chain_step_bigquery
from .legacy_data import query_legacy_database
from .models import (
    AgentQueryRequest,
    AgentQueryResponse,
    BoardMemoRequest,
    BoardMemoResponse,
    LegacyQueryFilter,
    LegacyQueryResponse,
    RefactorPipelineStatus,
    ShockImpactData,
    ShockParameters,
)
from .refactor_engine import run_autonomous_refactor_stream
from .shock_engine import compute_shock_impact

# Load environment overrides
load_dotenv(override=True)

app = FastAPI(
    title="Legacy to AI-Native Modernization Hub Backend",
    description="High-Impact Executive Briefing Center (EBC) Showcase for Autonomous Refactoring and Agent-Native UI",
    version="1.0.0",
)

# CORS middleware for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "legacy-to-ai-modernization-hub",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "model_target": os.getenv("GEMINI_MODEL", "gemini-3.7-flash"),
    }


# ==========================================
# 1. LEGACY 2015 ENTERPRISE ERP ENDPOINTS
# ==========================================

@app.post("/api/legacy/query", response_model=LegacyQueryResponse)
async def query_legacy(filter_req: LegacyQueryFilter):
    """
    Simulates a clunky, high-latency 2015 Enterprise ERP query across 20 dense columns.
    """
    records, total_count, latency_ms = await query_legacy_database(filter_req)
    total_pages = max(1, (total_count + filter_req.page_size - 1) // filter_req.page_size)

    return LegacyQueryResponse(
        total_records=total_count,
        page=filter_req.page,
        page_size=filter_req.page_size,
        total_pages=total_pages,
        query_latency_ms=round(latency_ms, 2),
        data=records,
        server_timestamp=time.strftime("%Y-%m-%d %H:%M:%S EST"),
        db_engine="Oracle Exadata 11g R2 (Legacy Connector // Host: erp-prod-db04.corp)",
    )


@app.post("/api/legacy/export-csv")
async def export_legacy_csv():
    """
    Simulates the dreaded legacy batch CSV export queue.
    """
    job_id = f"JOB-EXPORT-{int(time.time())}"
    return {
        "job_id": job_id,
        "status": "QUEUED_BATCH_PROCESSING",
        "estimated_wait_time": "14 minutes 30 seconds",
        "message": "Your report request has been enqueued to overnight batch cluster. An email with a secured ZIP link will be sent when the export completes.",
        "queue_position": 47,
        "queue_server": "batch-worker-prod-08.corp",
    }


@app.get("/api/legacy/execute-chain-step/{step_id}")
@app.post("/api/legacy/execute-chain-step/{step_id}")
async def execute_chain_step(step_id: int):
    """
    Executes a real BigQuery SQL query corresponding to the selected multi-department step.
    Measures real GCP query latency and returns true cloud data.
    """
    return execute_chain_step_bigquery(step_id)


# ==========================================
# 2. AUTONOMOUS REFACTOR PIPELINE (SSE STREAM)
# ==========================================

@app.get("/api/refactor/stream")
async def stream_refactor_pipeline():
    """
    Server-Sent Events (SSE) stream demonstrating the 3-stage Antigravity Autonomous Refactor.
    Stage 1: Schema Discovery -> Stage 2: ADK Tool Synthesis -> Stage 3: Generative Canvas.
    """
    async def event_generator():
        async for event_data in run_autonomous_refactor_stream():
            yield f"data: {json.dumps(event_data)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


# ==========================================
# 3. 2026 AGENT-NATIVE WHAT-IF SHOCK ENGINE
# ==========================================

@app.post("/api/shock/calculate", response_model=ShockImpactData)
async def calculate_shock(params: ShockParameters):
    """
    Real-time 50ms quantitative shock impact calculation.
    """
    return compute_shock_impact(params)


@app.post("/api/agent/query", response_model=AgentQueryResponse)
async def agent_query(request: AgentQueryRequest):
    """
    Natural Language Query handler powered by Gemini 2.5 Flash / Gemini 3.
    """
    return await process_agent_query(request)


@app.post("/api/agent/board-memo", response_model=BoardMemoResponse)
async def board_memo(request: BoardMemoRequest):
    """
    One-click Executive Boardroom Decision Memorandum Generator.
    """
    return await generate_board_memo(request)


def start():
    """Entry point for local server execution."""
    import uvicorn
    port = int(os.getenv("PORT", "8008"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)


if __name__ == "__main__":
    start()
