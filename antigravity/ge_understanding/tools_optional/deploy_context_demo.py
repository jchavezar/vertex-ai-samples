import os
import vertexai
from vertexai.preview import reasoning_engines
import logging
from typing import Optional, Any, Callable

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Deployment Config
PROJECT_ID = "vtxdemos"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://adk_staging_bucket_vtxdemos"

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)

# Define the Agent class directly in the script
try:
    from google.adk.agents import BaseAgent
    from google.adk.agents.callback_context import CallbackContext
    from google.adk.tools.tool_context import ToolContext
    import google.genai.types as types
except ImportError:
    pass

class ContextDemoAgent(BaseAgent):
    tools: list[Callable] = []
    
    def __init__(self):
        super().__init__(
            name="ContextDemoAgent",
            description="Agent to demonstrate ADK context extraction (Standalone Pattern)",
            tools=[self.who_am_i]
        )

    def who_am_i(self, tool_context: ToolContext = None) -> dict:
        """Returns the current session context information."""
        if tool_context and tool_context.invocation_context:
             session = tool_context.invocation_context.session
             return {
                 "session_id": session.session_id,
                 "user_id": session.user_id,
                 "state": session.state
             }
        return {"error": "No tool context available"}

    async def query(self, prompt: str = "", **kwargs) -> dict:
        """Entry point for Reasoning Engine. Returns debug info about inputs."""
        return {
            "message": "Hello from ContextDemoAgent (Standalone)",
            "received_kwargs": list(kwargs.keys()),
            "prompt": prompt,
            "tool_output": self.who_am_i() # Call without context to see default behavior
        }

def deploy():
    print("🚀 Starting ContextDemoAgent deployment...")
    agent = ContextDemoAgent()
    
    try:
        remote_agent = reasoning_engines.ReasoningEngine.create(
            agent,
            requirements=[
                "google-cloud-aiplatform[adk,agent_engines]>=1.75.0",
                "google-adk>=0.2.0",
                "cloudpickle",
            ],
            display_name="ContextDemoAgent_Standalone",
            description="Agent to demonstrate context extraction (Standalone Pattern)",
        )
        print(f"✅ Deployment successful!")
        print(f"Resource Name: {remote_agent.resource_name}")
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    deploy()
