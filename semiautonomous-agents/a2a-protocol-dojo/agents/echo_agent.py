"""
Echo Agent — A2A Protocol Dojo.

Simple A2A agent that echoes messages back. No API keys needed.
Port: 8001
"""

import asyncio
import uuid

import uvicorn
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
    Message,
    Part,
    Role,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
    TaskArtifactUpdateEvent,
    TextPart,
)


class EchoAgentExecutor(AgentExecutor):
    """Echoes user messages back with metadata."""

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

        # Simulate brief processing
        await asyncio.sleep(0.5)

        # Send artifact with echoed text
        echo_text = f"Echo: {user_text}"
        await event_queue.enqueue_event(
            TaskArtifactUpdateEvent(
                task_id=task_id,
                context_id=context_id,
                artifact=Artifact(
                    artifact_id=str(uuid.uuid4()),
                    parts=[TextPart(text=echo_text)],
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


# Agent Card
agent_card = AgentCard(
    name="echo_agent",
    description="A simple echo agent that repeats your messages back. Used for learning the A2A protocol basics.",
    url="http://localhost:8001",
    version="1.0.0",
    capabilities=AgentCapabilities(streaming=True),
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    skills=[
        AgentSkill(
            id="echo",
            name="Echo",
            description="Echoes back the user's message with an 'Echo:' prefix",
            tags=["echo", "test", "demo"],
            examples=["Hello, echo agent!", "What is A2A?"],
        ),
    ],
)

# Wire up
task_store = InMemoryTaskStore()
handler = DefaultRequestHandler(
    agent_executor=EchoAgentExecutor(),
    task_store=task_store,
)

app = A2AStarletteApplication(
    agent_card=agent_card,
    http_handler=handler,
)

if __name__ == "__main__":
    uvicorn.run(app.build(), host="0.0.0.0", port=8001)
