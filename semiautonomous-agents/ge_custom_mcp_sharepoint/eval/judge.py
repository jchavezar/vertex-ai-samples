"""
Judge for the SharePoint × GE comparative eval.

SCOPE OF THIS FILE: skeleton only.

TODO: port judge_v6 from
  ../../atlassian-jira-integration/eval/judge_v6.py

That judge does:
  - Tiered rubric (T1 lookup / T2 reasoning / T3 synthesis).
  - Primary model: gemini-3-flash-preview on Vertex AI global region.
  - Escalation: Haiku 4.5 re-judges low-confidence T1 verdicts.
  - 10-dimension scoring:
      correctness, completeness, citation accuracy, hallucination,
      <option-specific>, pagination completeness, refusal correctness,
      tool efficiency, latency, cost
  - Verdicts: correct | partial | wrong | hallucinated | refused | error.
  - Refusal-credited on safety categories (refusal, prompt-injection,
    permission-aware).

The port should:
  - Replace `JQL correctness` axis with `Graph query correctness` (does
    the model actually call the right MCP tool for the question type?).
  - Add `markdown fidelity` axis specifically for the `file-read` and
    `multi-file-synthesis` categories where option 2's lack of markdown
    conversion may produce different outputs than option 1.
  - Carry a `tool_calls` trace per response so the judge can score
    tool-efficiency without re-running the question.

Inputs: questions.json + responses_<option>.jsonl (one per option).
Output: judged_<option>.json per option + a combined summary.
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

logger = logging.getLogger("eval.judge")


def judge(questions_path: Path, *response_paths: Path) -> dict:
    raise NotImplementedError(
        "TODO: port judge_v6.py from atlassian-jira-integration/eval/. "
        "See module docstring for the porting plan."
    )


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print("usage: judge.py questions.json responses_a.jsonl [responses_b.jsonl ...]", file=sys.stderr)
        return 2
    try:
        judge(Path(argv[1]), *[Path(p) for p in argv[2:]])
    except NotImplementedError as e:
        logger.warning(str(e))
        return 2
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    sys.exit(main(sys.argv))
