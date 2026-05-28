# Option F — ADK SequentialAgent wrapping Atlassian's Rovo MCP

*Numbers as of 2026-05-27, judge_v6 (gemini-3-flash-preview + Haiku 4.5 escalation). F is evaluated on its own 500-question super-set; 172-subset score is reported for apples-to-apples comparison with A–E.*

A Cloud Run service deployed to Agent Engine that exposes a single MCP tool (`ask_rovo_jira_expert`) to Gemini Enterprise as a BYO_MCP datastore. Internally, every call runs an ADK `LlmAgent` (gemini-3.1-flash-lite) over Atlassian's hosted Rovo MCP (`mcp.atlassian.com/v1/mcp`) with a whitelisted 9-tool read surface, the Option-A 95%-tuned system prompt, PII/injection defenses, cloudId auto-resolution, and 429-aware retry.

The design rationale: keep B's vendor-native data plane (Rovo) but bolt on governance hooks (system prompt, tool allow-list, audit trace, retry) that B can't offer. The accuracy trade-off under judge_v6 is real (see §Evaluation) — F is shipped as the reference customer-deployable for accounts that require those hooks, not as a quality leader.

**Headline (judge_v6, 2026-05-27):**
- **500q super-set:** **41.0 % weighted-tier accuracy** (F's own corpus, where it was originally scored).
- **172-subset (apples-to-apples with A–E):** **58.1 %** (73 / 137 scoreable).
- **Latency:** p50 22.6 s · p90 64.8 s (measured on the 500q super-set).
- **Cost:** ~$2.50 / 1K queries (Agent Engine vCPU-hour + flash-lite tokens + Rovo HTTP).

---

## Architecture

```mermaid
flowchart TB
  user(["User in GE main chat"]):::user
  ge["Gemini Enterprise — custom_mcp_agent (single tool)"]:::ge
  store[("GE Custom MCP datastore<br/>option-f-rovo-wrapper_mcp_data")]:::store
  wrapper["Cloud Run option-f-rovo-wrapper<br/>FastAPI + StreamableHTTP /mcp<br/>single ask_rovo_jira_expert tool"]:::wrapper
  adk["ADK LlmAgent on Agent Engine<br/>gemini-3.1-flash-lite (global)<br/>9 whitelisted Rovo tools"]:::adk
  rovo["mcp.atlassian.com/v1/mcp<br/>37 hosted tools (9 used)"]:::rovo
  jira[("Atlassian Jira REST<br/>api.atlassian.com")]:::jira

  user --> ge
  ge ==>|ask_rovo_jira_expert(question)| store
  store -.->|OAuth 3LO via cf.mcp.atlassian.com| jira
  store ==> wrapper
  wrapper ==>|Authorization: Bearer rovo-oauth| adk
  adk ==>|MCPToolset / SSE| rovo
  rovo ==> jira

  classDef user fill:#FBBC04,stroke:#F29900,stroke-width:3px,color:#000
  classDef ge fill:#4285F4,stroke:#1967D2,stroke-width:3px,color:#fff
  classDef store fill:#9C27B0,stroke:#6A1B9A,stroke-width:2px,color:#fff
  classDef wrapper fill:#FF6F00,stroke:#E65100,stroke-width:3px,color:#fff
  classDef adk fill:#1A73E8,stroke:#174EA6,stroke-width:3px,color:#fff
  classDef rovo fill:#0052CC,stroke:#003D99,stroke-width:3px,color:#fff
  classDef jira fill:#0052CC,stroke:#003D99,stroke-width:2px,color:#fff
```

**OAuth model:** the connector's `auth_uri` / `token_uri` point at `cf.mcp.atlassian.com` (same DCR-minted client as Option B), so the bearer GE sends with each `/mcp` POST is already a Rovo OAuth token. The wrapper extracts it in an `AuthMiddleware` and passes it through to ADK's `MCPToolset` headers — per-user identity preserved end-to-end.

---

## Why this exists

GE's planner has two failure modes when a BYO MCP exposes canonical `search(query) + fetch(id)`:

1. It triggers the deep-research iteration pattern — 20+ sequential calls per question, blowing the 300-second timeout.
2. It runs its own per-call confirmation popup unless the [Option C five-part recipe](../option-c-custom-mcp-direct/FINDINGS.md#3-the-five-part-recipe) is applied.

A single domain-named tool (`ask_rovo_jira_expert`) sidesteps both. GE calls it **once** with the user's question verbatim; the ADK loop on the inside handles cloudId resolution, JQL planning, pagination, refusals, PII redaction, and 429 retry. The `ToolAnnotations(readOnlyHint=True, ...)` + `protocolVersion: 2025-06-18` on the wrapper's `/mcp` handler keeps GE in silent-dispatch mode.

F differs from Option E in one important axis: E runs a pure `google.genai` function-calling loop against the **custom** Jira MCP (your code, your tools); F runs an ADK `LlmAgent` against the **Atlassian-hosted** Rovo MCP. Same wrapper pattern, different upstream.

---

## What's in this folder

| Path | Purpose |
|---|---|
| `server/server.py` | FastAPI app, AuthMiddleware (Bearer capture), MCP server, single `ask_rovo_jira_expert` tool implementation, `/mcp` StreamableHTTP handler that serializes the full `Tool` (annotations + outputSchema) for GE silent-search |
| `server/agent_loop.py` | ADK `LlmAgent` + `MCPToolset(tool_filter=ROVO_TOOL_FILTER)` + 3,500-char Option-A system prompt + per-request Process trace + 429 retry with exponential backoff |
| `server/Dockerfile` | Cloud Run container |
| `server/requirements.txt` | `fastapi`, `mcp`, `google-adk`, `google-genai` |
| `register_datastore.py` | GE BYO_MCP datastore creation + engine attachment (clones Option B's pattern, points `instance_uri` at this wrapper's `/mcp`) |
| `probe_option_f.py` | Local probe to exercise the wrapper end-to-end against a real Rovo bearer |

The 9 whitelisted Rovo tools (defined in `agent_loop.ROVO_TOOL_FILTER`):
`searchJiraIssuesUsingJql`, `getJiraIssue`, `getJiraProjectIssueTypesMetadata`, `getVisibleJiraProjects`, `getTransitionsForJiraIssue`, `getJiraIssueRemoteIssueLinks`, `lookupJiraAccountId`, `atlassianUserInfo`, `getAccessibleAtlassianResources`.

---

## Key gotchas (from the source)

- **Bearer is never stored.** Each call rebuilds `MCPToolset` with the turn's token. `MCPSessionManager`'s session-pool key is hashed off headers, so two users' calls won't share an upstream Rovo session.
- **GCP project auto-detected from Cloud Run metadata.** No project ID is baked in — `_auto_detect_project()` falls back to ADC if `GCP_PROJECT` / `GOOGLE_CLOUD_PROJECT` env isn't set. Portable to any customer GCP.
- **Process trace is logs-only.** `EXPOSE_THINKING=0` (default) keeps the trace out of the user-visible answer because GE's synthesis pass aggressively strips `<details>` blocks and meta headings. The trace is always emitted to Cloud Run logs at INFO level.
- **Atlassian's "IMPORTANT:" notice must be stripped.** Rovo tool results sometimes prepend a bracketed deprecation notice — the system prompt instructs the model to silently drop it.
- **Wrapper-side semaphore is effectively off (`MAX_CONCURRENT_AGENT_RUNS=100`).** Earlier experiments at sem=3 and sem=6 both made accuracy WORSE — the bottleneck is Atlassian's per-OAuth-token throttle, not the wrapper. Cloud Run auto-scaling absorbs load better than a single-process queue.
- **Rate-limit retry on 429.** The regex `_RATE_LIMIT_PATTERNS` matches throttle phrasing in both tool observations AND the model's apology text. Up to 3 retries with 2s / 4s / 8s exponential backoff; if still throttled after retries, the wrapper REPLACES the answer with a self-contained "Atlassian is rate-limiting" message (GE preserves standalone answers but strips notices prepended above lists).
- **Rovo's tool surface is smaller than Option A's custom server.** Notably, `getJiraIssuesReport`, `summarizeJiraIssues`, `getIssueComments`, `getIssueWorklogs`, `getIssueLinks` are NOT available — the system prompt routes those questions through `searchJiraIssuesUsingJql` + `getJiraIssue` (which returns comments/links/worklogs in one payload).

---

## Tuning knobs

| Env var | Default | Effect |
|---|---|---|
| `MODEL_NAME` | `gemini-3.1-flash-lite` | Inner ADK model. Set higher (e.g. `gemini-3.5-flash`) for accuracy at ~6× token cost. |
| `MAX_AGENT_ITERATIONS` | `10` | Hard cap on ADK tool-call loop. Rovo's `searchJiraIssuesUsingJql` returns everything in one call, so 3–5 hops is typical. |
| `RATE_LIMIT_MAX_RETRIES` | `3` | Per-request 429 retry budget. 0 disables. |
| `RATE_LIMIT_BASE_DELAY_S` | `2.0` | Exponential backoff base; delays are `base × 2^attempt`. |
| `MAX_CONCURRENT_AGENT_RUNS` | `100` | Wrapper-side asyncio semaphore. Leave high — Cloud Run autoscale handles concurrency better than a single-process queue. |
| `ROVO_TIMEOUT_S` | `180` | Per-tool-call timeout to Atlassian's Rovo MCP. |
| `EXPOSE_THINKING` | `0` | If `1`, prepend a Markdown Process trace to the answer. Only useful when calling the wrapper DIRECTLY (GE strips trace blocks anyway). |

---

## Evaluation results — Option F specifically

### judge_v6 (gemini-3-flash-preview + Haiku 4.5 escalation, 2026-05-27)

| Dimension | F (500q super-set) | F (172-subset, apples-to-apples) | vs B (172q) |
|---|---:|---:|---:|
| **Headline accuracy (weighted-tier)** | **41.0 %** | **58.1 %** | −36.4 pp vs B (94.5 %) |
| Raw pass | (per-500q breakdown in `eval/option_f_benchmark/`) | 73 / 137 scoreable | 159 / 170 on B |
| Latency p50 / p90 | 22.6 s / 64.8 s | (subset latency not reported separately) | B 35.3 s / 68.6 s |
| Cost / 1K queries | ~$2.50 | ~$2.50 | B $0 (hosted) |

F's 172-subset score is computed by restricting F's 500q super-set responses to the 172 v2 questions and re-running judge_v6 on that slice — same rubric, same judge as A–E. The 500q super-set number (41.0 %) is what F was originally evaluated on; the subset number (58.1 %) is the comparable headline for the option picker.

See [`../F_vs_B_comparison.md`](../F_vs_B_comparison.md) for the dedicated F-vs-B writeup.

### Why F under-performs B on read-mostly Jira Q&A

- The Option-A system prompt was tuned against the **custom** Jira MCP's tool surface (`getJiraIssuesReport`, `summarizeJiraIssues`, etc.); Rovo doesn't expose those, so the model is routed through `searchJiraIssuesUsingJql` + `getJiraIssue` paths that the prompt only briefly addresses.
- ADK's per-turn LlmAgent adds latency-tax variance that hurts the v6 weighted-tier scoring on tail-percentile questions.
- The 9-tool whitelist removes Confluence/Compass surface that B has — fine for Jira-only workloads but eliminates B's fallback when a question is ambiguous about source.

### Where F still earns its keep

- Per-request audit trace in Cloud Run logs (cloudId resolution, every tool call/response, retry attempts) — B is opaque.
- Deterministic 429 retry — B has none.
- Tool allow-listing — B exposes Rovo's whole Jira+Confluence+Compass surface.
- System-prompt control — B has only GE Default Assistant instructions.
- Portable across customer GCP projects with zero code edits (`_auto_detect_project()`).

---

## Cleanup

```bash
gcloud run services delete option-f-rovo-wrapper --region us-central1 --project vtxdemos
# Detach + delete the datastore in the GE console: Data stores -> ... -> Delete
```

---

## Related

- **Option B** ([`../option-b-direct-remote-mcp/`](../option-b-direct-remote-mcp/)) — Rovo MCP directly to GE; same upstream, no wrapper. F's primary apples-to-apples comparator.
- **Option E** ([`../option-e-adk-wrapped-in-mcp/`](../option-e-adk-wrapped-in-mcp/)) — same wrapper pattern as F, but `google.genai` loop against the **custom** Jira MCP instead of ADK against Rovo.
- **F vs B writeup** ([`../F_vs_B_comparison.md`](../F_vs_B_comparison.md)) — dedicated apples-to-apples comparison under judge_v6.
- **Comparison site** ([`../eval/comparison-site/`](../eval/comparison-site/)) — interactive side-by-side across all options.
