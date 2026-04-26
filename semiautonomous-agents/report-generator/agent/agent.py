"""Root pipeline for the report-generator agent.

Pattern:

    SequentialAgent
      ├── Planner             (LlmAgent, output_schema=ResearchPlan)
      ├── ParallelAgent (ResearchLanes)
      │     ├── ResearchLane0  (LlmAgent + google_search, free-text)
      │     ├── ResearchLane1  (LlmAgent + google_search, free-text)
      │     ├── ResearchLane2  (LlmAgent + google_search, free-text)
      │     └── ResearchLane3  (LlmAgent + google_search, free-text)
      ├── FindingsMerger      (LlmAgent, output_schema=ResearchFindings)
      ├── SectionPlanner      (LlmAgent → state['outline'])
      ├── Writer              (LlmAgent, output_schema=ResearchReport)
      ├── CitationReplacer    (no-op LlmAgent + after_agent_callback)
      └── ParallelAgent (Renderers)
            ├── PdfRenderer   (BaseAgent → WeasyPrint)
            └── DocxRenderer  (BaseAgent → python-docx)

Research is fanned out across 4 lanes (split by query index modulo 4),
each calling google_search in parallel. The FindingsMerger then
deduplicates sources by URL and emits a single typed ResearchFindings.
The old critic/loop has been dropped — it was the dominant latency
source on the prior pipeline and the parallel design produces enough
coverage on a single pass.
"""
from __future__ import annotations

import os

from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import google_search

from . import prompts
from .callbacks import citation_replacement_callback
from .docx_renderer import DocxRendererAgent
from .renderer import PdfRendererAgent
from .schemas import ResearchFindings, ResearchPlan, ResearchReport

# Per user memory: prefer Gemini 3 preview models in `global` region.
PLANNER_MODEL = os.environ.get("REPORT_PLANNER_MODEL", "gemini-3-flash-preview")
RESEARCH_MODEL = os.environ.get("REPORT_RESEARCH_MODEL", "gemini-3-flash-preview")
WRITER_MODEL = os.environ.get("REPORT_WRITER_MODEL", "gemini-3-flash-preview")
LANE_COUNT = int(os.environ.get("REPORT_RESEARCH_LANES", "4"))


planner = LlmAgent(
    name="Planner",
    model=PLANNER_MODEL,
    description="Decomposes the topic into a research plan.",
    instruction=prompts.PLANNER_INSTRUCTION,
    output_schema=ResearchPlan,
    output_key="plan",
)


# Build N parallel research lanes. Each lane handles a disjoint subset of
# `state['plan'].queries` (split by index % LANE_COUNT) and emits free-text
# findings into its own state key. Free-text because google_search cannot
# coexist with output_schema in a single LlmAgent.
def _make_research_lane(i: int, n: int) -> LlmAgent:
    return LlmAgent(
        name=f"ResearchLane{i}",
        model=RESEARCH_MODEL,
        description=f"Lane {i}/{n}: runs google_search on assigned plan queries.",
        instruction=prompts.research_lane_instruction(i, n),
        tools=[google_search],
        output_key=f"findings_lane_{i}_raw",
    )


research_lanes = ParallelAgent(
    name="ResearchLanes",
    description=f"Fan-out research across {LANE_COUNT} concurrent lanes.",
    sub_agents=[_make_research_lane(i, LANE_COUNT) for i in range(LANE_COUNT)],
)


findings_merger = LlmAgent(
    name="FindingsMerger",
    model=RESEARCH_MODEL,
    description="Merges per-lane free-text findings into a single ResearchFindings JSON.",
    instruction=prompts.FINDINGS_MERGER_INSTRUCTION,
    output_schema=ResearchFindings,
    output_key="findings",
)


section_planner = LlmAgent(
    name="SectionPlanner",
    model=WRITER_MODEL,
    description="Produces the final ordered section outline.",
    instruction=prompts.SECTION_PLANNER_INSTRUCTION,
    output_key="outline",
)


writer = LlmAgent(
    name="Writer",
    model=WRITER_MODEL,
    description="Drafts the polished, fully-cited report with charts, tables, and metrics.",
    instruction=prompts.WRITER_INSTRUCTION,
    output_schema=ResearchReport,
    output_key="report",
)


def _noop_instruction(_: CallbackContext) -> str:
    """Writer-pass-through; the real work happens in the after_agent_callback."""
    return "Pass through."


citation_replacer = LlmAgent(
    name="CitationReplacer",
    model=WRITER_MODEL,
    description="Rewrites <cite> tags into numbered footnotes; reorders sources.",
    instruction="Reply with 'ok'. Do not modify state directly — the callback handles it.",
    after_agent_callback=citation_replacement_callback,
)


pdf_renderer = PdfRendererAgent(
    name="PdfRenderer",
    description="Renders the final ResearchReport to a PDF using WeasyPrint.",
)


docx_renderer = DocxRendererAgent(
    name="DocxRenderer",
    description="Renders the final ResearchReport to a Microsoft Word .docx using python-docx.",
)


# Parallel rendering: PDF and DOCX run concurrently via ADK's ParallelAgent.
# Both consume the same `state['report_for_render']` and write distinct
# state keys (pdf_path / docx_path) — no contention, no added latency.
renderers = ParallelAgent(
    name="Renderers",
    description="Renders PDF and DOCX outputs in parallel.",
    sub_agents=[pdf_renderer, docx_renderer],
)


root_agent = SequentialAgent(
    name="ReportGenerator",
    description=(
        "Multi-stage report-generator: plans research, fans out Google "
        "Search across parallel lanes, drafts a fully-cited magazine-style "
        "report (with charts, tables, and metrics), and renders both PDF "
        "and Microsoft Word documents in parallel."
    ),
    sub_agents=[
        planner,
        research_lanes,
        findings_merger,
        section_planner,
        writer,
        citation_replacer,
        renderers,
    ],
)
