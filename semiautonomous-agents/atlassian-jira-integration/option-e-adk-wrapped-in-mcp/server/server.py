"""Option E (rewrite) — MCP wrapper exposing ONE `ask_jira_expert` tool.

The old design exposed `search(query)` + `fetch(id)` which triggered GE's
deep-research pattern and caused it to call the wrapper 22+ times per
question, hitting the 300s timeout. The new design exposes a single
opaque tool — GE sees one read-only tool, calls it ONCE per question,
and we do all the multi-step Jira reasoning inside `agent_loop.py`
using google.genai function-calling against gemini-3.5-flash.

The result text the model produces is returned as the MCP tool result
verbatim, so GE just renders it.

Architecture:
    GE main chat
        -> custom MCP datastore
        -> THIS Cloud Run /mcp (ask_jira_expert)
                |
                v   in-process google.genai function-calling loop
            gemini-3.5-flash + 7 Jira function declarations
                |
                v   tools/call HTTP -> jira-mcp-server
            Atlassian Jira REST
"""
from __future__ import annotations

import asyncio
import contextvars
import hashlib
import json
import logging
import os
import time
from collections import OrderedDict
from typing import Any

import uvicorn
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

from mcp.server import Server
from mcp.types import Tool, ToolAnnotations, TextContent

from agent_loop import run_agent_loop

# --- Logging ----------------------------------------------------------------
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("option-e-mcp-wrapper")

# --- Bearer capture middleware ---------------------------------------------
# Mirrors option-a-custom-mcp-portal/jira_server/server.py:30-47. GE sends
# the per-user Jira OAuth token in the `Authorization` header on every /mcp
# request; we stash it in a contextvar so the agent loop can pass it into
# the inner jira-mcp-server HTTP calls.
_user_auth_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "user_auth", default=None
)


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization") or ""
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()
            _user_auth_var.set(token)
            logger.debug("Captured bearer (%s...)", token[:8])
        else:
            _user_auth_var.set(None)
            logger.debug("No bearer in request headers")
        return await call_next(request)


# --- MCP server & tool surface ---------------------------------------------
mcp_server = Server("jira-ask-expert-wrapper")

READ_ONLY = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=True,
)


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """Exactly ONE tool. We deliberately do NOT expose `search` or `fetch`
    — those names trigger GE's deep-research pattern matching and cause
    it to iterate 20+ times. A single opaque `ask_jira_expert` keeps GE
    in the "call once, get answer" mode."""
    return [
        Tool(
            name="ask_jira_expert",
            description=(
                "Ask the Jira expert assistant a question. Call this tool "
                "EXACTLY ONCE per user turn with the user's full original "
                "question verbatim. The tool runs all multi-step Jira "
                "reasoning internally (JQL search, pagination, comments, "
                "worklogs, issue links, multi-project lookups, refusals, "
                "PII redaction, prompt-injection defense) and returns a "
                "complete polished answer in one round-trip. The returned "
                "`answer` is markdown-formatted with [KEY](URL) issue links "
                "and is ready to surface to the user verbatim. DO NOT call "
                "this tool more than once per turn. DO NOT refine, rewrite, "
                "shorten, decompose, or translate the question — the inner "
                "agent's planner needs the exact original phrasing."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": (
                            "The user's full ORIGINAL question, verbatim. "
                            "Do not rewrite, shorten, decompose, or translate. "
                            "The inner agent needs the exact original phrasing."
                        ),
                    }
                },
                "required": ["question"],
            },
            annotations=READ_ONLY,
        ),
    ]


# --- Simple TTL+LRU cache (in-process) -------------------------------------
CACHE_ENABLED = os.environ.get("CACHE_ENABLED", "1") != "0"
CACHE_TTL_S = float(os.environ.get("CACHE_TTL_S", "300"))
CACHE_MAX = int(os.environ.get("CACHE_MAX", "100"))
_cache: "OrderedDict[str, tuple[float, str]]" = OrderedDict()


def _cache_key(question: str) -> str:
    norm = (question or "").lower().strip()
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()


def _cache_get(question: str) -> str | None:
    if not CACHE_ENABLED:
        return None
    k = _cache_key(question)
    if k not in _cache:
        return None
    ts, val = _cache[k]
    if (time.time() - ts) > CACHE_TTL_S:
        _cache.pop(k, None)
        return None
    # Refresh LRU order.
    _cache.move_to_end(k)
    return val


def _cache_put(question: str, answer: str) -> None:
    if not CACHE_ENABLED or not answer:
        return
    k = _cache_key(question)
    _cache[k] = (time.time(), answer)
    _cache.move_to_end(k)
    while len(_cache) > CACHE_MAX:
        _cache.popitem(last=False)


# --- Tool dispatch ----------------------------------------------------------
@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name != "ask_jira_expert":
        return [
            TextContent(
                type="text",
                text=f"Error: unknown tool {name!r}",
            )
        ]

    question = ((arguments or {}).get("question") or "").strip()
    if not question:
        return [
            TextContent(
                type="text",
                text="Please provide a question.",
            )
        ]

    cached = _cache_get(question)
    if cached is not None:
        logger.info("CACHE HIT for question[:60]=%r", question[:60])
        return [
            TextContent(type="text", text=cached)
        ]

    jira_bearer = _user_auth_var.get()
    logger.info(
        "ask_jira_expert START bearer=%s question[:120]=%r",
        "yes" if jira_bearer else "no",
        question[:120],
    )

    t0 = time.perf_counter()
    loop = asyncio.get_running_loop()
    try:
        answer = await loop.run_in_executor(
            None, run_agent_loop, question, jira_bearer
        )
    except Exception as exc:
        logger.exception("agent_loop raised: %s", exc)
        return [
            TextContent(
                type="text",
                text=f"Error: agent loop crashed: {exc}",
            )
        ]
    elapsed = time.perf_counter() - t0
    logger.info("ask_jira_expert DONE %.1fs (%d chars)", elapsed, len(answer or ""))

    _cache_put(question, answer)
    return [
        TextContent(type="text", text=answer)
    ]


# --- FastAPI app + /mcp StreamableHTTP endpoint -----------------------------
app = FastAPI(title="Option E — ask_jira_expert MCP wrapper")
app.add_middleware(AuthMiddleware)


@app.get("/")
async def root():
    return {
        "service": "option-e-ask-jira-expert",
        "mcp_endpoint": "/mcp",
        "tool": "ask_jira_expert",
        "model": os.environ.get("MODEL_NAME", "gemini-3.5-flash"),
        "cache": {
            "enabled": CACHE_ENABLED,
            "ttl_s": CACHE_TTL_S,
            "max": CACHE_MAX,
            "size": len(_cache),
        },
    }


@app.get("/healthz")
async def healthz():
    return {"ok": True}


@app.post("/mcp")
async def handle_mcp(request: Request):
    """JSON-RPC over StreamableHTTP. Same shape as before:
      - initialize: protocolVersion 2025-06-18
      - tools/list: full Tool.model_dump (preserves annotations + outputSchema)
      - tools/call: invokes call_tool(), returns TextContent as JSON-RPC content
    """
    body: dict[str, Any] | None = None
    try:
        body = await request.json()
        method = body.get("method")
        params = body.get("params", {}) or {}
        request_id = body.get("id")
        logger.info("JSON-RPC method=%s id=%s", method, request_id)

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2025-06-18",
                    "serverInfo": {
                        "name": "jira-ask-expert-wrapper",
                        "version": "2.0.0",
                    },
                    "capabilities": {"tools": {}},
                },
            }

        if method == "tools/list":
            tools_list = await list_tools()
            tools_dict = [
                t.model_dump(by_alias=True, exclude_none=True) for t in tools_list
            ]
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"tools": tools_dict},
            }

        if method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {}) or {}
            logger.info(
                "tools/call name=%s args=%s",
                tool_name,
                {k: (v[:120] if isinstance(v, str) else v) for k, v in tool_args.items()},
            )
            result = await call_tool(tool_name, tool_args)
            content_list = [
                {"type": "text", "text": item.text}
                for item in result
                if hasattr(item, "text")
            ]
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"content": content_list},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }

    except Exception as exc:
        logger.exception("MCP JSON-RPC handler error: %s", exc)
        return {
            "jsonrpc": "2.0",
            "id": (body or {}).get("id"),
            "error": {"code": -32603, "message": str(exc)},
        }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
