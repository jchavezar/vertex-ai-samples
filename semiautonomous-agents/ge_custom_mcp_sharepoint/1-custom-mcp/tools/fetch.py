"""Canonical fetch(id) primitive. id format: '{driveId}:{itemId}'."""
from __future__ import annotations

import logging

from auth import get_current_user_token
from doc_reader import extract_text
from graph_client import GraphAPIError, make_client

logger = logging.getLogger("sharepoint-mcp.tools.fetch")


def _split_id(compound: str) -> tuple[str, str]:
    if ":" not in compound:
        raise ValueError("id must be '<driveId>:<itemId>'")
    drive_id, _, item_id = compound.partition(":")
    if not drive_id or not item_id:
        raise ValueError("id must be '<driveId>:<itemId>'")
    return drive_id, item_id


async def fetch(id: str) -> dict:
    """Return file metadata + extracted text for a SharePoint driveItem."""
    bearer = get_current_user_token()
    client = make_client(bearer or "")
    try:
        drive_id, item_id = _split_id(id)
    except ValueError as e:
        return {"id": id, "title": "", "url": "", "text": "", "error": str(e)}
    try:
        meta = await client.get_file_metadata(item_id, drive_id)
        content, _ctype = await client.download_file_content(item_id, drive_id)
    except GraphAPIError as e:
        logger.warning("fetch graph error: %s", e)
        return {"id": id, "title": "", "url": "", "text": "", "error": str(e)}
    title = meta.get("name", "")
    url = meta.get("webUrl", "")
    text = extract_text(content, title)
    return {"id": id, "title": title, "url": url, "text": text}
