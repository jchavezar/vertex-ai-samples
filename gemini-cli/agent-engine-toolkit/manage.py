from google.genai import Client

# Configuration
PROJECT = "vtxdemos"
LOCATION = "us-central1"

def manage_engines():
    client = Client(
        vertexai=True,
        project=PROJECT,
        location=LOCATION
    )

    print(f"Listing Agent Engines in {PROJECT}/{LOCATION}:")
    try:
        engines = client.agent_engines.list()
        for engine in engines:
            print(f"- {engine.display_name} ({engine.name})")
    except Exception as e:
        print(f"Error listing engines: {e}")

if __name__ == "__main__":
    manage_engines()
