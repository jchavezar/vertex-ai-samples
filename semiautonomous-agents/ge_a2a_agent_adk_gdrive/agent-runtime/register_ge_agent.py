"""Register the AE-hosted A2A agent in Gemini Enterprise via Custom-A2A.

Uses the `agent_card.json` produced by deploy.py and points GE at the
canonical AE A2A URL. Wires the Authorization resource from
create_authorization.py.

NOTE: GE's harpoon proxy requires `preferredTransport: "JSONRPC"`. AE's
A2aAgent advertises `HTTP+JSON` (its validator rejects JSONRPC). As a
result this registration is accepted but GE chat will return a
synthetic 404 without ever issuing a request — see README "Known
limitations".
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
        "displayName": "GE A2A Auth Diagnostic (Agent Runtime)",
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
    print("Registered:", body.get("name"))
    print(json.dumps(body, indent=2))

    agent_resource = body["name"]
    share_url = f"https://discoveryengine.googleapis.com/v1alpha/{agent_resource}:setSharing"
    share_payload = {"sharingConfig": {"dimensionConfigs": [{"name": "ALL_USERS"}]}}
    rs = requests.post(share_url, headers=headers, json=share_payload, timeout=30)
    if rs.ok:
        print("Shared with ALL_USERS")
    else:
        print(f"Share failed ({rs.status_code}): {rs.text}")


if __name__ == "__main__":
    main()
