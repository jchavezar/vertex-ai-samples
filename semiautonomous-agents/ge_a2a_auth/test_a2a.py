"""Direct A2A test against the deployed Agent Runtime endpoint.

Uses your own ADC user token (same shape GE will use post-OAuth, just sourced
locally). Confirms the agent is up and responds to message/send before you
register it in GE.
"""

from __future__ import annotations

import json
import os
import time
import uuid
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
    a2a_url = os.environ["A2A_URL"]
    headers = {
        "Authorization": f"Bearer {bearer()}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": os.environ["PROJECT_ID"],
    }

    # 1. Fetch agent card
    card = requests.get(f"{a2a_url}/v1/card", headers=headers, timeout=30)
    card.raise_for_status()
    print("AGENT CARD")
    print(json.dumps(card.json(), indent=2)[:1000])

    # 2. message:send (proto wire shape: SendMessageRequest)
    body = {
        "request": {
            "message_id": str(uuid.uuid4()),
            "role": "ROLE_USER",
            "content": [{"text": "hello from test_a2a.py"}],
        }
    }
    r = requests.post(
        f"{a2a_url}/v1/message:send", headers=headers, json=body, timeout=60
    )
    print(f"\nmessage:send -> {r.status_code}")
    print(r.text[:2000])
    if r.status_code != 200:
        return

    # 3. Poll the task until COMPLETED (agent reply arrives via status/artifacts)
    data = r.json()
    task_id = data.get("task", {}).get("id")
    if not task_id:
        return
    for attempt in range(20):
        time.sleep(1.5)
        tr = requests.get(
            f"{a2a_url}/v1/tasks/{task_id}", headers=headers, timeout=30
        )
        tr.raise_for_status()
        task = tr.json()
        state = task.get("status", {}).get("state", "")
        print(f"  [poll {attempt}] state={state}")
        if state in {"TASK_STATE_COMPLETED", "TASK_STATE_FAILED", "TASK_STATE_CANCELED"}:
            print("\nFINAL TASK:")
            print(json.dumps(task, indent=2)[:3000])
            return


if __name__ == "__main__":
    main()
