"""
Local smoke test — verify the agent + token-injection wiring without browser.

Usage:
    cd vertex-ai-samples/semiautonomous-agents/adk-drive-ae
    uv sync
    cp .env.example .env

    # Get a temporary Drive access_token (any of these work):
    #   - https://developers.google.com/oauthplayground (scope: drive.readonly), copy the access_token
    #   - or `gcloud auth print-access-token` if you bound the user-OAuth scope to gcloud
    export DRIVE_ACCESS_TOKEN="ya29...."

    uv run python scripts/test_local.py "list my 5 most recent files"
"""
from __future__ import annotations

import asyncio
import os
import sys

from dotenv import load_dotenv

load_dotenv()

# Imports must come AFTER load_dotenv so GOOGLE_GENAI_USE_VERTEXAI etc. are set.
from google.adk.runners import InMemoryRunner  # noqa: E402
from google.genai.types import Content, Part  # noqa: E402

from agent import root_agent  # noqa: E402

APP_NAME = "adk-drive-ae"
USER_ID = "local-test"


async def ask(query: str, token: str) -> None:
    runner = InMemoryRunner(agent=root_agent, app_name=APP_NAME)

    # Inject the access token into session state under both keys (Agent Engine
    # uses temp:, local InMemoryRunner uses bare). Belt + suspenders.
    session = await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        state={
            "drive_access_token": token,
            "temp:drive_access_token": token,
        },
    )

    print(f"\n>>> {query}\n")

    content = Content(parts=[Part(text=query)], role="user")
    async for event in runner.run_async(
        user_id=USER_ID, session_id=session.id, new_message=content
    ):
        if not (event.content and event.content.parts):
            continue
        for part in event.content.parts:
            if part.function_call:
                fc = part.function_call
                print(f"[tool] {fc.name}({dict(fc.args or {})})")
            if part.function_response:
                preview = str(part.function_response.response)[:300]
                print(f"[tool result] {preview}")
            if part.text:
                print(f"\n{part.text}")


def main() -> None:
    token = os.environ.get("DRIVE_ACCESS_TOKEN", "")
    if not token:
        print("ERROR: DRIVE_ACCESS_TOKEN env var is required.")
        print("Get one from https://developers.google.com/oauthplayground")
        print("  Scope: https://www.googleapis.com/auth/drive.readonly")
        sys.exit(1)

    query = " ".join(sys.argv[1:]) or "list 5 most recent files I own in Google Drive"
    asyncio.run(ask(query, token))


if __name__ == "__main__":
    main()
