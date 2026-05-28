"""Thin async Microsoft Graph wrapper bound to a per-request user token.

No MSAL, no token cache. Construct one per request with the bearer
captured by BearerCaptureMiddleware; Graph enforces ACLs based on the
Entra user the token represents.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

import httpx

logger = logging.getLogger("sharepoint-mcp.graph")

GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"


class GraphAPIError(Exception):
    def __init__(self, status_code: int, message: str, code: Optional[str] = None):
        self.status_code = status_code
        self.code = code
        super().__init__(f"Graph {status_code}: {message}")


class GraphClient:
    """Async Graph client carrying the in-flight user's bearer."""

    def __init__(self, bearer: str, timeout: float = 60.0):
        if not bearer:
            raise GraphAPIError(401, "missing bearer token")
        self._bearer = bearer
        self._timeout = timeout

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._bearer}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        json_body: Optional[dict] = None,
    ) -> dict:
        url = f"{GRAPH_BASE_URL}{endpoint}"
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            r = await client.request(
                method, url, headers=self._headers(), params=params, json=json_body
            )
        if r.status_code == 204:
            return {}
        try:
            data = r.json()
        except Exception:
            data = {"raw": r.text}
        if r.status_code >= 400:
            err = (data or {}).get("error", {}) if isinstance(data, dict) else {}
            raise GraphAPIError(r.status_code, err.get("message", str(data)[:300]),
                                err.get("code"))
        return data

    async def search_sites_and_files(self, query: str, top: int = 20) -> list[dict]:
        """Return a flat list of search hits (driveItem entities)."""
        body = {
            "requests": [
                {
                    "entityTypes": ["driveItem"],
                    "query": {"queryString": query},
                    "from": 0,
                    "size": top,
                    "fields": [
                        "id", "name", "webUrl", "lastModifiedDateTime",
                        "size", "parentReference",
                    ],
                }
            ]
        }
        data = await self._request("POST", "/search/query", json_body=body)
        hits: list[dict] = []
        for resp in data.get("value", []) or []:
            for hc in resp.get("hitsContainers", []) or []:
                hits.extend(hc.get("hits", []) or [])
        return hits

    async def get_file_metadata(self, item_id: str, drive_id: str) -> dict:
        return await self._request("GET", f"/drives/{drive_id}/items/{item_id}")

    async def download_file_content(self, item_id: str, drive_id: str) -> tuple[bytes, str]:
        url = f"{GRAPH_BASE_URL}/drives/{drive_id}/items/{item_id}/content"
        async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
            r = await client.get(url, headers={"Authorization": f"Bearer {self._bearer}"})
            if r.status_code >= 400:
                raise GraphAPIError(r.status_code, r.text[:300])
            return r.content, r.headers.get("content-type", "application/octet-stream")

    async def list_sites(self, search: str = "") -> list[dict]:
        q = search if search else "*"
        data = await self._request("GET", f"/sites", params={"search": q})
        return data.get("value", []) or []

    async def list_libraries(self, site_id: str) -> list[dict]:
        data = await self._request("GET", f"/sites/{site_id}/drives")
        return data.get("value", []) or []

    async def list_children(
        self, drive_id: str, folder_id: str = "root", top: int = 50
    ) -> list[dict]:
        endpoint = f"/drives/{drive_id}/items/{folder_id}/children"
        data = await self._request("GET", endpoint, params={"$top": top})
        return data.get("value", []) or []


def make_client(bearer: str) -> GraphClient:
    return GraphClient(bearer)
