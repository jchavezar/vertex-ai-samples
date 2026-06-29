import os
import sys
import urllib.parse
import requests
import google.auth
import google.auth.transport.requests
from pathlib import Path

# Load environment from parent directory if needed
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

GE_PROJECT_ID = "vtxdemos"
GE_PROJECT_NUMBER = "254356041555"
AS_APP = "sp-mcp-hosted"  # The engine to attach to

REASONING_ENGINE_ID = os.environ.get("REASONING_ENGINE_ID")
if not REASONING_ENGINE_ID:
    print("ERROR: REASONING_ENGINE_ID environment variable is required.")
    sys.exit(1)

REASONING_ENGINE_RES = f"projects/{GE_PROJECT_NUMBER}/locations/us-central1/reasoningEngines/{REASONING_ENGINE_ID}"
AUTH_ID = "sharepointauth_hosted"  # Unique ID for hosted MCP auth config
CLIENT_ID = "030b6aac-63d1-40e9-8d80-7ce928b839b8"
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

TENANT_ID = "de46a3fd-0d68-4b25-8343-6eb5d71afce9"
AUTH_URI = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize"
TOKEN_URI = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"

# Scopes needed for Agent 365 hosted MCP server
SCOPES = "openid profile email offline_access https://agent365.svc.cloud.microsoft/McpServers.SharePoint.All"
GE_REDIRECT_URI = "https://vertexaisearch.cloud.google.com/oauth-redirect"

AGENT_DISPLAY_NAME = "SharePoint Hosted Explorer Agent"
AGENT_DESCRIPTION = "Search and access SharePoint documents via Microsoft Hosted Work IQ MCP with citations."
AGENT_ICON = "https://fonts.gstatic.com/s/i/short-term/release/googlesymbols/folder/default/24px.svg"
TOOL_DESCRIPTION = "Use this agent to search SharePoint content via Work IQ."

def register_auth() -> bool:
    redirect_uri = urllib.parse.quote(GE_REDIRECT_URI, safe="")
    scope = urllib.parse.quote(SCOPES, safe="")
    
    full_auth_uri = (
        f"{AUTH_URI}"
        f"?client_id={CLIENT_ID}"
        f"&scope={scope}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&prompt=consent"
    )

    url = f"{_base_url()}/authorizations?authorizationId={AUTH_ID}"
    payload = {
        "name": f"projects/{GE_PROJECT_NUMBER}/locations/global/authorizations/{AUTH_ID}",
        "serverSideOauth2": {
            "clientId": CLIENT_ID,
            "clientSecret": CLIENT_SECRET,
            "authorizationUri": full_auth_uri,
            "tokenUri": TOKEN_URI,
        },
    }

    print(f"POST {url}")
    resp = requests.post(url, headers=_headers(), json=payload)
    if resp.status_code == 200:
        print(f"Authorization registered: {AUTH_ID}")
        return True
    if resp.status_code == 409:
        print(f"Authorization '{AUTH_ID}' already exists")
        return True
    print(f"ERROR ({resp.status_code}): {resp.text}")
    return False

def _headers() -> dict:
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(google.auth.transport.requests.Request())
    return {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "x-goog-user-project": GE_PROJECT_ID,
    }

def _base_url() -> str:
    return (
        f"https://discoveryengine.googleapis.com/v1alpha/"
        f"projects/{GE_PROJECT_NUMBER}/locations/global"
    )

def register_agent() -> str | None:
    url = (
        f"{_base_url()}/collections/default_collection/"
        f"engines/{AS_APP}/assistants/default_assistant/agents"
    )
    payload = {
        "displayName": AGENT_DISPLAY_NAME,
        "description": AGENT_DESCRIPTION,
        "icon": {"uri": AGENT_ICON},
        "adk_agent_definition": {
            "tool_settings": {"tool_description": TOOL_DESCRIPTION},
            "provisioned_reasoning_engine": {"reasoning_engine": REASONING_ENGINE_RES},
        },
        "authorization_config": {
            "tool_authorizations": [
                f"projects/{GE_PROJECT_NUMBER}/locations/global/authorizations/{AUTH_ID}"
            ]
        },
    }
    print(f"POST {url}")
    resp = requests.post(url, headers=_headers(), json=payload)
    if resp.status_code == 200:
        name = resp.json().get("name", "")
        print(f"Agent registered: {name}")
        return name
    print(f"ERROR ({resp.status_code}): {resp.text}")
    return None

def share_agent(agent_name: str) -> bool:
    url = f"https://discoveryengine.googleapis.com/v1alpha/{agent_name}?updateMask=sharingConfig"
    payload = {"sharingConfig": {"scope": "ALL_USERS"}}
    resp = requests.patch(url, headers=_headers(), json=payload)
    if resp.status_code == 200:
        print("Shared with ALL_USERS")
        return True
    print(f"WARNING: sharing failed ({resp.status_code}): {resp.text}")
    return False

if __name__ == "__main__":
    print(f"Registering agent for Reasoning Engine: {REASONING_ENGINE_ID}")
    print("== 1/3 OAuth Authorization ==")
    if register_auth():
        print("\n== 2/3 Agent Registration ==")
        name = register_agent()
        if name:
            print("\n== 3/3 Share ==")
            share_agent(name)
