import vertexai
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env", override=True)

PROJECT_ID = "vtxdemos"
LOCATION = "us-central1"
REASONING_ENGINE_ID = "7757233204599193600"
PROJECT_NUMBER = "254356041555"

vertexai.init(project=PROJECT_ID, location=LOCATION)
client = vertexai.Client(project=PROJECT_ID, location=LOCATION)

resource_name = f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/reasoningEngines/{REASONING_ENGINE_ID}"

print(f"Getting engine: {resource_name}")
try:
    engine = client.agent_engines.get(name=resource_name)
    print(f"Type of engine: {type(engine)}")
    print("Attributes:")
    for name in dir(engine):
        if not name.startswith("_"):
            print(name)
except Exception as e:
    print(f"Failed to get engine: {e}")
