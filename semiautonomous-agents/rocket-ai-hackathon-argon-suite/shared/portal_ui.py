# -*- coding: utf-8 -*-
"""Redesigned Rocket AI Hackathon Flagship Portal (Gemini 4 Argon + Gemini Enterprise + Antigravity Edition)
and Dedicated Step-by-Step Reproduction Documentation Blueprint Pages (/docs/<code>)."""

import json
from shared.auth_and_vertex import get_recommended_model_for_square
from shared.bespoke_apps import get_bespoke_config
from shared.catalog_data import (
    ACCOUNT_RESEARCH_DOSSIER,
    ALL_DOMAINS,
    CLOUD_RUN_URLS,
    GLOSSARY_SERVICES,
    KEYNOTE_PRESENTATION,
    PROJECTS_BY_CODE,
    TRANSLATOR_SERVICES,
)


def render_docs_page_html(code: str, auth_token: str) -> str:
    """Renders the full step-by-step reproduction documentation blueprint for a specific square (or master index)."""
    p = PROJECTS_BY_CODE.get(code)
    if not p:
        p = PROJECTS_BY_CODE["1.4"]

    all_codes_nav = "".join(
        f'<a href="/docs/{c}?auth_token={auth_token}" class="px-2.5 py-1 rounded-lg text-xs font-bold mono border transition '
        f'{"bg-rose-600 text-white border-rose-500" if c == p["code"] else "bg-slate-900 text-slate-300 border-slate-800 hover:border-slate-600"}">'
        f'{c}</a>'
        for c in PROJECTS_BY_CODE.keys()
    )

    stack_badges = "".join(
        f'<span class="px-3 py-1 rounded-lg text-xs font-bold mono bg-indigo-500/15 text-indigo-300 border border-indigo-500/30">{s}</span>'
        for s in p.get("gcpStack", [])
    )

    steps_html = "".join(
        f'<li class="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 text-sm text-slate-200 leading-relaxed">'
        f'<strong class="text-rose-400 mono mr-2">STEP {idx + 1}:</strong> {step}</li>'
        for idx, step in enumerate(p.get("reproSteps", []))
    )

    demo_link = f"{p['demo_service_url']}&auth_token={auth_token}"

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Reproduction Blueprint [{p['code']}] {p['project']} | Rocket AI Hackathon Docs</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    body {{ font-family: 'Inter', sans-serif; background-color: #050811; color: #F8FAFC; }}
    .mono {{ font-family: 'JetBrains Mono', monospace; }}
  </style>
</head>
<body class="min-h-screen flex flex-col">
  <header class="bg-slate-950/90 border-b border-slate-800 px-6 py-4 sticky top-0 z-40 backdrop-blur-md">
    <div class="max-w-6xl mx-auto flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <a href="/?auth_token={auth_token}" class="px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-xs font-bold mono text-slate-200">
          ← Back to Rocket Portal
        </a>
        <span class="text-xs mono text-rose-400 font-bold">📘 OFFICIAL REPRODUCTION BLUEPRINT // SQUARE [{p['code']}]</span>
      </div>
      <div class="flex flex-wrap items-center gap-2">
        <a href="https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023" target="_blank"
           class="px-3 py-2 rounded-xl text-xs font-bold text-purple-200 bg-purple-950/70 border border-purple-500/40 hover:bg-purple-900 mono">
          ✨ Real Gemini Enterprise UI ↗
        </a>
        <a href="https://github.com/jchavezar/vertex-ai-samples/tree/main/semiautonomous-agents/rocket-ai-hackathon-argon-suite" target="_blank"
           class="px-3 py-2 rounded-xl text-xs font-bold text-emerald-200 bg-emerald-950/70 border border-emerald-500/40 hover:bg-emerald-900 mono">
          🐙 GitHub Repo & Skills ↗
        </a>
        <a href="{demo_link}" target="_blank"
           class="px-4 py-2 rounded-xl text-xs font-bold text-white shadow-lg bg-gradient-to-r from-rose-600 to-indigo-600 hover:opacity-95 mono">
          🚀 Launch Bespoke Demo [{p['code']}] ↗
        </a>
      </div>
    </div>
  </header>

  <main class="max-w-6xl mx-auto px-6 py-8 flex-grow w-full space-y-8">
    <!-- Square Jump Bar -->
    <div class="bg-slate-900/70 border border-slate-800 rounded-2xl p-4">
      <div class="text-[11px] font-bold uppercase mono text-slate-400 mb-2">Jump to Any of the 33 Hackathon Use Case Blueprints:</div>
      <div class="flex flex-wrap gap-1.5">{all_codes_nav}</div>
    </div>

    <!-- Title Banner -->
    <div class="bg-gradient-to-br from-slate-900 via-rose-950/25 to-indigo-950/30 border border-rose-500/30 rounded-2xl p-8 shadow-2xl">
      <div class="flex flex-wrap items-center gap-2.5 mb-3">
        <span class="px-3 py-1 rounded-full text-xs font-bold mono bg-rose-500/20 text-rose-300 border border-rose-500/30">SQUARE {p['code']}</span>
        <span class="px-3 py-1 rounded-full text-xs font-bold mono bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">{p['level']}</span>
        <span class="text-xs font-semibold text-slate-400 mono">{p['dept_full']}</span>
      </div>
      <h1 class="text-3xl md:text-4xl font-extrabold text-white tracking-tight mb-3">{p['project']}</h1>
      <p class="text-base text-slate-300 leading-relaxed mb-5">{p['desc']}</p>
      <div class="flex flex-wrap gap-2 mb-6">{stack_badges}</div>

      <div class="grid md:grid-cols-2 gap-4 pt-4 border-t border-slate-800/80 text-xs">
        <div class="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
          <div class="font-bold text-amber-400 mono uppercase mb-1">🎯 Competitive Win-Back vs. AWS / Anthropic / Sierra:</div>
          <p class="text-slate-300 leading-relaxed">{p['competeEdge']}</p>
        </div>
        <div class="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
          <div class="font-bold text-cyan-400 mono uppercase mb-1">☁️ Dedicated Cloud Run Demo Endpoint:</div>
          <p class="text-slate-300 mono break-all mb-2">{p['demo_service_url']}</p>
          <span class="text-[11px] text-slate-400 mono">Shared Login: User <code>rocket</code> / Pass <code>Argon2026!</code></span>
        </div>
      </div>
    </div>

    <!-- Architecture & Steps Grid -->
    <div class="grid lg:grid-cols-12 gap-8">
      <div class="lg:col-span-5 space-y-6">
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6">
          <h2 class="text-sm font-extrabold uppercase mono text-rose-400 mb-3">1. Reference Architecture Diagram</h2>
          <pre class="text-[11px] mono bg-slate-950 p-4 rounded-xl border border-slate-800 text-slate-200 overflow-x-auto leading-snug">{p['architectureDiagram']}</pre>
        </div>

        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6">
          <h2 class="text-sm font-extrabold uppercase mono text-emerald-400 mb-3">2. Sample Rocket Test Payload</h2>
          <pre class="text-xs mono bg-slate-950 p-4 rounded-xl border border-slate-800 text-emerald-300 whitespace-pre-wrap leading-relaxed">{p['sampleInput']}</pre>
        </div>
      </div>

      <div class="lg:col-span-7 space-y-6">
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6">
          <h2 class="text-sm font-extrabold uppercase mono text-indigo-400 mb-4">3. Step-by-Step GCP Reproduction Guide</h2>
          <ol class="space-y-3">{steps_html}</ol>
        </div>

        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6">
          <div class="flex items-center justify-between mb-3">
            <h2 class="text-sm font-extrabold uppercase mono text-cyan-400">4. Copy-Pasteable Implementation Code (`gemini-4-argon`)</h2>
            <button onclick="navigator.clipboard.writeText(document.getElementById('code-block').innerText); alert('Copied code!');"
                    class="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-bold mono text-white">
              📋 Copy Code
            </button>
          </div>
          <pre id="code-block" class="text-xs mono bg-slate-950 p-4 rounded-xl border border-slate-800 text-cyan-300 overflow-x-auto leading-relaxed">{p['codeSnippet']}</pre>
        </div>

        <div class="bg-slate-900 border border-emerald-500/40 rounded-2xl p-6">
          <div class="flex items-center justify-between mb-3">
            <h2 class="text-sm font-extrabold uppercase mono text-emerald-400">5. Reusable Antigravity / Jetski Skill (`SKILL.md`) & Model Routing Policy</h2>
            <span class="px-2.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[11px] font-bold mono">Bespoke UI Archetype + Model Router</span>
          </div>
          <p class="text-xs text-slate-300 mb-3 leading-relaxed">
            Drop this <code>SKILL.md</code> into <code>.agent/skills/rocket-square-{p['code'].lower().replace('.', '_')}/SKILL.md</code> so any Antigravity agent reproduces the bespoke UI archetype, structured JSON schema, and model routing automatically:
          </p>
          <pre class="text-xs mono bg-slate-950 p-4 rounded-xl border border-slate-800 text-emerald-300 overflow-x-auto leading-relaxed mb-4">---
name: rocket-square-{p['code'].lower().replace('.', '_')}
description: Reproduces Rocket AI Hackathon Square [{p['code']}] ({p['project']}) with bespoke UI archetype, gVisor sandbox verifier, and Vertex AI / ADK model routing.
---

# Square [{p['code']}]: {p['project']}
- **Bespoke UI Archetype:** `{get_bespoke_config(p['code'])['ui_archetype']}` (`{get_bespoke_config(p['code'])['app_title']}`)
- **Model Routing Rule:** `{get_recommended_model_for_square(p['code'])['runtime_badge']}` ({get_recommended_model_for_square(p['code'])['routing_note']})
- **Structured Output Contract:** {get_bespoke_config(p['code'])['output_schema_hint']}
- **Real Gemini Enterprise Engine:** `projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023`</pre>
        </div>

        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6">
          <h2 class="text-sm font-extrabold uppercase mono text-amber-400 mb-3">6. One-Command Cloud Run Deployment & System Prompt</h2>
          <p class="text-xs text-slate-400 mb-2">System Instruction passed to <code>projects/vtxdemos/locations/global/publishers/google/models/gemini-4-argon</code>:</p>
          <pre class="text-xs mono bg-slate-950 p-3.5 rounded-xl border border-slate-800 text-slate-300 whitespace-pre-wrap mb-4">{p['systemPrompt']}</pre>
          <p class="text-xs text-slate-400 mb-2">Deploy this microservice to Cloud Run with Private Auth Gate:</p>
          <pre class="text-xs mono bg-slate-950 p-3.5 rounded-xl border border-slate-800 text-amber-300 overflow-x-auto">git clone https://github.com/google/adk-samples.git
gcloud run deploy {ALL_DOMAINS[0]['service_name']} \\
  --source . \\
  --project vtxdemos \\
  --region us-central1 \\
  --set-env-vars="SERVICE_MODE={p['dept_id']},ROCKET_AUTH_USER=rocket,ROCKET_AUTH_PASS=Argon2026!"</pre>
        </div>
      </div>
    </div>
  </main>
</body>
</html>"""


def render_portal_html(auth_token: str) -> str:
    """Renders the redesigned Rocket x Google Cloud AI Hackathon Portal (Gemini 4 Argon Edition)."""
    domains_json = json.dumps(ALL_DOMAINS)
    translator_json = json.dumps(TRANSLATOR_SERVICES)
    glossary_json = json.dumps(GLOSSARY_SERVICES)
    keynote_json = json.dumps(KEYNOTE_PRESENTATION)
    account_json = json.dumps(ACCOUNT_RESEARCH_DOSSIER)
    urls_json = json.dumps(CLOUD_RUN_URLS)

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Rocket AI Hackathon | Gemini 4 Argon, Gemini Enterprise & Antigravity Command Hub</title>
  <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🚀</text></svg>">
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-canvas: #040711;
      --bg-card: #0C1222;
      --border-col: #1E293B;
      --text-main: #F8FAFC;
      --text-muted: #94A3B8;
    }}
    [data-theme="light"] {{
      --bg-canvas: #F8FAFC;
      --bg-card: #FFFFFF;
      --border-col: #E2E8F0;
      --text-main: #09090B;
      --text-muted: #475569;
    }}
    body {{
      background-color: var(--bg-canvas);
      color: var(--text-main);
      font-family: 'Inter', sans-serif;
      transition: background-color 0.2s ease, color 0.2s ease;
    }}
    .card-surface {{
      background-color: var(--bg-card);
      border: 1px solid var(--border-col);
    }}
    .mono {{ font-family: 'JetBrains Mono', monospace; }}
    .tab-content {{ display: none; }}
    .tab-content.active {{ display: block; animation: fadeIn 0.22s ease-out; }}
    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(6px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes pulse-ring {{
      0% {{ transform: scale(0.95); opacity: 0.8; }}
      50% {{ transform: scale(1.14); opacity: 0.3; }}
      100% {{ transform: scale(0.95); opacity: 0.8; }}
    }}
    .animate-pulse-ring {{ animation: pulse-ring 2.4s cubic-bezier(0.4, 0, 0.6, 1) infinite; }}
    .speaking-glow {{ box-shadow: 0 0 38px rgba(225, 29, 72, 0.65), 0 0 18px rgba(99, 102, 241, 0.5); }}
    .shrinking-shining-ink {{
      width: 18px; height: 18px; border-radius: 50%;
      background: radial-gradient(circle at 30% 30%, #ffffff, #E11D48, #6366F1);
      animation: inkPulse 1.3s ease-in-out infinite;
      display: inline-block;
    }}
    @keyframes inkPulse {{
      0%, 100% {{ transform: scale(1); opacity: 0.95; }}
      50% {{ transform: scale(0.55); opacity: 0.5; }}
    }}
  </style>
</head>
<body class="min-h-screen flex flex-col antialiased">

  <!-- TOP EXECUTIVE TELEMETRY BAR -->
  <div class="bg-slate-950 border-b border-slate-800/90 px-4 py-2 text-[11px] mono text-slate-300">
    <div class="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-2">
      <div class="flex flex-wrap items-center gap-2.5">
        <span class="px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30 font-bold">🚀 ROCKET BAY HALLOWEEN HACKATHON (OCT 28–29 • DETROIT & CHENNAI)</span>
        <span class="px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 font-bold">⚡ POWERED BY GEMINI 4 ARGON (`gemini-4-argon`)</span>
        <span class="hidden xl:inline text-slate-400">1-Hr Gemini Enterprise (Sobi/Spark) + 1-Hr Google Antigravity 2.0</span>
      </div>
      <div class="flex items-center gap-3">
        <span class="text-emerald-400 font-bold">🔒 Private Session Active (User: rocket)</span>
        <button onclick="toggleTheme()" class="px-2.5 py-0.5 rounded bg-slate-900 border border-slate-700 text-slate-200 hover:bg-slate-800">☀️/🌙 Theme</button>
        <a href="/logout" class="text-rose-400 hover:underline">Logout</a>
      </div>
    </div>
  </div>

  <!-- HERO HEADER -->
  <header class="relative overflow-hidden py-10 px-6 bg-gradient-to-br from-slate-950 via-rose-950/35 to-indigo-950/30 border-b border-rose-500/25">
    <div class="max-w-7xl mx-auto">

      <div class="grid lg:grid-cols-12 gap-8 items-center mb-8">
        <!-- Left 7 Cols: Title & Value Prop -->
        <div class="lg:col-span-7 text-left space-y-4">
          <div class="inline-flex flex-wrap items-center gap-2 px-3.5 py-1 rounded-full text-xs font-bold mono bg-rose-500/15 text-rose-300 border border-rose-500/30">
            <span>🔥 NEW GEMINI 4 ARGON EDITION</span>
            <span>•</span>
            <span>8 SEPARATED PRIVATE CLOUD RUN SERVICES</span>
          </div>
          <h1 class="text-4xl md:text-6xl font-black tracking-tight bg-gradient-to-r from-white via-rose-200 to-indigo-300 bg-clip-text text-transparent leading-tight">
            Rocket x Google Cloud AI Command Hub
          </h1>
          <p class="text-sm md:text-base text-slate-300 leading-relaxed max-w-2xl">
            Purpose-built for <strong>Rocket Companies</strong> (<strong>Rocket Mortgage</strong>, <strong>Redfin</strong>, <strong>Mr. Cooper</strong>, <strong>Rocket Money</strong>, and <strong>Rocket Close</strong>). Explore <strong>33 live, interactive demos</strong> running on <strong>7 separated Cloud Run UI/UX architectures</strong> powered by <strong>Gemini 4 Argon</strong>, <strong>Gemini Enterprise (Sobi / Spark)</strong>, and <strong>Google Antigravity 2.0</strong>—with full reproduction blueprints for every square.
          </p>

          <!-- 7 Direct Separated Cloud Run Domain App Launch Buttons -->
          <div class="pt-2">
            <div class="text-[11px] font-bold uppercase mono text-rose-300 mb-2">
              ⚡ Direct Launch: 7 Separated Cloud Run Domain Demo Apps (Each with Bespoke UI/UX):
            </div>
            <div class="flex flex-wrap gap-2">
              <a href="{CLOUD_RUN_URLS['sales']}?auth_token={auth_token}" target="_blank" class="px-3 py-1.5 rounded-xl text-xs font-bold mono bg-emerald-500/15 hover:bg-emerald-500/25 text-emerald-300 border border-emerald-500/30 transition">1. Origination Terminal ↗</a>
              <a href="{CLOUD_RUN_URLS['ops']}?auth_token={auth_token}" target="_blank" class="px-3 py-1.5 rounded-xl text-xs font-bold mono bg-sky-500/15 hover:bg-sky-500/25 text-sky-300 border border-sky-500/30 transition">2. Underwriting Lightbox ↗</a>
              <a href="{CLOUD_RUN_URLS['servicing']}?auth_token={auth_token}" target="_blank" class="px-3 py-1.5 rounded-xl text-xs font-bold mono bg-teal-500/15 hover:bg-teal-500/25 text-teal-300 border border-teal-500/30 transition">3. Mr. Cooper CX Studio ↗</a>
              <a href="{CLOUD_RUN_URLS['marketing']}?auth_token={auth_token}" target="_blank" class="px-3 py-1.5 rounded-xl text-xs font-bold mono bg-rose-500/15 hover:bg-rose-500/25 text-rose-300 border border-rose-500/30 transition">4. Redfin Creative Hub ↗</a>
              <a href="{CLOUD_RUN_URLS['risk']}?auth_token={auth_token}" target="_blank" class="px-3 py-1.5 rounded-xl text-xs font-bold mono bg-amber-500/15 hover:bg-amber-500/25 text-amber-300 border border-amber-500/30 transition">5. CFPB/TRID Vault ↗</a>
              <a href="{CLOUD_RUN_URLS['sdlc']}?auth_token={auth_token}" target="_blank" class="px-3 py-1.5 rounded-xl text-xs font-bold mono bg-green-500/15 hover:bg-green-500/25 text-green-300 border border-green-500/30 transition">6. Antigravity & CodeMender IDE ↗</a>
              <a href="{CLOUD_RUN_URLS['moonshots']}?auth_token={auth_token}" target="_blank" class="px-3 py-1.5 rounded-xl text-xs font-bold mono bg-purple-500/15 hover:bg-purple-500/25 text-purple-300 border border-purple-500/30 transition">7. Argon Moonshot Lab ↗</a>
            </div>
          </div>
        </div>

        <!-- Right 5 Cols: Interactive Astra 2.0 Gemini 3.8 Live Video Avatar + Extended Thinking + Omniscient Overlay -->
        <div class="lg:col-span-5">
          <div class="bg-slate-900/95 border border-rose-500/40 rounded-2xl p-5 shadow-2xl backdrop-blur-md">
            <div class="flex items-start gap-4">
              <!-- 9:16 Live Video Avatar Stage (704x1280 H.264 + 24kHz AAC via MSE) -->
              <div class="relative shrink-0">
                <div id="avatar-ring" class="absolute -inset-1.5 rounded-2xl bg-gradient-to-tr from-rose-500/35 via-indigo-500/30 to-cyan-500/35 animate-pulse-ring"></div>
                <div id="avatar-orb" onclick="window.toggleAstraLiveSession()" title="Click to Start/Stop Gemini 3.8 Live Video Avatar Session" class="cursor-pointer relative w-28 h-40 rounded-2xl bg-gradient-to-b from-slate-800 to-slate-950 border border-rose-500/40 flex items-center justify-center overflow-hidden shadow-xl transition-all duration-300">
                  <!-- Real 24 FPS Gemini 3.8 Live Video Avatar Stream -->
                  <video id="astra-live-video" playsinline autoplay class="w-full h-full object-cover hidden"></video>
                  <!-- Live User Camera / Screen PIP Preview -->
                  <video id="astra-vision-pip" playsinline autoplay muted class="absolute bottom-1.5 right-1.5 w-11 h-14 object-cover rounded-lg border border-cyan-400 shadow-lg hidden z-20"></video>
                  <!-- SVG Fallback / Idle Avatar -->
                  <svg id="astra-svg-avatar" class="w-full h-full p-1.5" viewBox="0 0 100 125" xmlns="http://www.w3.org/2000/svg">
                    <rect width="100" height="125" rx="14" fill="#0F172A" />
                    <g id="avatar-shoulders">
                      <path d="M 10,122 Q 12,92 30,83 L 70,83 Q 88,92 90,122 Z" fill="#E11D48" />
                      <path d="M 38,83 L 50,93 L 62,83" stroke="#fbcfe8" stroke-width="2" fill="#fbcfe8" />
                      <text x="50" y="106" font-size="6.8" font-family="monospace" font-weight="900" text-anchor="middle" fill="#ffffff">LIVE AVATAR</text>
                      <text x="50" y="116" font-size="5.5" font-family="monospace" font-weight="700" text-anchor="middle" fill="#fecdd3">24 FPS • 24kHz</text>
                    </g>
                    <g id="avatar-head-group">
                      <path d="M 22,64 C 15,27 32,5 50,5 C 68,5 85,27 78,64" fill="#1e1b4b" />
                      <circle cx="23" cy="52" r="5" fill="#fbcfe8" />
                      <circle cx="77" cy="52" r="5" fill="#fbcfe8" />
                      <path d="M 26,47 C 26,26 74,27 74,47 C 74,70 50,85 50,85 C 50,85 26,70 26,47 Z" fill="#fed7aa" />
                      <path d="M 23,40 Q 28,14 50,17 Q 72,14 77,40 Q 72,27 50,28 Q 28,27 23,40 Z" fill="#312e81" />
                      <g id="avatar-eyes">
                        <ellipse cx="39" cy="48" rx="3.5" ry="2.2" fill="#ffffff" />
                        <circle cx="39" cy="48" r="2.2" fill="#1e1b4b" />
                        <ellipse cx="61" cy="48" rx="3.5" ry="2.2" fill="#ffffff" />
                        <circle cx="61" cy="48" r="2.2" fill="#1e1b4b" />
                      </g>
                      <path d="M 34,43 Q 39,41 43,43.5" stroke="#1e1b4b" stroke-width="1.5" stroke-linecap="round" fill="none" />
                      <path d="M 66,43 Q 61,41 57,43.5" stroke="#1e1b4b" stroke-width="1.5" stroke-linecap="round" fill="none" />
                      <path d="M 48,53 Q 50,57 52,53" stroke="#f43f5e" stroke-width="1.2" stroke-linecap="round" fill="none" />
                      <path id="avatar-mouth-lip" d="M 43,67 Q 50,68 57,67" stroke="#be185d" stroke-width="2.5" stroke-linecap="round" fill="none" />
                    </g>
                  </svg>
                </div>
              </div>

              <div class="flex-grow min-w-0">
                <div class="flex flex-wrap items-center justify-between gap-1.5 mb-1.5">
                  <div class="flex flex-wrap items-center gap-1.5">
                    <h3 class="text-base font-extrabold text-white">Astra 2.0</h3>
                    <span class="text-[10px] mono px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/30">3.8 Live Avatar + Omniscient</span>
                    <span id="avatar-badge" class="text-[10px] mono px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300">24 FPS + 24kHz Ready</span>
                  </div>
                  <button onclick="window.openAstraCommandOverlay()" class="px-2.5 py-1 rounded-lg bg-gradient-to-r from-rose-600 to-indigo-600 hover:from-rose-500 hover:to-indigo-500 text-white text-[11px] font-extrabold mono shadow flex items-center gap-1">
                    <span>💬 Open Command Chat</span>
                    <span class="px-1 rounded bg-black/30 text-[9px]">⌘K</span>
                  </button>
                </div>

                <!-- Avatar Persona + Live Mode + Voice Selectors -->
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-1.5 mb-2">
                  <select id="astra-avatar-select" onchange="window.reconnectAstraIfLive()" class="bg-slate-950 border border-rose-500/40 rounded-lg px-2 py-1 text-[11px] text-amber-300 font-bold">
                    <option value="Kira" selected>🎥 Avatar: Kira (Exec Advisor)</option>
                    <option value="Ingrid">🎥 Avatar: Ingrid (Architect)</option>
                    <option value="Vera">🎥 Avatar: Vera (Risk/UW Lead)</option>
                    <option value="Sam">🎥 Avatar: Sam (FDE Director)</option>
                    <option value="Jay">🎥 Avatar: Jay (Staff SDLC)</option>
                    <option value="Paul">🎥 Avatar: Paul (Treasury Macro)</option>
                    <option value="Kai">🎥 Avatar: Kai (3D Concierge)</option>
                    <option value="Ben">🎥 Avatar: Ben (Dev Advocate)</option>
                    <option value="Carmen">🎥 Avatar: Carmen (Bilingual)</option>
                    <option value="Leo">🎥 Avatar: Leo (FinOps)</option>
                    <option value="Piper">🎥 Avatar: Piper (Product UI)</option>
                    <option value="off">🎙️ Audio Only (24kHz Native)</option>
                  </select>
                  <select id="astra-live-mode" onchange="window.reconnectAstraIfLive()" class="bg-slate-950 border border-slate-700 rounded-lg px-2 py-1 text-[11px] text-rose-300 font-semibold">
                    <option value="gemini-3.8-live" selected>Gemini 3.8 Live (24 FPS + 24kHz)</option>
                    <option value="gemini-3.8-live-extended-thinking">3.8 Live Extended Thinking</option>
                  </select>
                  <select id="astra-voice-select" onchange="window.reconnectAstraIfLive()" class="bg-slate-950 border border-slate-700 rounded-lg px-2 py-1 text-[11px] text-cyan-300 font-semibold">
                    <option value="Aoede" selected>Voice: Aoede (Warm HD)</option>
                    <option value="Kore">Voice: Kore (Executive HD)</option>
                    <option value="Puck">Voice: Puck (Dynamic HD)</option>
                    <option value="Fenrir">Voice: Fenrir (Deep HD)</option>
                  </select>
                </div>

                <div id="astra-live-transcript" class="text-xs text-slate-200 leading-relaxed bg-slate-950/90 border border-slate-800 rounded-xl p-2.5 max-h-24 overflow-y-auto">
                  "Welcome Rocket builders! I now run on <strong>Gemini 3.8 Live with 24 FPS Live Video Avatars</strong> and have complete knowledge of all <strong>33 demos</strong>, our <strong>Oct 16 Showcase</strong> & <strong>Oct 28–29 Detroit/Chennai Hackathon</strong> dates. Click <strong>Start Live Avatar</strong> or open my <strong>Command Chat (⌘K)</strong>!"
                </div>
                <div id="astra-hero-matched-cards" class="mt-1.5 flex flex-wrap gap-1.5"></div>
              </div>
            </div>

            <!-- Live Video Avatar, Mic, Camera, Screen & Barge-In Controls -->
            <div class="mt-3 pt-3 border-t border-slate-800 flex flex-wrap items-center gap-1.5">
              <button onclick="window.toggleAstraLiveSession()" id="btn-voice-tour" class="px-3 py-1.5 rounded-xl text-xs font-bold bg-rose-600 hover:bg-rose-500 text-white transition shadow flex items-center gap-1.5">
                <span id="voice-icon">🎥</span>
                <span id="voice-label">Start Live Video Avatar</span>
              </button>
              <button onclick="window.toggleAstraMic()" id="btn-astra-mic" class="px-2.5 py-1.5 rounded-xl text-xs font-bold bg-slate-800 hover:bg-slate-700 text-cyan-300 border border-cyan-500/30 transition flex items-center gap-1">
                <span>🎤</span>
                <span id="astra-mic-label">16kHz Mic</span>
              </button>
              <button onclick="window.toggleAstraCamera()" id="btn-astra-cam" title="Share Webcam so Astra's Live Avatar sees you or documents" class="px-2.5 py-1.5 rounded-xl text-xs font-bold bg-slate-800 hover:bg-slate-700 text-emerald-300 border border-emerald-500/30 transition">
                📷 Cam
              </button>
              <button onclick="window.toggleAstraScreen()" id="btn-astra-screen" title="Share Screen so Astra's Live Avatar sees your app or code" class="px-2.5 py-1.5 rounded-xl text-xs font-bold bg-slate-800 hover:bg-slate-700 text-indigo-300 border border-indigo-500/30 transition">
                🖥️ Screen
              </button>
              <button onclick="window.interruptAstraNow()" id="btn-astra-interrupt" class="px-2.5 py-1.5 rounded-xl text-xs font-bold bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40 transition">
                ✋ Interrupt
              </button>
              <button onclick="window.toggleAstraMute()" id="btn-astra-mute" class="px-2 py-1.5 rounded-xl text-xs font-bold bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition">
                🔊
              </button>
            </div>

            <!-- Instant Barge-In Chips & Text/Voice Input -->
            <div class="mt-2.5 flex flex-wrap gap-1.5">
              <button onclick="window.sendAstraBargeIn('What is our schedule for the Oct 16 Product Showcase and Oct 28–29 Detroit & Chennai Hackathon, and which demos should we highlight?')" class="text-[11px] px-2.5 py-1 rounded-lg bg-slate-800/90 hover:bg-rose-950/60 text-slate-300 hover:text-rose-200 border border-slate-700 transition">
                📅 Oct 16 & Oct 28–29 Dates + Top Demos
              </button>
              <button onclick="window.sendAstraBargeIn('Hold on—give me the 20-second executive pitch for why Rocket beats Sierra AI and AWS Bedrock with Gemini 3.8 Live Avatar and Gemini 4 Argon!')" class="text-[11px] px-2.5 py-1 rounded-lg bg-slate-800/90 hover:bg-rose-950/60 text-slate-300 hover:text-rose-200 border border-slate-700 transition">
                ⚡ Why We Beat Sierra AI & AWS
              </button>
            </div>
            <div class="mt-2 flex gap-1.5">
              <input id="astra-barge-input" type="text" placeholder="Ask or interrupt Astra 2.0 Live Avatar about any of the 33 use cases..." onkeydown="if(event.key==='Enter')window.sendAstraBargeIn()" class="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-white focus:border-rose-500 focus:outline-none">
              <button onclick="window.sendAstraBargeIn()" class="px-3 py-1.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold">
                Speak →
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- PRIMARY NAVIGATION TABS (11 TABS) -->
      <nav class="flex flex-wrap justify-center gap-1.5 bg-slate-900/95 p-2 rounded-2xl border border-slate-800 shadow-2xl">
        <button onclick="switchMainTab('depts')" id="btn-depts" class="main-tab-btn px-3.5 py-2.5 rounded-xl text-xs font-bold transition bg-rose-600 text-white shadow">
          🏢 1. Use Case Catalog & Live Demos (33)
        </button>
        <button onclick="switchMainTab('arena')" id="btn-arena" class="main-tab-btn px-3.5 py-2.5 rounded-xl text-xs font-bold transition text-amber-300 hover:text-white hover:bg-slate-800 border border-amber-500/30">
          ⚔️ 2. Live Model Arena (Argon vs. 3.8 Flash)
        </button>
        <button onclick="switchMainTab('matrix')" id="btn-matrix" class="main-tab-btn px-3.5 py-2.5 rounded-xl text-xs font-bold transition text-cyan-300 hover:text-white hover:bg-slate-800 border border-cyan-500/30">
          🎨 3. 33 UI Archetypes & Runtime Matrix
        </button>
        <button onclick="switchMainTab('account')" id="btn-account" class="main-tab-btn px-3.5 py-2.5 rounded-xl text-xs font-bold transition text-slate-300 hover:text-white hover:bg-slate-800">
          🎯 4. Rocket Account Research & AWS Win-Back
        </button>
        <button onclick="switchMainTab('keynote')" id="btn-keynote" class="main-tab-btn px-3.5 py-2.5 rounded-xl text-xs font-bold transition text-slate-300 hover:text-white hover:bg-slate-800">
          🎤 5. 2-Hr Presentation (1h GE + 1h Antigravity)
        </button>
        <button onclick="switchMainTab('alldocs')" id="btn-alldocs" class="main-tab-btn px-3.5 py-2.5 rounded-xl text-xs font-bold transition text-slate-300 hover:text-white hover:bg-slate-800">
          📘 6. Reproduction Docs (All 33 Blueprints)
        </button>
        <button onclick="switchMainTab('translator')" id="btn-translator" class="main-tab-btn px-3.5 py-2.5 rounded-xl text-xs font-bold transition text-slate-300 hover:text-white hover:bg-slate-800">
          🔄 7. Tool Translator (Claude/Sierra → GCP)
        </button>
        <button onclick="switchMainTab('levels')" id="btn-levels" class="main-tab-btn px-3.5 py-2.5 rounded-xl text-xs font-bold transition text-slate-300 hover:text-white hover:bg-slate-800">
          📚 8. L100/L200/L300 Tracks
        </button>
        <button onclick="switchMainTab('glossary')" id="btn-glossary" class="main-tab-btn px-3.5 py-2.5 rounded-xl text-xs font-bold transition text-slate-300 hover:text-white hover:bg-slate-800">
          📖 9. Service Glossary
        </button>
        <button onclick="switchMainTab('resources')" id="btn-resources" class="main-tab-btn px-3.5 py-2.5 rounded-xl text-xs font-bold transition text-slate-300 hover:text-white hover:bg-slate-800">
          🎓 10. Codelabs & Videos
        </button>
        <button onclick="switchMainTab('cocreate')" id="btn-cocreate" class="main-tab-btn px-3.5 py-2.5 rounded-xl text-xs font-bold transition text-slate-300 hover:text-white hover:bg-slate-800">
          💡 11. Co-Create & Argon Pitch Coach
        </button>
      </nav>
    </div>
  </header>

  <!-- INLINE QUICK-RUN ARGON MODAL -->
  <div id="quickrun-modal" class="fixed inset-0 bg-slate-950/85 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
    <div class="card-surface rounded-2xl max-w-4xl w-full p-6 shadow-2xl max-h-[90vh] overflow-y-auto space-y-4">
      <div class="flex items-center justify-between border-b border-slate-800 pb-3">
        <div>
          <span id="qr-badge" class="text-xs font-bold mono text-rose-400"></span>
          <h3 id="qr-title" class="text-xl font-extrabold text-white"></h3>
        </div>
        <button onclick="closeQuickRun()" class="px-3 py-1 rounded-lg bg-slate-800 text-slate-300 hover:text-white mono text-sm">✕</button>
      </div>
      <div id="qr-loading" class="hidden p-4 rounded-xl bg-slate-900 border border-rose-500/40 flex items-center gap-3">
        <span class="shrinking-shining-ink"></span>
        <span class="text-xs font-bold mono text-rose-300">Executing gVisor Sandbox & Calling Vertex AI gemini-4-argon...</span>
      </div>
      <div id="qr-sandbox-grid" class="grid sm:grid-cols-2 gap-3"></div>
      <div id="qr-vertex-out" class="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs md:text-sm leading-relaxed space-y-2"></div>
      <div class="flex flex-wrap justify-between items-center gap-3 pt-3 border-t border-slate-800">
        <a id="qr-docs-btn" href="#" target="_blank" class="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-bold mono text-cyan-300">📘 Open Full Reproduction Blueprint ↗</a>
        <a id="qr-demo-btn" href="#" target="_blank" class="px-5 py-2.5 rounded-xl bg-gradient-to-r from-rose-600 to-indigo-600 text-xs font-bold mono text-white shadow-lg">🚀 Open Dedicated Domain Cloud Run App ↗</a>
      </div>
    </div>
  </div>

  <!-- FLOATING DOCK LAUNCHER FOR ASTRA 2.0 OMNISCIENT OVERLAY (⌘K) -->
  <div id="astra-floating-dock" class="fixed bottom-5 right-5 z-40 flex items-center gap-2">
    <button onclick="window.openAstraCommandOverlay()" class="group px-4 py-3 rounded-2xl bg-gradient-to-r from-rose-600 via-indigo-600 to-cyan-600 hover:from-rose-500 hover:to-indigo-500 text-white font-extrabold text-xs shadow-2xl border border-white/20 flex items-center gap-2.5 transition-all hover:scale-105">
      <span class="relative flex h-3 w-3">
        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-300 opacity-75"></span>
        <span class="relative inline-flex rounded-full h-3 w-3 bg-emerald-400"></span>
      </span>
      <span>🎥 Ask Astra 2.0 • All 33 Demos, Dates & Live Avatar</span>
      <span class="px-1.5 py-0.5 rounded bg-black/40 mono text-[10px] text-amber-300">⌘K</span>
    </button>
  </div>

  <!-- ASTRA 2.0 OMNISCIENT COMMAND & LIVE AVATAR OVERLAY WINDOW -->
  <div id="astra-command-overlay" class="fixed inset-0 bg-slate-950/85 backdrop-blur-xl z-50 hidden flex items-center justify-center p-3 md:p-6">
    <div class="bg-slate-900 border border-rose-500/40 rounded-3xl max-w-6xl w-full h-[88vh] shadow-2xl flex flex-col overflow-hidden">
      <!-- Top Header Bar -->
      <div class="px-5 py-3.5 bg-slate-950 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3">
        <div class="flex items-center gap-2.5">
          <span class="px-2.5 py-1 rounded-lg bg-rose-500/20 text-rose-300 border border-rose-500/40 text-xs font-extrabold mono">
            🎥 ASTRA 2.0 OMNISCIENT ARCHITECT
          </span>
          <span class="text-xs text-slate-300 font-semibold hidden sm:inline">
            Full Access: All 33 Live Demos • Oct 16 Showcase & Oct 28–29 Detroit/Chennai Hackathon • Gemini 3.8 Live 24 FPS Avatar
          </span>
        </div>
        <div class="flex items-center gap-2">
          <select id="astra-chat-model" class="bg-slate-900 border border-slate-700 rounded-xl px-2.5 py-1.5 text-xs text-amber-300 font-bold mono">
            <option value="gemini-4-argon" selected>🧠 Model: Gemini 4 Argon (Frontier Reasoning)</option>
            <option value="gemini-3.8-flash">⚡ Model: Gemini 3.8 Flash (Sub-Second Speed)</option>
          </select>
          <label class="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-slate-900 border border-slate-700 text-xs text-cyan-300 font-semibold cursor-pointer">
            <input type="checkbox" id="astra-auto-speak" class="accent-rose-500">
            <span>🔊 Auto-Speak Replies</span>
          </label>
          <button onclick="window.closeAstraCommandOverlay()" class="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-rose-600 text-slate-200 hover:text-white text-xs font-bold mono transition">
            ✕ ESC
          </button>
        </div>
      </div>

      <!-- Main Split Body: Left 4 Cols (Live Video Avatar + Instant 33-Demo Finder) | Right 8 Cols (Multi-Turn Omniscient Chat) -->
      <div class="grid lg:grid-cols-12 flex-1 min-h-0 overflow-hidden">
        <!-- Left 4 Cols: Live 24 FPS Avatar Stage + Vision + Instant Filter -->
        <div class="lg:col-span-4 bg-slate-950/90 border-r border-slate-800 p-4 flex flex-col gap-3 overflow-y-auto">
          <div class="rounded-2xl bg-slate-900 border border-rose-500/30 p-3 space-y-2.5">
            <div class="flex items-center justify-between">
              <span class="text-[11px] font-extrabold uppercase mono text-rose-300">🎥 Gemini 3.8 Live Avatar Stage</span>
              <span id="overlay-avatar-status" class="text-[10px] mono px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300">Ready</span>
            </div>
            <!-- Video Container inside Overlay -->
            <div class="relative w-full h-52 rounded-xl bg-slate-950 border border-slate-800 overflow-hidden flex items-center justify-center">
              <video id="astra-overlay-video" playsinline autoplay muted class="w-full h-full object-cover hidden"></video>
              <div id="astra-overlay-placeholder" class="text-center p-4 space-y-1.5">
                <div class="text-2xl">🎥</div>
                <div class="text-xs font-bold text-white">Gemini 3.8 Live Video Avatar (24 FPS)</div>
                <p class="text-[11px] text-slate-400">Select an Avatar Persona in the header or click <strong>Start Live Avatar</strong> below for face-to-face lip-synced conversation.</p>
              </div>
            </div>
            <div class="flex flex-wrap gap-1.5">
              <button onclick="window.toggleAstraLiveSession()" class="flex-1 px-2.5 py-1.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold">
                🎥 Start / Stop Avatar
              </button>
              <button onclick="window.toggleAstraMic()" class="px-2.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-cyan-300 border border-cyan-500/30 text-xs font-bold">
                🎤 Mic
              </button>
              <button onclick="window.toggleAstraCamera()" class="px-2.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-emerald-300 border border-emerald-500/30 text-xs font-bold">
                📷 Cam
              </button>
              <button onclick="window.toggleAstraScreen()" class="px-2.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-indigo-300 border border-indigo-500/30 text-xs font-bold">
                🖥️ Screen
              </button>
            </div>
          </div>

          <!-- Instant 0ms 33-Demo Keyword Finder -->
          <div class="rounded-2xl bg-slate-900 border border-slate-800 p-3 space-y-2">
            <div class="text-[11px] font-extrabold uppercase mono text-cyan-300">🔍 Instant 33-Demo Finder (0ms)</div>
            <input id="astra-instant-filter" type="text" oninput="window.filterAstraCatalogInstant(this.value)" placeholder="Filter by 'Schedule C', 'TRID', 'Refi', 'COBOL', 'Redfin'..." class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-white focus:border-cyan-400 focus:outline-none">
            <div id="astra-instant-results" class="space-y-1.5 max-h-48 overflow-y-auto"></div>
          </div>

          <!-- Quick Curated Prompts for Dates, Use Cases & Executive Pitch -->
          <div class="space-y-1.5">
            <div class="text-[10px] font-extrabold uppercase mono text-slate-400">⚡ Curated Executive & Date Queries</div>
            <button onclick="window.sendAstraOverlayChat('Give me the complete schedule for our Oct 16 Product Showcase and Oct 28–29 Detroit & Chennai 24-Hour Halloween AI Hackathon, including key Rocket & Google stakeholders and which demos to show in Hour 1 vs Hour 2.')" class="w-full text-left px-3 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs text-slate-200 transition">
              📅 <strong>Oct 16 & Oct 28–29 Dates:</strong> Full Schedule, Stakeholders & Hour 1 vs Hour 2 Demo Plan
            </button>
            <button onclick="window.sendAstraOverlayChat('Which specific demos should I show for Self-Employed Underwriting, TRID Closing Disclosures, and Appraisal Anomalies?')" class="w-full text-left px-3 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs text-slate-200 transition">
              📑 <strong>Underwriting & TRID:</strong> Compare Squares [2.1], [2.2], [2.4], and [2.5]
            </button>
            <button onclick="window.sendAstraOverlayChat('Show me the best demos combining Redfin ($1.75B), Mr. Cooper ($9.4B / $2.1T servicing), and Rocket Money.')" class="w-full text-left px-3 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs text-slate-200 transition">
              🏠 <strong>Redfin + Mr. Cooper + Rocket Money:</strong> Cross-Brand Synergy Demos
            </button>
            <button onclick="window.sendAstraOverlayChat('Which demos highlight Google Antigravity 2.0, DeepMind CodeMender, and the 5 Moonshots?')" class="w-full text-left px-3 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs text-slate-200 transition">
              🛠️ <strong>Antigravity, CodeMender & Moonshots:</strong> Compare [6.1]–[6.5] & [M.1]–[M.5]
            </button>
          </div>
        </div>

        <!-- Right 8 Cols: Multi-Turn Omniscient Chat & Interactive Use-Case Action Cards -->
        <div class="lg:col-span-8 flex flex-col min-h-0 bg-slate-900/60">
          <div id="astra-overlay-chat-log" class="flex-1 p-5 overflow-y-auto space-y-4 text-xs md:text-sm">
            <!-- Initial Welcome Message with Interactive Cards -->
            <div class="p-4 rounded-2xl bg-slate-950/90 border border-rose-500/30 space-y-2">
              <div class="flex items-center justify-between">
                <span class="font-extrabold text-rose-400 mono text-xs">ASTRA 2.0 • OMNISCIENT ROCKET ARCHITECT</span>
                <span class="text-[11px] mono text-slate-400">33 Demos • Oct 16 & Oct 28–29 Ready</span>
              </div>
              <p class="text-slate-200 leading-relaxed">
                Hello! I have complete, real-time access to all <strong>33 Rocket Companies demos (`1.1` through `M.5`)</strong>, their <strong>authentic real-world UI archetypes</strong>, our <strong>Oct 16 Product Showcase</strong> and <strong>Oct 28–29 Detroit & Chennai 24-Hour Halloween Hackathon</strong> agenda, and the full <strong>Redfin ($1.75B) + Mr. Cooper ($9.4B / $2.1T UPB)</strong> account dossier.
              </p>
              <p class="text-slate-300 text-xs">
                Ask me for any specific use case, persona, or technical requirement below—I will recommend the exact squares and give you <strong>1-click Launch, Live Model Arena Race, and 24kHz Audio Pitch cards</strong> right inside our chat!
              </p>
            </div>
          </div>

          <!-- Chat Input Bar -->
          <div class="p-4 bg-slate-950 border-t border-slate-800 flex items-center gap-2">
            <input id="astra-overlay-input" type="text" placeholder="Ask Astra 2.0 anything (e.g., 'Which demos are best for self-employed borrowers or Spanish speakers?', 'What is our Oct 28 agenda?')..." onkeydown="if(event.key==='Enter')window.sendAstraOverlayChat()" class="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-xs md:text-sm text-white focus:border-rose-500 focus:outline-none">
            <button onclick="window.sendAstraOverlayChat()" id="btn-astra-chat-send" class="px-5 py-3 rounded-xl bg-gradient-to-r from-rose-600 to-indigo-600 hover:from-rose-500 hover:to-indigo-500 text-white font-extrabold text-xs md:text-sm shadow-lg transition">
              Ask Astra 2.0 →
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- MAIN CONTAINER -->
  <main class="max-w-7xl mx-auto px-6 py-10 flex-grow w-full">

    <!-- TAB 1: 33-SQUARE DEPARTMENT PROJECT CATALOG -->
    <section id="tab-depts" class="tab-content active space-y-8">
      <!-- FDE Executive Upgrade Showcase vs. Static Sales Page -->
      <div class="rounded-2xl p-5 bg-gradient-to-r from-slate-900 via-indigo-950/50 to-slate-900 border border-indigo-500/40 shadow-2xl">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div>
            <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold mono bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
              🏆 FDE PRODUCTION ARCHITECTURE UPGRADE (VS. STATIC SALES PROTOTYPE)
            </span>
            <h2 class="text-xl md:text-2xl font-extrabold text-white mt-1.5">
              33 Authentic Real-World Industry Web Apps • 8 Private Cloud Run Services • Real Gemini 3.8 Live 24kHz Audio
            </h2>
            <p class="text-xs text-slate-300 mt-1">
              Unlike static prompt mockups, every square below launches its own <strong>domain-authentic industry web UI</strong> (Encompass Light LOS, Salesforce CRM, Redfin Marketplace, Intuit TurboTax CPA Workbook, DocuSign Portal, Chase Bank Ledger, Westlaw Legal Brief, GitHub Light PR Diff, Braun Audio Studio, FT Forensic Paper) with <strong>real 24kHz Gemini 3.8 Live voice</strong>, <strong>Gemini Enterprise <code>streamAssist</code></strong>, and <strong>gVisor math sandboxes</strong>.
            </p>
          </div>
          <div class="flex flex-wrap gap-2 shrink-0">
            <button onclick="switchMainTab('arena')" class="px-4 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-extrabold text-xs mono shadow-lg transition">
              ⚔️ Open Live Model Arena (Argon vs. 3.8 Flash)
            </button>
            <button onclick="switchMainTab('matrix')" class="px-4 py-2.5 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-200 border border-cyan-500/40 font-bold text-xs mono transition">
              🎨 View 33 Unique UI Archetypes Table
            </button>
          </div>
        </div>
      </div>

      <div class="flex flex-wrap justify-center gap-2" id="dept-buttons"></div>
      <div id="dept-banner" class="rounded-2xl p-6 border border-rose-500/30 bg-gradient-to-r from-slate-900 via-rose-950/30 to-indigo-950/30"></div>
      <div id="dept-projects" class="grid md:grid-cols-2 gap-6"></div>
    </section>

    <!-- TAB 2: LIVE SIDE-BY-SIDE MODEL ARENA (GEMINI 4 ARGON VS. GEMINI 3.8 FLASH VS. AWS BEDROCK) -->
    <section id="tab-arena" class="tab-content space-y-8">
      <div class="text-center max-w-3xl mx-auto">
        <span class="px-3 py-1 rounded-full text-xs font-bold mono bg-amber-500/20 text-amber-300 border border-amber-500/40">
          ⚔️ REAL-TIME VERTEX AI PARALLEL BENCHMARK ARENA
        </span>
        <h2 class="text-3xl font-extrabold mt-3 mb-2">Live Head-to-Head Race: Gemini 4 Argon vs. Gemini 3.8 Flash</h2>
        <p class="text-sm" style="color:var(--text-muted);">
          Pick any of the 33 Rocket Companies use cases below and fire a <strong>simultaneous live Vertex AI request</strong> to both <code>gemini-4-argon</code> (Frontier Deep Reasoning) and <code>gemini-3.8-flash</code> (Sub-Second High-Throughput ADK Runtime), complete with deterministic gVisor math verification and AWS Bedrock / Claude TCO comparison.
        </p>
      </div>

      <div class="card-surface rounded-2xl p-6 shadow-2xl space-y-5">
        <div class="flex flex-wrap items-center gap-3 justify-between">
          <div class="flex-1 min-w-[260px]">
            <label class="text-xs font-bold mono text-slate-400 block mb-1">SELECT ROCKET USE CASE TO BENCHMARK:</label>
            <select id="arena-case-select" class="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-sm font-bold text-white"></select>
          </div>
          <div class="flex items-center gap-2 pt-4">
            <button onclick="window.runLiveModelArena()" id="btn-run-arena" class="px-6 py-3 rounded-xl bg-gradient-to-r from-rose-600 via-amber-500 to-emerald-500 text-slate-950 font-black text-xs mono shadow-xl hover:opacity-95 transition">
              🚀 Fire Parallel Race (Argon vs. 3.8 Flash)
            </button>
            <button onclick="window.speakArenaVerdict(this)" class="px-4 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 border border-cyan-500/40 text-cyan-300 font-bold text-xs mono transition">
              🔊 Speak Verdict (Gemini 3.8 Live)
            </button>
          </div>
        </div>

        <!-- Deterministic gVisor Math Baseline Strip -->
        <div id="arena-sandbox-strip" class="grid sm:grid-cols-4 gap-3"></div>

        <!-- Side-by-Side Live Race Columns -->
        <div class="grid lg:grid-cols-2 gap-6">
          <!-- Column A: Gemini 4 Argon -->
          <div class="rounded-2xl bg-slate-950 border-2 border-rose-500/50 p-5 space-y-3">
            <div class="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <span class="text-[10px] font-bold mono px-2 py-0.5 rounded bg-rose-500/20 text-rose-300">FRONTIER DEEP REASONING</span>
                <h3 class="text-lg font-extrabold text-white mt-1">gemini-4-argon (Global Endpoint)</h3>
              </div>
              <div class="text-right">
                <div class="text-[10px] mono text-slate-400">LIVE LATENCY</div>
                <div id="arena-argon-ms" class="text-xl font-black mono text-rose-400">— ms</div>
              </div>
            </div>
            <div id="arena-argon-out" class="text-xs md:text-sm text-slate-200 leading-relaxed whitespace-pre-wrap max-h-96 overflow-y-auto">
              Click "🚀 Fire Parallel Race" above to execute live against Vertex AI gemini-4-argon...
            </div>
          </div>

          <!-- Column B: Gemini 3.8 Flash -->
          <div class="rounded-2xl bg-slate-950 border-2 border-emerald-500/50 p-5 space-y-3">
            <div class="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <span class="text-[10px] font-bold mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300">HIGH-THROUGHPUT ADK RUNTIME</span>
                <h3 class="text-lg font-extrabold text-white mt-1">gemini-3.8-flash (Global Endpoint)</h3>
              </div>
              <div class="text-right">
                <div class="text-[10px] mono text-slate-400">LIVE LATENCY</div>
                <div id="arena-flash-ms" class="text-xl font-black mono text-emerald-400">— ms</div>
              </div>
            </div>
            <div id="arena-flash-out" class="text-xs md:text-sm text-slate-200 leading-relaxed whitespace-pre-wrap max-h-96 overflow-y-auto">
              Click "🚀 Fire Parallel Race" above to execute live against Vertex AI gemini-3.8-flash...
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- TAB 3: 33 UNIQUE UI ARCHETYPES & GCP RUNTIME MATRIX -->
    <section id="tab-matrix" class="tab-content space-y-8">
      <div class="text-center max-w-3xl mx-auto">
        <span class="px-3 py-1 rounded-full text-xs font-bold mono bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
          🎨 33 DISTINCT REAL-WORLD INDUSTRY WEB DESIGNS
        </span>
        <h2 class="text-3xl font-extrabold mt-3 mb-2">Architecture, GCP Engine & Real-World UI Design Matrix</h2>
        <p class="text-sm" style="color:var(--text-muted);">
          Every demo has been individually crafted after a real-world industry web application—spanning Encompass Light LOS, Salesforce Lightning CRM, Redfin Marketplace, Intuit TurboTax, DocuSign, Chase Banking, Westlaw Legal Paper, GitHub Light PR Review, Braun Tactile Audio Studio, and Goldman Sachs Macro Research.
        </p>
      </div>

      <div class="overflow-x-auto card-surface rounded-2xl shadow-2xl">
        <table class="w-full text-left border-collapse text-xs">
          <thead>
            <tr class="border-b border-slate-800 bg-slate-950/95 text-[11px] uppercase mono text-slate-400">
              <th class="p-3.5">Square</th>
              <th class="p-3.5">Use Case Title</th>
              <th class="p-3.5">Real-World Industry UI Design Archetype</th>
              <th class="p-3.5">Primary GCP Engine & Audio</th>
              <th class="p-3.5">Actions</th>
            </tr>
          </thead>
          <tbody id="matrix-archetype-tbody" class="divide-y divide-slate-800/70"></tbody>
        </table>
      </div>
    </section>

    <!-- TAB 2: ROCKET ACCOUNT RESEARCH & AWS/ANTHROPIC/SIERRA WIN-BACK WAR ROOM -->
    <section id="tab-account" class="tab-content space-y-8">
      <div class="text-center max-w-3xl mx-auto">
        <span class="px-3 py-1 rounded-full text-xs font-bold mono bg-rose-500/15 text-rose-300 border border-rose-500/30">
          🔍 DEEP ACCOUNT INTELLIGENCE // [INT RKT]
        </span>
        <h2 class="text-3xl font-extrabold mt-3 mb-2">Rocket Companies Ecosystem & Competitive Win-Back Architecture</h2>
        <p class="text-sm" style="color:var(--text-muted);">
          How Google Cloud (<strong>Gemini 4 Argon + Gemini Enterprise Sobi/Spark + Google Antigravity 2.0</strong>) unifies Rocket's end-to-end homeownership flywheel and displaces AWS Bedrock, Anthropic Claude Code, and Sierra AI.
        </p>
      </div>

      <!-- 5-Stage Rocket Flywheel -->
      <div class="card-surface rounded-2xl p-6 shadow-xl">
        <h3 class="text-lg font-extrabold mono text-rose-400 mb-4">1. The 5-Pillar Rocket Homeownership Flywheel (Post-Redfin & Mr. Cooper Acquisitions)</h3>
        <div class="grid md:grid-cols-5 gap-4" id="flywheel-grid"></div>
      </div>

      <!-- Head-to-Head Win-Back Matrix -->
      <div class="card-surface rounded-2xl p-6 shadow-xl">
        <h3 class="text-lg font-extrabold mono text-indigo-400 mb-4">2. Displacing AWS Bedrock, Anthropic Claude Code & Sierra AI at Rocket</h3>
        <div class="grid md:grid-cols-2 gap-6" id="winback-grid"></div>
      </div>

      <!-- Stakeholders & Event Briefing -->
      <div class="grid md:grid-cols-2 gap-6">
        <div class="card-surface rounded-2xl p-6">
          <h4 class="text-sm font-extrabold uppercase mono text-emerald-400 mb-3">🎯 Rocket Executive Hosts & Champions</h4>
          <ul class="space-y-2.5 text-xs" id="exec-sponsors-list"></ul>
        </div>
        <div class="card-surface rounded-2xl p-6">
          <h4 class="text-sm font-extrabold uppercase mono text-cyan-400 mb-3">🤝 Google Cloud Account & CE Team</h4>
          <ul class="space-y-2.5 text-xs" id="google-team-list"></ul>
        </div>
      </div>
    </section>

    <!-- TAB 3: 2-HOUR KEYNOTE PRESENTATION DECK (1 HR GEMINI ENTERPRISE + 1 HR ANTIGRAVITY) -->
    <section id="tab-keynote" class="tab-content space-y-8">
      <div class="text-center max-w-3xl mx-auto">
        <span class="px-3 py-1 rounded-full text-xs font-bold mono bg-indigo-500/15 text-indigo-300 border border-indigo-500/30">
          🎤 LIVE KEYNOTE RUNBOOK & DEMO LAUNCHER
        </span>
        <h2 class="text-3xl font-extrabold mt-3 mb-2">2-Hour Enablement Presentation: Gemini Enterprise & Google Antigravity</h2>
        <p class="text-sm" style="color:var(--text-muted);">
          Structured 60-minute executive & builder tracks with direct 1-click links into the live Cloud Run demos.
        </p>
      </div>

      <div class="grid lg:grid-cols-2 gap-8" id="keynote-columns"></div>
    </section>

    <!-- TAB 4: MASTER REPRODUCTION DOCUMENTATION HUB (ALL 33 BLUEPRINTS) -->
    <section id="tab-alldocs" class="tab-content space-y-8">
      <div class="text-center max-w-3xl mx-auto">
        <span class="px-3 py-1 rounded-full text-xs font-bold mono bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
          📘 COMPLETE REPRODUCTION DOCUMENTATION INDEX
        </span>
        <h2 class="text-3xl font-extrabold mt-3 mb-2">How to Reproduce Every Demo (All 33 GCP Blueprints)</h2>
        <p class="text-sm" style="color:var(--text-muted);">
          Click any square below to open its full standalone documentation page with architecture diagrams, Vertex AI <code>gemini-4-argon</code> code snippets, Antigravity MCP configs, and Cloud Run deployment commands.
        </p>
      </div>

      <div class="max-w-xl mx-auto">
        <input type="text" id="docs-search" oninput="renderAllDocsTable()" placeholder="Search 33 blueprints by code (e.g. 1.4, 2.4, 6.1), tool, or keyword..."
               class="w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-sm text-white mono focus:outline-none focus:border-rose-500">
      </div>

      <div class="overflow-x-auto card-surface rounded-2xl shadow-2xl">
        <table class="w-full text-left border-collapse text-xs">
          <thead>
            <tr class="border-b border-slate-800 bg-slate-950/90 text-[11px] uppercase mono text-slate-400">
              <th class="p-4">Square</th>
              <th class="p-4">Domain / Cloud Run Service</th>
              <th class="p-4">Use Case Title & GCP Stack</th>
              <th class="p-4">Reproduction Blueprint</th>
              <th class="p-4">Live Cloud Run Demo</th>
            </tr>
          </thead>
          <tbody id="alldocs-tbody" class="divide-y divide-slate-800/70"></tbody>
        </table>
      </div>
    </section>

    <!-- TAB 5: TOOL TRANSLATOR -->
    <section id="tab-translator" class="tab-content space-y-8">
      <div class="text-center max-w-3xl mx-auto">
        <span class="px-3 py-1 rounded-full text-xs font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30">
          ⚡ Fast Mental Model for Rocket Builders (O365 & AWS Mapped)
        </span>
        <h2 class="text-3xl font-extrabold mt-3 mb-2">Tool Translator: AWS Bedrock, Claude, Sierra AI & ChatGPT → Google Cloud</h2>
      </div>
      <div class="flex flex-wrap justify-center gap-2">
        <button onclick="filterTranslator('all')" id="trans-btn-all" class="trans-btn px-4 py-2 rounded-lg text-xs font-bold bg-rose-600 text-white">🔍 Show All (11 Services)</button>
        <button onclick="filterTranslator('sierra')" id="trans-btn-sierra" class="trans-btn px-4 py-2 rounded-lg text-xs font-bold bg-slate-800 text-slate-300">🎧 Sierra AI Equivalents</button>
        <button onclick="filterTranslator('claude')" id="trans-btn-claude" class="trans-btn px-4 py-2 rounded-lg text-xs font-bold bg-slate-800 text-slate-300">🤖 Claude / AWS Bedrock Equivalents</button>
        <button onclick="filterTranslator('chatgpt')" id="trans-btn-chatgpt" class="trans-btn px-4 py-2 rounded-lg text-xs font-bold bg-slate-800 text-slate-300">💬 ChatGPT / Copilot Equivalents</button>
      </div>
      <div class="overflow-x-auto card-surface rounded-2xl shadow-2xl">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="border-b border-slate-800 bg-slate-950/80 text-[11px] uppercase tracking-wider text-slate-400">
              <th class="p-4 font-bold text-rose-400">Google Hackathon Service</th>
              <th class="p-4 font-bold text-slate-200 w-1/4">What It Does</th>
              <th class="p-4 font-bold text-indigo-400 w-1/4">🎯 Rocket Use Cases</th>
              <th class="p-4 font-bold text-emerald-400">ChatGPT / OpenAI</th>
              <th class="p-4 font-bold text-amber-400">Claude / AWS Bedrock</th>
              <th class="p-4 font-bold text-cyan-400">Sierra / Microsoft</th>
            </tr>
          </thead>
          <tbody id="translator-tbody" class="divide-y divide-slate-800/70 text-sm"></tbody>
        </table>
      </div>
    </section>

    <!-- TAB 6: L100 / L200 / L300 AUDIENCE TRACKS -->
    <section id="tab-levels" class="tab-content space-y-8">
      <div class="flex flex-wrap justify-center gap-3">
        <button onclick="filterByLevel('L100')" id="lvl-btn-L100" class="lvl-btn px-5 py-2.5 rounded-xl text-sm font-bold bg-emerald-600 text-white shadow">🌱 L100 Business & Prompting</button>
        <button onclick="filterByLevel('L200')" id="lvl-btn-L200" class="lvl-btn px-5 py-2.5 rounded-xl text-sm font-bold bg-slate-800 text-slate-300">🛠️ L200 Low-Code & Studio</button>
        <button onclick="filterByLevel('L300')" id="lvl-btn-L300" class="lvl-btn px-5 py-2.5 rounded-xl text-sm font-bold bg-slate-800 text-slate-300">🚀 L300 Full-Stack, Antigravity & Argon</button>
      </div>
      <div id="level-projects" class="grid md:grid-cols-2 gap-6"></div>
    </section>

    <!-- TAB 7: SERVICE GLOSSARY -->
    <section id="tab-glossary" class="tab-content space-y-8">
      <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6" id="glossary-grid"></div>
    </section>

    <!-- TAB 8: CODELABS, GITHUB & VIDEOS -->
    <section id="tab-resources" class="tab-content space-y-8">
      <div class="grid md:grid-cols-2 gap-8">
        <div class="card-surface rounded-2xl overflow-hidden shadow-xl">
          <div class="aspect-video bg-slate-950">
            <iframe class="w-full h-full" src="https://www.youtube.com/embed/videoseries?list=PLBgogxgQVM9sBm7dy-KTntt1yPVNzOZ4H" title="Liftoff with Google Antigravity" frameborder="0" allowfullscreen></iframe>
          </div>
          <div class="p-6">
            <span class="text-xs font-bold mono text-purple-400">🚀 FEATURED PLAYLIST • L200–L300</span>
            <h3 class="text-xl font-bold mt-1 mb-2">Liftoff with Google Antigravity</h3>
            <p class="text-xs text-slate-400 mb-4">Official walkthrough of Google Antigravity agentic IDE workflows, subagents, browser automation, and MCP integrations.</p>
            <a href="https://antigravity.google" target="_blank" class="inline-block px-4 py-2 rounded-lg bg-rose-600 text-white text-xs font-bold">Launch Antigravity ↗</a>
          </div>
        </div>
        <div class="card-surface rounded-2xl overflow-hidden shadow-xl">
          <div class="aspect-video bg-slate-950">
            <iframe class="w-full h-full" src="https://www.youtube.com/embed/lB96_tdvdow" title="Megha Patel Spotlight" frameborder="0" allowfullscreen></iframe>
          </div>
          <div class="p-6">
            <span class="text-xs font-bold mono text-emerald-400">🎙️ FEATURED BRIEFING • ALL LEVELS</span>
            <h3 class="text-xl font-bold mt-1 mb-2">Rocket Hackathon Fast-Start Briefing (Megha Patel)</h3>
            <p class="text-xs text-slate-400 mb-4">4-minute executive walkthrough for Rocket Hackathon builders across Detroit and Chennai.</p>
            <a href="https://github.com/google-gemini/cookbook" target="_blank" class="inline-block px-4 py-2 rounded-lg bg-indigo-600 text-white text-xs font-bold">Open Gemini Cookbook Repo ↗</a>
          </div>
        </div>
      </div>
    </section>

    <!-- TAB 9: CO-CREATE & LIVE GEMINI 4 ARGON PITCH ARCHITECT -->
    <section id="tab-cocreate" class="tab-content space-y-8">
      <div class="max-w-4xl mx-auto card-surface rounded-2xl p-8 shadow-2xl">
        <span class="px-3 py-1 rounded-full text-xs font-bold mono bg-rose-500/15 text-rose-300 border border-rose-500/30">💡 LIVE GEMINI 4 ARGON HACKATHON ARCHITECT</span>
        <h2 class="text-2xl font-extrabold mt-3 mb-2">Pitch Your Rocket Hackathon Idea — Get an Instant Argon Architecture & Outlook Draft</h2>
        <p class="text-xs text-slate-400 mb-6">Describe your team's idea below. Gemini 4 Argon will instantly design your GCP architecture, select the best pre-built Cloud Run template from our 33 squares, and prepare your collaboration email to the Google CE team.</p>
        <div class="grid md:grid-cols-2 gap-4 mb-4">
          <input type="text" id="pitch-name" placeholder="Team Lead Name (e.g. Viraj Sanghvi)" class="bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white">
          <select id="pitch-dept" class="bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white">
            <option>Track 1: Client Experience & Interaction (Retail / Brokers / Voice)</option>
            <option>Track 2: Operational & Back-End Automation (Underwriting / Bankers)</option>
            <option>Track 3: Loan Servicing (Mr. Cooper / Escrow / Recapture)</option>
            <option>Track 4: Creative Innovation & SDLC Wildcard</option>
          </select>
        </div>
        <textarea id="pitch-desc" rows="4" placeholder="Describe your hackathon idea (e.g., 'We want to build an agent that reads Redfin inspection reports and auto-estimates repair credits for Rocket Close...')" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-4 text-sm text-white mb-4"></textarea>
        <div class="flex flex-wrap gap-3">
          <button onclick="generatePitchArchitecture()" class="px-5 py-3 rounded-xl bg-gradient-to-r from-rose-600 to-indigo-600 text-white font-bold text-xs mono shadow-lg">
            ⚡ Generate Instant Architecture with Gemini 4 Argon
          </button>
          <button onclick="submitOutlookPitch()" class="px-5 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-bold text-xs mono">
            📧 Open in O365 Outlook to Google CEs ↗
          </button>
        </div>
        <div id="pitch-argon-output" class="hidden mt-6 p-5 rounded-xl bg-slate-950 border border-indigo-500/40 text-xs md:text-sm leading-relaxed space-y-2"></div>
      </div>
    </section>

  </main>

  <footer class="border-t border-slate-900 py-6 px-6 text-center text-slate-500 text-xs mono">
    <p>© 2026 Rocket x Google Cloud Customer Engineering • Powered by Vertex AI Gemini 4 Argon (`gemini-4-argon`), Gemini Enterprise (Sobi/Spark) & Google Antigravity 2.0</p>
  </footer>

  <script>
    const AUTH_TOKEN = "{auth_token}";
    const DOMAINS = {domains_json};
    const TRANSLATOR = {translator_json};
    const GLOSSARY = {glossary_json};
    const KEYNOTE = {keynote_json};
    const ACCOUNT = {account_json};
    const CLOUD_URLS = {urls_json};

    function toggleTheme() {{
      const html = document.documentElement;
      html.setAttribute("data-theme", html.getAttribute("data-theme") === "dark" ? "light" : "dark");
    }}

    function badgeClass(level) {{
      if (level === "L100") return "bg-emerald-500/15 text-emerald-300 border-emerald-500/30";
      if (level === "L200") return "bg-cyan-500/15 text-cyan-300 border-cyan-500/30";
      if (level === "L300") return "bg-purple-500/15 text-purple-300 border-purple-500/30";
      return "bg-amber-500/15 text-amber-300 border-amber-500/30";
    }}

    const UI_ARCHETYPES = {{
      "1.1": {{ style: "Encompass Light LOS + Gong Call Studio", engine: "ADK + Gemini 3.8 Live 24kHz Multi-Speaker Audio" }},
      "1.2": {{ style: "Salesforce Lightning CRM (Light Cloud Gray)", engine: "Google ADK Multi-Agent + Gemini 3.8 Live Voicemail" }},
      "1.3": {{ style: "Redfin / Airbnb Consumer Marketplace White", engine: "Gemini Enterprise streamAssist + Home Tour Audio" }},
      "1.4": {{ style: "Apple Wallet Light Pre-Approval Pass & Certificate", engine: "Google ADK + gVisor LTV/DTI Sandbox" }},
      "1.5": {{ style: "NerdWallet / Bankrate Editorial Rate Comparison", engine: "Gemini 4 Argon + Breakeven Curve Sandbox" }},
      "2.1": {{ style: "Intuit TurboTax / QuickBooks CPA Tax Workbook", engine: "Google ADK + IRS Form 1084 Add-Back Sandbox" }},
      "2.2": {{ style: "DocuSign / Box 3-Pane Document Clearance Room", engine: "Gemini Enterprise streamAssist + Document AI" }},
      "2.3": {{ style: "Chase / Ally Online Banking Statement Ledger", engine: "Google ADK + BSA/AML 50% Threshold Sandbox" }},
      "2.4": {{ style: "Fannie Mae URAR Form 1004 Buff Appraisal Sheet", engine: "Gemini 4 Argon + 15%/25% Comp Adjustment Sandbox" }},
      "2.5": {{ style: "Deloitte / PwC TRID Audit Reconciliation Workpaper", engine: "Google ADK + 0%/10% TRID Tolerance Sandbox" }},
      "3.1": {{ style: "Mr. Cooper Warm Cream Homeowner Self-Service Portal", engine: "Gemini Enterprise streamAssist + Escrow Sandbox" }},
      "3.2": {{ style: "One Medical / Calm Compassionate Support Center", engine: "Google ADK + CFPB Reg X Waterfall + 3.8 Live Audio" }},
      "3.3": {{ style: "Stripe / Plaid Clean Account Onboarding Wizard", engine: "Google ADK + RESPA Boarding Audit Sandbox" }},
      "3.4": {{ style: "Daylight Consumer Voice & Refi Savings Concierge", engine: "Gemini 3.8 Live + Extended Thinking WebSocket (/ws/live-voice/3.4)" }},
      "4.1": {{ style: "Redfin Property Listing Page + Video Storyboard", engine: "Google ADK + Veo Storyboard + Gemini 3.8 Live Voiceover" }},
      "4.2": {{ style: "Rocket Money / Monarch Consumer Personal Finance App", engine: "Google ADK + Down-Payment Goal Vault Sandbox" }},
      "4.3": {{ style: "NYT Real Estate / Dwell Editorial Magazine Paper", engine: "Gemini Enterprise streamAssist + MSHDA Grant Sandbox" }},
      "4.4": {{ style: "Figma / Notion Light Ad Campaign Review Studio", engine: "Gemini Enterprise streamAssist + ECOA Redline Scanner" }},
      "5.1": {{ style: "Westlaw / Federal Register Archival Legal Paper", engine: "Gemini Enterprise streamAssist + State Bulletin Diff" }},
      "5.2": {{ style: "The Economist / Stata Quantitative Econometrics Report", engine: "Google ADK + EEOC 4/5ths Disparate Impact Sandbox" }},
      "5.3": {{ style: "Vanta / Drata Trust & Vendor Security Portal", engine: "Gemini Enterprise streamAssist + SOC2 Clause Redliner" }},
      "5.4": {{ style: "Official Printable CFPB Form C-1 Legal Notice", engine: "Google ADK + Regulation B Adverse Action Sandbox" }},
      "6.1": {{ style: "GitHub Light Pull Request & Split Diff Review", engine: "Google Antigravity 2.0 + Decimal128 Parity Sandbox" }},
      "6.2": {{ style: "Snyk / GitHub Dependabot Light Security Advisory", engine: "DeepMind CodeMender + SAST/DAST Patch Verifier" }},
      "6.3": {{ style: "Postman / Swagger OpenAPI Light Explorer", engine: "Google Antigravity + OpenAPI Contract Validator" }},
      "6.4": {{ style: "Datadog / PagerDuty Service Health & Postmortem", engine: "Google ADK + AlloyDB Trace Waterfall Sandbox" }},
      "6.5": {{ style: "Google Cloud Console Material 3 Light BigQuery Studio", engine: "Google Antigravity + BigQuery Slot/Cost Optimizer" }},
      "M.1": {{ style: "Dieter Rams Braun / Teenage Engineering Audio Studio", engine: "Gemini 3.8 Live + Extended Thinking WebSocket (/ws/live-voice/M.1)" }},
      "M.2": {{ style: "Financial Times (FT) Salmon Paper Forensic Board", engine: "Gemini 4 Argon + Cross-Loan Entity Fraud Graph" }},
      "M.3": {{ style: "Warm Sunlit Terracotta Bilingual Community Portal", engine: "Gemini 4 Argon + Gemini 3.8 Live Spanish Audio" }},
      "M.4": {{ style: "Architectural Digest Warm Living Room Whiteboard", engine: "Gemini 3.8 Live + Extended Thinking WebSocket (/ws/live-voice/M.4)" }},
      "M.5": {{ style: "Goldman Sachs / Bloomberg Institutional Macro Note", engine: "Gemini 4 Argon + $2.1T Servicing Treasury Sandbox" }}
    }};

    function renderProjectCard(p, deptTitle, deptDemoUrl) {{
      const liveDemoHref = `${{deptDemoUrl || p.demo_service_url}}${{(deptDemoUrl && !deptDemoUrl.includes('?')) ? '?case=' + p.code : ''}}&auth_token=${{AUTH_TOKEN}}`;
      const docsHref = `/docs/${{p.code}}?auth_token=${{AUTH_TOKEN}}`;
      const arch = UI_ARCHETYPES[p.code] || {{ style: "Custom Industry Web UI", engine: "Vertex AI Gemini 4 Argon" }};
      const stackHtml = (p.gcpStack || []).map(s =>
        `<span class="px-2 py-0.5 rounded text-[10px] mono bg-slate-950 text-indigo-300 border border-slate-800">${{s}}</span>`
      ).join("");

      return `
        <div class="card-surface hover:border-rose-500/50 rounded-2xl p-6 flex flex-col justify-between transition shadow-xl">
          <div>
            <div class="flex flex-wrap items-center justify-between gap-2 mb-2">
              <span class="text-xs font-bold mono text-rose-400">SQUARE ${{p.code}} • ${{p.tool}}</span>
              <span class="px-2.5 py-0.5 rounded-full text-xs font-bold border ${{badgeClass(p.level)}}">${{p.level}}</span>
            </div>
            <div class="mb-2.5 flex flex-wrap gap-1.5">
              <span class="px-2.5 py-1 rounded-lg text-[10.5px] font-bold bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
                🎨 UI Design: ${{arch.style}}
              </span>
              <span class="px-2.5 py-1 rounded-lg text-[10.5px] font-bold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                ⚙️ ${{arch.engine}}
              </span>
            </div>
            ${{deptTitle ? `<div class="text-[11px] font-bold mono text-indigo-400 mb-1">${{deptTitle}}</div>` : ''}}
            <h3 class="text-lg font-extrabold mb-2">${{p.project}}</h3>
            <p class="text-xs text-slate-400 italic mb-2.5"><strong class="text-slate-200 not-italic">Focus:</strong> ${{p.focus}}</p>
            <p class="text-xs md:text-sm leading-relaxed mb-4" style="color:var(--text-muted);">${{p.desc}}</p>
            <div class="flex flex-wrap gap-1.5 mb-4">${{stackHtml}}</div>
            <div class="p-3 rounded-xl bg-slate-950/90 border border-slate-800/90 mb-5 text-xs">
              <div class="text-[10px] uppercase font-bold mono text-amber-400 mb-1">🎯 AWS / Anthropic / Sierra Win-Back Edge:</div>
              <div class="text-slate-300 text-xs leading-snug">${{p.competeEdge}}</div>
            </div>
          </div>

          <div class="space-y-2 pt-2 border-t border-slate-800/80">
            <div class="grid grid-cols-2 gap-2">
              <a href="${{liveDemoHref}}" target="_blank"
                 class="px-3.5 py-2.5 rounded-xl bg-gradient-to-r from-rose-600 to-indigo-600 hover:opacity-95 text-white text-xs font-bold mono text-center shadow-lg transition">
                🚀 Launch Unique App ↗
              </a>
              <a href="${{docsHref}}" target="_blank"
                 class="px-3.5 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-cyan-300 text-xs font-bold mono text-center transition">
                📘 Reproduction Docs ↗
              </a>
            </div>
            <div class="grid grid-cols-3 gap-2">
              <button onclick="window.playCardAudioPitch('${{p.code}}', this)"
                      class="py-2 px-2 rounded-xl bg-rose-500/15 hover:bg-rose-500/25 border border-rose-500/30 text-[11px] font-bold mono text-rose-200 transition">
                🔊 15s Pitch (3.8 Live)
              </button>
              <button onclick="window.openArenaForCase('${{p.code}}')"
                      class="py-2 px-2 rounded-xl bg-amber-500/15 hover:bg-amber-500/25 border border-amber-500/30 text-[11px] font-bold mono text-amber-300 transition">
                ⚔️ Race Argon vs Flash
              </button>
              <button onclick="openQuickRun('${{p.code}}')"
                      class="py-2 px-2 rounded-xl bg-slate-950 hover:bg-slate-900 border border-slate-800 text-[11px] font-bold mono text-slate-300 transition">
                ⚡ Inline Sandbox
              </button>
            </div>
          </div>
        </div>
      `;
    }}

    function selectDept(deptId) {{
      const dept = DOMAINS.find(d => d.id === deptId) || DOMAINS[0];
      document.querySelectorAll(".dept-tab-btn").forEach(btn => {{
        btn.className = "dept-tab-btn px-4 py-2 rounded-xl text-xs font-bold mono transition bg-slate-900 text-slate-300 border border-slate-800 hover:bg-slate-800";
      }});
      const activeBtn = document.getElementById("dept-btn-" + dept.id);
      if (activeBtn) activeBtn.className = "dept-tab-btn px-4 py-2 rounded-xl text-xs font-bold mono transition bg-rose-600 text-white shadow-lg";

      document.getElementById("dept-banner").innerHTML = `
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div class="text-xs font-bold mono text-rose-400 uppercase mb-1">Dedicated Cloud Run Service: ${{dept.service_name}} • UI Persona: ${{dept.themeName}}</div>
            <h3 class="text-xl font-extrabold text-white mb-1">${{dept.fullTitle}}</h3>
            <p class="text-xs text-slate-300 mb-1"><strong class="text-emerald-300">Core Mission:</strong> ${{dept.mission}}</p>
            <p class="text-xs text-indigo-300"><strong>Why Google Wins:</strong> ${{dept.awsWinback}}</p>
          </div>
          <a href="${{dept.demo_url}}?auth_token=${{AUTH_TOKEN}}" target="_blank"
             class="shrink-0 px-5 py-3 rounded-xl bg-gradient-to-r from-rose-600 to-indigo-600 text-white text-xs font-bold mono shadow-xl hover:opacity-95">
            🚀 Open Full Domain Cloud Run App ↗
          </a>
        </div>
      `;
      document.getElementById("dept-projects").innerHTML = dept.projects.map(p => renderProjectCard(p, null, `${{dept.demo_url}}/?case=${{p.code}}`)).join("");
    }}

    function renderAccountTab() {{
      document.getElementById("flywheel-grid").innerHTML = ACCOUNT.ecosystemFlywheel.map(f => `
        <div class="p-4 rounded-xl bg-slate-950 border border-slate-800">
          <div class="text-xs font-extrabold mono text-rose-400 mb-1">${{f.brand}}</div>
          <div class="text-xs font-bold text-white mb-1.5">${{f.role}}</div>
          <p class="text-[11px] text-slate-400 leading-relaxed">${{f.stats}}</p>
        </div>
      `).join("");

      document.getElementById("winback-grid").innerHTML = ACCOUNT.competitorWinBackMatrix.map(w => `
        <div class="p-5 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-xs font-extrabold mono text-amber-400">VS. ${{w.incumbent}}</span>
            <span class="px-2 py-0.5 rounded text-[10px] mono bg-emerald-500/15 text-emerald-300">GCP WIN-BACK</span>
          </div>
          <p class="text-xs text-slate-400"><strong>Current Rocket Footprint:</strong> ${{w.currentRocketUse}}</p>
          <p class="text-xs text-emerald-300 leading-relaxed"><strong>How We Win with Gemini 4 Argon + GE + Antigravity:</strong> ${{w.whyGoogleWins}}</p>
        </div>
      `).join("");

      document.getElementById("exec-sponsors-list").innerHTML = ACCOUNT.executiveSponsors.map(s =>
        `<li class="p-2.5 rounded-lg bg-slate-950 border border-slate-800"><strong class="text-white">${{s.name}}</strong> — <span class="text-slate-400">${{s.role}}</span></li>`
      ).join("");
      document.getElementById("google-team-list").innerHTML = ACCOUNT.googleAccountTeam.map(s =>
        `<li class="p-2.5 rounded-lg bg-slate-950 border border-slate-800"><strong class="text-white">${{s.name}}</strong> — <span class="text-slate-400">${{s.role}}</span></li>`
      ).join("");
    }}

    function renderKeynoteTab() {{
      const cols = [KEYNOTE.hour1_gemini_enterprise, KEYNOTE.hour2_antigravity];
      document.getElementById("keynote-columns").innerHTML = cols.map((hr, i) => `
        <div class="card-surface rounded-2xl p-6 space-y-5 border-t-4 ${{i === 0 ? 'border-t-rose-500' : 'border-t-indigo-500'}}">
          <div>
            <span class="text-xs font-bold mono ${{i === 0 ? 'text-rose-400' : 'text-indigo-400'}}">${{hr.duration}}</span>
            <h3 class="text-xl font-extrabold text-white mt-1">${{hr.title}}</h3>
            <p class="text-xs text-slate-400 mt-0.5">Presenters: ${{hr.presenters}}</p>
          </div>
          <div class="space-y-4">
            ${{hr.slides.map(s => `
              <div class="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                <div class="flex items-center justify-between">
                  <span class="text-[11px] font-bold mono text-amber-400">⏱️ ${{s.time}}</span>
                  <a href="/docs/${{s.demoRef}}?auth_token=${{AUTH_TOKEN}}" target="_blank" class="text-[11px] font-bold mono text-cyan-400 hover:underline">
                    Launch Featured Demo [${{s.demoRef}}] ↗
                  </a>
                </div>
                <h4 class="text-sm font-bold text-white">${{s.title}}</h4>
                <div class="text-xs font-semibold text-indigo-300">${{s.subtitle}}</div>
                <ul class="list-disc list-inside text-xs text-slate-300 space-y-1 pt-1">
                  ${{s.bullets.map(b => `<li>${{b}}</li>`).join("")}}
                </ul>
              </div>
            `).join("")}}
          </div>
        </div>
      `).join("");
    }}

    function renderAllDocsTable() {{
      const q = (document.getElementById("docs-search")?.value || "").toLowerCase();
      const rows = [];
      DOMAINS.forEach(d => {{
        d.projects.forEach(p => {{
          const hay = `${{p.code}} ${{p.project}} ${{p.tool}} ${{d.shortTitle}} ${{(p.gcpStack||[]).join(" ")}}`.toLowerCase();
          if (q && !hay.includes(q)) return;
          rows.push(`
            <tr class="hover:bg-slate-900/60 transition">
              <td class="p-4 font-bold mono text-rose-400">[${{p.code}}] <span class="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">${{p.level}}</span></td>
              <td class="p-4 mono text-slate-300">${{d.shortTitle}}<br><span class="text-[10px] text-slate-500">${{d.service_name}}</span></td>
              <td class="p-4">
                <div class="font-bold text-white">${{p.project}}</div>
                <div class="text-[11px] text-slate-400">${{p.focus}}</div>
              </td>
              <td class="p-4">
                <a href="/docs/${{p.code}}?auth_token=${{AUTH_TOKEN}}" target="_blank" class="px-3 py-1.5 rounded-lg bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 font-bold mono inline-block hover:bg-cyan-500/25">
                  📘 Open Blueprint [${{p.code}}] ↗
                </a>
              </td>
              <td class="p-4">
                <a href="${{d.demo_url}}/?case=${{p.code}}&auth_token=${{AUTH_TOKEN}}" target="_blank" class="px-3 py-1.5 rounded-lg bg-rose-600 text-white font-bold mono inline-block hover:bg-rose-500">
                  🚀 Launch Demo ↗
                </a>
              </td>
            </tr>
          `);
        }});
      }});
      document.getElementById("alldocs-tbody").innerHTML = rows.join("");
    }}

    function filterByLevel(lvl) {{
      document.querySelectorAll(".lvl-btn").forEach(btn => {{
        btn.className = "lvl-btn px-5 py-2.5 rounded-xl text-sm font-bold bg-slate-800 text-slate-300";
      }});
      const activeBtn = document.getElementById("lvl-btn-" + lvl);
      if (activeBtn) activeBtn.className = "lvl-btn px-5 py-2.5 rounded-xl text-sm font-bold bg-rose-600 text-white shadow";
      const matches = [];
      DOMAINS.forEach(d => {{
        d.projects.forEach(p => {{
          if (p.tags.includes(lvl)) matches.push({{ project: p, dept: d.shortTitle, url: `${{d.demo_url}}/?case=${{p.code}}` }});
        }});
      }});
      document.getElementById("level-projects").innerHTML = matches.map(m => renderProjectCard(m.project, m.dept, m.url)).join("");
    }}

    function filterTranslator(filterType) {{
      const filtered = filterType === "all" ? TRANSLATOR : TRANSLATOR.filter(i => i.tags.includes(filterType));
      document.getElementById("translator-tbody").innerHTML = filtered.map(item => `
        <tr class="hover:bg-slate-800/40 transition border-b border-slate-800/70">
          <td class="p-4 align-top font-bold text-white max-w-xs">
            <a href="${{item.url}}" target="_blank" class="hover:text-rose-400 transition">${{item.service}} ↗</a>
            <div class="mt-1"><span class="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-300">${{item.level}}</span></div>
          </td>
          <td class="p-4 align-top text-slate-300 text-xs leading-relaxed">${{item.oneLiner}}</td>
          <td class="p-4 align-top text-slate-300 text-xs leading-relaxed">${{item.useCase}}</td>
          <td class="p-4 align-top text-emerald-300 text-xs font-medium">${{item.chatgpt}}</td>
          <td class="p-4 align-top text-amber-300 text-xs font-medium">${{item.claude}}</td>
          <td class="p-4 align-top text-cyan-300 text-xs font-medium">${{item.sierra}}</td>
        </tr>
      `).join("");
    }}

    function switchMainTab(tabName) {{
      document.querySelectorAll(".tab-content").forEach(el => el.classList.remove("active"));
      document.querySelectorAll(".main-tab-btn").forEach(btn => {{
        btn.classList.remove("bg-rose-600", "text-white", "shadow");
        btn.classList.add("text-slate-300");
      }});
      const target = document.getElementById("tab-" + tabName);
      if (target) target.classList.add("active");
      const activeBtn = document.getElementById("btn-" + tabName);
      if (activeBtn) {{
        activeBtn.classList.remove("text-slate-300");
        activeBtn.classList.add("bg-rose-600", "text-white", "shadow");
      }}
    }}

    async function openQuickRun(code) {{
      let found = null, foundDept = null;
      DOMAINS.forEach(d => d.projects.forEach(p => {{ if (p.code === code) {{ found = p; foundDept = d; }} }}));
      if (!found) return;
      document.getElementById("quickrun-modal").classList.remove("hidden");
      document.getElementById("qr-badge").innerText = `SQUARE [${{found.code}}] • ${{foundDept.shortTitle}}`;
      document.getElementById("qr-title").innerText = found.project;
      document.getElementById("qr-docs-btn").href = `/docs/${{found.code}}?auth_token=${{AUTH_TOKEN}}`;
      document.getElementById("qr-demo-btn").href = `${{foundDept.demo_url}}/?case=${{found.code}}&auth_token=${{AUTH_TOKEN}}`;
      document.getElementById("qr-loading").classList.remove("hidden");
      document.getElementById("qr-sandbox-grid").innerHTML = "";
      document.getElementById("qr-vertex-out").innerHTML = "";

      try {{
        const res = await fetch("/api/run-demo", {{
          method: "POST",
          headers: {{"Content-Type": "application/json"}},
          body: JSON.stringify({{ code: found.code, model: "gemini-4-argon", user_input: found.sampleInput, params: found.sandboxParams }})
        }});
        const data = await res.json();
        const metrics = (data.sandbox && data.sandbox.metrics) || {{}};
        document.getElementById("qr-sandbox-grid").innerHTML = Object.entries(metrics).map(([k, v]) => `
          <div class="p-3 rounded-xl bg-slate-900 border border-slate-800">
            <div class="text-[10px] mono uppercase text-slate-400">${{k.replace(/_/g, ' ')}}</div>
            <div class="text-xs font-bold mono text-emerald-400 mt-0.5">${{v}}</div>
          </div>
        `).join("");
        const md = (data.vertex && data.vertex.response_markdown) || "Completed.";
        document.getElementById("qr-vertex-out").innerHTML = `<div class="text-[11px] mono text-indigo-400 mb-2">⚡ Vertex AI ${{data.vertex?.model_used}} (${{data.vertex?.latency_ms}}ms):</div><div class="whitespace-pre-wrap text-slate-200">${{md.replace(/</g, '&lt;')}}</div>`;
      }} catch (e) {{
        document.getElementById("qr-vertex-out").innerText = "Error: " + e.message;
      }} finally {{
        document.getElementById("qr-loading").classList.add("hidden");
      }}
    }}

    function closeQuickRun() {{
      document.getElementById("quickrun-modal").classList.add("hidden");
    }}

    async function generatePitchArchitecture() {{
      const desc = document.getElementById("pitch-desc").value.trim();
      const dept = document.getElementById("pitch-dept").value;
      if (!desc) return alert("Please enter your project idea first.");
      const out = document.getElementById("pitch-argon-output");
      out.classList.remove("hidden");
      out.innerHTML = `<span class="shrinking-shining-ink mr-2"></span> <span class="mono text-rose-300">Gemini 4 Argon is designing your Rocket Hackathon reference architecture...</span>`;
      try {{
        const res = await fetch("/api/run-demo", {{
          method: "POST",
          headers: {{"Content-Type": "application/json"}},
          body: JSON.stringify({{
            code: "1.5",
            model: "gemini-4-argon",
            user_input: `Hackathon Track: ${{dept}}\\nTeam Idea: ${{desc}}\\nDesign a winning 24-hour Rocket Hackathon architecture using Gemini 4 Argon, Gemini Enterprise (Sobi/Spark), and Google Antigravity + MCP. Recommend which of the 33 portal blueprints to clone first.`
          }})
        }});
        const data = await res.json();
        out.innerHTML = `<div class="font-bold mono text-emerald-400 mb-2">✅ Gemini 4 Argon Custom Architecture Blueprint (${{data.vertex?.latency_ms}}ms):</div><div class="whitespace-pre-wrap text-slate-200">${{(data.vertex?.response_markdown || '').replace(/</g, '&lt;')}}</div>`;
      }} catch (e) {{
        out.innerText = "Error: " + e.message;
      }}
    }}

    function submitOutlookPitch() {{
      const name = document.getElementById("pitch-name").value || "Rocket Hackathon Builder";
      const dept = document.getElementById("pitch-dept").value;
      const desc = document.getElementById("pitch-desc").value || "";
      const subject = encodeURIComponent(`[Rocket Hackathon Proposal] ${{name}} - ${{dept}}`);
      const body = encodeURIComponent(`Team Lead: ${{name}}\\nTrack: ${{dept}}\\n\\nIdea:\\n${{desc}}`);
      window.open(`https://outlook.office.com/mail/deeplink/compose?to=sundarc@google.com;luisls@google.com;jesusarguelles@google.com&subject=${{subject}}&body=${{body}}`, "_blank");
    }}

    // =========================================================================
    // ASTRA 2.0 REAL GEMINI 3.8 LIVE VIDEO AVATAR (24 FPS MSE) + 24KHZ AUDIO
    // + CAMERA/SCREEN MULTIMODAL VISION + OMNISCIENT COMMAND OVERLAY (⌘K)
    // =========================================================================
    let astraWs = null;
    let astraAudioCtx = null;
    let astraActiveSources = [];
    let astraNextPlayTime = 0;
    let astraMuted = false;
    let astraMicStream = null;
    let astraMicProcessor = null;
    let astraVisionStream = null;
    let astraVisionInterval = null;
    let astraTranscriptBuffer = "";
    let astraChatHistory = [];

    // MediaSource Extensions (MSE) for 704x1280 24 FPS H.264 + 24kHz AAC Live Video Avatar
    let astraMediaSource = null;
    let astraSourceBuffer = null;
    let astraMseQueue = [];
    let astraMseReady = false;

    function initAstraMSE() {{
      if (astraMediaSource) return;
      const heroVid = document.getElementById("astra-live-video");
      const overlayVid = document.getElementById("astra-overlay-video");
      const svgFallback = document.getElementById("astra-svg-avatar");
      const overlayPlaceholder = document.getElementById("astra-overlay-placeholder");
      if (!heroVid) return;

      astraMediaSource = new MediaSource();
      heroVid.playsInline = true;
      heroVid.autoplay = true;
      heroVid.muted = astraMuted;
      heroVid.classList.remove("hidden");
      if (svgFallback) svgFallback.classList.add("hidden");
      heroVid.src = URL.createObjectURL(astraMediaSource);

      astraMediaSource.addEventListener("sourceopen", () => {{
        const candidates = [
          'video/mp4; codecs="avc1.42E01E, mp4a.40.2"',
          'video/mp4; codecs="avc1.42c01f, mp4a.40.2"',
          'video/mp4; codecs="avc1.4D401E, mp4a.40.2"',
          'video/mp4; codecs="avc1.64001E, mp4a.40.2"',
          'video/mp4; codecs="avc1.42E01E"',
          'video/mp4'
        ];
        const mime = candidates.find(t => MediaSource.isTypeSupported(t));
        if (!mime) return;
        try {{
          astraSourceBuffer = astraMediaSource.addSourceBuffer(mime);
          astraSourceBuffer.mode = "sequence";
          astraSourceBuffer.addEventListener("updateend", () => {{
            pumpAstraMseQueue();
            if (heroVid.paused) {{
              heroVid.play().then(() => {{
                if (overlayVid && heroVid.captureStream) {{
                  try {{
                    overlayVid.srcObject = heroVid.captureStream();
                    overlayVid.classList.remove("hidden");
                    if (overlayPlaceholder) overlayPlaceholder.classList.add("hidden");
                  }} catch (e) {{}}
                }}
              }}).catch(() => {{}});
            }}
          }});
          astraMseReady = true;
          pumpAstraMseQueue();
        }} catch (e) {{}}
      }});
    }}

    function pumpAstraMseQueue() {{
      if (!astraMseReady || !astraSourceBuffer || astraSourceBuffer.updating) return;
      if (astraMseQueue.length === 0) return;
      try {{
        astraSourceBuffer.appendBuffer(astraMseQueue.shift());
      }} catch (e) {{}}
    }}

    function appendAstraVideoChunk(arrayBuffer) {{
      if (!astraMediaSource) initAstraMSE();
      astraMseQueue.push(arrayBuffer);
      pumpAstraMseQueue();
    }}

    function resetAstraMSE() {{
      astraMseQueue = [];
      astraMseReady = false;
      astraSourceBuffer = null;
      astraMediaSource = null;
      const heroVid = document.getElementById("astra-live-video");
      if (heroVid && heroVid.src) {{
        try {{
          heroVid.pause();
          URL.revokeObjectURL(heroVid.src);
          heroVid.removeAttribute("src");
          heroVid.load();
        }} catch (e) {{}}
      }}
    }}

    function ensureAstraAudioCtx() {{
      if (!astraAudioCtx) {{
        const AC = window.AudioContext || window.webkitAudioContext;
        astraAudioCtx = new AC({{ sampleRate: 24000 }});
      }}
      if (astraAudioCtx.state === "suspended") {{
        astraAudioCtx.resume();
      }}
      return astraAudioCtx;
    }}

    function animateAstraMouth(openAmount) {{
      const lip = document.getElementById("avatar-mouth-lip");
      if (!lip) return;
      const curveY = 68 + Math.min(12, Math.round(openAmount * 28));
      lip.setAttribute("d", `M 43,67 Q 50,${{curveY}} 57,67`);
    }}

    window.interruptAstraNow = function() {{
      // Stop scheduled 24kHz PCM sources in 0ms
      astraActiveSources.forEach(src => {{
        try {{ src.stop(0); src.disconnect(); }} catch (e) {{}}
      }});
      astraActiveSources = [];
      if (astraAudioCtx) {{
        astraNextPlayTime = astraAudioCtx.currentTime;
      }}
      // Also flush any queued MSE video segments on barge-in
      astraMseQueue = [];
      animateAstraMouth(0);
      const badge = document.getElementById("avatar-badge");
      if (badge) {{
        badge.innerText = "Interrupted • Listening";
        badge.className = "text-[10px] mono px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300";
      }}
    }};

    function playAstraPcm24kChunk(b64Data) {{
      if (astraMuted) return;
      const ctx = ensureAstraAudioCtx();
      const bin = atob(b64Data);
      const int16 = new Int16Array(Math.floor(bin.length / 2));
      let peak = 0;
      for (let i = 0; i < int16.length; i++) {{
        const lo = bin.charCodeAt(i * 2);
        const hi = bin.charCodeAt(i * 2 + 1);
        let val = (hi << 8) | lo;
        if (val >= 0x8000) val -= 0x10000;
        int16[i] = val;
        const abs = Math.abs(val);
        if (abs > peak) peak = abs;
      }}
      const float32 = new Float32Array(int16.length);
      for (let i = 0; i < int16.length; i++) {{
        float32[i] = int16[i] / 32768.0;
      }}
      const buf = ctx.createBuffer(1, float32.length, 24000);
      buf.getChannelData(0).set(float32);

      const src = ctx.createBufferSource();
      src.buffer = buf;
      src.connect(ctx.destination);

      const now = ctx.currentTime;
      if (astraNextPlayTime < now) astraNextPlayTime = now + 0.01;
      src.start(astraNextPlayTime);
      astraNextPlayTime += buf.duration;
      astraActiveSources.push(src);

      animateAstraMouth(peak / 32768.0);
      src.onended = () => {{
        astraActiveSources = astraActiveSources.filter(s => s !== src);
        if (astraActiveSources.length === 0) {{
          animateAstraMouth(0);
        }}
      }};
    }}

    window.toggleAstraMute = function() {{
      astraMuted = !astraMuted;
      const btn = document.getElementById("btn-astra-mute");
      const heroVid = document.getElementById("astra-live-video");
      if (heroVid) heroVid.muted = astraMuted;
      if (astraMuted) {{
        window.interruptAstraNow();
        if (btn) btn.innerText = "🔇";
      }} else {{
        if (btn) btn.innerText = "🔊";
      }}
    }};

    window.reconnectAstraIfLive = function() {{
      if (astraWs && astraWs.readyState === WebSocket.OPEN) {{
        window.toggleAstraLiveSession();
        setTimeout(() => window.toggleAstraLiveSession(), 250);
      }}
    }};

    window.toggleAstraLiveSession = function() {{
      ensureAstraAudioCtx();
      const labelEl = document.getElementById("voice-label");
      const badgeEl = document.getElementById("avatar-badge");
      const ovStatus = document.getElementById("overlay-avatar-status");
      const txEl = document.getElementById("astra-live-transcript");
      const heroVid = document.getElementById("astra-live-video");
      const overlayVid = document.getElementById("astra-overlay-video");
      const svgFallback = document.getElementById("astra-svg-avatar");
      const overlayPlaceholder = document.getElementById("astra-overlay-placeholder");

      if (astraWs && astraWs.readyState === WebSocket.OPEN) {{
        window.interruptAstraNow();
        resetAstraMSE();
        if (astraMicStream) {{
          astraMicStream.getTracks().forEach(t => t.stop());
          astraMicStream = null;
        }}
        window.stopAstraVision();
        astraWs.close();
        astraWs = null;
        if (heroVid) heroVid.classList.add("hidden");
        if (overlayVid) overlayVid.classList.add("hidden");
        if (svgFallback) svgFallback.classList.remove("hidden");
        if (overlayPlaceholder) overlayPlaceholder.classList.remove("hidden");
        if (labelEl) labelEl.innerText = "Start Live Video Avatar";
        if (badgeEl) {{
          badgeEl.innerText = "24 FPS + 24kHz Ready";
          badgeEl.className = "text-[10px] mono px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300";
        }}
        if (ovStatus) ovStatus.innerText = "Idle";
        return;
      }}

      const voice = (document.getElementById("astra-voice-select") || {{value: "Aoede"}}).value;
      const liveMode = (document.getElementById("astra-live-mode") || {{value: "gemini-3.8-live"}}).value;
      const avatarChoice = (document.getElementById("astra-avatar-select") || {{value: "Kira"}}).value;
      const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
      const wsUrl = `${{proto}}//${{window.location.host}}/ws/live-voice/portal?voice=${{encodeURIComponent(voice)}}&live_mode=${{encodeURIComponent(liveMode)}}&avatar=${{encodeURIComponent(avatarChoice)}}`;

      if (labelEl) labelEl.innerText = "Connecting Live Avatar...";
      resetAstraMSE();
      astraWs = new WebSocket(wsUrl);
      astraWs.binaryType = "arraybuffer";

      astraWs.onopen = () => {{
        if (labelEl) labelEl.innerText = "⏹ Stop Live Avatar";
        const modeTag = avatarChoice !== "off" ? `🎥 Avatar ${{avatarChoice}} (24fps)` : `🎙️ ${{voice}} 24kHz`;
        if (badgeEl) {{
          badgeEl.innerText = modeTag;
          badgeEl.className = "text-[10px] mono px-2 py-0.5 rounded-full bg-rose-500 text-white animate-pulse";
        }}
        if (ovStatus) ovStatus.innerText = modeTag;
        astraTranscriptBuffer = "";
        if (txEl) txEl.innerHTML = `<span class="text-emerald-400 font-bold">[Connected to ${{liveMode}} • ${{modeTag}}]</span> Streaming real-time video & 24kHz audio...`;
        astraWs.send(JSON.stringify({{
          type: "text",
          text: "Welcome the Rocket Companies team warmly in 2 concise sentences! Mention that we are ready for the October 16 Showcase and October 28–29 Detroit and Chennai Hackathon with all 33 demos, and invite them to ask about any specific use case or interrupt you anytime."
        }}));
      }};

      astraWs.onmessage = (evt) => {{
        if (typeof evt.data !== "string") {{
          // Binary fMP4 chunk from Gemini 3.8 Live Video Avatar (via zero-copy ffmpeg remux)
          appendAstraVideoChunk(evt.data);
          return;
        }}
        try {{
          const msg = JSON.parse(evt.data);
          if (msg.interrupted) {{
            window.interruptAstraNow();
            return;
          }}
          if (msg.input_transcript && txEl) {{
            txEl.innerHTML = `<div class="text-cyan-300 font-semibold">You: "${{msg.input_transcript}}"</div>`;
            applyAstraVoiceNavigation(msg.input_transcript);
          }}
          if (msg.output_transcript && txEl) {{
            astraTranscriptBuffer += msg.output_transcript;
            txEl.innerHTML = `<div class="text-rose-200"><strong>Astra 2.0 (${{avatarChoice !== 'off' ? avatarChoice : voice}}):</strong> ${{astraTranscriptBuffer}}</div>`;
            txEl.scrollTop = txEl.scrollHeight;
          }}
          if (msg.matched_squares && msg.matched_squares.length > 0) {{
            renderHeroMatchedBadges(msg.matched_squares);
          }}
          if (msg.turn_complete) {{
            astraTranscriptBuffer = "";
          }}
          if (msg.audio_b64) {{
            playAstraPcm24kChunk(msg.audio_b64);
          }}
        }} catch (e) {{}}
      }};

      astraWs.onclose = () => {{
        window.interruptAstraNow();
        if (labelEl) labelEl.innerText = "Start Live Video Avatar";
      }};
    }};

    window.stopAstraVision = function() {{
      if (astraVisionInterval) {{
        clearInterval(astraVisionInterval);
        astraVisionInterval = null;
      }}
      if (astraVisionStream) {{
        astraVisionStream.getTracks().forEach(t => t.stop());
        astraVisionStream = null;
      }}
      const pip = document.getElementById("astra-vision-pip");
      if (pip) {{
        pip.srcObject = null;
        pip.classList.add("hidden");
      }}
      const camBtn = document.getElementById("btn-astra-cam");
      const scrBtn = document.getElementById("btn-astra-screen");
      if (camBtn) camBtn.innerText = "📷 Cam";
      if (scrBtn) scrBtn.innerText = "🖥️ Screen";
    }};

    async function startAstraVisionStream(mode) {{
      if (astraVisionStream) {{
        window.stopAstraVision();
        return;
      }}
      if (!astraWs || astraWs.readyState !== WebSocket.OPEN) {{
        window.toggleAstraLiveSession();
      }}
      try {{
        astraVisionStream = mode === "camera"
          ? await navigator.mediaDevices.getUserMedia({{ video: {{ width: 640, height: 480 }} }})
          : await navigator.mediaDevices.getDisplayMedia({{ video: true }});
        const pip = document.getElementById("astra-vision-pip");
        if (pip) {{
          pip.srcObject = astraVisionStream;
          pip.classList.remove("hidden");
        }}
        const btn = document.getElementById(mode === "camera" ? "btn-astra-cam" : "btn-astra-screen");
        if (btn) btn.innerText = mode === "camera" ? "🔴 Stop Cam" : "🔴 Stop Screen";

        const canvas = document.createElement("canvas");
        canvas.width = 640;
        canvas.height = 480;
        const ctx = canvas.getContext("2d");

        astraVisionInterval = setInterval(() => {{
          if (!astraWs || astraWs.readyState !== WebSocket.OPEN || !pip) return;
          try {{
            ctx.drawImage(pip, 0, 0, 640, 480);
            const b64 = canvas.toDataURL("image/jpeg", 0.72).split(",")[1];
            astraWs.send(JSON.stringify({{ type: "image", mime_type: "image/jpeg", data: b64 }}));
          }} catch (e) {{}}
        }}, 1000);

        astraVisionStream.getVideoTracks()[0].onended = () => window.stopAstraVision();
      }} catch (err) {{
        alert("Could not start " + mode + ": " + err.message);
      }}
    }}

    window.toggleAstraCamera = () => startAstraVisionStream("camera");
    window.toggleAstraScreen = () => startAstraVisionStream("screen");

    window.sendAstraBargeIn = function(customPrompt) {{
      const inp = document.getElementById("astra-barge-input");
      const text = customPrompt || (inp ? inp.value.trim() : "");
      if (!text) return;
      if (!customPrompt && inp) inp.value = "";

      window.interruptAstraNow();
      applyAstraVoiceNavigation(text);
      astraTranscriptBuffer = "";
      const txEl = document.getElementById("astra-live-transcript");
      if (txEl) {{
        txEl.innerHTML = `<div class="text-amber-300 font-bold">⚡ Barge-In: "${{text}}"</div><div class="text-slate-400 text-[11px]">Astra 2.0 Live Avatar responding...</div>`;
      }}

      if (!astraWs || astraWs.readyState !== WebSocket.OPEN) {{
        window.toggleAstraLiveSession();
        setTimeout(() => {{
          if (astraWs && astraWs.readyState === WebSocket.OPEN) {{
            window.interruptAstraNow();
            astraWs.send(JSON.stringify({{ type: "interrupt", text: text }}));
          }}
        }}, 700);
      }} else {{
        astraWs.send(JSON.stringify({{ type: "interrupt", text: text }}));
      }}
    }};

    window.toggleAstraMic = async function() {{
      const micBtn = document.getElementById("astra-mic-label");
      if (astraMicStream) {{
        astraMicStream.getTracks().forEach(t => t.stop());
        astraMicStream = null;
        if (astraMicProcessor) {{
          try {{ astraMicProcessor.disconnect(); }} catch (e) {{}}
          astraMicProcessor = null;
        }}
        if (micBtn) micBtn.innerText = "16kHz Mic";
        return;
      }}

      if (!astraWs || astraWs.readyState !== WebSocket.OPEN) {{
        window.toggleAstraLiveSession();
      }}

      try {{
        astraMicStream = await navigator.mediaDevices.getUserMedia({{
          audio: {{ sampleRate: 16000, channelCount: 1, echoCancellation: true, noiseSuppression: true }}
        }});
        if (micBtn) micBtn.innerText = "🔴 Mic Live";
        const micCtx = new (window.AudioContext || window.webkitAudioContext)({{ sampleRate: 16000 }});
        const source = micCtx.createMediaStreamSource(astraMicStream);
        const proc = micCtx.createScriptProcessor(2048, 1, 1);
        astraMicProcessor = proc;

        proc.onaudioprocess = (e) => {{
          if (!astraWs || astraWs.readyState !== WebSocket.OPEN) return;
          const input = e.inputBuffer.getChannelData(0);
          let rms = 0;
          const pcm16 = new Int16Array(input.length);
          for (let i = 0; i < input.length; i++) {{
            const s = Math.max(-1, Math.min(1, input[i]));
            rms += s * s;
            pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
          }}
          rms = Math.sqrt(rms / input.length);
          if (rms > 0.045 && astraActiveSources.length > 0) {{
            window.interruptAstraNow();
          }}
          const bytes = new Uint8Array(pcm16.buffer);
          let bin = "";
          for (let i = 0; i < bytes.byteLength; i++) {{
            bin += String.fromCharCode(bytes[i]);
          }}
          astraWs.send(JSON.stringify({{ type: "audio", data: btoa(bin) }}));
        }};

        source.connect(proc);
        proc.connect(micCtx.destination);
      }} catch (err) {{
        alert("Microphone access needed for live voice barge-in: " + err.message);
      }}
    }};

    // =========================================================================
    // ASTRA 2.0 OMNISCIENT COMMAND OVERLAY (⌘K) & USE-CASE ACTION CARDS
    // =========================================================================
    window.openAstraCommandOverlay = function() {{
      const el = document.getElementById("astra-command-overlay");
      if (el) {{
        el.classList.remove("hidden");
        window.filterAstraCatalogInstant("");
        const inp = document.getElementById("astra-overlay-input");
        if (inp) setTimeout(() => inp.focus(), 80);
      }}
    }};

    window.closeAstraCommandOverlay = function() {{
      const el = document.getElementById("astra-command-overlay");
      if (el) el.classList.add("hidden");
    }};

    document.addEventListener("keydown", (e) => {{
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {{
        e.preventDefault();
        const el = document.getElementById("astra-command-overlay");
        if (el && el.classList.contains("hidden")) window.openAstraCommandOverlay();
        else window.closeAstraCommandOverlay();
      }} else if (e.key === "Escape") {{
        window.closeAstraCommandOverlay();
      }}
    }});

    function renderHeroMatchedBadges(cards) {{
      const box = document.getElementById("astra-hero-matched-cards");
      if (!box || !cards || !cards.length) return;
      box.innerHTML = cards.map(c => `
        <a href="${{c.demo_url}}&auth_token=${{AUTH_TOKEN}}" target="_blank" class="px-2.5 py-1 rounded-lg bg-rose-500/20 hover:bg-rose-500/35 border border-rose-500/40 text-[11px] font-bold mono text-rose-200 transition">
          🚀 Open [${{c.code}}] ${{c.title}} ↗
        </a>
      `).join("");
    }}

    window.filterAstraCatalogInstant = function(query) {{
      const box = document.getElementById("astra-instant-results");
      if (!box) return;
      const q = (query || "").trim().toLowerCase();
      const matches = [];
      DOMAINS.forEach(d => {{
        d.projects.forEach(p => {{
          const arch = UI_ARCHETYPES[p.code] || {{ style: "Custom UI", engine: "Vertex AI" }};
          const hay = `${{p.code}} ${{p.project}} ${{p.focus || ''}} ${{p.desc || ''}} ${{p.competeEdge || ''}} ${{d.shortTitle}} ${{arch.style}} ${{arch.engine}}`.toLowerCase();
          if (!q || hay.includes(q)) {{
            matches.push({{ d, p, arch }});
          }}
        }});
      }});
      box.innerHTML = matches.slice(0, 8).map(({{ d, p, arch }}) => `
        <div class="p-2 rounded-xl bg-slate-950 border border-slate-800 hover:border-cyan-500/40 transition flex items-center justify-between gap-2">
          <div class="min-w-0">
            <div class="text-[11px] font-bold text-white truncate"><span class="text-rose-400 mono">[${{p.code}}]</span> ${{p.project}}</div>
            <div class="text-[10px] text-slate-400 truncate">🎨 ${{arch.style}}</div>
          </div>
          <div class="flex items-center gap-1 shrink-0">
            <a href="${{d.demo_url}}/?case=${{p.code}}&auth_token=${{AUTH_TOKEN}}" target="_blank" class="px-2 py-1 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-[10px] font-bold mono">Launch ↗</a>
            <button onclick="window.closeAstraCommandOverlay();window.openArenaForCase('${{p.code}}')" class="px-1.5 py-1 rounded-lg bg-amber-500/20 text-amber-300 text-[10px] font-bold mono">⚔️</button>
          </div>
        </div>
      `).join("");
    }};

    function formatAstraMarkdown(md) {{
      if (!md) return "";
      let safe = md
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
      safe = safe.replace(/^### (.*$)/gm, '<h4 class="text-sm font-extrabold text-rose-300 mt-3 mb-1">$1</h4>');
      safe = safe.replace(/^## (.*$)/gm, '<h3 class="text-base font-extrabold text-white mt-3 mb-1.5">$1</h3>');
      safe = safe.replace(/\\*\\*(.*?)\\*\\*/g, '<strong class="text-white font-bold">$1</strong>');
      safe = safe.replace(/`([^`]+)`/g, '<code class="px-1.5 py-0.5 rounded bg-slate-900 border border-slate-700 text-cyan-300 mono text-[11px]">$1</code>');
      safe = safe.replace(/\\[([1-6]\\.[1-5]|M\\.[1-5])\\]/g, '<span class="px-1.5 py-0.5 rounded bg-rose-500/25 border border-rose-500/40 text-rose-300 font-extrabold mono text-xs">[$1]</span>');
      safe = safe.replace(/^- (.*$)/gm, '<li class="ml-4 list-disc text-slate-200 my-0.5">$1</li>');
      safe = safe.replace(/\\n\\n/g, '<div class="h-2"></div>');
      return safe;
    }}

    function renderOverlaySquareCards(cards) {{
      if (!cards || !cards.length) return "";
      return `
        <div class="mt-3 pt-3 border-t border-slate-800/90">
          <div class="text-[10px] font-extrabold uppercase mono text-cyan-300 mb-2">⚡ Matched Interactive Demos (Click to Launch, Race or Hear 24kHz Pitch):</div>
          <div class="grid sm:grid-cols-2 gap-2.5">
            ${{cards.map(c => `
              <div class="p-3 rounded-xl bg-slate-900/95 border border-slate-700/80 hover:border-rose-500/50 transition flex flex-col justify-between gap-2">
                <div>
                  <div class="flex items-center justify-between gap-1.5">
                    <span class="px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 font-extrabold mono text-[11px]">[${{c.code}}]</span>
                    <span class="text-[10px] mono text-emerald-300 truncate">${{c.runtime}}</span>
                  </div>
                  <div class="text-xs font-extrabold text-white mt-1">${{c.title}}</div>
                  <div class="text-[11px] text-cyan-300 font-semibold mt-0.5">🎨 ${{c.ui_site}}</div>
                  <div class="text-[11px] text-slate-300 mt-1 line-clamp-2">${{c.impact}}</div>
                </div>
                <div class="flex flex-wrap gap-1.5 pt-1.5 border-t border-slate-800">
                  <a href="${{c.demo_url}}&auth_token=${{AUTH_TOKEN}}" target="_blank" class="px-2.5 py-1 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-[10px] font-bold mono">
                    🚀 Launch App ↗
                  </a>
                  <button onclick="window.closeAstraCommandOverlay();window.openArenaForCase('${{c.code}}')" class="px-2 py-1 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/30 text-[10px] font-bold mono">
                    ⚔️ Race Argon vs Flash
                  </button>
                  <button onclick="window.playCardAudioPitch('${{c.code}}', this)" class="px-2 py-1 rounded-lg bg-cyan-500/15 hover:bg-cyan-500/25 text-cyan-300 border border-cyan-500/30 text-[10px] font-bold mono">
                    🔊 15s Pitch
                  </button>
                  <a href="${{c.docs_url}}?auth_token=${{AUTH_TOKEN}}" target="_blank" class="px-2 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-[10px] font-bold mono">
                    📘 Docs
                  </a>
                </div>
              </div>
            `).join("")}}
          </div>
        </div>
      `;
    }}

    window.sendAstraOverlayChat = async function(customText) {{
      const inp = document.getElementById("astra-overlay-input");
      const log = document.getElementById("astra-overlay-chat-log");
      const modelSel = document.getElementById("astra-chat-model");
      const autoSpeak = document.getElementById("astra-auto-speak");

      const msg = (customText || (inp ? inp.value : "")).trim();
      if (!msg || !log) return;
      if (!customText && inp) inp.value = "";

      // Optimistic user bubble at 0ms
      const userDiv = document.createElement("div");
      userDiv.className = "ml-auto max-w-2xl p-3.5 rounded-2xl bg-gradient-to-r from-rose-600/90 to-indigo-600/90 text-white text-xs md:text-sm font-medium shadow";
      userDiv.textContent = msg;
      log.appendChild(userDiv);

      // Thinking indicator bubble
      const loadingDiv = document.createElement("div");
      loadingDiv.className = "p-4 rounded-2xl bg-slate-950 border border-slate-800 flex items-center gap-3 text-xs mono text-rose-300";
      loadingDiv.innerHTML = `<span class="shrinking-shining-ink"></span><span>Astra 2.0 querying all 33 demos, event dates & Rocket dossier...</span>`;
      log.appendChild(loadingDiv);
      log.scrollTop = log.scrollHeight;

      astraChatHistory.push({{ role: "user", text: msg }});

      try {{
        const res = await fetch("/api/astra-chat", {{
          method: "POST",
          headers: {{ "Content-Type": "application/json" }},
          body: JSON.stringify({{
            message: msg,
            history: astraChatHistory.slice(-8),
            model: modelSel ? modelSel.value : "gemini-4-argon"
          }})
        }});
        const data = await res.json();
        loadingDiv.remove();

        const replyMd = data.reply_markdown || "Here are the matching Rocket Hackathon use cases:";
        astraChatHistory.push({{ role: "assistant", text: replyMd }});

        const botDiv = document.createElement("div");
        botDiv.className = "p-4 rounded-2xl bg-slate-950/95 border border-slate-800 space-y-2 shadow-xl";
        botDiv.innerHTML = `
          <div class="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800/80 pb-2">
            <div class="flex items-center gap-2">
              <span class="font-extrabold text-rose-400 mono text-xs">ASTRA 2.0</span>
              <span class="px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 font-bold mono text-[10px]">${{data.model_used || 'gemini-4-argon'}} • ${{data.latency_ms || 0}}ms</span>
            </div>
            <button onclick="window.playCardAudioPitch_raw(this.dataset.speech, this)" data-speech="${{replyMd.replace(/"/g, '&quot;').slice(0, 420)}}" class="px-2.5 py-1 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 text-[10px] font-bold mono">
              🔊 Speak Reply (3.8 Live)
            </button>
          </div>
          <div class="text-slate-200 leading-relaxed text-xs md:text-sm">${{formatAstraMarkdown(replyMd)}}</div>
          ${{renderOverlaySquareCards(data.matched_squares || [])}}
        `;
        log.appendChild(botDiv);
        log.scrollTop = log.scrollHeight;

        if (data.matched_squares && data.matched_squares.length > 0) {{
          renderHeroMatchedBadges(data.matched_squares);
        }}

        if (autoSpeak && autoSpeak.checked) {{
          window.playCardAudioPitch_raw(replyMd.slice(0, 380), null);
        }}
      }} catch (err) {{
        loadingDiv.innerHTML = `<span class="text-rose-400">Error contacting Astra 2.0: ${{err.message}}</span>`;
      }}
    }};

    // =========================================================================
    // LIVE PARALLEL MODEL ARENA, CARD 15S AUDIO PITCH, 33-DEMO MATRIX & VOICE NAV
    // =========================================================================
    let lastArenaSummaryText = "";

    window.playCardAudioPitch = async function(code, btnEl) {{
      let found = null;
      DOMAINS.forEach(d => d.projects.forEach(p => {{ if (p.code === code) found = p; }}));
      if (!found) return;
      if (btnEl && btnEl.dataset.playing === "1") {{
        window.interruptAstraNow();
        btnEl.innerText = "🔊 15s Pitch (3.8 Live)";
        btnEl.dataset.playing = "0";
        return;
      }}
      window.interruptAstraNow();
      ensureAstraAudioCtx();
      const orig = btnEl ? btnEl.innerText : "";
      if (btnEl) {{
        btnEl.dataset.playing = "1";
        btnEl.innerText = "⏳ 3.8 Live...";
      }}
      const arch = UI_ARCHETYPES[code] || {{ style: "Bespoke Industry UI", engine: "Gemini 4 Argon" }};
      const script = `Square ${{found.code}}, ${{found.project}}. We designed this as a real-world ${{arch.style}} powered by ${{arch.engine}}. ${{found.competeEdge}}`;
      try {{
        const res = await fetch("/api/live-tts", {{
          method: "POST",
          headers: {{ "Content-Type": "application/json" }},
          body: JSON.stringify({{
            text: script,
            voice: "Aoede",
            speaker_role: "Rocket Hackathon Principal Architect",
            live_mode: "gemini-3.8-live"
          }})
        }});
        const data = await res.json();
        if (data.ok && data.pcm_b64) {{
          if (btnEl) btnEl.innerText = "⏹ Stop Pitch";
          playAstraPcm24kChunk(data.pcm_b64);
          setTimeout(() => {{
            if (btnEl && btnEl.dataset.playing === "1") {{
              btnEl.innerText = orig;
              btnEl.dataset.playing = "0";
            }}
          }}, 12000);
        }} else if (btnEl) {{
          btnEl.innerText = orig;
          btnEl.dataset.playing = "0";
        }}
      }} catch (e) {{
        if (btnEl) {{
          btnEl.innerText = orig;
          btnEl.dataset.playing = "0";
        }}
      }}
    }};

    window.openArenaForCase = function(code) {{
      switchMainTab("arena");
      const sel = document.getElementById("arena-case-select");
      if (sel) sel.value = code;
      window.runLiveModelArena();
    }};

    window.runLiveModelArena = async function() {{
      const sel = document.getElementById("arena-case-select");
      const code = sel ? sel.value : "1.1";
      let found = null;
      DOMAINS.forEach(d => d.projects.forEach(p => {{ if (p.code === code) found = p; }}));
      if (!found) return;

      const argonOut = document.getElementById("arena-argon-out");
      const flashOut = document.getElementById("arena-flash-out");
      const argonMs = document.getElementById("arena-argon-ms");
      const flashMs = document.getElementById("arena-flash-ms");
      const sbStrip = document.getElementById("arena-sandbox-strip");

      argonOut.innerHTML = `<span class="text-rose-300 font-bold animate-pulse">⚡ Calling Vertex AI gemini-4-argon (Global)...</span>`;
      flashOut.innerHTML = `<span class="text-emerald-300 font-bold animate-pulse">⚡ Calling Vertex AI gemini-3.8-flash (Global)...</span>`;
      argonMs.innerText = "Running...";
      flashMs.innerText = "Running...";

      const t0 = performance.now();
      const reqBody = (m) => ({{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{
          code: found.code,
          model: m,
          user_input: found.sampleInput,
          params: found.sandboxParams
        }})
      }});

      const pFlash = fetch("/api/run-demo", reqBody("gemini-3.8-flash")).then(r => r.json()).then(data => {{
        const ms = data.vertex?.latency_ms || Math.round(performance.now() - t0);
        flashMs.innerText = ms + " ms";
        flashOut.textContent = data.output || data.vertex?.response_markdown || "Completed.";
        return {{ ms, data }};
      }});

      const pArgon = fetch("/api/run-demo", reqBody("gemini-4-argon")).then(r => r.json()).then(data => {{
        const ms = data.vertex?.latency_ms || Math.round(performance.now() - t0);
        argonMs.innerText = ms + " ms";
        argonOut.textContent = data.output || data.vertex?.response_markdown || "Completed.";
        const metrics = (data.sandbox && data.sandbox.metrics) || {{}};
        sbStrip.innerHTML = Object.entries(metrics).slice(0, 4).map(([k, v]) => `
          <div class="p-3 rounded-xl bg-slate-950 border border-slate-800">
            <div class="text-[10px] mono uppercase text-slate-400">${{k.replace(/_/g, ' ')}}</div>
            <div class="text-xs font-bold mono text-cyan-300 mt-0.5">${{v}}</div>
          </div>
        `).join("");
        return {{ ms, data }};
      }});

      const [resF, resA] = await Promise.all([pFlash, pArgon]);
      lastArenaSummaryText = `In the live benchmark for Square ${{found.code}} (${{found.project}}), Gemini 3.8 Flash completed in ${{resF.ms}} milliseconds for ultra-low-latency ADK runtime execution, while Gemini 4 Argon completed in ${{resA.ms}} milliseconds with deep frontier reasoning and gVisor mathematical verification.`;
    }};

    window.speakArenaVerdict = function(btnEl) {{
      const txt = lastArenaSummaryText || "Pick any Rocket Companies use case and click Fire Parallel Race to benchmark Gemini 4 Argon against Gemini 3.8 Flash in real time!";
      window.playCardAudioPitch_raw(txt, btnEl);
    }};

    window.playCardAudioPitch_raw = async function(text, btnEl) {{
      window.interruptAstraNow();
      ensureAstraAudioCtx();
      const orig = btnEl ? btnEl.innerText : "";
      if (btnEl) btnEl.innerText = "⏳ Streaming 3.8 Live...";
      try {{
        const res = await fetch("/api/live-tts", {{
          method: "POST",
          headers: {{ "Content-Type": "application/json" }},
          body: JSON.stringify({{ text: text, voice: "Kore", speaker_role: "Rocket Benchmark Analyst" }})
        }});
        const data = await res.json();
        if (data.ok && data.pcm_b64) {{
          playAstraPcm24kChunk(data.pcm_b64);
        }}
      }} catch (e) {{}}
      if (btnEl) setTimeout(() => {{ btnEl.innerText = orig; }}, 4000);
    }};

    function renderMatrixArchetypeTable() {{
      const tbody = document.getElementById("matrix-archetype-tbody");
      if (!tbody) return;
      const rows = [];
      const arenaOpts = [];
      DOMAINS.forEach(d => {{
        d.projects.forEach(p => {{
          const arch = UI_ARCHETYPES[p.code] || {{ style: "Bespoke Industry Web UI", engine: "Vertex AI Gemini 4 Argon" }};
          arenaOpts.push(`<option value="${{p.code}}">[${{p.code}}] ${{p.project}} (${{d.shortTitle}})</option>`);
          rows.push(`
            <tr class="hover:bg-slate-900/70 transition">
              <td class="p-3.5 font-extrabold mono text-rose-400">[${{p.code}}]</td>
              <td class="p-3.5">
                <div class="font-bold text-white">${{p.project}}</div>
                <div class="text-[11px] text-slate-400">${{d.shortTitle}} • ${{d.service_name}}</div>
              </td>
              <td class="p-3.5">
                <span class="px-2.5 py-1 rounded-lg text-[11px] font-bold bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 inline-block">
                  🎨 ${{arch.style}}
                </span>
              </td>
              <td class="p-3.5">
                <span class="px-2.5 py-1 rounded-lg text-[11px] font-bold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 inline-block">
                  ⚙️ ${{arch.engine}}
                </span>
              </td>
              <td class="p-3.5 space-x-1.5 whitespace-nowrap">
                <a href="${{d.demo_url}}/?case=${{p.code}}&auth_token=${{AUTH_TOKEN}}" target="_blank" class="px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-bold mono inline-block">
                  🚀 Launch UI ↗
                </a>
                <button onclick="window.openArenaForCase('${{p.code}}')" class="px-2.5 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/30 font-bold mono">
                  ⚔️ Race
                </button>
              </td>
            </tr>
          `);
        }});
      }});
      tbody.innerHTML = rows.join("");
      const arenaSel = document.getElementById("arena-case-select");
      if (arenaSel) arenaSel.innerHTML = arenaOpts.join("");
    }}

    function applyAstraVoiceNavigation(text) {{
      if (!text) return;
      const low = text.toLowerCase();
      if (low.includes("arena") || low.includes("race") || low.includes("benchmark")) {{
        switchMainTab("arena");
      }} else if (low.includes("matrix") || low.includes("archetype") || low.includes("table")) {{
        switchMainTab("matrix");
      }} else if (low.includes("servicing") || low.includes("cooper") || low.includes("3.4")) {{
        switchMainTab("depts");
        selectDept("servicing");
      }} else if (low.includes("underwriting") || low.includes("schedule c") || low.includes("2.1")) {{
        switchMainTab("depts");
        selectDept("uw");
      }} else if (low.includes("redfin") || low.includes("rocket money") || low.includes("marketing")) {{
        switchMainTab("depts");
        selectDept("marketing");
      }} else if (low.includes("moonshot") || low.includes("siren") || low.includes("sherlock")) {{
        switchMainTab("depts");
        selectDept("moonshots");
      }} else if (low.includes("codemender") || low.includes("antigravity") || low.includes("sdlc")) {{
        switchMainTab("depts");
        selectDept("sdlc");
      }}
    }}

    document.addEventListener("DOMContentLoaded", () => {{
      document.getElementById("dept-buttons").innerHTML = DOMAINS.map(d =>
        `<button onclick="selectDept('${{d.id}}')" id="dept-btn-${{d.id}}" class="dept-tab-btn">${{d.shortTitle}}</button>`
      ).join("");
      document.getElementById("glossary-grid").innerHTML = GLOSSARY.map(item => `
        <div class="card-surface rounded-2xl p-6">
          <div class="flex items-center justify-between gap-2 mb-2">
            <h3 class="text-base font-bold text-white">${{item.name}}</h3>
            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/15 text-rose-300 border border-rose-500/30">${{item.level}}</span>
          </div>
          <p class="text-xs text-slate-300 mb-2">${{item.desc1}}</p>
          <p class="text-xs text-slate-400">${{item.desc2}}</p>
        </div>
      `).join("");

      selectDept("sales");
      renderAccountTab();
      renderKeynoteTab();
      renderAllDocsTable();
      renderMatrixArchetypeTable();
      filterByLevel("L100");
      filterTranslator("all");
    }});
  </script>
</body>
</html>"""
