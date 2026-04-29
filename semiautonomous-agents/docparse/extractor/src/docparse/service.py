from __future__ import annotations

import json
import logging
import os
import tempfile
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from google.api_core.exceptions import NotFound as GCSNotFound

from .discovery import import_single_doc
from .pipeline import parse_pdf_async
from .storage import (
    already_processed,
    download_blob,
    get_input_generation,
    upload_text,
)
from .tasks import enqueue_extract

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s :: %(message)s")
log = logging.getLogger("docparse.service")


OUTPUT_BUCKET = os.environ.get("OUTPUT_BUCKET")
WRITE_REPORT = os.environ.get("WRITE_REPORT", "true").lower() == "true"
SKIP_NON_PDF = os.environ.get("SKIP_NON_PDF", "true").lower() == "true"

# Streaming push to Gemini Enterprise / Discovery Engine. If GE_DATASTORE is set,
# every successfully written .txt is immediately imported into the datastore.
GE_DATASTORE = os.environ.get("GE_DATASTORE")
GE_PROJECT = os.environ.get("GE_PROJECT")
GE_LOCATION = os.environ.get("GE_LOCATION", "global")

app = FastAPI(title="docparse-service")


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


# /dispatch — Eventarc target. Receives OBJECT_FINALIZE, computes a deterministic
# Cloud Tasks name from (bucket, object, generation), enqueues. Pub/Sub redelivery
# of the same event hits ALREADY_EXISTS and returns 200 in <100ms.
@app.post("/dispatch")
async def dispatch(request: Request) -> dict[str, Any]:
    body = await request.json()
    log.info("dispatch event: %s", json.dumps({k: body.get(k) for k in ("type", "source", "subject")}))

    data = body.get("data") or body
    bucket = data.get("bucket")
    name = data.get("name")
    if not bucket or not name:
        raise HTTPException(400, f"missing bucket/name: keys={list(data.keys())}")

    if SKIP_NON_PDF and not name.lower().endswith(".pdf"):
        return {"skipped": True, "reason": "not a .pdf"}

    generation = data.get("generation")
    if generation is None:
        generation = await get_input_generation(bucket, name)
    if generation is None:
        log.warning("input gs://%s/%s not found at dispatch", bucket, name)
        return {"skipped": True, "reason": "input object not found"}

    result = await enqueue_extract(bucket, name, int(generation))
    return {"enqueued": result["created"], "task": result["task_name"]}


# /work — Cloud Tasks target. Belt-and-suspenders idempotency: even if a manual
# call bypasses the queue, GCS-metadata check short-circuits duplicate work.
@app.post("/work")
async def work(request: Request) -> dict[str, Any]:
    if not OUTPUT_BUCKET:
        raise HTTPException(500, "OUTPUT_BUCKET not set")

    body = await request.json()
    bucket = body.get("bucket")
    name = body.get("name")
    generation = body.get("generation")
    if not bucket or not name or generation is None:
        raise HTTPException(400, f"missing bucket/name/generation: {body}")
    generation = int(generation)

    out_name = name[:-4] + ".txt" if name.lower().endswith(".pdf") else name + ".txt"

    if await already_processed(OUTPUT_BUCKET, out_name, generation):
        log.info("work skip: gs://%s/%s gen=%s already processed", bucket, name, generation)
        return {"skipped": True, "reason": "already_processed"}

    return await _process_pdf(bucket, name, generation, out_name)


async def _process_pdf(bucket: str, name: str, generation: int, out_name: str) -> dict[str, Any]:
    t0 = time.time()
    with tempfile.TemporaryDirectory(prefix="docparse-") as tmp:
        local_pdf = Path(tmp) / Path(name).name
        log.info("downloading gs://%s/%s -> %s", bucket, name, local_pdf)
        try:
            await download_blob(bucket, name, local_pdf)
        except GCSNotFound:
            log.warning("gs://%s/%s not found — skipping", bucket, name)
            return {"skipped": True, "reason": "object not found"}

        log.info("parsing %s (gen=%s)", local_pdf, generation)
        result = await parse_pdf_async(local_pdf)

        # Mirror folder structure from input to output (.pdf → .txt).
        # Discovery Engine / GE infer MIME from the FILE EXTENSION, not the
        # GCS Content-Type metadata. .md is rejected; .txt with markdown
        # body is accepted and the LLM sees the structure at retrieval time.
        md_uri = await upload_text(
            OUTPUT_BUCKET,
            out_name,
            result.markdown,
            content_type="text/plain; charset=utf-8",
            metadata={"input_generation": str(generation)},
        )
        log.info("uploaded %s", md_uri)

        report_uri = None
        if WRITE_REPORT:
            report = {
                "source": f"gs://{bucket}/{name}",
                "input_generation": generation,
                "timings_seconds": result.timings,
                "page_count": len(result.pages),
                "pages": [
                    {
                        "page": p.page_num,
                        "markdown_chars": len(p.page_markdown),
                        "structured": [
                            {
                                "reading_order": s.reading_order,
                                "type": s.type.value,
                                "confidence": s.confidence,
                                "raw": s.raw,
                            }
                            for s in p.structured
                        ],
                    }
                    for p in result.pages
                ],
            }
            report_name = "_reports/" + out_name[:-4] + ".report.json"
            report_uri = await upload_text(
                OUTPUT_BUCKET,
                report_name,
                json.dumps(report, indent=2, ensure_ascii=False),
                content_type="application/json",
                metadata={"input_generation": str(generation)},
            )

    ge_op = None
    if GE_DATASTORE:
        try:
            project = GE_PROJECT or os.environ.get("GOOGLE_CLOUD_PROJECT") or _project_from_metadata()
            log.info("streaming import to GE: %s/%s/%s", project, GE_LOCATION, GE_DATASTORE)
            ge_op = await import_single_doc(
                project=project,
                datastore_id=GE_DATASTORE,
                location=GE_LOCATION,
                gcs_uri=md_uri,
            )
            log.info("GE import op: %s", ge_op.get("name", "?"))
        except Exception as e:  # noqa: BLE001
            log.error("GE streaming import failed: %s", e)
            ge_op = {"error": str(e)}

    elapsed = time.time() - t0
    log.info("done in %.1fs: %s", elapsed, md_uri)
    return {
        "source": f"gs://{bucket}/{name}",
        "generation": generation,
        "markdown": md_uri,
        "report": report_uri,
        "ge_import_op": ge_op.get("name") if isinstance(ge_op, dict) and "name" in ge_op else None,
        "elapsed_seconds": round(elapsed, 1),
        "page_count": len(result.pages),
    }


def _project_from_metadata() -> str:
    """Best-effort: read project from GCE metadata server when running on Cloud Run."""
    import urllib.request
    try:
        req = urllib.request.Request(
            "http://metadata.google.internal/computeMetadata/v1/project/project-id",
            headers={"Metadata-Flavor": "Google"},
        )
        return urllib.request.urlopen(req, timeout=2).read().decode("utf-8")
    except Exception:  # noqa: BLE001
        return ""
