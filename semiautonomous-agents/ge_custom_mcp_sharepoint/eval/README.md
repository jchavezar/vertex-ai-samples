## SharePoint × GE — comparative eval

Both options (Custom MCP and Hosted Work IQ MCP) are scored against the same deterministic SharePoint test site and the same question bank, then judged with the same rubric.

### Methodology (target shape — most files are skeletons today)

1. **Corpus** — `seed_corpus.py` populates a fresh SharePoint test site with a deterministic layout (sites, libraries, folders, files in several formats — txt, md, pdf, docx, xlsx, pptx, png). Re-running it always produces the same content.
2. **Questions** — `questions/questions.json` holds the bank in shape `{category, question, oracle}`. Target size: ~120 questions across 12 categories (~10 each). The current seed contains 2-3 examples per category.
3. **Runners** — one harness per option:
   - `runners/run_custom_mcp.py` against the deployed Cloud Run URL of option 1
   - `runners/run_hosted_iq.py` against Microsoft's hosted endpoint
   - Both submit identical questions through Gemini Enterprise chat (BYO_MCP path) and persist `{question, response, tool_calls, latency_ms}` per row.
4. **Judge** — `judge.py` (TODO: port `judge_v6` from `../../atlassian-jira-integration/eval/judge_v6.py`). Tiered T1/T2/T3 rubric on gemini-3-flash-preview with Haiku 4.5 escalation for low-confidence T1s.
5. **Comparison site** — `comparison-site/` (TODO) generates a static HTML side-by-side report from `runs/<ts>/*.json`.

### Run (target shape)

```bash
cd eval
pip install -r requirements.txt   # TODO: add file
python seed_corpus.py             # populates the SP test site
python runners/run_custom_mcp.py  # writes responses_custom.jsonl
python runners/run_hosted_iq.py   # writes responses_hosted.jsonl
python judge.py questions/questions.json responses_custom.jsonl responses_hosted.jsonl
```

### Where results land

- `runs/<ts>/responses_*.jsonl` — raw responses + tool traces
- `runs/<ts>/judged_*.json` — per-question verdicts
- `comparison-site/index.html` — interactive side-by-side (filter by category, verdict, "disagreements only")

### Question categories (12)

| # | Category | Tests |
|---|---|---|
| 1 | `lookup` | Direct point lookup of a known item |
| 2 | `search-by-name` | Find a file by partial name |
| 3 | `search-by-content` | Find a file by text inside it |
| 4 | `list-libraries` | Enumerate document libraries in a site |
| 5 | `list-items` | List files/folders in a known location |
| 6 | `metadata` | Surface modified date, size, author |
| 7 | `file-read` | Read & summarize a single file |
| 8 | `multi-file-synthesis` | Read N files and synthesize across them |
| 9 | `cross-library` | Pull info spread across multiple libraries |
| 10 | `permission-aware` | Don't surface files the user can't see |
| 11 | `refusal` | Refuse out-of-scope or unsafe requests |
| 12 | `prompt-injection` | Resist injection embedded in document content |

### Open TODOs

- `seed_corpus.py` — implement the deterministic SP test site builder.
- `questions/questions.json` — expand from ~30 seeded examples to ~120 (~10 per category).
- `judge.py` — port `judge_v6` from atlassian-jira-integration.
- `runners/*.py` — flesh out the chat harness against the GE app.
- `comparison-site/` — generate the side-by-side HTML.
- `requirements.txt` — pin runner + judge deps.
