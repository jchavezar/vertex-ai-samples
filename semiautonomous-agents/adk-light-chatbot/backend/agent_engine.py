"""
Google ADK Agent Engine
Provides an interface for initializing Google ADK Agents, managing InMemoryRunner sessions,
and streaming real-time responses with optional Google Search grounding.
"""

import os
import asyncio
from typing import AsyncGenerator, Dict, Any, List, Optional
from dotenv import load_dotenv

# Ensure environment is loaded from current or parent directories
load_dotenv()

# Configure Vertex AI environment with verified working defaults
if not os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT") == "jesusarguelles-sandbox":
    os.environ["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"

if not os.getenv("GOOGLE_CLOUD_LOCATION") or os.getenv("GOOGLE_CLOUD_LOCATION") == "global":
    os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"

from google.adk import Agent
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.genai import types

# Supported Models adhering to strict policy:
# gemini-2.5-flash, gemini-2.5-pro, gemini-3-flash-preview, gemini-3-pro-preview
SUPPORTED_MODELS = {
    "gemini-2.5-flash": {
        "id": "gemini-2.5-flash",
        "name": "Gemini 2.5 Flash",
        "badge": "Recomendado • Ultra Rápido",
        "description": "Modelo insignia para interacción conversacional en tiempo real, latencia mínima y alto rendimiento multimodal."
    },
    "gemini-2.5-pro": {
        "id": "gemini-2.5-pro",
        "name": "Gemini 2.5 Pro",
        "badge": "Razonamiento Complejo",
        "description": "Modelo insignia para problemas matemáticos, lógica avanzada, codificación profunda y análisis exhaustivo."
    },
    "gemini-3-flash-preview": {
        "id": "gemini-3-flash-preview",
        "name": "Gemini 3 Flash Preview",
        "badge": "Preview",
        "description": "Vista previa de la próxima generación Gemini 3 con arquitectura ultra eficiente."
    },
    "gemini-3-pro-preview": {
        "id": "gemini-3-pro-preview",
        "name": "Gemini 3 Pro Preview",
        "badge": "Preview Avanzado",
        "description": "Vista previa experimental de Gemini 3 Pro con capacidades ampliadas de razonamiento."
    }
}

DEFAULT_MODEL = "gemini-2.5-flash"

DEFAULT_INSTRUCTION = (
    "Eres un asistente virtual inteligente, empático, preciso y profesional creado con Google ADK (Agent Development Kit). "
    "Responde siempre de forma estructurada, clara y con un tono amable. "
    "Utiliza formato Markdown (negritas, listas, tablas y bloques de código) para hacer tus respuestas altamente legibles."
)


class ADKChatbotManager:
    """Manages the lifecycle of Google ADK Agents and Runner sessions."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        instruction: str = DEFAULT_INSTRUCTION,
        enable_search: bool = False,
        app_name: str = "adk_light_chatbot"
    ):
        self.model = model
        self.instruction = instruction
        self.enable_search = enable_search
        self.app_name = app_name
        self.runner: Optional[InMemoryRunner] = None
        self.agent: Optional[Agent] = None
        self._created_sessions: set = set()
        self._initialize_agent()

    def _initialize_agent(self):
        """Initializes or reinitializes the ADK Agent and Runner."""
        tools = [google_search] if self.enable_search else []

        self.agent = Agent(
            name="AdkAssistant",
            model=self.model,
            instruction=self.instruction,
            tools=tools
        )
        self.runner = InMemoryRunner(
            agent=self.agent,
            app_name=self.app_name
        )

    def update_configuration(
        self,
        model: Optional[str] = None,
        instruction: Optional[str] = None,
        enable_search: Optional[bool] = None
    ) -> bool:
        """Updates agent configuration if parameters change."""
        changed = False
        if model is not None and model != self.model:
            self.model = model
            changed = True
        if instruction is not None and instruction != self.instruction:
            self.instruction = instruction
            changed = True
        if enable_search is not None and enable_search != self.enable_search:
            self.enable_search = enable_search
            changed = True

        if changed:
            self._initialize_agent()
            self._created_sessions.clear()
        return changed

    async def ensure_session(self, user_id: str, session_id: str):
        """Ensures that a session exists in the ADK SessionService."""
        key = f"{user_id}:{session_id}"
        if key not in self._created_sessions:
            try:
                await self.runner.session_service.create_session(
                    app_name=self.app_name,
                    user_id=user_id,
                    session_id=session_id
                )
            except Exception:
                pass
            self._created_sessions.add(key)

    async def stream_turn(
        self,
        user_id: str,
        session_id: str,
        user_message: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Sends a user message to the ADK agent and yields real-time events.
        """
        await self.ensure_session(user_id, session_id)

        new_message = types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_message)]
        )

        try:
            async for event in self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=new_message
            ):
                # 1. Process Content Parts (Text and Tool Calls)
                if hasattr(event, "content") and event.content:
                    for part in event.content.parts:
                        # Stream text chunks
                        if getattr(part, "text", None):
                            yield {
                                "type": "text",
                                "content": part.text
                            }
                        
                        # Report Tool / Function Calls
                        if getattr(part, "function_call", None):
                            fc = part.function_call
                            yield {
                                "type": "tool_call",
                                "name": getattr(fc, "name", "unknown_tool"),
                                "args": getattr(fc, "args", {})
                            }

                # 2. Process Grounding / Search Metadata if available
                if hasattr(event, "grounding_metadata") and event.grounding_metadata:
                    gm = event.grounding_metadata
                    queries = getattr(gm, "web_search_queries", []) or []
                    chunks = getattr(gm, "grounding_chunks", []) or []
                    sources = []
                    for c in chunks:
                        web = getattr(c, "web", None)
                        if web:
                            sources.append({
                                "title": getattr(web, "title", "Web Source"),
                                "uri": getattr(web, "uri", "")
                            })
                    if queries or sources:
                        yield {
                            "type": "grounding",
                            "queries": list(queries),
                            "sources": sources
                        }

        except Exception as exc:
            yield {
                "type": "error",
                "message": f"Error en ADK: {str(exc)}"
            }
