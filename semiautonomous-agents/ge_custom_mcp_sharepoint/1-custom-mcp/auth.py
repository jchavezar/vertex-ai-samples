"""Per-request Entra bearer-token middleware.

GE BYO_MCP forwards the end-user's Entra access token on every /mcp
call in the Authorization header. We snapshot it into a contextvar so
the Graph client picks it up without threading it through every call
site. There is NO server-side token cache — every request brings its
own user-bound token.
"""
from __future__ import annotations

import contextvars
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

_user_token: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "sp_mcp_user_token", default=None
)

# Paths that may be hit without a bearer (Cloud Run health probe, etc.).
_PUBLIC_PATHS = {"/healthz", "/"}


def _looks_like_jwt(token: str) -> bool:
    # JWS compact serialization: three base64url segments separated by '.'.
    parts = token.split(".")
    return len(parts) == 3 and all(parts)


class BearerCaptureMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in _PUBLIC_PATHS:
            return await call_next(request)

        auth = request.headers.get("Authorization") or ""
        if not auth.startswith("Bearer "):
            return JSONResponse(
                {"error": "missing Authorization: Bearer <token>"},
                status_code=401,
            )
        token = auth.split(" ", 1)[1].strip()
        if not token or not _looks_like_jwt(token):
            return JSONResponse(
                {"error": "invalid bearer token"},
                status_code=401,
            )
        _user_token.set(token)
        return await call_next(request)


def get_current_user_token() -> Optional[str]:
    return _user_token.get()
