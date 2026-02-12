
import os
import sys
from dotenv import load_dotenv
from google import genai

# Mimic main.py logic
dotenv_path = os.path.expanduser("~/.env")
print(f"Loading .env from: {dotenv_path}")
if not os.path.exists(dotenv_path):
    print("File does not exist, trying ../.env")
    dotenv_path = "../.env"

load_dotenv(dotenv_path=dotenv_path)

PROJECT_ID = os.getenv("PROJECT_ID", "vtxdemos")
LOCATION = os.getenv("LOCATION", "us-central1")

print(f"PROJECT_ID: {PROJECT_ID}")
print(f"LOCATION: {LOCATION}")

try:
    print("Initializing Client...")
    client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION
    )
    print("Client initialized. Listing models...")
    # Try a simple call
    # models = list(client.models.list(config={"page_size": 1}))
    # print(f"Found models: {len(models) if models else 0}")
    # Or just generate text
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Hello"
    )
    print(f"Generate response: {response.text}")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
