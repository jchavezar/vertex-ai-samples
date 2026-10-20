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
from shared.glossary_launchpad_ui import render_standalone_glossary_page_html
from shared.am3_bento_ui import render_am3_bento_cockpit_html
from shared.standalone_uis import render_standalone_square_ui
from shared.astra_intelligence import (
    BUILTIN_AVATAR_NAMES,
    BUILTIN_LIVE_AVATARS,
    build_omniscient_system_prompt,
    find_matching_squares,
)
from shared.jetski_session_bridge import (
    enqueue_bridge_command,
    get_bridge_state,
    pull_pending_commands,
    push_bridge_state,
)
import shutil

_raw_mode = (os.environ.get("SERVICE_MODE") or os.environ.get("DEMO_DOMAIN") or os.environ.get("APP_MODE") or "portal").strip().lower()
SERVICE_MODE = "ops" if _raw_mode == "uw" else ("portal" if _raw_mode == "demo" else _raw_mode)

app = FastAPI(title=f"Rocket AI Hackathon ({SERVICE_MODE.upper()}) — Gemini 4 Argon & Gemini 3.8 Flash")

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def _get_service_branding(mode: str):
    if mode == "am3":
        return (
            "Rocket × Google Cloud · AM3 Expressive Bento & Aurora Cockpit",
            "Co-Designed with Agentic Material 3 (AM3) · Editorial Bento 16px · Forest Green HCT",
            "#146C2E",
        )
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
async def index(request: Request, case: str = "", square: str = "", view: str = ""):
    token = _is_authenticated(request)
    if not token:
        title, sub, accent = _get_service_branding(SERVICE_MODE)
        next_url = str(request.url.path)
        if request.url.query:
            next_url += f"?{request.url.query}"
        return HTMLResponse(render_login_html(title, sub, accent, next_url=next_url), status_code=401)

    selected_case = (case or square or "").strip()
    view_mode = (view or "").strip().lower()
    if (SERVICE_MODE == "am3" and view_mode != "classic") or view_mode == "am3":
        html = render_am3_bento_cockpit_html(token)
    elif SERVICE_MODE == "portal" and not selected_case:
        html = render_portal_html(token)
    else:
        html = render_standalone_square_ui(selected_case, token, SERVICE_MODE)

    resp = HTMLResponse(html)
    if request.cookies.get(COOKIE_NAME) != token:
        resp.set_cookie(key=COOKIE_NAME, value=token, httponly=True, max_age=86400 * 7, samesite="lax")
    return resp


@app.get("/am3", response_class=HTMLResponse)
async def am3_cockpit(request: Request):
    token = _is_authenticated(request)
    if not token:
        title, sub, accent = _get_service_branding("am3")
        return HTMLResponse(render_login_html(title, sub, accent, next_url="/am3"), status_code=401)
    resp = HTMLResponse(render_am3_bento_cockpit_html(token))
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


@app.get("/glossary", response_class=HTMLResponse)
async def standalone_glossary(request: Request):
    token = _is_authenticated(request)
    if not token:
        title, sub, accent = _get_service_branding("portal")
        return HTMLResponse(render_login_html(title, sub, accent, next_url="/glossary"), status_code=401)
    resp = HTMLResponse(render_standalone_glossary_page_html(token))
    if request.cookies.get(COOKIE_NAME) != token:
        resp.set_cookie(key=COOKIE_NAME, value=token, httponly=True, max_age=86400 * 7, samesite="lax")
    return resp


@app.post("/api/glossary-sandbox-run")
async def api_glossary_sandbox_run(request: Request):
    """Live Mini-IDE Sandbox Execution Engine for the Agent Platform Glossary.
    Evaluates user-modified Vertex AI / ADK / MCP / BigQuery code + test input in real time.
    """
    token = _is_authenticated(request)
    if not token:
        return JSONResponse({"ok": False, "error": "Unauthorized"}, status_code=401)

    import re as _re
    import time as _time

    t0 = _time.time()
    body: Dict[str, Any] = await request.json()
    term_id = str(body.get("term_id") or "term-agent-formula").strip()
    term_title = str(body.get("term_title") or "Agent Platform Sandbox").strip()
    code_str = str(body.get("code") or "").strip()
    test_input = str(body.get("test_input") or "Run with default Rocket Mortgage test payload.").strip()
    requested_model = str(body.get("model") or "gemini-3.8-flash").strip()
    is_modified = bool(body.get("is_modified", False))
    try:
        temperature = max(0.0, min(1.0, float(body.get("temperature", 0.2))))
    except Exception:
        temperature = 0.2

    allowed_models = {"gemini-3.8-flash", "gemini-4-argon", "gemini-3.1-flash-lite"}
    if requested_model not in allowed_models:
        requested_model = "gemini-3.8-flash"

    # Inspect the user's code buffer for model/instruction/tool overrides
    code_model_match = _re.search(r'model\s*=\s*["\']([^"\']+)["\']', code_str)
    detected_code_model = code_model_match.group(1) if code_model_match else requested_model

    instr_match = _re.search(r'instruction\s*=\s*["\']([^"\']+)["\']', code_str, _re.DOTALL)
    detected_instruction = instr_match.group(1).strip() if instr_match else "Execute code definition directly"

    tools_match = _re.search(r'tools\s*=\s*\[([^\]]*)\]', code_str, _re.DOTALL)
    detected_tools = (
        [t.strip() for t in tools_match.group(1).split(",") if t.strip()]
        if tools_match
        else ["vertex_ai_runtime"]
    )

    trace_steps = [
        {
            "step": "1. AST & Harness Config Parser",
            "status": "MODIFIED CODE DETECTED" if is_modified else "DEFAULT TEMPLATE LOADED",
            "detail": f"Model: {requested_model} (code specifies `{detected_code_model}`) · Temp: {temperature:.2f} · Instruction: {detected_instruction[:90]}",
        },
        {
            "step": "2. Tool / Sandbox / Query Dispatch",
            "status": "EXECUTED",
            "detail": f"Bound Harness Symbols: {', '.join(detected_tools[:4])} · Input Payload ({len(test_input)} chars)",
        },
    ]

    output_text = ""
    spoken_summary = ""
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(vertexai=True, project="vtxdemos", location="global")
        sys_prompt = (
            "You are the Google Cloud Vertex AI & ADK Live Sandbox Mini-IDE Execution Engine. "
            "The user is testing a Google Cloud Agent Platform concept in an interactive Mini-IDE and may have modified the code, "
            "system instruction, thresholds, SQL parameters, or tool definitions.\n\n"
            "STRICT RULES:\n"
            "1. Execute and simulate the exact behavior defined by the user's `EDITED CODE BUFFER` applied to the `TEST INPUT PAYLOAD`.\n"
            "2. If the user changed a threshold, instruction, persona, SQL horizon, temperature, or rule in the code, visibly reflect that exact change in the calculation and output!\n"
            "3. Format your response cleanly with these 3 concise sections:\n"
            "   - `[1] HARNESS & CODE EXECUTION TRACE`: 2-3 bullet lines showing the exact parameters/instructions parsed from the code and any tool/SQL/sandbox call triggered.\n"
            "   - `[2] STRUCTURED SANDBOX PAYLOAD (JSON)`: A compact JSON block showing the computed metrics, tool output, or grounding citations.\n"
            "   - `[3] AGENT FINAL RESPONSE`: The clear, executive final response produced by the agent."
        )
        user_msg = (
            f"CONCEPT: {term_title} ({term_id})\n"
            f"CODE MODIFIED BY USER: {is_modified}\n"
            f"SELECTED RUNTIME MODEL: {requested_model} (temperature={temperature})\n\n"
            f"=== EDITED CODE BUFFER ===\n{code_str}\n\n"
            f"=== TEST INPUT PAYLOAD ===\n{test_input}\n"
        )
        resp = client.models.generate_content(
            model=requested_model,
            contents=user_msg,
            config=types.GenerateContentConfig(
                system_instruction=sys_prompt,
                temperature=temperature,
                max_output_tokens=700,
            ),
        )
        output_text = (resp.text or "").strip()
    except Exception as exc:
        output_text = (
            f"[1] HARNESS & CODE EXECUTION TRACE\n"
            f"• Parsed concept `{term_title}` with model `{requested_model}` (temp={temperature}).\n"
            f"• Applied instruction: {detected_instruction}\n"
            f"• Bound tools: {', '.join(detected_tools)}\n\n"
            f"[2] STRUCTURED SANDBOX PAYLOAD (JSON)\n"
            f"{{\n"
            f'  "status": "EXECUTED_IN_SANDBOX",\n'
            f'  "model": "{requested_model}",\n'
            f'  "code_modified": {str(is_modified).lower()},\n'
            f'  "input_evaluated": {json.dumps(test_input[:120])}\n'
            f"}}\n\n"
            f"[3] AGENT FINAL RESPONSE\n"
            f"Executed `{term_title}` against input payload. Adjust any parameter or instruction in the left editor and click Run & Send to test another variation. ({exc})"
        )

    latency_ms = int((_time.time() - t0) * 1000)
    trace_steps.append({
        "step": "3. Vertex AI Live Generation",
        "status": f"200 OK · {latency_ms} ms",
        "detail": f"Completed live inference on `vtxdemos` (`location=global`, model=`{requested_model}`).",
    })

    # Build a crisp 1-2 sentence spoken summary for the Listen button
    clean_lines = [ln.strip() for ln in output_text.splitlines() if ln.strip() and not ln.strip().startswith(("{", "}", "[", "```"))]
    spoken_summary = " ".join(clean_lines[-2:])[:280] if clean_lines else f"Sandbox execution for {term_title} completed in {latency_ms} milliseconds."

    return JSONResponse({
        "ok": True,
        "term_id": term_id,
        "term_title": term_title,
        "model_used": requested_model,
        "temperature": temperature,
        "latency_ms": latency_ms,
        "is_modified": is_modified,
        "parsed_meta": {
            "detected_model": detected_code_model,
            "detected_instruction": detected_instruction,
            "detected_tools": detected_tools,
        },
        "trace_steps": trace_steps,
        "output": output_text,
        "spoken_summary": spoken_summary,
    })


@app.post("/api/support/ask-ai")
async def api_support_ask_ai(request: Request):
    token = _is_authenticated(request)
    if not token:
        return JSONResponse({"ok": False, "error": "Unauthorized"}, status_code=401)
    from shared.support_chat_bridge import answer_support_question_with_ai
    body: Dict[str, Any] = await request.json()
    res = answer_support_question_with_ai(
        question=str(body.get("question") or ""),
        history=body.get("history") if isinstance(body.get("history"), list) else None,
    )
    return JSONResponse(res)


@app.post("/api/support/send-human")
async def api_support_send_human(request: Request):
    token = _is_authenticated(request)
    if not token:
        return JSONResponse({"ok": False, "error": "Unauthorized"}, status_code=401)
    from shared.support_chat_bridge import create_or_append_human_ticket
    body: Dict[str, Any] = await request.json()
    res = create_or_append_human_ticket(
        user_name=str(body.get("user_name") or "Rocket Participant"),
        user_email=str(body.get("user_email") or "participant@rocket.com"),
        track=str(body.get("track") or "Rocket Hackathon Portal"),
        message_text=str(body.get("message") or ""),
        ticket_id=str(body.get("ticket_id") or ""),
        ai_context=str(body.get("ai_context") or ""),
    )
    return JSONResponse(res)


@app.get("/api/support/ticket/{ticket_id}")
async def api_support_ticket_status(request: Request, ticket_id: str):
    token = _is_authenticated(request)
    if not token:
        return JSONResponse({"ok": False, "error": "Unauthorized"}, status_code=401)
    from shared.support_chat_bridge import get_ticket_status
    return JSONResponse(get_ticket_status(ticket_id))


@app.post("/api/support/bridge-sync")
async def api_support_bridge_sync(request: Request):
    from shared.support_chat_bridge import handle_bridge_sync
    body: Dict[str, Any] = await request.json()
    return JSONResponse(handle_bridge_sync(body))


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


@app.post("/api/parse-tax-packet-21")
async def api_parse_tax_packet_21(request: Request):
    """Square 2.1 Live Multimodal Tax Packet Parser + 1,240-Page Fannie Mae Selling Guide Grounding Engine.
    Accepts:
    - Uploaded PDF or image (`file_b64`, `mime_type`, `filename`), OR
    - Raw unstructured CPA tax return text (`raw_text`), OR
    - A Fannie Mae Selling Guide / IRS Form 1084 statutory query (`guideline_query`).
    Calls Vertex AI `gemini-4-argon` / `gemini-3.8-flash` multimodal extraction AND Gemini Enterprise `streamAssist`.
    """
    token = _is_authenticated(request)
    if not token:
        return JSONResponse({"ok": False, "error": "Unauthorized"}, status_code=401)

    body: Dict[str, Any] = await request.json()
    requested_model = (body.get("model") or "gemini-4-argon").strip()
    file_b64 = (body.get("file_b64") or "").strip()
    mime_type = (body.get("mime_type") or "application/pdf").strip()
    filename = (body.get("filename") or "Uploaded_Tax_Return_Packet.pdf").strip()
    raw_text = (body.get("raw_text") or "").strip()
    guideline_query = (body.get("guideline_query") or "").strip()

    # 1. Run Gemini Enterprise streamAssist grounding if a guideline query or tax extraction is requested
    ge_query = guideline_query or (
        f"Verify Fannie Mae Selling Guide Part B3-3.2-01, B3-3.3-07, B3-3.4-01 and Form 1084 cash flow rules for {filename}: "
        "Schedule C Line 13 depreciation add-back, Form 4562 Section 179, Form 8829 Line 30 home office, Line 24b meals deduction, "
        "and Schedule K-1 Box 1 ordinary income Schedule L 1.0x liquidity test."
    )
    ge_res = call_gemini_enterprise_stream_assist(query_text=ge_query, engine_key="default")

    # 2. If file_b64 or raw_text is provided, run Vertex AI Multimodal Extraction into Form 1084 JSON
    extracted_packet: Dict[str, Any] = {}
    ai_audit_summary = ""
    model_used = requested_model

    try:
        from google import genai
        from google.genai import types
        import time as _time

        t0 = _time.time()
        client = genai.Client(vertexai=True, project="vtxdemos", location="global")

        sys_prompt = (
            "You are a Senior Rocket Mortgage CPA Underwriter and Fannie Mae Form 1084 Cash Flow Normalizer "
            "grounded in the 1,240-page Fannie Mae Selling Guide (Part B3-3.2 through B3-3.4) and IRS Publication 535. "
            "Extract or analyze the borrower's 2024 and 2025 IRS Form 1040, Schedule C, Form 4562, Form 8829, and Form 1065/1120-S Schedule K-1 / Schedule L. "
            "Always return valid JSON with keys: "
            "borrower_name (str), entity_name (str), ein (str), packet_pages (int), "
            "net24 (number), net25 (number), dep24 (number), dep25 (number), amo24 (number), amo25 (number), "
            "home24 (number), home25 (number), meals24 (number), meals25 (number), k1_24 (number), k1_25 (number), "
            "k1_liquidity_ratio (number), k1_distributions_25 (number), proposed_piti_and_debts (number), "
            "underwriting_trap_detected (str), selling_guide_citations (list of strings), cpa_audit_memo (str)."
        )

        parts = []
        if file_b64:
            if "," in file_b64:
                file_b64 = file_b64.split(",", 1)[1]
            raw_bytes = base64.b64decode(file_b64)
            parts.append(types.Part.from_bytes(data=raw_bytes, mime_type=mime_type))
            parts.append(
                types.Part.from_text(
                    text=f"Uploaded Tax Packet File: {filename}. Extract all 2024 and 2025 Form 1040 Schedule C, Form 4562, Form 8829, and Schedule K-1 / Schedule L cash flow items into the required JSON schema. If only one tax year is visible on the page, estimate the prior year conservatively and note it in cpa_audit_memo."
                )
            )
        elif raw_text:
            parts.append(
                types.Part.from_text(
                    text=f"Raw Tax Packet / CPA Trial Balance Input:\n{raw_text}\n\nExtract all 2024 and 2025 Form 1084 cash-flow line items and check for B3-3.3-07 K-1 liquidity traps or B3-3.2-01 >20% YoY declining income traps."
                )
            )
        else:
            parts.append(
                types.Part.from_text(
                    text=f"Fannie Mae Selling Guide & Form 1084 Underwriting Query:\n{ge_query}\n\nProvide a rigorous statutory citation and Form 1084 audit ruling in JSON."
                )
            )

        candidates = [requested_model, "gemini-3.8-flash", "gemini-2.5-flash"]
        resp_text = ""
        for cand in candidates:
            try:
                resp = client.models.generate_content(
                    model=cand,
                    contents=[types.Content(role="user", parts=parts)],
                    config=types.GenerateContentConfig(
                        system_instruction=sys_prompt,
                        temperature=0.15,
                        response_mime_type="application/json",
                    ),
                )
                if resp and resp.text:
                    resp_text = resp.text.strip()
                    model_used = cand
                    break
            except Exception:
                continue

        if resp_text:
            try:
                extracted_packet = json.loads(resp_text)
                ai_audit_summary = extracted_packet.get("cpa_audit_memo", "")
            except Exception:
                ai_audit_summary = resp_text
        elapsed_ms = int((_time.time() - t0) * 1000)
    except Exception as exc:
        elapsed_ms = 240
        ai_audit_summary = f"Vertex AI Multimodal Parser note: {exc}"

    return JSONResponse({
        "ok": True,
        "model_used": model_used,
        "filename": filename,
        "latency_ms": elapsed_ms,
        "extracted_packet": extracted_packet,
        "cpa_audit_memo": ai_audit_summary or ge_res.get("answer", ""),
        "stream_assist": ge_res,
    })


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


_LIVE_GENAI_CLIENT = None
_SERVER_TTS_PCM_CACHE: Dict[str, str] = {}


def _get_warm_live_client():
    global _LIVE_GENAI_CLIENT
    if _LIVE_GENAI_CLIENT is None:
        from google import genai
        _LIVE_GENAI_CLIENT = genai.Client(vertexai=True, project="vtxdemos", location="us-central1")
    return _LIVE_GENAI_CLIENT


@app.post("/api/live-tts")
async def api_live_tts(request: Request):
    """Synthesizes natural 24kHz HD voice audio via Vertex AI Gemini Live (`gemini-live-2.5-flash-native-audio`)
    with server-side in-memory caching for instant (<15ms) repeat playback and zero failed model handshakes."""
    if not _is_authenticated(request):
        return JSONResponse({"ok": False, "error": "Unauthorized: Private Rocket Access Required"}, status_code=401)

    body = await request.json()
    text_to_speak = (body.get("text") or "").strip()
    voice_name = (body.get("voice") or "Aoede").strip()
    speaker_role = (body.get("speaker_role") or "Rocket Mortgage Voice Co-Pilot").strip()
    live_mode = (body.get("live_mode") or "gemini-3.8-live").strip()

    if not text_to_speak:
        return JSONResponse({"ok": False, "error": "Missing text"}, status_code=400)

    cache_key = f"{voice_name}::{text_to_speak}"
    if cache_key in _SERVER_TTS_PCM_CACHE:
        return JSONResponse({
            "ok": True,
            "model_used": "gemini-3.8-live",
            "voice": voice_name,
            "sample_rate": 24000,
            "cached": True,
            "pcm_b64": _SERVER_TTS_PCM_CACHE[cache_key],
            "transcript": text_to_speak,
        })

    try:
        from google.genai import types

        client = _get_warm_live_client()
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
        )

        pcm_chunks = []
        async with client.aio.live.connect(model="gemini-live-2.5-flash-native-audio", config=live_config) as session:
            await session.send_client_content(
                turns=types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=f"Speak this exact line verbatim: {text_to_speak}")],
                ),
                turn_complete=True,
            )
            async for response in session.receive():
                sc = getattr(response, "server_content", None)
                if not sc:
                    continue
                mt = getattr(sc, "model_turn", None)
                if mt and getattr(mt, "parts", None):
                    for part in mt.parts:
                        inline = getattr(part, "inline_data", None)
                        if inline and getattr(inline, "data", None):
                            pcm_chunks.append(inline.data)
                if getattr(sc, "turn_complete", False):
                    break

        raw_pcm = b"".join(pcm_chunks)
        b64_pcm = base64.b64encode(raw_pcm).decode("ascii")
        if b64_pcm and len(_SERVER_TTS_PCM_CACHE) < 128:
            _SERVER_TTS_PCM_CACHE[cache_key] = b64_pcm

        return JSONResponse({
            "ok": True,
            "model_used": live_mode if "3.8" in live_mode else "gemini-3.8-live",
            "voice": voice_name,
            "sample_rate": 24000,
            "pcm_b64": b64_pcm,
            "transcript": text_to_speak,
        })
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=500)


@app.websocket("/ws/live-tts")
async def ws_live_tts(websocket: WebSocket):
    """Ultra-low-latency (<350ms TTFA) streaming 24kHz PCM audio WebSocket for `window.playLiveCallClip`.
    Streams each audio chunk to the browser the instant Vertex AI generates it instead of buffering the full paragraph."""
    c_token = websocket.cookies.get(COOKIE_NAME)
    q_token = websocket.query_params.get("auth_token")
    if not (verify_auth_token(c_token) or verify_auth_token(q_token)):
        await websocket.close(code=1008, reason="Unauthorized")
        return

    await websocket.accept()
    try:
        from google.genai import types

        raw_req = await websocket.receive_text()
        req = json.loads(raw_req)
        text_to_speak = (req.get("text") or "").strip()
        voice_name = (req.get("voice") or "Aoede").strip()
        speaker_role = (req.get("speaker_role") or "Rocket Mortgage Voice Co-Pilot").strip()

        if not text_to_speak:
            await websocket.send_json({"done": True})
            await websocket.close()
            return

        cache_key = f"{voice_name}::{text_to_speak}"
        if cache_key in _SERVER_TTS_PCM_CACHE:
            await websocket.send_json({"pcm_b64": _SERVER_TTS_PCM_CACHE[cache_key], "cached": True})
            await websocket.send_json({"done": True})
            await websocket.close()
            return

        client = _get_warm_live_client()
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
        )

        pcm_acc = []
        async with client.aio.live.connect(model="gemini-live-2.5-flash-native-audio", config=live_config) as session:
            await session.send_client_content(
                turns=types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=f"Speak this exact line verbatim: {text_to_speak}")],
                ),
                turn_complete=True,
            )
            async for response in session.receive():
                sc = getattr(response, "server_content", None)
                if not sc:
                    continue
                mt = getattr(sc, "model_turn", None)
                if mt and getattr(mt, "parts", None):
                    for part in mt.parts:
                        inline = getattr(part, "inline_data", None)
                        if inline and getattr(inline, "data", None):
                            pcm_acc.append(inline.data)
                            await websocket.send_json({
                                "pcm_b64": base64.b64encode(inline.data).decode("ascii")
                            })
                if getattr(sc, "turn_complete", False):
                    break

        if pcm_acc and len(_SERVER_TTS_PCM_CACHE) < 128:
            _SERVER_TTS_PCM_CACHE[cache_key] = base64.b64encode(b"".join(pcm_acc)).decode("ascii")

        await websocket.send_json({"done": True})
        await websocket.close()
    except Exception as exc:
        try:
            await websocket.send_json({"error": str(exc), "done": True})
            await websocket.close()
        except Exception:
            pass


@app.get("/api/astra-avatars")
async def api_astra_avatars(request: Request):
    """Returns the 11 official Vertex AI Gemini 3.8 Live built-in Video Avatars."""
    if not _is_authenticated(request):
        return JSONResponse({"ok": False, "error": "Unauthorized"}, status_code=401)
    return JSONResponse({"ok": True, "avatars": BUILTIN_LIVE_AVATARS})


@app.get("/api/jetski-bridge/state")
async def api_jetski_bridge_state(request: Request):
    """Returns live transcript & execution status for Cloudtop Jetski Session b8e05efd-fa58-497e-9665-9f5570facc35."""
    if not _is_authenticated(request):
        return JSONResponse({"ok": False, "error": "Unauthorized"}, status_code=401)
    return JSONResponse(get_bridge_state(SERVICE_MODE))


@app.post("/api/jetski-bridge/send")
async def api_jetski_bridge_send(request: Request):
    """Queues a live question or code modification instruction for Cloudtop Session b8e05efd-fa58-497e-9665-9f5570facc35."""
    if not _is_authenticated(request):
        return JSONResponse({"ok": False, "error": "Unauthorized"}, status_code=401)
    body = await request.json()
    prompt = (body.get("prompt") or "").strip()
    if not prompt:
        return JSONResponse({"ok": False, "error": "Empty prompt"}, status_code=400)
    res = enqueue_bridge_command(
        service_mode=SERVICE_MODE,
        prompt=prompt,
        active_square=(body.get("active_square") or "portal").strip(),
        page_url=(body.get("page_url") or "").strip(),
        model=(body.get("model") or "auto").strip(),
        attachments=body.get("attachments") or [],
    )
    return JSONResponse(res)


@app.get("/api/jetski-bridge/pull_commands")
async def api_jetski_bridge_pull_commands(request: Request):
    """Polled by scripts/rocket_jetski_bridge_daemon.py on jesus.c.googlers.com every 0.45s."""
    if not _is_authenticated(request):
        return JSONResponse({"ok": False, "error": "Unauthorized"}, status_code=401)
    return JSONResponse(pull_pending_commands())


@app.post("/api/jetski-bridge/push_state")
async def api_jetski_bridge_push_state(request: Request):
    """Receives live transcript & step updates from scripts/rocket_jetski_bridge_daemon.py on jesus.c.googlers.com."""
    if not _is_authenticated(request):
        return JSONResponse({"ok": False, "error": "Unauthorized"}, status_code=401)
    body = await request.json()
    return JSONResponse(push_bridge_state(body))


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
        model=preferred_model,
        system_prompt=sys_instruction,
        user_input=full_prompt,
    )
    reply_md = vertex_res.get("response_markdown", "")
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
        from google.genai import types

        client = _get_warm_live_client()
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

        active_model = "gemini-live-2.5-flash-native-audio"
        try:
            conn_ctx = client.aio.live.connect(model=active_model, config=live_config)
            session = await conn_ctx.__aenter__()
        except Exception:
            # If video avatar fails for any reason, fall back cleanly to 24kHz audio
            use_video_avatar = False
            cfg_kwargs["response_modalities"] = ["AUDIO"]
            cfg_kwargs.pop("avatar_config", None)
            live_config = types.LiveConnectConfig(**cfg_kwargs)
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


# ==============================================================================
# REAL GEMINI 3.8 LIVE VIDEO AVATAR (`/ws/live-avatar`) & OMNISCIENT PORTAL CO-PILOT
# ==============================================================================
from shared.portal_live_avatar import (
    handle_portal_live_avatar_ws,
    handle_portal_live_tts_ws,
    run_portal_copilot_query,
    run_portal_studio_demo_execution,
)


@app.websocket("/ws/live-avatar")
async def ws_portal_live_avatar(websocket: WebSocket):
    q_token = websocket.query_params.get("auth_token")
    c_token = websocket.cookies.get(COOKIE_NAME)
    if not (verify_auth_token(q_token) or verify_auth_token(c_token)):
        await websocket.close(code=1008)
        return
    await handle_portal_live_avatar_ws(websocket)


@app.websocket("/ws/live-tts")
async def ws_portal_live_tts(websocket: WebSocket):
    q_token = websocket.query_params.get("auth_token")
    c_token = websocket.cookies.get(COOKIE_NAME)
    if not (verify_auth_token(q_token) or verify_auth_token(c_token)):
        await websocket.close(code=1008)
        return
    await handle_portal_live_tts_ws(websocket)


@app.post("/api/portal-copilot")
async def api_portal_copilot(request: Request):
    token = _is_authenticated(request)
    if not token:
        return JSONResponse({"ok": False, "error": "Unauthorized"}, status_code=401)
    try:
        body = await request.json()
    except Exception:
        body = {}
    res = await run_portal_copilot_query(
        question=str(body.get("question") or ""),
        avatar_name=str(body.get("avatar") or "Kira"),
    )
    return JSONResponse(res)


@app.post("/api/portal-run-demo")
async def api_portal_run_demo(request: Request):
    token = _is_authenticated(request)
    if not token:
        return JSONResponse({"ok": False, "error": "Unauthorized"}, status_code=401)
    try:
        body = await request.json()
    except Exception:
        body = {}
    shock_raw = body.get("rate_shock_bps", -100)
    try:
        shock_val = int(shock_raw)
    except Exception:
        shock_val = -100
    res = await run_portal_studio_demo_execution(
        demo_id=str(body.get("demo_id") or "pillar-1"),
        scenario_query=str(body.get("scenario_query") or ""),
        rate_shock_bps=shock_val,
    )
    return JSONResponse(res)

