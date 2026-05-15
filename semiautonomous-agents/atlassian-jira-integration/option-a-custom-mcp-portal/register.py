"""Register the Jira MCP Portal agent + Atlassian OAuth authorization to
the jira-testing GE engine in vtxdemos.

Usage:
    python register.py auth     # Create the OAuth authorization in DE
    python register.py agent    # Register the agent (with auth wired)
    python register.py share    # Share with ALL_USERS
    python register.py all
"""
import os
import sys
import urllib.parse
import requests
import google.auth
import google.auth.transport.requests
from pathlib import Path

# Lightweight .env loader
_env_files = [
    Path(__file__).resolve().parent / ".env",
    Path(__file__).resolve().parent / "adk_agent" / ".env",
]
for _p in _env_files:
    if _p.exists():
        for line in _p.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

GE_PROJECT_ID = os.environ.get("GE_PROJECT_ID", "vtxdemos")
GE_PROJECT_NUMBER = os.environ.get("GE_PROJECT_NUMBER", "254356041555")
AS_APP = os.environ.get("AS_APP", "jira-testing_1778158449701")
REASONING_ENGINE_RES = os.environ.get(
    "REASONING_ENGINE_RES",
    "projects/254356041555/locations/us-central1/reasoningEngines/1666248848999186432",
)
AUTH_ID = os.environ.get("AGENTSPACE_AUTH_ID", "jira-mcp-portal-auth")
ATLASSIAN_CLIENT_ID = os.environ["ATLASSIAN_CLIENT_ID"]
ATLASSIAN_CLIENT_SECRET = os.environ["ATLASSIAN_CLIENT_SECRET"]

AGENT_DISPLAY_NAME = "Jira MCP Portal"
AGENT_DESCRIPTION = (
    "Query Jira with deep analysis (root cause, duration, JQL date logic, paginated reporting)."
)
AGENT_ICON = "https://fonts.gstatic.com/s/i/short-term/release/googlesymbols/bug_report/default/24px.svg"
TOOL_DESCRIPTION = "Use this agent to search and report on Jira issues."

GE_REDIRECT_URI = "https://vertexaisearch.cloud.google.com/oauth-redirect"
SCOPES = "read:jira-work read:jira-user write:jira-work offline_access"


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


def register_auth() -> bool:
    redirect_uri = urllib.parse.quote(GE_REDIRECT_URI, safe="")
    scope = urllib.parse.quote(SCOPES, safe="")
    auth_uri = (
        "https://auth.atlassian.com/authorize"
        f"?audience=api.atlassian.com"
        f"&client_id={ATLASSIAN_CLIENT_ID}"
        f"&scope={scope}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&prompt=consent"
    )
    token_uri = "https://auth.atlassian.com/oauth/token"

    url = f"{_base_url()}/authorizations?authorizationId={AUTH_ID}"
    payload = {
        "name": f"projects/{GE_PROJECT_NUMBER}/locations/global/authorizations/{AUTH_ID}",
        "serverSideOauth2": {
            "clientId": ATLASSIAN_CLIENT_ID,
            "clientSecret": ATLASSIAN_CLIENT_SECRET,
            "authorizationUri": auth_uri,
            "tokenUri": token_uri,
        },
    }

    print(f"POST {url}")
    resp = requests.post(url, headers=_headers(), json=payload)
    if resp.status_code == 200:
        print(f"Authorization registered: {AUTH_ID}")
        return True
    if resp.status_code == 409:
        print(f"Authorization '{AUTH_ID}' already exists — patching")
        patch_url = f"{_base_url()}/authorizations/{AUTH_ID}?updateMask=serverSideOauth2"
        resp = requests.patch(patch_url, headers=_headers(), json=payload)
        if resp.status_code == 200:
            print("Patched OK")
            return True
    print(f"ERROR ({resp.status_code}): {resp.text}")
    return False


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


def run_all():
    print("== 1/3 OAuth Authorization ==")
    register_auth()
    print("\n== 2/3 Agent Registration ==")
    name = register_agent()
    if name:
        print("\n== 3/3 Share ==")
        share_agent(name)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd == "auth":
        register_auth()
    elif cmd == "agent":
        register_agent()
    elif cmd == "share":
        if len(sys.argv) < 3:
            print("Usage: python register.py share <agent-resource-name>")
            sys.exit(1)
        share_agent(sys.argv[2])
    elif cmd == "all":
        run_all()
    else:
        print("Usage: python register.py [auth|agent|share|all]")
