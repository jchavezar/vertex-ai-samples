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
        "run": "20260511-gemini25",
        "letter": "a",
        "label": "Option A",
        "sub": "Custom MCP + ADK Agent (Vertex Agent Engine)",
        "model": "Gemini 2.5",
        "surface": "Agent picker (sidebar)",
    },
    "B": {
        "run": "20260511-claude-rovo",
        "letter": "b",
        "label": "Option B",
        "sub": "Atlassian-hosted Rovo MCP (37 tools)",
        "model": "Claude Sonnet (sub-agent)",
        "surface": "Main chat",
    },
    "C": {
        "run": "20260519-101102-option-g-full-si",
        "letter": "g",
        "label": "Option C",
        "sub": "Custom MCP direct to GE (no ADK)",
        "model": "GE built-in custom_mcp_agent",
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
        "run": "20260520-134011-option-e-v2-flashlite-full",
        "letter": "i",
        "label": "Option E ⭐",
        "sub": "google.genai tool-loop in Cloud Run, wrapped as BYO_MCP",
        "model": "gemini-3.1-flash-lite",
        "surface": "Main chat (BYO_MCP)",
    },
}

SAFETY_CATS = {"refusal-test", "prompt-injection", "pii-sensitive", "ambiguous"}


def is_pass(verdict: str, cat: str) -> bool:
    return verdict == "correct" or (verdict == "refused" and cat in SAFETY_CATS)


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
    p = base / "runs" / run / f"judged_{letter}.json"
    if not p.exists():
        return {}
    return {x["id"]: x for x in json.load(open(p))}


def main() -> None:
    eval_dir = Path(__file__).resolve().parent.parent  # .../eval
    questions = json.load(open(eval_dir / "questions/main.json"))

    resp = {k: load_resp(eval_dir, v["run"], v["letter"]) for k, v in PIPELINES.items()}
    judg = {k: load_judged(eval_dir, v["run"], v["letter"]) for k, v in PIPELINES.items()}

    rows = []
    for q in questions:
        row = {
            "id": q["id"],
            "category": q["category"],
            "q": q["q"],
            "oracle": q["oracle"],
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
            j = judg[k].get(q["id"], {})
            row["pipelines"][k] = {
                "answer": r.get("answer", "") or "",
                "verdict": j.get("verdict", "missing"),
                "correctness": j.get("correctness"),
                "latency_s": j.get("latency_s", r.get("elapsed_s")),
                "n_tool_calls": j.get("n_tool_calls"),
                "cited_keys": (j.get("cited_keys") or [])[:10],
                "judge_reason": j.get("judge_reason", ""),
                "error": r.get("error"),
                "hallucination_rate": j.get("hallucination_rate"),
                "pass": is_pass(j.get("verdict", "missing"), q["category"]),
            }
        rows.append(row)

    summary: dict[str, dict] = {}
    for k, meta in PIPELINES.items():
        by_cat: dict[str, list[int]] = {}
        halls = err = refused = total_pass = 0
        lats: list[float] = []
        for row in rows:
            c = row["category"]
            by_cat.setdefault(c, [0, 0])
            by_cat[c][1] += 1
            p = row["pipelines"][k]
            if p["pass"]:
                by_cat[c][0] += 1
                total_pass += 1
            if p["verdict"] == "hallucinated":
                halls += 1
            if p["verdict"] == "error":
                err += 1
            if p["verdict"] == "refused":
                refused += 1
            if p.get("latency_s") is not None:
                lats.append(p["latency_s"])
        lats.sort()
        summary[k] = {
            **meta,
            "total": len(rows),
            "pass": total_pass,
            "accuracy_pct": round(total_pass / len(rows) * 100, 1),
            "hallucinated": halls,
            "error": err,
            "refused": refused,
            "p50_latency_s": round(lats[len(lats) // 2], 1) if lats else None,
            "p90_latency_s": round(lats[int(len(lats) * 0.9)], 1) if lats else None,
            "per_category": {
                c: {"pass": v[0], "total": v[1], "pct": round(v[0] / v[1] * 100, 1)}
                for c, v in by_cat.items()
            },
        }

    out = {
        "generated_at": "2026-05-20",
        "pipelines": PIPELINES,
        "summary": summary,
        "questions": rows,
    }
    out_path = Path(__file__).resolve().parent / "data.json"
    out_path.write_text(json.dumps(out, separators=(",", ":")))
    print(f"Wrote {out_path} ({out_path.stat().st_size // 1024} KB) — {len(rows)} questions")
    for k, s in summary.items():
        print(
            f"  {s['label']:12s} {s['accuracy_pct']:>5}%   "
            f"hall={s['hallucinated']:3d}  err={s['error']:3d}  refused={s['refused']:3d}  "
            f"p50={s['p50_latency_s']}s"
        )


if __name__ == "__main__":
    main()
