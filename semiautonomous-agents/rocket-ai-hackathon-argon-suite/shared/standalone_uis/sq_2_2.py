# -*- coding: utf-8 -*-
"""Square 2.2 Standalone Full-Screen UI:
Low-Code Underwriting Condition Clearing Agent (Google ADK Runtime)
Aesthetic: Chase Bank Statement Ledger & Underwriter Rubber-Stamp Desk (#F8FAFC light ledger, #117ACA Chase Royal Blue header, #D97706 Amber deposit alerts, #059669 Emerald Approval Stamp)."""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_2_2(auth_token: str) -> str:
    floating_bar = render_floating_control_bar_and_drawer("2.2", auth_token)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>2.2 // Low-Code Underwriting Condition Clearing Agent — Chase Ledger &amp; Rubber-Stamp Desk</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=Public+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --ledger-bg: #F8FAFC;
      --card-bg: #FFFFFF;
      --chase-blue: #117ACA;
      --chase-dark: #0A4D82;
      --chase-soft: #E0F2FE;
      --amber: #D97706;
      --amber-bg: #FEF3C7;
      --emerald: #059669;
      --emerald-bg: #D1FAE5;
      --crimson: #DC2626;
      --crimson-bg: #FEE2E2;
      --ink: #0F172A;
      --muted: #475569;
      --border: #CBD5E1;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--ledger-bg);
      color: var(--ink);
      font-family: 'Public Sans', sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }}

    /* Top Chase Bank Institutional Header Bar */
    .chase-header {{
      background: linear-gradient(90deg, var(--chase-dark) 0%, var(--chase-blue) 100%);
      color: #FFFFFF;
      padding: 14px 26px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      flex-wrap: wrap;
      border-bottom: 4px solid #0284C7;
      box-shadow: 0 4px 16px rgba(17, 122, 202, 0.2);
    }}
    .brand-cluster {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}
    .octagon-logo {{
      width: 36px;
      height: 36px;
      background: #FFFFFF;
      color: var(--chase-blue);
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: 'IBM Plex Mono', monospace;
      font-weight: 800;
      font-size: 16px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }}
    .brand-title {{
      font-size: 19px;
      font-weight: 800;
      letter-spacing: -0.01em;
    }}
    .brand-sub {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11px;
      color: #BAE6FD;
    }}
    .header-actions {{
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }}
    .adk-model-pill {{
      background: rgba(255,255,255,0.14);
      border: 1px solid rgba(255,255,255,0.3);
      border-radius: 6px;
      padding: 6px 12px;
      display: flex;
      align-items: center;
      gap: 8px;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11px;
    }}
    .adk-model-pill select {{
      background: transparent;
      color: #FFFFFF;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      border: none;
      outline: none;
      cursor: pointer;
    }}
    .adk-model-pill select option {{
      background: #0F172A;
      color: #FFF;
    }}

    /* Account Summary Ribbon */
    .acct-ribbon {{
      background: #FFFFFF;
      border-bottom: 1px solid var(--border);
      padding: 12px 26px;
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
    }}
    @media (max-width: 960px) {{
      .acct-ribbon {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    .ribbon-metric {{
      border-left: 3px solid var(--chase-blue);
      padding-left: 12px;
    }}
    .ribbon-metric.warn {{ border-left-color: var(--amber); }}
    .ribbon-metric.pass {{ border-left-color: var(--emerald); }}
    .r-lbl {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 10.5px;
      text-transform: uppercase;
      color: var(--muted);
    }}
    .r-val {{
      font-size: 16px;
      font-weight: 800;
      color: var(--ink);
      margin-top: 2px;
      font-family: 'IBM Plex Mono', monospace;
    }}

    /* Main 2-Column Underwriter Workbench */
    .workbench {{
      display: grid;
      grid-template-columns: 1.15fr 0.85fr;
      gap: 20px;
      padding: 20px 26px 84px 26px;
      flex: 1;
    }}
    @media (max-width: 1100px) {{
      .workbench {{ grid-template-columns: 1fr; }}
    }}

    /* Left Column: 60-Day Checking Ledger + Threshold Sliders */
    .ledger-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }}
    .ledger-top {{
      background: #F1F5F9;
      padding: 14px 18px;
      border-bottom: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .ledger-top h2 {{
      font-size: 15px;
      font-weight: 800;
      color: var(--chase-dark);
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .threshold-sliders {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
      padding: 14px 18px;
      background: #F8FAFC;
      border-bottom: 1px solid #E2E8F0;
    }}
    .sl-group {{
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}
    .sl-group label {{
      display: flex;
      justify-content: space-between;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11px;
      font-weight: 600;
      color: var(--muted);
    }}
    .sl-group input[type=range] {{
      accent-color: var(--chase-blue);
      cursor: pointer;
    }}

    table.statement-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}
    table.statement-table th {{
      background: #0F172A;
      color: #F8FAFC;
      text-align: left;
      padding: 10px 14px;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    table.statement-table td {{
      padding: 12px 14px;
      border-bottom: 1px solid #E2E8F0;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 12.5px;
    }}
    tr.ledger-row {{
      cursor: pointer;
      transition: background 0.15s;
    }}
    tr.ledger-row:hover {{
      background: #F1F5F9;
    }}
    tr.ledger-row.flagged {{
      background: #FFFBEB;
      border-left: 4px solid var(--amber);
    }}
    tr.ledger-row.flagged:hover {{
      background: #FEF3C7;
    }}
    tr.ledger-row.selected-row {{
      outline: 2px solid var(--chase-blue);
      background: var(--chase-soft) !important;
    }}
    .badge-flag {{
      display: inline-block;
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 10.5px;
      font-weight: 700;
      background: var(--amber-bg);
      color: #B45309;
      border: 1px solid #F59E0B;
    }}
    .badge-ok {{
      display: inline-block;
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 10.5px;
      font-weight: 700;
      background: var(--emerald-bg);
      color: var(--emerald);
    }}

    .backout-footer {{
      padding: 16px 18px;
      background: #FFFBEB;
      border-top: 2px solid #F59E0B;
      display: flex;
      flex-direction: column;
      gap: 6px;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 12px;
    }}

    /* Right Column: Document Evidence Inspector, Rubber-Stamp Desk & ADK Trace */
    .desk-col {{
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}
    .evidence-card {{
      background: #FFFFFF;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 18px;
      position: relative;
      overflow: hidden;
    }}
    .doc-paper {{
      background: #FCFBF7;
      border: 1px dashed #94A3B8;
      border-radius: 8px;
      padding: 16px;
      margin-top: 10px;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 12px;
      line-height: 1.6;
      color: #1E293B;
      position: relative;
    }}

    /* Physical Rubber Stamp Overlay */
    .rubber-stamp-overlay {{
      position: absolute;
      top: 24px;
      right: 24px;
      padding: 8px 16px;
      border: 4px solid var(--emerald);
      color: var(--emerald);
      font-family: 'IBM Plex Mono', monospace;
      font-size: 15px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      border-radius: 6px;
      transform: rotate(-11deg);
      background: rgba(209, 250, 229, 0.88);
      box-shadow: 0 4px 12px rgba(5, 150, 105, 0.2);
      pointer-events: none;
      transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
    }}
    .rubber-stamp-overlay.stip {{
      border-color: var(--crimson);
      color: var(--crimson);
      background: rgba(254, 226, 226, 0.92);
      transform: rotate(8deg);
    }}

    .stamp-buttons {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      margin-top: 14px;
    }}
    .btn-stamp-clear {{
      background: var(--emerald);
      color: #FFFFFF;
      border: 2px solid #047857;
      padding: 12px 14px;
      border-radius: 8px;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 12px;
      font-weight: 800;
      cursor: pointer;
      box-shadow: 0 4px 0 #065F46;
      transition: transform 0.1s;
    }}
    .btn-stamp-clear:active {{ transform: translateY(2px); box-shadow: 0 2px 0 #065F46; }}
    .btn-stamp-stip {{
      background: #FFFBEB;
      color: #B45309;
      border: 2px solid var(--amber);
      padding: 12px 14px;
      border-radius: 8px;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 12px;
      font-weight: 800;
      cursor: pointer;
      box-shadow: 0 4px 0 #B45309;
      transition: transform 0.1s;
    }}
    .btn-stamp-stip:active {{ transform: translateY(2px); box-shadow: 0 2px 0 #B45309; }}

    .adk-trace-card {{
      background: #0F172A;
      color: #F8FAFC;
      border-radius: 10px;
      padding: 18px;
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 12px;
      font-family: 'IBM Plex Mono', monospace;
    }}
    .adk-trace-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid #334155;
      padding-bottom: 10px;
      font-size: 11.5px;
      color: #38BDF8;
      font-weight: 700;
    }}
    .cel-box {{
      background: #020617;
      border: 1px solid #1E293B;
      border-left: 3px solid #10B981;
      padding: 12px;
      border-radius: 6px;
      font-size: 11.5px;
      color: #A7F3D0;
      line-height: 1.5;
    }}
  </style>
</head>
<body>

  <!-- TOP CHASE BANK STATEMENT LEDGER HEADER -->
  <header class="chase-header">
    <div class="brand-cluster">
      <div class="octagon-logo">JPM</div>
      <div>
        <div class="brand-title">JPMorgan Chase Premier Checking // 60-Day Asset &amp; Large-Deposit Audit Desk</div>
        <div class="brand-sub">Square 2.2 • Google ADK Condition Clearing Agent • Fannie Mae B3-4.2-02 (50% Qualifying Income Rule)</div>
      </div>
    </div>
    <div class="header-actions">
      <div class="adk-model-pill">
        <span>ADK Runtime Model:</span>
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)">
          <option value="gemini-3.8-flash" selected>gemini-3.8-flash (ADK Default)</option>
          <option value="gemini-4-argon">gemini-4-argon (Frontier Global)</option>
        </select>
      </div>
      <button onclick="window.runLiveVertexAI()" style="background:#10B981;color:#052E16;border:none;padding:8px 14px;border-radius:6px;font-family:'IBM Plex Mono',monospace;font-size:11.5px;font-weight:800;cursor:pointer;">
        ⚡ Run ADK Condition Agent
      </button>
    </div>
  </header>

  <!-- 4-METRIC ACCOUNT & FANNIE MAE THRESHOLD RIBBON -->
  <section class="acct-ribbon">
    <div class="ribbon-metric">
      <div class="r-lbl">Account Holder &amp; Cash Needed</div>
      <div class="r-val" id="rib-needed">Acct #8841 • $44,000 Req.</div>
    </div>
    <div class="ribbon-metric warn">
      <div class="r-lbl">Fannie Mae B3-4.2-02 50% Threshold</div>
      <div class="r-val" id="rib-thresh">$5,700.00 (50% of $11,400/mo)</div>
    </div>
    <div class="ribbon-metric warn">
      <div class="r-lbl">Flagged Unsourced Deposits</div>
      <div class="r-val" id="rib-flagged" style="color:var(--amber);">2 Flagged ($25,700.00 Total)</div>
    </div>
    <div class="ribbon-metric pass">
      <div class="r-lbl">Asset Back-Out Sufficiency Test</div>
      <div class="r-val" id="rib-backout" style="color:var(--crimson);">$25,500 Verified (&lt; $44k!)</div>
    </div>
  </section>

  <!-- MAIN 2-COLUMN WORKBENCH -->
  <main class="workbench">
    <!-- LEFT: INTERACTIVE 60-DAY CHECKING LEDGER TABLE -->
    <section class="ledger-card">
      <div class="ledger-top">
        <h2>📄 JPMorgan Chase Statement (Aug 14, 2026 – Oct 13, 2026) — Click Any Row to Inspect</h2>
        <span style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--chase-blue);font-weight:700;">Plaid + Document AI Verified</span>
      </div>

      <div class="threshold-sliders">
        <div class="sl-group">
          <label>
            <span>Form 1003 Qualifying Monthly Income</span>
            <strong id="lbl-inc" style="color:var(--chase-blue);">$11,400/mo</strong>
          </label>
          <input type="range" id="sl-inc" min="6000" max="26000" step="500" value="11400" oninput="window.auditDepositsSandbox()" />
        </div>
        <div class="sl-group">
          <label>
            <span>Statement Ending Balance</span>
            <strong id="lbl-bal" style="color:var(--chase-blue);">$51,200.00</strong>
          </label>
          <input type="range" id="sl-bal" min="32000" max="90000" step="1000" value="51200" oninput="window.auditDepositsSandbox()" />
        </div>
      </div>

      <table class="statement-table">
        <thead>
          <tr>
            <th>Post Date</th>
            <th>Transaction Description</th>
            <th>Credit Amount</th>
            <th>vs. 50% Rule</th>
            <th>ADK Disposition</th>
          </tr>
        </thead>
        <tbody>
          <tr class="ledger-row" id="row-payroll-1" onclick="window.inspectRow('payroll1')">
            <td>09/15/2026</td>
            <td>ACH CREDIT: STELLANTIS NV PAYROLL DIR DEP</td>
            <td>+$4,150.00</td>
            <td>Exempt Payroll</td>
            <td><span class="badge-ok">AUTO-VERIFIED</span></td>
          </tr>
          <tr class="ledger-row flagged selected-row" id="row-coinbase" onclick="window.inspectRow('coinbase')">
            <td>09/22/2026</td>
            <td>FEDWIRE CREDIT: COINBASE INC SAN FRANCISCO CA</td>
            <td style="font-weight:800;color:var(--amber);">+$18,500.00</td>
            <td>&gt; $5,700 Cap!</td>
            <td><span class="badge-flag" id="status-coinbase">⚠ PTDF STIP #402A</span></td>
          </tr>
          <tr class="ledger-row" id="row-payroll-2" onclick="window.inspectRow('payroll2')">
            <td>09/30/2026</td>
            <td>ACH CREDIT: STELLANTIS NV PAYROLL DIR DEP</td>
            <td>+$4,150.00</td>
            <td>Exempt Payroll</td>
            <td><span class="badge-ok">AUTO-VERIFIED</span></td>
          </tr>
          <tr class="ledger-row flagged" id="row-check1042" onclick="window.inspectRow('check1042')">
            <td>10/04/2026</td>
            <td>MOBILE CHECK DEPOSIT #1042 (HANDWRITTEN MEMO: GIFT)</td>
            <td style="font-weight:800;color:var(--amber);">+$7,200.00</td>
            <td>&gt; $5,700 Cap!</td>
            <td><span class="badge-flag" id="status-check1042">⚠ GIFT LETTER MATCHED</span></td>
          </tr>
          <tr class="ledger-row" id="row-tax" onclick="window.inspectRow('ustreas')">
            <td>10/09/2026</td>
            <td>ACH CREDIT: IRS USATAXPYMT TAX REFUND</td>
            <td>+$1,840.00</td>
            <td>&lt; 50% Cap</td>
            <td><span class="badge-ok">AUTO-VERIFIED</span></td>
          </tr>
        </tbody>
      </table>

      <div class="backout-footer" id="backout-math-box">
        <div><strong>ASSET BACK-OUT TEST (Fannie Mae B3-4.2-02):</strong> Ending Balance ($51,200.00) − Unsourced Large Deposits ($25,700.00) = <strong>$25,500.00 Verified Liquid Funds</strong>.</div>
        <div style="color:#B45309;">Because $25,500.00 is less than the $44,000.00 Cash-to-Close requirement, Underwriter CANNOT back out the deposits — Condition #402 documentation is mandatory.</div>
      </div>
    </section>

    <!-- RIGHT: SUPPORTING DOCUMENT INSPECTOR, PHYSICAL RUBBER STAMPS & ADK TRACE -->
    <section class="desk-col">
      <div class="evidence-card">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <h3 style="font-size:15px;font-weight:800;color:var(--chase-dark);" id="doc-viewer-title">
            🔍 Selected Deposit Packet: $18,500.00 Coinbase Wire (09/22/2026)
          </h3>
          <span style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--muted);">Condition #402</span>
        </div>

        <div class="rubber-stamp-overlay stip" id="stamp-visual">PTDF STIPULATION #402</div>

        <div class="doc-paper" id="doc-viewer-body">
          <strong>DOCUMENT PACKET #402-A // CRYPTO LIQUIDATION &amp; PAPER TRAIL</strong><br/>
          • Source Institution: Coinbase Custody / Coinbase Retail Exchange<br/>
          • Wire Reference: FW-20260922-99281742 ($18,500.00 USD)<br/>
          • Fannie Mae B3-4.2-02 Requirement: Virtual currency may only be used for down payment if liquidated into U.S. dollars in a verified U.S. depository institution AND supported by a 60-day exchange account statement showing borrower ownership prior to sale.<br/>
          • <strong>Current Packet Status:</strong> Wire receipt present; 60-day Coinbase BTC/ETH holding statement missing.
        </div>

        <div class="stamp-buttons">
          <button class="btn-stamp-clear" onclick="window.applyRubberStamp('CLEAR')">
            [✓ STAMP: CLEAR CONDITION #402]
          </button>
          <button class="btn-stamp-stip" onclick="window.applyRubberStamp('STIP')">
            [⚠ ISSUE PTDF STIPULATION]
          </button>
        </div>
      </div>

      <!-- ADK Agent Trace Log & CEL Blocking Gate -->
      <div class="adk-trace-card">
        <div class="adk-trace-header">
          <span>🤖 GOOGLE ADK CONDITION CLEARING AGENT TRACE</span>
          <span id="live-model-pill">gemini-3.8-flash</span>
        </div>
        <div class="cel-box" id="adk-cel-output">
          [CEL POLICY GATE]: stage == "CLEAR_TO_CLOSE" &amp;&amp; unverified_large_deposits &gt; 0 &amp;&amp; (ending_balance - unverified_large_deposits) &lt; cash_to_close_required ==&gt; BLOCK_CTC("PTDF Condition #402")
        </div>
        <div id="adk-narrative-log" style="font-size:12px;line-height:1.6;color:#CBD5E1;">
          • <strong>Step 1 (Plaid + DocAI Ledger Scan):</strong> Scanned 42 transactions across 60-day Chase statement. Computed 50% threshold = $5,700.00.<br/>
          • <strong>Step 2 ( Gift &amp; Wire Cross-Match):</strong> Matched 10/04 Check #1042 ($7,200) to signed FHA/Fannie Gift Letter from donor Evelyn Vance. Flagged 09/22 Coinbase wire ($18,500) for missing 60-day exchange statement.<br/>
          • <strong>Step 3 (HITL Underwriter Action):</strong> Ready for one-click rubber-stamp clearance or borrower push-notification stipulation.
        </div>
      </div>
    </section>
  </main>

  <script>
    let currentRowKey = 'coinbase';

    const ROW_DOCS = {{
      coinbase: {{
        title: "🔍 Selected Deposit Packet: $18,500.00 Coinbase Wire (09/22/2026)",
        stampText: "PTDF STIPULATION #402",
        stampClass: "rubber-stamp-overlay stip",
        body: `<strong>DOCUMENT PACKET #402-A // CRYPTO LIQUIDATION &amp; PAPER TRAIL</strong><br/>
          • Source Institution: Coinbase Retail Exchange (San Francisco, CA)<br/>
          • Wire Reference: FW-20260922-99281742 ($18,500.00 USD)<br/>
          • Fannie Mae B3-4.2-02 Rule: Crypto assets liquidated into USD require a 60-day exchange statement proving the borrower owned the digital assets prior to liquidation.<br/>
          • <strong>ADK Audit Verdict:</strong> Wire credit verified on Chase statement; require 60-day Coinbase PDF statement or click Stamp Clear if uploaded.`
      }},
      check1042: {{
        title: "🔍 Selected Deposit Packet: $7,200.00 Check #1042 — Gift Letter (10/04/2026)",
        stampText: "CLEARED // B3-4.3-04",
        stampClass: "rubber-stamp-overlay",
        body: `<strong>DOCUMENT PACKET #402-B // EXECUTED GIFT LETTER &amp; CHECK IMAGE</strong><br/>
          • Donor Name: Evelyn Vance (Relationship: Mother — Eligible Family Donor per B3-4.3-04)<br/>
          • Check #1042 Amount: $7,200.00 (Drawn on Huntington National Bank Acct #4419)<br/>
          • No-Repayment Clause: Explicitly states "No repayment expected or implied."<br/>
          • <strong>ADK Audit Verdict:</strong> 100% of Fannie Mae B3-4.3-04 Gift Funds fields verified. Ready for Underwriter Rubber Stamp.`
      }},
      payroll1: {{
        title: "🔍 Selected Deposit Packet: $4,150.00 Stellantis NV Direct Deposit",
        stampText: "EXEMPT PAYROLL",
        stampClass: "rubber-stamp-overlay",
        body: `<strong>ACH PAYROLL DIRECT DEPOSIT // STELLANTIS NV (FCA US LLC)</strong><br/>
          • Bi-Weekly Net Pay: $4,150.00 (Matches ADP Paystub &amp; Form 1003 Employment)<br/>
          • <strong>ADK Audit Verdict:</strong> Regular payroll direct deposits are exempt from the Fannie Mae B3-4.2-02 large-deposit sourcing requirement.`
      }},
      payroll2: {{
        title: "🔍 Selected Deposit Packet: $4,150.00 Stellantis NV Direct Deposit (09/30/2026)",
        stampText: "EXEMPT PAYROLL",
        stampClass: "rubber-stamp-overlay",
        body: `<strong>ACH PAYROLL DIRECT DEPOSIT // STELLANTIS NV (FCA US LLC)</strong><br/>
          • Bi-Weekly Net Pay: $4,150.00 (Matches ADP Paystub &amp; Form 1003 Employment)<br/>
          • <strong>ADK Audit Verdict:</strong> Automatically cleared.`
      }},
      ustreas: {{
        title: "🔍 Selected Deposit Packet: $1,840.00 US Treasury IRS Tax Refund",
        stampText: "BELOW 50% THRESHOLD",
        stampClass: "rubber-stamp-overlay",
        body: `<strong>ACH CREDIT // IRS USATAXPYMT FEDERAL REFUND</strong><br/>
          • Deposit Amount: $1,840.00 (Below 50% Qualifying Income Threshold of $5,700.00)<br/>
          • <strong>ADK Audit Verdict:</strong> Exempt under Fannie Mae B3-4.2-02.`
      }}
    }};

    window.inspectRow = function(key) {{
      currentRowKey = key;
      document.querySelectorAll('.ledger-row').forEach(r => r.classList.remove('selected-row'));
      const mapId = {{
        coinbase: 'row-coinbase',
        check1042: 'row-check1042',
        payroll1: 'row-payroll-1',
        payroll2: 'row-payroll-2',
        ustreas: 'row-tax'
      }}[key];
      if (mapId && document.getElementById(mapId)) {{
        document.getElementById(mapId).classList.add('selected-row');
      }}
      const info = ROW_DOCS[key] || ROW_DOCS.coinbase;
      document.getElementById('doc-viewer-title').innerText = info.title;
      document.getElementById('doc-viewer-body').innerHTML = info.body;
      const st = document.getElementById('stamp-visual');
      st.className = info.stampClass;
      st.innerText = info.stampText;
    }};

    window.applyRubberStamp = function(mode) {{
      const st = document.getElementById('stamp-visual');
      if (mode === 'CLEAR') {{
        st.className = 'rubber-stamp-overlay';
        st.innerText = '✓ CLEARED BY UNDERWRITER #402';
        if (currentRowKey === 'coinbase') {{
          const b = document.getElementById('status-coinbase');
          b.className = 'badge-ok';
          b.innerText = '✓ STAMPED CLEAR';
        }} else if (currentRowKey === 'check1042') {{
          const b = document.getElementById('status-check1042');
          b.className = 'badge-ok';
          b.innerText = '✓ STAMPED CLEAR';
        }}
        document.getElementById('adk-cel-output').innerText =
          '[CEL POLICY GATE]: Condition #402 CLEARED via Underwriter Digital Stamp • Loan #RKT-2026-8841 Advanced to CLEAR_TO_CLOSE!';
      }} else {{
        st.className = 'rubber-stamp-overlay stip';
        st.innerText = '⚠ PTDF STIPULATION ISSUED';
        document.getElementById('adk-cel-output').innerText =
          '[CEL POLICY GATE]: PTDF Stipulation #402 Dispatched to Borrower Rocket Portal -> Provide 60-day Coinbase statement + signed LOE.';
      }}
    }};

    window.auditDepositsSandbox = async function() {{
      const inc = parseFloat(document.getElementById('sl-inc').value || 11400);
      const bal = parseFloat(document.getElementById('sl-bal').value || 51200);
      document.getElementById('lbl-inc').innerText = '$' + inc.toLocaleString() + '/mo';
      document.getElementById('lbl-bal').innerText = '$' + bal.toLocaleString() + '.00';

      try {{
        const res = await fetch('/api/sandbox', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '2.2',
            action: 'audit_large_deposits',
            params: {{ qualifying_monthly_income: inc, ending_balance: bal, funds_needed: 44000 }}
          }})
        }});
        const data = await res.json();
        if (data.ok && data.metrics) {{
          document.getElementById('rib-thresh').innerText = data.metrics.fannie_b3_4_2_02_threshold || '';
          document.getElementById('rib-backout').innerText = (data.metrics.asset_back_out_test || '').split('=')[1] || data.metrics.asset_back_out_test;
          document.getElementById('backout-math-box').innerHTML = `
            <div><strong>ASSET BACK-OUT TEST:</strong> ${{data.metrics.asset_back_out_test}}</div>
            <div style="color:#B45309;"><strong>Auto-Staged Condition:</strong> ${{data.metrics.auto_staged_condition}}</div>
          `;
        }}
      }} catch (e) {{
        console.error(e);
      }}
    }};

    window.runLiveVertexAI = async function() {{
      const model = window.getSelectedModel ? window.getSelectedModel() : 'gemini-3.8-flash';
      const inc = parseFloat(document.getElementById('sl-inc').value || 11400);
      const bal = parseFloat(document.getElementById('sl-bal').value || 51200);
      const logEl = document.getElementById('adk-narrative-log');
      logEl.innerHTML = `<span style="color:#38BDF8;">Executing Google ADK Condition Clearing Agent on ${{model}}...</span>`;

      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '2.2',
            model: model,
            params: {{ qualifying_monthly_income: inc, ending_balance: bal, funds_needed: 44000 }}
          }})
        }});
        const data = await res.json();
        const sd = data.structured_data || {{}};
        if (sd.cel_blocking_gate_payload) {{
          document.getElementById('adk-cel-output').innerText =
            `[CEL GATE • ${{sd.cel_blocking_gate_payload.stage || 'UNDERWRITING'}}]: ${{sd.cel_blocking_gate_payload.condition_text || data.output}}`;
        }}
        logEl.innerHTML = `<strong>[${{data.model_used || model}} ADK Synthesis]:</strong><br/>` + (data.output || 'Condition #402 audited.');
      }} catch (e) {{
        logEl.innerText = 'ADK execution complete.';
      }}
    }};
  </script>

  {floating_bar}
</body>
</html>"""
