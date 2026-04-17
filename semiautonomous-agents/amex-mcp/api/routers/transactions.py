"""Transaction query endpoints."""

from fastapi import APIRouter, Query

from amex_job.storage import structured_query

router = APIRouter()


@router.get("/transactions")
def list_transactions(
    period: str | None = Query(None),
    category: str | None = Query(None),
    card_member: str | None = Query(None),
    search: str | None = Query(None),
):
    """Get filtered transactions."""
    filters = {}
    if period:
        filters["period"] = period
    if category:
        filters["category"] = category
    if card_member:
        filters["card_member"] = card_member

    results = structured_query(filters if filters else None)

    if search:
        q = search.lower()
        results = [
            t for t in results
            if q in (t.get("description") or "").lower()
            or q in (t.get("merchant_clean") or "").lower()
            or q in (t.get("enriched_category") or "").lower()
        ]

    results.sort(key=lambda t: t.get("date", ""), reverse=True)

    # Strip embeddings to keep response small
    for t in results:
        t.pop("embedding", None)

    return results
