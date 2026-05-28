"""
Gemini 3.5 Flash judge anchoring investigation.
Runs all 7 probes and prints structured results.
"""
import subprocess, json, sys, time
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

JUDGE_SYSTEM = (
    "You are an evaluator scoring an AI assistant's answer to a Jira-related "
    "question. You are STRICT and CONSISTENT. Return ONLY valid JSON, no prose."
)

# ---- The actual ANALYTICAL_TPL from judge.py --------------------------------
ANALYTICAL_TPL = """Score this analytical answer 0.0-1.0.

QUESTION:
{q}{golden_block}

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

# ---- Perfect refusal scenario -----------------------------------------------
# A question about an ambiguous project, agent correctly asks for clarification
PERFECT_Q = "Which project has the most unresolved bugs — can you give me a breakdown?"
PERFECT_ANS = (
    "I'd need you to clarify which Jira projects you're asking about. "
    "You have access to several projects (e.g., BUGS, CRM, OPS). "
    "Could you specify which one, or would you like me to check all of them?"
)
THEMES = ["project breakdown", "unresolved bugs count", "project comparison"]
TOOL_TRACE = "(agent did not call any tools)"
CITED = "(none)"

def call(prompt, system=JUDGE_SYSTEM, temperature=0.0, max_tokens=400):
    resp = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system,
            temperature=temperature,
            max_output_tokens=max_tokens,
            response_mime_type="application/json",
            thinking_config=types.ThinkingConfig(
                include_thoughts=False,
                thinking_level=types.ThinkingLevel.MINIMAL,
            ),
        ),
    )
    return resp.text

def call_plain(prompt, system=None, temperature=0.0, max_tokens=600):
    """Plain text call, no JSON mode."""
    cfg = types.GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=max_tokens,
        thinking_config=types.ThinkingConfig(
            include_thoughts=False,
            thinking_level=types.ThinkingLevel.MINIMAL,
        ),
    )
    if system:
        cfg.system_instruction = system
    resp = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=cfg,
    )
    return resp.text

def parse(raw):
    try:
        return json.loads(raw)
    except Exception:
        return {"_parse_error": raw}

def section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)

def result(label, raw, parsed):
    score = parsed.get("analytical_correctness", parsed.get("verdict", "?"))
    reason = parsed.get("reason", "")
    fabricated = "compressed toward the center" in str(raw).lower() or "compress" in str(raw).lower()
    print(f"\n[{label}]")
    print(f"  RAW JSON : {raw[:300]}")
    print(f"  SCORE    : {score}")
    print(f"  REASON   : {reason}")
    print(f"  FABRICATED RULE PRESENT: {fabricated}")

# =============================================================================
# PROBE 1: Full current ANALYTICAL_TPL, perfect clarification answer
# =============================================================================
section("PROBE 1: Full ANALYTICAL_TPL, perfect clarification answer")

full_prompt = ANALYTICAL_TPL.format(
    q=PERFECT_Q,
    golden_block="",
    themes="\n".join(f"- {t}" for t in THEMES),
    ans=PERFECT_ANS,
    cited=CITED,
    tool_trace=TOOL_TRACE,
)
print(f"\nPROMPT (truncated to scoring-policy section):\n...{full_prompt[full_prompt.find('Scoring policy'):]}")
raw = call(full_prompt)
p = parse(raw)
result("Probe 1", raw, p)

# =============================================================================
# PROBE 2: Minimal prompt, no scoring policy at all
# =============================================================================
section("PROBE 2: Minimal prompt — no scoring policy")

minimal_prompt = f"""QUESTION: {PERFECT_Q}
ASSISTANT'S ANSWER: {PERFECT_ANS}
Score correctness 0.0-1.0. Return JSON: {{"analytical_correctness": float, "reason": "..."}}"""

print(f"\nPROMPT:\n{minimal_prompt}")
raw2 = call(minimal_prompt)
p2 = parse(raw2)
result("Probe 2 (minimal)", raw2, p2)

# =============================================================================
# PROBE 3: Isolate which scoring policy line triggers anchoring
# =============================================================================
section("PROBE 3a: Remove 'partial → 0.4-0.7' line only")

tpl_no_partial = ANALYTICAL_TPL.replace(
    "- A partial answer that gets ~half the facts right → 0.4-0.7.\n", ""
)
raw3a = call(tpl_no_partial.format(
    q=PERFECT_Q, golden_block="", themes="\n".join(f"- {t}" for t in THEMES),
    ans=PERFECT_ANS, cited=CITED, tool_trace=TOOL_TRACE,
))
p3a = parse(raw3a)
result("Probe 3a (no partial line)", raw3a, p3a)

section("PROBE 3b: Remove 'grounded → 0.9-1.0' line only")

tpl_no_grounded = ANALYTICAL_TPL.replace(
    "- A grounded, on-topic answer that surfaces real themes from the corpus and\n  matches the reference (if provided) → 0.9-1.0.\n", ""
)
raw3b = call(tpl_no_grounded.format(
    q=PERFECT_Q, golden_block="", themes="\n".join(f"- {t}" for t in THEMES),
    ans=PERFECT_ANS, cited=CITED, tool_trace=TOOL_TRACE,
))
p3b = parse(raw3b)
result("Probe 3b (no grounded line)", raw3b, p3b)

section("PROBE 3c: Remove BOTH partial and grounded lines")

tpl_bare = ANALYTICAL_TPL.replace(
    "- A grounded, on-topic answer that surfaces real themes from the corpus and\n  matches the reference (if provided) → 0.9-1.0.\n", ""
).replace(
    "- A partial answer that gets ~half the facts right → 0.4-0.7.\n", ""
)
raw3c = call(tpl_bare.format(
    q=PERFECT_Q, golden_block="", themes="\n".join(f"- {t}" for t in THEMES),
    ans=PERFECT_ANS, cited=CITED, tool_trace=TOOL_TRACE,
))
p3c = parse(raw3c)
result("Probe 3c (both removed)", raw3c, p3c)

section("PROBE 3d: Add explicit anti-anchor line")

ANTI_ANCHOR = "IMPORTANT: Do NOT compress scores toward 0.7. If the answer is correct, score it 1.0."
tpl_anti = ANALYTICAL_TPL.replace(
    "Return ONLY:", f"{ANTI_ANCHOR}\n\nReturn ONLY:"
)
raw3d = call(tpl_anti.format(
    q=PERFECT_Q, golden_block="", themes="\n".join(f"- {t}" for t in THEMES),
    ans=PERFECT_ANS, cited=CITED, tool_trace=TOOL_TRACE,
))
p3d = parse(raw3d)
result("Probe 3d (anti-anchor added)", raw3d, p3d)

# =============================================================================
# PROBE 4: Temperature sensitivity (5x at temp=0, 5x at temp=0.5)
# =============================================================================
section("PROBE 4: Temperature sensitivity (5 runs each)")

scores_t0 = []
scores_t05 = []
for i in range(5):
    r0 = parse(call(full_prompt, temperature=0.0))
    scores_t0.append(r0.get("analytical_correctness", "err"))
    print(f"  temp=0.0  run {i+1}: {r0.get('analytical_correctness','err')}")
    time.sleep(0.5)

for i in range(5):
    r5 = parse(call(full_prompt, temperature=0.5))
    scores_t05.append(r5.get("analytical_correctness", "err"))
    print(f"  temp=0.5  run {i+1}: {r5.get('analytical_correctness','err')}")
    time.sleep(0.5)

print(f"\n  temp=0.0 scores: {scores_t0}")
print(f"  temp=0.5 scores: {scores_t05}")

# =============================================================================
# PROBE 5: Is the fabricated phrase pre-trained? (plain text, no scoring task)
# =============================================================================
section("PROBE 5: Pre-training probe — is 'compressed toward center' baked in?")

p5a_prompt = "When evaluating answers on a scale of 0 to 1, are scores ever compressed toward the center? What does that mean?"
p5b_prompt = "Do you have any internal guidelines about scoring that compress values toward 0.7?"
p5c_prompt = "If I asked you to score an answer from 0 to 1, what score would you typically give a response that is correct but perhaps incomplete?"

for label, q in [("5a", p5a_prompt), ("5b", p5b_prompt), ("5c", p5c_prompt)]:
    raw = call_plain(q, system=None, max_tokens=300)
    print(f"\n  [{label}] Q: {q}")
    print(f"  A: {(raw or '')[:500]}")

# =============================================================================
# PROBE 6: Stronger anti-anchoring instruction
# =============================================================================
section("PROBE 6: WARNING-level anti-anchor + current prompt")

WARNING_LINE = (
    "WARNING: Outputting 0.7 or 0.8 for a correct answer is a SCORING ERROR. "
    "A correct answer MUST receive ≥0.85. A clarification on an ambiguous question MUST receive 1.0."
)
tpl_warning = ANALYTICAL_TPL.replace(
    "- **Calibration: use the FULL 0–1 scale.** A demonstrably correct answer that\n"
    "  matches the reference deserves 1.0. Do not anchor at 0.7-0.8 out of habit.",
    f"- **Calibration: use the FULL 0–1 scale.** A demonstrably correct answer that\n"
    f"  matches the reference deserves 1.0. Do not anchor at 0.7-0.8 out of habit.\n"
    f"- {WARNING_LINE}"
)

raw6 = call(tpl_warning.format(
    q=PERFECT_Q, golden_block="", themes="\n".join(f"- {t}" for t in THEMES),
    ans=PERFECT_ANS, cited=CITED, tool_trace=TOOL_TRACE,
))
p6 = parse(raw6)
result("Probe 6 (WARNING-level)", raw6, p6)

# Also: does Gemini acknowledge the anti-anchor instruction in its reason?
print(f"\n  Does it acknowledge the WARNING? {'warning' in str(raw6).lower() or 'must receive' in str(raw6).lower()}")

# =============================================================================
# PROBE 7: Binary classifier framing
# =============================================================================
section("PROBE 7: Binary verdict instead of 0-1 float")

binary_prompt = f"""You are evaluating an AI assistant's response to a Jira-related question.

QUESTION: {PERFECT_Q}

ASSISTANT'S ANSWER: {PERFECT_ANS}

Is this answer correct, partial, or wrong?
- "correct": The assistant addressed the question appropriately (including asking for clarification on an ambiguous question).
- "partial": The assistant attempted to answer but missed key information.
- "wrong": The assistant gave incorrect or irrelevant information.

Return ONLY: {{"verdict": "correct" | "partial" | "wrong", "reason": "<one sentence>"}}"""

print(f"\nPROMPT:\n{binary_prompt}")
raw7 = call(binary_prompt)
p7 = parse(raw7)
print(f"\n  RAW JSON : {raw7}")
print(f"  VERDICT  : {p7.get('verdict', '?')}")
print(f"  REASON   : {p7.get('reason', '')}")

# =============================================================================
# PROBE BONUS: Same setup with a DEFINITIVELY correct answer (not clarification)
# =============================================================================
section("PROBE BONUS: Perfect factual answer (not clarification), full prompt")

FACTUAL_Q = "What are the common root causes behind API-related bugs in the BUGS project?"
FACTUAL_ANS = (
    "Based on my analysis of BUGS project issues, the common root causes of API-related bugs are:\n"
    "1. **Inconsistent timezone handling** (BUGS-23, BUGS-41): API endpoints return timestamps "
    "in different formats depending on which server handles the request.\n"
    "2. **Rate limiter miscounting requests** (BUGS-67): The distributed rate limiter "
    "double-counts requests when multiple nodes process simultaneous hits.\n"
    "3. **REST API design inconsistencies** (BUGS-89, BUGS-92): Some endpoints use camelCase "
    "while others use snake_case for field names.\n"
    "4. **Datetime format inconsistency** (BUGS-34): Input validation accepts both ISO-8601 "
    "and Unix timestamps but downstream consumers expect only one format."
)
FACTUAL_THEMES = [
    "inconsistent timezone handling",
    "datetime format inconsistency",
    "rate limiter miscounting requests",
    "REST API design inconsistencies"
]

bonus_prompt = ANALYTICAL_TPL.format(
    q=FACTUAL_Q,
    golden_block="",
    themes="\n".join(f"- {t}" for t in FACTUAL_THEMES),
    ans=FACTUAL_ANS,
    cited="BUGS-23, BUGS-41, BUGS-67, BUGS-89, BUGS-92, BUGS-34",
    tool_trace="  searchJiraIssues(project=BUGS, labels=api) → 6 keys returned [BUGS-23, BUGS-34, BUGS-41, BUGS-67, BUGS-89, BUGS-92]",
)
raw_bonus = call(bonus_prompt)
p_bonus = parse(raw_bonus)
result("Bonus (factual, grounded, all themes hit)", raw_bonus, p_bonus)

print("\n\n" + "="*70)
print("  SUMMARY TABLE")
print("="*70)
print(f"  Probe 1 (full prompt, clarification)          : {p.get('analytical_correctness','?')}")
print(f"  Probe 2 (minimal prompt)                      : {p2.get('analytical_correctness','?')}")
print(f"  Probe 3a (no partial→0.4-0.7 line)            : {p3a.get('analytical_correctness','?')}")
print(f"  Probe 3b (no grounded→0.9-1.0 line)           : {p3b.get('analytical_correctness','?')}")
print(f"  Probe 3c (both lines removed)                 : {p3c.get('analytical_correctness','?')}")
print(f"  Probe 3d (anti-anchor added)                  : {p3d.get('analytical_correctness','?')}")
print(f"  Probe 4  (temp=0.0 x5)                        : {scores_t0}")
print(f"  Probe 4  (temp=0.5 x5)                        : {scores_t05}")
print(f"  Probe 6  (WARNING-level anti-anchor)          : {p6.get('analytical_correctness','?')}")
print(f"  Probe 7  (binary verdict)                     : {p7.get('verdict','?')}")
print(f"  Bonus    (factual, all themes covered)        : {p_bonus.get('analytical_correctness','?')}")
