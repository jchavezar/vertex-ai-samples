#!/usr/bin/env python3
"""
Comprehensive End-to-End (E2E) Verification Suite for the Rocket AI Hackathon Argon Suite.
Verifies:
1. All 8 Cloud Run Services (Unauthenticated 401 Gate + Authenticated 200 Login Gate)
2. All 33 Clickable Domain Demo UI Pages (?case=CODE)
3. All 33 Hosted Reproduction Documentation Pages (/docs/CODE)
4. All 33 Deterministic gVisor Sandbox Endpoints (POST /api/sandbox)
5. Live Vertex AI Gemini 4 Argon Execution Endpoints (POST /api/run-demo across all 7 domain apps)
6. All 33 Local GitHub Subfolders (docs/REPRODUCTION_GUIDE.md, code/agent.py, code/sandbox_tool.py, mock_data/sample_payload.json)
"""
import base64
import concurrent.futures
import json
import os
import subprocess
import sys
import time
import urllib.request
import shutil
import urllib.error

sys.path.insert(0, "/usr/local/google/home/jesusarguelles/rocket")
from shared.catalog_data import ALL_DOMAINS, CLOUD_RUN_URLS, PROJECTS_BY_CODE

TARGET_ROOT = "/usr/local/google/home/jesusarguelles/vertex-ai-samples/semiautonomous-agents/rocket-ai-hackathon-argon-suite"
AUTH_HEADER = "Basic " + base64.b64encode(b"rocket:Argon2026!").decode("ascii")


def http_request(url: str, method: str = "GET", payload: dict | None = None, use_auth: bool = True, timeout: int = 45):
    headers = {"User-Agent": "Rocket-Argon-E2E-Verifier/1.0"}
    if use_auth:
        headers["Authorization"] = AUTH_HEADER
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status, body, round((time.time() - t0) * 1000, 1)
    except urllib.error.HTTPError as e:
        return e.code, "", round((time.time() - t0) * 1000, 1)
    except Exception as e:
        return 0, str(e), round((time.time() - t0) * 1000, 1)


def verify_service_gate(item):
    key, url = item
    # Without auth -> should redirect (302/307) or return 401 or login page containing 'Argon2026' or 'Private Access'
    # Note: urllib follows redirects to /login which returns HTTP 200 with login form, whereas /api/health returns 200 and /api/sandbox without auth returns 401
    unauth_status, _, _ = http_request(f"{url}/api/sandbox", method="POST", payload={"action": "default"}, use_auth=False)
    auth_status, body, latency_ms = http_request(url, method="GET", use_auth=True)
    ok = (unauth_status == 401) and (auth_status == 200) and len(body) > 2000
    return {
        "service_key": key,
        "url": url,
        "unauth_api_status": unauth_status,
        "auth_ui_status": auth_status,
        "html_bytes": len(body),
        "latency_ms": latency_ms,
        "ok": ok,
    }


def verify_square_e2e(sq_row):
    code = sq_row["code"]
    proj = PROJECTS_BY_CODE[code]
    demo_url = sq_row["demo_link"]
    doc_url = sq_row["doc_cloud_link"]
    domain_base_url = CLOUD_RUN_URLS[sq_row["domain_id"]]

    # 1. Verify Demo UI page (?case=CODE)
    ui_status, ui_body, ui_ms = http_request(demo_url, method="GET", use_auth=True)
    ui_ok = (ui_status == 200) and (code in ui_body)

    # 2. Verify Reproduction Doc page (/docs/CODE)
    doc_status, doc_body, doc_ms = http_request(doc_url, method="GET", use_auth=True)
    doc_ok = (doc_status == 200) and (code in doc_body) and ("Step-by-Step" in doc_body or "Architecture" in doc_body or "Reproduce" in doc_body)

    # 3. Verify Deterministic Sandbox API on the Domain Cloud Run service (POST /api/sandbox)
    sb_status, sb_body, sb_ms = http_request(
        f"{domain_base_url}/api/sandbox",
        method="POST",
        payload={"action": proj.get("sandboxAction", "default"), "params": proj.get("sandboxParams", {})},
        use_auth=True,
    )
    sb_json = {}
    try:
        sb_json = json.loads(sb_body)
    except Exception:
        pass
    sb_ok = (sb_status == 200) and (sb_json.get("ok") is True or "result" in sb_json)

    # 4. Verify Local GitHub Subfolder Files & Standalone Sandbox Script
    sq_folder = os.path.join(TARGET_ROOT, sq_row["rel_github_path"])
    req_files = [
        os.path.join(sq_folder, "README.md"),
        os.path.join(sq_folder, "docs", "REPRODUCTION_GUIDE.md"),
        os.path.join(sq_folder, "code", "agent.py"),
        os.path.join(sq_folder, "code", "sandbox_tool.py"),
        os.path.join(sq_folder, "mock_data", "sample_payload.json"),
    ]
    files_ok = all(os.path.isfile(f) and os.path.getsize(f) > 100 for f in req_files)

    proc = subprocess.run(
        [sys.executable, os.path.join(sq_folder, "code", "sandbox_tool.py")],
        capture_output=True,
        text=True,
        timeout=10,
    )
    local_sb_ok = (proc.returncode == 0) and len(proc.stdout.strip()) > 10

    return {
        "code": code,
        "title": sq_row["title"],
        "domain_id": sq_row["domain_id"],
        "ui_ok": ui_ok,
        "ui_ms": ui_ms,
        "doc_ok": doc_ok,
        "doc_ms": doc_ms,
        "cloud_sandbox_ok": sb_ok,
        "cloud_sandbox_ms": sb_ms,
        "github_files_ok": files_ok,
        "local_sandbox_ok": local_sb_ok,
        "all_ok": ui_ok and doc_ok and sb_ok and files_ok and local_sb_ok,
    }


def verify_domain_live_vertex(d_meta):
    d_key = d_meta["id"]
    d_url = CLOUD_RUN_URLS[d_key]
    first_code = d_meta["projects"][0]["code"]
    status, body, ms = http_request(
        f"{d_url}/api/run-demo",
        method="POST",
        payload={"code": first_code, "model": "gemini-4-argon"},
        use_auth=True,
        timeout=60,
    )
    data = {}
    try:
        data = json.loads(body)
    except Exception:
        pass
    ok = (status == 200) and (data.get("ok") is True) and len(data.get("output", "")) > 80
    return {
        "domain_id": d_key,
        "service_name": d_meta["service_name"],
        "tested_square": first_code,
        "status": status,
        "model_used": data.get("model_used", ""),
        "output_chars": len(data.get("output", "")),
        "latency_ms": ms,
        "ok": ok,
    }


if __name__ == "__main__":
    print("=== 1. VERIFYING ALL 8 CLOUD RUN SERVICES (AUTH GATE + UI) ===")
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        service_results = list(ex.map(verify_service_gate, CLOUD_RUN_URLS.items()))
    for r in service_results:
        print(f"  [{ 'PASS' if r['ok'] else 'FAIL' }] {r['service_key']:10s} | Unauth API: {r['unauth_api_status']} | Auth UI: {r['auth_ui_status']} ({r['html_bytes']} bytes, {r['latency_ms']}ms) -> {r['url']}")

    with open(os.path.join(TARGET_ROOT, "docs", "square_index.json")) as f:
        sq_rows = json.load(f)

    print(f"\n=== 2. VERIFYING ALL {len(sq_rows)} SQUARES (UI + DOCS + CLOUD SANDBOX + GITHUB FOLDER + LOCAL SANDBOX) ===")
    with concurrent.futures.ThreadPoolExecutor(max_workers=11) as ex:
        sq_results = list(ex.map(verify_square_e2e, sq_rows))
    for r in sq_results:
        print(
            f"  [{ 'PASS' if r['all_ok'] else 'FAIL' }] Square [{r['code']:3s}] {r['title'][:40]:40s} | "
            f"UI:{r['ui_ok']} ({r['ui_ms']}ms) | Doc:{r['doc_ok']} | CloudSB:{r['cloud_sandbox_ok']} | GitHubFiles:{r['github_files_ok']} | LocalSB:{r['local_sandbox_ok']}"
        )

    print("\n=== 3. VERIFYING LIVE VERTEX AI (gemini-4-argon) SYNTHESIS ACROSS ALL 7 DOMAIN SERVICES ===")
    with concurrent.futures.ThreadPoolExecutor(max_workers=7) as ex:
        vertex_results = list(ex.map(verify_domain_live_vertex, ALL_DOMAINS))
    for r in vertex_results:
        print(
            f"  [{ 'PASS' if r['ok'] else 'FAIL' }] {r['service_name']:26s} (Square [{r['tested_square']}]) | "
            f"Model: {r['model_used']} | Output: {r['output_chars']} chars | {r['latency_ms']}ms"
        )

    summary = {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "services_passed": sum(1 for r in service_results if r["ok"]),
        "services_total": len(service_results),
        "squares_passed": sum(1 for r in sq_results if r["all_ok"]),
        "squares_total": len(sq_results),
        "vertex_domains_passed": sum(1 for r in vertex_results if r["ok"]),
        "vertex_domains_total": len(vertex_results),
        "service_results": service_results,
        "square_results": sq_results,
        "vertex_results": vertex_results,
    }
    os.makedirs(os.path.join(TARGET_ROOT, "tests"), exist_ok=True)
    shutil.copy2(__file__, os.path.join(TARGET_ROOT, "tests", "e2e_verify_all_33_demos.py"))
    with open(os.path.join(TARGET_ROOT, "docs", "E2E_VERIFICATION_REPORT.json"), "w") as f:
        json.dump(summary, f, indent=2)

    print(
        f"\n=== FINAL E2E SCORE: Services {summary['services_passed']}/{summary['services_total']} | "
        f"Squares {summary['squares_passed']}/{summary['squares_total']} | "
        f"Live Gemini 4 Argon Domains {summary['vertex_domains_passed']}/{summary['vertex_domains_total']} ==="
    )
    if (
        summary["services_passed"] != summary["services_total"]
        or summary["squares_passed"] != summary["squares_total"]
        or summary["vertex_domains_passed"] != summary["vertex_domains_total"]
    ):
        sys.exit(1)

# Additional E2E checks for WebSocket Live Audio and StreamAssist
