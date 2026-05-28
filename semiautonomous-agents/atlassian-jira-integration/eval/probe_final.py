"""
Final probes: isolate the exact trigger for the anchoring on this specific Q/A pair,
and test the most promising fixes.
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

# The problematic Q/A
PERFECT_Q = "Which project has the most unresolved bugs — can you give me a breakdown?"
PERFECT_ANS = (
    "I'd need you to clarify which Jira projects you're asking about. "
    "You have access to several projects (e.g., BUGS, CRM, OPS). "
    "Could you specify which one, or would you like me to check all of them?"
)
THEMES = ["project breakdown", "unresolved bugs count", "project comparison"]

# A Q/A that WORKS (F7) — deadline question
WORKS_Q = "Which issues are most at risk of missing their deadline?"
WORKS_ANS = "Could you clarify which project or sprint you're referring to? I have access to BUGS, CRM, and OPS — and without knowing the scope, I'd be guessing which issues to check."

def j(prompt, temperature=0.0):
    resp = client.models.generate_content(
        model=MODEL,
        contents=[{"role": "user", "parts": [{"text": prompt}]}],
        config=types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=400,
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
# G1: What exactly differs between the working Q (F7) and the broken Q?
#     — Test: use the WORKING Q but with the broken Q's THEMES
# ============================================================
section("G1: Working Q + broken Q's themes")
raw, p, fab = j(f"""Score this analytical answer 0.0-1.0.

QUESTION: {WORKS_Q}

EXPECTED THEMES:
- project breakdown
- unresolved bugs count
- project comparison

ASSISTANT'S ANSWER: {WORKS_ANS}

Scoring policy:
- An answer that ASKS FOR CLARIFICATION on a genuinely ambiguous question
  (no project named, vague time range) is CORRECT (1.0/1.0).
- A partial answer that gets ~half the facts right → 0.4-0.7.

Return ONLY: {{"analytical_correctness": 0.0-1.0, "reason": "..."}}""")
print(f"\nScore: {p.get('analytical_correctness')} | Fab: {fab}")
print(f"Reason: {p.get('reason')}")

# ============================================================
# G2: Broken Q + working Q's themes
# ============================================================
section("G2: Broken Q + working Q's themes")
raw2, p2, fab2 = j(f"""Score this analytical answer 0.0-1.0.

QUESTION: {PERFECT_Q}

EXPECTED THEMES:
- deadline risk assessment
- sprint timeline analysis
- at-risk issue identification

ASSISTANT'S ANSWER: {PERFECT_ANS}

Scoring policy:
- An answer that ASKS FOR CLARIFICATION on a genuinely ambiguous question
  (no project named, vague time range) is CORRECT (1.0/1.0).
- A partial answer that gets ~half the facts right → 0.4-0.7.

Return ONLY: {{"analytical_correctness": 0.0-1.0, "reason": "..."}}""")
print(f"\nScore: {p2.get('analytical_correctness')} | Fab: {fab2}")
print(f"Reason: {p2.get('reason')}")

# ============================================================
# G3: Is "can you give me a breakdown?" the problem?
#     — Rephrase the Q to be more obviously ambiguous
# ============================================================
section("G3: Broken Q rephrased to remove 'breakdown'")
raw3, p3, fab3 = j(f"""Score this analytical answer 0.0-1.0.

QUESTION: Which Jira project has the highest number of open, unresolved bug tickets?

EXPECTED THEMES:
- project breakdown
- unresolved bugs count
- project comparison

ASSISTANT'S ANSWER: {PERFECT_ANS}

Scoring policy:
- An answer that ASKS FOR CLARIFICATION on a genuinely ambiguous question
  (no project named, vague time range) is CORRECT (1.0/1.0).
- A partial answer that gets ~half the facts right → 0.4-0.7.

Return ONLY: {{"analytical_correctness": 0.0-1.0, "reason": "..."}}""")
print(f"\nScore: {p3.get('analytical_correctness')} | Fab: {fab3}")
print(f"Reason: {p3.get('reason')}")

# ============================================================
# G4: Does Gemini think "can you give me a breakdown?" means the agent
#     SHOULD have provided the breakdown (not asked)?
#     — Q explicitly says THERE IS NO KNOWN PROJECT SCOPE
# ============================================================
section("G4: Q explicitly marks scope as unknown")
raw4, p4, fab4 = j(f"""Score this analytical answer 0.0-1.0.

QUESTION: [NO PROJECT SPECIFIED] Which project has the most unresolved bugs?

EXPECTED THEMES:
- project breakdown
- unresolved bugs count

ASSISTANT'S ANSWER: {PERFECT_ANS}

Scoring policy:
- An answer that ASKS FOR CLARIFICATION on a genuinely ambiguous question
  (no project named, vague time range) is CORRECT (1.0/1.0).
- A partial answer → 0.4-0.7.

Return ONLY: {{"analytical_correctness": 0.0-1.0, "reason": "..."}}""")
print(f"\nScore: {p4.get('analytical_correctness')} | Fab: {fab4}")
print(f"Reason: {p4.get('reason')}")

# ============================================================
# G5: Does Gemini think the agent SHOULD have just queried all 3 projects?
#     Key test: can Gemini score 1.0 if we tell it "querying all is NOT required"
# ============================================================
section("G5: Explicitly say querying all projects is NOT required")
raw5, p5, fab5 = j(f"""Score this analytical answer 0.0-1.0.

QUESTION: {PERFECT_Q}

NOTE: The agent is NOT required to proactively query all available projects.
Asking for clarification before querying is the PREFERRED approach when scope is unclear.

EXPECTED THEMES:
- project breakdown
- unresolved bugs count
- project comparison

ASSISTANT'S ANSWER: {PERFECT_ANS}

Scoring policy:
- An answer that ASKS FOR CLARIFICATION on a genuinely ambiguous question
  (no project named, vague time range) is CORRECT (1.0/1.0).
- A partial answer → 0.4-0.7.

Return ONLY: {{"analytical_correctness": 0.0-1.0, "reason": "..."}}""")
print(f"\nScore: {p5.get('analytical_correctness')} | Fab: {fab5}")
print(f"Reason: {p5.get('reason')}")

# ============================================================
# G6: Best candidate fix — completely rewrite the clarification rule
#     so it fires FIRST and prevents theme-coverage fallback
# ============================================================
section("G6: PROPOSED FIX — clarification gets evaluated BEFORE themes")
FIXED_TPL = f"""Score this analytical answer 0.0-1.0.

QUESTION: {PERFECT_Q}

EXPECTED THEMES (only consulted if the answer attempts to answer the question):
- project breakdown
- unresolved bugs count
- project comparison

ASSISTANT'S ANSWER: {PERFECT_ANS}

PRE-CHECK (evaluate this first):
  Does the question lack a specific project name or scope? YES/NO
  Does the assistant's answer ask for clarification on that missing scope? YES/NO
  If BOTH are YES → score is 1.0. Do not evaluate themes. Return immediately.

ONLY IF the pre-check does not apply, use these scoring guidelines:
- Grounded, complete answer → 0.9-1.0
- Partial answer → 0.4-0.7
- Wrong/irrelevant → 0.0-0.3

Return ONLY: {{"analytical_correctness": 0.0-1.0, "reason": "..."}}"""
raw6, p6, fab6 = j(FIXED_TPL)
print(f"\nRAW: {raw6}")
print(f"Score: {p6.get('analytical_correctness')} | Fab: {fab6}")
print(f"Reason: {p6.get('reason')}")

# ============================================================
# G7: PROPOSED FIX v2 — use JSON schema with a dedicated
#     "asked_clarification_correctly" boolean the model must fill first
# ============================================================
section("G7: PROPOSED FIX v2 — structured JSON with clarification gate first")
raw7, p7, fab7 = j(f"""You are evaluating an AI assistant answer.

QUESTION: {PERFECT_Q}
ASSISTANT'S ANSWER: {PERFECT_ANS}

EXPECTED THEMES (only relevant if the assistant actually attempted to answer):
- project breakdown
- unresolved bugs count
- project comparison

Evaluate in this exact order:
1. Is the question missing a specific project/scope? (true/false)
2. Did the assistant ask for clarification on that gap? (true/false)
3. If (1) AND (2) are both true, set score=1.0 and stop.
4. Otherwise, evaluate theme coverage and score 0.0-1.0.

Return ONLY (fill all fields):
{{
  "question_is_ambiguous": true,
  "answer_asks_clarification": true,
  "clarification_gate_fired": true,
  "analytical_correctness": 1.0,
  "reason": "..."
}}""")
print(f"\nRAW: {raw7}")
print(f"Score: {p7.get('analytical_correctness')} | Gate fired: {p7.get('clarification_gate_fired')} | Fab: {fab7}")
print(f"Reason: {p7.get('reason')}")

# ============================================================
# G8: PROPOSED FIX v3 — move clarification detection out of the prompt
#     into a PRE-CHECK question, then pass the result to the judge
# ============================================================
section("G8: PROPOSED FIX v3 — two-stage: pre-check determines framing")

# Stage 1: Ask Gemini whether the answer is a clarification
precheck_raw, precheck_p, _ = j(f"""Is the following an answer that asks for clarification on an ambiguous question, rather than attempting to answer directly?

QUESTION: {PERFECT_Q}
ANSWER: {PERFECT_ANS}

Return ONLY: {{"is_clarification": true/false, "question_is_ambiguous": true/false}}""")
print(f"\nPre-check: {precheck_raw}")

is_clarification = precheck_p.get("is_clarification", False)
is_ambiguous = precheck_p.get("question_is_ambiguous", False)

if is_clarification and is_ambiguous:
    result = {"analytical_correctness": 1.0, "reason": "pre-check: correct clarification on ambiguous question"}
    print(f"Stage 2: SHORT-CIRCUITED — pre-check triggered auto-1.0")
else:
    # Stage 2: full scoring
    result_raw, result, _ = j(f"""Score 0-1. QUESTION: {PERFECT_Q} ANSWER: {PERFECT_ANS} Return JSON.""")
    print(f"Stage 2: ran full judge → {result_raw}")

print(f"FINAL Score: {result.get('analytical_correctness')} | Reason: {result.get('reason')}")

print("\n\n" + "="*70)
print("  SUMMARY")
print("="*70)
for label, pr, fab in [
    ("G1 (working Q, broken themes)", p, fab),
    ("G2 (broken Q, working themes)", p2, fab2),
    ("G3 (Q rephrased no 'breakdown')", p3, fab3),
    ("G4 (Q has [NO PROJECT SPECIFIED] prefix)", p4, fab4),
    ("G5 (note: querying all NOT required)", p5, fab5),
    ("G6 (PRE-CHECK in prompt)", p6, fab6),
    ("G7 (structured JSON clarification gate)", p7, fab7),
]:
    score = pr.get("analytical_correctness", "?")
    print(f"  {label:<50} score={score}  fab={fab}")
print(f"  {'G8 (two-stage pre-check)':<50} score={result.get('analytical_correctness')}  (two-stage)")
