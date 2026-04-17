"""Spending insights and recommendations tools."""

import json
import logging

from amex_job.storage import get_statement, get_latest_statement

logger = logging.getLogger("amex-mcp.tools.insights")


def register(mcp):
    @mcp.tool()
    def get_spending_insights(year: int, month: int) -> dict:
        """Get AI-generated spending insights for a specific month.

        Returns highlights, anomalies, trends, and category analysis.
        Requires the statement to be enriched first.

        Args:
            year: Four-digit year
            month: Month 1-12
        """
        stmt = get_statement(year, month)
        if stmt is None:
            return {"error": f"No statement found for {year:04d}-{month:02d}."}

        enrichment = stmt.get("enrichment", {})
        if not enrichment.get("enriched_at"):
            return {
                "error": f"Statement {year:04d}-{month:02d} has not been enriched yet. Run enrich_statement first.",
            }

        return {
            "period": f"{year:04d}-{month:02d}",
            "total_spend": stmt.get("total_debits", 0),
            "category_breakdown": enrichment.get("category_breakdown", {}),
            "top_merchants": enrichment.get("top_merchants", []),
            "month_over_month": enrichment.get("month_over_month", {}),
            "highlights": enrichment.get("highlights", []),
            "anomalies": enrichment.get("anomalies", []),
            "trends": enrichment.get("trends", []),
            "spending_score": enrichment.get("spending_score", 0),
        }

    @mcp.tool()
    def get_recommendations() -> dict:
        """Get AI financial recommendations based on recent spending patterns.

        Returns actionable savings suggestions, subscription audit results,
        and an overall spending health score (1-100).
        """
        stmt = get_latest_statement()
        if stmt is None:
            return {"error": "No statements found."}

        enrichment = stmt.get("enrichment", {})
        if not enrichment.get("enriched_at"):
            return {"error": "Latest statement has not been enriched. Run enrich_statement first."}

        return {
            "period": stmt.get("period"),
            "spending_score": enrichment.get("spending_score", 0),
            "score_explanation": enrichment.get("score_explanation", ""),
            "recommendations": enrichment.get("recommendations", []),
            "subscription_audit": enrichment.get("subscription_audit", []),
        }
