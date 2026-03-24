import httpx
import asyncio
import json

async def test_backend_stream():
    url = "http://localhost:8008/api/chat/stream"
    
    payload = {
        "model": "gemini-3-flash-preview",
        "routerMode": "ge_mcp",
        "messages": [
            {"role": "user", "content": "What is the capital of France?"}
        ],
        "sessionId": "test-ge-mcp-123"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer fake_or_optional_token" # Might be needed if verify_jwt allows
    }
    
    print(f"Calling {url} with routerMode=ge_mcp...")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", url, headers=headers, json=payload) as response:
                print(f"Status Code: {response.status_code}")
                async for chunk in response.aiter_bytes():
                     if chunk:
                         print(chunk.decode('utf-8'), end="")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_backend_stream())
