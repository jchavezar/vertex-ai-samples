#!/usr/bin/env python3
"""Pillar 5 · Veo 3.1 image-to-video listing walkthroughs (offline batch tool, not imported by app.py).

For each listing, every stop on the tour route (front exterior, great room, kitchen, ...) is animated from THAT
listing's own photo, used as the first frame, with a slow steadicam / dolly camera move (Veo 3.1 image-to-video).
The clips are stitched in route order with ffmpeg `xfade` + lower-third room titles, uploaded to
gs://vtxdemos-abnb-images/tours/veo/<id>_walkthrough.mp4 (public, video/mp4, +faststart) and recorded in
static/veo_tours_manifest.json, mirrored to gs://vtxdemos-abnb-images/tours/veo/veo_tours_manifest.json (no-cache).

Usage (ADC, project vtxdemos):
  python3 veo_tours.py RKT-098:ext                 # exterior-only route (front -> rear patio/pool -> aerial)
  python3 veo_tours.py RKT-010 RKT-044             # full route (exterior + key interiors + rear patio)
  python3 veo_tours.py RKT-012:ext_front+living_room+chef_kitchen
Options: --concurrency N (parallel Veo requests, default 12), --model veo-3.1-fast-generate-001
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime as _dt
import json
import os
import random
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

os.environ.setdefault("GOOGLE_API_USE_CLIENT_CERTIFICATE", "false")

from google import genai  # noqa: E402
from google.genai import types  # noqa: E402

PROJECT_ID = "vtxdemos"
LOCATION = "us-central1"
BUCKET = "vtxdemos-abnb-images"
GCS_PREFIX = "tours/veo"
PUBLIC_BASE = f"https://storage.googleapis.com/{BUCKET}/{GCS_PREFIX}"
GCS_PUBLIC_PREFIX = "https://storage.googleapis.com/"

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
CATALOG_PATH = HERE / "catalog_108_index.json"
MANIFEST_PATH = REPO / "static" / "veo_tours_manifest.json"
WORK = Path(os.environ.get("VEO_TOURS_WORKDIR", "/tmp/veo_tours"))

DEFAULT_MODELS = ["veo-3.1-fast-generate-001", "veo-3.1-generate-001"]
CLIP_SECONDS = 6
XFADE_S = 0.6
FONT_DIR = "/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF"
FONT_BOLD = f"{FONT_DIR}/Roboto-Bold.ttf"
FONT_REG = f"{FONT_DIR}/Roboto-Regular.ttf"
FONT_MED = f"{FONT_DIR}/Roboto-Medium.ttf"

# Tour stops: room_id -> (chapter title, camera kind, room noun used in the prompt)
STOPS: Dict[str, Dict[str, str]] = {
    "ext_front": {"title": "Front Exterior", "kind": "exterior", "noun": "front of the house"},
    "living_room": {"title": "Great Room", "kind": "interior", "noun": "great room"},
    "chef_kitchen": {"title": "Chef's Kitchen", "kind": "interior", "noun": "kitchen"},
    "dining_room": {"title": "Dining Room", "kind": "interior", "noun": "dining room"},
    "primary_bedroom": {"title": "Primary Suite", "kind": "interior", "noun": "primary bedroom"},
    "ext_rear": {"title": "Rear Patio & Pool", "kind": "rear", "noun": "rear patio and pool"},
    "ext_aerial": {"title": "Aerial View", "kind": "aerial", "noun": "house and its lot"},
}
ROUTES = {
    "full": ["ext_front", "living_room", "chef_kitchen", "dining_room", "primary_bedroom", "ext_rear"],
    "ext": ["ext_front", "ext_rear", "ext_aerial"],
}

_KEEP = (
    "Keep the exact architecture, layout, materials, colors, furniture, landscaping and lighting of the photo; "
    "nothing is added, removed or restyled."
)
_STYLE = (
    "Photorealistic real-estate cinematography, stabilized gimbal, steady exposure, natural parallax, "
    "slow and graceful camera motion. No people, no animals, no text, no captions, no logos, no watermarks."
)
_CAMERA = {
    "exterior": "the camera performs a slow, smooth lateral dolly with a gentle push-in along the {noun}, "
                "revealing natural parallax between the landscaping, facade and roofline.",
    "interior": "a smooth steadicam glides slowly forward into the {noun}, with natural parallax between the "
                "foreground furniture and the walls, windows and ceiling behind it.",
    "rear": "the camera performs a slow, gentle lateral dolly across the {noun}, with soft parallax between the "
            "outdoor furniture, the water and the rear facade.",
    "aerial": "a drone camera performs a slow, smooth orbit around the {noun}, keeping the building centered, "
              "with natural parallax between the roofline, trees and surrounding terrain.",
}
NEGATIVE_PROMPT = (
    "people, person, crowd, animals, text, captions, subtitles, logos, watermark, fast camera movement, shaky "
    "camera, zoom blur, morphing, warping or melting architecture, distorted furniture, flicker, cartoon, CGI look"
)

_print_lock = threading.Lock()
_manifest_lock = threading.Lock()
_tls = threading.local()


def log(msg: str) -> None:
    with _print_lock:
        print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def https_to_gs(url: str) -> str:
    u = (url or "").split("?", 1)[0]
    return "gs://" + u[len(GCS_PUBLIC_PREFIX):] if u.startswith(GCS_PUBLIC_PREFIX) else ""


def client() -> genai.Client:
    c = getattr(_tls, "client", None)
    if c is None:
        c = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
        _tls.client = c
    return c


def load_catalog() -> Dict[str, Dict[str, Any]]:
    cat = json.loads(CATALOG_PATH.read_text())
    return {it["id"]: it for it in cat.get("announcements", [])}


def room_image(listing: Dict[str, Any], room_id: str) -> str:
    for r in listing.get("rooms", []):
        if r.get("room_id") == room_id and r.get("image_url"):
            return r["image_url"]
    ext = listing.get("exterior_urls") or []
    idx = {"ext_front": 0, "ext_rear": 1, "ext_aerial": 2}.get(room_id)
    if idx is not None and idx < len(ext):
        return ext[idx]
    return ""


def room_subtitle(listing: Dict[str, Any], room_id: str) -> str:
    city = listing.get("city", "")
    for r in listing.get("rooms", []):
        if r.get("room_id") == room_id:
            dims = (r.get("dimensions") or "").replace(" · Level 1", "").strip()
            if room_id.startswith("ext_"):
                return f"{listing.get('address', '').split(',')[0]} · {city}".strip(" ·")
            return f"{dims} · {city}".strip(" ·") if dims else city
    return city


def build_prompt(room_id: str) -> str:
    st = STOPS[room_id]
    camera = _CAMERA[st["kind"]].format(noun=st["noun"])
    return f"Real-estate listing walkthrough video. Starting exactly from this photo, {camera} {_KEEP} {_STYLE}"


def _download_gs(uri: str) -> bytes:
    return subprocess.run(["gsutil", "-q", "cat", uri], check=True, capture_output=True).stdout


def generate_clip(listing_id: str, room_id: str, image_url: str, out_path: Path, models: List[str]) -> Dict[str, Any]:
    if out_path.exists() and out_path.stat().st_size > 100_000:
        return {"ok": True, "cached": True, "model": "cached"}
    gs_uri = https_to_gs(image_url)
    if not gs_uri:
        return {"ok": False, "error": f"not a GCS image url: {image_url}"}
    image = types.Image(gcs_uri=gs_uri, mime_type="image/jpeg")
    prompt = build_prompt(room_id)
    use_negative = True
    model_idx = 0
    delay = 8.0
    last_err = ""
    t_start = time.time()
    for attempt in range(1, 13):
        model = models[min(model_idx, len(models) - 1)]
        try:
            cfg_kwargs: Dict[str, Any] = dict(
                aspect_ratio="16:9", duration_seconds=CLIP_SECONDS, resolution="720p",
                generate_audio=False, number_of_videos=1,
            )
            if use_negative:
                cfg_kwargs["negative_prompt"] = NEGATIVE_PROMPT
            op = client().models.generate_videos(
                model=model, prompt=prompt, image=image, config=types.GenerateVideosConfig(**cfg_kwargs),
            )
            t_op = time.time()
            while not op.done:
                if time.time() - t_op > 900:
                    raise TimeoutError("Veo operation exceeded 15 min")
                time.sleep(7.0)
                op = client().operations.get(op)
            if getattr(op, "error", None):
                raise RuntimeError(f"operation error: {op.error}")
            resp = op.response or getattr(op, "result", None)
            vids = list(getattr(resp, "generated_videos", None) or [])
            if not vids:
                reasons = getattr(resp, "rai_media_filtered_reasons", None)
                raise RuntimeError(f"no video returned (rai_filtered={reasons})")
            video = vids[0].video
            data = getattr(video, "video_bytes", None)
            if not data and getattr(video, "uri", None):
                data = _download_gs(video.uri)
            if not data:
                raise RuntimeError("empty video payload")
            out_path.parent.mkdir(parents=True, exist_ok=True)
            tmp = out_path.with_suffix(".part")
            tmp.write_bytes(data)
            os.replace(tmp, out_path)
            dt = time.time() - t_start
            log(f"  ✓ {listing_id}/{room_id} via {model} in {dt:.0f}s ({len(data) / 1e6:.1f} MB, attempt {attempt})")
            return {"ok": True, "model": model, "seconds": round(dt, 1)}
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {str(e)[:300]}"
            low = last_err.lower()
            if "negative_prompt" in low or "negativeprompt" in low:
                use_negative = False
                continue
            if ("404" in low or "not_found" in low or "not found" in low or "permission" in low) and \
                    model_idx < len(models) - 1:
                model_idx += 1
                log(f"  ↪ {listing_id}/{room_id}: {model} unavailable, switching to {models[model_idx]}")
                continue
            quota = any(k in low for k in ("429", "resource_exhausted", "quota", "rate"))
            wait = (delay * (1.6 if quota else 1.0)) + random.uniform(0, 6)
            log(f"  … {listing_id}/{room_id} attempt {attempt} failed ({last_err[:160]}); retry in {wait:.0f}s")
            time.sleep(wait)
            delay = min(delay * 1.7, 120.0)
    return {"ok": False, "error": last_err}


def probe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    return float(out)


def stitch(listing: Dict[str, Any], stops: List[Dict[str, Any]], out_path: Path, route_label: str) -> Dict[str, Any]:
    """xfade the clips in route order and burn lower-third room titles. Returns duration + chapter offsets."""
    work = out_path.parent
    durs = [probe_duration(s["path"]) for s in stops]
    n = len(stops)
    starts = [0.0]
    parts: List[str] = []
    for i in range(n):
        parts.append(
            f"[{i}:v]scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,fps=24,"
            f"format=yuv420p,setsar=1,settb=AVTB,setpts=PTS-STARTPTS[v{i}]"
        )
    prev, acc = "v0", durs[0]
    for i in range(1, n):
        off = acc - XFADE_S
        parts.append(f"[{prev}][v{i}]xfade=transition=fade:duration={XFADE_S}:offset={off:.3f}[x{i}]")
        starts.append(off)
        prev, acc = f"x{i}", acc + durs[i] - XFADE_S
    total = acc

    tag_file = work / "txt_tag.txt"
    tag_file.write_text("AI walkthrough · Veo 3.1 · animated from this listing's photos")
    draws = [
        f"drawtext=fontfile={FONT_MED}:textfile={tag_file}:fontsize=17:fontcolor=white@0.95:"
        f"x=w-tw-30:y=26:box=1:boxcolor=black@0.42:boxborderw=9"
    ]
    for i, s in enumerate(stops):
        ts = starts[i] + (0.25 if i == 0 else 0.45)
        te = (starts[i + 1] if i + 1 < n else total) - 0.1
        tf, sf = work / f"txt_title_{i}.txt", work / f"txt_sub_{i}.txt"
        tf.write_text(s["title"])
        sf.write_text(s["subtitle"])
        en = f"enable='between(t,{ts:.2f},{te:.2f})'"
        draws.append(
            f"drawtext=fontfile={FONT_BOLD}:textfile={tf}:fontsize=40:fontcolor=white:x=56:y=h-162:"
            f"box=1:boxcolor=black@0.50:boxborderw=14:{en}"
        )
        draws.append(
            f"drawtext=fontfile={FONT_REG}:textfile={sf}:fontsize=22:fontcolor=0xE5E7EB:x=56:y=h-96:"
            f"box=1:boxcolor=black@0.50:boxborderw=10:{en}"
        )
    parts.append(f"[{prev}]" + ",".join(draws) + "[vout]")
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    for s in stops:
        cmd += ["-i", str(s["path"])]
    cmd += [
        "-filter_complex", ";".join(parts), "-map", "[vout]", "-an",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", str(out_path),
    ]
    subprocess.run(cmd, check=True)
    total = probe_duration(out_path)
    chapters = [
        {"room_id": s["room_id"], "title": s["title"], "t": round(starts[i], 2)} for i, s in enumerate(stops)
    ]
    return {"duration_s": round(total, 2), "chapters": chapters}


def gsutil_cp(local: Path, gs_uri: str, content_type: str, cache_control: str) -> None:
    subprocess.run(
        ["gsutil", "-q", "-h", f"Content-Type:{content_type}", "-h", f"Cache-Control:{cache_control}",
         "cp", str(local), gs_uri],
        check=True,
    )


def update_manifest(listing_id: str, entry: Dict[str, Any]) -> None:
    import fcntl  # cross-process lock: several veo_tours.py batches may run at once

    with _manifest_lock:
        MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
        lock_path = WORK / ".manifest.lock"
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        with open(lock_path, "w") as lock_fh:
            fcntl.flock(lock_fh, fcntl.LOCK_EX)
            try:
                data = json.loads(MANIFEST_PATH.read_text()) if MANIFEST_PATH.exists() else {}
            except Exception:
                data = {}
            data[listing_id] = entry
            tmp = MANIFEST_PATH.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
            os.replace(tmp, MANIFEST_PATH)
            try:
                gsutil_cp(MANIFEST_PATH, f"gs://{BUCKET}/{GCS_PREFIX}/veo_tours_manifest.json",
                          "application/json", "no-cache, max-age=0")
            except Exception as e:  # noqa: BLE001
                log(f"  ! manifest mirror upload failed: {e}")


def parse_spec(spec: str) -> Dict[str, Any]:
    lid, _, route = spec.partition(":")
    route = route or "full"
    if route in ROUTES:
        return {"id": lid, "route_name": "exterior" if route == "ext" else route, "stops": list(ROUTES[route])}
    return {"id": lid, "route_name": "custom", "stops": [r for r in route.split("+") if r in STOPS]}


def finish_listing(listing: Dict[str, Any], spec: Dict[str, Any], results: Dict[str, Dict[str, Any]],
                   models_used: List[str]) -> Dict[str, Any]:
    lid = listing["id"]
    work = WORK / lid
    stops = []
    for room_id in spec["stops"]:
        res = results.get(room_id) or {}
        path = work / f"{room_id}.mp4"
        if res.get("ok") and path.exists():
            stops.append({
                "room_id": room_id, "path": path,
                "title": STOPS[room_id]["title"], "subtitle": room_subtitle(listing, room_id),
            })
    failed = [r for r in spec["stops"] if not (results.get(r) or {}).get("ok")]
    if len(stops) < 2:
        log(f"✗ {lid}: only {len(stops)} clip(s) succeeded, skipping stitch (failed: {failed})")
        return {"id": lid, "ok": False, "failed": failed}
    out_mp4 = work / f"{lid}_walkthrough.mp4"
    meta = stitch(listing, stops, out_mp4, spec["route_name"])
    gs_uri = f"gs://{BUCKET}/{GCS_PREFIX}/{lid}_walkthrough.mp4"
    gsutil_cp(out_mp4, gs_uri, "video/mp4", "public, max-age=300")
    model = next((m for m in models_used if m and m != "cached"), DEFAULT_MODELS[0])
    entry = {
        "url": f"{PUBLIC_BASE}/{lid}_walkthrough.mp4?v={int(time.time())}",
        "poster": room_image(listing, "ext_front"),
        "duration_s": meta["duration_s"],
        "model": model,
        "route": spec["route_name"],
        "chapters": meta["chapters"],
        "title": listing.get("title", ""),
        "generated_at": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "width": 1280,
        "height": 720,
        "source_images": {s["room_id"]: room_image(listing, s["room_id"]) for s in stops},
    }
    update_manifest(lid, entry)
    log(f"★ {lid} DONE → {entry['url']} ({meta['duration_s']}s, {len(stops)} clips, failed={failed})")
    return {"id": lid, "ok": True, "url": entry["url"], "duration_s": meta["duration_s"],
            "clips": len(stops), "failed": failed}


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("specs", nargs="+", help="LISTING_ID[:ext|:full|:room+room+...]")
    ap.add_argument("--concurrency", type=int, default=12)
    ap.add_argument("--model", default="", help="force a single Veo model id")
    args = ap.parse_args(argv)

    catalog = load_catalog()
    models = [args.model] if args.model else list(DEFAULT_MODELS)
    specs = [parse_spec(s) for s in args.specs]
    for sp in specs:
        if sp["id"] not in catalog:
            log(f"unknown listing {sp['id']}")
            return 2

    results: Dict[str, Dict[str, Dict[str, Any]]] = {sp["id"]: {} for sp in specs}
    pending = {sp["id"]: len(sp["stops"]) for sp in specs}
    summaries: List[Dict[str, Any]] = []
    with cf.ThreadPoolExecutor(max_workers=max(1, args.concurrency)) as pool, \
            cf.ThreadPoolExecutor(max_workers=2) as stitch_pool:
        futs = {}
        for sp in specs:  # submission order = priority order
            listing = catalog[sp["id"]]
            for room_id in sp["stops"]:
                url = room_image(listing, room_id)
                out = WORK / sp["id"] / f"{room_id}.mp4"
                fut = pool.submit(generate_clip, sp["id"], room_id, url, out, models)
                futs[fut] = (sp, room_id)
        log(f"submitted {len(futs)} Veo clip jobs for {len(specs)} listing(s), concurrency={args.concurrency}")
        stitch_futs = []
        for fut in cf.as_completed(futs):
            sp, room_id = futs[fut]
            try:
                res = fut.result()
            except Exception as e:  # noqa: BLE001
                res = {"ok": False, "error": str(e)}
            if not res.get("ok"):
                log(f"  ✗ {sp['id']}/{room_id} failed: {res.get('error', '')[:200]}")
            results[sp["id"]][room_id] = res
            pending[sp["id"]] -= 1
            if pending[sp["id"]] == 0:
                used = [r.get("model", "") for r in results[sp["id"]].values()]
                stitch_futs.append(stitch_pool.submit(
                    finish_listing, catalog[sp["id"]], sp, results[sp["id"]], used))
        for sf in stitch_futs:
            try:
                summaries.append(sf.result())
            except Exception as e:  # noqa: BLE001
                log(f"✗ stitch/upload failed: {e}")
                summaries.append({"ok": False, "error": str(e)})
    log("SUMMARY " + json.dumps(summaries))
    return 0 if all(s.get("ok") for s in summaries) else 1


if __name__ == "__main__":
    sys.exit(main())
