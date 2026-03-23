import asyncio
import os
from dotenv import load_dotenv
from google.adk.tools import mcp_tool
from contextlib import AsyncExitStack

# Load env from parent directory
load_dotenv(dotenv_path="../.env")

async def test_mcp_connectivity(name, url):
    print(f"\n--- Testing {name} MCP at {url} ---")
    if not url:
        print(f"Skipping {name}: URL not set.")
        return

    exit_stack = AsyncExitStack()
    params = mcp_tool.SseConnectionParams(url=url)
    toolset = mcp_tool.McpToolset(connection_params=params)
    await exit_stack.enter_async_context(exit_stack) # Dummy for stack lifecycle
    exit_stack.push_async_callback(toolset.close)
    
    try:
        print(f"Connecting to {url}...")
        tools = await toolset.get_tools()
        print(f"Successfully retrieved {len(tools)} tools from {name} MCP.")
        for tool in tools[:5]:
            print(f" - {tool.name}")
        if len(tools) > 5:
            print(f" ... and {len(tools)-5} more.")
    except Exception as e:
        print(f"FAILED to connect to {name} MCP: {str(e)}")
    finally:
        await exit_stack.aclose()

async def main():
    sn_url = os.environ.get("SERVICENOW_MCP_URL")
    sp_url = os.environ.get("SHAREPOINT_MCP_URL")
    
    await test_mcp_connectivity("ServiceNow", sn_url)
    await test_mcp_connectivity("SharePoint", sp_url)

if __name__ == "__main__":
    asyncio.run(main())
