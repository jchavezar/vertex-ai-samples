from __future__ import annotations

import asyncio
import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

from rich.console import Console

from .detect import detect_regions
from .extract import (
    STRUCTURED_TYPES,
    extract_page_raw_ocr,
    extract_page_text,
    extract_structured,
)
from .gemini import warm_up
from .render import RenderedPage, render_pdf
from .schemas import ExtractedRegion, Region


console = Console(stderr=True)

PLACEHOLDER_RE = re.compile(r"<!--\s*REGION:(\d+)\s*-->")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n+")


def _normalize_for_dedup(s: str) -> str:
    """Aggressive normalisation for substring matching."""
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return " ".join(s.split())


def _unique_sentences(raw_ocr: str, page_md: str) -> list[str]:
    """Return sentences from raw_ocr that don't substantively appear in page_md.

    A sentence is "covered" if its 6-word fingerprint (or majority of distinct
    content words) appears in page_md. Otherwise it's content the structured
    pipeline missed and we should append it.
    """
    if not raw_ocr.strip():
        return []
    page_norm = _normalize_for_dedup(page_md)
    sentences = [s.strip() for s in SENTENCE_SPLIT_RE.split(raw_ocr) if len(s.strip()) >= 12]
    out: list[str] = []
    seen_norm: set[str] = set()
    for s in sentences:
        s_norm = _normalize_for_dedup(s)
        if not s_norm or s_norm in seen_norm:
            continue
        seen_norm.add(s_norm)
        words = s_norm.split()
        if len(words) >= 6:
            fp = " ".join(words[:6])
            if fp in page_norm:
                continue
        content_words = [w for w in words if len(w) > 3]
        if content_words:
            hits = sum(1 for w in content_words if w in page_norm)
            if hits / len(content_words) >= 0.85:
                continue
        out.append(s)
    return out


@dataclass
class PageOutput:
    page_num: int
    page_markdown: str  # text with placeholders for structured regions
    structured: list[ExtractedRegion] = field(default_factory=list)
    raw_ocr: str = ""  # safety-net full-page OCR
    text_layer: str = ""  # PDF text layer for the page (free dedup source)


@dataclass
class PipelineResult:
    markdown: str
    pages: list[PageOutput]
    timings: dict[str, float]


async def _detect(page: RenderedPage, sem: asyncio.Semaphore) -> tuple[RenderedPage, list[Region]]:
    async with sem:
        regions = await detect_regions(page)
        n_struct = sum(1 for r in regions if r.type in STRUCTURED_TYPES)
        console.log(
            f"  page {page.page_num:>2}: {len(regions)} regions ({n_struct} structured)"
        )
        return page, regions


async def _process_page(
    page: RenderedPage,
    regions: list[Region],
    text_sem: asyncio.Semaphore,
    struct_sem: asyncio.Semaphore,
) -> PageOutput:
    """Run page-level OCR + raw-OCR safety net + per-region structured
    extracts concurrently."""

    async def _do_text() -> str:
        async with text_sem:
            t0 = time.time()
            md = await extract_page_text(page, regions)
            console.log(f"  page {page.page_num:>2}: text OCR done in {time.time() - t0:.1f}s")
            return md

    async def _do_raw_ocr() -> str:
        # Cheap full-page transcription. The dedup in stitch() only appends
        # sentences NOT already in page_md, so duplicates from this pass are
        # filtered out — meaning this pass only "wins" when it caught
        # something the structured pipeline lost (e.g. an overlay quote).
        async with text_sem:
            return await extract_page_raw_ocr(page)

    async def _do_structured(r: Region) -> ExtractedRegion:
        async with struct_sem:
            t0 = time.time()
            ex = await extract_structured(page, r)
            console.log(
                f"  page {page.page_num:>2} r{r.reading_order:>2} [{r.type.value:<7}] "
                f"-> {len(ex.markdown)} chars in {time.time() - t0:.1f}s"
            )
            return ex

    text_task = asyncio.create_task(_do_text())
    raw_task = asyncio.create_task(_do_raw_ocr())
    struct_tasks = [
        asyncio.create_task(_do_structured(r))
        for r in regions
        if r.type in STRUCTURED_TYPES
    ]
    results = await asyncio.gather(text_task, raw_task, *struct_tasks)
    page_md = results[0]
    raw_ocr = results[1]
    structured = [t.result() for t in struct_tasks]
    return PageOutput(
        page_num=page.page_num,
        page_markdown=page_md,
        structured=structured,
        raw_ocr=raw_ocr,
        text_layer=page.text_layer or "",
    )


async def parse_pdf_async(
    pdf_path: Path,
    detect_concurrency: int = 8,
    text_concurrency: int = 8,
    struct_concurrency: int = 8,
) -> PipelineResult:
    timings: dict[str, float] = {}

    t0 = time.time()
    pages, _ = await asyncio.gather(
        asyncio.to_thread(render_pdf, pdf_path),
        warm_up(),
    )
    timings["render_and_warmup"] = time.time() - t0
    console.log(
        f"rendered {len(pages)} pages + warmed client in {timings['render_and_warmup']:.1f}s"
    )

    t0 = time.time()
    detect_sem = asyncio.Semaphore(detect_concurrency)
    detect_results = await asyncio.gather(
        *[_detect(p, detect_sem) for p in pages]
    )
    timings["detect"] = time.time() - t0
    console.log(f"detected all regions in {timings['detect']:.1f}s")

    t0 = time.time()
    text_sem = asyncio.Semaphore(text_concurrency)
    struct_sem = asyncio.Semaphore(struct_concurrency)
    page_outputs = await asyncio.gather(
        *[
            _process_page(page, regions, text_sem, struct_sem)
            for page, regions in detect_results
        ]
    )
    timings["extract"] = time.time() - t0
    console.log(f"extracted all pages in {timings['extract']:.1f}s")

    md = stitch(page_outputs, pdf_path.stem)
    timings["total"] = sum(v for k, v in timings.items() if k != "total")
    return PipelineResult(markdown=md, pages=page_outputs, timings=timings)


def stitch(pages: list[PageOutput], doc_title: str) -> str:
    lines: list[str] = [f"# {doc_title}", ""]
    for po in sorted(pages, key=lambda p: p.page_num):
        lines.append(f"<!-- page: {po.page_num} -->")
        lines.append("")
        struct_by_order = {s.reading_order: s for s in po.structured}
        page_md = po.page_markdown

        def _sub(m: re.Match) -> str:
            ro = int(m.group(1))
            ex = struct_by_order.pop(ro, None)
            if ex is None:
                return ""
            return "\n" + ex.markdown.rstrip() + "\n"

        page_md = PLACEHOLDER_RE.sub(_sub, page_md)
        lines.append(page_md.strip())
        # Any structured extract whose placeholder was missing
        for ex in struct_by_order.values():
            lines.append("")
            lines.append(ex.markdown.rstrip())
        # v6 augment: append sentences from raw-OCR + PDF text layer that
        # are NOT in page_md. Catches overlaid quotes / attributions Gemini
        # OCR dropped, without duplicating body text.
        augment_sources = (po.raw_ocr or "") + "\n" + (po.text_layer or "")
        if augment_sources.strip():
            extra = _unique_sentences(augment_sources, page_md)
            if extra:
                lines.append("")
                for s in extra:
                    lines.append(s)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(result: PipelineResult, pdf_path: Path, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    md_path = out_dir / f"{pdf_path.stem}.md"
    md_path.write_text(result.markdown, encoding="utf-8")

    report_path = out_dir / f"{pdf_path.stem}.report.json"
    report = {
        "pdf": str(pdf_path),
        "timings_seconds": result.timings,
        "page_count": len(result.pages),
        "pages": [
            {
                "page": p.page_num,
                "page_markdown_chars": len(p.page_markdown),
                "structured": [
                    {
                        "reading_order": s.reading_order,
                        "type": s.type.value,
                        "confidence": s.confidence,
                        "chars": len(s.markdown),
                        "raw": s.raw,
                    }
                    for s in p.structured
                ],
            }
            for p in result.pages
        ],
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return md_path
