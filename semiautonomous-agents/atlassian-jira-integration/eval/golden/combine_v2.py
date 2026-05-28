"""Phase 4: Combine curated (Phase 2) + handcrafted (Phase 3) into main_v2.json
and write main_v2_summary.md.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent.parent

SRC = EVAL_DIR / "questions/main.json"
PHASE2 = EVAL_DIR / "questions/main_v2_phase2.json"
PHASE3 = EVAL_DIR / "golden/phase3_handcrafted.json"
AUDIT = EVAL_DIR / "golden/dedup_audit.json"

OUT_QUESTIONS = EVAL_DIR / "questions/main_v2.json"
OUT_SUMMARY = EVAL_DIR / "questions/main_v2_summary.md"


def main():
    original = json.load(open(SRC))
    curated = json.load(open(PHASE2))
    handcrafted = json.load(open(PHASE3))
    audit = json.load(open(AUDIT))

    # Strip golden_facts from handcrafted before writing the questions file
    # (they go in main_v2.json but in a compact form — keep them, they're useful)
    combined = curated + handcrafted

    OUT_QUESTIONS.write_text(json.dumps(combined, indent=2, default=str))
    print(f"Wrote {len(combined)} questions → {OUT_QUESTIONS}")
    print(f"  curated (phase 2): {len(curated)}")
    print(f"  handcrafted (phase 3): {len(handcrafted)}")

    # Build summary report
    cat_before = Counter(q.get("category", "?") for q in original)
    cat_after = Counter(q.get("category", "?") for q in combined)

    # Top 10 downsampled templates (audit clusters where count > keep_sample_size)
    downsampled = [a for a in audit if a["count"] > a["keep_sample_size"]]
    downsampled.sort(key=lambda a: -(a["count"] - a["keep_sample_size"]))
    top10 = downsampled[:10]

    lines = []
    lines.append("# main_v2.json — Curated Question Set")
    lines.append("")
    lines.append(f"**Source:** `questions/main.json` ({len(original)} questions)")
    lines.append(f"**Output:** `questions/main_v2.json` ({len(combined)} questions)")
    lines.append("")
    lines.append("## Headline numbers")
    lines.append(f"- Original: {len(original)}")
    lines.append(f"- Curated (after dedup): {len(curated)}")
    lines.append(f"- Handcrafted real-power-user additions: {len(handcrafted)}")
    lines.append(f"- **Total v2: {len(combined)}**")
    lines.append("")
    lines.append("## Per-category distribution (before → after)")
    lines.append("")
    lines.append("| Category | Original | v2 | Δ |")
    lines.append("|---|---:|---:|---:|")
    all_cats = sorted(set(cat_before) | set(cat_after))
    for c in all_cats:
        b = cat_before.get(c, 0)
        a = cat_after.get(c, 0)
        lines.append(f"| {c} | {b} | {a} | {a - b:+d} |")
    lines.append(f"| **TOTAL** | **{len(original)}** | **{len(combined)}** | **{len(combined) - len(original):+d}** |")
    lines.append("")

    lines.append("## Top 10 templates that were downsampled")
    lines.append("")
    lines.append("These template clusters had many near-duplicate phrasings (e.g. lookup of "
                 "assignee/status/priority of different keys, or trend-over-30d for different "
                 "projects). We kept a representative sample per project.")
    lines.append("")
    lines.append("| Rank | Category | Cluster signature | Original | Kept | Dropped |")
    lines.append("|---:|---|---|---:|---:|---:|")
    for i, a in enumerate(top10, 1):
        lines.append(f"| {i} | {a['category']} | `{a['cluster_id']}` | {a['count']} | "
                     f"{a['keep_sample_size']} | {a['count'] - a['keep_sample_size']} |")
    lines.append("")

    lines.append("## 30 new realistic power-user questions (Phase 3)")
    lines.append("")
    lines.append("Each question was verified live against the Jira tenant; `golden_facts` "
                 "captured (count, keys, breakdowns, samples).")
    lines.append("")
    lines.append("| ID | Intent | Category | Question | Live count |")
    lines.append("|---|---|---|---|---:|")
    for q in handcrafted:
        n = q.get("golden_facts", {}).get("count", "?")
        question = q["q"].replace("|", "\\|")
        lines.append(f"| {q['id']} | {q.get('intent','-')} | {q['category']} | {question} | {n} |")
    lines.append("")

    lines.append("## Methodology notes")
    lines.append("")
    lines.append("**Phase 1 — Clustering.** Each question was hashed by intent signature "
                 "(category + field type + project count + presence of issue key + relative-date "
                 "flag) rather than by exact text, because the original set heavily paraphrases "
                 "the same intents (e.g. \"Who is assigned to BUGS-100?\" and \"Show me the "
                 "assignee for SMP-912\" are the same template).")
    lines.append("")
    lines.append("**Phase 2 — Dedup rules.** For templated clusters we kept up to 3 "
                 "representatives, biased for project diversity (one each from BUGS/CRM/OPS/PLAT/"
                 "SMP). Trend questions were dedup'd more aggressively (target 1 per "
                 "period/priority cell). Inherently unique categories — `ambiguous`, `multi-step`, "
                 "`root-cause-synthesis`, `cross-issue-analysis`, `refusal-test`, "
                 "`prompt-injection`, `pii-sensitive` — were kept in full (minus already-excluded "
                 "qids).")
    lines.append("")
    lines.append("**Relative dates.** 32 questions whose JQL used `-Nd` were rewritten to "
                 "absolute dates anchored to today (2026-05-21). Questions whose natural-language "
                 "phrasing relied on \"today/yesterday/this week\" without a JQL backing were "
                 "dropped because they rot.")
    lines.append("")
    lines.append("**Phase 3 — Handcrafted additions.** 30 questions across multi-dimensional "
                 "filter / comparative / cross-project dependency / workload / process compliance "
                 "/ sprint planning / risk surfacing / synthesis / audit / label exploration. Each "
                 "was validated against live Jira; queries that returned 0 issues were rewritten "
                 "until they had a non-empty answer.")
    lines.append("")
    lines.append("**Excluded qids honored:** `eval/golden/excluded_qids.json` (19 ambiguous "
                 "prompts that the prior audit marked broken).")
    lines.append("")
    lines.append("## Files")
    lines.append("")
    lines.append("- `eval/questions/main_v2.json` — the curated set (this report's output)")
    lines.append("- `eval/golden/dedup_audit.json` — per-cluster keep/drop decisions")
    lines.append("- `eval/golden/phase3_handcrafted.json` — handcrafted questions with full "
                 "golden_facts payload (counts, key lists, samples, link facts)")
    lines.append("- `eval/golden/dedup_curate.py`, `eval/golden/phase3_handcraft.py`, "
                 "`eval/golden/combine_v2.py` — the pipeline")

    OUT_SUMMARY.write_text("\n".join(lines) + "\n")
    print(f"Wrote summary → {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
