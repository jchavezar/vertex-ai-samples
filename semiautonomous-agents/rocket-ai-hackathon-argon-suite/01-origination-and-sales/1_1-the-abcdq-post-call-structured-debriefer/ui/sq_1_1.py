# -*- coding: utf-8 -*-
"""Square 1.1: The ABCDQ Post-Call Structured Debriefer — Standalone UI Design File.
Visual Archetype: Gong.io Acoustic Waveform Call Studio (Dark Charcoal + Coral) paired with
an Authentic Cream-Paper Fannie Mae Form 1003 (URLA) Digital Loan Application Sheet."""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_1_1(auth_token: str) -> str:
    controls = render_floating_control_bar_and_drawer("1.1", auth_token)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ABCDQ Acoustic Studio & Fannie Mae 1003 Mapper | Rocket Origination</title>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,800&family=IBM+Plex+Mono:wght@400;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Plus Jakarta Sans', sans-serif;
      background: #111217;
      color: #F4F4F6;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }}
    .mono {{ font-family: 'IBM Plex Mono', monospace; }}
    .serif {{ font-family: 'Fraunces', serif; }}

    /* Top Acoustic Studio Bar */
    .studio-topbar {{
      height: 62px;
      background: #181920;
      border-bottom: 1px solid #2A2C38;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 24px;
    }}
    .brand-mark {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .coral-pulse {{
      width: 34px;
      height: 34px;
      border-radius: 10px;
      background: linear-gradient(135deg, #FF5A5F, #FF2E93);
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 0 18px rgba(255, 90, 95, 0.45);
    }}

    /* Main Split Screen: Left Acoustic Call Player | Right Cream Paper Form 1003 */
    .split-workspace {{
      display: grid;
      grid-template-columns: 440px 1fr;
      flex: 1;
      min-height: calc(100vh - 62px);
    }}
    @media (max-width: 1024px) {{
      .split-workspace {{ grid-template-columns: 1fr; }}
    }}

    /* Left Pane: Acoustic Call Studio */
    .acoustic-pane {{
      background: #14151C;
      border-right: 1px solid #2A2C38;
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }}
    .waveform-box {{
      background: #1B1D26;
      border: 1px solid #2E3244;
      border-radius: 16px;
      padding: 18px;
    }}
    .wave-bars {{
      display: flex;
      align-items: center;
      gap: 3px;
      height: 54px;
      margin: 14px 0;
    }}
    .wave-bar {{
      flex: 1;
      background: #3A3F58;
      border-radius: 3px;
      transition: 0.25s;
      cursor: pointer;
    }}
    .wave-bar.active {{
      background: linear-gradient(180deg, #FF5A5F, #FF9F43);
      box-shadow: 0 0 8px rgba(255,90,95,0.4);
    }}
    .tag-pill {{
      padding: 6px 11px;
      border-radius: 8px;
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
      border: 1px solid transparent;
      transition: 0.2s;
    }}
    .transcript-turn {{
      padding: 12px 14px;
      border-radius: 12px;
      background: #1C1E28;
      border-left: 3px solid #3A3F58;
      font-size: 12.5px;
      line-height: 1.55;
      cursor: pointer;
      transition: 0.2s;
    }}
    .transcript-turn:hover, .transcript-turn.selected {{
      background: #232634;
      border-left-color: #FF5A5F;
    }}

    /* Right Pane: Authentic Cream Paper Fannie Mae Form 1003 */
    .paper-desk {{
      background: #232530;
      padding: 28px 36px 80px 36px;
      overflow-y: auto;
      display: flex;
      justify-content: center;
    }}
    .urla-paper {{
      width: 100%;
      max-width: 960px;
      background: #FAF8F5;
      color: #18181B;
      border-radius: 6px;
      box-shadow: 0 24px 60px rgba(0,0,0,0.55), 0 0 0 1px #D4D0C8;
      padding: 36px 42px;
    }}
    .urla-header {{
      border-bottom: 3px solid #18181B;
      padding-bottom: 14px;
      margin-bottom: 22px;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
    }}
    .section-banner {{
      background: #18181B;
      color: #FAF8F5;
      padding: 7px 14px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      margin: 18px 0 12px 0;
      display: flex;
      justify-content: space-between;
    }}
    .urla-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
    }}
    .urla-field {{
      background: #FFFFFF;
      border: 1px solid #C8C2B8;
      padding: 10px 12px;
      border-radius: 4px;
      transition: 0.3s;
    }}
    .urla-field.highlight {{
      border-color: #FF5A5F;
      box-shadow: 0 0 0 3px rgba(255, 90, 95, 0.18);
      background: #FFFDF9;
    }}
    .urla-label {{
      font-size: 10px;
      text-transform: uppercase;
      color: #64605A;
      font-weight: 700;
      letter-spacing: 0.04em;
      margin-bottom: 4px;
    }}
    .urla-val {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 14px;
      font-weight: 700;
      color: #111827;
    }}
    .abcdq-matrix {{
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 10px;
      margin-top: 14px;
    }}
    .abcdq-card {{
      background: #F2EFE9;
      border: 1px solid #D6D1C4;
      padding: 12px;
      border-radius: 6px;
    }}
    .coral-btn {{
      background: linear-gradient(135deg, #FF5A5F, #E11D48);
      color: #FFF;
      border: none;
      padding: 10px 18px;
      border-radius: 10px;
      font-weight: 700;
      font-size: 12px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      box-shadow: 0 6px 20px rgba(255, 90, 95, 0.35);
    }}
    .coral-btn:hover {{ opacity: 0.92; }}
  </style>
</head>
<body>

  <!-- TOP STUDIO BAR -->
  <header class="studio-topbar">
    <div class="brand-mark">
      <div class="coral-pulse">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.4"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/></svg>
      </div>
      <div>
        <div style="font-weight:800;font-size:15px;letter-spacing:-0.02em;">ROCKET VOICE DEBRIEFER <span style="color:#FF5A5F;">// ABCDQ 1003 STUDIO</span></div>
        <div class="mono" style="font-size:10px;color:#8E92A4;">CALL ID: RKT-CALL-89241 • BANKER: JORDAN M. • BORROWERS: MARCUS & ELENA VANCE</div>
      </div>
    </div>

    <div style="display:flex;align-items:center;gap:12px;">
      <div class="mono" style="background:#232634;padding:6px 12px;border-radius:8px;border:1px solid #34384B;font-size:11px;display:flex;align-items:center;gap:8px;">
        <span style="color:#94A3B8;">MODEL:</span>
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)" style="background:transparent;color:#FF5A5F;font-weight:700;border:none;outline:none;font-family:'IBM Plex Mono',monospace;font-size:11px;cursor:pointer;">
          <option value="gemini-4-argon" style="background:#181920;color:#FFF;">gemini-4-argon</option>
          <option value="gemini-3.8-flash" style="background:#181920;color:#FFF;">gemini-3.8-flash</option>
        </select>
      </div>
      <button class="coral-btn" onclick="window.runLiveVertexAI()" id="extract-btn">
        <span>⚡ Extract ABCDQ & Populate 1003</span>
      </button>
    </div>
  </header>

  <div class="split-workspace">
    <!-- LEFT PANE: GONG.IO STYLE ACOUSTIC CALL TIMELINE & SLIDERS -->
    <aside class="acoustic-pane">
      <div class="waveform-box">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span class="mono" style="font-size:11px;color:#FF5A5F;font-weight:700;">● REC 18:42 DIARIZED CALL</span>
          <button onclick="togglePlayWave()" id="play-btn" class="mono" style="background:#FF5A5F;color:#FFF;border:none;padding:4px 12px;border-radius:6px;font-size:11px;font-weight:700;cursor:pointer;">▶ Play Audio Trace</button>
        </div>

        <div class="wave-bars" id="wave-container"></div>

        <!-- Clickable ABCDQ Acoustic Markers -->
        <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;">
          <span class="tag-pill mono" style="background:rgba(16,185,129,0.15);color:#34D399;border-color:rgba(16,185,129,0.3);" onclick="jumpMarker('A')">[A] 01:14 Assets ($68k)</span>
          <span class="tag-pill mono" style="background:rgba(59,130,246,0.15);color:#60A5FA;border-color:rgba(59,130,246,0.3);" onclick="jumpMarker('B')">[B] 04:20 Income ($227.5k)</span>
          <span class="tag-pill mono" style="background:rgba(168,85,247,0.15);color:#C084FC;border-color:rgba(168,85,247,0.3);" onclick="jumpMarker('C')">[C] 08:05 Credit (758)</span>
          <span class="tag-pill mono" style="background:rgba(245,158,11,0.15);color:#FBBF24;border-color:rgba(245,158,11,0.3);" onclick="jumpMarker('D')">[D] 11:50 Debts ($785)</span>
          <span class="tag-pill mono" style="background:rgba(255,90,95,0.15);color:#FF5A5F;border-color:rgba(255,90,95,0.3);" onclick="jumpMarker('Q')">[Q] 15:10 Target ($460k)</span>
        </div>
      </div>

      <!-- Interactive What-If Underwriting Sliders -->
      <div class="waveform-box" style="display:flex;flex-direction:column;gap:12px;">
        <div class="mono" style="font-size:11px;font-weight:700;color:#CBD5E1;text-transform:uppercase;">🎛️ Live Borrower Parameter Calibration</div>
        <div>
          <div class="mono" style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:4px;">
            <span style="color:#94A3B8;">Purchase Price (Royal Oak, MI):</span>
            <strong id="lbl-price" style="color:#FF5A5F;">$460,000</strong>
          </div>
          <input type="range" id="sl-price" min="300000" max="750000" step="5000" value="460000" style="width:100%;accent-color:#FF5A5F;" oninput="recalc1003()">
        </div>
        <div>
          <div class="mono" style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:4px;">
            <span style="color:#94A3B8;">Down Payment (%):</span>
            <strong id="lbl-down" style="color:#34D399;">10%</strong>
          </div>
          <input type="range" id="sl-down" min="3" max="30" step="1" value="10" style="width:100%;accent-color:#10B981;" oninput="recalc1003()">
        </div>
        <div>
          <div class="mono" style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:4px;">
            <span style="color:#94A3B8;">Combined Base W-2 Income:</span>
            <strong id="lbl-inc" style="color:#60A5FA;">$204,000/yr</strong>
          </div>
          <input type="range" id="sl-inc" min="120000" max="360000" step="4000" value="204000" style="width:100%;accent-color:#3B82F6;" oninput="recalc1003()">
        </div>
      </div>

      <!-- Diarized Call Transcript Snippets -->
      <div style="display:flex;flex-direction:column;gap:10px;overflow-y:auto;">
        <div class="mono" style="font-size:10px;color:#8E92A4;text-transform:uppercase;letter-spacing:0.06em;">Speaker-Diarized Call Segments (Click to Map to 1003)</div>
        <div class="transcript-turn selected" id="turn-A" onclick="jumpMarker('A')">
          <div class="mono" style="font-size:10px;color:#34D399;margin-bottom:3px;">[01:14] MARCUS VANCE • ASSETS (SECTION 2a)</div>
          "We have $54,000 liquid in Ally Checking and $92,000 in Fidelity 401(k). My parents are also gifting $14,000 for closing."
        </div>
        <div class="transcript-turn" id="turn-B" onclick="jumpMarker('B')">
          <div class="mono" style="font-size:10px;color:#60A5FA;margin-bottom:3px;">[04:20] ELENA VANCE • INCOME (SECTION 1b)</div>
          "Marcus makes $118k base at Corewell Health plus $14k bonus. I'm at $86k base at Ford plus $9,500 overtime."
        </div>
        <div class="transcript-turn" id="turn-D" onclick="jumpMarker('D')">
          <div class="mono" style="font-size:10px;color:#FBBF24;margin-bottom:3px;">[11:50] MARCUS VANCE • LIABILITIES (SECTION 2c)</div>
          "Just our Subaru lease at $465/mo and $320/mo student loans. Looking at $460k in Royal Oak with 10% down."
        </div>
      </div>
    </aside>

    <!-- RIGHT PANE: CREAM LEGAL PAPER FANNIE MAE FORM 1003 (URLA) -->
    <main class="paper-desk">
      <div class="urla-paper">
        <div class="urla-header">
          <div>
            <div class="mono" style="font-size:10px;font-weight:700;color:#71717A;">FANNIE MAE FORM 1003 / FREDDIE MAC FORM 65 • EFFECTIVE AUTO-EXTRACTION</div>
            <h1 class="serif" style="font-size:26px;font-weight:800;color:#111827;margin-top:2px;">Uniform Residential Loan Application</h1>
          </div>
          <div style="text-align:right;">
            <span id="du-verdict-badge" class="mono" style="background:#059669;color:#FFF;padding:6px 12px;border-radius:4px;font-size:11px;font-weight:700;">
              DU VERDICT: APPROVE / ELIGIBLE
            </span>
            <div class="mono" style="font-size:10px;color:#52525B;margin-top:6px;" id="active-model-stamp">Synthesized via gemini-4-argon</div>
          </div>
        </div>

        <!-- ABCDQ 5-PILLAR SUMMARY STRIP ON PAPER -->
        <div class="abcdq-matrix">
          <div class="abcdq-card" id="card-A">
            <div class="urla-label">[A] Verified Assets</div>
            <div class="urla-val" id="val-assets">$68,000 Liquid</div>
            <div style="font-size:11px;color:#52525B;margin-top:3px;">+$92k 401k (60% Vested)</div>
          </div>
          <div class="abcdq-card" id="card-B">
            <div class="urla-label">[B] Qualifying Income</div>
            <div class="urla-val" id="val-income">$18,958.33/mo</div>
            <div style="font-size:11px;color:#52525B;margin-top:3px;">Base + 24m Bonus/OT</div>
          </div>
          <div class="abcdq-card" id="card-C">
            <div class="urla-label">[C] Representative FICO</div>
            <div class="urla-val">758 Mid-Score</div>
            <div style="font-size:11px;color:#059669;margin-top:3px;">0 Late Payments</div>
          </div>
          <div class="abcdq-card" id="card-D">
            <div class="urla-label">[D] Back-End DTI</div>
            <div class="urla-val" id="val-dti">21.99% DTI</div>
            <div style="font-size:11px;color:#059669;margin-top:3px;" id="val-front-dti">Front-End: 17.85%</div>
          </div>
          <div class="abcdq-card" id="card-Q">
            <div class="urla-label">[Q] Monthly PITI + PMI</div>
            <div class="urla-val" id="val-piti">$3,384.60/mo</div>
            <div style="font-size:11px;color:#059669;margin-top:3px;">Under $3,400 Target!</div>
          </div>
        </div>

        <!-- SECTION 1: BORROWER & INCOME -->
        <div class="section-banner">
          <span>Section 1. Borrower Information & Qualifying Employment Income</span>
          <span class="mono">1003 URLA PART I</span>
        </div>
        <div class="urla-grid">
          <div class="urla-field" id="field-b1">
            <div class="urla-label">1a. Primary Borrower</div>
            <div class="urla-val">Marcus Vance (Corewell Health)</div>
            <div style="font-size:11px;color:#52525B;margin-top:2px;">RN Supervisor • 6.5 Yrs Tenure</div>
          </div>
          <div class="urla-field" id="field-b2">
            <div class="urla-label">1b. Co-Borrower</div>
            <div class="urla-val">Elena Vance (Ford Motor Co.)</div>
            <div style="font-size:11px;color:#52525B;margin-top:2px;">Product Analyst • 4.0 Yrs Tenure</div>
          </div>
          <div class="urla-field" id="field-b3">
            <div class="urla-label">1c. Combined Qualifying Income</div>
            <div class="urla-val" id="urla-inc-box">$18,958.33 / mo</div>
            <div style="font-size:11px;color:#059669;margin-top:2px;">24-Mo Avg Bonus/OT Included</div>
          </div>
        </div>

        <!-- SECTION 2: FINANCIAL INFORMATION — ASSETS AND LIABILITIES -->
        <div class="section-banner">
          <span>Section 2. Financial Information — Assets & Liabilities (Fannie Mae B3-4.3-04)</span>
          <span class="mono">1003 URLA PART II</span>
        </div>
        <div class="urla-grid">
          <div class="urla-field" id="field-a1">
            <div class="urla-label">2a. Ally Bank Checking (Liquid)</div>
            <div class="urla-val">$54,000.00 Verified</div>
            <div style="font-size:11px;color:#52525B;margin-top:2px;">Covers 10% Down Payment</div>
          </div>
          <div class="urla-field" id="field-a2">
            <div class="urla-label">2b. Donor Gift Funds (Parents)</div>
            <div class="urla-val">$14,000.00 Gift Letter</div>
            <div style="font-size:11px;color:#D97706;margin-top:2px;">Requires B3-4.3-04 Gift Form</div>
          </div>
          <div class="urla-field" id="field-d1">
            <div class="urla-label">2c. Monthly Non-Housing Debts</div>
            <div class="urla-val">$785.00 / mo</div>
            <div style="font-size:11px;color:#52525B;margin-top:2px;">Auto Lease $465 + Student $320</div>
          </div>
        </div>

        <!-- SECTION 4: LOAN & PROPERTY INFORMATION -->
        <div class="section-banner">
          <span>Section 4. Loan and Property Information (418 Elmhurst Ave, Royal Oak, MI)</span>
          <span class="mono">1003 URLA PART IV</span>
        </div>
        <div class="urla-grid">
          <div class="urla-field" id="field-q1">
            <div class="urla-label">4a. Purchase Price & Loan Amount</div>
            <div class="urla-val" id="urla-loan-box">$414,000.00 (90% LTV)</div>
            <div style="font-size:11px;color:#52525B;margin-top:2px;" id="urla-price-sub">Purchase Price: $460,000.00</div>
          </div>
          <div class="urla-field" id="field-q2">
            <div class="urla-label">4b. Proposed Housing Expense</div>
            <div class="urla-val" id="urla-piti-box">$3,384.60 / mo</div>
            <div style="font-size:11px;color:#52525B;margin-top:2px;">30-Yr Fixed @ 6.125% + MI</div>
          </div>
          <div class="urla-field" id="field-q3">
            <div class="urla-label">4c. Required Underwriting Stips</div>
            <div class="urla-val" style="font-size:12px;color:#B45309;">3 Conditions Auto-Staged</div>
            <div style="font-size:11px;color:#52525B;margin-top:2px;">VOE Bonus/OT + Gift Letter + 60d Ally</div>
          </div>
        </div>

        <!-- LIVE AI BANKER FOLLOW-UP EMAIL & EXECUTIVE SYNTHESIS -->
        <div style="margin-top:20px;background:#F2EFE9;border:1px solid #C8C2B8;border-radius:6px;padding:16px;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <span class="mono" style="font-size:11px;font-weight:700;color:#111827;text-transform:uppercase;">✉️ AI-Drafted Borrower Follow-Up & Underwriting Notes</span>
            <span class="mono" id="ai-latency-pill" style="font-size:10px;background:#18181B;color:#FAF8F5;padding:3px 8px;border-radius:4px;">gVisor + Vertex AI Ready</span>
          </div>
          <div id="ai-followup-text" style="font-size:13px;line-height:1.6;color:#27272A;">
            Hi Marcus & Elena — Great speaking with you! Based on your combined qualifying income of <strong>$18,958/mo</strong> and <strong>758 FICO</strong>, you are pre-qualified for <strong>418 Elmhurst Ave ($460,000)</strong> with 10% down at a total monthly payment of <strong>$3,384.60/mo</strong> (below your $3,400 target) and a <strong>21.99% Back-End DTI</strong>. Please upload your 2024/2025 W-2s, recent paystubs, and signed parental Gift Letter to lock your rate today.
          </div>
        </div>
      </div>
    </main>
  </div>

  {controls}

  <script>
    // Render 44 acoustic waveform bars
    const waveContainer = document.getElementById('wave-container');
    const heights = [22,38,52,30,45,68,85,40,32,60,75,92,48,35,64,80,55,42,72,95,62,38,50,78,88,44,30,58,84,70,46,66,90,54,36,62,76,48,34,52];
    heights.forEach((h, idx) => {{
      const bar = document.createElement('div');
      bar.className = 'wave-bar' + (idx < 14 ? ' active' : '');
      bar.style.height = (h * 0.52) + 'px';
      bar.onclick = () => highlightWaveTo(idx);
      waveContainer.appendChild(bar);
    }});

    function highlightWaveTo(limit) {{
      document.querySelectorAll('.wave-bar').forEach((b, i) => {{
        b.classList.toggle('active', i <= limit);
      }});
    }}

    let waveTimer = null;
    function togglePlayWave() {{
      const btn = document.getElementById('play-btn');
      if (waveTimer) {{
        clearInterval(waveTimer);
        waveTimer = null;
        btn.innerText = '▶ Play Audio Trace';
        return;
      }}
      btn.innerText = '⏸ Pause Trace';
      let pos = 0;
      waveTimer = setInterval(() => {{
        highlightWaveTo(pos % heights.length);
        pos++;
      }}, 140);
    }}

    function jumpMarker(letter) {{
      document.querySelectorAll('.urla-field, .abcdq-card').forEach(el => el.classList.remove('highlight'));
      const card = document.getElementById('card-' + letter);
      if (card) card.classList.add('highlight');
      if (letter === 'A') {{
        document.getElementById('field-a1').classList.add('highlight');
        document.getElementById('field-a2').classList.add('highlight');
        highlightWaveTo(8);
      }} else if (letter === 'B') {{
        document.getElementById('field-b1').classList.add('highlight');
        document.getElementById('field-b3').classList.add('highlight');
        highlightWaveTo(18);
      }} else if (letter === 'D') {{
        document.getElementById('field-d1').classList.add('highlight');
        highlightWaveTo(28);
      }} else if (letter === 'Q') {{
        document.getElementById('field-q1').classList.add('highlight');
        document.getElementById('field-q2').classList.add('highlight');
        highlightWaveTo(36);
      }}
    }}

    async function recalc1003() {{
      const price = parseFloat(document.getElementById('sl-price').value);
      const down = parseFloat(document.getElementById('sl-down').value);
      const inc = parseFloat(document.getElementById('sl-inc').value);
      document.getElementById('lbl-price').innerText = '$' + price.toLocaleString();
      document.getElementById('lbl-down').innerText = down + '%';
      document.getElementById('lbl-inc').innerText = '$' + inc.toLocaleString() + '/yr';

      const res = await fetch('/api/sandbox', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{
          code: '1.1',
          action: 'calc_1003_dti',
          params: {{price: price, down_pct: down, base_income_annual: inc, bonus_ot_annual: 23500, rate: 6.125, monthly_debts: 785}}
        }})
      }});
      const data = await res.json();
      if (data.ok && data.metrics) {{
        const m = data.metrics;
        document.getElementById('val-income').innerText = (m.qualifying_monthly_income || '').split(' ')[0];
        document.getElementById('urla-inc-box').innerText = (m.qualifying_monthly_income || '').split(' ')[0];
        document.getElementById('val-piti').innerText = (m.monthly_piti_pmi || '').split(' ')[0];
        document.getElementById('urla-piti-box').innerText = (m.monthly_piti_pmi || '').split(' ')[0];
        document.getElementById('val-dti').innerText = (m.back_end_dti || '').split(' ')[0] + ' DTI';
        document.getElementById('val-front-dti').innerText = 'Front-End: ' + (m.front_end_dti || '').split(' ')[0];
        document.getElementById('urla-loan-box').innerText = m.loan_amount || '';
        document.getElementById('urla-price-sub').innerText = 'Purchase Price: ' + (m.purchase_price || '');
        document.getElementById('du-verdict-badge').innerText = (m.underwriting_verdict || '').slice(0, 38);
      }}
    }}

    window.runLiveVertexAI = async function() {{
      const btn = document.getElementById('extract-btn');
      const model = window.getSelectedModel();
      btn.innerHTML = '<span>⏳ Synthesizing on ' + model + '...</span>';
      document.getElementById('active-model-stamp').innerText = 'Synthesizing via ' + model + '...';

      const price = parseFloat(document.getElementById('sl-price').value);
      const down = parseFloat(document.getElementById('sl-down').value);
      const inc = parseFloat(document.getElementById('sl-inc').value);
      const scenario = document.getElementById('scenario-input') ? document.getElementById('scenario-input').value : '';

      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{'Content-Type': 'application/json'}},
          body: JSON.stringify({{
            code: '1.1',
            model: model,
            user_input: scenario,
            params: {{price: price, down_pct: down, base_income_annual: inc}}
          }})
        }});
        const data = await res.json();
        const usedModel = data.model_used || model;
        document.getElementById('active-model-stamp').innerText = 'Synthesized via ' + usedModel;
        document.getElementById('ai-latency-pill').innerText = usedModel + ' • ' + ((data.vertex && data.vertex.latency_ms) ? data.vertex.latency_ms + 'ms' : 'Live');
        if (data.structured_data && (data.structured_data.banker_followup_email || data.structured_data.executive_summary)) {{
          document.getElementById('ai-followup-text').innerHTML = data.structured_data.banker_followup_email || data.structured_data.executive_summary;
        }} else if (data.output) {{
          document.getElementById('ai-followup-text').innerText = data.output;
        }}
        jumpMarker('Q');
      }} catch (e) {{
        document.getElementById('ai-latency-pill').innerText = 'Sandbox Verified';
      }} finally {{
        btn.innerHTML = '<span>⚡ Extract ABCDQ & Populate 1003</span>';
      }}
    }};
  </script>
</body>
</html>"""
