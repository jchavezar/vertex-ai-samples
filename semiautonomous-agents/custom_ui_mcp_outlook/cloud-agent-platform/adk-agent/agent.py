import logging
import os
import re
import httpx
import base64
import json
from typing import List, Optional
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("outlook-adk-agent")

# MCP URL (Cloud Run service URL + /mcp)
MCP_URL = os.environ.get("OUTLOOK_MCP_URL", "https://ms365-mcp-server-254356041555.us-central1.run.app/mcp")

def decode_jwt_payload(token: str) -> dict:
    """Safely decodes JWT payload without signature verification."""
    try:
        parts = token.split('.')
        if len(parts) < 2:
            return {}
        payload_b64 = parts[1]
        # Add padding if necessary
        padding = '=' * (4 - (len(payload_b64) % 4))
        payload_json = base64.urlsafe_b64decode(payload_b64 + padding).decode('utf-8')
        return json.loads(payload_json)
    except Exception as e:
        logger.warning(f"[Agent] Failed to decode JWT payload: {e}")
        return {}

def mcp_header_provider(ctx: CallbackContext) -> dict[str, str]:
    headers = {}
    
    # Pillar B: Generate OIDC token for service-to-service auth (Cloud Run IAM)
    try:
        import google.auth.transport.requests
        from google.oauth2 import id_token
        request = google.auth.transport.requests.Request()
        # Use the base URL (without path) for audience
        audience = MCP_URL.split("/mcp")[0]
        cloud_run_token = id_token.fetch_id_token(request, audience)
        headers["Authorization"] = f"Bearer {cloud_run_token}"
        logger.info("[Agent] Added Service Account OIDC token to Authorization header")
    except Exception as e:
        logger.warning(f"[Agent] Failed to get OIDC token: {e}")

    # Extract user JWT from state or session state and put in X-User-Token
    user_token = None
    state_dict = {}
    if hasattr(ctx, "state") and ctx.state:
        try:
            if hasattr(ctx.state, "to_dict"):
                state_dict.update(ctx.state.to_dict())
            elif isinstance(ctx.state, dict):
                state_dict.update(ctx.state)
        except Exception as e:
            logger.warning(f"[Agent] Failed to read ctx.state: {e}")

    if hasattr(ctx, "session") and hasattr(ctx.session, "state"):
        try:
            if hasattr(ctx.session.state, "to_dict"):
                state_dict.update(ctx.session.state.to_dict())
            elif isinstance(ctx.session.state, dict):
                state_dict.update(ctx.session.state)
        except Exception as e:
            logger.warning(f"[Agent] Failed to read ctx.session.state: {e}")

        
    if state_dict:
        logger.info(f"[Agent] Found {len(state_dict)} keys in parsed states: {list(state_dict.keys())}")
        for key, val in state_dict.items():
            if isinstance(val, str) and len(val) > 20:
                if "token" in key.lower() or "entra" in key.lower() or "jwt" in key.lower() or val.startswith("eyJ"):
                    if val.startswith("eyJ"):
                        payload = decode_jwt_payload(val)
                        iss = str(payload.get("iss", "")).lower()
                        if "google" in iss or "accounts.google.com" in iss:
                            continue
                    user_token = val
                    logger.info(f"[Agent] Selected user token from state key='{key}' (length={len(val)})")
                    break
        
        if user_token:
            headers["X-User-Token"] = user_token
            logger.info(f"[Agent] Added X-User-Token (length: {len(user_token)})")
        else:
            logger.warning("[Agent] No user JWT/token found in state")


    return headers

async def _call_mcp(ctx: CallbackContext, method: str, arguments: dict) -> dict:
    headers = mcp_header_provider(ctx)
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": method,
            "arguments": arguments
        }
    }
    logger.info(f"[Agent] Calling MCP tool '{method}' at {MCP_URL}")
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(MCP_URL, headers=headers, json=payload, timeout=60)
            if resp.status_code == 200:
                result = resp.json().get("result", {})
                content = result.get("structuredContent") or result.get("content")
                if isinstance(content, (dict, list)):
                    return json.dumps(content)
                return str(content)
            else:
                logger.error(f"[Agent] MCP call failed with status {resp.status_code}: {resp.text}")
                return json.dumps({"error": f"MCP call failed with status {resp.status_code}", "detail": resp.text})
        except Exception as e:
            logger.exception(f"[Agent] Exception calling MCP: {e}")
            return json.dumps({"error": f"Exception calling MCP: {str(e)}"})


# ============================================================
# M365 Outlook Tool Declarations
# ============================================================

async def search_emails(
    ctx: CallbackContext,
    query: Optional[str] = None,
    sender: Optional[str] = None,
    hours_back: Optional[str] = None,
    unread_only: bool = False,
    limit: int = 25
) -> dict:
    """Search mailbox emails with keyword query expansion and date filtering.
    
    Args:
        query: Free-text keyword
        sender: Sender email address
        hours_back: Lookback window e.g. 24h, 7d, 720h
        unread_only: Filter unread only
        limit: Max results to return
    """
async def search_emails(
    ctx: CallbackContext,
    query: Optional[str] = None,
    sender: Optional[str] = None,
    hours_back: Optional[str] = None,
    unread_only: bool = False,
    limit: int = 25
) -> dict:
    """Search mailbox emails with keyword query expansion and date filtering.


    
    Args:
        query: Free-text keyword
        sender: Sender email address
        hours_back: Lookback window e.g. 24h, 7d
        unread_only: Filter unread only
        limit: Max results to return
    """
    return await _call_mcp(ctx, "search_emails", {
        "query": query, "sender": sender, "hours_back": hours_back, "unread_only": unread_only, "limit": limit
    })

async def get_email_full_body(ctx: CallbackContext, message_id: str) -> dict:
    """Fetch the complete body/payload for a specific email message ID.
    
    Args:
        message_id: The email message ID
    """
    return await _call_mcp(ctx, "get_email_full_body", {"message_id": message_id})

async def list_meetings(
    ctx: CallbackContext,
    lookback: str = "24h",
    lookahead: str = "48h",
    limit: int = 25
) -> dict:
    """List calendar meetings and schedule details within a time window.
    
    Args:
        lookback: Lookback window e.g. 24h, 7d
        lookahead: Lookahead window e.g. 48h, 7d
        limit: Max results to return
    """
    return await _call_mcp(ctx, "list_meetings", {
        "lookback": lookback, "lookahead": lookahead, "limit": limit
    })

async def send_email(
    ctx: CallbackContext,
    subject: str,
    body: str,
    to_recipients: List[str],
    importance: str = "normal",
    attachment_filename: Optional[str] = None
) -> dict:
    """Send an outgoing email message.
    
    Args:
        subject: Email subject
        body: Email body content
        to_recipients: List of recipient email addresses
        importance: high, normal, low
        attachment_filename: Optional name of file to attach from Downloads
    """
    return await _call_mcp(ctx, "send_email", {
        "subject": subject, "body": body, "to_recipients": to_recipients, "importance": importance, "attachment_filename": attachment_filename
    })

async def reply_email(ctx: CallbackContext, message_id: str, comment: str) -> dict:
    """Reply to an existing email thread using the message ID and comments.
    
    Args:
        message_id: The message ID to reply to
        comment: Comments / reply text
    """
    return await _call_mcp(ctx, "reply_email", {"message_id": message_id, "comment": comment})

async def create_meeting(
    ctx: CallbackContext,
    subject: str,
    start_time: str,
    end_time: str,
    attendees: Optional[List[str]] = None
) -> dict:
    """Create/schedule a new calendar meeting.
    
    Args:
        subject: Meeting title
        start_time: ISO 8601 UTC format e.g. 2026-07-25T14:00:00Z
        end_time: ISO 8601 UTC format
        attendees: List of invitee emails
    """
    return await _call_mcp(ctx, "create_meeting", {
        "subject": subject, "start_time": start_time, "end_time": end_time, "attendees": attendees
    })

async def delete_email(ctx: CallbackContext, message_id: str) -> dict:
    """Delete a specific email by message ID (moves it to Deleted Items).
    
    Args:
        message_id: The email message ID
    """
    return await _call_mcp(ctx, "delete_email", {"message_id": message_id})

async def move_email(ctx: CallbackContext, message_id: str, destination_folder_name: str) -> dict:
    """Move an email to a specific folder (creates folder if needed).
    
    Args:
        message_id: The email message ID
        destination_folder_name: Target folder name
    """
    return await _call_mcp(ctx, "move_email", {
        "message_id": message_id, "destination_folder_name": destination_folder_name
    })

async def restore_email(ctx: CallbackContext, message_id: str) -> dict:
    """Restore a deleted email by moving it back to the Inbox.
    
    Args:
        message_id: The email message ID
    """
    return await _call_mcp(ctx, "restore_email", {"message_id": message_id})

async def flag_email(ctx: CallbackContext, message_id: str, flag_status: str = "flagged") -> dict:
    """Set follow-up flag status for an email.
    
    Args:
        message_id: The email message ID
        flag_status: flagged, notFlagged, complete
    """
    return await _call_mcp(ctx, "flag_email", {"message_id": message_id, "flag_status": flag_status})

async def mark_email_read_status(ctx: CallbackContext, message_id: str, is_read: bool) -> dict:
    """Mark email as read (true) or unread (false).
    
    Args:
        message_id: The email message ID
        is_read: True for read, False for unread
    """
    return await _call_mcp(ctx, "mark_email_read_status", {"message_id": message_id, "is_read": is_read})




async def get_system_time(ctx: CallbackContext, timezone: str = "UTC") -> str:
    """Get the current system date and time in the specified timezone (e.g. 'America/New_York', 'UTC').
    Always call this tool to find out the current date and time if needed to resolve relative expressions like 'today', 'tomorrow', 'yesterday' or 'next week'.
    """
    import datetime
    try:
        import zoneinfo
        tz = zoneinfo.ZoneInfo(timezone)
    except Exception:
        tz = datetime.timezone.utc
        timezone = "UTC"
    now = datetime.datetime.now(tz)
    return now.strftime(f"%A, %B %d, %Y, %I:%M %p {timezone}")

# Initialize the ADK LlmAgent
root_agent = LlmAgent(
    name="M365OutlookExecutiveAgent",
    model="gemini-3.6-flash",
    instruction=open(os.path.join(os.path.dirname(__file__), "system_instructions.txt"), "r").read(),
    tools=[
        get_system_time,
        search_emails,
        get_email_full_body,
        list_meetings,
        send_email,
        reply_email,
        create_meeting,
        delete_email,
        move_email,
        restore_email,
        flag_email,
        mark_email_read_status
    ],
)

__all__ = ["root_agent"]
