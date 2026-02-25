import os
import vertexai
from agent_pkg.agent import interceptor_app

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
# Try to fall back to a known bucket or rely on Vertex AI defaults if possible
STAGING_BUCKET = os.environ.get("STAGING_BUCKET", f"gs://{PROJECT_ID}-agent-staging")
AGENT_ENGINE_DISPLAY_NAME = "GE Payload Interceptor"

print(f"Initializing Vertex AI for project {PROJECT_ID} in {LOCATION}")
vertexai.init(project=PROJECT_ID, location=LOCATION)
from vertexai.preview import reasoning_engines
import json
import time
import uuid
from typing import Iterator, AsyncIterator

class GEMINIPayloadInterceptor:
    """
    A pure Python class designed to intercept the raw request_json 
    from Gemini Enterprise (AgentSpace) and yield it back formatted so the UI can see it.
    """
    def __init__(self):
        self.name = "intercepting_agent"

    def set_up(self):
        pass
        
    def register_operations(self):
        return {
            "": ["query", "streaming_agent_run_with_events"],
            "stream": ["stream_query"]
        }
        
    def query(self, message: str) -> str:
        return f"Echo: {message}"
        
    def stream_query(self, message: str) -> Iterator[str]:
        yield "Not implemented directly - use streaming_agent_run_with_events"
        
    def streaming_agent_run_with_events(self, request_json: str) -> dict:
        """
        Intercepts the specific Gemini Enterprise method invocation.
        Instead of calling the LLM immediately, we return a single raw payload.
        """
        try:
            # Pretty-print for better UI wrapping
            import json
            payload_obj = json.loads(request_json)
            formatted_json = json.dumps(payload_obj, indent=2)
        except Exception:
            formatted_json = request_json

        raw_debug_event = {
             "content": {
                  "role": "model",
                  "parts": [
                       {
                            "text": f"### 🕵️ Gemini Enterprise Interceptor payload captured!\n\n**Raw `request_json`**:\n```json\n{formatted_json}\n```"
                       }
                  ]
             },
             "grounding_metadata": {},
             "error_code": "",
             "error_message": "",
             "invocation_id": "interceptor-auth",
             "author": "interceptor",
             "id": str(uuid.uuid4()),
             "timestamp": time.time()
        }
        
        return raw_debug_event

print("Starting Agent Engine deployment...")
print("This may take a few minutes as Google Cloud provisions the container.")

vertexai.init(
    project=os.getenv("PROJECT_ID"),
    location=os.getenv("LOCATION", "us-central1"),
    staging_bucket="gs://adk_staging_bucket_vtxdemos"
)

interceptor_app = GEMINIPayloadInterceptor()

try:
    remote_agent = reasoning_engines.ReasoningEngine.create(
        interceptor_app,
        requirements=[
            "google-adk",
            "google-cloud-aiplatform[adk,agent_engines]",
            "cloudpickle",
        ],
        display_name="GEMINIPayloadInterceptor"
    )

    print(f"Deployment successful!")
    print(f"Agent Engine ID: {remote_agent.resource_name}")
except Exception as e:
    print(f"Deployment failed: {e}")
