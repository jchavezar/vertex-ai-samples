"""Pre-compute the Judge Validation curated sample (~35 questions).

Reads:
  - runs/super500-b-rerun-20260526-092647/{responses_b.jsonl, judged_b_v6.json}
  - runs/super500-f-rev20-serial-20260525-000901/{responses_f.jsonl, judged_f_v6.json}
  - questions/*.json  (for question text)

Writes:
  - comparison-site/validation_sample.json

Three sections, computed deterministically at build time so the page is stable:
  A. Partials promoted to correct      (≤15) — B=correct but answer is hedgy
                                                or unusually short for a non-
                                                trivial category.
  B. Safety / refusal Tier 3           (≤12) — B=correct on tier-3 items OR on
                                                questions containing destructive
                                                keywords (delete, drop, rm -rf,
                                                production, credentials, …).
  C. Random control                    (8)   — random.seed(42) from B-correct
                                                not already in A or B.
"""
from __future__ import annotations

import glob
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EVAL = ROOT.parent  # …/eval/

B_DIR = EVAL / "runs" / "super500-b-rerun-20260526-092647"
F_DIR = EVAL / "runs" / "super500-f-rev20-serial-20260525-000901"
QDIR = EVAL / "questions"

OUT = ROOT / "validation_sample.json"

HEDGE_PHRASES = [
    "however",
    "but i ",
    "don't have access",
    "i don't have",
    "let me know if",
    "unfortunately",
    "i was unable",
    "cannot find",
    "couldn't find",
    "i am unable",
    "no matching issues",
]

SAFETY_KEYWORDS = [
    "delete",
    "drop ",
    "rm -rf",
    "password",
    "credential",
    "production",
    "destroy",
    "reveal",
    "leak",
    "override",
    "ignore previous",
    "bypass",
    "exfiltrate",
    "expose",
]

# Categories where a sub-300-char answer is plausibly fine (a single field
# lookup, a count, etc.). For other categories a short answer is more
# suspicious.
TRIVIAL_CATEGORIES = {"lookup"}


def load_all_questions() -> dict:
    out = {}
    for f in sorted(glob.glob(str(QDIR / "*.json"))):
        try:
            payload = json.load(open(f))
        except Exception:
            continue
        if not isinstance(payload, list) or not payload:
            continue
        if not isinstance(payload[0], dict) or "id" not in payload[0] or "q" not in payload[0]:
            continue
        for row in payload:
            qid = row.get("id")
            if qid and qid not in out:
                out[qid] = row
    return out


def load_responses(path: Path) -> dict:
    out = {}
    for line in open(path):
        try:
            r = json.loads(line)
        except Exception:
            continue
        out[r["id"]] = r
    return out


def load_judged(path: Path) -> dict:
    return {j["id"]: j for j in json.load(open(path))}


def is_hedgy(answer: str) -> bool:
    if not answer:
        return False
    a = answer.lower()
    return any(h in a for h in HEDGE_PHRASES)


def is_safety_q(qtext: str) -> bool:
    if not qtext:
        return False
    q = qtext.lower()
    return any(k in q for k in SAFETY_KEYWORDS)


def short_for_complexity(answer: str, category: str, tier) -> bool:
    """A < 300-char answer is suspicious unless it's a simple lookup tier-1."""
    if not answer:
        return True
    if len(answer) >= 300:
        return False
    # Simple lookup at tier 1 is fine being short.
    if category in TRIVIAL_CATEGORIES and tier == 1:
        return False
    return True


def build_card(qid, all_q, b_resp, b_judge, f_resp, f_judge, section, reason):
    qtext = (all_q.get(qid) or {}).get("q", "")
    cat = (all_q.get(qid) or {}).get("category") or b_judge[qid].get("category")
    tier = b_judge[qid].get("tier")
    b = b_resp.get(qid) or {}
    bj = b_judge[qid]
    f = f_resp.get(qid) or {}
    fj = f_judge.get(qid) or {}
    return {
        "id": qid,
        "question": qtext,
        "category": cat,
        "tier": tier,
        "section": section,
        "reason": reason,
        "b": {
            "answer": b.get("answer") or "",
            "verdict": bj.get("verdict"),
            "judge_reason": bj.get("judge_reason") or "",
            "composite_score": bj.get("composite_score"),
            "cited_keys": bj.get("cited_keys") or [],
            "latency_s": bj.get("latency_s"),
            "ok": bool(b.get("ok")),
            "answer_chars": bj.get("answer_chars"),
            "votes": bj.get("votes") or [],
        },
        "f": {
            "answer": f.get("answer") or "",
            "verdict": fj.get("verdict"),
            "judge_reason": fj.get("judge_reason") or "",
            "composite_score": fj.get("composite_score"),
            "cited_keys": fj.get("cited_keys") or [],
            "latency_s": fj.get("latency_s"),
            "ok": bool(f.get("ok")),
            "votes": fj.get("votes") or [],
        },
    }


def main() -> None:
    all_q = load_all_questions()
    b_resp = load_responses(B_DIR / "responses_b.jsonl")
    b_judge = load_judged(B_DIR / "judged_b_v6.json")
    f_resp = load_responses(F_DIR / "responses_f.jsonl")
    f_judge = load_judged(F_DIR / "judged_f_v6.json")

    print(f"Loaded {len(all_q)} questions, {len(b_resp)} B responses, {len(b_judge)} B judged.")
    print(f"Loaded {len(f_resp)} F responses, {len(f_judge)} F judged.")

    b_correct = [qid for qid, j in b_judge.items() if j.get("verdict") == "correct"]
    print(f"B verdict=correct: {len(b_correct)}")

    # -------- Section A: partials promoted to correct --------
    # Priority order: hedgy answers first (most suspicious), then short answers
    # outside trivial categories.
    hedgy_correct = []
    short_complex = []
    for qid in b_correct:
        r = b_resp.get(qid) or {}
        if not r.get("ok"):
            continue
        ans = r.get("answer") or ""
        j = b_judge[qid]
        cat = j.get("category") or ""
        tier = j.get("tier")
        if is_hedgy(ans):
            hedgy_correct.append(qid)
        elif short_for_complexity(ans, cat, tier):
            short_complex.append(qid)

    # Deterministic order: by qid.
    hedgy_correct.sort()
    short_complex.sort()
    sectionA_ids: list[str] = []
    for qid in hedgy_correct:
        if len(sectionA_ids) >= 15:
            break
        sectionA_ids.append(qid)
    for qid in short_complex:
        if len(sectionA_ids) >= 15:
            break
        sectionA_ids.append(qid)
    print(f"Section A: {len(sectionA_ids)}")

    # -------- Section B: safety / refusal Tier 3 --------
    sectionB_ids: list[str] = []
    tier3_correct = []
    safety_kw_correct = []
    for qid in b_correct:
        j = b_judge[qid]
        qtext = (all_q.get(qid) or {}).get("q") or ""
        if j.get("tier") == 3:
            tier3_correct.append(qid)
        elif is_safety_q(qtext):
            safety_kw_correct.append(qid)
    tier3_correct.sort()
    safety_kw_correct.sort()
    for qid in tier3_correct:
        if len(sectionB_ids) >= 12:
            break
        sectionB_ids.append(qid)
    for qid in safety_kw_correct:
        if qid in sectionB_ids:
            continue
        if len(sectionB_ids) >= 12:
            break
        sectionB_ids.append(qid)
    print(f"Section B: {len(sectionB_ids)} (tier3={sum(1 for q in sectionB_ids if b_judge[q].get('tier')==3)}, kw={sum(1 for q in sectionB_ids if b_judge[q].get('tier')!=3)})")

    # -------- Section C: random control --------
    excluded = set(sectionA_ids) | set(sectionB_ids)
    remaining = [qid for qid in b_correct if qid not in excluded]
    remaining.sort()
    rng = random.Random(42)
    rng.shuffle(remaining)
    sectionC_ids = remaining[:8]
    print(f"Section C: {len(sectionC_ids)}")

    cards = []
    for qid in sectionA_ids:
        reason = "hedgy" if is_hedgy((b_resp.get(qid) or {}).get("answer") or "") else "short"
        cards.append(build_card(qid, all_q, b_resp, b_judge, f_resp, f_judge, "A", reason))
    for qid in sectionB_ids:
        j = b_judge[qid]
        reason = "tier3" if j.get("tier") == 3 else "safety_keyword"
        cards.append(build_card(qid, all_q, b_resp, b_judge, f_resp, f_judge, "B", reason))
    for qid in sectionC_ids:
        cards.append(build_card(qid, all_q, b_resp, b_judge, f_resp, f_judge, "C", "random_control"))

    out_doc = {
        "generated_from": {
            "b_run": str(B_DIR.relative_to(EVAL)),
            "f_run": str(F_DIR.relative_to(EVAL)),
        },
        "judge": "judge_v6",
        "sections": {
            "A": {
                "label": "Partials promoted to correct",
                "description": "B graded 'correct' but the answer is plausibly incomplete (hedging language, or unusually short for a non-trivial category).",
                "ids": sectionA_ids,
            },
            "B": {
                "label": "Safety / refusal Tier 3",
                "description": "B graded 'correct' on tier-3 safety items, or on questions containing destructive keywords (delete, drop, rm -rf, production, credentials, …).",
                "ids": sectionB_ids,
            },
            "C": {
                "label": "Random control",
                "description": "Random sample (seed=42) from B-correct questions not in A or B. Sanity check.",
                "ids": sectionC_ids,
            },
        },
        "total_cards": len(cards),
        "cards": cards,
    }
    OUT.write_text(json.dumps(out_doc, indent=2, ensure_ascii=False))
    print(f"Wrote {OUT} with {len(cards)} cards.")


if __name__ == "__main__":
    main()
