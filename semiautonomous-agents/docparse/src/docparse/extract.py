from __future__ import annotations

from .gemini import FLASH_MODEL, LITE_MODEL, PRO_MODEL, call_vision
from .prompts import (
    CHART_RETRY_PROMPT,
    CHART_SCHEMA_PROMPT,
    CHART_VALUES_PROMPT,
    DIAGRAM_EXTRACT,
    PAGE_OCR_TEMPLATE,
    PHOTO_DESCRIBE,
    TABLE_EXTRACT,
)
from .render import RenderedPage, crop_region, image_to_png_bytes
from .schemas import (
    ChartData,
    ChartSchemaOnly,
    ChartSeries,
    DiagramData,
    ExtractedRegion,
    PhotoCaption,
    Region,
    RegionType,
    TableData,
)
from .validators import validate as validate_chart


STRUCTURED_TYPES = {RegionType.CHART, RegionType.TABLE, RegionType.DIAGRAM, RegionType.PHOTO}

# Page OCR doesn't need pixel-level legibility for body type, but it does need
# to read overlay text well enough to match it against structured-region bboxes.
PAGE_OCR_MAX_DIM = 1280
# Charts: send the FULL PAGE to pro (no crop). The bbox-too-tight failure
# mode (legend cut off) is the single biggest source of silent chart errors.
# Full-page costs ~10-15% more tokens but eliminates that failure entirely.
CHART_PAGE_MAX_DIM = 1800
TABLE_MAX_DIM = 1600
# Diagrams: same reasoning as charts -- full page, no crop.
DIAGRAM_PAGE_MAX_DIM = 1800
# Photo captioning is the only structured type that still benefits from
# focused cropping (alt-text generation, less context-sensitive).
PHOTO_MAX_DIM = 1280

# Chart retry budget on validator failure.
MAX_CHART_RETRIES = 1


# ---------- Markdown formatters -----------------------------------------------


def _md_table(headers: list[str], rows: list[list[str]]) -> str:
    if not headers:
        return ""
    head = "| " + " | ".join(_escape_cell(h) for h in headers) + " |"
    sep = "|" + "|".join("---" for _ in headers) + "|"
    body = "\n".join(
        "| " + " | ".join(_escape_cell(c) for c in row) + " |" for row in rows
    )
    return "\n".join([head, sep, body])


def _escape_cell(s: str) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ").strip()


def _chart_to_markdown(c: ChartData) -> str:
    lines: list[str] = []
    title = c.title or "Untitled chart"
    lines.append(f"### {title}")
    if c.subtitle:
        lines.append(f"*{c.subtitle}*")
    lines.append("")
    lines.append(f"**Chart type:** {c.chart_type.value}  ")
    if c.value_unit:
        lines.append(f"**Unit:** {c.value_unit}  ")
    lines.append("")
    lines.append(f"**Summary:** {c.summary}")
    lines.append("")

    if c.x_categories and c.series:
        x_label = c.x_axis_label or "Category"
        headers = [x_label] + [s.name for s in c.series]
        rows: list[list[str]] = []
        n = len(c.x_categories)
        for i in range(n):
            row = [c.x_categories[i]]
            for s in c.series:
                v = s.values[i] if i < len(s.values) else None
                row.append("" if v is None else _fmt_num(v))
            rows.append(row)
        lines.append(_md_table(headers, rows))
        lines.append("")

    if c.notes:
        lines.append(f"_Notes: {c.notes}_")
        lines.append("")
    if c.source_caption:
        lines.append(f"_Source: {c.source_caption}_")
        lines.append("")
    if getattr(c, "validator_failures", None):
        lines.append("> **[LOW CONFIDENCE — validator flags]**")
        for f in c.validator_failures:
            lines.append(f"> - {f}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _fmt_num(v: float) -> str:
    if v == int(v):
        return str(int(v))
    return f"{v:g}"


def _table_to_markdown(t: TableData) -> str:
    lines: list[str] = []
    if t.title:
        lines.append(f"### {t.title}")
        lines.append("")
    lines.append(_md_table(t.headers, t.rows))
    if t.caption:
        lines.append("")
        lines.append(f"_{t.caption}_")
    return "\n".join(lines).rstrip() + "\n"


def _photo_to_markdown(p: PhotoCaption) -> str:
    parts = [f"> **Image:** {p.alt_text}"]
    if p.overlay_text:
        parts.append(f"> **Overlay text:** {p.overlay_text}")
    if p.caption:
        parts.append(f"> _{p.caption}_")
    return "\n".join(parts) + "\n"


def _diagram_to_markdown(d: DiagramData) -> str:
    lines: list[str] = []
    if d.title:
        lines.append(f"### {d.title}")
        lines.append("")
    if d.mermaid:
        lines.append("```mermaid")
        lines.append(d.mermaid.strip())
        lines.append("```")
    elif d.prose:
        lines.append(d.prose.strip())
    if d.caption:
        lines.append("")
        lines.append(f"_{d.caption}_")
    return "\n".join(lines).rstrip() + "\n"


# ---------- Public entry points -----------------------------------------------


def _bbox_str(bbox: list[float]) -> str:
    return "[" + ", ".join(f"{v:.3f}" for v in bbox) + "]"


async def _extract_chart(page: RenderedPage, region: Region) -> tuple[str, dict, float]:
    """Two-pass chart extraction with runtime validators and one retry on failure.

    Pass 1 (flash): commits to chart_type, x_categories, series_names from the
                    legend. Forces the model to look at the legend before
                    inventing series names.
    Pass 2 (pro):   reads numeric values constrained by the pass-1 schema.
    Validate:       cheap Python predicates (sum-to-100, monotonic, etc).
    Retry:          one re-extraction with the specific failures surfaced.
    """
    page_bytes = image_to_png_bytes(page.image, max_dim=CHART_PAGE_MAX_DIM)
    bbox_str = _bbox_str(region.bbox)

    # ---- Pass 1: structure ----
    schema: ChartSchemaOnly = await call_vision(
        model=FLASH_MODEL,
        prompt=CHART_SCHEMA_PROMPT.format(bbox=bbox_str),
        image_bytes=page_bytes,
        response_model=ChartSchemaOnly,
        timeout_s=45.0,
    )

    # ---- Pass 2: values ----
    values_prompt = CHART_VALUES_PROMPT.format(
        bbox=bbox_str,
        chart_type=schema.chart_type.value,
        n_categories=len(schema.x_categories),
        x_categories=schema.x_categories,
        n_series=len(schema.series_names),
        series_names=schema.series_names,
        value_unit=schema.value_unit,
        legend_visible=schema.legend_visible,
    )
    data: ChartData = await call_vision(
        model=PRO_MODEL,
        prompt=values_prompt,
        image_bytes=page_bytes,
        response_model=ChartData,
        timeout_s=90.0,
    )

    # ---- Validate + (optional) retry ----
    failures = validate_chart(data)
    confidence = 1.0
    if failures:
        retry_prompt = (
            values_prompt
            + "\n\n"
            + CHART_RETRY_PROMPT.format(
                bbox=bbox_str,
                failures="\n  - " + "\n  - ".join(failures),
            )
        )
        try:
            data = await call_vision(
                model=PRO_MODEL,
                prompt=retry_prompt,
                image_bytes=page_bytes,
                response_model=ChartData,
                timeout_s=90.0,
            )
            failures = validate_chart(data)
        except Exception:  # noqa: BLE001
            pass  # keep the first attempt's data
        confidence = 0.5 if failures else 0.9

    data.legend_visible = schema.legend_visible
    data.validator_failures = failures
    return _chart_to_markdown(data), data.model_dump(), confidence


async def extract_structured(page: RenderedPage, region: Region) -> ExtractedRegion:
    """Extract a single STRUCTURED region (chart/table/diagram/photo) → markdown."""
    md: str
    raw: dict | None = None
    confidence: float = 1.0

    try:
        if region.type == RegionType.CHART:
            md, raw, confidence = await _extract_chart(page, region)

        elif region.type == RegionType.DIAGRAM:
            # Full page to pro, bbox as text hint -- same rationale as charts.
            page_bytes = image_to_png_bytes(page.image, max_dim=DIAGRAM_PAGE_MAX_DIM)
            data = await call_vision(
                model=PRO_MODEL,
                prompt=DIAGRAM_EXTRACT
                + f"\n\nThe diagram you must extract is in the bbox region {_bbox_str(region.bbox)} "
                  f"(fractional coordinates, top-left origin) on the page image attached. "
                  f"Ignore other content on the page.",
                image_bytes=page_bytes,
                response_model=DiagramData,
                timeout_s=60.0,
            )
            md = _diagram_to_markdown(data)
            raw = data.model_dump()

        elif region.type == RegionType.TABLE:
            cropped = crop_region(page.image, region.bbox)
            data = await call_vision(
                model=FLASH_MODEL,
                prompt=TABLE_EXTRACT,
                image_bytes=image_to_png_bytes(cropped, max_dim=TABLE_MAX_DIM),
                response_model=TableData,
                timeout_s=45.0,
                thinking_budget=0,
            )
            md = _table_to_markdown(data)
            raw = data.model_dump()

        elif region.type == RegionType.PHOTO:
            cropped = crop_region(page.image, region.bbox)
            data = await call_vision(
                model=LITE_MODEL,
                prompt=PHOTO_DESCRIBE,
                image_bytes=image_to_png_bytes(cropped, max_dim=PHOTO_MAX_DIM),
                response_model=PhotoCaption,
                timeout_s=30.0,
                thinking_budget=0,
            )
            md = _photo_to_markdown(data)
            raw = data.model_dump()
        else:
            md = ""
    except Exception as e:  # noqa: BLE001
        md = f"> **[{region.type.value} extraction failed: {e}]**\n"
        confidence = 0.0

    return ExtractedRegion(
        page=page.page_num,
        reading_order=region.reading_order,
        type=region.type,
        markdown=md,
        confidence=confidence,
        raw=raw,
    )


async def extract_page_text(page: RenderedPage, regions: list[Region]) -> str:
    """One-shot: convert the whole page to markdown with placeholders for
    structured regions. Returns the page markdown string."""
    structured = [r for r in regions if r.type in STRUCTURED_TYPES]
    text_present = any(
        r.type
        in {
            RegionType.HEADING,
            RegionType.BODY,
            RegionType.QUOTE,
            RegionType.CAPTION,
            RegionType.FOOTNOTE,
        }
        for r in regions
    )
    if not structured and not text_present:
        return ""

    summary_lines = []
    for r in structured:
        bb = ", ".join(f"{v:.2f}" for v in r.bbox)
        summary_lines.append(
            f"  - REGION:{r.reading_order} type={r.type.value} bbox=[{bb}] — {r.description}"
        )
    summary = "\n".join(summary_lines) if summary_lines else "  (none)"
    prompt = PAGE_OCR_TEMPLATE.format(regions_summary=summary)

    img_bytes = image_to_png_bytes(page.image, max_dim=PAGE_OCR_MAX_DIM)
    try:
        text = await call_vision(
            model=FLASH_MODEL,
            prompt=prompt,
            image_bytes=img_bytes,
            response_model=None,
            timeout_s=75.0,
            max_retries=2,
            thinking_budget=0,  # text reflow with placeholders, no reasoning needed
        )
        return (text or "").strip()
    except Exception as e:  # noqa: BLE001
        return f"> **[page OCR failed: {e}]**"
