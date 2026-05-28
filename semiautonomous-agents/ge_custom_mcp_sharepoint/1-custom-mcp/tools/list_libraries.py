"""list_libraries(site_id) - enumerate document libraries (drives) for a site."""
from __future__ import annotations

import logging

from auth import get_current_user_token
from graph_client import GraphAPIError, make_client

logger = logging.getLogger("sharepoint-mcp.tools.list_libraries")


async def list_libraries(site_id: str) -> dict:
    client = make_client(get_current_user_token() or "")
    try:
        drives = await client.list_libraries(site_id)
    except GraphAPIError as e:
        return {"libraries": [], "error": str(e)}
    return {
        "libraries": [
            {
                "id": d.get("id", ""),
                "name": d.get("name", ""),
                "url": d.get("webUrl", ""),
            }
            for d in drives
        ]
    }
