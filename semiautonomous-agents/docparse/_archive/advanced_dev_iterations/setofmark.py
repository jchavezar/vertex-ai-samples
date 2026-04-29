"""Set-of-Mark prompting (arXiv 2310.11441) for chart extraction.

Pre-processes a chart image by overlaying numbered marks on the most
informative regions (legend swatches, axis ticks, bar centers), then
sends the marked image to the VLM with a prompt that references marks by
number. This anchors VLM attention and significantly reduces series-color
misassignment errors on dense charts.

This module provides the marker overlay; the prompt template lives next to
it. Wire into a custom orchestrator when the default pipeline's two-pass
extraction misses the legend-color-mapping on a specific chart.
"""
from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont


SOM_PROMPT_TEMPLATE = """The chart in this image has had numbered marks overlaid on its key elements:
- Legend swatches are marked L1, L2, L3, ...
- X-axis tick labels are marked X1, X2, X3, ...
- Bar centers / data points are marked D1, D2, D3, ...

Use these marks to identify each series and value precisely. When you
report a series name, reference the L-mark you read it from (e.g. "L2: Gen X").
When you report a value, reference the D-mark (e.g. "D7 = 53"). This avoids
ambiguity from adjacent colors or overlapping labels."""


def overlay_marks(
    image: Image.Image,
    legend_boxes: list[tuple[int, int, int, int]] | None = None,
    xtick_positions: list[tuple[int, int]] | None = None,
    data_positions: list[tuple[int, int]] | None = None,
    color: str = "#FF00FF",
) -> Image.Image:
    """Overlay numbered marks on the chart. Returns a new image (input
    unchanged).

    Caller is responsible for computing the positions -- typically by asking
    a small VLM call beforehand to locate legend boxes and bar centers, or
    by deriving them from a structure-only first pass.
    """
    out = image.copy()
    draw = ImageDraw.Draw(out)
    font = _load_font(20)

    for i, box in enumerate(legend_boxes or [], start=1):
        x, y, _, _ = box
        _stamp(draw, f"L{i}", x - 4, y - 4, color, font)

    for i, (x, y) in enumerate(xtick_positions or [], start=1):
        _stamp(draw, f"X{i}", x, y, color, font)

    for i, (x, y) in enumerate(data_positions or [], start=1):
        _stamp(draw, f"D{i}", x, y, color, font)

    return out


def _stamp(draw: ImageDraw.ImageDraw, text: str, x: int, y: int, color: str, font) -> None:
    bbox = draw.textbbox((x, y), text, font=font)
    pad = 2
    draw.rectangle(
        (bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad),
        fill="white",
        outline=color,
        width=2,
    )
    draw.text((x, y), text, fill=color, font=font)


def _load_font(size: int):
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except Exception:  # noqa: BLE001
            continue
    return ImageFont.load_default()
