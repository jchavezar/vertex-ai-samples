#%%
import os
from google.genai import types
from typing import AsyncGenerator
from google.adk.tools import google_search
from google.adk.runners import Runner
from google.cloud import modelarmor_v1
from google.adk.tools import ToolContext
from google.adk.events import Event, EventActions
from google.adk.sessions import InMemorySessionService
from google.adk.agents import SequentialAgent, LlmAgent, BaseAgent
from google.adk.agents.invocation_context import InvocationContext


import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

project = "jesusarguelles-sandbox"
location = "us-central1"

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
os.environ["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

client = modelarmor_v1.ModelArmorClient(transport="rest", client_options = {"api_endpoint" : "modelarmor.us.rep.googleapis.com"})

def guardrail_check(prompt: str, tool_context: ToolContext) -> str:
    tool_context.state["original_query"] = prompt
    user_prompt_data = modelarmor_v1.DataItem()
    user_prompt_data.text = prompt

    request = modelarmor_v1.SanitizeUserPromptRequest(
        name=f"projects/{project}/locations/us/templates/ssn-test", # Use project variable
        user_prompt_data=user_prompt_data,
    )

    logger.info("[Callback] Calling Model Armor sanitize_user_prompt...")
    response = client.sanitize_user_prompt(request=request)

    sdp_filter_result = response.sanitization_result.filter_results.get("sdp")
    if sdp_filter_result and sdp_filter_result.sdp_filter_result.inspect_result.match_state.name == "MATCH_FOUND":
        logger.info("[Callback] PII MATCH_FOUND.")
    print(response)
    return str(response)


validator = LlmAgent(
    name="agent_validator",
    model="gemini-2.0-flash-001",
    instruction="""
    Step 1: Validate with `guardrail_check` tool output if the prompt has PII, if it does
    ask the customer if want to continue.
    
    Your output for Step 1 must have the query WITHOUT the PII detected (mask the PII) and add the info_type at the end.
    
    Step 2: Once you receive acceptance from the use to continue, save it in your state output_key as yes/no and
    continue.
    """,
    output_key='user_response',
    tools=[guardrail_check]
)

# Custom agent to check the status and escalate if 'pass'
class CheckStatusAndEscalate(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        status = ctx.session.state.get("user_response", "no")
        should_stop = (status == "yes")
        print(should_stop)
        yield Event(author=self.name, actions=EventActions(escalate=should_stop))

google_search_agent = LlmAgent(
    name="google_search_agent",
    model="gemini-2.0-flash-001",
    instruction="Take the state `original_query` value and use your tool `google_search`",
    tools=[google_search]
)

root_agent = SequentialAgent(
    name="root_agent",
    sub_agents=[validator, CheckStatusAndEscalate(name="StopChecker"), google_search_agent]
)

APP_NAME = "my_guardrail_app"
USER_ID = "test_user_1"
SESSION_ID = "test_session_001"

session_service = InMemorySessionService()
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)

runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

def call_my_agent(query: str):
    print(f"\nUser Query: {query}")
    content = types.Content(role='user', parts=[types.Part(text=query)])

    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    final_response = ""
    for event in events:
        if event.is_final_response():

            if event.content and event.content.parts:
                final_response = event.content.parts[0].text
            print(f"Agent Response: {final_response}")

    return final_response

# call_my_agent("My social is 123-45-7890, can you if theres any information on internet?")
# call_my_agent("no")