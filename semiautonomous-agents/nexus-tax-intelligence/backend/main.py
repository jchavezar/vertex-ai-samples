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
from vais import vais_client

load_dotenv(dotenv_path="../../.env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Nexus Tax Intelligence Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5182", "http://127.0.0.1:5182", "https://tax.sonrobots.net"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = genai.Client(vertexai=True, project=os.environ.get("GOOGLE_CLOUD_PROJECT"), location="global")

# Rewrite /pwc/api/* → /api/* so requests through the GLB path-based routing work
@app.middleware("http")
async def rewrite_pwc_api(request: Request, call_next):
    if request.url.path.startswith("/pwc/api/"):
        request.scope["path"] = request.url.path.replace("/pwc/api/", "/api/", 1)
    return await call_next(request)
MODEL_ID = "gemini-3.1-flash-lite-preview"

# ─── Instruction Strings ───────────────────────────────────────────────

GEMINI_INSTRUCTION = """
You are the Nexus Chief Tax Intelligence Advisor, an elite AI advisor specialized in global tax intelligence.
Your audience consists of corporate executives (CFOs, Heads of Tax, Directors).
Provide highly professional, accurate, and strategic tax advice.
When asked about current events, rely on your Google Search capability to find the latest real-world developments and cite them.
Focus on corporate tax, transfer pricing, indirect taxes, and OECD Pillar Two.
Be concise, proactive, and structure your insights with clear formatting (markdown, bolding, bullet points).
Always maintain a formal, enterprise-grade tone. Do not use generic AI greetings.
"""

RADAR_INSTRUCTION = """
You are the Strategic Tax Radar AI.
Generate a very concise, easy-to-understand insight about a recent global tax policy change.
CRITICAL: Highlight exactly the most critical key terms using bold markdown (e.g., **word**). Do not prefix your response with anything.
Use Google Search to find the latest news.
Format your response as a direct, streaming insight. No bullet points, just a continuous short paragraph. KEEP IT UNDER 2 SENTENCES.
"""

NAV_INSTRUCTION = """
You are the Nexus Navigation Architect AI.
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
You are the Nexus Global Insights Coordinator.
The user is requesting a live update on tax policies for a specific region or topic.
You MUST use your Google Search tool to find the absolute latest, current news on this topic.
Format your response beautifully with markdown:
- Start with a bold headline reflecting current news.
- Provide exactly 1-2 sentence executive summary of the real-world news.
- Add a bullet point "Risk Impact: [High/Medium/Low] - [1 sentence reason]".
DO NOT make up information. Use grounded search results.
"""

DASHBOARD_INSTRUCTION = """
You are the Nexus Global Insights Coordinator building a generative dashboard.
Given an industry, generate a comprehensive strategic tax risk assessment.
You MUST output a JSON object matching the requested schema exactly.
"""

PILLAR_TWO_INSTRUCTION = """
You are a Pillar Two (GloBE Rules) specialist advisor. Given a set of jurisdictions and corporate structure data, generate a comprehensive Pillar Two compliance assessment.
Include: effective tax rate analysis per jurisdiction, top-up tax exposure, safe harbor eligibility (simplified ETR, routine profits, de minimis), and transitional rule applicability.
Use Google Search for the latest IIR/UTPR implementation status per jurisdiction.
Format your response with clear markdown sections, tables where appropriate, and status indicators (use bold for emphasis).
"""

HEATMAP_INSTRUCTION = """
You are a jurisdictional tax risk analyst. Given a country/region and risk category, generate a concise risk briefing covering: current corporate tax rate, recent legislative changes, pending reforms, treaty network implications, and recommended mitigation strategies.
Use Google Search for the very latest regulatory developments. Keep it under 200 words with clear markdown formatting.
"""

AUDIT_AUDITOR_INSTRUCTION = """
You are an aggressive tax authority auditor from an OECD-aligned jurisdiction. Given a taxpayer's position, identify the 3 most vulnerable areas for challenge.
Ask pointed, specific questions about transfer pricing methodology, substance requirements, and economic rationale.
Format each as a numbered challenge with context. Be thorough but concise.
"""

AUDIT_DEFENSE_INSTRUCTION = """
You are an experienced tax defense advisor. Given the auditor's challenges, construct the strongest possible defense using arm's length principles, business purpose doctrine, and treaty protections.
Be specific and cite applicable guidelines (OECD TPG, UN Model Convention, local rules). End with an overall resilience assessment.
"""

AUDIT_VERDICT_INSTRUCTION = """
You are a senior tax tribunal judge. Given the auditor's challenges and the defense's responses, deliver a final verdict.
Score the taxpayer's position on an "Audit Resilience Score" from 1-10 (1=extremely vulnerable, 10=impregnable).
Provide the score prominently, then a brief rationale for each challenge area. Be balanced and cite specific strengths/weaknesses.
"""

ROADMAP_INSTRUCTION = """
You are a tax transformation strategist. Given a client's current and desired tax operating model, generate a 4-phase transformation roadmap.
Each phase must include: phase_name, duration, milestones (array of strings), technologies (array of strings), estimated_roi_percentage (string like "15-20%"), and mapped_pillar (one of: "Consulting", "Operations & Compliance", "Technology & Data", "Legislation & Regulation").
Also include: industry (string), executive_summary (string), total_estimated_savings (string like "$2-5M annually").
Output as JSON.
"""

HORIZON_INSTRUCTION = """
You are a regulatory intelligence scanner. Use Google Search to find the top 8 upcoming global tax regulatory changes expected in the next 12 months.
For each, provide: title, jurisdiction, expected_effective_date, impact_level (High/Medium/Low), and a one-sentence summary.
Output as a JSON array. Do not include markdown formatting or backticks.
"""

TREATY_INSTRUCTION = """
You are a tax treaty specialist. Given two countries, analyze their bilateral tax treaty (or the absence thereof).
Provide a JSON object with: country_a, country_b, treaty_exists (boolean), withholding_rates (object with dividends_portfolio, dividends_substantial, interest, royalties - each a string like "15%"),
pe_definition (string), lob_provisions (string), mli_impact (string), recent_amendments (string),
overall_protection_score (integer 1-10), strategic_recommendations (array of strings).
Use Google Search for the latest treaty status. Output as JSON only.
"""

# ─── Pydantic Models ───────────────────────────────────────────────────

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

class OverviewRequest(BaseModel):
    query: str
    search_results: Optional[List[Dict[str, Any]]] = None

class ActionItem(BaseModel):
    step: int
    title: str
    description: str

class RiskFactor(BaseModel):
    area: str
    impact: str
    severity: str

class GenerativeDashboardProfile(BaseModel):
    industry: str
    executive_summary: str
    market_trend: str
    risk_factors: List[RiskFactor]
    action_plan: List[ActionItem]

class DashboardRequest(BaseModel):
    industry: str

class BoardroomRequest(BaseModel):
    prompt: str

class PillarTwoRequest(BaseModel):
    jurisdictions: List[str]
    revenue_range: str
    effective_tax_rate: Optional[float] = None

class HeatmapRequest(BaseModel):
    country: str
    risk_category: str

class AuditSimRequest(BaseModel):
    scenario: str
    round_num: Optional[int] = 1
    auditor_questions: Optional[str] = None
    defense_responses: Optional[str] = None

class RoadmapRequest(BaseModel):
    current_state: str
    future_state: str
    industry: str

class Phase(BaseModel):
    phase_name: str
    duration: str
    milestones: List[str]
    technologies: List[str]
    estimated_roi_percentage: str
    mapped_pillar: str

class TransformationRoadmapResponse(BaseModel):
    industry: str
    executive_summary: str
    phases: List[Phase]
    total_estimated_savings: str

class TreatyRequest(BaseModel):
    country_a: str
    country_b: str

class InsightDetailRequest(BaseModel):
    title: str
    type: str
    description: str

class HorizonDetailRequest(BaseModel):
    title: str
    jurisdiction: str

# ─── Boardroom Agents ──────────────────────────────────────────────────

BOARDROOM_AGENTS = [
    {
        "id": "strategist",
        "name": "The Aggressive Strategist",
        "instruction": "You are the Aggressive Tax Strategist. Goal: find loopholes, aggressive restructuring opportunities, and maximum efficiency. Respond in EXACTLY 2 concise, punchy sentences. Be confident and aggressive. Use Google Search for factual grounding."
    },
    {
        "id": "auditor",
        "name": "The Conservative Auditor",
        "instruction": "You are the Conservative Auditor. Goal: 100% compliance, avoid audits, identify risks. You are pessimistic and rules-bound. Respond in EXACTLY 2 concise, clear sentences. Use Google Search for grounding."
    },
    {
        "id": "economist",
        "name": "The Global Economist",
        "instruction": "You are the Global Macro Economist. Focus on trade wars, currency fluctuation, and global GDP shifts. Synthesize the discussion and offer the final executive verdict in EXACTLY 2 concise, visionary sentences. Use Google Search for grounding."
    }
]

# ─── Core Endpoints ────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/api/search")
async def discovery_engine_search(request: SearchRequest):
    try:
        logger.info(f"Querying Discovery Engine for: {request.query}")
        results = await vais_client.search(request.query)
        return results
    except Exception as e:
        logger.error(f"Search error: {e}")
        return {"error": str(e), "results": []}

@app.post("/api/search/generative-overview")
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
                    file_format = struct_data.get("fileFormat", "")
                    contexts.append(f"Result {i+1}:\\nTitle: {title}\\nURL: {link}\\nSnippet: {snippet}\\nFormat: {file_format}")

            context_text = "\\n\\n".join(contexts)
            prompt = f"""User Query: {request.query}\n\nSearch Results:\n{context_text}\n\nTask: Summarize the findings VERY CONCISELY (max 2-3 sentences or 3 short bullet points). Be direct and insightful. If you see a highly relevant PDF in the results, append this exact tag at the very end of your response: [PDF_SUGGESTION]{{"title": "<pdf title>", "url": "<pdf url>", "reason": "<why it's useful>"}}[/PDF_SUGGESTION]"""

            config = types.GenerateContentConfig(
                system_instruction="You are a Strategic AI providing an ultra-concise, brief executive summary of search results. Use markdown. Do not provide lengthy explanations.",
                temperature=0.3
            )
            response_stream = await client.aio.models.generate_content_stream(
                model=MODEL_ID, contents=prompt, config=config
            )
            async for chunk in response_stream:
                if chunk.text:
                    yield {"event": "message", "data": json.dumps({"text": chunk.text})}
                    await asyncio.sleep(0.01)
            yield {"event": "done", "data": "[DONE]"}
        except Exception as e:
            logger.error(f"Error in generative overview: {e}")
            yield {"event": "error", "data": json.dumps({"error": str(e)})}
    return EventSourceResponse(sse_generator())

@app.get("/api/radar/insight")
async def generate_radar_insight(request: Request):
    async def sse_generator():
        try:
            config = types.GenerateContentConfig(
                system_instruction=RADAR_INSTRUCTION,
                tools=[{"google_search": {}}],
            )
            prompt = "What is the most critical corporate tax news right now? Give me a short, simple summary."
            response_stream = await client.aio.models.generate_content_stream(
                model=MODEL_ID, contents=prompt, config=config
            )
            async for chunk in response_stream:
                if chunk.text:
                    yield {"event": "message", "data": json.dumps({"text": chunk.text})}
                    await asyncio.sleep(0.01)
            yield {"event": "done", "data": "[DONE]"}
        except Exception as e:
            logger.error(f"Error in radar insight: {e}")
            yield {"event": "error", "data": json.dumps({"error": str(e)})}
    return EventSourceResponse(sse_generator())

@app.post("/api/gemini/chat")
async def gemini_chat(request: ChatRequest):
    async def sse_generator():
        try:
            gemini_messages = []
            for msg in request.messages:
                role = "user" if msg.role == "user" else "model"
                gemini_messages.append(
                    types.Content(role=role, parts=[types.Part.from_text(text=msg.content)])
                )
            if not gemini_messages:
                yield {"event": "done", "data": "[DONE]"}
                return
            config = types.GenerateContentConfig(
                system_instruction=GEMINI_INSTRUCTION,
                tools=[{"google_search": {}}],
            )
            response_stream = await client.aio.models.generate_content_stream(
                model=MODEL_ID, contents=gemini_messages, config=config
            )
            async for chunk in response_stream:
                if chunk.text:
                    yield {"event": "message", "data": json.dumps({"text": chunk.text})}
                    await asyncio.sleep(0.01)
            yield {"event": "done", "data": "[DONE]"}
        except Exception as e:
            logger.error(f"Error in gemini chat: {e}")
            yield {"event": "error", "data": json.dumps({"error": str(e)})}
    return EventSourceResponse(sse_generator())

@app.post("/api/nav/live-pulse")
async def live_policy_pulse(request: PulseRequest):
    async def sse_generator():
        try:
            config = types.GenerateContentConfig(
                system_instruction=LIVE_PULSE_INSTRUCTION,
                tools=[{"google_search": {}}],
                temperature=0.3
            )
            prompt = f"Fetch the absolute latest news regarding corporate tax policies for: {request.query}."
            response_stream = await client.aio.models.generate_content_stream(
                model=MODEL_ID, contents=prompt, config=config
            )
            async for chunk in response_stream:
                if chunk.text:
                    yield {"event": "message", "data": json.dumps({"text": chunk.text})}
                    await asyncio.sleep(0.01)
            yield {"event": "done", "data": "[DONE]"}
        except Exception as e:
            logger.error(f"Error in live pulse: {e}")
            yield {"event": "error", "data": json.dumps({"error": str(e)})}
    return EventSourceResponse(sse_generator())

@app.post("/api/nav/dynamic-industries")
async def generate_dynamic_nav(request: NavRequest):
    try:
        config = types.GenerateContentConfig(
            system_instruction=NAV_INSTRUCTION,
            response_mime_type="application/json",
            temperature=0.7
        )
        prompt = f"User Operating Model: {request.description}"
        response = await client.aio.models.generate_content(
            model=MODEL_ID, contents=prompt, config=config
        )
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
    try:
        config = types.GenerateContentConfig(
            system_instruction=DASHBOARD_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=GenerativeDashboardProfile,
            temperature=0.2
        )
        prompt = f"Identify the critical global tax risks and strategies for the {request.industry} industry in 2026."
        response = await client.aio.models.generate_content(
            model=MODEL_ID, contents=prompt, config=config
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Error generating dashboard: {e}")
        return {
            "industry": request.industry,
            "executive_summary": "System currently unavailable. Please try again.",
            "market_trend": "Data synthesis interrupted.",
            "risk_factors": [{"area": "System Error", "impact": str(e), "severity": "High"}],
            "action_plan": [{"step": 1, "title": "Retry Request", "description": "Please try submitting the request again."}]
        }

@app.post("/api/future/boardroom")
async def swarm_boardroom(request: Request):
    body = await request.json()
    prompt = body.get("prompt", "")
    async def sse_generator():
        try:
            for agent in BOARDROOM_AGENTS:
                yield {"data": json.dumps({"type": "agent_start", "agent_id": agent["id"], "agent_name": agent["name"]})}
                config = types.GenerateContentConfig(
                    system_instruction=agent["instruction"],
                    temperature=0.7,
                    tools=[{"google_search": {}}]
                )
                response_stream = await client.aio.models.generate_content_stream(
                    model=MODEL_ID, contents=prompt, config=config
                )
                async for chunk in response_stream:
                    if chunk.text:
                        yield {"data": json.dumps({"type": "chunk", "agent_id": agent["id"], "text": chunk.text})}
                yield {"data": json.dumps({"type": "agent_end", "agent_id": agent["id"]})}
                await asyncio.sleep(1)
            yield {"data": json.dumps({"type": "done"})}
        except Exception as e:
            logger.error(f"Boardroom error: {e}")
            yield {"data": json.dumps({"type": "error", "message": str(e)})}
    return EventSourceResponse(sse_generator())

# ─── WOW Feature Endpoints ─────────────────────────────────────────────

@app.post("/api/pillar-two/assess")
async def pillar_two_assess(request: PillarTwoRequest):
    async def sse_generator():
        try:
            jurisdictions_str = ", ".join(request.jurisdictions)
            prompt = f"Assess Pillar Two compliance for a multinational with subsidiaries in: {jurisdictions_str}. Revenue range: {request.revenue_range}. Average ETR: {request.effective_tax_rate or 'not specified'}%."
            config = types.GenerateContentConfig(
                system_instruction=PILLAR_TWO_INSTRUCTION,
                tools=[{"google_search": {}}],
                temperature=0.3
            )
            response_stream = await client.aio.models.generate_content_stream(
                model=MODEL_ID, contents=prompt, config=config
            )
            async for chunk in response_stream:
                if chunk.text:
                    yield {"event": "message", "data": json.dumps({"text": chunk.text})}
                    await asyncio.sleep(0.01)
            yield {"event": "done", "data": "[DONE]"}
        except Exception as e:
            logger.error(f"Error in Pillar Two assessment: {e}")
            yield {"event": "error", "data": json.dumps({"error": str(e)})}
    return EventSourceResponse(sse_generator())

@app.post("/api/heatmap/risk-brief")
async def heatmap_risk_brief(request: HeatmapRequest):
    async def sse_generator():
        try:
            prompt = f"Provide a tax risk briefing for {request.country} in the category of {request.risk_category}."
            config = types.GenerateContentConfig(
                system_instruction=HEATMAP_INSTRUCTION,
                tools=[{"google_search": {}}],
                temperature=0.3
            )
            response_stream = await client.aio.models.generate_content_stream(
                model=MODEL_ID, contents=prompt, config=config
            )
            async for chunk in response_stream:
                if chunk.text:
                    yield {"event": "message", "data": json.dumps({"text": chunk.text})}
                    await asyncio.sleep(0.01)
            yield {"event": "done", "data": "[DONE]"}
        except Exception as e:
            logger.error(f"Error in heatmap risk brief: {e}")
            yield {"event": "error", "data": json.dumps({"error": str(e)})}
    return EventSourceResponse(sse_generator())

@app.post("/api/audit-sim/start")
async def audit_sim_start(request: AuditSimRequest):
    async def sse_generator():
        try:
            prompt = f"Taxpayer's position:\n{request.scenario}\n\nIdentify the 3 most vulnerable areas and ask probing questions."
            config = types.GenerateContentConfig(
                system_instruction=AUDIT_AUDITOR_INSTRUCTION,
                tools=[{"google_search": {}}],
                temperature=0.4
            )
            response_stream = await client.aio.models.generate_content_stream(
                model=MODEL_ID, contents=prompt, config=config
            )
            async for chunk in response_stream:
                if chunk.text:
                    yield {"event": "message", "data": json.dumps({"text": chunk.text})}
                    await asyncio.sleep(0.01)
            yield {"event": "done", "data": "[DONE]"}
        except Exception as e:
            logger.error(f"Error in audit sim start: {e}")
            yield {"event": "error", "data": json.dumps({"error": str(e)})}
    return EventSourceResponse(sse_generator())

@app.post("/api/audit-sim/round")
async def audit_sim_round(request: AuditSimRequest):
    async def sse_generator():
        try:
            if request.round_num == 2:
                prompt = f"Taxpayer's position:\n{request.scenario}\n\nAuditor's challenges:\n{request.auditor_questions}\n\nConstruct the strongest defense."
                instruction = AUDIT_DEFENSE_INSTRUCTION
            else:
                prompt = f"Taxpayer's position:\n{request.scenario}\n\nAuditor's challenges:\n{request.auditor_questions}\n\nDefense responses:\n{request.defense_responses}\n\nDeliver the final verdict with Audit Resilience Score (1-10)."
                instruction = AUDIT_VERDICT_INSTRUCTION
            config = types.GenerateContentConfig(
                system_instruction=instruction,
                tools=[{"google_search": {}}],
                temperature=0.3
            )
            response_stream = await client.aio.models.generate_content_stream(
                model=MODEL_ID, contents=prompt, config=config
            )
            async for chunk in response_stream:
                if chunk.text:
                    yield {"event": "message", "data": json.dumps({"text": chunk.text})}
                    await asyncio.sleep(0.01)
            yield {"event": "done", "data": "[DONE]"}
        except Exception as e:
            logger.error(f"Error in audit sim round: {e}")
            yield {"event": "error", "data": json.dumps({"error": str(e)})}
    return EventSourceResponse(sse_generator())

@app.post("/api/roadmap/generate")
async def generate_roadmap(request: RoadmapRequest):
    try:
        config = types.GenerateContentConfig(
            system_instruction=ROADMAP_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=TransformationRoadmapResponse,
            temperature=0.3
        )
        prompt = f"Industry: {request.industry}\nCurrent State: {request.current_state}\nDesired Future State: {request.future_state}\n\nGenerate a 4-phase transformation roadmap."
        response = await client.aio.models.generate_content(
            model=MODEL_ID, contents=prompt, config=config
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Error generating roadmap: {e}")
        return {"error": str(e)}

@app.get("/api/horizon/scan")
async def horizon_scan(request: Request):
    async def sse_generator():
        try:
            config = types.GenerateContentConfig(
                system_instruction=HORIZON_INSTRUCTION,
                tools=[{"google_search": {}}],
                response_mime_type="application/json",
                temperature=0.3
            )
            prompt = "Scan for the top 8 upcoming global tax regulatory changes in the next 12 months. Include both enacted and proposed legislation."
            response = await client.aio.models.generate_content(
                model=MODEL_ID, contents=prompt, config=config
            )
            items = json.loads(response.text)
            for item in items:
                yield {"event": "message", "data": json.dumps({"type": "item", "item": item})}
                await asyncio.sleep(0.1)
            yield {"event": "done", "data": "[DONE]"}
        except Exception as e:
            logger.error(f"Error in horizon scan: {e}")
            yield {"event": "error", "data": json.dumps({"error": str(e)})}
    return EventSourceResponse(sse_generator())

@app.post("/api/horizon/detail")
async def horizon_detail(request: HorizonDetailRequest):
    async def sse_generator():
        try:
            prompt = f"Provide a detailed analysis of the following upcoming tax regulation:\nTitle: {request.title}\nJurisdiction: {request.jurisdiction}\n\nInclude: background, key provisions, affected taxpayers, implementation timeline, strategic implications, and recommended actions."
            config = types.GenerateContentConfig(
                system_instruction="You are a regulatory intelligence analyst. Provide a thorough but concise analysis of upcoming tax legislation. Use Google Search for the latest information. Format with markdown.",
                tools=[{"google_search": {}}],
                temperature=0.3
            )
            response_stream = await client.aio.models.generate_content_stream(
                model=MODEL_ID, contents=prompt, config=config
            )
            async for chunk in response_stream:
                if chunk.text:
                    yield {"event": "message", "data": json.dumps({"text": chunk.text})}
                    await asyncio.sleep(0.01)
            yield {"event": "done", "data": "[DONE]"}
        except Exception as e:
            logger.error(f"Error in horizon detail: {e}")
            yield {"event": "error", "data": json.dumps({"error": str(e)})}
    return EventSourceResponse(sse_generator())

@app.post("/api/insights/detail")
async def insight_detail(request: InsightDetailRequest):
    async def sse_generator():
        try:
            prompt = f"""Topic: {request.title}
Type: {request.type}
Brief: {request.description}

Provide a comprehensive, executive-level deep dive on this topic. Include:
1. Current landscape and recent developments (use Google Search for latest news)
2. Key implications for multinational corporations
3. Strategic recommendations
4. What to watch in the next 6-12 months

Use clear markdown formatting with headers, bullet points, and bold key terms."""
            config = types.GenerateContentConfig(
                system_instruction="You are a senior tax research analyst producing in-depth insight reports. Use Google Search to ground your analysis in the latest real-world developments. Write in a professional, executive-briefing style. Use markdown formatting.",
                tools=[{"google_search": {}}],
                temperature=0.3
            )
            response_stream = await client.aio.models.generate_content_stream(
                model=MODEL_ID, contents=prompt, config=config
            )
            async for chunk in response_stream:
                if chunk.text:
                    yield {"event": "message", "data": json.dumps({"text": chunk.text})}
                    await asyncio.sleep(0.01)
            yield {"event": "done", "data": "[DONE]"}
        except Exception as e:
            logger.error(f"Error in insight detail: {e}")
            yield {"event": "error", "data": json.dumps({"error": str(e)})}
    return EventSourceResponse(sse_generator())

@app.post("/api/treaty/analyze")
async def analyze_treaty(request: TreatyRequest):
    try:
        config = types.GenerateContentConfig(
            system_instruction=TREATY_INSTRUCTION,
            tools=[{"google_search": {}}],
            response_mime_type="application/json",
            temperature=0.3
        )
        prompt = f"Analyze the bilateral tax treaty between {request.country_a} and {request.country_b}."
        response = await client.aio.models.generate_content(
            model=MODEL_ID, contents=prompt, config=config
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Error analyzing treaty: {e}")
        return {"error": str(e)}

# ─── Startup ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8010, reload=True)
else:
    from fastapi.staticfiles import StaticFiles
    import mimetypes
    mimetypes.add_type("application/javascript", ".js")
    # Try multiple possible locations for the built frontend
    candidates = [
        os.path.join(os.path.dirname(__file__), "dist"),           # /app/dist (Docker)
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "dist"),  # ../dist (local dev)
    ]
    frontend_dir = next((d for d in candidates if os.path.exists(d)), None)
    if frontend_dir:
        app.mount("/pwc", StaticFiles(directory=frontend_dir, html=True), name="frontend")
        logger.info(f"Serving frontend from {frontend_dir} at /pwc")
    else:
        logger.warning(f"Frontend directory not found. Tried: {candidates}")
