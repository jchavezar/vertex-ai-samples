
import os
import logging
from google.cloud import aiplatform
from vertexai.preview import reasoning_engines
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))
load_dotenv() # Fallback

PROJECT_ID = os.getenv("PROJECT_ID", "254356041555")
LOCATION = os.getenv("LOCATION", "us-central1")
STAGING_BUCKET = os.getenv("STAGING_BUCKET", "gs://sockcop-staging-bucket")

def test_agent(resource_name):
    logger.info(f"Testing agent: {resource_name}")
    
    # Initialize Vertex AI
    aiplatform.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)
    
    # Load the remote agent
    remote_agent = reasoning_engines.ReasoningEngine(resource_name)
    
    # Query the agent
    print(f"Querying agent with 'Who am I?'...")
    response = remote_agent.query(prompt="Who am I?")
    print(f"Response: {response}")

if __name__ == "__main__":
    # You need to replace this with the actual resource name from deployment output
    # or passed as an argument
    import sys
    if len(sys.argv) > 1:
        resource_name = sys.argv[1]
        test_agent(resource_name)
    else:
        print("Usage: python test_context_demo.py <resource_name>")
