import os
import vertexai
from vertexai.agent_engines import AdkApp
from agent_pkg.agent import video_expert_agent

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
STAGING_BUCKET = os.environ.get("STAGING_BUCKET", "gs://gcp-vertex-ai-generative-ai")
AGENT_ENGINE_DISPLAY_NAME = "Veo Video Agent"

print(f"Initializing Vertex AI for project {PROJECT_ID} in {LOCATION}")
vertexai.init(project=PROJECT_ID, location=LOCATION)
client = vertexai.Client(project=PROJECT_ID, location=LOCATION)

deployment_app = AdkApp(
    agent=video_expert_agent,
    enable_tracing=False
)

requirements_list = [
    "google-cloud-aiplatform[adk,agent_engines]",
    "google-adk",
    "google-genai",
    "python-dotenv",
    "requests", 
    "pillow",
    "cloudpickle",
    "pydantic"
]

base_dir = os.path.dirname(__file__)
extra_packages = [
    os.path.join(base_dir, "agent_pkg")
]

print("Starting deployment to Agent Engine...")
try:
    remote_app = client.agent_engines.create(
        agent=deployment_app,
        config={
            "display_name": AGENT_ENGINE_DISPLAY_NAME,
            "staging_bucket": STAGING_BUCKET,
            "requirements": requirements_list,
            "extra_packages": extra_packages,
            "env_vars": {"ENABLE_TELEMETRY": "False"}
        }
    )
    print("Deployment successful!")
except Exception as e:
    print(f"Deployment failed: {e}")
