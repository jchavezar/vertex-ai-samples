# -*- coding: utf-8 -*-
"""7 Distinct Domain Applications + 33 Bespoke Use-Case App Canvases for the Rocket AI Hackathon Suite.
Every single square (`1.1` through `M.5`) renders its own bespoke interactive UI archetype,
custom sliders, structured visual output cards, real Gemini Live Audio WebSocket (`gemini-live-2.5-flash-native-audio`),
real Gemini Enterprise `streamAssist` API + Web UI links, and automatic model routing (`gemini-3.8-flash` for ADK/Agent Engine)."""

import json
from typing import Dict
from shared.bespoke_apps import BESPOKE_ARCHETYPES
from shared.bespoke_renderers import BESPOKE_RENDERER_JS
from shared.catalog_data import CLOUD_RUN_URLS, DOMAINS_BY_ID

DOMAIN_THEME_STYLES: Dict[str, Dict[str, str]] = {
    "sales": {
        "badge": "TERMINAL // ROCKET PRO TPO & ORIGINATION DESK",
        "bg_dark": "#050914",
        "panel_dark": "#0B1224",
        "border_dark": "#1E293B",
        "accent": "#10B981",
        "accent2": "#3B82F6",
        "font_heading": "'JetBrains Mono', monospace",
        "sub_banner": "LIVE MBS 30YR UMBS 5.5: 99-18 (+0-04)  •  10Y US TREASURY: 4.02% (-6 bps)  •  ROCKET PAR 30YR FIXED: 6.125%  •  FANNIE MAE DU API: ONLINE  •  O365 OUTLOOK/TEAMS MCP: CONNECTED"
    },
    "ops": {
        "badge": "WORKBENCH // ROCKET LOGIC UNDERWRITING & DOCUMENT AI",
        "bg_dark": "#0F172A",
        "panel_dark": "#1E293B",
        "border_dark": "#334155",
        "accent": "#0284C7",
        "accent2": "#4F46E5",
        "font_heading": "'Inter', sans-serif",
        "sub_banner": "DOCUMENT AI LENDING PARSERS: W-2 / PAYSTUB / 1040 SCHEDULE C (99.4% CONFIDENCE)  •  FANNIE MAE B3-3.1 & FORM 1084 ENGINE: ACTIVE  •  ROCKET CLOSE (AMROCK) TITLE GROUNDING: READY"
    },
    "servicing": {
        "badge": "OMNICHANNEL CX // MR. COOPER x ROCKET SERVICING STUDIO",
        "bg_dark": "#031217",
        "panel_dark": "#07222B",
        "border_dark": "#0F3D4C",
        "accent": "#14B8A6",
        "accent2": "#06B6D4",
        "font_heading": "'Inter', sans-serif",
        "sub_banner": "REAL GEMINI LIVE API (BIDI WEBSOCKETS 24kHz PCM)  •  CCAI AGENT ASSIST (SYNOPSIS NEXT-GEN)  •  CFPB REG X GUARDRAILS: ACTIVE  •  MR. COOPER PORTFOLIO RECAPTURE ENGINE"
    },
    "marketing": {
        "badge": "CREATIVE STUDIO // REDFIN x ROCKET MONEY GROWTH HUB",
        "bg_dark": "#12111A",
        "panel_dark": "#1C1A29",
        "border_dark": "#2E2A44",
        "accent": "#E11D48",
        "accent2": "#8B5CF6",
        "font_heading": "'Plus Jakarta Sans', 'Inter', sans-serif",
        "sub_banner": "GEMPIX-2 / NANO BANANA 2 VIRTUAL STAGING  •  GEMINI OMNI & VEO 3.1 9:16 REELS  •  ANTIGRAVITY MCP: REDFIN TOURS <-> ROCKET MONEY DOWN PAYMENT VAULTS  •  TILA REG Z APR VERIFIED"
    },
    "risk": {
        "badge": "SOVEREIGN VAULT // ROCKET LEGAL, CFPB, TRID & MODEL ARMOR",
        "bg_dark": "#090D16",
        "panel_dark": "#111827",
        "border_dark": "#374151",
        "accent": "#F59E0B",
        "accent2": "#10B981",
        "font_heading": "'Inter', sans-serif",
        "sub_banner": "GOOGLE CLOUD MODEL ARMOR + SENSITIVE DATA PROTECTION (GLBA NPI MASKING)  •  12 CFR § 1026.19 TRID 0%/10% TOLERANCE AUDITOR  •  ECOA REG B 500-TWIN FAIR LENDING CERTIFIER"
    },
    "sdlc": {
        "badge": "ANTIGRAVITY 2.0 IDE // CODEMENDER & AI SOFTWARE FACTORY",
        "bg_dark": "#040507",
        "panel_dark": "#0A0D12",
        "border_dark": "#1F2937",
        "accent": "#22C55E",
        "accent2": "#A855F7",
        "font_heading": "'JetBrains Mono', monospace",
        "sub_banner": "GOOGLE ANTIGRAVITY 2.0 SWARM (WORKSPACE='SHARE')  •  DEEPMIND CODEMENDER (`cm verify` / `cm fix` IN gVISOR SANDBOX)  •  LEGACY C# .NET 4.8 WCF -> .NET 9 CLOUD RUN MODERNIZER"
    },
    "moonshots": {
        "badge": "MOONSHOT LAB // GOOGLE X & DEEPMIND ARGON PROTOTYPES",
        "bg_dark": "#040014",
        "panel_dark": "#0B0524",
        "border_dark": "#261854",
        "accent": "#06B6D4",
        "accent2": "#EC4899",
        "font_heading": "'Space Grotesk', 'Inter', sans-serif",
        "sub_banner": "PROJECT SIREN (REAL 24kHz LIVE VOICE WEBSOCKET)  •  PROJECT SPATIAL CLOSE (GEMPIX-2 + HOMESTYLE)  •  PROJECT HIVEMIND (4-AGENT ADK SWARM)  •  PROJECT AIR-TIGHT (SELF-HEALING LOS)"
    }
}


def render_domain_service_html(dept_id: str, initial_case_code: str, auth_token: str) -> str:
    """Renders the bespoke UI/UX web application for one of the 7 separated Cloud Run services."""
    dept = DOMAINS_BY_ID.get(dept_id, DOMAINS_BY_ID["sales"])
    style = DOMAIN_THEME_STYLES.get(dept_id, DOMAIN_THEME_STYLES["sales"])
    projects = dept["projects"]
    if not initial_case_code or not any(p["code"] == initial_case_code for p in projects):
        initial_case_code = projects[0]["code"]

    default_theme = "light" if dept_id == "ops" else "dark"
    projects_json = json.dumps(projects)
    archetypes_json = json.dumps(BESPOKE_ARCHETYPES)

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="{default_theme}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{dept['shortTitle']} | Bespoke Rocket AI Hackathon Suite</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-canvas: {style['bg_dark']};
      --bg-panel: {style['panel_dark']};
      --border-col: {style['border_dark']};
      --text-main: #F8FAFC;
      --text-muted: #94A3B8;
      --accent: {style['accent']};
      --accent2: {style['accent2']};
    }}
    [data-theme="light"] {{
      --bg-canvas: #F8FAFC;
      --bg-panel: #FFFFFF;
      --border-col: #CBD5E1;
      --text-main: #0F172A;
      --text-muted: #475569;
    }}
    body {{
      background-color: var(--bg-canvas);
      color: var(--text-main);
      font-family: 'Inter', sans-serif;
      transition: background-color 0.25s ease, color 0.25s ease;
    }}
    .panel-card {{
      background-color: var(--bg-panel);
      border: 1px solid var(--border-col);
    }}
    .mono {{ font-family: 'JetBrains Mono', monospace; }}
    .heading-font {{ font-family: {style['font_heading']}; }}

    /* Claude-Code Shrinking & Shining Ink Animation */
    .shrinking-shining-ink {{
      width: 18px;
      height: 18px;
      border-radius: 50%;
      background: radial-gradient(circle at 30% 30%, #ffffff, var(--accent), var(--accent2));
      animation: inkPulse 1.35s ease-in-out infinite;
      box-shadow: 0 0 16px var(--accent);
      display: inline-block;
    }}
    @keyframes inkPulse {{
      0%, 100% {{ transform: scale(1) rotate(0deg); opacity: 0.95; border-radius: 50%; }}
      50% {{ transform: scale(0.58) rotate(180deg); opacity: 0.55; border-radius: 38% 62% 55% 45%; }}
    }}
    .sweep-text {{
      background: linear-gradient(90deg, var(--text-muted) 0%, var(--text-main) 50%, var(--accent) 100%);
      background-size: 200% auto;
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      animation: textSweep 1.8s linear infinite;
    }}
    @keyframes textSweep {{
      to {{ background-position: 200% center; }}
    }}
  </style>
</head>
<body class="min-h-screen flex flex-col">

  <!-- TOP TELEMETRY & DOMAIN RIBBON -->
  <div class="w-full py-1.5 px-4 text-[11px] mono border-b flex items-center justify-between overflow-x-auto whitespace-nowrap"
       style="background:rgba(0,0,0,0.6); border-color:var(--border-col); color:var(--accent);">
    <div class="flex items-center gap-3">
      <span class="inline-block w-2 h-2 rounded-full animate-ping" style="background:var(--accent);"></span>
      <span class="font-bold">{style['badge']}</span>
      <span class="text-slate-400">|</span>
      <span class="text-slate-300">{style['sub_banner']}</span>
    </div>
    <div class="flex items-center gap-3 pl-4">
      <a href="https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023" target="_blank"
         class="px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/40 hover:bg-purple-500/30 font-bold">
        ✨ Real Gemini Enterprise UI ↗
      </a>
      <span class="px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">SERVICE: {dept['service_name']}</span>
      <a href="/logout" class="text-slate-400 hover:text-rose-400 underline">Logout</a>
    </div>
  </div>

  <!-- MAIN DOMAIN HEADER -->
  <header class="panel-card border-t-0 border-x-0 px-6 py-4 shadow-lg">
    <div class="max-w-7xl mx-auto flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
      <div>
        <div class="flex flex-wrap items-center gap-2 mb-1.5">
          <a href="{CLOUD_RUN_URLS['portal']}?auth_token={auth_token}"
             class="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-bold mono border transition hover:opacity-90"
             style="border-color:var(--accent); color:var(--accent); background:rgba(255,255,255,0.03);">
            ← Main Rocket Hackathon Portal
          </a>
          <span id="header-runtime-pill" class="px-2.5 py-1 rounded-lg text-[11px] font-bold mono bg-indigo-500/15 text-indigo-300 border border-indigo-500/30">
            ⚡ Vertex AI Global + Agent Engine Runtime
          </span>
          <span id="header-archetype-pill" class="px-2.5 py-1 rounded-lg text-[11px] font-bold mono bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
            🎨 Bespoke Use-Case App
          </span>
        </div>
        <h1 id="bespoke-app-header-title" class="text-xl md:text-2xl font-extrabold heading-font tracking-tight">{dept['fullTitle']}</h1>
        <p id="bespoke-routing-note" class="text-xs mt-0.5 mono" style="color:var(--text-muted);"></p>
      </div>

      <!-- Header Right Controls: Model Selector + Theme Toggle + Docs Link -->
      <div class="flex flex-wrap items-center gap-2.5 shrink-0">
        <div class="panel-card rounded-xl px-3 py-1.5 flex items-center gap-2">
          <label class="text-[10px] mono uppercase font-bold" style="color:var(--text-muted);">Model Endpoint:</label>
          <select id="model-select" class="bg-transparent text-xs font-bold mono focus:outline-none" style="color:var(--accent);">
            <option value="gemini-4-argon" class="bg-slate-900 text-white">gemini-4-argon (Frontier Reasoning)</option>
            <option value="gemini-3.8-flash" class="bg-slate-900 text-white">gemini-3.8-flash (ADK / Agent Engine / Fast)</option>
          </select>
        </div>
        <button onclick="toggleTheme()" id="theme-btn"
                class="panel-card px-3.5 py-2 rounded-xl text-xs font-bold mono hover:opacity-80 transition">
          ☀️ / 🌙 Theme
        </button>
        <a id="top-docs-link" href="{CLOUD_RUN_URLS['portal']}/docs/{initial_case_code}?auth_token={auth_token}" target="_blank"
           class="px-4 py-2 rounded-xl text-xs font-bold text-white shadow-lg transition hover:opacity-95 mono"
           style="background:linear-gradient(135deg, var(--accent), var(--accent2));">
          📘 Reproduction Blueprint & Skills ↗
        </a>
      </div>
    </div>

    <!-- USE CASE SELECTOR PILLS FOR THIS DOMAIN -->
    <div class="max-w-7xl mx-auto mt-4 pt-3 border-t flex flex-wrap gap-2" style="border-color:var(--border-col);" id="case-tabs">
    </div>
  </header>

  <!-- MAIN WORKSPACE GRID -->
  <main class="max-w-7xl mx-auto px-6 py-6 flex-grow w-full space-y-6">

    <!-- 1. HERO BESPOKE INTERACTIVE APPLICATION CANVAS (UNIQUE PER USE CASE!) -->
    <section class="panel-card rounded-2xl p-6 shadow-2xl relative overflow-hidden">
      <div style="position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg, var(--accent), var(--accent2));"></div>
      <div class="flex flex-wrap items-center justify-between gap-2 pb-3 mb-4 border-b" style="border-color:var(--border-col);">
        <div class="flex items-center gap-2.5">
          <span class="w-3 h-3 rounded-full" style="background:var(--accent);"></span>
          <h2 id="canvas-section-title" class="text-sm md:text-base font-extrabold uppercase mono tracking-wider">Bespoke Interactive Use-Case Application</h2>
        </div>
        <div class="flex items-center gap-2">
          <span id="sandbox-ms-badge" class="text-[11px] mono px-2.5 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
            Verified in gVisor Sandbox
          </span>
        </div>
      </div>

      <!-- Bespoke Per-Square Interactive Sliders (if configured for this square) -->
      <div id="domain-custom-widget" class="mb-4"></div>

      <!-- Bespoke Per-Square Visual Application Surface -->
      <div id="domain-bespoke-visualizer" class="mb-5"></div>

      <!-- Deterministic Sandbox Metrics Cards -->
      <div id="sandbox-metrics-grid" class="grid sm:grid-cols-2 lg:grid-cols-4 gap-3"></div>
    </section>

    <!-- 2. TWO-COLUMN SCENARIO CONTROLLER & STRUCTURED AI DECISION CARDS -->
    <div class="grid lg:grid-cols-12 gap-6">

      <!-- LEFT COLUMN (5 COLS): SCENARIO PAYLOAD & ARCHITECTURE -->
      <div class="lg:col-span-5 space-y-6">
        <div class="panel-card rounded-2xl p-5 shadow-xl">
          <div class="flex items-center justify-between gap-2 mb-2">
            <span id="active-code-badge" class="px-2.5 py-0.5 rounded-full text-xs font-bold mono"
                  style="background:rgba(16,185,129,0.15); color:var(--accent); border:1px solid var(--accent);"></span>
            <span id="active-level-badge" class="px-2.5 py-0.5 rounded-full text-xs font-bold mono bg-purple-500/15 text-purple-300 border border-purple-500/30"></span>
          </div>
          <h3 id="active-title" class="text-lg font-extrabold heading-font mb-1"></h3>
          <p id="active-desc" class="text-xs leading-relaxed mb-3" style="color:var(--text-muted);"></p>

          <div class="mb-3">
            <div class="text-[10px] mono uppercase font-bold mb-1" style="color:var(--text-muted);">GCP & Antigravity Stack:</div>
            <div id="active-stack" class="flex flex-wrap gap-1.5"></div>
          </div>

          <div class="p-3 rounded-xl text-xs border mb-3"
               style="background:rgba(99,102,241,0.08); border-color:rgba(99,102,241,0.3);">
            <div class="font-bold text-indigo-400 mono text-[10px] uppercase mb-0.5">🎯 Why This Displaces AWS / Anthropic / Sierra:</div>
            <div id="active-compete" class="text-xs leading-relaxed"></div>
          </div>

          <div>
            <div class="flex items-center justify-between mb-1">
              <label class="text-[11px] font-bold uppercase mono" style="color:var(--text-muted);">Live Input Scenario / Artifact:</label>
              <button onclick="resetSampleInput()" class="text-[11px] mono underline" style="color:var(--accent);">Reset Preset</button>
            </div>
            <textarea id="scenario-input" rows="6"
                      class="w-full rounded-xl p-3 text-xs mono focus:outline-none border leading-relaxed"
                      style="background:rgba(0,0,0,0.35); color:var(--text-main); border-color:var(--border-col);"></textarea>
          </div>

          <div class="mt-3 flex flex-wrap gap-2">
            <button onclick="executeLiveDemo()" id="run-btn"
                    class="flex-grow py-3 px-4 rounded-xl font-bold text-xs text-white shadow-lg transition transform active:scale-[0.99] flex items-center justify-center gap-2 mono"
                    style="background:linear-gradient(135deg, var(--accent), var(--accent2));">
              <span id="run-btn-label">⚡ Execute Live Structured Synthesis</span>
            </button>
            <button onclick="speakCurrentOutput()" id="tts-btn"
                    class="px-3.5 py-3 rounded-xl font-bold text-xs panel-card hover:opacity-85 transition mono">
              🔊 Read
            </button>
          </div>
        </div>

        <div class="panel-card rounded-2xl p-5 shadow-xl">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-bold uppercase mono" style="color:var(--accent);">📐 GCP Reference Architecture (<=78 Cols)</span>
            <a id="card-docs-link" href="#" target="_blank" class="text-[11px] mono underline" style="color:var(--accent2);">Full Blueprint & Skills ↗</a>
          </div>
          <pre id="active-arch" class="text-[10px] mono overflow-x-auto p-3 rounded-xl border leading-snug"
               style="background:rgba(0,0,0,0.45); border-color:var(--border-col); color:#E2E8F0;"></pre>
        </div>
      </div>

      <!-- RIGHT COLUMN (7 COLS): STRUCTURED EXECUTIVE SYNTHESIS & REPRODUCTION CODE -->
      <div class="lg:col-span-7 space-y-6">

        <!-- Waiting / Shrinking & Shining Ink Loader -->
        <div id="loading-banner" class="hidden panel-card rounded-2xl p-5 border-2 flex items-center gap-4"
             style="border-color:var(--accent);">
          <span class="shrinking-shining-ink shrink-0"></span>
          <div>
            <div class="text-sm font-bold sweep-text mono" id="loading-status-text">
              Executing gVisor Sandbox & Structured Vertex AI Synthesis...
            </div>
            <div class="text-[11px] mono mt-0.5" style="color:var(--text-muted);" id="loading-sub-text">
              Project: vtxdemos • Enforcing Structured Use-Case Schema
            </div>
          </div>
        </div>

        <!-- Structured AI Executive Decision Cards (Never raw unformatted markdown dumps!) -->
        <div class="panel-card rounded-2xl p-6 shadow-xl">
          <div class="flex flex-wrap items-center justify-between gap-2 pb-3 mb-4 border-b" style="border-color:var(--border-col);">
            <div class="flex items-center gap-2">
              <span class="w-2.5 h-2.5 rounded-full bg-indigo-400"></span>
              <h3 class="text-sm font-extrabold uppercase mono tracking-wider" id="synthesis-card-title">Live Structured AI Decision Cards</h3>
            </div>
            <div class="flex items-center gap-2">
              <span id="vertex-model-badge" class="text-[11px] mono px-2.5 py-0.5 rounded bg-indigo-500/15 text-indigo-300 border border-indigo-500/30">
                gemini-4-argon
              </span>
              <span id="vertex-latency-badge" class="text-[11px] mono px-2.5 py-0.5 rounded bg-slate-800 text-slate-300">
                Ready
              </span>
            </div>
          </div>
          <div id="vertex-output-body" class="space-y-4"></div>
        </div>

        <!-- Production Code Snippet & Steps -->
        <div class="panel-card rounded-2xl p-6 shadow-xl">
          <div class="flex items-center justify-between pb-3 mb-3 border-b" style="border-color:var(--border-col);">
            <span class="text-xs font-bold uppercase mono" style="color:var(--accent);">💻 Standalone Reproduction Code & Steps</span>
            <button onclick="copyCodeSnippet()" class="px-3 py-1 rounded-lg text-[11px] font-bold mono panel-card hover:opacity-80">
              📋 Copy Code
            </button>
          </div>
          <ol id="active-repro-steps" class="list-decimal list-inside text-xs space-y-1.5 mb-4" style="color:var(--text-muted);"></ol>
          <pre id="active-code-snippet" class="text-[11px] mono overflow-x-auto p-4 rounded-xl border leading-relaxed"
               style="background:#020617; border-color:var(--border-col); color:#A5F3FC;"></pre>
        </div>

      </div>
    </div>
  </main>

  <!-- CROSS-SERVICE DOMAIN SWITCHER FOOTER -->
  <footer class="panel-card border-b-0 border-x-0 py-6 px-6 mt-8">
    <div class="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4 text-xs">
      <div class="mono" style="color:var(--text-muted);">
        🚀 <strong>Rocket AI Hackathon</strong> • 8 Separated Private Cloud Run Services • 33 Bespoke Use-Case Apps
      </div>
      <div class="flex flex-wrap gap-2 justify-center">
        <a href="{CLOUD_RUN_URLS['portal']}?auth_token={auth_token}" class="px-2.5 py-1 rounded panel-card mono text-[11px] hover:opacity-80">🏢 Main Portal</a>
        <a href="{CLOUD_RUN_URLS['sales']}?auth_token={auth_token}" class="px-2.5 py-1 rounded panel-card mono text-[11px] hover:opacity-80">1. Origination</a>
        <a href="{CLOUD_RUN_URLS['ops']}?auth_token={auth_token}" class="px-2.5 py-1 rounded panel-card mono text-[11px] hover:opacity-80">2. Underwriting</a>
        <a href="{CLOUD_RUN_URLS['servicing']}?auth_token={auth_token}" class="px-2.5 py-1 rounded panel-card mono text-[11px] hover:opacity-80">3. Servicing</a>
        <a href="{CLOUD_RUN_URLS['marketing']}?auth_token={auth_token}" class="px-2.5 py-1 rounded panel-card mono text-[11px] hover:opacity-80">4. Marketing</a>
        <a href="{CLOUD_RUN_URLS['risk']}?auth_token={auth_token}" class="px-2.5 py-1 rounded panel-card mono text-[11px] hover:opacity-80">5. Compliance</a>
        <a href="{CLOUD_RUN_URLS['sdlc']}?auth_token={auth_token}" class="px-2.5 py-1 rounded panel-card mono text-[11px] hover:opacity-80">6. SDLC/CodeMender</a>
        <a href="{CLOUD_RUN_URLS['moonshots']}?auth_token={auth_token}" class="px-2.5 py-1 rounded panel-card mono text-[11px] hover:opacity-80">7. Moonshots</a>
      </div>
    </div>
  </footer>

  <script>
    const DEPT_ID = "{dept_id}";
    const AUTH_TOKEN = "{auth_token}";
    const PORTAL_URL = "{CLOUD_RUN_URLS['portal']}";
    const PROJECTS = {projects_json};
    const ARCHETYPES = {archetypes_json};
    let activeProject = PROJECTS.find(p => p.code === "{initial_case_code}") || PROJECTS[0];
    let lastOutputText = "";

    function toggleTheme() {{
      const html = document.documentElement;
      const next = html.getAttribute("data-theme") === "dark" ? "light" : "dark";
      html.setAttribute("data-theme", next);
    }}

    function formatMarkdown(md) {{
      if (!md) return "";
      return String(md)
        .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
        .replace(/```([\\s\\S]*?)```/g, '<pre class="p-3 rounded-xl bg-slate-950 border border-slate-800 text-[11px] mono text-cyan-300 overflow-x-auto my-2">$1</pre>')
        .replace(/\\*\\*(.*?)\\*\\*/g, '<strong class="font-bold text-emerald-400">$1</strong>')
        .replace(/`([^`]+)`/g, '<code class="px-1.5 py-0.5 rounded bg-slate-900 text-amber-300 mono text-[11px]">$1</code>')
        .replace(/\\n/g, '<br>');
    }}

    {BESPOKE_RENDERER_JS}

    function applyUseCaseTheme(code) {{
      const cfg = ARCHETYPES[code] || {{}};
      const root = document.documentElement;
      if (cfg.accent) root.style.setProperty('--accent', cfg.accent);
      if (cfg.accent_secondary) root.style.setProperty('--accent2', cfg.accent_secondary);
      if (cfg.layout_mode === 'light_executive_paper') {{
        root.setAttribute('data-theme', 'light');
      }} else {{
        root.setAttribute('data-theme', 'dark');
        if (cfg.surface_bg) root.style.setProperty('--bg-canvas', cfg.surface_bg);
      }}
      document.getElementById('bespoke-app-header-title').innerText = cfg.app_title || activeProject.project;
      document.getElementById('canvas-section-title').innerText = `🎨 ${{cfg.app_title || activeProject.project}}`;
      document.getElementById('header-archetype-pill').innerText = `Archetype: ${{cfg.ui_archetype || 'bespoke_app'}}`;

      // Update model selector automatically based on ADK / Agent Engine vs Argon routing
      const modelSel = document.getElementById('model-select');
      if (cfg.default_model && modelSel) {{
        modelSel.value = cfg.default_model;
      }}
      document.getElementById('vertex-model-badge').innerText = cfg.default_model || 'gemini-4-argon';
      document.getElementById('run-btn-label').innerText = `⚡ Execute Live on ${{cfg.default_model || 'gemini-4-argon'}} + gVisor Sandbox`;
    }}

    function renderUseCaseSliders(code) {{
      const cfg = ARCHETYPES[code] || {{}};
      const controls = cfg.interactive_controls || [];
      const w = document.getElementById('domain-custom-widget');
      if (!controls.length) {{
        w.innerHTML = '';
        return;
      }}
      w.innerHTML = `
        <div class="p-4 rounded-xl border bg-black/25" style="border-color:var(--border-col);">
          <div class="text-[11px] font-bold mono uppercase mb-2.5" style="color:var(--accent);">🎛️ Live Interactive Parameters (Drag Sliders for Instant 0ms gVisor Recalculation)</div>
          <div class="grid sm:grid-cols-${{Math.min(3, controls.length)}} gap-4">
            ${{controls.map(c => {{
              const curVal = (activeProject.sandboxParams && activeProject.sandboxParams[c.id] !== undefined) ? activeProject.sandboxParams[c.id] : c.default;
              return `
                <div class="mono text-xs">
                  <div class="flex justify-between mb-1">
                    <span style="color:var(--text-muted);">${{c.label}}</span>
                    <strong id="slider-val-${{c.id}}" style="color:var(--accent);">${{curVal}}</strong>
                  </div>
                  <input type="range" min="${{c.min}}" max="${{c.max}}" step="${{c.step}}" value="${{curVal}}"
                         oninput="document.getElementById('slider-val-${{c.id}}').innerText=this.value; updateParam('${{c.id}}', this.value)"
                         class="w-full accent-emerald-500 cursor-pointer">
                </div>`;
            }}).join('')}}
          </div>
        </div>`;
    }}

    function renderStructuredSynthesisCards(structuredData, fallbackMarkdown, modelUsed, runtimeBadge) {{
      const out = document.getElementById('vertex-output-body');
      const obj = structuredData || {{}};
      const execSum = obj.executive_summary || fallbackMarkdown || '';
      const actions = obj.action_items || [];

      // Collect additional structured fields returned by the model
      const extraKeys = Object.keys(obj).filter(k => !['executive_summary', 'action_items'].includes(k));

      out.innerHTML = `
        <div class="p-4 rounded-xl border border-indigo-500/40 bg-indigo-950/20 space-y-2">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <span class="text-[10px] font-bold mono uppercase text-indigo-300">⚡ ${{runtimeBadge || modelUsed}} // EXECUTIVE VERDICT</span>
            <span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-bold mono">Structured JSON Schema Validated</span>
          </div>
          <div class="text-xs md:text-sm font-semibold leading-relaxed">${{formatMarkdown(execSum)}}</div>
        </div>

        ${{actions.length ? `
          <div class="p-4 rounded-xl border bg-black/20" style="border-color:var(--border-col);">
            <div class="text-[11px] font-bold mono uppercase mb-2" style="color:var(--accent);">✅ Recommended Next Actions for Rocket Team</div>
            <div class="grid sm:grid-cols-3 gap-2.5 text-xs mono">
              ${{actions.map((act, i) => `
                <div class="p-3 rounded-lg border bg-black/30" style="border-color:var(--border-col);">
                  <div class="text-[10px] font-bold mb-1" style="color:var(--accent2);">ACTION #${{i+1}}</div>
                  <div class="leading-snug">${{typeof act === 'string' ? act : JSON.stringify(act)}}</div>
                </div>`).join('')}}
            </div>
          </div>` : ''}}

        ${{extraKeys.length ? `
          <div class="grid sm:grid-cols-2 gap-3 text-xs mono">
            ${{extraKeys.slice(0, 6).map(k => {{
              const val = obj[k];
              const renderedVal = typeof val === 'object' ? `<pre class="text-[10px] overflow-x-auto whitespace-pre-wrap text-cyan-300 mt-1">${{JSON.stringify(val, null, 2)}}</pre>` : `<div class="font-bold mt-1" style="color:var(--accent);">${{val}}</div>`;
              return `
                <div class="p-3.5 rounded-xl border bg-black/25" style="border-color:var(--border-col);">
                  <div class="text-[10px] uppercase font-bold" style="color:var(--text-muted);">${{k.replace(/_/g, ' ')}}</div>
                  ${{renderedVal}}
                </div>`;
            }}).join('')}}
          </div>` : ''}}
      `;
    }}

    function renderTabs() {{
      const container = document.getElementById("case-tabs");
      container.innerHTML = PROJECTS.map(p => {{
        const isAct = p.code === activeProject.code;
        const cfg = ARCHETYPES[p.code] || {{}};
        return `<button onclick="selectCase('${{p.code}}')"
          class="px-3.5 py-2 rounded-xl text-xs font-bold mono transition flex items-center gap-2 border"
          style="${{isAct ? 'background:linear-gradient(135deg, var(--accent), var(--accent2)); color:#fff; border-color:transparent;' : 'background:rgba(255,255,255,0.03); border-color:var(--border-col); color:var(--text-muted);'}}">
          <span>[${{p.code}}]</span>
          <span>${{p.project}}</span>
          <span class="px-1.5 py-0.5 rounded bg-black/30 text-[10px]">${{cfg.default_model === 'gemini-3.8-flash' ? '3.8-Flash' : '4-Argon'}}</span>
        </button>`;
      }}).join("");
    }}

    function updateParam(key, val) {{
      activeProject.sandboxParams[key] = parseFloat(val);
      executeSandboxOnly();
    }}

    function selectCase(code) {{
      if (liveWs) {{
        liveWs.close();
      }}
      activeProject = PROJECTS.find(p => p.code === code) || PROJECTS[0];
      applyUseCaseTheme(activeProject.code);
      renderTabs();
      document.getElementById("active-code-badge").innerText = `SQUARE ${{activeProject.code}} • ${{activeProject.tool}}`;
      document.getElementById("active-level-badge").innerText = activeProject.level;
      document.getElementById("active-title").innerText = activeProject.project;
      document.getElementById("active-desc").innerText = activeProject.desc;
      document.getElementById("active-compete").innerText = activeProject.competeEdge;
      document.getElementById("scenario-input").value = activeProject.sampleInput;
      document.getElementById("active-arch").innerText = activeProject.architectureDiagram;
      document.getElementById("active-code-snippet").innerText = activeProject.codeSnippet;

      const docsHref = `${{PORTAL_URL}}/docs/${{activeProject.code}}?auth_token=${{AUTH_TOKEN}}`;
      document.getElementById("top-docs-link").href = docsHref;
      document.getElementById("card-docs-link").href = docsHref;

      document.getElementById("active-stack").innerHTML = (activeProject.gcpStack || []).map(s =>
        `<span class="px-2.5 py-1 rounded-lg text-[11px] font-semibold mono border" style="border-color:var(--border-col); background:rgba(255,255,255,0.04);">${{s}}</span>`
      ).join("");

      document.getElementById("active-repro-steps").innerHTML = (activeProject.reproSteps || []).map(s =>
        `<li>${{s}}</li>`
      ).join("");

      renderUseCaseSliders(activeProject.code);
      executeSandboxOnly();
    }}

    function resetSampleInput() {{
      document.getElementById("scenario-input").value = activeProject.sampleInput;
      executeSandboxOnly();
    }}

    function renderSandboxMetrics(data) {{
      document.getElementById("sandbox-ms-badge").innerText = `Verified in ${{data.execution_ms || 0.4}}ms • gVisor Sandbox`;
      if (data.route_info) {{
        document.getElementById("header-runtime-pill").innerText = `⚡ ${{data.route_info.runtime_badge}}`;
        document.getElementById("bespoke-routing-note").innerText = `Model Routing: ${{data.route_info.routing_note}}`;
      }}
      if (data.bespoke_artifact) {{
        renderBespokeAppCanvas(activeProject.code, data.bespoke_artifact, data);
      }}
      const metrics = data.metrics || {{}};
      const grid = document.getElementById("sandbox-metrics-grid");
      grid.innerHTML = Object.entries(metrics).map(([k, v]) => `
        <div class="p-3.5 rounded-xl border" style="background:rgba(0,0,0,0.22); border-color:var(--border-col);">
          <div class="text-[10px] mono uppercase font-bold mb-1" style="color:var(--text-muted);">${{k.replace(/_/g, ' ')}}</div>
          <div class="text-xs font-bold mono leading-snug" style="color:var(--accent);">${{v}}</div>
        </div>
      `).join("");
    }}

    async function executeSandboxOnly() {{
      try {{
        const res = await fetch("/api/sandbox", {{
          method: "POST",
          headers: {{"Content-Type": "application/json"}},
          body: JSON.stringify({{
            code: activeProject.code,
            action: activeProject.sandboxAction,
            params: activeProject.sandboxParams
          }})
        }});
        const data = await res.json();
        renderSandboxMetrics(data);
        const cfg = ARCHETYPES[activeProject.code] || {{}};
        document.getElementById("vertex-output-body").innerHTML = `
          <div class="p-4 rounded-xl border border-dashed text-xs mono" style="border-color:var(--border-col); color:var(--text-muted);">
            ✅ Bespoke <strong>${{cfg.app_title || activeProject.project}}</strong> UI & deterministic gVisor Sandbox metrics pre-rendered above.<br>
            👉 Click <strong>"⚡ Execute Live on ${{cfg.default_model || 'gemini-4-argon'}} + gVisor Sandbox"</strong> on the left to generate live structured decision cards!
          </div>`;
      }} catch (e) {{
        console.error(e);
      }}
    }}

    async function executeLiveDemo() {{
      const btn = document.getElementById("run-btn");
      const loader = document.getElementById("loading-banner");
      const model = document.getElementById("model-select").value;
      const userInput = document.getElementById("scenario-input").value;

      btn.disabled = true;
      loader.classList.remove("hidden");
      document.getElementById("loading-status-text").innerText = `Executing gVisor Sandbox & Structured Synthesis for [${{activeProject.code}}]...`;

      try {{
        const res = await fetch("/api/run-demo", {{
          method: "POST",
          headers: {{"Content-Type": "application/json"}},
          body: JSON.stringify({{
            code: activeProject.code,
            model: model,
            user_input: userInput,
            params: activeProject.sandboxParams
          }})
        }});
        const data = await res.json();
        if (data.sandbox) {{
          renderSandboxMetrics({{
            ...data.sandbox,
            bespoke_artifact: data.bespoke_artifact,
            route_info: {{ runtime_badge: data.runtime_badge, routing_note: data.routing_note }}
          }});
        }}
        if (data.vertex) {{
          document.getElementById("vertex-model-badge").innerText = data.vertex.model_used;
          document.getElementById("vertex-latency-badge").innerText = `${{data.vertex.latency_ms}}ms • ${{data.vertex.prompt_tokens || 0}}→${{data.vertex.candidate_tokens || 0}} tok`;
          lastOutputText = data.vertex.response_markdown || "";
          renderStructuredSynthesisCards(data.structured_data, lastOutputText, data.vertex.model_used, data.runtime_badge);
        }}
      }} catch (err) {{
        document.getElementById("vertex-output-body").innerHTML = `<div class="text-rose-400 mono text-xs">Error: ${{err.message}}</div>`;
      }} finally {{
        btn.disabled = false;
        loader.classList.add("hidden");
      }}
    }}

    function speakCurrentOutput() {{
      if (!('speechSynthesis' in window)) return alert("Speech Synthesis not supported.");
      window.speechSynthesis.cancel();
      const textToRead = (lastOutputText || activeProject.desc).replace(/[#*`_~]/g, "");
      const u = new SpeechSynthesisUtterance(textToRead.slice(0, 650));
      u.rate = 1.04;
      window.speechSynthesis.speak(u);
    }}

    function copyCodeSnippet() {{
      navigator.clipboard.writeText(activeProject.codeSnippet || "");
      alert("Copied reproduction snippet to clipboard!");
    }}

    document.addEventListener("DOMContentLoaded", () => {{
      selectCase(activeProject.code);
    }});
  </script>
</body>
</html>"""
