import os
import vertexai
from vertexai.preview import reasoning_engines
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ID = "vtxdemos"
LOCATION = "us-central1"

vertexai.init(project=PROJECT_ID, location=LOCATION)

def cleanup():
    print(f"Checking for engines to cleanup in {PROJECT_ID}...")
    engines = reasoning_engines.ReasoningEngine.list()
    
    # We want to keep active ones, but also remove the ones that explicitly failed recently.
    # Note: ReasoningEngine.create() doesn't immediately return a usable object if it fails,
    # but the listing will show it.
    
    for eng in engines:
        try:
            name = eng.resource_name
            uid = name.split("/")[-1]
            display_name = getattr(eng, "display_name", "Unknown")
            
            # Delete if it's one of the known failed ones or redundant ones
            if display_name in ["GEMINIPayloadInterceptor", "ContextDemoAgent"] and "Standalone" not in display_name:
                print(f"🗑️ Deleting redundant/failed engine: {name} ({display_name})")
                eng.delete()
            elif "Minimal" in display_name or "testing" in display_name.lower():
                print(f"🗑️ Deleting test engine: {name} ({display_name})")
                eng.delete()
            else:
                print(f"✅ Keeping engine: {name} ({display_name})")
        except Exception as e:
            print(f"⚠️ Error processing {eng.resource_name}: {e}")

if __name__ == "__main__":
    cleanup()
