# -*- coding: utf-8 -*-
"""Square 1.1: The ABCDQ Post-Call Structurer
Real-World Design Archetype: Encompass Digital Lending LOS + Gong.io Light Call Studio & Printable Fannie Mae Form 1003.
Palette: Warm Light Enterprise Gray (#F4F5F7), Pure White Paper (#FFFFFF), Encompass Royal Blue (#0052CC),
Approved Forest Green (#006644), Ink Charcoal (#172B4D).
Typography: Plus Jakarta Sans (UI & Controls) + Merriweather (Official Form 1003 Document Headings).
Audio: Real 24kHz HD Multi-Speaker Audio powered by Vertex AI Gemini 3.8 Live (/api/live-tts & /ws/live-voice/1.1).
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_1_1(auth_token: str) -> str:
    code = "1.1"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Rocket Mortgage Encompass LOS · ABCDQ Call Debriefer & Form 1003</title>
  <link href="https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700;900&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-canvas: #F4F5F7;
      --surface-card: #FFFFFF;
      --surface-muted: #FAFBFC;
      --ink-primary: #172B4D;
      --ink-secondary: #42526E;
      --ink-muted: #6B778C;
      --border-line: #DFE1E6;
      --brand-blue: #0052CC;
      --brand-blue-soft: #DEEBFF;
      --rocket-red: #C8102E;
      --rocket-red-soft: #FFEBE6;
      --status-green: #006644;
      --status-green-soft: #E3FCEF;
      --status-amber: #FF8B00;
      --status-amber-soft: #FFFAE6;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: var(--bg-canvas);
      color: var(--ink-primary);
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      min-height: 100vh;
      padding-bottom: 88px;
      -webkit-font-smoothing: antialiased;
    }}
    .tabular {{ font-variant-numeric: tabular-nums; }}

    /* Clean Enterprise Top Navigation Bar (3-Zone Contract) */
    .top-navbar {{
      background: var(--surface-card);
      border-bottom: 1px solid var(--border-line);
      padding: 14px 32px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 24px;
      position: sticky;
      top: 0;
      z-index: 40;
      box-shadow: 0 1px 3px rgba(9, 30, 66, 0.06);
    }}
    .brand-wordmark {{
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 17px;
      font-weight: 800;
      color: var(--ink-primary);
      letter-spacing: -0.02em;
      white-space: nowrap;
    }}
    .brand-mark-badge {{
      width: 34px;
      height: 34px;
      border-radius: 8px;
      background: var(--rocket-red);
      color: #FFFFFF;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 15px;
    }}
    .nav-links {{
      display: flex;
      align-items: center;
      gap: 24px;
      font-size: 13.5px;
      font-weight: 600;
      color: var(--ink-secondary);
    }}
    .nav-links span {{
      cursor: pointer;
      padding: 4px 0;
      border-bottom: 2px solid transparent;
      white-space: nowrap;
    }}
    .nav-links span.active {{
      color: var(--brand-blue);
      border-bottom-color: var(--brand-blue);
    }}
    .top-actions {{
      display: flex;
      align-items: center;
      gap: 12px;
      flex-shrink: 0;
    }}
    .model-picker {{
      padding: 7px 12px;
      border-radius: 8px;
      border: 1px solid var(--border-line);
      background: var(--surface-muted);
      color: var(--ink-primary);
      font-family: inherit;
      font-size: 12.5px;
      font-weight: 600;
      cursor: pointer;
    }}
    .btn-primary-extract {{
      background: var(--brand-blue);
      color: #FFFFFF;
      border: none;
      padding: 9px 18px;
      border-radius: 8px;
      font-family: inherit;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      transition: background 0.15s ease;
      white-space: nowrap;
    }}
    .btn-primary-extract:hover {{ background: #0747A6; }}

    /* Loan File Subheader Ribbon */
    .loan-file-ribbon {{
      max-width: 1520px;
      margin: 18px auto 0;
      padding: 0 28px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 12px;
      font-size: 13px;
      color: var(--ink-secondary);
    }}

    /* Main 2-Column Split Workspace */
    .workspace-split {{
      max-width: 1520px;
      margin: 14px auto 32px;
      padding: 0 28px;
      display: grid;
      grid-template-columns: 440px 1fr;
      gap: 24px;
      align-items: start;
    }}
    @media (max-width: 1120px) {{
      .workspace-split {{ grid-template-columns: 1fr; }}
    }}

    .panel-card {{
      background: var(--surface-card);
      border: 1px solid var(--border-line);
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 2px 6px rgba(9, 30, 66, 0.04);
      margin-bottom: 18px;
    }}

    /* Real Gemini 3.8 Live Recorded Call Player */
    .audio-studio-box {{
      background: #FAFBFC;
      border: 1px solid var(--border-line);
      border-radius: 10px;
      padding: 16px;
      margin-top: 10px;
    }}
    .waveform-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 3px;
      height: 46px;
      margin: 12px 0;
      padding: 0 4px;
    }}
    .wf-bar {{
      flex: 1;
      background: #B3D4FF;
      border-radius: 3px;
      transition: height 0.08s ease, background-color 0.15s ease;
    }}
    .wf-bar.speaking {{
      background: var(--brand-blue);
    }}
    .btn-play-call {{
      width: 100%;
      padding: 11px 16px;
      border-radius: 8px;
      border: none;
      background: var(--rocket-red);
      color: #FFFFFF;
      font-family: inherit;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      transition: opacity 0.15s;
    }}
    .btn-play-call:hover {{ opacity: 0.92; }}
    .btn-live-copilot {{
      width: 100%;
      margin-top: 8px;
      padding: 9px 14px;
      border-radius: 8px;
      border: 1px solid var(--brand-blue);
      background: var(--brand-blue-soft);
      color: var(--brand-blue);
      font-family: inherit;
      font-size: 12.5px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
    }}

    /* ABCDQ Filter Tabs */
    .abcdq-tab-grid {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 12px;
    }}
    .abcdq-btn {{
      padding: 6px 11px;
      border-radius: 6px;
      border: 1px solid var(--border-line);
      background: #FFFFFF;
      color: var(--ink-secondary);
      font-family: inherit;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s;
    }}
    .abcdq-btn:hover, .abcdq-btn.active {{
      background: var(--brand-blue);
      color: #FFFFFF;
      border-color: var(--brand-blue);
    }}

    /* Diarized Speaker Cards with Individual Real Audio Play Buttons */
    .speaker-card {{
      background: #FFFFFF;
      border: 1px solid var(--border-line);
      border-radius: 10px;
      padding: 14px;
      margin-bottom: 10px;
      transition: border-color 0.15s, box-shadow 0.15s;
    }}
    .speaker-card:hover, .speaker-card.active {{
      border-color: var(--brand-blue);
      box-shadow: 0 4px 12px rgba(0, 82, 204, 0.08);
    }}
    .speaker-meta {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 6px;
      font-size: 12px;
      font-weight: 700;
      color: var(--ink-secondary);
    }}
    .btn-listen-clip {{
      padding: 4px 10px;
      border-radius: 6px;
      border: 1px solid var(--brand-blue);
      background: var(--brand-blue-soft);
      color: var(--brand-blue);
      font-family: inherit;
      font-size: 11.5px;
      font-weight: 700;
      cursor: pointer;
    }}
    .btn-listen-clip:hover {{
      background: var(--brand-blue);
      color: #FFFFFF;
    }}

    /* Official Fannie Mae Form 1003 Document Sheet */
    .urla-paper-sheet {{
      background: #FFFFFF;
      border: 1px solid #C1C7D0;
      border-radius: 10px;
      padding: 36px 40px;
      box-shadow: 0 8px 24px rgba(9, 30, 66, 0.07);
    }}
    .urla-doc-header {{
      border-bottom: 2px solid var(--ink-primary);
      padding-bottom: 16px;
      margin-bottom: 22px;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      flex-wrap: wrap;
      gap: 14px;
    }}
    .urla-doc-title {{
      font-family: 'Merriweather', Georgia, serif;
      font-size: 24px;
      font-weight: 900;
      color: var(--ink-primary);
      letter-spacing: -0.01em;
    }}
    .aus-status-badge {{
      display: inline-block;
      padding: 6px 14px;
      border-radius: 6px;
      font-size: 12.5px;
      font-weight: 700;
      background: var(--status-green-soft);
      color: var(--status-green);
      border: 1px solid #79F2C0;
    }}
    .aus-status-badge.warn {{
      background: var(--status-amber-soft);
      color: #B65C02;
      border-color: #FFE380;
    }}

    .abcdq-kpi-strip {{
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 12px;
      margin-bottom: 24px;
    }}
    @media (max-width: 960px) {{
      .abcdq-kpi-strip {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    .abcdq-kpi-box {{
      background: var(--surface-muted);
      border: 1px solid var(--border-line);
      border-radius: 8px;
      padding: 12px 14px;
      transition: all 0.2s;
    }}
    .abcdq-kpi-box.highlighted {{
      background: var(--brand-blue-soft);
      border-color: var(--brand-blue);
    }}
    .kpi-kicker {{
      font-size: 11px;
      font-weight: 700;
      color: var(--ink-muted);
      margin-bottom: 4px;
    }}
    .kpi-val {{
      font-size: 17px;
      font-weight: 800;
      color: var(--ink-primary);
    }}
    .kpi-sub {{
      font-size: 11.5px;
      color: var(--ink-secondary);
      margin-top: 2px;
    }}

    .urla-section-bar {{
      background: #172B4D;
      color: #FFFFFF;
      padding: 8px 14px;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.03em;
      border-radius: 4px;
      margin: 20px 0 12px;
      display: flex;
      justify-content: space-between;
    }}
    .urla-grid-3 {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 14px;
    }}
    @media (max-width: 820px) {{
      .urla-grid-3 {{ grid-template-columns: 1fr; }}
    }}
    .urla-field-cell {{
      border: 1px solid var(--border-line);
      border-radius: 6px;
      padding: 12px 14px;
      background: #FFFFFF;
      transition: all 0.2s;
    }}
    .urla-field-cell.highlighted {{
      background: #FFFDF5;
      border-color: var(--brand-blue);
      box-shadow: 0 0 0 2px rgba(0, 82, 204, 0.15);
    }}
    .field-lbl {{
      font-size: 11px;
      font-weight: 600;
      color: var(--ink-muted);
      margin-bottom: 4px;
    }}
    .field-val {{
      font-size: 14.5px;
      font-weight: 700;
      color: var(--ink-primary);
    }}
    .field-note {{
      font-size: 12px;
      color: var(--ink-secondary);
      margin-top: 3px;
    }}
  </style>
</head>
<body>

  <!-- CLEAN ENTERPRISE LOS TOP BAR -->
  <header class="top-navbar">
    <div class="brand-wordmark">
      <div class="brand-mark-badge">R</div>
      <span>Rocket Mortgage Encompass LOS</span>
    </div>

    <nav class="nav-links">
      <span class="active" onclick="highlight1003Section('ALL', null)">Form 1003 Application</span>
      <span onclick="highlight1003Section('A', null)">Assets & Gift Funds</span>
      <span onclick="highlight1003Section('B', null)">Qualifying Income</span>
      <span onclick="highlight1003Section('D', null)">Debts & DTI Ratio</span>
      <span onclick="window.toggleBlueprintDrawer()">Architecture & SDK</span>
    </nav>

    <div class="top-actions">
      <select id="app-model-select" class="model-picker" onchange="window.syncSelectedModel(this.value)">
        <option value="gemini-4-argon" selected>Gemini 4 Argon (Frontier)</option>
        <option value="gemini-3.8-flash">Gemini 3.8 Flash (Fast ADK)</option>
      </select>
      <button class="btn-primary-extract" onclick="window.runLiveVertexAI()">
        Extract ABCDQ & Populate 1003
      </button>
    </div>
  </header>

  <!-- LOAN FILE CONTEXT RIBBON -->
  <div class="loan-file-ribbon">
    <div>
      <strong>Loan File #RKT-2026-89241</strong> · Borrowers: <strong>Marcus &amp; Elena Vance</strong> · Subject Property: <strong>418 Elmhurst Ave, Royal Oak, MI 48067</strong>
    </div>
    <div>
      Assigned Mortgage Banker: <strong>Jordan M. (NMLS #148920)</strong> · Audio Engine: <strong>Gemini 3.8 Live 24kHz Native Audio</strong>
    </div>
  </div>

  <!-- MAIN 2-COLUMN WORKSPACE -->
  <main class="workspace-split">

    <!-- LEFT COLUMN: REAL GEMINI 3.8 LIVE CALL RECORDING PLAYER & SCENARIO SLIDERS -->
    <aside>
      <!-- Recorded Call & Live Voice Studio -->
      <div class="panel-card">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
          <h2 style="font-size:15px;font-weight:800;color:var(--ink-primary);">Recorded Intake Call &amp; Live Audio</h2>
          <span id="audio-status-tag" style="font-size:11.5px;font-weight:700;color:var(--brand-blue);">24kHz HD Ready</span>
        </div>
        <p style="font-size:12.5px;color:var(--ink-secondary);line-height:1.5;">
          Listen to the diarized intake call between Banker Jordan, Marcus Vance, and Elena Vance—synthesized in real time via <strong>Gemini 3.8 Live</strong>—or click any transcript card below to hear that segment and highlight its Form 1003 fields.
        </p>

        <div class="audio-studio-box">
          <button id="btn-play-full-call" class="btn-play-call" onclick="playFullDiarizedCall(this)">
            ▶ Play Full Borrower Intake Call (Gemini 3.8 Live HD)
          </button>

          <button id="btn-live-bidi-11" class="btn-live-copilot" onclick="toggleLiveBankerCoPilot()">
            🎙️ Talk Live to ABCDQ Underwriting Co-Pilot (Interruptible)
          </button>

          <div id="live-copilot-status" style="display:none;margin-top:8px;padding:8px 10px;border-radius:6px;background:#FFFFFF;border:1px solid var(--border-line);font-size:12px;color:var(--ink-primary);">
          </div>

          <!-- Real-Time WebAudio Frequency Waveform -->
          <div class="waveform-row" id="waveform-container"></div>

          <!-- Clickable ABCDQ Section Filters -->
          <div class="abcdq-tab-grid">
            <button class="abcdq-btn active" onclick="highlight1003Section('ALL', this)">All Sections</button>
            <button class="abcdq-btn" onclick="highlight1003Section('A', this)">A · Assets ($68k)</button>
            <button class="abcdq-btn" onclick="highlight1003Section('B', this)">B · Income ($227.5k)</button>
            <button class="abcdq-btn" onclick="highlight1003Section('C', this)">C · Credit (758)</button>
            <button class="abcdq-btn" onclick="highlight1003Section('D', this)">D · Debts ($785)</button>
            <button class="abcdq-btn" onclick="highlight1003Section('Q', this)">Q · Payment</button>
          </div>
        </div>
      </div>

      <!-- Interactive Loan Scenario Sliders -->
      <div class="panel-card">
        <h3 style="font-size:14px;font-weight:800;color:var(--ink-primary);margin-bottom:12px;">
          Interactive Loan Scenario Calibration
        </h3>

        <div style="margin-bottom:14px;">
          <div style="display:flex;justify-content:space-between;font-size:12.5px;font-weight:600;margin-bottom:4px;">
            <span>Purchase Price (Royal Oak, MI):</span>
            <strong id="lbl-price" class="tabular" style="color:var(--brand-blue);">$460,000</strong>
          </div>
          <input type="range" id="slider-price" min="300000" max="750000" step="5000" value="460000"
                 style="width:100%;accent-color:var(--brand-blue);cursor:pointer;" oninput="recalculate1003()">
        </div>

        <div style="margin-bottom:14px;">
          <div style="display:flex;justify-content:space-between;font-size:12.5px;font-weight:600;margin-bottom:4px;">
            <span>Down Payment (%):</span>
            <strong id="lbl-down" class="tabular" style="color:var(--status-green);">10% ($46,000)</strong>
          </div>
          <input type="range" id="slider-down" min="5" max="25" step="5" value="10"
                 style="width:100%;accent-color:var(--status-green);cursor:pointer;" oninput="recalculate1003()">
        </div>

        <div>
          <div style="display:flex;justify-content:space-between;font-size:12.5px;font-weight:600;margin-bottom:4px;">
            <span>Combined Base W-2 Income:</span>
            <strong id="lbl-inc" class="tabular" style="color:var(--ink-primary);">$204,000/yr</strong>
          </div>
          <input type="range" id="slider-inc" min="140000" max="320000" step="4000" value="204000"
                 style="width:100%;accent-color:var(--brand-blue);cursor:pointer;" oninput="recalculate1003()">
        </div>
      </div>

      <!-- Diarized Speaker Segments with Real Gemini 3.8 Live Audio Playback -->
      <div class="panel-card">
        <div style="font-size:13px;font-weight:800;color:var(--ink-primary);margin-bottom:10px;">
          Diarized Call Transcript (Click to Listen &amp; Map to 1003)
        </div>

        <div class="speaker-card" id="seg-card-A" onclick="highlight1003Section('A', null)">
          <div class="speaker-meta">
            <span>01:14 · Marcus Vance (Assets · Section 2a)</span>
            <button class="btn-listen-clip" onclick="event.stopPropagation(); playSegmentAudio('A', this)">
              🔊 Listen (Puck HD)
            </button>
          </div>
          <p style="font-size:12.5px;color:var(--ink-primary);line-height:1.5;">
            "We have $54,000 liquid in our Ally Bank checking account and $92,000 in my Fidelity 401(k). My parents are also gifting us $14,000 toward closing."
          </p>
        </div>

        <div class="speaker-card" id="seg-card-B" onclick="highlight1003Section('B', null)">
          <div class="speaker-meta">
            <span>04:20 · Elena Vance (Income · Section 1b)</span>
            <button class="btn-listen-clip" onclick="event.stopPropagation(); playSegmentAudio('B', this)">
              🔊 Listen (Aoede HD)
            </button>
          </div>
          <p style="font-size:12.5px;color:var(--ink-primary);line-height:1.5;">
            "Marcus makes $118,000 base salary at Corewell Health plus a $14,000 annual bonus. I'm at $86,000 base at Ford Motor Company plus $9,500 in guaranteed overtime."
          </p>
        </div>

        <div class="speaker-card" id="seg-card-D" onclick="highlight1003Section('D', null)">
          <div class="speaker-meta">
            <span>11:50 · Marcus Vance (Debts &amp; Goal · Section 2c)</span>
            <button class="btn-listen-clip" onclick="event.stopPropagation(); playSegmentAudio('D', this)">
              🔊 Listen (Puck HD)
            </button>
          </div>
          <p style="font-size:12.5px;color:var(--ink-primary);line-height:1.5;">
            "Our only monthly debts are our Subaru lease at $465 a month and $320 a month in student loans. We want to buy at $460,000 in Royal Oak with 10% down and stay under $3,400 a month."
          </p>
        </div>
      </div>
    </aside>

    <!-- RIGHT COLUMN: PRINTABLE FANNIE MAE FORM 1003 (URLA) DOCUMENT -->
    <section class="urla-paper-sheet">
      <div class="urla-doc-header">
        <div>
          <div style="font-size:11.5px;font-weight:700;color:var(--ink-muted);text-transform:uppercase;letter-spacing:0.04em;">
            Fannie Mae Form 1003 · Freddie Mac Form 65 · Automated ABCDQ Structuring
          </div>
          <h1 class="urla-doc-title">Uniform Residential Loan Application</h1>
        </div>
        <div style="text-align:right;">
          <span class="aus-status-badge" id="urla-aus-badge">APPROVE / ELIGIBLE · Under $3,400 Target</span>
          <div style="font-size:11.5px;color:var(--ink-muted);margin-top:4px;">
            Active Model: <strong id="live-model-pill" style="color:var(--brand-blue);">gemini-4-argon</strong>
          </div>
        </div>
      </div>

      <!-- 5-Box ABCDQ Summary Strip -->
      <div class="abcdq-kpi-strip">
        <div class="abcdq-kpi-box" id="box-A">
          <div class="kpi-kicker">A · Verified Assets</div>
          <div class="kpi-val tabular" id="val-assets">$68,000 Liquid</div>
          <div class="kpi-sub">+$92k 401k (60% Vested)</div>
        </div>
        <div class="abcdq-kpi-box" id="box-B">
          <div class="kpi-kicker">B · Qualifying Income</div>
          <div class="kpi-val tabular" id="val-income">$18,958.33/mo</div>
          <div class="kpi-sub">Base + 24m Bonus/OT</div>
        </div>
        <div class="abcdq-kpi-box" id="box-C">
          <div class="kpi-kicker">C · Representative FICO</div>
          <div class="kpi-val tabular">758 Mid-Score</div>
          <div class="kpi-sub" style="color:var(--status-green);font-weight:600;">0 Late Payments</div>
        </div>
        <div class="abcdq-kpi-box" id="box-D">
          <div class="kpi-kicker">D · Back-End DTI</div>
          <div class="kpi-val tabular" id="val-dti">21.99% DTI</div>
          <div class="kpi-sub" id="val-fedti">Front-End: 17.85%</div>
        </div>
        <div class="abcdq-kpi-box" id="box-Q">
          <div class="kpi-kicker">Q · Monthly PITI + PMI</div>
          <div class="kpi-val tabular" id="val-piti">$3,384.60/mo</div>
          <div class="kpi-sub" id="val-target-note" style="color:var(--status-green);font-weight:600;">Saves $15.40 vs Target</div>
        </div>
      </div>

      <!-- Section 1: Borrower & Qualifying Income -->
      <div class="urla-section-bar">
        <span>SECTION 1. BORROWER INFORMATION &amp; QUALIFYING EMPLOYMENT INCOME</span>
        <span>1003 URLA PART I</span>
      </div>
      <div class="urla-grid-3">
        <div class="urla-field-cell sec-B">
          <div class="field-lbl">1a. Primary Borrower</div>
          <div class="field-val">Marcus Vance (Corewell Health)</div>
          <div class="field-note">RN Supervisor · 6.5 Yrs Tenure</div>
        </div>
        <div class="urla-field-cell sec-B">
          <div class="field-lbl">1b. Co-Borrower</div>
          <div class="field-val">Elena Vance (Ford Motor Co.)</div>
          <div class="field-note">Product Analyst · 4.0 Yrs Tenure</div>
        </div>
        <div class="urla-field-cell sec-B">
          <div class="field-lbl">1c. Combined Qualifying Income</div>
          <div class="field-val tabular" id="cell-qual-inc">$18,958.33 / month</div>
          <div class="field-note" style="color:var(--status-green);">24-Month Bonus &amp; OT Averaged</div>
        </div>
      </div>

      <!-- Section 2: Financial Information — Assets & Liabilities -->
      <div class="urla-section-bar">
        <span>SECTION 2. FINANCIAL INFORMATION — ASSETS &amp; LIABILITIES (FANNIE MAE B3-4.3-04)</span>
        <span>1003 URLA PART II</span>
      </div>
      <div class="urla-grid-3">
        <div class="urla-field-cell sec-A">
          <div class="field-lbl">2a. Ally Bank Checking (Liquid)</div>
          <div class="field-val tabular">$54,000.00 Verified</div>
          <div class="field-note" id="cell-down-cov">Covers 10% Down ($46,000)</div>
        </div>
        <div class="urla-field-cell sec-A">
          <div class="field-lbl">2b. Donor Gift Funds (Parents)</div>
          <div class="field-val tabular">$14,000.00 Gift Letter</div>
          <div class="field-note" style="color:#B65C02;">Requires Form B3-4.3-04 Gift Letter</div>
        </div>
        <div class="urla-field-cell sec-D">
          <div class="field-lbl">2c. Monthly Non-Housing Liabilities</div>
          <div class="field-val tabular">$785.00 / month</div>
          <div class="field-note">Subaru Lease $465 + Student $320</div>
        </div>
      </div>

      <!-- Section 4: Loan & Property Information -->
      <div class="urla-section-bar">
        <span>SECTION 4. LOAN AND PROPERTY INFORMATION (418 ELMHURST AVE, ROYAL OAK, MI)</span>
        <span>1003 URLA PART IV</span>
      </div>
      <div class="urla-grid-3">
        <div class="urla-field-cell sec-Q">
          <div class="field-lbl">4a. Purchase Price &amp; Base Loan</div>
          <div class="field-val tabular" id="cell-loan-amt">$414,000.00 (90% LTV)</div>
          <div class="field-note" id="cell-purch-price">Purchase Price: $460,000.00</div>
        </div>
        <div class="urla-field-cell sec-Q">
          <div class="field-lbl">4b. Proposed Monthly Housing Expense</div>
          <div class="field-val tabular" id="cell-piti-breakdown">$3,384.60 / month</div>
          <div class="field-note">30-Yr Fixed @ 6.125% + Taxes/Ins/MI</div>
        </div>
        <div class="urla-field-cell sec-C">
          <div class="field-lbl">4c. Required Underwriting Conditions</div>
          <div class="field-val" style="color:#B65C02;">3 Stipulations Staged</div>
          <div class="field-note">VOE Bonus/OT + Gift Letter + 60d Ally</div>
        </div>
      </div>

      <!-- AI-Drafted Borrower Follow-Up & Underwriting Summary -->
      <div style="margin-top:22px;background:var(--surface-muted);border:1px solid var(--border-line);border-radius:8px;padding:18px 20px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
          <span style="font-size:12px;font-weight:800;color:var(--ink-primary);text-transform:uppercase;">
            Borrower Pre-Approval Follow-Up &amp; Underwriting Notes
          </span>
          <span id="urla-latency-badge" style="font-size:11.5px;font-weight:600;color:var(--status-green);">
            Verified via gVisor Sandbox &amp; Vertex AI
          </span>
        </div>
        <div id="urla-ai-summary" style="font-size:13.5px;line-height:1.65;color:var(--ink-primary);">
          Hi Marcus &amp; Elena — Great speaking with you! Based on your combined qualifying income of <strong>$18,958.33/mo</strong> and <strong>758 FICO</strong>, you are pre-approved for <strong>418 Elmhurst Ave ($460,000)</strong> with 10% down at a total monthly payment of <strong>$3,384.60/mo</strong> (below your $3,400/mo budget) and a <strong>21.99% Back-End DTI</strong>. Please upload your 2024/2025 W-2s, recent paystubs, and signed parental Gift Letter to lock your 6.125% rate today.
        </div>
      </div>
    </section>

  </main>

  {render_floating_control_bar_and_drawer(code, auth_token)}

  <script>
    // Build 32 clean waveform bars
    const wfContainer = document.getElementById('waveform-container');
    const barHeights = [14,22,30,18,36,42,26,18,34,44,28,16,24,38,44,30,20,34,40,24,16,30,42,34,20,28,38,26,18,32,24,14];
    wfContainer.innerHTML = barHeights.map((h, i) =>
      `<div class="wf-bar" id="wf-bar-${{i}}" style="height:${{h}}px;"></div>`
    ).join('');

    function updateWaveformFromAudio(amp, freqArray) {{
      for (let i = 0; i < 32; i++) {{
        const bar = document.getElementById('wf-bar-' + i);
        if (!bar) continue;
        if (!freqArray || amp === 0) {{
          bar.style.height = barHeights[i] + 'px';
          bar.classList.remove('speaking');
        }} else {{
          const val = freqArray[i % freqArray.length] || 60;
          const h = Math.max(8, Math.min(45, Math.round((val / 255) * 45)));
          bar.style.height = h + 'px';
          bar.classList.add('speaking');
        }}
      }}
    }}

    const SEGMENT_SCRIPTS = {{
      'A': {{
        voice: 'Puck',
        role: 'Borrower Marcus Vance on a mortgage intake call',
        text: "We have fifty-four thousand dollars liquid in our Ally Bank checking account, and ninety-two thousand in my Fidelity 401k. My parents are also gifting us fourteen thousand dollars toward closing."
      }},
      'B': {{
        voice: 'Aoede',
        role: 'Co-Borrower Elena Vance on a mortgage intake call',
        text: "Marcus makes one hundred eighteen thousand base salary at Corewell Health plus a fourteen thousand dollar annual bonus. I'm at eighty-six thousand base at Ford Motor Company, plus nine thousand five hundred in overtime."
      }},
      'D': {{
        voice: 'Puck',
        role: 'Borrower Marcus Vance discussing monthly debts and target payment',
        text: "Our only monthly debts are our Subaru lease at four sixty-five a month and three twenty a month in student loans. We're looking at four hundred sixty thousand in Royal Oak with ten percent down, and want to stay under thirty-four hundred a month."
      }}
    }};

    function playSegmentAudio(secKey, btnEl) {{
      highlight1003Section(secKey, null);
      const seg = SEGMENT_SCRIPTS[secKey];
      if (!seg) return;
      const tag = document.getElementById('audio-status-tag');
      if (tag) tag.innerText = `Streaming ${{seg.voice}} 24kHz HD...`;
      window.playLiveCallClip(seg.text, seg.voice, seg.role, btnEl, (amp, arr) => {{
        updateWaveformFromAudio(amp, arr);
        if (amp === 0 && tag) tag.innerText = "24kHz HD Ready";
      }});
    }}

    function playFullDiarizedCall(btnEl) {{
      const fullScript = "Hi Jordan! We have fifty-four thousand dollars liquid in Ally Bank checking, plus a fourteen thousand dollar parental gift for closing. Marcus earns one hundred eighteen thousand base at Corewell Health plus a fourteen thousand bonus, and Elena earns eighty-six thousand at Ford plus ninety-five hundred overtime. With our Subaru lease and student loans totaling seven eighty-five a month, we want to buy at four hundred sixty thousand in Royal Oak with ten percent down under thirty-four hundred a month.";
      const tag = document.getElementById('audio-status-tag');
      if (tag) tag.innerText = "Streaming Gemini 3.8 Live 24kHz...";
      window.playLiveCallClip(fullScript, "Aoede", "Borrowers Marcus and Elena Vance on Rocket Mortgage intake call", btnEl, (amp, arr) => {{
        updateWaveformFromAudio(amp, arr);
        if (amp === 0 && tag) tag.innerText = "24kHz HD Ready";
      }});
    }}

    // Live Bidirectional Co-Pilot WebSocket (/ws/live-voice/1.1)
    let liveWs11 = null;
    function toggleLiveBankerCoPilot() {{
      const btn = document.getElementById('btn-live-bidi-11');
      const statusBox = document.getElementById('live-copilot-status');
      if (liveWs11 && liveWs11.readyState === WebSocket.OPEN) {{
        window.stopAllLiveAudio();
        liveWs11.close();
        liveWs11 = null;
        btn.innerText = "🎙️ Talk Live to ABCDQ Underwriting Co-Pilot (Interruptible)";
        statusBox.style.display = "none";
        return;
      }}
      window.stopAllLiveAudio();
      window.RocketLiveAudio.ensureCtx();
      const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
      liveWs11 = new WebSocket(`${{proto}}//${{window.location.host}}/ws/live-voice/1.1?voice=Kore&live_mode=gemini-3.8-live`);
      statusBox.style.display = "block";
      statusBox.innerHTML = "Connecting to <strong>Gemini 3.8 Live</strong> ABCDQ Co-Pilot (Voice: Kore)...";
      btn.innerText = "⏹ Stop Live ABCDQ Voice Co-Pilot";

      let txBuf = "";
      liveWs11.onopen = () => {{
        liveWs11.send(JSON.stringify({{
          type: "text",
          text: "Give a crisp 2-sentence voice debrief of Marcus and Elena Vance's ABCDQ qualification for 418 Elmhurst Ave at $460,000 with 10% down."
        }}));
      }};
      liveWs11.onmessage = (evt) => {{
        const msg = JSON.parse(evt.data);
        if (msg.interrupted) {{
          window.stopAllLiveAudio();
          return;
        }}
        if (msg.output_transcript) {{
          txBuf += msg.output_transcript;
          statusBox.innerHTML = `<strong>ABCDQ Live Co-Pilot (Kore 24kHz):</strong> ${{txBuf}}`;
        }}
        if (msg.turn_complete) txBuf = "";
        if (msg.audio_b64) {{
          window.RocketLiveAudio.playPcm24kBase64(msg.audio_b64, updateWaveformFromAudio, null);
        }}
      }};
      liveWs11.onclose = () => {{
        btn.innerText = "🎙️ Talk Live to ABCDQ Underwriting Co-Pilot (Interruptible)";
      }};
    }}

    function highlight1003Section(sec, btnEl) {{
      if (btnEl) {{
        document.querySelectorAll('.abcdq-btn').forEach(b => b.classList.remove('active'));
        btnEl.classList.add('active');
      }}
      ['A','B','C','D','Q'].forEach(k => {{
        const box = document.getElementById('box-' + k);
        if (box) box.classList.toggle('highlighted', sec === 'ALL' || sec === k);
      }});
      document.querySelectorAll('.urla-field-cell').forEach(cell => {{
        if (sec === 'ALL') {{
          cell.classList.remove('highlighted');
        }} else {{
          cell.classList.toggle('highlighted', cell.classList.contains('sec-' + sec));
        }}
      }});
    }}

    function recalculate1003() {{
      const price = parseFloat(document.getElementById('slider-price').value);
      const downPct = parseFloat(document.getElementById('slider-down').value);
      const baseInc = parseFloat(document.getElementById('slider-inc').value);

      const downAmt = Math.round(price * (downPct / 100));
      const loanAmt = price - downAmt;
      const ltv = 100 - downPct;

      const monthlyRate = 0.06125 / 12;
      const n = 360;
      const pi = loanAmt * (monthlyRate * Math.pow(1 + monthlyRate, n)) / (Math.pow(1 + monthlyRate, n) - 1);
      const taxesIns = (price * 0.0145) / 12 + 135;
      const pmi = ltv > 80 ? (loanAmt * 0.0042) / 12 : 0;
      const totalPiti = pi + taxesIns + pmi;

      const totalAnnualInc = baseInc + 23500;
      const monthlyQualInc = totalAnnualInc / 12;
      const frontEndDti = (totalPiti / monthlyQualInc) * 100;
      const backEndDti = ((totalPiti + 785) / monthlyQualInc) * 100;

      document.getElementById('lbl-price').innerText = '$' + price.toLocaleString();
      document.getElementById('lbl-down').innerText = downPct + '% ($' + downAmt.toLocaleString() + ')';
      document.getElementById('lbl-inc').innerText = '$' + baseInc.toLocaleString() + '/yr';

      document.getElementById('val-income').innerText = '$' + monthlyQualInc.toLocaleString(undefined, {{minimumFractionDigits:2, maximumFractionDigits:2}}) + '/mo';
      document.getElementById('cell-qual-inc').innerText = '$' + monthlyQualInc.toLocaleString(undefined, {{minimumFractionDigits:2, maximumFractionDigits:2}}) + ' / month';
      document.getElementById('val-dti').innerText = backEndDti.toFixed(2) + '% DTI';
      document.getElementById('val-fedti').innerText = 'Front-End: ' + frontEndDti.toFixed(2) + '%';
      document.getElementById('val-piti').innerText = '$' + totalPiti.toLocaleString(undefined, {{minimumFractionDigits:2, maximumFractionDigits:2}}) + '/mo';

      document.getElementById('cell-loan-amt').innerText = '$' + loanAmt.toLocaleString() + ' (' + ltv + '% LTV)';
      document.getElementById('cell-purch-price').innerText = 'Purchase Price: $' + price.toLocaleString();
      document.getElementById('cell-piti-breakdown').innerText = '$' + totalPiti.toLocaleString(undefined, {{minimumFractionDigits:2, maximumFractionDigits:2}}) + ' / month';
      document.getElementById('cell-down-cov').innerText = 'Covers ' + downPct + '% Down ($' + downAmt.toLocaleString() + ')';

      const badge = document.getElementById('urla-aus-badge');
      const note = document.getElementById('val-target-note');
      if (totalPiti <= 3400) {{
        badge.className = 'aus-status-badge';
        badge.innerText = 'APPROVE / ELIGIBLE · Under $3,400 Target';
        note.style.color = 'var(--status-green)';
        note.innerText = 'Saves $' + (3400 - totalPiti).toFixed(2) + ' vs Target';
      }} else {{
        badge.className = 'aus-status-badge warn';
        badge.innerText = 'APPROVE / CAUTION · Above $3,400 Target';
        note.style.color = '#B65C02';
        note.innerText = '+$' + (totalPiti - 3400).toFixed(2) + ' over $3,400 Target';
      }}
    }}

    window.runLiveVertexAI = async function() {{
      const model = window.getSelectedModel();
      const summaryEl = document.getElementById('urla-ai-summary');
      const latEl = document.getElementById('urla-latency-badge');
      const price = parseFloat(document.getElementById('slider-price').value);
      const downPct = parseFloat(document.getElementById('slider-down').value);
      const baseInc = parseFloat(document.getElementById('slider-inc').value);

      summaryEl.innerHTML = '<em>Synthesizing live Fannie Mae 1003 ABCDQ extraction via Vertex AI (<strong>' + model + '</strong>)...</em>';
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '1.1',
            model: model,
            user_input: document.getElementById('scenario-input') ? document.getElementById('scenario-input').value : '',
            params: {{
              purchase_price: price,
              down_payment_pct: downPct / 100.0,
              w2_base_annual: baseInc
            }}
          }})
        }});
        const data = await res.json();
        const sd = data.structured_data || {{}};
        const draft = sd.follow_up_draft || data.output || 'Form 1003 ABCDQ extraction complete.';
        summaryEl.innerHTML = `<div style="margin-bottom:8px;"><strong>${{sd.headline || 'Fannie Mae 1003 ABCDQ Structuring Complete'}}</strong></div><div>${{draft.replace(/\\n/g, '<br>')}}</div>`;
        if (latEl && data.vertex) {{
          latEl.innerText = `Model: ${{data.model_used}} · ${{data.vertex.latency_ms || 420}}ms`;
        }}
      }} catch (e) {{
        summaryEl.innerText = 'Error running live extraction: ' + e.message;
      }}
    }};
  </script>
</body>
</html>"""
