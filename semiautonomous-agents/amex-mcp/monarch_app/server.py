"""FastAPI + PWA Backend Server for Monarch Money (Royal Amethyst Edition) Web & Mobile App."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, Response
from pydantic import BaseModel

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from amex_job.simplefin import sync_simplefin_to_firestore
from monarch_app.data_engine import (
    DATA_CACHE_PATH,
    build_monarch_dataset,
    save_user_override,
)

app = FastAPI(title="Monarch Money — Royal Amethyst Edition", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

HTML_APP_PATH = Path(__file__).parent / "index.html"

ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <defs>
    <linearGradient id="amethyst" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#8B5CF6" />
      <stop offset="50%" stop-color="#7C3AED" />
      <stop offset="100%" stop-color="#4C1D95" />
    </linearGradient>
  </defs>
  <rect width="512" height="512" rx="118" fill="url(#amethyst)" />
  <path d="M256 226C212 140 105 112 86 178C71 232 115 292 172 315C156 344 168 388 206 388C234 388 248 360 256 332C264 360 278 388 306 388C344 388 356 344 340 315C397 292 441 232 426 178C407 112 300 140 256 226Z" fill="none" stroke="#FFFFFF" stroke-width="34" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

SERVICE_WORKER_JS = """
const CACHE_NAME = 'monarch-amethyst-v3';
self.addEventListener('install', (event) => {
  self.skipWaiting();
});
self.addEventListener('activate', (event) => {
  event.waitUntil(clients.claim());
});
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});
"""


class TransactionPatch(BaseModel):
    category: str | None = None
    merchant_clean: str | None = None
    tags: list[str] | None = None
    reviewed: bool | None = None
    needs_review: bool | None = None
    notes: str | None = None
    flex_bucket: str | None = None


class SyncRequest(BaseModel):
    days: int = 90


@app.get("/", response_class=HTMLResponse)
def serve_index() -> HTMLResponse:
    if not HTML_APP_PATH.exists():
        return HTMLResponse("<h1>Monarch App UI not found</h1>", status_code=404)
    return HTMLResponse(HTML_APP_PATH.read_text(encoding="utf-8"))


@app.get("/manifest.webmanifest")
def serve_manifest() -> JSONResponse:
    return JSONResponse({
        "name": "Monarch Money — Royal Amethyst",
        "short_name": "Monarch",
        "description": "Track, Budget, Plan and Manage Money across Amex, BofA & SoFi",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#0B0914",
        "theme_color": "#7C3AED",
        "orientation": "portrait-primary",
        "icons": [
            {
                "src": "/icon.svg",
                "sizes": "192x192 512x512",
                "type": "image/svg+xml",
                "purpose": "any maskable"
            }
        ]
    })


@app.get("/icon.svg")
def serve_icon() -> Response:
    return Response(content=ICON_SVG, media_type="image/svg+xml")


@app.get("/sw.js")
def serve_sw() -> Response:
    return Response(content=SERVICE_WORKER_JS, media_type="application/javascript")


@app.get("/api/state")
def get_state(refresh: bool = False) -> JSONResponse:
    if refresh or not DATA_CACHE_PATH.exists():
        ds = build_monarch_dataset()
    else:
        ds = json.loads(DATA_CACHE_PATH.read_text(encoding="utf-8"))
    return JSONResponse(ds)


@app.post("/api/sync")
def trigger_simplefin_sync(req: SyncRequest) -> JSONResponse:
    try:
        sync_res = sync_simplefin_to_firestore(days=req.days)
        ds = build_monarch_dataset()
        return JSONResponse({
            "status": "ok",
            "sync_result": sync_res,
            "dataset": ds,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/transaction/{txn_id}")
def update_transaction(txn_id: str, patch: TransactionPatch) -> JSONResponse:
    clean_patch = {k: v for k, v in patch.model_dump().items() if v is not None}
    updated = save_user_override(txn_id, clean_patch)
    if DATA_CACHE_PATH.exists():
        ds = json.loads(DATA_CACHE_PATH.read_text(encoding="utf-8"))
        for t in ds.get("transactions", []):
            if str(t.get("txn_id")) == str(txn_id):
                t.update(clean_patch)
                break
        DATA_CACHE_PATH.write_text(json.dumps(ds, indent=2), encoding="utf-8")
    return JSONResponse({"status": "ok", "txn_id": txn_id, "override": updated})


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8095"))
    uvicorn.run(app, host="0.0.0.0", port=port)
