"""Judge with gemini-2.5-pro instead of Claude (faster, no cross-provider permissions)."""
import asyncio, json, os, sys
from pathlib import Path
from google import genai
from google.genai import types

INPUT = Path(sys.argv[1])
LABEL = sys.argv[2]
OUT = Path("judged") / f"{LABEL}.json"
OUT.parent.mkdir(exist_ok=True)

JUDGE_PROMPT = """You are an evaluator scoring an AI assistant's answer against a known-correct ground-truth answer.

Score on two dimensions (0.0 to 1.0 each):
- correctness: factual accuracy (wrong number/entity = low, exact match = 1.0)
- completeness: coverage (half missing = 0.5, all there = 1.0)

Verdict:
- "correct" if answer matches GT in substance
- "partial" if some right, some missing/wrong
- "wrong" if confidently incorrect
- "refused" if assistant said it can't find/answer

Return ONLY JSON:
{{"correctness": 0.0-1.0, "completeness": 0.0-1.0, "verdict": "correct"|"partial"|"wrong"|"refused", "reason": "one sentence"}}

QUESTION: {q}
GROUND TRUTH: {gt}
ANSWER: {ans}"""

client = genai.Client(vertexai=True, project="vtxdemos", location="global")

async def judge_one(q, sa, sem):
    async with sem:
        if not sa.get("ok"):
            return {"id": q["id"], "correctness": 0, "completeness": 0,
                    "verdict": "error", "reason": f"answer failed: {sa.get('error','?')[:120]}"}
        prompt = JUDGE_PROMPT.format(q=q["q"], gt=q["a"], ans=sa.get("answer",""))
        for attempt in range(3):
            try:
                resp = await client.aio.models.generate_content(
                    model="gemini-2.5-pro",
                    contents=[types.Content(role="user", parts=[types.Part.from_text(text=prompt)])],
                    config=types.GenerateContentConfig(
                        max_output_tokens=400, temperature=0,
                        response_mime_type="application/json"))
                d = json.loads(resp.text)
                d["id"] = q["id"]
                return d
            except Exception as e:
                if "429" in str(e):
                    await asyncio.sleep(2 ** attempt)
                    continue
                return {"id": q["id"], "correctness": 0, "completeness": 0,
                        "verdict": "error", "reason": f"{type(e).__name__}: {str(e)[:200]}"}
        return {"id": q["id"], "correctness": 0, "completeness": 0,
                "verdict": "error", "reason": "rate-limited"}

async def main():
    questions = {q["id"]: q for q in json.loads(Path("~/docparse-eval-private/questions_full.json").expanduser().read_text())}
    answers = {r["id"]: r for r in json.loads(INPUT.read_text())}
    common = sorted(set(questions) & set(answers))
    print(f"judging {len(common)} with gemini-2.5-pro...", file=sys.stderr)

    sem = asyncio.Semaphore(6)
    judged = await asyncio.gather(*[judge_one(questions[i], answers[i], sem) for i in common])
    by_id = {j["id"]: j for j in judged}

    combined = []
    for q in sorted(questions.values(), key=lambda x: x["id"]):
        s = answers.get(q["id"], {})
        j = by_id.get(q["id"], {})
        combined.append({**q, "parser": LABEL,
            "sa_answer": s.get("answer", ""), "sa_elapsed_s": s.get("elapsed_s"),
            "sa_ok": s.get("ok", False), "correctness": j.get("correctness", 0),
            "completeness": j.get("completeness", 0), "verdict": j.get("verdict", "error"),
            "judge_reason": j.get("reason", "")})
    OUT.write_text(json.dumps(combined, indent=2, ensure_ascii=False))
    print(f"done -> {OUT}", file=sys.stderr)

asyncio.run(main())
