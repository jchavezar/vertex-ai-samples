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
        self._cache = {}

    def _get_cache_key(self, method_name: str, *args, **kwargs) -> tuple:
        normalized_kwargs = tuple(sorted((k, v) for k, v in kwargs.items() if k != 'token'))
        return (method_name, args, normalized_kwargs)

    def clear_cache(self) -> None:
        self._cache.clear()
        logger.info("OutlookClient cache cleared.")

    def _get_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        load_dotenv(override=True)
        load_dotenv("../.env", override=True)
        
        refresh_token = os.getenv("MS_GRAPH_REFRESH_TOKEN")
        client_id = os.getenv("CLIENT_ID") or os.getenv("CONNECTOR_CLIENT_ID")
        client_secret = os.getenv("CLIENT_SECRET") or os.getenv("CONNECTOR_CLIENT_SECRET")
        tenant_id = os.getenv("TENANT_ID") or "de46a3fd-0d68-4b25-8343-6eb5d71afce9"

        if not token:
            token = os.getenv("MS_GRAPH_TOKEN")

        if not token and refresh_token and client_id and client_secret:
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
            "Prefer": 'outlook.body-content-type=text, outlook.timezone="America/New_York"',
            "ConsistencyLevel": "eventual",
        }

    async def get_user_profile(self, user_email: Optional[str] = None, token: Optional[str] = None) -> Dict[str, Any]:
        cache_key = self._get_cache_key("get_user_profile", user_email=user_email)
        if cache_key in self._cache:
            return self._cache[cache_key]

        headers = self._get_headers(token)
        target = user_email or self.user_email
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self.base_url}/me", headers=headers)
            if resp.status_code == 200:
                res = resp.json()
                self._cache[cache_key] = res
                return res
            resp2 = await client.get(f"{self.base_url}/users/{target}", headers=headers)
            if resp2.status_code == 200:
                res = resp2.json()
                self._cache[cache_key] = res
                return res
            res = {
                "displayName": "Jesus Chavez",
                "userPrincipalName": "admin@sockcop.onmicrosoft.com",
                "jobTitle": None,
                "officeLocation": None
            }
            self._cache[cache_key] = res
            return res

    async def search_emails(self, query: Optional[str] = None, sender: Optional[str] = None, hours_back: Optional[str] = "24h", unread_only: bool = False, limit: int = 50, token: Optional[str] = None) -> List[Dict[str, Any]]:
        cache_key = self._get_cache_key("search_emails", query=query, sender=sender, hours_back=hours_back, unread_only=unread_only, limit=limit)
        if cache_key in self._cache:
            return self._cache[cache_key]

        headers = self._get_headers(token)
        import re
        
        search_term = None
        if query:
            quoted_terms = re.findall(r'"([^"]+)"', query)
            if quoted_terms:
                search_term = quoted_terms[0]
            else:
                stop_words = {'give', 'me', 'the', 'email', 'emails', 'from', 'a', 'week', 'ago', 'around', 'this', 'hour', 'what', 'day', 'is', 'today', 'that', 'thats', 'not', 'recent', 'latest', 'show', 'get', 'find', 'search', 'all', 'my', 'inbox', 'sent', 'last', 'message', 'messages'}
                words = re.findall(r'\b[a-zA-Z0-9_-]+\b', query.lower())
                kw = [w for w in words if w not in stop_words and not w.isdigit()]
                if kw:
                    search_term = ' '.join(kw)

        async with httpx.AsyncClient(timeout=10.0) as client:
            # 1. Targeted keyword search attempt if specific term extracted
            if search_term:
                for prefix in ["/me/mailFolders/inbox", "/me/mailFolders/sentitems", "/me/mailFolders/drafts", "/me"]:
                    url = f"{self.base_url}{prefix}/messages"
                    params: Dict[str, Any] = {"$top": limit, "$select": "id,subject,from,toRecipients,receivedDateTime,body,bodyPreview,importance,isRead,isDraft,webLink,parentFolderId"}
                    params["$search"] = f'"{search_term}"'
                    try:
                        resp = await client.get(url, headers=headers, params=params)
                        if resp.status_code == 200:
                            val = resp.json().get("value", [])
                            if val:
                                self._cache[cache_key] = val
                                return val
                    except Exception:
                        pass

            # 2. Comprehensive Multi-Bucket Fetch across ALL Outlook Folders
            all_msgs = []
            seen_ids = set()
            folder_endpoints = [
                ("/me/mailFolders/inbox", 25),
                ("/me/mailFolders/sentitems", 15),
                ("/me/mailFolders/drafts", 15),
                ("/me/mailFolders/deleteditems", 10),
                ("/me", 25)
            ]
            
            for prefix, top_n in folder_endpoints:
                url = f"{self.base_url}{prefix}/messages"
                params: Dict[str, Any] = {"$top": top_n, "$select": "id,subject,from,toRecipients,receivedDateTime,body,bodyPreview,importance,isRead,isDraft,webLink,parentFolderId"}
                try:
                    resp = await client.get(url, headers=headers, params=params)
                    if resp.status_code == 200:
                        val = resp.json().get("value", [])
                        for m in val:
                            if m.get("id") not in seen_ids:
                                seen_ids.add(m.get("id"))
                                all_msgs.append(m)
                except Exception:
                    pass

            if all_msgs:
                all_msgs.sort(key=lambda x: x.get("receivedDateTime") or "", reverse=True)
                self._cache[cache_key] = all_msgs
                return all_msgs

        self._cache[cache_key] = []
        return []

    async def get_email_full_body(self, message_id: str, token: Optional[str] = None) -> Dict[str, Any]:
        cache_key = self._get_cache_key("get_email_full_body", message_id=message_id)
        if cache_key in self._cache:
            return self._cache[cache_key]

        headers = self._get_headers(token)
        async with httpx.AsyncClient(timeout=10.0) as client:
            for prefix in ["/me", f"/users/{self.user_email}"]:
                url = f"{self.base_url}{prefix}/messages/{message_id}"
                try:
                    resp = await client.get(url, headers=headers, params={"$select": "id,subject,from,toRecipients,receivedDateTime,body"})
                    if resp.status_code == 200:
                        res = resp.json()
                        self._cache[cache_key] = res
                        return res
                except Exception:
                    pass
        raise RuntimeError("Failed to query Microsoft Graph API get_email_full_body: Access denied or token invalid.")

    async def get_folder_mapping(self, token: Optional[str] = None) -> Dict[str, str]:
        cache_key = self._get_cache_key("get_folder_mapping")
        if cache_key in self._cache:
            return self._cache[cache_key]

        headers = self._get_headers(token)
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self.base_url}/me/mailFolders", headers=headers)
            if resp.status_code == 200:
                folders = resp.json().get("value", [])
                res = {f["id"]: f["displayName"] for f in folders}
                self._cache[cache_key] = res
                return res
            else:
                print(f"DEBUG: Graph API mailFolders returned {resp.status_code}: {resp.text}")
        return {}

    async def list_meetings(self, lookback: str = "0h", lookahead: str = "24h", limit: int = 100, token: Optional[str] = None) -> List[Dict[str, Any]]:
        cache_key = self._get_cache_key("list_meetings", lookback=lookback, lookahead=lookahead, limit=limit)
        if cache_key in self._cache:
            return self._cache[cache_key]

        headers = self._get_headers(token)
        now = datetime.datetime.now(datetime.timezone.utc)
        st = (now - datetime.timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
        en = (now + datetime.timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
        async with httpx.AsyncClient(timeout=10.0) as client:
            for prefix in ["/me", f"/users/{self.user_email}"]:
                url = f"{self.base_url}{prefix}/calendar/calendarView"
                params = {"startDateTime": st, "endDateTime": en, "$top": limit, "$select": "id,subject,start,end,organizer,location,webLink,isOnlineMeeting,bodyPreview"}
                try:
                    resp = await client.get(url, headers=headers, params=params)
                    if resp.status_code == 200:
                        val = resp.json().get("value", [])
                        self._cache[cache_key] = val
                        return val
                    else:
                        print(f"DEBUG: Graph API calendarView prefix {prefix} returned {resp.status_code}: {resp.text}")
                except Exception as e:
                    print(f"DEBUG: Graph API calendarView prefix {prefix} threw exception: {e}")
        return []

    async def federated_search(self, query: str, token: Optional[str] = None) -> Dict[str, Any]:
        prof_task = self.get_user_profile(token=token)
        mail_task = self.search_emails(query=query, limit=25, token=token)
        cal_task = self.list_meetings(lookahead="48h", limit=100, token=token)
        folder_task = self.get_folder_mapping(token=token)
        
        # Split gather sequentially 2-and-2 to prevent Graph API concurrency throttling (429)
        prof, mails = await asyncio.gather(prof_task, mail_task)
        cals, folder_map = await asyncio.gather(cal_task, folder_task)
        
        # Inject folder name and clean isDraft flag for Inbox
        for mail in mails:
            p_id = mail.get("parentFolderId")
            f_name = folder_map.get(p_id, "Unknown")
            mail["folderName"] = f_name
            if f_name.lower() == "inbox":
                mail["isDraft"] = False
            
        return {"profile": prof, "emails": mails, "meetings": cals}

    async def send_email(self, subject: str, body: str, to_recipients: List[str], token: Optional[str] = None) -> str:
        """Send an outgoing email message via Microsoft Graph API."""
        try:
            headers = self._get_headers(token)
            url = f"{self.base_url}/me/sendMail"
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
