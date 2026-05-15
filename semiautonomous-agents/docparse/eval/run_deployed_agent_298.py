"""Run the deployed GA agent on all 298 questions (216 original + 82 new)."""
import json, time, sys
from pathlib import Path
import vertexai
from vertexai import agent_engines

vertexai.init(project="vtxdemos", location="us-central1")
agent = agent_engines.get("projects/254356041555/locations/us-central1/reasoningEngines/8912734163484803072")

questions = json.loads(Path("~/docparse-eval-private/questions_full.json").expanduser().read_text())
print(f"Testing deployed GA agent on {len(questions)} questions...", file=sys.stderr)

results = []
for i, q in enumerate(questions, 1):
    session = agent.create_session(user_id=f"eval-{i}")
    sid = session.get('id') if isinstance(session, dict) else session.id
    
    t0 = time.time()
    answer = ""
    try:
        for event in agent.stream_query(user_id=f"eval-{i}", session_id=sid, message=q["q"]):
            c = event.get('content', {}) if isinstance(event, dict) else {}
            for p in c.get('parts', []):
                if isinstance(p, dict) and 'text' in p:
                    answer += p['text']
        elapsed = time.time() - t0
        results.append({"id": q["id"], "ok": True, "answer": answer, "elapsed_s": round(elapsed, 1)})
    except Exception as e:
        elapsed = time.time() - t0
        results.append({"id": q["id"], "ok": False, "error": f"{type(e).__name__}: {str(e)[:300]}", "elapsed_s": round(elapsed, 1)})
    
    if i % 20 == 0:
        print(f"  {i}/{len(questions)} complete...", file=sys.stderr)

Path("runs/deployed_ga_agent_298.json").write_text(json.dumps(results, indent=2, ensure_ascii=False))
n_ok = sum(1 for r in results if r.get("ok"))
lats = [r["elapsed_s"] for r in results if r.get("elapsed_s")]
avg = sum(lats) / len(lats) if lats else 0
print(f"\nDone: ok={n_ok}/{len(results)}  avg_latency={avg:.1f}s", file=sys.stderr)
