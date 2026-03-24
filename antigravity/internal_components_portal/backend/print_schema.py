import vertexai
import os
from dotenv import load_dotenv

load_dotenv(override=True)
vertexai.init(project=os.getenv("GOOGLE_CLOUD_PROJECT", "vtxdemos"), location="us-central1")
client = vertexai.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT", "vtxdemos"), location="us-central1")

ENGINE_ID = "projects/254356041555/locations/us-central1/reasoningEngines/3149353695427166208"
print(f"Loading engine: {ENGINE_ID}")
remote_app = client.agent_engines.get(name=ENGINE_ID)

print("\nOperation Schemas:")
schemas = remote_app.operation_schemas()
print(schemas)
for schema in schemas:
     print(f"\nSchema Details for {schema.name if hasattr(schema, 'name') else 'unknown'}:")
     print(schema)
