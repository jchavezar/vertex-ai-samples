"""Pydantic schemas for the report-generator pipeline.

These types are the contract between agents in the SequentialAgent.
Keep field names stable — they're referenced by name in prompts.py.
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    query: str
    rationale: str
    classification: Literal["RESEARCH", "DELIVERABLE"] = "RESEARCH"


class ResearchPlan(BaseModel):
    topic: str
    audience: str = "general technical reader"
    queries: list[SearchQuery]
    deliverables: list[str] = Field(
        default_factory=list,
        description="Section headings the final report MUST contain.",
    )


class Source(BaseModel):
    id: str = Field(description="Stable id like 'src-1' used in <cite> tags.")
    title: str
    url: str
    domain: str
    snippet: str = ""
    publication_date: str | None = None
    author: str | None = None
    credibility_tier: Literal["primary", "reputable", "secondary", "unknown"] = "unknown"
    key_claims: list[str] = Field(default_factory=list)


class Finding(BaseModel):
    claim: str
    evidence: str
    source_ids: list[str]


class ResearchFindings(BaseModel):
    findings: list[Finding]
    sources: list[Source]
    coverage_notes: str = ""


class Critique(BaseModel):
    grade: Literal["pass", "fail"]
    comment: str
    follow_up_queries: list[SearchQuery] = Field(default_factory=list)


class Block(BaseModel):
    """A unit of report content. `text` carries narrative; `data` carries
    structured payload for visual blocks (tables, charts, metric grids,
    comparison cards). The renderer dispatches on `type`."""

    type: Literal[
        "paragraph",
        "callout",
        "quote",
        "list",
        "code",
        "metric",
        "metrics_grid",
        "table",
        "chart",
        "comparison",
    ] = "paragraph"
    text: str = ""
    data: dict[str, Any] | None = Field(
        default=None,
        description=(
            "Structured payload for non-prose blocks. Schemas by type:\n"
            "  metric        -> {value: '$42B', label: 'Market 2026', delta: '+18% YoY', trend: 'up|down|flat'}\n"
            "  metrics_grid  -> {metrics: [<metric>, ...]}\n"
            "  table         -> {caption: '...', headers: ['A', 'B'], rows: [['x','y'], ...]}\n"
            "  chart         -> {kind: 'bar|line|pie', title: '...', x_label: '', y_label: '',"
            " series: [{name: 'X', data: [{x: 'Q1', y: 12}, ...]}]}\n"
            "  comparison    -> {items: [{name: 'A', highlights: ['..'], verdict: '..'}, ...]}"
        ),
    )
    citations: list[str] = Field(default_factory=list, description="Source ids cited in this block.")


class Section(BaseModel):
    heading: str
    summary: str = ""
    blocks: list[Block]


class ResearchReport(BaseModel):
    """Final structured report. Renders to PDF via agent.renderer."""

    topic: str
    subtitle: str = ""
    audience: str = "general technical reader"
    executive_summary: str
    key_takeaways: list[str] = Field(default_factory=list)
    sections: list[Section]
    open_questions: list[str] = Field(default_factory=list)
    sources: list[Source]
    generated_at: str | None = None


class ReportBrief(BaseModel):
    """Captured user intent from the intake/discovery agent.

    Drives the rest of the pipeline (becomes state['brief']).
    """

    topic: str = Field(description="The subject the user wants researched.")
    audience: str = Field(
        default="general technical reader",
        description="Who reads this — e.g. 'CTO at a Series B fintech', 'undergrad CS student'.",
    )
    angle: str = Field(
        default="",
        description="Optional framing — e.g. 'compare to alternatives', 'focus on 2026 changes'.",
    )
    length: Literal["brief", "standard", "deep"] = Field(
        default="standard",
        description="brief ≈ 800w, standard ≈ 1500w, deep ≈ 3000w.",
    )
    tone: Literal["analytical", "narrative", "executive", "academic"] = "analytical"
    visuals: list[Literal["callouts", "pull_quotes", "code_blocks", "tables", "icons"]] = Field(
        default_factory=lambda: ["callouts", "pull_quotes"],
        description="Which visual block types the writer should favor.",
    )
    formats: list[Literal["pdf", "docx"]] = Field(
        default_factory=lambda: ["pdf", "docx"],
        description="Which output formats to render in parallel.",
    )
    citation_style: Literal["numbered", "inline_url"] = "numbered"
    upload_to_onedrive: bool = Field(
        default=False,
        description="If True, the on-demand /api/ms365-upload endpoint will push the docx to OneDrive after render.",
    )
    notes: str = Field(default="", description="Anything else the user mentioned.")
