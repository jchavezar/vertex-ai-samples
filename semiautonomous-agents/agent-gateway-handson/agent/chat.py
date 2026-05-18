"""Run one prompt through the deployed reasoning engine and print the result.

Usage:
  export REASONING_ENGINE_NAME=projects/.../reasoningEngines/123...
  python3 chat.py "List the documents available"
"""

from __future__ import annotations

import os
import sys

from vertexai import agent_engines


def main() -> None:
    name = os.environ.get("REASONING_ENGINE_NAME")
    if not name:
        sys.exit("Set REASONING_ENGINE_NAME first (printed by deploy.py)")
    prompt = " ".join(sys.argv[1:]) or "List the documents available."

    remote = agent_engines.get(name)
    for event in remote.async_stream_query(message=prompt):
        # event shape varies by ADK version; print whatever looks like text.
        print(event)


if __name__ == "__main__":
    main()
