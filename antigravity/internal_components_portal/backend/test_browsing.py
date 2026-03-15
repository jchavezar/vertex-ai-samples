import asyncio
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path="../.env")

from agents.public_agent import get_public_agent
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types

import pytest

@pytest.mark.asyncio
async def test_browsing():
    agent = get_public_agent("gemini-2.5-flash")
    session_service = InMemorySessionService()
    await session_service.create_session(app_name="Public_Test", user_id="test", session_id="test")
    runner = Runner(app_name="Public_Test", agent=agent, session_service=session_service)
    
    msg = types.Content(role="user", parts=[types.Part.from_text(text="What is the latest news about Google Gemini?")])
    
    print("Starting research...")
    async for event in runner.run_async(user_id="test", session_id="test", new_message=msg):
        edata = event.model_dump()
        print(f"EVENT: {edata}")
        
if __name__ == "__main__":
    asyncio.run(test_browsing())
