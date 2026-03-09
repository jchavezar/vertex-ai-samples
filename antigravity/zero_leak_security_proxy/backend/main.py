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
from agent import get_agent
from protocol import AIStreamProtocol
from pdf_editor_agent import PDFDeSynthesizer, create_pdf_editor_agent
from pwc_renderer import render_report
from regenerative_pipeline import run_regenerative_pipeline
from mcp_sharepoint import SharePointMCP

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
    
    pub_runner = Runner(app_name="Public_Research_Proxy", agent=get_public_agent("gemini-3.1-flash-lite-preview"), session_service=session_service)

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

    current_action = {"sharepoint": "LLM Orchestration & Reasoning", "public": "Web Research Orchestration"}
    
    while active_streams > 0:
        msg_obj = await queue.get()
        tag = msg_obj["tag"]
        msg_type = msg_obj["type"]

        if msg_type == "done":
            active_streams -= 1
            log_latency(tag, current_action[tag])
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
                            yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": total_tokens})

                    if p.get("function_call"):
                        tool_name = p["function_call"].get("name", "")
                        args_str = str(p["function_call"].get("args", {}))
                        
                        log_latency(tag, current_action[tag])
                        
                        if tool_name == "google_search":
                            reasoning_steps.append(f"{agent_label} THOUGHT:\nI need to search the public internet for relevant general market information.")
                            yield AIStreamProtocol.data({"type": "status", "message": "Searching public web...", "icon": "globe", "pulse": True})
                            current_action[tag] = "Google Search API"
                        elif "search" in tool_name:
                            reasoning_steps.append(f"{agent_label} THOUGHT:\nI need to search the enterprise database for relevant information. I will use a **Parallel Fan-out Search** with 3 distinct query angles to maximize recall.")
                            yield AIStreamProtocol.data({"type": "status", "message": "Executing Parallel Fan-out Search...", "icon": "search", "pulse": True})
                            current_action[tag] = "Graph Parallel Fan-out Search"
                        elif "read" in tool_name:
                            reasoning_steps.append(f"{agent_label} ANALYSIS:\nI identified relevant documents. I will now trigger the **MarkItDown Global Conversion** engine to transform complex binaries into clean Markdown for high-scale synthesis.")
                            yield AIStreamProtocol.data({"type": "status", "message": "Neural Markdown Conversion...", "icon": "file-text", "pulse": True})
                            current_action[tag] = "Neural Markdown Conversion"
                        else:
                            current_action[tag] = f"Tool: {tool_name}"
                            
                        reasoning_steps.append(f"{agent_label} TOOL:\n{tool_name}")
                        reasoning_steps.append(f"{agent_label} ARGS:\n{args_str}")

                        current_total = round(time.time() - start_time, 2)
                        temp_metrics = latency_metrics + [{"step": "Total Turnaround Time", "duration_s": current_total}]
                        yield AIStreamProtocol.data({"type": "telemetry", "data": temp_metrics, "reasoning": reasoning_steps, "tokens": total_tokens})
                            
                    elif p.get("function_response"):
                        tool_name = p["function_response"].get("name", "")
                        resp_data = p["function_response"].get("response", "")
                        res_str = str(resp_data)
                        
                        if len(res_str) > 500:
                            res_str = res_str[:500] + "... [TRUNCATED]"
                        
                        # Phase: Detect Vision triggers and update UI status
                        if "read" in tool_name and "[NEURAL VISION BLOCK:" in str(resp_data):
                            yield AIStreamProtocol.data({"type": "status", "message": "Neural Vision describing visual assets...", "icon": "eye", "pulse": True})
                            
                        reasoning_steps.append(f"{agent_label} RESPONSE:\n{tool_name}")
                        reasoning_steps.append(f"{agent_label} RESULT:\n{res_str}")
                        
                        log_latency(tag, current_action[tag])
                        
                        if tag != "public":
                            yield AIStreamProtocol.data({"type": "status", "message": "Synthesizing zero-leak intelligence...", "icon": "cpu", "pulse": True})
                        current_action[tag] = "LLM Final Synthesis"
                        
                        current_total = round(time.time() - start_time, 2)
                        temp_metrics = latency_metrics + [{"step": "Total Turnaround Time", "duration_s": current_total}]
                        yield AIStreamProtocol.data({"type": "telemetry", "data": temp_metrics, "reasoning": reasoning_steps, "tokens": total_tokens})

                    if p.get("text"):
                        txt = p['text'].strip()
                        if txt:
                            if tag == "sharepoint":
                                step_text = f"{agent_label} SYNTHESIS:\n{txt}"
                                if step_text not in reasoning_steps:
                                    reasoning_steps.append(step_text)
                                    yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": total_tokens})
                                    
                            if tag == "public":
                                pub_insight += p['text']
                                yield AIStreamProtocol.data({
                                    "type": "public_insight", 
                                    "message": "Public Web Consensus",
                                    "data": pub_insight.strip(),
                                    "icon": "globe",
                                    "pulse": True
                                })
        except Exception as e:
            print("===== ERROR IN EVENT PARSING ===== ", e)
            pass

    total_time = time.time() - start_time
    latency_metrics.append({"step": "Total Turnaround Time", "duration_s": round(total_time, 2)})

    # Final public_insight payload explicitly to stop pulse
    if pub_insight:
        reasoning_steps.append(f"[Public Web] SYNTHESIS:\n{pub_insight.strip()}")
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
    model_name = data.get("model", "gemini-3-pro-preview")
    
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        extracted = auth_header.split(" ")[1]
        if extracted and extracted not in ["null", "undefined"]:
            token = extracted

    set_user_token(token)
    return StreamingResponse(_chat_stream(data.get("messages", []), model_name), media_type="text/plain; charset=utf-8")

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
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
