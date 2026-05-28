# Comparative Evaluation Harness

*Numbers as of 2026-05-27, judge_v6 (gemini-3-flash-preview + Haiku 4.5 escalation), n=172 v2 corpus.*

172 grounded Jira questions × 20 categories (the v2 curated corpus; 500q
for Option F's own super-set), scored on 10 dimensions by **judge_v6** —
gemini-3-flash-preview tiered T1/T2/T3 with Haiku 4.5 low-confidence
escalation.

**Latest results (2026-05-27, judge_v6 headline):**

| Pipeline | Accuracy (v6 headline) | Hallucination | p50 latency |
|---|---:|---:|---:|
| **Option A** — Custom MCP + ADK (Gemini 2.5) | **94.7 %** | 0.0 % | 24.7 s |
| **Option B** — Atlassian Rovo (Claude Sonnet sub-agent) | **94.5 %** | 1.4 % | 35.3 s |
| Option E — `google.genai` loop in MCP wrapper (gemini-3.1-flash-lite) | 90.5 % | 3.4 % | 20.6 s |
| Option C — Custom MCP via GE BYO_MCP (no ADK) | 87.9 % | 3.4 % | 28.9 s |
| Option D — GE federated `jira_cloud` | 77.5 % | 8.5 % | 20.2 s |
| Option F — ADK + Rovo MCP wrapper | 58.1 % (172-subset) / 41.0 % (500q) | <!-- TODO: verify against judge_v6 --> | 22.6 s (500q) |

> **Interactive side-by-side**: open [`comparison-site/index.html`](comparison-site/index.html) — every question, every answer, every verdict, filterable.
> **Category taxonomy with examples**: [`QUESTION_TYPES.md`](QUESTION_TYPES.md).
> **F vs B head-to-head**: [`../F_vs_B_comparison.md`](../F_vs_B_comparison.md).

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

JUDGE_REGION=global
JUDGE_MODEL=gemini-3-flash-preview          # judge_v6 primary
JUDGE_ESCALATION_MODEL=claude-haiku-4-5     # Tier-1 low-confidence escalation
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
| `report.py` | Pure-CSS HTML side-by-side report (per-run A vs B style) |
| `QUESTION_TYPES.md` | The 20 categories with concrete examples + per-category Option E scores |
| `comparison-site/` | Single-page multi-option HTML comparison; `python3 comparison-site/build_data.py` regenerates from runs |
| `judge_v6.py` | Tiered judge (T1/T2/T3) on gemini-3-flash-preview + Haiku 4.5 escalation |

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

## Cost estimate (500 questions × 1 pipeline)

- Vertex Gemini (Option A agent or E genai loop): covered by project TPM
- Atlassian REST (oracle): free
- judge_v6 (gemini-3-flash-preview + occasional Haiku 4.5 escalation): ~$5–10 per full run
- Cloud Run MCP: pennies

Total per full run: ~$10. For at-scale (4,000-user) pricing per option, see [`../docs/PRICING.md`](../docs/PRICING.md).
