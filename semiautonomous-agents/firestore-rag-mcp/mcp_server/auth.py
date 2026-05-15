"""Google OAuth bearer-token validator for the MCP server.

Gemini Enterprise performs the OAuth dance against Google (you configure the
client_id/secret/auth URL/token URL in the GE Connected Data Store form), then
calls our MCP endpoint with `Authorization: Bearer <google_access_token>`.

This middleware verifies that token via Google's `tokeninfo` endpoint and
optionally enforces audience (client_id) and email-domain restrictions.
"""
from __future__ import annotations

import os

import httpx
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

OAUTH_CLIENT_ID = os.environ.get("OAUTH_CLIENT_ID", "").strip()
ALLOWED_DOMAIN = os.environ.get("ALLOWED_DOMAIN", "").strip()  # e.g. "altostrat.com"
PUBLIC_PATHS = {"/healthz", "/"}


class GoogleBearerAuth(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS" or request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("authorization", "")
        if not auth_header.lower().startswith("bearer "):
            return JSONResponse({"error": "missing_bearer_token"}, status_code=401)
        token = auth_header.split(None, 1)[1].strip()

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(
                    "https://oauth2.googleapis.com/tokeninfo",
                    params={"access_token": token},
                )
        except Exception as e:
            return JSONResponse({"error": "tokeninfo_unreachable", "detail": str(e)}, status_code=503)

        if resp.status_code != 200:
            return JSONResponse({"error": "invalid_token"}, status_code=401)
        info = resp.json()

        if OAUTH_CLIENT_ID and info.get("audience") != OAUTH_CLIENT_ID:
            return JSONResponse({"error": "audience_mismatch"}, status_code=403)
        if ALLOWED_DOMAIN:
            email = info.get("email", "")
            if not email.endswith(f"@{ALLOWED_DOMAIN}"):
                return JSONResponse({"error": "domain_not_allowed"}, status_code=403)

        request.state.user_email = info.get("email")
        return await call_next(request)
