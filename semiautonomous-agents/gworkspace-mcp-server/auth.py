"""
Google OAuth Authentication Manager

Uses authorization code flow with loopback redirect for user authentication.
Tokens persist in Google Secret Manager so they survive Cloud Run cold starts
and are shared across MCP clients (Claude Code, gemini-cli, etc.).
"""
import os
import time
import json
import logging
import threading
import urllib.parse
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
import requests

logger = logging.getLogger("gworkspace-mcp.auth")

# Optional Secret Manager — only used when GWORKSPACE_SECRET_ID is set
try:
    from google.cloud import secretmanager
    _SM_AVAILABLE = True
except ImportError:
    _SM_AVAILABLE = False

# Google Workspace OAuth scopes
GOOGLE_SCOPES = [
    "openid",
    "email",
    "profile",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/documents.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/photoslibrary.readonly",
]


@dataclass
class AuthState:
    """Holds the current authentication state."""
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[float] = None
    user_info: Optional[Dict[str, Any]] = None


class GoogleAuthManager:
    """
    Manages Google Workspace authentication using authorization code flow.

    Uses a loopback redirect URI (Google's officially supported flow). The user
    opens the auth URL on any machine; after consent Google redirects to
    http://localhost:<port>/?code=... — the page won't load (nothing listens),
    but the user copies the code from the browser URL bar.
    """

    AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
    REDIRECT_URI = "http://localhost:8765/"

    def __init__(self, client_id: str, client_secret: str = ""):
        self.client_id = client_id
        self.client_secret = client_secret
        self.state = AuthState()
        self._auth_code: Optional[str] = None
        self._lock = threading.Lock()

        self._secret_id = os.getenv("GWORKSPACE_SECRET_ID", "")
        self._secret_project = os.getenv("GOOGLE_CLOUD_PROJECT", "")
        self._sm_client = None
        if self._secret_id and self._secret_project and _SM_AVAILABLE:
            try:
                self._sm_client = secretmanager.SecretManagerServiceClient()
                self._load_from_secret()
            except Exception as e:
                logger.warning(f"Secret Manager unavailable: {e}")

    def _secret_name(self) -> str:
        return f"projects/{self._secret_project}/secrets/{self._secret_id}"

    def _load_from_secret(self) -> None:
        try:
            resp = self._sm_client.access_secret_version(
                request={"name": f"{self._secret_name()}/versions/latest"}
            )
            data = json.loads(resp.payload.data.decode("utf-8"))
            self.state.access_token = data.get("access_token")
            self.state.refresh_token = data.get("refresh_token")
            self.state.expires_at = data.get("expires_at")
            self.state.user_info = data.get("user_info")
            logger.info("Loaded tokens from Secret Manager")
        except Exception as e:
            logger.info(f"No existing tokens in Secret Manager: {e}")

    def _save_to_secret(self) -> None:
        if not self._sm_client:
            return
        try:
            payload = json.dumps(asdict(self.state)).encode("utf-8")
            self._sm_client.add_secret_version(
                request={"parent": self._secret_name(), "payload": {"data": payload}}
            )
            logger.info("Persisted tokens to Secret Manager")
        except Exception as e:
            logger.error(f"Failed to persist tokens to Secret Manager: {e}")

    def get_auth_url(self) -> str:
        """Generate the authorization URL for manual auth flow."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.REDIRECT_URI,
            "response_type": "code",
            "scope": " ".join(GOOGLE_SCOPES),
            "access_type": "offline",
            "prompt": "consent",
        }
        return f"{self.AUTH_URL}?{urllib.parse.urlencode(params)}"

    def start_auth_flow(self) -> Dict[str, str]:
        """Start the authorization flow and return the auth URL."""
        auth_url = self.get_auth_url()
        return {
            "auth_url": auth_url,
            "instructions": "Open the URL, sign in, and copy the authorization code"
        }

    def exchange_code(self, auth_code: str) -> bool:
        """Exchange authorization code for tokens."""
        try:
            data = {
                "client_id": self.client_id,
                "code": auth_code,
                "grant_type": "authorization_code",
                "redirect_uri": self.REDIRECT_URI,
            }
            if self.client_secret:
                data["client_secret"] = self.client_secret

            response = requests.post(self.TOKEN_URL, data=data)
            response.raise_for_status()
            token_data = response.json()

            with self._lock:
                self.state.access_token = token_data["access_token"]
                self.state.refresh_token = token_data.get("refresh_token")
                self.state.expires_at = time.time() + token_data.get("expires_in", 3600)
                self._fetch_user_info()

            self._save_to_secret()
            logger.info("Authentication successful")
            return True

        except Exception as e:
            logger.error(f"Token exchange failed: {e}")
            return False

    def _fetch_user_info(self):
        """Fetch user info after successful authentication."""
        if not self.state.access_token:
            return

        try:
            response = requests.get(
                self.USERINFO_URL,
                headers={"Authorization": f"Bearer {self.state.access_token}"}
            )
            response.raise_for_status()
            self.state.user_info = response.json()
        except Exception as e:
            logger.error(f"Failed to fetch user info: {e}")

    def is_authenticated(self) -> bool:
        """Check if user is authenticated with valid token."""
        with self._lock:
            if not self.state.access_token:
                return False
            if self.state.expires_at and time.time() > self.state.expires_at:
                return self._refresh_token()
            return True

    def _refresh_token(self) -> bool:
        """Refresh the access token using refresh token."""
        if not self.state.refresh_token:
            return False

        try:
            data = {
                "client_id": self.client_id,
                "refresh_token": self.state.refresh_token,
                "grant_type": "refresh_token",
            }
            if self.client_secret:
                data["client_secret"] = self.client_secret

            response = requests.post(self.TOKEN_URL, data=data)
            response.raise_for_status()
            token_data = response.json()

            self.state.access_token = token_data["access_token"]
            self.state.expires_at = time.time() + token_data.get("expires_in", 3600)
            self._save_to_secret()
            logger.info("Token refreshed successfully")
            return True

        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return False

    def get_access_token(self) -> Optional[str]:
        """Get current access token, refreshing if needed."""
        if self.is_authenticated():
            return self.state.access_token
        return None

    def get_user_info(self) -> Dict[str, Any]:
        """Get cached user info."""
        return self.state.user_info or {}

    def get_token_expiry(self) -> str:
        """Get token expiry time as string."""
        if self.state.expires_at:
            from datetime import datetime
            return datetime.fromtimestamp(self.state.expires_at).strftime("%Y-%m-%d %H:%M:%S")
        return "Unknown"

    def logout(self):
        """Clear all authentication state."""
        with self._lock:
            self.state = AuthState()

    # Legacy methods for compatibility
    def start_device_flow(self) -> Dict[str, str]:
        """Start auth flow (returns auth URL instead of device code)."""
        return self.start_auth_flow()

    def complete_device_flow(self) -> bool:
        """Check if auth completed."""
        return self.is_authenticated()
