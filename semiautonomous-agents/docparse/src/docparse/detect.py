from __future__ import annotations

from .gemini import FLASH_MODEL, LITE_MODEL, call_vision
from .prompts import DETECT_REGIONS
from .render import RenderedPage, image_to_png_bytes, normalize_bbox
from .schemas import PageRegions, Region, RegionType


# Detect just needs bbox accuracy, not pixel-level legibility -> cheaper image.
DETECT_MAX_DIM = 1024
# A bbox below this fractional area is treated as model garbage.
MIN_BBOX_AREA = 0.001


def _bbox_area(bbox: list[float]) -> float:
    x1, y1, x2, y2 = bbox
    return max(0.0, x2 - x1) * max(0.0, y2 - y1)


async def _call_detect(page_img_bytes: bytes, model: str, timeout_s: float) -> list[Region]:
    # NOTE: tried thinking_budget=0 here -- it makes detect ~2x faster but
    # gives sloppy bboxes (e.g. cuts charts in half), which then poisons
    # the chart/photo extractors downstream. Default thinking is worth it.
    result: PageRegions = await call_vision(
        model=model,
        prompt=DETECT_REGIONS,
        image_bytes=page_img_bytes,
        response_model=PageRegions,
        timeout_s=timeout_s,
        max_retries=2,
    )
    regions = sorted(result.regions, key=lambda r: r.reading_order)
    for r in regions:
        r.bbox = list(normalize_bbox(r.bbox))
    return regions


async def detect_regions(page: RenderedPage) -> list[Region]:
    img_bytes = image_to_png_bytes(page.image, max_dim=DETECT_MAX_DIM)

    # First attempt: cheap + fast lite model.
    try:
        regions = await _call_detect(img_bytes, LITE_MODEL, timeout_s=45.0)
        # Lite occasionally collapses right-column regions to (1,1,1,1).
        # If any non-decorative region is degenerate, retry on flash.
        bad = [
            r for r in regions
            if r.type not in {RegionType.HEADER, RegionType.FOOTER}
            and _bbox_area(r.bbox) < MIN_BBOX_AREA
        ]
        if regions and not bad:
            return regions
    except Exception:  # noqa: BLE001
        regions = []

    # Retry with flash for higher bbox quality.
    try:
        regions = await _call_detect(img_bytes, FLASH_MODEL, timeout_s=60.0)
        if regions:
            return regions
    except Exception:  # noqa: BLE001
        pass

    # Final fallback: whole-page body so page OCR still produces output.
    return [
        Region(
            type=RegionType.BODY,
            bbox=[0.0, 0.0, 1.0, 1.0],
            reading_order=1,
            description="(detect failed; full-page fallback)",
        )
    ]
