"""Option F — MCP wrapper exposing canonical search/fetch over an ADK LlmAgent
that drives Atlassian's official Rovo MCP.

GE -> /mcp (this Cloud Run service) -> ADK LlmAgent -> mcp.atlassian.com/v1/sse

The five-part silent-search recipe (see memory `ge_custom_mcp_confirmation_fix`)
is required for GE to dispatch tool calls without per-call confirmation popups:
  1. /mcp handler serializes the FULL Tool object (model_dump).
  2. initialize returns protocolVersion "2025-06-18".
  3. Each read tool declares ToolAnnotations(readOnly=True, ...).
  4. Each read tool has an outputSchema.
  5. Canonical search(query) + fetch(id) primitives.

The bearer token GE sends with each /mcp request IS the user's Rovo MCP OAuth
bearer (because the connector's auth_uri/token_uri are pointed at
cf.mcp.atlassian.com). We extract it from the Authorization header and pass it
straight through to MCPToolset for the inner Rovo call.
"""
from __future__ import annotations

import contextvars
import logging
import os
import time
from typing import Any

import uvicorn
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

from mcp.server import Server
from mcp.types import Tool, ToolAnnotations, TextContent

from agent_loop import run_agent_async

# --- Logging ---------------------------------------------------------------
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("option-f.server")

# --- Bearer capture middleware --------------------------------------------
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
        return await call_next(request)


# --- MCP server + tool surface --------------------------------------------
mcp_server = Server("option-f-rovo-wrapper")

READ_ONLY = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=True,
)


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """ONE opaque tool. Option E proved that exposing `search`/`fetch` triggers
    GE's deep-research pattern and causes GE to either skip the wrapper or
    iterate 20+ times. A single Jira-named tool keeps GE in call-once mode."""
    return [
        Tool(
            name="ask_rovo_jira_expert",
            description=(
                "Ask the Rovo-backed Jira expert assistant a question. Call "
                "this tool EXACTLY ONCE per user turn with the user's full "
                "original question verbatim. The tool runs all multi-step "
                "Jira reasoning internally via an ADK agent driving "
                "Atlassian's official Rovo MCP (JQL search, pagination, "
                "comments, worklogs, issue links, multi-project lookups, "
                "refusals, PII redaction, prompt-injection defense) and "
                "returns a complete polished answer in one round-trip. The "
                "returned `answer` is markdown-formatted with [KEY](URL) "
                "issue links and is ready to surface to the user verbatim. "
                "DO NOT call this tool more than once per turn. DO NOT "
                "refine, rewrite, shorten, decompose, or translate the "
                "question — the inner agent's planner needs the exact "
                "original phrasing."
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
            outputSchema={
                "type": "object",
                "properties": {
                    "answer": {"type": "string"},
                },
                "required": ["answer"],
            },
            annotations=READ_ONLY,
        ),
    ]


# --- Tool dispatch ---------------------------------------------------------
@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    bearer = _user_auth_var.get()
    args = arguments or {}

    if name == "ask_rovo_jira_expert":
        question = (args.get("question") or "").strip()
        if not question:
            return [TextContent(type="text", text="Please provide a Jira question.")]
        return await _dispatch(question, bearer, label="ask")

    return [TextContent(type="text", text=f"Error: unknown tool {name!r}")]


async def _dispatch(question: str, bearer: str | None, *, label: str) -> list[TextContent]:
    logger.info(
        "%s START bearer=%s question[:120]=%r",
        label, "yes" if bearer else "no", question[:120],
    )
    t0 = time.perf_counter()
    try:
        answer = await run_agent_async(question, bearer)
    except Exception as exc:  # noqa: BLE001
        logger.exception("run_agent_async crashed: %s", exc)
        return [TextContent(type="text", text=f"Error: agent crashed: {exc}")]
    elapsed = time.perf_counter() - t0
    logger.info("%s DONE %.2fs (%d chars)", label, elapsed, len(answer or ""))
    return [TextContent(type="text", text=answer or "[empty]")]


# --- FastAPI app + /mcp StreamableHTTP endpoint ----------------------------
app = FastAPI(title="Option F — ADK + Rovo MCP wrapper")
app.add_middleware(AuthMiddleware)


@app.get("/")
async def root():
    return {
        "service": "option-f-adk-rovo-wrapper",
        "mcp_endpoint": "/mcp",
        "tools": ["ask_rovo_jira_expert"],
        "model": os.environ.get("MODEL_NAME", "gemini-flash-lite-latest"),
        "upstream": os.environ.get("ROVO_MCP_URL", "https://mcp.atlassian.com/v1/sse"),
    }


@app.get("/healthz")
async def healthz():
    return {"ok": True}


@app.post("/mcp")
async def handle_mcp(request: Request):
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
                        "name": "option-f-rovo-wrapper",
                        "version": "1.0.0",
                    },
                    "capabilities": {"tools": {}},
                },
            }

        if method == "notifications/initialized":
            # Pure notification; no response body in JSON-RPC.
            return {"jsonrpc": "2.0", "id": request_id, "result": {}}

        if method == "tools/list":
            tools_list = await list_tools()
            # CRITICAL: full Tool serialization to preserve annotations +
            # outputSchema. Required for GE silent-search.
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
            answer_text = "".join(c["text"] for c in content_list)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": content_list,
                    "structuredContent": {"answer": answer_text},
                },
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }

    except Exception as exc:  # noqa: BLE001
        logger.exception("MCP JSON-RPC handler error: %s", exc)
        return {
            "jsonrpc": "2.0",
            "id": (body or {}).get("id"),
            "error": {"code": -32603, "message": str(exc)},
        }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
