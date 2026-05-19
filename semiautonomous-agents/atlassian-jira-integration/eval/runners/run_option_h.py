"""Option H runner — streamAssist routed to the *federated* Jira Cloud connector.

Same wire shape as Option B/G (streamAssist + vertexAiSearchSpec.dataStoreSpecs),
but points at GE's OOB Google-built ``jira_cloud`` federated connector (data
source ``jira``) instead of the BYO custom MCP. The federated connector exposes
one data store *per Jira entity* (issue, project, story, task, bug, epic,
comment, attachment, worklog, board). We list ALL of them in ``dataStoreSpecs``
so the assistant can pick whichever entity matches the question.

No ADK, no Agent Engine, no custom MCP wrapper — GE's federated retrieval
returns ``groundingChunks`` for citation tracking; the chat assistant LLM
synthesizes the answer.

OAuth identity that completed the GE Console connector wizard
(``admin@jesusarguelles.altostrat.com`` on 2026-05-19) must match the
``GCLOUD_ACCOUNT`` env var used to mint the streamAssist bearer token — same
gotcha as Option G. See ../option-d-jira-cloud-federated/README.md.
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
        "languageCode": "en-US",
        "userMetadata": {"timeZone": "America/New_York"},
        "assistSkippingMode": "REQUEST_ASSIST",
    }


async def run_one(question: dict[str, Any], client: httpx.AsyncClient, raw_dir: Path) -> C.RunnerResult:
    qid = question["id"]
    body = build_body(question["q"])
    raw_path = raw_dir / f"{qid}_h.json"
    t0 = time.perf_counter()
    ok, chunks, err = await C.call_stream_assist(body, client, raw_dump_path=raw_path)
    elapsed = time.perf_counter() - t0
    if not ok:
        return C.RunnerResult(id=qid, pipeline="h", ok=False, answer="", elapsed_s=elapsed, error=err, raw_path=str(raw_path))
    answer, tool_calls, grounding = C._parse_stream(chunks)
    # For federated retrieval, citations come from groundingChunks (URIs / titles
    # contain the Jira issue key as the page slug); fall back to keys mentioned
    # in the answer text via cited_keys.
    cited = C.cited_keys(answer)
    if not cited and grounding:
        # Pull keys out of grounding URIs/titles too
        gtext = " ".join((g.get("title", "") + " " + g.get("uri", "")) for g in grounding)
        cited = C.cited_keys(gtext) or C.cited_keys(answer)
    return C.RunnerResult(
        id=qid, pipeline="h", ok=True, answer=answer,
        tool_calls=tool_calls, citations=cited,
        grounding_chunks=grounding, elapsed_s=elapsed, raw_path=str(raw_path),
    )
