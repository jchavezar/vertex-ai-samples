"""Vibe Search v2 — segment-level multimodal indexing pipeline.

Per-modality plan (locked in the demo plan):
  • photo  → 1 segment (whole asset)
  • video  → 10s window, 2s overlap, mid-frame thumbnail
  • music  → 25s window, 5s overlap, waveform thumbnail
  • sfx    → 8s segments,             waveform thumbnail

Datapoint id convention:  <asset_id>__seg_<NN>__t<start>-<end>

Per segment we:
  1. Cut clip + render thumbnail with ffmpeg
  2. Upload (clip, thumb) to gs://<your-bucket>/segments/<asset_id>/
     and the original (lazy, once) to gs://.../originals/<asset_id>.<ext>
  3. Caption the segment with Gemini (structured JSON)
       - video → gemini-3.0-flash-preview      (visual+motion nuance)
       - audio → gemini-3.1-flash-lite-preview (cheaper, listens to mp3)
       - photo → gemini-3.1-flash-lite-preview
  4. Embed (segment thumbnail + caption text) with gemini-embedding-2-preview
     (multimodal, 3072-dim, L2-normed)
  5. Write a Firestore doc keyed by datapoint_id (`segments` collection)
  6. Upsert into Vector Search with namespace restricts:
       modality, length_bucket, tempo_bucket (music only), palette

Idempotent: if a Firestore doc already exists for a datapoint_id, the segment
is skipped unless --force.

Usage:
  uv run --python .venv/bin/python pipeline/build.py --asset-id px-video-9620654
  uv run --python .venv/bin/python pipeline/build.py --modality video --limit 3
  uv run --python .venv/bin/python pipeline/build.py            # full corpus
"""
from __future__ import annotations

import argparse
import io
import json
import math
import os
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "demos"))
from _client import CLIENT  # noqa: E402
from google import genai  # noqa: E402
from google.genai import types  # noqa: E402

# Lite captioner only lives in `global` region — own client.
GLOBAL_CLIENT = genai.Client(vertexai=True,
                             project=os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos"),
                             location="global")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
GCS_BUCKET = os.environ.get("ENVATO_GCS_BUCKET", "envato-vibe-demo")
INDEX_DISPLAY_NAME = "envato-vibe-multimodal"
ENDPOINT_DISPLAY_NAME = "envato-vibe-endpoint"
FIRESTORE_COLLECTION = "segments"

EMBED_MODEL = "gemini-embedding-2-preview"
VIDEO_CAPTIONER = "gemini-3-flash-preview"          # us-central1
AUDIO_CAPTIONER = "gemini-3.1-flash-lite-preview"   # global
PHOTO_CAPTIONER = "gemini-3.1-flash-lite-preview"   # global

MANIFEST_PATH = ROOT / "assets" / "manifest.json"

# Segmentation knobs (seconds)
SEG_VIDEO_WINDOW, SEG_VIDEO_OVERLAP = 10.0, 2.0
SEG_MUSIC_WINDOW, SEG_MUSIC_OVERLAP = 25.0, 5.0
SEG_SFX_WINDOW = 8.0

SFX_KEYWORDS = (
    "sound effect", "whoosh", "footsteps", "thunder", "static",
    "applause", "crowd", "transition", "cheer",
)

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------
def log(stage: str, msg: str) -> None:
    print(f"[{stage}] {msg}", flush=True)


def run(cmd: list[str]) -> None:
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"{cmd[0]} failed: {res.stderr.strip()[:300]}")


def ffprobe_duration(path: Path) -> float:
    res = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True,
    )
    if res.returncode != 0 or not res.stdout.strip():
        return 0.0
    return float(res.stdout.strip())


def is_sfx(item: dict, duration: float) -> bool:
    sub = (item.get("sub_category") or "").lower()
    if any(k in sub for k in SFX_KEYWORDS):
        return True
    return duration > 0 and duration < 30.0


def length_bucket(duration: float) -> str:
    if duration < 5: return "short"
    if duration < 15: return "mid"
    if duration < 60: return "long"
    return "epic"


def tempo_bucket(bpm: float | None) -> str | None:
    if not bpm or bpm <= 0:
        return None
    if bpm < 90: return "slow"
    if bpm < 120: return "mid"
    if bpm < 140: return "upbeat"
    return "fast"


def l2(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.where(n == 0, 1, n)


# ---------------------------------------------------------------------------
# Segment planning
# ---------------------------------------------------------------------------
def plan_segments(item: dict, duration: float) -> list[dict]:
    """Return [{idx, start, end, kind}] for one asset."""
    cat = item["category"]
    if cat == "photo" or cat == "graphic":
        return [{"idx": 0, "start": 0.0, "end": 0.0, "kind": "image"}]

    if cat == "video":
        win, overlap = SEG_VIDEO_WINDOW, SEG_VIDEO_OVERLAP
        kind = "video"
    elif cat == "audio":
        if is_sfx(item, duration):
            return [{"idx": 0, "start": 0.0, "end": min(duration, SEG_SFX_WINDOW),
                     "kind": "sfx"}]
        win, overlap = SEG_MUSIC_WINDOW, SEG_MUSIC_OVERLAP
        kind = "music"
    else:
        return []

    if duration <= win:
        return [{"idx": 0, "start": 0.0, "end": duration, "kind": kind}]

    step = win - overlap
    segs = []
    idx = 0
    t = 0.0
    while t + 1.0 < duration:           # require at least 1s of content
        end = min(t + win, duration)
        segs.append({"idx": idx, "start": round(t, 2), "end": round(end, 2), "kind": kind})
        idx += 1
        if end >= duration:
            break
        t += step
    return segs


def datapoint_id(asset_id: str, seg: dict) -> str:
    return f"{asset_id}__seg_{seg['idx']:02d}__t{int(seg['start'])}-{int(seg['end'])}"


# ---------------------------------------------------------------------------
# Per-segment artifact extraction
# ---------------------------------------------------------------------------
def extract_video_segment(src: Path, start: float, end: float, out_dir: Path,
                          dp_id: str) -> tuple[Path, Path]:
    """Returns (clip_path, thumb_path) — both webp/mp4."""
    clip = out_dir / f"{dp_id}.mp4"
    thumb = out_dir / f"{dp_id}.webp"
    if not clip.exists() or clip.stat().st_size == 0:
        clip.unlink(missing_ok=True)
        run(["ffmpeg", "-y", "-loglevel", "error",
             "-ss", f"{start}", "-to", f"{end}", "-i", str(src),
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "26",
             "-vf", "scale='min(720,iw)':-2", "-an",
             str(clip)])
    if not thumb.exists() or thumb.stat().st_size == 0:
        thumb.unlink(missing_ok=True)
        mid = (start + end) / 2
        png = out_dir / f"{dp_id}.png"
        run(["ffmpeg", "-y", "-loglevel", "error",
             "-ss", f"{mid}", "-i", str(src), "-frames:v", "1",
             "-vf", "scale='min(640,iw)':-2",
             str(png)])
        Image.open(png).convert("RGB").save(thumb, "WEBP", quality=82)
        png.unlink(missing_ok=True)
    return clip, thumb


def extract_audio_segment(src: Path, start: float, end: float, out_dir: Path,
                          dp_id: str) -> tuple[Path, Path]:
    clip = out_dir / f"{dp_id}.mp3"
    thumb = out_dir / f"{dp_id}.webp"
    if not clip.exists() or clip.stat().st_size == 0:
        clip.unlink(missing_ok=True)
        run(["ffmpeg", "-y", "-loglevel", "error",
             "-ss", f"{start}", "-to", f"{end}", "-i", str(src),
             "-c:a", "libmp3lame", "-b:a", "128k", str(clip)])
    if not thumb.exists():
        png = out_dir / f"{dp_id}.png"
        # showwavespic: a clean horizontal waveform PNG
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(clip),
             "-filter_complex",
             "showwavespic=s=640x180:colors=0x6E56CF",
             "-frames:v", "1", str(png)])
        Image.open(png).convert("RGB").save(thumb, "WEBP", quality=85)
        png.unlink(missing_ok=True)
    return clip, thumb


def use_image_as_segment(src: Path, out_dir: Path, dp_id: str) -> tuple[Path, Path]:
    """Photo/graphic: original IS the segment. Generate a 640px webp thumb."""
    thumb = out_dir / f"{dp_id}.webp"
    if not thumb.exists():
        im = Image.open(src).convert("RGB")
        im.thumbnail((640, 640))
        im.save(thumb, "WEBP", quality=85)
    return src, thumb


# ---------------------------------------------------------------------------
# GCS
# ---------------------------------------------------------------------------
class GCS:
    def __init__(self):
        from google.cloud import storage
        self.client = storage.Client(project=PROJECT)
        self.bucket = self.client.bucket(GCS_BUCKET)

    def upload(self, local: Path, gcs_path: str, content_type: str | None = None) -> str:
        blob = self.bucket.blob(gcs_path)
        if not blob.exists():
            blob.upload_from_filename(str(local), content_type=content_type)
        return f"gs://{GCS_BUCKET}/{gcs_path}"

    def signed_url(self, gcs_path: str, hours: int = 24) -> str:
        from datetime import timedelta
        return self.bucket.blob(gcs_path).generate_signed_url(
            expiration=timedelta(hours=hours), version="v4", method="GET",
        )


# ---------------------------------------------------------------------------
# Captioning (structured JSON via Gemini)
# ---------------------------------------------------------------------------
VIDEO_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "scene": {"type": "STRING"},
        "action": {"type": "STRING"},
        "mood": {"type": "STRING"},
        "camera": {"type": "STRING"},
        "dominant_colors": {"type": "ARRAY", "items": {"type": "STRING"}},
        "objects": {"type": "ARRAY", "items": {"type": "STRING"}},
    },
    "required": ["scene", "action", "mood", "dominant_colors", "objects"],
}

MUSIC_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "genre": {"type": "STRING"},
        "mood": {"type": "STRING"},
        "instruments": {"type": "ARRAY", "items": {"type": "STRING"}},
        "tempo_bpm": {"type": "NUMBER"},
        "energy": {"type": "STRING"},
    },
    "required": ["genre", "mood", "instruments", "tempo_bpm", "energy"],
}

SFX_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "category": {"type": "STRING"},
        "source": {"type": "STRING"},
        "environment": {"type": "STRING"},
    },
    "required": ["category", "source", "environment"],
}

PHOTO_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "scene": {"type": "STRING"},
        "mood": {"type": "STRING"},
        "dominant_colors": {"type": "ARRAY", "items": {"type": "STRING"}},
        "objects": {"type": "ARRAY", "items": {"type": "STRING"}},
    },
    "required": ["scene", "mood", "dominant_colors", "objects"],
}


def _structured_caption(model: str, parts: list, schema: dict) -> dict:
    cfg = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=schema,
        temperature=0.2,
    )
    # Both gemini-3 captioners only live in the `global` location.
    resp = GLOBAL_CLIENT.models.generate_content(model=model, contents=parts, config=cfg)
    return json.loads(resp.text)


def caption_video(clip: Path, item: dict) -> dict:
    parts = [
        f"Asset theme: {item.get('sub_category','')}. "
        "Describe THIS clip — focus on what's visually happening, the camera, the mood.",
        types.Part.from_bytes(data=clip.read_bytes(), mime_type="video/mp4"),
    ]
    return _structured_caption(VIDEO_CAPTIONER, parts, VIDEO_SCHEMA)


def caption_music(clip: Path, item: dict) -> dict:
    parts = [
        f"Track theme: {item.get('sub_category','')}. "
        "Listen and describe genre, mood, instruments, tempo (BPM, integer), and energy.",
        types.Part.from_bytes(data=clip.read_bytes(), mime_type="audio/mpeg"),
    ]
    return _structured_caption(AUDIO_CAPTIONER, parts, MUSIC_SCHEMA)


def caption_sfx(clip: Path, item: dict) -> dict:
    parts = [
        f"Sound theme: {item.get('sub_category','')}. "
        "Classify this sound effect: category, sound source, environment.",
        types.Part.from_bytes(data=clip.read_bytes(), mime_type="audio/mpeg"),
    ]
    return _structured_caption(AUDIO_CAPTIONER, parts, SFX_SCHEMA)


def caption_photo(image: Path, item: dict) -> dict:
    mime = "image/png" if image.suffix.lower() == ".png" else "image/jpeg"
    parts = [
        f"Asset theme: {item.get('sub_category','')}. "
        "Describe scene, mood, dominant colors (hex preferred), salient objects.",
        types.Part.from_bytes(data=image.read_bytes(), mime_type=mime),
    ]
    return _structured_caption(PHOTO_CAPTIONER, parts, PHOTO_SCHEMA)


def caption_segment(kind: str, clip_or_image: Path, item: dict) -> dict:
    if kind == "video":
        return caption_video(clip_or_image, item)
    if kind == "music":
        return caption_music(clip_or_image, item)
    if kind == "sfx":
        return caption_sfx(clip_or_image, item)
    return caption_photo(clip_or_image, item)


# ---------------------------------------------------------------------------
# Embedding
# ---------------------------------------------------------------------------
def caption_to_text(kind: str, cap: dict, item: dict) -> str:
    if kind == "video":
        return (f"{cap.get('scene','')}. {cap.get('action','')}. "
                f"Mood: {cap.get('mood','')}. Camera: {cap.get('camera','')}. "
                f"Colors: {', '.join(cap.get('dominant_colors',[]))}. "
                f"Objects: {', '.join(cap.get('objects',[]))}. "
                f"Theme: {item.get('sub_category','')}.")
    if kind == "music":
        scenes = ", ".join(cap.get("scenes", []) or [])
        scenes_part = f" Fits scenes: {scenes}." if scenes else ""
        return (f"{cap.get('genre','')} track, {cap.get('mood','')} mood, "
                f"{cap.get('energy','')} energy, ~{int(cap.get('tempo_bpm') or 0)} BPM. "
                f"Instruments: {', '.join(cap.get('instruments',[]))}. "
                f"Theme: {item.get('sub_category','')}.{scenes_part}")
    if kind == "sfx":
        scenes = ", ".join(cap.get("scenes", []) or [])
        scenes_part = f" Fits scenes: {scenes}." if scenes else ""
        return (f"Sound effect — {cap.get('category','')} from {cap.get('source','')} "
                f"in {cap.get('environment','')}. Theme: {item.get('sub_category','')}.{scenes_part}")
    return (f"{cap.get('scene','')}. Mood: {cap.get('mood','')}. "
            f"Colors: {', '.join(cap.get('dominant_colors',[]))}. "
            f"Objects: {', '.join(cap.get('objects',[]))}. "
            f"Theme: {item.get('sub_category','')}.")


def embed_segment(clip: Path, thumb: Path, kind: str, cap: dict,
                  item: dict) -> np.ndarray:
    """True multimodal: audio bytes for music/sfx, video bytes for video,
    image bytes for photo/graphic. Caption text always concatenated."""
    text = caption_to_text(kind, cap, item)
    if kind in ("music", "sfx"):
        media = types.Part.from_bytes(
            data=clip.read_bytes(), mime_type="audio/mpeg")
    elif kind == "video":
        media = types.Part.from_bytes(
            data=clip.read_bytes(), mime_type="video/mp4")
    else:
        media = types.Part.from_bytes(
            data=thumb.read_bytes(), mime_type="image/webp")
    resp = CLIENT.models.embed_content(model=EMBED_MODEL, contents=[text, media])
    v = np.asarray(resp.embeddings[0].values, dtype=np.float32)
    return l2(v.reshape(1, -1))[0]


# ---------------------------------------------------------------------------
# Vector Search upsert
# ---------------------------------------------------------------------------
class VS:
    def __init__(self):
        from google.cloud import aiplatform
        from google.cloud.aiplatform_v1.types.index import IndexDatapoint
        aiplatform.init(project=PROJECT, location=LOCATION)
        self.IndexDatapoint = IndexDatapoint
        idx = aiplatform.MatchingEngineIndex.list(
            filter=f'display_name="{INDEX_DISPLAY_NAME}"')
        if not idx:
            raise RuntimeError(f"index '{INDEX_DISPLAY_NAME}' not found")
        self.index = idx[0]

    def upsert(self, dp_id: str, vec: np.ndarray, restricts: dict[str, str]) -> None:
        DP = self.IndexDatapoint
        rs = [DP.Restriction(namespace=k, allow_list=[v])
              for k, v in restricts.items() if v]
        self.index.upsert_datapoints(datapoints=[DP(
            datapoint_id=dp_id, feature_vector=vec.tolist(), restricts=rs,
        )])


# ---------------------------------------------------------------------------
# Per-segment processing
# ---------------------------------------------------------------------------
def process_asset(item: dict, gcs: GCS, fs, vs: VS, force: bool) -> int:
    """Returns # segments newly written for this asset."""
    cat = item["category"]
    asset_id = item["asset_id"]
    src = ROOT / item["local_path"]
    if not src.exists():
        log("skip", f"{asset_id}: missing local file")
        return 0

    duration = ffprobe_duration(src) if cat in ("video", "audio") else 0.0
    segs = plan_segments(item, duration)
    if not segs:
        return 0

    # Lazy upload of original (once per asset).
    ext = src.suffix
    original_gcs = f"originals/{asset_id}{ext}"
    gcs.upload(src, original_gcs)

    out_dir = ROOT / "segments_cache" / asset_id
    out_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    for seg in segs:
        dp_id = datapoint_id(asset_id, seg)
        doc_ref = fs.collection(FIRESTORE_COLLECTION).document(dp_id)
        if not force and doc_ref.get().exists:
            continue

        # 1. Cut clip + thumbnail
        if seg["kind"] == "video":
            clip, thumb = extract_video_segment(src, seg["start"], seg["end"],
                                                out_dir, dp_id)
            clip_mime = "video/mp4"
        elif seg["kind"] in ("music", "sfx"):
            clip, thumb = extract_audio_segment(src, seg["start"], seg["end"],
                                                out_dir, dp_id)
            clip_mime = "audio/mpeg"
        else:  # image
            clip, thumb = use_image_as_segment(src, out_dir, dp_id)
            clip_mime = "image/jpeg" if src.suffix.lower() in (".jpg", ".jpeg") else "image/png"

        # 2. Upload artifacts to GCS
        thumb_gcs = f"thumbnails/{asset_id}/{dp_id}.webp"
        clip_gcs = (f"segments/{asset_id}/{dp_id}{clip.suffix}"
                    if seg["kind"] != "image" else original_gcs)
        gcs.upload(thumb, thumb_gcs, "image/webp")
        if seg["kind"] != "image":
            gcs.upload(clip, clip_gcs, clip_mime)

        # 3. Caption
        try:
            cap = caption_segment(seg["kind"], clip, item)
        except Exception as exc:
            log("caption", f"{dp_id}: {exc}; falling back to manifest caption")
            cap = {"fallback_caption": item.get("caption", ""),
                   "tags": item.get("tags", [])}

        # 4. Embed
        try:
            vec = embed_segment(clip, thumb, seg["kind"], cap, item)
        except Exception as exc:
            log("embed", f"FAIL {dp_id}: {exc}")
            continue

        # 5. Restricts
        bpm = cap.get("tempo_bpm") if seg["kind"] == "music" else None
        restricts = {
            "modality": cat if seg["kind"] != "sfx" else "sfx",
            "length_bucket": length_bucket(seg["end"] - seg["start"])
                              if seg["kind"] in ("video", "music", "sfx") else "image",
            "tempo_bucket": tempo_bucket(bpm) or "",
            "kind": seg["kind"],
        }

        # 6. Firestore doc
        doc_ref.set({
            "datapoint_id": dp_id,
            "asset_id": asset_id,
            "modality": cat,
            "kind": seg["kind"],
            "sub_category": item.get("sub_category", ""),
            "start_s": seg["start"],
            "end_s": seg["end"],
            "duration_s": float(seg["end"] - seg["start"]),
            "caption": cap,
            "caption_text": caption_to_text(seg["kind"], cap, item),
            "thumbnail_gcs": f"gs://{GCS_BUCKET}/{thumb_gcs}",
            "clip_gcs": f"gs://{GCS_BUCKET}/{clip_gcs}",
            "original_gcs": f"gs://{GCS_BUCKET}/{original_gcs}",
            "contributor": item.get("contributor", ""),
            "license": item.get("license", ""),
            "restricts": restricts,
            "embed_dim": int(vec.shape[0]),
            "ingest_ts": time.time(),
        })

        # 7. VS upsert
        vs.upsert(dp_id, vec, restricts)

        written += 1
        log("seg", f"✓ {dp_id}  ({seg['kind']}, {restricts.get('length_bucket','')})")

    return written


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--asset-id", help="process exactly one asset")
    ap.add_argument("--modality", choices=["photo", "video", "audio", "graphic"])
    ap.add_argument("--limit", type=int, default=0,
                    help="process at most N assets (after filtering)")
    ap.add_argument("--workers", type=int, default=4,
                    help="parallelism per asset (segments processed serially per asset)")
    ap.add_argument("--force", action="store_true",
                    help="re-process even if Firestore doc exists")
    args = ap.parse_args()

    if not MANIFEST_PATH.exists():
        log("env", f"missing {MANIFEST_PATH} — run pipeline.py first to harvest")
        sys.exit(1)

    items = json.loads(MANIFEST_PATH.read_text())
    if args.asset_id:
        items = [i for i in items if i["asset_id"] == args.asset_id]
    if args.modality:
        items = [i for i in items if i["category"] == args.modality]
    if args.limit:
        items = items[:args.limit]

    log("plan", f"{len(items)} assets to process")

    from google.cloud import firestore
    fs = firestore.Client(project=PROJECT)
    gcs = GCS()
    vs = VS()

    t0 = time.perf_counter()
    total = 0
    if args.workers <= 1 or len(items) <= 1:
        for it in items:
            try:
                total += process_asset(it, gcs, fs, vs, args.force)
            except Exception as exc:
                log("asset", f"FAIL {it['asset_id']}: {exc}")
    else:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futs = {pool.submit(process_asset, it, gcs, fs, vs, args.force): it
                    for it in items}
            for fut in as_completed(futs):
                it = futs[fut]
                try:
                    total += fut.result()
                except Exception as exc:
                    log("asset", f"FAIL {it['asset_id']}: {exc}")

    log("done", f"{total} new segments in {time.perf_counter()-t0:.1f}s")


if __name__ == "__main__":
    main()
