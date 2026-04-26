from __future__ import annotations

import json
import logging
import os
import tempfile
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request

from .discovery import import_single_doc
from .pipeline import parse_pdf_async
from .storage import download_blob, upload_text

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s :: %(message)s")
log = logging.getLogger("docparse.service")


OUTPUT_BUCKET = os.environ.get("OUTPUT_BUCKET")
WRITE_REPORT = os.environ.get("WRITE_REPORT", "true").lower() == "true"
SKIP_NON_PDF = os.environ.get("SKIP_NON_PDF", "true").lower() == "true"

# Streaming push to Gemini Enterprise / Discovery Engine. If GE_DATASTORE is set,
# every successfully written .txt is immediately imported into the datastore via
# a single-URI gcsSource — gives "streaming" semantics for GCS-backed datastores
# (which don't have a native streaming API).
GE_DATASTORE = os.environ.get("GE_DATASTORE")
GE_PROJECT = os.environ.get("GE_PROJECT")  # defaults to current project if unset
GE_LOCATION = os.environ.get("GE_LOCATION", "global")

app = FastAPI(title="docparse-service")


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/")
async def handle_event(request: Request) -> dict[str, Any]:
    """Entry point for Eventarc CloudEvents from GCS object.finalized."""
    if not OUTPUT_BUCKET:
        raise HTTPException(500, "OUTPUT_BUCKET env var is not set")

    body = await request.json()
    log.info("event received: %s", json.dumps({k: body.get(k) for k in ("type", "source", "subject")}))

    data = body.get("data") or body  # Eventarc nests in `data`; raw GCS POST does not
    bucket = data.get("bucket")
    name = data.get("name")
    if not bucket or not name:
        raise HTTPException(400, f"missing bucket/name in event: keys={list(data.keys())}")

    if SKIP_NON_PDF and not name.lower().endswith(".pdf"):
        log.info("skipping non-pdf object gs://%s/%s", bucket, name)
        return {"skipped": True, "reason": "not a .pdf", "object": f"gs://{bucket}/{name}"}

    return await _process_pdf(bucket, name)


async def _process_pdf(bucket: str, name: str) -> dict[str, Any]:
    t0 = time.time()
    with tempfile.TemporaryDirectory(prefix="docparse-") as tmp:
        local_pdf = Path(tmp) / Path(name).name
        log.info("downloading gs://%s/%s -> %s", bucket, name, local_pdf)
        await download_blob(bucket, name, local_pdf)

        log.info("parsing %s", local_pdf)
        result = await parse_pdf_async(local_pdf)

        # Mirror folder structure from input to output (.pdf → .txt).
        # NOTE: extension is .txt (not .md) because Discovery Engine / Gemini
        # Enterprise infers MIME from the FILE EXTENSION, not the GCS
        # Content-Type metadata. .md is rejected ("Field content.mime_type must
        # be one of [...] got 'text/markdown'") even when Content-Type is
        # text/plain. The file body is still markdown and the LLM sees the
        # structure at retrieval time.
        out_name = name[:-4] + ".txt" if name.lower().endswith(".pdf") else name + ".txt"
        md_uri = await upload_text(
            OUTPUT_BUCKET,
            out_name,
            result.markdown,
            content_type="text/plain; charset=utf-8",
        )
        log.info("uploaded %s", md_uri)

        report_uri = None
        if WRITE_REPORT:
            report = {
                "source": f"gs://{bucket}/{name}",
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
            # Write report to a `_reports/` subfolder so it stays out of the
            # default `gs://bucket/*.txt` import wildcard that GE/DE picks up.
            # Reports are diagnostic artifacts (timings, raw chart JSON) -- not
            # meant to be retrievable content. Keeping them in a subfolder lets
            # users keep the data without polluting the search index.
            report_name = "_reports/" + out_name[:-4] + ".report.json"
            report_uri = await upload_text(
                OUTPUT_BUCKET,
                report_name,
                json.dumps(report, indent=2, ensure_ascii=False),
                content_type="application/json",
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
            # Don't fail the whole pipeline if GE import errors -- the .txt is
            # already in the bucket and a manual import can recover.
            log.error("GE streaming import failed: %s", e)
            ge_op = {"error": str(e)}

    elapsed = time.time() - t0
    log.info("done in %.1fs: %s", elapsed, md_uri)
    return {
        "source": f"gs://{bucket}/{name}",
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
