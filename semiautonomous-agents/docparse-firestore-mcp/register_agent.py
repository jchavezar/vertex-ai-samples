"""Register the Docparse Firestore ADK Agent inside the Gemini Enterprise Agent Registry.

This registers the agent so that it appears in the Gemini Enterprise Agent side panel/picker.
The agent connects to the ADK Reasoning Engine that invokes your Cloud Run Firestore MCP.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import requests

# ---- Load .env if present -------------------
_HERE = Path(__file__).resolve().parent
for _candidate in (_HERE / ".env", _HERE.parent / "eval" / ".env", _HERE.parent / ".env"):
    if _candidate.exists():
        for line in _candidate.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

GE_PROJECT_ID = os.environ.get("GE_PROJECT_ID", "vtxdemos")
GE_PROJECT_NUMBER = os.environ.get("GE_PROJECT_NUMBER", "254356041555")
AS_APP = os.environ.get("AS_APP", "docparse-testing")
ASSISTANT = os.environ.get("AS_ASSISTANT", "default_assistant")
REASONING_ENGINE_RES = os.environ.get("REASONING_ENGINE_RES", "")

AGENT_DISPLAY_NAME = os.environ.get("AGENT_DISPLAY_NAME", "Firestore PDF RAG Agent")
AGENT_DESCRIPTION = os.environ.get(
    "AGENT_DESCRIPTION",
    "Answers questions about reports indexed by docparse on Firestore, bringing rich PDF-level page grounding.",
)
AGENT_TOOL_DESCRIPTION = os.environ.get(
    "AGENT_TOOL_DESCRIPTION",
    "Use for questions about documents in this corpus. Connects to Cloud Run Firestore RAG.",
)
AGENT_ICON_URI = os.environ.get(
    "AGENT_ICON_URI",
    "https://fonts.gstatic.com/s/i/short-term/release/googlesymbols/find_in_page/default/24px.svg",
)


def _bearer() -> str:
    return subprocess.check_output(
        ["gcloud", "auth", "print-access-token"], text=True
    ).strip()


def main():
    if not REASONING_ENGINE_RES:
        print("[!] Error: REASONING_ENGINE_RES not set in environment or .env file.")
        print("    Please deploy your ADK Reasoning Engine first to get the resource ID.")
        sys.exit(1)

    print(f"[*] Registering Agent in Agent Registry Panel")
    print(f"    GCP Project ID:     {GE_PROJECT_ID}")
    print(f"    GCP Project Number: {GE_PROJECT_NUMBER}")
    print(f"    GE App ID:          {AS_APP}")
    print(f"    Reasoning Engine:   {REASONING_ENGINE_RES}")

    headers = {
        "Authorization": f"Bearer {_bearer()}",
        "Content-Type": "application/json",
        "x-goog-user-project": GE_PROJECT_ID,
    }

    url = (
        f"https://discoveryengine.googleapis.com/v1alpha/"
        f"projects/{GE_PROJECT_NUMBER}/locations/global/collections/"
        f"default_collection/engines/{AS_APP}/assistants/{ASSISTANT}/agents"
    )

    payload = {
        "displayName": AGENT_DISPLAY_NAME,
        "description": AGENT_DESCRIPTION,
        "icon": {"uri": AGENT_ICON_URI},
        "adk_agent_definition": {
            "tool_settings": {"tool_description": AGENT_TOOL_DESCRIPTION},
            "provisioned_reasoning_engine": {
                "reasoning_engine": REASONING_ENGINE_RES,
            },
        },
    }

    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code != 200:
        print(f"[!] Error registering agent ({resp.status_code}): {resp.text}")
        sys.exit(1)

    res = resp.json()
    agent_name = res.get("name")
    print(f"[+] Agent Registered Successfully!")
    print(f"    Agent ID: {agent_name}")
    print(f"    Display Name: {res.get('displayName')}")

    # Share with ALL_USERS automatically
    share_url = f"https://discoveryengine.googleapis.com/v1alpha/{agent_name}?updateMask=sharingConfig"
    share_payload = {"sharingConfig": {"scope": "ALL_USERS"}}
    r_share = requests.patch(share_url, headers=headers, json=share_payload)
    if r_share.status_code == 200:
        print(f"[+] Shared successfully with: ALL_USERS")
    else:
        print(f"[!] Warning: share failed ({r_share.status_code}): {r_share.text}")


if __name__ == "__main__":
    main()
