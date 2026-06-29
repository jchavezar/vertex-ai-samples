import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/usr/local/google/home/jesusarguelles/.config/gcloud/legacy_credentials/admin@jesusarguelles.altostrat.com/adc.json"
import importlib
from dotenv import load_dotenv
import vertexai
from vertexai.agent_engines import AdkApp
from vertexai._genai import types as ge_types

# Load environment from parent directory
load_dotenv(dotenv_path="../.env", override=True)



# Configuration
PROJECT_ID = "vtxdemos"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://vtxdemos_staging"
AGENT_ENGINE_NAME = os.getenv("AGENT_ENGINE_NAME", "bain-financial-secure-agent")
MCP_URL = os.getenv("SHAREPOINT_MCP_URL", "https://ge-custom-sharepoint-mcp-254356041555.us-central1.run.app/mcp")

print(f"""
========================================
Agent Engine Deployment - Bain Financial Agent (Ultra-Low Latency Edition)
========================================
Project:           {PROJECT_ID}
Location:          {LOCATION}
Agent Name:        {AGENT_ENGINE_NAME}
Staging Bucket:    {STAGING_BUCKET}
MCP URL:           {MCP_URL}
========================================
""")

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Set agent identity configuration
os.environ["USE_AGENT_IDENTITY"] = "0"
os.environ["CONNECTOR_RESOURCE"] = "projects/254356041555/locations/us-central1/connectors/entra-oauth-sharepoint"

# Import and reload agent module
import agent
importlib.reload(agent)

# Create client
client = vertexai.Client(
    project=PROJECT_ID,
    location=LOCATION,
    http_options=dict(api_version="v1beta1")
)

# Wrap the agent with AdkApp using standard console-controlled telemetry
deployment_app = AdkApp(
    agent=agent.root_agent,
    app_name=AGENT_ENGINE_NAME,
)

# Check for existing engine
print(f"Searching for existing Agent Engine: {AGENT_ENGINE_NAME}...")
all_engines = list(client.agent_engines.list())
target_engine = next(
    (e for e in all_engines if e.api_resource.display_name == AGENT_ENGINE_NAME),
    None
)

# Get project number for service account
import subprocess
project_number = subprocess.run(
    ["gcloud", "projects", "describe", PROJECT_ID, "--format=value(projectNumber)"],
    capture_output=True, text=True
).stdout.strip()
SERVICE_ACCOUNT = f"{project_number}-compute@developer.gserviceaccount.com"
print(f"Using service account: {SERVICE_ACCOUNT}")

from vertexai._genai import types as ge_types

# Deploy configuration
deploy_config = {
    "display_name": "bain-financial-secure-agent",
    "staging_bucket": STAGING_BUCKET,
    "requirements": "requirements.txt",
    # "identity_type": ge_types.IdentityType.AGENT_IDENTITY,
    # "agent_gateway_config": {
    #     "agent_to_anywhere_config": {
    #         "agent_gateway": f"projects/{project_number}/locations/{LOCATION}/agentGateways/reasoning-engine-gateway"
    #     }
    # },
    # Ensure all ultra-low latency Graph client modules are bundled into the container
    "extra_packages": ["agent.py", "graph_client.py", "doc_reader.py"],
    "env_vars": {
        "GOOGLE_CLOUD_LOCATION": "global",
        "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY": "true",
        "GOOGLE_GENAI_USE_VERTEXAI": "true",
        "SHAREPOINT_MCP_URL": MCP_URL,
        "PROJECT_NUMBER": project_number,
        "CONNECTOR_RESOURCE": f"projects/{project_number}/locations/{LOCATION}/connectors/sharepoint-3lo",
        "USE_AGENT_IDENTITY": "0",
        "PYTHONUNBUFFERED": "1",
    }
}

if target_engine:
    print(f"Found existing engine: {target_engine.api_resource.name}. Updating...")
    try:
        remote_app = client.agent_engines.update(
            name=target_engine.api_resource.name,
            agent=deployment_app,
            config=deploy_config
        )
        print(f"Update complete: {remote_app.api_resource.name}")
    except Exception as e:
        print(f"Update failed with error: {e}. Deleting existing engine and creating a new one...")
        try:
            client.agent_engines.delete(name=target_engine.api_resource.name, force=True)
        except Exception as delete_e:
            print(f"Delete failed: {delete_e}")
        remote_app = client.agent_engines.create(
            agent=deployment_app,
            config=deploy_config
        )
        print(f"Creation complete: {remote_app.api_resource.name}")
else:
    print("No existing engine found. Creating new one...")
    remote_app = client.agent_engines.create(
        agent=deployment_app,
        config=deploy_config
    )
    print(f"Creation complete: {remote_app.api_resource.name}")

# Extract resource ID
resource_name = remote_app.api_resource.name
resource_id = resource_name.split("/")[-1]

print(f"""
========================================
Deployment Complete!
========================================
Resource Name: {resource_name}
Resource ID:   {resource_id}
========================================
""")
