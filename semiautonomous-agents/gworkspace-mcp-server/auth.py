"""
Google OAuth Authentication Manager

Uses authorization code flow with loopback redirect for user authentication.
"""
import os
import time
import logging
import threading
import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional, Dict, Any
from dataclasses import dataclass
import requests

logger = logging.getLogger("gworkspace-mcp.auth")

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
    Uses a manual copy-paste approach for cloud deployment compatibility.
    """

    AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
    REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"  # Manual copy-paste flow

    def __init__(self, client_id: str, client_secret: str = ""):
        self.client_id = client_id
        self.client_secret = client_secret
        self.state = AuthState()
        self._auth_code: Optional[str] = None
        self._lock = threading.Lock()

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
