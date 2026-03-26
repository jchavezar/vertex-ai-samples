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
from agents.router_agent import get_router_agent

logging.basicConfig(level=logging.INFO)

async def main():
    print("Initializing Runner for Router agent...")
    session_service = InMemorySessionService()
    
    # Get router agent
    router_agent = get_router_agent()
    
    # Create session first
    session_id = "test-session-router"
    await session_service.create_session(app_name="light_portal_router", user_id="default_user", session_id=session_id)
    
    runner = Runner(app_name="light_portal_router", agent=router_agent, session_service=session_service)
    
    # Simulate a query
    print("\nTest 1: Search query")
    msg_obj = types.Content(role="user", parts=[types.Part.from_text(text="What is the weather in Delhi?")])
    stream = runner.run_async(user_id="default_user", session_id=session_id, new_message=msg_obj)
    async for event in stream:
        pass # Router might not print text directly, it sets state
        
    session = await session_service.get_session(app_name="light_portal_router", user_id="default_user", session_id=session_id)
    print(f"Router Classification (Search): {session.state.get('router_classification')}")

    print("\nTest 2: ServiceNow query")
    # Reset session for fresh test or use new ID
    session_id_2 = "test-session-router-2"
    await session_service.create_session(app_name="light_portal_router", user_id="default_user", session_id=session_id_2)
    
    msg_obj_2 = types.Content(role="user", parts=[types.Part.from_text(text="List ServiceNow incidents")])
    stream_2 = runner.run_async(user_id="default_user", session_id=session_id_2, new_message=msg_obj_2)
    async for event in stream_2:
        pass
        
    session_2 = await session_service.get_session(app_name="light_portal_router", user_id="default_user", session_id=session_id_2)
    print(f"Router Classification (ServiceNow): {session_2.state.get('router_classification')}")

if __name__ == "__main__":
    asyncio.run(main())
