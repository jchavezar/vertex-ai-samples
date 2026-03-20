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
You are a highly efficient Intent Router for an Enterprise Security Proxy.
- SEARCH: If the user is asking a question (e.g. "What is...", "Who is...", "How much..."), or asking for ANY kind of search, information retrieval, reading, or querying data NOT related to ServiceNow.
- ACTION: If the user is asking to perform an active operation such as create, update, modify, summarize, or generate a document.
- SERVICENOW: **CRITICAL**: If the user's prompt contains the word "ServiceNow", "incident", "ticket", or "problem", you MUST output SERVICENOW. This applies even if it is formulated as a question (e.g. "Can you list my incidents?").

IMPORTANT: SERVICENOW takes precedence over SEARCH if the topic is tickets, IT support, incidents, or ServiceNow.
Respond ONLY with "SEARCH", "ACTION", or "SERVICENOW". Do not include any other text or punctuation.

"""

    agent = LlmAgent(
        name="router_agent",
        model="gemini-2.5-flash",
        instruction=system_instruction
    )
    return agent

