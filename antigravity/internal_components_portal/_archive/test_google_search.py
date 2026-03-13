import asyncio
import os
from google.adk.agents import LlmAgent
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"

async def main():
    agent = LlmAgent(
        name="TestAgent",
        model="gemini-2.5-flash",
        instruction="Use the Google Search Tool to look up SpaceX. Respond with bullet points.",
        tools=[GoogleSearchTool()]
    )
    
    session_service = InMemorySessionService()
    runner = Runner(app_name="TestApp", agent=agent, session_service=session_service)
    
    await session_service.create_session(app_name="TestApp", user_id="test_user", session_id="session1")
    
    msg = types.Content(role="user", parts=[types.Part.from_text(text="What is the latest news on SpaceX? Use the google search tool.")])
    
    async for event in runner.run_async(user_id="test_user", session_id="session1", new_message=msg):
        if event.content and event.content.parts:
             for part in event.content.parts:
                  if part.function_call:
                       print(f"Tool call: {part.function_call.name}({part.function_call.args})")
                  if part.function_response:
                       print(f"Tool response size: {len(str(part.function_response.response))}")
                  if part.text:
                       print(f"Text: {part.text}")

if __name__ == "__main__":
    asyncio.run(main())
