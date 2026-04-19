"""Enrich every audio (music + sfx) segment with scene/setting tags.

Why: the original audio captions are pure musicology (genre / BPM /
instruments) with no scene anchor — so a query like "tropical beach getaway"
falls back on the affect axis and pulls in synthwave next to the relaxed
acoustic folk that *should* have won. After this script, each audio caption
text grows a "Fits scenes: tropical beach, sunset poolside, ..." tail and
the segment is re-embedded multimodally so the Vector Search index reflects
the new text.

Models (per the user's standing rule — Gemini 3 + global region):
  - gemini-3-flash-lite-preview  (global)  → scene tagging
  - gemini-embedding-2-preview              → re-embed (audio bytes + text)

Usage
-----
    python pipeline/enrich_audio_captions.py             # all music + sfx
    python pipeline/enrich_audio_captions.py --kind music
    python pipeline/enrich_audio_captions.py --limit 20  # smoke-test a few
    python pipeline/enrich_audio_captions.py --workers 6
    python pipeline/enrich_audio_captions.py --dry-run   # don't write back
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from pipeline_v2 import (  # noqa: E402
    CLIENT,
    EMBED_MODEL,
    GLOBAL_CLIENT,
    VS,
    caption_to_text,
    l2,
    log,
)
from google.genai import types  # noqa: E402

SCENE_MODEL = "gemini-3.1-flash-lite-preview"  # global region, fast + cheap
SEGMENTS_DIR = ROOT / "segments_cache"

SCENE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "scenes": {
            "type": "ARRAY",
            "items": {"type": "STRING"},
            "minItems": 6,
            "maxItems": 10,
        }
    },
    "required": ["scenes"],
}

MUSIC_PROMPT = (
    "You are tagging a music clip for a stock-media search engine. "
    "Given the existing musicology metadata AND a short audio sample, return "
    "6-10 short concrete SCENE / SETTING / VIBE tags this music best fits. "
    "Examples of good tags: 'tropical beach', 'sunset poolside', 'morning "
    "coffee shop', 'late-night drive', 'corporate explainer', 'wedding first "
    "dance', 'epic battle trailer', 'study lo-fi', 'rainy window'. "
    "Bad tags: genre names, instruments, BPM. Tags must be 1-4 words each, "
    "lowercase, no punctuation. Return strict JSON: {\"scenes\": [..]}."
)

SFX_PROMPT = (
    "You are tagging a sound-effect clip for a stock-media search engine. "
    "Given the existing classification AND a short audio sample, return 6-10 "
    "short concrete SCENE / USE-CASE tags where this SFX would fit. "
    "Examples: 'thriller chase scene', 'kitchen cooking video', 'tech product "
    "reveal', 'horror jump scare', 'cozy fireplace ambience', 'car commercial'. "
    "Bad tags: just repeating the source noun. Tags 1-4 words each, lowercase, "
    "no punctuation. Return strict JSON: {\"scenes\": [..]}."
)


def find_local_clip(asset_id: str, datapoint_id: str) -> Path | None:
    """The pipeline writes mp3 segments to segments_cache/<asset_id>/<dp>.mp3.
    Some bbc-sfx assets may not have the segment cached after a clean rebuild
    — return None and the caller will skip them (they keep their old caption)."""
    p = SEGMENTS_DIR / asset_id / f"{datapoint_id}.mp3"
    return p if p.exists() else None


def get_scenes(clip: Path, kind: str, existing_caption: dict, sub_category: str) -> list[str]:
    summary = (
        f"Existing caption JSON: {json.dumps(existing_caption, ensure_ascii=False)}\n"
        f"Asset theme/sub_category: {sub_category}"
    )
    parts = [
        MUSIC_PROMPT if kind == "music" else SFX_PROMPT,
        summary,
        types.Part.from_bytes(data=clip.read_bytes(), mime_type="audio/mpeg"),
    ]
    cfg = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=SCENE_SCHEMA,
        temperature=0.4,
    )
    resp = GLOBAL_CLIENT.models.generate_content(
        model=SCENE_MODEL, contents=parts, config=cfg)
    data = json.loads(resp.text)
    scenes = data.get("scenes") or []
    return [s.strip().lower() for s in scenes if s and s.strip()][:10]


def reembed(clip: Path, caption_text: str) -> np.ndarray:
    media = types.Part.from_bytes(data=clip.read_bytes(), mime_type="audio/mpeg")
    resp = CLIENT.models.embed_content(
        model=EMBED_MODEL, contents=[caption_text, media])
    v = np.asarray(resp.embeddings[0].values, dtype=np.float32)
    return l2(v.reshape(1, -1))[0]


def process_one(doc_dict: dict, fs, vs: VS, dry_run: bool) -> tuple[str, str]:
    """Return (datapoint_id, status). Status: 'ok' | 'skip:<reason>' | 'fail:<reason>'."""
    dp_id = doc_dict["datapoint_id"]
    asset_id = doc_dict["asset_id"]
    kind = doc_dict.get("kind") or "music"
    cap = dict(doc_dict.get("caption") or {})
    sub = doc_dict.get("sub_category", "")

    # Idempotent: skip if already has non-empty scenes.
    if cap.get("scenes"):
        return dp_id, "skip:already-enriched"

    clip = find_local_clip(asset_id, dp_id)
    if clip is None:
        return dp_id, "skip:no-local-clip"

    try:
        scenes = get_scenes(clip, kind, cap, sub)
    except Exception as exc:
        return dp_id, f"fail:scene:{exc}"

    if not scenes:
        return dp_id, "skip:empty-scenes"

    cap["scenes"] = scenes
    new_text = caption_to_text(kind, cap, {"sub_category": sub})

    try:
        vec = reembed(clip, new_text)
    except Exception as exc:
        return dp_id, f"fail:embed:{exc}"

    if dry_run:
        return dp_id, f"dry:{','.join(scenes[:4])}..."

    # Update Firestore.
    fs.collection("segments").document(dp_id).update({
        "caption": cap,
        "caption_text": new_text,
        "scenes_enriched_ts": time.time(),
    })

    # Re-upsert into Vector Search (same dp_id overwrites).
    restricts = doc_dict.get("restricts") or {
        "modality": "audio",
        "kind": kind,
    }
    vs.upsert(dp_id, vec, restricts)

    return dp_id, f"ok:{','.join(scenes[:3])}"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--kind", choices=["music", "sfx", "all"], default="all")
    ap.add_argument("--limit", type=int, default=0,
                    help="cap total processed (0 = no cap)")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    from google.cloud import firestore
    fs = firestore.Client(project=os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos"))

    log("load", "querying Firestore for audio segments...")
    q = fs.collection("segments").where(filter=firestore.FieldFilter("modality", "==", "audio"))
    docs = [d.to_dict() for d in q.stream()]
    if args.kind != "all":
        docs = [d for d in docs if (d.get("kind") or "music") == args.kind]
    if args.limit:
        docs = docs[: args.limit]
    log("load", f"{len(docs)} candidate segments to enrich")

    vs = VS() if not args.dry_run else None

    counters = {"ok": 0, "skip": 0, "fail": 0, "dry": 0}
    start = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futs = {pool.submit(process_one, d, fs, vs, args.dry_run): d for d in docs}
        for i, fut in enumerate(as_completed(futs), 1):
            try:
                dp, status = fut.result()
            except Exception as exc:
                dp, status = "?", f"fail:fut:{exc}"
            bucket = status.split(":", 1)[0]
            counters[bucket] = counters.get(bucket, 0) + 1
            if args.dry_run or i % 25 == 0 or status.startswith("fail"):
                log("enrich",
                    f"[{i}/{len(docs)}] {dp[-50:]:>50} → {status[:120]}")

    elapsed = time.time() - start
    log("done",
        f"ok={counters['ok']} skip={counters['skip']} fail={counters['fail']} "
        f"dry={counters['dry']}  in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
