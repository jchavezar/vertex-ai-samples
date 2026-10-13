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

SERVICE_MODE = os.environ.get("SERVICE_MODE", "portal").strip().lower()

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


@app.websocket("/ws/live-voice/{code}")
async def ws_live_voice(websocket: WebSocket, code: str):
    """Real Bidirectional WebSocket connected to Vertex AI Live API (`gemini-live-2.5-flash-native-audio` in `us-central1`).
    Accepts 16kHz PCM audio chunks or text barge-in turns from the browser and streams back 24kHz native audio + live transcripts."""
    c_token = websocket.cookies.get(COOKIE_NAME)
    q_token = websocket.query_params.get("auth_token")
    if not (verify_auth_token(c_token) or verify_auth_token(q_token)):
        await websocket.close(code=1008, reason="Unauthorized: Private Rocket Hackathon Access Required")
        return

    await websocket.accept()
    proj = PROJECTS_BY_CODE.get(code, PROJECTS_BY_CODE.get("M.1"))
    cfg = get_bespoke_config(code)
    sys_prompt = cfg.get(
        "live_voice_prompt",
        f"You are Rocket Mortgage's real-time voice advisor for {proj['project']}. Speak warmly and concisely in 2 sentences.",
    )

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(vertexai=True, project="vtxdemos", location="us-central1")
        live_config = types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            system_instruction=types.Content(parts=[types.Part.from_text(text=sys_prompt)]),
            input_audio_transcription=types.AudioTranscriptionConfig(),
            output_audio_transcription=types.AudioTranscriptionConfig(),
        )

        async with client.aio.live.connect(model="gemini-live-2.5-flash-native-audio", config=live_config) as session:

            async def browser_to_gemini():
                try:
                    while True:
                        raw = await websocket.receive_text()
                        msg = json.loads(raw)
                        if msg.get("type") == "audio" and msg.get("data"):
                            pcm_bytes = base64.b64decode(msg["data"])
                            await session.send_realtime_input(
                                media=types.Blob(data=pcm_bytes, mime_type="audio/pcm;rate=16000")
                            )
                        elif msg.get("type") == "text" and msg.get("text"):
                            await session.send_client_content(
                                turns=types.Content(role="user", parts=[types.Part.from_text(text=msg["text"])]),
                                turn_complete=True,
                            )
                except WebSocketDisconnect:
                    pass
                except Exception:
                    pass

            async def gemini_to_browser():
                try:
                    while True:
                        async for response in session.receive():
                            sc = getattr(response, "server_content", None)
                            if not sc:
                                continue
                            in_tx = getattr(sc, "input_transcription", None)
                            if in_tx and getattr(in_tx, "text", None):
                                await websocket.send_json({"input_transcript": in_tx.text})

                            out_tx = getattr(sc, "output_transcription", None)
                            if out_tx and getattr(out_tx, "text", None):
                                await websocket.send_json({"output_transcript": out_tx.text})

                            mt = getattr(sc, "model_turn", None)
                            if mt and getattr(mt, "parts", None):
                                for part in mt.parts:
                                    inline = getattr(part, "inline_data", None)
                                    if inline and getattr(inline, "data", None):
                                        b64_audio = base64.b64encode(inline.data).decode("ascii")
                                        await websocket.send_json({"audio_b64": b64_audio})
                except Exception:
                    pass

            await asyncio.gather(browser_to_gemini(), gemini_to_browser())
    except Exception as exc:
        try:
            await websocket.send_json({"status_note": f"Live API Note: {exc}"})
        except Exception:
            pass
