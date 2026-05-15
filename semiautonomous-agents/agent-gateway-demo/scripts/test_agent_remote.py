"""Smoke-test the deployed Agent Engine: create session with fake token, send
a prompt, print streamed events. Useful for validating the wiring before the
backend or frontend exist."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "agent"))

import vertexai  # noqa: E402
from dotenv import load_dotenv  # noqa: E402
from vertexai import agent_engines  # noqa: E402

load_dotenv(ROOT / ".env")

PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
DEPLOY_LOCATION = os.environ.get("DEPLOY_LOCATION", "us-central1")
RESOURCE = os.environ["AGENT_ENGINE_RESOURCE"]
SESSION_TOKEN_KEY = os.environ.get("SESSION_TOKEN_KEY", "temp:sharepoint_3lo")

FAKE_TOKEN = (
    "eyJhbGciOiJub25lIn0."
    "eyJzdWIiOiJ0ZXN0LXVzZXJAdmlybnZla28udGVzdCIsIm5hbWUiOiJUZXN0IFVzZXIifQ."
)


def main(prompt: str) -> None:
    vertexai.init(project=PROJECT, location=DEPLOY_LOCATION)
    remote = agent_engines.get(RESOURCE)
    print(f"[remote] resource={RESOURCE}")

    session = remote.create_session(
        user_id="remote_tester", state={SESSION_TOKEN_KEY: FAKE_TOKEN}
    )
    sid = session.get("id") if isinstance(session, dict) else session.id
    print(f"[remote] session_id={sid}")
    print(f"[remote] prompt: {prompt}\n")

    for event in remote.stream_query(user_id="remote_tester", session_id=sid, message=prompt):
        content = event.get("content") or {}
        author = event.get("author") or "?"
        for p in content.get("parts") or []:
            if p.get("text"):
                print(p["text"], end="", flush=True)
            if "function_call" in p:
                print(f"\n[{author}] function_call: {p['function_call'].get('name')}({list((p['function_call'].get('args') or {}).keys())})")
            if "function_response" in p:
                resp = p["function_response"].get("response") or {}
                keys = list(resp.keys()) if isinstance(resp, dict) else []
                print(f"\n[{author}] function_response: {p['function_response'].get('name')} -> {keys}")
    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python scripts/test_agent_remote.py "<prompt>"')
        sys.exit(1)
    main(sys.argv[1])
