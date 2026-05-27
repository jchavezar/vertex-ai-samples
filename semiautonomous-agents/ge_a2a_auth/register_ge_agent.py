"""Register the A2A agent in Gemini Enterprise via the Custom-A2A path.

Equivalent to what the GE UI "Add agent -> Custom agent via A2A" does, but
scripted so we can wire the Authorization resource in step 2 automatically.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from google.auth import default
from google.auth.transport.requests import Request

HERE = Path(__file__).resolve().parent
load_dotenv(HERE / ".env")

AGENT_ID = "ge_a2a_auth_agent"


def bearer() -> str:
    creds, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(Request())
    return creds.token


def main() -> None:
    project = os.environ["PROJECT_ID"]
    app_id = os.environ["GEMINI_ENTERPRISE_APP_ID"]
    authorization = os.environ["AGENT_AUTHORIZATION"]

    card_path = HERE / "agent_card.json"
    if not card_path.exists():
        raise SystemExit("agent_card.json missing — run deploy.py first.")
    agent_card = card_path.read_text()

    endpoint = (
        "https://discoveryengine.googleapis.com/v1alpha/"
        f"projects/{project}/locations/global/collections/default_collection/"
        f"engines/{app_id}/assistants/default_assistant/agents"
    )

    payload = {
        "displayName": "GE A2A Auth Diagnostic",
        "description": (
            "ADK agent on Agent Runtime, reached via the Custom-A2A path "
            "with OAuth2-cloud-platform bridge auth (proves Agent Runtime "
            "is NOT registered directly)."
        ),
        "a2aAgentDefinition": {"jsonAgentCard": agent_card},
        "authorizationConfig": {"agentAuthorization": authorization},
    }

    headers = {
        "Authorization": f"Bearer {bearer()}",
        "X-Goog-User-Project": project,
        "Content-Type": "application/json",
    }
    r = requests.post(endpoint, headers=headers, json=payload, timeout=30)
    if not r.ok:
        print(f"POST {endpoint}")
        print(f"status={r.status_code}")
        print(r.text)
        r.raise_for_status()
    body = r.json()
    print("✓ Registered:", body.get("name"))
    print(json.dumps(body, indent=2))

    # Auto-share so all users in the org can chat with it.
    agent_resource = body["name"]
    share_url = f"https://discoveryengine.googleapis.com/v1alpha/{agent_resource}:setSharing"
    share_payload = {"sharingConfig": {"dimensionConfigs": [{"name": "ALL_USERS"}]}}
    rs = requests.post(share_url, headers=headers, json=share_payload, timeout=30)
    if rs.ok:
        print("✓ Shared with ALL_USERS")
    else:
        print(f"! Share failed ({rs.status_code}): {rs.text}")


if __name__ == "__main__":
    main()
