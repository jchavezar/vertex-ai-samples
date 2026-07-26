import google.auth
import vertexai

credentials, project = google.auth.default()

try:
    print("Initializing Vertex Client...")
    client = vertexai.Client(project="254356041555", location="us-central1")
    print("Listing Agent Engines...")
    for engine in client.agent_engines.list():
        print("Engine Resource Name:", engine.api_resource.name)
        print("Display Name:", engine.api_resource.display_name)
        print("Staging Bucket:", engine.api_resource.config.staging_bucket)
        print("Identity Type:", getattr(engine.api_resource.config, "identity_type", "None"))
        print("-" * 40)
except Exception as e:
    print("Failed to list agent engines:", e)
