import asyncio
import json
import google.auth
import google.auth.transport.requests
import httpx

ENGINE_RESOURCE = "projects/254356041555/locations/us-central1/reasoningEngines/4299946434406383616"

async def main():
    credentials, project = google.auth.default()
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    token = credentials.token

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Step 1: Query the agent with a prompt requiring google search
    stream_url = f"https://us-central1-aiplatform.googleapis.com/v1/{ENGINE_RESOURCE}:streamQuery?alt=sse"
    stream_body = {
        "class_method": "async_stream_query",
        "input": {
            "message": "Search the web for the latest news on Gemini 3.5 and Gemini 3.0. What are the key announcements?",
            "user_id": "test-user-123"
        }
    }

    print("Sending search query to agent...")
    async with httpx.AsyncClient(timeout=180.0) as client:
        async with client.stream("POST", stream_url, headers=headers, json=stream_body) as response:
            if response.status_code != 200:
                print(f"Error status: {response.status_code}")
                print(await response.aread())
                return
            
            async for line in response.aiter_lines():
                if not line.strip():
                    continue
                if line.startswith("data:"):
                    line = line[5:].strip()
                try:
                    event = json.loads(line)
                    content = event.get("content", {})
                    for part in content.get("parts", []):
                        if "text" in part:
                            print(part["text"], end="", flush=True)
                except Exception as e:
                    pass
    print()

if __name__ == "__main__":
    asyncio.run(main())
