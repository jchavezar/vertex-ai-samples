
import asyncio
import os
import json
from dotenv import load_dotenv

# Load env from parent if needed, or current
load_dotenv()

from src.factset_core import check_factset_health, google_search, get_current_datetime
from src.smart_agent import create_smart_agent
import google.adk as adk
from google.genai.types import Content, Part
from google.adk.sessions import InMemorySessionService

async def main():
    print("--- STARTING STANDALONE FACTSET TEST ---")
    
    # 1. Check Env
    token = os.getenv("FS_CLIENT_ID") # Just checking if we have *something*, though real token comes from OAuth workflow usually.
    # Actually, in this app, the token is stored in `factset_tokens.json` managed by `main.py`.
    # We should try to load it from there to be realistic.
    
    token_file = "factset_tokens.json"
    active_token = None
    
    if os.path.exists(token_file):
        try:
            with open(token_file, 'r') as f:
                tokens = json.load(f)
                # Just take the first one or a default
                if "default_chat" in tokens:
                    active_token = tokens["default_chat"].get("token")
                    print(f"Found token for default_chat: {active_token[:10]}...")
                else:
                    print("No default_chat token in file.")
        except Exception as e:
            print(f"Error reading token file: {e}")
    else:
        print("No token file found. Will run in MOCK mode or fail if strict.")

    # 2. Test create_smart_agent
    print(f"\nCreating Smart Agent (Token: {'YES' if active_token else 'NO/Mock'})...")
    agent = await create_smart_agent(token=active_token, model_name="gemini-3-flash-preview")
    
    print(f"Agent Created: {agent.name}")
    print(f"Tools: {[t.__name__ for t in agent.tools]}")
    
    # 3. Simple Run - "What is the stock price of Apple?"
    # This tests the router and the tool execution.
    print("\n--- RUNNING QUERY: 'What is the stock price of Apple?' ---")
    
    session_service = InMemorySessionService()
    runner = adk.Runner(app_name="test_app", agent=agent, session_service=session_service)
    session_id = "test_session_1"
    await session_service.create_session(session_id=session_id, app_name="test_app", user_id="tester")
    
    msg = Content(role="user", parts=[Part(text="What is the stock price of Apple today include a chart?")])
    
    async for event in runner.run_async(user_id="tester", session_id=session_id, new_message=msg):
        # We just print what happens
        if hasattr(event, "get_function_calls"):
            fcalls = event.get_function_calls()
            if fcalls:
                for fc in fcalls:
                    print(f"[TOOL CALL] {fc.name} args={fc.args}")
        
        if event.content:
            text = event.content.parts[0].text if event.content.parts else ""
            if text:
                print(f"[TEXT] {text[:100]}...")
                
    print("\n--- TEST COMPLETE ---")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupted")
    except Exception as e:
        print(f"FATAL ERROR: {e}")
