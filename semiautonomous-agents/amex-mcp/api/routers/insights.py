"""AI insights endpoints."""

from fastapi import APIRouter, HTTPException

from amex_job.storage import get_statement

router = APIRouter()


@router.get("/insights/{period}")
def get_insights(period: str):
    """Get AI-generated insights for a period."""
    year, month = int(period[:4]), int(period[5:7])
    stmt = get_statement(year, month)
    if stmt is None:
        raise HTTPException(status_code=404, detail=f"No statement for {period}")

    enrichment = stmt.get("enrichment", {})
    return {
        "highlights": enrichment.get("highlights", []),
        "anomalies": enrichment.get("anomalies", []),
        "ai_trends": enrichment.get("trends", []),
        "recommendations": enrichment.get("recommendations", []),
        "spending_score": enrichment.get("spending_score", 0),
        "score_explanation": enrichment.get("score_explanation", ""),
    }
