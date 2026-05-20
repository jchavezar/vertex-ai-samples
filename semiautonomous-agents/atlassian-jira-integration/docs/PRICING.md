# Pricing — Atlassian Jira × Gemini Enterprise (5 options)

**Updated 2026-05-20.** All prices in USD, `us-central1` SKUs, on-demand (no CUDs), excluding the per-seat Gemini Enterprise subscription (orthogonal — applies to every option equally).

## Official rate cards used

| Resource | Price | Source |
|---|---|---|
| Cloud Run vCPU-second (active) | $0.000018 | [cloud.google.com/run/pricing](https://cloud.google.com/run/pricing) |
| Cloud Run GiB-second | $0.000002 | same |
| Cloud Run requests | $0.40 / 1M | same |
| Cloud Run free tier | 180,000 vCPU-s + 360,000 GiB-s + 2M requests / month | same |
| Agent Engine vCPU-hour | $0.0864 | [cloud.google.com/products/gemini-enterprise-agent-platform/pricing](https://cloud.google.com/products/gemini-enterprise-agent-platform/pricing) |
| Agent Engine GiB-hour | $0.0090 | same |
| Agent Engine Sessions | $0.25 / 1,000 stored events | same |
| Agent Engine Memory Bank stored | $0.25 / 1,000 memories / month | same |
| Agent Engine Memory Bank retrieved | $0.50 / 1,000 retrievals | same |
| Gemini 3.1 Flash-Lite | $0.25 in / $1.50 out per 1M tokens | [cloud.google.com/vertex-ai/generative-ai/pricing](https://cloud.google.com/vertex-ai/generative-ai/pricing) |
| Gemini 2.5 Flash | $0.30 in / $2.50 out per 1M tokens | same |

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

### Token model assumptions

Same 3,500-char system prompt across A and E (verbatim copy). Per query I assume:

- **System prompt:** ~1,500 input tokens (3,500 chars ≈ 875 tokens, padded for tool schemas).
- **Per assistant turn:** ~500 tokens of growing history per iteration.
- **Per tool result fed back:** ~1,200 tokens (Jira issue rows).
- **Final answer:** ~600 output tokens.

For a 4-turn agent loop:

| | Input tokens / query | Output tokens / query |
|---|---:|---:|
| A (ADK on AE, Gemini 2.5 Flash) | ~10,000 | ~1,500 |
| E (Cloud Run, gemini-3.1-flash-lite) | ~10,000 | ~1,500 |
| C (GE built-in LLM, single turn) | ~3,000 | ~600 |
| D (GE built-in LLM, single turn) | ~3,000 | ~600 |
| B (Claude sub-agent — bundled with Atlassian's hosted MCP) | n/a (you don't pay Vertex LLM here) | n/a |

These are deliberately conservative — actual production traffic will be smaller (less history per turn). Real bills should come in at or below these estimates.

---

## Per-query cost (1 user query, all-in)

| Option | LLM tokens | Compute (Cloud Run / Agent Engine) | Sessions / requests | **Total per query** |
|---|---:|---:|---:|---:|
| **A** — ADK + Agent Engine | (10K in × $0.30 + 1.5K out × $2.50) / 1M = **$0.00675** | AE: (24.7s ÷ 3600 × 1 vCPU × $0.0864) + (24.7s ÷ 3600 × 2 GiB × $0.0090) = **$0.000717** | Sessions: (~10 events × $0.25/1K) = **$0.0025** | **≈ $0.00997 / query** |
| **B** — Atlassian Rovo | $0 (Atlassian hosts the LLM) | $0 | $0 | **$0 / query** † |
| **C** — Custom MCP direct (GE built-in LLM) | bundled in GE seat | Cloud Run MCP: (28.9s × 1 vCPU × $0.000018) + (28.9s × 0.5 GiB × $0.000002) = **$0.000550** | 2 requests × $0.40/1M = **$0.0000008** | **≈ $0.000551 / query** |
| **D** — Federated | bundled in GE seat | $0 (no Cloud Run) | $0 | **≈ $0 / query** (orthogonal grounding charges may apply) |
| **E** — google.genai + MCP wrapper | (10K in × $0.25 + 1.5K out × $1.50) / 1M = **$0.00475** | Wrapper Cloud Run: (24.5s × 2 vCPU × $0.000018) + (24.5s × 1 GiB × $0.000002) = **$0.000931**<br>Jira MCP: 0.000550 (as C) | 3 requests × $0.40/1M = **$0.0000012** | **≈ $0.00623 / query** |

† **Option B caveat**: free at consumption, but you depend on Atlassian's hosted LLM call. You also pay a **68.9 %** hallucination rate (per the 500-question eval). It's free for a reason — read [option-b/README.md](../option-b-direct-remote-mcp/README.md) before betting prod traffic on it.

‡ **Option D caveat**: Federated grounded responses are billed under GE's grounding SKU (separate from chat seat). If your engine has the federated `jira_cloud` connector enabled, each user query that hits federation counts as a grounded prompt. See the [GE pricing page](https://cloud.google.com/products/gemini-enterprise-agent-platform/pricing) for current numbers.

---

## At-scale forecast — 4,000 users

Three usage tiers, 22 working days/month:

| Tier | Queries/user/day | Monthly query volume |
|---|---:|---:|
| Light | 5 | **440,000** |
| Moderate | 10 | **880,000** |
| Heavy | 20 | **1,760,000** |

### Monthly bill at moderate (880K queries)

| Option | LLM tokens | Compute | Sessions / requests | Free tier offset | **Total / month** | Per-user / month |
|---|---:|---:|---:|---:|---:|---:|
| **A** — ADK + Agent Engine | $5,940 | $630 | $2,200 | none | **$8,770** | $2.19 |
| **B** — Atlassian Rovo | $0 | $0 | $0 | – | **$0** † | $0 |
| **C** — Custom MCP direct | bundled | $484 | $0.70 | -$3.24 vCPU + -$0.65 RAM + -$0.80 reqs | **$480** | $0.12 |
| **D** — Federated | bundled | $0 | $0 | – | **$0** ‡ | $0 |
| **E** — google.genai + MCP wrapper | $4,180 | $1,303 | $1.06 | -$3.24 vCPU + -$0.72 RAM + -$0.80 reqs | **$5,484** | $1.37 |

### Monthly bill at light / moderate / heavy

| Option | Light (440K) | Moderate (880K) | Heavy (1.76M) |
|---|---:|---:|---:|
| **A** — ADK + Agent Engine | **$4,385** | **$8,770** | **$17,541** |
| **B** — Atlassian Rovo | $0 † | $0 † | $0 † |
| **C** — Custom MCP direct | **$242** | **$484** | **$968** |
| **D** — Federated | $0 ‡ | $0 ‡ | $0 ‡ |
| **E** — google.genai + MCP wrapper | **$2,742** | **$5,484** | **$10,967** |

### Where does the money go?

Stacked breakdown, **Option A at moderate (880K queries)**:

| Component | Per-query | Monthly | % of bill |
|---|---:|---:|---:|
| Gemini 2.5 Flash tokens | $0.00675 | $5,940 | 68 % |
| Agent Engine vCPU + GiB | $0.000717 | $630 | 7 % |
| Agent Engine Sessions (10 stored events) | $0.0025 | $2,200 | 25 % |
| **Total** | $0.00997 | **$8,770** | 100 % |

Stacked breakdown, **Option E at moderate (880K queries)**:

| Component | Per-query | Monthly | % of bill |
|---|---:|---:|---:|
| Gemini 3.1 Flash-Lite tokens | $0.00475 | $4,180 | 76 % |
| Wrapper Cloud Run | $0.000931 | $819 | 15 % |
| Jira MCP Cloud Run | $0.000550 | $484 | 9 % |
| Cloud Run requests | $0.0000012 | $1.06 | <1 % |
| **Total** | $0.00623 | **$5,484** | 100 % |

E saves **~$3,286 / month at moderate load** vs A (-37 %) because:
1. Flash-Lite is ~30 % cheaper per token than 2.5 Flash on input and ~40 % on output.
2. No Agent Engine Sessions billing — the in-process genai loop holds history in RAM for the duration of the request; nothing is persisted as a billable session event.
3. Cloud Run's idle-trim + 100ms billing granularity is finer than Agent Engine's vCPU-hour metering.

---

## Decision frame

| If your priority is… | Pick |
|---|---|
| Lowest total cost AND you accept "answers feel wrong" 30–40 % of the time | **D** (federated) — $0 infra, ~41 % accuracy |
| Lowest cost with usable accuracy on lookups / counts | **C** — ~$480/mo at moderate load, 52 % accuracy |
| Highest accuracy with main-chat delivery | **E** — ~$5,484/mo at moderate load, **88 %** accuracy, no agent picker |
| Highest accuracy with agent-picker UX | **A** — ~$8,770/mo at moderate load, **93 %** accuracy |
| Zero infra and zero LLM bill, prototype only | **B** — $0 but 69 % hallucination disqualifies for prod |

**Recommendation for production at 4,000 users:** **Option E**. Within 5 percentage points of A's accuracy at **~37 % lower cost**, and delivered in GE's main chat surface (no agent picker required).

---

## Assumptions and caveats

1. **22 working days × queries/day** for monthly volume. Real distributions are spikier — peak Mondays will spike compute charges but Cloud Run's per-100ms billing absorbs that better than Agent Engine's vCPU-hour metering.
2. **No CUDs (committed use discounts) applied.** Cloud Run 1-year CUD saves ~17 %; Agent Engine has no CUD as of 2026-05.
3. **Free tier modeled only against the smallest workload.** At 4,000 users the Cloud Run free tier (180K vCPU-s) is exhausted in <1 day; effectively zero impact at scale.
4. **Per-seat Gemini Enterprise subscription is excluded.** That's a flat per-user cost orthogonal to which option you pick.
5. **Token counts are estimates.** Actual production traffic with shorter user questions and fewer agent turns will land lower than these forecasts. The numbers above are a defensible *ceiling*, not a target.
6. **Gemini Enterprise grounding SKUs (Option D)** are not modeled — if you turn on federation and exceed the free 5,000 queries/month, separate per-grounded-query charges apply.
7. **Network egress** is not modeled — Cloud Run → Vertex AI and Cloud Run → Cloud Run in the same region is free, so this is correctly $0 for our topology.

---

## How to recompute

Edit the constants at the top of `eval/comparison-site/build_data.py` and re-derive the per-query model from the latest run's `judged_*.json`. The formulas above are linear in:

- `queries_per_month` (drives token + Sessions + requests)
- `median_latency_s` (drives Cloud Run vCPU-s + Agent Engine vCPU-h)
- `tokens_in_per_query`, `tokens_out_per_query` (drives the LLM line)

If your real traffic has shorter average answers (e.g. lookups dominate), the LLM line drops linearly; compute lines stay roughly flat because they're dominated by latency-while-waiting-on-tool-calls, not generation time.
