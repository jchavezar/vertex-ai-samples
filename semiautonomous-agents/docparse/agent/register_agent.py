"""Register the deployed Agent Engine with a Gemini Enterprise app, then
share with ALL_USERS automatically.

This is a CROSS-PROJECT link: the agent runs in DEPLOY_PROJECT_ID, but
exposes itself in GE_PROJECT_ID's app.

Prerequisites:
  1. Agent deployed via deploy.py (REASONING_ENGINE_RES set in .env).
  2. Gemini Enterprise app already exists (AS_APP set in .env).
  3. Cross-project IAM: in DEPLOY_PROJECT_ID, grant
       service-{GE_PROJECT_NUMBER}@gcp-sa-discoveryengine.iam.gserviceaccount.com
     the role roles/aiplatform.user. Otherwise GE can't invoke the agent.

Auth note:
  This script uses `gcloud auth print-access-token` (the active gcloud user
  identity), NOT Application Default Credentials. ADC sometimes resolves to
  a different identity that doesn't have discoveryengine.agents.create on
  the target GE project, especially in cross-org setups. Make sure the
  active gcloud account is the one with the perms.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

# Walk up to docparse/.env (one level above agent/)
_HERE = Path(__file__).resolve().parent
load_dotenv(_HERE.parent / ".env")


GE_PROJECT_ID = os.environ["GE_PROJECT_ID"]
GE_PROJECT_NUMBER = os.environ["GE_PROJECT_NUMBER"]
AS_APP = os.environ["AS_APP"]
ASSISTANT = os.environ.get("AS_ASSISTANT", "default_assistant")
REASONING_ENGINE_RES = os.environ["REASONING_ENGINE_RES"]

AGENT_DISPLAY_NAME = os.environ.get("AGENT_DISPLAY_NAME", "docparse RAG agent")
AGENT_DESCRIPTION = os.environ.get(
    "AGENT_DESCRIPTION",
    "Answers questions about reports indexed by docparse, citing the exact "
    "source page for every fact.",
)
AGENT_TOOL_DESCRIPTION = os.environ.get(
    "AGENT_TOOL_DESCRIPTION",
    "Use for questions about the documents in this corpus. Handles page-"
    "anchored lookups, chart-cell values, math/aggregation across charts, "
    "and free-text body content.",
)
AGENT_ICON_URI = os.environ.get(
    "AGENT_ICON_URI",
    "https://fonts.gstatic.com/s/i/short-term/release/googlesymbols/find_in_page/default/24px.svg",
)


def _bearer() -> str:
    return subprocess.check_output(
        ["gcloud", "auth", "print-access-token"], text=True
    ).strip()


def _api(path: str) -> str:
    return f"https://discoveryengine.googleapis.com/v1alpha/{path.lstrip('/')}"


def register() -> dict:
    print(f"\n=== Registering agent ===")
    print(f"  Agent Engine: {REASONING_ENGINE_RES}")
    print(f"  GE project:   {GE_PROJECT_ID} ({GE_PROJECT_NUMBER})")
    print(f"  GE app:       {AS_APP} / {ASSISTANT}\n")

    headers = {
        "Authorization": f"Bearer {_bearer()}",
        "Content-Type": "application/json",
        "x-goog-user-project": GE_PROJECT_ID,
    }

    url = _api(
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

    r = requests.post(url, headers=headers, data=json.dumps(payload))
    if r.status_code != 200:
        sys.exit(f"ERROR ({r.status_code}): {r.text}")

    res = r.json()
    print(f"=== Registered ===")
    print(f"  agent: {res.get('name')}")
    print(f"  display: {res.get('displayName')}")

    share_agent(res["name"], headers)
    return res


def share_agent(agent_name: str, headers: dict) -> None:
    """Patch sharingConfig.scope to ALL_USERS so anyone with access to the
    GE app can pick the agent without a per-user grant."""
    url = _api(f"{agent_name}?updateMask=sharingConfig")
    payload = {"sharingConfig": {"scope": "ALL_USERS"}}
    r = requests.patch(url, headers=headers, data=json.dumps(payload))
    if r.status_code == 200:
        print(f"  shared with: ALL_USERS")
    else:
        print(f"  WARNING: share failed ({r.status_code}): {r.text}")


if __name__ == "__main__":
    register()
