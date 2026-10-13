# -*- coding: utf-8 -*-
"""Square 4.2 — Rocket Money 'Home-Ready' Coach (Consumer Personal Finance & Savings Vault App).
Visual Design: Authentic Rocket Money / Monarch Consumer Personal Finance & Down Payment Vault App.
Palette: #F7F6F2 soft alabaster/cream background, #E11D48 Rocket Money crimson, #0D9488 savings teal, #FFFFFF rounded 16px cards.
Typography: Google Fonts 'Outfit' + 'Plus Jakarta Sans'.
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_4_2(auth_token: str) -> str:
    floating_drawer = render_floating_control_bar_and_drawer("4.2", auth_token)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Rocket Money Home-Ready Coach | Down Payment Vault & Subscription Audit</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --alabaster: #F7F6F2;
      --card-white: #FFFFFF;
      --rm-crimson: #E11D48;
      --rm-crimson-dark: #BE123C;
      --rm-crimson-soft: #FFF1F2;
      --savings-teal: #0D9488;
      --savings-teal-dark: #0F766E;
      --savings-teal-soft: #F0FDFA;
      --ink-dark: #18181B;
      --ink-body: #27272A;
      --ink-muted: #52525B;
      --ink-subtle: #71717A;
      --border-soft: #E5E4DF;
      --amber-badge: #D97706;
      --amber-bg: #FEF3C7;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: var(--alabaster);
      color: var(--ink-body);
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      min-height: 100vh;
      overflow-x: hidden;
      padding-bottom: 96px;
      line-height: 1.5;
    }}
    h1, h2, h3, .display-font {{
      font-family: 'Outfit', sans-serif;
    }}

    /* Top Rocket Money Consumer App Header */
    .rm-topbar {{
      background: var(--card-white);
      border-bottom: 1px solid var(--border-soft);
      position: sticky;
      top: 0;
      z-index: 100;
      box-shadow: 0 2px 12px rgba(24, 24, 27, 0.03);
    }}
    .rm-topbar-inner {{
      max-width: 1360px;
      margin: 0 auto;
      padding: 13px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      flex-wrap: wrap;
    }}
    .rm-brand {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .rm-logo-badge {{
      background: var(--rm-crimson);
      color: #FFFFFF;
      font-family: 'Outfit', sans-serif;
      font-weight: 800;
      font-size: 16px;
      padding: 7px 13px;
      border-radius: 11px;
      display: inline-flex;
      align-items: center;
      gap: 7px;
      letter-spacing: -0.02em;
    }}
    .rm-nav-pills {{
      display: flex;
      align-items: center;
      gap: 6px;
      background: var(--alabaster);
      padding: 4px;
      border-radius: 10px;
      border: 1px solid var(--border-soft);
    }}
    .rm-nav-pill {{
      font-size: 12.5px;
      font-weight: 700;
      padding: 6px 12px;
      border-radius: 8px;
      color: var(--ink-muted);
    }}
    .rm-nav-pill.active {{
      background: var(--card-white);
      color: var(--ink-dark);
      box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }}
    .rm-header-controls {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .model-picker-pill {{
      display: flex;
      align-items: center;
      gap: 6px;
      background: var(--alabaster);
      border: 1px solid var(--border-soft);
      padding: 6px 12px;
      border-radius: 10px;
      font-size: 12px;
      font-weight: 600;
    }}
    #app-model-select {{
      border: none;
      background: transparent;
      font-family: inherit;
      font-size: 12px;
      font-weight: 700;
      color: var(--rm-crimson);
      outline: none;
      cursor: pointer;
    }}
    .btn-crimson {{
      background: var(--rm-crimson);
      color: #FFFFFF;
      border: none;
      border-radius: 11px;
      padding: 9px 16px;
      font-family: inherit;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 7px;
      transition: background 0.15s ease;
    }}
    .btn-crimson:hover {{
      background: var(--rm-crimson-dark);
    }}
    .btn-teal {{
      background: var(--savings-teal);
      color: #FFFFFF;
      border: none;
      border-radius: 11px;
      padding: 9px 16px;
      font-family: inherit;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 7px;
      transition: background 0.15s ease;
    }}
    .btn-teal:hover {{
      background: var(--savings-teal-dark);
    }}

    /* Main Content Container */
    .app-container {{
      max-width: 1360px;
      margin: 0 auto;
      padding: 24px;
    }}

    /* Top Consumer KPI Summary Strip */
    .kpi-strip {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      margin-bottom: 22px;
    }}
    @media (max-width: 980px) {{
      .kpi-strip {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    .kpi-card {{
      background: var(--card-white);
      border: 1px solid var(--border-soft);
      border-radius: 16px;
      padding: 18px 20px;
      box-shadow: 0 4px 14px rgba(24, 24, 27, 0.03);
    }}
    .kpi-label {{
      font-size: 12px;
      font-weight: 700;
      color: var(--ink-muted);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .kpi-value {{
      font-family: 'Outfit', sans-serif;
      font-size: 28px;
      font-weight: 800;
      color: var(--ink-dark);
      margin-top: 6px;
      letter-spacing: -0.02em;
    }}
    .kpi-value.teal {{ color: var(--savings-teal); }}
    .kpi-value.crimson {{ color: var(--rm-crimson); }}
    .kpi-sub {{
      font-size: 12px;
      color: var(--ink-subtle);
      margin-top: 4px;
      font-weight: 500;
    }}

    /* Two-Column Consumer Finance Layout */
    .coach-grid {{
      display: grid;
      grid-template-columns: 1.05fr 1.25fr;
      gap: 22px;
      align-items: start;
    }}
    @media (max-width: 1040px) {{
      .coach-grid {{ grid-template-columns: 1fr; }}
    }}

    .finance-card {{
      background: var(--card-white);
      border: 1px solid var(--border-soft);
      border-radius: 16px;
      padding: 22px;
      box-shadow: 0 4px 16px rgba(24, 24, 27, 0.03);
      margin-bottom: 20px;
    }}
    .card-header {{
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 16px;
      flex-wrap: wrap;
    }}
    .card-title {{
      font-size: 18px;
      font-weight: 800;
      color: var(--ink-dark);
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .card-subtitle {{
      font-size: 12.5px;
      color: var(--ink-muted);
      margin-top: 3px;
    }}
    .badge-freed {{
      background: var(--savings-teal-soft);
      color: var(--savings-teal-dark);
      border: 1px solid #99F6E4;
      font-size: 12px;
      font-weight: 800;
      padding: 5px 11px;
      border-radius: 999px;
      white-space: nowrap;
    }}

    /* Interactive Subscription Audit Checklist */
    .sub-list {{
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}
    .sub-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 13px 15px;
      border-radius: 12px;
      border: 1px solid var(--border-soft);
      background: #FCFCFA;
      transition: all 0.15s ease;
      cursor: pointer;
    }}
    .sub-row.cancelled {{
      background: var(--savings-teal-soft);
      border-color: #99F6E4;
    }}
    .sub-left {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .sub-icon {{
      width: 38px;
      height: 38px;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 13px;
      background: var(--rm-crimson-soft);
      color: var(--rm-crimson);
      border: 1px solid #FECDD3;
      flex-shrink: 0;
    }}
    .sub-row.cancelled .sub-icon {{
      background: #CCFBF1;
      color: var(--savings-teal-dark);
      border-color: #5EEAD4;
    }}
    .sub-name {{
      font-size: 14px;
      font-weight: 700;
      color: var(--ink-dark);
    }}
    .sub-reason {{
      font-size: 11.5px;
      color: var(--ink-muted);
      margin-top: 1px;
    }}
    .sub-right {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}
    .sub-amount {{
      font-family: 'Outfit', sans-serif;
      font-size: 15px;
      font-weight: 800;
      color: var(--ink-dark);
    }}
    .sub-row.cancelled .sub-amount {{
      color: var(--savings-teal-dark);
    }}

    /* Toggle Switch */
    .toggle-switch {{
      width: 44px;
      height: 24px;
      border-radius: 999px;
      background: #D4D4D8;
      position: relative;
      transition: background 0.2s ease;
      flex-shrink: 0;
    }}
    .sub-row.cancelled .toggle-switch {{
      background: var(--savings-teal);
    }}
    .toggle-knob {{
      width: 18px;
      height: 18px;
      border-radius: 50%;
      background: #FFFFFF;
      position: absolute;
      top: 3px;
      left: 3px;
      transition: transform 0.2s ease;
      box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }}
    .sub-row.cancelled .toggle-knob {{
      transform: translateX(20px);
    }}

    /* Sliders Section */
    .vault-sliders {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 16px;
      background: var(--alabaster);
      border: 1px solid var(--border-soft);
      border-radius: 14px;
      padding: 16px;
      margin-bottom: 18px;
    }}
    @media (max-width: 680px) {{
      .vault-sliders {{ grid-template-columns: 1fr; }}
    }}
    .slider-field label {{
      display: flex;
      justify-content: space-between;
      font-size: 12px;
      font-weight: 700;
      color: var(--ink-muted);
      margin-bottom: 7px;
    }}
    .slider-field input[type="range"] {{
      width: 100%;
      accent-color: var(--savings-teal);
      cursor: pointer;
    }}

    /* Month-by-Month Down Payment Goal Progress Bar */
    .timeline-banner {{
      background: linear-gradient(135deg, #FFF1F2 0%, #F0FDFA 100%);
      border: 1px solid #CBD5E1;
      border-radius: 14px;
      padding: 16px 18px;
      margin-bottom: 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 12px;
    }}
    .timeline-shift {{
      display: flex;
      align-items: center;
      gap: 10px;
      font-family: 'Outfit', sans-serif;
      font-size: 22px;
      font-weight: 800;
    }}
    .old-months {{
      color: var(--ink-subtle);
      text-decoration: line-through;
      font-weight: 700;
    }}
    .new-months {{
      color: var(--savings-teal-dark);
      background: #CCFBF1;
      padding: 3px 11px;
      border-radius: 10px;
    }}

    .goal-progress-wrap {{
      margin-bottom: 18px;
    }}
    .goal-progress-top {{
      display: flex;
      justify-content: space-between;
      font-size: 13px;
      font-weight: 700;
      margin-bottom: 8px;
    }}
    .goal-bar-outer {{
      width: 100%;
      height: 18px;
      background: #E4E4E7;
      border-radius: 999px;
      overflow: hidden;
      display: flex;
    }}
    .goal-bar-saved {{
      background: var(--savings-teal);
      height: 100%;
      transition: width 0.25s ease;
    }}
    .goal-bar-audit-boost {{
      background: var(--rm-crimson);
      height: 100%;
      transition: width 0.25s ease;
    }}

    /* Interactive 14-Month Grid */
    .month-grid-title {{
      font-size: 12.5px;
      font-weight: 700;
      color: var(--ink-muted);
      margin-bottom: 10px;
      display: flex;
      justify-content: space-between;
    }}
    .months-track {{
      display: grid;
      grid-template-columns: repeat(7, 1fr);
      gap: 8px;
    }}
    @media (max-width: 680px) {{
      .months-track {{ grid-template-columns: repeat(4, 1fr); }}
    }}
    .month-cell {{
      border: 1px solid var(--border-soft);
      border-radius: 10px;
      padding: 9px 8px;
      text-align: center;
      background: #FAFAFA;
      transition: all 0.18s ease;
    }}
    .month-cell.active-save {{
      background: var(--savings-teal-soft);
      border-color: #5EEAD4;
    }}
    .month-cell.goal-hit {{
      background: var(--savings-teal);
      color: #FFFFFF;
      border-color: var(--savings-teal-dark);
      font-weight: 800;
      box-shadow: 0 4px 12px rgba(13, 148, 136, 0.22);
    }}
    .month-cell.shaved-off {{
      background: var(--rm-crimson-soft);
      border-color: #FECDD3;
      color: var(--rm-crimson);
      opacity: 0.85;
    }}
    .m-num {{
      font-size: 11px;
      font-weight: 700;
    }}
    .m-bal {{
      font-family: 'Outfit', sans-serif;
      font-size: 13px;
      font-weight: 800;
      margin-top: 2px;
    }}

    /* Audio Coach Card */
    .coach-audio-box {{
      background: var(--alabaster);
      border: 1px solid var(--border-soft);
      border-radius: 14px;
      padding: 16px;
      margin-top: 18px;
    }}
    .ai-response-box {{
      background: var(--card-white);
      border: 1px solid var(--border-soft);
      border-left: 4px solid var(--savings-teal);
      border-radius: 12px;
      padding: 15px 18px;
      margin-top: 16px;
      font-size: 13px;
      line-height: 1.6;
      white-space: pre-wrap;
    }}
  </style>
</head>
<body>

  <!-- Top Rocket Money Consumer Header -->
  <header class="rm-topbar">
    <div class="rm-topbar-inner">
      <div class="rm-brand">
        <div class="rm-logo-badge">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/>
          </svg>
          ROCKET MONEY
        </div>
        <div>
          <div style="font-size:15px;font-weight:800;color:var(--ink-dark);">Home-Ready Down Payment Coach</div>
          <div style="font-size:11.5px;color:var(--ink-muted);">Smart Subscription Concierge &amp; FHA 3.5% Smart Savings Vault</div>
        </div>
      </div>

      <div class="rm-nav-pills">
        <span class="rm-nav-pill active">Down Payment Vault</span>
        <span class="rm-nav-pill">Recurring Bills Audit</span>
        <span class="rm-nav-pill">Rocket Mortgage Readiness</span>
      </div>

      <div class="rm-header-controls">
        <div class="model-picker-pill">
          <span>Coach Model:</span>
          <select id="app-model-select" onchange="window.syncSelectedModel(this.value)">
            <option value="gemini-4-argon">Gemini 4 Argon (Frontier)</option>
            <option value="gemini-3.8-flash">Gemini 3.8 Flash (Fast)</option>
          </select>
        </div>
        <button class="btn-crimson" onclick="window.runLiveVertexAI()">
          Generate Personalized Home-Ready Plan
        </button>
      </div>
    </div>
  </header>

  <main class="app-container">
    <!-- Top KPI Cards -->
    <section class="kpi-strip">
      <div class="kpi-card">
        <div class="kpi-label">
          <span>FHA 3.5% Down Payment Goal</span>
          <span style="color:var(--savings-teal);font-weight:800;">Target</span>
        </div>
        <div class="kpi-value" id="kpi-goal-dollar">$17,500</div>
        <div class="kpi-sub" id="kpi-goal-sub">For $500,000 Target Home Price</div>
      </div>

      <div class="kpi-card">
        <div class="kpi-label">
          <span>Current Home-Ready Vault</span>
          <span style="color:var(--savings-teal);font-weight:800;">FDIC 4.65% APY</span>
        </div>
        <div class="kpi-value teal" id="kpi-vault-balance">$10,210</div>
        <div class="kpi-sub" id="kpi-remaining-sub">$7,290 remaining to FHA goal</div>
      </div>

      <div class="kpi-card">
        <div class="kpi-label">
          <span>Cancelled Bill Cashflow Boost</span>
          <span style="color:var(--rm-crimson);font-weight:800;">Auto-Sweep</span>
        </div>
        <div class="kpi-value crimson" id="kpi-freed-monthly">+$285/mo</div>
        <div class="kpi-sub" id="kpi-freed-annual">$3,420/yr redirected to Down Payment</div>
      </div>

      <div class="kpi-card">
        <div class="kpi-label">
          <span>Time to Mortgage Pre-Approval</span>
          <span style="color:var(--savings-teal);font-weight:800;">Accelerated</span>
        </div>
        <div class="kpi-value teal" id="kpi-months-headline">9 Months</div>
        <div class="kpi-sub" id="kpi-months-saved-sub">Shaved 5 months off 14-month baseline</div>
      </div>
    </section>

    <div class="coach-grid">
      <!-- Left Column: Interactive Subscription Audit Checklist -->
      <div class="finance-card">
        <div class="card-header">
          <div>
            <div class="card-title">
              <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="#E11D48" stroke-width="2.2">
                <path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
              </svg>
              Interactive Subscription Audit Checklist
            </div>
            <div class="card-subtitle">
              Toggle switches to cancel duplicate streaming, unused gym, and SaaS bills—auto-sweeping savings into your Home-Ready Vault.
            </div>
          </div>
          <span class="badge-freed" id="audit-badge-pill">Freed: +$285/mo</span>
        </div>

        <div style="display:flex;gap:8px;margin-bottom:14px;">
          <button class="btn-teal" style="padding:6px 12px;font-size:12px;" onclick="window.setAllSubscriptions(true)">
            Cancel All 5 Flagged Bills (+$285/mo)
          </button>
          <button class="btn-crimson" style="padding:6px 12px;font-size:12px;background:#71717A;" onclick="window.setAllSubscriptions(false)">
            Reset to Baseline (14 Months)
          </button>
        </div>

        <div class="sub-list" id="subscription-checklist">
          <!-- Item 0: $82 -->
          <div class="sub-row cancelled" data-amount="82" onclick="window.toggleSubRow(this)">
            <div class="sub-left">
              <div class="sub-icon">TV</div>
              <div>
                <div class="sub-name">Duplicate Live TV + Sports Bundle</div>
                <div class="sub-reason">Overlaps with family streaming plan · Last watched 47 days ago</div>
              </div>
            </div>
            <div class="sub-right">
              <div class="sub-amount">+$82/mo</div>
              <div class="toggle-switch"><div class="toggle-knob"></div></div>
            </div>
          </div>

          <!-- Item 1: $94 -->
          <div class="sub-row cancelled" data-amount="94" onclick="window.toggleSubRow(this)">
            <div class="sub-left">
              <div class="sub-icon">GYM</div>
              <div>
                <div class="sub-name">Equinox / Boutique Fitness Studio Tier</div>
                <div class="sub-reason">0 check-ins in 60 days · Covered by employer wellness benefit</div>
              </div>
            </div>
            <div class="sub-right">
              <div class="sub-amount">+$94/mo</div>
              <div class="toggle-switch"><div class="toggle-knob"></div></div>
            </div>
          </div>

          <!-- Item 2: $49 -->
          <div class="sub-row cancelled" data-amount="49" onclick="window.toggleSubRow(this)">
            <div class="sub-left">
              <div class="sub-icon">APP</div>
              <div>
                <div class="sub-name">Unused Cloud Creative &amp; AI SaaS Seat</div>
                <div class="sub-reason">Auto-renewed after free trial · 0 active projects</div>
              </div>
            </div>
            <div class="sub-right">
              <div class="sub-amount">+$49/mo</div>
              <div class="toggle-switch"><div class="toggle-knob"></div></div>
            </div>
          </div>

          <!-- Item 3: $36 -->
          <div class="sub-row cancelled" data-amount="36" onclick="window.toggleSubRow(this)">
            <div class="sub-left">
              <div class="sub-icon">BOX</div>
              <div>
                <div class="sub-name">Gourmet Coffee &amp; Snack Subscription Box</div>
                <div class="sub-reason">Recurring monthly shipment · Paused &amp; redirected to vault</div>
              </div>
            </div>
            <div class="sub-right">
              <div class="sub-amount">+$36/mo</div>
              <div class="toggle-switch"><div class="toggle-knob"></div></div>
            </div>
          </div>

          <!-- Item 4: $24 -->
          <div class="sub-row cancelled" data-amount="24" onclick="window.toggleSubRow(this)">
            <div class="sub-left">
              <div class="sub-icon">AUD</div>
              <div>
                <div class="sub-name">Duplicate Audiobook &amp; Music Family Add-On</div>
                <div class="sub-reason">Billed on secondary card · Cancelled by Rocket Concierge</div>
              </div>
            </div>
            <div class="sub-right">
              <div class="sub-amount">+$24/mo</div>
              <div class="toggle-switch"><div class="toggle-knob"></div></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Interactive Sliders + Month-by-Month Down Payment Goal Progress Bar -->
      <div class="finance-card">
        <div class="card-header">
          <div>
            <div class="card-title">
              <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="#0D9488" stroke-width="2.2">
                <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
              </svg>
              Month-by-Month Down Payment Goal Progress Bar
            </div>
            <div class="card-subtitle">
              Real-time FHA 3.5% down payment runway calculator powered by your Rocket Money savings vault.
            </div>
          </div>
        </div>

        <!-- Monthly Savings & Target Home Price Sliders -->
        <div class="vault-sliders">
          <div class="slider-field">
            <label>
              <span>Target Home Price (FHA 3.5% Goal)</span>
              <span style="color:var(--ink-dark);font-weight:800;" id="target-home-label">$500,000 ($17,500 Goal)</span>
            </label>
            <input type="range" id="target-home-slider" min="300000" max="750000" step="10000" value="500000" oninput="window.recalculateHomeReadyVault()">
          </div>

          <div class="slider-field">
            <label>
              <span>Base Monthly Vault Deposit</span>
              <span style="color:var(--savings-teal-dark);font-weight:800;" id="base-save-label">$520/mo</span>
            </label>
            <input type="range" id="base-save-slider" min="250" max="1500" step="10" value="520" oninput="window.recalculateHomeReadyVault()">
          </div>
        </div>

        <!-- 14 Months -> 9 Months Highlight Banner -->
        <div class="timeline-banner">
          <div>
            <div style="font-size:11.5px;font-weight:800;text-transform:uppercase;color:var(--ink-muted);letter-spacing:0.04em;">
              Down Payment Goal Timeline Acceleration
            </div>
            <div class="timeline-shift">
              <span class="old-months" id="baseline-months-badge">14 Months</span>
              <span style="color:var(--ink-muted);">&rarr;</span>
              <span class="new-months" id="accelerated-months-badge">9 Months</span>
              <span style="font-size:14px;font-weight:700;color:var(--ink-body);" id="goal-target-inline">to $17,500 FHA 3.5% Goal</span>
            </div>
          </div>
          <div style="text-align:right;">
            <div style="font-size:12px;color:var(--ink-muted);font-weight:600;">Total Monthly Contribution</div>
            <div class="display-font" style="font-size:22px;font-weight:800;color:var(--savings-teal-dark);" id="combined-monthly-rate">
              $805/mo ($520 + $285 Audit)
            </div>
          </div>
        </div>

        <!-- Visual Progress Bar -->
        <div class="goal-progress-wrap">
          <div class="goal-progress-top">
            <span>Current Vault: <strong style="color:var(--savings-teal-dark);">$10,210</strong> (58% of $17,500)</span>
            <span id="boost-share-label" style="color:var(--rm-crimson);">+$2,565 from Cancelled Bills over 9 Mos</span>
          </div>
          <div class="goal-bar-outer">
            <div class="goal-bar-saved" id="bar-existing" style="width:58%;"></div>
            <div class="goal-bar-audit-boost" id="bar-boost" style="width:22%;"></div>
          </div>
        </div>

        <!-- Month-by-Month Milestone Cells (Month 1 .. Month 14) -->
        <div class="month-grid-title">
          <span>Month-by-Month Vault Trajectory (Green = Goal Reached · Pink = Months Saved)</span>
          <span id="eta-month-tag" style="color:var(--savings-teal-dark);font-weight:800;">Pre-Approval Ready in Month 9</span>
        </div>
        <div class="months-track" id="months-grid-container"></div>

        <!-- Gemini 3.8 Live Puck HD Audio Briefing -->
        <div class="coach-audio-box">
          <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;margin-bottom:10px;">
            <div>
              <div style="font-size:14px;font-weight:800;color:var(--ink-dark);">
                Rocket Money Coach Voice Briefing (Synced to Your Vault &amp; Audit)
              </div>
              <div style="font-size:12px;color:var(--ink-muted);">
                Powered by Gemini 3.8 Live 24kHz Native Audio · Voice: Puck HD
              </div>
            </div>
            <button class="btn-crimson" id="btn-puck-coach" onclick="window.playCoachBriefing(this)">
              🔊 Listen to Rocket Money Coach Briefing (Gemini 3.8 Live · Puck HD)
            </button>
          </div>
          <div id="coach-script-preview" style="font-size:13px;color:var(--ink-body);background:#FFFFFF;padding:10px 12px;border-radius:9px;border:1px solid var(--border-soft);">
            "Great news! By cancelling 5 unused subscriptions—including your duplicate live TV bundle and unused gym tier—Rocket Money just freed up $285 a month. Added to your $520 monthly deposit, you're now saving $805 every month, cutting your $17,500 FHA down payment timeline from 14 months down to just 9 months!"
          </div>
        </div>

        <!-- Vertex AI Live Output -->
        <div class="ai-response-box" id="vertex-ai-output">
          <strong>Rocket Money Coach Ready:</strong> Toggle any subscription or move the sliders above, or click <em>"Generate Personalized Home-Ready Plan"</em> to run <span id="live-model-pill">gemini-4-argon</span> on your cashflow.
        </div>
      </div>
    </div>
  </main>

  <script>
    const CURRENT_VAULT_BALANCE = 10210;

    window.toggleSubRow = function(rowEl) {{
      rowEl.classList.toggle('cancelled');
      window.recalculateHomeReadyVault();
    }};

    window.setAllSubscriptions = function(cancelAll) {{
      document.querySelectorAll('#subscription-checklist .sub-row').forEach(r => {{
        r.classList.toggle('cancelled', cancelAll);
      }});
      window.recalculateHomeReadyVault();
    }};

    window.recalculateHomeReadyVault = function() {{
      let freedMonthly = 0;
      let cancelledCount = 0;
      document.querySelectorAll('#subscription-checklist .sub-row').forEach(r => {{
        if (r.classList.contains('cancelled')) {{
          freedMonthly += parseInt(r.dataset.amount || "0", 10);
          cancelledCount++;
        }}
      }});

      const homePrice = parseInt(document.getElementById('target-home-slider').value || "500000", 10);
      const baseSave = parseInt(document.getElementById('base-save-slider').value || "520", 10);

      const fhaGoal = Math.round(homePrice * 0.035);
      const remainingNeeded = Math.max(0, fhaGoal - CURRENT_VAULT_BALANCE);

      const baselineMonths = Math.max(1, Math.ceil(remainingNeeded / baseSave));
      const newMonthlyTotal = baseSave + freedMonthly;
      const acceleratedMonths = Math.max(1, Math.ceil(remainingNeeded / newMonthlyTotal));
      const monthsSaved = Math.max(0, baselineMonths - acceleratedMonths);

      document.getElementById('target-home-label').textContent =
        '$' + homePrice.toLocaleString() + ' ($' + fhaGoal.toLocaleString() + ' Goal)';
      document.getElementById('base-save-label').textContent = '$' + baseSave.toLocaleString() + '/mo';

      document.getElementById('kpi-goal-dollar').textContent = '$' + fhaGoal.toLocaleString();
      document.getElementById('kpi-goal-sub').textContent = 'For $' + homePrice.toLocaleString() + ' Target Home Price';
      document.getElementById('kpi-remaining-sub').textContent = '$' + remainingNeeded.toLocaleString() + ' remaining to FHA goal';
      document.getElementById('kpi-freed-monthly').textContent = '+$' + freedMonthly.toLocaleString() + '/mo';
      document.getElementById('kpi-freed-annual').textContent = '$' + (freedMonthly * 12).toLocaleString() + '/yr redirected to Down Payment';
      document.getElementById('kpi-months-headline').textContent = acceleratedMonths + ' Months';
      document.getElementById('kpi-months-saved-sub').textContent =
        monthsSaved > 0
          ? ('Shaved ' + monthsSaved + ' months off ' + baselineMonths + '-month baseline')
          : ('Baseline ' + baselineMonths + '-month trajectory');

      document.getElementById('audit-badge-pill').textContent = 'Freed: +$' + freedMonthly + '/mo';
      document.getElementById('baseline-months-badge').textContent = baselineMonths + ' Months';
      document.getElementById('accelerated-months-badge').textContent = acceleratedMonths + ' Months';
      document.getElementById('goal-target-inline').textContent = 'to $' + fhaGoal.toLocaleString() + ' FHA 3.5% Goal';
      document.getElementById('combined-monthly-rate').textContent =
        '$' + newMonthlyTotal.toLocaleString() + '/mo ($' + baseSave + ' + $' + freedMonthly + ' Audit)';
      document.getElementById('eta-month-tag').textContent = 'Pre-Approval Ready in Month ' + acceleratedMonths;

      const boostOverRunway = freedMonthly * acceleratedMonths;
      document.getElementById('boost-share-label').textContent =
        '+$' + boostOverRunway.toLocaleString() + ' from Cancelled Bills over ' + acceleratedMonths + ' Mos';

      const pctExisting = Math.min(100, Math.round((CURRENT_VAULT_BALANCE / fhaGoal) * 100));
      const pctBoost = Math.min(100 - pctExisting, Math.round((boostOverRunway / fhaGoal) * 100));
      document.getElementById('bar-existing').style.width = pctExisting + '%';
      document.getElementById('bar-boost').style.width = pctBoost + '%';

      // Render 14 Month Milestone Cells
      const totalCells = Math.max(14, baselineMonths);
      const grid = document.getElementById('months-grid-container');
      let cellsHtml = '';
      for (let m = 1; m <= Math.min(totalCells, 14); m++) {{
        const projBal = Math.min(fhaGoal, CURRENT_VAULT_BALANCE + m * newMonthlyTotal);
        let cls = 'month-cell';
        let statusTag = '$' + (projBal / 1000).toFixed(1) + 'K';
        if (m < acceleratedMonths) {{
          cls += ' active-save';
        }} else if (m === acceleratedMonths) {{
          cls += ' goal-hit';
          statusTag = 'GOAL $' + (fhaGoal / 1000).toFixed(1) + 'K';
        }} else if (m <= baselineMonths) {{
          cls += ' shaved-off';
          statusTag = 'Saved Mo!';
        }}
        cellsHtml += '<div class="' + cls + '"><div class="m-num">Month ' + m + '</div><div class="m-bal">' + statusTag + '</div></div>';
      }}
      if (grid) grid.innerHTML = cellsHtml;

      const scriptEl = document.getElementById('coach-script-preview');
      if (scriptEl) {{
        scriptEl.textContent =
          '"Great news! By cancelling ' + cancelledCount + ' flagged subscriptions, Rocket Money freed up $' + freedMonthly + ' a month. Added to your $' + baseSave + ' monthly deposit, you are now saving $' + newMonthlyTotal + ' every month—accelerating your $' + fhaGoal.toLocaleString() + ' FHA 3.5% down payment goal from ' + baselineMonths + ' months down to just ' + acceleratedMonths + ' months!"';
      }}
    }};

    window.playCoachBriefing = function(btnEl) {{
      const scriptEl = document.getElementById('coach-script-preview');
      const text = scriptEl ? scriptEl.textContent.replace(/^"|"$/g, '') : "Welcome to your Rocket Money Home-Ready Coach.";
      window.playLiveCallClip(
        text,
        "Puck",
        "Rocket Money Home-Ready Coach",
        btnEl
      );
    }};

    window.runLiveVertexAI = async function() {{
      const model = window.getSelectedModel ? window.getSelectedModel() : "gemini-4-argon";
      const outEl = document.getElementById('vertex-ai-output');
      const freed = document.getElementById('kpi-freed-monthly').textContent;
      const months = document.getElementById('kpi-months-headline').textContent;
      const goal = document.getElementById('kpi-goal-dollar').textContent;
      const drawerInput = document.getElementById('scenario-input');
      const scenarioText = (drawerInput && drawerInput.value.trim())
        ? drawerInput.value.trim() + " | Freed Subscriptions: " + freed + ", FHA Goal: " + goal + ", New ETA: " + months
        : "Create a Rocket Money Home-Ready savings action plan for a buyer targeting a " + goal + " FHA 3.5% down payment who just freed " + freed + " in recurring subscriptions to hit their goal in " + months + ".";

      if (outEl) {{
        outEl.innerHTML = "<strong>⏳ Synthesizing Personalized Rocket Money Home-Ready Action Plan via Vertex AI (" + model + ")...</strong>";
      }}
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            square: "4.2",
            model: model,
            scenario: scenarioText
          }})
        }});
        const data = await res.json();
        if (outEl) {{
          outEl.textContent = data.output || data.text || "Action plan generated.";
        }}
      }} catch (err) {{
        if (outEl) {{
          outEl.textContent = "Unable to reach Vertex AI endpoint: " + err.message;
        }}
      }}
    }};

    document.addEventListener('DOMContentLoaded', () => {{
      window.recalculateHomeReadyVault();
    }});
  </script>

  {floating_drawer}
</body>
</html>"""
