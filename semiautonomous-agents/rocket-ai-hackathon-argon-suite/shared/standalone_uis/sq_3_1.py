# -*- coding: utf-8 -*-
"""Square 3.1: Annual Escrow Shortage Resolution Journey (GECX + Gemini Enterprise streamAssist)
Visual Design: Mr. Cooper x Rocket Consumer Mobile/Web Banking App (#F0F9FF soft sky canvas,
#0D9488 teal brand header, rounded 24px consumer cards, Google Fonts DM Sans + JetBrains Mono)."""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_3_1(auth_token: str) -> str:
    ge_ui_url = "https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mr. Cooper x Rocket Servicing | Annual Escrow Analysis & Shortage Resolution [3.1]</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;0,9..40,800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --sky-canvas: #F0F9FF;
      --teal-brand: #0D9488;
      --teal-dark: #0F766E;
      --card-radius: 24px;
    }}
    body {{
      font-family: 'DM Sans', sans-serif;
      background-color: var(--sky-canvas);
      background-image: radial-gradient(circle at 15% 10%, rgba(13, 148, 136, 0.08) 0%, transparent 45%),
                        radial-gradient(circle at 85% 80%, rgba(2, 132, 199, 0.08) 0%, transparent 50%);
      color: #0F172A;
      margin: 0;
    }}
    .mono {{ font-family: 'JetBrains Mono', monospace; }}
    .consumer-card {{
      background: #FFFFFF;
      border-radius: 24px;
      border: 1px solid #E0F2FE;
      box-shadow: 0 12px 32px -8px rgba(13, 148, 136, 0.08), 0 4px 12px -2px rgba(15, 23, 42, 0.04);
    }}
    .option-card {{
      border-radius: 20px;
      border: 2px solid #E2E8F0;
      transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
      cursor: pointer;
    }}
    .option-card:hover {{
      transform: translateY(-2px);
      border-color: #5EEAD4;
    }}
    .option-card.selected {{
      border-color: #0D9488;
      background: linear-gradient(180deg, #F0FDFA 0%, #FFFFFF 100%);
      box-shadow: 0 10px 25px -5px rgba(13, 148, 136, 0.18);
    }}
    input[type="range"] {{
      accent-color: #0D9488;
    }}
    .shrinking-shining-ink {{
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background: radial-gradient(circle at 30% 30%, #ffffff, #0D9488, #0284C7);
      animation: inkPulse 1.2s ease-in-out infinite;
      display: inline-block;
    }}
    @keyframes inkPulse {{
      0%, 100% {{ transform: scale(1); opacity: 0.95; }}
      50% {{ transform: scale(0.6); opacity: 0.5; }}
    }}
  </style>
</head>
<body class="min-h-screen pb-24">

  <!-- TOP MR. COOPER x ROCKET CONSUMER BANKING APP HEADER -->
  <header class="sticky top-0 z-40 shadow-md" style="background: linear-gradient(135deg, #0D9488 0%, #0F766E 55%, #115E59 100%); color: #FFFFFF;">
    <div class="max-w-7xl mx-auto px-6 py-4 flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-3.5">
        <div class="w-11 h-11 rounded-2xl bg-white/15 backdrop-blur flex items-center justify-center border border-white/25 shadow-inner">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
          </svg>
        </div>
        <div>
          <div class="flex items-center gap-2">
            <span class="text-xs font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-teal-950/40 text-teal-100 mono border border-teal-300/30">
              MR. COOPER x ROCKET SERVICING
            </span>
            <span class="text-xs mono text-teal-100/90">Loan #0498-2910-MC • Troy, MI 48084</span>
          </div>
          <h1 class="text-xl md:text-2xl font-extrabold tracking-tight mt-0.5">
            2026 Annual Escrow Account Review &amp; Self-Service Resolution
          </h1>
        </div>
      </div>

      <!-- Right App Bar Controls: Inline Model Selector + Real Gemini Enterprise UI Link -->
      <div class="flex flex-wrap items-center gap-3">
        <div class="flex items-center gap-2 bg-teal-950/45 border border-white/20 rounded-full px-3.5 py-1.5">
          <span class="w-2 h-2 rounded-full bg-emerald-300 animate-pulse"></span>
          <label for="app-model-select" class="text-[11px] mono uppercase font-semibold text-teal-100">AI Engine:</label>
          <select id="app-model-select" onchange="window.syncSelectedModel(this.value)"
                  class="bg-transparent text-white text-xs font-bold mono focus:outline-none cursor-pointer">
            <option value="gemini-4-argon" class="bg-slate-900 text-sky-300">gemini-4-argon (Frontier Global)</option>
            <option value="gemini-3.8-flash" selected class="bg-slate-900 text-emerald-300">gemini-3.8-flash (GECX + streamAssist)</option>
          </select>
        </div>
        <a href="{ge_ui_url}" target="_blank"
           class="inline-flex items-center gap-1.5 px-4 py-2 rounded-full text-xs font-bold bg-white text-teal-900 shadow hover:bg-teal-50 transition mono">
          <span>✨ Real Gemini Enterprise UI ↗</span>
        </a>
        <button onclick="window.runLiveVertexAI()" id="top-run-btn"
                class="inline-flex items-center gap-1.5 px-4 py-2 rounded-full text-xs font-bold bg-amber-400 text-slate-950 shadow hover:bg-amber-300 transition mono">
          <span>⚡ Re-Synthesize Analysis</span>
        </button>
      </div>
    </div>
  </header>

  <!-- EMPATHETIC ZERO-JARGON REASSURANCE BANNER -->
  <div class="max-w-7xl mx-auto px-6 pt-6">
    <div class="consumer-card p-5 bg-gradient-to-r from-teal-50/90 via-white to-sky-50/90 border-l-4 border-l-teal-600 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div class="flex items-start gap-3.5">
        <div class="w-10 h-10 rounded-2xl bg-teal-600 text-white flex items-center justify-center shrink-0 font-bold text-lg shadow">
          ✓
        </div>
        <div>
          <div class="text-xs font-bold uppercase tracking-wider text-teal-700 mono">Good News First — Your Fixed Mortgage Rate Did Not Change</div>
          <p id="ai-empathetic-headline" class="text-sm md:text-base font-semibold text-slate-800 mt-0.5 leading-snug">
            Your <strong>5.250% fixed interest rate</strong> and <strong>$1,840.00/mo Principal &amp; Interest</strong> are 100% locked. The adjustment below comes strictly from Oakland County property tax and homeowners insurance billing increases.
          </p>
        </div>
      </div>
      <div class="shrink-0 flex items-center gap-2">
        <span id="sandbox-status-pill" class="px-3 py-1 rounded-full text-xs font-bold mono bg-teal-100 text-teal-800 border border-teal-300">
          RESPA 12 CFR § 1024.17 Verified
        </span>
      </div>
    </div>
  </div>

  <!-- MAIN 12-COLUMN CONSUMER BANKING WORKSPACE -->
  <main class="max-w-7xl mx-auto px-6 py-6 grid lg:grid-cols-12 gap-6">

    <!-- LEFT 7 COLUMNS: WATERFALL VISUALIZER + INTERACTIVE HIKE SLIDERS + GEMINI ENTERPRISE STREAMASSIST CHAT -->
    <div class="lg:col-span-7 space-y-6">

      <!-- 1. 2025 vs 2026 COUNTY PROPERTY TAX & HAZARD INSURANCE WATERFALL CHART -->
      <section class="consumer-card p-6">
        <div class="flex flex-wrap items-center justify-between gap-2 pb-4 mb-5 border-b border-slate-100">
          <div>
            <span class="text-[11px] font-bold uppercase tracking-wider text-teal-700 mono">Step 1 • Visual Escrow Breakdown</span>
            <h2 class="text-lg font-extrabold text-slate-900">2025 vs. 2026 County Property Tax &amp; Hazard Insurance Waterfall</h2>
          </div>
          <div class="flex items-center gap-3 text-xs font-semibold">
            <span class="inline-flex items-center gap-1.5"><span class="w-3 h-3 rounded-sm bg-slate-300 inline-block"></span> 2025 Billed</span>
            <span class="inline-flex items-center gap-1.5"><span class="w-3 h-3 rounded-sm bg-teal-600 inline-block"></span> 2026 Actual</span>
            <span class="inline-flex items-center gap-1.5"><span class="w-3 h-3 rounded-sm bg-amber-500 inline-block"></span> Monthly Hike</span>
          </div>
        </div>

        <!-- Interactive Tax & Insurance Hike Sliders -->
        <div class="grid sm:grid-cols-3 gap-4 p-4 rounded-2xl bg-sky-50/80 border border-sky-100 mb-6">
          <div>
            <div class="flex justify-between text-xs font-bold mb-1">
              <span class="text-slate-600">2026 Property Tax/Yr</span>
              <span id="lbl-new-tax" class="mono text-teal-700">$6,000/yr</span>
            </div>
            <input id="slider-new-tax" type="range" min="4920" max="8400" step="120" value="6000"
                   oninput="window.updateEscrowSliders()" class="w-full cursor-pointer">
            <div class="flex justify-between text-[10px] mono text-slate-400 mt-0.5">
              <span>2025: $4,920</span>
              <span id="lbl-tax-delta" class="text-amber-700 font-bold">+$90/mo</span>
            </div>
          </div>

          <div>
            <div class="flex justify-between text-xs font-bold mb-1">
              <span class="text-slate-600">2026 Hazard Ins/Yr</span>
              <span id="lbl-new-ins" class="mono text-teal-700">$2,280/yr</span>
            </div>
            <input id="slider-new-ins" type="range" min="1680" max="3600" step="120" value="2280"
                   oninput="window.updateEscrowSliders()" class="w-full cursor-pointer">
            <div class="flex justify-between text-[10px] mono text-slate-400 mt-0.5">
              <span>2025: $1,680</span>
              <span id="lbl-ins-delta" class="text-amber-700 font-bold">+$50/mo</span>
            </div>
          </div>

          <div>
            <div class="flex justify-between text-xs font-bold mb-1">
              <span class="text-slate-600">Escrow Shortage Gap</span>
              <span id="lbl-shortage" class="mono text-rose-600">$1,740</span>
            </div>
            <input id="slider-shortage" type="range" min="600" max="3600" step="60" value="1740"
                   oninput="window.updateEscrowSliders()" class="w-full cursor-pointer">
            <div class="flex justify-between text-[10px] mono text-slate-400 mt-0.5">
              <span>RESPA 2-Mo Cushion</span>
              <span id="lbl-spread12-delta" class="text-rose-600 font-bold">$145/mo (12m)</span>
            </div>
          </div>
        </div>

        <!-- Visual Waterfall Comparison Bars -->
        <div class="space-y-4" id="waterfall-chart-rows">
          <!-- Row 1: Principal & Interest -->
          <div class="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80">
            <div class="flex items-center justify-between text-xs font-bold mb-1.5">
              <span class="text-slate-700">1. Principal &amp; Interest (Locked @ 5.250% Fixed)</span>
              <div class="mono flex items-center gap-2">
                <span class="text-slate-500">$1,840.00/mo → $1,840.00/mo</span>
                <span class="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px]">$0.00 Change</span>
              </div>
            </div>
            <div class="w-full h-3 rounded-full bg-slate-200 overflow-hidden flex">
              <div class="bg-teal-600 h-full" style="width: 68%"></div>
            </div>
          </div>

          <!-- Row 2: Oakland County Property Tax -->
          <div class="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80">
            <div class="flex items-center justify-between text-xs font-bold mb-1.5">
              <span class="text-slate-700">2. City of Troy / Oakland County Property Tax</span>
              <div class="mono flex items-center gap-2">
                <span class="text-slate-500" id="wf-tax-comparison">$410.00/mo → $500.00/mo</span>
                <span class="px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 text-[10px]" id="wf-tax-badge">+$90.00/mo</span>
              </div>
            </div>
            <div class="w-full h-3 rounded-full bg-slate-200 overflow-hidden flex">
              <div class="bg-slate-400 h-full" style="width: 41%"></div>
              <div id="wf-tax-bar" class="bg-amber-500 h-full transition-all duration-300" style="width: 14%"></div>
            </div>
          </div>

          <!-- Row 3: Homeowners Hazard Insurance -->
          <div class="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80">
            <div class="flex items-center justify-between text-xs font-bold mb-1.5">
              <span class="text-slate-700">3. Homeowners Hazard Insurance Premium</span>
              <div class="mono flex items-center gap-2">
                <span class="text-slate-500" id="wf-ins-comparison">$140.00/mo → $190.00/mo</span>
                <span class="px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 text-[10px]" id="wf-ins-badge">+$50.00/mo</span>
              </div>
            </div>
            <div class="w-full h-3 rounded-full bg-slate-200 overflow-hidden flex">
              <div class="bg-slate-400 h-full" style="width: 22%"></div>
              <div id="wf-ins-bar" class="bg-amber-500 h-full transition-all duration-300" style="width: 10%"></div>
            </div>
          </div>

          <!-- Row 4: Past-Year Advancement + RESPA 2-Month Cushion Shortage -->
          <div class="p-3.5 rounded-2xl bg-rose-50/60 border border-rose-200">
            <div class="flex items-center justify-between text-xs font-bold mb-1.5">
              <span class="text-rose-950">4. Escrow Shortage Catch-Up (2025 Tax/Ins Advance + 2-Mo RESPA Cushion)</span>
              <div class="mono flex items-center gap-2">
                <span class="text-rose-700" id="wf-shortage-total">Total Shortage: $1,740.00</span>
                <span class="px-2 py-0.5 rounded-full bg-rose-100 text-rose-800 text-[10px]" id="wf-shortage-badge">+$145.00/mo (12-Mo)</span>
              </div>
            </div>
            <div class="w-full h-3 rounded-full bg-rose-100 overflow-hidden flex">
              <div id="wf-shortage-bar" class="bg-rose-500 h-full transition-all duration-300" style="width: 32%"></div>
            </div>
          </div>
        </div>
      </section>

      <!-- 2. LIVE GEMINI ENTERPRISE streamAssist CONSUMER Q&A CHAT BAR -->
      <section class="consumer-card p-6">
        <div class="flex flex-wrap items-center justify-between gap-2 pb-3 mb-4 border-b border-slate-100">
          <div class="flex items-center gap-2.5">
            <span class="w-3 h-3 rounded-full bg-teal-600 animate-ping"></span>
            <div>
              <span class="text-[11px] font-bold uppercase tracking-wider text-teal-700 mono">Live Grounded Consumer Concierge</span>
              <h3 class="text-base font-extrabold text-slate-900">Ask Gemini Enterprise <code>streamAssist</code> About Your Escrow Statement</h3>
            </div>
          </div>
          <a href="{ge_ui_url}" target="_blank"
             class="px-3 py-1.5 rounded-full text-xs font-bold mono bg-teal-50 text-teal-800 border border-teal-200 hover:bg-teal-100 transition">
            ✨ Real Gemini Enterprise UI ↗
          </a>
        </div>

        <!-- Preset Consumer Questions -->
        <div class="flex flex-wrap gap-2 mb-3">
          <button onclick="window.askEscrowStreamAssist('Why did my payment go up $285/month if I have a fixed 5.25% mortgage rate?')"
                  class="text-xs px-3 py-1.5 rounded-full bg-slate-100 hover:bg-teal-50 text-slate-700 hover:text-teal-800 font-medium border border-slate-200 transition">
            💬 "Why did my payment jump if my rate is fixed?"
          </button>
          <button onclick="window.askEscrowStreamAssist('Is there any interest or fee charged if I spread the $1,740 shortage over 12 months?')"
                  class="text-xs px-3 py-1.5 rounded-full bg-slate-100 hover:bg-teal-50 text-slate-700 hover:text-teal-800 font-medium border border-slate-200 transition">
            💬 "Is the 12-month shortage spread 0% interest?"
          </button>
          <button onclick="window.askEscrowStreamAssist('How do I verify my Michigan Principal Residence Exemption (PRE) in Troy?')"
                  class="text-xs px-3 py-1.5 rounded-full bg-slate-100 hover:bg-teal-50 text-slate-700 hover:text-teal-800 font-medium border border-slate-200 transition">
            💬 "How do I check my Michigan Homestead PRE?"
          </button>
        </div>

        <div class="flex gap-2">
          <input id="escrow-chat-input" type="text"
                 value="Why did my monthly payment increase by $285/month if I have a fixed 5.25% interest rate, and which shortage option is best?"
                 placeholder="Ask anything about your Oakland County taxes, insurance, or RESPA cushion..."
                 class="flex-1 px-4 py-2.5 rounded-2xl bg-slate-50 border border-slate-200 text-xs md:text-sm focus:outline-none focus:border-teal-600">
          <button onclick="window.askEscrowStreamAssist()"
                  class="px-5 py-2.5 rounded-2xl bg-teal-600 hover:bg-teal-700 text-white font-bold text-xs md:text-sm shadow transition shrink-0">
            Ask Gemini ↗
          </button>
        </div>

        <!-- StreamAssist Grounded Answer Output -->
        <div id="escrow-streamassist-output" class="mt-4 p-4 rounded-2xl bg-slate-50 border border-slate-200/90 text-xs md:text-sm text-slate-700 leading-relaxed">
          <div class="flex items-center justify-between text-[11px] mono text-teal-700 font-bold mb-1.5">
            <span>✅ GECX + GEMINI ENTERPRISE STREAMASSIST GROUNDED EXPLANATION</span>
            <span id="streamassist-latency-pill">Engine: gemini-enterprise-17877637_1787763712023</span>
          </div>
          <div id="escrow-streamassist-body">
            Your Principal &amp; Interest is locked at <strong>$1,840.00/mo (5.250% fixed)</strong>. The increase has two parts:
            (1) <strong>+$140.00/mo permanent base escrow adjustment</strong> because City of Troy property taxes rose +$90/mo and hazard insurance rose +$50/mo; and
            (2) <strong>+$145.00/mo temporary 12-month shortage catch-up</strong> ($1,740.00 divided by 12 months at <strong>0% interest</strong>). Select any of the 3 options on the right to customize your March 1 AutoPay!
          </div>
        </div>
      </section>
    </div>

    <!-- RIGHT 5 COLUMNS: 3 CLICKABLE CONSUMER RESOLUTION CARDS + INTERACTIVE MONTHLY AUTOPAY RECEIPT -->
    <div class="lg:col-span-5 space-y-6">

      <!-- 3 CLICKABLE CONSUMER RESOLUTION CARDS -->
      <section class="consumer-card p-6">
        <div class="mb-4">
          <span class="text-[11px] font-bold uppercase tracking-wider text-teal-700 mono">Step 2 • Choose Your Resolution Plan</span>
          <h2 class="text-lg font-extrabold text-slate-900">3 One-Tap Escrow Shortage Options</h2>
          <p class="text-xs text-slate-500 mt-0.5">Click any option below to preview your updated March 1, 2026 AutoPay receipt.</p>
        </div>

        <div class="space-y-3.5">
          <!-- Option 1: Pay Lump Sum -->
          <div id="opt-card-1" onclick="window.selectResolutionOption(1)" class="option-card p-4">
            <div class="flex items-start justify-between gap-2">
              <div class="flex items-center gap-2.5">
                <div id="opt-radio-1" class="w-5 h-5 rounded-full border-2 border-slate-300 flex items-center justify-center text-xs font-bold"></div>
                <div>
                  <div class="text-sm font-extrabold text-slate-900">Option 1: Pay Lump Sum Today</div>
                  <div class="text-xs text-slate-500">Eliminate the entire shortage upfront via one-time ACH</div>
                </div>
              </div>
              <span class="px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 text-[11px] font-bold mono">Lowest Monthly</span>
            </div>
            <div class="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs mono">
              <span class="text-slate-600">Upfront Today: <strong id="opt1-upfront" class="text-slate-900">$1,740.00</strong></span>
              <span class="text-teal-700 font-bold text-sm" id="opt1-monthly">$2,530.00/mo</span>
            </div>
          </div>

          <!-- Option 2: 12-Month Spread (Default Selected) -->
          <div id="opt-card-2" onclick="window.selectResolutionOption(2)" class="option-card selected p-4">
            <div class="flex items-start justify-between gap-2">
              <div class="flex items-center gap-2.5">
                <div id="opt-radio-2" class="w-5 h-5 rounded-full border-2 border-teal-600 bg-teal-600 text-white flex items-center justify-center text-xs font-bold">✓</div>
                <div>
                  <div class="text-sm font-extrabold text-slate-900">Option 2: 12-Month 0% Spread</div>
                  <div class="text-xs text-slate-500">Interest-free RESPA standard spread over 12 payments</div>
                </div>
              </div>
              <span class="px-2.5 py-1 rounded-full bg-teal-100 text-teal-800 text-[11px] font-bold mono">Most Popular • $0 Now</span>
            </div>
            <div class="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs mono">
              <span class="text-slate-600">Upfront Today: <strong class="text-slate-900">$0.00</strong> (+<span id="opt2-spread">$145.00</span>/mo)</span>
              <span class="text-teal-700 font-bold text-sm" id="opt2-monthly">$2,675.00/mo</span>
            </div>
          </div>

          <!-- Option 3: 24-Month Hardship Spread -->
          <div id="opt-card-3" onclick="window.selectResolutionOption(3)" class="option-card p-4">
            <div class="flex items-start justify-between gap-2">
              <div class="flex items-center gap-2.5">
                <div id="opt-radio-3" class="w-5 h-5 rounded-full border-2 border-slate-300 flex items-center justify-center text-xs font-bold"></div>
                <div>
                  <div class="text-sm font-extrabold text-slate-900">Option 3: 24-Month Hardship Spread</div>
                  <div class="text-xs text-slate-500">Extended 0% cushion relief to cut monthly shock in half</div>
                </div>
              </div>
              <span class="px-2.5 py-1 rounded-full bg-sky-100 text-sky-800 text-[11px] font-bold mono">Gentle Cushion</span>
            </div>
            <div class="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs mono">
              <span class="text-slate-600">Upfront Today: <strong class="text-slate-900">$0.00</strong> (+<span id="opt3-spread">$72.50</span>/mo)</span>
              <span class="text-teal-700 font-bold text-sm" id="opt3-monthly">$2,602.50/mo</span>
            </div>
          </div>
        </div>
      </section>

      <!-- INTERACTIVE MONTHLY AUTOPAY RECEIPT -->
      <section class="consumer-card p-6 bg-gradient-to-b from-white to-teal-50/40 relative overflow-hidden">
        <div class="flex items-center justify-between pb-3 mb-4 border-b border-dashed border-slate-300">
          <div>
            <div class="text-[10px] font-bold uppercase tracking-widest text-teal-700 mono">Official Mr. Cooper AutoPay Preview</div>
            <h3 class="text-base font-extrabold text-slate-900">Effective March 1, 2026 Draft Receipt</h3>
          </div>
          <span id="receipt-plan-badge" class="px-2.5 py-1 rounded-full text-[11px] font-bold mono bg-teal-600 text-white">
            Option 2: 12-Mo Spread
          </span>
        </div>

        <div class="space-y-2.5 text-xs md:text-sm">
          <div class="flex justify-between items-center py-1">
            <span class="text-slate-600">Principal &amp; Interest (5.250% Fixed)</span>
            <span class="mono font-bold text-slate-900">$1,840.00</span>
          </div>
          <div class="flex justify-between items-center py-1">
            <span class="text-slate-600">2026 Base Property Tax Escrow</span>
            <span id="rcpt-tax" class="mono font-bold text-slate-900">$500.00</span>
          </div>
          <div class="flex justify-between items-center py-1">
            <span class="text-slate-600">2026 Base Hazard Insurance Escrow</span>
            <span id="rcpt-ins" class="mono font-bold text-slate-900">$190.00</span>
          </div>
          <div class="flex justify-between items-center py-1.5 px-3 rounded-xl bg-teal-50 border border-teal-200/80">
            <span class="text-teal-900 font-semibold" id="rcpt-shortage-label">Monthly Shortage Catch-Up (12 Mos @ 0%)</span>
            <span id="rcpt-shortage-mo" class="mono font-extrabold text-teal-800">$145.00</span>
          </div>
        </div>

        <div class="mt-4 pt-4 border-t-2 border-slate-900/10 flex items-baseline justify-between">
          <div>
            <div class="text-xs font-bold uppercase text-slate-500 mono">New Monthly AutoPay</div>
            <div class="text-[11px] text-slate-500">Previous 2025 Payment: <span class="mono line-through">$2,390.00/mo</span></div>
          </div>
          <div class="text-right">
            <div id="rcpt-total-monthly" class="text-2xl font-extrabold text-teal-700 mono">$2,675.00<span class="text-xs font-normal text-slate-500">/mo</span></div>
            <div id="rcpt-upfront-due" class="text-[11px] font-bold mono text-emerald-700">One-Time ACH Today: $0.00</div>
          </div>
        </div>

        <button onclick="window.confirmAutoPaySelection()" id="confirm-autopay-btn"
                class="mt-5 w-full py-3.5 px-4 rounded-2xl font-bold text-sm text-white shadow-lg transition transform active:scale-[0.99] flex items-center justify-center gap-2"
                style="background: linear-gradient(135deg, #0D9488 0%, #0284C7 100%);">
          <span>✓ Lock In Selected Escrow Plan &amp; Update AutoPay</span>
        </button>

        <div id="autopay-confirmation-toast" class="hidden mt-3 p-3 rounded-xl bg-emerald-50 border border-emerald-300 text-emerald-900 text-xs font-semibold mono text-center"></div>
      </section>
    </div>
  </main>

  <script>
    let currentOption = 2;
    const BASE_PI = 1840.00;
    const OLD_TAX_YR = 4920.00;
    const OLD_INS_YR = 1680.00;

    function fmtMoney(n) {{
      return '$' + Number(n).toLocaleString('en-US', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
    }}

    window.selectResolutionOption = function(optNum) {{
      currentOption = optNum;
      [1, 2, 3].forEach(i => {{
        const card = document.getElementById('opt-card-' + i);
        const radio = document.getElementById('opt-radio-' + i);
        if (i === optNum) {{
          card.classList.add('selected');
          radio.className = 'w-5 h-5 rounded-full border-2 border-teal-600 bg-teal-600 text-white flex items-center justify-center text-xs font-bold';
          radio.innerText = '✓';
        }} else {{
          card.classList.remove('selected');
          radio.className = 'w-5 h-5 rounded-full border-2 border-slate-300 flex items-center justify-center text-xs font-bold';
          radio.innerText = '';
        }}
      }});
      window.recalcReceiptUI();
    }};

    window.recalcReceiptUI = function() {{
      const newTaxYr = parseFloat(document.getElementById('slider-new-tax').value || 6000);
      const newInsYr = parseFloat(document.getElementById('slider-new-ins').value || 2280);
      const shortage = parseFloat(document.getElementById('slider-shortage').value || 1740);

      const oldTaxMo = OLD_TAX_YR / 12.0;
      const oldInsMo = OLD_INS_YR / 12.0;
      const newTaxMo = newTaxYr / 12.0;
      const newInsMo = newInsYr / 12.0;
      const baseNewPiti = BASE_PI + newTaxMo + newInsMo;

      const spread12 = shortage / 12.0;
      const spread24 = shortage / 24.0;

      // Update slider labels
      document.getElementById('lbl-new-tax').innerText = '$' + newTaxYr.toLocaleString() + '/yr';
      document.getElementById('lbl-tax-delta').innerText = '+$' + Math.round(newTaxMo - oldTaxMo) + '/mo';
      document.getElementById('lbl-new-ins').innerText = '$' + newInsYr.toLocaleString() + '/yr';
      document.getElementById('lbl-ins-delta').innerText = '+$' + Math.round(newInsMo - oldInsMo) + '/mo';
      document.getElementById('lbl-shortage').innerText = '$' + shortage.toLocaleString();
      document.getElementById('lbl-spread12-delta').innerText = fmtMoney(spread12) + '/mo (12m)';

      // Update Waterfall Chart
      document.getElementById('wf-tax-comparison').innerText = fmtMoney(oldTaxMo) + '/mo → ' + fmtMoney(newTaxMo) + '/mo';
      document.getElementById('wf-tax-badge').innerText = '+' + fmtMoney(newTaxMo - oldTaxMo) + '/mo';
      document.getElementById('wf-ins-comparison').innerText = fmtMoney(oldInsMo) + '/mo → ' + fmtMoney(newInsMo) + '/mo';
      document.getElementById('wf-ins-badge').innerText = '+' + fmtMoney(newInsMo - oldInsMo) + '/mo';
      document.getElementById('wf-shortage-total').innerText = 'Total Shortage: ' + fmtMoney(shortage);
      document.getElementById('wf-shortage-badge').innerText = '+' + fmtMoney(spread12) + '/mo (12-Mo)';

      // Update Option Cards
      document.getElementById('opt1-upfront').innerText = fmtMoney(shortage);
      document.getElementById('opt1-monthly').innerText = fmtMoney(baseNewPiti) + '/mo';
      document.getElementById('opt2-spread').innerText = fmtMoney(spread12);
      document.getElementById('opt2-monthly').innerText = fmtMoney(baseNewPiti + spread12) + '/mo';
      document.getElementById('opt3-spread').innerText = fmtMoney(spread24);
      document.getElementById('opt3-monthly').innerText = fmtMoney(baseNewPiti + spread24) + '/mo';

      // Update Receipt
      document.getElementById('rcpt-tax').innerText = fmtMoney(newTaxMo);
      document.getElementById('rcpt-ins').innerText = fmtMoney(newInsMo);

      if (currentOption === 1) {{
        document.getElementById('receipt-plan-badge').innerText = 'Option 1: Lump Sum ACH';
        document.getElementById('rcpt-shortage-label').innerText = 'Monthly Shortage Catch-Up (Paid in Full)';
        document.getElementById('rcpt-shortage-mo').innerText = '$0.00';
        document.getElementById('rcpt-total-monthly').innerHTML = fmtMoney(baseNewPiti) + '<span class="text-xs font-normal text-slate-500">/mo</span>';
        document.getElementById('rcpt-upfront-due').innerText = 'One-Time ACH Today: ' + fmtMoney(shortage);
      }} else if (currentOption === 2) {{
        document.getElementById('receipt-plan-badge').innerText = 'Option 2: 12-Mo Spread';
        document.getElementById('rcpt-shortage-label').innerText = 'Monthly Shortage Catch-Up (12 Mos @ 0%)';
        document.getElementById('rcpt-shortage-mo').innerText = fmtMoney(spread12);
        document.getElementById('rcpt-total-monthly').innerHTML = fmtMoney(baseNewPiti + spread12) + '<span class="text-xs font-normal text-slate-500">/mo</span>';
        document.getElementById('rcpt-upfront-due').innerText = 'One-Time ACH Today: $0.00';
      }} else {{
        document.getElementById('receipt-plan-badge').innerText = 'Option 3: 24-Mo Hardship Spread';
        document.getElementById('rcpt-shortage-label').innerText = 'Monthly Shortage Catch-Up (24 Mos @ 0%)';
        document.getElementById('rcpt-shortage-mo').innerText = fmtMoney(spread24);
        document.getElementById('rcpt-total-monthly').innerHTML = fmtMoney(baseNewPiti + spread24) + '<span class="text-xs font-normal text-slate-500">/mo</span>';
        document.getElementById('rcpt-upfront-due').innerText = 'One-Time ACH Today: $0.00';
      }}
    }};

    let sandboxTimer = null;
    window.updateEscrowSliders = function() {{
      window.recalcReceiptUI();
      clearTimeout(sandboxTimer);
      sandboxTimer = setTimeout(async () => {{
        const newTaxYr = parseFloat(document.getElementById('slider-new-tax').value || 6000);
        const newInsYr = parseFloat(document.getElementById('slider-new-ins').value || 2280);
        const shortage = parseFloat(document.getElementById('slider-shortage').value || 1740);
        try {{
          const res = await fetch('/api/sandbox', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
              code: '3.1',
              action: 'calc_escrow_shortage',
              params: {{
                pi_monthly: BASE_PI,
                old_tax_yr: OLD_TAX_YR,
                old_ins_yr: OLD_INS_YR,
                new_tax_yr: newTaxYr,
                new_ins_yr: newInsYr,
                shortage_total: shortage
              }}
            }})
          }});
          const data = await res.json();
          const pill = document.getElementById('sandbox-status-pill');
          if (pill && data.execution_ms !== undefined) {{
            pill.innerText = `gVisor Sandbox Verified (${{data.execution_ms}}ms)`;
          }}
        }} catch (e) {{}}
      }}, 180);
    }};

    window.askEscrowStreamAssist = async function(presetText) {{
      const inp = document.getElementById('escrow-chat-input');
      if (presetText && inp) inp.value = presetText;
      const query = inp ? inp.value : 'Explain my escrow shortage options.';
      const bodyEl = document.getElementById('escrow-streamassist-body');
      const latEl = document.getElementById('streamassist-latency-pill');
      if (bodyEl) {{
        bodyEl.innerHTML = `<span class="inline-flex items-center gap-2 text-teal-700 font-semibold"><span class="shrinking-shining-ink"></span> Querying live Gemini Enterprise Discovery Engine v1alpha <code>streamAssist</code>...</span>`;
      }}
      try {{
        const res = await fetch('/api/stream-assist', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ code: '3.1', query: query }})
        }});
        const data = await res.json();
        if (latEl) {{
          latEl.innerText = `streamAssist v1alpha • ${{data.latency_ms || 320}}ms`;
        }}
        if (bodyEl) {{
          const txt = (data.answer_markdown || 'Grounded explanation ready.').replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>').replace(/\\n/g, '<br>');
          bodyEl.innerHTML = txt;
        }}
      }} catch (err) {{
        if (bodyEl) bodyEl.innerText = 'Error calling streamAssist: ' + err.message;
      }}
    }};

    window.confirmAutoPaySelection = function() {{
      const toast = document.getElementById('autopay-confirmation-toast');
      const planNames = {{ 1: 'Option 1 (Lump Sum ACH)', 2: 'Option 2 (12-Month 0% Spread)', 3: 'Option 3 (24-Month Hardship Spread)' }};
      const totalTxt = document.getElementById('rcpt-total-monthly').innerText;
      toast.classList.remove('hidden');
      toast.innerHTML = `✅ Confirmed! Your Mr. Cooper AutoPay is updated to <strong>${{planNames[currentOption]}}</strong> (${{totalTxt}}) effective March 1, 2026. Confirmation #MC-ESC-2026-8841.`;
    }};

    window.runLiveVertexAI = async function() {{
      const btn = document.getElementById('top-run-btn');
      const headline = document.getElementById('ai-empathetic-headline');
      const bodyEl = document.getElementById('escrow-streamassist-body');
      const newTaxYr = parseFloat(document.getElementById('slider-new-tax').value || 6000);
      const newInsYr = parseFloat(document.getElementById('slider-new-ins').value || 2280);
      const shortage = parseFloat(document.getElementById('slider-shortage').value || 1740);
      const scenarioInput = document.getElementById('scenario-input') ? document.getElementById('scenario-input').value : '';

      if (btn) btn.innerHTML = `<span class="shrinking-shining-ink"></span> <span>Synthesizing...</span>`;
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '3.1',
            model: window.getSelectedModel(),
            user_input: scenarioInput,
            params: {{
              pi_monthly: BASE_PI,
              old_tax_yr: OLD_TAX_YR,
              old_ins_yr: OLD_INS_YR,
              new_tax_yr: newTaxYr,
              new_ins_yr: newInsYr,
              shortage_total: shortage
            }}
          }})
        }});
        const data = await res.json();
        const sd = data.structured_data || {{}};
        if (sd.empathetic_headline && headline) {{
          headline.innerHTML = sd.empathetic_headline;
        }} else if (data.vertex && data.vertex.response_markdown && headline) {{
          headline.innerHTML = data.vertex.response_markdown;
        }}
        if (sd.executive_summary && bodyEl) {{
          bodyEl.innerHTML = `<strong>[${{data.vertex ? data.vertex.model_used : window.getSelectedModel()}} Synthesis]:</strong> ` + sd.executive_summary;
        }}
        const pill = document.getElementById('sandbox-status-pill');
        if (pill && data.vertex) {{
          pill.innerText = `Verified • ${{data.vertex.model_used}} (${{data.vertex.latency_ms}}ms)`;
        }}
      }} catch (e) {{
        console.error(e);
      }} finally {{
        if (btn) btn.innerHTML = `<span>⚡ Re-Synthesize Analysis</span>`;
      }}
    }};

    document.addEventListener('DOMContentLoaded', () => {{
      window.recalcReceiptUI();
    }});
  </script>

  {render_floating_control_bar_and_drawer("3.1", auth_token)}
</body>
</html>"""
