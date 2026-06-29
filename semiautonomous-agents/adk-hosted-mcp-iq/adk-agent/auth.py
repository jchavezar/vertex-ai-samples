import os
import json
import logging
import threading
from typing import Optional
from dataclasses import dataclass
import msal

logger = logging.getLogger("adk-hosted-mcp.auth")

# Scopes needed for Microsoft Agent 365 Work IQ SharePoint MCP
HOSTED_MCP_SCOPES = [
    "https://agent365.svc.cloud.microsoft/McpServers.SharePoint.All"
]

@dataclass
class AuthState:
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    account: Optional[dict] = None
    expires_at: Optional[float] = None

class MSALAuthManager:
    def __init__(
        self,
        client_id: str,
        tenant_id: str = "common",
        authority: Optional[str] = None,
    ):
        self.client_id = client_id
        self.tenant_id = tenant_id
        self.authority = authority or f"https://login.microsoftonline.com/{tenant_id}"
        self._lock = threading.Lock()
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.cache_path = os.path.join(current_dir, ".hosted_auth.json")
        
        self._app = msal.PublicClientApplication(
            client_id=self.client_id,
            authority=self.authority,
        )
        self._load_state()
        logger.info(f"[Auth] MSAL Auth Manager initialized for tenant: {tenant_id}")

    def _load_state(self) -> None:
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
                    if self._auth_state.refresh_token:
                        self._app.acquire_token_by_refresh_token(
                            self._auth_state.refresh_token,
                            scopes=HOSTED_MCP_SCOPES
                        )
                    logger.info("[Auth] Loaded session from cache")
                    return
                except Exception as e:
                    logger.error(f"[Auth] Failed to load cache: {e}")
            self._auth_state = AuthState()

    def _save_state(self) -> None:
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
        with self._lock:
            return self._auth_state.access_token is not None

    def get_account_info(self) -> Optional[dict]:
        with self._lock:
            return self._auth_state.account

    def start_device_code_flow(self) -> dict:
        flow = self._app.initiate_device_flow(scopes=HOSTED_MCP_SCOPES)
        if "error" in flow:
            raise Exception(f"Device code flow initiation failed: {flow.get('error_description', flow.get('error'))}")
        logger.info(f"[Auth] Initiated device flow: {flow.get('user_code')}")
        return flow

    def complete_device_code_flow(self, flow: dict) -> dict:
        result = self._app.acquire_token_by_device_flow(flow)
        if "error" in result:
            raise Exception(f"Authentication failed: {result.get('error_description', result.get('error'))}")
        
        with self._lock:
            self._auth_state.access_token = result.get("access_token")
            self._auth_state.refresh_token = result.get("refresh_token")
            self._auth_state.account = {
                "username": result.get("id_token_claims", {}).get("preferred_username"),
                "name": result.get("id_token_claims", {}).get("name"),
                "tenant_id": result.get("id_token_claims", {}).get("tid"),
            }
            self._save_state()
            
        logger.info(f"[Auth] Successfully logged in as: {self._auth_state.account.get('username')}")
        return self._auth_state.account

    def get_access_token(self) -> Optional[str]:
        with self._lock:
            if not self._auth_state.access_token:
                return None
            
            # Check silent token acquisition using MSAL accounts cache
            accounts = self._app.get_accounts()
            if accounts:
                result = self._app.acquire_token_silent(
                    scopes=HOSTED_MCP_SCOPES,
                    account=accounts[0]
                )
                if result and "access_token" in result:
                    self._auth_state.access_token = result["access_token"]
                    self._auth_state.refresh_token = result.get("refresh_token", self._auth_state.refresh_token)
                    self._save_state()
                    return result["access_token"]
            
            return self._auth_state.access_token

    def logout(self) -> None:
        with self._lock:
            self._auth_state = AuthState()
            if os.path.exists(self.cache_path):
                try:
                    os.remove(self.cache_path)
                except Exception:
                    pass
            for account in self._app.get_accounts():
                self._app.remove_account(account)
        logger.info("[Auth] Logged out successfully")
