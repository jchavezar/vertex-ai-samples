import os
import asyncio
import google.adk as adk
from google.genai.types import Content, Part
from google.adk.sessions import InMemorySessionService
from dotenv import load_dotenv

load_dotenv()

async def test_adk():
    print("Starting ADK test...")
    agent = adk.Agent(
        name="test_agent",
        model="gemini-2.0-flash-001",
        instruction="Be a helpful assistant."
    )
    
    session_service = InMemorySessionService()
    runner = adk.Runner(
        app_name="test_app",
        agent=agent,
        session_service=session_service
    )

    new_message = Content(parts=[Part(text="Hello, how are you?")])
    
    await session_service.create_session(
        session_id="test_session",
        app_name=runner.app_name,
        user_id="user_1"
    )

    print("Running runner.run_async...")
    async for event in runner.run_async(
        user_id="user_1",
        session_id="test_session",
        new_message=new_message
    ):
        if event.content:
            print(f"Event content: {event.content}")
    print("Test finished successfully.")

if __name__ == "__main__":
    asyncio.run(test_adk())
