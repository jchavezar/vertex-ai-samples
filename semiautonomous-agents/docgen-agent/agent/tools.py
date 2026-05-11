"""FunctionTool that turns a structured outline into a PDF artifact.

The artifact is saved via `tool_context.save_artifact(...)`. Inside Agent
Engine + Gemini Enterprise this triggers GE's session-file metadata
poll and a download chip appears in the chat bubble.

GE's chip label is *always* `file_<microsecond_timestamp>.pdf` — neither
the `save_artifact` filename nor `Blob.display_name` propagates through
the public Discovery Engine SDK. The agent compensates by stating the
logical filename in the chat reply.

All exceptions are caught and returned as `{"status": "error", ...}` —
uncaught tool exceptions silently kill `stream_query` on Agent Engine.
"""
from __future__ import annotations

import logging
from typing import Any

from google.adk.tools import ToolContext
from google.genai import types

from .pdf import render_pdf, slugify

logger = logging.getLogger("docgen-agent.tools")
logger.setLevel(logging.INFO)


def _coerce_sections(sections: Any) -> list[dict]:
    """Be tolerant of model-emitted shapes."""
    if not sections:
        return []
    if isinstance(sections, dict):
        sections = [sections]
    out: list[dict] = []
    for s in sections:
        if isinstance(s, str):
            out.append({"heading": "", "body": s})
            continue
        if not isinstance(s, dict):
            continue
        out.append(
            {
                "heading": str(s.get("heading") or s.get("title") or ""),
                "body": str(s.get("body") or s.get("content") or ""),
                "bullets": [str(b) for b in (s.get("bullets") or [])],
            }
        )
    return out


def _coerce_sources(sources: Any) -> list[dict]:
    if not sources:
        return []
    if isinstance(sources, dict):
        sources = [sources]
    out: list[dict] = []
    for s in sources:
        if isinstance(s, str):
            out.append({"title": s, "uri": s if s.startswith("http") else ""})
            continue
        if not isinstance(s, dict):
            continue
        out.append(
            {
                "title": str(s.get("title") or s.get("name") or s.get("uri") or ""),
                "uri": str(s.get("uri") or s.get("url") or ""),
            }
        )
    return out


async def generate_pdf_report(
    title: str,
    sections: list[dict],
    sources: list[dict],
    tool_context: ToolContext,
) -> dict:
    """Render a PDF report from a structured outline and save it as a session artifact.

    Call this when the user has asked for a downloadable document, PDF, or
    report. The user will then see a download chip in the chat.

    Args:
      title: Report title — used as the PDF cover heading and to derive
        the artifact filename.
      sections: List of `{"heading": str, "body": str, "bullets"?: [str]}`.
        Body may contain blank-line-separated paragraphs.
      sources: List of `{"title": str, "uri": str}` for the references page.
        Pass an empty list if no sources.

    Returns:
      `{"status": "ok", "filename": str, "byte_size": int}` on success.
      `{"status": "error", "message": str}` on failure.
    """
    try:
        norm_sections = _coerce_sections(sections) or [
            {"heading": "Report", "body": "(No content provided.)"}
        ]
        norm_sources = _coerce_sources(sources)
        pdf_bytes = render_pdf(
            title=title or "Report",
            sections=norm_sections,
            sources=norm_sources,
        )
        filename = f"{slugify(title)}.pdf"
        await tool_context.save_artifact(
            filename=filename,
            artifact=types.Part.from_bytes(
                data=pdf_bytes, mime_type="application/pdf"
            ),
        )
        logger.info(
            "generate_pdf_report: saved %s (%d bytes, %d sections, %d sources)",
            filename, len(pdf_bytes), len(norm_sections), len(norm_sources),
        )
        return {
            "status": "ok",
            "filename": filename,
            "byte_size": len(pdf_bytes),
            "sections": len(norm_sections),
            "sources": len(norm_sources),
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception("generate_pdf_report failed")
        return {"status": "error", "message": f"PDF generation failed: {exc}"}
