import os
import vertexai
from google.adk.agents import BaseAgent
from google.adk.agents.callback_context import CallbackContext
import google.genai.types as types
from vertexai.preview import reasoning_engines

class InspectAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="InspectAgent", before_agent_callback=self.inspect)
    
    async def inspect(self, ctx: CallbackContext, **kwargs) -> types.Content:
        info = [
            f"Attributes: {dir(ctx)}",
            f"Kwargs keys: {list(kwargs.keys())}",
            f"User Content: {ctx.user_content}",
            f"Agent Name: {ctx.agent_name}",
            f"State: {ctx.state if hasattr(ctx, 'state') else 'N/A'}"
        ]
        # Check if ctx has state and what's in it
        if hasattr(ctx, 'state') and ctx.state:
            info.append(f"State type: {type(ctx.state)}")
            info.append(f"State dir: {dir(ctx.state)}")
            
        return types.Content(role="model", parts=[types.Part(text="\n".join(info))])

    async def _run_async_impl(self, ctx, **kwargs):
        return types.Content(role="model", parts=[types.Part(text="Done")])

if __name__ == "__main__":
    agent = InspectAgent()
    # Test locally with a fake context
    from unittest.mock import MagicMock
    mock_ctx = MagicMock(spec=CallbackContext)
    mock_ctx.agent_name = "test"
    # Actually, better to just rely on the managed instance if I can.
