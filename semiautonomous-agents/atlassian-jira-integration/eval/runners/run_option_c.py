"""Option C runner — ADK + Atlassian Rovo MCP.

Same pattern as Option A (invoke AE :streamQuery directly), but with Rovo MCP
instead of the custom MCP server.
"""
from __future__ import annotations

import asyncio
import json
import os
import time
from pathlib import Path
from typing import Any

import google.auth
import google.auth.transport.requests
from google.oauth2 import service_account
import httpx

from . import _common as C

OPTION_C_AE_RESOURCE = os.environ.get(
    "OPTION_C_AE_RESOURCE",
    f"projects/{C.GE_PROJECT_NUMBER}/locations/us-central1/reasoningEngines/4970193329535844352",
)
AE_REGION = OPTION_C_AE_RESOURCE.split("/locations/")[1].split("/")[0]
AE_STREAM_URL = (
    f"https://{AE_REGION}-aiplatform.googleapis.com/v1beta1/{OPTION_C_AE_RESOURCE}:streamQuery?alt=sse"
)


def build_session_url() -> str:
    return f"https://{AE_REGION}-aiplatform.googleapis.com/v1beta1/{OPTION_C_AE_RESOURCE}:query"


def build_query_payload(question_text: str, session_id: str, user_id: str = "eval-user") -> dict[str, Any]:
    return {
        "class_method": "async_stream_query",
        "input": {
            "user_id": user_id,
            "session_id": session_id,
            "message": question_text,
        },
    }


def _ae_token() -> str:
    """Get token for Agent Engine :query/:streamQuery.

    Try SA credentials first (for deployment-container pattern), fallback to ADC.
    """
    sa_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if sa_path and Path(sa_path).exists():
        creds = service_account.Credentials.from_service_account_file(
            sa_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        creds.refresh(google.auth.transport.requests.Request())
        return creds.token  # type: ignore
    # Fallback to ADC (user creds)
    return C._gcp_token()


def _ae_headers() -> dict[str, str]:
    """Build headers for Agent Engine :query/:streamQuery."""
    return {
        "Authorization": f"Bearer {_ae_token()}",
        "Content-Type": "application/json",
        "x-goog-user-project": C.GE_PROJECT_ID,
    }


async def _create_session(client: httpx.AsyncClient, user_id: str = "eval-user") -> str:
    body = {"class_method": "async_create_session", "input": {"user_id": user_id}}
    url = f"https://{AE_REGION}-aiplatform.googleapis.com/v1beta1/{OPTION_C_AE_RESOURCE}:query"
    resp = await client.post(url, headers=_ae_headers(), json=body, timeout=60)
    resp.raise_for_status()
    out = resp.json().get("output", {})
    sid = out.get("id") or out.get("session_id")
    if not sid:
        raise RuntimeError(f"No session id in response: {resp.text[:300]}")
    return sid


def _parse_ae_sse(body_text: str) -> tuple[str, list[dict[str, Any]]]:
    """Parse :streamQuery?alt=sse response. Each line is a JSON event."""
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
        # ADK events shape: {"content": {"role": "model"|"user", "parts": [{...}]}, ...}
        content = ev.get("content") or {}
        for part in content.get("parts", []) or []:
            if "text" in part and content.get("role") in (None, "model"):
                t = part.get("text") or ""
                # Skip thinking text (parts with `thought: true`)
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
                # Find matching call by id
                key = fr.get("id") or fr.get("name") or ""
                idx = last_call_idx.get(key, len(tool_calls) - 1 if tool_calls else None)
                resp_text = json.dumps(fr.get("response") or {}, default=str)
                keys = sorted(set(C.KEY_RE.findall(resp_text)))
                if idx is not None and 0 <= idx < len(tool_calls):
                    tool_calls[idx]["result_keys_returned"] = keys
                else:
                    tool_calls.append({"name": fr.get("name"), "result_keys_returned": keys})
    return "".join(answer_parts), tool_calls


async def run_one(question: dict[str, Any], client: httpx.AsyncClient, raw_dir: Path) -> C.RunnerResult:
    qid = question["id"]
    raw_path = raw_dir / f"{qid}_c.json"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    user_id = f"eval-{qid}"
    try:
        session_id = await _create_session(client, user_id=user_id)
        body = build_query_payload(question["q"], session_id, user_id=user_id)
        url = AE_STREAM_URL
        async with client.stream("POST", url, headers=_ae_headers(), json=body, timeout=300) as resp:
            chunks = []
            async for line in resp.aiter_lines():
                if not line:
                    continue
                chunks.append(line)
            text = "\n".join(chunks)
            raw_path.write_text(text)
            if resp.status_code >= 400:
                return C.RunnerResult(id=qid, pipeline="c", ok=False, answer="",
                                      elapsed_s=time.perf_counter() - t0,
                                      error=f"http {resp.status_code}: {text[:300]}",
                                      raw_path=str(raw_path))
        elapsed = time.perf_counter() - t0
        answer, tool_calls = _parse_ae_sse(text)
        return C.RunnerResult(
            id=qid, pipeline="c", ok=True, answer=answer,
            tool_calls=tool_calls, citations=C.cited_keys(answer),
            elapsed_s=elapsed, raw_path=str(raw_path),
        )
    except Exception as exc:
        return C.RunnerResult(id=qid, pipeline="c", ok=False, answer="",
                              elapsed_s=time.perf_counter() - t0,
                              error=f"{type(exc).__name__}: {exc}",
                              raw_path=str(raw_path))
