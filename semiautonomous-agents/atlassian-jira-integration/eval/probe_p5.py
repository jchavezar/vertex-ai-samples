"""Probe 5 and supplementary probes — plain text, no JSON mode forced."""
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

def call_text(prompt, system=None, temperature=0.0, max_tokens=600):
    cfg_kwargs = dict(
        temperature=temperature,
        max_output_tokens=max_tokens,
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
# PROBE 5: Pre-training introspection
# =============================================================================
section("PROBE 5a: General scoring philosophy")
r = call_text(
    "When you evaluate AI assistant answers on a scale of 0 to 1, "
    "do you tend to compress scores toward the center (like 0.6-0.7)? "
    "If so, why? Be honest about your scoring tendencies."
)
print(f"\nA: {r}")

section("PROBE 5b: Internal scoring guidelines")
r = call_text(
    "Do you have any internal trained preferences or guidelines that cause you to give "
    "scores around 0.7 even for answers that are mostly correct? "
    "Specifically, do you avoid giving 0.9 or 1.0 unless something is absolutely perfect?"
)
print(f"\nA: {r}")

section("PROBE 5c: Typical score for correct-but-incomplete")
r = call_text(
    "If I asked you to score an answer from 0 to 1, what score would you give "
    "a response that correctly identifies ambiguity in a question and asks for clarification? "
    "The answer is technically correct behavior but doesn't provide the actual data."
)
print(f"\nA: {r}")

section("PROBE 5d: Source of 'compressed toward center' phrase")
r = call_text(
    "Have you ever seen or used the phrase 'scores are compressed toward the center per instructions' "
    "when evaluating something? Where does that phrase come from — is it from training, "
    "calibration instructions, or somewhere else?"
)
print(f"\nA: {r}")

# =============================================================================
# PROBE EXTRA-A: Does Gemini understand the clarification-is-correct rule?
# =============================================================================
section("PROBE EXTRA-A: Direct rule application — clarification = 1.0?")
q = """You are scoring an AI response.
The scoring rule says: "An answer that ASKS FOR CLARIFICATION on a genuinely ambiguous question is CORRECT (1.0/1.0)."

QUESTION: Which project has the most unresolved bugs — can you give me a breakdown?

ASSISTANT'S ANSWER: I'd need you to clarify which Jira projects you're asking about. You have access to several projects (e.g., BUGS, CRM, OPS). Could you specify which one, or would you like me to check all of them?

Is the question genuinely ambiguous? Does the answer ask for clarification? What score does the rule mandate?
Return JSON: {"is_ambiguous": true/false, "asks_clarification": true/false, "score_per_rule": float, "reason": "..."}"""
resp = client.models.generate_content(
    model=MODEL,
    contents=[{"role": "user", "parts": [{"text": q}]}],
    config=types.GenerateContentConfig(
        temperature=0.0,
        max_output_tokens=400,
        response_mime_type="application/json",
        thinking_config=types.ThinkingConfig(
            include_thoughts=False,
            thinking_level=types.ThinkingLevel.MINIMAL,
        ),
    ),
)
raw = resp.text
print(f"\nRAW: {raw}")
try:
    p = json.loads(raw)
    print(f"is_ambiguous: {p.get('is_ambiguous')}")
    print(f"asks_clarification: {p.get('asks_clarification')}")
    print(f"score_per_rule: {p.get('score_per_rule')}")
    print(f"reason: {p.get('reason')}")
except Exception:
    pass

# =============================================================================
# PROBE EXTRA-B: Gemini's reasoning WITHOUT json mode — does it reason toward 1.0
#                but then emit a lower number?
# =============================================================================
section("PROBE EXTRA-B: Think-aloud scoring (no JSON mode)")

think_prompt = """You are evaluating an AI assistant response.

SCORING RULES:
- An answer that ASKS FOR CLARIFICATION on a genuinely ambiguous question is CORRECT (1.0/1.0).
- A partial answer that gets ~half the facts right → 0.4-0.7.

QUESTION: Which project has the most unresolved bugs — can you give me a breakdown?

ASSISTANT'S ANSWER: I'd need you to clarify which Jira projects you're asking about. You have access to several projects (e.g., BUGS, CRM, OPS). Could you specify which one, or would you like me to check all of them?

Think step by step:
1. Is the question ambiguous?
2. Does the answer ask for clarification?
3. What does rule 1 say the score should be?
4. Final score:"""

resp_think = client.models.generate_content(
    model=MODEL,
    contents=[{"role": "user", "parts": [{"text": think_prompt}]}],
    config=types.GenerateContentConfig(
        temperature=0.0,
        max_output_tokens=500,
        thinking_config=types.ThinkingConfig(
            include_thoughts=False,
            thinking_level=types.ThinkingLevel.MINIMAL,
        ),
    ),
)
print(f"\nThink-aloud response:\n{resp_think.text}")

# =============================================================================
# PROBE EXTRA-C: Competing signals — does Gemini weigh the question as "comparative"
#                regardless of clarification intent?
# =============================================================================
section("PROBE EXTRA-C: Completely unambiguous question, clarification is WRONG")

q2 = """Score this analytical answer 0.0-1.0.

QUESTION: In the BUGS project specifically, what are the top 3 issues by priority?

ASSISTANT'S ANSWER: I'd need you to clarify which Jira projects you're asking about. You have access to several projects (e.g., BUGS, CRM, OPS). Could you specify which one, or would you like me to check all of them?

Scoring policy:
- An answer that ASKS FOR CLARIFICATION on a genuinely ambiguous question is CORRECT (1.0/1.0).
- A partial answer → 0.4-0.7.
- Wrong/irrelevant answer → 0.0-0.3.

Return ONLY: {"analytical_correctness": 0.0-1.0, "reason": "..."}"""

resp2 = client.models.generate_content(
    model=MODEL,
    contents=[{"role": "user", "parts": [{"text": q2}]}],
    config=types.GenerateContentConfig(
        temperature=0.0,
        max_output_tokens=300,
        response_mime_type="application/json",
        thinking_config=types.ThinkingConfig(
            include_thoughts=False,
            thinking_level=types.ThinkingLevel.MINIMAL,
        ),
    ),
)
print(f"\nRAW (unambiguous Q, wrong clarification): {resp2.text}")

# =============================================================================
# PROBE EXTRA-D: Same clarification answer with EXPLICIT instruction the question IS ambiguous
# =============================================================================
section("PROBE EXTRA-D: Force Gemini to accept ambiguity with explicit note")

q3 = """Score this analytical answer 0.0-1.0.

QUESTION: Which project has the most unresolved bugs — can you give me a breakdown?

NOTE: This question is GENUINELY AMBIGUOUS — the user did not specify which of the 12 available projects to compare.

ASSISTANT'S ANSWER: I'd need you to clarify which Jira projects you're asking about. You have access to several projects (e.g., BUGS, CRM, OPS). Could you specify which one, or would you like me to check all of them?

Scoring policy:
- An answer that ASKS FOR CLARIFICATION on a GENUINELY AMBIGUOUS question (like this one) is CORRECT (1.0/1.0).
- A partial answer → 0.4-0.7.

Return ONLY: {"analytical_correctness": 0.0-1.0, "reason": "..."}"""

resp3 = client.models.generate_content(
    model=MODEL,
    contents=[{"role": "user", "parts": [{"text": q3}]}],
    config=types.GenerateContentConfig(
        temperature=0.0,
        max_output_tokens=300,
        response_mime_type="application/json",
        thinking_config=types.ThinkingConfig(
            include_thoughts=False,
            thinking_level=types.ThinkingLevel.MINIMAL,
        ),
    ),
)
print(f"\nRAW (with explicit ambiguity note): {resp3.text}")

# =============================================================================
# PROBE EXTRA-E: What does Gemini actually THINK the question expects?
# =============================================================================
section("PROBE EXTRA-E: Ask Gemini what a GOOD answer to the question looks like")

q4 = """A user asked an AI assistant: "Which project has the most unresolved bugs — can you give me a breakdown?"

The AI assistant has access to Jira projects BUGS, CRM, and OPS.

What would be the IDEAL response to this question? Would asking for clarification be appropriate, or should the assistant just query all projects?"""

r4 = call_text(q4)
print(f"\nGemini's view of ideal answer:\n{r4}")
