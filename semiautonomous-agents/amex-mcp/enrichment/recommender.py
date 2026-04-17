"""Stage 5: AI-powered financial recommendations."""

import json
import logging

from enrichment.gemini_client import generate_json
from enrichment.prompts import RECOMMENDATIONS_PROMPT, RECOMMENDATIONS_SYSTEM

logger = logging.getLogger("amex-mcp.recommender")


async def generate_recommendations(
    statements: list[dict],
    subscriptions: list[dict],
    insights: dict,
) -> dict:
    """Generate financial recommendations from multi-month spending data."""
    # Build monthly summaries
    summaries = []
    for stmt in statements:
        summaries.append({
            "period": stmt.get("period", ""),
            "total_spend": stmt.get("total_debits", 0),
            "total_credits": stmt.get("total_credits", 0),
            "transaction_count": stmt.get("total_transactions", 0),
        })

    anomalies = insights.get("anomalies", [])

    prompt = RECOMMENDATIONS_PROMPT.format(
        num_months=len(summaries),
        summaries_json=json.dumps(summaries, indent=2),
        subscriptions_json=json.dumps(subscriptions, indent=2),
        anomalies_json=json.dumps(anomalies, indent=2),
    )

    logger.info(json.dumps({"event": "recommendations_started"}))

    try:
        result = await generate_json(prompt, system_instruction=RECOMMENDATIONS_SYSTEM)
    except Exception as e:
        logger.error(json.dumps({
            "event": "recommendations_failed",
            "error": str(e),
        }))
        return {
            "recommendations": [],
            "subscription_audit": [],
            "spending_score": 0,
            "score_explanation": "Unable to generate recommendations.",
        }

    logger.info(json.dumps({
        "event": "recommendations_generated",
        "score": result.get("spending_score", 0),
        "count": len(result.get("recommendations", [])),
    }))
    return result
