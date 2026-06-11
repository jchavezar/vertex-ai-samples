"""Canonical search(query) primitive for GE BYO_MCP."""
from __future__ import annotations

import logging

from auth import get_current_user_token
from graph_client import GraphAPIError, make_client

logger = logging.getLogger("sharepoint-mcp.tools.search")

SNIPPET_BUDGET = 400


async def search(query: str, top: int = 20) -> dict:
    """Free-text SharePoint search. Returns {"results": [{id,title,url,snippet}]}."""
    if not query or not query.strip():
        return {"results": []}
        
    bearer = get_current_user_token()
    client = make_client(bearer or "")
    try:
        hits = await client.search_sites_and_files(query, top=top)
    except GraphAPIError as e:
        logger.warning("search graph error: %s", e)
        return {"results": [], "error": str(e)}
    results = []
    for h in hits:
        r = h.get("resource", {}) or {}
        pr = r.get("parentReference", {}) or {}
        drive_id = pr.get("driveId", "")
        item_id = r.get("id", "")
        compound_id = f"{drive_id}:{item_id}" if drive_id else item_id
        results.append({
            "id": compound_id,
            "title": r.get("name", ""),
            "url": r.get("webUrl", ""),
            "snippet": (h.get("summary") or "")[:SNIPPET_BUDGET],
        })
    return {"results": results}
