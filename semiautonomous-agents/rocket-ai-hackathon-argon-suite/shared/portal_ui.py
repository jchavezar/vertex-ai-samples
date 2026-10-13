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

        <!-- Right 5 Cols: Interactive Astra 2.0 Argon Avatar Card -->
        <div class="lg:col-span-5">
          <div class="bg-slate-900/95 border border-rose-500/35 rounded-2xl p-5 shadow-2xl backdrop-blur-md">
            <div class="flex items-center gap-4">
              <div class="relative shrink-0">
                <div id="avatar-ring" class="absolute -inset-2 rounded-full bg-rose-500/20 animate-pulse-ring"></div>
                <div id="avatar-orb" class="relative w-24 h-24 rounded-full bg-gradient-to-b from-slate-800 to-slate-950 border border-slate-700 flex items-center justify-center overflow-hidden shadow-lg transition-all duration-300">
                  <svg class="w-full h-full p-1" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="50" cy="50" r="46" fill="#0F172A" />
                    <g id="avatar-shoulders">
                      <path d="M 15,95 Q 15,80 30,73 L 70,73 Q 85,80 85,95 Z" fill="#E11D48" />
                      <path d="M 38,73 L 50,81 L 62,73" stroke="#fbcfe8" stroke-width="2" fill="#fbcfe8" />
                      <text x="50" y="89" font-size="6.8" font-family="monospace" font-weight="900" text-anchor="middle" fill="#ffffff">ARGON 4</text>
                    </g>
                    <g id="avatar-head-group">
                      <path d="M 22,60 C 15,25 32,3 50,3 C 68,3 85,25 78,60" fill="#1e1b4b" />
                      <circle cx="23" cy="50" r="5" fill="#fbcfe8" />
                      <circle cx="77" cy="50" r="5" fill="#fbcfe8" />
                      <path d="M 26,45 C 26,24 74,25 74,45 C 74,68 50,83 50,83 C 50,83 26,68 26,45 Z" fill="#fed7aa" />
                      <path d="M 23,38 Q 28,12 50,15 Q 72,12 77,38 Q 72,25 50,26 Q 28,25 23,38 Z" fill="#312e81" />
                      <g id="avatar-eyes">
                        <ellipse cx="39" cy="46" rx="3.5" ry="2.2" fill="#ffffff" />
                        <circle cx="39" cy="46" r="2.2" fill="#1e1b4b" />
                        <ellipse cx="61" cy="46" rx="3.5" ry="2.2" fill="#ffffff" />
                        <circle cx="61" cy="46" r="2.2" fill="#1e1b4b" />
                      </g>
                      <path d="M 34,41 Q 39,39 43,41.5" stroke="#1e1b4b" stroke-width="1.5" stroke-linecap="round" fill="none" />
                      <path d="M 66,41 Q 61,39 57,41.5" stroke="#1e1b4b" stroke-width="1.5" stroke-linecap="round" fill="none" />
                      <path d="M 48,51 Q 50,55 52,51" stroke="#f43f5e" stroke-width="1.2" stroke-linecap="round" fill="none" />
                      <path id="avatar-mouth-lip" d="M 43,65 Q 50,66 57,65" stroke="#be185d" stroke-width="2.5" stroke-linecap="round" fill="none" />
                    </g>
                  </svg>
                </div>
              </div>
              <div class="flex-grow">
                <div class="flex flex-wrap items-center gap-2 mb-1">
                  <h3 class="text-base font-extrabold text-white">Astra 2.0</h3>
                  <span class="text-[10px] mono px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/30">Gemini 4 Argon Guide</span>
                  <span id="avatar-badge" class="text-[10px] mono px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300">Online</span>
                </div>
                <p class="text-xs text-slate-300 leading-relaxed">
                  "Welcome Rocket builders! Every project square below now has a <strong>Live Cloud Run Demo</strong> powered by <strong>Gemini 4 Argon</strong> and a complete <strong>Step-by-Step Reproduction Blueprint</strong>!"
                </p>
              </div>
            </div>
            <div class="mt-4 pt-3 border-t border-slate-800 flex flex-wrap justify-between gap-2">
              <button onclick="toggleVoiceIntro()" id="btn-voice-tour" class="px-3.5 py-2 rounded-xl text-xs font-bold bg-rose-600 hover:bg-rose-500 text-white transition shadow flex items-center gap-1.5">
                <span id="voice-icon">🎙️</span>
                <span id="voice-label">Play Argon Voice Briefing</span>
              </button>
              <button onclick="switchMainTab('keynote')" class="px-3.5 py-2 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white transition">
                🎤 Open 2-Hr Presentation Deck
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- PRIMARY NAVIGATION TABS (9 TABS) -->
      <nav class="flex flex-wrap justify-center gap-1.5 bg-slate-900/95 p-2 rounded-2xl border border-slate-800 shadow-2xl">
        <button onclick="switchMainTab('depts')" id="btn-depts" class="main-tab-btn px-3.5 py-2.5 rounded-xl text-xs font-bold transition bg-rose-600 text-white shadow">
          🏢 1. Use Case Catalog & Live Demos (33)
        </button>
        <button onclick="switchMainTab('account')" id="btn-account" class="main-tab-btn px-3.5 py-2.5 rounded-xl text-xs font-bold transition text-slate-300 hover:text-white hover:bg-slate-800">
          🎯 2. Rocket Account Research & AWS Win-Back
        </button>
        <button onclick="switchMainTab('keynote')" id="btn-keynote" class="main-tab-btn px-3.5 py-2.5 rounded-xl text-xs font-bold transition text-slate-300 hover:text-white hover:bg-slate-800">
          🎤 3. 2-Hr Presentation (1h GE + 1h Antigravity)
        </button>
        <button onclick="switchMainTab('alldocs')" id="btn-alldocs" class="main-tab-btn px-3.5 py-2.5 rounded-xl text-xs font-bold transition text-slate-300 hover:text-white hover:bg-slate-800">
          📘 4. Reproduction Docs (All 33 Blueprints)
        </button>
        <button onclick="switchMainTab('translator')" id="btn-translator" class="main-tab-btn px-3.5 py-2.5 rounded-xl text-xs font-bold transition text-slate-300 hover:text-white hover:bg-slate-800">
          🔄 5. Tool Translator (Claude/Sierra → GCP)
        </button>
        <button onclick="switchMainTab('levels')" id="btn-levels" class="main-tab-btn px-3.5 py-2.5 rounded-xl text-xs font-bold transition text-slate-300 hover:text-white hover:bg-slate-800">
          📚 6. L100/L200/L300 Tracks
        </button>
        <button onclick="switchMainTab('glossary')" id="btn-glossary" class="main-tab-btn px-3.5 py-2.5 rounded-xl text-xs font-bold transition text-slate-300 hover:text-white hover:bg-slate-800">
          📖 7. Service Glossary
        </button>
        <button onclick="switchMainTab('resources')" id="btn-resources" class="main-tab-btn px-3.5 py-2.5 rounded-xl text-xs font-bold transition text-slate-300 hover:text-white hover:bg-slate-800">
          🎓 8. Codelabs, GitHub & Videos
        </button>
        <button onclick="switchMainTab('cocreate')" id="btn-cocreate" class="main-tab-btn px-3.5 py-2.5 rounded-xl text-xs font-bold transition text-slate-300 hover:text-white hover:bg-slate-800">
          💡 9. Co-Create & Argon Pitch Coach
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

  <!-- MAIN CONTAINER -->
  <main class="max-w-7xl mx-auto px-6 py-10 flex-grow w-full">

    <!-- TAB 1: 33-SQUARE DEPARTMENT PROJECT CATALOG -->
    <section id="tab-depts" class="tab-content active space-y-8">
      <div class="text-center max-w-3xl mx-auto">
        <h2 class="text-3xl font-extrabold mb-2">33 Interactive Use Cases Across 7 Dedicated Cloud Run Suites</h2>
        <p class="text-sm" style="color:var(--text-muted);">
          Every single square below features a <strong>🚀 Live Private Cloud Run Demo</strong> (with a custom domain UI/UX powered by <code>gemini-4-argon</code>), an <strong>⚡ Instant Preview</strong>, and a <strong>📘 Complete Step-by-Step Reproduction Documentation Link</strong>.
        </p>
      </div>

      <div class="flex flex-wrap justify-center gap-2" id="dept-buttons"></div>
      <div id="dept-banner" class="rounded-2xl p-6 border border-rose-500/30 bg-gradient-to-r from-slate-900 via-rose-950/30 to-indigo-950/30"></div>
      <div id="dept-projects" class="grid md:grid-cols-2 gap-6"></div>
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

    function renderProjectCard(p, deptTitle, deptDemoUrl) {{
      const liveDemoHref = `${{deptDemoUrl || p.demo_service_url}}${{(deptDemoUrl && !deptDemoUrl.includes('?')) ? '?case=' + p.code : ''}}&auth_token=${{AUTH_TOKEN}}`;
      const docsHref = `/docs/${{p.code}}?auth_token=${{AUTH_TOKEN}}`;
      const stackHtml = (p.gcpStack || []).map(s =>
        `<span class="px-2 py-0.5 rounded text-[10px] mono bg-slate-950 text-indigo-300 border border-slate-800">${{s}}</span>`
      ).join("");

      return `
        <div class="card-surface hover:border-rose-500/50 rounded-2xl p-6 flex flex-col justify-between transition shadow-xl">
          <div>
            <div class="flex flex-wrap items-center justify-between gap-2 mb-2.5">
              <span class="text-xs font-bold mono text-rose-400">SQUARE ${{p.code}} • ${{p.tool}}</span>
              <span class="px-2.5 py-0.5 rounded-full text-xs font-bold border ${{badgeClass(p.level)}}">${{p.level}}</span>
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
                🚀 Launch Live Demo ↗
              </a>
              <a href="${{docsHref}}" target="_blank"
                 class="px-3.5 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-cyan-300 text-xs font-bold mono text-center transition">
                📘 Reproduction Docs ↗
              </a>
            </div>
            <button onclick="openQuickRun('${{p.code}}')"
                    class="w-full py-2 rounded-xl bg-slate-950 hover:bg-slate-900 border border-slate-800 text-[11px] font-bold mono text-slate-300 transition">
              ⚡ Quick Inline Argon Execution & Sandbox Preview
            </button>
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

    // Voice Tour
    let isSpeaking = false;
    const introScript = "Welcome Rocket Companies builders across Detroit and Chennai! I am Astra 2.0, powered by Google's new frontier model, Gemini 4 Argon. Every single project square in this portal now launches a live, private Cloud Run application tailored to your business unit—spanning Rocket Mortgage Origination, Rocket Logic Underwriting, Mr. Cooper Servicing, Redfin and Rocket Money Growth, CFPB Compliance, and Google Antigravity with DeepMind CodeMender. Click Launch Live Demo on any square to test real payloads on GCP, or open its Reproduction Blueprint to clone the architecture in minutes!";

    function toggleVoiceIntro() {{
      if (!('speechSynthesis' in window)) return alert("Speech Synthesis not supported.");
      if (isSpeaking) {{
        window.speechSynthesis.cancel();
        isSpeaking = false;
        document.getElementById("voice-label").innerText = "Play Argon Voice Briefing";
        return;
      }}
      window.speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(introScript);
      u.rate = 1.02;
      u.onstart = () => {{ isSpeaking = true; document.getElementById("voice-label").innerText = "Stop Voice Briefing"; }};
      u.onend = () => {{ isSpeaking = false; document.getElementById("voice-label").innerText = "Play Argon Voice Briefing"; }};
      window.speechSynthesis.speak(u);
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
      filterByLevel("L100");
      filterTranslator("all");
    }});
  </script>
</body>
</html>"""
