# `_archive/` — preserved but off the production path

These files are committed to git but are NOT used by the running pipeline.
They exist so the research history isn't lost.

## `advanced_dev_iterations/`

Experimental "premium precision" techniques that were prototyped but never
shipped to production:

- `setofmark.py` — Set-of-Mark prompting (arXiv 2310.11441) for chart extraction
- `multivote.py` — run chart value extraction 3× and vote on each cell
- `judge.py` — render extracted ChartData back to Vega-Lite, rasterize, ask LLM if it matches the original
- `pipeline_premium.py` — wires the above three together as an opt-in path

To re-enable, copy the folder back to `extractor/src/docparse/advanced/` and
import `parse_pdf_premium` from `pipeline.py`. Production has not measured a
quality lift from these vs. the standard pipeline that justifies the extra
cost — re-test before shipping.

## `storm_test.py`

Standalone script that fires 100 simultaneous duplicate enqueue calls at
the Cloud Tasks queue to verify named-task dedup. Used by
`extractor/PRODUCTION_READINESS.md` for the verification reproduction step.

Run with:

```bash
cd extractor
PROJECT=your-project uv run python ../_archive/storm_test.py
# expect: created=1, suppressed=99, errors=0
```
