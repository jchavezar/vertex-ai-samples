"""Callbacks that wire the multi-agent pipeline together.

`escalation_checker` breaks the research LoopAgent when the critic is happy.
`citation_replacement_callback` rewrites <cite source="src-N"/> tags into
numbered footnote markers and registers the sources used.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any

from google.adk.agents.callback_context import CallbackContext
from google.adk.events import Event, EventActions
from google.genai.types import Content, Part

from .schemas import ResearchReport

_CITE_RE = re.compile(r'<cite\s+source="(src-\d+)"\s*/?>', re.IGNORECASE)


def escalation_checker(callback_context: CallbackContext) -> Event | None:
    """End the research loop when the critic returns grade=='pass'."""
    critique_raw = callback_context.state.get("critique")
    if not critique_raw:
        return None

    grade = None
    if isinstance(critique_raw, dict):
        grade = critique_raw.get("grade")
    else:
        try:
            grade = json.loads(critique_raw).get("grade")
        except (TypeError, ValueError, json.JSONDecodeError):
            grade = None

    if grade == "pass":
        return Event(
            author=callback_context.agent_name,
            actions=EventActions(escalate=True),
            content=Content(parts=[Part(text="Research sufficient — escalating out of loop.")]),
        )
    return None


def _coerce_report(state_value: Any) -> ResearchReport | None:
    if state_value is None:
        return None
    if isinstance(state_value, ResearchReport):
        return state_value
    if isinstance(state_value, dict):
        return ResearchReport.model_validate(state_value)
    if isinstance(state_value, str):
        try:
            return ResearchReport.model_validate_json(state_value)
        except ValueError:
            return None
    return None


def citation_replacement_callback(callback_context: CallbackContext) -> Event | None:
    """Resolve <cite source="src-N"/> tags into [N] footnote markers.

    Runs after the Writer. Reads state['report'], rewrites every block's
    text, registers which sources were actually cited, and writes back to
    state['report'] (and a flat state['report_for_render']).
    """
    report = _coerce_report(callback_context.state.get("report"))
    if report is None:
        return None

    by_id = {s.id: s for s in report.sources}
    cited_ids: list[str] = []

    def _register(src_id: str) -> int:
        if src_id not in cited_ids:
            cited_ids.append(src_id)
        return cited_ids.index(src_id) + 1

    def _rewrite(text: str) -> tuple[str, list[str]]:
        block_cites: list[str] = []

        def _sub(m: re.Match[str]) -> str:
            src_id = m.group(1)
            if src_id not in by_id:
                return ""  # unknown id — strip silently
            block_cites.append(src_id)
            return f"[{_register(src_id)}]"

        return _CITE_RE.sub(_sub, text), block_cites

    for section in report.sections:
        for block in section.blocks:
            block.text, ids = _rewrite(block.text)
            block.citations = list(dict.fromkeys(block.citations + ids))

    # Reorder sources to match citation order; append uncited at the end.
    ordered = [by_id[i] for i in cited_ids]
    uncited = [s for s in report.sources if s.id not in set(cited_ids)]
    report.sources = ordered + uncited
    report.generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    callback_context.state["report"] = report.model_dump(mode="json")
    callback_context.state["report_for_render"] = report.model_dump(mode="json")
    return None
