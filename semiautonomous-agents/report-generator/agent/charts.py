"""Pure-Python inline-SVG chart generator for the report renderer.

No matplotlib dependency — we build SVG strings directly. Output is
embedded straight into the WeasyPrint HTML, so it scales cleanly in PDFs.

Supported chart `kind` values: bar, line, pie. Spec shape:
    {"kind": "bar", "title": "...", "x_label": "...", "y_label": "...",
     "series": [{"name": "Pinecone", "data": [{"x": "Q1", "y": 12}, ...]}]}
"""
from __future__ import annotations

from html import escape
from typing import Any, Iterable

# Brand-aligned palette (matches report.css accent + tier colors).
PALETTE = [
    "#1d4ed8",  # accent blue
    "#16a34a",  # primary green
    "#a16207",  # secondary amber
    "#dc2626",  # red
    "#7c3aed",  # purple
    "#0891b2",  # teal
]


def _fnum(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _fmt_axis(v: float) -> str:
    av = abs(v)
    if av >= 1_000_000_000:
        return f"{v / 1_000_000_000:.1f}B"
    if av >= 1_000_000:
        return f"{v / 1_000_000:.1f}M"
    if av >= 1_000:
        return f"{v / 1_000:.1f}k"
    if av >= 10:
        return f"{v:.0f}"
    return f"{v:.1f}"


def _series(spec: dict[str, Any]) -> list[dict[str, Any]]:
    raw = spec.get("series") or []
    out: list[dict[str, Any]] = []
    for s in raw:
        if not isinstance(s, dict):
            continue
        data = s.get("data") or []
        if not isinstance(data, list):
            continue
        out.append({"name": str(s.get("name", "")), "data": data})
    return out


def _all_x(series: Iterable[dict[str, Any]]) -> list[str]:
    seen: list[str] = []
    for s in series:
        for pt in s["data"]:
            if not isinstance(pt, dict):
                continue
            x = str(pt.get("x", ""))
            if x and x not in seen:
                seen.append(x)
    return seen


def _max_y(series: Iterable[dict[str, Any]]) -> float:
    m = 0.0
    for s in series:
        for pt in s["data"]:
            if isinstance(pt, dict):
                m = max(m, _fnum(pt.get("y")))
    return m or 1.0


def _legend(series: list[dict[str, Any]], width: int, y: float) -> str:
    if len(series) <= 1 and not (series and series[0]["name"]):
        return ""
    parts: list[str] = []
    x_cursor = 12
    for i, s in enumerate(series):
        name = s["name"] or f"Series {i + 1}"
        color = PALETTE[i % len(PALETTE)]
        parts.append(
            f'<rect x="{x_cursor}" y="{y - 9}" width="10" height="10" rx="2" fill="{color}"/>'
            f'<text x="{x_cursor + 14}" y="{y}" class="chart-legend">{escape(name)}</text>'
        )
        x_cursor += 18 + max(len(name) * 6, 40)
        if x_cursor > width - 80:
            break
    return "".join(parts)


def _bar(spec: dict[str, Any]) -> str:
    series = _series(spec)
    if not series:
        return ""
    width, height = 600, 320
    pad_l, pad_r = 56, 16
    pad_t = 38 if spec.get("title") else 16
    pad_b = 64
    inner_w = width - pad_l - pad_r
    inner_h = height - pad_t - pad_b

    cats = _all_x(series)
    if not cats:
        return ""
    max_y = _max_y(series)

    n_groups = len(cats)
    n_series = len(series)
    group_w = inner_w / n_groups
    bar_w = (group_w * 0.72) / n_series

    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'class="chart chart-bar" role="img" aria-label="{escape(spec.get("title", "bar chart"))}">'
    )

    if spec.get("title"):
        parts.append(
            f'<text x="{width / 2}" y="22" text-anchor="middle" class="chart-title">'
            f'{escape(spec["title"])}</text>'
        )

    # gridlines + y ticks
    for i in range(5):
        y_val = (max_y / 4) * i
        y_pos = (height - pad_b) - (inner_h * i / 4)
        parts.append(
            f'<line x1="{pad_l}" y1="{y_pos}" x2="{width - pad_r}" y2="{y_pos}" '
            f'stroke="#e5e7eb" stroke-width="0.5"/>'
        )
        parts.append(
            f'<text x="{pad_l - 6}" y="{y_pos + 3}" text-anchor="end" class="chart-tick">'
            f'{_fmt_axis(y_val)}</text>'
        )

    # axes
    parts.append(
        f'<line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{height - pad_b}" '
        f'stroke="#94a3b8" stroke-width="1"/>'
    )
    parts.append(
        f'<line x1="{pad_l}" y1="{height - pad_b}" x2="{width - pad_r}" y2="{height - pad_b}" '
        f'stroke="#94a3b8" stroke-width="1"/>'
    )

    # bars
    for gi, x in enumerate(cats):
        gx = pad_l + gi * group_w + (group_w - bar_w * n_series) / 2
        for si, s in enumerate(series):
            y_val = 0.0
            for pt in s["data"]:
                if isinstance(pt, dict) and str(pt.get("x", "")) == x:
                    y_val = _fnum(pt.get("y"))
                    break
            bar_h = inner_h * (y_val / max_y) if max_y > 0 else 0
            bx = gx + si * bar_w
            by = (height - pad_b) - bar_h
            color = PALETTE[si % len(PALETTE)]
            parts.append(
                f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_w * 0.85:.1f}" '
                f'height="{bar_h:.1f}" fill="{color}" rx="2"/>'
            )
        cx = pad_l + gi * group_w + group_w / 2
        parts.append(
            f'<text x="{cx:.1f}" y="{height - pad_b + 16}" text-anchor="middle" '
            f'class="chart-tick">{escape(x)}</text>'
        )

    if spec.get("y_label"):
        parts.append(
            f'<text x="14" y="{pad_t + inner_h / 2}" text-anchor="middle" '
            f'transform="rotate(-90 14 {pad_t + inner_h / 2})" '
            f'class="chart-axis-label">{escape(spec["y_label"])}</text>'
        )
    if spec.get("x_label"):
        parts.append(
            f'<text x="{width / 2}" y="{height - 28}" text-anchor="middle" '
            f'class="chart-axis-label">{escape(spec["x_label"])}</text>'
        )

    parts.append(_legend(series, width, height - 6))
    parts.append("</svg>")
    return "".join(parts)


def _line(spec: dict[str, Any]) -> str:
    series = _series(spec)
    if not series:
        return ""
    width, height = 600, 320
    pad_l, pad_r = 56, 16
    pad_t = 38 if spec.get("title") else 16
    pad_b = 64
    inner_w = width - pad_l - pad_r
    inner_h = height - pad_t - pad_b

    cats = _all_x(series)
    if not cats:
        return ""
    max_y = _max_y(series)
    n_pts = len(cats)
    step = inner_w / max(n_pts - 1, 1)

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'class="chart chart-line" role="img" aria-label="{escape(spec.get("title", "line chart"))}">'
    ]

    if spec.get("title"):
        parts.append(
            f'<text x="{width / 2}" y="22" text-anchor="middle" class="chart-title">'
            f'{escape(spec["title"])}</text>'
        )

    for i in range(5):
        y_val = (max_y / 4) * i
        y_pos = (height - pad_b) - (inner_h * i / 4)
        parts.append(
            f'<line x1="{pad_l}" y1="{y_pos}" x2="{width - pad_r}" y2="{y_pos}" '
            f'stroke="#e5e7eb" stroke-width="0.5"/>'
        )
        parts.append(
            f'<text x="{pad_l - 6}" y="{y_pos + 3}" text-anchor="end" class="chart-tick">'
            f'{_fmt_axis(y_val)}</text>'
        )

    parts.append(
        f'<line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{height - pad_b}" '
        f'stroke="#94a3b8"/>'
    )
    parts.append(
        f'<line x1="{pad_l}" y1="{height - pad_b}" x2="{width - pad_r}" y2="{height - pad_b}" '
        f'stroke="#94a3b8"/>'
    )

    for si, s in enumerate(series):
        color = PALETTE[si % len(PALETTE)]
        pts: list[tuple[float, float]] = []
        for i, x in enumerate(cats):
            y_val = None
            for pt in s["data"]:
                if isinstance(pt, dict) and str(pt.get("x", "")) == x:
                    y_val = _fnum(pt.get("y"))
                    break
            if y_val is None:
                continue
            px = pad_l + i * step
            py = (height - pad_b) - inner_h * (y_val / max_y if max_y else 0)
            pts.append((px, py))
        if not pts:
            continue
        path_d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        parts.append(
            f'<path d="{path_d}" fill="none" stroke="{color}" stroke-width="2.4" '
            f'stroke-linecap="round" stroke-linejoin="round"/>'
        )
        for x, y in pts:
            parts.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="white" '
                f'stroke="{color}" stroke-width="2"/>'
            )

    for i, x in enumerate(cats):
        cx = pad_l + i * step
        parts.append(
            f'<text x="{cx:.1f}" y="{height - pad_b + 16}" text-anchor="middle" '
            f'class="chart-tick">{escape(x)}</text>'
        )

    if spec.get("y_label"):
        parts.append(
            f'<text x="14" y="{pad_t + inner_h / 2}" text-anchor="middle" '
            f'transform="rotate(-90 14 {pad_t + inner_h / 2})" '
            f'class="chart-axis-label">{escape(spec["y_label"])}</text>'
        )
    if spec.get("x_label"):
        parts.append(
            f'<text x="{width / 2}" y="{height - 28}" text-anchor="middle" '
            f'class="chart-axis-label">{escape(spec["x_label"])}</text>'
        )

    parts.append(_legend(series, width, height - 6))
    parts.append("</svg>")
    return "".join(parts)


def _pie(spec: dict[str, Any]) -> str:
    """Pie / donut. Reads first series only — pies don't multi-series."""
    series = _series(spec)
    if not series:
        return ""
    data = series[0]["data"]
    slices: list[tuple[str, float]] = []
    for pt in data:
        if isinstance(pt, dict):
            label = str(pt.get("x", ""))
            value = _fnum(pt.get("y"))
            if value > 0:
                slices.append((label, value))
    if not slices:
        return ""
    total = sum(v for _, v in slices) or 1.0

    width, height = 560, 320
    cx, cy = 160, 160
    r_outer, r_inner = 120, 60

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'class="chart chart-pie" role="img" aria-label="{escape(spec.get("title", "pie chart"))}">'
    ]
    if spec.get("title"):
        parts.append(
            f'<text x="{width / 2}" y="22" text-anchor="middle" class="chart-title">'
            f'{escape(spec["title"])}</text>'
        )

    import math

    angle = -math.pi / 2  # start at 12 o'clock
    for i, (label, value) in enumerate(slices):
        portion = value / total
        sweep = portion * 2 * math.pi
        a1, a2 = angle, angle + sweep
        large = 1 if sweep > math.pi else 0
        x1o, y1o = cx + r_outer * math.cos(a1), cy + r_outer * math.sin(a1)
        x2o, y2o = cx + r_outer * math.cos(a2), cy + r_outer * math.sin(a2)
        x1i, y1i = cx + r_inner * math.cos(a1), cy + r_inner * math.sin(a1)
        x2i, y2i = cx + r_inner * math.cos(a2), cy + r_inner * math.sin(a2)
        d = (
            f"M {x1o:.1f} {y1o:.1f} "
            f"A {r_outer} {r_outer} 0 {large} 1 {x2o:.1f} {y2o:.1f} "
            f"L {x2i:.1f} {y2i:.1f} "
            f"A {r_inner} {r_inner} 0 {large} 0 {x1i:.1f} {y1i:.1f} Z"
        )
        color = PALETTE[i % len(PALETTE)]
        parts.append(f'<path d="{d}" fill="{color}"/>')
        angle = a2

    legend_x = cx + r_outer + 36
    for i, (label, value) in enumerate(slices):
        ly = 60 + i * 22
        if ly > height - 20:
            break
        color = PALETTE[i % len(PALETTE)]
        pct = (value / total) * 100
        parts.append(
            f'<rect x="{legend_x}" y="{ly - 9}" width="12" height="12" rx="2" fill="{color}"/>'
            f'<text x="{legend_x + 18}" y="{ly}" class="chart-legend">'
            f'{escape(label)} <tspan class="chart-legend-pct">{pct:.0f}%</tspan></text>'
        )

    parts.append("</svg>")
    return "".join(parts)


def render_chart_svg(spec: dict[str, Any] | None) -> str:
    """Public entrypoint. Returns inline SVG string or empty string on failure."""
    if not isinstance(spec, dict):
        return ""
    kind = (spec.get("kind") or "bar").lower()
    try:
        if kind == "line":
            return _line(spec)
        if kind == "pie" or kind == "donut":
            return _pie(spec)
        return _bar(spec)
    except Exception:
        return ""
