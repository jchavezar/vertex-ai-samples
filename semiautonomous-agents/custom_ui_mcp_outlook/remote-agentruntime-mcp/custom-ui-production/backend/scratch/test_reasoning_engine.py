import google.auth
from google.cloud import aiplatform

credentials, project = google.auth.default()
aiplatform.init(project="254356041555", location="us-central1")

try:
    print("Initializing reasoning engine connection...")
    # Instantiate the deployed reasoning engine by its resource name
    engine = aiplatform.ReasoningEngine("projects/254356041555/locations/us-central1/reasoningEngines/3073250998110650368")
    print("Executing test query...")
    res = engine.query(input="what was my oldest email?")
    print("Success! Response:")
    print(res)
except Exception as e:
    print("Failed to query reasoning engine directly:", e)
