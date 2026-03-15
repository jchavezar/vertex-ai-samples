import asyncio
from google.adk.events import Event
from google.genai import types
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService

async def main():
    agent = LlmAgent(name='test_agent', model='gemini-2.5-flash', instruction='say hello')
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name='test', user_id='default', session_id='123')
    
    # insert a dictionary into the session events directly, mimicking what might happen
    session.events.append({"role": "user", "content": "hi"})
    
    runner = Runner(app_name='test', agent=agent, session_service=session_service)
    msg_obj = types.Content(role='user', parts=[types.Part.from_text(text='how are you')])
    
    try:
        async for e in runner.run_async(user_id='default', session_id='123', new_message=msg_obj):
            print(e)
    except Exception as ex:
        import traceback
        traceback.print_exc()

asyncio.run(main())
