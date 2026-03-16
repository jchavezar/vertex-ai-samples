import asyncio
import os
import sys
# Add current dir to path
sys.path.append(os.getcwd())

from agents.agent import get_agent_with_mcp_tools
from google.adk.tools import mcp_tool

async def test():
    print("Testing ADK + MCP Initialization...")
    try:
        # Check if McpToolset exists
        print(f"McpToolset exists in mcp_tool: {hasattr(mcp_tool, 'McpToolset')}")
        
        agent, stack = await get_agent_with_mcp_tools()
        print(f"Success! Discovered tools: {[t.name for t in agent.tools]}")
        await stack.aclose()
    except Exception as e:
        print(f"Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
