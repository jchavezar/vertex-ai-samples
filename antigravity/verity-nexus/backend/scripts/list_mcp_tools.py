
import asyncio
import json
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams

async def list_tools():
    toolset = MCPToolset(
        connection_params=SseConnectionParams(
            url="https://mcp-ledger-toolbox-oyntfgdwsq-uc.a.run.app/mcp/sse"
        )
    )
    
    tools = await toolset.get_tools()
    
    for tool in tools:
        print(f"Tool: {tool.name}")
        # Use the internal _mcp_tool if it exists or parameters
        if hasattr(tool, '_mcp_tool'):
            inner = tool._mcp_tool
            # Try some common property names
            schema = getattr(inner, 'inputSchema', getattr(inner, 'input_schema', None))
            if schema:
                print(f"Schema: {json.dumps(schema, indent=2)}")
        print("-" * 20)

if __name__ == "__main__":
    asyncio.run(list_tools())
