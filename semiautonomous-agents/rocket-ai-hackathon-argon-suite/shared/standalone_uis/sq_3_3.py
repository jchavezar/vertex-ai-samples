# -*- coding: utf-8 -*-
"""Square 3.3: M&A Servicing Welcome & Audit Engine
Visual Design: Stripe / Plaid Clean Financial Account Onboarding & Transfer Tracker
(#F8FAFC light slate background, #4F46E5 trustworthy indigo, #059669 verified emerald,
#FFFFFF clean step cards, Google Fonts Plus Jakarta Sans)."""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_3_3(auth_token: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mr. Cooper → Rocket Mortgage | M&amp;A Servicing Welcome &amp; Boarding Audit Tracker [3.3]</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --slate-bg: #F8FAFC;
      --indigo-primary: #4F46E5;
      --emerald-verified: #059669;
      --card-surface: #FFFFFF;
    }}
    body {{
      background-color: var(--slate-bg);
      color: #0F172A;
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      margin: 0;
    }}
    .mono {{
      font-family: 'JetBrains Mono', monospace;
    }}
    .stripe-card {{
      background: #FFFFFF;
      border-radius: 18px;
      border: 1px solid #E2E8F0;
      box-shadow: 0 10px 25px -6px rgba(15, 23, 42, 0.05), 0 2px 6px -1px rgba(79, 70, 229, 0.04);
    }}
    .step-card {{
      background: #FFFFFF;
      border-radius: 16px;
      border: 1.5px solid #E2E8F0;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
      cursor: pointer;
    }}
    .step-card:hover {{
      border-color: #818CF8;
      transform: translateY(-1px);
    }}
    .step-card.active {{
      border-color: #4F46E5;
      background: linear-gradient(180deg, #EEF2FF 0%, #FFFFFF 100%);
      box-shadow: 0 10px 22px -6px rgba(79, 70, 229, 0.14);
    }}
    input[type="range"] {{
      accent-color: #4F46E5;
    }}
    .shrinking-shining-ink {{
      width: 14px;
      height: 14px;
      border-radius: 50%;
      background: radial-gradient(circle at 30% 30%, #E0E7FF, #4F46E5, #059669);
      animation: plaidPulse 1.2s ease-in-out infinite;
      display: inline-block;
    }}
    @keyframes plaidPulse {{
      0%, 100% {{ transform: scale(1); opacity: 0.95; }}
      50% {{ transform: scale(0.6); opacity: 0.5; }}
    }}
  </style>
</head>
<body class="min-h-screen pb-28">

  <!-- TOP STRIPE / PLAID CLEAN FINANCIAL ONBOARDING HEADER -->
  <header class="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200 px-6 py-4">
    <div class="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-3.5">
        <div class="w-11 h-11 rounded-2xl bg-[#4F46E5] text-white flex items-center justify-center font-extrabold shadow-sm">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
          </svg>
        </div>
        <div>
          <div class="flex flex-wrap items-center gap-2">
            <span class="text-xs font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-indigo-50 text-[#4F46E5] border border-indigo-200">
              Mr. Cooper → Rocket Mortgage Onboarding
            </span>
            <span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-50 text-[#059669] border border-emerald-200">
              ✓ 100% Penny-Perfect Ledger Match
            </span>
          </div>
          <h1 class="text-xl md:text-2xl font-extrabold text-slate-900 tracking-tight mt-0.5">
            M&amp;A Servicing Welcome &amp; Automated Boarding Audit Tracker
          </h1>
        </div>
      </div>

      <!-- Right Header Controls: Model Selector + Play Personalized Welcome Call + Re-Audit -->
      <div class="flex flex-wrap items-center gap-2.5">
        <div class="flex items-center gap-2 bg-slate-100 border border-slate-200 rounded-full px-3.5 py-1.5">
          <span class="w-2 h-2 rounded-full bg-[#4F46E5]"></span>
          <label for="app-model-select" class="text-[11px] font-semibold text-slate-600">Audit Engine:</label>
          <select id="app-model-select" onchange="window.syncSelectedModel(this.value)"
                  class="bg-transparent text-slate-900 text-xs font-bold focus:outline-none cursor-pointer">
            <option value="gemini-4-argon" selected>gemini-4-argon (Frontier Global)</option>
            <option value="gemini-3.8-flash">gemini-3.8-flash (Fast Boarding Audit)</option>
          </select>
        </div>

        <button id="btn-welcome-call"
                onclick="window.playPersonalizedWelcomeCall(this)"
                class="inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-bold bg-indigo-50 text-[#4F46E5] border border-indigo-200 shadow-sm hover:bg-indigo-100 transition cursor-pointer">
          <span>🔊 Play Personalized Welcome Call (Gemini 3.8 Live · Puck HD)</span>
        </button>

        <button id="synthesize-empathy-btn" onclick="window.runLiveVertexAI()"
                class="inline-flex items-center gap-1.5 px-4 py-2 rounded-full text-xs font-bold bg-[#4F46E5] text-white shadow-sm hover:bg-indigo-700 transition cursor-pointer">
          <span>⚡ Re-Run Boarding Audit</span>
        </button>
      </div>
    </div>
  </header>

  <!-- PLAID-STYLE ACCOUNT BRIDGE STATUS BANNER -->
  <div class="max-w-7xl mx-auto px-6 pt-6">
    <div class="stripe-card p-5 bg-gradient-to-r from-indigo-50/80 via-white to-emerald-50/80 border-l-4 border-l-[#4F46E5] flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div class="flex items-center gap-4">
        <div class="flex items-center -space-x-2 shrink-0">
          <div class="w-10 h-10 rounded-full bg-teal-700 text-white font-bold text-xs flex items-center justify-center border-2 border-white shadow">MC</div>
          <div class="w-10 h-10 rounded-full bg-[#4F46E5] text-white font-bold text-xs flex items-center justify-center border-2 border-white shadow">RKT</div>
        </div>
        <div>
          <div class="text-xs font-bold uppercase tracking-wider text-[#4F46E5]">
            Zero-Disruption Servicing Transfer · RESPA 12 CFR § 1024.33 Verified
          </div>
          <p id="welcome-audit-headline" class="text-sm md:text-base text-slate-700 mt-0.5">
            Welcome to Rocket Mortgage! Your loan terms, <strong>5.625% fixed interest rate</strong>, <strong><span id="banner-upb">$342,180.44</span> principal balance</strong>, escrow impounds, and Chase AutoPay routing have been verified and bridged automatically.
          </p>
        </div>
      </div>
      <div class="shrink-0">
        <span id="hud-sandbox-pill" class="px-3.5 py-1.5 rounded-full text-xs font-bold bg-emerald-50 text-[#059669] border border-emerald-200 mono">
          4 / 4 Checks Verified
        </span>
      </div>
    </div>
  </div>

  <!-- MAIN 12-COLUMN ONBOARDING & TRANSFER TRACKER WORKSPACE -->
  <main class="max-w-7xl mx-auto px-6 py-6 grid lg:grid-cols-12 gap-6 items-start">

    <!-- LEFT 7 COLUMNS: 4-STEP TRANSFER TIMELINE -->
    <section class="lg:col-span-7 space-y-4">
      <div class="stripe-card p-6">
        <div class="flex flex-wrap items-center justify-between gap-2 pb-4 mb-5 border-b border-slate-100">
          <div>
            <span class="text-xs font-bold uppercase tracking-wider text-[#4F46E5]">Mr. Cooper → Rocket Mortgage Boarding Ledger</span>
            <h2 class="text-lg md:text-xl font-extrabold text-slate-900 mt-0.5">
              4-Step Servicing Transfer &amp; Protection Timeline
            </h2>
          </div>
          <span class="text-xs font-semibold text-slate-500">Click any step to inspect audit proof</span>
        </div>

        <div class="space-y-3.5">
          <!-- Step 1: Principal Balance Match $342,180.44 -->
          <div id="step-card-1" onclick="window.selectTransferStep(1)" class="step-card active p-4">
            <div class="flex items-start justify-between gap-3">
              <div class="flex items-start gap-3.5">
                <div class="w-8 h-8 rounded-full bg-[#059669] text-white flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">✓</div>
                <div>
                  <div class="flex flex-wrap items-center gap-2">
                    <h3 class="text-sm md:text-base font-extrabold text-slate-900" id="step1-title">
                      1. Principal Balance Match $342,180.44
                    </h3>
                    <span class="px-2 py-0.5 rounded-full text-[11px] font-bold bg-emerald-50 text-[#059669] border border-emerald-200 mono">
                      $0.00 Variance
                    </span>
                  </div>
                  <p class="text-xs text-slate-600 mt-1">
                    Unpaid Principal Balance (<span id="step1-upb-copy" class="mono font-semibold text-slate-900">$342,180.44</span>) and <strong>5.625% fixed note rate</strong> reconciled penny-for-penny between Mr. Cooper Prior Servicer tape and Rocket Mortgage Core Ledger.
                  </p>
                </div>
              </div>
              <span class="text-xs font-bold text-[#4F46E5] shrink-0">Verified</span>
            </div>
          </div>

          <!-- Step 2: Escrow Tax/Insurance Impound Carryover -->
          <div id="step-card-2" onclick="window.selectTransferStep(2)" class="step-card p-4">
            <div class="flex items-start justify-between gap-3">
              <div class="flex items-start gap-3.5">
                <div class="w-8 h-8 rounded-full bg-[#059669] text-white flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">✓</div>
                <div>
                  <div class="flex flex-wrap items-center gap-2">
                    <h3 class="text-sm md:text-base font-extrabold text-slate-900">
                      2. Escrow Tax/Insurance Impound Carryover
                    </h3>
                    <span class="px-2 py-0.5 rounded-full text-[11px] font-bold bg-emerald-50 text-[#059669] border border-emerald-200 mono" id="step2-escrow-badge">
                      $4,280.00 Carried Over
                    </span>
                  </div>
                  <p class="text-xs text-slate-600 mt-1">
                    Your existing property tax and homeowners insurance impound balance (<span id="step2-escrow-copy" class="mono font-semibold text-slate-900">$4,280.00</span>) transferred intact with unbroken county tax &amp; carrier disbursement schedules.
                  </p>
                </div>
              </div>
              <span class="text-xs font-bold text-[#059669] shrink-0">Intact</span>
            </div>
          </div>

          <!-- Step 3: AutoPay ACH Routing Continuity -->
          <div id="step-card-3" onclick="window.selectTransferStep(3)" class="step-card p-4">
            <div class="flex items-start justify-between gap-3">
              <div class="flex items-start gap-3.5">
                <div class="w-8 h-8 rounded-full bg-[#059669] text-white flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">✓</div>
                <div>
                  <div class="flex flex-wrap items-center gap-2">
                    <h3 class="text-sm md:text-base font-extrabold text-slate-900">
                      3. AutoPay ACH Routing Continuity
                    </h3>
                    <span class="px-2 py-0.5 rounded-full text-[11px] font-bold bg-indigo-50 text-[#4F46E5] border border-indigo-200 mono">
                      Chase Checking ••••4819
                    </span>
                  </div>
                  <p class="text-xs text-slate-600 mt-1">
                    Plaid / NACHA recurring ACH authorization bridged automatically. Your monthly draft of <strong id="step3-draft-amt" class="mono text-slate-900">$2,485.12/mo</strong> on the 1st of each month continues with zero action required.
                  </p>
                </div>
              </div>
              <span class="text-xs font-bold text-[#4F46E5] shrink-0">Bridged</span>
            </div>
          </div>

          <!-- Step 4: 60-Day RESPA Goodbye/Hello Fee Waiver Shield -->
          <div id="step-card-4" onclick="window.selectTransferStep(4)" class="step-card p-4">
            <div class="flex items-start justify-between gap-3">
              <div class="flex items-start gap-3.5">
                <div class="w-8 h-8 rounded-full bg-[#059669] text-white flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">✓</div>
                <div>
                  <div class="flex flex-wrap items-center gap-2">
                    <h3 class="text-sm md:text-base font-extrabold text-slate-900">
                      4. 60-Day RESPA Goodbye/Hello Fee Waiver Shield
                    </h3>
                    <span class="px-2 py-0.5 rounded-full text-[11px] font-bold bg-emerald-50 text-[#059669] border border-emerald-200 mono">
                      12 CFR § 1024.33(c)
                    </span>
                  </div>
                  <p class="text-xs text-slate-600 mt-1">
                    Federal 60-day safe harbor active: even if a check or bank bill-pay is accidentally mailed to Mr. Cooper during the first 60 days, <strong>$0 late fees</strong> apply and it is forwarded &amp; credited as on-time.
                  </p>
                </div>
              </div>
              <span class="text-xs font-bold text-[#059669] shrink-0">Protected</span>
            </div>
          </div>
        </div>
      </div>

      <!-- SELECTED STEP CRYPTOGRAPHIC AUDIT CERTIFICATE -->
      <div class="stripe-card p-6 bg-slate-900 text-white">
        <div class="flex items-center justify-between pb-3 mb-3 border-b border-slate-800">
          <div class="flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
            <span class="text-xs font-bold uppercase tracking-wider mono text-indigo-300" id="audit-cert-title">
              STEP 1 AUDIT PROOF · PRINCIPAL BALANCE RECONCILIATION
            </span>
          </div>
          <span class="text-[11px] mono text-emerald-400" id="empathy-model-tag">SHA-256 Ledger Match</span>
        </div>
        <p id="live-empathy-script" class="text-xs md:text-sm text-slate-200 leading-relaxed">
          Prior Servicer (Mr. Cooper Loan #0912-7741-MC) ending Unpaid Principal Balance of <strong>$342,180.44</strong> matches Rocket Mortgage Boarding Ledger (#RKT-8841-2026) to the exact cent ($0.00 variance). Fixed note rate locked at 5.625% with 312 remaining payments.
        </p>
      </div>
    </section>

    <!-- RIGHT 5 COLUMNS: INTERACTIVE LOAN BALANCE & ESCROW SLIDERS + SIDE-BY-SIDE LEDGER COMPARISON -->
    <aside class="lg:col-span-5 space-y-6">

      <!-- INTERACTIVE LOAN BALANCE & ESCROW SLIDERS -->
      <section class="stripe-card p-6 space-y-5">
        <div>
          <span class="text-xs font-bold uppercase tracking-wider text-[#4F46E5]">Interactive Boarding Inspector</span>
          <h2 class="text-lg font-extrabold text-slate-900 mt-0.5">Loan Balance &amp; Escrow Carryover Sliders</h2>
          <p class="text-xs text-slate-500 mt-0.5">Adjust the transferred principal balance or escrow impound to verify real-time reconciliation.</p>
        </div>

        <div class="space-y-4">
          <div>
            <div class="flex justify-between text-xs font-semibold mb-1">
              <span class="text-slate-600">Transferred Principal Balance (UPB):</span>
              <strong id="lbl-board-upb" class="mono text-[#4F46E5]">$342,180.44</strong>
            </div>
            <input id="slider-board-upb" type="range" min="180180.44" max="620180.44" step="5000" value="342180.44"
                   oninput="window.updateBoardingAudit()" class="w-full cursor-pointer">
          </div>

          <div>
            <div class="flex justify-between text-xs font-semibold mb-1">
              <span class="text-slate-600">Escrow Impound Carryover Balance:</span>
              <strong id="lbl-board-escrow" class="mono text-[#059669]">$4,280.00</strong>
            </div>
            <input id="slider-board-escrow" type="range" min="1200" max="9600" step="120" value="4280"
                   oninput="window.updateBoardingAudit()" class="w-full cursor-pointer">
          </div>

          <div>
            <div class="flex justify-between text-xs font-semibold mb-1">
              <span class="text-slate-600">Monthly PITI AutoPay Draft:</span>
              <strong id="lbl-board-piti" class="mono text-slate-900">$2,485.12/mo</strong>
            </div>
            <input id="slider-board-piti" type="range" min="1685.12" max="4285.12" step="100" value="2485.12"
                   oninput="window.updateBoardingAudit()" class="w-full cursor-pointer">
          </div>
        </div>

        <!-- Side-by-Side Ledger Verification Table -->
        <div class="rounded-2xl border border-slate-200 overflow-hidden text-xs">
          <div class="grid grid-cols-3 bg-slate-50 px-4 py-2.5 font-bold text-slate-600 border-b border-slate-200">
            <span>Ledger Field</span>
            <span class="text-right">Mr. Cooper</span>
            <span class="text-right text-[#4F46E5]">Rocket Mortgage</span>
          </div>
          <div class="divide-y divide-slate-100">
            <div class="grid grid-cols-3 px-4 py-2.5 items-center">
              <span class="font-semibold text-slate-700">Principal Balance</span>
              <span id="tbl-mc-upb" class="text-right mono text-slate-600">$342,180.44</span>
              <span id="tbl-rkt-upb" class="text-right mono font-bold text-[#059669]">$342,180.44 ✓</span>
            </div>
            <div class="grid grid-cols-3 px-4 py-2.5 items-center">
              <span class="font-semibold text-slate-700">Escrow Impound</span>
              <span id="tbl-mc-esc" class="text-right mono text-slate-600">$4,280.00</span>
              <span id="tbl-rkt-esc" class="text-right mono font-bold text-[#059669]">$4,280.00 ✓</span>
            </div>
            <div class="grid grid-cols-3 px-4 py-2.5 items-center">
              <span class="font-semibold text-slate-700">Fixed Note Rate</span>
              <span class="text-right mono text-slate-600">5.625%</span>
              <span class="text-right mono font-bold text-[#059669]">5.625% ✓</span>
            </div>
            <div class="grid grid-cols-3 px-4 py-2.5 items-center">
              <span class="font-semibold text-slate-700">Monthly AutoPay</span>
              <span id="tbl-mc-piti" class="text-right mono text-slate-600">$2,485.12</span>
              <span id="tbl-rkt-piti" class="text-right mono font-bold text-[#059669]">$2,485.12 ✓</span>
            </div>
          </div>
        </div>

        <button onclick="window.downloadWelcomeCertificate()"
                class="w-full py-3.5 px-4 rounded-xl font-bold text-sm text-white bg-[#059669] hover:bg-emerald-700 shadow-md transition cursor-pointer flex items-center justify-center gap-2">
          <span>✓ Confirm Onboarding Audit &amp; Issue Welcome Certificate</span>
        </button>

        <div id="welcome-cert-toast" class="hidden p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-[#059669] text-xs font-semibold text-center"></div>
      </section>
    </aside>
  </main>

  <script>
    let activeStep = 1;

    function fmtMoney(n) {{
      return '$' + Number(n).toLocaleString('en-US', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
    }}

    window.playPersonalizedWelcomeCall = function(btnEl) {{
      const upb = parseFloat(document.getElementById('slider-board-upb').value || 342180.44);
      const esc = parseFloat(document.getElementById('slider-board-escrow').value || 4280);
      const piti = parseFloat(document.getElementById('slider-board-piti').value || 2485.12);
      const msg = `Welcome to Rocket Mortgage! We are thrilled to care for your home loan following our partnership with Mr. Cooper. We have completed our automated four-step boarding audit: your unpaid principal balance of ${{fmtMoney(upb)}} and your 5.625 percent fixed rate match to the exact penny, your ${{fmtMoney(esc)}} tax and insurance escrow balance carried over intact, and your automatic payment of ${{fmtMoney(piti)}} from Chase Checking ending in 4819 will continue seamlessly with zero action needed from you. Plus, your 60-day RESPA fee-waiver shield is active from day one!`;
      window.playLiveCallClip(msg, 'Puck', 'Rocket Mortgage Welcome Concierge', btnEl);
    }};

    window.selectTransferStep = function(stepNum) {{
      activeStep = stepNum;
      [1, 2, 3, 4].forEach(i => {{
        const c = document.getElementById('step-card-' + i);
        if (c) {{
          if (i === stepNum) c.classList.add('active');
          else c.classList.remove('active');
        }}
      }});
      window.updateBoardingAudit();
    }};

    let boardTimer = null;
    window.updateBoardingAudit = function() {{
      const upb = parseFloat(document.getElementById('slider-board-upb').value || 342180.44);
      const esc = parseFloat(document.getElementById('slider-board-escrow').value || 4280);
      const piti = parseFloat(document.getElementById('slider-board-piti').value || 2485.12);

      document.getElementById('banner-upb').innerText = fmtMoney(upb);
      document.getElementById('lbl-board-upb').innerText = fmtMoney(upb);
      document.getElementById('lbl-board-escrow').innerText = fmtMoney(esc);
      document.getElementById('lbl-board-piti').innerText = fmtMoney(piti) + '/mo';

      document.getElementById('step1-title').innerText = `1. Principal Balance Match ${{fmtMoney(upb)}}`;
      document.getElementById('step1-upb-copy').innerText = fmtMoney(upb);
      document.getElementById('step2-escrow-badge').innerText = `${{fmtMoney(esc)}} Carried Over`;
      document.getElementById('step2-escrow-copy').innerText = fmtMoney(esc);
      document.getElementById('step3-draft-amt').innerText = fmtMoney(piti) + '/mo';

      document.getElementById('tbl-mc-upb').innerText = fmtMoney(upb);
      document.getElementById('tbl-rkt-upb').innerText = fmtMoney(upb) + ' ✓';
      document.getElementById('tbl-mc-esc').innerText = fmtMoney(esc);
      document.getElementById('tbl-rkt-esc').innerText = fmtMoney(esc) + ' ✓';
      document.getElementById('tbl-mc-piti').innerText = fmtMoney(piti);
      document.getElementById('tbl-rkt-piti').innerText = fmtMoney(piti) + ' ✓';

      const certTitle = document.getElementById('audit-cert-title');
      const certBody = document.getElementById('live-empathy-script');

      if (activeStep === 1) {{
        certTitle.innerText = 'STEP 1 AUDIT PROOF · PRINCIPAL BALANCE RECONCILIATION';
        certBody.innerHTML = `Prior Servicer (Mr. Cooper Loan #0912-7741-MC) ending Unpaid Principal Balance of <strong>${{fmtMoney(upb)}}</strong> matches Rocket Mortgage Boarding Ledger (#RKT-8841-2026) to the exact cent ($0.00 variance). Fixed note rate locked at 5.625%.`;
      }} else if (activeStep === 2) {{
        certTitle.innerText = 'STEP 2 AUDIT PROOF · ESCROW IMPOUND & DISBURSEMENT CONTINUITY';
        certBody.innerHTML = `Full Escrow Impound Balance of <strong>${{fmtMoney(esc)}}</strong> transferred with zero holdback. Upcoming county property tax and hazard insurance policy disbursements are scheduled automatically.`;
      }} else if (activeStep === 3) {{
        certTitle.innerText = 'STEP 3 AUDIT PROOF · NACHA / PLAID AUTOPAY ROUTING BRIDGE';
        certBody.innerHTML = `Existing recurring ACH mandate on <strong>Chase Checking ••••4819</strong> bridged to Rocket Mortgage Servicing. Your monthly draft of <strong>${{fmtMoney(piti)}}/mo</strong> will draft on the 1st of the month without interruption.`;
      }} else {{
        certTitle.innerText = 'STEP 4 AUDIT PROOF · 60-DAY RESPA § 1024.33(c) SAFE HARBOR';
        certBody.innerHTML = `Statutory 60-day Goodbye/Hello protection active from transfer effective date: any payment sent to Mr. Cooper is automatically forwarded to Rocket Mortgage with <strong>$0 late fees</strong> and <strong>zero adverse credit reporting</strong>.`;
      }}

      clearTimeout(boardTimer);
      boardTimer = setTimeout(async () => {{
        try {{
          const res = await fetch('/api/sandbox', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
              code: '3.3',
              action: 'eval_loss_mitigation',
              params: {{
                piti: piti,
                upb: upb,
                escrow_balance: esc
              }}
            }})
          }});
          const data = await res.json();
          const pill = document.getElementById('hud-sandbox-pill');
          if (pill && data.execution_ms !== undefined) {{
            pill.innerText = `4 / 4 Verified (${{data.execution_ms}}ms)`;
          }}
        }} catch (e) {{}}
      }}, 180);
    }};

    window.downloadWelcomeCertificate = function() {{
      const toast = document.getElementById('welcome-cert-toast');
      const upb = parseFloat(document.getElementById('slider-board-upb').value || 342180.44);
      toast.classList.remove('hidden');
      toast.innerHTML = `✓ Boarding Audit Certified! Welcome Certificate #RKT-WELCOME-2026-994 issued for Principal Balance <strong>${{fmtMoney(upb)}}</strong> with 60-Day RESPA Protection.`;
    }};

    window.runLiveVertexAI = async function() {{
      const btn = document.getElementById('synthesize-empathy-btn');
      const scriptEl = document.getElementById('live-empathy-script');
      const modelTag = document.getElementById('empathy-model-tag');
      const upb = parseFloat(document.getElementById('slider-board-upb').value || 342180.44);
      const esc = parseFloat(document.getElementById('slider-board-escrow').value || 4280);
      const piti = parseFloat(document.getElementById('slider-board-piti').value || 2485.12);
      const scenarioInput = document.getElementById('scenario-input') ? document.getElementById('scenario-input').value : '';

      if (btn) btn.innerHTML = `<span class="shrinking-shining-ink"></span> <span>Auditing...</span>`;
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '3.3',
            model: window.getSelectedModel(),
            user_input: scenarioInput || `Audit Mr. Cooper to Rocket Mortgage loan boarding for UPB ${{upb}}, Escrow ${{esc}}, AutoPay ${{piti}}/mo.`,
            params: {{
              piti: piti,
              upb: upb,
              escrow_balance: esc
            }}
          }})
        }});
        const data = await res.json();
        const sd = data.structured_data || {{}};
        if (modelTag && data.vertex) {{
          modelTag.innerText = `${{data.vertex.model_used}} (${{data.vertex.latency_ms}}ms)`;
        }}
        if (sd.executive_summary && scriptEl) {{
          scriptEl.innerHTML = sd.executive_summary;
        }} else if (data.vertex && data.vertex.response_markdown && scriptEl) {{
          scriptEl.innerHTML = data.vertex.response_markdown;
        }}
      }} catch (e) {{
        console.error(e);
      }} finally {{
        if (btn) btn.innerHTML = `<span>⚡ Re-Run Boarding Audit</span>`;
      }}
    }};

    document.addEventListener('DOMContentLoaded', () => {{
      window.updateBoardingAudit();
    }});
  </script>

  {render_floating_control_bar_and_drawer("3.3", auth_token)}
</body>
</html>"""
