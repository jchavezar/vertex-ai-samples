import asyncio
import os
import traceback
import logging
from dotenv import load_dotenv
from google.adk.tools import mcp_tool
from contextlib import AsyncExitStack

# Setup verbose logging to catch internal anyio/httpx-sse errors
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("mcp_debug")

# Load env from parent directory
load_dotenv(dotenv_path="../.env")

async def test_mcp_deep_debug(name, url):
    print(f"\n{'='*20} DEEP DEBUG: {name} {'='*20}")
    print(f"Target URL: {url}")
    
    if not url:
        print("Error: URL is None")
        return

    exit_stack = AsyncExitStack()
    try:
        # 1. Manual HTTP Check
        import httpx
        async with httpx.AsyncClient(timeout=10.0) as client:
            print("--- Step 1: Manual HTTP GET /sse ---")
            try:
                resp = await client.get(f"{url}/sse")
                print(f"Status: {resp.status_code}")
                print(f"Headers: {dict(resp.headers)}")
                # Read just the start to confirm it looks like SSE
                line = await resp.aread()
                print(f"Preview: {line.decode()[:100]}")
            except Exception as e:
                print(f"HTTP GET Failed: {e}")

        # 2. ADK SSE Discovery
        print("\n--- Step 2: ADK McpToolset Discovery ---")
        
        # Enable debug logging for the underlying mcp library
        logging.getLogger('mcp').setLevel(logging.DEBUG)
        
        params = mcp_tool.SseConnectionParams(url=url)
        toolset = mcp_tool.McpToolset(connection_params=params)
        
        # We manually manage the lifecycle since TaskGroups are sensitive
        try:
            # get_tools() handles the session internally
            tools = await asyncio.wait_for(toolset.get_tools(), timeout=15.0)
            print(f"SUCCESS! Found {len(tools)} tools.")
        except asyncio.TimeoutError:
            print("FAILED: Connection timed out after 15s")
        except Exception as e:
            print(f"ERROR during get_tools(): {type(e).__name__}: {e}")
            traceback.print_exc()
            
            # Check for ExceptionGroup/TaskGroup specifics
            if hasattr(e, "__exceptions__"):
                print("\nNested Exceptions:")
                for i, sub in enumerate(e.__exceptions__):
                    print(f"  [{i}] {type(sub).__name__}: {sub}")
                    traceback.print_exception(type(sub), sub, sub.__traceback__)

    except Exception as general_e:
        print(f"General script error: {general_e}")
        traceback.print_exc()
    finally:
        await exit_stack.aclose()
        await toolset.close()

async def main():
    sn_url = os.environ.get("SERVICENOW_MCP_URL")
    # Only test one to reduce noise
    await test_mcp_deep_debug("ServiceNow", sn_url)

if __name__ == "__main__":
    asyncio.run(main())
