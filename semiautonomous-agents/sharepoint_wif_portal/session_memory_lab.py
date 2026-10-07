"""
Unified ADK + VertexAiSessionService + VertexAiMemoryBankService + GE streamAssist Lab
======================================================================================
Demonstrates how Google ADK (`gemini-3-flash-preview`) owns the conversation chain
and long-term memory in Vertex AI Agent Engine while using Gemini Enterprise
`streamAssist` as a 1:1 session-bound RAG tool (zero orphan GE session bloat).
"""
import asyncio
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

import google.auth
import google.auth.transport.requests
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from google.adk.agents import Agent
from google.adk.memory.vertex_ai_memory_bank_service import VertexAiMemoryBankService
from google.adk.runners import Runner
from google.adk.sessions.vertex_ai_session_service import VertexAiSessionService
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types
from pydantic import BaseModel, Field

load_dotenv()

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
os.environ["GOOGLE_CLOUD_PROJECT"] = os.environ.get("PROJECT_ID", "sharepoint-wif-agent")
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("session_memory_lab")

app = FastAPI(title="ADK + GE streamAssist Session & Memory Bank Lab")

REASONING_ENGINE_RES = os.environ.get(
    "REASONING_ENGINE_RES",
    "projects/545964020693/locations/us-central1/reasoningEngines/1988251824309665792",
)
_re_parts = REASONING_ENGINE_RES.split("/")
RE_PROJECT = _re_parts[1]
RE_LOCATION = _re_parts[3]
RE_ID = _re_parts[5]

DEFAULT_USER_ID = "jesus_e2e_test"

session_service = VertexAiSessionService(
    project=RE_PROJECT, location=RE_LOCATION, agent_engine_id=RE_ID
)
memory_service = VertexAiMemoryBankService(
    project=RE_PROJECT, location=RE_LOCATION, agent_engine_id=RE_ID
)

# Available GE streamAssist targets
GE_TARGETS: Dict[str, Dict[str, str]] = {
    "wif_gcs_10k": {
        "label": "vtxdemos / wif-gcs-eng-jesus-1780519266 (Live 10-K Grounded Store)",
        "project": "vtxdemos",
        "engine": "wif-gcs-eng-jesus-1780519266",
        "datastore": "wif-gcs-ds-jesus-1780519266",
    },
    "sp_streamassist": {
        "label": "545964020693 / streamassist-app (SharePoint 3P Connector)",
        "project": "545964020693",
        "engine": "streamassist-app",
        "datastore": "sharepoint-streamassist-connector_1776274898317_file",
    },
    "sp_wif_default": {
        "label": "545964020693 / gemini-enterprise (SharePoint WIF Connector)",
        "project": "545964020693",
        "engine": "gemini-enterprise",
        "datastore": "sharepoint-data-def-connector_file",
    },
}

_active_target_key = "wif_gcs_10k"
_last_turn_trace: List[Dict[str, Any]] = []


def _get_adc_token() -> str:
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(google.auth.transport.requests.Request())
    return creds.token


def stream_assist_rag(rewritten_query: str, tool_context: ToolContext) -> dict:
    """Search enterprise documents via Gemini Enterprise streamAssist.

    IMPORTANT: Always pass a self-contained, coreference-resolved `rewritten_query`
    that explicitly includes entity names, years, or document names from earlier turns.
    """
    t0 = time.time()
    target_key = tool_context.state.get("ge_target_key") or _active_target_key
    target = GE_TARGETS.get(target_key, GE_TARGETS["wif_gcs_10k"])
    proj = target["project"]
    eng = target["engine"]
    ds = target["datastore"]

    sa_url = (
        f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj}/"
        f"locations/global/collections/default_collection/engines/{eng}/"
        f"assistants/default_assistant:streamAssist"
    )

    existing_ge_session = tool_context.state.get("ge_session_id")
    # Only reuse existing_ge_session if it belongs to the same engine
    if existing_ge_session and f"/engines/{eng}/" not in existing_ge_session:
        existing_ge_session = None

    payload: Dict[str, Any] = {
        "query": {"text": rewritten_query},
        "toolsSpec": {
            "vertexAiSearchSpec": {
                "dataStoreSpecs": [
                    {
                        "dataStore": (
                            f"projects/{proj}/locations/global/collections/"
                            f"default_collection/dataStores/{ds}"
                        )
                    }
                ]
            }
        },
    }
    if existing_ge_session:
        payload["session"] = existing_ge_session

    token = _get_adc_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Goog-User-Project": proj,
        "Content-Type": "application/json",
    }

    session_status = (
        "REUSED_EXISTING_GE_SESSION"
        if existing_ge_session
        else "CREATED_INITIAL_GE_SESSION"
    )

    try:
        r = requests.post(sa_url, headers=headers, json=payload, timeout=30)
        elapsed_s = round(time.time() - t0, 2)
        if not r.ok:
            err_preview = r.text[:400]
            _last_turn_trace.append(
                {
                    "step": "GE_STREAM_ASSIST_ERROR",
                    "http_status": r.status_code,
                    "rewritten_query": rewritten_query,
                    "session_status": session_status,
                    "ge_session_id": existing_ge_session,
                    "duration_s": elapsed_s,
                    "error": err_preview,
                }
            )
            return {
                "status": "error",
                "http_status": r.status_code,
                "message": err_preview,
                "rewritten_query": rewritten_query,
            }

        data = r.json()
        returned_sess = next(
            (
                c.get("sessionInfo", {}).get("session")
                for c in data
                if isinstance(c, dict) and c.get("sessionInfo", {}).get("session")
            ),
            existing_ge_session,
        )
        ans_parts = []
        for c in data:
            if not isinstance(c, dict):
                continue
            for rep in c.get("answer", {}).get("replies", []):
                content = rep.get("groundedContent", {}).get("content", {})
                if content.get("text") and not content.get("thought"):
                    ans_parts.append(content["text"])
        ans = "".join(ans_parts).strip()

        tool_context.state["ge_session_id"] = returned_sess
        tool_context.state["ge_call_count"] = tool_context.state.get("ge_call_count", 0) + 1
        tool_context.state["last_rewritten_query"] = rewritten_query

        _last_turn_trace.append(
            {
                "step": "GE_STREAM_ASSIST_CALL",
                "http_status": 200,
                "target": f"{proj}/{eng}/{ds}",
                "rewritten_query": rewritten_query,
                "session_status": session_status,
                "ge_session_id": returned_sess,
                "duration_s": elapsed_s,
                "answer_preview": ans[:300],
            }
        )
        return {
            "answer": ans,
            "ge_session_id": returned_sess,
            "session_status": session_status,
            "rewritten_query": rewritten_query,
            "duration_s": elapsed_s,
        }
    except Exception as exc:
        elapsed_s = round(time.time() - t0, 2)
        _last_turn_trace.append(
            {
                "step": "GE_STREAM_ASSIST_EXCEPTION",
                "rewritten_query": rewritten_query,
                "duration_s": elapsed_s,
                "error": str(exc),
            }
        )
        return {"status": "exception", "error": str(exc)}


def create_servicenow_ticket(
    short_description: str, details: str, tool_context: ToolContext
) -> dict:
    """Create a ServiceNow / Governance audit ticket using context already in the ADK session."""
    ticket_num = 8840 + int(tool_context.state.get("ge_call_count", 1))
    ticket_id = f"INC-2026-{ticket_num}"
    tool_context.state["last_ticket_id"] = ticket_id
    _last_turn_trace.append(
        {
            "step": "ADK_ACTION_TOOL_ONLY",
            "tool": "create_servicenow_ticket",
            "ticket_id": ticket_id,
            "short_description": short_description,
            "session_status": "BYPASSED_GE_USED_ADK_SESSION_CONTEXT",
            "ge_session_id": tool_context.state.get("ge_session_id"),
            "duration_s": 0.05,
        }
    )
    return {
        "ticket_id": ticket_id,
        "status": "OPEN",
        "short_description": short_description,
        "details": details,
    }


root_agent = Agent(
    name="UnifiedEnterpriseOrchestrator",
    model="gemini-3-flash-preview",
    instruction="""You are an Enterprise Orchestrator combining Gemini Enterprise `streamAssist` RAG, Action tools, and Vertex AI Memory Bank.
1. For any document, financial, SharePoint, or policy question, call `stream_assist_rag`.
2. CRITICAL: When calling `stream_assist_rag` on follow-up questions, ALWAYS resolve pronouns ("it", "its", "that report", "that year") into an explicit, self-contained `rewritten_query` using the ADK conversation history.
3. For ticket creation requests, call `create_servicenow_ticket` using the exact facts already gathered in the ADK session without calling `stream_assist_rag` again unless new document facts are needed.
4. If the user asks about previous sessions or past tickets/audits, use your preloaded memory from Vertex AI Memory Bank to answer accurately.
Keep answers crisp, structured, and concise.""",
    tools=[PreloadMemoryTool(), stream_assist_rag, create_servicenow_ticket],
)

runner = Runner(
    app_name=RE_ID,
    agent=root_agent,
    session_service=session_service,
    memory_service=memory_service,
)


def _serialize_session(session_obj: Any) -> Dict[str, Any]:
    """Converts a VertexAI Session into a clean JSON structure showing the chain."""
    events_out = []
    chain_turns = []
    current_turn: Optional[Dict[str, Any]] = None

    for idx, ev in enumerate(getattr(session_obj, "events", []) or []):
        author = getattr(ev, "author", "unknown")
        content = getattr(ev, "content", None)
        role = getattr(content, "role", author) if content else author
        parts_list = getattr(content, "parts", []) if content else []

        for p in parts_list:
            txt = getattr(p, "text", None)
            fc = getattr(p, "function_call", None)
            fr = getattr(p, "function_response", None)

            if txt and role == "user":
                events_out.append({"index": idx, "type": "USER_PROMPT", "text": txt})
                current_turn = {
                    "turn_number": len(chain_turns) + 1,
                    "user_prompt": txt,
                    "tool_calls": [],
                    "agent_response": "",
                }
                chain_turns.append(current_turn)
            elif fc:
                fc_name = getattr(fc, "name", "")
                fc_args = dict(getattr(fc, "args", {}) or {})
                events_out.append(
                    {"index": idx, "type": "FUNCTION_CALL", "name": fc_name, "args": fc_args}
                )
                if current_turn is not None:
                    current_turn["tool_calls"].append(
                        {"name": fc_name, "args": fc_args, "response": None}
                    )
            elif fr:
                fr_name = getattr(fr, "name", "")
                fr_resp = dict(getattr(fr, "response", {}) or {})
                events_out.append(
                    {
                        "index": idx,
                        "type": "FUNCTION_RESPONSE",
                        "name": fr_name,
                        "response": fr_resp,
                    }
                )
                if current_turn is not None and current_turn["tool_calls"]:
                    current_turn["tool_calls"][-1]["response"] = fr_resp
            elif txt and role != "user":
                events_out.append({"index": idx, "type": "MODEL_RESPONSE", "text": txt})
                if current_turn is not None:
                    current_turn["agent_response"] += txt

    return {
        "session_id": session_obj.id,
        "user_id": getattr(session_obj, "user_id", DEFAULT_USER_ID),
        "reasoning_engine": REASONING_ENGINE_RES,
        "state": dict(getattr(session_obj, "state", {}) or {}),
        "event_count": len(events_out),
        "events": events_out,
        "chain_turns": chain_turns,
    }


class CreateSessionBody(BaseModel):
    user_id: str = Field(default=DEFAULT_USER_ID, max_length=64)
    ge_target_key: str = Field(default="wif_gcs_10k", max_length=64)


class ChatTurnBody(BaseModel):
    session_id: str = Field(..., max_length=128)
    prompt: str = Field(..., min_length=1, max_length=2000)
    user_id: str = Field(default=DEFAULT_USER_ID, max_length=64)
    ge_target_key: str = Field(default="wif_gcs_10k", max_length=64)
    sync_memory: bool = Field(default=True)


@app.get("/")
async def index():
    static_file = os.path.join(os.path.dirname(__file__), "static", "session_memory_lab.html")
    return FileResponse(static_file)


@app.get("/api/overview")
async def get_overview(user_id: str = DEFAULT_USER_ID):
    """Lists all VertexAiSessionService sessions and VertexAiMemoryBankService entries."""
    s_list = await session_service.list_sessions(app_name=RE_ID, user_id=user_id)
    sessions_summary = []
    for s in s_list.sessions:
        sessions_summary.append(
            {
                "session_id": s.id,
                "state": dict(getattr(s, "state", {}) or {}),
                "last_update_time": getattr(s, "last_update_time", None),
            }
        )

    memories_out = []
    try:
        mem_res = await memory_service.search_memory(
            app_name=RE_ID, user_id=user_id, query="user audit ticket sales report"
        )
        for m in getattr(mem_res, "memories", []) or []:
            parts = getattr(getattr(m, "content", None), "parts", []) or []
            txt = "".join(getattr(p, "text", "") for p in parts)
            if txt:
                memories_out.append(
                    {
                        "text": txt,
                        "author": getattr(m, "author", "user"),
                        "timestamp": str(getattr(m, "timestamp", "")),
                    }
                )
    except Exception as exc:
        logger.warning(f"Memory search warning: {exc}")

    return {
        "reasoning_engine": REASONING_ENGINE_RES,
        "user_id": user_id,
        "model": "gemini-3-flash-preview",
        "targets": GE_TARGETS,
        "sessions": sessions_summary,
        "memories": memories_out,
    }


@app.get("/api/session/{session_id}")
async def get_session_detail(session_id: str, user_id: str = DEFAULT_USER_ID):
    s = await session_service.get_session(
        app_name=RE_ID, user_id=user_id, session_id=session_id
    )
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    return _serialize_session(s)


@app.post("/api/session/create")
async def create_new_session(body: CreateSessionBody):
    s = await session_service.create_session(
        app_name=RE_ID,
        user_id=body.user_id,
        state={"ge_target_key": body.ge_target_key, "ge_call_count": 0},
    )
    return _serialize_session(s)


@app.post("/api/chat")
async def run_chat_turn(body: ChatTurnBody):
    global _active_target_key
    _active_target_key = body.ge_target_key
    _last_turn_trace.clear()

    t0 = time.time()
    msg = types.Content(role="user", parts=[types.Part.from_text(text=body.prompt)])
    final_text = ""

    async for ev in runner.run_async(
        user_id=body.user_id, session_id=body.session_id, new_message=msg
    ):
        if ev.content and ev.content.parts:
            for part in ev.content.parts:
                if part.text:
                    final_text += part.text

    updated_session = await session_service.get_session(
        app_name=RE_ID, user_id=body.user_id, session_id=body.session_id
    )

    memory_synced = False
    if body.sync_memory and updated_session:
        try:
            await memory_service.add_session_to_memory(updated_session)
            memory_synced = True
        except Exception as exc:
            logger.warning(f"Memory Bank sync warning: {exc}")

    total_duration_s = round(time.time() - t0, 2)
    return JSONResponse(
        {
            "reply": final_text,
            "duration_s": total_duration_s,
            "memory_synced": memory_synced,
            "turn_trace": list(_last_turn_trace),
            "session": _serialize_session(updated_session),
        }
    )


@app.post("/api/session/{session_id}/sync-memory")
async def manual_sync_memory(session_id: str, user_id: str = DEFAULT_USER_ID):
    s = await session_service.get_session(
        app_name=RE_ID, user_id=user_id, session_id=session_id
    )
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    await memory_service.add_session_to_memory(s)
    return {"status": "synced", "session_id": session_id}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("LAB_PORT", "8094"))
    # Mandatory Secure Web Skills: bind strictly to 127.0.0.1 for local testing
    uvicorn.run(app, host="127.0.0.1", port=port)
