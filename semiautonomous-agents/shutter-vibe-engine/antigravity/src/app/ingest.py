"""Cloud Run service that turns GCS object-finalized events into segments.

Drop any file into gs://<your-bucket>/ingest/<name>.{jpg,png,mp4,mp3,wav}
and within seconds it becomes:
  • thumbnails/<asset_id>/...webp
  • segments/<asset_id>/...{mp4,mp3}
  • originals/<asset_id>.<ext>
  • Firestore docs in `segments`
  • Vector Search datapoints (queryable in seconds via STREAM_UPDATE)

Wiring:
  Eventarc trigger filters bucket=<your-bucket>. The handler ignores any
  event NOT under `ingest/` so the writes the pipeline itself makes
  (thumbnails/, segments/, originals/) don't recurse.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path

from fastapi import FastAPI, Request, Response

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "pipeline"))

from build import (  # noqa: E402
    GCS, VS, GCS_BUCKET, process_asset,
)

app = FastAPI(title="Vibe Search — auto-ingest")

EXT_TO_CATEGORY = {
    ".jpg": "photo", ".jpeg": "photo", ".webp": "photo",
    ".png": "graphic", ".svg": "graphic",
    ".mp4": "video", ".mov": "video", ".webm": "video",
    ".mp3": "audio", ".wav": "audio", ".m4a": "audio", ".ogg": "audio",
}

# Stills where the extension can't tell us photo-vs-illustration. PNGs from
# AI image generators are photo-like, but PNGs from designers are usually
# logos/illustrations — same extension. Same for webp. We re-classify these
# by content with a tiny Gemini call instead of trusting the suffix.
AMBIGUOUS_STILL_EXTS = {".png", ".webp", ".jpg", ".jpeg"}

INGEST_PREFIX = "ingest/"

CLASSIFIER_MODEL = "gemini-3.1-flash-lite-preview"  # cheapest still-image model
_CLASSIFIER_CLIENT = None


def _classifier_client():
    """Global region — flash-lite preview only lives there."""
    global _CLASSIFIER_CLIENT
    if _CLASSIFIER_CLIENT is None:
        from google import genai
        _CLASSIFIER_CLIENT = genai.Client(
            vertexai=True,
            project=os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos"),
            location="global",
        )
    return _CLASSIFIER_CLIENT


def classify_still(image_bytes: bytes, mime: str) -> str:
    """Return 'photo' or 'graphic' based on what's in the pixels.

    Photo  = photograph, AI-generated photoreal image, video frame still.
    Graphic = logo, icon, illustration, diagram, screenshot, UI mockup,
              vector art, anything with flat color regions or transparency.

    On any error → fall back to 'photo' (the safer default for stock catalogs:
    a misclassified graphic in the photo bucket is less surprising than a
    misclassified photo hidden under graphics)."""
    from google.genai import types
    try:
        resp = _classifier_client().models.generate_content(
            model=CLASSIFIER_MODEL,
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime),
                "Is this a photograph (or AI-generated photo-like image), "
                "or a graphic (logo, icon, illustration, diagram, screenshot, "
                "UI element)? Answer with exactly one word: 'photo' or 'graphic'.",
            ],
            config=types.GenerateContentConfig(
                temperature=0.0, max_output_tokens=8,
            ),
        )
        out = (resp.text or "").strip().lower()
        if "graphic" in out: return "graphic"
        if "photo"   in out: return "photo"
    except Exception as exc:
        print(f"[classify] failed, defaulting to photo: {exc}")
    return "photo"


def _slug(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:48] or "asset"


def _asset_id_for(object_name: str) -> str:
    base = Path(object_name).stem
    digest = hashlib.sha1(object_name.encode()).hexdigest()[:8]
    return f"upload-{_slug(base)}-{digest}"


@app.get("/")
def health() -> dict:
    return {"ok": True, "service": "envato-vibe-ingest"}


@app.post("/")
async def handle_event(request: Request) -> Response:
    payload = await request.json()
    bucket = payload.get("bucket") or ""
    name = payload.get("name") or ""

    if bucket != GCS_BUCKET or not name.startswith(INGEST_PREFIX):
        return Response(status_code=204)        # ack and ignore

    ext = Path(name).suffix.lower()
    category = EXT_TO_CATEGORY.get(ext)
    if not category:
        print(f"[ingest] skip unsupported ext: {name}")
        return Response(status_code=204)

    asset_id = _asset_id_for(name)
    print(f"[ingest] start  bucket={bucket} name={name} asset_id={asset_id}")

    from google.cloud import storage, firestore
    storage_client = storage.Client()
    src_blob = storage_client.bucket(bucket).blob(name)
    if not src_blob.exists():
        return Response(status_code=204)

    # For ambiguous still extensions (.png, .webp, .jpg) re-classify by
    # content. The download_as_bytes is cheap relative to the embedding/
    # captioning that follows and avoids a second GCS round-trip.
    if ext in AMBIGUOUS_STILL_EXTS:
        try:
            head = src_blob.download_as_bytes()
            mime = "image/png" if ext == ".png" else (
                "image/webp" if ext == ".webp" else "image/jpeg")
            classified = classify_still(head, mime)
            if classified != category:
                print(f"[ingest] reclassify {ext} {category} → {classified}")
                category = classified
        except Exception as exc:
            print(f"[ingest] classify skipped, keeping ext default: {exc}")

    # Download to a temp local path that pipeline_v2 expects under ROOT.
    sub = {"photo": "photos", "graphic": "graphics",
           "video": "videos", "audio": "audio"}[category]
    local_dir = ROOT / "assets" / sub
    local_dir.mkdir(parents=True, exist_ok=True)
    local_path = local_dir / f"{asset_id}{ext}"
    src_blob.download_to_filename(str(local_path))

    item = {
        "asset_id": asset_id,
        "category": category,
        "sub_category": "user-upload",
        "caption": f"User-uploaded {category}: {Path(name).stem}",
        "tags": [category, "user-upload"],
        "contributor": "user",
        "license": "user-supplied",
        "local_path": str(local_path.relative_to(ROOT)),
    }

    fs = firestore.Client(project=os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos"))
    gcs = GCS()
    vs = VS()

    t0 = time.perf_counter()
    written = process_asset(item, gcs, fs, vs, force=False)
    elapsed = time.perf_counter() - t0
    print(f"[ingest] done   asset_id={asset_id} segments={written} elapsed={elapsed:.1f}s")

    # Move the source out of ingest/ so the same upload doesn't reprocess.
    archived_blob = storage_client.bucket(bucket).blob(
        f"originals/{asset_id}{ext}")
    if not archived_blob.exists():
        storage_client.bucket(bucket).copy_blob(
            src_blob, storage_client.bucket(bucket), archived_blob.name)
    src_blob.delete()

    # Stamp a per-upload audit doc so the UI can show an "ingested" toast.
    fs.collection("uploads").document(asset_id).set({
        "asset_id": asset_id,
        "object_name": name,
        "segments_written": written,
        "elapsed_s": elapsed,
        "ts": time.time(),
    })

    return Response(status_code=200)
