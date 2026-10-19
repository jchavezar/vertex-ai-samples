"""Unified FastAPI Server for Rocket Companies × Google Gemini Next-Gen 4-Pillar AI Studio."""

import asyncio
import base64
import hashlib
import hmac
import importlib.util
import json
import os
import time
from pathlib import Path
from fastapi import FastAPI, Form, Request, WebSocket
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from google.genai import types

from ui_studio import render_4pillars_studio

BASE_DIR = Path(__file__).resolve().parent


def _load_module(name: str, rel_path: str):
    spec = importlib.util.spec_from_file_location(name, str(BASE_DIR / rel_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


p1_engine = _load_module("p1_engine", "pillar-1-bqml-timesfm/engine.py")
p2_engine = _load_module("p2_engine", "pillar-2-veo-reels-studio/engine.py")
p3_engine = _load_module("p3_engine", "pillar-3-trimodal-grounding/engine.py")
p4_engine = _load_module("p4_engine", "pillar-4-live-api-avatar/engine.py")
p5_engine = _load_module("p5_engine", "pillar-5-realestate-marketplace/engine.py")

app = FastAPI(title="Rocket Next-Gen 4-Pillar Gemini Studio")

STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

AUTH_USER = os.environ.get("ROCKET_USER") or os.environ.get("ROCKET_AUTH_USER", "rocket")
AUTH_PASS = os.environ.get("ROCKET_PASS") or os.environ.get("ROCKET_AUTH_PASS", "Argon2026!")
AUTH_SECRET = os.environ.get("ROCKET_SECRET", "rocket-nextgen-4pillars-secret-2026")
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "vtxdemos")
GCS_MEDIA_BUCKET = os.environ.get("GCS_MEDIA_BUCKET", "vtxdemos-abnb-images")
COOKIE_NAME = "rocket_4pillars_auth"
_TTS_CACHE = {}


@app.on_event("startup")
async def _warm_engines():
    try:
        p4_engine.get_warm_live_client()
        p5_engine.get_catalog()
    except Exception:
        pass


def _make_token(username: str) -> str:
    sig = hmac.new(AUTH_SECRET.encode(), username.encode(), hashlib.sha256).hexdigest()[:24]
    return f"{username}:{sig}"


def _verify_token(token: str | None) -> bool:
    if not token or ":" not in token:
        return False
    user, _ = token.split(":", 1)
    return hmac.compare_digest(token, _make_token(user))


def _is_authed(req: Request) -> bool:
    return _verify_token(req.cookies.get(COOKIE_NAME)) or _verify_token(req.query_params.get("auth_token"))


LOGIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" /><meta name="viewport" content="width=device-width,initial-scale=1.0" />
  <title>Rocket × Google Gemini · Next-Gen 4-Pillar Studio Login</title>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;700;800&display=swap" rel="stylesheet">
  <style>
    body { margin:0; font-family:'Plus Jakarta Sans',sans-serif; background:#090D16; color:#F8FAFC; display:flex; align-items:center; justify-content:center; min-height:100vh; }
    .card { width:100%; max-width:410px; background:#111827; border:1px solid #1E293B; border-radius:20px; padding:32px; box-shadow:0 24px 60px rgba(0,0,0,0.5); }
    .logo { width:44px; height:44px; border-radius:12px; background:#D81E28; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:20px; margin-bottom:16px; }
    input { width:100%; padding:12px 14px; border-radius:10px; border:1px solid #334155; background:#0F172A; color:#FFF; margin-top:6px; margin-bottom:14px; font-size:14px; box-sizing:border-box; }
    button { width:100%; padding:13px; border:none; border-radius:10px; background:#D81E28; color:#FFF; font-weight:800; font-size:14px; cursor:pointer; }
  </style>
</head>
<body>
  <form class="card" method="POST" action="/login">
    <div class="logo">R</div>
    <h1 style="font-size:20px;margin:0 0 6px;">Rocket Next-Gen 4-Pillar Studio</h1>
    <p style="font-size:12.5px;color:#94A3B8;margin:0 0 20px;">1. BQML TimesFM · 2. Veo 3.1 Reels · 3. Maps/YT/Search · 4. Live Avatar &amp; Screen Co-Pilot</p>
    <label style="font-size:12px;font-weight:700;">Username</label>
    <input type="text" name="username" value="rocket" required />
    <label style="font-size:12px;font-weight:700;">Password</label>
    <input type="password" name="password" placeholder="••••••••••" required autofocus />
    <button type="submit">Enter 4-Pillar Studio</button>
  </form>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    no_cache = {"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"}
    if not _is_authed(request):
        return HTMLResponse(LOGIN_HTML, headers=no_cache)
    resp = HTMLResponse(render_4pillars_studio(), headers=no_cache)
    q_token = request.query_params.get("auth_token")
    if q_token and _verify_token(q_token) and not _verify_token(request.cookies.get(COOKIE_NAME)):
        resp.set_cookie(COOKIE_NAME, q_token, httponly=True, max_age=86400 * 7, samesite="lax")
    return resp


@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    if username == AUTH_USER and password == AUTH_PASS:
        resp = RedirectResponse(url="/", status_code=303)
        resp.set_cookie(COOKIE_NAME, _make_token(username), httponly=True, max_age=86400 * 7, samesite="lax")
        return resp
    return HTMLResponse(LOGIN_HTML, status_code=401)


@app.get("/healthz")
async def healthz():
    return {"ok": True, "service": "rocket-nextgen-4pillars", "version": "v2"}


@app.get("/api/models/verify")
async def api_models_verify():
    return {
        "project": "vtxdemos (Argolis Internal Allowlisted)",
        "models": {
            "pillar_1_timeseries": "BigQuery ML AI.FORECAST (TimesFM 2.0)",
            "pillar_2_video_image": "veo-3.1-generate-001 (us-central1) + imagen-4.0-generate-001 + gemini-3.8-flash (global)",
            "pillar_3_grounding": "gemini-4-argon (global) + gemini-3.8-flash (global) [GoogleMaps + YouTube URI + GoogleSearch]",
            "pillar_4_live_screen_copilot": "gemini-3.8-live (us-central1, v1beta1) + Real-Time Function Calling + Computer-Use Ghost Cursor",
            "computer_use_agent": "gemini-3.8-flash-computer-use",
        },
        "gcp_maps_api_key_resource": "projects/254356041555/locations/global/keys/211f59cf-285e-49fa-b899-4fa64a52e75a",
    }


# -------------------------------------------------------------------------
# PILLAR 1: BIGQUERY ML TIMESFM (`AI.FORECAST`)
# -------------------------------------------------------------------------
@app.post("/api/pillar1/forecast")
async def api_p1_forecast(request: Request):
    if not _is_authed(request):
        return JSONResponse({"ok": False, "error": "Unauthorized"}, status_code=401)
    body = await request.json()
    res = p1_engine.run_timesfm_forecast(
        metric_id=body.get("metric_id", "mrcooper_refi_locks"),
        horizon=int(body.get("horizon", 12)),
        confidence_level=float(body.get("confidence_level", 0.90)),
        rate_shock_bps=int(body.get("rate_shock_bps", -50)),
    )
    return JSONResponse(res)


# -------------------------------------------------------------------------
# PILLAR 2: VEO 3.1 REELS STUDIO
# -------------------------------------------------------------------------
@app.get("/api/pillar2/presets")
async def api_p2_presets_list(request: Request):
    if not _is_authed(request):
        return JSONResponse({"ok": False, "error": "Unauthorized"}, status_code=401)
    return JSONResponse({"ok": True, "count": len(p2_engine.PRESET_REELS), "presets": list(p2_engine.PRESET_REELS.values())})


@app.get("/api/pillar2/preset/{preset_id}")
async def api_p2_preset(preset_id: str, request: Request):
    if not _is_authed(request):
        return JSONResponse({"ok": False, "error": "Unauthorized"}, status_code=401)
    preset = p2_engine.PRESET_REELS.get(preset_id, p2_engine.PRESET_REELS["royal_oak"])
    return JSONResponse(preset)


@app.post("/api/pillar2/generate")
async def api_p2_generate(request: Request):
    if not _is_authed(request):
        return JSONResponse({"ok": False, "error": "Unauthorized"}, status_code=401)
    body = await request.json()
    res = await asyncio.to_thread(
        p2_engine.generate_reel_from_text,
        prompt_text=body.get("prompt_text", "Modern home in Royal Oak MI"),
        price=int(body.get("price", 460000)),
        rate_pct=float(body.get("rate_pct", 5.875)),
        down_pct=int(body.get("down_pct", 10)),
        voice=body.get("voice", "Aoede"),
        generate_live_veo_mp4=bool(body.get("generate_live_veo_mp4", False)),
        static_reels_dir=str(STATIC_DIR / "reels"),
        current_video_url=str(body.get("current_video_url", "")),
    )
    return JSONResponse(res)


# -------------------------------------------------------------------------
# PILLAR 3: TRI-MODAL GROUNDING (GOOGLE MAPS + YOUTUBE + GOOGLE SEARCH)
# -------------------------------------------------------------------------
@app.post("/api/pillar3/ground")
async def api_p3_ground(request: Request):
    if not _is_authed(request):
        return JSONResponse({"ok": False, "error": "Unauthorized"}, status_code=401)
    body = await request.json()
    res = p3_engine.run_trimodal_grounding(
        hub_id=body.get("hub_id", "royal_oak"),
        custom_maps_query=body.get("custom_maps_query", ""),
        custom_search_query=body.get("custom_search_query", ""),
        custom_youtube_url=body.get("custom_youtube_url", ""),
    )
    return JSONResponse(res)


@app.post("/api/pillar3/chat")
async def api_p3_chat(request: Request):
    """Ask Redfin 2.0 grounded chat: NDJSON stream of status | delta | sources | done events."""
    from fastapi.responses import StreamingResponse
    if not _is_authed(request):
        return JSONResponse({"ok": False, "error": "Unauthorized"}, status_code=401)
    try:
        body = await request.json()
    except Exception:
        body = {}
    messages = body.get("messages") if isinstance(body.get("messages"), list) else []

    async def _ndjson():
        try:
            async for evt in p3_engine.stream_grounded_chat(
                messages=messages,
                hub_id=str(body.get("hub_id") or "royal_oak"),
                youtube_url=str(body.get("youtube_url") or ""),
            ):
                yield json.dumps(evt, ensure_ascii=False) + "\n"
        except asyncio.CancelledError:
            raise
        except Exception as e:  # never break the NDJSON contract
            yield json.dumps({"type": "delta", "text": "Grounding is briefly unavailable, please try again."}) + "\n"
            yield json.dumps({"type": "done", "latency_ms": 0, "model": "gemini-3.8-flash", "error": str(e)[:200]}) + "\n"

    return StreamingResponse(
        _ndjson(),
        media_type="application/x-ndjson",
        headers={"Cache-Control": "no-cache, no-transform", "X-Accel-Buffering": "no"},
    )


# -------------------------------------------------------------------------
# PILLAR 5: AI REAL ESTATE & HYBRID VECTOR MARKETPLACE (108 HOMES + CDN)
# -------------------------------------------------------------------------
@app.post("/api/pillar5/search")
async def api_p5_search(request: Request):
    if not _is_authed(request):
        return JSONResponse({"ok": False, "error": "Unauthorized"}, status_code=401)
    body = await request.json()
    res = p5_engine.hybrid_search_marketplace(
        query_text=body.get("query_text", ""),
        beds_filter=int(body.get("beds_filter", 0)),
        family_filter=body.get("family_filter", "all"),
        max_price=int(body.get("max_price", 3500000)),
        reference_listing_id=body.get("reference_listing_id", ""),
        reference_image_b64=body.get("reference_image_b64", ""),
        semantic_weight=float(body.get("semantic_weight", 0.45)),
        visual_weight=float(body.get("visual_weight", 0.35)),
        keyword_weight=float(body.get("keyword_weight", 0.20)),
        limit=int(body.get("limit", 108)),
    )
    return JSONResponse(res)


@app.post("/api/pillar5/evaluate")
async def api_p5_evaluate(request: Request):
    if not _is_authed(request):
        return JSONResponse({"ok": False, "error": "Unauthorized"}, status_code=401)
    body = await request.json()
    listing_id = body.get("listing_id", "RKT-001")
    fresh = bool(body.get("fresh", False))
    try:
        res = p5_engine.evaluate_listing_live_with_gemini(listing_id=listing_id, fresh=fresh)
    except TypeError:
        res = p5_engine.evaluate_listing_live_with_gemini(listing_id=listing_id)
    return JSONResponse(res)


# Pre-rendered tours: cinematic walkthroughs (pillar-5-realestate-marketplace/render_tours.py)
# and Veo 3.1 AI walkthroughs, both shaped {listing_id: {url, poster, duration_s, chapters: [...]}}.
_TOURS_MANIFEST_PATH = STATIC_DIR / "tours_manifest.json"
_VEO_MANIFEST_PATH = STATIC_DIR / "veo_tours_manifest.json"
_VEO_MANIFEST_GCS = os.environ.get(
    "VEO_MANIFEST_GCS_URL",
    f"https://storage.googleapis.com/{GCS_MEDIA_BUCKET}/tours/veo/veo_tours_manifest.json",
)
_TOURS_CACHE: dict = {"t": 0.0, "data": None}
_TOURS_LOCK = asyncio.Lock()


def _tour_entries(raw) -> dict:
    """Keeps only {id: {url, ...}} entries; accepts a bare map or a {"tours": {...}} wrapper."""
    if isinstance(raw, dict) and isinstance(raw.get("tours"), dict):
        raw = raw["tours"]
    if not isinstance(raw, dict):
        return {}
    return {k: v for k, v in raw.items() if isinstance(v, dict) and v.get("url")}


def _read_tour_file(path: Path) -> dict:
    try:
        return _tour_entries(json.loads(path.read_text()))
    except Exception:
        return {}


def _fetch_gcs_veo_manifest() -> dict:
    import urllib.request
    try:
        req = urllib.request.Request(f"{_VEO_MANIFEST_GCS}?ts={int(time.time())}", headers={"Cache-Control": "no-cache"})
        with urllib.request.urlopen(req, timeout=3) as r:
            return _tour_entries(json.loads(r.read().decode("utf-8")))
    except Exception:
        return {}


async def _get_tours_manifest(force: bool = False) -> dict:
    """Merges the cinematic + Veo manifests (local files + GCS mirror) with a 30 s cache."""
    now = time.time()
    cached = _TOURS_CACHE.get("data")
    if not force and cached is not None and now - _TOURS_CACHE["t"] < 30:
        return cached
    async with _TOURS_LOCK:
        cached = _TOURS_CACHE.get("data")
        if not force and cached is not None and time.time() - _TOURS_CACHE["t"] < 30:
            return cached
        cinematic = _read_tour_file(_TOURS_MANIFEST_PATH)
        veo = _read_tour_file(_VEO_MANIFEST_PATH)
        veo.update(await asyncio.to_thread(_fetch_gcs_veo_manifest))
        data = {"cinematic": cinematic, "veo": veo, "generated_at": int(time.time())}
        _TOURS_CACHE.update(t=time.time(), data=data)
        return data


@app.get("/api/pillar5/tours-manifest")
async def api_p5_tours_manifest(request: Request):
    if not _is_authed(request):
        return JSONResponse({"ok": False, "error": "Unauthorized"}, status_code=401)
    data = await _get_tours_manifest(force=request.query_params.get("refresh") == "1")
    return JSONResponse(data, headers={"Cache-Control": "no-store"})


@app.get("/api/pillar5/listing-video/{listing_id}")
async def api_p5_listing_video(listing_id: str, request: Request):
    """Serves THAT listing's 16:9 (or 9:16) H.264 tour.

    Pre-rendered tours (static/tours_manifest.json, Veo via ?source=veo) redirect to
    Cloud Storage instantly; anything else falls back to a fast on-demand ffmpeg build.
    """
    from fastapi.responses import FileResponse
    import urllib.request
    import subprocess
    raw_aspect = (request.query_params.get("aspect", "16x9") or "16x9").replace(":", "x").lower()
    aspect = "9x16" if raw_aspect == "9x16" else "16x9"
    safe_id = "".join(c for c in listing_id if c.isalnum() or c in ("-", "_")) or "RKT-001"

    if aspect == "16x9" and request.query_params.get("live") != "1":
        tours = await _get_tours_manifest()
        source = request.query_params.get("source", "cinematic")
        order = ("veo", "cinematic") if source == "veo" else ("cinematic", "veo")
        for kind in order:
            entry = tours.get(kind, {}).get(safe_id)
            if entry and entry.get("url"):
                return RedirectResponse(entry["url"], status_code=302, headers={"Cache-Control": "no-store"})

    out_dir = Path("/tmp/rocket_listing_videos")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_mp4 = out_dir / f"{safe_id}_{aspect}.mp4"
    if out_mp4.exists() and out_mp4.stat().st_size > 10000:
        return FileResponse(str(out_mp4), media_type="video/mp4")

    def _build_listing_mp4() -> str:
        cat = p5_engine.get_catalog()
        items = cat.get("announcements", [])
        target = next((x for x in items if x.get("id") == safe_id), items[0] if items else None)
        if not target:
            return ""
        rooms_by_id = {r.get("room_id"): r.get("image_url") for r in target.get("rooms", [])}
        ordered_urls = [rooms_by_id[k] for k in (
            "ext_front", "living_room", "chef_kitchen", "dining_room", "primary_bedroom",
            "primary_bathroom", "ext_rear", "ext_aerial") if rooms_by_id.get(k)]
        if not ordered_urls:
            ordered_urls = [r.get("image_url") for r in target.get("rooms", [])[:8] if r.get("image_url")]
        work_dir = out_dir / f"work_{safe_id}_{aspect}"
        work_dir.mkdir(parents=True, exist_ok=True)
        img_paths = []
        for idx, url in enumerate(ordered_urls[:8]):
            p = work_dir / f"img_{idx:02d}.jpg"
            if not p.exists():
                try:
                    urllib.request.urlretrieve(url, str(p))
                except Exception:
                    continue
            if p.exists() and p.stat().st_size > 500:
                img_paths.append(p)
        if not img_paths:
            return ""
        w, h = (1280, 720) if aspect == "16x9" else (720, 1280)
        sw, sh = int(w * 1.12) // 2 * 2, int(h * 1.12) // 2 * 2
        dur = 3.4
        inputs, filter_parts = [], []
        for i, p in enumerate(img_paths):
            inputs.extend(["-loop", "1", "-framerate", "30", "-t", str(dur), "-i", str(p)])
            # Cheap lateral dolly (time-based crop, no zoompan / upscale), alternating direction.
            xexpr = f"(in_w-out_w)*(t/{dur})" if i % 2 == 0 else f"(in_w-out_w)*(1-t/{dur})"
            filter_parts.append(
                f"[{i}:v]scale={sw}:{sh}:force_original_aspect_ratio=increase,crop={sw}:{sh},"
                f"crop={w}:{h}:x='{xexpr}':y='(in_h-out_h)/2',setsar=1,format=yuv420p[v{i}]"
            )
        concat_in = "".join(f"[v{i}]" for i in range(len(img_paths)))
        filter_complex = ";".join(filter_parts) + f";{concat_in}concat=n={len(img_paths)}:v=1:a=0[outv]"
        tmp_mp4 = out_mp4.with_suffix(".tmp.mp4")
        cmd = [
            "ffmpeg", "-y", *inputs,
            "-filter_complex", filter_complex,
            "-map", "[outv]",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", "-threads", "0",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-f", "mp4",
            str(tmp_mp4),
        ]
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
        except Exception:
            return ""
        if tmp_mp4.exists() and tmp_mp4.stat().st_size > 10000:
            tmp_mp4.replace(out_mp4)
            return str(out_mp4)
        return ""

    built = await asyncio.to_thread(_build_listing_mp4)
    if built and Path(built).exists():
        return FileResponse(built, media_type="video/mp4")
    return JSONResponse({"ok": False, "error": "Failed to build listing video"}, status_code=500)


# -------------------------------------------------------------------------
# OUT-OF-ORDER ASYNC SUBAGENT FAN-OUT ROUTER (`gemini-3.8-flash` / `Flash-Next`)
# -------------------------------------------------------------------------
def _classify_subagent_route(prompt_text: str, preferred_model: str = "auto") -> dict:
    s = (prompt_text or "").lower()
    if preferred_model and preferred_model not in ("auto", ""):
        model_label = preferred_model
    elif any(w in s for w in ("deep", "audit", "underwriting", "trid", "econometric", "disparate", "architecture")):
        model_label = "gemini-4-argon"
    elif any(w in s for w in ("lite", "fastest", "micro", "ping")):
        model_label = "gemini-3.8-flash-lite"
    else:
        # Default fast questions, lookups, GCP prerequisites, rate math & concierge Q&A to Flash-Next!
        model_label = "gemini-3.8-flash"

    if any(w in s for w in ("gcp", "service", "enable", "api", "iam", "prerequisite", "hackathon", "deploy")):
        role = "GCP Prerequisites & IAM Subagent"
        kind = "gcp_prereq"
    elif any(w in s for w in ("timesfm", "forecast", "shock", "bps", "cooper", "refi wave", "pillar 1")):
        role = "BQML TimesFM 2.0 Forecast Subagent"
        kind = "pillar1_forecast"
    elif any(w in s for w in ("colonial", "coastal", "craftsman", "mid-century", "midcentury", "loft", "desert", "house", "home", "bedroom", "beds", "airbnb", "map", "pillar 5", "under $")):
        role = "Pillar 5 Hybrid Vector Search Subagent"
        kind = "pillar5_search"
    elif any(w in s for w in ("maps", "youtube", "grounding", "tax", "mshda", "pillar 3")):
        role = "Tri-Modal Grounding Subagent"
        kind = "pillar3_grounding"
    elif any(w in s for w in ("veo", "reel", "video", "tiktok", "pillar 2")):
        role = "Veo 3.1 Reel Studio Subagent"
        kind = "pillar2_reel"
    else:
        role = "Flash-Next Instant Q&A Subagent"
        kind = "flash_qa"

    return {"role": role, "kind": kind, "model_label": model_label}


@app.post("/api/async-subagents/decompose")
async def api_decompose_subagents(request: Request):
    """Splits a multi-intent prompt or array of simultaneous prompts into independent parallel subagent specs."""
    if not _is_authed(request):
        return JSONResponse({"ok": False, "error": "Unauthorized"}, status_code=401)
    payload = await request.json()
    raw_prompts = payload.get("prompts") or []
    single_prompt = (payload.get("prompt") or "").strip()
    preferred_model = (payload.get("preferred_model") or "auto").strip()

    tasks_raw = []
    if isinstance(raw_prompts, list) and raw_prompts:
        for p in raw_prompts:
            if str(p).strip():
                tasks_raw.append(str(p).strip())
    elif single_prompt:
        import re as _re
        parts = [
            p.strip()
            for p in _re.split(
                r"(?:\s*;\s*|\s*\|\|\s*|\n+|(?:\s+and\s+also\s+)|(?:\s+also\s+tell\s+me\s+)|(?:\s+plus\s+))",
                single_prompt,
                flags=_re.IGNORECASE,
            )
            if p and p.strip()
        ]
        tasks_raw = parts if len(parts) > 1 else [single_prompt]

    specs = []
    for idx, text in enumerate(tasks_raw[:6], 1):
        route = _classify_subagent_route(text, preferred_model)
        specs.append({
            "subagent_id": f"sub-{int(time.time()*1000)}-{idx}",
            "index": idx,
            "prompt": text,
            "role": route["role"],
            "kind": route["kind"],
            "model_label": route["model_label"],
        })
    return JSONResponse({"ok": True, "count": len(specs), "subagents": specs})


@app.post("/api/async-subagent")
async def api_run_async_subagent(request: Request):
    """Executes an independent subagent task asynchronously so multiple concurrent requests return in first-ready order."""
    if not _is_authed(request):
        return JSONResponse({"ok": False, "error": "Unauthorized"}, status_code=401)
    payload = await request.json()
    t0 = time.perf_counter()
    prompt_text = (payload.get("prompt") or "").strip()
    subagent_id = (payload.get("subagent_id") or f"sub-{int(time.time()*1000)}").strip()
    preferred_model = (payload.get("preferred_model") or "auto").strip()
    route = _classify_subagent_route(prompt_text, preferred_model)
    kind = route["kind"]
    model_label = route["model_label"]

    try:
        if kind == "gcp_prereq":
            answer = (
                "Enable 7 Google Cloud APIs (`aiplatform`, `bigquery`, `bigquerystorage`, `run`, `storage`, "
                "`cloudbuild`, `artifactregistry`) via `gcloud services enable`, grant 4 IAM roles (`aiplatform.user`, "
                "`bigquery.admin`, `storage.objectAdmin`, `run.invoker`), and ensure `GOOGLE_MAPS_API_KEY` + "
                "`gs://vtxdemos-abnb-images` CDN access are active."
            )
            return JSONResponse({
                "ok": True,
                "subagent_id": subagent_id,
                "role": route["role"],
                "kind": kind,
                "model": model_label,
                "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
                "answer": answer,
                "action_badge": "gcloud services enable (7 APIs) · 4 IAM Roles",
            })

        if kind == "pillar5_search":
            import re as _re
            s = prompt_text.lower()
            beds = 0
            bm = _re.search(r"\b([23456])\s*(?:bed|beds|bedroom|bedrooms|br)\b", s)
            if bm:
                beds = int(bm.group(1))
            fam = "all"
            if any(w in s for w in ("colonial", "georgian", "federal", "cape cod")):
                fam = "colonial_georgian"
            elif any(w in s for w in ("coastal", "villa", "beach", "waterfront", "hamptons")):
                fam = "coastal_villa"
            elif any(w in s for w in ("craftsman", "bungalow", "prairie")):
                fam = "modern_craftsman"
            elif any(w in s for w in ("mid-century", "midcentury", "glass", "cantilever")):
                fam = "midcentury_glass"
            elif any(w in s for w in ("brick", "timber", "loft", "warehouse")):
                fam = "brick_timber_loft"
            elif any(w in s for w in ("desert", "mountain", "scottsdale", "aspen")):
                fam = "desert_mountain"

            res = await asyncio.to_thread(
                p5_engine.hybrid_search_marketplace,
                query_text=prompt_text,
                beds_filter=beds,
                family_filter=fam,
                max_price=2500000,
                limit=6,
            )
            top = (res.get("results") or [None])[0]
            if top:
                answer = (
                    f"Matched {res.get('total_matched', 0)} distinct homes across our 108-house catalog. "
                    f"Top match: {top['title']} in {top['city']} (${top['price']:,} · {top['beds']} Beds · "
                    f"{top['baths']} Baths · {top['total_rooms_mapped']} coinciding rooms · "
                    f"${top['monthly_piti']:,}/mo PITI + ${top['closing_credit']:,} Rocket credit)."
                )
            else:
                answer = "Searched 108 distinct homes in Pillar 5 Hybrid Vector Marketplace."
            return JSONResponse({
                "ok": True,
                "subagent_id": subagent_id,
                "role": route["role"],
                "kind": kind,
                "model": model_label,
                "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
                "answer": answer,
                "action_badge": f"Pillar 5 Map Synced · {res.get('total_matched', 0)} Matches",
                "screen_action": {
                    "name": "control_realestate_marketplace",
                    "args": {"query_text": prompt_text, "beds_filter": beds, "family_filter": fam},
                },
            })

        if kind == "pillar1_forecast":
            import re as _re
            s = prompt_text.lower()
            shock = -75
            sm = _re.search(r"(-\d+)\s*(?:bps|basis)?", s)
            if sm:
                shock = max(-150, min(100, int(sm.group(1))))
            res = await asyncio.to_thread(
                p1_engine.run_timesfm_forecast,
                metric_id="mrcooper_refi_locks",
                horizon=12,
                confidence_level=0.90,
                rate_shock_bps=shock,
            )
            kpis = res.get("kpis") or {}
            answer = (
                f"BigQuery ML TimesFM 2.0 forecast complete for {shock} bps rate shock: "
                f"peak weekly volume reaches {int(kpis.get('peak_forecast', 0)):,} locks "
                f"({kpis.get('delta_pct', 0):+}% vs baseline), capturing "
                f"${kpis.get('est_value_usd', 0)/1e6:.1f}M in portfolio value."
            )
            return JSONResponse({
                "ok": True,
                "subagent_id": subagent_id,
                "role": route["role"],
                "kind": kind,
                "model": model_label,
                "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
                "answer": answer,
                "action_badge": f"BQML AI.FORECAST · {shock} bps",
                "screen_action": {
                    "name": "control_bqml_timesfm",
                    "args": {"rate_shock_bps": shock, "horizon": 12},
                },
            })

        # Default: Live Vertex AI Flash-Next (`gemini-3.8-flash` / `gemini-3.8-flash-lite` / `gemini-4-argon`) sub-second call!
        client = p4_engine.get_warm_live_client()
        if "lite" in model_label.lower():
            vertex_model = "gemini-3.8-flash-lite"
        elif "argon" in model_label.lower():
            vertex_model = "gemini-4-argon"
        else:
            vertex_model = "gemini-3.8-flash"
        sys_inst = (
            "You are a fast, executive Rocket Companies + Redfin + Mr. Cooper AI Subagent running on "
            f"{vertex_model}. Answer the user's question in 2-3 crisp, high-signal sentences with exact numbers."
        )
        resp = await asyncio.to_thread(
            client.models.generate_content,
            model=vertex_model,
            contents=prompt_text,
            config=types.GenerateContentConfig(
                system_instruction=sys_inst,
                temperature=0.2,
                max_output_tokens=220,
            ),
        )
        ans_txt = (getattr(resp, "text", None) or "").strip() or "Subagent task completed."
        return JSONResponse({
            "ok": True,
            "subagent_id": subagent_id,
            "role": route["role"],
            "kind": kind,
            "model": vertex_model,
            "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
            "answer": ans_txt,
            "action_badge": f"Vertex AI · {vertex_model}",
        })
    except Exception as exc:
        return JSONResponse({
            "ok": True,
            "subagent_id": subagent_id,
            "role": route["role"],
            "kind": kind,
            "model": model_label,
            "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
            "answer": f"Completed via {model_label}: {prompt_text} ({exc})",
            "action_badge": f"Fast Fallback · {model_label}",
        })


# -------------------------------------------------------------------------
# PILLAR 4: GEMINI LIVE API + AVATAR WEBSOCKETS
# -------------------------------------------------------------------------
@app.websocket("/ws/live-avatar")
async def ws_live_avatar(websocket: WebSocket):
    if not (_verify_token(websocket.cookies.get(COOKIE_NAME)) or _verify_token(websocket.query_params.get("auth_token"))):
        await websocket.close(code=1008)
        return
    await p4_engine.handle_live_avatar_ws(websocket)


@app.websocket("/ws/live-tts")
async def ws_live_tts(websocket: WebSocket):
    if not (_verify_token(websocket.cookies.get(COOKIE_NAME)) or _verify_token(websocket.query_params.get("auth_token"))):
        await websocket.close(code=1008)
        return
    await websocket.accept()
    try:
        raw = await websocket.receive_text()
        req = json.loads(raw)
        text = (req.get("text") or "").strip()
        voice = (req.get("voice") or "Aoede").strip()
        if not text:
            await websocket.send_json({"done": True})
            await websocket.close()
            return
        ckey = f"{voice}::{text}"
        if ckey in _TTS_CACHE:
            await websocket.send_json({"pcm_b64": _TTS_CACHE[ckey], "cached": True})
            await websocket.send_json({"done": True})
            await websocket.close()
            return

        client = p4_engine.get_warm_live_client()
        cfg = types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            system_instruction=types.Content(
                parts=[types.Part.from_text(text="Read the user's line warmly and verbatim with natural human pacing.")]
            ),
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice)
                )
            ),
        )
        acc = []
        async with client.aio.live.connect(model="gemini-3.8-live", config=cfg) as session:
            await session.send_client_content(
                turns=types.Content(role="user", parts=[types.Part.from_text(text=f"Speak verbatim: {text}")]),
                turn_complete=True,
            )
            async for resp in session.receive():
                sc = getattr(resp, "server_content", None)
                if not sc:
                    continue
                mt = getattr(sc, "model_turn", None)
                if mt and getattr(mt, "parts", None):
                    for part in mt.parts:
                        inl = getattr(part, "inline_data", None)
                        if inl and getattr(inl, "data", None):
                            acc.append(inl.data)
                            await websocket.send_json({"pcm_b64": base64.b64encode(inl.data).decode("ascii")})
                if getattr(sc, "turn_complete", False):
                    break
        if acc and len(_TTS_CACHE) < 64:
            _TTS_CACHE[ckey] = base64.b64encode(b"".join(acc)).decode("ascii")
        await websocket.send_json({"done": True})
        await websocket.close()
    except Exception as exc:
        try:
            await websocket.send_json({"error": str(exc), "done": True})
            await websocket.close()
        except Exception:
            pass
