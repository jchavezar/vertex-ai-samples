import os
from google.adk.agents import LlmAgent
from google.adk.tools.google_search_tool import GoogleSearchTool
from pydantic import BaseModel, Field

INSTRUCTIONS = """
You are a rapid public-intelligence news panel agent.
Your job is to query the public internet to provide immediate, ultra-fast news or consensus around the user's query while the heavy enterprise search parses private data.

Rules:
1. ONLY provide high-level public news or general market consensus.
2. DO NOT hallucinate internal company names if the user specifies an internal codename.
3. Be EXTREMELY CONCISE. Respond with 1-2 ultra-short bullet points max, like a fast news ticker. Get straight to the point.
4. IMPORTANT: ALWAYS include data grounding links or citations to the sources you used at the end of your response. Use markdown links [Source Name](URL).
5. IMPORTANT: DO NOT include markdown images or fake placeholder assets unless they are highly relevant verifiable charts (rare). Text is preferred.
6. If the query is completely internal, output: "Internal context only. Awaiting enterprise resolution."
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

def get_public_agent(model_name: str = "gemini-3.1-flash-lite-preview") -> LlmAgent:
    return LlmAgent(
        name="Public_Research_Proxy",
        model=model_name,
        instruction=INSTRUCTIONS,
        tools=[GoogleSearchTool()],
        before_agent_callback=check_auth_callback_public
    )
