"""Spending category analysis tools."""

import json
import logging
from collections import defaultdict

from amex_job.storage import get_statement, get_statements_range

logger = logging.getLogger("amex-mcp.tools.categories")


def register(mcp):
    @mcp.tool()
    def get_spending_by_category(year: int, month: int) -> dict:
        """Get spending breakdown by category for a specific month.

        Args:
            year: Four-digit year
            month: Month 1-12

        Returns category totals, percentages, and transaction counts.
        Requires the statement to be enriched first.
        """
        stmt = get_statement(year, month)
        if stmt is None:
            return {"error": f"No statement found for {year:04d}-{month:02d}."}

        transactions = stmt.get("transactions", [])

        # Check if enrichment data exists at top level
        enrichment = stmt.get("enrichment", {})
        if enrichment.get("category_breakdown"):
            breakdown = enrichment["category_breakdown"]
        else:
            # Compute from transactions (works with or without enrichment)
            breakdown = defaultdict(float)
            for txn in transactions:
                cat = txn.get("enriched_category", txn.get("category", "Other")) or "Other"
                breakdown[cat] += txn.get("amount", 0)
            breakdown = {k: round(v, 2) for k, v in sorted(breakdown.items(), key=lambda x: -x[1])}

        total = sum(breakdown.values())
        categories = []
        for cat, amount in breakdown.items():
            pct = round(amount / total * 100, 1) if total > 0 else 0
            count = sum(1 for t in transactions if (t.get("enriched_category") or t.get("category", "Other")) == cat)
            categories.append({
                "category": cat,
                "amount": amount,
                "percentage": pct,
                "transaction_count": count,
            })

        return {
            "period": f"{year:04d}-{month:02d}",
            "total_spend": round(total, 2),
            "categories": categories,
        }

    @mcp.tool()
    def get_category_trends(months: int = 6) -> dict:
        """Get month-over-month spending trends by category.

        Args:
            months: Number of months to analyze (default 6)
        """
        statements = get_statements_range(months)
        if not statements:
            return {"error": "No statements found."}

        # Build {category: [{period, amount}]}
        trends: dict[str, list] = defaultdict(list)
        period_totals = []

        for stmt in reversed(statements):  # oldest first
            period = stmt.get("period", "")
            period_sum = 0.0
            cat_sums: dict[str, float] = defaultdict(float)
            for txn in stmt.get("transactions", []):
                cat = txn.get("enriched_category", txn.get("category", "Other")) or "Other"
                amt = txn.get("amount", 0)
                cat_sums[cat] += amt
                period_sum += amt

            for cat, amt in cat_sums.items():
                trends[cat].append({"period": period, "amount": round(amt, 2)})

            period_totals.append({"period": period, "total": round(period_sum, 2)})

        return {
            "months_analyzed": len(statements),
            "period_totals": period_totals,
            "category_trends": dict(trends),
        }

    @mcp.tool()
    def get_top_merchants(year: int, month: int, limit: int = 10) -> dict:
        """Get top merchants by spending for a specific month.

        Args:
            year: Four-digit year
            month: Month 1-12
            limit: Number of merchants to return (default 10)
        """
        stmt = get_statement(year, month)
        if stmt is None:
            return {"error": f"No statement found for {year:04d}-{month:02d}."}

        merchant_totals: dict[str, dict] = defaultdict(lambda: {"total": 0.0, "count": 0})
        for txn in stmt.get("transactions", []):
            name = txn.get("merchant_clean") or txn.get("description", "Unknown")
            merchant_totals[name]["total"] += txn.get("amount", 0)
            merchant_totals[name]["count"] += 1

        sorted_merchants = sorted(merchant_totals.items(), key=lambda x: -x[1]["total"])
        merchants = [
            {"merchant": name, "total": round(data["total"], 2), "transactions": data["count"]}
            for name, data in sorted_merchants[:limit]
        ]

        return {
            "period": f"{year:04d}-{month:02d}",
            "top_merchants": merchants,
        }
