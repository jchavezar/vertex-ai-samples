"""Standalone FastAPI Microservice for Pillar 5: AI Real Estate Marketplace & Hybrid Vector Search.

Exposes:
  - GET  /                                  Interactive Marketplace Studio HTML or JSON Health
  - POST /api/pillar5/search                Multimodal Hybrid Search (Semantic 45% + Visual 35% + Keyword 20%)
  - POST /api/pillar5/evaluate              Honest Multimodal Gemini Judge (8 labeled images per home)
  - GET  /api/pillar5/tours-manifest        Catalog of pre-rendered Cinematic & Veo 3.1 video tours
  - GET  /api/pillar5/listing-video/{id}    Serves / redirects to 16:9 H.264 video tour
  - GET  /healthz                           Kubernetes / Cloud Run liveness probe
  - Mounted: /frontend                      Serves p5_media.js and p5_media.css
  - Mounted: /static                        Serves static tour manifests and thumbnails
"""

import asyncio
import json
import os
import subprocess
import time
import urllib.request
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from engine import (
    evaluate_listing_live_with_gemini,
    get_catalog,
    hybrid_search_marketplace,
)

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Rocket × Pillar 5: Real Estate Marketplace Microservice",
    description="Standalone 108-home multimodal hybrid vector search, honest Gemini photo judge, and pre-rendered cinematic/Veo tour delivery microservice",
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

GCS_MEDIA_BUCKET = os.environ.get("GCS_MEDIA_BUCKET", "vtxdemos-abnb-images")
_TOURS_MANIFEST_PATH = STATIC_DIR / "tours_manifest.json" if STATIC_DIR.exists() else BASE_DIR / "tours_manifest.json"
_VEO_MANIFEST_PATH = STATIC_DIR / "veo_tours_manifest.json" if STATIC_DIR.exists() else BASE_DIR / "veo_tours_manifest.json"
_VEO_MANIFEST_GCS = os.environ.get(
    "VEO_MANIFEST_GCS_URL",
    f"https://storage.googleapis.com/{GCS_MEDIA_BUCKET}/tours/veo/veo_tours_manifest.json",
)

_TOURS_CACHE: dict = {"t": 0.0, "data": None}
_TOURS_LOCK = asyncio.Lock()


def _tour_entries(raw) -> dict:
    if isinstance(raw, dict) and isinstance(raw.get("tours"), dict):
        raw = raw["tours"]
    if not isinstance(raw, dict):
        return {}
    return {k: v for k, v in raw.items() if isinstance(v, dict) and v.get("url")}


def _read_tour_file(path: Path) -> dict:
    try:
        if path.exists():
            return _tour_entries(json.loads(path.read_text()))
    except Exception:
        pass
    return {}


def _fetch_gcs_veo_manifest() -> dict:
    try:
        req = urllib.request.Request(f"{_VEO_MANIFEST_GCS}?ts={int(time.time())}", headers={"Cache-Control": "no-cache"})
        with urllib.request.urlopen(req, timeout=3) as r:
            return _tour_entries(json.loads(r.read().decode("utf-8")))
    except Exception:
        return {}


async def _get_tours_manifest(force: bool = False) -> dict:
    now = time.time()
    cached = _TOURS_CACHE.get("data")
    if not force and cached is not None and now - _TOURS_CACHE["t"] < 30:
        return cached
    async with _TOURS_LOCK:
        cached = _TOURS_CACHE.get("data")
        if not force and cached is not None and time.time() - _TOURS_CACHE["t"] < 30:
            return cached
        cinematic = _read_tour_file(_TOURS_MANIFEST_PATH)
        veo = _read_tour_file(_VEO_MANIFEST_PATH)
        veo.update(await asyncio.to_thread(_fetch_gcs_veo_manifest))
        data = {"cinematic": cinematic, "veo": veo, "generated_at": int(time.time())}
        _TOURS_CACHE.update(t=time.time(), data=data)
        return data


INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Pillar 5 · AI Real Estate Marketplace Studio</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/frontend/p5_media.css">
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
      padding: 24px;
    }
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 16px;
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
    .search-bar {
      display: flex;
      gap: 12px;
      margin-bottom: 20px;
    }
    input[type=text] {
      flex: 1;
      padding: 12px 16px;
      border-radius: 12px;
      background: var(--card-bg);
      border: 1px solid var(--border);
      color: #FFF;
      font-size: 14px;
    }
    button.btn-search {
      padding: 12px 24px;
      background: var(--accent);
      border: none;
      border-radius: 12px;
      color: #FFF;
      font-weight: 700;
      cursor: pointer;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 20px;
    }
    .listing-card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 16px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      transition: transform 0.15s ease;
    }
    .listing-card:hover { transform: translateY(-3px); }
    .card-img-wrap {
      position: relative;
      height: 200px;
      background: #000;
      cursor: pointer;
    }
    .card-img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    .score-pill {
      position: absolute;
      top: 12px; right: 12px;
      background: rgba(15, 23, 42, 0.85);
      backdrop-filter: blur(8px);
      padding: 4px 10px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 800;
      color: #38BDF8;
      border: 1px solid rgba(255,255,255,0.15);
    }
    .card-body { padding: 16px; flex: 1; display: flex; flex-direction: column; }
    .card-title { font-size: 15px; font-weight: 700; margin: 0 0 6px; }
    .card-sub { font-size: 12px; color: var(--text-muted); margin-bottom: 12px; }
    .card-price { font-size: 18px; font-weight: 800; font-family: 'JetBrains Mono'; margin-top: auto; }
    .btn-evaluate {
      margin-top: 10px;
      padding: 8px 12px;
      background: #1E293B;
      border: 1px solid #334155;
      border-radius: 8px;
      color: #FFF;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
    }
    .btn-evaluate:hover { background: #334155; }
  </style>
</head>
<body>
  <div class="header">
    <div>
      <h1 style="margin:0; font-size:22px; font-weight:800;">Pillar 5 · AI Real Estate Marketplace Studio</h1>
      <p style="margin:4px 0 0; font-size:13px; color:var(--text-muted);">
        108 Architecturally Distinct Homes · 3-Way Hybrid Search (Semantic 45% + Visual 35% + Keyword 20%) · Honest Gemini Multimodal Judge
      </p>
    </div>
    <div class="badge">
      <span class="dot-pulse"></span>
      <span id="p5-badge-text">Port 8085 · Standalone</span>
    </div>
  </div>

  <div class="search-bar">
    <input type="text" id="p5-query" placeholder="Search: e.g. waterfront coastal villa, modern craftsman with chef kitchen, brick & timber loft..." value="luxury craftsman in Royal Oak MI">
    <button class="btn-search" id="btn-search">Search Homes</button>
  </div>

  <div class="grid" id="listing-grid"></div>

  <script src="/frontend/p5_media.js"></script>
  <script>
    async function doSearch() {
      const q = document.getElementById('p5-query').value;
      const badge = document.getElementById('p5-badge-text');
      badge.innerText = 'Searching 108 listings...';

      try {
        const res = await fetch('/api/pillar5/search', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query_text: q, limit: 12 })
        });
        const data = await res.json();
        badge.innerText = `Pillar 5 · ${data.latency_ms}ms (${data.total_matched} homes)`;
        renderListings(data.results || []);
      } catch (err) {
        badge.innerText = 'Error: ' + err.message;
      }
    }

    function renderListings(items) {
      const grid = document.getElementById('listing-grid');
      grid.innerHTML = items.map(item => `
        <div class="listing-card">
          <div class="card-img-wrap" onclick="viewTour('${item.id}')">
            <img class="card-img" src="${item.hero_image_url}" alt="${item.title}" loading="lazy">
            <div class="score-pill">Score ${item.hybrid_score || (item.similarity * 100).toFixed(1)}%</div>
          </div>
          <div class="card-body">
            <h4 class="card-title">${item.title}</h4>
            <div class="card-sub">${item.city || item.location} · ${item.beds} Beds · ${item.baths} Baths · ${item.sqft} sqft</div>
            <div class="card-price">$${(item.price).toLocaleString()}</div>
            <button class="btn-evaluate" onclick="evaluateListing('${item.id}')">Gemini Photo Judge Audit</button>
          </div>
        </div>
      `).join('');
    }

    async function evaluateListing(listingId) {
      alert('Running Gemini 3.8 Multimodal Photo Judge on ' + listingId + ' (8 labeled photos)...');
      try {
        const res = await fetch('/api/pillar5/evaluate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ listing_id: listingId, fresh: false })
        });
        const data = await res.json();
        const audit = data.audit || {};
        alert(`Gemini Judge on ${listingId}: Verdict: ${audit.verdict || 'AUDITED'} | Integrity Score: ${audit.score || audit.integrity_score || '--'}/100\\nSummary: ${audit.summary || data.summary || 'Audit complete.'}`);
      } catch (e) {
        alert('Judge failed: ' + e.message);
      }
    }

    function viewTour(listingId) {
      window.location.href = `/api/pillar5/listing-video/${listingId}?source=cinematic`;
    }

    document.getElementById('btn-search').addEventListener('click', doSearch);
    window.addEventListener('DOMContentLoaded', doSearch);
  </script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """Renders standalone AI Real Estate Marketplace Studio HTML, or returns JSON health if requested."""
    accept = request.headers.get("accept", "")
    if "application/json" in accept or request.query_params.get("format") == "json":
        return JSONResponse({
            "ok": True,
            "service": "pillar-5-realestate-marketplace",
            "port": 8085,
            "engine": "108 Homes Hybrid Vector Search + Gemini Photo Judge",
        })
    return HTMLResponse(INDEX_HTML)


@app.post("/api/pillar5/search")
async def api_p5_search(request: Request):
    """Multimodal hybrid vector search across 108 listings."""
    try:
        body = await request.json()
    except Exception:
        body = {}
    res = hybrid_search_marketplace(
        query_text=body.get("query_text", ""),
        beds_filter=int(body.get("beds_filter", 0)),
        family_filter=body.get("family_filter", "all"),
        max_price=int(body.get("max_price", 3500000)),
        reference_listing_id=body.get("reference_listing_id", ""),
        reference_image_b64=body.get("reference_image_b64", ""),
        semantic_weight=float(body.get("semantic_weight", 0.45)),
        visual_weight=float(body.get("visual_weight", 0.35)),
        keyword_weight=float(body.get("keyword_weight", 0.20)),
        limit=int(body.get("limit", 108)),
    )
    return JSONResponse(res)


@app.post("/api/pillar5/evaluate")
async def api_p5_evaluate(request: Request):
    """Honest multimodal Gemini Judge evaluating 8 labeled photos per home."""
    try:
        body = await request.json()
    except Exception:
        body = {}
    listing_id = body.get("listing_id", "RKT-001")
    fresh = bool(body.get("fresh", False))
    try:
        res = evaluate_listing_live_with_gemini(listing_id=listing_id, fresh=fresh)
    except TypeError:
        res = evaluate_listing_live_with_gemini(listing_id=listing_id)
    return JSONResponse(res)


@app.get("/api/pillar5/tours-manifest")
async def api_p5_tours_manifest(request: Request):
    """Returns the merged cinematic + Veo tour manifest."""
    data = await _get_tours_manifest(force=request.query_params.get("refresh") == "1")
    return JSONResponse(data, headers={"Cache-Control": "no-store"})


@app.get("/api/pillar5/listing-video/{listing_id}")
async def api_p5_listing_video(listing_id: str, request: Request):
    """Serves THAT listing's 16:9 H.264 video tour."""
    raw_aspect = (request.query_params.get("aspect", "16x9") or "16x9").replace(":", "x").lower()
    aspect = "9x16" if raw_aspect == "9x16" else "16x9"
    safe_id = "".join(c for c in listing_id if c.isalnum() or c in ("-", "_")) or "RKT-001"

    if aspect == "16x9" and request.query_params.get("live") != "1":
        tours = await _get_tours_manifest()
        source = request.query_params.get("source", "cinematic")
        order = ("veo", "cinematic") if source == "veo" else ("cinematic", "veo")
        for kind in order:
            entry = tours.get(kind, {}).get(safe_id)
            if entry and entry.get("url"):
                return RedirectResponse(entry["url"], status_code=302, headers={"Cache-Control": "no-store"})

    out_dir = Path("/tmp/rocket_listing_videos")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_mp4 = out_dir / f"{safe_id}_{aspect}.mp4"
    if out_mp4.exists() and out_mp4.stat().st_size > 10000:
        return FileResponse(str(out_mp4), media_type="video/mp4")

    # Fallback default video if available in static/reels
    reels_sample = STATIC_DIR / "reels" / "modern_craftsman_reel_9x16.mp4" if STATIC_DIR.exists() else None
    if reels_sample and reels_sample.exists():
        return FileResponse(str(reels_sample), media_type="video/mp4")

    return JSONResponse({"ok": False, "error": f"Tour not found for {safe_id}"}, status_code=404)


@app.get("/healthz")
async def healthz():
    return JSONResponse({"status": "ok", "service": "pillar-5-realestate-marketplace", "port": 8085})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8085, reload=True)
