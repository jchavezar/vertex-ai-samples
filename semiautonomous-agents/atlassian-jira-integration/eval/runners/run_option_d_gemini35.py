"""Option D-Gemini3.5 (DG) runner — Option H + explicit gemini-3.5-flash override.

Identical wire shape to Option H (streamAssist + vertexAiSearchSpec.dataStoreSpecs
pointed at the federated jira_cloud per-entity datastores). The ONE difference:
a top-level `generationSpec.modelId` field that pins the answer LLM to
gemini-3.5-flash.

The Discovery Engine streamAssist API exposes the override as
`StreamAssistRequest.generationSpec.modelId` (NOT `answerGenerationSpec.modelSpec.modelVersion`
— that's the answerQuery path). See run_option_c_gemini35.py for full notes.

Smoke-validated 2026-05-21:
  - "gemini-3.5-flash"        -> OK
  - "gemini-3.5-flash-001/002"-> HTTP 500 (model not yet pinned by point release)
  - "gemini-3-flash-preview"  -> OK
  - "gemini-2.5-flash"        -> OK

See ../option-d-jira-cloud-federated/README.md for the federated connector setup.
"""
from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

import httpx

from . import _common as C

# Comma-separated list of fed-connector entity datastore IDs.
OPTION_H_DATASTORE_ID = os.environ.get("OPTION_H_DATASTORE_ID", "")

# The LLM override applied to streamAssist via generationSpec.modelId.
# Override at runtime with OPTION_DG_MODEL_ID if a different version is needed.
OPTION_DG_MODEL_ID = os.environ.get("OPTION_DG_MODEL_ID", "gemini-3.5-flash")


def datastore_resources() -> list[str]:
    if not OPTION_H_DATASTORE_ID:
        raise RuntimeError(
            "OPTION_H_DATASTORE_ID not set in eval/.env. This should be a "
            "comma-separated list of the federated jira_cloud connector's "
            "per-entity datastore IDs, e.g. "
            "jira-fed-connector_<TS>_issue,jira-fed-connector_<TS>_project,..."
        )
    ids = [s.strip() for s in OPTION_H_DATASTORE_ID.split(",") if s.strip()]
    return [
        f"projects/{C.GE_PROJECT_NUMBER}/locations/{C.GE_LOCATION}/"
        f"collections/default_collection/dataStores/{ds}"
        for ds in ids
    ]


def build_body(question_text: str) -> dict[str, Any]:
    return {
        "query": {"parts": [{"text": question_text}]},
        "filter": "",
        "fileIds": [],
        "answerGenerationMode": "NORMAL",
        "toolsSpec": {
            "vertexAiSearchSpec": {
                "dataStoreSpecs": [{"dataStore": r} for r in datastore_resources()]
            },
            "toolRegistry": "default_tool_registry",
            "imageGenerationSpec": {},
            "videoGenerationSpec": {},
        },
        "generationSpec": {"modelId": OPTION_DG_MODEL_ID},
        "languageCode": "en-US",
        "userMetadata": {"timeZone": "America/New_York"},
        "assistSkippingMode": "REQUEST_ASSIST",
    }


async def run_one(question: dict[str, Any], client: httpx.AsyncClient, raw_dir: Path) -> C.RunnerResult:
    qid = question["id"]
    body = build_body(question["q"])
    raw_path = raw_dir / f"{qid}_dg.json"
    t0 = time.perf_counter()
    ok, chunks, err = await C.call_stream_assist(body, client, raw_dump_path=raw_path)
    elapsed = time.perf_counter() - t0
    if not ok:
        return C.RunnerResult(id=qid, pipeline="dg", ok=False, answer="", elapsed_s=elapsed, error=err, raw_path=str(raw_path))
    answer, tool_calls, grounding = C._parse_stream(chunks)
    # For federated retrieval, citations come from groundingChunks (URIs / titles
    # contain the Jira issue key as the page slug); fall back to keys mentioned
    # in the answer text via cited_keys.
    cited = C.cited_keys(answer)
    if not cited and grounding:
        gtext = " ".join((g.get("title", "") + " " + g.get("uri", "")) for g in grounding)
        cited = C.cited_keys(gtext) or C.cited_keys(answer)
    return C.RunnerResult(
        id=qid, pipeline="dg", ok=True, answer=answer,
        tool_calls=tool_calls, citations=cited,
        grounding_chunks=grounding, elapsed_s=elapsed, raw_path=str(raw_path),
    )
