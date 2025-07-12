#%%
import os
import logging
from dotenv import load_dotenv
from typing import Optional
from google.genai import types
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.cloud import modelarmor_v1
from google.adk.tools import google_search
from google.adk.models import LlmResponse, LlmRequest
from google.adk.sessions import InMemorySessionService
from google.adk.agents.callback_context import CallbackContext

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

project = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION")
template_model_id = os.getenv("TEMPLATE_MODEL_ARMOR_ID")

client = modelarmor_v1.ModelArmorClient(transport="rest", client_options = {"api_endpoint" : "modelarmor.us.rep.googleapis.com"})

APP_NAME = "Analyzer"
USER_ID = "jesus"
SESSION_ID = USER_ID

# Initialize session_service once globally to persist state across generate_content calls
global_session_service = InMemorySessionService()

async def setup_session_and_runner(agent):
    session = await global_session_service.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )

    if session:
        print(f"Retrieved existing session: {SESSION_ID}")
    else:
        session = await global_session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID,
        )
        print(f"Created new session: {SESSION_ID}")

    runner = Runner(agent=agent, app_name=APP_NAME, session_service=global_session_service)
    return session, runner


def model_armor_analyze(prompt: str):
    user_prompt_data = modelarmor_v1.DataItem()
    user_prompt_data.text = prompt

    # noinspection PyTypeChecker
    request = modelarmor_v1.SanitizeUserPromptRequest(
        name=f"projects/{project}/locations/us/templates/{template_model_id}",
        user_prompt_data=user_prompt_data,
    )
    response = client.sanitize_user_prompt(request=request)
    print(response)
    jailbreak = response.sanitization_result.filter_results.get("pi_and_jailbreak")
    sensitive_data = response.sanitization_result.filter_results.get("sdp")

    return jailbreak, sensitive_data


def guardrail_function(callback_context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
    agent_name = callback_context.agent_name
    print(f"[Callback] Before model call for agent: {agent_name}")

    pii_found = callback_context.state.get("PII", False)

    last_user_message = ""
    if llm_request.contents and llm_request.contents[-1].role == 'user':
        if llm_request.contents[-1].parts:
            last_user_message = llm_request.contents[-1].parts[0].text
    print(f"[Callback] Inspecting last user message: '{last_user_message}'")

    if pii_found and last_user_message.lower() != "yes":
        callback_context.state["PII"] = False
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text="Please respond Yes/No to continue")]
            )
        )

    jailbreak, sensitive_data = model_armor_analyze(last_user_message)
    if sensitive_data and sensitive_data.sdp_filter_result and sensitive_data.sdp_filter_result.deidentify_result:
        if sensitive_data.sdp_filter_result.deidentify_result.match_state.name == "MATCH_FOUND":
            pii_found = True
            callback_context.state["PII"] = True
            if pii_found and last_user_message.lower() != "no":
                return LlmResponse(
                    content=types.Content(
                        role="model",
                        parts=[types.Part(text=
                                          f"""
                                          Your query has identify the following personal information:
                                          {sensitive_data.sdp_filter_result.deidentify_result.info_types}
                                          
                                          Would you like to continue? (Yes/No)
                                          """
                                          )],
                    )
                )
            elif pii_found and last_user_message.lower() == "yes":
                callback_context.state["PII"] = False
                return None

    elif jailbreak and jailbreak.pi_and_jailbreak_filter_result:
        if jailbreak.pi_and_jailbreak_filter_result.match_state.name == "MATCH_FOUND":
            return LlmResponse(
                content=types.Content(
                    role="model",
                    parts=[types.Part(text="""Break Reason: Jailbreak""")]
                )
            )
    return None


root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    description="You are an Artificial General Intelligence",
    instruction="Answer any question using your `google_search_tool` as your grounding",
    before_model_callback=guardrail_function,
    tools=[google_search]
)

async def generate_content(prompt: str):
    session, runner = await setup_session_and_runner(root_agent)

    content = types.Content(role='user', parts=[types.Part(text=prompt)])
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    final_response = None
    async for event in events:
        print(event)
        if event.is_final_response() and event.content and event.content.parts:
            logger.info(f"Potential final response from [{event.author}]: {event.content.parts[0].text}")
            final_response = event.content.parts[0].text
    return final_response