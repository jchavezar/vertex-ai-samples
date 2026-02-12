import os
import time
from google import genai
from google.genai import types

def test():
    client = genai.Client(vertexai=True, location="us-central1")
    prompt = "A simple 1 second test, minimal text."
    source = types.GenerateVideosSource(prompt=prompt)
    config = types.GenerateVideosConfig(
        duration_seconds=5,
        aspect_ratio="16:9",
        number_of_videos=1,
        resolution="720p"
    )
    
    op = client.models.generate_videos(
        model="veo-3.1-fast-generate-preview",
        source=source,
        config=config
    )
    
    print(f"op name: {op.name}")
    print("Waiting for completion...")
    while not op.done:
        print("Polling...")
        time.sleep(5)
        # Refresh the operation
        try:
           op = client.operations.get(operation=op.name)
        except Exception as e:
           print(f"client.operations.get failed: {e}")
           break

    print(f"op done: {op.done}")
    if hasattr(op, 'error') and op.error:
        print(f"op ERROR: {op.error}")
        
    if op.done:
        print(f"op result: {op.result}")
        if hasattr(op, 'result') and hasattr(op.result, 'generated_videos'):
             print(f"Got {len(op.result.generated_videos)} videos")
             
if __name__ == "__main__":
    test()
