import logging
from typing import Any
from google.adk.agents import Agent
from google.adk.tools import google_search

logger = logging.getLogger("research_agent")

RESEARCH_INSTRUCTIONS = """
You are the **General Research Specialist**.
Your mission is to answer general questions using Google Search.
You do NOT have access to financial data or FactSet tools.
If the user asks a financial question, you should NOT try to answer it; 
instead, let the root agent handle it or suggest using the Analyst.

Keep your answers concise and accurate based on web search results.
Always cite your sources.
"""

def create_research_agent(model_name: str = "gemini-2.5-flash", tool_observer: Any = None) -> Agent:
    """
    Creates an isolated sub-agent for general web research.
    Optimized for speed using gemini-2.5-flash.
    """
    return Agent(
        name="research_specialist",
        model=model_name,
        instruction=RESEARCH_INSTRUCTIONS,
        tools=[google_search],
        description="Specialist for general web search and non-financial research questions."
    )
