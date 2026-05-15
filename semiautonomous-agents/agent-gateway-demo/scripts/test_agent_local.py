"""Local end-to-end test using InMemoryRunner and a stubbed MCP via header_provider.

The agent runs in-process, McpToolset connects to whatever MCP_SERVER_URL is set
(point it at a locally-running mcp_server on http://localhost:8080/mcp). We
seed the session state with a fake token so the header_provider has something
to forward.

    cd agent-gateway-demo/agent
    uv venv && uv sync
    # in another shell, run the MCP server locally:
    cd ../mcp_server && uv run uvicorn main:app --port 8080
    # then:
    cd ../scripts
    uv run python test_agent_local.py "find documents about agent gateway"
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "agent"))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env")

# Force the runtime model location to global (gemini-2.5-flash is OK on either,
# but most VMs pin GOOGLE_CLOUD_LOCATION to us-central1 which is fine).
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "1")
os.environ.setdefault("MCP_SERVER_URL", "http://localhost:8080/mcp")
os.environ.setdefault("USE_AGENT_IDENTITY", "0")

from google.adk.runners import InMemoryRunner  # noqa: E402
from google.genai import types  # noqa: E402

from agent import root_agent  # noqa: E402

FAKE_TOKEN = (
    "eyJhbGciOiJub25lIn0."
    "eyJzdWIiOiJ0ZXN0LXVzZXJAdmlybnZla28udGVzdCIsIm5hbWUiOiJUZXN0IFVzZXIifQ."
)
SESSION_TOKEN_KEY = os.environ.get("SESSION_TOKEN_KEY", "temp:sharepoint_3lo")


async def run(prompt: str) -> None:
    runner = InMemoryRunner(agent=root_agent, app_name="agent-gateway-demo-local")
    session = await runner.session_service.create_session(
        app_name="agent-gateway-demo-local",
        user_id="local_tester",
        state={SESSION_TOKEN_KEY: FAKE_TOKEN},
    )

    user_msg = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
    print(f"[local] prompt: {prompt}\n")

    async for event in runner.run_async(
        user_id="local_tester", session_id=session.id, new_message=user_msg
    ):
        author = getattr(event, "author", None) or "?"
        for p in (event.content.parts if event.content else []) or []:
            if getattr(p, "text", None):
                print(p.text, end="", flush=True)
            fc = getattr(p, "function_call", None)
            if fc:
                print(f"\n[{author}] function_call: {fc.name}({dict(fc.args or {})})")
            fr = getattr(p, "function_response", None)
            if fr:
                resp_keys = list((fr.response or {}).keys()) if isinstance(fr.response, dict) else []
                print(f"\n[{author}] function_response: {fr.name} -> {resp_keys}")
    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python scripts/test_agent_local.py "<prompt>"')
        sys.exit(1)
    asyncio.run(run(sys.argv[1]))
