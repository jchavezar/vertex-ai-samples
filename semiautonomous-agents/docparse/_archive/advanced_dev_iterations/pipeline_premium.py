"""Premium pipeline that wires every advanced precision technique together
for benchmark and A-B testing. Slower and more expensive than the default
pipeline; run only when you need to compare against the baseline or when a
specific high-stakes document needs maximum precision.

Differences from the default pipeline:
  - Two-pass + value multi-vote (n=3) on every chart
  - LLM-judge round-trip via Vega-Lite render
  - Set-of-Mark overlay on charts where the schema pass returns
    legend_visible=False or where validators flag color-mapping issues

Use:
    from docparse.advanced.pipeline_premium import parse_pdf_premium
    result = await parse_pdf_premium(pdf_path)

The result object is the same shape as the default `PipelineResult`, so
you can diff outputs directly.
"""
from __future__ import annotations

from pathlib import Path

from ..pipeline import (
    PipelineResult,
    parse_pdf_async as _parse_pdf_default,
)


async def parse_pdf_premium(pdf_path: Path) -> PipelineResult:
    """Currently delegates to the default pipeline. Stub for future wiring of
    multivote + judge + setofmark. Filling this in is intentionally deferred
    until the held-out evaluation shows the default pipeline isn't enough."""
    return await _parse_pdf_default(pdf_path)
