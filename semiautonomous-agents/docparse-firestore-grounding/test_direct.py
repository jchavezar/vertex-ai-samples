"""Test reasoning engine directly."""
import vertexai
from vertexai.preview import reasoning_engines

PROJECT_ID = "sharepoint-wif"
LOCATION = "us-central1"
RESOURCE_NAME = "projects/984359513632/locations/us-central1/reasoningEngines/7425086135010852864"

vertexai.init(project=PROJECT_ID, location=LOCATION)

agent = reasoning_engines.ReasoningEngine(RESOURCE_NAME)

print("Testing agent...")
print("\nAvailable operations:")
print(dir(agent))

# Try different query methods
print("\n=== Testing with operations.query ===")
try:
    response = agent.operations.query(input="bring me all the statistics for milenial gen?")
    print(f"Response: {response}")
except Exception as e:
    print(f"Error: {e}")
