"""Generate a sanitized RESULTS.md from summary-only judged data.

This version works with the redacted eval data (questions with [REDACTED] content
and judged files with only composite scores, no per-question verdicts).
"""
import json
from pathlib import Path
from datetime import date

HERE = Path(__file__).resolve().parent
JUDGED_DIR = HERE / "judged"
OUT = HERE / "RESULTS.md"

STRATEGY_ORDER = ["rag_md_v2", "rag_md", "digital_v2", "digital", "ocr", "layout", "digital_200", "rag_pdf"]

def bar(pct, width=20):
    """Render a percent as a Unicode block bar."""
    filled = round(pct / 100 * width)
    return "█" * filled + "░" * (width - filled)

# Load summary stats
summaries = {}
for f in JUDGED_DIR.glob("*.json"):
    summaries[f.stem] = json.load(open(f))

# Build doc
lines = []

# === Header ===
top = summaries["rag_md_v2"]
top_comp = top["composite_score"]

lines.append('<div align="center">')
lines.append("")
lines.append("# 🏆 docparse — Full Evaluation Results")
lines.append("")
lines.append("**216 questions · 8 strategies · judged by Claude Opus 4.5**")
lines.append("")
lines.append(f"![winner](https://img.shields.io/badge/winner-rag__md__v2-1A73E8?style=for-the-badge)")
lines.append(f"![score](https://img.shields.io/badge/composite-{top_comp}%25-137333?style=for-the-badge)")
lines.append(f"![delta](https://img.shields.io/badge/%CE%94_vs_baseline-%2B11.9pts-EA8600?style=for-the-badge)")
lines.append(f"![questions](https://img.shields.io/badge/questions-216-5A6373?style=for-the-badge)")
lines.append("")
lines.append(f"<sub>Last run: {date.today().isoformat()}  ·  Eval corpus: 2 enterprise reports (industry analysis + competitive-intelligence pricing)</sub>")
lines.append("")
lines.append("</div>")
lines.append("")

# === TL;DR ===
lines.append("## TL;DR")
lines.append("")
lines.append("| | |")
lines.append("|---|---|")
lines.append(f"| 🥇 **Winner** | `rag_md_v2` — docparse markdown · per-page chunks · RAG Engine · Gemini 3 flash · top_k=20 · exhaustive system prompt |")
lines.append(f"| 🎯 **Composite score** | **{top_comp}%** (correctness {top['correctness_score']}%, completeness {top['completeness_score']}%) |")
lines.append(f"| 🔍 **Eval set** | 216 hand-crafted Q&A pairs across 2 enterprise PDFs (customer data redacted for public release) |")
lines.append(f"| ⚖️ **Judge** | `claude-opus-4-5@20251101` via AnthropicVertex (different model family — avoids self-preference bias) |")
lines.append(f"| 📐 **Composite** | (correctness + completeness) / 2, both 0.0–1.0 |")
lines.append(f"| 🏗️ **Production stack lives in** | [`docparse-rag-agent/`](./README.md) |")
lines.append("")
lines.append("---")
lines.append("")

# === Leaderboard ===
lines.append("## 1 · Leaderboard")
lines.append("")
lines.append("Composite score across all 216 questions, with the verdict mix that produced it.")
lines.append("")
lines.append("| Rank | Strategy | Composite | Visual | ✓ correct | × wrong | ? refused | ~ partial |")
lines.append("|---:|---|---:|---|---:|---:|---:|---:|")
for i, label in enumerate(STRATEGY_ORDER, 1):
    s = summaries[label]
    comp = s["composite_score"]
    vc = s["verdicts"]
    medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"{i}"
    bar_str = bar(comp)
    lines.append(
        f"| {medal} | **`{label}`** | **{comp}%** | `{bar_str}` | "
        f"{vc.get('correct',0)} | {vc.get('wrong',0)} | {vc.get('refused',0)} | {vc.get('partial',0)} |"
    )
lines.append("")
lines.append("**Read this as:** the gap between the top three (~81–93%) shows engine + retrieval matters; the gap to bottom (63.8% for `rag_pdf`) shows extraction matters. Both axes stack.")
lines.append("")
lines.append("---")
lines.append("")

# === What each strategy is ===
lines.append("## 1b · What each strategy is")
lines.append("")
lines.append("The full stack behind each strategy name.")
lines.append("")
lines.append("| Strategy | Full stack description |")
lines.append("|---|---|")
stack_descriptions = [
    ("rag_md_v2",  "docparse markdown → **Vertex AI RAG Engine** (72 per-page files, chunk 1000) → **gemini-3-flash-preview** (direct retrieval tool, top_k=20) → **ADK Agent** deployed to Agent Engine → registered in **Gemini Enterprise**"),
    ("rag_md",     "docparse markdown → **Vertex AI RAG Engine** (2 whole-doc files, auto-chunked 500) → **gemini-3-flash-preview** (direct retrieval tool, top_k=5)"),
    ("digital_v2", "docparse markdown → **Vertex AI Search** (GCS connector, digitalParsingConfig, chunk 500) → **Gemini Enterprise streamAssist** + maximal config (system instruction, web grounding off, managed agents deleted)"),
    ("digital",    "docparse markdown → **Vertex AI Search** (GCS connector, digitalParsingConfig, chunk 500) → **Gemini Enterprise streamAssist** (default assistant config)"),
    ("ocr",        "docparse markdown → **Vertex AI Search** (GCS connector, **ocrParsingConfig**, chunk 500) → **Gemini Enterprise streamAssist**"),
    ("layout",     "docparse markdown → **Vertex AI Search** (GCS connector, **layoutParsingConfig + image annotation**, chunk 500) → **Gemini Enterprise streamAssist**"),
    ("digital_200","docparse markdown → **Vertex AI Search** (GCS connector, digitalParsingConfig, **chunk 200**) → **Gemini Enterprise streamAssist**"),
    ("rag_pdf",    "**raw PDFs (NO docparse extraction)** → **Vertex AI RAG Engine** (PDFs direct-imported, RAG's built-in PDF chunker) → **gemini-3-flash-preview** (direct retrieval tool) — ablation test to isolate extraction quality"),
]
for label, desc in stack_descriptions:
    lines.append(f"| `{label}` | {desc} |")
lines.append("")
lines.append("**The 1P baseline = strategies 3–7** (Vertex AI Search → Gemini Enterprise, the out-of-the-box GCS-connector experience). Strategies 1–2 and 8 bypass Vertex AI Search and use Vertex AI RAG Engine directly.")
lines.append("")
lines.append("---")
lines.append("")

# === Detailed metrics ===
lines.append("## 1a · Detailed metrics")
lines.append("")
lines.append("Composite is the headline, but correctness + completeness matter for production.")
lines.append("")
lines.append("| Strategy | Composite | Correctness | Completeness | ✓ | × | ? | ~ |")
lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
for label in STRATEGY_ORDER:
    s = summaries[label]
    comp = s["composite_score"]
    cor = s["correctness_score"]
    com = s["completeness_score"]
    vc = s["verdicts"]
    lines.append(
        f"| `{label}` | **{comp}%** | {cor}% | {com}% | "
        f"{vc.get('correct',0)} | {vc.get('wrong',0)} | {vc.get('refused',0)} | {vc.get('partial',0)} |"
    )
lines.append("")
lines.append("**Note:** Per-question data and sample failures redacted for customer privacy. Full evaluation dataset available internally.")
lines.append("")
lines.append("---")
lines.append("")

# === Two-axis ablation ===
lines.append("## 2 · The two-axis ablation")
lines.append("")
lines.append("| Comparison | Δ composite | What it isolates |")
lines.append("|---|---:|---|")
lines.append("| `rag_md_v2` vs `rag_md` (same engine, swap chunking strategy) | **+5.5 pts** | per-page chunks + exhaustive prompt vs vanilla RAG |")
lines.append("| `rag_md` vs `digital_v2` (same markdown, swap engine) | **+6.2 pts** | RAG Engine + Gemini beats DE streamAssist |")
lines.append("| `rag_md_v2` vs `rag_pdf` (same engine, swap input) | **+29.1 pts** | docparse extraction beats raw-PDF ingestion |")
lines.append("| `digital_v2` vs `rag_pdf` (better extraction, worse engine) | **+17.4 pts** | extraction > engine when you can't have both |")
lines.append("")
lines.append("---")
lines.append("")

# === Methodology ===
lines.append("## 3 · How we tested")
lines.append("")
lines.append("```mermaid")
lines.append("flowchart LR")
lines.append("    Q[216 Q and A pairs<br/>hand-crafted from 2 PDFs] --> R[run each strategy<br/>through the same 216 questions]")
lines.append("    R --> J[Claude Opus 4.5<br/>scores each Q and A pair]")
lines.append("    J --> S[correctness 0.0 to 1.0<br/>completeness 0.0 to 1.0<br/>verdict: correct / partial / wrong / refused]")
lines.append("    S --> A[aggregate to composite<br/>correctness plus completeness over 2]")
lines.append("```")
lines.append("")
lines.append("**Composite formula:** `composite = mean( (correctness + completeness) / 2 )` across all answered questions.")
lines.append("")
lines.append("**Verdict labels:**")
lines.append("- `correct` — answer matches ground truth in substance.")
lines.append("- `partial` — some right, some missing or wrong.")
lines.append("- `wrong` — confidently incorrect fact.")
lines.append("- `refused` — assistant said it couldn't find / answer.")
lines.append("")
lines.append("**Why Claude as judge?** Different model family from the systems-under-test (Gemini), so no self-preference bias. Prompt forces strict JSON output; retries on rate-limits with exponential backoff.")
lines.append("")
lines.append("**Question categories:** page-anchored lookups, chart-cell reads, math/aggregation, text-lookup, photo/vision, and diagram interpretation. See full evaluation methodology in internal docs.")
lines.append("")
lines.append("---")
lines.append("")

# === All configurations ===
lines.append("## 4 · All 8 configurations tested")
lines.append("")
lines.append("Every extraction × indexing × parser combination we benchmarked.")
lines.append("")
lines.append("| # | Strategy | Extraction | Indexing product | Parser / chunking | Answering | Composite |")
lines.append("|---:|---|---|---|---|---|---:|")
configs_table = [
    ("1", "rag_md_v2",  "docparse markdown", "Vertex AI RAG Engine", "72 per-page files, chunk 1000/overlap 100", "gemini-3-flash + retrieval tool, top_k=20"),
    ("2", "rag_md",     "docparse markdown", "Vertex AI RAG Engine", "2 full files, auto-chunked 500/overlap 100", "gemini-3-flash + retrieval tool, top_k=5"),
    ("3", "digital_v2", "docparse markdown", "Vertex AI Search (GCS connector)", "digitalParsingConfig, chunk 500, + system instr + web off + agents deleted", "Gemini Enterprise streamAssist"),
    ("4", "digital",    "docparse markdown", "Vertex AI Search (GCS connector)", "digitalParsingConfig, chunk 500, default config", "Gemini Enterprise streamAssist"),
    ("5", "ocr",        "docparse markdown", "Vertex AI Search (GCS connector)", "**ocrParsingConfig**, chunk 500", "Gemini Enterprise streamAssist"),
    ("6", "layout",     "docparse markdown", "Vertex AI Search (GCS connector)", "**layoutParsingConfig** + image annotation, chunk 500", "Gemini Enterprise streamAssist"),
    ("7", "digital_200","docparse markdown", "Vertex AI Search (GCS connector)", "digitalParsingConfig, **chunk 200**", "Gemini Enterprise streamAssist"),
    ("8", "rag_pdf",    "**raw PDFs (no extraction)**", "Vertex AI RAG Engine", "PDFs direct-import, RAG's built-in PDF chunker", "gemini-3-flash + retrieval tool"),
]
for rank, label, ext, idx, parse, ans in configs_table:
    comp = summaries[label]["composite_score"]
    lines.append(f"| {rank} | `{label}` | {ext} | {idx} | {parse} | {ans} | **{comp}%** |")
lines.append("")
lines.append("**The 1P baseline = rows 3-7** (Vertex AI Search → Gemini Enterprise). Rows 1-2 and 8 use Vertex AI RAG Engine instead (bypassing Vertex AI Search).")
lines.append("")
lines.append("---")
lines.append("")

# === Reproduce ===
lines.append("## 5 · Reproduce")
lines.append("")
lines.append("Eval scaffolding lives in this repo's `eval/` directory. The public release includes:")
lines.append("")
lines.append("- `questions.json` — 216 Q&A pairs with structure preserved but content redacted")
lines.append("- `judged/*.json` — composite scores and verdict counts for each strategy (per-question data redacted)")
lines.append("- `build_results_md_sanitized.py` — regenerates this RESULTS.md from sanitized data")
lines.append("")
lines.append("Full evaluation dataset (with actual questions and answers) available internally at `~/docparse-eval-private/`.")
lines.append("")
lines.append("To regenerate this document:")
lines.append("")
lines.append("```bash")
lines.append("cd eval/")
lines.append("python3 build_results_md_sanitized.py")
lines.append("```")
lines.append("")
lines.append("---")
lines.append("")
lines.append('<div align="center"><sub>Generated from sanitized eval data · 8 strategies · 216 questions per strategy</sub></div>')
lines.append("")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(lines))
print(f"Wrote {OUT} ({OUT.stat().st_size:,} bytes, {len(lines)} lines)")
