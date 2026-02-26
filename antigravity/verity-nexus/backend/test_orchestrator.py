import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
from agents.orchestrator.main import orchestrator
from google.adk.sessions import InMemorySessionService
from google.adk import Runner
from google.genai import types

async def test_orchestrator():
    session_service = InMemorySessionService()
    runner = Runner(
        agent=orchestrator,
        session_service=session_service,
        app_name="verity_nexus",
        auto_create_session=True
    )
    
    user_msg = types.Content(role="user", parts=[types.Part(text="Perform a forensic audit on the Q4 transaction set. Focus on high-value outliers.")])
    
    print("Starting runner...")
    async for event in runner.run_async(new_message=user_msg, user_id="test_user", session_id="test_session"):
        print(f"\n--- Event from {event.author} ---")
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(f"TEXT: {part.text}")
                if part.function_call:
                    print(f"FUNCTION CALL: {part.function_call.name}({part.function_call.args})")
                if part.function_response:
                    print(f"FUNCTION RESPONSE: {part.function_response.name} -> {part.function_response.response}")
        if event.actions:
            if event.actions.transfer_to_agent:
                print(f"TRANSFER TO AGENT: {event.actions.transfer_to_agent}")
            if event.actions.escalate:
                print(f"ESCALATE: {event.actions.escalate}")
            if event.actions.end_of_agent:
                print(f"END OF AGENT: {event.actions.end_of_agent}")

if __name__ == "__main__":
    asyncio.run(test_orchestrator())
