"""
Universal Context HTTP & In-Memory Bridge (`context_bridge.py`).
Allows standalone A2A Agent Runtimes (ports 8011, 8012, 8013) to read and write
to the Universal Context & Memory Bank Hub (port 8010) with zero latency or drift.
"""

import os
from typing import Any, Dict, List, Optional
import httpx

ORCHESTRATOR_URL = os.environ.get("ORCHESTRATOR_URL", "http://localhost:8010")


async def fetch_universal_injection(user_id: str, agent_name: str, session_id: str) -> Dict[str, Any]:
    """Fetches the live Universal Context prompt injection from the Hub."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{ORCHESTRATOR_URL}/api/context/{user_id}/injection",
                params={"agent_name": agent_name, "session_id": session_id},
            )
            if resp.status_code == 200:
                return resp.json()
    except Exception as e:
        print(f"[ContextBridge] HTTP fallback to local engine for fetch_universal_injection: {e}")

    from backend.universal_memory_engine import context_engine
    return await context_engine.build_universal_context_injection(user_id, agent_name, session_id)


async def push_universal_state_update(
    user_id: str,
    namespace_key: str,
    updates: Dict[str, Any],
    source_agent: str,
    session_id: str = "global",
) -> Dict[str, Any]:
    """Pushes a `user:*` namespace state mutation to the Universal Context Hub."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{ORCHESTRATOR_URL}/api/context/{user_id}/state",
                json={
                    "namespace_key": namespace_key,
                    "updates": updates,
                    "source_agent": source_agent,
                    "session_id": session_id,
                },
            )
            if resp.status_code == 200:
                return resp.json()
    except Exception as e:
        print(f"[ContextBridge] HTTP fallback to local engine for state update: {e}")

    from backend.universal_memory_engine import context_engine
    return await context_engine.update_universal_state(user_id, namespace_key, updates, source_agent, session_id)


async def push_memory_bank_fact(
    user_id: str,
    fact: str,
    category: str,
    source_agent: str,
    session_id: str = "global",
    confidence: float = 0.96,
) -> Dict[str, Any]:
    """Pushes a semantic memory fact to the Universal Memory Bank."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{ORCHESTRATOR_URL}/api/context/{user_id}/memory",
                json={
                    "fact": fact,
                    "category": category,
                    "source_agent": source_agent,
                    "session_id": session_id,
                    "confidence": confidence,
                },
            )
            if resp.status_code == 200:
                return resp.json()
    except Exception as e:
        print(f"[ContextBridge] HTTP fallback to local engine for memory push: {e}")

    from backend.universal_memory_engine import context_engine
    return await context_engine.add_memory(user_id, fact, category, source_agent, session_id, confidence)


async def push_shared_artifact(
    user_id: str,
    filename: str,
    title: str,
    content: str,
    created_by_agent: str,
    session_id: str = "global",
    mime_type: str = "text/markdown",
) -> Dict[str, Any]:
    """Pushes a versioned artifact to the Universal Artifact Vault."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{ORCHESTRATOR_URL}/api/context/{user_id}/artifact",
                json={
                    "filename": filename,
                    "title": title,
                    "content": content,
                    "created_by_agent": created_by_agent,
                    "session_id": session_id,
                    "mime_type": mime_type,
                },
            )
            if resp.status_code == 200:
                return resp.json()
    except Exception as e:
        print(f"[ContextBridge] HTTP fallback to local engine for artifact push: {e}")

    from backend.universal_memory_engine import context_engine
    return await context_engine.save_artifact(
        user_id, filename, title, content, created_by_agent, session_id, mime_type
    )


async def emit_remote_telemetry(event_type: str, payload: Dict[str, Any]) -> None:
    """Emits real-time telemetry event to the Hub WebSocket broadcaster."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(
                f"{ORCHESTRATOR_URL}/api/telemetry",
                json={"event_type": event_type, "payload": payload},
            )
    except Exception:
        pass
