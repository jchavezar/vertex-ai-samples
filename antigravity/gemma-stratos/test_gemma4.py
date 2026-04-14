# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "httpx",
#   "google-auth",
# ]
# ///
import os
import json
import asyncio
import httpx
import google.auth
import google.auth.transport.requests

async def test_gemma4():
    credentials, project = google.auth.default()
    auth_request = google.auth.transport.requests.Request()
    credentials.refresh(auth_request)
    token = credentials.token

    # Default values if not in env
    project_id = os.environ.get("PROJECT_ID", project)
    region = os.environ.get("REGION", "global")
    endpoint = os.environ.get("ENDPOINT", "aiplatform.googleapis.com")

    url = f"https://{endpoint}/v1/projects/{project_id}/locations/{region}/endpoints/openapi/chat/completions"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "google/gemma-4-26b-a4b-it-maas",
        "stream": True,
        "messages": [{"role": "user", "content": "Hello Gemma, tell me a short joke."}]
    }

    print(f"Sending request to {url}...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        async with client.stream("POST", url, headers=headers, json=payload) as response:
            print(f"HTTP Status: {response.status_code}")
            if response.status_code != 200:
                print(await response.aread())
                return
            async for chunk in response.aiter_bytes():
                if chunk:
                    print("Chunk:", chunk.decode('utf-8'))

if __name__ == "__main__":
    asyncio.run(test_gemma4())
