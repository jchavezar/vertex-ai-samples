from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image


@dataclass
class RenderedPage:
    page_num: int
    image: Image.Image
    width: int       # pixels
    height: int      # pixels
    width_pts: float
    height_pts: float
    text_layer: str
    _textpage: object | None = None  # pypdfium2 PdfTextPage handle


def render_pdf(pdf_path: Path, dpi: int = 200) -> list[RenderedPage]:
    """Render every page to a PIL image + keep its text page handle."""
    pdf = pdfium.PdfDocument(str(pdf_path))
    scale = dpi / 72.0
    out: list[RenderedPage] = []
    for i, page in enumerate(pdf, start=1):
        bitmap = page.render(scale=scale)
        pil = bitmap.to_pil().convert("RGB")
        textpage = page.get_textpage()
        text = textpage.get_text_range() or ""
        w_pts, h_pts = page.get_size()
        out.append(
            RenderedPage(
                page_num=i,
                image=pil,
                width=pil.width,
                height=pil.height,
                width_pts=w_pts,
                height_pts=h_pts,
                text_layer=text,
                _textpage=textpage,
            )
        )
    return out


def normalize_bbox(bbox: list[float]) -> tuple[float, float, float, float]:
    """Coerce a model-returned bbox into a clean [x1,y1,x2,y2] in [0,1]."""
    coords = [float(c) for c in bbox][:4]
    while len(coords) < 4:
        coords.append(1.0 if len(coords) >= 2 else 0.0)
    x1, y1, x2, y2 = (max(0.0, min(1.0, c)) for c in coords)
    if x2 < x1:
        x1, x2 = x2, x1
    if y2 < y1:
        y1, y2 = y2, y1
    return x1, y1, x2, y2


def crop_region(image: Image.Image, bbox: list[float]) -> Image.Image:
    """Crop a region given fractional bbox [x1,y1,x2,y2].

    Tolerant to model-returned bboxes that are inverted, out-of-range,
    have wrong arity, or are zero-area.
    """
    w, h = image.size
    x1, y1, x2, y2 = normalize_bbox(bbox)
    left = max(0, int(x1 * w))
    upper = max(0, int(y1 * h))
    right = max(left + 1, min(w, int(x2 * w)))
    lower = max(upper + 1, min(h, int(y2 * h)))
    return image.crop((left, upper, right, lower))


def text_in_bbox(page: RenderedPage, bbox: list[float], pad: float = 0.005) -> str:
    """Return text from the PDF text layer that falls inside `bbox`.

    bbox is fractional [x1,y1,x2,y2] with origin top-left (image coords).
    PDF coordinates are bottom-left origin in points.
    """
    if page._textpage is None:
        return ""
    x1, y1, x2, y2 = bbox
    x1 = max(0.0, x1 - pad)
    y1 = max(0.0, y1 - pad)
    x2 = min(1.0, x2 + pad)
    y2 = min(1.0, y2 + pad)
    left = x1 * page.width_pts
    right = x2 * page.width_pts
    top_pts = (1.0 - y1) * page.height_pts
    bottom_pts = (1.0 - y2) * page.height_pts
    try:
        return page._textpage.get_text_bounded(
            left=left, bottom=bottom_pts, right=right, top=top_pts
        ) or ""
    except Exception:
        return ""


def image_to_png_bytes(image: Image.Image, max_dim: int = 2048) -> bytes:
    """Encode PIL image to PNG bytes, downscaling if too large."""
    img = image
    if max(img.size) > max_dim:
        img.thumbnail((max_dim, max_dim))
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
