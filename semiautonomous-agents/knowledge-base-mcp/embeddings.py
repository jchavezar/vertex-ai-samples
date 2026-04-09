"""Vertex AI text-embedding-004 wrapper for knowledge base embeddings."""

import os
import logging

from google import genai
from google.genai.types import EmbedContentConfig

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "text-embedding-004"
EMBEDDING_DIM = 768
BATCH_SIZE = 250

_genai_client = None


def get_genai_client():
    global _genai_client
    if _genai_client is None:
        _genai_client = genai.Client(
            vertexai=True,
            project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
            location=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1"),
        )
    return _genai_client


async def embed_texts(
    texts: list[str],
    task_type: str = "RETRIEVAL_DOCUMENT",
) -> list[list[float]]:
    """Batch-embed texts using Vertex AI text-embedding-004."""
    client = get_genai_client()
    all_embeddings = []

    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        response = await client.aio.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=batch,
            config=EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=EMBEDDING_DIM,
            ),
        )
        all_embeddings.extend([e.values for e in response.embeddings])
        logger.info(f"Embedded batch {i // BATCH_SIZE + 1} ({len(batch)} texts)")

    return all_embeddings


async def embed_query(text: str) -> list[float]:
    """Embed a single search query."""
    result = await embed_texts([text], task_type="RETRIEVAL_QUERY")
    return result[0]
