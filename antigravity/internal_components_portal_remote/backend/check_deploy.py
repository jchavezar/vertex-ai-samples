import vertexai
import os
from dotenv import load_dotenv

load_dotenv(override=True)

vertexai.init(project=os.getenv("GOOGLE_CLOUD_PROJECT", "vtxdemos"), location="us-central1")
client = vertexai.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT", "vtxdemos"), location="us-central1")

print("Listing Agent Engines...")
engines = list(client.agent_engines.list())
if not engines:
    print("No Agent Engines found.")
else:
    for e in engines:
        print(f"Name: {e.api_resource.name}")
        print(f"Display Name: {e.api_resource.display_name}")
        # Some versions might use different attr structure or dictionaries layout
        try:
             print(f"Create Time: {e.api_resource.create_time}")
        except: pass
        print("-" * 40)
