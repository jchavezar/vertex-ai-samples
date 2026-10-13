# -*- coding: utf-8 -*-
"""Square M.2: Project Sherlock: Cross-Document Fraud Graph & Entity Resolution
Visual Design: Financial Times (FT) / Palantir Foundry Investigative Journalism & Forensic Board
(#FFF1E5 authentic Financial Times warm salmon/cream paper background, #990F3D FT claret crimson accents,
#0F172A editorial ink, #FFFFFF evidence cards, Playfair Display serif + Public Sans + IBM Plex Mono).
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_m_2(auth_token: str) -> str:
    code = "M.2"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[M.2] Project Sherlock: Cross-Document Fraud Graph | FT Forensic Investigation Dossier</title>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,600&family=Public+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --ft-paper: #FFF1E5;
      --ft-tint: #F2DFCE;
      --ft-claret: #990F3D;
      --ft-claret-soft: #FCE8EF;
      --ft-oxford: #0D7680;
      --ft-ink: #0F172A;
      --ft-muted: #59524C;
      --ft-card: #FFFFFF;
      --ft-rule: #DECAB8;
      --ft-gold: #B45309;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: var(--ft-paper);
      color: var(--ft-ink);
      font-family: 'Public Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      min-height: 100vh;
      padding-bottom: 96px;
    }}
    .serif-ft {{ font-family: 'Playfair Display', Georgia, serif; }}
    .mono {{ font-family: 'IBM Plex Mono', monospace; }}

    /* Financial Times Editorial Masthead & Forensic Header */
    .ft-masthead {{
      background: var(--ft-paper);
      border-top: 4px solid var(--ft-claret);
      border-bottom: 2px solid var(--ft-ink);
      padding: 18px 28px;
    }}
    .ft-masthead-inner {{
      max-width: 1540px;
      margin: 0 auto;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 16px;
    }}
    .ft-kicker {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: var(--ft-claret);
      color: #FFFFFF;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      padding: 4px 10px;
      letter-spacing: 0.05em;
      text-transform: uppercase;
    }}
    .ft-select-pill {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: var(--ft-card);
      border: 1px solid #C4B09E;
      padding: 6px 12px;
      border-radius: 6px;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11.5px;
    }}
    .ft-select-pill select {{
      background: transparent;
      color: var(--ft-claret);
      border: none;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11.5px;
      font-weight: 700;
      outline: none;
      cursor: pointer;
    }}

    /* Investigative Board Grid */
    .forensic-grid {{
      max-width: 1540px;
      margin: 24px auto;
      padding: 0 28px;
      display: grid;
      grid-template-columns: 420px 1fr;
      gap: 24px;
      align-items: start;
    }}
    @media (max-width: 1120px) {{
      .forensic-grid {{ grid-template-columns: 1fr; }}
    }}

    .ft-panel {{
      background: var(--ft-card);
      border: 1px solid var(--ft-rule);
      border-top: 3px solid var(--ft-claret);
      border-radius: 6px;
      padding: 22px;
      box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05);
    }}

    /* Clickable Evidence Discrepancy Cards */
    .evidence-card {{
      width: 100%;
      text-align: left;
      background: #FFFDFB;
      border: 1.5px solid var(--ft-rule);
      border-left: 4px solid #C4B09E;
      border-radius: 6px;
      padding: 13px 14px;
      margin-bottom: 10px;
      cursor: pointer;
      transition: all 0.15s ease;
    }}
    .evidence-card:hover {{
      border-color: var(--ft-claret);
      background: var(--ft-claret-soft);
    }}
    .evidence-card.active {{
      border-color: var(--ft-claret);
      border-left: 5px solid var(--ft-claret);
      background: var(--ft-claret-soft);
      box-shadow: 0 4px 12px rgba(153, 15, 61, 0.10);
    }}
    .severity-tag {{
      display: inline-block;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 10px;
      font-weight: 700;
      padding: 2px 7px;
      border-radius: 3px;
      background: var(--ft-claret);
      color: #FFFFFF;
      text-transform: uppercase;
    }}

    /* Audio Briefing Button */
    .ft-audio-btn {{
      width: 100%;
      background: var(--ft-claret);
      color: #FFFFFF;
      border: none;
      border-radius: 6px;
      padding: 13px 16px;
      font-family: 'Public Sans', sans-serif;
      font-size: 13.5px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      transition: opacity 0.15s;
      box-shadow: 0 3px 10px rgba(153, 15, 61, 0.22);
    }}
    .ft-audio-btn:hover {{ opacity: 0.94; }}

    .ft-secondary-btn {{
      background: var(--ft-ink);
      color: #FFFFFF;
      border: none;
      border-radius: 6px;
      padding: 8px 14px;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
    }}

    input[type="range"] {{
      width: 100%;
      accent-color: var(--ft-claret);
      cursor: pointer;
    }}

    /* KPI Editorial Strip */
    .ft-kpi-row {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 14px;
      margin-bottom: 18px;
    }}
    @media (max-width: 900px) {{
      .ft-kpi-row {{ grid-template-columns: 1fr 1fr; }}
    }}
    .ft-kpi-cell {{
      background: var(--ft-paper);
      border: 1px solid var(--ft-rule);
      border-top: 2px solid var(--ft-ink);
      padding: 12px 14px;
    }}
  </style>
</head>
<body>

  <!-- FINANCIAL TIMES / PALANTIR FOUNDRY EDITORIAL FORENSIC HEADER -->
  <header class="ft-masthead">
    <div class="ft-masthead-inner">
      <div>
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;flex-wrap:wrap;">
          <span class="ft-kicker">SPECIAL INVESTIGATION • USE CASE M.2</span>
          <span class="mono" style="font-size:11px;color:var(--ft-muted);font-weight:600;">
            SPANNER GRAPH + DOCUMENT AI FORENSICS • CASE FILE #RKT-FRD-8819
          </span>
        </div>
        <h1 class="serif-ft" style="font-size:26px;font-weight:800;color:var(--ft-ink);letter-spacing:-0.01em;">
          Project Sherlock: Cross-Document Fraud Graph &amp; Synthetic Ring Detection
        </h1>
      </div>

      <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
        <div class="ft-select-pill">
          <span style="color:var(--ft-muted);font-weight:600;">MODEL:</span>
          <select id="app-model-select" onchange="window.syncSelectedModel(this.value)" aria-label="Select Gemini Model">
            <option value="gemini-4-argon" selected>gemini-4-argon (Frontier Graph Reasoning)</option>
            <option value="gemini-3.8-flash">gemini-3.8-flash (Fast Document Triage)</option>
          </select>
        </div>
        <button class="ft-secondary-btn" onclick="window.runLiveVertexAI()">
          Run Deep Forensic Audit
        </button>
      </div>
    </div>
  </header>

  <!-- MAIN FORENSIC BOARD -->
  <main class="forensic-grid">

    <!-- LEFT COLUMN: EVIDENCE DISCREPANCY CARDS, SENSITIVITY SLIDER & LIVE AUDIO BRIEFING -->
    <aside class="ft-panel">
      <div style="border-bottom:1px solid var(--ft-rule);padding-bottom:10px;margin-bottom:14px;">
        <div class="mono" style="font-size:11px;font-weight:700;color:var(--ft-claret);text-transform:uppercase;">
          EXHIBIT LEDGER • 3 CROSS-FILE ANOMALIES FLAGGED
        </div>
        <h2 class="serif-ft" style="font-size:19px;font-weight:700;margin-top:2px;">
          Clickable Evidence Discrepancy Cards
        </h2>
        <p style="font-size:12.5px;color:var(--ft-muted);margin-top:4px;">
          Select any forensic discrepancy below to isolate its cross-loan entity ring on the Financial Times investigation board.
        </p>
      </div>

      <!-- 3 Clickable Evidence Discrepancy Cards -->
      <button class="evidence-card active" onclick="window.selectEvidenceCard('kerning', this)">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
          <span class="severity-tag">EXHIBIT A • PDF FORGERY (99.4%)</span>
          <span class="mono" style="font-size:11px;color:var(--ft-claret);font-weight:700;">Box 1 &amp; Box 5 Tamper</span>
        </div>
        <div class="serif-ft" style="font-size:15.5px;font-weight:700;color:var(--ft-ink);">
          Font Kerning Tamper on W-2
        </div>
        <div style="font-size:12px;color:var(--ft-muted);margin-top:4px;line-height:1.45;">
          PDF `/Producer` string reveals `Canva PDF Engine v4.2` edited at 02:14 AM. Box 1 wages (`$194,500`) use Arial-MT kerning (+1.8pt offset) over original ADP Courier template.
        </div>
      </button>

      <button class="evidence-card" onclick="window.selectEvidenceCard('ein', this)">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
          <span class="severity-tag" style="background:var(--ft-oxford);">EXHIBIT B • SHELL ENTITY RING</span>
          <span class="mono" style="font-size:11px;color:var(--ft-oxford);font-weight:700;">4 Unrelated 1003s</span>
        </div>
        <div class="serif-ft" style="font-size:15.5px;font-weight:700;color:var(--ft-ink);">
          Synthetic Shell LLC EIN
        </div>
        <div style="font-size:12px;color:var(--ft-muted);margin-top:4px;line-height:1.45;">
          Employer `"Apex Precision Logistics LLC"` (EIN `88-4019283`) was registered 19 days ago at a UPS Store mailbox in Warren, MI—shared across 4 pending FHA/Conventional loans.
        </div>
      </button>

      <button class="evidence-card" onclick="window.selectEvidenceCard('wire', this)">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
          <span class="severity-tag" style="background:var(--ft-gold);">EXHIBIT C • ASSET LAYERING</span>
          <span class="mono" style="font-size:11px;color:var(--ft-gold);font-weight:700;">$42,000 Round-Trip</span>
        </div>
        <div class="serif-ft" style="font-size:15.5px;font-weight:700;color:var(--ft-ink);">
          Circular Gift Wire &amp; Notary Collusion
        </div>
        <div style="font-size:12px;color:var(--ft-muted);margin-top:4px;line-height:1.45;">
          ABA Routing `#072000326` trace shows the `$42,000` "Down Payment Gift" originated from Co-Borrower on Loan `#9912`, notarized by suspended Commission `#MI-44019`.
        </div>
      </button>

      <!-- Fraud Sensitivity Slider -->
      <div style="background:var(--ft-paper);border:1px solid var(--ft-rule);border-radius:6px;padding:14px;margin:14px 0;">
        <div style="display:flex;justify-content:space-between;align-items:center;font-size:12px;font-weight:700;margin-bottom:6px;">
          <span>Graph Anomaly Sensitivity Threshold</span>
          <span class="mono" id="lbl-sensitivity" style="color:var(--ft-claret);font-weight:700;">88 / 100 (Strict SIU)</span>
        </div>
        <input type="range" id="sld-sensitivity" min="50" max="98" step="2" value="88" oninput="window.updateFraudSensitivity()">
        <div class="mono" style="display:flex;justify-content:space-between;font-size:10px;color:var(--ft-muted);margin-top:4px;">
          <span>50 (Permissive)</span>
          <span>75 (Standard AUS)</span>
          <span>98 (Zero-Tolerance SIU)</span>
        </div>
      </div>

      <!-- Gemini 3.8 Live Fenrir HD Audio Briefing Button -->
      <div style="display:flex;flex-direction:column;gap:8px;">
        <button id="btn-sherlock-audio" class="ft-audio-btn" onclick="window.playSherlockAudioBriefing(this)">
          🔊 Listen to Forensic Investigator Audio Briefing (Gemini 3.8 Live · Fenrir HD)
        </button>
        <button onclick="window.stopAllLiveAudio && window.stopAllLiveAudio()" style="background:transparent;border:1px solid var(--ft-rule);color:var(--ft-muted);padding:7px;border-radius:6px;font-family:'IBM Plex Mono',monospace;font-size:11px;font-weight:600;cursor:pointer;">
          ✋ Interrupt / Stop Audio Briefing (0ms Barge-In)
        </button>
      </div>
    </aside>

    <!-- RIGHT COLUMN: INTERACTIVE SVG ENTITY RESOLUTION & FRAUD RING GRAPH ON WARM FT PAPER -->
    <section style="display:flex;flex-direction:column;gap:20px;">
      <div class="ft-panel">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid var(--ft-rule);">
          <div>
            <span class="mono" style="font-size:11px;font-weight:700;color:var(--ft-claret);text-transform:uppercase;">
              PALANTIR FOUNDRY x SPANNER PROPERTY GRAPH • 3-HOP ENTITY RESOLUTION
            </span>
            <h2 class="serif-ft" style="font-size:22px;font-weight:800;color:var(--ft-ink);margin-top:2px;" id="graph-focus-title">
              Cross-Loan Synthetic Identity &amp; Collusion Network
            </h2>
          </div>
          <div class="mono" style="font-size:11px;background:var(--ft-claret-soft);border:1px solid var(--ft-claret);color:var(--ft-claret);padding:5px 10px;border-radius:4px;font-weight:700;" id="siu-verdict-badge">
            SIU HOLD: BLOCK FUNDING ($1.84M RING EXPOSURE)
          </div>
        </div>

        <!-- 4 Forensic KPI Cells -->
        <div class="ft-kpi-row">
          <div class="ft-kpi-cell">
            <div class="mono" style="font-size:10px;color:var(--ft-muted);">COMPOSITE FRAUD SCORE</div>
            <div class="serif-ft" id="kpi-fraud-score" style="font-size:22px;font-weight:800;color:var(--ft-claret);margin-top:2px;">96.4 / 100</div>
            <div class="mono" style="font-size:10.5px;color:var(--ft-muted);margin-top:2px;">Critical Collusion Ring</div>
          </div>
          <div class="ft-kpi-cell">
            <div class="mono" style="font-size:10px;color:var(--ft-muted);">LINKED 1003 APPLICATIONS</div>
            <div class="serif-ft" id="kpi-linked-loans" style="font-size:22px;font-weight:800;color:var(--ft-ink);margin-top:2px;">4 Active Loans</div>
            <div class="mono" style="font-size:10.5px;color:var(--ft-muted);margin-top:2px;">$1,840,000 Total UPB</div>
          </div>
          <div class="ft-kpi-cell">
            <div class="mono" style="font-size:10px;color:var(--ft-muted);">PDF STREAM INTEGRITY</div>
            <div class="serif-ft" style="font-size:22px;font-weight:800;color:var(--ft-claret);margin-top:2px;">FAIL (+1.8pt)</div>
            <div class="mono" style="font-size:10.5px;color:var(--ft-muted);margin-top:2px;">Canva XMP Layer Detected</div>
          </div>
          <div class="ft-kpi-cell">
            <div class="mono" style="font-size:10px;color:var(--ft-muted);">FANNIE MAE DEFECT PROTECTION</div>
            <div class="serif-ft" style="font-size:22px;font-weight:800;color:var(--ft-oxford);margin-top:2px;">100% Shielded</div>
            <div class="mono" style="font-size:10.5px;color:var(--ft-muted);margin-top:2px;">Zero Repurchase Loss</div>
          </div>
        </div>

        <!-- Interactive SVG Entity Resolution & Fraud Ring Graph on Warm FT Paper -->
        <div style="background:var(--ft-paper);border:1.5px solid var(--ft-rule);border-radius:6px;padding:16px;">
          <svg id="sherlock-fraud-svg" viewBox="0 0 880 350" style="width:100%;height:auto;display:block;"></svg>
        </div>
      </div>

      <!-- Investigative Journalist & SIU Narrative Dossier -->
      <div class="ft-panel" style="background:#FFFDF9;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;flex-wrap:wrap;gap:8px;">
          <span class="mono" style="font-size:11.5px;font-weight:700;color:var(--ft-claret);">
            SPECIAL INVESTIGATIONS UNIT (SIU) FORENSIC BRIEFING &amp; SAR DRAFT
          </span>
          <span class="mono" style="font-size:11px;color:var(--ft-muted);">
            FinCEN SAR Auto-Staged • Gemini 4 Argon Graph Synthesis
          </span>
        </div>
        <div id="sherlock-narrative-box" style="font-size:14.5px;line-height:1.65;color:var(--ft-ink);">
          <strong>[Exhibit A — Font Kerning Tamper on W-2]:</strong> Document AI Lending Forensics inspected the raw PDF binary dictionary of the borrower's 2025 Form W-2 and detected an unflattened `/Producer (Canva PDF Engine 4.2)` revision saved at 02:14 AM EST. While the ADP employer header uses authentic monospaced `CourierStd`, Box 1 (`$194,500.00`) was overwritten in `Arial-MT` with a `+1.8pt` baseline shift and mismatched Medicare withholding math (`Box 5 * 1.45% != Box 6`).
        </div>
      </div>
    </section>

  </main>

  <script>
    let activeEvidenceKey = 'kerning';

    const EVIDENCE_DATA = {{
      kerning: {{
        title: "Exhibit A: Font Kerning Tamper on W-2 & PDF Metadata Forgery",
        narrative: "<strong>[Exhibit A — Font Kerning Tamper on W-2]:</strong> Document AI Lending Forensics inspected the raw PDF binary dictionary of the borrower's 2025 Form W-2 and detected an unflattened `/Producer (Canva PDF Engine 4.2)` revision saved at 02:14 AM EST. While the ADP employer header uses authentic monospaced `CourierStd`, Box 1 (`$194,500.00`) was overwritten in `Arial-MT` with a `+1.8pt` baseline shift and mismatched Medicare withholding math (`Box 5 * 1.45% != Box 6`).",
        speech: "Forensic briefing on Exhibit A. Our Document AI inspection of the borrower's W-2 uncovered a Canva PDF modification layer saved at 2:14 AM. Box 1 wages of 194,500 dollars exhibit a 1.8 point font kerning shift and fail the mandatory 1.45 percent Medicare tax cross-check. We have placed an immediate Special Investigations hold on all four linked applications."
      }},
      ein: {{
        title: "Exhibit B: Synthetic Shell LLC EIN Shared Across 4 Active Loans",
        narrative: "<strong>[Exhibit B — Synthetic Shell LLC EIN Registry Collision]:</strong> Spanner Graph entity resolution linked Employer EIN `88-4019283` (`Apex Precision Logistics LLC`) across 4 supposedly unrelated mortgage applications totaling `$1.84M`. Michigan LARA corporate registry records show the LLC was formed 19 days ago using a commercial UPS Store PMB address in Warren, MI with zero quarterly UIA payroll tax filings.",
        speech: "Forensic briefing on Exhibit B. Spanner Graph entity resolution flagged Employer E-I-N 88-4019283, Apex Precision Logistics LLC, across four simultaneous mortgage applications totaling 1.84 million dollars. State registry checks confirm this shell company was registered 19 days ago at a retail mailbox with zero verified payroll filings."
      }},
      wire: {{
        title: "Exhibit C: Circular Gift Wire & Suspended Notary Commission Ring",
        narrative: "<strong>[Exhibit C — Circular Gift Wire &amp; Notary Commission Collusion]:</strong> Tracing ABA Routing `#072000326` and account suffix `#8841` reveals that the borrower's `$42,000` 'Family Gift Wire' was funded 72 hours earlier by the co-borrower on Loan `#9912`. Furthermore, all 4 Gift Letters and Occupancy Affidavits bear Notary Commission `#MI-44019`, whose commission was suspended in Wayne County.",
        speech: "Forensic briefing on Exhibit C. Tracing bank routing number 072000326 reveals a circular 42,000 dollar gift wire cycling between co-borrowers across three separate loan files, all notarized under suspended Wayne County Notary Commission M-I 44019."
      }}
    }};

    window.renderSherlockGraph = function() {{
      const svg = document.getElementById('sherlock-fraud-svg');
      const sens = parseInt(document.getElementById('sld-sensitivity').value || 88, 10);

      const hlKerning = activeEvidenceKey === 'kerning';
      const hlEin = activeEvidenceKey === 'ein';
      const hlWire = activeEvidenceKey === 'wire';

      const strokeA = hlKerning ? '#990F3D' : '#8C7A6B';
      const strokeB = hlEin ? '#990F3D' : '#8C7A6B';
      const strokeC = hlWire ? '#990F3D' : '#8C7A6B';

      svg.innerHTML = `
        <defs>
          <marker id="ftArrow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1 L 10 5 L 0 9 z" fill="#990F3D"/>
          </marker>
        </defs>

        <!-- Subtle Editorial Grid Lines -->
        <line x1="30" y1="85" x2="850" y2="85" stroke="#EAD8C7" stroke-width="1"/>
        <line x1="30" y1="175" x2="850" y2="175" stroke="#EAD8C7" stroke-width="1"/>
        <line x1="30" y1="265" x2="850" y2="265" stroke="#EAD8C7" stroke-width="1"/>

        <!-- Edges Connecting Central Loan Ring to the 4 Forensic Entities -->
        <line x1="250" y1="90" x2="420" y2="165" stroke="${{strokeA}}" stroke-width="${{hlKerning ? 4 : 2}}" stroke-dasharray="${{hlKerning ? 'none' : '5,4'}}" marker-end="url(#ftArrow)"/>
        <line x1="630" y1="90" x2="460" y2="165" stroke="${{strokeB}}" stroke-width="${{hlEin ? 4 : 2}}" stroke-dasharray="${{hlEin ? 'none' : '5,4'}}" marker-end="url(#ftArrow)"/>
        <line x1="250" y1="265" x2="420" y2="185" stroke="${{strokeC}}" stroke-width="${{hlWire ? 4 : 2}}" stroke-dasharray="${{hlWire ? 'none' : '5,4'}}" marker-end="url(#ftArrow)"/>
        <line x1="630" y1="265" x2="460" y2="185" stroke="${{strokeC}}" stroke-width="${{hlWire ? 4 : 2}}" stroke-dasharray="${{hlWire ? 'none' : '5,4'}}" marker-end="url(#ftArrow)"/>

        <!-- Cross-ring dotted links -->
        <line x1="250" y1="90" x2="630" y2="90" stroke="#990F3D" stroke-width="1.5" stroke-dasharray="4,4"/>
        <line x1="250" y1="265" x2="630" y2="265" stroke="#B45309" stroke-width="1.5" stroke-dasharray="4,4"/>

        <!-- NODE 1: Borrower PDF Metadata (Top Left) -->
        <g style="cursor:pointer;" onclick="window.selectEvidenceCard('kerning')">
          <rect x="45" y="42" width="235" height="88" rx="6" fill="${{hlKerning ? '#FCE8EF' : '#FFFFFF'}}" stroke="#990F3D" stroke-width="${{hlKerning ? 3 : 1.5}}"/>
          <text x="60" y="65" fill="#990F3D" font-family="IBM Plex Mono" font-size="10.5" font-weight="700">NODE 01 • BORROWER PDF METADATA</text>
          <text x="60" y="88" fill="#0F172A" font-family="Playfair Display" font-size="15" font-weight="700">Canva XMP Layer &amp; W-2 Kerning</text>
          <text x="60" y="110" fill="#59524C" font-family="IBM Plex Mono" font-size="10.5">Arial-MT +1.8pt Shift • 02:14 AM Edit</text>
        </g>

        <!-- NODE 2: Employer EIN Registry (Top Right) -->
        <g style="cursor:pointer;" onclick="window.selectEvidenceCard('ein')">
          <rect x="600" y="42" width="235" height="88" rx="6" fill="${{hlEin ? '#FCE8EF' : '#FFFFFF'}}" stroke="#0D7680" stroke-width="${{hlEin ? 3 : 1.5}}"/>
          <text x="615" y="65" fill="#0D7680" font-family="IBM Plex Mono" font-size="10.5" font-weight="700">NODE 02 • EMPLOYER EIN REGISTRY</text>
          <text x="615" y="88" fill="#0F172A" font-family="Playfair Display" font-size="15" font-weight="700">EIN 88-4019283 (Shell LLC)</text>
          <text x="615" y="110" fill="#59524C" font-family="IBM Plex Mono" font-size="10.5">Formed 19d Ago • UPS Mailbox #402</text>
        </g>

        <!-- CENTER HUB: Synthetic Collusion Ring -->
        <g>
          <rect x="315" y="132" width="250" height="88" rx="8" fill="#990F3D" stroke="#0F172A" stroke-width="2"/>
          <text x="440" y="156" fill="#FCE8EF" font-family="IBM Plex Mono" font-size="10.5" font-weight="700" text-anchor="middle">SYNTHETIC COLLUSION HUB</text>
          <text x="440" y="180" fill="#FFFFFF" font-family="Playfair Display" font-size="16.5" font-weight="700" text-anchor="middle">4 Linked Loans ($1.84M UPB)</text>
          <text x="440" y="202" fill="#F2DFCE" font-family="IBM Plex Mono" font-size="11" text-anchor="middle">Sensitivity Gate: ${{sens}}/100 • BLOCKED</text>
        </g>

        <!-- NODE 3: Bank Routing Number (Bottom Left) -->
        <g style="cursor:pointer;" onclick="window.selectEvidenceCard('wire')">
          <rect x="45" y="222" width="235" height="88" rx="6" fill="${{hlWire ? '#FCE8EF' : '#FFFFFF'}}" stroke="#B45309" stroke-width="${{hlWire ? 3 : 1.5}}"/>
          <text x="60" y="245" fill="#B45309" font-family="IBM Plex Mono" font-size="10.5" font-weight="700">NODE 03 • BANK ROUTING NUMBER</text>
          <text x="60" y="268" fill="#0F172A" font-family="Playfair Display" font-size="15" font-weight="700">ABA #072000326 • Acct #8841</text>
          <text x="60" y="290" fill="#59524C" font-family="IBM Plex Mono" font-size="10.5">$42,000 Circular Gift Wire Loop</text>
        </g>

        <!-- NODE 4: Notary Commission # (Bottom Right) -->
        <g style="cursor:pointer;" onclick="window.selectEvidenceCard('wire')">
          <rect x="600" y="222" width="235" height="88" rx="6" fill="${{hlWire ? '#FCE8EF' : '#FFFFFF'}}" stroke="#990F3D" stroke-width="${{hlWire ? 3 : 1.5}}"/>
          <text x="615" y="245" fill="#990F3D" font-family="IBM Plex Mono" font-size="10.5" font-weight="700">NODE 04 • NOTARY COMMISSION #</text>
          <text x="615" y="268" fill="#0F172A" font-family="Playfair Display" font-size="15" font-weight="700">Commission #MI-44019</text>
          <text x="615" y="290" fill="#59524C" font-family="IBM Plex Mono" font-size="10.5">Stamped All 4 Gift Affidavits</text>
        </g>
      `;
    }};

    window.selectEvidenceCard = function(key, btnEl) {{
      activeEvidenceKey = key;
      if (btnEl) {{
        document.querySelectorAll('.evidence-card').forEach(c => c.classList.remove('active'));
        btnEl.classList.add('active');
      }}
      const item = EVIDENCE_DATA[key] || EVIDENCE_DATA.kerning;
      document.getElementById('graph-focus-title').innerText = item.title;
      document.getElementById('sherlock-narrative-box').innerHTML = item.narrative;
      window.renderSherlockGraph();
    }};

    window.updateFraudSensitivity = async function() {{
      const sens = parseInt(document.getElementById('sld-sensitivity').value || 88, 10);
      document.getElementById('lbl-sensitivity').innerText = `${{sens}} / 100 (${{sens >= 80 ? 'Strict SIU' : 'Standard AUS'}})`;
      const score = Math.min(99.8, (89.0 + (sens - 50) * 0.19)).toFixed(1);
      const loans = sens >= 80 ? 4 : 3;
      document.getElementById('kpi-fraud-score').innerText = `${{score}} / 100`;
      document.getElementById('kpi-linked-loans').innerText = `${{loans}} Active Loans`;
      window.renderSherlockGraph();

      try {{
        await fetch('/api/sandbox', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: 'M.2',
            action: 'audit_large_deposits',
            params: {{ qualifying_monthly_income: 11400, ending_balance: 51200, funds_needed: 44000 }}
          }})
        }});
      }} catch (e) {{}}
    }};

    window.playSherlockAudioBriefing = function(btnEl) {{
      const item = EVIDENCE_DATA[activeEvidenceKey] || EVIDENCE_DATA.kerning;
      if (window.playLiveCallClip) {{
        window.playLiveCallClip(
          item.speech,
          "Fenrir",
          "Chief Forensic Investigator (Project Sherlock)",
          btnEl
        );
      }}
    }};

    window.runLiveVertexAI = async function() {{
      const model = window.getSelectedModel ? window.getSelectedModel() : 'gemini-4-argon';
      const sens = document.getElementById('sld-sensitivity').value || 88;
      const box = document.getElementById('sherlock-narrative-box');
      box.innerHTML = `<em>Running Spanner Graph 3-Hop Entity Resolution &amp; PDF Forensic Audit with <strong>${{model}}</strong>...</em>`;
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: 'M.2',
            model: model,
            user_input: `Analyze the cross-document fraud ring connecting Borrower PDF Metadata (Canva W-2 kerning tamper), Employer EIN Registry (88-4019283), Bank Routing Number (#072000326 circular gift wire), and Notary Commission #MI-44019 at sensitivity ${{sens}}/100.`,
            params: {{ sensitivity: sens, exhibit: activeEvidenceKey }}
          }})
        }});
        const data = await res.json();
        const textOut = (data.vertex && data.vertex.response_markdown) || data.output || EVIDENCE_DATA[activeEvidenceKey].narrative;
        box.innerHTML = `<strong>[${{data.model_used || model}} Forensic Synthesis]:</strong> ${{textOut}}`;
      }} catch (e) {{
        box.innerText = "Forensic Engine Error: " + e.message;
      }}
    }};

    document.addEventListener('DOMContentLoaded', () => {{
      window.renderSherlockGraph();
    }});
  </script>

  {render_floating_control_bar_and_drawer(code, auth_token)}
</body>
</html>"""
