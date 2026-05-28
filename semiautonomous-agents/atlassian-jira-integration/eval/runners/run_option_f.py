"""Option F runner — streamAssist routed to the ADK+Rovo MCP wrapper datastore.

Structurally identical to Option B/E: GE planner -> dataStoreSpecs filter
forces the call into the `mcp-adk-rovo-wrapper` Cloud Run /mcp endpoint,
which in turn calls Atlassian's hosted Rovo MCP via Google ADK + Gemini.
"""
from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

import httpx

from . import _common as C

OPTION_F_DATASTORE_ID = os.environ.get("OPTION_F_DATASTORE_ID", "")


def datastore_resource() -> str:
    if not OPTION_F_DATASTORE_ID:
        raise RuntimeError(
            "OPTION_F_DATASTORE_ID not set in eval/.env — run "
            "option-f-adk-rovo-wrapper/register_datastore.py first."
        )
    return (
        f"projects/{C.GE_PROJECT_NUMBER}/locations/{C.GE_LOCATION}/"
        f"collections/default_collection/dataStores/{OPTION_F_DATASTORE_ID}"
    )


def build_body(question_text: str) -> dict[str, Any]:
    return {
        "query": {"parts": [{"text": question_text}]},
        "filter": "",
        "fileIds": [],
        "answerGenerationMode": "NORMAL",
        "toolsSpec": {
            "vertexAiSearchSpec": {
                "dataStoreSpecs": [{"dataStore": datastore_resource()}]
            },
            "toolRegistry": "default_tool_registry",
            "imageGenerationSpec": {},
            "videoGenerationSpec": {},
        },
        "languageCode": "en-US",
        "userMetadata": {"timeZone": "America/New_York"},
        "assistSkippingMode": "REQUEST_ASSIST",
    }


async def run_one(question: dict[str, Any], client: httpx.AsyncClient, raw_dir: Path) -> C.RunnerResult:
    qid = question["id"]
    body = build_body(question["q"])
    raw_path = raw_dir / f"{qid}_f.json"
    t0 = time.perf_counter()
    ok, chunks, err = await C.call_stream_assist(body, client, raw_dump_path=raw_path)
    elapsed = time.perf_counter() - t0
    if not ok:
        return C.RunnerResult(id=qid, pipeline="f", ok=False, answer="", elapsed_s=elapsed, error=err, raw_path=str(raw_path))
    answer, tool_calls, grounding = C._parse_stream(chunks)
    return C.RunnerResult(
        id=qid, pipeline="f", ok=True, answer=answer,
        tool_calls=tool_calls, citations=C.cited_keys(answer),
        grounding_chunks=grounding, elapsed_s=elapsed, raw_path=str(raw_path),
    )
