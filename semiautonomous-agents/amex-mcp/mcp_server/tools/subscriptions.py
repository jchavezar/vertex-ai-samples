"""Subscription detection and audit tools."""

import json
import logging

from amex_job.storage import get_latest_statement

logger = logging.getLogger("amex-mcp.tools.subscriptions")


def register(mcp):
    @mcp.tool()
    def get_subscriptions() -> dict:
        """Get all detected recurring charges and subscriptions.

        Returns a list of subscriptions with merchant, amount, frequency,
        status (active/cancelled), and annual cost. Requires enrichment
        to have been run on at least 3 months of data.
        """
        stmt = get_latest_statement()
        if stmt is None:
            return {"error": "No statements found."}

        enrichment = stmt.get("enrichment", {})
        subscriptions = enrichment.get("subscriptions", [])
        audit = enrichment.get("subscription_audit", [])

        if not subscriptions:
            return {
                "error": "No subscriptions detected. Run enrich_statement on 3+ months of data first.",
                "period": stmt.get("period"),
            }

        active = [s for s in subscriptions if s.get("status") == "active"]
        total_monthly = sum(s.get("amount", 0) for s in active if s.get("frequency") == "monthly")
        total_annual = sum(s.get("annual_cost", 0) for s in active)

        return {
            "period": stmt.get("period"),
            "subscriptions": subscriptions,
            "subscription_audit": audit,
            "summary": {
                "total_active": len(active),
                "total_monthly_cost": round(total_monthly, 2),
                "total_annual_cost": round(total_annual, 2),
            },
        }
