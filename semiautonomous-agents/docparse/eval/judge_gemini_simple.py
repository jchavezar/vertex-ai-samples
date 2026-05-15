"""Judge with gemini-3.1-pro using the simple syntax that works."""
import json, sys
from pathlib import Path
from google import genai

INPUT = Path(sys.argv[1])
LABEL = sys.argv[2]
OUT = Path("judged") / f"{LABEL}.json"
OUT.parent.mkdir(exist_ok=True)

JUDGE_PROMPT = """You are an evaluator. Score this Q&A:

QUESTION: {q}
GROUND TRUTH: {gt}
ANSWER: {ans}

Return ONLY JSON:
{{"correctness": 0.0-1.0, "completeness": 0.0-1.0, "verdict": "correct"|"partial"|"wrong"|"refused", "reason": "one sentence"}}"""

client = genai.Client(vertexai=True, project="vtxdemos", location="global")

questions = {q["id"]: q for q in json.loads((Path.home() / "docparse-eval-private" / "questions_full.json").read_text())}
answers = {r["id"]: r for r in json.loads(INPUT.read_text())}
common = sorted(set(questions) & set(answers))
print(f"judging {len(common)} questions...")

results = []
for i, qid in enumerate(common, 1):
    q, sa = questions[qid], answers[qid]
    if not sa.get("ok"):
        results.append({**q, "parser": LABEL, "sa_answer": "", "sa_elapsed_s": sa.get("elapsed_s"),
            "sa_ok": False, "correctness": 0, "completeness": 0, "verdict": "error", "judge_reason": "answer failed"})
        continue
    
    prompt = JUDGE_PROMPT.format(q=q["q"], gt=q["a"], ans=sa.get("answer",""))
    try:
        resp = client.models.generate_content(
            model="gemini-3.1-pro-preview",
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                max_output_tokens=400, temperature=0,
                response_mime_type="application/json"))
        d = json.loads(resp.text)
        d["id"] = qid
        results.append({**q, "parser": LABEL, "sa_answer": sa.get("answer",""), "sa_elapsed_s": sa.get("elapsed_s"),
            "sa_ok": True, **d})
    except Exception as e:
        results.append({**q, "parser": LABEL, "sa_answer": sa.get("answer",""), "sa_elapsed_s": sa.get("elapsed_s"),
            "sa_ok": True, "correctness": 0, "completeness": 0, "verdict": "error", "judge_reason": f"{type(e).__name__}"})
    
    if i % 50 == 0:
        print(f"  {i}/{len(common)} complete...")

OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False))
print(f"done -> {OUT}")
