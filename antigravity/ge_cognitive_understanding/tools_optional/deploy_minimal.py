
import os
import logging
import vertexai
from vertexai.preview import reasoning_engines
from dotenv import load_dotenv
from minimal_agent import MinimalAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
PROJECT_ID = os.getenv("PROJECT_ID", "254356041555")
LOCATION = os.getenv("LOCATION", "us-central1")
STAGING_BUCKET = os.getenv("STAGING_BUCKET", "gs://sockcop-staging-bucket")

def deploy():
    vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)
    
    agent = MinimalAgent()
    
    try:
        remote_agent = reasoning_engines.ReasoningEngine.create(
            agent,
            display_name="MinimalAgent",
            requirements=[
                # Minimal requirements to mirror defaults somewhat
                "cloudpickle",
                "pydantic",
                "google-cloud-aiplatform",
                "google-genai",
                "google-cloud-logging" 
            ]
        )
        logger.info(f"DEPLOYMENT SUCCESSFUL: {remote_agent.resource_name}")
        return remote_agent.resource_name
    except Exception as e:
        logger.error(f"Deployment failed: {e}")

if __name__ == "__main__":
    deploy()
