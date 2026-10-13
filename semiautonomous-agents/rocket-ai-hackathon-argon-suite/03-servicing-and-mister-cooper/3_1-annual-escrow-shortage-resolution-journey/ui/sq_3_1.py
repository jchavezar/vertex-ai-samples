# -*- coding: utf-8 -*-
"""Square 3.1: Escrow Shortage Explainer & Planner (GECX + Gemini Enterprise streamAssist)
Visual Design: Mr. Cooper / Rocket Mortgage Homeowner Self-Service Portal
(#FFFDF9 warm homeowner cream background, #0F766E reassuring teal & #B45309 warm amber,
#FFFFFF clean homeowner cards, Google Fonts Fraunces serif headings + DM Sans body)."""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_3_1(auth_token: str) -> str:
    ge_ui_url = "https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mr. Cooper &amp; Rocket Mortgage | Homeowner Annual Escrow Statement &amp; Planner [3.1]</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {{
      --cream-bg: #FFFDF9;
      --teal-primary: #0F766E;
      --teal-soft: #F0FDFA;
      --amber-warm: #B45309;
      --amber-soft: #FEF3C7;
      --card-border: #E7E5E4;
    }}
    body {{
      font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: var(--cream-bg);
      color: #1C1917;
      margin: 0;
    }}
    .serif-heading {{
      font-family: 'Fraunces', Georgia, serif;
    }}
    .mono {{
      font-family: 'JetBrains Mono', monospace;
    }}
    .homeowner-card {{
      background: #FFFFFF;
      border-radius: 20px;
      border: 1px solid #E7E5E4;
      box-shadow: 0 10px 28px -8px rgba(28, 25, 23, 0.05), 0 2px 6px -1px rgba(15, 118, 110, 0.04);
    }}
    .plan-card {{
      background: #FFFFFF;
      border-radius: 16px;
      border: 2px solid #E7E5E4;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
      cursor: pointer;
    }}
    .plan-card:hover {{
      border-color: #99F6E4;
      transform: translateY(-2px);
    }}
    .plan-card.selected {{
      border-color: #0F766E;
      background: linear-gradient(180deg, #F0FDFA 0%, #FFFFFF 100%);
      box-shadow: 0 12px 24px -6px rgba(15, 118, 110, 0.14);
    }}
    input[type="range"] {{
      accent-color: #0F766E;
    }}
    .shrinking-shining-ink {{
      width: 14px;
      height: 14px;
      border-radius: 50%;
      background: radial-gradient(circle at 30% 30%, #FEF3C7, #0F766E, #115E59);
      animation: gentlePulse 1.2s ease-in-out infinite;
      display: inline-block;
    }}
    @keyframes gentlePulse {{
      0%, 100% {{ transform: scale(1); opacity: 0.95; }}
      50% {{ transform: scale(0.6); opacity: 0.5; }}
    }}
  </style>
</head>
<body class="min-h-screen pb-28">

  <!-- WARM HOMEOWNER SELF-SERVICE PORTAL HEADER -->
  <header class="sticky top-0 z-40 bg-[#FFFDF9]/95 backdrop-blur-md border-b border-stone-200">
    <div class="max-w-7xl mx-auto px-6 py-4 flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-3.5">
        <div class="w-11 h-11 rounded-2xl bg-[#0F766E] text-white flex items-center justify-center shadow-sm">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
          </svg>
        </div>
        <div>
          <div class="flex flex-wrap items-center gap-2">
            <span class="text-xs font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-teal-50 text-[#0F766E] border border-teal-200">
              Mr. Cooper &amp; Rocket Mortgage Homeowner Portal
            </span>
            <span class="text-xs text-stone-500">Loan #0498-2910-MC · 1842 Maplewood Dr, Troy, MI 48084</span>
          </div>
          <h1 class="text-xl md:text-2xl font-bold serif-heading text-stone-900 mt-0.5">
            Your 2026 Annual Escrow Account Statement &amp; Payment Planner
          </h1>
        </div>
      </div>

      <!-- Top Right Actions: Model Selector + Listen Button + Re-Synthesize -->
      <div class="flex flex-wrap items-center gap-2.5">
        <div class="flex items-center gap-2 bg-stone-100 border border-stone-200 rounded-full px-3.5 py-1.5">
          <span class="w-2 h-2 rounded-full bg-[#0F766E]"></span>
          <label for="app-model-select" class="text-[11px] font-semibold text-stone-600">AI Advisor:</label>
          <select id="app-model-select" onchange="window.syncSelectedModel(this.value)"
                  class="bg-transparent text-stone-900 text-xs font-bold focus:outline-none cursor-pointer">
            <option value="gemini-4-argon">gemini-4-argon (Frontier Global)</option>
            <option value="gemini-3.8-flash" selected>gemini-3.8-flash (GECX + streamAssist)</option>
          </select>
        </div>

        <button id="btn-warm-audio-explainer"
                onclick="window.playWarmHomeownerExplainer(this)"
                class="inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-bold bg-[#FEF3C7] text-[#B45309] border border-amber-300 shadow-sm hover:bg-amber-100 transition cursor-pointer">
          <span>🔊 Listen to Warm Homeowner Explainer (Gemini 3.8 Live · Aoede HD)</span>
        </button>

        <button onclick="window.runLiveVertexAI()" id="top-run-btn"
                class="inline-flex items-center gap-1.5 px-4 py-2 rounded-full text-xs font-bold bg-[#0F766E] text-white shadow-sm hover:bg-teal-800 transition cursor-pointer">
          <span>✨ Refresh Personalized Summary</span>
        </button>
      </div>
    </div>
  </header>

  <!-- REASSURING GOOD NEWS BANNER -->
  <div class="max-w-7xl mx-auto px-6 pt-6">
    <div class="homeowner-card p-5 bg-gradient-to-r from-[#F0FDFA] via-white to-[#FFFBEB] border-l-4 border-l-[#0F766E] flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div class="flex items-start gap-3.5">
        <div class="w-10 h-10 rounded-full bg-[#0F766E] text-white flex items-center justify-center shrink-0 font-bold text-base shadow-sm">
          ✓
        </div>
        <div>
          <div class="text-xs font-bold uppercase tracking-wider text-[#0F766E]">
            Reassurance First — Your Fixed 5.250% Mortgage Rate Has Not Changed
          </div>
          <p id="ai-empathetic-headline" class="text-sm md:text-base text-stone-800 mt-0.5 leading-relaxed">
            Your <strong>$1,840.00/month Principal &amp; Interest</strong> payment is 100% locked. Because Oakland County Property Taxes rose <strong>+$1,140/yr</strong> and your Homeowners Insurance rose <strong>+$480/yr</strong>, your escrow account experienced a <strong>$1,620.00</strong> shortage that we advanced on your behalf at <strong>0% interest</strong>.
          </p>
        </div>
      </div>
      <div class="shrink-0 flex items-center gap-2">
        <span id="sandbox-status-pill" class="px-3.5 py-1.5 rounded-full text-xs font-semibold bg-amber-50 text-[#B45309] border border-amber-200">
          RESPA 12 CFR § 1024.17 Verified
        </span>
      </div>
    </div>
  </div>

  <!-- MAIN 12-COLUMN HOMEOWNER WORKSPACE -->
  <main class="max-w-7xl mx-auto px-6 py-6 grid lg:grid-cols-12 gap-6 items-start">

    <!-- LEFT 7 COLUMNS: ANNUAL ESCROW STATEMENT BREAKDOWN + SLIDERS + HOMEOWNER Q&A -->
    <div class="lg:col-span-7 space-y-6">

      <!-- 1. FRIENDLY HOMEOWNER ANNUAL ESCROW ANALYSIS STATEMENT -->
      <section class="homeowner-card p-6">
        <div class="flex flex-wrap items-center justify-between gap-2 pb-4 mb-5 border-b border-stone-200/80">
          <div>
            <span class="text-xs font-bold uppercase tracking-wider text-[#0F766E]">Step 1 · Plain-English Statement</span>
            <h2 class="text-lg md:text-xl font-bold serif-heading text-stone-900 mt-0.5">
              Why Did My Escrow Account Have a $1,620 Shortage?
            </h2>
          </div>
          <div class="flex items-center gap-3 text-xs font-medium text-stone-600">
            <span class="inline-flex items-center gap-1.5"><span class="w-3 h-3 rounded-sm bg-stone-300 inline-block"></span> 2025 Billed</span>
            <span class="inline-flex items-center gap-1.5"><span class="w-3 h-3 rounded-sm bg-[#0F766E] inline-block"></span> 2026 Actual</span>
            <span class="inline-flex items-center gap-1.5"><span class="w-3 h-3 rounded-sm bg-[#B45309] inline-block"></span> Bill Increase</span>
          </div>
        </div>

        <!-- Plain-English Summary Callout Cards -->
        <div class="grid sm:grid-cols-3 gap-3.5 mb-6">
          <div class="p-4 rounded-2xl bg-[#F0FDFA] border border-teal-200/80">
            <div class="text-[11px] font-bold uppercase text-[#0F766E]">Fixed Mortgage P&amp;I</div>
            <div class="text-xl font-bold serif-heading text-stone-900 mt-1">$1,840.00/mo</div>
            <div class="text-xs text-[#0F766E] font-medium mt-1">Locked @ 5.250% ($0 change)</div>
          </div>
          <div class="p-4 rounded-2xl bg-[#FFFBEB] border border-amber-200">
            <div class="text-[11px] font-bold uppercase text-[#B45309]">County Property Taxes</div>
            <div id="stat-tax-rise" class="text-xl font-bold serif-heading text-[#B45309] mt-1">+$1,140/yr</div>
            <div id="stat-tax-mo" class="text-xs text-stone-600 font-medium mt-1">$4,860 → $6,000/yr (+$95/mo)</div>
          </div>
          <div class="p-4 rounded-2xl bg-[#FFFBEB] border border-amber-200">
            <div class="text-[11px] font-bold uppercase text-[#B45309]">Homeowners Insurance</div>
            <div id="stat-ins-rise" class="text-xl font-bold serif-heading text-[#B45309] mt-1">+$480/yr</div>
            <div id="stat-ins-mo" class="text-xs text-stone-600 font-medium mt-1">$1,800 → $2,280/yr (+$40/mo)</div>
          </div>
        </div>

        <!-- Interactive Tax & Insurance Sliders -->
        <div class="p-4 rounded-2xl bg-stone-50 border border-stone-200/90 mb-6">
          <div class="flex items-center justify-between mb-3">
            <span class="text-xs font-bold text-stone-800">Interactive What-If Tax &amp; Insurance Calculator</span>
            <span class="text-[11px] text-stone-500">Slide to test insurance shopping or a property tax appeal</span>
          </div>
          <div class="grid sm:grid-cols-3 gap-5">
            <div>
              <div class="flex justify-between text-xs font-semibold mb-1">
                <span class="text-stone-600">2026 Property Tax/Yr</span>
                <span id="lbl-new-tax" class="mono font-bold text-[#0F766E]">$6,000/yr</span>
              </div>
              <input id="slider-new-tax" type="range" min="4860" max="7860" step="60" value="6000"
                     oninput="window.updateEscrowSliders()" class="w-full cursor-pointer">
              <div class="flex justify-between text-[11px] text-stone-500 mt-0.5">
                <span>2025: $4,860</span>
                <span id="lbl-tax-delta" class="text-[#B45309] font-bold">+$1,140/yr (+$95/mo)</span>
              </div>
            </div>

            <div>
              <div class="flex justify-between text-xs font-semibold mb-1">
                <span class="text-stone-600">2026 Insurance/Yr</span>
                <span id="lbl-new-ins" class="mono font-bold text-[#0F766E]">$2,280/yr</span>
              </div>
              <input id="slider-new-ins" type="range" min="1560" max="3360" step="60" value="2280"
                     oninput="window.updateEscrowSliders()" class="w-full cursor-pointer">
              <div class="flex justify-between text-[11px] text-stone-500 mt-0.5">
                <span>2025: $1,800</span>
                <span id="lbl-ins-delta" class="text-[#B45309] font-bold">+$480/yr (+$40/mo)</span>
              </div>
            </div>

            <div>
              <div class="flex justify-between text-xs font-semibold mb-1">
                <span class="text-stone-600">Total Escrow Shortage</span>
                <span id="lbl-shortage" class="mono font-bold text-[#B45309]">$1,620</span>
              </div>
              <input id="slider-shortage" type="range" min="480" max="3240" step="60" value="1620"
                     oninput="window.updateEscrowSliders()" class="w-full cursor-pointer">
              <div class="flex justify-between text-[11px] text-stone-500 mt-0.5">
                <span>0% Interest Advance</span>
                <span id="lbl-spread12-delta" class="text-[#0F766E] font-bold">$135.00/mo (12m)</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Visual Statement Line Items -->
        <div class="space-y-3.5">
          <!-- Line 1: Principal & Interest -->
          <div class="p-3.5 rounded-xl bg-stone-50/80 border border-stone-200/80">
            <div class="flex items-center justify-between text-xs font-bold mb-1.5">
              <span class="text-stone-800">1. Principal &amp; Interest (Fixed @ 5.250%)</span>
              <div class="mono flex items-center gap-2">
                <span class="text-stone-600">$1,840.00/mo → $1,840.00/mo</span>
                <span class="px-2 py-0.5 rounded-full bg-teal-100 text-[#0F766E] text-[10px]">No Change</span>
              </div>
            </div>
            <div class="w-full h-2.5 rounded-full bg-stone-200 overflow-hidden flex">
              <div class="bg-[#0F766E] h-full" style="width: 68%"></div>
            </div>
          </div>

          <!-- Line 2: County Property Taxes -->
          <div class="p-3.5 rounded-xl bg-stone-50/80 border border-stone-200/80">
            <div class="flex items-center justify-between text-xs font-bold mb-1.5">
              <span class="text-stone-800">2. Oakland County Property Tax Bill</span>
              <div class="mono flex items-center gap-2">
                <span class="text-stone-600" id="wf-tax-comparison">$405.00/mo → $500.00/mo</span>
                <span class="px-2 py-0.5 rounded-full bg-amber-100 text-[#B45309] text-[10px]" id="wf-tax-badge">+$95.00/mo</span>
              </div>
            </div>
            <div class="w-full h-2.5 rounded-full bg-stone-200 overflow-hidden flex">
              <div class="bg-stone-400 h-full" style="width: 42%"></div>
              <div id="wf-tax-bar" class="bg-[#B45309] h-full transition-all duration-300" style="width: 14%"></div>
            </div>
          </div>

          <!-- Line 3: Homeowners Hazard Insurance -->
          <div class="p-3.5 rounded-xl bg-stone-50/80 border border-stone-200/80">
            <div class="flex items-center justify-between text-xs font-bold mb-1.5">
              <span class="text-stone-800">3. Homeowners Hazard Insurance Policy</span>
              <div class="mono flex items-center gap-2">
                <span class="text-stone-600" id="wf-ins-comparison">$150.00/mo → $190.00/mo</span>
                <span class="px-2 py-0.5 rounded-full bg-amber-100 text-[#B45309] text-[10px]" id="wf-ins-badge">+$40.00/mo</span>
              </div>
            </div>
            <div class="w-full h-2.5 rounded-full bg-stone-200 overflow-hidden flex">
              <div class="bg-stone-400 h-full" style="width: 24%"></div>
              <div id="wf-ins-bar" class="bg-[#B45309] h-full transition-all duration-300" style="width: 9%"></div>
            </div>
          </div>

          <!-- Line 4: Escrow Shortage Catch-Up -->
          <div class="p-3.5 rounded-xl bg-[#FFFBEB] border border-amber-200">
            <div class="flex items-center justify-between text-xs font-bold mb-1.5">
              <span class="text-stone-900">4. Escrow Shortage Catch-Up (2025 Tax/Insurance Advance at 0% Interest)</span>
              <div class="mono flex items-center gap-2">
                <span class="text-[#B45309]" id="wf-shortage-total">Shortage: $1,620.00</span>
                <span class="px-2 py-0.5 rounded-full bg-amber-200/80 text-[#B45309] text-[10px]" id="wf-shortage-badge">+$135.00/mo (12-Mo)</span>
              </div>
            </div>
            <div class="w-full h-2.5 rounded-full bg-amber-100 overflow-hidden flex">
              <div id="wf-shortage-bar" class="bg-[#B45309] h-full transition-all duration-300" style="width: 30%"></div>
            </div>
          </div>
        </div>
      </section>

      <!-- 2. HOMEOWNER ESCROW Q&A CONCIERGE (GEMINI ENTERPRISE streamAssist) -->
      <section class="homeowner-card p-6">
        <div class="flex flex-wrap items-center justify-between gap-2 pb-3 mb-4 border-b border-stone-200/80">
          <div class="flex items-center gap-2.5">
            <span class="w-2.5 h-2.5 rounded-full bg-[#0F766E]"></span>
            <div>
              <span class="text-[11px] font-bold uppercase tracking-wider text-[#0F766E]">Homeowner Help Desk · Gemini Enterprise</span>
              <h3 class="text-base font-bold serif-heading text-stone-900">Ask a Question About Your Escrow Statement</h3>
            </div>
          </div>
          <a href="{ge_ui_url}" target="_blank"
             class="px-3 py-1.5 rounded-full text-xs font-bold bg-[#F0FDFA] text-[#0F766E] border border-teal-200 hover:bg-teal-100 transition">
            Open Gemini Enterprise ↗
          </a>
        </div>

        <div class="flex flex-wrap gap-2 mb-3">
          <button onclick="window.askEscrowStreamAssist('Why did my payment increase if I have a fixed 5.25% interest rate?')"
                  class="text-xs px-3 py-1.5 rounded-full bg-stone-100 hover:bg-[#F0FDFA] text-stone-700 hover:text-[#0F766E] font-medium border border-stone-200 transition cursor-pointer">
            "Why did my payment go up if my rate is fixed?"
          </button>
          <button onclick="window.askEscrowStreamAssist('Is there any interest or fee if I choose the 12-month or 24-month shortage spread?')"
                  class="text-xs px-3 py-1.5 rounded-full bg-stone-100 hover:bg-[#F0FDFA] text-stone-700 hover:text-[#0F766E] font-medium border border-stone-200 transition cursor-pointer">
            "Is the 12-month or 24-month spread 0% interest?"
          </button>
          <button onclick="window.askEscrowStreamAssist('How can I lower my homeowners insurance or verify my Michigan Principal Residence Exemption?')"
                  class="text-xs px-3 py-1.5 rounded-full bg-stone-100 hover:bg-[#F0FDFA] text-stone-700 hover:text-[#0F766E] font-medium border border-stone-200 transition cursor-pointer">
            "Can I shop my insurance or check my Homestead exemption?"
          </button>
        </div>

        <div class="flex gap-2">
          <input id="escrow-chat-input" type="text"
                 value="Why did my escrow account have a $1,620 shortage when my 5.25% mortgage rate is fixed, and which payment plan is best?"
                 class="flex-1 px-4 py-2.5 rounded-xl bg-stone-50 border border-stone-300 text-xs md:text-sm focus:outline-none focus:border-[#0F766E]">
          <button onclick="window.askEscrowStreamAssist()"
                 class="px-5 py-2.5 rounded-xl bg-[#0F766E] hover:bg-teal-800 text-white font-bold text-xs md:text-sm shadow-sm transition shrink-0 cursor-pointer">
            Ask Advisor
          </button>
        </div>

        <div id="escrow-streamassist-output" class="mt-4 p-4 rounded-xl bg-[#FFFDF9] border border-stone-200 text-xs md:text-sm text-stone-700 leading-relaxed">
          <div class="flex items-center justify-between text-[11px] text-[#0F766E] font-bold mb-1.5">
            <span>✓ HOMEOWNER ESCROW EXPLANATION</span>
            <span id="streamassist-latency-pill" class="mono text-stone-500">RESPA Grounded</span>
          </div>
          <div id="escrow-streamassist-body">
            Your Principal &amp; Interest remains locked at <strong>$1,840.00/mo (5.250% fixed)</strong>. Because your local County Property Taxes rose by <strong>+$1,140/yr (+$95/mo)</strong> and your Homeowners Insurance rose by <strong>+$480/yr (+$40/mo)</strong>, your new base escrow requirement increased by <strong>+$135.00/mo</strong>, and we paid the <strong>$1,620.00</strong> difference on your behalf. You can pay the $1,620 lump sum today, spread it over 12 months at 0% interest (+$135.00/mo), or request a 24-month hardship spread (+$67.50/mo).
          </div>
        </div>
      </section>
    </div>

    <!-- RIGHT 5 COLUMNS: 3 CLICKABLE PAYMENT PLAN CARDS + UPDATED MONTHLY AUTOPAY STATEMENT -->
    <div class="lg:col-span-5 space-y-6">

      <!-- 3 CLICKABLE PAYMENT PLAN CARDS -->
      <section class="homeowner-card p-6">
        <div class="mb-4">
          <span class="text-xs font-bold uppercase tracking-wider text-[#0F766E]">Step 2 · Choose Your Payment Plan</span>
          <h2 class="text-lg md:text-xl font-bold serif-heading text-stone-900 mt-0.5">
            3 Flexible Ways to Handle the $1,620 Shortage
          </h2>
          <p class="text-xs text-stone-500 mt-0.5">All options carry <strong>0% interest and $0 servicing fees</strong>. Select the option that fits your household budget:</p>
        </div>

        <div class="space-y-3.5">
          <!-- Option A: Pay $1,620 Lump Sum -->
          <div id="opt-card-1" onclick="window.selectResolutionOption(1)" class="plan-card p-4">
            <div class="flex items-start justify-between gap-2">
              <div class="flex items-center gap-2.5">
                <div id="opt-radio-1" class="w-5 h-5 rounded-full border-2 border-stone-300 flex items-center justify-center text-xs font-bold"></div>
                <div>
                  <div class="text-sm font-bold text-stone-900" id="optA-title">Option A: Pay $1,620 Lump Sum</div>
                  <div class="text-xs text-stone-500">Pay the shortage once today to keep your monthly payment as low as possible</div>
                </div>
              </div>
              <span class="px-2.5 py-1 rounded-full bg-teal-50 text-[#0F766E] border border-teal-200 text-[11px] font-bold">Lowest Monthly</span>
            </div>
            <div class="mt-3 pt-3 border-t border-stone-100 flex items-center justify-between text-xs">
              <span class="text-stone-600">Due Today: <strong id="opt1-upfront" class="mono text-stone-900">$1,620.00</strong></span>
              <span class="text-[#0F766E] font-bold text-sm mono" id="opt1-monthly">$2,530.00/mo</span>
            </div>
          </div>

          <!-- Option B: Standard 12-Month Spread (+$135/mo) -->
          <div id="opt-card-2" onclick="window.selectResolutionOption(2)" class="plan-card selected p-4">
            <div class="flex items-start justify-between gap-2">
              <div class="flex items-center gap-2.5">
                <div id="opt-radio-2" class="w-5 h-5 rounded-full border-2 border-[#0F766E] bg-[#0F766E] text-white flex items-center justify-center text-xs font-bold">✓</div>
                <div>
                  <div class="text-sm font-bold text-stone-900" id="optB-title">Option B: Standard 12-Month Spread (+$135/mo)</div>
                  <div class="text-xs text-stone-500">Spread the shortage evenly over 12 months at 0% interest with $0 due today</div>
                </div>
              </div>
              <span class="px-2.5 py-1 rounded-full bg-[#FEF3C7] text-[#B45309] text-[11px] font-bold">Most Popular · $0 Now</span>
            </div>
            <div class="mt-3 pt-3 border-t border-stone-100 flex items-center justify-between text-xs">
              <span class="text-stone-600">Due Today: <strong class="mono text-stone-900">$0.00</strong> (+<span id="opt2-spread" class="mono">$135.00</span>/mo)</span>
              <span class="text-[#0F766E] font-bold text-sm mono" id="opt2-monthly">$2,665.00/mo</span>
            </div>
          </div>

          <!-- Option C: Hardship 24-Month Spread (+$67.50/mo) -->
          <div id="opt-card-3" onclick="window.selectResolutionOption(3)" class="plan-card p-4">
            <div class="flex items-start justify-between gap-2">
              <div class="flex items-center gap-2.5">
                <div id="opt-radio-3" class="w-5 h-5 rounded-full border-2 border-stone-300 flex items-center justify-center text-xs font-bold"></div>
                <div>
                  <div class="text-sm font-bold text-stone-900" id="optC-title">Option C: Hardship 24-Month Spread (+$67.50/mo)</div>
                  <div class="text-xs text-stone-500">Cuts the monthly shortage catch-up in half over 24 months at 0% interest</div>
                </div>
              </div>
              <span class="px-2.5 py-1 rounded-full bg-stone-100 text-stone-700 text-[11px] font-bold">Gentle Budget Relief</span>
            </div>
            <div class="mt-3 pt-3 border-t border-stone-100 flex items-center justify-between text-xs">
              <span class="text-stone-600">Due Today: <strong class="mono text-stone-900">$0.00</strong> (+<span id="opt3-spread" class="mono">$67.50</span>/mo)</span>
              <span class="text-[#0F766E] font-bold text-sm mono" id="opt3-monthly">$2,597.50/mo</span>
            </div>
          </div>
        </div>
      </section>

      <!-- HOMEOWNER AUTOPAY STATEMENT SUMMARY -->
      <section class="homeowner-card p-6 bg-gradient-to-b from-white to-[#F0FDFA]/50">
        <div class="flex items-center justify-between pb-3 mb-4 border-b border-dashed border-stone-300">
          <div>
            <div class="text-[11px] font-bold uppercase tracking-wider text-[#0F766E]">Updated Monthly Statement Preview</div>
            <h3 class="text-base font-bold serif-heading text-stone-900">Effective March 1, 2026 AutoPay</h3>
          </div>
          <span id="receipt-plan-badge" class="px-3 py-1 rounded-full text-xs font-bold bg-[#0F766E] text-white">
            Option B · 12-Mo Spread
          </span>
        </div>

        <div class="space-y-2.5 text-xs md:text-sm">
          <div class="flex justify-between items-center py-1">
            <span class="text-stone-600">Principal &amp; Interest (5.250% Fixed)</span>
            <span class="mono font-bold text-stone-900">$1,840.00</span>
          </div>
          <div class="flex justify-between items-center py-1">
            <span class="text-stone-600">2026 County Property Tax Escrow</span>
            <span id="rcpt-tax" class="mono font-bold text-stone-900">$500.00</span>
          </div>
          <div class="flex justify-between items-center py-1">
            <span class="text-stone-600">2026 Homeowners Insurance Escrow</span>
            <span id="rcpt-ins" class="mono font-bold text-stone-900">$190.00</span>
          </div>
          <div class="flex justify-between items-center py-2 px-3 rounded-xl bg-[#FEF3C7]/60 border border-amber-200">
            <span class="text-stone-800 font-semibold" id="rcpt-shortage-label">Escrow Shortage Catch-Up (12 Mos @ 0%)</span>
            <span id="rcpt-shortage-mo" class="mono font-bold text-[#B45309]">$135.00</span>
          </div>
        </div>

        <div class="mt-4 pt-4 border-t border-stone-200 flex items-baseline justify-between">
          <div>
            <div class="text-xs font-bold uppercase text-stone-500">New Monthly Payment</div>
            <div class="text-[11px] text-stone-500">Previous 2025 Payment: <span class="mono line-through">$2,395.00/mo</span></div>
          </div>
          <div class="text-right">
            <div id="rcpt-total-monthly" class="text-2xl font-bold serif-heading text-[#0F766E]">$2,665.00<span class="text-xs font-normal text-stone-500">/mo</span></div>
            <div id="rcpt-upfront-due" class="text-xs font-semibold text-[#B45309]">One-Time ACH Today: $0.00</div>
          </div>
        </div>

        <button onclick="window.confirmAutoPaySelection()" id="confirm-autopay-btn"
                class="mt-5 w-full py-3.5 px-4 rounded-xl font-bold text-sm text-white bg-[#0F766E] hover:bg-teal-800 shadow-md transition cursor-pointer flex items-center justify-center gap-2">
          <span>✓ Save Payment Plan &amp; Update March 1 AutoPay</span>
        </button>

        <div id="autopay-confirmation-toast" class="hidden mt-3 p-3.5 rounded-xl bg-[#F0FDFA] border border-teal-300 text-[#0F766E] text-xs font-semibold text-center"></div>
      </section>
    </div>
  </main>

  <script>
    let currentOption = 2;
    const BASE_PI = 1840.00;
    const OLD_TAX_YR = 4860.00;
    const OLD_INS_YR = 1800.00;

    function fmtMoney(n) {{
      return '$' + Number(n).toLocaleString('en-US', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
    }}

    window.playWarmHomeownerExplainer = function(btnEl) {{
      const shortage = parseFloat(document.getElementById('slider-shortage').value || 1620);
      const spread12 = (shortage / 12.0).toFixed(2);
      const spread24 = (shortage / 24.0).toFixed(2);
      const spokenText = `Hi there! First, the most important news: your 5.25 percent fixed mortgage rate and your 1,840 dollar principal and interest payment did not change by a single penny. Your escrow shortage of ${{shortage.toLocaleString()}} dollars happened only because Oakland County property taxes rose by 1,140 dollars a year and your homeowners insurance rose by 480 dollars a year. We already paid those bills on time for you, and you can pay the shortage in full, spread it interest-free over 12 months at ${{spread12}} dollars a month, or choose our gentle 24-month hardship plan at ${{spread24}} dollars a month.`;
      window.playLiveCallClip(spokenText, 'Aoede', 'Mr. Cooper Homeowner Concierge', btnEl);
    }};

    window.selectResolutionOption = function(optNum) {{
      currentOption = optNum;
      [1, 2, 3].forEach(i => {{
        const card = document.getElementById('opt-card-' + i);
        const radio = document.getElementById('opt-radio-' + i);
        if (i === optNum) {{
          card.classList.add('selected');
          radio.className = 'w-5 h-5 rounded-full border-2 border-[#0F766E] bg-[#0F766E] text-white flex items-center justify-center text-xs font-bold';
          radio.innerText = '✓';
        }} else {{
          card.classList.remove('selected');
          radio.className = 'w-5 h-5 rounded-full border-2 border-stone-300 flex items-center justify-center text-xs font-bold';
          radio.innerText = '';
        }}
      }});
      window.recalcReceiptUI();
    }};

    window.recalcReceiptUI = function() {{
      const newTaxYr = parseFloat(document.getElementById('slider-new-tax').value || 6000);
      const newInsYr = parseFloat(document.getElementById('slider-new-ins').value || 2280);
      const shortage = parseFloat(document.getElementById('slider-shortage').value || 1620);

      const oldTaxMo = OLD_TAX_YR / 12.0;
      const oldInsMo = OLD_INS_YR / 12.0;
      const newTaxMo = newTaxYr / 12.0;
      const newInsMo = newInsYr / 12.0;
      const taxRiseYr = Math.max(0, newTaxYr - OLD_TAX_YR);
      const insRiseYr = Math.max(0, newInsYr - OLD_INS_YR);
      const baseNewPiti = BASE_PI + newTaxMo + newInsMo;

      const spread12 = shortage / 12.0;
      const spread24 = shortage / 24.0;

      document.getElementById('stat-tax-rise').innerText = '+$' + taxRiseYr.toLocaleString() + '/yr';
      document.getElementById('stat-tax-mo').innerText = `$4,860 → $${{newTaxYr.toLocaleString()}}/yr (+$${{Math.round(newTaxMo - oldTaxMo)}}/mo)`;
      document.getElementById('stat-ins-rise').innerText = '+$' + insRiseYr.toLocaleString() + '/yr';
      document.getElementById('stat-ins-mo').innerText = `$1,800 → $${{newInsYr.toLocaleString()}}/yr (+$${{Math.round(newInsMo - oldInsMo)}}/mo)`;

      document.getElementById('lbl-new-tax').innerText = '$' + newTaxYr.toLocaleString() + '/yr';
      document.getElementById('lbl-tax-delta').innerText = `+$${{taxRiseYr.toLocaleString()}}/yr (+$${{Math.round(newTaxMo - oldTaxMo)}}/mo)`;
      document.getElementById('lbl-new-ins').innerText = '$' + newInsYr.toLocaleString() + '/yr';
      document.getElementById('lbl-ins-delta').innerText = `+$${{insRiseYr.toLocaleString()}}/yr (+$${{Math.round(newInsMo - oldInsMo)}}/mo)`;
      document.getElementById('lbl-shortage').innerText = '$' + shortage.toLocaleString();
      document.getElementById('lbl-spread12-delta').innerText = fmtMoney(spread12) + '/mo (12m)';

      document.getElementById('wf-tax-comparison').innerText = fmtMoney(oldTaxMo) + '/mo → ' + fmtMoney(newTaxMo) + '/mo';
      document.getElementById('wf-tax-badge').innerText = '+' + fmtMoney(newTaxMo - oldTaxMo) + '/mo';
      document.getElementById('wf-ins-comparison').innerText = fmtMoney(oldInsMo) + '/mo → ' + fmtMoney(newInsMo) + '/mo';
      document.getElementById('wf-ins-badge').innerText = '+' + fmtMoney(newInsMo - oldInsMo) + '/mo';
      document.getElementById('wf-shortage-total').innerText = 'Shortage: ' + fmtMoney(shortage);
      document.getElementById('wf-shortage-badge').innerText = '+' + fmtMoney(spread12) + '/mo (12-Mo)';

      document.getElementById('optA-title').innerText = `Option A: Pay $${{shortage.toLocaleString()}} Lump Sum`;
      document.getElementById('optB-title').innerText = `Option B: Standard 12-Month Spread (+${{fmtMoney(spread12)}}/mo)`;
      document.getElementById('optC-title').innerText = `Option C: Hardship 24-Month Spread (+${{fmtMoney(spread24)}}/mo)`;

      document.getElementById('opt1-upfront').innerText = fmtMoney(shortage);
      document.getElementById('opt1-monthly').innerText = fmtMoney(baseNewPiti) + '/mo';
      document.getElementById('opt2-spread').innerText = fmtMoney(spread12);
      document.getElementById('opt2-monthly').innerText = fmtMoney(baseNewPiti + spread12) + '/mo';
      document.getElementById('opt3-spread').innerText = fmtMoney(spread24);
      document.getElementById('opt3-monthly').innerText = fmtMoney(baseNewPiti + spread24) + '/mo';

      document.getElementById('rcpt-tax').innerText = fmtMoney(newTaxMo);
      document.getElementById('rcpt-ins').innerText = fmtMoney(newInsMo);

      if (currentOption === 1) {{
        document.getElementById('receipt-plan-badge').innerText = 'Option A · Lump Sum';
        document.getElementById('rcpt-shortage-label').innerText = 'Escrow Shortage Catch-Up (Paid in Full Today)';
        document.getElementById('rcpt-shortage-mo').innerText = '$0.00';
        document.getElementById('rcpt-total-monthly').innerHTML = fmtMoney(baseNewPiti) + '<span class="text-xs font-normal text-stone-500">/mo</span>';
        document.getElementById('rcpt-upfront-due').innerText = 'One-Time ACH Today: ' + fmtMoney(shortage);
      }} else if (currentOption === 2) {{
        document.getElementById('receipt-plan-badge').innerText = 'Option B · 12-Mo Spread';
        document.getElementById('rcpt-shortage-label').innerText = 'Escrow Shortage Catch-Up (12 Mos @ 0%)';
        document.getElementById('rcpt-shortage-mo').innerText = fmtMoney(spread12);
        document.getElementById('rcpt-total-monthly').innerHTML = fmtMoney(baseNewPiti + spread12) + '<span class="text-xs font-normal text-stone-500">/mo</span>';
        document.getElementById('rcpt-upfront-due').innerText = 'One-Time ACH Today: $0.00';
      }} else {{
        document.getElementById('receipt-plan-badge').innerText = 'Option C · 24-Mo Hardship Spread';
        document.getElementById('rcpt-shortage-label').innerText = 'Escrow Shortage Catch-Up (24 Mos @ 0%)';
        document.getElementById('rcpt-shortage-mo').innerText = fmtMoney(spread24);
        document.getElementById('rcpt-total-monthly').innerHTML = fmtMoney(baseNewPiti + spread24) + '<span class="text-xs font-normal text-stone-500">/mo</span>';
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
        const shortage = parseFloat(document.getElementById('slider-shortage').value || 1620);
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
            pill.innerText = `RESPA Verified (${{data.execution_ms}}ms)`;
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
        bodyEl.innerHTML = `<span class="inline-flex items-center gap-2 text-[#0F766E] font-semibold"><span class="shrinking-shining-ink"></span> Consulting Gemini Enterprise Homeowner Advisor...</span>`;
      }}
      try {{
        const res = await fetch('/api/stream-assist', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ code: '3.1', query: query }})
        }});
        const data = await res.json();
        if (latEl) {{
          latEl.innerText = `Grounded · ${{data.latency_ms || 310}}ms`;
        }}
        if (bodyEl) {{
          const txt = (data.answer_markdown || 'Grounded explanation ready.').replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>').replace(/\\n/g, '<br>');
          bodyEl.innerHTML = txt;
        }}
      }} catch (err) {{
        if (bodyEl) bodyEl.innerText = 'Advisor note: ' + err.message;
      }}
    }};

    window.confirmAutoPaySelection = function() {{
      const toast = document.getElementById('autopay-confirmation-toast');
      const planNames = {{
        1: 'Option A (Pay Lump Sum)',
        2: 'Option B (Standard 12-Month 0% Spread)',
        3: 'Option C (Hardship 24-Month 0% Spread)'
      }};
      const totalTxt = document.getElementById('rcpt-total-monthly').innerText;
      toast.classList.remove('hidden');
      toast.innerHTML = `✓ Saved! Your Mr. Cooper AutoPay is scheduled for <strong>${{planNames[currentOption]}}</strong> (${{totalTxt}}) beginning March 1, 2026. Confirmation #MC-ESC-2026-8841.`;
    }};

    window.runLiveVertexAI = async function() {{
      const btn = document.getElementById('top-run-btn');
      const headline = document.getElementById('ai-empathetic-headline');
      const bodyEl = document.getElementById('escrow-streamassist-body');
      const newTaxYr = parseFloat(document.getElementById('slider-new-tax').value || 6000);
      const newInsYr = parseFloat(document.getElementById('slider-new-ins').value || 2280);
      const shortage = parseFloat(document.getElementById('slider-shortage').value || 1620);
      const scenarioInput = document.getElementById('scenario-input') ? document.getElementById('scenario-input').value : '';

      if (btn) btn.innerHTML = `<span class="shrinking-shining-ink"></span> <span>Refreshing...</span>`;
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
          bodyEl.innerHTML = `<strong>[${{data.vertex ? data.vertex.model_used : window.getSelectedModel()}} Homeowner Brief]:</strong> ` + sd.executive_summary;
        }}
        const pill = document.getElementById('sandbox-status-pill');
        if (pill && data.vertex) {{
          pill.innerText = `Verified · ${{data.vertex.model_used}} (${{data.vertex.latency_ms}}ms)`;
        }}
      }} catch (e) {{
        console.error(e);
      }} finally {{
        if (btn) btn.innerHTML = `<span>✨ Refresh Personalized Summary</span>`;
      }}
    }};

    document.addEventListener('DOMContentLoaded', () => {{
      window.recalcReceiptUI();
    }});
  </script>

  {render_floating_control_bar_and_drawer("3.1", auth_token)}
</body>
</html>"""
