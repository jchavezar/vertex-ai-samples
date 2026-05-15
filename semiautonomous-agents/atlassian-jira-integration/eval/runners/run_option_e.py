"""Option E runner — GenAI SDK + custom MCP (in-process).

Replaces ADK with GenAI SDK to isolate ADK/Agent Engine latency.
Calls genai_agent.answer_question() in-process (not over HTTP).
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

# Add option-e to path
_HERE = Path(__file__).resolve().parent.parent
_OPTION_E = _HERE.parent / "option-e-langchain-custom-mcp"
sys.path.insert(0, str(_OPTION_E))

from genai_agent import answer_question

from . import _common as C


async def run_one(question: dict[str, Any], client: Any, raw_dir: Path) -> C.RunnerResult:
    """Run one question through ADK in-process agent."""
    qid = question["id"]
    raw_path = raw_dir / f"{qid}_e.json"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    try:
        # Import the async function directly
        from genai_agent import _answer_question_async
        result = await _answer_question_async(question["q"])
        elapsed = time.perf_counter() - t0
        # Save raw result
        raw_path.write_text(json.dumps(result, indent=2, default=str))
        if "error" in result and result["error"]:
            return C.RunnerResult(
                id=qid,
                pipeline="e",
                ok=False,
                answer="",
                elapsed_s=elapsed,
                error=result["error"],
                raw_path=str(raw_path),
            )
        answer = result.get("answer", "")
        tool_calls = result.get("tool_calls", [])
        return C.RunnerResult(
            id=qid,
            pipeline="e",
            ok=True,
            answer=answer,
            tool_calls=tool_calls,
            citations=C.cited_keys(answer),
            elapsed_s=elapsed,
            raw_path=str(raw_path),
        )
    except Exception as exc:
        return C.RunnerResult(
            id=qid,
            pipeline="e",
            ok=False,
            answer="",
            elapsed_s=time.perf_counter() - t0,
            error=f"{type(exc).__name__}: {exc}",
            raw_path=str(raw_path),
        )
