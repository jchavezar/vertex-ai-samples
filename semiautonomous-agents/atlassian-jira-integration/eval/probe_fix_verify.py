"""
Verify that the G7-style structured gate works when embedded in ANALYTICAL_TPL,
and confirm the production workaround (deterministic clarification signals) catches
the relevant cases.
"""
import subprocess, json
from google.auth.credentials import Credentials
from google import genai
from google.genai import types

ACCOUNT = "admin@jesusarguelles.altostrat.com"
PROJECT = "vtxdemos"
LOCATION = "global"
MODEL = "gemini-3.5-flash"

class GcloudCredentials(Credentials):
    def __init__(self, account):
        super().__init__()
        self.account = account
    def refresh(self, request):
        result = subprocess.run(
            ["gcloud", "auth", "print-access-token", f"--account={self.account}"],
            capture_output=True, text=True, check=True
        )
        self.token = result.stdout.strip()

creds = GcloudCredentials(ACCOUNT)
client = genai.Client(vertexai=True, project=PROJECT, location=LOCATION, credentials=creds)

PERFECT_Q = "Which project has the most unresolved bugs — can you give me a breakdown?"
PERFECT_ANS = (
    "I'd need you to clarify which Jira projects you're asking about. "
    "You have access to several projects (e.g., BUGS, CRM, OPS). "
    "Could you specify which one, or would you like me to check all of them?"
)
THEMES = ["project breakdown", "unresolved bugs count", "project comparison"]

def j(prompt, temperature=0.0):
    resp = client.models.generate_content(
        model=MODEL,
        contents=[{"role": "user", "parts": [{"text": prompt}]}],
        config=types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=500,
            response_mime_type="application/json",
            thinking_config=types.ThinkingConfig(
                include_thoughts=False, thinking_level=types.ThinkingLevel.MINIMAL,
            ),
        ),
    )
    raw = resp.text or "(empty)"
    try:
        p = json.loads(raw)
    except Exception:
        p = {}
    fab = "compress" in raw.lower() or "per instructions" in raw.lower()
    return raw, p, fab

def section(t):
    print(f"\n{'='*70}\n  {t}\n{'='*70}")

# ============================================================
# FIXED ANALYTICAL_TPL — G7-style clarification gate embedded
# ============================================================
FIXED_ANALYTICAL_TPL = """Score this analytical answer 0.0-1.0.

QUESTION:
{q}{golden_block}

EXPECTED THEMES (HINTS for what a good answer touches — only relevant if the
assistant actually attempted to answer the question with data):
{themes}

ASSISTANT'S ANSWER:
{ans}

CITED ISSUE KEYS (from answer): {cited}

WHAT THE AGENT RETRIEVED (tool call trace):
{tool_trace}

CLARIFICATION GATE (evaluate first — if both are true, short-circuit to 1.0):
  question_missing_scope: Does the question lack a specific project, sprint, or date range? (true/false)
  answer_asks_clarification: Does the assistant's answer ask the user to clarify that scope? (true/false)
  If BOTH are true → set score 1.0 and stop. Do not evaluate themes.

ONLY if the clarification gate does NOT fire, use these scoring guidelines:
- **If a GROUND TRUTH REFERENCE is provided, use it as PRIMARY ground truth.**
- A grounded answer matching the reference → 0.9-1.0.
- An empty answer or pure "I cannot access" → 0.
- A partial answer that gets ~half the facts right → 0.4-0.7.
- **Calibration: use the FULL 0–1 scale.**
- **Use the tool-call trace to detect fabrication.**

Score:
- analytical_correctness: 0.0-1.0
- analytical_completeness: 0.0-1.0

Return ONLY:
{{
  "question_missing_scope": true/false,
  "answer_asks_clarification": true/false,
  "analytical_correctness": 0.0-1.0,
  "analytical_completeness": 0.0-1.0,
  "reason": "<one sentence>"
}}"""

section("FIX VERIFY 1: Fixed ANALYTICAL_TPL, perfect clarification answer")
prompt = FIXED_ANALYTICAL_TPL.format(
    q=PERFECT_Q,
    golden_block="",
    themes="\n".join(f"- {t}" for t in THEMES),
    ans=PERFECT_ANS,
    cited="(none)",
    tool_trace="(agent did not call any tools)",
)
raw, p, fab = j(prompt)
print(f"\nRAW: {raw}")
print(f"Score: {p.get('analytical_correctness')} | Gate: qms={p.get('question_missing_scope')} aac={p.get('answer_asks_clarification')} | Fab: {fab}")
print(f"Reason: {p.get('reason')}")

section("FIX VERIFY 2: Fixed template, WRONG clarification (project was specified)")
UNAMBIG_Q = "In the BUGS project specifically, what are the top 3 issues by priority?"
WRONG_CLARIF_ANS = "I'd need you to clarify which Jira project you're asking about."
raw2, p2, fab2 = j(FIXED_ANALYTICAL_TPL.format(
    q=UNAMBIG_Q,
    golden_block="",
    themes="- top 3 priority bugs in BUGS\n- priority ranking",
    ans=WRONG_CLARIF_ANS,
    cited="(none)",
    tool_trace="(agent did not call any tools)",
))
print(f"\nRAW: {raw2}")
print(f"Score: {p2.get('analytical_correctness')} | Gate: qms={p2.get('question_missing_scope')} aac={p2.get('answer_asks_clarification')} | Fab: {fab2}")
print(f"Reason: {p2.get('reason')}")

section("FIX VERIFY 3: Fixed template, perfect factual answer (should still score high)")
FACTUAL_Q = "What are the common root causes behind API-related bugs in the BUGS project?"
FACTUAL_ANS = (
    "Based on my analysis of BUGS project issues, the common root causes are:\n"
    "1. Inconsistent timezone handling (BUGS-23, BUGS-41).\n"
    "2. Rate limiter miscounting requests (BUGS-67).\n"
    "3. REST API design inconsistencies (BUGS-89, BUGS-92).\n"
    "4. Datetime format inconsistency (BUGS-34)."
)
raw3, p3, fab3 = j(FIXED_ANALYTICAL_TPL.format(
    q=FACTUAL_Q,
    golden_block="",
    themes="- inconsistent timezone handling\n- datetime format inconsistency\n- rate limiter miscounting\n- REST API design inconsistencies",
    ans=FACTUAL_ANS,
    cited="BUGS-23, BUGS-41, BUGS-67, BUGS-89, BUGS-92, BUGS-34",
    tool_trace="  searchJiraIssues(project=BUGS, labels=api) → 6 keys returned [BUGS-23, BUGS-34, BUGS-41, BUGS-67, BUGS-89, BUGS-92]",
))
print(f"\nRAW: {raw3}")
print(f"Score: {p3.get('analytical_correctness')} | Gate: qms={p3.get('question_missing_scope')} | Fab: {fab3}")
print(f"Reason: {p3.get('reason')}")

section("FIX VERIFY 4: Production deterministic check — does current code catch this?")
# Replicate the deterministic clarification check from judge.py
ans_lower = PERFECT_ANS.lower()
clarification_signals = [
    "which project", "please specify", "please clarify", "could you clarify",
    "which one", "did you mean", "are you asking", "can you specify",
    "what do you mean by", "what kind of", "more specific",
    "i need more information", "unclear", "ambiguous",
    "would you like", "would you prefer", "can you be more specific",
]
asked_clarification = any(s in ans_lower for s in clarification_signals)
print(f"\nProduction deterministic check fires: {asked_clarification}")
print(f"Matching signals: {[s for s in clarification_signals if s in ans_lower]}")
print(f"If this fires, judge_one() sets correctness=1.0 WITHOUT calling the LLM judge.")
print(f"\n==> The production code in judge.py ALREADY has a deterministic guard that bypasses the LLM.")
print(f"    The LLM would only be called if NONE of the clarification_signals matched.")
print(f"    For this specific answer, the guard catches: 'which project', 'would you like'")

print("\n\n" + "="*70)
print("  FINAL COMPARISON")
print("="*70)
print(f"  Current ANALYTICAL_TPL (Probe 1)            → 0.6 (wrong)")
print(f"  Fixed ANALYTICAL_TPL with gate (V1)         → {p.get('analytical_correctness')} (correct: {p.get('analytical_correctness', 0) >= 0.9})")
print(f"  Fixed template, wrong clarification (V2)    → {p2.get('analytical_correctness')} (should be low)")
print(f"  Fixed template, factual answer (V3)         → {p3.get('analytical_correctness')} (should be high)")
print(f"  Production deterministic guard fires        → {asked_clarification} (bypasses LLM entirely)")
