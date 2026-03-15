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
Your job is to read the user's prompt and output exactly one word from the following options:

- SEARCH: If the user is asking a question (e.g. "What is...", "Who is...", "How much..."), or asking for ANY kind of search, information retrieval, reading, or querying data. This includes both general web search AND internal enterprise data, employee info, company policies, salaries, or metrics (like latency). **KEY IDENTIFIER**: Question words and requests for information. Examples: "What are the latest AI trends?", "What is the salary of our CFO?", "What is the latency of a cfo?", "Tell me about the internal travel policy", "Read from SharePoint".
- ACTION: If the user is asking to perform an active operation such as create, update, modify, summarize, or generate a document. **KEY IDENTIFIER**: Verbs like "Create", "Generate", "Update", "Edit". Examples: "Generate a PDF summary of X", "Create a new entry for Y".

IMPORTANT: If the prompt is a question asking for information, it is ALWAYS a SEARCH.
Respond ONLY with "SEARCH" or "ACTION". Do not include any other text or punctuation.
"""

    agent = LlmAgent(
        name="router_agent",
        model="gemini-2.5-flash",
        instruction=system_instruction
    )
    return agent

