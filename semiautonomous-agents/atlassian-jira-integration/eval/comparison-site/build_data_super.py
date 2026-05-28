"""Build comparison-site/data.json from the per-option judged runs.

Edit `PIPELINES` below to point at the latest run directory you want to surface
in the website. Then run `python eval/comparison-site/build_data.py` from the
repo root. The HTML page loads data.json from the same directory.
"""
from __future__ import annotations

import json
from pathlib import Path

# Public-facing option letter -> (run dir, jsonl letter, display metadata)
PIPELINES: dict[str, dict] = {
    "A": {
        "run": "super-20260521-121602-a",
        "letter": "a",
        "label": "Option A",
        "sub": "Custom MCP + ADK Agent (Vertex Agent Engine)",
        "model": "Gemini 2.5",
        "surface": "Agent picker (sidebar)",
    },
    "B": {
        "run": "20260521-101429-option-b-rovo-CLEAN",
        "letter": "b",
        "label": "Option B",
        "sub": "Atlassian-hosted Rovo MCP (37 tools) via GE streamAssist BYO_MCP",
        "model": "GE chat LLM + Rovo MCP (Atlassian-hosted)",
        "surface": "Main chat (BYO_MCP)",
    },
    "C": {
        "run": "super-20260521-121602-g",
        "letter": "g",
        "label": "Option C",
        "sub": "Custom MCP direct to GE (no ADK)",
        "model": "GE chat LLM + Custom MCP (Cloud Run, self-hosted)",
        "surface": "Main chat (BYO_MCP)",
    },
    "D": {
        "run": "20260519-203012-option-h-full",
        "letter": "h",
        "label": "Option D",
        "sub": "GE federated jira_cloud (no MCP, no Cloud Run)",
        "model": "GE built-in retrieval + chat LLM",
        "surface": "Main chat (federated)",
    },
    "E": {
        "run": "super-20260521-121602-i",
        "letter": "i",
        "label": "Option E ⭐",
        "sub": "google.genai tool-loop in Cloud Run, wrapped as BYO_MCP",
        "model": "gemini-3.1-flash-lite",
        "surface": "Main chat (BYO_MCP)",
    },
    "AL": {
        "run": "super-20260521-121602-al",
        "letter": "al",
        "label": "Option A-lite",
        "sub": "Same as A but on gemini-3.1-flash-lite (apples-to-apples vs E)",
        "model": "gemini-3.1-flash-lite",
        "surface": "Agent picker (sidebar)",
        "cost_per_1k": 5.30,
    },
    "AG": {
        "run": "super-20260521-121602-ag",
        "letter": "ag",
        "label": "Option A-Gemini3.5",
        "sub": "Same as A but on gemini-3.5-flash",
        "model": "gemini-3.5-flash",
        "surface": "Agent picker (sidebar)",
        "cost_per_1k": 25.00,
    },
    "EG": {
        "run": "super-20260521-121602-eg",
        "letter": "eg",
        "label": "Option E-Gemini3.5",
        "sub": "Same as E but on gemini-3.5-flash (same model as AG, no ADK)",
        "model": "gemini-3.5-flash",
        "surface": "Main chat (BYO_MCP)",
        "cost_per_1k": 20.00,
    },
    "CG": {
        "run": "super-20260521-121602-cg",
        "letter": "cg",
        "label": "Option C-Gemini3.5",
        "sub": "Same as C (BYO_MCP via streamAssist) but with explicit gemini-3.5-flash override",
        "model": "gemini-3.5-flash (via streamAssist generationSpec.modelId)",
        "surface": "Main chat (BYO_MCP)",
        "cost_per_1k": 4.00,
    },
    "DG": {
        "run": "20260521-104255-option-d-gemini35-CLEAN",
        "letter": "dg",
        "label": "Option D-Gemini3.5",
        "sub": "Same as D (federated, no MCP) but with explicit gemini-3.5-flash override",
        "model": "gemini-3.5-flash (via streamAssist generationSpec.modelId)",
        "surface": "Main chat (federated)",
        "cost_per_1k": 4.00,
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
      1. judged_<letter>_v4_<backend>.json   (semantic + tool-using judge v4)
      2. judged_<letter>_<backend>_v2.json   (golden-aware v2)
      3. judged_<letter>_<backend>.json      (legacy v1)
      4. judged_<letter>.json                (un-suffixed)
    """
    candidates = [
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


def load_judged_any(base: Path, run: str, letter: str, suffix: str) -> dict[str, dict]:
    """Load a specifically-named judged file (e.g. _sonnet, _gemini)."""
    p = base / "runs" / run / f"judged_{letter}{suffix}.json"
    if not p.exists():
        return {}
    return {x["id"]: x for x in json.load(open(p))}


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
        # super (judge_v3 + golden_super) takes precedence over all legacy variants.
        suffixes = [f"_super_{judge}", f"_v4_{judge}", f"_{judge}_v2", f"_{judge}"]
        # Allow sonnet alias to pick up claude-tagged files (judge_v3/v4 emit
        # _super_claude.json / _v4_claude.json under --backend claude).
        if judge == "sonnet":
            suffixes = ["_super_claude", "_v4_claude"] + suffixes
        for suffix in suffixes:
            d = load_judged_any(eval_dir, run, letter, suffix)
            if d:
                return d
        return {}
    judg_gemini = {k: _load_with_fallback(v["run"], v["letter"], "gemini") for k, v in PIPELINES.items()}
    judg_sonnet = {k: _load_with_fallback(v["run"], v["letter"], "sonnet") for k, v in PIPELINES.items()}
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
            primary = jg if jg else js  # gemini first; claude fallback if missing
            # judge_v4 emits `score` (0-1); legacy emits `correctness`.
            def _corr(j):
                if not j: return None
                if j.get("correctness") is not None: return j.get("correctness")
                if j.get("score") is not None: return j.get("score")
                return None
            gem_v = jg.get("verdict", "missing") if jg else "missing"
            son_v = js.get("verdict", "missing") if js else "missing"
            gem_pass = is_pass(gem_v, q["category"]) if jg else False
            son_pass = is_pass(son_v, q["category"]) if js else False
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
            row["pipelines"][k] = {
                "answer": r.get("answer", "") or "",
                # Primary verdict (used by existing UI)
                "verdict": primary.get("verdict", "missing"),
                "correctness": _corr(primary),
                "latency_s": primary.get("latency_s", r.get("elapsed_s")),
                "n_tool_calls": primary.get("n_tool_calls"),
                "cited_keys": (primary.get("cited_keys") or [])[:10],
                "judge_reason": primary.get("judge_reason", ""),
                "error": r.get("error"),
                "hallucination_rate": primary.get("hallucination_rate"),
                "pass": is_pass(primary.get("verdict", "missing"), q["category"]),
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
            # Headline accuracy = strict (both judges agree it's correct)
            # when both judges scored; otherwise falls back to single-judge.
            "accuracy_pct": (
                round(both_corr / both_scored * 100, 1) if both_scored
                else (round(total_pass / denom * 100, 1) if denom else 0)
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

    out = {
        "generated_at": "2026-05-21",
        "judge": "gemini-3.5-flash + claude-sonnet-4-6 (two-judge consensus; judge_v4 with live Jira tool access)",
        "judges": {
            "primary": "gemini-3.5-flash @ global",
            "secondary": "claude-sonnet-4-6 @ us-east5",
        },
        "judge_agreement": judge_agreement,
        "pipelines": PIPELINES,
        "summary": summary,
        "questions": rows,
    }
    # Default: data_super.json (so this doesn't clobber the v2 dashboard's data.json).
    # Override with DATA_OUT env var if you want to write data.json instead.
    import os as _os
    out_name = _os.environ.get("DATA_OUT", "data_super.json")
    out_path = Path(__file__).resolve().parent / out_name
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
