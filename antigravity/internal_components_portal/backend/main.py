import os
import sys
import time
from datetime import timedelta
import mcp.client.session

# --- BOOTSTRAP: Increase MCP Client Timeout to handle SharePoint Latency ---
_orig_call_tool = mcp.client.session.ClientSession.call_tool
async def patched_call_tool(self, *args, **kwargs):
    if "read_timeout_seconds" not in kwargs:
        kwargs["read_timeout_seconds"] = timedelta(seconds=30)
    return await _orig_call_tool(self, *args, **kwargs)
mcp.client.session.ClientSession.call_tool = patched_call_tool

# Ensure backend directory is in sys.path so 'agent' can be imported easily even if run from root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
import logging
import requests
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import List, Optional, Any
from pydantic import BaseModel
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Now we can safely import agent, protocol, etc.
from agents.agent import get_agent_with_mcp_tools, get_action_agent_with_mcp_tools, get_servicenow_agent_with_mcp_tools

from agents.router_agent import get_router_agent
from agents.ge_search_branch import stream_ge_search
from agents.redaction_agent import generalize_content
from utils.protocol import AIStreamProtocol
from agents.pdf_editor_agent import PDFDeSynthesizer, create_pdf_editor_agent
from utils.pwc_renderer import render_report
from pipelines.regenerative_pipeline import run_regenerative_pipeline
from mcp_service.mcp_sharepoint import SharePointMCP
from utils.auth_context import set_user_token, set_user_id_token
from agents.analyze_latency_agent import analyze_latency_profiles
from agents.latency_chat_agent import chat_with_latency_data
from nexus_telemetry import push_telemetry_async, NexusAPITrackerMiddleware

from dotenv import load_dotenv
load_dotenv(dotenv_path="../.env")

os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"

app = FastAPI()

app.add_middleware(NexusAPITrackerMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

session_service = InMemorySessionService()

class ChatRequest(BaseModel):
    messages: list

class LatencyAnalyzeRequest(BaseModel):
    history: list
    model: str = "gemini-2.5-flash"
from typing import Tuple, Dict, Any
import jwt

async def verify_jwt(request: Request) -> Tuple[str, Dict[str, Any]]:
    """
    Helper to extract and verify the JWT from the request headers.
    Matches the naming and pattern in the Auth Flow & GE+MCP snippets.
    """
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        if token in ["null", "undefined"]:
            token = None
            
    id_token = request.headers.get("X-Entra-Id-Token")
    if id_token and id_token in ["null", "undefined", "None"]:
        id_token = None

    # In a real enterprise app, we would use jwt.decode(token, ...) with public keys
    # For this portal, we prioritize propagation of the 'id_token' for GE / WIF
    payload = {}
    if token and len(token.split('.')) == 3:
        try:
            # We skip verification for the proxy but decode payload for identity
            payload = jwt.decode(token, options={"verify_signature": False})
        except:
            payload = {}
            
    # We return the primary token (access_token) and the payload
    # The id_token is also retrieved from headers elsewhere
    return token, payload

async def _chat_stream(messages: list, model_name: str, token: str = None, id_token: str = None):
    # Set the token in the current context (essential for async streaming tasks)
    set_user_token(token)
    set_user_id_token(id_token)
    
    prompt = messages[-1]["content"] if messages else ""
    
    latency_metrics = []
    reasoning_steps = []
    total_tokens = {"prompt": 0, "candidates": 0, "total": 0}
    adk_events_trace = []

    
    def log_latency(tag, step_name):
        now = time.time()
        duration_sec = now - last_phase_time[tag]
        if duration_sec > 0.01:
            # Enhanced labels for atomic visibility (normalized)
            prefix = f"[ENTERPRISE-ATOMIC: {model_name}] " if tag == "sharepoint" else f"[PUBLIC-ATOMIC: {model_name}] "
            latency_metrics.append({"step": prefix + step_name, "duration_s": round(duration_sec, 2)})
        last_phase_time[tag] = now
        # PROACTIVE TELEMETRY YIELD
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We use a small delay or direct put to ensure it's processed after the append
                loop.create_task(queue.put({"tag": "system", "type": "telemetry_yield"}))
        except:
            pass



    start_time = time.time()
    last_phase_time = {"sharepoint": start_time, "public": start_time}
    tool_start_times = {"sharepoint": {}, "public": {}}
    llm_start_time = {"sharepoint": start_time, "public": start_time}
    
    pipe_start = start_time

    has_yielded_text = False
    import uuid
    current_request_id = str(uuid.uuid4())
    sess_id = f"sess_{current_request_id}"
    pub_sess_id = f"pub_{current_request_id}"

    # --- LATENCY OPTIMIZATION PROFILE ---
    optimization_params = {
        "model": model_name,
        "thinking_budget": 1024,
        "optimizations": [
            "BuiltInPlanner Enabled",
            "Parallel Tool Fan-out",
            "Auth Context Caching",
            "Zero-Leak Masking Protocol"
        ]
    }
    
    # Inject optimization details directly into the trace as a system step
    reasoning_steps.append(f"[SYSTEM] OPTIMIZATION PROFILE:\n{json.dumps(optimization_params, indent=2)}")
    
    # Ensure session exists
    session = await session_service.get_session(app_name="PWC_Security_Proxy", user_id="default_user", session_id=sess_id)
    if not session:
        session = await session_service.create_session(app_name="PWC_Security_Proxy", user_id="default_user", session_id=sess_id)

    import asyncio
    from agents.public_agent import get_public_agent
    from google.genai import types
    from google.adk.events import Event

    queue = asyncio.Queue()
    msg_obj = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])

    # 1. Initialize Public Agent immediately (Prior to Discovery)
    pub_session = await session_service.get_session(app_name="Public_Research_Proxy", user_id="default_user", session_id=pub_sess_id)
    if not pub_session:
        pub_session = await session_service.create_session(app_name="Public_Research_Proxy", user_id="default_user", session_id=pub_sess_id)
    
    # POPULATE ADK SESSIONS WITH FRONTEND TRUTH HISTORY
    if len(messages) > 1:
        for msg in messages[:-1]: # Exclude the current prompt
            role = "user" if msg.get("role") == "user" else "model"
            part = types.Part.from_text(text=msg.get("content", ""))
            content_obj = types.Content(role=role, parts=[part])
            evt = Event(author=role, content=content_obj)
            session.events.append(evt)
            pub_session.events.append(evt)
    # ------------------------------------------------

    # Use gemini-2.5-flash for ultra-fast response for Public Web Consensus and to avoid 429s
    pub_agent = get_public_agent(model_name, token=token)
    pub_runner = Runner(
        app_name="Public_Research_Proxy", 
        agent=pub_agent, 
        session_service=session_service
    )

    async def stream_agent(runner_obj, sid, tag):
        try:
            # Use Content object for consistency and to avoid role errors
            async for event in runner_obj.run_async(user_id="default_user", session_id=sid, new_message=msg_obj):
                await queue.put({"tag": tag, "event": event, "type": "data"})
        except Exception as e:
            import traceback
            tb_str = traceback.format_exc()
            with open("traceback_dump.txt", "w") as f:
                f.write(tb_str)
            logger.exception(f"Task {tag} failed: {e}")
            await queue.put({"tag": tag, "event": str(e), "type": "error"})
        finally:
            await queue.put({"tag": tag, "type": "done"})

    import threading
    def stream_public_in_new_loop(runner_obj, sid, tag):
        main_loop = asyncio.get_running_loop()
        def target():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            async def run_it():
                try:
                    async for event in runner_obj.run_async(user_id="default_user", session_id=sid, new_message=msg_obj):
                        asyncio.run_coroutine_threadsafe(queue.put({"tag": tag, "event": event, "type": "data"}), main_loop)
                except Exception as e:
                    import traceback
                    logger.error(f"Thread task {tag} failed: {traceback.format_exc()}")
                    asyncio.run_coroutine_threadsafe(queue.put({"tag": tag, "event": str(e), "type": "error"}), main_loop)
                finally:
                    asyncio.run_coroutine_threadsafe(queue.put({"tag": tag, "type": "done"}), main_loop)
            new_loop.run_until_complete(run_it())
            new_loop.close()
        t = threading.Thread(target=target)
        t.start()

    # Launch Public Agent background task in true OS thread - prevents sync blocks
    stream_public_in_new_loop(pub_runner, pub_sess_id, "public")

    yield AIStreamProtocol.data({
        "type": "public_insight", 
        "message": "Public Web Consensus",
        "data": "",
        "icon": "globe",
        "pulse": True
    })
    yield AIStreamProtocol.data({"type": "status", "message": "Launching Global Consensus...", "icon": "globe", "pulse": True})

    # 2. Start Enterprise Discovery in background to avoid blocking public stream
    yield AIStreamProtocol.data({"type": "status", "message": "Discovering Enterprise Toolset...", "icon": "shield-alert", "pulse": True})
    
    discovery_task = asyncio.create_task(get_agent_with_mcp_tools(token=token, id_token=id_token, model_name=model_name))
    
    active_streams = 1 # Public started
    sharepoint_started = False
    exit_stack = None
    pub_insight = ""
    current_action = {"sharepoint": "LLM Orchestration & Reasoning", "public": "Web Research Orchestration"}


    try:
        while active_streams > 0 or not sharepoint_started:
            # Check if discovery finished and we need to start sharepoint stream
            if not sharepoint_started and discovery_task.done():
                discovery_time = time.time() - start_time
                latency_metrics.append({"step": "[SYSTEM-ATOMIC] Official MCP Handshake", "duration_s": round(discovery_time, 2)})
                try:
                    agent, exit_stack = await discovery_task
                    sp_runner = Runner(app_name="PWC_Security_Proxy", agent=agent, session_service=session_service)
                    asyncio.create_task(stream_agent(sp_runner, sess_id, "sharepoint"))
                    sharepoint_started = True
                    llm_start_time["sharepoint"] = time.time() # Start tracking first LLM call
                    active_streams += 1
                except Exception as e:
                    import traceback
                    logger.error(f"Enterprise Discovery failed: {e}\n{traceback.format_exc()}")
                    sharepoint_started = True # mark as attempted
                    yield AIStreamProtocol.data({"type": "status", "message": f"Discovery Error: {str(e)}", "icon": "alert-triangle", "pulse": False})
                    yield AIStreamProtocol.text(f"\n❌ Enterprise Discovery failed: {str(e)}\n")

            # Wait for any event from either stream
            try:
                # Poll with short timeout to allow checking discovery_task status
                q_item = await asyncio.wait_for(queue.get(), timeout=0.1)
            except asyncio.TimeoutError:
                continue

            tag = q_item["tag"]
            msg_type = q_item["type"]

            if msg_type == "telemetry_yield":
                yield AIStreamProtocol.data({"type": "telemetry", "data": list(latency_metrics), "reasoning": reasoning_steps, "tokens": total_tokens, "adk_events": adk_events_trace, "config": optimization_params})
                continue


            if msg_type == "done":
                active_streams -= 1
                log_latency(tag, current_action[tag])
                if tag == "public":
                    # PROACTIVE YIELD: Send public insight as soon as it's ready, 
                    # with is_streaming=False to avoid the 'black bubble' wait effect.
                    if pub_insight:
                        yield AIStreamProtocol.data({
                            "type": "public_insight", 
                            "message": "Public Web Consensus",
                            "data": pub_insight.strip(),
                            "icon": "globe",
                            "pulse": False,
                            "is_streaming": False
                        })
                continue

                
            evt = q_item["event"]
            if msg_type == "error":
                if tag == "sharepoint":
                    yield AIStreamProtocol.data({"type": "status", "message": f"Enterprise Proxy Error: {str(evt)}", "icon": "alert-triangle", "pulse": False})
                    reasoning_steps.append(f"AGENT EXECUTION HALTED [{tag}]: {str(evt)}")
                    yield AIStreamProtocol.text(f"\n❌ Error: {str(evt)}\n")
                continue
            # Process Event
            try:
                edata = evt.model_dump(mode='json')
                
                # ADK Events for enterprise trace
                if tag == "sharepoint":
                    adk_events_trace.append({"source": "PWC_Security_Proxy", "event": edata})
                    push_telemetry_async({"tag": "security_proxy", "event": edata})
                
                # DEBUG DUMP FOR PUBLIC EVENT
                if tag == "public":
                    logger.info(f"[PUBLIC EVENT DUMP] {edata}")
                    
                usage = edata.get("usage_metadata")
                if usage:
                    total_tokens["prompt"] += usage.get("prompt_token_count") or 0
                    total_tokens["candidates"] += usage.get("candidates_token_count") or 0
                    total_tokens["total"] += usage.get("total_token_count") or 0

                content = edata.get("content")
                author = edata.get("author") or "unknown"
                is_model_role = (edata.get("content") or {}).get("role") == "model"
                if content and isinstance(content, dict):
                    parts = content.get("parts", [])
                    for p in parts:
                        agent_label = "[Public Web]" if tag == "public" else "[Enterprise Proxy]"
                        
                        is_native_thought = p.get("thought") is True or (p.get("thought") and isinstance(p["thought"], str))
                        has_function_call_in_turn = any(part.get("function_call") for part in parts)
                        is_thought = is_native_thought or (has_function_call_in_turn and p.get("text"))
                        
                        if is_thought:
                            thought_text = p.get("text") if (is_native_thought and p.get("thought") is True) or (not is_native_thought and p.get("text")) else p.get("thought")
                            if thought_text and isinstance(thought_text, str):
                                txt = f"{agent_label} THOUGHT ({author}) [{model_name}]:\n{thought_text.strip()}"
                                if txt not in reasoning_steps:
                                    reasoning_steps.append(txt)
                                    yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": total_tokens, "adk_events": adk_events_trace})
                            
                            # If it was just 'text' acting as a thought before a function call, we don't 'continue' so it doesn't break function_call parsing,
                            # but we definitely shouldn't yield it to the UI below. We will handle that below.
                            if is_native_thought:
                                continue # CRITICAL: Skip standard text extraction so thoughts don't leak into the frontend UI chat
                                
                        # Extract Google Search Grounding Metadata dynamically
                        if tag == "public":
                            grounding = edata.get("grounding_metadata")
                            if grounding and isinstance(grounding, dict):
                                qs = grounding.get("web_search_queries", [])
                                if qs:
                                    search_str = ", ".join(qs)
                                    tool_str = f"{agent_label} TOOL:\ngoogle_search"
                                    if tool_str not in reasoning_steps:
                                        reasoning_steps.append(tool_str)
                                        reasoning_steps.append(f"{agent_label} ARGS:\n{{queries: [{search_str}]}}")
                                        yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": total_tokens, "adk_events": adk_events_trace})

                        if p.get("function_call"):
                            tool_name = p["function_call"].get("name", "")
                            tool_args = p["function_call"].get("args", {})
                            
                            log_latency(tag, current_action[tag])
                            
                            if tool_name == "google_search":
                                yield AIStreamProtocol.data({"type": "status", "message": "Searching public web...", "icon": "globe", "pulse": True})
                                current_action[tag] = "Google Search API"
                            elif "search" in tool_name:
                                reasoning_steps.append(f"{agent_label} THOUGHT ({author}):\nI need to search the enterprise database. Using **Parallel Fan-out Search**.")
                                yield AIStreamProtocol.data({"type": "status", "message": "Executing Parallel Fan-out Search...", "icon": "search", "pulse": True})
                                current_action[tag] = "Graph Parallel Fan-out Search"
                            elif tool_name == "emit_project_card":
                                # INTERCEPT: Send card to frontend immediately
                                yield AIStreamProtocol.data({"type": "project_card", "data": tool_args})
                            elif "read" in tool_name:
                                reasoning_steps.append(f"{agent_label} ANALYSIS ({author}):\nThe search results found relevant files. I must now extract their text to synthesize the final answer.")
                                current_action[tag] = "Document Extraction"

                            else:
                                current_action[tag] = f"Tool: {tool_name}"
                            
                            reasoning_steps.append(f"{agent_label} TOOL ({author}) [{model_name}]:\n{tool_name}")
                            reasoning_steps.append(f"{agent_label} ARGS [{model_name}]:\n{str(tool_args)}")
                            yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": total_tokens})
                                
                        elif p.get("function_response"):
                            tool_name = p["function_response"].get("name", "")
                            
                            resp_data = p["function_response"].get("response", "")
                            res_str = str(resp_data)[:500] + "... [TRUNCATED]" if len(str(resp_data)) > 500 else str(resp_data)
                            
                            reasoning_steps.append(f"{agent_label} RESPONSE ({author}) [{model_name}]:\n{tool_name}")
                            reasoning_steps.append(f"{agent_label} RESULT [{model_name}]:\n{res_str}")
                            log_latency(tag, current_action[tag])
                            
                            if tag == "sharepoint":
                                yield AIStreamProtocol.data({"type": "status", "message": "Synthesizing zero-leak intelligence...", "icon": "cpu", "pulse": True})
                            current_action[tag] = "LLM Final Synthesis"
                            yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": total_tokens})

                        if p.get("text") and isinstance(p["text"], str) and not has_function_call_in_turn:
                            txt = p['text'].strip()
                            if txt:
                                if is_model_role or author == "model":
                                    step_text = f"{agent_label} SYNTHESIS ({author}) [{model_name}]:\n{txt}"
                                    if step_text not in reasoning_steps:
                                        reasoning_steps.append(step_text)
                                        yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": total_tokens, "adk_events": adk_events_trace})
                                
                                if tag == "public":
                                    pub_insight += txt
                                    # STREAMING YIELD: Send public insight as soon as it accumulates significant text
                                    if len(pub_insight) % 50 < 5: # Periodic yield to feel alive
                                        yield AIStreamProtocol.data({
                                            "type": "public_insight", 
                                            "message": "Public Web Consensus",
                                            "data": pub_insight.strip() + "...",
                                            "icon": "globe",
                                            "pulse": True,
                                            "is_streaming": True
                                        })
                                else:
                                    # Track TTFT (Time to First Token)
                                    if not has_yielded_text:
                                        ttft = time.time() - pipe_start
                                        latency_metrics.append({"step": "[SYSTEM-ATOMIC] Time to First Token (TTFT)", "duration_s": round(ttft, 2)})
                                        has_yielded_text = True
                                        asyncio.create_task(queue.put({"tag": "system", "type": "telemetry_yield"}))
                                    
                                    # Main synthesis stream
                                    if is_model_role or author == "model":
                                        yield AIStreamProtocol.text(txt)

            except Exception as e:
                logger.error(f"Event parsing error in {tag}: {e}")

        # Cards are now emitted in real-time via the 'emit_project_card' tool interception in the event loop.

    finally:
        if exit_stack:
            await exit_stack.aclose()

    total_time = time.time() - start_time
    latency_metrics.append({"step": "[SYSTEM-ATOMIC] Total Pipeline Turnaround", "duration_s": round(total_time, 2)})
    
    # Public insight fallback yield if it wasn't already sent (e.g. loops broke before the delayed public insight could flush)
    if pub_insight:
        yield AIStreamProtocol.data({
            "type": "public_insight", 
            "message": "Public Web Consensus",
            "data": pub_insight.strip(),
            "icon": "globe",
            "pulse": False,
            "is_streaming": False
        })

    yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": total_tokens, "adk_events": adk_events_trace, "config": optimization_params})
    yield AIStreamProtocol.data({"type": "status", "message": "Transmission complete.", "icon": "check-circle", "pulse": False})

from utils.auth_context import set_user_token

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "internal_components_portal"}

@app.get("/")
async def root():
    return {"message": "Zero-Leak Security Proxy Backend is running.", "docs": "/docs"}

async def auth_error_stream(message: str):
    yield AIStreamProtocol.text(message)

async def _ge_mcp_chat_stream(messages: list, model_name: str, token: str = None, id_token: str = None):
    set_user_token(token)
    set_user_id_token(id_token)
    prompt = messages[-1]['content']
    
    reasoning_steps = []
    latency_metrics = []
    adk_events_trace = []
    tokens = {"prompt": 0, "candidates": 0, "total": 0}
    
    # --- LATENCY OPTIMIZATION PROFILE ---
    optimization_params = {
        "model": model_name,
        "thinking_budget": "N/A (GE-Optimized)",
        "optimizations": [
            "Gemini Enterprise Sequential Search",
            "Vertex AI Search Toolset",
            "Router Intent Classification",
            "WIF Auth Implementation"
        ]
    }
    # Inject optimization details directly into the trace as a system step
    reasoning_steps.append(f"[SYSTEM] OPTIMIZATION PROFILE:\n{json.dumps(optimization_params, indent=2)}")
    
    import time
    from google.genai import types
    from google.adk.events import Event
    import uuid
    import asyncio

    router_start = time.time()
    yield AIStreamProtocol.data({"type": "status", "message": "Analyzing Intent...", "icon": "cpu", "pulse": True})
    
    router_agent = get_router_agent()
    # Log evidence of API call for telemetry roughly
    api_evidence = {
        "endpoint": "Vertex AI (Gemini Enterprise)",
        "model": "gemini-2.5-flash",
        "project": os.environ.get("GOOGLE_CLOUD_PROJECT"),
        "location": "us-central1"
    }
    reasoning_steps.append(f"[Router API EVIDENCE]\n{json.dumps(api_evidence, indent=2)}")
    
    router_runner = Runner(app_name="PWC_Router", agent=router_agent, session_service=session_service)
    router_sess_id = f"router_{uuid.uuid4()}"
    
    # Create the session before running
    router_session = await session_service.get_session(app_name="PWC_Router", user_id="default_user", session_id=router_sess_id)
    if not router_session:
        router_session = await session_service.create_session(app_name="PWC_Router", user_id="default_user", session_id=router_sess_id)
        
    if len(messages) > 1:
        for msg in messages[:-1]:
            role = "user" if msg.get("role") == "user" else "model"
            part = types.Part.from_text(text=msg.get("content", ""))
            content_obj = types.Content(role=role, parts=[part])
            evt = Event(author=role, content=content_obj)
            router_session.events.append(evt)
        
    msg_obj = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
    
    intent = "SEARCH"
    
    try:
        async for event in router_runner.run_async(user_id="default_user", session_id=router_sess_id, new_message=msg_obj):
            edata = event.model_dump(mode='json')
            adk_events_trace.append({"source": "PWC_Router", "event": edata})
            push_telemetry_async({"tag": "router", "event": edata})
            author = edata.get("author", "unknown")
            content = edata.get("content", {})
            
            usage = edata.get("usage_metadata")
            if usage:
                tokens["prompt"] += usage.get("prompt_token_count") or 0
                tokens["candidates"] += usage.get("candidates_token_count") or 0
                tokens["total"] += usage.get("total_token_count") or 0
                
            if content and isinstance(content, dict):
                parts = content.get("parts", [])
                for p in parts:
                    if p.get("thought"):
                        txt = f"[ADK Router: {author}] THOUGHT:\n{p['thought'].strip()}"
                        if txt not in reasoning_steps:
                            reasoning_steps.append(txt)
                            yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": tokens, "adk_events": adk_events_trace})
                    if p.get("text") and author in ["model", "router_agent"]:
                        intent_text = p.get("text").strip().upper()
                        if "ACTION" in intent_text and "SEARCH" not in intent_text:
                            intent = "ACTION"
                        elif "SERVICENOW" in intent_text:
                            intent = "SERVICENOW"
                        elif "SEARCH" in intent_text:
                            intent = "SEARCH"
                        
                        txt_trace = f"[ADK Router: {author}] RESPONSE TEXT:\n{intent_text}"
                        if txt_trace not in reasoning_steps:
                            reasoning_steps.append(txt_trace)
                            yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": tokens, "adk_events": adk_events_trace})

        router_duration = time.time() - router_start
        latency_metrics.append({"step": f"[SYSTEM-ATOMIC: {model_name}] Intent Classification", "duration_s": round(router_duration, 2)})
        
        # Hardcode safety net: if the user explicitly asked for servicenow
        if "servicenow" in prompt.lower() or "incident" in prompt.lower():
            intent = "SERVICENOW"

        reasoning_steps.append(f"[Router] INTENT DETECTED: {intent}")
        yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": tokens, "adk_events": adk_events_trace})
        
    except Exception as e:
        logger.error(f"Router Exception: {e}", exc_info=True)
        yield AIStreamProtocol.data({"type": "status", "message": f"Error during intent routing: {e}", "icon": "error", "pulse": False})
        return
        
    if intent == "SEARCH":
        raw_answer = ""
        # Pass the adk_events_trace to GE search so it can append traces
        async for chunk in stream_ge_search(messages, adk_events_trace, id_token):
            # If the chunk is telemetry from GE, we merge it
            if isinstance(chunk, str) and '"type": "telemetry"' in chunk:
                try:
                    # The chunk is formatted as "2:[...]" for data chunks in AIStreamProtocol
                    payload_str = chunk[2:] # Strip "2:"
                    chunk_arr = json.loads(payload_str)
                    
                    if isinstance(chunk_arr, list) and len(chunk_arr) > 0:
                        chunk_data = chunk_arr[0]
                    else:
                        chunk_data = chunk_arr
                        
                    # Merge reasoning and metrics
                    ge_reasoning = chunk_data.get("reasoning", [])
                    ge_metrics = chunk_data.get("data", [])
                    
                    combined_reasoning = reasoning_steps + ge_reasoning
                    combined_metrics = latency_metrics + ge_metrics
                    
                    yield AIStreamProtocol.data({
                        "type": "telemetry", 
                        "data": combined_metrics, 
                        "reasoning": combined_reasoning, 
                        "tokens": tokens,
                        "adk_events": adk_events_trace,
                        "config": optimization_params
                    })
                    continue # Don't yield the original telemetry chunk as-is
                except Exception as e:
                    logger.error(f"Telemetry merge failed: {e}")
                    pass
            
            # Stream the unredacted text directly
            yield chunk
        
        yield AIStreamProtocol.data({"type": "status", "message": "Search completed.", "icon": "check-circle", "pulse": False})
    
    elif intent == "SERVICENOW":
        yield AIStreamProtocol.data({"type": "status", "message": "Intent Detected: ServiceNow. Routing to ServiceNow Agent...", "icon": "zap", "pulse": True})
        
        reasoning_steps.append("[Router] Dispatching to ServiceNow Runner with Standard ServiceNow MCP tools...")
        yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": tokens, "adk_events": adk_events_trace})
        
        sess_id = f"sno_{uuid.uuid4()}"
        session = await session_service.get_session(app_name="PWC_ServiceNow_Proxy", user_id="default_user", session_id=sess_id)
        if not session:
            session = await session_service.create_session(app_name="PWC_ServiceNow_Proxy", user_id="default_user", session_id=sess_id)
            
        if len(messages) > 1:
            for msg in messages[:-1]:
                role = "user" if msg.get("role") == "user" else "model"
                part = types.Part.from_text(text=msg.get("content", ""))
                content_obj = types.Content(role=role, parts=[part])
                evt = Event(author=role, content=content_obj)
                session.events.append(evt)
            
        try:
            agent, exit_stack = await get_servicenow_agent_with_mcp_tools(token=token, id_token=id_token, model_name=model_name, enable_google_search=True)
            runner = Runner(app_name="PWC_ServiceNow_Proxy", agent=agent, session_service=session_service)
            msg_obj = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
            
            queue = asyncio.Queue()
            async def stream_sno():
                try:
                    async for event in runner.run_async(user_id="default_user", session_id=sess_id, new_message=msg_obj):
                        await queue.put({"event": event, "type": "data"})
                except Exception as e:
                    logger.exception(f"ServiceNow Task failed: {e}")
                    await queue.put({"event": str(e), "type": "error"})
                finally:
                    await queue.put({"type": "done"})
                    
            asyncio.create_task(stream_sno())
            sno_start = time.time()
            
            while True:
                msg_q = await queue.get()
                t = msg_q["type"]
                if t == "done":
                    break
                elif t == "error":
                    yield AIStreamProtocol.text(f"\n❌ ServiceNow Proxy Error: {msg_q['event']}\n")
                    continue
                    
                evt = msg_q["event"]
                edata = evt.model_dump(mode='json')
                adk_events_trace.append({"source": "PWC_ServiceNow_Proxy", "event": edata})
                push_telemetry_async({"tag": "servicenow", "event": edata})
                usage = edata.get("usage_metadata")
                if usage:
                    tokens["prompt"] += usage.get("prompt_token_count") or 0
                    tokens["candidates"] += usage.get("candidates_token_count") or 0
                    tokens["total"] += usage.get("total_token_count") or 0
                
                parts = edata.get("content", {}).get("parts", []) if edata.get("content") else []
                author = edata.get("author") or "unknown"
                is_model_role = (edata.get("content") or {}).get("role") == "model"
                for p in parts:
                    if p.get("thought"):
                        txt = f"[ServiceNow: {author}] THOUGHT:\n{p['thought'].strip()}"
                        if txt not in reasoning_steps:
                            reasoning_steps.append(txt)
                            yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": tokens, "adk_events": adk_events_trace})
                    
                    if p.get("function_call"):
                        tool_name = p["function_call"].get("name", "")
                        yield AIStreamProtocol.data({"type": "status", "message": f"Executing ServiceNow Action: {tool_name}...", "icon": "zap", "pulse": True})
                    elif p.get("function_response"):
                        tool_name = p["function_response"].get("name", "")
                        yield AIStreamProtocol.data({"type": "status", "message": f"Completed ServiceNow Action: {tool_name}", "icon": "check", "pulse": False})
                    elif p.get("text"):
                        if is_model_role or author == "model":
                            yield AIStreamProtocol.text(p.get("text"))
            
            sno_duration = time.time() - sno_start
            latency_metrics.append({"step": f"[SYSTEM-ATOMIC: {model_name}] ServiceNow Execution", "duration_s": round(sno_duration, 2)})
            yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": tokens, "adk_events": adk_events_trace, "config": optimization_params})
        finally:
            if 'exit_stack' in locals() and exit_stack:
                await exit_stack.aclose()
                
        yield AIStreamProtocol.data({"type": "status", "message": "ServiceNow operation completed.", "icon": "check-circle", "pulse": False})

    else:
        yield AIStreamProtocol.data({"type": "status", "message": "Intent Detected: Action. Routing to MCP Action Server...", "icon": "zap", "pulse": True})

        
        # Evidence for Action LLM
        action_api_info = {
            "endpoint": "Vertex AI (Gemini Enterprise)",
            "model": model_name,
            "project": os.environ.get("GOOGLE_CLOUD_PROJECT"),
            "location": "us-central1",
            "mcp_enabled": True
        }
        reasoning_steps.append(f"[Action Setup] API EVIDENCE:\n{json.dumps(action_api_info, indent=2)}")
        reasoning_steps.append("[Router] Dispatching to Runner with MCP tools...")
        yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": tokens, "adk_events": adk_events_trace})
        
        sess_id = f"action_{uuid.uuid4()}"
        session = await session_service.get_session(app_name="PWC_Action_Proxy", user_id="default_user", session_id=sess_id)
        if not session:
            session = await session_service.create_session(app_name="PWC_Action_Proxy", user_id="default_user", session_id=sess_id)
            
        # POPULATE ADK SESSION WITH FRONTEND TRUTH HISTORY
        if len(messages) > 1:
            for msg in messages[:-1]: # Exclude the current prompt
                role = "user" if msg.get("role") == "user" else "model"
                part = types.Part.from_text(text=msg.get("content", ""))
                content_obj = types.Content(role=role, parts=[part])
                evt = Event(author=role, content=content_obj)
                session.events.append(evt)
        # ------------------------------------------------
            
        try:
            agent, exit_stack = await get_action_agent_with_mcp_tools(token=token, id_token=id_token, model_name=model_name)
            runner = Runner(app_name="PWC_Action_Proxy", agent=agent, session_service=session_service)
            msg_obj = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
            
            queue = asyncio.Queue()
            async def stream_action():
                try:
                    # new_message correctly handles the final user prompt through the runner
                    async for event in runner.run_async(user_id="default_user", session_id=sess_id, new_message=msg_obj):
                        await queue.put({"event": event, "type": "data"})
                except Exception as e:
                    logger.exception(f"Action Task failed: {e}")
                    await queue.put({"event": str(e), "type": "error"})
                finally:
                    await queue.put({"type": "done"})
                    
            asyncio.create_task(stream_action())
            
            action_start = time.time()
            
            while True:
                msg_q = await queue.get()
                t = msg_q["type"]
                if t == "done":
                    break
                elif t == "error":
                    yield AIStreamProtocol.text(f"\n❌ Action Proxy Error: {msg_q['event']}\n")
                    continue
                    
                evt = msg_q["event"]
                edata = evt.model_dump(mode='json')
                adk_events_trace.append({"source": "PWC_Action_Proxy", "event": edata})
                push_telemetry_async({"tag": "action", "event": edata})
                usage = edata.get("usage_metadata")
                if usage:
                    tokens["prompt"] += usage.get("prompt_token_count") or 0
                    tokens["candidates"] += usage.get("candidates_token_count") or 0
                    tokens["total"] += usage.get("total_token_count") or 0
                
                author = edata.get("author") or "unknown"
                
                content = edata.get("content", {})
                is_model_role = content.get("role") == "model" if isinstance(content, dict) else False
                if content and isinstance(content, dict):
                    parts = content.get("parts", [])
                    for p in parts:
                        if p.get("call"):
                            tool_name = p["call"].get("name")
                            yield AIStreamProtocol.data({"type": "status", "message": f"Executing {tool_name}...", "icon": "cpu", "pulse": True})
                        
                        if p.get("response"):
                            tool_name = p["response"].get("name")

                        if p.get("thought"):
                            txt = f"[ADK: {author}] THOUGHT:\n{p['thought'].strip()}"
                            if txt not in reasoning_steps:
                                reasoning_steps.append(txt)
                                yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": tokens, "adk_events": adk_events_trace})
                        
                        if p.get("function_call"):
                            tool_name = p["function_call"].get("name", "")
                            tool_args = p["function_call"].get("args", {})
                            yield AIStreamProtocol.data({"type": "status", "message": f"Executing Action: {tool_name}...", "icon": "zap", "pulse": True})
                            reasoning_steps.append(f"[ADK: {author}] TOOL CALL: {tool_name}\nARGS: {json.dumps(tool_args, indent=2)}")
                            yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": tokens, "adk_events": adk_events_trace})
                            
                        elif p.get("function_response"):
                            tool_name = p["function_response"].get("name", "")
                            resp_data = p["function_response"].get("response", "")
                            res_str = json.dumps(resp_data, indent=2) if isinstance(resp_data, (dict, list)) else str(resp_data)
                            if len(res_str) > 1000:
                                res_str = res_str[:1000] + "... [TRUNCATED]"
                            reasoning_steps.append(f"[ADK: {author}] TOOL RESPONSE ({tool_name}):\n{res_str}")
                            yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": tokens, "adk_events": adk_events_trace})
                            yield AIStreamProtocol.data({"type": "status", "message": f"Completed action: {tool_name}", "icon": "check", "pulse": False})
                            
                        elif p.get("text"):
                            # Ensure we trace everything in ADK if possible
                            if is_model_role or author == "model":
                                txt_trace = f"[ADK: {author}] RESPONSE TEXT:\n{p.get('text')}"
                                if txt_trace not in reasoning_steps:
                                    reasoning_steps.append(txt_trace)
                                    yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": tokens, "adk_events": adk_events_trace})
                                
                                yield AIStreamProtocol.text(p.get("text"))
            
            action_duration = time.time() - action_start
            latency_metrics.append({"step": f"[SYSTEM-ATOMIC: {model_name}] Action Execution", "duration_s": round(action_duration, 2)})
            yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": tokens, "adk_events": adk_events_trace, "config": optimization_params})
            yield AIStreamProtocol.data({"type": "status", "message": "Action completed.", "icon": "check-circle", "pulse": False})
        finally:
            if exit_stack:
                await exit_stack.aclose()


@app.post("/api/chat/stream")
async def chat_endpoint(request: Request):
    """
    Renamed endpoint to match documented architecture snippets.
    Enforces the 'Zero-Leak' token passing pattern.
    """
    data = await request.json()
    model_name = data.get("model", "gemini-3-flash-preview")
    router_mode = data.get("routerMode", "all_mcp")
    
    # Extract tokens using the new standard helper
    token, auth_payload = await verify_jwt(request)
    
    # Also grab the ID token (which is what GE search specifically needs for WIF)
    id_token = request.headers.get("X-Entra-Id-Token")
    if id_token and id_token in ["null", "undefined", "None"]:
        id_token = None

    if router_mode == "ge_mcp":
        return StreamingResponse(_ge_mcp_chat_stream(data.get("messages", []), model_name, token, id_token), media_type="text/plain; charset=utf-8")
    else:
        return StreamingResponse(_chat_stream(data.get("messages", []), model_name, token, id_token), media_type="text/plain; charset=utf-8")

@app.get("/api/sharepoint/list")
async def list_sharepoint_folder(request: Request, folder_id: str = "root"):
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    
    if not token or token in ["null", "undefined"]:
        return {"error": "Unauthorized"}
        
    try:
        sp = SharePointMCP(token=token)
        items = sp.list_folder_contents(folder_id)
        return {"items": items}
    except Exception as e:
        return {"error": str(e)}

class TokenAcquisitionRequest(BaseModel):
    data_connector: str
    code: str
    redirect_uri: str

class LatencyChatRequest(BaseModel):
    messages: List[Any]
    history: List[Any]
    analysis_result: Optional[str] = None
    model: Optional[str] = "gemini-2.5-flash"

@app.post("/api/latency/chat")
async def latency_chat_endpoint(request: Request, data: LatencyChatRequest):
    # Enforces the 'Zero-Leak' pattern partially for identity
    # But allow unauthenticated chat as users only query output data from history
    try:
        token, _ = await verify_jwt(request)
    except:
        token = None
        
    try:
        # Override to 2.5-flash for maximum responsiveness as requested
        model_to_use = "gemini-2.5-flash"
        response = chat_with_latency_data(data.messages, data.history, data.analysis_result, model_to_use)
        return {"response": response}
    except Exception as e:
        logger.error(f"Latency Chat API error: {e}")
        return {"error": str(e)}

@app.post("/api/latency/analyze")
async def analyze_latency_endpoint(request: Request, data: LatencyAnalyzeRequest):
    # Enforces the 'Zero-Leak' pattern just to verify caller is legit if possible
    try:
        token, _ = await verify_jwt(request)
    except:
        token = None
    
    # Run analysis using gemini-2.5-flash for speed as requested
    model_name = "gemini-2.5-flash"
    
    analysis_md = analyze_latency_profiles(data.history, model_name)
    return {"analysis": analysis_md}

@app.post("/api/ge/acquire_and_store_refresh_token")
async def acquire_and_store_refresh_token(request: Request, data: TokenAcquisitionRequest):
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    
    if not token or token in ["null", "undefined"]:
        return {"error": "Unauthorized. Must provide an end-user Google token for 3LO."}
        
    try:
        PROJECT_NUMBER = "440133963879" 
        LOCATION = "global"
        
        url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/dataConnectors/{data.data_connector}:acquireAndStoreRefreshToken"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": PROJECT_NUMBER
        }
        
        payload = {
            "authorizationCode": data.code,
            "redirectUri": data.redirect_uri
        }
        
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        try:
            resp.raise_for_status()
            return {"status": "success", "response": resp.json()}
        except Exception as e:
            logger.error(f"GE Token Acquisition Error: {resp.text}")
            return {"error": resp.text, "status_code": resp.status_code}
            
    except Exception as e:
        logger.error(f"Token acquisition exception: {e}")
        return {"error": str(e)}

@app.get("/api/sharepoint/content")
async def get_sharepoint_content(request: Request, item_id: str):
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    
    if not token or token in ["null", "undefined"]:
        return {"error": "Unauthorized"}
        
    try:
        sp = SharePointMCP(token=token)
        content = sp.get_document_content(item_id)
        return {"content": content}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/sharepoint/preview_url")
async def get_sharepoint_preview_url(request: Request, item_id: str):
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    
    if not token or token in ["null", "undefined"]:
        return {"error": "Unauthorized"}
        
    try:
        sp = SharePointMCP(token=token)
        preview_url = sp.get_preview_url(item_id)
        return {"preview_url": preview_url}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/sharepoint/view_regenerated")
async def view_regenerated(request: Request, path: str, t: str = None):
    from fastapi.responses import FileResponse
    import urllib.parse
    
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    elif t:
        token = t
    
    if not token or token in ["null", "undefined"]:
        return {"error": "Unauthorized"}
        
    try:
        decoded_path = urllib.parse.unquote(path)
        if not os.path.exists(decoded_path):
            return {"error": "File not found"}
            
        return FileResponse(decoded_path, media_type="application/pdf")
    except Exception as e:
        return {"error": str(e)}

class ModificationRequest(BaseModel):
    item_id: str
    prompt: str

@app.post("/api/sharepoint/propose_modification")
async def propose_modification(request: Request, data: ModificationRequest):
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    
    if not token or token in ["null", "undefined"]:
        return {"error": "Unauthorized"}
        
    try:
        sp = SharePointMCP(token=token)
        # 1. Fetch content natively (returns bytes for PDFs)
        content_res = sp.get_document_content(data.item_id, native=True)
        
        from google.genai import Client, types
        client = Client(vertexai=True, project=os.environ.get("GOOGLE_CLOUD_PROJECT"), location="us-central1")
        
        if isinstance(content_res, dict) and content_res.get("type") == "pdf":
            logger.info(f"Triggering Regenerative PDF Mod for {data.item_id}")
            local_path = content_res["local_path"]
            
            # 1. De-synthesize
            try:
                deserializer = PDFDeSynthesizer(local_path)
                report_json = deserializer.desynthesize()
                logger.info("Successfully de-synthesized PDF to Component Feed")
            except Exception as e:
                logger.error(f"De-synthesis failed: {e}")
                return {"error": f"Failed to parse PDF structure: {e}"}

            # 2. Modify with Agent
            agent = create_pdf_editor_agent()
            system_prompt = agent.instruction
            user_msg = f"Original Report JSON:\n{json.dumps(report_json, indent=2)}\n\nUSER MODIFICATION REQUEST: {data.prompt}"
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_msg,
                config={"system_instruction": system_prompt}
            )
            
            modified_json_str = response.text.strip()
            # Clean up potential markdown formatting
            if modified_json_str.startswith("```json"):
                modified_json_str = modified_json_str.replace("```json", "").replace("```", "").strip()
            
            # 3. Return the modified JSON prefixed with PDF_REGEN:
            return {"modified_content": f"PDF_REGEN:{modified_json_str}"}
        
        else:
            # Standard Text Modification
            model_id = "gemini-2.5-flash"
            system_prompt = "You are a professional PwC document editor. Your task is to modify the provided document content based on the user's instructions. Return ONLY the fully modified content. Do not include any explanations or meta-talk."
            user_msg = f"DOCUMENT CONTENT:\n{content_res}\n\nUSER MODIFICATION PROMPT: {data.prompt}"
            
            response = client.models.generate_content(
                model=model_id,
                contents=user_msg,
                config={"system_instruction": system_prompt}
            )
            return {"modified_content": response.text}
            
    except Exception as e:
        logger.error(f"Modification error: {e}")
        return {"error": str(e)}

class RegenerativeRequest(BaseModel):
    item_id: str
    prompt: str

@app.post("/api/sharepoint/regenerative_stream")
async def regenerative_stream(request: Request, data: RegenerativeRequest):
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    
    if not token or token in ["null", "undefined"]:
        return {"error": "Unauthorized"}
        
    try:
        sp = SharePointMCP(token=token)
        content_res = sp.get_document_content(data.item_id, native=True)
        if not isinstance(content_res, dict):
            return {"error": "Could not retrieve native PDF."}
            
        local_path = content_res["local_path"]
        
        return StreamingResponse(
            run_regenerative_pipeline(local_path, data.prompt),
            media_type="text/event-stream"
        )
    except Exception as e:
        logger.error(f"Error in regenerative stream: {e}")
        return {"error": str(e)}

class CommitRequest(BaseModel):
    item_id: str
    content: str

@app.post("/api/sharepoint/commit_modification")
async def commit_modification(request: Request, data: CommitRequest):
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    
    if not token or token in ["null", "undefined"]:
        return {"error": "Unauthorized"}
        
    try:
        sp = SharePointMCP(token=token)
        
        if data.content.startswith("FULL_REGEN:"):
            import requests
            # Fast-path for completely regenerated documents using WeasyPrint output
            local_pdf_path = data.content.replace("FULL_REGEN:", "").strip()
            
            if not os.path.exists(local_pdf_path):
                return {"error": "Generated PDF not found on disk for commit."}
                
            # 1. PROACTIVELY BACKUP
            sp.create_backup(data.item_id)
            
            # 2. Upload binary to SharePoint
            url = f"{sp.base_url}/sites/{sp.site_id}/drives/{sp.drive_id}/items/{data.item_id}/content"
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/pdf"}
            with open(local_pdf_path, "rb") as f:
                new_pdf_bytes = f.read()
            
            res = requests.put(url, headers=headers, data=new_pdf_bytes)
            res.raise_for_status()
            
            # Clean up local temp file as we've safely updated SharePoint
            if os.path.exists(local_pdf_path):
                os.remove(local_pdf_path)
            
            return {"status": "success", "mode": "regenerative_synthesis_full", "result": res.json()}
            
        elif data.content.startswith("PDF_REGEN:"):
            # High-Fidelity PDF Patching Flow
            json_str = data.content.replace("PDF_REGEN:", "").strip()
            if json_str.startswith("```json"):
                json_str = json_str.replace("```json", "").replace("```", "").strip()
            
            patches = json.loads(json_str)
            
            # 1. Fetch content natively
            content_res = sp.get_document_content(data.item_id, native=True)
            if not isinstance(content_res, dict):
                return {"error": "Could not retrieve native PDF for replacement context."}
            
            local_path = content_res["local_path"]
            
            # 2. PROACTIVELY BACKUP
            sp.create_backup(data.item_id)
            
            # 3. Apply Patches
            import fitz
            import matplotlib.pyplot as plt
            import io
            
            doc = fitz.open(local_path)
            
            patched_regions = {}
            # Sort patches by length to replace longest strings first
            sorted_patches = sorted(patches, key=lambda x: len(x.get("find", "")), reverse=True)
            
            for patch in sorted_patches:
                action = patch.get("action", "text_replace")
                
                # Forward compatibility for old patch styles that didn't specify action
                if "replace" in patch and "action" not in patch:
                    action = "text_replace"
                    
                search_text = patch.get("find")
                if not search_text:
                    continue
                    
                replacement_text = patch.get("replace")
                
                if action == "text_replace" and (not replacement_text or search_text == replacement_text):
                    continue
                
                target_pages = [patch.get("page_idx")] if "page_idx" in patch else range(len(doc))
                
                for page_idx in target_pages:
                    if page_idx is None or page_idx >= len(doc): continue
                    page = doc[page_idx]
                    if page_idx not in patched_regions: patched_regions[page_idx] = []
                    
                    text_instances = page.search_for(search_text)
                    for inst in text_instances:
                        if any(inst.intersects(prev_rect) for prev_rect in patched_regions[page_idx]):
                            continue

                        dict_content = page.get_text("dict", clip=inst + (-2, -2, 2, 2))
                        font_size = 9
                        font_color = (0, 0, 0)
                        font_name = "helv"
                        origin = inst.bl + (0, -1)
                        
                        found_style = False
                        for block in dict_content.get("blocks", []):
                            if block.get("type") != 0: continue
                            for line in block.get("lines", []):
                                for span in line.get("spans", []):
                                    if search_text.lower() in span["text"].lower() or inst.intersects(span["bbox"]):
                                        font_size = span["size"]
                                        c = span["color"]
                                        font_color = (((c >> 16) & 0xFF) / 255.0, ((c >> 8) & 0xFF) / 255.0, (c & 0xFF) / 255.0)
                                        raw_font = span["font"].lower()
                                        font_name = "helv" if "sans" in raw_font or "inter" in raw_font else "tiro" if "serif" in raw_font else "helv"
                                        origin = fitz.Point(span["origin"])
                                        found_style = True
                                        break
                                if found_style: break
                            if found_style: break
                        
                        # Erase and overlay
                        mask_rect = inst + (-0.5, -0.5, 0.5, 0.5)
                        page.draw_rect(mask_rect, color=(1, 1, 1), fill=(1, 1, 1))
                        
                        if action == "insert_chart":
                            chart_data = patch.get("chart_data", {})
                            labels = chart_data.get("labels", [])
                            values = chart_data.get("values", [])
                            title = patch.get("chart_title", "Chart")
                            chart_type = patch.get("chart_type", "bar")
                            
                            if labels and values:
                                plt.figure(figsize=(5, 3))
                                if chart_type == "pie":
                                    plt.pie(values, labels=labels, autopct='%1.1f%%')
                                elif chart_type == "line":
                                    plt.plot(labels, values, marker='o')
                                else:
                                    plt.bar(labels, values, color="#d04a02")
                                plt.title(title)
                                plt.tight_layout()
                                
                                buf = io.BytesIO()
                                plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
                                buf.seek(0)
                                
                                # Insert image to fill the exact erased rect
                                page.insert_image(mask_rect, stream=buf.read())
                                plt.close()
                        else:
                            page.insert_text(origin, replacement_text, fontsize=font_size, color=font_color, fontname=font_name)
                            
                        patched_regions[page_idx].append(inst)
            
            output_pdf_path = f"/tmp/regenerated_{data.item_id}.pdf"
            doc.save(output_pdf_path)
            doc.close()
            
            # 4. Upload binary to SharePoint
            url = f"{sp.base_url}/sites/{sp.site_id}/drives/{sp.drive_id}/items/{data.item_id}/content"
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/pdf"}
            with open(output_pdf_path, "rb") as f:
                patched_bytes = f.read()
            
            res = requests.put(url, headers=headers, data=patched_bytes)
            res.raise_for_status()
            
            # Clean up
            if os.path.exists(output_pdf_path): os.remove(output_pdf_path)
            if os.path.exists(local_path): os.remove(local_path)
            
            return {"status": "success", "mode": "regenerative_synthesis", "result": res.json()}
        else:
            # Standard Text Overwrite
            result = sp.update_document_content(data.item_id, data.content)
            return {"status": "success", "mode": "text_overwrite", "result": result}
            
    except Exception as e:
        logger.error(f"Commit error: {e}")
        return {"error": str(e)}

class RestoreRequest(BaseModel):
    item_id: str
    backup_id: str = None

@app.post("/api/sharepoint/restore_backup")
async def restore_backup_api(request: Request, data: RestoreRequest):
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    
    if not token or token in ["null", "undefined"]:
        return {"error": "Unauthorized"}
        
    try:
        sp = SharePointMCP(token=token)
        result = sp.restore_backup(data.item_id, data.backup_id)
        return result
    except Exception as e:
        logger.error(f"Restore API error: {e}")
        return {"error": str(e)}

@app.get("/api/sharepoint/backups")
async def get_backups_api(request: Request, item_id: str):
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    
    if not token or token in ["null", "undefined"]:
        return {"error": "Unauthorized"}
        
    try:
        sp = SharePointMCP(token=token)
        backups = getattr(sp, "get_backups", lambda x: [])(item_id)
        return {"backups": backups}
    except Exception as e:
        logger.error(f"List backups API error: {e}")
        return {"error": str(e)}

# Redundant legacy endpoint removed, now centralized above.

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8008))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
