"""ADK LlmAgent -> A2A AgentExecutor bridge.

Decodes the Google-signed ID token the runtime presents to this container
and pushes a one-line identity summary into ADK session state under
`caller_identity`. The LlmAgent reads that line when asked "whoami".
"""

from __future__ import annotations

import base64
import json
import logging
import traceback
import uuid
from typing import Any

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import (
    Message,
    Part,
    Role,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
    TextPart,
)
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types


APP_NAME = "ge_a2a_auth_agent"
logger = logging.getLogger("ge_a2a_auth.executor")
logger.setLevel(logging.INFO)


def _decode_jwt_payload(jwt: str) -> dict[str, Any]:
    try:
        payload_b64 = jwt.split(".")[1]
        payload_b64 += "=" * (-len(payload_b64) % 4)
        return json.loads(base64.urlsafe_b64decode(payload_b64))
    except Exception:
        return {}


def _caller_identity(context: RequestContext) -> str:
    """Inspect every Google-identity hint in the request and return a single
    human-readable line."""
    cc = context.call_context
    headers = (cc.state.get("headers") if cc and cc.state else {}) or {}

    auth = headers.get("authorization") or headers.get("Authorization") or ""
    token = auth[7:] if auth.lower().startswith("bearer ") else auth
    claims = _decode_jwt_payload(token) if token else {}

    extra_ids = {
        k: v for k, v in headers.items()
        if k.lower().startswith(("x-goog-authenticated", "x-goog-iap", "x-goog-user"))
    }
    return (
        f"caller_identity:\n"
        f"  iss={claims.get('iss', '?')}\n"
        f"  aud={claims.get('aud', '?')}\n"
        f"  sub={claims.get('sub', '?')}\n"
        f"  email={claims.get('email', '(not present)')}\n"
        f"  azp={claims.get('azp', '?')}\n"
        f"  extra_identity_headers={extra_ids or '(none)'}"
    )


class AdkAgentExecutor(AgentExecutor):
    def __init__(self, agent: LlmAgent):
        self.agent = agent
        self._session_service = InMemorySessionService()
        self._runner = Runner(
            agent=self.agent,
            app_name=APP_NAME,
            session_service=self._session_service,
        )

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        task_id = context.task_id or str(uuid.uuid4())
        context_id = context.context_id or str(uuid.uuid4())
        try:
            user_text = _extract_user_text(context.message)
            caller = _caller_identity(context)
            logger.info("execute: text=%r task=%s ctx=%s", user_text, task_id, context_id)
            logger.info("execute: %s", caller.replace("\n", " | "))

            user_id = context_id
            initial_state = {"caller_identity": caller}
            session = await self._session_service.get_session(
                app_name=APP_NAME, user_id=user_id, session_id=context_id
            )
            if session is None:
                session = await self._session_service.create_session(
                    app_name=APP_NAME, user_id=user_id, session_id=context_id,
                    state=initial_state,
                )
            else:
                session.state["caller_identity"] = caller

            adk_input = genai_types.Content(
                role="user", parts=[genai_types.Part(text=user_text)]
            )

            final_text: list[str] = []
            async for event in self._runner.run_async(
                user_id=user_id, session_id=session.id, new_message=adk_input
            ):
                if event.is_final_response() and event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            final_text.append(part.text)

            reply = "".join(final_text) or "(empty)"
            logger.info("execute: ADK reply=%r", reply[:200])

            await event_queue.enqueue_event(
                Message(
                    messageId=str(uuid.uuid4()),
                    role=Role.agent,
                    parts=[Part(root=TextPart(text=reply))],
                    taskId=task_id,
                    contextId=context_id,
                )
            )
        except Exception as e:
            logger.error("execute failed: %s\n%s", e, traceback.format_exc())
            await event_queue.enqueue_event(
                TaskStatusUpdateEvent(
                    taskId=task_id,
                    contextId=context_id,
                    status=TaskStatus(
                        state=TaskState.failed,
                        message=Message(
                            messageId=str(uuid.uuid4()),
                            role=Role.agent,
                            parts=[Part(root=TextPart(text=f"executor error: {e}"))],
                            taskId=task_id,
                            contextId=context_id,
                        ),
                    ),
                    final=True,
                )
            )

    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        task_id = context.task_id or str(uuid.uuid4())
        context_id = context.context_id or str(uuid.uuid4())
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                taskId=task_id,
                contextId=context_id,
                status=TaskStatus(state=TaskState.canceled),
                final=True,
            )
        )


def _extract_user_text(message: Any) -> str:
    if message is None:
        return ""
    parts = getattr(message, "parts", []) or []
    out: list[str] = []
    for p in parts:
        root = getattr(p, "root", p)
        text = getattr(root, "text", None)
        if text:
            out.append(text)
    return "\n".join(out).strip()


def build_executor() -> AdkAgentExecutor:
    from .agent import root_agent
    return AdkAgentExecutor(agent=root_agent)
