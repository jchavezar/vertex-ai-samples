"""
FastAPI proxy that streams Gemini Enterprise streamAssist events to the browser via SSE.

Hard-coded to the jira-testing engine in vtxdemos. Re-streams every chunk verbatim
plus a parsed "chat" delta for the UI.
"""

from __future__ import annotations

import asyncio
import datetime as _dt
import hashlib
import json
import logging
import os
import re
import secrets
import sys
import time
import uuid
from pathlib import Path
from typing import AsyncIterator, Optional

import httpx
from fastapi import Cookie, FastAPI, Header, HTTPException, Request, Response
from fastapi.responses import (
    FileResponse,
    JSONResponse,
    PlainTextResponse,
    StreamingResponse,
)
from fastapi.staticfiles import StaticFiles
from itsdangerous import BadSignature, URLSafeSerializer
from pydantic import BaseModel

# ---------- logging (JSON to stdout for Cloud Logging) ----------

class JsonLineFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": int(record.created * 1000),
            "level": record.levelname,
            "msg": record.getMessage(),
        }
        if isinstance(record.args, dict):
            payload.update(record.args)
        for k in ("method", "url", "status", "elapsed_ms", "event"):
            v = getattr(record, k, None)
            if v is not None:
                payload[k] = v
        return json.dumps(payload, separators=(",", ":"))


_root = logging.getLogger()
_root.setLevel(logging.INFO)
_h = logging.StreamHandler(sys.stdout)
_h.setFormatter(JsonLineFormatter())
_root.handlers = [_h]
log = logging.getLogger("streamassist")

# ---------- config ----------

ENGINE_RESOURCE = os.environ.get(
    "ENGINE_RESOURCE",
    "projects/254356041555/locations/global/collections/default_collection/engines/jira-testing_1778158449701",
)
ASSISTANT_RESOURCE = f"{ENGINE_RESOURCE}/assistants/default_assistant"
GE_USER_PROJECT = os.environ.get("GE_USER_PROJECT", "vtxdemos")
LOG_PROJECT = os.environ.get("LOG_PROJECT", GE_USER_PROJECT)
DE_HOST = "https://discoveryengine.googleapis.com"
LOGGING_HOST = "https://logging.googleapis.com"
STATIC_DIR = Path(__file__).parent / "static"

# ---------- OAuth / session config ----------

OAUTH_CLIENT_ID = os.environ.get("OAUTH_CLIENT_ID") or ""
# Used to sign the session cookie. Stable across revisions if SESSION_SECRET is
# set in env; otherwise we generate an ephemeral one per process (sessions only
# survive in-memory of one Cloud Run instance, which is fine for this demo).
SESSION_SECRET = os.environ.get("SESSION_SECRET") or secrets.token_urlsafe(32)
SESSION_COOKIE_NAME = "ess_session"
_session_serializer = URLSafeSerializer(SESSION_SECRET, salt="ess-session-v1")

# ---------- Jira federated-connector OAuth (Atlassian 3LO) ----------
#
# Same pattern as semiautonomous-agents/streamassist-oauth-flow-sharepoint
# (Microsoft variant) but stripped of WIF since the user is already on a
# Google identity. Flow:
#   1. Frontend opens popup -> AT_AUTHORIZE_URL with redirect_uri pinned to
#      Google's well-known oauth-redirect page (the only URI registered on
#      Google's BAP-managed Atlassian app).
#   2. Atlassian -> vertexaisearch.cloud.google.com/oauth-redirect?code=...
#   3. Google's redirect page postMessages {fullRedirectUrl} back to opener
#      origin (read from state.origin we encoded).
#   4. Frontend POSTs that URL to /api/jira/exchange with user's Google
#      access token in Authorization header.
#   5. Backend calls dataConnector:acquireAndStoreRefreshToken with the URL;
#      GE swaps the code for an Atlassian refresh token and stores it under
#      the user identity carried by the bearer.
JIRA_CONNECTOR_NAME = os.environ.get(
    "JIRA_CONNECTOR_NAME",
    "projects/254356041555/locations/global/collections/"
    "jira-fed-connector_1779221270798/dataConnector",
)
ATLASSIAN_AUTHORIZE_URL = "https://auth.atlassian.com/authorize"
ATLASSIAN_REDIRECT_URI = "https://vertexaisearch.cloud.google.com/oauth-redirect"
# Google's BAP-managed Atlassian app — fixed; the only client registered with
# ATLASSIAN_REDIRECT_URI as a callback. We can't substitute our own app.
ATLASSIAN_CLIENT_ID = os.environ.get(
    "ATLASSIAN_CLIENT_ID", "PEqLi0lwHtcpIBBU8Dx4PnhuEzMqd07K"
)
ATLASSIAN_SCOPES = " ".join([
    "read:jira-work",
    "read:jira-user",
    "read:user:jira",
    "write:jira-work",
    "offline_access",
])

# Pending consent state -> stores the opener origin keyed by nonce so we can
# verify the postMessage came from a request we initiated.
_pending_jira_consents: dict[str, dict] = {}


OAUTH_SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "openid",
    "email",
    "profile",
]

if not OAUTH_CLIENT_ID:
    logging.getLogger("streamassist").warning(
        "OAUTH_CLIENT_ID not set — running in service-account-only mode. "
        "Sign-In button on the UI will fail until you create the OAuth client "
        "and redeploy with OAUTH_CLIENT_ID set."
    )

# ---------- auth ----------

_creds = None
_auth_mode: Optional[str] = os.environ.get("AUTH_MODE") or None  # "adc" | "gcloud"


def _get_sa_token() -> str:
    """Prefer ADC (Cloud Run metadata server); fall back to gcloud CLI locally.

    Returns the Cloud Run service-account access token. Used for logging tail
    and as a fallback when the end-user has no OAuth access token.
    """
    global _creds, _auth_mode

    # Already decided on gcloud path
    if _auth_mode == "gcloud":
        import subprocess

        return subprocess.check_output(
            ["gcloud", "auth", "print-access-token"],
            env={**os.environ, "GOOGLE_CLOUD_QUOTA_PROJECT": "cloud-llm-preview1"},
        ).decode().strip()

    import google.auth
    import google.auth.transport.requests as gar

    if _creds is None:
        try:
            _creds, _ = google.auth.default(
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            _creds.refresh(gar.Request())
            _auth_mode = "adc"
        except Exception as e:
            # Only fall back to gcloud if the binary is on PATH (i.e. local dev).
            import shutil

            if shutil.which("gcloud"):
                log.info("ADC unavailable, falling back to gcloud: %s", e)
                _auth_mode = "gcloud"
                _creds = None
                return _get_sa_token()
            raise

    if not _creds.valid:
        _creds.refresh(gar.Request())
    return _creds.token


# Backwards-compat alias used elsewhere in this module.
_get_token = _get_sa_token


# ---------- session helpers ----------


def _load_session(cookie_val: Optional[str]) -> Optional[dict]:
    if not cookie_val:
        return None
    try:
        return _session_serializer.loads(cookie_val)
    except BadSignature:
        return None


def _set_session_cookie(resp: Response, payload: dict) -> None:
    val = _session_serializer.dumps(payload)
    resp.set_cookie(
        SESSION_COOKIE_NAME,
        val,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 12,  # 12h
        path="/",
    )


def _user_pseudo_id_from_sub(sub: str) -> str:
    """Deterministic pseudonymous ID derived from the Google `sub` claim.

    GE keys per-user 3LO grants by `userPseudoId`. As long as the same user
    signs into our app AND completes consent at geminienterprise.google.com
    while signed in as the same Google identity, the GE backend can match
    the grant if we use the same derivation. We use sha256(sub)[:32] — a
    common pattern; if GE actually wants the raw `sub`, swap this here.
    """
    return hashlib.sha256(sub.encode("utf-8")).hexdigest()[:32]

# ---------- engine cache ----------

_engine_cache: Optional[dict] = None


async def _fetch_engine_meta(client: httpx.AsyncClient) -> dict:
    global _engine_cache
    if _engine_cache:
        return _engine_cache
    token = _get_token()
    url = f"{DE_HOST}/v1alpha/{ENGINE_RESOURCE}"
    t0 = time.monotonic()
    r = await client.get(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "X-Goog-User-Project": GE_USER_PROJECT,
        },
        timeout=30,
    )
    log.info(
        "engine.get",
        extra={
            "method": "GET",
            "url": url,
            "status": r.status_code,
            "elapsed_ms": int((time.monotonic() - t0) * 1000),
        },
    )
    r.raise_for_status()
    body = r.json()
    _engine_cache = {
        "name": body.get("name"),
        "displayName": body.get("displayName"),
        "dataStoreIds": body.get("dataStoreIds", []),
        "industryVertical": body.get("industryVertical"),
    }
    return _engine_cache


# ---------- streaming JSON-array parser ----------

# DE streamAssist returns a top-level JSON array, with elements arriving over
# multiple chunks separated by commas. We walk the buffer balancing braces &
# string literals to find one full top-level object at a time.

def _scan_top_level_objects(buf: str) -> tuple[list[str], str]:
    """Return (complete_json_object_strs, remainder)."""
    out: list[str] = []
    depth = 0
    start = -1
    in_str = False
    esc = False
    i = 0
    while i < len(buf):
        c = buf[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        else:
            if c == '"':
                in_str = True
            elif c == "{":
                if depth == 0:
                    start = i
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0 and start >= 0:
                    out.append(buf[start : i + 1])
                    start = -1
        i += 1
    rem = buf[i:] if depth == 0 else buf[start if start >= 0 else i :]
    return out, rem


# ---------- SSE helpers ----------

def _sse(event: str, data: dict | str) -> bytes:
    if not isinstance(data, str):
        data = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    # split data across newlines per SSE spec
    lines = "\n".join(f"data: {ln}" for ln in data.split("\n"))
    return f"event: {event}\n{lines}\n\n".encode("utf-8")


def _extract_chat_delta(chunk: dict, include_thoughts: bool) -> str:
    """Walk a streamAssist chunk and return user-visible text delta."""
    out_parts: list[str] = []
    ans = chunk.get("answer", {})
    for reply in ans.get("replies", []):
        gc = reply.get("groundedContent", {})
        content = gc.get("content", {})
        if not include_thoughts and content.get("thought"):
            continue
        text = content.get("text")
        if text:
            out_parts.append(text)
    return "".join(out_parts)


# ---------- app ----------

app = FastAPI(title="exploring-streamassist")


@app.on_event("startup")
async def _startup() -> None:
    # Prefetch engine meta but don't fail startup. We retry on first /api/engine call.
    try:
        async with httpx.AsyncClient() as c:
            await _fetch_engine_meta(c)
    except Exception as e:
        log.warning("engine prefetch failed (will retry on demand): %s", e)


@app.get("/api/health")
async def health() -> dict:
    return {"ok": True, "engine": ENGINE_RESOURCE}


@app.get("/api/engine")
async def engine_meta() -> dict:
    async with httpx.AsyncClient() as c:
        return await _fetch_engine_meta(c)


# ---------- auth endpoints ----------


@app.get("/api/auth/config")
async def auth_config() -> dict:
    """Frontend bootstrap. Returns null client_id when OAUTH_CLIENT_ID is unset
    so the UI can show a friendly notice instead of trying to render the
    Google Sign-In button with a broken client.
    """
    return {
        "client_id": OAUTH_CLIENT_ID or None,
        "scopes": OAUTH_SCOPES,
        "configured": bool(OAUTH_CLIENT_ID),
    }


class VerifyReq(BaseModel):
    credential: str  # Google ID token (JWT) from GIS callback


@app.post("/api/auth/verify")
async def auth_verify(req: VerifyReq, response: Response) -> dict:
    if not OAUTH_CLIENT_ID:
        raise HTTPException(503, "OAUTH_CLIENT_ID not configured on server")
    if not req.credential:
        raise HTTPException(400, "missing credential")
    # Verify the ID token issued by Google to OUR client_id.
    try:
        from google.auth.transport import requests as g_requests
        from google.oauth2 import id_token as g_id_token

        info = g_id_token.verify_oauth2_token(
            req.credential,
            g_requests.Request(),
            OAUTH_CLIENT_ID,
        )
    except Exception as e:
        log.warning("id_token verify failed: %s", e)
        raise HTTPException(401, f"invalid id token: {e}")

    sub = info.get("sub")
    email = info.get("email")
    if not sub:
        raise HTTPException(401, "id token missing sub claim")

    pseudo = _user_pseudo_id_from_sub(sub)
    payload = {
        "sub": sub,
        "email": email,
        "name": info.get("name"),
        "picture": info.get("picture"),
        "user_pseudo_id": pseudo,
        "iat": int(time.time()),
    }
    _set_session_cookie(response, payload)
    return {
        "email": email,
        "sub": sub,
        "user_pseudo_id": pseudo,
        "name": info.get("name"),
        "picture": info.get("picture"),
    }


@app.post("/api/auth/logout")
async def auth_logout(response: Response) -> dict:
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    return {"ok": True}


@app.get("/api/auth/me")
async def auth_me(
    ess_session: Optional[str] = Cookie(default=None, alias=SESSION_COOKIE_NAME),
) -> dict:
    sess = _load_session(ess_session)
    if not sess:
        return {"signed_in": False}
    return {
        "signed_in": True,
        "email": sess.get("email"),
        "name": sess.get("name"),
        "picture": sess.get("picture"),
        "user_pseudo_id": sess.get("user_pseudo_id"),
    }


@app.get("/api/auth/jira-consent-url")
async def auth_jira_consent_url(request: Request) -> dict:
    """Legacy endpoint — kept so older deployments keep working.

    Delegates to /api/jira/auth-url which is the real implementation.
    """
    return await jira_auth_url(request)


@app.get("/api/jira/auth-url")
async def jira_auth_url(request: Request) -> dict:
    """Build the Atlassian 3LO authorize URL for the Jira connector.

    state is a base64url JSON blob with `origin` (so Google's redirect page
    knows where to postMessage the result) and a server-side `nonce` we
    later verify when /api/jira/exchange is called.
    """
    import base64
    from urllib.parse import urlencode

    origin = request.headers.get("origin") or str(request.base_url).rstrip("/")
    nonce = secrets.token_urlsafe(16)
    _pending_jira_consents[nonce] = {
        "origin": origin,
        "ts": int(time.time()),
    }
    # Reap entries older than 10 min to keep the dict from growing unbounded.
    cutoff = int(time.time()) - 600
    for k, v in list(_pending_jira_consents.items()):
        if v.get("ts", 0) < cutoff:
            _pending_jira_consents.pop(k, None)

    state_obj = {"origin": origin, "nonce": nonce, "useBroadcastChannel": "false"}
    state_b64 = base64.b64encode(json.dumps(state_obj).encode()).decode()
    params = {
        "audience": "api.atlassian.com",
        "client_id": ATLASSIAN_CLIENT_ID,
        "scope": ATLASSIAN_SCOPES,
        "redirect_uri": ATLASSIAN_REDIRECT_URI,
        "state": state_b64,
        "response_type": "code",
        "prompt": "consent",
    }
    auth_url = f"{ATLASSIAN_AUTHORIZE_URL}?{urlencode(params)}"
    return {"auth_url": auth_url, "nonce": nonce}


class JiraExchangeReq(BaseModel):
    fullRedirectUrl: str


@app.post("/api/jira/exchange")
async def jira_exchange(
    body: JiraExchangeReq,
    authorization: Optional[str] = Header(default=None),
    ess_session: Optional[str] = Cookie(default=None, alias=SESSION_COOKIE_NAME),
) -> JSONResponse:
    """Hand the fullRedirectUrl off to GE, which swaps the code for a refresh
    token and stores it keyed by the user identity in the bearer.

    Requires a per-user Google OAuth bearer (NOT the SA token) so GE writes
    the grant under the same identity that future /api/assist calls present.
    """
    import base64
    from urllib.parse import urlparse, parse_qs

    user_token: Optional[str] = None
    if authorization and authorization.lower().startswith("bearer "):
        cand = authorization.split(" ", 1)[1].strip()
        if cand:
            user_token = cand
    if not user_token:
        return JSONResponse(
            {"success": False, "error": "missing user OAuth bearer; sign in first"},
            status_code=401,
        )

    # Verify the state nonce matches one we issued (CSRF guard).
    try:
        parsed = urlparse(body.fullRedirectUrl)
        qs = parse_qs(parsed.query)
        raw_state = qs.get("state", [""])[0]
        state = json.loads(base64.b64decode(raw_state).decode())
        nonce = state.get("nonce")
    except Exception as ex:
        return JSONResponse(
            {"success": False, "error": f"unparseable state: {ex}"},
            status_code=400,
        )
    if not nonce or nonce not in _pending_jira_consents:
        return JSONResponse(
            {"success": False, "error": "unknown or expired nonce"},
            status_code=400,
        )
    _pending_jira_consents.pop(nonce, None)

    # Call GE's acquireAndStoreRefreshToken.
    url = f"{DE_HOST}/v1alpha/{JIRA_CONNECTOR_NAME}:acquireAndStoreRefreshToken"
    headers = {
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": GE_USER_PROJECT,
    }
    payload = {"fullRedirectUri": body.fullRedirectUrl}
    t_start = time.monotonic()
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(url, headers=headers, json=payload)
        except Exception as ex:
            return JSONResponse(
                {"success": False, "error": f"network: {ex}"}, status_code=502
            )
    elapsed_ms = int((time.monotonic() - t_start) * 1000)
    log.info(
        "jira acquireAndStoreRefreshToken",
        extra={"event": "jira_exchange", "status": resp.status_code, "elapsed_ms": elapsed_ms},
    )
    if resp.status_code >= 400:
        return JSONResponse(
            {
                "success": False,
                "error": resp.text[:500],
                "status": resp.status_code,
            },
            status_code=resp.status_code,
        )
    return JSONResponse({"success": True, "elapsed_ms": elapsed_ms})


@app.get("/api/jira/check-connection")
async def jira_check_connection(
    authorization: Optional[str] = Header(default=None),
) -> JSONResponse:
    """Probe whether a Jira refresh-token grant already exists under the
    caller's identity. Used by the UI's fallback path: when postMessage
    from Google's redirect page doesn't arrive (COOP can sever it), we
    can still confirm consent landed by trying to acquire an access token.
    """
    user_token: Optional[str] = None
    if authorization and authorization.lower().startswith("bearer "):
        cand = authorization.split(" ", 1)[1].strip()
        if cand:
            user_token = cand
    if not user_token:
        return JSONResponse(
            {"connected": False, "error": "missing user OAuth bearer"},
            status_code=401,
        )

    url = f"{DE_HOST}/v1alpha/{JIRA_CONNECTOR_NAME}:acquireAccessToken"
    headers = {
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": GE_USER_PROJECT,
    }
    t_start = time.monotonic()
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.post(url, headers=headers, json={})
        except Exception as ex:
            return JSONResponse(
                {"connected": False, "error": f"network: {ex}"}, status_code=502
            )
    elapsed_ms = int((time.monotonic() - t_start) * 1000)
    if resp.status_code >= 400:
        log.info(
            "jira check-connection negative",
            extra={"event": "jira_check", "status": resp.status_code, "elapsed_ms": elapsed_ms},
        )
        return JSONResponse(
            {"connected": False, "status": resp.status_code, "error": resp.text[:300]},
        )
    try:
        body = resp.json()
    except Exception:
        body = {}
    connected = bool(body.get("accessToken"))
    log.info(
        "jira check-connection",
        extra={"event": "jira_check", "connected": connected, "elapsed_ms": elapsed_ms},
    )
    return JSONResponse({"connected": connected, "elapsed_ms": elapsed_ms})


class AssistReq(BaseModel):
    question: str
    session: Optional[str] = None
    include_thoughts: bool = False


@app.post("/api/assist")
async def assist(
    req: AssistReq,
    request: Request,
    authorization: Optional[str] = Header(default=None),
    ess_session: Optional[str] = Cookie(default=None, alias=SESSION_COOKIE_NAME),
) -> StreamingResponse:
    if not req.question.strip():
        raise HTTPException(400, "empty question")

    session_id = req.session or f"local-{uuid.uuid4().hex[:8]}"

    # streamAssist expects "/sessions/-" sentinel for ephemeral, but to thread
    # conversation we'd need to register a session. For demo we use the sentinel
    # but echo a stable local id back so the UI can correlate logs.
    session_resource = (
        req.session
        if req.session and req.session.startswith("projects/")
        else f"{ENGINE_RESOURCE}/sessions/-"
    )

    # ---- Decide auth mode ----
    user_token: Optional[str] = None
    if authorization and authorization.lower().startswith("bearer "):
        candidate = authorization.split(" ", 1)[1].strip()
        # Reject obviously empty / clearly-an-ID-token (JWTs start with eyJ but
        # GIS access tokens are opaque ya29.* strings). We accept anything
        # non-empty and let DE reject if invalid.
        if candidate:
            user_token = candidate

    sess = _load_session(ess_session)

    auth_mode = "service_account"
    bearer_token: str
    if user_token:
        auth_mode = "user_oauth"
        bearer_token = user_token
    else:
        bearer_token = _get_sa_token()
        if sess:
            log.warning(
                "user signed in but no Authorization header; falling back to SA"
            )
        else:
            log.info("anonymous assist call; using SA token")

    body: dict = {
        "query": {"text": req.question},
        "session": session_resource,
        "assistSkippingMode": "REQUEST_ASSIST",
    }
    # Intentionally NOT setting body["userInfo"].userPseudoId — GE derives the
    # per-user identity (and therefore the 3LO grant lookup key) from the OAuth
    # bearer token. Sending our own sha256(sub) pseudoId would key into a
    # different slot than the one Console writes during consent, so federated
    # connectors would never find the stored refresh token.

    url = f"{DE_HOST}/v1alpha/{ASSISTANT_RESOURCE}:streamAssist"

    async def gen() -> AsyncIterator[bytes]:
        t_start = time.monotonic()
        # Surface which auth mode we're using so the UI can warn user if SA.
        yield _sse(
            "auth_mode",
            {
                "mode": auth_mode,
                "user_pseudo_id": (sess or {}).get("user_pseudo_id")
                if auth_mode == "user_oauth"
                else None,
                "email": (sess or {}).get("email") if auth_mode == "user_oauth" else None,
            },
        )
        # Tell the client we started + show the request that's being sent.
        yield _sse(
            "request",
            {
                "session_id": session_id,
                "method": "POST",
                "url": url,
                "auth_mode": auth_mode,
                "headers": {
                    "Authorization": "Bearer <REDACTED>",
                    "X-Goog-User-Project": GE_USER_PROJECT,
                    "Content-Type": "application/json",
                },
                "body": body,
                "started_at": int(time.time() * 1000),
            },
        )

        token = bearer_token
        timeout = httpx.Timeout(connect=15.0, read=300.0, write=30.0, pool=30.0)
        # Record the wall-clock window so the fallback trace lookup is bounded.
        window_start_iso = _dt.datetime.now(_dt.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        trace_emitted = False
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                t0 = time.monotonic()
                async with client.stream(
                    "POST",
                    url,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "X-Goog-User-Project": GE_USER_PROJECT,
                        "Content-Type": "application/json",
                    },
                    json=body,
                ) as resp:
                    log.info(
                        "streamAssist.start",
                        extra={"method": "POST", "url": url, "status": resp.status_code},
                    )
                    # Try to capture trace from X-Cloud-Trace-Context header (if present).
                    xctc = resp.headers.get("x-cloud-trace-context") or resp.headers.get(
                        "X-Cloud-Trace-Context"
                    )
                    if xctc:
                        # header format: TRACE_ID/SPAN_ID;o=TRACE_TRUE
                        trace_hex = xctc.split("/", 1)[0].strip()
                        if trace_hex:
                            trace_emitted = True
                            yield _sse(
                                "trace",
                                {
                                    "trace_id": trace_hex,
                                    "project": LOG_PROJECT,
                                    "source": "response_header",
                                },
                            )
                    if resp.status_code >= 400:
                        err_body = (await resp.aread()).decode("utf-8", "replace")
                        yield _sse(
                            "error",
                            {
                                "status": resp.status_code,
                                "body": err_body[:4000],
                                "elapsed_ms": int((time.monotonic() - t0) * 1000),
                            },
                        )
                        return

                    buf = ""
                    n = 0
                    async for chunk in resp.aiter_text():
                        if not chunk:
                            continue
                        buf += chunk
                        objs, buf = _scan_top_level_objects(buf)
                        for obj_str in objs:
                            try:
                                obj = json.loads(obj_str)
                            except Exception as e:
                                yield _sse(
                                    "error",
                                    {
                                        "parse_error": str(e),
                                        "snippet": obj_str[:500],
                                    },
                                )
                                continue
                            n += 1
                            # chat delta
                            delta = _extract_chat_delta(obj, req.include_thoughts)
                            if delta:
                                yield _sse(
                                    "chat",
                                    {
                                        "delta": delta,
                                        "seq": n,
                                        "t_ms": int(
                                            (time.monotonic() - t_start) * 1000
                                        ),
                                    },
                                )
                            # full raw
                            yield _sse(
                                "raw",
                                {
                                    "seq": n,
                                    "t_ms": int((time.monotonic() - t_start) * 1000),
                                    "chunk": obj,
                                },
                            )
                            # avoid starving the event loop on big bursts
                            await asyncio.sleep(0)

                    log.info(
                        "streamAssist.done",
                        extra={
                            "method": "POST",
                            "url": url,
                            "status": resp.status_code,
                            "elapsed_ms": int((time.monotonic() - t0) * 1000),
                            "event": f"events={n}",
                        },
                    )

                    # Fallback trace discovery: if we never got x-cloud-trace-context,
                    # poll the activity log for ~6s looking for the most recent
                    # StreamAssist entry for this engine inside our wall-clock window.
                    if not trace_emitted:
                        try:
                            trace_hex = await _lookup_recent_trace(
                                client, window_start_iso
                            )
                            if trace_hex:
                                trace_emitted = True
                                yield _sse(
                                    "trace",
                                    {
                                        "trace_id": trace_hex,
                                        "project": LOG_PROJECT,
                                        "source": "log_lookup",
                                    },
                                )
                            else:
                                yield _sse(
                                    "trace",
                                    {
                                        "trace_id": None,
                                        "project": LOG_PROJECT,
                                        "source": "unavailable",
                                        "note": "no x-cloud-trace-context; no matching activity log in window",
                                    },
                                )
                        except Exception as ex:
                            log.warning("trace lookup failed: %s", ex)
                            yield _sse(
                                "trace",
                                {
                                    "trace_id": None,
                                    "project": LOG_PROJECT,
                                    "source": "error",
                                    "note": str(ex)[:200],
                                },
                            )

                    yield _sse(
                        "done",
                        {
                            "events": n,
                            "elapsed_ms": int((time.monotonic() - t0) * 1000),
                        },
                    )
        except Exception as e:
            log.exception("stream failed")
            yield _sse("error", {"exception": str(e)})

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


# ---------- cloud logging tail ----------


def _log_filter_for_trace(trace_hex: str, window_start_iso: str) -> str:
    """Filter that scopes by trace + the two log streams we care about.

    Critically: Cloud Logging's `trace=` indexed field uses the BARE hex token
    for discoveryengine.googleapis.com entries (NOT the projects/X/traces/Y
    long form). A timestamp lower bound is required to make the query cheap.
    """
    return (
        f'trace="{trace_hex}"\n'
        f'timestamp >= "{window_start_iso}"\n'
        '(logName="projects/' + LOG_PROJECT + '/logs/'
        'discoveryengine.googleapis.com%2Fgemini_enterprise_user_activity"'
        ' OR logName=~"discoveryengine.googleapis.com%2Fgen_ai")'
    )


async def _list_log_entries(
    client: httpx.AsyncClient,
    flt: str,
    *,
    page_size: int = 100,
    order: str = "timestamp asc",
) -> list[dict]:
    token = _get_token()
    r = await client.post(
        f"{LOGGING_HOST}/v2/entries:list",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": GE_USER_PROJECT,
        },
        json={
            "resourceNames": [f"projects/{LOG_PROJECT}"],
            "filter": flt,
            "orderBy": order,
            "pageSize": page_size,
        },
        timeout=30,
    )
    if r.status_code >= 400:
        raise RuntimeError(f"logging.entries.list {r.status_code}: {r.text[:500]}")
    return r.json().get("entries", []) or []


async def _lookup_recent_trace(
    client: httpx.AsyncClient, window_start_iso: str
) -> Optional[str]:
    """Fallback when x-cloud-trace-context is absent.

    Polls the user_activity log up to ~6s for a StreamAssist entry on our
    engine inside the wall-clock window we opened. Returns the bare hex trace.
    """
    name_prefix = (
        f'logName="projects/{LOG_PROJECT}/logs/'
        'discoveryengine.googleapis.com%2Fgemini_enterprise_user_activity"'
    )
    method_filter = (
        'jsonPayload.logMetadata.methodName="StreamAssist"'
    )
    engine_filter = (
        'jsonPayload.logMetadata.name=~"' + ASSISTANT_RESOURCE.replace(".", "\\.") + '"'
    )
    flt = (
        f"{name_prefix}\n"
        f"{method_filter}\n"
        f"{engine_filter}\n"
        f'timestamp >= "{window_start_iso}"'
    )
    deadline = time.monotonic() + 20.0
    poll = 1.0
    while time.monotonic() < deadline:
        try:
            entries = await _list_log_entries(client, flt, page_size=5, order="timestamp desc")
        except Exception as e:
            log.warning("trace lookup poll error: %s", e)
            entries = []
        for e in entries:
            t = e.get("trace")
            if t:
                # strip any "projects/.../traces/" prefix just in case
                return t.rsplit("/", 1)[-1]
        await asyncio.sleep(poll)
        # Backoff a little so we don't hammer the API
        poll = min(poll + 0.5, 2.5)
    return None


def _entry_event_name(e: dict) -> str:
    labels = e.get("labels") or {}
    en = labels.get("event.name")
    if en:
        return en
    ln = e.get("logName", "").rsplit("/", 1)[-1]
    if "gen_ai" in ln:
        return ln.replace("discoveryengine.googleapis.com%2F", "")
    if "gemini_enterprise_user_activity" in ln:
        return "user_activity"
    return ln or "entry"


def _entry_role(e: dict) -> Optional[str]:
    jp = e.get("jsonPayload") or {}
    # gen_ai.user.message → role is in content.role
    content = jp.get("content")
    if isinstance(content, dict):
        r = content.get("role")
        if r:
            return r
    # gen_ai.choice has top-level finish_reason; surface that
    if "finish_reason" in jp:
        return jp.get("finish_reason")
    return None


def _entry_method(e: dict) -> Optional[str]:
    jp = e.get("jsonPayload") or {}
    md = jp.get("logMetadata") or {}
    return md.get("methodName")


def _summarize_entry(e: dict) -> dict:
    """Project a Cloud Logging entry to the small payload the frontend needs."""
    jp = e.get("jsonPayload") or {}
    return {
        "insertId": e.get("insertId"),
        "timestamp": e.get("timestamp"),
        "logName": e.get("logName"),
        "spanId": e.get("spanId"),
        "trace": e.get("trace"),
        "labels": e.get("labels") or {},
        "eventName": _entry_event_name(e),
        "role": _entry_role(e),
        "methodName": _entry_method(e),
        "userIamPrincipal": jp.get("userIamPrincipal"),
        "payload": jp,
    }


@app.get("/api/logs/{trace_id}")
async def logs_tail(trace_id: str, request: Request) -> StreamingResponse:
    # validate trace ID shape (32 hex)
    if not re.fullmatch(r"[0-9a-fA-F]{16,32}", trace_id):
        raise HTTPException(400, "invalid trace_id")

    window_start_iso = (
        _dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(minutes=5)
    ).strftime("%Y-%m-%dT%H:%M:%SZ")

    async def gen() -> AsyncIterator[bytes]:
        seen: set[str] = set()
        emitted = 0
        last_emit_at: float | None = None
        t_start = time.monotonic()
        try:
            async with httpx.AsyncClient() as client:
                flt = _log_filter_for_trace(trace_id, window_start_iso)
                yield _sse(
                    "log_meta",
                    {
                        "trace_id": trace_id,
                        "project": LOG_PROJECT,
                        "filter": flt,
                        "poll_interval_s": 2,
                    },
                )
                while True:
                    # hard timeout
                    elapsed = time.monotonic() - t_start
                    if elapsed > 90:
                        yield _sse(
                            "log_done",
                            {
                                "reason": "timeout_90s",
                                "entries": emitted,
                                "elapsed_s": round(elapsed, 1),
                            },
                        )
                        return
                    # quiet timeout (only valid after we got at least one entry)
                    if (
                        last_emit_at is not None
                        and (time.monotonic() - last_emit_at) > 30
                        and emitted > 0
                    ):
                        yield _sse(
                            "log_done",
                            {
                                "reason": "quiet_30s",
                                "entries": emitted,
                                "elapsed_s": round(elapsed, 1),
                            },
                        )
                        return
                    if await request.is_disconnected():
                        return
                    try:
                        entries = await _list_log_entries(
                            client, flt, page_size=100, order="timestamp asc"
                        )
                    except Exception as ex:
                        log.warning("logs poll failed: %s", ex)
                        yield _sse(
                            "log_error",
                            {"message": str(ex)[:500]},
                        )
                        await asyncio.sleep(2.0)
                        continue

                    new_entries: list[dict] = []
                    for e in entries:
                        iid = e.get("insertId")
                        if not iid or iid in seen:
                            continue
                        seen.add(iid)
                        new_entries.append(e)

                    if new_entries:
                        for e in new_entries:
                            yield _sse(
                                "log_entry",
                                _summarize_entry(e),
                            )
                        emitted += len(new_entries)
                        last_emit_at = time.monotonic()
                        # tick a counter so the frontend can show "n entries received"
                        yield _sse(
                            "log_tick",
                            {"entries": emitted, "elapsed_s": round(time.monotonic() - t_start, 1)},
                        )

                    await asyncio.sleep(2.0)
        except asyncio.CancelledError:
            return

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


# ---------- static ----------


class _NoCacheStatic(StaticFiles):
    """StaticFiles subclass that disables browser caching so deploys
    aren't masked by a stale app.js / styles.css in the user's tab.
    Tiny site, no CDN — fine to skip caching entirely."""

    async def get_response(self, path, scope):
        resp = await super().get_response(path, scope)
        resp.headers["Cache-Control"] = "no-store, must-revalidate"
        resp.headers["Pragma"] = "no-cache"
        return resp


if STATIC_DIR.exists():
    app.mount("/static", _NoCacheStatic(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def root() -> FileResponse:
    idx = STATIC_DIR / "index.html"
    if not idx.exists():
        return JSONResponse({"error": "index.html missing"}, status_code=500)
    return FileResponse(
        str(idx),
        headers={"Cache-Control": "no-store, must-revalidate", "Pragma": "no-cache"},
    )
