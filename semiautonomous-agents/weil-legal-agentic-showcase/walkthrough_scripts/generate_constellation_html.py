import os
from pathlib import Path

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Weil AI Constellation — Interactive 3D Architecture Universe</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/tween.js/18.6.4/tween.umd.js"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    body {
      margin: 0;
      overflow: hidden;
      background-color: #030712;
      font-family: 'Plus Jakarta Sans', sans-serif;
      user-select: none;
    }
    .font-mono {
      font-family: 'JetBrains Mono', monospace;
    }
    /* Glassmorphic Cards */
    .glass-card {
      background: rgba(15, 23, 42, 0.78);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid rgba(255, 255, 255, 0.12);
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
    }
    .glass-card-glow {
      box-shadow: 0 0 30px rgba(59, 130, 246, 0.2), inset 0 0 20px rgba(255, 255, 255, 0.05);
    }
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
      width: 6px;
    }
    ::-webkit-scrollbar-track {
      background: rgba(15, 23, 42, 0.6);
    }
    ::-webkit-scrollbar-thumb {
      background: rgba(71, 85, 105, 0.6);
      border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: rgba(100, 116, 139, 0.8);
    }
    .node-label {
      position: absolute;
      transform: translate(-50%, -100%);
      pointer-events: auto;
      white-space: nowrap;
      transition: opacity 0.4s ease, filter 0.4s ease, transform 0.2s ease;
      cursor: pointer;
    }
    .node-label.dimmed {
      opacity: 0.18 !important;
      filter: grayscale(85%) brightness(0.65);
      pointer-events: none;
    }
    .moon-label {
      position: absolute;
      transform: translate(-50%, -50%);
      pointer-events: auto;
      white-space: nowrap;
      transition: opacity 0.3s ease, transform 0.2s ease, background-color 0.15s ease;
      cursor: pointer;
    }
    .moon-label:hover {
      transform: translate(-50%, -50%) scale(1.08);
      border-color: #60a5fa !important;
      background-color: rgba(30, 58, 138, 0.95) !important;
      box-shadow: 0 0 15px rgba(96, 165, 250, 0.5);
    }
  </style>
</head>
<body class="text-slate-100 antialiased">

  <!-- 3D WebGL Canvas Container -->
  <div id="canvas-container" class="absolute inset-0 w-full h-full cursor-grab active:cursor-grabbing"></div>

  <!-- HTML Labels Overlay -->
  <div id="labels-container" class="absolute inset-0 pointer-events-none overflow-hidden"></div>

  <!-- Top Executive Header -->
  <header class="absolute top-0 left-0 right-0 p-6 flex justify-between items-center pointer-events-none z-20">
    <div class="flex items-center gap-4 pointer-events-auto">
      <div class="w-2.5 h-9 bg-gradient-to-b from-blue-500 via-indigo-500 to-amber-500 rounded-full shadow-lg shadow-blue-500/30"></div>
      <div>
        <div class="flex items-center gap-2">
          <span class="text-xs font-mono font-bold tracking-widest text-amber-400 uppercase">WEIL, GOTSHAL & MANGES</span>
          <span class="text-xs text-slate-500 font-mono">/</span>
          <span class="text-xs text-slate-400 font-mono">Google Cloud Architecture Universe</span>
        </div>
        <h1 class="text-lg font-bold tracking-tight text-white flex items-center gap-2">
          3D Enterprise Agentic Constellation
          <span class="text-[10px] font-mono font-medium px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/30">
            gemini-3.8-flash
          </span>
        </h1>
      </div>
    </div>

    <!-- Category Filter Controls -->
    <div class="flex items-center gap-1.5 glass-card p-1.5 rounded-2xl pointer-events-auto shadow-xl">
      <button onclick="filterCategory('all')" id="filter-all" class="filter-btn px-3 py-1 text-xs rounded-xl bg-blue-600 text-white font-medium transition">All Products</button>
      <button onclick="filterCategory('framework')" id="filter-framework" class="filter-btn px-3 py-1 text-xs rounded-xl text-slate-400 hover:text-white transition">Frameworks</button>
      <button onclick="filterCategory('protocol')" id="filter-protocol" class="filter-btn px-3 py-1 text-xs rounded-xl text-slate-400 hover:text-white transition">Protocols (MCP)</button>
      <button onclick="filterCategory('runtime')" id="filter-runtime" class="filter-btn px-3 py-1 text-xs rounded-xl text-slate-400 hover:text-white transition">Agent Runtime</button>
      <button onclick="filterCategory('governance')" id="filter-governance" class="filter-btn px-3 py-1 text-xs rounded-xl text-slate-400 hover:text-white transition">Governance & Trace</button>
    </div>

    <!-- Right Quick Actions -->
    <div class="flex items-center gap-2 pointer-events-auto">
      <!-- Orbit Speed / Pause Toggle -->
      <button onclick="toggleOrbitMovement()" id="orbit-toggle-btn" class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl glass-card hover:bg-slate-800 text-slate-300 hover:text-white text-xs font-mono transition cursor-pointer" title="Pause or Slow Down Moons Motion">
        <span id="orbit-toggle-icon">⏸</span>
        <span id="orbit-toggle-text">Freeze Motion</span>
      </button>

      <button onclick="toggleGuidedTour()" id="tour-btn" class="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-xs shadow-lg shadow-amber-500/20 transition cursor-pointer">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
        <span>Start Executive Tour</span>
      </button>
      <button onclick="resetCamera()" class="p-2 rounded-xl glass-card hover:bg-slate-800 text-slate-300 hover:text-white transition cursor-pointer" title="Reset Camera View">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
      </button>
    </div>
  </header>

  <!-- Left Quick Navigation Drawer (Collapsible) -->
  <aside class="absolute left-6 top-24 bottom-12 w-64 glass-card rounded-2xl p-3.5 flex flex-col z-10 pointer-events-auto border border-slate-700/50">
    <div class="flex items-center justify-between pb-2 mb-2 border-b border-slate-800">
      <span class="text-[11px] font-mono uppercase tracking-wider text-slate-400 font-bold">Universe Directory</span>
      <span class="text-[10px] font-mono text-slate-500" id="node-count">10 Nodes</span>
    </div>
    <div class="flex-1 overflow-y-auto space-y-1 pr-1" id="nodes-list">
      <!-- Injected by JavaScript -->
    </div>
    <div class="mt-2 pt-2 border-t border-slate-800 text-[10px] text-slate-500 font-mono flex flex-col gap-1">
      <div class="flex justify-between">
        <span>Orbit: Click+Drag</span>
        <span>Zoom: Scroll</span>
      </div>
      <div class="text-blue-400/90 text-[10px] flex items-center gap-1">
        <span>💡 Click Google ADK to reveal Moons</span>
      </div>
    </div>
  </aside>

  <!-- Right Inspector Drawer (Slides out when a node/moon is clicked) -->
  <div id="inspector-drawer" class="absolute right-0 top-0 bottom-0 w-[490px] glass-card glass-card-glow transform translate-x-full transition-transform duration-300 ease-out z-30 p-8 flex flex-col pointer-events-auto border-l border-slate-700/80">
    <div class="flex items-center justify-between pb-4 border-b border-slate-800">
      <div class="flex items-center gap-2.5">
        <span id="inspect-badge" class="px-2.5 py-0.5 rounded-full text-[11px] font-mono font-bold tracking-wide uppercase">
          Category
        </span>
        <span id="inspect-env" class="text-xs font-mono text-slate-400">
          vtxdemos / global
        </span>
      </div>
      <button onclick="closeInspector()" class="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition cursor-pointer">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
      </button>
    </div>

    <div class="flex-1 overflow-y-auto py-6 space-y-6 pr-2">
      <!-- Title & Headline -->
      <div>
        <div class="flex items-center gap-2 mb-1">
          <span id="inspect-icon" class="text-lg">🪐</span>
          <span id="inspect-parent" class="text-[11px] font-mono text-slate-400">Google Cloud Architecture</span>
        </div>
        <h2 id="inspect-title" class="text-2xl font-bold text-white tracking-tight leading-tight">Product Name</h2>
        <p id="inspect-subtitle" class="text-xs font-mono text-blue-400 mt-1">Product Subtitle / Architecture Role</p>
      </div>

      <!-- Description / Core Concept -->
      <div class="space-y-2">
        <h3 class="text-xs font-mono uppercase tracking-wider text-slate-400 font-bold">1. Enterprise Concept</h3>
        <p id="inspect-description" class="text-sm text-slate-300 leading-relaxed">
          Product description and functional explanation.
        </p>
      </div>

      <!-- Why It Matters to Weil -->
      <div class="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 space-y-1.5">
        <div class="flex items-center gap-2 text-amber-400 text-xs font-bold font-mono">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          <span>Why This Matters to Weil</span>
        </div>
        <p id="inspect-why-matters" class="text-xs text-amber-200/90 leading-relaxed">
          Architectural justification for BigLaw governance, risk mitigation, and client confidentiality.
        </p>
      </div>

      <!-- Production Code Snippet -->
      <div class="space-y-2">
        <div class="flex items-center justify-between">
          <h3 class="text-xs font-mono uppercase tracking-wider text-slate-400 font-bold">2. Production Code / Implementation</h3>
          <button onclick="copySnippet()" class="text-xs font-mono text-blue-400 hover:text-blue-300 flex items-center gap-1 cursor-pointer">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"></path></svg>
            <span id="copy-text">Copy Code</span>
          </button>
        </div>
        <div class="relative rounded-xl overflow-hidden bg-slate-950 border border-slate-800">
          <pre class="p-4 text-xs font-mono text-emerald-400 overflow-x-auto leading-relaxed max-h-64"><code id="inspect-code"># Code snippet</code></pre>
        </div>
      </div>

      <!-- Sub-Moons Quick Navigation (Visible when on Google ADK Planet) -->
      <div id="moons-quicknav" class="hidden space-y-2 p-3.5 rounded-xl bg-blue-950/40 border border-blue-800/40">
        <div class="text-[11px] font-mono text-blue-300 font-bold uppercase tracking-wider flex items-center gap-1.5">
          <span>🌙 Orbiting ADK Element Moons:</span>
        </div>
        <div class="grid grid-cols-1 gap-1.5" id="moons-button-list">
          <!-- Injected dynamically -->
        </div>
      </div>

      <!-- Back to ADK Planet Button (Visible when on a Moon) -->
      <div id="back-to-planet" class="hidden pt-1">
        <button onclick="focusNode('google_adk')" class="w-full py-2.5 px-4 rounded-xl bg-blue-600/30 hover:bg-blue-600/50 border border-blue-500/40 text-xs font-mono text-blue-200 flex items-center justify-center gap-2 transition cursor-pointer">
          <span>⬅ Back to Google ADK Planet</span>
        </button>
      </div>

      <!-- GCP Console Quick Link -->
      <div class="pt-2">
        <a id="inspect-link" href="#" target="_blank" class="flex items-center justify-between p-3 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-xs text-slate-200 transition">
          <div class="flex items-center gap-2">
            <svg class="w-4 h-4 text-blue-400" viewBox="0 0 24 24" fill="currentColor"><path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM17 13l-5 5-5-5h3V9h4v4h3z"/></svg>
            <span id="inspect-link-label">Open in Google Cloud Console</span>
          </div>
          <svg class="w-3.5 h-3.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
        </a>
      </div>
    </div>
  </div>

  <!-- Bottom Telemetry Bar -->
  <footer class="absolute bottom-4 left-6 right-6 flex items-center justify-between pointer-events-none z-20 text-xs font-mono text-slate-400">
    <div class="glass-card px-4 py-2 rounded-xl flex items-center gap-3 pointer-events-auto border border-slate-800">
      <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
      <span>VPC-SC Air-Gap: ACTIVE</span>
      <span class="text-slate-600">|</span>
      <span>GCP Project: <strong class="text-white">vtxdemos</strong></span>
      <span class="text-slate-600">|</span>
      <span>Foundation: <strong class="text-amber-400">gemini-3.8-flash</strong></span>
    </div>

    <div class="glass-card px-4 py-2 rounded-xl pointer-events-auto border border-slate-800 flex items-center gap-2">
      <span class="text-slate-400">Weil Executive Briefing Center</span>
      <span class="text-slate-600">•</span>
      <span class="text-slate-400">September 9, 2026</span>
    </div>
  </footer>

  <!-- CONSTELLATION 3D LOGIC, DATASET & ORBITING MOONS -->
  <script>
    // -------------------------------------------------------------------------
    // 1. Constellation Nodes Dataset (10 Architectural Core Products)
    // -------------------------------------------------------------------------
    const CONSTELLATION_NODES = [
      {
        id: "gemini_foundation",
        name: "Gemini 3.8 Flash Foundation",
        subtitle: "Multimodal Foundation & High-Fidelity Reasoning Engine",
        category: "framework",
        categoryName: "Foundation Model",
        color: "#f59e0b", // Gold
        position: [0, 0, 0],
        size: 2.8,
        description: "Google's flagship lightweight reasoning model delivering 1M+ token context windows, sub-second reasoning latency, native multimodal processing, and deterministic function calling.",
        whyMatters: "Enables Weil to ingest full 600-page Credit Agreements and complex merger filings in a single context window without lossy chunking, while ensuring cost-efficient token inference.",
        code: `from google import genai
from google.genai import types

client = genai.Client(vertexai=True, project="vtxdemos", location="global")

response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents="Synthesize CFIUS national security exposure for autonomous robotics acquisition.",
    config=types.GenerateContentConfig(
        temperature=0.2,
        system_instruction="You are the Weil Senior Legal AI Intelligence Partner."
    )
)
print(response.text)`,
        consoleLink: "https://console.cloud.google.com/vertex-ai?project=vtxdemos",
        consoleLabel: "Vertex AI Model Garden (vtxdemos)"
      },
      {
        id: "google_adk",
        name: "Google ADK (Agent Development Kit)",
        subtitle: "Pythonic Multi-Agent Orchestration & Lifecycle Framework",
        category: "framework",
        categoryName: "Agent Framework",
        color: "#3b82f6", // Blue
        position: [-14, 7, 6],
        size: 2.2,
        description: "The official Google open-source framework for building production agents. Provides structured Agent abstractions, FunctionTool decorators, stateful memory sessions, and pre/post-invocation lifecycle callbacks.",
        whyMatters: "Decouples business logic from model vendors. ADK allows Weil to define specialized sub-agents (Tax, Antitrust, Ethics) that operate collaboratively rather than relying on one fragile mega-prompt.",
        code: `from google.adk.agents import Agent
from google.adk.tools import FunctionTool

def check_conflicts(matter_name: str) -> dict:
    \"\"\"Checks Weil ethical wall clearance.\"\"\"
    return {"status": "CLEARED", "matter_id": "MATTER-2026-88"}

conflict_tool = FunctionTool(func=check_conflicts)

lead_agent = Agent(
    name="weil_lead_agent",
    model="gemini-3.8-flash",
    instruction="Run intake and verify ethical wall clearance.",
    tools=[conflict_tool]
)`,
        consoleLink: "https://adk.dev",
        consoleLabel: "Google ADK Official Documentation"
      },
      {
        id: "gemini_python_sdk",
        name: "Gemini Python SDK (google-genai)",
        subtitle: "Unified Direct Python SDK for Vertex AI",
        category: "framework",
        categoryName: "Client SDK",
        color: "#06b6d4", // Cyan
        position: [-9, -8, 10],
        size: 1.8,
        description: "The unified Python SDK (`from google import genai`) replacing legacy libraries. Provides zero-friction transition between Vertex AI enterprise endpoints and Gemini developer environments.",
        whyMatters: "Provides high-throughput asynchronous token streaming (`generate_content_stream`), typed Pydantic structured output validation, and native GCP Application Default Credentials (ADC) authentication.",
        code: `import asyncio
from google import genai

async def stream_legal_opinion(deal_summary: str):
    client = genai.Client(vertexai=True, project="vtxdemos", location="global")
    
    stream = await client.aio.models.generate_content_stream(
        model="gemini-3.8-flash",
        contents=f"Draft closing opinion clause: {deal_summary}"
    )
    async for chunk in stream:
        print(chunk.text, end="", flush=True)

asyncio.run(stream_legal_opinion("Nexus / Zephyr $2.3B Tech Merger"))`,
        consoleLink: "https://cloud.google.com/vertex-ai/docs/reference/rest",
        consoleLabel: "Google Cloud Python SDK Reference"
      },
      {
        id: "mcp_protocol",
        name: "Model Context Protocol (MCP)",
        subtitle: "Open Standard for Enterprise Tool & Data Connectivity",
        category: "protocol",
        categoryName: "Open Protocol",
        color: "#10b981", // Emerald
        position: [12, 9, -5],
        size: 2.1,
        description: "An open protocol created to standardize how AI agents connect to enterprise data sources (BigQuery, SharePoint, iManage, Jira). Separates tool execution from prompt context via JSON-RPC.",
        whyMatters: "Prevents vendor lock-in. Weil can build one BigQuery MCP server and plug it into Google ADK, Claude Code, or any internal legal workflow without rewriting integration code.",
        code: `from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weil-BigQuery-Precedents")

@mcp.tool()
def query_bigquery_deal_benchmarks(sector: str, min_deal_size_m: float) -> list[dict]:
    \"\"\"Query BigQuery for precedent reverse break-up fees and deal covenants.\"\"\"
    # Executes BigQuery SQL with row-level matter security
    return [
        {"deal_id": "DEAL-2025-104", "fee_pct": 4.5, "covenant": "Reasonable Best Efforts"}
    ]

if __name__ == "__main__":
    mcp.run()`,
        consoleLink: "https://modelcontextprotocol.io",
        consoleLabel: "Model Context Protocol (MCP) Specification"
      },
      {
        id: "agent_gateway",
        name: "Agent Gateway & Registry",
        subtitle: "Centralized Enterprise Governance & Tool Discovery Proxy",
        category: "protocol",
        categoryName: "GCP Gateway",
        color: "#14b8a6", // Teal
        position: [15, -5, 3],
        size: 2.0,
        description: "A managed Google Cloud gateway that acts as a secure reverse proxy for all agent-to-tool (MCP) and client-to-agent communications. Enforces IAM, rate limits, and audit logging at the gateway boundary.",
        whyMatters: "Individual agents never connect directly to sensitive document repositories. All traffic traverses the Agent Gateway with centralized DLP inspection, blocking data leakage before it happens.",
        code: `# GCP Agent Gateway Configuration (us-central1)
# Gateway: projects/254356041555/locations/us-central1/agentGateways/reasoning-engine-gateway

protocols:
  - "MCP"
governedAccessPath: "AGENT_TO_ANYWHERE"
registry: "//agentregistry.googleapis.com/projects/vtxdemos/locations/us-central1"
registeredServices:
  - "sharepoint-mcp"       # Weil Matter Records
  - "ms365-outlook-custom" # Client Communications
  - "jira-mcp-custom"      # Deal Milestones`,
        consoleLink: "https://console.cloud.google.com/vertex-ai?project=vtxdemos",
        consoleLabel: "Agent Gateway Registry in vtxdemos"
      },
      {
        id: "agent_runtime",
        name: "Vertex AI Agent Runtime",
        subtitle: "Managed Serverless MicroVM Execution for Stateful Python Agents",
        category: "runtime",
        categoryName: "Agent Runtime",
        color: "#8b5cf6", // Violet
        position: [0, 15, -8],
        size: 2.4,
        description: "Google's purpose-built, fully-managed serverless hosting environment for Python agents (Reasoning Engines). Handles containerization, auto-scaling, persistent session state, and VPC network attachments.",
        whyMatters: "Zero infrastructure burden for Weil's DevOps. Deploys Python ADK classes directly into Google Cloud with enterprise SLA, automatic cold-start optimization, and managed security patching.",
        code: `import vertexai
from vertexai.preview import reasoning_engines

vertexai.init(project="vtxdemos", location="us-central1", staging_bucket="gs://vtxdemos-agent-staging")

remote_app = reasoning_engines.ReasoningEngine.create(
    WeilManagedLegalEngine(model="gemini-3.8-flash"),
    requirements=["google-adk>=0.1.0", "google-genai>=0.1.1", "mcp>=1.0.0"],
    display_name="Weil_Legal_ADK_Engine_v1",
    description="Autonomous M&A intelligence engine hosted in Agent Runtime."
)
print(f"Live Endpoint: {remote_app.resource_name}")`,
        consoleLink: "https://console.cloud.google.com/vertex-ai/reasoning-engines?project=vtxdemos",
        consoleLabel: "Reasoning Engines in Google Cloud Console"
      },
      {
        id: "antigravity_sandbox",
        name: "Antigravity Autonomous Sandbox",
        subtitle: "Air-Gapped Self-Healing Execution & Error Remediation",
        category: "runtime",
        categoryName: "Autonomous Sandbox",
        color: "#d946ef", // Fuchsia
        position: [-16, 2, -10],
        size: 1.9,
        description: "An isolated runtime sandbox providing autonomous execution, tool validation, and real-time self-healing. When a tool or SQL query fails, Antigravity synthesizes the traceback and auto-remediates the environment.",
        whyMatters: "Prevents pipeline crashes during high-stakes partner deal sessions. If an external API or database changes schemas, Antigravity diagnoses the failure and applies a runtime patch seamlessly.",
        code: `# Antigravity Self-Healing Event Hook
async def on_tool_exception(exc: Exception, context: AgentContext):
    diagnostic = await antigravity_engine.diagnose(
        traceback=exc,
        sandbox_id=context.sandbox_id
    )
    if diagnostic.auto_remediable:
        patch = await diagnostic.generate_patch()
        await antigravity_engine.apply_in_sandbox(patch)
        return await context.retry_active_step()
    raise FatalAgentException(diagnostic.root_cause)`,
        consoleLink: "http://localhost:8000/api/health",
        consoleLabel: "Antigravity Sandbox Engine (Local Daemon)"
      },
      {
        id: "agent_identity",
        name: "Agent Identity & Zero-Trust",
        subtitle: "SPIFFE x509, Ephemeral Tokens & Workload Identity Federation",
        category: "governance",
        categoryName: "Security & IAM",
        color: "#eab308", // Amber
        position: [-7, 13, 9],
        size: 1.9,
        description: "Zero-Trust cryptographic security for AI agents. Replaces static API keys with short-lived SPIFFE x509 certificates, DPoP (Demonstrating Proof-of-Possession) tokens, and IAM conditions scoped to active matter IDs.",
        whyMatters: "Guarantees that an agent working on 'Matter Alpha' has zero mathematical ability to query documents belonging to 'Matter Beta'. Access tokens expire every 15 minutes and are cryptographically bound.",
        code: `# Workload Identity & Scoped Token Exchange
# IAM Condition: request.auth.claims['matter_id'] == resource.labels['matter_id']

from google.auth import identity_pool

credentials = identity_pool.Credentials.from_info({
    "type": "external_account",
    "audience": "//iam.googleapis.com/projects/254356041555/locations/global/workloadIdentityPools/weil-agents",
    "subject_token_type": "urn:ietf:params:oauth:token-type:jwt",
    "token_url": "https://sts.googleapis.com/v1/token"
})
# Ephemeral scope: read-only BigQuery deal precedent access for 15 minutes`,
        consoleLink: "https://console.cloud.google.com/iam-admin/iam?project=vtxdemos",
        consoleLabel: "IAM & Workload Identity in vtxdemos"
      },
      {
        id: "deterministic_interceptor",
        name: "Deterministic Interceptors (Ethical Wall)",
        subtitle: "Non-Probabilistic Policy Enforcement & DLP Guardrails",
        category: "governance",
        categoryName: "Deterministic Safety",
        color: "#f43f5e", // Rose
        position: [7, -11, -7],
        size: 2.1,
        description: "Hard-coded Python circuit-breakers that evaluate prompt context, client entities, and target counterparties BEFORE invoking the LLM. Completely eliminates hallucinated compliance.",
        whyMatters: "State Bar ethics rules and SEC insider trading laws cannot be entrusted to an LLM system prompt. If a hostile target matches Weil's client list, execution halts instantly with an HTTP 403.",
        code: `class GovernanceInterceptor:
    \"\"\"Deterministic Circuit-Breaker: Executes PRIOR to any LLM generation.\"\"\"
    
    RESTRICTED_TARGETS = {"AlphaCorp", "Initech Global", "Omni Consumer"}
    
    def evaluate_request(self, client: str, target: str) -> InterceptorVerdict:
        if target in self.RESTRICTED_TARGETS:
            # Deterministic halt - NO TOKENS GENERATED
            return InterceptorVerdict(
                status="POLICY_VIOLATION",
                reason=f"Ethical Wall: Target '{target}' is an existing active client.",
                action="HALT_EXECUTION_AND_ALERT_PARTNER"
            )
        return InterceptorVerdict(status="ALLOW")`,
        consoleLink: "http://localhost:5173",
        consoleLabel: "Weil Single-Pane Cockpit"
      },
      {
        id: "cloud_trace_logging",
        name: "Cloud Trace & Cloud Logging",
        subtitle: "Sub-Millisecond Waterfall Observability & Audit Trail",
        category: "governance",
        categoryName: "Observability",
        color: "#38bdf8", // Sky
        position: [9, 5, 13],
        size: 2.0,
        description: "Comprehensive enterprise telemetry. Cloud Trace captures distributed waterfall spans across Orchestrator -> Gateway -> Interceptor -> Model -> Tool. Cloud Logging creates tamper-proof JSON audit trails.",
        whyMatters: "Provides exact proof of execution latency, token costs, and prompt-response compliance for every transaction in Weil's history.",
        code: `from google.cloud import trace_v2
from google.cloud import logging as cloud_logging

# Cloud Trace context propagation
trace_client = trace_v2.TraceServiceClient()
logging_client = cloud_logging.Client(project="vtxdemos")
logger = logging_client.logger("weil-adk-orchestrator")

# Immutable audit log
logger.log_struct({
    "matter_id": "MATTER-2026-6141",
    "partner": "Andrew Simon",
    "action": "BENCHMARK_REVERSE_BREAKUP_FEE",
    "target": "Zephyr Robotics",
    "status": "APPROVED",
    "trace_id": "trace-991204-adk-vertex"
})`,
        consoleLink: "https://console.cloud.google.com/traces/list?project=vtxdemos",
        consoleLabel: "Cloud Trace in Google Cloud Console"
      }
    ];

    // Constellation Connections (Interconnecting Energy Lines)
    const CONSTELLATION_EDGES = [
      ["gemini_foundation", "google_adk"],
      ["gemini_foundation", "gemini_python_sdk"],
      ["gemini_foundation", "agent_runtime"],
      ["google_adk", "mcp_protocol"],
      ["google_adk", "deterministic_interceptor"],
      ["google_adk", "agent_identity"],
      ["mcp_protocol", "agent_gateway"],
      ["agent_runtime", "agent_gateway"],
      ["agent_runtime", "cloud_trace_logging"],
      ["agent_runtime", "antigravity_sandbox"],
      ["agent_identity", "deterministic_interceptor"],
      ["cloud_trace_logging", "deterministic_interceptor"]
    ];

    // -------------------------------------------------------------------------
    // 2. Google ADK Orbiting Moons Dataset
    // (SPATIALLY SPREAD OUT in 3D HALO with slow, graceful motion & clickable labels)
    // -------------------------------------------------------------------------
    const ADK_MOONS = [
      {
        id: "moon_agent_types",
        name: "Agent Orchestration Types",
        subtitle: "Specialist, Sequential, Parallel, Loop & Workflow Graphs",
        category: "ADK Core Architecture",
        color: "#60a5fa", // Sky Blue
        distance: 8.8,
        angle: 0.2, // ~12 degrees
        elevation: 2.2,
        speed: 0.0012,
        size: 0.75,
        labelOffset: -42,
        description: "Google ADK provides specialized architectural primitives for agent composition: standard LLM Agent (single domain expert), SequentialAgent (linear deterministic step-by-step pipeline A -> B -> C), ParallelAgent (concurrent fan-out of subtasks), LoopAgent (iterative revision until convergence), and ADK 2.0 Graph Workflows.",
        whyMatters: "Prevents fragile monolithic prompts. Weil builds modular legal workflows where an intake agent, a regulatory agent, and a tax agent execute in deterministic sequences with formal handoffs.",
        code: `from google.adk.agents import Agent, SequentialAgent, ParallelAgent

# 1. Parallel domain specialist analysis
specialists = ParallelAgent(
    name="due_diligence_team",
    sub_agents=[antitrust_agent, tax_agent, ip_litigation_agent]
)

# 2. Sequential pipeline: Intake -> Parallel Review -> Partner Sign-off
deal_workflow = SequentialAgent(
    name="weil_closing_pipeline",
    sub_agents=[intake_agent, specialists, partner_summary_agent]
)`,
        consoleLink: "https://adk.dev/agents/overview/",
        consoleLabel: "ADK Agent Orchestration Docs"
      },
      {
        id: "moon_runners",
        name: "Runners (Execution Engine)",
        subtitle: "Runner.run_async(), Event Streaming & Tool Dispatch",
        category: "ADK Core Architecture",
        color: "#38bdf8", // Light Cyan
        distance: 9.0,
        angle: 0.2 + (Math.PI * 2) / 5, // ~84 degrees
        elevation: -2.0,
        speed: 0.0012,
        size: 0.72,
        labelOffset: 34,
        description: "The Runner is ADK's decoupled runtime execution harness. It consumes messages, coordinates memory lookups, dispatches tool calls, executes before/after callbacks, and streams granular Server-Sent Events (SSE) token-by-token.",
        whyMatters: "Decouples business logic from web frameworks. The exact same Runner executes inside a local CLI (`adk run`), a FastAPI microservice, or Vertex AI Agent Runtime without modifying agent code.",
        code: `from google.adk.runners import Runner
from google.genai import types

runner = Runner(agent=lead_agent, session_service=session_service)

# High-performance async SSE event generator
async for event in runner.run_async(
    user_id="partner_andrew",
    session_id="session_ma_01",
    new_message=types.Content(
        role="user", 
        parts=[types.Part.from_text(text="Benchmark break-up fees")]
    )
):
    if hasattr(event, "content") and event.content:
        yield event.content.parts[0].text`,
        consoleLink: "https://adk.dev/runners/overview/",
        consoleLabel: "ADK Runner Architecture"
      },
      {
        id: "moon_sessions",
        name: "Sessions & State",
        subtitle: "InMemory, SQLite & Managed VertexAiSessionService",
        category: "ADK Core Architecture",
        color: "#818cf8", // Indigo
        distance: 8.6,
        angle: 0.2 + ((Math.PI * 2) / 5) * 2, // ~156 degrees
        elevation: 2.8,
        speed: 0.0012,
        size: 0.72,
        labelOffset: -42,
        description: "Manages conversational history, user session state, and matter context. Pluggable session service backends include InMemorySessionService (testing), SQLite (local dev), and VertexAiSessionService (serverless, enterprise GCP persistence).",
        whyMatters: "Enforces strict Zero-Trust matter isolation. An associate working on Matter Alpha has zero access to the memory state or session tokens of Matter Beta. Session databases can be partitioned per matter.",
        code: `from google.adk.sessions import VertexAiSessionService, InMemorySessionService

# Enterprise persistence in Google Cloud Vertex AI
session_service = VertexAiSessionService(
    project="vtxdemos",
    location="us-central1"
)

# Create an authenticated, cryptographically isolated matter session
session = await session_service.create_session(
    app_name="weil_showcase",
    user_id="partner_001",
    session_id="matter_2026_nexus_zephyr"
)`,
        consoleLink: "https://adk.dev/sessions/overview/",
        consoleLabel: "ADK Session Services"
      },
      {
        id: "moon_memory",
        name: "Memory & Precedent RAG",
        subtitle: "Short-Term Working Memory & Vertex AI RAG Memory Service",
        category: "ADK Core Architecture",
        color: "#a78bfa", // Violet
        distance: 9.1,
        angle: 0.2 + ((Math.PI * 2) / 5) * 3, // ~228 degrees
        elevation: -1.8,
        speed: 0.0012,
        size: 0.72,
        labelOffset: 34,
        description: "Provides semantic long-term memory across deals and sessions. Native integration with Vertex AI RAG Corpus (`rag://...`) allows agents to search, retrieve, and recall gold-standard Weil clause precedents automatically.",
        whyMatters: "Associates and partners can instantly query: 'What reverse break-up fee did we negotiate in the 2024 autonomous robotics deal?' and receive fully grounded, citation-backed answers.",
        code: `# Connect ADK Agent to Vertex AI RAG Memory Corpus
# CLI flag: --memory_service_uri=rag://projects/vtxdemos/locations/us-central1/ragCorpora/weil_precedents

from google.adk.agents import Agent

deal_agent = Agent(
    name="precedent_advisor",
    model="gemini-3.8-flash",
    instruction="Recall historical deal terms from firm memory."
    # Memory is automatically retrieved and injected into prompt context
)`,
        consoleLink: "https://adk.dev/memory/overview/",
        consoleLabel: "Vertex AI RAG Memory Service"
      },
      {
        id: "moon_callbacks_tools",
        name: "Tools & Callbacks",
        subtitle: "FunctionTool, McpToolset & Zero-Trust Pre-Execution Hooks",
        category: "ADK Core Architecture",
        color: "#c084fc", // Fuchsia
        distance: 8.7,
        angle: 0.2 + ((Math.PI * 2) / 5) * 4, // ~300 degrees
        elevation: 2.0,
        speed: 0.0012,
        size: 0.75,
        labelOffset: -42,
        description: "Tools empower agents to interact with firm systems (FunctionTool auto-generates JSON Schema from Python docstrings; McpToolset bridges to Model Context Protocol). Lifecycle callbacks (before_agent_callback, after_agent_callback) intercept execution for policy checks and state mutation.",
        whyMatters: "Ethical wall enforcement is executed deterministically in code BEFORE the LLM generates a single token. Callbacks inspect partner credentials, verify matter tags, and block conflicted counterparties with zero hallucination risk.",
        code: `from google.adk.tools import FunctionTool
from google.adk.agents.callback_context import CallbackContext

async def enforce_ethical_wall(ctx: CallbackContext):
    target = ctx.state.get("target_entity")
    if target in {"AlphaCorp", "Initech"}:
        raise PermissionError(f"Ethical Wall Violation: {target} is a restricted client.")

lead_agent = Agent(
    name="ethical_intake_agent",
    model="gemini-3.8-flash",
    tools=[precedent_mcp_toolset],
    before_agent_callback=enforce_ethical_wall
)`,
        consoleLink: "https://adk.dev/tools/overview/",
        consoleLabel: "ADK Tooling & Callback Reference"
      }
    ];

    // -------------------------------------------------------------------------
    // 3. Three.js Scene Setup
    // -------------------------------------------------------------------------
    let scene, camera, renderer, controls;
    let nodeMeshes = [];
    let edgeLines = [];
    let starParticles;
    let raycaster = new THREE.Raycaster();
    let mouse = new THREE.Vector2();
    let hoveredObject = null;
    let selectedNode = null;
    let tourActive = false;
    let tourIndex = 0;
    let tourTimeout = null;

    // Movement Freeze / Slow toggle
    let isMotionFrozen = false;
    let isHoveringCanvas = false;

    // Google ADK Moons System
    let adkPlanetGroup = null;
    let adkOrbitRing = null;
    let adkMoonMeshes = [];
    let moonsVisible = false;

    // Focus / Dimming State
    let isAdkFocused = false;

    const container = document.getElementById('canvas-container');
    const labelsContainer = document.getElementById('labels-container');

    function initThree() {
      // Scene
      scene = new THREE.Scene();
      scene.fog = new THREE.FogExp2(0x030712, 0.015);

      // Camera
      camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 1000);
      camera.position.set(0, 18, 38);

      // Renderer
      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
      renderer.setSize(window.innerWidth, window.innerHeight);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      container.appendChild(renderer.domElement);

      // OrbitControls
      controls = new THREE.OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.05;
      controls.maxDistance = 80;
      controls.minDistance = 5;
      controls.autoRotate = true;
      controls.autoRotateSpeed = 0.35;

      // Lights
      const ambientLight = new THREE.AmbientLight(0xffffff, 0.65);
      scene.add(ambientLight);

      const pointLight1 = new THREE.PointLight(0x3b82f6, 2.2, 80);
      pointLight1.position.set(20, 20, 20);
      scene.add(pointLight1);

      const pointLight2 = new THREE.PointLight(0xf59e0b, 2.2, 80);
      pointLight2.position.set(-20, -20, -20);
      scene.add(pointLight2);

      // Starfield Background Particles
      createStarfield();

      // Create Constellation Nodes
      createNodes();

      // Create Constellation Edges
      createEdges();

      // Setup Google ADK Moon System
      setupAdkMoons();

      // Populate Left Drawer List
      populateNodeList();

      // Events
      window.addEventListener('resize', onWindowResize);
      container.addEventListener('mousemove', onMouseMove);
      container.addEventListener('click', onMouseClick);
      container.addEventListener('mouseenter', () => { isHoveringCanvas = true; });
      container.addEventListener('mouseleave', () => { isHoveringCanvas = false; });

      // Animation Loop
      animate();
    }

    // -------------------------------------------------------------------------
    // 4. Object Creation & Moons Architecture
    // -------------------------------------------------------------------------
    function createStarfield() {
      const count = 1800;
      const geometry = new THREE.BufferGeometry();
      const positions = new Float32Array(count * 3);
      const colors = new Float32Array(count * 3);

      for (let i = 0; i < count * 3; i += 3) {
        positions[i] = (Math.random() - 0.5) * 160;
        positions[i + 1] = (Math.random() - 0.5) * 160;
        positions[i + 2] = (Math.random() - 0.5) * 160;

        const isGold = Math.random() > 0.8;
        colors[i] = isGold ? 0.96 : 0.4;
        colors[i + 1] = isGold ? 0.62 : 0.6;
        colors[i + 2] = isGold ? 0.04 : 0.95;
      }

      geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
      geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

      const material = new THREE.PointsMaterial({
        size: 0.65,
        vertexColors: true,
        transparent: true,
        opacity: 0.75
      });

      starParticles = new THREE.Points(geometry, material);
      scene.add(starParticles);
    }

    function createNodes() {
      CONSTELLATION_NODES.forEach((node) => {
        const group = new THREE.Group();
        group.position.set(node.position[0], node.position[1], node.position[2]);

        // Core Sphere
        const geom = new THREE.SphereGeometry(node.size * 0.6, 32, 32);
        const mat = new THREE.MeshStandardMaterial({
          color: new THREE.Color(node.color),
          emissive: new THREE.Color(node.color),
          emissiveIntensity: 0.55,
          roughness: 0.2,
          metalness: 0.8,
          transparent: true,
          opacity: 1.0
        });
        const mesh = new THREE.Mesh(geom, mat);
        mesh.userData = { 
          ...node, 
          isMoon: false,
          originalColor: new THREE.Color(node.color),
          originalEmissive: new THREE.Color(node.color),
          originalEmissiveIntensity: 0.55,
          originalOpacity: 1.0
        };
        group.add(mesh);

        // Glowing Atmosphere / Halo
        const haloGeom = new THREE.SphereGeometry(node.size * 0.92, 24, 24);
        const haloMat = new THREE.MeshBasicMaterial({
          color: new THREE.Color(node.color),
          transparent: true,
          opacity: 0.22,
          wireframe: true
        });
        const halo = new THREE.Mesh(haloGeom, haloMat);
        halo.name = "halo";
        halo.userData = { originalOpacity: 0.22 };
        group.add(halo);

        // Outer Ring for Center Foundation
        if (node.id === "gemini_foundation") {
          const ringGeom = new THREE.RingGeometry(node.size * 1.25, node.size * 1.45, 32);
          const ringMat = new THREE.MeshBasicMaterial({
            color: 0xf59e0b,
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.4
          });
          const ring = new THREE.Mesh(ringGeom, ringMat);
          ring.rotation.x = Math.PI / 2;
          ring.userData = { originalOpacity: 0.4 };
          group.add(ring);
        }

        scene.add(group);
        nodeMeshes.push({ group, mesh, node, halo });

        if (node.id === "google_adk") {
          adkPlanetGroup = group;
        }

        // HTML Label Overlay
        createHtmlLabel(node);
      });
    }

    function setupAdkMoons() {
      if (!adkPlanetGroup) return;

      // 1. Spacious 3D Orbital Ring for ADK Planet (radius 8.8)
      const ringGeom = new THREE.RingGeometry(8.6, 8.9, 64);
      const ringMat = new THREE.MeshBasicMaterial({
        color: 0x60a5fa,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.0, // hidden initially
        wireframe: true
      });
      adkOrbitRing = new THREE.Mesh(ringGeom, ringMat);
      // Tilt the orbit slightly for a gorgeous perspective (not edge-on)
      adkOrbitRing.rotation.x = Math.PI / 3;
      adkPlanetGroup.add(adkOrbitRing);

      // 2. Create the 5 Moons in a spacious 3D configuration
      ADK_MOONS.forEach((moon) => {
        const moonGroup = new THREE.Group();
        moonGroup.visible = false;
        moonGroup.scale.set(0.001, 0.001, 0.001); // collapsed initially

        // Moon Sphere (Large enough to easily target with mouse)
        const geom = new THREE.SphereGeometry(moon.size * 0.75, 24, 24);
        const mat = new THREE.MeshStandardMaterial({
          color: new THREE.Color(moon.color),
          emissive: new THREE.Color(moon.color),
          emissiveIntensity: 0.85,
          roughness: 0.25,
          metalness: 0.75,
          transparent: true,
          opacity: 1.0
        });
        const mesh = new THREE.Mesh(geom, mat);
        mesh.userData = { ...moon, isMoon: true };
        moonGroup.add(mesh);

        // Glowing Wireframe Aura
        const haloGeom = new THREE.SphereGeometry(moon.size * 1.15, 16, 16);
        const haloMat = new THREE.MeshBasicMaterial({
          color: new THREE.Color(moon.color),
          transparent: true,
          opacity: 0.45,
          wireframe: true
        });
        const halo = new THREE.Mesh(haloGeom, haloMat);
        moonGroup.add(halo);

        // Position on the spacious 3D orbital space
        const x = Math.cos(moon.angle) * moon.distance;
        const z = Math.sin(moon.angle) * moon.distance;
        moonGroup.position.set(x, moon.elevation, z);

        adkPlanetGroup.add(moonGroup);
        adkMoonMeshes.push({ moonGroup, mesh, moon, halo });

        // HTML Clickable Label for Moon
        createMoonHtmlLabel(moon);
      });
    }

    function createHtmlLabel(node) {
      const label = document.createElement('div');
      label.id = `label-${node.id}`;
      label.onclick = () => focusNode(node.id);
      label.className = 'node-label flex items-center gap-1.5 px-2.5 py-1 rounded-lg glass-card text-[11px] font-mono border border-slate-700/60 shadow-md text-slate-300 hover:border-blue-400 hover:text-white transition';
      label.innerHTML = `
        <span class="w-1.5 h-1.5 rounded-full" style="background-color: ${node.color}"></span>
        <span>${node.name}</span>
      `;
      labelsContainer.appendChild(label);
    }

    function createMoonHtmlLabel(moon) {
      const label = document.createElement('div');
      label.id = `label-${moon.id}`;
      label.onclick = (e) => {
        e.stopPropagation();
        focusMoon(moon.id);
      };
      label.className = 'moon-label hidden items-center gap-1.5 px-3 py-1 rounded-xl bg-slate-900/95 text-[11px] font-mono border border-blue-500/70 shadow-2xl text-blue-100 transition';
      label.innerHTML = `
        <span class="w-2 h-2 rounded-full shadow-xs" style="background-color: ${moon.color}"></span>
        <span class="font-bold">🌙 ${moon.name}</span>
      `;
      labelsContainer.appendChild(label);
    }

    function createEdges() {
      CONSTELLATION_EDGES.forEach(([fromId, toId]) => {
        const fromNode = CONSTELLATION_NODES.find(n => n.id === fromId);
        const toNode = CONSTELLATION_NODES.find(n => n.id === toId);
        if (!fromNode || !toNode) return;

        const points = [];
        points.push(new THREE.Vector3(...fromNode.position));
        points.push(new THREE.Vector3(...toNode.position));

        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const material = new THREE.LineBasicMaterial({
          color: 0x3b82f6,
          transparent: true,
          opacity: 0.35,
          linewidth: 1.5
        });

        const line = new THREE.Line(geometry, material);
        line.userData = { originalOpacity: 0.35 };
        scene.add(line);
        edgeLines.push(line);
      });
    }

    // -------------------------------------------------------------------------
    // 5. Cinematic Focus & "Gray-Out" of Non-Selected Planets
    // -------------------------------------------------------------------------
    function applyAdkFocusDimming() {
      if (isAdkFocused) return;
      isAdkFocused = true;

      // 1. Dim all other planets subtly (gray out slightly without completely disappearing)
      nodeMeshes.forEach(({ mesh, halo, node, group }) => {
        if (node.id === "google_adk") {
          // Keep Google ADK vibrant and glowing
          new TWEEN.Tween(mesh.material)
            .to({ emissiveIntensity: 0.95, opacity: 1.0 }, 600)
            .start();
          new TWEEN.Tween(halo.material)
            .to({ opacity: 0.35 }, 600)
            .start();
          const label = document.getElementById(`label-${node.id}`);
          if (label) label.classList.remove('dimmed');
        } else {
          // Gray out and soften other planets
          new TWEEN.Tween(mesh.material)
            .to({ emissiveIntensity: 0.08, opacity: 0.28 }, 600)
            .start();

          // Subtly desaturate towards slate gray
          const desatColor = new THREE.Color(mesh.userData.originalColor).lerp(new THREE.Color(0x64748b), 0.65);
          new TWEEN.Tween(mesh.material.color)
            .to({ r: desatColor.r, g: desatColor.g, b: desatColor.b }, 600)
            .start();

          new TWEEN.Tween(halo.material)
            .to({ opacity: 0.04 }, 600)
            .start();

          // Dim outer rings if present
          group.children.forEach(child => {
            if (child.geometry instanceof THREE.RingGeometry && child !== adkOrbitRing) {
              new TWEEN.Tween(child.material)
                .to({ opacity: 0.06 }, 600)
                .start();
            }
          });

          // Dim HTML labels
          const label = document.getElementById(`label-${node.id}`);
          if (label) label.classList.add('dimmed');
        }
      });

      // 2. Soften connecting constellation lines
      edgeLines.forEach(line => {
        new TWEEN.Tween(line.material)
          .to({ opacity: 0.08 }, 600)
          .start();
      });
    }

    function restoreAllNodesFromDimming() {
      if (!isAdkFocused) return;
      isAdkFocused = false;

      // Restore all planets to full color and brilliance
      nodeMeshes.forEach(({ mesh, halo, node, group }) => {
        new TWEEN.Tween(mesh.material)
          .to({ 
            emissiveIntensity: mesh.userData.originalEmissiveIntensity, 
            opacity: mesh.userData.originalOpacity 
          }, 600)
          .start();

        const origColor = mesh.userData.originalColor;
        new TWEEN.Tween(mesh.material.color)
          .to({ r: origColor.r, g: origColor.g, b: origColor.b }, 600)
          .start();

        new TWEEN.Tween(halo.material)
          .to({ opacity: halo.userData.originalOpacity }, 600)
          .start();

        group.children.forEach(child => {
          if (child.geometry instanceof THREE.RingGeometry && child !== adkOrbitRing) {
            new TWEEN.Tween(child.material)
              .to({ opacity: child.userData.originalOpacity || 0.4 }, 600)
              .start();
          }
        });

        const label = document.getElementById(`label-${node.id}`);
        if (label) label.classList.remove('dimmed');
      });

      // Restore connecting constellation lines
      edgeLines.forEach(line => {
        new TWEEN.Tween(line.material)
          .to({ opacity: line.userData.originalOpacity || 0.35 }, 600)
          .start();
      });
    }

    // -------------------------------------------------------------------------
    // 6. Moons Reveal / Hide Animations
    // -------------------------------------------------------------------------
    function showAdkMoons() {
      if (moonsVisible) return;
      moonsVisible = true;

      // Apply subtle background dimming to non-ADK planets
      applyAdkFocusDimming();

      // Reveal Orbit Ring
      new TWEEN.Tween(adkOrbitRing.material)
        .to({ opacity: 0.5 }, 600)
        .start();

      // Expand Moons outward
      adkMoonMeshes.forEach(({ moonGroup, moon }, idx) => {
        moonGroup.visible = true;
        new TWEEN.Tween(moonGroup.scale)
          .to({ x: 1, y: 1, z: 1 }, 800 + (idx * 100))
          .easing(TWEEN.Easing.Back.Out)
          .start();

        const label = document.getElementById(`label-${moon.id}`);
        if (label) {
          label.classList.remove('hidden');
          label.classList.add('flex');
        }
      });
    }

    function hideAdkMoons() {
      if (!moonsVisible) return;
      moonsVisible = false;

      // Restore all other planets from dimming
      restoreAllNodesFromDimming();

      // Fade Orbit Ring
      new TWEEN.Tween(adkOrbitRing.material)
        .to({ opacity: 0.0 }, 400)
        .start();

      // Collapse Moons inward
      adkMoonMeshes.forEach(({ moonGroup, moon }) => {
        new TWEEN.Tween(moonGroup.scale)
          .to({ x: 0.001, y: 0.001, z: 0.001 }, 400)
          .onComplete(() => { moonGroup.visible = false; })
          .start();

        const label = document.getElementById(`label-${moon.id}`);
        if (label) {
          label.classList.add('hidden');
          label.classList.remove('flex');
        }
      });
    }

    // -------------------------------------------------------------------------
    // 7. Interaction & UI Updates
    // -------------------------------------------------------------------------
    function populateNodeList() {
      const listContainer = document.getElementById('nodes-list');
      listContainer.innerHTML = '';
      CONSTELLATION_NODES.forEach((node) => {
        const item = document.createElement('button');
        item.onclick = () => focusNode(node.id);
        item.className = 'w-full text-left p-2 rounded-xl hover:bg-slate-800/80 transition flex items-center gap-2.5 text-xs group cursor-pointer';
        item.innerHTML = `
          <span class="w-2 h-2 rounded-full shrink-0" style="background-color: ${node.color}"></span>
          <div class="truncate">
            <div class="font-medium text-slate-200 group-hover:text-white truncate flex items-center gap-1.5">
              <span>${node.name}</span>
              ${node.id === 'google_adk' ? '<span class="text-[9px] px-1.5 py-0.2 bg-blue-500/20 text-blue-300 rounded-full font-mono">+5 Moons</span>' : ''}
            </div>
            <div class="text-[10px] text-slate-500 font-mono truncate">${node.categoryName}</div>
          </div>
        `;
        listContainer.appendChild(item);
      });
    }

    function onMouseMove(event) {
      mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
      mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);

      // Test intersections with both nodes and moons
      const interactableMeshes = [
        ...nodeMeshes.map(n => n.mesh),
        ...(moonsVisible ? adkMoonMeshes.map(m => m.mesh) : [])
      ];

      const intersects = raycaster.intersectObjects(interactableMeshes);

      if (intersects.length > 0) {
        const target = intersects[0].object;
        if (hoveredObject !== target) {
          hoveredObject = target;
          container.style.cursor = 'pointer';
        }
      } else {
        if (hoveredObject) {
          hoveredObject = null;
          container.style.cursor = 'grab';
        }
      }
    }

    function onMouseClick(event) {
      raycaster.setFromCamera(mouse, camera);

      const interactableMeshes = [
        ...nodeMeshes.map(n => n.mesh),
        ...(moonsVisible ? adkMoonMeshes.map(m => m.mesh) : [])
      ];

      const intersects = raycaster.intersectObjects(interactableMeshes);

      if (intersects.length > 0) {
        const clickedData = intersects[0].object.userData;
        if (clickedData.isMoon) {
          focusMoon(clickedData.id);
        } else {
          focusNode(clickedData.id);
        }
      }
    }

    function focusNode(nodeId) {
      const node = CONSTELLATION_NODES.find(n => n.id === nodeId);
      if (!node) return;

      selectedNode = node;
      controls.autoRotate = false;

      // If clicking Google ADK, reveal the 5 moons and gently dim the background!
      if (nodeId === "google_adk") {
        showAdkMoons();
      } else {
        hideAdkMoons();
      }

      // Smooth Camera Animation:
      const targetPos = new THREE.Vector3(...node.position);
      const offset = (nodeId === "google_adk") 
        ? new THREE.Vector3(0, 11, 19) // High-angle panoramic view framing all moons
        : new THREE.Vector3(0, 3, 10);
      const destPos = targetPos.clone().add(offset);

      new TWEEN.Tween(camera.position)
        .to({ x: destPos.x, y: destPos.y, z: destPos.z }, 1200)
        .easing(TWEEN.Easing.Cubic.Out)
        .start();

      new TWEEN.Tween(controls.target)
        .to({ x: targetPos.x, y: targetPos.y, z: targetPos.z }, 1200)
        .easing(TWEEN.Easing.Cubic.Out)
        .start();

      // Open Inspector Drawer for Node
      openInspector(node, false);
    }

    function focusMoon(moonId) {
      const moon = ADK_MOONS.find(m => m.id === moonId);
      if (!moon || !adkPlanetGroup) return;

      const moonMeshObj = adkMoonMeshes.find(m => m.moon.id === moonId);
      if (!moonMeshObj) return;

      controls.autoRotate = false;

      // Ensure background dimming stays active when inspecting a moon
      applyAdkFocusDimming();

      // Get world position of this moon
      const worldPos = new THREE.Vector3();
      moonMeshObj.mesh.getWorldPosition(worldPos);

      // Smooth camera focus onto the moon
      const destPos = worldPos.clone().add(new THREE.Vector3(0, 2.0, 6.5));

      new TWEEN.Tween(camera.position)
        .to({ x: destPos.x, y: destPos.y, z: destPos.z }, 1000)
        .easing(TWEEN.Easing.Cubic.Out)
        .start();

      new TWEEN.Tween(controls.target)
        .to({ x: worldPos.x, y: worldPos.y, z: worldPos.z }, 1000)
        .easing(TWEEN.Easing.Cubic.Out)
        .start();

      // Open Inspector Drawer for Moon
      openInspector(moon, true);
    }

    function openInspector(item, isMoon) {
      const drawer = document.getElementById('inspector-drawer');
      const badge = document.getElementById('inspect-badge');
      const icon = document.getElementById('inspect-icon');
      const parentLabel = document.getElementById('inspect-parent');
      const title = document.getElementById('inspect-title');
      const subtitle = document.getElementById('inspect-subtitle');
      const desc = document.getElementById('inspect-description');
      const whyMatters = document.getElementById('inspect-why-matters');
      const code = document.getElementById('inspect-code');
      const link = document.getElementById('inspect-link');
      const linkLabel = document.getElementById('inspect-link-label');
      const moonsQuickNav = document.getElementById('moons-quicknav');
      const backBtn = document.getElementById('back-to-planet');

      badge.textContent = item.categoryName || item.category;
      badge.style.backgroundColor = `${item.color}20`;
      badge.style.color = item.color;
      badge.style.borderColor = `${item.color}50`;

      if (isMoon) {
        icon.textContent = "🌙";
        parentLabel.textContent = "Orbiting Google ADK Planet";
        moonsQuickNav.classList.add('hidden');
        backBtn.classList.remove('hidden');
      } else {
        icon.textContent = item.id === 'google_adk' ? "🪐" : "⭐";
        parentLabel.textContent = item.id === 'google_adk' ? "Google ADK Planet (Click Moons to Explore)" : "Google Cloud Architecture";
        backBtn.classList.add('hidden');

        if (item.id === 'google_adk') {
          moonsQuickNav.classList.remove('hidden');
          populateMoonsQuickNav();
        } else {
          moonsQuickNav.classList.add('hidden');
        }
      }

      title.textContent = item.name;
      subtitle.textContent = item.subtitle;
      desc.textContent = item.description;
      whyMatters.textContent = item.whyMatters;
      code.textContent = item.code;
      link.href = item.consoleLink;
      linkLabel.textContent = item.consoleLabel;

      drawer.classList.remove('translate-x-full');
    }

    function populateMoonsQuickNav() {
      const list = document.getElementById('moons-button-list');
      list.innerHTML = '';
      ADK_MOONS.forEach((moon) => {
        const btn = document.createElement('button');
        btn.onclick = () => focusMoon(moon.id);
        btn.className = 'w-full text-left p-2.5 rounded-lg bg-blue-900/30 hover:bg-blue-800/50 border border-blue-500/30 text-xs flex items-center justify-between transition group cursor-pointer';
        btn.innerHTML = `
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full" style="background-color: ${moon.color}"></span>
            <span class="font-medium text-slate-200 group-hover:text-white">${moon.name}</span>
          </div>
          <span class="text-[10px] font-mono text-blue-300">Inspect ➔</span>
        `;
        list.appendChild(btn);
      });
    }

    function closeInspector() {
      const drawer = document.getElementById('inspector-drawer');
      drawer.classList.add('translate-x-full');
      selectedNode = null;
      hideAdkMoons();
      controls.autoRotate = true;
    }

    function resetCamera() {
      closeInspector();
      if (tourActive) stopGuidedTour();

      new TWEEN.Tween(camera.position)
        .to({ x: 0, y: 18, z: 38 }, 1400)
        .easing(TWEEN.Easing.Cubic.Out)
        .start();

      new TWEEN.Tween(controls.target)
        .to({ x: 0, y: 0, z: 0 }, 1400)
        .easing(TWEEN.Easing.Cubic.Out)
        .start();

      controls.autoRotate = true;
    }

    function copySnippet() {
      const code = document.getElementById('inspect-code').textContent;
      navigator.clipboard.writeText(code).then(() => {
        const text = document.getElementById('copy-text');
        text.textContent = "Copied to Clipboard!";
        setTimeout(() => { text.textContent = "Copy Code"; }, 2000);
      });
    }

    // Toggle Motion / Pause
    function toggleOrbitMovement() {
      isMotionFrozen = !isMotionFrozen;
      const btn = document.getElementById('orbit-toggle-btn');
      const icon = document.getElementById('orbit-toggle-icon');
      const text = document.getElementById('orbit-toggle-text');

      if (isMotionFrozen) {
        controls.autoRotate = false;
        icon.textContent = "▶";
        text.textContent = "Resume Motion";
        btn.classList.add('bg-blue-600', 'text-white');
      } else {
        controls.autoRotate = true;
        icon.textContent = "⏸";
        text.textContent = "Freeze Motion";
        btn.classList.remove('bg-blue-600', 'text-white');
      }
    }

    // -------------------------------------------------------------------------
    // 8. Category Filtering
    // -------------------------------------------------------------------------
    function filterCategory(cat) {
      document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.className = 'filter-btn px-3 py-1 text-xs rounded-xl text-slate-400 hover:text-white transition';
      });
      const activeBtn = document.getElementById(`filter-${cat}`);
      if (activeBtn) {
        activeBtn.className = 'filter-btn px-3 py-1 text-xs rounded-xl bg-blue-600 text-white font-medium transition';
      }

      nodeMeshes.forEach(({ group, node, halo }) => {
        const match = (cat === 'all' || node.category === cat);
        group.visible = match;
        const label = document.getElementById(`label-${node.id}`);
        if (label) label.style.display = match ? 'flex' : 'none';
      });

      if (cat !== 'all' && cat !== 'framework') {
        hideAdkMoons();
      }
    }

    // -------------------------------------------------------------------------
    // 9. Guided Executive Tour
    // -------------------------------------------------------------------------
    function toggleGuidedTour() {
      if (tourActive) {
        stopGuidedTour();
      } else {
        startGuidedTour();
      }
    }

    function startGuidedTour() {
      tourActive = true;
      tourIndex = 0;
      const btn = document.getElementById('tour-btn');
      btn.innerHTML = `
        <span class="w-2 h-2 rounded-full bg-red-600 animate-ping"></span>
        <span>Stop Tour</span>
      `;
      btn.className = "flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-red-500 hover:bg-red-400 text-white font-bold text-xs shadow-lg shadow-red-500/30 transition cursor-pointer";
      tourStep();
    }

    function stopGuidedTour() {
      tourActive = false;
      clearTimeout(tourTimeout);
      const btn = document.getElementById('tour-btn');
      btn.innerHTML = `
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
        <span>Start Executive Tour</span>
      `;
      btn.className = "flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-xs shadow-lg shadow-amber-500/20 transition cursor-pointer";
    }

    function tourStep() {
      if (!tourActive) return;
      if (tourIndex >= CONSTELLATION_NODES.length) {
        stopGuidedTour();
        resetCamera();
        return;
      }
      const node = CONSTELLATION_NODES[tourIndex];
      focusNode(node.id);
      tourIndex++;
      tourTimeout = setTimeout(tourStep, 8000); // 8 seconds per node
    }

    // -------------------------------------------------------------------------
    // 10. Labels Position Sync & Render Loop
    // -------------------------------------------------------------------------
    function updateLabels() {
      const tempV = new THREE.Vector3();

      // Main Planet Labels
      nodeMeshes.forEach(({ node, group }) => {
        const label = document.getElementById(`label-${node.id}`);
        if (!label || !group.visible) return;

        tempV.set(...node.position);
        tempV.project(camera);

        const isBehind = tempV.z > 1;
        if (isBehind) {
          label.style.opacity = '0';
        } else {
          const x = (tempV.x * 0.5 + 0.5) * window.innerWidth;
          const y = (-(tempV.y * 0.5) + 0.5) * window.innerHeight;
          label.style.left = `${x}px`;
          label.style.top = `${y - 25}px`;
          // If dimmed, let CSS .dimmed handle opacity (0.18)
          if (!label.classList.contains('dimmed')) {
            label.style.opacity = '0.9';
          }
        }
      });

      // Moons Labels (Staggered offsets to NEVER overlap)
      if (moonsVisible && adkPlanetGroup) {
        adkMoonMeshes.forEach(({ mesh, moon, moonGroup }) => {
          const label = document.getElementById(`label-${moon.id}`);
          if (!label || !moonGroup.visible) return;

          mesh.getWorldPosition(tempV);
          tempV.project(camera);

          const isBehind = tempV.z > 1;
          if (isBehind) {
            label.style.opacity = '0';
          } else {
            const x = (tempV.x * 0.5 + 0.5) * window.innerWidth;
            const y = (-(tempV.y * 0.5) + 0.5) * window.innerHeight;
            label.style.left = `${x}px`;
            // Staggered Y positioning prevents any horizontal collision
            label.style.top = `${y + (moon.labelOffset || -35)}px`;
            label.style.opacity = '0.96';
          }
        });
      }
    }

    function onWindowResize() {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    }

    function animate(time) {
      requestAnimationFrame(animate);
      TWEEN.update();
      controls.update();

      // Subtle star particle drift
      if (starParticles && !isMotionFrozen) {
        starParticles.rotation.y += 0.0003;
      }

      // Rotate planet halos
      nodeMeshes.forEach(({ halo }) => {
        halo.rotation.y += 0.008;
        halo.rotation.x += 0.004;
      });

      // Orbit the Moons:
      // 1. Automatically FREEZES or slows when user hovers canvas or freezes motion!
      // 2. Orbits at ultra-slow, graceful speed (0.0012)
      if (moonsVisible && adkMoonMeshes.length > 0) {
        if (!isMotionFrozen && !isHoveringCanvas) {
          adkMoonMeshes.forEach(({ moonGroup, moon }) => {
            moon.angle += moon.speed;
            const x = Math.cos(moon.angle) * moon.distance;
            const z = Math.sin(moon.angle) * moon.distance;
            moonGroup.position.set(x, moon.elevation, z);
          });

          if (adkOrbitRing) {
            adkOrbitRing.rotation.z += 0.0004;
          }
        }
      }

      updateLabels();
      renderer.render(scene, camera);
    }

    window.onload = initThree;
  </script>
</body>
</html>
"""

# Write to both frontend/public/constellation.html and walkthrough_scripts/presentation_3d_constellation.html
frontend_path = Path("/Users/jesusarguelles/IdeaProjects/vertex-ai-samples/semiautonomous-agents/weil-legal-agentic-showcase/frontend/public/constellation.html")
walkthrough_path = Path("/Users/jesusarguelles/IdeaProjects/vertex-ai-samples/semiautonomous-agents/weil-legal-agentic-showcase/walkthrough_scripts/presentation_3d_constellation.html")

frontend_path.parent.mkdir(parents=True, exist_ok=True)
walkthrough_path.parent.mkdir(parents=True, exist_ok=True)

with open(frontend_path, "w") as f:
    f.write(html_content)

with open(walkthrough_path, "w") as f:
    f.write(html_content)

print(f"✅ Generated 3D Constellation with Cinematic ADK Focus & Subtle Background Dimming in:\n - {frontend_path}\n - {walkthrough_path}")
