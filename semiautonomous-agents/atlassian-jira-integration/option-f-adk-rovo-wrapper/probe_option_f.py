"""End-to-end probe for Option F. Tells you EXACTLY which layer broke.

Layers checked, in order:
  1. Wrapper alive            (HTTP GET /)
  2. Wrapper tools/list works (POST /mcp directly with SA bearer)
  3. Wrapper tools/call works (POST /mcp ask_rovo_jira_expert with SA bearer)
  4. F datastore exists       (Discovery Engine GET)
  5. F datastore attached     (Engine.dataStoreIds includes F)
  6. GE streamAssist routes   (POST :streamAssist with dataStoreSpecs=[F])
  7. GE hit the wrapper       (Cloud Run logs show tools/list AND tools/call
                                 in the time window of the streamAssist call)

Each layer prints PASS / FAIL with a one-line reason. Stops at first FAIL
and prints the recommended next action.

Usage:
    GCLOUD_ACCOUNT=admin@jesusarguelles.altostrat.com \\
    GOOGLE_CLOUD_QUOTA_PROJECT=cloud-llm-preview1 \\
    python probe_option_f.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import requests

# ---- env --------------------------------------------------------------------
_HERE = Path(__file__).resolve().parent
for _cand in (_HERE / ".env", _HERE.parent / "eval" / ".env"):
    if _cand.exists():
        for line in _cand.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

PROJECT_ID = os.environ.get("GE_PROJECT_ID", "vtxdemos")
PROJECT_NUMBER = os.environ.get("GE_PROJECT_NUMBER", "254356041555")
ENGINE_ID = os.environ.get("GE_ENGINE_ID", "jira-testing_1778158449701")
LOCATION = os.environ.get("GE_LOCATION", "global")
COLLECTION = os.environ.get("GE_COLLECTION_ID", "default_collection")

DATASTORE_ID = os.environ.get(
    "OPTION_F_DATASTORE_ID", "mcp-adk-rovo-wrapper-1779480642_mcp_data"
)
WRAPPER_URL = os.environ.get(
    "WRAPPER_BASE_URL",
    "https://option-f-adk-rovo-wrapper-254356041555.us-central1.run.app",
).rstrip("/")
SERVICE_NAME = os.environ.get(
    "WRAPPER_SERVICE_NAME", "option-f-adk-rovo-wrapper"
)

PROBE_Q = os.environ.get(
    "PROBE_QUESTION",
    "List 5 issues from project SMP with their summaries.",
)

GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
RESET = "\033[0m"
BOLD = "\033[1m"


def _ok(msg: str) -> None:
    print(f"  {GREEN}PASS{RESET}  {msg}")


def _fail(msg: str, hint: str = "") -> None:
    print(f"  {RED}FAIL{RESET}  {msg}")
    if hint:
        print(f"        {YELLOW}fix:{RESET}  {hint}")


def _info(msg: str) -> None:
    print(f"        {msg}")


def _header(n: int, name: str) -> None:
    print(f"\n{BOLD}[{n}] {name}{RESET}")


def _gcp_token() -> str:
    acct = os.environ.get("GCLOUD_ACCOUNT")
    if acct:
        out = subprocess.run(
            ["gcloud", "auth", "print-access-token", "--account", acct],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    import google.auth
    import google.auth.transport.requests as gar
    creds, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    creds.refresh(gar.Request())
    return creds.token


def _ge_headers() -> dict:
    return {
        "Authorization": f"Bearer {_gcp_token()}",
        "Content-Type": "application/json",
        "x-goog-user-project": PROJECT_ID,
    }


def _logs_in_window(start_ts: float, end_ts: float, filter_extra: str = "") -> list[str]:
    """Return Cloud Run log textPayloads between start_ts and end_ts (unix)."""
    start_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(start_ts))
    end_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(end_ts + 1))
    flt = (
        f'resource.type="cloud_run_revision" '
        f'AND resource.labels.service_name="{SERVICE_NAME}" '
        f'AND timestamp>="{start_iso}" '
        f'AND timestamp<="{end_iso}"'
    )
    if filter_extra:
        flt += f" AND {filter_extra}"
    out = subprocess.run(
        ["gcloud", "logging", "read", flt, "--project", PROJECT_ID,
         "--limit", "200", "--format=value(textPayload)"],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        return []
    return [ln for ln in out.stdout.splitlines() if ln.strip()]


def probe() -> int:
    failed = 0
    print(f"\n{BOLD}=== Option F end-to-end probe ==={RESET}")
    print(f"  wrapper : {WRAPPER_URL}")
    print(f"  ds id   : {DATASTORE_ID}")
    print(f"  engine  : {ENGINE_ID}")
    print(f"  probe q : {PROBE_Q!r}")

    # 1) wrapper alive
    _header(1, "Wrapper alive")
    try:
        r = requests.get(WRAPPER_URL + "/", timeout=15)
        if r.status_code == 200:
            j = r.json()
            tools = j.get("tools", [])
            _ok(f"GET / → 200, tools={tools}")
            if "ask_rovo_jira_expert" not in tools:
                _fail(
                    "wrapper does not advertise ask_rovo_jira_expert",
                    "redeploy: gcloud run deploy option-f-adk-rovo-wrapper "
                    "--source server --region us-central1 --project vtxdemos",
                )
                return 1
        else:
            _fail(f"GET / → {r.status_code}", "cold start failed or rollout incomplete")
            return 1
    except Exception as e:
        _fail(f"GET / errored: {e}", "wrapper Cloud Run is down or wrong URL")
        return 1

    # 2) wrapper tools/list directly
    _header(2, "Wrapper /mcp tools/list (direct, SA bearer)")
    bearer = _gcp_token()
    headers = {"Authorization": f"Bearer {bearer}", "Content-Type": "application/json"}
    try:
        r = requests.post(
            WRAPPER_URL + "/mcp",
            headers=headers,
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
            timeout=30,
        )
        if r.status_code == 200:
            tools = r.json().get("result", {}).get("tools", [])
            names = [t.get("name") for t in tools]
            if "ask_rovo_jira_expert" in names:
                _ok(f"tools/list returned {names}")
            else:
                _fail(
                    f"tools/list missing ask_rovo_jira_expert: {names}",
                    "redeploy wrapper",
                )
                return 1
        else:
            _fail(f"tools/list → {r.status_code}: {r.text[:200]}")
            return 1
    except Exception as e:
        _fail(f"tools/list errored: {e}")
        return 1

    # 3) wrapper tools/call directly (will call Rovo MCP with NO user bearer →
    # likely returns an auth-error answer, but proves dispatch + agent work)
    _header(3, "Wrapper /mcp tools/call (direct, no user bearer)")
    try:
        r = requests.post(
            WRAPPER_URL + "/mcp",
            headers=headers,
            json={
                "jsonrpc": "2.0", "id": 2, "method": "tools/call",
                "params": {
                    "name": "ask_rovo_jira_expert",
                    "arguments": {"question": PROBE_Q},
                },
            },
            timeout=180,
        )
        if r.status_code == 200:
            body = r.json()
            if "error" in body:
                _fail(f"tools/call returned JSON-RPC error: {body['error']}")
                failed += 1
            else:
                content = body.get("result", {}).get("content", [])
                text = content[0].get("text", "") if content else ""
                _ok(f"tools/call → 200, answer[:120]={text[:120]!r}")
                if not text.strip():
                    _fail("answer was empty — agent_loop returned nothing")
                    failed += 1
        else:
            _fail(f"tools/call → {r.status_code}: {r.text[:200]}")
            failed += 1
    except Exception as e:
        _fail(f"tools/call errored: {e}")
        failed += 1

    # 4) datastore exists
    _header(4, "F datastore exists in Discovery Engine")
    ds_url = (
        f"https://discoveryengine.googleapis.com/v1alpha/"
        f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/"
        f"collections/{COLLECTION}/dataStores/{DATASTORE_ID}"
    )
    r = requests.get(ds_url, headers=_ge_headers(), timeout=30)
    if r.status_code == 200:
        _ok(f"GET dataStore → 200 ({DATASTORE_ID})")
    elif r.status_code == 404:
        _fail(
            f"datastore {DATASTORE_ID} not found (404)",
            "run register_datastore.py to create it",
        )
        return 1
    else:
        _fail(f"GET dataStore → {r.status_code}: {r.text[:200]}")
        return 1

    # 5) attached to engine
    _header(5, "F datastore attached to engine")
    eng_url = (
        f"https://discoveryengine.googleapis.com/v1alpha/"
        f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/"
        f"collections/{COLLECTION}/engines/{ENGINE_ID}"
    )
    r = requests.get(eng_url, headers=_ge_headers(), timeout=30)
    if r.status_code != 200:
        _fail(f"GET engine → {r.status_code}: {r.text[:200]}")
        return 1
    attached = r.json().get("dataStoreIds", [])
    if DATASTORE_ID in attached:
        _ok(f"engine.dataStoreIds includes {DATASTORE_ID} ({len(attached)} total)")
    else:
        _fail(
            f"engine.dataStoreIds does NOT include {DATASTORE_ID}",
            "run register_datastore.py — attach_to_engine step",
        )
        return 1

    # 6) streamAssist via F datastore filter — watch wrapper logs in parallel
    _header(6, "streamAssist with dataStoreSpecs=[F] (+ log capture)")
    sa_url = (
        f"https://discoveryengine.googleapis.com/v1alpha/"
        f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/"
        f"collections/{COLLECTION}/engines/{ENGINE_ID}/"
        f"assistants/default_assistant:streamAssist"
    )
    body = {
        "query": {"parts": [{"text": PROBE_Q}]},
        "filter": "",
        "fileIds": [],
        "answerGenerationMode": "NORMAL",
        "toolsSpec": {
            "vertexAiSearchSpec": {
                "dataStoreSpecs": [{
                    "dataStore": (
                        f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/"
                        f"collections/{COLLECTION}/dataStores/{DATASTORE_ID}"
                    )
                }]
            },
            "toolRegistry": "default_tool_registry",
            "imageGenerationSpec": {},
            "videoGenerationSpec": {},
        },
        "languageCode": "en-US",
        "userMetadata": {"timeZone": "America/New_York"},
        "assistSkippingMode": "REQUEST_ASSIST",
    }
    t0 = time.time()
    try:
        r = requests.post(sa_url, headers=_ge_headers(), json=body, timeout=300)
    except Exception as e:
        _fail(f"streamAssist errored: {e}")
        return 1
    t1 = time.time()
    if r.status_code >= 400:
        _fail(f"streamAssist → {r.status_code}: {r.text[:200]}")
        return 1
    chunks = r.json() if isinstance(r.json(), list) else [r.json()]
    answer_parts = []
    for c in chunks:
        for reply in c.get("answer", {}).get("replies", []) or []:
            txt = reply.get("groundedContent", {}).get("content", {}).get("text", "")
            if txt:
                answer_parts.append(txt)
    answer = "".join(answer_parts)
    _ok(f"streamAssist → 200 in {t1 - t0:.1f}s")
    _info(f"answer[:160] = {answer[:160]!r}")

    # 7) did GE actually hit our wrapper?
    _header(7, "GE actually invoked wrapper (Cloud Run logs)")
    # Give logs ~5s to land in Cloud Logging.
    time.sleep(6)
    logs = _logs_in_window(t0 - 2, t1 + 6)
    list_hits = [ln for ln in logs if "tools/list" in ln]
    call_hits = [ln for ln in logs if "tools/call" in ln or "ask START" in ln]
    bearer_yes = any("bearer=yes" in ln for ln in logs)
    bearer_no = any("bearer=no" in ln for ln in logs)
    _info(f"log lines in window: {len(logs)}")
    _info(f"  tools/list hits : {len(list_hits)}")
    _info(f"  tools/call hits : {len(call_hits)}")
    _info(f"  bearer present  : {'yes' if bearer_yes else ('no' if bearer_no else '?')}")

    if not list_hits and not call_hits:
        _fail(
            "GE never hit the wrapper for this request",
            "datastore tool surface is stale OR connector OAuth not enabled "
            "for the calling identity. Delete + re-register the datastore.",
        )
        failed += 1
    elif list_hits and not call_hits:
        _fail(
            "GE probed tools/list but skipped tools/call",
            "tool description/name doesn't match GE planner expectations, OR "
            "user OAuth token missing. Confirm 3LO is completed in GE UI as "
            "the same Google identity used for the eval.",
        )
        failed += 1
    elif call_hits and not bearer_yes:
        _fail(
            "tools/call reached the wrapper but with NO user bearer",
            "GE didn't inject a Rovo OAuth token. User needs to complete the "
            "3LO consent flow in GE chat under the F connector.",
        )
        failed += 1
    else:
        _ok("GE invoked tools/call with a user bearer — full path is green")

    # Final answer sanity
    has_key = any(
        seg in answer
        for seg in ("SMP-", "OPS-", "PROJ-")
    )
    if has_key:
        _ok("answer contains Jira issue keys")
    else:
        _fail(
            "answer contains NO Jira issue keys",
            "even if calls land, the upstream Rovo MCP isn't returning data — "
            "check OPTION_F_ROVO_CLIENT_ID/SECRET and Rovo token URL.",
        )
        failed += 1

    print(f"\n{BOLD}=== probe done: {failed} failure(s) ==={RESET}\n")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.exit(probe())
