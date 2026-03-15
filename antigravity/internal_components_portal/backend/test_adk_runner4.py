from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.genai import types
from google.adk.events import Event
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.agents.callback_context import CallbackContext
import asyncio
import traceback

async def test():
    try:
        ss = InMemorySessionService()
        sess = await ss.create_session(app_name="app", user_id="default", session_id="123")
        
        async def before_run(**kwargs):
            return types.Content(role="model", parts=[types.Part.from_text(text="Stop")]) 
            
        agent = LlmAgent(name="test", model="gemini-2.5-flash", instruction="test", 
                         before_agent_callback=before_run)
                         
        runner = Runner(app_name="app", agent=agent, session_service=ss)
        
        msg_obj = types.Content(role="user", parts=[types.Part.from_text(text="And what is 2+2?")])
        print("Running...")
        async for e in runner.run_async(user_id="default", session_id="123", new_message=msg_obj):
            print("Event author:", getattr(e, "author", None))
    except Exception as e:
        print("CRASHED:", str(e))
        traceback.print_exc()

if __name__ == "__main__":
    import os
    os.environ["GOOGLE_API_KEY"] = "fake"
    asyncio.run(test())
