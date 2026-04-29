from __future__ import annotations

import asyncio
from pathlib import Path

from google.cloud import storage
from google.cloud.exceptions import NotFound

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


async def upload_text(
    bucket: str,
    name: str,
    content: str,
    content_type: str = "text/markdown",
    metadata: dict[str, str] | None = None,
) -> str:
    """Upload `content` to gs://bucket/name with optional custom metadata.
    Returns the gs:// URI."""

    def _do() -> str:
        b = gcs_client().bucket(bucket)
        blob = b.blob(name)
        if metadata:
            blob.metadata = metadata
        blob.upload_from_string(content, content_type=content_type)
        return f"gs://{bucket}/{name}"

    return await asyncio.to_thread(_do)


async def get_input_generation(bucket: str, name: str) -> int | None:
    """Return the current `generation` of gs://bucket/name, or None if missing.

    GCS `generation` is a monotonic per-object counter that bumps on every
    overwrite. We use it as the immutable identity for the input file in
    Cloud Tasks named-task dedup.
    """

    def _do() -> int | None:
        b = gcs_client().bucket(bucket)
        blob = b.blob(name)
        try:
            blob.reload()
        except NotFound:
            return None
        return blob.generation

    return await asyncio.to_thread(_do)


async def already_processed(
    output_bucket: str,
    output_name: str,
    input_generation: int,
) -> bool:
    """True iff the output blob exists AND records the same input_generation.

    Belt-and-suspenders idempotency: even if a malformed manual call bypasses
    the Cloud Tasks queue, the worker checks here before doing any work.
    """

    def _do() -> bool:
        b = gcs_client().bucket(output_bucket)
        blob = b.blob(output_name)
        try:
            blob.reload()
        except NotFound:
            return False
        recorded = (blob.metadata or {}).get("input_generation")
        return recorded == str(input_generation)

    return await asyncio.to_thread(_do)
