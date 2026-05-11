# Sample Run — 2026-05-11

500 questions × 20 categories × 5 Jira projects (~1,310 issues), head-to-head between two production patterns for putting Atlassian Jira behind a chat agent.

## View the report

[**Open the report (HTML, with side-by-side answers)** ↗](https://htmlpreview.github.io/?https://github.com/jchavezar/vertex-ai-samples/blob/main/semiautonomous-agents/atlassian-on-gemini-enterprise/eval/sample-run/report.html)

## Headline result

| | Gemini + Custom MCP | Claude Code + Rovo MCP |
|---|---|---|
| LLM | Vertex AI Gemini 3 Flash Preview | Anthropic Claude Sonnet 4.6 |
| Tools | Custom Cloud Run MCP (7 tools we ship) | Atlassian Rovo MCP (~37 tools they ship) |
| **Composite** | **91.3%** | **87.1%** |
| Correctness | 91.3% | 87.7% |
| Citation accuracy | **99.9%** | 69.5% |
| Hallucination rate ↓ | **1.1%** | **68.9%** ⚠️ |
| Verdicts | 430 correct, 12 partial, 33 wrong, 0 hallucinated, 21 refused, 4 error | 381 correct, 65 partial, 22 wrong, **9 hallucinated**, 23 refused, 0 error |

## Per-category — where each pipeline wins

```
category                      Gemini     Claude        Δ (Claude − Gemini)
-------------------------------------------------------------------------
epic-tree                     84.4%     99.0%   +14.6  ← Claude wins
lookup                        88.0%    100.0%   +12.0  ← Claude wins
trend                         82.9%     91.7%    +8.8  ← Claude wins
comments-worklogs             87.3%     95.8%    +8.5  ← Claude wins
typo-robustness               92.0%    100.0%    +8.0  ← Claude wins
refusal-test                  84.0%     92.0%    +8.0  ← Claude wins
prompt-injection              96.0%    100.0%    +4.0
root-cause-synthesis          97.4%     99.8%    +2.4
pii-sensitive                 92.1%     93.5%    +1.4
cross-issue-analysis          97.0%     98.3%    +1.3
multi-step                    96.9%     94.9%    -2.0
ambiguous                     97.0%     94.6%    -2.4
issue-links                   86.1%     83.4%    -2.7
tool-efficiency               95.0%     87.0%    -8.0  ← Gemini wins
multi-project                 83.4%     67.8%   -15.6  ← Gemini wins
count-aggregate               96.0%     75.4%   -20.6  ← Gemini wins
golden-anti-regression        96.0%     72.0%   -24.0  ← Gemini wins
components-versions           92.7%     67.3%   -25.4  ← Gemini wins
jql-filter                    95.5%     69.6%   -25.9  ← Gemini wins
pagination-required           86.0%     60.0%   -26.0  ← Gemini wins
```

**Pattern:** Claude is better at **reasoning, narrative, single-key precision, and safety**. Gemini is better at **numeric/structural correctness** — counting, JQL, pagination, structured filters.

## The hallucination caveat

Claude+Rovo cited fake issue keys in **~7 of 10 answers** (vs Gemini's ~1 in 100). Why: when synthesizing the final answer, Claude sometimes invents plausible-looking keys (e.g. cites "BUGS-50" when the tool only returned "BUGS-100", "BUGS-99"). The Gemini agent was instructed to *"NEVER cite a key not present in tool output"*; the Claude sub-agents had no equivalent guardrail.

For a real Jira chatbot where *"link to a real issue or don't link"* matters, **Gemini + Custom MCP is the safer default** until Claude+Rovo gets a citation-discipline guardrail.

## What's in this folder

| File | What |
|---|---|
| `report.html` | Side-by-side report — open this. Includes scoreboard, per-category bars, latency histogram, win/loss matrix, **failures section** (every wrong/hallucinated answer, both pipelines side-by-side, oracle visible), 20 random samples. |
| `summary.json` | Machine-readable scoreboard. |
| `judged_a.json` / `judged_b.json` | Per-question scores across all 10 dimensions. |
| `responses_a.jsonl` | Gemini agent answers + tool calls. |
| `responses_b.jsonl` | Claude+Rovo answers + tool calls. |
| `questions.json` | All 500 questions with their oracles (expected_keys / count / JQL / themes). |

## How to reproduce

```bash
cd ../        # eval/
source .venv/bin/activate
python build_corpus.py                                      # one-time: create 4 test projects + ~400 issues in Jira
python generate_questions.py --n 25 --out questions/main.json
python -m runners.orchestrator --questions questions/main.json --out runs/<ts>
python judge.py runs/<ts>/responses_a.jsonl --pipeline a --questions runs/<ts>/questions.json --out runs/<ts>/judged_a.json
python judge.py runs/<ts>/responses_b.jsonl --pipeline b --questions runs/<ts>/questions.json --out runs/<ts>/judged_b.json
REPORT_SHORT_A="Gemini + Custom MCP" REPORT_SHORT_B="Claude Code + Rovo MCP" python report.py --run runs/<ts> --questions runs/<ts>/questions.json
```

Option B in this run was actually 20 parallel Claude Code sub-agents (each handling 25 questions via `mcp__atlassian-rovo__*` tools) rather than the standard `runners/run_option_b.py`. Same data, different invocation path.
