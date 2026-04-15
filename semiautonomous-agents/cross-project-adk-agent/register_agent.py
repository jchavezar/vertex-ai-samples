"""
Register the Agent Engine (in sharepoint-wif-agent) to Gemini Enterprise Agentspace (in vtxdemos).

This is the cross-project link: the agent runs in Project A but is accessible in Project B's Agentspace.

Prerequisites:
    1. Agent deployed via deploy.py (REASONING_ENGINE_RES set in .env)
    2. Agentspace app created in vtxdemos (AS_APP set in .env)
    3. IAM: vtxdemos service account needs roles/aiplatform.user on sharepoint-wif-agent

Usage:
    uv run python register_agent.py
"""
import json
import os
import requests
import google.auth
import google.auth.transport.requests
from dotenv import load_dotenv

load_dotenv()

# Project B: Gemini Enterprise / Agentspace
GE_PROJECT_ID = os.environ.get("GE_PROJECT_ID", "vtxdemos")
GE_PROJECT_NUMBER = os.environ["GE_PROJECT_NUMBER"]
AS_APP = os.environ.get("AS_APP", "")

# Agent Engine resource from deploy.py
REASONING_ENGINE_RES = os.environ.get("REASONING_ENGINE_RES", "")

# Agent metadata
AGENT_DISPLAY_NAME = os.environ.get("AGENT_DISPLAY_NAME", "Cross-Project Assistant")
AGENT_DESCRIPTION = os.environ.get(
    "AGENT_DESCRIPTION",
    "Simple ADK agent deployed in sharepoint-wif-agent, registered in vtxdemos Gemini Enterprise",
)


def register():
    """Register agent in Gemini Enterprise Agentspace."""
    if not REASONING_ENGINE_RES:
        print("ERROR: REASONING_ENGINE_RES not set. Run deploy.py first.")
        return
    if not AS_APP:
        print("ERROR: AS_APP not set. Set your Agentspace app ID in .env.")
        return

    print(f"""
=====================================
Registering Agent in Gemini Enterprise
=====================================
Agent Engine:    {REASONING_ENGINE_RES}
Agentspace App:  {AS_APP}
GE Project:      {GE_PROJECT_ID}
Display Name:    {AGENT_DISPLAY_NAME}
=====================================
""")

    # Get access token
    credentials, _ = google.auth.default()
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    access_token = credentials.token

    # Discovery Engine API to register agent in Agentspace
    api_url = (
        f"https://discoveryengine.googleapis.com/v1alpha/"
        f"projects/{GE_PROJECT_NUMBER}/locations/global/"
        f"collections/default_collection/engines/{AS_APP}/"
        f"assistants/default_assistant/agents"
    )

    payload = {
        "displayName": AGENT_DISPLAY_NAME,
        "description": AGENT_DESCRIPTION,
        "icon": {
            "uri": "https://fonts.gstatic.com/s/i/short-term/release/googlesymbols/globe/default/24px.svg"
        },
        "adk_agent_definition": {
            "tool_settings": {
                "tool_description": "Use this agent to answer questions. It is a helpful assistant."
            },
            "provisioned_reasoning_engine": {
                "reasoning_engine": REASONING_ENGINE_RES,
            },
        },
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "x-goog-user-project": GE_PROJECT_ID,
    }

    response = requests.post(api_url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        result = response.json()
        agent_name = result.get("name", "")
        print(f"""
=====================================
Registration Complete!
=====================================
Agent Name: {agent_name}
Display:    {result.get('displayName', 'N/A')}
=====================================
""")

        # Share agent with all users
        share_agent(agent_name, headers)

        print(f"""
The agent is now available in Gemini Enterprise at:
  Project: {GE_PROJECT_ID}
  Agentspace: {AS_APP}
""")
    else:
        print(f"ERROR ({response.status_code}): {response.text}")

    return response.json()


def share_agent(agent_name: str, headers: dict):
    """Share the agent with all Agentspace users."""
    share_url = (
        f"https://discoveryengine.googleapis.com/v1alpha/"
        f"{agent_name}?updateMask=sharingConfig"
    )

    share_payload = {
        "sharingConfig": {
            "scope": "ALL_USERS"
        }
    }

    resp = requests.patch(share_url, headers=headers, data=json.dumps(share_payload))

    if resp.status_code == 200:
        print("Shared with ALL_USERS.")
    else:
        print(f"WARNING: sharing failed ({resp.status_code}): {resp.text}")
        print("You can share manually -- see docs/04-REGISTER-GEMINI-ENTERPRISE.md")


if __name__ == "__main__":
    register()
