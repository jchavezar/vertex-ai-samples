## comparison-site/

TODO: generate a static side-by-side HTML report from the runners +
judge output (same shape as `../../atlassian-jira-integration/eval/comparison-site/`).

Inputs:
- `../runs/<ts>/responses_custom_mcp.jsonl`
- `../runs/<ts>/responses_hosted_iq.jsonl`
- `../runs/<ts>/judged_*.json`

Output:
- `index.html` — filterable table: every question, both options' answers,
  judge verdict for each, "disagreements only" filter, per-category
  drill-down.

Suggested implementation:
- A small `build_site.py` script that reads the JSONLs and emits a
  single self-contained HTML file with vanilla JS for filtering.
- No backend; serve from `gsutil cp -r` to a public bucket if you
  want a shareable URL.
