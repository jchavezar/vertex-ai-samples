"""
Universal Context Orchestrator Service & A2A Hub (`orchestrator_service.py`).
Runs on Port 8010. Powered by Google ADK (gemini-3-flash-preview) & A2A Protocol Client.
Coordinates `wealth_agent` (:8011), `legal_tax_agent` (:8012), and `mobility_agent` (:8013),
exposes REST APIs for Universal State, Memory Bank, Shared Artifacts, and streams
real-time session-share telemetry over WebSockets (`/ws/telemetry`).
"""

import asyncio
import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv(Path(__file__).parent.parent / ".env", override=True)

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3-flash-preview")

ORCHESTRATOR_PORT = int(os.environ.get("ORCHESTRATOR_PORT", "8010"))
WEALTH_AGENT_PORT = int(os.environ.get("WEALTH_AGENT_PORT", "8011"))
LEGAL_AGENT_PORT = int(os.environ.get("LEGAL_AGENT_PORT", "8012"))
MOBILITY_AGENT_PORT = int(os.environ.get("MOBILITY_AGENT_PORT", "8013"))

AGENT_ENDPOINTS = {
    "wealth_agent": f"http://localhost:{WEALTH_AGENT_PORT}",
    "legal_tax_agent": f"http://localhost:{LEGAL_AGENT_PORT}",
    "mobility_agent": f"http://localhost:{MOBILITY_AGENT_PORT}",
}

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from backend.universal_memory_engine import context_engine
from backend.agents.wealth_agent import run_wealth_agent_turn
from backend.agents.legal_tax_agent import run_legal_agent_turn
from backend.agents.mobility_agent import run_mobility_agent_turn

app = FastAPI(
    title="Universal User Context Mesh — ADK & A2A Orchestrator Hub",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# A2A PROTOCOL JSON-RPC 2.0 DISPATCHER
# -----------------------------------------------------------------------------
async def call_a2a_agent_runtime(
    target_agent: str,
    user_id: str,
    session_id: str,
    message: str,
) -> Dict[str, Any]:
    """
    Sends a real A2A JSON-RPC 2.0 `message/send` request to the target A2A Agent Runtime
    (ports 8011, 8012, 8013). Captures the full JSON-RPC request & response trace for the UI.
    If the remote HTTP port is unreachable, falls back gracefully to direct ADK execution.
    """
    endpoint = AGENT_ENDPOINTS.get(target_agent)
    task_id = f"task-{uuid.uuid4().hex[:8]}"
    message_id = f"msg-{uuid.uuid4().hex[:8]}"

    envelope_payload = json.dumps(
        {
            "user_id": user_id,
            "session_id": session_id,
            "message": message,
        }
    )

    jsonrpc_request = {
        "jsonrpc": "2.0",
        "id": f"rpc-{uuid.uuid4().hex[:8]}",
        "method": "message/send",
        "params": {
            "message": {
                "messageId": message_id,
                "role": "user",
                "parts": [{"kind": "text", "text": envelope_payload}],
            },
            "configuration": {
                "acceptedOutputModes": ["application/json", "text/plain"],
            },
        },
    }

    await context_engine.broadcast_telemetry(
        "A2A_JSONRPC_SEND",
        {
            "source": "orchestrator_agent",
            "target_agent": target_agent,
            "endpoint": endpoint,
            "user_id": user_id,
            "session_id": session_id,
            "jsonrpc_request": jsonrpc_request,
            "summary": f"A2A Client dispatched JSON-RPC `message/send` to `{target_agent}` ({endpoint})",
        },
    )

    start_ts = time.time()
    result_data: Optional[Dict[str, Any]] = None
    transport_used = "A2A_HTTP_JSONRPC"

    if endpoint:
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    f"{endpoint}/",
                    json=jsonrpc_request,
                    headers={"Content-Type": "application/json"},
                )
                if resp.status_code == 200:
                    rpc_resp = resp.json()
                    # Extract text artifact from A2A JSON-RPC response
                    raw_text = ""
                    res_obj = rpc_resp.get("result", {})
                    # Check artifacts or status message parts
                    artifacts = res_obj.get("artifacts", [])
                    if artifacts:
                        for art in artifacts:
                            for part in art.get("parts", []):
                                if part.get("text"):
                                    raw_text = part["text"]
                    if not raw_text and "status" in res_obj:
                        msg_obj = res_obj["status"].get("message", {})
                        for part in msg_obj.get("parts", []):
                            if part.get("text"):
                                raw_text = part["text"]
                    if raw_text:
                        try:
                            result_data = json.loads(raw_text)
                        except Exception:
                            result_data = {
                                "agent_name": target_agent,
                                "response": raw_text,
                                "tool_calls": [],
                            }
        except Exception as e:
            print(f"[A2A Client] HTTP call to {endpoint} encountered {e}; executing ADK runtime directly.")

    if not result_data:
        transport_used = "ADK_DIRECT_RUNTIME"
        if target_agent == "wealth_agent":
            result_data = await run_wealth_agent_turn(user_id, session_id, message)
        elif target_agent == "legal_tax_agent":
            result_data = await run_legal_agent_turn(user_id, session_id, message)
        elif target_agent == "mobility_agent":
            result_data = await run_mobility_agent_turn(user_id, session_id, message)
        else:
            raise ValueError(f"Unknown target agent: {target_agent}")

    latency_ms = int((time.time() - start_ts) * 1000)

    jsonrpc_response = {
        "jsonrpc": "2.0",
        "id": jsonrpc_request["id"],
        "transport": transport_used,
        "latency_ms": latency_ms,
        "result": {
            "task_id": task_id,
            "state": "completed",
            "agent_output": result_data,
        },
    }

    await context_engine.broadcast_telemetry(
        "A2A_JSONRPC_COMPLETE",
        {
            "source": target_agent,
            "target": "orchestrator_agent",
            "user_id": user_id,
            "session_id": session_id,
            "latency_ms": latency_ms,
            "transport": transport_used,
            "tool_calls_count": len(result_data.get("tool_calls", [])),
            "summary": f"`{target_agent}` completed A2A task in {latency_ms}ms ({len(result_data.get('tool_calls', []))} tools executed)",
        },
    )

    return {
        "agent_result": result_data,
        "a2a_trace_item": {
            "target_agent": target_agent,
            "endpoint": endpoint,
            "transport": transport_used,
            "latency_ms": latency_ms,
            "request": jsonrpc_request,
            "response": jsonrpc_response,
        },
    }


# -----------------------------------------------------------------------------
# ORCHESTRATOR ADK AGENT & TOOLS
# -----------------------------------------------------------------------------
_ORCH_TURN_CONTEXT: Dict[str, Any] = {
    "user_id": "alex.rivera@enterprise.io",
    "session_id": "global",
    "a2a_traces": [],
    "delegated_tool_calls": [],
}


async def consult_wealth_agent_a2a(query: str) -> dict:
    """
    Delegates a wealth, liquidity, currency hedging, or asset allocation task to the
    Wealth & Portfolio A2A Agent (`wealth_agent` on port 8011).
    The agent automatically shares and updates the user's Universal Context (`user:financial_profile`).
    """
    user_id = _ORCH_TURN_CONTEXT["user_id"]
    session_id = _ORCH_TURN_CONTEXT["session_id"]
    res = await call_a2a_agent_runtime("wealth_agent", user_id, session_id, query)
    _ORCH_TURN_CONTEXT["a2a_traces"].append(res["a2a_trace_item"])
    _ORCH_TURN_CONTEXT["delegated_tool_calls"].extend(res["agent_result"].get("tool_calls", []))
    return {
        "agent": "wealth_agent",
        "response": res["agent_result"]["response"],
        "tools_executed": res["agent_result"].get("tool_calls", []),
    }


async def consult_legal_tax_agent_a2a(query: str) -> dict:
    """
    Delegates a legal, tax residency, FATCA/FBAR, exit tax, or corporate holding task to the
    Legal & Cross-Border Tax A2A Agent (`legal_tax_agent` on port 8012).
    The agent automatically reads wealth/mobility context and updates `user:legal_tax_status`.
    """
    user_id = _ORCH_TURN_CONTEXT["user_id"]
    session_id = _ORCH_TURN_CONTEXT["session_id"]
    res = await call_a2a_agent_runtime("legal_tax_agent", user_id, session_id, query)
    _ORCH_TURN_CONTEXT["a2a_traces"].append(res["a2a_trace_item"])
    _ORCH_TURN_CONTEXT["delegated_tool_calls"].extend(res["agent_result"].get("tool_calls", []))
    return {
        "agent": "legal_tax_agent",
        "response": res["agent_result"]["response"],
        "tools_executed": res["agent_result"].get("tool_calls", []),
    }


async def consult_mobility_agent_a2a(query: str) -> dict:
    """
    Delegates an international relocation, investor visa, Schengen day count, or lifestyle logistics
    task to the Global Mobility A2A Agent (`mobility_agent` on port 8013).
    The agent automatically reads wealth/legal context and updates `user:mobility_plan`.
    """
    user_id = _ORCH_TURN_CONTEXT["user_id"]
    session_id = _ORCH_TURN_CONTEXT["session_id"]
    res = await call_a2a_agent_runtime("mobility_agent", user_id, session_id, query)
    _ORCH_TURN_CONTEXT["a2a_traces"].append(res["a2a_trace_item"])
    _ORCH_TURN_CONTEXT["delegated_tool_calls"].extend(res["agent_result"].get("tool_calls", []))
    return {
        "agent": "mobility_agent",
        "response": res["agent_result"]["response"],
        "tools_executed": res["agent_result"].get("tool_calls", []),
    }


async def publish_master_executive_artifact(title: str, markdown_content: str) -> dict:
    """
    Publishes a synthesized multi-agent master plan (`executive_master_plan.md`)
    to the Universal Shared Artifact Vault.
    """
    user_id = _ORCH_TURN_CONTEXT["user_id"]
    session_id = _ORCH_TURN_CONTEXT["session_id"]
    art = await context_engine.save_artifact(
        user_id=user_id,
        filename="executive_master_plan.md",
        title=title,
        content=markdown_content,
        created_by_agent="orchestrator_agent",
        session_id=session_id,
    )
    _ORCH_TURN_CONTEXT["delegated_tool_calls"].append(
        {
            "tool": "publish_master_executive_artifact",
            "filename": "executive_master_plan.md",
            "version": art.get("version", 1),
        }
    )
    return {"status": "published", "filename": "executive_master_plan.md", "version": art.get("version", 1)}


ORCHESTRATOR_INSTRUCTION = """You are the **Universal Context Orchestrator (`orchestrator_agent`)**, an executive multi-agent coordinator built with Google ADK and the A2A Protocol.
You oversee 3 specialized A2A Agent Runtimes that share a single **Universal User Context Mesh** (`user:*` state, Universal Memory Bank, and Shared Artifact Vault):
1. `wealth_agent` (Port 8011) — Use `consult_wealth_agent_a2a` for portfolio, liquidity, secondary sales, and currency hedging.
2. `legal_tax_agent` (Port 8012) — Use `consult_legal_tax_agent_a2a` for international tax treaties, California/UK exit tax, FATCA, and Swiss/Singapore holding structures.
3. `mobility_agent` (Port 8013) — Use `consult_mobility_agent_a2a` for visas, Swiss Permit B / US O-1A, Schengen day limits, and family relocation logistics.

CRITICAL RULES:
- When a user request spans multiple domains (or when synchronizing a new user event across domains), invoke the relevant A2A specialist agents via your tools (`consult_wealth_agent_a2a`, `consult_legal_tax_agent_a2a`, `consult_mobility_agent_a2a`).
- Observe how each specialist agent automatically receives the Universal Context from previous agents and updates the shared state!
- Synthesize their findings clearly, explicitly pointing out **how context from one agent enriched another agent's decision** (e.g. how a liquidity update in Wealth immediately shaped the Legal tax treaty structure and Mobility visa budget).
- Whenever you produce a comprehensive multi-agent strategy, call `publish_master_executive_artifact` to save `executive_master_plan.md` in the Shared Artifact Vault.
"""

orchestrator_session_service = InMemorySessionService()


async def run_orchestrator_turn(
    user_id: str, session_id: str, user_message: str, synthesis_only: bool = False
) -> Dict[str, Any]:
    _ORCH_TURN_CONTEXT["user_id"] = user_id
    _ORCH_TURN_CONTEXT["session_id"] = session_id
    _ORCH_TURN_CONTEXT["a2a_traces"] = []
    _ORCH_TURN_CONTEXT["delegated_tool_calls"] = []

    injection = await context_engine.build_universal_context_injection(
        user_id=user_id, requesting_agent="orchestrator_agent", session_id=session_id
    )
    augmented_prompt = (
        f"{injection['prompt_block']}\n\n"
        f"USER MESSAGE TO UNIVERSAL ORCHESTRATOR:\n{user_message}"
    )

    tools_list = (
        [publish_master_executive_artifact]
        if synthesis_only
        else [
            consult_wealth_agent_a2a,
            consult_legal_tax_agent_a2a,
            consult_mobility_agent_a2a,
            publish_master_executive_artifact,
        ]
    )

    instr = (
        "You are the Universal Context Orchestrator (`orchestrator_agent`). "
        "The Wealth, Legal/Tax, and Global Mobility A2A agents have just completed their sessions and updated the Universal User Context above. "
        "Synthesize their cross-session findings into a cohesive executive master plan, explicitly highlighting how memories and `user:*` state from one agent shaped the others. "
        "Call `publish_master_executive_artifact` to save `executive_master_plan.md`."
        if synthesis_only
        else ORCHESTRATOR_INSTRUCTION
    )

    adk_agent = Agent(
        name="orchestrator_agent",
        model=GEMINI_MODEL,
        instruction=instr,
        description="Coordinates Wealth, Legal/Tax, and Global Mobility A2A agents over a shared Universal User Context.",
        tools=tools_list,
    )

    adk_session_id = f"adk-orch-{session_id}"
    try:
        await orchestrator_session_service.create_session(
            app_name="orchestrator_app", user_id=user_id, session_id=adk_session_id
        )
    except Exception:
        pass

    runner = Runner(
        agent=adk_agent,
        app_name="orchestrator_app",
        session_service=orchestrator_session_service,
    )
    final_text = ""

    async for event in runner.run_async(
        user_id=user_id,
        session_id=adk_session_id,
        new_message=genai_types.Content(
            role="user", parts=[genai_types.Part.from_text(text=augmented_prompt)]
        ),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            for part in event.content.parts:
                if getattr(part, "text", None):
                    final_text += part.text

    return {
        "agent_name": "orchestrator_agent",
        "response": final_text.strip() or "Universal Orchestrator coordinated A2A specialists and synchronized context.",
        "tool_calls": list(_ORCH_TURN_CONTEXT["delegated_tool_calls"]),
        "a2a_trace": list(_ORCH_TURN_CONTEXT["a2a_traces"]),
        "injected_memories": injection.get("injected_memories", []),
    }


# -----------------------------------------------------------------------------
# API REQUEST SCHEMAS
# -----------------------------------------------------------------------------
class ChatRequest(BaseModel):
    user_id: str = "alex.rivera@enterprise.io"
    session_id: str = "session-main"
    target_agent: str = "orchestrator_agent"  # orchestrator_agent | wealth_agent | legal_tax_agent | mobility_agent
    message: str


class StateUpdateRequest(BaseModel):
    namespace_key: str
    updates: Dict[str, Any]
    source_agent: str = "manual_ui"
    session_id: str = "global"


class MemoryCreateRequest(BaseModel):
    fact: str
    category: str = "general"
    source_agent: str = "manual_ui"
    session_id: str = "global"
    confidence: float = 0.98


class ArtifactCreateRequest(BaseModel):
    filename: str
    title: str
    content: str
    created_by_agent: str = "manual_ui"
    session_id: str = "global"
    mime_type: str = "text/markdown"


class RoundtableRequest(BaseModel):
    user_id: str = "alex.rivera@enterprise.io"
    scenario_prompt: Optional[str] = None


class CreateUserRequest(BaseModel):
    user_id: str
    display_name: str
    primary_goal: str = "Global Multi-Agent Wealth, Tax & Mobility Strategy"


# -----------------------------------------------------------------------------
# REST API ENDPOINTS
# -----------------------------------------------------------------------------
@app.get("/api/health")
async def get_health() -> Dict[str, Any]:
    """Checks health and fetches live A2A Agent Cards from ports 8011, 8012, 8013."""
    agents_status = {}
    async with httpx.AsyncClient(timeout=3.0) as client:
        for name, url in AGENT_ENDPOINTS.items():
            try:
                resp = await client.get(f"{url}/.well-known/agent-card.json")
                if resp.status_code == 200:
                    agents_status[name] = {
                        "status": "online",
                        "endpoint": url,
                        "protocol": "A2A JSON-RPC 2.0",
                        "agent_card": resp.json(),
                    }
                else:
                    agents_status[name] = {"status": "standby", "endpoint": url, "protocol": "A2A JSON-RPC 2.0"}
            except Exception:
                agents_status[name] = {
                    "status": "embedded_adk_ready",
                    "endpoint": url,
                    "protocol": "A2A + In-Process Fallback",
                }

    return {
        "status": "healthy",
        "orchestrator": {
            "name": "orchestrator_agent",
            "port": ORCHESTRATOR_PORT,
            "model": GEMINI_MODEL,
        },
        "a2a_agents": agents_status,
    }


@app.get("/api/users")
async def list_users() -> List[Dict[str, Any]]:
    res = []
    for uid, udata in context_engine.users.items():
        res.append(
            {
                "user_id": uid,
                "display_name": udata.get("display_name", uid),
                "avatar": udata.get("avatar", uid[:2].upper()),
                "memories_count": len(udata.get("memories", [])),
                "artifacts_count": len(udata.get("artifacts", [])),
                "sessions_count": len(udata.get("sessions", {})),
            }
        )
    return res


@app.post("/api/users")
async def create_user(req: CreateUserRequest) -> Dict[str, Any]:
    u = context_engine.ensure_user(req.user_id)
    u["display_name"] = req.display_name
    u["universal_state"]["user:profile"] = {
        "full_name": req.display_name,
        "primary_goal": req.primary_goal,
    }
    context_engine._save()
    return {"status": "created", "user": u}


@app.get("/api/users/{user_id}/context")
async def get_user_universal_context(user_id: str) -> Dict[str, Any]:
    u = context_engine.ensure_user(user_id)
    return {
        "user_id": user_id,
        "display_name": u.get("display_name", user_id),
        "universal_state": u.get("universal_state", {}),
        "memories": u.get("memories", []),
        "artifacts": u.get("artifacts", []),
        "sessions": u.get("sessions", {}),
        "mutation_history": u.get("mutation_history", []),
        "recent_telemetry": context_engine.telemetry_log[-60:],
    }


@app.post("/api/users/{user_id}/clear")
async def clear_user_slate_endpoint(user_id: str) -> Dict[str, Any]:
    """
    Completely wipes all preloaded orders, Memory Bank facts, chat sessions, and artifacts
    for `user_id`, AND resets the local ADK InMemorySessionService caches across all 4 ports!
    """
    global orchestrator_session_service
    await context_engine.clear_user_context(user_id)
    orchestrator_session_service = InMemorySessionService()

    # Clear local ADK session caches on peer A2A runtimes (:8011, :8012, :8013)
    async with httpx.AsyncClient(timeout=2.0) as client:
        for _, url in AGENT_ENDPOINTS.items():
            try:
                await client.post(f"{url}/clear_sessions")
            except Exception:
                pass

    return {
        "status": "cleared",
        "user_id": user_id,
        "universal_context": await get_user_universal_context(user_id),
    }


@app.get("/api/context/{user_id}/injection")
async def get_context_injection(user_id: str, agent_name: str = "agent", session_id: str = "global") -> Dict[str, Any]:
    return await context_engine.build_universal_context_injection(user_id, agent_name, session_id)


@app.post("/api/context/{user_id}/state")
async def post_state_update(user_id: str, req: StateUpdateRequest) -> Dict[str, Any]:
    updated = await context_engine.update_universal_state(
        user_id=user_id,
        namespace_key=req.namespace_key,
        updates=req.updates,
        source_agent=req.source_agent,
        session_id=req.session_id,
    )
    return {"status": "updated", "namespace_key": req.namespace_key, "state": updated}


@app.post("/api/context/{user_id}/memory")
async def post_memory_fact(user_id: str, req: MemoryCreateRequest) -> Dict[str, Any]:
    mem = await context_engine.add_memory(
        user_id=user_id,
        fact=req.fact,
        category=req.category,
        source_agent=req.source_agent,
        session_id=req.session_id,
        confidence=req.confidence,
    )
    return {"status": "added", "memory": mem}


@app.delete("/api/context/{user_id}/memory/{memory_id}")
async def delete_memory_fact(user_id: str, memory_id: str) -> Dict[str, Any]:
    u = context_engine.ensure_user(user_id)
    u["memories"] = [m for m in u["memories"] if m.get("memory_id") != memory_id]
    context_engine._save()
    return {"status": "deleted", "memory_id": memory_id}


@app.post("/api/context/{user_id}/artifact")
async def post_shared_artifact(user_id: str, req: ArtifactCreateRequest) -> Dict[str, Any]:
    art = await context_engine.save_artifact(
        user_id=user_id,
        filename=req.filename,
        title=req.title,
        content=req.content,
        created_by_agent=req.created_by_agent,
        session_id=req.session_id,
        mime_type=req.mime_type,
    )
    return {"status": "saved", "artifact": art}


@app.post("/api/telemetry")
async def receive_remote_telemetry(body: Dict[str, Any]) -> Dict[str, Any]:
    event_type = body.get("event_type", "REMOTE_EVENT")
    payload = body.get("payload", {})
    await context_engine.broadcast_telemetry(event_type, payload)
    return {"status": "ok"}


# -----------------------------------------------------------------------------
# UNIFIED CHAT ENDPOINT (DIRECT AGENT OR ORCHESTRATOR SESSION)
# -----------------------------------------------------------------------------
@app.post("/api/chat")
async def handle_chat_turn(req: ChatRequest) -> Dict[str, Any]:
    """
    Handles a conversation turn in a specific session (`req.session_id`) with either:
    - `orchestrator_agent` (Coordinates across A2A agents)
    - `wealth_agent` (Direct A2A session with Wealth Agent on port 8011)
    - `legal_tax_agent` (Direct A2A session with Legal & Tax Agent on port 8012)
    - `mobility_agent` (Direct A2A session with Mobility Agent on port 8013)
    Records user message, agent response, A2A traces, injected memories from other sessions,
    and state mutations into the session history store.
    """
    user_id = req.user_id
    session_id = req.session_id
    target_agent = req.target_agent
    user_message = req.message
    turn_start = time.time()
    reasoning_steps = []

    async def emit_reasoning(step_title: str, detail: str) -> None:
        elapsed = round(time.time() - turn_start, 2)
        step_obj = {"elapsed_sec": elapsed, "title": step_title, "detail": detail}
        reasoning_steps.append(step_obj)
        await context_engine.broadcast_telemetry(
            "REASONING_STEP",
            {
                "user_id": user_id,
                "session_id": session_id,
                "agent": target_agent,
                "elapsed_sec": elapsed,
                "title": step_title,
                "summary": detail,
            },
        )

    # Record user message in session history
    context_engine.append_message(
        user_id=user_id,
        session_id=session_id,
        target_agent=target_agent,
        role="user",
        content=user_message,
        agent_name="user",
    )

    await emit_reasoning(
        "Universal Context Mesh Lookup",
        f"Reading shared `user:*` namespaces & Cross-Agent Memory Bank for `{user_id}`...",
    )

    if target_agent == "orchestrator_agent":
        await emit_reasoning(
            "Orchestrator ADK Planning",
            "Analyzing query across Ordering (:8011), Delivery (:8012), and Support (:8013) A2A agents...",
        )
        turn_res = await run_orchestrator_turn(user_id, session_id, user_message)
        response_text = turn_res["response"]
        tool_calls = turn_res.get("tool_calls", [])
        a2a_trace = turn_res.get("a2a_trace", [])
        injected_memories = turn_res.get("injected_memories", [])
    else:
        await emit_reasoning(
            f"A2A JSON-RPC 2.0 Dispatch → `{target_agent}`",
            f"Injecting Universal Context block & invoking `{target_agent}` runtime over JSON-RPC 2.0...",
        )
        rpc_res = await call_a2a_agent_runtime(target_agent, user_id, session_id, user_message)
        agent_out = rpc_res["agent_result"]
        response_text = agent_out.get("response", "")
        tool_calls = agent_out.get("tool_calls", [])
        a2a_trace = [rpc_res["a2a_trace_item"]]
        injected_memories = agent_out.get("injected_memories", [])

    if tool_calls:
        tool_names = ", ".join([tc.get("tool") or tc.get("name", "tool") for tc in tool_calls])
        await emit_reasoning(
            "ADK Tool Execution Complete",
            f"Executed {len(tool_calls)} tool(s): `{tool_names}` — synchronized state with Universal Hub.",
        )

    mutated_keys = [tc.get("namespace") for tc in tool_calls if tc.get("namespace")]

    await emit_reasoning(
        "Post-Turn Memory & Context Extractor",
        "Running `gemini-3-flash-preview` auto-extractor to commit new turn facts into Memory Bank...",
    )

    # AUTOMATIC POST-TURN MEMORY & UNIVERSAL CONTEXT SYNC
    auto_sync_result = await context_engine.auto_extract_and_sync_turn(
        user_id=user_id,
        session_id=session_id,
        agent_name=target_agent,
        user_message=user_message,
        agent_response=response_text,
    )
    if isinstance(auto_sync_result, list) and len(auto_sync_result) > 0:
        await emit_reasoning(
            "Memory Bank Synchronized",
            f"Committed {len(auto_sync_result)} new semantic fact(s) to shared Memory Bank across all sessions.",
        )
    elif isinstance(auto_sync_result, dict) and auto_sync_result.get("mutated_keys"):
        for mk in auto_sync_result["mutated_keys"]:
            if mk not in mutated_keys:
                mutated_keys.append(mk)

    total_elapsed = round(time.time() - turn_start, 2)
    await emit_reasoning(
        "Response Ready",
        f"Completed cross-session turn in {total_elapsed}s ({len(injected_memories)} memories inherited).",
    )

    agent_msg = context_engine.append_message(
        user_id=user_id,
        session_id=session_id,
        target_agent=target_agent,
        role="agent",
        content=response_text,
        agent_name=target_agent,
        tool_calls=tool_calls,
        a2a_trace=a2a_trace,
        injected_memories=injected_memories,
        mutated_keys=mutated_keys,
    )
    agent_msg["reasoning_steps"] = reasoning_steps
    agent_msg["elapsed_sec"] = total_elapsed
    context_engine._save()

    return {
        "status": "completed",
        "session_id": session_id,
        "target_agent": target_agent,
        "message": agent_msg,
        "universal_context": await get_user_universal_context(user_id),
    }


# -----------------------------------------------------------------------------
# REAL-TIME MULTI-AGENT COLLABORATION & SESSION SHARE ROUNDTABLE
# -----------------------------------------------------------------------------
@app.post("/api/roundtable/run")
async def run_realtime_multi_agent_roundtable(req: RoundtableRequest) -> Dict[str, Any]:
    """
    Executes an autonomous, real-time E2E multi-agent session-sharing collaboration across
    separate sessions:
    - If `user_id` is `carlos@restaurant.io`: Runs Ordering Agent (Session #1) -> Delivery Agent (Session #2) -> Support Agent (Session #3) -> Master Synthesis.
    - If `user_id` is `alex.rivera@enterprise.io`: Runs Wealth (Session A) -> Legal/Tax (Session B) -> Mobility (Session C) -> Master Synthesis.
    Streams every step live over WebSocket so the user can watch how context written in Session #1
    is immediately injected and utilized in Session #2 and Session #3!
    """
    user_id = req.user_id
    is_restaurant = "carlos" in user_id.lower() or "restaurant" in user_id.lower()

    roundtable_id = f"rt-{uuid.uuid4().hex[:5]}"
    steps_summary = []

    if is_restaurant:
        sess_order = f"session-ordering-{roundtable_id}"
        sess_delivery = f"session-delivery-{roundtable_id}"
        sess_support = f"session-support-{roundtable_id}"
        sess_orch = f"session-master-{roundtable_id}"

        order_prompt = req.scenario_prompt or (
            "Hi! I'm Carlos. I want to update my order #ORD-9042: add 1x Truffle Wagyu Gyoza ($18) "
            "and swap my drink to a Yuzu Sparkling Water ($5) for delivery to 742 Evergreen Terrace, Apt 4B. "
            "Please note my severe peanut allergy!"
        )

        # STEP 1: ORDERING AGENT IN SESSION #1
        await context_engine.broadcast_telemetry(
            "ROUNDTABLE_STEP",
            {
                "step": 1,
                "total_steps": 4,
                "agent": "ordering_agent",
                "session_id": sess_order,
                "title": f"Step 1/4: Ordering Agent (`{sess_order}`) takes Carlos's food order & updates `user:active_order`",
                "summary": "Ordering Agent (:8011) recording Wagyu Gyoza + Yuzu Water + Peanut Allergy into Universal Context...",
            },
        )
        context_engine.append_message(
            user_id=user_id,
            session_id=sess_order,
            target_agent="wealth_agent",
            role="user",
            content=f"[Session #1 - Ordering Agent] {order_prompt}",
            agent_name="user",
        )
        res_o = await call_a2a_agent_runtime(
            "wealth_agent",
            user_id,
            sess_order,
            (
                f"{order_prompt}\n\n"
                "Call `update_active_order` to update `user:active_order` with the new items (2x Spicy Tuna Crispy Rice, "
                "1x Wagyu Truffle Burger, 1x Truffle Wagyu Gyoza, 1x Yuzu Sparkling Water, total $62.50), call `record_wealth_memory` "
                "with this updated order fact, and call `publish_order_receipt`."
            ),
        )
        o_out = res_o["agent_result"]
        await context_engine.auto_extract_and_sync_turn(
            user_id, sess_order, "ordering_agent", order_prompt, o_out["response"]
        )
        context_engine.append_message(
            user_id=user_id,
            session_id=sess_order,
            target_agent="wealth_agent",
            role="agent",
            content=o_out["response"],
            agent_name="ordering_agent",
            tool_calls=o_out.get("tool_calls", []),
            a2a_trace=[res_o["a2a_trace_item"]],
            injected_memories=o_out.get("injected_memories", []),
        )
        steps_summary.append({"step": 1, "agent": "ordering_agent", "session_id": sess_order, "output": o_out})

        # STEP 2: DELIVERY AGENT IN SESSION #2 (SEPARATE SESSION!)
        await context_engine.broadcast_telemetry(
            "ROUNDTABLE_STEP",
            {
                "step": 2,
                "total_steps": 4,
                "agent": "delivery_agent",
                "session_id": sess_delivery,
                "title": f"Step 2/4: Delivery Agent (`{sess_delivery}`) AUTOMATICALLY knows items ordered in `{sess_order}`!",
                "summary": "Delivery Agent (:8012) reading `user:active_order` & setting gate code #9988 for driver Marco...",
            },
        )
        delivery_prompt = (
            "[Session #2 - Delivery Agent (Separate Session!)] Hey Delivery Agent! Without me repeating my order, "
            "can you tell me what items you see in my order #ORD-9042 right now, and please give driver Marco "
            "gate code #9988 and instructions to leave the food on the heated porch bench?"
        )
        context_engine.append_message(
            user_id=user_id,
            session_id=sess_delivery,
            target_agent="legal_tax_agent",
            role="user",
            content=delivery_prompt,
            agent_name="user",
        )
        res_d = await call_a2a_agent_runtime(
            "legal_tax_agent",
            user_id,
            sess_delivery,
            (
                f"{delivery_prompt}\n\n"
                "Recite Carlos's exact items from `user:active_order` (including the Truffle Wagyu Gyoza and Yuzu Sparkling Water "
                "ordered in Session #1!), then call `update_delivery_logistics` with gate code #9988 and call `record_legal_memory`."
            ),
        )
        d_out = res_d["agent_result"]
        await context_engine.auto_extract_and_sync_turn(
            user_id, sess_delivery, "delivery_agent", delivery_prompt, d_out["response"]
        )
        context_engine.append_message(
            user_id=user_id,
            session_id=sess_delivery,
            target_agent="legal_tax_agent",
            role="agent",
            content=d_out["response"],
            agent_name="delivery_agent",
            tool_calls=d_out.get("tool_calls", []),
            a2a_trace=[res_d["a2a_trace_item"]],
            injected_memories=d_out.get("injected_memories", []),
        )
        steps_summary.append({"step": 2, "agent": "delivery_agent", "session_id": sess_delivery, "output": d_out})

        # STEP 3: VIP SUPPORT AGENT IN SESSION #3 (SEPARATE SESSION!)
        await context_engine.broadcast_telemetry(
            "ROUNDTABLE_STEP",
            {
                "step": 3,
                "total_steps": 4,
                "agent": "support_agent",
                "session_id": sess_support,
                "title": f"Step 3/4: Support Agent (`{sess_support}`) verifies BOTH Order (Session #1) & Gate Code (Session #2)",
                "summary": "Support Agent (:8013) confirming peanut-free prep & driver gate code #9988 across sessions...",
            },
        )
        support_prompt = (
            "[Session #3 - VIP Customer Support (Separate Session!)] Hi Support! Can you verify that the kitchen "
            "saw my peanut allergy from Session #1 and that driver Marco has gate code #9988 from Session #2?"
        )
        context_engine.append_message(
            user_id=user_id,
            session_id=sess_support,
            target_agent="mobility_agent",
            role="user",
            content=support_prompt,
            agent_name="user",
        )
        res_s = await call_a2a_agent_runtime(
            "mobility_agent",
            user_id,
            sess_support,
            (
                f"{support_prompt}\n\n"
                "Confirm both the peanut allergy and Wagyu Gyoza from Session #1 AND gate code #9988 from Session #2! "
                "Call `update_support_ticket` and `record_mobility_memory`."
            ),
        )
        s_out = res_s["agent_result"]
        await context_engine.auto_extract_and_sync_turn(
            user_id, sess_support, "support_agent", support_prompt, s_out["response"]
        )
        context_engine.append_message(
            user_id=user_id,
            session_id=sess_support,
            target_agent="mobility_agent",
            role="agent",
            content=s_out["response"],
            agent_name="support_agent",
            tool_calls=s_out.get("tool_calls", []),
            a2a_trace=[res_s["a2a_trace_item"]],
            injected_memories=s_out.get("injected_memories", []),
        )
        steps_summary.append({"step": 3, "agent": "support_agent", "session_id": sess_support, "output": s_out})

        # STEP 4: ORCHESTRATOR SYNTHESIS
        await context_engine.broadcast_telemetry(
            "ROUNDTABLE_STEP",
            {
                "step": 4,
                "total_steps": 4,
                "agent": "orchestrator_agent",
                "session_id": sess_orch,
                "title": "Step 4/4: Universal Orchestrator synthesizes cross-session Restaurant Order & Delivery Lineage",
                "summary": "Orchestrator generating Master Restaurant Delivery Dossier across all 3 sessions...",
            },
        )
        synth_prompt = (
            "Synthesize how Carlos's order in Session #1 (`ordering_agent`) was automatically shared via the Universal User Context "
            "to Session #2 (`delivery_agent`) and Session #3 (`support_agent`) without Carlos ever repeating his order items or allergy!"
        )
        orch_res = await run_orchestrator_turn(user_id, sess_orch, synth_prompt, synthesis_only=True)
        context_engine.append_message(
            user_id=user_id,
            session_id=sess_orch,
            target_agent="orchestrator_agent",
            role="agent",
            content=orch_res["response"],
            agent_name="orchestrator_agent",
            tool_calls=orch_res.get("tool_calls", []),
            a2a_trace=orch_res.get("a2a_trace", []),
            injected_memories=orch_res.get("injected_memories", []),
        )
        steps_summary.append({"step": 4, "agent": "orchestrator_agent", "session_id": sess_orch, "output": orch_res})

        await context_engine.broadcast_telemetry(
            "ROUNDTABLE_COMPLETE",
            {
                "user_id": user_id,
                "roundtable_id": roundtable_id,
                "sessions_created": [sess_order, sess_delivery, sess_support, sess_orch],
                "summary": "Restaurant Ordering (Session 1) <-> Delivery (Session 2) <-> Support (Session 3) E2E Complete!",
            },
        )
        return {
            "status": "completed",
            "roundtable_id": roundtable_id,
            "sessions": [sess_order, sess_delivery, sess_support, sess_orch],
            "steps": steps_summary,
            "universal_context": await get_user_universal_context(user_id),
        }

    scenario_trigger = req.scenario_prompt or (
        "URGENT CLIENT UPDATE: I just closed an additional $4.8M secondary liquidity tranche "
        "(bringing my liquid net worth to $19.3M USD). I want to accelerate my family relocation "
        "to Zurich, Switzerland to Q4 2026, allocate $5M into Swiss CHF sovereign assets, "
        "and ensure full California FTB exit tax compliance and Swiss Permit B readiness."
    )

    sess_wealth = f"session-wealth-{roundtable_id}"
    sess_legal = f"session-legal-{roundtable_id}"
    sess_mobility = f"session-mobility-{roundtable_id}"
    sess_orch = f"session-master-{roundtable_id}"

    # --- STEP 1: WEALTH AGENT IN SESSION A ---
    await context_engine.broadcast_telemetry(
        "ROUNDTABLE_STEP",
        {
            "step": 1,
            "total_steps": 4,
            "agent": "wealth_agent",
            "session_id": sess_wealth,
            "title": "Step 1/4: Wealth Agent (`session-wealth`) ingests liquidity event & updates `user:financial_profile`",
            "summary": "Wealth Agent (:8011) processing $4.8M liquidity tranche & CHF currency hedge...",
        },
    )
    context_engine.append_message(
        user_id=user_id,
        session_id=sess_wealth,
        target_agent="wealth_agent",
        role="user",
        content=f"[Session A - Wealth Strategy] {scenario_trigger}",
        agent_name="user",
    )
    res_w = await call_a2a_agent_runtime(
        "wealth_agent",
        user_id,
        sess_wealth,
        (
            f"{scenario_trigger}\n\n"
            "Please call `update_financial_profile` to update liquid net worth to $19,300,000 USD and core holdings "
            "to reflect the $5M CHF hedge, call `record_wealth_memory` with this new $19.3M net worth fact so peer agents see it, "
            "and call `publish_portfolio_artifact` to update `portfolio_analysis.md`."
        ),
    )
    w_out = res_w["agent_result"]
    context_engine.append_message(
        user_id=user_id,
        session_id=sess_wealth,
        target_agent="wealth_agent",
        role="agent",
        content=w_out["response"],
        agent_name="wealth_agent",
        tool_calls=w_out.get("tool_calls", []),
        a2a_trace=[res_w["a2a_trace_item"]],
        injected_memories=w_out.get("injected_memories", []),
    )
    steps_summary.append({"step": 1, "agent": "wealth_agent", "session_id": sess_wealth, "output": w_out})

    # --- STEP 2: LEGAL & TAX AGENT IN SESSION B (READS WEALTH CONTEXT!) ---
    await context_engine.broadcast_telemetry(
        "ROUNDTABLE_STEP",
        {
            "step": 2,
            "total_steps": 4,
            "agent": "legal_tax_agent",
            "session_id": sess_legal,
            "title": "Step 2/4: Legal Agent (`session-legal`) automatically inherits $19.3M Wealth Memory & structures Swiss/CA Tax",
            "summary": "Legal & Tax Agent (:8012) reading new $19.3M wealth context & updating `user:legal_tax_status`...",
        },
    )
    legal_prompt = (
        "[Session B - Cross-Border Legal & Tax Review] Based on the brand-new liquidity update and $19.3M net worth "
        "just recorded in the Universal Context by `wealth_agent`, evaluate the California FTB exit tax compliance "
        "for accelerating relocation to Q4 2026 and structuring the Swiss GmbH / Lump-Sum tax treaty arrangement. "
        "Call `update_legal_tax_status`, `record_legal_memory`, and `publish_tax_compliance_memo`."
    )
    context_engine.append_message(
        user_id=user_id,
        session_id=sess_legal,
        target_agent="legal_tax_agent",
        role="user",
        content=legal_prompt,
        agent_name="user",
    )
    res_l = await call_a2a_agent_runtime("legal_tax_agent", user_id, sess_legal, legal_prompt)
    l_out = res_l["agent_result"]
    context_engine.append_message(
        user_id=user_id,
        session_id=sess_legal,
        target_agent="legal_tax_agent",
        role="agent",
        content=l_out["response"],
        agent_name="legal_tax_agent",
        tool_calls=l_out.get("tool_calls", []),
        a2a_trace=[res_l["a2a_trace_item"]],
        injected_memories=l_out.get("injected_memories", []),
    )
    steps_summary.append({"step": 2, "agent": "legal_tax_agent", "session_id": sess_legal, "output": l_out})

    # --- STEP 3: MOBILITY AGENT IN SESSION C (READS BOTH WEALTH & LEGAL CONTEXT!) ---
    await context_engine.broadcast_telemetry(
        "ROUNDTABLE_STEP",
        {
            "step": 3,
            "total_steps": 4,
            "agent": "mobility_agent",
            "session_id": sess_mobility,
            "title": "Step 3/4: Mobility Agent (`session-mobility`) inherits BOTH Wealth & Legal memories for Q4 2026 Zurich Move",
            "summary": "Mobility Agent (:8013) aligning Permit B investment visa with Legal day-count & Wealth CHF budget...",
        },
    )
    mobility_prompt = (
        "[Session C - Global Mobility & Visa Execution] Incorporating the $19.3M liquid net worth and $5M CHF allocation "
        "from `wealth_agent` AND the California exit day-count & Swiss GmbH structure from `legal_tax_agent`, "
        "finalize the Q4 2026 Zurich family relocation roadmap and Swiss Permit B submission schedule. "
        "Call `update_mobility_plan`, `record_mobility_memory`, and `publish_relocation_dossier`."
    )
    context_engine.append_message(
        user_id=user_id,
        session_id=sess_mobility,
        target_agent="mobility_agent",
        role="user",
        content=mobility_prompt,
        agent_name="user",
    )
    res_m = await call_a2a_agent_runtime("mobility_agent", user_id, sess_mobility, mobility_prompt)
    m_out = res_m["agent_result"]
    context_engine.append_message(
        user_id=user_id,
        session_id=sess_mobility,
        target_agent="mobility_agent",
        role="agent",
        content=m_out["response"],
        agent_name="mobility_agent",
        tool_calls=m_out.get("tool_calls", []),
        a2a_trace=[res_m["a2a_trace_item"]],
        injected_memories=m_out.get("injected_memories", []),
    )
    steps_summary.append({"step": 3, "agent": "mobility_agent", "session_id": sess_mobility, "output": m_out})

    # --- STEP 4: UNIVERSAL ORCHESTRATOR SYNTHESIS ---
    await context_engine.broadcast_telemetry(
        "ROUNDTABLE_STEP",
        {
            "step": 4,
            "total_steps": 4,
            "agent": "orchestrator_agent",
            "session_id": sess_orch,
            "title": "Step 4/4: Universal Orchestrator synthesizes cross-session memory lineage & publishes `executive_master_plan.md`",
            "summary": "Orchestrator generating unified Executive Master Plan across all 3 A2A sessions...",
        },
    )
    orch_prompt = (
        "Synthesize the live multi-agent roundtable across Session A (`wealth_agent`), Session B (`legal_tax_agent`), "
        "and Session C (`mobility_agent`). Explicitly trace how the $19.3M liquidity update flowed across the "
        "Universal Context Mesh into Legal & Mobility decisions, and call `publish_master_executive_artifact` "
        "to save the complete `executive_master_plan.md`."
    )
    context_engine.append_message(
        user_id=user_id,
        session_id=sess_orch,
        target_agent="orchestrator_agent",
        role="user",
        content=orch_prompt,
        agent_name="user",
    )
    orch_out = await run_orchestrator_turn(user_id, sess_orch, orch_prompt, synthesis_only=True)
    context_engine.append_message(
        user_id=user_id,
        session_id=sess_orch,
        target_agent="orchestrator_agent",
        role="agent",
        content=orch_out["response"],
        agent_name="orchestrator_agent",
        tool_calls=orch_out.get("tool_calls", []),
        a2a_trace=orch_out.get("a2a_trace", []),
        injected_memories=orch_out.get("injected_memories", []),
    )
    steps_summary.append({"step": 4, "agent": "orchestrator_agent", "session_id": sess_orch, "output": orch_out})

    await context_engine.broadcast_telemetry(
        "ROUNDTABLE_COMPLETE",
        {
            "roundtable_id": roundtable_id,
            "user_id": user_id,
            "master_session_id": sess_orch,
            "summary": "Real-Time Multi-Agent Session Share Roundtable completed across all 4 runtimes!",
        },
    )

    return {
        "status": "completed",
        "roundtable_id": roundtable_id,
        "master_session_id": sess_orch,
        "sessions_created": [sess_wealth, sess_legal, sess_mobility, sess_orch],
        "steps": steps_summary,
        "universal_context": await get_user_universal_context(user_id),
    }


@app.post("/api/reset")
async def reset_demo_state() -> Dict[str, Any]:
    from backend.universal_memory_engine import DEFAULT_USERS
    context_engine.users = json.loads(json.dumps(DEFAULT_USERS))
    context_engine.telemetry_log = []
    context_engine._save()
    await context_engine.broadcast_telemetry(
        "SYSTEM_RESET",
        {"summary": "Universal Context Mesh reset to clean initial enterprise profiles."},
    )
    return {"status": "reset"}


# -----------------------------------------------------------------------------
# WEBSOCKET TELEMETRY STREAM
# -----------------------------------------------------------------------------
@app.websocket("/ws/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    q = context_engine.subscribe_ws()
    try:
        # Send recent history on connect
        await websocket.send_json(
            {
                "type": "INITIAL_LOG",
                "events": context_engine.telemetry_log[-40:],
            }
        )
        while True:
            event = await q.get()
            await websocket.send_json({"type": "LIVE_EVENT", "event": event})
    except WebSocketDisconnect:
        context_engine.unsubscribe_ws(q)
    except Exception:
        context_engine.unsubscribe_ws(q)


# -----------------------------------------------------------------------------
# SERVE FRONTEND STATIC ASSETS
# -----------------------------------------------------------------------------
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

@app.get("/")
async def serve_index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/styles.css")
async def serve_styles() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "styles.css")

@app.get("/app.js")
async def serve_js() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "app.js")

if __name__ == "__main__":
    print(f"Starting Universal Context Orchestrator & Hub on http://0.0.0.0:{ORCHESTRATOR_PORT}")
    uvicorn.run(app, host="0.0.0.0", port=ORCHESTRATOR_PORT)
