import google.auth
import google.auth.transport.requests
import httpx
import os
import asyncio
import json

async def test():
    credentials, project = google.auth.default()
    auth_request = google.auth.transport.requests.Request()
    credentials.refresh(auth_request)
    token = credentials.token

    ENGINE_ID = "projects/254356041555/locations/us-central1/reasoningEngines/3149353695427166208"
    url = f"https://us-central1-aiplatform.googleapis.com/v1beta1/{ENGINE_ID}:streamQuery?alt=sse"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "class_method": "async_stream_query",
        "input": {
            "message": "What is the temperature in Seattle? Respond STRICTLY with SEARCH.",
            "user_id": "test_user_123"
        }
    }

    print(f"Sending async httpx stream to {url}...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        async with client.stream("POST", url, headers=headers, json=payload) as response:
            print(f"HTTP Status: {response.status_code}")
            async for chunk in response.aiter_bytes():
                if chunk:
                    print("Chunk:", chunk.decode('utf-8'))

asyncio.run(test())
