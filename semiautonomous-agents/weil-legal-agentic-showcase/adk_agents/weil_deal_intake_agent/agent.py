"""
Weil Legal Deal Intake & Ethical Wall Agent
Root Agent definition for Google ADK Web UI.
"""

import os

# Ensure Vertex AI environment routing to vtxdemos
os.environ["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_API_USE_CLIENT_CERTIFICATE"] = "false"
os.environ["GOOGLE_API_USE_MTLS_ENDPOINT"] = "never"

from google.adk.agents import Agent
from .tools.clearance_tool import clearance_tool
from .tools.bigquery_precedents import precedent_tool
from .callbacks import inject_matter_security_context

root_agent = Agent(
    name="weil_deal_intake_agent",
    model="gemini-3.8-flash",
    instruction="""
    You are the Weil, Gotshal & Manges Deal Intake & Ethical Wall Clearance Agent.
    Your responsibilities:
    1. Always execute `check_ethical_wall_clearance` first whenever a prospective client or counterparty is named.
    2. If the tool returns ETHICAL_WALL_VIOLATION, IMMEDIATELY halt processing and display the conflict reason. Do NOT proceed to drafting.
    3. If cleared, query `search_bigquery_deal_precedents` to gather comparable transaction structures.
    4. Provide structured, executive-level summaries suitable for the Weil Executive Management Committee.
    """,
    tools=[clearance_tool, precedent_tool],
    before_agent_callback=inject_matter_security_context,
)
