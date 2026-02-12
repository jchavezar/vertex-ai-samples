import os
import time
import base64
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

def run_debug_test():
    print("=== HYPER-ROBUST VEO DEBUG TEST ===")
    prompt = "A high-speed race car driving through a futuristic city at night, neon lights"
    source = types.GenerateVideosSource(prompt=prompt)
    config = types.GenerateVideosConfig(
        duration_seconds=5,
        aspect_ratio="16:9",
        resolution="720p",
        person_generation="allow_all"
    )
    
    try:
        print(f"Submitting request to veo-3.1-fast-generate-preview...")
        op = client.models.generate_videos(
            model="veo-3.1-fast-generate-preview",
            source=source,
            config=config
        )
        
        # Determine name
        if isinstance(op, str):
            op_name = op
        elif hasattr(op, 'name'):
            op_name = op.name
        else:
            print(f"FAILED to find name in op: {type(op)} - {op}")
            return

        print(f"Operation Name: {op_name}")
        
        timeout = 600 # 10 minutes
        start = time.time()
        
        while True:
            elapsed = time.time() - start
            if elapsed > timeout:
                print(f"TIMEOUT reached after {elapsed:.1f}s")
                return
            
            # Fetch status
            current_op = client.operations.get(op_name)
            print(f"Polling (Elapsed: {elapsed:.1f}s) - Status: {getattr(current_op, 'done', 'UNKNOWN')} - Type: {type(current_op)}")
            
            if hasattr(current_op, 'done') and current_op.done:
                print("Operation DONE!")
                if current_op.result and hasattr(current_op.result, 'generated_videos') and current_op.result.generated_videos:
                    print(f"SUCCESS: Generated {len(current_op.result.generated_videos)} videos.")
                else:
                    print(f"FAILURE: No videos in result. Result: {getattr(current_op, 'result', 'NO_RESULT')}")
                break
                
            time.sleep(15)
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    run_debug_test()
