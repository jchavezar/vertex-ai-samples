"""Register The Paperclip Detective in Gemini Enterprise + share with ALL_USERS."""
import os
import sys

import google.auth
import google.auth.transport.requests
import requests
from dotenv import load_dotenv

load_dotenv()

GE_PROJECT_ID = os.environ["GE_PROJECT_ID"]
GE_PROJECT_NUMBER = os.environ["GE_PROJECT_NUMBER"]
AS_APP = os.environ["AS_APP"]
REASONING_ENGINE_RES = os.environ["REASONING_ENGINE_RES"]

AGENT_DISPLAY_NAME = os.environ.get("AGENT_DISPLAY_NAME", "The Paperclip Detective")
AGENT_DESCRIPTION = os.environ.get("AGENT_DESCRIPTION", "Forensic file-routing agent")
TOOL_DESCRIPTION = os.environ.get(
    "TOOL_DESCRIPTION",
    "Use this agent to inspect how files attached in the chat reach the agent.",
)
AGENT_ICON = os.environ.get(
    "AGENT_ICON",
    "https://fonts.gstatic.com/s/i/short-term/release/googlesymbols/attach_file/default/24px.svg",
)


def _headers() -> dict:
    creds, _ = google.auth.default()
    creds.refresh(google.auth.transport.requests.Request())
    return {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "x-goog-user-project": GE_PROJECT_ID,
    }


def _base() -> str:
    return f"https://discoveryengine.googleapis.com/v1alpha/projects/{GE_PROJECT_NUMBER}/locations/global"


def register_agent() -> str | None:
    url = f"{_base()}/collections/default_collection/engines/{AS_APP}/assistants/default_assistant/agents"
    payload = {
        "displayName": AGENT_DISPLAY_NAME,
        "description": AGENT_DESCRIPTION,
        "icon": {"uri": AGENT_ICON},
        "adk_agent_definition": {
            "tool_settings": {"tool_description": TOOL_DESCRIPTION},
            "provisioned_reasoning_engine": {"reasoning_engine": REASONING_ENGINE_RES},
        },
    }
    print(f"Registering: {AGENT_DISPLAY_NAME}")
    resp = requests.post(url, headers=_headers(), json=payload)
    if resp.status_code == 200:
        name = resp.json().get("name", "")
        print(f"Registered: {name}")
        return name
    print(f"ERROR ({resp.status_code}): {resp.text}")
    return None


def share(agent_name: str) -> bool:
    url = f"https://discoveryengine.googleapis.com/v1alpha/{agent_name}?updateMask=sharingConfig"
    resp = requests.patch(url, headers=_headers(), json={"sharingConfig": {"scope": "ALL_USERS"}})
    if resp.status_code == 200:
        print("Shared with ALL_USERS")
        return True
    print(f"WARNING ({resp.status_code}): {resp.text}")
    return False


if __name__ == "__main__":
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
