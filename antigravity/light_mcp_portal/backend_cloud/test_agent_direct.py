import os
import asyncio
import logging
from google.adk.runners import Runner
from google.genai import types

from dotenv import load_dotenv

# Fix path to load agents
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load .env
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"))

from google.adk.sessions import InMemorySessionService
from agents.agent import root_agent

logging.basicConfig(level=logging.INFO)

async def main():
    print("Initializing Runner for ServiceNow agent...")
    session_service = InMemorySessionService()
    # Create session first to avoid SessionNotFoundError
    session_id = "test-session-direct"
    await session_service.create_session(app_name="test_servicenow_agent", user_id="default_user", session_id=session_id)
    
    runner = Runner(app_name="test_servicenow_agent", agent=root_agent, session_service=session_service)
    
    # Simulate a query
    print("Running query: List ServiceNow incidents")
    msg_obj = types.Content(role="user", parts=[types.Part.from_text(text="List ServiceNow incidents")])
    
    # Run
    stream = runner.run_async(user_id="default_user", session_id=session_id, new_message=msg_obj)
    async for event in stream:
        if event.text:
            print(event.text, end="")
    print("\nDone!")

if __name__ == "__main__":
    asyncio.run(main())
