import os
import vertexai
from vertexai.preview import reasoning_engines
import logging
import json
import time
import uuid
from typing import Optional, Any, AsyncGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Deployment Config
PROJECT_ID = "vtxdemos"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://adk_staging_bucket_vtxdemos"

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)

# Define the Agent class directly in the script to avoid ModuleNotFoundError on remote side
try:
    from google.adk.agents import BaseAgent
    from google.adk.agents.callback_context import CallbackContext
    import google.genai.types as types
except ImportError:
    # This might happen locally if adk is not installed in the current environment
    # but we need it for the remote runtime.
    # We define placeholders for static analysis if needed, but it should be fine here.
    pass

class GEMINIPayloadInterceptor(BaseAgent):
    """
    A legitimate Google ADK agent that intercepts the raw request_json 
    from Gemini Enterprise (AgentSpace).
    """
    def __init__(self, name: str = "ge_interceptor"):
        super().__init__(
            name=name,
            description="Intercepts and visualizes Gemini Enterprise payloads.",
            before_agent_callback=self.intercept_logic
        )

    async def intercept_logic(self, ctx: CallbackContext) -> Optional[types.Content]:
        # Extract the raw payload from reasoning engine request if available
        request_json = ctx.arguments.get("request_json", "{}")
        
        try:
            import json
            payload_obj = json.loads(request_json)
            
            # Extract high-value fields
            session = payload_obj.get("session", "N/A")
            user_id = payload_obj.get("user_id", "N/A")
            metadata = payload_obj.get("metadata", {})
            grounding = metadata.get("grounding_config", "None")
            
            formatted_json = json.dumps(payload_obj, indent=2)
            
            summary_md = f"""### 🕵️ Gemini Enterprise Interceptor payload captured!

**Core Context Attributes**:
*   **👤 User ID**: `{user_id}`
*   **🆔 Session**: `{session}`
*   **🛰️ Grounding**: `{grounding}`

**Full Raw Payload**:
```json
{formatted_json}
```
"""
        except Exception as e:
            summary_md = f"### 🕵️ Interception Error\n\nFailed to parse JSON: {str(e)}\n\nRaw:\n```\n{request_json}\n```"

        return types.Content(
            role="model",
            parts=[types.Part(text=summary_md)]
        )

    async def _run_async_impl(self, ctx: CallbackContext, **kwargs) -> types.Content:
        return types.Content(
            role="model",
            parts=[types.Part(text="Interceptor Active: Waiting for payload...")]
        )

    async def query(self, payload: dict) -> str:
        request_json = json.dumps(payload)
        logger.info(f"Query called with payload type: {type(payload)}")
        try:
            response_content = ""
            async for chunk in self.streaming_agent_run_with_events(request_json):
                response_content += chunk
            return response_content
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return json.dumps({"text": f"Error: {str(e)}", "metadata": {}})

    async def streaming_agent_run_with_events(self, request_json: str, config: Optional[Any] = None) -> AsyncGenerator[str, None]:
        logger.info(f"Interceptor received request_json: {request_json[:200]}...")
        
        # Mock context for the intercept logic
        class MockContext:
            def __init__(self, arg):
                self.arguments = {"request_json": arg}
        
        ctx = MockContext(request_json)
        content = await self.intercept_logic(ctx)
        response_text = content.parts[0].text
        
        try:
            req_data = json.loads(request_json)
        except:
            req_data = {"raw": request_json}

        full_payload = {
            "text": response_text,
            "metadata": {
                "original_request": req_data,
                "session_id": req_data.get("session", "unknown") if isinstance(req_data, dict) else "unknown",
                "timestamp": time.time()
            }
        }
        yield json.dumps(full_payload)

def deploy():
    print("🚀 Starting GEMINIPayloadInterceptor deployment...")
    agent = GEMINIPayloadInterceptor()
    
    try:
        remote_agent = reasoning_engines.ReasoningEngine.create(
            agent,
            requirements=[
                "google-cloud-aiplatform[adk,agent_engines]>=1.75.0",
                "google-adk>=0.2.0",
                "cloudpickle",
            ],
            display_name="GEMINIPayloadInterceptor_Standalone",
            description="Agent to intercept GE payloads (Standalone Pattern)",
        )
        print(f"✅ Deployment successful!")
        print(f"Resource Name: {remote_agent.resource_name}")
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    deploy()
