"""
LOCAL TESTING - Before Agent Engine Deployment
===============================================

This script tests the agent locally using in-memory sessions.
Run this BEFORE deploying to Agent Engine to verify:
1. Agent tools work correctly
2. Discovery Engine client connects
3. WIF token exchange works (if testing with real tokens)

Usage:
    uv run python test_local.py                    # Basic test
    uv run python test_local.py "custom query"     # Custom query
    uv run python test_local.py --with-token       # Test with real JWT

Version: 1.1.0
Date: 2026-04-04
Last Used: 2026-04-04 09:20 UTC
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()

# Required for google.adk
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

# Import agent from the agent package
from agent import root_agent


def print_banner(title: str):
    """Print a formatted banner."""
    width = 60
    print("=" * width)
    print(f" {title}".center(width))
    print("=" * width)


async def test_tools_directly():
    """
    Test individual tools without the full agent.
    Useful for debugging Discovery Engine connectivity.
    """
    from agent.discovery_engine import DiscoveryEngineClient

    print_banner("Phase 1: Direct Tool Testing")

    client = DiscoveryEngineClient()
    print(f"Project Number: {client.project_number}")
    print(f"Engine ID:      {client.engine_id}")
    print(f"Data Store ID:  {client.data_store_id}")
    print(f"WIF Pool ID:    {client.wif_pool_id}")
    print(f"WIF Provider:   {client.wif_provider_id}")
    print()

    # Test without user token (service account fallback)
    print("[Test] Calling Discovery Engine with service account...")
    try:
        result = await client.search("test query", user_token=None)
        print(f"[OK] Answer: {result.answer[:200]}...")
        print(f"[OK] Sources: {len(result.sources)}")
    except Exception as e:
        print(f"[ERROR] {e}")

    print()


async def test_agent_conversation(query: str, simulate_token: str = None):
    """
    Test the full agent with in-memory sessions.

    Args:
        query: The test query
        simulate_token: Optional JWT to inject into session state
    """
    print_banner("Phase 2: Agent Conversation Testing")

    print(f"Agent:  {root_agent.name}")
    print(f"Model:  {root_agent.model}")
    print(f"Tools:  {[t.__name__ if hasattr(t, '__name__') else str(t) for t in root_agent.tools]}")
    print()

    # Create session service and runner
    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent,
        app_name="local_test",
        session_service=session_service
    )

    # Create session
    session = await session_service.create_session(
        app_name="local_test",
        user_id="test_user"
    )

    # Optionally inject a token to simulate Agentspace
    if simulate_token:
        session.state["temp:sharepointauth2"] = simulate_token
        print(f"[Injected] Token into session state (temp:sharepointauth2)")

    print(f"[Query] {query}")
    print("-" * 60)

    # Create proper message content
    user_message = types.Content(
        role="user",
        parts=[types.Part(text=query)]
    )

    response_text = ""
    async for event in runner.run_async(
        user_id="test_user",
        session_id=session.id,
        new_message=user_message
    ):
        if hasattr(event, 'content') and event.content:
            if hasattr(event.content, 'parts'):
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        print(part.text, end="", flush=True)
                        response_text += part.text
        elif hasattr(event, 'text'):
            print(event.text, end="", flush=True)
            response_text += event.text

    print()
    print("-" * 60)
    print(f"[Response Length] {len(response_text)} chars")
    return response_text


async def main():
    """Main test runner."""
    print_banner("LOCAL TESTING - InsightComparator Agent")
    print()
    print("This tests the agent BEFORE deploying to Agent Engine.")
    print("Use this to verify tools, connectivity, and basic behavior.")
    print()

    # Parse arguments
    query = "What are best practices for cloud security?"
    use_token = False

    for arg in sys.argv[1:]:
        if arg == "--with-token":
            use_token = True
        elif not arg.startswith("-"):
            query = arg

    # Phase 1: Direct tool testing
    await test_tools_directly()

    # Phase 2: Agent conversation
    token = None
    if use_token:
        # Try to read a saved token
        token_path = "/tmp/entra_token.txt"
        if os.path.exists(token_path):
            with open(token_path) as f:
                token = f.read().strip()
            print(f"[Token] Loaded from {token_path}")
        else:
            print(f"[Token] No token found at {token_path}")
            print("[Token] Run the frontend, login, and make a request first")

    await test_agent_conversation(query, simulate_token=token)

    print()
    print_banner("LOCAL TESTING COMPLETE")
    print()
    print("Next steps:")
    print("  1. If tests pass, deploy to Agent Engine:")
    print("     uv run python deploy.py")
    print()
    print("  2. After deployment, test remotely:")
    print("     uv run python test_remote.py")


if __name__ == "__main__":
    asyncio.run(main())
