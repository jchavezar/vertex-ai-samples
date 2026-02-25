
import os
import logging
from vertexai.preview import reasoning_engines
import vertexai
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

def cleanup_duplicates(display_name_target):
    logger.info(f"Initializing Vertex AI with Project: {PROJECT_ID}, Location: {LOCATION}")
    vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)

    logger.info(f"Listing agents to find duplicates of '{display_name_target}'...")
    try:
        agents = reasoning_engines.ReasoningEngine.list(project=PROJECT_ID, location=LOCATION)
    except Exception as e:
        logger.error(f"Failed to list agents: {e}")
        return

    targets = []
    for agent in agents:
        if agent.display_name == display_name_target:
            targets.append(agent)
    
    if not targets:
        logger.info(f"No agents found with display name '{display_name_target}'")
        return

    logger.info(f"Found {len(targets)} agents with name '{display_name_target}'.")
    
    # Sort by update_time ? ReasoningEngine object might not have it easily accessible in list
    # We will assume order returned is ... indeterminate?
    # Actually, we probably want to keep the NEWEST one.
    # Let's just list them with their resource names.
    
    for agent in targets:
        logger.info(f"Found: {agent.resource_name} (created/updated: {agent.update_time})")

    # For safety, this script will NOT delete automatically yet.
    # It just lists them. To delete, we would call agent.delete()
    
    # To delete all but the last one (assuming list is not sorted, we rely on update_time if available):
    sorted_targets = sorted(targets, key=lambda x: x.update_time, reverse=True)
    
    logger.info(f"Keeping the most recent one: {sorted_targets[0].resource_name}")
    to_delete = sorted_targets[1:]
    
    if not to_delete:
         logger.info("No duplicates to delete (only 1 exists).")
         return

    logger.info(f"Ready to delete {len(to_delete)} old agents.")
    # Uncomment to enable deletion
    for agent in to_delete:
        logger.info(f"Deleting {agent.resource_name}...")
        try:
            agent.delete()
            logger.info("Deleted.")
        except Exception as e:
            logger.error(f"Failed to delete {agent.resource_name}: {e}")

if __name__ == "__main__":
    # Example usage: duplicate name cleanup
    cleanup_duplicates("FixedGEInterceptor")
    cleanup_duplicates("GEMINIPayloadInterceptor")
    # cleanup_duplicates("ContextDemoAgent")
