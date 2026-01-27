
import asyncio
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.getcwd())

from src.smart_agent import create_smart_agent
import google.adk as adk
from google.adk.sessions import InMemorySessionService
from google.genai import types

async def main():
    print("--- Starting Agent Loop Verification ---")
    load_dotenv()
    token = os.getenv("FACTSET_API_KEY", "mock_token")
    
    # Create Agent
    agent = await create_smart_agent(token)
    
    # Create Runner
    session_service = InMemorySessionService()
    runner = adk.Runner(app_name="test_app", agent=agent, session_service=session_service)
    
    session_id = "test_session_1"
    await session_service.create_session(session_id=session_id, user_id="test_user", app_name="test_app")
    
    query = "What is the price of Alphabet and Microsoft?"
    print(f"\nUser Query: {query}")
    
    msg = types.Content(role="user", parts=[types.Part(text=query)])
    
    print("\n--- Agent Response Stream ---")
    async for event in runner.run_async(user_id="test_user", session_id=session_id, new_message=msg):
        # adk events can be complicated, let's just print text content
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text, end="", flush=True)
                if part.function_call:
                    print(f"\n[Tool Call] {part.function_call.name}({part.function_call.args})")
        if event.tool_response:
             print(f"\n[Tool Result] {event.tool_response.name} completed.")
             
    print("\n\n--- End verification ---")

if __name__ == "__main__":
    asyncio.run(main())
