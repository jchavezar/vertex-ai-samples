from google.adk.agents import Agent
from google.genai import types
from google.adk.models import LlmRequest
from google.adk.agents.callback_context import CallbackContext

def before_model_call(callback_context: CallbackContext, llm_request: LlmRequest):
    print(callback_context)
    print(llm_request)
    print(type(llm_request))
    print(llm_request.contents[-1].parts)
    print(llm_request.contents[-1].parts[0].text)
    llm_request.contents[-1].parts.append(types.Part.from_uri(file_uri="gs://vtxdemos-datasets-public/10k-files/goog-10-k-2024.pdf"))
    print(llm_request)
    return None

root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    description="You are an AGI",
    instruction="Answer any question",
    before_model_callback=before_model_call
)

