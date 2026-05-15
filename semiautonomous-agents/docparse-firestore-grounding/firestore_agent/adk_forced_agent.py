"""ADK-based agent that PRE-calls Firestore retrieval before LLM."""
import os
import json
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from .firestore_retrieval import retrieve_with_pdf_grounding


MODEL = os.environ.get("AGENT_MODEL", "gemini-2.5-flash")


class FirestoreAgent(LlmAgent):
    """
    Custom ADK Agent that ALWAYS calls Firestore retrieval before answering.

    Overrides the default behavior to pre-call the retrieval tool,
    then provides the results as context to the LLM.
    """

    def __init__(self):
        super().__init__(
            model=MODEL,
            name="firestore_forced_agent",
            instruction="""You answer questions about PDF reports.

The user's question has ALREADY been used to retrieve relevant document chunks.
These chunks are provided in the CONTEXT section below.

Your job:
- Use ONLY the provided context chunks to answer
- Quote statistics and numbers VERBATIM
- Provide EXHAUSTIVE answers with all relevant details
- Do NOT say you lack access - the context IS your data source"""
        )

    def __call__(self, query: str) -> str:
        """
        Handle query by pre-calling Firestore retrieval, then answering with context.

        Args:
            query: User's question

        Returns:
            Answer text (grounding metadata handled separately by GE)
        """
        # STEP 1: Always call retrieval FIRST
        retrieval_result = retrieve_with_pdf_grounding(query)

        try:
            result_data = json.loads(retrieval_result)
        except:
            return "Error parsing retrieval results."

        if result_data.get("status") == "no_results":
            return "I don't have information about that in my knowledge base."

        if result_data.get("status") == "error":
            return f"Error retrieving data: {result_data.get('message', 'Unknown error')}"

        # STEP 2: Build context
        chunks = result_data.get("chunks", [])
        if not chunks:
            return "No relevant data found."

        context = "\n\n---\n\n".join(chunks[:5])

        # STEP 3: Call parent LLM with context injected
        prompt_with_context = f"""CONTEXT (retrieved from knowledge base for query: "{query}"):

{context}

---

USER QUESTION: {query}

Answer the question using ONLY the context above. Be exhaustive and quote numbers verbatim."""

        # Call the LLM via parent class
        return super().__call__(prompt_with_context)


# Create singleton
root_agent = FirestoreAgent()
