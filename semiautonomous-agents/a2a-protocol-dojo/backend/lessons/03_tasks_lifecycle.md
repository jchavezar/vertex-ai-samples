---
title: "Tasks & Lifecycle"
description: "The fundamental unit of work in A2A"
hasDemo: true
demoComponent: "TaskLifecycle"
---

# Tasks & Lifecycle

## What Is a Task?

A **Task** is the fundamental unit of work in A2A. When you send a message to an agent, it creates a task to track the work.

Each task has:
- A unique **task_id**
- A **state** that changes over time
- **Artifacts** containing the results

## Task State Machine

```
                    ┌──────────────┐
                    │  submitted   │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
               ┌───►│   working    │◄───┐
               │    └──────┬───────┘    │
               │           │            │
      ┌────────┴──────┐    │    ┌───────┴────────┐
      │ input-required │    │    │ auth-required  │
      └───────────────┘    │    └────────────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
       ┌──────▼──────┐ ┌──▼────┐ ┌─────▼─────┐
       │  completed   │ │failed │ │ canceled  │
       └─────────────┘ └───────┘ └───────────┘
```

### States

| State | Description | Terminal? |
|-------|-------------|-----------|
| `submitted` | Task received, not yet started | No |
| `working` | Agent is actively processing | No |
| `input-required` | Agent needs more info from user | No |
| `auth-required` | Agent needs authentication | No |
| `completed` | Successfully finished | **Yes** |
| `failed` | Error occurred | **Yes** |
| `canceled` | User canceled the task | **Yes** |

**Terminal states are immutable** — once a task is completed, failed, or canceled, it cannot change state again.

## Task Status Events

As a task progresses, the server sends `TaskStatusUpdateEvent` messages:

```python
from a2a.types import TaskStatusUpdateEvent, TaskStatus, TaskState

# Signal that work has started
event = TaskStatusUpdateEvent(
    task_id="task-123",
    context_id="ctx-456",
    final=False,  # Not terminal yet
    status=TaskStatus(state=TaskState.working),
)

# Signal completion
event = TaskStatusUpdateEvent(
    task_id="task-123",
    context_id="ctx-456",
    final=True,  # This is a terminal state
    status=TaskStatus(state=TaskState.completed),
)
```

The `final` flag tells the client whether to expect more events.

## Implementing Task Lifecycle (Server Side)

```python
class MyAgentExecutor(AgentExecutor):
    async def execute(self, context, event_queue):
        task_id = context.task_id
        ctx_id = context.context_id

        # 1. Signal: working
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=task_id,
                context_id=ctx_id,
                final=False,
                status=TaskStatus(state=TaskState.working),
            )
        )

        # 2. Do the actual work...
        result = await self.process(context.get_user_input())

        # 3. Send the result as an artifact
        await event_queue.enqueue_event(
            TaskArtifactUpdateEvent(
                task_id=task_id,
                context_id=ctx_id,
                artifact=Artifact(
                    artifact_id=str(uuid.uuid4()),
                    parts=[TextPart(text=result)],
                ),
                last_chunk=True,
            )
        )

        # 4. Signal: completed
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=task_id,
                context_id=ctx_id,
                final=True,
                status=TaskStatus(state=TaskState.completed),
            )
        )
```

## Checking Task Status (Client Side)

```python
# Using JSON-RPC
request = {
    "jsonrpc": "2.0",
    "id": "1",
    "method": "tasks/get",
    "params": {"id": "task-123"}
}
```

## Try It!

Click "Create Task" below to watch a simulated task progress through the state machine in real-time. You'll see each state transition as it happens.
