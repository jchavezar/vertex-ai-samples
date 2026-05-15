"""Judge using EXACT syntax from user's working REPL."""
import json, sys
from pathlib import Path
from google import genai
from google.genai import types

INPUT = Path(sys.argv[1])
LABEL = sys.argv[2]
OUT = Path("judged") / f"{LABEL}.json"
OUT.parent.mkdir(exist_ok=True)

# EXACT syntax from user's REPL
client = genai.Client(vertexai=True, project="vtxdemos", location="global")

questions = {q["id"]: q for q in json.loads((Path.home() / "docparse-eval-private" / "questions_full.json").read_text())}
answers = {r["id"]: r for r in json.loads(INPUT.read_text())}
common = sorted(set(questions) & set(answers))
print(f"judging {len(common)}...")

results = []
for i, qid in enumerate(common, 1):
    q, sa = questions[qid], answers[qid]
    if not sa.get("ok"):
        results.append({**q, "parser": LABEL, "sa_answer": "", "correctness": 0, "completeness": 0, "verdict": "error", "judge_reason": "answer failed", "sa_ok": False, "sa_elapsed_s": sa.get("elapsed_s")})
        continue
    
    prompt = f'''Score this Q&A. Return ONLY JSON:

QUESTION: {q["q"]}
GROUND TRUTH: {q["a"]}
ANSWER: {sa.get("answer","")}

{{"correctness": 0.0-1.0, "completeness": 0.0-1.0, "verdict": "correct"|"partial"|"wrong"|"refused", "reason": "one sentence"}}'''
    
    try:
        # EXACT REPL syntax: client.models.generate_content(model="...", contents="...")
        re = client.models.generate_content(
            model="gemini-3.1-pro-preview",
            contents=prompt,
            config=types.GenerateContentConfig(max_output_tokens=400, temperature=0, response_mime_type="application/json"))
        d = json.loads(re.text)
        d["id"] = qid
        results.append({**q, "parser": LABEL, "sa_answer": sa.get("answer",""), "sa_ok": True, "sa_elapsed_s": sa.get("elapsed_s"), **d})
    except Exception as e:
        results.append({**q, "parser": LABEL, "sa_answer": sa.get("answer",""), "sa_ok": True, "sa_elapsed_s": sa.get("elapsed_s"), "correctness": 0, "completeness": 0, "verdict": "error", "judge_reason": str(e)[:200]})
    
    if i % 50 == 0:
        print(f"  {i}/{len(common)}")

OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False))
print(f"done -> {OUT}")
