"""Vector Search Canvas — FastAPI backend.

The whole point of this app is to make Vector Search 2.0's knobs
visible. Every toggle in the UI maps 1:1 to a kwarg on
`MatchingEngineIndexEndpoint.find_neighbors()`. The UI sends those
kwargs to /api/search; the server forwards them and returns:

    - approx hits (whatever algorithm/index was selected)
    - exact hits (BRUTE_FORCE on the same query for ground-truth)
    - recall@k overlap between the two
    - per-call latency

Run locally:
    python -m app.main
or:
    uvicorn app.main:app --reload --port 8770
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Literal

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor

from google import genai
from google.cloud import aiplatform
from google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint import (
    Namespace,
    NumericNamespace,
)

ROOT = Path(__file__).parent
CFG  = json.loads((ROOT.parent / "deploy" / "indexes.json").read_text())

PROJECT  = CFG["project"]
LOCATION = CFG["location"]
TREE_AH_INDEX = CFG["tree_ah_index"]
BRUTE_INDEX   = CFG["brute_index"]
ENDPOINT_NAME = CFG["endpoint"]
DEPLOYED_TREE = CFG["deployed_tree"]
DEPLOYED_BRUTE = CFG["deployed_brute"]

EMBED_MODEL = "gemini-embedding-2-preview"

aiplatform.init(project=PROJECT, location=LOCATION)
_GENAI = genai.Client(vertexai=True, project=PROJECT, location=LOCATION)
_ENDPOINT = None


def endpoint() -> aiplatform.MatchingEngineIndexEndpoint:
    global _ENDPOINT
    if _ENDPOINT is None:
        _ENDPOINT = aiplatform.MatchingEngineIndexEndpoint(ENDPOINT_NAME)
    return _ENDPOINT


# ---------------------------------------------------------------------------
# Embedding (cache the last query so toggle changes don't re-embed)
# ---------------------------------------------------------------------------
_EMBED_CACHE: dict[str, list[float]] = {}


def embed(text: str) -> list[float]:
    text = (text or "").strip()
    if not text:
        raise HTTPException(400, "empty query")
    if text in _EMBED_CACHE:
        return _EMBED_CACHE[text]
    from google.genai import types
    resp = _GENAI.models.embed_content(
        model=EMBED_MODEL,
        contents=[text],
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    )
    vec = list(resp.embeddings[0].values)
    _EMBED_CACHE[text] = vec
    if len(_EMBED_CACHE) > 256:
        _EMBED_CACHE.pop(next(iter(_EMBED_CACHE)))
    return vec


# ---------------------------------------------------------------------------
# Search request schema — these field names are deliberately the SAME as the
# kwarg names on find_neighbors, so the UI's "code panel" can stringify the
# exact call shape without translation.
# ---------------------------------------------------------------------------
class SearchReq(BaseModel):
    query: str
    num_neighbors: int = 20
    algorithm: Literal["tree_ah", "brute_force", "both"] = "both"
    modality_allow: list[str] = []
    modality_deny: list[str] = []
    tempo_allow: list[str] = []
    length_allow: list[str] = []
    per_crowding_attribute_num_neighbors: int = 0
    return_full_datapoint: bool = False
    leaf_nodes_to_search_percent_override: int = 0  # 0 = use index default


def build_filter(req: SearchReq) -> list[Namespace]:
    f = []
    if req.modality_allow or req.modality_deny:
        f.append(Namespace(
            name="modality",
            allow_tokens=req.modality_allow or [],
            deny_tokens=req.modality_deny or [],
        ))
    if req.tempo_allow:
        f.append(Namespace(name="tempo_bucket", allow_tokens=req.tempo_allow))
    if req.length_allow:
        f.append(Namespace(name="length_bucket", allow_tokens=req.length_allow))
    return f


def _call_one(deployed_id: str, vec: list[float], req: SearchReq) -> dict:
    """Time a single find_neighbors call and return its raw shape."""
    kwargs = {
        "deployed_index_id": deployed_id,
        "queries": [vec],
        "num_neighbors": req.num_neighbors,
        "return_full_datapoint": req.return_full_datapoint,
    }
    f = build_filter(req)
    if f:
        kwargs["filter"] = f
    if req.per_crowding_attribute_num_neighbors > 0:
        kwargs["per_crowding_attribute_num_neighbors"] = (
            req.per_crowding_attribute_num_neighbors)
    # leaf_nodes_to_search_percent_override only valid for tree_ah; ignore on brute
    if (req.leaf_nodes_to_search_percent_override > 0
            and deployed_id == DEPLOYED_TREE):
        kwargs["leaf_nodes_to_search_percent_override"] = (
            req.leaf_nodes_to_search_percent_override)

    t0 = time.perf_counter()
    resp = endpoint().find_neighbors(**kwargs)
    dt_ms = (time.perf_counter() - t0) * 1000.0

    hits = []
    if resp and resp[0]:
        for n in resp[0]:
            hits.append({
                "id": n.id,
                "similarity": 1.0 - float(n.distance),
                "distance": float(n.distance),
            })
    return {"hits": hits, "latency_ms": round(dt_ms, 1)}


def recall(approx: list[dict], exact: list[dict]) -> dict:
    """recall@k = |approx ∩ exact| / |exact|. Order doesn't count."""
    if not exact:
        return {"recall": None, "overlap": 0, "k": 0}
    ax = {h["id"] for h in approx}
    ex = {h["id"] for h in exact}
    overlap = len(ax & ex)
    return {
        "recall": overlap / len(ex),
        "overlap": overlap,
        "k": len(ex),
        "missed_ids": sorted(ex - ax),
    }


# ---------------------------------------------------------------------------
# FastAPI
# ---------------------------------------------------------------------------
app = FastAPI(title="Vector Search Canvas")
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")
templates = Jinja2Templates(directory=str(ROOT / "templates"))


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "config": {
                "project": PROJECT,
                "location": LOCATION,
                "endpoint": ENDPOINT_NAME.split("/")[-1],
                "deployed_tree": DEPLOYED_TREE,
                "deployed_brute": DEPLOYED_BRUTE,
            },
        },
    )


@app.get("/api/config")
def api_config():
    return {
        "project": PROJECT,
        "location": LOCATION,
        "endpoint": ENDPOINT_NAME,
        "tree_ah": {"index": TREE_AH_INDEX, "deployed_id": DEPLOYED_TREE},
        "brute":   {"index": BRUTE_INDEX,   "deployed_id": DEPLOYED_BRUTE},
        "embed_model": EMBED_MODEL,
    }


@app.get("/api/health")
def api_health():
    """Quick liveness — also tells the UI whether both deploys are up."""
    try:
        ep = endpoint()
        deployed = {d.id: getattr(d, "index_sync_time", None)
                    for d in (ep.deployed_indexes or [])}
        return {
            "ok": True,
            "deployed_ids": list(deployed.keys()),
            "tree_ah_ready": DEPLOYED_TREE in deployed,
            "brute_ready":   DEPLOYED_BRUTE in deployed,
        }
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=503)


@app.post("/api/search")
def api_search(req: SearchReq):
    t0 = time.perf_counter()
    vec = embed(req.query)
    embed_ms = (time.perf_counter() - t0) * 1000.0

    out: dict = {
        "query": req.query,
        "embed_ms": round(embed_ms, 1),
        "dim": len(vec),
        "algorithm": req.algorithm,
        "kwargs_preview": _kwargs_preview(req),
    }

    with ThreadPoolExecutor(max_workers=2) as ex:
        futs = {}
        if req.algorithm in ("tree_ah", "both"):
            futs["tree_ah"] = ex.submit(_call_one, DEPLOYED_TREE, vec, req)
        if req.algorithm in ("brute_force", "both"):
            futs["brute_force"] = ex.submit(_call_one, DEPLOYED_BRUTE, vec, req)
        results = {k: f.result() for k, f in futs.items()}

    out.update(results)

    # Recall only meaningful when we have both
    if "tree_ah" in results and "brute_force" in results:
        out["recall"] = recall(results["tree_ah"]["hits"],
                               results["brute_force"]["hits"])

    return out


def _kwargs_preview(req: SearchReq) -> dict:
    """The same kwargs the server is going to send, but in a JSON-safe shape
    so the UI can pretty-print it as a code block."""
    f = []
    if req.modality_allow or req.modality_deny:
        f.append({
            "Namespace": "modality",
            "allow_tokens": req.modality_allow,
            "deny_tokens": req.modality_deny,
        })
    if req.tempo_allow:
        f.append({"Namespace": "tempo_bucket", "allow_tokens": req.tempo_allow})
    if req.length_allow:
        f.append({"Namespace": "length_bucket", "allow_tokens": req.length_allow})
    base = {
        "queries": "[<3072-d query vector>]",
        "num_neighbors": req.num_neighbors,
        "return_full_datapoint": req.return_full_datapoint,
    }
    if f:
        base["filter"] = f
    if req.per_crowding_attribute_num_neighbors > 0:
        base["per_crowding_attribute_num_neighbors"] = (
            req.per_crowding_attribute_num_neighbors)
    if req.leaf_nodes_to_search_percent_override > 0:
        base["leaf_nodes_to_search_percent_override"] = (
            req.leaf_nodes_to_search_percent_override)
    return base


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8770, reload=True)
