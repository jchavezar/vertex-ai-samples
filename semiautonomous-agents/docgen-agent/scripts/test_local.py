"""Local sanity check: runs the agent end-to-end without hitting
Agent Engine, and saves any generated PDF artifact to disk for visual
inspection.

Usage:
    cd semiautonomous-agents/docgen-agent
    uv run python scripts/test_local.py "summarize Liga MX this weekend and create a PDF report"
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env")

# gemini-3-* preview models only serve from `global`. Force-override the
# shell's GOOGLE_CLOUD_LOCATION (often pinned to us-central1 on this VM).
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ["GOOGLE_CLOUD_LOCATION"] = os.environ.get("RUNTIME_GENAI_LOCATION", "global")

from google.adk.runners import InMemoryRunner  # noqa: E402
from google.genai import types  # noqa: E402

from agent import root_agent  # noqa: E402

OUT_DIR = ROOT / "out"


async def run(prompt: str) -> None:
    runner = InMemoryRunner(agent=root_agent, app_name="docgen_local")
    session = await runner.session_service.create_session(
        app_name="docgen_local", user_id="local_tester"
    )
    user_msg = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])

    print(f"[local] prompt: {prompt}\n")
    saw_pdf = False
    async for event in runner.run_async(
        user_id="local_tester", session_id=session.id, new_message=user_msg
    ):
        author = getattr(event, "author", None) or "?"
        for p in (event.content.parts if event.content else []) or []:
            if getattr(p, "text", None):
                print(p.text, end="", flush=True)
            if getattr(p, "inline_data", None):
                mt = p.inline_data.mime_type or ""
                size = len(p.inline_data.data or b"")
                print(f"\n[{author}] inline_data: {mt}, {size} bytes")
                if mt == "application/pdf":
                    saw_pdf = True
            fc = getattr(p, "function_call", None)
            if fc:
                args_keys = list((fc.args or {}).keys())
                print(f"\n[{author}] function_call: {fc.name}(keys={args_keys})")
            fr = getattr(p, "function_response", None)
            if fr:
                resp_keys = list((fr.response or {}).keys()) if isinstance(fr.response, dict) else []
                print(f"\n[{author}] function_response: {fr.name} -> {resp_keys}")
    print()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    artifacts = await runner.artifact_service.list_artifact_keys(
        app_name="docgen_local", user_id="local_tester", session_id=session.id
    )
    print(f"[local] artifacts: {artifacts}")
    for name in artifacts:
        if not name.lower().endswith(".pdf"):
            continue
        part = await runner.artifact_service.load_artifact(
            app_name="docgen_local",
            user_id="local_tester",
            session_id=session.id,
            filename=name,
        )
        out_path = OUT_DIR / name
        out_path.write_bytes(part.inline_data.data)
        print(f"[local] wrote {out_path} ({len(part.inline_data.data)} bytes)")
        saw_pdf = True

    if not saw_pdf:
        print("[local] NOTE: no PDF artifact produced — agent decided no document was needed.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python scripts/test_local.py "<prompt>"')
        sys.exit(1)
    asyncio.run(run(sys.argv[1]))
