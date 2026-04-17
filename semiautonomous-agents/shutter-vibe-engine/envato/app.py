"""Envato Vibe — FastAPI + multimodal search demo.

Endpoints
---------
GET  /                       Envato-style search UI (HTML)
GET  /api/search?q=...       Vector search with auto-rescue
POST /api/visual             Upload an image, return visually similar assets
GET  /api/probe?q=...&qtwo=  Two-query similarity probe (for narrating)
GET  /api/stats              Index size + capabilities
GET  /assets/...             Static asset files (thumbnails, originals)

Search backend
--------------
Queries Vertex AI Vector Search (deployed `MatchingEngineIndexEndpoint`) when
the endpoint is reachable. Falls back to a local NumPy brute-force pass over
`asset_index.npz` only if the SDK call fails (useful for local dev before the
endpoint finishes deploying).

Zero-result rescue policy (the headline feature):
* Run vector search.
* If best score < CONFIDENCE_FLOOR, mark as "low confidence".
* Return rescue strategies built ENTIRELY from vector search — no LLM hop:
    1. Catalog detour: surface the closest match per modality (photo / video /
       graphic / audio) so the user discovers a parallel format.
    2. Visual paraphrase: take the top-1 visual hit and return its visual
       neighbours — "more like this style", computed in-index.
* The UI also surfaces a "Generate it" CTA pointing at Imagen/Veo/Lyria.
"""
from __future__ import annotations

import io
import json
import os
import sys
import time
from pathlib import Path
from typing import Literal

import numpy as np
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "demos"))
from _client import CLIENT, MM_MODEL, TEXT_MODEL  # noqa: E402
from google.genai import types  # noqa: E402

CONFIDENCE_FLOOR = 0.42   # below this we treat the result set as "low signal"
HARD_FLOOR = 0.20         # below this we don't even show the weak hits

# Per-modality score calibration. Gemini Embedding 2 in text-only mode (which
# is how we encode audio metadata) produces vectors that cluster very close to
# text queries — much closer than image+text fused vectors do. Without this
# offset, every text query would top with an audio result even when the user
# clearly wants visuals. Mirrors Envato's prod approach of using DIFFERENT
# embedding models per content type (see EBC briefing Marqo item-models table).
MODALITY_BIAS = {"audio": -0.18}

# ---------------------------------------------------------------------------
# Vector Search — managed Vertex AI endpoint configuration
# ---------------------------------------------------------------------------
PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
INDEX_DISPLAY_NAME = "envato-vibe-multimodal"
ENDPOINT_DISPLAY_NAME = "envato-vibe-endpoint"
DEPLOYED_INDEX_ID = INDEX_DISPLAY_NAME.replace("-", "_")

ENDPOINT = None              # cached resolved endpoint (success path)
_ENDPOINT_RECHECK_AT = 0.0   # epoch seconds; controls re-probing the deploy
_ENDPOINT_RECHECK_INTERVAL = 60.0


def _resolve_endpoint():
    """Find the deployed MatchingEngineIndexEndpoint by display name. Caches
    the success path forever and the failure path for 60 s so we don't pay
    a network round-trip on every search while the endpoint is provisioning."""
    global ENDPOINT, _ENDPOINT_RECHECK_AT
    if ENDPOINT is not None:
        return ENDPOINT
    if time.time() < _ENDPOINT_RECHECK_AT:
        return None
    _ENDPOINT_RECHECK_AT = time.time() + _ENDPOINT_RECHECK_INTERVAL
    try:
        from google.cloud import aiplatform
        aiplatform.init(project=PROJECT, location=LOCATION)
        eps = aiplatform.MatchingEngineIndexEndpoint.list(
            filter=f'display_name="{ENDPOINT_DISPLAY_NAME}"'
        )
        if not eps:
            print("[boot] WARN: endpoint not found yet — using local NumPy fallback")
            return None
        ep = eps[0]
        if not any(d.id == DEPLOYED_INDEX_ID for d in ep.deployed_indexes):
            print("[boot] WARN: endpoint exists but index not yet deployed — fallback")
            return None
        ENDPOINT = ep
        print(f"[boot] Vector Search endpoint: {ep.resource_name}")
        return ep
    except Exception as exc:
        print(f"[boot] WARN: Vector Search unavailable ({exc}) — fallback")
        return None


# ---------------------------------------------------------------------------
# Boot — load metadata + local NPZ (used as hydration source + fallback)
# ---------------------------------------------------------------------------
NPZ = ROOT / "index" / "asset_index.npz"
if not NPZ.exists():
    raise SystemExit("Run envato/pipeline.py first to build the index.")

_data = np.load(NPZ, allow_pickle=True)
ASSET_IDS: list[str] = list(_data["ids"].tolist())
FUSED_VECS: np.ndarray = _data["fused"].astype("float32")  # already L2 normed
ID_TO_IDX = {aid: i for i, aid in enumerate(ASSET_IDS)}

MANIFEST = {a["asset_id"]: a for a in
            json.loads((ROOT / "assets" / "manifest.json").read_text())}

print(f"[boot] loaded {len(ASSET_IDS)} assets  fused={FUSED_VECS.shape}")
_resolve_endpoint()

app = FastAPI(title="Envato Vibe")
app.mount("/assets", StaticFiles(directory=str(ROOT / "assets")), name="assets")
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")
templates = Jinja2Templates(directory=str(ROOT / "templates"))


# ---------------------------------------------------------------------------
# Embedding helpers
# ---------------------------------------------------------------------------
def l2(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.where(n == 0, 1, n)


def embed_query_mm(query: str) -> np.ndarray:
    """Multimodal-space text query. Same space as the fused asset vectors."""
    resp = CLIENT.models.embed_content(model=MM_MODEL, contents=[query])
    return l2(np.asarray(resp.embeddings[0].values, dtype=np.float32))


def embed_image_mm(image_bytes: bytes, mime: str = "image/png") -> np.ndarray:
    resp = CLIENT.models.embed_content(
        model=MM_MODEL,
        contents=[types.Part.from_bytes(data=image_bytes, mime_type=mime)],
    )
    return l2(np.asarray(resp.embeddings[0].values, dtype=np.float32))


# ---------------------------------------------------------------------------
# Search core — Vertex AI Vector Search with local NumPy fallback
# ---------------------------------------------------------------------------
def _vector_search_remote(q_vec: np.ndarray, k: int,
                          modality: str | None) -> list[tuple[str, float]] | None:
    """Query the deployed MatchingEngineIndexEndpoint. Returns None on failure
    so the caller can fall back to the local NumPy path."""
    ep = _resolve_endpoint()
    if ep is None:
        return None
    try:
        from google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint import (
            Namespace,
        )
        # Over-fetch when modality bias is in play so we have headroom to
        # re-rank without losing top results (the bias is a post-hoc tilt).
        over_k = k * 4 if modality is None else k
        kwargs = {
            "deployed_index_id": DEPLOYED_INDEX_ID,
            "queries": [q_vec.tolist()],
            "num_neighbors": over_k,
        }
        if modality:
            kwargs["filter"] = [Namespace(name="modality", allow_tokens=[modality])]
        response = ep.find_neighbors(**kwargs)
        # find_neighbors returns COSINE_DISTANCE → cosine similarity = 1 - d.
        hits = [(n.id, 1.0 - float(n.distance)) for n in response[0]]
        # Apply modality bias when running unfiltered, then trim to k.
        if modality is None and MODALITY_BIAS:
            hits = [(aid, score + MODALITY_BIAS.get(MANIFEST[aid]["category"], 0.0))
                    for aid, score in hits]
            hits.sort(key=lambda x: -x[1])
        return hits[:k]
    except Exception as exc:
        print(f"[vs] remote query failed ({exc}) — local fallback")
        return None


def _vector_search_local(q_vec: np.ndarray, k: int,
                         modality: str | None) -> list[tuple[str, float]]:
    """Brute-force NumPy over the in-memory NPZ. Identical scoring formula
    to the remote path, used as fallback before the endpoint is deployed."""
    sims = (FUSED_VECS @ q_vec.reshape(-1)).astype(float)
    for i, aid in enumerate(ASSET_IDS):
        bias = MODALITY_BIAS.get(MANIFEST[aid]["category"], 0.0)
        if bias:
            sims[i] += bias
    order = np.argsort(-sims)
    results: list[tuple[str, float]] = []
    for i in order:
        aid = ASSET_IDS[i]
        if modality and MANIFEST[aid]["category"] != modality:
            continue
        results.append((aid, float(sims[i])))
        if len(results) >= k:
            break
    return results


def vector_search(q_vec: np.ndarray, k: int = 12,
                  modality: str | None = None) -> list[tuple[str, float]]:
    remote = _vector_search_remote(q_vec, k, modality)
    if remote is not None:
        return remote
    return _vector_search_local(q_vec, k, modality)


def hydrate(hits: list[tuple[str, float]]) -> list[dict]:
    out = []
    for aid, score in hits:
        item = dict(MANIFEST[aid])
        item["score"] = round(score, 4)
        # Audio has no rendered thumbnail — the UI swaps in a waveform glyph.
        if item.get("category") == "audio":
            item["thumb_url"] = ""
        else:
            item["thumb_url"] = f"/assets/thumbnails/{aid}.webp"
        out.append(item)
    return out


def _pick_unseen(candidates: list[tuple[str, float]], seen: set[str],
                 limit: int = 1) -> list[tuple[str, float]]:
    """Return up to `limit` (asset_id, score) pairs not in `seen`,
    mutating `seen` in place. Keeps every panel cross-deduplicated."""
    picked: list[tuple[str, float]] = []
    for aid, score in candidates:
        if aid in seen:
            continue
        if score < HARD_FLOOR:
            break
        picked.append((aid, score))
        seen.add(aid)
        if len(picked) >= limit:
            break
    return picked


def build_rescue(query: str, primary: list[tuple[str, float]],
                 q_vec: np.ndarray) -> dict:
    """Two rescue strategies — both pure vector search, no LLM.

    1. Catalog detour — closest match per modality (cross-modal fan-out for
       project-level discovery). Reuses the already-embedded query vector.
    2. Visual paraphrase — neighbours of the top weak hit ("more like this
       style"), computed against the local index for sub-ms latency.

    The "Generate it" CTA is rendered by the UI alongside these — it doesn't
    require a backend call at this stage.
    """
    rescue: dict = {"strategies": []}
    seen: set[str] = {aid for aid, _ in primary[:4]}

    # 1. Catalog detour — best unseen hit per modality.
    #    The EBC briefing flags "project-level satisfaction" (one user needing
    #    a video + matching music + complementary graphic for ONE project) as
    #    the most underappreciated success metric. This panel is exactly that.
    detour_items = []
    available_mods = sorted({m["category"] for m in MANIFEST.values()})
    for mod in available_mods:
        mod_top = vector_search(q_vec, k=8, modality=mod)
        chosen = _pick_unseen(mod_top, seen, limit=1)
        if chosen:
            detour_items.append({
                "modality": mod,
                "asset": hydrate(chosen)[0],
            })
    rescue["strategies"].append({
        "kind": "catalog_detour",
        "headline": "Closest match in each format",
        "items": detour_items,
    })

    # 2. Visual paraphrase — neighbours of the top weak hit. Computed against
    #    the local fused matrix because it's a known asset id, not a query.
    if primary:
        anchor_id, _ = primary[0]
        anchor_idx = ID_TO_IDX.get(anchor_id)
        if anchor_idx is not None:
            sims = (FUSED_VECS @ FUSED_VECS[anchor_idx]).astype(float)
            sims[anchor_idx] = -1
            order = np.argsort(-sims)
            candidates = [(ASSET_IDS[i], float(sims[i])) for i in order[:20]]
            chosen = _pick_unseen(candidates, seen, limit=4)
            if chosen:
                rescue["strategies"].append({
                    "kind": "visual_paraphrase",
                    "headline": f"More in the style of {anchor_id}",
                    "items": [{"asset": hydrate([(aid, score)])[0]}
                              for aid, score in chosen],
                })

    return rescue


# ---------------------------------------------------------------------------
# HTTP API
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request, "index.html", {"asset_count": len(ASSET_IDS)},
    )


@app.get("/api/stats")
def stats():
    ep = _resolve_endpoint()
    return {
        "asset_count": len(ASSET_IDS),
        "fused_dim": int(FUSED_VECS.shape[1]),
        "models": {"multimodal": MM_MODEL, "text": TEXT_MODEL},
        "confidence_floor": CONFIDENCE_FLOOR,
        "categories": sorted({m["category"] for m in MANIFEST.values()}),
        "sub_categories": sorted({m["sub_category"] for m in MANIFEST.values()}),
        "backend": ("vertex_vector_search" if ep else "local_numpy_fallback"),
        "endpoint": (ep.resource_name if ep else None),
        "deployed_index_id": (DEPLOYED_INDEX_ID if ep else None),
    }


@app.get("/api/search")
def api_search(q: str,
               modality: Literal["photo", "video", "graphic", "audio", "all"] = "all",
               k: int = 12):
    t0 = time.perf_counter()
    q_vec = embed_query_mm(q)
    embed_ms = (time.perf_counter() - t0) * 1000

    t1 = time.perf_counter()
    mod = None if modality == "all" else modality
    hits = vector_search(q_vec, k=k, modality=mod)
    search_ms = (time.perf_counter() - t1) * 1000

    best = hits[0][1] if hits else 0.0
    low_confidence = best < CONFIDENCE_FLOOR

    payload = {
        "query": q,
        "modality": modality,
        "best_score": round(best, 4),
        "low_confidence": low_confidence,
        "results": hydrate(hits) if best >= HARD_FLOOR else [],
        "timings_ms": {
            "embed": round(embed_ms, 1),
            "search": round(search_ms, 2),
            "total": round(embed_ms + search_ms, 1),
        },
    }
    if low_confidence:
        t2 = time.perf_counter()
        payload["rescue"] = build_rescue(q, hits, q_vec)
        payload["timings_ms"]["rescue"] = round((time.perf_counter() - t2) * 1000, 1)
    return JSONResponse(payload)


@app.post("/api/visual")
async def api_visual(file: UploadFile = File(...), k: int = 8):
    raw = await file.read()
    # normalise to a small PNG for the API
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    im.thumbnail((512, 512))
    buf = io.BytesIO()
    im.save(buf, format="PNG")

    t0 = time.perf_counter()
    qv = embed_image_mm(buf.getvalue(), mime="image/png")
    embed_ms = (time.perf_counter() - t0) * 1000

    hits = vector_search(qv, k=k)
    return {
        "filename": file.filename,
        "best_score": round(hits[0][1] if hits else 0.0, 4),
        "results": hydrate(hits),
        "timings_ms": {"embed": round(embed_ms, 1)},
    }


@app.get("/api/probe")
def api_probe(q: str, qtwo: str):
    """Side-by-side similarity probe — useful when narrating the demo."""
    a = embed_query_mm(q)
    b = embed_query_mm(qtwo)
    return {"q1": q, "q2": qtwo, "cosine": round(float(a @ b.reshape(-1)), 4)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=False)
