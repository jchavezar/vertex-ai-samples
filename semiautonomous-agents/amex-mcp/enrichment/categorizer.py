"""Stage 1: AI-powered expense categorization."""

import asyncio
import json
import logging

from enrichment.gemini_client import generate_json
from enrichment.merchant_lookup import match_lookup
from enrichment.prompts import CATEGORIZE_PROMPT, CATEGORIZE_SYSTEM

logger = logging.getLogger("amex-mcp.categorizer")

BATCH_SIZE = 25


async def categorize_transactions(
    transactions: list[dict],
    merchant_lookup: dict[str, dict] | None = None,
) -> list[dict]:
    """Categorize transactions using Gemini in batches.

    Adds enriched_category, subcategory, merchant_clean, and
    categorization_confidence to each transaction dict.

    If merchant_lookup is provided, web-verified merchant info is injected
    into the prompt so Gemini has accurate context for each transaction.
    """
    if not transactions:
        return transactions

    enriched = list(transactions)  # shallow copy
    batches = [enriched[i:i + BATCH_SIZE] for i in range(0, len(enriched), BATCH_SIZE)]

    logger.info(json.dumps({
        "event": "categorization_started",
        "total": len(transactions),
        "batches": len(batches),
    }))

    tasks = [
        _categorize_batch(batch, batch_idx, merchant_lookup)
        for batch_idx, batch in enumerate(batches)
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    offset = 0
    for batch_idx, result in enumerate(results):
        batch = batches[batch_idx]
        if isinstance(result, Exception):
            logger.error(json.dumps({
                "event": "batch_categorization_failed",
                "batch": batch_idx,
                "error": str(result),
            }))
            for i in range(len(batch)):
                enriched[offset + i]["enriched_category"] = "Unknown"
                enriched[offset + i]["subcategory"] = ""
                enriched[offset + i]["merchant_clean"] = enriched[offset + i].get("description", "")
                enriched[offset + i]["categorization_confidence"] = 0.0
                enriched[offset + i]["tags"] = []
                enriched[offset + i]["merchant_type"] = "unknown"
                enriched[offset + i]["purchase_channel"] = "unknown"
                enriched[offset + i]["purpose"] = "unknown"
        else:
            for item in result:
                idx = item.get("index", 0)
                if 0 <= idx < len(batch):
                    pos = offset + idx
                    enriched[pos]["enriched_category"] = item.get("enriched_category", "Other")
                    enriched[pos]["subcategory"] = item.get("subcategory", "")
                    enriched[pos]["merchant_clean"] = item.get("merchant_clean", enriched[pos].get("description", ""))
                    enriched[pos]["categorization_confidence"] = item.get("confidence", 0.5)
                    enriched[pos]["tags"] = item.get("tags", [])
                    enriched[pos]["merchant_type"] = item.get("merchant_type", "unknown")
                    enriched[pos]["purchase_channel"] = item.get("purchase_channel", "unknown")
                    enriched[pos]["purpose"] = item.get("purpose", "unknown")
        offset += len(batch)

    logger.info(json.dumps({"event": "categorization_completed", "total": len(enriched)}))
    return enriched


async def _categorize_batch(
    batch: list[dict],
    batch_idx: int,
    merchant_lookup: dict[str, dict] | None = None,
) -> list[dict]:
    """Categorize a single batch of transactions."""
    txn_summaries = []
    for i, t in enumerate(batch):
        summary = {
            "index": i,
            "description": t.get("description", ""),
            "amount": t.get("amount", 0),
            "category": t.get("category", ""),
            "date": t.get("date", ""),
        }
        # Inject web-verified merchant info if available
        if merchant_lookup:
            match = match_lookup(t.get("description", ""), merchant_lookup)
            if match:
                summary["verified_merchant"] = match.get("merchant_name", "")
                summary["verified_description"] = match.get("business_description", "")
                summary["verified_category"] = match.get("category_hint", "")
                summary["verified_subcategory"] = match.get("subcategory_hint", "")
                summary["verified_merchant_type"] = match.get("merchant_type_hint", "")
        txn_summaries.append(summary)

    prompt = CATEGORIZE_PROMPT.format(transactions_json=json.dumps(txn_summaries, indent=2))
    result = await generate_json(prompt, system_instruction=CATEGORIZE_SYSTEM)

    if isinstance(result, list):
        return result
    if isinstance(result, dict) and "transactions" in result:
        return result["transactions"]
    return []
