"""
Probe 6 / deep-dive: nail the exact trigger for the fabricated phrase
and test concrete fixes.
"""
import subprocess, json, sys
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

def call_json(prompt, system=None, temperature=0.0, max_tokens=400):
    cfg_kwargs = dict(
        temperature=temperature,
        max_output_tokens=max_tokens,
        response_mime_type="application/json",
        thinking_config=types.ThinkingConfig(
            include_thoughts=False,
            thinking_level=types.ThinkingLevel.MINIMAL,
        ),
    )
    if system:
        cfg_kwargs["system_instruction"] = system
    resp = client.models.generate_content(
        model=MODEL,
        contents=[{"role": "user", "parts": [{"text": prompt}]}],
        config=types.GenerateContentConfig(**cfg_kwargs),
    )
    return resp.text or "(empty)"

def section(t):
    print(f"\n{'='*70}\n  {t}\n{'='*70}")

# =============================================================================
# PROBE F1: Exactly the Extra-D prompt — confirm it's reproducible
# =============================================================================
section("F1: Reproduct Extra-D — explicit ambiguity note, simple policy")
q = f"""Score this analytical answer 0.0-1.0.

QUESTION: {PERFECT_Q}

NOTE: This question is GENUINELY AMBIGUOUS — the user did not specify which of the 12 available projects to compare.

ASSISTANT'S ANSWER: {PERFECT_ANS}

Scoring policy:
- An answer that ASKS FOR CLARIFICATION on a GENUINELY AMBIGUOUS question (like this one) is CORRECT (1.0/1.0).
- A partial answer → 0.4-0.7.

Return ONLY: {{"analytical_correctness": 0.0-1.0, "reason": "..."}}"""
raw = call_json(q)
print(f"\nRAW: {raw}")
p = json.loads(raw)
print(f"Score: {p.get('analytical_correctness')} | Fabricated: {'compress' in raw.lower() or 'per instructions' in raw.lower()}")
print(f"Reason: {p.get('reason')}")

# =============================================================================
# F2: Same as F1 but WITHOUT the range "0.4-0.7" anchor — just "partial → low"
# =============================================================================
section("F2: Remove '0.4-0.7' numeric range from partial rule")
q2 = f"""Score this analytical answer 0.0-1.0.

QUESTION: {PERFECT_Q}

NOTE: This question is GENUINELY AMBIGUOUS — the user did not specify which of the 12 available projects to compare.

ASSISTANT'S ANSWER: {PERFECT_ANS}

Scoring policy:
- An answer that ASKS FOR CLARIFICATION on a GENUINELY AMBIGUOUS question (like this one) is CORRECT (1.0/1.0).
- A partial answer → low score.

Return ONLY: {{"analytical_correctness": 0.0-1.0, "reason": "..."}}"""
raw2 = call_json(q2)
print(f"\nRAW: {raw2}")
p2 = json.loads(raw2)
print(f"Score: {p2.get('analytical_correctness')} | Fabricated: {'compress' in raw2.lower() or 'per instructions' in raw2.lower()}")
print(f"Reason: {p2.get('reason')}")

# =============================================================================
# F3: Same but no partial rule at all — only the clarification=1.0 rule
# =============================================================================
section("F3: Only the clarification=1.0 rule, no partial range at all")
q3 = f"""Score this analytical answer 0.0-1.0.

QUESTION: {PERFECT_Q}

NOTE: This question is GENUINELY AMBIGUOUS — the user did not specify which of the 12 available projects to compare.

ASSISTANT'S ANSWER: {PERFECT_ANS}

Scoring policy:
- An answer that ASKS FOR CLARIFICATION on a GENUINELY AMBIGUOUS question is CORRECT (1.0/1.0).

Return ONLY: {{"analytical_correctness": 0.0-1.0, "reason": "..."}}"""
raw3 = call_json(q3)
print(f"\nRAW: {raw3}")
p3 = json.loads(raw3)
print(f"Score: {p3.get('analytical_correctness')} | Fabricated: {'compress' in raw3.lower() or 'per instructions' in raw3.lower()}")
print(f"Reason: {p3.get('reason')}")

# =============================================================================
# F4: The FULL ANALYTICAL_TPL but with explicit NOTE that question is ambiguous
# =============================================================================
ANALYTICAL_TPL = """Score this analytical answer 0.0-1.0.

QUESTION:
{q}{golden_block}

NOTE: This question is GENUINELY AMBIGUOUS — the user did not specify which of the available projects to compare.

EXPECTED THEMES (HINTS for what a good answer touches — these were
pre-imagined; the agent answers from REAL data and may surface different
but equally valid themes):
{themes}

ASSISTANT'S ANSWER:
{ans}

CITED ISSUE KEYS (from answer): {cited}

WHAT THE AGENT RETRIEVED (tool call trace — use this to see if the agent
actually had the data, vs fabricating from memory):
{tool_trace}

Scoring policy:
- **If a GROUND TRUTH REFERENCE is provided above, use it as the PRIMARY ground
  truth.** The expected themes are secondary hints. Compare the assistant's
  answer to the reference and grade for FACTUAL CORRECTNESS first, coverage
  second. If the answer flatly contradicts the reference (e.g., reference says
  CRM-100's parent is CRM-97 and the answer says "no parent"), that's WRONG
  (score 0.0-0.2) regardless of how much theme vocabulary it includes.
- **If only THEMES are provided (no reference), themes are HINTS not a
  checklist.** Grade based on whether the answer addresses the SPIRIT of the
  question with grounded data.
- An answer that ASKS FOR CLARIFICATION on a genuinely ambiguous question
  (no project named, vague time range) is CORRECT (1.0/1.0).
- A grounded, on-topic answer that surfaces real themes from the corpus and
  matches the reference (if provided) → 0.9-1.0.
- An empty answer or pure "I cannot access" → 0.
- A partial answer that gets ~half the facts right → 0.4-0.7.
- **Calibration: use the FULL 0–1 scale.** A demonstrably correct answer that
  matches the reference deserves 1.0. Do not anchor at 0.7-0.8 out of habit.
- **Use the tool-call trace to detect fabrication.** If the agent claims a
  parent/count/value that wasn't in any tool result, lower the score.

Score:
- analytical_correctness: Does the answer factually match the reference (or
  themes if no reference)?
- analytical_completeness: Coverage of the asked facts.

Return ONLY: {{"analytical_correctness": 0.0-1.0, "analytical_completeness": 0.0-1.0, "reason": "<one sentence>"}}"""

section("F4: Full ANALYTICAL_TPL with explicit ambiguity NOTE added")
full_prompt = ANALYTICAL_TPL.format(
    q=PERFECT_Q,
    golden_block="",
    themes="\n".join(f"- {t}" for t in THEMES),
    ans=PERFECT_ANS,
    cited="(none)",
    tool_trace="(agent did not call any tools)",
)
raw4 = call_json(full_prompt)
print(f"\nRAW: {raw4}")
p4 = json.loads(raw4)
print(f"Score: {p4.get('analytical_correctness')} | Fabricated: {'compress' in raw4.lower() or 'per instructions' in raw4.lower()}")
print(f"Reason: {p4.get('reason')}")

# =============================================================================
# F5: Investigate whether THEMES themselves cause the downgrade
#     The themes are about "project breakdown" — the agent didn't cover them
# =============================================================================
section("F5: Same full prompt but themes removed (no themes to miss)")
q5 = f"""Score this analytical answer 0.0-1.0.

QUESTION: {PERFECT_Q}

ASSISTANT'S ANSWER: {PERFECT_ANS}

Scoring policy:
- An answer that ASKS FOR CLARIFICATION on a genuinely ambiguous question
  (no project named, vague time range) is CORRECT (1.0/1.0).
- A partial answer that gets ~half the facts right → 0.4-0.7.
- An empty answer or pure "I cannot access" → 0.
- **Calibration: use the FULL 0–1 scale.** A demonstrably correct answer
  deserves 1.0. Do not anchor at 0.7-0.8 out of habit.

Return ONLY: {{"analytical_correctness": 0.0-1.0, "reason": "..."}}"""
raw5 = call_json(q5)
print(f"\nRAW: {raw5}")
p5 = json.loads(raw5)
print(f"Score: {p5.get('analytical_correctness')} | Fabricated: {'compress' in raw5.lower() or 'per instructions' in raw5.lower()}")
print(f"Reason: {p5.get('reason')}")

# =============================================================================
# F6: What if the THEMES match what the agent said (clarification IS the theme)?
# =============================================================================
section("F6: Themes that match the clarification answer")
q6 = f"""Score this analytical answer 0.0-1.0.

QUESTION: {PERFECT_Q}

EXPECTED THEMES:
- requesting project scope clarification
- identifying ambiguity in the query
- listing available projects

ASSISTANT'S ANSWER: {PERFECT_ANS}

Scoring policy:
- An answer that ASKS FOR CLARIFICATION on a genuinely ambiguous question
  (no project named, vague time range) is CORRECT (1.0/1.0).
- A partial answer that gets ~half the facts right → 0.4-0.7.

Return ONLY: {{"analytical_correctness": 0.0-1.0, "reason": "..."}}"""
raw6 = call_json(q6)
print(f"\nRAW: {raw6}")
p6 = json.loads(raw6)
print(f"Score: {p6.get('analytical_correctness')} | Fabricated: {'compress' in raw6.lower() or 'per instructions' in raw6.lower()}")
print(f"Reason: {p6.get('reason')}")

# =============================================================================
# F7: Full analytical TPL, using a DIFFERENT perfect clarification scenario
#     where the ambiguity is even MORE obvious (no project specified at all)
# =============================================================================
section("F7: Unambiguously ambiguous Q + clarification answer")
Q7 = "Which issues are most at risk of missing their deadline?"
ANS7 = "Could you clarify which project or sprint you're referring to? I have access to BUGS, CRM, and OPS — and without knowing the scope, I'd be guessing which issues to check."
raw7 = call_json(f"""Score this analytical answer 0.0-1.0.

QUESTION: {Q7}

EXPECTED THEMES:
- deadline risk assessment
- sprint timeline analysis
- at-risk issue identification

ASSISTANT'S ANSWER: {ANS7}

Scoring policy:
- An answer that ASKS FOR CLARIFICATION on a genuinely ambiguous question
  (no project named, vague time range) is CORRECT (1.0/1.0).
- A partial answer that gets ~half the facts right → 0.4-0.7.

Return ONLY: {{"analytical_correctness": 0.0-1.0, "reason": "..."}}""")
print(f"\nRAW: {raw7}")
p7 = json.loads(raw7)
print(f"Score: {p7.get('analytical_correctness')} | Fabricated: {'compress' in raw7.lower() or 'per instructions' in raw7.lower()}")
print(f"Reason: {p7.get('reason')}")

# =============================================================================
# F8: PROPOSED FIX — Rewrite the clarification rule as a hard override
# =============================================================================
section("F8: Proposed fix — clarification rule as OVERRIDE before other scoring")
q8 = f"""Score this analytical answer 0.0-1.0.

QUESTION: {PERFECT_Q}

EXPECTED THEMES:
- project breakdown
- unresolved bugs count
- project comparison

ASSISTANT'S ANSWER: {PERFECT_ANS}

STEP 1 — OVERRIDE CHECK (apply first, skip steps 2-3 if triggered):
  If the question does not name a specific project/sprint and the answer asks
  for clarification → score 1.0 immediately. Reason: "correct clarification".

STEP 2 — THEME COVERAGE (only if step 1 not triggered):
  How many expected themes does the answer address?

STEP 3 — FINAL SCORE (only if step 2 was reached):
  - All themes covered → 0.9-1.0
  - ~Half themes → 0.4-0.7
  - No themes → 0.0-0.3

Apply steps in order. Return ONLY: {{"analytical_correctness": 0.0-1.0, "reason": "..."}}"""
raw8 = call_json(q8)
print(f"\nRAW: {raw8}")
p8 = json.loads(raw8)
print(f"Score: {p8.get('analytical_correctness')} | Fabricated: {'compress' in raw8.lower() or 'per instructions' in raw8.lower()}")
print(f"Reason: {p8.get('reason')}")

# =============================================================================
# F9: Does the model know it scored wrong? Post-hoc challenge.
# =============================================================================
section("F9: Post-hoc challenge — confront Gemini with its own score")
challenge = f"""You just scored an AI assistant's answer at 0.6 out of 1.0.

The question was: "{PERFECT_Q}"
The answer was: "{PERFECT_ANS}"

Your scoring rules explicitly state:
"An answer that ASKS FOR CLARIFICATION on a genuinely ambiguous question (no project named, vague time range) is CORRECT (1.0/1.0)."

The question does NOT name a project. The answer DID ask for clarification.
Therefore, per your own rules, the score should be 1.0, not 0.6.

Please re-evaluate and correct your score.
Return ONLY: {{"analytical_correctness": 0.0-1.0, "reason": "..."}}"""
raw9 = call_json(challenge)
print(f"\nRAW: {raw9}")
p9 = json.loads(raw9)
print(f"Score: {p9.get('analytical_correctness')} | Fabricated: {'compress' in raw9.lower() or 'per instructions' in raw9.lower()}")
print(f"Reason: {p9.get('reason')}")

print("\n\n" + "="*70)
print("  FINAL SUMMARY TABLE")
print("="*70)
for label, pr, raw_r in [
    ("F1 (explicit ambiguity note, simple policy)", p, raw),
    ("F2 (no numeric range on partial)", p2, raw2),
    ("F3 (only clarification rule)", p3, raw3),
    ("F4 (full ANALYTICAL_TPL + ambiguity note)", p4, raw4),
    ("F5 (no themes)", p5, raw5),
    ("F6 (themes match clarification)", p6, raw6),
    ("F7 (different unambiguous Q)", p7, raw7),
    ("F8 (proposed step-override fix)", p8, raw8),
    ("F9 (post-hoc challenge)", p9, raw9),
]:
    score = pr.get('analytical_correctness', pr.get('verdict', '?'))
    fabricated = 'compress' in raw_r.lower() or 'per instructions' in raw_r.lower()
    print(f"  {label:<50} score={score}  fab={fabricated}")
