"""M365 Outlook MCP server for Gemini Enterprise.

Every /mcp call carries the end-user's Entra access token in the headers,
captured by the BearerCaptureMiddleware and used directly against Microsoft Graph.
"""
from __future__ import annotations

import json
import logging
import os
import uvicorn
from fastapi import FastAPI, Request
from mcp.server import Server
from mcp.types import Tool, ToolAnnotations

from auth import BearerCaptureMiddleware, get_current_user_token
from outlook_client import OutlookClient

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("outlook-mcp")

app = FastAPI(title="M365 Outlook MCP for Gemini Enterprise")
app.add_middleware(BearerCaptureMiddleware)
mcp_server = Server("outlook-mcp")

READ_ONLY = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=True,
)

MUTATION = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=False,
    openWorldHint=True,
)

# Helpers to resolve dynamic Graph client
def get_client() -> OutlookClient:
    token = get_current_user_token()
    return OutlookClient(token)

async def _dispatch_tool(name: str, arguments: dict) -> dict:
    client = get_client()
    
    if name == "search_emails":
        res = await client.search_emails(
            query=arguments.get("query"),
            sender=arguments.get("sender"),
            hours_back=arguments.get("hours_back", "24h"),
            unread_only=arguments.get("unread_only", False),
            limit=arguments.get("limit", 25)
        )
        return {"emails": res}

    if name == "get_email_full_body":
        res = await client.get_email_full_body(arguments["message_id"])
        return {"email": res}

    if name == "list_meetings":
        res = await client.list_meetings(
            lookback=arguments.get("lookback", "24h"),
            lookahead=arguments.get("lookahead", "48h"),
            limit=arguments.get("limit", 25)
        )
        return {"meetings": res}

    if name == "send_email":
        res = await client.send_email_v2(
            subject=arguments["subject"],
            body=arguments["body"],
            to_recipients=arguments["to_recipients"],
            importance=arguments.get("importance", "normal"),
            attachment_filename=arguments.get("attachment_filename")
        )
        return res

    if name == "reply_email":
        # Reply is handled via Microsoft Graph API reply endpoint
        headers = client._get_headers()
        url = f"{client.base_url}/me/messages/{arguments['message_id']}/reply"
        import httpx
        async with httpx.AsyncClient(timeout=15.0) as http_client:
            resp = await http_client.post(url, headers=headers, json={"comment": arguments["comment"]})
            if resp.status_code in (200, 202):
                return {"success": True, "message": "Reply sent successfully."}
            return {"success": False, "error": f"Graph API returned {resp.status_code}: {resp.text}"}

    if name == "create_meeting":
        res = await client.create_meeting_v2(
            subject=arguments["subject"],
            start_time=arguments["start_time"],
            end_time=arguments["end_time"],
            attendees=arguments.get("attendees")
        )
        return res

    if name == "delete_email":
        res = await client.delete_email(arguments["message_id"])
        return res

    if name == "move_email":
        res = await client.move_email(
            message_id=arguments["message_id"],
            destination_folder_name=arguments["destination_folder_name"]
        )
        return res

    if name == "restore_email":
        res = await client.restore_email(arguments["message_id"])
        return res

    if name == "flag_email":
        res = await client.flag_email(
            message_id=arguments["message_id"],
            flag_status=arguments.get("flag_status", "flagged")
        )
        return res

    if name == "mark_email_read_status":
        res = await client.mark_email_read_status(
            message_id=arguments["message_id"],
            is_read=arguments["is_read"]
        )
        return res

    raise ValueError(f"Unknown tool: {name}")


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_emails",
            description="Search mailbox emails with keyword query expansion and date filtering.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Free-text keyword"},
                    "sender": {"type": "string", "description": "Sender email address"},
                    "hours_back": {"type": "string", "default": "24h", "description": "Lookback window e.g. 24h, 7d"},
                    "unread_only": {"type": "boolean", "default": False, "description": "Filter unread only"},
                    "limit": {"type": "integer", "default": 25}
                }
            },
            annotations=READ_ONLY
        ),
        Tool(
            name="get_email_full_body",
            description="Fetch the complete body/payload for a specific email message ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {"type": "string", "description": "The email message ID"}
                },
                "required": ["message_id"]
            },
            annotations=READ_ONLY
        ),
        Tool(
            name="list_meetings",
            description="List calendar meetings and schedule details within a time window.",
            inputSchema={
                "type": "object",
                "properties": {
                    "lookback": {"type": "string", "default": "24h"},
                    "lookahead": {"type": "string", "default": "48h"},
                    "limit": {"type": "integer", "default": 25}
                }
            },
            annotations=READ_ONLY
        ),
        Tool(
            name="send_email",
            description="Send an outgoing email message, optionally with attachment or priority.",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject": {"type": "string"},
                    "body": {"type": "string"},
                    "to_recipients": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of recipient email addresses"
                    },
                    "importance": {"type": "string", "default": "normal", "description": "high, normal, low"},
                    "attachment_filename": {"type": "string", "description": "Optional name of file to attach"}
                },
                "required": ["subject", "body", "to_recipients"]
            },
            annotations=MUTATION
        ),
        Tool(
            name="reply_email",
            description="Reply to an existing email thread using the message ID and comments.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {"type": "string"},
                    "comment": {"type": "string"}
                },
                "required": ["message_id", "comment"]
            },
            annotations=MUTATION
        ),
        Tool(
            name="create_meeting",
            description="Create/schedule a new calendar meeting.",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject": {"type": "string"},
                    "start_time": {"type": "string", "description": "ISO 8601 UTC format e.g. 2026-07-25T14:00:00Z"},
                    "end_time": {"type": "string", "description": "ISO 8601 UTC format"},
                    "attendees": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of invitee emails"
                    }
                },
                "required": ["subject", "start_time", "end_time"]
            },
            annotations=MUTATION
        ),
        Tool(
            name="delete_email",
            description="Delete a specific email by message ID (moves it to Deleted Items).",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {"type": "string"}
                },
                "required": ["message_id"]
            },
            annotations=MUTATION
        ),
        Tool(
            name="move_email",
            description="Move an email to a specific folder (creates folder if needed).",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {"type": "string"},
                    "destination_folder_name": {"type": "string"}
                },
                "required": ["message_id", "destination_folder_name"]
            },
            annotations=MUTATION
        ),
        Tool(
            name="restore_email",
            description="Restore a deleted email by moving it back to the Inbox.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {"type": "string"}
                },
                "required": ["message_id"]
            },
            annotations=MUTATION
        ),
        Tool(
            name="flag_email",
            description="Set follow-up flag status for an email.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {"type": "string"},
                    "flag_status": {"type": "string", "default": "flagged", "description": "flagged, notFlagged, complete"}
                },
                "required": ["message_id"]
            },
            annotations=MUTATION
        ),
        Tool(
            name="mark_email_read_status",
            description="Mark email as read (true) or unread (false).",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {"type": "string"},
                    "is_read": {"type": "boolean"}
                },
                "required": ["message_id", "is_read"]
            },
            annotations=MUTATION
        )
    ]


@app.api_route("/mcp", methods=["GET", "POST"])
async def handle_mcp_jsonrpc(request: Request):
    if request.method == "GET":
        return {"status": "ok", "service": "outlook-mcp"}

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
                    "serverInfo": {"name": "outlook-mcp", "version": "0.1.0"},
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
