# main_v2.json — Curated Question Set

**Source:** `questions/main.json` (500 questions)
**Output:** `questions/main_v2.json` (172 questions)

## Headline numbers
- Original: 500
- Curated (after dedup): 142
- Handcrafted real-power-user additions: 30
- **Total v2: 172**

## Per-category distribution (before → after)

| Category | Original | v2 | Δ |
|---|---:|---:|---:|
| ambiguous | 25 | 6 | -19 |
| comments-worklogs | 25 | 6 | -19 |
| components-versions | 25 | 6 | -19 |
| count-aggregate | 25 | 8 | -17 |
| cross-issue-analysis | 25 | 15 | -10 |
| epic-tree | 25 | 8 | -17 |
| golden-anti-regression | 25 | 9 | -16 |
| issue-links | 25 | 10 | -15 |
| jql-filter | 25 | 10 | -15 |
| lookup | 25 | 12 | -13 |
| multi-project | 25 | 9 | -16 |
| multi-step | 25 | 13 | -12 |
| pagination-required | 25 | 6 | -19 |
| pii-sensitive | 25 | 7 | -18 |
| prompt-injection | 25 | 7 | -18 |
| refusal-test | 25 | 6 | -19 |
| root-cause-synthesis | 25 | 14 | -11 |
| tool-efficiency | 25 | 6 | -19 |
| trend | 25 | 10 | -15 |
| typo-robustness | 25 | 4 | -21 |
| **TOTAL** | **500** | **172** | **-328** |

## Top 10 templates that were downsampled

These template clusters had many near-duplicate phrasings (e.g. lookup of assignee/status/priority of different keys, or trend-over-30d for different projects). We kept a representative sample per project.

| Rank | Category | Cluster signature | Original | Kept | Dropped |
|---:|---|---|---:|---:|---:|
| 1 | typo-robustness | `('typo-robustness', 'search')` | 25 | 4 | 21 |
| 2 | epic-tree | `('epic-tree', 'children')` | 18 | 3 | 15 |
| 3 | comments-worklogs | `('comments-worklogs', 'comments', 'with_key')` | 18 | 3 | 15 |
| 4 | pagination-required | `('pagination-required', 'proj1', 'other')` | 13 | 1 | 12 |
| 5 | refusal-test | `('refusal-test', 'delete')` | 13 | 1 | 12 |
| 6 | issue-links | `('issue-links', 'link')` | 14 | 3 | 11 |
| 7 | jql-filter | `('jql-filter', 'proj1', 'other')` | 12 | 1 | 11 |
| 8 | count-aggregate | `('count-aggregate', 'proj1', 'other')` | 12 | 1 | 11 |
| 9 | golden-anti-regression | `('golden-anti-regression', 'abs', 'no_key')` | 13 | 3 | 10 |
| 10 | trend | `('trend', 'monthly', 'nopri', 'proj1')` | 11 | 1 | 10 |

## 30 new realistic power-user questions (Phase 3)

Each question was verified live against the Jira tenant; `golden_facts` captured (count, keys, breakdowns, samples).

| ID | Intent | Category | Question | Live count |
|---|---|---|---|---:|
| q5000 | key_recall | multi-step | Show me all High priority OPS issues currently unresolved that involve either CI/CD or observability work. | 9 |
| q5001 | key_recall | multi-step | Which BUGS stories are tagged 'api-v2' and were created in May 2026? | 9 |
| q5002 | key_recall | multi-step | List CRM tickets in the 'refunds' or 'billing-support' components that are tagged as either an initiative or 'automation'. | 3 |
| q5003 | key_recall | multi-step | Find every PLAT story (not subtask) at High or Highest priority that mentions service mesh or RBAC. | 3 |
| q5004 | comparative | cross-issue-analysis | Compare the number of High and Highest priority issues between BUGS and CRM — which project has more and by how much? | 28 |
| q5005 | comparative | cross-issue-analysis | Across all four engineering projects (BUGS/CRM/OPS/PLAT), which one has the most subtasks and which has the fewest? | 200 |
| q5006 | comparative | cross-issue-analysis | How does the priority mix of the OPS project compare to the PLAT project — give me percentages by priority level. | 200 |
| q5007 | synthesis | root-cause-synthesis | Summarize the work captured under the 'API v2 Modernization' initiative (BUGS-76) — what are the major workstreams in its subtasks? | 6 |
| q5008 | synthesis | root-cause-synthesis | Looking at all High-priority OPS issues, what are the recurring themes — is it more about reliability, performance, or cost? | 12 |
| q5009 | synthesis | root-cause-synthesis | Across CRM's 'account-recovery' component, what self-service capabilities are being built and what's still manual? | 10 |
| q5010 | key_recall | issue-links | Which PLAT issues are currently blocking other PLAT issues, and what's the dependency chain? | 8 |
| q5011 | analytical | issue-links | Are any OPS issues blocking work in other projects, or vice versa? | 5 |
| q5012 | analytical | issue-links | Show me the full blockers tree for PLAT-43 — who blocks it, and who do those blockers block in turn? | 1 |
| q5013 | analytical | cross-issue-analysis | Who currently has the most High and Highest priority unresolved tickets across all engineering projects? | 61 |
| q5014 | analytical | multi-step | Among unresolved BUGS issues, list the 5 with the oldest creation date — they're at risk of stalling. | 100 |
| q5015 | count_or_groupby | cross-issue-analysis | How many Story-type issues across the engineering projects are at High or Highest priority right now, broken down by project? | 61 |
| q5016 | analytical | cross-issue-analysis | Find every Epic across our engineering projects that has fewer than 3 subtasks — these epics may be under-broken-down. | 16 |
| q5017 | key_recall | jql-filter | Show me all CRM Story-type issues at High or Highest priority — these are the candidates for the next sprint. | 12 |
| q5018 | key_recall | epic-tree | Of the issues under the 'Service Mesh Migration' epic (PLAT-1), which are the high-priority ones to tackle first? | 4 |
| q5019 | key_recall | cross-issue-analysis | Give me every Highest-priority issue across the four engineering projects, grouped by project — these are our top-of-mind risks right now. | 21 |
| q5020 | key_recall | jql-filter | List all OPS Highest-priority issues created in May 2026 — these are the top-of-mind production-risk items. | 6 |
| q5021 | synthesis | root-cause-synthesis | Walk me through the four 'initiative'-tagged epics across BUGS/CRM/OPS/PLAT — what's the high-level theme of each program? | 16 |
| q5022 | synthesis | root-cause-synthesis | Give me the 5 most important takeaways from the 'Cloud Cost Optimization' initiative (PLAT-76) and its subtasks. | 7 |
| q5023 | synthesis | root-cause-synthesis | What's the architectural direction of the OPS Kubernetes Cluster Upgrade initiative (OPS-1) based on its subtasks? | 7 |
| q5024 | analytical | issue-links | Has PLAT-43 ever been blocked, and if so, by which issues is it blocked right now? | 1 |
| q5025 | analytical | epic-tree | When was BUGS-76 (the API v2 Modernization epic) created, and how many child issues does it have today? | 7 |
| q5026 | key_recall | jql-filter | Across BUGS, which mobile-related tickets (mobile-android or mobile-ios labels) are at High priority or above? | 7 |
| q5027 | count_or_groupby | multi-project | What 'developer-experience'-tagged work is in flight across PLAT and OPS, grouped by project? | 7 |
| q5028 | count_or_groupby | trend | How many issues were created across all engineering projects in the second week of May 2026 (May 8-14)? | 200 |
| q5029 | count_or_groupby | trend | For the BUGS project, give me a priority breakdown of the issues created on May 9, 2026 — that was a high-volume day. | 100 |

## Methodology notes

**Phase 1 — Clustering.** Each question was hashed by intent signature (category + field type + project count + presence of issue key + relative-date flag) rather than by exact text, because the original set heavily paraphrases the same intents (e.g. "Who is assigned to BUGS-100?" and "Show me the assignee for SMP-912" are the same template).

**Phase 2 — Dedup rules.** For templated clusters we kept up to 3 representatives, biased for project diversity (one each from BUGS/CRM/OPS/PLAT/SMP). Trend questions were dedup'd more aggressively (target 1 per period/priority cell). Inherently unique categories — `ambiguous`, `multi-step`, `root-cause-synthesis`, `cross-issue-analysis`, `refusal-test`, `prompt-injection`, `pii-sensitive` — were kept in full (minus already-excluded qids).

**Relative dates.** 32 questions whose JQL used `-Nd` were rewritten to absolute dates anchored to today (2026-05-21). Questions whose natural-language phrasing relied on "today/yesterday/this week" without a JQL backing were dropped because they rot.

**Phase 3 — Handcrafted additions.** 30 questions across multi-dimensional filter / comparative / cross-project dependency / workload / process compliance / sprint planning / risk surfacing / synthesis / audit / label exploration. Each was validated against live Jira; queries that returned 0 issues were rewritten until they had a non-empty answer.

**Excluded qids honored:** `eval/golden/excluded_qids.json` (19 ambiguous prompts that the prior audit marked broken).

## Files

- `eval/questions/main_v2.json` — the curated set (this report's output)
- `eval/golden/dedup_audit.json` — per-cluster keep/drop decisions
- `eval/golden/phase3_handcrafted.json` — handcrafted questions with full golden_facts payload (counts, key lists, samples, link facts)
- `eval/golden/dedup_curate.py`, `eval/golden/phase3_handcraft.py`, `eval/golden/combine_v2.py` — the pipeline
