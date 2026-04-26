"""PDF renderer agent.

Reads `state['report_for_render']` (a ResearchReport JSON), populates a
Jinja2 HTML template, and converts to PDF with WeasyPrint. Emits the
output path back into state and a chat message with a download hint.

We use a plain BaseAgent (not LlmAgent) because PDF rendering is pure
I/O — no need to spend tokens on it.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncGenerator

import markdown_it
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai.types import Content, Part
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

from .charts import render_chart_svg
from .schemas import ResearchReport

_TEMPLATES_DIR = Path(__file__).parent / "templates"
_DEFAULT_OUTPUT_DIR = Path(
    os.environ.get(
        "REPORT_OUTPUT_DIR",
        Path(__file__).resolve().parents[1] / "outputs",
    )
)

_md = markdown_it.MarkdownIt("commonmark", {"breaks": True, "html": False})


def _render_markdown(text: str) -> str:
    return _md.render(text or "")


def _slugify(text: str) -> str:
    keep = "abcdefghijklmnopqrstuvwxyz0123456789-"
    return "".join(c if c in keep else "-" for c in text.lower()).strip("-")[:60] or "report"


def render_report_to_pdf(report: ResearchReport, output_dir: Path | None = None) -> Path:
    """Public, agent-free entrypoint — useful for tests and run_local.py."""
    out_dir = Path(output_dir or _DEFAULT_OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    env.filters["md"] = _render_markdown
    env.globals["render_chart"] = render_chart_svg
    template = env.get_template("report.html.j2")

    now = datetime.now(timezone.utc)
    if report.generated_at:
        try:
            now = datetime.fromisoformat(report.generated_at.replace("Z", "+00:00"))
        except ValueError:
            pass
    pretty = now.strftime("%B %-d, %Y")
    full = now.strftime("%B %-d, %Y · %H:%M UTC")

    html_str = template.render(
        report=report,
        generated_at=full,
        generated_date=pretty,
    )

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    base = f"{stamp}-{_slugify(report.topic)}"
    (out_dir / f"{base}.json").write_text(report.model_dump_json(indent=2))
    (out_dir / f"{base}.html").write_text(html_str)
    pdf_path = out_dir / f"{base}.pdf"
    HTML(string=html_str, base_url=str(_TEMPLATES_DIR)).write_pdf(str(pdf_path))
    return pdf_path


class PdfRendererAgent(BaseAgent):
    """Custom agent that converts state['report_for_render'] -> PDF."""

    output_dir: Path = _DEFAULT_OUTPUT_DIR

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        raw = ctx.session.state.get("report_for_render") or ctx.session.state.get("report")
        if raw is None:
            yield Event(
                author=self.name,
                content=Content(parts=[Part(text="No report in state — nothing to render.")]),
            )
            return

        report = (
            raw if isinstance(raw, ResearchReport)
            else ResearchReport.model_validate(raw)
        )

        try:
            pdf_path = render_report_to_pdf(report, self.output_dir)
        except Exception as e:  # noqa: BLE001 — surface to user
            import traceback
            tb = traceback.format_exc()
            yield Event(
                author=self.name,
                content=Content(parts=[Part(text=f"PDF rendering failed: {type(e).__name__}: {e}\n{tb}")]),
            )
            return

        ctx.session.state["pdf_path"] = str(pdf_path)
        msg = (
            f"Report ready: **{report.topic}**\n\n"
            f"- Sections: {len(report.sections)}\n"
            f"- Sources cited: {len(report.sources)}\n"
            f"- Generated: {report.generated_at}\n"
            f"- PDF: `{pdf_path}`"
        )
        yield Event(author=self.name, content=Content(parts=[Part(text=msg)]))
