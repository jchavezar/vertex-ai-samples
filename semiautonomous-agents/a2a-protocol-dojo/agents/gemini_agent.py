"""
Gemini Agent — A2A Protocol Dojo.

A2A agent powered by Gemini 2.5 Flash with streaming support.
Falls back to mock mode when no GCP project is configured.
Port: 8002
"""

import asyncio
import os
import uuid
from pathlib import Path

import uvicorn
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from a2a.server.agent_execution import AgentExecutor
from a2a.server.events import EventQueue
from a2a.server.request_handlers.default_request_handler import (
    DefaultRequestHandler,
    RequestContext,
)
from a2a.server.apps.jsonrpc.starlette_app import A2AStarletteApplication
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCard,
    AgentCapabilities,
    AgentSkill,
    Artifact,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
    TaskArtifactUpdateEvent,
    TextPart,
)

PROJECT_ID = os.environ.get("PROJECT_ID", "")
USE_GEMINI = bool(PROJECT_ID)

if USE_GEMINI:
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
    os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
    from google import genai

    client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=os.environ.get("LOCATION", "us-central1"),
    )

MOCK_RESPONSES = [
    "The A2A protocol enables seamless agent-to-agent communication. ",
    "It's built on HTTP, JSON-RPC 2.0, and Server-Sent Events. ",
    "Each agent publishes an Agent Card at /.well-known/agent-card.json. ",
    "Tasks progress through states: submitted, working, completed. ",
    "This allows agents from different vendors to collaborate securely.",
]


class GeminiAgentExecutor(AgentExecutor):
    """Processes queries using Gemini or mock mode."""

    async def execute(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        user_text = context.get_user_input()
        task_id = context.task_id
        context_id = context.context_id

        # Signal: working
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=task_id,
                context_id=context_id,
                final=False,
                status=TaskStatus(state=TaskState.working),
            )
        )

        if USE_GEMINI:
            # Stream from Gemini
            full_text = ""
            response = client.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=user_text,
            )
            for chunk in response:
                if chunk.text:
                    full_text += chunk.text
                    await event_queue.enqueue_event(
                        TaskArtifactUpdateEvent(
                            task_id=task_id,
                            context_id=context_id,
                            artifact=Artifact(
                                artifact_id=str(uuid.uuid4()),
                                parts=[TextPart(text=full_text)],
                            ),
                            append=False,
                            last_chunk=False,
                        )
                    )
        else:
            # Mock streaming mode
            full_text = ""
            for sentence in MOCK_RESPONSES:
                for word in sentence.split():
                    full_text += word + " "
                    await asyncio.sleep(0.1)
                    await event_queue.enqueue_event(
                        TaskArtifactUpdateEvent(
                            task_id=task_id,
                            context_id=context_id,
                            artifact=Artifact(
                                artifact_id=str(uuid.uuid4()),
                                parts=[TextPart(text=full_text)],
                            ),
                            append=False,
                            last_chunk=False,
                        )
                    )

        # Final artifact
        await event_queue.enqueue_event(
            TaskArtifactUpdateEvent(
                task_id=task_id,
                context_id=context_id,
                artifact=Artifact(
                    artifact_id=str(uuid.uuid4()),
                    parts=[TextPart(text=full_text.strip())],
                ),
                last_chunk=True,
            )
        )

        # Signal: completed
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=task_id,
                context_id=context_id,
                final=True,
                status=TaskStatus(state=TaskState.completed),
            )
        )

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=context.task_id,
                context_id=context.context_id,
                final=True,
                status=TaskStatus(state=TaskState.canceled),
            )
        )


mode_label = "Gemini 2.5 Flash" if USE_GEMINI else "Mock Mode"
print(f"Gemini Agent starting in: {mode_label}")

agent_card = AgentCard(
    name="gemini_agent",
    description=f"AI assistant powered by {mode_label}. Answers questions with streaming responses.",
    url="http://localhost:8002",
    version="1.0.0",
    capabilities=AgentCapabilities(streaming=True),
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    skills=[
        AgentSkill(
            id="general_assistant",
            name="General Assistant",
            description="Answers general questions using Gemini AI",
            tags=["ai", "gemini", "assistant"],
            examples=["What is machine learning?", "Explain cloud computing"],
        ),
        AgentSkill(
            id="code_helper",
            name="Code Helper",
            description="Helps with coding questions and generates code snippets",
            tags=["code", "programming", "python"],
            examples=["Write a Python function to sort a list", "Explain async/await"],
        ),
    ],
)

task_store = InMemoryTaskStore()
handler = DefaultRequestHandler(
    agent_executor=GeminiAgentExecutor(),
    task_store=task_store,
)

app = A2AStarletteApplication(
    agent_card=agent_card,
    http_handler=handler,
)

if __name__ == "__main__":
    uvicorn.run(app.build(), host="0.0.0.0", port=8002)
