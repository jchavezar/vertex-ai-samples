from __future__ import annotations

import asyncio
import logging
from typing import Any

import google.auth
import google.auth.transport.requests
import httpx

log = logging.getLogger("docparse.discovery")


_credentials = None


def _creds():
    global _credentials
    if _credentials is None:
        _credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    return _credentials


def _bearer_token() -> str:
    c = _creds()
    if not c.valid:
        c.refresh(google.auth.transport.requests.Request())
    return c.token


async def import_single_doc(
    *,
    project: str,
    datastore_id: str,
    location: str,
    gcs_uri: str,
    collection: str = "default_collection",
    branch: str = "0",
) -> dict[str, Any]:
    """Stream a single GCS object into a Discovery Engine datastore.

    Calls `documents:import` with a single-URI gcsSource — equivalent to a
    streaming insert for a GCS-backed datastore. Returns the operation JSON.
    The operation is async; doc typically becomes searchable in 30-60 s.
    """
    url = (
        f"https://discoveryengine.googleapis.com/v1/projects/{project}"
        f"/locations/{location}/collections/{collection}"
        f"/dataStores/{datastore_id}/branches/{branch}/documents:import"
    )
    body = {
        "gcsSource": {"inputUris": [gcs_uri], "dataSchema": "content"},
        "reconciliationMode": "INCREMENTAL",
    }
    headers = {
        "Authorization": f"Bearer {await asyncio.to_thread(_bearer_token)}",
        "X-Goog-User-Project": project,
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=30.0) as c:
        r = await c.post(url, json=body, headers=headers)
    if r.status_code >= 400:
        log.warning("DE import failed (%s): %s", r.status_code, r.text[:300])
        r.raise_for_status()
    return r.json()
