---
name: pillar-2-veo-reels-studio
description: Step-by-step LLM replication skill to build and deploy Pillar 2 (Text-to-Reels Studio with Veo 3.1, Imagen 4.0, and Gemini Live 24kHz Audio) from scratch for Rocket Companies & Redfin.
---

# SKILL: Replicating Pillar 2 (`Veo 3.1` Text-to-Reels Studio) From Scratch

Any frontier coding assistant (**Claude Code, Gemini CLI, Cursor, Windsurf, Antigravity/Jetski**) can rebuild Pillar 2 from zero by executing the following 4 engineering steps:

## Step 1: Initialize the Vertex AI GenAI SDK Client

Use the official `google-genai` SDK (`google-genai >= 2.31.0`):

```python
import os
from google import genai
from google.genai import types

PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "vtxdemos")

# Global client for Gemini 3.8 Flash & Veo 3.1
client_global = genai.Client(vertexai=True, project=PROJECT_ID, location="global")

# Regional client for Imagen 4.0 & Gemini 3.8 Live API
client_us = genai.Client(vertexai=True, project=PROJECT_ID, location="us-central1")
```

## Step 2: Implement the Creative Director & Keyframe Engine

```python
def generate_reel_creative_plan(property_info: dict) -> dict:
    """Uses gemini-3.8-flash to create structured storyboard timings, captions, and script."""
    prompt = f"""
    You are an elite real estate creative director creating a viral vertical 9:16 Reel for Redfin & Rocket Mortgage.
    Property: {property_info['title']} - Price: ${property_info['price']:,} - PITI: ${property_info['monthly_piti']:,}/mo.
    Return JSON with:
    1. 'captions': list of 4 objects (start, end, tag, text).
    2. 'veo_prompt': high-detail camera prompt for veo-3.1-generate-001 (vertical 9:16).
    3. 'voiceover_script': conversational script under 45 words for 24kHz audio.
    """
    resp = client_global.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.3,
            thinking_config=types.ThinkingConfig(thinking_level="LOW"),
        ),
    )
    return json.loads(resp.text)

def generate_imagen4_keyframe(visual_prompt: str) -> bytes:
    """Uses imagen-4.0-generate-001 to render a 9:16 vertical anchor frame."""
    result = client_us.models.generate_images(
        model="imagen-4.0-generate-001",
        prompt=visual_prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="9:16",
            output_mime_type="image/jpeg",
        ),
    )
    return result.generated_images[0].image.image_bytes
```

## Step 3: Implement Veo 3.1 Motion & 24kHz Native Voiceover

```python
def generate_veo_video(prompt: str, image_gcs_uri: str = None) -> str:
    """Uses veo-3.1-generate-001 for high-fidelity vertical video generation."""
    source_kwargs = {}
    if image_gcs_uri:
        source_kwargs["image"] = types.Image.from_uri(image_gcs_uri)
    
    op = client_global.models.generate_videos(
        model="veo-3.1-generate-001",
        prompt=prompt,
        config=types.GenerateVideosConfig(
            aspect_ratio="9:16",
            duration_seconds=6,
            person_generation="dont_allow",
        ),
        **source_kwargs,
    )
    # Poll operation until completion and return Cloud Storage MP4 URI
    return op.result().generated_videos[0].video.uri

def generate_gemini_voiceover(script: str, voice_name: str = "Aoede") -> bytes:
    """Generates 24,000Hz 16-bit linear PCM audio via Gemini 3.8 Live."""
    # Connects to Gemini Live audio synthesis endpoint and yields audio bytes...
```

## Step 4: Verification & Edge Reel Pre-Caching

Test the module with the CLI:

```bash
python3 -c "import engine; print(engine.PRESET_REELS['royal_oak']['title'], engine.PRESET_REELS['royal_oak']['monthly_piti'])"
```

Verify that `static/reels/` contains all 11 production video files and thumbnails for zero-latency demonstration.
