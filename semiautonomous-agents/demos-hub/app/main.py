"""demos.sonrobots.net — curated demo hub.

Single FastAPI app behind IAP. Loads the card list from app/demos.yaml at
startup and renders one page. No DB, no auth code (IAP handles it).
"""
from __future__ import annotations

from pathlib import Path

import yaml
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent

with (ROOT / "demos.yaml").open() as f:
    DEMOS = yaml.safe_load(f)

ALL_TAGS = sorted({t for d in DEMOS for t in d.get("tags", [])})
TAG_COUNTS = {t: sum(1 for d in DEMOS if t in d.get("tags", [])) for t in ALL_TAGS}

app = FastAPI(title="demos.sonrobots.net")
app.mount("/static", StaticFiles(directory=str(REPO / "static")), name="static")
templates = Jinja2Templates(directory=str(ROOT / "templates"))


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "demos": DEMOS,
         "all_tags": ALL_TAGS, "tag_counts": TAG_COUNTS},
    )


@app.get("/healthz")
def healthz():
    return JSONResponse({"ok": True, "demos": len(DEMOS)})
