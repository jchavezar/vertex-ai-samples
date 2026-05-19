# Comparative Evaluation Harness

500 grounded Jira questions × 20 categories, scored on 10 dimensions by Claude Opus.

**Latest result:** [`sample-run/`](./sample-run/) — Gemini 2.5 + Custom MCP **94.5%** vs Claude Code + Rovo MCP **87.1%**

[**View the report** ↗](https://htmlpreview.github.io/?https://github.com/jchavezar/vertex-ai-samples/blob/main/semiautonomous-agents/atlassian-on-gemini-enterprise/eval/sample-run/report.html)

---

## What gets tested

**20 categories across 3 buckets:**

| Bucket | Categories |
|---|---|
| **Read-side correctness** (10) | lookup, jql-filter, count-aggregate, pagination-required, root-cause-synthesis, cross-issue-analysis, trend, ambiguous, multi-step, epic-tree |
| **Production features** (5) | multi-project, issue-links, components-versions, comments-worklogs, golden-anti-regression |
| **Safety / robustness** (5) | refusal-test, prompt-injection, pii-sensitive, typo-robustness, tool-efficiency |

Full taxonomy: [`question_categories.md`](./question_categories.md)

**10 dimensions per question:**

correctness · completeness · citation accuracy · hallucination rate · JQL correctness · pagination completeness · refusal correctness · tool efficiency · latency · cost

Verdicts: `correct | partial | wrong | hallucinated | refused | error`

---

## Quick reproduction

```bash
source .venv/bin/activate

# (one-time) create test corpus: 4 Jira projects + ~400 issues
python build_corpus.py

# generate 500 grounded questions
python generate_questions.py --n 25 --out questions/main.json

# run both pipelines in parallel
python -m runners.orchestrator --questions questions/main.json --out runs/<timestamp>

# judge both pipelines
python judge.py runs/<ts>/responses_a.jsonl --pipeline a --questions runs/<ts>/questions.json --out runs/<ts>/judged_a.json
python judge.py runs/<ts>/responses_b.jsonl --pipeline b --questions runs/<ts>/questions.json --out runs/<ts>/judged_b.json

# render HTML report
python report.py --run runs/<ts> --questions runs/<ts>/questions.json

# open it
xdg-open runs/<ts>/report.html
```

Takes ~30-90 min depending on concurrency settings.

---

## Configuration

Edit `.env` (template in `.env.example`):

```
GE_PROJECT_ID=vtxdemos
GE_PROJECT_NUMBER=254356041555
OPTION_A_AGENT_ID=1666248848999186432
OPTION_B_DATASTORE_ID=mcp-jira_1778158685439_mcp_data
OPTION_G_DATASTORE_ID=custom-mcp-jira_1779142849168_mcp_data   # Custom MCP via streamAssist (no ADK)

ATLASSIAN_SITE_URL=https://sockcop.atlassian.net
ATLASSIAN_EMAIL=admin@jesusarguelles.demo.altostrat.com
ATLASSIAN_API_TOKEN=<from id.atlassian.com/manage-profile/security/api-tokens>

JUDGE_REGION=us-east5
JUDGE_MODEL=claude-opus-4-5@20251101
EVAL_CONCURRENCY=6
```

---

## Option G — streamAssist + Custom MCP (no ADK)

Added 2026-05-19. Same Cloud Run MCP server as Option A, but consumed via GE's `streamAssist` endpoint directly — no Agent Engine, no ADK agent. See [`../option-c-custom-mcp-direct/README.md`](../option-c-custom-mcp-direct/README.md) for the five-part recipe that makes this silent (no per-call confirmation popup).

Runner: [`runners/run_option_g.py`](./runners/run_option_g.py)

```bash
# Smoke test (5 questions)
GCLOUD_ACCOUNT=admin@yourcompany.com \
  ./.venv/bin/python -m runners.orchestrator \
    --questions questions/_smoke.json --smoke 5 --only g \
    --out runs/_smoke-g --concurrency 3

# Full 500
GCLOUD_ACCOUNT=admin@yourcompany.com \
  ./.venv/bin/python -m runners.orchestrator \
    --questions questions/main.json --only g \
    --out runs/$(date +%Y%m%d-%H%M%S)-option-g-full --concurrency 6
```

**Auth gotcha**: `GCLOUD_ACCOUNT` must be the gcloud-active user that completed the Atlassian OAuth 3LO in the GE console (i.e., the user the connector's refresh token is bound to). On GCE the default ADC resolves to the compute SA, which has no Jira refresh token tied to the connector — the runner returns "I am currently unable to retrieve" answers. The `_common._gcp_token()` helper reads `GCLOUD_ACCOUNT` and shells out to `gcloud auth print-access-token --account ...` to force the right identity.

Judge + report the same way as Options A/B:

```bash
./.venv/bin/python judge.py runs/<ts>-option-g-full/responses_g.jsonl \
  --pipeline g --questions runs/<ts>-option-g-full/questions.json \
  --out runs/<ts>-option-g-full/judged_g.json
```

---

## Files

| File | What |
|---|---|
| `build_corpus.py` | Creates 4 Jira projects (BUGS, CRM, OPS, PLAT) with realistic content |
| `generate_questions.py` | Generates questions grounded in real issue text via `deep_corpus()` |
| `jira_oracle.py` | Jira REST helpers (Basic auth) — used for ground-truth synthesis + existence checks |
| `runners/orchestrator.py` | Runs both pipelines in parallel with asyncio.Semaphore |
| `runners/run_option_a.py` | Calls Vertex AI Agent Engine via `:streamQuery` |
| `runners/run_option_b.py` | Calls GE streamAssist with MCP datastore routing (legacy — current run uses Claude sub-agents) |
| `judge.py` | Multi-dimensional judge — deterministic dims computed in code, analytical ones LLM-judged |
| `report.py` | Pure-CSS HTML side-by-side report with collapsible sections for all 500 questions |
| `sample-run/` | Latest committed run (Gemini 94.5%, Claude 87.1%) |

---

## Test corpus

5 Jira projects on `sockcop.atlassian.net`:

| Project | Issues | Type | Created |
|---|---|---|---|
| **SMP** | 910 | Motorcycle service tickets | Pre-existing |
| **BUGS** | 100 | Software bug triage | Built by eval |
| **CRM** | 100 | Customer support | Built by eval |
| **OPS** | 100 | SRE / infrastructure | Built by eval |
| **PLAT** | 100 | Platform engineering | Built by eval |

All eval-created issues tagged `eval-corpus` for cleanup. To delete the 4 test projects: `DELETE /rest/api/3/project/{BUGS,CRM,OPS,PLAT}`.

---

## Methodology

- **Grounded questions** — generator samples real issue descriptions (not invented generic ones) via `jira_oracle.deep_corpus()`. Themes come from actual issue text.
- **Hybrid oracle** — JQL-derivable Qs get programmatic ground truth (run JQL, capture exact `expected_keys`); analytical Qs get LLM-judged with `expected_themes`.
- **Deterministic scoring** — judge computes correctness/completeness/citation-accuracy/hallucination/pagination/refusal/efficiency in code; only analytical-correctness + JQL-correctness invoke the LLM. Cheaper, faster, reproducible.

---

## Cost estimate (500 questions × 2 pipelines)

- Vertex Gemini (Option A agent): covered by project TPM
- Atlassian REST (oracle): free
- Claude Opus judge: ~$10-15 (only on analytical Qs)
- Cloud Run MCP: pennies

Total per full run: ~$15.
