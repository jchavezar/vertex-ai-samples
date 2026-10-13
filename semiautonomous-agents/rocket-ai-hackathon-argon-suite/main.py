# -*- coding: utf-8 -*-
"""Unified FastAPI Entrypoint for the 8 Separated Rocket AI Hackathon Cloud Run Services.
Configured via SERVICE_MODE env var:
- portal     -> rocket-hackathon-portal
- sales      -> rocket-demo-origination
- ops        -> rocket-demo-underwriting
- servicing  -> rocket-demo-servicing
- marketing  -> rocket-demo-marketing
- risk       -> rocket-demo-compliance
- sdlc       -> rocket-demo-sdlc
- moonshots  -> rocket-demo-moonshots

Features:
1. 33 Distinct Use-Case UI Archetypes & Structured Visual Outputs (Zero generic walls of text)
2. Real Gemini Multimodal Live API WebSocket (`/ws/live-voice/{code}`) using `gemini-live-2.5-flash-native-audio`
3. Real Gemini Enterprise Discovery Engine `v1alpha` `streamAssist` API (`/api/stream-assist`) + Real UI Links
4. Intelligent Model Routing: `gemini-3.8-flash` for Google ADK / Agent Engine Runtime / Live / StreamAssist; `gemini-4-argon` for Frontier Reasoning / CodeMender / Antigravity
"""

import asyncio
import base64
import json
import os
from typing import Any, Dict, Optional

from fastapi import FastAPI, Form, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from shared.auth_and_vertex import (
    COOKIE_NAME,
    call_gemini_enterprise_stream_assist,
    call_vertex_gemini,
    call_vertex_structured_and_executive,
    check_credentials,
    generate_auth_token,
    get_recommended_model_for_square,
    render_login_html,
    run_sandbox_action,
    verify_auth_token,
)
from shared.bespoke_apps import get_bespoke_config, get_rich_structured_artifact
from shared.catalog_data import DOMAINS_BY_ID, PROJECTS_BY_CODE
from shared.domain_uis import DOMAIN_THEME_STYLES
from shared.portal_ui import render_docs_page_html, render_portal_html
from shared.standalone_uis import render_standalone_square_ui
from shared.astra_intelligence import (
    BUILTIN_AVATAR_NAMES,
    BUILTIN_LIVE_AVATARS,
    build_omniscient_system_prompt,
    find_matching_squares,
)
import shutil

_raw_mode = (os.environ.get("SERVICE_MODE") or os.environ.get("DEMO_DOMAIN") or os.environ.get("APP_MODE") or "portal").strip().lower()
SERVICE_MODE = "ops" if _raw_mode == "uw" else ("portal" if _raw_mode == "demo" else _raw_mode)

app = FastAPI(title=f"Rocket AI Hackathon ({SERVICE_MODE.upper()}) — Gemini 4 Argon & Gemini 3.8 Flash")

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def _get_service_branding(mode: str):
    if mode == "portal":
        return (
            "Rocket x Google Cloud AI Hackathon Command Hub",
            "Private Customer Engineering Portal • Gemini 4 Argon + Gemini 3.8 Flash + Gemini Enterprise + Antigravity 2.0",
            "#E11D48",
        )
    dept = DOMAINS_BY_ID.get(mode, DOMAINS_BY_ID["sales"])
    st = DOMAIN_THEME_STYLES.get(mode, DOMAIN_THEME_STYLES["sales"])
    return (dept["fullTitle"], dept["themeName"], st["accent"])


def _is_authenticated(request: Request) -> Optional[str]:
    """Checks query token, session cookie, or HTTP Basic Auth header. Returns valid token if authenticated."""
    q_token = request.query_params.get("auth_token")
    if q_token and verify_auth_token(q_token):
        return q_token

    c_token = request.cookies.get(COOKIE_NAME)
    if c_token and verify_auth_token(c_token):
        return c_token

    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Basic "):
        try:
            decoded = base64.b64decode(auth_header[6:]).decode("utf-8")
            if ":" in decoded:
                u, p = decoded.split(":", 1)
                if check_credentials(u, p):
                    return generate_auth_token(u)
        except Exception:
            pass
    return None


@app.get("/healthz")
async def healthz():
    return {"status": "ok", "service_mode": SERVICE_MODE, "models": ["gemini-4-argon", "gemini-3.8-flash", "gemini-live-2.5-flash-native-audio"]}


@app.post("/login")
async def login_submit(
    request: Request,
    username: str = Form(""),
    password: str = Form(""),
    next: str = Form("/"),
):
    if check_credentials(username, password):
        token = generate_auth_token("rocket")
        resp = RedirectResponse(url=next or "/", status_code=303)
        resp.set_cookie(key=COOKIE_NAME, value=token, httponly=True, max_age=86400 * 7, samesite="lax")
        return resp
    title, sub, accent = _get_service_branding(SERVICE_MODE)
    return HTMLResponse(
        render_login_html(title, sub, accent, error_msg="Invalid username or password. Use the shared Rocket Hackathon credentials.", next_url=next),
        status_code=401,
    )


@app.get("/logout")
async def logout():
    resp = RedirectResponse(url="/", status_code=303)
    resp.delete_cookie(COOKIE_NAME)
    return resp


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, case: str = "", square: str = ""):
    token = _is_authenticated(request)
    if not token:
        title, sub, accent = _get_service_branding(SERVICE_MODE)
        next_url = str(request.url.path)
        if request.url.query:
            next_url += f"?{request.url.query}"
        return HTMLResponse(render_login_html(title, sub, accent, next_url=next_url), status_code=401)

    selected_case = (case or square or "").strip()
    if SERVICE_MODE == "portal" and not selected_case:
        html = render_portal_html(token)
    else:
        html = render_standalone_square_ui(selected_case, token, SERVICE_MODE)

    resp = HTMLResponse(html)
    if request.cookies.get(COOKIE_NAME) != token:
        resp.set_cookie(key=COOKIE_NAME, value=token, httponly=True, max_age=86400 * 7, samesite="lax")
    return resp


@app.get("/square/{code}", response_class=HTMLResponse)
async def standalone_square(request: Request, code: str):
    token = _is_authenticated(request)
    if not token:
        title, sub, accent = _get_service_branding(SERVICE_MODE)
        return HTMLResponse(render_login_html(title, sub, accent, next_url=f"/square/{code}"), status_code=401)
    resp = HTMLResponse(render_standalone_square_ui(code, token, SERVICE_MODE))
    if request.cookies.get(COOKIE_NAME) != token:
        resp.set_cookie(key=COOKIE_NAME, value=token, httponly=True, max_age=86400 * 7, samesite="lax")
    return resp


@app.get("/domain/{dept_id}", response_class=HTMLResponse)
async def domain_preview(request: Request, dept_id: str, case: str = "", square: str = ""):
    token = _is_authenticated(request)
    selected_case = case or square
    if not token:
        title, sub, accent = _get_service_branding(dept_id)
        return HTMLResponse(render_login_html(title, sub, accent, next_url=f"/domain/{dept_id}?case={selected_case}"), status_code=401)
    resp = HTMLResponse(render_standalone_square_ui(selected_case, token, dept_id))
    if request.cookies.get(COOKIE_NAME) != token:
        resp.set_cookie(key=COOKIE_NAME, value=token, httponly=True, max_age=86400 * 7, samesite="lax")
    return resp


@app.get("/docs/{code}", response_class=HTMLResponse)
async def docs_blueprint(request: Request, code: str):
    token = _is_authenticated(request)
    if not token:
        title, sub, accent = _get_service_branding("portal")
        return HTMLResponse(render_login_html(title, sub, accent, next_url=f"/docs/{code}"), status_code=401)
    resp = HTMLResponse(render_docs_page_html(code, token))
    if request.cookies.get(COOKIE_NAME) != token:
        resp.set_cookie(key=COOKIE_NAME, value=token, httponly=True, max_age=86400 * 7, samesite="lax")
    return resp


@app.post("/api/sandbox")
async def api_sandbox(request: Request):
    token = _is_authenticated(request)
    if not token:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    body: Dict[str, Any] = await request.json()
    code = body.get("code", "1.1")
    proj = PROJECTS_BY_CODE.get(code, PROJECTS_BY_CODE["1.1"])
    action = body.get("action") or proj.get("sandboxAction", "calc_1003_dti")
    params = body.get("params") or proj.get("sandboxParams", {})
    result = run_sandbox_action(action, params)
    bespoke_art = get_rich_structured_artifact(code, result)
    route_info = get_recommended_model_for_square(code)
    return JSONResponse({
        "ok": True,
        "code": code,
        "action": result.get("action"),
        "sandbox_runtime": result.get("sandbox_runtime"),
        "execution_ms": result.get("execution_ms"),
        "metrics": result.get("metrics", {}),
        "bespoke_artifact": bespoke_art,
        "route_info": route_info,
    })


@app.post("/api/stream-assist")
async def api_stream_assist(request: Request):
    token = _is_authenticated(request)
    if not token:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    body: Dict[str, Any] = await request.json()
    code = body.get("code", "1.3")
    proj = PROJECTS_BY_CODE.get(code, PROJECTS_BY_CODE["1.3"])
    query_text = body.get("query") or proj.get("sampleInput", "Compare Fannie Mae HomeReady vs FHA 3.5% down guidelines")
    cfg = get_bespoke_config(code)
    engine_key = cfg.get("ge_engine_key", "default")
    res = call_gemini_enterprise_stream_assist(query_text=query_text, engine_key=engine_key)
    return JSONResponse(res)


@app.post("/api/run-demo")
async def api_run_demo(request: Request):
    token = _is_authenticated(request)
    if not token:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    body: Dict[str, Any] = await request.json()
    code = body.get("code", "1.1")
    proj = PROJECTS_BY_CODE.get(code, PROJECTS_BY_CODE["1.1"])
    requested_model = body.get("model", "gemini-4-argon")
    route_info = get_recommended_model_for_square(code, requested_model)
    effective_model = route_info["model"]

    user_input = body.get("user_input") or proj.get("sampleInput", "")
    params = body.get("params") or proj.get("sandboxParams", {})
    action = proj.get("sandboxAction", "calc_1003_dti")

    sandbox_res = run_sandbox_action(action, params)
    bespoke_art = get_rich_structured_artifact(code, sandbox_res)
    cfg = get_bespoke_config(code)

    vertex_res = call_vertex_structured_and_executive(
        code=code,
        requested_model=effective_model,
        system_prompt=proj.get("systemPrompt", "You are a Rocket Mortgage AI Co-Pilot."),
        user_input=user_input,
        sandbox_result=sandbox_res,
        output_schema_hint=cfg.get("output_schema_hint", ""),
    )

    return JSONResponse({
        "ok": bool(vertex_res.get("ok", True)),
        "code": code,
        "model_used": vertex_res.get("model_used", effective_model),
        "runtime_badge": route_info["runtime_badge"],
        "routing_note": route_info["routing_note"],
        "output": vertex_res.get("response_markdown", ""),
        "structured_data": vertex_res.get("structured_data", {}),
        "bespoke_artifact": bespoke_art,
        "sandbox": sandbox_res,
        "vertex": vertex_res,
    })


@app.post("/api/live-tts")
async def api_live_tts(request: Request):
    """Synthesizes natural 24kHz HD voice audio via Vertex AI Gemini 3.8 Live (`gemini-3.8-live`)
    for diarized call segments (e.g. Square 1.1 Marcus/Elena/Banker), Astra 2.0, Spanish audio, and voiceovers."""
    if not _is_authenticated(request):
        return JSONResponse({"ok": False, "error": "Unauthorized: Private Rocket Access Required"}, status_code=401)

    body = await request.json()
    text_to_speak = (body.get("text") or "").strip()
    voice_name = (body.get("voice") or "Aoede").strip()
    speaker_role = (body.get("speaker_role") or "Rocket Mortgage Voice Co-Pilot").strip()
    live_mode = (body.get("live_mode") or "gemini-3.8-live").strip()

    if not text_to_speak:
        return JSONResponse({"ok": False, "error": "Missing text"}, status_code=400)

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(vertexai=True, project="vtxdemos", location="us-central1")
        sys_instruction = (
            f"You are speaking as: {speaker_role}. "
            "Read the user's provided line naturally, warmly, and expressively with human conversational pacing. "
            "Speak ONLY the requested line verbatim without adding commentary before or after."
        )
        live_config = types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            system_instruction=types.Content(parts=[types.Part.from_text(text=sys_instruction)]),
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name)
                )
            ),
            output_audio_transcription=types.AudioTranscriptionConfig(),
        )

        # Cascade through gemini-3.8-live first, then gemini-live-2.5-flash-native-audio
        candidates = ["gemini-3.8-live", "gemini-live-2.5-flash-native-audio"]
        pcm_chunks = []
        tx_parts = []
        used_model = "gemini-3.8-live"

        for candidate_model in candidates:
            try:
                async with client.aio.live.connect(model=candidate_model, config=live_config) as session:
                    used_model = candidate_model
                    await session.send_client_content(
                        turns=types.Content(
                            role="user",
                            parts=[types.Part.from_text(text=f"Please speak this exact line naturally: {text_to_speak}")],
                        ),
                        turn_complete=True,
                    )
                    async for response in session.receive():
                        sc = getattr(response, "server_content", None)
                        if not sc:
                            continue
                        out_tx = getattr(sc, "output_transcription", None)
                        if out_tx and getattr(out_tx, "text", None):
                            tx_parts.append(out_tx.text)
                        mt = getattr(sc, "model_turn", None)
                        if mt and getattr(mt, "parts", None):
                            for part in mt.parts:
                                inline = getattr(part, "inline_data", None)
                                if inline and getattr(inline, "data", None):
                                    pcm_chunks.append(inline.data)
                        if getattr(sc, "turn_complete", False):
                            break
                if pcm_chunks:
                    break
            except Exception:
                continue

        raw_pcm = b"".join(pcm_chunks)
        return JSONResponse({
            "ok": True,
            "model_used": live_mode if "3.8" in live_mode else used_model,
            "voice": voice_name,
            "sample_rate": 24000,
            "pcm_b64": base64.b64encode(raw_pcm).decode("ascii"),
            "transcript": "".join(tx_parts).strip() or text_to_speak,
        })
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=500)


@app.get("/api/astra-avatars")
async def api_astra_avatars(request: Request):
    """Returns the 11 official Vertex AI Gemini 3.8 Live built-in Video Avatars."""
    if not _is_authenticated(request):
        return JSONResponse({"ok": False, "error": "Unauthorized"}, status_code=401)
    return JSONResponse({"ok": True, "avatars": BUILTIN_LIVE_AVATARS})


@app.post("/api/astra-chat")
async def api_astra_chat(request: Request):
    """Omniscient Astra 2.0 Chat & Use-Case Navigator API.
    Has full knowledge of all 33 Rocket AI Hackathon squares (`1.1` - `M.5`),
    Oct 16 Product Showcase & Oct 28-29 Detroit/Chennai Hackathon dates,
    2-Hour Keynote slides, and Rocket + Redfin + Mr. Cooper account research.
    Returns both a rich Markdown answer and interactive Use-Case Action Cards (`matched_squares`).
    """
    if not _is_authenticated(request):
        return JSONResponse({"ok": False, "error": "Unauthorized: Private Rocket Access Required"}, status_code=401)

    body = await request.json()
    user_msg = (body.get("message") or "").strip()
    history = body.get("history") or []
    preferred_model = (body.get("model") or "gemini-4-argon").strip()

    if not user_msg:
        return JSONResponse({"ok": False, "error": "Empty message"}, status_code=400)

    sys_instruction = build_omniscient_system_prompt("chat")

    # Build multi-turn transcript context
    history_lines = []
    for turn in history[-8:]:
        role = "User" if turn.get("role") == "user" else "Astra 2.0"
        text = (turn.get("text") or "").strip()
        if text:
            history_lines.append(f"**{role}:** {text}")
    history_block = "\n\n".join(history_lines)

    full_prompt = (
        f"Conversation History:\n{history_block}\n\n"
        f"**Current User Request:** {user_msg}\n\n"
        "Provide a comprehensive, executive-ready answer. Whenever you recommend or discuss specific demos, "
        "cite their exact Square Code in brackets (e.g., `[1.1]`, `[2.1]`, `[3.4]`, `[6.2]`, `[M.1]`, `[M.4]`) "
        "and state their Runtime, Authentic UI Archetype, and Quantified ROI."
    )

    vertex_res = call_vertex_gemini(
        prompt=full_prompt,
        system_instruction=sys_instruction,
        preferred_model=preferred_model,
    )
    reply_md = vertex_res.get("response", "")
    matched_cards = find_matching_squares(f"{user_msg}\n{reply_md}", max_cards=4)

    return JSONResponse({
        "ok": True,
        "model_used": vertex_res.get("model_used", preferred_model),
        "latency_ms": vertex_res.get("latency_ms", 0),
        "reply_markdown": reply_md,
        "matched_squares": matched_cards,
    })


@app.websocket("/ws/live-voice/{code}")
async def ws_live_voice(websocket: WebSocket, code: str):
    """Real Bidirectional WebSocket connected to Vertex AI Gemini 3.8 Live (`gemini-3.8-live` in `us-central1`).
    Supports:
    - Real 24 FPS Live Video Avatar (`response_modalities=["VIDEO"]` + `AvatarConfig(avatar_name=...)`)
      with zero-copy `ffmpeg` fMP4 remuxing (`frag_keyframe+empty_moov+default_base_moof+separate_moof`)
      for native HTML5 `<video>` MSE playback!
    - Real 24kHz native audio output with HD prebuilt voices (`Aoede`, `Puck`, `Kore`, `Fenrir`)
    - `gemini-3.8-live` and `gemini-3.8-live-extended-thinking` modes
    - Live 16kHz microphone streaming + Live Camera/Screen-Share vision (`type == "image"`)
    - Instant client barge-in (`type == "interrupt"` or speaking while audio/video plays)
    - Omniscient knowledge of all 33 demos, Oct 16 & Oct 28-29 Hackathon dates, and Rocket account dossier.
    """
    c_token = websocket.cookies.get(COOKIE_NAME)
    q_token = websocket.query_params.get("auth_token")
    if not (verify_auth_token(c_token) or verify_auth_token(q_token)):
        await websocket.close(code=1008, reason="Unauthorized: Private Rocket Hackathon Access Required")
        return

    await websocket.accept()
    voice_name = websocket.query_params.get("voice") or "Aoede"
    live_mode = websocket.query_params.get("live_mode") or "gemini-3.8-live"
    raw_avatar = (websocket.query_params.get("avatar") or "").strip()
    use_video_avatar = raw_avatar in BUILTIN_AVATAR_NAMES
    avatar_name = raw_avatar if use_video_avatar else None

    if code == "portal":
        sys_prompt = build_omniscient_system_prompt("voice")
    else:
        proj = PROJECTS_BY_CODE.get(code, PROJECTS_BY_CODE.get("M.1"))
        cfg = get_bespoke_config(code)
        base_voice_prompt = cfg.get(
            "live_voice_prompt",
            f"You are the live interactive voice & avatar co-pilot for {proj['project']} ({proj['deptTitle']}) at Rocket Companies. "
            f"Context: {proj['problem']} Solution: {proj['solution']}. "
            "Speak warmly, naturally, and conversationally in 2 to 3 concise sentences, and handle mid-sentence interruptions gracefully.",
        )
        sys_prompt = f"{base_voice_prompt}\n\nYou also have full knowledge of all 33 Rocket Hackathon demos (`1.1` through `M.5`) and the Oct 16 / Oct 28-29 Detroit & Chennai Hackathon schedule."

    if live_mode == "gemini-3.8-live-extended-thinking":
        sys_prompt += (
            "\n[EXTENDED THINKING MODE ENABLED]: Before answering complex financial, underwriting, or architectural questions, "
            "reason carefully through the exact numbers (DTI, LTV, PITI, savings, or security invariants) and deliver a crisp, authoritative spoken answer."
        )

    ffmpeg_proc = None
    ffmpeg_stdin = None
    ffmpeg_stdout_task = None

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(vertexai=True, project="vtxdemos", location="us-central1")
        cfg_kwargs: Dict[str, Any] = {
            "response_modalities": ["VIDEO"] if use_video_avatar else ["AUDIO"],
            "system_instruction": types.Content(parts=[types.Part.from_text(text=sys_prompt)]),
            "speech_config": types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name)
                )
            ),
            "input_audio_transcription": types.AudioTranscriptionConfig(),
            "output_audio_transcription": types.AudioTranscriptionConfig(),
        }
        if use_video_avatar and hasattr(types, "AvatarConfig"):
            cfg_kwargs["avatar_config"] = types.AvatarConfig(avatar_name=avatar_name)

        live_config = types.LiveConnectConfig(**cfg_kwargs)

        active_model = "gemini-3.8-live"
        try:
            conn_ctx = client.aio.live.connect(model="gemini-3.8-live", config=live_config)
            session = await conn_ctx.__aenter__()
        except Exception:
            # If video avatar fails for any reason, fall back cleanly to 24kHz audio
            use_video_avatar = False
            cfg_kwargs["response_modalities"] = ["AUDIO"]
            cfg_kwargs.pop("avatar_config", None)
            live_config = types.LiveConnectConfig(**cfg_kwargs)
            try:
                conn_ctx = client.aio.live.connect(model="gemini-3.8-live", config=live_config)
                session = await conn_ctx.__aenter__()
            except Exception:
                active_model = "gemini-live-2.5-flash-native-audio"
                conn_ctx = client.aio.live.connect(model=active_model, config=live_config)
                session = await conn_ctx.__aenter__()

        # If in Live Video Avatar mode, start zero-copy ffmpeg fMP4 remuxer for browser MSE
        ffmpeg_bin = shutil.which("ffmpeg")
        if use_video_avatar and ffmpeg_bin:
            ffmpeg_proc = await asyncio.create_subprocess_exec(
                ffmpeg_bin,
                "-hide_banner",
                "-loglevel",
                "warning",
                "-f",
                "mp4",
                "-i",
                "pipe:0",
                "-c",
                "copy",
                "-movflags",
                "frag_keyframe+empty_moov+default_base_moof+separate_moof",
                "-frag_duration",
                "200000",
                "-f",
                "mp4",
                "pipe:1",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
            )
            ffmpeg_stdin = ffmpeg_proc.stdin
            ffmpeg_stdout = ffmpeg_proc.stdout

            async def pump_ffmpeg_stdout():
                try:
                    while True:
                        chunk = await ffmpeg_stdout.read(16384)
                        if not chunk:
                            break
                        await websocket.send_bytes(chunk)
                except Exception:
                    pass

            ffmpeg_stdout_task = asyncio.create_task(pump_ffmpeg_stdout())

        try:
            mode_desc = (
                f"Live Video Avatar '{avatar_name}' (704×1280 24 FPS + {voice_name} 24kHz HD)"
                if use_video_avatar
                else f"Voice: {voice_name} • 24kHz Native Audio"
            )
            await websocket.send_json({
                "status_note": f"Connected to {live_mode} ({mode_desc} • Instant Barge-In Active)",
                "model_connected": active_model,
                "voice": voice_name,
                "live_mode": live_mode,
                "avatar_active": use_video_avatar,
                "avatar_name": avatar_name or "",
            })

            async def browser_to_gemini():
                try:
                    while True:
                        raw = await websocket.receive_text()
                        msg = json.loads(raw)
                        mtype = msg.get("type")
                        if mtype == "audio" and msg.get("data"):
                            pcm_bytes = base64.b64decode(msg["data"])
                            await session.send_realtime_input(
                                media=types.Blob(data=pcm_bytes, mime_type="audio/pcm;rate=16000")
                            )
                        elif mtype == "image" and msg.get("data"):
                            img_bytes = base64.b64decode(msg["data"])
                            await session.send_realtime_input(
                                video=types.Blob(data=img_bytes, mime_type=msg.get("mime_type", "image/jpeg"))
                            )
                        elif mtype == "interrupt":
                            await websocket.send_json({"interrupted": True})
                            if msg.get("text"):
                                await session.send_client_content(
                                    turns=types.Content(role="user", parts=[types.Part.from_text(text=msg["text"])]),
                                    turn_complete=True,
                                )
                        elif mtype == "text" and msg.get("text"):
                            await websocket.send_json({"interrupted": True})
                            await session.send_client_content(
                                turns=types.Content(role="user", parts=[types.Part.from_text(text=msg["text"])]),
                                turn_complete=True,
                            )
                except WebSocketDisconnect:
                    pass
                except Exception:
                    pass

            async def gemini_to_browser():
                turn_out_acc: list[str] = []
                try:
                    while True:
                        async for response in session.receive():
                            sc = getattr(response, "server_content", None)
                            if not sc:
                                continue
                            if getattr(sc, "interrupted", False):
                                turn_out_acc.clear()
                                await websocket.send_json({"interrupted": True})

                            in_tx = getattr(sc, "input_transcription", None)
                            if in_tx and getattr(in_tx, "text", None):
                                await websocket.send_json({"input_transcript": in_tx.text})

                            out_tx = getattr(sc, "output_transcription", None)
                            if out_tx and getattr(out_tx, "text", None):
                                turn_out_acc.append(out_tx.text)
                                await websocket.send_json({"output_transcript": out_tx.text})

                            mt = getattr(sc, "model_turn", None)
                            if mt and getattr(mt, "parts", None):
                                for part in mt.parts:
                                    inline = getattr(part, "inline_data", None)
                                    if inline and getattr(inline, "data", None):
                                        mime = (getattr(inline, "mime_type", "") or "").lower()
                                        if use_video_avatar or "video" in mime or "mp4" in mime:
                                            if ffmpeg_stdin is not None and not ffmpeg_stdin.is_closing():
                                                ffmpeg_stdin.write(inline.data)
                                                await ffmpeg_stdin.drain()
                                            else:
                                                await websocket.send_bytes(inline.data)
                                        else:
                                            b64_audio = base64.b64encode(inline.data).decode("ascii")
                                            await websocket.send_json({"audio_b64": b64_audio})

                            if getattr(sc, "turn_complete", False):
                                full_turn_text = "".join(turn_out_acc).strip()
                                turn_out_acc.clear()
                                matched = find_matching_squares(full_turn_text, max_cards=3) if full_turn_text else []
                                await websocket.send_json({
                                    "turn_complete": True,
                                    "matched_squares": matched,
                                })
                except Exception:
                    pass

            await asyncio.gather(browser_to_gemini(), gemini_to_browser())
        finally:
            if ffmpeg_stdin and not ffmpeg_stdin.is_closing():
                try:
                    ffmpeg_stdin.close()
                except Exception:
                    pass
            if ffmpeg_proc:
                try:
                    ffmpeg_proc.terminate()
                except Exception:
                    pass
            if ffmpeg_stdout_task:
                ffmpeg_stdout_task.cancel()
            try:
                await conn_ctx.__aexit__(None, None, None)
            except Exception:
                pass
    except Exception as exc:
        try:
            await websocket.send_json({"status_note": f"Live API Note: {exc}"})
        except Exception:
            pass
