"""
SecretOps Agent — Google ADK + ServiceNow MCP + Secret Manager.

Credentials are loaded from Google Secret Manager at runtime,
injected into a ServiceNow MCP server, and exposed as agent tools.
Google Search is available via ADK's built-in google_search tool
wrapped as an AgentTool.
"""
import os
import json
import shutil
import asyncio
import subprocess
from contextlib import AsyncExitStack

from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.mcp_tool import McpToolset, SseConnectionParams
from google.cloud import secretmanager

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "vtxdemos")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")

PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]
SECRET_ID = os.environ.get("SERVICENOW_SECRET_ID", "servicenow-credentials")
MCP_PORT = int(os.environ.get("MCP_PORT", "9090"))

MODEL = "gemini-2.5-flash"

INSTRUCTION = """\
You are SecretOps, an IT operations assistant.

Capabilities (use your tools accordingly):
- Search the web for real-time information using the google_search_agent tool.
- Create, search, list, and update ServiceNow incidents via MCP tools.
- Add work notes to existing incidents.

Workflow for new incidents:
1. If the user asks to find information online, use google_search_agent first.
2. Search existing incidents for duplicates.
3. Create the incident with a detailed description.
4. Report the incident number and summary.

Always confirm before creating or updating incidents.\
"""

google_search_agent = LlmAgent(
    name="google_search_agent",
    model=MODEL,
    description="Searches the internet for real-time information using Google Search.",
    instruction="Search the web and return detailed, factual results with sources.",
    tools=[google_search],
)


def _load_credentials():
    """Pull ServiceNow credentials from Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{SECRET_ID}/versions/latest"
    payload = client.access_secret_version(request={"name": name}).payload.data
    return json.loads(payload.decode("UTF-8"))


def _inject_credentials():
    """Load credentials into env vars for the MCP subprocess."""
    try:
        creds = _load_credentials()
        os.environ["SERVICENOW_INSTANCE_URL"] = creds["instance_url"]
        os.environ["SERVICENOW_BASIC_AUTH_USER"] = creds["username"]
        os.environ["SERVICENOW_BASIC_AUTH_PASS"] = creds["password"]
        print(f"[SecretOps] Credentials loaded from Secret Manager ({SECRET_ID})")
        print(f"[SecretOps] Instance: {creds['instance_url']}")
    except Exception as e:
        print(f"[SecretOps] Secret Manager unavailable ({e}), using env vars")


async def _start_mcp_server() -> subprocess.Popen:
    """Spawn the ServiceNow MCP server as a subprocess."""
    uv = shutil.which("uv") or "uv"
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    proc = subprocess.Popen(
        [uv, "run", "python", "-m", "servicenow_mcp.server"],
        env={**os.environ, "PORT": str(MCP_PORT), "FASTMCP_SHOW_SERVER_BANNER": "false"},
        cwd=root,
    )
    await asyncio.sleep(2)
    print(f"[SecretOps] MCP server on port {MCP_PORT} (pid={proc.pid})")
    return proc


async def create_agent() -> tuple[InMemoryRunner, AsyncExitStack, subprocess.Popen]:
    """Build the ADK agent with ServiceNow MCP tools and Google Search."""
    _inject_credentials()

    mcp_process = await _start_mcp_server()

    exit_stack = AsyncExitStack()
    toolset = McpToolset(
        connection_params=SseConnectionParams(url=f"http://localhost:{MCP_PORT}/sse")
    )
    exit_stack.push_async_callback(toolset.close)
    mcp_tools = await toolset.get_tools()
    print(f"[SecretOps] MCP tools: {[t.name for t in mcp_tools]}")

    agent = LlmAgent(
        name="SecretOpsAgent",
        model=MODEL,
        instruction=INSTRUCTION,
        tools=[AgentTool(agent=google_search_agent)] + mcp_tools,
    )

    runner = InMemoryRunner(agent=agent, app_name="secretops")
    return runner, exit_stack, mcp_process
