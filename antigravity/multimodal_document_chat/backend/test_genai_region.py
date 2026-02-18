import os
from google import genai

project_id = os.environ.get("PROJECT_ID", "vtxdemos")

for model in ["gemini-3.0-flash", "gemini-3.0-flash-preview", "gemini-3-flash-preview", "gemini-3-pro-preview"]:
    for loc in ["us-central1", "us-east1", "us-east5", "europe-west1", "global"]:
        try:
            client = genai.Client(vertexai=True, project=project_id, location=loc)
            response = client.models.generate_content(model=model, contents='hi')
            print(f"SUCCESS: {model} in {loc}")
            break
        except Exception as e:
            # print(f"Failed {model} in {loc}: {repr(e)}")
            pass
