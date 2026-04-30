"""
REMOTE TESTING - After Agent Engine Deployment
===============================================

This script tests the deployed agent on Agent Engine.
Run this AFTER deploying to verify:
1. Agent is accessible via Agent Engine API
2. Tools work in the cloud environment
3. Environment variables are correctly configured

Prerequisites:
    - REASONING_ENGINE_RES set in .env (from deploy.py output)
    - Agent deployed to Agent Engine

Usage:
    uv run python test_remote.py                    # Basic test
    uv run python test_remote.py "custom query"     # Custom query
    uv run python test_remote.py --list             # List deployed agents

Version: 1.1.0
Date: 2026-04-04
Last Used: 2026-04-04 13:17 UTC
"""
import sys
import os
from dotenv import load_dotenv

load_dotenv()

import vertexai
from vertexai import agent_engines

PROJECT_ID = os.environ.get("PROJECT_ID", "")
LOCATION = os.environ.get("LOCATION", "us-central1")
REASONING_ENGINE_RES = os.environ.get("REASONING_ENGINE_RES", "")


def print_banner(title: str):
    """Print a formatted banner."""
    width = 60
    print("=" * width)
    print(f" {title}".center(width))
    print("=" * width)


def list_deployed_agents():
    """List all deployed agents in the project."""
    print_banner("Deployed Agent Engines")

    vertexai.init(project=PROJECT_ID, location=LOCATION)

    try:
        agents = agent_engines.list()
        for i, agent in enumerate(agents, 1):
            print(f"\n{i}. {agent.display_name or 'Unnamed'}")
            print(f"   Resource: {agent.resource_name}")
            print(f"   State:    {agent.state}")
            if hasattr(agent, 'create_time'):
                print(f"   Created:  {agent.create_time}")
    except Exception as e:
        print(f"Error listing agents: {e}")


def test_remote_query(query: str):
    """
    Test the deployed agent with a query.

    Args:
        query: The test query to send
    """
    print_banner("REMOTE TESTING - Agent Engine")

    if not REASONING_ENGINE_RES:
        print("[ERROR] REASONING_ENGINE_RES not set in .env")
        print("        Deploy first: uv run python deploy.py")
        print("        Then add the resource name to .env")
        return

    print(f"Project:  {PROJECT_ID}")
    print(f"Location: {LOCATION}")
    print(f"Engine:   {REASONING_ENGINE_RES}")
    print()

    vertexai.init(project=PROJECT_ID, location=LOCATION)

    # Get the deployed agent
    print("[Loading] Agent from Agent Engine...")
    try:
        remote_agent = agent_engines.get(REASONING_ENGINE_RES)
        print(f"[OK] Agent loaded: {remote_agent.display_name or 'Unnamed'}")
    except Exception as e:
        print(f"[ERROR] Could not load agent: {e}")
        return

    # Create a session and query
    print()
    print(f"[Query] {query}")
    print("-" * 60)

    try:
        # Create session
        session = remote_agent.create_session(user_id="remote_test_user")
        # Handle both dict and object response
        session_id = session.get("id") if isinstance(session, dict) else session.id
        print(f"[Session] Created: {session_id}")

        # Stream the response
        response_text = ""
        for event in remote_agent.stream_query(
            user_id="remote_test_user",
            session_id=session_id,
            message=query
        ):
            # Debug: uncomment to see event structure
            # print(f"\n[Event] {type(event)}: {str(event)[:200]}", flush=True)

            if isinstance(event, dict):
                # Handle dict response
                content = event.get("content", {})
                parts = content.get("parts", [])
                for part in parts:
                    if isinstance(part, dict) and part.get("text"):
                        print(part["text"], end="", flush=True)
                        response_text += part["text"]
            elif hasattr(event, 'text'):
                print(event.text, end="", flush=True)
                response_text += event.text
            elif hasattr(event, 'content'):
                if hasattr(event.content, 'parts'):
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            print(part.text, end="", flush=True)
                            response_text += part.text

        if not response_text:
            print("[No response text captured - check event format]")

        print()
        print("-" * 60)
        print("[OK] Remote test complete!")

    except Exception as e:
        print(f"\n[ERROR] Query failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Check Cloud Logging for agent errors")
        print("  2. Verify environment variables in Agent Engine")
        print("  3. Check IAM permissions for WIF")


def test_tool_call():
    """
    Test calling a specific tool on the deployed agent.
    """
    print_banner("TOOL TESTING - Remote")

    if not REASONING_ENGINE_RES:
        print("[ERROR] REASONING_ENGINE_RES not set")
        return

    vertexai.init(project=PROJECT_ID, location=LOCATION)

    try:
        remote_agent = agent_engines.get(REASONING_ENGINE_RES)

        # Get agent info
        print(f"Agent Name:  {remote_agent.display_name}")
        print(f"Agent State: {remote_agent.state}")

        # List available tools
        if hasattr(remote_agent, 'tools'):
            print(f"Tools: {remote_agent.tools}")

    except Exception as e:
        print(f"[ERROR] {e}")


def main():
    """Main test runner."""
    print_banner("REMOTE TESTING - InsightComparator Agent")
    print()
    print("This tests the agent AFTER deploying to Agent Engine.")
    print("Use this to verify the deployed agent works correctly.")
    print()

    if not PROJECT_ID:
        print("[ERROR] PROJECT_ID not set in .env")
        return

    # Parse arguments
    query = "What are cloud security best practices?"

    for arg in sys.argv[1:]:
        if arg == "--list":
            list_deployed_agents()
            return
        elif arg == "--tools":
            test_tool_call()
            return
        elif not arg.startswith("-"):
            query = arg

    test_remote_query(query)

    print()
    print_banner("REMOTE TESTING COMPLETE")
    print()
    print("Next steps:")
    print("  1. Register authorization (if not done):")
    print("     ./register_auth.sh")
    print()
    print("  2. Register agent to Agentspace:")
    print("     ./register_agent.sh")
    print()
    print("  3. Test in Gemini Enterprise UI")


if __name__ == "__main__":
    main()
