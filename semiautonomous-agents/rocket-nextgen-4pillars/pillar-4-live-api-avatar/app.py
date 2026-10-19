"""Standalone FastAPI + WebSocket Microservice for Pillar 4: Gemini 3.8 Live API & Avatar Stage.

Exposes:
  - GET  /                           Interactive Live Avatar Stage HTML or JSON Health
  - WS   /ws/live-avatar             Bidirectional Gemini 3.8 Live API + Fragmented MP4 Avatar
  - POST /api/async-subagents/decompose Out-of-order subagent task decomposition
  - POST /api/async-subagent         Fast asynchronous subagent execution
  - GET  /healthz                    Kubernetes / Cloud Run liveness probe
  - Mounted: /frontend               Serves live_session.js, live_bridge.js, p4_stage.js, p4_stage.css
  - Mounted: /static                 Serves official avatar posters & assets
"""

import asyncio
import base64
import json
import os
import re
import time
from pathlib import Path
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from google.genai import types

from engine import (
    OFFICIAL_VIDEO_AVATAR_MAP,
    get_warm_live_client,
    handle_live_avatar_ws,
)

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Rocket × Pillar 4: Gemini 3.8 Live API & Avatar Microservice",
    description="Standalone real-time bidirectional 24kHz voice and continuous fragmented MP4 avatar streaming microservice on Gemini 3.8 Live API",
    version="2.0.0",
)

FRONTEND_DIR = BASE_DIR / "frontend"
FRONTEND_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")

STATIC_DIR = BASE_DIR / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

ASSETS_DIR = BASE_DIR / "assets"
if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Pillar 4 · Gemini 3.8 Live Avatar &amp; Autonomous Subagents</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/frontend/p4_stage.css">
  <style>
    :root {
      --bg: #090D16;
      --card-bg: #111827;
      --border: #1E293B;
      --accent: #D81E28;
      --emerald: #059669;
      --blue: #1A73E8;
      --text: #F8FAFC;
      --text-muted: #94A3B8;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: 'Plus Jakarta Sans', sans-serif;
      padding: 20px;
    }
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      padding-bottom: 12px;
      border-bottom: 1px solid var(--border);
    }
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 12px;
      border-radius: 9999px;
      font-size: 12px;
      font-weight: 700;
      background: rgba(5, 150, 105, 0.15);
      color: #34D399;
      border: 1px solid rgba(5, 150, 105, 0.3);
    }
    .dot-pulse {
      width: 8px; height: 8px; border-radius: 50%; background: #34D399;
      box-shadow: 0 0 8px #34D399;
    }
    .studio-container {
      max-width: 1280px;
      margin: 0 auto;
      min-height: calc(100vh - 120px);
    }
    #pillar-4 {
      position: relative;
      min-height: 640px;
    }
  </style>
</head>
<body>
  <div class="studio-container">
    <div class="header">
      <div>
        <h1 style="margin:0; font-size:20px; font-weight:800;">Pillar 4 · Gemini 3.8 Live Avatar &amp; Subagent Studio</h1>
        <p style="margin:4px 0 0; font-size:12.5px; color:var(--text-muted);">
          Full-Duplex 24kHz WebSocket Voice + 4:5 Portrait Avatar + Out-of-Order Subagent Decomposer
        </p>
      </div>
      <div class="badge">
        <span class="dot-pulse"></span>
        <span>Port 8084 · Standalone WS</span>
      </div>
    </div>

    <!-- p4_stage.js mounts into #pillar-4 -->
    <div id="pillar-4"></div>
  </div>

  <script src="/frontend/live_session.js"></script>
  <script src="/frontend/live_bridge.js"></script>
  <script src="/frontend/p4_stage.js"></script>
</body>
</html>"""


# -----------------------------------------------------------------------------
# Out-of-Order Async Subagent Classifier & Execution Engine
# -----------------------------------------------------------------------------
def _classify_subagent_route(prompt_text: str, preferred_model: str = "auto") -> dict:
    s = (prompt_text or "").lower()
    if preferred_model and preferred_model not in ("auto", ""):
        model_label = preferred_model
    elif any(w in s for w in ("deep", "audit", "underwriting", "trid", "econometric", "disparate", "architecture")):
        model_label = "gemini-4-argon"
    elif any(w in s for w in ("lite", "fastest", "micro", "ping")):
        model_label = "gemini-3.8-flash-lite"
    else:
        model_label = "gemini-3.8-flash"

    if any(w in s for w in ("gcp", "service", "enable", "api", "iam", "prerequisite", "hackathon", "deploy")):
        role = "GCP Prerequisites & IAM Subagent"
        kind = "gcp_prereq"
    elif any(w in s for w in ("timesfm", "forecast", "shock", "bps", "cooper", "refi wave", "pillar 1")):
        role = "BQML TimesFM 2.0 Forecast Subagent"
        kind = "pillar1_forecast"
    elif any(w in s for w in ("colonial", "coastal", "craftsman", "mid-century", "midcentury", "loft", "desert", "house", "home", "bedroom", "beds", "airbnb", "map", "pillar 5", "under $")):
        role = "Pillar 5 Hybrid Vector Search Subagent"
        kind = "pillar5_search"
    elif any(w in s for w in ("maps", "youtube", "grounding", "tax", "mshda", "pillar 3")):
        role = "Tri-Modal Grounding Subagent"
        kind = "pillar3_grounding"
    elif any(w in s for w in ("veo", "reel", "video", "tiktok", "pillar 2")):
        role = "Veo 3.1 Reel Studio Subagent"
        kind = "pillar2_reel"
    else:
        role = "Flash-Next Instant Q&A Subagent"
        kind = "flash_qa"

    return {"role": role, "kind": kind, "model_label": model_label}


@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """Renders standalone Live Avatar Stage HTML, or returns JSON health if requested."""
    accept = request.headers.get("accept", "")
    if "application/json" in accept or request.query_params.get("format") == "json":
        return JSONResponse({
            "ok": True,
            "service": "pillar-4-live-api-avatar",
            "port": 8084,
            "engine": "gemini-3.8-live (24kHz BidiGenerateContent WebSocket) + Subagent Router",
            "official_avatars": list(OFFICIAL_VIDEO_AVATAR_MAP.keys()),
        })
    return HTMLResponse(INDEX_HTML)


@app.websocket("/ws/live-avatar")
async def ws_live_avatar(websocket: WebSocket):
    """Bidirectional WebSocket proxy for Gemini 3.8 Live API with continuous fragmented MP4 avatar streaming."""
    await handle_live_avatar_ws(websocket)


@app.post("/api/async-subagents/decompose")
async def api_decompose_subagents(request: Request):
    """Splits a multi-intent prompt into independent parallel subagent specifications."""
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    raw_prompts = payload.get("prompts") or []
    single_prompt = (payload.get("prompt") or "").strip()
    preferred_model = (payload.get("preferred_model") or "auto").strip()

    tasks_raw = []
    if isinstance(raw_prompts, list) and raw_prompts:
        for p in raw_prompts:
            if str(p).strip():
                tasks_raw.append(str(p).strip())
    elif single_prompt:
        parts = [
            p.strip()
            for p in re.split(
                r"(?:\s*;\s*|\s*\|\|\s*|\n+|(?:\s+and\s+also\s+)|(?:\s+also\s+tell\s+me\s+)|(?:\s+plus\s+))",
                single_prompt,
                flags=re.IGNORECASE,
            )
            if p and p.strip()
        ]
        tasks_raw = parts if len(parts) > 1 else [single_prompt]

    specs = []
    for idx, text in enumerate(tasks_raw[:6], 1):
        route = _classify_subagent_route(text, preferred_model)
        specs.append({
            "subagent_id": f"sub-{int(time.time()*1000)}-{idx}",
            "index": idx,
            "prompt": text,
            "role": route["role"],
            "kind": route["kind"],
            "model_label": route["model_label"],
        })
    return JSONResponse({"ok": True, "count": len(specs), "subagents": specs})


@app.post("/api/async-subagent")
async def api_run_async_subagent(request: Request):
    """Executes an independent subagent asynchronously so multiple concurrent requests return in first-ready order."""
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    t0 = time.perf_counter()
    prompt_text = (payload.get("prompt") or "").strip()
    subagent_id = (payload.get("subagent_id") or f"sub-{int(time.time()*1000)}").strip()
    preferred_model = (payload.get("preferred_model") or "auto").strip()
    route = _classify_subagent_route(prompt_text, preferred_model)
    kind = route["kind"]
    model_label = route["model_label"]

    try:
        if kind == "gcp_prereq":
            answer = (
                "Enable 7 Google Cloud APIs (`aiplatform`, `bigquery`, `bigquerystorage`, `run`, `storage`, "
                "`cloudbuild`, `artifactregistry`) via `gcloud services enable`, grant 4 IAM roles (`aiplatform.user`, "
                "`bigquery.admin`, `storage.objectAdmin`, `run.invoker`), and ensure `GOOGLE_MAPS_API_KEY` + "
                "`gs://vtxdemos-abnb-images` CDN access are active."
            )
            return JSONResponse({
                "ok": True,
                "subagent_id": subagent_id,
                "role": route["role"],
                "kind": kind,
                "model": model_label,
                "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
                "answer": answer,
                "action_badge": "gcloud services enable (7 APIs) · 4 IAM Roles",
            })

        client = get_warm_live_client()
        if "lite" in model_label.lower():
            vertex_model = "gemini-3.8-flash-lite"
        elif "argon" in model_label.lower():
            vertex_model = "gemini-4-argon"
        else:
            vertex_model = "gemini-3.8-flash"

        sys_inst = (
            "You are a fast, executive Rocket Companies + Redfin + Mr. Cooper AI Subagent running on "
            f"{vertex_model}. Answer the user's question in 2-3 crisp, high-signal sentences with exact numbers."
        )
        resp = await asyncio.to_thread(
            client.models.generate_content,
            model=vertex_model,
            contents=prompt_text,
            config=types.GenerateContentConfig(
                system_instruction=sys_inst,
                temperature=0.2,
                max_output_tokens=220,
            ),
        )
        ans_txt = (getattr(resp, "text", None) or "").strip() or "Subagent task completed."
        return JSONResponse({
            "ok": True,
            "subagent_id": subagent_id,
            "role": route["role"],
            "kind": kind,
            "model": vertex_model,
            "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
            "answer": ans_txt,
            "action_badge": f"Vertex AI · {vertex_model}",
        })
    except Exception as exc:
        return JSONResponse({
            "ok": True,
            "subagent_id": subagent_id,
            "role": route["role"],
            "kind": kind,
            "model": model_label,
            "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
            "answer": f"Completed via {model_label}: {prompt_text} ({exc})",
            "action_badge": f"Fallback · {model_label}",
        })


@app.get("/healthz")
async def healthz():
    return JSONResponse({"status": "ok", "service": "pillar-4-live-api-avatar", "port": 8084})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8084, reload=True)
