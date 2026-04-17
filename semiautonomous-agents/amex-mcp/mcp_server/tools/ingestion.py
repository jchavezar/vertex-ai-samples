"""CSV ingestion (fallback) and enrichment trigger tools."""

import asyncio
import json
import logging
import re
from datetime import datetime, timezone

from amex_job.parser import parse_statement_csv
from amex_job.storage import statement_exists, write_statement, get_statement
from enrichment.pipeline import run_enrichment_pipeline

logger = logging.getLogger("amex-mcp.tools.ingestion")


def _detect_period(csv_content: str) -> str:
    """Try to detect the statement period from CSV dates."""
    dates = re.findall(r'(\d{1,2})/(\d{1,2})/(\d{2,4})', csv_content)
    if not dates:
        return datetime.now(timezone.utc).strftime("%Y-%m")
    # Use the most common month/year combo
    from collections import Counter
    periods = []
    for m, _, y in dates:
        yr = int(y)
        if yr < 100:
            yr += 2000
        periods.append(f"{yr:04d}-{int(m):02d}")
    if periods:
        most_common = Counter(periods).most_common(1)[0][0]
        return most_common
    return datetime.now(timezone.utc).strftime("%Y-%m")


def register(mcp):
    @mcp.tool()
    def ingest_amex_csv(csv_content: str, period: str = "") -> dict:
        """Manually ingest an Amex CSV statement (fallback if automated download is unavailable).

        Args:
            csv_content: Raw CSV file content from Amex statement download
            period: Statement period as "YYYY-MM" (auto-detected if omitted)
        """
        if not period:
            period = _detect_period(csv_content)

        logger.info(json.dumps({"event": "manual_ingestion_started", "period": period}))

        # Check if statement already exists
        if statement_exists(period):
            year, month = int(period[:4]), int(period[5:7])
            existing = get_statement(year, month)
            existing_count = existing.get("total_transactions", 0) if existing else 0

            # Parse new to compare
            new_statement = parse_statement_csv(csv_content, period)
            new_count = new_statement.get("total_transactions", 0)

            if new_count <= existing_count:
                return {
                    "status": "skipped",
                    "period": period,
                    "reason": f"Statement already exists with {existing_count} transactions (new has {new_count}). Use enrich_statement to re-enrich.",
                }

            logger.info(json.dumps({
                "event": "overwriting_statement",
                "period": period,
                "old_count": existing_count,
                "new_count": new_count,
            }))
            statement = new_statement
        else:
            statement = parse_statement_csv(csv_content, period)

        write_statement(statement)

        # Auto-trigger enrichment
        try:
            enrichment = asyncio.run(run_enrichment_pipeline(period, force=True))
            enrichment_status = "completed"
        except Exception as e:
            logger.error(json.dumps({"event": "auto_enrichment_failed", "error": str(e)}))
            enrichment_status = f"failed: {e}"
            enrichment = {}

        return {
            "status": "ingested",
            "period": period,
            "transactions": statement.get("total_transactions", 0),
            "total_debits": statement.get("total_debits", 0),
            "enrichment_status": enrichment_status,
            "spending_score": enrichment.get("spending_score", None),
        }

    @mcp.tool()
    def enrich_statement(year: int, month: int, force: bool = False) -> dict:
        """Run or re-run the AI enrichment pipeline on a statement.

        Enrichment includes: categorization, subscription detection, Gmail receipt
        matching, spending insights, and financial recommendations.

        Args:
            year: Four-digit year
            month: Month 1-12
            force: Re-run even if already enriched
        """
        period = f"{year:04d}-{month:02d}"

        if not statement_exists(period):
            return {"error": f"No statement found for {period}. Ingest or sync first."}

        try:
            enrichment = asyncio.run(run_enrichment_pipeline(period, force=force))
        except Exception as e:
            return {"error": f"Enrichment failed: {e}"}

        return {
            "status": "enriched",
            "period": period,
            "categories": len(enrichment.get("category_breakdown", {})),
            "subscriptions": len(enrichment.get("subscriptions", [])),
            "spending_score": enrichment.get("spending_score", 0),
            "highlights": enrichment.get("highlights", []),
        }
