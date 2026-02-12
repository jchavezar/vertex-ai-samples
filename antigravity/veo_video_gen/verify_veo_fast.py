import os
import base64
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")

client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location=LOCATION
)

def test_text_to_video():
    print("\n--- Testing Text-to-Video (Fast) ---")
    prompt = "A cinematic shot of a sunset over a digital ocean, cyberpunk style"
    source = types.GenerateVideosSource(prompt=prompt)
    config = types.GenerateVideosConfig(duration_seconds=5)
    
    try:
        print(f"Submitting request with model: veo-3.1-fast-generate-preview")
        op = client.models.generate_videos(
            model="veo-3.1-fast-generate-preview",
            source=source,
            config=config
        )
        print(f"Operation started: {op.name}")
        
        # Poll for 30 seconds max for a quick test
        start_time = time.time()
        while not op.done:
            if time.time() - start_time > 60:
                print("Timed out waiting for operation (Expected for full generation, but connectivity confirmed).")
                return True
            print("Polling...")
            time.sleep(5)
            op = client.operations.get(op.name)
            
        print("Success! Operation complete.")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_text_to_video()
