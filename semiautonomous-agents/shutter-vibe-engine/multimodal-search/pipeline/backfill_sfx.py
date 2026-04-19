"""SFX-only backfill from BBC Sound Effects (RemArc).

The Internet Archive corpus we used originally is music-biased, so the
`audio_sfx` bucket plateaued at ~28 segments. The BBC Rewind sound-effects
archive (https://sound-effects.bbcrewind.co.uk) exposes a public Elasticsearch
endpoint and serves MP3 originals from a CDN — perfect for a fast top-up.

Licence: BBC Sound Effects content is released under the **RemArc** licence,
which permits free use for personal, educational, and research purposes.
That covers our internal demo. Every row stamps `license = "BBC Sound Effects
(RemArc)"` so it is traceable in the manifest.

Usage:

    python pipeline/backfill_sfx.py                  # default themes, 6 hits each
    python pipeline/backfill_sfx.py --per-query 8    # tune fetch depth
    python pipeline/backfill_sfx.py --max-new 60     # hard cap
    python pipeline/backfill_sfx.py --no-download    # dry-run

After this writes new rows, re-run pipeline_v2.py to segment + index:

    python pipeline/build.py --modality audio --workers 4
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from pipeline import (  # noqa: E402
    ASSETS_DIR,
    MANIFEST_PATH,
    log,
    save_manifest,
    slug,
)

BBC_SEARCH_URL = "https://sound-effects-api.bbcrewind.co.uk/api/sfx/search"
BBC_MEDIA_URL = "https://sound-effects-media.bbcrewind.co.uk/mp3/{id}.mp3"

# Themed queries — picked to spread coverage across cinematic SFX, foley,
# ambience, and transitions. Every theme yields a sub_category that contains
# the literal phrase "sound effect" so pipeline_v2.is_sfx() classifies the
# resulting segments as SFX (the keyword + <30s duration gates both fire).
SFX_QUERIES: list[tuple[str, str]] = [
    # (search query, sub_category label — must contain "sound effect")
    ("glass shatter",                "glass shatter sound effect"),
    ("wooden door slam",             "wooden door slam sound effect"),
    ("typewriter clicking",          "typewriter keys click sound effect"),
    ("footsteps gravel",             "footsteps on gravel sound effect"),
    ("footsteps snow",               "footsteps on snow sound effect"),
    ("horse galloping",              "horse galloping sound effect"),
    ("whoosh",                       "cinematic whoosh sound effect"),
    ("deep boom",                    "deep boom impact sound effect"),
    ("water drip cave",              "water drip cave sound effect"),
    ("fire crackling",               "fire crackling sound effect"),
    ("rain on roof",                 "rain on roof sound effect"),
    ("thunder rolling",              "thunder rolling sound effect"),
    ("coffee shop chatter",          "coffee shop chatter sound effect"),
    ("radio static",                 "vintage radio static sound effect"),
    ("crowd applause",               "crowd applause sound effect"),
    ("subway train arriving",        "subway train arriving sound effect"),
    ("riser sweep",                  "cinematic riser sweep sound effect"),
]

# Reject clips longer than this (seconds). pipeline_v2 will trim to 8 s but
# we want clean SFX, not 5-minute ambiences.
MAX_DURATION_S = 25.0
# Reject clips shorter than this (seconds) — sub-half-second blips are noise.
MIN_DURATION_S = 0.4


def load_manifest_ids() -> tuple[list[dict], set[str]]:
    if MANIFEST_PATH.exists():
        items = json.loads(MANIFEST_PATH.read_text())
        return items, {it["asset_id"] for it in items}
    return [], set()


def fetch_bbc_sfx(query: str, n: int) -> list[dict]:
    """Search the BBC Rewind sound-effects API and return raw hits.

    Over-fetches by 4x because many hits are too long for SFX use; we filter
    client-side on duration.
    """
    payload = {
        "criteria": {
            "from": 0,
            "size": max(n * 4, 12),
            "query": query,
            "persistentlyExcludedAssetIds": [],
        }
    }
    r = requests.post(BBC_SEARCH_URL, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    hits = []
    for h in data.get("results", []):
        # BBC reports `duration` in milliseconds.
        dur_ms = h.get("duration") or 0
        dur_s = dur_ms / 1000.0
        if dur_s < MIN_DURATION_S or dur_s > MAX_DURATION_S:
            continue
        hits.append({
            "id": h["id"],
            "duration_s": round(dur_s, 3),
            "description": (h.get("description") or "").strip(),
            "tags": [str(t).lower() for t in (h.get("tags") or [])],
            "categories": [c.get("className", "") for c in (h.get("categories") or [])],
            "location": (h.get("location") or {}).get("continent", ""),
            "source": h.get("source", ""),
            "recordedDate": h.get("recordedDate", ""),
        })
        if len(hits) >= n:
            break
    return hits


def to_manifest_row(hit: dict, query: str, sub_category: str) -> dict:
    """Convert a BBC search hit into a pipeline.py-compatible manifest row."""
    desc = hit["description"] or query
    cats = ", ".join(c for c in hit["categories"] if c)
    tag_str = ", ".join(hit["tags"][:8]) if hit["tags"] else query
    caption = (
        f"{desc} BBC Sound Effects archive — {hit['duration_s']:.1f}s clip. "
        f"Categories: {cats or 'sound effect'}. "
        f"Tags: {tag_str}. Theme: {query}."
    )
    return {
        "asset_id": f"bbc-sfx-{slug(hit['id'])}",
        "category": "audio",
        "sub_category": sub_category,
        "caption": caption,
        "tags": (hit["tags"][:8] if hit["tags"]
                 else [t for t in query.split() if t]),
        "contributor": "BBC",
        "license": "BBC Sound Effects (RemArc)",
        "source_url": BBC_MEDIA_URL.format(id=hit["id"]),
        "video_url": "",
        "preview_url": "",
        "title": desc[:120] or hit["id"],
        "duration_s": hit["duration_s"],
    }


def download_one(item: dict) -> bool:
    """Stream the MP3 to assets/audio/<asset_id>.mp3. Idempotent."""
    out_dir = ASSETS_DIR / "audio"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{item['asset_id']}.mp3"
    if path.exists() and path.stat().st_size > 1024:
        item["local_path"] = str(path.relative_to(ROOT))
        item["thumb_path"] = ""
        return True
    try:
        with requests.get(item["source_url"], timeout=120, stream=True) as r:
            r.raise_for_status()
            with open(path, "wb") as fh:
                for chunk in r.iter_content(1 << 15):
                    fh.write(chunk)
    except Exception as exc:
        log("download", f"FAIL {item['asset_id']}: {exc}")
        if path.exists():
            try:
                path.unlink()
            except OSError:
                pass
        return False
    item["local_path"] = str(path.relative_to(ROOT))
    item["thumb_path"] = ""
    return True


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--per-query", type=int, default=6,
                    help="how many candidate clips per theme (default 6)")
    ap.add_argument("--max-new", type=int, default=0,
                    help="hard cap on new items added (0=unlimited)")
    ap.add_argument("--no-download", action="store_true",
                    help="harvest only; skip downloads (dry-run)")
    args = ap.parse_args()

    items, seen = load_manifest_ids()
    log("plan", f"{len(SFX_QUERIES)} themes; manifest currently has "
                f"{len(items)} items, {sum(1 for i in items if i.get('asset_id','').startswith('bbc-sfx-'))} from BBC")

    new_items: list[dict] = []
    for query, sub_category in SFX_QUERIES:
        if args.max_new and len(new_items) >= args.max_new:
            log("cap", f"hit max-new={args.max_new}, stopping fetch")
            break
        try:
            hits = fetch_bbc_sfx(query, args.per_query)
        except Exception as exc:
            log("fetch", f"sfx/{query!r}: {exc}")
            continue

        added = 0
        for h in hits:
            row = to_manifest_row(h, query, sub_category)
            if row["asset_id"] in seen:
                continue
            seen.add(row["asset_id"])
            new_items.append(row)
            added += 1
            if args.max_new and len(new_items) >= args.max_new:
                break
        log("fetch", f"sfx/{query[:30]:<30} +{added}  (running total: {len(new_items)})")
        # Be polite to the BBC endpoint.
        time.sleep(0.25)

    if not new_items:
        log("done", "no new items to add — manifest unchanged")
        return

    if args.no_download:
        log("dry", f"--no-download — would add {len(new_items)} items")
        return

    log("download", f"{len(new_items)} clips to download from BBC CDN")
    ok_items: list[dict] = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futs = {pool.submit(download_one, it): it for it in new_items}
        for fut in as_completed(futs):
            it = futs[fut]
            try:
                if fut.result():
                    ok_items.append(it)
            except Exception as exc:
                log("download", f"{it['asset_id']}: {exc}")
    log("download", f"{len(ok_items)}/{len(new_items)} downloaded ok")

    items.extend(ok_items)
    save_manifest(items)
    log("manifest", f"appended {len(ok_items)} items, total now {len(items)}")
    log("done", "now run: python pipeline/build.py --modality audio --workers 4")


if __name__ == "__main__":
    main()
