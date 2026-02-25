import os
import vertexai
from vertexai import agent_engines

os.environ["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

vertexai.init(project="vtxdemos", location="us-central1")
try:
    agents = agent_engines.list()
    for a in agents:
         print(f"Found: {a.display_name} -> {a.resource_name}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
