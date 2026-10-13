# -*- coding: utf-8 -*-
"""Square 4.5 — Redfin-to-Rocket Cross-Funnel Campaign Bot (Antigravity MCP).
Visual Design: 3-Phone Consumer App Ecosystem Continuity Lab.
Palette: #0A0818 deep workspace hosting 3 distinct interactive smartphone mockups side-by-side:
- Phone 1: Rocket Money (#7C3AED purple)
- Phone 2: Redfin (#E11D48 crimson)
- Phone 3: Rocket Mortgage (#10B981 emerald)
Typography: Google Fonts 'Plus Jakarta Sans' + 'JetBrains Mono'.
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_4_5(auth_token: str) -> str:
    floating_drawer = render_floating_control_bar_and_drawer("4.5", auth_token)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>4.5 3-Phone Ecosystem Continuity Lab | Rocket Money × Redfin × Rocket Mortgage MCP</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --workspace-bg: #0A0818;
      --card-bg: #110F24;
      --rm-purple: #7C3AED;
      --rm-purple-soft: rgba(124, 58, 237, 0.16);
      --redfin-crimson: #E11D48;
      --redfin-soft: rgba(225, 29, 72, 0.16);
      --rkt-emerald: #10B981;
      --rkt-emerald-soft: rgba(16, 185, 129, 0.16);
      --text-white: #F8FAFC;
      --text-muted: #94A3B8;
      --border: rgba(255, 255, 255, 0.12);
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: var(--workspace-bg);
      color: var(--text-white);
      font-family: 'Plus Jakarta Sans', sans-serif;
      min-height: 100vh;
      overflow-x: hidden;
      padding-bottom: 92px;
      background-image:
        radial-gradient(circle at 18% 35%, rgba(124, 58, 237, 0.18) 0%, transparent 40%),
        radial-gradient(circle at 50% 35%, rgba(225, 29, 72, 0.15) 0%, transparent 40%),
        radial-gradient(circle at 82% 35%, rgba(16, 185, 129, 0.16) 0%, transparent 40%);
    }}
    .mono {{ font-family: 'JetBrains Mono', monospace; }}

    /* Top Ecosystem Header */
    .lab-header {{
      background: rgba(10, 8, 24, 0.9);
      backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--border);
      padding: 14px 28px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: sticky;
      top: 0;
      z-index: 100;
      flex-wrap: wrap;
      gap: 12px;
    }}
    .lab-title-group {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}
    .mcp-pill {{
      background: linear-gradient(135deg, var(--rm-purple), var(--redfin-crimson), var(--rkt-emerald));
      padding: 6px 12px;
      border-radius: 999px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 0.05em;
    }}
    .lab-title-group h1 {{
      font-size: 18px;
      font-weight: 800;
      letter-spacing: -0.02em;
    }}
    .lab-title-group p {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      color: var(--text-muted);
    }}
    .header-actions {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .model-select-pill {{
      display: flex;
      align-items: center;
      gap: 8px;
      background: var(--card-bg);
      border: 1px solid var(--border);
      padding: 6px 12px;
      border-radius: 8px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
    }}
    #app-model-select {{
      background: transparent;
      color: #6EE7B7;
      border: none;
      outline: none;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
    }}
    #app-model-select option {{
      background: #110F24;
      color: #FFF;
    }}
    .btn-mcp-ripple {{
      background: linear-gradient(135deg, var(--rm-purple), var(--redfin-crimson));
      color: #FFF;
      border: 1px solid rgba(255,255,255,0.25);
      padding: 9px 16px;
      border-radius: 8px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11.5px;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 8px 25px rgba(225, 29, 72, 0.35);
    }}

    /* Container */
    .lab-container {{
      max-width: 1460px;
      margin: 0 auto;
      padding: 20px 28px;
    }}

    /* Top Control Strip for Rent Hike & Vault Sliders */
    .control-ribbon {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 16px 22px;
      margin-bottom: 24px;
      display: grid;
      grid-template-columns: repeat(3, 1fr) 260px;
      gap: 22px;
      align-items: center;
    }}
    @media (max-width: 1150px) {{
      .control-ribbon {{ grid-template-columns: 1fr; }}
    }}
    .ctrl-box label {{
      display: flex;
      justify-content: space-between;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      color: #CBD5E1;
      margin-bottom: 6px;
    }}
    .ctrl-box input[type="range"] {{
      width: 100%;
      cursor: pointer;
    }}

    /* 3-Phone Continuity Stage */
    .phones-stage {{
      display: grid;
      grid-template-columns: 1fr 48px 1fr 48px 1fr;
      align-items: center;
      gap: 8px;
      margin-bottom: 24px;
    }}
    @media (max-width: 1240px) {{
      .phones-stage {{
        grid-template-columns: 1fr;
        gap: 20px;
      }}
      .mcp-bridge-arrow {{ display: none; }}
    }}
    .mcp-bridge-arrow {{
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 6px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 9px;
      color: #A5B4FC;
      text-align: center;
    }}
    .pulse-arrow {{
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(255,255,255,0.2);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 16px;
      transition: all 0.25s;
    }}
    .pulse-arrow.active-pulse {{
      transform: scale(1.22);
      background: var(--rkt-emerald);
      color: #05050A;
      box-shadow: 0 0 24px var(--rkt-emerald);
    }}

    /* Individual Smartphone Chassis */
    .phone-mockup {{
      background: #0D0B1A;
      border-radius: 36px;
      padding: 14px;
      border: 4px solid #26233D;
      box-shadow: 0 24px 60px rgba(0,0,0,0.75);
      min-height: 585px;
      display: flex;
      flex-direction: column;
      position: relative;
      transition: transform 0.25s ease, box-shadow 0.25s ease;
    }}
    .phone-mockup.phone-1 {{ border-color: rgba(124, 58, 237, 0.65); }}
    .phone-mockup.phone-2 {{ border-color: rgba(225, 29, 72, 0.65); }}
    .phone-mockup.phone-3 {{ border-color: rgba(16, 185, 129, 0.65); }}

    .phone-status-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 4px 12px 10px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
      color: var(--text-muted);
    }}
    .phone-app-header {{
      padding: 12px 14px;
      border-radius: 18px;
      margin-bottom: 12px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .phone-card {{
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid rgba(255, 255, 255, 0.09);
      border-radius: 14px;
      padding: 12px 14px;
      margin-bottom: 10px;
    }}
    .phone-btn {{
      margin-top: auto;
      width: 100%;
      padding: 12px;
      border-radius: 12px;
      border: none;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 800;
      color: #FFF;
      cursor: pointer;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      transition: 0.18s;
    }}
    .phone-btn:hover {{
      filter: brightness(1.12);
      transform: translateY(-1px);
    }}
  </style>
</head>
<body>

  <!-- TOP ECOSYSTEM CONTINUITY HEADER -->
  <header class="lab-header">
    <div class="lab-title-group">
      <span class="mcp-pill">ANTIGRAVITY MCP BUS</span>
      <div>
        <h1>3-Phone Consumer App Ecosystem Continuity Lab</h1>
        <p>Phone 1: Rocket Money (#7C3AED) ➔ Phone 2: Redfin (#E11D48) ➔ Phone 3: Rocket Mortgage (#10B981)</p>
      </div>
    </div>
    <div class="header-actions">
      <div class="model-select-pill">
        <span style="color:var(--text-muted);">ORCHESTRATOR:</span>
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)">
          <option value="gemini-4-argon" selected>gemini-4-argon (Frontier MCP Agent)</option>
          <option value="gemini-3.8-flash">gemini-3.8-flash (Fast Subagent)</option>
        </select>
      </div>
      <button class="btn-mcp-ripple" id="btn-run-mcp" onclick="window.runLiveVertexAI()">
        ⚡ Trigger Cross-Funnel MCP Synthesis
      </button>
    </div>
  </header>

  <main class="lab-container">
    <!-- INTERACTIVE SLIDER RIBBON (/api/sandbox action:"calc_cross_funnel_mcp") -->
    <section class="control-ribbon">
      <div class="ctrl-box">
        <label>
          <span>1. LANDLORD RENEWAL RENT HIKE ($/MO)</span>
          <strong style="color:#C4B5FD;" id="lbl-rent-hike">$2,480/mo (+12%)</strong>
        </label>
        <input type="range" id="inp-rent-hike" min="1950" max="3400" step="25" value="2480" style="accent-color:var(--rm-purple);" oninput="window.rippleMcpState()">
      </div>

      <div class="ctrl-box">
        <label>
          <span>2. ROCKET MONEY DOWN-PAYMENT VAULT</span>
          <strong style="color:#6EE7B7;" id="lbl-vault-bal">$31,200 Saved</strong>
        </label>
        <input type="range" id="inp-vault-bal" min="15000" max="65000" step="1000" value="31200" style="accent-color:var(--rkt-emerald);" oninput="window.rippleMcpState()">
      </div>

      <div class="ctrl-box">
        <label>
          <span>3. REDFIN TARGET HOME LIST PRICE</span>
          <strong style="color:#FDA4AF;" id="lbl-target-home">$365,000 (Ferndale MI)</strong>
        </label>
        <input type="range" id="inp-target-home" min="260000" max="550000" step="5000" value="365000" style="accent-color:var(--redfin-crimson);" oninput="window.rippleMcpState()">
      </div>

      <div class="mono" style="background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.35);padding:10px 12px;border-radius:10px;font-size:10.5px;line-height:1.45;">
        <div style="color:#6EE7B7;font-weight:700;">MCP BUS LATENCY: <span id="mcp-latency-tag">1.4ms</span></div>
        <div id="mcp-Quick-Verdict" style="color:#E2E8F0;margin-top:2px;">Net P&I ($1,865/mo) beats $2,480 Rent Hike by $615/mo!</div>
      </div>
    </section>

    <!-- 3 INTERACTIVE SMARTPHONES SIDE-BY-SIDE -->
    <section class="phones-stage">

      <!-- PHONE 1: ROCKET MONEY (#7C3AED PURPLE) -->
      <div class="phone-mockup phone-1">
        <div class="phone-status-bar">
          <span>9:41 AM • 5G</span>
          <span style="color:#C4B5FD;">MCP: rocket_money_mcp</span>
        </div>

        <div class="phone-app-header" style="background:var(--rm-purple-soft);border:1px solid rgba(124,58,237,0.45);">
          <div>
            <div class="mono" style="font-size:10px;color:#C4B5FD;font-weight:700;">PHONE 1 • ROCKET MONEY</div>
            <div style="font-size:16px;font-weight:800;color:#FFF;">Maya Lin • Smart Financial OS</div>
          </div>
          <span style="background:var(--rm-purple);padding:4px 8px;border-radius:8px;font-size:11px;font-weight:800;">PREMIUM</span>
        </div>

        <div class="phone-card" style="border-left:3px solid #F43F5E;">
          <div class="mono" style="font-size:10px;color:#FDA4AF;font-weight:700;">⚠️ RENT HIKE DETECTED ON CHASE ACH</div>
          <div style="font-size:18px;font-weight:800;margin:4px 0;" id="p1-rent-display">$2,480 / month</div>
          <div style="font-size:11.5px;color:var(--text-muted);">Ferndale Lofts LLC increased renewal rent by +$265/mo starting Nov 1.</div>
        </div>

        <div class="phone-card" style="border-left:3px solid var(--rm-purple);">
          <div class="mono" style="font-size:10px;color:#C4B5FD;font-weight:700;">🏦 HOME DOWN-PAYMENT GOAL VAULT</div>
          <div style="font-size:21px;font-weight:800;color:#FFF;margin:4px 0;" id="p1-vault-display">$31,200.00</div>
          <div style="font-size:11.5px;color:#A7F3D0;" id="p1-vault-pct">Covers 5% Down ($18,250) + Closing Costs with $7,800 Reserve left!</div>
        </div>

        <div class="phone-card">
          <div class="mono" style="font-size:10px;color:#FDE68A;font-weight:700;">✂️ SUBSCRIPTION AUDIT OFFSET</div>
          <div style="font-size:12px;margin-top:4px;line-height:1.45;">
            Auto-canceling <strong>$215/mo</strong> in duplicate streaming & gym memberships lowers effective monthly housing cost by <strong>-$215/mo</strong>.
          </div>
        </div>

        <button class="phone-btn" style="background:var(--rm-purple);" onclick="window.triggerPhone1Ripple()">
          [1] Broadcast Vault & Rent Alert via MCP ➔
        </button>
      </div>

      <!-- MCP BRIDGE ARROW 1 -> 2 -->
      <div class="mcp-bridge-arrow">
        <div class="pulse-arrow" id="arrow-1-2">➔</div>
        <span>MCP SYNC</span>
      </div>

      <!-- PHONE 2: REDFIN (#E11D48 CRIMSON) -->
      <div class="phone-mockup phone-2">
        <div class="phone-status-bar">
          <span>9:41 AM • 5G</span>
          <span style="color:#FDA4AF;">MCP: redfin_tour_mcp</span>
        </div>

        <div class="phone-app-header" style="background:var(--redfin-soft);border:1px solid rgba(225,29,72,0.45);">
          <div>
            <div class="mono" style="font-size:10px;color:#FDA4AF;font-weight:700;">PHONE 2 • REDFIN MOBILE</div>
            <div style="font-size:16px;font-weight:800;color:#FFF;">Homes Beating Your New Rent</div>
          </div>
          <span style="background:var(--redfin-crimson);padding:4px 8px;border-radius:8px;font-size:11px;font-weight:800;">MLS LIVE</span>
        </div>

        <!-- Mini Architectural Home Illustration -->
        <div class="phone-card" style="padding:10px;">
          <svg viewBox="0 0 320 110" width="100%" height="105" style="border-radius:8px;margin-bottom:8px;">
            <rect width="320" height="110" fill="#1E1B2E"/>
            <polygon points="45,55 160,15 275,55" fill="#E11D48"/>
            <rect x="65" y="55" width="190" height="50" fill="#334155"/>
            <rect x="85" y="65" width="45" height="28" fill="#FDE68A"/>
            <rect x="190" y="65" width="45" height="28" fill="#FDE68A"/>
            <rect x="145" y="68" width="30" height="37" fill="#10B981"/>
          </svg>
          <div style="display:flex;justify-content:space-between;align-items:baseline;">
            <strong style="font-size:15px;" id="p2-home-price">$365,000</strong>
            <span class="mono" style="font-size:10px;color:#6EE7B7;" id="p2-piti-badge">Net P&I: $1,865/mo</span>
          </div>
          <div style="font-size:12px;color:#E2E8F0;margin-top:2px;">612 W Saratoga St, Ferndale, MI 48220</div>
          <div class="mono" style="font-size:10px;color:var(--text-muted);margin-top:4px;">3 Bed • 2 Bath • 1,640 SqFt • Tour: Sat 11:00 AM</div>
        </div>

        <div class="phone-card" style="border-left:3px solid var(--redfin-crimson);">
          <div class="mono" style="font-size:10px;color:#FDA4AF;font-weight:700;">🎯 RENT-VS-BUY MATCH ENGINE</div>
          <div style="font-size:12px;margin-top:4px;line-height:1.45;" id="p2-match-reason">
            After $215/mo Rocket Money subscription savings, owning this Ferndale bungalow costs <strong>$1,865/mo</strong>—saving <strong>$615/mo</strong> vs your $2,480 rent renewal!
          </div>
        </div>

        <button class="phone-btn" style="background:var(--redfin-crimson);" onclick="window.triggerPhone2Ripple()">
          [2] Lock Sat 11 AM Tour & Claim $3,500 Credit ➔
        </button>
      </div>

      <!-- MCP BRIDGE ARROW 2 -> 3 -->
      <div class="mcp-bridge-arrow">
        <div class="pulse-arrow" id="arrow-2-3">➔</div>
        <span>1-TAP CLOSE</span>
      </div>

      <!-- PHONE 3: ROCKET MORTGAGE (#10B981 EMERALD) -->
      <div class="phone-mockup phone-3">
        <div class="phone-status-bar">
          <span>9:41 AM • 5G</span>
          <span style="color:#6EE7B7;">MCP: rocket_pricing_mcp</span>
        </div>

        <div class="phone-app-header" style="background:var(--rkt-emerald-soft);border:1px solid rgba(16,185,129,0.45);">
          <div>
            <div class="mono" style="font-size:10px;color:#6EE7B7;font-weight:700;">PHONE 3 • ROCKET MORTGAGE</div>
            <div style="font-size:16px;font-weight:800;color:#FFF;">Verified Approval Certificate</div>
          </div>
          <span style="background:var(--rkt-emerald);color:#04120C;padding:4px 8px;border-radius:8px;font-size:11px;font-weight:800;">APPROVED</span>
        </div>

        <div class="phone-card" style="border:1px solid rgba(16,185,129,0.4);background:rgba(16,185,129,0.07);">
          <div class="mono" style="font-size:10px;color:#6EE7B7;font-weight:700;">✓ BUY+BORROW BUNDLE UNLOCKED</div>
          <div style="font-size:19px;font-weight:800;color:#FFF;margin:4px 0;" id="p3-cash-to-close">$23,400 Cash to Close</div>
          <div style="font-size:11.5px;color:#D1FAE5;" id="p3-cash-breakdown">
            5% Down ($18,250) + Net Closing ($5,150 after <strong>$3,500 Redfin × Rocket Credit</strong>).
          </div>
        </div>

        <div class="phone-card">
          <div class="mono" style="font-size:10px;color:#A7F3D0;font-weight:700;">🛡️ POST-CLOSING RESERVE PROOF</div>
          <div style="font-size:16px;font-weight:800;color:#6EE7B7;margin:4px 0;" id="p3-reserves-left">$7,800.00 Cushion Left</div>
          <div style="font-size:11.5px;color:var(--text-muted);">
            Remaining inside your linked Rocket Money Emergency Vault after closing.
          </div>
        </div>

        <div class="phone-card" style="font-size:11.5px;line-height:1.45;" id="p3-ai-dossier">
          <div class="mono" style="font-size:10px;color:#6EE7B7;margin-bottom:3px;">MODEL: <span id="live-model-pill">gemini-4-argon</span></div>
          Pre-Approval Letter #RKT-48220-MAYA attached to Saturday 11:00 AM Redfin tour calendar invite.
        </div>

        <button class="phone-btn" style="background:var(--rkt-emerald);color:#04130D;" onclick="window.runLiveVertexAI()">
          [3] Issue Instant Pre-Approval & Transfer Vault
        </button>
      </div>

    </section>
  </main>

  <script>
    function calcMonthlyPI(principal, ratePct) {{
      const r = (ratePct / 100) / 12;
      return principal * (r * Math.pow(1 + r, 360)) / (Math.pow(1 + r, 360) - 1);
    }}

    window.pulseArrows = function() {{
      ['arrow-1-2', 'arrow-2-3'].forEach((id, i) => {{
        const el = document.getElementById(id);
        if (!el) return;
        setTimeout(() => {{
          el.classList.add('active-pulse');
          setTimeout(() => el.classList.remove('active-pulse'), 550);
        }}, i * 180);
      }});
    }};

    window.triggerPhone1Ripple = function() {{
      window.pulseArrows();
      window.rippleMcpState();
    }};

    window.triggerPhone2Ripple = function() {{
      window.pulseArrows();
      window.rippleMcpState();
    }};

    window.rippleMcpState = async function() {{
      const rent = parseFloat(document.getElementById('inp-rent-hike').value || 2480);
      const vault = parseFloat(document.getElementById('inp-vault-bal').value || 31200);
      const price = parseFloat(document.getElementById('inp-target-home').value || 365000);
      const credit = 3500;
      const subOffset = 215;

      document.getElementById('lbl-rent-hike').innerText = `$${{rent.toLocaleString()}}/mo (+12%)`;
      document.getElementById('lbl-vault-bal').innerText = `$${{vault.toLocaleString()}} Saved`;
      document.getElementById('lbl-target-home').innerText = `$${{price.toLocaleString()}} (Ferndale MI)`;

      const down5 = Math.round(price * 0.05);
      const netClosing = 8650 - credit;
      const cashNeeded = down5 + netClosing;
      const reserves = vault - cashNeeded;
      const loan = price - down5;
      const basePi = Math.round(calcMonthlyPI(loan, 6.0));
      const effHousing = basePi - subOffset;
      const monthlyBeat = rent - effHousing;

      // Update Phone 1
      document.getElementById('p1-rent-display').innerText = `$${{rent.toLocaleString()}} / month`;
      document.getElementById('p1-vault-display').innerText = `$${{vault.toLocaleString()}}.00`;
      document.getElementById('p1-vault-pct').innerText = reserves >= 0
        ? `Covers 5% Down ($${{down5.toLocaleString()}}) + Net Closing ($${{netClosing.toLocaleString()}}) with $${{reserves.toLocaleString()}} Reserve left!`
        : `Covers $${{vault.toLocaleString()}} toward $${{cashNeeded.toLocaleString()}} Cash to Close (Add $${{Math.abs(reserves).toLocaleString()}} to Vault).`;

      // Update Phone 2
      document.getElementById('p2-home-price').innerText = `$${{price.toLocaleString()}}`;
      document.getElementById('p2-piti-badge').innerText = `Net P&I: $${{effHousing.toLocaleString()}}/mo`;
      document.getElementById('p2-match-reason').innerHTML =
        `After $215/mo Rocket Money subscription savings, owning this Ferndale home costs <strong>$${{effHousing.toLocaleString()}}/mo</strong> (Base P&I $${{basePi.toLocaleString()}})—${{monthlyBeat >= 0 ? 'saving <strong>$' + monthlyBeat.toLocaleString() + '/mo</strong> vs' : 'within $' + Math.abs(monthlyBeat) + ' of'}} your $${{rent.toLocaleString()}} rent renewal!`;

      // Update Phone 3
      document.getElementById('p3-cash-to-close').innerText = `$${{cashNeeded.toLocaleString()}} Cash to Close`;
      document.getElementById('p3-cash-breakdown').innerHTML =
        `5% Down ($${{down5.toLocaleString()}}) + Net Closing ($${{netClosing.toLocaleString()}} after <strong>$3,500 Redfin × Rocket Credit</strong>).`;
      document.getElementById('p3-reserves-left').innerText = reserves >= 0
        ? `$${{reserves.toLocaleString()}}.00 Cushion Left`
        : `$${{Math.abs(reserves).toLocaleString()}} Vault Shortfall`;

      document.getElementById('mcp-Quick-Verdict').innerText =
        `Net P&I ($${{effHousing.toLocaleString()}}/mo) vs $${{rent.toLocaleString()}} Rent • $${{reserves.toLocaleString()}} Reserve Cushion`;

      try {{
        const resp = await fetch('/api/sandbox', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '4.5',
            action: 'calc_cross_funnel_mcp',
            params: {{ list_price: price, vault_balance: vault, bundle_credit: credit }}
          }})
        }});
        const data = await resp.json();
        if (data && data.ok) {{
          document.getElementById('mcp-latency-tag').innerText = `${{data.execution_ms || 1.2}}ms`;
        }}
      }} catch (e) {{}}
    }};

    window.runLiveVertexAI = async function() {{
      const btn = document.getElementById('btn-run-mcp');
      const orig = btn ? btn.innerText : '';
      if (btn) {{
        btn.innerText = '⏳ Antigravity MCP Fan-Out Running...';
        btn.disabled = true;
      }}
      window.pulseArrows();

      const rent = parseFloat(document.getElementById('inp-rent-hike').value || 2480);
      const vault = parseFloat(document.getElementById('inp-vault-bal').value || 31200);
      const price = parseFloat(document.getElementById('inp-target-home').value || 365000);
      const scenarioEl = document.getElementById('scenario-input');
      const promptText = scenarioEl && scenarioEl.value
        ? scenarioEl.value
        : `Synthesize a Redfin-to-Rocket cross-funnel pre-approval package for Maya Lin: Rent hiked to $${{rent}}/mo, Rocket Money Vault has $${{vault}}, touring $${{price}} home in Ferndale MI with $3,500 Buy+Borrow credit.`;

      try {{
        const resp = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '4.5',
            model: window.getSelectedModel(),
            user_input: promptText,
            params: {{ list_price: price, vault_balance: vault, bundle_credit: 3500 }}
          }})
        }});
        const res = await resp.json();
        if (res && res.ok) {{
          const sd = res.structured_data || {{}};
          const summaryText = sd.executive_summary || res.output || 'Verified Approval Certificate synced across Rocket Money, Redfin, and Rocket Mortgage.';
          document.getElementById('p3-ai-dossier').innerHTML = `
            <div class="mono" style="font-size:10px;color:#6EE7B7;margin-bottom:3px;">LIVE VERTEX AI (${{res.model_used}})</div>
            ${{summaryText}}
          `;
        }}
      }} catch (e) {{
        console.error(e);
      }} finally {{
        if (btn) {{
          btn.innerText = orig;
          btn.disabled = false;
        }}
      }}
    }};

    document.addEventListener('DOMContentLoaded', () => {{
      window.rippleMcpState();
    }});
  </script>

  {floating_drawer}
</body>
</html>"""
