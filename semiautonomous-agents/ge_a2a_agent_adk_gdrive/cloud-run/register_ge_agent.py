"""Register the Cloud Run agent in Gemini Enterprise via Custom-A2A.

Creates the GE agent if it doesn't exist, otherwise PATCHes it. The agent
card uses `preferredTransport: "JSONRPC"` — GE's harpoon proxy silently
rejects any other transport (it returns a synthetic 404 with zero upstream
egress).

Authorization is wired via `authorizationConfig.agentAuthorization`,
pointing at the resource created by create_authorization.py.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv, set_key
from google.auth import default
from google.auth.transport.requests import Request

HERE = Path(__file__).resolve().parent
ENV_FILE = HERE / ".env"
load_dotenv(ENV_FILE)


def bearer() -> str:
    creds, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(Request())
    return creds.token


def _build_card(cr_url: str) -> str:
    card = {
        "name": "ge_cr_a2a_agent",
        "description": (
            "Diagnostic agent demonstrating end-to-end user OAuth delegation: "
            "Gemini Enterprise -> Custom A2A -> Google Drive (as the user)."
        ),
        "url": cr_url,
        "version": "1.0.0",
        "protocolVersion": "0.3.0",
        "preferredTransport": "JSONRPC",
        "defaultInputModes": ["text/plain"],
        "defaultOutputModes": ["text/plain"],
        "capabilities": {"streaming": False},
        "supportsAuthenticatedExtendedCard": True,
        "skills": [
            {
                "id": "whoami",
                "name": "Caller identity (from user OAuth token)",
                "description": (
                    "Echo the email + sub claims of the OAuth bearer GE "
                    "forwarded. Proves user identity reaches the container."
                ),
                "tags": ["diagnostic", "identity"],
                "examples": ["whoami", "who am i?"],
            },
            {
                "id": "drive_search_files",
                "name": "Search the caller's Google Drive (as the user)",
                "description": (
                    "Calls drive.files.list using the user's OAuth token."
                ),
                "tags": ["drive", "delegation"],
                "examples": [
                    "list my Drive files",
                    "find my Drive PDFs",
                    "show my recent docs",
                ],
            },
        ],
    }
    return json.dumps(card)


def main() -> None:
    project = os.environ["PROJECT_ID"]
    app_id = os.environ["GEMINI_ENTERPRISE_APP_ID"]
    authorization = os.environ["AGENT_AUTHORIZATION"]
    cr_url = os.environ["A2A_URL_CR"]
    existing_agent_id = os.environ.get("GE_AGENT_ID_CR", "").strip()

    card_json = _build_card(cr_url)
    base = (
        "https://discoveryengine.googleapis.com/v1alpha/"
        f"projects/{project}/locations/global/collections/default_collection/"
        f"engines/{app_id}/assistants/default_assistant/agents"
    )
    headers = {
        "Authorization": f"Bearer {bearer()}",
        "X-Goog-User-Project": project,
        "Content-Type": "application/json",
    }
    payload = {
        "displayName": "GE A2A Auth + Drive (Cloud Run)",
        "description": (
            "User OAuth bearer from GE consent -> Custom A2A -> Cloud Run "
            "agent -> Drive API (as the user). True delegation."
        ),
        "a2aAgentDefinition": {"jsonAgentCard": card_json},
        "authorizationConfig": {"agentAuthorization": authorization},
    }

    if existing_agent_id:
        patch_url = (
            f"{base}/{existing_agent_id}"
            "?updateMask=displayName,description,a2aAgentDefinition,authorizationConfig"
        )
        r = requests.patch(patch_url, headers=headers, json=payload, timeout=30)
        if not r.ok:
            print(f"PATCH status={r.status_code}\n{r.text}")
            r.raise_for_status()
        body = r.json()
        print("PATCHed agent:", body.get("name"))
    else:
        r = requests.post(base, headers=headers, json=payload, timeout=30)
        if not r.ok:
            print(f"POST status={r.status_code}\n{r.text}")
            r.raise_for_status()
        body = r.json()
        print("Created agent:", body.get("name"))
        new_id = body["name"].rsplit("/", 1)[1]
        set_key(str(ENV_FILE), "GE_AGENT_ID_CR", new_id)
        print(f"Wrote GE_AGENT_ID_CR={new_id} to {ENV_FILE.name}")

    print(json.dumps(body, indent=2))


if __name__ == "__main__":
    main()
