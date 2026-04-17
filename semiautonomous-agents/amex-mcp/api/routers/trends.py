"""Spending trends endpoints."""

from collections import defaultdict

from fastapi import APIRouter, Query

from amex_job.storage import get_statements_range

router = APIRouter()


@router.get("/trends")
def get_trends(months: int = Query(6)):
    """Get month-over-month spending trends."""
    statements = get_statements_range(months)
    if not statements:
        return {"period_totals": [], "category_trends": {}, "member_totals": {}}

    trends: dict[str, list] = defaultdict(list)
    period_totals = []
    member_totals: dict[str, dict[str, float]] = {}

    for stmt in reversed(statements):  # oldest first
        period = stmt.get("period", "")
        period_sum = 0.0
        cat_sums: dict[str, float] = defaultdict(float)
        mem_sums: dict[str, float] = defaultdict(float)

        for txn in stmt.get("transactions", []):
            cat = txn.get("enriched_category") or txn.get("category", "Other") or "Other"
            amt = txn.get("amount", 0)
            cat_sums[cat] += amt
            period_sum += amt
            member = txn.get("card_member", "Unknown")
            mem_sums[member] += amt

        for cat, amt in cat_sums.items():
            trends[cat].append({"period": period, "amount": round(amt, 2)})

        period_totals.append({"period": period, "total": round(period_sum, 2)})
        member_totals[period] = {m: round(t, 2) for m, t in mem_sums.items()}

    return {
        "period_totals": period_totals,
        "category_trends": dict(trends),
        "member_totals": member_totals,
    }
