"""SimpleFIN Bridge MCP tools for multi-bank (Amex, Bank of America, SoFi) sync and live balances."""

import asyncio
import json
import logging

from amex_job.simplefin import (
    claim_setup_token,
    get_cached_balances,
    sync_simplefin_to_firestore,
)
from enrichment.pipeline import run_enrichment_pipeline

logger = logging.getLogger("amex-mcp.tools.simplefin")


def register(mcp):
    @mcp.tool()
    def simplefin_claim_token(setup_token: str, sync_days: int = 60) -> dict:
        """Exchange a one-time Base64 SimpleFIN Setup Token for a permanent Access URL and sync all linked banks.

        Args:
            setup_token: Base64 Setup Token created under SimpleFIN Bridge -> My Account -> Apps -> New App Connection
            sync_days: Number of days of transaction history to pull on initial sync (default 60)
        """
        try:
            access_url = claim_setup_token(setup_token)
            masked_host = access_url.split("@")[-1] if "@" in access_url else access_url
            sync_result = sync_simplefin_to_firestore(days=sync_days)

            # Enrich synced periods
            enriched_periods = []
            for p_info in sync_result.get("synced_periods", []):
                period = p_info["period"]
                try:
                    asyncio.run(run_enrichment_pipeline(period, force=True))
                    enriched_periods.append(period)
                except Exception as e:
                    logger.warning(json.dumps({"event": "enrichment_warning", "period": period, "error": str(e)}))

            return {
                "status": "connected_and_synced",
                "endpoint": masked_host,
                "accounts": sync_result.get("accounts", []),
                "synced_periods": sync_result.get("synced_periods", []),
                "enriched_periods": enriched_periods,
                "errors": sync_result.get("errors", []),
            }
        except Exception as e:
            logger.error(json.dumps({"event": "simplefin_claim_failed", "error": str(e)}))
            return {"error": f"Failed to claim SimpleFIN token or sync: {e}"}

    @mcp.tool()
    def simplefin_sync(days: int = 30, enrich: bool = True) -> dict:
        """Sync live balances and recent transactions across all SimpleFIN-connected banks (Amex, BofA, SoFi).

        Args:
            days: Number of days of history to sync (default 30)
            enrich: Run the 5-stage Gemini categorization & vector embedding pipeline on updated months
        """
        try:
            sync_result = sync_simplefin_to_firestore(days=days)
            enriched_periods = []
            if enrich:
                for p_info in sync_result.get("synced_periods", []):
                    period = p_info["period"]
                    try:
                        asyncio.run(run_enrichment_pipeline(period, force=True))
                        enriched_periods.append(period)
                    except Exception as e:
                        logger.warning(json.dumps({"event": "enrichment_warning", "period": period, "error": str(e)}))

            return {
                "status": "synced",
                "accounts": sync_result.get("accounts", []),
                "synced_periods": sync_result.get("synced_periods", []),
                "enriched_periods": enriched_periods,
                "errors": sync_result.get("errors", []),
            }
        except Exception as e:
            logger.error(json.dumps({"event": "simplefin_sync_failed", "error": str(e)}))
            return {"error": f"SimpleFIN sync failed: {e}"}

    @mcp.tool()
    def get_bank_balances(refresh: bool = False) -> dict:
        """Get balances across all connected bank and card accounts (Amex, Bank of America, SoFi).

        Args:
            refresh: If True, fetches live balances from SimpleFIN before returning (default False uses Firestore cache)
        """
        try:
            if refresh:
                sync_res = sync_simplefin_to_firestore(days=7)
                accounts = sync_res.get("accounts", [])
            else:
                accounts = get_cached_balances()
                if not accounts:
                    sync_res = sync_simplefin_to_firestore(days=7)
                    accounts = sync_res.get("accounts", [])

            by_institution = {}
            for acc in accounts:
                inst = acc.get("institution", "other")
                by_institution.setdefault(inst, []).append(acc)

            return {
                "total_accounts": len(accounts),
                "accounts": accounts,
                "by_institution": by_institution,
            }
        except Exception as e:
            return {"error": f"Failed to retrieve balances: {e}"}
