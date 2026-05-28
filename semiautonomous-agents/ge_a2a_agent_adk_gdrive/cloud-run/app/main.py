"""FastAPI entrypoint for the Cloud Run-hosted A2A agent.

Implements the JSON-RPC transport that Gemini Enterprise's Custom-A2A
proxy ("harpoon") requires. The card advertises `preferredTransport: "JSONRPC"`
and the entrypoint at POST `/` accepts `{jsonrpc, method, params, id}`
messages. The only method GE issues for chat is `message/send`.

Cloud Run preserves the `Authorization` header verbatim, so the user OAuth
bearer GE captured during consent lands here intact. We:

  1. Extract the token from `Authorization: Bearer <ya29.user>`.
  2. Resolve the user's identity via the OAuth2 userinfo endpoint.
  3. Push the token + identity into ADK session state.
  4. Run the LlmAgent — its `drive_search_files` tool reads the token and
     calls Drive AS the user. End-to-end delegation, no SA impersonation.
"""

from __future__ import annotations

import logging
import os
import uuid
from typing import Any

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from .agent import root_agent

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ge_cr_agent")

APP_NAME = "ge_cr_a2a_agent"
USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

_session_service = InMemorySessionService()
_runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=_session_service)
app = FastAPI(title="GE A2A Auth Demo (Cloud Run)")


@app.middleware("http")
async def log_every_request(request: Request, call_next):
    interesting = {k: v for k, v in request.headers.items() if k.lower() in (
        "user-agent", "host", "x-forwarded-for", "x-forwarded-proto", "x-forwarded-host",
        "x-cloud-trace-context", "x-goog-authenticated-user-email", "x-goog-iap-jwt-assertion",
        "x-goog-user-project", "x-server-timing", "traceparent",
        "x-goog-api-client", "x-request-id",
    )}
    log.info("REQ %s %s q=%r headers=%s", request.method, request.url.path, request.url.query, interesting)
    return await call_next(request)


def _agent_card() -> dict[str, Any]:
    return {
        "name": "ge_cr_a2a_agent",
        "description": (
            "Diagnostic agent demonstrating end-to-end user OAuth delegation: "
            "Gemini Enterprise -> Custom A2A -> Google Drive (as the user)."
        ),
        "url": os.environ.get("PUBLIC_A2A_URL", "http://localhost:8080"),
        "version": "1.0.0",
        "protocolVersion": "0.3.0",
        "preferredTransport": "JSONRPC",
        "defaultInputModes": ["text/plain"],
        "defaultOutputModes": ["text/plain"],
        "capabilities": {"streaming": False},
        "supportsAuthenticatedExtendedCard": True,
        "skills": [
            {
                "id": "whoami",
                "name": "Caller identity (from user OAuth token)",
                "description": (
                    "Echo the email + sub claims of the OAuth bearer GE "
                    "forwarded. Proves user identity reaches the container."
                ),
                "tags": ["diagnostic", "identity"],
                "examples": ["whoami", "who am i?"],
            },
            {
                "id": "drive_search_files",
                "name": "Search the caller's Google Drive (as the user)",
                "description": (
                    "Calls drive.files.list using the user's OAuth token. "
                    "Returns files visible to the calling Google account."
                ),
                "tags": ["drive", "delegation"],
                "examples": [
                    "list my Drive files",
                    "find my Drive PDFs",
                    "show my recent docs",
                ],
            },
        ],
    }


async def _userinfo(token: str) -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=10) as cx:
            r = await cx.get(USERINFO_URL, headers={"Authorization": f"Bearer {token}"})
        if r.status_code == 200:
            return r.json()
        log.warning("userinfo non-200: %s %s", r.status_code, r.text[:200])
    except Exception as e:
        log.warning("userinfo error: %s", e)
    return {}


def _extract_text(message: dict[str, Any]) -> str:
    parts = message.get("parts") or []
    out = []
    for p in parts:
        if (p.get("kind") or p.get("type")) in (None, "text"):
            t = p.get("text")
            if t:
                out.append(t)
    return "\n".join(out).strip()


async def _run_agent(text: str, context_id: str, token: str, user: dict[str, Any]) -> str:
    email = user.get("email") or "(not present)"
    sub = user.get("sub") or "(not present)"
    name = user.get("name") or "(not present)"
    caller_block = (
        "caller_identity:\n"
        f"  email={email}\n"
        f"  sub={sub}\n"
        f"  name={name}\n"
        f"  source=GE-forwarded user OAuth bearer (drive.readonly + cloud-platform)"
    )
    initial_state = {
        "user_token": token,
        "user_email": email,
        "user_sub": sub,
        "caller_identity": caller_block,
    }

    session = await _session_service.get_session(
        app_name=APP_NAME, user_id=context_id, session_id=context_id
    )
    if session is None:
        session = await _session_service.create_session(
            app_name=APP_NAME, user_id=context_id, session_id=context_id,
            state=initial_state,
        )
    else:
        for k, v in initial_state.items():
            session.state[k] = v

    adk_in = genai_types.Content(role="user", parts=[genai_types.Part(text=text)])
    out: list[str] = []
    async for ev in _runner.run_async(
        user_id=context_id, session_id=context_id, new_message=adk_in
    ):
        if ev.is_final_response() and ev.content and ev.content.parts:
            for p in ev.content.parts:
                if p.text:
                    out.append(p.text)
    return "".join(out) or "(empty)"


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/v1/card")
@app.get("/.well-known/agent-card.json")
@app.get("/.well-known/agent.json")
async def card():
    return _agent_card()


async def _handle_message_send(params: dict[str, Any], token: str) -> dict[str, Any]:
    """Build the A2A `Message` result for a JSONRPC message/send call."""
    message = params.get("message") or {}
    text = _extract_text(message)
    context_id = message.get("contextId") or str(uuid.uuid4())
    task_id = message.get("taskId") or str(uuid.uuid4())

    user = await _userinfo(token)
    log.info("inbound: user=%s sub=%s text=%r", user.get("email"), user.get("sub"), text[:120])

    reply = await _run_agent(text=text, context_id=context_id, token=token, user=user)
    log.info("reply: %r", reply[:200])

    return {
        "kind": "message",
        "messageId": str(uuid.uuid4()),
        "role": "agent",
        "parts": [{"kind": "text", "text": reply}],
        "contextId": context_id,
        "taskId": task_id,
    }


def _jsonrpc_error(req_id: Any, code: int, message: str, data: Any = None) -> dict[str, Any]:
    err: dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    return {"jsonrpc": "2.0", "id": req_id, "error": err}


@app.post("/")
@app.post("/v1/message:send")
@app.post("/v1/messages:send")
async def jsonrpc_endpoint(request: Request):
    """A2A JSONRPC entrypoint. GE posts {jsonrpc, method, params, id} here."""
    try:
        body = await request.json()
    except Exception as e:
        log.warning("jsonrpc: bad JSON body: %s", e)
        return JSONResponse(_jsonrpc_error(None, -32700, f"Parse error: {e}"))

    req_id = body.get("id")
    method = body.get("method") or ""
    params = body.get("params") or {}

    auth = request.headers.get("authorization") or request.headers.get("Authorization") or ""
    token = auth[7:] if auth.lower().startswith("bearer ") else ""
    if not token:
        return JSONResponse(_jsonrpc_error(req_id, -32001, "Missing Authorization: Bearer <token>"))

    log.info("jsonrpc method=%s id=%r", method, req_id)
    try:
        if method == "message/send":
            result = await _handle_message_send(params, token)
            return JSONResponse({"jsonrpc": "2.0", "id": req_id, "result": result})
        return JSONResponse(_jsonrpc_error(req_id, -32601, f"Method not found: {method}"))
    except Exception as e:
        log.exception("jsonrpc handler failed")
        return JSONResponse(_jsonrpc_error(req_id, -32000, f"Internal error: {e}"))
