import os
from dotenv import load_dotenv
import vertexai
from google.cloud import aiplatform

# Load environment from parent directory
load_dotenv(dotenv_path="../.env", override=True)

PROJECT_ID = "vtxdemos"
LOCATION = "us-central1"
REASONING_ENGINE_ID = "7757233204599193600"
PROJECT_NUMBER = "254356041555"

print("Initializing Vertex AI...")
aiplatform.init(project=PROJECT_ID, location=LOCATION)

resource_name = f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/reasoningEngines/{REASONING_ENGINE_ID}"

print(f"Loading engine via aiplatform.ReasoningEngine: {resource_name}")
try:
    engine = aiplatform.ReasoningEngine(resource_name)
    print("Engine loaded successfully.")
except Exception as e:
    print(f"Failed to load engine: {e}")
    exit(1)

print("\n--- Attempting to query agent via predict ---")
query = "Who is Jennifer Walsh?"
print(f"Query: {query}")

try:
    print("Trying engine.predict()...")
    # ADK agents usually expect a dict with 'message' or similar.
    # Let's try passing the message.
    resp = engine.predict(message=query)
    print(f"Predict Response: {resp}")
except Exception as e:
    print(f"Predict failed: {e}")

try:
    print("Trying engine.predict() with input dict...")
    resp = engine.predict(input={"message": query})
    print(f"Predict Response: {resp}")
except Exception as e:
    print(f"Predict with input dict failed: {e}")
