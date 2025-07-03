from typing import Optional
from google.genai import types
from google.adk.agents import Agent
from google.cloud import modelarmor_v1
from google.adk.tools import google_search
from google.adk.models import LlmResponse, LlmRequest
from google.adk.agents.callback_context import CallbackContext

project = "vtxdemos"
location = "us-central1"

client = modelarmor_v1.ModelArmorClient(transport="rest", client_options = {"api_endpoint" : "modelarmor.us.rep.googleapis.com"})

def model_armor_analyze(prompt: str):
    user_prompt_data = modelarmor_v1.DataItem()
    user_prompt_data.text = prompt

    request = modelarmor_v1.SanitizeUserPromptRequest(
        name=f"projects/{project}/locations/us/templates/model-armor-demo",
        user_prompt_data=user_prompt_data,
    )
    response = client.sanitize_user_prompt(request=request)
    return response.sanitization_result.filter_results.get("sdp")

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

    response = model_armor_analyze(last_user_message)
    if response and response.sdp_filter_result and response.sdp_filter_result.deidentify_result:
        if response.sdp_filter_result.deidentify_result.match_state.name == "MATCH_FOUND":
            pii_found = True
            print("#"*80)
            print(pii_found)
            callback_context.state["PII"] = True
            if pii_found and last_user_message.lower() != "no":
                return LlmResponse(
                    content=types.Content(
                        role="model",
                        parts=[types.Part(text="Your query has PII would you like to continue? (Yes/No)" )],
                    )
                )
            elif pii_found and last_user_message.lower() == "yes":
                callback_context.state["PII"] = False
                return None

root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    description="You are an Artificial General Intelligence",
    instruction="Answer any question using your `google_search_tool` as your grounding",
    before_model_callback=guardrail_function,
    tools=[google_search]
)