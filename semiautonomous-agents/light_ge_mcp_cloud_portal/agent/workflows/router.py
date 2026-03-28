"""
Dynamic Workflow Router.
Uses ADK 2.0 @node pattern with session state for conversation stickiness.
"""
import os
import sys
import logging
import asyncio
from typing import Optional, AsyncGenerator, Any
from dataclasses import dataclass, field
from enum import Enum

from google.adk.agents import BaseAgent, LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from agents.classifier import IntentClassifier, Intent, is_hard_topic_switch, is_exit_signal
from agents.servicenow_agent import create_servicenow_agent
from tools.discovery_engine import DiscoveryEngineClient, SearchResult

logger = logging.getLogger(__name__)


@dataclass
class RouterState:
    """State maintained across conversation turns."""
    current_route: Optional[str] = None
    turn_count: int = 0
    last_intent_confidence: float = 0.0
    conversation_history: list = field(default_factory=list)  # Track history for context


@dataclass
class RouterConfig:
    """Configuration for the router."""
    classifier_model: str = "gemini-2.5-flash"
    servicenow_model: str = "gemini-2.5-flash"
    reclassify_threshold: float = 0.7  # Reclassify if confidence below this
    max_sticky_turns: int = 10  # Force reclassify after this many turns


class RouterWorkflow:
    """
    Dynamic Workflow Router implementing conversation stickiness.

    Flow:
    1. Check if in active route (stickiness)
    2. If not, or topic switch detected, classify intent
    3. Route to appropriate handler
    4. Maintain state for follow-ups
    """

    def __init__(
        self,
        config: Optional[RouterConfig] = None,
        user_token: Optional[str] = None,
    ):
        self.config = config or RouterConfig()
        self.user_token = user_token

        # Initialize components
        self.classifier = IntentClassifier(model=self.config.classifier_model)
        self.discovery_client = DiscoveryEngineClient()
        self._servicenow_agent: Optional[LlmAgent] = None
        self._session_service = InMemorySessionService()

    @property
    def servicenow_agent(self) -> LlmAgent:
        """Lazy initialization of ServiceNow agent."""
        if self._servicenow_agent is None:
            self._servicenow_agent = create_servicenow_agent(
                user_token=self.user_token,
                model=self.config.servicenow_model
            )
        return self._servicenow_agent

    def _get_router_state(self, session_state: dict) -> RouterState:
        """Extract router state from session."""
        return RouterState(
            current_route=session_state.get("current_route"),
            turn_count=session_state.get("turn_count", 0),
            last_intent_confidence=session_state.get("last_intent_confidence", 0.0),
            conversation_history=session_state.get("conversation_history", [])
        )

    def _update_router_state(self, session_state: dict, state: RouterState):
        """Update router state in session."""
        session_state["current_route"] = state.current_route
        session_state["turn_count"] = state.turn_count
        session_state["last_intent_confidence"] = state.last_intent_confidence
        session_state["conversation_history"] = state.conversation_history

    def _build_context_prompt(self, history: list, current_query: str) -> str:
        """Build a context-aware query from conversation history."""
        if not history:
            return current_query

        # Include recent history for context (last 5 exchanges)
        recent = history[-10:]  # Last 5 user+assistant pairs
        context_parts = []
        for entry in recent:
            role = entry.get("role", "user")
            content = entry.get("content", "")[:500]  # Truncate long messages
            context_parts.append(f"{role.upper()}: {content}")

        context = "\n".join(context_parts)
        return f"""Previous conversation:
{context}

Current question: {current_query}

Please answer the current question, taking into account the conversation history above."""

    def _is_follow_up(self, user_input: str, history: list) -> bool:
        """Detect if user is asking a follow-up question."""
        if not history:
            return False

        input_lower = user_input.lower()

        # Explicit follow-up phrases
        follow_up_phrases = [
            "how much", "what about", "tell me more", "and the", "and what",
            "did you say", "you mentioned", "can you", "more details",
            "explain", "elaborate", "what else", "anything else", "more info",
            "why", "when", "where", "who", "which", "could you",
            "again", "repeat", "clarify", "summary", "summarize"
        ]

        # Short messages with follow-up phrases are likely follow-ups
        if len(user_input.split()) < 12:
            if any(phrase in input_lower for phrase in follow_up_phrases):
                return True

        # References to previous response ("you said", "as you mentioned", etc.)
        reference_phrases = ["you said", "you mentioned", "as mentioned", "from before", "earlier"]
        if any(phrase in input_lower for phrase in reference_phrases):
            return True

        return False

    async def _should_reclassify(
        self,
        user_input: str,
        router_state: RouterState
    ) -> bool:
        """
        Determine if we should reclassify intent.

        Returns True if:
        - No active route
        - Explicit topic switch detected
        - Exit signal detected
        - Too many turns without reclassification
        - Low confidence on last classification

        Returns False if:
        - User is asking a follow-up question
        """
        # No active route - must classify
        if not router_state.current_route:
            return True

        # Exit signal - reset route
        if is_exit_signal(user_input):
            return True

        # Follow-up questions should NOT reclassify
        if self._is_follow_up(user_input, router_state.conversation_history):
            logger.info(f"[Router] Detected follow-up question, skipping classification")
            return False

        # Explicit topic switch
        if is_hard_topic_switch(user_input, router_state.current_route):
            return True

        # Too many turns - periodic reclassification
        if router_state.turn_count >= self.config.max_sticky_turns:
            return True

        # Low confidence - reclassify
        if router_state.last_intent_confidence < self.config.reclassify_threshold:
            return True

        return False

    async def route(
        self,
        user_input: str,
        session_state: dict,
    ) -> AsyncGenerator[str, None]:
        """
        Main routing logic.

        Args:
            user_input: User's message
            session_state: Mutable session state dict

        Yields:
            Response chunks
        """
        router_state = self._get_router_state(session_state)
        router_state.turn_count += 1

        # Check for exit
        if is_exit_signal(user_input):
            router_state.current_route = None
            router_state.turn_count = 0
            self._update_router_state(session_state, router_state)
            yield "Conversation reset. How can I help you?"
            return

        # Determine if we need to classify
        should_classify = await self._should_reclassify(user_input, router_state)

        if should_classify:
            # Classify intent
            logger.info(f"[Router] Classifying intent for: {user_input[:50]}...")
            intent_result = await self.classifier.classify(user_input, session_state)

            router_state.current_route = intent_result.intent.value
            router_state.last_intent_confidence = intent_result.confidence
            router_state.turn_count = 1  # Reset turn count on new route

            logger.info(
                f"[Router] Classified as {intent_result.intent.value} "
                f"(confidence: {intent_result.confidence:.2f})"
            )
        else:
            logger.info(
                f"[Router] Sticking with route: {router_state.current_route} "
                f"(turn {router_state.turn_count})"
            )

        # Route to appropriate handler and collect response
        full_response = ""
        if router_state.current_route == Intent.DISCOVERY.value:
            async for chunk in self._handle_discovery(user_input, session_state, router_state.conversation_history):
                full_response += chunk
                yield chunk
        else:
            async for chunk in self._handle_servicenow(user_input, session_state, router_state.conversation_history):
                full_response += chunk
                yield chunk

        # Update conversation history
        router_state.conversation_history.append({"role": "user", "content": user_input})
        router_state.conversation_history.append({"role": "assistant", "content": full_response})

        # Keep history bounded (last 20 messages)
        if len(router_state.conversation_history) > 20:
            router_state.conversation_history = router_state.conversation_history[-20:]

        # Update state
        self._update_router_state(session_state, router_state)

    async def _handle_discovery(
        self,
        user_input: str,
        session_state: dict,
        history: list
    ) -> AsyncGenerator[str, None]:
        """Handle Discovery Engine queries with conversation context."""
        logger.info(f"[Router] Routing to Discovery Engine")

        try:
            # Build context-aware query if there's history
            query = self._build_context_prompt(history, user_input) if history else user_input

            # Use streaming search
            async for chunk in self.discovery_client.stream_search(
                query=query,
                user_token=session_state.get("USER_TOKEN")
            ):
                yield chunk
        except Exception as e:
            logger.error(f"[Router] Discovery error: {e}")
            yield f"I encountered an error searching: {str(e)}"

    async def _handle_servicenow(
        self,
        user_input: str,
        session_state: dict,
        history: list
    ) -> AsyncGenerator[str, None]:
        """Handle ServiceNow requests with conversation context."""
        logger.info(f"[Router] Routing to ServiceNow Agent")

        try:
            runner = Runner(
                app_name="servicenow_handler",
                agent=self.servicenow_agent,
                session_service=self._session_service
            )

            # Get or create session
            session_id = session_state.get("servicenow_session_id")
            if not session_id:
                session = await self._session_service.create_session(
                    app_name="servicenow_handler",
                    user_id="default"
                )
                session_id = session.id
                session_state["servicenow_session_id"] = session_id

            # Inject user token and conversation history into session state
            try:
                session = await self._session_service.get_session(
                    app_name="servicenow_handler",
                    user_id="default",
                    session_id=session_id
                )
                if session:
                    if session_state.get("USER_TOKEN"):
                        session.state["USER_TOKEN"] = session_state["USER_TOKEN"]
                    session.state["conversation_history"] = history
            except Exception:
                pass

            # Build context-aware message
            context_message = self._build_context_prompt(history, user_input) if history else user_input

            msg = genai_types.Content(
                role="user",
                parts=[genai_types.Part.from_text(text=context_message)]
            )

            async for event in runner.run_async(
                user_id="default",
                session_id=session_id,
                new_message=msg
            ):
                # Extract text from event
                if hasattr(event, "content") and event.content:
                    content = event.content
                    if hasattr(content, "parts"):
                        for part in content.parts:
                            if hasattr(part, "text") and part.text:
                                # Skip thoughts
                                if not getattr(part, "thought", False):
                                    yield part.text

        except Exception as e:
            logger.error(f"[Router] ServiceNow error: {e}")
            yield f"I encountered an error with ServiceNow: {str(e)}"


class RouterAgent(BaseAgent):
    """
    ADK BaseAgent wrapper for the RouterWorkflow.
    Enables integration with Agent Engine deployment.
    """

    # Declare workflow as a Pydantic field
    workflow: RouterWorkflow = None

    model_config = {"arbitrary_types_allowed": True}

    def __init__(
        self,
        name: str = "RouterAgent",
        config: Optional[RouterConfig] = None,
        **kwargs
    ):
        workflow = RouterWorkflow(config=config)
        super().__init__(
            name=name,
            description="Routes requests to Discovery or ServiceNow",
            workflow=workflow,
            **kwargs
        )

    async def _run_async_impl(
        self,
        ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """Implement BaseAgent interface."""
        # Extract user input from context
        user_input = ""
        if ctx.user_content and ctx.user_content.parts:
            for part in ctx.user_content.parts:
                if hasattr(part, "text"):
                    user_input = part.text
                    break

        if not user_input:
            yield Event(
                invocation_id=ctx.invocation_id,
                author=self.name,
                content=genai_types.Content(
                    role="model",
                    parts=[genai_types.Part.from_text(text="I didn't receive any input.")]
                )
            )
            return

        # Get session state
        session_state = dict(ctx.session.state) if ctx.session else {}

        # Route and stream response
        full_response = ""
        async for chunk in self.workflow.route(user_input, session_state):
            full_response += chunk

        # Update session state
        if ctx.session:
            for key, value in session_state.items():
                ctx.session.state[key] = value

        # Yield final response
        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            content=genai_types.Content(
                role="model",
                parts=[genai_types.Part.from_text(text=full_response)]
            )
        )


# Factory function for Agent Engine deployment
def create_router_agent(
    user_token: Optional[str] = None,
    config: Optional[RouterConfig] = None
) -> RouterAgent:
    """Create a RouterAgent for deployment."""
    agent = RouterAgent(config=config)
    if user_token:
        agent.workflow.user_token = user_token
    return agent
