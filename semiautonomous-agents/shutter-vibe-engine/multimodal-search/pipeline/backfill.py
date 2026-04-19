"""Targeted corpus backfill for the EBC demo.

Adds NEW themes per modality that align with the 50-question demo doc.
Reuses pipeline.py's fetchers + downloaders; only writes new rows to
manifest.json (idempotent — never re-fetches an asset_id we already have).

Run AFTER setting PEXELS_API_KEY / PIXABAY_API_KEY.

    python pipeline/backfill.py                  # all modalities
    python pipeline/backfill.py --mod photo      # one modality
    python pipeline/backfill.py --per-query 6    # tune fetch depth

Then push the new assets through pipeline_v2.py:

    python pipeline/build.py --modality photo --workers 6
    python pipeline/build.py --modality video --workers 4
    python pipeline/build.py --modality graphic --workers 6
    python pipeline/build.py --modality audio --workers 4
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from pipeline import (  # noqa: E402
    MANIFEST_PATH,
    download_asset,
    fetch_internet_archive_audio,
    fetch_pexels_photos,
    fetch_pexels_videos,
    fetch_pixabay_graphics,
    log,
    save_manifest,
)

# ---------------------------------------------------------------------------
# Curated NEW themes — picked to (a) close the modality balance gap and
# (b) prove fine-grained semantic recall in the 50-question demo.
# Each theme = a Pexels/Pixabay/IA search query. Some themes are intentionally
# "weird-specific" (e.g. tiny ant on leaf) to showcase the model's ability to
# pick up subtle visual cues.
# ---------------------------------------------------------------------------
PHOTO_THEMES = [
    # Fine-grained / subtle subjects
    "ant crawling on leaf macro",
    "ladybug on green leaf",
    "single dewdrop on spider web",
    "tiny mushroom forest floor",
    "honeybee pollen flower closeup",
    # Mood + atmosphere
    "empty park bench autumn fog",
    "lonely lighthouse stormy sea",
    "abandoned house overgrown",
    "rainy window cafe interior bokeh",
    "candlelit dinner romantic",
    # Compositional / relational
    "elderly hands holding warm cup",
    "child sharing umbrella with grandmother",
    "father teaching son to ride bike",
    "two friends laughing rooftop sunset",
    "hands passing letter envelope",
    # Style / cultural
    "holi festival color powder india",
    "japanese cherry blossom temple",
    "moroccan market spice stall",
    "venice gondola canal sunrise",
    "scandinavian sauna lakeside",
    # Color + lighting cues
    "monochrome black and white street photography",
    "blue hour city skyline reflection",
    "golden hour wheat field",
    "neon pink purple cyberpunk alley",
    "frost on window crystals macro",
    # Texture
    "rough peeling paint barn door",
    "cracked desert mud pattern",
    "weathered rusted metal texture",
    "knitted wool sweater closeup",
    # Specific objects / icons
    "vintage volkswagen beetle beach",
    "old typewriter desk sunlight",
    "vinyl record player turntable",
    "polaroid photos hanging string lights",
    "single red leaf on snow",
]

VIDEO_THEMES = [
    # Process / craft
    "hands kneading bread dough closeup",
    "sushi chef preparing nigiri",
    "glassblower shaping molten glass",
    "potter throwing clay wheel",
    "barista pouring latte art slow motion",
    "calligraphy brush ink writing",
    # Action / sport
    "kayaker paddling whitewater rapids",
    "skateboarder kickflip slow motion",
    "rock climber chalk hands",
    "surfer riding wave aerial drone",
    "marathon runners feet pavement",
    # Emotion / human
    "mother holding newborn baby",
    "elderly couple walking hand in hand park",
    "dog tail wagging happy",
    "stadium crowd cheering wave",
    # Tiny detail
    "ant carrying leaf macro",
    "spider weaving web macro",
    "butterfly emerging chrysalis time lapse",
    "flower blooming time lapse",
    "ice melting time lapse",
    # Workflow / template
    "abstract particle reveal background loop",
    "modern logo intro minimal animation",
    "gradient liquid loop seamless",
    "glitch transition vfx loop",
]

GRAPHIC_THEMES = [
    # Style packs
    "art deco gold geometric poster",
    "bauhaus primary colors poster",
    "mid century modern abstract",
    "japanese woodblock ukiyo-e",
    "russian constructivism poster",
    "memphis design pattern 80s",
    # Subject + style combo
    "sci-fi spaceship illustration retro",
    "fantasy castle illustration watercolor",
    "cute kawaii cat sticker",
    "skateboard deck graphic illustration",
    "tarot card mystical illustration",
    "botanical watercolor leaves wreath",
    # Templates / utility
    "instagram reel cover template gradient",
    "linkedin banner minimalist",
    "podcast cover art illustration",
    "youtube thumbnail bold typography",
    "resume cv template minimalist",
    "pitch deck cover slide",
    # Decorative / pattern
    "mandala intricate symmetric pattern",
    "stained glass cathedral window",
    "holographic gradient iridescent",
    "tropical leaves seamless pattern",
    "art nouveau ornamental frame",
    # Iconography
    "minimalist line icon set tech",
    "weather icon set rounded",
    "food icon set hand drawn",
]

# Music — already over-target (635). We INTENTIONALLY skip more music.
MUSIC_THEMES: list[str] = []

# SFX — single most under-served bucket. Use sub_category names that match
# pipeline_v2's SFX_KEYWORDS regex so they get treated as 8-second SFX clips.
SFX_THEMES = [
    "glass shatter sound effect",
    "wooden door slam sound effect",
    "typewriter keys click sound effect",
    "footsteps on snow sound effect",
    "footsteps on gravel sound effect",
    "horse galloping hooves sound effect",
    "whoosh swoosh transition sound effect",
    "deep boom impact sound effect",
    "water dripping cave sound effect",
    "fire crackling fireplace sound effect",
    "thunder rolling distant sound effect",
    "heavy rain on roof sound effect",
    "tropical jungle birds ambience",
    "city traffic ambience sound effect",
    "ocean waves crashing sound effect",
    "vintage radio static crackle sound effect",
    "crowd applause cheer sound effect",
    "cinematic riser whoosh sound effect",
    "subway train arriving sound effect",
    "coffee shop ambience chatter sound effect",
]


# ---------------------------------------------------------------------------
def load_manifest_ids() -> tuple[list[dict], set[str]]:
    if MANIFEST_PATH.exists():
        items = json.loads(MANIFEST_PATH.read_text())
        return items, {it["asset_id"] for it in items}
    return [], set()


def harvest_one(mod: str, query: str, per_query: int) -> list[dict]:
    if mod == "photo":
        return fetch_pexels_photos(query, per_query)
    if mod == "video":
        return fetch_pexels_videos(query, per_query)
    if mod == "graphic":
        half = max(2, per_query // 2)
        return (fetch_pixabay_graphics(query, half, "illustration")
                + fetch_pixabay_graphics(query, half, "vector"))
    if mod in ("music", "sfx"):
        return fetch_internet_archive_audio(query, per_query)
    return []


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mod", choices=["photo", "video", "graphic", "sfx", "music", "all"],
                    default="all")
    ap.add_argument("--per-query", type=int, default=6,
                    help="how many candidates to fetch per query")
    ap.add_argument("--max-new", type=int, default=0,
                    help="hard cap on new items added (0=unlimited)")
    ap.add_argument("--no-download", action="store_true",
                    help="harvest only; skip downloads (for dry-run)")
    args = ap.parse_args()

    plan = []
    if args.mod in ("all", "photo"):
        plan += [("photo", q) for q in PHOTO_THEMES]
    if args.mod in ("all", "video"):
        plan += [("video", q) for q in VIDEO_THEMES]
    if args.mod in ("all", "graphic"):
        plan += [("graphic", q) for q in GRAPHIC_THEMES]
    if args.mod in ("all", "sfx"):
        plan += [("sfx", q) for q in SFX_THEMES]
    if args.mod in ("all", "music"):
        plan += [("music", q) for q in MUSIC_THEMES]

    log("plan", f"{len(plan)} (modality, query) pairs to fetch")

    items, seen = load_manifest_ids()
    new_items: list[dict] = []

    for mod, q in plan:
        if args.max_new and len(new_items) >= args.max_new:
            log("cap", f"hit max-new={args.max_new}, stopping fetch")
            break
        try:
            fetched = harvest_one(mod, q, args.per_query)
        except Exception as exc:
            log("fetch", f"{mod}/{q!r}: {exc}")
            continue

        added = 0
        for it in fetched:
            if it["asset_id"] in seen:
                continue
            # Force the manifest's category to "audio" for both music+sfx; the
            # SFX flag comes from sub_category being one of pipeline_v2's
            # SFX_KEYWORDS — which our SFX_THEMES already include.
            if mod in ("music", "sfx"):
                it["category"] = "audio"
                if mod == "sfx":
                    # Make sure sub_category contains a recognised SFX keyword.
                    it["sub_category"] = q
            seen.add(it["asset_id"])
            new_items.append(it)
            added += 1
            if args.max_new and len(new_items) >= args.max_new:
                break
        log("fetch", f"{mod:>7}/{q[:42]:<42} +{added}  (running new total: {len(new_items)})")

    if not new_items:
        log("done", "no new items to add — manifest unchanged")
        return

    log("download", f"{len(new_items)} new items to download")
    if args.no_download:
        log("dry", "skip download (--no-download)")
        return

    # Parallel download — drop on failure.
    with ThreadPoolExecutor(max_workers=8) as pool:
        futs = {pool.submit(download_asset, it): it for it in new_items}
        ok_items = []
        for fut in as_completed(futs):
            it = futs[fut]
            try:
                if fut.result():
                    ok_items.append(it)
            except Exception as exc:
                log("download", f"{it['asset_id']}: {exc}")
    log("download", f"{len(ok_items)}/{len(new_items)} downloaded ok")

    # Append to manifest + save.
    items.extend(ok_items)
    save_manifest(items)
    log("manifest", f"appended {len(ok_items)} items, total now {len(items)}")
    log("done", f"now run pipeline_v2.py per-modality to segment + index")


if __name__ == "__main__":
    main()
