"""Stage 4: Spending analytics and insights."""

import json
import logging
from collections import defaultdict

from enrichment.gemini_client import generate_json
from enrichment.prompts import INSIGHTS_PROMPT, INSIGHTS_SYSTEM

logger = logging.getLogger("amex-mcp.insights")


def _compute_category_breakdown(transactions: list[dict]) -> dict[str, float]:
    """Sum spending by enriched category."""
    breakdown: dict[str, float] = defaultdict(float)
    for txn in transactions:
        cat = txn.get("enriched_category", txn.get("category", "Other")) or "Other"
        breakdown[cat] += txn.get("amount", 0)
    return {k: round(v, 2) for k, v in sorted(breakdown.items(), key=lambda x: -x[1])}


def _compute_top_merchants(transactions: list[dict], limit: int = 10) -> list[dict]:
    """Top merchants by total spend."""
    merchant_totals: dict[str, float] = defaultdict(float)
    for txn in transactions:
        name = txn.get("merchant_clean") or txn.get("description", "Unknown")
        merchant_totals[name] += txn.get("amount", 0)
    sorted_merchants = sorted(merchant_totals.items(), key=lambda x: -x[1])
    return [
        {"merchant": m, "total": round(t, 2)}
        for m, t in sorted_merchants[:limit]
    ]


async def generate_insights(statement: dict, historical: list[dict]) -> dict:
    """Generate spending insights for a statement.

    Combines deterministic analytics with Gemini narrative generation.
    """
    transactions = statement.get("transactions", [])
    period = statement.get("period", "")
    total_spend = statement.get("total_debits", 0)

    category_breakdown = _compute_category_breakdown(transactions)
    top_merchants = _compute_top_merchants(transactions)

    # Build prior month comparison
    comparison = {}
    for hist in historical:
        if hist.get("period") != period:
            hist_breakdown = _compute_category_breakdown(hist.get("transactions", []))
            comparison[hist["period"]] = {
                "total_spend": hist.get("total_debits", 0),
                "category_breakdown": hist_breakdown,
            }

    # Month-over-month change
    mom = {}
    if historical:
        prior = [h for h in historical if h.get("period", "") < period]
        if prior:
            prev = prior[0]
            prev_total = prev.get("total_debits", 0)
            if prev_total > 0:
                mom = {
                    "previous_period": prev["period"],
                    "previous_total": prev_total,
                    "change_pct": round((total_spend - prev_total) / prev_total * 100, 1),
                }

    logger.info(json.dumps({
        "event": "insights_computation_started",
        "period": period,
        "categories": len(category_breakdown),
    }))

    # Gemini narrative
    prompt = INSIGHTS_PROMPT.format(
        period=period,
        total_spend=total_spend,
        category_breakdown_json=json.dumps(category_breakdown, indent=2),
        top_merchants_json=json.dumps(top_merchants, indent=2),
        comparison_json=json.dumps(comparison, indent=2) if comparison else "No prior data available",
    )

    try:
        narrative = await generate_json(prompt, system_instruction=INSIGHTS_SYSTEM)
    except Exception as e:
        logger.error(json.dumps({"event": "insights_generation_failed", "error": str(e)}))
        narrative = {"highlights": [], "anomalies": [], "trends": []}

    result = {
        "category_breakdown": category_breakdown,
        "top_merchants": top_merchants,
        "month_over_month": mom,
        "highlights": narrative.get("highlights", []),
        "anomalies": narrative.get("anomalies", []),
        "trends": narrative.get("trends", []),
    }

    logger.info(json.dumps({"event": "insights_generated", "period": period}))
    return result
