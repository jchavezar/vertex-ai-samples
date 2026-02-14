import os
import time
import base64
import tempfile
import vertexai
from google import genai
from google.genai import types
from google.adk.tools import FunctionTool
from google.adk.agents import LlmAgent
from vertexai.agent_engines import AdkApp

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
STAGING_BUCKET = os.environ.get("STAGING_BUCKET", "gs://gcp-vertex-ai-generative-ai")
AGENT_ENGINE_DISPLAY_NAME = "Veo Video Agent"

print(f"Initializing Vertex AI for project {PROJECT_ID} in {LOCATION}")
vertexai.init(project=PROJECT_ID, location=LOCATION)
client = vertexai.Client(project=PROJECT_ID, location=LOCATION)

_client = None
def get_client():
    global _client
    if _client is None:
        p_id = os.getenv("PROJECT_ID", "vtxdemos")
        loc = os.getenv("LOCATION", "us-central1")
        _client = genai.Client(vertexai=True, project=p_id, location=loc)
    return _client

def _poll_and_return(operation):
    c = get_client()
    if not c: return "Error: GenAI client not initialized."
    while not operation.done:
        time.sleep(10)
        operation = c.operations.get(operation)
    if hasattr(operation, 'error') and operation.error:
        raise ValueError(f"Veo API returned an error: {operation.error}")
    response = operation.result
    if response and hasattr(response, 'generated_videos') and response.generated_videos:
        video = response.generated_videos[0]
        if hasattr(video, 'video') and hasattr(video.video, 'video_bytes'):
             video_bytes = video.video.video_bytes
             fd, temp_path = tempfile.mkstemp(suffix=".mp4", prefix="veo_out_")
             with os.fdopen(fd, "wb") as f:
                 f.write(video_bytes)
             return f"VIDEO_FILE_PATH_PAYLOAD:{temp_path}"
        else:
             raise ValueError(f"Video structure unexpected: {video}")
    else:
        raise ValueError("No videos generated.")

def generate_text_to_video(prompt: str, aspect_ratio: str = "16:9", duration_seconds: int = 4) -> str:
    """Generates a video from a text description using Veo."""
    try:
        source = types.GenerateVideosSource(prompt=prompt)
        config = types.GenerateVideosConfig(aspect_ratio=aspect_ratio, duration_seconds=duration_seconds, resolution="720p", person_generation="allow_all")
        op = get_client().models.generate_videos(model="veo-3.1-fast-generate-preview", source=source, config=config)
        return _poll_and_return(op)
    except Exception as e:
        return f"Error generating video: {str(e)}"

SYSTEM_PROMPT = """You are a helpful and creative Video Generation Expert using Google's Veo api...
When asked to create a video from text, ALWAYS use the `generate_text_to_video` tool.
IMPORTANT Rules:
- Only generate 4, 6, or 8 second videos. Default to 4 seconds.
- Do not repeat base64 payloads to the user.
"""

all_tools = [FunctionTool(generate_text_to_video)]

video_expert_agent = LlmAgent(
    id="video_expert_agent",
    model="gemini-3-pro-preview",
    system_instruction=SYSTEM_PROMPT,
    tools=all_tools
)

deployment_app = AdkApp(agent=video_expert_agent, enable_tracing=False)

requirements_list = [
    "google-cloud-aiplatform[adk,agent_engines]",
    "google-adk",
    "google-genai",
    "python-dotenv",
    "requests", "pillow", "cloudpickle", "pydantic"
]

print("Starting deployment to Agent Engine...")
try:
    remote_app = client.agent_engines.create(
        agent=deployment_app,
        config={
            "display_name": AGENT_ENGINE_DISPLAY_NAME,
            "staging_bucket": STAGING_BUCKET,
            "requirements": requirements_list,
            "env_vars": {"ENABLE_TELEMETRY": "False"}
        }
    )
    print("Deployment successful!")
    print(remote_app.api_resource.name)
except Exception as e:
    print(f"Deployment failed: {e}")
