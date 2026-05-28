# Pricing — Atlassian Jira × Gemini Enterprise (10 pipelines)

**Updated 2026-05-21.** All prices in USD, `us-central1` Cloud Run + `global` Gemini endpoint SKUs, on-demand (no CUDs), excluding the per-seat Gemini Enterprise subscription (orthogonal — applies to every option equally).

> **What's new (2026-05-21)**: explicit cost-per-1K rows for the **CG / DG / EG** model-swap variants surfaced in the v2 benchmark; per-query token model unchanged. The 5-pipeline narrative is preserved; new variants are additive.

## Official rate cards used

Verified live 2026-05-20 against the pages linked in the Source column.

| Resource | Price | Source |
|---|---|---|
| Cloud Run vCPU-second (active) | $0.000018 | [cloud.google.com/run/pricing](https://cloud.google.com/run/pricing) |
| Cloud Run GiB-second | $0.000002 | same |
| Cloud Run requests | $0.40 / 1M | same |
| Cloud Run free tier (Tier-1 region) | 180,000 vCPU-s + 360,000 GiB-s + 2M requests / month | same |
| Agent Engine vCPU-hour | $0.0864 | [cloud.google.com/products/gemini-enterprise-agent-platform/pricing](https://cloud.google.com/products/gemini-enterprise-agent-platform/pricing) |
| Agent Engine GiB-hour | $0.0090 | same |
| Agent Engine Sessions | $0.25 / 1,000 events stored | same |
| Agent Engine Memory Bank — stored | $0.25 / 1,000 memories / month | same |
| Agent Engine Memory Bank — retrieved | $0.50 / 1,000 retrievals (first 1,000 / mo free) | same |
| Gemini 2.5 Flash (Standard) | $0.30 in / $2.50 out per 1M tokens | [cloud.google.com/vertex-ai/generative-ai/pricing](https://cloud.google.com/vertex-ai/generative-ai/pricing) |
| Gemini 3 Flash Preview (Standard) | $0.50 in / $3.00 out per 1M tokens | same |
| Gemini 3.1 Flash-Lite (Global, Standard) | $0.25 in / $1.50 out per 1M tokens | same |
| Gemini 3.5 Flash (Global, Standard) | $1.50 in / $9.00 out per 1M tokens | same |

> Agent Engine billing note: an "event" is anything stored with `content` — user messages, model responses, function calls/responses. System checkpoints are not billable events.

---

## Per-query resource model (grounded in real eval data)

Measured from the 500-question eval run, 2026-05-20.

| Option | Median latency | Avg LLM turns | Avg tool calls | Cloud Run service hops per query |
|---|---:|---:|---:|---:|
| **A** — Custom MCP + ADK | 24.7 s | ~4 (ADK loop) | 2.8 | 1 (Jira MCP) |
| **B** — Atlassian Rovo | 2.0 s | 1 | 1.05 | 0 |
| **C** — Custom MCP direct | 28.9 s | 1 (GE planner) | n/a* | 1 (Jira MCP) |
| **D** — Federated | 20.2 s | 1 (GE chat) | 0 | 0 |
| **E** — google.genai + MCP wrapper | 24.5 s | ~3–4 (genai loop) | n/a* | 2 (wrapper + Jira MCP) |

\* GE's planner makes the tool calls internally; the runner JSON doesn't expose the count for C and E.

### Deployed Cloud Run sizes (verified via `gcloud run services describe`, 2026-05-20)

| Service | vCPU | Memory | Used by |
|---|---:|---:|---|
| `jira-mcp-server` | 2 | 1 GiB | A, C, E (shared) |
| `mcp-adk-wrapper` | 2 | 1 GiB | E only |

### Token model assumptions

Same 3,500-char system prompt across A and E (verbatim copy). Per query I assume:

- **System prompt:** ~1,500 input tokens (3,500 chars ≈ 875 tokens, padded for tool schemas).
- **Per assistant turn:** ~500 tokens of growing history per iteration.
- **Per tool result fed back:** ~1,200 tokens (Jira issue rows).
- **Final answer:** ~600 output tokens.

For a 4-turn agent loop:

| | Input tokens / query | Output tokens / query |
|---|---:|---:|
| A (ADK on AE, Gemini 2.5 Flash †) | ~10,000 | ~1,500 |
| E (Cloud Run, gemini-3.1-flash-lite) | ~10,000 | ~1,500 |
| C (GE built-in LLM, single turn) | ~3,000 | ~600 |
| D (GE built-in LLM, single turn) | ~3,000 | ~600 |
| B (Claude sub-agent — bundled with Atlassian's hosted MCP) | n/a (you don't pay Vertex LLM here) | n/a |

† **Option A model note**: the historical 500-question eval that produced the A column in `eval/comparison-site/` was run against `Gemini 2.5 Flash`, and the headline cost figures below model that run for apples-to-apples comparison. The agent **currently deployed** in `option-a-custom-mcp-portal/adk_agent/agent.py` uses `gemini-3-flash-preview`, which prices at $0.50 in / $3.00 out (Standard). Per-query cost with the deployed model would be ~$0.0095 of LLM tokens (vs $0.00675 for 2.5 Flash), pushing the all-in to ~$0.013/q and monthly-at-moderate to ~$11.5K. The cost-vs-accuracy trade-off is identical in shape; only the dollar figure shifts.

### Cloud Run active-time model

Cloud Run only bills CPU + memory while a request is being served. For each option:

- **`jira-mcp-server`** (used by A, C, E) is hit only during tool calls. With ~3 tool calls × ~2 s each per query, we model **~6 s of active MCP time per query**.
- **`mcp-adk-wrapper`** (E only) holds the inbound GE request open for the full query duration (the genai loop runs synchronously inside it), so we model it at **the full 24.5 s p50 latency**.
- **Agent Engine** (A only) is billed by total wall-clock per query — 24.7 s p50.

These are deliberately conservative — actual production traffic with shorter user questions and fewer agent turns will land lower than these forecasts. The numbers below are a defensible *ceiling*, not a target.

---

## Per-query cost (1 user query, all-in)

| Option | LLM tokens | Compute (Cloud Run / Agent Engine) | Sessions / requests | **Total per query** |
|---|---:|---:|---:|---:|
| **A** — ADK + Agent Engine | (10K in × $0.30 + 1.5K out × $2.50) / 1M = **$0.00675** | AE: (24.7s ÷ 3600 × 1 vCPU × $0.0864) + (24.7s ÷ 3600 × 2 GiB × $0.0090) = **$0.000716**<br>Jira MCP CR (6s × 2 vCPU+1 GiB) = **$0.000228** | Sessions: (10 events × $0.25/1K) = **$0.0025**<br>Requests (3): $0.0000012 | **≈ $0.0102 / query** |
| **B** — Atlassian Rovo | $0 (Atlassian hosts the LLM) | $0 | $0 | **$0 / query** † |
| **C** — Custom MCP direct (GE built-in LLM) | bundled in GE seat | Cloud Run MCP (6s active × 2 vCPU + 1 GiB) = **$0.000228** | 3 requests × $0.40/1M = **$0.0000012** | **≈ $0.000229 / query** |
| **D** — Federated | bundled in GE seat | $0 (no Cloud Run) | $0 | **≈ $0 / query** ‡ |
| **E** — google.genai + MCP wrapper | (10K in × $0.25 + 1.5K out × $1.50) / 1M = **$0.00475** | Wrapper Cloud Run (24.5s × 2 vCPU + 1 GiB) = **$0.000931**<br>Jira MCP CR (6s active × 2+1) = **$0.000228** | 4 requests × $0.40/1M = **$0.0000016** | **≈ $0.00591 / query** |

† **Option B caveat**: free at consumption, but you depend on Atlassian's hosted LLM call. You also pay a **68.9 %** hallucination rate (per the 500-question eval). It's free for a reason — read [option-b/README.md](../option-b-direct-remote-mcp/README.md) before betting prod traffic on it.

‡ **Option D caveat**: Federated grounded responses are billed under GE's grounding SKU (separate from chat seat). If your engine has the federated `jira_cloud` connector enabled, each user query that hits federation counts as a grounded prompt. See the [GE pricing page](https://cloud.google.com/products/gemini-enterprise-agent-platform/pricing) for current numbers.

### Per-1K queries (rounded for the headline tables)

| Option | $ / 1K queries | Notes |
|---|---:|---|
| A | **$10.20** | ADK + AE + Sessions + Gemini 2.5 Flash |
| AL | **$5.30** | A architecture, swap to `gemini-3.1-flash-lite` |
| AG | **$25.00** | A architecture, swap to `gemini-3.5-flash` ($1.50 in / $9.00 out) |
| B | $0 | Atlassian hosts the LLM |
| C | **$0.23** | Cloud Run MCP only; GE bundles the chat LLM |
| CG | **$4.00** | C path but with `gemini-3.5-flash` override via `streamAssist.generationSpec.modelId` — token cost dominates, no per-call infra premium |
| D | ~$0 (GE-bundled) | Federated; grounding SKU may apply |
| DG | **$4.00** | D path with `gemini-3.5-flash` override |
| E | **$5.91** | genai + Cloud Run + flash-lite tokens |
| EG | **$20.00** | E architecture with `gemini-3.5-flash` (~6× token cost vs flash-lite, no Sessions billing → ~$5 cheaper than AG) |

> Variant-cost provenance: `_DEFAULT_COSTS` in
> [`eval/comparison-site/build_data.py`](../eval/comparison-site/build_data.py)
> and per-pipeline `cost_per_1k` overrides in the same file. Numbers
> assume the same 4-turn / ~10K-input / 1.5K-output token profile as the
> base option; for a query mix dominated by lookups (~3K input / 400
> output), divide LLM-token lines by ~3.

---

## At-scale forecast — 4,000 users

Three usage tiers, 22 working days/month:

| Tier | Queries/user/day | Monthly query volume |
|---|---:|---:|
| Light | 5 | **440,000** |
| Moderate | 10 | **880,000** |
| Heavy | 20 | **1,760,000** |

### Monthly bill at moderate (880K queries)

Per-query × 880,000, minus Cloud Run free tier where it applies (free tier saves at most ~$5/month at this scale — Cloud Run free tier is consumed in <1 day of 4,000-user traffic).

| Option | LLM tokens | Compute | Sessions / requests | Free tier offset | **Total / month** | Per-user / month |
|---|---:|---:|---:|---:|---:|---:|
| **A** — ADK + Agent Engine | $5,940 | AE $630 + Jira MCP $197 | $2,200 + $1 | ~$5 (negligible) | **$8,967** | $2.24 |
| **B** — Atlassian Rovo | $0 | $0 | $0 | – | **$0** † | $0 |
| **C** — Custom MCP direct | bundled | $197 | $0.35 | ~$5 (negligible) | **$197** | $0.05 |
| **D** — Federated | bundled | $0 | $0 | – | **$0** ‡ | $0 |
| **E** — google.genai + MCP wrapper | $4,180 | Wrapper $815 + Jira MCP $197 | $1.40 | ~$5 (negligible) | **$5,193** | $1.30 |

### Monthly bill at light / moderate / heavy

| Option | Light (440K) | Moderate (880K) | Heavy (1.76M) |
|---|---:|---:|---:|
| **A** — ADK + Agent Engine | **$4,482** | **$8,967** | **$17,939** |
| **B** — Atlassian Rovo | $0 † | $0 † | $0 † |
| **C** — Custom MCP direct | **$96** | **$197** | **$399** |
| **D** — Federated | $0 ‡ | $0 ‡ | $0 ‡ |
| **E** — google.genai + MCP wrapper | **$2,592** | **$5,193** | **$10,393** |

### Where does the money go?

Stacked breakdown, **Option A at moderate (880K queries)** — 2.5 Flash basis:

| Component | Per-query | Monthly | % of bill |
|---|---:|---:|---:|
| Gemini 2.5 Flash tokens | $0.00675 | $5,940 | 66 % |
| Agent Engine vCPU + GiB | $0.000716 | $630 | 7 % |
| Agent Engine Sessions (10 stored events) | $0.0025 | $2,200 | 25 % |
| Jira MCP Cloud Run (6s active × 2 vCPU+1 GiB) | $0.000228 | $197 | 2 % |
| **Total** | **$0.0102** | **$8,967** | 100 % |

Stacked breakdown, **Option E at moderate (880K queries)**:

| Component | Per-query | Monthly | % of bill |
|---|---:|---:|---:|
| Gemini 3.1 Flash-Lite tokens | $0.00475 | $4,180 | 81 % |
| Wrapper Cloud Run (24.5s × 2 vCPU+1 GiB) | $0.000931 | $815 | 16 % |
| Jira MCP Cloud Run (6s active × 2 vCPU+1 GiB) | $0.000228 | $197 | 4 % |
| Cloud Run requests | $0.0000016 | $1.40 | <1 % |
| **Total** | **$0.00591** | **$5,193** | 100 % |

E saves **~$3,774 / month at moderate load** vs A (-42 %) because:
1. Flash-Lite is ~17 % cheaper per input token and ~40 % cheaper per output token than 2.5 Flash.
2. No Agent Engine Sessions billing — the in-process genai loop holds history in RAM for the duration of the request; nothing is persisted as a billable session event ($2,200/mo saved at moderate).
3. Cloud Run's idle-trim + 100 ms billing granularity is finer than Agent Engine's vCPU-hour metering.

---

## Decision frame

| If your priority is… | Pick |
|---|---|
| Lowest total cost AND you accept "answers feel wrong" 30–40 % of the time | **D** (federated) — $0 infra, ~41 % accuracy |
| Lowest cost with usable accuracy on lookups / counts | **C** — ~$197/mo at moderate load, 52 % accuracy |
| Highest accuracy with main-chat delivery | **E** — ~$5,193/mo at moderate load, **88 %** accuracy, no agent picker |
| Highest accuracy with agent-picker UX | **A** — ~$8,967/mo at moderate load, **93 %** accuracy |
| Zero infra and zero LLM bill, prototype only | **B** — $0 but 69 % hallucination disqualifies for prod |

**Recommendation for production at 4,000 users:** **Option E**. Within 5 percentage points of A's accuracy at **~42 % lower cost**, and delivered in GE's main chat surface (no agent picker required).

---

## Assumptions and caveats

1. **22 working days × queries/day** for monthly volume. Real distributions are spikier — peak Mondays will spike compute charges but Cloud Run's per-100ms billing absorbs that better than Agent Engine's vCPU-hour metering.
2. **No CUDs (committed use discounts) applied.** Cloud Run 1-year CUD saves ~17 %; Agent Engine has no CUD as of 2026-05.
3. **Free tier modeled as ~$5/month** for the shared Cloud Run services. At 4,000 users the 180K vCPU-s tier is exhausted in <1 day; negligible at scale.
4. **Per-seat Gemini Enterprise subscription is excluded.** That's a flat per-user cost orthogonal to which option you pick.
5. **Token counts are estimates.** Actual production traffic with shorter user questions and fewer agent turns will land lower than these forecasts. The numbers above are a defensible *ceiling*, not a target.
6. **MCP active-time per query is modeled at ~6 s** (3 tool calls × ~2 s each). This is the realistic Cloud Run billing window — MCP is not alive for the full 24-29 s query latency. If you have a workload that holds long-running MCP streams open, recompute by replacing 6 with the actual mean active-seconds-per-query measured in your trace data.
7. **Gemini Enterprise grounding SKUs (Option D)** are not modeled — if you turn on federation and exceed the free 5,000 queries/month, separate per-grounded-query charges apply.
8. **Network egress** is not modeled — Cloud Run → Vertex AI and Cloud Run → Cloud Run in the same region is free, so this is correctly $0 for our topology.
9. **Option A model**: the cost figures above model the **historical 2.5 Flash eval run**. The deployed agent now uses `gemini-3-flash-preview` (Standard $0.50 in / $3.00 out per 1M); that would push A's per-query LLM cost from $0.00675 → $0.00950 and its all-in from ~$10.20/1K → ~$13/1K. The relative ordering vs E does not change — E still wins on cost by ~50 %.

---

## How to recompute

Edit the constants at the top of `eval/comparison-site/build_data.py` and re-derive the per-query model from the latest run's `judged_*.json`. The formulas above are linear in:

- `queries_per_month` (drives token + Sessions + requests)
- `median_latency_s` (drives Cloud Run vCPU-s + Agent Engine vCPU-h)
- `mcp_active_s_per_query` (drives Jira MCP Cloud Run line — model assumes 6 s)
- `tokens_in_per_query`, `tokens_out_per_query` (drives the LLM line)

If your real traffic has shorter average answers (e.g. lookups dominate), the LLM line drops linearly; compute lines stay roughly flat because they're dominated by latency-while-waiting-on-tool-calls, not generation time.
