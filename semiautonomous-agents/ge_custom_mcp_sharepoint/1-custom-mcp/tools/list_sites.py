"""list_sites() - enumerate SharePoint sites visible to the user."""
from __future__ import annotations

import logging

from auth import get_current_user_token
from graph_client import GraphAPIError, make_client

logger = logging.getLogger("sharepoint-mcp.tools.list_sites")


async def list_sites(search: str = "") -> dict:
    client = make_client(get_current_user_token() or "")
    try:
        sites = await client.list_sites(search)
    except GraphAPIError as e:
        return {"sites": [], "error": str(e)}
    return {
        "sites": [
            {
                "id": s.get("id", ""),
                "name": s.get("displayName", ""),
                "url": s.get("webUrl", ""),
            }
            for s in sites
        ]
    }
