"""Standalone FastAPI Microservice for Pillar 3: Tri-Modal Grounding (Ask Redfin 2.0).

Exposes:
  - GET  /                  Ask Redfin 2.0 Grounded Chat Studio HTML or JSON Health
  - POST /api/pillar3/chat  NDJSON Streaming Grounded Chat (Google Maps + YouTube + Google Search)
  - POST /api/pillar3/ground Run Tri-Modal Grounding (batch)
  - GET  /healthz           Kubernetes / Cloud Run liveness probe
  - Mounted: /frontend      Serves p3_chat.js and p3_chat.css
"""

import asyncio
import json
import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from engine import run_trimodal_grounding, stream_grounded_chat

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Rocket × Pillar 3: Tri-Modal Grounding Microservice (Ask Redfin 2.0)",
    description="Standalone streaming conversational grounding microservice combining Google Maps (250M+ Places), YouTube video tour inspection, and Google Search live citations on gemini-3.8-flash",
    version="2.0.0",
)

FRONTEND_DIR = BASE_DIR / "frontend"
FRONTEND_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")

ASSETS_DIR = BASE_DIR / "assets"
if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Pillar 3 · Ask Redfin 2.0 Tri-Modal Grounding Studio</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <link rel="stylesheet" href="/frontend/p3_chat.css">
  <style>
    :root {
      --bg: #090D16;
      --card-bg: #111827;
      --border: #1E293B;
      --accent: #D81E28;
      --blue: #1A73E8;
      --emerald: #059669;
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
      background: rgba(26, 115, 232, 0.15);
      color: #60A5FA;
      border: 1px solid rgba(26, 115, 232, 0.3);
    }
    .dot-pulse {
      width: 8px; height: 8px; border-radius: 50%; background: #60A5FA;
      box-shadow: 0 0 8px #60A5FA;
    }
    .studio-grid {
      display: grid;
      grid-template-columns: 1fr 420px;
      gap: 20px;
      height: calc(100vh - 110px);
      min-height: 600px;
    }
    @media (max-width: 980px) {
      .studio-grid { grid-template-columns: 1fr; height: auto; }
    }
    .chat-panel {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 16px;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    .side-panel {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .map-box, .yt-box {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 16px;
      overflow: hidden;
      flex: 1;
      display: flex;
      flex-direction: column;
    }
    .box-title {
      padding: 10px 14px;
      font-size: 12px;
      font-weight: 700;
      color: var(--text-muted);
      border-bottom: 1px solid var(--border);
      background: #0B111E;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    #grounding-map { width: 100%; height: 100%; min-height: 240px; }
    #p3-yt-iframe { width: 100%; height: 100%; min-height: 220px; border: none; }
  </style>
</head>
<body>
  <div class="header">
    <div>
      <h1 style="margin:0; font-size:20px; font-weight:800;">Pillar 3 · Tri-Modal Grounding Studio (Ask Redfin 2.0)</h1>
      <p style="margin:4px 0 0; font-size:12.5px; color:var(--text-muted);">
        Google Maps (250M+ POIs) + YouTube Multimodal Tour Inspection + Google Search Live Citations
      </p>
    </div>
    <div class="badge">
      <span class="dot-pulse"></span>
      <span>Port 8083 · Standalone</span>
    </div>
  </div>

  <div class="studio-grid" id="pillar-3">
    <!-- Center: Conversational Ask Redfin 2.0 Chat Engine -->
    <div class="chat-panel" id="p3c-root">
      <!-- p3_chat.js mounts into #pillar-3 -->
    </div>

    <!-- Right: Visual Grounding Displays (Leaflet Map & YouTube Inspector) -->
    <div class="side-panel">
      <div class="map-box">
        <div class="box-title">
          <span>Google Maps Grounding (Places API New)</span>
          <span style="font-size:11px;color:#60A5FA;">Leaflet Pins</span>
        </div>
        <div id="grounding-map"></div>
      </div>
      <div class="yt-box">
        <div class="box-title">
          <span>YouTube Video Tour Grounding</span>
          <span style="font-size:11px;color:#F87171;">gemini-3.8-flash Part</span>
        </div>
        <iframe id="p3-yt-iframe" src="https://www.youtube-nocookie.com/embed/S_vLp1e39hM?enablejsapi=1" allowfullscreen></iframe>
      </div>
    </div>
  </div>

  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script src="/frontend/p3_chat.js"></script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """Renders standalone Ask Redfin 2.0 grounding studio HTML, or returns JSON health if requested."""
    accept = request.headers.get("accept", "")
    if "application/json" in accept or request.query_params.get("format") == "json":
        return JSONResponse({
            "ok": True,
            "service": "pillar-3-trimodal-grounding",
            "port": 8083,
            "engine": "Ask Redfin 2.0 (Google Maps + YouTube + Google Search on gemini-3.8-flash)",
        })
    return HTMLResponse(INDEX_HTML)


@app.post("/api/pillar3/chat")
async def api_p3_chat(request: Request):
    """Ask Redfin 2.0 grounded chat: NDJSON stream of route | status | delta | sources | done events."""
    try:
        body = await request.json()
    except Exception:
        body = {}
    messages = body.get("messages") if isinstance(body.get("messages"), list) else []

    async def _ndjson():
        try:
            async for evt in stream_grounded_chat(
                messages=messages,
                hub_id=str(body.get("hub_id") or "royal_oak"),
                youtube_url=str(body.get("youtube_url") or ""),
            ):
                yield json.dumps(evt, ensure_ascii=False) + "\n"
        except asyncio.CancelledError:
            raise
        except Exception as e:
            yield json.dumps({"type": "delta", "text": "Grounding is briefly unavailable, please try again."}) + "\n"
            yield json.dumps({"type": "done", "latency_ms": 0, "model": "gemini-3.8-flash", "error": str(e)[:200]}) + "\n"

    return StreamingResponse(
        _ndjson(),
        media_type="application/x-ndjson",
        headers={"Cache-Control": "no-cache, no-transform", "X-Accel-Buffering": "no"},
    )


@app.post("/api/pillar3/ground")
async def api_p3_ground(request: Request):
    """Batch tri-modal grounding endpoint for quick structured evaluation."""
    try:
        body = await request.json()
    except Exception:
        body = {}
    res = run_trimodal_grounding(
        hub_id=body.get("hub_id", "royal_oak"),
        custom_maps_query=body.get("custom_maps_query", ""),
        custom_search_query=body.get("custom_search_query", ""),
        custom_youtube_url=body.get("custom_youtube_url", ""),
    )
    return JSONResponse(res)


@app.get("/healthz")
async def healthz():
    return JSONResponse({"status": "ok", "service": "pillar-3-trimodal-grounding", "port": 8083})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8083, reload=True)
