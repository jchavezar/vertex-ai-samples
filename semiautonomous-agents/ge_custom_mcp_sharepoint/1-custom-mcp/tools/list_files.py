"""list_files(library_id, folder?) - enumerate items in a library or sub-folder."""
from __future__ import annotations

import logging
from typing import Optional

from auth import get_current_user_token
from graph_client import GraphAPIError, make_client

logger = logging.getLogger("sharepoint-mcp.tools.list_files")


async def list_files(
    library_id: str, folder: Optional[str] = None, limit: int = 50
) -> dict:
    """folder is a driveItem id; defaults to 'root'."""
    client = make_client(get_current_user_token() or "")
    folder_id = folder or "root"
    try:
        items = await client.list_children(library_id, folder_id=folder_id, top=limit)
    except GraphAPIError as e:
        return {"items": [], "error": str(e)}
    out = []
    for it in items:
        is_folder = "folder" in it
        out.append({
            "id": f"{library_id}:{it.get('id', '')}",
            "name": it.get("name", ""),
            "kind": "folder" if is_folder else "file",
            "size": it.get("size", 0),
            "url": it.get("webUrl", ""),
            "modified": it.get("lastModifiedDateTime", ""),
        })
    return {"items": out}
