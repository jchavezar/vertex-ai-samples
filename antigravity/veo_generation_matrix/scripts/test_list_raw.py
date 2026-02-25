import os
from google.cloud import aiplatform

aiplatform.init(project="vtxdemos", location="us-central1")
engines = aiplatform.ReasoningEngine.list()
print(f"Total engines found: {len(engines)}")
for e in engines:
    print(f"Name: {e.display_name}, Resource: {e.resource_name}")
