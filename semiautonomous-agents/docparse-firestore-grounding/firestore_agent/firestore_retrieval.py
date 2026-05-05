"""Custom Firestore retrieval tool with PDF grounding for GE.

Queries Firestore vector search, builds GroundingMetadata pointing to PDF URIs
so Gemini Enterprise UI renders clickable citations to source PDFs.
"""
import os
from google.cloud import firestore
from google import genai
from google.genai import types
from google.adk.tools import FunctionTool


def retrieve_with_pdf_grounding(query: str) -> str:
    """Retrieve chunks from Firestore and return formatted context.

    This is the text the outer agent will see. The grounding metadata
    is built separately in the agent wrapper.

    Args:
        query: User's question

    Returns:
        Concatenated chunk text for synthesis
    """
    project = os.environ.get("GOOGLE_CLOUD_PROJECT", "sharepoint-wif")
    collection_name = os.environ.get("FIRESTORE_COLLECTION", "docparse_chunks")
    top_k = int(os.environ.get("AGENT_TOP_K", "20"))

    db = firestore.Client(project=project)
    genai_client = genai.Client(vertexai=True, project=project, location="global")

    # 1. Embed query with gemini-embeddings-002
    try:
        resp = genai_client.models.embed_content(
            model="gemini-embeddings-002",
            contents=types.EmbedContentRequest(content=types.Content(parts=[types.Part(text=query)])))
        q_embedding = resp.embeddings[0].values
    except Exception as e:
        return f"Embedding failed: {type(e).__name__}: {str(e)[:200]}"

    # 2. Firestore vector search
    try:
        collection = db.collection(collection_name)
        results = collection.find_nearest(
            vector_field="embedding",
            query_vector=firestore.VectorValue(q_embedding),
            limit=top_k,
            distance_measure=firestore.DistanceMeasure.COSINE
        )

        chunks = []
        for doc in results:
            data = doc.to_dict()
            chunks.append(data.get("text", ""))

        if not chunks:
            return "No relevant chunks found in Firestore."

        return "\n\n---\n\n".join(chunks)

    except Exception as e:
        return f"Firestore search failed: {type(e).__name__}: {str(e)[:200]}"


# Wrap as ADK FunctionTool
firestore_retrieval_tool = FunctionTool(retrieve_with_pdf_grounding)
