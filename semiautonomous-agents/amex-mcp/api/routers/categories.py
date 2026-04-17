"""Category breakdown and Sankey diagram endpoints."""

from collections import defaultdict

from fastapi import APIRouter, HTTPException

from amex_job.storage import get_statement

router = APIRouter()


@router.get("/categories/{period}")
def get_categories(period: str):
    """Get spending breakdown by category for a period."""
    year, month = int(period[:4]), int(period[5:7])
    stmt = get_statement(year, month)
    if stmt is None:
        raise HTTPException(status_code=404, detail=f"No statement for {period}")

    transactions = stmt.get("transactions", [])

    # Compute from transactions
    cat_totals: dict[str, float] = defaultdict(float)
    cat_counts: dict[str, int] = defaultdict(int)
    for txn in transactions:
        cat = txn.get("enriched_category") or txn.get("category", "Other") or "Other"
        cat_totals[cat] += txn.get("amount", 0)
        cat_counts[cat] += 1

    total = sum(cat_totals.values())
    categories = []
    for cat, amount in sorted(cat_totals.items(), key=lambda x: -x[1]):
        categories.append({
            "category": cat,
            "amount": round(amount, 2),
            "percentage": round(amount / total * 100, 1) if total > 0 else 0,
            "count": cat_counts[cat],
        })

    return {
        "period": period,
        "total_spend": round(total, 2),
        "categories": categories,
    }


@router.get("/sankey/{period}")
def get_sankey(period: str):
    """Get Sankey diagram data: category → top merchants (Monarch-style).

    Every category gets its top merchants (up to 3 each), ensuring all
    categories have visible flows. Nodes include amount metadata for labels.
    """
    year, month = int(period[:4]), int(period[5:7])
    stmt = get_statement(year, month)
    if stmt is None:
        raise HTTPException(status_code=404, detail=f"No statement for {period}")

    transactions = stmt.get("transactions", [])

    # Build category → merchant → total
    cat_merchant: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    cat_totals: dict[str, float] = defaultdict(float)
    for txn in transactions:
        cat = txn.get("enriched_category") or txn.get("category", "Other") or "Other"
        merchant = txn.get("merchant_clean") or txn.get("description", "Unknown")
        amt = txn.get("amount", 0)
        if amt > 0:
            cat_merchant[cat][merchant] += amt
            cat_totals[cat] += amt

    total_spend = sum(cat_totals.values())

    # For each category, pick top 3 merchants — ensures every category has flows
    selected_merchants: dict[str, float] = {}
    cat_top: dict[str, list[tuple[str, float]]] = {}
    for cat, merchants in cat_merchant.items():
        sorted_m = sorted(merchants.items(), key=lambda x: -x[1])
        top = sorted_m[:3]
        cat_top[cat] = top
        for m, amt in top:
            if m in selected_merchants:
                selected_merchants[m] = max(selected_merchants[m], amt)
            else:
                selected_merchants[m] = amt

    # Sort categories by total descending
    sorted_cats = sorted(cat_totals.keys(), key=lambda c: -cat_totals[c])

    # Build ordered merchant list (preserve per-category grouping)
    merchant_order = []
    seen = set()
    for cat in sorted_cats:
        for m, _ in cat_top.get(cat, []):
            if m not in seen:
                merchant_order.append(m)
                seen.add(m)

    # Build nodes: categories (left), then merchants (right)
    nodes = []
    for cat in sorted_cats:
        pct = round(cat_totals[cat] / total_spend * 100, 1) if total_spend else 0
        nodes.append({
            "name": cat,
            "amount": round(cat_totals[cat], 2),
            "percentage": pct,
            "side": "left",
        })

    cat_count = len(sorted_cats)
    for m in merchant_order:
        # Sum across all categories for this merchant
        m_total = sum(merchants.get(m, 0) for merchants in cat_merchant.values())
        nodes.append({
            "name": m,
            "amount": round(m_total, 2),
            "side": "right",
        })

    cat_idx = {c: i for i, c in enumerate(sorted_cats)}
    merchant_idx = {m: cat_count + i for i, m in enumerate(merchant_order)}

    # Build links with category color info
    links = []
    for cat in sorted_cats:
        for m, amt in cat_top.get(cat, []):
            links.append({
                "source": cat_idx[cat],
                "target": merchant_idx[m],
                "value": round(amt, 2),
                "sourceCategory": cat,
            })

    return {"nodes": nodes, "links": links}
