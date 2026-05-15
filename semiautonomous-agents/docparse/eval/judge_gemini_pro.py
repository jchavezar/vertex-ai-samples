"""Judge with gemini-3.1-pro-preview (uses gcloud user token)."""
import asyncio, json, os, sys, subprocess
from pathlib import Path
from google import genai
from google.genai import types

INPUT = Path(sys.argv[1])
LABEL = sys.argv[2]
OUT = Path("judged") / f"{LABEL}.json"
OUT.parent.mkdir(exist_ok=True)

# Use explicit token from gcloud
def _token():
    return subprocess.check_output(["gcloud", "auth", "print-access-token"], text=True).strip()

# Try sharepoint-wif (where earlier Gemini calls succeeded)
PROJECT = "sharepoint-wif"

JUDGE_PROMPT = """You are an evaluator scoring an AI assistant's answer against known-correct ground truth.

Score (0.0-1.0 each):
- correctness: factual accuracy
- completeness: coverage

Verdict: correct / partial / wrong / refused

Return ONLY JSON: {{"correctness": 0.0-1.0, "completeness": 0.0-1.0, "verdict": "...", "reason": "one sentence"}}

QUESTION: {q}
GROUND TRUTH: {gt}
ANSWER: {ans}"""

async def judge_one(q, sa, sem, client):
    async with sem:
        if not sa.get("ok"):
            return {"id": q["id"], "correctness": 0, "completeness": 0,
                    "verdict": "error", "reason": f"answer failed"}
        prompt = JUDGE_PROMPT.format(q=q["q"], gt=q["a"], ans=sa.get("answer",""))
        for attempt in range(3):
            try:
                resp = await client.aio.models.generate_content(
                    model="gemini-3.1-pro-preview",
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
                        "verdict": "error", "reason": f"{type(e).__name__}"}
        return {"id": q["id"], "correctness": 0, "completeness": 0, "verdict": "error", "reason": "rate-limited"}

async def main():
    client = genai.Client(vertexai=True, project=PROJECT, location="global")
    
    questions = {q["id"]: q for q in json.loads(Path("~/docparse-eval-private/questions_full.json").expanduser().read_text())}
    answers = {r["id"]: r for r in json.loads(INPUT.read_text())}
    common = sorted(set(questions) & set(answers))
    print(f"judging {len(common)} with gemini-3.1-pro (project={PROJECT})...", file=sys.stderr)

    sem = asyncio.Semaphore(6)
    judged = await asyncio.gather(*[judge_one(questions[i], answers[i], sem, client) for i in common])
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
