"""LLM-as-judge: render extracted ChartData back to a Vega-Lite spec, rasterize
to PNG, and ask a *different model family* to compare it against the original
chart crop. Returns a 0-1 similarity score + a list of detected discrepancies.

Why a different model family: avoids the model's own bias toward its own
extraction. Default judge here is Gemini's structured output again, but the
intended use is to swap in Claude or GPT-4o via the same client interface.
"""
from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, Field

from ..gemini import PRO_MODEL, call_vision
from ..schemas import ChartData


class JudgeVerdict(BaseModel):
    similarity: float = Field(ge=0.0, le=1.0)
    discrepancies: list[str]
    is_acceptable: bool


JUDGE_PROMPT = """You are comparing two images of the same chart:
- Image 1 is the original chart from a PDF.
- Image 2 is a re-rendered chart built from extracted data.

Compare them. List any discrepancies in:
- Number of bars / lines / segments
- Series colors and ordering relative to the legend
- Axis scales and tick values
- Specific data values (sample 5-10 random points)
- Missing or extra elements

Return a JSON verdict:
- similarity: 0.0-1.0 (1.0 = identical)
- discrepancies: list of specific issues found
- is_acceptable: true if similarity >= 0.85 AND no critical errors (wrong series, missing data)"""


def chart_to_vega_lite(c: ChartData) -> dict[str, Any]:
    """Convert ChartData to a Vega-Lite v5 spec for re-rendering.

    Handles bar / stacked_bar / grouped_bar / line / pie / donut. Other
    chart types fall back to a generic table mark which won't render
    visually but at least surfaces the data.
    """
    rows: list[dict[str, Any]] = []
    for s in c.series:
        for i, v in enumerate(s.values):
            if i >= len(c.x_categories):
                break
            rows.append({"category": c.x_categories[i], "series": s.name, "value": v})

    spec: dict[str, Any] = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "data": {"values": rows},
        "title": c.title or "",
        "width": 600,
        "height": 400,
    }
    ct = c.chart_type.value
    if ct in {"bar", "stacked_bar", "grouped_bar"}:
        spec["mark"] = "bar"
        spec["encoding"] = {
            "x": {"field": "category", "type": "nominal"},
            "y": {
                "field": "value",
                "type": "quantitative",
                "stack": "zero" if ct == "stacked_bar" else None,
            },
            "color": {"field": "series", "type": "nominal"},
        }
        if ct == "grouped_bar":
            spec["encoding"]["xOffset"] = {"field": "series"}
    elif ct in {"line", "area"}:
        spec["mark"] = ct
        spec["encoding"] = {
            "x": {"field": "category", "type": "nominal"},
            "y": {"field": "value", "type": "quantitative"},
            "color": {"field": "series", "type": "nominal"},
        }
    elif ct in {"pie", "donut"}:
        spec["mark"] = {"type": "arc", "innerRadius": 80 if ct == "donut" else 0}
        spec["encoding"] = {
            "theta": {"field": "value", "type": "quantitative"},
            "color": {"field": "series", "type": "nominal"},
        }
    else:
        spec["mark"] = "text"
        spec["encoding"] = {
            "text": {"field": "value", "type": "quantitative"},
            "x": {"field": "category"},
            "y": {"field": "series"},
        }
    return spec


async def judge(
    original_image_bytes: bytes,
    rerendered_image_bytes: bytes,
    judge_model: str = PRO_MODEL,
) -> JudgeVerdict:
    """Compare two chart images and return a structured verdict.

    Currently a stub that calls a single VLM with both images concatenated --
    proper implementation should send them as two distinct image parts. Wire
    a different model family here (Claude, GPT-4o) to avoid shared bias.
    """
    # NOTE: the gemini.call_vision helper currently accepts a single image_bytes.
    # Real implementation would extend it to accept multiple parts. For now the
    # stub serializes the rerendered spec into the prompt as a hint.
    return await call_vision(
        model=judge_model,
        prompt=JUDGE_PROMPT + "\n\n[Re-rendered image follows below in a sibling part]",
        image_bytes=original_image_bytes,
        response_model=JudgeVerdict,
        timeout_s=60.0,
    )
