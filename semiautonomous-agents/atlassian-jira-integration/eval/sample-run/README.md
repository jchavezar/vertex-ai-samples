# Final Run — 2026-05-12

> **DEPRECATED — historical snapshot.** This run pre-dates the v2 corpus
> and the judge_v6 rubric. For current canonical numbers, see
> [`../README.md`](../README.md) and the root
> [`../../README.md`](../../README.md), both judged under **judge_v6**
> (gemini-3-flash-preview + Haiku 4.5 escalation, n=172 v2 corpus,
> 2026-05-27).

**Gemini 3 Flash + Custom MCP: 95.5%** · Claude Code + Rovo MCP: 87.1%

[**View the report** ↗](https://htmlpreview.github.io/?https://github.com/jchavezar/vertex-ai-samples/blob/main/semiautonomous-agents/atlassian-on-gemini-enterprise/eval/sample-run/report.html)

## Result

| | Gemini 3 + Custom MCP | Claude Code + Rovo MCP |
|---|---|---|
| **Composite** | **95.5%** | **87.1%** |
| **Latency p50** | **7.8s** | ~5-10s |
| **Latency < 10s** | **68%** of questions | ~80% (est) |
| Simple questions (lookup, count) | **2-5s** | ~3-7s |
| Complex questions (analytics, multi-step) | 10-50s | 10-30s |
| Hallucination rate ↓ | **0.2%** | 68.9% |
| Verdicts | 449 correct, 9 partial, 16 wrong, 0 hallucinated, 25 refused, 1 error | 381 correct, 65 partial, 22 wrong, 9 hallucinated, 23 refused, 0 error |

## Configuration

**Gemini (Option A):**
- Framework: In-process ADK (no Agent Runtime deployment)
- Model: gemini-3-flash-preview
- Thinking: thinking_level=MINIMAL (balance speed/quality)
- MCP: Custom Cloud Run server (7 tools — search, report, summarize, comments, worklogs, links, list-projects)
- Per-user ACL: ✅ Multi-tenant via contextvars

**Claude (Option B):**
- Framework: Claude Code sub-agents (20 parallel batches)
- Model: Claude Sonnet 4.6
- MCP: Atlassian Rovo (mcp.atlassian.com, ~37 tools)
- Per-user ACL: ✅ Via Atlassian's OAuth

## Key Finding

**You can hit both targets simultaneously:**
- **≥ 90% composite** ✅ (95.5%)
- **< 10s for most questions** ✅ (68% under 10s, p50 = 7.8s)

The winning formula:
1. **In-process ADK** (not deployed Agent Runtime) — saves ~2s deployment overhead
2. **gemini-3-flash-preview** (not 2.5) — better quality on this corpus
3. **thinking_level=MINIMAL** — balances speed vs reasoning depth
4. **Custom MCP with tight instruction** — citation discipline + pagination callbacks

## What's in here

| File | What |
|---|---|
| `report.html` | Side-by-side report with all 500 questions |
| `summary.json` | Scoreboard |
| `judged_a.json` / `judged_b.json` | Per-question scores |
| `responses_a.jsonl` / `responses_b.jsonl` | Answers + tool calls + latency |
| `questions.json` | All 500 questions with oracles |

## For production

**If deploying to Agent Runtime:** expect p50 ~9-10s (adds ~2s vs in-process). Still meets the <10s target for simple questions.

**If running in-process** (FastAPI endpoint that imports ADK Runner): p50 ~7.8s as shown here.
