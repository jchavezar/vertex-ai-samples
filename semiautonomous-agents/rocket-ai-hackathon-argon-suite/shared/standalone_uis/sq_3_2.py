# -*- coding: utf-8 -*-
"""Square 3.2: Hardship & Forbearance Empathy Co-Pilot (Google ADK Runtime)
Visual Design: One Medical / Calm Compassionate Homeowner Assistance Center
(#FAF7F2 soft linen background, #2D6A4F sage forest green, #1E293B warm slate ink,
Google Fonts Lora serif headings + Plus Jakarta Sans body)."""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_3_2(auth_token: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Homeowner Hardship &amp; Forbearance Assistance Center | Compassionate Servicing [3.2]</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,500;0,600;0,700;1,500&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {{
      --linen-bg: #FAF7F2;
      --sage-green: #2D6A4F;
      --sage-soft: #ECFDF5;
      --slate-ink: #1E293B;
    }}
    body {{
      background-color: var(--linen-bg);
      color: var(--slate-ink);
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      margin: 0;
    }}
    .serif-calm {{
      font-family: 'Lora', Georgia, serif;
    }}
    .mono {{
      font-family: 'JetBrains Mono', monospace;
    }}
    .calm-card {{
      background: #FFFFFF;
      border-radius: 22px;
      border: 1px solid #E5E0D8;
      box-shadow: 0 12px 30px -10px rgba(45, 106, 79, 0.06), 0 4px 12px -2px rgba(30, 41, 59, 0.04);
    }}
    .reason-pill {{
      border: 1.5px solid #E2DDD5;
      background: #FAF7F2;
      border-radius: 14px;
      transition: all 0.2s ease;
      cursor: pointer;
    }}
    .reason-pill:hover {{
      border-color: #95D5B2;
    }}
    .reason-pill.active {{
      border-color: #2D6A4F;
      background: #ECFDF5;
      box-shadow: 0 4px 12px rgba(45, 106, 79, 0.12);
    }}
    .workout-card {{
      border-radius: 18px;
      border: 2px solid #E5E0D8;
      background: #FFFFFF;
      transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
      cursor: pointer;
    }}
    .workout-card:hover {{
      border-color: #74C69D;
      transform: translateY(-2px);
    }}
    .workout-card.selected {{
      border-color: #2D6A4F;
      background: linear-gradient(180deg, #F0FDF4 0%, #FFFFFF 100%);
      box-shadow: 0 12px 26px -6px rgba(45, 106, 79, 0.16);
    }}
    input[type="range"] {{
      accent-color: #2D6A4F;
    }}
    .shrinking-shining-ink {{
      width: 14px;
      height: 14px;
      border-radius: 50%;
      background: radial-gradient(circle at 30% 30%, #D8F3DC, #2D6A4F, #1B4332);
      animation: calmPulse 1.2s ease-in-out infinite;
      display: inline-block;
    }}
    @keyframes calmPulse {{
      0%, 100% {{ transform: scale(1); opacity: 0.95; }}
      50% {{ transform: scale(0.6); opacity: 0.5; }}
    }}
  </style>
</head>
<body class="min-h-screen pb-28">

  <!-- TOP ONE MEDICAL / CALM COMPASSIONATE HOMEOWNER ASSISTANCE HEADER -->
  <header class="sticky top-0 z-40 bg-[#FAF7F2]/95 backdrop-blur-md border-b border-[#E5E0D8] px-6 py-4">
    <div class="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-3.5">
        <div class="w-11 h-11 rounded-2xl bg-[#2D6A4F] text-white flex items-center justify-center shadow-sm">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
          </svg>
        </div>
        <div>
          <div class="flex flex-wrap items-center gap-2">
            <span class="text-xs font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-[#ECFDF5] text-[#2D6A4F] border border-emerald-200">
              Homeowner Care &amp; Hardship Sanctuary
            </span>
            <span class="text-xs text-slate-500">CFPB Regulation X (§ 1024.41) Protected · Loan #0912-7741-MC</span>
          </div>
          <h1 class="text-xl md:text-2xl font-semibold serif-calm text-[#1E293B] mt-0.5">
            Compassionate Forbearance &amp; Payment Relief Co-Pilot
          </h1>
        </div>
      </div>

      <!-- Right Controls: Model Selector + Hear Empathetic Counselor Voice + Synthesize -->
      <div class="flex flex-wrap items-center gap-2.5">
        <div class="flex items-center gap-2 bg-white border border-[#E5E0D8] rounded-full px-3.5 py-1.5">
          <span class="w-2 h-2 rounded-full bg-[#2D6A4F]"></span>
          <label for="app-model-select" class="text-[11px] font-semibold text-slate-600">Care Model:</label>
          <select id="app-model-select" onchange="window.syncSelectedModel(this.value)"
                  class="bg-transparent text-[#1E293B] text-xs font-bold focus:outline-none cursor-pointer">
            <option value="gemini-4-argon">gemini-4-argon (Frontier Global)</option>
            <option value="gemini-3.8-flash" selected>gemini-3.8-flash (ADK Care Runtime)</option>
          </select>
        </div>

        <button id="btn-empathetic-voice"
                onclick="window.playCounselorVoiceMessage(this)"
                class="inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-bold bg-[#ECFDF5] text-[#2D6A4F] border border-emerald-300 shadow-sm hover:bg-emerald-100 transition cursor-pointer">
          <span>🔊 Hear Empathetic Counselor Voice Message (Gemini 3.8 Live · Aoede HD)</span>
        </button>

        <button id="adk-verify-btn" onclick="window.runLiveVertexAI()"
                class="inline-flex items-center gap-1.5 px-4 py-2 rounded-full text-xs font-bold bg-[#2D6A4F] text-white shadow-sm hover:bg-[#1B4332] transition cursor-pointer">
          <span>🌿 Personalize Relief Plan</span>
        </button>
      </div>
    </div>
  </header>

  <!-- CALM REASSURANCE SANCTUARY BANNER -->
  <div class="max-w-7xl mx-auto px-6 pt-6">
    <div class="calm-card p-6 bg-gradient-to-r from-[#ECFDF5]/90 via-white to-[#FAF7F2] border-l-4 border-l-[#2D6A4F] flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div class="flex items-start gap-4">
        <div class="w-11 h-11 rounded-full bg-[#2D6A4F] text-white flex items-center justify-center shrink-0 text-lg font-bold shadow-sm">
          ♥
        </div>
        <div>
          <div class="text-xs font-bold uppercase tracking-wider text-[#2D6A4F]">
            You Are Safe Here — Your Home Is Protected Under Federal CFPB Regulation X
          </div>
          <p id="counselor-reassurance-banner" class="text-sm md:text-base text-slate-700 mt-1 leading-relaxed">
            Life happens, and a temporary setback should never put your family's home at risk. Under <strong>12 CFR § 1024.41</strong>, foreclosure actions are strictly prohibited while we review your relief options, late fees are <strong>100% waived</strong>, and you will never be asked for a lump-sum balloon payment when your forbearance ends.
          </p>
        </div>
      </div>
      <div class="shrink-0">
        <span id="payoff-sandbox-badge" class="px-3.5 py-1.5 rounded-full text-xs font-semibold bg-[#ECFDF5] text-[#2D6A4F] border border-emerald-200 inline-block">
          120-Day Reg X Shield Active
        </span>
      </div>
    </div>
  </div>

  <!-- MAIN WORKSPACE: LEFT HARDSHIP & CASH-FLOW STUDIO (5 COLS) + RIGHT CFPB REG X WORKOUT WATERFALL (7 COLS) -->
  <main class="max-w-7xl mx-auto px-6 py-6 grid lg:grid-cols-12 gap-6 items-start">

    <!-- LEFT 5 COLUMNS: HARDSHIP REASON SELECTOR + CASH-FLOW RECOVERY SLIDERS + COUNSELOR NOTE -->
    <aside class="lg:col-span-5 space-y-6">

      <!-- 1. HARDSHIP REASON SELECTOR -->
      <section class="calm-card p-6">
        <span class="text-xs font-bold uppercase tracking-wider text-[#2D6A4F]">Step 1 · Tell Us What Happened</span>
        <h2 class="text-lg font-bold serif-calm text-[#1E293B] mt-0.5">Select Your Household Hardship Situation</h2>
        <p class="text-xs text-slate-500 mt-1 mb-4">We tailor your CFPB Regulation X workout options without requiring complex paperwork upfront.</p>

        <div class="space-y-2.5">
          <div id="reason-1" onclick="window.selectHardshipReason('Temporary Medical Leave', 1)" class="reason-pill active p-3.5 flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-full bg-[#2D6A4F] text-white flex items-center justify-center text-xs font-bold">1</div>
              <div>
                <div class="text-sm font-bold text-[#1E293B]">Temporary Medical Leave</div>
                <div class="text-xs text-slate-500">Short-term surgery recovery or family medical care (2–3 mos)</div>
              </div>
            </div>
            <span class="text-xs font-bold text-[#2D6A4F]">Selected ✓</span>
          </div>

          <div id="reason-2" onclick="window.selectHardshipReason('Spouse Job Transition', 2)" class="reason-pill p-3.5 flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-full bg-stone-200 text-slate-700 flex items-center justify-center text-xs font-bold">2</div>
              <div>
                <div class="text-sm font-bold text-[#1E293B]">Spouse Job Transition</div>
                <div class="text-xs text-slate-500">Temporary layoff, plant retooling, or career transition</div>
              </div>
            </div>
            <span class="text-xs font-semibold text-slate-400">Select</span>
          </div>

          <div id="reason-3" onclick="window.selectHardshipReason('Natural Disaster Recovery', 3)" class="reason-pill p-3.5 flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-full bg-stone-200 text-slate-700 flex items-center justify-center text-xs font-bold">3</div>
              <div>
                <div class="text-sm font-bold text-[#1E293B]">Natural Disaster Recovery</div>
                <div class="text-xs text-slate-500">FEMA-declared severe storm, flood, or home repair pause</div>
              </div>
            </div>
            <span class="text-xs font-semibold text-slate-400">Select</span>
          </div>
        </div>
      </section>

      <!-- 2. CASH-FLOW RECOVERY SLIDERS -->
      <section class="calm-card p-6 space-y-4">
        <div>
          <span class="text-xs font-bold uppercase tracking-wider text-[#2D6A4F]">Step 2 · Gentle Cash-Flow Planner</span>
          <h2 class="text-lg font-bold serif-calm text-[#1E293B] mt-0.5">Your Monthly Recovery Comfort Sliders</h2>
        </div>

        <div class="space-y-4 pt-1">
          <div>
            <div class="flex justify-between text-xs font-semibold mb-1">
              <span class="text-slate-600">Current Monthly Mortgage (PITI):</span>
              <strong id="lbl-cur-piti" class="mono text-[#1E293B]">$2,180.00/mo</strong>
            </div>
            <input id="slider-cur-piti" type="range" min="1400" max="3800" step="20" value="2180"
                   oninput="window.updateHardshipControls()" class="w-full cursor-pointer">
          </div>

          <div>
            <div class="flex justify-between text-xs font-semibold mb-1">
              <span class="text-slate-600">Current Monthly Household Income:</span>
              <strong id="lbl-house-income" class="mono text-[#2D6A4F]">$5,800.00/mo</strong>
            </div>
            <input id="slider-house-income" type="range" min="3200" max="10000" step="100" value="5800"
                   oninput="window.updateHardshipControls()" class="w-full cursor-pointer">
          </div>

          <div>
            <div class="flex justify-between text-xs font-semibold mb-1">
              <span class="text-slate-600">Months of Breathing Room Needed:</span>
              <strong id="lbl-relief-months" class="mono text-[#2D6A4F]">3 Months</strong>
            </div>
            <input id="slider-relief-months" type="range" min="1" max="6" step="1" value="3"
                   oninput="window.updateHardshipControls()" class="w-full cursor-pointer">
          </div>
        </div>

        <!-- Dedicated Single Point of Contact (SPOC) Counselor Card -->
        <div class="p-4 rounded-2xl bg-[#FAF7F2] border border-[#E5E0D8] space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-bold uppercase text-[#2D6A4F]">Dedicated Care Counselor (12 CFR § 1024.40)</span>
            <span class="text-[11px] mono text-slate-500">SPOC #MC-CARE-409</span>
          </div>
          <p id="adk-verdict-text" class="text-xs text-slate-700 leading-relaxed italic">
            "Please take a deep breath—your home is completely safe. For your <strong>Temporary Medical Leave</strong>, we can pause your next <strong>3 monthly payments ($6,540.00)</strong> and place them at the very end of your mortgage at <strong>0% interest</strong> so you have zero catch-up shock when you recover."
          </p>
        </div>
      </section>
    </aside>

    <!-- RIGHT 7 COLUMNS: INTERACTIVE CFPB REG X WORKOUT WATERFALL CARDS + RESOLUTION SUMMARY -->
    <section class="lg:col-span-7 space-y-6">

      <!-- 3 INTERACTIVE CFPB REGULATION X WORKOUT WATERFALL CARDS -->
      <div class="calm-card p-6">
        <div class="flex flex-wrap items-center justify-between gap-2 pb-4 mb-5 border-b border-stone-200/80">
          <div>
            <span class="text-xs font-bold uppercase tracking-wider text-[#2D6A4F]">Step 3 · CFPB Regulation X (§ 1024.41) Workout Waterfall</span>
            <h2 class="text-lg md:text-xl font-bold serif-calm text-[#1E293B] mt-0.5">
              Choose the Relief Path That Gives Your Family Peace of Mind
            </h2>
          </div>
          <span class="px-3 py-1 rounded-full text-xs font-semibold bg-[#ECFDF5] text-[#2D6A4F] border border-emerald-200">
            $0 Late Fees · No Credit Penalty
          </span>
        </div>

        <div class="space-y-4">
          <!-- Card 1: 3-Month Forbearance + Payment Deferral -->
          <div id="workout-card-1" onclick="window.selectWorkoutPlan(1)" class="workout-card selected p-5">
            <div class="flex flex-wrap items-start justify-between gap-2">
              <div class="flex items-center gap-3">
                <div id="workout-radio-1" class="w-6 h-6 rounded-full bg-[#2D6A4F] text-white flex items-center justify-center text-xs font-bold">✓</div>
                <div>
                  <div class="flex items-center gap-2">
                    <span class="text-base font-bold serif-calm text-[#1E293B]" id="wk1-title">1. 3-Month Forbearance + Payment Deferral</span>
                    <span class="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-[#ECFDF5] text-[#2D6A4F] border border-emerald-200">Recommended Sanctuary Path</span>
                  </div>
                  <p class="text-xs text-slate-600 mt-1">
                    Pause your mortgage payments during recovery, then move the paused amount (<strong id="wk1-defer-sum" class="mono text-[#2D6A4F]">$6,540.00</strong>) to a non-interest-bearing balance at the end of your loan term.
                  </p>
                </div>
              </div>
            </div>
            <div class="mt-4 pt-3 border-t border-stone-100 grid sm:grid-cols-3 gap-3 text-xs">
              <div class="p-2.5 rounded-xl bg-[#FAF7F2]">
                <div class="text-[10px] uppercase text-slate-500 font-bold">During Relief Period</div>
                <div class="text-sm font-bold text-[#2D6A4F] mono mt-0.5">$0.00 / month</div>
              </div>
              <div class="p-2.5 rounded-xl bg-[#FAF7F2]">
                <div class="text-[10px] uppercase text-slate-500 font-bold">Deferred at 0% Interest</div>
                <div id="wk1-box-deferred" class="text-sm font-bold text-[#1E293B] mono mt-0.5">$6,540.00 (At Maturity)</div>
              </div>
              <div class="p-2.5 rounded-xl bg-[#FAF7F2]">
                <div class="text-[10px] uppercase text-slate-500 font-bold">Resumed Monthly Payment</div>
                <div id="wk1-box-resumed" class="text-sm font-bold text-[#2D6A4F] mono mt-0.5">$2,180.00/mo (No Shock)</div>
              </div>
            </div>
          </div>

          <!-- Card 2: Flex Modification Rate Drop -->
          <div id="workout-card-2" onclick="window.selectWorkoutPlan(2)" class="workout-card p-5">
            <div class="flex flex-wrap items-start justify-between gap-2">
              <div class="flex items-center gap-3">
                <div id="workout-radio-2" class="w-6 h-6 rounded-full border-2 border-stone-300 flex items-center justify-center text-xs font-bold"></div>
                <div>
                  <div class="flex items-center gap-2">
                    <span class="text-base font-bold serif-calm text-[#1E293B]">2. Flex Modification Rate Drop</span>
                    <span class="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-stone-100 text-slate-700">Permanent Monthly Savings (-22%)</span>
                  </div>
                  <p class="text-xs text-slate-600 mt-1">
                    If your household income has permanently changed, we modify your rate down to <strong>4.625%</strong> and extend the term to permanently lower your monthly payment by <strong id="wk2-save-amt" class="mono text-[#2D6A4F]">$479.60/month</strong>.
                  </p>
                </div>
              </div>
            </div>
            <div class="mt-4 pt-3 border-t border-stone-100 grid sm:grid-cols-3 gap-3 text-xs">
              <div class="p-2.5 rounded-xl bg-[#FAF7F2]">
                <div class="text-[10px] uppercase text-slate-500 font-bold">Previous Monthly Payment</div>
                <div id="wk2-box-old" class="text-sm font-bold text-slate-500 line-through mono mt-0.5">$2,180.00/mo</div>
              </div>
              <div class="p-2.5 rounded-xl bg-[#FAF7F2]">
                <div class="text-[10px] uppercase text-slate-500 font-bold">New Modified Payment</div>
                <div id="wk2-box-new" class="text-sm font-bold text-[#2D6A4F] mono mt-0.5">$1,700.40/mo</div>
              </div>
              <div class="p-2.5 rounded-xl bg-[#FAF7F2]">
                <div class="text-[10px] uppercase text-slate-500 font-bold">Monthly Budget Relief</div>
                <div id="wk2-box-sav" class="text-sm font-bold text-[#2D6A4F] mono mt-0.5">Saves $479.60/mo</div>
              </div>
            </div>
          </div>

          <!-- Card 3: Repayment Plan -->
          <div id="workout-card-3" onclick="window.selectWorkoutPlan(3)" class="workout-card p-5">
            <div class="flex flex-wrap items-start justify-between gap-2">
              <div class="flex items-center gap-3">
                <div id="workout-radio-3" class="w-6 h-6 rounded-full border-2 border-stone-300 flex items-center justify-center text-xs font-bold"></div>
                <div>
                  <div class="flex items-center gap-2">
                    <span class="text-base font-bold serif-calm text-[#1E293B]">3. Repayment Plan (12-Month Gradual Catch-Up)</span>
                    <span class="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-stone-100 text-slate-700">For Restored Overtime / Bonus Income</span>
                  </div>
                  <p class="text-xs text-slate-600 mt-1">
                    Spread the paused payments evenly across 12 months at 0% interest once your household income is back above pre-hardship levels.
                  </p>
                </div>
              </div>
            </div>
            <div class="mt-4 pt-3 border-t border-stone-100 grid sm:grid-cols-3 gap-3 text-xs">
              <div class="p-2.5 rounded-xl bg-[#FAF7F2]">
                <div class="text-[10px] uppercase text-slate-500 font-bold">Base Monthly Payment</div>
                <div id="wk3-box-base" class="text-sm font-bold text-[#1E293B] mono mt-0.5">$2,180.00/mo</div>
              </div>
              <div class="p-2.5 rounded-xl bg-[#FAF7F2]">
                <div class="text-[10px] uppercase text-slate-500 font-bold">12-Mo Catch-Up Portion</div>
                <div id="wk3-box-add" class="text-sm font-bold text-slate-700 mono mt-0.5">+$545.00/mo</div>
              </div>
              <div class="p-2.5 rounded-xl bg-[#FAF7F2]">
                <div class="text-[10px] uppercase text-slate-500 font-bold">Total Temporary Payment</div>
                <div id="wk3-box-tot" class="text-sm font-bold text-[#1E293B] mono mt-0.5">$2,725.00/mo</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- HOMEOWNER PEACE-OF-MIND PROTECTION SUMMARY & ENROLLMENT -->
      <div class="calm-card p-6 bg-gradient-to-b from-white to-[#ECFDF5]/60">
        <div class="flex flex-wrap items-center justify-between gap-2 pb-3 mb-4 border-b border-stone-200">
          <div>
            <div class="text-[11px] font-bold uppercase tracking-wider text-[#2D6A4F]">Your Written Relief Guarantee</div>
            <h3 class="text-base font-bold serif-calm text-[#1E293B]" id="summary-plan-heading">
              Selected Plan: 3-Month Forbearance + Payment Deferral
            </h3>
          </div>
          <span class="px-3 py-1 rounded-full text-xs font-bold bg-[#2D6A4F] text-white" id="summary-dti-badge">
            Post-Relief Housing Ratio: 37.6%
          </span>
        </div>

        <div class="grid sm:grid-cols-2 gap-4 text-xs text-slate-700 mb-5">
          <div class="p-3.5 rounded-xl bg-white border border-stone-200">
            <div class="font-bold text-[#2D6A4F] mb-1">✓ Zero Balloon Payment Guarantee</div>
            <div id="summary-left-copy">Your paused payments ($6,540.00) are placed into a 0% interest balance due only when you sell, refinance, or reach the end of your mortgage.</div>
          </div>
          <div class="p-3.5 rounded-xl bg-white border border-stone-200">
            <div class="font-bold text-[#2D6A4F] mb-1">✓ CFPB Reg X &amp; Credit Protection</div>
            <div>100% late-fee waiver and CARES/FCRA credit reporting protection while you focus on your family's recovery.</div>
          </div>
        </div>

        <button onclick="window.activateReliefPlan()"
                class="w-full py-3.5 px-4 rounded-xl font-bold text-sm text-white bg-[#2D6A4F] hover:bg-[#1B4332] shadow-md transition cursor-pointer flex items-center justify-center gap-2">
          <span>🌿 Confirm &amp; Activate My Homeowner Relief Plan</span>
        </button>

        <div id="relief-confirmation-toast" class="hidden mt-3 p-3.5 rounded-xl bg-[#ECFDF5] border border-emerald-300 text-[#2D6A4F] text-xs font-semibold text-center"></div>
      </div>
    </section>
  </main>

  <script>
    let currentHardshipReason = 'Temporary Medical Leave';
    let selectedWorkout = 1;

    function fmtMoney(n) {{
      return '$' + Number(n).toLocaleString('en-US', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
    }}

    window.playCounselorVoiceMessage = function(btnEl) {{
      const piti = parseFloat(document.getElementById('slider-cur-piti').value || 2180);
      const mos = parseInt(document.getElementById('slider-relief-months').value || 3, 10);
      const deferred = (piti * mos).toLocaleString('en-US', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
      const modPiti = (piti * 0.78).toLocaleString('en-US', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
      const msg = `Hello, this is Sarah from the Mr. Cooper and Rocket Homeowner Care team. First, please take a deep breath—your home is completely safe and protected under federal CFPB Regulation X rules. Because your family is navigating ${{currentHardshipReason}}, we can immediately pause your next ${{mos}} monthly payments totaling ${{deferred}} dollars, waive every late fee, and defer that balance to the very end of your mortgage at zero percent interest so there is never a lump sum due. Or, if you need a permanent lower payment, our Flex Modification Rate Drop reduces your monthly payment down to ${{modPiti}} dollars a month. We are right here with you every step of the way.`;
      window.playLiveCallClip(msg, 'Aoede', 'Compassionate Homeowner Care Counselor', btnEl);
    }};

    window.selectHardshipReason = function(reasonName, idx) {{
      currentHardshipReason = reasonName;
      [1, 2, 3].forEach(i => {{
        const el = document.getElementById('reason-' + i);
        if (!el) return;
        const badge = el.querySelector('span:last-child');
        const circle = el.querySelector('div > div:first-child');
        if (i === idx) {{
          el.classList.add('active');
          if (badge) {{ badge.innerText = 'Selected ✓'; badge.className = 'text-xs font-bold text-[#2D6A4F]'; }}
          if (circle) {{ circle.className = 'w-8 h-8 rounded-full bg-[#2D6A4F] text-white flex items-center justify-center text-xs font-bold'; }}
        }} else {{
          el.classList.remove('active');
          if (badge) {{ badge.innerText = 'Select'; badge.className = 'text-xs font-semibold text-slate-400'; }}
          if (circle) {{ circle.className = 'w-8 h-8 rounded-full bg-stone-200 text-slate-700 flex items-center justify-center text-xs font-bold'; }}
        }}
      }});
      window.updateHardshipControls();
    }};

    window.selectWorkoutPlan = function(planIdx) {{
      selectedWorkout = planIdx;
      [1, 2, 3].forEach(i => {{
        const card = document.getElementById('workout-card-' + i);
        const radio = document.getElementById('workout-radio-' + i);
        if (i === planIdx) {{
          card.classList.add('selected');
          radio.className = 'w-6 h-6 rounded-full bg-[#2D6A4F] text-white flex items-center justify-center text-xs font-bold';
          radio.innerText = '✓';
        }} else {{
          card.classList.remove('selected');
          radio.className = 'w-6 h-6 rounded-full border-2 border-stone-300 flex items-center justify-center text-xs font-bold';
          radio.innerText = '';
        }}
      }});
      window.updateHardshipControls();
    }};

    let calcTimer = null;
    window.updateHardshipControls = function() {{
      const piti = parseFloat(document.getElementById('slider-cur-piti').value || 2180);
      const income = parseFloat(document.getElementById('slider-house-income').value || 5800);
      const mos = parseInt(document.getElementById('slider-relief-months').value || 3, 10);

      const deferredSum = piti * mos;
      const modNewPiti = Math.round(piti * 0.78 * 100) / 100;
      const modSave = piti - modNewPiti;
      const repayAdd = deferredSum / 12.0;
      const repayTot = piti + repayAdd;

      document.getElementById('lbl-cur-piti').innerText = fmtMoney(piti) + '/mo';
      document.getElementById('lbl-house-income').innerText = fmtMoney(income) + '/mo';
      document.getElementById('lbl-relief-months').innerText = mos + (mos === 1 ? ' Month' : ' Months');

      document.getElementById('wk1-title').innerText = `1. ${{mos}}-Month Forbearance + Payment Deferral`;
      document.getElementById('wk1-defer-sum').innerText = fmtMoney(deferredSum);
      document.getElementById('wk1-box-deferred').innerText = fmtMoney(deferredSum) + ' (At Maturity)';
      document.getElementById('wk1-box-resumed').innerText = fmtMoney(piti) + '/mo (No Shock)';

      document.getElementById('wk2-save-amt').innerText = fmtMoney(modSave) + '/month';
      document.getElementById('wk2-box-old').innerText = fmtMoney(piti) + '/mo';
      document.getElementById('wk2-box-new').innerText = fmtMoney(modNewPiti) + '/mo';
      document.getElementById('wk2-box-sav').innerText = 'Saves ' + fmtMoney(modSave) + '/mo';

      document.getElementById('wk3-box-base').innerText = fmtMoney(piti) + '/mo';
      document.getElementById('wk3-box-add').innerText = '+' + fmtMoney(repayAdd) + '/mo';
      document.getElementById('wk3-box-tot').innerText = fmtMoney(repayTot) + '/mo';

      const verdictEl = document.getElementById('adk-verdict-text');
      if (verdictEl) {{
        verdictEl.innerHTML = `"Please take a deep breath—your home is completely safe. For your <strong>${{currentHardshipReason}}</strong>, we can pause your next <strong>${{mos}} monthly payments (${{fmtMoney(deferredSum)}})</strong> and place them at the very end of your mortgage at <strong>0% interest</strong> so you have zero catch-up shock when you recover."`;
      }}

      const headingEl = document.getElementById('summary-plan-heading');
      const dtiEl = document.getElementById('summary-dti-badge');
      const copyEl = document.getElementById('summary-left-copy');

      if (selectedWorkout === 1) {{
        headingEl.innerText = `Selected Plan: ${{mos}}-Month Forbearance + Payment Deferral`;
        dtiEl.innerText = `Resumed Housing Ratio: ${{((piti / income) * 100).toFixed(1)}}%`;
        copyEl.innerText = `Your paused payments (${{fmtMoney(deferredSum)}}) are placed into a 0% interest balance due only when you sell, refinance, or reach the end of your mortgage.`;
      }} else if (selectedWorkout === 2) {{
        headingEl.innerText = `Selected Plan: Flex Modification Rate Drop (${{fmtMoney(modNewPiti)}}/mo)`;
        dtiEl.innerText = `Modified Housing Ratio: ${{((modNewPiti / income) * 100).toFixed(1)}}%`;
        copyEl.innerText = `Your monthly payment permanently drops from ${{fmtMoney(piti)}}/mo to ${{fmtMoney(modNewPiti)}}/mo (saving ${{fmtMoney(modSave)}} every month).`;
      }} else {{
        headingEl.innerText = `Selected Plan: 12-Month Gradual Repayment Plan`;
        dtiEl.innerText = `Repayment Housing Ratio: ${{((repayTot / income) * 100).toFixed(1)}}%`;
        copyEl.innerText = `Your paused balance (${{fmtMoney(deferredSum)}}) is spread across 12 monthly installments of +${{fmtMoney(repayAdd)}}/mo at 0% interest.`;
      }}

      clearTimeout(calcTimer);
      calcTimer = setTimeout(async () => {{
        try {{
          const res = await fetch('/api/sandbox', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
              code: '3.2',
              action: 'eval_loss_mitigation',
              params: {{
                piti: piti,
                delinquent_months: mos
              }}
            }})
          }});
          const data = await res.json();
          const badge = document.getElementById('payoff-sandbox-badge');
          if (badge && data.execution_ms !== undefined) {{
            badge.innerText = `Reg X Shield Verified (${{data.execution_ms}}ms)`;
          }}
        }} catch (e) {{}}
      }}, 180);
    }};

    window.activateReliefPlan = function() {{
      const toast = document.getElementById('relief-confirmation-toast');
      const heading = document.getElementById('summary-plan-heading').innerText;
      toast.classList.remove('hidden');
      toast.innerHTML = `🌿 Confirmed! <strong>${{heading}}</strong> is now active for your account (${{currentHardshipReason}}). All late fees are waived and CFPB Regulation X protection is locked in. Reference #CARE-2026-4109.`;
    }};

    window.runLiveVertexAI = async function() {{
      const btn = document.getElementById('adk-verify-btn');
      const verdict = document.getElementById('adk-verdict-text');
      const banner = document.getElementById('counselor-reassurance-banner');
      const piti = parseFloat(document.getElementById('slider-cur-piti').value || 2180);
      const mos = parseInt(document.getElementById('slider-relief-months').value || 3, 10);
      const scenarioInput = document.getElementById('scenario-input') ? document.getElementById('scenario-input').value : '';

      if (btn) btn.innerHTML = `<span class="shrinking-shining-ink"></span> <span>Personalizing...</span>`;
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '3.2',
            model: window.getSelectedModel(),
            user_input: scenarioInput || `Homeowner experiencing ${{currentHardshipReason}} requesting ${{mos}}-month relief on ${{piti}}/mo PITI.`,
            params: {{
              piti: piti,
              delinquent_months: mos,
              hardship_reason: currentHardshipReason
            }}
          }})
        }});
        const data = await res.json();
        const sd = data.structured_data || {{}};
        if (sd.executive_summary && verdict) {{
          verdict.innerHTML = `<strong>[${{data.vertex ? data.vertex.model_used : window.getSelectedModel()}} Counselor Guidance]:</strong> ` + sd.executive_summary;
        }} else if (data.vertex && data.vertex.response_markdown && verdict) {{
          verdict.innerHTML = data.vertex.response_markdown;
        }}
        if (sd.empathetic_headline && banner) {{
          banner.innerHTML = sd.empathetic_headline;
        }}
      }} catch (e) {{
        console.error(e);
      }} finally {{
        if (btn) btn.innerHTML = `<span>🌿 Personalize Relief Plan</span>`;
      }}
    }};

    document.addEventListener('DOMContentLoaded', () => {{
      window.updateHardshipControls();
    }});
  </script>

  {render_floating_control_bar_and_drawer("3.2", auth_token)}
</body>
</html>"""
