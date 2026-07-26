"""Per-request Entra bearer-token middleware.

Every M365 Outlook call forwards the end-user's Entra access token in the 
Authorization header (or X-User-Token). We snapshot it into a contextvar so
the Graph client picks it up without threading it through every call site.
There is NO server-side token cache — every request brings its own user-bound token.
"""
from __future__ import annotations

import contextvars
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

_user_token: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "outlook_mcp_user_token", default=None
)

# Public paths that do not require authentication
_PUBLIC_PATHS = {"/healthz", "/"}


def _is_microsoft_jwt(token: str) -> bool:
    import base64, json
    parts = token.split(".")
    if len(parts) != 3:
        return False
    try:
        payload_b64 = parts[1] + '=' * (4 - (len(parts[1]) % 4))
        payload = json.loads(base64.urlsafe_b64decode(payload_b64).decode('utf-8'))
        iss = str(payload.get("iss", "")).lower()
        aud = str(payload.get("aud", "")).lower()
        return "microsoft" in iss or "windows.net" in iss or "graph.microsoft.com" in aud or "00000003-0000-0000-c000-000000000000" in aud
    except Exception:
        return False

class BearerCaptureMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in _PUBLIC_PATHS:
            return await call_next(request)

        token = None
        # 1. Check X-User-Token header
        x_user_token = request.headers.get("X-User-Token") or request.headers.get("X-Entra-Id-Token")
        if x_user_token and _is_microsoft_jwt(x_user_token):
            token = x_user_token

        # 2. Check Authorization header
        if not token:
            auth = request.headers.get("Authorization") or ""
            if auth.startswith("Bearer "):
                candidate = auth.split(" ", 1)[1].strip()
                if _is_microsoft_jwt(candidate):
                    token = candidate

        _user_token.set(token)
        return await call_next(request)



def get_current_user_token() -> Optional[str]:
    return _user_token.get()
