"""Debug script to test agent tool invocation"""
import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

# Get JWT from environment or test UI
JWT = os.environ.get("TEST_JWT", "")
AUTH_ID = os.environ.get("AUTH_ID", "sharepointauth")

async def test():
    from google.adk.sessions import InMemorySessionService
    from google.adk.runners import Runner
    from google.genai.types import Content, Part
    from agent import root_agent

    print("=" * 60)
    print("Agent info:")
    print(f"  Name: {root_agent.name}")
    print(f"  Model: {root_agent.model}")
    print(f"  Tools: {[t.__name__ if hasattr(t, '__name__') else str(t) for t in root_agent.tools]}")
    print(f"  Instruction (first 200):\n{root_agent.instruction[:200]}...")
    print("=" * 60)

    session_service = InMemorySessionService()
    # Use key WITHOUT temp: prefix for local testing
    # (temp: keys are runtime-only in Agentspace, not stored in session state)
    token_key = AUTH_ID

    await session_service.create_session(
        app_name="test",
        user_id="test",
        session_id="test",
        state={token_key: JWT},
    )
    print(f"Session created with state key: {token_key}")

    runner = Runner(agent=root_agent, app_name="test", session_service=session_service)
    query = "what is the salary of a cfo?"
    content = Content(role="user", parts=[Part(text=query)])

    print(f"\nQuery: {query}")
    print("=" * 60)
    print("Running agent (watching for events)...")

    async for event in runner.run_async(user_id="test", session_id="test", new_message=content):
        event_type = type(event).__name__
        print(f"[EVENT] {event_type}")

        # Check if it's a tool call
        if hasattr(event, 'function_calls') and event.function_calls:
            for fc in event.function_calls:
                print(f"  -> TOOL CALL: {fc.name}({fc.args})")

        if event.is_final_response():
            print(f"\n[FINAL] {event.content.parts[0].text if event.content and event.content.parts else 'No content'}")

if __name__ == "__main__":
    asyncio.run(test())
