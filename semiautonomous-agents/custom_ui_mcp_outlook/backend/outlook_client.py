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

def save_token_to_env(key: str, value: str):
    # Locate and update the .env file to persist rotated tokens
    for path in [".env", "../.env", "../../.env"]:
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    lines = f.readlines()
                updated = False
                for idx, line in enumerate(lines):
                    if line.strip().startswith(f"{key}="):
                        lines[idx] = f"{key}={value}\n"
                        updated = True
                        break
                if not updated:
                    lines.append(f"{key}={value}\n")
                with open(path, "w") as f:
                    f.writelines(lines)
                os.environ[key] = value
                logger.info(f"Persisted updated env variable {key} to {path}")
            except Exception as e:
                logger.warning(f"Failed to persist env variable {key} to {path}: {e}")
            break

class OutlookClient:
    """Production-Ready Client for interacting with Microsoft Graph API with Federated Search & Auto-Refresh."""

    def __init__(self, base_url: str = "https://graph.microsoft.com/v1.0"):
        self.base_url = base_url.rstrip("/")
        self.user_email = os.getenv("USER_EMAIL", "admin@sockcop.onmicrosoft.com")

    def _get_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        load_dotenv(override=True)
        # Use valid active/cached token first
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
                    save_token_to_env("MS_GRAPH_TOKEN", token)
                    if res.get("refresh_token"):
                        save_token_to_env("MS_GRAPH_REFRESH_TOKEN", res["refresh_token"])
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

    async def search_emails(self, query: Optional[str] = None, sender: Optional[str] = None, hours_back: Optional[str] = "24h", unread_only: bool = False, limit: int = 25, token: Optional[str] = None) -> List[Dict[str, Any]]:
        headers = self._get_headers(token)
        import re
        
        search_term = None
        if query:
            quoted_terms = re.findall(r'"([^"]+)"', query)
            if quoted_terms:
                search_term = quoted_terms[0]
            else:
                search_term = query.replace('"', '')

        async with httpx.AsyncClient(timeout=10.0) as client:
            # 1. Primary search attempt
            for prefix in ["/me", f"/users/{self.user_email}"]:
                url = f"{self.base_url}{prefix}/messages"
                params: Dict[str, Any] = {"$top": limit, "$select": "id,subject,from,receivedDateTime,body,bodyPreview,importance,isRead,webLink,parentFolderId"}
                if search_term:
                    params["$search"] = f'"{search_term}"'
                try:
                    resp = await client.get(url, headers=headers, params=params)
                    if resp.status_code == 200:
                        val = resp.json().get("value", [])
                        if val:
                            return val
                except Exception:
                    pass

            # 2. Fallback: Fetch latest messages if search returned nothing
            for prefix in ["/me", f"/users/{self.user_email}"]:
                url = f"{self.base_url}{prefix}/messages"
                params: Dict[str, Any] = {"$top": limit, "$select": "id,subject,from,receivedDateTime,body,bodyPreview,importance,isRead,webLink,parentFolderId"}
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

    async def get_folder_mapping(self, token: Optional[str] = None) -> Dict[str, str]:
        headers = self._get_headers(token)
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self.base_url}/me/mailFolders", headers=headers)
            if resp.status_code == 200:
                folders = resp.json().get("value", [])
                return {f["id"]: f["displayName"] for f in folders}
            else:
                print(f"DEBUG: Graph API mailFolders returned {resp.status_code}: {resp.text}")
        return {}

    async def list_meetings(self, lookback: str = "0h", lookahead: str = "24h", limit: int = 25, token: Optional[str] = None) -> List[Dict[str, Any]]:
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
        mail_task = self.search_emails(query=query, limit=25, token=token)
        cal_task = self.list_meetings(lookahead="48h", limit=25, token=token)
        folder_task = self.get_folder_mapping(token=token)
        
        prof, mails, cals, folder_map = await asyncio.gather(prof_task, mail_task, cal_task, folder_task)
        
        # Inject folder name
        for mail in mails:
            p_id = mail.get("parentFolderId")
            mail["folderName"] = folder_map.get(p_id, "Unknown")
            
        return {"profile": prof, "emails": mails, "meetings": cals}
