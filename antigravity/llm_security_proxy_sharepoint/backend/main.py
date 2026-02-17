import json
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from agent import get_agent
from protocol import AIStreamProtocol
from dotenv import load_dotenv
import os

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

    prompt = messages[-1]['content']
    # Ensure session exists
    session = await session_service.get_session(app_name="PWC_Security_Proxy", user_id="default_user", session_id="default_sess")
    if not session:
        await session_service.create_session(app_name="PWC_Security_Proxy", user_id="default_user", session_id="default_sess")

    runner = Runner(app_name="PWC_Security_Proxy", agent=get_agent(model_name), session_service=session_service)
    
    from google.genai import types
    msg = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
    
    # Run the agent (synchronously handles the tools and LLM)
    yield AIStreamProtocol.data({"type": "status", "message": "Establishing secure context...", "icon": "shield-alert", "pulse": True})
    
    log_latency("Context Initialization")
    current_action = "LLM Orchestration & Reasoning"

    try:
        async for event in runner.run_async(user_id="default_user", session_id="default_sess", new_message=msg):
            try:
                edata = event.model_dump()
                
                # Extract usage metadata
                usage = edata.get("usage_metadata")
                if usage:
                    # Sum up usage across all turns in this reasoning chain
                    total_tokens["prompt"] += usage.get("prompt_token_count") or 0
                    total_tokens["candidates"] += usage.get("candidates_token_count") or 0
                    total_tokens["total"] += usage.get("total_token_count") or 0

                content = edata.get("content", {})
                if content and isinstance(content, dict):
                    parts = content.get("parts", [])
                    for p in parts:
                        # Capture thoughts if present
                        if p.get("thought"):
                            txt = f"THOUGHT:\n{p['thought'].strip()}"
                            if txt not in reasoning_steps:
                                reasoning_steps.append(txt)

                        # Capture reasoning steps explicitly from text
                        if p.get("text"):
                            txt = p['text'].strip()
                            if txt and txt not in reasoning_steps:
                                reasoning_steps.append(txt)
                                
                        if p.get("function_call"):
                            tool_name = p["function_call"].get("name", "")
                            args_str = str(p["function_call"].get("args", {}))
                            reasoning_steps.append(f"TOOL CALL: {tool_name}\nARGS: {args_str}")
                            
                            log_latency(current_action)
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
                            # truncate response because it can be massive
                            if len(res_str) > 500:
                                res_str = res_str[:500] + "... [TRUNCATED]"
                            reasoning_steps.append(f"TOOL RESPONSE: {tool_name}\nRESULT: {res_str}")
                            
                            log_latency(current_action)
                            yield AIStreamProtocol.data({"type": "status", "message": "Synthesizing zero-leak intelligence...", "icon": "cpu", "pulse": True})
                            current_action = "LLM Final Synthesis"
            except Exception as e:
                print("===== ERROR IN EVENT ===== ", e)
                pass
    except Exception as e:
        print("===== RUNNER CRASHED ===== ", e)
        yield AIStreamProtocol.data({"type": "status", "message": f"Security Proxy Error: {str(e)}", "icon": "alert-triangle", "pulse": False})
        reasoning_steps.append(f"AGENT EXECUTION HALTED: {str(e)}")
        log_latency("Agent Exception")

    log_latency(current_action)
    total_time = time.time() - start_time
    latency_metrics.append({"step": "Total Turnaround Time", "duration_s": round(total_time, 2)})

    yield AIStreamProtocol.data({
        "type": "telemetry",
        "data": latency_metrics,
        "reasoning": reasoning_steps,
        "tokens": total_tokens
    })

    yield AIStreamProtocol.data({"type": "status", "message": "Transmission complete.", "icon": "check-circle", "pulse": False})
        
    session = await session_service.get_session(app_name="PWC_Security_Proxy", user_id="default_user", session_id="default_sess")
    
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
