import os
import json
import time
import base64
import logging
from typing import Dict, Any, List, Optional
import requests
from google.cloud import secretmanager

logger = logging.getLogger(__name__)

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
SECRET_ID = os.environ.get("GWORKSPACE_SECRET_ID", "gworkspace-mcp-tokens")

class GmailService:
    def __init__(self):
        self.is_connected = False
        self.user_email = None
        self.access_token = None
        self._check_initial_auth()

    def _check_initial_auth(self):
        """Check if Secret Manager or environment has valid tokens."""
        try:
            client = secretmanager.SecretManagerServiceClient()
            name = f"projects/{PROJECT_ID}/secrets/{SECRET_ID}/versions/latest"
            resp = client.access_secret_version(request={"name": name})
            raw = resp.payload.data.decode("utf-8")
            data = json.loads(raw)
            self.access_token = data.get("access_token")
            self.user_email = data.get("user_info", {}).get("email", "jesusarguelles@google.com")
            self.is_connected = True
            logger.info(f"GmailService initialized for {self.user_email}")
        except Exception as e:
            logger.warning(f"GmailService could not load Secret Manager tokens: {e}")
            self.is_connected = False

    def get_status(self) -> Dict[str, Any]:
        return {
            "connected": self.is_connected,
            "email": self.user_email or "Not connected",
            "provider": "Google Workspace / Gmail API",
            "scopes": ["gmail.readonly", "gmail.labels"]
        }

    def connect(self, email: Optional[str] = None) -> Dict[str, Any]:
        """Simulate or complete OAuth connection."""
        self._check_initial_auth()
        if not self.is_connected:
            self.is_connected = True
            self.user_email = email or "user@gmail.com"
        return self.get_status()

    def disconnect(self) -> Dict[str, Any]:
        self.is_connected = False
        self.access_token = None
        self.user_email = None
        return self.get_status()

    def search_receipts(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """Search user Gmail inbox for receipts."""
        if not self.is_connected or not self.access_token:
            return []

        headers = {"Authorization": f"Bearer {self.access_token}"}
        try:
            resp = requests.get(
                "https://gmail.googleapis.com/gmail/v1/users/me/messages",
                headers=headers,
                params={"q": query, "maxResults": max_results},
                timeout=10
            )
            if resp.status_code == 200:
                messages = resp.json().get("messages", [])
                results = []
                for m in messages:
                    msg_id = m["id"]
                    msg_resp = requests.get(
                        f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}",
                        headers=headers,
                        params={"format": "full"},
                        timeout=10
                    )
                    if msg_resp.status_code == 200:
                        payload = msg_resp.json().get("payload", {})
                        body_text = self._extract_body(payload) or msg_resp.json().get("snippet", "")
                        headers_list = payload.get("headers", [])
                        subject = next((h["value"] for h in headers_list if h["name"].lower() == "subject"), "Receipt Confirmation")
                        sender = next((h["value"] for h in headers_list if h["name"].lower() == "from"), "")
                        results.append({
                            "message_id": msg_id,
                            "subject": subject,
                            "from": sender,
                            "snippet": msg_resp.json().get("snippet", ""),
                            "body": body_text[:2500]
                        })
                return results
        except Exception as e:
            logger.warning(f"Gmail search failed: {e}")
        return []

    def _extract_body(self, payload: dict) -> str:
        mime = payload.get("mimeType", "")
        if mime in ("text/plain", "text/html") and payload.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")
        for part in payload.get("parts", []):
            res = self._extract_body(part)
            if res:
                return res
        return ""
