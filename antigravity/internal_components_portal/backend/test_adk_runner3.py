from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.genai import types
from google.adk.events import Event
from google.adk.sessions.in_memory_session_service import InMemorySessionService
import asyncio
import traceback

async def test():
    try:
        ss = InMemorySessionService()
        sess = await ss.create_session(app_name="app", user_id="default", session_id="123")
        
        agent = LlmAgent(name="test", model="gemini-2.5-flash", instruction="test")
        runner = Runner(app_name="app", agent=agent, session_service=ss)
        
        # Add history where content is a dict!
        content_dict = {"role": "user", "parts": [{"text": "What is 1+1?"}]}
        evt = Event(author="user", content=content_dict)
        sess.events.append(evt)
        await ss.append_event(sess, evt)
        
        # Run
        msg_obj = types.Content(role="user", parts=[types.Part.from_text(text="And what is 2+2?")])
        print("Running...")
        async for e in runner.run_async(user_id="default", session_id="123", new_message=msg_obj):
            print("Event author:", getattr(e, "author", None))
    except Exception as e:
        print("CRASHED:", str(e))

if __name__ == "__main__":
    import os
    os.environ["GOOGLE_API_KEY"] = "fake"  # to avoid the other crash
    asyncio.run(test())
