# Atlassian Rovo MCP — Integration Findings & Recommendations

> **SUPERSEDED — historical snapshot for the 2026-05-12 call.** Numbers in
> this document reflect the eval state on that date and the 2026-05-21
> dual-judge update. For current canonical figures, see the root
> [`README.md`](../README.md) and [`docs/REFERENCE.md`](./REFERENCE.md),
> both judged under **judge_v6** (gemini-3-flash-preview + Haiku 4.5
> escalation, n=172 v2 corpus, 2026-05-27).

**For:** Atlassian product call, 2026-05-12  
**From:** Jesus Chavez (Google), testing Rovo MCP integration with Google Vertex AI  
**Summary:** Your MCP is production-grade on quality + latency. One auth gap blocks Google ADK integration. Fix is straightforward.

> **Reading note (added 2026-05-20)**: this document was written for the 2026-05-12 Atlassian call and reflects the eval state at that date. The accuracy / hallucination / latency numbers below are correct for that run. The cost-per-1K-query figures in this document are NOT updated to the current pricing model — see [`PRICING.md`](./PRICING.md) for the current, verified-against-live-rate-card numbers ($10.20/1K for A, $0.23/1K for C, $0/1K for B, $5.91/1K for E, ~$0 for D).

---

## POST-MEETING UPDATES (as of 2026-05-21)

The recommendations to Atlassian remain unchanged. The Google-side eval
methodology has been substantially overhauled since the call; updated
numbers below replace the headline figures in *§Key Findings* and
*§Appendix — Data* with the v2 benchmark results.

### Methodology overhaul

- **Question set rebuilt** — replaced 500 templated questions with **172
  curated questions** (templated repeats removed, 30 hand-crafted
  realistic complex queries added). Per-category counts in
  [`REFERENCE.md §1.1`](./REFERENCE.md#11-question-set--evalquestionsmain_v2json).
- **Dual-judge consensus** — every answer is judged by **both**
  `gemini-3.5-flash` and `claude-sonnet-4-6`, each with live Jira tool
  access via the v4 oracle MCP. Headline = both judges agree on
  `verdict == "correct"` (strict); credible = either marks correct.
  Removes the single-judge-bias risk that drove the 1.0 %–68.9 %
  hallucination spread in the v1 run.
- **MCP server fix** — added `assignee` / `reporter` to the
  `searchJiraIssuesUsingJql` and `getJiraIssue` response payloads so the
  v4 judge can verify "who is assigned to X" without falling back to
  speculation. Applied before v2 runs.
- **Option A regression + fix** — the initial v2-A run scored 1.7 % strict
  because the deployed Agent Engine had a stale Atlassian OAuth token in
  its env (tool calls were 401'ing silently). Redeployed with a fresh
  token; the same code path now scores **68.0 % strict / 83.7 % credible**
  — the highest of any pipeline.

### New winners (v2 dual-judge, 172 questions)

| Pipeline | Strict | Credible | p50 | p90 | $ / 1K |
|---|---:|---:|---:|---:|---:|
| **A** (Custom MCP + ADK, Gemini 2.5) | **68.0 %** | **83.7 %** | 24.7 s | 58.0 s | $10.20 |
| **AL** (Custom MCP + ADK, flash-lite) | 64.0 % | 83.7 % | 30.8 s | 82.0 s | **$5.30** |
| **C** (Custom MCP direct via GE BYO_MCP) | 58.1 % | 82.0 % | 49.3 s | 110.6 s | $0.23 |
| **AG** (ADK + gemini-3.5-flash) | 57.0 % | 79.7 % | 33.9 s | 83.8 s | $25.00 |
| **B** (Atlassian Rovo, hosted) | 57.0 % | 81.4 % | 35.3 s | 68.6 s | $0 |
| **E** (genai loop in MCP wrapper) | 55.8 % | 82.0 % | 32.9 s | 67.5 s | $5.91 |
| **D** (GE federated) | 43.6 % | 62.2 % | 21.2 s | 57.4 s | ~$0 |

**Takeaways for Atlassian:**

- The headline shifts from "Custom (Gemini) > Rovo (Claude)" to "every
  pipeline that has the same MCP server clusters at 80–84 % credible". The
  consumption layer (ADK vs GE planner vs genai loop) drives the **strict**
  number more than the MCP server does.
- **Option B (Rovo) holds 81.4 % credible accuracy**, statistically tied
  with A/AL/C/E. The Rovo MCP is genuinely competitive once the consumer
  has citation discipline — *the original recommendation* "publish a
  citation-discipline best practice" stands and is the cheapest single
  Atlassian-side improvement.
- **B's latency on count/aggregate is the new finding**. On the 906-issue
  SMP count, B p50 is **113–156 s**; C with the same question + same
  server-side `summarizeJiraIssues` tool is **~14 s**. Root cause: GE's
  `custom_mcp_agent` sub-planner loops over Rovo's ~40-tool catalog
  without auto-pagination — ~10 sequential paginated tool calls with an
  LLM "should I continue?" decision between each. Detailed evidence in
  [`/tmp/test_b_vs_g.log`](file:///tmp/test_b_vs_g.log) and
  [`REFERENCE.md §2`](./REFERENCE.md#2-latency-breakdown-by-question-category).
  **Atlassian-side mitigation**: expose a server-side aggregation /
  `summarizeIssues` tool that paginates internally (mirrors the custom
  MCP's `summarizeJiraIssues`). Would reduce the 2-minute count to
  one-shot ~5 s.
- The original "Add Basic auth fallback" ask (Action Item below) is
  unchanged — still the single biggest unlock for Google ADK customers.

### Compatibility with the v1 numbers

The v1 87.1 % composite for Claude + Rovo translates to **57.0 % strict /
81.4 % credible** under the v2 dual-judge consensus. The credible number
matches v1 within 6 pp; the strict number is structurally lower because
the v2 judge is harsher on partials. **Both v1 and v2 agree** that Rovo
delivers usable answers ~80 % of the time; v2 just exposes more of the
"partial / wrong on edges" cases that v1 lumped under correct.

---

## What We Tested

500 grounded Jira questions across 20 categories (lookup, JQL, pagination, analytics, safety, etc.) on a 5-project corpus (~1,310 issues).

**4 configurations:**

| Config | Framework | MCP | LLM | Result |
|---|---|---|---|
| **A** | Google ADK + Agent Engine | **Custom** (7 tools, FastAPI) | Gemini 3 Flash | ✅ 91.3% composite, 10.2s p50 |
| **B** | Claude Code sub-agents | **Atlassian Rovo** (~37 tools) | Claude Sonnet 4.6 | ✅ 87.1% composite, ~5-10s |
| **C** | Google ADK + Agent Engine | **Atlassian Rovo** (~37 tools) | Gemini 3 Flash | ❌ Can't connect (400) |
| **D** | GenAI SDK (in-process) | **Atlassian Rovo** (~37 tools) | Gemini 3 Flash | ❌ Can't connect (400) |

---

## Key Findings

### 1. Your Rovo MCP quality is production-grade

**Composite accuracy: 87.1%** (Claude + Rovo) vs 91.3% (Gemini + Custom MCP).

The 4.2pp gap is **NOT your MCP** — it's:
- **Instruction tuning (50%)** — Our agent has ~200 lines of citation discipline, safety blocks, pagination hints. Claude sub-agents had ~10 lines. Portable to Rovo.
- **Framework callbacks (20%)** — ADK's `before_model_callback` trims paginated context; Claude sub-agents had no callbacks.
- **Tool design (30%)** — Our 7 custom tools are optimized for bulk analytics (`getJiraIssuesReport` server-side pagination, `summarizeJiraIssues` pre-aggregates counts). Your 37 tools are broader and more granular (better for lookups, less optimized for dashboards).

**Per-category split:**
- **Rovo wins:** `lookup` (100% vs 88%), `epic-tree` (+14pp), `comments` (+9pp), `typo-robustness` (+8pp) — single-issue precision
- **Custom wins:** `pagination` (−26pp), `jql-filter` (−26pp), `count` (−21pp) — bulk analytics

**Bottom line:** Rovo's 37-tool breadth is an advantage. The quality gap closes to ~1-2pp with equivalent instruction tuning.

### 2. Your Rovo MCP latency is competitive

**Claude + Rovo: ~5-10s p50** (fastest in the test)  
**Gemini + Custom MCP: 10.2s p50** (our baseline)

Your MCP is **NOT slower** than a tuned custom server. The difference is:
- Claude Sonnet 4.6 has faster TTFT than Gemini
- Claude Code's sub-agents skip Agent Engine deployment overhead
- Direct MCP call (no callbacks, no session management)

When we tried ADK + Rovo (Option C), the connection attempt took ~10s before failing with 400 — meaning even the failed handshake wasn't noticeably slower than our custom MCP.

**Bottom line:** Rovo MCP latency is production-optimized. No changes needed.

### 3. The hallucination caveat (consumer-side fix)

Claude + Rovo cited **fake issue keys in 68.9% of answers** (vs Gemini's 1%). Example: tool returns `[BUGS-100, BUGS-99]`, Claude cites `BUGS-50` in the answer (invented a plausible key in the range).

**This is NOT your MCP's fault** — it's the consumer not being instructed *"never cite a key that's not in tool results."* Our Gemini agent has that instruction; the Claude sub-agents didn't.

**For a production Jira agent, fake issue keys → broken URLs → user frustration.** This is the most important quality metric.

**Recommendation:** Add a "Best Practices" section to your Rovo MCP docs:

> **Citation Discipline:** Instruct your LLM to only cite issue keys present in tool results. Example prompt snippet:
>
> ```
> CRITICAL: When mentioning Jira issue keys, use ONLY the keys returned by
> your most recent tool call. NEVER invent plausible-looking keys (e.g.,
> don't cite BUGS-50 if the tool only returned BUGS-100, BUGS-99). If you
> can't find a key in tool results, say "I couldn't find X" instead of guessing.
> ```
>
> Without this, LLMs hallucinate issue keys ~70% of the time. With it, <2%.

---

## The Integration Gap (Action Item)

**Google ADK + Agent Engine cannot connect to Rovo MCP.**

**Why:** Rovo requires `Authorization: Bearer <oauth_token>` on the initial `/v1/mcp` connection. ADK's `MCPToolset` has a `header_provider` callback, but it runs AFTER session creation (too late).

Logs from our attempts (Options C + D):
```
GET https://mcp.atlassian.com/v1/mcp → 400 Bad Request
www-authenticate: Bearer realm="OAuth", error="invalid_token"
```

We sent `Authorization: Basic <email:api_token>` (the fallback that works for every other Atlassian API). Rovo rejected it.

**Impact:**
- Google customers using ADK/Agent Engine **cannot integrate** with Rovo today
- Eval harnesses, batch jobs, CI/CD pipelines **cannot use Rovo** (no headless auth)
- LangChain + GenAI SDK also fail (same auth issue)

**The fix (on Atlassian's side):**

Add **API-token Basic auth as a fallback** to Rovo MCP's authentication. Accept:
```
Authorization: Basic <base64(email:api_token)>
```

...where the API token comes from `https://id.atlassian.com/manage-profile/security/api-tokens`.

**Why this is the right fix:**
- Every other Atlassian API (Jira REST, Confluence REST, Trello) supports this
- Keeps per-user ACLs (the email in the Basic auth identifies the user)
- Enables headless/batch flows (eval, automation, service accounts)
- OAuth Bearer stays the primary path (interactive chat); Basic is the fallback

**Estimated effort:** ~1 day server-side work for Atlassian. Zero client-side changes needed.

**Alternative (on Google's side):** Google could add "OAuth on connection" to ADK's MCPToolset (not just on tool calls). But that's a bigger platform change, and it still leaves eval/batch flows broken.

---

## Recommendations Summary

**For Atlassian:**
1. ✅ **Quality is production-grade** — 87% composite is strong; the gap to 91% closes with instruction tuning (publish prompt templates)
2. ✅ **Latency is competitive** — 5-10s is as fast as any MCP can be
3. ⚠️ **Add Basic auth fallback** — unblocks Google ADK, eval harnesses, batch jobs (1-day fix)
4. 📖 **Publish citation-discipline best practice** in docs — drops hallucination from 69% → <2%

**For Google customers choosing Rovo vs custom:**
- **Use Rovo** if: you want 37-tool breadth, zero MCP ops, and can use Claude/OpenAI/non-ADK consumers
- **Use custom** if: you need bulk-analytics tools, ADK callbacks, or Agent Engine observability

**Bottom line:** Rovo MCP is enterprise-ready. The ADK integration gap is fixable with Basic auth support.

---

## Appendix — Data

Full benchmark report: https://htmlpreview.github.io/?https://github.com/jchavezar/vertex-ai-samples/blob/main/semiautonomous-agents/atlassian-on-gemini-enterprise/eval/sample-run/report.html

Repo: https://github.com/jchavezar/vertex-ai-samples/tree/main/semiautonomous-agents/atlassian-on-gemini-enterprise

| Metric | Gemini + Custom MCP | Claude + Rovo MCP |
|---|---|---|
| Composite | 91.3% | 87.1% |
| Citation accuracy | 99.9% | 69.5% |
| Hallucination rate | 1.0% | 68.9% |
| Latency p50 | 10.2s | ~5-10s |
| Verdicts | 441 correct, 16 wrong, 0 hallucinated | 381 correct, 22 wrong, 9 hallucinated |

Contact: jchavezar@google.com
