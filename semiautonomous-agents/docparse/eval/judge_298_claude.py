"""Judge 298 questions with Claude Opus."""
import asyncio, json, re, sys
from pathlib import Path
from anthropic import AsyncAnthropicVertex

REGION = "us-east5"
PROJECT = "vtxdemos"
JUDGE_MODEL = "claude-opus-4-5@20251101"
CONCURRENCY = 4

INPUT = Path(sys.argv[1])
LABEL = sys.argv[2]
OUT = Path("judged") / f"{LABEL}.json"
OUT.parent.mkdir(exist_ok=True)

JUDGE_SYSTEM = "You are an evaluator scoring an AI assistant's answer against a known-correct ground-truth answer. You are STRICT and CONSISTENT. You return ONLY valid JSON, no prose."
JUDGE_USER_TPL = """Score this Q&A on two dimensions, 0.0 to 1.0 each.

QUESTION: {q}
GROUND TRUTH: {gt}
ASSISTANT'S ANSWER: {ans}

Score:
- correctness: Does the answer match ground truth facts?
- completeness: Does the answer cover full content?

Verdict: correct / partial / wrong / refused

Return ONLY JSON:
{{"correctness": 0.0-1.0, "completeness": 0.0-1.0, "verdict": "correct"|"partial"|"wrong"|"refused", "reason": "one sentence"}}"""

_CLIENT = None
def client():
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = AsyncAnthropicVertex(region=REGION, project_id=PROJECT)
    return _CLIENT

def _strip(t):
    t = t.strip()
    if t.startswith("```"):
        t = re.sub(r"^```(?:json)?\n", "", t); t = re.sub(r"\n```$", "", t)
    return t

async def judge_one(q, sa, sem):
    async with sem:
        if not sa.get("ok"):
            return {"id": q["id"], "correctness": 0, "completeness": 0, "verdict": "error", "reason": "answer failed"}
        prompt = JUDGE_USER_TPL.format(q=q["q"], gt=q["a"], ans=sa.get("answer",""))
        for attempt in range(5):
            try:
                resp = await client().messages.create(model=JUDGE_MODEL, max_tokens=400, system=JUDGE_SYSTEM, messages=[{"role": "user", "content": prompt}])
                d = json.loads(_strip(resp.content[0].text))
                d["id"] = q["id"]
                return d
            except Exception as e:
                if "429" in str(e) or "RateLimit" in type(e).__name__:
                    await asyncio.sleep(min(60, 2 ** attempt + 1))
                    continue
                return {"id": q["id"], "correctness": 0, "completeness": 0, "verdict": "error", "reason": f"{type(e).__name__}"}
        return {"id": q["id"], "correctness": 0, "completeness": 0, "verdict": "error", "reason": "rate-limited"}

async def main():
    qfile = Path.home() / "docparse-eval-private" / "questions_full.json"
    questions = {q["id"]: q for q in json.loads(qfile.read_text())}
    answers = {r["id"]: r for r in json.loads(INPUT.read_text())}
    common = sorted(set(questions) & set(answers))
    print(f"judging {len(common)} questions...", file=sys.stderr)
    sem = asyncio.Semaphore(CONCURRENCY)
    judged = await asyncio.gather(*[judge_one(questions[i], answers[i], sem) for i in common])
    by_id = {j["id"]: j for j in judged}
    combined = []
    for q in sorted(questions.values(), key=lambda x: x["id"]):
        s = answers.get(q["id"], {})
        j = by_id.get(q["id"], {})
        combined.append({**q, "parser": LABEL, "sa_answer": s.get("answer", ""), "sa_elapsed_s": s.get("elapsed_s"), "sa_ok": s.get("ok", False), "correctness": j.get("correctness", 0), "completeness": j.get("completeness", 0), "verdict": j.get("verdict", "error"), "judge_reason": j.get("reason", "")})
    OUT.write_text(json.dumps(combined, indent=2, ensure_ascii=False))
    print(f"done -> {OUT}", file=sys.stderr)

asyncio.run(main())
