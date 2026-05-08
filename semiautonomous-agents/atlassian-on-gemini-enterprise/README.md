# Atlassian on Gemini Enterprise — Two Integration Patterns

Two ways to put Atlassian (Jira / Confluence) data behind a Gemini Enterprise agent, presented side-by-side so you can pick the one that fits your constraints.

| | **Option A — Custom MCP Portal** | **Option B — Direct Remote MCP** |
|---|---|---|
| Folder | [`option-a-custom-mcp-portal/`](./option-a-custom-mcp-portal/) | [`option-b-direct-remote-mcp/`](./option-b-direct-remote-mcp/) |
| Who runs the MCP server | **You** (Cloud Run) | **Atlassian** (`mcp.atlassian.com/v1/mcp`) |
| Who runs the agent | **You** (Vertex AI Agent Engine + ADK) | **Gemini Enterprise** (built-in) |
| OAuth client | Your own developer.atlassian.com OAuth 2.0 (3LO) app | Dynamic Client Registration against `cf.mcp.atlassian.com` |
| Token URL | `auth.atlassian.com/oauth/token` | `cf.mcp.atlassian.com/v1/token` (the `cf.` subdomain is mandatory) |
| Tools available | Whatever you implement (`getJiraIssuesReport`, `summarizeJiraIssues`, custom JQL helpers — all your code) | The ~37 tools Atlassian publishes via their MCP server (`searchJiraIssuesUsingJql`, `getJiraIssue`, `createJiraIssue`, Confluence search, etc.) |
| Custom logic (pagination, formatting, JQL date helpers, business rules) | **Yes — full control** | No — what Atlassian ships is what you get |
| Per-tool enable in console | N/A — agent decides | **Required** — must click "Reload custom actions" → check tools → "Enable actions" or nothing is callable |
| New Atlassian features | You implement them | Available the day Atlassian ships them |
| Setup time | Higher (build, deploy, register agent + auth) | Lower (one console flow + one curl for DCR) |
| Ongoing maintenance | You patch the MCP server, manage Cloud Run, ADK upgrades | Zero — Atlassian ships, you pull |
| Auth flow seen by user | Standard 3LO consent | DCR client + 3LO chained through `mcp.atlassian.com/v1/authorize` |
| Where the LLM runs | Gemini in your Agent Engine (your model choice, your `generate_content_config`) | Gemini Enterprise's default assistant |
| Observability | Full Vertex AI logs + Cloud Run logs + ADK traces | GE assistant logs only |
| Ideal for | Demos, prototypes, customers who want to embed business logic, pagination across thousands of issues, cross-tool orchestration | Customers who want the standard Atlassian experience with minimal lift, or who need Confluence + Jira + Compass coverage out of the box |

---

## Decision shortcuts

**Pick Option A when:**

- You need pagination over thousands of issues (Option A's `getJiraIssuesReport` paginates server-side and the agent has a `before_model_callback` that bounds LLM context — see [PAGINATION.md](./option-a-custom-mcp-portal/PAGINATION.md)).
- You need custom tools (e.g., a `summarizeJiraIssues` that aggregates by component, or a `findRelatedSlackThreads` that joins Atlassian + Slack in one tool call).
- You need to embed business rules / format / brand voice in agent instructions.
- You want the model and prompts in your control (model selection, temperature, thinking config, before/after callbacks).

**Pick Option B when:**

- You want the fastest possible time-to-value (≤ 30 min from zero to working agent).
- The Atlassian-published tool catalog covers your use case.
- You don't want to operate Cloud Run + Agent Engine.
- You need Confluence and other Atlassian products covered in addition to Jira.

**Use both when:**

- You start with B for speed, migrate to A as you discover places you need control.
- A handles deep-analysis flows; B handles "just look it up" lookups in the same engine.

---

## Common ground (both options share)

- The same Gemini Enterprise app/project — the agent picker can route to either approach in one chat.
- The same Atlassian Cloud site (the user picks which site to grant access to during 3LO consent).
- The same redirect URI Google publishes: `https://vertexaisearch.cloud.google.com/oauth-redirect`.

---

## Setup guides

- [Option A — step-by-step](./option-a-custom-mcp-portal/README.md)
- [Option B — step-by-step](./option-b-direct-remote-mcp/README.md)
- [Pagination deep-dive](./option-a-custom-mcp-portal/PAGINATION.md) (option A only)

Both guides assume project `vtxdemos`, region `us-central1`, GE engine in `global` location. Substitute your own values.

---

## Comparative evaluation

How do the two patterns actually perform? See [`eval/`](./eval/).

A reproducible benchmark over ~480 grounded Jira questions:

- Questions are mined from your real Atlassian site (no hallucinated test data — we query the corpus, then ask Claude to author questions answerable from what's actually there).
- Hybrid ground truth: deterministic for JQL-derivable questions (the generator runs the JQL and stores `expected_keys`/`expected_count`); LLM-judge for analytical ones (root-cause synthesis, trend analysis).
- Both pipelines run in parallel against the **same** GE engine via streamAssist (Option A → `agentsSpec`; Option B → `dataStoreSpecs`).
- Multi-dimensional scoring: correctness, completeness, citation accuracy, **hallucination rate** (a Jira-specific metric for fake issue keys), JQL correctness, pagination completeness, refusal correctness, tool efficiency, latency, cost.
- Side-by-side HTML report with per-category bars, latency histogram, win/loss matrix, verdict confusion, hallucination spotlight, and 20 random sample answers shown side-by-side.

Quick smoke (5 questions through both pipelines + report) takes ~3 minutes. Full run (~480 questions) ~30–60 minutes wall.

```bash
cd eval
source .venv/bin/activate
python generate_questions.py --categories lookup --n 5 --out questions/_smoke.json
python -m runners.orchestrator --questions questions/_smoke.json --out runs/_smoke
python judge.py runs/_smoke/responses_a.jsonl --pipeline a --questions questions/_smoke.json --out runs/_smoke/judged_a.json
python judge.py runs/_smoke/responses_b.jsonl --pipeline b --questions questions/_smoke.json --out runs/_smoke/judged_b.json
python report.py --run runs/_smoke
```

See [`eval/README.md`](./eval/README.md) for full reproduction recipe and [`eval/question_categories.md`](./eval/question_categories.md) for the 10 question categories and what each one tests.

---

## Interpretation guide

Don't read the headline scoreboard as "winner takes all." Each pattern is optimized for a different shape of work — the per-category bars in the report tell the real story:

- **Option A wins where you'd expect:**
  - `pagination-required` — its `getJiraIssuesReport` paginates server-side AND the agent's `before_model_callback` bounds LLM context (see [PAGINATION.md](./option-a-custom-mcp-portal/PAGINATION.md)).
  - `multi-step` and `cross-issue-analysis` — custom logic baked into the agent instruction.
  - `tool_efficiency` — purpose-built tools, fewer round-trips.
- **Option B wins where you'd expect:**
  - `lookup` and basic `jql-filter` — Atlassian's tool catalog is broader and more granular; no agent-runtime overhead.
  - Median `latency` — no agent reasoning loop in the middle.
- **Both perform similarly** on `root-cause-synthesis` (LLM reasoning quality dominates) and `trend` (date math is the bottleneck).
- **Both struggle** on `refusal-test` and `ambiguous` — neither has explicit "ask before destructive action" guardrails today.

Anomalies worth investigating:
- Option B dominating on `pagination-required` → likely a bug in your Option A `before_model_callback` config.
- Option A dominating on `lookup` → over-prompted instruction inflating latency without adding value.
- Both pipelines ≥ 50% `hallucinated` on `lookup` → check that the Cloud Run MCP is returning fresh data, not cached/stale.

The `hallucinated` verdict is Jira-specific: a confident answer with fake issue keys is worse than no answer (sends users to 404s, breaks downstream automations). Track this metric over time as the regression-prevention signal that matters most.
