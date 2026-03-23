import sys
import os
import asyncio

backend_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(backend_dir)

# Read real token
token_path = os.path.join(backend_dir, "scratch", "real_token.txt")
with open(token_path, "r") as f:
    token = f.read().strip()

# Set env for local fallback
os.environ["USER_TOKEN"] = token
os.environ["SHAREPOINT_MCP_URL"] = "" # Force local stdio for test stability

from agents.agent import get_agent_with_mcp_tools
from google.adk.runners import Runner

async def main():
    print("🚀 Initializing Agent with Real Entra ID Token execution frame...")
    try:
        agent, exit_stack = await get_agent_with_mcp_tools()
    except Exception as e:
        print(f"❌ Failed to load agent/tools: {e}")
        return

    print("\n🕵️ Running Agent query: 'List files in SharePoint'...")
    from google.adk.sessions.in_memory_session_service import InMemorySessionService
    runner = Runner(agent=agent, app_name="test_mcp_app", session_service=InMemorySessionService())

    from google.genai import types
    msg_obj = types.Content(role="user", parts=[types.Part.from_text(text="List items or files in the SharePoint drive root")])
    
    try:
        # Pre-create session so run_async finds it
        await runner.session_service.create_session(user_id="default_user", app_name="test_mcp_app", session_id="test_session")
        
        # Use run_async which streams events
        async for event in runner.run_async(user_id="default_user", session_id="test_session", new_message=msg_obj):

            # Check the design structure of returned logs
            if hasattr(event, "content") and event.content:
                 if hasattr(event.content, "parts"):
                      for part in event.content.parts:
                           if hasattr(part, "text") and part.text:
                                print(f"[{event.author or 'Model'}]: {part.text}")
                           elif hasattr(part, "thought") and part.thought:
                                print(f"🤔 Thought: {part.thought}")
            elif hasattr(event, "status"):
                 print(f"📌 Status: {event.status}")
                 
    except Exception as e:
         import traceback
         print(f"❌ Execution error: {e}")
         print(traceback.format_exc())
    finally:
         await exit_stack.aclose()
         print("\n🏁 Session closed.")


if __name__ == "__main__":
    asyncio.run(main())
