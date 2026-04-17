"""Enrichment pipeline orchestrator — runs all stages in sequence."""

import json
import logging
import os
import sys

# Enable imports from parent directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from amex_job.credentials import get_gmail_access_token
from amex_job.storage import (
    get_statement,
    get_statements_range,
    is_enriched,
    update_transactions,
    write_enrichment,
)
from enrichment.categorizer import categorize_transactions
from enrichment.embedder import embed_transactions
from enrichment.merchant_lookup import lookup_merchants
from enrichment.insights import generate_insights
from enrichment.receipt_matcher import match_receipts
from enrichment.recommender import generate_recommendations
from enrichment.subscription_detector import detect_subscriptions

logger = logging.getLogger("amex-mcp.pipeline")


async def run_enrichment_pipeline(period: str, force: bool = False) -> dict:
    """Run the full enrichment pipeline for a statement period.

    Stages:
      0. Merchant lookup via Google Search grounding (Gemini + web)
      1. Categorize transactions with verified merchant context (Gemini)
      2. Detect subscriptions (deterministic + Gemini)
      3. Match receipts for ambiguous transactions (Gmail + Gemini)
      4. Generate spending insights (deterministic + Gemini)
      5. Generate recommendations (Gemini)

    Args:
        period: Statement period as "YYYY-MM"
        force: Re-run even if already enriched

    Returns:
        Enrichment result dict
    """
    logger.info(json.dumps({"event": "pipeline_started", "period": period, "force": force}))

    # Check if already enriched
    if not force and is_enriched(period):
        logger.info(json.dumps({"event": "pipeline_skipped", "period": period, "reason": "already_enriched"}))
        year, month = int(period[:4]), int(period[5:7])
        stmt = get_statement(year, month)
        return stmt.get("enrichment", {})

    # Load target statement
    year, month = int(period[:4]), int(period[5:7])
    statement = get_statement(year, month)
    if statement is None:
        raise ValueError(f"No statement found for {period}")

    transactions = statement.get("transactions", [])
    if not transactions:
        logger.warning(json.dumps({"event": "pipeline_skipped", "period": period, "reason": "no_transactions"}))
        return {"error": "No transactions to enrich"}

    # Load historical data for context
    historical = get_statements_range(months=6)

    # Stage 0: Merchant lookup via Google Search grounding
    logger.info(json.dumps({"event": "stage_0_merchant_lookup", "count": len(transactions)}))
    merchant_lookup = await lookup_merchants(transactions)

    # Stage 1: Categorize transactions (with web-verified merchant context)
    logger.info(json.dumps({"event": "stage_1_categorize", "count": len(transactions)}))
    enriched_txns = await categorize_transactions(transactions, merchant_lookup)

    # Stage 1.5: Embed transactions (vector for semantic search)
    logger.info(json.dumps({"event": "stage_1_5_embed", "count": len(enriched_txns)}))
    enriched_txns = await embed_transactions(enriched_txns)

    # Stage 2: Detect subscriptions (uses all available statements)
    logger.info(json.dumps({"event": "stage_2_subscriptions"}))
    # Temporarily update the current statement's transactions for subscription detection
    stmt_with_enriched = {**statement, "transactions": enriched_txns}
    all_stmts = [stmt_with_enriched] + [h for h in historical if h.get("period") != period]
    subscriptions = await detect_subscriptions(all_stmts)

    # Stage 3: Match receipts for ambiguous transactions
    logger.info(json.dumps({"event": "stage_3_receipts"}))
    try:
        gmail_token = get_gmail_access_token()
        receipt_results = await match_receipts(enriched_txns, gmail_token)

        # Merge receipt data back into enriched transactions
        for r in receipt_results:
            idx = r.pop("_original_index", None)
            if idx is not None and 0 <= idx < len(enriched_txns):
                enriched_txns[idx]["receipt_found"] = r.get("receipt_found", False)
                enriched_txns[idx]["receipt_details"] = r.get("receipt_details")
    except Exception as e:
        logger.warning(json.dumps({
            "event": "receipt_matching_skipped",
            "error": str(e),
        }))

    # Stage 4: Generate insights
    logger.info(json.dumps({"event": "stage_4_insights"}))
    stmt_for_insights = {**statement, "transactions": enriched_txns}
    insights = await generate_insights(stmt_for_insights, historical)

    # Stage 5: Generate recommendations
    logger.info(json.dumps({"event": "stage_5_recommendations"}))
    recommendations = await generate_recommendations(historical, subscriptions, insights)

    # Build enrichment result
    enrichment = {
        "version": 1,
        "category_breakdown": insights.get("category_breakdown", {}),
        "top_merchants": insights.get("top_merchants", []),
        "month_over_month": insights.get("month_over_month", {}),
        "subscriptions": subscriptions,
        "highlights": insights.get("highlights", []),
        "anomalies": insights.get("anomalies", []),
        "trends": insights.get("trends", []),
        "recommendations": recommendations.get("recommendations", []),
        "subscription_audit": recommendations.get("subscription_audit", []),
        "spending_score": recommendations.get("spending_score", 0),
        "score_explanation": recommendations.get("score_explanation", ""),
    }

    # Write enriched transactions and enrichment metadata to Firestore
    update_transactions(period, enriched_txns)
    write_enrichment(period, enrichment)

    logger.info(json.dumps({
        "event": "pipeline_completed",
        "period": period,
        "categories": len(enrichment["category_breakdown"]),
        "subscriptions": len(subscriptions),
        "score": enrichment["spending_score"],
    }))

    return enrichment
