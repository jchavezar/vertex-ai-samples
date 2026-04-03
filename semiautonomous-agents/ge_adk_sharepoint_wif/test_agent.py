"""
Test deployed agent locally or via Agent Engine.
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()


def test_local(query: str):
    """Test agent locally without deployment."""
    import asyncio
    from agent import root_agent
    from google.adk.sessions import InMemorySessionService
    from google.adk.runners import Runner
    from google.genai.types import Content, Part

    print(f"Testing locally: {query}\n")

    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent,
        app_name="test",
        session_service=session_service
    )

    async def run():
        await session_service.create_session(
            app_name="test",
            user_id="test",
            session_id="test"
        )

        content = Content(role="user", parts=[Part(text=query)])

        async for event in runner.run_async(
            user_id="test",
            session_id="test",
            new_message=content
        ):
            if event.is_final_response() and event.content and event.content.parts:
                print(event.content.parts[0].text)

    asyncio.run(run())


def test_deployed(query: str, resource_name: str):
    """Test deployed agent via Agent Engine."""
    import vertexai
    from vertexai import agent_engines
    from dotenv import load_dotenv
    load_dotenv()

    PROJECT_ID = os.environ.get("PROJECT_ID", "deloitte-plantas")
    LOCATION = os.environ.get("LOCATION", "us-central1")

    vertexai.init(project=PROJECT_ID, location=LOCATION)

    print(f"Testing deployed agent: {resource_name}")
    print(f"Query: {query}\n")

    deployed_agent = agent_engines.get(resource_name)

    # Create session first
    try:
        session = deployed_agent.create_session(user_id="test")
        print(f"Session created: {session}")
        # The session ID is in the 'id' field
        session_id = session.get("id")
        if not session_id:
            print("Warning: No session ID returned, using default")
            session_id = "default"
    except Exception as e:
        print(f"create_session() failed: {e}")
        session_id = None

    if not session_id:
        print("Error: Could not create session")
        return

    # Use streaming_agent_run_with_events (ADK native)
    try:
        import time
        print(f"\nUsing streaming_agent_run_with_events with session_id={session_id}...")
        start = time.perf_counter()

        final_text = ""
        # Use stream_query (not streaming_agent_run_with_events which expects request_json)
        for event in deployed_agent.stream_query(
            user_id="test",
            session_id=session_id,
            message=query
        ):
            # Event is a dict, not an object with content attribute
            if isinstance(event, dict):
                content = event.get('content', {})
                parts = content.get('parts', [])
                for part in parts:
                    if 'text' in part:
                        final_text += part['text']
                        print(part['text'], end="", flush=True)

        elapsed = time.perf_counter() - start
        print(f"\n\nLatency: {elapsed*1000:.0f}ms ({elapsed:.2f}s)")
    except Exception as e:
        print(f"streaming_agent_run_with_events() failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python test_agent.py local 'your query'")
        print("  python test_agent.py deployed 'your query' <resource_name>")
        sys.exit(1)

    mode = sys.argv[1]
    query = sys.argv[2] if len(sys.argv) > 2 else "What documents do you have?"

    if mode == "local":
        test_local(query)
    elif mode == "deployed":
        resource_name = sys.argv[3] if len(sys.argv) > 3 else os.environ.get("REASONING_ENGINE_RES")
        if not resource_name:
            print("Error: Provide resource_name or set REASONING_ENGINE_RES")
            sys.exit(1)
        test_deployed(query, resource_name)
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)
