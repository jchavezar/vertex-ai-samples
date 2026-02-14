import os
import vertexai
from vertexai.agent_engines import AdkApp


import os
import time
import base64
from typing import Optional, List
from google.adk.tools import FunctionTool
from google import genai
from google.genai import types

_client = None

def get_client():
    global _client
    if _client is None:
        PROJECT_ID = os.getenv("PROJECT_ID", "vtxdemos")
        LOCATION = os.getenv("LOCATION", "us-central1")
        print(f"Initializing GenAI Client for {PROJECT_ID} in {LOCATION}")
        _client = genai.Client(
            vertexai=True,
            project=PROJECT_ID,
            location=LOCATION,
        )
    return _client

def _poll_and_return(operation):
    client = get_client()
    if not client: return "Error: GenAI client not initialized."
    
    while not operation.done:
        print("Video generating... waiting 10s")
        time.sleep(10)
        # Refresh operation state
        operation = client.operations.get(operation)

    if hasattr(operation, 'error') and operation.error:
        error_msg = f"Veo API returned an error: {operation.error}"
        print(error_msg)
        raise ValueError(error_msg)

    response = operation.result
    if response and hasattr(response, 'generated_videos') and response.generated_videos:
        video = response.generated_videos[0]
        # Log the structure for debugging
        print(f"Video generated: {type(video)}")
        if hasattr(video, 'video') and hasattr(video.video, 'video_bytes'):
             video_bytes = video.video.video_bytes
             
             # Save to temporary file to keep model history clean (avoid token bloat)
             import tempfile
             fd, temp_path = tempfile.mkstemp(suffix=".mp4", prefix="veo_out_")
             with os.fdopen(fd, "wb") as f:
                 f.write(video_bytes)
             
             print(f"Saved generated video to {temp_path}")
             # Return file path marker for main.py to handle
             return f"VIDEO_FILE_PATH_PAYLOAD:{temp_path}"
        else:
             print(f"Video structure missing bytes: {video}")
             raise ValueError(f"Video structure unexpected: {video}")
    else:
        print(f"Operation result: {response}")
        raise ValueError("No videos generated.")

def generate_text_to_video(
    prompt: str,
    aspect_ratio: str = "16:9",
    duration_seconds: int = 4
) -> str:
    """
    Generates a video from a text description using Veo.
    
    Args:
        prompt: Detailed description of the video scene.
        aspect_ratio: Aspect ratio (e.g. "16:9", "9:16").
        duration_seconds: Duration in seconds (4, 6, or 8).
    """
    print(f"Generating Video (Text-to-Video): {prompt}")
    try:
        source = types.GenerateVideosSource(prompt=prompt)
        config = types.GenerateVideosConfig(
            aspect_ratio=aspect_ratio,
            duration_seconds=duration_seconds,
            resolution="720p",
            person_generation="allow_all"
        )
        op = get_client().models.generate_videos(
            model="veo-3.1-fast-generate-preview",
            source=source,
            config=config
        )
        return _poll_and_return(op)
    except Exception as e:
        return f"Error generating video: {str(e)}"

def generate_image_to_video(
    image_base64: str,
    prompt: Optional[str] = None,
    duration_seconds: int = 4
) -> str:
    """
    Generates a video starting from an initial image (Image-to-Video).
    
    Args:
        image_base64: The base64 string of the image OR a local file path.
        prompt: Optional text prompt to guide the animation.
        duration_seconds: Duration in seconds.
    """
    print(f"Generating Video (Image-to-Video) with input length: {len(image_base64)}")
    try:
        img_bytes = None
        if os.path.exists(image_base64):
            print(f"Reading image from file: {image_base64}")
            with open(image_base64, "rb") as f:
                img_bytes = f.read()
        else:
            # Decode base64
            # Fix potential padding issues
            missing_padding = len(image_base64) % 4
            if missing_padding:
                image_base64 += '=' * (4 - missing_padding)
            img_bytes = base64.b64decode(image_base64)
        
        source = types.GenerateVideosSource(
            image=types.Image(image_bytes=img_bytes, mime_type="image/png"),
            prompt=prompt
        )
        config = types.GenerateVideosConfig(
            duration_seconds=duration_seconds,
            aspect_ratio="16:9",
            resolution="720p",
            person_generation="allow_all"
        )
        op = get_client().models.generate_videos(
            model="veo-3.1-fast-generate-preview",
            source=source,
            config=config
        )
        return _poll_and_return(op)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error animating image exception: {e}")
        return f"Error animating image: {str(e)}"

def generate_video_with_reference(
    prompt: str,
    reference_image_base64: str,
    reference_type: str = "style", # 'style' or 'subject' - checking API support
    duration_seconds: int = 4
) -> str:
    """
    Generates a video using a text prompt and a reference image for style or subject control.
    
    Args:
        prompt: The text prompt.
        reference_image_base64: The reference image (base64).
        reference_type: How to use the reference ('style' or 'subject' -- Verify API support, usually implied by model or config).
        duration_seconds: Duration.
    """
    print(f"Generating Video (Reference: {reference_type}): {prompt}")
    try:
        # Fix potential padding issues
        b64_ref = reference_image_base64
        missing_padding = len(b64_ref) % 4
        if missing_padding:
            b64_ref += '=' * (4 - missing_padding)
        img_bytes = base64.b64decode(b64_ref)
        
        source = types.GenerateVideosSource(prompt=prompt)
        config = types.GenerateVideosConfig(
            duration_seconds=duration_seconds,
            aspect_ratio="16:9",
            number_of_videos=1,
            resolution="720p",
            reference_images=[
                types.VideoGenerationReferenceImage(
                    image=types.Image(image_bytes=img_bytes, mime_type="image/png"),
                    reference_type=types.VideoGenerationReferenceType("asset")
                )
            ]
        )
        op = get_client().models.generate_videos(
            model="veo-3.1-fast-generate-preview",
            source=source,
            config=config
        )
        return _poll_and_return(op)
    except Exception as e:
        return f"Error generating with reference: {str(e)}"

def generate_video_from_video(
    video_base64: str,
    prompt: str,
    duration_seconds: int = 6
) -> str:
    """
    Generates a video from a video input (Video-to-Video / Editing).
    
    Args:
        video_base64: Base64 string of the input video.
        prompt: Text prompt to guide the generation/edit.
        duration_seconds: Duration in seconds.
    """
    print(f"Generating Video (Video-to-Video): {prompt}")
    try:
        vid_bytes = base64.b64decode(video_base64)
        source = types.GenerateVideosSource(
            video=types.Video(video_bytes=vid_bytes),
            prompt=prompt
        )
        config = types.GenerateVideosConfig(
            duration_seconds=duration_seconds,
            aspect_ratio="16:9",
            resolution="720p",
            person_generation="allow_all"
        )
        op = get_client().models.generate_videos(
            model="veo-3.1-fast-generate-preview",
            source=source,
            config=config
        )
        return _poll_and_return(op)
    except Exception as e:
        return f"Error processing video: {str(e)}"

# Create Tool Objects
text_to_video_tool = FunctionTool(generate_text_to_video)
image_to_video_tool = FunctionTool(generate_image_to_video)
reference_video_tool = FunctionTool(generate_video_with_reference)
video_to_video_tool = FunctionTool(generate_video_from_video)

all_tools = [text_to_video_tool, image_to_video_tool, reference_video_tool, video_to_video_tool]


import os
from dotenv import load_dotenv

# Load .env aggressively
dotenv_path = os.path.expanduser("~/.env")
if not os.path.exists(dotenv_path):
    dotenv_path = "../.env"
load_dotenv(dotenv_path=dotenv_path)

# Set env vars for ADK
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("PROJECT_ID", "vtxdemos")
os.environ["GOOGLE_CLOUD_LOCATION"] = os.getenv("LOCATION", "us-central1")

from typing import Optional, Dict, Any
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService


# Define the System Prompt
SYSTEM_PROMPT = """You are a Video Generation Expert Agent powered by Veo.
Your goal is to help users create amazing videos.

You have access to the following tools:
1. `generate_text_to_video(prompt, aspect_ratio, duration_seconds)`: Use this when the user handles a pure text request. 
   - Improve the user's prompt to be more descriptive, cinematic, and detailed before calling this tool.
   - Supported durations: 4, 6, 8 seconds. Default to 4.
   - Ask for aspect ratio (default 16:9) or duration if not specified.

2. `generate_image_to_video(image_base64, prompt, duration_seconds)`: Use this when the user provides an image and wants to animate it ("make this move", "animate this").
   - The user might provide an image as a base64 string or a file path.
   - Supported durations: 4, 6, 8 seconds.

3. `generate_video_with_reference(prompt, reference_image_base64, reference_type, duration_seconds)`: Use this when the user wants to generate a video *based on* a reference image (e.g., "use this style", "keep this character").
   - `reference_type` can be 'style' or 'subject'.

**Rules:**
- If the user asks about your capabilities, explain that you are a Video Expert and list your tools. Do NOT call any tools yet if they just ask for your capabilities.
- Always be helpful and enthusiastic.
- When a tool returns a video file path (starts with "VIDEO_FILE_PATH_PAYLOAD:"), strictly reply with: "Here is your generated video!" and nothing else, as the UI will render it. 
- If the tool returns an error, explain it to the user.
"""

# Create the Agent
video_expert_agent = LlmAgent(
    name="video_expert",
    model="gemini-2.5-flash", # User Mandated: Only 2.5 or 3.0 allowed
    instruction=SYSTEM_PROMPT,
    tools=[text_to_video_tool, image_to_video_tool, reference_video_tool]
)

# ==========================================
# DEPLOYMENT SCRIPT
# ==========================================
if __name__ == "__main__":
    PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
    LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    STAGING_BUCKET = os.environ.get("STAGING_BUCKET", "gs://gcp-vertex-ai-generative-ai")
    AGENT_ENGINE_DISPLAY_NAME = "Veo Video Agent"

    print(f"Initializing Vertex AI for project {PROJECT_ID} in {LOCATION}")
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    client = vertexai.Client(project=PROJECT_ID, location=LOCATION)

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
    except Exception as e:
        print(f"Deployment failed: {e}")
