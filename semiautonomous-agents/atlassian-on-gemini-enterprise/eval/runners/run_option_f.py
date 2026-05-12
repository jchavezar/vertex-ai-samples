"""
Runner for Option F: In-Process ADK (identical to Option E but labeled F)
"""
import sys
import os
from pathlib import Path

# Add option-f to path
option_f_path = Path(__file__).parent.parent.parent / "option-f-langchain-custom-mcp"
sys.path.insert(0, str(option_f_path))

from langchain_agent import _answer_question_async
from runners import _common as C


async def run_one(q: dict, client, raw_dir: Path) -> C.RunnerResult:
    """
    Run a single question through Option F (in-process ADK).
    """
    question_text = q.get("q") or q.get("question")
    result = await _answer_question_async(question_text)
    return C.RunnerResult(
        id=q["id"],
        pipeline="f",
        ok=result["ok"],
        answer=result.get("answer", ""),
        elapsed_s=result["elapsed_s"],
        error=result.get("error"),
    )


if __name__ == "__main__":
    # Smoke test
    import asyncio
    q = {"id": 0, "question": "How many issues are in project SMP?"}
    result = asyncio.run(run_one(q, None, Path(".")))
    print(f"\nAnswer: {result.answer[:200]}")
    print(f"Elapsed: {result.elapsed_s}s")
    print(f"OK: {result.ok}")
