"""
Eval runner for Option 2 (Microsoft-hosted Work IQ SharePoint MCP).

Same request shape as run_custom_mcp.py — the only difference is which
BYO_MCP datastore the GE app has attached. Use a separate GE app (or
toggle the connector) so both runs target the same conversation surface
but route to different MCP endpoints.

PLAN (TODO):
  - Identical to run_custom_mcp.py.
  - Additionally tag each tool call with the hosted tool name (e.g.
    `findFileOrFolder` vs the canonical `search`) so the judge can
    score the 5 MB ceiling and top-20 result-cap distortions when they
    cause a different verdict.
  - Output: responses_hosted_iq.jsonl
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

logger = logging.getLogger("eval.run_hosted_iq")


def run(questions_path: Path, out_path: Path) -> None:
    raise NotImplementedError(
        "TODO: implement streamAssist runner against the GE app that "
        "has the hosted Work IQ MCP attached. Mirror run_custom_mcp.py."
    )


def main(argv: list[str]) -> int:
    qpath = Path(argv[1]) if len(argv) > 1 else Path("questions/questions.json")
    out = Path(argv[2]) if len(argv) > 2 else Path("responses_hosted_iq.jsonl")
    try:
        run(qpath, out)
    except NotImplementedError as e:
        logger.warning(str(e))
        return 2
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    sys.exit(main(sys.argv))
