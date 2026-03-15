import asyncio
from google.adk.tools import mcp_tool
import os

async def main():
    env = {"PYTHONPATH": ".", "PATH": os.environ.get("PATH", ""), "FASTMCP_SHOW_SERVER_BANNER": "false"}
    params = mcp_tool.StdioConnectionParams(
        server_params={
            "command": "python",
            "args": ["-m", "mcp_service.mcp_server_actions"],
            "env": env
        }
    )
    toolset = mcp_tool.McpToolset(connection_params=params)
    print("Trying to get tools...")
    try:
        tools = await toolset.get_tools()
        print(f"Success! Got {len(tools)} tools: {[t.name for t in tools]}")
    except Exception as e:
        print(f"Failed. Error: {e}")
    finally:
        await toolset.close()

if __name__ == "__main__":
    asyncio.run(main())
