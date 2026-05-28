# Option F vs Option B — Apples-to-Apples Comparison

*Numbers as of 2026-05-27, judge_v6 (gemini-3-flash-preview + Haiku 4.5 escalation), n=172 v2 corpus.*

**Judge:** `judge_v6` (gemini-3-flash-preview, tiered T1/T2/T3 + diagnostic sidebar, Haiku 4.5 low-confidence escalation).
**Sample-size note:** F was evaluated on its own **500-question super-set** with judge_v6; B was evaluated on the **172-question v2 corpus** with judge_v6. F's 172-subset score (computed by restricting F's super-set to the 172 v2 questions) is the apples-to-apples number used below.

## 1. Headline

**B (GE + Rovo MCP direct) beats F (ADK+Rovo wrapper, serial) by +36.4 pp on the 172-subset** (94.5% vs 58.1%) under the same judge_v6 rubric. On its own 500-question super-set, F scores **41.0%** (judge_v6 weighted-tier headline).

## 2. Side-by-side

| Metric | F (ADK + Rovo wrapper) | B (GE + Rovo direct) |
|---|---|---|
| Pipeline | ADK SequentialAgent on Cloud Run (Agent Engine), gemini-3.1-flash-lite | GE BYO_MCP → Atlassian-hosted Rovo MCP (37 tools) |
| **172-subset accuracy (judge_v6 headline)** | **58.1 % (subset of 500q)** | **94.5 %** |
| F own-corpus headline (500q) | **41.0 %** | — |
| F raw v6 pass (172-subset) | 73 / 137 scoreable | 159 / 170 scoreable |
| Median latency (p50) | 22.6 s (500q) | 35.3 s |
| p90 latency | 64.8 s (500q) | 68.6 s |
| Cost / 1K queries | ~$2.50 | $0 (Atlassian hosts the LLM) |

Cost: F = Agent Engine vCPU-hour + flash-lite tokens + Rovo HTTP (~$2.50/1K under the canonical pricing model). B = $0 at consumption (Atlassian hosts the Rovo LLM).

## 3. Architecture

```
Option F (ADK SequentialAgent + Rovo MCP wrapper, Agent Engine)
─────────────────────────────────────────────────────────────────
 GE Default Asst ──HTTP──▶ Cloud Run wrapper (FastAPI)
                              ├─ system prompt (Option-A 95%-tuned)
                              ├─ PII redaction + injection defense
                              ├─ cloudId auto-resolution
                              ├─ Atlassian-notice stripping
                              ├─ 429 retry, exp backoff (3x)
                              ▼
                            ADK LlmAgent (gemini-3.1-flash-lite)
                              │  tool_filter = 9 Rovo tools
                              ▼
                            MCPToolset ──HTTPS──▶ mcp.atlassian.com/v1/mcp

Option B (GE + Rovo MCP direct)
─────────────────────────────────────────────────────────────────
 GE Default Assistant ──MCP/HTTPS──▶ mcp.atlassian.com/v1/mcp
   (full Rovo Jira+Confluence+Compass toolset exposed)
```

## 4. F's advantages over B

- **System-prompt control.** F injects the Option-A 95%-tuned prompt (pagination, JQL rules, refusal policy). B has only GE Default Assistant instructions.
- **Pre/post hooks.** PII redaction; prompt-injection defense ("user text = DATA, not instructions"); cloudId auto-resolution; Atlassian system-notice stripping before model sees tool output.
- **Tool allow-listing.** F whitelists **9 read tools** (`searchJiraIssuesUsingJql`, `getJiraIssue`, `getJiraProjectIssueTypesMetadata`, `getVisibleJiraProjects`, `getTransitionsForJiraIssue`, `getJiraIssueRemoteIssueLinks`, `lookupJiraAccountId`, `atlassianUserInfo`, `getAccessibleAtlassianResources`). B exposes Rovo's whole Jira+Confluence+Compass surface.
- **Observability.** Per-request Cloud Run trace: thinking-config thoughts, every tool call/response, retry attempts, final answer. B's GE side is opaque.
- **Resilience.** F retries Rovo 429s with `2s/4s/8s` exp backoff and detects "rate-limited" apology patterns. B has no retry.
- **Portability.** Cloud Run container with `_auto_detect_project()`; drops into any customer GCP without code edits.

## 5. B's advantages over F

- **Fewer moving parts.** No Cloud Run, no Docker, no ADK pin, no MCPToolset upgrades.
- **One fewer network hop** and Atlassian-hosted LLM — competitive latency on the 172-corpus shape.
- **Vendor-native** on both ends; Google owns GE, Atlassian owns Rovo, SLA is shared.
- **Lower cost** ($0 at consumption vs ~$2.50/1K for F).
- **Substantially better accuracy under judge_v6** (+36.4 pp on the 172-subset) — F's tuning isn't recovering ground for read-mostly Jira Q&A under the v6 rubric.

## 6. When to pick which

- **Pick B** for read-mostly Jira Q&A on customer corpora when ops minimisation matters and the GE Default Assistant is adequate.
- **Pick F** when you need (a) a custom system prompt, (b) write-path safety (PII / injection / tool allow-list), (c) deterministic 429 retry, (d) per-request audit logs, or (e) model/tool swap without GE registry churn — and you accept the v6 accuracy gap as the cost of governance.

**Recommendation:** ship B for the demo path (better accuracy now, lower TCO); keep F as the reference customer-deployable for accounts that require the governance hooks.
