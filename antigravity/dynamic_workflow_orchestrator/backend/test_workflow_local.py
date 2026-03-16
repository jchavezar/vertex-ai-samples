
import asyncio
import json
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from workflow_agent import root_agent

import os

# Force Vertex AI usage
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
os.environ["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

async def test_full_workflow():
    session_service = InMemorySessionService()
    APP_NAME = "test_app"
    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
    
    user_id = "user_1"
    session_id = "sess_1"
    
    # Create session
    await session_service.create_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)
    
    print("\n=== STEP 1: START WORKFLOW ===")
    input_text = "SpaceX is planning to launch a new rocket next week. It will carry satellites for Starlink."
    content = types.Content(role='user', parts=[types.Part(text=input_text)])
    state_delta = {"input_text": input_text, "workflow_step": "start", "user_decision": None}
    
    events = runner.run_async(user_id=user_id, session_id=session_id, new_message=content, state_delta=state_delta)
    async for event in events:
        text = event.content.parts[0].text if event.content and event.content.parts else ""
        print(f"[{event.author}] (id={event.id}): {text[:100]}...")

    # Check state after Step 1
    session = await session_service.get_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)
    print(f"\nState after Step 1: {session.state}")
    
    print("\n=== STEP 2: CONTINUE WITH YES ===")
    content = types.Content(role='user', parts=[types.Part(text="Yes")])
    # Runner handles adding this message to session history.
    # In local server, we pass state_delta["user_decision"] = "Yes"
    state_delta = {"user_decision": "Yes"}
    
    events = runner.run_async(user_id=user_id, session_id=session_id, new_message=content, state_delta=state_delta)
    async for event in events:
        text = event.content.parts[0].text if event.content and event.content.parts else ""
        print(f"[{event.author}] (id={event.id}): {text[:100]}...")

    # Check final state
    session = await session_service.get_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)
    print(f"\nFinal State: {session.state}")

if __name__ == "__main__":
    asyncio.run(test_full_workflow())
