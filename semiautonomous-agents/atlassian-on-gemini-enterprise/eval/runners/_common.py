"""Shared helpers for the streamAssist runners (Option A & Option B).

Both runners hit the SAME endpoint with DIFFERENT request bodies and routings:
- Option A: agentsSpec.agentSpecs[].agentId  → registered Agent Engine
- Option B: toolsSpec.vertexAiSearchSpec.dataStoreSpecs[].dataStore  → custom MCP DS

The exact streamAssist body shape is non-negotiable — see memory
`streamassist_request_shape.md`. Don't trust v1alpha schema docs; copy from
the GE Console's browser DevTools network tab.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

import google.auth
import google.auth.transport.requests
import httpx

# --- .env loader (no python-dotenv dep) ---------------------------------------
_HERE = Path(__file__).resolve().parent.parent
_env = _HERE / ".env"
if _env.exists():
    for line in _env.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

GE_PROJECT_NUMBER = os.environ.get("GE_PROJECT_NUMBER", "254356041555")
GE_PROJECT_ID = os.environ.get("GE_PROJECT_ID", "vtxdemos")
GE_ENGINE_ID = os.environ.get("GE_ENGINE_ID", "jira-testing_1778158449701")
GE_LOCATION = os.environ.get("GE_LOCATION", "global")

STREAM_ASSIST_URL = (
    f"https://discoveryengine.googleapis.com/v1alpha/"
    f"projects/{GE_PROJECT_NUMBER}/locations/{GE_LOCATION}/"
    f"collections/default_collection/engines/{GE_ENGINE_ID}/"
    f"assistants/default_assistant:streamAssist"
)

KEY_RE = re.compile(r"\b([A-Z][A-Z0-9_]+-\d+)\b")


def _gcp_token() -> str:
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(google.auth.transport.requests.Request())
    return creds.token  # type: ignore[return-value]


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {_gcp_token()}",
        "Content-Type": "application/json",
        "x-goog-user-project": GE_PROJECT_ID,
    }


@dataclass
class RunnerResult:
    id: str
    pipeline: str  # "a" | "b"
    ok: bool
    answer: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    citations: list[str] = field(default_factory=list)
    grounding_chunks: list[dict[str, Any]] = field(default_factory=list)
    elapsed_s: float = 0.0
    error: str | None = None
    raw_path: str | None = None

    def to_jsonl_line(self) -> str:
        return json.dumps(asdict(self), default=str, ensure_ascii=False)


def _parse_stream(chunks: list[dict[str, Any]]) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
    """Walk all chunks, accumulate answer text (skip thoughts), tool calls,
    grounding chunks. Mirrors discovery-engine-latency-probe/probe.py:200-225.
    """
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

            # Adk surfaces tool calls under reply['actions'] or as part of executable code.
            for action in reply.get("actions", []) or []:
                fc = (action.get("functionCall") or {})
                if fc:
                    tool_calls.append({"name": fc.get("name"), "args": fc.get("args", {})})
                fr = (action.get("functionResponse") or {})
                if fr:
                    # capture issue keys returned by the tool
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


async def call_stream_assist(
    body: dict[str, Any],
    client: httpx.AsyncClient,
    raw_dump_path: Path | None = None,
    timeout_s: float = 180.0,
) -> tuple[bool, list[dict[str, Any]], str | None]:
    """POST a streamAssist request, return (ok, chunks, error)."""
    try:
        resp = await client.post(STREAM_ASSIST_URL, headers=_headers(), json=body, timeout=timeout_s)
    except Exception as exc:  # network / timeout
        return False, [], f"network: {exc}"
    if resp.status_code >= 400:
        return False, [], f"http {resp.status_code}: {resp.text[:400]}"
    try:
        data = resp.json()
    except Exception as exc:
        return False, [], f"json parse: {exc}; body[:200]={resp.text[:200]}"
    chunks = data if isinstance(data, list) else [data]
    if raw_dump_path is not None:
        raw_dump_path.parent.mkdir(parents=True, exist_ok=True)
        raw_dump_path.write_text(json.dumps(chunks, indent=2, default=str))
    return True, chunks, None


def cited_keys(answer: str) -> list[str]:
    """Issue keys mentioned in the answer text (Markdown link or bare)."""
    return sorted(set(KEY_RE.findall(answer)))


# --- Resumable JSONL append ---------------------------------------------------

def already_done_ids(jsonl_path: Path) -> set[str]:
    if not jsonl_path.exists():
        return set()
    out: set[str] = set()
    for line in jsonl_path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.add(json.loads(line)["id"])
        except Exception:
            pass
    return out


def append_jsonl(jsonl_path: Path, line: str) -> None:
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with jsonl_path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
