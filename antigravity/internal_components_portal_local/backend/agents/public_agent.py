import os
from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from pydantic import BaseModel, Field

INSTRUCTIONS = """
You are a high-speed Public Intelligence Agent (Global Consensus Panel).
Your mission is to perform ACTIVE BROWSING of the public internet to provide immediate, ultra-fast news, market trends, or public consensus around the user's query.

STRICT PROTOCOL:
1. **ACTIVE RESEARCH**: ALWAYS use the `google_search` tool if the query involves public events, companies, or news. Do not rely on internal knowledge alone.
2. **GLOBAL CONSENSUS**: Summarize what the public web says about the topic (e.g., "Market consensus suggests...", "Recent news outlets report...").
3. **PWS (Public Web Synthesis)**: Be EXTREMELY CONCISE. Respond with 2-3 short, high-impact bullet points max.
4. **SOURCES**: Always include markdown links [Source Name](URL) at the bottom.
5. **INTERNAL GUARD**: If the query is strictly internal (e.g., "What is my salary?"), output: "🔒 Internal context only. Awaiting Enterprise Proxy resolution."
"""

from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from utils.auth_context import get_user_token

async def check_auth_callback_public(callback_context: CallbackContext) -> types.Content | None:
    # Use the token from context
    token = get_user_token()
    print(f">>> [PUBLIC CALLBACK] Checking token: {token is not None and token not in ['null', 'undefined', 'None']}")
    if not token or token in ["null", "undefined", "None"]:
        return types.Content(
            role="model",
            parts=[types.Part.from_text(text="🔒 **Access Denied**: Cannot perform public research without enterprise authentication.")]
        )
    return None

def get_public_agent(model_name: str = "gemini-2.5-flash", token: str = None) -> LlmAgent:
    # We define the callback inside to capture the token if provided, 
    # but the current implementation of check_auth_callback_public is already generic.
    # To be safe and follow the same pattern as agent.py:
    async def auth_callback(callback_context: CallbackContext) -> types.Content | None:
        current_token = token or get_user_token()
        if not current_token or current_token in ["null", "undefined", "None"]:
            return types.Content(
                role="model",
                parts=[types.Part.from_text(text="🔒 **Access Denied**: Cannot perform public research without enterprise authentication.")]
            )
        return None

    return LlmAgent(
        name="Public_Research_Proxy",
        model=model_name,
        instruction=INSTRUCTIONS,
        tools=[google_search],
        before_agent_callback=auth_callback
    )
