"""Custom retrieval tool that supports re-ranking.

ADK's built-in VertexAiRagRetrieval doesn't expose rag_retrieval_config,
so we wrap the genai SDK's retrieval API as a FunctionTool.
"""
import os
from google import genai
from google.genai import types
from google.adk.tools import FunctionTool


RAG_CORPUS = os.environ["RAG_CORPUS_NAME"]
TOP_K = int(os.environ.get("AGENT_TOP_K", "20"))
USE_RERANKER = os.environ.get("AGENT_USE_RERANKER", "true").lower() == "true"


def retrieve_with_reranker(query: str) -> str:
    """Retrieve relevant chunks from the RAG corpus with optional re-ranking.

    Args:
        query: The search query

    Returns:
        Concatenated text from top-k retrieved chunks
    """
    client = genai.Client(
        vertexai=True,
        project=os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos"),
        location=os.environ.get("GOOGLE_CLOUD_LOCATION", "global"),
    )

    # Build retrieval config with optional re-ranker
    if USE_RERANKER:
        rag_retrieval_config = types.RagRetrievalConfig(
            top_k=TOP_K,
            ranking=types.RagRetrievalConfigRanking(
                rank_service=types.RagRetrievalConfigRankingRankService(
                    model_name="semantic-ranker-default@latest"
                )
            ),
        )
    else:
        rag_retrieval_config = types.RagRetrievalConfig(top_k=TOP_K)

    # Call RAG retrieval API
    resp = client.aio.models.retrieve_contexts(
        model="gemini-2.5-pro",  # model parameter required but doesn't affect retrieval
        contents=[types.Content(role="user", parts=[types.Part.from_text(text=query)])],
        rag_resources=[types.RagResource(rag_corpus=RAG_CORPUS)],
        rag_retrieval_config=rag_retrieval_config,
    )

    # Extract chunks (this is sync; in prod would need async wrapper)
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(resp)

    chunks = []
    if hasattr(result, 'contexts') and result.contexts:
        for ctx in result.contexts.contexts[:TOP_K]:
            if hasattr(ctx, 'text'):
                chunks.append(ctx.text)

    return "\n\n---\n\n".join(chunks) if chunks else "No relevant chunks found."


# Wrap as a FunctionTool that ADK can call
reranker_retrieval_tool = FunctionTool(
    name="retrieve_from_corpus",
    description=(
        "Retrieves relevant page-level chunks from the docparse markdown corpus. "
        "Uses semantic re-ranking to ensure the most relevant chunks appear first."
    ),
    func=retrieve_with_reranker,
)
