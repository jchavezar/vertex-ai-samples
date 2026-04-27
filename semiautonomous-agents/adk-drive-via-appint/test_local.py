"""
Local smoke test.

Usage:
    uv sync
    cp .env.example .env
    uv run python test_local.py "find my notes about envato"
"""
import asyncio
import sys

from dotenv import load_dotenv

load_dotenv()

from google.adk.runners import InMemoryRunner  # noqa: E402
from google.genai.types import Content, Part  # noqa: E402

from agent import root_agent  # noqa: E402


async def ask(query: str) -> None:
    runner = InMemoryRunner(agent=root_agent, app_name="adk-drive-via-appint")
    session = await runner.session_service.create_session(
        app_name="adk-drive-via-appint", user_id="local"
    )

    print(f"\n>>> {query}\n")
    content = Content(parts=[Part(text=query)], role="user")
    async for event in runner.run_async(
        user_id="local", session_id=session.id, new_message=content
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.function_call:
                    fc = part.function_call
                    print(f"[tool] {fc.name}({dict(fc.args or {})})")
                if part.function_response:
                    print(f"[tool result] {str(part.function_response.response)[:300]}")
                if part.text:
                    print(f"\n{part.text}")


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) or "list 5 most recent files I own in Google Drive"
    asyncio.run(ask(query))
