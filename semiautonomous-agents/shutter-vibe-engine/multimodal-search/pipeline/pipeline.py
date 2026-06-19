"""Asset-harvesting helpers shared by `backfill.py` and `backfill_sfx.py`.

Each `fetch_*` function returns a list of *manifest rows* that downstream
code (`download_asset` then `build.process_asset`) consumes. A manifest row
is a plain dict with at minimum:

    asset_id       unique id
    category       photo | video | audio | graphic
    sub_category   short theme label
    caption        free-text description (used to seed embedding text)
    tags           list[str]
    contributor    str
    license        str
    source_url     where to download the actual file
    preview_url    (optional) thumbnail url
    title          str
    duration_s     float (videos / audio only)

`download_asset` writes the file under `ASSETS_DIR/<category>/<asset_id>.<ext>`
and sets `item["local_path"]` (relative to the `multimodal-search/` root, the
same path `build.process_asset` expects).

Requires env vars:
    PEXELS_API_KEY    — https://www.pexels.com/api/
    PIXABAY_API_KEY   — https://pixabay.com/api/docs/
The Internet Archive endpoint is keyless.
"""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Iterable

import requests

ROOT = Path(__file__).resolve().parent.parent  # = multimodal-search/
ASSETS_DIR = ROOT / "assets"
MANIFEST_PATH = ASSETS_DIR / "manifest.json"

PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
PIXABAY_KEY = os.environ.get("PIXABAY_API_KEY", "")

PEXELS_PHOTO_URL = "https://api.pexels.com/v1/search"
PEXELS_VIDEO_URL = "https://api.pexels.com/videos/search"
PIXABAY_URL = "https://pixabay.com/api/"
IA_SEARCH_URL = "https://archive.org/advancedsearch.php"
IA_FILES_URL = "https://archive.org/metadata/{identifier}"
IA_DOWNLOAD_URL = "https://archive.org/download/{identifier}/{filename}"

# ---------------------------------------------------------------------------
# Small utilities
# ---------------------------------------------------------------------------
def log(stage: str, msg: str) -> None:
    print(f"[{stage:>9}] {msg}", flush=True)


def slug(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", str(s)).strip("-").lower()
    return s or "x"


def save_manifest(items: list[dict]) -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(items, indent=2, ensure_ascii=False))


def _ext_from_url(url: str, fallback: str) -> str:
    suffix = Path(url.split("?")[0]).suffix.lower()
    return suffix if suffix and len(suffix) <= 5 else fallback


def _download_to(url: str, dest: Path, timeout: int = 120) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        with requests.get(url, stream=True, timeout=timeout) as r:
            r.raise_for_status()
            with open(dest, "wb") as fh:
                for chunk in r.iter_content(1 << 15):
                    fh.write(chunk)
        return dest.exists() and dest.stat().st_size > 0
    except Exception as exc:
        log("download", f"FAIL {url}: {exc}")
        if dest.exists():
            try:
                dest.unlink()
            except OSError:
                pass
        return False


# ---------------------------------------------------------------------------
# Pexels — photos
# ---------------------------------------------------------------------------
def fetch_pexels_photos(query: str, n: int) -> list[dict]:
    if not PEXELS_KEY:
        log("pexels", "PEXELS_API_KEY not set — returning []")
        return []
    headers = {"Authorization": PEXELS_KEY}
    params = {"query": query, "per_page": max(n, 1), "orientation": "landscape"}
    r = requests.get(PEXELS_PHOTO_URL, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    out: list[dict] = []
    for p in r.json().get("photos", [])[:n]:
        src = p.get("src", {})
        out.append({
            "asset_id": f"pexels-photo-{p['id']}",
            "category": "photo",
            "sub_category": query,
            "caption": (p.get("alt") or query).strip(),
            "tags": [t for t in query.split() if t],
            "contributor": p.get("photographer", ""),
            "license": "Pexels License",
            "source_url": src.get("original") or src.get("large2x") or src.get("large"),
            "preview_url": src.get("medium", ""),
            "title": (p.get("alt") or query)[:120],
        })
    return out


# ---------------------------------------------------------------------------
# Pexels — videos
# ---------------------------------------------------------------------------
def fetch_pexels_videos(query: str, n: int) -> list[dict]:
    if not PEXELS_KEY:
        log("pexels", "PEXELS_API_KEY not set — returning []")
        return []
    headers = {"Authorization": PEXELS_KEY}
    params = {"query": query, "per_page": max(n, 1), "orientation": "landscape"}
    r = requests.get(PEXELS_VIDEO_URL, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    out: list[dict] = []
    for v in r.json().get("videos", [])[:n]:
        # Prefer an HD .mp4 if available; otherwise the highest-quality variant.
        files = sorted(
            (f for f in v.get("video_files", []) if f.get("link")),
            key=lambda f: (f.get("width") or 0) * (f.get("height") or 0),
            reverse=True,
        )
        if not files:
            continue
        best = next((f for f in files if (f.get("file_type") or "").endswith("mp4")), files[0])
        pics = v.get("video_pictures") or []
        out.append({
            "asset_id": f"pexels-video-{v['id']}",
            "category": "video",
            "sub_category": query,
            "caption": query,  # Pexels videos lack alt text
            "tags": [t for t in query.split() if t],
            "contributor": (v.get("user") or {}).get("name", ""),
            "license": "Pexels License",
            "source_url": best["link"],
            "preview_url": pics[0]["picture"] if pics else "",
            "title": query[:120],
            "duration_s": float(v.get("duration", 0)),
        })
    return out


# ---------------------------------------------------------------------------
# Pixabay — graphics (illustrations + vectors)
# ---------------------------------------------------------------------------
def fetch_pixabay_graphics(query: str, n: int, image_type: str = "illustration") -> list[dict]:
    if not PIXABAY_KEY:
        log("pixabay", "PIXABAY_API_KEY not set — returning []")
        return []
    params = {
        "key": PIXABAY_KEY,
        "q": query,
        "image_type": image_type,  # "illustration" or "vector"
        "per_page": max(n, 3),
        "safesearch": "true",
    }
    r = requests.get(PIXABAY_URL, params=params, timeout=30)
    r.raise_for_status()
    out: list[dict] = []
    for h in r.json().get("hits", [])[:n]:
        url = h.get("largeImageURL") or h.get("webformatURL")
        if not url:
            continue
        tags = [t.strip() for t in (h.get("tags") or "").split(",") if t.strip()]
        out.append({
            "asset_id": f"pb-{image_type[:3]}-{h['id']}",
            "category": "graphic",
            "sub_category": query,
            "caption": ", ".join(tags) or query,
            "tags": tags or [query],
            "contributor": h.get("user", ""),
            "license": "Pixabay Content License",
            "source_url": url,
            "preview_url": h.get("previewURL", ""),
            "title": (tags[0] if tags else query)[:120],
        })
    return out


# ---------------------------------------------------------------------------
# Internet Archive — audio (music / SFX)
# ---------------------------------------------------------------------------
def _ia_pick_audio_file(identifier: str) -> tuple[str, float] | None:
    """Return (filename, duration_s) of the best audio file in an IA item."""
    try:
        r = requests.get(IA_FILES_URL.format(identifier=identifier), timeout=30)
        r.raise_for_status()
    except Exception:
        return None
    files = (r.json() or {}).get("files", [])
    candidates: list[tuple[str, float, int]] = []
    for f in files:
        name = f.get("name", "")
        fmt = (f.get("format") or "").lower()
        if not name:
            continue
        if not (name.lower().endswith((".mp3", ".ogg", ".wav", ".m4a")) or "mp3" in fmt):
            continue
        try:
            dur = float(f.get("length", "0") or 0)
        except ValueError:
            # "length" sometimes shows as "M:SS"
            parts = (f.get("length") or "0").split(":")
            try:
                dur = sum(float(p) * 60 ** i for i, p in enumerate(reversed(parts)))
            except ValueError:
                dur = 0.0
        size = int(f.get("size", 0) or 0)
        candidates.append((name, dur, size))
    if not candidates:
        return None
    # Prefer mp3, then smaller files (to keep the demo download cheap).
    candidates.sort(key=lambda c: (not c[0].lower().endswith(".mp3"), c[2]))
    name, dur, _ = candidates[0]
    return name, dur


def fetch_internet_archive_audio(query: str, n: int) -> list[dict]:
    """Search audio collection items on archive.org for `query`."""
    params = {
        "q": f'({query}) AND mediatype:(audio)',
        "fl[]": ["identifier", "title", "creator", "description", "subject"],
        "rows": max(n * 3, n + 3),
        "page": 1,
        "output": "json",
    }
    r = requests.get(IA_SEARCH_URL, params=params, timeout=30)
    r.raise_for_status()
    docs = (r.json() or {}).get("response", {}).get("docs", [])
    out: list[dict] = []
    for d in docs:
        if len(out) >= n:
            break
        identifier = d.get("identifier")
        if not identifier:
            continue
        picked = _ia_pick_audio_file(identifier)
        if not picked:
            continue
        filename, dur = picked
        if dur and (dur < 1.0 or dur > 600.0):
            continue
        subj = d.get("subject")
        if isinstance(subj, list):
            tags = [str(s).lower() for s in subj][:8]
        elif subj:
            tags = [s.strip().lower() for s in str(subj).split(",")][:8]
        else:
            tags = [t for t in query.split() if t]
        desc = d.get("description") or d.get("title") or query
        if isinstance(desc, list):
            desc = " ".join(str(x) for x in desc)
        out.append({
            "asset_id": f"ia-audio-{slug(identifier)}",
            "category": "audio",
            "sub_category": query,
            "caption": (str(desc) or query)[:500],
            "tags": tags,
            "contributor": str(d.get("creator", "") or ""),
            "license": "Internet Archive (item-specific)",
            "source_url": IA_DOWNLOAD_URL.format(identifier=identifier, filename=filename),
            "preview_url": "",
            "title": str(d.get("title", "") or identifier)[:120],
            "duration_s": float(dur or 0.0),
        })
        time.sleep(0.05)  # play nice with IA metadata endpoint
    return out


# ---------------------------------------------------------------------------
# Generic download — called from backfill.py's ThreadPoolExecutor
# ---------------------------------------------------------------------------
_EXT_FALLBACK = {
    "photo":   ".jpg",
    "video":   ".mp4",
    "graphic": ".png",
    "audio":   ".mp3",
}

def download_asset(item: dict) -> bool:
    """Download `item["source_url"]` under ASSETS_DIR/<category>/<asset_id><ext>.

    Mutates `item` in place, setting `local_path` (relative to ROOT) on
    success. Returns True iff the file is on disk and non-empty.
    """
    src = item.get("source_url")
    if not src:
        return False
    cat = item.get("category", "")
    ext = _ext_from_url(src, _EXT_FALLBACK.get(cat, ".bin"))
    out_dir = ASSETS_DIR / (cat if cat else "misc")
    dest = out_dir / f"{item['asset_id']}{ext}"
    if dest.exists() and dest.stat().st_size > 1024:
        item["local_path"] = str(dest.relative_to(ROOT))
        return True
    if not _download_to(src, dest):
        return False
    item["local_path"] = str(dest.relative_to(ROOT))
    return True
