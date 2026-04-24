"""Runtime predicates that catch chart-extraction errors before they hit
markdown. All validators take a ChartData and return a list of failure
messages (empty list = passed). They are pure Python, no LLM calls."""
from __future__ import annotations

import re
from collections.abc import Callable

from .schemas import ChartData, ChartType


PLACEHOLDER_NAME_RE = re.compile(
    r"^(series|group|category|column|col|set|bar|line|var)\s*\d*$",
    re.IGNORECASE,
)
NO_LEGEND_SENTINEL = "(legend not visible)"


def no_placeholder_series_names(c: ChartData) -> list[str]:
    fails: list[str] = []
    for s in c.series:
        name = (s.name or "").strip()
        if not name:
            fails.append("series with empty name")
            continue
        if PLACEHOLDER_NAME_RE.match(name):
            fails.append(
                f"series name {name!r} looks like a placeholder; the legend was likely "
                f"missed or unreadable. Re-read the chart's legend / color key and use "
                f"the literal text shown there."
            )
    return fails


def consistent_value_lengths(c: ChartData) -> list[str]:
    n = len(c.x_categories)
    fails: list[str] = []
    if n == 0 and c.series:
        fails.append("x_categories is empty but series have values")
    for s in c.series:
        if len(s.values) != n and n > 0:
            fails.append(
                f"series {s.name!r} has {len(s.values)} values but x_categories has {n}"
            )
    return fails


def stacks_sum_close_to_100(c: ChartData, tol: float = 2.0) -> list[str]:
    """For stacked/donut/pie charts in % units, each stack should sum near 100."""
    if c.value_unit not in {"%", "percent", "percentage"}:
        return []
    if c.chart_type not in {ChartType.STACKED_BAR, ChartType.PIE, ChartType.DONUT}:
        return []
    fails: list[str] = []
    if c.chart_type in {ChartType.PIE, ChartType.DONUT}:
        total = sum((s.values[0] or 0) for s in c.series if s.values)
        if abs(total - 100) > tol:
            fails.append(f"{c.chart_type.value} segments sum to {total} (expected ~100)")
        return fails
    # stacked bar: each x-category's stack should sum near 100
    for i, cat in enumerate(c.x_categories):
        stack = sum((s.values[i] if i < len(s.values) and s.values[i] is not None else 0) for s in c.series)
        if abs(stack - 100) > tol:
            fails.append(
                f"stacked bar at x={cat!r} sums to {stack} (expected ~100). "
                f"Re-check the segment values for this bar."
            )
    return fails


def values_within_axis_range(c: ChartData) -> list[str]:
    """If unit is % values must be 0-100; nothing should be wildly negative
    unless explicitly noted."""
    if c.value_unit not in {"%", "percent", "percentage"}:
        return []
    fails: list[str] = []
    for s in c.series:
        for i, v in enumerate(s.values):
            if v is None:
                continue
            if v < -5 or v > 105:
                fails.append(
                    f"series {s.name!r} value at index {i} = {v} is outside 0-100 (% scale)"
                )
    return fails


def time_axis_is_sorted(c: ChartData) -> list[str]:
    """If x looks like time labels, they should be in chronological order
    (this catches the model returning categories in legend order instead of
    time order)."""
    yr_re = re.compile(r"^(?:CY\s*|FY\s*)?(\d{4})(?:Q[1-4])?$|^(20\d{2})Q[1-4]$|^Q[1-4]\s*20\d{2}$", re.IGNORECASE)
    keys = []
    for cat in c.x_categories:
        m = yr_re.search(cat)
        if not m:
            return []  # not a time axis we recognise
        keys.append(cat)
    if keys != sorted(keys):
        return [f"time-like x_categories are not in sorted order: {c.x_categories}"]
    return []


def has_some_data(c: ChartData) -> list[str]:
    if not c.series:
        return ["no series extracted"]
    if not c.x_categories:
        return ["no x_categories extracted"]
    non_null = sum(1 for s in c.series for v in s.values if v is not None)
    if non_null == 0:
        return ["all extracted values are null — chart was likely unreadable"]
    return []


VALIDATORS: list[Callable[[ChartData], list[str]]] = [
    has_some_data,
    no_placeholder_series_names,
    consistent_value_lengths,
    stacks_sum_close_to_100,
    values_within_axis_range,
    time_axis_is_sorted,
]


def validate(c: ChartData) -> list[str]:
    """Run all validators; return the concatenated list of failures."""
    out: list[str] = []
    for v in VALIDATORS:
        out.extend(v(c))
    return out
