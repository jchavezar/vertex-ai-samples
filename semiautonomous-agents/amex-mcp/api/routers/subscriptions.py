"""Subscription endpoints."""

from fastapi import APIRouter

from amex_job.storage import get_statements_range

router = APIRouter()


@router.get("/subscriptions")
def get_subscriptions():
    """Get subscription data from the latest enriched statement."""
    statements = get_statements_range(1)
    if not statements:
        return {"subscriptions": [], "audit": []}

    enrichment = statements[0].get("enrichment", {})
    return {
        "subscriptions": enrichment.get("subscriptions", []),
        "audit": enrichment.get("subscription_audit", []),
    }
