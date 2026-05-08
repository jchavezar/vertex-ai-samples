"""Async Jira REST helpers for ground-truth synthesis.

Used by `generate_questions.py` (computes deterministic answers when the
question is JQL-derivable) and the judge (verifies cited issue keys exist).
Reads OAuth credentials from .env (preferred) or falls back to the OAuth
helper at option-a-custom-mcp-portal/utils/oauth_oneshot.py output file.

Auto-refreshes access tokens on 401. Auto-paginates JQL searches.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import time
from pathlib import Path
from typing import Any, Iterable

import httpx

# --- Lightweight .env loader (no python-dotenv dep) -------------------------
_HERE = Path(__file__).resolve().parent
for _p in [_HERE / ".env", _HERE.parent / "option-a-custom-mcp-portal" / "adk_agent" / ".env"]:
    if _p.exists():
        for line in _p.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

ATLASSIAN_CLIENT_ID = os.environ.get("ATLASSIAN_CLIENT_ID", "")
ATLASSIAN_CLIENT_SECRET = os.environ.get("ATLASSIAN_CLIENT_SECRET", "")
ATLASSIAN_REFRESH_TOKEN = os.environ.get("ATLASSIAN_REFRESH_TOKEN", "")
SITE_URL = os.environ.get("ATLASSIAN_SITE_URL", "https://sockcop.atlassian.net").rstrip("/")
CLOUD_ID = os.environ.get("ATLASSIAN_CLOUD_ID", "")

# Optional Basic-auth (email + API token). Preferred over OAuth for the eval
# because API tokens never expire and don't share the rotating refresh-token
# chain that the AE deploy uses (avoids chain-invalidation collisions).
ATLASSIAN_EMAIL = os.environ.get("ATLASSIAN_EMAIL", "")
ATLASSIAN_API_TOKEN = os.environ.get("ATLASSIAN_API_TOKEN", "")
USE_BASIC_AUTH = bool(ATLASSIAN_EMAIL and ATLASSIAN_API_TOKEN)

_TOKEN_PATH = _HERE.parent / "option-a-custom-mcp-portal" / "adk_agent" / ".atlassian_token"

KEY_RE = re.compile(r"\b([A-Z][A-Z0-9_]+-\d+)\b")


class _TokenStore:
    """Holds the current access token + refresh token in memory.

    On 401 the caller invokes `await refresh()` to mint a new access token
    using the refresh token. Refresh tokens for Atlassian rotate — the new
    refresh token returned in the token endpoint response replaces the old.
    """

    def __init__(self) -> None:
        self.access_token: str | None = None
        self.refresh_token: str = ATLASSIAN_REFRESH_TOKEN
        self.expires_at: float = 0
        # Bootstrap from the file the option-a OAuth helper writes.
        if not self.access_token and _TOKEN_PATH.exists():
            self.access_token = _TOKEN_PATH.read_text().strip()
            self.expires_at = time.time() + 3500

    async def get(self, client: httpx.AsyncClient) -> str:
        if self.access_token and time.time() < self.expires_at - 60:
            return self.access_token
        await self.refresh(client)
        return self.access_token  # type: ignore[return-value]

    async def refresh(self, client: httpx.AsyncClient) -> None:
        if not (ATLASSIAN_CLIENT_ID and ATLASSIAN_CLIENT_SECRET and self.refresh_token):
            raise RuntimeError(
                "Cannot refresh Atlassian token: set ATLASSIAN_CLIENT_ID, "
                "ATLASSIAN_CLIENT_SECRET, ATLASSIAN_REFRESH_TOKEN in eval/.env "
                "(or run utils/oauth_oneshot.py once to seed .atlassian_token)."
            )
        resp = await client.post(
            "https://auth.atlassian.com/oauth/token",
            json={
                "grant_type": "refresh_token",
                "client_id": ATLASSIAN_CLIENT_ID,
                "client_secret": ATLASSIAN_CLIENT_SECRET,
                "refresh_token": self.refresh_token,
            },
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        self.access_token = data["access_token"]
        self.expires_at = time.time() + float(data.get("expires_in", 3600))
        if data.get("refresh_token"):
            self.refresh_token = data["refresh_token"]


_TOKEN = _TokenStore()


def _basic_auth_header() -> str:
    import base64
    raw = f"{ATLASSIAN_EMAIL}:{ATLASSIAN_API_TOKEN}".encode()
    return "Basic " + base64.b64encode(raw).decode()


async def _resolve_cloud_id(client: httpx.AsyncClient) -> str:
    global CLOUD_ID
    if CLOUD_ID:
        return CLOUD_ID
    if USE_BASIC_AUTH:
        # accessible-resources is OAuth-only. With Basic auth we hit the site
        # directly via {site}/_edge/tenant_info or just bypass cloudId lookup.
        resp = await client.get(
            f"{SITE_URL}/_edge/tenant_info",
            headers={"Authorization": _basic_auth_header(), "Accept": "application/json"},
            timeout=30,
        )
        if resp.status_code == 200:
            CLOUD_ID = resp.json().get("cloudId", "")
        if not CLOUD_ID:
            CLOUD_ID = "_basic"  # sentinel — _api_url handles it
        return CLOUD_ID
    for attempt in range(2):
        token = await _TOKEN.get(client)
        resp = await client.get(
            "https://api.atlassian.com/oauth/token/accessible-resources",
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
            timeout=30,
        )
        if resp.status_code == 401 and attempt == 0:
            await _TOKEN.refresh(client)
            continue
        resp.raise_for_status()
        sites = resp.json()
        site = next((s for s in sites if s["url"].rstrip("/") == SITE_URL), sites[0] if sites else None)
        if not site:
            raise RuntimeError(f"No Atlassian sites accessible to this token (looking for {SITE_URL}).")
        CLOUD_ID = site["id"]
        return CLOUD_ID
    raise RuntimeError("token refresh failed")


async def _api_url(client: httpx.AsyncClient, path: str) -> str:
    if USE_BASIC_AUTH:
        # Direct site access for Basic auth (no OAuth proxy).
        return f"{SITE_URL}{path}"
    cid = await _resolve_cloud_id(client)
    return f"https://api.atlassian.com/ex/jira/{cid}{path}"


async def _request(client: httpx.AsyncClient, method: str, path: str, **kw) -> httpx.Response:
    """One retry on 401 with token refresh (OAuth path only)."""
    url = await _api_url(client, path)
    if USE_BASIC_AUTH:
        kw.setdefault("headers", {})
        kw["headers"]["Authorization"] = _basic_auth_header()
        kw["headers"].setdefault("Accept", "application/json")
        return await client.request(method, url, timeout=60, **kw)
    for attempt in range(2):
        token = await _TOKEN.get(client)
        kw.setdefault("headers", {})
        kw["headers"]["Authorization"] = f"Bearer {token}"
        kw["headers"].setdefault("Accept", "application/json")
        resp = await client.request(method, url, timeout=60, **kw)
        if resp.status_code == 401 and attempt == 0:
            await _TOKEN.refresh(client)
            continue
        return resp
    return resp  # type: ignore[return-value]


async def run_jql(jql: str, fields: Iterable[str] = ("summary", "status", "assignee", "labels", "priority"),
                  client: httpx.AsyncClient | None = None, max_pages: int = 100) -> dict[str, Any]:
    """Execute a JQL query, auto-paginating up to `max_pages * 100` issues.

    Returns: {jql, count, keys: [...], issues: [{key, fields...}, ...]}.
    """
    own_client = client is None
    if own_client:
        client = httpx.AsyncClient()
    try:
        all_issues: list[dict] = []
        next_token: str | None = None
        for _ in range(max_pages):
            params: dict[str, Any] = {
                "jql": jql,
                "fields": ",".join(fields),
                "maxResults": 100,
            }
            if next_token:
                params["nextPageToken"] = next_token
            resp = await _request(client, "GET", "/rest/api/3/search/jql", params=params)  # type: ignore[arg-type]
            if resp.status_code >= 400:
                return {"jql": jql, "error": resp.status_code, "body": resp.text[:500]}
            data = resp.json()
            all_issues.extend(data.get("issues", []))
            next_token = data.get("nextPageToken")
            if not next_token or data.get("isLast", False) or not data.get("issues"):
                break
        return {
            "jql": jql,
            "count": len(all_issues),
            "keys": [i["key"] for i in all_issues],
            "issues": [{"key": i["key"], **{f: i.get("fields", {}).get(f) for f in fields}} for i in all_issues],
        }
    finally:
        if own_client:
            await client.aclose()  # type: ignore[union-attr]


async def get_issue(key: str, client: httpx.AsyncClient | None = None) -> dict[str, Any]:
    own_client = client is None
    if own_client:
        client = httpx.AsyncClient()
    try:
        resp = await _request(client, "GET", f"/rest/api/3/issue/{key}")  # type: ignore[arg-type]
        if resp.status_code == 404:
            return {"key": key, "exists": False}
        if resp.status_code >= 400:
            return {"key": key, "error": resp.status_code, "body": resp.text[:300]}
        d = resp.json()
        f = d.get("fields", {})
        return {
            "key": d["key"],
            "exists": True,
            "summary": f.get("summary"),
            "status": (f.get("status") or {}).get("name"),
            "assignee": (f.get("assignee") or {}).get("displayName") if f.get("assignee") else None,
            "labels": f.get("labels") or [],
            "priority": (f.get("priority") or {}).get("name") if f.get("priority") else None,
            "issue_type": (f.get("issuetype") or {}).get("name") if f.get("issuetype") else None,
            "created": f.get("created"),
            "updated": f.get("updated"),
            "resolution_date": f.get("resolutiondate"),
            "url": f"{SITE_URL}/browse/{d['key']}",
        }
    finally:
        if own_client:
            await client.aclose()  # type: ignore[union-attr]


async def issue_keys_exist(keys: Iterable[str], client: httpx.AsyncClient | None = None) -> dict[str, bool]:
    """Bulk-check existence by JQL: `key in (KEY-1, KEY-2, ...)`. Faster than N GETs."""
    keys = list(dict.fromkeys(keys))
    if not keys:
        return {}
    out: dict[str, bool] = {}
    for i in range(0, len(keys), 100):
        chunk = keys[i:i + 100]
        jql = "key in (" + ",".join(chunk) + ")"
        result = await run_jql(jql, fields=("summary",), client=client, max_pages=2)
        found = set(result.get("keys", []))
        for k in chunk:
            out[k] = k in found
    return out


async def list_projects(client: httpx.AsyncClient | None = None) -> list[dict[str, Any]]:
    own_client = client is None
    if own_client:
        client = httpx.AsyncClient()
    try:
        resp = await _request(client, "GET", "/rest/api/3/project/search", params={"maxResults": 50})  # type: ignore[arg-type]
        resp.raise_for_status()
        return resp.json().get("values", [])
    finally:
        if own_client:
            await client.aclose()  # type: ignore[union-attr]


async def corpus_stats(client: httpx.AsyncClient | None = None) -> dict[str, Any]:
    """High-level corpus stats used by the question generator to ground prompts."""
    own_client = client is None
    if own_client:
        client = httpx.AsyncClient()
    try:
        projects = await list_projects(client)
        stats: dict[str, Any] = {"site": SITE_URL, "projects": []}
        for p in projects[:10]:
            key = p["key"]
            total = await run_jql(f"project = {key}", fields=("summary",), client=client, max_pages=20)
            recent = await run_jql(f"project = {key} AND created >= -30d", fields=("summary",), client=client, max_pages=2)
            stats["projects"].append({
                "key": key,
                "name": p.get("name"),
                "total_issues": total.get("count"),
                "issues_last_30d": recent.get("count"),
                "sample_keys": total.get("keys", [])[:5],
            })
        return stats
    finally:
        if own_client:
            await client.aclose()  # type: ignore[union-attr]


# --- Convenience for ground-truth synthesis ---------------------------------

async def ground_truth_for(question: dict[str, Any], client: httpx.AsyncClient | None = None) -> dict[str, Any]:
    """Resolve a question's oracle field into expected_keys/expected_count.

    Question shape (input):
      {"id": ..., "q": ..., "category": ..., "oracle": "jql"|"llm-judge",
       "jql": "...", "expected_themes": [...]}
    """
    if question.get("oracle") == "jql" and question.get("jql"):
        result = await run_jql(question["jql"], client=client)
        return {
            "expected_keys": result.get("keys", []),
            "expected_count": result.get("count"),
            "_oracle_raw": result.get("error"),
        }
    return {"expected_themes": question.get("expected_themes", [])}


if __name__ == "__main__":
    async def _main() -> None:
        async with httpx.AsyncClient() as client:
            stats = await corpus_stats(client)
            print(json.dumps(stats, indent=2, default=str))
    asyncio.run(_main())
