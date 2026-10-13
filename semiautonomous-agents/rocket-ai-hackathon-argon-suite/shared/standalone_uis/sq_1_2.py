# -*- coding: utf-8 -*-
"""Square 1.2: Automated Lead Follow-Up Engine — Standalone UI Design File.
Visual Archetype: Authentic Salesforce Lightning / HubSpot CRM Light Interface
(#F3F2F2 cloud gray background, #0176D3 Salesforce Blue top bar, #FFFFFF crisp CRM cards, Public Sans font).
3-Column CRM Lead Record for Borrower David Chen (Austin, TX · $485,000 Refi Lead)."""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_1_2(auth_token: str) -> str:
    controls = render_floating_control_bar_and_drawer("1.2", auth_token)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Rocket Mortgage CRM · Automated Lead Follow-Up Engine (David Chen)</title>
  <link href="https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Public Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background: #F3F2F2;
      color: #181818;
      min-height: 100vh;
      padding-bottom: 84px;
    }}
    .mono {{ font-family: 'IBM Plex Mono', monospace; }}

    /* Salesforce Lightning Global Header */
    .sf-topbar {{
      background: #0176D3;
      color: #FFFFFF;
      height: 54px;
      padding: 0 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12);
    }}
    .sf-brand {{
      display: flex;
      align-items: center;
      gap: 12px;
      font-weight: 700;
      font-size: 16px;
    }}
    .sf-waffle {{
      width: 32px;
      height: 32px;
      border-radius: 6px;
      background: rgba(255, 255, 255, 0.16);
      display: grid;
      grid-template-columns: repeat(3, 5px);
      gap: 3px;
      place-content: center;
      cursor: pointer;
    }}
    .sf-waffle span {{
      width: 5px;
      height: 5px;
      border-radius: 50%;
      background: #FFFFFF;
    }}
    .sf-search {{
      background: #FFFFFF;
      color: #444444;
      border-radius: 6px;
      padding: 7px 14px;
      width: 360px;
      font-size: 13px;
      display: flex;
      align-items: center;
      gap: 8px;
      box-shadow: inset 0 1px 2px rgba(0,0,0,0.08);
    }}
    @media (max-width: 960px) {{
      .sf-search {{ display: none; }}
    }}

    /* Salesforce Record Highlights Subheader */
    .sf-record-header {{
      background: #FFFFFF;
      border-bottom: 1px solid #DDDBDA;
      padding: 16px 28px;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }}
    .lead-badge {{
      background: #E8F4FF;
      color: #0176D3;
      font-weight: 700;
      font-size: 11px;
      padding: 3px 9px;
      border-radius: 4px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}

    /* 3-Column CRM Workspace Grid */
    .crm-grid {{
      max-width: 1420px;
      margin: 20px auto;
      padding: 0 24px;
      display: grid;
      grid-template-columns: 330px 1fr 350px;
      gap: 18px;
      align-items: start;
    }}
    @media (max-width: 1180px) {{
      .crm-grid {{ grid-template-columns: 1fr; }}
    }}

    .crm-card {{
      background: #FFFFFF;
      border: 1px solid #DDDBDA;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
      overflow: hidden;
      margin-bottom: 16px;
    }}
    .crm-card-header {{
      background: #FAF9F8;
      border-bottom: 1px solid #DDDBDA;
      padding: 12px 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-weight: 700;
      font-size: 13.5px;
      color: #181818;
    }}
    .crm-card-body {{
      padding: 16px;
    }}

    /* Field List */
    .field-row {{
      display: flex;
      justify-content: space-between;
      padding: 8px 0;
      border-bottom: 1px solid #F3F2F2;
      font-size: 13px;
    }}
    .field-label {{ color: #5C5C5C; font-weight: 500; }}
    .field-val {{ color: #181818; font-weight: 700; }}

    /* Composer Tabs */
    .tab-bar {{
      display: flex;
      border-bottom: 2px solid #E5E5E5;
      background: #FAF9F8;
      padding: 0 16px;
      gap: 4px;
    }}
    .tab-btn {{
      padding: 11px 16px;
      border: none;
      background: transparent;
      font-family: inherit;
      font-size: 13px;
      font-weight: 600;
      color: #5C5C5C;
      cursor: pointer;
      border-bottom: 3px solid transparent;
      margin-bottom: -2px;
      transition: 0.15s;
    }}
    .tab-btn.active {{
      color: #0176D3;
      border-bottom-color: #0176D3;
      font-weight: 700;
      background: #FFFFFF;
    }}
    .tab-panel {{
      display: none;
      padding: 18px;
    }}
    .tab-panel.active {{
      display: block;
    }}

    /* Buttons */
    .sf-btn-primary {{
      background: #0176D3;
      color: #FFFFFF;
      border: 1px solid #0176D3;
      border-radius: 6px;
      padding: 10px 16px;
      font-family: inherit;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      transition: 0.15s;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }}
    .sf-btn-primary:hover {{ background: #014486; }}

    .sf-btn-voice {{
      background: #EFF6FF;
      color: #0176D3;
      border: 1px solid #93C5FD;
      border-radius: 6px;
      padding: 9px 14px;
      font-family: inherit;
      font-size: 12.5px;
      font-weight: 700;
      cursor: pointer;
      transition: 0.15s;
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }}
    .sf-btn-voice:hover {{ background: #DBEAFE; }}

    /* Pipeline Stages */
    .stage-pill {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 10px 12px;
      border-radius: 6px;
      border: 1px solid #DDDBDA;
      margin-bottom: 8px;
      font-size: 12.5px;
      font-weight: 600;
      cursor: pointer;
      background: #FFFFFF;
      transition: 0.15s;
    }}
    .stage-pill.completed {{
      background: #ECFDF5;
      border-color: #A7F3D0;
      color: #065F46;
    }}
    .stage-pill.current {{
      background: #E8F4FF;
      border-color: #0176D3;
      color: #014486;
      font-weight: 700;
    }}

    /* Timeline */
    .timeline-item {{
      position: relative;
      padding-left: 24px;
      padding-bottom: 14px;
      border-left: 2px solid #0176D3;
      margin-left: 10px;
    }}
    .timeline-dot {{
      position: absolute;
      left: -7px;
      top: 2px;
      width: 12px;
      height: 12px;
      border-radius: 50%;
      background: #0176D3;
      border: 2px solid #FFFFFF;
    }}
  </style>
</head>
<body>

  <!-- SALESFORCE LIGHTNING TOP BAR -->
  <header class="sf-topbar">
    <div class="sf-brand">
      <div class="sf-waffle" title="App Launcher">
        <span></span><span></span><span></span>
        <span></span><span></span><span></span>
        <span></span><span></span><span></span>
      </div>
      <span>Rocket Mortgage CRM</span>
      <span style="opacity:0.5;">|</span>
      <span style="font-size:13px;font-weight:500;opacity:0.95;">Automated Lead Follow-Up Engine</span>
    </div>

    <div class="sf-search">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#5C5C5C" stroke-width="2.2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
      <span>Search Leads, NMLS Records, Rate Alerts (David Chen)...</span>
    </div>

    <div style="display:flex;align-items:center;gap:12px;">
      <div style="background:rgba(255,255,255,0.16);padding:5px 12px;border-radius:6px;font-size:12px;display:flex;align-items:center;gap:6px;">
        <span style="font-weight:600;">AI Model:</span>
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)" style="background:transparent;color:#FFFFFF;font-weight:700;border:none;outline:none;font-family:inherit;font-size:12px;cursor:pointer;">
          <option value="gemini-4-argon" style="color:#181818;">gemini-4-argon</option>
          <option value="gemini-3.8-flash" style="color:#181818;">gemini-3.8-flash</option>
        </select>
      </div>
    </div>
  </header>

  <!-- RECORD HIGHLIGHTS BAR -->
  <section class="sf-record-header">
    <div style="display:flex;align-items:center;gap:14px;">
      <div style="width:46px;height:46px;border-radius:50%;background:#0176D3;color:#FFFFFF;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:17px;">
        DC
      </div>
      <div>
        <div style="display:flex;align-items:center;gap:8px;">
          <span class="lead-badge">Refi Rate-Drop Lead · #LD-88412</span>
          <span style="font-size:12px;color:#059669;font-weight:700;">● Active Rate Trigger (-150 bps)</span>
        </div>
        <h1 style="font-size:21px;font-weight:800;color:#181818;margin-top:3px;">
          David Chen · Austin, TX 78704 (<span id="hdr-loan-amt">$485,000</span> Refi Lead)
        </h1>
      </div>
    </div>

    <div style="display:flex;align-items:center;gap:18px;flex-wrap:wrap;">
      <div>
        <div style="font-size:11px;color:#5C5C5C;text-transform:uppercase;font-weight:600;">Current Note Rate</div>
        <div class="mono" style="font-size:15px;font-weight:700;color:#B91C1C;">7.375% ($3,349/mo)</div>
      </div>
      <div>
        <div style="font-size:11px;color:#5C5C5C;text-transform:uppercase;font-weight:600;">Target Rocket Rate</div>
        <div class="mono" id="hdr-target-rate" style="font-size:15px;font-weight:700;color:#0176D3;">5.875% ($2,869/mo)</div>
      </div>
      <div>
        <div style="font-size:11px;color:#5C5C5C;text-transform:uppercase;font-weight:600;">Monthly P&I Savings</div>
        <div class="mono" id="hdr-mo-savings" style="font-size:16px;font-weight:800;color:#059669;">+$480 / mo ($5,760/yr)</div>
      </div>
    </div>
  </section>

  <!-- 3-COLUMN SALESFORCE LIGHTNING LEAD RECORD -->
  <div class="crm-grid">

    <!-- LEFT COLUMN: CRM CONTACT CARD & INTERACTIVE RATE SLIDERS -->
    <aside>
      <div class="crm-card">
        <div class="crm-card-header">
          <span>👤 Borrower Contact Profile</span>
          <span class="mono" style="font-size:11px;color:#0176D3;">Verified</span>
        </div>
        <div class="crm-card-body">
          <div class="field-row">
            <span class="field-label">Full Name</span>
            <span class="field-val">David Chen</span>
          </div>
          <div class="field-row">
            <span class="field-label">Property City</span>
            <span class="field-val">Austin, TX 78704 (Travis Co.)</span>
          </div>
          <div class="field-row">
            <span class="field-label">Mobile Phone</span>
            <span class="field-val mono">(512) 555-0194</span>
          </div>
          <div class="field-row">
            <span class="field-label">Email</span>
            <span class="field-val">dchen.austin@gmail.com</span>
          </div>
          <div class="field-row">
            <span class="field-label">Middle FICO Score</span>
            <span class="field-val" style="color:#059669;">742 (Soft Pull Verified)</span>
          </div>
          <div class="field-row">
            <span class="field-label">Current Servicer Rate</span>
            <span class="field-val mono" style="color:#B91C1C;">7.375% (Orig. Oct 2024)</span>
          </div>
          <div class="field-row" style="border-bottom:none;">
            <span class="field-label">Target Refi Rate</span>
            <span class="field-val mono" id="contact-target-rate" style="color:#0176D3;">5.875% (30-Yr Fixed)</span>
          </div>
        </div>
      </div>

      <div class="crm-card">
        <div class="crm-card-header">
          <span>🎛️ Refi Savings Scenario Calibration</span>
        </div>
        <div class="crm-card-body" style="display:flex;flex-direction:column;gap:14px;">
          <div>
            <div style="display:flex;justify-content:space-between;font-size:12.5px;margin-bottom:5px;">
              <span style="color:#5C5C5C;font-weight:600;">Loan Balance:</span>
              <strong class="mono" id="lbl-loan-bal" style="color:#0176D3;">$485,000</strong>
            </div>
            <input type="range" id="sl-loan" min="250000" max="850000" step="5000" value="485000" style="width:100%;accent-color:#0176D3;" oninput="recalcCrmLead()">
          </div>

          <div>
            <div style="display:flex;justify-content:space-between;font-size:12.5px;margin-bottom:5px;">
              <span style="color:#5C5C5C;font-weight:600;">Target Note Rate (%):</span>
              <strong class="mono" id="lbl-target-rate" style="color:#059669;">5.875%</strong>
            </div>
            <input type="range" id="sl-rate" min="5.125" max="6.750" step="0.125" value="5.875" style="width:100%;accent-color:#059669;" oninput="recalcCrmLead()">
          </div>

          <div style="background:#F3F2F2;border-radius:6px;padding:12px;font-size:12.5px;line-height:1.5;">
            <div style="font-weight:700;color:#181818;margin-bottom:4px;">Net Benefit Check (TX 50(f)(2) Compliant):</div>
            <div id="net-benefit-summary" style="color:#444444;">
              Drops rate by <strong>1.500%</strong>, saving <strong>$480/mo</strong> ($5,760/yr) with zero prepayment penalty and 8.2-month closing cost recapture.
            </div>
          </div>
        </div>
      </div>
    </aside>

    <!-- CENTER COLUMN: MULTI-CHANNEL COMPOSER TABS & ACTIVITY TIMELINE -->
    <main>
      <div class="crm-card">
        <div class="crm-card-header">
          <span>✉️ Multi-Channel Follow-Up Composer</span>
          <button class="sf-btn-voice" onclick="playVoicemailClip(this)">
            🔊 Listen to Outbound Voice Voicemail (Gemini 3.8 Live · Puck HD)
          </button>
        </div>

        <div class="tab-bar">
          <button class="tab-btn active" onclick="switchComposerTab('email', this)">Email Sequence (3-Touch)</button>
          <button class="tab-btn" onclick="switchComposerTab('sms', this)">SMS Outreach</button>
          <button class="tab-btn" onclick="switchComposerTab('voice', this)">Voice Script (Puck HD)</button>
        </div>

        <!-- TAB 1: EMAIL SEQUENCE -->
        <div id="tab-email" class="tab-panel active">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;padding-bottom:10px;border-bottom:1px solid #E5E5E5;">
            <div>
              <div style="font-size:12px;color:#5C5C5C;">Subject Line:</div>
              <div id="email-subj" style="font-size:14px;font-weight:700;color:#181818;">
                David — Your Austin 78704 Rate Alert hit 5.875% ($480/mo savings unlocked)
              </div>
            </div>
            <span class="mono" id="active-model-pill" style="font-size:11px;background:#E8F4FF;color:#0176D3;padding:4px 8px;border-radius:4px;font-weight:700;">gemini-4-argon</span>
          </div>

          <div id="email-body-box" style="font-size:13.5px;line-height:1.65;color:#2B2826;background:#FAF9F8;border:1px solid #DDDBDA;border-radius:6px;padding:16px;">
            Hi David,<br><br>
            Great news from the Rocket Mortgage Austin Refi Desk — the 30-year fixed rate alert you set for your home in <strong>78704</strong> just crossed your target threshold at <strong>5.875%</strong> (down 150 bps from your current <strong>7.375%</strong> note rate).<br><br>
            On your <strong>$485,000 balance</strong>, stepping down from 7.375% ($3,349/mo) to <strong>5.875% ($2,869/mo)</strong> puts <strong>$480 per month ($5,760/year)</strong> right back in your pocket. With your verified <strong>742 FICO score</strong>, you qualify for our automated property appraisal waiver and streamlined Texas rate-and-term lock.<br><br>
            Would you like me to hold this 5.875% lock window for 15 minutes this afternoon? Simply reply <strong>"LOCK"</strong> or click below to pick a call time.
          </div>

          <div style="margin-top:12px;display:flex;justify-content:space-between;align-items:center;">
            <span style="font-size:12px;color:#5C5C5C;">✓ Includes NMLS #3030 & TILA Reg Z APR footer</span>
            <button class="sf-btn-primary" onclick="markOutreachDispatched('Email Sequence #1 Queued in Salesforce Marketing Cloud')">
              Send Day-1 Email & Arm Drip Sequence
            </button>
          </div>
        </div>

        <!-- TAB 2: SMS OUTREACH -->
        <div id="tab-sms" class="tab-panel">
          <div style="background:#F3F2F2;border-radius:12px;padding:16px;max-width:480px;border:1px solid #DDDBDA;">
            <div style="font-size:11px;color:#5C5C5C;font-weight:700;margin-bottom:6px;">SMS TO: (512) 555-0194 · TCPA OPT-IN VERIFIED</div>
            <div id="sms-body-box" style="background:#0176D3;color:#FFFFFF;padding:13px 16px;border-radius:14px 14px 14px 4px;font-size:13.5px;line-height:1.5;">
              Hi David! This is Alex at Rocket Mortgage. Your Austin refi rate alert just triggered: we can drop your $485,000 loan from 7.375% down to 5.875%, saving you ~$480/mo ($5,760/yr) with your 742 FICO. Want me to text over the 1-page breakdown or lock this rate today? Reply STOP to opt out.
            </div>
          </div>
          <div style="margin-top:12px;">
            <button class="sf-btn-primary" onclick="markOutreachDispatched('Two-Way SMS Dispatched via Twilio/Salesforce')">
              Send Instant SMS to (512) 555-0194
            </button>
          </div>
        </div>

        <!-- TAB 3: VOICE SCRIPT -->
        <div id="tab-voice" class="tab-panel">
          <div style="font-size:12px;font-weight:700;color:#0176D3;text-transform:uppercase;margin-bottom:8px;">
            🎙️ Outbound Banker / AI Voice Drop Script (Gemini 3.8 Live · Voice: Puck HD)
          </div>
          <div id="voice-script-box" style="font-size:13.5px;line-height:1.65;color:#181818;background:#FAF9F8;border:1px solid #DDDBDA;border-radius:6px;padding:16px;">
            "Hey David, this is Alex calling from the Rocket Mortgage Rate Watch desk here in Austin. I'm calling because the rate alert on your four hundred eighty-five thousand dollar mortgage just hit five point eight seven five percent—which is a full point and a half below your current seven point three seven five percent rate. That drops your principal and interest payment by about four hundred eighty dollars every single month, or over fifty-seven hundred dollars a year. Because your credit score is a strong seven forty-two, we already have an appraisal waiver lined up. Give me a quick text back or tap the link in your email so we can lock this in before the market moves!"
          </div>
        </div>
      </div>

      <!-- CRM ACTIVITY TIMELINE -->
      <div class="crm-card">
        <div class="crm-card-header">
          <span>🕒 Lead Activity Timeline & Engagement Log</span>
          <span id="dispatch-toast" style="font-size:12px;color:#059669;font-weight:700;"></span>
        </div>
        <div class="crm-card-body">
          <div class="timeline-item">
            <div class="timeline-dot"></div>
            <div style="font-size:12.5px;font-weight:700;color:#181818;">Rate Watch Alert Triggered (-150 bps Threshold Crossed)</div>
            <div style="font-size:12px;color:#5C5C5C;margin-top:2px;">Today, 9:14 AM CDT · Automated Pricing Engine matched 742 FICO @ 5.875% ($480/mo savings)</div>
          </div>
          <div class="timeline-item">
            <div class="timeline-dot" style="background:#059669;"></div>
            <div style="font-size:12.5px;font-weight:700;color:#181818;">Soft-Pull Credit & Property AVM Refreshed</div>
            <div style="font-size:12px;color:#5C5C5C;margin-top:2px;">Today, 9:14 AM CDT · Travis County AVM $640,000 (75.7% LTV · Appraisal Waiver Eligible)</div>
          </div>
          <div class="timeline-item" style="border-left-color:transparent;padding-bottom:0;">
            <div class="timeline-dot" style="background:#64748B;"></div>
            <div style="font-size:12.5px;font-weight:700;color:#181818;">Borrower Opted In to Rocket Rate Drop Alerts</div>
            <div style="font-size:12px;color:#5C5C5C;margin-top:2px;">Oct 18, 2025 · Signed TCPA SMS/Voice Consent Form #TCPA-99201-TX</div>
          </div>
        </div>
      </div>
    </main>

    <!-- RIGHT COLUMN: DEAL STAGE PIPELINE, TCPA CHECKLIST & VERTEX AI CTA -->
    <aside>
      <div class="crm-card">
        <div class="crm-card-header">
          <span>🚀 Deal Stage Pipeline</span>
        </div>
        <div class="crm-card-body">
          <div class="stage-pill completed" onclick="setDealStage(0)">
            <span>1. Rate Alert Triggered</span>
            <span>✓ Done</span>
          </div>
          <div class="stage-pill current" id="stage-1" onclick="setDealStage(1)">
            <span>2. Outreach Sent</span>
            <span>In Progress</span>
          </div>
          <div class="stage-pill" id="stage-2" onclick="setDealStage(2)">
            <span>3. Lock Scheduled</span>
            <span>Pending</span>
          </div>

          <button class="sf-btn-primary" id="gen-seq-btn" onclick="window.runLiveVertexAI()" style="width:100%;margin-top:10px;padding:12px;">
            ✨ Generate Follow-Up Sequence
          </button>
        </div>
      </div>

      <div class="crm-card">
        <div class="crm-card-header">
          <span>🛡️ TCPA & Reg Z Compliance Checklist</span>
          <span style="font-size:11px;background:#ECFDF5;color:#059669;padding:2px 8px;border-radius:4px;font-weight:700;">4/4 Passed</span>
        </div>
        <div class="crm-card-body" style="display:flex;flex-direction:column;gap:10px;font-size:12.5px;">
          <label style="display:flex;align-items:flex-start;gap:8px;cursor:pointer;">
            <input type="checkbox" checked style="margin-top:3px;accent-color:#0176D3;">
            <span><strong>TCPA Prior Express Written Consent:</strong> Verified on file (#TCPA-99201-TX).</span>
          </label>
          <label style="display:flex;align-items:flex-start;gap:8px;cursor:pointer;">
            <input type="checkbox" checked style="margin-top:3px;accent-color:#0176D3;">
            <span><strong>Borrower Local Calling Window:</strong> 9:15 AM – 8:00 PM CDT (Austin, TX Safe Window).</span>
          </label>
          <label style="display:flex;align-items:flex-start;gap:8px;cursor:pointer;">
            <input type="checkbox" checked style="margin-top:3px;accent-color:#0176D3;">
            <span><strong>National & Internal DNC Scrub:</strong> Cleared 60 seconds ago.</span>
          </label>
          <label style="display:flex;align-items:flex-start;gap:8px;cursor:pointer;">
            <input type="checkbox" checked style="margin-top:3px;accent-color:#0176D3;">
            <span><strong>TILA Reg Z § 1026.24 APR Pairing:</strong> APR disclosed alongside note rate.</span>
          </label>
        </div>
      </div>
    </aside>

  </div>

  {controls}

  <script>
    function calcMonthlyPI(principal, annualRate) {{
      const r = (annualRate / 100) / 12;
      return principal * (r * Math.pow(1 + r, 360)) / (Math.pow(1 + r, 360) - 1);
    }}

    function switchComposerTab(tabId, btnEl) {{
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
      btnEl.classList.add('active');
      document.getElementById('tab-' + tabId).classList.add('active');
    }}

    function setDealStage(idx) {{
      const s1 = document.getElementById('stage-1');
      const s2 = document.getElementById('stage-2');
      if (idx === 1) {{
        s1.className = 'stage-pill current';
        s1.children[1].innerText = 'In Progress';
        s2.className = 'stage-pill';
        s2.children[1].innerText = 'Pending';
      }} else if (idx === 2) {{
        s1.className = 'stage-pill completed';
        s1.children[1].innerText = '✓ Sent';
        s2.className = 'stage-pill current';
        s2.children[1].innerText = 'Locked 4:00 PM';
      }}
    }}

    function markOutreachDispatched(msg) {{
      const toast = document.getElementById('dispatch-toast');
      toast.innerText = '✓ ' + msg;
      setDealStage(2);
    }}

    function recalcCrmLead() {{
      const loan = parseFloat(document.getElementById('sl-loan').value);
      const targetRate = parseFloat(document.getElementById('sl-rate').value);
      const curRate = 7.375;

      const curPi = Math.round(calcMonthlyPI(loan, curRate));
      const newPi = Math.round(calcMonthlyPI(loan, targetRate));
      const moSav = Math.max(0, curPi - newPi);
      const yrSav = moSav * 12;

      document.getElementById('lbl-loan-bal').innerText = '$' + loan.toLocaleString();
      document.getElementById('lbl-target-rate').innerText = targetRate.toFixed(3) + '%';
      document.getElementById('hdr-loan-amt').innerText = '$' + loan.toLocaleString();
      document.getElementById('hdr-target-rate').innerText = targetRate.toFixed(3) + '% ($' + newPi.toLocaleString() + '/mo)';
      document.getElementById('hdr-mo-savings').innerText = '+$' + moSav.toLocaleString() + ' / mo ($' + yrSav.toLocaleString() + '/yr)';
      document.getElementById('contact-target-rate').innerText = targetRate.toFixed(3) + '% (30-Yr Fixed)';

      const dropBps = Math.round((curRate - targetRate) * 100);
      document.getElementById('net-benefit-summary').innerHTML =
        `Drops rate by <strong>${{(curRate - targetRate).toFixed(3)}}% (${{dropBps}} bps)</strong>, saving <strong>$${{moSav.toLocaleString()}}/mo</strong> ($${{yrSav.toLocaleString()}}/yr) with streamlined appraisal waiver.`;

      document.getElementById('email-subj').innerText =
        `David — Your Austin 78704 Rate Alert hit ${{targetRate.toFixed(3)}}% ($${{moSav.toLocaleString()}}/mo savings unlocked)`;

      document.getElementById('sms-body-box').innerText =
        `Hi David! This is Alex at Rocket Mortgage. Your Austin refi rate alert just triggered: we can drop your $${{loan.toLocaleString()}} loan from 7.375% down to ${{targetRate.toFixed(3)}}%, saving you ~$${{moSav.toLocaleString()}}/mo ($${{yrSav.toLocaleString()}}/yr) with your 742 FICO. Want me to text over the 1-page breakdown or lock this rate today? Reply STOP to opt out.`;
    }}

    function playVoicemailClip(btnEl) {{
      const scriptText = document.getElementById('voice-script-box').innerText.replace(/"/g, '');
      window.playLiveCallClip(
        scriptText,
        'Puck',
        'Alex · Rocket Mortgage Austin Refi Specialist',
        btnEl
      );
    }}

    window.runLiveVertexAI = async function() {{
      const btn = document.getElementById('gen-seq-btn');
      const model = window.getSelectedModel();
      btn.innerText = '⏳ Generating Sequence (' + model + ')...';
      document.getElementById('active-model-pill').innerText = model;

      const loan = parseFloat(document.getElementById('sl-loan').value);
      const targetRate = parseFloat(document.getElementById('sl-rate').value);

      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '1.2',
            model: model,
            params: {{
              borrower: 'David Chen (Austin, TX)',
              loan_amount: loan,
              base_rate: 7.375,
              buydown_rate: targetRate,
              buydown_pts: 0.0
            }}
          }})
        }});
        const data = await res.json();
        document.getElementById('active-model-pill').innerText = data.model_used || model;
        if (data.structured_data && (data.structured_data.email_body || data.structured_data.executive_summary)) {{
          document.getElementById('email-body-box').innerHTML = data.structured_data.email_body || data.structured_data.executive_summary;
        }} else if (data.output) {{
          document.getElementById('email-body-box').innerHTML = data.output.replace(/\\n/g, '<br>');
        }}
      }} catch (e) {{
        console.error(e);
      }} finally {{
        btn.innerText = '✨ Generate Follow-Up Sequence';
      }}
    }};
  </script>
</body>
</html>"""
