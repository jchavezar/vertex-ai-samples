"""
Local test for Cortex Retriever.

Phase 1: Direct Discovery Engine connectivity test
Phase 2: Full agent conversation via ADK Runner

Usage:
    uv run python test_local.py                          # Default query
    uv run python test_local.py "your custom query"      # Custom query
    uv run python test_local.py --discovery-only          # Phase 1 only
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


async def test_discovery_engine(query: str):
    """Phase 1: Direct Discovery Engine search."""
    from agent.discovery_engine import DiscoveryEngineClient

    print("=" * 50)
    print("Phase 1: Discovery Engine Connectivity")
    print("=" * 50)

    client = DiscoveryEngineClient()
    print(f"Project:    {client.project_number}")
    print(f"Engine:     {client.engine_id}")
    print(f"Data Store: {client.data_store_id}")
    print(f"Query:      {query}")
    print()

    result = await client.search(query)

    print(f"Answer ({len(result.answer)} chars):")
    print(result.answer[:500])
    print()
    print(f"Sources ({len(result.sources)}):")
    for s in result.sources[:3]:
        print(f"  - {s.title}: {s.url}")

    return result


async def test_agent(query: str):
    """Phase 2: Full agent conversation."""
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types

    from agent import root_agent

    print()
    print("=" * 50)
    print("Phase 2: Agent Conversation")
    print("=" * 50)
    print(f"Agent: {root_agent.name}")
    print(f"Model: {root_agent.model}")
    print(f"Tools: {[t.name if hasattr(t, 'name') else type(t).__name__ for t in root_agent.tools]}")
    print(f"Query: {query}")
    print()

    session_service = InMemorySessionService()
    runner = Runner(agent=root_agent, app_name="cortex-test", session_service=session_service)

    session = await session_service.create_session(app_name="cortex-test", user_id="test-user")

    user_msg = types.Content(role="user", parts=[types.Part(text=query)])

    print("Running agent...")
    print("-" * 50)

    async for event in runner.run_async(
        new_message=user_msg,
        user_id="test-user",
        session_id=session.id,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text, end="", flush=True)
                if part.function_call:
                    print(f"\n[Tool call: {part.function_call.name}]")

    print()
    print("-" * 50)
    print("Done.")


async def main():
    query = "What documents do we have about compliance policies?"

    discovery_only = False
    for arg in sys.argv[1:]:
        if arg == "--discovery-only":
            discovery_only = True
        elif not arg.startswith("-"):
            query = arg

    result = await test_discovery_engine(query)

    if not discovery_only:
        await test_agent(query)


if __name__ == "__main__":
    asyncio.run(main())
