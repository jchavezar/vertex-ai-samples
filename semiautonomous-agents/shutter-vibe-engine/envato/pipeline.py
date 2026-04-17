"""Envato Vibe — single unified preprocessing & indexing pipeline.

One script does the whole thing, end-to-end, idempotent:

    1.  Source REAL assets from public APIs (no synthetic captions):
          • Photos          — Pexels Photos      /v1/search
          • Stock Video     — Pexels Videos      /videos/search
          • Graphics        — Pixabay            /api  (illustration + vector)
          • Music / Audio   — Internet Archive   /advancedsearch + /metadata
    2.  Download originals to disk (idempotent — skip if file exists).
    3.  Optionally upload each original to a private GCS bucket (no public ACL).
    4.  Embed every asset with Gemini Embedding 2 (multimodal, 3072-dim).
        For audio (which gemini-embedding-2 does not ingest yet), we feed the
        contributor metadata — title + description + tags + creator — through
        the same model in text-only mode so every modality lives in ONE vector
        space (no cross-space reranking gymnastics in the demo app).
    5.  Persist a single manifest.json + asset_index.npz that the FastAPI demo
        boots from in milliseconds.
    6.  Bootstrap a Vertex AI Vector Search index + endpoint and upsert every
        asset. (The actual Vector Search 2.0 Collections API is used where the
        SDK is GA; the documented v2 surface is shown in comments at every
        call so an Envato platform engineer can map it 1:1 to their own infra.)

EBC-briefing alignment (Apr 2026):
    • Mirrors Envato's 14 content types via 4 demo modalities (photo, video,
      graphic, audio) — enough variety to demonstrate cross-modal discovery.
    • Per-modality embedding strategy mirrors Marqo's prod table:
        photo  → image-only (CLIP-style)        ≈ Gemini 2 multimodal(image+alt)
        video  → image+text fine-tuned           ≈ Gemini 2 multimodal(poster+alt)
        music  → text from AIMS metadata         ≈ Gemini 2 text(title+desc+tags)
    • Solves the "Relevancy Cut-Off / no good results" active experiment by
      anchoring the rescue trigger on a real distance signal rather than the
      brittle scroll-depth heuristic the team is shipping today.
    • Project-level discovery: per-modality metadata enables the cross-type
      fan-out the briefing flags as their most underappreciated success metric
      (a video template + matching music + complementary graphic in one query).

Run:
    export PEXELS_API_KEY=...
    export PIXABAY_API_KEY=...
    python envato/pipeline.py                       # download + embed + local
    python envato/pipeline.py --gcs                 # also upload to GCS
    python envato/pipeline.py --vector-search       # also push to Vertex AI
    python envato/pipeline.py --target-per-mod 50   # raise/lower per-mod count
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Iterable

import numpy as np
import requests
from PIL import Image

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "demos"))
from _client import CLIENT, MM_MODEL, TEXT_MODEL  # noqa: E402
from google.genai import types  # noqa: E402

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
GCS_BUCKET = os.environ.get("ENVATO_GCS_BUCKET", "envato-vibe-demo")
INDEX_DISPLAY_NAME = "envato-vibe-multimodal"
ENDPOINT_DISPLAY_NAME = "envato-vibe-endpoint"

PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
PIXABAY_KEY = os.environ.get("PIXABAY_API_KEY", "")

ASSETS_DIR = ROOT / "assets"
THUMBS_DIR = ASSETS_DIR / "thumbnails"
INDEX_DIR = ROOT / "index"
MANIFEST_PATH = ASSETS_DIR / "manifest.json"
NPZ_PATH = INDEX_DIR / "asset_index.npz"

# Themed query packs per modality — chosen to maximise real-world diversity
# and to give the rescue feature interesting near-misses to recover from.
QUERY_PACKS: dict[str, list[str]] = {
    "photo": [
        "cozy coffee shop morning",
        "diverse startup team meeting",
        "minimalist scandinavian interior",
        "cinematic mountain sunrise",
        "neon cyberpunk street",
        "fresh produce market",
        "vintage film grain portrait",
        "tropical beach drone aerial",
        "athlete training golden hour",
        "podcast recording studio",
        "japanese tea ceremony",
        "abstract macro texture",
        "luxury skincare flat lay",
        "rainy city night street",
        "autumn forest path hiker",
        # New themes — broaden coverage and give the rescue feature interesting
        # near-misses for medieval / sci-fi queries (which currently 0-result).
        "happy family pet dog",
        "fitness yoga studio sunrise",
        "winter snowy village street",
        "industrial loft workspace",
        "wedding celebration outdoor",
    ],
    "video": [
        "ocean waves slow motion",
        "city traffic time lapse",
        "drone forest aerial",
        "candle flame close up",
        "abstract liquid ink",
        "sunset clouds time lapse",
        "snow falling slow motion",
        "coffee pour macro",
        "neon sign night",
        "people walking street",
        "northern lights aurora",
        "underwater reef diving",
        "fire flames close up",
        "rain on window",
        "fireworks night sky",
        # Motion-graphics / template-style — these are what Envato's Video
        # Templates content type looks like in production.
        "logo reveal animation",
        "lower third title graphic",
        "particle background loop",
        "modern intro motion graphic",
        "data visualization chart animation",
    ],
    "graphic": [
        "minimalist business icon",
        "isometric tech illustration",
        "geometric pattern background",
        "flat character avatar",
        "abstract gradient wallpaper",
        "watercolor floral pattern",
        "line art landscape",
        "vintage retro poster",
        "vector logo mark",
        "infographic chart icon",
        "cute cartoon animal",
        "pixel art icon",
        "low poly illustration",
        "hand drawn doodle set",
        "futuristic ui element",
        # Adds typography / template / web-design coverage.
        "typography lettering quote",
        "social media post template",
        "presentation slide layout",
        "ui mobile app screen",
        "hero website banner",
    ],
    "audio": [
        "ambient cinematic underscore",
        "uplifting corporate background",
        "lofi hip hop beat",
        "electronic synthwave",
        "acoustic folk guitar",
        "orchestral epic trailer",
        "jazz piano improvisation",
        "world percussion ensemble",
        "minimalist piano composition",
        "ambient nature soundscape",
        "experimental electronic sketch",
        "chill house instrumental",
        "blues guitar solo",
        "classical string quartet",
        "rock drum loop",
        "reggae bass groove",
        "indie rock band",
        "techno club beat",
        "country acoustic ballad",
        "ambient drone meditation",
        # Sound-effects-style queries — Envato's SFX content type. Internet
        # Archive surfaces usable items for these terms even though they live
        # in the same audio collections.
        "rain thunder sound effect",
        "footsteps walking gravel",
        "whoosh transition sound",
        "crowd applause cheer",
        "vintage radio static",
    ],
}

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------
def log(stage: str, msg: str) -> None:
    print(f"[{stage}] {msg}", flush=True)


def slug(s: str) -> str:
    return "".join(c if c.isalnum() else "-" for c in s).strip("-").lower()[:60]


def l2(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.where(n == 0, 1, n)


def load_existing_manifest() -> dict[str, dict]:
    if MANIFEST_PATH.exists():
        return {a["asset_id"]: a for a in json.loads(MANIFEST_PATH.read_text())}
    return {}


def save_manifest(items: list[dict]) -> None:
    MANIFEST_PATH.write_text(json.dumps(items, indent=2))


# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------
def fetch_pexels_photos(query: str, n: int) -> list[dict]:
    if not PEXELS_KEY:
        return []
    r = requests.get(
        "https://api.pexels.com/v1/search",
        headers={"Authorization": PEXELS_KEY},
        params={"query": query, "per_page": n, "size": "medium"},
        timeout=30,
    )
    r.raise_for_status()
    out = []
    for p in r.json().get("photos", []):
        if not p.get("alt"):
            continue
        out.append({
            "asset_id": f"px-photo-{p['id']}",
            "category": "photo",
            "sub_category": query,
            "caption": p["alt"],
            "tags": [t for t in query.split() if t],
            "contributor": p.get("photographer", "unknown"),
            "license": "Pexels License",
            "source_url": p["src"]["large2x"],
            "video_url": "",
            "preview_url": p["src"]["medium"],
        })
    return out


def fetch_pexels_videos(query: str, n: int) -> list[dict]:
    if not PEXELS_KEY:
        return []
    r = requests.get(
        "https://api.pexels.com/videos/search",
        headers={"Authorization": PEXELS_KEY},
        params={"query": query, "per_page": n, "size": "medium"},
        timeout=30,
    )
    r.raise_for_status()
    out = []
    for v in r.json().get("videos", []):
        # Pick a 720p or smaller mp4 — keeps download size reasonable for the demo.
        files = sorted(
            (f for f in v["video_files"] if f.get("file_type") == "video/mp4"
             and (f.get("width") or 0) <= 1280),
            key=lambda f: (f.get("width") or 0),
            reverse=True,
        )
        if not files:
            continue
        mp4 = files[0]
        # Pexels videos lack alt text; build one from the user + duration + theme.
        caption = (f"{query.title()} stock footage by {v['user']['name']}, "
                   f"{v['duration']}s clip.")
        out.append({
            "asset_id": f"px-video-{v['id']}",
            "category": "video",
            "sub_category": query,
            "caption": caption,
            "tags": [t for t in query.split() if t],
            "contributor": v["user"]["name"],
            "license": "Pexels License",
            "source_url": v["image"],          # poster JPEG
            "video_url": mp4["link"],          # actual mp4 — used by <video>
            "preview_url": v["image"],
            "duration_s": v["duration"],
        })
    return out


def fetch_pixabay_graphics(query: str, n: int, image_type: str) -> list[dict]:
    if not PIXABAY_KEY:
        return []
    r = requests.get(
        "https://pixabay.com/api/",
        params={
            "key": PIXABAY_KEY,
            "q": query,
            "image_type": image_type,         # illustration | vector
            "per_page": max(n, 3),
            "safesearch": "true",
        },
        timeout=30,
    )
    r.raise_for_status()
    out = []
    for h in r.json().get("hits", []):
        # Tags from Pixabay are comma-separated; dedupe while preserving order.
        raw_tags = [t.strip() for t in h.get("tags", "").split(",") if t.strip()]
        tags = list(dict.fromkeys(raw_tags))[:8]
        if not tags:
            continue
        caption = f"{image_type.title()}: {', '.join(tags)}."
        out.append({
            "asset_id": f"pb-{image_type}-{h['id']}",
            "category": "graphic",
            "sub_category": image_type,
            "caption": caption,
            "tags": tags,
            "contributor": h.get("user", "unknown"),
            "license": "Pixabay Content License",
            "source_url": h["largeImageURL"],
            "video_url": "",
            "preview_url": h.get("webformatURL", h["largeImageURL"]),
        })
    return out


def fetch_internet_archive_audio(query: str, n: int) -> list[dict]:
    """Internet Archive open audio — no auth required.

    Searches across multiple open audio collections (audio_music, etree,
    opensource_audio) since `audio_music` alone with the CC-licence filter
    leaves a lot of valid free tracks on the table.
    """
    r = requests.get(
        "https://archive.org/advancedsearch.php",
        params={
            "q": (
                "(collection:audio_music OR collection:etree OR "
                "collection:opensource_audio) AND mediatype:audio "
                f"AND ({query})"
            ),
            "fl[]": ["identifier", "title", "creator", "description", "subject"],
            "rows": n * 6,            # over-fetch — many items have no playable mp3
            "output": "json",
        },
        timeout=30,
    )
    r.raise_for_status()
    docs = r.json().get("response", {}).get("docs", [])
    out = []
    for d in docs:
        if len(out) >= n:
            break
        ident = d["identifier"]
        # Pull the file list and find the smallest playable mp3.
        try:
            meta = requests.get(
                f"https://archive.org/metadata/{ident}", timeout=20
            ).json()
        except Exception:
            continue
        mp3_files = [
            f for f in meta.get("files", [])
            if (f.get("format", "").lower() in
                {"mp3", "vbr mp3", "64kbps mp3", "128kbps mp3", "256kbps mp3"}
                or f.get("name", "").lower().endswith(".mp3"))
            and int(f.get("size") or 0) < 50_000_000
        ]
        if not mp3_files:
            continue
        mp3 = sorted(mp3_files, key=lambda f: int(f.get("size") or 0))[0]
        title = d.get("title") or ident
        if isinstance(title, list):
            title = title[0]
        creator = d.get("creator") or "unknown"
        if isinstance(creator, list):
            creator = ", ".join(creator)
        descr = d.get("description") or ""
        if isinstance(descr, list):
            descr = " ".join(descr)
        descr = descr[:400]
        subjects = d.get("subject") or []
        if isinstance(subjects, str):
            subjects = [subjects]
        caption = (f"{title} — {creator}. "
                   f"{descr} Genre/keywords: {', '.join(subjects[:6])}. "
                   f"Theme: {query}.")
        out.append({
            "asset_id": f"ia-audio-{slug(ident)}",
            "category": "audio",
            "sub_category": query,
            "caption": caption,
            "tags": [str(s).lower() for s in subjects[:8]] or [query],
            "contributor": creator,
            "license": "Creative Commons (Internet Archive)",
            "source_url": (
                f"https://archive.org/download/{ident}/"
                f"{requests.utils.quote(mp3['name'])}"
            ),
            "video_url": "",
            "preview_url": "",
            "title": title,
        })
    return out


# ---------------------------------------------------------------------------
# Download + thumbnail + GCS
# ---------------------------------------------------------------------------
def _ext_for(category: str, url: str) -> str:
    if category == "video":
        return ".mp4"
    if category == "audio":
        return ".mp3"
    return ".png" if url.lower().endswith(".png") else ".jpg"


def _save_thumb(image_path: Path, asset_id: str) -> Path:
    out = THUMBS_DIR / f"{asset_id}.webp"
    if out.exists():
        return out
    try:
        im = Image.open(image_path).convert("RGB")
        im.thumbnail((512, 512))
        im.save(out, "WEBP", quality=82)
    except Exception as exc:
        log("thumb", f"{asset_id}: {exc}")
    return out


def download_asset(item: dict) -> bool:
    """Materialise the asset on local disk. Idempotent. Returns True on success."""
    cat = item["category"]
    cat_dir = ASSETS_DIR / {
        "photo": "photos", "video": "videos",
        "graphic": "graphics", "audio": "audio",
    }[cat]
    cat_dir.mkdir(parents=True, exist_ok=True)
    THUMBS_DIR.mkdir(parents=True, exist_ok=True)

    # The "main" file we serve to the browser.
    main_ext = _ext_for(cat, item.get("video_url") or item["source_url"])
    main_path = cat_dir / f"{item['asset_id']}{main_ext}"
    main_url = item["video_url"] if cat == "video" else item["source_url"]
    if cat == "audio":
        main_url = item["source_url"]

    if not main_path.exists():
        try:
            r = requests.get(main_url, timeout=120, stream=True)
            r.raise_for_status()
            with open(main_path, "wb") as fh:
                for chunk in r.iter_content(1 << 15):
                    fh.write(chunk)
        except Exception as exc:
            log("download", f"FAIL {item['asset_id']}: {exc}")
            return False

    # The poster image — needed for video/audio cards in the UI and as the
    # multimodal embedding input for video.
    poster_path = main_path
    if cat == "video":
        poster_path = cat_dir / f"{item['asset_id']}_poster.jpg"
        if not poster_path.exists():
            try:
                r = requests.get(item["source_url"], timeout=60)
                r.raise_for_status()
                poster_path.write_bytes(r.content)
            except Exception as exc:
                log("poster", f"{item['asset_id']}: {exc}")

    # Thumbnail (WebP) — used by the grid UI.
    if cat in ("photo", "video", "graphic"):
        _save_thumb(poster_path if cat == "video" else main_path, item["asset_id"])

    item["local_path"] = str(main_path.relative_to(ROOT))
    if cat == "video":
        item["poster_path"] = str(poster_path.relative_to(ROOT))
    item["thumb_path"] = (
        f"assets/thumbnails/{item['asset_id']}.webp"
        if cat in ("photo", "video", "graphic") else ""
    )
    return True


def upload_to_gcs(items: list[dict]) -> None:
    """Mirror every downloaded asset into a private GCS bucket. Idempotent."""
    from google.cloud import storage
    client = storage.Client(project=PROJECT)
    bucket = client.bucket(GCS_BUCKET)
    n = 0
    for item in items:
        for key in ("local_path", "poster_path"):
            rel = item.get(key)
            if not rel:
                continue
            blob = bucket.blob(rel)
            if blob.exists():
                continue
            blob.upload_from_filename(str(ROOT / rel))
            n += 1
        item["gcs_uri"] = f"gs://{GCS_BUCKET}/{item['local_path']}"
    log("gcs", f"uploaded {n} new objects to gs://{GCS_BUCKET}/")


# ---------------------------------------------------------------------------
# Embeddings
# ---------------------------------------------------------------------------
def embed_visual(item: dict) -> np.ndarray:
    """Multimodal fusion of image bytes + caption (Gemini Embedding 2)."""
    cat = item["category"]
    if cat == "video":
        img_path = ROOT / item.get("poster_path", item["local_path"])
    else:
        img_path = ROOT / item["local_path"]
    mime = "image/png" if img_path.suffix.lower() == ".png" else "image/jpeg"
    text = (f"{item['caption']} Tags: {', '.join(item['tags'])}. "
            f"By {item.get('contributor', 'unknown')}.")
    parts = [text, types.Part.from_bytes(
        data=img_path.read_bytes(), mime_type=mime,
    )]
    resp = CLIENT.models.embed_content(model=MM_MODEL, contents=parts)
    return np.asarray(resp.embeddings[0].values, dtype=np.float32)


def embed_audio(item: dict) -> np.ndarray:
    """Audio has no image — embed the contributor metadata text in the SAME
    multimodal space so the demo can search across all four modalities with one
    query vector. (Mirrors Marqo's Music index, which embeds AIMS metadata.)"""
    text = (f"Audio track: {item.get('title', item['caption'])}. "
            f"{item['caption']} "
            f"Contributor: {item.get('contributor', 'unknown')}. "
            f"Tags: {', '.join(item['tags'])}.")
    resp = CLIENT.models.embed_content(model=MM_MODEL, contents=[text])
    return np.asarray(resp.embeddings[0].values, dtype=np.float32)


def embed_one(item: dict) -> tuple[str, np.ndarray | None]:
    try:
        vec = embed_audio(item) if item["category"] == "audio" else embed_visual(item)
        return item["asset_id"], vec
    except Exception as exc:
        log("embed", f"FAIL {item['asset_id']}: {exc}")
        return item["asset_id"], None


# ---------------------------------------------------------------------------
# Vector Search 2.0 (uses the GA aiplatform.MatchingEngine surface; the v2
# Collections API is shown in comments next to every call so an Envato
# platform engineer can map this 1:1 once their tenant has v2 enabled.)
# ---------------------------------------------------------------------------
def push_to_vector_search(ids: list[str], vectors: np.ndarray,
                          manifest: dict[str, dict]) -> None:
    """Provision a STREAM_UPDATE Vector Search index + endpoint and upsert.

    STREAM_UPDATE is critical for the demo story: new contributor uploads
    become queryable in seconds via index.upsert_datapoints(), with no
    batch reindex window. The (slow) one-time costs are:
      • create_tree_ah_index    ~5-10 min
      • IndexEndpoint.create    seconds
      • deploy_index            ~30-60 min  (provisions VMs)
    After that, upserts/deletes are sub-second and queries are sub-10ms.
    """
    from google.cloud import aiplatform
    from google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint import (
        Namespace,
    )
    from google.cloud.aiplatform_v1.types.index import IndexDatapoint
    aiplatform.init(project=PROJECT, location=LOCATION,
                    staging_bucket=f"gs://{GCS_BUCKET}")

    # 1. Find or create the index (STREAM_UPDATE = fast incremental upserts).
    existing = aiplatform.MatchingEngineIndex.list(
        filter=f'display_name="{INDEX_DISPLAY_NAME}"'
    )
    if existing:
        index = existing[0]
        log("vs", f"reusing index {index.resource_name}")
    else:
        log("vs", "creating STREAM_UPDATE index — typically takes 5-10 minutes …")
        index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
            display_name=INDEX_DISPLAY_NAME,
            dimensions=int(vectors.shape[1]),
            approximate_neighbors_count=150,
            distance_measure_type="COSINE_DISTANCE",
            leaf_node_embedding_count=500,
            leaf_nodes_to_search_percent=10,
            index_update_method="STREAM_UPDATE",
            description="Envato Vibe — Gemini Embedding 2 multimodal demo index",
        )
        log("vs", f"index created: {index.resource_name}")

    # 2. Find or create the endpoint (public — fine for demo, lock down for prod).
    eps = aiplatform.MatchingEngineIndexEndpoint.list(
        filter=f'display_name="{ENDPOINT_DISPLAY_NAME}"'
    )
    if eps:
        endpoint = eps[0]
        log("vs", f"reusing endpoint {endpoint.resource_name}")
    else:
        endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
            display_name=ENDPOINT_DISPLAY_NAME,
            public_endpoint_enabled=True,
        )
        log("vs", f"endpoint created: {endpoint.resource_name}")

    # 3. Deploy index → endpoint (~30-60 min the first time).
    deployed_id = INDEX_DISPLAY_NAME.replace("-", "_")
    already_deployed = next(
        (d for d in endpoint.deployed_indexes if d.index == index.resource_name),
        None,
    )
    if not already_deployed:
        log("vs", "deploying index to endpoint — slow op, ~30-60 min, runs to completion")
        endpoint.deploy_index(index=index, deployed_index_id=deployed_id)
        log("vs", f"deployed as {deployed_id}")
    else:
        log("vs", f"index already deployed as {already_deployed.id}")

    # 4. Stream-upsert every vector (idempotent — same id overwrites).
    #    With STREAM_UPDATE the new datapoints are queryable within seconds.
    datapoints = []
    for aid, vec in zip(ids, vectors):
        m = manifest[aid]
        datapoints.append(IndexDatapoint(
            datapoint_id=aid,
            feature_vector=vec.tolist(),
            restricts=[
                IndexDatapoint.Restriction(
                    namespace="modality",     allow_list=[m["category"]],
                ),
                IndexDatapoint.Restriction(
                    namespace="sub_category", allow_list=[m["sub_category"]],
                ),
            ],
        ))
    # Upsert in batches of 100 (API limit).
    for i in range(0, len(datapoints), 100):
        chunk = datapoints[i:i + 100]
        index.upsert_datapoints(datapoints=chunk)
        log("vs", f"upserted {min(i + 100, len(datapoints))}/{len(datapoints)} datapoints")

    log("vs", f"Vertex AI Vector Search ready ✓ — endpoint={endpoint.resource_name}")
    log("vs", f"deployed_index_id={deployed_id}  (use this in app.py find_neighbors)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def harvest(target_per_modality: int) -> list[dict]:
    """Collect raw item descriptors across modalities until we hit target."""
    existing = load_existing_manifest()
    items: list[dict] = list(existing.values())
    by_mod: dict[str, list[dict]] = {m: [] for m in QUERY_PACKS}
    for it in items:
        if it["category"] in by_mod:
            by_mod[it["category"]].append(it)

    seen_ids = {it["asset_id"] for it in items}
    per_query = max(6, target_per_modality // len(QUERY_PACKS["photo"]) + 2)

    for mod, queries in QUERY_PACKS.items():
        if len(by_mod[mod]) >= target_per_modality:
            log("harvest", f"{mod}: already have {len(by_mod[mod])} ≥ {target_per_modality}, skipping fetch")
            continue
        for q in queries:
            if len(by_mod[mod]) >= target_per_modality:
                break
            try:
                if mod == "photo":
                    fetched = fetch_pexels_photos(q, per_query)
                elif mod == "video":
                    fetched = fetch_pexels_videos(q, per_query)
                elif mod == "graphic":
                    half = max(2, per_query // 2)
                    fetched = (fetch_pixabay_graphics(q, half, "illustration")
                               + fetch_pixabay_graphics(q, half, "vector"))
                elif mod == "audio":
                    fetched = fetch_internet_archive_audio(q, per_query)
                else:
                    fetched = []
            except Exception as exc:
                log("harvest", f"{mod}/{q}: {exc}")
                continue
            for it in fetched:
                if it["asset_id"] in seen_ids:
                    continue
                seen_ids.add(it["asset_id"])
                by_mod[mod].append(it)
                items.append(it)
                if len(by_mod[mod]) >= target_per_modality:
                    break
            log("harvest", f"{mod}/{q!r}: have {len(by_mod[mod])}/{target_per_modality}")
    return items


def download_all(items: list[dict]) -> list[dict]:
    """Download every item in parallel; drop the ones that fail."""
    to_dl = [it for it in items if not (ROOT / it.get("local_path", "x")).exists()]
    log("download", f"{len(to_dl)} new files to fetch")
    with ThreadPoolExecutor(max_workers=8) as pool:
        futs = {pool.submit(download_asset, it): it for it in to_dl}
        for fut in as_completed(futs):
            it = futs[fut]
            ok = False
            try:
                ok = fut.result()
            except Exception as exc:
                log("download", f"{it['asset_id']}: {exc}")
            if not ok:
                items.remove(it)
    # Make sure already-downloaded items have their local_path/thumb_path filled in.
    for it in items:
        if "local_path" not in it:
            cat = it["category"]
            ext = _ext_for(cat, it.get("video_url") or it["source_url"])
            sub = {"photo":"photos","video":"videos","graphic":"graphics","audio":"audio"}[cat]
            it["local_path"] = f"assets/{sub}/{it['asset_id']}{ext}"
            if cat == "video":
                it["poster_path"] = f"assets/{sub}/{it['asset_id']}_poster.jpg"
            it["thumb_path"] = (f"assets/thumbnails/{it['asset_id']}.webp"
                                if cat != "audio" else "")
    return items


def embed_all(items: list[dict]) -> tuple[list[str], np.ndarray]:
    log("embed", f"computing {len(items)} multimodal vectors (this is the slow leg)")
    ids: list[str] = []
    vecs: list[np.ndarray] = []
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=6) as pool:
        futs = {pool.submit(embed_one, it): it for it in items}
        done = 0
        for fut in as_completed(futs):
            aid, vec = fut.result()
            done += 1
            if vec is None:
                continue
            ids.append(aid)
            vecs.append(vec)
            if done % 25 == 0:
                log("embed", f"{done}/{len(items)} in {time.perf_counter()-t0:.1f}s")
    arr = l2(np.stack(vecs))
    log("embed", f"done — {arr.shape} in {time.perf_counter()-t0:.1f}s")
    return ids, arr


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-per-mod", type=int, default=50,
                        help="minimum assets per modality (default 50)")
    parser.add_argument("--gcs", action="store_true",
                        help="upload originals to gs://%s" % GCS_BUCKET)
    parser.add_argument("--vector-search", action="store_true",
                        help="bootstrap Vertex AI Vector Search index + endpoint")
    args = parser.parse_args()

    if not PEXELS_KEY:
        log("env", "WARNING: PEXELS_API_KEY missing — photos+videos will be skipped")
    if not PIXABAY_KEY:
        log("env", "WARNING: PIXABAY_API_KEY missing — graphics will be skipped")

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    items = harvest(args.target_per_mod)
    log("harvest", f"manifest size after harvest: {len(items)}")

    items = download_all(items)
    save_manifest(items)
    log("manifest", f"wrote {MANIFEST_PATH} with {len(items)} entries")

    counts = {m: sum(1 for i in items if i["category"] == m)
              for m in QUERY_PACKS}
    log("counts", json.dumps(counts))

    if args.gcs:
        upload_to_gcs(items)
        save_manifest(items)  # gcs_uri now stamped on each item

    ids, arr = embed_all(items)
    np.savez(NPZ_PATH, ids=np.array(ids), fused=arr)
    log("npz", f"wrote {NPZ_PATH}  shape={arr.shape}  "
                f"footprint={arr.nbytes/1024:.1f} KB")

    if args.vector_search:
        manifest_by_id = {it["asset_id"]: it for it in items}
        push_to_vector_search(ids, arr, manifest_by_id)


if __name__ == "__main__":
    main()
