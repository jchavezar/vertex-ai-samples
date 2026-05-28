"""
Eval runner for Option 1 (Custom MCP on Cloud Run).

PLAN (TODO):
  - Load questions.json.
  - For each question, hit the GE chat surface (the GE app that has
    Option 1's BYO_MCP datastore attached). Use streamAssist with the
    user's bearer token so per-question per-user ACLs apply.
  - Capture {question_id, response_text, tool_calls[], latency_ms,
    cost_estimate} per row. Write to responses_custom_mcp.jsonl.

NOTES:
  - The GE chat surface is the same one as in the atlassian-jira-integration
    eval runners — see eval/runners/run_a.py there for the streamAssist
    request shape.
  - Optionally also probe the MCP server directly via /mcp JSON-RPC to
    record raw tool-level latencies (used for the latency p50/p90 axis).
"""
from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

logger = logging.getLogger("eval.run_custom_mcp")

GE_APP_ID = os.environ.get("GE_APP_ID")
GE_LOCATION = os.environ.get("GE_LOCATION", "global")
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")


def run(questions_path: Path, out_path: Path) -> None:
    raise NotImplementedError(
        "TODO: implement streamAssist runner. See module docstring + "
        "../../atlassian-jira-integration/eval/runners/run_a.py for "
        "the request shape."
    )


def main(argv: list[str]) -> int:
    qpath = Path(argv[1]) if len(argv) > 1 else Path("questions/questions.json")
    out = Path(argv[2]) if len(argv) > 2 else Path("responses_custom_mcp.jsonl")
    try:
        run(qpath, out)
    except NotImplementedError as e:
        logger.warning(str(e))
        return 2
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    sys.exit(main(sys.argv))
