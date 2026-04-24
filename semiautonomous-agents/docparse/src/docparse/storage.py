from __future__ import annotations

import asyncio
from pathlib import Path

from google.cloud import storage

_client: storage.Client | None = None


def gcs_client() -> storage.Client:
    global _client
    if _client is None:
        _client = storage.Client()
    return _client


async def download_blob(bucket: str, name: str, dest: Path) -> Path:
    """Download gs://bucket/name to dest. Returns dest."""

    def _do() -> Path:
        b = gcs_client().bucket(bucket)
        blob = b.blob(name)
        dest.parent.mkdir(parents=True, exist_ok=True)
        blob.download_to_filename(str(dest))
        return dest

    return await asyncio.to_thread(_do)


async def upload_text(bucket: str, name: str, content: str, content_type: str = "text/markdown") -> str:
    """Upload `content` to gs://bucket/name. Returns the gs:// URI."""

    def _do() -> str:
        b = gcs_client().bucket(bucket)
        blob = b.blob(name)
        blob.upload_from_string(content, content_type=content_type)
        return f"gs://{bucket}/{name}"

    return await asyncio.to_thread(_do)
