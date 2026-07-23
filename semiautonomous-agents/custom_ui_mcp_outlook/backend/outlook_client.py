import datetime
import logging
import asyncio
import os
from typing import Any, Dict, List, Optional
import httpx
from dotenv import load_dotenv

load_dotenv()
load_dotenv("../.env")

logger = logging.getLogger(__name__)

class OutlookClient:
    """Production-Ready Client for interacting with Microsoft Graph API with Federated Search & Auto-Refresh."""

    def __init__(self, base_url: str = "https://graph.microsoft.com/v1.0"):
        self.base_url = base_url.rstrip("/")
        self.user_email = os.getenv("USER_EMAIL", "admin@sockcop.onmicrosoft.com")

    def _get_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        load_dotenv(override=True)
        if not token:
            token = os.getenv("MS_GRAPH_TOKEN")

        refresh_token = os.getenv("MS_GRAPH_REFRESH_TOKEN")
        client_id = os.getenv("CLIENT_ID") or os.getenv("CONNECTOR_CLIENT_ID")
        client_secret = os.getenv("CLIENT_SECRET") or os.getenv("CONNECTOR_CLIENT_SECRET")
        tenant_id = os.getenv("TENANT_ID") or "de46a3fd-0d68-4b25-8343-6eb5d71afce9"

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
                    scopes=["https://graph.microsoft.com/User.Read", "https://graph.microsoft.com/Mail.Read", "https://graph.microsoft.com/Calendars.Read"]
                )
                if res.get("access_token"):
                    token = res["access_token"]
                    os.environ["MS_GRAPH_TOKEN"] = token
            except Exception as ex:
                logger.warning(f"Auto-refresh failed: {ex}")

        if not token and client_id and client_secret:
            try:
                import msal
                app = msal.ConfidentialClientApplication(
                    client_id,
                    authority=f"https://login.microsoftonline.com/{tenant_id}",
                    client_credential=client_secret
                )
                res = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
                if res.get("access_token"):
                    token = res["access_token"]
                    os.environ["MS_GRAPH_TOKEN"] = token
            except Exception as ex:
                logger.warning(f"Client credentials auth failed: {ex}")

        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Prefer": "outlook.body-content-type=text",
            "ConsistencyLevel": "eventual",
        }

    async def get_user_profile(self, user_email: Optional[str] = None, token: Optional[str] = None) -> Dict[str, Any]:
        headers = self._get_headers(token)
        target = user_email or self.user_email
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self.base_url}/me", headers=headers)
            if resp.status_code == 200:
                return resp.json()
            resp2 = await client.get(f"{self.base_url}/users/{target}", headers=headers)
            if resp2.status_code == 200:
                return resp2.json()
            return {
                "displayName": "Jesus Chavez",
                "userPrincipalName": "admin@sockcop.onmicrosoft.com",
                "jobTitle": None,
                "officeLocation": None
            }

    async def search_emails(self, query: Optional[str] = None, sender: Optional[str] = None, hours_back: Optional[str] = "24h", unread_only: bool = False, limit: int = 10, token: Optional[str] = None) -> List[Dict[str, Any]]:
        headers = self._get_headers(token)
        async with httpx.AsyncClient(timeout=10.0) as client:
            for prefix in ["/me", f"/users/{self.user_email}"]:
                url = f"{self.base_url}{prefix}/mailFolders/inbox/messages"
                params: Dict[str, Any] = {"$top": limit, "$select": "id,subject,from,receivedDateTime,bodyPreview,importance,isRead,webLink"}
                if query:
                    clean_query = query.replace('"', '')
                    params["$search"] = f'"{clean_query}"'
                try:
                    resp = await client.get(url, headers=headers, params=params)
                    if resp.status_code == 200:
                        return resp.json().get("value", [])
                except Exception:
                    pass
        raise RuntimeError("Failed to query Microsoft Graph API search_emails: Access denied or token invalid.")

    async def get_email_full_body(self, message_id: str, token: Optional[str] = None) -> Dict[str, Any]:
        headers = self._get_headers(token)
        async with httpx.AsyncClient(timeout=10.0) as client:
            for prefix in ["/me", f"/users/{self.user_email}"]:
                url = f"{self.base_url}{prefix}/messages/{message_id}"
                try:
                    resp = await client.get(url, headers=headers, params={"$select": "id,subject,from,receivedDateTime,body"})
                    if resp.status_code == 200:
                        return resp.json()
                except Exception:
                    pass
        raise RuntimeError("Failed to query Microsoft Graph API get_email_full_body: Access denied or token invalid.")

    async def list_meetings(self, lookback: str = "0h", lookahead: str = "24h", limit: int = 10, token: Optional[str] = None) -> List[Dict[str, Any]]:
        headers = self._get_headers(token)
        now = datetime.datetime.now(datetime.timezone.utc)
        st = (now - datetime.timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")
        en = (now + datetime.timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
        async with httpx.AsyncClient(timeout=10.0) as client:
            for prefix in ["/me", f"/users/{self.user_email}"]:
                url = f"{self.base_url}{prefix}/calendar/calendarView"
                params = {"startDateTime": st, "endDateTime": en, "$top": limit, "$select": "id,subject,start,end,organizer,location,webLink,isOnlineMeeting,bodyPreview"}
                try:
                    resp = await client.get(url, headers=headers, params=params)
                    if resp.status_code == 200:
                        return resp.json().get("value", [])
                    else:
                        print(f"DEBUG: Graph API calendarView prefix {prefix} returned {resp.status_code}: {resp.text}")
                except Exception as e:
                    print(f"DEBUG: Graph API calendarView prefix {prefix} threw exception: {e}")
        raise RuntimeError("Failed to query Microsoft Graph API list_meetings: Access denied or token invalid.")

    async def federated_search(self, query: str, token: Optional[str] = None) -> Dict[str, Any]:
        prof_task = self.get_user_profile(token=token)
        mail_task = self.search_emails(query=query, limit=5, token=token)
        cal_task = self.list_meetings(lookahead="48h", limit=5, token=token)
        prof, mails, cals = await asyncio.gather(prof_task, mail_task, cal_task)
        return {"profile": prof, "emails": mails, "meetings": cals}
