"""
Microsoft 365 Authentication Module
Uses MSAL with device code flow for delegated (user) authentication.
"""
import os
import json
import logging
import threading
from typing import Optional
from dataclasses import dataclass
from cryptography.fernet import Fernet
import msal

logger = logging.getLogger("ms365-mcp.auth")

# Microsoft Graph scopes for delegated access
GRAPH_SCOPES = [
    "User.Read",
    "Sites.ReadWrite.All",
    "Files.ReadWrite.All",
    "Mail.ReadWrite",
    "Calendars.ReadWrite",
    "Team.ReadBasic.All",
    "Channel.ReadBasic.All",
    "Chat.ReadWrite",
    "Application.ReadWrite.All",
    "Directory.ReadWrite.All",
]


@dataclass
class AuthState:
    """Holds the current authentication state."""
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    account: Optional[dict] = None
    expires_at: Optional[float] = None


class MSALAuthManager:
    """
    Manages Microsoft 365 authentication using MSAL device code flow.
    Tokens are cached in-memory with optional encryption.
    """

    def __init__(
        self,
        client_id: str,
        tenant_id: str = "common",
        authority: Optional[str] = None,
    ):
        self.client_id = client_id
        self.tenant_id = tenant_id
        self.authority = authority or f"https://login.microsoftonline.com/{tenant_id}"
        # Thread-safe token cache
        self._lock = threading.Lock()
        
        # Determine path relative to script directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.cache_path = os.path.join(current_dir, ".ms365_auth.json")
        
        # Generate encryption key for token storage (per-instance)
        self._encryption_key = Fernet.generate_key()
        self._cipher = Fernet(self._encryption_key)

        # Initialize MSAL public client application
        self._app = msal.PublicClientApplication(
            client_id=self.client_id,
            authority=self.authority,
        )

        self._load_state()
        logger.info(f"[Auth] Initialized MSAL for tenant: {tenant_id}")

    def _load_state(self) -> None:
        """Load authentication state from local cache if available."""
        with self._lock:
            if os.path.exists(self.cache_path):
                try:
                    with open(self.cache_path, "r") as f:
                        data = json.load(f)
                    self._auth_state = AuthState(
                        access_token=data.get("access_token"),
                        refresh_token=data.get("refresh_token"),
                        account=data.get("account"),
                        expires_at=data.get("expires_at")
                    )
                    # Load accounts into MSAL's in-memory cache using our tokens
                    if self._auth_state.refresh_token:
                        # Feed the refresh token back into MSAL app
                        self._app.acquire_token_by_refresh_token(
                            self._auth_state.refresh_token,
                            scopes=GRAPH_SCOPES
                        )
                    logger.info("[Auth] Successfully loaded active session from cache")
                    return
                except Exception as e:
                    logger.error(f"[Auth] Failed to load cache: {e}")
            self._auth_state = AuthState()

    def _save_state(self) -> None:
        """Save authentication state to local cache."""
        try:
            os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
            with open(self.cache_path, "w") as f:
                json.dump({
                    "access_token": self._auth_state.access_token,
                    "refresh_token": self._auth_state.refresh_token,
                    "account": self._auth_state.account,
                    "expires_at": self._auth_state.expires_at
                }, f, indent=2)
        except Exception as e:
            logger.error(f"[Auth] Failed to save cache: {e}")

    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated."""
        with self._lock:
            return self._auth_state.access_token is not None

    def get_account_info(self) -> Optional[dict]:
        """Get current authenticated account info."""
        with self._lock:
            return self._auth_state.account

    def start_device_code_flow(self) -> dict:
        """
        Start device code flow authentication.
        Returns dict with 'user_code', 'verification_uri', and 'message'.
        """
        flow = self._app.initiate_device_flow(scopes=GRAPH_SCOPES)

        if "error" in flow:
            raise Exception(f"Device code flow failed: {flow.get('error_description', flow.get('error'))}")

        logger.info(f"[Auth] Device code flow started. Code: {flow.get('user_code')}")
        return flow

    def complete_device_code_flow(self, flow: dict) -> dict:
        """
        Complete device code flow after user has authenticated.
        Returns account info on success.
        """
        result = self._app.acquire_token_by_device_flow(flow)

        if "error" in result:
            raise Exception(f"Authentication failed: {result.get('error_description', result.get('error'))}")

        # Store tokens securely
        with self._lock:
            self._auth_state.access_token = result.get("access_token")
            self._auth_state.refresh_token = result.get("refresh_token")
            self._auth_state.account = {
                "username": result.get("id_token_claims", {}).get("preferred_username"),
                "name": result.get("id_token_claims", {}).get("name"),
                "tenant_id": result.get("id_token_claims", {}).get("tid"),
            }
            self._save_state()

        logger.info(f"[Auth] Authenticated as: {self._auth_state.account.get('username')}")
        return self._auth_state.account

    def get_access_token(self) -> Optional[str]:
        """
        Get current access token, refreshing if needed.
        Returns None if not authenticated.
        """
        with self._lock:
            if not self._auth_state.access_token:
                return None

            # Try to get token silently (will use cached/refresh token)
            accounts = self._app.get_accounts()
            if accounts:
                result = self._app.acquire_token_silent(
                    scopes=GRAPH_SCOPES,
                    account=accounts[0]
                )
                if result and "access_token" in result:
                    self._auth_state.access_token = result["access_token"]
                    self._auth_state.refresh_token = result.get("refresh_token", self._auth_state.refresh_token)
                    self._save_state()
                    return result["access_token"]

            return self._auth_state.access_token

    def logout(self) -> None:
        """Clear all cached tokens and authentication state."""
        with self._lock:
            self._auth_state = AuthState()
            # Clear cache file
            if os.path.exists(self.cache_path):
                try:
                    os.remove(self.cache_path)
                except Exception:
                    pass
            # Clear MSAL cache
            for account in self._app.get_accounts():
                self._app.remove_account(account)

        logger.info("[Auth] Logged out and cleared tokens")


# Global auth manager instance (initialized lazily)
_auth_manager: Optional[MSALAuthManager] = None
_pending_flow: Optional[dict] = None


def get_auth_manager() -> MSALAuthManager:
    """Get or create the global auth manager."""
    global _auth_manager

    if _auth_manager is None:
        # Get client ID from environment or Secret Manager
        client_id = os.environ.get("MS365_CLIENT_ID")
        tenant_id = os.environ.get("MS365_TENANT_ID", "common")

        if not client_id:
            raise ValueError(
                "MS365_CLIENT_ID environment variable is required. "
                "Set it to your Azure AD application (client) ID."
            )

        _auth_manager = MSALAuthManager(
            client_id=client_id,
            tenant_id=tenant_id,
        )

    return _auth_manager


def get_pending_flow() -> Optional[dict]:
    """Get pending device code flow (if any)."""
    global _pending_flow
    return _pending_flow


def set_pending_flow(flow: Optional[dict]) -> None:
    """Set pending device code flow."""
    global _pending_flow
    _pending_flow = flow
