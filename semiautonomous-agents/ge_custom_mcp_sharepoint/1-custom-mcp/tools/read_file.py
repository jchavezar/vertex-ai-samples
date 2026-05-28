"""read_file(file_id) - download a single SharePoint file and return extracted text.

file_id format mirrors fetch(): '{driveId}:{itemId}'. Capped at 5 MB to
keep parity with Option 2 for fair comparison.
"""
from __future__ import annotations

import logging

from auth import get_current_user_token
from doc_reader import extract_text
from graph_client import GraphAPIError, make_client

logger = logging.getLogger("sharepoint-mcp.tools.read_file")

MAX_DOWNLOAD_BYTES = 5 * 1024 * 1024  # 5 MB


def _split_id(compound: str) -> tuple[str, str]:
    if ":" not in compound:
        raise ValueError("file_id must be '<driveId>:<itemId>'")
    drive_id, _, item_id = compound.partition(":")
    if not drive_id or not item_id:
        raise ValueError("file_id must be '<driveId>:<itemId>'")
    return drive_id, item_id


async def read_file(file_id: str) -> dict:
    client = make_client(get_current_user_token() or "")
    try:
        drive_id, item_id = _split_id(file_id)
    except ValueError as e:
        return {"id": file_id, "title": "", "url": "", "text": "", "error": str(e)}
    try:
        meta = await client.get_file_metadata(item_id, drive_id)
        size = meta.get("size", 0)
        if size and size > MAX_DOWNLOAD_BYTES:
            return {
                "id": file_id,
                "title": meta.get("name", ""),
                "url": meta.get("webUrl", ""),
                "text": "",
                "error": f"file too large ({size} bytes; limit {MAX_DOWNLOAD_BYTES})",
            }
        content, _ctype = await client.download_file_content(item_id, drive_id)
        if len(content) > MAX_DOWNLOAD_BYTES:
            content = content[:MAX_DOWNLOAD_BYTES]
    except GraphAPIError as e:
        return {"id": file_id, "title": "", "url": "", "text": "", "error": str(e)}
    title = meta.get("name", "")
    text = extract_text(content, title)
    return {"id": file_id, "title": title, "url": meta.get("webUrl", ""), "text": text}
