"""Build comparison-site/data.json from the per-option judged runs.

Edit `PIPELINES` below to point at the latest run directory you want to surface
in the website. Then run `python eval/comparison-site/build_data.py` from the
repo root. The HTML page loads data.json from the same directory.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Public-facing option letter -> (run dir, jsonl letter, display metadata)
PIPELINES: dict[str, dict] = {
    "A": {
        "run": "v2fix-20260521-145509-a",
        "letter": "a",
        "label": "Option A",
        "sub": "Custom MCP + ADK Agent (Vertex Agent Engine)",
        "model": "Gemini 2.5",
        "surface": "Agent picker (sidebar)",
        "question_set": "main_v2",
        "judge_version": "v6"
    },
    "B": {
        "run": "v2-20260521-124231-b",
        "letter": "b",
        "label": "Option B",
        "sub": "Atlassian-hosted Rovo MCP (37 tools) via GE streamAssist BYO_MCP",
        "model": "GE chat LLM + Rovo MCP (Atlassian-hosted)",
        "surface": "Main chat (BYO_MCP)",
        "question_set": "main_v2",
        "judge_version": "v6"
    },
    "C": {
        "run": "v2-20260521-124231-g",
        "letter": "g",
        "label": "Option C",
        "sub": "Custom MCP direct to GE (no ADK)",
        "model": "GE chat LLM + Custom MCP (Cloud Run, self-hosted)",
        "surface": "Main chat (BYO_MCP)",
        "question_set": "main_v2",
        "judge_version": "v6"
    },
    "D": {
        "run": "v2-20260521-124231-h",
        "letter": "h",
        "label": "Option D",
        "sub": "GE federated jira_cloud (no MCP, no Cloud Run)",
        "model": "GE built-in retrieval + chat LLM",
        "surface": "Main chat (federated)",
        "question_set": "main_v2",
        "judge_version": "v6"
    },
    "E": {
        "run": "v2-20260521-124231-i",
        "letter": "i",
        "label": "Option E ⭐",
        "sub": "google.genai tool-loop in Cloud Run, wrapped as BYO_MCP",
        "model": "gemini-3.1-flash-lite",
        "surface": "Main chat (BYO_MCP)",
        "question_set": "main_v2",
        "judge_version": "v6"
    },
    # Option F: ADK SequentialAgent wrapping Atlassian Rovo MCP, deployed to
    # Agent Engine. Different sample size (500q super-set) — flagged in the UI.
    "F": {
        "run": "super500-f-rev20-serial-20260525-000901",
        "letter": "f",
        "label": "Option F",
        "sub": "ADK + Atlassian Rovo MCP wrapper (Vertex Agent Engine) — 500q super-set",
        "model": "Gemini 2.5 Flash (ADK loop) + Rovo MCP (Atlassian-hosted)",
        "surface": "Agent picker (sidebar)",
        "question_set": "super500",
        "cost_per_1k": 2.50,
        "judge_version": "v6"
    },
    # A-lite: Option A's architecture (ADK + Custom MCP) but on
    # gemini-3.1-flash-lite for an apples-to-apples vs Option E comparison.
    "AL": {
        "run": "v2-20260521-124231-al",
        "letter": "al",
        "label": "Option A-lite",
        "sub": "Same as A but on gemini-3.1-flash-lite (apples-to-apples vs E)",
        "model": "gemini-3.1-flash-lite",
        "surface": "Agent picker (sidebar)",
        "cost_per_1k": 5.30,  # similar compute to A; cheaper LLM tokens,
        "question_set": "main_v2",
        "judge_version": "v6"
    },
    # A-Gemini3.5: Option A's architecture but on gemini-3.5-flash, the most
    # expensive Flash variant. Tests whether the ADK ceiling is the model
    # (would expect ~95%+) or the architecture.
    "AG": {
        "run": "v2-20260521-124231-ag",
        "letter": "ag",
        "label": "Option A-Gemini3.5",
        "sub": "Same as A but on gemini-3.5-flash ($1.50/$9.00 — most expensive Flash)",
        "model": "gemini-3.5-flash",
        "surface": "Agent picker (sidebar)",
        "cost_per_1k": 25.00,
        "question_set": "main_v2",
        "judge_version": "v6"
    },
    # E-Gemini3.5: Option E's architecture (genai loop) but on gemini-3.5-flash
    # — for apples-to-apples comparison with AG to see if E's simpler loop is
    # competitive vs A's ADK callbacks on the same expensive model.
    "EG": {
        "run": "v2-20260521-124231-eg",
        "letter": "eg",
        "label": "Option E-Gemini3.5",
        "sub": "Same as E but on gemini-3.5-flash (same model as AG, no ADK)",
        "model": "gemini-3.5-flash",
        "surface": "Main chat (BYO_MCP)",
        "cost_per_1k": 20.00,  # similar to AG but no Sessions billing — ~$5 cheaper,
        "question_set": "main_v2",
        "judge_version": "v6"
    },
    # C-Gemini3.5: Option C's architecture (BYO_MCP via streamAssist, no ADK,
    # no Cloud Run loop) but with explicit gemini-3.5-flash override applied
    # via streamAssist's generationSpec.modelId. Tests whether swapping GE's
    # default chat LLM for the more expensive 3.5-flash improves the C ceiling.
    "CG": {
        "run": "v2-20260521-124231-cg",
        "letter": "cg",
        "label": "Option C-Gemini3.5",
        "sub": "Same as C (BYO_MCP via streamAssist) but with explicit gemini-3.5-flash model override",
        "model": "gemini-3.5-flash (via streamAssist generationSpec.modelId)",
        "surface": "Main chat (BYO_MCP)",
        # No Cloud Run code runs on the data path (GE drives the MCP); the LLM
        # tokens get billed at 3.5-flash rates (~6x default chat LLM). Net cost
        # is dominated by tokens but no per-call infra premium.
        "cost_per_1k": 4.00,
        "question_set": "main_v2",
        "judge_version": "v6"
    },
    # D-Gemini3.5: Option D (GE federated jira_cloud) + explicit
    # gemini-3.5-flash override via streamAssist generationSpec.modelId.
    # Tests whether swapping GE's default chat LLM for 3.5-flash improves
    # the D ceiling on the federated retrieval path.
    "DG": {
        "run": "v2-20260521-124231-dg",
        "letter": "dg",
        "label": "Option D-Gemini3.5",
        "sub": "Same as D (federated, no MCP) but with explicit gemini-3.5-flash override",
        "model": "gemini-3.5-flash (via streamAssist generationSpec.modelId)",
        "surface": "Main chat (federated)",
        "cost_per_1k": 4.00,
        "question_set": "main_v2",
        "judge_version": "v6"
    },
}

# Per-pipeline cost-per-1K (from docs/PRICING.md, 2026-05-20). Values
# already verified against official Google rate cards.
_DEFAULT_COSTS = {
    "A":  10.20,  # ADK + AE + Sessions, Gemini 2.5 Flash
    "B":   0.00,  # Atlassian hosts
    "C":   0.23,  # Cloud Run MCP only; GE bundles the chat LLM
    "D":   0.00,  # GE federated, bundled
    "E":   5.91,  # genai + Cloud Run + flash-lite tokens
    "AL":  5.30,  # ADK + AE + Sessions but flash-lite tokens (vs A's Gemini 2.5)
    "AG": 25.00,  # ADK + AE + Sessions + Gemini 3.5 Flash ($1.50/$9.00)
}

# Judge backend to read. "gemini" uses judged_<letter>_gemini.json (rejudged
# 2026-05-20 with gemini-3.5-flash for apples-to-apples scoring across all 5
# pipelines, with retry-on-error tagging). "claude" reads the original
# judged_<letter>.json (legacy — had silent 403s on C and D).
import os as _os
JUDGE_TAG = _os.environ.get("JUDGE_TAG", "gemini")
JUDGED_SUFFIX = "_gemini" if JUDGE_TAG == "gemini" else ""

SAFETY_CATS = {"refusal-test", "prompt-injection", "pii-sensitive", "ambiguous"}


def is_pass(verdict: str, cat: str) -> bool:
    return verdict == "correct" or (verdict == "refused" and cat in SAFETY_CATS)


def is_judge_error(verdict: str) -> bool:
    """judge_error verdicts mean the judge LLM failed transiently and the row
    should be excluded from the accuracy denominator (not counted as wrong)."""
    return verdict == "judge_error"


def load_resp(base: Path, run: str, letter: str) -> dict[str, dict]:
    p = base / "runs" / run / f"responses_{letter}.jsonl"
    out: dict[str, dict] = {}
    if not p.exists():
        return out
    with open(p) as f:
        for ln in f:
            try:
                d = json.loads(ln)
            except Exception:
                continue
            out[d["id"]] = d
    return out


def load_judged(base: Path, run: str, letter: str) -> dict[str, dict]:
    """Read the configured primary judge variant.

    Order of preference:
      1. judged_<letter>_v6.json             (v6 tiered evaluator; preferred)
      2. judged_<letter>_v5_1_gemini.json    (v5.1 calibration patch)
      3. judged_<letter>_v5_gemini.json      (single-judge v5; structured + self-consistency)
      4. judged_<letter>_v4_<backend>.json   (semantic + tool-using judge v4)
      5. judged_<letter>_<backend>_v2.json   (golden-aware v2)
      6. judged_<letter>_<backend>.json      (legacy v1)
      7. judged_<letter>.json                (un-suffixed)
    """
    candidates = [
        f"judged_{letter}_v6.json",
        f"judged_{letter}_v5_1_gemini.json",
        f"judged_{letter}_v5_gemini.json",
        f"judged_{letter}_v4_{JUDGE_TAG}.json",
        f"judged_{letter}{JUDGED_SUFFIX}_v2.json",
        f"judged_{letter}{JUDGED_SUFFIX}.json",
        f"judged_{letter}.json",
    ]
    for name in candidates:
        p = base / "runs" / run / name
        if p.exists():
            return {x["id"]: x for x in json.load(open(p))}
    return {}


# v6 tier weights — must match judge_v6.TIER_WEIGHTS.
V6_TIER_WEIGHTS = {1: 0.40, 2: 0.35, 3: 0.25}


def _v6_tier_of(category: str) -> int | str:
    """Mirror of judge_v6.TIER_FOR_CATEGORY (kept local to avoid import side-effects)."""
    return {
        "lookup": 1, "count-aggregate": 1, "jql-filter": 1,
        "golden-anti-regression": 1, "components-versions": 1,
        "comments-worklogs": 1, "epic-tree": 1, "issue-links": 1, "multi-project": 1,
        "root-cause-synthesis": 2, "cross-issue-analysis": 2, "multi-step": 2,
        "refusal-test": 3, "prompt-injection": 3, "pii-sensitive": 3,
        "pagination-required": "diagnostic", "ambiguous": "diagnostic",
        "trend": "diagnostic", "typo-robustness": "diagnostic",
        "tool-efficiency": "diagnostic",
    }.get(category, "diagnostic")


def load_judged_any(base: Path, run: str, letter: str, suffix: str) -> dict[str, dict]:
    """Load a specifically-named judged file (e.g. _sonnet, _gemini)."""
    p = base / "runs" / run / f"judged_{letter}{suffix}.json"
    if not p.exists():
        return {}
    return {x["id"]: x for x in json.load(open(p))}


def _v6_headline(by_tier: dict[Any, list[int]]) -> float | None:
    """Weighted-avg of T1/T2/T3 pass-pct, weights re-normalized over judged tiers.

    Returns percentage 0-100 rounded to 1dp, or None if no headline-eligible tier judged.
    """
    pcts = {}
    for t in (1, 2, 3):
        d = by_tier.get(t, [0, 0])[1]
        if d:
            pcts[t] = by_tier[t][0] / d
    if not pcts:
        return None
    total_w = sum(V6_TIER_WEIGHTS[t] for t in pcts)
    headline = sum(V6_TIER_WEIGHTS[t] / total_w * pcts[t] for t in pcts) * 100
    return round(headline, 1)


def _v6_headline_bar(by_tier: dict[Any, list[int]]) -> list[dict]:
    """Three stacked segments for the UI accuracy bar, one per tier.

    Each segment has the tier's weight (sum of widths = 100% of the bar) and the
    portion that passed (filled vs unfilled).
    """
    out = []
    judged_tiers = [t for t in (1, 2, 3) if by_tier.get(t, [0, 0])[1] > 0]
    if not judged_tiers:
        return out
    total_w = sum(V6_TIER_WEIGHTS[t] for t in judged_tiers)
    for t in (1, 2, 3):
        d = by_tier.get(t, [0, 0])[1]
        if not d:
            continue
        seg_width_pct = round(V6_TIER_WEIGHTS[t] / total_w * 100, 1)
        passes = by_tier[t][0]
        pass_pct = passes / d
        out.append({
            "tier": t,
            "weight": V6_TIER_WEIGHTS[t],
            "seg_width_pct": seg_width_pct,
            "width_pct": seg_width_pct,  # alias for older readers
            "pass_pct": round(pass_pct * 100, 1),
            "pass": passes,
            "passed": passes,
            "judged": d,
            "total": d,
            "fill_pct": round(seg_width_pct * pass_pct, 1),  # actual filled width
        })
    return out


def main() -> None:
    global PIPELINES
    eval_dir = Path(__file__).resolve().parent.parent  # .../eval
    # Question set: prefer main_v2.json if any pipeline declares it, else main.json.
    qs_path_main = eval_dir / "questions/main.json"
    qs_path_v2 = eval_dir / "questions/main_v2.json"
    use_v2 = any(v.get("question_set") == "main_v2" for v in PIPELINES.values())
    qs_path = qs_path_v2 if (use_v2 and qs_path_v2.exists()) else qs_path_main
    questions = json.load(open(qs_path))
    print(f"Using question set: {qs_path.name} ({len(questions)} questions)")

    # Skip any pipeline whose run dir doesn't exist yet (allows partial
    # rebuilds while late-arriving pipelines are still mid-eval).
    available_pipelines = {}
    for k, v in PIPELINES.items():
        run_dir = eval_dir / "runs" / v["run"]
        if run_dir.exists():
            available_pipelines[k] = v
        else:
            print(f"  ⚠ {k} skipped — run dir {v['run']} not found")
    PIPELINES = available_pipelines

    resp = {k: load_resp(eval_dir, v["run"], v["letter"]) for k, v in PIPELINES.items()}
    # Two judges, v4 = semantic + tool-using (current). Falls back to golden-aware
    # v2 (_gemini_v2 / _sonnet_v2), then v1 (_gemini / _sonnet) only if v4 doesn't
    # exist for that pipeline.
    #
    # For the secondary "claude" judge, we accept either `_v4_claude.json`
    # (judge_v4.py naming) or `_sonnet_v2.json` / `_sonnet.json` (legacy).
    def _load_with_fallback(run, letter, judge):
        # judged_<letter>_v4_<backend>.json wins; v2 next; v1 last.
        suffixes = [f"_v4_{judge}", f"_{judge}_v2", f"_{judge}"]
        # Allow sonnet alias to also pick up v4_claude (judge_v4.py emits
        # _v4_claude.json under --backend claude).
        if judge == "sonnet":
            suffixes = ["_v4_claude"] + suffixes
        for suffix in suffixes:
            d = load_judged_any(eval_dir, run, letter, suffix)
            if d:
                return d
        return {}
    judg_gemini = {k: _load_with_fallback(v["run"], v["letter"], "gemini") for k, v in PIPELINES.items()}
    judg_sonnet = {k: _load_with_fallback(v["run"], v["letter"], "sonnet") for k, v in PIPELINES.items()}
    # v5 — single-judge Gemini with structured output + adversarial self-critique
    # + self-consistency N=3 majority. Used for the new headline number; falls
    # back to v4 when v5 hasn't been run yet for a pipeline.
    judg_v5 = {
        k: load_judged_any(eval_dir, v["run"], v["letter"], "_v5_gemini")
        for k, v in PIPELINES.items()
    }
    # v5.1 — calibration patch on top of v5: skips adversarial Pass 2 for
    # binary categories (lookup, count-aggregate, golden-anti-regression,
    # typo-robustness, tool-efficiency) and tightens downgrade triggers.
    judg_v5_1 = {
        k: load_judged_any(eval_dir, v["run"], v["letter"], "_v5_1_gemini")
        for k, v in PIPELINES.items()
    }
    # v6 — tiered evaluator (T1 binary, T2 multi-axis, T3 refusal-strict, sidebar diagnostic).
    judg_v6 = {
        k: load_judged_any(eval_dir, v["run"], v["letter"], "_v6")
        for k, v in PIPELINES.items()
    }
    # Primary judge for the headline (still gemini for now). After human
    # tiebreak we'll merge a `_consensus` file.
    judg = judg_gemini

    rows = []
    for q in questions:
        row = {
            "id": q["id"],
            "category": q["category"],
            "q": q["q"],
            "oracle": q.get("oracle", "handcrafted"),
            "tags": q.get("tags", []),
            "expected_count": q.get("expected_count"),
            "expected_keys_sample": q.get("expected_keys", [])[:5],
            "expected_keys_total": len(q.get("expected_keys", [])),
            "expected_themes": q.get("expected_themes"),
            "jql": q.get("jql"),
            "min_tool_calls": q.get("min_tool_calls"),
            "pipelines": {},
        }
        for k in PIPELINES:
            r = resp[k].get(q["id"], {})
            jg = judg_gemini[k].get(q["id"], {})
            js = judg_sonnet[k].get(q["id"], {})
            jv5 = judg_v5[k].get(q["id"], {})
            jv51 = judg_v5_1[k].get(q["id"], {})
            jv6 = judg_v6[k].get(q["id"], {})
            primary = jg if jg else js  # gemini first; claude fallback if missing
            # judge_v4 emits `score` (0-1); legacy emits `correctness`.
            def _corr(j):
                if not j: return None
                if j.get("correctness") is not None: return j.get("correctness")
                if j.get("score") is not None: return j.get("score")
                return None
            gem_v = jg.get("verdict", "missing") if jg else "missing"
            son_v = js.get("verdict", "missing") if js else "missing"
            v5_v = jv5.get("verdict", "missing") if jv5 else "missing"
            v5_1_v = jv51.get("verdict", "missing") if jv51 else "missing"
            v6_v = jv6.get("verdict", "missing") if jv6 else "missing"
            # v6 uses its own explicit "pass" boolean in the row (set by the judge),
            # because pass semantics differ per tier (T1 binary vs T2 composite>=0.7).
            v6_pass = bool(jv6.get("pass")) if jv6 else False
            gem_pass = is_pass(gem_v, q["category"]) if jg else False
            son_pass = is_pass(son_v, q["category"]) if js else False
            v5_pass = is_pass(v5_v, q["category"]) if jv5 else False
            v5_1_pass = is_pass(v5_1_v, q["category"]) if jv51 else False
            # Consensus categorisation (only meaningful when BOTH judges scored):
            if jg and js and not is_judge_error(gem_v) and not is_judge_error(son_v) \
                    and gem_v != "missing" and son_v != "missing":
                if gem_pass and son_pass:
                    consensus = "both_correct"
                elif gem_pass and not son_pass:
                    consensus = "gemini_only"
                elif son_pass and not gem_pass:
                    consensus = "claude_only"
                else:
                    consensus = "both_wrong"
            else:
                consensus = "single_judge" if (jg or js) else "missing"
            # Headline verdict preference: v6 > v5.1 > v5 > v4 (gemini) > sonnet.
            if jv6:
                head = jv6
            elif jv51:
                head = jv51
            elif jv5:
                head = jv5
            elif jg:
                head = jg
            else:
                head = js or {}
            head_verdict = head.get("verdict", "missing")
            row["pipelines"][k] = {
                "answer": r.get("answer", "") or "",
                # Primary verdict (used by existing UI) — now reflects v5.1
                # when present, falling back to v5 / v4.
                "verdict": head_verdict,
                "correctness": _corr(head),
                "latency_s": head.get("latency_s", r.get("elapsed_s")),
                "n_tool_calls": head.get("n_tool_calls"),
                "cited_keys": (head.get("cited_keys") or [])[:10],
                "judge_reason": head.get("judge_reason", ""),
                "error": r.get("error"),
                "hallucination_rate": head.get("hallucination_rate"),
                "pass": (
                    v6_pass if jv6 else is_pass(head_verdict, q["category"])
                ),
                "primary_judge_version": (
                    "v6" if jv6 else "v5.1" if jv51 else "v5" if jv5 else "v4-gemini" if jg else "v4-sonnet" if js else "missing"
                ),
                # Per-question wall-clock timestamps
                "started_at": r.get("started_at_iso"),
                "finished_at": r.get("finished_at_iso"),
                "evaluated_at_estimated": bool(r.get("evaluated_at_estimated")),
                # Per-judge breakdown
                "gemini": {
                    "verdict": gem_v,
                    "correctness": _corr(jg),
                    "reason": (jg.get("judge_reason") or "")[:600] if jg else "",
                    "pass": gem_pass,
                    "tools_called": (jg.get("tools_called") or [])[:8] if jg else [],
                },
                "sonnet": {
                    "verdict": son_v,
                    "correctness": _corr(js),
                    "reason": (js.get("judge_reason") or "")[:600] if js else "",
                    "pass": son_pass,
                    "tools_called": (js.get("tools_called") or [])[:8] if js else [],
                },
                "judges_agree": (gem_pass == son_pass) if (jg and js) else None,
                # New consensus fields
                "consensus": consensus,
                "consensus_verdict": (
                    "correct" if consensus == "both_correct" else
                    "wrong" if consensus == "both_wrong" else
                    "disputed" if consensus in ("gemini_only", "claude_only") else
                    primary.get("verdict", "missing")
                ),
                "credible_pass": gem_pass or son_pass,
                "strict_pass": gem_pass and son_pass,
                # v5 single-judge (structured + adversarial + self-consistency)
                "v5": {
                    "verdict": v5_v,
                    "correctness": _corr(jv5),
                    "reason": (jv5.get("judge_reason") or "")[:600] if jv5 else "",
                    "pass": v5_pass,
                    "votes": (jv5.get("votes") or []) if jv5 else [],
                    "pass1_verdicts": (jv5.get("pass1_verdicts") or []) if jv5 else [],
                    "pass2_verdicts": (jv5.get("pass2_verdicts") or []) if jv5 else [],
                    "samples": (jv5.get("samples") or 0) if jv5 else 0,
                    "n_tool_calls": (jv5.get("n_judge_tool_calls") or 0) if jv5 else 0,
                },
                "v5_pass": v5_pass,
                # v5.1 calibration patch (per-category adversarial skip + tightened downgrade)
                "v5_1": {
                    "verdict": v5_1_v,
                    "correctness": _corr(jv51),
                    "reason": (jv51.get("judge_reason") or "")[:600] if jv51 else "",
                    "pass": v5_1_pass,
                    "votes": (jv51.get("votes") or []) if jv51 else [],
                    "pass1_verdicts": (jv51.get("pass1_verdicts") or []) if jv51 else [],
                    "pass2_verdicts": (jv51.get("pass2_verdicts") or []) if jv51 else [],
                    "samples": (jv51.get("samples") or 0) if jv51 else 0,
                    "n_tool_calls": (jv51.get("n_judge_tool_calls") or 0) if jv51 else 0,
                    "adversarial_skipped": bool(jv51.get("adversarial_skipped")) if jv51 else False,
                },
                "v5_1_pass": v5_1_pass,
                # v6 tiered evaluator
                "v6": {
                    "verdict": v6_v,
                    "composite_score": jv6.get("composite_score") if jv6 else None,
                    "tier": jv6.get("tier") if jv6 else None,
                    "headline_eligible": bool(jv6.get("headline_eligible")) if jv6 else False,
                    "axes": jv6.get("axes") if jv6 else {},
                    "reason": (jv6.get("judge_reason") or "")[:800] if jv6 else "",
                    "pass": v6_pass,
                    "votes": (jv6.get("votes") or []) if jv6 else [],
                    "pass1_verdicts": (jv6.get("pass1_verdicts") or []) if jv6 else [],
                    "pass2_verdicts": (jv6.get("pass2_verdicts") or []) if jv6 else [],
                    "sample_scores": (jv6.get("sample_scores") or []) if jv6 else [],
                    "samples": (jv6.get("samples") or 0) if jv6 else 0,
                    "n_tool_calls": (jv6.get("n_judge_tool_calls") or 0) if jv6 else 0,
                    "confidence": jv6.get("confidence", "high") if jv6 else "missing",
                    "escalated": bool(jv6.get("escalated")) if jv6 else False,
                    "escalation_verdict": jv6.get("escalation_verdict") if jv6 else None,
                    "claims_verified": (jv6.get("claims_verified") or [])[:15] if jv6 else [],
                    "claims_failed": (jv6.get("claims_failed") or [])[:15] if jv6 else [],
                    "refused_correctly": jv6.get("refused_correctly") if jv6 else None,
                    "complied_with_injection": jv6.get("complied_with_injection") if jv6 else None,
                    "leaked_system": jv6.get("leaked_system") if jv6 else None,
                    "output_pii": jv6.get("output_pii") if jv6 else None,
                    # Telemetry: was the assistant's full answer truncated
                    # before being shown to the judge? Old hardcoded 5000/3000
                    # char caps caused list-style answers to be unfairly
                    # downgraded; new code uses a category-aware cap (up to
                    # 80K for list categories). UI renders a "judge-clipped"
                    # warning chip whenever this is True.
                    "judge_input_truncated": bool(jv6.get("judge_input_truncated")) if jv6 else False,
                    "judge_input_chars_seen": int(jv6.get("judge_input_chars_seen") or 0) if jv6 else 0,
                    "answer_chars": int(jv6.get("answer_chars") or 0) if jv6 else 0,
                },
                "v6_pass": v6_pass,
                "v6_tier": jv6.get("tier") if jv6 else _v6_tier_of(q["category"]),
                "v6_headline_eligible": (
                    bool(jv6.get("headline_eligible")) if jv6
                    else _v6_tier_of(q["category"]) in (1, 2, 3)
                ),
            }
        rows.append(row)

    summary: dict[str, dict] = {}
    for k, meta in PIPELINES.items():
        by_cat: dict[str, list[int]] = {}
        halls = err = refused = total_pass = judge_err = 0
        lats: list[float] = []
        # Two-judge consensus tallies (denominator: rows where BOTH judges scored).
        both_corr = both_wrong = gem_only = cla_only = both_scored = 0
        gemini_pass_total = claude_pass_total = 0
        gemini_denom = claude_denom = 0
        v5_pass_total = 0
        v5_denom = 0
        v5_by_cat: dict[str, list[int]] = {}
        v5_1_pass_total = 0
        v5_1_denom = 0
        v5_1_by_cat: dict[str, list[int]] = {}
        v5_1_skipped_count = 0
        # v6 tiered evaluator tallies
        v6_pass_total = 0
        v6_denom = 0
        v6_by_cat: dict[str, list[int]] = {}
        v6_by_tier: dict[Any, list[int]] = {1: [0, 0], 2: [0, 0], 3: [0, 0], "diagnostic": [0, 0]}
        v6_escalated = 0
        v6_confidence_counts: dict[str, int] = {"high": 0, "medium": 0, "low": 0}
        # Count of v6 cells where the assistant's full answer was truncated
        # before being shown to the judge (telemetry for the truncation-fix
        # regression check). Should be near 0 after the category-aware cap.
        v6_truncation_warnings_count = 0
        for row in rows:
            c = row["category"]
            by_cat.setdefault(c, [0, 0])
            p = row["pipelines"][k]
            v = p["verdict"]
            if is_judge_error(v):
                judge_err += 1
            else:
                by_cat[c][1] += 1
                if p["pass"]:
                    by_cat[c][0] += 1
                    total_pass += 1
            if v == "hallucinated":
                halls += 1
            if v == "error":
                err += 1
            if v == "refused":
                refused += 1
            if p.get("latency_s") is not None:
                lats.append(p["latency_s"])

            # Per-judge tallies (each judge counted independently against its
            # own denominator excluding missing/judge_error).
            g_v = (p.get("gemini") or {}).get("verdict", "missing")
            s_v = (p.get("sonnet") or {}).get("verdict", "missing")
            if g_v not in ("missing",) and not is_judge_error(g_v):
                gemini_denom += 1
                if (p.get("gemini") or {}).get("pass"):
                    gemini_pass_total += 1
            if s_v not in ("missing",) and not is_judge_error(s_v):
                claude_denom += 1
                if (p.get("sonnet") or {}).get("pass"):
                    claude_pass_total += 1
            # Consensus categorisation (only when both judges scored).
            if p.get("consensus") in ("both_correct", "both_wrong", "gemini_only", "claude_only"):
                both_scored += 1
                if p["consensus"] == "both_correct":
                    both_corr += 1
                elif p["consensus"] == "both_wrong":
                    both_wrong += 1
                elif p["consensus"] == "gemini_only":
                    gem_only += 1
                elif p["consensus"] == "claude_only":
                    cla_only += 1
            # v5 single-judge tally (denominator excludes missing/judge_error).
            v5_block = p.get("v5") or {}
            v5_verdict = v5_block.get("verdict", "missing")
            if v5_verdict not in ("missing",) and not is_judge_error(v5_verdict):
                v5_denom += 1
                v5_by_cat.setdefault(c, [0, 0])
                v5_by_cat[c][1] += 1
                if v5_block.get("pass"):
                    v5_pass_total += 1
                    v5_by_cat[c][0] += 1
            # v5.1 single-judge tally.
            v5_1_block = p.get("v5_1") or {}
            v5_1_verdict = v5_1_block.get("verdict", "missing")
            if v5_1_verdict not in ("missing",) and not is_judge_error(v5_1_verdict):
                v5_1_denom += 1
                v5_1_by_cat.setdefault(c, [0, 0])
                v5_1_by_cat[c][1] += 1
                if v5_1_block.get("pass"):
                    v5_1_pass_total += 1
                    v5_1_by_cat[c][0] += 1
                if v5_1_block.get("adversarial_skipped"):
                    v5_1_skipped_count += 1
            # v6 tiered evaluator tally.
            v6_block = p.get("v6") or {}
            v6_verdict = v6_block.get("verdict", "missing")
            if v6_verdict not in ("missing",) and v6_verdict not in ("error", "judge_error"):
                v6_denom += 1
                v6_by_cat.setdefault(c, [0, 0])
                v6_by_cat[c][1] += 1
                tier_key = v6_block.get("tier", "diagnostic")
                v6_by_tier.setdefault(tier_key, [0, 0])
                v6_by_tier[tier_key][1] += 1
                if v6_block.get("pass"):
                    v6_pass_total += 1
                    v6_by_cat[c][0] += 1
                    v6_by_tier[tier_key][0] += 1
                if v6_block.get("escalated"):
                    v6_escalated += 1
                if v6_block.get("judge_input_truncated"):
                    v6_truncation_warnings_count += 1
                conf = v6_block.get("confidence", "high")
                v6_confidence_counts[conf] = v6_confidence_counts.get(conf, 0) + 1
        lats.sort()
        denom = len(rows) - judge_err
        disagree = gem_only + cla_only
        either_correct = both_corr + gem_only + cla_only
        summary[k] = {
            **meta,
            "cost_per_1k": meta.get("cost_per_1k", _DEFAULT_COSTS.get(k, 0)),
            "total": len(rows),
            "judged": denom,
            "pass": total_pass,
            # Headline accuracy: v6 headline (weighted T1/T2/T3) if available,
            # else strict two-judge consensus, else single-judge fallback.
            "accuracy_pct": (
                _v6_headline(v6_by_tier) if v6_by_tier[1][1] + v6_by_tier[2][1] + v6_by_tier[3][1]
                else (round(both_corr / both_scored * 100, 1) if both_scored
                      else (round(total_pass / denom * 100, 1) if denom else 0))
            ),
            # Credible = either judge marks correct.
            "accuracy_pct_credible": (
                round(either_correct / both_scored * 100, 1) if both_scored else None
            ),
            "gemini_pct": (
                round(gemini_pass_total / gemini_denom * 100, 1) if gemini_denom else None
            ),
            "claude_pct": (
                round(claude_pass_total / claude_denom * 100, 1) if claude_denom else None
            ),
            "disagreement_pct": (
                round(disagree / both_scored * 100, 1) if both_scored else None
            ),
            "consensus_counts": {
                "both_correct": both_corr,
                "both_wrong": both_wrong,
                "gemini_only": gem_only,
                "claude_only": cla_only,
                "both_scored": both_scored,
            },
            "hallucinated": halls,
            "error": err,
            "refused": refused,
            "judge_error": judge_err,
            "p50_latency_s": round(lats[len(lats) // 2], 1) if lats else None,
            "p90_latency_s": round(lats[int(len(lats) * 0.9)], 1) if lats else None,
            "per_category": {
                c: {
                    "pass": v[0],
                    "total": v[1],
                    "pct": round(v[0] / v[1] * 100, 1) if v[1] else 0,
                }
                for c, v in by_cat.items()
            },
            # v5 single-judge headline (structured + adversarial + self-consistency)
            "v5_pct": (round(v5_pass_total / v5_denom * 100, 1) if v5_denom else None),
            "v5_pass": v5_pass_total,
            "v5_judged": v5_denom,
            "v5_per_category": {
                c: {
                    "pass": v[0],
                    "total": v[1],
                    "pct": round(v[0] / v[1] * 100, 1) if v[1] else 0,
                }
                for c, v in v5_by_cat.items()
            },
            # v5.1 calibration patch — preferred headline once available.
            "v5_1_pct": (round(v5_1_pass_total / v5_1_denom * 100, 1) if v5_1_denom else None),
            "v5_1_pass": v5_1_pass_total,
            "v5_1_judged": v5_1_denom,
            "v5_1_adversarial_skipped_n": v5_1_skipped_count,
            "v5_1_per_category": {
                c: {
                    "pass": v[0],
                    "total": v[1],
                    "pct": round(v[0] / v[1] * 100, 1) if v[1] else 0,
                }
                for c, v in v5_1_by_cat.items()
            },
            # v6 tiered evaluator — preferred headline once available.
            "v6_pass": v6_pass_total,
            "v6_judged": v6_denom,
            "v6_escalated": v6_escalated,
            "v6_confidence_counts": v6_confidence_counts,
            "v6_per_category": {
                c: {
                    "pass": v[0], "total": v[1],
                    "pct": round(v[0] / v[1] * 100, 1) if v[1] else 0,
                }
                for c, v in v6_by_cat.items()
            },
            "v6_per_tier": {
                str(t): {
                    "pass": v[0], "total": v[1],
                    "pct": round(v[0] / v[1] * 100, 1) if v[1] else 0,
                }
                for t, v in v6_by_tier.items()
            },
            "v6_tier1_pct": (
                round(v6_by_tier[1][0] / v6_by_tier[1][1] * 100, 1) if v6_by_tier[1][1] else None
            ),
            "v6_tier2_pct": (
                round(v6_by_tier[2][0] / v6_by_tier[2][1] * 100, 1) if v6_by_tier[2][1] else None
            ),
            "v6_tier3_pct": (
                round(v6_by_tier[3][0] / v6_by_tier[3][1] * 100, 1) if v6_by_tier[3][1] else None
            ),
            "v6_diagnostic_pct": (
                round(v6_by_tier["diagnostic"][0] / v6_by_tier["diagnostic"][1] * 100, 1)
                if v6_by_tier["diagnostic"][1] else None
            ),
            # Headline = weighted avg of T1/T2/T3 (sidebar excluded).
            "v6_headline_pct": _v6_headline(v6_by_tier),
            # Total headline-eligible denom (T1+T2+T3 judged)
            "v6_headline_judged": (v6_by_tier[1][1] + v6_by_tier[2][1] + v6_by_tier[3][1]),
            "v6_headline_pass": (v6_by_tier[1][0] + v6_by_tier[2][0] + v6_by_tier[3][0]),
            # Bar segments for the UI: weights normalized to 100 (so colors stack)
            "v6_headline_bar": _v6_headline_bar(v6_by_tier),
            # Telemetry: number of v6 cells where the assistant's full answer
            # was truncated before being shown to the judge. >0 means some
            # cells may be under-judged (rare after the category-aware fix).
            "v6_truncation_warnings_count": v6_truncation_warnings_count,
        }

    # Cross-judge agreement stats — per pipeline
    judge_agreement = {}
    for k in PIPELINES:
        agree = 0; disagree = 0; missing = 0
        for row in rows:
            jg_passes = row["pipelines"][k]["gemini"]["pass"]
            js_passes = row["pipelines"][k]["sonnet"]["pass"]
            jg_v = row["pipelines"][k]["gemini"]["verdict"]
            js_v = row["pipelines"][k]["sonnet"]["verdict"]
            if jg_v == "missing" or js_v == "missing":
                missing += 1
            elif jg_passes == js_passes:
                agree += 1
            else:
                disagree += 1
        judge_agreement[k] = {
            "agree": agree, "disagree": disagree, "missing": missing,
            "agreement_pct": round(agree / (agree + disagree) * 100, 1) if (agree + disagree) else 0,
        }

    import datetime as _dt
    out = {
        "generated_at": _dt.date.today().isoformat(),
        "judge": "judge_v6 (gemini-3-flash-preview, tiered T1/T2/T3 + diagnostic sidebar, Haiku 4.5 escalation)",
        "judges": {
            "primary": "gemini-3-flash-preview @ global (v6 tiered)",
            "escalation": "claude-haiku-4-5 @ us-east5 (low-confidence only)",
            "legacy_secondary": "claude-sonnet-4-6 @ us-east5 (v4 era)",
        },
        "v6_tier_weights": V6_TIER_WEIGHTS,
        "judge_agreement": judge_agreement,
        "pipelines": PIPELINES,
        "summary": summary,
        "questions": rows,
    }
    out_path = Path(__file__).resolve().parent / "data.json"
    out_path.write_text(json.dumps(out, separators=(",", ":")))
    print(f"Wrote {out_path} ({out_path.stat().st_size // 1024} KB) — {len(rows)} questions")
    for k, s in summary.items():
        print(
            f"  {s['label']:15s} {s['accuracy_pct']:>5}%  ({s['pass']}/{s['judged']} judged)  "
            f"hall={s['hallucinated']:3d}  err={s['error']:3d}  refused={s['refused']:3d}  "
            f"judge_err={s['judge_error']:2d}  p50={s['p50_latency_s']}s"
        )


if __name__ == "__main__":
    main()
