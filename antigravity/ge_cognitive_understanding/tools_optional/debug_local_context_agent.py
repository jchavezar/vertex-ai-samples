
import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

# Ensure backend path is in sys.path
sys.path.append(os.path.dirname(__file__))

from agent_pkg import agent

async def main():
    logger.info("Initializing ContextDemoAgent...")
    try:
        my_agent = agent.ContextDemoAgent()
        logger.info("Agent initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        return

    logger.info("Testing query method...")
    try:
        response = await my_agent.query(prompt="Who am I?")
        logger.info(f"Query response: {response}")
    except Exception as e:
        logger.error(f"Query failed: {e}")

    logger.info("Testing who_am_i tool directly...")
    try:
        # This will likely return "No tool context available" since it's not running in RE
        # but we want to ensure it doesn't crash.
        who = my_agent.who_am_i()
        logger.info(f"who_am_i response: {who}")
    except Exception as e:
        logger.error(f"who_am_i failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
