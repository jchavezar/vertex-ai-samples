# -*- coding: utf-8 -*-
"""Square 5.1: CFPB & State Regulatory Change Radar — Gemini Enterprise streamAssist
Design Style: Westlaw / Federal Register Archival Legal Publication
(#FAF8F5 warm archival legal paper, #1E3A8A lapis law blue, #991B1B statutory redline crimson,
Merriweather serif headings + Source Serif 4 & Public Sans).
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_5_1(auth_token: str) -> str:
    code = "5.1"
    ge_ui_url = "https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CFPB & State Regulatory Change Radar | Rocket Legal & Compliance</title>
  <link href="https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,400;0,700;0,900;1,400&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&family=Public+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --paper: #FAF8F5;
      --paper-card: #FFFFFF;
      --paper-tint: #F3EFEA;
      --lapis: #1E3A8A;
      --lapis-dark: #172554;
      --lapis-light: #EFF6FF;
      --crimson: #991B1B;
      --crimson-bg: #FEF2F2;
      --green: #166534;
      --green-bg: #F0FDF4;
      --ink: #1C1917;
      --ink-muted: #57534E;
      --rule: #D6D3D1;
      --gold-rule: #B45309;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: var(--paper);
      color: var(--ink);
      font-family: 'Source Serif 4', Georgia, serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      padding-bottom: 84px;
    }}
    .sans {{ font-family: 'Public Sans', -apple-system, BlinkMacSystemFont, sans-serif; }}
    .serif-head {{ font-family: 'Merriweather', Georgia, serif; }}

    /* Top Archival Masthead (Federal Register / Westlaw Style) */
    .legal-masthead {{
      background: #FFFFFF;
      border-bottom: 3px double var(--lapis);
      padding: 16px 32px;
    }}
    .masthead-top-bar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid var(--rule);
      padding-bottom: 10px;
      margin-bottom: 12px;
      flex-wrap: wrap;
      gap: 12px;
    }}
    .vol-meta {{
      font-family: 'Public Sans', sans-serif;
      font-size: 11.5px;
      font-weight: 600;
      color: var(--ink-muted);
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }}
    .masthead-actions {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .model-select-pill {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: var(--lapis-light);
      border: 1px solid #BFDBFE;
      padding: 5px 12px;
      border-radius: 6px;
      font-family: 'Public Sans', sans-serif;
      font-size: 12px;
      color: var(--lapis);
      font-weight: 600;
    }}
    .model-select-pill select {{
      background: transparent;
      border: none;
      color: var(--lapis-dark);
      font-family: inherit;
      font-size: 12px;
      font-weight: 700;
      outline: none;
      cursor: pointer;
    }}
    .masthead-main {{
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 16px;
    }}
    .publication-title {{
      font-family: 'Merriweather', Georgia, serif;
      font-size: 24px;
      font-weight: 900;
      color: var(--lapis-dark);
      letter-spacing: -0.01em;
    }}
    .publication-sub {{
      font-size: 14px;
      color: var(--ink-muted);
      margin-top: 4px;
    }}
    .audio-brief-btn {{
      background: var(--lapis);
      color: #FFFFFF;
      border: 1px solid var(--lapis-dark);
      padding: 10px 18px;
      border-radius: 6px;
      font-family: 'Public Sans', sans-serif;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      box-shadow: 0 2px 6px rgba(30, 58, 138, 0.18);
      transition: 0.15s;
    }}
    .audio-brief-btn:hover {{ background: var(--lapis-dark); }}

    /* State Bulletin Selector Tabs */
    .bulletin-bar {{
      background: var(--paper-tint);
      border-bottom: 1px solid var(--rule);
      padding: 12px 32px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 12px;
    }}
    .state-tabs {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }}
    .state-tab {{
      background: #FFFFFF;
      border: 1px solid var(--rule);
      color: var(--ink);
      padding: 8px 15px;
      border-radius: 5px;
      font-family: 'Public Sans', sans-serif;
      font-size: 12.5px;
      font-weight: 600;
      cursor: pointer;
      transition: 0.15s;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .state-tab:hover {{ border-color: var(--lapis); color: var(--lapis); }}
    .state-tab.active {{
      background: var(--lapis);
      color: #FFFFFF;
      border-color: var(--lapis-dark);
      box-shadow: 0 2px 5px rgba(30, 58, 138, 0.2);
    }}
    .cite-badge {{
      font-size: 10.5px;
      padding: 2px 6px;
      border-radius: 3px;
      background: rgba(0,0,0,0.07);
      font-weight: 700;
    }}
    .state-tab.active .cite-badge {{
      background: rgba(255,255,255,0.2);
      color: #FFFFFF;
    }}

    /* Main Two-Column Legal Digest Layout */
    .digest-grid {{
      max-width: 1440px;
      width: 100%;
      margin: 24px auto;
      padding: 0 32px;
      display: grid;
      grid-template-columns: 1fr 1.15fr;
      gap: 28px;
      flex: 1;
    }}
    @media (max-width: 1060px) {{
      .digest-grid {{ grid-template-columns: 1fr; }}
    }}

    .archival-card {{
      background: var(--paper-card);
      border: 1px solid var(--rule);
      border-top: 4px solid var(--lapis);
      border-radius: 4px;
      box-shadow: 0 4px 16px rgba(28, 25, 23, 0.05);
      display: flex;
      flex-direction: column;
    }}
    .archival-card.redline-card {{
      border-top-color: var(--crimson);
    }}
    .card-header {{
      padding: 16px 22px;
      border-bottom: 1px solid var(--rule);
      background: #FCFBF9;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
    }}
    .card-kicker {{
      font-family: 'Public Sans', sans-serif;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--lapis);
    }}
    .redline-card .card-kicker {{ color: var(--crimson); }}
    .card-title {{
      font-family: 'Merriweather', Georgia, serif;
      font-size: 17px;
      font-weight: 700;
      color: var(--ink);
      margin-top: 3px;
    }}
    .card-body {{
      padding: 22px 24px;
      display: flex;
      flex-direction: column;
      gap: 18px;
    }}

    /* Statutory Text Box */
    .statutory-notice {{
      background: var(--paper);
      border: 1px solid #E7E5E4;
      border-left: 4px solid var(--lapis);
      padding: 16px 18px;
      line-height: 1.7;
      font-size: 15px;
    }}
    .statute-citation-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-family: 'Public Sans', sans-serif;
      font-size: 12px;
      font-weight: 700;
      color: var(--lapis-dark);
      margin-bottom: 8px;
      padding-bottom: 6px;
      border-bottom: 1px solid #E7E5E4;
    }}
    .key-holding {{
      background: #FEF3C7;
      padding: 1px 4px;
      border-bottom: 1px solid #D97706;
      font-weight: 600;
    }}

    /* Impact Matrix Table */
    .impact-table {{
      width: 100%;
      border-collapse: collapse;
      font-family: 'Public Sans', sans-serif;
      font-size: 13px;
    }}
    .impact-table th {{
      text-align: left;
      padding: 9px 12px;
      background: var(--paper-tint);
      color: var(--ink-muted);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      border-bottom: 1px solid var(--rule);
    }}
    .impact-table td {{
      padding: 10px 12px;
      border-bottom: 1px solid #E7E5E4;
      vertical-align: top;
    }}
    .severity-pill {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 700;
      background: var(--crimson-bg);
      color: var(--crimson);
      border: 1px solid #FECACA;
    }}

    /* Microsoft Word Track-Changes Style Redline Policy Diff */
    .word-toolbar {{
      background: #F8FAFC;
      border: 1px solid var(--rule);
      border-radius: 4px;
      padding: 8px 14px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-family: 'Public Sans', sans-serif;
      font-size: 12px;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .track-pill {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-weight: 600;
      color: var(--crimson);
    }}
    .word-page {{
      background: #FFFFFF;
      border: 1px solid #CBD5E1;
      box-shadow: inset 0 1px 3px rgba(0,0,0,0.03), 0 2px 8px rgba(0,0,0,0.04);
      padding: 24px 28px 24px 36px;
      border-left: 5px solid var(--crimson);
      position: relative;
      line-height: 1.8;
      font-size: 15px;
    }}
    .word-section-heading {{
      font-family: 'Merriweather', Georgia, serif;
      font-size: 15px;
      font-weight: 700;
      color: var(--ink);
      margin-bottom: 12px;
      padding-bottom: 6px;
      border-bottom: 1px solid #E2E8F0;
    }}
    del.redline-del {{
      background: #FEE2E2;
      color: var(--crimson);
      text-decoration: line-through;
      padding: 1px 4px;
      border-radius: 2px;
    }}
    ins.redline-ins {{
      background: #DCFCE7;
      color: var(--green);
      text-decoration: underline;
      text-decoration-thickness: 2px;
      padding: 1px 4px;
      border-radius: 2px;
      font-weight: 600;
    }}
    .margin-comment {{
      margin-top: 14px;
      background: #FFFBEB;
      border: 1px solid #FDE68A;
      border-left: 3px solid var(--gold-rule);
      padding: 10px 14px;
      border-radius: 4px;
      font-family: 'Public Sans', sans-serif;
      font-size: 12.5px;
      color: #78350F;
    }}

    /* Action Bar */
    .redline-actions {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      padding-top: 8px;
      border-top: 1px solid #E7E5E4;
    }}
    .btn-primary {{
      background: var(--lapis);
      color: #FFFFFF;
      border: none;
      padding: 9px 16px;
      border-radius: 5px;
      font-family: 'Public Sans', sans-serif;
      font-size: 12.5px;
      font-weight: 600;
      cursor: pointer;
    }}
    .btn-primary:hover {{ background: var(--lapis-dark); }}
    .btn-outline {{
      background: #FFFFFF;
      color: var(--ink);
      border: 1px solid var(--rule);
      padding: 8px 14px;
      border-radius: 5px;
      font-family: 'Public Sans', sans-serif;
      font-size: 12.5px;
      font-weight: 600;
      cursor: pointer;
    }}
    .btn-outline:hover {{ background: var(--paper-tint); }}
    .ai-output-box {{
      background: #F8FAFC;
      border: 1px solid #CBD5E1;
      border-radius: 4px;
      padding: 14px 16px;
      font-family: 'Public Sans', sans-serif;
      font-size: 13px;
      line-height: 1.6;
      color: #1E293B;
      display: none;
      white-space: pre-wrap;
    }}
  </style>
</head>
<body>

  <!-- Archival Legal Masthead -->
  <header class="legal-masthead">
    <div class="masthead-top-bar">
      <div class="vol-meta">
        WESTLAW ARCHIVAL DIGEST · FEDERAL REGISTER &amp; STATE MORTGAGE SUPERVISORY RADAR · USE CASE 5.1
      </div>
      <div class="masthead-actions">
        <div class="model-select-pill">
          <span>Model:</span>
          <select id="app-model-select" onchange="window.syncSelectedModel(this.value)">
            <option value="gemini-4-argon">gemini-4-argon (Frontier Legal)</option>
            <option value="gemini-3.8-flash">gemini-3.8-flash (Fast Audit)</option>
          </select>
        </div>
        <a href="{ge_ui_url}" target="_blank" class="sans" style="font-size:12px;font-weight:600;color:var(--lapis);text-decoration:none;padding:6px 10px;border:1px solid #BFDBFE;border-radius:5px;background:#EFF6FF;">
          Gemini Enterprise Search ↗
        </a>
      </div>
    </div>

    <div class="masthead-main">
      <div>
        <h1 class="publication-title">CFPB &amp; State Regulatory Change Radar</h1>
        <p class="publication-sub">
          Automated Statutory Cross-Referencing against Rocket Mortgage Servicing Manual &amp; Encompass Lock Rules
        </p>
      </div>
      <button class="audio-brief-btn" onclick="window.playGCBriefing(this)">
        🔊 Listen to General Counsel Audio Briefing (Gemini 3.8 Live · Kore HD)
      </button>
    </div>
  </header>

  <!-- State Bulletin Selector Bar -->
  <nav class="bulletin-bar">
    <div class="state-tabs" role="tablist">
      <button class="state-tab active" onclick="window.selectBulletin('MI', this)">
        <span>Michigan DIFS</span>
        <span class="cite-badge">Bulletin 2026-14-CF</span>
      </button>
      <button class="state-tab" onclick="window.selectBulletin('CA', this)">
        <span>California DFPI</span>
        <span class="cite-badge">CRMLA § 50204(i)</span>
      </button>
      <button class="state-tab" onclick="window.selectBulletin('NY', this)">
        <span>New York DFS</span>
        <span class="cite-badge">3 NYCRR Part 419.11</span>
      </button>
      <button class="state-tab" onclick="window.selectBulletin('TX', this)">
        <span>Texas SML</span>
        <span class="cite-badge">7 TAC § 80.204</span>
      </button>
    </div>
    <div class="sans" style="font-size:12px;color:var(--ink-muted);">
      Effective Compliance Window: <strong id="eff-date-label" style="color:var(--crimson);">November 15, 2026 (33 Days Remaining)</strong>
    </div>
  </nav>

  <!-- Two-Column Legal Digest -->
  <main class="digest-grid">
    <!-- Left Column: Primary Statutory Text & Supervisory Digest -->
    <section class="archival-card">
      <div class="card-header">
        <div>
          <div class="card-kicker" id="digest-kicker">PRIMARY STATUTORY SOURCE · MICHIGAN DIFS + CFPB CIRCULAR 2026-04</div>
          <h2 class="card-title" id="digest-title">Servicing Loss Mitigation &amp; Junk Fee Prohibition Order</h2>
        </div>
        <span class="severity-pill" id="digest-severity">MANDATORY POLICY UPDATE</span>
      </div>

      <div class="card-body">
        <div class="statutory-notice">
          <div class="statute-citation-bar">
            <span id="statute-cite">12 CFR § 1024.41(c)(2)(iii) &amp; MI DIFS Bulletin 2026-14-CF</span>
            <span>Archival Vol. 91, No. 198</span>
          </div>
          <p id="statute-excerpt">
            “A mortgage servicer operating within the State of Michigan shall not assess, accrue, or collect convenience pay-by-phone fees, automated IVR processing fees, or late charges while a borrower’s <span class="key-holding">facially complete loss mitigation application</span> or streamlined forbearance deferral is under supervisory review. Furthermore, acknowledgment notices must be transmitted within <span class="key-holding">three (3) business days</span> (reduced from 5 business days under federal baseline RESPA Rule X).”
          </p>
        </div>

        <div>
          <h3 class="sans" style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;color:var(--ink-muted);margin-bottom:8px;">
            Impacted Rocket Servicing Systems &amp; Controls
          </h3>
          <table class="impact-table">
            <thead>
              <tr>
                <th>Manual Section</th>
                <th>Current Rocket Control</th>
                <th>Statutory Gap Detected</th>
              </tr>
            </thead>
            <tbody id="impact-tbody">
              <tr>
                <td><strong>§ 4.12(a)</strong> SLA Clock</td>
                <td>5 Business Days acknowledgment</td>
                <td><span class="severity-pill">Shorten to 3 Business Days (MI)</span></td>
              </tr>
              <tr>
                <td><strong>§ 4.12(c)</strong> Fee Waiver</td>
                <td>Suspends late fees upon full approval</td>
                <td><span class="severity-pill">Suspend upon receipt of application</span></td>
              </tr>
              <tr>
                <td><strong>§ 7.04</strong> IVR/ACH Billing</td>
                <td>$7.50 agent-assisted phone fee</td>
                <td><span class="severity-pill">Zero-Fee Mandate (Prohibited)</span></td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="sans" style="background:var(--lapis-light);border:1px solid #BFDBFE;padding:12px 16px;border-radius:4px;font-size:12.5px;color:var(--lapis-dark);">
          <strong>Gemini Enterprise Grounding Source:</strong> Indexed across 1,420 CFPB Supervisory Highlights, 50 State Banking Bulletins, and Rocket Servicing Policy Corpus (`v2026.10`).
        </div>
      </div>
    </section>

    <!-- Right Column: Microsoft Word Track-Changes Style Redline Policy Diff -->
    <section class="archival-card redline-card">
      <div class="card-header">
        <div>
          <div class="card-kicker">MICROSOFT WORD TRACK-CHANGES REDLINE · ROCKET SERVICING MANUAL</div>
          <h2 class="card-title" id="redline-doc-title">Rocket Servicing Manual § 4.12 — Loss Mitigation &amp; Fee Suspension</h2>
        </div>
        <div class="sans" style="display:flex;gap:6px;">
          <button class="btn-outline" style="padding:5px 10px;font-size:11.5px;" onclick="window.toggleViewMode('redline')">All Markup</button>
          <button class="btn-outline" style="padding:5px 10px;font-size:11.5px;" onclick="window.toggleViewMode('clean')">Clean Final</button>
        </div>
      </div>

      <div class="card-body">
        <div class="word-toolbar">
          <span class="track-pill">● Track Changes: ON (Author: Gemini 4 Argon General Counsel Co-Pilot)</span>
          <span id="redline-stats" style="color:var(--ink-muted);">3 Deletions · 3 Statutory Insertions</span>
        </div>

        <div class="word-page" id="word-redline-container">
          <div class="word-section-heading" id="word-sec-head">
            SECTION 4.12 — LOSS MITIGATION APPLICATION ACKNOWLEDGMENT &amp; FEE MORATORIUM
          </div>
          <div id="word-diff-body">
            <p style="margin-bottom:12px;">
              <strong>4.12.1 Written Acknowledgment Timeline.</strong> Upon receipt of a borrower’s loss mitigation package through the Rocket Homes Servicing Portal or mail intake, Servicing Operations shall issue a written notice of completeness within <del class="redline-del">five (5) business days</del> <ins class="redline-ins">three (3) business days for Michigan, California, and New York properties (and five (5) business days for all other jurisdictions)</ins> pursuant to 12 CFR § 1024.41(b)(2) and MI DIFS Bulletin 2026-14-CF.
            </p>
            <p style="margin-bottom:12px;">
              <strong>4.12.2 Late Charge &amp; Convenience Fee Suppression.</strong> Automated Servicing Core (MSP / Rocket Logic) shall suppress late fee accrual <del class="redline-del">only after final underwriting approval of a trial modification plan</del> <ins class="redline-ins">immediately upon intake timestamp of a facially complete loss mitigation application or hardship attestation</ins>.
            </p>
            <p>
              <strong>4.12.3 Expedited Payment Processing Fees.</strong> Representatives and IVR voice agents <del class="redline-del">may collect a standard $7.50 expedited drafting fee when authorized by the borrower</del> <ins class="redline-ins">are strictly prohibited from assessing any pay-by-phone, IVR, or electronic ACH convenience fee across all 50 states under CFPB Circular 2026-04</ins>.
            </p>
          </div>

          <div class="margin-comment" id="word-margin-note">
            <strong>General Counsel Audit Note (Cite: MI DIFS 2026-14-CF § III.B):</strong> Encompass &amp; Rocket Servicing Core rule flag <code>SRV_FEE_LOCK_2026</code> must be toggled prior to November 15, 2026 to avoid retroactive restitution orders.
          </div>
        </div>

        <div class="redline-actions">
          <div style="display:flex;gap:8px;flex-wrap:wrap;">
            <button class="btn-primary" onclick="window.acceptAllRedlines()">✓ Accept All Statutory Redlines into § 4.12</button>
            <button class="btn-outline" onclick="window.runLiveVertexAI()">⚡ Synthesize Live Vertex AI Legal Opinion</button>
          </div>
          <span class="sans" id="approval-status" style="font-size:12px;font-weight:700;color:var(--gold-rule);">
            Status: Pending Deputy GC Sign-Off
          </span>
        </div>

        <div id="ai-legal-output" class="ai-output-box"></div>
      </div>
    </section>
  </main>

  <script>
    const BULLETINS = {{
      MI: {{
        kicker: "PRIMARY STATUTORY SOURCE · MICHIGAN DIFS + CFPB CIRCULAR 2026-04",
        title: "Servicing Loss Mitigation & Junk Fee Prohibition Order",
        effDate: "November 15, 2026 (33 Days Remaining)",
        cite: "12 CFR § 1024.41(c)(2)(iii) & MI DIFS Bulletin 2026-14-CF",
        excerpt: `“A mortgage servicer operating within the State of Michigan shall not assess, accrue, or collect convenience pay-by-phone fees, automated IVR processing fees, or late charges while a borrower’s <span class="key-holding">facially complete loss mitigation application</span> or streamlined forbearance deferral is under supervisory review. Furthermore, acknowledgment notices must be transmitted within <span class="key-holding">three (3) business days</span> (reduced from 5 business days under federal baseline RESPA Rule X).”`,
        docTitle: "Rocket Servicing Manual § 4.12 — Loss Mitigation & Fee Suspension",
        secHead: "SECTION 4.12 — LOSS MITIGATION APPLICATION ACKNOWLEDGMENT & FEE MORATORIUM",
        diffHtml: `<p style="margin-bottom:12px;"><strong>4.12.1 Written Acknowledgment Timeline.</strong> Upon receipt of a borrower’s loss mitigation package through the Rocket Homes Servicing Portal or mail intake, Servicing Operations shall issue a written notice of completeness within <del class="redline-del">five (5) business days</del> <ins class="redline-ins">three (3) business days for Michigan, California, and New York properties (and five (5) business days for all other jurisdictions)</ins> pursuant to 12 CFR § 1024.41(b)(2) and MI DIFS Bulletin 2026-14-CF.</p><p style="margin-bottom:12px;"><strong>4.12.2 Late Charge &amp; Convenience Fee Suppression.</strong> Automated Servicing Core (MSP / Rocket Logic) shall suppress late fee accrual <del class="redline-del">only after final underwriting approval of a trial modification plan</del> <ins class="redline-ins">immediately upon intake timestamp of a facially complete loss mitigation application or hardship attestation</ins>.</p><p><strong>4.12.3 Expedited Payment Processing Fees.</strong> Representatives and IVR voice agents <del class="redline-del">may collect a standard $7.50 expedited drafting fee when authorized by the borrower</del> <ins class="redline-ins">are strictly prohibited from assessing any pay-by-phone, IVR, or electronic ACH convenience fee across all 50 states under CFPB Circular 2026-04</ins>.</p>`,
        note: "<strong>General Counsel Audit Note (Cite: MI DIFS 2026-14-CF § III.B):</strong> Encompass & Rocket Servicing Core rule flag <code>SRV_FEE_LOCK_2026</code> must be toggled prior to November 15, 2026 to avoid retroactive restitution orders.",
        audioScript: "General Counsel Regulatory Alert for Michigan DIFS Bulletin 2026-14-CF and CFPB Circular 2026-04. We have drafted three mandatory redlines to Rocket Servicing Manual Section 4.12. First, loss mitigation acknowledgment notices must be issued within three business days instead of five. Second, late fee accrual must pause immediately upon intake of a facially complete application. Third, all IVR and pay-by-phone convenience fees are permanently prohibited."
      }},
      CA: {{
        kicker: "PRIMARY STATUTORY SOURCE · CALIFORNIA DFPI CRMLA § 50204(i)",
        title: "California Per-Diem Interest & Impound Account Escrow Yield Mandate",
        effDate: "December 1, 2026 (49 Days Remaining)",
        cite: "Cal. Civ. Code § 2948.5 & Cal. Fin. Code § 50204(i)",
        excerpt: `“A residential mortgage lender shall not require a borrower to pay interest on the principal obligation for a period in excess of <span class="key-holding">one (1) business day prior to recording</span> of the deed of trust. Additionally, all California escrow impound accounts must credit statutory minimum interest of <span class="key-holding">2.00% per annum</span> paid quarterly.”`,
        docTitle: "Rocket Servicing Manual § 4.12 & Closing Addendum § 2.08 (CA)",
        secHead: "SECTION 4.12(CA) — CALIFORNIA PER-DIEM DISBURSEMENT & ESCROW INTEREST",
        diffHtml: `<p style="margin-bottom:12px;"><strong>4.12.1(CA) Per-Diem Interest Start Date.</strong> For California properties where disbursement occurs on a Monday or day following a state holiday, per-diem interest calculation shall commence <del class="redline-del">on the wire initiation date</del> <ins class="redline-ins">no earlier than one (1) business day immediately preceding the County Recorder confirmation timestamp</ins> per Cal. Civ. Code § 2948.5.</p><p><strong>4.12.2(CA) Escrow Impound Yield Credit.</strong> Rocket Servicing Treasury shall credit California tax and hazard impound balances at <del class="redline-del">standard money-market pass-through rates</del> <ins class="redline-ins">a statutory floor of 2.00% per annum compounded quarterly</ins>.</p>`,
        note: "<strong>General Counsel Audit Note (Cite: CA DFPI Exam Manual):</strong> Auto-refund trigger added in Rocket Closing Engine if county recording slips by >24 hours.",
        audioScript: "California DFPI Regulatory Briefing. Under California Civil Code Section 2948.5, per-diem mortgage interest cannot be charged more than one business day before deed recording. Our redline to Section 4.12 automatically triggers a borrower per-diem credit whenever county recording is delayed over a weekend."
      }},
      NY: {{
        kicker: "PRIMARY STATUTORY SOURCE · NEW YORK DFS 3 NYCRR PART 419.11",
        title: "NY DFS Single Point of Contact (SPOC) & Dual-Tracking Ban",
        effDate: "November 30, 2026 (48 Days Remaining)",
        cite: "3 NYCRR § 419.11(d) & RPAPL § 1304",
        excerpt: `“Where a New York borrower submits an incomplete loss mitigation application, the servicer shall assign a dedicated <span class="key-holding">Single Point of Contact (SPOC) within 48 hours</span> and stay all foreclosure referrals or dispositive motions for a minimum of <span class="key-holding">45 calendar days</span> to permit document cure.”`,
        docTitle: "Rocket Servicing Manual § 4.12(NY) — Dual-Tracking Prohibition",
        secHead: "SECTION 4.12(NY) — NEW YORK 3 NYCRR PART 419 FORECLOSURE HOLD",
        diffHtml: `<p style="margin-bottom:12px;"><strong>4.12.1(NY) Dedicated SPOC Assignment.</strong> New York borrowers requesting hardship assistance shall be routed to a dedicated New York SPOC specialist <del class="redline-del">upon reaching 60 days delinquency</del> <ins class="redline-ins">within 48 hours of initial verbal or portal hardship inquiry regardless of delinquency day-count</ins>.</p><p><strong>4.12.2(NY) Incomplete Package Cure Window.</strong> Foreclosure counsel holds shall remain active for <del class="redline-del">30 calendar days</del> <ins class="redline-ins">45 calendar days following written itemized notice of missing borrower documents</ins> under 3 NYCRR § 419.11.</p>`,
        note: "<strong>General Counsel Audit Note (Cite: 3 NYCRR § 419.11):</strong> Rocket Logic Foreclosure Gate updated to enforce 45-day document cure timer on all NY loans.",
        audioScript: "New York Department of Financial Services Part 419 update. We have updated Section 4.12 to assign a dedicated Single Point of Contact within 48 hours of any borrower hardship inquiry and extended the foreclosure dual-tracking hold from 30 days to 45 days."
      }},
      TX: {{
        kicker: "PRIMARY STATUTORY SOURCE · TEXAS CONSTITUTION ART. XVI § 50(a)(6)",
        title: "Texas Home Equity 2% Fee Cap & 12-Day Cooling-Off Verification",
        effDate: "December 10, 2026 (58 Days Remaining)",
        cite: "Tex. Const. art. XVI, § 50(a)(6)(E) & 7 TAC § 80.204",
        excerpt: `“Under revised Texas Finance Commission interpretation, bona fide discount points and automated valuation model (AVM) inspection fees must be <span class="key-holding">included inside the mandatory 2.00% constitutional fee cap</span> unless substantiated by a signed borrower rate-reduction election form executed <span class="key-holding">12 days prior to closing</span>.”`,
        docTitle: "Rocket Servicing & Origination Manual § 4.12(TX) — 50(a)(6) Audit",
        secHead: "SECTION 4.12(TX) — TEXAS HOME EQUITY 2.00% FEE CAP & CURE PROVISION",
        diffHtml: `<p style="margin-bottom:12px;"><strong>4.12.1(TX) Constitutional 2% Fee Cap Inclusion.</strong> The Encompass Texas 50(a)(6) fee accumulator shall include <del class="redline-del">only lender origination and processing charges</del> <ins class="redline-ins">all lender origination, processing, AVM property inspection, and unsubstantiated discount fees inside the strict 2.00% principal cap</ins>.</p><p><strong>4.12.2(TX) 60-Day Constitutional Cure Protocol.</strong> Any post-closing audit detecting a cap overage of even $0.01 shall trigger <del class="redline-del">manual compliance review</del> <ins class="redline-ins">an automated principal curtailment and borrower refund wire within 10 business days</ins> (well inside the 60-day statutory cure window).</p>`,
        note: "<strong>General Counsel Audit Note (Cite: Tex. Const. Art. XVI § 50(a)(6)):</strong> Prevents forfeiture of principal and interest under Texas home equity strict liability rules.",
        audioScript: "Texas Department of Savings and Mortgage Lending update for Section 50(a)(6) Home Equity loans. Our redline includes AVM inspection fees inside the strict two percent constitutional fee cap and automates a ten-day refund wire if any post-close audit detects a single cent overage."
      }}
    }};

    let currentState = 'MI';

    window.selectBulletin = function(stateCode, btnEl) {{
      currentState = stateCode;
      document.querySelectorAll('.state-tab').forEach(b => b.classList.remove('active'));
      if (btnEl) btnEl.classList.add('active');
      const b = BULLETINS[stateCode];
      document.getElementById('digest-kicker').innerText = b.kicker;
      document.getElementById('digest-title').innerText = b.title;
      document.getElementById('eff-date-label').innerText = b.effDate;
      document.getElementById('statute-cite').innerText = b.cite;
      document.getElementById('statute-excerpt').innerHTML = b.excerpt;
      document.getElementById('redline-doc-title').innerText = b.docTitle;
      document.getElementById('word-sec-head').innerText = b.secHead;
      document.getElementById('word-diff-body').innerHTML = b.diffHtml;
      document.getElementById('word-margin-note').innerHTML = b.note;
      document.getElementById('approval-status').innerText = "Status: Pending Deputy GC Sign-Off";
      document.getElementById('approval-status').style.color = "#B45309";
    }};

    window.toggleViewMode = function(mode) {{
      const dels = document.querySelectorAll('.redline-del');
      const inss = document.querySelectorAll('.redline-ins');
      dels.forEach(d => {{ d.style.display = (mode === 'clean') ? 'none' : 'inline'; }});
      inss.forEach(i => {{
        i.style.background = (mode === 'clean') ? 'transparent' : '#DCFCE7';
        i.style.textDecoration = (mode === 'clean') ? 'none' : 'underline';
      }});
    }};

    window.acceptAllRedlines = function() {{
      window.toggleViewMode('clean');
      const st = document.getElementById('approval-status');
      st.innerText = "✓ Signed & Adopted into Rocket Servicing Manual v2026.11";
      st.style.color = "#166534";
    }};

    window.playGCBriefing = function(btnEl) {{
      const b = BULLETINS[currentState] || BULLETINS.MI;
      window.playLiveCallClip(b.audioScript, "Kore", "Rocket Deputy General Counsel", btnEl);
    }};

    window.runLiveVertexAI = async function() {{
      const out = document.getElementById('ai-legal-output');
      out.style.display = 'block';
      const model = window.getSelectedModel ? window.getSelectedModel() : 'gemini-4-argon';
      out.textContent = `Synthesizing statutory redline memo for ${{currentState}} via Vertex AI (${{model}})...`;
      const b = BULLETINS[currentState] || BULLETINS.MI;
      const scenarioEl = document.getElementById('scenario-input');
      const promptText = `Analyze statutory change (${{b.cite}}): ${{b.title}}. Draft formal General Counsel redline justification for Rocket Servicing Manual Section 4.12. ` + (scenarioEl ? scenarioEl.value : '');
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ code: '5.1', model: model, scenario: promptText }})
        }});
        const data = await res.json();
        out.textContent = data.output || data.text || "Statutory opinion generated successfully.";
      }} catch (e) {{
        out.textContent = "Error invoking Vertex AI endpoint: " + e.message;
      }}
    }};
  </script>

  {render_floating_control_bar_and_drawer(code, auth_token)}
</body>
</html>
"""
