# Sample Run — 2026-05-07

A canonical execution of the eval harness over 478 grounded questions against the live `sockcop.atlassian.net` Jira instance. Committed so external reviewers can see exactly what the harness produces without needing a Jira account or running anything.

## View the report

GitHub doesn't render HTML inline. Use one of these:

- **htmlpreview** (one click, no setup): https://htmlpreview.github.io/?https://github.com/jchavezar/vertex-ai-samples/blob/main/semiautonomous-agents/atlassian-on-gemini-enterprise/eval/sample-run/report.html
- **Local clone:**
  ```
  git clone git@github.com:jchavezar/vertex-ai-samples.git
  xdg-open vertex-ai-samples/semiautonomous-agents/atlassian-on-gemini-enterprise/eval/sample-run/report.html
  ```

## Headline result

| | Option A — Custom MCP Portal | Option B — Direct Remote MCP |
|---|---|---|
| **Composite** | **66.1%** | 45.4% |
| Correctness | 65.7% | 44.6% |
| Completeness | 66.4% | 46.2% |
| Citation accuracy | **95.5%** | 81.8% |
| Hallucination rate | **4.8%** | 18.2% |
| Latency p50 | 32.5 s | 53.3 s |
| Latency p95 | 366.0 s | 121.4 s |
| Verdicts | 239 correct, 55 partial, 139 wrong, 1 hallucinated, 30 refused, 14 error | 79 correct, 95 partial, 199 wrong, 1 hallucinated, 41 refused, 63 error |

Option A wins decisively on quality (correctness, citation accuracy, hallucination rate ~4× lower) but trades long-tail latency (p95 6× worse — multi-step questions take minutes). Option B is faster on the long tail but cites ~18% fake/wrong issue keys and errors out 13% of the time.

## What's in here

| File | Size | What it is |
|---|---|---|
| `report.html` | 1.1 MB | The side-by-side report — open this. Includes hero, headline scoreboard, per-category bars, latency histogram, win/loss matrix, verdict confusion, hallucination spotlight, **failures section** (every wrong question with full agent answer text + judge reasoning + oracle), 20 random samples, failure-mode taxonomy, methodology. |
| `summary.json` | 16 KB | Same data as the report's hero/scoreboard, machine-readable. |
| `judged_a.json` | 650 KB | Per-question scores for Option A across all 10 dimensions. |
| `judged_b.json` | 451 KB | Same for Option B. |
| `responses_a.jsonl` | 3.8 MB | Per-question answer text + tool calls + citations + latency for Option A. |
| `responses_b.jsonl` | 536 KB | Same for Option B. |
| `questions.json` | 1.8 MB | The 478 grounded questions used for this run, with their oracle (expected_keys / expected_count / oracle JQL / expected_themes). |

The per-question raw streamAssist SSE dumps (`runs/<ts>/raw/`) are not committed — they're 50+ MB and only useful for debugging the runner.

## Reproducing

The data above came from these exact commands:

```bash
cd ../   # back to eval/
source .venv/bin/activate
python generate_questions.py --n 48 --out questions/main.json
python -m runners.orchestrator --questions questions/main.json --out runs/<ts>
python judge.py runs/<ts>/responses_a.jsonl --pipeline a --questions questions/main.json --out runs/<ts>/judged_a.json
python judge.py runs/<ts>/responses_b.jsonl --pipeline b --questions questions/main.json --out runs/<ts>/judged_b.json
python report.py --run runs/<ts> --questions questions/main.json
```

Wall-clock on this run: question gen ~5 min, parallel A+B run ~1 h 50 min, both judges ~3 min, report ~1 s.

## Caveats

- **Only one Jira project (SMP)** in the test corpus, so categories that benefit from cross-project filters (`jql-filter`, `count-aggregate`) are easier than they would be on a real multi-project instance.
- **No labels in the corpus** so `pagination-required` questions that depend on label filters degenerate to "list all 910 issues" — both pipelines partial-credit since neither lists all 910 in chat.
- **Refusal heuristic is keyword-based** — agents that refuse using uncommon phrasing get marked `wrong`. Tightening the heuristic (or LLM-judging refusal) would lift both pipelines' refusal scores ~5pp.
- **Option A goes through `:streamQuery`** (direct Agent Engine invocation) rather than `streamAssist`, because GE's per-user OAuth gates programmatic agent calls. The agent code, model, tools are identical to production GE chats — only the OAuth layer differs.
- **Hallucination rate** for Option B is likely understated: when GE's MCP datastore times out or 500s, no tool result is captured, so cited keys can't be cross-checked against tool output. The deterministic citation_accuracy metric (does the key exist in Jira?) is more reliable for B.
