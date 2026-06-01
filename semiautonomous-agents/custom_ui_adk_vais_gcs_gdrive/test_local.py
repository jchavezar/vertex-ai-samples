"""
test_local.py
Minimal, clean runner to smoke test the Google ADK Grounding Agent locally.

Usage:
    export DRIVE_ACCESS_TOKEN="ya29.your_oauth_token..."
    python test_local.py "what was alphabet revenue?"
"""
from __future__ import annotations

import asyncio
import os
import sys
from dotenv import load_dotenv

# 1. Load local environment configurations
load_dotenv()

# Imports must come after load_dotenv to register Vertex AI configurations
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
from agent.agent import root_agent

APP_NAME = "adk-drive-ae"
USER_ID = "local-test-user"


async def ask_local_agent(query: str, token: str) -> None:
    # 2. Initialize the Google ADK local InMemoryRunner
    runner = InMemoryRunner(agent=root_agent, app_name=APP_NAME)

    # 3. Create a secure local session with user credentials
    session = await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        state={
            "drive_access_token": token,
            "temp:drive_access_token": token,
        },
    )

    print(f"\n[Prompt]: {query}")
    print("=" * 60)

    content = Content(parts=[Part(text=query)], role="user")
    
    # 4. Stream response and capture tool events
    async for event in runner.run_async(
        user_id=USER_ID, 
        session_id=session.id, 
        new_message=content
    ):
        if not (event.content and event.content.parts):
            continue
            
        for part in event.content.parts:
            # Output tool selection and query details
            if part.function_call:
                fc = part.function_call
                print(f"\n🔧 [Tool Invocation] {fc.name}({dict(fc.args or {})})")
                
            # Output preview of the live search results
            if part.function_response:
                resp = part.function_response.response
                results = resp.get("results", [])
                print(f"📊 [Tool Response] Returned {len(results)} search results")
                
            # Output generated reasoning and text from Gemini
            if part.text:
                print(part.text, end="", flush=True)
    print("\n" + "=" * 60 + "\n")


def main() -> None:
    # Read GSuite access token
    token = os.environ.get("DRIVE_ACCESS_TOKEN", "")
    if not token:
        print("❌ ERROR: DRIVE_ACCESS_TOKEN environment variable is not set.")
        print("Please obtain an OAuth token and export it:")
        print("  export DRIVE_ACCESS_TOKEN=\"ya29.your_token...\"")
        sys.exit(1)

    # Grab query from command arguments or use default
    query = " ".join(sys.argv[1:]) or "list 5 most recent files I own in Google Drive"
    
    try:
        asyncio.run(ask_local_agent(query, token))
    except Exception as e:
        print(f"❌ Error executing local agent: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
