import asyncio
from agents.agent import get_agent_with_mcp_tools

async def main():
    agent, exit_stack = await get_agent_with_mcp_tools(token="test")
    print("Agent initialized successfully without stdio corruption!")
    if exit_stack:
        await exit_stack.aclose()

if __name__ == "__main__":
    asyncio.run(main())
