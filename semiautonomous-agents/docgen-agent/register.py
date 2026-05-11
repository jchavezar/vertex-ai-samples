"""Register docgen-agent in Gemini Enterprise (Discovery Engine v1alpha).

Usage:
    cd semiautonomous-agents/docgen-agent
    uv run python register.py            # register + share with ALL_USERS
    uv run python register.py agent      # register only (no sharing change)
    uv run python register.py share <agent-resource-name>   # share existing

Reads from .env:
    GE_PROJECT_ID            project that owns the GE app (vtxdemos)
    GE_PROJECT_NUMBER        numeric project number for the v1alpha URL
    GE_ENGINE_ID             GE engine ID (default jira-testing_1778158449701)
    AGENT_ENGINE_RESOURCE    full Vertex AI ReasoningEngine resource name
"""
from __future__ import annotations

import os
import sys

import google.auth
import google.auth.transport.requests
import requests
from dotenv import load_dotenv

load_dotenv()

GE_PROJECT_ID = os.environ["GE_PROJECT_ID"]
GE_PROJECT_NUMBER = os.environ["GE_PROJECT_NUMBER"]
GE_ENGINE_ID = os.environ.get("GE_ENGINE_ID", "jira-testing_1778158449701")
AGENT_ENGINE_RESOURCE = os.environ["AGENT_ENGINE_RESOURCE"]

AGENT_DISPLAY_NAME = os.environ.get("AGENT_DISPLAY_NAME", "Doc Gen")
AGENT_DESCRIPTION = os.environ.get(
    "AGENT_DESCRIPTION",
    "Researches a topic with Google Search and generates a downloadable PDF report.",
)
TOOL_DESCRIPTION = os.environ.get(
    "TOOL_DESCRIPTION",
    "Use this agent when the user wants a researched summary AND a downloadable PDF "
    "report. It uses Google Search for grounding and emits a PDF artifact that "
    "appears as a download chip in the chat.",
)
AGENT_ICON = os.environ.get(
    "AGENT_ICON",
    "https://fonts.gstatic.com/s/i/short-term/release/googlesymbols/picture_as_pdf/default/24px.svg",
)


def _headers() -> dict:
    creds, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    creds.refresh(google.auth.transport.requests.Request())
    return {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "x-goog-user-project": GE_PROJECT_ID,
    }


def _base() -> str:
    return f"https://discoveryengine.googleapis.com/v1alpha/projects/{GE_PROJECT_NUMBER}/locations/global"


def register_agent() -> str | None:
    url = (
        f"{_base()}/collections/default_collection/engines/{GE_ENGINE_ID}"
        "/assistants/default_assistant/agents"
    )
    payload = {
        "displayName": AGENT_DISPLAY_NAME,
        "description": AGENT_DESCRIPTION,
        "icon": {"uri": AGENT_ICON},
        "adk_agent_definition": {
            "tool_settings": {"tool_description": TOOL_DESCRIPTION},
            "provisioned_reasoning_engine": {
                "reasoning_engine": AGENT_ENGINE_RESOURCE,
            },
        },
    }
    print(f"[register] POST {url}")
    print(f"[register] display_name={AGENT_DISPLAY_NAME}")
    print(f"[register] reasoning_engine={AGENT_ENGINE_RESOURCE}")
    resp = requests.post(url, headers=_headers(), json=payload)
    if resp.status_code in (200, 201):
        name = resp.json().get("name", "")
        print(f"[register] OK: {name}")
        return name
    print(f"[register] ERROR ({resp.status_code}): {resp.text}")
    return None


def share(agent_name: str) -> bool:
    url = f"https://discoveryengine.googleapis.com/v1alpha/{agent_name}?updateMask=sharingConfig"
    resp = requests.patch(
        url,
        headers=_headers(),
        json={"sharingConfig": {"scope": "ALL_USERS"}},
    )
    if resp.status_code == 200:
        print("[share] OK: shared with ALL_USERS")
        return True
    print(f"[share] WARNING ({resp.status_code}): {resp.text}")
    return False


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd in ("agent", "all"):
        name = register_agent()
        if cmd == "all" and name:
            share(name)
    elif cmd == "share":
        if len(sys.argv) < 3:
            print("Usage: register.py share <agent-resource-name>")
            sys.exit(1)
        share(sys.argv[2])
    else:
        print("Usage: register.py [agent|share|all]")
        sys.exit(1)


if __name__ == "__main__":
    main()
