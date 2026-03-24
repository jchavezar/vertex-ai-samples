import os
import json
import logging
import asyncio
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Try to load env vars from current, parent, or grandparent dir
for path in [".env", "../.env", "../../.env"]:
    load_dotenv(dotenv_path=path)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Project detection
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("PROJECT_ID")
if not PROJECT_ID:
    try:
        import google.auth
        _, auto_project = google.auth.default()
        PROJECT_ID = auto_project
        logger.info(f"Auto-detected Project ID from ADC: {PROJECT_ID}")
    except Exception:
        PROJECT_ID = "254356041555" # Last resort fallback
        logger.warning(f"Project ID not detected, using fallback: {PROJECT_ID}")

# Initialize Gemini Client
client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
MODEL_ID = "gemini-3.1-flash-lite-preview"

# Discovery client import after env loading
try:
    from vais import vais_client
except ImportError:
    logger.warning("vais_client not found. Discovery search will be unavailable.")
    vais_client = None

# Initialize FastAPI (Root App)
app = FastAPI(title="Accenture Tax Catalyst Root")

# Setup CORS on root app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define instructions
GEMINI_INSTRUCTION = """
You are the Accenture Chief Tax Catalyst, an elite AI advisor specialized in Global Tax Intelligence developed for Accenture.
Your audience consists of corporate executives (CFOs, Heads of Tax, Directors).
Provide highly professional, accurate, and strategic tax advice.
When asked about current events, upcoming tax rules (e.g., tax updates for 2026), rely on your Google Search capability to find the latest real-world developments and cite them.
Focus on corporate tax, transfer pricing, indirect taxes, and OECD Pillar Two. 
If the user asks why "tax", explain that Accenture is a leader in business and tax strategy services and this tool is built to navigate complex global tax landscapes.
Be concise, proactive, and structure your insights with clear formatting (markdown, bolding, bullet points when appropriate).
Always maintain a formal, 'enterprise-grade' Accenture tone. Do not use generic AI greetings.
"""

RADAR_INSTRUCTION = """
You are the Strategic Tax Radar AI.
Generate a very concise, easy-to-understand insight about a recent global tax policy change.
CRITICAL: Highlight exactly the most critical key terms using bold markdown (e.g., **word**). Do not prefix your response with anything.
Use Google Search to find the latest news.
Format your response as a direct, streaming insight. No bullet points, just a continuous short paragraph. KEEP IT UNDER 2 SENTENCES.
"""

NAV_INSTRUCTION = """
You are the Accenture Navigation Architect AI.
A user has provided a short description of their operating model or industry.
Your job is to generate a custom website navigation menu structure tailored specifically to their situation.
The output MUST be a valid JSON array of objects. 
Each object must have:
- "title": A short, punchy category title (e.g., "LatAm Digital Taxes")
- "description": A short 1-sentence description.
- "icon": Choose ONE of these strings representing a lucide-react icon: ["Globe", "Briefcase", "TrendingUp", "Shield", "Activity", "FileText", "Building", "Cpu", "Landmark"]

Generate exactly 4 distinct categories. 
DO NOT include any markdown formatting, backticks, or other text outside the JSON array. Just the raw JSON array.
"""

LIVE_PULSE_INSTRUCTION = """
You are the Accenture Global Insights Coordinator.
The user is requesting a live update on tax policies for a specific region or topic.
You MUST use your Google Search tool to find the absolute latest, current news on this topic.
Format your response beautifully with markdown:
- Start with a bold headline reflecting current news.
- Provide a exactly 1-2 sentence executive summary of the real-world news.
- Add a bullet point "Risk Impact: [High/Medium/Low] - [1 sentence reason]".
DO NOT make up information. Use grounded search results.
"""

DASHBOARD_INSTRUCTION = """
You are the Accenture Global Insights Coordinator building a generative dashboard.
Given an industry, generate a comprehensive strategic tax risk assessment.
You MUST output a JSON object matching the requested schema exactly.
"""

# Models
class ChatMessage(BaseModel):
    role: str 
    content: str
    
class ChatRequest(BaseModel):
    messages: List[ChatMessage]

class NavRequest(BaseModel):
    description: str

class PulseRequest(BaseModel):
    query: str

class SearchRequest(BaseModel):
    query: str

class DashboardRequest(BaseModel):
    industry: str

# Create a sub-app for the actual logic
# This sub-app will be mounted at /acc
acc_app = FastAPI(title="Accenture Tax Catalyst Content")

@acc_app.get("/health")
async def health_check():
    return {"status": "ok", "project_id": PROJECT_ID, "vais_enabled": vais_client is not None}

@acc_app.post("/api/search")
async def discovery_engine_search(request: SearchRequest):
    try:
        logger.info(f"Querying Discovery Engine for: {request.query}")
        if not vais_client:
            return {"error": "Discovery Engine client not initialized", "results": []}
        results = await vais_client.search(request.query)
        return results
    except Exception as e:
        logger.exception(f"Search error: {e}")
        return {"error": str(e), "results": []}

class OverviewRequest(BaseModel):
    query: str
    search_results: Optional[List[Dict[str, Any]]] = None

@acc_app.post("/api/search/generative-overview")
async def generative_search_overview(request: OverviewRequest):
    async def sse_generator():
        try:
            contexts = []
            if request.search_results and isinstance(request.search_results, list):
                for i, res in enumerate(request.search_results[:5]):
                    doc = res.get("document", {})
                    struct_data = doc.get("derivedStructData", {})
                    title = struct_data.get("title", "")
                    link = struct_data.get("link", "")
                    snippets = struct_data.get("snippets", [])
                    snippet = snippets[0].get("snippet", "") if snippets else ""
                    contexts.append(f"Result {i+1}:\\nTitle: {title}\\nURL: {link}\\nSnippet: {snippet}")
            
            context_text = "\\n\\n".join(contexts)
            prompt = f"User Query: {request.query}\n\nSearch Results:\n{context_text}\n\nTask: Summarize the findings VERY CONCISELY (max 2-3 sentences). Be direct. If you see a highly relevant PDF, append: [PDF_SUGGESTION]{{\"title\": \"...\", \"url\": \"...\"}}[/PDF_SUGGESTION]"
            
            config = types.GenerateContentConfig(
                system_instruction="You are an Accenture Strategic AI providing an ultra-concise executive summary. Use markdown.",
                temperature=0.3,
                tools=[{"google_search": {}}],
            )
            
            response_stream = await client.aio.models.generate_content_stream(
                model=MODEL_ID,
                contents=prompt,
                config=config
            )
            
            async for chunk in response_stream:
                if chunk.text:
                    yield {"event": "message", "data": json.dumps({"text": chunk.text})}
                    await asyncio.sleep(0.01)
            yield {"event": "done", "data": "[DONE]"}
        except Exception as e:
            logger.exception(f"Error in generative overview: {e}")
            yield {"event": "error", "data": json.dumps({"error": str(e)})}
            
    return EventSourceResponse(sse_generator())

@acc_app.get("/api/radar/insight")
async def generate_radar_insight(request: Request):
    async def sse_generator():
        try:
            config = types.GenerateContentConfig(system_instruction=RADAR_INSTRUCTION, tools=[{"google_search": {}}])
            response_stream = await client.aio.models.generate_content_stream(model=MODEL_ID, contents="What is the most critical corporate tax news right now?", config=config)
            async for chunk in response_stream:
                if chunk.text:
                    yield {"event": "message", "data": json.dumps({"text": chunk.text})}
                    await asyncio.sleep(0.01)
            yield {"event": "done", "data": "[DONE]"}
        except Exception as e:
            logger.exception(f"Error in radar insight: {e}")
            yield {"event": "error", "data": json.dumps({"error": str(e)})}
    return EventSourceResponse(sse_generator())

@acc_app.post("/api/gemini/chat")
async def gemini_chat(request: ChatRequest):
    async def sse_generator():
        try:
            gemini_messages = [types.Content(role="user" if m.role == "user" else "model", parts=[types.Part.from_text(text=m.content)]) for m in request.messages]
            if not gemini_messages:
                yield {"event": "done", "data": "[DONE]"}
                return
            config = types.GenerateContentConfig(system_instruction=GEMINI_INSTRUCTION, tools=[{"google_search": {}}])
            response_stream = await client.aio.models.generate_content_stream(model=MODEL_ID, contents=gemini_messages, config=config)
            async for chunk in response_stream:
                if chunk.text:
                    yield {"event": "message", "data": json.dumps({"text": chunk.text})}
                    await asyncio.sleep(0.01)
            yield {"event": "done", "data": "[DONE]"}
        except Exception as e:
            logger.exception(f"Error in gemini chat: {e}")
            yield {"event": "error", "data": json.dumps({"error": str(e)})}
    return EventSourceResponse(sse_generator())

@acc_app.post("/api/nav/live-pulse")
async def live_policy_pulse(request: PulseRequest):
    async def sse_generator():
        try:
            config = types.GenerateContentConfig(system_instruction=LIVE_PULSE_INSTRUCTION, tools=[{"google_search": {}}], temperature=0.3)
            response_stream = await client.aio.models.generate_content_stream(model=MODEL_ID, contents=f"Fetch latest tax policies for: {request.query}.", config=config)
            async for chunk in response_stream:
                if chunk.text:
                    yield {"event": "message", "data": json.dumps({"text": chunk.text})}
                    await asyncio.sleep(0.01)
            yield {"event": "done", "data": "[DONE]"}
        except Exception as e:
            logger.exception(f"Error in live pulse: {e}")
            yield {"event": "error", "data": json.dumps({"error": str(e)})}
    return EventSourceResponse(sse_generator())

@acc_app.post("/api/nav/dynamic-industries")
async def generate_dynamic_nav(request: NavRequest):
    try:
        config = types.GenerateContentConfig(system_instruction=NAV_INSTRUCTION, response_mime_type="application/json")
        response = await client.aio.models.generate_content(model=MODEL_ID, contents=f"User Operating Model: {request.description}", config=config)
        return {"categories": json.loads(response.text)}
    except Exception as e:
        logger.exception(f"Error generating dynamic nav: {e}")
        return {"categories": [{"title": "Global Compliance", "description": "Tax analysis", "icon": "Globe"}]}

@acc_app.post("/api/generate-dashboard")
async def generate_dashboard(request: DashboardRequest):
    try:
        config = types.GenerateContentConfig(system_instruction=DASHBOARD_INSTRUCTION, response_mime_type="application/json")
        response = await client.aio.models.generate_content(model=MODEL_ID, contents=f"Tax risks for {request.industry} in 2026.", config=config)
        return json.loads(response.text)
    except Exception as e:
        logger.exception(f"Error generating dashboard: {e}")
        return {"industry": request.industry, "risk_factors": [{"area": "System Error", "impact": str(e), "severity": "High"}]}

@acc_app.post("/api/future/boardroom")
async def swarm_boardroom(request: Request):
    body = await request.json()
    prompt = body.get("prompt", "")
    async def sse_generator():
        try:
            BOARDROOM_AGENTS = [
                {"id": "strategist", "name": "Strategist", "instruction": "Aggressive Strategist..."},
                {"id": "auditor", "name": "Auditor", "instruction": "Conservative Auditor..."},
                {"id": "economist", "name": "Economist", "instruction": "Global Economist..."}
            ]
            for agent in BOARDROOM_AGENTS:
                yield {"data": json.dumps({"type": "agent_start", "agent_id": agent["id"], "agent_name": agent["name"]})}
                response_stream = await client.aio.models.generate_content_stream(model=MODEL_ID, contents=prompt, config=types.GenerateContentConfig(system_instruction=agent["instruction"], tools=[{"google_search": {}}]))
                async for chunk in response_stream:
                    if chunk.text: yield {"data": json.dumps({"type": "chunk", "agent_id": agent["id"], "text": chunk.text})}
                yield {"data": json.dumps({"type": "agent_end", "agent_id": agent["id"]})}
                await asyncio.sleep(1)
            yield {"data": json.dumps({"type": "done"})}
        except Exception as e:
            yield {"data": json.dumps({"type": "error", "message": str(e)})}
    return EventSourceResponse(sse_generator())

# Serving the frontend
import os
from fastapi.staticfiles import StaticFiles
import mimetypes

mimetypes.add_type("application/javascript", ".js")
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dist")

if os.path.exists(frontend_dir):
    # Mount static files at the ROOT of the sub-app
    acc_app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
    logger.info(f"Frontend mounted at /acc/ using directory {frontend_dir}")
else:
    logger.warning(f"Frontend directory not found at {frontend_dir}")

# Mount the sub-app at /acc in the main app
app.mount("/acc", acc_app)

@app.get("/health")
async def root_health():
    return {"status": "ok", "message": "Backend is running. App is at /acc"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
