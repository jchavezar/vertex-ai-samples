"""Option EG runner — streamAssist routed to the Option E mcp-adk-wrapper.

Same streamAssist wire shape as Option G (custom MCP datastore via
`toolsSpec.vertexAiSearchSpec.dataStoreSpecs`). Difference: the datastore
behind this connector is `mcp-adk-wrapper-*_mcp_data`, whose Cloud Run
endpoint delegates each `search`/`fetch` tool call to the Option A ADK
agent on Vertex Agent Engine. GE sees a normal MCP; the polished ADK
answer comes back as the tool result text.

Set `OPTION_I_DATASTORE_ID` in eval/.env before running.
"""
from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

import httpx

from . import _common as C

OPTION_I_DATASTORE_ID = os.environ.get(
    "OPTION_I_DATASTORE_ID",
    "mcp-adk-wrapper-1779222346_mcp_data",
)


def datastore_resource() -> str:
    if not OPTION_I_DATASTORE_ID:
        raise RuntimeError(
            "OPTION_I_DATASTORE_ID not set in eval/.env. Run "
            "option-e-adk-wrapped-in-mcp/register_datastore.py first."
        )
    return (
        f"projects/{C.GE_PROJECT_NUMBER}/locations/{C.GE_LOCATION}/"
        f"collections/default_collection/dataStores/{OPTION_I_DATASTORE_ID}"
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


async def run_one(
    question: dict[str, Any], client: httpx.AsyncClient, raw_dir: Path
) -> C.RunnerResult:
    qid = question["id"]
    body = build_body(question["q"])
    raw_path = raw_dir / f"{qid}_i.json"
    t0 = time.perf_counter()
    # Option E adds an extra hop (GE → wrapper → AE → MCP → Jira). The ADK
    # agent itself can take 60-120s on multi-step questions. Give the call a
    # generous timeout so we don't false-fail on legitimately long answers.
    ok, chunks, err = await C.call_stream_assist(
        body, client, raw_dump_path=raw_path, timeout_s=300.0
    )
    elapsed = time.perf_counter() - t0
    if not ok:
        return C.RunnerResult(
            id=qid, pipeline="eg", ok=False, answer="",
            elapsed_s=elapsed, error=err, raw_path=str(raw_path),
        )
    answer, tool_calls, grounding = C._parse_stream(chunks)
    return C.RunnerResult(
        id=qid, pipeline="eg", ok=True, answer=answer,
        tool_calls=tool_calls, citations=C.cited_keys(answer),
        grounding_chunks=grounding, elapsed_s=elapsed,
        raw_path=str(raw_path),
    )
