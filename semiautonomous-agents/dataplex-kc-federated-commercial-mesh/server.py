#!/usr/bin/env python3
"""
FastAPI Backend Server for the Dataplex Knowledge Catalog & Federated Commercial Mesh.

Exposes:
  - GET  /api/health
  - GET  /api/bq-explorer       (Live BigQuery metadata, row counts: 500, 500, 120, 150, 120, 14 & sample rows from vtxdemos.commercial_mesh_gold)
  - GET  /api/demo-parts        (5 concise Python walkthrough parts, code, architectural explanations, and pre-verified outputs)
  - POST /api/run-demo-part     (Executes part1..part5 live against vtxdemos.commercial_mesh_gold + gemini-3.8-flash @ global)
  - GET  /api/catalog           (24 benchmark questions, confidence %, missing artifacts, tier summary, blockers, governance table)
  - GET  /api/questions         (alias for frontend hydration)
  - GET  /api/artifacts         (returns config/tools.yaml and config/bigquery_gold_views.sql)
  - POST /api/simulate-question (4-tier federated router + Python counterfactual simulator)
  - POST /api/copilot/chat      (Vertex AI Gemini 3.8 Flash Architect Copilot @ global)
  - POST /api/antigravity/send  (Dispatches architectural blueprints into Antigravity IDE via agentapi)
"""

from __future__ import annotations

import glob
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_LOCAL_VENV_SITE = glob.glob(
    str(Path(__file__).resolve().parent / ".venv" / "lib" / "python*" / "site-packages")
)
for _p in _LOCAL_VENV_SITE:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from agent.mesh_orchestrator import (
    BASE_DIR,
    BQ_DATASET_ID,
    BQ_PROJECT_ID,
    GOLD_VIEWS_SQL_PATH,
    TOOLS_YAML_PATH,
    FederatedCommercialMeshOrchestrator,
)
from data.synthetic_topology_seed import (
    CATALOG_PATH,
    DB_PATH,
    build_sqlite_db,
    write_catalog_json,
)

app = FastAPI(
    title="Dataplex Knowledge Catalog & Federated Commercial Mesh API",
    version="2026.10.2",
    description=(
        "Enterprise B2B Commercial Intelligence Reference Architecture: "
        "BigQuery `vtxdemos.commercial_mesh_gold` + Dataplex Knowledge Catalog + "
        "Google MCP Toolbox + Vertex AI Gemini 3.8 Flash Federated Multi-Tool Agent."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = FederatedCommercialMeshOrchestrator()


@app.on_event("startup")
def ensure_seed_data() -> None:
    if not DB_PATH.exists() or not CATALOG_PATH.exists():
        build_sqlite_db()
        write_catalog_json()


class SimulateQuestionRequest(BaseModel):
    question_id: Optional[str] = Field(default="Q-001", description="Question ID (e.g. Q-001)")
    code: Optional[str] = None
    question: Optional[str] = None
    tier: Optional[str] = None
    systems_involved: Optional[List[str]] = None
    blocker_flags: Optional[List[str]] = None
    custom_params: Optional[Dict[str, Any]] = None


class RunDemoPartRequest(BaseModel):
    part_id: str = Field(default="part1", description="Demo part identifier ('part1'..'part5')")


class CopilotChatRequest(BaseModel):
    message: str = Field(..., description="User question or instruction for the AI Architect Copilot")
    question_id: Optional[str] = Field(default=None, description="Selected benchmark question ID")
    question_code: Optional[str] = None
    question_text: Optional[str] = None
    tier: Optional[str] = None
    confidence_pct: Optional[int] = None
    missing_artifacts: Optional[List[str]] = None
    systems_involved: Optional[List[str]] = None
    blocker_flags: Optional[List[str]] = None
    dax_formula: Optional[str] = None
    gold_view_ddl: Optional[str] = None
    history: Optional[List[Dict[str, str]]] = None
    custom_params: Optional[Dict[str, Any]] = None


class AntigravitySendRequest(BaseModel):
    prompt: str = Field(..., description="Architectural prompt or blueprint to send to Antigravity IDE agent")
    question_id: Optional[str] = None
    code: Optional[str] = None
    conversation_id: Optional[str] = None


@app.get("/api/health")
def health_check() -> Dict[str, Any]:
    return {
        "status": "ok",
        "service": "dataplex-kc-federated-commercial-mesh",
        "bigquery_dataset": f"{BQ_PROJECT_ID}.{BQ_DATASET_ID}",
        "sqlite_db_ready": DB_PATH.exists(),
        "catalog_ready": CATALOG_PATH.exists(),
        "model": orchestrator.model_name,
        "location": orchestrator.location,
    }


@app.get("/api/bq-explorer")
def get_bq_explorer(refresh: bool = False) -> Dict[str, Any]:
    return orchestrator.get_bq_explorer_data(force_refresh=refresh)


@app.get("/api/demo-parts")
def get_demo_parts() -> Dict[str, Any]:
    return orchestrator.get_demo_parts_catalog()


@app.post("/api/run-demo-part")
def run_demo_part(req: RunDemoPartRequest) -> Dict[str, Any]:
    try:
        return orchestrator.run_demo_part_live(part_id=req.part_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/catalog")
@app.get("/api/questions")
def get_catalog() -> Dict[str, Any]:
    ensure_seed_data()
    return orchestrator.load_catalog()


@app.get("/api/artifacts")
def get_config_artifacts() -> Dict[str, str]:
    tools_yaml = TOOLS_YAML_PATH.read_text(encoding="utf-8") if TOOLS_YAML_PATH.exists() else ""
    gold_views_sql = GOLD_VIEWS_SQL_PATH.read_text(encoding="utf-8") if GOLD_VIEWS_SQL_PATH.exists() else ""
    return {
        "tools_yaml": tools_yaml,
        "bigquery_gold_views_sql": gold_views_sql,
    }


@app.post("/api/simulate-question")
def simulate_question(req: SimulateQuestionRequest) -> Dict[str, Any]:
    ensure_seed_data()
    qid = req.question_id or req.code or "Q-001"
    try:
        return orchestrator.simulate_question_execution(
            question_id=qid,
            custom_params=req.custom_params,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/copilot/chat")
def copilot_chat(req: CopilotChatRequest) -> Dict[str, Any]:
    ensure_seed_data()
    qid = req.question_code or req.question_id
    frontend_ctx = {
        "question_code": req.question_code,
        "question_text": req.question_text,
        "tier": req.tier,
        "confidence_pct": req.confidence_pct,
        "missing_artifacts": req.missing_artifacts,
        "systems_involved": req.systems_involved,
        "blocker_flags": req.blocker_flags,
        "dax_formula": req.dax_formula,
        "gold_view_ddl": req.gold_view_ddl,
        "history": req.history,
    }
    result = orchestrator.copilot_architect_chat(
        user_message=req.message,
        question_id=qid,
        custom_params=req.custom_params,
        frontend_context=frontend_ctx,
    )
    return {
        **result,
        "response": result["reply"],
        "content": result["reply"],
    }


@app.post("/api/antigravity/send")
def antigravity_send(req: AntigravitySendRequest) -> Dict[str, Any]:
    qid = req.question_id or req.code
    return orchestrator.dispatch_to_antigravity_agent(
        prompt_text=req.prompt,
        conversation_id=req.conversation_id,
        question_id=qid,
    )


FRONTEND_DIST = BASE_DIR / "frontend" / "dist"
if FRONTEND_DIST.exists():
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        candidate = FRONTEND_DIST / full_path
        if full_path and candidate.exists() and candidate.is_file():
            return FileResponse(str(candidate))
        index_html = FRONTEND_DIST / "index.html"
        if index_html.exists():
            return FileResponse(str(index_html))
        return {"message": "Dataplex KC Federated Commercial Mesh API is running."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8094, reload=False)
