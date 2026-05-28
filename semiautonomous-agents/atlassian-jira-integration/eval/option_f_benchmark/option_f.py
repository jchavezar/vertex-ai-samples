"""Option F benchmark: ADK-style agent + Atlassian Jira tools + Flash Lite.

Goal: measure end-to-end latency for an agent that calls Jira through
Atlassian's official surface — i.e. WITHOUT a custom Jira REST wrapper the
customer would have to maintain.

What this script actually does
------------------------------
Pattern: Option E's tool-call loop (google-genai), because real ADK
`LlmAgent` + `MCPToolset` against Atlassian's Rovo MCP needs the cf.mcp
OAuth authorization_code flow (browser pop-up; can't be automated as a
script). The brief explicitly authorises falling back to direct REST.

Tool layer: a single function declaration `search_jira_jql` that hits
`https://sockcop.atlassian.net/rest/api/3/search/jql` with HTTP Basic
(email + API token from eval/.env). This is the exact API the Rovo MCP
`searchJiraIssuesUsingJql` tool wraps — the wire latency profile is
the same modulo MCP protocol framing.

Documented fallback ====> result is a fair latency proxy for Option F's
"agent + Atlassian-managed tool" architecture.

Model: tries gemini-flash-lite-latest, then 3-flash-lite-preview, then
3.5-flash-lite, then 2.5-flash-lite. Records which one was used.

Output:
  - results.jsonl (one row per question)
  - stdout summary: n/min/p50/p90/max/mean + accuracy
"""
from __future__ import annotations

import base64
import json
import os
import statistics
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx

# Force quota project at process start (memory: NEVER mutate global ADC).
os.environ.setdefault("GOOGLE_CLOUD_QUOTA_PROJECT", "cloud-llm-preview1")

from google import genai  # noqa: E402
from google.genai import types  # noqa: E402
import google.auth  # noqa: E402

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
EVAL_ROOT = HERE.parent
ENV_FILE = EVAL_ROOT / ".env"


def _load_env() -> None:
    """Minimal .env loader so we don't pull in python-dotenv."""
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())


_load_env()

ATLASSIAN_SITE_URL = os.environ.get("ATLASSIAN_SITE_URL", "https://sockcop.atlassian.net")
ATLASSIAN_EMAIL = os.environ["ATLASSIAN_EMAIL"]
ATLASSIAN_API_TOKEN = os.environ["ATLASSIAN_API_TOKEN"]

GCP_PROJECT = "cloud-llm-preview1"   # quota project also acts as the billing project here
GCP_LOCATION = "global"

CANDIDATE_MODELS = [
    "gemini-flash-lite-latest",
    "gemini-3-flash-lite-preview",
    "gemini-3.5-flash-lite",
    "gemini-2.5-flash-lite",
]

MAX_LOOP_ITERATIONS = 6
JIRA_TIMEOUT_S = 30.0
N_QUESTIONS = 10
DATA_JSON = EVAL_ROOT / "comparison-site" / "data.json"
RESULTS_PATH = HERE / "results.jsonl"


# ---------------------------------------------------------------------------
# Jira REST tool — what Rovo MCP wraps under the hood
# ---------------------------------------------------------------------------
def _basic_header() -> dict[str, str]:
    raw = f"{ATLASSIAN_EMAIL}:{ATLASSIAN_API_TOKEN}".encode()
    return {
        "Authorization": f"Basic {base64.b64encode(raw).decode()}",
        "Accept": "application/json",
    }


def jira_search_jql(
    client: httpx.Client,
    jql: str,
    max_results: int = 50,
    fields: list[str] | None = None,
) -> str:
    """Call the new Atlassian /rest/api/3/search/jql endpoint and return a
    compact string view of the results. Returns at most max_results issues
    in a single call — no internal pagination (the brief asks for a fair
    proxy, not pagination heroics)."""
    fields_str = ",".join(fields or ["summary", "status", "priority", "issuetype", "labels"])
    params = {
        "jql": jql,
        "maxResults": max(1, min(max_results, 100)),
        "fields": fields_str,
    }
    t0 = time.perf_counter()
    try:
        resp = client.get(
            f"{ATLASSIAN_SITE_URL}/rest/api/3/search/jql",
            params=params,
            headers=_basic_header(),
            timeout=JIRA_TIMEOUT_S,
        )
    except Exception as exc:
        return f"Error calling Jira: {exc}"
    elapsed = time.perf_counter() - t0
    if resp.status_code >= 400:
        return f"Error: HTTP {resp.status_code}: {resp.text[:300]}"
    try:
        body = resp.json()
    except Exception as exc:
        return f"Error: non-JSON response: {exc}"
    issues = body.get("issues") or []
    lines: list[str] = [f"Found {len(issues)} issues (HTTP 200 in {elapsed:.2f}s) for JQL: {jql}"]
    for it in issues:
        key = it.get("key", "?")
        f = it.get("fields") or {}
        summary = (f.get("summary") or "")[:120]
        status = ((f.get("status") or {}).get("name")) or "?"
        prio = ((f.get("priority") or {}).get("name")) or "?"
        url = f"{ATLASSIAN_SITE_URL}/browse/{key}"
        lines.append(f"- [{key}]({url}) status={status} prio={prio}: {summary}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Function declarations for Gemini
# ---------------------------------------------------------------------------
TOOLS: list[types.FunctionDeclaration] = [
    types.FunctionDeclaration(
        name="search_jira_jql",
        description=(
            "Search Jira issues by JQL. Returns up to `max_results` issues "
            "with key, status, priority, and summary. This is the same "
            "operation Atlassian's Rovo MCP `searchJiraIssuesUsingJql` "
            "tool performs."
        ),
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "jql": types.Schema(type=types.Type.STRING, description="JQL query string."),
                "max_results": types.Schema(
                    type=types.Type.INTEGER,
                    description="Max issues to return (1-100). Default 50.",
                ),
            },
            required=["jql"],
        ),
    ),
]


def _system_prompt() -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    return (
        f"You are a Jira assistant. Today is {today}. The Jira site is "
        f"{ATLASSIAN_SITE_URL}.\n\n"
        "Use the search_jira_jql tool to answer questions. Common projects: "
        "SMP, BUGS, CRM, OPS, PLAT. When a question names a project (e.g. "
        "'OPS issues'), scope JQL with `project = X`. For labels use "
        "`labels in (\"a\",\"b\")`. For components use `component in (...)`. "
        "Always include enough fields to support your answer.\n\n"
        "When you answer, ALWAYS list every issue key you found. Format keys "
        "verbatim like OPS-97. Quote the count exactly. Do NOT fabricate keys."
    )


# ---------------------------------------------------------------------------
# Pick model
# ---------------------------------------------------------------------------
def pick_model(client: genai.Client) -> str:
    for m in CANDIDATE_MODELS:
        try:
            client.models.generate_content(model=m, contents="ok")
            return m
        except Exception as e:  # noqa: BLE001
            print(f"  candidate {m}: FAIL {str(e)[:120]}", file=sys.stderr)
    raise RuntimeError("No candidate flash-lite model is reachable.")


# ---------------------------------------------------------------------------
# Agent loop
# ---------------------------------------------------------------------------
def run_agent(
    genai_client: genai.Client,
    http_client: httpx.Client,
    model: str,
    question: str,
) -> tuple[str, list[dict[str, Any]], int]:
    """Return (final_answer, tool_call_records, iterations)."""
    contents: list[types.Content] = [
        types.Content(role="user", parts=[types.Part.from_text(text=question)])
    ]
    config = types.GenerateContentConfig(
        system_instruction=_system_prompt(),
        temperature=0.2,
        tools=[types.Tool(function_declarations=TOOLS)],
    )

    tool_calls: list[dict[str, Any]] = []

    for it in range(1, MAX_LOOP_ITERATIONS + 1):
        try:
            resp = genai_client.models.generate_content(
                model=model, contents=contents, config=config,
            )
        except Exception as exc:
            return f"[model_error] {exc}", tool_calls, it

        cand = (resp.candidates or [None])[0]
        if cand is None or cand.content is None:
            return (resp.text or "").strip() or "[empty]", tool_calls, it

        contents.append(cand.content)

        fcalls = [p.function_call for p in (cand.content.parts or []) if p.function_call is not None]
        text_parts = [p.text for p in (cand.content.parts or []) if p.text and not getattr(p, "thought", False)]

        if not fcalls:
            return "".join(text_parts).strip() or "[empty]", tool_calls, it

        response_parts: list[types.Part] = []
        for fc in fcalls:
            name = fc.name or ""
            args = dict(fc.args or {})
            tcall_t0 = time.perf_counter()
            if name == "search_jira_jql":
                result = jira_search_jql(
                    http_client,
                    jql=str(args.get("jql", "")),
                    max_results=int(args.get("max_results", 50) or 50),
                )
            else:
                result = f"Error: unknown tool {name}"
            tool_calls.append({
                "tool": name,
                "args": args,
                "elapsed_s": time.perf_counter() - tcall_t0,
                "result_len": len(result),
            })
            response_parts.append(
                types.Part.from_function_response(name=name, response={"result": result})
            )
        contents.append(types.Content(role="user", parts=response_parts))

    return "[max_iterations_exhausted]", tool_calls, MAX_LOOP_ITERATIONS


# ---------------------------------------------------------------------------
# Question loading
# ---------------------------------------------------------------------------
def load_q5_questions(n: int) -> list[dict[str, Any]]:
    raw = json.loads(DATA_JSON.read_text())
    items = raw if isinstance(raw, list) else raw.get("questions", [])
    q5 = [x for x in items if isinstance(x, dict) and str(x.get("id", "")).startswith("q5")]
    return q5[:n]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    print(f"[{datetime.now():%H:%M:%S}] starting option_f benchmark")

    creds, _ = google.auth.default(quota_project_id="cloud-llm-preview1")
    genai_client = genai.Client(
        vertexai=True,
        project=GCP_PROJECT,
        location=GCP_LOCATION,
        credentials=creds,
    )

    print("Picking model ...")
    model = pick_model(genai_client)
    print(f"  selected model: {model}")

    questions = load_q5_questions(N_QUESTIONS)
    print(f"Loaded {len(questions)} q5xxx questions")

    rows: list[dict[str, Any]] = []
    elapsed_list: list[float] = []
    acc_hits = 0

    with httpx.Client() as http_client, RESULTS_PATH.open("w") as f_out:
        for i, q in enumerate(questions, 1):
            qid = q["id"]
            qtext = q["q"]
            expected_keys = q.get("expected_keys_sample") or []
            print(f"\n[{i}/{len(questions)}] {qid} :: {qtext[:90]}")
            t0 = time.perf_counter()
            try:
                answer, tool_calls, iters = run_agent(
                    genai_client, http_client, model, qtext,
                )
                err = None
            except Exception as exc:  # noqa: BLE001
                answer, tool_calls, iters, err = f"[exception] {exc}", [], 0, str(exc)
            elapsed = time.perf_counter() - t0
            elapsed_list.append(elapsed)

            # Accuracy: all expected_keys_sample appear in the answer text.
            all_present = bool(expected_keys) and all(k in answer for k in expected_keys)
            if all_present:
                acc_hits += 1

            row = {
                "id": qid,
                "q": qtext,
                "model": model,
                "elapsed_s": elapsed,
                "iterations": iters,
                "n_tool_calls": len(tool_calls),
                "tool_calls": tool_calls,
                "answer": answer,
                "expected_keys_sample": expected_keys,
                "all_expected_present": all_present,
                "error": err,
            }
            rows.append(row)
            f_out.write(json.dumps(row, default=str) + "\n")
            f_out.flush()
            print(
                f"  -> {elapsed:.2f}s iters={iters} tools={len(tool_calls)} "
                f"acc={'Y' if all_present else 'N'} ans_len={len(answer)}"
            )

    # Summary
    print("\n" + "=" * 68)
    print("SUMMARY")
    print("=" * 68)
    if elapsed_list:
        srt = sorted(elapsed_list)
        n = len(srt)
        p50 = statistics.median(srt)
        # robust p90 for small n
        p90 = srt[max(0, int(round(0.9 * n)) - 1)] if n >= 2 else srt[0]
        print(
            f"n={n}  min={min(srt):.2f}s  p50={p50:.2f}s  p90={p90:.2f}s  "
            f"max={max(srt):.2f}s  mean={statistics.mean(srt):.2f}s"
        )
        print(f"Accuracy (all expected_keys_sample present): {acc_hits}/{n}")
    print(f"\nResults: {RESULTS_PATH}")


if __name__ == "__main__":
    main()
