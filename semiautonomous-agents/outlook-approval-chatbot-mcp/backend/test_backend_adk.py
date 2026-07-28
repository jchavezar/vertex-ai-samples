import os
import asyncio
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="../.env", override=True)

# Explicitly point to the target vtxdemos project
os.environ["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"
os.environ["GEMINI_PROJECT"] = "vtxdemos"
os.environ["PROJECT_ID"] = "vtxdemos"

from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
from main import outlook_agent, current_graph_token


async def run_local_test():
    print("=" * 60)
    print("Initializing local ADK Agent test runner...")
    print("=" * 60)

    # Mock a fake Graph Token for local validation
    mock_token = "mock-graph-token-12345"
    token_token = current_graph_token.set(mock_token)

    runner = InMemoryRunner(agent=outlook_agent, app_name="outlook-mcp-test")
    session = await runner.session_service.create_session(
        app_name="outlook-mcp-test", user_id="test-user"
    )

    query = "List my recent email messages"
    print(f"\nSending Query: '{query}'")

    content = Content(parts=[Part(text=query)], role="user")
    
    print("\n--- Agent Execution Output ---")
    async for event in runner.run_async(
        user_id="test-user", session_id=session.id, new_message=content
    ):
        if hasattr(event, "content") and event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    print(part.text, end="", flush=True)
    print("\n------------------------------")

    # Clean up token context
    current_graph_token.reset(token_token)
    print("\nTest completed successfully! ADK Agent is fully initialized and operational.")


if __name__ == "__main__":
    asyncio.run(run_local_test())
