"""Option C-Gemini3.5 (CG) runner — Option G + explicit gemini-3.5-flash override.

Identical wire shape to Option G (streamAssist + vertexAiSearchSpec.dataStoreSpecs
pointed at the custom MCP datastore). The ONE difference: a top-level
`generationSpec.modelId` field that pins the answer LLM to gemini-3.5-flash.

The Discovery Engine streamAssist API exposes the override as
`StreamAssistRequest.generationSpec.modelId` (NOT `answerGenerationSpec.modelSpec.modelVersion`
— that's the answerQuery path). The field is discoverable via the discovery doc:
  curl -s "https://discoveryengine.googleapis.com/$discovery/rest?version=v1alpha"

Smoke-validated 2026-05-21:
  - "gemini-3.5-flash"        -> OK
  - "gemini-3.5-flash-001/002"-> HTTP 500 (model not yet pinned by point release)
  - "gemini-3-flash-preview"  -> OK (also valid; flash-preview is the Gemini 3 line)
  - "gemini-2.5-flash"        -> OK (current default behaves the same)

See ../option-a-custom-mcp-portal/jira_server/server.py for the server side
and memory/ge_custom_mcp_confirmation_fix.md for the streamAssist recipe.
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

# The LLM override applied to streamAssist via generationSpec.modelId.
# Override at runtime with OPTION_CG_MODEL_ID if a different version is needed.
OPTION_CG_MODEL_ID = os.environ.get("OPTION_CG_MODEL_ID", "gemini-3.5-flash")


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
        "generationSpec": {"modelId": OPTION_CG_MODEL_ID},
        "languageCode": "en-US",
        "userMetadata": {"timeZone": "America/New_York"},
        "assistSkippingMode": "REQUEST_ASSIST",
    }


async def run_one(question: dict[str, Any], client: httpx.AsyncClient, raw_dir: Path) -> C.RunnerResult:
    qid = question["id"]
    body = build_body(question["q"])
    raw_path = raw_dir / f"{qid}_cg.json"
    t0 = time.perf_counter()
    ok, chunks, err = await C.call_stream_assist(body, client, raw_dump_path=raw_path)
    elapsed = time.perf_counter() - t0
    if not ok:
        return C.RunnerResult(id=qid, pipeline="cg", ok=False, answer="", elapsed_s=elapsed, error=err, raw_path=str(raw_path))
    answer, tool_calls, grounding = C._parse_stream(chunks)
    return C.RunnerResult(
        id=qid, pipeline="cg", ok=True, answer=answer,
        tool_calls=tool_calls, citations=C.cited_keys(answer),
        grounding_chunks=grounding, elapsed_s=elapsed, raw_path=str(raw_path),
    )
