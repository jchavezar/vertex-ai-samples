# -*- coding: utf-8 -*-
"""Google Cloud Agent Platform & AI Glossary (`shared/glossary_launchpad_ui.py`).

A clean, authoritative, A-to-Z & categorized AI Glossary built specifically for
testing and building on Google Cloud's Agent Platform (Vertex AI, ADK, Agent Engine,
MCP, A2A, Tri-Modal Grounding, BigQuery ML & Vector Search, GECX, and Safety Guardrails).

Exports:
1. `render_dynamic_glossary_tab_html(auth_token: str) -> str`
   Inner HTML for `<div id="tab-pane-glossary" class="portal-tab-pane">...</div>`.
2. `render_standalone_glossary_page_html(auth_token: str) -> str`
   Complete standalone Apple Liquid Glass page (`<!DOCTYPE html>...`) for `GET /glossary`.
"""

import html as _html
import json
import re as _re
from typing import Dict, List, Any


def _fmt_inline_md(raw_text: str) -> str:
    """Safely escapes HTML and formats `**bold**` and `` `code` `` inline tokens."""
    escaped = _html.escape(str(raw_text or "")).replace("\n", "<br>")
    escaped = _re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = _re.sub(r"`([^`]+)`", r'<code class="lg-inline-code">\1</code>', escaped)
    return escaped

NEXTGEN_TOKEN = "rocket:e3a48aa96ebeb0731e4c751d"
GLOSSARY_DOC_URL = "https://docs.google.com/document/d/1UwZpS8gmEwY07329NjUakSmNZSHL-WEwhI2ivG8a7dk/edit?tab=t.0"

# ==============================================================================
# PRECISION VECTOR SVG ICON SYSTEM (`GL_ICONS`) — ZERO EMOJIS
# ==============================================================================
GL_ICONS: Dict[str, str] = {
    "compass": '<circle cx="12" cy="12" r="9"/><polygon points="15.5,8.5 13.5,13.5 8.5,15.5 10.5,10.5"/>',
    "cpu": '<rect x="6" y="6" width="12" height="12" rx="2"/><rect x="9.5" y="9.5" width="5" height="5" rx="1"/><path d="M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4"/>',
    "doc_ext": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="8" y1="13" x2="16" y2="13"/><line x1="8" y1="17" x2="13" y2="17"/>',
    "arrow_left": '<line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/>',
    "arrow_right": '<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>',
    "arrow_up_right": '<line x1="7" y1="17" x2="17" y2="7"/><polyline points="8 7 17 7 17 16"/>',
    "search": '<circle cx="11" cy="11" r="7.5"/><line x1="21" y1="21" x2="16.4" y2="16.4"/>',
    "flip": '<polyline points="17 2 21 6 17 10"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><polyline points="7 22 3 18 7 14"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/>',
    "listen": '<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.5 8.5a5 5 0 0 1 0 7"/><path d="M19 6a8.5 8.5 0 0 1 0 12"/>',
    "lightbulb": '<path d="M9 18h6"/><path d="M10 22h4"/><path d="M15.1 14c.2-.9.7-1.6 1.4-2.3A6 6 0 1 0 7.5 11.7c.7.7 1.2 1.4 1.4 2.3"/>',
    "layers": '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 12 12 17 22 12"/><polyline points="2 17 12 22 22 17"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/>',
    "terminal": '<polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/><rect x="2" y="3" width="20" height="18" rx="3" stroke-opacity="0.45"/>',
    "book": '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',
    "rocket": '<path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/>',
    "play": '<polygon points="6 4 20 12 6 20 6 4" fill="currentColor" fill-opacity="0.22"/>',
    "reset": '<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/>',
    "close": '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
    "copy": '<rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>',
}


def gl_icon(name: str, size: int = 16, cls: str = "gl-vec-icon") -> str:
    """Renders a crisp inline SVG vector icon."""
    inner = GL_ICONS.get(name, GL_ICONS["compass"])
    return (
        f'<svg class="{cls}" width="{size}" height="{size}" viewBox="0 0 24 24" '
        f'fill="none" stroke="currentColor" stroke-width="1.8" '
        f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{inner}</svg>'
    )


def gl_well(name: str, well_cls: str = "well-cobalt", size: int = 18) -> str:
    """Renders a 36x36 anodized glass squircle well containing a precision vector SVG."""
    return f'<span class="gl-icon-well {well_cls}" aria-hidden="true">{gl_icon(name, size)}</span>'


# ==============================================================================
# AUTHORITATIVE GLOSSARY DICTIONARY (20 CORE AGENT PLATFORM & AI TERMS)
# Focused 100% on Google Cloud Vertex AI, Agent Platform, ADK, BigQuery & GECX
# ==============================================================================
GLOSSARY_TERMS: List[Dict[str, Any]] = [
    # --- 1. CORE MENTAL MODEL ---
    {
        "id": "term-agent-formula",
        "cat": "Mental Model",
        "badge": "MENTAL MODEL · CORE FORMULA",
        "badge_cls": "lg-badge-emerald",
        "term": "Agent = Model (Brain) + Harness (Hands & Guardrails)",
        "summary": "The foundational formula of Google Cloud's Agent Platform: an LLM alone only predicts text/audio; the Agent Harness gives it tools, memory, sandboxes, and security to execute real work.",
        "analogy": "A raw AI Model (`gemini-3.8-flash`) is like a brilliant underwriter locked in an empty room—it can reason and talk, but it cannot look up a live mortgage rate or calculate a payment. The Agent Harness (built with ADK and Vertex AI Agent Engine) gives that brain hands, a calculator, database access, and compliance rules.",
        "platform": "In Google Cloud Agent Platform, the **Brain** is a Vertex AI model (`gemini-4-argon` or `gemini-3.8-flash`) and the **Harness** is orchestrated by the **Agent Development Kit (ADK)** and **Vertex AI Agent Engine**.",
        "code": """from google.adk.agents import LlmAgent

# Agent = Brain (model) + Harness (instruction + tools + guardrails)
underwriting_agent = LlmAgent(
    name="rocket_underwriting_auditor",
    model="gemini-4-argon",
    instruction="Verify Fannie Mae B3-3.1 income rules and compute DTI via the sandbox tool.",
    tools=[query_bigquery_guidelines, calculate_dti_in_sandbox],
)""",
    },
    {
        "id": "term-task-vs-chat",
        "cat": "Mental Model",
        "badge": "MENTAL MODEL · ARCHITECTURE",
        "badge_cls": "lg-badge-emerald",
        "term": "Prompt Chat vs. Task-Based Agentic AI",
        "summary": "Prompt Chat waits for a human to type every question; a Task-Based Agent on Vertex AI breaks a business goal into steps, calls APIs/databases autonomously, and returns a verified result.",
        "analogy": "Prompt Chat is like asking a colleague for advice in a hallway. Task-Based Agentic AI is like handing a complete loan file to an automated operations pipeline that extracts the W-2s, checks guidelines, runs the math, and hands you a finished worksheet.",
        "platform": "Built on **Vertex AI Agent Platform** using **ADK (`SequentialAgent`, `ParallelAgent`, `LlmAgent`)** deployed on **Cloud Run** or **Vertex AI Agent Engine**.",
        "code": """from google.adk.agents import SequentialAgent

# Multi-step task pipeline on Google Cloud Agent Platform
loan_audit_pipeline = SequentialAgent(
    name="loan_clear_to_close_pipeline",
    sub_agents=[document_ocr_agent, fannie_mae_rag_agent, trid_math_sandbox_agent],
)""",
    },
    {
        "id": "term-tokens-context",
        "cat": "Mental Model",
        "badge": "MENTAL MODEL · CAPACITY",
        "badge_cls": "lg-badge-emerald",
        "term": "Tokens, Context Window (1M–2M) & Context Caching",
        "summary": "Tokens are the building blocks of text, audio, and video processed by Gemini; the Context Window is how much data the model can hold in working memory in a single call.",
        "analogy": "If a standard AI has a sticky-note-sized desk, Gemini's 1M-to-2M token Context Window is a conference table big enough to lay out an entire 1,200-page Fannie Mae Selling Guide, a 200-page borrower tax packet, and a 10-minute walkthrough video all at once. **Context Caching** keeps that manual pinned on the table so you don't pay to re-read it on every question.",
        "platform": "**Vertex AI Context Caching (`client.caches.create`)** cuts input token costs by up to 75% and reduces latency when multiple agents query the same underwriting manuals or codebases.",
        "code": """from google import genai
from google.genai import types

client = genai.Client(vertexai=True, project="dev-233554-hllwn26-hack-f1f8", location="global")
cache = client.caches.create(
    model="gemini-3.8-flash",
    config=types.CreateCachedContentConfig(
        contents=[fannie_mae_selling_guide_pdf],
        ttl="3600s",
    ),
)""",
    },
    {
        "id": "term-structured-outputs",
        "cat": "Mental Model",
        "badge": "MENTAL MODEL · RELIABILITY",
        "badge_cls": "lg-badge-emerald",
        "term": "Structured Outputs (`response_schema`) & System Instructions",
        "summary": "Forcing the model to follow strict behavioral rules (`system_instruction`) and return guaranteed, type-safe JSON matching a Pydantic or OpenAPI schema (`response_schema`).",
        "analogy": "Instead of letting an AI write a free-form essay that breaks your downstream UI or database, Structured Outputs act like a strict digital tax form—every box must be filled with the exact data type required (numbers, booleans, enums).",
        "platform": "Enforced natively by **Vertex AI Gemini API** during token decoding (`response_mime_type='application/json'`), guaranteeing 100% valid JSON for downstream APIs.",
        "code": """from pydantic import BaseModel

class UnderwritingDecision(BaseModel):
    loan_id: str
    dti_ratio: float
    qualifies: bool
    citations: list[str]

resp = client.models.generate_content(
    model="gemini-3.8-flash",
    contents="Audit borrower DTI and cite guidelines.",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=UnderwritingDecision,
    ),
)""",
    },

    # --- 2. AGENT PLATFORM & ADK ---
    {
        "id": "term-adk",
        "cat": "Agent Platform",
        "badge": "AGENT PLATFORM · FRAMEWORK",
        "badge_cls": "lg-badge-cobalt",
        "term": "ADK (Agent Development Kit)",
        "summary": "Google's open-source, code-first Python/TypeScript framework (`google-adk`) for building, orchestrating, testing, and debugging single and multi-agent systems.",
        "analogy": "If Gemini is the engine, **ADK** is the chassis, steering wheel, and transmission that lets engineers wire together tools, subagents, session memory, and guardrails in clean, testable Python code.",
        "platform": "Runs locally with a built-in web debugger (`adk web`) and deploys in one command to **Cloud Run** or **Vertex AI Agent Engine**.",
        "code": """# Install & launch the local ADK Agent Debugger UI:
pip install google-adk
adk web ./my_rocket_agent""",
    },
    {
        "id": "term-agent-engine",
        "cat": "Agent Platform",
        "badge": "AGENT PLATFORM · RUNTIME",
        "badge_cls": "lg-badge-cobalt",
        "term": "Vertex AI Agent Engine",
        "summary": "Google Cloud's fully managed enterprise runtime for deploying, scaling, tracing, and governing production agents with persistent session state and memory.",
        "analogy": "Once you build an agent on your laptop with ADK, **Vertex AI Agent Engine** is the managed hospital-grade control tower that runs it 24/7, tracks every tool call in Cloud Trace, manages user sessions, and scales automatically.",
        "platform": "Part of **Vertex AI Agent Builder**; integrates natively with **Cloud Trace (OpenTelemetry)**, **Session Memory Bank**, and **IAM**.",
        "code": """from vertexai.preview import reasoning_engines

# Deploy an ADK agent to managed Vertex AI Agent Engine
remote_agent = reasoning_engines.ReasoningEngine.create(
    underwriting_agent,
    requirements=["google-cloud-aiplatform[adk,agent_engines]"],
)""",
    },
    {
        "id": "term-skills",
        "cat": "Agent Platform",
        "badge": "AGENT PLATFORM · MODULARITY",
        "badge_cls": "lg-badge-cobalt",
        "term": "Skills (`SKILL.md`) & Reusable Agent Playbooks",
        "summary": "Self-contained folders containing a `SKILL.md` instruction file plus helper scripts and examples that teach an agent how to perform a specialized domain workflow on demand.",
        "analogy": "Instead of cramming 50 different job manuals into one giant prompt, a **Skill (`SKILL.md`)** is a modular recipe card. When an agent encounters a TRID fee audit or a BigQuery forecast task, it loads only the exact `SKILL.md` playbook it needs.",
        "platform": "Used across **Google Antigravity IDE**, **Agents CLI**, and **ADK** repositories so every microservice carries its own step-by-step domain instructions.",
        "code": """# Standard SKILL.md structure inside each microservice repo:
---
name: fannie-mae-1084-auditor
description: Reconciles W-2 and Schedule C tax returns using deterministic Python math.
---
1. Parse line items via Document AI.
2. Execute `sandbox_tool.py` for penny-exact cash-flow math.""",
    },
    {
        "id": "term-subagents",
        "cat": "Agent Platform",
        "badge": "AGENT PLATFORM · VELOCITY",
        "badge_cls": "lg-badge-cobalt",
        "term": "Parallel Subagents (Swarm Fan-Out)",
        "summary": "An orchestrator pattern where a coordinator agent dispatches multiple specialized worker agents (`Subagents`) concurrently and merges their structured outputs.",
        "analogy": "Instead of sending one home inspector to check the roof, plumbing, electrical, title, and flood zone one after another (taking 6.4 seconds), you send 5 specialist inspectors into the house **at the exact same time** and merge their reports in 1.5 seconds (4.0x faster).",
        "platform": "Implemented via **`ParallelAgent` in ADK** or `asyncio.gather` calling **`gemini-3.1-flash-lite`** workers, synthesized by a **`gemini-3.8-flash`** or **`gemini-4-argon`** coordinator.",
        "code": """import asyncio

# 5 concurrent subagents execute in ~1.5s instead of ~6.4s serial
income, title, trid = await asyncio.gather(
    run_subagent("income_1084", model="gemini-3.1-flash-lite", data=tax_docs),
    run_subagent("title_liens", model="gemini-3.1-flash-lite", data=title_commitment),
    run_subagent("trid_audit",  model="gemini-3.1-flash-lite", data=cd_vs_le),
)""",
    },
    {
        "id": "term-alm",
        "cat": "Agent Platform",
        "badge": "AGENT PLATFORM · TAXONOMY",
        "badge_cls": "lg-badge-cobalt",
        "term": "ALM — All 3 Meanings in AI & Engineering",
        "summary": "Depending on the team, 'ALM' refers to: (1) Application Lifecycle Management (SDLC), (2) Agent Lifecycle Management (AgentOps), or (3) Audio-Language Model (Native Voice AI).",
        "analogy": "One acronym, three distinct meanings: **Software Engineers** mean writing, testing, and deploying code (`Antigravity IDE`). **Platform Engineers** mean versioning, tracing, and evaluating AI agents (`Vertex AI Agent Engine`). **Voice/CX Engineers** mean native 24kHz audio models (`gemini-3.8-live`) that hear tone and interruptions directly without speech-to-text.",
        "platform": "Covered end-to-end on Google Cloud via **Antigravity IDE** (App ALM), **Vertex AI Agent Engine** (Agent ALM), and **`gemini-3.8-live` + GECX** (Audio-Language Model).",
        "code": """# 1. App ALM:   Antigravity IDE + Gemini Code Assist
# 2. Agent ALM: Vertex AI Agent Engine + Cloud Trace + Eval Service
# 3. Audio ALM: gemini-3.8-live (Native 24kHz BidiGenerateContent WebSocket)""",
    },
    {
        "id": "term-gecx",
        "cat": "Agent Platform",
        "badge": "AGENT PLATFORM · CONTACT CENTER",
        "badge_cls": "lg-badge-cobalt",
        "term": "GECX (Customer Engagement Suite) & `cxas-scrappy`",
        "summary": "Google Cloud's omnichannel Contact Center & Customer Experience Agent Platform (`ces.cloud.google.com`) paired with `cxas-scrappy` for automated PRD-to-Agent evaluation hill-climbing.",
        "analogy": "GECX is the mission control for voice and chat customer service agents (like Mr. Cooper servicing or Rocket Mortgage inbound calls). **`cxas-scrappy`** takes a written Product Requirements Document (PRD), builds the agent, runs 100 simulated borrower calls against it, and refines the instructions until it passes every test.",
        "platform": "Accessible at **`ces.cloud.google.com`** and Ricky Merrefield's **GECX Launchpad**, supporting telephony, WebRTC voice, deterministic tool guardrails, and warm banker transfers.",
        "code": """# Compile a PRD into a tested GECX voice/chat agent and hill-climb accuracy:
cxas-scrappy build --prd ./mr_cooper_escrow_concierge.md --eval-runs 25""",
    },

    # --- 3. GROUNDING, RAG & TOOLS ---
    {
        "id": "term-function-calling",
        "cat": "Grounding & Tools",
        "badge": "GROUNDING & TOOLS · ACTION",
        "badge_cls": "lg-badge-amber",
        "term": "Function Calling (Tool Use)",
        "summary": "The capability of a Gemini model to recognize when it needs external data or action, emit a structured JSON function call (`name` + `args`), and incorporate the API's return value into its answer.",
        "analogy": "Instead of guessing today's 30-year fixed mortgage rate from training data, Function Calling lets Gemini pause, fill out a structured request slip to your pricing API (`get_live_rate(fico=760, ltv=80)`), wait 50ms for the real number, and give the borrower an exact quote.",
        "platform": "Supported across all **Vertex AI Gemini 3.x / 4.0 models** (including real-time **`gemini-3.8-live`** voice sessions) via Python function docstrings or OpenAPI schemas.",
        "code": """def get_conforming_rate(fico: int, ltv_pct: float, state: str) -> dict:
    \"\"\"Returns live conforming 30-year fixed mortgage rate and points.\"\"\"
    return {"rate_pct": 6.125, "points": 0.25, "apr_pct": 6.210}

resp = client.models.generate_content(
    model="gemini-3.8-flash",
    contents="What is my rate in MI with a 760 FICO and 80% LTV?",
    config=types.GenerateContentConfig(tools=[get_conforming_rate]),
)""",
    },
    {
        "id": "term-mcp",
        "cat": "Grounding & Tools",
        "badge": "GROUNDING & TOOLS · PROTOCOL",
        "badge_cls": "lg-badge-amber",
        "term": "MCP (Model Context Protocol)",
        "summary": "An open standard that acts as a universal 'USB-C port' connecting AI agents to enterprise databases, APIs, and internal tools without writing custom glue code for every model.",
        "analogy": "Before USB-C, every phone and laptop needed a different charger cable. **MCP** is USB-C for AI tools: once Rocket wraps BigQuery, Encompass, or SharePoint in an MCP server, any ADK agent, Antigravity IDE session, or CLI can plug into it immediately.",
        "platform": "Natively supported in **Google ADK (`MCPToolset`)**, **Antigravity IDE**, and **Cloud Run** microservices.",
        "code": """from mcp.server.fastmcp import FastMCP

mcp = FastMCP("rocket-pricing-mcp")

@mcp.tool()
def lookup_mshda_grant(zip_code: str, purchase_price: float) -> dict:
    return {"eligible": purchase_price <= 544233, "max_grant_usd": 10000}""",
    },
    {
        "id": "term-a2a",
        "cat": "Grounding & Tools",
        "badge": "GROUNDING & TOOLS · INTEROP",
        "badge_cls": "lg-badge-amber",
        "term": "A2A (Agent-to-Agent Protocol)",
        "summary": "Google's open interoperability standard enabling independent AI agents built by different teams (or on different frameworks) to discover capabilities (`AgentCard`) and delegate tasks securely.",
        "analogy": "**MCP** connects an *Agent to a Tool* (like a calculator or database). **A2A** connects an *Agent to another Agent*—like a Redfin Home-Search Agent passing a pre-qualified buyer's context baton directly to a Rocket Mortgage Rate-Lock Agent.",
        "platform": "Built into **Vertex AI Agent Engine** and **Google ADK**, using JSON-RPC task lifecycles and `/.well-known/agent.json` discovery cards.",
        "code": """# MCP vs. A2A Rule of Thumb:
# - Use MCP when an agent calls a stateless tool/database (Agent -> Tool).
# - Use A2A when a Redfin Agent delegates a goal to a Rocket Mortgage Agent (Agent -> Agent).""",
    },
    {
        "id": "term-trimodal-grounding",
        "cat": "Grounding & Tools",
        "badge": "GROUNDING & TOOLS · VERIFICATION",
        "badge_cls": "lg-badge-amber",
        "term": "Tri-Modal Grounding (Google Maps + YouTube + Google Search)",
        "summary": "Anchoring Gemini's responses simultaneously in live Google Maps place data, YouTube video streams (`Part.from_uri`), and live Google Search web citations in a single request.",
        "analogy": "Turns every question from a closed-book memory test into an open-book inspection across three worlds at once: **Google Maps** verifies actual walking distances and schools, **YouTube** inspects the property walkthrough video frame-by-frame, and **Google Search** verifies 2026 county property taxes and down-payment grants.",
        "platform": "Exclusive to **Vertex AI Gemini (`gemini-3.8-flash` / `gemini-4-argon`)** using `GoogleMaps()`, `GoogleSearch()`, and native `Part.from_uri` video understanding.",
        "code": """stream = client.models.generate_content_stream(
    model="gemini-3.8-flash",
    contents=[
        types.Part.from_uri(file_uri="https://www.youtube.com/watch?v=...", mime_type="video/*"),
        "Verify kitchen finishes in video, walkable cafes on Maps, and 2026 MSHDA grants."
    ],
    config=types.GenerateContentConfig(
        tools=[types.Tool(google_maps=types.GoogleMaps()), types.Tool(google_search=types.GoogleSearch())]
    ),
)""",
    },
    {
        "id": "term-rag-vector-rrf",
        "cat": "Grounding & Tools",
        "badge": "GROUNDING & TOOLS · DATA & SEARCH",
        "badge_cls": "lg-badge-amber",
        "term": "Enterprise RAG, Vector Embeddings & Hybrid RRF Search",
        "summary": "Retrieval-Augmented Generation (RAG) converts text (`gemini-embedding-001`, 3072-D) and photos (`multimodalembedding@001`, 1408-D) into numeric coordinates in BigQuery and merges results via Reciprocal Rank Fusion (RRF).",
        "analogy": "Keyword search only matches exact words (missing a house described as 'sun-drenched timber sanctuary' when you searched 'bright wood home'). **Vector Embeddings** map meaning and visual style into GPS coordinates so BigQuery `VECTOR_SEARCH` finds architectural twins by text AND photo at once.",
        "platform": "Runs directly inside **BigQuery (`VECTOR_SEARCH` with `COSINE` distance)** and **Vertex AI Search** with zero external vector database required.",
        "code": """SELECT base.listing_id, base.address, base.price, (1 - distance) AS cosine_similarity
FROM VECTOR_SEARCH(
  TABLE `vtxdemos.rocket_re.listings_multimodal_vectors`, 'text_embedding_3072',
  (SELECT query_vec FROM query_embedding),
  top_k => 12, distance_type => 'COSINE'
);""",
    },

    # --- 4. SAFETY, SANDBOX & EVAL ---
    {
        "id": "term-gvisor-sandbox",
        "cat": "Safety & Eval",
        "badge": "SAFETY & EVAL · DETERMINISTIC MATH",
        "badge_cls": "lg-badge-purple",
        "term": "gVisor Code Execution Sandbox (Deterministic Math)",
        "summary": "An isolated, kernel-hardened container environment where an AI agent writes and executes real Python code (`Decimal`) so financial calculations are 100% penny-exact.",
        "analogy": "Language models predict words—they should never do mental math on a borrower's Debt-to-Income (DTI) ratio, amortization table, or TRID tolerance cure. A **gVisor Sandbox** is a sealed, blast-proof calculator room where the agent executes real Python code and returns exact numbers.",
        "platform": "Available via **Vertex AI Code Execution Tool (`Tool(code_execution=...)`)**, **Agent Engine Code Interpreter**, and **Cloud Run gVisor (`runsc`)** sandboxes.",
        "code": """from decimal import Decimal, ROUND_HALF_UP

def compute_piti_exact(loan_amount: float, annual_rate_pct: float, term_months: int = 360) -> float:
    # Executed inside deterministic Python sandbox — zero LLM arithmetic guessing
    r = Decimal(str(annual_rate_pct)) / Decimal("100") / Decimal("12")
    p = Decimal(str(loan_amount))
    pmt = p * (r * (1 + r) ** term_months) / ((1 + r) ** term_months - 1)
    return float(pmt.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))""",
    },
    {
        "id": "term-model-armor-dlp",
        "cat": "Safety & Eval",
        "badge": "SAFETY & EVAL · SECURITY",
        "badge_cls": "lg-badge-purple",
        "term": "Model Armor & Cloud Sensitive Data Protection (DLP)",
        "summary": "Enterprise security filters that screen prompts and responses for prompt-injection attacks, jailbreaks, and toxic content while automatically masking SSNs, account numbers, and GLBA PII.",
        "analogy": "Think of **Model Armor** as the airport security scanner that blocks malicious prompt injections at the door, and **Cloud DLP** as the automatic black marker that redacts Social Security and bank routing numbers before any document touches a log.",
        "platform": "Enforced at the **Vertex AI API & Agent Engine** boundary alongside VPC Service Controls (VPC-SC) and Customer-Managed Encryption Keys (CMEK).",
        "code": """# Zero-Training & PII Guardrail Invariant on Vertex AI:
# 1. Cloud SDP de-identifies [SSN], [ACCOUNT_NUMBER], [ROUTING_NUMBER] pre-inference.
# 2. Model Armor blocks prompt injection & jailbreak attempts prior to tool execution.""",
    },
    {
        "id": "term-llm-judge",
        "cat": "Safety & Eval",
        "badge": "SAFETY & EVAL · QUALITY",
        "badge_cls": "lg-badge-purple",
        "term": "LLM-as-a-Judge & Multimodal Evaluation",
        "summary": "Using an independent evaluator model (`gemini-3.8-flash` or `gemini-4-argon`) with a strict grading rubric to score another agent's accuracy, groundedness, and visual coherence.",
        "analogy": "Just like a senior quality-control underwriter reviews a junior processor's file before closing, an **LLM-as-a-Judge** inspects the agent's output (and even inspects listing photos to verify they match the architectural claim) and assigns an objective score.",
        "platform": "Built into **Vertex AI GenAI Evaluation Service** and used live in **Demo #5 (Honest 8-Photo Multimodal Appraisal Judge)**.",
        "code": """judge_resp = client.models.generate_content(
    model="gemini-3.8-flash",
    contents=[*eight_property_photos, "Score architectural coherence (0-100) and list any discrepancies."],
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=MultimodalAuditVerdict,
    ),
)""",
    },

    # --- 5. 2026 VERTEX AI MODELS ---
    {
        "id": "term-gemini-models-tier",
        "cat": "2026 Models",
        "badge": "2026 MODELS · TEXT, VISION & VOICE",
        "badge_cls": "lg-badge-crimson",
        "term": "Gemini 4 Argon vs. Gemini 3.8 Flash vs. 3.1 Flash-Lite vs. 3.8 Live",
        "summary": "How to pick the right 2026 Gemini model on Vertex AI based on reasoning depth, latency budget, concurrency, and real-time voice/video modality.",
        "analogy": "• **`gemini-4-argon`**: Your *Supreme Court Underwriter* for deep multi-document tax, legal, and code reasoning.\n• **`gemini-3.8-flash`**: Your *Everyday All-Star Workhorse* for sub-2s chat, Tri-Modal Maps/YouTube/Search grounding, and multimodal judging.\n• **`gemini-3.1-flash-lite`**: Your *High-Speed Parallel Sorting Crew* for 5-way subagent swarms and high-volume classification.\n• **`gemini-3.8-live`**: Your *Face-to-Face 24kHz Voice & 24fps Video Concierge* with <200ms native barge-in (`BidiGenerateContent`).",
        "platform": "All verified live on **Vertex AI (`location='global'` for Argon/Flash/Flash-Lite; `location='us-central1'` for `gemini-3.8-live`)**.",
        "code": """# 2026 Vertex AI Model Selection Cheat-Sheet:
MODEL_DEEP_REASONING = "gemini-4-argon"        # Complex 1084 underwriting & legal AST redlining
MODEL_FAST_DEFAULT   = "gemini-3.8-flash"      # Sub-2s chat, Maps/YouTube grounding & Judge
MODEL_SWARM_LITE     = "gemini-3.1-flash-lite" # Parallel subagent fan-out & routing
MODEL_LIVE_AVATAR    = "gemini-3.8-live"       # 24kHz Bidi audio + 24fps H.264 Video Avatar""",
    },
    {
        "id": "term-veo-imagen-timesfm",
        "cat": "2026 Models",
        "badge": "2026 MODELS · MEDIA & TIME-SERIES",
        "badge_cls": "lg-badge-crimson",
        "term": "Veo 3.1, Nano Banana 2 (`gemini-3.1-flash-image`) & BigQuery TimesFM 2.0",
        "summary": "Google Cloud's specialized foundation models for cinematic 9:16/16:9 video generation (`veo-3.1`), conversational image staging (`gemini-3.1-flash-image`), and zero-shot SQL forecasting (`TimesFM 2.0`).",
        "analogy": "• **`veo-3.1-fast-generate-001`**: Turns property photos or prompts into smooth 9:16 social Reels and 16:9 steadicam room walkthroughs.\n• **`gemini-3.1-flash-image` (Nano Banana 2) & `imagen-4.0-generate-001`**: Stages empty rooms and renders photorealistic architectural keyframes in ~2.5s.\n• **BigQuery ML `AI.FORECAST` (`TimesFM 2.0`)**: A 200M-parameter time-series foundation model built right into SQL that forecasts refinance waves and escrow outflows with zero model training.",
        "platform": "Live in **Demo #1 (`BigQuery TimesFM 2.0`)**, **Demo #2 (`Veo 3.1 Reels Studio`)**, and **Demo #5 (`Veo 3.1 Property Tours`)**.",
        "code": """-- Zero-Shot Time-Series Forecasting in 1 BigQuery SQL Query (TimesFM 2.0):
SELECT forecast_timestamp, forecast_value, prediction_interval_lower_bound, prediction_interval_upper_bound
FROM AI.FORECAST(
  TABLE `vtxdemos.rocket_nextgen_timesfm.weekly_refi_locks`,
  data_col => 'lock_volume',
  timestamp_col => 'week_start',
  horizon => 12
);""",
    },
]


# ==============================================================================
# INDUSTRY TOOL -> GOOGLE CLOUD AGENT PLATFORM TRANSLATOR ROWS
# ==============================================================================
AGENT_PLATFORM_TRANSLATOR: List[Dict[str, str]] = [
    {
        "familiar": "LangChain / CrewAI / AutoGen",
        "category": "Multi-Agent Orchestration",
        "gcp": "Google ADK (`google-adk`) + Vertex AI Agent Engine",
        "why": "Native support for `SequentialAgent`, `ParallelAgent`, `LlmAgent`, MCP tools, A2A handoffs, local `adk web` trace UI, and 1-command managed deployment on Vertex AI Agent Engine.",
    },
    {
        "familiar": "OpenAI Assistants API / Responses API",
        "category": "Stateful Tool-Using Agents",
        "gcp": "Vertex AI Gemini API (`google-genai`) + Agent Engine Sessions",
        "why": "1M–2M token context window, native Tri-Modal Grounding (Google Maps + YouTube + Search), deterministic gVisor code execution, and VPC-SC data residency inside Rocket's GCP project.",
    },
    {
        "familiar": "Anthropic Claude Sonnet / Opus & Claude Code",
        "category": "Deep Reasoning & Agentic Coding",
        "gcp": "Vertex AI `gemini-4-argon` + Google Antigravity IDE + Model Garden",
        "why": "`gemini-4-argon` delivers frontier multi-document reasoning and coding with `SKILL.md` & parallel subagents (plus Claude models are also available directly on Vertex AI Model Garden under GCP billing/IAM).",
    },
    {
        "familiar": "Sierra AI / OpenAI Realtime Voice / Legacy IVR",
        "category": "Voice & Video Customer Concierge",
        "gcp": "Vertex AI `gemini-3.8-live` + GECX (`ces.cloud.google.com`) + `cxas-scrappy`",
        "why": "Native 24kHz audio + 24fps H.264 official video avatars (`AvatarConfig`), <200ms server VAD barge-in, automated PRD-to-Agent hill-climbing (`cxas-scrappy`), and zero per-resolution third-party markup.",
    },
    {
        "familiar": "Pinecone / Weaviate / Separate Vector DBs",
        "category": "Semantic & Multimodal Vector Search",
        "gcp": "BigQuery `VECTOR_SEARCH` (`COSINE` + RRF) + `gemini-embedding-001`",
        "why": "Keep 3072-D text vectors and 1408-D image vectors directly inside BigQuery alongside loan/listing tables—join SQL filters with vector similarity in <50ms with zero data movement.",
    },
    {
        "familiar": "Prophet / Custom ARIMA / PyTorch Forecasting",
        "category": "Time-Series Volume Forecasting",
        "gcp": "BigQuery ML `AI.FORECAST` (`TimesFM 2.0`)",
        "why": "Forecast refinance lock waves, buyer tour demand, and escrow cash outflows in a single Standard SQL query with 90% confidence bands—no model training or GPU cluster maintenance required.",
    },
]


def render_dynamic_glossary_tab_html(auth_token: str) -> str:
    """Renders a clean, scannable, zero-overflow Google Cloud Agent Platform & AI Glossary."""
    safe_token = _html.escape(str(auth_token or NEXTGEN_TOKEN))

    # Build Term Cards HTML & Sandbox Registry Map
    term_cards_html: List[str] = []
    sandbox_registry: Dict[str, Dict[str, Any]] = {}
    for idx, item in enumerate(GLOSSARY_TERMS, start=1):
        cat_attr = _html.escape(item["cat"])
        kw_attr = _html.escape(
            f"{item['term']} {item['summary']} {item['analogy']} {item['platform']} {item['cat']}".lower()
        )
        speech_text = (
            _re.sub(r"[*`]", "", f"{item['term']}. {item['summary']} {item['analogy']}")
            .replace("'", "\\'")
            .replace("\n", " ")
        )
        term_formatted = _fmt_inline_md(item["term"])
        summary_formatted = _fmt_inline_md(item["summary"])
        analogy_formatted = _fmt_inline_md(item["analogy"])
        platform_formatted = _fmt_inline_md(item["platform"])

        default_test_input = item.get(
            "test_input",
            f"Borrower in Royal Oak, MI ($460,000 purchase, 20% down, $148,000 qualifying income, $19,200 Schedule C depreciation add-back). Execute {item['term']} and verify compliance.",
        )
        sandbox_registry[item["id"]] = {
            "id": item["id"],
            "index": idx,
            "cat": item["cat"],
            "badge": item["badge"],
            "term": _re.sub(r"[*`]", "", item["term"]),
            "summary": _re.sub(r"[*`]", "", item["summary"]),
            "code": item["code"],
            "test_input": default_test_input,
            "presets": [
                "Standard Loan Audit: $460K purchase, 20% down, $148K W-2 + $19.2K Schedule C depreciation add-back",
                "High-DTI Stress Test: $720K jumbo home, 10% down, 6.25% rate, $450/mo HOA + student loan debt",
                "Rate-Shock Scenario: Simulate -100 bps Fed rate cut impact on refinance recapture & monthly PITI",
            ],
        }

        term_cards_html.append(f"""
        <article class="gl-concept-card" id="{_html.escape(item['id'])}" data-gl-cat="{cat_attr}" data-keywords="{kw_attr}">
          <div class="gl-concept-top">
            <span class="lg-badge {_html.escape(item['badge_cls'])}">{_html.escape(item['badge'])}</span>
            <button type="button" class="gl-card-flip-btn mono"
                    onclick="window.toggleSingleGlossaryCardCode(this)" title="Flip between Plain-English Analogy and Vertex AI / ADK Code">
              {gl_icon("flip", 13)}
              <span class="gl-flip-btn-lbl">Flip Card</span>
            </button>
          </div>

          <h4 class="gl-concept-title">{idx}. {term_formatted}</h4>
          <p class="gl-concept-one-liner">{summary_formatted}</p>

          <div class="gl-view-beginner">
            <div class="gl-concept-analogy-box">
              <div style="margin-bottom:8px;">
                <span class="gl-inline-lead">{gl_icon("lightbulb", 14)} Plain-English Analogy:</span>
                <span>{analogy_formatted}</span>
              </div>
              <div style="padding-top:8px;border-top:1px solid var(--glass-outer-stroke);">
                <span class="gl-inline-lead" style="color:var(--accent-secondary);">{gl_icon("cpu", 14)} On Google Cloud Agent Platform:</span>
                <span>{platform_formatted}</span>
              </div>
            </div>
          </div>

          <div class="gl-view-builder" style="display:none;">
            <pre class="gl-concept-builder-box">{_html.escape(item['code'])}</pre>
          </div>

          <div class="gl-concept-actions">
            <button type="button" class="lg-btn lg-btn-glass sm"
                    onclick="window.speakGlossaryText('{speech_text}', this)" title="Listen to 24kHz audio definition (click again to stop)">
              {gl_icon("listen", 14)}
              <span>Listen</span>
            </button>
            <button type="button" class="lg-btn lg-btn-primary sm"
                    onclick="window.openGlossarySandboxIde('{_html.escape(item['id'])}')" title="Open Live Sandbox Mini-IDE to modify code, reset, and test response behavior in real time">
              {gl_icon("play", 14)}
              <span>See Live in Studio</span>
            </button>
          </div>
        </article>
        """)

    # Build Translator Table Rows HTML
    translator_rows_html: List[str] = []
    for row in AGENT_PLATFORM_TRANSLATOR:
        translator_rows_html.append(f"""
        <tr>
          <td>
            <div style="font-weight:800;color:var(--text-primary);">{_fmt_inline_md(row['familiar'])}</div>
            <div class="mono" style="font-size:11px;color:var(--text-muted);margin-top:2px;">{_fmt_inline_md(row['category'])}</div>
          </td>
          <td>
            <div style="font-weight:800;color:var(--accent-secondary);">{_fmt_inline_md(row['gcp'])}</div>
          </td>
          <td style="color:var(--text-secondary);line-height:1.55;">
            {_fmt_inline_md(row['why'])}
          </td>
        </tr>
        """)

    return f"""
<link rel="stylesheet" href="/static/glossary_launchpad.css">

<div class="gl-launchpad-shell gl-launchpad-root" id="gl-launchpad-root" data-gl-depth="beginner" data-auth-token="{safe_token}">

  <!-- ========================================================================
       1. GLOSSARY HEADER, SEARCH, CATEGORY PILLS & DEPTH MODE TOGGLE
       ======================================================================== -->
  <section class="liquid-card gl-hero-card gl-hero-banner" id="gl-hero-banner">
    <div class="gl-hero-top-row">
      <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
        <span class="lg-badge lg-badge-crimson">GOOGLE CLOUD AGENT PLATFORM · AI GLOSSARY</span>
        <span class="lg-badge lg-badge-cobalt mono">VERTEX AI · ADK · AGENT ENGINE · MCP · A2A · BIGQUERY · GECX</span>
      </div>
      <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
        <div class="gl-depth-switcher gl-mode-toggle-group" role="group" aria-label="Glossary Explanation Depth">
          <button type="button" id="gl-mode-beginner" class="gl-mode-btn active" data-gl-depth-btn="beginner"
                  onclick="window.setGlossaryDepthMode('beginner')" aria-pressed="true">
            {gl_icon("book", 15)}
            <span>Plain-English Definitions &amp; Analogies</span>
          </button>
          <button type="button" id="gl-mode-builder" class="gl-mode-btn" data-gl-depth-btn="builder"
                  onclick="window.setGlossaryDepthMode('builder')" aria-pressed="false">
            {gl_icon("terminal", 15)}
            <span>Show All Vertex AI / ADK Code Snippets</span>
          </button>
        </div>
        <a href="{GLOSSARY_DOC_URL}" target="_blank" class="lg-btn lg-btn-glass sm" title="Open Printable 3-Tab Google Doc Companion">
          {gl_icon("doc_ext", 15)}
          <span>Printable Google Doc</span>
          {gl_icon("arrow_up_right", 13)}
        </a>
      </div>
    </div>

    <div>
      <h2 class="gl-hero-title">
        Google Cloud Agent Platform &amp; AI Glossary
      </h2>
      <p class="gl-hero-sub" style="margin-top:6px;">
        Clear, plain-English definitions, real-world mortgage &amp; real-estate analogies, and copy-paste <strong>Vertex AI / ADK / BigQuery</strong> code snippets for every concept, protocol, guardrail, and 2026 model we are testing on Google Cloud.
      </p>
    </div>

    <!-- Responsive 3-Box HTML Architecture Formula (100% Auto-Wrapping HTML Cards — Zero SVG Text Overflow!) -->
    <div class="gl-formula-grid" role="region" aria-label="Agent Platform Core Formula">
      <div class="gl-formula-box box-crimson">
        <div class="gl-formula-kicker mono">1 · THE BRAIN (VERTEX AI MODEL)</div>
        <div class="gl-formula-title">Reasons, Sees, Hears &amp; Plans</div>
        <div class="gl-formula-desc">
          <code class="lg-inline-code">gemini-4-argon</code> (Deep Reasoning), <code class="lg-inline-code">gemini-3.8-flash</code> (Fast Multimodal), <code class="lg-inline-code">gemini-3.1-flash-lite</code> (Subagents), &amp; <code class="lg-inline-code">gemini-3.8-live</code> (24kHz Voice / 24fps Video).
        </div>
      </div>

      <div class="gl-formula-operator mono" aria-hidden="true">+</div>

      <div class="gl-formula-box box-cobalt">
        <div class="gl-formula-kicker mono">2 · THE HANDS &amp; GUARDRAILS (AGENT HARNESS)</div>
        <div class="gl-formula-title">ADK, Tools, Grounding &amp; Sandbox</div>
        <div class="gl-formula-desc">
          <strong>Google ADK</strong> + <strong>MCP</strong> tools + <strong>A2A</strong> handoffs + <strong>Tri-Modal Grounding</strong> (Maps, YouTube, Search) + <strong>Python gVisor Sandbox</strong> + <strong>Model Armor</strong>.
        </div>
      </div>

      <div class="gl-formula-operator mono" aria-hidden="true">=</div>

      <div class="gl-formula-box box-emerald">
        <div class="gl-formula-kicker mono">3 · PRODUCTION AGENT PLATFORM</div>
        <div class="gl-formula-title">Autonomous Enterprise Execution</div>
        <div class="gl-formula-desc">
          Deployed on <strong>Vertex AI Agent Engine</strong>, <strong>Cloud Run</strong>, or <strong>GECX (`ces.cloud.google.com`)</strong> with session memory, Cloud Trace, and <strong>LLM-as-a-Judge</strong> evaluation.
        </div>
      </div>
    </div>

    <!-- Search & Category Filter Toolbar -->
    <div class="gl-toolbar-row" style="margin-top:4px;">
      <div class="gl-search-box">
        {gl_icon("search", 16)}
        <input type="text" id="gl-search-input"
               placeholder="Search glossary terms (e.g. 'ADK', 'Agent Engine', 'Harness', 'MCP', 'A2A', 'ALM', 'RAG', 'gVisor', 'TimesFM', 'Veo')…"
               oninput="window.searchGlossaryConcepts && window.searchGlossaryConcepts(this.value)">
      </div>
      <div class="gl-pill-row" role="tablist" aria-label="Filter Glossary by Category">
        <button type="button" class="gl-select-pill active" data-gl-cat="all" onclick="window.filterGlossaryConcepts('all')">All Terms ({len(GLOSSARY_TERMS)})</button>
        <button type="button" class="gl-select-pill" data-gl-cat="Mental Model" onclick="window.filterGlossaryConcepts('Mental Model')">1. Mental Model (4)</button>
        <button type="button" class="gl-select-pill" data-gl-cat="Agent Platform" onclick="window.filterGlossaryConcepts('Agent Platform')">2. Agent Platform &amp; ADK (6)</button>
        <button type="button" class="gl-select-pill" data-gl-cat="Grounding &amp; Tools" onclick="window.filterGlossaryConcepts('Grounding & Tools')">3. Grounding, RAG &amp; MCP (5)</button>
        <button type="button" class="gl-select-pill" data-gl-cat="Safety &amp; Eval" onclick="window.filterGlossaryConcepts('Safety & Eval')">4. Sandbox, Safety &amp; Eval (3)</button>
        <button type="button" class="gl-select-pill" data-gl-cat="2026 Models" onclick="window.filterGlossaryConcepts('2026 Models')">5. 2026 Vertex AI Models (2)</button>
      </div>
      <span id="gl-concepts-count" class="lg-chip lg-chip-mono">{len(GLOSSARY_TERMS)} Terms Shown</span>
    </div>
  </section>

  <!-- ========================================================================
       2. GLOSSARY CARDS GRID (CLEAN DICTIONARY ENTRIES)
       ======================================================================== -->
  <section class="liquid-card gl-section-card" id="gl-concepts-section">
    <div id="gl-concepts-grid">
      {"".join(term_cards_html)}
    </div>
  </section>

  <!-- ========================================================================
       3. INDUSTRY FRAMEWORK / TOOL -> GOOGLE CLOUD AGENT PLATFORM TRANSLATOR
       ======================================================================== -->
  <section class="liquid-card gl-section-card" id="gl-rosetta-section">
    <div class="gl-hero-top-row">
      <div>
        <span class="lg-badge lg-badge-amber">QUICK TRANSLATOR · FAMILIAR STACK → GOOGLE CLOUD AGENT PLATFORM</span>
        <div class="gl-module-title-row">
          {gl_well("layers", "well-amber", 18)}
          <h3 class="gl-wiz-headline" style="font-size:20px;">Familiar AI Tools &amp; Frameworks → Google Cloud Agent Platform Equivalent</h3>
        </div>
        <p class="gl-wiz-desc" style="margin-top:4px;">
          How common external AI libraries, APIs, and vector databases map directly onto the Google Cloud Vertex AI, ADK, BigQuery, and GECX services in our environment.
        </p>
      </div>
    </div>

    <div class="liquid-table-wrap" style="border:1px solid var(--glass-outer-stroke);border-radius:16px;overflow-x:auto;">
      <table class="liquid-table" style="width:100%;border-collapse:collapse;font-size:13px;">
        <thead>
          <tr>
            <th style="width:26%;">Familiar Tool / Framework</th>
            <th style="width:30%;">Google Cloud Agent Platform Equivalent</th>
            <th style="width:44%;">Why We Use It on Google Cloud</th>
          </tr>
        </thead>
        <tbody>
          {"".join(translator_rows_html)}
        </tbody>
      </table>
    </div>
  </section>

  <!-- ========================================================================
       4. LIVE SANDBOX MINI-IDE MODAL POP-UP WINDOW (`#gl-sandbox-ide-modal`)
       ======================================================================== -->
  <div id="gl-sandbox-ide-modal" class="gl-ide-backdrop" role="dialog" aria-modal="true" aria-labelledby="gl-ide-title" onclick="if(event.target===this)window.closeGlossarySandboxIde()">
    <div class="gl-ide-window">
      <!-- Top Mini-IDE Window Bar -->
      <div class="gl-ide-topbar">
        <div class="gl-ide-topbar-left">
          <div class="gl-ide-window-dots" aria-hidden="true">
            <span class="dot-red"></span>
            <span class="dot-amber"></span>
            <span class="dot-green"></span>
          </div>
          <div>
            <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
              <span id="gl-ide-badge" class="lg-badge lg-badge-crimson">LIVE VERTEX AI SANDBOX IDE</span>
              <span id="gl-ide-status-pill" class="lg-badge lg-badge-emerald mono">READY · INTERACTIVE</span>
            </div>
            <h3 id="gl-ide-title" class="gl-ide-title">1. Agent = Model (Brain) + Harness (Hands)</h3>
          </div>
        </div>

        <div class="gl-ide-topbar-controls">
          <label class="gl-ide-ctrl-label mono">
            <span>MODEL:</span>
            <select id="gl-ide-model" class="gl-ide-select mono">
              <option value="gemini-3.8-flash" selected>gemini-3.8-flash (Fast Default)</option>
              <option value="gemini-4-argon">gemini-4-argon (Deep Reasoning)</option>
              <option value="gemini-3.1-flash-lite">gemini-3.1-flash-lite (Subagent Lite)</option>
            </select>
          </label>

          <label class="gl-ide-ctrl-label mono" title="Adjust model temperature (0.0 = deterministic, 1.0 = creative)">
            <span>TEMP: <strong id="gl-ide-temp-val">0.20</strong></span>
            <input type="range" id="gl-ide-temp" min="0" max="1" step="0.05" value="0.20"
                   oninput="var el=document.getElementById('gl-ide-temp-val');if(el)el.textContent=Number(this.value).toFixed(2);">
          </label>

          <button type="button" id="gl-ide-reset-btn" class="lg-btn lg-btn-glass sm"
                  onclick="window.resetGlossarySandboxCode()" title="Reset code and test prompt back to original starter template">
            {gl_icon("reset", 14)}
            <span>Reset Code</span>
          </button>

          <button type="button" id="gl-ide-run-btn" class="lg-btn lg-btn-primary sm"
                  onclick="window.runGlossarySandboxCode()" title="Execute modified code &amp; test payload against live Vertex AI (Ctrl/Cmd + Enter)">
            {gl_icon("play", 14)}
            <span id="gl-ide-run-lbl">Run &amp; Send</span>
          </button>

          <button type="button" class="lg-btn lg-btn-glass sm"
                  onclick="window.closeGlossarySandboxIde()" title="Close Mini-IDE Sandbox (Esc)">
            {gl_icon("close", 15)}
          </button>
        </div>
      </div>

      <!-- Split 2-Pane IDE Body: Left = Editable Code & Payload | Right = Live Execution Output -->
      <div class="gl-ide-split">
        <!-- LEFT PANE: EDITABLE CODE & TEST INPUT -->
        <div class="gl-ide-pane gl-ide-pane-left">
          <div class="gl-ide-pane-hdr">
            <div style="display:flex;align-items:center;gap:8px;">
              {gl_icon("terminal", 14)}
              <span class="mono" style="font-weight:800;font-size:12px;">agent_sandbox.py · Editable Vertex AI / ADK Code</span>
            </div>
            <span id="gl-ide-modified-badge" class="mono" style="font-size:11px;color:#38BDF8;">Edit code, instruction, or thresholds below</span>
          </div>

          <div class="gl-ide-editor-wrap">
            <textarea id="gl-ide-code-editor" class="gl-ide-code-textarea mono" spellcheck="false"
                      aria-label="Editable Vertex AI and ADK Python Code"
                      oninput="window.onGlossaryCodeEdited && window.onGlossaryCodeEdited()"></textarea>
          </div>

          <div class="gl-ide-input-section">
            <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap;">
              <span class="mono" style="font-size:11px;font-weight:800;color:#94A3B8;">TEST INPUT PAYLOAD / PROMPT SENT TO AGENT:</span>
              <span class="mono" style="font-size:10.5px;color:#64748B;">Press Ctrl+Enter (or Cmd+Enter) to Run &amp; Send</span>
            </div>
            <textarea id="gl-ide-test-input" class="gl-ide-input-textarea" rows="2"
                      aria-label="Test Input Payload"></textarea>
            <div id="gl-ide-presets-row" class="gl-ide-presets-row"></div>
          </div>
        </div>

        <!-- RIGHT PANE: REAL-TIME EXECUTION TRACE & RESPONSE BEHAVIOR -->
        <div class="gl-ide-pane gl-ide-pane-right">
          <div class="gl-ide-pane-hdr">
            <div style="display:flex;align-items:center;gap:8px;">
              {gl_icon("cpu", 14)}
              <span class="mono" style="font-weight:800;font-size:12px;">Live Sandbox Response &amp; Execution Behavior</span>
            </div>
            <div style="display:flex;align-items:center;gap:6px;">
              <button type="button" id="gl-ide-listen-btn" class="gl-card-flip-btn mono"
                      onclick="window.speakGlossaryIdeOutput(this)" title="Listen to 24kHz audio of the sandbox response (click again to stop)">
                {gl_icon("listen", 13)}
                <span>Listen</span>
              </button>
              <button type="button" class="gl-card-flip-btn mono"
                      onclick="window.copyGlossaryIdeOutput(this)" title="Copy sandbox output">
                {gl_icon("copy", 13)}
                <span>Copy</span>
              </button>
            </div>
          </div>

          <!-- 3-Step Execution Trace -->
          <div id="gl-ide-trace-list" class="gl-ide-trace-list"></div>

          <!-- Live Model Output Console -->
          <pre id="gl-ide-output-console" class="gl-ide-output-console mono">Click "Run &amp; Send" to execute the code buffer on Vertex AI...</pre>
        </div>
      </div>
    </div>
  </div>

  <script>
    window.GLOSSARY_SANDBOX_REGISTRY = {json.dumps(sandbox_registry)};
  </script>

</div>
"""


def render_standalone_glossary_page_html(auth_token: str) -> str:
    """Renders the complete standalone HTML page (`<!DOCTYPE html>...`) for `GET /glossary`."""
    safe_token = _html.escape(str(auth_token or NEXTGEN_TOKEN))
    inner_glossary_html = render_dynamic_glossary_tab_html(safe_token)

    return f"""<!DOCTYPE html>
<html lang="en" data-liquid-version="v1">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Google Cloud Agent Platform &amp; AI Glossary | Rocket × Google Cloud</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/static/glossary_launchpad.css">
  <style>
    :root,
    html[data-liquid-version="v1"] {{
      --bg-canvas: linear-gradient(155deg, #EEF3FC 0%, #E5ECF9 48%, #F3EEF8 100%);
      --glass-surface: rgba(255, 255, 255, 0.72);
      --glass-surface-strong: rgba(255, 255, 255, 0.88);
      --glass-surface-subtle: rgba(255, 255, 255, 0.52);
      --glass-border-light: rgba(255, 255, 255, 0.95);
      --glass-outer-stroke: rgba(15, 23, 42, 0.08);
      --glass-shadow: 0 22px 48px -12px rgba(15, 23, 42, 0.09), 0 4px 16px -2px rgba(15, 23, 42, 0.04);
      --glass-inner-glow: inset 0 1.5px 0 0 rgba(255, 255, 255, 0.95), inset 0 -1px 0 0 rgba(255, 255, 255, 0.45);
      --text-primary: #0B0F19;
      --text-secondary: #334155;
      --text-muted: #64748B;
      --accent-primary: #D81E28;
      --accent-secondary: #0066CC;
      --accent-tertiary: #059669;
      --radius-card: 26px;
      --font-display: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    html[data-liquid-version="v2"] {{
      --bg-canvas: radial-gradient(circle at 18% 12%, #190D1C 0%, #070A12 52%, #05070D 100%);
      --glass-surface: rgba(17, 23, 38, 0.72);
      --glass-surface-strong: rgba(22, 30, 48, 0.88);
      --glass-surface-subtle: rgba(15, 20, 34, 0.56);
      --glass-border-light: rgba(255, 255, 255, 0.18);
      --glass-outer-stroke: rgba(56, 189, 248, 0.16);
      --glass-shadow: 0 28px 60px -12px rgba(0, 0, 0, 0.72), 0 0 32px -8px rgba(216, 30, 40, 0.18);
      --glass-inner-glow: inset 0 1px 0 0 rgba(255, 255, 255, 0.22), inset 0 -1px 0 0 rgba(56, 189, 248, 0.12);
      --text-primary: #F8FAFC;
      --text-secondary: #CBD5E1;
      --text-muted: #94A3B8;
      --accent-primary: #FF3B47;
      --accent-secondary: #38BDF8;
      --accent-tertiary: #10B981;
      --radius-card: 22px;
      --font-display: 'Plus Jakarta Sans', -apple-system, sans-serif;
    }}
    html[data-liquid-version="v3"] {{
      --bg-canvas: linear-gradient(160deg, #1E1C1A 0%, #141416 55%, #1C1917 100%);
      --glass-surface: rgba(42, 40, 38, 0.68);
      --glass-surface-strong: rgba(54, 51, 48, 0.86);
      --glass-surface-subtle: rgba(34, 32, 30, 0.55);
      --glass-border-light: rgba(245, 238, 228, 0.26);
      --glass-outer-stroke: rgba(214, 201, 184, 0.16);
      --glass-shadow: 0 32px 64px -16px rgba(0, 0, 0, 0.75);
      --glass-inner-glow: inset 0 1.5px 0 0 rgba(255, 248, 237, 0.30);
      --text-primary: #FAF7F2;
      --text-secondary: #D6D0C4;
      --text-muted: #A8A093;
      --accent-primary: #F43F5E;
      --accent-secondary: #F59E0B;
      --accent-tertiary: #34D399;
      --radius-card: 28px;
      --font-display: 'Plus Jakarta Sans', -apple-system, sans-serif;
    }}
    html[data-liquid-version="v4"] {{
      --bg-canvas: linear-gradient(180deg, #FAF8F5 0%, #F2EFE9 100%);
      --glass-surface: rgba(255, 255, 255, 0.84);
      --glass-surface-strong: rgba(255, 255, 255, 0.94);
      --glass-surface-subtle: rgba(247, 244, 238, 0.72);
      --glass-border-light: rgba(255, 255, 255, 0.98);
      --glass-outer-stroke: rgba(28, 25, 23, 0.09);
      --glass-shadow: 0 16px 36px -10px rgba(28, 25, 23, 0.06);
      --glass-inner-glow: inset 0 1px 0 0 rgba(255, 255, 255, 1);
      --text-primary: #1C1917;
      --text-secondary: #44403C;
      --text-muted: #78716C;
      --accent-primary: #B91C1C;
      --accent-secondary: #1D4ED8;
      --accent-tertiary: #047857;
      --radius-card: 16px;
      --font-display: 'Instrument Serif', Georgia, serif;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background: var(--bg-canvas);
      background-attachment: fixed;
      color: var(--text-primary);
      min-height: 100vh;
      line-height: 1.55;
      -webkit-font-smoothing: antialiased;
    }}
    .mono {{ font-family: 'JetBrains Mono', monospace; }}
    .liquid-card {{
      background: var(--glass-surface);
      backdrop-filter: blur(28px) saturate(180%);
      -webkit-backdrop-filter: blur(28px) saturate(180%);
      border: 1px solid var(--glass-border-light);
      outline: 1px solid var(--glass-outer-stroke);
      border-radius: var(--radius-card);
      box-shadow: var(--glass-shadow), var(--glass-inner-glow);
    }}
    .spatial-header-wrap {{
      position: sticky;
      top: 14px;
      z-index: 90;
      max-width: 1420px;
      margin: 14px auto 0;
      padding: 0 20px;
    }}
    .spatial-ornament-bar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 10px 16px;
      border-radius: 999px;
      background: var(--glass-surface-strong);
      backdrop-filter: blur(36px) saturate(190%);
      border: 1px solid var(--glass-border-light);
      outline: 1px solid var(--glass-outer-stroke);
      box-shadow: var(--glass-shadow), var(--glass-inner-glow);
      flex-wrap: wrap;
    }}
    .portal-main {{
      max-width: 1420px;
      margin: 22px auto 80px;
      padding: 0 20px;
    }}
    .lg-badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 11px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      font-family: 'JetBrains Mono', monospace;
    }}
    .lg-badge-crimson {{ background: rgba(216, 30, 40, 0.12); color: var(--accent-primary); border: 1px solid rgba(216, 30, 40, 0.28); }}
    .lg-badge-cobalt  {{ background: rgba(0, 102, 204, 0.12); color: var(--accent-secondary); border: 1px solid rgba(0, 102, 204, 0.28); }}
    .lg-badge-emerald {{ background: rgba(5, 150, 105, 0.12); color: var(--accent-tertiary); border: 1px solid rgba(5, 150, 105, 0.28); }}
    .lg-badge-amber   {{ background: rgba(217, 119, 6, 0.14); color: #D97706; border: 1px solid rgba(217, 119, 6, 0.30); }}
    .lg-badge-purple  {{ background: rgba(124, 58, 237, 0.12); color: #7C3AED; border: 1px solid rgba(124, 58, 237, 0.28); }}
    .lg-chip {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 4px 10px;
      border-radius: 9px;
      font-size: 11.5px;
      font-weight: 600;
      background: var(--glass-surface-subtle);
      border: 1px solid var(--glass-outer-stroke);
      color: var(--text-secondary);
    }}
    .lg-chip-mono {{ font-family: 'JetBrains Mono', monospace; font-size: 11px; }}
    .lg-inline-code {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.9em;
      padding: 2px 6px;
      border-radius: 6px;
      background: var(--glass-surface-subtle);
      border: 1px solid var(--glass-outer-stroke);
      color: var(--accent-secondary);
    }}
    .lg-btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 7px;
      padding: 10px 16px;
      border-radius: 14px;
      font-size: 13px;
      font-weight: 700;
      text-decoration: none;
      cursor: pointer;
      border: 1px solid transparent;
      transition: all 0.18s ease;
      font-family: inherit;
    }}
    .lg-btn.sm {{ padding: 7px 12px; font-size: 12px; border-radius: 11px; }}
    .lg-btn-primary {{
      background: linear-gradient(180deg, #E6222E 0%, #C41620 100%);
      color: #FFFFFF;
      box-shadow: 0 8px 20px -4px rgba(216, 30, 40, 0.45);
    }}
    .lg-btn-glass {{
      background: var(--glass-surface-strong);
      color: var(--text-primary);
      border: 1px solid var(--glass-outer-stroke);
    }}
    table.liquid-table th {{
      padding: 14px 16px;
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      font-family: 'JetBrains Mono', monospace;
      color: var(--text-muted);
      border-bottom: 1px solid var(--glass-outer-stroke);
      background: var(--glass-surface-subtle);
      text-align: left;
    }}
    table.liquid-table td {{
      padding: 14px 16px;
      border-bottom: 1px solid var(--glass-outer-stroke);
      vertical-align: top;
    }}
  </style>
</head>
<body>
  <header class="spatial-header-wrap">
    <div class="spatial-ornament-bar">
      <div style="display:flex;align-items:center;gap:12px;">
        <a href="/?auth_token={safe_token}" class="lg-btn lg-btn-glass sm" title="Return to Rocket × Google Cloud Unified Portal">
          {gl_icon("arrow_left", 15)}
          <span>Back to Unified Portal</span>
        </a>
        <div>
          <div style="font-size:15px;font-weight:800;letter-spacing:-0.02em;">Rocket × Google Cloud — Agent Platform &amp; AI Glossary</div>
          <div class="mono" style="font-size:10.5px;color:var(--text-muted);">VERTEX AI · ADK · AGENT ENGINE · MCP · A2A · BIGQUERY · GECX</div>
        </div>
      </div>
      <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
        <button type="button" class="gl-select-pill active" onclick="document.documentElement.setAttribute('data-liquid-version','v1')">V1 · Prism</button>
        <button type="button" class="gl-select-pill" onclick="document.documentElement.setAttribute('data-liquid-version','v2')">V2 · Black Mirror</button>
        <button type="button" class="gl-select-pill" onclick="document.documentElement.setAttribute('data-liquid-version','v3')">V3 · Titanium 3D</button>
        <button type="button" class="gl-select-pill" onclick="document.documentElement.setAttribute('data-liquid-version','v4')">V4 · Stillness</button>
      </div>
    </div>
  </header>

  <main class="portal-main">
    {inner_glossary_html}
  </main>

  <script>
    window.PORTAL_AUTH_TOKEN = {json.dumps(auth_token or NEXTGEN_TOKEN)};
  </script>
  <link rel="stylesheet" href="/static/support_overlay.css">
  <script src="/static/glossary_launchpad.js"></script>
  <script src="/static/support_overlay.js"></script>
  <script src="/static/portal_telemetry.js"></script>
</body>
</html>
"""
