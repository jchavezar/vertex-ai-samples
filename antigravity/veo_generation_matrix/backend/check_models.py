
import os
import vertexai
from vertexai.preview.generative_models import GenerativeModel
from google.cloud import aiplatform

project_id = os.getenv("PROJECT_ID", "vtxdemos")
location = os.getenv("LOCATION", "us-central1")

vertexai.init(project=project_id, location=location)

print(f"Checking models in {project_id} / {location}")

try:
    models = aiplatform.Model.list(project=project_id, location=location)
    print("Custom Models:")
    for m in models:
        print(f"- {m.display_name} ({m.resource_name})")
except Exception as e:
    print(f"Error listing custom models: {e}")

print("\nTrying to list publisher models via Model Garden API (if possible) or just testing common ones...")

common_models = [
    "gemini-1.5-flash-001",
    "gemini-1.5-flash-002",
    "gemini-1.5-pro-001",
    "gemini-1.5-pro-002",
    "gemini-1.0-pro-001",
    "gemini-1.0-pro",
    "gemini-pro",
    "text-bison@001",
    "text-bison@002"
]

for m_name in common_models:
    try:
        model = GenerativeModel(m_name)
        print(f"Checking {m_name}...")
        response = model.generate_content("Hello")
        print(f"SUCCESS: {m_name} worked.")
        break
    except Exception as e:
        print(f"FAIL: {m_name} - {e}")
