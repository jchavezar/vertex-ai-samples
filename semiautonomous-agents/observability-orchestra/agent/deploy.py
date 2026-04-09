"""
Deploy Observability Orchestra to Vertex AI Agent Engine.

This deploys the multi-agent setup with tracing enabled for observability testing.

Usage:
    python deploy.py
"""
import os
import subprocess
import importlib
from dotenv import load_dotenv

# Load environment
load_dotenv(override=True)

# Set required environment variables
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "1")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")

import vertexai
from vertexai.agent_engines import AdkApp

# Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "vtxdemos")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
STAGING_BUCKET = os.getenv("STAGING_BUCKET", f"gs://{PROJECT_ID}-staging")
AGENT_ENGINE_NAME = os.getenv("AGENT_ENGINE_NAME", "observability-orchestra")

print(f"""
========================================
Agent Engine Deployment
========================================
Project:        {PROJECT_ID}
Location:       {LOCATION}
Agent Name:     {AGENT_ENGINE_NAME}
Staging Bucket: {STAGING_BUCKET}
========================================
""")

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Import and reload agent module to pick up env changes
import agent
importlib.reload(agent)

# Create client
client = vertexai.Client(project=PROJECT_ID, location=LOCATION)

# Wrap the agent with tracing ENABLED for observability
deployment_app = AdkApp(
    agent=agent.root_agent,
    enable_tracing=True,  # Critical for observability testing
)

# Check for existing engine
print(f"Searching for existing Agent Engine: {AGENT_ENGINE_NAME}...")
all_engines = list(client.agent_engines.list())
target_engine = next(
    (e for e in all_engines if e.api_resource.display_name == AGENT_ENGINE_NAME),
    None
)

# Get project number for service account
project_number = subprocess.run(
    ["gcloud", "projects", "describe", PROJECT_ID, "--format=value(projectNumber)"],
    capture_output=True, text=True
).stdout.strip()
SERVICE_ACCOUNT = f"{project_number}-compute@developer.gserviceaccount.com"
print(f"Using service account: {SERVICE_ACCOUNT}")

# Deploy configuration
deploy_config = {
    "display_name": AGENT_ENGINE_NAME,
    "staging_bucket": STAGING_BUCKET,
    "requirements": "requirements.txt",
    "extra_packages": ["agent.py"],
    "env_vars": {
        "GOOGLE_GENAI_USE_VERTEXAI": "1",
        "GOOGLE_CLOUD_LOCATION": LOCATION,
        "CLAUDE_REGION": os.getenv("CLAUDE_REGION", "us-east5"),  # Claude needs us-east5
        "GEMINI_GLOBAL_REGION": os.getenv("GEMINI_GLOBAL_REGION", "global"),  # Flash-Lite needs global
        "CLAUDE_MODEL": os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6"),
        "FLASHLITE_MODEL": os.getenv("FLASHLITE_MODEL", "gemini-3.1-flash-lite-preview"),
        "ORCHESTRATOR_MODEL": os.getenv("ORCHESTRATOR_MODEL", "gemini-2.5-flash"),
        # OpenTelemetry / Cloud Trace settings
        "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY": "true",
        "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "true",
    },
    "service_account": SERVICE_ACCOUNT,
}

if target_engine:
    print(f"Found existing engine: {target_engine.api_resource.name}. Updating...")
    remote_app = client.agent_engines.update(
        name=target_engine.api_resource.name,
        agent=deployment_app,
        config=deploy_config
    )
    print(f"Update complete: {remote_app.api_resource.name}")
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

Test with:
curl -X POST https://{LOCATION}-aiplatform.googleapis.com/v1/{resource_name}:query \\
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \\
  -H "Content-Type: application/json" \\
  -d '{{"class_method": "async_create_session", "input": {{"user_id": "test"}}}}'

Observability:
- Cloud Trace: https://console.cloud.google.com/traces/list?project={PROJECT_ID}
- Cloud Logging: https://console.cloud.google.com/logs/query?project={PROJECT_ID}
========================================
""")
