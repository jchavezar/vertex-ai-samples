# -*- coding: utf-8 -*-
"""Square 3.5: Autonomous Borrower Retention & Life-Event Orchestrator (Google ADK Runtime)
Visual Design: Redfin + Mr. Cooper Family Wealth & Home Move-Up Concierge (#F5F3EF warm architectural sand,
#C82021 Redfin crimson, #15803D forest wealth green, Google Fonts Bricolage Grotesque + Inter)."""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_3_5(auth_token: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Redfin + Mr. Cooper Family Wealth &amp; Move-Up Concierge | Google ADK Runtime [3.5]</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,600;12..96,700;12..96,800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --warm-sand: #F5F3EF;
      --redfin-crimson: #C82021;
      --wealth-green: #15803D;
    }}
    body {{
      background-color: var(--warm-sand);
      color: #1C1917;
      font-family: 'Inter', sans-serif;
      margin: 0;
    }}
    .display-font {{
      font-family: 'Bricolage Grotesque', sans-serif;
    }}
    .mono {{
      font-family: 'JetBrains Mono', monospace;
    }}
    .wealth-card {{
      background: #FFFFFF;
      border: 1px solid #E7E5E4;
      border-radius: 22px;
      box-shadow: 0 12px 30px -10px rgba(28, 25, 23, 0.08);
    }}
    .redfin-prop-card {{
      border: 2px solid #E7E5E4;
      border-radius: 18px;
      transition: all 0.2s ease;
      cursor: pointer;
    }}
    .redfin-prop-card:hover {{
      transform: translateY(-2px);
      border-color: #FCA5A5;
    }}
    .redfin-prop-card.active {{
      border-color: #C82021;
      background: #FEF2F2;
      box-shadow: 0 10px 24px -6px rgba(200, 32, 33, 0.16);
    }}
    input[type="range"] {{
      accent-color: #15803D;
    }}
    .shrinking-shining-ink {{
      width: 15px;
      height: 15px;
      border-radius: 50%;
      background: radial-gradient(circle at 30% 30%, #ffffff, #C82021, #15803D);
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

  <!-- TOP REDFIN + MR. COOPER FAMILY WEALTH HEADER -->
  <header class="sticky top-0 z-40 bg-[#1C1917] text-stone-100 border-b border-stone-800 px-6 py-4 shadow-md">
    <div class="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-3.5">
        <div class="flex items-center -space-x-2">
          <div class="w-10 h-10 rounded-xl bg-[#C82021] text-white font-black display-font flex items-center justify-center text-sm shadow">R</div>
          <div class="w-10 h-10 rounded-xl bg-[#15803D] text-white font-black display-font flex items-center justify-center text-sm shadow border-2 border-[#1C1917]">MC</div>
        </div>
        <div>
          <div class="flex items-center gap-2">
            <span class="text-[11px] font-bold uppercase tracking-widest text-amber-400 mono">
              REDFIN + MR. COOPER + ROCKET MONEY • GOOGLE ADK WEALTH ORCHESTRATOR
            </span>
          </div>
          <h1 class="text-xl md:text-2xl font-extrabold display-font text-white tracking-tight">
            The Miller Family Move-Up &amp; 3.25% Rate-Lock Retention Concierge
          </h1>
        </div>
      </div>

      <!-- Inline App Bar Model Selector & ADK Trigger -->
      <div class="flex flex-wrap items-center gap-3">
        <div class="flex items-center gap-2 bg-stone-900 border border-stone-700 rounded-full px-3.5 py-1.5">
          <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
          <label for="app-model-select" class="text-[10px] mono uppercase text-stone-400 font-bold">ADK Model:</label>
          <select id="app-model-select" onchange="window.syncSelectedModel(this.value)"
                  class="bg-transparent text-amber-300 text-xs font-bold mono focus:outline-none cursor-pointer">
            <option value="gemini-4-argon" class="bg-stone-900 text-sky-300">gemini-4-argon (Frontier Global)</option>
            <option value="gemini-3.8-flash" selected class="bg-stone-900 text-emerald-300">gemini-3.8-flash (ADK Runtime Default)</option>
          </select>
        </div>
        <button id="adk-moveup-btn" onclick="window.runLiveVertexAI()"
                class="px-4 py-2 rounded-full font-bold text-xs mono text-white shadow-lg transition hover:opacity-95 flex items-center gap-2"
                style="background: linear-gradient(135deg, #C82021 0%, #15803D 100%);">
          <span>⚡ Run ADK Move-Up Matrix</span>
        </button>
      </div>
    </div>
  </header>

  <!-- MAIN 3-ZONE FAMILY WEALTH & MOVE-UP WORKSPACE -->
  <main class="max-w-7xl mx-auto px-6 py-6 space-y-6">

    <!-- ZONE 1 & ZONE 2 TOP GRID -->
    <div class="grid lg:grid-cols-12 gap-6 items-stretch">

      <!-- ZONE 1 (5 COLS): UNLOCKED HOME EQUITY VAULT ($262,000) WITH SLIDERS -->
      <section class="lg:col-span-5 wealth-card p-6 flex flex-col justify-between relative overflow-hidden">
        <div style="position:absolute;top:0;left:0;right:0;height:5px;background:linear-gradient(90deg, #15803D, #C82021);"></div>
        <div>
          <div class="flex items-center justify-between mb-2">
            <span class="text-[11px] font-bold uppercase tracking-wider text-[#15803D] mono">Zone 1 • Mr. Cooper Equity Vault</span>
            <span id="equity-sandbox-pill" class="px-2.5 py-0.5 rounded-full text-[10px] font-bold mono bg-emerald-100 text-emerald-900">
              3.250% 1st Lien Protected
            </span>
          </div>
          <h2 class="text-xl font-extrabold display-font text-stone-900">Unlocked Home Equity Vault</h2>
          <p class="text-xs text-stone-500 mt-0.5">Current Home: 1842 Catalpa Dr, Royal Oak, MI 48067</p>

          <!-- Hero Unlocked Equity Figure -->
          <div class="my-5 p-5 rounded-2xl bg-gradient-to-br from-emerald-900 via-[#15803D] to-emerald-800 text-white shadow-lg">
            <div class="flex items-center justify-between text-xs mono text-emerald-200">
              <span>TOTAL UNLOCKED EQUITY</span>
              <span>REDFIN AVM VERIFIED</span>
            </div>
            <div id="vault-equity-total" class="text-3xl md:text-4xl font-extrabold display-font mt-1">$262,000</div>
            <div class="mt-2 pt-2 border-t border-white/20 flex items-center justify-between text-xs mono text-emerald-100">
              <span>Net Sale Proceeds (Redfin 1% Listing):</span>
              <strong id="vault-net-proceeds">$238,400</strong>
            </div>
          </div>

          <!-- Sliders for Current Home Value & Mortgage Balance -->
          <div class="space-y-4 p-4 rounded-2xl bg-stone-50 border border-stone-200/80">
            <div>
              <div class="flex justify-between text-xs font-bold mb-1">
                <span class="text-stone-600">Current Home AVM Value:</span>
                <span id="lbl-home-val" class="mono text-[#15803D]">$472,000</span>
              </div>
              <input id="slider-home-val" type="range" min="380000" max="680000" step="2000" value="472000"
                     oninput="window.updateMoveUpVault()" class="w-full cursor-pointer">
            </div>

            <div>
              <div class="flex justify-between text-xs font-bold mb-1">
                <span class="text-stone-600">Existing 3.25% Mortgage Balance:</span>
                <span id="lbl-mtg-bal" class="mono text-stone-900">$210,000</span>
              </div>
              <input id="slider-mtg-bal" type="range" min="120000" max="340000" step="2000" value="210000"
                     oninput="window.updateMoveUpVault()" class="w-full cursor-pointer">
            </div>
          </div>
        </div>

        <div class="mt-4 pt-3 border-t border-stone-200 flex items-center justify-between text-xs mono text-stone-600">
          <span>Rocket Money Monthly Surplus:</span>
          <strong class="text-[#15803D]">+$3,920/mo Free Cash Flow</strong>
        </div>
      </section>

      <!-- ZONE 2 (7 COLS): REDFIN SAVED 4-BEDROOM HOMES FEED (TROY / BIRMINGHAM MI) -->
      <section class="lg:col-span-7 wealth-card p-6 flex flex-col justify-between">
        <div>
          <div class="flex flex-wrap items-center justify-between gap-2 mb-4">
            <div>
              <span class="text-[11px] font-bold uppercase tracking-wider text-[#C82021] mono">Zone 2 • Live Cross-Brand Intent Signal</span>
              <h2 class="text-xl font-extrabold display-font text-stone-900">Redfin Saved 4-Bedroom Homes Feed (Troy &amp; Birmingham, MI)</h2>
            </div>
            <span class="px-3 py-1 rounded-full text-xs font-bold mono bg-red-50 text-[#C82021] border border-red-200">
              ♥ 3 Saved Family Move-Up Homes
            </span>
          </div>

          <!-- 3 Clickable Property Cards -->
          <div class="grid sm:grid-cols-3 gap-3.5">
            <!-- Property 1: Troy MI (Default Selected) -->
            <div id="prop-card-0" onclick="window.selectRedfinHome(0, 685000, '4120 Squirrel Rd, Troy, MI 48098')"
                 class="redfin-prop-card active p-3.5 flex flex-col justify-between">
              <div>
                <div class="h-28 rounded-xl bg-gradient-to-br from-stone-800 via-red-950 to-stone-900 p-3 flex flex-col justify-between text-white relative overflow-hidden">
                  <span class="px-2 py-0.5 rounded bg-[#C82021] text-[10px] font-bold mono w-fit">REDFIN HOT HOME</span>
                  <div class="font-extrabold display-font text-lg">$685,000</div>
                </div>
                <div class="mt-2.5 font-bold text-xs text-stone-900">4120 Squirrel Rd</div>
                <div class="text-[11px] text-stone-500">Troy, MI 48098 • Troy High School</div>
              </div>
              <div class="mt-2.5 pt-2 border-t border-stone-200 flex justify-between text-[11px] mono font-semibold text-stone-700">
                <span>4 Bd • 3.5 Ba</span>
                <span>3,240 SqFt</span>
              </div>
            </div>

            <!-- Property 2: Birmingham MI -->
            <div id="prop-card-1" onclick="window.selectRedfinHome(1, 750000, '884 Purdy St, Birmingham, MI 48009')"
                 class="redfin-prop-card p-3.5 flex flex-col justify-between">
              <div>
                <div class="h-28 rounded-xl bg-gradient-to-br from-emerald-950 via-stone-800 to-stone-900 p-3 flex flex-col justify-between text-white relative overflow-hidden">
                  <span class="px-2 py-0.5 rounded bg-emerald-700 text-[10px] font-bold mono w-fit">WALK TO DOWNTOWN</span>
                  <div class="font-extrabold display-font text-lg">$750,000</div>
                </div>
                <div class="mt-2.5 font-bold text-xs text-stone-900">884 Purdy St</div>
                <div class="text-[11px] text-stone-500">Birmingham, MI 48009 • Seaholm HS</div>
              </div>
              <div class="mt-2.5 pt-2 border-t border-stone-200 flex justify-between text-[11px] mono font-semibold text-stone-700">
                <span>4 Bd • 4.0 Ba</span>
                <span>3,480 SqFt</span>
              </div>
            </div>

            <!-- Property 3: Northville / Troy Border -->
            <div id="prop-card-2" onclick="window.selectRedfinHome(2, 635000, '2190 Boulan Park Dr, Troy, MI 48084')"
                 class="redfin-prop-card p-3.5 flex flex-col justify-between">
              <div>
                <div class="h-28 rounded-xl bg-gradient-to-br from-amber-950 via-stone-800 to-stone-900 p-3 flex flex-col justify-between text-white relative overflow-hidden">
                  <span class="px-2 py-0.5 rounded bg-amber-600 text-[10px] font-bold mono w-fit">CUL-DE-SAC LOT</span>
                  <div class="font-extrabold display-font text-lg">$635,000</div>
                </div>
                <div class="mt-2.5 font-bold text-xs text-stone-900">2190 Boulan Park Dr</div>
                <div class="text-[11px] text-stone-500">Troy, MI 48084 • Boulan Park MS</div>
              </div>
              <div class="mt-2.5 pt-2 border-t border-stone-200 flex justify-between text-[11px] mono font-semibold text-stone-700">
                <span>4 Bd • 2.5 Ba</span>
                <span>2,980 SqFt</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Selected Target Home Summary Bar -->
        <div class="mt-4 p-4 rounded-2xl bg-stone-100 border border-stone-200 flex flex-wrap items-center justify-between gap-3 text-xs">
          <div>
            <span class="text-stone-500 font-semibold">Selected Target Move-Up Home:</span>
            <strong id="selected-prop-label" class="text-stone-900 ml-1">4120 Squirrel Rd, Troy, MI 48098 ($685,000)</strong>
          </div>
          <span class="px-2.5 py-1 rounded-lg bg-[#C82021]/10 text-[#C82021] font-bold mono">
            Redfin 1% Listing Fee Saves $9,440
          </span>
        </div>
      </section>
    </div>

    <!-- ZONE 3: KEEP 3.25% FIRST LIEN + SECOND LIEN VS. BLENDED MOVE-UP LOAN COMPARISON MATRIX -->
    <section class="wealth-card p-6 md:p-8">
      <div class="flex flex-wrap items-center justify-between gap-3 pb-4 mb-6 border-b border-stone-200">
        <div>
          <span class="text-[11px] font-bold uppercase tracking-wider text-[#15803D] mono">Zone 3 • Solving the "3.25% Rate Lock-In" Paradox</span>
          <h2 class="text-xl md:text-2xl font-extrabold display-font text-stone-900">
            Keep 3.25% First Lien + Second Lien vs. Blended Move-Up Loan Comparison Matrix
          </h2>
        </div>
        <span id="adk-model-status" class="px-3 py-1 rounded-full text-xs font-bold mono bg-stone-100 text-stone-700 border border-stone-300">
          Google ADK Runtime • gemini-3.8-flash
        </span>
      </div>

      <div class="grid md:grid-cols-3 gap-5">
        <!-- Strategy A: Keep 3.25% Royal Oak Home as Cash-Flow Rental + Rocket Closed-End Second Lien -->
        <div class="p-5 rounded-2xl border-2 border-[#15803D] bg-emerald-50/40 flex flex-col justify-between relative">
          <span class="absolute -top-3 left-4 px-3 py-0.5 rounded-full bg-[#15803D] text-white text-[10px] font-bold mono uppercase">
            Strategy A • Keep 3.25% 1st Lien + 2nd Lien
          </span>
          <div>
            <h3 class="text-base font-extrabold display-font text-stone-900 mt-1">
              Retain Royal Oak @ 3.25% as Rental + Rocket Second Lien Bridge
            </h3>
            <p class="text-xs text-stone-600 mt-1 leading-relaxed">
              Never surrender your 3.25% first mortgage! Rent Royal Oak for <strong>$2,680/mo</strong> (generating <strong>+$1,260/mo net rental income</strong> over its $1,420 PITI) and tap <span id="mat-second-lien-amt" class="font-bold mono">$165,000</span> via a Rocket Closed-End Second Lien for the Troy down payment.
            </p>
            <div class="mt-4 space-y-2 text-xs mono border-t border-emerald-200 pt-3">
              <div class="flex justify-between">
                <span class="text-stone-600">1st Lien Kept Untouched:</span>
                <strong class="text-[#15803D]">$210,000 @ 3.250%</strong>
              </div>
              <div class="flex justify-between">
                <span class="text-stone-600">Net Rental Cash-Flow Offset:</span>
                <strong class="text-[#15803D]">+$1,260/mo Surplus</strong>
              </div>
              <div class="flex justify-between">
                <span class="text-stone-600">Effective Net Move-Up Cost:</span>
                <strong id="mat-optA-net-pmt" class="text-stone-900 text-sm">$2,945/mo</strong>
              </div>
            </div>
          </div>
          <div class="mt-4 pt-3 border-t border-emerald-200/80 text-[11px] font-bold text-[#15803D] mono">
            ✓ Preserves Cheap 3.25% Leverage + Dual-Property Appreciation
          </div>
        </div>

        <!-- Strategy B: Sell Royal Oak with Redfin 1% Listing Fee + Blended Move-Up Loan -->
        <div class="p-5 rounded-2xl border-2 border-[#C82021] bg-red-50/30 flex flex-col justify-between relative">
          <span class="absolute -top-3 left-4 px-3 py-0.5 rounded-full bg-[#C82021] text-white text-[10px] font-bold mono uppercase">
            Strategy B • Redfin 1% Sale + Move-Up Loan
          </span>
          <div>
            <h3 class="text-base font-extrabold display-font text-stone-900 mt-1">
              Roll Full <span id="mat-optB-equity">$238,400</span> Net Equity into New Move-Up Mortgage
            </h3>
            <p class="text-xs text-stone-600 mt-1 leading-relaxed">
              List Royal Oak with Redfin at a <strong>1% listing fee</strong> (saving $9,440 vs 3% brokers) plus a <strong>$2,500 Rocket Buy+Borrow closing credit</strong>. Roll 100% of net equity into the new 4-bedroom home to eliminate PMI and minimize the new loan balance.
            </p>
            <div class="mt-4 space-y-2 text-xs mono border-t border-red-200 pt-3">
              <div class="flex justify-between">
                <span class="text-stone-600">New Move-Up Loan Amount:</span>
                <strong id="mat-optB-loan" class="text-stone-900">$446,600 (65% LTV)</strong>
              </div>
              <div class="flex justify-between">
                <span class="text-stone-600">Blended Family Wealth Rate:</span>
                <strong class="text-[#C82021]">5.990% (0% PMI)</strong>
              </div>
              <div class="flex justify-between">
                <span class="text-stone-600">New Monthly P&amp;I Payment:</span>
                <strong id="mat-optB-pi" class="text-stone-900 text-sm">$2,674.72/mo</strong>
              </div>
            </div>
          </div>
          <div class="mt-4 pt-3 border-t border-red-200/80 text-[11px] font-bold text-[#C82021] mono">
            ✓ Lowest Single Monthly Payment • Zero Landlord Duties
          </div>
        </div>

        <!-- Strategy C: ADK Autonomous Wealth Concierge Verdict -->
        <div class="p-5 rounded-2xl bg-stone-900 text-stone-100 flex flex-col justify-between">
          <div>
            <div class="text-[10px] font-bold uppercase tracking-widest text-amber-400 mono">
              ADK Multi-Agent Synthesis Verdict
            </div>
            <h3 class="text-base font-extrabold display-font text-white mt-1">
              Personalized Family Wealth Recommendation
            </h3>
            <p id="adk-wealth-summary" class="text-xs text-stone-300 mt-2 leading-relaxed">
              With <strong>$262,000 in unlocked Royal Oak equity</strong> and <strong>$3,920/mo in Rocket Money free cash flow</strong>, the Miller family comfortably qualifies for both paths on <strong>4120 Squirrel Rd ($685,000)</strong>:
              Strategy B delivers the lowest single payment (<strong>$2,674.72/mo P&amp;I</strong> with $11,940 in combined Redfin 1% + Rocket bundle credits), while Strategy A keeps the 3.25% asset compounding.
            </p>
          </div>
          <div class="mt-4 pt-3 border-t border-stone-700 space-y-2 text-xs mono">
            <div class="flex justify-between text-amber-300">
              <span>Redfin Tour + Bridge Pre-Approval:</span>
              <strong>READY IN 1 TAP</strong>
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>

  <script>
    let selectedTargetPrice = 685000;
    let selectedTargetAddress = '4120 Squirrel Rd, Troy, MI 48098';

    function calcPI(principal, ratePct, months) {{
      if (principal <= 0) return 0;
      const r = (ratePct / 100.0) / 12.0;
      return principal * (r * Math.pow(1 + r, months)) / (Math.pow(1 + r, months) - 1);
    }}

    window.selectRedfinHome = function(idx, price, addr) {{
      selectedTargetPrice = price;
      selectedTargetAddress = addr;
      [0, 1, 2].forEach(i => {{
        const c = document.getElementById('prop-card-' + i);
        if (i === idx) c.classList.add('active');
        else c.classList.remove('active');
      }});
      document.getElementById('selected-prop-label').innerText = `${{addr}} ($${{price.toLocaleString()}})`;
      window.updateMoveUpVault();
    }};

    let vaultTimer = null;
    window.updateMoveUpVault = function() {{
      const homeVal = parseFloat(document.getElementById('slider-home-val').value || 472000);
      const mtgBal = parseFloat(document.getElementById('slider-mtg-bal').value || 210000);
      const rawEquity = Math.max(0, homeVal - mtgBal);
      const netSaleProceeds = Math.max(0, Math.round(homeVal * 0.95 - mtgBal)); // 1% Redfin listing + buyer agent/closing

      document.getElementById('lbl-home-val').innerText = '$' + homeVal.toLocaleString();
      document.getElementById('lbl-mtg-bal').innerText = '$' + mtgBal.toLocaleString();
      document.getElementById('vault-equity-total').innerText = '$' + rawEquity.toLocaleString();
      document.getElementById('vault-net-proceeds').innerText = '$' + netSaleProceeds.toLocaleString();

      // Update Zone 3 Matrix
      const secondLienTap = Math.min(200000, Math.max(80000, Math.round(homeVal * 0.80 - mtgBal)));
      const newLoanB = Math.max(100000, selectedTargetPrice - netSaleProceeds);
      const ltvB = Math.round((newLoanB / selectedTargetPrice) * 100);
      const piB = calcPI(newLoanB, 5.99, 360);
      const netRentalOffsetPmt = Math.round(piB + 270);

      document.getElementById('mat-second-lien-amt').innerText = '$' + secondLienTap.toLocaleString();
      document.getElementById('mat-optA-net-pmt').innerText = '$' + netRentalOffsetPmt.toLocaleString() + '/mo';
      document.getElementById('mat-optB-equity').innerText = '$' + netSaleProceeds.toLocaleString();
      document.getElementById('mat-optB-loan').innerText = `$${{newLoanB.toLocaleString()}} (${{ltvB}}% LTV)`;
      document.getElementById('mat-optB-pi').innerText = '$' + piB.toFixed(2) + '/mo';

      clearTimeout(vaultTimer);
      vaultTimer = setTimeout(async () => {{
        try {{
          const res = await fetch('/api/sandbox', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
              code: '3.5',
              action: 'calc_equity_moveup',
              params: {{
                current_home_val: homeVal,
                current_upb: mtgBal,
                target_purchase: selectedTargetPrice
              }}
            }})
          }});
          const data = await res.json();
          const pill = document.getElementById('equity-sandbox-pill');
          if (pill && data.execution_ms !== undefined) {{
            pill.innerText = `gVisor Verified (${{data.execution_ms}}ms)`;
          }}
        }} catch (e) {{}}
      }}, 180);
    }};

    window.runLiveVertexAI = async function() {{
      const btn = document.getElementById('adk-moveup-btn');
      const sumEl = document.getElementById('adk-wealth-summary');
      const statusEl = document.getElementById('adk-model-status');
      const homeVal = parseFloat(document.getElementById('slider-home-val').value || 472000);
      const mtgBal = parseFloat(document.getElementById('slider-mtg-bal').value || 210000);
      const scenarioInput = document.getElementById('scenario-input') ? document.getElementById('scenario-input').value : '';

      if (btn) btn.innerHTML = `<span class="shrinking-shining-ink"></span> <span>Running ADK Move-Up Matrix...</span>`;
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '3.5',
            model: window.getSelectedModel(),
            user_input: scenarioInput,
            params: {{
              current_home_val: homeVal,
              current_upb: mtgBal,
              target_purchase: selectedTargetPrice
            }}
          }})
        }});
        const data = await res.json();
        const sd = data.structured_data || {{}};
        if (statusEl && data.vertex) {{
          statusEl.innerText = `Google ADK • ${{data.vertex.model_used}} (${{data.vertex.latency_ms}}ms)`;
        }}
        if (sd.recommended_path && sumEl) {{
          sumEl.innerHTML = sd.recommended_path;
        }} else if (sd.executive_summary && sumEl) {{
          sumEl.innerHTML = sd.executive_summary;
        }} else if (data.vertex && data.vertex.response_markdown && sumEl) {{
          sumEl.innerHTML = data.vertex.response_markdown;
        }}
      }} catch (e) {{
        console.error(e);
      }} finally {{
        if (btn) btn.innerHTML = `<span>⚡ Run ADK Move-Up Matrix</span>`;
      }}
    }};

    document.addEventListener('DOMContentLoaded', () => {{
      window.updateMoveUpVault();
    }});
  </script>

  {render_floating_control_bar_and_drawer("3.5", auth_token)}
</body>
</html>"""
