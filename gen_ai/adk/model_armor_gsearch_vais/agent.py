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
    name="guardrail_agent",
    model="gemini-2.0-flash-001",  # You can adjust the model if needed
    instruction="Check if the prompt has PII",
    tools=[guardrail_check]
)

google_search_agent = LlmAgent(
    name="google_search_agent",
    model="gemini-2.0-flash-001",
    description="Take original_query from your state and use google search to answer the query.",
    tools=[google_search]
)

root_agent = LlmAgent(
    name="init_agent",
    model="gemini-2.0-flash-001",
    instruction="""
    Validate with `guardrail_check` sub_agent output if the prompt has PII,
    If the tool output has PII:
    
    1. ASK AND WAIT FOR the user if they want to approve or reject indicating there is PII [PAUSE].
    
    First Agent Output expected:
    Your query has <infotype>/<rai_filter_key>/<pi_and_jailbreak_key> would you like to continue?
    
    If the User approve continue with the google_search_agent subagent with the PII and give me a response back.
    
    """,
    # tools=[guardrail_check],
    tools=[AgentTool(guardrail_agent), AgentTool(google_search_agent)],
    output_key='human_decision'
)
