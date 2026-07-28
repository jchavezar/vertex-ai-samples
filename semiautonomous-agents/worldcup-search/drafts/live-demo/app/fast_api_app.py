# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import json
import httpx
import google.auth
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from google.adk.cli.fast_api import get_fast_api_app
from google.cloud import logging as google_cloud_logging

from app.app_utils.telemetry import setup_telemetry
from app.app_utils.typing import Feedback

setup_telemetry()
_, project_id = google.auth.default()
logging_client = google_cloud_logging.Client()
logger = logging_client.logger(__name__)
allow_origins = (
    os.getenv("ALLOW_ORIGINS", "").split(",") if os.getenv("ALLOW_ORIGINS") else None
)

# Artifact bucket for ADK (created by Terraform, passed via env var)
logs_bucket_name = os.environ.get("LOGS_BUCKET_NAME")

AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Deploy reasoning engine resource ID
deployed_engine_id = "projects/254356041555/locations/us-east1/reasoningEngines/4837393765377245184"

# Use agentengine:// schema to connect the local FastAPI session service directly to GCP Vertex Session Service
session_service_uri = f"agentengine://{deployed_engine_id}"

artifact_service_uri = f"gs://{logs_bucket_name}" if logs_bucket_name else None

app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    artifact_service_uri=artifact_service_uri,
    allow_origins=allow_origins,
    session_service_uri=session_service_uri,
    otel_to_cloud=True,
)
app.title = "worldcup-search"
app.description = "API for interacting with the Agent worldcup-search"

# Remove standard ADK root and run routes in-place to let our premium UI/custom router take precedence
for route in list(app.routes):
    if route.path in ("/", "/run"):
        app.routes.remove(route)


@app.get("/", response_class=HTMLResponse)
@app.get("/worldcup", response_class=HTMLResponse)
def get_worldcup_ui():
    """Serves the custom grounded chatbot user interface."""
    static_file_path = os.path.join(AGENT_DIR, "app", "static", "index.html")
    with open(static_file_path, "r", encoding="utf-8") as f:
        return f.read()


@app.post("/run")
async def run_query(request: Request):
    """Intercepts and forwards the user query directly to the deployed reasoning engine."""
    payload = await request.json()
    message_text = payload.get("newMessage", {}).get("parts", [{}])[0].get("text", "")
    user_id = payload.get("userId", "scout_fan")
    session_id = payload.get("sessionId")

    # Resolve deployed agent ID from metadata if possible, otherwise use fallback constant
    metadata_path = os.path.join(AGENT_DIR, "deployment_metadata.json")
    remote_agent_id = deployed_engine_id
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
                remote_agent_id = metadata.get("remote_agent_runtime_id") or deployed_engine_id
        except Exception:
            pass

    # Authenticate with Google Application Default Credentials
    credentials, project = google.auth.default()
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    token = credentials.token

    location = "us-east1"
    if "locations/" in remote_agent_id:
        location = remote_agent_id.split("locations/")[1].split("/")[0]

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    stream_url = f"https://{location}-aiplatform.googleapis.com/v1/{remote_agent_id}:streamQuery?alt=sse"
    stream_body = {
        "class_method": "async_stream_query",
        "input": {
            "message": message_text,
            "user_id": user_id,
        }
    }
    if session_id:
        stream_body["input"]["session_id"] = session_id

    events = []
    async with httpx.AsyncClient(timeout=180.0) as client:
        async with client.stream("POST", stream_url, headers=headers, json=stream_body) as response:
            if response.status_code != 200:
                err_text = await response.aread()
                return {"error": f"Remote reasoning engine returned status {response.status_code}: {err_text.decode('utf-8', errors='ignore')}"}

            async for line in response.aiter_lines():
                if not line.strip():
                    continue
                if line.startswith("data:"):
                    line = line[5:].strip()
                try:
                    event = json.loads(line)
                    events.append(event)
                except Exception:
                    pass

    return events




@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    """Collect and log feedback.

    Args:
        feedback: The feedback data to log

    Returns:
        Success message
    """
    logger.log_struct(feedback.model_dump(), severity="INFO")
    return {"status": "success"}


# Main execution
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

