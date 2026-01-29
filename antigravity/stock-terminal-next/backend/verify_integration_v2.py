import asyncio
import json
import secrets
from src.smart_agent import create_smart_agent
from google.adk.sessions import InMemorySessionService
from google.adk import Runner
from google.genai import types

async def test_high_impact_queries():
    print("\n=== SYSTEM INTEGRATION TEST: HIGH IMPACT QUERIES ===\n")
    
    # Use a dummy token to trigger fallbacks for local test efficiency
    token = "mock_token"
    agent = await create_smart_agent(token=token, model_name="gemini-2.5-flash")
    
    session_service = InMemorySessionService()
    runner = Runner(app_name="stock_terminal", agent=agent, session_service=session_service)
    
    sid = f"test_{secrets.token_hex(4)}"
    await session_service.create_session(session_id=sid, user_id="test_user", app_name="stock_terminal")

    queries = [
        "Initiate a full neural recon for NVDA: I need the latest headlines, fair value analysis, and a technical chart.",
        "What is the investability context for semiconductors? Switch to a sector overview with competitors."
    ]

    for query in queries:
        print(f"\n> QUERY: {query}")
        msg = types.Content(role="user", parts=[types.Part(text=query)])
        
        full_response = ""
        ui_commands_detected = []
        
        async for event in runner.run_async(user_id="test_user", session_id=sid, new_message=msg):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        text = part.text
                        full_response += text
                        if "[UI_COMMAND]" in text:
                            # Extract command
                            start = text.find("[UI_COMMAND]") + 12
                            end = text.find("[/UI_COMMAND]")
                            cmd_str = text[start:end]
                            try:
                                ui_commands_detected.append(json.loads(cmd_str))
                            except: pass

        print(f"Response Preview: {full_response[:200]}...")
        print(f"UI Commands Found: {len(ui_commands_detected)}")
        for cmd in ui_commands_detected:
            print(f"  - Type: {cmd.get('type')} | View: {cmd.get('viewMode') or cmd.get('view')}")

if __name__ == "__main__":
    asyncio.run(test_high_impact_queries())
