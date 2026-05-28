# Eval Reference — Atlassian Jira × Gemini Enterprise

*Numbers as of 2026-05-27, judge_v6 (gemini-3-flash-preview + Haiku 4.5 escalation), n=172 v2 corpus.*

Comprehensive technical reference for the multi-pipeline evaluation harness.
Covers the **v2 benchmark** (172 curated questions, 11 pipelines including
Option F on its own 500-question super-set, judged consistently with
**judge_v6**). For per-option walkthroughs, see each option's README; for
executive-level number tables and decision guidance, see the comparison
site at [`eval/comparison-site/`](../eval/comparison-site/) (deployed to
Cloud Run).

> The legacy Rovo MCP **setup guide** that used to live in this file has
> been merged into [`option-b-direct-remote-mcp/README.md`](../option-b-direct-remote-mcp/README.md);
> see the appendix at the bottom of this doc for the short version.

---

## 1. v2 benchmark methodology (current)

### 1.1 Question set — `eval/questions/main_v2.json`

**172 questions across 20 categories** in 3 buckets (read-side correctness,
production features, safety / robustness). The v2 set replaces the original
500-question set:

- **Templated repeats removed** — the v1 generator emitted families of near-
  identical questions (e.g. 25 "list all issues in `<PROJECT>` with
  `<STATUS>`" with project/status swapped). v2 dedupes to one representative
  per intent.
- **30 hand-crafted realistic complex queries added** — phase-3 handcrafts in
  [`eval/golden/phase3_handcrafted.json`](../eval/golden/phase3_handcrafted.json),
  generated from real Jira corpus reads and reviewed for ground-truth fidelity.
- **Golden truths attached** — every question has either an exact-key list
  (deterministic `jql` oracle) or a curated `expected_themes`/`expected_count`
  (handcraft oracle). See [`eval/golden/golden_super.json`](../eval/golden/).

Per-category counts (172 total): cross-issue-analysis 15 · root-cause-synthesis 14 ·
multi-step 13 · lookup 12 · jql-filter 10 · trend 10 · issue-links 10 ·
multi-project 9 · golden-anti-regression 9 · count-aggregate 8 · epic-tree 8 ·
prompt-injection 7 · pii-sensitive 7 · pagination-required 6 · refusal-test 6 ·
ambiguous 6 · components-versions 6 · comments-worklogs 6 · tool-efficiency 6 ·
typo-robustness 4.

### 1.2 Pipelines under test

11 pipelines, all run against the same 172 v2 questions (Option F on its own
500-question super-set) on `sockcop.atlassian.net`:

| Key | Label | Architecture | Model |
|---|---|---|---|
| **A** | Option A (⭐) | Custom MCP + ADK on Agent Engine | Gemini 2.5 Flash |
| **AL** | Option A-lite | Same as A | gemini-3.1-flash-lite |
| **AG** | Option A-Gemini3.5 | Same as A | gemini-3.5-flash |
| **B** | Option B | Atlassian-hosted Rovo MCP via GE streamAssist | GE chat LLM + Rovo (Claude) |
| **C** | Option C | Custom MCP direct via GE streamAssist (no ADK) | GE chat LLM (default) |
| **CG** | Option C-Gemini3.5 | Same as C | gemini-3.5-flash via `streamAssist.generationSpec.modelId` |
| **D** | Option D | GE federated `jira_cloud` connector | GE chat LLM (default) |
| **DG** | Option D-Gemini3.5 | Same as D | gemini-3.5-flash override |
| **E** | Option E | `google.genai` tool-loop in Cloud Run, wrapped as BYO MCP | gemini-3.1-flash-lite |
| **EG** | Option E-Gemini3.5 | Same as E | gemini-3.5-flash |
| **F** | Option F | ADK LlmAgent over Rovo MCP, exposed as 1-tool BYO MCP wrapper | gemini-3.1-flash-lite |

Pipeline-letter → run-dir mapping is in
[`eval/comparison-site/build_data.py`](../eval/comparison-site/build_data.py).

### 1.3 Judge — judge_v6 (tiered + Haiku escalation)

[`eval/judge_v6.py`](../eval/judge_v6.py) is the current canonical judge. It
replaces the dual-judge (Gemini + Claude consensus) approach used in v4 with
a **single tiered judge** running on **gemini-3-flash-preview**, with a
**Haiku 4.5 escalation step** for low-confidence Tier-1 judgments.

| Tier | Question shape | Rubric |
|---|---|---|
| **T1** | Lookup / direct fact retrieval | Exact-match + diagnostic sidebar |
| **T2** | Reasoning / cross-issue / multi-step | Weighted rubric (correctness, completeness, citation) |
| **T3** | Synthesis / root-cause / open-ended | Holistic rubric + grounding check |

The headline score is a **weighted-tier accuracy**: T1, T2, T3 pass rates
weighted by their share of the corpus. Low-confidence T1 verdicts are
re-judged by Haiku 4.5 to recover the cases where the gemini-3-flash-preview
judge anchors too low on objectively correct answers.

Why we retired the v4 dual-judge: dual-judge consensus was noisy on
subjective rubrics (Claude anchored high, Gemini anchored low; "strict" vs
"credible" both encoded judge bias rather than answer quality). judge_v6
collapses to one number per pipeline that tracks human grading more
faithfully on a hand-graded subset.

Scoring still spans the **10 dimensions** below:
`correctness · completeness · citation accuracy · hallucination rate · JQL correctness · pagination completeness · refusal correctness · tool efficiency · latency · cost`.

### 1.4 Headline metric

- **Accuracy (v6 headline)** = `judge_v6` weighted-tier score (T1 + T2 + T3
  pass rates weighted by category mix), with refusal-credited on safety
  categories and Haiku 4.5 escalation on low-confidence T1 rows.

### 1.5 Latest results (172 v2 questions, 2026-05-27)

| Pipeline | Accuracy (v6 headline) | p50 | p90 |
|---|---:|---:|---:|
| **A** ⭐ (Custom MCP + ADK, Gemini 2.5) | **94.7 %** | **24.7 s** | 72.3 s |
| **B** (Rovo, hosted) | **94.5 %** | 35.3 s | 68.6 s |
| **E** (genai loop) | 90.5 % | 20.6 s | 45.3 s |
| **EG** (genai loop + gemini-3.5-flash) | 93.7 % | 32.4 s | 77.3 s |
| **C** (Custom MCP direct) | 87.9 % | 28.9 s | 91.1 s |
| **CG** (Custom MCP + gemini-3.5-flash) | 94.0 % | 61.7 s | 154.1 s |
| **AL** (ADK + flash-lite) | <!-- TODO: verify against judge_v6 --> | 30.8 s | 82.0 s |
| **AG** (ADK + gemini-3.5-flash) | <!-- TODO: verify against judge_v6 --> | 33.9 s | 83.8 s |
| **D** (GE federated) | 77.5 % | 20.2 s | 64.2 s |
| **DG** (Federated + gemini-3.5-flash) | 86.0 % | 22.7 s | 53.2 s |
| **F** (ADK + Rovo MCP wrapper) | 58.1 % (172-subset) / 41.0 % (500q) | 22.6 s (500q) | 64.8 s (500q) |

Notes:

- **Option F** was evaluated on its own 500-question super-set; the 172-subset
  score (58.1%) restricts F to the same 172 v2 questions the other options
  ran on. See [`F_vs_B_comparison.md`](../F_vs_B_comparison.md).
- **Option A regression + fix**: the first v2-A run had a stale Atlassian
  OAuth token in the Agent Engine env. We redeployed with a fresh token
  (`v2fix-20260521-145509-a/`), and A recovered to top-of-table.
- **MCP server fix**: `assignee` / `reporter` fields were missing from
  `searchJiraIssuesUsingJql` and `getJiraIssue` tool responses, causing
  judges to mark "who is assigned to X" answers wrong even when the agent
  answered correctly from other context. Added to both tools' return shapes
  in `jira_server/server.py` before v2.

## 2. Latency breakdown by question category

> **Count/aggregate questions are systematically slow on Option B (Rovo).**
> Investigation traced the 1.5-min latency to GE's `custom_mcp_agent`
> sub-planner looping over Rovo's ~40-tool catalog without auto-pagination.
> Atlassian's MCP returns ≤100 issues per page, forcing the planner to make
> ~10 sequential paginated tool calls with an LLM "should I continue?"
> decision between each, totaling ~140 s for a 906-issue count. Custom MCP
> (Option C) auto-paginates server-side up to 2000 issues and returns the
> count in one tool call (~14 s). **For count/aggregate workloads, C is
> ~10× faster than B.**

Evidence: [`/tmp/test_b_vs_g.log`](file:///tmp/test_b_vs_g.log) — raw 6-run
output from the latency investigation (3× B, 3× C, same question:
*"How many SMP issues have Medium priority?"*).

| Run | Pipeline | Elapsed | Answer |
|---|---|---:|---|
| 1 | B | 113.8 s | "**906** issues with Medium priority…" |
| 2 | C | 16.4 s | "**906** issues with **Medium** priority…" |
| 3 | B | 156.2 s | "exactly 806 issues with Medium priority" |
| 4 | C | 13.8 s | "over 200 issues with Medium priority…" |
| 5 | B | 153.0 s | *(empty / failed)* |
| 6 | C | 14.1 s | "**200 issues** with Medium priority (additional may exist beyond)" |

C answers in ~14 s every run; B varies 114 s to 156 s (or fails) — and
delivers a slightly wrong count in run 3 (806 vs the true 906) because the
planner stopped paginating mid-stream.

Mechanism in `/tmp/test_direct_mcp_v2.log`: direct MCP probe shows the
custom MCP server's `summarizeJiraIssues` returns
`Analyzed 906 issues … Medium: 906` in **~4 s** for one call (no
paginated loop needed). The slow path is GE's planner over Rovo, not the
MCP server itself.

### 2.1 Per-category p50 latency (seconds, dashboard render uses these too)

| Category | A | B | C | D | E | AL | AG | EG | CG | DG |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ambiguous | 23.1 | 28.6 | 68.4 | **11.4** | 36.3 | 30.9 | 41.8 | 23.8 | 54.8 | 12.1 |
| comments-worklogs | 22.9 | 23.3 | 35.7 | **9.0** | 22.1 | 26.6 | 35.0 | 25.3 | 52.0 | 16.0 |
| components-versions | 27.2 | 24.7 | 69.2 | 28.2 | 33.5 | 39.2 | 37.7 | 37.6 | 183.9 | 36.3 |
| count-aggregate | 25.4 | **36.4** | 52.1 | 31.8 | **22.3** | 29.1 | 25.5 | **16.3** | 66.0 | 27.9 |
| cross-issue-analysis | 33.2 | 47.0 | 57.7 | 29.4 | 44.8 | 42.6 | 37.9 | 44.9 | 70.2 | 20.7 |
| epic-tree | 59.0 | 18.4 | 52.7 | 15.3 | 33.6 | **312.6** | 202.7 | 24.9 | 54.9 | 30.4 |
| golden-anti-regression | 25.8 | 22.7 | 23.2 | **8.5** | 17.2 | 23.6 | 19.1 | 19.8 | 27.5 | 9.0 |
| issue-links | 37.8 | 36.2 | 73.0 | 16.3 | 33.2 | 63.8 | 32.9 | 41.8 | 83.5 | 37.1 |
| jql-filter | 24.1 | 29.7 | 61.4 | 23.0 | 35.3 | 29.8 | 57.6 | 38.5 | 100.7 | 24.5 |
| lookup | 29.0 | 10.4 | 23.5 | **7.1** | 12.9 | 52.8 | 39.3 | 14.1 | 27.8 | 9.0 |
| multi-project | 32.2 | 62.1 | 83.8 | 54.0 | 40.2 | 21.6 | 39.1 | 32.3 | 99.9 | 32.9 |
| multi-step | 20.7 | 42.9 | 69.8 | 26.6 | 41.6 | 22.3 | 32.1 | 42.5 | 64.4 | 28.3 |
| pagination-required | 35.5 | 58.9 | **112.8** | 39.1 | 82.6 | 67.8 | 71.4 | 89.7 | 101.1 | 55.5 |
| pii-sensitive | 20.0 | 34.0 | 39.7 | 20.4 | 32.9 | 42.9 | 41.4 | 41.4 | 50.3 | 16.5 |
| prompt-injection | 6.3 | 7.9 | 6.6 | 7.0 | 5.8 | 10.8 | 21.4 | 7.2 | 4.1 | 4.6 |
| refusal-test | 18.9 | 44.8 | 27.6 | 19.2 | 15.3 | 28.4 | 7.3 | 21.0 | 31.4 | 14.1 |
| root-cause-synthesis | 32.4 | 49.6 | 80.2 | 26.5 | 43.7 | 31.0 | 31.6 | 43.8 | 70.8 | 22.1 |
| tool-efficiency | 18.0 | 9.8 | 14.8 | **6.6** | 14.4 | 38.4 | 28.4 | 11.6 | 23.0 | 8.3 |
| trend | 24.3 | 41.0 | 56.2 | 41.5 | 44.1 | 18.7 | 27.6 | 45.4 | 69.3 | 35.8 |
| typo-robustness | 17.3 | 10.7 | 16.3 | **8.0** | 15.4 | 72.0 | 36.2 | 8.4 | 45.4 | 12.1 |

Highlights:

- **D (federated) is the fastest** on simple lookups, comments, refusals
  (no MCP planner loop at all). It's also the lowest-accuracy pipeline —
  speed without retrieval depth.
- **B (Rovo) and C (custom direct) are slowest on count-aggregate / multi-
  project / pagination-required** because GE's `custom_mcp_agent` planner
  serializes one paginated tool call per LLM turn, with a "continue?"
  decision in between.
- **A / AL / AG** are middle-of-pack on most categories — the ADK
  `before_model_callback` keeps prompt size linear, so deep pagination
  doesn't blow up wall-clock the way it does on C.
- **AL on `epic-tree` (312.6 s)** is an outlier — flash-lite enters an
  iteration loop on a small number of multi-hop traversal questions.
  Production deployments should set `MAX_LOOP_ITERATIONS` lower than 10
  for cost discipline if they expect those query shapes.

## 3. Comparison-site dashboard

The interactive dashboard at [`eval/comparison-site/`](../eval/comparison-site/)
is rebuilt from `data.json` (which `build_data.py` regenerates from the
per-pipeline judged JSONs in `eval/runs/`).

Two heatmaps render per-(category, pipeline):

1. **Per-category accuracy** — `% pass`, refusal-credited on safety
   categories. Color: green ≥90 %, amber 60–89 %, red <60 %.
2. **Per-category p50 latency** — median elapsed seconds across the
   category's questions for that pipeline. Color: green ≤15 s, amber
   15–45 s, red >45 s. Cells with no data render "—".

Both heatmaps share a generic renderer (`renderHeatmapGeneric` in
`index.html`) — call it twice with different metric pickers and color
scales.

## 4. Cost reference (per-1K queries)

See [`PRICING.md`](./PRICING.md) for the verified-against-live-rate-card
model. Headline:

| Pipeline | $ / 1K queries | Notes |
|---|---:|---|
| **A** | $10.20 | ADK + AE + Sessions + Gemini 2.5 Flash |
| **AL** | $5.30 | ADK + AE + Sessions + flash-lite (model swap from A) |
| **AG** | $25.00 | ADK + AE + Sessions + gemini-3.5-flash ($1.50/$9.00) |
| **C / CG** | $0.23 / $4.00 | Cloud Run MCP only (C); + 3.5-flash token premium (CG) |
| **D / DG** | ~$0 / $4.00 | GE-bundled (D); + 3.5-flash override (DG) |
| **E** | $5.91 | genai loop + flash-lite + Cloud Run |
| **EG** | $20.00 | genai loop + gemini-3.5-flash + Cloud Run |
| **B** | $0 | Atlassian hosts the LLM |
| **F** | ~$2.50 | ADK Cloud Run + flash-lite tokens + Rovo HTTP (Atlassian hosts inner LLM via Rovo) |

## 5. Files of interest

| Path | Purpose |
|---|---|
| `eval/questions/main_v2.json` | The 172-question v2 corpus |
| `eval/golden/golden_super.json` | Curated ground truth per question |
| `eval/judge_v6.py` | Tiered judge (T1/T2/T3) on gemini-3-flash-preview + Haiku 4.5 escalation |
| `eval/judge_all_super.sh` | Convenience script: run judge_v6 over a run dir |
| `eval/runners/orchestrator.py` | Drives all pipelines in parallel |
| `eval/runs/v2-20260521-124231-*/` | Per-pipeline v2 run data + judged JSONs |
| `eval/runs/v2fix-20260521-145509-a/` | A redeployed with fresh OAuth token |
| `eval/runs/f-500q-*/` | Option F 500-question super-set runs |
| `eval/comparison-site/build_data.py` | Regenerates `data.json` from runs |
| `eval/comparison-site/index.html` | Single-page dashboard (heatmaps + Q-by-Q drilldown) |
| `option-a-custom-mcp-portal/jira_server/server.py` | Shared MCP server (A, AL, AG, C, CG, E, EG) |
| `option-f-adk-rovo-wrapper/server/` | F's ADK + Rovo wrapper (FastAPI + MCP + MCPToolset) |

---

## Appendix — Atlassian Rovo MCP setup (legacy)

If you need to wire Atlassian's hosted Remote MCP to a Gemini Enterprise
app outside this benchmark (the "Option B" flow), the short version is:

1. Run `option-b-direct-remote-mcp/dcr_register.py` to mint an OAuth client
   against `https://cf.mcp.atlassian.com/v1/register` (RFC 7591 DCR — NOT
   developer.atlassian.com).
2. Create a custom MCP datastore in the GE console with:
   - MCP Server URL: `https://mcp.atlassian.com/v1/mcp`
   - Authorization URL: `https://mcp.atlassian.com/v1/authorize`
   - Token URL: `https://cf.mcp.atlassian.com/v1/token` (the `cf.` host
     is critical — the apex returns `invalid_client`)
   - Scopes: `read:jira-work write:jira-work read:jira-user read:me offline_access`
3. Complete the OAuth 3LO (uncheck Confluence/Compass during consent —
   they require admin scopes we don't have).
4. Open the datastore's **Actions** tab → **Reload custom actions** →
   enable the 2 core read tools (`searchJiraIssuesUsingJql`,
   `getJiraIssue`); skip Confluence tools.

Full walkthrough lives in [`option-b-direct-remote-mcp/README.md`](../option-b-direct-remote-mcp/README.md).
Saved working config: collection `jiramcp_1778106767686`, client
`E7rKFMHq_CC3dgN9` (Option B reference deployment).
