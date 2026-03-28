"""
Local test script for the Cloud Portal Agent.
Tests the agent using AdkApp locally before deploying to Agent Engine.
This avoids long deployment cycles.

Usage:
    uv run python test_local.py
"""
import asyncio
import os
import sys
import json

# Set up environment
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("GOOGLE_CLOUD_PROJECT", "deloitte-plantas")
os.environ["GOOGLE_CLOUD_LOCATION"] = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

# Ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

import vertexai
from vertexai.agent_engines import AdkApp
from google.adk.sessions import InMemorySessionService

# Initialize Vertex AI
vertexai.init(
    project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
    location=os.environ.get("GOOGLE_CLOUD_LOCATION")
)

# Import our agent
from agent import root_agent

# Create shared session service with initial state support
session_service = InMemorySessionService()


async def test_agent(user_token: str = None):
    """Test the agent locally using AdkApp.async_stream_query"""
    print("=" * 60)
    print("Local Agent Test - Cloud Portal Assistant")
    print("=" * 60)

    app_name = "cloud_portal_test"
    user_id = "test-user"

    # Create session with initial state (including USER_TOKEN if provided)
    initial_state = {}
    if user_token:
        initial_state["USER_TOKEN"] = user_token
        print(f"[Test] Using USER_TOKEN (length: {len(user_token)})")
    else:
        print("[Test] No USER_TOKEN provided - service account will be used")

    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        state=initial_state
    )
    session_id = session.id
    print(f"[Test] Created session: {session_id}")
    print(f"[Test] Session state keys: {list(session.state.keys())}")

    # Create AdkApp wrapper with our session service
    app = AdkApp(
        agent=root_agent,
        enable_tracing=False,
        session_service_builder=lambda: session_service,
    )

    # Test queries
    test_queries = [
        "What is the salary of a CFO?",
        # "List my open incidents",
        # "Tell me more about the CFO compensation",
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print("-" * 60)

        try:
            # Use async_stream_query to stream responses
            chunks = []
            async for event in app.async_stream_query(
                message=query,
                user_id=user_id,
                session_id=session_id,
            ):
                # Print event info
                if isinstance(event, dict):
                    # Extract text content
                    content = event.get("content", {})
                    if isinstance(content, dict):
                        parts = content.get("parts", [])
                        for part in parts:
                            if isinstance(part, dict) and part.get("text"):
                                text = part["text"]
                                print(text, end="", flush=True)
                                chunks.append(text)

                    # Check for tool calls
                    if event.get("tool_calls"):
                        print(f"\n[Tool Call: {event['tool_calls']}]")

                    # Check for tool results
                    if event.get("tool_response"):
                        print(f"\n[Tool Response received]")

            print()  # Newline after streaming

            if not chunks:
                print("[No text response received]")
                print(f"Raw event: {json.dumps(event, indent=2, default=str)[:500]}")

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'='*60}")
    print("Test complete!")
    print(f"Session ID: {session_id}")


async def test_single_query(query: str, user_token: str = None):
    """Test a single query interactively."""
    print(f"Testing: {query}")
    print("-" * 40)

    user_id = "test-user"

    # Create AdkApp
    app = AdkApp(
        agent=root_agent,
        enable_tracing=False,
    )

    # Create session with USER_TOKEN in state if provided
    initial_state = {}
    if user_token:
        initial_state["USER_TOKEN"] = user_token
        print(f"[Test] USER_TOKEN provided (length: {len(user_token)})")
    else:
        print("[Test] No USER_TOKEN - using service account credentials")

    # Create session with initial state
    session = await app.async_create_session(
        user_id=user_id,
        state=initial_state
    )
    print(f"[Test] Session ID: {session.id}")

    # Query with the session
    async for event in app.async_stream_query(
        message=query,
        user_id=user_id,
        session_id=session.id,
    ):
        if isinstance(event, dict):
            content = event.get("content", {})
            if isinstance(content, dict):
                parts = content.get("parts", [])
                for part in parts:
                    if isinstance(part, dict) and part.get("text"):
                        print(part["text"], end="", flush=True)
    print()


if __name__ == "__main__":
    # Check for USER_TOKEN environment variable
    user_token = os.environ.get("USER_TOKEN")

    if len(sys.argv) > 1:
        # Run with custom query
        query = " ".join(sys.argv[1:])
        asyncio.run(test_single_query(query, user_token=user_token))
    else:
        # Run full test suite
        asyncio.run(test_agent(user_token=user_token))
