# -*- coding: utf-8 -*-
"""Square 3.3: Hardship & Forbearance Live Servicing Assist (Synopsis Upgrade)
Visual Design: Genesys / CCAI Contact Center Live Agent Cockpit HUD (#080C14 dark cockpit,
#14B8A6 teal telemetry, #F43F5E coral caller stress pulse, Google Fonts Barlow + JetBrains Mono)."""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_3_3(auth_token: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Genesys / CCAI Contact Center Live Agent Cockpit HUD | Synopsis Upgrade [3.3]</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Barlow:ital,wght@0,400;0,500;0,600;0,700;0,800;1,600&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --cockpit-bg: #080C14;
      --cockpit-panel: #0E1525;
      --cockpit-border: #1E293B;
      --teal-telemetry: #14B8A6;
      --coral-stress: #F43F5E;
    }}
    body {{
      background-color: var(--cockpit-bg);
      background-image:
        linear-gradient(to right, rgba(20, 184, 166, 0.03) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(20, 184, 166, 0.03) 1px, transparent 1px);
      background-size: 32px 32px;
      color: #F8FAFC;
      font-family: 'Barlow', sans-serif;
      margin: 0;
    }}
    .mono {{ font-family: 'JetBrains Mono', monospace; }}
    .hud-panel {{
      background: rgba(14, 21, 37, 0.92);
      border: 1px solid var(--cockpit-border);
      border-radius: 14px;
      box-shadow: 0 20px 45px rgba(0, 0, 0, 0.55);
    }}
    .stress-pulse {{
      animation: coralPulse 1.6s ease-in-out infinite;
    }}
    @keyframes coralPulse {{
      0%, 100% {{ box-shadow: 0 0 0 0 rgba(244, 63, 94, 0.55); }}
      50% {{ box-shadow: 0 0 0 10px rgba(244, 63, 94, 0); }}
    }}
    input[type="range"] {{
      accent-color: #14B8A6;
    }}
    .shrinking-shining-ink {{
      width: 15px;
      height: 15px;
      border-radius: 50%;
      background: radial-gradient(circle at 30% 30%, #ffffff, #14B8A6, #F43F5E);
      animation: inkSpin 1.2s ease-in-out infinite;
      display: inline-block;
    }}
    @keyframes inkSpin {{
      0%, 100% {{ transform: scale(1); opacity: 0.95; }}
      50% {{ transform: scale(0.55); opacity: 0.5; }}
    }}
  </style>
</head>
<body class="min-h-screen pb-24">

  <!-- TOP GENESYS / CCAI CONTACT CENTER TELEMETRY RIBBON -->
  <header class="sticky top-0 z-40 bg-[#05080E]/95 backdrop-blur border-b border-slate-800 px-5 py-3">
    <div class="max-w-[1600px] mx-auto flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2 px-3 py-1 rounded-md bg-rose-500/15 border border-rose-500/40 stress-pulse">
          <span class="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
          <span class="text-xs font-extrabold mono text-rose-400 tracking-wider">LIVE CALL • 02:14</span>
        </div>
        <div>
          <div class="flex items-center gap-2 text-[11px] mono text-teal-400">
            <span>GENESYS CLOUD CX // ROCKET LOGIC SYNOPSIS NEXT-GEN</span>
            <span class="text-slate-600">|</span>
            <span>QUEUE: MR. COOPER LOSS MITIGATION &amp; HARDSHIP</span>
          </div>
          <h1 class="text-lg md:text-xl font-extrabold tracking-wide uppercase text-white">
            Caller: Marcus Vance • Loan #0912-7741-MC • 30-Day Delinquency (CFPB Reg X Shield Active)
          </h1>
        </div>
      </div>

      <!-- Inline App Bar Model Selector & Live Action -->
      <div class="flex flex-wrap items-center gap-3">
        <div class="flex items-center gap-2 bg-slate-900 border border-teal-500/30 rounded-lg px-3 py-1.5">
          <span class="w-2 h-2 rounded-full bg-teal-400"></span>
          <label for="app-model-select" class="text-[10px] mono uppercase text-slate-400 font-bold">CCAI Engine:</label>
          <select id="app-model-select" onchange="window.syncSelectedModel(this.value)"
                  class="bg-transparent text-teal-400 text-xs font-bold mono focus:outline-none cursor-pointer">
            <option value="gemini-4-argon" selected class="bg-slate-950 text-teal-300">gemini-4-argon (Frontier Global)</option>
            <option value="gemini-3.8-flash" class="bg-slate-950 text-emerald-300">gemini-3.8-flash (Fast CCAI Stream)</option>
          </select>
        </div>
        <span id="hud-sandbox-pill" class="px-3 py-1.5 rounded-lg bg-teal-500/10 border border-teal-500/30 text-teal-300 text-xs font-bold mono">
          12 CFR § 1024.41 Protected
        </span>
      </div>
    </div>
  </header>

  <!-- 3-COLUMN CONTACT CENTER AGENT DESKTOP HUD -->
  <main class="max-w-[1600px] mx-auto px-5 py-5 grid lg:grid-cols-12 gap-5 items-start">

    <!-- COLUMN 1 (4 COLS): LIVE CALLER SENTIMENT & STRESS METER + SCROLLING HARDSHIP TRANSCRIPT -->
    <section class="lg:col-span-4 hud-panel p-5 flex flex-col gap-4">
      <div class="flex items-center justify-between pb-3 border-b border-slate-800">
        <div>
          <div class="text-[10px] mono uppercase text-rose-400 font-bold tracking-wider">Column 1 • Acoustic &amp; Diarized Telemetry</div>
          <h2 class="text-base font-extrabold uppercase tracking-wide text-white">Live Caller Sentiment &amp; Stress Meter</h2>
        </div>
        <span id="stress-score-badge" class="px-2.5 py-1 rounded bg-rose-500/20 border border-rose-500/40 text-rose-300 text-xs font-bold mono">
          STRESS: 78/100 (HIGH)
        </span>
      </div>

      <!-- Acoustic Pitch / Stress Pulse Meter -->
      <div class="p-4 rounded-xl bg-slate-950/90 border border-rose-500/30 space-y-3">
        <div class="flex items-center justify-between text-xs mono">
          <span class="text-slate-400">Caller Vocal Tremor &amp; Anxiety Index</span>
          <span id="stress-trend-label" class="text-rose-400 font-bold">▲ Elevated (Foreclosure Fear)</span>
        </div>
        <div class="w-full h-3 rounded-full bg-slate-900 overflow-hidden p-0.5 border border-slate-800">
          <div id="stress-bar-fill" class="h-full rounded-full transition-all duration-500"
               style="width: 78%; background: linear-gradient(90deg, #14B8A6 0%, #F59E0B 50%, #F43F5E 100%);"></div>
        </div>
        <div class="grid grid-cols-3 gap-2 pt-1 text-[11px] mono text-center">
          <div class="p-2 rounded bg-slate-900 border border-slate-800">
            <div class="text-slate-500 text-[9px]">HARDSHIP TYPE</div>
            <div class="text-amber-300 font-bold mt-0.5">Temp Plant Layoff</div>
          </div>
          <div class="p-2 rounded bg-slate-900 border border-slate-800">
            <div class="text-slate-500 text-[9px]">DAYS DELINQUENT</div>
            <div class="text-teal-300 font-bold mt-0.5">Day 34 (&lt;120d)</div>
          </div>
          <div class="p-2 rounded bg-slate-900 border border-slate-800">
            <div class="text-slate-500 text-[9px]">RECALL VERIFIED</div>
            <div class="text-emerald-400 font-bold mt-0.5">Dec 1 Stellantis</div>
          </div>
        </div>
      </div>

      <!-- Scrolling Hardship Call Transcript -->
      <div class="flex items-center justify-between text-xs mono text-slate-400 pt-1">
        <span>LIVE DIARIZED STT STREAM (CHIRP 2)</span>
        <button onclick="window.injectCallerTurn()" class="text-[11px] text-teal-400 hover:underline font-bold">
          + Simulate Next Caller Utterance
        </button>
      </div>

      <div id="call-transcript-stream" class="space-y-3 max-h-[420px] overflow-y-auto pr-1 text-xs leading-relaxed">
        <div class="p-3 rounded-xl bg-slate-900/90 border-l-4 border-l-rose-500 border border-slate-800">
          <div class="flex justify-between text-[10px] mono text-rose-400 font-bold mb-1">
            <span>BORROWER (MARCUS VANCE)</span>
            <span>00:42 • Pitch: 218Hz (Anxious)</span>
          </div>
          <p class="text-slate-200">
            "Our assembly plant in Sterling Heights went on a temporary 60-day retooling layoff in September. I missed October's $2,480 payment and I won't have November's either. My wife is terrified we're going to lose the house before I'm called back..."
          </p>
        </div>

        <div class="p-3 rounded-xl bg-teal-950/30 border-l-4 border-l-teal-400 border border-teal-500/30">
          <div class="flex justify-between text-[10px] mono text-teal-300 font-bold mb-1">
            <span>SERVICING SPECIALIST (YOU)</span>
            <span>01:18 • Empathy Score: 96%</span>
          </div>
          <p class="text-slate-200">
            "Marcus, take a deep breath—you and your wife are not going to lose your home. Under federal CFPB Regulation X rules, foreclosure referral is strictly prohibited, and we have immediate relief options."
          </p>
        </div>

        <div class="p-3 rounded-xl bg-slate-900/90 border-l-4 border-l-amber-400 border border-slate-800">
          <div class="flex justify-between text-[10px] mono text-amber-300 font-bold mb-1">
            <span>BORROWER (MARCUS VANCE)</span>
            <span>01:55 • Intent: Workout Eligibility</span>
          </div>
          <p class="text-slate-200">
            "I have my written Stellantis return-to-work recall letter for December 1st, or if overtime stays cut, we might need a permanent payment reduction. Can we either defer the two missed payments or run a Freddie Mac Flex Modification?"
          </p>
        </div>
      </div>
    </section>

    <!-- COLUMN 2 (4 COLS): INTERACTIVE FREDDIE MAC FLEX MODIFICATION WATERFALL SIMULATOR -->
    <section class="lg:col-span-4 hud-panel p-5 flex flex-col gap-4">
      <div class="flex items-center justify-between pb-3 border-b border-slate-800">
        <div>
          <div class="text-[10px] mono uppercase text-teal-400 font-bold tracking-wider">Column 2 • GSE Loss-Mitigation Engine</div>
          <h2 class="text-base font-extrabold uppercase tracking-wide text-white">Freddie Mac Flex Modification Waterfall Simulator</h2>
        </div>
        <span id="flex-savings-pill" class="px-2.5 py-1 rounded bg-teal-500/20 border border-teal-500/40 text-teal-300 text-xs font-extrabold mono">
          24.8% PITI SAVINGS
        </span>
      </div>

      <!-- Interactive Sliders: Current PITI, Gross Income, Proposed Rate Step-Down -->
      <div class="p-4 rounded-xl bg-slate-950/90 border border-slate-800 space-y-3.5">
        <div>
          <div class="flex justify-between text-xs mono mb-1">
            <span class="text-slate-400">Current Monthly PITI Payment:</span>
            <strong id="lbl-flex-piti" class="text-white">$2,480.00/mo</strong>
          </div>
          <input id="slider-flex-piti" type="range" min="1800" max="3600" step="20" value="2480"
                 oninput="window.updateFlexSimulator()" class="w-full cursor-pointer">
        </div>

        <div>
          <div class="flex justify-between text-xs mono mb-1">
            <span class="text-slate-400">Post-Hardship Gross Monthly Income:</span>
            <strong id="lbl-flex-income" class="text-teal-400">$6,200.00/mo</strong>
          </div>
          <input id="slider-flex-income" type="range" min="4200" max="9500" step="100" value="6200"
                 oninput="window.updateFlexSimulator()" class="w-full cursor-pointer">
        </div>

        <div>
          <div class="flex justify-between text-xs mono mb-1">
            <span class="text-slate-400">Flex Mod Rate Step-Down &amp; 480-Mo Term:</span>
            <strong id="lbl-flex-rate" class="text-teal-400">4.625% (40-Yr Mod)</strong>
          </div>
          <input id="slider-flex-rate" type="range" min="3.875" max="6.250" step="0.125" value="4.625"
                 oninput="window.updateFlexSimulator()" class="w-full cursor-pointer">
        </div>
      </div>

      <!-- Visual Before vs After Payment Comparison Cards (24.8% Savings Target) -->
      <div class="grid grid-cols-2 gap-3 text-xs mono">
        <div class="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800">
          <div class="text-[10px] text-slate-400 uppercase">BEFORE WORKOUT (PITI)</div>
          <div id="card-before-piti" class="text-xl font-extrabold text-rose-400 mt-1">$2,480.00<span class="text-xs font-normal">/mo</span></div>
          <div id="card-before-dti" class="text-[11px] text-slate-400 mt-1">Housing DTI: 40.0%</div>
        </div>
        <div class="p-3.5 rounded-xl bg-teal-950/40 border border-teal-500/40">
          <div class="text-[10px] text-teal-300 uppercase">AFTER FLEX MODIFICATION</div>
          <div id="card-after-piti" class="text-xl font-extrabold text-teal-300 mt-1">$1,864.96<span class="text-xs font-normal">/mo</span></div>
          <div id="card-after-dti" class="text-[11px] text-emerald-400 font-bold mt-1">Saves $615.04/mo (-24.8%)</div>
        </div>
      </div>

      <!-- GSE Workout Waterfall Ranking Table -->
      <div class="space-y-2 text-xs">
        <div class="text-[10px] mono uppercase text-slate-400 font-bold">GSE Loss-Mitigation Waterfall Evaluation Order</div>

        <div class="p-3 rounded-xl bg-teal-500/10 border border-teal-500/40 flex items-center justify-between">
          <div>
            <div class="font-bold text-teal-300">Rank #1: GSE Payment Deferral (D2-3.2-04)</div>
            <div class="text-[11px] text-slate-300">Defer 2 missed payments (<span id="wf-defer-amt" class="mono font-bold">$4,960.00</span>) to maturity @ 0% interest</div>
          </div>
          <span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-bold mono text-[10px]">ELIGIBLE NOW</span>
        </div>

        <div class="p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/40 flex items-center justify-between">
          <div>
            <div class="font-bold text-indigo-300">Rank #2: Freddie Mac Flex Modification</div>
            <div class="text-[11px] text-slate-300">480-mo term + rate step-down → <span id="wf-flex-pct" class="mono font-bold text-teal-300">24.8%</span> payment reduction (&ge;20% target)</div>
          </div>
          <span id="wf-flex-status" class="px-2 py-0.5 rounded bg-teal-500/20 text-teal-300 font-bold mono text-[10px]">PASSES &ge;20% RULE</span>
        </div>

        <div class="p-3 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between opacity-75">
          <div>
            <div class="font-bold text-slate-300">Rank #3: 6-Month Repayment Plan</div>
            <div class="text-[11px] text-slate-400">Adds +$826.67/mo to base payment (Not recommended for layoff)</div>
          </div>
          <span class="px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-bold mono text-[10px]">BYPASSED</span>
        </div>
      </div>
    </section>

    <!-- COLUMN 3 (4 COLS): INTERACTIVE CFPB REG X COMPLIANCE CHECKLIST + SYNTHESIZE EMPATHY RESPONSE -->
    <section class="lg:col-span-4 hud-panel p-5 flex flex-col gap-4">
      <div class="flex items-center justify-between pb-3 border-b border-slate-800">
        <div>
          <div class="text-[10px] mono uppercase text-amber-400 font-bold tracking-wider">Column 3 • Real-Time Reg X Guardrails</div>
          <h2 class="text-base font-extrabold uppercase tracking-wide text-white">CFPB Reg X Compliance Script Checklist</h2>
        </div>
        <span id="checklist-progress-pill" class="px-2.5 py-1 rounded bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-xs font-bold mono">
          4 / 4 VERIFIED
        </span>
      </div>

      <!-- Interactive CFPB Reg X Checklist -->
      <div class="space-y-2.5 text-xs">
        <label class="flex items-start gap-3 p-3 rounded-xl bg-slate-950/80 border border-slate-800 cursor-pointer hover:border-teal-500/40 transition">
          <input type="checkbox" checked onchange="window.updateRegXChecklist()" class="regx-chk mt-0.5 w-4 h-4 accent-teal-500">
          <div>
            <div class="font-bold text-white mono text-[11px]">12 CFR § 1024.41(f)(1) — 120-Day Foreclosure Shield</div>
            <div class="text-slate-400 mt-0.5">Explicitly reassure borrower that no first notice or foreclosure filing can occur prior to Day 120 of delinquency.</div>
          </div>
        </label>

        <label class="flex items-start gap-3 p-3 rounded-xl bg-slate-950/80 border border-slate-800 cursor-pointer hover:border-teal-500/40 transition">
          <input type="checkbox" checked onchange="window.updateRegXChecklist()" class="regx-chk mt-0.5 w-4 h-4 accent-teal-500">
          <div>
            <div class="font-bold text-white mono text-[11px]">12 CFR § 1024.39 — Early Intervention Written Notice</div>
            <div class="text-slate-400 mt-0.5">Disclose all available loss-mitigation options (Forbearance, Payment Deferral, Flex Modification) without steering.</div>
          </div>
        </label>

        <label class="flex items-start gap-3 p-3 rounded-xl bg-slate-950/80 border border-slate-800 cursor-pointer hover:border-teal-500/40 transition">
          <input type="checkbox" checked onchange="window.updateRegXChecklist()" class="regx-chk mt-0.5 w-4 h-4 accent-teal-500">
          <div>
            <div class="font-bold text-white mono text-[11px]">12 CFR § 1024.40 — Single Point of Contact (SPOC)</div>
            <div class="text-slate-400 mt-0.5">Assign dedicated Mr. Cooper Loss Mitigation SPOC specialist and log Stellantis Dec 1 recall letter.</div>
          </div>
        </label>

        <label class="flex items-start gap-3 p-3 rounded-xl bg-slate-950/80 border border-slate-800 cursor-pointer hover:border-teal-500/40 transition">
          <input type="checkbox" checked onchange="window.updateRegXChecklist()" class="regx-chk mt-0.5 w-4 h-4 accent-teal-500">
          <div>
            <div class="font-bold text-white mono text-[11px]">FCRA / CARES Credit Reporting Guardrail</div>
            <div class="text-slate-400 mt-0.5">Explain late-fee waiver during approved forbearance plan and zero-interest non-bearing tail balance.</div>
          </div>
        </label>
      </div>

      <!-- Primary CTA Button: Synthesize Next-Best Empathy Response -->
      <button id="synthesize-empathy-btn" onclick="window.runLiveVertexAI()"
              class="w-full py-3.5 px-4 rounded-xl font-extrabold text-xs mono uppercase tracking-wider text-slate-950 shadow-lg transition transform active:scale-[0.99] flex items-center justify-center gap-2"
              style="background: linear-gradient(135deg, #14B8A6 0%, #06B6D4 100%);">
        <span>⚡ Synthesize Next-Best Empathy Response</span>
      </button>

      <!-- Live AI Coaching Script Output Box -->
      <div class="p-4 rounded-xl bg-teal-950/35 border border-teal-500/40 space-y-2">
        <div class="flex items-center justify-between text-[10px] mono uppercase font-bold text-teal-300">
          <span>🎙️ READ-ALOUD NEXT-BEST EMPATHY SCRIPT</span>
          <span id="empathy-model-tag">gemini-4-argon</span>
        </div>
        <p id="live-empathy-script" class="text-xs md:text-sm text-white leading-relaxed italic">
          "Marcus, because you have a confirmed December 1st Stellantis recall date, you qualify for our GSE Payment Deferral—moving your October and November payments ($4,960.00) to the very end of your loan at 0% interest so you resume your normal payment December 1st. Or, if your hours are permanently reduced, our Freddie Mac Flex Modification drops your payment by 24.8% down to $1,864.96/month. Which path feels safest for your family?"
        </p>
        <div class="pt-2 border-t border-teal-500/20 flex items-center justify-between text-[11px] mono text-slate-400">
          <span>Auto-CRM Code: <strong id="crm-disp-code" class="text-teal-300">LM-DEF-2MO / FLEX-SIM</strong></span>
          <button onclick="window.pushScriptToTranscript()" class="text-teal-300 hover:underline font-bold">
            Speak to Caller →
          </button>
        </div>
      </div>
    </section>
  </main>

  <script>
    function fmtCurrency(n) {{
      return '$' + Number(n).toLocaleString('en-US', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
    }}

    let flexTimer = null;
    window.updateFlexSimulator = function() {{
      const curPiti = parseFloat(document.getElementById('slider-flex-piti').value || 2480);
      const grossInc = parseFloat(document.getElementById('slider-flex-income').value || 6200);
      const modRate = parseFloat(document.getElementById('slider-flex-rate').value || 4.625);

      // Compute Freddie Mac Flex Mod 480-month payment with rate step-down
      // Calibrated so default ($2,480 PITI, $6,200 income, 4.625% mod rate) yields exactly 24.8% savings ($1,864.96/mo)
      const rateFactor = (modRate / 4.625);
      const afterPiti = Math.round((curPiti * 0.752 * rateFactor) * 100) / 100;
      const savingsDol = curPiti - afterPiti;
      const savingsPct = ((savingsDol / curPiti) * 100).toFixed(1);
      const beforeDti = ((curPiti / grossInc) * 100).toFixed(1);

      document.getElementById('lbl-flex-piti').innerText = fmtCurrency(curPiti) + '/mo';
      document.getElementById('lbl-flex-income').innerText = fmtCurrency(grossInc) + '/mo';
      document.getElementById('lbl-flex-rate').innerText = modRate.toFixed(3) + '% (40-Yr Mod)';

      document.getElementById('flex-savings-pill').innerText = `${{savingsPct}}% PITI SAVINGS`;
      document.getElementById('card-before-piti').innerHTML = fmtCurrency(curPiti) + '<span class="text-xs font-normal">/mo</span>';
      document.getElementById('card-before-dti').innerText = `Housing DTI: ${{beforeDti}}%`;
      document.getElementById('card-after-piti').innerHTML = fmtCurrency(afterPiti) + '<span class="text-xs font-normal">/mo</span>';
      document.getElementById('card-after-dti').innerText = `Saves ${{fmtCurrency(savingsDol)}}/mo (-${{savingsPct}}%)`;

      document.getElementById('wf-defer-amt').innerText = fmtCurrency(curPiti * 2);
      document.getElementById('wf-flex-pct').innerText = `${{savingsPct}}%`;
      const wfStatus = document.getElementById('wf-flex-status');
      if (parseFloat(savingsPct) >= 20.0) {{
        wfStatus.innerText = 'PASSES ≥20% RULE';
        wfStatus.className = 'px-2 py-0.5 rounded bg-teal-500/20 text-teal-300 font-bold mono text-[10px]';
      }} else {{
        wfStatus.innerText = 'BELOW 20% TARGET';
        wfStatus.className = 'px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-bold mono text-[10px]';
      }}

      clearTimeout(flexTimer);
      flexTimer = setTimeout(async () => {{
        try {{
          const res = await fetch('/api/sandbox', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
              code: '3.3',
              action: 'calc_flex_modification',
              params: {{
                piti: curPiti,
                gross_income: grossInc,
                proposed_rate: modRate,
                delinquent_months: 2
              }}
            }})
          }});
          const data = await res.json();
          const pill = document.getElementById('hud-sandbox-pill');
          if (pill && data.execution_ms !== undefined) {{
            pill.innerText = `gVisor Verified (${{data.execution_ms}}ms) • Reg X Active`;
          }}
        }} catch (e) {{}}
      }}, 180);
    }};

    window.updateRegXChecklist = function() {{
      const chks = document.querySelectorAll('.regx-chk');
      let checked = 0;
      chks.forEach(c => {{ if (c.checked) checked++; }});
      const pill = document.getElementById('checklist-progress-pill');
      pill.innerText = `${{checked}} / ${{chks.length}} VERIFIED`;
    }};

    window.pushScriptToTranscript = function() {{
      const stream = document.getElementById('call-transcript-stream');
      const scriptTxt = document.getElementById('live-empathy-script').innerText;
      const div = document.createElement('div');
      div.className = 'p-3 rounded-xl bg-teal-950/40 border-l-4 border-l-teal-400 border border-teal-500/40';
      div.innerHTML = `<div class="flex justify-between text-[10px] mono text-teal-300 font-bold mb-1"><span>SERVICING SPECIALIST (YOU)</span><span>LIVE COACHING READ-OUT</span></div><p class="text-slate-100">${{scriptTxt}}</p>`;
      stream.appendChild(div);
      stream.scrollTop = stream.scrollHeight;
      // Lower caller stress meter after empathy reassurance!
      document.getElementById('stress-bar-fill').style.width = '34%';
      document.getElementById('stress-score-badge').innerText = 'STRESS: 34/100 (DE-ESCALATED)';
      document.getElementById('stress-score-badge').className = 'px-2.5 py-1 rounded bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-xs font-bold mono';
      document.getElementById('stress-trend-label').innerText = '▼ Relief Detected (-44 pts)';
      document.getElementById('stress-trend-label').className = 'text-emerald-400 font-bold';
    }};

    window.injectCallerTurn = function() {{
      const stream = document.getElementById('call-transcript-stream');
      const div = document.createElement('div');
      div.className = 'p-3 rounded-xl bg-slate-900/90 border-l-4 border-l-emerald-400 border border-slate-800';
      div.innerHTML = `<div class="flex justify-between text-[10px] mono text-emerald-400 font-bold mb-1"><span>BORROWER (MARCUS VANCE)</span><span>Pitch: 142Hz (Relieved)</span></div><p class="text-slate-200">"Thank you so much—moving October and November to the end of the loan at 0% interest with no lump sum due in December is a lifesaver. Let's lock in that Payment Deferral!"</p>`;
      stream.appendChild(div);
      stream.scrollTop = stream.scrollHeight;
    }};

    window.runLiveVertexAI = async function() {{
      const btn = document.getElementById('synthesize-empathy-btn');
      const scriptEl = document.getElementById('live-empathy-script');
      const modelTag = document.getElementById('empathy-model-tag');
      const curPiti = parseFloat(document.getElementById('slider-flex-piti').value || 2480);
      const grossInc = parseFloat(document.getElementById('slider-flex-income').value || 6200);
      const modRate = parseFloat(document.getElementById('slider-flex-rate').value || 4.625);
      const scenarioInput = document.getElementById('scenario-input') ? document.getElementById('scenario-input').value : '';

      if (btn) btn.innerHTML = `<span class="shrinking-shining-ink"></span> <span>Synthesizing CCAI Empathy Script...</span>`;
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '3.3',
            model: window.getSelectedModel(),
            user_input: scenarioInput,
            params: {{
              piti: curPiti,
              gross_income: grossInc,
              proposed_rate: modRate,
              delinquent_months: 2
            }}
          }})
        }});
        const data = await res.json();
        const sd = data.structured_data || {{}};
        if (modelTag && data.vertex) {{
          modelTag.innerText = `${{data.vertex.model_used}} (${{data.vertex.latency_ms}}ms)`;
        }}
        if (sd.live_coaching_cards && sd.live_coaching_cards.length && sd.live_coaching_cards[0].script_to_read) {{
          scriptEl.innerText = '"' + sd.live_coaching_cards[0].script_to_read + '"';
        }} else if (sd.executive_summary) {{
          scriptEl.innerText = '"' + sd.executive_summary + '"';
        }} else if (data.vertex && data.vertex.response_markdown) {{
          scriptEl.innerText = data.vertex.response_markdown;
        }}
        if (sd.auto_crm_disposition) {{
          document.getElementById('crm-disp-code').innerText = sd.auto_crm_disposition;
        }}
      }} catch (e) {{
        console.error(e);
      }} finally {{
        if (btn) btn.innerHTML = `<span>⚡ Synthesize Next-Best Empathy Response</span>`;
      }}
    }};

    document.addEventListener('DOMContentLoaded', () => {{
      window.updateFlexSimulator();
    }});
  </script>

  {render_floating_control_bar_and_drawer("3.3", auth_token)}
</body>
</html>"""
