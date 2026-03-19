import os
import sys
import asyncio

# Add current directory to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from dotenv import load_dotenv

load_dotenv()

from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agents.orchestrator.main import orchestrator

async def main():
    # DEBUG: Check if sub-agents are registered
    print(f"Orchestrator Name: {orchestrator.name}")
    print(f"Registered Sub-agents: {[a.name for a in (orchestrator.sub_agents or [])]}")
    
    runner = Runner(
        agent=orchestrator, 
        session_service=InMemorySessionService(), 
        app_name="verity_nexus",
        auto_create_session=True
    )


    user_msg = types.Content(role="user", parts=[types.Part(text="Analyze the ledger for anomalies.")])
    print("Starting runner loop...")
    try:
        async for event in runner.run_async(new_message=user_msg, user_id="test_user", session_id="test_session"):
            print(f"\n--- [EVENT] Author: {getattr(event, 'author', 'None')}")
            if hasattr(event, 'content') and event.content:
                 for part in event.content.parts:
                     if hasattr(part, 'text') and part.text:
                         print(f"  TEXT: {part.text}")
                     if hasattr(part, 'function_call') and part.function_call:
                         print(f"  CALL: {part.function_call}")
                     if hasattr(part, 'function_response') and part.function_response:
                         print(f"  RESP: {part.function_response}")
            if hasattr(event, "actions") and event.actions:
                print(f"  ACTIONS: {event.actions}")
            if hasattr(event, "output") and event.output:
                print(f"  OUTPUT: {event.output}")
    except Exception as e:
        print(f"EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
