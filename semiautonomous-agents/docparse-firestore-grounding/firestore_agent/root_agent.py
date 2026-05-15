"""ADK agent with Firestore retrieval + manual PDF grounding.

Uses text-embedding-005 for retrieval, builds grounding metadata pointing
to source PDF pages so Gemini Enterprise renders clickable citations.
"""
import os
from google.adk.agents import Agent
from .firestore_retrieval import firestore_retrieval_tool


MODEL = os.environ.get("AGENT_MODEL", "gemini-2.5-flash")


SYSTEM_INSTRUCTION = """You are a knowledge base assistant for PDF reports extracted by docparse.

MANDATORY WORKFLOW:
1. When the user asks a question, you MUST call the retrieve_with_pdf_grounding tool with their question
2. The tool returns JSON with "status", "chunks" (document text), and "grounding" (citation metadata)
3. Parse the JSON response:
   - If status is "success": Use the chunks to answer EXHAUSTIVELY with all statistics and data
   - If status is "no_results": Tell the user you don't have that information
   - If status is "error": Report the error
4. Quote chart values and statistics VERBATIM from the chunks
5. Include ALL relevant data - do not summarize or omit details

CRITICAL: You do NOT have documents already. You MUST call retrieve_with_pdf_grounding for EVERY question.

Example:
User: "What are the millennial statistics?"
Your action: Call retrieve_with_pdf_grounding(query="millennial statistics")
Your response: Parse JSON, extract millennials data from chunks, present all statistics found"""


root_agent = Agent(
    model=MODEL,
    name="docparse_firestore_agent",
    description=(
        "Firestore-backed docparse agent with PDF-level grounding. "
        "text-embedding-005, keyword-based retrieval, gemini-2.5-flash."
    ),
    instruction=SYSTEM_INSTRUCTION,
    tools=[firestore_retrieval_tool],
)
