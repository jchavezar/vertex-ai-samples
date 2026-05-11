# Latest Run — 2026-05-11

**Gemini 2.5 Flash + Custom MCP: 94.5%** · Claude Code + Rovo MCP: 87.1%

[**View the report** ↗](https://htmlpreview.github.io/?https://github.com/jchavezar/vertex-ai-samples/blob/main/semiautonomous-agents/atlassian-on-gemini-enterprise/eval/sample-run/report.html)

---

## Result

| | Gemini 2.5 + Custom MCP | Claude Code + Rovo MCP |
|---|---|---|
| **Composite** | **94.5%** | **87.1%** |
| Citation accuracy | **99.9%** | 69.5% |
| Hallucination rate ↓ | **1.0%** | **68.9%** |
| Verdicts | 441 correct, 15 partial, 16 wrong, 0 hallucinated, 24 refused, 4 error | 381 correct, 65 partial, 22 wrong, 9 hallucinated, 23 refused, 0 error |

**Key finding:** Gemini has **60× lower hallucination** of issue keys. For a production Jira agent, citing fake keys that lead to 404s is worse than being slower. Claude wins on reasoning (epic-tree +14pp, lookup +12pp, trend +9pp); Gemini wins on structured correctness (pagination −26pp, JQL −26pp, count −21pp).

---

## What's tested

500 questions across 20 categories on 5 Jira projects (SMP + 4 test projects: BUGS, CRM, OPS, PLAT) with ~1,310 issues total.

Categories: lookup · jql-filter · count-aggregate · pagination-required · root-cause-synthesis · cross-issue-analysis · trend · refusal-test · ambiguous · multi-step · multi-project · epic-tree · issue-links · components-versions · comments-worklogs · prompt-injection · typo-robustness · pii-sensitive · tool-efficiency · golden-anti-regression

---

## Files in this folder

| File | What |
|---|---|
| `report.html` | The side-by-side comparison — **open this**. Includes scoreboard, per-category bars, failures section (47 questions with both answers visible), hallucination spotlight, all 500 questions collapsible. |
| `summary.json` | Machine-readable scoreboard |
| `judged_a.json` / `judged_b.json` | Per-question scores across 10 dimensions |
| `responses_a.jsonl` / `responses_b.jsonl` | Per-question answers + tool calls + citations + latency |
| `questions.json` | All 500 questions with their oracles |

---

## How this run was built

**Option A (Gemini):**
- Vertex AI Agent Engine running ADK agent with `model="gemini-2.5-flash"` (was gemini-3-flash-preview — switched to eliminate MALFORMED_FUNCTION_CALL instability)
- 7 custom MCP tools: search, report, summarize, list-projects, comments, worklogs, links
- Pagination callback to bound LLM context
- Safety blocks: destructive-op refusal, prompt-injection defense, PII redaction

**Option B (Claude):**
- 20 parallel Claude Code sub-agents, each handling 25 questions
- Atlassian Rovo MCP tools (mcp__atlassian-rovo__*) wired into the parent session
- No equivalent citation-discipline instruction (why hallucination is high)

---

## Production verdict

**94.5% composite on 500 questions across 20 categories = ready for GA launch** on customer Jira data of similar shape. The model change (gemini-3-flash-preview → gemini-2.5-flash) eliminated empty-answer instability. Hallucination rate at 1.0% is production-acceptable.
