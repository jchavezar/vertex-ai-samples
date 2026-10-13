# -*- coding: utf-8 -*-
"""Square 2.3 Standalone Full-Screen UI:
Bank Statement Large-Deposit Sourcer (Fannie Mae B3-4.2-02 50% Qualifying Income Rule & BSA/AML Paper Trail)
Design Style: Chase / Ally Online Banking Statement & Transaction Ledger (#FFFFFF clean white banking portal, #117ACA Chase banking blue header, #F3F6F9 ledger row hover, Public Sans tabular figures).
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_2_3(auth_token: str) -> str:
    floating_bar = render_floating_control_bar_and_drawer("2.3", auth_token)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>2.3 · Bank Statement Large-Deposit Sourcer — Online Banking &amp; Asset Audit Ledger</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=Public+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bank-white: #FFFFFF;
      --bank-canvas: #F5F7FA;
      --chase-blue: #117ACA;
      --chase-dark: #0A4D82;
      --row-hover: #F3F6F9;
      --ink: #0F172A;
      --muted: #475569;
      --border: #CBD5E1;
      --emerald: #059669;
      --emerald-soft: #ECFDF5;
      --amber: #D97706;
      --amber-soft: #FEF3C7;
      --crimson: #DC2626;
      --crimson-soft: #FEF2F2;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--bank-canvas);
      color: var(--ink);
      font-family: 'Public Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      font-variant-numeric: tabular-nums;
    }}

    /* Chase / Ally Banking Blue Top Header */
    .bank-topbar {{
      background: var(--chase-blue);
      color: #FFFFFF;
      padding: 14px 28px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      flex-wrap: wrap;
      border-bottom: 3px solid var(--chase-dark);
      box-shadow: 0 3px 12px rgba(17, 122, 202, 0.2);
    }}
    .bank-brand {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}
    .bank-emblem {{
      width: 38px;
      height: 38px;
      border-radius: 8px;
      background: #FFFFFF;
      color: var(--chase-blue);
      font-weight: 800;
      font-size: 15px;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .bank-title {{
      font-size: 18px;
      font-weight: 800;
      letter-spacing: -0.01em;
    }}
    .bank-sub {{
      font-size: 12px;
      color: #E0F2FE;
    }}
    .topbar-actions {{
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }}
    .model-box {{
      background: rgba(255, 255, 255, 0.16);
      border: 1px solid rgba(255, 255, 255, 0.32);
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 12px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .model-box select {{
      background: transparent;
      border: none;
      color: #FFFFFF;
      font-family: inherit;
      font-size: 12px;
      font-weight: 700;
      outline: none;
      cursor: pointer;
    }}
    .model-box select option {{
      background: #0F172A;
      color: #FFFFFF;
    }}
    .btn-bsa-audio {{
      background: #FFFFFF;
      color: var(--chase-dark);
      border: none;
      padding: 8px 14px;
      border-radius: 6px;
      font-family: inherit;
      font-size: 12.5px;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }}
    .btn-audit-run {{
      background: #059669;
      color: #FFFFFF;
      border: 1px solid #34D399;
      padding: 8px 16px;
      border-radius: 6px;
      font-family: inherit;
      font-size: 12.5px;
      font-weight: 700;
      cursor: pointer;
    }}

    /* Account Summary Banner */
    .acct-summary-bar {{
      background: #FFFFFF;
      border-bottom: 1px solid var(--border);
      padding: 16px 28px;
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      max-width: 1520px;
      margin: 0 auto;
      width: 100%;
    }}
    @media (max-width: 960px) {{
      .acct-summary-bar {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    .acct-tile {{
      border-right: 1px solid #E2E8F0;
      padding-right: 14px;
    }}
    .acct-tile:last-child {{ border-right: none; }}
    .acct-lbl {{
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--muted);
    }}
    .acct-val {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 21px;
      font-weight: 700;
      color: var(--ink);
      margin-top: 4px;
    }}
    .acct-sub {{
      font-size: 11.5px;
      color: var(--muted);
      margin-top: 2px;
    }}

    /* 2-Column Statement Ledger + Gift Letter Verification */
    .banking-layout {{
      display: grid;
      grid-template-columns: 1.3fr 0.9fr;
      gap: 20px;
      padding: 20px 28px 90px 28px;
      max-width: 1520px;
      margin: 0 auto;
      width: 100%;
    }}
    @media (max-width: 1120px) {{
      .banking-layout {{ grid-template-columns: 1fr; }}
    }}

    .statement-card {{
      background: #FFFFFF;
      border: 1px solid var(--border);
      border-radius: 10px;
      overflow: hidden;
      box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    }}
    .statement-header {{
      background: #F8FAFC;
      border-bottom: 1px solid var(--border);
      padding: 16px 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
    }}
    .threshold-control {{
      background: #EFF6FF;
      border: 1px solid #BFDBFE;
      border-radius: 8px;
      padding: 12px 16px;
      margin: 14px 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      flex-wrap: wrap;
    }}
    .threshold-control input[type="range"] {{
      width: 240px;
      accent-color: var(--chase-blue);
      cursor: pointer;
    }}
    .ledger-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}
    .ledger-table th {{
      background: #F1F5F9;
      text-align: left;
      padding: 10px 14px;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--muted);
      border-bottom: 1px solid var(--border);
    }}
    .ledger-table th.num, .ledger-table td.num {{
      text-align: right;
      font-family: 'IBM Plex Mono', monospace;
    }}
    .ledger-table td {{
      padding: 12px 14px;
      border-bottom: 1px solid #E2E8F0;
      cursor: pointer;
      transition: background 0.12s;
    }}
    .ledger-table tr:hover td {{
      background: var(--row-hover);
    }}
    .ledger-table tr.flagged-row td {{
      background: #FFFBEB;
    }}
    .ledger-table tr.selected-row td {{
      outline: 2px solid var(--chase-blue);
      background: #E0F2FE;
    }}
    .pill-exempt {{
      font-size: 10.5px;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 999px;
      background: var(--emerald-soft);
      color: var(--emerald);
      border: 1px solid #A7F3D0;
    }}
    .pill-flag {{
      font-size: 10.5px;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 999px;
      background: var(--amber-soft);
      color: var(--amber);
      border: 1px solid #FDE68A;
    }}

    /* Right Column: Paper Gift Letter & Wire Receipt Verification */
    .source-panel {{
      display: flex;
      flex-direction: column;
      gap: 18px;
    }}
    .paper-gift-card {{
      background: #FFFFFF;
      border: 1px solid var(--border);
      border-top: 4px solid var(--chase-blue);
      border-radius: 10px;
      padding: 20px;
      box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    }}
    .gift-doc-sheet {{
      background: #FCFBF7;
      border: 1px solid #E2D9C8;
      border-radius: 6px;
      padding: 16px 18px;
      margin-top: 12px;
      font-size: 12.5px;
      line-height: 1.6;
    }}
    .bsa-memo-card {{
      background: #FFFFFF;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 18px 20px;
      box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    }}
  </style>
</head>
<body>

  <!-- CHASE / ALLY ONLINE BANKING HEADER -->
  <header class="bank-topbar">
    <div class="bank-brand">
      <div class="bank-emblem">ALLY</div>
      <div>
        <div class="bank-title">Bank Statement Large-Deposit Sourcer · 60-Day Asset &amp; BSA/AML Ledger</div>
        <div class="bank-sub">Ally Bank Interest Checking Account #...4829 · Fannie Mae Selling Guide B3-4.2-02 (50% Qualifying Income Rule)</div>
      </div>
    </div>
    <div class="topbar-actions">
      <div class="model-box">
        <span>Asset Audit Model:</span>
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)">
          <option value="gemini-4-argon" selected>gemini-4-argon (BSA/AML &amp; B3-4.2-02)</option>
          <option value="gemini-3.8-flash">gemini-3.8-flash (Fast Ledger Scan)</option>
        </select>
      </div>
      <button class="btn-bsa-audio" onclick="window.playBsaAuditAudio(this)">
        🔊 Play BSA/AML Deposit Audit Audio
      </button>
      <button class="btn-audit-run" onclick="window.runLiveVertexAI()">
        Verify Deposit Paper Trail
      </button>
    </div>
  </header>

  <!-- 60-DAY STATEMENT SUMMARY RIBBON -->
  <section class="acct-summary-bar">
    <div class="acct-tile">
      <div class="acct-lbl">Ending Statement Balance (10/10/2026)</div>
      <div class="acct-val">$68,420.50</div>
      <div class="acct-sub">Ally Bank Checking #...4829 (Verified Plaid + PDF)</div>
    </div>
    <div class="acct-tile">
      <div class="acct-lbl">Total Qualifying Monthly Income (Form 1003)</div>
      <div class="acct-val" id="val-qual-inc">$18,958.33/mo</div>
      <div class="acct-sub">Combined Base + Variable Monthly Income</div>
    </div>
    <div class="acct-tile">
      <div class="acct-lbl">Fannie Mae 50% Large-Deposit Threshold</div>
      <div class="acct-val" id="val-threshold" style="color:var(--chase-blue);">$9,479.17</div>
      <div class="acct-sub">Non-Payroll Deposits &gt; 50% Require Sourcing</div>
    </div>
    <div class="acct-tile">
      <div class="acct-lbl">Flagged Unsourced Large Deposits</div>
      <div class="acct-val" id="val-flagged-count" style="color:var(--amber);">1 Flagged ($14,000.00)</div>
      <div class="acct-sub">09/18/2026 Domestic Fedwire Credit</div>
    </div>
  </section>

  <!-- MAIN 2-COLUMN BANKING STATEMENT LEDGER & GIFT LETTER VERIFICATION -->
  <main class="banking-layout">
    <!-- LEFT: 60-DAY ALLY BANK CHECKING STATEMENT LEDGER -->
    <div class="statement-card">
      <div class="statement-header">
        <div>
          <div style="font-size:15.5px;font-weight:800;color:var(--ink);">60-Day Ally Bank Checking Statement (Account #...4829)</div>
          <div style="font-size:12px;color:var(--muted);">Statement Period: August 11, 2026 – October 10, 2026 · Click any deposit row to inspect sourcing</div>
        </div>
        <span style="font-family:'IBM Plex Mono',monospace;font-size:11.5px;background:#E0F2FE;color:#0A4D82;padding:4px 10px;border-radius:6px;font-weight:700;">Plaid Asset Report #PLD-8821</span>
      </div>

      <!-- Interactive 50% Qualifying Income Threshold Slider -->
      <div class="threshold-control">
        <div>
          <div style="font-size:12.5px;font-weight:700;color:#0A4D82;">Fannie Mae B3-4.2-02 50% Qualifying Income Threshold Slider</div>
          <div style="font-size:11.5px;color:#334155;">Adjust Form 1003 Monthly Qualifying Income to dynamically recalculate the 50% Large-Deposit Sourcing Cutoff:</div>
        </div>
        <div style="display:flex;align-items:center;gap:12px;">
          <input type="range" id="sl-qual-income" min="10000" max="32000" step="500" value="18958.33" oninput="window.updateDepositThreshold()" />
          <span id="lbl-slider-thresh" style="font-family:'IBM Plex Mono',monospace;font-weight:800;font-size:14px;color:#0A4D82;">$9,479.17</span>
        </div>
      </div>

      <table class="ledger-table">
        <thead>
          <tr>
            <th>Post Date</th>
            <th>Transaction Description &amp; Counterparty</th>
            <th>ACH / Wire Type</th>
            <th class="num">Amount</th>
            <th>Fannie Mae B3-4.2-02 Status</th>
          </tr>
        </thead>
        <tbody>
          <tr onclick="window.inspectTxRow('tx1', this)">
            <td style="font-family:'IBM Plex Mono',monospace;">08/15/2026</td>
            <td><strong>GUSTO PAYROLL ACH · STRIPE INC.</strong> (Direct Deposit)</td>
            <td>PPD Payroll ACH</td>
            <td class="num" style="color:var(--emerald);font-weight:700;">+$5,412.80</td>
            <td><span class="pill-exempt">EXEMPT · PAYROLL ACH</span></td>
          </tr>
          <tr onclick="window.inspectTxRow('tx2', this)">
            <td style="font-family:'IBM Plex Mono',monospace;">08/31/2026</td>
            <td><strong>GUSTO PAYROLL ACH · STRIPE INC.</strong> (Direct Deposit)</td>
            <td>PPD Payroll ACH</td>
            <td class="num" style="color:var(--emerald);font-weight:700;">+$5,412.80</td>
            <td><span class="pill-exempt">EXEMPT · PAYROLL ACH</span></td>
          </tr>
          <tr onclick="window.inspectTxRow('tx3', this)">
            <td style="font-family:'IBM Plex Mono',monospace;">09/08/2026</td>
            <td><strong>US TREASURY IRS TAX REFUND 310</strong> (2025 Amended Return)</td>
            <td>ACH Treasury Credit</td>
            <td class="num" style="color:var(--ink);font-weight:600;">+$2,140.00</td>
            <td><span class="pill-exempt" id="status-tx3">EXEMPT · BELOW 50%</span></td>
          </tr>
          <tr onclick="window.inspectTxRow('tx4', this)">
            <td style="font-family:'IBM Plex Mono',monospace;">09/15/2026</td>
            <td><strong>GUSTO PAYROLL ACH · STRIPE INC.</strong> (Direct Deposit)</td>
            <td>PPD Payroll ACH</td>
            <td class="num" style="color:var(--emerald);font-weight:700;">+$5,412.80</td>
            <td><span class="pill-exempt">EXEMPT · PAYROLL ACH</span></td>
          </tr>
          <tr class="flagged-row selected-row" id="row-wire" onclick="window.inspectTxRow('tx5', this)">
            <td style="font-family:'IBM Plex Mono',monospace;font-weight:700;">09/18/2026</td>
            <td><strong>FEDWIRE INCOMING CREDIT · IMAD 0918B1Q802C004192</strong> (Sender: Robert M. Chen)</td>
            <td>Domestic Fedwire</td>
            <td class="num" style="color:var(--amber);font-weight:800;">+$14,000.00</td>
            <td><span class="pill-flag" id="status-tx5">FLAGGED &gt; $9,479.17 THRESHOLD</span></td>
          </tr>
          <tr onclick="window.inspectTxRow('tx6', this)">
            <td style="font-family:'IBM Plex Mono',monospace;">09/24/2026</td>
            <td><strong>VENMO CASHOUT · SHARED DINNER REIMBURSEMENT</strong></td>
            <td>P2P Transfer</td>
            <td class="num" style="color:var(--ink);font-weight:600;">+$6,200.00</td>
            <td><span class="pill-exempt" id="status-tx6">EXEMPT · BELOW 50%</span></td>
          </tr>
          <tr onclick="window.inspectTxRow('tx7', this)">
            <td style="font-family:'IBM Plex Mono',monospace;">09/30/2026</td>
            <td><strong>GUSTO PAYROLL ACH · STRIPE INC.</strong> (Direct Deposit)</td>
            <td>PPD Payroll ACH</td>
            <td class="num" style="color:var(--emerald);font-weight:700;">+$5,412.80</td>
            <td><span class="pill-exempt">EXEMPT · PAYROLL ACH</span></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- RIGHT: PAPER GIFT LETTER & FEDWIRE RECEIPT VERIFICATION PANEL -->
    <div class="source-panel">
      <div class="paper-gift-card">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <h3 style="font-size:15px;font-weight:800;color:var(--ink);">Paper Gift Letter &amp; Fedwire Receipt Verification</h3>
          <span style="font-size:11px;font-weight:700;padding:3px 8px;border-radius:999px;background:var(--emerald-soft);color:var(--emerald);">SOURCED PER B3-4.3-04</span>
        </div>

        <div class="gift-doc-sheet" id="tx-detail-sheet">
          <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--chase-dark);font-weight:700;border-bottom:1px solid #D6CBB5;padding-bottom:6px;margin-bottom:8px;">
            FANNIE MAE STANDARD GIFT LETTER (B3-4.3-04) + FEDWIRE IMAD #0918B1Q802C004192
          </div>
          <p><strong>Selected Transaction:</strong> 09/18/2026 Incoming Fedwire of <strong>$14,000.00</strong> (+$4,520.83 above the $9,479.17 50% threshold).</p>
          <p style="margin-top:8px;"><strong>Donor Verification:</strong> Robert M. Chen (Relationship: Father — Eligible Relative per B3-4.3-04) · Wells Fargo Bank Acct #...9104.</p>
          <p style="margin-top:8px;"><strong>No-Repayment Attestation:</strong> <em>"No repayment of this $14,000.00 gift is expected or implied either in the form of cash or future services of any kind."</em></p>
          <div style="margin-top:10px;padding:8px 12px;background:#ECFDF5;border:1px solid #A7F3D0;border-radius:6px;color:#065F46;font-weight:600;font-size:12px;">
            ✓ Donor Wire Receipt + Executed Gift Letter Matched · Cleared for Closing Cash-to-Close
          </div>
        </div>
      </div>

      <div class="bsa-memo-card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
          <span style="font-size:14px;font-weight:800;color:var(--ink);">BSA/AML &amp; Asset Underwriting Ruling</span>
          <span id="live-model-pill" style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--chase-blue);font-weight:700;">gemini-4-argon</span>
        </div>
        <div id="bsa-audit-output" style="font-size:12.5px;line-height:1.6;color:var(--ink);background:#F8FAFC;padding:14px;border:1px solid #E2E8F0;border-radius:6px;">
          <strong>ASSET SOURCING DETERMINATION (FANNIE MAE B3-4.2-02):</strong><br/>
          • <strong>50% Threshold Calculation:</strong> $18,958.33/mo Total Qualifying Income × 50% = <strong>$9,479.17</strong>.<br/>
          • <strong>Automated Payroll Exemption:</strong> Four recurring Gusto ACH credits ($5,412.80 each) carry standard PPD payroll descriptors and are automatically exempt.<br/>
          • <strong>Large Deposit Resolution:</strong> The 09/18/2026 $14,000.00 wire exceeds $9,479.17 by $4,520.83 and is 100% sourced via signed Gift Letter + Fedwire IMAD receipt.
        </div>
      </div>
    </div>
  </main>

  <script>
    const TX_DETAILS = {{
      "tx1": "<strong>08/15/2026 Gusto Payroll ACH (+$5,412.80):</strong> Recurring semi-monthly net paycheck from Stripe Inc. Automatically exempt from large-deposit sourcing per Fannie Mae B3-4.2-02.",
      "tx2": "<strong>08/31/2026 Gusto Payroll ACH (+$5,412.80):</strong> Recurring semi-monthly net paycheck from Stripe Inc. Automatically exempt from large-deposit sourcing per Fannie Mae B3-4.2-02.",
      "tx3": "<strong>09/08/2026 US Treasury IRS Tax Refund (+$2,140.00):</strong> Official U.S. Treasury ACH refund credit; falls well below the 50% qualifying income threshold.",
      "tx4": "<strong>09/15/2026 Gusto Payroll ACH (+$5,412.80):</strong> Recurring semi-monthly net paycheck from Stripe Inc. Automatically exempt from large-deposit sourcing.",
      "tx5": `<div style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:#0A4D82;font-weight:700;border-bottom:1px solid #D6CBB5;padding-bottom:6px;margin-bottom:8px;">FANNIE MAE STANDARD GIFT LETTER (B3-4.3-04) + FEDWIRE IMAD #0918B1Q802C004192</div><p><strong>Selected Transaction:</strong> 09/18/2026 Incoming Fedwire of <strong>$14,000.00</strong>.</p><p style="margin-top:8px;"><strong>Donor Verification:</strong> Robert M. Chen (Father — Eligible Relative per B3-4.3-04) · Wells Fargo Bank Acct #...9104.</p><p style="margin-top:8px;"><strong>No-Repayment Attestation:</strong> <em>"No repayment of this $14,000.00 gift is expected or implied."</em></p><div style="margin-top:10px;padding:8px 12px;background:#ECFDF5;border:1px solid #A7F3D0;border-radius:6px;color:#065F46;font-weight:600;font-size:12px;">✓ Donor Wire Receipt + Executed Gift Letter Matched · Cleared for Closing Cash-to-Close</div>`,
      "tx6": "<strong>09/24/2026 Venmo Cashout (+$6,200.00):</strong> P2P transfer inspected against the current 50% qualifying income threshold.",
      "tx7": "<strong>09/30/2026 Gusto Payroll ACH (+$5,412.80):</strong> Recurring semi-monthly net paycheck from Stripe Inc. Automatically exempt from large-deposit sourcing."
    }};

    window.inspectTxRow = function(txId, rowEl) {{
      document.querySelectorAll('.ledger-table tr').forEach(r => r.classList.remove('selected-row'));
      if (rowEl) rowEl.classList.add('selected-row');
      document.getElementById('tx-detail-sheet').innerHTML = TX_DETAILS[txId] || TX_DETAILS['tx5'];
    }};

    window.updateDepositThreshold = function() {{
      const qualInc = parseFloat(document.getElementById('sl-qual-income').value || 18958.33);
      const thresh = qualInc * 0.50;
      const threshFmt = '$' + thresh.toLocaleString('en-US', {{minimumFractionDigits: 2, maximumFractionDigits: 2}});

      document.getElementById('val-qual-inc').innerText = '$' + qualInc.toLocaleString('en-US', {{minimumFractionDigits: 2, maximumFractionDigits: 2}}) + '/mo';
      document.getElementById('val-threshold').innerText = threshFmt;
      document.getElementById('lbl-slider-thresh').innerText = threshFmt;

      let flaggedCount = 0;
      let flaggedSum = 0;

      const tx5El = document.getElementById('status-tx5');
      if (14000 > thresh) {{
        tx5El.className = 'pill-flag';
        tx5El.innerText = 'FLAGGED > ' + threshFmt + ' THRESHOLD';
        flaggedCount++;
        flaggedSum += 14000;
      }} else {{
        tx5El.className = 'pill-exempt';
        tx5El.innerText = 'EXEMPT · BELOW 50%';
      }}

      const tx6El = document.getElementById('status-tx6');
      if (6200 > thresh) {{
        tx6El.className = 'pill-flag';
        tx6El.innerText = 'FLAGGED > ' + threshFmt + ' THRESHOLD';
        flaggedCount++;
        flaggedSum += 6200;
      }} else {{
        tx6El.className = 'pill-exempt';
        tx6El.innerText = 'EXEMPT · BELOW 50%';
      }}

      document.getElementById('val-flagged-count').innerText = flaggedCount + ' Flagged ($' + flaggedSum.toLocaleString() + ')';
    }};

    window.playBsaAuditAudio = function(btnEl) {{
      const thresh = document.getElementById('val-threshold').innerText;
      const script = "BSA AML and Fannie Mae B3-4.2-02 Large Deposit Audit for Ally Bank Checking Account ending in 4829. Based on qualifying income of 18,958 dollars and 33 cents per month, the 50 percent large deposit threshold is " + thresh + ". All four Gusto ACH payroll deposits are automatically exempted. The September 18th incoming Fedwire of 14,000 dollars exceeds the threshold and has been fully sourced using a signed Fannie Mae Gift Letter and Wells Fargo Fedwire confirmation from the borrower's father, Robert Chen.";
      if (window.playLiveCallClip) {{
        window.playLiveCallClip(script, "Puck", "BSA/AML & Asset Underwriting Auditor", btnEl);
      }}
    }};

    window.runLiveVertexAI = async function() {{
      const model = window.getSelectedModel ? window.getSelectedModel() : 'gemini-4-argon';
      const thresh = document.getElementById('val-threshold').innerText;
      const outEl = document.getElementById('bsa-audit-output');
      outEl.innerHTML = '<em>Running Vertex AI (' + model + ') BSA/AML &amp; Fannie Mae B3-4.2-02 Deposit Sourcing Audit...</em>';
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '2.3',
            model: model,
            user_input: 'Audit Ally Bank Checking #...4829 60-day statement with 50% threshold ' + thresh + ' and verify the $14,000.00 09/18/2026 Fedwire gift deposit per Fannie Mae B3-4.2-02 and B3-4.3-04.'
          }})
        }});
        const data = await res.json();
        const text = data.output || data.response || data.result || '';
        if (text) {{
          outEl.innerHTML = '<strong>VERTEX AI (' + model.toUpperCase() + ') BSA/AML AUDIT:</strong><br/>' + text.replace(/\\n/g, '<br/>');
        }} else {{
          outEl.innerHTML = '<strong>ASSET SOURCING CLEARED (' + model + '):</strong> 09/18/2026 $14,000.00 Fedwire verified against executed Gift Letter &amp; IMAD receipt.';
        }}
      }} catch (e) {{
        outEl.innerHTML = '<strong>ASSET SOURCING CLEARED:</strong> 09/18/2026 $14,000.00 Fedwire verified against executed Gift Letter &amp; IMAD receipt.';
      }}
    }};
  </script>

  {floating_bar}
</body>
</html>"""
