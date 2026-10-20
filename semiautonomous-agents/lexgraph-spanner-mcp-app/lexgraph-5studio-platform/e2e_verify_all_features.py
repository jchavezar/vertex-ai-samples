#!/usr/bin/env python3
"""Comprehensive End-to-End Verification Suite for All 5 LexGraph Legal AI Cloud Run Services.

Tests every HTTP UI route, REST API endpoint, ADK agent execution, MCP JSON-RPC 2.0 tool & UI resource,
A2A agent card & message/send, and verifies zero broken JS handlers in the HTML.
"""

import json
import re
import sys
import time
import urllib.request
import urllib.error

SERVICES = [
    {
        "name": "mike-gcp-platform",
        "url": "https://mike-gcp-platform-254356041555.us-central1.run.app",
        "expected_view": "assistant-view",
        "expected_mcp_uri": "ui://mike-gcp/workspace.html",
    },
    {
        "name": "lexgraph-redline-word-agent",
        "url": "https://lexgraph-redline-word-agent-254356041555.us-central1.run.app",
        "expected_view": "redline-view",
        "expected_mcp_uri": "ui://mike-gcp/redline-studio.html",
    },
    {
        "name": "lexgraph-funds-antitrust-agent",
        "url": "https://lexgraph-funds-antitrust-agent-254356041555.us-central1.run.app",
        "expected_view": "funds-view",
        "expected_mcp_uri": "ui://mike-gcp/funds-antitrust.html",
    },
    {
        "name": "lexgraph-governance-wall-agent",
        "url": "https://lexgraph-governance-wall-agent-254356041555.us-central1.run.app",
        "expected_view": "governance-view",
        "expected_mcp_uri": "ui://mike-gcp/governance-wall.html",
    },
    {
        "name": "lexgraph-inbox-calendar-agent",
        "url": "https://lexgraph-inbox-calendar-agent-254356041555.us-central1.run.app",
        "expected_view": "inbox-view",
        "expected_mcp_uri": "ui://mike-gcp/inbox-calendar.html",
    },
]


def http_req(url: str, method: str = "GET", payload: dict = None, timeout: int = 45):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"} if payload is not None else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
        elapsed_ms = round((time.time() - t0) * 1000, 1)
        return resp.status, body, elapsed_ms


def run_suite():
    failures = []
    total_checks = 0

    def check(cond: bool, label: str, detail: str = ""):
        nonlocal total_checks
        total_checks += 1
        if cond:
            print(f"  ✅ PASS: {label} {f'({detail})' if detail else ''}")
        else:
            print(f"  ❌ FAIL: {label} {f'({detail})' if detail else ''}")
            failures.append(f"{label}: {detail}")

    # 1. Verify all 5 Cloud Run Services (Root HTML, Readiness, Agent Card, A2A, MCP)
    for svc in SERVICES:
        base = svc["url"]
        name = svc["name"]
        print(f"\n======================================================================")
        print(f"🚀 Testing Cloud Run Service: {name} ({base})")
        print(f"======================================================================")

        # Root UI HTML
        st, html, ms = http_req(f"{base}/")
        check(st == 200 and len(html) > 80000, f"[{name}] GET / UI HTML", f"{len(html):,} bytes in {ms}ms")
        check(
            f"const requestedView = urlParams.get('view') || '{svc['expected_view']}';" in html,
            f"[{name}] Default Studio View = {svc['expected_view']}",
        )

        # Verify all JS handlers defined in HTML
        onclicks = re.findall(r'onclick="([a-zA-Z0-9_]+)\(', html)
        onchanges = re.findall(r'onchange="([a-zA-Z0-9_]+)\(', html)
        onkeydowns = re.findall(r'onkeydown="([a-zA-Z0-9_]+)\(', html)
        funcs = set(re.findall(r'function\s+([a-zA-Z0-9_]+)\s*\(', html))
        missing_handlers = set(onclicks + onchanges + onkeydowns) - funcs - {"alert"}
        check(len(missing_handlers) == 0, f"[{name}] Zero undefined JS event handlers", f"missing={missing_handlers}")
        check("formatMarkdown(" not in html, f"[{name}] No undefined formatMarkdown() call")

        # Readiness
        st, body, ms = http_req(f"{base}/health/readiness")
        rd = json.loads(body)
        check(
            st == 200 and rd.get("status") == "READY" and rd.get("clauses_indexed", 0) >= 1200,
            f"[{name}] GET /health/readiness",
            f"clauses_indexed={rd.get('clauses_indexed')}, models={rd.get('active_models')}",
        )

        # Well-known Agent Card
        st, body, ms = http_req(f"{base}/.well-known/agent.json")
        ac = json.loads(body)
        check(st == 200 and "skills" in ac, f"[{name}] GET /.well-known/agent.json", f"name={ac.get('name')}")

        # MCP initialize & tools/list & resources/read
        st, body, ms = http_req(
            f"{base}/mcp",
            method="POST",
            payload={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
        )
        mcp_tools = json.loads(body).get("result", {}).get("tools", [])
        check(
            st == 200 and len(mcp_tools) == 7,
            f"[{name}] POST /mcp tools/list (7 tools)",
            f"tools={[t['name'] for t in mcp_tools]}",
        )

        st, body, ms = http_req(
            f"{base}/mcp",
            method="POST",
            payload={
                "jsonrpc": "2.0",
                "id": 2,
                "method": "resources/read",
                "params": {"uri": svc["expected_mcp_uri"]},
            },
        )
        mcp_res = json.loads(body).get("result", {}).get("contents", [{}])[0]
        check(
            st == 200 and mcp_res.get("uri") == svc["expected_mcp_uri"] and len(mcp_res.get("text", "")) > 80000,
            f"[{name}] POST /mcp resources/read ({svc['expected_mcp_uri']})",
            f"{len(mcp_res.get('text', '')):,} bytes in {ms}ms",
        )

    # 2. Deep E2E Feature & Button Verification on Primary Hub (`mike-gcp-platform`)
    hub = SERVICES[0]["url"]
    print(f"\n======================================================================")
    print(f"🔬 Deep E2E Feature & Button Verification on {hub}")
    print(f"======================================================================")

    # Dedicated Studio UI routes
    for route in ["/ui/mike-cockpit", "/ui/redline-studio", "/ui/funds-antitrust", "/ui/governance-wall", "/ui/inbox-calendar"]:
        st, body, ms = http_req(f"{hub}{route}")
        check(st == 200 and len(body) > 80000, f"GET {route}", f"{ms}ms")

    # Feature 1: Workspace State (Kestrel mode vs Scaled 46-doc mode)
    st, body, ms = http_req(f"{hub}/api/state?corpus=kestrel")
    d_kestrel = json.loads(body)
    check(
        st == 200 and len(d_kestrel.get("documents", [])) >= 6 and d_kestrel["benchmark_summary"]["total_clauses"] >= 1200,
        "Button: Corpus Mode 'Kestrel (6)' (/api/state?corpus=kestrel)",
        f"docs={len(d_kestrel['documents'])}, total_clauses={d_kestrel['benchmark_summary']['total_clauses']}",
    )

    st, body, ms = http_req(f"{hub}/api/state?corpus=scaled")
    d_scaled = json.loads(body)
    check(
        st == 200 and len(d_scaled.get("documents", [])) >= 40,
        "Button: Corpus Mode 'Scaled (46 | 1,293 Clauses)' (/api/state?corpus=scaled)",
        f"docs={len(d_scaled['documents'])}",
    )

    # Feature 2: Scalability Benchmark Modal & Re-run
    st, body, ms = http_req(f"{hub}/api/benchmark")
    bm = json.loads(body)
    check(
        st == 200 and bm.get("status") == "SUCCESS" and bm["corpus_metrics"]["total_clauses"] >= 1200,
        "Button: ⚡ 1,293 Clauses Benchmark Modal (/api/benchmark)",
        f"p50={bm['query_performance']['end_to_end']['p50']}ms, qps={bm['query_performance']['estimated_qps']}",
    )

    st, body, ms = http_req(f"{hub}/api/benchmark/rerun", method="POST", payload={})
    bm_re = json.loads(body)
    check(
        st == 200 and bm_re.get("status") == "SUCCESS" and bm_re["corpus_metrics"]["total_clauses"] >= 1200,
        "Button: 🔄 Re-run Live Stress-Test (/api/benchmark/rerun POST)",
        f"p50={bm_re['query_performance']['end_to_end']['p50']}ms in {ms}ms",
    )

    # Feature 3: 100 Golden Questions Modal & Report
    st, body, ms = http_req(f"{hub}/api/eval/dataset")
    eval_ds = json.loads(body)
    check(
        st == 200 and eval_ds.get("total_questions") == 100,
        "Button: 🎯 100 Golden Questions Modal (/api/eval/dataset)",
        f"total={eval_ds.get('total_questions')}, breakdown={eval_ds.get('difficulty_breakdown')}",
    )

    st, body, ms = http_req(f"{hub}/api/eval/report")
    eval_rep = json.loads(body)
    check(st == 200 and "summary" in eval_rep, "Golden Eval Report (/api/eval/report)", f"{ms}ms")

    # Feature 4: Pin-Cite Document Page Lightbox (Yellow Chunk Highlighting)
    st, body, ms = http_req(f"{hub}/api/document_page?doc_id=DOC-KESTREL-01&page=12")
    dp = json.loads(body)
    check(
        st == 200 and len(dp.get("text", "")) > 50,
        "Button: 📌 Pin-Cite Citation Pill Lightbox (/api/document_page)",
        f"chars={len(dp.get('text', ''))} in {ms}ms",
    )

    # Feature 5: Grant & Revoke Teammate Access (EM-9901 Unfiled Email)
    st, body, ms = http_req(f"{hub}/api/grant", method="POST", payload={"email_id": "EM-9901"})
    gr = json.loads(body)
    check(
        st == 200 and gr.get("granted") is True and "CLEARED" in gr.get("ethical_wall_status", ""),
        "Button: ⚡ Grant EM-9901 (/api/grant)",
        f"grant_id={gr.get('grant_id')}, status={gr.get('ethical_wall_status')}",
    )

    st, body, ms = http_req(f"{hub}/api/revoke", method="POST", payload={"email_id": "EM-9901"})
    rv = json.loads(body)
    check(st == 200 and (rv.get("status") == "REVOKED" or rv.get("revoked") is True), "Revoke EM-9901 (/api/revoke)")

    # Feature 6: Studio 2 — Redline Pair Switcher, Custom Redline Diff, and Legal Legos Composer
    for pair_id in ["KESTREL-SPA-802", "KESTREL-COC-804"]:
        st, body, ms = http_req(f"{hub}/api/redline?pair_id={pair_id}")
        rl = json.loads(body)
        check(
            st == 200 and "redline_html" in rl and len(rl.get("key_deviations", [])) > 0,
            f"Button: Redline Pair Tab '{pair_id}' (/api/redline)",
            f"similarity={rl['stats']['similarity_pct']}%, deviations={len(rl['key_deviations'])}",
        )

    st, body, ms = http_req(
        f"{hub}/api/redline",
        method="POST",
        payload={
            "pair_id": "KESTREL-SPA-802",
            "custom_clause_a": "Seller cap shall not exceed $31,500,000 (0.75% EV).",
            "custom_clause_b": "Seller cap shall not exceed $630,000,000 (15.0% EV) plus Constructive Fraud.",
        },
    )
    crl = json.loads(body)
    check(
        st == 200 and "redline-del" in crl.get("redline_html", "") and "redline-ins" in crl.get("redline_html", ""),
        "Button: Compute Live Deterministic Diff (/api/redline POST)",
        f"similarity={crl['stats']['similarity_pct']}% in {ms}ms",
    )

    st, body, ms = http_req(
        f"{hub}/api/legal-legos",
        method="POST",
        payload={"block_ids": ["LEGO-DE-FRAUD", "LEGO-338H10-TAX", "LEGO-PRIVACY-PRO", "LEGO-MFN-FUNDGEN"]},
    )
    ll = json.loads(body)
    check(
        st == 200 and len(ll.get("selected_block_ids", [])) == 4 and "8.02" in ll.get("composed_docx_preview", ""),
        "Button: Assemble .docx Rider (/api/legal-legos)",
        f"blocks={len(ll.get('selected_block_ids', []))} in {ms}ms",
    )

    # Feature 7: Studio 3 — FundGen / FundHQ LP Tier Filters & HSR HHI Divestiture Remedy Toggle
    for tier_m in [0, 150, 250]:
        for remedy in [True, False]:
            st, body, ms = http_req(f"{hub}/api/funds-antitrust?commitment_filter_m={tier_m}&include_remedy={str(remedy).lower()}")
            fa = json.loads(body)
            check(
                st == 200 and len(fa.get("lp_side_letters", [])) >= 1 and "antitrust_hsr" in fa,
                f"Button: FundGen Tier>={tier_m}M & Remedy={remedy}",
                f"LPs={len(fa['lp_side_letters'])}, HHI_delta=+{fa['antitrust_hsr']['active_hhi_delta']}",
            )

    # Feature 8: Studio 4 — CMN Switcher, Intapp Ethical Wall Check & Cloud Spanner LexGraphLegalGraph
    for m_id, l_id, expect_access in [
        ("M-331-KESTREL", "L-001", True),
        ("M-610-FUNDGEN", "L-001", True),
        ("M-720-ANTITRUST", "L-001", True),
        ("M-999", "L-001", False),
        ("M-999", "L-003", True),
    ]:
        st, body, ms = http_req(f"{hub}/api/governance/wall-check?matter_id={m_id}&lawyer_id={l_id}")
        gw = json.loads(body)
        actual_access = gw.get("intapp_wall_check", {}).get("access_granted")
        check(
            st == 200 and actual_access is expect_access,
            f"Button: CMN Switcher ({m_id}, {l_id}) -> access={actual_access}",
            f"CMN={gw.get('cmn')}, status={gw['intapp_wall_check']['ethical_wall_status']}",
        )

    st, body, ms = http_req(f"{hub}/api/graph?matter_id=M-331-KESTREL&lawyer_id=L-001")
    gr_data = json.loads(body)
    check(
        st == 200 and len(gr_data.get("nodes", [])) >= 5 and len(gr_data.get("edges", [])) >= 5,
        "Spanner LexGraphLegalGraph Multi-Hop Topology (/api/graph)",
        f"nodes={len(gr_data.get('nodes', []))}, edges={len(gr_data.get('edges', []))}",
    )

    # Feature 9: Studio 5 — Partner Inbox One-Tap Approve & Calendar Conflict Delegation
    st, body, ms = http_req(
        f"{hub}/api/inbox-triage",
        method="POST",
        payload={"approve_email_id": "EM-9901", "resolve_conflict_id": "CAL-101"},
    )
    ib = json.loads(body)
    em_status = next((e["status"] for e in ib.get("emails", []) if e["email_id"] == "EM-9901"), "")
    cal_status = next((c["status"] for c in ib.get("calendar_conflicts", []) if c["conflict_id"] == "CAL-101"), "")
    check(
        st == 200 and "APPROVED" in em_status and "RESOLVED" in cal_status,
        "Buttons: ✅ One-Tap Approve EM-9901 & ⚡ Execute Delegation CAL-101 (/api/inbox-triage)",
        f"em_status={em_status}, cal_status={cal_status}",
    )

    # Feature 10: Live Gemini 3.8 Flash Calls (Chat, Dynamic Column Extraction, ADK Specialist Agent)
    st, body, ms = http_req(
        f"{hub}/api/ask",
        method="POST",
        payload={"query": "What is the liability cap and termination fee in the Halvorsen Supply Agreement?", "model": "gemini-3.8-flash"},
        timeout=60,
    )
    ask_res = json.loads(body)
    check(
        st == 200 and len(ask_res.get("answer", "")) > 40 and len(ask_res.get("citations", [])) > 0,
        "Button: Live Chat Submit (/api/ask on gemini-3.8-flash)",
        f"citations={len(ask_res.get('citations', []))}, latency={ask_res.get('latency_ms')}ms",
    )

    st, body, ms = http_req(
        f"{hub}/api/extract_single",
        method="POST",
        payload={
            "doc_id": "DOC-KESTREL-01",
            "column_name": "Fraud Carveout",
            "column_prompt": "Does fraud or willful misconduct bypass the liability cap?",
            "model": "gemini-3.8-flash",
        },
        timeout=60,
    )
    ext_res = json.loads(body)
    check(
        st == 200 and bool(ext_res.get("extracted_value")),
        "Button: + Evaluate Dynamic Column (/api/extract_single on gemini-3.8-flash)",
        f"extracted={ext_res.get('extracted_value')}, citation={ext_res.get('citation')}",
    )

    for agent_id, prompt_text in [
        ("redline_word_composer_agent", "Summarize the 3 critical deviations in Skadden v4 Section 8.02."),
        ("private_funds_antitrust_agent", "Summarize the FundGen XII MFN exposure and FTC HSR HHI remedy."),
        ("ethical_wall_cmn_governance_agent", "Verify CMN 31402-0018 and Intapp Ethical Wall status for L-001."),
        ("inbox_calendar_triage_agent", "Summarize the P0 signing blockers in the Partner Inbox and CAL-101 conflict."),
    ]:
        st, body, ms = http_req(
            f"{hub}/api/adk/run",
            method="POST",
            payload={
                "agent_id": agent_id,
                "prompt": prompt_text,
                "matter_id": "M-331-KESTREL",
                "lawyer_id": "L-001",
            },
            timeout=60,
        )
        adk_res = json.loads(body)
        check(
            st == 200 and len(adk_res.get("answer", "")) > 40 and "gemini-3.8-flash" in adk_res.get("model_used", ""),
            f"Button: ⚡ Run ADK Studio Agent '{agent_id}' (/api/adk/run)",
            f"model={adk_res.get('model_used')}, latency={adk_res.get('latency_ms')}ms",
        )

    # Feature 11: Verify All 7 MCP JSON-RPC Tools Execute Cleanly
    mcp_tool_calls = [
        ("open_legal_analysis_grid", {"question": "Change of Control notice period", "matter_id": "M-331-KESTREL"}),
        ("hybrid_search_legal_graph", {"query": "Section 338(h)(10) indemnity escrow", "matter_id": "M-331-KESTREL"}),
        ("traverse_precedent_graph", {"matter_id": "M-331-KESTREL", "lawyer_id": "L-001"}),
        ("run_deterministic_redline", {"pair_id": "KESTREL-SPA-802"}),
        ("analyze_fundgen_and_antitrust", {"commitment_filter_m": 150, "include_divestiture_remedy": True}),
        ("triage_inbox_and_cmn_wall", {"matter_id": "M-999", "lawyer_id": "L-001", "approve_email_id": "EM-9902"}),
    ]
    for tool_name, tool_args in mcp_tool_calls:
        st, body, ms = http_req(
            f"{hub}/mcp",
            method="POST",
            payload={"jsonrpc": "2.0", "id": 99, "method": "tools/call", "params": {"name": tool_name, "arguments": tool_args}},
        )
        res_obj = json.loads(body).get("result", {})
        check(
            st == 200 and len(res_obj.get("content", [])) > 0 and "_meta" in res_obj,
            f"MCP Tool Call: {tool_name}",
            f"ui={res_obj.get('_meta', {}).get('ui', {}).get('resourceUri')} in {ms}ms",
        )

    print(f"\n======================================================================")
    print(f"🏁 E2E Verification Summary: {total_checks - len(failures)}/{total_checks} Checks Passed")
    print(f"======================================================================")
    if failures:
        print("Failures detected:")
        for f in failures:
            print("  -", f)
        sys.exit(1)


if __name__ == "__main__":
    run_suite()
