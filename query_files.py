import asyncio
import json
import google.auth
import google.auth.transport.requests
import httpx

ENGINE_RESOURCE = "projects/254356041555/locations/us-central1/reasoningEngines/4299946434406383616"
TUNNEL_URL = "https://94a5c7848d7e3c.lhr.life/sse"

async def main():
    credentials, project = google.auth.default()
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    token = credentials.token

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Step 1: Create a session with session state (MCP_URL)
    create_session_url = f"https://us-central1-aiplatform.googleapis.com/v1/{ENGINE_RESOURCE}:query"
    create_session_body = {
        "class_method": "async_create_session",
        "input": {
            "user_id": "test-user-123",
            "state": {
                "MCP_URL": TUNNEL_URL
            }
        }
    }

    print("Creating session with MCP_URL...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(create_session_url, headers=headers, json=create_session_body)
        if response.status_code != 200:
            print(f"Error creating session: {response.status_code}")
            print(response.text)
            return
        
        session_data = response.json()
        print("Session creation response:", json.dumps(session_data, indent=2))
        
        # Inside the returned object, we want to extract the session ID
        # Wait, the structure is usually inside a top-level "output" or similar key.
        # Let's inspect the response structure and extract it.
        # If it returns the serialized session, it should have a key "id".
        # Let's handle both possibilities.
        output = session_data.get("output", {})
        if isinstance(output, str):
            try:
                output = json.loads(output)
            except:
                pass
        
        session_id = None
        if isinstance(output, dict):
            session_id = output.get("id")
        if not session_id:
            session_id = session_data.get("id")
            
        if not session_id:
            print("Failed to find session ID in response.")
            return

        print(f"Successfully created session: {session_id}")

    # Step 2: Query the agent with the message in that session
    stream_url = f"https://us-central1-aiplatform.googleapis.com/v1/{ENGINE_RESOURCE}:streamQuery?alt=sse"
    stream_body = {
        "class_method": "async_stream_query",
        "input": {
            "message": "how many files do I have in my fileserver?",
            "user_id": "test-user-123",
            "session_id": session_id
        }
    }

    print(f"Sending stream query for session {session_id}...")
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
