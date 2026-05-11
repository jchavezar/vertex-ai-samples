"""Smoke-test the deployed Agent Engine: send a prompt, confirm the PDF
artifact was saved (via `actions.artifact_delta`) and the agent
returned a chat reply.

Usage:
    cd semiautonomous-agents/docgen-agent
    uv run python scripts/test_remote.py "summarize Liga MX this weekend and create a PDF report"
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import vertexai  # noqa: E402
from dotenv import load_dotenv  # noqa: E402
from vertexai import agent_engines  # noqa: E402

load_dotenv(ROOT / ".env")

PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
DEPLOY_LOCATION = os.environ.get("DEPLOY_LOCATION", "us-central1")
RESOURCE = os.environ["AGENT_ENGINE_RESOURCE"]


def main(prompt: str) -> None:
    vertexai.init(project=PROJECT, location=DEPLOY_LOCATION)
    remote = agent_engines.get(RESOURCE)
    print(f"[remote] resource={RESOURCE}")
    print(f"[remote] prompt: {prompt}\n")

    saw_text = False
    saved_pdfs: list[str] = []
    for event in remote.stream_query(message=prompt, user_id="remote_tester"):
        content = event.get("content") or {}
        author = event.get("author") or "?"
        actions = event.get("actions") or {}
        for name, _version in (actions.get("artifact_delta") or {}).items():
            if name.lower().endswith(".pdf"):
                saved_pdfs.append(name)
                print(f"\n[{author}] artifact_delta: saved {name}")
        for p in content.get("parts") or []:
            if p.get("text"):
                print(p["text"], end="", flush=True)
                saw_text = True
            if "function_call" in p:
                print(f"\n[{author}] function_call: {p['function_call'].get('name')}")
            if "function_response" in p:
                print(f"\n[{author}] function_response: {p['function_response'].get('name')}")
    print()
    print(f"[remote] saw_text={saw_text} pdfs={saved_pdfs}")
    if not saved_pdfs:
        sys.exit(2)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python scripts/test_remote.py "<prompt>"')
        sys.exit(1)
    main(sys.argv[1])
