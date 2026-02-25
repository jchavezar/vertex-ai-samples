import os
import vertexai
from vertexai.preview import reasoning_engines
from vertexai import agent_engines # If this fails, I'll alias it
import logging
from typing import Optional, Any, Callable

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Deployment Config
PROJECT_ID = "vtxdemos"
PROJECT_NUMBER = "254356041555"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://adk_staging_bucket_vtxdemos"

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)

# Try to handle the 'agent_engines' alias if it's missing in vertexai directly
try:
    from vertexai import agent_engines
except ImportError:
    # In some versions of aiplatform, it's inside preview or needs to be accessed via ReasoningEngine
    agent_engines = reasoning_engines.ReasoningEngine

# Define the Managed Agent class directly for pickling safety
from google.adk.agents import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
import google.genai.types as types

class ManagedInterceptor(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ManagedInterceptor",
            description="Captures platform-managed session and metadata via AdkApp.",
            before_agent_callback=self.intercept_logic
        )

    async def intercept_logic(self, callback_context: CallbackContext, **kwargs) -> Optional[types.Content]:
        ctx = callback_context
        session = ctx.session
        user_id = getattr(session, "user_id", "N/A")
        session_id = getattr(session, "session_id", "N/A")
        request_json = ctx.arguments.get("request_json", "{}")
        
        summary = f"""### 🛡️ Managed ADK Interceptor
*   **User**: `{user_id}`
*   **Session**: `{session_id}`
*   **Platform**: Vertex AI Agent Engine (AdkApp)

**Incoming JSON**:
```json
{request_json}
```
"""
        return types.Content(role="model", parts=[types.Part(text=summary)])

    async def _run_async_impl(self, callback_context: CallbackContext, **kwargs) -> types.Content:
        return types.Content(role="model", parts=[types.Part(text="Interceptor fallback.")])

def deploy():
    print("🚀 Deploying proper Managed ADK Agent...")
    
    # 1. Instantiate the agent
    agent = ManagedInterceptor()
    
    # 2. Wrap in AdkApp (The secret sauce for managed sessions)
    # This automatically adds set_up and query methods compatible with Reasoning Engine
    app = reasoning_engines.AdkApp(
        agent=agent,
        enable_tracing=True
    )
    
    try:
        # 3. Create using ReasoningEngine.create or agent_engines.create
        # AdkApp acts as the bridge
        remote_agent = reasoning_engines.ReasoningEngine.create(
            app,
            requirements=[
                "google-cloud-aiplatform[adk,agent_engines]>=1.104.0",
                "google-adk>=0.2.0",
                "cloudpickle",
            ],
            display_name="Managed_ADK_Interceptor_V2",
            description="Managed ADK Interceptor compliant with AdkApp patterns.",
        )
        print(f"✅ Deployment successful!")
        print(f"Resource Name: {remote_agent.resource_name}")
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    deploy()
