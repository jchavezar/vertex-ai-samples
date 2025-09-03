#%%
import asyncio
import os
import time
from dotenv import load_dotenv
load_dotenv(verbose=True, override=True)
from utils import Grounding
from google.genai import types
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

session_service = InMemorySessionService()
grounding = Grounding(
    refresh_token=os.getenv("REFRESH_TOKEN"),
    token_url=os.getenv("TOKEN_URL"),
    endpoint_url=os.getenv("ENDPOINT_URL")
)

def agent(direct: bool = True):
    return Agent(
        name="root_agent",
        model="gemini-2.5-flash",
        description=(
            "Agent to answer questions about any financial figure"
        ),
        instruction=(
            """
            Use the `grounding_service_tool` tool to get any information relevant to user's original query.
            - **IMPORTANT** If you dont understand something trying to figure it out with your `grounding_service_tool` tool.
            - You can use the tool many times if you need until you fulfill the original query.
            
            -- Rules: --
            There are situations where your answer has many chunks e.g. different companies, different years, etc, get the
            chunks and the links from grounding_service_tool and structure the output in the following day.
            It's not companies only, it could be whatever figure but use your imagination without any hallucination for
            a correct representation of your tool output.
            -- end of rules --
            
            -- Expected Output Structure: --
            Summary:
            Response with details without hallucinations. Nice view format output.
            
            Sources:
            - company_1: url_link
            - company_2: url_link
            - company_n: url_link
            -- end --
            """
        ),
        tools=[grounding.direct_api_call if direct else grounding.enterprise_grounding_api_call]
    )

APP_NAME="grounding"
USER_ID="user1"
SESSION_ID="session1"


async def send_question(prompt: str, direct: bool = True):
    global final_response_content
    runner = Runner(agent=agent(direct=direct), app_name=APP_NAME, session_service=session_service)
    session = await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    user_content = types.Content(
        role="user", parts=[types.Part(text=prompt)]
    )
    start_time = time.time()
    async for event in runner.run_async(
            user_id=USER_ID, session_id=SESSION_ID, new_message=user_content
    ):
        try:
            if event.is_final_response() and event.content and event.content.parts:
                final_response_content = event.content.parts[0].text
        except Exception as e:
            final_response_content = f"Error: {e}"

    return final_response_content, time.time()-start_time
