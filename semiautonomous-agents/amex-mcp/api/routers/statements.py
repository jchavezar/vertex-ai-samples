"""Statement endpoints."""

from fastapi import APIRouter, HTTPException

from amex_job.storage import get_all_statements, get_statement

router = APIRouter()


@router.get("/statements")
def list_statements():
    """List all statement periods with summary info."""
    statements = get_all_statements()
    return [
        {
            "period": s.get("period", ""),
            "total_debits": round(s.get("total_debits", 0), 2),
            "total_credits": round(s.get("total_credits", 0), 2),
            "transaction_count": len(s.get("transactions", [])),
        }
        for s in statements
    ]


@router.get("/statements/{period}")
def get_statement_detail(period: str):
    """Get full statement for a period (e.g. 2026-04)."""
    year, month = int(period[:4]), int(period[5:7])
    stmt = get_statement(year, month)
    if stmt is None:
        raise HTTPException(status_code=404, detail=f"No statement for {period}")
    return stmt
