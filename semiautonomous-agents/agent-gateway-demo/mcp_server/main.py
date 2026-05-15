"""MCP server (streamable-HTTP transport) for the Agent Gateway demo.

Uses the official `mcp` Python SDK's FastMCP to handle the JSON-RPC
protocol correctly. McpToolset(StreamableHTTPConnectionParams(url=…/mcp))
posts initialize / tools/list / tools/call messages here.

Two modes:
  STUB  (default, DEMO_REAL_MCP=0): return mock results + echo the
        injected user-token claims so we can see Door-1 + Door-2 wiring.
  REAL  (DEMO_REAL_MCP=1): forward the user token to Microsoft Graph
        /me/drive/root/search(q='…').

Headers Agent Gateway injects when fully wired in front of this server:
  Authorization: Bearer <user_token>     ← decrypted by Auth Manager
  X-Agent-Spiffe-Id: spiffe://...        ← from the agent's mTLS cert
  X-Agent-Resource: projects/.../reasoningEngines/<id>
"""
from __future__ import annotations

import base64
import json
import logging
import os
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP, Context
from mcp.server.transport_security import TransportSecuritySettings

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("mcp_server")

DEMO_REAL_MCP = os.environ.get("DEMO_REAL_MCP", "0") == "1"
GRAPH_API_BASE = os.environ.get("GRAPH_API_BASE", "https://graph.microsoft.com/v1.0")


# ──────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────

def _decode_jwt_unsafe(token: str) -> dict[str, Any]:
    """Decode a JWT WITHOUT verifying — for echoing claims in stub mode only."""
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        return json.loads(base64.urlsafe_b64decode(payload).decode())
    except Exception:  # noqa: BLE001
        return {}


def _bearer_from_headers(headers: dict[str, str]) -> str | None:
    h = headers.get("authorization") or headers.get("Authorization") or ""
    return h[7:] if h.lower().startswith("bearer ") else None


def _agent_identity_from_headers(headers: dict[str, str]) -> dict[str, str | None]:
    return {
        "spiffe_id": headers.get("x-agent-spiffe-id") or headers.get("X-Agent-Spiffe-Id"),
        "agent_resource": headers.get("x-agent-resource") or headers.get("X-Agent-Resource"),
    }


# ──────────────────────────────────────────────────────────────────────────
# FastMCP server + tool
# ──────────────────────────────────────────────────────────────────────────

# Disable the FastMCP DNS-rebinding/host check — Cloud Run sits behind GFE
# which forwards arbitrary Host headers, and (in production) Agent Gateway
# does its own mTLS-based ingress auth. Without this, the FastMCP server
# returns 421 "Invalid Host header" for every request.
mcp = FastMCP(
    "agent-gateway-demo-mcp",
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
)


@mcp.tool()
async def search_documents(query: str, top: int = 5, ctx: Context = None) -> dict:
    """Search documents the signed-in user has access to.

    Use this for queries about files, decks, reports, policies, or any
    SharePoint/OneDrive content. The user's identity is provided via the
    request's Authorization header (injected by Agent Gateway in production).
    """
    headers: dict[str, str] = {}
    try:
        # The streamable-HTTP transport exposes the underlying ASGI request
        # via the request context. Different mcp SDK versions surface this
        # differently — try a few.
        rc = ctx.request_context if ctx else None
        req = getattr(rc, "request", None) or getattr(rc, "raw_request", None)
        if req is not None:
            for k, v in req.headers.items():
                headers[k.lower()] = v
    except Exception:  # noqa: BLE001
        pass

    user_token = _bearer_from_headers(headers)
    agent = _agent_identity_from_headers(headers)

    if DEMO_REAL_MCP and not user_token:
        return {
            "status": "error",
            "code": 401,
            "message": "Missing user token (Authorization: Bearer …) — Auth Manager did not inject it.",
        }

    if DEMO_REAL_MCP:
        results = await _graph_search(user_token or "", query, top)
        mode = "real"
    else:
        results = _stub_results(query, top)
        mode = "stub"

    return {
        "mode": mode,
        "query": query,
        "agent_identity": agent,
        "user_token_present": bool(user_token),
        "user_token_claims": _decode_jwt_unsafe(user_token) if user_token else {},
        "results": results,
    }


# ──────────────────────────────────────────────────────────────────────────
# STUB / REAL implementations
# ──────────────────────────────────────────────────────────────────────────

def _stub_results(query: str, top: int) -> list[dict[str, str]]:
    base = [
        {"name": f"{query.title()} — overview.docx", "url": "https://example.com/1"},
        {"name": f"{query.title()} 2026 deck.pptx", "url": "https://example.com/2"},
        {"name": f"Notes on {query}.md", "url": "https://example.com/3"},
        {"name": f"FAQ — {query}.pdf", "url": "https://example.com/4"},
        {"name": f"Slack export — {query}.txt", "url": "https://example.com/5"},
    ]
    return base[:top]


async def _graph_search(user_token: str, query: str, top: int) -> list[dict[str, str]]:
    """Search across EVERYTHING the user has access to in M365 — OneDrive,
    SharePoint sites, Teams files. Uses Graph Search API (`POST /search/query`)
    which is what real enterprise search apps use.

    `/me/drive/root/search` (the previous impl) only sees the signed-in user's
    *personal* OneDrive, missing SharePoint-site documents the user has read
    access to via group membership.
    """
    url = f"{GRAPH_API_BASE}/search/query"
    body = {
        "requests": [
            {
                "entityTypes": ["driveItem", "listItem"],
                "query": {"queryString": query},
                "from": 0,
                "size": top,
            }
        ]
    }
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {user_token}",
                    "Content-Type": "application/json",
                },
                json=body,
            )
    except httpx.HTTPError as exc:
        log.exception("Graph call failed")
        return [{"name": f"(graph error: {exc})", "url": ""}]

    if resp.status_code == 401:
        return [{"name": "(graph 401: token rejected)", "url": ""}]
    if resp.status_code >= 400:
        return [{"name": f"(graph {resp.status_code}: {resp.text[:200]})", "url": ""}]

    payload = resp.json()
    hits: list[dict[str, str]] = []
    for container in payload.get("value", []) or []:
        for hits_container in container.get("hitsContainers", []) or []:
            for hit in hits_container.get("hits", []) or []:
                res = hit.get("resource") or {}
                # driveItem / listItem both expose name + webUrl + lastModified
                hits.append({
                    "name": res.get("name") or hit.get("summary") or "(unnamed)",
                    "url": res.get("webUrl", ""),
                    "lastModified": res.get("lastModifiedDateTime", ""),
                    "summary": hit.get("summary", "")[:200],
                })
                if len(hits) >= top:
                    return hits
    return hits


# ──────────────────────────────────────────────────────────────────────────
# ASGI entrypoint — expose FastMCP's streamable-HTTP app directly.
# Wrapping it in a parent Starlette via Mount() drops FastMCP's lifespan
# context, which the session_manager requires (RuntimeError: Task group
# is not initialized). Cloud Run uses a TCP probe for health, so we don't
# need a /healthz route.
# ──────────────────────────────────────────────────────────────────────────
def _mcp_app():
    for fn_name in ("streamable_http_app", "sse_app"):
        fn = getattr(mcp, fn_name, None)
        if callable(fn):
            log.info("MCP transport: %s", fn_name)
            return fn()
    raise RuntimeError("FastMCP has no streamable_http_app / sse_app")


app = _mcp_app()
