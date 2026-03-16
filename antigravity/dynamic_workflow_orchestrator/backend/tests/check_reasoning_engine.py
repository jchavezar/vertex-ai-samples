import os
import vertexai
from vertexai.agent_engines import AdkApp
from dotenv import load_dotenv

load_dotenv()
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos") 
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
if LOCATION == "global":
    LOCATION = "us-central1"
vertexai.init(project=PROJECT_ID, location=LOCATION)
client = vertexai.Client(project=PROJECT_ID, location=LOCATION)
all_engines = list(client.agent_engines.list())
for e in all_engines:
    if e.api_resource.display_name == "dynamic_workflow_orchestrator":
        print(f"Engine name: {e.api_resource.name}")
        print(f"Error: {getattr(e.api_resource, 'error', 'No error')}")
