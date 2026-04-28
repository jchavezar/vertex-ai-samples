"""
ADK Drive agent designed to be deployed to Vertex AI Agent Engine.

The agent's tools call Drive API v3 directly. The user's OAuth access token is
NOT obtained by the agent — it is injected into the session state by the
custom UI's backend, which got it from a Google Identity Services popup in
the browser.

Token lookup order (matches the pattern in
gemini-enterprise-sharepoint-agent/agent/agent.py):

1. tool_context.state["temp:drive_access_token"]   <- runtime injection
2. tool_context.state["drive_access_token"]        <- local InMemoryRunner
3. tool_context._invocation_context.session.state["drive_access_token"]
"""
from __future__ import annotations

import logging
from typing import Any

import httpx
from google.adk.agents import Agent
from google.adk.tools import ToolContext

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
logger = logging.getLogger("adk-drive-ae")

TOKEN_KEY = "drive_access_token"
DRIVE_BASE = "https://www.googleapis.com/drive/v3"
DEFAULT_TIMEOUT = 30.0


def _get_token(tool_context: ToolContext) -> str:
    state = tool_context.state
    token = state.get(f"temp:{TOKEN_KEY}") or state.get(TOKEN_KEY)
    if not token and hasattr(tool_context, "_invocation_context"):
        sess = getattr(tool_context._invocation_context, "session", None)
        if sess is not None and isinstance(getattr(sess, "state", None), dict):
            token = sess.state.get(TOKEN_KEY)
    if not token:
        raise RuntimeError(
            "Drive access token missing from session state. "
            "The UI must call create_session(state={'temp:drive_access_token': <token>})."
        )
    return token


def _drive_request(
    method: str,
    path: str,
    token: str,
    *,
    params: dict | None = None,
    accept: str = "application/json",
) -> Any:
    url = f"{DRIVE_BASE}{path}"
    headers = {"Authorization": f"Bearer {token}", "Accept": accept}
    with httpx.Client(timeout=DEFAULT_TIMEOUT) as client:
        resp = client.request(method, url, headers=headers, params=params)
    if resp.status_code >= 400:
        raise RuntimeError(f"Drive API {method} {path} -> HTTP {resp.status_code}: {resp.text[:300]}")
    if accept == "application/json":
        return resp.json()
    return resp.text


def _err(tool: str, exc: Exception) -> dict:
    logger.exception("tool %s failed", tool)
    return {"error": str(exc), "tool": tool}


def drive_files_list(q: str, page_size: int, tool_context: ToolContext) -> dict:
    """Search the user's Google Drive.

    Args:
        q: Drive query string. Examples:
           - fullText contains 'envato'
           - name contains 'budget' and mimeType != 'application/vnd.google-apps.folder'
           - modifiedTime > '2025-01-01T00:00:00'
        page_size: Max number of files to return (1-25 recommended).

    Returns:
        {"files": [{id, name, mimeType, modifiedTime, webViewLink, owners}, ...]}
    """
    try:
        token = _get_token(tool_context)
        params = {
            "q": q,
            "pageSize": max(1, min(int(page_size), 25)),
            "fields": "files(id,name,mimeType,modifiedTime,webViewLink,owners(displayName,emailAddress))",
            "orderBy": "modifiedTime desc",
        }
        logger.info("drive_files_list q=%r pageSize=%s", q, params["pageSize"])
        return _drive_request("GET", "/files", token, params=params)
    except Exception as e:  # noqa: BLE001
        return _err("drive_files_list", e)


def drive_files_get(file_id: str, tool_context: ToolContext) -> dict:
    """Fetch metadata + raw text content of a non-Workspace file.

    Use for plain-text / source files. For Google Docs/Sheets/Slides,
    use drive_files_export instead.
    """
    try:
        token = _get_token(tool_context)
        meta = _drive_request(
            "GET", f"/files/{file_id}", token,
            params={"fields": "id,name,mimeType,modifiedTime,webViewLink,size"},
        )
        body = ""
        try:
            body = _drive_request(
                "GET", f"/files/{file_id}", token, params={"alt": "media"}, accept="text/plain"
            )
            if isinstance(body, str) and len(body) > 8000:
                body = body[:8000] + "\n... [truncated]"
        except Exception as e:
            body = f"[could not fetch body: {e}]"
        return {**meta, "content": body}
    except Exception as e:  # noqa: BLE001
        return _err("drive_files_get", e)


def drive_files_export(file_id: str, mime_type: str, tool_context: ToolContext) -> dict:
    """Export a Google Workspace doc (Docs/Sheets/Slides) as text/csv/html.

    Common mime_type values:
        text/plain       - Docs as plain text
        text/csv         - Sheets as CSV
        text/html        - Docs as HTML
    """
    try:
        token = _get_token(tool_context)
        meta = _drive_request(
            "GET", f"/files/{file_id}", token,
            params={"fields": "id,name,mimeType,webViewLink,modifiedTime"},
        )
        body = _drive_request(
            "GET", f"/files/{file_id}/export", token,
            params={"mimeType": mime_type}, accept="text/plain",
        )
        if isinstance(body, str) and len(body) > 8000:
            body = body[:8000] + "\n... [truncated]"
        return {**meta, "exported_as": mime_type, "content": body}
    except Exception as e:  # noqa: BLE001
        return _err("drive_files_export", e)


def drive_about_get(tool_context: ToolContext) -> dict:
    """Return identity + storage quota of the signed-in Drive user. Use to confirm whose Drive is being read."""
    try:
        token = _get_token(tool_context)
        return _drive_request(
            "GET", "/about", token,
            params={"fields": "user(displayName,emailAddress),storageQuota(limit,usage)"},
        )
    except Exception as e:  # noqa: BLE001
        return _err("drive_about_get", e)


root_agent = Agent(
    name="drive_assistant",
    model="gemini-3-flash-preview",
    description=(
        "Answers questions by reading the signed-in user's Google Drive. The user's "
        "OAuth access token is injected via session state by the calling UI."
    ),
    instruction="""You are the user's Google Drive assistant.

For every question that could plausibly be answered from their files:

1. Call `drive_files_list` with a `q` parameter using Drive query syntax.
   - Content searches: `q="fullText contains 'topic'"`
   - Filename searches: `q="name contains 'budget'"`
   - Always exclude folders unless asked: `... and mimeType != 'application/vnd.google-apps.folder'`
   - Pass `page_size=10`.

2. If results look promising, fetch the top 1-3 files:
   - For Workspace docs (mimeType starts with `application/vnd.google-apps.`):
     call `drive_files_export` with `mime_type='text/plain'`.
   - For other text files: call `drive_files_get`.

3. Answer using only retrieved content. Cite each source with file name and webViewLink.

Rules:
- If a search returns nothing, broaden it (drop quotes, fewer keywords) before giving up.
- Never invent file content.
- For general-knowledge questions clearly unrelated to the user's files, just answer directly without calling Drive.
- If a tool errors with "access token missing", tell the user the UI did not pass their Google sign-in to the backend.
""",
    tools=[drive_files_list, drive_files_get, drive_files_export, drive_about_get],
)
