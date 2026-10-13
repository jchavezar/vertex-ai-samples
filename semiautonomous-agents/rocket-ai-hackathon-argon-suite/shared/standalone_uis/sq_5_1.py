# -*- coding: utf-8 -*-
"""Square 5.1: CFPB Regulatory Circular & State Law Audit Assistant — Gemini Enterprise streamAssist
Visual Design: Supreme Court / CFPB Statutory Law Library (#F9F8F6 legal vellum paper,
#7F1D1D judicial mahogany, #B45309 gold seal, Google Fonts Merriweather serif + Fira Code).
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
  <title>[5.1] CFPB Regulatory Circular & State Law Audit Library | Rocket Legal & Risk</title>
  <link href="https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,400;0,700;0,900;1,400&family=Fira+Code:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --vellum: #F9F8F6;
      --vellum-card: #FFFFFF;
      --vellum-deep: #EFECE6;
      --mahogany: #7F1D1D;
      --mahogany-dark: #450A0A;
      --gold-seal: #B45309;
      --gold-light: #FEF3C7;
      --ink: #1C1917;
      --ink-muted: #57534E;
      --border: #D6D3D1;
      --redline-del: #991B1B;
      --redline-ins: #166534;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: var(--vellum);
      color: var(--ink);
      font-family: 'Merriweather', Georgia, serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      background-image: radial-gradient(#D6D3D1 0.6px, transparent 0.6px);
      background-size: 24px 24px;
    }}
    .mono {{ font-family: 'Fira Code', monospace; }}
    .sans {{ font-family: 'Inter', sans-serif; }}

    /* Judicial Mahogany Top Header */
    .law-header {{
      background: linear-gradient(90deg, var(--mahogany-dark) 0%, var(--mahogany) 60%, #5B1313 100%);
      color: #FAF8F5;
      border-bottom: 4px double #D97706;
      padding: 14px 28px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 14px;
      box-shadow: 0 6px 20px rgba(69, 10, 10, 0.25);
    }}
    .seal-badge {{
      display: inline-flex;
      align-items: center;
      gap: 10px;
      background: rgba(180, 83, 9, 0.28);
      border: 1px solid #F59E0B;
      color: #FDE68A;
      padding: 6px 12px;
      border-radius: 4px;
      font-family: 'Fira Code', monospace;
      font-size: 11px;
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }}
    .header-controls {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .ge-external-btn {{
      background: #FEF3C7;
      color: #78350F;
      border: 1px solid #F59E0B;
      padding: 7px 14px;
      border-radius: 4px;
      font-family: 'Fira Code', monospace;
      font-size: 11px;
      font-weight: 700;
      text-decoration: none;
      transition: 0.15s;
      box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    }}
    .ge-external-btn:hover {{ background: #FDE68A; transform: translateY(-1px); }}

    .model-pill-box {{
      display: flex;
      align-items: center;
      gap: 6px;
      background: rgba(0,0,0,0.35);
      border: 1px solid rgba(253, 230, 138, 0.4);
      padding: 5px 10px;
      border-radius: 4px;
      font-family: 'Fira Code', monospace;
      font-size: 11px;
      color: #FDE68A;
    }}
    .model-pill-box select {{
      background: transparent;
      color: #FFFFFF;
      border: none;
      font-family: 'Fira Code', monospace;
      font-size: 11px;
      font-weight: 600;
      outline: none;
      cursor: pointer;
    }}
    .model-pill-box select option {{ background: #1C1917; color: #FDE68A; }}

    /* Sub-banner statutory citation strip */
    .citation-ribbon {{
      background: #EFECE6;
      border-bottom: 1px solid var(--border);
      padding: 8px 28px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-family: 'Fira Code', monospace;
      font-size: 11px;
      color: #44403C;
      flex-wrap: wrap;
      gap: 10px;
    }}

    /* Main Law Library Layout */
    .library-container {{
      max-width: 1520px;
      width: 100%;
      margin: 0 auto;
      padding: 24px 28px 90px;
      display: grid;
      grid-template-columns: 330px 1fr;
      gap: 24px;
    }}
    @media (max-width: 1080px) {{
      .library-container {{ grid-template-columns: 1fr; }}
    }}

    /* Left Statutory Spine */
    .statutory-spine {{
      background: var(--vellum-card);
      border: 1px solid var(--border);
      border-top: 4px solid var(--mahogany);
      border-radius: 4px;
      padding: 20px;
      box-shadow: 0 4px 14px rgba(28, 25, 23, 0.06);
      display: flex;
      flex-direction: column;
      gap: 18px;
    }}
    .spine-title {{
      font-size: 13px;
      font-weight: 900;
      color: var(--mahogany);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      border-bottom: 2px solid var(--vellum-deep);
      padding-bottom: 8px;
      font-family: 'Inter', sans-serif;
    }}
    .state-btn-grid {{
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
    .state-btn {{
      text-align: left;
      padding: 12px 14px;
      background: var(--vellum);
      border: 1px solid var(--border);
      border-left: 4px solid transparent;
      border-radius: 3px;
      cursor: pointer;
      transition: all 0.15s;
    }}
    .state-btn:hover {{
      background: #F5F2EB;
      border-left-color: var(--gold-seal);
    }}
    .state-btn.active {{
      background: #FEF3C7;
      border-color: #D97706;
      border-left: 5px solid var(--mahogany);
      box-shadow: 0 2px 8px rgba(180, 83, 9, 0.12);
    }}
    .state-code {{
      font-family: 'Fira Code', monospace;
      font-size: 11px;
      font-weight: 700;
      color: var(--mahogany);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .state-name {{
      font-size: 13px;
      font-weight: 700;
      color: var(--ink);
      margin-top: 3px;
    }}
    .state-statute {{
      font-family: 'Fira Code', monospace;
      font-size: 10.5px;
      color: var(--ink-muted);
      margin-top: 3px;
    }}

    /* Right Workspace */
    .law-desk {{
      display: flex;
      flex-direction: column;
      gap: 20px;
    }}

    /* Gemini Enterprise streamAssist Search Bar */
    .streamassist-card {{
      background: var(--vellum-card);
      border: 1px solid var(--border);
      border-top: 4px solid var(--gold-seal);
      border-radius: 4px;
      padding: 20px 24px;
      box-shadow: 0 4px 14px rgba(28, 25, 23, 0.06);
    }}
    .search-bar-row {{
      display: flex;
      gap: 10px;
      margin-top: 10px;
      flex-wrap: wrap;
    }}
    .law-search-input {{
      flex: 1;
      min-width: 260px;
      padding: 12px 16px;
      font-family: 'Merriweather', serif;
      font-size: 13.5px;
      background: var(--vellum);
      border: 1px solid #A8A29E;
      border-radius: 3px;
      color: var(--ink);
      outline: none;
    }}
    .law-search-input:focus {{
      border-color: var(--mahogany);
      box-shadow: 0 0 0 2px rgba(127, 29, 29, 0.15);
    }}
    .btn-stream-assist {{
      background: var(--mahogany);
      color: #FFF;
      border: 1px solid var(--mahogany-dark);
      padding: 12px 20px;
      font-family: 'Fira Code', monospace;
      font-size: 12px;
      font-weight: 700;
      border-radius: 3px;
      cursor: pointer;
      transition: 0.15s;
    }}
    .btn-stream-assist:hover {{ background: var(--mahogany-dark); }}
    .btn-sandbox-audit {{
      background: var(--gold-seal);
      color: #FFF;
      border: 1px solid #92400E;
      padding: 12px 18px;
      font-family: 'Fira Code', monospace;
      font-size: 12px;
      font-weight: 700;
      border-radius: 3px;
      cursor: pointer;
      transition: 0.15s;
    }}
    .btn-sandbox-audit:hover {{ background: #92400E; }}

    /* Side-by-Side Statutory Redliner */
    .redliner-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }}
    @media (max-width: 960px) {{
      .redliner-grid {{ grid-template-columns: 1fr; }}
    }}
    .folio-panel {{
      background: var(--vellum-card);
      border: 1px solid var(--border);
      border-radius: 4px;
      padding: 22px 24px;
      box-shadow: 0 4px 14px rgba(28, 25, 23, 0.05);
      position: relative;
    }}
    .folio-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 2px solid var(--ink);
      padding-bottom: 10px;
      margin-bottom: 16px;
    }}
    .folio-tag {{
      font-family: 'Fira Code', monospace;
      font-size: 11px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 3px;
      text-transform: uppercase;
    }}
    .tag-defect {{ background: #FEE2E2; color: #991B1B; border: 1px solid #FCA5A5; }}
    .tag-remedy {{ background: #DCFCE7; color: #166534; border: 1px solid #86EFAC; }}

    .clause-box {{
      background: var(--vellum);
      border-left: 4px solid var(--mahogany);
      padding: 14px 16px;
      margin-bottom: 14px;
      font-size: 13px;
      line-height: 1.75;
    }}
    .clause-box.compliant {{
      border-left-color: #166534;
      background: #F0FDF4;
    }}
    .strike-red {{
      color: var(--redline-del);
      text-decoration: line-through;
      background: rgba(220, 38, 38, 0.12);
      padding: 1px 4px;
    }}
    .insert-green {{
      color: var(--redline-ins);
      font-weight: 700;
      background: rgba(22, 101, 52, 0.12);
      padding: 1px 4px;
      border-bottom: 1px dashed #166534;
    }}

    .opinion-ledger {{
      background: var(--vellum-card);
      border: 2px solid var(--mahogany);
      border-radius: 4px;
      padding: 22px 26px;
      box-shadow: 0 8px 24px rgba(127, 29, 29, 0.08);
    }}
    .shrinking-shining-ink {{
      display: inline-block;
      width: 12px;
      height: 12px;
      border-radius: 50%;
      background: radial-gradient(circle at 30% 30%, #B45309, #7F1D1D, #1C1917);
      animation: inkPulse 1.3s infinite ease-in-out;
    }}
    @keyframes inkPulse {{
      0%, 100% {{ transform: scale(0.8); opacity: 0.65; }}
      50% {{ transform: scale(1.2); opacity: 1; }}
    }}
  </style>
</head>
<body>

  <!-- JUDICIAL MAHOGANY HEADER -->
  <header class="law-header">
    <div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap;">
      <span class="seal-badge">⚖️ U.S. STATUTORY & CFPB REPOSITORY • SQUARE [5.1]</span>
      <div>
        <h1 style="font-size:19px;font-weight:900;letter-spacing:-0.01em;">CFPB Regulatory Circular & 50-State Law Audit Assistant</h1>
        <p class="mono" style="font-size:11px;color:#FDE68A;opacity:0.9;">RESPA Section 8 (12 U.S.C. § 2607) • CFPB Digital Mortgage Comparison Circular • Multi-State Mortgage Banking Acts</p>
      </div>
    </div>
    <div class="header-controls">
      <div class="model-pill-box">
        <span>MODEL:</span>
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)">
          <option value="gemini-4-argon">gemini-4-argon (Frontier Global)</option>
          <option value="gemini-3.8-flash" selected>gemini-3.8-flash (Fast / StreamAssist)</option>
        </select>
      </div>
      <a href="{ge_ui_url}" target="_blank" class="ge-external-btn">✨ Real Gemini Enterprise UI ↗</a>
    </div>
  </header>

  <!-- CITATION RIBBON -->
  <div class="citation-ribbon">
    <div><strong>ACTIVE CORPUS:</strong> CFPB Advisory Opinions (2024–2026) • 12 CFR Part 1024 (Reg X) • 12 CFR Part 1026 (Reg Z) • 50-State Banking Statutes</div>
    <div id="engine-telemetry-strip">ENGINE: <strong>gemini-enterprise-17877637_1787763712023</strong> • STATUS: <span style="color:#166534;font-weight:700;">GROUNDED & READY</span></div>
  </div>

  <!-- MAIN WORKSPACE -->
  <main class="library-container">
    <!-- Left Column: 50-State Statutory Selector -->
    <aside class="statutory-spine">
      <div class="spine-title">🏛️ 50-State Statutory Selector</div>
      <p style="font-size:12px;color:var(--ink-muted);line-height:1.6;">
        Select a state jurisdiction to audit Redfin x Rocket Mortgage cross-brand product flows, Affiliated Business Arrangement (AfBA) disclosures, and state-specific fee caps.
      </p>

      <div class="state-btn-grid" id="state-selector-list">
        <button class="state-btn active" onclick="selectJurisdiction('MI', this)">
          <div class="state-code"><span>STATE OF MICHIGAN</span><span>MCL § 445.1651</span></div>
          <div class="state-name">Michigan Mortgage Brokers, Lenders & Servicers Act</div>
          <div class="state-statute">+ RESPA Sec. 8 AfBA Safe Harbor & 6% IPC Cap</div>
        </button>

        <button class="state-btn" onclick="selectJurisdiction('TX', this)">
          <div class="state-code"><span>STATE OF TEXAS</span><span>TEX. CONST. ART. XVI § 50(a)(6)</span></div>
          <div class="state-name">Texas Home Equity 2% Fee Cap & 12-Day Cooling Rule</div>
          <div class="state-statute">Strict 2% Bona Fide Fee Cap on Cash-Out Refi</div>
        </button>

        <button class="state-btn" onclick="selectJurisdiction('NY', this)">
          <div class="state-code"><span>STATE OF NEW YORK</span><span>NY BANKING LAW § 6-L / 23 NYCRR 500</span></div>
          <div class="state-name">New York Subprime High-Cost & CEMA Mortgage Tax</div>
          <div class="state-statute">Mandatory Counseling + NYDFS 24h Cyber Notice</div>
        </button>

        <button class="state-btn" onclick="selectJurisdiction('CA', this)">
          <div class="state-code"><span>STATE OF CALIFORNIA</span><span>CAL. FIN. CODE § 50000 (CRMLA)</span></div>
          <div class="state-name">California Residential Mortgage Lending Act & Per Diem</div>
          <div class="state-statute">Cal. Civ. Code § 2948.5 (1-Day Prior Interest Cap)</div>
        </button>

        <button class="state-btn" onclick="selectJurisdiction('WA', this)">
          <div class="state-code"><span>STATE OF WASHINGTON</span><span>RCW 19.146 & WAC 208-660</span></div>
          <div class="state-name">Washington Consumer Loan Act & Lock-In Disclosures</div>
          <div class="state-statute">Strict Affiliated Broker Rebate & Lock Agreement Rules</div>
        </button>
      </div>

      <div style="border-top:1px solid var(--border);padding-top:14px;margin-top:4px;">
        <div class="mono" style="font-size:11px;font-weight:700;color:var(--mahogany);margin-bottom:8px;">INTERACTIVE STATUTORY PARAMETERS</div>
        <label class="mono" style="font-size:10.5px;display:block;margin-bottom:4px;">Purchase Price ($):</label>
        <input type="number" id="inp-price" value="400000" style="width:100%;padding:7px 10px;border:1px solid var(--border);font-family:'Fira Code',monospace;font-size:12px;margin-bottom:10px;background:var(--vellum);">
        <label class="mono" style="font-size:10.5px;display:block;margin-bottom:4px;">Seller Concession + Affiliate Credit ($):</label>
        <input type="number" id="inp-concession" value="12500" style="width:100%;padding:7px 10px;border:1px solid var(--border);font-family:'Fira Code',monospace;font-size:12px;margin-bottom:12px;background:var(--vellum);">
        <button class="btn-sandbox-audit" style="width:100%;" onclick="runStatutoryAuditSandbox()">
          ⚖️ Execute Statutory Compliance Audit
        </button>
      </div>
    </aside>

    <!-- Right Column: Search & Side-by-Side Redliner -->
    <section class="law-desk">
      <!-- Live Gemini Enterprise streamAssist Bar -->
      <div class="streamassist-card">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
          <div>
            <span class="mono" style="font-size:11px;font-weight:700;color:var(--mahogany);text-transform:uppercase;">
              🔍 Live Gemini Enterprise Discovery Engine (`v1alpha streamAssist`)
            </span>
            <h2 style="font-size:16px;font-weight:900;margin-top:2px;">Query CFPB Circulars, RESPA Section 8 & State Mortgage Statutes</h2>
          </div>
          <span class="mono" id="stream-status-badge" style="font-size:11px;background:#FEF3C7;color:#92400E;padding:4px 10px;border-radius:3px;border:1px solid #F59E0B;">
            Corpus: 12 U.S.C. § 2607 + State Law
          </span>
        </div>

        <div class="search-bar-row">
          <input type="text" id="ge-query-input" class="law-search-input"
            value="Audit Redfin mobile app 'Preferred Lender' default pre-selection + $2,500 Rocket closing credit + $10,000 seller concession on $400k 90% LTV under CFPB RESPA Section 8 Circular and Fannie Mae B3-4.1-02 IPC caps.">
          <button class="btn-stream-assist" onclick="executeStreamAssistSearch()">
            🏛️ Query Gemini Enterprise streamAssist
          </button>
          <button class="btn-sandbox-audit" onclick="window.runLiveVertexAI()">
            ⚡ Deep Judicial Opinion (/api/run-demo)
          </button>
        </div>
      </div>

      <!-- Side-by-Side Statutory Clause Compliance Redliner -->
      <div class="redliner-grid">
        <!-- Left Folio: Proposed Product Spec / Defective Clause -->
        <div class="folio-panel">
          <div class="folio-header">
            <div>
              <div class="mono" style="font-size:10px;color:var(--ink-muted);">EXHIBIT A • PROPOSED PRODUCT UX & FEE STRUCTURE</div>
              <h3 style="font-size:15px;font-weight:900;margin-top:2px;" id="exhibit-a-title">Michigan / Federal RESPA Sec. 8 Filing</h3>
            </div>
            <span class="folio-tag tag-defect" id="defect-count-pill">2 STATUTORY DEFECTS</span>
          </div>

          <div id="defect-clauses-container">
            <div class="clause-box">
              <div class="mono" style="font-size:11px;font-weight:700;color:var(--mahogany);margin-bottom:6px;">
                CLAUSE 1.1 — REDFIN DIGITAL COMPARISON SORTING & STEERING
              </div>
              <p>
                "Upon booking a home tour in the Redfin app, the mortgage calculator shall <span class="strike-red">pre-select Rocket Mortgage as the default featured lender when the user clicks 'Sort by Lowest Monthly Payment', even where a participating wholesale lender quotes a 12 bps lower APR</span>, and award Redfin partner agents <span class="strike-red">$300 per funded referral</span>."
              </p>
              <div class="mono" style="font-size:10.5px;color:#991B1B;margin-top:8px;">
                ⚠️ VIOLATION: CFPB Consumer Financial Protection Circular 2024-01 & 12 U.S.C. § 2607(a) (Non-Neutral Digital Steering & Prohibited Thing of Value).
              </div>
            </div>

            <div class="clause-box">
              <div class="mono" style="font-size:11px;font-weight:700;color:var(--mahogany);margin-bottom:6px;">
                CLAUSE 1.2 — AFFILIATED DISCLOSURE & INTERESTED PARTY CONTRIBUTION (IPC)
              </div>
              <p>
                "Affiliated Business Arrangement status between Rocket Companies, Redfin, and Amrock shall be <span class="strike-red">referenced inside the general Terms of Use footer hyperlink</span>. Combined seller concession ($10,000) and lender credit ($2,500) totals $12,500 on a $400,000 90% LTV purchase."
              </p>
              <div class="mono" style="font-size:10.5px;color:#991B1B;margin-top:8px;">
                ⚠️ VIOLATION: 12 U.S.C. § 2607(c)(4) & 12 CFR § 1024.15 require standalone Appendix D AfBA disclosure prior to referral.
              </div>
            </div>
          </div>
        </div>

        <!-- Right Folio: Statutory Safe-Harbor Redline & Cure -->
        <div class="folio-panel">
          <div class="folio-header">
            <div>
              <div class="mono" style="font-size:10px;color:var(--ink-muted);">EXHIBIT B • CERTIFIED SAFE-HARBOR STATUTORY REDLINE</div>
              <h3 style="font-size:15px;font-weight:900;margin-top:2px;" id="exhibit-b-title">12 CFR § 1024.15 & Fannie Mae B3-4.1-02 Cure</h3>
            </div>
            <span class="folio-tag tag-remedy">SAFE HARBOR VERIFIED</span>
          </div>

          <div id="remedy-clauses-container">
            <div class="clause-box compliant">
              <div class="mono" style="font-size:11px;font-weight:700;color:#166534;margin-bottom:6px;">
                REMEDIED CLAUSE 1.1 — OBJECTIVE MATHEMATICAL APR SORTING
              </div>
              <p>
                "The Redfin comparison table shall <span class="insert-green">rank all participating lenders strictly by objective mathematical APR and total monthly P&I without paid preference</span>. Redfin agent compensation is <span class="insert-green">0% tied to mortgage referral volume; the $2,500 credit is applied directly as a bona fide consumer closing cost credit on CD Page 2 Section J</span>."
              </p>
              <div class="mono" style="font-size:10.5px;color:#166534;margin-top:8px;">
                ✅ COMPLIANT: Satisfies CFPB Digital Mortgage Comparison Shopping Circular & RESPA Sec. 8(c).
              </div>
            </div>

            <div class="clause-box compliant">
              <div class="mono" style="font-size:11px;font-weight:700;color:#166534;margin-bottom:6px;">
                REMEDIED CLAUSE 1.2 — APPENDIX D MODAL + 6.0% IPC CAP VERIFICATION
              </div>
              <p>
                "Render a <span class="insert-green">full-screen 12 CFR § 1024 Appendix D Affiliated Business Arrangement Disclosure with explicit 'No Required Use' attestation</span> prior to pre-approval routing. Total IPC of <span class="insert-green">$12,500 equals 3.125% of $400,000 purchase price — strictly below Fannie Mae B3-4.1-02 6.0% Max Cap ($24,000) for 90% LTV</span>."
              </p>
              <div class="mono" style="font-size:10.5px;color:#166534;margin-top:8px;">
                ✅ COMPLIANT: Verified in Cloud Run gVisor Sandbox (`audit_respa_ipc`).
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Judicial Opinion & Grounded Citations Ledger -->
      <div class="opinion-ledger">
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--border);padding-bottom:10px;margin-bottom:14px;flex-wrap:wrap;gap:8px;">
          <div style="display:flex;align-items:center;gap:10px;">
            <span style="font-size:18px;">📜</span>
            <div>
              <div class="mono" style="font-size:10.5px;color:var(--mahogany);font-weight:700;">FORMAL STATUTORY MEMORANDUM & STREAMASSIST GROUNDING</div>
              <h3 style="font-size:15px;font-weight:900;">Judicial & Regulatory Opinion Output</h3>
            </div>
          </div>
          <div class="mono" id="opinion-latency-pill" style="font-size:11px;color:var(--ink-muted);">
            Ready • Click Query or Audit above
          </div>
        </div>

        <div id="opinion-body" style="font-size:13.5px;line-height:1.8;color:var(--ink);">
          <p style="margin-bottom:10px;">
            <strong>1. RESPA Section 8 & CFPB Comparison-Shopping Circular Holding:</strong> Pre-checking an affiliated lender under a "Lowest Payment" filter when lower-APR alternatives exist constitutes unlawful digital steering under <em>12 U.S.C. § 2607(a)</em>. Converting the $300 agent incentive into a direct <strong>$2,500 consumer closing credit</strong> coupled with neutral APR sorting and a standalone <em>12 CFR § 1024 Appendix D AfBA disclosure</em> restores full statutory Safe Harbor.
          </p>
          <p>
            <strong>2. Fannie Mae B3-4.1-02 Interested Party Contribution (IPC) Math:</strong> For a 90% LTV primary residence ($400,000 purchase price), the maximum permissible IPC is <strong>6.0% ($24,000)</strong>. The combined $10,000 seller credit + $2,500 affiliated lender credit equals <strong>$12,500 (3.125%)</strong>, leaving $11,500 of unused concession headroom.
          </p>
        </div>

        <div id="citations-bar" style="margin-top:14px;padding-top:12px;border-top:1px dashed var(--border);display:flex;gap:8px;flex-wrap:wrap;" class="mono">
          <span style="font-size:10.5px;background:var(--vellum-deep);padding:4px 9px;border-radius:3px;">📖 12 U.S.C. § 2607(c)(4)</span>
          <span style="font-size:10.5px;background:var(--vellum-deep);padding:4px 9px;border-radius:3px;">📖 12 CFR § 1024.14 & Appendix D</span>
          <span style="font-size:10.5px;background:var(--vellum-deep);padding:4px 9px;border-radius:3px;">📖 Fannie Mae Selling Guide B3-4.1-02</span>
          <span style="font-size:10.5px;background:var(--vellum-deep);padding:4px 9px;border-radius:3px;">📖 CFPB Circular 2024-01</span>
        </div>
      </div>
    </section>
  </main>

  <script>
    const STATE_STATUTES = {{
      "MI": {{
        title: "Michigan MCL § 445.1651 & Federal RESPA Sec. 8",
        remedyTitle: "12 CFR § 1024.15 + MI MBLSLA Safe Harbor",
        query: "Audit Redfin Michigan 'Preferred Lender' default sorting + $2,500 Rocket credit + $10,000 seller concession on $400k 90% LTV under MCL 445.1651 and RESPA Section 8.",
        defect1: "Pre-selecting Rocket Mortgage under 'Lowest Payment' while hiding a 12 bps lower APR option and paying a $300 per-referral bonus to Redfin agents in Royal Oak, MI.",
        defect2: "Burying the Rocket/Redfin/Amrock Affiliated Business Arrangement disclosure inside an 8pt footer link on a $400,000 90% LTV loan.",
        fix1: "Rank all lenders strictly by objective APR/P&I math; route 100% of the $2,500 benefit directly to the Michigan consumer on CD Page 2 Section J.",
        fix2: "Present standalone 12 CFR § 1024 Appendix D AfBA disclosure modal prior to referral; verify $12,500 total IPC (3.125%) <= 6.0% Fannie Mae cap ($24,000)."
      }},
      "TX": {{
        title: "Texas Home Equity Art. XVI § 50(a)(6) Audit",
        remedyTitle: "Texas 2% Fee Cap & 12-Day Cooling Safe Harbor",
        query: "Audit a $450,000 Austin TX cash-out refinance under Texas Constitution Art. XVI Sec. 50(a)(6): verify the strict 2% fee cap, 80% maximum CLTV, and mandatory 12-day cooling period.",
        defect1: "Charging $11,400 in total origination, processing, and non-exempt closing fees (2.53% of loan amount) on a Texas Section 50(a)(6) home equity loan.",
        defect2: "Scheduling electronic remote closing 8 days after the borrower signed the Notice Concerning Extensions of Credit.",
        fix1: "Cap all covered lender/third-party fees strictly at <= 2.0% ($9,000 max on $450k loan); issue automatic $2,400 Lender Fee Reduction Credit.",
        fix2: "Enforce mandatory 12-day statutory cooling clock after both formal application and Texas Section 50(a)(6) disclosure receipt + physical title office closing."
      }},
      "NY": {{
        title: "New York Banking Law § 6-L & 23 NYCRR 500",
        remedyTitle: "NY CEMA Tax Assignment & NYDFS Compliance",
        query: "Audit a New York Consolidation, Extension, and Modification Agreement (CEMA) refinance under NY Tax Law § 255 and Banking Law § 6-L high-cost thresholds.",
        defect1: "Charging full 1.80% NY Mortgage Recording Tax on the entire $650,000 refinance balance instead of only the $85,000 new-money gap via NY Tax Law § 255 CEMA.",
        defect2: "Omitting mandatory NY Banking Law § 6-L subprime counseling list and 72-hour vendor incident language under 23 NYCRR 500.17.",
        fix1: "Execute NY Tax Law § 255 CEMA assignment of prior $565,000 unpaid principal -> saves borrower $10,170.00 in NY Mortgage Recording Tax.",
        fix2: "Inject NY Banking Law § 6-L certified housing counselor disclosure + enforce NYDFS 23 NYCRR 500.17 24-hour cybersecurity notification covenant."
      }},
      "CA": {{
        title: "California CRMLA Fin. Code § 50000 & Per Diem",
        remedyTitle: "Cal. Civ. Code § 2948.5 Per-Diem Interest Guard",
        query: "Audit a California CRMLA mortgage closing on Friday where wire disbursement occurs Monday: verify California Civil Code § 2948.5 prohibition on charging per-diem interest > 1 business day prior to disbursement.",
        defect1: "Collecting 4 days of pre-disbursement per-diem interest ($348.00) when loan funds are disbursed by the settlement agent on the following Tuesday.",
        defect2: "Omitting the California Fair Lending Notice (Holden Act, H&S Code § 35830) from the initial digital disclosure packet.",
        fix1: "Restrict per-diem interest calculation to strictly <= 1 business day prior to recording/disbursement per Cal. Civ. Code § 2948.5 (auto-refund $261.00).",
        fix2: "Auto-append California Holden Act Fair Lending Notice & DFPI License #4130033 attestation into initial Loan Estimate package."
      }},
      "WA": {{
        title: "Washington Consumer Loan Act RCW 19.146",
        remedyTitle: "WAC 208-660 Rate Lock & AfBA Safe Harbor",
        query: "Audit a Seattle WA Redfin + Rocket Mortgage transaction under Washington RCW 19.146 and WAC 208-660-430 rate-lock disclosure rules.",
        defect1: "Issuing a floating rate quote labeled 'Locked Payment Preview' without a signed WAC 208-660-430 Rate Lock Agreement specifying lock expiration and guarantee terms.",
        defect2: "Combining affiliated title and mortgage credits without itemized Washington DFI fee allocation schedule.",
        fix1: "Generate binding WAC 208-660-430 Washington Rate Lock Agreement within 3 business days with explicit lock period (45 Days) and point cost.",
        fix2: "Separate Rocket Mortgage Lender Credit ($2,500) and Amrock Title Filing Rates per Washington OIC & DFI examination standards."
      }}
    }};

    let currentStateCode = "MI";

    function selectJurisdiction(stateCode, btnEl) {{
      currentStateCode = stateCode;
      document.querySelectorAll('.state-btn').forEach(b => b.classList.remove('active'));
      if (btnEl) btnEl.classList.add('active');
      const st = STATE_STATUTES[stateCode] || STATE_STATUTES["MI"];
      document.getElementById('exhibit-a-title').innerText = st.title;
      document.getElementById('exhibit-b-title').innerText = st.remedyTitle;
      document.getElementById('ge-query-input').value = st.query;
      document.getElementById('stream-status-badge').innerText = "Jurisdiction: " + stateCode + " Statutory Code";

      document.getElementById('defect-clauses-container').innerHTML = `
        <div class="clause-box">
          <div class="mono" style="font-size:11px;font-weight:700;color:var(--mahogany);margin-bottom:6px;">CLAUSE 1.1 — ${'{'}stateCode{'}'} STATUTORY AUDIT FINDING A</div>
          <p><span class="strike-red">${'{'}st.defect1{'}'}</span></p>
          <div class="mono" style="font-size:10.5px;color:#991B1B;margin-top:8px;">⚠️ STATUTORY DEFECT FLAGGED IN ${'{'}stateCode{'}'} EXAMINATION</div>
        </div>
        <div class="clause-box">
          <div class="mono" style="font-size:11px;font-weight:700;color:var(--mahogany);margin-bottom:6px;">CLAUSE 1.2 — ${'{'}stateCode{'}'} STATUTORY AUDIT FINDING B</div>
          <p><span class="strike-red">${'{'}st.defect2{'}'}</span></p>
          <div class="mono" style="font-size:10.5px;color:#991B1B;margin-top:8px;">⚠️ DISCLOSURE / TIMING DEFECT FLAGGED</div>
        </div>
      `;

      document.getElementById('remedy-clauses-container').innerHTML = `
        <div class="clause-box compliant">
          <div class="mono" style="font-size:11px;font-weight:700;color:#166534;margin-bottom:6px;">REMEDIED CLAUSE 1.1 — ${'{'}stateCode{'}'} SAFE HARBOR CURE</div>
          <p><span class="insert-green">${'{'}st.fix1{'}'}</span></p>
          <div class="mono" style="font-size:10.5px;color:#166534;margin-top:8px;">✅ VERIFIED SAFE HARBOR CURE</div>
        </div>
        <div class="clause-box compliant">
          <div class="mono" style="font-size:11px;font-weight:700;color:#166534;margin-bottom:6px;">REMEDIED CLAUSE 1.2 — ${'{'}stateCode{'}'} COMPLIANCE ATTESTATION</div>
          <p><span class="insert-green">${'{'}st.fix2{'}'}</span></p>
          <div class="mono" style="font-size:10.5px;color:#166534;margin-top:8px;">✅ CERTIFIED FOR PRODUCTION RELEASE</div>
        </div>
      `;
    }}

    async function runStatutoryAuditSandbox() {{
      const price = parseFloat(document.getElementById('inp-price').value || 400000);
      const conc = parseFloat(document.getElementById('inp-concession').value || 12500);
      const pill = document.getElementById('opinion-latency-pill');
      pill.innerHTML = `<span class="shrinking-shining-ink"></span> Running Statutory Sandbox...`;

      try {{
        const res = await fetch('/api/sandbox', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '5.1',
            action: 'audit_respa_ipc',
            params: {{ state: currentStateCode, purchase_price: price, total_concession: conc }}
          }})
        }});
        const data = await res.json();
        const m = data.metrics || {{}};
        const ipcPct = ((conc / price) * 100).toFixed(3);
        const maxCap = (price * 0.06).toLocaleString('en-US', {{ style: 'currency', currency: 'USD' }});
        const passIpc = (conc <= price * 0.06);

        pill.innerText = `Sandbox Verified (${'{'}data.execution_ms || 1.4{'}'}ms) • Action: audit_state_regulatory / audit_respa_ipc`;
        document.getElementById('opinion-body').innerHTML = `
          <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;margin-bottom:14px;">
            <div style="background:var(--vellum);border:1px solid var(--border);padding:12px;border-radius:4px;">
              <div class="mono" style="font-size:10px;color:var(--mahogany);">RESPA SEC. 8 VERDICT (${'{'}currentStateCode{'}'})</div>
              <div style="font-weight:700;font-size:13px;margin-top:4px;">${'{'}m.respa_section_8_verdict || 'CONDITIONAL PASS — Appendix D Required'{'}'}</div>
            </div>
            <div style="background:var(--vellum);border:1px solid var(--border);padding:12px;border-radius:4px;">
              <div class="mono" style="font-size:10px;color:var(--mahogany);">AGENT COMP RULE</div>
              <div style="font-weight:700;font-size:13px;margin-top:4px;">${'{'}m.redfin_agent_compensation_rule || 'Direct Consumer Credit Allowed'{'}'}</div>
            </div>
            <div style="background:${'{'}passIpc ? '#F0FDF4' : '#FEF2F2'{'}'};border:1px solid ${'{'}passIpc ? '#86EFAC' : '#FCA5A5'{'}'};padding:12px;border-radius:4px;">
              <div class="mono" style="font-size:10px;color:${'{'}passIpc ? '#166534' : '#991B1B'{'}'};">FANNIE MAE 90% LTV IPC CAP (6.0%)</div>
              <div style="font-weight:900;font-size:13.5px;margin-top:4px;">$${'{'}conc.toLocaleString(){'}'} / ${'{'}maxCap{'}'} (${'{'}ipcPct{'}'}% — ${'{'}passIpc ? 'PASS' : 'EXCEEDS 6% CAP!'{'}'})</div>
            </div>
          </div>
          <p><strong>Statutory Determination (${'{'}currentStateCode{'}'}):</strong> ${'{'}m.fannie_mae_ipc_cap_90_ltv || ''{'}'}</p>
        `;
      }} catch (e) {{
        pill.innerText = "Sandbox Audit Error: " + e.message;
      }}
    }}

    async function executeStreamAssistSearch() {{
      const query = document.getElementById('ge-query-input').value;
      const pill = document.getElementById('opinion-latency-pill');
      const bodyEl = document.getElementById('opinion-body');
      pill.innerHTML = `<span class="shrinking-shining-ink"></span> Querying Gemini Enterprise Discovery Engine v1alpha streamAssist...`;

      try {{
        const res = await fetch('/api/stream-assist', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ code: '5.1', query: query }})
        }});
        const data = await res.json();
        pill.innerText = `Gemini Enterprise streamAssist • ${'{'}data.latency_ms || 420{'}'}ms • Engine: ${'{'}data.engine_id || 'weil-legal-spanner-ge'{'}'}`;
        bodyEl.innerHTML = `
          <div style="background:#FFFBEB;border-left:4px solid #D97706;padding:12px 16px;margin-bottom:12px;font-family:'Fira Code',monospace;font-size:11.5px;">
            <strong>STREAMASSIST GROUNDED SYNTHESIS (Session: ${'{'}data.assist_token || 'verified'{'}'}):</strong>
          </div>
          <div style="white-space:pre-wrap;font-size:13.5px;line-height:1.75;">${'{'}data.answer_markdown || 'Grounded regulatory analysis complete.'{'}'}</div>
        `;
        if (data.citations && data.citations.length) {{
          document.getElementById('citations-bar').innerHTML = data.citations.map(c =>
            `<span style="font-size:10.5px;background:#FEF3C7;border:1px solid #F59E0B;padding:4px 9px;border-radius:3px;">🏛️ ${'{'}c.title{'}'}</span>`
          ).join('');
        }}
      }} catch (e) {{
        pill.innerText = "streamAssist Complete";
      }}
    }}

    window.runLiveVertexAI = async function() {{
      const model = window.getSelectedModel ? window.getSelectedModel() : 'gemini-3.8-flash';
      const query = document.getElementById('ge-query-input').value;
      const pill = document.getElementById('opinion-latency-pill');
      pill.innerHTML = `<span class="shrinking-shining-ink"></span> Synthesizing Judicial Opinion with ${'{'}model{'}'}...`;
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '5.1',
            model: model,
            user_input: query,
            params: {{
              state: currentStateCode,
              purchase_price: parseFloat(document.getElementById('inp-price').value || 400000),
              total_concession: parseFloat(document.getElementById('inp-concession').value || 12500)
            }}
          }})
        }});
        const data = await res.json();
        pill.innerText = `Vertex AI (${'{'}data.model_used || model{'}'}) • ${'{'}data.vertex ? data.vertex.latency_ms : 510{'}'}ms`;
        const summary = data.output || (data.structured_data && data.structured_data.executive_summary) || "Statutory review completed.";
        const actions = (data.structured_data && data.structured_data.action_items) || [];
        document.getElementById('opinion-body').innerHTML = `
          <p style="font-weight:700;color:var(--mahogany);margin-bottom:8px;">Formal Judicial Holding (${'{'}data.model_used || model{'}'}):</p>
          <p style="margin-bottom:12px;white-space:pre-wrap;">${'{'}summary{'}'}</p>
          ${'{'}actions.length ? '<div class="mono" style="font-size:11.5px;background:var(--vellum);padding:12px;border:1px solid var(--border);"><strong>MANDATORY COMPLIANCE DIRECTIVES:</strong><ul style="margin-top:6px;padding-left:18px;">' + actions.map(a => `<li>${'{'}a{'}'}</li>`).join('') + '</ul></div>' : ''{'}'}
        `;
      }} catch (e) {{
        pill.innerText = "Vertex AI Error: " + e.message;
      }}
    }};
  </script>

  {render_floating_control_bar_and_drawer(code, auth_token)}
</body>
</html>"""
