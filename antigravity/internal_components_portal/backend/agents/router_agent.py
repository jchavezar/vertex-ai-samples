import os
import logging
from google.adk.agents.llm_agent import LlmAgent

logger = logging.getLogger("router_agent")

def get_router_agent() -> LlmAgent:
    """
    Returns a Google ADK LlmAgent configured to route the user's prompt 
    as either SEARCH or ACTION.
    """
    system_instruction = """
You are a highly efficient Intent Router for an Enterprise Security Proxy. You evaluate the full conversation history to determine the user's current intent.

- **SEARCH**: The user is asking a question aiming for information retrieval, reading, or querying data NOT related to ServiceNow.
- **ACTION**: The user is asking to perform an active operation such as create, update, modify, summarize, or generate a document.
- **SERVICENOW**: The user's prompt contains terms like "ServiceNow", "incident", "ticket", "problem", "gas", "fuel", "tank", "leak", or "recall" in the context of reporting an issue with a product (like a Ducati bike).
- **FOLLOW-UPS**: If the user is giving a short confirmation (e.g., "yes please", "do it", "looks good") or answering a clarifying question from the model, you MUST look at the immediate conversation history. If the history involves drafting or discussing a ServiceNow incident/ticket, you MUST output SERVICENOW. If it involves an Action, output ACTION.

IMPORTANT: SERVICENOW takes absolute precedence if the user is describing a problem, failure, or maintenance task that needs to be recorded, even if they don't explicitly name the system.
Respond ONLY with "SEARCH", "ACTION", or "SERVICENOW". Do not include any other text or punctuation.
"""

    agent = LlmAgent(
        name="router_agent",
        model="gemini-2.5-flash",
        instruction=system_instruction
    )
    return agent

