"""Weil Legal-Tech Innovation Showcase — FastAPI Server.

Powers the Single-Pane-of-Glass Legal Cockpit with:
- Google ADK Multi-Agent Orchestration & Real-Time SSE Streaming
- Antigravity Managed Agent Sandbox Runtime & Forensic Wire-Tap
- Model Context Protocol (MCP) Gateway for iManage & Legal Databases
"""
from __future__ import annotations
import os
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel

from backend.services.mcp_service import mcp_gateway
from backend.services.adk_service import adk_orchestrator
from backend.services.antigravity_service import antigravity_sandbox

app = FastAPI(
    title="Weil Legal-Tech Innovation API",
    description="Backend service powering ADK Multi-Agent and Antigravity Managed Sandbox showcases.",
    version="1.0.0"
)

# Enable CORS for local Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request Models
# ---------------------------------------------------------------------------
class ADKWorkflowRequest(BaseModel):
    prompt: str
    matter_id: str = "MATTER-9042"
    client_name: str = "Apex Pharma Inc."
    attorney_email: str = "jesusarguelles@google.com"
    runtime_target: str = "local"  # "local" or "cloud_agent_runtime"


class SandboxTaskRequest(BaseModel):
    prompt: str
    matter_id: str = "MATTER-9042"
    claim_amount_millions: float = 45.0


class LegoHarmonizeRequest(BaseModel):
    clause_ids: list[str]
    posture: str = "aggressive"


ADKWorkflowRequest.model_rebuild()
SandboxTaskRequest.model_rebuild()
LegoHarmonizeRequest.model_rebuild()


# ---------------------------------------------------------------------------
# 1. Google ADK Multi-Agent Endpoints
# ---------------------------------------------------------------------------
@app.post("/api/adk/stream")
async def run_adk_workflow_stream(req: ADKWorkflowRequest):
    """Server-Sent Events endpoint streaming live parallel deliberation across 4 subagent lanes.
    Supports either Local Orchestrator or Cloud Agent Runtime (Vertex AI).
    """
    if req.runtime_target == "cloud_agent_runtime":
        stream_gen = adk_orchestrator.stream_cloud_agent_runtime(
            prompt=req.prompt,
            matter_id=req.matter_id,
            attorney_email=req.attorney_email,
            client_name=req.client_name
        )
    else:
        stream_gen = adk_orchestrator.stream_workflow(
            prompt=req.prompt,
            matter_id=req.matter_id,
            attorney_email=req.attorney_email,
            client_name=req.client_name
        )

    return StreamingResponse(
        stream_gen,
        media_type="text/event-stream"
    )


# ---------------------------------------------------------------------------
# 2. Antigravity Managed Agent Sandbox Endpoints
# ---------------------------------------------------------------------------
@app.post("/api/antigravity/stream")
async def run_sandbox_task_stream(req: SandboxTaskRequest):
    """Server-Sent Events endpoint streaming the Linux MicroVM terminal wire-tap & artifacts."""
    return StreamingResponse(
        antigravity_sandbox.stream_sandbox_task(
            prompt=req.prompt,
            matter_id=req.matter_id,
            dispute_amount_millions=req.claim_amount_millions
        ),
        media_type="text/event-stream"
    )


@app.get("/api/sandbox/files")
def get_sandbox_files():
    """List virtual files persisted inside `/workspace`."""
    return {"files": antigravity_sandbox.list_workspace_files()}


@app.get("/api/sandbox/file/{filename:path}")
def get_sandbox_file_content(filename: str):
    """Read full content of a specific file inside `/workspace`."""
    full_path = f"/workspace/{filename}" if not filename.startswith("/workspace/") else filename
    if full_path in antigravity_sandbox.workspace_files:
        return antigravity_sandbox.workspace_files[full_path]
    raise HTTPException(status_code=404, detail=f"File {full_path} not found on sandbox disk.")


# ---------------------------------------------------------------------------
# 3. Model Context Protocol (MCP) Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/mcp/tools")
def list_mcp_tools():
    """List registered Model Context Protocol tools."""
    return {"tools": mcp_gateway.list_tools()}


@app.get("/api/mcp/imanage/search")
def search_imanage(
    q: str = Query(..., description="Search query"),
    matter_id: Optional[str] = Query(None, description="Requesting matter ID"),
    attorney: Optional[str] = Query(None, description="Attorney email")
):
    """Search iManage DMS documents with automatic ethical wall filtering."""
    return mcp_gateway.imanage_search_precedents(query=q, matter_id=matter_id, attorney_email=attorney)


@app.get("/api/mcp/clauses")
def list_lego_clauses():
    """List all available modular Lego clauses in the Privacy Pro repository."""
    return {"clauses": list(mcp_gateway.lego_clauses.values())}


@app.post("/api/mcp/lego/harmonize")
def harmonize_lego_clauses(req: LegoHarmonizeRequest):
    """Run Gemini 3.7 Flash Contract Harmonization & Risk Audit on selected clauses."""
    return mcp_gateway.harmonize_contract(clause_ids=req.clause_ids, posture=req.posture)


@app.get("/api/mcp/clause/{clause_id}")
def get_lego_clause(clause_id: str):
    """Get a specific modular clause by ID."""
    res = mcp_gateway.fetch_lego_clause(clause_id)
    if not res.get("found"):
        raise HTTPException(status_code=404, detail=res.get("error"))
    return res


@app.get("/api/mcp/citations/verify")
def verify_citation(citation: str = Query(...), court: Optional[str] = None):
    """Verify legal case law citation against Delaware, SDNY, and CJEU records."""
    return mcp_gateway.verify_case_citation(citation_or_name=citation, court=court)


@app.get("/api/mcp/ethical-wall/check")
def check_ethical_wall(
    source_matter: str = Query(...),
    target_matter: str = Query(...),
    attorney: Optional[str] = None
):
    """Evaluate Chinese wall conflict barrier between two matters."""
    return mcp_gateway.enforce_ethical_wall(
        source_matter=source_matter,
        target_matter=target_matter,
        attorney_email=attorney
    )


# ---------------------------------------------------------------------------
# 4. Health & Status
# ---------------------------------------------------------------------------
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Weil Legal-Tech Innovation Hub",
        "adk_ready": True,
        "antigravity_sandbox_ready": True,
        "mcp_gateway_ready": True,
        "port": 8000
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
