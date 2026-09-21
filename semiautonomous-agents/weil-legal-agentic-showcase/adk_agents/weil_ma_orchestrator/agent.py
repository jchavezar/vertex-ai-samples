"""
Weil Lead M&A Relationship Partner & Multi-Agent Orchestrator
Root Agent definition for Google ADK Web UI.
"""

import os

# Ensure Vertex AI environment routing to vtxdemos
os.environ["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_API_USE_CLIENT_CERTIFICATE"] = "false"
os.environ["GOOGLE_API_USE_MTLS_ENDPOINT"] = "never"

from google.adk.agents import Agent
from google.adk.tools import AgentTool
from .subagents.antitrust_agent import antitrust_subagent
from .subagents.tax_agent import tax_subagent

antitrust_tool = AgentTool(agent=antitrust_subagent)
tax_tool = AgentTool(agent=tax_subagent)

root_agent = Agent(
    name="weil_ma_orchestrator",
    model="gemini-3.8-flash",
    instruction="""
    You are the Lead M&A Relationship Partner at Weil, Gotshal & Manges LLP.
    When a complex corporate transaction or acquisition is submitted:
    1. Delegate regulatory, CFIUS, and antitrust issues to the `antitrust_specialist`.
    2. Delegate tax structuring, basis step-up, and Section 338 questions to the `tax_specialist`.
    3. Synthesize the subagent analyses into a unified, high-level Executive Deal Memorandum for the lead partner.
    """,
    tools=[antitrust_tool, tax_tool],
)
