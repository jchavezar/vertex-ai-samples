
from google.cloud import aiplatform
from vertexai.preview import reasoning_engines
import vertexai

import os
import sys
from dotenv import load_dotenv
from google.cloud import aiplatform
from vertexai.preview import reasoning_engines
import vertexai

# Load environment variables from .env file
# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the .env file (one level up)
dotenv_path = os.path.join(os.path.dirname(script_dir), '.env')

if os.path.exists(dotenv_path):
    print(f"Loading .env from: {dotenv_path}")
    load_dotenv(dotenv_path=dotenv_path)
else:
    print(f"Warning: .env file not found at {dotenv_path}")

PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
STAGING_BUCKET = os.getenv("STAGING_BUCKET")

if not PROJECT_ID or not LOCATION or not STAGING_BUCKET:
    print("Error: PROJECT_ID, LOCATION, or STAGING_BUCKET not set in .env")
    sys.exit(1)

print(f"Initializing Vertex AI with Project: {PROJECT_ID}, Location: {LOCATION}, Bucket: {STAGING_BUCKET}")
vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)

def list_agents():
    print(f"Listing agents in project {PROJECT_ID} location {LOCATION}...")
    try:
        agents = reasoning_engines.ReasoningEngine.list()
        found_count = 0
        for agent in agents:
            print(f"ID: {agent.resource_name} | Display Name: {agent.display_name}")
            found_count += 1
        print(f"Total agents found: {found_count}")
    except Exception as e:
        print(f"Error listing agents: {e}")

if __name__ == "__main__":
    list_agents()
