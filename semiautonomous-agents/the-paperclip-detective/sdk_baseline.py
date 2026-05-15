"""Programmatic baseline tests against the deployed agent.

Sends three controlled payloads via stream_query and prints the agent's
verdict for each. These baselines tell us what each routing path looks like
in the agent's logs, so the GE-UI test result is unambiguous to interpret.

Cases:
    1. NO_FILE       — plain text query, no file at all
    2. INLINE_PDF    — text + Part(inline_data=PDF bytes) in the same message
    3. (artifact-only requires session-side artifact upload — GE flow)
"""
import asyncio
import base64
import os
import sys
from pathlib import Path

import vertexai
from dotenv import load_dotenv
from vertexai import agent_engines

load_dotenv()
PROJECT_ID = os.environ["PROJECT_ID"]
LOCATION = os.environ.get("LOCATION", "us-central1")
RE_RES = os.environ["REASONING_ENGINE_RES"]
PDF_PATH = Path("/tmp/paperclip-test.pdf")

vertexai.init(project=PROJECT_ID, location=LOCATION)
agent = agent_engines.get(RE_RES)


def run(label: str, message):
    print(f"\n{'=' * 70}\n  {label}\n{'=' * 70}")
    last_text = ""
    for ev in agent.stream_query(message=message, user_id="paperclip-tester"):
        # ev is a dict with 'content' -> {'parts': [...]}
        content = (ev or {}).get("content") or {}
        for p in content.get("parts", []) or []:
            if p.get("text"):
                last_text = p["text"]
                print(p["text"], end="", flush=True)
            elif p.get("function_call"):
                fc = p["function_call"]
                print(f"\n  -> tool call: {fc.get('name')}({list(fc.get('args', {}).keys())})", flush=True)
            elif p.get("function_response"):
                fr = p["function_response"]
                resp = fr.get("response") or {}
                print(f"\n  <- tool result: {fr.get('name')} keys={list(resp.keys()) if isinstance(resp, dict) else type(resp).__name__}", flush=True)
    print(f"\n--- final text ({len(last_text)} chars) ---")


# Case 1: plain text, no file
run("CASE 1 — NO FILE (plain text)",
    "Run your forensic procedure. Tell me how this message reached you.")

# Case 2: inline PDF as Part
pdf_bytes = PDF_PATH.read_bytes()
print(f"\n[loaded PDF: {len(pdf_bytes)} bytes from {PDF_PATH}]")

inline_message = {
    "role": "user",
    "parts": [
        {"text": "What's in the attached PDF? Run your forensic procedure first."},
        {
            "inline_data": {
                "mime_type": "application/pdf",
                "data": base64.b64encode(pdf_bytes).decode("ascii"),
            }
        },
    ],
}
run("CASE 2 — INLINE PDF (Part with inline_data)", inline_message)

print("\nDone.")
