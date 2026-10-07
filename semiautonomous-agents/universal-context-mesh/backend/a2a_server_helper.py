"""
A2A Protocol JSON-RPC 2.0 FastAPI Server Builder (`a2a_server_helper.py`).
Exposes standard `/.well-known/agent-card.json` using `a2a.types.AgentCard`
and handles JSON-RPC 2.0 `message/send` and `tasks/send` invocations for Google ADK agents.
"""

import json
import uuid
from typing import Any, Callable, Coroutine, Dict
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from a2a.types import AgentCard

from backend.context_bridge import emit_remote_telemetry


def create_a2a_fastapi_app(
    agent_card: AgentCard,
    turn_handler: Callable[[str, str, str], Coroutine[Any, Any, Dict[str, Any]]],
    port: int,
    clear_handler: Callable[[], None] = None,
) -> FastAPI:
    """
    Creates a compliant A2A Protocol JSON-RPC 2.0 FastAPI server for an ADK Agent Runtime.
    - `GET /.well-known/agent-card.json`: Returns the official A2A AgentCard JSON.
    - `POST /`: Processes A2A JSON-RPC 2.0 requests (`message/send`, `tasks/send`).
    - `POST /clear_sessions`: Resets local ADK InMemorySessionService cache.
    """
    app = FastAPI(title=f"A2A Runtime: {agent_card.name}", version=agent_card.version)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/.well-known/agent-card.json")
    async def get_agent_card() -> Dict[str, Any]:
        from google.protobuf.json_format import MessageToDict
        if hasattr(agent_card, "DESCRIPTOR"):
            data = MessageToDict(agent_card)
        elif hasattr(agent_card, "model_dump"):
            data = agent_card.model_dump(mode="json", exclude_none=True)
        else:
            data = dict(agent_card)
        data["url"] = f"http://localhost:{port}"
        return data

    @app.get("/health")
    async def health() -> Dict[str, Any]:
        return {"status": "online", "agent": agent_card.name, "port": port, "protocol": "A2A JSON-RPC 2.0"}

    @app.post("/clear_sessions")
    async def clear_sessions_endpoint() -> Dict[str, Any]:
        if clear_handler:
            clear_handler()
        return {"status": "cleared", "agent": agent_card.name}

    @app.post("/")
    async def handle_jsonrpc(request: Request) -> Dict[str, Any]:
        body = await request.json()
        rpc_id = body.get("id", f"rpc-{uuid.uuid4().hex[:8]}")
        method = body.get("method", "message/send")
        params = body.get("params", {})

        # Extract text payload from A2A JSON-RPC message parts
        raw_text = ""
        msg_obj = params.get("message", {})
        parts = msg_obj.get("parts", [])
        for part in parts:
            if isinstance(part, dict) and part.get("text"):
                raw_text += part["text"]

        user_id = "alex.rivera@enterprise.io"
        session_id = f"a2a-{uuid.uuid4().hex[:6]}"
        user_message = raw_text

        try:
            parsed = json.loads(raw_text)
            if isinstance(parsed, dict) and "message" in parsed:
                user_id = parsed.get("user_id", user_id)
                session_id = parsed.get("session_id", session_id)
                user_message = parsed["message"]
        except Exception:
            pass

        task_id = f"task-{uuid.uuid4().hex[:8]}"

        await emit_remote_telemetry(
            "A2A_JSONRPC_RECEIVE",
            {
                "agent": agent_card.name,
                "port": port,
                "method": method,
                "task_id": task_id,
                "user_id": user_id,
                "session_id": session_id,
                "summary": f"A2A Server `{agent_card.name}` (:{port}) received JSON-RPC `{method}` task `{task_id}`",
            },
        )

        # Run ADK agent turn with Universal Context injection
        result_dict = await turn_handler(user_id, session_id, user_message)
        artifact_text = json.dumps(result_dict)

        return {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "result": {
                "id": task_id,
                "contextId": session_id,
                "status": {
                    "state": "completed",
                    "message": {
                        "messageId": f"msg-{uuid.uuid4().hex[:8]}",
                        "role": "agent",
                        "parts": [{"kind": "text", "text": artifact_text}],
                    },
                },
                "artifacts": [
                    {
                        "artifactId": f"art-{uuid.uuid4().hex[:8]}",
                        "name": f"{agent_card.name}_output",
                        "parts": [{"kind": "text", "text": artifact_text}],
                    }
                ],
            },
        }

    return app
