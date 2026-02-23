import json
import logging
import uuid
import time
from typing import Optional, Any, AsyncGenerator
from google.adk.agents import BaseAgent
from google.adk.agents.callback_context import CallbackContext
import google.genai.types as types

logger = logging.getLogger(__name__)

def intercept_payload_callback(ctx: CallbackContext, **kwargs) -> Optional[types.Content]:
    """
    Interceptor callback that captures the raw request_json from Gemini Enterprise.
    It returns a formatted response immediately, effectively 'echoing' the payload
    without triggering the underlying LLM logic.
    """
    # In ADK, the incoming message is usually in ctx.message or arguments
    # However, Gemini Enterprise calls streaming_agent_run_with_events(request_json=...)
    # We can try to get it from the state if the Runner injects it, 
    # or we can rely on the fact that we are intercepting the method call at the Runner level.
    
    # For this specific implementation, we will assume the Runner passes the raw payload 
    # and we want to format it for the user.
    return None # We will handle the specific 'request_json' interception in the Runner proxy

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
        # In this specific context, we are getting it from the 'request_json' arg
        # formatted by the proxy in main.py or deploy_standalone.py
        request_json = ctx.arguments.get("request_json", "{}")
        
        try:
            # Attempt to pretty-print the intercepted JSON
            import json
            payload_obj = json.loads(request_json)
            formatted_json = json.dumps(payload_obj, indent=2)
        except Exception:
            formatted_json = request_json

        return types.Content(
            role="model",
            parts=[types.Part(text=f"### 🕵️ Gemini Enterprise Interceptor payload captured!\n\n**Raw `request_json`**:\n```json\n{formatted_json}\n```")]
        )

    async def _run_async_impl(self, ctx: CallbackContext, **kwargs) -> types.Content:
        # Fallback if no content is returned by the callback
        return types.Content(
            role="model",
            parts=[types.Part(text="Interceptor Active: Waiting for payload...")]
        )

    def query(self, **kwargs):
        """
        Required by Reasoning Engine validation.
        """
        pass

    async def streaming_agent_run_with_events(self, request_json: str, config: Optional[Any] = None) -> AsyncGenerator[str, None]:
        """
        Method required by Gemini Enterprise (Discovery Engine) to invoke the agent.
        It parses the 'request_json', runs the intercept logic, and yields the response event.
        """
        logger.info(f"Interceptor received request_json: {request_json[:200]}...") # Log first 200 chars

        # Create a mock context for the intercept logic
        class MockContext:
            def __init__(self, arg):
                self.arguments = {"request_json": arg}
        
        ctx = MockContext(request_json)
        
        # Run the intercept logic
        content = await self.intercept_logic(ctx)
        
        # Yield the response as a JSON string, mocking a generation event
        # The format must match what GE expects from a custom agent
        # We wrap the content text in a valid response structure
        response_text = content.parts[0].text
        
        # Construct a simple response event
        # In a real scenario, this might need to match the specific schema GE expects from the agent
        # for now, we just yield the text.
        yield response_text

interceptor_app = GEMINIPayloadInterceptor()
