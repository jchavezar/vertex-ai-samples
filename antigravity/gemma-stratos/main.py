# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "fastapi",
#   "uvicorn",
#   "httpx",
#   "google-auth",
#   "requests",
# ]
# ///
import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import google.auth
import google.auth.transport.requests

app = FastAPI()

# Add CORS middleware to allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/chat")
async def chat(request: Request):
    body = await request.json()
    messages = body.get("messages", [])
    
    # Get ADC token
    credentials, default_project = google.auth.default()
    auth_request = google.auth.transport.requests.Request()
    credentials.refresh(auth_request)
    token = credentials.token
    
    project_id = os.environ.get("PROJECT_ID", default_project)
    region = os.environ.get("REGION", "global")
    
    url = f"https://aiplatform.googleapis.com/v1/projects/{project_id}/locations/{region}/endpoints/openapi/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "google/gemma-4-26b-a4b-it-maas",
        "stream": True,
        "messages": messages
    }
    
    async def stream_response():
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", url, headers=headers, json=payload) as response:
                if response.status_code != 200:
                    error_detail = await response.aread()
                    yield f"data: {json.dumps({'error': f'HTTP {response.status_code}: {error_detail.decode()}'})}\n\n"
                    return
                async for chunk in response.aiter_bytes():
                    yield chunk

    return StreamingResponse(stream_response(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
