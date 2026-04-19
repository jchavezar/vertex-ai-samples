"""Vibe Search v2 — FastAPI surface for segment-level multimodal search.

The pipeline is already deployed (pipeline_v2 + Eventarc + Cloud Run). This app
is purely the read/upload API surface that the UI agent consumes.

Endpoints (contract):
  GET  /api/health
  GET  /api/search?q=&modality=&limit=
  POST /api/search/sounds-like   (multipart "file": mp3/wav)
  POST /api/image-to-anything    (multipart "file": image)
  GET  /api/segment/{datapoint_id}
  POST /api/upload               (multipart "file": any)
  GET  /api/stats
  GET  /api/uploads/recent?limit=10

Wow features layered into the above:
  1. per-segment retrieval     → data model from pipeline_v2
  2. cross-modality fan-out    → grouped[] in /api/search response
  3. sounds-like               → /api/search/sounds-like
  4. image-to-anything         → /api/image-to-anything
  5. zero-result rescue        → catalog_detour + visual_paraphrase via Gemini
  6. precision/latency stats   → /api/stats + per-search timings
  7. auto-ingest               → /api/upload drops to gs://.../ingest/
  8. tempo-aware music         → ?tempo= namespace restrict
  9. length-aware video        → ?length= namespace restrict
 10. palette filter            → ?color=#hex post-filter
 11. recent queries            → /api/stats.recent_queries
 12. brand-safe signed URLs    → all asset URLs signed v4 1h
"""
from __future__ import annotations

import asyncio
import base64
import collections
import io
import json
import os
import re
import subprocess
import sys
import time
import uuid
from datetime import timedelta
from pathlib import Path
from typing import Literal

import numpy as np
from fastapi import (
    FastAPI,
    File,
    HTTPException,
    Request,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent
# `_client.py` lives at <repo>/semiautonomous-agents/shutter-vibe-engine/demos/.
# Locally that's `ROOT.parent.parent.parent / "demos"`; in the Docker image it
# is COPYed to `/app/demos` (see deploy/Dockerfile.app).
for _cand in (ROOT.parent.parent.parent / "demos", Path("/app/demos")):
    if _cand.exists():
        sys.path.insert(0, str(_cand))
        break

from _client import CLIENT  # noqa: E402  shared genai.Client (us-central1)
from google import genai  # noqa: E402
from google.genai import types  # noqa: E402

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
GCS_BUCKET = os.environ.get("ENVATO_GCS_BUCKET", "envato-vibe-demo")

INDEX_DISPLAY_NAME = "envato-vibe-multimodal"
ENDPOINT_DISPLAY_NAME = "envato-vibe-endpoint"
DEPLOYED_INDEX_ID = "envato_vibe_multimodal"

FIRESTORE_SEGMENTS = "segments"
FIRESTORE_UPLOADS = "uploads"

EMBED_MODEL = "gemini-embedding-2-preview"
RESCUE_MODEL = "gemini-3.1-flash-lite-preview"  # global region

# "Talk to this Asset" — Gemini Live API + text fallback chat models.
# Vertex AI uses the dash-suffixed preview model id; these can change with
# the SDK / region — keep in sync with google-genai release notes.
LIVE_MODEL = os.environ.get(
    # As of 2026-04, this is the native-audio Live preview model available
    # in us-central1 for Vertex AI. It speaks PCM16 mono 24kHz back to us,
    # and accepts mic audio at 16kHz mono. Older `gemini-2.0-flash-live-*`
    # ids return 1008 model-not-found in our project.
    "ENVATO_LIVE_MODEL", "gemini-live-2.5-flash-preview-native-audio-09-2025",
)
CHAT_MODEL = os.environ.get("ENVATO_CHAT_MODEL", "gemini-2.5-flash")
ASSET_CHAT_SYSTEM = (
    "You are an art-director assistant for a creative team browsing the "
    "stock catalogue. The user is asking questions about THIS specific "
    "asset (image, video frame or audio clip) which is attached to the "
    "conversation as context. Be concise, opinionated, and helpful for "
    "creative decisions: mood, lighting, composition, what to pair it with, "
    "where it would work, what to avoid. Speak like a senior creative "
    "director — confident, specific, never generic."
)

# Confidence scoring — same shape as v1 but expressed against cosine similarity.
LOW_CONFIDENCE_FLOOR = 0.45     # below this we trigger rescue
ZERO_RESULT_FANOUT_K = 24

# In-memory telemetry buffers
LATENCIES_MS = collections.deque(maxlen=200)
RECENT_QUERIES = collections.deque(maxlen=20)
FIRESTORE_RECENT_QUERIES = "recent_queries"
RECENT_DEDUP_WINDOW_S = 30  # collapse same q within this window

# Lite captioner / rewriter only lives in the `global` region — own client.
GLOBAL_CLIENT = genai.Client(vertexai=True, project=PROJECT, location="global")

# ---------------------------------------------------------------------------
# Lazy-resolved cloud singletons
# ---------------------------------------------------------------------------
_ENDPOINT = None
_FS = None
_GCS_BUCKET_OBJ = None


def fs():
    global _FS
    if _FS is None:
        from google.cloud import firestore
        _FS = firestore.Client(project=PROJECT)
    return _FS


def _is_refinement(prev: str, curr: str) -> bool:
    """Treat prev and curr as the same search session if either:
      - one is a prefix of the other (typing progressively: 'dron ar' → 'dron aerial')
      - they share ≥70% of characters and differ by ≤3 edits (typo fixes:
        'dron aerila' ↔ 'dron aerial')"""
    if not prev or not curr:
        return False
    a, b = prev.lower(), curr.lower()
    if a == b or a.startswith(b) or b.startswith(a):
        return True
    # Cheap edit-distance bound (Levenshtein) only when lengths are similar
    if abs(len(a) - len(b)) > 3:
        return False
    if min(len(a), len(b)) < 4:
        return False
    # Bounded DP — early-exit at threshold 3
    n, m = len(a), len(b)
    prev_row = list(range(m + 1))
    for i in range(1, n + 1):
        curr_row = [i] + [0] * m
        row_min = curr_row[0]
        for j in range(1, m + 1):
            cost = 0 if a[i-1] == b[j-1] else 1
            curr_row[j] = min(curr_row[j-1] + 1, prev_row[j] + 1, prev_row[j-1] + cost)
            if curr_row[j] < row_min:
                row_min = curr_row[j]
        if row_min > 3:
            return False
        prev_row = curr_row
    return prev_row[m] <= 3


def record_recent_query(q_text: str, n_results: int,
                        rescue: str | None, total_ms: float) -> None:
    """Append a query to the in-process deque AND persist to Firestore.
    Collapses progressive refinements and typo corrections within
    RECENT_DEDUP_WINDOW_S into a single entry, so a user's search session
    ('dron ar' → 'dron aerial' → 'drone aerial') shows as one final entry
    instead of three. Firestore persistence survives server restarts."""
    now = time.time()
    q_clean = (q_text or "").strip()
    if not q_clean:
        return

    if RECENT_QUERIES:
        last = RECENT_QUERIES[0]
        if (now - last.get("ts", 0)) <= RECENT_DEDUP_WINDOW_S \
                and _is_refinement(last.get("q", ""), q_clean):
            # Always keep the latest text — it's the most refined version.
            last["q"] = q_clean
            last["ts"] = now
            last["result_count"] = n_results
            last["total_ms"] = round(float(total_ms), 2)
            last["rescue"] = rescue
            try:
                fs().collection(FIRESTORE_RECENT_QUERIES).document(last["_id"]).set({
                    "q": q_clean, "ts": now, "result_count": n_results,
                    "rescue": rescue, "total_ms": round(float(total_ms), 2),
                })
            except Exception as exc:
                print(f"[recent_queries] dedup update failed: {exc}")
            return

    entry_id = f"{int(now*1000):013d}"
    entry = {
        "_id": entry_id, "q": q_clean, "ts": now,
        "result_count": n_results, "rescue": rescue,
        "total_ms": round(float(total_ms), 2),
    }
    RECENT_QUERIES.appendleft(entry)
    try:
        fs().collection(FIRESTORE_RECENT_QUERIES).document(entry_id).set({
            k: v for k, v in entry.items() if k != "_id"
        })
    except Exception as exc:
        print(f"[recent_queries] persist failed: {exc}")


def warm_recent_queries() -> None:
    """Load the most recent persisted queries into the in-memory deque so
    the list survives restarts. Called once at app startup."""
    from google.cloud import firestore as _fs_mod
    try:
        q = (fs().collection(FIRESTORE_RECENT_QUERIES)
             .order_by("ts", direction=_fs_mod.Query.DESCENDING)
             .limit(RECENT_QUERIES.maxlen))
        loaded: list[dict] = []
        for snap in q.stream():
            d = snap.to_dict() or {}
            d["_id"] = snap.id
            loaded.append(d)
        # Append in reverse so the newest ends up at index 0.
        for d in reversed(loaded):
            RECENT_QUERIES.appendleft(d)
        print(f"[recent_queries] warmed {len(loaded)} entries from Firestore")
    except Exception as exc:
        print(f"[recent_queries] warm failed: {exc}")


def gcs_bucket():
    global _GCS_BUCKET_OBJ
    if _GCS_BUCKET_OBJ is None:
        from google.cloud import storage
        _GCS_BUCKET_OBJ = storage.Client(project=PROJECT).bucket(GCS_BUCKET)
    return _GCS_BUCKET_OBJ


def endpoint():
    global _ENDPOINT
    if _ENDPOINT is not None:
        return _ENDPOINT
    from google.cloud import aiplatform
    aiplatform.init(project=PROJECT, location=LOCATION)
    # Resolve the resource name via list(), then construct directly so the
    # public-match client gets wired up (the list() shortcut leaves it None).
    eps = aiplatform.MatchingEngineIndexEndpoint.list(
        filter=f'display_name="{ENDPOINT_DISPLAY_NAME}"'
    )
    if not eps:
        raise RuntimeError(f"endpoint '{ENDPOINT_DISPLAY_NAME}' not found")
    _ENDPOINT = aiplatform.MatchingEngineIndexEndpoint(
        index_endpoint_name=eps[0].resource_name
    )
    return _ENDPOINT


_INDEX = None


def index():
    """Returns the MatchingEngineIndex (for upsert/remove). Distinct from
    endpoint(), which is the query-serving handle."""
    global _INDEX
    if _INDEX is not None:
        return _INDEX
    from google.cloud import aiplatform
    aiplatform.init(project=PROJECT, location=LOCATION)
    idx = aiplatform.MatchingEngineIndex.list(
        filter=f'display_name="{INDEX_DISPLAY_NAME}"')
    if not idx:
        raise RuntimeError(f"index '{INDEX_DISPLAY_NAME}' not found")
    _INDEX = idx[0]
    return _INDEX


# ---------------------------------------------------------------------------
# FastAPI app + middleware
# ---------------------------------------------------------------------------
app = FastAPI(title="Vibe Search v2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")
templates = Jinja2Templates(directory=str(ROOT / "templates"))


@app.on_event("startup")
def _warm_caches() -> None:
    warm_recent_queries()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def l2(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.where(n == 0, 1, n)


def now_ms() -> float:
    return time.perf_counter() * 1000.0


def ms_since(t0: float) -> float:
    return round(now_ms() - t0, 2)


def gs_to_blob_path(gs_uri: str | None) -> str | None:
    """gs://envato-vibe-demo/foo/bar.webp -> foo/bar.webp"""
    if not gs_uri or not gs_uri.startswith(f"gs://{GCS_BUCKET}/"):
        return None
    return gs_uri[len(f"gs://{GCS_BUCKET}/"):]


def signed_url(gs_uri: str | None, hours: int = 1) -> str | None:
    """Bucket is configured for public read (allUsers:objectViewer) since
    the corpus is public-domain Pexels/Pixabay/Internet-Archive material.
    Return the direct https URL — no signing needed, works locally and on
    Cloud Run identically."""
    blob_path = gs_to_blob_path(gs_uri)
    if not blob_path:
        return None
    return f"https://storage.googleapis.com/{GCS_BUCKET}/{blob_path}"


def slugify(name: str) -> str:
    base, ext = os.path.splitext(name)
    base = re.sub(r"[^a-zA-Z0-9]+", "-", base).strip("-").lower()
    if not base:
        base = uuid.uuid4().hex[:10]
    return base + ext.lower()


# ---------------------------------------------------------------------------
# Embedding helpers — gemini-embedding-2-preview, NO task_type, NO output_dim
# ---------------------------------------------------------------------------
def embed_text(text: str) -> np.ndarray:
    resp = CLIENT.models.embed_content(model=EMBED_MODEL, contents=[text])
    v = np.asarray(resp.embeddings[0].values, dtype=np.float32)
    return l2(v.reshape(1, -1))[0]


def embed_image(image_bytes: bytes, mime: str = "image/png") -> np.ndarray:
    resp = CLIENT.models.embed_content(
        model=EMBED_MODEL,
        contents=[types.Part.from_bytes(data=image_bytes, mime_type=mime)],
    )
    v = np.asarray(resp.embeddings[0].values, dtype=np.float32)
    return l2(v.reshape(1, -1))[0]


def embed_audio(audio_bytes: bytes, mime: str = "audio/mpeg") -> np.ndarray:
    resp = CLIENT.models.embed_content(
        model=EMBED_MODEL,
        contents=[types.Part.from_bytes(data=audio_bytes, mime_type=mime)],
    )
    v = np.asarray(resp.embeddings[0].values, dtype=np.float32)
    return l2(v.reshape(1, -1))[0]


# ---------------------------------------------------------------------------
# Vector Search
# ---------------------------------------------------------------------------
def _restrict(name: str, allow: list[str]):
    from google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint import (
        Namespace,
    )
    return Namespace(name=name, allow_tokens=allow)


def vs_find_neighbors(q_vec: np.ndarray, *, k: int = 20,
                      modality: str | None = None,
                      tempo: str | None = None,
                      length: str | None = None) -> list[tuple[str, float]]:
    """Returns [(datapoint_id, cosine_similarity), ...] ordered best-first."""
    ep = endpoint()
    restricts = []
    if modality and modality != "all":
        # Map UI modality → restrict tokens. SFX is its own modality bucket
        # in the index; users asking for "audio" want both music and sfx.
        if modality == "audio":
            restricts.append(_restrict("modality", ["audio", "sfx"]))
        else:
            restricts.append(_restrict("modality", [modality]))
    if tempo:
        restricts.append(_restrict("tempo_bucket", [tempo]))
    if length:
        restricts.append(_restrict("length_bucket", [length]))

    kwargs = {
        "deployed_index_id": DEPLOYED_INDEX_ID,
        "queries": [q_vec.tolist()],
        "num_neighbors": k,
    }
    if restricts:
        kwargs["filter"] = restricts
    response = ep.find_neighbors(**kwargs)
    if not response or not response[0]:
        return []
    # find_neighbors returns COSINE_DISTANCE → similarity = 1 - distance.
    return [(n.id, 1.0 - float(n.distance)) for n in response[0]]


# ---------------------------------------------------------------------------
# Firestore hydration
# ---------------------------------------------------------------------------
def hydrate_segments(hits: list[tuple[str, float]],
                     rescue_strategy: str | None = None) -> list[dict]:
    """Fetch Firestore docs for the hit list and shape into SegmentResult."""
    if not hits:
        return []
    coll = fs().collection(FIRESTORE_SEGMENTS)
    refs = [coll.document(dp_id) for dp_id, _ in hits]
    snaps = fs().get_all(refs)
    by_id: dict[str, dict] = {}
    for snap in snaps:
        if snap.exists:
            by_id[snap.id] = snap.to_dict() or {}

    out: list[dict] = []
    for dp_id, score in hits:
        doc = by_id.get(dp_id)
        if not doc:
            continue
        modality = doc.get("modality") or doc.get("restricts", {}).get("modality") or ""
        kind = doc.get("kind") or doc.get("restricts", {}).get("kind") or ""
        out.append({
            "datapoint_id": dp_id,
            "asset_id": doc.get("asset_id", ""),
            "modality": modality,
            "kind": kind,
            "score": round(float(score), 4),
            "start_s": float(doc.get("start_s", 0.0) or 0.0),
            "end_s": float(doc.get("end_s", 0.0) or 0.0),
            "caption": doc.get("caption") or {},
            "caption_text": doc.get("caption_text", ""),
            "sub_category": doc.get("sub_category", ""),
            "contributor": doc.get("contributor", ""),
            "license": doc.get("license", ""),
            "thumbnail_url": signed_url(doc.get("thumbnail_gcs")),
            "clip_url": signed_url(doc.get("clip_gcs")),
            "original_url": signed_url(doc.get("original_gcs")),
            "rescue_strategy": rescue_strategy,
        })
    return out


def group_by_modality(results: list[dict]) -> dict[str, list[dict]]:
    """grouped: { photo, video, audio_music, audio_sfx, graphic }"""
    grouped = {"photo": [], "video": [], "audio_music": [],
               "audio_sfx": [], "graphic": []}
    for r in results:
        modality = r.get("modality")
        kind = r.get("kind")
        if modality == "audio" or modality == "sfx" or kind == "sfx":
            if kind == "sfx" or modality == "sfx":
                grouped["audio_sfx"].append(r)
            else:
                grouped["audio_music"].append(r)
        elif modality in grouped:
            grouped[modality].append(r)
    return grouped


# ---------------------------------------------------------------------------
# Palette filter (feature 10)
# ---------------------------------------------------------------------------
def _hex_to_rgb(h: str) -> tuple[int, int, int] | None:
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        return None
    try:
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    except ValueError:
        return None


def _color_distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    return float(sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5)


def palette_filter(results: list[dict], hex_color: str,
                   max_dist: float = 140.0) -> list[dict]:
    target = _hex_to_rgb(hex_color)
    if not target:
        return results
    filtered = []
    for r in results:
        colors = (r.get("caption") or {}).get("dominant_colors") or []
        best = None
        for c in colors:
            rgb = _hex_to_rgb(c) if isinstance(c, str) else None
            if rgb is None:
                continue
            d = _color_distance(target, rgb)
            if best is None or d < best:
                best = d
        if best is not None and best <= max_dist:
            r2 = dict(r)
            r2["palette_distance"] = round(best, 1)
            filtered.append(r2)
    return filtered


# ---------------------------------------------------------------------------
# Zero-result rescue (feature 5) — Gemini structured rewriting + paraphrase
# ---------------------------------------------------------------------------
DETOUR_SCHEMA = {
    "type": "OBJECT",
    "properties": {"rewrite": {"type": "STRING"}},
    "required": ["rewrite"],
}

PARAPHRASE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "paraphrases": {
            "type": "ARRAY",
            "items": {"type": "STRING"},
            "minItems": 3, "maxItems": 3,
        },
    },
    "required": ["paraphrases"],
}


def gemini_catalog_detour(query: str) -> str:
    """Rewrite a query into a nearby in-vocab phrase the catalog likely covers."""
    prompt = (
        "You are a search query rewriter for a stock media catalog (photos, "
        "videos, music, sound effects, graphics). The user's query returned "
        "no results. Rewrite it as ONE short phrase (≤ 8 words) that is likely "
        "to exist in a generic stock catalog. Keep the user's intent; broaden "
        "specifics (brand names, niche jargon) into generic visual/audio terms.\n\n"
        f"User query: {query}\n"
    )
    cfg = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=DETOUR_SCHEMA,
        temperature=0.4,
    )
    resp = GLOBAL_CLIENT.models.generate_content(
        model=RESCUE_MODEL, contents=[prompt], config=cfg,
    )
    data = json.loads(resp.text)
    return data["rewrite"].strip()


def gemini_visual_paraphrases(query: str) -> list[str]:
    """3 visual paraphrases of the query — different ways a photographer / "
    director would describe the same scene."""
    prompt = (
        "Give exactly 3 distinct visual paraphrases of the following stock-media "
        "search query. Each paraphrase is one short sentence describing the same "
        "scene from a different angle (composition, lighting, mood, subject). "
        "Avoid repeating the same nouns.\n\n"
        f"Query: {query}\n"
    )
    cfg = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=PARAPHRASE_SCHEMA,
        temperature=0.7,
    )
    resp = GLOBAL_CLIENT.models.generate_content(
        model=RESCUE_MODEL, contents=[prompt], config=cfg,
    )
    data = json.loads(resp.text)
    return [p.strip() for p in data["paraphrases"]][:3]


def union_rerank(per_query_hits: list[list[tuple[str, float]]],
                 limit: int) -> list[tuple[str, float]]:
    """Reciprocal-rank-fusion-ish union; collapse duplicates keeping max score."""
    best: dict[str, float] = {}
    for hits in per_query_hits:
        for dp_id, score in hits:
            if dp_id not in best or score > best[dp_id]:
                best[dp_id] = score
    ranked = sorted(best.items(), key=lambda x: -x[1])
    return ranked[:limit]


def maybe_rescue(q_vec_query: str, primary: list[tuple[str, float]],
                 *, limit: int, modality: str | None,
                 tempo: str | None, length: str | None
                 ) -> tuple[list[tuple[str, float]], str | None]:
    """If primary is empty or all scores < floor, run rescue strategies.
    Returns (new_hits, rescue_label)."""
    needs_rescue = (not primary) or (max(s for _, s in primary) < LOW_CONFIDENCE_FLOOR)
    if not needs_rescue:
        return primary, None

    # Strategy A: catalog detour (single Gemini rewrite + re-search).
    try:
        rewrite = gemini_catalog_detour(q_vec_query)
        rv = embed_text(rewrite)
        hits_a = vs_find_neighbors(rv, k=limit, modality=modality,
                                   tempo=tempo, length=length)
        if hits_a and max(s for _, s in hits_a) >= LOW_CONFIDENCE_FLOOR:
            return hits_a, "catalog_detour"
    except Exception as exc:
        print(f"[rescue.catalog_detour] {exc}")
        hits_a = []

    # Strategy B: visual paraphrase (3 rewrites embedded + union-rerank).
    try:
        paraphrases = gemini_visual_paraphrases(q_vec_query)
        per_q: list[list[tuple[str, float]]] = []
        for p in paraphrases:
            pv = embed_text(p)
            per_q.append(vs_find_neighbors(pv, k=limit, modality=modality,
                                           tempo=tempo, length=length))
        union = union_rerank(per_q, limit)
        if union:
            return union, "visual_paraphrase"
    except Exception as exc:
        print(f"[rescue.visual_paraphrase] {exc}")

    # Fall back to whatever rewrite path produced — even if weak.
    if hits_a:
        return hits_a, "catalog_detour"
    return primary, None


# ---------------------------------------------------------------------------
# Search core
# ---------------------------------------------------------------------------
FANOUT_MODALITIES = ("photo", "video", "audio", "graphic")


def vs_fanout_all(q_vec: np.ndarray, *, k: int,
                  tempo: str | None, length: str | None
                  ) -> list[tuple[str, float]]:
    """Per-modality fan-out for cross-modal 'all' searches. Issues one
    restricted vs_find_neighbors call per modality in parallel, then merges
    by raw cosine similarity. Without this, a single dominant modality
    (music = ~60% of the corpus) crowds out photo/video/graphic results."""
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=len(FANOUT_MODALITIES)) as ex:
        futures = {m: ex.submit(vs_find_neighbors, q_vec, k=k,
                                modality=m, tempo=tempo, length=length)
                   for m in FANOUT_MODALITIES}
        per_mod = {m: f.result() for m, f in futures.items()}
    merged: dict[str, float] = {}
    for hits in per_mod.values():
        for dp_id, score in hits:
            if dp_id not in merged or score > merged[dp_id]:
                merged[dp_id] = score
    return sorted(merged.items(), key=lambda x: -x[1])


def _do_search(q_text: str, q_vec: np.ndarray, modality: str, limit: int,
               tempo: str | None, length: str | None,
               color: str | None, *, t0_total: float,
               t_embed_ms: float, vibe: dict | None = None) -> dict:
    mod = None if modality == "all" else modality

    # ---- Vibe slider bias: nudge the query embedding along learned axes ----
    # Each axis stores delta = l2norm(embed(positive) - embed(negative)). We
    # add (strength * value) * delta for each axis with |value| > epsilon, then
    # re-normalise. Tuned so a full slider shifts the result mix without
    # scrambling intent. Cached deltas are computed lazily on first call.
    vibe_applied: dict[str, float] = {}
    if vibe:
        try:
            deltas = compute_vibe_deltas()
            strength = 0.35
            biased = q_vec.astype(np.float32, copy=True)
            for axis, value in vibe.items():
                try:
                    v = float(value)
                except (TypeError, ValueError):
                    continue
                if abs(v) <= 0.01 or axis not in deltas:
                    continue
                biased = biased + (strength * v) * deltas[axis]
                vibe_applied[axis] = round(v, 3)
            if vibe_applied:
                n = float(np.linalg.norm(biased))
                if n > 0:
                    q_vec = (biased / n).astype(np.float32)
        except Exception as exc:
            print(f"[vibe] bias failed: {exc}")

    t1 = now_ms()
    if modality == "all":
        hits = vs_fanout_all(q_vec, k=limit, tempo=tempo, length=length)
    else:
        hits = vs_find_neighbors(q_vec, k=limit, modality=mod,
                                 tempo=tempo, length=length)
    vs_ms = ms_since(t1)

    hits, rescue_label = maybe_rescue(q_text, hits, limit=limit,
                                      modality=mod, tempo=tempo, length=length)

    t3 = now_ms()
    results = hydrate_segments(hits, rescue_strategy=rescue_label)
    hydrate_ms = ms_since(t3)

    if color:
        results = palette_filter(results, color)

    total_ms = ms_since(t0_total)

    LATENCIES_MS.append(total_ms)
    record_recent_query(q_text, len(results), rescue_label, total_ms)

    return {
        "query": q_text,
        "query_embed_ms": round(t_embed_ms, 2),
        "vs_search_ms": round(vs_ms, 2),
        "hydrate_ms": round(hydrate_ms, 2),
        "total_ms": round(total_ms, 2),
        "result_count": len(results),
        "rescue": rescue_label,
        "vibe_applied": vibe_applied,
        "results": results,
        "grouped": group_by_modality(results),
    }


# ---------------------------------------------------------------------------
# HTTP API
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index_v2.html", {})


@app.get("/api/health")
def api_health():
    try:
        n = sum(1 for _ in fs().collection(FIRESTORE_SEGMENTS).select([]).stream())
    except Exception as exc:
        return {"ok": False, "error": str(exc), "stats": {"segments_indexed": 0}}
    return {"ok": True, "stats": {"segments_indexed": n}}


@app.get("/api/search")
def api_search(q: str,
               modality: Literal["all", "photo", "video", "audio", "graphic"] = "all",
               limit: int = 20,
               tempo: Literal["slow", "mid", "upbeat", "fast"] | None = None,
               length: Literal["short", "mid", "long", "epic"] | None = None,
               color: str | None = None,
               vibe_warm: float = 0.0,
               vibe_energy: float = 0.0,
               vibe_cinematic: float = 0.0,
               vibe_busy: float = 0.0):
    if not q or not q.strip():
        raise HTTPException(400, "missing query")
    t0 = now_ms()
    t_embed = now_ms()
    q_vec = embed_text(q)
    embed_ms = ms_since(t_embed)
    vibe = {
        "warm": max(-1.0, min(1.0, float(vibe_warm))),
        "energy": max(-1.0, min(1.0, float(vibe_energy))),
        "cinematic": max(-1.0, min(1.0, float(vibe_cinematic))),
        "busy": max(-1.0, min(1.0, float(vibe_busy))),
    }
    return JSONResponse(_do_search(q, q_vec, modality, limit, tempo, length,
                                   color, t0_total=t0, t_embed_ms=embed_ms,
                                   vibe=vibe))


@app.post("/api/search/sounds-like")
async def api_sounds_like(file: UploadFile = File(...), limit: int = 20):
    raw = await file.read()
    mime = file.content_type or "audio/mpeg"
    if "wav" in (file.filename or "").lower() and "wav" not in mime:
        mime = "audio/wav"
    t0 = now_ms()
    t_embed = now_ms()
    q_vec = embed_audio(raw, mime=mime)
    embed_ms = ms_since(t_embed)
    return JSONResponse(_do_search("(uploaded audio)", q_vec, "audio", limit,
                                   None, None, None,
                                   t0_total=t0, t_embed_ms=embed_ms))


@app.post("/api/image-to-anything")
async def api_image_to_anything(file: UploadFile = File(...), limit: int = 20):
    raw = await file.read()
    mime = file.content_type or "image/png"
    t0 = now_ms()
    t_embed = now_ms()
    q_vec = embed_image(raw, mime=mime)
    embed_ms = ms_since(t_embed)
    return JSONResponse(_do_search("(uploaded image)", q_vec, "all", limit,
                                   None, None, None,
                                   t0_total=t0, t_embed_ms=embed_ms))


@app.get("/api/segment/{datapoint_id}")
def api_segment(datapoint_id: str):
    snap = fs().collection(FIRESTORE_SEGMENTS).document(datapoint_id).get()
    if not snap.exists:
        raise HTTPException(404, f"segment {datapoint_id} not found")
    doc = snap.to_dict() or {}
    doc["thumbnail_url"] = signed_url(doc.get("thumbnail_gcs"))
    doc["clip_url"] = signed_url(doc.get("clip_gcs"))
    doc["original_url"] = signed_url(doc.get("original_gcs"))
    return JSONResponse(doc)


@app.post("/api/upload")
async def api_upload(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "no filename")
    safe = slugify(file.filename)
    blob_path = f"ingest/{safe}"
    blob = gcs_bucket().blob(blob_path)
    blob.upload_from_file(file.file, content_type=file.content_type)
    # Best-effort: register an "uploads" doc the UI can poll for ETA / status.
    try:
        fs().collection(FIRESTORE_UPLOADS).document(safe).set({
            "filename": file.filename,
            "object_name": blob_path,
            "content_type": file.content_type or "",
            "uploaded_at": time.time(),
            "status": "queued",
        })
    except Exception as exc:
        print(f"[upload] could not write uploads doc: {exc}")
    return {"object_name": blob_path, "eta_seconds": 8}


@app.get("/api/stats")
def api_stats():
    by_modality: dict[str, int] = {}
    total = 0
    last_24h = 0
    cutoff = time.time() - 24 * 3600
    try:
        for snap in fs().collection(FIRESTORE_SEGMENTS).stream():
            d = snap.to_dict() or {}
            modality = d.get("modality", "unknown")
            kind = d.get("kind", "")
            key = "audio_sfx" if kind == "sfx" else (
                "audio_music" if modality == "audio" else modality
            )
            by_modality[key] = by_modality.get(key, 0) + 1
            total += 1
    except Exception as exc:
        print(f"[stats] segments scan failed: {exc}")

    try:
        for snap in fs().collection(FIRESTORE_UPLOADS).stream():
            d = snap.to_dict() or {}
            if (d.get("uploaded_at") or 0) >= cutoff:
                last_24h += 1
    except Exception as exc:
        print(f"[stats] uploads scan failed: {exc}")

    if LATENCIES_MS:
        arr = np.asarray(LATENCIES_MS, dtype=np.float32)
        p50 = float(np.percentile(arr, 50))
        p95 = float(np.percentile(arr, 95))
    else:
        p50 = p95 = 0.0

    return {
        "segments_indexed": total,
        "by_modality": by_modality,
        "last_24h_uploads": last_24h,
        "query_latency_ms_p50": round(p50, 2),
        "query_latency_ms_p95": round(p95, 2),
        "recent_queries": list(RECENT_QUERIES)[:10],
    }


@app.get("/api/uploads/recent")
def api_uploads_recent(limit: int = 10):
    """Lists upload audit docs. Two writers populate this collection:
    /api/upload writes a slug-keyed doc with `uploaded_at` (status=queued),
    and the ingest_handler writes an asset_id-keyed doc with `ts` after
    processing. We can't order_by either field server-side without
    excluding docs missing it, so fetch all and sort in Python."""
    try:
        items = []
        for snap in fs().collection(FIRESTORE_UPLOADS).stream():
            d = snap.to_dict() or {}
            d["id"] = snap.id
            d["_sort_ts"] = float(d.get("uploaded_at") or d.get("ts") or 0)
            items.append(d)
        items.sort(key=lambda x: -x["_sort_ts"])
        items = items[: max(1, min(50, limit))]
        for it in items:
            it.pop("_sort_ts", None)
        return {"items": items}
    except Exception as exc:
        return {"items": [], "error": str(exc)}


@app.delete("/api/asset/{asset_id}")
def api_delete_asset(asset_id: str):
    """Wipe a user-uploaded asset from VS, Firestore, and GCS.
    Restricted to asset_ids prefixed `upload-` so the seeded catalog is safe."""
    if not asset_id.startswith("upload-"):
        raise HTTPException(403, "only user-uploaded assets (upload-*) may be deleted")

    # 1. Collect segment docs and the GCS URIs they point at.
    seg_coll = fs().collection(FIRESTORE_SEGMENTS)
    seg_docs = list(seg_coll.where("asset_id", "==", asset_id).stream())
    dp_ids = [s.id for s in seg_docs]
    gcs_paths: set[str] = set()
    for s in seg_docs:
        d = s.to_dict() or {}
        for key in ("thumbnail_gcs", "clip_gcs", "original_gcs"):
            obj = gs_to_blob_path(d.get(key))
            if obj:
                gcs_paths.add(obj)

    # 2. Vector Search streaming delete.
    vs_removed = 0
    if dp_ids:
        try:
            index().remove_datapoints(datapoint_ids=dp_ids)
            vs_removed = len(dp_ids)
        except Exception as exc:
            print(f"[delete] VS remove failed for {asset_id}: {exc}")

    # 3. GCS — delete tracked objects + sweep the per-asset prefixes for any
    #    untracked artifacts (defensive; covers thumbnails/segments produced
    #    by reruns that never landed in Firestore).
    gcs_removed = 0
    bucket = gcs_bucket()
    for prefix in (f"segments/{asset_id}/", f"thumbnails/{asset_id}/"):
        for blob in bucket.list_blobs(prefix=prefix):
            gcs_paths.add(blob.name)
    for path in gcs_paths:
        try:
            bucket.blob(path).delete()
            gcs_removed += 1
        except Exception as exc:
            print(f"[delete] GCS delete failed {path}: {exc}")

    # 4. Firestore — segment docs (batched 500 per the API limit).
    fs_removed = 0
    batch = fs().batch()
    n_in_batch = 0
    for s in seg_docs:
        batch.delete(s.reference)
        n_in_batch += 1
        if n_in_batch >= 450:
            batch.commit()
            fs_removed += n_in_batch
            batch = fs().batch()
            n_in_batch = 0
    if n_in_batch:
        batch.commit()
        fs_removed += n_in_batch

    # 5. Drop the uploads/ audit doc.
    upload_doc_removed = False
    try:
        fs().collection(FIRESTORE_UPLOADS).document(asset_id).delete()
        upload_doc_removed = True
    except Exception as exc:
        print(f"[delete] uploads doc delete failed {asset_id}: {exc}")

    return {
        "asset_id": asset_id,
        "deleted": {
            "vs_datapoints": vs_removed,
            "firestore_segments": fs_removed,
            "gcs_objects": gcs_removed,
            "uploads_doc": upload_doc_removed,
        },
    }


# ---------------------------------------------------------------------------
# Talk to this Asset — multimodal chat (Gemini Live API + text fallback)
# ---------------------------------------------------------------------------
def _segment_doc(asset_id: str) -> dict:
    """Resolve a result-card identifier to a segment doc.

    The UI passes `datapoint_id` (the doc id in the segments collection) but
    older paths sometimes pass the parent `asset_id`. Try both."""
    coll = fs().collection(FIRESTORE_SEGMENTS)
    snap = coll.document(asset_id).get()
    if snap.exists:
        d = snap.to_dict() or {}
        d["_doc_id"] = snap.id
        return d
    # Fallback: scan-by-asset-id, take the first segment.
    for s in coll.where("asset_id", "==", asset_id).limit(1).stream():
        d = s.to_dict() or {}
        d["_doc_id"] = s.id
        return d
    raise HTTPException(404, f"asset/segment {asset_id} not found")


def _gcs_read(gs_uri: str | None) -> bytes | None:
    """Download bytes for a gs:// URI (lives in our public bucket)."""
    blob_path = gs_to_blob_path(gs_uri)
    if not blob_path:
        return None
    try:
        return gcs_bucket().blob(blob_path).download_as_bytes()
    except Exception as exc:
        print(f"[asset_chat] gcs download failed {gs_uri}: {exc}")
        return None


def _video_first_frame_jpeg(video_bytes: bytes) -> bytes | None:
    """Extract a representative frame from a video as JPEG using ffmpeg.
    Returns None if ffmpeg isn't available — the caller will fall back to
    sending the original asset bytes (still works for photo / graphic)."""
    if not video_bytes:
        return None
    try:
        proc = subprocess.run(
            [
                "ffmpeg", "-loglevel", "error",
                "-ss", "0.5",
                "-f", "mp4", "-i", "pipe:0",
                "-frames:v", "1",
                "-vf", "scale=1024:-2",
                "-f", "image2pipe", "-vcodec", "mjpeg",
                "pipe:1",
            ],
            input=video_bytes,
            capture_output=True,
            timeout=20,
        )
        if proc.returncode == 0 and proc.stdout:
            return proc.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        print(f"[asset_chat] ffmpeg frame extraction failed: {exc}")
    return None


def _build_asset_part(doc: dict) -> tuple[types.Part | None, str, str]:
    """Returns (genai Part, mime_type, kind_hint).

    Strategy by modality:
      photo / graphic → image bytes from original_gcs (or thumbnail fallback)
      video           → first frame jpeg from clip_gcs  (image inline)
      audio           → mp3 bytes from clip_gcs         (audio inline)
    """
    modality = (doc.get("modality") or "").lower()
    kind = (doc.get("kind") or "").lower()
    caption_text = doc.get("caption_text") or (doc.get("caption") or {}).get("title") or ""

    if modality in ("photo", "graphic"):
        raw = _gcs_read(doc.get("original_gcs")) or _gcs_read(doc.get("thumbnail_gcs"))
        if not raw:
            return None, "", caption_text
        mime = "image/jpeg"
        return types.Part.from_bytes(data=raw, mime_type=mime), mime, "image"

    if modality == "video":
        raw = _gcs_read(doc.get("clip_gcs")) or _gcs_read(doc.get("original_gcs"))
        if not raw:
            return None, "", caption_text
        # Try a single representative frame so we stay light enough for the
        # Live API system turn; fall back to the raw video bytes if ffmpeg
        # isn't on PATH (Live API also accepts video/mp4 inline).
        frame = _video_first_frame_jpeg(raw)
        if frame:
            return types.Part.from_bytes(data=frame, mime_type="image/jpeg"), "image/jpeg", "image"
        return types.Part.from_bytes(data=raw, mime_type="video/mp4"), "video/mp4", "video"

    if modality in ("audio", "sfx") or kind == "sfx":
        raw = _gcs_read(doc.get("clip_gcs")) or _gcs_read(doc.get("original_gcs"))
        if not raw:
            return None, "", caption_text
        # mp3 is the canonical clip format in our pipeline; if not, the
        # generic audio/mpeg header still works for both Live API and
        # generate_content.
        mime = "audio/mpeg"
        return types.Part.from_bytes(data=raw, mime_type=mime), mime, "audio"

    return None, "", caption_text


def _build_system_instruction(doc: dict) -> str:
    cap = doc.get("caption") or {}
    bits = []
    if cap.get("title"):
        bits.append(f"title='{cap['title']}'")
    if doc.get("caption_text"):
        bits.append(f"caption='{doc['caption_text'][:200]}'")
    if doc.get("modality"):
        bits.append(f"modality={doc['modality']}")
    if doc.get("kind"):
        bits.append(f"kind={doc['kind']}")
    if cap.get("dominant_colors"):
        bits.append(f"colors={cap['dominant_colors'][:4]}")
    if cap.get("tags"):
        bits.append(f"tags={cap['tags'][:8]}")
    if cap.get("bpm") or cap.get("tempo_bpm"):
        bits.append(f"bpm={cap.get('bpm') or cap.get('tempo_bpm')}")
    meta = " · ".join(bits) if bits else "(no structured caption)"
    return f"{ASSET_CHAT_SYSTEM}\n\nAsset metadata: {meta}"


# ---------- text-mode chat (fallback / no-mic clients) ----------------------
class AssetChatMessage(BaseModel):
    role: str
    text: str


class AssetChatRequest(BaseModel):
    message: str
    history: list[AssetChatMessage] = []


@app.post("/api/chat/{asset_id}")
async def api_asset_chat(asset_id: str, body: AssetChatRequest):
    """Text-only chat about a single asset, using gemini-2.5-flash with the
    asset attached as multimodal context. This is the graceful fallback for
    when the user can't (or won't) use the Live voice path."""
    doc = _segment_doc(asset_id)
    asset_part, mime, kind = _build_asset_part(doc)
    sys_instruction = _build_system_instruction(doc)

    # Build the multi-turn `contents` array. We attach the asset to the very
    # first user turn so it persists across follow-ups, then replay history.
    contents: list = []
    first_parts: list = []
    if asset_part is not None:
        first_parts.append(asset_part)
    first_parts.append(types.Part.from_text(
        text="(The asset above is the subject of this conversation.)"
    ))
    contents.append(types.Content(role="user", parts=first_parts))
    contents.append(types.Content(role="model", parts=[types.Part.from_text(
        text="Got it — I have the asset in front of me. Ask away."
    )]))
    for m in body.history[-12:]:
        role = "user" if m.role == "user" else "model"
        contents.append(types.Content(
            role=role, parts=[types.Part.from_text(text=m.text)]
        ))
    contents.append(types.Content(
        role="user", parts=[types.Part.from_text(text=body.message)]
    ))

    cfg = types.GenerateContentConfig(
        system_instruction=sys_instruction,
        temperature=0.6,
        max_output_tokens=400,
    )

    t0 = now_ms()
    try:
        resp = await CLIENT.aio.models.generate_content(
            model=CHAT_MODEL, contents=contents, config=cfg,
        )
    except Exception as exc:
        raise HTTPException(500, f"chat failed: {exc}")
    return {
        "asset_id": asset_id,
        "modality": doc.get("modality"),
        "kind": doc.get("kind"),
        "asset_attached": asset_part is not None,
        "asset_kind": kind,
        "asset_mime": mime,
        "model": CHAT_MODEL,
        "reply": (resp.text or "").strip(),
        "latency_ms": round(ms_since(t0), 2),
    }


# ---------- live voice chat (WebSocket bridge) ------------------------------
@app.websocket("/api/live/{asset_id}")
async def api_asset_live(ws: WebSocket, asset_id: str):
    """Bidirectional bridge between the browser and Gemini Live API.

    Browser → server (binary):   PCM16 mono 16kHz audio chunks
    Browser → server (text):     {"type":"end"}  end-of-turn marker
                                 {"type":"text","text":"..."}  optional text
    Server → browser (binary):   PCM16 mono 24kHz model audio chunks
    Server → browser (text):     {"type":"transcript","role":"user|model","text":"..."}
                                 {"type":"status","msg":"..."}
                                 {"type":"error","msg":"..."}
                                 {"type":"turn_complete"}
    """
    await ws.accept()
    try:
        doc = _segment_doc(asset_id)
    except HTTPException as exc:
        await ws.send_json({"type": "error", "msg": exc.detail})
        await ws.close()
        return

    asset_part, mime, kind = _build_asset_part(doc)
    sys_instruction = _build_system_instruction(doc)

    config = types.LiveConnectConfig(
        response_modalities=[types.Modality.AUDIO],
        system_instruction=types.Content(
            role="user", parts=[types.Part.from_text(text=sys_instruction)],
        ),
        input_audio_transcription=types.AudioTranscriptionConfig(),
        output_audio_transcription=types.AudioTranscriptionConfig(),
    )

    await ws.send_json({
        "type": "status",
        "msg": f"connecting to {LIVE_MODEL}",
        "asset_kind": kind,
        "asset_attached": asset_part is not None,
        "modality": doc.get("modality"),
    })

    try:
        async with CLIENT.aio.live.connect(model=LIVE_MODEL, config=config) as session:
            # Seed the session with the asset bytes so every voice turn is
            # asset-aware. Use send_client_content (turn-complete=False) so
            # the model treats this as background context.
            if asset_part is not None:
                try:
                    await session.send_client_content(
                        turns=types.Content(role="user", parts=[
                            asset_part,
                            types.Part.from_text(text=(
                                "This is the asset we're discussing. "
                                "Listen for my next question and respond about it."
                            )),
                        ]),
                        turn_complete=True,
                    )
                except Exception as exc:
                    await ws.send_json({"type": "status",
                                        "msg": f"asset attach warn: {exc}"})

            await ws.send_json({"type": "status", "msg": "live"})

            async def browser_to_model():
                """Pump browser → Gemini Live."""
                try:
                    while True:
                        msg = await ws.receive()
                        if msg.get("type") == "websocket.disconnect":
                            return
                        if "bytes" in msg and msg["bytes"] is not None:
                            await session.send_realtime_input(audio=types.Blob(
                                data=msg["bytes"],
                                mime_type="audio/pcm;rate=16000",
                            ))
                            continue
                        if "text" in msg and msg["text"]:
                            try:
                                payload = json.loads(msg["text"])
                            except Exception:
                                continue
                            ev = payload.get("type")
                            if ev == "end":
                                # End-of-turn marker; tells Gemini we're done speaking.
                                try:
                                    await session.send_realtime_input(audio_stream_end=True)
                                except Exception:
                                    pass
                            elif ev == "text" and payload.get("text"):
                                await session.send_client_content(
                                    turns=types.Content(role="user", parts=[
                                        types.Part.from_text(text=payload["text"]),
                                    ]),
                                    turn_complete=True,
                                )
                            elif ev == "interrupt":
                                # Best-effort interrupt: send activity_end so the
                                # model knows the user wants to barge in.
                                try:
                                    await session.send_realtime_input(activity_end={})
                                except Exception:
                                    pass
                except WebSocketDisconnect:
                    return
                except Exception as exc:
                    print(f"[live] browser_to_model error: {exc}")

            async def model_to_browser():
                """Pump Gemini Live → browser. session.receive() yields one
                turn at a time and then exits, so we wrap it in a loop that
                keeps draining as long as the session and websocket are open."""
                try:
                    while True:
                        try:
                            async for response in session.receive():
                                sc = getattr(response, "server_content", None)
                                if sc is not None:
                                    mt = getattr(sc, "model_turn", None)
                                    if mt and getattr(mt, "parts", None):
                                        for part in mt.parts:
                                            inline = getattr(part, "inline_data", None)
                                            if inline and getattr(inline, "data", None):
                                                await ws.send_bytes(inline.data)
                                            txt = getattr(part, "text", None)
                                            if txt:
                                                await ws.send_json({
                                                    "type": "transcript",
                                                    "role": "model",
                                                    "text": txt,
                                                })
                                    it = getattr(sc, "input_transcription", None)
                                    if it and getattr(it, "text", None):
                                        await ws.send_json({
                                            "type": "transcript",
                                            "role": "user",
                                            "text": it.text,
                                        })
                                    ot = getattr(sc, "output_transcription", None)
                                    if ot and getattr(ot, "text", None):
                                        await ws.send_json({
                                            "type": "transcript",
                                            "role": "model",
                                            "text": ot.text,
                                        })
                                    if getattr(sc, "turn_complete", False):
                                        await ws.send_json({"type": "turn_complete"})
                                data = getattr(response, "data", None)
                                if data:
                                    await ws.send_bytes(data)
                        except Exception as exc:
                            # Connection closed by the server / SDK — exit the
                            # outer loop too. Any other transient error: same.
                            print(f"[live] receive loop ended: {exc}")
                            return
                        # Yield to the event loop so the writer can run a tick.
                        await asyncio.sleep(0)
                except Exception as exc:
                    print(f"[live] model_to_browser error: {exc}")

            up = asyncio.create_task(browser_to_model())
            down = asyncio.create_task(model_to_browser())
            done, pending = await asyncio.wait(
                {up, down}, return_when=asyncio.FIRST_COMPLETED
            )
            for t in pending:
                t.cancel()
    except Exception as exc:
        print(f"[live] session error: {exc}")
        try:
            await ws.send_json({"type": "error",
                                "msg": f"live session failed: {exc}"})
        except Exception:
            pass
    finally:
        try:
            await ws.close()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Vibe Slider — learned delta vectors per perceptual axis.
# Each axis = l2norm(embed(positive_pole) - embed(negative_pole)). Adding a
# scaled delta to a query vector nudges retrieval along that axis (warmer,
# more energetic, more cinematic, busier) without changing the search topic.
# Computed lazily on first search and cached process-wide.
# ---------------------------------------------------------------------------
VIBE_AXES: dict[str, tuple[str, str]] = {
    "warm":      ("warm cozy nostalgic golden glowing inviting amber sunlit "
                  "soft firelight tungsten honeyed",
                  "cool sterile clinical blue harsh detached fluorescent icy "
                  "metallic shadowy steel-toned"),
    "energy":    ("energetic fast intense kinetic high-tempo bursting "
                  "frenetic explosive driving pulsing vivid action",
                  "calm quiet still tranquil meditative slow ambient "
                  "peaceful gentle restful hushed serene"),
    "cinematic": ("cinematic dramatic moody film grain anamorphic shallow "
                  "depth-of-field directed lit storyboarded epic widescreen",
                  "casual snapshot everyday flat documentary candid amateur "
                  "phone-photo handheld unposed plain"),
    "busy":      ("busy crowded layered detailed maximalist intricate dense "
                  "ornate textured packed cluttered complex",
                  "minimal empty negative-space clean simple sparse plain "
                  "uncluttered restrained spacious bare"),
}

_VIBE_DELTAS: dict[str, np.ndarray] = {}


def compute_vibe_deltas() -> dict[str, np.ndarray]:
    """Return the cached {axis: unit-delta} dict, embedding the pole pairs
    on first call. embed_text already l2-normalises, but the *difference* of
    two unit vectors is not unit-length — we re-normalise so a slider value
    of 1.0 always biases by the same magnitude regardless of axis.
    Thread-safety: dict assignment is atomic in CPython, and a duplicate
    first-call from a concurrent request just wastes one batch of embeds."""
    global _VIBE_DELTAS
    if _VIBE_DELTAS:
        return _VIBE_DELTAS
    deltas: dict[str, np.ndarray] = {}
    for axis, (pos_text, neg_text) in VIBE_AXES.items():
        try:
            pos_v = embed_text(pos_text)
            neg_v = embed_text(neg_text)
            d = pos_v - neg_v
            n = float(np.linalg.norm(d))
            if n > 0:
                deltas[axis] = (d / n).astype(np.float32)
        except Exception as exc:
            print(f"[vibe] embed failed for axis '{axis}': {exc}")
    if deltas:
        _VIBE_DELTAS = deltas
        print(f"[vibe] computed {len(deltas)} axis deltas: {list(deltas.keys())}")
    return _VIBE_DELTAS


# ---------------------------------------------------------------------------
# Build a Kit — cross-modal complementary asset bundle from a seed segment
# ---------------------------------------------------------------------------
KIT_TARGET_MODALITIES: tuple[str, ...] = (
    "photo", "video", "audio_music", "audio_sfx", "graphic",
)


def _kit_source_modality(doc: dict) -> str:
    """Map a Firestore segment doc to one of KIT_TARGET_MODALITIES."""
    modality = (doc.get("modality") or "").lower()
    kind = (doc.get("kind") or "").lower()
    if modality == "audio" or modality == "sfx" or kind == "sfx":
        return "audio_sfx" if (kind == "sfx" or modality == "sfx") else "audio_music"
    return modality or ""


def _kit_query_one(q_vec: np.ndarray, target: str, *,
                   exclude_dp: str, exclude_asset: str) -> dict | None:
    """Single-modality VS query, returning the best non-self hit hydrated as
    a result-card dict. Music vs sfx is split client-side because the index
    stores them under different `modality` tokens."""
    if target == "audio_music":
        # Music is stored with modality="audio" (kind != "sfx"). Over-fetch
        # so we can drop self + any sfx bleed before picking top-1.
        hits = vs_find_neighbors(q_vec, k=8, modality="audio")
    elif target == "audio_sfx":
        # SFX lives under modality="sfx" in this index.
        hits = vs_find_neighbors(q_vec, k=8, modality="sfx")
    else:
        hits = vs_find_neighbors(q_vec, k=8, modality=target)

    if not hits:
        return None
    cards = hydrate_segments(hits)
    for c in cards:
        if c.get("datapoint_id") == exclude_dp:
            continue
        if exclude_asset and c.get("asset_id") == exclude_asset:
            continue
        mod = (c.get("modality") or "").lower()
        kind = (c.get("kind") or "").lower()
        if target == "audio_music":
            if kind == "sfx" or mod != "audio":
                continue
        elif target == "audio_sfx":
            if mod != "sfx" and kind != "sfx":
                continue
        return c
    return None


@app.post("/api/kit/{datapoint_id}")
def api_build_kit(datapoint_id: str, q: str | None = None):
    """Build a complementary cross-modal "kit" for a seed segment.

    Re-embed the seed's caption_text (fast + deterministic) and fan out one
    single-modality VS query per target modality, returning the top-1 hit
    per modality (excluding the seed's own asset) shaped as standard
    result-card dicts so the UI can render with existing widgets.
    """
    t0 = now_ms()
    snap = fs().collection(FIRESTORE_SEGMENTS).document(datapoint_id).get()
    if not snap.exists:
        raise HTTPException(404, f"segment {datapoint_id} not found")
    doc = snap.to_dict() or {}

    src_modality = _kit_source_modality(doc)
    src_asset = doc.get("asset_id") or ""
    cap = doc.get("caption") or {}
    seed_caption = (
        doc.get("caption_text")
        or cap.get("title")
        or cap.get("description")
        or ""
    ).strip()
    # When the kit is opened from a search result, prefix the user's query so
    # the embedded vector inherits the scene words the seed caption may lack
    # (e.g. a folk-guitar caption with no "beach" anchor still produces a
    # beach-flavoured kit when q="tropical beach getaway").
    user_q = (q or "").strip()
    if user_q:
        caption_text = f"Project vibe: {user_q}. Seed asset: {seed_caption}"
    else:
        caption_text = seed_caption

    seed_summary = {
        "datapoint_id": datapoint_id,
        "asset_id": src_asset,
        "modality": src_modality,
        "modality_raw": doc.get("modality"),
        "kind": doc.get("kind"),
        "caption_text": seed_caption,
        "title": cap.get("title") or "",
        "thumbnail_url": signed_url(doc.get("thumbnail_gcs")),
        "embedding_source": "caption_text+query" if user_q else "caption_text",
        "user_query": user_q or None,
    }

    targets = [m for m in KIT_TARGET_MODALITIES if m != src_modality]

    if not caption_text:
        # Nothing to embed → empty kit + warning, instead of 500.
        return JSONResponse({
            "source": seed_summary,
            "kit": {m: None for m in targets},
            "build_ms": round(ms_since(t0), 2),
            "warning": "seed segment has no caption_text — kit unavailable",
        })

    try:
        q_vec = embed_text(caption_text)
    except Exception as exc:
        raise HTTPException(500, f"failed to embed seed caption: {exc}")

    from concurrent.futures import ThreadPoolExecutor
    kit: dict[str, dict | None] = {}
    with ThreadPoolExecutor(max_workers=max(1, len(targets))) as ex:
        futs = {
            m: ex.submit(_kit_query_one, q_vec, m,
                         exclude_dp=datapoint_id, exclude_asset=src_asset)
            for m in targets
        }
        for m, fut in futs.items():
            try:
                kit[m] = fut.result()
            except Exception as exc:
                print(f"[kit] target={m} failed: {exc}")
                kit[m] = None

    return JSONResponse({
        "source": seed_summary,
        "kit": kit,
        "build_ms": round(ms_since(t0), 2),
    })


NANO_BANANA_MODEL = os.environ.get("ENVATO_NANO_BANANA_MODEL", "gemini-3.1-flash-image-preview")
LYRIA_MODEL = os.environ.get("ENVATO_LYRIA_MODEL", "lyria-3-clip-preview")
VEO_MODEL = os.environ.get("ENVATO_VEO_MODEL", "veo-3.1-lite-generate-001")
CHIRP_VOICE = os.environ.get("ENVATO_CHIRP_VOICE", "en-US-Chirp3-HD-Charon")
GEMINI_TTS_MODEL = os.environ.get("ENVATO_GEMINI_TTS_MODEL", "gemini-3.1-flash-tts-preview")
GEMINI_TTS_VOICE = os.environ.get("ENVATO_GEMINI_TTS_VOICE", "Kore")


class CreateImageReq(BaseModel):
    prompt: str


@app.post("/api/create/image")
def api_create_image(req: CreateImageReq):
    """Generate an image with Nano Banana (gemini-3.1-flash-image-preview, global region)
    from a prompt. Returns the PNG bytes as base64 so the panel can render inline."""
    import base64
    t0 = now_ms()
    prompt = (req.prompt or "").strip()
    if not prompt:
        raise HTTPException(400, "prompt is required")
    cfg = types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"])
    resp = GLOBAL_CLIENT.models.generate_content(
        model=NANO_BANANA_MODEL, contents=prompt, config=cfg,
    )
    img_b64 = None
    mime = "image/png"
    text_out = []
    for p in (resp.candidates[0].content.parts or []):
        if getattr(p, "inline_data", None) and p.inline_data.data:
            img_b64 = base64.b64encode(p.inline_data.data).decode("ascii")
            mime = p.inline_data.mime_type or "image/png"
            break
        if getattr(p, "text", None):
            text_out.append(p.text)
    if not img_b64:
        raise HTTPException(502, f"no image returned (text='{' '.join(text_out)[:200]}')")
    return JSONResponse({
        "model": NANO_BANANA_MODEL,
        "mime": mime,
        "image_b64": img_b64,
        "prompt": prompt,
        "elapsed_ms": round(ms_since(t0), 2),
    })


class CreateMusicReq(BaseModel):
    prompt: str


@app.post("/api/create/music")
def api_create_music(req: CreateMusicReq):
    """Generate music with Lyria 3 (lyria-3-clip-preview, global region) from a prompt.
    Returns base64 MP3 bytes plus the model's auto-generated caption."""
    import base64
    import google.auth
    import google.auth.transport.requests
    import requests as _requests

    t0 = now_ms()
    prompt = (req.prompt or "").strip()
    if not prompt:
        raise HTTPException(400, "prompt is required")

    creds, _proj = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(google.auth.transport.requests.Request())
    url = f"https://aiplatform.googleapis.com/v1beta1/projects/{PROJECT}/locations/global/interactions"
    body = {"model": LYRIA_MODEL, "input": [{"type": "text", "text": prompt}]}
    r = _requests.post(
        url,
        headers={"Authorization": f"Bearer {creds.token}", "Content-Type": "application/json"},
        json=body, timeout=180,
    )
    if r.status_code >= 400:
        raise HTTPException(r.status_code, f"lyria error: {r.text[:400]}")
    j = r.json()
    audio_b64 = None
    mime = "audio/mpeg"
    caption = ""
    for o in (j.get("outputs") or []):
        if o.get("type") == "audio" and o.get("data"):
            audio_b64 = o["data"]
            mime = o.get("mime_type") or mime
        elif o.get("type") == "text" and o.get("text"):
            caption = o["text"]
    if not audio_b64:
        raise HTTPException(502, "lyria returned no audio")
    return JSONResponse({
        "model": LYRIA_MODEL,
        "mime": mime,
        "audio_b64": audio_b64,
        "caption": caption,
        "prompt": prompt,
        "elapsed_ms": round(ms_since(t0), 2),
    })


class CreateVideoReq(BaseModel):
    prompt: str
    aspect_ratio: str | None = "16:9"


@app.post("/api/create/video")
def api_create_video(req: CreateVideoReq):
    """Generate a short video with Veo 3 (veo-3.0-generate-001, us-central1) from a prompt.
    Polls the LRO and returns base64 MP4 bytes inline."""
    import base64, time as _time
    t0 = now_ms()
    prompt = (req.prompt or "").strip()
    if not prompt:
        raise HTTPException(400, "prompt is required")
    src = types.GenerateVideosSource(prompt=prompt)
    cfg = types.GenerateVideosConfig(
        aspect_ratio=(req.aspect_ratio or "16:9"),
        number_of_videos=1,
        duration_seconds=8,
        person_generation="allow_all",
        generate_audio=True,
        resolution="720p",
    )
    op = CLIENT.models.generate_videos(model=VEO_MODEL, source=src, config=cfg)
    deadline = _time.time() + 240  # 4-min cap
    while not getattr(op, "done", False):
        if _time.time() > deadline:
            raise HTTPException(504, "veo generation timed out after 240s")
        _time.sleep(5)
        op = CLIENT.operations.get(op)
    if not op.result or not op.result.generated_videos:
        raise HTTPException(502, "veo returned no videos")
    gv = op.result.generated_videos[0]
    if not gv.video or not gv.video.video_bytes:
        raise HTTPException(502, "veo result missing video_bytes")
    video_b64 = base64.b64encode(gv.video.video_bytes).decode("ascii")
    return JSONResponse({
        "model": VEO_MODEL,
        "mime": gv.video.mime_type or "video/mp4",
        "video_b64": video_b64,
        "prompt": prompt,
        "elapsed_ms": round(ms_since(t0), 2),
    })


class CreateVoiceReq(BaseModel):
    prompt: str
    voice: str | None = None
    language_code: str | None = None


def _pcm_to_wav(pcm: bytes, channels: int = 1, rate: int = 24000, sample_width: int = 2) -> bytes:
    import io, wave
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)
    return buf.getvalue()


@app.post("/api/create/voice")
def api_create_voice(req: CreateVoiceReq):
    """Synthesize speech with Gemini 3.1 Flash TTS (audio-tag aware).
    Returns base64 WAV (PCM 24kHz mono) inline."""
    import base64
    t0 = now_ms()
    text = (req.prompt or "").strip()
    if not text:
        raise HTTPException(400, "prompt is required")
    voice_name = (req.voice or GEMINI_TTS_VOICE).strip()
    cfg = types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name),
            ),
        ),
    )
    try:
        resp = GLOBAL_CLIENT.models.generate_content(
            model=GEMINI_TTS_MODEL, contents=text, config=cfg,
        )
    except Exception as e:
        raise HTTPException(502, f"gemini tts error: {e}")
    if not resp.candidates:
        pf = getattr(resp, "prompt_feedback", None)
        reason = getattr(pf, "block_reason", None)
        msg = getattr(pf, "block_reason_message", "") or ""
        if reason:
            raise HTTPException(400, f"gemini tts blocked ({reason}): {msg[:240]}")
        raise HTTPException(502, "gemini tts: empty response")
    pcm = None
    try:
        for part in (resp.candidates[0].content.parts or []):
            inline = getattr(part, "inline_data", None)
            if inline and getattr(inline, "data", None):
                pcm = inline.data
                break
    except Exception as e:
        raise HTTPException(502, f"gemini tts parse error: {e}")
    if not pcm:
        raise HTTPException(502, "gemini tts: no audio in response parts")
    wav = _pcm_to_wav(pcm)
    return JSONResponse({
        "model": GEMINI_TTS_MODEL,
        "voice": voice_name,
        "mime": "audio/wav",
        "audio_b64": base64.b64encode(wav).decode("ascii"),
        "prompt": text,
        "elapsed_ms": round(ms_since(t0), 2),
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app_v2:app", host="0.0.0.0", port=8090, reload=False)
