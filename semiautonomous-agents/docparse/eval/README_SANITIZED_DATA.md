# Sanitized Evaluation Data

This directory contains **sanitized** evaluation data for the docparse project. Customer-identifiable information has been redacted for public GitHub release.

## What's Redacted

### questions.json
- Original questions and answers replaced with `[REDACTED]` placeholders
- Metadata preserved: `id`, `pdf`, `page`, `element`, `category`, `difficulty`
- Structure intact: 216 questions spanning 2 PDFs, same distribution across categories

**Example:**
```json
{
  "id": 1,
  "pdf": "accenture",
  "page": 1,
  "element": "title",
  "category": "lookup",
  "difficulty": "easy",
  "q": "[REDACTED — sample lookup question about title on page 1]",
  "a": "[REDACTED]"
}
```

### judged/*.json
- Per-question data removed
- Only composite scores and verdict counts remain
- One file per strategy showing overall performance

**Example:**
```json
{
  "strategy": "rag_md_v2",
  "total_questions": 216,
  "composite_score": 92.9,
  "correctness_score": 92.9,
  "completeness_score": 93.0,
  "verdicts": {
    "correct": 196,
    "partial": 7,
    "refused": 3,
    "wrong": 10
  },
  "note": "Per-question data redacted for customer privacy."
}
```

### RESULTS.md
- Regenerated from sanitized data using `build_results_md_sanitized.py`
- Shows methodology, leaderboard, and scores
- No actual question text or answers
- No sample failures or showcase sections (those would leak Q&A content)

## Full Dataset Location

The **unredacted** evaluation data is backed up locally at:
```
~/docparse-eval-private/
├── questions.json          (full Q&A pairs)
├── judged/*.json          (per-question verdicts)
└── dashboard.html         (interactive viewer)
```

**DO NOT commit the private backup to any public repo.**

## Regenerating RESULTS.md

To regenerate the sanitized RESULTS.md:

```bash
cd eval/
python3 build_results_md_sanitized.py
```

## Why This Structure?

The public GitHub repo demonstrates:
1. **Evaluation methodology** — how we tested 8 strategies against 216 questions
2. **Scores and verdicts** — the 92.9% composite score and what strategies produced it
3. **Technical approach** — RAG Engine vs Discovery Engine, chunking strategies, etc.

Without revealing:
- Actual customer report content
- Company names or proprietary data
- Specific questions that could identify the source documents

Readers can understand the testing rigor and reproduce the methodology without access to the original PDFs.
