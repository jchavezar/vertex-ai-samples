"""Render an HTML side-by-side comparison report for the two pipelines.

Reads:  runs/<ts>/judged_a.json  +  runs/<ts>/judged_b.json
Writes: runs/<ts>/report.html  +  runs/<ts>/summary.json

Pure inline-CSS HTML, no JS, no Jinja, no external assets. Adapted from
docparse/eval/ga_comparison.py with sections specific to a Jira-agent eval.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import statistics
from collections import Counter, defaultdict
from html import escape
from pathlib import Path
from typing import Any


VERDICTS = ["correct", "partial", "wrong", "hallucinated", "refused", "error"]
VERDICT_COLORS = {
    "correct": "#10b981",
    "partial": "#f59e0b",
    "wrong": "#ef4444",
    "hallucinated": "#dc2626",
    "refused": "#6b7280",
    "error": "#1f2937",
}


def _safe_avg(xs: list[float | None]) -> float | None:
    vals = [x for x in xs if x is not None]
    return sum(vals) / len(vals) if vals else None


def _pct(x: float | None) -> str:
    return "—" if x is None else f"{x*100:.1f}%"


def aggregate(judged: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(judged)
    ok = [j for j in judged if j["verdict"] != "error"]
    correctness = _safe_avg([j["correctness"] for j in ok]) or 0.0
    completeness = _safe_avg([j["completeness"] for j in ok]) or 0.0
    citation = _safe_avg([j.get("citation_accuracy") for j in ok])
    halluc = _safe_avg([j.get("hallucination_rate") for j in ok])
    jql = _safe_avg([j.get("jql_correctness") for j in ok])
    paginate = _safe_avg([j.get("pagination_completeness") for j in ok if j.get("category") == "pagination-required"])
    refusal = _safe_avg([j.get("refusal_correctness") for j in ok if j.get("category") == "refusal-test"])
    eff = _safe_avg([j.get("tool_efficiency") for j in ok])
    lat = sorted([j["latency_s"] for j in ok if j.get("latency_s")])
    p50 = lat[len(lat) // 2] if lat else 0.0
    p95 = lat[min(len(lat) - 1, int(len(lat) * 0.95))] if lat else 0.0
    avg_lat = sum(lat) / len(lat) if lat else 0.0
    composite = (correctness + completeness) / 2
    verdicts = Counter(j["verdict"] for j in judged)
    return {
        "n": n, "n_ok": len(ok), "composite": composite,
        "correctness": correctness, "completeness": completeness,
        "citation_accuracy": citation, "hallucination_rate": halluc,
        "jql_correctness": jql, "pagination_completeness": paginate,
        "refusal_correctness": refusal, "tool_efficiency": eff,
        "latency_p50": p50, "latency_p95": p95, "latency_avg": avg_lat,
        "verdicts": {v: verdicts.get(v, 0) for v in VERDICTS},
    }


def by_category(judged: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for j in judged:
        buckets[j.get("category", "unknown")].append(j)
    return {cat: aggregate(qs) for cat, qs in buckets.items()}


def latency_buckets(judged: list[dict[str, Any]], bins: int = 10) -> list[int]:
    vals = [j["latency_s"] for j in judged if j.get("latency_s")]
    if not vals:
        return [0] * bins
    mx = max(vals)
    edges = [mx * (i + 1) / bins for i in range(bins)]
    counts = [0] * bins
    for v in vals:
        for i, e in enumerate(edges):
            if v <= e:
                counts[i] += 1
                break
    return counts


# --- HTML helpers ---

def bar(value: float | None, color: str = "#3b82f6", max_v: float = 1.0) -> str:
    if value is None:
        return '<span class="muted">—</span>'
    pct = max(0.0, min(1.0, value / max_v)) * 100
    return (
        f'<div class="bar"><div class="bar-fill" style="width:{pct:.1f}%;background:{color}"></div>'
        f'<span class="bar-label">{value*100:.1f}%</span></div>'
    )


def comp_bar(va: float | None, vb: float | None, max_v: float = 1.0) -> str:
    return (
        '<div class="comp"><div class="comp-side">'
        + bar(va, "#3b82f6", max_v)
        + '</div><div class="comp-side">'
        + bar(vb, "#a855f7", max_v)
        + '</div></div>'
    )


def _load_answers(run_dir: Path, pipeline: str) -> dict[str, dict[str, Any]]:
    """Pull answer text + tool calls out of responses_<pipeline>.jsonl by id."""
    path = run_dir / f"responses_{pipeline}.jsonl"
    out: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return out
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
            out[r["id"]] = r
        except Exception:
            pass
    return out


def render(run_dir: Path, judged_a: list[dict], judged_b: list[dict],
           qs_by_id: dict[str, dict]) -> tuple[str, dict[str, Any]]:
    # Pipeline labels — overridable via env so the same data can be re-rendered
    # with different framings (e.g., Gemini vs Claude+Rovo).
    label_a = os.environ.get("REPORT_LABEL_A", "Option A — Custom MCP Portal (Vertex AI Agent + Gemini)")
    label_b = os.environ.get("REPORT_LABEL_B", "Option B — Atlassian Rovo Direct MCP")
    short_a = os.environ.get("REPORT_SHORT_A", "Option A")
    short_b = os.environ.get("REPORT_SHORT_B", "Option B")

    agg_a = aggregate(judged_a)
    agg_b = aggregate(judged_b)
    cat_a = by_category(judged_a)
    cat_b = by_category(judged_b)
    all_cats = sorted(set(cat_a) | set(cat_b))
    by_id_a = {j["id"]: j for j in judged_a}
    by_id_b = {j["id"]: j for j in judged_b}

    summary = {
        "run_dir": str(run_dir),
        "n_questions": max(agg_a["n"], agg_b["n"]),
        "option_a": agg_a, "option_b": agg_b,
        "categories": {cat: {"a": cat_a.get(cat), "b": cat_b.get(cat)} for cat in all_cats},
    }

    # Headline scoreboard
    headline_rows = [
        ("Composite", agg_a["composite"], agg_b["composite"]),
        ("Correctness", agg_a["correctness"], agg_b["correctness"]),
        ("Completeness", agg_a["completeness"], agg_b["completeness"]),
        ("Citation accuracy", agg_a["citation_accuracy"], agg_b["citation_accuracy"]),
        ("Hallucination rate (lower is better)", agg_a["hallucination_rate"], agg_b["hallucination_rate"]),
        ("JQL correctness", agg_a["jql_correctness"], agg_b["jql_correctness"]),
        ("Pagination completeness", agg_a["pagination_completeness"], agg_b["pagination_completeness"]),
        ("Refusal correctness", agg_a["refusal_correctness"], agg_b["refusal_correctness"]),
        ("Tool efficiency", agg_a["tool_efficiency"], agg_b["tool_efficiency"]),
    ]
    head_html = f'<table class="scoreboard"><tr><th></th><th>{escape(short_a)}</th><th>{escape(short_b)}</th></tr>'
    for label, va, vb in headline_rows:
        head_html += f'<tr><td>{escape(label)}</td><td>{_pct(va)}</td><td>{_pct(vb)}</td></tr>'
    head_html += (
        f'<tr><td>Latency p50 / p95 / avg</td>'
        f'<td>{agg_a["latency_p50"]:.1f}s / {agg_a["latency_p95"]:.1f}s / {agg_a["latency_avg"]:.1f}s</td>'
        f'<td>{agg_b["latency_p50"]:.1f}s / {agg_b["latency_p95"]:.1f}s / {agg_b["latency_avg"]:.1f}s</td>'
        '</tr></table>'
    )

    # Verdict bars
    verdict_html = '<div class="verdicts">'
    for label, agg in ((short_a, agg_a), (short_b, agg_b)):
        total = sum(agg["verdicts"].values()) or 1
        verdict_html += f'<div class="verdict-col"><h4>{label}</h4>'
        for v in VERDICTS:
            n = agg["verdicts"][v]
            pct = n / total * 100
            verdict_html += (
                f'<div class="verdict-row"><span class="verdict-label">{v}</span>'
                f'<div class="bar"><div class="bar-fill" style="width:{pct:.1f}%;background:{VERDICT_COLORS[v]}"></div>'
                f'<span class="bar-label">{n} ({pct:.0f}%)</span></div></div>'
            )
        verdict_html += '</div>'
    verdict_html += '</div>'

    # Per-category bars
    cat_rows = f'<table class="cats"><tr><th>Category</th><th>n</th><th>{escape(short_a)} composite</th><th>{escape(short_b)} composite</th><th>Δ</th></tr>'
    for cat in all_cats:
        a = cat_a.get(cat, {"composite": None, "n": 0})
        b = cat_b.get(cat, {"composite": None, "n": 0})
        delta = (a["composite"] or 0) - (b["composite"] or 0)
        cat_rows += (
            f'<tr><td>{escape(cat)}</td><td>{max(a["n"], b["n"])}</td>'
            f'<td>{bar(a["composite"], "#3b82f6")}</td>'
            f'<td>{bar(b["composite"], "#a855f7")}</td>'
            f'<td>{delta*100:+.1f}pp</td></tr>'
        )
    cat_rows += '</table>'

    # Latency histogram (10 buckets, side-by-side)
    bk_a = latency_buckets(judged_a)
    bk_b = latency_buckets(judged_b)
    mx = max(max(bk_a, default=0), max(bk_b, default=0)) or 1
    hist_html = '<div class="hist">'
    for i in range(10):
        ha = bk_a[i] / mx * 100
        hb = bk_b[i] / mx * 100
        hist_html += (
            f'<div class="hist-bin"><div class="hist-bars">'
            f'<div class="hist-bar a" style="height:{ha:.0f}%" title="A: {bk_a[i]}"></div>'
            f'<div class="hist-bar b" style="height:{hb:.0f}%" title="B: {bk_b[i]}"></div>'
            f'</div><div class="hist-label">b{i+1}</div></div>'
        )
    hist_html += '</div>'

    # Win/loss matrix (correctness)
    a_wins = b_wins = ties = 0
    for qid in by_id_a.keys() & by_id_b.keys():
        ca = by_id_a[qid]["correctness"]
        cb = by_id_b[qid]["correctness"]
        if abs(ca - cb) < 0.05:
            ties += 1
        elif ca > cb:
            a_wins += 1
        else:
            b_wins += 1
    wl_html = (
        f'<div class="wl"><div class="wl-cell wl-a">{a_wins}<br><small>A wins</small></div>'
        f'<div class="wl-cell wl-tie">{ties}<br><small>ties</small></div>'
        f'<div class="wl-cell wl-b">{b_wins}<br><small>B wins</small></div></div>'
    )

    # Verdict confusion matrix (A x B)
    confusion: dict[tuple[str, str], int] = Counter()
    for qid in by_id_a.keys() & by_id_b.keys():
        confusion[(by_id_a[qid]["verdict"], by_id_b[qid]["verdict"])] += 1
    conf_html = '<table class="confusion"><tr><th>A ↓ / B →</th>' + "".join(f'<th>{v}</th>' for v in VERDICTS) + '</tr>'
    for va in VERDICTS:
        conf_html += f'<tr><th>{va}</th>'
        for vb in VERDICTS:
            n = confusion.get((va, vb), 0)
            cell = f'<td class="conf-cell" style="background:rgba(59,130,246,{min(0.7, n/40)})">{n}</td>'
            conf_html += cell
        conf_html += '</tr>'
    conf_html += '</table>'

    # Hallucination spotlight
    halluc_cases: list[tuple[str, dict, dict]] = []
    for qid in by_id_a.keys() | by_id_b.keys():
        a = by_id_a.get(qid)
        b = by_id_b.get(qid)
        worst = max(((a or {}).get("hallucination_rate") or 0), ((b or {}).get("hallucination_rate") or 0))
        if worst > 0.2:
            halluc_cases.append((qid, a or {}, b or {}))
    halluc_cases.sort(key=lambda x: -max((x[1].get("hallucination_rate") or 0), (x[2].get("hallucination_rate") or 0)))
    halluc_cases = halluc_cases[:10]
    halluc_html = '<table class="halluc"><tr><th>id</th><th>question</th><th>A halluc</th><th>B halluc</th></tr>'
    for qid, a, b in halluc_cases:
        q = qs_by_id.get(qid, {})
        halluc_html += (
            f'<tr><td>{qid}</td><td>{escape((q.get("q") or "")[:120])}</td>'
            f'<td>{_pct(a.get("hallucination_rate"))}</td>'
            f'<td>{_pct(b.get("hallucination_rate"))}</td></tr>'
        )
    halluc_html += '</table>' if halluc_cases else '<p class="muted">No hallucinations &gt; 20% detected. Nice.</p>'

    # Pull answer text from responses_*.jsonl (judged JSON only has scores).
    ans_a_by_id = _load_answers(run_dir, "a")
    ans_b_by_id = _load_answers(run_dir, "b")

    def _render_sample_block(qid: str) -> str:
        q = qs_by_id.get(qid, {})
        a = by_id_a.get(qid, {})
        b = by_id_b.get(qid, {})
        rA = ans_a_by_id.get(qid, {})
        rB = ans_b_by_id.get(qid, {})
        ans_a = (rA.get("answer") or rA.get("error") or "(no answer captured)")[:2500]
        ans_b = (rB.get("answer") or rB.get("error") or "(no answer captured)")[:2500]
        oracle_line = ""
        if q.get("expected_keys") is not None:
            ek = q.get("expected_keys", [])
            ek_preview = ", ".join(ek[:6]) + (f" …(+{len(ek)-6})" if len(ek) > 6 else "")
            oracle_line += f"<b>Expected keys:</b> {escape(ek_preview) or '<i>none</i>'}<br>"
        if q.get("expected_count") is not None:
            oracle_line += f"<b>Expected count:</b> {q['expected_count']}<br>"
        if q.get("jql"):
            oracle_line += f"<b>Oracle JQL:</b> <code>{escape(q['jql'])}</code><br>"
        if q.get("expected_themes"):
            oracle_line += f"<b>Expected themes:</b> {escape(', '.join(q['expected_themes']))}<br>"
        return (
            f'<details class="sample"><summary><b>{qid}</b> · '
            f'<span class="cat">{escape(q.get("category",""))}</span> · '
            f'A:<span class="vbadge v-{a.get("verdict","?")}">{a.get("verdict","?")}</span> '
            f'B:<span class="vbadge v-{b.get("verdict","?")}">{b.get("verdict","?")}</span> · '
            f'{escape((q.get("q") or "")[:160])}'
            f'</summary>'
            f'<div class="sample-oracle">{oracle_line}</div>'
            f'<div class="sample-body">'
            f'<div class="sample-col"><h4>{escape(short_a)} · <span class="vbadge v-{a.get("verdict","?")}">{a.get("verdict","?")}</span> · '
            f'{a.get("latency_s",0):.1f}s · {a.get("n_tool_calls",0)} tool calls</h4>'
            f'<pre>{escape(ans_a)}</pre>'
            f'<p class="muted"><b>Cited:</b> {escape(", ".join(a.get("cited_keys", [])[:8]) or "—")}</p>'
            f'<p class="muted"><b>Judge:</b> {escape(a.get("judge_reason",""))}</p></div>'
            f'<div class="sample-col"><h4>{escape(short_b)} · <span class="vbadge v-{b.get("verdict","?")}">{b.get("verdict","?")}</span> · '
            f'{b.get("latency_s",0):.1f}s · {b.get("n_tool_calls",0)} tool calls</h4>'
            f'<pre>{escape(ans_b)}</pre>'
            f'<p class="muted"><b>Cited:</b> {escape(", ".join(b.get("cited_keys", [])[:8]) or "—")}</p>'
            f'<p class="muted"><b>Judge:</b> {escape(b.get("judge_reason",""))}</p>'
            f'</div></div></details>'
        )

    # Failure spotlight — every question where AT LEAST ONE pipeline lost.
    failure_verdicts = {"wrong", "hallucinated", "error"}
    common_ids = sorted(by_id_a.keys() & by_id_b.keys())
    failure_ids = [qid for qid in common_ids
                   if by_id_a.get(qid, {}).get("verdict") in failure_verdicts
                   or by_id_b.get(qid, {}).get("verdict") in failure_verdicts]
    failures_html = "".join(_render_sample_block(qid) for qid in failure_ids)
    failures_count_html = f'<p class="muted">{len(failure_ids)} of {len(common_ids)} questions had at least one pipeline fail. Click to expand each.</p>'

    # Random sample (for spot-checking correct answers too).
    random.seed(42)
    sample_ids = random.sample(common_ids, min(20, len(common_ids)))
    samples_html = "".join(_render_sample_block(qid) for qid in sample_ids)

    # Failure-mode taxonomy
    fail_html = '<table class="fail"><tr><th>Category</th>' + "".join(f'<th>A {v}</th><th>B {v}</th>' for v in ["wrong", "hallucinated", "refused", "error"]) + '</tr>'
    for cat in all_cats:
        a_cnt = Counter(j["verdict"] for j in judged_a if j.get("category") == cat)
        b_cnt = Counter(j["verdict"] for j in judged_b if j.get("category") == cat)
        fail_html += f'<tr><td>{escape(cat)}</td>'
        for v in ["wrong", "hallucinated", "refused", "error"]:
            fail_html += f'<td>{a_cnt.get(v, 0)}</td><td>{b_cnt.get(v, 0)}</td>'
        fail_html += '</tr>'
    fail_html += '</table>'

    css = """
    * {margin:0;padding:0;box-sizing:border-box}
    body {font-family:-apple-system,BlinkMacSystemFont,'Inter',sans-serif;background:#f8fafc;color:#0f172a;padding:2rem}
    .container {max-width:1280px;margin:0 auto}
    .hero {background:linear-gradient(135deg,#3b82f6,#a855f7);color:#fff;padding:2rem;border-radius:12px;margin-bottom:2rem}
    .hero h1 {font-size:2rem}
    .hero p {opacity:0.9;margin-top:0.5rem}
    section {background:#fff;padding:1.5rem 2rem;border-radius:12px;margin-bottom:1.5rem;box-shadow:0 1px 3px rgba(0,0,0,0.05)}
    section h2 {color:#0f172a;font-size:1.25rem;margin-bottom:1rem;border-bottom:2px solid #f1f5f9;padding-bottom:0.5rem}
    .scoreboard, .cats, .confusion, .fail, .halluc {width:100%;border-collapse:collapse;font-size:0.9rem}
    .scoreboard td, .scoreboard th, .cats td, .cats th, .confusion td, .confusion th, .fail td, .fail th, .halluc td, .halluc th {
        padding:0.5rem 0.75rem;text-align:left;border-bottom:1px solid #f1f5f9}
    .scoreboard th, .cats th, .confusion th, .fail th, .halluc th {background:#f8fafc;font-weight:600}
    .bar {position:relative;background:#f1f5f9;border-radius:6px;height:18px;display:inline-block;width:100%;min-width:120px}
    .bar-fill {height:100%;border-radius:6px;transition:width 0.3s}
    .bar-label {position:absolute;left:8px;top:0;line-height:18px;font-size:0.75rem;color:#0f172a;font-weight:600}
    .verdicts {display:grid;grid-template-columns:1fr 1fr;gap:2rem}
    .verdict-col h4 {color:#475569;margin-bottom:0.5rem;font-size:0.9rem;text-transform:uppercase;letter-spacing:0.05em}
    .verdict-row {display:grid;grid-template-columns:120px 1fr;gap:0.75rem;align-items:center;margin-bottom:0.4rem}
    .verdict-label {font-size:0.85rem;color:#334155}
    .hist {display:grid;grid-template-columns:repeat(10,1fr);gap:0.5rem;height:160px;align-items:end}
    .hist-bin {display:flex;flex-direction:column;align-items:center;height:100%}
    .hist-bars {display:flex;align-items:end;gap:2px;height:140px;width:100%}
    .hist-bar {flex:1;border-radius:3px 3px 0 0;min-height:2px}
    .hist-bar.a {background:#3b82f6}
    .hist-bar.b {background:#a855f7}
    .hist-label {font-size:0.7rem;color:#94a3b8;margin-top:4px}
    .wl {display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem;text-align:center}
    .wl-cell {padding:1.5rem;border-radius:8px;font-size:2rem;font-weight:700}
    .wl-a {background:#dbeafe;color:#1e3a8a}
    .wl-tie {background:#f1f5f9;color:#475569}
    .wl-b {background:#f3e8ff;color:#581c87}
    .wl-cell small {display:block;font-size:0.75rem;font-weight:400;margin-top:0.25rem}
    .conf-cell {text-align:center;font-weight:600}
    details.sample {border:1px solid #e2e8f0;border-radius:8px;padding:0.75rem 1rem;margin-bottom:0.5rem}
    details.sample summary {cursor:pointer;font-size:0.9rem}
    details.sample .cat {color:#3b82f6;font-weight:600}
    .sample-body {display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:1rem}
    .sample-col h4 {font-size:0.85rem;color:#475569;margin-bottom:0.5rem}
    .sample-col pre {background:#f8fafc;padding:0.75rem;border-radius:6px;font-size:0.8rem;white-space:pre-wrap;max-height:300px;overflow:auto;border:1px solid #e2e8f0}
    .muted {color:#94a3b8;font-size:0.8rem;margin-top:0.5rem}
    .vbadge {display:inline-block;padding:1px 8px;border-radius:10px;font-size:0.75rem;font-weight:700;text-transform:uppercase}
    .v-correct {background:#d1fae5;color:#065f46}
    .v-partial {background:#fef3c7;color:#92400e}
    .v-wrong {background:#fee2e2;color:#991b1b}
    .v-hallucinated {background:#fecaca;color:#7f1d1d;border:1px solid #b91c1c}
    .v-refused {background:#e5e7eb;color:#374151}
    .v-error {background:#1f2937;color:#f9fafb}
    .sample-oracle {background:#fafafa;border-left:3px solid #3b82f6;padding:0.75rem 1rem;margin-top:0.75rem;font-size:0.8rem;line-height:1.6}
    .sample-oracle code {background:#e2e8f0;padding:1px 6px;border-radius:3px;font-size:0.75rem}
    """

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Comparative Eval — {short_a} vs {short_b}</title>
<style>{css}</style></head><body><div class="container">
<div class="hero">
  <h1>Comparative Jira-AI Eval</h1>
  <h2 style="font-size:1.1rem;font-weight:400;opacity:0.95;margin-top:0.5rem">{short_a} <span style="opacity:0.7">vs</span> {short_b}</h2>
  <p>{summary['n_questions']} grounded questions · run dir <code>{escape(str(run_dir))}</code></p>
  <p style="font-size:0.85rem;opacity:0.8;margin-top:0.75rem">{escape(label_a)}<br>{escape(label_b)}</p>
</div>

<section><h2>Headline Scoreboard</h2>{head_html}</section>

<section><h2>Verdict Distribution</h2>{verdict_html}</section>

<section><h2>Per-Category Composite</h2>{cat_rows}</section>

<section><h2>Latency Distribution (10 buckets, side-by-side)</h2>{hist_html}
  <p class="muted"><span style="display:inline-block;width:12px;height:12px;background:#3b82f6;margin-right:4px"></span> {escape(short_a)}
  &nbsp;&nbsp;<span style="display:inline-block;width:12px;height:12px;background:#a855f7;margin-right:4px"></span> {escape(short_b)}</p>
</section>

<section><h2>Win / Loss (correctness, common questions)</h2>{wl_html}</section>

<section><h2>Verdict Confusion Matrix</h2>{conf_html}</section>

<section><h2>Hallucination Spotlight (top 10)</h2>{halluc_html}
<p class="muted">"Hallucination" = cited issue keys NOT returned by any tool call (or non-existent in Jira if tool-call inspection unavailable). For Jira agents this is the failure mode that matters: plausible-but-fake keys mislead users.</p>
</section>

<section><h2>Failure-Mode Taxonomy by Category</h2>{fail_html}</section>

<section><h2>Failures — every question with at least one pipeline mistake</h2>
{failures_count_html}
{failures_html}
</section>

<section><h2>Spot-Check (20 random answers)</h2>{samples_html}</section>

<section><h2>Methodology</h2>
<p>10 dimensions per question. Deterministic dimensions (correctness for jql-derivable Qs, completeness, citation accuracy, hallucination rate, pagination completeness, refusal correctness, tool efficiency, latency) computed from the runner's structured output and the Jira REST oracle. Two analytical dimensions (analytical_correctness, jql_correctness) use Claude Opus on Vertex.</p>
<p>Verdicts: <code>correct</code> · <code>partial</code> · <code>wrong</code> · <code>hallucinated</code> · <code>refused</code> · <code>error</code>. The <code>hallucinated</code> bucket is added because plausible-but-fake issue keys are the critical failure mode for AI ticketing assistants.</p>
<p>Full methodology: see <code>eval/README.md</code> and <code>eval/question_categories.md</code>.</p>
</section>

<script type="application/json" id="summary">{json.dumps(summary, default=str)}</script>
</div></body></html>"""
    return html, summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, help="run dir, e.g. runs/20260507-1234")
    ap.add_argument("--questions", default="questions/main.json")
    args = ap.parse_args()
    run_dir = Path(args.run)
    judged_a = json.loads((run_dir / "judged_a.json").read_text())
    judged_b = json.loads((run_dir / "judged_b.json").read_text())
    qs_path = run_dir / "questions.json"
    if not qs_path.exists():
        qs_path = Path(args.questions)
    qs_by_id = {q["id"]: q for q in json.loads(qs_path.read_text())}
    html, summary = render(run_dir, judged_a, judged_b, qs_by_id)
    (run_dir / "report.html").write_text(html)
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(f"Wrote {run_dir / 'report.html'} and {run_dir / 'summary.json'}")


if __name__ == "__main__":
    main()
