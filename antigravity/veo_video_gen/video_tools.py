
import os
import time
import base64
from typing import Optional, List
from google.adk.tools import FunctionTool
from google import genai
from google.genai import types

# Initialize Client
PROJECT_ID = os.getenv("PROJECT_ID", "vtxdemos")
LOCATION = os.getenv("LOCATION", "us-central1")

try:
    client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION,
    )
except:
    client = None

def _poll_and_return(operation):
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
             video_base64 = base64.b64encode(video_bytes).decode("utf-8")
             import tempfile
             fd, temp_path = tempfile.mkstemp(suffix=".txt")
             with os.fdopen(fd, "w") as f:
                 f.write(video_base64)
             # Return file path marker for UI, keeps LLM context tiny
             print(f"Saved video payload to {temp_path}")
             return f"VIDEO_BASE64_FILE:{temp_path}"
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
        op = client.models.generate_videos(
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
        op = client.models.generate_videos(
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
        op = client.models.generate_videos(
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
    duration_seconds: int = 5
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
        op = client.models.generate_videos(
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
