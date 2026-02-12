
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID", "vtxdemos")
LOCATION = os.getenv("LOCATION", "us-central1")

print(f"Project: {PROJECT_ID}, Location: {LOCATION}")

client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location=LOCATION
)

print("Listing models...")
try:
    # This might list a lot, let's filter
    for m in client.models.list(config={"page_size": 100}):
        if "veo" in m.name or "video" in m.name:
            print(f"Found model: {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")

print("\nTesting Text-to-Video with 'veo-2.0-generate-001'...")
try:
    from google.genai import types
    source = types.GenerateVideosSource(prompt="Test video of a ball")
    config = types.GenerateVideosConfig(
        duration_seconds=5,
        model="veo-2.0-generate-001"
    )
    # Just check if we can creating the operation, don't wait for result if it takes too long
    # But failing fast is good
    op = client.models.generate_videos(
        model="veo-2.0-generate-001",
        source=source,
        config=config
    )
    print(f"Operation created: {op.name}")
except Exception as e:
    print(f"Error testing video generation: {e}")
