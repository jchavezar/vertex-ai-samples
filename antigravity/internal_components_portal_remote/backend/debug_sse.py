import asyncio
import aiohttp
import json

async def debug_sse(url):
    print(f"\n--- Debugging SSE: {url} ---")
    async with aiohttp.ClientSession() as session:
        try:
            sse_url = f"{url}/sse"
            print(f"Connecting to SSE: {sse_url}")
            async with session.get(sse_url) as resp:
                print(f"SSE Status: {resp.status}")
                if resp.status != 200:
                    print(f"Error Body: {await resp.text()}")
                    return
                
                # FastMCP SSE Transport:
                # 1. First event is 'endpoint' which gives the POST URL for messages
                
                line1 = await resp.content.readline()
                print(f"Read Line 1: {line1.decode().strip()}")
                
                line2 = await resp.content.readline()
                line2_str = line2.decode().strip()
                print(f"Read Line 2: {line2_str}")
                
                if not line2_str.startswith("data:"):
                    print("Unexpected format - missing 'data:' line")
                    return
                
                msg_path = line2_str.replace("data:", "").strip()
                print(f"Extracted Message Path: {msg_path}")
                
                # 2. POST to the message endpoint
                full_post_url = f"{url}{msg_path}"
                print(f"Posting to: {full_post_url}")
                
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "listTools"
                }
                
                async with session.post(full_post_url, json=payload) as post_resp:
                    print(f"POST Status: {post_resp.status}")
                    result = await post_resp.text()
                    print(f"POST Result: {result}")
                    
        except Exception as e:
            print(f"Connection Exception: {e}")

async def main():
    # Test both
    await debug_sse("https://servicenow-mcp-REDACTED_PROJECT_NUMBER.us-central1.run.app")
    await debug_sse("https://sharepoint-mcp-REDACTED_PROJECT_NUMBER.us-central1.run.app")

if __name__ == "__main__":
    asyncio.run(main())
