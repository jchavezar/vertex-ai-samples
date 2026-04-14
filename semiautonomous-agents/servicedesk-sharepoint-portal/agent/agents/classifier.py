"""
Intent Classifier Agent.
Fast classification using gemini-2.5-flash with thinking_budget=0.
"""
import os
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent
from google.adk.planners import BuiltInPlanner
from google.genai.types import ThinkingConfig


class Intent(str, Enum):
    """Possible routing intents."""
    DISCOVERY = "DISCOVERY"
    SERVICENOW = "SERVICENOW"


class IntentResult(BaseModel):
    """Structured output for intent classification."""
    intent: Intent = Field(description="The classified intent")
    confidence: float = Field(description="Confidence score 0.0-1.0", ge=0.0, le=1.0)
    reasoning: str = Field(description="Brief explanation for the classification")


CLASSIFIER_INSTRUCTION = """You are an intelligent intent classifier. Analyze the user's message and classify it into ONE of these intents:

**DISCOVERY** - Use for ANY information lookup, questions, or searches:
- "What are the Ducati issues?" → DISCOVERY (looking up information about Ducati)
- "Find quarterly earnings" → DISCOVERY
- "List all problems with X" → DISCOVERY (asking for information, not creating a ticket)
- "Tell me about Y" → DISCOVERY
- Any question asking for data, documents, reports, or information
- Searching enterprise datastores or SharePoint

**SERVICENOW** - Use ONLY for explicit ticket/incident ACTIONS:
- "Create a ticket for..." → SERVICENOW
- "Open an incident about..." → SERVICENOW
- "Submit a change request" → SERVICENOW
- "Report this issue" (explicitly asking to create a record) → SERVICENOW
- "Find my tickets" or "List my incidents" → SERVICENOW (querying ITSM system)

IMPORTANT: If the user is ASKING about something (issues, problems, information) - use DISCOVERY.
Only use SERVICENOW when they want to CREATE, SUBMIT, or MANAGE tickets/incidents explicitly.

Respond with JSON:
- intent: "DISCOVERY" or "SERVICENOW"
- confidence: 0.0-1.0
- reasoning: Brief explanation
"""


class IntentClassifier:
    """
    Fast intent classifier using gemini-2.5-flash with thinking_budget=0.
    Designed for minimal latency (~100-200ms).
    """

    def __init__(self, model: str = "gemini-2.5-flash"):
        self.model = model
        self._agent: Optional[LlmAgent] = None

    @property
    def agent(self) -> LlmAgent:
        """Lazy initialization of the classifier agent."""
        if self._agent is None:
            self._agent = LlmAgent(
                name="IntentClassifier",
                model=self.model,
                instruction=CLASSIFIER_INSTRUCTION,
                output_schema=IntentResult,
                output_key="intent_result",
                planner=BuiltInPlanner(
                    thinking_config=ThinkingConfig(
                        thinking_budget=0  # No thinking = fastest response
                    )
                )
            )
        return self._agent

    async def classify(self, user_input: str, session_state: dict) -> IntentResult:
        """
        Classify user intent using direct Gemini API call.
        Optimized for speed with thinking_budget=0.

        Args:
            user_input: The user's message
            session_state: Current session state (for context)

        Returns:
            IntentResult with intent, confidence, and reasoning
        """
        from google.genai import Client
        from google.genai import types as genai_types
        import json
        import os

        # Check if this looks like a follow-up question
        current_route = session_state.get("current_route")
        history = session_state.get("conversation_history", [])

        # Quick heuristics for obvious follow-ups
        follow_up_phrases = [
            "how much", "what about", "tell me more", "and the", "and what",
            "did you say", "you mentioned", "can you", "more details",
            "explain", "elaborate", "what else", "anything else"
        ]
        input_lower = user_input.lower()

        # If it's a short follow-up question and we have history, stick with current route
        if current_route and history and len(user_input.split()) < 10:
            if any(phrase in input_lower for phrase in follow_up_phrases):
                return IntentResult(
                    intent=Intent(current_route),
                    confidence=0.9,
                    reasoning="Follow-up question detected, maintaining current route"
                )

        client = Client(
            vertexai=True,
            project=os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos"),
            location=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
        )

        # Include recent conversation context for smarter classification
        context_hint = ""
        if history:
            recent = history[-4:]  # Last 2 exchanges
            context_lines = [f"- {h['role']}: {h['content'][:100]}..." for h in recent]
            context_hint = f"\n\nRecent conversation:\n" + "\n".join(context_lines)

        prompt = f"""Classify this user message into ONE intent. Be smart about understanding what they want.

User message: "{user_input}"{context_hint}

Rules:
- If asking ABOUT something (issues, problems, data, information) → DISCOVERY
- If wanting to CREATE/SUBMIT a ticket or incident → SERVICENOW
- "List issues about X" = DISCOVERY (looking up info)
- "List my incidents" = SERVICENOW (querying ITSM)
- "What are the problems with X" = DISCOVERY
- "Report an issue" or "Create a ticket" = SERVICENOW
- Follow-up questions (asking for more details, clarification) should maintain the previous topic's intent

Respond with JSON only:
{{"intent": "DISCOVERY" or "SERVICENOW", "confidence": 0.0-1.0, "reasoning": "brief explanation"}}"""

        try:
            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    thinking_config=genai_types.ThinkingConfig(
                        thinking_budget=0
                    ),
                    response_mime_type="application/json",
                )
            )

            # Parse JSON response
            result_text = response.text.strip()
            if result_text.startswith("```"):
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]

            data = json.loads(result_text)
            intent_str = data.get("intent", "DISCOVERY").upper()
            intent = Intent.SERVICENOW if "SERVICENOW" in intent_str else Intent.DISCOVERY

            return IntentResult(
                intent=intent,
                confidence=float(data.get("confidence", 0.8)),
                reasoning=data.get("reasoning", "Classified by LLM")
            )

        except Exception as e:
            # Fallback to keyword-based classification
            input_lower = user_input.lower()
            servicenow_keywords = ["ticket", "incident", "create", "report", "problem", "issue", "fix", "broken"]

            if any(kw in input_lower for kw in servicenow_keywords):
                return IntentResult(
                    intent=Intent.SERVICENOW,
                    confidence=0.7,
                    reasoning=f"Keyword fallback (error: {str(e)[:50]})"
                )

            return IntentResult(
                intent=Intent.DISCOVERY,
                confidence=0.6,
                reasoning=f"Default fallback (error: {str(e)[:50]})"
            )


def is_hard_topic_switch(user_input: str, current_route: str) -> bool:
    """
    Detect if user is explicitly switching topics.
    Uses keyword heuristics for speed (no LLM call).
    """
    input_lower = user_input.lower()

    # Explicit switch signals
    switch_phrases = [
        "actually", "instead", "forget that", "new topic",
        "something else", "different question", "switch to"
    ]
    has_switch_signal = any(phrase in input_lower for phrase in switch_phrases)

    if not has_switch_signal:
        return False

    # Check if switching TO the other route
    if current_route == "SERVICENOW":
        discovery_keywords = ["search", "find", "document", "report", "financial", "quarterly"]
        return any(kw in input_lower for kw in discovery_keywords)
    else:
        servicenow_keywords = ["ticket", "incident", "create", "report issue", "problem"]
        return any(kw in input_lower for kw in servicenow_keywords)


def is_exit_signal(user_input: str) -> bool:
    """Detect if user wants to exit current flow."""
    exit_phrases = ["cancel", "stop", "exit", "quit", "start over", "reset", "nevermind"]
    input_lower = user_input.lower()
    return any(phrase in input_lower for phrase in exit_phrases)
