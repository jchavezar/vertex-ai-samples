# Sample Run — 2026-05-08 (post-fixes)

A canonical execution of the eval harness over 478 grounded questions against
`sockcop.atlassian.net`, after applying four fixes to address eval-harness
artifacts and real agent issues uncovered by the first run (2026-05-07).

## What changed vs 2026-05-07

**Agent fixes (Option A):**
1. `MALFORMED_FUNCTION_CALL` recovery — `after_model_callback` catches
   Gemini 3 flash's malformed-tool-call edge cases and returns a fallback
   text instead of an empty answer.
2. Refusal guardrail — explicit "DESTRUCTIVE BULK OPERATIONS" block in the
   agent instruction tells it to refuse mass-reassign / mass-delete / drop
   project requests until the user confirms.

**Judge fixes (apply to both pipelines):**
3. **Pagination judge** — for questions with >30 expected keys, score by
   whether the count appears in the answer + whether cited keys are a valid
   subset, instead of demanding all 910 keys cited (which no agent can fit
   in a chat answer).
4. **Empty-set judge** — when `expected_count == 0`, accept any answer that
   acknowledges "no / none / 0 / not found", even if it cites helpful close
   matches. Previously the judge required `cited_keys == []` which gave
   "I can't access Jira" answers a free pass.

## View the report

https://htmlpreview.github.io/?https://github.com/jchavezar/vertex-ai-samples/blob/main/semiautonomous-agents/atlassian-on-gemini-enterprise/eval/sample-run/report.html

## Headline result

| | Option A — Custom MCP Portal | Δ vs prev | Option B — Direct Remote MCP | Δ vs prev |
|---|---|---|---|---|
| **Composite** | **78.4%** | +12.3pp | 41.7% | −3.8pp |
| Correctness | 78.9% | +13.2pp | 40.9% | −3.7pp |
| Completeness | 77.8% | +11.3pp | 42.4% | −3.8pp |
| Citation accuracy | 95.3% | flat | 81.8% | flat |
| Hallucination rate | **4.9%** | flat | 18.2% | flat |
| Latency p50 | 32.8 s | flat | 53.3 s | flat |
| Latency p95 | 330.2 s | flat | 121.4 s | flat |
| Verdicts | 300 correct, 60 partial, 72 wrong, 1 hallucinated, 38 refused, 7 error | — | 62 correct, 96 partial, 215 wrong, 1 hallucinated, 41 refused, 63 error | — |

Gap widened: A is 36.7pp ahead of B (was 20.7pp). The widening reflects the
fairer judge — Option B was previously getting credit for answers like
"I can't access Jira" when the expected answer was "no matching issues".

## Why Option B dropped slightly

The old empty-set judge had a bug: any pipeline that cited 0 keys against an
expected 0 keys got perfect score, regardless of what the answer text said.
Option B's frequent connector-error responses ("I'm currently unable to fetch
data") were thus scored as correct on empty-set questions. The new judge
requires the answer to actually acknowledge "no / none / 0 / not found"
before crediting it — Option B's connector-error pattern is now correctly
scored as wrong.

So the drop is the judge becoming more honest, not Option B getting worse.
The previous run is still available at sample-run-2026-05-07/ for comparison.

## What's in here

| File | Size | What it is |
|---|---|---|
| `report.html` | 1.1 MB | The side-by-side report |
| `summary.json` | 16 KB | Machine-readable scoreboard |
| `judged_a.json` / `judged_b.json` | ~1.1 MB | Per-question scores across all 10 dimensions |
| `responses_a.jsonl` / `responses_b.jsonl` | ~4 MB | Per-question answers + tool calls + citations + latency |
| `questions.json` | 1.8 MB | The 478 grounded questions with their oracles |

## Reproducing

```bash
cd ../   # back to eval/
source .venv/bin/activate
python generate_questions.py --n 48 --out questions/main.json
python -m runners.orchestrator --questions questions/main.json --out runs/<ts>
python judge.py runs/<ts>/responses_a.jsonl --pipeline a --questions questions/main.json --out runs/<ts>/judged_a.json
python judge.py runs/<ts>/responses_b.jsonl --pipeline b --questions questions/main.json --out runs/<ts>/judged_b.json
python report.py --run runs/<ts> --questions questions/main.json
```

## Caveats (still apply)

- Single Jira project (SMP) in the test corpus — cross-project questions and
  ambiguity-resolution questions are easier than they would be on a real
  multi-project instance.
- Zero issues created in the last 30 days — "this week" / "trend" questions
  return 0, which is awkward to evaluate.
- No labels, no sprints, no custom fields in the corpus.
- Refusal heuristic is keyword-based; uncommon phrasing of refusals may
  still get marked wrong.
- Option A goes through `:streamQuery` (direct Agent Engine invocation)
  rather than `streamAssist`, because GE's per-user OAuth gates programmatic
  agent calls. The agent code, model, tools are identical to production GE
  chats — only the OAuth layer differs.
