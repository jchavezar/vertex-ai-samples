"""Discovery Engine agent — uses Vertex AI Search retrieval instead of RAG Engine.

The key difference: Discovery Engine auto-populates grounding_metadata in Gemini
responses, so citations appear in Gemini Enterprise UI without manual construction.
"""
import os
from google.adk.agents import Agent
from google.adk.tools import vertex_ai_search

DS_ID = os.environ["DE_DATASTORE_ID"]
PROJECT = os.environ["DE_PROJECT"]
LOCATION = os.environ.get("DE_LOCATION", "global")
MODEL = os.environ.get("AGENT_MODEL", "gemini-3-flash-preview")

SYSTEM_INSTRUCTION = """You answer questions about a corpus of report PDFs extracted to markdown by docparse.

CRITICAL RULES:
1. Always check retrieved search results first.
2. Prefer EXHAUSTIVE over terse — include all relevant detail from the chunks.
3. Quote chart values VERBATIM. Do not reformat ranges.
4. If search results contain the answer, state it directly. Do NOT say "I cannot find".
5. Do NOT search the web. Use only the retrieved chunks from the datastore."""

search_tool = vertex_ai_search(
    data_store_id=DS_ID,
    project_id=PROJECT,
    location=LOCATION,
    name="docparse_de_search",
    description="Search the docparse markdown corpus via Discovery Engine.",
)

root_agent = Agent(
    model=MODEL,
    name="docparse_de_agent",
    description="Answers questions over Discovery Engine, with auto-grounding citations.",
    instruction=SYSTEM_INSTRUCTION,
    tools=[search_tool],
)
