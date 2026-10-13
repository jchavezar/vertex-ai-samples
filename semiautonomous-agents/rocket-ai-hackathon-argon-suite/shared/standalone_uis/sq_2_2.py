# -*- coding: utf-8 -*-
"""Square 2.2 Standalone Full-Screen UI:
Condition & Stipulation Auto-Clearer (DocuSign / Box Enterprise Document Review & Underwriting Portal)
Design Style: DocuSign / Box Enterprise Document Review & Underwriting Portal (#F9FAFB light gray canvas, #2463EB DocuSign royal blue top bar, #FFFFFF document sheet viewer, Plus Jakarta Sans).
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_2_2(auth_token: str) -> str:
    floating_bar = render_floating_control_bar_and_drawer("2.2", auth_token)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>2.2 · Condition &amp; Stipulation Auto-Clearer — Enterprise Document Review Portal</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --canvas: #F9FAFB;
      --doc-blue: #2463EB;
      --doc-blue-dark: #1D4ED8;
      --doc-blue-soft: #EFF6FF;
      --surface: #FFFFFF;
      --ink: #0F172A;
      --muted: #475569;
      --border: #E2E8F0;
      --emerald: #059669;
      --emerald-soft: #ECFDF5;
      --amber: #D97706;
      --amber-soft: #FFFBEB;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--canvas);
      color: var(--ink);
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }}

    /* DocuSign / Box Royal Blue Top Bar */
    .docusign-topbar {{
      background: var(--doc-blue);
      color: #FFFFFF;
      padding: 13px 26px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      flex-wrap: wrap;
      box-shadow: 0 3px 12px rgba(36, 99, 235, 0.22);
    }}
    .brand-cluster {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}
    .doc-logo {{
      width: 36px;
      height: 36px;
      border-radius: 8px;
      background: #FFFFFF;
      color: var(--doc-blue);
      font-weight: 800;
      font-size: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .portal-title {{
      font-size: 18px;
      font-weight: 800;
      letter-spacing: -0.01em;
    }}
    .portal-sub {{
      font-size: 12px;
      color: #DBEAFE;
    }}
    .topbar-controls {{
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }}
    .model-pill {{
      background: rgba(255, 255, 255, 0.16);
      border: 1px solid rgba(255, 255, 255, 0.32);
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 12px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .model-pill select {{
      background: transparent;
      border: none;
      color: #FFFFFF;
      font-family: inherit;
      font-size: 12px;
      font-weight: 700;
      outline: none;
      cursor: pointer;
    }}
    .model-pill select option {{
      background: #0F172A;
      color: #FFFFFF;
    }}
    .btn-audio {{
      background: #FFFFFF;
      color: var(--doc-blue-dark);
      border: none;
      padding: 8px 14px;
      border-radius: 6px;
      font-family: inherit;
      font-size: 12.5px;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }}
    .btn-autoclear {{
      background: #059669;
      color: #FFFFFF;
      border: 1px solid #34D399;
      padding: 8px 16px;
      border-radius: 6px;
      font-family: inherit;
      font-size: 12.5px;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 2px 8px rgba(5, 150, 105, 0.3);
    }}

    /* 3-Pane Document Clearance Room */
    .clearance-room {{
      display: grid;
      grid-template-columns: 340px 1fr 380px;
      gap: 18px;
      padding: 20px 26px 90px 26px;
      max-width: 1560px;
      margin: 0 auto;
      width: 100%;
      flex: 1;
    }}
    @media (max-width: 1200px) {{
      .clearance-room {{ grid-template-columns: 1fr; }}
    }}

    /* Left Pane: Stipulations Queue */
    .stip-pane {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 18px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      box-shadow: 0 1px 4px rgba(15, 23, 42, 0.04);
    }}
    .pane-heading {{
      font-size: 14px;
      font-weight: 800;
      color: var(--ink);
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 10px;
      border-bottom: 1px solid var(--border);
    }}
    .stip-card {{
      border: 1.5px solid var(--border);
      border-radius: 8px;
      padding: 13px 14px;
      cursor: pointer;
      transition: all 0.15s;
      background: #FFFFFF;
    }}
    .stip-card:hover {{
      border-color: #93C5FD;
      background: #F8FAFC;
    }}
    .stip-card.active {{
      border-color: var(--doc-blue);
      background: var(--doc-blue-soft);
      box-shadow: 0 3px 10px rgba(36, 99, 235, 0.1);
    }}
    .stip-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 6px;
    }}
    .stip-id {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11.5px;
      font-weight: 700;
      color: var(--doc-blue-dark);
    }}
    .stip-badge {{
      font-size: 10.5px;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 999px;
      background: var(--emerald-soft);
      color: var(--emerald);
      border: 1px solid #A7F3D0;
    }}
    .stip-title {{
      font-size: 13.5px;
      font-weight: 700;
      color: var(--ink);
      margin-bottom: 4px;
    }}
    .stip-meta {{
      font-size: 11.5px;
      color: var(--muted);
    }}

    /* Center Pane: Uploaded Paper Document Viewer */
    .doc-viewer-pane {{
      background: #E2E8F0;
      border: 1px solid #CBD5E1;
      border-radius: 10px;
      padding: 22px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}
    .viewer-toolbar {{
      background: #FFFFFF;
      border: 1px solid #CBD5E1;
      border-radius: 8px;
      padding: 10px 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 12px;
      font-weight: 600;
      color: var(--muted);
    }}
    .paper-sheet {{
      background: #FFFFFF;
      border: 1px solid #CBD5E1;
      border-radius: 6px;
      padding: 32px 36px;
      box-shadow: 0 10px 28px rgba(15, 23, 42, 0.1);
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}
    .doc-watermark {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 12px;
      border-bottom: 2px solid var(--ink);
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11px;
      color: var(--muted);
    }}
    .verified-highlight {{
      background: #FEF9C3;
      border: 1.5px solid #EAB308;
      border-radius: 6px;
      padding: 10px 14px;
      font-size: 13px;
      line-height: 1.55;
    }}
    .sig-box {{
      margin-top: 12px;
      padding: 14px 18px;
      border: 2px dashed var(--doc-blue);
      background: var(--doc-blue-soft);
      border-radius: 8px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .sig-script {{
      font-family: Georgia, serif;
      font-style: italic;
      font-size: 20px;
      color: var(--doc-blue-dark);
      font-weight: 700;
    }}

    /* Right Pane: Underwriter Clearance Stamp & Checklist */
    .clearance-pane {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      box-shadow: 0 1px 4px rgba(15, 23, 42, 0.04);
    }}
    .rubber-stamp {{
      border: 3px double var(--emerald);
      background: var(--emerald-soft);
      color: var(--emerald);
      border-radius: 8px;
      padding: 14px;
      text-align: center;
      font-family: 'IBM Plex Mono', monospace;
      font-weight: 800;
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }}
    .check-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px 12px;
      background: #F8FAFC;
      border: 1px solid var(--border);
      border-radius: 6px;
      font-size: 12.5px;
    }}
    .check-row strong {{
      color: var(--emerald);
      font-family: 'IBM Plex Mono', monospace;
    }}
    .audit-memo {{
      background: #F8FAFC;
      border: 1px solid var(--border);
      border-left: 4px solid var(--doc-blue);
      border-radius: 6px;
      padding: 14px;
      font-size: 12.5px;
      line-height: 1.6;
      color: var(--ink);
    }}
  </style>
</head>
<body>

  <!-- DOCUSIGN / BOX ENTERPRISE TOP HEADER -->
  <header class="docusign-topbar">
    <div class="brand-cluster">
      <div class="doc-logo">DS</div>
      <div>
        <div class="portal-title">Condition &amp; Stipulation Auto-Clearer · Document Clearance Room</div>
        <div class="portal-sub">Loan #RKT-9948120 · Borrower: Sarah &amp; David Chen · Prior-to-Docs (PTD) Condition Portal</div>
      </div>
    </div>
    <div class="topbar-controls">
      <div class="model-pill">
        <span>Clearance Model:</span>
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)">
          <option value="gemini-4-argon" selected>gemini-4-argon (Underwriter Audit)</option>
          <option value="gemini-3.8-flash">gemini-3.8-flash (Instant Doc Match)</option>
        </select>
      </div>
      <button class="btn-audio" onclick="window.playStipAudioSummary(this)">
        🔊 Listen to Stip Clearance Audio Summary
      </button>
      <button class="btn-autoclear" onclick="window.runLiveVertexAI()">
        ✓ Auto-Clear Stipulations
      </button>
    </div>
  </header>

  <!-- 3-PANE DOCUMENT CLEARANCE ROOM -->
  <main class="clearance-room">
    <!-- LEFT PANE: CLICKABLE UNDERWRITING STIPULATIONS -->
    <aside class="stip-pane">
      <div class="pane-heading">
        <span>Underwriting Stipulations (3)</span>
        <span style="font-size:11.5px;color:var(--emerald);font-weight:700;">3 / 3 Matched</span>
      </div>

      <div class="stip-card active" id="stip-104" onclick="window.selectStipulation('104')">
        <div class="stip-top">
          <span class="stip-id">Stip #104 · Income</span>
          <span class="stip-badge" id="badge-104">CLEARED · 100%</span>
        </div>
        <div class="stip-title">Stip #104: 2025 W-2 Match</div>
        <div class="stip-meta">Verify 2025 IRS Form W-2 Box 1 wages ($148,500.00) match Uniform Residential Loan Application (Form 1003).</div>
      </div>

      <div class="stip-card" id="stip-108" onclick="window.selectStipulation('108')">
        <div class="stip-top">
          <span class="stip-id">Stip #108 · Credit</span>
          <span class="stip-badge" id="badge-108">CLEARED · eSIGNED</span>
        </div>
        <div class="stip-title">Stip #108: Signed LOE for Credit Inquiry</div>
        <div class="stip-meta">Borrower signed Letter of Explanation confirming 09/14/2026 JPMorgan Chase inquiry resulted in no new debt.</div>
      </div>

      <div class="stip-card" id="stip-112" onclick="window.selectStipulation('112')">
        <div class="stip-top">
          <span class="stip-id">Stip #112 · Collateral</span>
          <span class="stip-badge" id="badge-112">CLEARED · BINDER OK</span>
        </div>
        <div class="stip-title">Stip #112: Homeowners Insurance Binder</div>
        <div class="stip-meta">Verify 100% Replacement Cost coverage ($485,000) &amp; Rocket Mortgage ISAOA ATIMA mortgagee clause.</div>
      </div>
    </aside>

    <!-- CENTER PANE: UPLOADED BORROWER PAPER DOCUMENT VIEWER -->
    <section class="doc-viewer-pane">
      <div class="viewer-toolbar">
        <span id="doc-filename">📄 Uploaded File: 2025_IRS_Form_W2_Sarah_Chen.pdf (Page 1 of 1)</span>
        <span style="color:var(--doc-blue-dark);font-family:'IBM Plex Mono',monospace;">DocuSign Envelope #8492-BC91-4402</span>
      </div>

      <article class="paper-sheet" id="paper-sheet-content">
        <!-- Dynamically populated by window.selectStipulation() -->
      </article>
    </section>

    <!-- RIGHT PANE: UNDERWRITER CLEARANCE STAMP & AUTO-CLEAR ACTION -->
    <aside class="clearance-pane">
      <div class="pane-heading">
        <span>Underwriter Clearance Stamp</span>
        <span id="live-model-pill" style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--doc-blue-dark);">gemini-4-argon</span>
      </div>

      <div class="rubber-stamp" id="stamp-box">
        <div style="font-size:15px;">✓ PRIOR-TO-DOCS CLEARED</div>
        <div style="font-size:11px;margin-top:4px;font-weight:600;">STIP #104 · #108 · #112 VERIFIED FOR CLOSING</div>
      </div>

      <div id="checklist-container" style="display:flex;flex-direction:column;gap:8px;">
        <div class="check-row">
          <span>Borrower Name &amp; SSN Match</span>
          <strong>✓ 100% MATCH</strong>
        </div>
        <div class="check-row">
          <span>Form 1003 vs. Document Variance</span>
          <strong>$0.00 (0.0%)</strong>
        </div>
        <div class="check-row">
          <span>DocuSign Tamper-Evident Seal</span>
          <strong>✓ VALIDATED</strong>
        </div>
      </div>

      <button class="btn-autoclear" style="width:100%;padding:12px;font-size:13.5px;" onclick="window.runLiveVertexAI()">
        Auto-Clear Stipulations via Vertex AI
      </button>

      <div class="audit-memo" id="stip-audit-output">
        <strong>UNDERWRITER CLEARANCE LOG:</strong><br/>
        All 3 Prior-to-Docs (PTD) underwriting conditions for Loan #RKT-9948120 have been cross-checked against uploaded borrower artifacts. Stip #104 (2025 W-2 Box 1 $148,500.00), Stip #108 (DocuSigned Credit Inquiry LOE), and Stip #112 (Travelers HO-3 Binder with Rocket Mortgage ISAOA/ATIMA clause) satisfy Fannie Mae Selling Guide criteria.
      </div>
    </aside>
  </main>

  <script>
    const STIP_DOCS = {{
      "104": {{
        filename: "📄 Uploaded File: 2025_IRS_Form_W2_Sarah_Chen.pdf (Page 1 of 1)",
        html: `
          <div class="doc-watermark">
            <span>OMB No. 1545-0008 · 2025 FORM W-2 WAGE AND TAX STATEMENT</span>
            <span>EIN: 94-3194820 · STRIPE INC.</span>
          </div>
          <h3 style="font-size:18px;font-weight:800;color:#0F172A;">2025 IRS Form W-2 — Copy B (To Be Filed With Employee's Federal Tax Return)</h3>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;font-size:13px;background:#F8FAFC;padding:14px;border:1px solid #CBD5E1;border-radius:6px;">
            <div><strong>Employee:</strong> Sarah L. Chen (SSN: ***-**-4819)</div>
            <div><strong>Employer:</strong> Stripe, Inc. · 354 Oyster Point Blvd, South San Francisco, CA</div>
            <div><strong>Box 1 (Wages, tips, other comp):</strong> <span style="font-family:'IBM Plex Mono',monospace;font-weight:800;color:#059669;">$148,500.00</span></div>
            <div><strong>Box 2 (Federal income tax withheld):</strong> <span style="font-family:'IBM Plex Mono',monospace;">$28,410.00</span></div>
            <div><strong>Box 3 (Social security wages):</strong> <span style="font-family:'IBM Plex Mono',monospace;">$148,500.00</span></div>
            <div><strong>Box 5 (Medicare wages and tips):</strong> <span style="font-family:'IBM Plex Mono',monospace;">$148,500.00</span></div>
          </div>
          <div class="verified-highlight">
            <strong>✓ Highlighted Underwriting Match (Stip #104):</strong> Box 1 Wages of <strong>$148,500.00</strong> ($12,375.00/mo) matches Form 1003 Section 1b Base Employment Income with <strong>0.00% variance</strong>. Employer EIN 94-3194820 verified active.
          </div>
          <div class="sig-box">
            <div>
              <div style="font-size:11px;font-weight:700;color:#1D4ED8;text-transform:uppercase;">IRS Transcript Cross-Check</div>
              <div style="font-size:12.5px;color:#0F172A;">Matched against Form 4506-C Wage &amp; Income Transcript</div>
            </div>
            <div class="sig-script">Verified Electronic W-2</div>
          </div>
        `
      }},
      "108": {{
        filename: "📄 Uploaded File: DocuSign_LOE_Credit_Inquiry_09142026.pdf (Page 1 of 1)",
        html: `
          <div class="doc-watermark">
            <span>BORROWER LETTER OF EXPLANATION (LOE) · STIPULATION #108</span>
            <span>DOCUSIGN ENVELOPE: 8492-BC91-4402</span>
          </div>
          <h3 style="font-size:18px;font-weight:800;color:#0F172A;">Letter of Explanation — Recent Credit Bureau Inquiry</h3>
          <p style="font-size:13.5px;line-height:1.65;color:#1E293B;">
            To Rocket Mortgage Underwriting Department:<br/><br/>
            I am writing to explain the hard credit inquiry recorded by <strong>JPMorgan Chase Bank, N.A. on September 14, 2026</strong> on my Equifax and Experian tri-merge credit report. This inquiry occurred when I inquired about increasing the travel limit on my existing personal checking overdraft line prior to our international flight.
          </p>
          <div class="verified-highlight">
            <strong>✓ Highlighted Attestation Clause (Stip #108):</strong> "I hereby certify and attest that <strong>no new credit account, loan, or revolving credit line was opened</strong> as a result of the 09/14/2026 JPMorgan Chase inquiry, and I have incurred <strong>$0.00 in undisclosed monthly debt obligations</strong>."
          </div>
          <div class="sig-box">
            <div>
              <div style="font-size:11px;font-weight:700;color:#1D4ED8;text-transform:uppercase;">DocuSign eSignature Certificate</div>
              <div style="font-size:12px;color:#0F172A;">Signed by Sarah L. Chen on 10/11/2026 at 14:22:09 EDT · IP: 73.162.88.14</div>
            </div>
            <div class="sig-script">Sarah L. Chen</div>
          </div>
        `
      }},
      "112": {{
        filename: "📄 Uploaded File: Travelers_HO3_Insurance_Binder_2026.pdf (Page 1 of 1)",
        html: `
          <div class="doc-watermark">
            <span>ACORD 75 INSURANCE BINDER · POLICY #TRV-HO3-8849201</span>
            <span>EFFECTIVE: 10/25/2026 – 10/25/2027</span>
          </div>
          <h3 style="font-size:18px;font-weight:800;color:#0F172A;">Homeowners Insurance Evidence of Property Coverage (HO-3 Special Form)</h3>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;font-size:13px;background:#F8FAFC;padding:14px;border:1px solid #CBD5E1;border-radius:6px;">
            <div><strong>Insured Property:</strong> 418 Elmhurst Ave, Royal Oak, MI 48067</div>
            <div><strong>Loan Amount:</strong> $460,000.00</div>
            <div><strong>Coverage A (Dwelling Replacement):</strong> <span style="font-family:'IBM Plex Mono',monospace;font-weight:800;color:#059669;">$485,000.00 (100% RCE)</span></div>
            <div><strong>Annual Premium (Escrowed):</strong> <span style="font-family:'IBM Plex Mono',monospace;">$1,680.00/yr ($140.00/mo)</span></div>
            <div><strong>All-Peril Deductible:</strong> <span style="font-family:'IBM Plex Mono',monospace;">$1,500.00 (&lt; 5% Max)</span></div>
            <div><strong>Carrier Rating:</strong> A.M. Best A++ (Travelers Personal Insurance)</div>
          </div>
          <div class="verified-highlight">
            <strong>✓ Highlighted Mortgagee Loss Payee Clause (Stip #112):</strong><br/>
            <code>ROCKET MORTGAGE, LLC, ITS SUCCESSORS AND/OR ASSIGNS ATIMA (ISAOA/ATIMA) · 1050 WOODWARD AVE, DETROIT, MI 48226 · LOAN #RKT-9948120</code>
          </div>
          <div class="sig-box">
            <div>
              <div style="font-size:11px;font-weight:700;color:#1D4ED8;text-transform:uppercase;">Authorized Producer Signature</div>
              <div style="font-size:12px;color:#0F172A;">Bound &amp; Active for 10/25/2026 Closing Date</div>
            </div>
            <div class="sig-script">J. Reynolds, CPCU</div>
          </div>
        `
      }}
    }};

    window.selectStipulation = function(stipId) {{
      document.querySelectorAll('.stip-card').forEach(el => el.classList.remove('active'));
      const card = document.getElementById('stip-' + stipId);
      if (card) card.classList.add('active');
      const doc = STIP_DOCS[stipId] || STIP_DOCS['104'];
      document.getElementById('doc-filename').innerText = doc.filename;
      document.getElementById('paper-sheet-content').innerHTML = doc.html;
    }};

    window.playStipAudioSummary = function(btnEl) {{
      const script = "Underwriting Stipulation Clearance Summary for Loan RKT-9948120, Sarah and David Chen. All three Prior-to-Docs conditions have been verified and auto-cleared. Stipulation 104 is cleared with a 100 percent match on Sarah Chen's 2025 Form W-2 Box 1 wages of 148,500 dollars. Stipulation 108 is cleared with a DocuSigned Letter of Explanation confirming the September 14th Chase inquiry resulted in zero new debt. Stipulation 112 is cleared with a Travelers HO-3 binder providing 485,000 dollars in replacement cost coverage and the exact Rocket Mortgage ISAOA ATIMA mortgagee clause.";
      if (window.playLiveCallClip) {{
        window.playLiveCallClip(script, "Aoede", "Senior Mortgage Underwriter", btnEl);
      }}
    }};

    window.runLiveVertexAI = async function() {{
      const model = window.getSelectedModel ? window.getSelectedModel() : 'gemini-4-argon';
      const outEl = document.getElementById('stip-audit-output');
      outEl.innerHTML = '<em>Running Vertex AI (' + model + ') Stipulation Clearance Verification across Stips #104, #108, and #112...</em>';
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '2.2',
            model: model,
            user_input: 'Verify and clear Underwriting Stipulations #104 (2025 W-2 Match $148,500), #108 (Signed LOE for Credit Inquiry), and #112 (Homeowners Insurance Binder $485,000 replacement cost with ISAOA/ATIMA clause).'
          }})
        }});
        const data = await res.json();
        const text = data.output || data.response || data.result || '';
        if (text) {{
          outEl.innerHTML = '<strong>VERTEX AI (' + model.toUpperCase() + ') CLEARANCE CERTIFICATE:</strong><br/>' + text.replace(/\\n/g, '<br/>');
        }} else {{
          outEl.innerHTML = '<strong>ALL 3 STIPULATIONS CLEARED (' + model + '):</strong> Stip #104, Stip #108, and Stip #112 verified and stamped Clear-to-Close.';
        }}
      }} catch (e) {{
        outEl.innerHTML = '<strong>ALL 3 STIPULATIONS CLEARED:</strong> Stip #104, Stip #108, and Stip #112 verified and stamped Clear-to-Close.';
      }}
    }};

    document.addEventListener('DOMContentLoaded', () => {{
      window.selectStipulation('104');
    }});
  </script>

  {floating_bar}
</body>
</html>"""
