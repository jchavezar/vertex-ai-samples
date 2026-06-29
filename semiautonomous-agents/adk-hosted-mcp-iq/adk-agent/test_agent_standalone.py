import asyncio
import os
import sys
import json
import httpx
from pathlib import Path

# Load environment
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

async def run_test(query: str):
    backend_url = "http://localhost:8002"
    
    # 1. Verify Auth Status
    print("Checking auth status with backend...")
    async with httpx.AsyncClient() as client:
        try:
            status_resp = await client.get(f"{backend_url}/api/auth/status")
            if status_resp.status_code != 200:
                print(f"Error: Backend is not running or returned status {status_resp.status_code}")
                return
            
            auth_info = status_resp.json()
            if not auth_info.get("authenticated"):
                print("Error: Account is not authenticated. Please sign in via the browser UI first.")
                return
            
            print(f"Authenticated as: {auth_info['account']['username']}")
            print(f"Tenant ID: {auth_info['account']['tenant_id']}")
            
        except Exception as e:
            print(f"Failed to connect to backend at {backend_url}: {e}")
            return

        # 2. Call Chat Stream
        print(f"\nSending Query: '{query}'")
        payload = {"message": query}
        
        try:
            async with client.stream("POST", f"{backend_url}/api/chat", json=payload, timeout=60) as response:
                if response.status_code != 200:
                    print(f"Chat failed with status {response.status_code}")
                    return
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if not data_str:
                            continue
                        
                        try:
                            event = json.loads(data_str)
                            if event["type"] == "text":
                                print(event["content"], end="", flush=True)
                            elif event["type"] == "tool_start":
                                print(f"\n[Tool Invoke] Calling {event['name']} with args: {event['arguments']}")
                            elif event["type"] == "tool_end":
                                print(f"[Tool Response] Completed {event['name']}")
                            elif event["type"] == "error":
                                print(f"\n[Error] {event['message']}")
                        except Exception as json_e:
                            pass
            print("\n\nTest Stream Completed.")
        except Exception as e:
            print(f"\nFailed during streaming test: {e}")

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "Who is Jennifer Walsh?"
    asyncio.run(run_test(query))
