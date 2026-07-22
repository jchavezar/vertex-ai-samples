import os
import sys
import logging
import datetime
import asyncio
from typing import Any, Dict, List, Optional
import httpx
from mcp.server.fastmcp import FastMCP

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("outlook-enterprise-mcp")

# Initialize Production FastMCP Server
mcp = FastMCP(
    "Outlook-Enterprise-MCP",
    dependencies=["httpx", "msal", "pydantic"]
)

# ---------------------------------------------------------------------------
# Embedded Self-Contained Microsoft Graph Engine
# ---------------------------------------------------------------------------
class MicrosoftGraphEngine:
    """Self-contained Graph API Engine with MSAL Token Auto-Refresh & Federated Search."""

    def __init__(self, base_url: str = "https://graph.microsoft.com/v1.0"):
        self.base_url = base_url.rstrip("/")

    def get_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        from dotenv import load_dotenv
        load_dotenv()
        load_dotenv("../.env")
        load_dotenv("../../.env")

        if not token:
            token = os.getenv("MS_GRAPH_TOKEN")

        refresh_token = os.getenv("MS_GRAPH_REFRESH_TOKEN")
        client_id = os.getenv("CLIENT_ID") or os.getenv("CONNECTOR_CLIENT_ID")
        client_secret = os.getenv("CLIENT_SECRET") or os.getenv("CONNECTOR_CLIENT_SECRET")
        tenant_id = os.getenv("TENANT_ID") or "common"

        # MSAL Auto-Refresh Persistence
        if refresh_token and client_id and client_secret and not token:
            try:
                import msal
                app = msal.ConfidentialClientApplication(
                    client_id,
                    authority=f"https://login.microsoftonline.com/{tenant_id}",
                    client_credential=client_secret
                )
                res = app.acquire_token_by_refresh_token(
                    refresh_token,
                    scopes=["https://graph.microsoft.com/User.Read", "https://graph.microsoft.com/Mail.Read", "https://graph.microsoft.com/Calendars.Read", "offline_access"]
                )
                new_token = res.get("access_token")
                if new_token:
                    token = new_token
                    os.environ["MS_GRAPH_TOKEN"] = new_token
                    if res.get("refresh_token"):
                        os.environ["MS_GRAPH_REFRESH_TOKEN"] = res.get("refresh_token")
                    logger.info("Auto-refreshed MS_GRAPH_TOKEN successfully.")
            except Exception as ex:
                logger.warning(f"Token refresh attempt failed: {ex}")

        if not token:
            raise ValueError("🔑 Microsoft Graph authentication token missing. Please authenticate via OAuth.")

        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Prefer": "outlook.body-content-type=text",
            "ConsistencyLevel": "eventual",
        }

    def parse_hours(self, hours_str: Optional[str]) -> Optional[datetime.timedelta]:
        if not hours_str:
            return None
        h = str(hours_str).strip().lower()
        if h.endswith("h"): return datetime.timedelta(hours=int(h[:-1]))
        if h.endswith("d"): return datetime.timedelta(days=int(h[:-1]))
        if h.endswith("w"): return datetime.timedelta(weeks=int(h[:-1]))
        return datetime.timedelta(hours=int(h))

engine = MicrosoftGraphEngine()

# ---------------------------------------------------------------------------
# Complete 8-Tool Enterprise MCP Suite
# ---------------------------------------------------------------------------

@mcp.tool()
async def federated_m365_search(query: str, token: Optional[str] = None) -> str:
    """Execute parallel federated search across user profile, emails, and calendar events."""
    try:
        headers = engine.get_headers(token)
        
        async def fetch_prof(client):
            r = await client.get(f"{engine.base_url}/me", headers=headers)
            return r.json() if r.status_code == 200 else {}

        async def fetch_mails(client):
            params = {"$top": 5, "$select": "id,subject,from,receivedDateTime,bodyPreview"}
            r = await client.get(f"{engine.base_url}/me/mailFolders/inbox/messages", headers=headers, params=params)
            return r.json().get("value", []) if r.status_code == 200 else []

        async def fetch_cal(client):
            now = datetime.datetime.now(datetime.timezone.utc)
            params = {
                "startDateTime": (now - datetime.timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "endDateTime": (now + datetime.timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "$top": 5,
                "$select": "id,subject,start,end,organizer,webLink"
            }
            r = await client.get(f"{engine.base_url}/me/calendar/calendarView", headers=headers, params=params)
            return r.json().get("value", []) if r.status_code == 200 else []

        async with httpx.AsyncClient(timeout=15.0) as client:
            prof, mails, cals = await asyncio.gather(fetch_prof(client), fetch_mails(client), fetch_cal(client))

        out = [f"### 🌐 Federated Microsoft 365 Search Results for '{query}':"]
        if prof:
            out.append(f"* **User Profile**: {prof.get('displayName')} ({prof.get('userPrincipalName')}) | Title: {prof.get('jobTitle') or 'None'}")
        if mails:
            out.append(f"* **Emails Found ({len(mails)})**:")
            for em in mails[:3]:
                out.append(f"  - **{em.get('subject')}** (From: {(em.get('from') or {}).get('emailAddress', {}).get('address')})\n    Preview: {em.get('bodyPreview')}")
        if cals:
            out.append(f"* **Calendar Events ({len(cals)})**:")
            for mt in cals[:3]:
                out.append(f"  - **{mt.get('subject')}** (Time: {(mt.get('start') or {}).get('dateTime')})")
        return "\n\n".join(out)
    except Exception as e:
        return f"Federated search error: {str(e)}"

@mcp.tool()
async def search_emails(
    query: Optional[str] = None,
    sender: Optional[str] = None,
    hours_back: Optional[str] = "24h",
    unread_only: bool = False,
    limit: int = 10,
    token: Optional[str] = None
) -> str:
    """Search Outlook inbox emails with keyword query expansion and date filtering."""
    try:
        headers = engine.get_headers(token)
        url = f"{engine.base_url}/me/mailFolders/inbox/messages"
        params: Dict[str, Any] = {"$top": limit, "$select": "id,subject,from,receivedDateTime,bodyPreview,isRead"}

        filters = []
        if unread_only: filters.append("isRead eq false")
        if sender: filters.append(f"from/emailAddress/address eq '{sender}'")
        delta = engine.parse_hours(hours_back)
        if delta:
            since = (datetime.datetime.now(datetime.timezone.utc) - delta).strftime("%Y-%m-%dT%H:%M:%SZ")
            filters.append(f"receivedDateTime ge {since}")
        if filters: params["$filter"] = " and ".join(filters)
        if query: params["$search"] = f'"{query}"'
        if "$search" not in params: params["$orderby"] = "receivedDateTime desc"

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers=headers, params=params)
            if resp.status_code == 200:
                emails = resp.json().get("value", [])
                if not emails: return "No emails found matching criteria."
                lines = []
                for i, em in enumerate(emails, 1):
                    lines.append(f"{i}. **{em.get('subject')}**\n   From: {(em.get('from') or {}).get('emailAddress', {}).get('address')}\n   Date: {em.get('receivedDateTime')}\n   Preview: {em.get('bodyPreview')}\n   ID: `{em.get('id')}`")
                return "\n\n".join(lines)
            elif resp.status_code == 400 and "$search" in params:
                del params["$search"]
                params["$orderby"] = "receivedDateTime desc"
                resp2 = await client.get(url, headers=headers, params=params)
                items = resp2.json().get("value", [])
                ql = query.lower()
                matched = [em for em in items if ql in (em.get("subject") or "").lower() or ql in (em.get("bodyPreview") or "").lower()]
                if not matched: return "No emails found matching criteria."
                return "\n\n".join([f"{i}. **{em.get('subject')}** (Preview: {em.get('bodyPreview')})" for i, em in enumerate(matched[:limit], 1)])
            return f"Graph API Error: {resp.status_code} {resp.text}"
    except Exception as e:
        return f"Error searching emails: {str(e)}"

@mcp.tool()
async def get_email_full_body(message_id: str, token: Optional[str] = None) -> str:
    """Fetch complete MIME HTML/Text payload for a specific email message."""
    try:
        headers = engine.get_headers(token)
        url = f"{engine.base_url}/me/messages/{message_id}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers=headers, params={"$select": "id,subject,from,receivedDateTime,body"})
            if resp.status_code != 200: return f"Error fetching email: {resp.status_code} {resp.text}"
            data = resp.json()
            return f"### Subject: {data.get('subject')}\n**From**: {(data.get('from') or {}).get('emailAddress', {}).get('address')}\n\n**Full Content**:\n{(data.get('body') or {}).get('content', '')}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def list_meetings(lookback: str = "0h", lookahead: str = "24h", limit: int = 10, token: Optional[str] = None) -> str:
    """List calendar meetings from Microsoft Outlook."""
    try:
        headers = engine.get_headers(token)
        now = datetime.datetime.now(datetime.timezone.utc)
        st = (now - (engine.parse_hours(lookback) or datetime.timedelta(0))).strftime("%Y-%m-%dT%H:%M:%SZ")
        en = (now + (engine.parse_hours(lookahead) or datetime.timedelta(hours=24))).strftime("%Y-%m-%dT%H:%M:%SZ")
        url = f"{engine.base_url}/me/calendar/calendarView"
        params = {"startDateTime": st, "endDateTime": en, "$top": limit, "$select": "id,subject,start,end,organizer,webLink"}

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers=headers, params=params)
            if resp.status_code != 200: return f"Error: {resp.status_code} {resp.text}"
            meetings = resp.json().get("value", [])
            if not meetings: return "No meetings scheduled in this timeframe."
            lines = []
            for i, m in enumerate(meetings, 1):
                lines.append(f"{i}. **{m.get('subject')}** (Time: {(m.get('start') or {}).get('dateTime')} to {(m.get('end') or {}).get('dateTime')})\n   Organizer: {(m.get('organizer') or {}).get('emailAddress', {}).get('name')}\n   Link: {m.get('webLink')}")
            return "\n\n".join(lines)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def get_user_profile(user_email: Optional[str] = None, token: Optional[str] = None) -> str:
    """Retrieve Azure AD / Microsoft Graph user profile details."""
    try:
        headers = engine.get_headers(token)
        path = f"/users/{user_email}" if user_email else "/me"
        url = f"{engine.base_url}{path}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200: return f"Error: {resp.status_code} {resp.text}"
            p = resp.json()
            return f"**Display Name**: {p.get('displayName')}\n**Email**: {p.get('userPrincipalName')}\n**Job Title**: {p.get('jobTitle') or 'None'}\n**Office**: {p.get('officeLocation') or 'None'}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def send_email(subject: str, body: str, to_recipients: List[str], token: Optional[str] = None) -> str:
    """Send an outgoing email message via Microsoft Graph API."""
    try:
        headers = engine.get_headers(token)
        url = f"{engine.base_url}/me/sendMail"
        payload = {
            "message": {
                "subject": subject,
                "body": {"contentType": "Text", "content": body},
                "toRecipients": [{"emailAddress": {"address": a}} for a in to_recipients]
            }
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            return "Email sent successfully." if resp.status_code in (200, 202) else f"Error: {resp.status_code} {resp.text}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def reply_email(message_id: str, comment: str, token: Optional[str] = None) -> str:
    """Reply to an existing email thread."""
    try:
        headers = engine.get_headers(token)
        url = f"{engine.base_url}/me/messages/{message_id}/reply"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers=headers, json={"comment": comment})
            return "Reply posted successfully." if resp.status_code in (200, 202) else f"Error: {resp.status_code} {resp.text}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def create_meeting(subject: str, start_time: str, end_time: str, attendees: Optional[List[str]] = None, token: Optional[str] = None) -> str:
    """Create a new Microsoft Teams calendar event."""
    try:
        headers = engine.get_headers(token)
        url = f"{engine.base_url}/me/events"
        payload = {
            "subject": subject,
            "start": {"dateTime": start_time, "timeZone": "UTC"},
            "end": {"dateTime": end_time, "timeZone": "UTC"},
            "isOnlineMeeting": True,
            "onlineMeetingProvider": "teamsForBusiness",
            "attendees": [{"emailAddress": {"address": a}, "type": "required"} for a in (attendees or [])]
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            return "Meeting created successfully." if resp.status_code in (200, 201) else f"Error: {resp.status_code} {resp.text}"
    except Exception as e:
        return f"Error: {str(e)}"

# ---------------------------------------------------------------------------
# Cloud Run SSE & Local STDIO Transports
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "stdio").lower()
    port = int(os.getenv("PORT", 8080))
    if transport == "sse":
        logger.info(f"Starting Production FastMCP Server with SSE on port {port}...")
        mcp.run(transport="sse")
    else:
        logger.info("Starting Production FastMCP Server over STDIO...")
        mcp.run()
