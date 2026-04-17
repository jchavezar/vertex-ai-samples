"""Core statement retrieval tools."""

import json
import logging

from amex_job.storage import get_latest_statement, get_statement

logger = logging.getLogger("amex-mcp.tools.statements")


def register(mcp):
    @mcp.tool()
    def get_latest_amex_statement() -> dict:
        """Returns the most recent American Express statement from Firestore.

        Includes balance, minimum due, due date, payment history, and all
        transactions. Data is refreshed automatically on the 1st of each month.
        """
        result = get_latest_statement()
        if result is None:
            return {"error": "No statements found. The data may not have been synced yet."}
        result.pop("fetched_at", None)
        logger.info(json.dumps({"event": "tool_called", "tool": "get_latest_amex_statement", "period": result.get("period")}))
        return result

    @mcp.tool()
    def get_amex_statement(year: int, month: int) -> dict:
        """Returns the American Express statement for a specific month.

        Args:
            year: Four-digit year (e.g., 2025)
            month: Month number 1-12 (e.g., 3 for March)
        """
        if not (2000 <= year <= 2099) or not (1 <= month <= 12):
            return {"error": f"Invalid date: year={year}, month={month}. Use 4-digit year and month 1-12."}
        result = get_statement(year, month)
        if result is None:
            period = f"{year:04d}-{month:02d}"
            return {"error": f"No statement found for {period}. It may not have been synced yet."}
        result.pop("fetched_at", None)
        logger.info(json.dumps({"event": "tool_called", "tool": "get_amex_statement", "period": result.get("period")}))
        return result
