
import os
import logging
from dotenv import load_dotenv
from google import genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")

logger.info(f"Project: {PROJECT_ID}")
logger.info(f"Location: {LOCATION}")

try:
    # Explicitly creating client with vertexai=True
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    
    # Simple list models call to verify auth
    logger.info("Listing models...")
    models = list(client.models.list(config={"page_size": 5}))
    for m in models:
        logger.info(f"Found model: {m.name}")
        
    logger.info("Auth successful!")

except Exception as e:
    logger.error(f"Auth failed: {e}")
    raise
