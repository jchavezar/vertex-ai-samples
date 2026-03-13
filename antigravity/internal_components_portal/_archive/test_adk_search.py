import asyncio
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.tools import google_search
from google.adk.sessions import InMemorySessionService

async def main():
    agent = LlmAgent(name="test", model="gemini-2.5-flash", instruction="Use google search.", tools=[google_search])
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, app_name="test_app", session_service=session_service)
    async for event in runner.run_async(user_id="u1", session_id="s1", new_message="What are the latest Google AI announcements?"):
        print("====== EVENT ======")
        print(event.model_dump())

asyncio.run(main())
