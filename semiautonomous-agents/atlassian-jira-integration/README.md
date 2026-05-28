# Atlassian Jira + Gemini Enterprise

*Numbers as of 2026-05-27, judge_v6 (gemini-3-flash-preview + Haiku 4.5 escalation), n=172 v2 corpus.*

[![Accuracy](https://img.shields.io/badge/accuracy_v6-95%25_A_/_91%25_E-success)]()
[![Hallucination](https://img.shields.io/badge/hallucination-0%25_A_/_3%25_E-success)]()
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)]()

Six working ways to connect Atlassian Jira to Gemini Enterprise. Pick the option that matches your priorities (accuracy, cost, or speed-to-demo), then follow that option's walkthrough.

> **Reading guide**: this README compares all options at the architectural level. For the deep dives:
> - **Eval taxonomy** — what the 172-question v2 corpus actually tests (500q for F): [`eval/QUESTION_TYPES.md`](eval/QUESTION_TYPES.md)
> - **Side-by-side answers** for every question, every option: [`eval/comparison-site/`](eval/comparison-site/) (open `index.html`)
> - **Pricing math at 4,000 users**: [`docs/PRICING.md`](docs/PRICING.md)
> - **F vs B head-to-head**: [`F_vs_B_comparison.md`](F_vs_B_comparison.md)

```mermaid
flowchart LR
  user(["👤 User in GE chat"]):::user

  subgraph A ["⭐ Option A — Custom MCP + ADK Agent (agent picker)"]
    direction TB
    ge_a["Gemini Enterprise"]:::ge --> ae["ADK Agent on Agent Engine"]:::ae
    ae --> mcp_a["Cloud Run MCP — 7 tools"]:::cr
  end

  subgraph E ["🧪 Option E — ADK wrapped in custom MCP (main chat)"]
    direction TB
    ge_e["Gemini Enterprise — BYO_MCP"]:::ge --> wrap["Cloud Run wrapper — search + fetch"]:::cr
    wrap --> ae_e["ADK Agent on Agent Engine"]:::ae
    ae_e --> mcp_e["Cloud Run MCP — 7 tools"]:::cr
  end

  subgraph C ["💰 Option C — Custom MCP, direct (main chat)"]
    direction TB
    ge_c["Gemini Enterprise — BYO_MCP"]:::ge --> mcp_c["Cloud Run MCP — 7 tools"]:::cr
  end

  subgraph D ["🚀 Option D — GE federated Jira Cloud (main chat)"]
    direction TB
    ge_d["Gemini Enterprise — federated jira_cloud"]:::ge --> fed["10 per-entity datastores (GE-managed)"]:::fed
  end

  subgraph B ["⚡ Option B — Atlassian Remote MCP (main chat)"]
    direction TB
    ge_b["Gemini Enterprise"]:::ge --> rmcp["mcp.atlassian.com — 37 tools"]:::rmcp
  end

  user --> A
  user --> E
  user --> C
  user --> D
  user --> B

  A --> jira[("Atlassian Jira REST")]:::jira
  E --> jira
  C --> jira
  D --> jira
  B --> jira

  classDef user fill:#FBBC04,stroke:#F29900,stroke-width:3px,color:#000
  classDef ge fill:#4285F4,stroke:#1967D2,stroke-width:2px,color:#fff
  classDef ae fill:#1A73E8,stroke:#174EA6,stroke-width:2px,color:#fff
  classDef cr fill:#FF6F00,stroke:#E65100,stroke-width:2px,color:#fff
  classDef fed fill:#F9A825,stroke:#E65100,stroke-width:2px,color:#000
  classDef rmcp fill:#0052CC,stroke:#003D99,stroke-width:2px,color:#fff
  classDef jira fill:#0052CC,stroke:#003D99,stroke-width:2px,color:#fff
  style A fill:#E8F0FE,stroke:#1A73E8,stroke-width:3px,color:#000
  style E fill:#F3E5F5,stroke:#7B1FA2,stroke-width:3px,color:#000
  style C fill:#FFF3E0,stroke:#FF6F00,stroke-width:3px,color:#000
  style D fill:#FFF8E1,stroke:#F9A825,stroke-width:3px,color:#000
  style B fill:#FCE8E8,stroke:#D93025,stroke-width:2px,stroke-dasharray:5 3,color:#000
```

| Option | Accuracy (v6 headline) | Hallucination | Cost / 1K queries | Setup |
|---|---:|---:|---:|---:|
| **⭐ A — Custom MCP + ADK** | **94.7 %** | **0.0 %** | $10.20 | ~45 min |
| **B — Atlassian Remote (Rovo)** | **94.5 %** | 1.4 % | $0 (hosted) | ~15 min |
| **E — google.genai loop wrapped as MCP** | 90.5 % | 3.4 % | $5.91 | ~30 min |
| **C — Custom MCP direct (no ADK)** | 87.9 % | 3.4 % | $0.23 | ~30 min |
| **D — GE federated jira_cloud** | 77.5 % | 8.5 % | **~$0** | **~5 min** |
| **F — ADK + Rovo MCP wrapper** ³ | 58.1 % (172-subset) / 41.0 % (500q) | <!-- TODO: verify against judge_v6 --> | ~$2.50 | ~30 min |

> **Numbers as of 2026-05-27**, judged consistently with **judge_v6** (gemini-3-flash-preview tiered T1/T2/T3 + Haiku 4.5 low-confidence escalation, n=172 v2 corpus).
>
> **Accuracy (v6 headline)** = judge_v6 weighted-tier score. The previous strict/credible two-column split has been retired in favour of the single v6 headline metric.
>
> ³ **Option F** was evaluated on its own 500-question super-set (41.0%); the 172-subset score (58.1%) restricts F to the same 172 v2 questions the other options ran on. See [`F_vs_B_comparison.md`](F_vs_B_comparison.md).
>
> Per-1K-query cost from [`docs/PRICING.md`](docs/PRICING.md).

---

## Pick an option

| | **⭐ Option A**<br/>Custom MCP + ADK Agent | **Option B**<br/>Atlassian Remote MCP | **Option E**<br/>google.genai loop in MCP wrapper | **Option C**<br/>Custom MCP, direct to GE | **Option D**<br/>GE federated Jira Cloud | **Option F**<br/>ADK + Rovo MCP wrapper |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Accuracy (v6 headline)** *(172q v2 corpus)* | **94.7 %** | **94.5 %** | 90.5 % | 87.9 % | 77.5 % | 58.1 % (172-subset) / 41.0 % (500q) |
| **Hallucination rate** | **0.0 %** | 1.4 % | 3.4 % | 3.4 % | 8.5 % | <!-- TODO: verify against judge_v6 --> |
| **Cost / 1K queries** (all-in) | $10.20 | $0 (hosted) | $5.91 | $0.23 | ~$0 (GE-bundled) | ~$2.50 |
| **GE consumption surface** | Agent picker (sidebar) | **Main chat** | **Main chat (BYO_MCP)** | **Main chat (BYO_MCP)** | **Main chat (federated)** | **Main chat (BYO_MCP)** |
| **Infrastructure you run** | Cloud Run + Agent Engine | None | Cloud Run × 2 | Cloud Run | **None** | Cloud Run |
| **LLM model** | Gemini 2.5 Flash (ADK) | Claude Sonnet (sub-agent) | gemini-3.1-flash-lite | GE built-in chat LLM | GE built-in chat LLM | gemini-3.1-flash-lite (ADK) |
| **Setup time** | ~45 min | ~15 min | ~30 min | ~30 min | **~5 min** | ~30 min |
| **Tool count GE sees** | 7 (your code) | 37 (Atlassian's) | **1 (`ask_jira_expert`)** | 7 (your code) | 10 datastores (GE-managed) | **1 (`ask_rovo_jira_expert`)** |
| **Prompt control** | Full (ADK system prompt) | None | **Full (genai system prompt)** | Connector `mcp_agent_instructions` | **None — GE owns it** | Full (ADK + Option-A prompt) |
| **Pagination** | Custom callback | Atlassian default | **Custom (genai-loop internal)** | GE default | GE default (sample cap ≈ 50) | Rovo-managed |
| **Walkthrough** | [option-a/README.md](option-a-custom-mcp-portal/README.md) | [option-b/README.md](option-b-direct-remote-mcp/README.md) | [option-e/README.md](option-e-adk-wrapped-in-mcp/README.md) | [option-c/README.md](option-c-custom-mcp-direct/README.md) | [option-d/README.md](option-d-jira-cloud-federated/README.md) | [option-f/README.md](option-f-adk-rovo-wrapper/README.md) |

### Decision guide

- **Pick A (recommended)** if the agent-picker sidebar is acceptable and you want every last accuracy point — 0 hallucinations, top v6 score (94.7%).
- **Pick B** for the fastest path to main-chat delivery with competitive accuracy (94.5%). Atlassian-hosted, $0 at consumption. Hallucination is 1.4% with the Claude+Rovo setup we tested.
- **Pick E** if you want main-chat delivery (no agent picker) with full prompt control. The Cloud Run wrapper runs a `google.genai` function-calling loop with Option A's verbatim system prompt — single MCP tool from GE's perspective, full agent reasoning inside.
- **Pick C** for low-cost lookups + counts where multi-step reasoning isn't needed. Strong safety profile.
- **Pick D** for fastest setup (5-min wizard, zero infra). Point-lookups work; anything that requires counting > sample size, comments/worklogs, or multi-step chaining collapses. See [option-d/FINDINGS.md](option-d-jira-cloud-federated/FINDINGS.md).
- **Pick F** when you need governance hooks (custom system prompt, PII redaction, prompt-injection defense, deterministic 429 retry, per-request audit logs) on top of Rovo and accept the v6 accuracy gap as the cost of those hooks. See [`F_vs_B_comparison.md`](F_vs_B_comparison.md).

> All six options share the same OAuth model (Atlassian 3LO) and the same Gemini Enterprise app. You can deploy more than one side-by-side and compare in the same chat surface.

---

## What it does

Once any option is deployed, users ask Jira questions in Gemini Enterprise chat:

- *"Show me 10 high-priority bugs"* → real issues with keys, summaries, status
- *"What's blocking the mobile release?"* → cross-project search
- *"Create a bug: login button broken on staging"* → opens a new issue
- *"Update SMP-123 to In Progress"* → transitions

---

## Evaluation

A **172-question v2 benchmark** (500q for F) across 20 categories, scored by **judge_v6** (gemini-3-flash-preview tiered T1/T2/T3 + Haiku 4.5 low-confidence escalation). This is the data behind the decision table above — the numbers are what should drive your choice, not the marketing claims.

### Headline results (judge_v6, refusal-credited on safety categories)

| Metric | **⭐ Option A**<br/>Custom + ADK | **Option B**<br/>Atlassian Rovo | **Option E**<br/>genai loop in MCP wrap | **Option C**<br/>Custom direct | **Option D**<br/>GE federated | **Option F**<br/>ADK + Rovo wrapper |
|---|---:|---:|---:|---:|---:|---:|
| **Accuracy (v6 headline)** | **94.7 %** | **94.5 %** | 90.5 % | 87.9 % | 77.5 % | 58.1 % (172-subset) / 41.0 % (500q) |
| **Hallucination rate** *(lower is better)* | **0.0 %** | 1.4 % | 3.4 % | 3.4 % | 8.5 % | <!-- TODO: verify against judge_v6 --> |
| **Valid refusals** *(safety categories)* | 24 | 23 | 23 | 24 | 23 | <!-- TODO: verify against judge_v6 --> |
| **Latency p50 / p90** | 24.7 / 72.3 s | 35.3 / 68.6 s | 20.6 / 45.3 s | 28.9 / 91.1 s | 20.2 / 64.2 s | 22.6 / 64.8 s (500q) |
| **All-in cost / 1K queries** | $10.20 | $0 (hosted) | $5.91 | $0.23 | ~$0 (GE-bundled) | ~$2.50 |
| **Per-category breakdown** | see [comparison-site](eval/comparison-site/) | see [comparison-site](eval/comparison-site/) | see [comparison-site](eval/comparison-site/) | see [option-c/FINDINGS.md](option-c-custom-mcp-direct/FINDINGS.md) | see [option-d/FINDINGS.md](option-d-jira-cloud-federated/FINDINGS.md) | see [option-f/README.md](option-f-adk-rovo-wrapper/README.md) + [F_vs_B_comparison.md](F_vs_B_comparison.md) |

> **judge_v6** is a tiered rubric (T1 lookup / T2 reasoning / T3 synthesis) with Haiku 4.5 escalation for low-confidence Tier-1 judgments. It replaces the prior dual-judge (strict/credible) split — every option above now reports a single weighted-tier headline against the same 172 v2 questions. F was evaluated on its own 500-question super-set; the 172-subset score restricts F to the same questions.

> **Option A recipe** — ADK Agent on Agent Engine with custom MCP and a tuned 3,500-char system prompt. Top accuracy + zero hallucinations; agent-picker delivery.

> **Option B recipe** — Atlassian-hosted Rovo MCP wired into GE's main chat. $0 at consumption, 37 tools exposed, no Cloud Run, no Docker.

> **Option E recipe** — single MCP tool (`ask_jira_expert`) exposed to GE; the Cloud Run service runs a `google.genai` function-calling loop internally with the same 3,500-char system prompt as Option A. Trades a few accuracy points for ~42 % cost reduction and main-chat delivery. Full details in [option-e/README.md](option-e-adk-wrapped-in-mcp/README.md).

> **Option D nuance** — Federation pulls a ~50-document sample per query, so counts > 100 systematically under-report. Without an auto-MCP-agent in front, federated never retries when entity routing returns 0 — `comments-worklogs` and `multi-step` collapse to 0–4 %.

> **Option C nuance** — Strong on lookups, counts, refusals (≥90 %); collapses on multi-step / cross-issue / per-issue side-data (0–30 %) because GE's planner is single-shot.

> **Option B nuance** — The 1.4 % hallucination above is with Claude Sonnet sub-agents and explicit citation discipline. The same Atlassian MCP without consumer-side guardrails has run 69 % hallucination in earlier tests. The MCP is fine; consumers need to enforce "never cite a key not returned by a tool call."

> **Option F nuance** — F was designed to add governance hooks (custom prompt, PII redaction, prompt-injection defense, deterministic 429 retry, per-request audit logs) on top of Rovo. Under judge_v6 it lags B by ~36pp on the 172-subset; pick F only when those hooks justify the accuracy and cost trade-off. See [`F_vs_B_comparison.md`](F_vs_B_comparison.md).

### Methodology — what we actually tested

- **Corpus:** 50 real Jira projects with ~50 issues each, populated by `eval/build_corpus.py` (deterministic for reproducibility).
- **Questions:** 172 v2 questions for A/B/C/D/E (500 for F's own super-set) generated by `eval/generate_questions.py` across **20 categories** in 3 buckets:

  | Bucket | Categories |
  |---|---|
  | Read-side correctness (10) | lookup, jql-filter, count-aggregate, pagination-required, root-cause-synthesis, cross-issue-analysis, trend, ambiguous, multi-step, epic-tree |
  | Production features (5) | multi-project, issue-links, components-versions, comments-worklogs, golden-anti-regression |
  | Safety / robustness (5) | refusal-test, prompt-injection, pii-sensitive, typo-robustness, tool-efficiency |

  Full taxonomy: [`eval/question_categories.md`](eval/question_categories.md).

- **Ground truth:** `eval/jira_oracle.py` queries the Jira REST directly with deterministic JQL, building a per-question expected answer.
- **Judge:** `eval/judge_v6.py` runs a tiered rubric — T1 (lookup), T2 (reasoning), T3 (synthesis) — on **gemini-3-flash-preview**, with a Haiku 4.5 escalation step for low-confidence Tier-1 judgments. Scoring still spans the **10 dimensions** below:

  `correctness · completeness · citation accuracy · hallucination rate · JQL correctness · pagination completeness · refusal correctness · tool efficiency · latency · cost`

  Verdicts: `correct | partial | wrong | hallucinated | refused | error`.

- **Runners:** `eval/runners/` — one harness per option. A runs against the deployed Agent Engine, B against the GE chat surface with the Atlassian MCP wired in, C against the GE chat surface with the custom MCP datastore.

### Reproduce

```bash
cd eval
pip install -r requirements.txt
python build_corpus.py            # ~10 min to populate Jira
python generate_questions.py      # writes questions/*.jsonl
python runners/run_a.py           # ~2 h depending on TPM
python runners/run_b.py           # ~30 min
python judge.py questions/ responses_a.jsonl responses_b.jsonl
python report.py                  # writes report.html
```

### Where the results live

- **Interactive comparison site:** [`eval/comparison-site/index.html`](eval/comparison-site/index.html) — every question, every answer, every verdict, side-by-side. Filter by category, verdict, or "disagreements only".
- **Question taxonomy:** [`eval/QUESTION_TYPES.md`](eval/QUESTION_TYPES.md) — what each of the 20 categories tests, with concrete question + expected-answer examples.
- **Pricing math:** [`docs/PRICING.md`](docs/PRICING.md) — 4,000-user forecast grounded in official Google rate cards.
- **Raw judged scores:** `eval/runs/<ts>/judged_*.json` for each pipeline run.
- **Methodology README:** [`eval/README.md`](eval/README.md)

---

## Repository layout

```
atlassian-jira-integration/
├── README.md                         ← you are here
│
├── option-a-custom-mcp-portal/       ← Custom MCP + ADK agent on Agent Engine
│   ├── README.md                       walkthrough + architecture + design notes
│   ├── PAGINATION.md                   deep dive on the context-bounding callback
│   ├── adk_agent/                      ADK Agent + before_model_callback
│   ├── jira_server/                    Cloud Run MCP server (FastAPI + SSE)
│   ├── register.py                     register OAuth + agent in GE
│   └── utils/                          local OAuth helpers
│
├── option-b-direct-remote-mcp/       ← Atlassian-hosted MCP (baseline)
│   ├── README.md                       walkthrough + DCR + GE wiring
│   ├── dcr_register.py                 RFC 7591 dynamic client registration
│   └── register_datastore.py           API-driven datastore create
│
├── option-c-custom-mcp-direct/       ← Custom MCP via GE BYO_MCP (no ADK)
│   ├── README.md                       walkthrough + the 5-part recipe
│   └── (reuses option-a/jira_server)
│
├── option-d-jira-cloud-federated/    ← GE federated jira_cloud connector (no Cloud Run, no MCP)
│   ├── README.md                       5-min wizard + granular OAuth scopes gotcha
│   └── FINDINGS.md                     500-Q eval + architectural ceilings
│
├── option-e-adk-wrapped-in-mcp/      ← google.genai loop in a Cloud Run MCP wrapper
│   ├── README.md                       walkthrough + architecture
│   ├── server/                         FastAPI + MCP + genai function-calling loop
│   └── register_datastore.py           GE BYO_MCP datastore creation
│
├── option-f-adk-rovo-wrapper/        ← ADK LlmAgent over Rovo MCP, exposed as 1-tool wrapper
│   ├── README.md                       walkthrough + architecture + tuning knobs
│   ├── server/                         FastAPI + MCP + ADK LlmAgent + Rovo MCPToolset
│   └── register_datastore.py           GE BYO_MCP datastore creation
│
├── eval/                              172-question (v2) comparative benchmark, 500q for F
│   ├── QUESTION_TYPES.md               taxonomy with examples (per-category)
│   ├── comparison-site/                interactive 5-option HTML report
│   └── runs/                           per-run responses + judged scores
│
├── docs/
│   ├── PRICING.md                      4,000-user pricing forecast (this option, all 5)
│   ├── GE_VS_ADK_REPORT.md             A vs C vs D — for the GE product team
│   ├── ATLASSIAN_CALL_2026-05-12.md    Findings & recommendations for Atlassian
│   └── REFERENCE.md                    consolidated tech reference (Rovo MCP setup)
│
└── scripts/                           OAuth + config helpers
```

---

## Prerequisites (any option)

- Google Cloud project with **Gemini Enterprise** enabled
- Atlassian Jira Cloud site with admin access
- `gcloud` CLI authed with **Owner** on the project
- Python 3.10+ with pip
- IAM roles needed for A and C: `roles/aiplatform.user`, `roles/run.admin`, `roles/storage.admin`. Option B needs no GCP services beyond GE itself.

---

## Related projects

- [`agent-gateway-demo/`](../agent-gateway-demo/) — Add Agent Gateway + IAP enforcement in front of any of these
- [`streamassist-oauth-flow-sharepoint/`](../streamassist-oauth-flow-sharepoint/) — Same OAuth pattern for SharePoint
- [`observability-orchestra/`](../observability-orchestra/) — Multi-tenant OAuth agent reference

---

**Authors:** Google Cloud AI Demos Team — **Last updated:** 2026-05-27 — **Target:** Gemini Enterprise + Atlassian Jira Cloud
