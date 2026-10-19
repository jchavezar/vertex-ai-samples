#!/usr/bin/env python3
"""
Standalone FastAPI Microservice for Rocket Demo Square [5.5]: Fair Lending Disparate Impact & Bias Audit Engine (ECOA / Reg B)
Run locally:
    pip install -r requirements.txt
    uvicorn app:app --host 0.0.0.0 --port 8080
"""
import json
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

from code.agent import execute_square_demo
from code.sandbox_tool import load_payload, run_deterministic_sandbox

app = FastAPI(
    title="Rocket AI Demo [5.5] — Fair Lending Disparate Impact & Bias Audit Engine (ECOA / Reg B)",
    version="2.0.0",
    description="ECOA Regulation B // 500-Counterfactual Twin Fair Lending & Adverse Action Certifier",
)

UI_HTML_PATH = Path(__file__).resolve().parent / "ui" / "standalone_app.html"


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    if UI_HTML_PATH.exists():
        return HTMLResponse(UI_HTML_PATH.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Rocket Square [5.5] Standalone Service Ready</h1>")


@app.get("/healthz")
async def healthz() -> JSONResponse:
    return JSONResponse({"ok": True, "square": "5.5", "title": "Fair Lending Disparate Impact & Bias Audit Engine (ECOA / Reg B)"})


@app.post("/api/sandbox")
async def api_sandbox(request: Request) -> JSONResponse:
    body: Dict[str, Any] = {}
    try:
        body = await request.json()
    except Exception:
        pass
    bundle = run_deterministic_sandbox(body.get("params"))
    return JSONResponse({
        "ok": True,
        "code": "5.5",
        "action": bundle["sandbox"].get("action"),
        "sandbox_runtime": bundle["sandbox"].get("sandbox_runtime"),
        "execution_ms": bundle["sandbox"].get("execution_ms", 0.04),
        "metrics": bundle["sandbox"].get("metrics", {}),
        "bespoke_artifact": bundle["bespoke_artifact"],
    })


@app.post("/api/run")
async def api_run(request: Request) -> JSONResponse:
    body: Dict[str, Any] = {}
    try:
        body = await request.json()
    except Exception:
        pass
    res = execute_square_demo(
        custom_input=body.get("input"),
        model_override=body.get("model"),
    )
    return JSONResponse(res)
