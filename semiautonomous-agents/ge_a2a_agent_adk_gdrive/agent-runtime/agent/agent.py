"""ADK LlmAgent with Google Search grounding.

This agent runs as the Agent Runtime service account. Calls to Google
Search are authenticated via the AE SA's Google identity. End-user
authentication is enforced upstream by Gemini Enterprise's OAuth
Authorization resource (the user must hold a valid Google account and
consent before any request reaches this agent), but the user's OAuth
token does NOT survive the AE proxy — see the README's "Known
limitations" section.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import google_search


root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="ge_a2a_auth_agent",
    description=(
        "Diagnostic ADK agent reached through the GE Custom-A2A bridge, "
        "grounded with Google Search via the AE service account."
    ),
    instruction=(
        "You are a helpful assistant deployed on Vertex AI Agent Runtime "
        "and reached through Gemini Enterprise via the Custom-A2A bridge.\n\n"
        "Caller identity (verbatim from the runtime — do not invent):\n"
        "{caller_identity?}\n\n"
        "Behavior:\n"
        "1. If the user asks `whoami` or any identity question, reply with "
        "the caller identity block above verbatim, then a one-line note "
        "explaining that `sub` is the Google numeric ID of whoever the "
        "Vertex AI proxy authenticated as.\n"
        "2. Otherwise, answer using Google Search grounding. Cite the "
        "sources you used. Keep replies under 8 lines."
    ),
    tools=[google_search],
)
