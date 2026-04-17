"""Secret Manager helpers for Amex statement automation."""

import json
import logging
import os
import time
from typing import Any

import requests
from google.cloud import secretmanager

logger = logging.getLogger("amex-job.secrets")

PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "vtxdemos")
GWORKSPACE_SECRET_ID = os.environ.get("GWORKSPACE_SECRET_ID", "gworkspace-mcp-tokens")


def _access_secret(secret_id: str) -> str:
    """Access the latest version of a secret. Never logs the value."""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    logger.info(json.dumps({"event": "secret_accessed", "secret": secret_id}))
    return response.payload.data.decode("utf-8")


def get_amex_credentials() -> dict[str, str]:
    """Return {"username": ..., "code": ...} from the `amx` secret."""
    raw = _access_secret("amx")
    creds = json.loads(raw)
    if "username" not in creds or "code" not in creds:
        raise ValueError("Secret 'amx' missing required keys: username, code")
    logger.info(json.dumps({"event": "amex_credentials_loaded"}))
    return creds


def get_gmail_access_token() -> str:
    """Get a valid Gmail access token from the gworkspace-mcp-tokens secret.

    Reuses the existing OAuth tokens from the gworkspace MCP server.
    Refreshes the token if expired.
    """
    raw = _access_secret(GWORKSPACE_SECRET_ID)
    tokens = json.loads(raw)

    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    expires_at = tokens.get("expires_at", 0)

    # If token is still valid, return it
    if access_token and time.time() < expires_at - 60:
        logger.info(json.dumps({"event": "gmail_token_valid"}))
        return access_token

    # Token expired — refresh it
    if not refresh_token:
        raise ValueError("No refresh token in gworkspace-mcp-tokens")

    # We need the OAuth client_id to refresh. Check env or use the one from gworkspace server.
    client_id = os.environ.get("GOOGLE_CLIENT_ID", "")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "")

    if not client_id:
        raise ValueError("GOOGLE_CLIENT_ID env var required for token refresh")

    data = {
        "client_id": client_id,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    if client_secret:
        data["client_secret"] = client_secret

    resp = requests.post("https://oauth2.googleapis.com/token", data=data)
    resp.raise_for_status()
    token_data = resp.json()

    logger.info(json.dumps({"event": "gmail_token_refreshed"}))
    return token_data["access_token"]
