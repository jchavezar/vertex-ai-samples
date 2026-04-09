"""MSAL client_credentials authentication for Microsoft Graph API."""

import os
import time
import msal
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / "sharepoint_wif_portal" / ".env")

TENANT_ID = os.environ["TENANT_ID"]
CLIENT_ID = os.environ["OAUTH_CLIENT_ID"]
CLIENT_SECRET = os.environ["OAUTH_CLIENT_SECRET"]

_app = None
_token_cache = {"token": None, "expires_at": 0}


def _get_app() -> msal.ConfidentialClientApplication:
    global _app
    if _app is None:
        _app = msal.ConfidentialClientApplication(
            CLIENT_ID,
            authority=f"https://login.microsoftonline.com/{TENANT_ID}",
            client_credential=CLIENT_SECRET,
        )
    return _app


def get_graph_token() -> str:
    """Acquire a Graph API token via client_credentials flow.

    Returns the access_token string. Caches until expiry.
    """
    if _token_cache["token"] and time.time() < _token_cache["expires_at"] - 60:
        return _token_cache["token"]

    app = _get_app()
    result = app.acquire_token_for_client(
        scopes=["https://graph.microsoft.com/.default"]
    )

    if "access_token" not in result:
        raise RuntimeError(f"MSAL auth failed: {result.get('error_description', result)}")

    _token_cache["token"] = result["access_token"]
    _token_cache["expires_at"] = time.time() + result.get("expires_in", 3600)
    return result["access_token"]
