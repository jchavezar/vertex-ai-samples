"""Judge with gemini-3.1-pro using explicit gcloud token (not ADC)."""
import json, re, subprocess, sys
from pathlib import Path
from google import genai
from google.genai import types

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

# Use explicit token from gcloud (admin@jesusarguelles.altostrat.com)
def _get_token():
    return subprocess.check_output(["gcloud", "auth", "print-access-token"], text=True).strip()

# Initialize client with sharepoint-wif project and explicit credentials
import google.auth.transport.requests
from google.auth import credentials as creds_module

class TokenCredentials(creds_module.Credentials):
    def __init__(self, token):
        super().__init__()
        self.token = token
    
    def refresh(self, request):
        self.token = _get_token()

token = _get_token()
client = genai.Client(
    vertexai=True,
    project="sharepoint-wif",
    location="global",
    http_options={"headers": {"Authorization": f"Bearer {token}"}},
)

questions = {q["id"]: q for q in json.loads((Path.home() / "docparse-eval-private" / "questions_full.json").read_text())}
answers = {r["id"]: r for r in json.loads(INPUT.read_text())}
common = sorted(set(questions) & set(answers))
print(f"judging {len(common)} with gemini-3.1-pro-preview (sharepoint-wif, explicit token)...")

results = []
for i, qid in enumerate(common, 1):
    q, sa = questions[qid], answers[qid]
    if not sa.get("ok"):
        results.append({**q, "parser": LABEL, "sa_answer": "", "sa_elapsed_s": sa.get("elapsed_s"),
            "sa_ok": False, "correctness": 0, "completeness": 0, "verdict": "error", "judge_reason": "answer failed"})
        continue
    
    prompt = JUDGE_PROMPT.format(q=q["q"], gt=q["a"], ans=sa.get("answer",""))
    try:
        # Refresh token before each call (they expire after ~1h)
        if i % 50 == 0:
            token = _get_token()
            client = genai.Client(
                vertexai=True, project="sharepoint-wif", location="global",
                http_options={"headers": {"Authorization": f"Bearer {token}"}})
        
        resp = client.models.generate_content(
            model="gemini-3.1-pro-preview",
            contents=prompt,
            config=types.GenerateContentConfig(max_output_tokens=400, temperature=0, response_mime_type="application/json"))
        d = json.loads(resp.text)
        d["id"] = qid
        results.append({**q, "parser": LABEL, "sa_answer": sa.get("answer",""), "sa_elapsed_s": sa.get("elapsed_s"),
            "sa_ok": True, **d})
    except Exception as e:
        error_msg = str(e)[:200]
        results.append({**q, "parser": LABEL, "sa_answer": sa.get("answer",""), "sa_elapsed_s": sa.get("elapsed_s"),
            "sa_ok": True, "correctness": 0, "completeness": 0, "verdict": "error", "judge_reason": error_msg})
    
    if i % 50 == 0:
        print(f"  {i}/{len(common)} complete...")

OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False))
print(f"done -> {OUT}")
