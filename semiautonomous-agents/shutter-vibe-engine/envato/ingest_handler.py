"""Cloud Run service that turns GCS object-finalized events into segments.

Drop any file into gs://envato-vibe-demo/ingest/<name>.{jpg,png,mp4,mp3,wav}
and within seconds it becomes:
  • thumbnails/<asset_id>/...webp
  • segments/<asset_id>/...{mp4,mp3}
  • originals/<asset_id>.<ext>
  • Firestore docs in `segments`
  • Vector Search datapoints (queryable in seconds via STREAM_UPDATE)

Wiring:
  Eventarc trigger filters bucket=envato-vibe-demo. The handler ignores any
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
sys.path.insert(0, str(ROOT))

from pipeline_v2 import (  # noqa: E402
    GCS, VS, GCS_BUCKET, process_asset,
)

app = FastAPI(title="Envato Vibe — auto-ingest")

EXT_TO_CATEGORY = {
    ".jpg": "photo", ".jpeg": "photo", ".webp": "photo",
    ".png": "graphic", ".svg": "graphic",
    ".mp4": "video", ".mov": "video", ".webm": "video",
    ".mp3": "audio", ".wav": "audio", ".m4a": "audio", ".ogg": "audio",
}

INGEST_PREFIX = "ingest/"


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
