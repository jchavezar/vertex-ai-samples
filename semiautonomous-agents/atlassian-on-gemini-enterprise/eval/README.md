# Comparative Eval — Option A vs Option B

A reproducible benchmark over ~500 grounded Jira questions. Runs both pipelines in parallel against the same GE engine, scores each answer on 10 dimensions, produces a side-by-side HTML report.

## What "grounded" means

Questions are not invented from thin air. The generator queries the real `sockcop.atlassian.net` (or whichever site you point it at) via the Atlassian REST API, mines projects + issue keys + labels + assignees + sprints, and then asks Claude to write 480 read-only questions that are *answerable* from what's actually in the corpus. For each question, when the answer is JQL-derivable, the generator runs the JQL itself and stores `expected_keys` / `expected_count` as ground truth. Analytical questions (root-cause synthesis, trend analysis) get LLM-judged instead.

## Scoring (10 dimensions)

| Dim | Source | Notes |
|---|---|---|
| `correctness` | Set-equality of cited issue keys vs `expected_keys` (jql oracle) OR Claude Opus vs `expected_themes` (analytical) | F1 when set-derivable |
| `completeness` | Recall of expected keys (jql) or LLM judgment (analytical) | |
| `citation_accuracy` | Fraction of cited keys that EXIST in Jira | regex `[A-Z]+-\d+` from answer text → bulk JQL `key in (...)` |
| `hallucination_rate` | Fraction of cited keys NOT returned by any tool call | The metric for "plausible but fake" — the failure mode that matters for ticketing assistants |
| `jql_correctness` | Claude Opus equivalence judgment of generated JQL vs oracle JQL | Only for pipelines that emit `searchJiraIssuesUsingJql` calls |
| `pagination_completeness` | Coverage of `expected_keys` in answer for `pagination-required` questions | Tests whether the agent finished its pagination loop |
| `refusal_correctness` | Boolean: did refusal-test category get refused/clarified? | |
| `tool_efficiency` | `min_tool_calls / actual_tool_calls`, capped at 1 | Lower is worse — agent is wasting calls |
| `latency_s` | Wall-clock | |
| `n_tool_calls` | Count | Tracked for analysis |

Verdicts: `correct | partial | wrong | hallucinated | refused | error`. The `hallucinated` bucket exists because for ticketing agents, a confident answer with fake issue keys is worse than no answer.

## Quick reproduction (smoke)

```bash
cd ~/vertex-ai-samples/semiautonomous-agents/atlassian-on-gemini-enterprise/eval

# 0. Activate venv (created via `uv venv .venv` + `uv pip install -r requirements.txt`)
source .venv/bin/activate

# 1. Generate 5 questions in one category for a quick sanity check
python generate_questions.py --categories lookup --n 5 --out questions/_smoke.json

# 2. Run both pipelines on those 5 questions
python -m runners.orchestrator --questions questions/_smoke.json --out runs/_smoke

# 3. Judge both
python judge.py runs/_smoke/responses_a.jsonl --pipeline a --questions questions/_smoke.json --out runs/_smoke/judged_a.json
python judge.py runs/_smoke/responses_b.jsonl --pipeline b --questions questions/_smoke.json --out runs/_smoke/judged_b.json

# 4. Render the HTML report
python report.py --run runs/_smoke

# 5. Open it
xdg-open runs/_smoke/report.html
```

Acceptance: 5/5 `ok=True` for both pipelines; report renders; latency Option A in single-digit seconds, Option B in 2–6 s.

## Full run (~480 questions)

```bash
python generate_questions.py --n 480 --out questions/main.json
python -m runners.orchestrator --questions questions/main.json --out runs/$(date -u +%Y%m%d-%H%M)
# ... judge both pipelines ...
python report.py --run runs/<that timestamp>
```

Wall clock ~30–60 min depending on `EVAL_CONCURRENCY` (default 6 in-flight per pipeline). Resumable — re-running `orchestrator.py` skips IDs already present in the JSONLs.

## Configuration

Edit `eval/.env` (template in `.env.example`). Critical fields:

- `OPTION_A_AGENT_ID` — registered agent ID for the custom-MCP-portal Agent Engine.
- `OPTION_B_DATASTORE_ID` — Atlassian Rovo datastore ID created in Phase 2 (`option-b-direct-remote-mcp/register_datastore.py`).
- `ATLASSIAN_REFRESH_TOKEN` — written automatically by `option-a-custom-mcp-portal/utils/oauth_oneshot.py` once you re-run it; the oracle uses this to keep itself authenticated forever.
- `JUDGE_MODEL` — default `claude-opus-4-7@default` on Vertex region `us-east5`.
- `EVAL_CONCURRENCY`, `JUDGE_CONCURRENCY` — semaphore sizes per pipeline.

## Question categories

Documented in [`question_categories.md`](./question_categories.md) — 10 deliberately chosen buckets, each targeting a distinct failure mode. The split makes per-category bars in the report meaningful (e.g. "Option A wins on pagination-required, Option B wins on lookup").

## File layout

```
eval/
├── README.md                ← this file
├── question_categories.md
├── requirements.txt, .env.example, .gitignore
├── jira_oracle.py           ← Jira REST helpers (auto-refresh, auto-paginate)
├── generate_questions.py    ← uses Atlassian MCP / oracle to mine ~480 grounded questions
├── runners/
│   ├── _common.py           ← shared streamAssist call + parser
│   ├── run_option_a.py      ← agentsSpec routing
│   ├── run_option_b.py      ← dataStoreSpecs routing
│   └── orchestrator.py      ← parallel A+B; asyncio.Semaphore per pipeline
├── judge.py                 ← multi-dimensional judge
├── report.py                ← HTML side-by-side report
├── questions/
│   ├── main.json
│   └── writes.json          ← optional 20-question writes suite
└── runs/<UTC-ts>/
    ├── responses_a.jsonl, responses_b.jsonl
    ├── judged_a.json, judged_b.json
    ├── report.html, summary.json
    └── raw/<id>_{a,b}.json  ← per-question full streamAssist response
```

## Cost estimate

For ~480 questions × 2 pipelines:
- Vertex Gemini 3 flash (Option A's model) — covered by your project's TPM. The runner doesn't pay for it directly; the AE invokes it.
- Atlassian REST hits — well under any rate limit.
- Judge: Claude Opus 4.7 on Vertex, ~600 input + 200 output per analytical Q × ~50% of questions × 2 pipelines = ~480 judge calls × ~$0.03 each ≈ **$15**.
- Cloud Run MCP server (Option A) — pennies.

Smoke run is free (under all per-day quotas).

## Sanity checks before declaring done

- Both pipelines populated in the report.
- Composite delta is non-zero (if it's exactly 0 something is wrong — most likely both pipelines hit a quota and returned errors).
- ≥1 refusal-test gets verdict `refused` per pipeline (otherwise the safety check isn't probing).
- No question has `hallucination_rate > 0.5 AND correctness > 0.5` — if any do, the judge logic has a bug.

## Interpreting the headline scoreboard

Don't read it as "winner takes all." Each pipeline is optimized for a different shape of work:

- **Option A wins where you'd expect:** `pagination-required` (its agent has a `before_model_callback` that bounds prompt size — see [PAGINATION.md](../option-a-custom-mcp-portal/PAGINATION.md)), `multi-step` and `cross-issue-analysis` (custom logic in the instruction), and likely `tool_efficiency` (purpose-built tools).
- **Option B wins where you'd expect:** `lookup` and basic `jql-filter` (Atlassian's tool catalog is broader and more granular; no agent-runtime overhead) and probably median `latency` (no agent reasoning loop in the middle).
- **Both should perform similarly** on `root-cause-synthesis` (LLM reasoning quality dominates) and `trend` (date math is the bottleneck).

If you see Option B dominating on `pagination-required`, suspect a bug. If Option A dominates on `lookup`, suspect over-prompted instruction inflating latency.

## Why these dimensions and not GenAI Eval Service

This codebase doesn't use `vertexai.evaluation.EvalTask` — every existing eval (docparse, multimodal-doc-nexus, multi-agent-workbench) hand-rolls a Claude judge. Reasons:

1. Domain-specific dimensions (`hallucination_rate` for fake issue keys, `pagination_completeness` for the loop completeness, `jql_correctness` for query-equivalence) aren't in the stock metric catalog.
2. The judge model + prompts are pinned and version-controlled; rerunnable bit-for-bit.
3. Deterministic dimensions skip the LLM call entirely (cheaper, faster, and exactly reproducible).

If you'd rather use GenAI Eval Service, the per-question `judged_a.json` / `judged_b.json` shape is compatible with `pandas.DataFrame.from_records` for ingestion.
