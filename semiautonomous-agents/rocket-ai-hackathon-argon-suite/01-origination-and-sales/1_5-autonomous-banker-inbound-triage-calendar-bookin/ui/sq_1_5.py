# -*- coding: utf-8 -*-
"""Square 1.5: Autonomous Banker Inbound Triage & Calendar Dispatcher — Standalone UI Design File.
Visual Archetype: Air-Traffic Control Live Webhook Switchboard & NMLS Dispatch Radar
(Radar Midnight #040D1A, Neon Cyan #00F5D4, Amber Alert #FBBF24, Chakra Petch + Fira Code fonts,
Angled Tactical Buttons, Live Redfin Tour Webhook Stream -> NMLS Matcher -> Banker Calendar Grid)."""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_1_5(auth_token: str) -> str:
    controls = render_floating_control_bar_and_drawer("1.5", auth_token)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Antigravity MCP Dispatch Radar | Redfin -> Rocket Banker Switchboard</title>
  <link href="https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;600;700&family=Fira+Code:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Chakra Petch', sans-serif;
      background: radial-gradient(circle at 50% 0%, #091E3A 0%, #040D1A 70%);
      color: #E2F1FF;
      min-height: 100vh;
      padding-bottom: 80px;
    }}
    .mono {{ font-family: 'Fira Code', monospace; }}

    .radar-header {{
      background: rgba(4, 13, 26, 0.9);
      border-bottom: 1px solid rgba(0, 245, 212, 0.3);
      padding: 16px 28px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .tactical-btn {{
      background: linear-gradient(135deg, #00F5D4, #00BBF9);
      color: #040D1A;
      border: none;
      padding: 10px 20px;
      clip-path: polygon(8px 0, 100% 0, calc(100% - 8px) 100%, 0 100%);
      font-family: 'Chakra Petch', sans-serif;
      font-weight: 700;
      font-size: 13px;
      cursor: pointer;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    .switchboard-grid {{
      max-width: 1340px;
      margin: 24px auto;
      padding: 0 24px;
      display: grid;
      grid-template-columns: 380px 1fr 390px;
      gap: 20px;
    }}
    @media (max-width: 1120px) {{
      .switchboard-grid {{ grid-template-columns: 1fr; }}
    }}
    .radar-panel {{
      background: rgba(8, 22, 42, 0.85);
      border: 1px solid rgba(0, 245, 212, 0.25);
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 0 30px rgba(0, 245, 212, 0.06);
    }}
    .webhook-item {{
      background: #061326;
      border: 1px solid #153258;
      border-left: 4px solid #00F5D4;
      padding: 12px;
      border-radius: 8px;
      margin-bottom: 10px;
      cursor: pointer;
      transition: 0.2s;
    }}
    .webhook-item:hover, .webhook-item.active {{
      background: #0C2342;
      border-color: #00F5D4;
    }}
    .slot-btn {{
      background: #071930;
      border: 1px solid #1B3B68;
      color: #E2F1FF;
      padding: 10px;
      border-radius: 8px;
      font-family: 'Fira Code', monospace;
      font-size: 11.5px;
      cursor: pointer;
      text-align: left;
    }}
    .slot-btn.booked {{
      background: rgba(0, 245, 212, 0.15);
      border-color: #00F5D4;
      color: #00F5D4;
      font-weight: 700;
    }}
  </style>
</head>
<body>

  <header class="radar-header">
    <div style="display:flex;align-items:center;gap:14px;">
      <div style="width:14px;height:14px;border-radius:50%;background:#00F5D4;box-shadow:0 0 14px #00F5D4;"></div>
      <div>
        <div style="font-size:19px;font-weight:700;letter-spacing:0.04em;color:#00F5D4;">ANTIGRAVITY MCP // AUTONOMOUS LEAD TRIAGE & NMLS SWITCHBOARD</div>
        <div class="mono" style="font-size:11px;color:#7FA6C9;">REDFIN TOUR WEBHOOK -> ROCKET MONEY PLAID ASSETS -> STATE NMLS ROUTING -> MS GRAPH CALENDAR</div>
      </div>
    </div>

    <div style="display:flex;align-items:center;gap:12px;">
      <div class="mono" style="background:#06152B;padding:6px 12px;border:1px solid rgba(0,245,212,0.35);border-radius:6px;font-size:11px;">
        MODEL:
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)" style="background:transparent;color:#00F5D4;font-weight:700;border:none;outline:none;font-family:'Fira Code',monospace;font-size:11px;cursor:pointer;">
          <option value="gemini-3.8-flash" style="background:#040D1A;">gemini-3.8-flash</option>
          <option value="gemini-4-argon" style="background:#040D1A;">gemini-4-argon</option>
        </select>
      </div>
      <button class="tactical-btn" onclick="window.runLiveVertexAI()" id="dispatch-btn">⚡ Execute MCP Triage & Book Slot</button>
    </div>
  </header>

  <div class="switchboard-grid">
    <!-- COLUMN 1: LIVE REDFIN INBOUND WEBHOOK STREAM -->
    <section class="radar-panel">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
        <span style="font-weight:700;font-size:14px;color:#00F5D4;text-transform:uppercase;">📡 1. Live Redfin Tour Webhooks</span>
        <span class="mono" style="font-size:10px;background:rgba(251,191,36,0.2);color:#FBBF24;padding:3px 8px;border-radius:4px;">SLA &lt; 800ms</span>
      </div>

      <div class="webhook-item active" onclick="loadWebhook(585000, 215000, 94500, 'MI', this)">
        <div class="mono" style="display:flex;justify-content:space-between;font-size:11px;color:#FBBF24;font-weight:700;">
          <span>🔥 URGENCY: 98/100</span>
          <span>T-MINUS 44 HRS</span>
        </div>
        <div style="font-weight:700;font-size:14px;margin:4px 0;">Chloe & Liam Sterling • Birmingham, MI</div>
        <div class="mono" style="font-size:11px;color:#94B8D7;">Redfin Tour Booked: $585,000 • No Pre-Approval on File!</div>
      </div>

      <div class="webhook-item" onclick="loadWebhook(740000, 265000, 148000, 'TX', this)">
        <div class="mono" style="display:flex;justify-content:space-between;font-size:11px;color:#00F5D4;font-weight:700;">
          <span>⚡ URGENCY: 94/100</span>
          <span>T-MINUS 28 HRS</span>
        </div>
        <div style="font-weight:700;font-size:14px;margin:4px 0;">Mateo Rivera • Austin, TX (78704)</div>
        <div class="mono" style="font-size:11px;color:#94B8D7;">Redfin Tour Booked: $740,000 • Rocket Money Vault: $148k</div>
      </div>

      <div class="webhook-item" onclick="loadWebhook(495000, 178000, 62000, 'FL', this)">
        <div class="mono" style="display:flex;justify-content:space-between;font-size:11px;color:#38BDF8;font-weight:700;">
          <span>📡 URGENCY: 91/100</span>
          <span>T-MINUS 60 HRS</span>
        </div>
        <div style="font-weight:700;font-size:14px;margin:4px 0;">Hannah Chen • Tampa, FL</div>
        <div class="mono" style="font-size:11px;color:#94B8D7;">Redfin Offer Intent: $495,000 • 764 FICO Soft-Pull</div>
      </div>

      <!-- Sliders -->
      <div style="margin-top:16px;padding-top:14px;border-top:1px solid rgba(0,245,212,0.2);">
        <div class="mono" style="font-size:11px;color:#00F5D4;margin-bottom:8px;">🎛️ Webhook Payload Simulator</div>
        <div style="margin-bottom:10px;">
          <div class="mono" style="display:flex;justify-content:space-between;font-size:11px;">
            <span>Redfin Listing Price:</span>
            <strong id="lbl-price" style="color:#00F5D4;">$585,000</strong>
          </div>
          <input type="range" id="sl-price" min="300000" max="950000" step="5000" value="585000" style="width:100%;accent-color:#00F5D4;" oninput="recalcTriage()">
        </div>
        <div>
          <div class="mono" style="display:flex;justify-content:space-between;font-size:11px;">
            <span>Rocket Money Verified Liquid Assets:</span>
            <strong id="lbl-assets" style="color:#FBBF24;">$94,500</strong>
          </div>
          <input type="range" id="sl-assets" min="25000" max="220000" step="2500" value="94500" style="width:100%;accent-color:#FBBF24;" oninput="recalcTriage()">
        </div>
      </div>
    </section>

    <!-- COLUMN 2: MCP STATE NMLS MATCHER & SANDBOX 1003 PRE-FILL -->
    <section class="radar-panel" style="display:flex;flex-direction:column;gap:14px;">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <span style="font-weight:700;font-size:14px;color:#00F5D4;text-transform:uppercase;">🧭 2. Antigravity MCP NMLS Router & Buying Power</span>
        <span class="mono" id="mcp-profile-id" style="font-size:11px;color:#00F5D4;">RKT-1003-SBX-20261013-8841</span>
      </div>

      <div style="background:#051122;border:1px solid #16365F;border-radius:10px;padding:16px;">
        <div class="mono" style="font-size:10px;color:#7FA6C9;text-transform:uppercase;">Instant Pre-Computed Buying Power</div>
        <div class="mono" style="font-size:20px;font-weight:700;color:#00F5D4;margin-top:4px;" id="val-buying-power">
          Pre-Approved up to $680,000 | Target: $585,000 (86.3% LTV)
        </div>
      </div>

      <div style="background:#051122;border:1px solid #16365F;border-radius:10px;padding:16px;">
        <div class="mono" style="font-size:10px;color:#FBBF24;text-transform:uppercase;">Matched State-Licensed Senior Rocket Banker</div>
        <div style="font-size:17px;font-weight:700;color:#FFF;margin-top:4px;" id="val-banker">
          Brandon Kowalski (Sr. Premier Banker • NMLS #1498212)
        </div>
        <div class="mono" style="font-size:11px;color:#94B8D7;margin-top:4px;">
          Active State License Verified • 94.2% Redfin Tour Conversion • Sub-5m Response
        </div>
      </div>

      <div style="background:#051122;border:1px solid #16365F;border-radius:10px;padding:16px;flex:1;">
        <div class="mono" style="font-size:10px;color:#38BDF8;text-transform:uppercase;margin-bottom:6px;">📲 Instant Borrower SMS & Banker Whisper Brief</div>
        <div id="sms-preview-box" style="font-size:13px;line-height:1.6;color:#E2F1FF;">
          "Hi Chloe & Liam! Saw your Redfin tour for Saturday in Birmingham ($585k). Because your Rocket Money Vault shows $94.5k liquid, you're already eligible for Verified Pre-Approval up to $680k. I locked a 15-min video slot with Sr. MI Banker Brandon Kowalski today at 4:30 PM EDT so you walk into Saturday's tour with a cash-backed offer letter!"
        </div>
      </div>
    </section>

    <!-- COLUMN 3: MICROSOFT GRAPH CALENDAR DISPATCH BOARD -->
    <section class="radar-panel">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
        <span style="font-weight:700;font-size:14px;color:#00F5D4;text-transform:uppercase;">📅 3. Banker Live Calendar Slots</span>
        <span class="mono" style="font-size:10px;color:#10B981;">MS GRAPH API CONNECTED</span>
      </div>

      <div style="display:grid;grid-template-columns:1fr;gap:10px;">
        <button class="slot-btn" onclick="bookCalendarSlot(this, 'Today • 3:00 PM EDT')">
          <div>🕒 Today • 3:00 PM EDT (Available)</div>
          <div style="font-size:10px;color:#7FA6C9;">15-Min Redfin Fast-Track Video Pre-Approval</div>
        </button>
        <button class="slot-btn booked" id="default-slot" onclick="bookCalendarSlot(this, 'Today • 4:30 PM EDT')">
          <div>✅ Today • 4:30 PM EDT (AUTO-BOOKED BY MCP)</div>
          <div style="font-size:10px;color:#E2F1FF;">Chloe & Liam Sterling + Redfin Agent Co-Invite</div>
        </button>
        <button class="slot-btn" onclick="bookCalendarSlot(this, 'Today • 5:15 PM EDT')">
          <div>🕒 Today • 5:15 PM EDT (Available)</div>
          <div style="font-size:10px;color:#7FA6C9;">15-Min Redfin Fast-Track Video Pre-Approval</div>
        </button>
        <button class="slot-btn" onclick="bookCalendarSlot(this, 'Tomorrow • 9:00 AM EDT')">
          <div>🕒 Tomorrow • 9:00 AM EDT (Available)</div>
          <div style="font-size:10px;color:#7FA6C9;">Pre-Tour Same-Day Verified Approval Desk</div>
        </button>
      </div>

      <div style="margin-top:16px;padding:12px;border-radius:8px;background:rgba(0,245,212,0.08);border:1px solid rgba(0,245,212,0.3);font-size:12px;" id="slot-confirm-banner">
        <strong>✓ Calendar Invite Dispatched:</strong> Today at 4:30 PM EDT with Teams Link + Pre-Filled 1003 Sandbox Packet.
      </div>
    </section>
  </div>

  {controls}

  <script>
    function loadWebhook(price, inc, assets, state, el) {{
      document.querySelectorAll('.webhook-item').forEach(i => i.classList.remove('active'));
      el.classList.add('active');
      document.getElementById('sl-price').value = price;
      document.getElementById('sl-assets').value = assets;
      recalcTriage();
    }}

    function bookCalendarSlot(btn, label) {{
      document.querySelectorAll('.slot-btn').forEach(b => b.classList.remove('booked'));
      btn.classList.add('booked');
      document.getElementById('slot-confirm-banner').innerHTML =
        `<strong>✓ Calendar Invite Dispatched:</strong> ${{label}} with Microsoft Teams Link + Pre-Filled 1003 Sandbox Packet.`;
    }}

    async function recalcTriage() {{
      const price = parseFloat(document.getElementById('sl-price').value);
      const assets = parseFloat(document.getElementById('sl-assets').value);
      document.getElementById('lbl-price').innerText = '$' + price.toLocaleString();
      document.getElementById('lbl-assets').innerText = '$' + assets.toLocaleString();

      const res = await fetch('/api/sandbox', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{code: '1.5', action: 'triage_inbound_webhook', params: {{list_price: price, income: 215000, assets: assets}}}})
      }});
      const data = await res.json();
      if (data.ok && data.metrics) {{
        const m = data.metrics;
        document.getElementById('val-buying-power').innerText = m.computed_buying_power || '';
        document.getElementById('val-banker').innerText = m.mcp_routed_banker || '';
        document.getElementById('mcp-profile-id').innerText = m.sandbox_1003_profile_id || '';
      }}
    }}

    window.runLiveVertexAI = async function() {{
      const btn = document.getElementById('dispatch-btn');
      const model = window.getSelectedModel();
      btn.innerText = '⏳ Dispatching on ' + model + '...';
      const price = parseFloat(document.getElementById('sl-price').value);
      const assets = parseFloat(document.getElementById('sl-assets').value);
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{'Content-Type': 'application/json'}},
          body: JSON.stringify({{code: '1.5', model: model, params: {{list_price: price, income: 215000, assets: assets}}}})
        }});
        const data = await res.json();
        if (data.structured_data && (data.structured_data.instant_borrower_sms || data.structured_data.executive_summary)) {{
          document.getElementById('sms-preview-box').innerHTML = data.structured_data.instant_borrower_sms || data.structured_data.executive_summary;
        }} else if (data.output) {{
          document.getElementById('sms-preview-box').innerText = data.output;
        }}
      }} catch (e) {{}}
      finally {{
        btn.innerText = '⚡ Execute MCP Triage & Book Slot';
      }}
    }};
  </script>
</body>
</html>"""
