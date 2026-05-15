"""Custom RAG retrieval FunctionTool with semantic re-ranker.

Wraps the genai SDK's RAG retrieval because ADK's built-in VertexAiRagRetrieval
doesn't expose rag_retrieval_config (needed for semantic-ranker-default@latest).
"""
import os
from google import genai
from google.genai import types
from google.adk.tools import FunctionTool


def retrieve_from_corpus(query: str) -> str:
    """Retrieve relevant page-level chunks from the docparse markdown corpus.

    Uses semantic re-ranking (semantic-ranker-default@latest) to ensure the
    most relevant chunks for THIS specific question appear first.

    Args:
        query: The user's question

    Returns:
        Concatenated text from top-k re-ranked chunks
    """
    corpus = os.environ["RAG_CORPUS_NAME"]
    project = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
    top_k = int(os.environ.get("AGENT_TOP_K", "20"))
    use_reranker = os.environ.get("AGENT_USE_RERANKER", "true").lower() == "true"

    client = genai.Client(vertexai=True, project=project, location=location)

    # Build retrieval config (with optional re-ranker)
    if use_reranker:
        rag_retrieval_config = types.RagRetrievalConfig(
            top_k=top_k,
            ranking=types.RagRetrievalConfigRanking(
                rank_service=types.RagRetrievalConfigRankingRankService(
                    model_name="semantic-ranker-default@latest"
                )
            ),
        )
    else:
        rag_retrieval_config = types.RagRetrievalConfig(top_k=top_k)

    # Retrieve contexts using genai SDK
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def _fetch():
            return await client.aio.models.retrieve_contexts(
                model="gemini-2.5-flash",
                contents=[types.Content(role="user", parts=[types.Part.from_text(text=query)])],
                rag_resources=[types.RagResource(rag_corpus=corpus)],
                rag_retrieval_config=rag_retrieval_config,
            )

        resp = loop.run_until_complete(_fetch())
        loop.close()

        chunks = []
        if hasattr(resp, 'contexts') and resp.contexts and hasattr(resp.contexts, 'contexts'):
            for ctx in resp.contexts.contexts[:top_k]:
                if hasattr(ctx, 'text') and ctx.text:
                    chunks.append(ctx.text)

        return "\n\n---\n\n".join(chunks) if chunks else "No relevant chunks found."

    except Exception as e:
        return f"Retrieval failed: {type(e).__name__}: {str(e)[:300]}"


# Wrap as ADK FunctionTool (infers name/description from the function)
reranker_retrieval_tool = FunctionTool(retrieve_from_corpus)
