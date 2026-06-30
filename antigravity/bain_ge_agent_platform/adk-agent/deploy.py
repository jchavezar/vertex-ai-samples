import os
# Honor an explicit GOOGLE_APPLICATION_CREDENTIALS first; otherwise fall back
# to the user's workstation legacy creds if that file exists (it does on the
# author's machine; it does NOT exist in CI / cloud workstations / new VMs).
# Anywhere else, defer to ADC: `gcloud auth application-default login`.
_DEFAULT_ADC = "/usr/local/google/home/jesusarguelles/.config/gcloud/legacy_credentials/admin@jesusarguelles.altostrat.com/adc.json"
if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") and os.path.exists(_DEFAULT_ADC):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = _DEFAULT_ADC
import importlib
from dotenv import load_dotenv
import vertexai
from vertexai.agent_engines import AdkApp
from vertexai._genai import types as ge_types

# NB: Agent Identity (preview) requires the v1beta1 API surface AND
# IdentityType.AGENT_IDENTITY in the deploy config below. Without those,
# the engine is assigned the default compute SA principal instead of a
# per-agent SPIFFE identity (principal://agents.global.org-*.system.id.goog/...).

# Load environment from parent directory
load_dotenv(dotenv_path="../.env", override=True)



# Configuration
PROJECT_ID = "vtxdemos"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://vtxdemos-staging"
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
    # Agent Identity (preview): assign a per-agent SPIFFE principal so the
    # runtime has a verifiable cryptographic identity at the network layer.
    # Visible in Cloud Audit logs as
    #   principal://agents.global.org-<ORG>.system.id.goog/resources/aiplatform/
    #     projects/<PROJ>/locations/<LOC>/reasoningEngines/<ID>
    "identity_type": ge_types.IdentityType.AGENT_IDENTITY,
    # NOTE: `agent_gateway_config` is NOT a real SDK field. Gateway routing
    # is wired at the network layer (networkservices+networksecurity APIs),
    # not in the engine deploy spec. See ../PRODUCTION_GATEWAY_WIRING.md.
    # Ensure all ultra-low latency Graph client modules + real Agent Gateway
    # policy guard are bundled into the container.
    "extra_packages": [
        "agent.py",
        "graph_client.py",
        "doc_reader.py",
        "policy_guard.py",
    ],
    "env_vars": {
        "GOOGLE_CLOUD_LOCATION": "global",
        "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY": "true",
        "GOOGLE_GENAI_USE_VERTEXAI": "true",
        "SHAREPOINT_MCP_URL": MCP_URL,
        "PROJECT_NUMBER": project_number,
        "CONNECTOR_RESOURCE": f"projects/{project_number}/locations/{LOCATION}/connectors/sharepoint-3lo",
        "USE_AGENT_IDENTITY": "0",
        "PYTHONUNBUFFERED": "1",
        # Real Agent Gateway policy service — every tool call routes through this
        # for an allow/deny decision before execution. Cloud Logging entries
        # surface in the UI's gateway log panel via bain-ge-gateway-logs-svc.
        "POLICY_SERVICE_URL": os.getenv(
            "POLICY_SERVICE_URL",
            "https://bain-ge-policy-svc-254356041555.us-central1.run.app",
        ),
        # Fail-closed by default. Set POLICY_FAIL_OPEN=1 only for emergency
        # graceful-degrade (logs a warning, then permits the call).
        "POLICY_FAIL_OPEN": os.getenv("POLICY_FAIL_OPEN", "0"),
        "GOOGLE_CLOUD_LOCATION_AE": LOCATION,
        # OpenTelemetry / GenAI semantic conventions (preview): the runtime
        # emits agent / model / tool spans to Cloud Trace under the
        # ReasoningEngine resource. Visible at:
        # https://console.cloud.google.com/traces/list?project=vtxdemos
        "OTEL_SEMCONV_STABILITY_OPT_IN": "gen_ai_latest_experimental",
        "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "EVENT_ONLY",
    },
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

# Patch the deployed agent's env to embed its own engine ID so policy_guard.py
# can build the correct source SPIFFE/URN at runtime. (We don't know the ID
# until creation completes, so this is a two-phase update.)
try:
    print(f"Patching REASONING_ENGINE_ID env var to {resource_id}...")
    final_env = dict(deploy_config["env_vars"])
    final_env["REASONING_ENGINE_ID"] = resource_id
    patched_config = {**deploy_config, "env_vars": final_env}
    client.agent_engines.update(
        name=resource_name,
        agent=deployment_app,
        config=patched_config,
    )
    print(f"REASONING_ENGINE_ID env patched.")
except Exception as patch_e:
    print(f"WARN: REASONING_ENGINE_ID patch failed (will fall back to default in policy_guard): {patch_e}")

print(f"""
========================================
Deployment Complete!
========================================
Resource Name: {resource_name}
Resource ID:   {resource_id}
Policy Service: {deploy_config['env_vars']['POLICY_SERVICE_URL']}
========================================
""")
