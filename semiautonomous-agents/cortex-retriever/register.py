"""
Register Cortex Retriever to Gemini Enterprise (Agentspace).

Three steps consolidated into one script:
    uv run python register.py auth     # Register OAuth authorization
    uv run python register.py agent    # Register agent to Agentspace
    uv run python register.py share    # Share with ALL_USERS
    uv run python register.py all      # All three in sequence
"""
import os
import sys
import requests
import google.auth
import google.auth.transport.requests
from dotenv import load_dotenv

load_dotenv()

# Agentspace lives in the GE project (may differ from agent's project)
GE_PROJECT_ID = os.environ.get("GE_PROJECT_ID") or os.environ.get("PROJECT_ID", "")
GE_PROJECT_NUMBER = os.environ.get("GE_PROJECT_NUMBER") or os.environ.get("PROJECT_NUMBER", "")
AS_APP = os.environ.get("AS_APP", "")
REASONING_ENGINE_RES = os.environ.get("REASONING_ENGINE_RES", "")
AUTH_ID = os.environ.get("AUTH_ID", "")
TENANT_ID = os.environ.get("TENANT_ID", "")
OAUTH_CLIENT_ID = os.environ.get("OAUTH_CLIENT_ID", "")
OAUTH_CLIENT_SECRET = os.environ.get("OAUTH_CLIENT_SECRET", "")
AGENT_DISPLAY_NAME = os.environ.get("AGENT_DISPLAY_NAME", "Cortex Retriever")
AGENT_DESCRIPTION = os.environ.get("AGENT_DESCRIPTION", "Search SharePoint documents and the public web")
AGENT_ICON = os.environ.get("AGENT_ICON", "https://fonts.gstatic.com/s/i/short-term/release/googlesymbols/travel_explore/default/24px.svg")
TOOL_DESCRIPTION = os.environ.get("TOOL_DESCRIPTION", "Use this agent to search SharePoint documents and compare with public web information")


def _get_headers() -> dict:
    credentials, _ = google.auth.default()
    credentials.refresh(google.auth.transport.requests.Request())
    return {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json",
        "x-goog-user-project": GE_PROJECT_ID,
    }


def _base_url() -> str:
    return (
        f"https://discoveryengine.googleapis.com/v1alpha/"
        f"projects/{GE_PROJECT_NUMBER}/locations/global"
    )


def register_auth():
    """Register OAuth authorization resource in Discovery Engine."""
    if not all([GE_PROJECT_NUMBER, AUTH_ID, OAUTH_CLIENT_ID, OAUTH_CLIENT_SECRET, TENANT_ID]):
        print("ERROR: GE_PROJECT_NUMBER, AUTH_ID, OAUTH_CLIENT_ID, OAUTH_CLIENT_SECRET, TENANT_ID required")
        return False

    redirect_uri = "https%3A%2F%2Fvertexaisearch.cloud.google.com%2Foauth-redirect"
    scopes = f"openid%20profile%20email%20offline_access%20api%3A%2F%2F{OAUTH_CLIENT_ID}%2Fuser_impersonation"
    auth_uri = (
        f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize"
        f"?response_type=code&client_id={OAUTH_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}&scope={scopes}&prompt=consent"
    )
    token_uri = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"

    url = f"{_base_url()}/authorizations?authorizationId={AUTH_ID}"
    payload = {
        "name": f"projects/{GE_PROJECT_NUMBER}/locations/global/authorizations/{AUTH_ID}",
        "serverSideOauth2": {
            "clientId": OAUTH_CLIENT_ID,
            "clientSecret": OAUTH_CLIENT_SECRET,
            "authorizationUri": auth_uri,
            "tokenUri": token_uri,
        },
    }

    print(f"Registering authorization: {AUTH_ID}")
    resp = requests.post(url, headers=_get_headers(), json=payload)

    if resp.status_code == 200:
        print(f"Authorization registered: projects/{GE_PROJECT_NUMBER}/locations/global/authorizations/{AUTH_ID}")
        return True
    elif resp.status_code == 409:
        print(f"Authorization '{AUTH_ID}' already exists (409) — skipping")
        return True
    else:
        print(f"ERROR ({resp.status_code}): {resp.text}")
        return False


def register_agent() -> str | None:
    """Register agent to Agentspace and return the agent resource name."""
    if not all([GE_PROJECT_NUMBER, AS_APP, REASONING_ENGINE_RES]):
        print("ERROR: GE_PROJECT_NUMBER, AS_APP, REASONING_ENGINE_RES required")
        return None

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
    }

    if AUTH_ID:
        payload["authorization_config"] = {
            "tool_authorizations": [
                f"projects/{GE_PROJECT_NUMBER}/locations/global/authorizations/{AUTH_ID}"
            ]
        }

    print(f"Registering agent: {AGENT_DISPLAY_NAME}")
    resp = requests.post(url, headers=_get_headers(), json=payload)

    if resp.status_code == 200:
        agent_name = resp.json().get("name", "")
        print(f"Agent registered: {agent_name}")
        return agent_name
    else:
        print(f"ERROR ({resp.status_code}): {resp.text}")
        return None


def share_agent(agent_name: str):
    """Share agent with all Agentspace users."""
    if not agent_name:
        print("ERROR: agent_name required")
        return False

    url = f"https://discoveryengine.googleapis.com/v1alpha/{agent_name}?updateMask=sharingConfig"
    payload = {"sharingConfig": {"scope": "ALL_USERS"}}

    print(f"Sharing with ALL_USERS...")
    resp = requests.patch(url, headers=_get_headers(), json=payload)

    if resp.status_code == 200:
        print("Shared with ALL_USERS")
        return True
    else:
        print(f"WARNING: sharing failed ({resp.status_code}): {resp.text}")
        return False


def run_all():
    print("=" * 50)
    print("Step 1/3: Register OAuth Authorization")
    print("=" * 50)
    register_auth()

    print()
    print("=" * 50)
    print("Step 2/3: Register Agent to Agentspace")
    print("=" * 50)
    agent_name = register_agent()

    if agent_name:
        print()
        print("=" * 50)
        print("Step 3/3: Share with ALL_USERS")
        print("=" * 50)
        share_agent(agent_name)

    print()
    print("=" * 50)
    print("Done. Agent is now available in Gemini Enterprise.")
    print("=" * 50)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"

    if cmd == "auth":
        register_auth()
    elif cmd == "agent":
        name = register_agent()
        if name:
            print(f"\nTo share: uv run python register.py share {name}")
    elif cmd == "share":
        agent_name = sys.argv[2] if len(sys.argv) > 2 else None
        if not agent_name:
            print("Usage: python register.py share <agent-resource-name>")
            sys.exit(1)
        share_agent(agent_name)
    elif cmd == "all":
        run_all()
    else:
        print("Usage: python register.py [auth|agent|share|all]")
