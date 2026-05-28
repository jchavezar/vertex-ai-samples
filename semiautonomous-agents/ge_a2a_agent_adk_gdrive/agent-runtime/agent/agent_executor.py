"""ADK LlmAgent -> A2A AgentExecutor bridge.

Inspects every Google-identity hint that survives the Vertex AI -> AE
proxy chain and pushes a one-line identity summary into ADK session
state under `caller_identity`. The LlmAgent reads it when asked
"whoami". Useful for proving exactly what identity (SA vs. user)
reaches the executor.
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


_REDACT_HEADERS = {"authorization", "cookie", "proxy-authorization", "x-goog-iam-authorization-token"}


def _redact(name: str, value: str) -> str:
    if name.lower() in _REDACT_HEADERS:
        return f"<redacted len={len(value)}>"
    if len(value) > 256:
        return value[:256] + f"...<truncated total={len(value)}>"
    return value


def _safe_dump(obj: Any, depth: int = 0, max_depth: int = 4) -> Any:
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if depth >= max_depth:
        return f"<truncated depth={depth} type={type(obj).__name__}>"
    if isinstance(obj, dict):
        return {str(k): _safe_dump(v, depth + 1, max_depth) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_safe_dump(v, depth + 1, max_depth) for v in obj]
    if hasattr(obj, "model_dump"):
        try:
            return _safe_dump(obj.model_dump(mode="json"), depth + 1, max_depth)
        except Exception:
            pass
    if hasattr(obj, "__dict__"):
        return {
            k: _safe_dump(v, depth + 1, max_depth)
            for k, v in vars(obj).items()
            if not k.startswith("_")
        }
    return repr(obj)


def _caller_identity(context: RequestContext) -> str:
    cc = context.call_context
    state = (cc.state if cc and cc.state else {}) or {}
    headers = state.get("headers") or {}

    auth = headers.get("authorization") or headers.get("Authorization") or ""
    token = auth[7:] if auth.lower().startswith("bearer ") else auth
    claims = _decode_jwt_payload(token) if token else {}

    all_headers_str = "\n".join(
        f"    {k}: {_redact(k, str(v))}" for k, v in sorted(headers.items())
    ) or "    (none)"

    other_state_keys = sorted(k for k in state.keys() if k != "headers")
    state_str = "\n".join(
        f"    {k}: {_redact(k, str(state[k]))}" for k in other_state_keys
    ) or "    (none)"

    msg_dump = _safe_dump(getattr(context, "message", None))
    cfg_dump = _safe_dump(getattr(context, "configuration", None))
    ctx_attrs = {
        k: _safe_dump(getattr(context, k, None))
        for k in ("task_id", "context_id", "current_task", "related_tasks", "metadata")
        if hasattr(context, k)
    }

    return (
        f"caller_identity:\n"
        f"  jwt_claims:\n"
        f"    iss={claims.get('iss', '?')}\n"
        f"    aud={claims.get('aud', '?')}\n"
        f"    sub={claims.get('sub', '?')}\n"
        f"    email={claims.get('email', '(not present)')}\n"
        f"    azp={claims.get('azp', '?')}\n"
        f"    all_claims={json.dumps(claims)}\n"
        f"  all_headers:\n{all_headers_str}\n"
        f"  call_context.state_extras:\n{state_str}\n"
        f"  request.message={json.dumps(msg_dump, default=str)}\n"
        f"  request.configuration={json.dumps(cfg_dump, default=str)}\n"
        f"  request.context_attrs={json.dumps(ctx_attrs, default=str)}"
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
