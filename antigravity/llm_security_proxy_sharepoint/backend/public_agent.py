import os
from google.adk.agents import LlmAgent
from google.adk.tools.google_search_tool import GoogleSearchTool
from pydantic import BaseModel, Field

INSTRUCTIONS = """
You are a rapid public-intelligence research agent.
The user is asking a question that will be processed against highly secure enterprise data.
While that secure processing happens, your job is to query the public internet to provide immediate, general market consensus, benchmarks, or standard practices related to their query.

Rules:
1. ONLY provide high-level public information or general methodologies.
2. DO NOT hallucinate internal company names if the user specifies an internal codename.
3. Be concise and authoritative. Formulate your response as a bulleted list of key findings in single sentence bullet points. Maximum 3 bullets total.
4. If the user query is completely internal and impossible to search on the public web, simply state: "Query relates strictly to internal data; awaiting enterprise search resolution."
"""

from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from auth_context import get_user_token

async def check_auth_callback_public(callback_context: CallbackContext) -> types.Content | None:
    token = get_user_token()
    if not token or token in ["null", "undefined"]:
        return types.Content(
            role="model",
            parts=[types.Part.from_text(text="🔒 **Access Denied**: Cannot perform public research without enterprise authentication.")]
        )
    return None

def get_public_agent(model_name: str = "gemini-2.5-flash") -> LlmAgent:
    return LlmAgent(
        name="Public_Research_Proxy",
        model=model_name,
        instruction=INSTRUCTIONS,
        tools=[GoogleSearchTool()],
        before_agent_callback=check_auth_callback_public
    )
