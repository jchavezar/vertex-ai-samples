"""Drive tool that calls Drive as the calling user.

Reads the per-request user OAuth token from ADK session state (populated by
the A2A handler in main.py). This token is the one GE captured during the
OAuth consent screen and forwarded as `Authorization: Bearer <ya29.user>`.
"""

from __future__ import annotations

from typing import Any

from google.adk.tools import ToolContext
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def drive_search_files(
    tool_context: ToolContext,
    query: str = "",
    page_size: int = 10,
) -> dict[str, Any]:
    """List the calling user's Google Drive files.

    Args:
        query: Drive query (Drive query language). Empty = most recent.
        page_size: Max files to return (capped at 25).
    """
    state = tool_context.state
    token = state.get("user_token") or ""
    email = state.get("user_email") or "(unknown)"

    if not token:
        return {
            "error": (
                "No user OAuth token in session — this agent expects to be "
                "called via the GE Custom-A2A bridge."
            ),
        }

    try:
        creds = Credentials(token=token)
        svc = build("drive", "v3", credentials=creds, cache_discovery=False)
        resp = (
            svc.files()
            .list(
                q=query or None,
                pageSize=min(max(page_size, 1), 25),
                fields=(
                    "files(id,name,mimeType,modifiedTime,webViewLink,"
                    "owners(emailAddress))"
                ),
                orderBy="modifiedTime desc",
            )
            .execute()
        )
        files = resp.get("files", [])
        return {
            "queried_as": email,
            "count": len(files),
            "files": files,
        }
    except Exception as e:
        return {"queried_as": email, "error": str(e)}
