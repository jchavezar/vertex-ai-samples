"""Batch-embed transaction descriptions using Vertex AI gemini-embedding-001."""

import asyncio
import json
import logging
import os

from google import genai
from google.genai import types

logger = logging.getLogger("amex-mcp.embedder")

PROJECT = os.environ.get("GCP_PROJECT_ID", "vtxdemos")
LOCATION = os.environ.get("EMBEDDING_LOCATION", "us-central1")
EMBEDDING_MODEL = "gemini-embedding-001"
DIMENSIONS = 768  # MRL reduction from 3072 to save storage
BATCH_SIZE = 50  # Max texts per embed call

_client = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(vertexai=True, project=PROJECT, location=LOCATION)
    return _client


def _build_text(txn: dict) -> str:
    """Build a rich text representation of a transaction for embedding."""
    parts = []
    parts.append(txn.get("merchant_clean", txn.get("description", "")))
    if txn.get("enriched_category"):
        parts.append(txn["enriched_category"])
    if txn.get("subcategory"):
        parts.append(txn["subcategory"])
    if txn.get("tags"):
        parts.append(" ".join(txn["tags"]))
    if txn.get("amount"):
        parts.append(f"${txn['amount']:.2f}")
    return " | ".join(parts)


async def embed_transactions(transactions: list[dict]) -> list[dict]:
    """Add embedding vectors to each transaction.

    Uses gemini-embedding-001 with 768 dimensions (MRL).
    Embeds a rich text combining merchant, category, subcategory, and tags.
    """
    if not transactions:
        return transactions

    texts = [_build_text(txn) for txn in transactions]
    batches = [texts[i:i + BATCH_SIZE] for i in range(0, len(texts), BATCH_SIZE)]

    logger.info(json.dumps({
        "event": "embedding_started",
        "total": len(transactions),
        "batches": len(batches),
    }))

    all_embeddings = []
    for batch_idx, batch in enumerate(batches):
        try:
            result = await asyncio.to_thread(
                _get_client().models.embed_content,
                model=EMBEDDING_MODEL,
                contents=batch,
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT",
                    output_dimensionality=DIMENSIONS,
                ),
            )
            all_embeddings.extend([e.values for e in result.embeddings])
        except Exception as e:
            logger.error(json.dumps({
                "event": "embedding_batch_failed",
                "batch": batch_idx,
                "error": str(e),
            }))
            # Fill with empty vectors so indexing stays aligned
            all_embeddings.extend([None] * len(batch))

    for i, txn in enumerate(transactions):
        if i < len(all_embeddings) and all_embeddings[i] is not None:
            txn["embedding"] = all_embeddings[i]

    embedded_count = sum(1 for e in all_embeddings if e is not None)
    logger.info(json.dumps({
        "event": "embedding_completed",
        "total": len(transactions),
        "embedded": embedded_count,
    }))
    return transactions


async def embed_query(text: str) -> list[float]:
    """Embed a search query for semantic retrieval."""
    result = await asyncio.to_thread(
        _get_client().models.embed_content,
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=DIMENSIONS,
        ),
    )
    return result.embeddings[0].values
