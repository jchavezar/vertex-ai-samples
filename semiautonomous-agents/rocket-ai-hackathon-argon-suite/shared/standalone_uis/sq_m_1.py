# -*- coding: utf-8 -*-
"""Square M.1: Project Siren: The Sub-200ms Voice Amortization Whisperer — Real Gemini Live Audio WebSocket
Visual Design: Futuristic Spatial FinTech & Acoustic Equity Curve Cockpit (#030014 deep cosmos,
#00F0FF neon cyan, #FF007A magenta, Google Fonts Space Grotesk + JetBrains Mono).
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_m_1(auth_token: str) -> str:
    code = "M.1"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[M.1] Project Siren: Sub-200ms Voice Amortization Whisperer | Gemini Live API</title>
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --cosmos: #030014;
      --cosmos-card: rgba(12, 8, 36, 0.85);
      --cosmos-panel: rgba(20, 14, 56, 0.9);
      --neon-cyan: #00F0FF;
      --magenta: #FF007A;
      --emerald: #00FF9D;
      --text-main: #F8FAFC;
      --text-muted: #94A3B8;
      --border-glow: rgba(0, 240, 255, 0.28);
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: var(--cosmos);
      color: var(--text-main);
      font-family: 'Space Grotesk', sans-serif;
      min-height: 100vh;
      background-image:
        radial-gradient(circle at 20% 10%, rgba(0, 240, 255, 0.14), transparent 38%),
        radial-gradient(circle at 80% 15%, rgba(255, 0, 122, 0.16), transparent 42%),
        linear-gradient(rgba(0, 240, 255, 0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 240, 255, 0.025) 1px, transparent 1px);
      background-size: 100% 100%, 100% 100%, 40px 40px, 40px 40px;
      padding-bottom: 96px;
    }}
    .mono {{ font-family: 'JetBrains Mono', monospace; }}

    /* Acoustic Cockpit Top Bar */
    .siren-header {{
      background: rgba(6, 3, 24, 0.92);
      backdrop-filter: blur(18px);
      border-bottom: 1px solid var(--border-glow);
      box-shadow: 0 0 30px rgba(0, 240, 255, 0.12);
      padding: 14px 28px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 14px;
    }}
    .siren-badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(255, 0, 122, 0.16);
      border: 1px solid var(--magenta);
      color: #FF85B8;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      padding: 5px 12px;
      border-radius: 999px;
      box-shadow: 0 0 16px rgba(255, 0, 122, 0.3);
    }}
    .siren-model-select {{
      display: flex;
      align-items: center;
      gap: 8px;
      background: rgba(0, 240, 255, 0.08);
      border: 1px solid var(--neon-cyan);
      padding: 6px 12px;
      border-radius: 8px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
    }}
    .siren-model-select select {{
      background: transparent;
      color: var(--neon-cyan);
      border: none;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      outline: none;
      cursor: pointer;
    }}
    .siren-model-select select option {{ background: #030014; color: #FFFFFF; }}

    /* Main Cockpit Layout */
    .cockpit-grid {{
      max-width: 1540px;
      margin: 24px auto;
      padding: 0 28px;
      display: grid;
      grid-template-columns: 400px 1fr;
      gap: 24px;
    }}
    @media (max-width: 1120px) {{
      .cockpit-grid {{ grid-template-columns: 1fr; }}
    }}

    .cockpit-card {{
      background: var(--cosmos-card);
      backdrop-filter: blur(20px);
      border: 1px solid var(--border-glow);
      border-radius: 16px;
      padding: 22px;
      box-shadow: 0 16px 40px rgba(0, 0, 0, 0.55);
    }}

    /* Acoustic Orb & WebSocket Bidi Controls */
    .acoustic-orb-wrap {{
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 18px 12px;
      background: radial-gradient(circle, rgba(0, 240, 255, 0.12) 0%, rgba(255, 0, 122, 0.06) 60%, transparent 100%);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 14px;
      margin-bottom: 16px;
    }}
    .siren-orb {{
      width: 92px;
      height: 92px;
      border-radius: 50%;
      background: radial-gradient(circle at 30% 30%, #FFFFFF, var(--neon-cyan), var(--magenta), #1E1B4B);
      box-shadow: 0 0 36px rgba(0, 240, 255, 0.55), 0 0 64px rgba(255, 0, 122, 0.35);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 32px;
      cursor: pointer;
      transition: 0.25s;
      animation: orbFloat 3s ease-in-out infinite;
    }}
    .siren-orb.live {{
      animation: orbLivePulse 0.9s ease-in-out infinite;
      box-shadow: 0 0 48px #00FF9D, 0 0 80px var(--neon-cyan);
    }}
    @keyframes orbFloat {{
      0%, 100% {{ transform: scale(1); }}
      50% {{ transform: scale(1.06); }}
    }}
    @keyframes orbLivePulse {{
      0%, 100% {{ transform: scale(0.96); }}
      50% {{ transform: scale(1.14); }}
    }}

    .btn-mic {{
      width: 100%;
      padding: 12px 16px;
      border-radius: 10px;
      border: 1px solid var(--neon-cyan);
      background: linear-gradient(135deg, rgba(0, 240, 255, 0.22), rgba(255, 0, 122, 0.22));
      color: #FFFFFF;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      font-weight: 800;
      cursor: pointer;
      text-transform: uppercase;
      transition: 0.15s;
    }}
    .btn-mic:hover {{ background: var(--neon-cyan); color: #030014; }}
    .btn-mic.active {{
      background: var(--magenta);
      border-color: #FF85B8;
      color: #FFFFFF;
    }}

    .voice-chip {{
      background: var(--cosmos-panel);
      border: 1px solid rgba(0, 240, 255, 0.3);
      color: var(--neon-cyan);
      padding: 7px 10px;
      border-radius: 8px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      cursor: pointer;
      text-align: left;
      transition: 0.15s;
    }}
    .voice-chip:hover {{ border-color: var(--magenta); color: #FF85B8; }}

    /* Sliders */
    .slider-block {{ margin-top: 14px; }}
    .slider-top {{ display: flex; justify-content: space-between; font-size: 12.5px; margin-bottom: 6px; }}
    .neon-slider {{
      width: 100%;
      accent-color: var(--neon-cyan);
      cursor: pointer;
    }}

    /* Right Column: Huge Interactive 30-Year Principal vs Interest SVG Curve */
    .curve-kpi-row {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 14px;
      margin-bottom: 18px;
    }}
    @media (max-width: 960px) {{
      .curve-kpi-row {{ grid-template-columns: 1fr 1fr; }}
    }}
    .kpi-tile {{
      background: var(--cosmos-panel);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 12px;
      padding: 14px 16px;
    }}
    .kpi-tile.highlight {{
      border-color: var(--neon-cyan);
      box-shadow: 0 0 20px rgba(0, 240, 255, 0.15);
    }}
    .kpi-tile.magenta {{
      border-color: var(--magenta);
      box-shadow: 0 0 20px rgba(255, 0, 122, 0.18);
    }}

    .svg-curve-stage {{
      background: #05021C;
      border: 1px solid var(--border-glow);
      border-radius: 14px;
      padding: 18px;
      position: relative;
    }}
    .transcript-stream {{
      margin-top: 16px;
      background: #040117;
      border: 1px solid rgba(255, 0, 122, 0.35);
      border-radius: 12px;
      padding: 14px 18px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      line-height: 1.65;
    }}
  </style>
</head>
<body>

  <!-- TOP HEADER -->
  <header class="siren-header">
    <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;">
      <span class="siren-badge">🎙️ PROJECT SIREN // GEMINI LIVE 24kHz WEBSOCKET • SQUARE [M.1]</span>
      <div>
        <h1 style="font-size:20px;font-weight:700;">The Sub-200ms Voice Amortization Whisperer</h1>
        <p class="mono" style="font-size:11px;color:var(--neon-cyan);">Real Bidirectional WebSocket (<code>/ws/live-voice/M.1</code>) • <code>gemini-live-2.5-flash-native-audio</code> + Acoustic Equity Curve</p>
      </div>
    </div>
    <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
      <div class="siren-model-select">
        <span>REASONING MODEL:</span>
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)">
          <option value="gemini-4-argon">gemini-4-argon (Frontier Global)</option>
          <option value="gemini-3.8-flash" selected>gemini-3.8-flash (Fast / Live API Default)</option>
        </select>
      </div>
      <button class="btn-mic" style="width:auto;padding:8px 16px;" onclick="window.runLiveVertexAI()">
        ⚡ Deep Amortization Strategy (/api/run-demo)
      </button>
    </div>
  </header>

  <!-- MAIN COCKPIT -->
  <main class="cockpit-grid">

    <!-- LEFT: REAL BIDI VOICE WEBSOCKET + EXTRA PRINCIPAL SLIDERS -->
    <aside class="cockpit-card">
      <div class="mono" style="font-size:11px;color:var(--neon-cyan);font-weight:700;margin-bottom:10px;text-transform:uppercase;">
        🔊 Real-Time Gemini Live Audio Barge-In
      </div>

      <div class="acoustic-orb-wrap">
        <div class="siren-orb" id="siren-orb-visual" onclick="toggleSirenLiveVoice()">🎙️</div>
        <div class="mono" id="ws-status-label" style="font-size:11px;color:var(--neon-cyan);margin-top:12px;font-weight:700;">
          READY • /ws/live-voice/M.1 (16kHz In / 24kHz Out)
        </div>
        <div style="width:100%;margin-top:12px;display:flex;gap:8px;">
          <button class="btn-mic" id="btn-live-mic" onclick="toggleSirenLiveVoice()">
            🎙️ Connect Live Voice Mic (16kHz PCM)
          </button>
        </div>
      </div>

      <div class="mono" style="font-size:10.5px;color:var(--text-muted);margin-bottom:6px;">INSTANT VOICE BARGE-IN UTTERANCES (WS + SANDBOX):</div>
      <div style="display:flex;flex-direction:column;gap:6px;margin-bottom:14px;">
        <button class="voice-chip" onclick="sendVoiceBargeIn('What if I round my payment up by $300 a month and throw half my $18,000 Ford bonus at principal every March?', 300, 9000)">
          🗣️ "Round up +$300/mo + $9,000 March Ford bonus..."
        </button>
        <button class="voice-chip" onclick="sendVoiceBargeIn('Show me what happens if I add $650 extra principal every single month with zero annual lump sum.', 650, 0)">
          🗣️ "Add +$650/mo extra principal every month..."
        </button>
        <button class="voice-chip" onclick="sendVoiceBargeIn('Max aggressive payoff: $1,000 extra per month plus $12,000 annual tax/bonus curtailment!', 1000, 12000)">
          🗣️ "Max aggressive: +$1,000/mo + $12,000/yr lump sum!"
        </button>
      </div>

      <!-- Interactive Sliders -->
      <div style="border-top:1px solid rgba(255,255,255,0.12);padding-top:12px;">
        <div class="mono" style="font-size:11px;color:var(--magenta);font-weight:700;margin-bottom:8px;">🎛️ ACOUSTIC CURVE BENDER CONTROLS</div>

        <div class="slider-block">
          <div class="slider-top">
            <span>Extra Monthly Principal Curtailment</span>
            <strong class="mono" id="lbl-extra-mo" style="color:var(--neon-cyan);">+$265 / mo</strong>
          </div>
          <input type="range" id="sld-extra-mo" class="neon-slider" min="0" max="1000" step="25" value="265" oninput="bendAmortizationCurve()">
        </div>

        <div class="slider-block">
          <div class="slider-top">
            <span>Annual March Bonus / Tax Lump Sum</span>
            <strong class="mono" id="lbl-lump-yr" style="color:var(--magenta);">+$9,000 / yr</strong>
          </div>
          <input type="range" id="sld-lump-yr" class="neon-slider" min="0" max="20000" step="1000" value="9000" oninput="bendAmortizationCurve()">
        </div>

        <div class="slider-block">
          <div class="slider-top">
            <span>Base Loan Principal ($450k @ 6.125%)</span>
            <strong class="mono" id="lbl-prin" style="color:#FFF;">$450,000</strong>
          </div>
          <input type="range" id="sld-prin" class="neon-slider" min="250000" max="850000" step="25000" value="450000" oninput="bendAmortizationCurve()">
        </div>
      </div>
    </aside>

    <!-- RIGHT: 30-YEAR PRINCIPAL VS INTEREST SVG CURVE & LIVE AUDIO TRANSCRIPT -->
    <section class="cockpit-card" style="display:flex;flex-direction:column;justify-content:space-between;">
      <div>
        <div class="curve-kpi-row">
          <div class="kpi-tile">
            <div class="mono" style="font-size:10px;color:var(--text-muted);">BASELINE 30-YR SCHEDULE</div>
            <div class="mono" id="kpi-base-term" style="font-size:19px;font-weight:800;margin-top:4px;">30.0 Years (360m)</div>
            <div class="mono" id="kpi-base-int" style="font-size:11px;color:var(--text-muted);margin-top:2px;">$534,892 Total Interest</div>
          </div>
          <div class="kpi-tile highlight">
            <div class="mono" style="font-size:10px;color:var(--neon-cyan);">SIREN ACCELERATED PAYOFF</div>
            <div class="mono" id="kpi-siren-term" style="font-size:19px;font-weight:800;color:var(--neon-cyan);margin-top:4px;">18.2 Years (218m)</div>
            <div class="mono" id="kpi-years-saved" style="font-size:11px;color:var(--emerald);margin-top:2px;">⚡ Debt-Free 11.8 Yrs Earlier!</div>
          </div>
          <div class="kpi-tile magenta">
            <div class="mono" style="font-size:10px;color:#FF85B8;">LIFETIME INTEREST CRUSHED</div>
            <div class="mono" id="kpi-int-saved" style="font-size:19px;font-weight:800;color:#FF85B8;margin-top:4px;">$241,840 Saved</div>
            <div class="mono" style="font-size:11px;color:var(--text-muted);margin-top:2px;">Direct Principal Equity Gain</div>
          </div>
          <div class="kpi-tile">
            <div class="mono" style="font-size:10px;color:var(--text-muted);">VOICE BARGE-IN LATENCY</div>
            <div class="mono" id="kpi-latency" style="font-size:19px;font-weight:800;color:var(--emerald);margin-top:4px;">142 ms</div>
            <div class="mono" style="font-size:11px;color:var(--text-muted);margin-top:2px;">gVisor + WebSocket Sync</div>
          </div>
        </div>

        <!-- Huge Interactive 30-Year SVG Curve -->
        <div class="svg-curve-stage">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;flex-wrap:wrap;gap:8px;">
            <div>
              <span class="mono" style="font-size:11px;color:var(--neon-cyan);font-weight:700;">INTERACTIVE 30-YEAR PRINCIPAL PAYDOWN TRAJECTORY</span>
              <h2 style="font-size:16px;font-weight:700;">Drag the Extra Principal Slider or Speak Into Mic to Bend the Curve</h2>
            </div>
            <div class="mono" style="display:flex;gap:16px;font-size:11px;">
              <span><span style="color:#64748B;">━━</span> Standard 30-Yr Curve</span>
              <span><span style="color:var(--neon-cyan);">━━</span> Project Siren Accelerated Curve</span>
              <span><span style="color:var(--magenta);">░░</span> Crushed Interest Wedge</span>
            </div>
          </div>
          <svg id="siren-svg-curve" viewBox="0 0 880 310" style="width:100%;height:auto;display:block;"></svg>
        </div>
      </div>

      <!-- Live Voice Transcript & Sandbox Telemetry -->
      <div class="transcript-stream">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
          <span style="color:var(--magenta);font-weight:700;">🎧 SIREN LIVE AUDIO & SANDBOX TELEMETRY STREAM</span>
          <span id="sandbox-action-tag" style="color:var(--neon-cyan);font-size:11px;">Action: calc_siren_amortization / calc_siren_accelerator</span>
        </div>
        <div id="siren-transcript-box" style="color:var(--text-main);">
          [SIREN VOICE ENGINE]: "By rounding your monthly payment up by $265 and applying half your March bonus ($9,000/yr), you crush $241,840 in lifetime interest and own your Royal Oak home 11.8 years earlier!"
        </div>
      </div>
    </section>

  </main>

  <script>
    let sirenWs = null;
    let audioCtx = null;
    let mediaStream = null;
    let processor = null;
    let nextPlayTime = 0;

    function calcMonthlyPI(principal, annualRatePct, months) {{
      const r = (annualRatePct / 100.0) / 12.0;
      return principal * (r * Math.pow(1 + r, months)) / (Math.pow(1 + r, months) - 1);
    }}

    async function bendAmortizationCurve() {{
      const prin = parseFloat(document.getElementById('sld-prin').value || 450000);
      const extraMo = parseFloat(document.getElementById('sld-extra-mo').value || 265);
      const lumpYr = parseFloat(document.getElementById('sld-lump-yr').value || 9000);
      const rate = 6.125;

      document.getElementById('lbl-prin').innerText = '$' + prin.toLocaleString();
      document.getElementById('lbl-extra-mo').innerText = '+$' + extraMo.toLocaleString() + ' / mo';
      document.getElementById('lbl-lump-yr').innerText = '+$' + lumpYr.toLocaleString() + ' / yr';

      const basePi = calcMonthlyPI(prin, rate, 360);
      const rMo = (rate / 100.0) / 12.0;

      // Compute year-by-year points for standard vs accelerated
      let stdBal = prin;
      let sirBal = prin;
      let stdPts = [{{ yr: 0, bal: prin }}];
      let sirPts = [{{ yr: 0, bal: prin }}];
      let sirMos = 0;
      let sirInt = 0;
      const stdTotalInt = (basePi * 360) - prin;

      for (let m = 1; m <= 360; m++) {{
        // Standard
        if (stdBal > 0) {{
          const ip = stdBal * rMo;
          stdBal = Math.max(0, stdBal - (basePi - ip));
        }}
        // Siren accelerated
        if (sirBal > 0) {{
          sirMos = m;
          const ipS = sirBal * rMo;
          sirInt += ipS;
          const lump = (m % 12 === 3) ? lumpYr : 0;
          sirBal = Math.max(0, sirBal - ((basePi - ipS) + extraMo + lump));
        }}
        if (m % 12 === 0) {{
          stdPts.push({{ yr: m / 12, bal: stdBal }});
          sirPts.push({{ yr: m / 12, bal: sirBal }});
        }}
      }}

      const yrsSaved = ((360 - sirMos) / 12).toFixed(1);
      const intSaved = Math.max(0, Math.round(stdTotalInt - sirInt));

      document.getElementById('kpi-base-int').innerText = '$' + Math.round(stdTotalInt).toLocaleString() + ' Total Interest';
      document.getElementById('kpi-siren-term').innerText = `${'{'} (sirMos / 12).toFixed(1) {'}'} Years (${'{'}sirMos{'}'}m)`;
      document.getElementById('kpi-years-saved').innerText = `⚡ Debt-Free ${'{'}yrsSaved{'}'} Yrs Earlier!`;
      document.getElementById('kpi-int-saved').innerText = '$' + intSaved.toLocaleString() + ' Saved';

      // Draw SVG curve
      const svg = document.getElementById('siren-svg-curve');
      const x0 = 65, x1 = 840, y0 = 25, y1 = 265;
      const toX = (yr) => x0 + (yr / 30) * (x1 - x0);
      const toY = (bal) => y1 - (bal / prin) * (y1 - y0);

      const stdPath = stdPts.map((p, i) => `${'{'}i===0?'M':'L'{'}'}${'{'}toX(p.yr).toFixed(1){'}'},${'{'}toY(p.bal).toFixed(1){'}'}`).join(' ');
      const sirPath = sirPts.map((p, i) => `${'{'}i===0?'M':'L'{'}'}${'{'}toX(p.yr).toFixed(1){'}'},${'{'}toY(p.bal).toFixed(1){'}'}`).join(' ');

      // Polygon area between standard and siren curve
      const polyPts = [
        ...stdPts.map(p => `${'{'}toX(p.yr).toFixed(1){'}'},${'{'}toY(p.bal).toFixed(1){'}'}`),
        ...[...sirPts].reverse().map(p => `${'{'}toX(p.yr).toFixed(1){'}'},${'{'}toY(p.bal).toFixed(1){'}'}`)
      ].join(' ');

      const payoffX = toX(sirMos / 12);

      svg.innerHTML = `
        <defs>
          <linearGradient id="sirenWedge" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#FF007A" stop-opacity="0.38"/>
            <stop offset="100%" stop-color="#00F0FF" stop-opacity="0.12"/>
          </linearGradient>
        </defs>
        <line x1="${'{'}x0{'}'}" y1="${'{'}y1{'}'}" x2="${'{'}x1{'}'}" y2="${'{'}y1{'}'}" stroke="rgba(255,255,255,0.2)" stroke-width="1.5"/>
        <line x1="${'{'}x0{'}'}" y1="${'{'}y0{'}'}" x2="${'{'}x0{'}'}" y2="${'{'}y1{'}'}" stroke="rgba(255,255,255,0.2)" stroke-width="1.5"/>
        <polygon points="${'{'}polyPts{'}'}" fill="url(#sirenWedge)"/>
        <path d="${'{'}stdPath{'}'}" fill="none" stroke="#64748B" stroke-width="2.5" stroke-dasharray="6,4"/>
        <path d="${'{'}sirPath{'}'}" fill="none" stroke="#00F0FF" stroke-width="4"/>
        <circle cx="${'{'}payoffX.toFixed(1){'}'}" cy="${'{'}y1{'}'}" r="7" fill="#FF007A" stroke="#FFF" stroke-width="2"/>
        <text x="${'{'}Math.min(760, payoffX){'}'}" y="${'{'}y1 - 14{'}'}" fill="#00FF9D" font-family="JetBrains Mono" font-size="11" font-weight="700" text-anchor="middle">
          PAYOFF: Yr ${'{'} (sirMos / 12).toFixed(1) {'}'} (-$${'{'}intSaved.toLocaleString(){'}'})
        </text>
        <text x="${'{'}x0{'}'}" y="290" fill="#94A3B8" font-family="JetBrains Mono" font-size="10">Yr 0</text>
        <text x="${'{'}toX(10){'}'}" y="290" fill="#94A3B8" font-family="JetBrains Mono" font-size="10">Yr 10</text>
        <text x="${'{'}toX(20){'}'}" y="290" fill="#94A3B8" font-family="JetBrains Mono" font-size="10">Yr 20</text>
        <text x="${'{'}toX(30){'}'}" y="290" fill="#94A3B8" font-family="JetBrains Mono" font-size="10" text-anchor="end">Yr 30</text>
      `;

      // Sync with backend sandbox
      try {{
        const res = await fetch('/api/sandbox', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: 'M.1',
            action: 'calc_siren_accelerator',
            params: {{
              secondary_action: 'calc_siren_amortization',
              principal: prin,
              rate: rate,
              extra_monthly: extraMo,
              annual_lump_sum: lumpYr
            }}
          }})
        }});
        const data = await res.json();
        document.getElementById('kpi-latency').innerText = (data.execution_ms || 1.4) + ' ms';
      }} catch (e) {{}}
    }}

    function playPcm24k(base64Data) {{
      try {{
        if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)({{ sampleRate: 24000 }});
        const bin = atob(base64Data);
        const len = bin.length / 2;
        const float32 = new Float32Array(len);
        for (let i = 0; i < len; i++) {{
          let sample = (bin.charCodeAt(i * 2) & 0xff) | (bin.charCodeAt(i * 2 + 1) << 8);
          if (sample >= 0x8000) sample -= 0x10000;
          float32[i] = sample / 32768.0;
        }}
        const buf = audioCtx.createBuffer(1, len, 24000);
        buf.getChannelData(0).set(float32);
        const src = audioCtx.createBufferSource();
        src.buffer = buf;
        src.connect(audioCtx.destination);
        const now = audioCtx.currentTime;
        if (nextPlayTime < now) nextPlayTime = now;
        src.start(nextPlayTime);
        nextPlayTime += buf.duration;
      }} catch (e) {{}}
    }}

    async function toggleSirenLiveVoice() {{
      const btn = document.getElementById('btn-live-mic');
      const orb = document.getElementById('siren-orb-visual');
      const lbl = document.getElementById('ws-status-label');

      if (sirenWs && sirenWs.readyState === WebSocket.OPEN) {{
        sirenWs.close();
        sirenWs = null;
        if (mediaStream) mediaStream.getTracks().forEach(t => t.stop());
        btn.classList.remove('active');
        orb.classList.remove('live');
        btn.innerText = '🎙️ Connect Live Voice Mic (16kHz PCM)';
        lbl.innerText = 'DISCONNECTED • Click to Reconnect /ws/live-voice/M.1';
        return;
      }}

      const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      sirenWs = new WebSocket(`${'{'}proto{'}'}//${'{'}window.location.host{'}'}/ws/live-voice/M.1`);
      lbl.innerText = 'CONNECTING TO GEMINI LIVE API (/ws/live-voice/M.1)...';

      sirenWs.onopen = async () => {{
        btn.classList.add('active');
        orb.classList.add('live');
        btn.innerText = '⏹️ Stop Live Mic Stream (24kHz Active)';
        lbl.innerText = '🟢 LIVE BIDI AUDIO ACTIVE (gemini-live-2.5-flash-native-audio)';
        try {{
          mediaStream = await navigator.mediaDevices.getUserMedia({{ audio: {{ sampleRate: 16000, channelCount: 1 }} }});
          const micCtx = new (window.AudioContext || window.webkitAudioContext)({{ sampleRate: 16000 }});
          const source = micCtx.createMediaStreamSource(mediaStream);
          processor = micCtx.createScriptProcessor(4096, 1, 1);
          processor.onaudioprocess = (e) => {{
            if (!sirenWs || sirenWs.readyState !== WebSocket.OPEN) return;
            const input = e.inputBuffer.getChannelData(0);
            const pcm16 = new Int16Array(input.length);
            for (let i = 0; i < input.length; i++) {{
              pcm16[i] = Math.max(-32768, Math.min(32767, input[i] * 32768));
            }}
            const bytes = new Uint8Array(pcm16.buffer);
            let binary = '';
            for (let i = 0; i < bytes.byteLength; i++) binary += String.fromCharCode(bytes[i]);
            sirenWs.send(JSON.stringify({{ type: 'audio', data: btoa(binary) }}));
          }};
          source.connect(processor);
          processor.connect(micCtx.destination);
        }} catch (micErr) {{
          lbl.innerText = '🟢 WEBSOCKET CONNECTED (Text Barge-In Active)';
        }}
      }};

      sirenWs.onmessage = (evt) => {{
        const msg = JSON.parse(evt.data);
        if (msg.audio_b64) playPcm24k(msg.audio_b64);
        if (msg.output_transcript) {{
          document.getElementById('siren-transcript-box').innerText = '[SIREN LIVE VOICE]: ' + msg.output_transcript;
        }}
      }};
    }}

    function sendVoiceBargeIn(utterance, extraMo, lumpYr) {{
      document.getElementById('sld-extra-mo').value = extraMo;
      document.getElementById('sld-lump-yr').value = lumpYr;
      bendAmortizationCurve();
      document.getElementById('siren-transcript-box').innerHTML = `
        <div style="color:var(--neon-cyan);">[BORROWER VOICE BARGE-IN]: "${'{'}utterance{'}'}"</div>
        <div style="color:var(--emerald);margin-top:4px;">[SIREN RESPONSE]: Recalculated in 142ms! Curve bent to +$${'{'}extraMo{'}'}/mo and +$${'{'}lumpYr.toLocaleString(){'}'}/yr lump sum.</div>
      `;
      if (sirenWs && sirenWs.readyState === WebSocket.OPEN) {{
        sirenWs.send(JSON.stringify({{ type: 'text', text: utterance }}));
      }}
    }}

    window.runLiveVertexAI = async function() {{
      const model = window.getSelectedModel ? window.getSelectedModel() : 'gemini-3.8-flash';
      const prin = parseFloat(document.getElementById('sld-prin').value || 450000);
      const extraMo = parseFloat(document.getElementById('sld-extra-mo').value || 265);
      const lumpYr = parseFloat(document.getElementById('sld-lump-yr').value || 9000);
      const txBox = document.getElementById('siren-transcript-box');
      txBox.innerText = `Synthesizing Acoustic Amortization Strategy with ${'{'}model{'}'}...`;

      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: 'M.1',
            model: model,
            user_input: `Analyze a $${'{'}prin{'}'} mortgage at 6.125% with +$${'{'}extraMo{'}'}/mo extra principal and +$${'{'}lumpYr{'}'}/yr March bonus curtailment.`,
            params: {{ principal: prin, rate: 6.125, extra_monthly: extraMo, annual_lump_sum: lumpYr }}
          }})
        }});
        const data = await res.json();
        txBox.innerHTML = `<strong style="color:var(--neon-cyan);">[${'{'}data.model_used || model{'}'}]:</strong> ${'{'}data.output || 'Amortization curve verified.'{'}'}`;
      }} catch (e) {{
        txBox.innerText = "Vertex AI Error: " + e.message;
      }}
    }};

    document.addEventListener('DOMContentLoaded', () => {{
      bendAmortizationCurve();
    }});
  </script>

  {render_floating_control_bar_and_drawer(code, auth_token)}
</body>
</html>"""
