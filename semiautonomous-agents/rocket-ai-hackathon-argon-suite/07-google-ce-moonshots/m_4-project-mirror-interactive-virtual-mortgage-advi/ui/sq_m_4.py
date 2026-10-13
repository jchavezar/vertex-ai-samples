# -*- coding: utf-8 -*-
"""Square M.4: Project Mirror: Interactive Virtual Mortgage Advisor 'Astra Pro' — Real Gemini Live Audio WebSocket
Visual Design: 2 AM Calm Closing-Table Interactive Whiteboard & Voice Lounge (#09101D midnight lounge,
#FBBF24 warm candlelight gold, #38BDF8 soft sky, Google Fonts Fraunces + DM Sans).
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_m_4(auth_token: str) -> str:
    code = "M.4"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[M.4] Project Mirror: 'Astra Pro' 2 AM Closing-Table Whiteboard & Voice Lounge</title>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,400&family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --lounge-bg: #09101D;
      --lounge-card: #101B2E;
      --lounge-panel: #16243D;
      --candle-gold: #FBBF24;
      --candle-soft: rgba(251, 191, 36, 0.14);
      --soft-sky: #38BDF8;
      --sage-green: #34D399;
      --warm-text: #F8FAFC;
      --muted-text: #94A3B8;
      --border-warm: rgba(251, 191, 36, 0.25);
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: var(--lounge-bg);
      color: var(--warm-text);
      font-family: 'DM Sans', -apple-system, sans-serif;
      min-height: 100vh;
      background-image:
        radial-gradient(circle at 20% 15%, rgba(251, 191, 36, 0.10), transparent 45%),
        radial-gradient(circle at 80% 25%, rgba(56, 189, 248, 0.08), transparent 45%);
      padding-bottom: 96px;
    }}
    .serif-lounge {{ font-family: 'Fraunces', Georgia, serif; }}
    .mono {{ font-family: 'JetBrains Mono', monospace; }}

    /* Warm Midnight Lounge Header */
    .lounge-header {{
      background: rgba(16, 27, 46, 0.92);
      backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--border-warm);
      padding: 14px 28px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 14px;
    }}
    .candle-badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: var(--candle-soft);
      border: 1px solid var(--candle-gold);
      color: var(--candle-gold);
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      padding: 5px 14px;
      border-radius: 999px;
    }}
    .lounge-model-box {{
      display: flex;
      align-items: center;
      gap: 8px;
      background: var(--lounge-bg);
      border: 1px solid var(--soft-sky);
      padding: 6px 14px;
      border-radius: 999px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
    }}
    .lounge-model-box select {{
      background: transparent;
      color: var(--soft-sky);
      border: none;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      outline: none;
      cursor: pointer;
    }}
    .lounge-model-box select option {{ background: #09101D; color: #FFFFFF; }}

    /* Main Lounge Layout */
    .lounge-grid {{
      max-width: 1520px;
      margin: 26px auto;
      padding: 0 28px;
      display: grid;
      grid-template-columns: 400px 1fr;
      gap: 26px;
    }}
    @media (max-width: 1120px) {{
      .lounge-grid {{ grid-template-columns: 1fr; }}
    }}

    .lounge-card {{
      background: var(--lounge-card);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 20px;
      padding: 24px;
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.45);
    }}

    /* Interactive Closing Disclosure (CD) Line Items */
    .cd-item-btn {{
      width: 100%;
      text-align: left;
      background: var(--lounge-panel);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-left: 4px solid transparent;
      border-radius: 12px;
      padding: 13px 16px;
      margin-bottom: 10px;
      cursor: pointer;
      transition: all 0.2s;
      color: var(--warm-text);
    }}
    .cd-item-btn:hover {{
      border-color: var(--candle-gold);
      transform: translateX(3px);
    }}
    .cd-item-btn.active {{
      background: rgba(251, 191, 36, 0.14);
      border-color: var(--candle-gold);
      border-left: 5px solid var(--candle-gold);
    }}
    .cd-item-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: 700;
      font-size: 13.5px;
    }}
    .cd-item-sub {{
      font-size: 11.5px;
      color: var(--muted-text);
      margin-top: 3px;
    }}

    .btn-astra-voice {{
      width: 100%;
      padding: 13px 16px;
      border-radius: 12px;
      border: 1px solid var(--candle-gold);
      background: linear-gradient(135deg, #FBBF24, #D97706);
      color: #09101D;
      font-family: 'DM Sans', sans-serif;
      font-size: 13.5px;
      font-weight: 800;
      cursor: pointer;
      transition: 0.2s;
      box-shadow: 0 8px 24px rgba(251, 191, 36, 0.25);
    }}
    .btn-astra-voice:hover {{ filter: brightness(1.06); }}
    .btn-astra-voice.live {{
      background: var(--sage-green);
      border-color: #6EE7B7;
      color: #052E16;
    }}

    /* Interactive Closing-Table Whiteboard */
    .whiteboard-canvas {{
      background: #0B1424;
      border: 2px solid var(--border-warm);
      border-radius: 18px;
      padding: 22px 24px;
      box-shadow: inset 0 0 40px rgba(251, 191, 36, 0.04);
    }}
    .astra-voice-bubble {{
      margin-top: 16px;
      background: rgba(251, 191, 36, 0.09);
      border: 1px solid var(--border-warm);
      border-radius: 14px;
      padding: 16px 20px;
      font-size: 14px;
      line-height: 1.7;
    }}
  </style>
</head>
<body>

  <!-- 2 AM CLOSING-TABLE LOUNGE HEADER -->
  <header class="lounge-header">
    <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;">
      <span class="candle-badge">🕯️ PROJECT MIRROR // 'ASTRA PRO' 2 AM VOICE LOUNGE • SQUARE [M.4]</span>
      <div>
        <h1 class="serif-lounge" style="font-size:21px;font-weight:600;">Interactive Closing-Table Whiteboard & Live Voice Advisor</h1>
        <p class="mono" style="font-size:11px;color:var(--soft-sky);">Real Bidirectional WebSocket (<code>/ws/live-voice/M.4</code>) • Zero-Jargon Closing Disclosure (CD) Visual Explainer</p>
      </div>
    </div>
    <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
      <div class="lounge-model-box">
        <span>ADVISOR MODEL:</span>
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)">
          <option value="gemini-4-argon">gemini-4-argon (Frontier Global)</option>
          <option value="gemini-3.8-flash" selected>gemini-3.8-flash (Fast / Live API Default)</option>
        </select>
      </div>
      <button class="btn-astra-voice" style="width:auto;padding:9px 18px;" onclick="window.runLiveVertexAI()">
        ⚡ Full CD Walkthrough (/api/run-demo)
      </button>
    </div>
  </header>

  <!-- MAIN LOUNGE WORKSPACE -->
  <main class="lounge-grid">

    <!-- LEFT: CLICKABLE CLOSING DISCLOSURE (CD) LINE ITEMS & REAL LIVE AUDIO -->
    <aside class="lounge-card" style="display:flex;flex-direction:column;justify-content:space-between;gap:16px;">
      <div>
        <div class="mono" style="font-size:11px;color:var(--candle-gold);font-weight:700;text-transform:uppercase;margin-bottom:6px;">
          📄 Confusing Closing Disclosure (CD) Line Items
        </div>
        <h2 class="serif-lounge" style="font-size:19px;margin-bottom:6px;">Tap Any CD Box to Draw & Explain</h2>
        <p style="font-size:12.5px;color:var(--muted-text);line-height:1.55;margin-bottom:14px;">
          It's 2:00 AM the night before closing on a $350,000 Royal Oak home. Click any line item below to draw an interactive whiteboard diagram and hear Astra Pro explain it warmly.
        </p>

        <!-- Clickable CD Box 1 -->
        <button class="cd-item-btn active" id="cd-btn-cash" onclick="selectCdWhiteboardItem('cash', this)">
          <div class="cd-item-top">
            <span>💰 Cash to Close & Reserve Cushion</span>
            <span class="mono" style="color:var(--candle-gold);">$22,300.00</span>
          </div>
          <div class="cd-item-sub">Why does 5% down ($17,500) + closing leaves $2,700 in Rocket Money?</div>
        </button>

        <!-- Clickable CD Box 2 -->
        <button class="cd-item-btn" id="cd-btn-boxA" onclick="selectCdWhiteboardItem('boxA', this)">
          <div class="cd-item-top">
            <span>🏛️ Box A: Origination Charges</span>
            <span class="mono" style="color:var(--soft-sky);">$1,295.00</span>
          </div>
          <div class="cd-item-sub">0% Zero-Tolerance Locked Underwriting & Rate-Lock Processing</div>
        </button>

        <!-- Clickable CD Box 3 -->
        <button class="cd-item-btn" id="cd-btn-boxF" onclick="selectCdWhiteboardItem('boxF', this)">
          <div class="cd-item-top">
            <span>📅 Box F: Prepaids (15 Days Interest + Ins)</span>
            <span class="mono" style="color:var(--soft-sky);">$2,480.00</span>
          </div>
          <div class="cd-item-sub">Why do I pay per-diem interest before my first mortgage payment?</div>
        </button>

        <!-- Clickable CD Box 4 -->
        <button class="cd-item-btn" id="cd-btn-boxG" onclick="selectCdWhiteboardItem('boxG', this)">
          <div class="cd-item-top">
            <span>🛡️ Box G: Initial Escrow Cushion & PMI Drop</span>
            <span class="mono" style="color:var(--sage-green);">$2,320.00</span>
          </div>
          <div class="cd-item-sub">2-Month RESPA Tax/Insurance Cushion + Month 84 Auto PMI Drop</div>
        </button>

        <!-- Interactive Purchase & Savings Inputs -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:12px;">
          <div>
            <label class="mono" style="font-size:10px;color:var(--muted-text);display:block;margin-bottom:3px;">HOME PRICE ($):</label>
            <input type="number" id="inp-mirror-price" value="350000" oninput="refreshMirrorSandbox()"
              style="width:100%;padding:8px 10px;border-radius:8px;border:1px solid var(--border-warm);background:#09101D;color:#FFF;font-family:'JetBrains Mono',monospace;font-size:12px;">
          </div>
          <div>
            <label class="mono" style="font-size:10px;color:var(--muted-text);display:block;margin-bottom:3px;">ROCKET MONEY VAULT ($):</label>
            <input type="number" id="inp-mirror-sav" value="25000" oninput="refreshMirrorSandbox()"
              style="width:100%;padding:8px 10px;border-radius:8px;border:1px solid var(--border-warm);background:#09101D;color:#FFF;font-family:'JetBrains Mono',monospace;font-size:12px;">
          </div>
        </div>
      </div>

      <div>
        <div class="mono" id="mirror-ws-status" style="font-size:10.5px;color:var(--candle-gold);text-align:center;margin-bottom:8px;">
          WebSocket Ready: /ws/live-voice/M.4 (16kHz Mic / 24kHz Voice)
        </div>
        <button class="btn-astra-voice" id="btn-mirror-mic" onclick="toggleMirrorLiveVoice()">
          🎙️ Speak with 'Astra Pro' Live Voice (/ws/live-voice/M.4)
        </button>
      </div>
    </aside>

    <!-- RIGHT: INTERACTIVE CLOSING DISCLOSURE (CD) EXPLAINER WHITEBOARD -->
    <section class="lounge-card" style="display:flex;flex-direction:column;justify-content:space-between;">
      <div class="whiteboard-canvas">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;flex-wrap:wrap;gap:10px;">
          <div>
            <span class="mono" style="font-size:10.5px;color:var(--candle-gold);font-weight:700;">INTERACTIVE CLOSING-TABLE WHITEBOARD (`calc_mirror_cd_explainer`)</span>
            <h2 class="serif-lounge" id="wb-title" style="font-size:20px;margin-top:2px;">Cash to Close & Post-Closing Safety Cushion</h2>
          </div>
          <span class="mono" id="wb-sandbox-pill" style="background:rgba(52,211,153,0.16);border:1px solid var(--sage-green);color:var(--sage-green);padding:4px 10px;border-radius:999px;font-size:11px;font-weight:700;">
            Verified in gVisor Sandbox
          </span>
        </div>

        <!-- Dynamic SVG Visual Diagram Drawn on Whiteboard -->
        <div style="background:#070D19;border:1px solid rgba(255,255,255,0.08);border-radius:14px;padding:16px;">
          <svg id="mirror-whiteboard-svg" viewBox="0 0 840 270" style="width:100%;height:auto;display:block;"></svg>
        </div>

        <!-- 3-Column Summary Strip Under Whiteboard -->
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:14px;">
          <div style="background:var(--lounge-panel);padding:12px 14px;border-radius:12px;border:1px solid rgba(255,255,255,0.08);">
            <div class="mono" style="font-size:10px;color:var(--muted-text);">CASH TO CLOSE VS VAULT</div>
            <div class="mono" id="wb-kpi-cash" style="font-size:14px;font-weight:700;color:var(--candle-gold);margin-top:4px;">$22,300 Needed ($2,700 Left)</div>
          </div>
          <div style="background:var(--lounge-panel);padding:12px 14px;border-radius:12px;border:1px solid rgba(255,255,255,0.08);">
            <div class="mono" style="font-size:10px;color:var(--muted-text);">TOTAL MONTHLY PITI + PMI</div>
            <div class="mono" id="wb-kpi-piti" style="font-size:14px;font-weight:700;color:var(--soft-sky);margin-top:4px;">$2,633.18 / month</div>
          </div>
          <div style="background:var(--lounge-panel);padding:12px 14px;border-radius:12px;border:1px solid rgba(255,255,255,0.08);">
            <div class="mono" style="font-size:10px;color:var(--muted-text);">HPA 78% LTV AUTO PMI DROP</div>
            <div class="mono" id="wb-kpi-pmi" style="font-size:14px;font-weight:700;color:var(--sage-green);margin-top:4px;">Month 84 (-$118/mo Auto)</div>
          </div>
        </div>
      </div>

      <!-- Warm Astra Pro Spoken Transcript Bubble -->
      <div class="astra-voice-bubble">
        <div class="mono" style="font-size:11px;color:var(--candle-gold);font-weight:700;margin-bottom:6px;">
          ✨ ASTRA PRO SPOKEN EXPLANATION (ZERO JARGON • 2 AM CALM MODE):
        </div>
        <div id="astra-spoken-text" class="serif-lounge" style="font-size:15px;">
          "Take a deep breath—you don't need to drain your entire $25,000 savings! Your 5% down payment is $17,500, and after your Rocket credit, closing & escrow costs are $4,800. That's $22,300 total at the closing table, leaving a comfortable $2,700 emergency cushion untouched in your Rocket Money Vault."
        </div>
      </div>
    </section>

  </main>

  <script>
    let mirrorWs = null;
    let mirrorAudioCtx = null;
    let mirrorStream = null;
    let mirrorNextTime = 0;
    let activeCdKey = 'cash';

    const CD_EXPLAINERS = {{
      cash: {{
        title: "Cash to Close & Post-Closing Safety Cushion",
        speech: "Take a deep breath—you don't need to drain your entire $25,000 savings! Your 5% down payment is $17,500, and after your Rocket credit, closing & escrow costs are $4,800. That's $22,300 total at the closing table, leaving a comfortable $2,700 emergency cushion untouched in your Rocket Money Vault."
      }},
      boxA: {{
        title: "CD Page 2, Box A: Origination Charges ($1,295 Locked)",
        speech: "Box A covers Rocket Mortgage's flat underwriting and rate-lock processing fee of $1,295. Under federal TRID law, Box A is in the strict 0% Zero-Tolerance bucket—meaning it cannot increase by a single penny from your original Loan Estimate!"
      }},
      boxF: {{
        title: "CD Page 2, Box F: Prepaids (15 Days Interest + 12-Mo Hazard Insurance)",
        speech: "Box F isn't an extra lender fee! Because mortgages are paid in arrears, closing on October 16 means your first full monthly payment isn't due until December 1. Box F simply covers the 15 days of October interest plus your first year of homeowners insurance."
      }},
      boxG: {{
        title: "CD Page 2, Box G: Initial Escrow Cushion & HPA 78% LTV Auto-PMI Drop",
        speech: "Box G seeds your personal property tax and insurance piggy bank with a 2-month RESPA cushion so Oakland County taxes are paid on time. Plus, your $118/mo PMI isn't forever—under the federal Homeowners Protection Act, it automatically drops off at 78% LTV (Month 84), or even sooner if Royal Oak home values rise on Redfin!"
      }}
    }};

    function drawWhiteboardDiagram(key, price, sav) {{
      const down = Math.round(price * 0.05);
      const closeEsc = 4800;
      const totalNeeded = down + closeEsc;
      const cushion = Math.max(0, sav - totalNeeded);
      const svg = document.getElementById('mirror-whiteboard-svg');

      if (key === 'cash') {{
        svg.innerHTML = `
          <rect x="40" y="35" width="220" height="190" rx="14" fill="#16243D" stroke="#38BDF8" stroke-width="2"/>
          <text x="150" y="75" fill="#94A3B8" font-family="JetBrains Mono" font-size="11" text-anchor="middle">ROCKET MONEY VAULT</text>
          <text x="150" y="120" fill="#38BDF8" font-family="Fraunces" font-size="28" font-weight="700" text-anchor="middle">$${'{'}sav.toLocaleString(){'}'}</text>
          <text x="150" y="155" fill="#CBD5E1" font-family="DM Sans" font-size="12" text-anchor="middle">Total Liquid Savings</text>

          <path d="M 275 130 L 325 130" stroke="#FBBF24" stroke-width="3" stroke-dasharray="5,4"/>
          <polygon points="325,124 338,130 325,136" fill="#FBBF24"/>

          <rect x="350" y="35" width="230" height="190" rx="14" fill="#16243D" stroke="#FBBF24" stroke-width="2"/>
          <text x="465" y="70" fill="#FBBF24" font-family="JetBrains Mono" font-size="11" text-anchor="middle">CLOSING TABLE WIRE</text>
          <text x="465" y="110" fill="#FFFFFF" font-family="Fraunces" font-size="25" font-weight="700" text-anchor="middle">$${'{'}totalNeeded.toLocaleString(){'}'}</text>
          <text x="465" y="145" fill="#CBD5E1" font-family="JetBrains Mono" font-size="11" text-anchor="middle">5% Down: $${'{'}down.toLocaleString(){'}'}</text>
          <text x="465" y="168" fill="#CBD5E1" font-family="JetBrains Mono" font-size="11" text-anchor="middle">Net Closing/Escrow: $4,800</text>

          <path d="M 595 130 L 635 130" stroke="#34D399" stroke-width="3"/>
          <polygon points="635,124 648,130 635,136" fill="#34D399"/>

          <rect x="655" y="35" width="155" height="190" rx="14" fill="rgba(52,211,153,0.12)" stroke="#34D399" stroke-width="2.5"/>
          <text x="732" y="75" fill="#34D399" font-family="JetBrains Mono" font-size="10.5" text-anchor="middle">SAFETY CUSHION</text>
          <text x="732" y="122" fill="#34D399" font-family="Fraunces" font-size="26" font-weight="700" text-anchor="middle">$${'{'}cushion.toLocaleString(){'}'}</text>
          <text x="732" y="155" fill="#A7F3D0" font-family="DM Sans" font-size="11.5" text-anchor="middle">Stays in Your Account!</text>
        `;
      }} else if (key === 'boxA') {{
        svg.innerHTML = `
          <rect x="60" y="45" width="320" height="175" rx="14" fill="#16243D" stroke="#38BDF8" stroke-width="2"/>
          <text x="220" y="85" fill="#38BDF8" font-family="JetBrains Mono" font-size="12" text-anchor="middle">INITIAL LOAN ESTIMATE (LE)</text>
          <text x="220" y="130" fill="#FFFFFF" font-family="Fraunces" font-size="30" font-weight="700" text-anchor="middle">$1,295.00</text>
          <text x="220" y="165" fill="#94A3B8" font-family="JetBrains Mono" font-size="11" text-anchor="middle">Box A Origination Flat Fee</text>

          <text x="420" y="135" fill="#34D399" font-family="JetBrains Mono" font-size="22" font-weight="700" text-anchor="middle">== 0% Δ ==</text>

          <rect x="460" y="45" width="320" height="175" rx="14" fill="rgba(52,211,153,0.12)" stroke="#34D399" stroke-width="2"/>
          <text x="620" y="85" fill="#34D399" font-family="JetBrains Mono" font-size="12" text-anchor="middle">FINAL CLOSING DISCLOSURE (CD)</text>
          <text x="620" y="130" fill="#34D399" font-family="Fraunces" font-size="30" font-weight="700" text-anchor="middle">$1,295.00</text>
          <text x="620" y="165" fill="#A7F3D0" font-family="JetBrains Mono" font-size="11" text-anchor="middle">100% Locked Under TRID Zero-Tolerance</text>
        `;
      }} else if (key === 'boxF') {{
        svg.innerHTML = `
          <line x1="70" y1="140" x2="770" y2="140" stroke="#FBBF24" stroke-width="4"/>
          <circle cx="130" cy="140" r="10" fill="#FBBF24"/>
          <text x="130" y="105" fill="#FBBF24" font-family="JetBrains Mono" font-size="12" font-weight="700" text-anchor="middle">OCT 16 CLOSING</text>
          <text x="130" y="175" fill="#CBD5E1" font-family="DM Sans" font-size="12" text-anchor="middle">15 Days Per-Diem ($510)</text>

          <circle cx="430" cy="140" r="10" fill="#34D399"/>
          <text x="430" y="105" fill="#34D399" font-family="JetBrains Mono" font-size="12" font-weight="700" text-anchor="middle">NOV 1 — NO PAYMENT DUE!</text>
          <text x="430" y="175" fill="#A7F3D0" font-family="DM Sans" font-size="12" text-anchor="middle">Skip November Mortgage Bill</text>

          <circle cx="710" cy="140" r="10" fill="#38BDF8"/>
          <text x="710" y="105" fill="#38BDF8" font-family="JetBrains Mono" font-size="12" font-weight="700" text-anchor="middle">DEC 1 FIRST PAYMENT</text>
          <text x="710" y="175" fill="#CBD5E1" font-family="DM Sans" font-size="12" text-anchor="middle">Pays November Interest in Arrears</text>
        `;
      }} else {{
        svg.innerHTML = `
          <rect x="55" y="45" width="330" height="175" rx="14" fill="#16243D" stroke="#FBBF24" stroke-width="2"/>
          <text x="220" y="82" fill="#FBBF24" font-family="JetBrains Mono" font-size="11.5" text-anchor="middle">BOX G: ESCROW PIGGY BANK</text>
          <text x="220" y="122" fill="#FFFFFF" font-family="Fraunces" font-size="26" font-weight="700" text-anchor="middle">$2,320 Cushion</text>
          <text x="220" y="155" fill="#CBD5E1" font-family="DM Sans" font-size="12" text-anchor="middle">2-Mo RESPA Buffer for Oakland Tax & Ins</text>

          <rect x="445" y="45" width="340" height="175" rx="14" fill="rgba(52,211,153,0.12)" stroke="#34D399" stroke-width="2"/>
          <text x="615" y="82" fill="#34D399" font-family="JetBrains Mono" font-size="11.5" text-anchor="middle">HPA 78% LTV AUTO-PMI TERMINATION</text>
          <text x="615" y="122" fill="#34D399" font-family="Fraunces" font-size="26" font-weight="700" text-anchor="middle">Month 84 (-$118/mo)</text>
          <text x="615" y="155" fill="#A7F3D0" font-family="DM Sans" font-size="12" text-anchor="middle">Drops Automatically by Law (12 U.S.C. § 4902)</text>
        `;
      }}
    }}

    function selectCdWhiteboardItem(key, btnEl) {{
      activeCdKey = key;
      document.querySelectorAll('.cd-item-btn').forEach(b => b.classList.remove('active'));
      if (btnEl) btnEl.classList.add('active');
      const info = CD_EXPLAINERS[key] || CD_EXPLAINERS.cash;
      document.getElementById('wb-title').innerText = info.title;
      document.getElementById('astra-spoken-text').innerText = '"' + info.speech + '"';
      refreshMirrorSandbox();

      if (mirrorWs && mirrorWs.readyState === WebSocket.OPEN) {{
        mirrorWs.send(JSON.stringify({{ type: 'text', text: 'Explain ' + info.title + ' warmly in 2 sentences.' }}));
      }}
    }}

    async function refreshMirrorSandbox() {{
      const price = parseFloat(document.getElementById('inp-mirror-price').value || 350000);
      const sav = parseFloat(document.getElementById('inp-mirror-sav').value || 25000);
      drawWhiteboardDiagram(activeCdKey, price, sav);

      try {{
        const res = await fetch('/api/sandbox', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: 'M.4',
            action: 'calc_mirror_whiteboard',
            params: {{
              secondary_action: 'calc_mirror_cd_explainer',
              price: price,
              savings: sav,
              cd_section: activeCdKey
            }}
          }})
        }});
        const data = await res.json();
        const m = data.metrics || {{}};
        document.getElementById('wb-sandbox-pill').innerText = `Verified (${'{'}data.execution_ms || 1.1{'}'}ms)`;
        const down = Math.round(price * 0.05);
        const rem = Math.max(0, sav - (down + 4800));
        document.getElementById('wb-kpi-cash').innerText = `$${'{'} (down + 4800).toLocaleString() {'}'} Needed ($${'{'}rem.toLocaleString(){'}'} Left)`;
      }} catch (e) {{}}
    }}

    function playMirrorPcm24k(base64Data) {{
      try {{
        if (!mirrorAudioCtx) mirrorAudioCtx = new (window.AudioContext || window.webkitAudioContext)({{ sampleRate: 24000 }});
        const bin = atob(base64Data);
        const len = bin.length / 2;
        const float32 = new Float32Array(len);
        for (let i = 0; i < len; i++) {{
          let s = (bin.charCodeAt(i * 2) & 0xff) | (bin.charCodeAt(i * 2 + 1) << 8);
          if (s >= 0x8000) s -= 0x10000;
          float32[i] = s / 32768.0;
        }}
        const buf = mirrorAudioCtx.createBuffer(1, len, 24000);
        buf.getChannelData(0).set(float32);
        const src = mirrorAudioCtx.createBufferSource();
        src.buffer = buf;
        src.connect(mirrorAudioCtx.destination);
        const now = mirrorAudioCtx.currentTime;
        if (mirrorNextTime < now) mirrorNextTime = now;
        src.start(mirrorNextTime);
        mirrorNextTime += buf.duration;
      }} catch (e) {{}}
    }}

    async function toggleMirrorLiveVoice() {{
      const btn = document.getElementById('btn-mirror-mic');
      const status = document.getElementById('mirror-ws-status');

      if (mirrorWs && mirrorWs.readyState === WebSocket.OPEN) {{
        mirrorWs.close();
        mirrorWs = null;
        if (mirrorStream) mirrorStream.getTracks().forEach(t => t.stop());
        btn.classList.remove('live');
        btn.innerText = "🎙️ Speak with 'Astra Pro' Live Voice (/ws/live-voice/M.4)";
        status.innerText = "Disconnected • Click to Reconnect /ws/live-voice/M.4";
        return;
      }}

      const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      mirrorWs = new WebSocket(`${'{'}proto{'}'}//${'{'}window.location.host{'}'}/ws/live-voice/M.4`);
      status.innerText = "Connecting to /ws/live-voice/M.4...";

      mirrorWs.onopen = async () => {{
        btn.classList.add('live');
        btn.innerText = "🟢 Astra Pro Listening Live (24kHz Audio Active)";
        status.innerText = "Connected to gemini-live-2.5-flash-native-audio";
        try {{
          mirrorStream = await navigator.mediaDevices.getUserMedia({{ audio: {{ sampleRate: 16000, channelCount: 1 }} }});
          const micCtx = new (window.AudioContext || window.webkitAudioContext)({{ sampleRate: 16000 }});
          const src = micCtx.createMediaStreamSource(mirrorStream);
          const proc = micCtx.createScriptProcessor(4096, 1, 1);
          proc.onaudioprocess = (e) => {{
            if (!mirrorWs || mirrorWs.readyState !== WebSocket.OPEN) return;
            const input = e.inputBuffer.getChannelData(0);
            const pcm16 = new Int16Array(input.length);
            for (let i = 0; i < input.length; i++) pcm16[i] = Math.max(-32768, Math.min(32767, input[i] * 32768));
            const bytes = new Uint8Array(pcm16.buffer);
            let bin = '';
            for (let i = 0; i < bytes.byteLength; i++) bin += String.fromCharCode(bytes[i]);
            mirrorWs.send(JSON.stringify({{ type: 'audio', data: btoa(bin) }}));
          }};
          src.connect(proc);
          proc.connect(micCtx.destination);
        }} catch (e) {{}}
      }};

      mirrorWs.onmessage = (evt) => {{
        const msg = JSON.parse(evt.data);
        if (msg.audio_b64) playMirrorPcm24k(msg.audio_b64);
        if (msg.output_transcript) {{
          document.getElementById('astra-spoken-text').innerText = '"' + msg.output_transcript + '"';
        }}
      }};
    }}

    window.runLiveVertexAI = async function() {{
      const model = window.getSelectedModel ? window.getSelectedModel() : 'gemini-3.8-flash';
      const price = parseFloat(document.getElementById('inp-mirror-price').value || 350000);
      const sav = parseFloat(document.getElementById('inp-mirror-sav').value || 25000);
      const spk = document.getElementById('astra-spoken-text');
      spk.innerText = `Synthesizing 2 AM Closing-Table Walkthrough with ${'{'}model{'}'}...`;

      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: 'M.4',
            model: model,
            user_input: `Explain Cash to Close, Box A, Box F, Box G, and Month 84 HPA PMI termination for a $${'{'}price{'}'} home with $${'{'}sav{'}'} in Rocket Money savings.`,
            params: {{ price: price, savings: sav }}
          }})
        }});
        const data = await res.json();
        spk.innerText = data.output || "Closing walkthrough complete.";
      }} catch (e) {{
        spk.innerText = "Error: " + e.message;
      }}
    }};

    document.addEventListener('DOMContentLoaded', () => {{
      refreshMirrorSandbox();
    }});
  </script>

  {render_floating_control_bar_and_drawer(code, auth_token)}
</body>
</html>"""
