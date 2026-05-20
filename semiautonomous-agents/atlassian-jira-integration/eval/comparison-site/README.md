# Comparison Site

Single-page HTML report comparing the five Jira × Gemini Enterprise options on the 500-question benchmark.

## What it shows

- **Headline cards** — accuracy, hallucinations, errors, refusals, p50/p90 latency for each option.
- **Comparison table** — same metrics in side-by-side form, plus the LLM model and consumption surface for each option.
- **Per-category heatmap** — 20 categories × 5 pipelines, color-coded.
- **All 500 questions** — searchable, filterable. Click any row to expand and read the full answer from each pipeline side-by-side, along with verdict, latency, and tool-call count.

## View locally

```bash
cd eval/comparison-site
python3 -m http.server 8000
# open http://localhost:8000/
```

Or open `index.html` directly in a browser (works because the site fetches `data.json` over `file://` in most modern browsers; if your browser blocks it, use the http.server one-liner above).

## Regenerate after a new run

```bash
# from repo root
python3 eval/comparison-site/build_data.py
```

The script reads the runs hard-coded in `PIPELINES` (top of `build_data.py`). Update those if you want to surface a different run for a given option.

## Files

| Path | Purpose |
|---|---|
| `index.html` | Single-page app — vanilla JS, no build step. |
| `data.json` | 500 questions × 5 pipeline answers + per-category summary stats (~5.6 MB). |
| `build_data.py` | Regenerates `data.json` from `eval/runs/<ts>/responses_*.jsonl` + `judged_*.json`. |

## How options map to runs

| Public option | Run directory | Why |
|---|---|---|
| **A** Custom MCP + ADK | `runs/20260511-gemini25/` | Best A run with Gemini 2.5 + ADK Agent Engine |
| **B** Atlassian Rovo | `runs/20260511-claude-rovo/` | Best B run; Claude Sonnet sub-agent |
| **C** Custom MCP direct | `runs/20260519-101102-option-g-full-si/` | Same architecture as published "Option C" (GE BYO_MCP w/o ADK); measured via the streamAssist harness for parity with B |
| **D** Federated jira_cloud | `runs/20260519-203012-option-h-full/` | GE's built-in federated connector via streamAssist |
| **E** google.genai + MCP wrapper | `runs/20260520-134011-option-e-v2-flashlite-full/` | Current production design — single `ask_jira_expert` MCP tool, internal genai tool-loop with `gemini-3.1-flash-lite` |
