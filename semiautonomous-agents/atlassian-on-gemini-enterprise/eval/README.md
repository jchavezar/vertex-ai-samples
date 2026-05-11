# Comparative Eval Harness

Reproducible benchmark of Jira-AI assistants. 500 grounded questions across 20 categories on a multi-project Jira corpus (~1,310 issues), scored on 10 dimensions by Claude Opus.

Latest result: see [`sample-run/`](./sample-run/).

## What gets measured

| Dimension | Source | Notes |
|---|---|---|
| `correctness` | Set-equality of cited keys vs `expected_keys` (deterministic) OR Claude Opus vs `expected_themes` (analytical) | F1 when set-derivable |
| `completeness` | Recall against expected | |
| `citation_accuracy` | Fraction of cited issue keys that EXIST in Jira | Bulk JQL `key in (...)` |
| `hallucination_rate` | Cited keys NOT returned by any tool call | The metric that matters most for Jira agents |
| `jql_correctness` | Claude Opus equivalence of generated JQL vs oracle JQL | When the agent emits a JQL tool call |
| `pagination_completeness` | Coverage of `expected_keys` in answer | For `pagination-required` |
| `refusal_correctness` | Did refusal-test category get refused/clarified? | Boolean |
| `tool_efficiency` | `min_tool_calls / actual_tool_calls`, capped at 1 | |
| `latency_s` | Wall-clock | |
| `n_tool_calls` | Count | |

Verdicts: `correct | partial | wrong | hallucinated | refused | error`. The `hallucinated` bucket exists because for ticketing agents, a confident answer with fake issue keys is worse than no answer (broken URLs).

## Question categories

20 categories deliberately picked to cover production-readiness — see [`question_categories.md`](./question_categories.md) for the full taxonomy. Headline groups:

- **Read-side correctness** — `lookup`, `jql-filter`, `count-aggregate`, `pagination-required`, `multi-step`, `cross-issue-analysis`, `root-cause-synthesis`, `trend`, `ambiguous`, `multi-step`
- **Production patterns** — `multi-project`, `epic-tree`, `issue-links`, `components-versions`, `comments-worklogs`
- **Safety / robustness** — `refusal-test`, `prompt-injection`, `pii-sensitive`, `typo-robustness`, `tool-efficiency`, `golden-anti-regression`

## File layout

```
eval/
├── README.md                this file
├── question_categories.md
├── requirements.txt, .env.example, .gitignore
├── jira_oracle.py           Jira REST helpers (Basic auth + API token)
├── build_corpus.py          create test projects + populate them
├── generate_questions.py    LLM-generates questions grounded in real issue text
├── runners/
│   ├── run_option_a.py      :streamQuery to Vertex AI Agent Engine
│   ├── run_option_b.py      streamAssist via GE datastore (legacy)
│   └── orchestrator.py      parallel A+B; asyncio.Semaphore(6) per pipeline
├── judge.py                 multi-dim Claude Opus judge (auto-skips deterministic dims)
├── report.py                pure-CSS HTML side-by-side, no JS
└── sample-run/              the latest committed run (open report.html)
```

## Quick reproduction

```bash
source .venv/bin/activate

# (one-time) populate the test corpus
python build_corpus.py

# generate questions grounded in real Jira data
python generate_questions.py --n 25 --out questions/main.json

# run both pipelines (parallel, asyncio.Semaphore(6) per pipeline)
python -m runners.orchestrator --questions questions/main.json --out runs/<ts>

# judge both
python judge.py runs/<ts>/responses_a.jsonl --pipeline a --questions runs/<ts>/questions.json --out runs/<ts>/judged_a.json
python judge.py runs/<ts>/responses_b.jsonl --pipeline b --questions runs/<ts>/questions.json --out runs/<ts>/judged_b.json

# render report (REPORT_SHORT_A/B labels are env-overridable)
python report.py --run runs/<ts> --questions runs/<ts>/questions.json
xdg-open runs/<ts>/report.html
```

Smoke takes ~3 min for 5 questions; full 500 takes ~30-90 min for orchestrator + ~5 min for judge depending on concurrency.

## Configuration

Edit `eval/.env` (template in `.env.example`):

- `OPTION_A_AGENT_ID` — registered agent ID for the custom-MCP-portal Agent Engine.
- `OPTION_B_DATASTORE_ID` — Atlassian Rovo datastore ID created in Phase 2 of `option-b-direct-remote-mcp/`.
- `ATLASSIAN_EMAIL` + `ATLASSIAN_API_TOKEN` — for `jira_oracle.py` (oracle / question generation / citation existence checks). Get an API token at https://id.atlassian.com/manage-profile/security/api-tokens.
- `JUDGE_MODEL`, `JUDGE_REGION`, `JUDGE_PROJECT` — defaults to `claude-opus-4-5@20251101` on `us-east5` in `vtxdemos`.
- `EVAL_CONCURRENCY`, `JUDGE_CONCURRENCY` — semaphore sizes per pipeline (defaults: 6 / 4).

## Methodology notes

- **Grounded questions** — generator passes real issue descriptions (sampled per status/priority/type bucket via `deep_corpus()`) to Claude so themes match real corpus content, not pre-imagined generic ones.
- **Hybrid oracle** — JQL-derivable questions get programmatic ground truth (run JQL, store `expected_keys` + `expected_count`); analytical ones get LLM-judged with `expected_themes`.
- **Deterministic dims skip the LLM** — judge only invokes Claude for analytical-correctness and JQL-equivalence; everything else is computed in code (cheaper, faster, exactly reproducible).
- **No Vertex GenAI Eval Service** — every existing eval in this codebase (docparse, multimodal-doc-nexus, multi-agent-workbench) hand-rolls a Claude judge for the same reasons (domain-specific dimensions, pinned prompts, reproducibility).

## Cost estimate

For ~500 questions × 2 pipelines:
- Vertex Gemini (Option A's model) — covered by your project's TPM, no direct charge.
- Atlassian REST hits (oracle + ground truth) — well under any rate limit, free.
- Judge: Claude Opus 4.5 on Vertex × ~50% analytical questions × 2 pipelines ≈ ~$10-15.
- Cloud Run MCP server (Option A) — pennies.
