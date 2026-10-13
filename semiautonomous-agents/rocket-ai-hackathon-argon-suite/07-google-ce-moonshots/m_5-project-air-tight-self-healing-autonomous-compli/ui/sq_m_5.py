# -*- coding: utf-8 -*-
"""Square M.5: Project Pulse: Macro Treasury & Refi-Wave Simulator ($2.1T Servicing Portfolio)
Visual Design: Goldman Sachs / Bloomberg Global Macro Institutional Research Note
(#FFFFFF crisp institutional white paper, #0A2540 deep institutional navy header rule,
#0066CC research blue charts, #F8FAFC table tint, Playfair Display masthead + Public Sans & tabular numerals).
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_m_5(auth_token: str) -> str:
    code = "M.5"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[M.5] Project Pulse: Macro Treasury & Refi-Wave Simulator | Institutional Research Note</title>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,600&family=Public+Sans:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --inst-white: #FFFFFF;
      --inst-tint: #F8FAFC;
      --inst-navy: #0A2540;
      --research-blue: #0066CC;
      --research-blue-soft: #EFF6FF;
      --inst-emerald: #047857;
      --inst-amber: #B45309;
      --inst-ink: #0F172A;
      --inst-muted: #475569;
      --inst-border: #CBD5E1;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: var(--inst-white);
      color: var(--inst-ink);
      font-family: 'Public Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      font-variant-numeric: tabular-nums;
      min-height: 100vh;
      padding-bottom: 96px;
    }}
    .serif-inst {{ font-family: 'Playfair Display', Georgia, serif; }}
    .mono {{ font-family: 'IBM Plex Mono', monospace; }}

    /* Goldman Sachs / Institutional Global Macro Research Masthead */
    .inst-header {{
      background: var(--inst-white);
      border-top: 6px solid var(--inst-navy);
      border-bottom: 2px solid var(--inst-navy);
      padding: 18px 28px;
    }}
    .inst-header-inner {{
      max-width: 1540px;
      margin: 0 auto;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 16px;
    }}
    .inst-tag {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: var(--inst-navy);
      color: #FFFFFF;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      padding: 4px 10px;
      letter-spacing: 0.05em;
      text-transform: uppercase;
    }}
    .inst-select-box {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: var(--inst-tint);
      border: 1px solid var(--inst-border);
      padding: 6px 12px;
      border-radius: 4px;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11.5px;
    }}
    .inst-select-box select {{
      background: transparent;
      color: var(--inst-navy);
      border: none;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11.5px;
      font-weight: 700;
      outline: none;
      cursor: pointer;
    }}

    /* Institutional Note Grid */
    .macro-grid {{
      max-width: 1540px;
      margin: 24px auto;
      padding: 0 28px;
      display: grid;
      grid-template-columns: 420px 1fr;
      gap: 26px;
      align-items: start;
    }}
    @media (max-width: 1140px) {{
      .macro-grid {{ grid-template-columns: 1fr; }}
    }}

    .inst-card {{
      background: var(--inst-white);
      border: 1px solid var(--inst-border);
      border-top: 3px solid var(--inst-navy);
      padding: 22px;
      box-shadow: 0 4px 14px rgba(10, 37, 64, 0.04);
    }}

    /* Treasury Shock Slider Box */
    .shock-box {{
      background: var(--inst-tint);
      border: 1px solid var(--inst-border);
      padding: 16px;
      margin-bottom: 16px;
    }}
    input[type="range"] {{
      width: 100%;
      accent-color: var(--research-blue);
      cursor: pointer;
    }}

    /* Chief Economist Audio Briefing Button */
    .econ-audio-btn {{
      width: 100%;
      background: var(--inst-navy);
      color: #FFFFFF;
      border: none;
      padding: 13px 16px;
      font-family: 'Public Sans', sans-serif;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      transition: background 0.15s;
    }}
    .econ-audio-btn:hover {{
      background: var(--research-blue);
    }}

    /* Institutional KPI Table Strip */
    .macro-kpi-strip {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 14px;
      margin-bottom: 20px;
    }}
    @media (max-width: 920px) {{
      .macro-kpi-strip {{ grid-template-columns: 1fr 1fr; }}
    }}
    .macro-kpi-cell {{
      background: var(--inst-tint);
      border: 1px solid var(--inst-border);
      border-left: 3px solid var(--research-blue);
      padding: 13px 14px;
    }}

    /* Institutional Staffing & Warehouse Liquidity Table */
    .inst-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 12.5px;
      margin-top: 10px;
    }}
    .inst-table th {{
      background: var(--inst-navy);
      color: #FFFFFF;
      text-align: left;
      padding: 9px 12px;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11px;
      text-transform: uppercase;
    }}
    .inst-table td {{
      padding: 10px 12px;
      border-bottom: 1px solid #E2E8F0;
    }}
    .inst-table tr:nth-child(even) {{
      background: var(--inst-tint);
    }}
  </style>
</head>
<body>

  <!-- GOLDMAN SACHS / BLOOMBERG GLOBAL MACRO INSTITUTIONAL RESEARCH MASTHEAD -->
  <header class="inst-header">
    <div class="inst-header-inner">
      <div>
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;flex-wrap:wrap;">
          <span class="inst-tag">GLOBAL MACRO &amp; CAPITAL MARKETS RESEARCH • USE CASE M.5</span>
          <span class="mono" style="font-size:11px;color:var(--inst-muted);font-weight:600;">
            MR. COOPER + ROCKET COMBINED SERVICING BOOK • $2.10 TRILLION UPB (9.5M LOANS)
          </span>
        </div>
        <h1 class="serif-inst" style="font-size:26px;font-weight:800;color:var(--inst-navy);letter-spacing:-0.01em;">
          Project Pulse: Macro Treasury &amp; Refi-Wave Simulator ($2.1T Servicing Portfolio)
        </h1>
      </div>

      <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
        <div class="inst-select-box">
          <span style="color:var(--inst-muted);font-weight:600;">MODEL:</span>
          <select id="app-model-select" onchange="window.syncSelectedModel(this.value)" aria-label="Select Gemini Model">
            <option value="gemini-4-argon" selected>gemini-4-argon (Frontier Macro Econometrics)</option>
            <option value="gemini-3.8-flash">gemini-3.8-flash (Real-Time Desk Simulation)</option>
          </select>
        </div>
        <button onclick="window.runLiveVertexAI()" style="background:var(--research-blue);color:#FFFFFF;border:none;padding:8px 14px;font-family:'IBM Plex Mono',monospace;font-size:12px;font-weight:700;cursor:pointer;">
          Publish Desk Note
        </button>
      </div>
    </div>
  </header>

  <!-- MAIN INSTITUTIONAL MACRO WORKSPACE -->
  <main class="macro-grid">

    <!-- LEFT COLUMN: FED RATE CUT / 10-YR TREASURY SHOCK SLIDER & LIQUIDITY PLANNER -->
    <aside class="inst-card">
      <div style="border-bottom:1px solid var(--inst-border);padding-bottom:10px;margin-bottom:14px;">
        <div class="mono" style="font-size:11px;font-weight:700;color:var(--research-blue);text-transform:uppercase;">
          FOMC &amp; 10-YEAR TREASURY YIELD SHOCK SIMULATOR
        </div>
        <h2 class="serif-inst" style="font-size:19px;font-weight:700;color:var(--inst-navy);margin-top:2px;">
          Interactive Rate-Cut Elasticity &amp; Prepayment Speeds
        </h2>
        <p style="font-size:12.5px;color:var(--inst-muted);margin-top:4px;line-height:1.45;">
          Simulate instantaneous shifts in the 10-Year US Treasury and 30-Year UMBS par coupon across Rocket + Mr. Cooper's 9.5 million serviced mortgages.
        </p>
      </div>

      <!-- Interactive Federal Reserve Rate Cut / 10-Yr Treasury Shock Slider (-150 bps to +50 bps) -->
      <div class="shock-box">
        <div style="display:flex;justify-content:space-between;align-items:center;font-size:12.5px;font-weight:700;margin-bottom:8px;">
          <span>Fed / 10-Yr Treasury Yield Shock</span>
          <span class="mono" id="lbl-bps-shock" style="background:var(--inst-navy);color:#FFFFFF;padding:3px 8px;font-size:12px;">-75 bps Shock</span>
        </div>
        <input type="range" id="sld-bps-shock" min="-150" max="50" step="25" value="-75" oninput="window.updateMacroPulseSimulator()">
        <div class="mono" style="display:flex;justify-content:space-between;font-size:10px;color:var(--inst-muted);margin-top:6px;">
          <span>-150 bps (Bull Rally)</span>
          <span>-75 bps (Base Cut)</span>
          <span>0 bps (Unchanged)</span>
          <span>+50 bps (Bear Selloff)</span>
        </div>
      </div>

      <div class="shock-box">
        <div style="display:flex;justify-content:space-between;align-items:center;font-size:12.5px;font-weight:700;margin-bottom:8px;">
          <span>AI Voice &amp; Digital Recapture Rate (%)</span>
          <span class="mono" id="lbl-recap-rate" style="color:var(--research-blue);font-weight:700;">83.0% Target</span>
        </div>
        <input type="range" id="sld-recap-rate" min="50" max="92" step="1" value="83" oninput="window.updateMacroPulseSimulator()">
      </div>

      <!-- Staffing & Warehouse Line Liquidity Planner -->
      <div style="margin-bottom:16px;">
        <div class="mono" style="font-size:11px;font-weight:700;color:var(--inst-navy);text-transform:uppercase;margin-bottom:6px;">
          Staffing &amp; Warehouse Line Liquidity Planner
        </div>
        <table class="inst-table">
          <thead>
            <tr>
              <th>Operational Desk</th>
              <th>Required Capacity</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Warehouse Repo Lines</strong></td>
              <td class="mono" id="tbl-warehouse">$18.4B Facility</td>
              <td class="mono" style="color:var(--inst-emerald);font-weight:700;">PRE-FUNDED</td>
            </tr>
            <tr>
              <td><strong>Licensed Loan Officers</strong></td>
              <td class="mono" id="tbl-bankers">2,420 + AI Voice</td>
              <td class="mono" style="color:var(--research-blue);font-weight:700;">AUTOSCALED</td>
            </tr>
            <tr>
              <td><strong>MSR Hedge Offset (Gain-on-Sale)</strong></td>
              <td class="mono" id="tbl-msr-hedge">+$612M Net Gain</td>
              <td class="mono" style="color:var(--inst-emerald);font-weight:700;">DELTA-NEUTRAL</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Chief Economist Morning Call Audio Briefing -->
      <div style="display:flex;flex-direction:column;gap:8px;">
        <button id="btn-pulse-audio" class="econ-audio-btn" onclick="window.playChiefEconomistCall(this)">
          🔊 Listen to Chief Economist Morning Call (Gemini 3.8 Live · Kore HD)
        </button>
        <button onclick="window.stopAllLiveAudio && window.stopAllLiveAudio()" style="background:var(--inst-tint);border:1px solid var(--inst-border);color:var(--inst-muted);padding:7px;font-family:'IBM Plex Mono',monospace;font-size:11px;font-weight:600;cursor:pointer;">
          ✋ Interrupt / Stop Morning Call Audio (0ms Barge-In)
        </button>
      </div>
    </aside>

    <!-- RIGHT COLUMN: 7-COHORT WAC DISTRIBUTION BAR CHART & INSTITUTIONAL DESK NOTE -->
    <section style="display:flex;flex-direction:column;gap:20px;">
      <div class="inst-card">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid var(--inst-border);">
          <div>
            <span class="mono" style="font-size:11px;font-weight:700;color:var(--research-blue);text-transform:uppercase;">
              EXHIBIT 1: 7-COHORT WAC DISTRIBUTION ACROSS $2.1T SERVICING PORTFOLIO (3.0% TO 7.5%+)
            </span>
            <h2 class="serif-inst" style="font-size:22px;font-weight:800;color:var(--inst-navy);margin-top:2px;">
              In-The-Money (ITM) Refinance Strike Threshold &amp; Recapture Volume
            </h2>
          </div>
          <span class="mono" id="implied-30yr-pill" style="background:var(--research-blue-soft);border:1px solid #93C5FD;color:var(--research-blue);padding:5px 12px;font-size:11.5px;font-weight:700;">
            Implied 30-Yr Par Rate: 5.50%
          </span>
        </div>

        <!-- 4 Macro Institutional KPIs -->
        <div class="macro-kpi-strip">
          <div class="macro-kpi-cell">
            <div class="mono" style="font-size:10px;color:var(--inst-muted);">IMPLIED 30-YR MORTGAGE RATE</div>
            <div class="serif-inst" id="kpi-macro-rate" style="font-size:22px;font-weight:800;color:var(--inst-navy);margin-top:2px;">5.50% Par</div>
            <div class="mono" style="font-size:10.5px;color:var(--research-blue);margin-top:2px;">After -75 bps Treasury Shift</div>
          </div>
          <div class="macro-kpi-cell">
            <div class="mono" style="font-size:10px;color:var(--inst-muted);">IN-THE-MONEY (ITM) LOANS</div>
            <div class="serif-inst" id="kpi-macro-itm" style="font-size:22px;font-weight:800;color:var(--research-blue);margin-top:2px;">2.18M Loans</div>
            <div class="mono" style="font-size:10.5px;color:var(--inst-muted);margin-top:2px;">&ge; 75 bps Rate Drop Incentive</div>
          </div>
          <div class="macro-kpi-cell">
            <div class="mono" style="font-size:10px;color:var(--inst-muted);">PROJECTED 90-DAY REFI locks</div>
            <div class="serif-inst" id="kpi-macro-vol" style="font-size:22px;font-weight:800;color:var(--inst-emerald);margin-top:2px;">$54.8B UPB</div>
            <div class="mono" style="font-size:10.5px;color:var(--inst-emerald);margin-top:2px;">Recaptured Inside Ecosystem</div>
          </div>
          <div class="macro-kpi-cell">
            <div class="mono" style="font-size:10px;color:var(--inst-muted);">MSR RUNOFF VS. ORIGINATION GAIN</div>
            <div class="serif-inst" id="kpi-macro-net" style="font-size:22px;font-weight:800;color:var(--inst-navy);margin-top:2px;">+$612M Net</div>
            <div class="mono" style="font-size:10.5px;color:var(--inst-muted);margin-top:2px;">Natural Servicing-to-Origination Hedge</div>
          </div>
        </div>

        <!-- 7-Cohort WAC Distribution SVG Bar Chart (3.0% to 7.5%+) -->
        <div style="background:var(--inst-tint);border:1px solid var(--inst-border);padding:16px;">
          <svg id="pulse-wac-svg" viewBox="0 0 880 300" style="width:100%;height:auto;display:block;"></svg>
        </div>
      </div>

      <!-- Institutional Desk Research Note Commentary -->
      <div class="inst-card" style="background:var(--inst-tint);">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;flex-wrap:wrap;gap:8px;">
          <span class="mono" style="font-size:11.5px;font-weight:700;color:var(--inst-navy);">
            CHIEF ECONOMIST &amp; CAPITAL MARKETS DESK NOTE • GEMINI 3.8 LIVE (KORE HD)
          </span>
          <span class="mono" style="font-size:11px;color:var(--research-blue);font-weight:700;">
            TBA UMBS Hedge Desk • Warehouse Liquidity Verified
          </span>
        </div>
        <div id="pulse-research-note" style="font-size:14px;line-height:1.65;color:var(--inst-ink);">
          <strong>[Global Macro Treasury Desk Note]:</strong> Under a <strong>-75 bps</strong> Federal Reserve and 10-Year Treasury rally, the primary 30-year fixed par rate compresses to <strong>5.50%</strong>. Across the combined Rocket + Mr. Cooper <strong>$2.1 Trillion (9.5M-loan)</strong> servicing portfolio, every cohort with a Weighted Average Coupon (WAC) of <strong>6.25% to 7.50%+</strong> immediately crosses the 75 bps In-The-Money refinance threshold—unlocking <strong>2.18 million households</strong> and <strong>$54.8B in 90-day recaptured origination volume</strong> at an 83% AI-assisted recapture rate, more than offsetting MSR prepayment runoff by <strong>+$612M</strong>.
        </div>
      </div>
    </section>

  </main>

  <script>
    // 7-Cohort WAC Distribution across $2.1T Servicing Portfolio (in $ Billions UPB)
    const WAC_COHORTS = [
      {{ label: "3.0–3.75%", wac: 3.38, upbB: 520, loansM: 2.45 }},
      {{ label: "4.0–4.75%", wac: 4.38, upbB: 340, loansM: 1.55 }},
      {{ label: "5.0–5.50%", wac: 5.25, upbB: 280, loansM: 1.25 }},
      {{ label: "5.75–6.25%", wac: 6.00, upbB: 310, loansM: 1.38 }},
      {{ label: "6.50–6.875%", wac: 6.68, upbB: 295, loansM: 1.31 }},
      {{ label: "7.00–7.375%", wac: 7.18, upbB: 215, loansM: 0.96 }},
      {{ label: "7.50%+", wac: 7.75, upbB: 140, loansM: 0.60 }}
    ];

    window.updateMacroPulseSimulator = async function() {{
      const shockBps = parseInt(document.getElementById('sld-bps-shock').value || -75, 10);
      const recapPct = parseFloat(document.getElementById('sld-recap-rate').value || 83);

      const baseRate = 6.25;
      const newRate = Math.max(4.50, (baseRate + shockBps / 100.0)).toFixed(2);
      const strikeWac = parseFloat(newRate) + 0.70; // 70 bps incentive threshold

      const sign = shockBps > 0 ? '+' : '';
      document.getElementById('lbl-bps-shock').innerText = `${{sign}}${{shockBps}} bps Shock`;
      document.getElementById('lbl-recap-rate').innerText = `${{recapPct.toFixed(1)}}% Target`;
      document.getElementById('implied-30yr-pill').innerText = `Implied 30-Yr Par Rate: ${{newRate}}%`;
      document.getElementById('kpi-macro-rate').innerText = `${{newRate}}% Par`;

      let itmLoansM = 0;
      let itmUpbB = 0;
      WAC_COHORTS.forEach(c => {{
        if (c.wac >= strikeWac) {{
          itmLoansM += c.loansM;
          itmUpbB += c.upbB;
        }}
      }});

      const locked90dB = Math.max(4.2, (itmUpbB * (recapPct / 100.0) * 0.102)).toFixed(1);
      const warehouseNeedB = Math.max(6.0, (parseFloat(locked90dB) * 0.335)).toFixed(1);
      const netGainM = Math.round(parseFloat(locked90dB) * 11.2);
      const bankersReq = Math.round(1650 + parseFloat(locked90dB) * 14);

      document.getElementById('kpi-macro-itm').innerText = `${{itmLoansM.toFixed(2)}}M Loans`;
      document.getElementById('kpi-macro-vol').innerText = `$${{locked90dB}}B UPB`;
      document.getElementById('kpi-macro-net').innerText = `+$${{netGainM}}M Net`;

      document.getElementById('tbl-warehouse').innerText = `$${{warehouseNeedB}}B Facility`;
      document.getElementById('tbl-bankers').innerText = `${{bankersReq.toLocaleString()}} + AI Voice`;
      document.getElementById('tbl-msr-hedge').innerText = `+$${{netGainM}}M Net Gain`;

      // Render 7-Cohort WAC Distribution SVG Bar Chart
      const svg = document.getElementById('pulse-wac-svg');
      const x0 = 65, y0 = 25, y1 = 245;
      const barW = 82;
      const gap = 28;
      let barsHtml = '';

      WAC_COHORTS.forEach((c, idx) => {{
        const bx = x0 + idx * (barW + gap);
        const bh = Math.round((c.upbB / 560) * (y1 - y0));
        const by = y1 - bh;
        const isItm = c.wac >= strikeWac;
        const fill = isItm ? '#0066CC' : '#94A3B8';
        const badge = isItm ? 'IN-THE-MONEY' : 'LOCKED-IN';
        const badgeColor = isItm ? '#0066CC' : '#64748B';

        barsHtml += `
          <g>
            <rect x="${{bx}}" y="${{by}}" width="${{barW}}" height="${{bh}}" rx="3" fill="${{fill}}"/>
            <text x="${{bx + barW/2}}" y="${{by - 18}}" fill="${{badgeColor}}" font-family="IBM Plex Mono" font-size="9.5" font-weight="700" text-anchor="middle">${{badge}}</text>
            <text x="${{bx + barW/2}}" y="${{by - 5}}" fill="#0A2540" font-family="IBM Plex Mono" font-size="11.5" font-weight="700" text-anchor="middle">$${{c.upbB}}B</text>
            <text x="${{bx + barW/2}}" y="${{y1 + 18}}" fill="#0F172A" font-family="IBM Plex Mono" font-size="11" font-weight="700" text-anchor="middle">${{c.label}}</text>
            <text x="${{bx + barW/2}}" y="${{y1 + 34}}" fill="#475569" font-family="Public Sans" font-size="10.5" text-anchor="middle">${{c.loansM}}M Loans</text>
          </g>
        `;
      }});

      svg.innerHTML = `
        <line x1="50" y1="${{y1}}" x2="850" y2="${{y1}}" stroke="#0A2540" stroke-width="2"/>
        <line x1="50" y1="${{y0}}" x2="50" y2="${{y1}}" stroke="#CBD5E1" stroke-width="1.5"/>
        ${{barsHtml}}
      `;

      document.getElementById('pulse-research-note').innerHTML =
        `<strong>[Global Macro Treasury Desk Note]:</strong> Under a <strong>${{sign}}${{shockBps}} bps</strong> Treasury shift, the 30-year par mortgage rate moves to <strong>${{newRate}}%</strong> (strike WAC <strong>${{strikeWac.toFixed(2)}}%</strong>). Across the <strong>$2.1T</strong> servicing book, <strong>${{itmLoansM.toFixed(2)}}M loans ($${{itmUpbB}}B UPB)</strong> are immediately In-The-Money—generating <strong>$${{locked90dB}}B</strong> in 90-day recaptured volume at a <strong>${{recapPct.toFixed(0)}}%</strong> recapture rate and <strong>+$${{netGainM}}M</strong> in net origination-over-MSR hedge gain.`;

      try {{
        await fetch('/api/sandbox', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: 'M.5',
            action: 'simulate_hivemind_swarm',
            params: {{ cohort_size: Math.round(itmLoansM * 1000), avg_loan: 400000, conversion_pct: recapPct }}
          }})
        }});
      }} catch (e) {{}}
    }};

    window.playChiefEconomistCall = function(btnEl) {{
      const shockBps = document.getElementById('lbl-bps-shock').innerText;
      const rate = document.getElementById('kpi-macro-rate').innerText;
      const itm = document.getElementById('kpi-macro-itm').innerText;
      const vol = document.getElementById('kpi-macro-vol').innerText;
      const net = document.getElementById('kpi-macro-net').innerText;

      const speech =
        `Good morning from the Rocket and Mr. Cooper Global Macro Treasury Desk. Following a ${{shockBps}} move in the ten-year Treasury yield, our implied thirty-year par mortgage rate stands at ${{rate}}. Across our 2.1 trillion dollar servicing portfolio, ${{itm}} immediately enter the refinance strike zone, projecting ${{vol}} in ninety-day recaptured loan locks and ${{net}} in positive origination-over-servicing hedge revenue.`;

      if (window.playLiveCallClip) {{
        window.playLiveCallClip(speech, "Kore", "Chief Economist & Capital Markets Desk (Project Pulse)", btnEl);
      }}
    }};

    window.runLiveVertexAI = async function() {{
      const model = window.getSelectedModel ? window.getSelectedModel() : 'gemini-4-argon';
      const shock = document.getElementById('sld-bps-shock').value || -75;
      const recap = document.getElementById('sld-recap-rate').value || 83;
      const note = document.getElementById('pulse-research-note');
      note.innerHTML = `<em>Synthesizing Institutional Capital Markets Research Note with <strong>${{model}}</strong>...</em>`;
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: 'M.5',
            model: model,
            user_input: `Generate an institutional treasury and capital markets briefing on Rocket + Mr. Cooper's $2.1T servicing portfolio (9.5M loans) under a ${{shock}} bps 10-Yr Treasury shock and ${{recap}}% recapture target.`,
            params: {{ treasury_shock_bps: shock, recapture_pct: recap }}
          }})
        }});
        const data = await res.json();
        const textOut = (data.vertex && data.vertex.response_markdown) || data.output || 'Desk note verified.';
        note.innerHTML = `<strong>[${{data.model_used || model}} Institutional Research Note]:</strong> ${{textOut}}`;
      }} catch (e) {{
        note.innerText = "Error: " + e.message;
      }}
    }};

    document.addEventListener('DOMContentLoaded', () => {{
      window.updateMacroPulseSimulator();
    }});
  </script>

  {render_floating_control_bar_and_drawer(code, auth_token)}
</body>
</html>"""
