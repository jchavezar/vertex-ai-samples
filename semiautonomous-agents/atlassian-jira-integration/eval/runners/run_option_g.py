"""Option G runner — streamAssist routed to the *custom* MCP datastore.

Identical wire shape to Option B (streamAssist + vertexAiSearchSpec.dataStoreSpecs),
but points at the BYO custom MCP server (Cloud Run jira-mcp-server) instead of
the OOB Atlassian Rovo MCP. No ADK, no Agent Engine — GE's built-in
custom_mcp_agent dispatches tool calls directly.

This is the path validated on 2026-05-19 after applying the five-part recipe:
 1. /mcp StreamableHTTP handler serializes the full Tool object (annotations,
    outputSchema, descriptions all flow through).
 2. initialize returns protocolVersion 2025-06-18.
 3. Each read tool declares ToolAnnotations(readOnlyHint=true, ...).
 4. Each read tool has an outputSchema.
 5. Connector exposes canonical search(query)/fetch(id) tools.

See ../option-a-custom-mcp-portal/jira_server/server.py for the server side
and memory/ge_custom_mcp_confirmation_fix.md for the full recipe.
"""
from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

import httpx

from . import _common as C

OPTION_G_DATASTORE_ID = os.environ.get(
    "OPTION_G_DATASTORE_ID",
    "custom-mcp-jira_1779142849168_mcp_data",
)


def datastore_resource() -> str:
    if not OPTION_G_DATASTORE_ID:
        raise RuntimeError(
            "OPTION_G_DATASTORE_ID not set in eval/.env. This should be the "
            "datastore ID of the custom MCP connector pointing at the Cloud "
            "Run jira-mcp-server, e.g. custom-mcp-jira_1779142849168_mcp_data."
        )
    return (
        f"projects/{C.GE_PROJECT_NUMBER}/locations/{C.GE_LOCATION}/"
        f"collections/default_collection/dataStores/{OPTION_G_DATASTORE_ID}"
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
    raw_path = raw_dir / f"{qid}_g.json"
    t0 = time.perf_counter()
    ok, chunks, err = await C.call_stream_assist(body, client, raw_dump_path=raw_path)
    elapsed = time.perf_counter() - t0
    if not ok:
        return C.RunnerResult(id=qid, pipeline="g", ok=False, answer="", elapsed_s=elapsed, error=err, raw_path=str(raw_path))
    answer, tool_calls, grounding = C._parse_stream(chunks)
    return C.RunnerResult(
        id=qid, pipeline="g", ok=True, answer=answer,
        tool_calls=tool_calls, citations=C.cited_keys(answer),
        grounding_chunks=grounding, elapsed_s=elapsed, raw_path=str(raw_path),
    )
