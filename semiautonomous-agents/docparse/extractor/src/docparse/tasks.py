"""Cloud Tasks integration with named-task deduplication.

Storm-prevention core. When an OBJECT_FINALIZE event arrives we compute a
deterministic task ID from `sha256(bucket:object:generation)` and attempt
to create a Cloud Tasks entry with that exact name. If the same event was
already enqueued (or processed within the dedup window), the Cloud Tasks
API returns ALREADY_EXISTS and the dispatcher returns 200 immediately —
the worker is never invoked twice for the same input.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os

from google.api_core.exceptions import AlreadyExists
from google.cloud import tasks_v2

log = logging.getLogger("docparse.tasks")

PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("DOCPARSE_PROJECT")
LOCATION = os.environ.get("TASKS_LOCATION", "us-central1")
QUEUE = os.environ.get("TASKS_QUEUE", "docparse-extract")
WORKER_URL = os.environ.get("WORKER_URL")  # https://docparse-xxx.run.app/work
WORKER_SA = os.environ.get("WORKER_SA")    # SA that signs OIDC tokens for /work

_client: tasks_v2.CloudTasksAsyncClient | None = None


def _client_singleton() -> tasks_v2.CloudTasksAsyncClient:
    global _client
    if _client is None:
        _client = tasks_v2.CloudTasksAsyncClient()
    return _client


def task_name_for(bucket: str, object_name: str, generation: int) -> str:
    """Deterministic task ID. Same (bucket, object, generation) → same name.

    GCS `generation` is a monotonic per-object counter that bumps on every
    overwrite — so re-uploading byte-identical content gets a NEW task
    (intentional: it's a real new event the user triggered). But Pub/Sub
    redelivering the SAME OBJECT_FINALIZE multiple times always carries
    the same generation → same task name → dedup wins.
    """
    raw = f"{bucket}:{object_name}:{generation}".encode()
    digest = hashlib.sha256(raw).hexdigest()[:32]
    return f"projects/{PROJECT}/locations/{LOCATION}/queues/{QUEUE}/tasks/extract-{digest}"


async def enqueue_extract(bucket: str, object_name: str, generation: int) -> dict:
    """Enqueue an extraction task. Returns {created: bool, task_name: str}.

    `created` is True only on the first call for this (bucket, object, gen).
    Subsequent calls with the same identity hit ALREADY_EXISTS and return
    `created=False` immediately — no work scheduled.
    """
    if not WORKER_URL:
        raise RuntimeError("WORKER_URL env var not set")
    if not PROJECT:
        raise RuntimeError("GOOGLE_CLOUD_PROJECT / DOCPARSE_PROJECT env var not set")

    client = _client_singleton()
    task_name = task_name_for(bucket, object_name, generation)
    parent = f"projects/{PROJECT}/locations/{LOCATION}/queues/{QUEUE}"

    payload = json.dumps({
        "bucket": bucket,
        "name": object_name,
        "generation": generation,
    }).encode()

    http_request = tasks_v2.HttpRequest(
        http_method=tasks_v2.HttpMethod.POST,
        url=WORKER_URL,
        headers={"Content-Type": "application/json"},
        body=payload,
    )
    if WORKER_SA:
        http_request.oidc_token = tasks_v2.OidcToken(service_account_email=WORKER_SA)

    task = tasks_v2.Task(name=task_name, http_request=http_request)

    try:
        created = await client.create_task(
            tasks_v2.CreateTaskRequest(parent=parent, task=task)
        )
        log.info("task created: %s", created.name)
        return {"created": True, "task_name": created.name}
    except AlreadyExists:
        log.info(
            "duplicate event suppressed: gs://%s/%s gen=%s already enqueued",
            bucket, object_name, generation,
        )
        return {"created": False, "task_name": task_name}
