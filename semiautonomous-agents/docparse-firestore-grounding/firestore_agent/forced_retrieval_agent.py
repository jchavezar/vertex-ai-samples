"""Agent wrapper that FORCES retrieval tool to be called every time."""
import os
import json
from google import genai
from google.genai import types
from .firestore_retrieval import retrieve_with_pdf_grounding


PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "sharepoint-wif")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
MODEL = os.environ.get("AGENT_MODEL", "gemini-2.5-flash")


class ForcedRetrievalAgent:
    """Agent that always calls Firestore retrieval before answering."""

    def __init__(self):
        self.project_id = PROJECT_ID
        self.location = LOCATION
        self.model = MODEL

    def _get_client(self):
        """Create client on-demand (not picklable if created in __init__)."""
        return genai.Client(
            vertexai=True,
            project=self.project_id,
            location=self.location
        )

    def query(self, query: str) -> dict:
        """
        Handle query by ALWAYS calling retrieval first, then answering with grounding.

        Returns:
            dict with 'response' and 'grounding_metadata'
        """
        # STEP 1: Always call retrieval tool
        retrieval_result = retrieve_with_pdf_grounding(query)

        try:
            result_data = json.loads(retrieval_result)
        except:
            return {
                "response": "Error parsing retrieval results",
                "grounding_metadata": {}
            }

        if result_data.get("status") == "no_results":
            return {
                "response": "I don't have information about that in my knowledge base.",
                "grounding_metadata": {}
            }

        if result_data.get("status") == "error":
            return {
                "response": f"Error retrieving data: {result_data.get('message', 'Unknown error')}",
                "grounding_metadata": {}
            }

        # STEP 2: Build context from chunks
        chunks = result_data.get("chunks", [])
        grounding_items = result_data.get("grounding", [])

        if not chunks:
            return {
                "response": "No relevant data found.",
                "grounding_metadata": {}
            }

        context = "\n\n---\n\n".join(chunks)

        # STEP 3: Call LLM with retrieved context
        prompt = f"""You are answering a question using retrieved PDF document chunks.

User question: {query}

Retrieved document chunks:
{context}

Instructions:
- Answer EXHAUSTIVELY using all relevant data from the chunks
- Quote statistics and numbers VERBATIM
- If the chunks contain the answer, provide it in detail
- Do NOT say you don't have access - the chunks above are your data source

Answer:"""

        client = self._get_client()
        response = client.models.generate_content(
            model=self.model,
            contents=prompt
        )

        answer_text = response.text

        # STEP 4: Build grounding metadata
        grounding_metadata = {
            "grounding_chunks": [
                {
                    "web": {
                        "uri": item["uri"],
                        "title": item["title"]
                    }
                }
                for item in grounding_items
            ],
            "grounding_supports": []
        }

        return {
            "response": answer_text,
            "grounding_metadata": grounding_metadata
        }


# Singleton instance
_agent = None

def get_agent():
    global _agent
    if _agent is None:
        _agent = ForcedRetrievalAgent()
    return _agent
