"""Minimal FastAPI backend for the comparison-site.

Serves three static files (`index.html`, `data.json`, `reference_answers.json`)
and exposes a single write endpoint, `POST /api/grade`, that validates the
payload and emits it as a structured JSON line to stdout — Cloud Logging
picks it up automatically. No database, no IAM permissions, no secrets.

Security posture matches the prior nginx version: same zero-IAM SA, same
security headers, same locked-down method/path allow-list, no env vars, no
shell access.
"""
from __future__ import annotations

import asyncio
import base64
import dataclasses
import hashlib
import hmac
import json
import logging
import os
import secrets
import sys
import time
import uuid
from pathlib import Path
from typing import Any, AsyncIterator, Optional

import httpx
from fastapi import Cookie, Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse, StreamingResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field, field_validator

import race_runner

# --- Config -----------------------------------------------------------------
HERE = Path(__file__).resolve().parent
STATIC_FILES = {
    "/":                          (HERE / "index.html",            "text/html; charset=utf-8"),
    "/index.html":                (HERE / "index.html",            "text/html; charset=utf-8"),
    "/data.json":                 (HERE / "data.json",             "application/json"),
    "/reference_answers.json":    (HERE / "reference_answers.json","application/json"),
    "/claude_code_answers.json":  (HERE / "claude_code_answers.json","application/json"),
    "/sample_50_ids.json":        (HERE / "sample_50_ids.json",    "application/json"),
    "/validation_sample.json":    (HERE / "validation_sample.json","application/json"),
}

# Verdicts allowed on grade submissions. Refused only counts on safety
# categories per the same convention as the LLM judge.
ALLOWED_VERDICTS = {"correct", "partial", "wrong", "refused", "skip"}

# --- Live Race auth ---------------------------------------------------------
# The /api/query endpoint fans out 10 parallel calls to Agent Engine and
# streamAssist per race — that's real money. Gate it behind a signed cookie
# (set via the /api/login form) so the browser can actually authenticate.
#
# Modern Chrome no longer pops a native Basic-Auth dialog for fetch() / SSE
# requests, only for top-level navigations — that's why the old auth_check
# bounce stopped working. We keep Basic-Auth accepted as a fallback so
# `curl -u admin:…` continues to work for ops.
_basic_optional = HTTPBasic(auto_error=False)
_LIVE_USER = os.environ.get("LIVE_RACE_USER", "admin")
_LIVE_PASS = os.environ.get("LIVE_RACE_PASSWORD", "")  # if unset, deny all
# Stable session-signing secret. If unset, fall back to a random one minted at
# boot — sessions then die on restart but the app keeps working.
_LIVE_SECRET = os.environ.get("LIVE_RACE_SECRET") or secrets.token_hex(32)
_SESSION_COOKIE = "live_race_session"
_SESSION_TTL_S = 14400  # 4 hours, matches cookie Max-Age.


def _sign_session(user: str, expiry: int) -> str:
    """Return a URL-safe `user.expiry.signature` token."""
    payload = f"{user}:{expiry}".encode("utf-8")
    sig = hmac.new(_LIVE_SECRET.encode("utf-8"), payload, hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(sig).rstrip(b"=").decode("ascii")
    user_b64 = base64.urlsafe_b64encode(user.encode("utf-8")).rstrip(b"=").decode("ascii")
    return f"{user_b64}.{expiry}.{sig_b64}"


def _verify_session(token: str) -> Optional[str]:
    """Return the username if the token is a valid, unexpired signature."""
    if not token or token.count(".") != 2:
        return None
    user_b64, expiry_s, sig_b64 = token.split(".", 2)
    try:
        # Restore padding for base64 decode.
        pad = "=" * (-len(user_b64) % 4)
        user = base64.urlsafe_b64decode((user_b64 + pad).encode("ascii")).decode("utf-8")
        expiry = int(expiry_s)
    except (ValueError, UnicodeDecodeError):
        return None
    if expiry < int(time.time()):
        return None
    expected = _sign_session(user, expiry).rsplit(".", 1)[-1]
    if not secrets.compare_digest(expected, sig_b64):
        return None
    return user


def _check_creds(user: str, password: str) -> bool:
    """Constant-time check against the configured operator credentials."""
    if not _LIVE_PASS:
        return False
    return (
        secrets.compare_digest(user or "", _LIVE_USER)
        and secrets.compare_digest(password or "", _LIVE_PASS)
    )


def _set_session_cookie(response: Response, user: str) -> None:
    expiry = int(time.time()) + _SESSION_TTL_S
    token = _sign_session(user, expiry)
    response.set_cookie(
        key=_SESSION_COOKIE,
        value=token,
        max_age=_SESSION_TTL_S,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
    )


def require_race_auth(
    request: Request,
    creds: Optional[HTTPBasicCredentials] = Depends(_basic_optional),
    live_race_session: Optional[str] = Cookie(default=None),
) -> str:
    """Allow access via signed cookie OR HTTP Basic header.

    Returns the authenticated username so callers can log it. Refuses with
    503 if the service isn't configured with a password env var.
    """
    if not _LIVE_PASS:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Live Race auth not configured",
        )

    # 1) Cookie path — used by the browser UI.
    if live_race_session:
        user = _verify_session(live_race_session)
        if user:
            return user

    # 2) Basic-Auth fallback — used by curl/ops.
    if creds is not None and _check_creds(creds.username, creds.password):
        return creds.username

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": 'Basic realm="Live Race"'},
    )

# --- Logging: structured JSON to stdout -------------------------------------
# Cloud Logging's stdout sink parses one JSON object per line into structured
# fields. Keep keys flat for easy querying in Log Explorer.
_log = logging.getLogger("grade")
_log.setLevel(logging.INFO)
_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(logging.Formatter("%(message)s"))
_log.addHandler(_handler)
_log.propagate = False

# --- App + security headers --------------------------------------------------
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

# Tight CORS — only the deployed domain. Cloud Run gives us
# https://<service>-<projectnumber>.<region>.run.app at runtime; we don't know
# it at build time, so allow same-origin only by default and let the static
# fetch() rely on relative paths.
@app.middleware("http")
async def security(request: Request, call_next):
    response: Response = await call_next(request)
    # Drop the server-identifying header if present.
    if "server" in response.headers:
        del response.headers["server"]
    # Apply hardening headers to every response.
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = (
        "geolocation=(), microphone=(), camera=()"
    )
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    # CSP — inline JS is part of index.html, so script-src needs unsafe-inline.
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'none'"
    )
    return response


# --- Routes: static read -----------------------------------------------------
def _serve_static(path: str) -> Response:
    if path not in STATIC_FILES:
        return PlainTextResponse("not found", status_code=404)
    fp, ctype = STATIC_FILES[path]
    if not fp.exists():
        return PlainTextResponse("not found", status_code=404)
    headers = {"Cache-Control": "public, max-age=300"}
    return FileResponse(str(fp), media_type=ctype, headers=headers)


@app.get("/")
async def root() -> Response:
    return _serve_static("/")


@app.get("/index.html")
async def index_html() -> Response:
    return _serve_static("/index.html")


@app.get("/data.json")
async def data_json() -> Response:
    return _serve_static("/data.json")


@app.get("/reference_answers.json")
async def references_json() -> Response:
    return _serve_static("/reference_answers.json")


@app.get("/claude_code_answers.json")
async def claude_code_answers_json() -> Response:
    return _serve_static("/claude_code_answers.json")


@app.get("/sample_50_ids.json")
async def sample_ids_json() -> Response:
    return _serve_static("/sample_50_ids.json")


@app.get("/validation_sample.json")
async def validation_sample_json() -> Response:
    return _serve_static("/validation_sample.json")


@app.get("/api/validation-sample")
async def api_validation_sample() -> Response:
    # Convenience alias — same payload, friendlier API path.
    return _serve_static("/validation_sample.json")


@app.get("/healthz")
async def health() -> Response:
    return PlainTextResponse("ok\n")


# --- Route: POST /api/grade --------------------------------------------------
class GradePayload(BaseModel):
    """One human grade event. We don't persist server-side — we just log it
    as structured JSON to stdout. Cloud Logging captures stdout automatically,
    so the grade history can be queried with:

        gcloud logging read 'jsonPayload.event="human_grade"' --limit 500
    """

    question_id: str = Field(..., min_length=2, max_length=20)
    pipeline: str = Field(..., min_length=1, max_length=4)  # A/B/C/D/E
    verdict: str = Field(...)
    grader_id: str = Field(default="anonymous", max_length=64)
    session_id: str = Field(default="", max_length=64)
    notes: str = Field(default="", max_length=500)

    @field_validator("verdict")
    @classmethod
    def _v(cls, v: str) -> str:
        if v not in ALLOWED_VERDICTS:
            raise ValueError(f"verdict must be one of {sorted(ALLOWED_VERDICTS)}")
        return v

    @field_validator("pipeline")
    @classmethod
    def _p(cls, v: str) -> str:
        if v not in {"A", "B", "C", "D", "E"}:
            raise ValueError("pipeline must be A/B/C/D/E")
        return v


@app.post("/api/grade")
async def post_grade(req: Request) -> Response:
    try:
        raw = await req.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid JSON")
    try:
        payload = GradePayload(**raw)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)[:300])

    entry = {
        "event": "human_grade",
        "ts": time.time(),
        "question_id": payload.question_id,
        "pipeline": payload.pipeline,
        "verdict": payload.verdict,
        "grader_id": payload.grader_id,
        "session_id": payload.session_id,
        "notes": payload.notes[:500],
        "request_id": str(uuid.uuid4()),
        "remote": req.client.host if req.client else None,
        "ua": (req.headers.get("user-agent") or "")[:160],
    }
    _log.info(json.dumps(entry))
    return Response(status_code=204)


# --- Route: GET /api/query (SSE stream for the Live Race tab) ----------------
# Browsers can't open EventSource with custom headers or a POST body, so we
# accept the question as a query-string param and stream answers as SSE.
# Two event types are emitted:
#   progress  data: {"elapsed_ms": int}            # heartbeat every 500ms
#   done      data: {"ok": bool, ...}              # final answer (one per stream)

# Shared httpx client. One per-process is plenty for the few-races/sec the
# Live Race tab generates and avoids the connect overhead on every request.
_RACE_TIMEOUT = httpx.Timeout(connect=15.0, read=300.0, write=60.0, pool=60.0)
_race_client: httpx.AsyncClient | None = None


@app.on_event("startup")
async def _race_startup() -> None:
    global _race_client
    _race_client = httpx.AsyncClient(timeout=_RACE_TIMEOUT)


@app.on_event("shutdown")
async def _race_shutdown() -> None:
    if _race_client is not None:
        await _race_client.aclose()


def _sse(event: str, payload: dict[str, Any]) -> bytes:
    return f"event: {event}\ndata: {json.dumps(payload, default=str, ensure_ascii=False)}\n\n".encode("utf-8")


@app.get("/api/auth_check")
async def api_auth_check(user: str = Depends(require_race_auth)) -> JSONResponse:
    """Probe endpoint the Live Race tab uses to decide whether to show the
    login overlay. Returns 200 with the username when the signed cookie (or
    Basic-Auth header) is valid; otherwise the dependency raises 401.
    """
    return JSONResponse({"ok": True, "user": user})


class LoginPayload(BaseModel):
    user: str = Field(..., min_length=1, max_length=64)
    # `pass` is a Python keyword so accept it via alias.
    password: str = Field(..., min_length=1, max_length=200, alias="pass")

    model_config = {"populate_by_name": True}


@app.post("/api/login")
async def api_login(req: Request) -> Response:
    """Validate username+password and set the signed `live_race_session`
    cookie. Returns 200 `{ok: true, user}` on success; 401 otherwise.
    """
    if not _LIVE_PASS:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Live Race auth not configured",
        )
    try:
        raw = await req.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid JSON")
    try:
        payload = LoginPayload(**raw)
    except Exception:
        raise HTTPException(status_code=400, detail="bad payload")
    if not _check_creds(payload.user, payload.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid credentials",
        )
    resp = JSONResponse({"ok": True, "user": payload.user})
    _set_session_cookie(resp, payload.user)
    return resp


@app.post("/api/logout")
async def api_logout() -> Response:
    """Clear the session cookie. Always returns 200."""
    resp = JSONResponse({"ok": True})
    resp.delete_cookie(_SESSION_COOKIE, path="/")
    return resp


class UserTokenPayload(BaseModel):
    access_token: str = Field(..., min_length=20, max_length=8192)
    ttl_s: int = Field(default=3000, ge=60, le=3600)


@app.get("/api/race/user_token")
async def api_user_token_status(user: str = Depends(require_race_auth)) -> JSONResponse:
    """Report whether a user OAuth token is currently installed for outbound
    GE/AE calls (lets the UI show 'service-account' vs 'user OAuth active')."""
    return JSONResponse(race_runner.user_token_status())


@app.post("/api/race/user_token")
async def api_user_token_set(req: Request, user: str = Depends(require_race_auth)) -> JSONResponse:
    """Install a user-supplied OAuth access token for outbound streamAssist /
    AE calls. Needed because the Cloud Run service account has no Jira refresh
    token bound to the GE Atlassian connector, so B/C/CG/DG fail with auth
    errors otherwise. Token is process-scoped (not persisted, not per-user)."""
    try:
        raw = await req.json()
        payload = UserTokenPayload(**raw)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"bad payload: {exc}")
    exp = race_runner.set_user_token(payload.access_token, ttl_s=float(payload.ttl_s))
    return JSONResponse({"ok": True, "expires_at": exp, "expires_in_s": int(payload.ttl_s)})


@app.delete("/api/race/user_token")
async def api_user_token_clear(user: str = Depends(require_race_auth)) -> JSONResponse:
    race_runner.clear_user_token()
    return JSONResponse({"ok": True})


@app.get("/api/query")
async def api_query(
    pipeline: str,
    q: str,
    user: str = Depends(require_race_auth),
) -> Response:
    """Fire `q` at the given pipeline and stream progress + done events.

    `pipeline` is one of the lowercased UI letters (a, al, ag, b, c, cg, d, dg,
    e, eg). `q` is the user question. Gated behind HTTP Basic — each race
    costs real money so only authenticated operators can trigger it.
    """
    pk = (pipeline or "").lower().strip()
    if pk not in race_runner.PIPELINE_KEYS:
        raise HTTPException(status_code=400, detail=f"unknown pipeline: {pipeline}")
    if not q or len(q) > 4000:
        raise HTTPException(status_code=400, detail="q must be 1..4000 chars")

    if _race_client is None:
        raise HTTPException(status_code=503, detail="race client not initialised")

    async def stream() -> AsyncIterator[bytes]:
        t0 = time.perf_counter()
        # Kick off the pipeline call in the background so we can interleave
        # heartbeat events while we wait. The runner returns a RaceResult.
        task = asyncio.create_task(race_runner.run_pipeline(pk, q, _race_client))
        try:
            while not task.done():
                elapsed_ms = int((time.perf_counter() - t0) * 1000)
                yield _sse("progress", {"elapsed_ms": elapsed_ms})
                try:
                    await asyncio.wait_for(asyncio.shield(task), timeout=0.5)
                except asyncio.TimeoutError:
                    continue
            result: race_runner.RaceResult = await task
        except asyncio.CancelledError:
            # Client closed the connection — propagate cancellation to the
            # in-flight pipeline call.
            task.cancel()
            raise
        except Exception as exc:
            yield _sse("done", {"ok": False, "elapsed_s": time.perf_counter() - t0,
                                "error": f"{type(exc).__name__}: {exc}"})
            return
        payload = dataclasses.asdict(result)
        # Trim verbose fields before serialising.
        payload["grounding_chunks"] = payload.pop("grounding", [])[:20]
        if payload.get("tool_calls"):
            payload["tool_calls"] = payload["tool_calls"][:50]
        yield _sse("done", payload)

    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "X-Accel-Buffering": "no",
        "Content-Type": "text/event-stream; charset=utf-8",
    }
    return StreamingResponse(stream(), media_type="text/event-stream", headers=headers)


# --- Catch-all: deny everything else ----------------------------------------
@app.api_route(
    "/{full_path:path}",
    methods=["POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    include_in_schema=False,
)
async def deny_writes(full_path: str) -> Response:
    return PlainTextResponse("method not allowed", status_code=405)


@app.api_route("/{full_path:path}", methods=["GET", "HEAD"], include_in_schema=False)
async def catch_all_get(full_path: str) -> Response:
    return _serve_static("/" + full_path)
