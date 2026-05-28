"""Pre-generate reference answers for the 50-Q grading sample.

For each analytical question (oracle=llm-judge or hybrid) in
`sample_50_ids.json`, ask a strong LLM (gemini-3-pro-preview by default) to
synthesize a reference answer using the question + expected themes +
expected count + a small sample of issue keys + the actual pipeline answers
as ground-truth anchors. The reference is meant to give a HUMAN GRADER a
quick gold-standard to compare each pipeline's answer against — it doesn't
have to be perfect, just defensible.

For pure JQL/count questions (oracle=jql) we already have the literal
answer (expected_count + expected_keys), so no LLM call is needed; the
build script will inject those directly into data.json as the reference.

Writes `reference_answers.json` next to this script:
  { "q0107": {"reference": "...", "kind": "llm-synthesized"}, ... }
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

# Same gcloud-user-token path as judge.py, just for generation
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))  # eval/
for _p in [_HERE.parent / ".env"]:
    if _p.exists():
        for line in _p.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

import judge  # noqa: E402

REFERENCE_MODEL = os.environ.get("REFERENCE_MODEL", "gemini-3-pro-preview")
REFERENCE_PROJECT = os.environ.get("JUDGE_PROJECT", "vtxdemos")
REFERENCE_LOCATION = "global"

SAMPLE_PATH = _HERE / "sample_50_ids.json"
OUT_PATH = _HERE / "reference_answers.json"

SYSTEM = (
    "You are synthesizing a REFERENCE ANSWER for a human grader. The grader "
    "will use this reference to evaluate AI assistant answers to a Jira "
    "question. Your reference should be (a) grounded in the issue keys that "
    "appeared in the agent answers, (b) cover the expected themes, (c) be "
    "concise (under 300 words). Do NOT prefix with 'Reference:'. Do NOT use "
    "headers or markdown — plain prose with inline issue keys."
)

PROMPT_TPL = """Synthesize a concise reference answer to this question, grounded in the real Jira data the agents retrieved.

QUESTION:
{q}

EXPECTED THEMES (what a good answer should cover):
{themes}

{count_line}

ISSUE KEYS THE AGENTS COMMONLY CITED:
{keys}

AGENT ANSWERS (for grounding — synthesize a consensus answer; do NOT copy any one verbatim):
{agent_answers}

Produce a reference answer (under 300 words, plain prose, cite issue keys when relevant)."""


def _gemini_pro_client():
    """Reuse judge.py's user-credentials helper but with a larger model."""
    from google import genai
    return genai.Client(
        vertexai=True,
        project=REFERENCE_PROJECT,
        location=REFERENCE_LOCATION,
        credentials=judge._user_credentials(),
    )


async def synthesize_reference(client, question: dict, agent_answers: list[str]) -> str:
    from google.genai import types as _t
    themes = "\n".join(f"- {t}" for t in question.get("expected_themes", []))
    count = question.get("expected_count")
    count_line = f"EXPECTED COUNT: {count}\n" if count is not None else ""
    # Collect the union of issue keys cited across the answers (truncate)
    import re
    keys: list[str] = []
    seen = set()
    for ans in agent_answers:
        for m in re.findall(r"\b[A-Z]{2,8}-\d+\b", ans or ""):
            if m not in seen:
                seen.add(m)
                keys.append(m)
    keys_str = ", ".join(keys[:30]) if keys else "(none cited)"
    # Trim agent answers
    trimmed = []
    for i, a in enumerate(agent_answers, 1):
        if not a:
            continue
        trimmed.append(f"Agent {i}: {a[:800]}")
    prompt = PROMPT_TPL.format(
        q=question["q"],
        themes=themes or "(no themes specified)",
        count_line=count_line,
        keys=keys_str,
        agent_answers="\n\n".join(trimmed),
    )

    def _do():
        resp = client.models.generate_content(
            model=REFERENCE_MODEL,
            contents=prompt,
            config=_t.GenerateContentConfig(
                system_instruction=SYSTEM,
                temperature=0.2,
                max_output_tokens=600,
                thinking_config=_t.ThinkingConfig(
                    include_thoughts=False,
                    thinking_level=_t.ThinkingLevel.MINIMAL,
                ),
            ),
        )
        return (resp.text or "").strip()
    return await asyncio.to_thread(_do)


async def main():
    sample_ids = set(json.load(open(SAMPLE_PATH)))
    questions = {q["id"]: q for q in json.load(open(_HERE.parent / "questions/main.json"))}
    # Load pipeline answers for grounding (use any one of the 5 runs — they
    # have the same question set; pick the runs the comparison site uses).
    PIPELINES = {
        "A": ("20260511-gemini25", "a"),
        "B": ("20260511-claude-rovo", "b"),
        "C": ("20260519-101102-option-g-full-si", "g"),
        "D": ("20260519-203012-option-h-full", "h"),
        "E": ("20260520-151125-option-e-v2-flashlite-FINAL", "i"),
    }
    answers_by_qid: dict[str, list[str]] = {}
    for run, letter in PIPELINES.values():
        path = _HERE.parent / "runs" / run / f"responses_{letter}.jsonl"
        with open(path) as f:
            for ln in f:
                try:
                    d = json.loads(ln)
                except Exception:
                    continue
                if d["id"] in sample_ids:
                    answers_by_qid.setdefault(d["id"], []).append(d.get("answer", "") or "")

    # Existing references (resume support)
    existing: dict = {}
    if OUT_PATH.exists():
        existing = json.loads(OUT_PATH.read_text())

    # Need-refs = sample ids whose oracle is analytical AND not already done
    needs_ref = []
    for qid in sample_ids:
        q = questions[qid]
        if q.get("oracle") in ("llm-judge", "hybrid") and qid not in existing:
            needs_ref.append(q)
    print(f"Generating references for {len(needs_ref)} questions "
          f"(model={REFERENCE_MODEL}, region={REFERENCE_LOCATION}).")
    if not needs_ref:
        return

    client = _gemini_pro_client()
    sem = asyncio.Semaphore(5)

    async def _one(q: dict):
        async with sem:
            try:
                ref = await synthesize_reference(client, q, answers_by_qid.get(q["id"], []))
                existing[q["id"]] = {"reference": ref, "kind": "llm-synthesized", "model": REFERENCE_MODEL}
                print(f"  ✓ {q['id']}  {q['category']:25s}  {len(ref):>4} chars")
            except Exception as exc:
                print(f"  ✗ {q['id']}  ERROR: {exc}")

    await asyncio.gather(*[_one(q) for q in needs_ref])
    OUT_PATH.write_text(json.dumps(existing, indent=2, ensure_ascii=False))
    print(f"\nWrote {len(existing)} reference answers → {OUT_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
