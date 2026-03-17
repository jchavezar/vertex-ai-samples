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

# Load env vars
load_dotenv(dotenv_path="../../.env")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="Global Tax Intelligence Backend")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5178", "http://127.0.0.1:5178", "http://localhost:5179", "http://127.0.0.1:5179"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini Client
# We must ensure GEMINI_API_KEY is in the environment
import os
client = genai.Client(vertexai=True, project=os.environ.get("GOOGLE_CLOUD_PROJECT"), location="global")

MODEL_ID = "gemini-3.1-flash-lite-preview"

# Define instructions
COPILOT_INSTRUCTION = """
You are the KPMG Chief Tax Copilot, an elite AI advisor specialized in Global Tax Intelligence developed for KPMG.
Your audience consists of corporate executives (CFOs, Heads of Tax, Directors).
Provide highly professional, accurate, and strategic tax advice.
When asked about current events, upcoming tax rules (e.g., tax updates for 2026), rely on your Google Search capability to find the latest real-world developments and cite them.
Focus on corporate tax, transfer pricing, indirect taxes, and OECD Pillar Two. 
If the user asks why "tax", explain that KPMG is a leader in tax services and this tool is built to navigate complex global tax landscapes.
Be concise, proactive, and structure your insights with clear formatting (markdown, bolding, bullet points when appropriate).
Always maintain a formal, 'enterprise-grade' KPMG tone. Do not use generic AI greetings.
"""

RADAR_INSTRUCTION = """
You are the Strategic Tax Radar AI.
Generate a very concise, easy-to-understand insight about a recent global tax policy change.
CRITICAL: Highlight exactly the most critical key terms using bold markdown (e.g., **word**). Do not prefix your response with anything.
Use Google Search to find the latest news.
Format your response as a direct, streaming insight. No bullet points, just a continuous short paragraph. KEEP IT UNDER 2 SENTENCES.
"""

NAV_INSTRUCTION = """
You are the KPMG Navigation Architect AI.
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
You are the KPMG Global Insights Coordinator.
The user is requesting a live update on tax policies for a specific region or topic.
You MUST use your Google Search tool to find the absolute latest, current news on this topic.
Format your response beautifully with markdown:
- Start with a bold headline reflecting current news.
- Provide a exactly 1-2 sentence executive summary of the real-world news.
- Add a bullet point "Risk Impact: [High/Medium/Low] - [1 sentence reason]".
DO NOT make up information. Use grounded search results.
"""

DASHBOARD_INSTRUCTION = """
You are the KPMG Global Insights Coordinator building a generative dashboard.
Given an industry, generate a comprehensive strategic tax risk assessment.
You MUST output a JSON object matching the requested schema exactly.
"""

# Models
class ChatMessage(BaseModel):
    role: str # "user" or "model" 
    content: str
    
class ChatRequest(BaseModel):
    messages: List[ChatMessage]

class NavRequest(BaseModel):
    description: str

class PulseRequest(BaseModel):
    query: str

class ActionItem(BaseModel):
    step: int
    title: str
    description: str

class RiskFactor(BaseModel):
    area: str
    impact: str
    severity: str # High, Medium, Low

class GenerativeDashboardProfile(BaseModel):
    industry: str
    executive_summary: str
    market_trend: str
    risk_factors: List[RiskFactor]
    action_plan: List[ActionItem]

class DashboardRequest(BaseModel):
    industry: str

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/api/radar/insight")
async def generate_radar_insight(request: Request):
    """
    Generate a live insight based on current search trends for global tax.
    Uses GET to easily trigger from frontend event sources, though POST is also fine.
    """
    async def sse_generator():
        try:
            config = types.GenerateContentConfig(
                system_instruction=RADAR_INSTRUCTION,
                tools=[{"google_search": {}}],
            )
            prompt = "What is the most critical corporate tax news right now? Give me a short, simple summary."
            
            logger.info("Generating Radar Insight...")
            response_stream = await client.aio.models.generate_content_stream(
                model=MODEL_ID,
                contents=prompt,
                config=config
            )
            
            async for chunk in response_stream:
                if chunk.text:
                    yield {
                        "event": "message",
                        "data": json.dumps({"text": chunk.text})
                    }
                    await asyncio.sleep(0.01)
            
            yield {
                "event": "done",
                "data": "[DONE]"
            }
        except Exception as e:
            logger.error(f"Error in radar insight: {e}")
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }
            
    return EventSourceResponse(sse_generator())

@app.post("/api/copilot/chat")
async def copilot_chat(request: ChatRequest):
    """
    Handles multi-turn chat for the Chief Tax Copilot.
    """
    async def sse_generator():
        try:
            # Format history for Gemini API
            gemini_messages = []
            for msg in request.messages:
                role = "user" if msg.role == "user" else "model"
                gemini_messages.append(
                    types.Content(role=role, parts=[types.Part.from_text(text=msg.content)])
                )
                
            if not gemini_messages:
                # Should not happen
                yield {"event": "done", "data": "[DONE]"}
                return
                
            config = types.GenerateContentConfig(
                system_instruction=COPILOT_INSTRUCTION,
                tools=[{"google_search": {}}],
            )
            
            logger.info(f"Chat request with {len(gemini_messages)} history messages")
            
            response_stream = await client.aio.models.generate_content_stream(
                model=MODEL_ID,
                contents=gemini_messages,
                config=config
            )

            async for chunk in response_stream:
                if chunk.text:
                    yield {
                        "event": "message",
                        "data": json.dumps({"text": chunk.text})
                    }
                    await asyncio.sleep(0.01)
                    
            yield {
                "event": "done",
                "data": "[DONE]"
            }
            
        except Exception as e:
            logger.error(f"Error in copilot chat: {e}")
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }

    return EventSourceResponse(sse_generator())

@app.post("/api/nav/live-pulse")
async def live_policy_pulse(request: PulseRequest):
    """
    Streams a live, search-grounded real-world tax policy update.
    """
    async def sse_generator():
        try:
            config = types.GenerateContentConfig(
                system_instruction=LIVE_PULSE_INSTRUCTION,
                tools=[{"google_search": {}}],
                temperature=0.3
            )
            prompt = f"Fetch the absolute latest news regarding corporate tax policies for: {request.query}."
            
            logger.info(f"Generating Live Pulse for: {prompt}")
            response_stream = await client.aio.models.generate_content_stream(
                model=MODEL_ID,
                contents=prompt,
                config=config
            )
            
            async for chunk in response_stream:
                if chunk.text:
                    yield {
                        "event": "message",
                        "data": json.dumps({"text": chunk.text})
                    }
                    await asyncio.sleep(0.01)
            
            yield {
                "event": "done",
                "data": "[DONE]"
            }
        except Exception as e:
            logger.error(f"Error in live pulse: {e}")
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }
            
    return EventSourceResponse(sse_generator())

@app.post("/api/nav/dynamic-industries")
async def generate_dynamic_nav(request: NavRequest):
    """
    Generates a custom navigation structure based on the user's input.
    """
    try:
        config = types.GenerateContentConfig(
            system_instruction=NAV_INSTRUCTION,
            response_mime_type="application/json",
            temperature=0.7
        )
        
        prompt = f"User Operating Model: {request.description}"
        logger.info(f"Generating custom navigation for: {prompt}")
        
        response = await client.aio.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=config
        )
        
        # The response should already be valid JSON due to response_mime_type 
        # and our strict instructions, but we parse it to ensure we send it back correctly
        nav_data = json.loads(response.text)
        return {"categories": nav_data}
        
    except Exception as e:
        logger.error(f"Error generating dynamic nav: {e}")
        return {"categories": [
            {"title": "Global Compliance Engine", "description": "Automated cross-border tax analysis", "icon": "Globe"},
            {"title": "Transfer Pricing Nexus", "description": "Intercompany agreement insights", "icon": "FileText"},
            {"title": "M&A Structuring", "description": "Risk assessment for global transactions", "icon": "Briefcase"},
            {"title": "Digital Service Taxes", "description": "Evaluating digital product exposure", "icon": "Cpu"}
        ]}

@app.post("/api/generate-dashboard")
async def generate_dashboard(request: DashboardRequest):
    """
    Generates a structured interactive dashboard profile for a given industry.
    """
    try:
        config = types.GenerateContentConfig(
            system_instruction=DASHBOARD_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=GenerativeDashboardProfile,
            temperature=0.2
        )
        
        prompt = f"Identify the critical global tax risks and strategies for the {request.industry} industry in 2026."
        logger.info(f"Generating dashboard for industry: {request.industry}")
        
        response = await client.aio.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=config
        )
        
        dashboard_data = json.loads(response.text)
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Error generating dashboard: {e}")
        return {
            "industry": request.industry,
            "executive_summary": "System currently unavailable. Please try again or consult your KPMG representative.",
            "market_trend": "Data synthesis interrupted.",
            "risk_factors": [{"area": "System Error", "impact": str(e), "severity": "High"}],
            "action_plan": [{"step": 1, "title": "Retry Request", "description": "Please try submitting the request again."}]
        }

BOARDROOM_AGENTS = [
    {
        "id": "strategist",
        "name": "The Aggressive Strategist",
        "instruction": "You are the Aggressive Tax Strategist. Goal: find loopholes, aggressive restructuring opportunities, and maximum efficiency at any cost. Respond to the prompt in EXACTLY 2 concise, punchy sentences. Be very confident and aggressive. Use your Search tool for factual grounding in 2026 events."
    },
    {
        "id": "auditor",
        "name": "The Conservative Auditor",
        "instruction": "You are the Conservative Auditor. Goal: 100% compliance, avoid audits, identify risks in the aggressive plan. You are pessimistic and rules-bound. Respond to the prompt and the strategist's ideas in EXACTLY 2 concise, clear sentences. Use your Search tool for grounding."
    },
    {
        "id": "economist",
        "name": "The Global Economist",
        "instruction": "You are the Global Macro Economist. Focus on the big picture: trade wars, currency fluctuation, and global GDP shifts. Synthesize the previous discussion and offer the final executive verdict in EXACTLY 2 concise, visionary sentences. Use your Search tool for real-world grounding."
    }
]

class BoardroomRequest(BaseModel):
    prompt: str

@app.post("/api/future/boardroom")
async def swarm_boardroom(request: Request):
    """
    Streams a debate between 3 AI agents sequentially.
    """
    body = await request.json()
    prompt = body.get("prompt", "")
    
    async def sse_generator():
        try:
            for agent in BOARDROOM_AGENTS:
                agent_id = agent["id"]
                agent_name = agent["name"]
                
                # Signal frontend that this agent is starting
                yield {"data": json.dumps({"type": "agent_start", "agent_id": agent_id, "agent_name": agent_name})}
                
                config = types.GenerateContentConfig(
                    system_instruction=agent["instruction"],
                    temperature=0.7,
                    tools=[{"google_search": {}}]
                )
                
                response_stream = await client.aio.models.generate_content_stream(
                    model=MODEL_ID,
                    contents=prompt,
                    config=config
                )
                
                async for chunk in response_stream:
                    if chunk.text:
                        yield {"data": json.dumps({"type": "chunk", "agent_id": agent_id, "text": chunk.text})}
                
                # Signal frontend that this agent finished
                yield {"data": json.dumps({"type": "agent_end", "agent_id": agent_id})}
                
                # Small pause between agents for dramatic effect
                await asyncio.sleep(1)
                
            yield {"data": json.dumps({"type": "done"})}
        except Exception as e:
            logger.error(f"Boardroom error: {e}")
            yield {"data": json.dumps({"type": "error", "message": str(e)})}

    return EventSourceResponse(sse_generator())

if __name__ == "__main__":
    import uvicorn
    # If running directly, we don't mount the frontend because Vite handles it in dev mode
    uvicorn.run("main:app", host="0.0.0.0", port=8009, reload=True)
else:
    # When deployed (or run via some production script), we serve the dist folder
    import os
    from fastapi.staticfiles import StaticFiles
    import mimetypes
    
    # ensure JS files are served correctly
    mimetypes.add_type("application/javascript", ".js")
    
    # Path to the React built files
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dist")
    
    if os.path.exists(frontend_dir):
        # Mount the static files at root
        app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
    else:
        logger.warning(f"Frontend directory not found at {frontend_dir}. Ensure 'npm run build' is run.")

