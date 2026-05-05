"""ADK agent with Firestore retrieval + manual PDF grounding.

Uses gemini-embeddings-002 for retrieval, builds grounding metadata pointing
to source PDF pages so Gemini Enterprise renders clickable citations.
"""
import os
from google.adk.agents import Agent
from .firestore_retrieval import firestore_retrieval_tool


MODEL = os.environ.get("AGENT_MODEL", "gemini-2.5-flash")


SYSTEM_INSTRUCTION = """You answer questions about PDF reports extracted by docparse.

CRITICAL RULES:
1. Check retrieved chunks first. Each starts with "# <doc> — Page N".
2. Prefer EXHAUSTIVE — include all relevant detail.
3. Quote chart values VERBATIM.
4. If chunks contain the answer, state it directly. Do NOT say "I cannot find".
5. Do NOT search the web. Use only retrieved chunks."""


root_agent = Agent(
    model=MODEL,
    name="docparse_firestore_agent",
    description=(
        "Firestore-backed docparse agent with PDF-level grounding. "
        "gemini-embeddings-002, manual grounding construction."
    ),
    instruction=SYSTEM_INSTRUCTION,
    tools=[firestore_retrieval_tool],
)
