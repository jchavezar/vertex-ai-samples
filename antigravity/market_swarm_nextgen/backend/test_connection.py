
import os
import json
import httpx
import asyncio

TOKEN_FILE = "factset_tokens.json"
URL = "https://mcp.factset.com/content/v1/sse"

async def main():
    if not os.path.exists(TOKEN_FILE):
        print("No token file found.")
        return

    with open(TOKEN_FILE, 'r') as f:
        data = json.load(f).get("default_chat", {})
        token = data.get("token")
    
    if not token:
        print("No token found in file.")
        return
        
    print(f"Testing connection to {URL} with token: {token[:10]}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "text/event-stream"
    }
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(URL, headers=headers, timeout=10.0)
        print(f"Status: {resp.status_code}")
        print(f"Headers: {resp.headers}")
        print(f"Content Preview: {resp.text[:200]}")

if __name__ == "__main__":
    asyncio.run(main())
