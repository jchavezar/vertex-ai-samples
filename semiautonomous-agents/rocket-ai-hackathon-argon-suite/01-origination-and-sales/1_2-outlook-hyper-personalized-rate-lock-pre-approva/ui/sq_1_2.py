# -*- coding: utf-8 -*-
"""Square 1.2: Outlook Hyper-Personalized Rate-Lock & Pre-Approval Agent — Standalone UI Design File.
Visual Archetype: Authentic Microsoft Outlook 365 Desktop Client (Fluent Blue #0F6CBD, Ribbon Gray #F3F2F1,
4-column desktop client: App Rail -> Folder Tree -> Inbox List -> Email Reading/Compose Pane + Copilot Add-In)."""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_1_2(auth_token: str) -> str:
    controls = render_floating_control_bar_and_drawer("1.2", auth_token)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Outlook 365 Rocket Rate-Lock Copilot Add-In</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Segoe UI', 'Inter', sans-serif;
      background: #F3F2F1;
      color: #201F1E;
      height: 100vh;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }}
    .mono {{ font-family: 'JetBrains Mono', monospace; }}

    /* Microsoft 365 Top Fluent Title Bar */
    .o365-topbar {{
      height: 48px;
      background: #0F6CBD;
      color: #FFFFFF;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 18px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.12);
    }}
    .o365-search {{
      background: rgba(255,255,255,0.88);
      color: #323130;
      border-radius: 6px;
      padding: 6px 14px;
      width: 380px;
      font-size: 12.5px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    /* Outlook Ribbon Command Bar */
    .o365-ribbon {{
      height: 44px;
      background: #FAF9F8;
      border-bottom: 1px solid #EDEBE9;
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 0 16px;
      font-size: 12.5px;
    }}
    .ribbon-btn {{
      padding: 6px 12px;
      border-radius: 4px;
      border: 1px solid transparent;
      background: transparent;
      color: #323130;
      font-weight: 600;
      font-size: 12px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}
    .ribbon-btn:hover {{
      background: #EDEBE9;
    }}
    .ribbon-btn.primary {{
      background: #0F6CBD;
      color: #FFFFFF;
    }}
    .ribbon-btn.primary:hover {{
      background: #115EA3;
    }}

    /* 4-Pane Desktop Grid */
    .o365-grid {{
      display: grid;
      grid-template-columns: 52px 190px 300px 1fr 370px;
      flex: 1;
      height: calc(100vh - 92px);
      overflow: hidden;
    }}
    @media (max-width: 1200px) {{
      .o365-grid {{ grid-template-columns: 260px 1fr 340px; }}
      .app-rail, .folder-pane {{ display: none; }}
    }}

    .app-rail {{
      background: #F3F2F1;
      border-right: 1px solid #EDEBE9;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding-top: 12px;
      gap: 16px;
    }}
    .folder-pane {{
      background: #F3F2F1;
      border-right: 1px solid #EDEBE9;
      padding: 14px 10px;
      font-size: 13px;
    }}
    .folder-item {{
      padding: 8px 12px;
      border-radius: 6px;
      display: flex;
      justify-content: space-between;
      cursor: pointer;
      color: #323130;
      margin-bottom: 2px;
    }}
    .folder-item.active {{
      background: #E1DFDD;
      font-weight: 700;
      color: #0F6CBD;
    }}

    /* Message List */
    .msg-list {{
      background: #FFFFFF;
      border-right: 1px solid #EDEBE9;
      overflow-y: auto;
    }}
    .msg-card {{
      padding: 14px 16px;
      border-bottom: 1px solid #F3F2F1;
      border-left: 4px solid transparent;
      cursor: pointer;
      transition: 0.15s;
    }}
    .msg-card:hover {{ background: #FAF9F8; }}
    .msg-card.active {{
      background: #EFF6FC;
      border-left-color: #0F6CBD;
    }}

    /* Email Reading & Compose Pane */
    .reading-pane {{
      background: #FFFFFF;
      padding: 24px 32px 80px 32px;
      overflow-y: auto;
    }}
    .email-draft-box {{
      margin-top: 18px;
      border: 1px solid #C8C6C4;
      border-radius: 8px;
      box-shadow: 0 6px 20px rgba(0,0,0,0.06);
      overflow: hidden;
    }}
    .rate-table {{
      width: 100%;
      border-collapse: collapse;
      margin: 14px 0;
      font-size: 12.5px;
    }}
    .rate-table th {{
      background: #EFF6FC;
      color: #0F6CBD;
      text-align: left;
      padding: 10px 12px;
      border-bottom: 2px solid #0F6CBD;
      font-size: 11px;
      text-transform: uppercase;
    }}
    .rate-table td {{
      padding: 10px 12px;
      border-bottom: 1px solid #EDEBE9;
    }}
    .pdf-chip {{
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 8px 14px;
      border-radius: 6px;
      border: 1px solid #E1DFDD;
      background: #FAF9F8;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
    }}

    /* Right Copilot Sidecar Add-In */
    .copilot-pane {{
      background: #FAF9F8;
      border-left: 1px solid #EDEBE9;
      padding: 18px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}
    .copilot-card {{
      background: #FFFFFF;
      border: 1px solid #E1DFDD;
      border-radius: 10px;
      padding: 14px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }}
  </style>
</head>
<body>

  <!-- MICROSOFT OUTLOOK 365 FLUENT BAR -->
  <header class="o365-topbar">
    <div style="display:flex;align-items:center;gap:12px;">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="white"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
      <span style="font-weight:700;font-size:15px;">Outlook</span>
      <span style="opacity:0.6;">|</span>
      <span style="font-size:12px;font-weight:600;background:rgba(255,255,255,0.18);padding:3px 10px;border-radius:999px;">Rocket Pro TPO Banker Desk • O365 Add-In</span>
    </div>
    <div class="o365-search">
      <span>🔍</span>
      <span>Search borrower emails, NMLS #10492, rate locks...</span>
    </div>
    <div style="display:flex;align-items:center;gap:10px;">
      <div class="mono" style="background:rgba(0,0,0,0.22);padding:4px 10px;border-radius:6px;font-size:11px;">
        Model:
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)" style="background:transparent;color:#FFF;font-weight:700;border:none;outline:none;font-family:'JetBrains Mono',monospace;font-size:11px;cursor:pointer;">
          <option value="gemini-4-argon" style="color:#000;">gemini-4-argon</option>
          <option value="gemini-3.8-flash" style="color:#000;">gemini-3.8-flash</option>
        </select>
      </div>
    </div>
  </header>

  <!-- OUTLOOK RIBBON BAR -->
  <div class="o365-ribbon">
    <button class="ribbon-btn primary" onclick="window.runLiveVertexAI()" id="draft-btn">✨ Draft Hyper-Personalized Rate Lock Reply</button>
    <button class="ribbon-btn" onclick="selectOptionHighlight(1)">📊 Highlight Option A (Par 6.125%)</button>
    <button class="ribbon-btn" onclick="selectOptionHighlight(2)">🎯 Highlight Option B (5.875% Permanent Buydown)</button>
    <button class="ribbon-btn" onclick="selectOptionHighlight(3)">🏡 Highlight Option C (2-1 Seller Buydown)</button>
    <button class="ribbon-btn" onclick="alert('Verified Pre-Approval Letter RKT-PA-500K.pdf queued in Encompass & O365 Outbox!')">📎 Preview Attached Pre-Approval PDF</button>
  </div>

  <!-- 4-PANE OUTLOOK WORKSPACE -->
  <div class="o365-grid">
    <!-- Pane 1: App Rail -->
    <div class="app-rail">
      <div title="Mail" style="color:#0F6CBD;font-size:18px;cursor:pointer;">✉️</div>
      <div title="Calendar" style="color:#605E5C;font-size:18px;cursor:pointer;">📅</div>
      <div title="Contacts" style="color:#605E5C;font-size:18px;cursor:pointer;">👥</div>
      <div title="Rocket Add-In" style="color:#E11D48;font-size:18px;cursor:pointer;">🚀</div>
    </div>

    <!-- Pane 2: Folder Tree -->
    <div class="folder-pane">
      <div style="font-size:11px;font-weight:700;color:#605E5C;text-transform:uppercase;padding:4px 12px 8px 12px;">Favorites</div>
      <div class="folder-item active"><span>📥 Rate Lock Inbox</span><span>3</span></div>
      <div class="folder-item"><span>⚡ Pre-Approvals</span><span>12</span></div>
      <div class="folder-item"><span>📤 Sent Items</span><span></span></div>
      <div class="folder-item"><span>🛡️ Compliance Archive</span><span></span></div>
    </div>

    <!-- Pane 3: Inbox Message List -->
    <div class="msg-list">
      <div style="padding:12px 16px;border-bottom:1px solid #EDEBE9;font-weight:700;font-size:13px;display:flex;justify-content:space-between;">
        <span>Focused Inbox</span>
        <span style="color:#0F6CBD;font-size:11px;">Filter ▼</span>
      </div>
      <div class="msg-card active" onclick="loadThread(0, this)">
        <div style="display:flex;justify-content:space-between;font-size:13px;font-weight:700;">
          <span>David & Priya Patel</span>
          <span style="color:#0F6CBD;font-size:11px;">10:42 AM</span>
        </div>
        <div style="font-size:12px;font-weight:600;color:#0F6CBD;margin:2px 0;">URGENT: Offer on $625k Novi Home — Lock Rate or Buy Points?</div>
        <div style="font-size:11.5px;color:#605E5C;">We are submitting our offer today ($500k loan, 20% down). Seller offered $8,500 credit...</div>
      </div>
      <div class="msg-card" onclick="loadThread(1, this)">
        <div style="display:flex;justify-content:space-between;font-size:13px;font-weight:700;">
          <span>Sarah Jenkins (Redfin Agent)</span>
          <span style="color:#605E5C;font-size:11px;">9:15 AM</span>
        </div>
        <div style="font-size:12px;font-weight:600;color:#323130;margin:2px 0;">Updated Pre-Approval Letter for 812 Villa Rd ($550,000)</div>
        <div style="font-size:11.5px;color:#605E5C;">Can we regenerate the Verified Approval letter at $550k so listing agent doesn't see max cap?</div>
      </div>
      <div class="msg-card" onclick="loadThread(2, this)">
        <div style="display:flex;justify-content:space-between;font-size:13px;font-weight:700;">
          <span>Rocket Secondary Desk</span>
          <span style="color:#605E5C;font-size:11px;">8:30 AM</span>
        </div>
        <div style="font-size:12px;font-weight:600;color:#323130;margin:2px 0;">Morning Rate Sheet: 30Yr Fixed Par 6.125% (-8 bps)</div>
        <div style="font-size:11.5px;color:#605E5C;">UMBS 5.5 rallied +0-06 following CPI print. 2-1 Temporary Buydown pricing improved...</div>
      </div>
    </div>

    <!-- Pane 4: Email Reading & Live Reply Composer -->
    <main class="reading-pane">
      <h2 id="mail-subject" style="font-size:19px;font-weight:700;color:#201F1E;margin-bottom:12px;">
        URGENT: Offer on $625k Novi Home — Lock Rate or Buy Points?
      </h2>
      <div style="display:flex;align-items:center;justify-content:space-between;padding-bottom:14px;border-bottom:1px solid #EDEBE9;">
        <div style="display:flex;align-items:center;gap:10px;">
          <div style="width:38px;height:38px;border-radius:50%;background:#0F6CBD;color:#FFF;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;">DP</div>
          <div>
            <div style="font-size:13.5px;font-weight:700;" id="mail-sender">David & Priya Patel &lt;dpatel.novi@gmail.com&gt;</div>
            <div style="font-size:11.5px;color:#605E5C;">To: You (Senior Loan Officer • NMLS #1049281); Cc: Sarah Jenkins (Redfin Partner)</div>
          </div>
        </div>
        <span class="mono" style="font-size:11px;background:#EFF6FC;color:#0F6CBD;padding:4px 10px;border-radius:4px;font-weight:700;">Loan #RKT-994120 • 772 FICO</span>
      </div>

      <div id="inbound-body" style="padding:14px 0;font-size:13.5px;line-height:1.6;color:#323130;">
        Hi Jordan — We are writing our offer on 44910 Twining Dr in Novi for <strong>$625,000</strong> with 20% down (<strong>$500,000 loan amount</strong>). The seller is willing to give us an <strong>$8,500 closing cost concession</strong>. Should we take the Par rate at 6.125%, pay 0.75 points to permanently buy down to 5.875%, or use the seller credit for a 2-1 temporary buydown? Also please attach our Verified Pre-Approval letter!
      </div>

      <!-- AI Compose Box Inside Outlook -->
      <div class="email-draft-box">
        <div style="background:#EFF6FC;padding:10px 16px;border-bottom:1px solid #C8C6C4;display:flex;justify-content:space-between;align-items:center;">
          <div style="font-size:12px;font-weight:700;color:#0F6CBD;display:flex;align-items:center;gap:6px;">
            <span>🚀 Rocket AI Rate-Lock Draft</span>
            <span class="mono" id="draft-model-badge" style="background:#0F6CBD;color:#FFF;padding:2px 7px;border-radius:4px;font-size:10px;">gemini-4-argon</span>
          </div>
          <div style="display:flex;gap:8px;">
            <button onclick="sendOutlookReply()" style="background:#0F6CBD;color:#FFF;border:none;padding:5px 14px;border-radius:4px;font-size:12px;font-weight:700;cursor:pointer;">Send Email + Pre-Approval PDF</button>
          </div>
        </div>

        <div style="padding:18px;">
          <div id="ai-email-intro" style="font-size:13.5px;line-height:1.6;color:#201F1E;margin-bottom:12px;">
            Hi David & Priya — Congratulations on submitting your offer in Novi! I ran all three structures through our deterministic pricing engine for your <strong>$500,000 loan</strong> (80% LTV, $0 PMI). Because your seller is contributing <strong>$8,500</strong>, here is your exact side-by-side comparison:
          </div>

          <!-- Side-by-Side 3-Option Rate Table inside the Email Draft -->
          <table class="rate-table">
            <thead>
              <tr>
                <th>Structure</th>
                <th>Interest Rate / APR</th>
                <th>Monthly P&I Payment</th>
                <th>Upfront Points / Subsidy</th>
                <th>Break-Even / Strategy</th>
              </tr>
            </thead>
            <tbody>
              <tr id="row-opt-1">
                <td><strong>Option A: 30-Yr Par Lock</strong></td>
                <td class="mono" id="tb-par-rate">6.125% (6.184% APR)</td>
                <td class="mono" style="font-weight:700;" id="tb-par-pi">$3,038.05 / mo</td>
                <td class="mono">$0.00 (0.000 pts)</td>
                <td>Apply $8,500 seller credit to escrow/title fees</td>
              </tr>
              <tr id="row-opt-2" style="background:#F0FDF4;">
                <td><strong>Option B: Permanent Buydown ⭐</strong></td>
                <td class="mono" id="tb-buy-rate">5.875% (5.962% APR)</td>
                <td class="mono" style="font-weight:700;color:#059669;" id="tb-buy-pi">$2,957.69 / mo</td>
                <td class="mono" id="tb-buy-cost">$3,750.00 (0.750 pts)</td>
                <td class="mono" id="tb-buy-be">46.7 Mos (Saves $80.36/mo for 30 yrs)</td>
              </tr>
              <tr id="row-opt-3">
                <td><strong>Option C: 2-1 Seller Buydown</strong></td>
                <td class="mono">Yr1: 4.125% | Yr2: 5.125%</td>
                <td class="mono" style="font-weight:700;color:#0F6CBD;" id="tb-21-pi">Yr1: $2,423.25 / Yr2: $2,722.43</td>
                <td class="mono" id="tb-21-sub">$11,168.16 Seller Escrow</td>
                <td>Saves $614.80/mo in Year 1; refi when rates dip</td>
              </tr>
            </tbody>
          </table>

          <!-- Attached Pre-Approval PDF Card -->
          <div style="margin-top:14px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;">
            <div class="pdf-chip">
              <span style="color:#D83B01;font-size:18px;">📄</span>
              <div>
                <div id="pdf-filename">Rocket_Verified_PreApproval_Patel_$625000.pdf</div>
                <div style="font-size:10.5px;color:#605E5C;">TILA Reg Z § 1026.24 Compliant • NMLS #3030 • Verified Assets & DU Approve/Eligible</div>
              </div>
            </div>
            <span id="send-toast" style="font-size:12px;font-weight:700;color:#059669;display:none;">✓ Sent via Microsoft Graph API + Logged to CRM!</span>
          </div>
        </div>
      </div>
    </main>

    <!-- Pane 5: Rocket Rate-Lock Copilot Add-In Sidecar -->
    <aside class="copilot-pane">
      <div style="display:flex;align-items:center;justify-content:space-between;">
        <div style="font-weight:800;font-size:13.5px;color:#0F6CBD;">🚀 Rocket Rate-Lock Add-In</div>
        <span class="mono" style="font-size:10px;background:#E1DFDD;padding:2px 6px;border-radius:4px;">LIVE SANDBOX</span>
      </div>

      <div class="copilot-card">
        <div style="font-size:11px;font-weight:700;color:#605E5C;text-transform:uppercase;margin-bottom:10px;">🎛️ Interactive Pricing Calibration</div>
        <div style="margin-bottom:12px;">
          <div style="display:flex;justify-content:space-between;font-size:11.5px;margin-bottom:4px;">
            <span>Loan Amount:</span>
            <strong class="mono" id="lbl-loan" style="color:#0F6CBD;">$500,000</strong>
          </div>
          <input type="range" id="sl-loan" min="250000" max="900000" step="10000" value="500000" style="width:100%;accent-color:#0F6CBD;" oninput="recalcRateLock()">
        </div>
        <div style="margin-bottom:12px;">
          <div style="display:flex;justify-content:space-between;font-size:11.5px;margin-bottom:4px;">
            <span>30-Yr Par Rate (%):</span>
            <strong class="mono" id="lbl-par" style="color:#0F6CBD;">6.125%</strong>
          </div>
          <input type="range" id="sl-par" min="5.250" max="7.250" step="0.125" value="6.125" style="width:100%;accent-color:#0F6CBD;" oninput="recalcRateLock()">
        </div>
        <div>
          <div style="display:flex;justify-content:space-between;font-size:11.5px;margin-bottom:4px;">
            <span>Permanent Buydown Rate (%):</span>
            <strong class="mono" id="lbl-buy" style="color:#059669;">5.875%</strong>
          </div>
          <input type="range" id="sl-buy" min="4.875" max="6.875" step="0.125" value="5.875" style="width:100%;accent-color:#059669;" oninput="recalcRateLock()">
        </div>
      </div>

      <div class="copilot-card">
        <div style="font-size:11px;font-weight:700;color:#605E5C;text-transform:uppercase;margin-bottom:6px;">🛡️ TILA Reg Z § 1026.24 Guardrail</div>
        <div style="font-size:12px;color:#323130;line-height:1.5;">
          Every quoted note rate automatically pairs with its <strong>Annual Percentage Rate (APR)</strong> and NMLS #3030 disclosure footer before Outlook enables Send.
        </div>
      </div>

      <button onclick="window.runLiveVertexAI()" style="width:100%;padding:11px;border-radius:8px;background:#0F6CBD;color:#FFF;border:none;font-weight:700;font-size:12.5px;cursor:pointer;">
        ⚡ Re-Generate Draft with Selected Model
      </button>
    </aside>
  </div>

  {controls}

  <script>
    function selectOptionHighlight(opt) {{
      [1,2,3].forEach(i => {{
        document.getElementById('row-opt-' + i).style.background = (i === opt) ? '#EFF6FC' : '#FFFFFF';
      }});
    }}

    function sendOutlookReply() {{
      const t = document.getElementById('send-toast');
      t.style.display = 'inline';
      setTimeout(() => {{ t.style.display = 'none'; }}, 4000);
    }}

    function loadThread(idx, el) {{
      document.querySelectorAll('.msg-card').forEach(c => c.classList.remove('active'));
      el.classList.add('active');
      if (idx === 0) {{
        document.getElementById('sl-loan').value = 500000;
        document.getElementById('mail-subject').innerText = 'URGENT: Offer on $625k Novi Home — Lock Rate or Buy Points?';
        document.getElementById('pdf-filename').innerText = 'Rocket_Verified_PreApproval_Patel_$625000.pdf';
      }} else if (idx === 1) {{
        document.getElementById('sl-loan').value = 440000;
        document.getElementById('mail-subject').innerText = 'Updated Pre-Approval Letter for 812 Villa Rd ($550,000)';
        document.getElementById('pdf-filename').innerText = 'Rocket_Verified_PreApproval_VillaRd_$550000.pdf';
      }} else {{
        document.getElementById('sl-loan').value = 600000;
        document.getElementById('mail-subject').innerText = 'Morning Rate Sheet Lock Advisory ($600,000 Jumbo/Conforming)';
        document.getElementById('pdf-filename').innerText = 'Rocket_RateSheet_Lock_Advisory_$600000.pdf';
      }}
      recalcRateLock();
    }}

    async function recalcRateLock() {{
      const loan = parseFloat(document.getElementById('sl-loan').value);
      const par = parseFloat(document.getElementById('sl-par').value);
      const buy = parseFloat(document.getElementById('sl-buy').value);
      document.getElementById('lbl-loan').innerText = '$' + loan.toLocaleString();
      document.getElementById('lbl-par').innerText = par.toFixed(3) + '%';
      document.getElementById('lbl-buy').innerText = buy.toFixed(3) + '%';

      const res = await fetch('/api/sandbox', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{
          code: '1.2',
          action: 'calc_rate_lock_options',
          params: {{loan_amount: loan, base_rate: par, buydown_rate: buy, buydown_pts: 0.75}}
        }})
      }});
      const data = await res.json();
      if (data.ok && data.metrics) {{
        const m = data.metrics;
        document.getElementById('tb-par-rate').innerText = par.toFixed(3) + '% (' + (par + 0.059).toFixed(3) + '% APR)';
        document.getElementById('tb-par-pi').innerText = (m.option_a_par_pi || '').split('@')[0].trim();
        document.getElementById('tb-buy-rate').innerText = buy.toFixed(3) + '% (' + (buy + 0.087).toFixed(3) + '% APR)';
        document.getElementById('tb-buy-pi').innerText = (m.option_b_buydown_pi || '').split('@')[0].trim();
        document.getElementById('tb-buy-cost').innerText = '$' + Math.round(loan * 0.0075).toLocaleString() + ' (0.750 pts)';
        document.getElementById('tb-buy-be').innerText = m.option_b_breakeven || '';
        document.getElementById('tb-21-pi').innerText = (m.option_c_2_1_buydown || '').split('|').slice(0,2).join(' | ');
        document.getElementById('tb-21-sub').innerText = ((m.option_c_2_1_buydown || '').split('Subsidy:')[1] || '').trim() + ' Seller Escrow';
      }}
    }}

    window.runLiveVertexAI = async function() {{
      const btn = document.getElementById('draft-btn');
      const model = window.getSelectedModel();
      btn.innerText = '⏳ Drafting on ' + model + '...';
      document.getElementById('draft-model-badge').innerText = model;

      const loan = parseFloat(document.getElementById('sl-loan').value);
      const par = parseFloat(document.getElementById('sl-par').value);
      const buy = parseFloat(document.getElementById('sl-buy').value);

      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{'Content-Type': 'application/json'}},
          body: JSON.stringify({{
            code: '1.2',
            model: model,
            params: {{loan_amount: loan, base_rate: par, buydown_rate: buy, buydown_pts: 0.75}}
          }})
        }});
        const data = await res.json();
        document.getElementById('draft-model-badge').innerText = data.model_used || model;
        if (data.structured_data && (data.structured_data.email_body || data.structured_data.executive_summary)) {{
          document.getElementById('ai-email-intro').innerHTML = data.structured_data.email_body || data.structured_data.executive_summary;
        }} else if (data.output) {{
          document.getElementById('ai-email-intro').innerText = data.output;
        }}
      }} catch (e) {{}}
      finally {{
        btn.innerText = '✨ Draft Hyper-Personalized Rate Lock Reply';
      }}
    }};
  </script>
</body>
</html>"""
