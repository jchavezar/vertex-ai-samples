import asyncio
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_LOCATION"] = "global"

from dotenv import load_dotenv
import os
load_dotenv(dotenv_path="../.env")
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_LOCATION"] = "global"

from public_agent import get_public_agent
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types

async def main():
    service = InMemorySessionService()
    runner = Runner(app_name="test", agent=get_public_agent(), session_service=service)
    msg = types.Content(role="user", parts=[types.Part.from_text(text="competitor salaries out there")])
    await service.create_session(app_name="test", user_id="u", session_id="s")
    
    async for e in runner.run_async(user_id="u", session_id="s", new_message=msg):
        print(type(e))
        print(e.model_dump())

if __name__ == "__main__":
    asyncio.run(main())
