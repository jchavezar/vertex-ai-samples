import os
import vertexai
from google.auth import default

# Force variables
os.environ["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

creds, project = default()
print("Default ADC Project:", project)

vertexai.init(project="vtxdemos", location="us-central1")
print("Vertex AI Project:", vertexai._config.env.project)
