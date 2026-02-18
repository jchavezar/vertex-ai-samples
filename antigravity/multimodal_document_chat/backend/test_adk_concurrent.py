import asyncio
import time
import uuid
import sys
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest
from google.genai import types

import os
from dotenv import load_dotenv
import vertexai

load_dotenv(dotenv_path="../.env")
os.environ["GOOGLE_CLOUD_LOCATION"] = os.environ.get("LOCATION", "us-central1")
os.environ["GOOGLE_GENAI_LOCATION"] = os.environ.get("LOCATION", "us-central1")
os.environ["GOOGLE_CLOUD_PROJECT"] = os.environ.get("PROJECT_ID", "")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
vertexai.init(project=os.environ.get("PROJECT_ID"), location=os.environ.get("LOCATION", "us-central1"))
def create_mock_agent(i):
    return LlmAgent(
        name=f"test_agent_{i}",
        model="gemini-2.5-flash",
        instruction="Reply exactly with: 'Hello from page'"
    )

async def run_single(agent, session_service, i, sem):
    async with sem:
        session_id = str(uuid.uuid4())
        await session_service.create_session(user_id="system", session_id=session_id, app_name="test", state={})
        runner = Runner(agent=agent, session_service=session_service, app_name="test")
        content = types.Content(role="user", parts=[types.Part.from_text(text="Test")])
        
        start = time.time()
        res = ""
        try:
            async for event in runner.run_async(user_id="system", session_id=session_id, new_message=content):
                if event.is_final_response() and event.content and event.content.parts:
                    res = event.content.parts[0].text
        except Exception as e:
            res = f"Error: {e}"
        end = time.time()
        print(f"Task {i} took {end - start:.2f} seconds. Result: {res}")

async def main():
    service = InMemorySessionService()
    sem = asyncio.Semaphore(25)
    tasks = []
    
    start_total = time.time()
    for i in range(10):
        agent = create_mock_agent(i)
        tasks.append(run_single(agent, service, i, sem))
        
    await asyncio.gather(*tasks)
    print(f"Total time for 10 tasks: {time.time() - start_total:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
