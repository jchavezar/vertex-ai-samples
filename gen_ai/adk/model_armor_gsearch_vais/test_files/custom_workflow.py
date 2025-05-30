#%%
import logging
from google.genai import types
from typing import override, AsyncGenerator
from google.adk.runners import Runner
from google.cloud import modelarmor_v1
from google.adk.tools import VertexAiSearchTool, google_search, ToolContext
from google.adk.agents import LlmAgent, BaseAgent
from google.adk.sessions import InMemorySessionService
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

import os

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
os.environ["GOOGLE_CLOUD_PROJECT"] = "jesusarguelles-sandbox"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

project = "jesusarguelles-sandbox"
location = "us-central1"

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

class WorkFlow(BaseAgent):
    pii_validator_agent: LlmAgent
    # google_search_agent: LlmAgent
    # summarizer_agent: LlmAgent

    model_config = {"arbitrary_types_allowed": True}

    def __init__(
            self,
            name: str,
            pii_validator_agent: LlmAgent,
            # google_search_agent: LlmAgent,
            # summarizer_agent: LlmAgent,
    ):
        super().__init__(
            name=name,
            pii_validator_agent=pii_validator_agent,
            # google_search_agent=google_search_agent,
            # summarizer_agent=summarizer_agent
        )


    @override
    async def _run_async_impl(
      self, ctx: InvocationContext
  ) -> AsyncGenerator[Event, None]:
        logger.info(f"{self.name} starting workflow")

        async for event in self.pii_validator_agent.run_async(ctx):
            logger.info(f"{self.name} Event from PII Validator: {event.model_dump_json(indent=2, exclude_none=True)}")
            yield event

        if ctx.session.state.get["approval"]:
            print(ctx.session.state.get["approval"])

validator_agent = LlmAgent(
    name="pii_validator_agent",
    model="gemini-2.0-flash-001",  # Or your preferred model
    instruction="""You are an AI Assistant specializing in PII detection.
You have one tool, `guardrail_check`. This tool will analyze the user's query for PII.
The tool will return a JSON object (Python dictionary) with a key 'pii_detected' (boolean: true if PII is found, false otherwise) and 'model_armor_response_summary' (string, a summary from the tool).

Your task is to:
1. Call the `guardrail_check` tool with the user's query.
2. Examine the 'pii_detected' field in the tool's JSON output.
3. If 'pii_detected' is true, your response MUST be exactly: "PII was detected in your query. Do you want to proceed?"
4. If 'pii_detected' is false, your response MUST be exactly: "No PII detected. Continuing workflow."
Do not add any other text, explanations, or conversational filler to these two specific responses.
If the tool call fails or returns unexpected data, state that you encountered an issue with the PII check.
    """,
    tools=[guardrail_check],
    output_key="approval"  # This will store the LLM's response in session_state
)

workflow = WorkFlow(
    name="WorkFlowAgent",
    pii_validator_agent=validator_agent,
)

APP_NAME = "Analyzer"
USER_ID = "jesus"
SESSION_ID = USER_ID


session_service = InMemorySessionService()
session = session_service.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID,
)

def generate_content(prompt: str):

    runner = Runner(
        agent=workflow,
        app_name=APP_NAME,
        session_service=session_service
    )

    content = types.Content(role='user', parts=[types.Part(text=prompt)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    for event in events:
        if event.is_final_response() and event.content and event.content.parts:
            logger.info(f"Potential final response from [{event.author}]: {event.content.parts[0].text}")
            final_response = event.content.parts[0].text
    return final_response


re = generate_content("my ssn is 917-750-3256")
print(re)
re = generate_content("yes")

