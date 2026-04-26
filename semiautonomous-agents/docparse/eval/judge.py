"""Judge a strategy's eval output with Claude Opus 4.5 on Vertex.

Usage:
    uv run --with 'anthropic[vertex]' python judge.py <runs/foo.json> <label>

Reads runs/<label>.json (the strategy's answers), writes judged/<label>.json
(answers + correctness + completeness + verdict + reason).
"""
import asyncio
import json
import os
import re
import sys
from pathlib import Path

from anthropic import AsyncAnthropicVertex

HERE = Path(__file__).resolve().parent

REGION = os.environ.get("JUDGE_REGION", "us-east5")
PROJECT = os.environ.get("JUDGE_PROJECT", "vtxdemos")
JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "claude-opus-4-5@20251101")
CONCURRENCY = int(os.environ.get("JUDGE_CONCURRENCY", "4"))

if len(sys.argv) < 3:
    sys.exit("usage: judge.py <runs/foo.json> <label>")
INPUT = Path(sys.argv[1])
LABEL = sys.argv[2]
OUT = HERE / "judged" / f"{LABEL}.json"
OUT.parent.mkdir(exist_ok=True)

JUDGE_SYSTEM = (
    "You are an evaluator scoring an AI assistant's answer against a "
    "known-correct ground-truth answer for a single question. You are "
    "STRICT and CONSISTENT. You return ONLY valid JSON, no prose."
)

JUDGE_USER_TPL = """Score this Q&A on two dimensions, 0.0 to 1.0 each.

QUESTION:
{q}

GROUND TRUTH (what a perfect answer would say):
{gt}

ASSISTANT'S ANSWER:
{ans}

Score:
- correctness: Does the answer match the ground truth's facts? Wrong number / wrong entity / wrong direction = low. Partial = 0.4-0.7. Exact match or fully equivalent = 1.0.
- completeness: Does the answer cover the ground truth's full content? Half the cells = 0.5. All cells but missing context = 0.8. Everything plus useful context = 1.0.

A "refused" answer is correctness=0, completeness=0, verdict=refused.
A "wrong" answer is correctness < 0.3, verdict=wrong.
A "partial" answer is verdict=partial.
A "correct" answer is verdict=correct.

Return ONLY this JSON object:
{{"correctness": 0.0-1.0, "completeness": 0.0-1.0, "verdict": "correct"|"partial"|"wrong"|"refused", "reason": "<one short sentence explaining the score>"}}"""

_CLIENT = None
def client():
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = AsyncAnthropicVertex(region=REGION, project_id=PROJECT)
    return _CLIENT


def _strip(t):
    t = t.strip()
    if t.startswith("```"):
        t = re.sub(r"^```(?:json)?\n", "", t)
        t = re.sub(r"\n```$", "", t)
    return t


async def judge_one(q, sa, sem):
    async with sem:
        if not sa.get("ok"):
            return {"id": q["id"], "correctness": 0, "completeness": 0,
                    "verdict": "error",
                    "reason": f"answer step failed: {sa.get('error','?')[:120]}"}
        prompt = JUDGE_USER_TPL.format(q=q["q"], gt=q["a"], ans=sa.get("answer",""))
        for attempt in range(5):
            try:
                resp = await client().messages.create(
                    model=JUDGE_MODEL, max_tokens=400,
                    system=JUDGE_SYSTEM,
                    messages=[{"role": "user", "content": prompt}],
                )
                d = json.loads(_strip(resp.content[0].text))
                d["id"] = q["id"]
                return d
            except Exception as e:
                if "429" in str(e) or "RateLimit" in type(e).__name__:
                    await asyncio.sleep(min(60, 2 ** attempt + 1))
                    continue
                return {"id": q["id"], "correctness": 0, "completeness": 0,
                        "verdict": "error",
                        "reason": f"judge error: {type(e).__name__}: {str(e)[:200]}"}
        return {"id": q["id"], "correctness": 0, "completeness": 0,
                "verdict": "error", "reason": "judge rate-limited 5x"}


async def main():
    questions = {q["id"]: q for q in json.loads((HERE / "questions.json").read_text())}
    answers = {r["id"]: r for r in json.loads(INPUT.read_text())}
    common = sorted(set(questions) & set(answers))
    print(f"judging {len(common)} questions  ({INPUT.name} → {OUT.name})", file=sys.stderr)

    sem = asyncio.Semaphore(CONCURRENCY)
    judged = await asyncio.gather(*[judge_one(questions[i], answers[i], sem) for i in common])
    by_id = {j["id"]: j for j in judged}

    combined = []
    for q in sorted(questions.values(), key=lambda x: x["id"]):
        s = answers.get(q["id"], {})
        j = by_id.get(q["id"], {})
        combined.append({
            **q,
            "parser": LABEL,
            "sa_answer": s.get("answer", ""),
            "sa_chunks_used": s.get("chunks_used", 0),
            "sa_elapsed_s": s.get("elapsed_s"),
            "sa_ok": s.get("ok", False),
            "correctness": j.get("correctness", 0),
            "completeness": j.get("completeness", 0),
            "verdict": j.get("verdict", "error"),
            "judge_reason": j.get("reason", ""),
        })
    OUT.write_text(json.dumps(combined, indent=2, ensure_ascii=False))
    print(f"done -> {OUT}", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())
