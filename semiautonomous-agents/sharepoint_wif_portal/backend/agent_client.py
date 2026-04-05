"""
Agent Engine Client for InsightComparator Agent.

Provides Agent Engine SDK integration for the backend.
Supports WIF token pass-through for user-level SharePoint ACL.

Version: 1.2.0
Date: 2026-04-05
"""
import os
from typing import Optional
import vertexai
from vertexai import agent_engines

PROJECT_ID = os.environ.get("PROJECT_ID", "sharepoint-wif-agent")
LOCATION = os.environ.get("LOCATION", "us-central1")
REASONING_ENGINE_RES = os.environ.get("REASONING_ENGINE_RES", "")


class AgentClient:
    """Client for interacting with the deployed InsightComparator agent."""

    def __init__(self):
        self._default_agent = None
        self._initialized = False

    def _ensure_initialized(self):
        """Initialize Vertex AI and load agent."""
        if not REASONING_ENGINE_RES:
            raise ValueError("REASONING_ENGINE_RES not set in environment")

        if not self._initialized:
            vertexai.init(project=PROJECT_ID, location=LOCATION)
            self._default_agent = agent_engines.get(REASONING_ENGINE_RES)
            self._initialized = True

        return self._default_agent

    def query(self, message: str, user_id: str = "portal_user", microsoft_jwt: Optional[str] = None) -> str:
        """
        Query the agent and return the full response.

        Args:
            message: User's query
            user_id: User identifier for session
            microsoft_jwt: Optional Microsoft Entra ID JWT for SharePoint ACL

        Returns:
            Complete response text
        """
        agent = self._ensure_initialized()

        # Create session with Microsoft JWT in state (same key agent expects)
        # Agent looks for token at "sharepointauth2" or "temp:sharepointauth2"
        session_state = None
        if microsoft_jwt:
            session_state = {"sharepointauth2": microsoft_jwt}
            print(f"[AgentClient] Passing JWT to session state (length: {len(microsoft_jwt)})")

        session = agent.create_session(user_id=user_id, state=session_state)
        session_id = session.get("id") if isinstance(session, dict) else session.id

        # Collect response
        response_text = ""
        for event in agent.stream_query(
            user_id=user_id,
            session_id=session_id,
            message=message
        ):
            if isinstance(event, dict):
                content = event.get("content", {})
                for part in content.get("parts", []):
                    if isinstance(part, dict) and part.get("text"):
                        response_text += part["text"]
            elif hasattr(event, 'content'):
                if hasattr(event.content, 'parts'):
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            response_text += part.text

        return response_text

    def stream_query(self, message: str, user_id: str = "portal_user"):
        """
        Stream query response from the agent.

        Args:
            message: User's query
            user_id: User identifier

        Yields:
            Text chunks as they arrive
        """
        self._ensure_initialized()

        # Create session
        session = self._agent.create_session(user_id=user_id)
        session_id = session.get("id") if isinstance(session, dict) else session.id

        for event in self._agent.stream_query(
            user_id=user_id,
            session_id=session_id,
            message=message
        ):
            text = ""
            if isinstance(event, dict):
                content = event.get("content", {})
                for part in content.get("parts", []):
                    if isinstance(part, dict) and part.get("text"):
                        text = part["text"]
            elif hasattr(event, 'content'):
                if hasattr(event.content, 'parts'):
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            text = part.text

            if text:
                yield text

    def get_info(self) -> dict:
        """Get agent information."""
        self._ensure_initialized()
        return {
            "name": getattr(self._agent, 'display_name', 'InsightComparator'),
            "resource": REASONING_ENGINE_RES,
            "project": PROJECT_ID,
            "location": LOCATION,
        }


# Singleton instance
_client: Optional[AgentClient] = None


def get_agent_client() -> AgentClient:
    """Get or create agent client instance."""
    global _client
    if _client is None:
        _client = AgentClient()
    return _client
