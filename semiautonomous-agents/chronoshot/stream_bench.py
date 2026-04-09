"""
chronoshot stream_bench — 100-question benchmark with REAL per-chunk event timing.

Streams the StreamAssist response to capture actual wall-clock timing
for each chunk arrival, then maps chunks to pipeline events:

  Request → First byte           Network + server accept
  First thought → Last thought   LLM reasoning + SharePoint retrieval
  Last thought → First answer    Answer generation
  First answer → Last answer     Answer streaming
  Last answer → Final metadata   Grounding + citations

Usage:
    uv run python stream_bench.py               # run all 100
    uv run python stream_bench.py --section 1   # run one section
    uv run python stream_bench.py --resume      # skip already-done questions
    uv run python stream_bench.py --count 10    # run first N questions
"""

import os, sys, json, time, base64, math, argparse, requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / "sharepoint_wif_portal" / ".env")

PROJECT_NUMBER  = os.environ["PROJECT_NUMBER"]
ENGINE_ID       = os.environ["ENGINE_ID"]
WIF_POOL_ID     = os.environ["WIF_POOL_ID"]
WIF_PROVIDER_ID = os.environ["WIF_PROVIDER_ID"]
TENANT_ID       = os.environ["TENANT_ID"]
CLIENT_ID       = os.environ["OAUTH_CLIENT_ID"]
CLIENT_SECRET   = os.environ["OAUTH_CLIENT_SECRET"]

BASE_URL = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/engines/{ENGINE_ID}"
STREAM_ASSIST_URL = f"{BASE_URL}/assistants/default_assistant:streamAssist"
RESULTS_FILE = Path("/tmp/chronoshot_stream_bench.json")

# Import questions from bench.py
from bench import QUESTIONS, evaluate, percentile

# ── Auth ──────────────────────────────────────────────────────────────────────

def get_tokens() -> str:
    user_tok_path = Path("/tmp/entra_token.txt")
    if user_tok_path.exists():
        raw = user_tok_path.read_text().strip()
        try:
            payload = raw.split(".")[1] + "=="
            claims = json.loads(base64.urlsafe_b64decode(payload))
            if claims.get("exp", 0) > time.time() + 60:
                print(f"  Token: user session ({claims.get('name','?')}) — SharePoint ACLs active")
                return _exchange(raw)
        except Exception:
            pass
    print("  Token: client_credentials (app-level — no SharePoint doc access)")
    resp = requests.post(
        f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token",
        data={"grant_type": "client_credentials", "client_id": CLIENT_ID,
              "client_secret": CLIENT_SECRET, "scope": f"api://{CLIENT_ID}/.default"},
        timeout=10,
    )
    resp.raise_for_status()
    return _exchange(resp.json()["access_token"])


def _exchange(entra_jwt: str) -> str:
    resp = requests.post("https://sts.googleapis.com/v1/token", json={
        "audience": f"//iam.googleapis.com/locations/global/workforcePools/{WIF_POOL_ID}/providers/{WIF_PROVIDER_ID}",
        "grantType": "urn:ietf:params:oauth:grant-type:token-exchange",
        "requestedTokenType": "urn:ietf:params:oauth:token-type:access_token",
        "scope": "https://www.googleapis.com/auth/cloud-platform",
        "subjectToken": entra_jwt,
        "subjectTokenType": "urn:ietf:params:oauth:token-type:jwt",
    }, timeout=10)
    resp.raise_for_status()
    return resp.json()["access_token"]


# ── Streaming StreamAssist call ──────────────────────────────────────────────

def stream_call(question: str, gcp_token: str) -> dict:
    """Call StreamAssist with streaming to capture real per-chunk timing."""
    t0 = time.perf_counter()

    # Create session
    sess_resp = requests.post(f"{BASE_URL}/sessions",
        headers={"Authorization": f"Bearer {gcp_token}", "Content-Type": "application/json"},
        json={"displayName": question[:40]}, timeout=10)
    session_id = sess_resp.json().get("name") if sess_resp.ok else None

    payload = {"query": {"text": question}}
    if session_id:
        payload["session"] = session_id

    # Stream the response
    t_req = time.perf_counter()
    try:
        resp = requests.post(STREAM_ASSIST_URL,
            headers={"Authorization": f"Bearer {gcp_token}", "Content-Type": "application/json"},
            json=payload, timeout=90, stream=True)
    except Exception as e:
        return {"error": str(e)[:200], "total_ms": int((time.perf_counter() - t0) * 1000)}

    if not resp.ok:
        return {"error": f"{resp.status_code}: {resp.text[:200]}", "total_ms": int((time.perf_counter() - t0) * 1000)}

    # Collect chunks with timestamps
    chunks = []
    buffer = ""
    try:
      for raw_chunk in resp.iter_content(chunk_size=None, decode_unicode=True):
        t_now = time.perf_counter()
        buffer += raw_chunk
        try:
            parsed = json.loads("[" + buffer.rstrip().rstrip("]").lstrip("[") + "]")
            while len(parsed) > len(chunks):
                idx = len(chunks)
                chunks.append({
                    "at_ms": int((t_now - t0) * 1000),
                    "data": parsed[idx],
                })
        except json.JSONDecodeError:
            pass
    except Exception as e:
      t_done = time.perf_counter()
      if not chunks:
          return {"error": f"stream: {str(e)[:150]}", "total_ms": int((t_done - t0) * 1000)}

    t_done = time.perf_counter()
    total_ms = int((t_done - t0) * 1000)

    if not chunks:
        return {"error": "no chunks received", "total_ms": total_ms}

    # Classify each chunk
    classified = []
    for c in chunks:
        answer = c["data"].get("answer", {})
        state = answer.get("state", "")
        replies = answer.get("replies", [])
        text = ""
        is_thought = False
        for r in replies:
            gc = r.get("groundedContent", {}).get("content", {})
            text = gc.get("text", "")
            is_thought = gc.get("thought", False)

        if state == "SUCCEEDED":
            ctype = "final"
        elif is_thought:
            ctype = "thought"
        elif text:
            ctype = "answer"
        else:
            ctype = "metadata"

        classified.append({
            "at_ms": c["at_ms"],
            "type": ctype,
            "text": text[:100] if text else "",
        })

    # Build event breakdown
    thoughts = [c for c in classified if c["type"] == "thought"]
    answers  = [c for c in classified if c["type"] == "answer"]
    finals   = [c for c in classified if c["type"] == "final"]

    first_byte_ms = classified[0]["at_ms"] if classified else 0

    events = []

    # Event 1: Request → StreamAssist logged
    events.append({
        "event": "Request → StreamAssist logged",
        "duration_ms": first_byte_ms,
        "description": "Network + server accept",
    })

    # Event 2: LLM reasoning (thought chunks)
    if thoughts:
        reasoning_ms = thoughts[-1]["at_ms"] - thoughts[0]["at_ms"]
        events.append({
            "event": "StreamAssist → Search",
            "duration_ms": reasoning_ms,
            "description": "LLM reasoning + SharePoint retrieval",
        })

    # Event 3: Search → Answer (gap between last thought and first answer)
    if thoughts and answers:
        search_ms = answers[0]["at_ms"] - thoughts[-1]["at_ms"]
        events.append({
            "event": "Search → AcquireAccessToken",
            "duration_ms": search_ms,
            "description": "SharePoint connector auth + query",
        })

    # Event 4: Answer streaming
    if answers:
        stream_ms = answers[-1]["at_ms"] - answers[0]["at_ms"] if len(answers) > 1 else 0
        events.append({
            "event": "AcquireAccessToken → Answer",
            "duration_ms": stream_ms,
            "description": "LLM generates + streams answer",
        })

    # Event 5: Final metadata
    if finals and answers:
        final_ms = finals[0]["at_ms"] - answers[-1]["at_ms"]
        events.append({
            "event": "Answer → Final metadata",
            "duration_ms": final_ms,
            "description": "Grounding metadata + citations",
        })
    elif finals and thoughts:
        final_ms = finals[0]["at_ms"] - thoughts[-1]["at_ms"]
        events.append({
            "event": "Answer → Final metadata",
            "duration_ms": final_ms,
            "description": "Grounding metadata + citations",
        })

    # Extract answer text
    answer_text = " ".join(c["text"] for c in classified if c["type"] == "answer")

    # Extract sources
    sources = []
    for c in chunks:
        gm = c["data"].get("answer", {}).get("groundingMetadata", {})
        for gc in gm.get("groundingChunks", []):
            ctx = gc.get("retrievedContext", {})
            t = ctx.get("title", "")
            if t and t not in [s.get("title") for s in sources]:
                sources.append({"title": t})
        # Also check textGroundingMetadata in replies
        for r in c["data"].get("answer", {}).get("replies", []):
            tgm = r.get("groundedContent", {}).get("textGroundingMetadata", {})
            for ref in tgm.get("references", []):
                dm = ref.get("documentMetadata", {})
                t = dm.get("title", "")
                if t and t not in [s.get("title") for s in sources]:
                    sources.append({"title": t})

    return {
        "answer": answer_text,
        "sources": sources,
        "total_ms": total_ms,
        "events": events,
        "chunks": classified,
        "timestamp": datetime.now().isoformat(),
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--section",  type=int, choices=list(range(1, 9)))
    parser.add_argument("--resume",   action="store_true")
    parser.add_argument("--count",    type=int, help="Run first N questions only")
    args = parser.parse_args()

    section_map = {
        1: range(1, 11), 2: range(11, 21), 3: range(21, 31),
        4: range(31, 41), 5: range(41, 53), 6: range(53, 73),
        7: range(73, 87), 8: range(87, 101),
    }

    targets = QUESTIONS
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

    print(f"\n  chronoshot stream_bench ⚡  {len(targets)} questions (streaming mode)")
    print(f"  Engine: {ENGINE_ID} | Project: {PROJECT_NUMBER}\n")

    gcp_token = get_tokens()
    print()

    all_results = list(existing.values())

    for i, (qnum, question, keywords) in enumerate(targets, 1):
        print(f"  [{i}/{len(targets)}] Q{qnum}: {question[:50]}...", end=" ", flush=True)

        result = stream_call(question, gcp_token)
        result["qnum"] = qnum
        result["question"] = question
        result["keywords"] = keywords

        if "error" in result:
            result["pass"] = False
            print(f"ERROR ({result['error'][:40]})")
        else:
            passed = evaluate(result["answer"], keywords)
            result["pass"] = passed
            status = "✓" if passed else "✗"
            # Show event breakdown inline
            evts = result.get("events", [])
            evt_str = " | ".join(f"{e['event'].split('→')[-1].strip()[:12]}:{e['duration_ms']}ms" for e in evts)
            print(f"{status} {result['total_ms']:,}ms  [{evt_str}]")

        all_results.append(result)
        RESULTS_FILE.write_text(json.dumps(all_results, indent=2))
        time.sleep(0.3)

    # Summary
    print("\n" + "=" * 80)
    print(f"  CHRONOSHOT STREAM BENCH — {len(all_results)} questions | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 80)

    valid = [r for r in all_results if "error" not in r]
    passed = sum(1 for r in all_results if r.get("pass"))
    print(f"\n  Accuracy: {passed}/{len(all_results)} ({passed/len(all_results)*100:.0f}%)")

    if valid:
        latencies = [r["total_ms"] for r in valid]
        print(f"  Latency:  P50={int(percentile(latencies,50)):,}ms  Mean={int(sum(latencies)/len(latencies)):,}ms  Min={min(latencies):,}ms  Max={max(latencies):,}ms")

    # Aggregate events
    event_names = ["Request → StreamAssist logged", "StreamAssist → Search",
                   "Search → AcquireAccessToken", "AcquireAccessToken → Answer",
                   "Answer → Final metadata"]
    event_data = {name: [] for name in event_names}
    for r in valid:
        for e in r.get("events", []):
            if e["event"] in event_data:
                event_data[e["event"]].append(e["duration_ms"])

    print(f"\n  {'Event':<35} {'Min':>8} {'P50':>8} {'Mean':>8} {'P90':>8} {'Max':>8}")
    print(f"  {'-'*35} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")
    for name in event_names:
        vals = event_data[name]
        if vals:
            print(f"  {name:<35} {min(vals):>7}ms {int(percentile(vals,50)):>7}ms {int(sum(vals)/len(vals)):>7}ms {int(percentile(vals,90)):>7}ms {max(vals):>7}ms")

    print(f"\n  Full results → {RESULTS_FILE}")


if __name__ == "__main__":
    main()
