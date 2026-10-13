# -*- coding: utf-8 -*-
"""Square 3.2: Self-Service Payoff Quote & IRS Form 1098 Action Agent (Google ADK Runtime)
Visual Design: Official Treasury & Mortgage Document Portal (#0F172A slate chrome framing a crisp
#FFFFFF printable official Payoff Statement & IRS Form 1098 with #EAB308 gold seal accents,
Google Fonts Libre Baskerville + JetBrains Mono)."""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_3_2(auth_token: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Official Treasury &amp; Payoff Document Portal | Google ADK Runtime [3.2]</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    body {{
      background-color: #0F172A;
      color: #F8FAFC;
      font-family: 'Inter', sans-serif;
      margin: 0;
    }}
    .serif-doc {{
      font-family: 'Libre Baskerville', Georgia, serif;
    }}
    .mono {{
      font-family: 'JetBrains Mono', monospace;
    }}
    .paper-sheet {{
      background: #FFFFFF;
      color: #0F172A;
      box-shadow: 0 25px 60px rgba(0, 0, 0, 0.65), 0 0 0 1px rgba(234, 179, 8, 0.35);
      border-top: 6px solid #EAB308;
    }}
    .gold-seal {{
      background: radial-gradient(circle at 30% 30%, #FEF08A, #EAB308, #A16207);
      box-shadow: 0 4px 16px rgba(234, 179, 8, 0.4);
    }}
    input[type="range"] {{
      accent-color: #EAB308;
    }}
    .shrinking-shining-ink {{
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background: radial-gradient(circle at 30% 30%, #FEF08A, #EAB308, #10B981);
      animation: inkPulse 1.2s ease-in-out infinite;
      display: inline-block;
    }}
    @keyframes inkPulse {{
      0%, 100% {{ transform: scale(1); opacity: 0.95; }}
      50% {{ transform: scale(0.55); opacity: 0.5; }}
    }}
  </style>
</head>
<body class="min-h-screen pb-24">

  <!-- TOP SLATE TREASURY & DOCUMENT PORTAL HEADER -->
  <header class="sticky top-0 z-40 bg-slate-950/95 backdrop-blur border-b border-slate-800 px-6 py-3.5">
    <div class="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-3.5">
        <div class="w-10 h-10 rounded-xl gold-seal flex items-center justify-center text-slate-950 font-black mono text-sm">
          §
        </div>
        <div>
          <div class="flex items-center gap-2">
            <span class="text-[11px] font-bold uppercase tracking-widest text-yellow-400 mono">
              MR. COOPER x ROCKET TREASURY DESK • GOOGLE ADK RUNTIME
            </span>
            <span class="px-2 py-0.5 rounded bg-yellow-500/15 text-yellow-300 border border-yellow-500/30 text-[10px] mono font-bold">
              ACTUAL/365 PER-DIEM ENGINE
            </span>
          </div>
          <h1 class="text-lg md:text-xl font-bold text-white serif-doc tracking-tight">
            Official Mortgage Payoff Statement &amp; IRS Form 1098 Tax Certificate Portal
          </h1>
        </div>
      </div>

      <!-- Inline Model Selector + Print Action -->
      <div class="flex flex-wrap items-center gap-3">
        <div class="flex items-center gap-2 bg-slate-900 border border-slate-700 rounded-xl px-3 py-1.5">
          <span class="w-2 h-2 rounded-full bg-yellow-400"></span>
          <label for="app-model-select" class="text-[10px] mono uppercase text-slate-400 font-bold">ADK Model:</label>
          <select id="app-model-select" onchange="window.syncSelectedModel(this.value)"
                  class="bg-transparent text-yellow-400 text-xs font-bold mono focus:outline-none cursor-pointer">
            <option value="gemini-4-argon" class="bg-slate-900 text-sky-300">gemini-4-argon (Frontier Global)</option>
            <option value="gemini-3.8-flash" selected class="bg-slate-900 text-yellow-300">gemini-3.8-flash (ADK Runtime Default)</option>
          </select>
        </div>
        <button onclick="window.print()" class="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-bold mono text-slate-200 transition">
          🖨️ Print Official PDF
        </button>
      </div>
    </div>
  </header>

  <!-- MAIN WORKSPACE: LEFT CONTROL RAIL (4 COLS) + RIGHT PRINTABLE OFFICIAL DOCUMENT CANVAS (8 COLS) -->
  <main class="max-w-7xl mx-auto px-6 py-6 grid lg:grid-cols-12 gap-6 items-start">

    <!-- LEFT INTERACTIVE CONTROL RAIL -->
    <aside class="lg:col-span-4 bg-slate-900/90 border border-slate-800 rounded-2xl p-5 space-y-5 shadow-2xl">
      <div class="pb-3 border-b border-slate-800 flex items-center justify-between">
        <div>
          <div class="text-[10px] mono uppercase tracking-wider text-yellow-400 font-bold">ADK Tool Parameters</div>
          <h2 class="text-sm font-bold text-white mt-0.5">Per-Diem &amp; County Lien Release Calculator</h2>
        </div>
        <span id="payoff-sandbox-badge" class="px-2 py-0.5 rounded text-[10px] mono bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
          0.3ms Sandbox
        </span>
      </div>

      <!-- Good-Through Date Picker & Accrued Days Slider -->
      <div class="space-y-1.5">
        <div class="flex justify-between text-xs mono">
          <label class="text-slate-300 font-semibold">Good-Through Payoff Date:</label>
          <span id="lbl-good-date" class="text-yellow-400 font-bold">Nov 12, 2026</span>
        </div>
        <input id="input-good-date" type="date" value="2026-11-12" onchange="window.syncDateToDays(this.value)"
               class="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-700 text-xs mono text-white focus:border-yellow-500 focus:outline-none">
      </div>

      <div class="space-y-1">
        <div class="flex justify-between text-xs mono">
          <span class="text-slate-400">Accrued Interest Days (since Oct 1):</span>
          <strong id="lbl-days" class="text-yellow-400">42 Days</strong>
        </div>
        <input id="slider-days" type="range" min="5" max="60" step="1" value="42"
               oninput="window.updatePayoffControls()" class="w-full cursor-pointer">
      </div>

      <!-- Unpaid Principal Balance Slider -->
      <div class="space-y-1">
        <div class="flex justify-between text-xs mono">
          <span class="text-slate-400">Unpaid Principal Balance (UPB):</span>
          <strong id="lbl-upb" class="text-yellow-400">$284,500.00</strong>
        </div>
        <input id="slider-upb" type="range" min="150000" max="650000" step="2500" value="284500"
               oninput="window.updatePayoffControls()" class="w-full cursor-pointer">
      </div>

      <!-- Note Interest Rate Slider -->
      <div class="space-y-1">
        <div class="flex justify-between text-xs mono">
          <span class="text-slate-400">Note Interest Rate (Actual/365):</span>
          <strong id="lbl-rate" class="text-yellow-400">6.000%</strong>
        </div>
        <input id="slider-rate" type="range" min="3.0" max="8.0" step="0.125" value="6.0"
               oninput="window.updatePayoffControls()" class="w-full cursor-pointer">
      </div>

      <!-- State County Recording Fee Selector -->
      <div class="space-y-1.5">
        <label class="block text-xs mono text-slate-300 font-semibold">State / County Lien Release Fee:</label>
        <select id="select-county-fee" onchange="window.updatePayoffControls()"
                class="w-full px-3 py-2.5 rounded-xl bg-slate-950 border border-slate-700 text-xs mono text-white focus:border-yellow-500 focus:outline-none">
          <option value="30.00" data-county="Wayne County, MI (MCL 600.2567)">Wayne County, MI — $30.00 Statutory Discharge</option>
          <option value="30.00" data-county="Oakland County, MI (MCL 600.2567)">Oakland County, MI — $30.00 Statutory Discharge</option>
          <option value="45.00" data-county="Cook County, IL (Release of Mortgage)">Cook County, IL — $45.00 Release Recording</option>
          <option value="26.00" data-county="Travis County, TX (County Clerk)">Travis County, TX — $26.00 Lien Release</option>
          <option value="14.00" data-county="Maricopa County, AZ (Flat Release)">Maricopa County, AZ — $14.00 Flat Release</option>
        </select>
      </div>

      <!-- ADK Tool Execution Telemetry Box -->
      <div class="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-2 text-xs mono">
        <div class="text-[10px] uppercase text-slate-400 font-bold">ADK Sub-Agent Tool Chain Status</div>
        <div class="flex items-center justify-between">
          <span class="text-slate-300">1. <code>get_loan_balance_and_rate</code></span>
          <span class="text-emerald-400 font-bold">✓ PASS</span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-slate-300">2. <code>calculate_per_diem_payoff</code></span>
          <span id="tool-perdiem-val" class="text-yellow-400 font-bold">$46.77/day</span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-slate-300">3. <code>fetch_irs_form_1098_data</code></span>
          <span class="text-emerald-400 font-bold">✓ TAX YR 2025</span>
        </div>
      </div>

      <!-- Primary Action Button -->
      <button id="adk-verify-btn" onclick="window.runLiveVertexAI()"
              class="w-full py-3.5 px-4 rounded-xl font-bold text-xs mono text-slate-950 shadow-xl transition transform active:scale-[0.99] flex items-center justify-center gap-2"
              style="background: linear-gradient(135deg, #FACC15 0%, #EAB308 55%, #CA8A04 100%);">
        <span>⚡ Run ADK Agent Verification &amp; Issue Payoff Wire Instructions</span>
      </button>

      <div id="adk-live-verdict" class="p-3.5 rounded-xl bg-yellow-500/10 border border-yellow-500/30 text-xs text-yellow-100 leading-relaxed">
        <div class="font-bold mono text-[10px] uppercase text-yellow-400 mb-1">ADK Runtime Verification Note</div>
        <div id="adk-verdict-text">
          Per-diem interest verified at <strong>$46.77/day</strong> ($284,500.00 × 6.000% ÷ 365). Existing positive escrow balance of <strong>$1,120.00</strong> is scheduled for automatic ACH refund within 10 business days of payoff wire receipt.
        </div>
      </div>
    </aside>

    <!-- RIGHT MAIN CANVAS: DUAL-TABBED OFFICIAL PRINTABLE PAYOFF QUOTE & IRS FORM 1098 -->
    <section class="lg:col-span-8 space-y-4">

      <!-- Document Tab Switcher -->
      <div class="flex flex-wrap items-center justify-between gap-3 bg-slate-900 border border-slate-800 p-2 rounded-2xl">
        <div class="flex gap-2">
          <button id="tab-btn-payoff" onclick="window.switchDocTab('payoff')"
                  class="px-4 py-2 rounded-xl text-xs font-bold mono bg-yellow-400 text-slate-950 shadow transition">
            📜 Tab 1: Official Printable Payoff Statement
          </button>
          <button id="tab-btn-1098" onclick="window.switchDocTab('1098')"
                  class="px-4 py-2 rounded-xl text-xs font-bold mono text-slate-300 hover:bg-slate-800 transition">
            🏛️ Tab 2: Official IRS Form 1098 Tax Certificate
          </button>
        </div>
        <span class="px-3 py-1 rounded-lg bg-slate-950 text-[11px] mono text-yellow-400 border border-yellow-500/30">
          Cert #RKT-PAY-2026-99214
        </span>
      </div>

      <!-- TAB 1: OFFICIAL PRINTABLE PAYOFF STATEMENT PDF PREVIEW -->
      <div id="doc-pane-payoff" class="paper-sheet rounded-2xl p-8 md:p-10">
        <!-- Letterhead -->
        <div class="flex flex-wrap items-start justify-between gap-4 pb-6 border-b-2 border-slate-900">
          <div>
            <div class="text-xs font-bold uppercase tracking-widest text-amber-700 mono">MR. COOPER GROUP INC. • ROCKET MORTGAGE SERVICING</div>
            <h2 class="text-2xl md:text-3xl font-bold serif-doc text-slate-900 mt-1">OFFICIAL PAYOFF DEMAND STATEMENT</h2>
            <p class="text-xs text-slate-600 mt-1">Issued Pursuant to 12 CFR § 1026.36(c)(3) (TILA Payoff Statement Rule)</p>
          </div>
          <div class="text-right mono text-xs">
            <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full gold-seal text-slate-950 font-extrabold text-[11px] mb-1">
              ★ TREASURY CERTIFIED
            </div>
            <div class="text-slate-600">Statement Date: <strong>Oct 13, 2026</strong></div>
            <div class="text-slate-900 font-bold">Loan Number: #0449-8821-RKT</div>
          </div>
        </div>

        <!-- Borrower & Property Metadata Grid -->
        <div class="grid sm:grid-cols-2 gap-4 my-6 p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs">
          <div>
            <div class="text-[10px] font-bold uppercase text-slate-500 mono">Borrower(s) &amp; Property Address</div>
            <div class="font-bold text-slate-900 text-sm mt-0.5 serif-doc">Elena &amp; David Rostova</div>
            <div class="text-slate-700">1420 Woodward Ave, Unit 4B, Detroit, MI 48226</div>
            <div class="text-slate-500 mono mt-1" id="doc-county-label">Jurisdiction: Wayne County, MI (MCL 600.2567)</div>
          </div>
          <div class="sm:text-right">
            <div class="text-[10px] font-bold uppercase text-slate-500 mono">Quote Good-Through Expiration</div>
            <div id="doc-good-date" class="font-bold text-amber-800 text-base mt-0.5 mono">November 12, 2026 (5:00 PM EST)</div>
            <div class="text-slate-700 mono">Daily Per-Diem Interest Rate: <strong id="doc-per-diem">$46.77 / day</strong></div>
            <div class="text-slate-500 mono">Note Rate: <span id="doc-note-rate">6.000%</span> (Actual/365 Basis)</div>
          </div>
        </div>

        <!-- Itemized Payoff Calculation Table -->
        <div class="border border-slate-300 rounded-xl overflow-hidden mb-6">
          <table class="w-full text-left border-collapse text-xs md:text-sm">
            <thead>
              <tr class="bg-slate-900 text-white mono text-xs uppercase">
                <th class="py-3 px-4">Payoff Line Item Description</th>
                <th class="py-3 px-4">Statutory / Math Basis</th>
                <th class="py-3 px-4 text-right">Verified Amount</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200">
              <tr>
                <td class="py-3.5 px-4 font-semibold text-slate-900 serif-doc">1. Unpaid Principal Balance (UPB)</td>
                <td class="py-3.5 px-4 text-slate-600 mono text-xs">Principal as of Last Paid Installment (Oct 1, 2026)</td>
                <td id="tbl-upb" class="py-3.5 px-4 text-right font-bold mono text-slate-900">$284,500.00</td>
              </tr>
              <tr class="bg-amber-50/40">
                <td class="py-3.5 px-4 font-semibold text-slate-900 serif-doc">2. Accrued Interest to Good-Through Date</td>
                <td id="tbl-int-formula" class="py-3.5 px-4 text-slate-600 mono text-xs">42 Days × $46.77/day (Oct 1 – Nov 12, 2026)</td>
                <td id="tbl-accrued-int" class="py-3.5 px-4 text-right font-bold mono text-slate-900">$1,964.34</td>
              </tr>
              <tr>
                <td class="py-3.5 px-4 font-semibold text-slate-900 serif-doc">3. County Mortgage Discharge / Release Fee</td>
                <td id="tbl-fee-basis" class="py-3.5 px-4 text-slate-600 mono text-xs">Wayne County Register of Deeds Statutory Fee</td>
                <td id="tbl-rec-fee" class="py-3.5 px-4 text-right font-bold mono text-slate-900">$30.00</td>
              </tr>
              <tr class="bg-slate-50">
                <td class="py-3 px-4 text-slate-600 serif-doc">4. Prepayment Penalty / Late Charges</td>
                <td class="py-3 px-4 text-slate-500 mono text-xs">Fannie Mae / Freddie Mac Uniform Note ($0 Penalty)</td>
                <td class="py-3 px-4 text-right font-bold mono text-emerald-700">$0.00</td>
              </tr>
            </tbody>
            <tfoot>
              <tr class="bg-slate-900 text-white">
                <td colspan="2" class="py-4 px-4 font-bold uppercase tracking-wider mono text-xs">
                  TOTAL OFFICIAL PAYOFF FUNDS REQUIRED BY <span id="tbl-footer-date" class="text-yellow-400">NOV 12, 2026</span>
                </td>
                <td id="tbl-total-payoff" class="py-4 px-4 text-right text-xl font-extrabold mono text-yellow-400">
                  $286,494.34
                </td>
              </tr>
            </tfoot>
          </table>
        </div>

        <!-- Fedwire Instructions & Escrow Surplus Refund Notice -->
        <div class="grid sm:grid-cols-2 gap-4 text-xs">
          <div class="p-4 rounded-xl bg-amber-50 border border-amber-300">
            <div class="font-bold uppercase tracking-wider text-amber-900 mono text-[11px] mb-1">
              🏦 Official Same-Day Fedwire Payoff Instructions
            </div>
            <div class="space-y-1 mono text-slate-800">
              <div>Beneficiary Bank: <strong>JPMorgan Chase Bank, N.A.</strong></div>
              <div>ABA Routing (Wire): <strong id="wire-aba">021000021</strong></div>
              <div>Beneficiary Acct: <strong id="wire-acct">8800-4912-0449 (Mr. Cooper Payoff Trust)</strong></div>
              <div>Reference Credit: <strong>Loan #0449-8821-RKT — E. Rostova</strong></div>
            </div>
          </div>
          <div class="p-4 rounded-xl bg-emerald-50 border border-emerald-300">
            <div class="font-bold uppercase tracking-wider text-emerald-900 mono text-[11px] mb-1">
              💸 Automatic Escrow Surplus Refund ($1,120.00)
            </div>
            <p class="text-slate-700 leading-relaxed">
              Your current positive escrow balance of <strong>$1,120.00</strong> is held in trust and will be automatically refunded via direct ACH to your linked checking account (<code>••••4819</code>) within 10 business days of payoff clearance.
            </p>
          </div>
        </div>
      </div>

      <!-- TAB 2: OFFICIAL IRS FORM 1098 TAX CERTIFICATE PREVIEW -->
      <div id="doc-pane-1098" class="hidden paper-sheet rounded-2xl p-8 md:p-10">
        <div class="flex flex-wrap items-start justify-between gap-4 pb-5 border-b-2 border-slate-900">
          <div>
            <div class="text-xs font-bold uppercase tracking-widest text-slate-500 mono">OMB No. 1545-1380 • COPY B FOR PAYER/BORROWER</div>
            <h2 class="text-2xl font-bold serif-doc text-slate-900 mt-1">IRS Form 1098: Mortgage Interest Statement</h2>
            <p class="text-xs text-slate-600 mt-0.5">Information Return Reported to the Internal Revenue Service</p>
          </div>
          <div class="text-right mono">
            <div class="text-2xl font-black text-slate-900">2025 / 2026 YTD</div>
            <div class="text-xs text-amber-700 font-bold">VERIFIED TAX CERTIFICATE</div>
          </div>
        </div>

        <div class="grid sm:grid-cols-2 gap-4 my-6 text-xs mono">
          <div class="p-4 rounded-xl border border-slate-300 bg-slate-50">
            <div class="text-[10px] font-bold uppercase text-slate-500">RECIPIENT'S / LENDER'S NAME, ADDRESS &amp; TIN</div>
            <div class="font-bold text-slate-900 mt-1">Nationstar Mortgage LLC d/b/a Mr. Cooper</div>
            <div class="text-slate-600">8950 Cypress Waters Blvd, Coppell, TX 75019</div>
            <div class="text-slate-800 mt-1">Federal FEIN: <strong>75-2921540</strong></div>
          </div>
          <div class="p-4 rounded-xl border border-slate-300 bg-slate-50">
            <div class="text-[10px] font-bold uppercase text-slate-500">PAYER'S / BORROWER'S NAME &amp; TIN</div>
            <div class="font-bold text-slate-900 mt-1">Elena &amp; David Rostova</div>
            <div class="text-slate-600">1420 Woodward Ave, Unit 4B, Detroit, MI 48226</div>
            <div class="text-slate-800 mt-1">Borrower TIN: <strong>***-**-8841 (GLBA Masked)</strong></div>
          </div>
        </div>

        <div class="grid sm:grid-cols-3 gap-4 mb-6 text-xs mono">
          <div class="p-4 rounded-xl border-2 border-amber-500 bg-amber-50/50">
            <div class="text-[10px] font-bold text-amber-900">BOX 1 • MORTGAGE INTEREST RECEIVED</div>
            <div id="f1098-box1" class="text-xl font-extrabold text-slate-900 mt-1">$17,190.42</div>
            <div class="text-[10px] text-slate-600 mt-1">Includes prior year + YTD accrued</div>
          </div>
          <div class="p-4 rounded-xl border border-slate-300">
            <div class="text-[10px] font-bold text-slate-500">BOX 2 • OUTSTANDING MORTGAGE PRINCIPAL</div>
            <div id="f1098-box2" class="text-xl font-extrabold text-slate-900 mt-1">$284,500.00</div>
            <div class="text-[10px] text-slate-600 mt-1">Principal balance as of Jan 1</div>
          </div>
          <div class="p-4 rounded-xl border border-slate-300">
            <div class="text-[10px] font-bold text-slate-500">BOX 10 • PROPERTY TAXES PAID FROM ESCROW</div>
            <div class="text-xl font-extrabold text-emerald-700 mt-1">$5,480.00</div>
            <div class="text-[10px] text-slate-600 mt-1">Wayne County Treasurer Disbursed</div>
          </div>
        </div>

        <div class="p-4 rounded-xl bg-slate-100 border border-slate-300 text-xs text-slate-700 serif-doc leading-relaxed">
          <strong>Tax Deductibility Notice:</strong> If you pay off your mortgage on <span id="f1098-payoff-date" class="font-bold">Nov 12, 2026</span>, the additional <span id="f1098-add-int" class="font-bold">$1,964.34</span> in per-diem accrued interest paid at closing will be automatically added to Box 1 of your 2026 Form 1098.
        </div>
      </div>
    </section>
  </main>

  <script>
    function fmtUSD(v) {{
      return '$' + Number(v).toLocaleString('en-US', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
    }}

    window.switchDocTab = function(tab) {{
      const pPay = document.getElementById('doc-pane-payoff');
      const p1098 = document.getElementById('doc-pane-1098');
      const bPay = document.getElementById('tab-btn-payoff');
      const b1098 = document.getElementById('tab-btn-1098');
      if (tab === 'payoff') {{
        pPay.classList.remove('hidden');
        p1098.classList.add('hidden');
        bPay.className = 'px-4 py-2 rounded-xl text-xs font-bold mono bg-yellow-400 text-slate-950 shadow transition';
        b1098.className = 'px-4 py-2 rounded-xl text-xs font-bold mono text-slate-300 hover:bg-slate-800 transition';
      }} else {{
        pPay.classList.add('hidden');
        p1098.classList.remove('hidden');
        b1098.className = 'px-4 py-2 rounded-xl text-xs font-bold mono bg-yellow-400 text-slate-950 shadow transition';
        bPay.className = 'px-4 py-2 rounded-xl text-xs font-bold mono text-slate-300 hover:bg-slate-800 transition';
      }}
    }};

    window.syncDateToDays = function(dateStr) {{
      try {{
        const oct1 = new Date('2026-10-01T00:00:00');
        const target = new Date(dateStr + 'T00:00:00');
        const diffDays = Math.max(5, Math.min(60, Math.round((target - oct1) / (1000 * 60 * 60 * 24))));
        document.getElementById('slider-days').value = diffDays;
        window.updatePayoffControls();
      }} catch (e) {{}}
    }};

    let payoffTimer = null;
    window.updatePayoffControls = function() {{
      const days = parseInt(document.getElementById('slider-days').value || 42, 10);
      const upb = parseFloat(document.getElementById('slider-upb').value || 284500);
      const rate = parseFloat(document.getElementById('slider-rate').value || 6.0);
      const sel = document.getElementById('select-county-fee');
      const recFee = parseFloat(sel.value || 30.0);
      const countyLabel = sel.options[sel.selectedIndex].getAttribute('data-county') || 'Wayne County, MI';

      const oct1 = new Date(2026, 9, 1);
      oct1.setDate(oct1.getDate() + days);
      const dateFormatted = oct1.toLocaleDateString('en-US', {{ month: 'short', day: 'numeric', year: 'numeric' }});
      const isoDate = oct1.toISOString().slice(0, 10);
      document.getElementById('input-good-date').value = isoDate;
      document.getElementById('lbl-good-date').innerText = dateFormatted;

      const perDiem = Math.round(((upb * (rate / 100.0)) / 365.0) * 100) / 100;
      const accrued = Math.round((perDiem * days) * 100) / 100;
      const totalPayoff = upb + accrued + recFee;

      document.getElementById('lbl-days').innerText = days + ' Days';
      document.getElementById('lbl-upb').innerText = fmtUSD(upb);
      document.getElementById('lbl-rate').innerText = rate.toFixed(3) + '%';
      document.getElementById('tool-perdiem-val').innerText = fmtUSD(perDiem) + '/day';

      document.getElementById('doc-county-label').innerText = 'Jurisdiction: ' + countyLabel;
      document.getElementById('doc-good-date').innerText = dateFormatted + ' (5:00 PM EST)';
      document.getElementById('doc-per-diem').innerText = fmtUSD(perDiem) + ' / day';
      document.getElementById('doc-note-rate').innerText = rate.toFixed(3) + '%';

      document.getElementById('tbl-upb').innerText = fmtUSD(upb);
      document.getElementById('tbl-int-formula').innerText = `${{days}} Days × ${{fmtUSD(perDiem)}}/day (Oct 1 – ${{dateFormatted}})`;
      document.getElementById('tbl-accrued-int').innerText = fmtUSD(accrued);
      document.getElementById('tbl-fee-basis').innerText = countyLabel + ' Statutory Recording';
      document.getElementById('tbl-rec-fee').innerText = fmtUSD(recFee);
      document.getElementById('tbl-footer-date').innerText = dateFormatted.toUpperCase();
      document.getElementById('tbl-total-payoff').innerText = fmtUSD(totalPayoff);

      document.getElementById('f1098-box2').innerText = fmtUSD(upb);
      document.getElementById('f1098-payoff-date').innerText = dateFormatted;
      document.getElementById('f1098-add-int').innerText = fmtUSD(accrued);

      clearTimeout(payoffTimer);
      payoffTimer = setTimeout(async () => {{
        try {{
          const res = await fetch('/api/sandbox', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
              code: '3.2',
              action: 'calc_payoff_quote',
              params: {{
                upb: upb,
                rate: rate,
                days_accrued: days,
                recording_fee: recFee,
                escrow_balance: 1120.0
              }}
            }})
          }});
          const data = await res.json();
          const b = document.getElementById('payoff-sandbox-badge');
          if (b && data.execution_ms !== undefined) b.innerText = `${{data.execution_ms}}ms Sandbox`;
        }} catch (e) {{}}
      }}, 180);
    }};

    window.runLiveVertexAI = async function() {{
      const btn = document.getElementById('adk-verify-btn');
      const verdictEl = document.getElementById('adk-verdict-text');
      const days = parseInt(document.getElementById('slider-days').value || 42, 10);
      const upb = parseFloat(document.getElementById('slider-upb').value || 284500);
      const rate = parseFloat(document.getElementById('slider-rate').value || 6.0);
      const recFee = parseFloat(document.getElementById('select-county-fee').value || 30.0);
      const scenarioInput = document.getElementById('scenario-input') ? document.getElementById('scenario-input').value : '';

      if (btn) btn.innerHTML = `<span class="shrinking-shining-ink"></span> <span>Executing Google ADK Verification...</span>`;
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '3.2',
            model: window.getSelectedModel(),
            user_input: scenarioInput,
            params: {{
              upb: upb,
              rate: rate,
              days_accrued: days,
              recording_fee: recFee,
              escrow_balance: 1120.0
            }}
          }})
        }});
        const data = await res.json();
        const sd = data.structured_data || {{}};
        if (sd.payoff_letter && sd.payoff_letter.wire_aba) {{
          document.getElementById('wire-aba').innerText = sd.payoff_letter.wire_aba;
        }}
        if (sd.executive_summary && verdictEl) {{
          verdictEl.innerHTML = `<strong>[${{data.vertex ? data.vertex.model_used : window.getSelectedModel()}} Verified]:</strong> ` + sd.executive_summary;
        }} else if (data.vertex && data.vertex.response_markdown && verdictEl) {{
          verdictEl.innerHTML = data.vertex.response_markdown;
        }}
      }} catch (e) {{
        console.error(e);
      }} finally {{
        if (btn) btn.innerHTML = `<span>⚡ Run ADK Agent Verification &amp; Issue Payoff Wire Instructions</span>`;
      }}
    }};

    document.addEventListener('DOMContentLoaded', () => {{
      window.updatePayoffControls();
    }});
  </script>

  {render_floating_control_bar_and_drawer("3.2", auth_token)}
</body>
</html>"""
