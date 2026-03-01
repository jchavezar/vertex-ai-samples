import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
from agents.audit_agent.main import audit_agent
from google.adk.sessions import InMemorySessionService
from google.adk import Runner
from google.genai import types

async def test_audit():
    session_service = InMemorySessionService()
    runner = Runner(
        agent=audit_agent,
        session_service=session_service,
        app_name="verity_nexus",
        auto_create_session=True
    )
    
    user_msg = types.Content(role="user", parts=[types.Part(text="Perform a forensic audit on the ledger database. Focus on high-value outliers.")])
    
    print("Starting runner for audit_agent...")
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

if __name__ == "__main__":
    asyncio.run(test_audit())
