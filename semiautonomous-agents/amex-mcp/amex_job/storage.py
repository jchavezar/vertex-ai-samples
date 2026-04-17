"""Firestore helpers for Amex statement storage."""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Optional

from google.cloud import firestore
from google.cloud.firestore_v1.vector import Vector
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure

logger = logging.getLogger("amex-job.storage")

COLLECTION = os.environ.get("FIRESTORE_COLLECTION", "amex_statements")
TXN_COLLECTION = os.environ.get("FIRESTORE_TXN_COLLECTION", "amex_transactions")
PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "vtxdemos")

_db: Optional[firestore.Client] = None


def _get_db() -> firestore.Client:
    global _db
    if _db is None:
        _db = firestore.Client(project=PROJECT_ID)
    return _db


def write_statement(data: dict) -> None:
    """Write a statement document to Firestore (upsert)."""
    db = _get_db()
    period = data["period"]
    data["fetched_at"] = datetime.now(timezone.utc).isoformat()
    db.collection(COLLECTION).document(period).set(data)
    logger.info(json.dumps({"event": "statement_written", "period": period}))


def statement_exists(period: str) -> bool:
    """Check if a statement document exists for the given period."""
    db = _get_db()
    doc = db.collection(COLLECTION).document(period).get()
    return doc.exists


def get_latest_statement() -> Optional[dict]:
    """Return the most recent statement, or None if empty."""
    db = _get_db()
    docs = (
        db.collection(COLLECTION)
        .order_by("period", direction=firestore.Query.DESCENDING)
        .limit(1)
        .stream()
    )
    for doc in docs:
        return doc.to_dict()
    return None


def get_statement(year: int, month: int) -> Optional[dict]:
    """Return statement for a specific month, or None if not found."""
    db = _get_db()
    period = f"{year:04d}-{month:02d}"
    doc = db.collection(COLLECTION).document(period).get()
    if doc.exists:
        return doc.to_dict()
    return None


def get_statements_range(months: int = 6) -> list[dict]:
    """Return the most recent N statements, ordered newest-first."""
    db = _get_db()
    docs = (
        db.collection(COLLECTION)
        .order_by("period", direction=firestore.Query.DESCENDING)
        .limit(months)
        .stream()
    )
    return [doc.to_dict() for doc in docs]


def get_all_statements() -> list[dict]:
    """Return all statements, ordered newest-first."""
    db = _get_db()
    docs = (
        db.collection(COLLECTION)
        .order_by("period", direction=firestore.Query.DESCENDING)
        .stream()
    )
    return [doc.to_dict() for doc in docs]


def is_enriched(period: str) -> bool:
    """Check if a statement has already been enriched."""
    db = _get_db()
    doc = db.collection(COLLECTION).document(period).get()
    if not doc.exists:
        return False
    data = doc.to_dict()
    return "enrichment" in data and data["enrichment"].get("enriched_at") is not None


def write_enrichment(period: str, enrichment_data: dict) -> None:
    """Merge enrichment data into an existing statement document.

    Updates individual transaction fields inline and adds the top-level
    'enrichment' object with category_breakdown, subscriptions, insights, etc.
    """
    db = _get_db()
    doc_ref = db.collection(COLLECTION).document(period)

    enrichment_data["enriched_at"] = datetime.now(timezone.utc).isoformat()
    doc_ref.update({"enrichment": enrichment_data})
    logger.info(json.dumps({"event": "enrichment_written", "period": period}))


def update_transactions(period: str, transactions: list[dict]) -> None:
    """Replace the transactions array and write denormalized transaction docs.

    Embeddings are stripped from the main statement doc (to stay under 1MB)
    and only stored in the denormalized amex_transactions collection.
    """
    db = _get_db()
    doc_ref = db.collection(COLLECTION).document(period)
    # Strip embeddings from main doc to avoid 1MB Firestore limit
    txns_without_embeddings = [
        {k: v for k, v in txn.items() if k != "embedding"}
        for txn in transactions
    ]
    doc_ref.update({"transactions": txns_without_embeddings})

    # Write each transaction as a separate doc in the txns subcollection
    # for vector search with pre-filtering
    txn_coll = db.collection(TXN_COLLECTION)
    batch = db.batch()
    batch_count = 0
    for i, txn in enumerate(transactions):
        doc_id = f"{period}_{i:04d}"
        doc_data = {
            "period": period,
            "date": txn.get("date", ""),
            "description": txn.get("description", ""),
            "amount": txn.get("amount", 0),
            "card_member": txn.get("card_member", ""),
            "enriched_category": txn.get("enriched_category", ""),
            "subcategory": txn.get("subcategory", ""),
            "merchant_clean": txn.get("merchant_clean", ""),
            "tags": txn.get("tags", []),
            "merchant_type": txn.get("merchant_type", "unknown"),
            "purchase_channel": txn.get("purchase_channel", "unknown"),
            "purpose": txn.get("purpose", "unknown"),
            "categorization_confidence": txn.get("categorization_confidence", 0),
        }
        if txn.get("embedding"):
            doc_data["embedding"] = Vector(txn["embedding"])
        batch.set(txn_coll.document(doc_id), doc_data)
        batch_count += 1
        if batch_count >= 400:  # Firestore batch limit is 500
            batch.commit()
            batch = db.batch()
            batch_count = 0
    if batch_count > 0:
        batch.commit()

    logger.info(json.dumps({
        "event": "transactions_updated",
        "period": period,
        "denormalized": len(transactions),
    }))


# ---------------------------------------------------------------------------
# Denormalized transaction collection for hybrid search
# ---------------------------------------------------------------------------


def semantic_search(
    query_vector: list[float],
    filters: dict | None = None,
    limit: int = 1000,
    distance_threshold: float = 0.4,
) -> list[dict]:
    """Vector search with optional structured pre-filtering.

    Uses Firestore find_nearest (exact KNN at this scale) with
    pre-filters on structured fields applied before the vector scan.

    Args:
        query_vector: Embedded query (768d from gemini-embedding-001)
        filters: Optional dict with keys like date_after, date_before,
                 category, card_member, merchant_type, purchase_channel, purpose
        limit: Max results (default 1000 for full recall at small scale)
        distance_threshold: Max cosine distance (lower = more relevant)
    """
    db = _get_db()
    query = db.collection(TXN_COLLECTION)

    if filters:
        if filters.get("date_after"):
            query = query.where("date", ">=", filters["date_after"])
        if filters.get("date_before"):
            query = query.where("date", "<=", filters["date_before"])
        if filters.get("category"):
            query = query.where("enriched_category", "==", filters["category"])
        if filters.get("card_member"):
            query = query.where("card_member", "==", filters["card_member"])
        if filters.get("merchant_type"):
            query = query.where("merchant_type", "==", filters["merchant_type"])
        if filters.get("purchase_channel"):
            query = query.where("purchase_channel", "==", filters["purchase_channel"])
        if filters.get("purpose"):
            query = query.where("purpose", "==", filters["purpose"])
        if filters.get("period"):
            query = query.where("period", "==", filters["period"])

    results = query.find_nearest(
        vector_field="embedding",
        query_vector=Vector(query_vector),
        distance_measure=DistanceMeasure.COSINE,
        limit=limit,
        distance_threshold=distance_threshold,
    ).stream()

    return [doc.to_dict() for doc in results]


def structured_query(filters: dict | None = None) -> list[dict]:
    """Query all transactions matching structured filters (no vector search).

    Returns ALL matching rows — no top-K limit.
    """
    db = _get_db()
    query = db.collection(TXN_COLLECTION)

    if filters:
        if filters.get("date_after"):
            query = query.where("date", ">=", filters["date_after"])
        if filters.get("date_before"):
            query = query.where("date", "<=", filters["date_before"])
        if filters.get("category"):
            query = query.where("enriched_category", "==", filters["category"])
        if filters.get("card_member"):
            query = query.where("card_member", "==", filters["card_member"])
        if filters.get("merchant_type"):
            query = query.where("merchant_type", "==", filters["merchant_type"])
        if filters.get("purchase_channel"):
            query = query.where("purchase_channel", "==", filters["purchase_channel"])
        if filters.get("purpose"):
            query = query.where("purpose", "==", filters["purpose"])
        if filters.get("period"):
            query = query.where("period", "==", filters["period"])

    return [doc.to_dict() for doc in query.stream()]
