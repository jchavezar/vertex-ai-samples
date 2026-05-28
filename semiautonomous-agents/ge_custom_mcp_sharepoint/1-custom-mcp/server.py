"""SharePoint MCP server for Gemini Enterprise (BYO_MCP).

Per-request bearer pass-through: every /mcp call carries the end-user's
Entra access token in the Authorization header, captured by the
BearerCaptureMiddleware and used directly against Microsoft Graph.

Implements the silent-search recipe from memory
``ge_custom_mcp_confirmation_fix``:
  1. /mcp handler returns FULL Tool.model_dump(by_alias=True, exclude_none=True).
  2. initialize returns protocolVersion "2025-06-18".
  3. Every read tool carries ToolAnnotations(readOnlyHint=True, ...).
  4. Every read tool has an outputSchema.
  5. Canonical search(query) + fetch(id) primitives are present.
"""
from __future__ import annotations

import json
import logging
import os

import uvicorn
from fastapi import FastAPI, Request
from mcp.server import Server
from mcp.types import Tool, ToolAnnotations

from auth import BearerCaptureMiddleware
from tools.fetch import fetch as fetch_tool
from tools.list_files import list_files as list_files_tool
from tools.list_libraries import list_libraries as list_libraries_tool
from tools.list_sites import list_sites as list_sites_tool
from tools.read_file import read_file as read_file_tool
from tools.search import search as search_tool

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("sharepoint-mcp")

app = FastAPI(title="SharePoint MCP for Gemini Enterprise")
app.add_middleware(BearerCaptureMiddleware)
mcp_server = Server("sharepoint-mcp")

READ_ONLY = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=True,
)

_SEARCH_RESULT_SCHEMA = {
    "type": "object",
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "title": {"type": "string"},
                    "url": {"type": "string"},
                    "snippet": {"type": "string"},
                },
                "required": ["id", "title"],
            },
        }
    },
    "required": ["results"],
}

_FETCH_RESULT_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "title": {"type": "string"},
        "url": {"type": "string"},
        "text": {"type": "string"},
    },
    "required": ["id", "title", "text"],
}


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search",
            description=(
                "Search SharePoint content by free-text query. Returns a "
                "SearchResultPage of {id, title, url, snippet}. The id is "
                "'<driveId>:<itemId>' and can be passed back to fetch()."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Free-text query."},
                    "top": {"type": "integer", "default": 20},
                },
                "required": ["query"],
            },
            outputSchema=_SEARCH_RESULT_SCHEMA,
            annotations=READ_ONLY,
        ),
        Tool(
            name="fetch",
            description=(
                "Fetch a SharePoint driveItem by id and return extracted text. "
                "id is '<driveId>:<itemId>' as returned by search()."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "'<driveId>:<itemId>'."},
                },
                "required": ["id"],
            },
            outputSchema=_FETCH_RESULT_SCHEMA,
            annotations=READ_ONLY,
        ),
        Tool(
            name="list_sites",
            description="List SharePoint sites visible to the user (optional name filter).",
            inputSchema={
                "type": "object",
                "properties": {"search": {"type": "string"}},
            },
            outputSchema={
                "type": "object",
                "properties": {
                    "sites": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "name": {"type": "string"},
                                "url": {"type": "string"},
                            },
                        },
                    }
                },
                "required": ["sites"],
            },
            annotations=READ_ONLY,
        ),
        Tool(
            name="list_libraries",
            description="List document libraries (drives) for a SharePoint site.",
            inputSchema={
                "type": "object",
                "properties": {"site_id": {"type": "string"}},
                "required": ["site_id"],
            },
            outputSchema={
                "type": "object",
                "properties": {
                    "libraries": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "name": {"type": "string"},
                                "url": {"type": "string"},
                            },
                        },
                    }
                },
                "required": ["libraries"],
            },
            annotations=READ_ONLY,
        ),
        Tool(
            name="list_files",
            description=(
                "List items in a library (or sub-folder). folder is a "
                "driveItem id; omit for root."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "library_id": {"type": "string"},
                    "folder": {"type": "string"},
                    "limit": {"type": "integer", "default": 50},
                },
                "required": ["library_id"],
            },
            outputSchema={
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "name": {"type": "string"},
                                "kind": {"type": "string"},
                                "size": {"type": "integer"},
                                "url": {"type": "string"},
                                "modified": {"type": "string"},
                            },
                        },
                    }
                },
                "required": ["items"],
            },
            annotations=READ_ONLY,
        ),
        Tool(
            name="read_file",
            description=(
                "Download a SharePoint file (<=5 MB) and return extracted text "
                "(PDF/docx/text). file_id is '<driveId>:<itemId>'."
            ),
            inputSchema={
                "type": "object",
                "properties": {"file_id": {"type": "string"}},
                "required": ["file_id"],
            },
            outputSchema=_FETCH_RESULT_SCHEMA,
            annotations=READ_ONLY,
        ),
    ]


async def _dispatch_tool(name: str, arguments: dict) -> dict:
    if name == "search":
        return await search_tool(
            arguments.get("query", ""), top=arguments.get("top", 20)
        )
    if name == "fetch":
        return await fetch_tool(arguments.get("id", ""))
    if name == "list_sites":
        return await list_sites_tool(arguments.get("search", ""))
    if name == "list_libraries":
        return await list_libraries_tool(arguments["site_id"])
    if name == "list_files":
        return await list_files_tool(
            arguments["library_id"],
            folder=arguments.get("folder"),
            limit=arguments.get("limit", 50),
        )
    if name == "read_file":
        return await read_file_tool(arguments["file_id"])
    raise ValueError(f"unknown tool: {name}")


@app.post("/mcp")
async def handle_mcp_jsonrpc(request: Request):
    body: dict | None = None
    try:
        body = await request.json()
        method = body.get("method")
        params = body.get("params", {}) or {}
        request_id = body.get("id")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2025-06-18",
                    "serverInfo": {"name": "sharepoint-mcp", "version": "0.1.0"},
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
            try:
                structured = await _dispatch_tool(tool_name, tool_args)
                text_fallback = json.dumps(structured)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": text_fallback}],
                        "structuredContent": structured,
                    },
                }
            except Exception as tool_err:
                logger.exception("tool %s failed", tool_name)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps({"error": str(tool_err)})}
                        ],
                        "isError": True,
                    },
                }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"method not found: {method}"},
        }
    except Exception as e:
        logger.exception("/mcp error")
        return {
            "jsonrpc": "2.0",
            "id": (body or {}).get("id"),
            "error": {"code": -32603, "message": str(e)},
        }


@app.get("/healthz")
async def healthz():
    return {"ok": True}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
