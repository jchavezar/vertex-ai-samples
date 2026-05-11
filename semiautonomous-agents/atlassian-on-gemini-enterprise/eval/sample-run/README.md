# Sample Run — 2026-05-11 (Gemini + Custom MCP **vs** Claude Code + Rovo MCP)

The customer was claiming **Atlassian's Rovo MCP is more accurate than what
we built with Gemini**. This run tests that claim head-to-head over 500
grounded questions on the same 5-project Jira corpus.

## Setup

| | Option A (this is what "we built") | Option B (this is what the customer prefers) |
|---|---|---|
| **LLM** | Vertex AI Gemini 3 Flash Preview | Claude Sonnet 4.6 (sub-agent) |
| **Agent runtime** | Vertex AI Agent Engine + Google ADK | Claude Code's general-purpose sub-agent harness |
| **Tools** | Custom Cloud Run MCP server (4 tools we wrote + 3 added today: comments/worklogs/links) | Atlassian's official Rovo MCP server (~37 tools, run by Atlassian) |
| **Data path** | Cloud Run → Atlassian REST | Atlassian Rovo MCP → Atlassian REST |
| **Where Jira is hit** | sockcop.atlassian.net | sockcop.atlassian.net (same site, same data) |

Same 500 questions, same judge (Claude Opus 4.5), same harness — only the
agent + tools change.

## View the report

https://htmlpreview.github.io/?https://github.com/jchavezar/vertex-ai-samples/blob/main/semiautonomous-agents/atlassian-on-gemini-enterprise/eval/sample-run/report.html

## Headline result

| | Gemini + Custom MCP | Claude Code + Rovo MCP |
|---|---|---|
| **Composite** | **91.3%** | **87.1%** |
| Correctness | 91.3% | 87.7% |
| Completeness | 91.2% | 86.5% |
| **Citation accuracy** | **99.9%** | 69.5% |
| **Hallucination rate** ↓ | **1.1%** | **68.9%** |
| Latency p50 / p95 | 28s / 192s | (parallel batched, not directly comparable) |
| Verdicts | 430 correct, 12 partial, 33 wrong, 0 hallucinated, 21 refused, 4 error | 381 correct, 65 partial, 22 wrong, **9 hallucinated**, 23 refused, 0 error |

**Bottom line:** Gemini wins headline composite by 4.2pp — but the difference
is dwarfed by a much more important finding: **Claude+Rovo hallucinates issue
keys at 60× the rate of Gemini+Custom MCP** (68.9% vs 1.1%). The judge
flagged 9 questions as `hallucinated` for Claude vs 0 for Gemini.

## Where each pipeline wins / loses

```
category                      Gemini     Claude        Δ (Claude − Gemini)
-------------------------------------------------------------------------
epic-tree                     84.4%     99.0%   +14.6  ← Claude wins (graph reasoning)
lookup                        88.0%    100.0%   +12.0  ← Claude wins (single-key precision)
trend                         82.9%     91.7%    +8.8  ← Claude wins (narrative)
comments-worklogs             87.3%     95.8%    +8.5  ← Claude wins (long-text reasoning)
typo-robustness               92.0%    100.0%    +8.0  ← Claude wins (key normalization)
refusal-test                  84.0%     92.0%    +8.0  ← Claude wins (safety)
prompt-injection              96.0%    100.0%    +4.0  ← tied at the top
root-cause-synthesis          97.4%     99.8%    +2.4
cross-issue-analysis          97.0%     98.3%    +1.3
pii-sensitive                 92.1%     93.5%    +1.4
multi-step                    96.9%     94.9%    -2.0
ambiguous                     97.0%     94.6%    -2.4
issue-links                   86.1%     83.4%    -2.7
tool-efficiency               95.0%     87.0%    -8.0  ← Gemini wins (fewer wasted calls)
multi-project                 83.4%     67.8%   -15.6  ← Gemini wins (cross-project filters)
count-aggregate               96.0%     75.4%   -20.6  ← Gemini wins (numeric precision)
golden-anti-regression        96.0%     72.0%   -24.0  ← Gemini wins (canary set)
components-versions           92.7%     67.3%   -25.4  ← Gemini wins (metadata filter)
jql-filter                    95.5%     69.6%   -25.9  ← Gemini wins (JQL accuracy)
pagination-required           86.0%     60.0%   -26.0  ← Gemini wins (full-set retrieval)
```

**Pattern:** Claude is better at **reasoning, narrative, single-key precision,
and safety**. Gemini is better at **numeric/structural correctness** —
counting, JQL, pagination, structured filters.

## The hallucination problem (Claude + Rovo's biggest issue)

68.9% of Claude's answers contained at least one cited issue key that wasn't
returned by any tool call (or doesn't exist in Jira). That's a **6.6× higher
hallucination rate than Gemini's 1.1%**.

Why it happens: when Claude finishes its tool calls and synthesizes the
final answer, it sometimes invents plausible-looking keys (e.g. cites
"BUGS-50" when the tool only returned "BUGS-100", "BUGS-99" — the model
"helps" by sampling other plausible numbers in the range). The custom-MCP
agent (Gemini) was instructed to ONLY cite keys that appeared in tool
results; the Claude sub-agent had no such instruction.

This is critical for production: a Jira agent that confidently links to
fake issue keys creates broken URLs that lead users to 404s. **Hallucination
rate is a more important quality metric than composite for ticketing
agents.** Gemini's 1.1% is production-grade; Claude's 68.9% is not, even
though composite makes them look comparable.

The fix would be straightforward: add to the sub-agent prompt *"NEVER cite
an issue key that wasn't returned by a tool call this turn — if you can't
find the key in tool results, say so instead of guessing."* — but that's a
fix on the consumer side (Claude Code's prompting), not on the Rovo MCP
itself.

## Why each side wins what it wins

**Claude + Rovo wins on:**
- `epic-tree`, `comments-worklogs`, `trend`, `root-cause-synthesis` — natural-language
  reasoning over fetched content. Claude's general LLM strength.
- `lookup`, `typo-robustness` — Rovo's purpose-built `getJiraIssue` tool
  normalizes keys and returns rich data. The custom MCP requires a
  generic search call.
- `refusal-test`, `prompt-injection` — Anthropic's RLHF safety training
  is generally stronger than Gemini's on adversarial prompts.

**Gemini + Custom MCP wins on:**
- `count-aggregate`, `golden-anti-regression`, `pagination-required` — the
  custom `summarizeJiraIssues` and `getJiraIssuesReport` tools are
  purpose-built for these patterns; Rovo's `searchJiraIssuesUsingJql`
  with pagination tokens has gaps (some sub-agents reported pagination
  tokens being rejected by the API mid-run).
- `jql-filter`, `multi-project`, `components-versions` — instruction tuning
  for cross-project JQL syntax; Claude was less precise.
- Hallucination control — the agent's explicit "URL must come from tool
  output" instruction; sub-agents had no equivalent.

## Production interpretation

The customer's claim *"Rovo MCP is more accurate"* is **partially true**:
- For interactive single-issue queries, Rovo + Claude is excellent (lookup
  100%, comments 96%, epic-tree 99%).
- For dashboard-style aggregations and large-result-set retrieval,
  Gemini + Custom MCP is meaningfully better (count 96 vs 75, pagination
  86 vs 60).

The right answer depends on the workload. For a customer-facing chatbot
that mostly answers "what's the status of X" — Claude + Rovo wins.
For an analytics/reporting assistant that does counts and dashboards —
Gemini + Custom MCP wins.

**For a balanced ticketing agent, neither pipeline is clearly better
overall — but the hallucination disparity makes Gemini + Custom MCP
the safer default until Claude+Rovo gets a "no fake citations" guardrail.**

## What's in here

| File | What it is |
|---|---|
| `report.html` | Side-by-side report — open this. Includes scoreboard, per-category bars, latency histogram, win/loss matrix, **failures section** with both pipelines' answers shown side-by-side, hallucination spotlight, and 20 random samples. |
| `summary.json` | Machine-readable scoreboard. |
| `judged_a.json` / `judged_b.json` | Per-question scores across all 10 dimensions. |
| `responses_a.jsonl` | Gemini agent's responses (carried over from the prior run). |
| `responses_b.jsonl` | Claude+Rovo responses — built fresh from 20 sub-agents that each handled 25 questions in parallel. |
| `questions.json` | All 500 questions with their oracles. |

## How Option B was actually run

Not the regular orchestrator — instead, 20 `general-purpose` sub-agents
were spawned in parallel from this Claude Code session. Each was given
25 questions and the `mcp__atlassian-rovo__*` tool inventory (the same
Atlassian Rovo MCP wired into the parent session via `claude mcp add`).
Each sub-agent answered, formatted as JSONL, wrote to its batch file. All
20 batch files were concatenated into `responses_b.jsonl`.

Total wall-clock from spawning to last completion: ~7 minutes (massive
parallelism). Token cost for the sub-agents: ~2.5M tokens of Claude
Sonnet 4.6 ≈ ~$8-10.

This is meaningfully different from the prior Option B (which was
GE+Datastore+Atlassian Rovo, suffered from 65% connector errors) — by
giving Claude Code direct MCP access, we get a fair test of "what Claude
can do with Rovo's tools" without the GE-platform headless-OAuth problems.

## Caveats

- The Claude sub-agents had a brief safety-and-format prompt (read-only,
  refuse injection, don't echo PII). They did NOT have the elaborate
  "never cite a key that's not in tool results" instruction that the
  Gemini agent has — that's why hallucination is higher. A fairer test
  would give both pipelines equivalent safety/citation prompts.
- Latency comparison isn't apples-to-apples: Gemini ran one-question-at-a-time
  through Vertex AI Agent Engine; Claude sub-agents batched 25 questions
  each in parallel. Per-question latency for Claude is approximate.
- 9 of Claude's answers were classified `hallucinated` (cited fake keys
  while still being partially correct). Gemini had 0. This skews the
  composite slightly in Gemini's favor.

Previous runs preserved at `eval/sample-run-<date>-*/` for comparison.
