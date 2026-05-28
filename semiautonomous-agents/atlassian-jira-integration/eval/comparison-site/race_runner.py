"""Self-contained pipeline invokers for the Live Race tab.

We deliberately do not import from `eval/runners/` here because:
  - run_option_d.py and run_option_e.py import from sibling packages
    (`option-d-langchain-rovo/`, `option-e-langchain-custom-mcp/`) that do
    not exist in this repo, so they'd raise ImportError at module load.
  - The runners are batch-eval entry points that also depend on `eval/.env`
    file mutation and other infrastructure that doesn't ship in this image.

The 10 UI letters map to the same HTTP shapes the runners use:

  UI key | request shape                             | runner counterpart
  -------+-------------------------------------------+--------------------
  A      | AE :streamQuery (gemini-2.5-flash)        | run_option_a
  AL     | AE :streamQuery (gemini-3.1-flash-lite)   | run_option_a_lite
  AG     | AE :streamQuery (gemini-3.5-flash)        | run_option_a_gemini35
  B      | streamAssist (Rovo MCP datastore)         | run_option_b
  C      | streamAssist (custom MCP datastore)       | run_option_g
  CG     | streamAssist (custom MCP) + modelId       | run_option_c_gemini35
  D      | streamAssist (federated jira_cloud)       | run_option_h
  DG     | streamAssist (federated) + modelId        | run_option_d_gemini35
  E      | streamAssist (mcp-adk-wrapper)            | run_option_i
  EG     | streamAssist (mcp-adk-wrapper) [same DS]  | run_option_e_gemini35
  F      | streamAssist (mcp-adk-rovo-wrapper)       | run_option_f

The eval orchestrator's `data.json` keys (A, B, C, D, E, AL, AG, EG, CG, DG)
agree with the comparison-site index.html's `PIPELINES` and `SHORT_LABELS`,
so the UI/backend wire by lowercased letter.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any

import google.auth
import google.auth.transport.requests
import httpx


# ---------------------------------------------------------------------------
# Config — all values match eval/runners/_common.py + eval/.env in the repo.
# Override at deploy time via env vars on the Cloud Run service.
# ---------------------------------------------------------------------------
GE_PROJECT_NUMBER = os.environ.get("GE_PROJECT_NUMBER", "254356041555")
GE_PROJECT_ID = os.environ.get("GE_PROJECT_ID", "vtxdemos")
GE_ENGINE_ID = os.environ.get("GE_ENGINE_ID", "jira-testing_1778158449701")
GE_LOCATION = os.environ.get("GE_LOCATION", "global")

# Agent Engine resource ids (one per Option A variant).
AE_REGION = "us-central1"
A_AGENT_ID = os.environ.get("OPTION_A_AGENT_ID", "1666248848999186432")
A_LITE_AGENT_ID = os.environ.get("OPTION_A_FLASHLITE_AGENT_ID", "1830381745770332160")
A_G35_AGENT_ID = os.environ.get("OPTION_A_GEMINI35_AGENT_ID", "2865752263228391424")

# Datastore ids for the streamAssist-based pipelines.
B_DATASTORE_ID = os.environ.get("OPTION_B_DATASTORE_ID", "mcp-jira_1778158685439_mcp_data")
C_DATASTORE_ID = os.environ.get("OPTION_G_DATASTORE_ID", "custom-mcp-jira_1779142849168_mcp_data")
D_DATASTORE_IDS = os.environ.get(
    "OPTION_H_DATASTORE_ID",
    "jira-fed-connector_1779221270798_issue,"
    "jira-fed-connector_1779221270798_project,"
    "jira-fed-connector_1779221270798_story,"
    "jira-fed-connector_1779221270798_task,"
    "jira-fed-connector_1779221270798_bug,"
    "jira-fed-connector_1779221270798_epic,"
    "jira-fed-connector_1779221270798_comment,"
    "jira-fed-connector_1779221270798_attachment,"
    "jira-fed-connector_1779221270798_worklog,"
    "jira-fed-connector_1779221270798_board",
)
E_DATASTORE_ID = os.environ.get("OPTION_I_DATASTORE_ID", "mcp-adk-wrapper-1779222346_mcp_data")
F_DATASTORE_ID = os.environ.get("OPTION_F_DATASTORE_ID", "mcp-adk-rovo-wrapper-1779555470_mcp_data")

CG_MODEL_ID = os.environ.get("OPTION_CG_MODEL_ID", "gemini-3.5-flash")
DG_MODEL_ID = os.environ.get("OPTION_DG_MODEL_ID", "gemini-3.5-flash")

STREAM_ASSIST_URL = (
    f"https://discoveryengine.googleapis.com/v1alpha/"
    f"projects/{GE_PROJECT_NUMBER}/locations/{GE_LOCATION}/"
    f"collections/default_collection/engines/{GE_ENGINE_ID}/"
    f"assistants/default_assistant:streamAssist"
)

KEY_RE = re.compile(r"\b([A-Z][A-Z0-9_]+-\d+)\b")

# Per-pipeline default timeouts (seconds).
DEFAULT_TIMEOUT_S = 240.0


# ---------------------------------------------------------------------------
# Auth — cache google.auth credentials at module scope so we don't refresh
# on every request. Cloud Run mints a fresh ADC token on cold start; the
# google-auth library handles refresh-near-expiry automatically.
#
# A user-supplied access token can override ADC. The Rovo MCP + custom-MCP
# pipelines (B/C/CG) need an OAuth token from the GE user identity that
# completed the Jira 3LO; the Cloud Run service account doesn't have that
# binding, so without an override those pipelines return auth errors.
# ---------------------------------------------------------------------------
_creds = None
_user_token: str | None = None
_user_token_exp: float = 0.0  # unix seconds


def set_user_token(token: str, ttl_s: float = 3000.0) -> float:
    """Install a user OAuth access token for outbound calls. TTL defaults to
    50 min (gcloud access tokens last 60 min). Returns the expiry timestamp."""
    global _user_token, _user_token_exp
    _user_token = (token or "").strip() or None
    _user_token_exp = time.time() + ttl_s if _user_token else 0.0
    return _user_token_exp


def clear_user_token() -> None:
    global _user_token, _user_token_exp
    _user_token = None
    _user_token_exp = 0.0


def user_token_status() -> dict[str, Any]:
    if _user_token and time.time() < _user_token_exp:
        return {"active": True, "expires_at": _user_token_exp, "expires_in_s": int(_user_token_exp - time.time())}
    return {"active": False, "expires_at": 0, "expires_in_s": 0}


def _token() -> str:
    global _creds, _user_token
    # Prefer user-supplied token while it's still fresh.
    if _user_token and time.time() < _user_token_exp:
        return _user_token
    if _creds is None:
        _creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    if not _creds.valid:
        _creds.refresh(google.auth.transport.requests.Request())
    return _creds.token  # type: ignore[return-value]


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {_token()}",
        "Content-Type": "application/json",
        "x-goog-user-project": GE_PROJECT_ID,
    }


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------
@dataclass
class RaceResult:
    ok: bool
    answer: str = ""
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    citations: list[str] = field(default_factory=list)
    grounding: list[dict[str, Any]] = field(default_factory=list)
    elapsed_s: float = 0.0
    error: str | None = None


# ---------------------------------------------------------------------------
# streamAssist parser (lifted verbatim from eval/runners/_common.py)
# ---------------------------------------------------------------------------
def _parse_streamassist_chunks(
    chunks: list[dict[str, Any]],
) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
    answer_parts: list[str] = []
    tool_calls: list[dict[str, Any]] = []
    grounding: list[dict[str, Any]] = []
    seen_g: set[str] = set()

    for chunk in chunks:
        ans = chunk.get("answer", {})
        for reply in ans.get("replies", []):
            content = reply.get("groundedContent", {}).get("content", {})
            text = content.get("text") or ""
            is_thought = content.get("thought", False)
            if text and not is_thought:
                answer_parts.append(text)
            for action in reply.get("actions", []) or []:
                fc = action.get("functionCall") or {}
                if fc:
                    tool_calls.append({"name": fc.get("name"), "args": fc.get("args", {})})
                fr = action.get("functionResponse") or {}
                if fr:
                    res_text = json.dumps(fr.get("response", {}), default=str)
                    keys = sorted(set(KEY_RE.findall(res_text)))
                    if tool_calls and tool_calls[-1].get("name") == fr.get("name"):
                        tool_calls[-1]["result_keys_returned"] = keys
                    else:
                        tool_calls.append({"name": fr.get("name"), "result_keys_returned": keys})
        gm = ans.get("groundingMetadata", {}) or {}
        for gc in gm.get("groundingChunks", []) or []:
            ctx = gc.get("retrievedContext") or {}
            uri = ctx.get("uri") or ""
            title = ctx.get("title") or ""
            sig = f"{title}|{uri}"
            if sig in seen_g:
                continue
            seen_g.add(sig)
            grounding.append({"title": title, "uri": uri, "text": (ctx.get("text") or "")[:400]})
    return "".join(answer_parts), tool_calls, grounding


# ---------------------------------------------------------------------------
# AE :streamQuery (Options A / AL / AG)
# ---------------------------------------------------------------------------
def _parse_ae_sse(body_text: str) -> tuple[str, list[dict[str, Any]]]:
    answer_parts: list[str] = []
    tool_calls: list[dict[str, Any]] = []
    last_call_idx: dict[str, int] = {}
    for raw in body_text.splitlines():
        raw = raw.strip()
        if not raw or raw.startswith("event:") or raw == "data:":
            continue
        if raw.startswith("data: "):
            raw = raw[6:]
        try:
            ev = json.loads(raw)
        except Exception:
            continue
        content = ev.get("content") or {}
        for part in content.get("parts", []) or []:
            if "text" in part and content.get("role") in (None, "model"):
                t = part.get("text") or ""
                if part.get("thought"):
                    continue
                if t:
                    answer_parts.append(t)
            if "function_call" in part:
                fc = part["function_call"]
                tool_calls.append({"name": fc.get("name"), "args": fc.get("args", {})})
                last_call_idx[fc.get("id") or fc.get("name") or ""] = len(tool_calls) - 1
            if "function_response" in part:
                fr = part["function_response"]
                key = fr.get("id") or fr.get("name") or ""
                idx = last_call_idx.get(key, len(tool_calls) - 1 if tool_calls else None)
                resp_text = json.dumps(fr.get("response") or {}, default=str)
                keys = sorted(set(KEY_RE.findall(resp_text)))
                if idx is not None and 0 <= idx < len(tool_calls):
                    tool_calls[idx]["result_keys_returned"] = keys
                else:
                    tool_calls.append({"name": fr.get("name"), "result_keys_returned": keys})
    return "".join(answer_parts), tool_calls


async def _run_agent_engine(question: str, agent_id: str, client: httpx.AsyncClient) -> RaceResult:
    resource = f"projects/{GE_PROJECT_NUMBER}/locations/{AE_REGION}/reasoningEngines/{agent_id}"
    query_url = f"https://{AE_REGION}-aiplatform.googleapis.com/v1beta1/{resource}:query"
    stream_url = f"https://{AE_REGION}-aiplatform.googleapis.com/v1beta1/{resource}:streamQuery?alt=sse"
    user_id = f"race-{int(time.time())}"
    t0 = time.perf_counter()
    try:
        sess_body = {"class_method": "async_create_session", "input": {"user_id": user_id}}
        s = await client.post(query_url, headers=_headers(), json=sess_body, timeout=60)
        s.raise_for_status()
        out = s.json().get("output", {})
        sid = out.get("id") or out.get("session_id")
        if not sid:
            return RaceResult(ok=False, elapsed_s=time.perf_counter() - t0,
                              error=f"no session id: {s.text[:200]}")
        body = {
            "class_method": "async_stream_query",
            "input": {"user_id": user_id, "session_id": sid, "message": question},
        }
        async with client.stream(
            "POST", stream_url, headers=_headers(), json=body, timeout=DEFAULT_TIMEOUT_S,
        ) as resp:
            lines: list[str] = []
            async for line in resp.aiter_lines():
                if line:
                    lines.append(line)
            text = "\n".join(lines)
            if resp.status_code >= 400:
                return RaceResult(ok=False, elapsed_s=time.perf_counter() - t0,
                                  error=f"http {resp.status_code}: {text[:300]}")
        answer, tool_calls = _parse_ae_sse(text)
        return RaceResult(
            ok=True, answer=answer, tool_calls=tool_calls,
            citations=sorted(set(KEY_RE.findall(answer))),
            elapsed_s=time.perf_counter() - t0,
        )
    except Exception as exc:
        return RaceResult(ok=False, elapsed_s=time.perf_counter() - t0,
                          error=f"{type(exc).__name__}: {exc}")


# ---------------------------------------------------------------------------
# streamAssist (Options B/C/CG/D/DG/E/EG/F)
# ---------------------------------------------------------------------------
def _ds_resource(ds_id: str) -> str:
    return (
        f"projects/{GE_PROJECT_NUMBER}/locations/{GE_LOCATION}/"
        f"collections/default_collection/dataStores/{ds_id}"
    )


def _streamassist_body(
    question: str, datastore_ids: list[str], model_id: str | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "query": {"parts": [{"text": question}]},
        "filter": "",
        "fileIds": [],
        "answerGenerationMode": "NORMAL",
        "toolsSpec": {
            "vertexAiSearchSpec": {
                "dataStoreSpecs": [{"dataStore": _ds_resource(d)} for d in datastore_ids],
            },
            "toolRegistry": "default_tool_registry",
            "imageGenerationSpec": {},
            "videoGenerationSpec": {},
        },
        "languageCode": "en-US",
        "userMetadata": {"timeZone": "America/New_York"},
        "assistSkippingMode": "REQUEST_ASSIST",
    }
    if model_id:
        body["generationSpec"] = {"modelId": model_id}
    return body


async def _run_streamassist(
    question: str, datastore_ids: list[str], model_id: str | None,
    client: httpx.AsyncClient, timeout_s: float = DEFAULT_TIMEOUT_S,
) -> RaceResult:
    t0 = time.perf_counter()
    if not datastore_ids:
        return RaceResult(ok=False, elapsed_s=0.0, error="no datastore id configured")
    body = _streamassist_body(question, datastore_ids, model_id)
    try:
        resp = await client.post(STREAM_ASSIST_URL, headers=_headers(), json=body, timeout=timeout_s)
    except Exception as exc:
        return RaceResult(ok=False, elapsed_s=time.perf_counter() - t0,
                          error=f"network: {type(exc).__name__}: {exc}")
    elapsed = time.perf_counter() - t0
    if resp.status_code >= 400:
        return RaceResult(ok=False, elapsed_s=elapsed,
                          error=f"http {resp.status_code}: {resp.text[:300]}")
    try:
        data = resp.json()
    except Exception as exc:
        return RaceResult(ok=False, elapsed_s=elapsed,
                          error=f"json parse: {exc}; body[:200]={resp.text[:200]}")
    chunks = data if isinstance(data, list) else [data]
    answer, tool_calls, grounding = _parse_streamassist_chunks(chunks)
    return RaceResult(
        ok=True, answer=answer, tool_calls=tool_calls,
        citations=sorted(set(KEY_RE.findall(answer))),
        grounding=grounding, elapsed_s=elapsed,
    )


# ---------------------------------------------------------------------------
# Public dispatcher
# ---------------------------------------------------------------------------
PIPELINE_KEYS = {"a", "al", "ag", "b", "c", "cg", "d", "dg", "e", "eg", "f"}


async def run_pipeline(key: str, question: str, client: httpx.AsyncClient) -> RaceResult:
    k = key.lower()
    if k == "a":
        return await _run_agent_engine(question, A_AGENT_ID, client)
    if k == "al":
        return await _run_agent_engine(question, A_LITE_AGENT_ID, client)
    if k == "ag":
        return await _run_agent_engine(question, A_G35_AGENT_ID, client)
    if k == "b":
        return await _run_streamassist(question, [B_DATASTORE_ID], None, client)
    if k == "c":
        return await _run_streamassist(question, [C_DATASTORE_ID], None, client)
    if k == "cg":
        return await _run_streamassist(question, [C_DATASTORE_ID], CG_MODEL_ID, client)
    if k == "d":
        ids = [s.strip() for s in D_DATASTORE_IDS.split(",") if s.strip()]
        return await _run_streamassist(question, ids, None, client)
    if k == "dg":
        ids = [s.strip() for s in D_DATASTORE_IDS.split(",") if s.strip()]
        return await _run_streamassist(question, ids, DG_MODEL_ID, client)
    if k == "e":
        return await _run_streamassist(question, [E_DATASTORE_ID], None, client, timeout_s=300.0)
    if k == "eg":
        return await _run_streamassist(question, [E_DATASTORE_ID], None, client, timeout_s=300.0)
    if k == "f":
        return await _run_streamassist(question, [F_DATASTORE_ID], None, client, timeout_s=300.0)
    return RaceResult(ok=False, elapsed_s=0.0, error=f"unknown pipeline: {key}")
