"""
Google ADK (Agent Development Kit) & Google Workspace Remote MCP Example

This script demonstrates:
1. Configuring Google Workspace remote MCP servers (Gmail, Drive, Docs, Calendar)
   using ADK's `McpToolset` with `StreamableHTTPConnectionParams`.
2. Inspecting the live handshake and tool definitions exposed by the Workspace MCP endpoint.
3. Running an ADK Agent with `InMemoryRunner` and `gemini-3.7-flash`.
"""

import asyncio
import os
import sys
import google.auth
from google.auth.transport.requests import Request
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.genai import types
import httpx

# Configure Vertex AI environment for ADK
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"


def get_workspace_mcp_config():
    """
    Retrieves the remote MCP server configuration as documented in:
    https://developers.google.com/workspace/guides/configure-mcp-servers#others
    """
    creds, project_id = google.auth.default()
    if not creds.valid:
        creds.refresh(Request())

    # Google Workspace Remote MCP Endpoints
    workspace_endpoints = {
        "gmail": "https://gmailmcp.googleapis.com/mcp/v1",
        "drive": "https://drivemcp.googleapis.com/mcp/v1",
        "docs": "https://docsmcp.googleapis.com/mcp/v1",
        "sheets": "https://sheetsmcp.googleapis.com/mcp/v1",
        "slides": "https://slidesmcp.googleapis.com/mcp/v1",
        "calendar": "https://calendarmcp.googleapis.com/mcp/v1",
        "chat": "https://chatmcp.googleapis.com/mcp/v1",
        "people": "https://people.googleapis.com/mcp/v1",
    }

    # Common Streamable HTTP Headers required by Google's MCP Gateway
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "x-goog-user-project": project_id or os.environ.get("GOOGLE_CLOUD_PROJECT", ""),
    }

    return workspace_endpoints, headers, creds, project_id


async def demonstrate_mcp_handshake(endpoint_url: str, headers: dict):
    """
    Performs the standard Model Context Protocol (MCP) JSON-RPC handshake
    against the Google Workspace remote MCP endpoint.
    """
    print(f"\n--- [1] Testing Remote Workspace MCP Handshake: {endpoint_url} ---")
    async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
        # Step 1: MCP initialize handshake
        init_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "google-adk-client", "version": "2.1.0"},
            },
        }
        res = await client.post(endpoint_url, json=init_payload)
        if res.status_code == 200:
            data = res.json()
            server_info = data.get("result", {}).get("serverInfo", {})
            protocol = data.get("result", {}).get("protocolVersion")
            print(f" Handshake succeeded!")
            print(f"  - Server Info: {server_info}")
            print(f"  - MCP Protocol Version: {protocol}")
        else:
            print(f"❌ Initialize failed with HTTP status: {res.status_code}")

        # Step 2: Query tools list
        list_payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        }
        res_tools = await client.post(endpoint_url, json=list_payload)
        # Note: If the OAuth token lacks user-level Workspace scopes, Google ESF
        # may return HTTP 403, but the tool schema is still validated by the gateway.
        tools_data = res_tools.json().get("result", {}).get("tools", [])
        if tools_data:
            print(f"\n Discovered {len(tools_data)} tools from {endpoint_url}:")
            for tool in tools_data[:6]:
                print(f"  * {tool.get('name')}: {tool.get('description', '').splitlines()[0]}")
        else:
            print(f"  Note: tools/list status {res_tools.status_code}. (Ensure OAuth scope is enabled)")


def create_adk_workspace_agent(endpoint_url: str, headers: dict):
    """
    Instantiates an ADK Agent equipped with McpToolset pointing to the Workspace MCP server.
    """
    print(f"\n--- [2] Configuring Google ADK Agent with McpToolset ---")
    
    # Configure McpToolset with StreamableHTTPConnectionParams
    workspace_toolset = McpToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=endpoint_url,
            headers=headers,
            timeout=30.0,
            sse_read_timeout=300.0,
        ),
        # Optional: restrict tools exposed to agent
        tool_filter=["create_draft", "get_thread", "search_threads"],
    )

    agent = Agent(
        name="workspace_assistant",
        model="gemini-3.7-flash",
        instruction=(
            "You are an executive assistant integrated with Google Workspace via MCP. "
            "You help the user manage communications, calendar, and documents."
        ),
        tools=[workspace_toolset],
    )
    print(f" Agent created: '{agent.name}' using model '{agent.model}'")
    print(f" Attached McpToolset endpoint: {endpoint_url}")
    return agent


async def run_adk_agent_simulation():
    """
    Executes a test query through ADK's InMemoryRunner to demonstrate agent execution.
    """
    print(f"\n--- [3] Executing Query through ADK InMemoryRunner ---")
    standalone_agent = Agent(
        name="adk_demo_agent",
        model="gemini-3.7-flash",
        instruction="You are a helpful AI assistant explaining ADK MCP integration. Be concise.",
    )

    runner = InMemoryRunner(agent=standalone_agent)
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="demo_user"
    )

    prompt = (
        "In 2 sentences, explain how Google ADK connects to remote Google Workspace MCP servers "
        "using StreamableHTTPConnectionParams."
    )
    print(f"Prompt: \"{prompt}\"\n")
    print("Agent Response: ", end="", flush=True)

    async for event in runner.run_async(
        session_id=session.id,
        user_id="demo_user",
        new_message=types.Content(parts=[types.Part.from_text(text=prompt)]),
    ):
        if event.content and event.content.parts:
            for p in event.content.parts:
                if p.text:
                    print(p.text, end="", flush=True)
    print("\n")


async def main():
    print("================================================================")
    print("  Google ADK + Google Workspace Remote MCP Configuration Demo   ")
    print("================================================================")
    
    endpoints, headers, creds, project = get_workspace_mcp_config()
    print(f"Active Google Cloud Project: {project or os.environ.get('GOOGLE_CLOUD_PROJECT')}")
    print(f"Target Gmail MCP Endpoint: {endpoints['gmail']}")

    # 1. Test MCP protocol handshake
    await demonstrate_mcp_handshake(endpoints["gmail"], headers)

    # 2. Scaffolding ADK Agent with McpToolset
    _ = create_adk_workspace_agent(endpoints["gmail"], headers)

    # 3. Execute ADK agent query
    await run_adk_agent_simulation()

    print("================================================================")
    print("  Demo Complete!                                               ")
    print("================================================================")


def safe_run(coro):
    """Runs an async coroutine safely in both standard CLI and Jupyter / Interactive loops."""
    import concurrent.futures
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # Running inside VS Code Interactive Window or Jupyter Kernel
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return pool.submit(asyncio.run, coro).result()
    else:
        return asyncio.run(coro)


if __name__ == "__main__":
    safe_run(main())

