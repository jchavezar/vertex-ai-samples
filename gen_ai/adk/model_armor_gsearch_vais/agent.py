#%%
import os
from google.genai import types
from typing import AsyncGenerator
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from google.adk.runners import Runner
from google.cloud import modelarmor_v1
from google.adk.tools import ToolContext
from google.adk.events import Event, EventActions
from google.adk.sessions import InMemorySessionService
from google.adk.agents import SequentialAgent, LlmAgent, BaseAgent
from google.adk.agents.invocation_context import InvocationContext

APP_NAME = "Analyzer"
USER_ID = "jesus"
SESSION_ID = USER_ID

session_service = InMemorySessionService()
session = session_service.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID,
)

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

project = "jesusarguelles-sandbox"
location = "us-central1"

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
os.environ["GOOGLE_CLOUD_PROJECT"] = project
os.environ["GOOGLE_CLOUD_LOCATION"] = location

client = modelarmor_v1.ModelArmorClient(transport="rest", client_options = {"api_endpoint" : "modelarmor.us.rep.googleapis.com"})

def guardrail_check_tool(prompt: str, tool_context: ToolContext) -> str:
    logging.info("[Callback] Guardrail check tool called")
    try:
        if "original_query" not in session.state:
            session.state["original_query"] = [prompt]
        else:
            session.state["original_query"].append(prompt)
    except Exception as e:
        logging.info("[Callback] Guardrail check tool failed {e}")
    logger.info(f"Session state: {session.state}")
    tool_context.state["original_query"] = prompt
    user_prompt_data = modelarmor_v1.DataItem()
    user_prompt_data.text = prompt

    request = modelarmor_v1.SanitizeUserPromptRequest(
        name=f"projects/{project}/locations/us/templates/ai-template", # Use project variable
        user_prompt_data=user_prompt_data,
    )

    logger.info("[Callback] Calling Model Armor sanitize_user_prompt...")
    response = client.sanitize_user_prompt(request=request)

    sdp_filter_result = response.sanitization_result.filter_results.get("sdp")
    if sdp_filter_result and sdp_filter_result.sdp_filter_result.inspect_result.match_state.name == "MATCH_FOUND":
        logger.info("[Callback] PII MATCH_FOUND.")
    print(response)
    return str(response)

guardrail_agent = LlmAgent(
    name="guardrail_check",
    description="This is a global checker tool to detect PII",
    instruction="""Use the tool to check if the prompt/original_query has PII if not return it back to the main agent
    with a note that there's no PII and can continue to execute the original_query.
    """,
    model="gemini-2.0-flash-001",  # You can adjust the model if needed
    tools=[guardrail_check_tool]
)

google_search_agent = LlmAgent(
    name="internet_search",
    description="This is a tool for surfacing information from the internet",
    instruction="Get the original_query from the state as fulfill it",
    model="gemini-2.0-flash-001",
    tools=[google_search]
)

root_agent = LlmAgent(
    name="init_agent",
    model="gemini-2.0-flash-001",
    instruction="""
    *Always use your the guardrail_check tool as validator for any query.*
    
    Validate the prompt for PII using guardrail_check tool. 
    
    PRINT the guardrail_check tool output.
    
    If the guardrail_check tool's output indicates PII is found, 
    **immediately ask the user 'Your query has PII. Do you want to continue?' and wait for their 'yes' or 'no' response.** 
    
    If the user explicitly approves by saying 'yes', 
    then proceed to use other relevant agents, such as internet_search, 
    to effectively fulfill the original query.
    
    """,
    tools=[AgentTool(guardrail_agent), AgentTool(google_search_agent)],
    output_key='human_decision'
)


def generate_content(prompt: str):
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service
    )

    content = types.Content(role='user', parts=[types.Part(text=prompt)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    for event in events:
        print(event)
        if event.is_final_response() and event.content and event.content.parts:
            logger.info(f"Potential final response from [{event.author}]: {event.content.parts[0].text}")
            final_response = event.content.parts[0].text
    return final_response