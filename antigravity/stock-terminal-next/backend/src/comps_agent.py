import os
import logging
import asyncio
import json
import re
from typing import List, Optional, Dict, Any
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
import google.adk as adk
from google.genai import types

# Import the new ADK workflow
from src.adk_comps_workflow import run_adk_comps_workflow

logger = logging.getLogger("comps_agent")

async def run_comps_intelligence(ticker: str, session_id: str, context: str = "", token: Optional[str] = None):
    """
    Runs the live ADK intelligence workflow and yields reasoning steps and final intel.
    """
    print(f"\n[NEURAL_SYNC] Establishing isolated live channel for {ticker}...")
    
    try:
        # Delegate to the specialized ADK workflow
        async for event in run_adk_comps_workflow(ticker, session_id, context, token):
            if event["type"] == "reasoning":
                # Ensure the message has the leading '>' for the frontend to recognize it as reasoning
                message = event["message"]
                if not message.startswith('>'):
                    message = f"> {message}"
                
                print(f"[AGENT_THOUGHT] {message[:70]}...")
                yield {
                    "type": "reasoning", 
                    "message": message, 
                    "progress": event.get("progress", 50)
                }
            elif event["type"] == "intel":
                print(f"[NEURAL_SYNC] Deep intelligence received for {ticker}")
                yield {"type": "intel", "data": event["data"]}
            elif event["type"] == "error":
                logger.error(f"ADK Workflow Error: {event.get('message')}")
                yield {"type": "error", "message": event.get("message", "Unknown recon error")}
                
    except Exception as e:
        logger.error(f"Failed to run live comps intelligence: {e}")
        yield {"type": "error", "message": f"Intelligence synthesis failed: {str(e)}"}


if __name__ == "__main__":
    async def main():
        print("Starting direct live agent test...")
        async for event in run_comps_intelligence("NVDA", "test_session_live"):
            if event["type"] == "reasoning":
                print(f"REASONING: {event['message']}")
            elif event["type"] == "intel":
                print(f"INTEL DATA: {json.dumps(event['data'], indent=2)}")
            else:
                print(f"EVENT: {event}")
    
    asyncio.run(main())
