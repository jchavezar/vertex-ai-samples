import json
import logging
import uuid
import time
from typing import Optional, Any, AsyncGenerator, Callable
import sys
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("DEBUG: Starting agent.py", file=sys.stderr)
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"DEBUG: current_dir={current_dir}", file=sys.stderr)
    parent_dir = os.path.dirname(current_dir)
    print(f"DEBUG: parent_dir={parent_dir}", file=sys.stderr)
    print(f"DEBUG: Listing parent_dir: {os.listdir(parent_dir)}", file=sys.stderr)
    
    vendor_path = os.path.join(parent_dir, 'vendor')
    print(f"DEBUG: vendor_path={vendor_path}", file=sys.stderr)
    if os.path.exists(vendor_path):
        print(f"DEBUG: Adding vendor path: {vendor_path}", file=sys.stderr)
        sys.path.insert(0, vendor_path)
    else:
        print("DEBUG: vendor path DOES NOT EXIST", file=sys.stderr)

    import google.adk
    print("DEBUG: Successfully imported google.adk", file=sys.stderr)
except Exception as e:
    print(f"DEBUG: Error in agent.py setup: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)

from google.adk.agents import BaseAgent, InvocationContext
from google.adk.agents.callback_context import CallbackContext
from google.adk.events.event import Event
from google.adk.tools.tool_context import ToolContext
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

    async def intercept_logic(self, callback_context: CallbackContext, **kwargs) -> Optional[types.Content]:
        # Extract the raw payload from reasoning engine request if available
        # In current ADK, callback_context wraps invocation_context.
        ctx = callback_context
        request_json = kwargs.get("request_json", "{}")
        
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

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # Fallback if no content is returned by the callback
        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            content=types.Content(
                role="model",
                parts=[types.Part(text="Interceptor Active: Waiting for payload...")]
            )
        )

    async def query(self, payload: dict) -> str:
        """
        Standard Reasoning Engine query method.
        Wraps the GE-specific streaming method for easier testing.
        """
        request_json = json.dumps(payload)
        logger.info(f"Query called with payload type: {type(payload)}")
        
        # Invoke the streaming logic
        # Since query is expected to return a value (not a stream usually in this context),
        # we will collect the stream.
        try:
            response_content = ""
            async for chunk in self.streaming_agent_run_with_events(request_json):
                response_content += chunk
            return response_content
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return json.dumps({"text": f"Error: {str(e)}", "metadata": {}})

    async def streaming_agent_run_with_events(self, request_json: str, config: Optional[Any] = None) -> AsyncGenerator[str, None]:
        """
        Method required by Gemini Enterprise (Discovery Engine) to invoke the agent.
        It parses the 'request_json', runs the intercept logic, and yields the response event.
        """
        logger.info(f"Interceptor received request_json: {request_json[:200]}...") # Log first 200 chars

        # Create a mock context for the intercept logic
        callback_context = CallbackContext(invocation_context=None) # Bare context for demo
        
        # Run the intercept logic
        content = await self.intercept_logic(callback_context=callback_context, request_json=request_json)
        response_text = content.parts[0].text
        
        # Try to parse request_json for metadata
        try:
            req_data = json.loads(request_json)
        except:
            req_data = {"raw": request_json}

        # Construct the full payload with metadata
        full_payload = {
            "text": response_text,
            "metadata": {
                "original_request": req_data,
                "session_id": req_data.get("session", "unknown") if isinstance(req_data, dict) else "unknown",
                "timestamp": time.time()
            }
        }
        
        # Yield the response as a JSON string
        yield json.dumps(full_payload)


class ContextDemoAgent(BaseAgent):
    tools: list[Callable] = []

    def __init__(self):
        super().__init__(
            name="ContextDemoAgent",
            description="Agent to demonstrate ADK context extraction",
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
            "message": "Hello from ContextDemoAgent",
            "received_kwargs": list(kwargs.keys()),
            "prompt": prompt,
            "tool_output": self.who_am_i() # Call without context to see default behavior
        }

interceptor_app = GEMINIPayloadInterceptor()
