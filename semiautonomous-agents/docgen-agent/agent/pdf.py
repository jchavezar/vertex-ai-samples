"""PDF rendering for docgen-agent.

Pure-Python reportlab so it runs on managed Agent Engine (no native libs).
Returns raw bytes; the caller wraps them in a `types.Part` artifact.
"""
from __future__ import annotations

import io
import re
from datetime import datetime, timezone

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(text: str, max_len: int = 60) -> str:
    """ASCII slug suitable for a filename. Falls back to a timestamp if empty."""
    s = _SLUG_RE.sub("_", (text or "").lower()).strip("_")
    if not s:
        s = datetime.now(timezone.utc).strftime("report_%Y%m%d_%H%M%S")
    return s[:max_len]


def _build_styles():
    base = getSampleStyleSheet()
    title = ParagraphStyle(
        "DocgenTitle",
        parent=base["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#1a73e8"),
        spaceAfter=4,
    )
    subtitle = ParagraphStyle(
        "DocgenSubtitle",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=12,
        textColor=colors.HexColor("#5f6368"),
        spaceAfter=18,
    )
    h2 = ParagraphStyle(
        "DocgenH2",
        parent=base["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#202124"),
        spaceBefore=14,
        spaceAfter=6,
    )
    body = ParagraphStyle(
        "DocgenBody",
        parent=base["BodyText"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=15,
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor("#202124"),
        spaceAfter=8,
    )
    bullet = ParagraphStyle(
        "DocgenBullet",
        parent=body,
        leftIndent=12,
        bulletIndent=0,
        spaceAfter=2,
        alignment=TA_LEFT,
    )
    source = ParagraphStyle(
        "DocgenSource",
        parent=body,
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#3c4043"),
        spaceAfter=4,
    )
    return {
        "title": title,
        "subtitle": subtitle,
        "h2": h2,
        "body": body,
        "bullet": bullet,
        "source": source,
    }


def _escape(text: str) -> str:
    """reportlab Paragraph treats `<` as markup. Escape user content."""
    return (
        (text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def render_pdf(
    title: str,
    sections: list[dict],
    sources: list[dict] | None = None,
    subtitle: str | None = None,
) -> bytes:
    """Render a clean report PDF and return its bytes.

    sections: list of {"heading": str, "body": str, "bullets"?: list[str]}
    sources:  list of {"title": str, "uri": str}
    """
    styles = _build_styles()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=LETTER,
        leftMargin=0.9 * inch,
        rightMargin=0.9 * inch,
        topMargin=0.8 * inch,
        bottomMargin=0.8 * inch,
        title=title or "Report",
        author="docgen-agent",
    )

    story = []
    story.append(Paragraph(_escape(title or "Report"), styles["title"]))
    sub = subtitle or datetime.now(timezone.utc).strftime("Generated %Y-%m-%d UTC")
    story.append(Paragraph(_escape(sub), styles["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#dadce0")))
    story.append(Spacer(1, 10))

    for section in sections or []:
        heading = section.get("heading") or ""
        body = section.get("body") or ""
        bullets = section.get("bullets") or []
        if heading:
            story.append(Paragraph(_escape(heading), styles["h2"]))
        if body:
            for para in str(body).split("\n\n"):
                para = para.strip()
                if para:
                    story.append(Paragraph(_escape(para), styles["body"]))
        if bullets:
            items = [
                ListItem(Paragraph(_escape(str(b)), styles["bullet"]), leftIndent=12)
                for b in bullets
            ]
            story.append(ListFlowable(items, bulletType="bullet", leftIndent=14))
            story.append(Spacer(1, 4))

    if sources:
        story.append(PageBreak())
        story.append(Paragraph("Sources", styles["h2"]))
        story.append(HRFlowable(width="100%", thickness=0.4, color=colors.HexColor("#dadce0")))
        story.append(Spacer(1, 6))
        for i, src in enumerate(sources, 1):
            t = _escape(src.get("title") or src.get("uri") or "Untitled")
            uri = _escape(src.get("uri") or "")
            if uri:
                line = f'[{i}] {t}<br/><font color="#1a73e8">{uri}</font>'
            else:
                line = f"[{i}] {t}"
            story.append(Paragraph(line, styles["source"]))

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buf.getvalue()


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#80868b"))
    canvas.drawRightString(
        LETTER[0] - 0.9 * inch,
        0.45 * inch,
        f"Page {doc.page}",
    )
    canvas.drawString(
        0.9 * inch,
        0.45 * inch,
        "docgen-agent",
    )
    canvas.restoreState()
