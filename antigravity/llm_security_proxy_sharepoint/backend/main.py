import os
import sys

# Ensure backend directory is in sys.path so 'agent' can be imported easily even if run from root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService

# Now we can safely import agent, protocol, etc.
from agent import get_agent
from protocol import AIStreamProtocol
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_LOCATION"] = "global"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

session_service = InMemorySessionService()

class ChatRequest(BaseModel):
    messages: list

async def _chat_stream(messages: list, model_name: str):
    import time
    start_time = time.time()
    last_phase_time = start_time
    latency_metrics = []
    reasoning_steps = []
    total_tokens = {"prompt": 0, "candidates": 0, "total": 0}
    
    def log_latency(step_name):
        nonlocal last_phase_time
        now = time.time()
        duration_sec = now - last_phase_time
        if duration_sec > 0.01:
            latency_metrics.append({"step": step_name, "duration_s": round(duration_sec, 2)})
        last_phase_time = now

    import uuid
    current_request_id = str(uuid.uuid4())
    sess_id = f"sess_{current_request_id}"
    pub_sess_id = f"pub_{current_request_id}"

    prompt = messages[-1]['content']
    # Ensure session exists
    session = await session_service.get_session(app_name="PWC_Security_Proxy", user_id="default_user", session_id=sess_id)
    if not session:
        await session_service.create_session(app_name="PWC_Security_Proxy", user_id="default_user", session_id=sess_id)

    runner = Runner(app_name="PWC_Security_Proxy", agent=get_agent(model_name), session_service=session_service)
    
    from google.genai import types
    msg = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
    
    # Run the agent (synchronously handles the tools and LLM)
    yield AIStreamProtocol.data({
        "type": "public_insight", 
        "message": "Public Web Consensus",
        "data": "",
        "icon": "globe",
        "pulse": True
    })
    yield AIStreamProtocol.data({"type": "status", "message": "Establishing secure context...", "icon": "shield-alert", "pulse": True})
    
    import asyncio
    from public_agent import get_public_agent

    queue = asyncio.Queue()

    # Create private session copies to avoid clashes
    pub_session = await session_service.get_session(app_name="Public_Research_Proxy", user_id="default_user", session_id=pub_sess_id)
    if not pub_session:
        await session_service.create_session(app_name="Public_Research_Proxy", user_id="default_user", session_id=pub_sess_id)
    
    pub_runner = Runner(app_name="Public_Research_Proxy", agent=get_public_agent("gemini-2.5-flash"), session_service=session_service)

    async def stream_agent(runner_obj, sid, tag):
        try:
            async for event in runner_obj.run_async(user_id="default_user", session_id=sid, new_message=msg):
                await queue.put({"tag": tag, "event": event, "type": "data"})
        except Exception as e:
            await queue.put({"tag": tag, "event": e, "type": "error"})
        finally:
            await queue.put({"tag": tag, "type": "done"})

    asyncio.create_task(stream_agent(runner, sess_id, "sharepoint"))
    asyncio.create_task(stream_agent(pub_runner, pub_sess_id, "public"))

    active_streams = 2
    pub_insight = ""

    current_action = "LLM Orchestration & Reasoning"
    
    while active_streams > 0:
        msg_obj = await queue.get()
        tag = msg_obj["tag"]
        msg_type = msg_obj["type"]

        if msg_type == "done":
            active_streams -= 1
            if tag == "sharepoint":
                log_latency("SharePoint Turnaround")
            continue
            
        evt = msg_obj["event"]
        
        if msg_type == "error":
            print(f"===== RUNNER CRASHED [{tag}] ===== ", evt)
            if tag == "sharepoint":
                yield AIStreamProtocol.data({"type": "status", "message": f"Security Proxy Error: {str(evt)}", "icon": "alert-triangle", "pulse": False})
                reasoning_steps.append(f"AGENT EXECUTION HALTED [{tag}]: {str(evt)}")
            continue

        try:
            edata = evt.model_dump()
            
            # Combine token stats
            usage = edata.get("usage_metadata")
            if usage:
                total_tokens["prompt"] += usage.get("prompt_token_count") or 0
                total_tokens["candidates"] += usage.get("candidates_token_count") or 0
                total_tokens["total"] += usage.get("total_token_count") or 0

            content = edata.get("content", {})
            if content and isinstance(content, dict):
                parts = content.get("parts", [])
                for p in parts:
                    agent_label = "[Public Web]" if tag == "public" else "[Enterprise Proxy]"
                    
                    if p.get("thought"):
                        txt = f"{agent_label} THOUGHT:\n{p['thought'].strip()}"
                        if txt not in reasoning_steps:
                            reasoning_steps.append(txt)

                    if p.get("function_call"):
                        tool_name = p["function_call"].get("name", "")
                        args_str = str(p["function_call"].get("args", {}))
                        reasoning_steps.append(f"{agent_label} TOOL: {tool_name}\nARGS: {args_str}")
                        
                        if tag != "public":
                            log_latency(current_action)
                            current_total = round(time.time() - start_time, 2)
                            temp_metrics = latency_metrics + [{"step": "Total Turnaround Time", "duration_s": current_total}]
                            yield AIStreamProtocol.data({"type": "telemetry", "data": temp_metrics, "reasoning": reasoning_steps, "tokens": total_tokens})
                            
                            if "search" in tool_name:
                                yield AIStreamProtocol.data({"type": "status", "message": "Searching enterprise indices...", "icon": "search", "pulse": True})
                                current_action = "Graph API Search"
                            elif "read" in tool_name:
                                yield AIStreamProtocol.data({"type": "status", "message": "Extracting text via MarkItDown OCR...", "icon": "database", "pulse": True})
                                current_action = "Document MarkItDown OCR"
                            else:
                                current_action = f"Tool: {tool_name}"
                                
                    elif p.get("function_response"):
                        tool_name = p["function_response"].get("name", "")
                        res_str = str(p["function_response"].get("response", {}))
                        if len(res_str) > 500:
                            res_str = res_str[:500] + "... [TRUNCATED]"
                        reasoning_steps.append(f"{agent_label} RESPONSE: {tool_name}\nRESULT: {res_str}")
                        
                        if tag != "public":
                            log_latency(current_action)
                            yield AIStreamProtocol.data({"type": "status", "message": "Synthesizing zero-leak intelligence...", "icon": "cpu", "pulse": True})
                            current_action = "LLM Final Synthesis"
                            
                            current_total = round(time.time() - start_time, 2)
                            temp_metrics = latency_metrics + [{"step": "Total Turnaround Time", "duration_s": current_total}]
                            yield AIStreamProtocol.data({"type": "telemetry", "data": temp_metrics, "reasoning": reasoning_steps, "tokens": total_tokens})

                    if p.get("text"):
                        txt = p['text'].strip()
                        if tag == "public":
                            pub_insight += txt + "\n"
                            yield AIStreamProtocol.data({
                                "type": "public_insight", 
                                "message": "Public Web Consensus",
                                "data": pub_insight.strip(),
                                "icon": "globe",
                                "pulse": True
                            })
                            yield AIStreamProtocol.data({"type": "status", "message": "Researching public web...", "icon": "globe", "pulse": True})
                        else:
                            if txt and txt not in reasoning_steps:
                                reasoning_steps.append(f"{agent_label} SYNTHESIS:\n{txt}")
        except Exception as e:
            print("===== ERROR IN EVENT PARSING ===== ", e)
            pass

    log_latency(current_action)
    total_time = time.time() - start_time
    latency_metrics.append({"step": "Total Turnaround Time", "duration_s": round(total_time, 2)})

    # Final public_insight payload explicitly to stop pulse
    if pub_insight:
        yield AIStreamProtocol.data({
            "type": "public_insight", 
            "message": "Public Web Consensus",
            "data": pub_insight.strip(),
            "icon": "globe",
            "pulse": False
        })

    yield AIStreamProtocol.data({
        "type": "telemetry",
        "data": latency_metrics,
        "reasoning": reasoning_steps,
        "tokens": total_tokens
    })

    yield AIStreamProtocol.data({"type": "status", "message": "Transmission complete.", "icon": "check-circle", "pulse": False})
        
    session = await session_service.get_session(app_name="PWC_Security_Proxy", user_id="default_user", session_id=sess_id)
    
    # Get the resulting parts from schema
    result = session.state.get("proxy_output") if session else None
    if not result:
        yield AIStreamProtocol.text("Error: Failed to generate response or no output returned.")
        return

    # Yield parts according to Vercel AI SDK Zero-Parsing stream protocol
    if isinstance(result, dict):
        text_content = result.get('markdown_text', '')
        cards = result.get('project_cards', [])
        
        if text_content:
            yield AIStreamProtocol.text(text_content)
            
        for card in cards:
            widget_payload = {
                "type": "project_card",
                "data": card
            }
            yield AIStreamProtocol.data(widget_payload)
    else:
        text_content = getattr(result, 'markdown_text', '')
        cards = getattr(result, 'project_cards', [])
        
        if text_content:
            yield AIStreamProtocol.text(text_content)
            
        for card in cards:
            widget_payload = {
                "type": "project_card",
                "data": card.model_dump() if hasattr(card, 'model_dump') else card
            }
            yield AIStreamProtocol.data(widget_payload)

from auth_context import set_user_token

async def auth_error_stream(message: str):
    yield AIStreamProtocol.text(message)

@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    model_name = data.get("model", "gemini-3-pro-preview")
    
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        msg = "🔒 **Access Denied: Zero-Leak Protocol active.**\n\nPlease sign in using the button in the top right to securely query the enterprise index."
        return StreamingResponse(auth_error_stream(msg), media_type="text/plain; charset=utf-8")
        
    token = auth_header.split(" ")[1]
    if not token or token in ["null", "undefined"]:
        msg = "🔒 **Access Denied: Invalid token.**\n\nPlease sign in using the button in the top right to securely query the enterprise index."
        return StreamingResponse(auth_error_stream(msg), media_type="text/plain; charset=utf-8")
        
    set_user_token(token)
    return StreamingResponse(_chat_stream(data.get("messages", []), model_name), media_type="text/plain; charset=utf-8")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
