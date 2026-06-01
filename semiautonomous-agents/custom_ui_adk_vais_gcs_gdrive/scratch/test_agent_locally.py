import asyncio
import os
import sys
import google.auth
import google.auth.transport.requests

# Add project root to path
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load dotenv to configure model wrapper
from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env", override=True)

from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
from agent.agent import root_agent

async def test_agent(query):
    # 1. Get token for admin@jesusarguelles.altostrat.com
    creds, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    token = creds.token
    
    print(f"Testing local agent as user: admin@jesusarguelles.altostrat.com")
    print(f"Query: '{query}'")
    
    runner = InMemoryRunner(agent=root_agent, app_name="adk-drive-ae")
    
    # 2. Initialize session with credentials
    session = await runner.session_service.create_session(
        app_name="adk-drive-ae",
        user_id="admin@jesusarguelles.altostrat.com",
        state={
            "drive_access_token": token,
            "temp:drive_access_token": token,
        },
    )
    
    # 3. Execute query
    content = Content(parts=[Part(text=query)], role="user")
    
    print("\n--- AGENT STREAM START ---")
    async for event in runner.run_async(
        user_id="admin@jesusarguelles.altostrat.com", 
        session_id=session.id, 
        new_message=content
    ):
        if not (event.content and event.content.parts):
            continue
        for part in event.content.parts:
            if part.function_call:
                fc = part.function_call
                print(f"\n[TOOL CALL] {fc.name}({dict(fc.args or {})})")
            if part.function_response:
                resp = part.function_response.response
                print(f"[TOOL RESPONSE] Returned {len(resp.get('results', []))} results")
            if part.text:
                print(part.text, end="", flush=True)
    print("\n--- AGENT STREAM END ---\n")

if __name__ == "__main__":
    q = "what was alphabet revenue?"
    asyncio.run(test_agent(q))
