"""Hybrid search tool — combines semantic (vector), structured (filters), and compute (aggregation)."""

import asyncio
import json
import logging
from collections import defaultdict

from amex_job.storage import semantic_search, structured_query
from enrichment.embedder import embed_query

logger = logging.getLogger("amex-mcp.tools.search")

VALID_AGGREGATES = {"sum", "avg", "count", "min", "max"}
VALID_GROUP_BY = {
    "enriched_category", "subcategory", "merchant_clean", "card_member",
    "merchant_type", "purchase_channel", "purpose", "period", "date",
}


def _aggregate(transactions: list[dict], group_by: str | None, aggregate: str) -> dict:
    """Run deterministic aggregation on matched transactions."""
    amounts = [t.get("amount", 0) for t in transactions]

    if not group_by:
        if aggregate == "sum":
            value = round(sum(amounts), 2)
        elif aggregate == "avg":
            value = round(sum(amounts) / len(amounts), 2) if amounts else 0
        elif aggregate == "count":
            value = len(transactions)
        elif aggregate == "min":
            value = round(min(amounts), 2) if amounts else 0
        elif aggregate == "max":
            value = round(max(amounts), 2) if amounts else 0
        else:
            value = len(transactions)
        return {"aggregate": aggregate, "value": value}

    # Group by field, then aggregate each group
    groups = defaultdict(list)
    for txn in transactions:
        key = txn.get(group_by, "unknown")
        groups[key].append(txn.get("amount", 0))

    result = {}
    for key, vals in sorted(groups.items(), key=lambda kv: sum(kv[1]), reverse=True):
        if aggregate == "sum":
            result[key] = round(sum(vals), 2)
        elif aggregate == "avg":
            result[key] = round(sum(vals) / len(vals), 2) if vals else 0
        elif aggregate == "count":
            result[key] = len(vals)
        elif aggregate == "min":
            result[key] = round(min(vals), 2) if vals else 0
        elif aggregate == "max":
            result[key] = round(max(vals), 2) if vals else 0

    return {"aggregate": aggregate, "group_by": group_by, "groups": result}


def register(mcp):
    @mcp.tool()
    def smart_query(
        query: str = "",
        filters: str = "{}",
        group_by: str = "",
        aggregate: str = "",
        limit: int = 50,
    ) -> dict:
        """Hybrid transaction search combining semantic, structured, and compute layers.

        Three layers work together:
        - SEMANTIC (query): "coffee shops", "trip expenses" -> vector search
        - STRUCTURED (filters): exact field matches -> date, category, amount, etc.
        - COMPUTE (aggregate + group_by): SUM, AVG, COUNT -> deterministic Python math

        If only filters are provided (no query), returns ALL matching transactions
        with no top-K approximation.

        Args:
            query: Semantic search text (e.g., "coffee shops", "kids activities").
                   Leave empty for purely structured queries.
            filters: JSON string with structured filters. Available fields:
                - date_after / date_before: "YYYY-MM-DD" date range
                - category: enriched category (Dining, Groceries, etc.)
                - card_member: card member name
                - merchant_type: chain, local, online, service
                - purchase_channel: in_store, online, app, subscription
                - purpose: personal, business, gift, travel, medical
                - period: statement period "YYYY-MM"
            group_by: Group results by field (enriched_category, merchant_clean,
                      card_member, period, merchant_type, purchase_channel, purpose, date)
            aggregate: Aggregation function (sum, avg, count, min, max).
                       Applied after grouping if group_by is set.
            limit: Max transactions to return in detail (default 50)

        Examples:
            Semantic: query="coffee shops" filters='{"date_after":"2026-03-01"}'
            Structured: filters='{"category":"Dining","period":"2026-04"}'
            Compute: filters='{"period":"2026-04"}' group_by="enriched_category" aggregate="sum"
            Hybrid: query="business meals" filters='{"purpose":"business"}' aggregate="sum"
        """
        # Parse filters
        try:
            filter_dict = json.loads(filters) if filters else {}
        except json.JSONDecodeError:
            return {"error": f"Invalid filters JSON: {filters}"}

        # Validate group_by and aggregate
        if group_by and group_by not in VALID_GROUP_BY:
            return {"error": f"Invalid group_by: {group_by}. Valid: {sorted(VALID_GROUP_BY)}"}
        if aggregate and aggregate not in VALID_AGGREGATES:
            return {"error": f"Invalid aggregate: {aggregate}. Valid: {sorted(VALID_AGGREGATES)}"}

        # Route: semantic vs structured
        if query:
            # Path A: Semantic + structured + compute
            try:
                query_vector = asyncio.run(embed_query(query))
            except Exception as e:
                logger.error(json.dumps({"event": "embed_query_failed", "error": str(e)}))
                return {"error": f"Failed to embed query: {e}"}

            transactions = semantic_search(
                query_vector=query_vector,
                filters=filter_dict if filter_dict else None,
                limit=1000,
                distance_threshold=0.4,
            )
            search_mode = "semantic"
        else:
            # Path B: Structured only — returns ALL matches
            transactions = structured_query(
                filters=filter_dict if filter_dict else None,
            )
            search_mode = "structured"

        if not transactions:
            return {
                "search_mode": search_mode,
                "query": query,
                "filters": filter_dict,
                "results_count": 0,
                "transactions": [],
            }

        # Strip embeddings from output (large, not useful for display)
        for txn in transactions:
            txn.pop("embedding", None)

        # Sort by date descending
        transactions.sort(key=lambda t: t.get("date", ""), reverse=True)

        # Build response
        response = {
            "search_mode": search_mode,
            "query": query or None,
            "filters": {k: v for k, v in filter_dict.items() if v} if filter_dict else None,
            "results_count": len(transactions),
            "total_amount": round(sum(t.get("amount", 0) for t in transactions), 2),
        }

        # Compute layer
        if aggregate:
            response["aggregation"] = _aggregate(
                transactions,
                group_by if group_by else None,
                aggregate,
            )

        # Return transaction details (capped at limit)
        response["transactions"] = transactions[:limit]

        return response

    @mcp.tool()
    def search_transactions(query: str, months: int = 3) -> dict:
        """Search transactions using natural language (convenience wrapper for smart_query).

        Args:
            query: Natural language search (e.g., "uber rides over $30",
                   "subscriptions", "dining last month")
            months: Number of months to search (default 3)
        """
        return smart_query(query=query, limit=50)
