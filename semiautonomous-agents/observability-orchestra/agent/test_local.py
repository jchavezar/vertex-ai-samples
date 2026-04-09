"""
Local testing script for Observability Orchestra.

Tests the multi-agent setup before deployment to Agent Engine.

Usage:
    python test_local.py
"""
import os
import asyncio
from dotenv import load_dotenv

# Load environment
load_dotenv(override=True)

# Set required environment variables
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "1")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Import the agent (this also registers Claude)
import agent

# Test queries - mix of direct answers and product research delegation
TEST_QUERIES = [
    # Direct answer (fast) - general question
    "What is Kubernetes?",

    # DELEGATION - Product research triggers both sub-agents
    "Product research for an AI code review tool",
]


async def test_agent():
    """Run test queries through the agent."""
    print(f"""
========================================
Local Agent Testing
========================================
Testing: Observability Orchestra
Models:
  - Orchestrator: {agent.ORCHESTRATOR_MODEL}
  - Claude: {agent.CLAUDE_MODEL}
  - Flash-Lite: {agent.FLASHLITE_MODEL}
========================================
""")

    # Create session service and runner
    session_service = InMemorySessionService()
    runner = Runner(
        agent=agent.root_agent,
        app_name="observability-orchestra-test",
        session_service=session_service,
    )

    # Create a session
    session = await session_service.create_session(
        app_name="observability-orchestra-test",
        user_id="test-user",
    )

    print(f"Session created: {session.id}\n")

    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"--- Query {i}/{len(TEST_QUERIES)} ---")
        print(f"User: {query}\n")

        # Create user message
        user_content = types.Content(
            role="user",
            parts=[types.Part(text=query)]
        )

        # Run the agent
        try:
            response_parts = []
            agent_names = []
            async for event in runner.run_async(
                session_id=session.id,
                user_id="test-user",
                new_message=user_content,
            ):
                # Track which agents respond
                if hasattr(event, "author"):
                    if event.author not in agent_names:
                        agent_names.append(event.author)
                        print(f"  [Agent: {event.author}]")

                # Collect response text
                if hasattr(event, "content") and event.content:
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            response_parts.append(part.text)

            response = "".join(response_parts)
            print(f"\nAgents involved: {agent_names}")
            print(f"Response length: {len(response)} chars")
            print(f"Response:\n{response}\n")

        except Exception as e:
            print(f"Error: {e}\n")

        print("=" * 50 + "\n")

    print("Testing complete!")


if __name__ == "__main__":
    asyncio.run(test_agent())
