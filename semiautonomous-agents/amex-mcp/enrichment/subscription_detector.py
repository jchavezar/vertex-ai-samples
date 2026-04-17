"""Stage 2: Recurring charge / subscription detection."""

import json
import logging
import re
from collections import defaultdict

from enrichment.gemini_client import generate_json
from enrichment.prompts import SUBSCRIPTION_DETECT_PROMPT, SUBSCRIPTION_DETECT_SYSTEM

logger = logging.getLogger("amex-mcp.subscriptions")


def _normalize_merchant(description: str) -> str:
    """Normalize merchant name for grouping."""
    s = description.upper().strip()
    # Remove common prefixes
    for prefix in ["SQ *", "TST* ", "SP * ", "PAYPAL *", "GOOGLE *"]:
        if s.startswith(prefix):
            s = s[len(prefix):]
    # Remove trailing location/reference info
    s = re.sub(r'\s+(#\d+|[A-Z]{2}\s*\d{5}|[A-Z]{2}$)', '', s)
    s = re.sub(r'\s{2,}', ' ', s).strip()
    return s


async def detect_subscriptions(statements: list[dict]) -> list[dict]:
    """Detect recurring charges across multiple months of statements.

    First pass: deterministic grouping by merchant/amount patterns.
    Second pass: Gemini verification and enrichment.
    """
    if not statements:
        return []

    # Collect all transactions with their periods
    merchant_history: dict[str, list[dict]] = defaultdict(list)
    for stmt in statements:
        period = stmt.get("period", "")
        for txn in stmt.get("transactions", []):
            key = _normalize_merchant(txn.get("description", ""))
            if key:
                merchant_history[key].append({
                    "period": period,
                    "date": txn.get("date", ""),
                    "amount": txn.get("amount", 0),
                    "description": txn.get("description", ""),
                    "enriched_category": txn.get("enriched_category", ""),
                    "merchant_clean": txn.get("merchant_clean", ""),
                })

    # Deterministic filter: merchants appearing in 3+ months with similar amounts
    candidates = {}
    for merchant, txns in merchant_history.items():
        periods = set(t["period"] for t in txns)
        if len(periods) < 3:
            continue

        amounts = [t["amount"] for t in txns]
        avg_amount = sum(amounts) / len(amounts)
        if avg_amount == 0:
            continue

        # Check amount variance — within 20%
        variance_ok = all(abs(a - avg_amount) / avg_amount < 0.20 for a in amounts)
        if variance_ok:
            candidates[merchant] = {
                "merchant": merchant,
                "transactions": sorted(txns, key=lambda t: t["date"]),
                "avg_amount": round(avg_amount, 2),
                "occurrences": len(txns),
                "months_seen": len(periods),
            }

    if not candidates:
        logger.info(json.dumps({"event": "no_subscription_candidates"}))
        return []

    logger.info(json.dumps({
        "event": "subscription_candidates_found",
        "count": len(candidates),
    }))

    # Gemini verification
    prompt = SUBSCRIPTION_DETECT_PROMPT.format(
        candidates_json=json.dumps(list(candidates.values()), indent=2)
    )

    try:
        result = await generate_json(prompt, system_instruction=SUBSCRIPTION_DETECT_SYSTEM)
        subscriptions = result if isinstance(result, list) else result.get("subscriptions", [])
    except Exception as e:
        logger.error(json.dumps({"event": "subscription_detection_failed", "error": str(e)}))
        # Fall back to deterministic results
        subscriptions = []
        for c in candidates.values():
            txns = c["transactions"]
            subscriptions.append({
                "merchant": txns[0].get("merchant_clean") or c["merchant"],
                "amount": c["avg_amount"],
                "frequency": "monthly",
                "category": txns[0].get("enriched_category", "Subscriptions"),
                "first_seen": txns[0]["date"],
                "last_seen": txns[-1]["date"],
                "status": "active",
                "annual_cost": round(c["avg_amount"] * 12, 2),
            })

    logger.info(json.dumps({
        "event": "subscriptions_detected",
        "count": len(subscriptions),
    }))
    return subscriptions
