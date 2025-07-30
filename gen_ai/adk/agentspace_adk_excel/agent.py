import sys

import pandas as pd
from io import BytesIO
from google.genai import types
from google.adk.agents import Agent
from google.adk.models import LlmRequest
from google.adk.agents.callback_context import CallbackContext

def extract_data_callback(
        callback_context: CallbackContext,
        llm_request: LlmRequest,
):
    for content in llm_request.contents:
        if (content.role == "user" and
                len(content.parts) > 1 and
                content.parts[1].inline_data):
            print(content.parts[1], file=sys.stdout)
            excel_file_like_object = BytesIO(content.parts[1].inline_data.data)
            df = pd.read_excel(excel_file_like_object)
            markdown_output = df.to_markdown(index=False)
            content.parts[1] = types.Part.from_text(text=f"Context: {markdown_output}")
            break
    return None

root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    description="You are a AGI",
    instruction="""
    Use the context if available.
    
    Respond Any question
    """,
    before_model_callback=extract_data_callback,
)