#%%
import os
import logging
from typing import Optional
from google.adk import Agent
from google.genai import types
from google.adk.runners import Runner
from google.adk.models import LlmRequest, LlmResponse
from google.adk.agents.callback_context import CallbackContext
from google.cloud import modelarmor_v1
from google.adk.sessions import InMemorySessionService
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

APP_NAME = "Analyzer"
USER_ID = "jesus"
SESSION_ID = USER_ID

session_service = InMemorySessionService()
session = session_service.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID,
)

project = "jesusarguelles-sandbox"
location = "us-central1"

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
os.environ["GOOGLE_CLOUD_PROJECT"] = project
os.environ["GOOGLE_CLOUD_LOCATION"] = location

client = modelarmor_v1.ModelArmorClient(transport="rest", client_options = {"api_endpoint" : "modelarmor.us.rep.googleapis.com"})

def guardrail_check(
        callback_context: CallbackContext,
        llm_request: LlmRequest
) -> Optional[LlmResponse]:
    logger.info("[Callback] Guardrail check tool called")

    user_query = llm_request.contents[-1].parts[0].text if llm_request.contents[-1].role == "user" else ""
    if "yes" in user_query:
        return None

    print(llm_request.contents)
    print(callback_context)
    print(dir(callback_context))
    user_prompt_data = modelarmor_v1.DataItem()
    user_prompt_data.text = user_query

    request = modelarmor_v1.SanitizeUserPromptRequest(
        name=f"projects/{project}/locations/us/templates/ai-template", # Use project variable
        user_prompt_data=user_prompt_data,
    )

    logger.info("[Callback] Calling Model Armor sanitize_user_prompt...")
    response = client.sanitize_user_prompt(request=request)
    logger.info(f"[Model Armor]\n {response}\n[End Model Armor]")
    # Results from Model Armor
    sdp_filter_result = response.sanitization_result.filter_results.get("sdp")
    if sdp_filter_result and sdp_filter_result.sdp_filter_result.inspect_result.match_state.name == "MATCH_FOUND":
        logger.info("[Callback] PII MATCH_FOUND.")
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text="PII was detected in your query. Do you want to proceed?")],
            )
        )

    return None

root_agent = Agent(
    name="root_agent",
    model="gemini-2.0-flash-001",
    description="You are a sharp AI assistant",
    instruction="""
    As an assistant you have a before_model_call to detect any PII. If pass use your tools to answer any question.
    """,
    before_model_callback=[guardrail_check]
)


runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service
)

content = types.Content(role='user', parts=[types.Part(text="my ssn is 917-750-3256 do you think is a social?")])
events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

for event in events:
    print(event)
    if event.is_final_response() and event.content and event.content.parts:
        logger.info(f"Potential final response from [{event.author}]: {event.content.parts[0].text}")
        final_response = event.content.parts[0].text

