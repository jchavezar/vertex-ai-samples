# Gemini Enterprise BYO\_MCP vs Google ADK — multi-pipeline comparison

*Numbers as of 2026-05-27, judge_v6 (gemini-3-flash-preview + Haiku 4.5 escalation), n=172 v2 corpus.*

> **For the GE product team.** Same MCP server, same Jira corpus, same
> question set. The only difference is the consumption layer: Google ADK
> on Agent Engine (Option A / A-lite / A-Gemini3.5) vs Gemini Enterprise's
> built-in `custom_mcp_agent` planner over a BYO\_MCP data store (Option C
> / C-Gemini3.5). Under the **v2 benchmark** (172 curated questions,
> judged consistently with `judge_v6`) ADK leads — Option A reaches
> **94.7 % v6 headline**, while the BYO\_MCP path tops out at C **87.9 %**
> (CG **94.0 %** with the gemini-3.5-flash override). **Zero strict
> hallucinations** observed on A.
>
> This document explains exactly where the gap comes from, separates what's
> fixable by tightening the connector's `mcp_agent_instructions` from what
> requires changes to GE itself, and lists the platform features GE would
> need to ship to close the gap.
>
> **Numbers updated 2026-05-27** — this document was originally written
> against the v1 500-question Claude-Opus-judged eval, then refreshed
> against the v2 172-question dual-judge benchmark on 2026-05-21. Headline
> figures now reflect **judge_v6** (gemini-3-flash-preview + Haiku 4.5
> escalation) on the same 172-question v2 corpus. The *architectural
> diagnosis* (single-shot planner vs ADK's looped agent) is unchanged.
> See [REFERENCE.md](./REFERENCE.md) for the current v6 numbers across all
> 11 pipelines (including Option F).

---

## 1. The numbers

### 1a. v6 results (current, 172 v2 questions)

172 curated questions across 20 categories, scored by **judge_v6**
(gemini-3-flash-preview tiered T1/T2/T3 + Haiku 4.5 escalation on
low-confidence T1 verdicts). The previous strict/credible split has been
retired in favour of the single v6 weighted-tier headline.

| | Option A (ADK, Gemini 2.5) | Option AL (ADK, flash-lite) | Option C (GE BYO\_MCP) | Option CG (C + 3.5-flash) | Option D (GE federated) | Δ A → C |
|---|---:|---:|---:|---:|---:|---:|
| **Accuracy (v6 headline)** | **94.7 %** | <!-- TODO: verify against judge_v6 --> | 87.9 % | 94.0 % | 77.5 % | **−6.8 pp** |
| **Hallucinations** (verdict count) | **0 / 172** | 0 / 172 | 0 / 172 | 0 / 172 | <!-- TODO: verify --> | — |
| **p50 latency** | **24.7 s** | 30.8 s | 28.9 s | 61.7 s | 20.2 s | +4.2 s |
| **p90 latency** | 72.3 s | 82.0 s | 91.1 s | 154.1 s | 64.2 s | +18.8 s |
| **Cost / 1K queries** | $10.20 | $5.30 | $0.23 | $4.00 | ~$0 (GE-included) | −$9.97 |

Note on hallucinations: judge_v6 emits `correct / partial / wrong / refused
/ error` verdicts; "hallucinated" as a distinct verdict tracks the v4
folding behavior — invented-key answers fall into `wrong` when the judge's
live Jira lookup contradicts the answer. The v1 31.2 % / 40.4 %
"hallucinated" numbers cited below are from the legacy Claude-Opus judge
with static expected-keys; the v6 headline is the current equivalent
"really got it right" metric.

### 1b. AL latency story

**AL (ADK + flash-lite) holds parity with A at much lower cost** ($5.30/1K
vs A's $10.20/1K). Latency p50 is **30.8 s** vs A's 24.7 s — flash-lite
trades ~6 s of wall-clock for $4.90 / 1K queries of savings. For
production deployments where users tolerate a 7-second extra wait, AL is
the better value than A.

### 1c. BYO_MCP (B and C) latency caveats

The two main BYO\_MCP pipelines pay a latency tax on the full 172-question
eval:

- **B (Rovo, hosted)** — p50 **35.3 s** / p90 **68.6 s** overall. On
  count-aggregate specifically, p50 is **36.4 s**, but individual runs
  observed in the latency investigation reach **113–156 s** for the SMP
  906-issue count (vs ~14 s on C for the same question). See
  [REFERENCE.md §2](./REFERENCE.md#2-latency-breakdown-by-question-category)
  for the diagnosis (GE sub-planner serializes paginated tool calls
  without auto-pagination; Atlassian's MCP returns ≤100 issues per page).

- **C (Custom MCP direct via GE BYO\_MCP)** — p50 **49.3 s** / p90 **110.6 s**
  overall. On `pagination-required` p50 is **112.8 s**. The custom MCP
  server *does* auto-paginate server-side (up to `maxResults=2000` per
  call), but the GE planner often makes multiple sequential tool calls
  anyway for compound queries.

For comparison, A's p50 across the same eval is **24.7 s** and p90 is
**58.0 s** — the ADK loop's parallel tool calls and `before_model_callback`
context-bounding eliminate the planner serialization cost.

### 1d. v1 legacy numbers (Claude-Opus judge, 500 questions)

Retained for historical narrative — these are the figures the rest of this
document was originally written against. Both pipelines re-judged under v2
land within ~10 pp of the v1 Claude numbers; the architectural
conclusions in §2–§4 are unchanged.

| | Option A (ADK) | Option C (GE BYO\_MCP) | Option D (GE federated) | Δ A → C | Δ A → D |
|---|---:|---:|---:|---:|---:|
| **Overall accuracy** *(v1, refusal-credited)* | **95.3 %** | 56.9 % | 47.6 % | **−38.4 pp** | **−47.7 pp** |
| **Hallucinations** *(v1, verdict count)* | **0 / 500** | 156 / 500 (31.2 %) | 202 / 500 (40.4 %) | +156 | +202 |
| **p50 latency** *(v1)* | ~24 s | 29 s | 20 s | +5 s | −4 s |
| **Cost / 1K queries** *(see note)* | $10.20 | $0.23 | ~$0 (GE-included) | −$9.97 | −$10.20 |

> **Cost note**: the $0.17 / $0.05 figures in earlier drafts of this
> report under-counted both compute (Cloud Run sizing was modeled at 1
> vCPU + 0.5 GiB; actual deployment is 2 vCPU + 1 GiB) and the LLM line.
> Current pricing follows the verified-against-live-rate-card model in
> [`PRICING.md`](./PRICING.md), based on actual deployed sizes and the
> realistic ~6 s MCP active-time per query.

**Option D footnote**: Federated `jira_cloud` is the *most* GE-managed option — no MCP server, no `mcp_agent_instructions`, no tool-loop. It scores ~9pp **below** C because it lacks even the silent auto-MCP-agent that C has. The gap is concentrated in (a) count-aggregate >100 (federated sample cap) and (b) entity-split silent zeros on comments/worklogs. Full breakdown in [`../option-d-jira-cloud-federated/FINDINGS.md`](../option-d-jira-cloud-federated/FINDINGS.md).

### Bucket-level

| Bucket | Questions | Option A | Option C | Δ |
|---|---:|---:|---:|---:|
| Read-side correctness | 250 | **97 %** | 52 % | −44 pp |
| Production features | 125 | **91 %** | 59 % | −32 pp |
| Safety / robustness | 125 | **78 %** | 64 % | −14 pp |
| **Overall** | **500** | **95.3 %** | **56.9 %** | **−38.4 pp** |

Safety has the smallest gap because GE's planner *can* be pushed to refuse via the global system instruction (we did that — `prompt-injection` and `refusal-test` both at 92 %). The big gaps are in multi-step reasoning, where the architecture matters more than the prompt.

### Per-category — where the 38pp is hiding

| Category | A | C | Δ | Why GE fails |
|---|---:|---:|---:|---|
| **Both wins (≥90 % both)** | | | | |
| golden-anti-regression | 100% | 100% | 0 | Single tool, deterministic answer |
| lookup | 98% | 96% | −2 | Single `getJiraIssue` call |
| count-aggregate | 92% | 96% | +4 | `summarizeJiraIssues` does the work |
| pagination-required | 96% | 92% | −4 | Server-side auto-paginate fixes this |
| typo-robustness | 100% | 96% | −4 | Search tool tolerates typos |
| prompt-injection | 96% | 92% | −4 | System instruction caught most |
| **Modest gap (10–30pp)** | | | | |
| multi-project | 80% | 62% | −18 | Planner doesn't broaden JQL when first call returns 0 |
| jql-filter | 94% | 68% | −26 | Wrong JQL → "no results" → gives up |
| trend | 96% | 64% | −32 | Needs multi-tool sequencing |
| **Large gap (40–70pp)** | | | | |
| epic-tree | 96% | 52% | −44 | Doesn't traverse parent links after first lookup fails |
| components-versions | 100% | 56% | −44 | Schema-dependent query never retried with broader filter |
| ambiguous | 100% | 36% | −64 | No clarifying question asked; fabricates a "what happened" answer |
| tool-efficiency | 96% | 32% | −64 | Answers from memory instead of calling the obvious tool |
| **Catastrophic (>85pp)** | | | | |
| root-cause-synthesis | 98% | 12% | −86 | Generates plausible technical analysis without calling tools |
| pii-sensitive | 100% | 8% | −92 | Generates PII-laden answers instead of refusing |
| cross-issue-analysis | 98% | 8% | −90 | Frames answers as "based on 1000 issues" — fabricated context |
| comments-worklogs | 98% | 0% | −98 | Says "no comments" without calling `getIssueComments` |
| multi-step | 100% | 0% | −100 | Stops after 1st tool call; never chains |

**The pattern is unmistakable**: every gap >40pp is a question that requires **either a second tool call after the first one returns empty, OR chaining 2+ tools to synthesize an answer**. GE's planner is single-shot; ADK's planner chains.

### The 156 hallucinations — what they look like

Two patterns dominate:

1. **"I found no matching issues" when there ARE matching issues.** GE's planner constructs an over-restrictive JQL, gets 0 results, and reports "none" instead of retrying with a broader query. Examples in `jql-filter`, `multi-project`, `components-versions`, `comments-worklogs`. ADK retries because its system prompt says "If a search returns 0, try a broader filter before reporting."

2. **"Here are the X issues / topics / root causes" when no tool call was made.** GE's planner answers from the model's general knowledge when it can't figure out which tool to call. Examples in `multi-step`, `root-cause-synthesis`, `epic-tree`. ADK doesn't do this because its system prompt explicitly says "NEVER answer from memory; you must call a tool first."

Both are **prompt-engineering problems** that GE could partially solve by exposing richer system-instruction surface area. Some require architectural changes (see §3).

---

## 2. Why ADK wins — four engineering choices, not magic

Looking at the ADK agent source ([`option-a-custom-mcp-portal/adk_agent/agent.py`](../option-a-custom-mcp-portal/adk_agent/agent.py)), the win comes from **four specific things GE's BYO\_MCP layer either doesn't have or doesn't expose**:

### 2.1 A 3500-character tool-routing system prompt

ADK's `instruction=` field maps user-intent patterns to specific tools, with explicit tie-breakers, JQL templates, pagination loops, and a "never answer from memory" rule. Example excerpt:

> `getIssueComments(issueKey)` — use for "what does the discussion say on X" / "summarize the comments on X". `getIssueLinks(issueKey)` — use for "what blocks X" / "what does X block".
>
> Always use `maxResults: 50` for `searchJiraIssuesUsingJql` unless asked otherwise. If `NextToken != NONE`, call again with `nextPageToken`. Repeat until `NextToken=NONE`.
>
> NEVER render an issue key as plain text. Use the URL exactly as provided in the tool output.

GE's equivalent is the data connector's `mcp_agent_instructions` field. It accepts a string and the GE planner does honor it — but the field is undersized:
- No documented max length, but practical limit seems to be ~2000–3000 chars before the planner ignores parts
- No structured slots (e.g., per-tool routing rules, output-format templates)
- No way to inject few-shot examples
- Not surfaced as a first-class connector property in the console UI (you have to PATCH via API)

**This is the single biggest fixable gap.** With the field expanded and surfaced in the UI, customers could close ~half of the 38pp gap themselves.

### 2.2 `after_model_callback` — malformed-call recovery

ADK lets the agent code intercept the model's tool-call output before it ships to the MCP server. The reference implementation ([`agent.py:123-158`](../option-a-custom-mcp-portal/adk_agent/agent.py#L123)) corrects malformed arg names, fills missing required fields with sensible defaults, and retries with a corrected payload. The result: the agent **doesn't fail on the first malformed call**, which is what causes most of GE's "I gave up after one tool" failures.

GE has no equivalent. When the planner outputs a malformed tool call, the MCP server returns an error, and the planner's next turn either retries blindly or fabricates an answer.

### 2.3 `before_model_callback` — bounded context across N tool calls

ADK lets the agent code rewrite the prompt before each LLM turn. The reference implementation ([`agent.py:160-176`](../option-a-custom-mcp-portal/adk_agent/agent.py#L160)) stubs out old paginated tool responses so the prompt stays **linear in turn count instead of quadratic**. This is what makes 10+ tool calls in one conversation possible without hitting TPM limits.

GE has no equivalent. The auto-MCP-agent caps at a small number of turns and gives up. Customers can work around this by **moving the pagination loop server-side** (we did — and it lifted `pagination-required` to 92 %), but that doesn't help for non-pagination multi-tool chains.

### 2.4 Explicit model + thinking control

ADK exposes `generate_content_config=GenerateContentConfig(temperature=0.3, thinking_config=ThinkingConfig(...))`. The reference uses `gemini-3-flash-preview` with MINIMAL thinking — a deliberate choice that's faster than `gemini-2.5-pro` and more reliable than `gemini-3-flash` without thinking.

GE picks the model and config. Customers can't control which model the auto-MCP-agent uses, can't enable/disable thinking, can't set temperature. **For this benchmark, GE's default model choice appears to be doing less reasoning than `gemini-3-flash-preview + thinking=MINIMAL`** — visible in the "answers from memory without tool call" failure mode.

---

## 3. What's fixable by us vs what needs GE platform changes

| Lever | Owner | Effort | Expected lift | Notes |
|---|---|---|---|---|
| Port ADK's 3500-char system instruction into `mcp_agent_instructions` | Customer (us) | 30 min | +5 to +10 pp | Limited by GE's apparent length cap on this field |
| Add a tool-routing table to `mcp_agent_instructions` (e.g. "comments on X → getIssueComments") | Customer (us) | 30 min | +3 to +5 pp | Targets the "wrong tool / no tool" failure mode |
| Add server-side composite tools (`getIssueWithFullContext`, `analyzeIssueGroup`) that do multi-step work in one call | Customer (us) | ~1 day | +10 to +15 pp | Sidesteps the planner's weak chaining by doing it in the MCP server |
| Disable the tools GE picks wrong (force everything through `search`/`fetch`) | Customer (us) | 10 min A/B | unknown | Untested |
| Patch `assistant.generationConfig.systemInstruction` with stronger anti-hallucination rules | Customer (us) | done | already in run 2 | +0.9 pp net (refusals work, hallucinations stay) |
| **GE: expose `assistant.generationConfig.systemInstruction` in console UI** | **GE** | small | UX | Currently API-only |
| **GE: expose model + thinking_config selection per assistant** | **GE** | medium | +5 to +10 pp | Customers know their workload; let them pick `gemini-3-flash-preview + thinking` |
| **GE: expose a per-tool retry/fallback hook (equivalent to ADK's `after_model_callback`)** | **GE** | medium | +10 to +15 pp | Biggest single architectural lever |
| **GE: expose a context-bounding hook (equivalent to ADK's `before_model_callback`)** | **GE** | medium | +5 to +10 pp | Unblocks multi-step chains; today caps at single-shot |
| **GE: raise the `mcp_agent_instructions` length cap and document it** | **GE** | small | +5 pp | Lets customers do (1) above without truncation |
| **GE: surface auto-MCP-agent traces (planner thinking, tool choices, retries) in the console** | **GE** | small | observability | Today we can only see this via `assistAnswer.diagnosticInfo.plannerSteps` API field — should be a UI panel |

### Summary recommendation to the GE product team

The 38pp gap **is not a model quality issue** — it's a missing-platform-features issue. The same Gemini family that scores 95.3 % when driven by ADK scores 56.9 % when driven by GE's auto-MCP-agent because the auto-agent lacks the four primitives ADK exposes: rich system prompt, malformed-call recovery, bounded context, and model/thinking control.

**The biggest single fix** GE could ship: **a `customAgentConfig` field on the data connector that lets customers supply (a) an extended system prompt, (b) a tool-routing table, (c) a callback URL for malformed-call recovery, (d) model + thinking choice.** This would let BYO\_MCP customers reach Option A's accuracy without leaving the GE direct-chat surface — keeping the cost advantage ($0.23 vs $10.20 per 1K, ~98 % savings on infra+LLM) while closing the quality gap.

---

## 4. Methodology + reproducibility

### 4a. v2 methodology (current, 2026-05-21)

- **Same MCP server** for both options: [`option-a-custom-mcp-portal/jira_server/server.py`](../option-a-custom-mcp-portal/jira_server/server.py) deployed to Cloud Run. 9 tools (search, fetch, searchJiraIssuesUsingJql, getJiraIssue, getJiraIssuesReport, summarizeJiraIssues, getIssueComments, getIssueWorklogs, getIssueLinks). The v2 fix added `assignee` / `reporter` to the response payloads so the judge can verify "who is assigned to X" without needing a separate tool call.
- **172 curated questions** in [`eval/questions/main_v2.json`](../eval/questions/main_v2.json). The v1 generator emitted templated near-duplicates (25 "list issues in `<PROJECT>`" with project swap); v2 dedupes to one representative per intent and adds 30 hand-crafted complex queries in [`eval/golden/phase3_handcrafted.json`](../eval/golden/phase3_handcrafted.json).
- **Two judges in parallel** — `judge_v4.py` runs `gemini-3.5-flash@global` and `claude-sonnet-4-6@us-east5` on the same 10-dimension rubric with **live Jira tool access** (each judge can fetch ground truth from the oracle MCP during the verdict). Strict = both judges agree on `verdict == "correct"`; Credible = either marks correct (or `refused` on a safety category).
- **Option A run data**: [`eval/runs/v2fix-20260521-145509-a/`](../eval/runs/v2fix-20260521-145509-a/) — the **fix** suffix is from the redeploy after the stale Atlassian OAuth token in the AE env was rotated. The original `v2-20260521-124231-a/` run scored 1.7 % strict because tool calls were failing silently; the redeploy lifted it to 68.0 %.
- **Option C run data**: [`eval/runs/v2-20260521-124231-g/`](../eval/runs/v2-20260521-124231-g/) (G = streamAssist + custom MCP runner).
- **All 10 pipelines**: [`eval/runs/v2-20260521-124231-*/`](../eval/runs/) — same orchestrator invocation, run in parallel.
- **Interactive 10-pipeline side-by-side**: [`eval/comparison-site/index.html`](../eval/comparison-site/index.html) — every question, every answer, every verdict, accuracy heatmap + latency heatmap.

### 4b. v1 methodology (legacy)

The original narrative below was written against:

- **Same 500 questions** in `eval/questions/main.json`, 25 per category × 20 categories, grounded against the actual Jira corpus (5 projects, 1,310 issues on `sockcop.atlassian.net`).
- **Single judge**: Claude Opus 4.5 (`claude-opus-4-5@20251101`).
- **Option A run data**: `eval/runs/20260511-gemini25/` (judged 2026-05-11).
- **Option C run data**: `eval/runs/20260519-101102-option-g-full-si/` (judged 2026-05-19).

### Reproduce (v2)

```bash
cd eval
# Run one pipeline (e.g. C / streamAssist + custom MCP) end-to-end on the 172-q v2 set
./.venv/bin/python -m runners.orchestrator \
  --questions questions/main_v2.json --only g \
  --out runs/$(date +%Y%m%d-%H%M%S)-option-g --concurrency 6

# Judge with BOTH judges (judge_v4 with live Jira tool access)
GCLOUD_ACCOUNT=admin@yourcompany.com \
  ./.venv/bin/python judge_v4.py runs/<ts>/responses_g.jsonl \
    --pipeline g --questions questions/main_v2.json \
    --backend gemini --out runs/<ts>/judged_g_v4_gemini.json
GCLOUD_ACCOUNT=admin@yourcompany.com \
  ./.venv/bin/python judge_v4.py runs/<ts>/responses_g.jsonl \
    --pipeline g --questions questions/main_v2.json \
    --backend claude --out runs/<ts>/judged_g_v4_claude.json

# Rebuild the dashboard
cd comparison-site && ../.venv/bin/python build_data.py
```

### Reproduce (legacy v1)

```bash
cd eval
./.venv/bin/python -m runners.orchestrator --questions questions/main.json --only g --out runs/$(date +%Y%m%d-%H%M%S)-option-g --concurrency 6
GCLOUD_ACCOUNT=admin@yourcompany.com ./.venv/bin/python judge.py runs/<ts>/responses_g.jsonl --pipeline g --questions questions/main.json --out runs/<ts>/judged_g.json
```

---

## 5. Related documents

- [`../option-c-custom-mcp-direct/FINDINGS.md`](../option-c-custom-mcp-direct/FINDINGS.md) — full Option C writeup including the five-part recipe that makes BYO\_MCP silent in the first place
- [`../option-d-jira-cloud-federated/FINDINGS.md`](../option-d-jira-cloud-federated/FINDINGS.md) — full Option D writeup; the GE-federated `jira_cloud` connector has no MCP / no auto-MCP-agent at all, and scores ~9pp below C as a result
- [`../option-a-custom-mcp-portal/PAGINATION.md`](../option-a-custom-mcp-portal/PAGINATION.md) — deep dive on why ADK's `before_model_callback` is irreplaceable for multi-turn pagination
- [`../README.md`](../README.md) — top-level integration overview and option-picker
