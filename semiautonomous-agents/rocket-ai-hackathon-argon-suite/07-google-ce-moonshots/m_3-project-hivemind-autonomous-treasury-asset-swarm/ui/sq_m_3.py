# -*- coding: utf-8 -*-
"""Square M.3: Project HiveMind: Autonomous Treasury & Asset Swarm — Google ADK Runtime
Visual Design: Wall Street Bloomberg Terminal (#000000 pure black canvas, #FF9900 Bloomberg amber headers,
#00E5FF cyan, #00E676 ticker green, #FF1744 ticker red, strict IBM Plex Mono / JetBrains Mono high-density terminal layout).
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_m_3(auth_token: str) -> str:
    code = "M.3"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[M.3] Project HiveMind: Autonomous Treasury & MBS Swarm | Bloomberg Terminal</title>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bb-black: #000000;
      --bb-panel: #070707;
      --bb-amber: #FF9900;
      --bb-amber-bg: rgba(255, 153, 0, 0.14);
      --bb-cyan: #00E5FF;
      --bb-green: #00E676;
      --bb-red: #FF1744;
      --bb-border: #262626;
      --bb-text: #F5F5F5;
      --bb-muted: #8C8C8C;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: var(--bb-black);
      color: var(--bb-text);
      font-family: 'IBM Plex Mono', 'JetBrains Mono', monospace;
      min-height: 100vh;
      font-size: 12px;
      padding-bottom: 92px;
    }}

    /* Top Bloomberg Command Bar */
    .bb-cmd-bar {{
      background: #120B00;
      border-bottom: 2px solid var(--bb-amber);
      padding: 8px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .bb-fn-key {{
      background: var(--bb-amber);
      color: #000000;
      font-weight: 800;
      padding: 3px 8px;
      font-size: 11px;
      letter-spacing: 0.04em;
    }}
    .bb-model-select {{
      display: flex;
      align-items: center;
      gap: 6px;
      background: #000;
      border: 1px solid var(--bb-amber);
      padding: 4px 10px;
      font-size: 11px;
      color: var(--bb-amber);
    }}
    .bb-model-select select {{
      background: #000;
      color: var(--bb-cyan);
      border: none;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      outline: none;
      cursor: pointer;
    }}

    /* Live Flashing Treasury & UMBS Coupon Ticker Strip */
    .bb-ticker-strip {{
      background: #050505;
      border-bottom: 1px solid var(--bb-border);
      padding: 7px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 14px;
      font-size: 11.5px;
    }}
    .ticker-item {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 2px 8px;
      border: 1px solid #1C1C1C;
      background: #0A0A0A;
    }}
    .flash-green {{
      color: var(--bb-green);
      animation: pulseTicker 1.6s infinite;
    }}
    .flash-red {{
      color: var(--bb-red);
      animation: pulseTicker 1.6s infinite;
    }}
    @keyframes pulseTicker {{
      0%, 100% {{ opacity: 1; }}
      50% {{ opacity: 0.55; }}
    }}

    /* High-Density 4-Quadrant Bloomberg Grid */
    .bb-terminal-grid {{
      max-width: 1600px;
      margin: 12px auto;
      padding: 0 14px;
      display: grid;
      grid-template-columns: 390px 1fr;
      gap: 12px;
    }}
    @media (max-width: 1120px) {{
      .bb-terminal-grid {{ grid-template-columns: 1fr; }}
    }}

    .bb-window {{
      background: var(--bb-panel);
      border: 1px solid var(--bb-border);
      display: flex;
      flex-direction: column;
    }}
    .bb-win-header {{
      background: #1A1100;
      border-bottom: 1px solid var(--bb-amber);
      color: var(--bb-amber);
      padding: 6px 12px;
      font-size: 11.5px;
      font-weight: 700;
      display: flex;
      justify-content: space-between;
      align-items: center;
      text-transform: uppercase;
    }}
    .bb-win-body {{
      padding: 14px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}

    .bps-slider {{
      width: 100%;
      accent-color: var(--bb-amber);
      cursor: pointer;
    }}

    /* 4-Agent ADK Swarm Bus Cards */
    .swarm-bus-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 10px;
    }}
    @media (max-width: 1050px) {{
      .swarm-bus-grid {{ grid-template-columns: 1fr 1fr; }}
    }}
    .agent-node {{
      background: #000000;
      border: 1px solid var(--bb-border);
      border-top: 2px solid var(--bb-cyan);
      padding: 10px 12px;
    }}
    .agent-node.amber {{ border-top-color: var(--bb-amber); }}
    .agent-node.green {{ border-top-color: var(--bb-green); }}

    .bb-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 11.5px;
    }}
    .bb-table th {{
      background: #121212;
      color: var(--bb-amber);
      text-align: left;
      padding: 6px 8px;
      border-bottom: 1px solid var(--bb-amber);
      font-size: 10.5px;
      text-transform: uppercase;
    }}
    .bb-table td {{
      padding: 7px 8px;
      border-bottom: 1px solid #1C1C1C;
    }}

    .btn-execute-hedge {{
      width: 100%;
      padding: 12px 16px;
      background: var(--bb-amber);
      color: #000000;
      border: 2px solid #FFB74D;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 13px;
      font-weight: 800;
      cursor: pointer;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      transition: 0.12s;
    }}
    .btn-execute-hedge:hover {{
      background: var(--bb-green);
      border-color: var(--bb-green);
    }}
  </style>
</head>
<body>

  <!-- TOP BLOOMBERG COMMAND BAR -->
  <header class="bb-cmd-bar">
    <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
      <span class="bb-fn-key">&lt;GO&gt; RKT HIVEMIND // SQUARE [M.3]</span>
      <span style="color:var(--bb-amber);font-weight:700;">AUTONOMOUS TREASURY, TBA HEDGE & MR. COOPER RECAPTURE SWARM</span>
      <span style="color:var(--bb-cyan);">[GOOGLE ADK 4-AGENT BUS]</span>
    </div>
    <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
      <div class="bb-model-select">
        <span>SWARM MODEL:</span>
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)">
          <option value="gemini-4-argon">gemini-4-argon (Frontier Global)</option>
          <option value="gemini-3.8-flash" selected>gemini-3.8-flash (Fast / ADK Runtime)</option>
        </select>
      </div>
    </div>
  </header>

  <!-- FLASHING TREASURY & UMBS TICKER BAR -->
  <div class="bb-ticker-strip">
    <div class="ticker-item">
      <span style="color:var(--bb-amber);font-weight:700;">USGG10YR (10-YR TREASURY):</span>
      <strong id="tkr-10yr" class="flash-green">4.02% (-12 bps)</strong>
    </div>
    <div class="ticker-item">
      <span style="color:var(--bb-amber);font-weight:700;">FNCL 5.5 (UMBS 30Y 5.5 COUPON):</span>
      <strong id="tkr-umbs55" class="flash-green">99-24 (+0-14 / +43.7 bps)</strong>
    </div>
    <div class="ticker-item">
      <span style="color:var(--bb-amber);font-weight:700;">FNCL 6.0 (UMBS 30Y 6.0 COUPON):</span>
      <strong id="tkr-umbs60" class="flash-green">101-08 (+0-10 / +31.2 bps)</strong>
    </div>
    <div class="ticker-item">
      <span style="color:var(--bb-amber);font-weight:700;">RKT 30Y PAR SHEET:</span>
      <strong id="tkr-par" style="color:var(--bb-cyan);">5.750% (UNLOCKED)</strong>
    </div>
  </div>

  <!-- MAIN HIGH-DENSITY BLOOMBERG WORKSPACE -->
  <main class="bb-terminal-grid">

    <!-- LEFT WINDOW: BASIS-POINT RATE SHOCK SIMULATOR & TRADE TICKET -->
    <aside class="bb-window">
      <div class="bb-win-header">
        <span>1. BASIS-POINT RATE SHOCK SIMULATOR</span>
        <span style="color:var(--bb-cyan);">[-50 TO +50 BPS]</span>
      </div>
      <div class="bb-win-body">
        <p style="color:var(--bb-muted);line-height:1.5;">
          Simulate an intraday 10-Year US Treasury shock (`-50 bps` rally to `+50 bps` selloff). Calls <code>/api/sandbox</code> (`calc_hivemind_hedge` / `simulate_hivemind_swarm`) to recompute UMBS TBA hedge delta and Mr. Cooper refi recapture cohort.
        </p>

        <div style="background:#000;border:1px solid var(--bb-border);padding:12px;">
          <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
            <span style="color:var(--bb-amber);">INTRADAY 10Y TREASURY SHOCK:</span>
            <strong id="lbl-shock-bps" style="color:var(--bb-green);font-size:14px;">-12 bps (Rally)</strong>
          </div>
          <input type="range" id="sld-shock-bps" class="bps-slider" min="-50" max="50" step="2" value="-12" oninput="recalcHiveMindTerminal()">
          <div style="display:flex;justify-content:space-between;font-size:10px;color:var(--bb-muted);margin-top:4px;">
            <span>-50 bps (3.64% 10Y)</span>
            <span>0 bps (4.14%)</span>
            <span>+50 bps (4.64% 10Y)</span>
          </div>
        </div>

        <div style="background:#000;border:1px solid var(--bb-border);padding:12px;">
          <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
            <span style="color:var(--bb-amber);">MR. COOPER COHORT SIZE:</span>
            <strong id="lbl-cohort" style="color:var(--bb-cyan);">1,240 Loans</strong>
          </div>
          <input type="range" id="sld-cohort" class="bps-slider" min="400" max="3000" step="40" value="1240" oninput="recalcHiveMindTerminal()">
        </div>

        <div style="background:#000;border:1px solid var(--bb-border);padding:12px;">
          <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
            <span style="color:var(--bb-amber);">4-HR 1-TAP LOCK CONVERSION:</span>
            <strong id="lbl-conv" style="color:var(--bb-green);">28.6%</strong>
          </div>
          <input type="range" id="sld-conv" class="bps-slider" min="10" max="50" step="0.5" value="28.6" oninput="recalcHiveMindTerminal()">
        </div>

        <button class="btn-execute-hedge" onclick="executeUmbsHedgeBlotter()">
          [EXECUTE $142M UMBS TBA HEDGE]
        </button>

        <button onclick="window.runLiveVertexAI()" style="width:100%;padding:9px;background:#000;border:1px solid var(--bb-cyan);color:var(--bb-cyan);font-family:'IBM Plex Mono',monospace;font-weight:700;cursor:pointer;">
          ⚡ RUN 4-AGENT ADK SWARM BRIEF (/api/run-demo)
        </button>
      </div>
    </aside>

    <!-- RIGHT WINDOW: 4-AGENT ADK SWARM COMMUNICATION BUS & TBA HEDGE BLOTTER -->
    <section style="display:flex;flex-direction:column;gap:12px;">

      <!-- 4-AGENT ADK SWARM COMMUNICATION BUS -->
      <div class="bb-window">
        <div class="bb-win-header">
          <span>2. GOOGLE ADK 4-AGENT SWARM COMMUNICATION BUS (MACRO → PREPAYMENT → HEDGE → PRICE)</span>
          <span id="swarm-speed-pill" style="color:var(--bb-green);">LATENCY: 2.84s E2E</span>
        </div>
        <div class="bb-win-body">
          <div class="swarm-bus-grid">
            <div class="agent-node amber">
              <div style="color:var(--bb-amber);font-weight:700;font-size:11px;">[1. MACRO AGENT]</div>
              <div style="color:var(--bb-cyan);font-size:10px;margin:2px 0 6px;">gemini-3.8-flash</div>
              <div id="bus-macro" style="font-size:11px;line-height:1.45;">
                10Y Treasury yield dropped -12 bps to 4.02%. UMBS 5.5 coupon rallied +14/32nds to 99-24.
              </div>
            </div>

            <div class="agent-node">
              <div style="color:var(--bb-cyan);font-weight:700;font-size:11px;">[2. PREPAYMENT CPR AGENT]</div>
              <div style="color:var(--bb-muted);font-size:10px;margin:2px 0 6px;">BigQuery 4.2M Servicing</div>
              <div id="bus-prepay" style="font-size:11px;line-height:1.45;">
                Filtered 1,240 Mr. Cooper households (>6.75% note rate, >=22% equity) with CPR jump to 26.4%.
              </div>
            </div>

            <div class="agent-node green">
              <div style="color:var(--bb-green);font-weight:700;font-size:11px;">[3. TBA HEDGE AGENT]</div>
              <div style="color:var(--bb-muted);font-size:10px;margin:2px 0 6px;">Duration & Convexity Desk</div>
              <div id="bus-hedge" style="font-size:11px;line-height:1.45;">
                Staged $142,000,000 Short FNCL 5.5 Forward TBA Hedge to lock pipeline pull-through margin.
              </div>
            </div>

            <div class="agent-node amber">
              <div style="color:var(--bb-amber);font-weight:700;font-size:11px;">[4. PRICE & PUSH AGENT]</div>
              <div style="color:var(--bb-muted);font-size:10px;margin:2px 0 6px;">AUS + DU Waiver Batch</div>
              <div id="bus-price" style="font-size:11px;line-height:1.45;">
                Published 5.750% 1-Tap Refi Lock to Rocket Money & Mr. Cooper apps (-$293.43/mo savings).
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- UMBS TBA HEDGE EXECUTION BLOTTER TABLE -->
      <div class="bb-window">
        <div class="bb-win-header">
          <span>3. CAPITAL MARKETS TBA HEDGE & RECAPTURE EXECUTION BLOTTER</span>
          <span id="blotter-status-tag" style="color:var(--bb-amber);">STATUS: STAGED FOR DESK EXECUTION</span>
        </div>
        <div class="bb-win-body">
          <table class="bb-table">
            <thead>
              <tr>
                <th>Desk / Instrument</th>
                <th>Coupon / Benchmark</th>
                <th>Notional Volume</th>
                <th>DV01 / Hedge Ratio</th>
                <th>Household Impact</th>
                <th>Execution State</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style="color:var(--bb-amber);font-weight:700;">UMBS 30Y TBA FORWARD</td>
                <td>FNCL 5.5% Nov Settle</td>
                <td id="tbl-notional" style="color:var(--bb-green);font-weight:700;">$142,000,000</td>
                <td id="tbl-dv01">-$68,160 / bp (0.94 HR)</td>
                <td>Protects 355 Locked Refis</td>
                <td id="tbl-state-1" style="color:var(--bb-cyan);">READY TO EXECUTE</td>
              </tr>
              <tr>
                <td style="color:var(--bb-amber);font-weight:700;">MR. COOPER RECAPTURE</td>
                <td>6.875% → 5.750% Streamline</td>
                <td id="tbl-recap-vol" style="color:var(--bb-cyan);font-weight:700;">$142,000,000 (355 Locks)</td>
                <td>DU Appraisal Waiver (100%)</td>
                <td id="tbl-hh-sav" style="color:var(--bb-green);">-$293.43/mo ($3,521/yr)</td>
                <td id="tbl-state-2" style="color:var(--bb-green);">PUSH DISPATCHED</td>
              </tr>
              <tr>
                <td style="color:var(--bb-amber);font-weight:700;">MSR SERVICING HEDGE</td>
                <td>10Y SOFR Receiver Swap</td>
                <td>$45,000,000 Notional</td>
                <td>+$21,400 / bp Offset</td>
                <td>Zero Net Runoff Loss</td>
                <td style="color:var(--bb-green);">HEDGED</td>
              </tr>
            </tbody>
          </table>

          <div id="bb-audit-console" style="background:#000;border:1px solid var(--bb-amber);padding:12px;color:var(--bb-text);line-height:1.6;">
            <span style="color:var(--bb-amber);font-weight:700;">[BLOOMBERG // ADK SWARM TELEMETRY]:</span> Ready. Drag the Basis-Point Rate Shock slider or click <strong>[EXECUTE $142M UMBS TBA HEDGE]</strong> to lock the TBA forward blotter.
          </div>
        </div>
      </div>

    </section>

  </main>

  <script>
    async function recalcHiveMindTerminal() {{
      const shockBps = parseInt(document.getElementById('sld-shock-bps').value || -12);
      const cohort = parseInt(document.getElementById('sld-cohort').value || 1240);
      const convPct = parseFloat(document.getElementById('sld-conv').value || 28.6);

      const new10Yr = (4.14 + shockBps / 100.0).toFixed(2);
      const newParRate = Math.max(4.875, Math.min(6.750, 5.875 + (shockBps / 100.0))).toFixed(3);
      const lockedCount = Math.round(cohort * (convPct / 100.0));
      const lockedVol = lockedCount * 400000;

      document.getElementById('lbl-shock-bps').innerText = (shockBps >= 0 ? '+' : '') + shockBps + ' bps ' + (shockBps <= 0 ? '(Rally)' : '(Selloff)');
      document.getElementById('lbl-shock-bps').style.color = shockBps <= 0 ? '#00E676' : '#FF1744';
      document.getElementById('lbl-cohort').innerText = cohort.toLocaleString() + ' Loans';
      document.getElementById('lbl-conv').innerText = convPct.toFixed(1) + '%';

      document.getElementById('tkr-10yr').innerText = `${'{'}new10Yr{'}'}% (${'{'}shockBps >= 0 ? '+' : ''{'}'}${'{'}shockBps{'}'} bps)`;
      document.getElementById('tkr-par').innerText = `${'{'}newParRate{'}'}% (${'{'}shockBps <= 0 ? 'RALLY WINDOW' : 'DEFENSIVE'{'}'})`;

      document.getElementById('tbl-notional').innerText = '$' + lockedVol.toLocaleString();
      document.getElementById('tbl-recap-vol').innerText = `$${'{'}lockedVol.toLocaleString(){'}'} (${'{'}lockedCount{'}'} Locks)`;
      document.getElementById('bus-macro').innerText = `10Y Treasury shifted ${'{'}shockBps{'}'} bps to ${'{'}new10Yr{'}'}%. Rocket Par sheet repriced to ${'{'}newParRate{'}'}%.`;
      document.getElementById('bus-hedge').innerText = `Staged $${'{'}lockedVol.toLocaleString(){'}'} Short FNCL 5.5/6.0 TBA Forward Hedge across ${'{'}lockedCount{'}'} locks.`;

      try {{
        const res = await fetch('/api/sandbox', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: 'M.3',
            action: 'simulate_hivemind_swarm',
            params: {{
              secondary_action: 'calc_hivemind_hedge',
              rate_shock_bps: shockBps,
              cohort_size: cohort,
              avg_loan: 400000,
              conversion_pct: convPct
            }}
          }})
        }});
        const data = await res.json();
        document.getElementById('swarm-speed-pill').innerText = `SANDBOX: ${'{'}data.execution_ms || 1.2{'}'}ms • SWARM: 2.84s`;
      }} catch (e) {{}}
    }}

    function executeUmbsHedgeBlotter() {{
      const notional = document.getElementById('tbl-notional').innerText;
      document.getElementById('blotter-status-tag').innerText = 'STATUS: FILLED @ JP MORGAN / TRADEWEB TBA DESK';
      document.getElementById('blotter-status-tag').style.color = '#00E676';
      document.getElementById('tbl-state-1').innerText = '✅ FILLED @ 99-24';
      document.getElementById('tbl-state-1').style.color = '#00E676';
      document.getElementById('bb-audit-console').innerHTML = `
        <span style="color:#00E676;font-weight:700;">[TRADE CONFIRMED // TICKET #TBA-994821]:</span> Executed <strong>${'{'}notional{'}'} UMBS 5.5 TBA Forward Sale</strong> on TradeWeb in 38ms. Pipeline pull-through delta hedged at 94.2% efficiency; 1-Tap Refi offers live in Rocket Money & Mr. Cooper mobile apps.
      `;
    }}

    window.runLiveVertexAI = async function() {{
      const model = window.getSelectedModel ? window.getSelectedModel() : 'gemini-3.8-flash';
      const shockBps = parseInt(document.getElementById('sld-shock-bps').value || -12);
      const cohort = parseInt(document.getElementById('sld-cohort').value || 1240);
      const convPct = parseFloat(document.getElementById('sld-conv').value || 28.6);
      const consoleEl = document.getElementById('bb-audit-console');
      consoleEl.innerHTML = `<span style="color:var(--bb-amber);">[EXECUTING GOOGLE ADK 4-AGENT SWARM ON ${'{'}model{'}'}]...</span>`;

      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: 'M.3',
            model: model,
            user_input: `Simulate a ${'{'}shockBps{'}'} bps 10-Yr Treasury shock across ${'{'}cohort{'}'} Mr. Cooper loans and execute the $142M UMBS TBA Forward Hedge.`,
            params: {{ cohort_size: cohort, avg_loan: 400000, conversion_pct: convPct }}
          }})
        }});
        const data = await res.json();
        consoleEl.innerHTML = `<span style="color:var(--bb-amber);font-weight:700;">[${'{'}data.model_used || model{'}'} // ADK TREASURY SWARM]:</span> ${'{'}data.output || 'TBA Hedge executed.'{'}'}`;
      }} catch (e) {{
        consoleEl.innerText = "ADK Swarm Error: " + e.message;
      }}
    }};

    document.addEventListener('DOMContentLoaded', () => {{
      recalcHiveMindTerminal();
    }});
  </script>

  {render_floating_control_bar_and_drawer(code, auth_token)}
</body>
</html>"""
