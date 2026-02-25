from typing import Any, Optional

from google.adk.plugins.base_plugin import BasePlugin
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.callback_context import CallbackContext
from google.adk.events.event import Event
from google.genai import types

class AgentEngineInterceptorPlugin(BasePlugin):
    """
    A custom plugin that intercepts payloads and context exactly as they
    are provided by the Agent Engine (A2A) integration into ADK.
    """

    def __init__(self):
      super().__init__(name="agent_engine_interceptor")

    async def on_user_message_callback(
        self,
        *,
        invocation_context: InvocationContext,
        user_message: types.Content,
    ) -> Optional[types.Content]:
        """
        Intercepts the incoming request right as it maps from the Agent Engine A2A RequestContext.
        """
        # 1. Extract User ID (Mapped from request.call_context.user.user_name)
        user_id = invocation_context.user_id

        # 2. Extract Session ID (Mapped from request.context_id)
        session_id = invocation_context.session.id

        # 3. Extract Text payload (Mapped from request.message.parts)
        text_payload = ""
        for part in user_message.parts:
          if part.text:
            text_payload += part.text

        print("="*50)
        print("[A2A Interceptor] 📥 INCOMING PAYLOAD FROM AGENT ENGINE")
        print(f"Session ID: {session_id}")
        print(f"User ID:    {user_id}")
        print(f"Text Input: {text_payload}")
        print(f"App Name:   {invocation_context.app_name}")
        print("="*50)

        # You can also modify the user_message here or return None to proceed normally
        return None

    async def before_run_callback(
        self, *, invocation_context: InvocationContext
    ) -> Optional[Event]:
        """
        Executed before the ADK runner starts, giving you access to the session state.
        """
        state = invocation_context.session.state
        print(f"[A2A Interceptor] 🗄️ Session State before run: {state}")
        return None

    async def on_event_callback(
        self, *, invocation_context: InvocationContext, event: Event
    ) -> Optional[Event]:
        """
        Intercepts the outgoing events that will be converted back to Agent Engine
        TaskUpdateEvents (A2A protocol).
        """
        print(f"[A2A Interceptor] 📤 OUTGOING EVENT TO AGENT ENGINE FROM {event.author}")
        
        # If the event contains grounding metadata, you can inspect it here
        # Example: inspect grounding attribution from LLM Responses
        if hasattr(event, "content") and event.content and hasattr(event.content, "parts"):
            for part in event.content.parts:
                # You can extract grounding, text, or any rich artifact being sent back
                if part.text:
                    print(f"  -> Sending Text: {part.text[:50]}...")
                # Grounding metadata (if populated by models) would be attached to the parts or model response metadata.

        return None
