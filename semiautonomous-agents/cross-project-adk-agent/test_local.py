"""
Test the agent locally before deploying.

Usage:
    uv run python test_local.py
"""
import asyncio
from dotenv import load_dotenv

load_dotenv()

from google.adk.runners import InMemoryRunner
from agent import root_agent


async def test():
    runner = InMemoryRunner(agent=root_agent, app_name="cross-project-test")
    session = await runner.session_service.create_session(
        app_name="cross-project-test", user_id="test-user"
    )

    test_queries = [
        "What is Vertex AI Agent Engine?",
        "Explain the difference between Gemini Pro and Flash",
    ]

    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        print("=" * 50)

        from google.genai.types import Content, Part

        content = Content(parts=[Part(text=query)], role="user")
        async for event in runner.run_async(
            user_id="test-user", session_id=session.id, new_message=content
        ):
            if hasattr(event, "content") and event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        print(f"\nResponse: {part.text}")


if __name__ == "__main__":
    asyncio.run(test())
