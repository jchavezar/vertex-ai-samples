"""Quick local sanity check for the agent — runs the spatial detector on a
local image without going through Agent Engine or Gemini Enterprise.

Usage:
    cd semiautonomous-agents/spatial_on_ge
    uv run python scripts/test_local.py path/to/image.jpg "find the cats"
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

# Make sure the GenAI client knows where to call.
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")

from google.adk.runners import InMemoryRunner  # noqa: E402
from google.genai import types  # noqa: E402

from agent import root_agent  # noqa: E402


async def main(image_path: str, prompt: str):
    img_bytes = Path(image_path).read_bytes()
    mime = "image/jpeg" if image_path.lower().endswith((".jpg", ".jpeg")) else "image/png"

    runner = InMemoryRunner(agent=root_agent, app_name="spatial_local")
    session = await runner.session_service.create_session(
        app_name="spatial_local", user_id="local_tester"
    )
    # Pre-stage the image as an artifact (mirrors the GE artifact-only routing).
    await runner.artifact_service.save_artifact(
        app_name="spatial_local",
        user_id="local_tester",
        session_id=session.id,
        filename="user_upload.jpeg",
        artifact=types.Part.from_bytes(data=img_bytes, mime_type=mime),
    )

    user_msg = types.Content(
        role="user",
        parts=[
            types.Part.from_text(
                text=f"{prompt}\n<start_of_user_uploaded_file: user_upload.jpeg>\n<end_of_user_uploaded_file: user_upload.jpeg>"
            )
        ],
    )

    print(f"[local] prompt: {prompt}\n")
    async for event in runner.run_async(
        user_id="local_tester", session_id=session.id, new_message=user_msg
    ):
        for p in (event.content.parts if event.content else []) or []:
            if getattr(p, "text", None):
                print(p.text, end="", flush=True)
            if getattr(p, "inline_data", None):
                mt = p.inline_data.mime_type or ""
                size = len(p.inline_data.data or b"")
                print(f"\n[inline_data: {mt}, {size} bytes]")
            fc = getattr(p, "function_call", None)
            if fc:
                print(f"\n[function_call: {fc.name}({dict(fc.args or {})})]")
            fr = getattr(p, "function_response", None)
            if fr:
                print(f"\n[function_response: {fr.name} -> keys={list((fr.response or {}).keys())}]")
    print()

    # Save any annotated artifact to disk so you can eyeball it.
    artifacts = await runner.artifact_service.list_artifact_keys(
        app_name="spatial_local", user_id="local_tester", session_id=session.id
    )
    for name in artifacts:
        if name.startswith("annotated_"):
            part = await runner.artifact_service.load_artifact(
                app_name="spatial_local",
                user_id="local_tester",
                session_id=session.id,
                filename=name,
            )
            out = ROOT / name
            out.write_bytes(part.inline_data.data)
            print(f"[local] wrote {out}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('Usage: python scripts/test_local.py <image-path> "<what to detect>"')
        sys.exit(1)
    asyncio.run(main(sys.argv[1], sys.argv[2]))
