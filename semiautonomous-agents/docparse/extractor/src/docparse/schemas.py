from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class RegionType(str, Enum):
    HEADING = "heading"
    BODY = "body"
    TABLE = "table"
    CHART = "chart"
    DIAGRAM = "diagram"
    PHOTO = "photo"
    QUOTE = "quote"
    CAPTION = "caption"
    FOOTNOTE = "footnote"
    HEADER = "header"
    FOOTER = "footer"


class Region(BaseModel):
    type: RegionType
    bbox: list[float] = Field(description="[x1,y1,x2,y2] as fractions 0-1")
    reading_order: int
    description: str = ""


class PageRegions(BaseModel):
    regions: list[Region]


class ChartType(str, Enum):
    BAR = "bar"
    STACKED_BAR = "stacked_bar"
    GROUPED_BAR = "grouped_bar"
    LINE = "line"
    AREA = "area"
    PIE = "pie"
    DONUT = "donut"
    SCATTER = "scatter"
    BUBBLE = "bubble"
    HEATMAP = "heatmap"
    SANKEY = "sankey"
    TREEMAP = "treemap"
    RADAR = "radar"
    OTHER = "other"


class ChartSeries(BaseModel):
    name: str
    color_hex: str | None = None
    values: list[float | None] = Field(
        description="Numeric value per x_category. For ranges (e.g. '560-850'), "
                    "use the midpoint here so downstream math still works.",
    )
    value_labels: list[str | None] = Field(
        default_factory=list,
        description="Literal text label as shown on the chart per x_category. "
                    "For single values, the number as printed (e.g. '53' or '53%'). "
                    "For ranges, the literal text (e.g. '560-850' or '$560-$850'). "
                    "For lists or annotated values, the literal label. "
                    "MUST have the same length as values when populated; the "
                    "markdown stitcher prefers value_labels over values when "
                    "rendering, so ranges are preserved verbatim. "
                    "If empty, values are rendered as plain numbers.",
    )


class ChartSchemaOnly(BaseModel):
    """Pass-1 output: chart structure (type, axes, categories, legend names)
    WITHOUT values. Forces the model to commit to legend / category labels
    before reading numbers."""

    chart_type: ChartType
    title: str | None = None
    subtitle: str | None = None
    x_axis_label: str | None = None
    y_axis_label: str | None = None
    x_categories: list[str] = Field(
        description="Bar / tick labels along the x axis (or row labels for non-axis charts). "
                    "Read literal text from the image.",
    )
    series_names: list[str] = Field(
        description="Literal legend entries (left-to-right or top-to-bottom). "
                    "Use exact text shown in the legend / color key. If the legend is "
                    "not visible in the image, return ['(legend not visible)'].",
    )
    value_unit: str | None = Field(
        default=None,
        description="e.g. '%', 'USD', 'count', 'index'",
    )
    legend_visible: bool = Field(
        description="True only if the legend / color key was clearly readable.",
    )


class ChartData(BaseModel):
    chart_type: ChartType
    title: str | None = None
    subtitle: str | None = None
    x_axis_label: str | None = None
    y_axis_label: str | None = None
    x_categories: list[str] = Field(default_factory=list)
    series: list[ChartSeries] = Field(default_factory=list)
    value_unit: str | None = None
    source_caption: str | None = None
    notes: str | None = None
    summary: str = Field(description="One-sentence plain-English summary")
    legend_visible: bool = True
    validator_failures: list[str] = Field(
        default_factory=list,
        description="Runtime predicate failures that survived retries. Surfaced for human review.",
    )


class TableData(BaseModel):
    title: str | None = None
    headers: list[str]
    rows: list[list[str]]
    caption: str | None = None


class TextBlock(BaseModel):
    level: int = Field(default=0, description="0=body, 1-6=heading levels")
    text: str


class PhotoCaption(BaseModel):
    alt_text: str
    overlay_text: str | None = None
    caption: str | None = None


class DiagramData(BaseModel):
    title: str | None = None
    mermaid: str | None = None
    prose: str | None = None
    caption: str | None = None


class ExtractedRegion(BaseModel):
    page: int
    reading_order: int
    type: RegionType
    markdown: str
    confidence: float = 1.0
    raw: dict | None = None
