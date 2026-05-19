"""Option E — ADK-wrapped-in-MCP server.

Cloud Run MCP server that GE consumes as a *custom MCP data store* (so it
shows up in GE's main chat surface — no agent picker needed). Internally,
every tool call delegates to the existing Option A ADK agent running on
Vertex AI Agent Engine via `stream_query`. The ADK agent owns the real tool
loop (Jira MCP, before/after callbacks, 3500-char system prompt) and its
polished answer text becomes the MCP tool result that GE renders.

Architecture:
    GE main chat --> custom_mcp datastore --> THIS Cloud Run /mcp
                                                  |
                                                  | vertexai.agent_engines.stream_query
                                                  v
                                            Vertex AI Agent Engine (Option A)
                                                  |
                                                  | MCP/SSE
                                                  v
                                            Cloud Run jira-mcp-server (Jira tools)

The five-part GE-silent-dispatch recipe is applied here verbatim (see
`option-c-custom-mcp-direct/FINDINGS.md` §3):
  1. /mcp StreamableHTTP handler serializes the FULL Tool object via model_dump
  2. initialize returns protocolVersion 2025-06-18
  3. Every read tool declares ToolAnnotations(readOnlyHint=True, ...)
  4. Every read tool has an outputSchema
  5. Canonical search(query) + fetch(id) primitives exposed
"""
from __future__ import annotations

import asyncio
import contextvars
import json
import logging
import os
import re
import time
from typing import Any

import uvicorn
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

from mcp.server import Server
from mcp.types import Tool, ToolAnnotations, TextContent

import vertexai
from vertexai import agent_engines

# --- 0. Logging ---
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("option-e-mcp-wrapper")

# --- 1. Config ---
GCP_PROJECT = os.environ.get("GCP_PROJECT", "vtxdemos")
GCP_LOCATION = os.environ.get("GCP_LOCATION", "us-central1")
# Option A's deployed Agent Engine. Resource name format:
# projects/<num>/locations/<region>/reasoningEngines/<id>
AGENT_ENGINE_RESOURCE = os.environ.get(
    "AGENT_ENGINE_RESOURCE",
    "projects/254356041555/locations/us-central1/reasoningEngines/1666248848999186432",
)
# Must match `AGENTSPACE_AUTH_ID` baked into the Option A agent
# (option-a-custom-mcp-portal/adk_agent/agent.py:29). The agent's
# `get_access_token()` accepts any state key equal to or starting with this id,
# bare or with the `temp:` prefix. We use `temp:<auth_id>` per the
# Vertex SDK gotchas memo (state with `temp:` prefix syncs through
# `create_session`).
AGENTSPACE_AUTH_ID = os.environ.get("AGENTSPACE_AUTH_ID", "jira-mcp-portal-auth")
# User id sent to the agent. Per-request session, so this can be a constant
# (the OAuth token in state is what actually scopes the data access).
WRAPPER_USER_ID = os.environ.get("WRAPPER_USER_ID", "ge-mcp-wrapper")
# Max time we wait for the AE stream to drain before returning what we have.
AGENT_STREAM_TIMEOUT_S = float(os.environ.get("AGENT_STREAM_TIMEOUT_S", "300"))

# --- 2. Auth middleware (capture Jira OAuth bearer from /mcp request) ---
# Mirrors option-a-custom-mcp-portal/jira_server/server.py:30-47.
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


# --- 3. Vertex AI / Agent Engine bootstrap ---
vertexai.init(project=GCP_PROJECT, location=GCP_LOCATION)

# The remote AdkApp handle. Cached at module load. agent_engines.get() is
# a metadata fetch; actual stream_query negotiates per-call.
_agent: Any | None = None


def _get_agent():
    global _agent
    if _agent is None:
        logger.info("Resolving Agent Engine: %s", AGENT_ENGINE_RESOURCE)
        _agent = agent_engines.get(AGENT_ENGINE_RESOURCE)
        logger.info("Agent Engine resolved: %s", getattr(_agent, "resource_name", "?"))
    return _agent


# --- 4. MCP server & tool surface ---
mcp_server = Server("jira-adk-wrapper")

READ_ONLY = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=True,
)


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """Two tools — the canonical search/fetch primitives. GE's auto-MCP-agent
    treats this connector as retrieval-shaped and dispatches both silently
    (no per-call confirmation popup) when the 5-part recipe is intact."""
    return [
        Tool(
            name="search",
            description=(
                "Search Jira via the deep-orchestration ADK agent. Use for any "
                "Jira-related question — counts, lookups, JQL filters, "
                "comments/worklogs/links lookups, multi-step analysis. The ADK "
                "agent picks tools, paginates, formats markdown tables with "
                "clickable issue keys, and synthesizes a complete answer. "
                "Returns a SearchResultPage whose single result wraps the "
                "agent's full polished answer."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "The user's full question, verbatim. Do not "
                            "rewrite or shorten it — the ADK agent's planner "
                            "needs the original phrasing."
                        ),
                    }
                },
                "required": ["query"],
            },
            outputSchema={
                "type": "object",
                "properties": {
                    "results": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "title": {"type": "string"},
                                "text": {"type": "string"},
                            },
                            "required": ["id", "title", "text"],
                        },
                    }
                },
                "required": ["results"],
            },
            annotations=READ_ONLY,
        ),
        Tool(
            name="fetch",
            description=(
                "Fetch detailed info for a specific Jira issue via the ADK "
                "agent. The agent will call the per-issue tools "
                "(getIssueComments / getIssueWorklogs / getIssueLinks) as "
                "needed to assemble a complete profile. Returns a "
                "FetchResult containing the agent's answer text."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Jira issue key, e.g. SMP-912.",
                    }
                },
                "required": ["id"],
            },
            outputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "title": {"type": "string"},
                    "text": {"type": "string"},
                    "url": {"type": "string"},
                },
                "required": ["id", "title", "text"],
            },
            annotations=READ_ONLY,
        ),
    ]


_KEY_RE = re.compile(r"\b([A-Z][A-Z0-9_]+-\d+)\b")


async def _run_adk_agent(message: str, jira_bearer: str | None) -> str:
    """Open a fresh AE session with the Jira OAuth token in state, stream the
    query, accumulate non-thought text parts, return the final answer string.

    A fresh session per call is intentional: GE may multiplex requests from
    different users and we don't want one user's Jira token in another user's
    session state. Sessions are cheap (AE-side in-memory)."""
    agent = _get_agent()

    state: dict[str, str] = {}
    if jira_bearer:
        # The Option A agent's `get_access_token` scans state for keys equal
        # to or prefixed with AGENTSPACE_AUTH_ID (with or without `temp:`).
        # Use `temp:<id>` per Vertex SDK memo on state sync.
        state[f"temp:{AGENTSPACE_AUTH_ID}"] = jira_bearer
        logger.debug(
            "Session state seeded with key temp:%s (token %s...)",
            AGENTSPACE_AUTH_ID, jira_bearer[:8],
        )
    else:
        logger.warning(
            "No Jira bearer captured — relying on the AE agent's "
            "ATLASSIAN_EMAIL/ATLASSIAN_API_TOKEN env-var fallback."
        )

    # `create_session` accepts `state` and the SDK syncs it to the deployed
    # runtime (confirmed in `~/.claude/.../memory/agent_engine_gotchas.md`).
    loop = asyncio.get_running_loop()

    def _create_session_sync():
        return agent.create_session(user_id=WRAPPER_USER_ID, state=state)

    session = await loop.run_in_executor(None, _create_session_sync)
    session_id = session["id"] if isinstance(session, dict) else getattr(session, "id", None)
    if not session_id:
        raise RuntimeError(f"AE create_session returned no id: {session!r}")
    logger.debug("AE session id: %s", session_id)

    # `stream_query` is sync-generator on the AdkApp wrapper. Pump it in a
    # thread and accumulate non-thought text parts. AE streams ADK events
    # of shape {"content": {"role": "model"|"user", "parts": [{...}]}, ...}.
    answer_parts: list[str] = []

    def _drain_stream():
        for event in agent.stream_query(
            user_id=WRAPPER_USER_ID, session_id=session_id, message=message
        ):
            content = (event or {}).get("content") or {}
            for part in content.get("parts", []) or []:
                if part.get("thought"):
                    continue
                text = part.get("text")
                if text and content.get("role") in (None, "model"):
                    answer_parts.append(text)
        return "".join(answer_parts)

    try:
        answer = await asyncio.wait_for(
            loop.run_in_executor(None, _drain_stream),
            timeout=AGENT_STREAM_TIMEOUT_S,
        )
    except asyncio.TimeoutError:
        logger.error("AE stream_query timed out after %.0fs", AGENT_STREAM_TIMEOUT_S)
        partial = "".join(answer_parts).strip()
        if partial:
            return partial + "\n\n[NOTE: ADK agent timed out; partial answer above.]"
        raise

    return answer


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    jira_bearer = _user_auth_var.get()
    try:
        if name == "search":
            query = (arguments or {}).get("query") or ""
            if not query.strip():
                return [TextContent(type="text", text=json.dumps({"results": []}))]
            t0 = time.perf_counter()
            answer = await _run_adk_agent(query, jira_bearer)
            elapsed = time.perf_counter() - t0
            logger.info("search OK %.1fs (%d chars)", elapsed, len(answer))

            # Wrap the agent's polished answer in a SearchResultPage. The text
            # field IS what GE renders to the user.
            cited_keys = sorted(set(_KEY_RE.findall(answer)))
            result_id = cited_keys[0] if cited_keys else "agent-answer"
            title = (answer.strip().splitlines() or ["Jira answer"])[0][:200]
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "results": [
                                {"id": result_id, "title": title, "text": answer}
                            ]
                        }
                    ),
                )
            ]

        elif name == "fetch":
            issue_id = (arguments or {}).get("id") or ""
            if not issue_id.strip():
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {"id": "", "title": "", "text": "Missing issue id."}
                        ),
                    )
                ]
            prompt = (
                f"Give me complete details for Jira issue {issue_id}: title, "
                f"status, priority, assignee, reporter, created, updated, "
                f"description, and any comments, worklogs, or links. "
                f"Format with a markdown table where possible."
            )
            t0 = time.perf_counter()
            answer = await _run_adk_agent(prompt, jira_bearer)
            elapsed = time.perf_counter() - t0
            logger.info("fetch OK %.1fs (%d chars) for %s", elapsed, len(answer), issue_id)

            title = (answer.strip().splitlines() or [issue_id])[0][:200]
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "id": issue_id,
                            "title": title,
                            "text": answer,
                            # The agent emits canonical browse URLs inside `answer`;
                            # we don't have a site host independent of that here.
                            "url": "",
                        }
                    ),
                )
            ]

        return [
            TextContent(
                type="text", text=f"Error: unknown tool {name!r}"
            )
        ]

    except Exception as exc:
        logger.exception("tool %s failed: %s", name, exc)
        return [TextContent(type="text", text=f"Error: {exc}")]


# --- 5. FastAPI + StreamableHTTP /mcp endpoint ---
app = FastAPI(title="Option E — ADK-wrapped-in-MCP")
app.add_middleware(AuthMiddleware)


@app.get("/")
async def root():
    return {
        "service": "option-e-adk-wrapped-in-mcp",
        "agent_engine": AGENT_ENGINE_RESOURCE,
        "mcp_endpoint": "/mcp",
        "auth_id": AGENTSPACE_AUTH_ID,
    }


@app.get("/healthz")
async def healthz():
    return {"ok": True}


@app.post("/mcp")
async def handle_mcp(request: Request):
    """JSON-RPC over StreamableHTTP. Same handler shape as Option A's
    `/mcp` endpoint (option-a-custom-mcp-portal/jira_server/server.py:613-700).

    The five-part recipe is critical:
      - initialize returns protocolVersion 2025-06-18
      - tools/list uses `t.model_dump(by_alias=True, exclude_none=True)` so
        annotations + outputSchema flow through (GE keys silent dispatch on
        these fields)
      - tools/call returns the agent's answer wrapped as TextContent."""
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
                        "name": "jira-adk-wrapper",
                        "version": "1.0.0",
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
                {k: (v[:80] if isinstance(v, str) else v) for k, v in tool_args.items()},
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
