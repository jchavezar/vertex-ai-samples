import os
import sys

# Ensure backend directory is in sys.path so 'agent' can be imported easily even if run from root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
import logging
import requests
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Now we can safely import agent, protocol, etc.
from agents.agent import get_agent_with_mcp_tools
from utils.protocol import AIStreamProtocol
from agents.pdf_editor_agent import PDFDeSynthesizer, create_pdf_editor_agent
from utils.pwc_renderer import render_report
from pipelines.regenerative_pipeline import run_regenerative_pipeline
from mcp_service.mcp_sharepoint import SharePointMCP
from utils.auth_context import set_user_token

from dotenv import load_dotenv
load_dotenv(dotenv_path="../.env")

os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"

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
async def _chat_stream(messages: list, model_name: str, token: str = None):
    # Set the token in the current context (essential for async streaming tasks)
    set_user_token(token)
    
    import time
    start_time = time.time()
    last_phase_time = {"sharepoint": start_time, "public": start_time}
    latency_metrics = []
    reasoning_steps = []
    total_tokens = {"prompt": 0, "candidates": 0, "total": 0}
    
    def log_latency(tag, step_name):
        now = time.time()
        duration_sec = now - last_phase_time[tag]
        if duration_sec > 0.01:
            prefix = "[Enterprise] " if tag == "sharepoint" else "[Public Web] "
            latency_metrics.append({"step": prefix + step_name, "duration_s": round(duration_sec, 2)})
        last_phase_time[tag] = now

    import uuid
    current_request_id = str(uuid.uuid4())
    sess_id = f"sess_{current_request_id}"
    pub_sess_id = f"pub_{current_request_id}"

    prompt = messages[-1]['content']
    # Ensure session exists
    session = await session_service.get_session(app_name="PWC_Security_Proxy", user_id="default_user", session_id=sess_id)
    if not session:
        await session_service.create_session(app_name="PWC_Security_Proxy", user_id="default_user", session_id=sess_id)

    import asyncio
    from agents.public_agent import get_public_agent
    from google.genai import types

    queue = asyncio.Queue()
    msg = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])

    # 1. Initialize Public Agent immediately (Prior to Discovery)
    pub_session = await session_service.get_session(app_name="Public_Research_Proxy", user_id="default_user", session_id=pub_sess_id)
    if not pub_session:
        await session_service.create_session(app_name="Public_Research_Proxy", user_id="default_user", session_id=pub_sess_id)
    
    # Use gemini-2.5-flash for ultra-fast response for Public Web Consensus and to avoid 429s
    pub_agent = get_public_agent("gemini-2.5-flash")
    pub_runner = Runner(
        app_name="Public_Research_Proxy", 
        agent=pub_agent, 
        session_service=session_service
    )

    async def stream_agent(runner_obj, sid, tag):
        try:
            async for event in runner_obj.run_async(user_id="default_user", session_id=sid, new_message=msg):
                await queue.put({"tag": tag, "event": event, "type": "data"})
        except Exception as e:
            logger.error(f"Task {tag} failed: {e}")
            await queue.put({"tag": tag, "event": e, "type": "error"})
        finally:
            await queue.put({"tag": tag, "type": "done"})

    # Launch Public Agent background task NOW - it starts working immediately
    asyncio.create_task(stream_agent(pub_runner, pub_sess_id, "public"))

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
    
    discovery_task = asyncio.create_task(get_agent_with_mcp_tools(token=token, model_name=model_name))
    
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
                logger.info(f">>> [LATENCY] MCP Discovery Time: {discovery_time:.2f}s")
                try:
                    agent, exit_stack = await discovery_task
                    sp_runner = Runner(app_name="PWC_Security_Proxy", agent=agent, session_service=session_service)
                    asyncio.create_task(stream_agent(sp_runner, sess_id, "sharepoint"))
                    sharepoint_started = True
                    active_streams += 1
                except Exception as e:
                    logger.error(f"Enterprise Discovery failed: {e}")
                    sharepoint_started = True # mark as attempted
                    yield AIStreamProtocol.data({"type": "status", "message": f"Discovery Error: {str(e)}", "icon": "alert-triangle", "pulse": False})

            # Wait for any event from either stream
            try:
                # Poll with short timeout to allow checking discovery_task status
                msg_obj = await asyncio.wait_for(queue.get(), timeout=0.1)
            except asyncio.TimeoutError:
                continue

            tag = msg_obj["tag"]
            msg_type = msg_obj["type"]

            if msg_type == "done":
                active_streams -= 1
                log_latency(tag, current_action[tag])
                if tag == "public":
                    # Send final settled state for public insight immediately so UI can decouple
                    yield AIStreamProtocol.data({
                        "type": "public_insight", 
                        "message": "Public Web Consensus",
                        "data": pub_insight.strip(),
                        "icon": "globe",
                        "pulse": False
                    })
                continue
                
            evt = msg_obj["event"]
            if msg_type == "error":
                if tag == "sharepoint":
                    yield AIStreamProtocol.data({"type": "status", "message": f"Enterprise Proxy Error: {str(evt)}", "icon": "alert-triangle", "pulse": False})
                    reasoning_steps.append(f"AGENT EXECUTION HALTED [{tag}]: {str(evt)}")
                continue

            # Process Event
            try:
                edata = evt.model_dump()
                
                # DEBUG DUMP FOR PUBLIC EVENT
                if tag == "public":
                    logger.info(f"[PUBLIC EVENT DUMP] {edata}")
                    
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
                                yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": total_tokens})
                                
                        # Extract Google Search Grounding Metadata dynamically since built-in tool doesn't emit a standard function call
                        if tag == "public":
                            grounding = edata.get("grounding_metadata", {})
                            if grounding:
                                qs = grounding.get("web_search_queries", [])
                                if qs:
                                    search_str = ", ".join(qs)
                                    tool_str = f"{agent_label} TOOL:\ngoogle_search"
                                    if tool_str not in reasoning_steps:
                                        reasoning_steps.append(tool_str)
                                        reasoning_steps.append(f"{agent_label} ARGS:\n{{queries: [{search_str}]}}")
                                        yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": total_tokens})

                        if p.get("function_call"):
                            tool_name = p["function_call"].get("name", "")
                            tool_args = p["function_call"].get("args", {})
                            log_latency(tag, current_action[tag])
                            
                            if tool_name == "google_search":
                                yield AIStreamProtocol.data({"type": "status", "message": "Searching public web...", "icon": "globe", "pulse": True})
                                current_action[tag] = "Google Search API"
                            elif "search" in tool_name:
                                reasoning_steps.append(f"{agent_label} THOUGHT:\nI need to search the enterprise database. Using **Parallel Fan-out Search**.")
                                yield AIStreamProtocol.data({"type": "status", "message": "Executing Parallel Fan-out Search...", "icon": "search", "pulse": True})
                                current_action[tag] = "Graph Parallel Fan-out Search"
                            elif tool_name == "emit_project_card":
                                # INTERCEPT: Send card to frontend immediately
                                yield AIStreamProtocol.data({"type": "project_card", "data": tool_args})
                            elif "read" in tool_name:
                                reasoning_steps.append(f"{agent_label} ANALYSIS:\nThe search results found relevant files. I must now extract their text to synthesize the final answer.")
                                current_action[tag] = "Document Extraction"
                            else:
                                current_action[tag] = f"Tool: {tool_name}"
                            
                            reasoning_steps.append(f"{agent_label} TOOL:\n{tool_name}")
                            reasoning_steps.append(f"{agent_label} ARGS:\n{str(tool_args)}")
                            yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": total_tokens})
                                
                        elif p.get("function_response"):
                            tool_name = p["function_response"].get("name", "")
                            resp_data = p["function_response"].get("response", "")
                            res_str = str(resp_data)[:500] + "... [TRUNCATED]" if len(str(resp_data)) > 500 else str(resp_data)
                            
                            reasoning_steps.append(f"{agent_label} RESPONSE:\n{tool_name}")
                            reasoning_steps.append(f"{agent_label} RESULT:\n{res_str}")
                            log_latency(tag, current_action[tag])
                            
                            if tag == "sharepoint":
                                yield AIStreamProtocol.data({"type": "status", "message": "Synthesizing zero-leak intelligence...", "icon": "cpu", "pulse": True})
                            current_action[tag] = "LLM Final Synthesis"
                            yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": total_tokens})

                        if p.get("text"):
                            txt = p['text'].strip()
                            if txt:
                                if tag == "sharepoint":
                                    step_text = f"{agent_label} SYNTHESIS:\n{txt}"
                                    if step_text not in reasoning_steps:
                                        reasoning_steps.append(step_text)
                                        yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": total_tokens})
                                
                                if tag == "public":
                                    pub_insight += txt
                                    # Streaming cursor character █ for fast feedback
                                    yield AIStreamProtocol.data({
                                        "type": "public_insight", 
                                        "message": "Public Web Consensus",
                                        "data": pub_insight.strip() + " █",
                                        "icon": "globe",
                                        "pulse": True
                                    })
                                else:
                                    # Main synthesis stream
                                    yield AIStreamProtocol.text(txt)
            except Exception as e:
                logger.error(f"Event parsing error in {tag}: {e}")

        # Cards are now emitted in real-time via the 'emit_project_card' tool interception in the event loop.

    finally:
        if exit_stack:
            await exit_stack.aclose()

    total_time = time.time() - start_time
    latency_metrics.append({"step": "[Total] Turnaround Time", "duration_s": round(total_time, 2)})
    yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": total_tokens})
    yield AIStreamProtocol.data({"type": "status", "message": "Transmission complete.", "icon": "check-circle", "pulse": False})

from utils.auth_context import set_user_token

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "zero_leak_security_proxy"}

@app.get("/")
async def root():
    return {"message": "Zero-Leak Security Proxy Backend is running.", "docs": "/docs"}

async def auth_error_stream(message: str):
    yield AIStreamProtocol.text(message)

@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    model_name = data.get("model", "gemini-2.5-flash")
    
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        extracted = auth_header.split(" ")[1]
        if extracted and extracted not in ["null", "undefined"]:
            token = extracted

    return StreamingResponse(_chat_stream(data.get("messages", []), model_name, token), media_type="text/plain; charset=utf-8")

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

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8002))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
