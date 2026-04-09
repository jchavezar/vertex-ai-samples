"""
chronoshot mcp_bench — 100-question MCP benchmark.

Tests direct SharePoint → Gemini pipeline vs Discovery Engine StreamAssist:

  Phase 1 (Setup — one-time, amortized):
    Auth       MSAL client_credentials → Graph API token
    Download   Graph API → SharePoint documents
    Parse      markitdown → text extraction

  Phase 2 (Per-question):
    LLM        Gemini 2.0 Flash → answer generation

Usage:
    uv run python mcp_bench.py               # run all 100
    uv run python mcp_bench.py --section 1   # run one section
    uv run python mcp_bench.py --resume      # skip already-done questions
    uv run python mcp_bench.py --count 10    # run first N questions
"""

import time, json, math, argparse
from pathlib import Path
from datetime import datetime

from bench import QUESTIONS, evaluate, percentile
from sharepoint_mcp.auth import get_graph_token
from sharepoint_mcp.graph import GraphClient
from sharepoint_mcp.parser import parse_all
from sharepoint_mcp.rag import create_qa_chain

RESULTS_FILE = Path("/tmp/chronoshot_mcp_bench.json")


def main():
    parser = argparse.ArgumentParser(description="MCP benchmark: SharePoint → Gemini pipeline")
    parser.add_argument("--section", type=int, choices=list(range(1, 9)))
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--count", type=int, help="Run first N questions only")
    args = parser.parse_args()

    section_map = {
        1: range(1, 11), 2: range(11, 21), 3: range(21, 31),
        4: range(31, 41), 5: range(41, 53), 6: range(53, 73),
        7: range(73, 87), 8: range(87, 101),
    }

    targets = list(QUESTIONS)
    if args.section:
        rng = section_map[args.section]
        targets = [(n, q, kw) for n, q, kw in QUESTIONS if n in rng]

    existing = {}
    if args.resume and RESULTS_FILE.exists():
        for r in json.loads(RESULTS_FILE.read_text()):
            existing[r["qnum"]] = r
        print(f"  Resuming: {len(existing)} questions already done")
        targets = [(n, q, kw) for n, q, kw in targets if n not in existing]

    if args.count:
        targets = targets[:args.count]

    print(f"\n  chronoshot mcp_bench ⚡  {len(targets)} questions (MCP pipeline)")
    print(f"  Pipeline: SharePoint → markitdown → Gemini 2.0 Flash\n")

    # ── Phase 1: Setup (one-time) ────────────────────────────────────────────

    # Auth
    print("  [Setup] Authenticating with MSAL...", end=" ", flush=True)
    t0 = time.perf_counter()
    try:
        token = get_graph_token()
        auth_ms = int((time.perf_counter() - t0) * 1000)
        print(f"✓ {auth_ms}ms")
    except Exception as e:
        auth_ms = int((time.perf_counter() - t0) * 1000)
        token = ""
        print(f"⚠ {auth_ms}ms (using cache: {str(e)[:50]})")

    # Download
    print("  [Setup] Loading SharePoint documents...", end=" ", flush=True)
    t0 = time.perf_counter()
    client = GraphClient(token)
    files = client.download_all()
    download_ms = int((time.perf_counter() - t0) * 1000)
    print(f"✓ {download_ms}ms ({len(files)} docs, {sum(len(v) for v in files.values()) / 1024:.0f} KB)")

    # Parse
    print("  [Setup] Parsing documents with markitdown...", end=" ", flush=True)
    t0 = time.perf_counter()
    documents = parse_all(files)
    parse_ms = int((time.perf_counter() - t0) * 1000)
    total_chars = sum(len(v) for v in documents.values())
    print(f"✓ {parse_ms}ms ({total_chars:,} chars)")

    setup_ms = auth_ms + download_ms + parse_ms
    n_questions = len(targets) + len(existing)
    amortized_auth = auth_ms // n_questions if n_questions else auth_ms
    amortized_download = download_ms // n_questions if n_questions else download_ms
    amortized_parse = parse_ms // n_questions if n_questions else parse_ms

    print(f"\n  Setup total: {setup_ms:,}ms  (amortized per-question: {setup_ms // n_questions if n_questions else setup_ms}ms)")

    # Create QA chain
    print("  [Setup] Initializing Gemini 2.0 Flash...", end=" ", flush=True)
    t0 = time.perf_counter()
    qa = create_qa_chain(documents)
    init_ms = int((time.perf_counter() - t0) * 1000)
    print(f"✓ {init_ms}ms\n")

    # ── Phase 2: Per-question benchmark ──────────────────────────────────────

    all_results = list(existing.values())

    for i, (qnum, question, keywords) in enumerate(targets, 1):
        print(f"  [{i}/{len(targets)}] Q{qnum}: {question[:50]}...", end=" ", flush=True)

        t0 = time.perf_counter()
        try:
            answer_text = qa(question)
            llm_ms = int((time.perf_counter() - t0) * 1000)
        except Exception as e:
            llm_ms = int((time.perf_counter() - t0) * 1000)
            result = {
                "qnum": qnum,
                "question": question,
                "keywords": keywords,
                "error": str(e)[:200],
                "pass": False,
                "total_ms": llm_ms + amortized_auth + amortized_download + amortized_parse,
                "phases": {
                    "auth_ms": amortized_auth,
                    "download_ms": amortized_download,
                    "parse_ms": amortized_parse,
                    "llm_ms": llm_ms,
                },
                "timestamp": datetime.now().isoformat(),
            }
            all_results.append(result)
            RESULTS_FILE.write_text(json.dumps(all_results, indent=2))
            print(f"ERROR ({str(e)[:40]})")
            continue

        passed = evaluate(answer_text, keywords)
        total_q_ms = amortized_auth + amortized_download + amortized_parse + llm_ms

        result = {
            "qnum": qnum,
            "question": question,
            "keywords": keywords,
            "answer": answer_text,
            "pass": passed,
            "total_ms": total_q_ms,
            "phases": {
                "auth_ms": amortized_auth,
                "download_ms": amortized_download,
                "parse_ms": amortized_parse,
                "llm_ms": llm_ms,
            },
            "timestamp": datetime.now().isoformat(),
        }

        all_results.append(result)
        RESULTS_FILE.write_text(json.dumps(all_results, indent=2))

        status = "✓" if passed else "✗"
        print(f"{status} {total_q_ms:,}ms  [LLM:{llm_ms}ms]")

        time.sleep(0.2)

    # ── Summary ──────────────────────────────────────────────────────────────

    print("\n" + "=" * 80)
    print(f"  CHRONOSHOT MCP BENCH — {len(all_results)} questions | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 80)

    valid = [r for r in all_results if "error" not in r]
    passed_count = sum(1 for r in all_results if r.get("pass"))
    print(f"\n  Accuracy: {passed_count}/{len(all_results)} ({passed_count / len(all_results) * 100:.0f}%)")

    if valid:
        latencies = [r["total_ms"] for r in valid]
        llm_times = [r["phases"]["llm_ms"] for r in valid]
        print(f"  Total:    P50={int(percentile(latencies, 50)):,}ms  Mean={int(sum(latencies) / len(latencies)):,}ms  Min={min(latencies):,}ms  Max={max(latencies):,}ms")
        print(f"  LLM only: P50={int(percentile(llm_times, 50)):,}ms  Mean={int(sum(llm_times) / len(llm_times)):,}ms  Min={min(llm_times):,}ms  Max={max(llm_times):,}ms")

    print(f"\n  Setup costs (one-time):")
    print(f"    Auth:     {auth_ms:,}ms")
    print(f"    Download: {download_ms:,}ms")
    print(f"    Parse:    {parse_ms:,}ms")
    print(f"    Total:    {setup_ms:,}ms")

    # Section breakdown
    sections = {
        "Contract Basics (1-10)":       range(1, 11),
        "Financial Terms (11-20)":      range(11, 21),
        "SLA + Term (21-30)":           range(21, 31),
        "Financial Performance (31-40)":range(31, 41),
        "M&A Starlight (41-52)":        range(41, 53),
        "Cybersecurity (53-72)":        range(53, 73),
        "Paraphrased (73-86)":          range(73, 87),
        "Number Recall (87-93)":        range(87, 94),
        "Synthesis (94-100)":           range(94, 101),
    }
    print(f"\n  {'Section':<30} {'Pass':>6} {'Fail':>6} {'Acc':>7}")
    print(f"  {'─' * 30} {'─' * 6} {'─' * 6} {'─' * 7}")
    for name, rng in sections.items():
        sec = [r for r in all_results if r["qnum"] in rng]
        if not sec:
            continue
        sp = sum(1 for r in sec if r.get("pass"))
        sf = len(sec) - sp
        acc = sp / len(sec) * 100
        print(f"  {name:<30} {sp:>6} {sf:>6} {acc:>6.0f}%")

    print(f"\n  Full results → {RESULTS_FILE}")


if __name__ == "__main__":
    main()
