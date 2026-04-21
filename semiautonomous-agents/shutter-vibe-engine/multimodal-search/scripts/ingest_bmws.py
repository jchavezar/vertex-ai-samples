"""One-shot ingest from tmp/{images,videos}/<batch>/ that bypasses the broken
Cloud Run ingest service. Forces the right category so the deployed service's
PNG→graphic default doesn't bury still images in the wrong modality.

Usage:
    python scripts/ingest_bmws.py images bmw_x3_car_20260419_221944
    python scripts/ingest_bmws.py videos bmw_x3_car_20260419_224622
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
sys.path.insert(0, str(ROOT.parent / "demos"))   # for _client

from build import GCS, VS, GCS_BUCKET, process_asset  # noqa: E402
from google.cloud import storage, firestore  # noqa: E402

PROJECT = "vtxdemos"

# kind → (extension allowlist, modality category, asset_id prefix, sub-dir)
KIND_CFG = {
    "images": ((".png", ".jpg", ".jpeg", ".webp"), "photo", "image", "photos"),
    "videos": ((".mp4", ".mov", ".webm"),          "video", "video", "videos"),
}


def _slug(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:48] or "asset"


def asset_id_for(object_name: str, prefix: str) -> str:
    base = Path(object_name).stem
    digest = hashlib.sha1(object_name.encode()).hexdigest()[:8]
    return f"upload-{prefix}-{_slug(base)}-{digest}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=list(KIND_CFG.keys()),
                    help="images or videos")
    ap.add_argument("batch", help="batch folder name under tmp/<kind>/")
    ap.add_argument("--tags", default="bmw,x3,car",
                    help="comma-separated tags appended to each item")
    args = ap.parse_args()

    exts, category, aid_prefix, subdir = KIND_CFG[args.kind]
    gcs_prefix = f"tmp/{args.kind}/{args.batch}/"
    extra_tags = [t.strip() for t in args.tags.split(",") if t.strip()]

    sclient = storage.Client(project=PROJECT)
    bucket = sclient.bucket(GCS_BUCKET)
    blobs = [b for b in sclient.list_blobs(GCS_BUCKET, prefix=gcs_prefix)
             if b.name.lower().endswith(exts)]
    print(f"Found {len(blobs)} {args.kind} to ingest under {gcs_prefix}")

    fs = firestore.Client(project=PROJECT)
    gcs = GCS()
    vs = VS()

    local_dir = ROOT / "assets" / subdir
    local_dir.mkdir(parents=True, exist_ok=True)

    total_segments = 0
    for i, blob in enumerate(blobs, 1):
        aid = asset_id_for(blob.name, aid_prefix)
        ext = Path(blob.name).suffix.lower()
        local_path = local_dir / f"{aid}{ext}"
        if not local_path.exists():
            blob.download_to_filename(str(local_path))
        item = {
            "asset_id": aid,
            "category": category,
            "sub_category": "user-upload",
            "caption": f"User-uploaded {category}: {Path(blob.name).stem} ({' '.join(extra_tags)})",
            "tags": [category, "user-upload", *extra_tags],
            "contributor": "user",
            "license": "user-supplied",
            # process_asset resolves with build.ROOT = pipeline/, so we go up.
            "local_path": str(Path("..") / local_path.relative_to(ROOT)),
        }
        t0 = time.perf_counter()
        try:
            n = process_asset(item, gcs, fs, vs, force=False)
            print(f"  [{i:2}/{len(blobs)}] {aid} → {n} seg ({time.perf_counter()-t0:.1f}s)")
            total_segments += n
        except Exception as exc:
            print(f"  [{i:2}/{len(blobs)}] {aid} FAILED: {exc}")

        archived = bucket.blob(f"originals/{aid}{ext}")
        if not archived.exists():
            bucket.copy_blob(blob, bucket, archived.name)

    print(f"\nDone. {total_segments} total segments upserted.")


if __name__ == "__main__":
    main()
