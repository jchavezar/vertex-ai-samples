"""Local CLI to run the report-generator end-to-end.

Usage:
    python run_local.py "Vertex AI Vector Search vs. Pinecone in 2026"
"""
from __future__ import annotations

import asyncio
import sys

from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part

load_dotenv(override=True)

from agent import root_agent  # noqa: E402  — load env first


async def _run(topic: str) -> None:
    runner = InMemoryRunner(agent=root_agent, app_name="report-generator")
    session = await runner.session_service.create_session(
        app_name="report-generator", user_id="local"
    )
    msg = Content(parts=[Part(text=topic)], role="user")

    async for event in runner.run_async(
        user_id="local", session_id=session.id, new_message=msg
    ):
        if event.content and event.content.parts:
            for p in event.content.parts:
                if getattr(p, "text", None):
                    print(f"[{event.author}] {p.text[:400]}")

    final = await runner.session_service.get_session(
        app_name="report-generator", user_id="local", session_id=session.id
    )
    pdf = final.state.get("pdf_path")
    if pdf:
        print(f"\nPDF written to: {pdf}")
    else:
        print("\nNo PDF produced — check earlier output for errors.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    asyncio.run(_run(" ".join(sys.argv[1:])))
