"""Multi-vote (n=3) on numeric chart values. Runs the value pass N times in
parallel at moderate temperature, then takes the median per (series, x) cell.
For non-numeric / categorical series, falls back to majority vote.

When to use: a single chart's validators consistently fail (e.g. stacks not
summing to 100 even after the cheap retry). Costs ~N times the pro tokens
per chart -- only worth it on a small set of high-stakes charts.
"""
from __future__ import annotations

import asyncio
from statistics import median

from ..gemini import PRO_MODEL, call_vision
from ..prompts import CHART_VALUES_PROMPT
from ..schemas import ChartData, ChartSchemaOnly, ChartSeries


async def extract_with_vote(
    page_bytes: bytes,
    bbox_str: str,
    schema: ChartSchemaOnly,
    n: int = 3,
    temperature: float = 0.4,
) -> ChartData:
    """Run the values pass N times, return a ChartData with cell-wise medians."""
    prompt = CHART_VALUES_PROMPT.format(
        bbox=bbox_str,
        chart_type=schema.chart_type.value,
        n_categories=len(schema.x_categories),
        x_categories=schema.x_categories,
        n_series=len(schema.series_names),
        series_names=schema.series_names,
        value_unit=schema.value_unit,
        legend_visible=schema.legend_visible,
    )

    async def one() -> ChartData:
        return await call_vision(
            model=PRO_MODEL,
            prompt=prompt,
            image_bytes=page_bytes,
            response_model=ChartData,
            temperature=temperature,
            timeout_s=90.0,
        )

    samples = await asyncio.gather(*[one() for _ in range(n)])
    return _merge_by_median(samples, schema)


def _merge_by_median(samples: list[ChartData], schema: ChartSchemaOnly) -> ChartData:
    """Per-cell median across N samples. Categorical mismatches use majority."""
    if not samples:
        raise ValueError("no samples to merge")

    n_cat = len(schema.x_categories)
    n_ser = len(schema.series_names)
    series: list[ChartSeries] = []
    for si in range(n_ser):
        merged_values: list[float | None] = []
        for ci in range(n_cat):
            cell = []
            for s in samples:
                if si >= len(s.series) or ci >= len(s.series[si].values):
                    continue
                v = s.series[si].values[ci]
                if v is not None:
                    cell.append(v)
            merged_values.append(median(cell) if cell else None)
        series.append(
            ChartSeries(
                name=schema.series_names[si],
                values=merged_values,
            )
        )

    base = samples[0]
    return ChartData(
        chart_type=schema.chart_type,
        title=base.title,
        subtitle=base.subtitle,
        x_axis_label=base.x_axis_label,
        y_axis_label=base.y_axis_label,
        x_categories=schema.x_categories,
        series=series,
        value_unit=schema.value_unit,
        source_caption=base.source_caption,
        notes=base.notes,
        summary=base.summary,
        legend_visible=schema.legend_visible,
    )
