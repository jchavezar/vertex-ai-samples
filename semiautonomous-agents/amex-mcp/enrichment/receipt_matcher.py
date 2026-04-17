"""Stage 3: Gmail receipt matching for ambiguous transactions."""

import asyncio
import base64
import json
import logging
import re

import requests

from enrichment.gemini_client import generate_json
from enrichment.prompts import RECEIPT_QUERY_PROMPT, RECEIPT_EXTRACT_PROMPT

logger = logging.getLogger("amex-mcp.receipts")

# Merchants whose descriptions are typically ambiguous
AMBIGUOUS_PATTERNS = re.compile(
    r"APPLE\.COM|AMZN|AMAZON|GOOGLE|PAYPAL|SQ \*|SQUARE|"
    r"VENMO|ZELLE|CASH APP|STRIPE",
    re.IGNORECASE,
)

_gmail_semaphore = asyncio.Semaphore(2)


def _is_ambiguous(txn: dict) -> bool:
    """Check if a transaction needs receipt matching."""
    confidence = txn.get("categorization_confidence", 1.0)
    if confidence < 0.7:
        return True
    desc = txn.get("description", "")
    return bool(AMBIGUOUS_PATTERNS.search(desc))


def _extract_email_body(payload: dict) -> str:
    """Extract text body from Gmail message payload."""
    mime = payload.get("mimeType", "")
    if mime in ("text/plain", "text/html") and payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")
    for part in payload.get("parts", []):
        result = _extract_email_body(part)
        if result:
            return result
    return ""


async def match_receipts(
    transactions: list[dict],
    gmail_access_token: str,
) -> list[dict]:
    """Match ambiguous transactions with Gmail receipts.

    Returns only the transactions that were processed, with receipt fields added.
    """
    ambiguous = [(i, txn) for i, txn in enumerate(transactions) if _is_ambiguous(txn)]

    if not ambiguous:
        logger.info(json.dumps({"event": "no_ambiguous_transactions"}))
        return []

    logger.info(json.dumps({
        "event": "receipt_matching_started",
        "ambiguous_count": len(ambiguous),
        "total_count": len(transactions),
    }))

    tasks = [
        _match_single(txn, gmail_access_token)
        for _, txn in ambiguous
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    matched = []
    for (orig_idx, txn), result in zip(ambiguous, results):
        if isinstance(result, Exception):
            logger.warning(json.dumps({
                "event": "receipt_match_failed",
                "description": txn.get("description", ""),
                "error": str(result),
            }))
            txn["receipt_found"] = False
            txn["receipt_details"] = None
        else:
            txn["receipt_found"] = result.get("receipt_found", False)
            txn["receipt_details"] = result if result.get("receipt_found") else None
        txn["_original_index"] = orig_idx
        matched.append(txn)

    found_count = sum(1 for t in matched if t.get("receipt_found"))
    logger.info(json.dumps({
        "event": "receipt_matching_completed",
        "processed": len(matched),
        "found": found_count,
    }))
    return matched


async def _match_single(txn: dict, gmail_access_token: str) -> dict:
    """Match a single transaction with a Gmail receipt."""
    description = txn.get("description", "")
    amount = txn.get("amount", 0)
    date = txn.get("date", "")

    # Step 1: Generate Gmail search query
    prompt = RECEIPT_QUERY_PROMPT.format(
        description=description, amount=amount, date=date
    )
    query_result = await generate_json(prompt)
    gmail_query = query_result.get("gmail_query", "")

    if not gmail_query:
        return {"receipt_found": False}

    # Step 2: Search Gmail
    async with _gmail_semaphore:
        headers = {"Authorization": f"Bearer {gmail_access_token}"}
        search_resp = await asyncio.to_thread(
            requests.get,
            "https://gmail.googleapis.com/gmail/v1/users/me/messages",
            headers=headers,
            params={"q": gmail_query, "maxResults": 3},
        )
        search_resp.raise_for_status()
        messages = search_resp.json().get("messages", [])

    if not messages:
        return {"receipt_found": False}

    # Step 3: Get email body
    msg_id = messages[0]["id"]
    async with _gmail_semaphore:
        msg_resp = await asyncio.to_thread(
            requests.get,
            f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}",
            headers={"Authorization": f"Bearer {gmail_access_token}"},
            params={"format": "full"},
        )
        msg_resp.raise_for_status()

    payload = msg_resp.json().get("payload", {})
    email_body = _extract_email_body(payload) or msg_resp.json().get("snippet", "")

    # Truncate to avoid exceeding context
    if len(email_body) > 3000:
        email_body = email_body[:3000]

    # Step 4: Extract receipt details
    extract_prompt = RECEIPT_EXTRACT_PROMPT.format(
        description=description,
        amount=amount,
        date=date,
        email_body=email_body,
    )
    return await generate_json(extract_prompt)
