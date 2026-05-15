# GA Models vs Preview Models: Docparse Benchmark Results

**Date:** 2026-04-30  
**Test:** Can Gemini 2.5-flash (GA) match Gemini 3-flash-preview performance?

## Executive Summary

**Answer: NO** — The customer cannot use GA models and still hit 90% composite.

- **Preview model (gemini-3-flash-preview):** 92.9% composite
- **GA model (gemini-2.5-flash):** 87.7% composite
- **Delta:** -5.2 percentage points

## Detailed Scores

### Baseline: Gemini 3 Flash Preview (rag_md_v2)

| Metric | Score |
|--------|-------|
| Composite | 92.9% |
| Correctness | 92.9% |
| Completeness | 93.0% |
| Correct answers | 196 / 216 |
| Partial answers | 7 / 216 |
| Wrong answers | 10 / 216 |
| Refused | 3 / 216 |

### GA Model: Gemini 2.5 Flash (agent_ga_flash)

| Metric | Score |
|--------|-------|
| Composite | 87.7% |
| Correctness | 89.0% |
| Completeness | 86.4% |
| Correct answers | 182 / 216 |
| Partial answers | 14 / 216 |
| Wrong answers | 5 / 216 |
| Refused | 15 / 216 |

### Delta (GA - Preview)

| Metric | Delta |
|--------|-------|
| Composite | -5.2% |
| Correctness | -3.9% |
| Completeness | -6.6% |
| Correct answers | -14 |

## Key Differences

### Model Capabilities

- **Thinking mode:** Preview model uses `thinking_level=HIGH` (extended reasoning). GA 2.5-flash does not support `thinking_config`.
- **Model family:** Preview uses Gemini 3.x experimental features. GA uses Gemini 2.5 stable API.

### Performance Characteristics

- **Refusals:** GA model refused 15 questions vs 3 for preview (12 more refusals)
- **Wrong answers:** GA model had fewer wrong answers (5 vs 10)
- **Partial answers:** GA model had more partial answers (14 vs 7)

The GA model is more conservative (more refusals) but when it does answer, it's slightly more accurate (fewer wrongs), though less complete.

## Methodology

- **Dataset:** 216 questions across 5 categories (lookup, comparison, inference, math, visual)
- **Corpus:** Same RAG Engine corpus for both tests
  - `projects/254356041555/locations/us-central1/ragCorpora/8818611020344852480`
  - Per-page chunks from docparse-extracted markdown
  - text-embedding-005 embeddings
- **Retrieval:** top_k=20, vector_distance_threshold=0.5
- **Judge:** Claude Opus 4.5 on Vertex AI (us-east5)
- **Location:** Both models called via `global` region endpoint

## Files

- Raw results: `eval/runs/agent_ga_flash.json`
- Judged results: `eval/judged/agent_ga_flash.json`
- Baseline (preview): `eval/judged/rag_md_v2.json`
- HTML report: `eval/ga_comparison.html`

## Recommendation

The 5.2 percentage point drop from 92.9% to 87.7% is significant. The customer should:

1. **Stick with preview models** if 90%+ accuracy is required
2. **Consider Gemini 2.5-pro** (GA) as an alternative — may perform better than 2.5-flash
3. **Wait for Gemini 3.x GA release** if production stability is required with 90%+ accuracy

The lack of thinking mode support in GA 2.5-flash appears to be a major factor in the performance gap.
