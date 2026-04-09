"""Load extracted knowledge items into Firestore with embeddings."""

import logging

from pipeline.models import KnowledgeItem, PlaybookItem, SessionMeta

logger = logging.getLogger(__name__)


async def load_knowledge_items(
    items: list[KnowledgeItem],
    firestore_client,
    embedding_service,
) -> int:
    """Generate embeddings and store knowledge items in Firestore.

    Args:
        items: Extracted knowledge items.
        firestore_client: FirestoreClient instance.
        embedding_service: Module with embed_texts function.

    Returns:
        Number of items stored.
    """
    if not items:
        return 0

    # Generate embeddings from search_text
    search_texts = [item.search_text for item in items]
    logger.info(f"Generating embeddings for {len(search_texts)} items...")
    embeddings = await embedding_service.embed_texts(search_texts)

    # Prepare documents for Firestore
    docs = []
    for item, embedding in zip(items, embeddings):
        doc = item.model_dump()
        doc["embedding"] = embedding
        # Convert tuple to list for Firestore
        doc["window"] = list(doc["window"])
        # Convert FailedAttempt models to dicts
        doc["failed_attempts"] = [fa.model_dump() for fa in item.failed_attempts]
        docs.append(doc)

    count = await firestore_client.store_knowledge_items(docs)
    return count


async def load_playbook_items(
    items: list[PlaybookItem],
    firestore_client,
    embedding_service,
) -> int:
    """Generate embeddings and store playbook items in Firestore."""
    if not items:
        return 0

    search_texts = [item.search_text for item in items]
    logger.info(f"Generating embeddings for {len(search_texts)} playbook items...")
    embeddings = await embedding_service.embed_texts(search_texts)

    docs = []
    for item, embedding in zip(items, embeddings):
        doc = item.model_dump()
        doc["embedding"] = embedding
        doc["window"] = list(doc["window"])
        docs.append(doc)

    count = await firestore_client.store_playbook_items(docs)
    return count


async def load_session_meta(
    session_meta: SessionMeta,
    firestore_client,
) -> str:
    """Store session metadata in Firestore."""
    return await firestore_client.store_session(session_meta.model_dump())
