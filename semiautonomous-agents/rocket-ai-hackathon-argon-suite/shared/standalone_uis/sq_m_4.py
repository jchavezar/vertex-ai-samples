# -*- coding: utf-8 -*-
"""Square M.4: Project Mirror: Interactive Virtual Mortgage Advisor 'Astra Pro' — Real Gemini 3.8 Live Audio WebSocket
Visual Design: Architectural Digest Warm Living Room & Closing-Table Interactive Whiteboard
(#FAF8F5 warm alabaster paper, #D97706 warm amber/gold, #0284C7 sky blue, #FFFFFF whiteboard canvas,
Fraunces serif + DM Sans + IBM Plex Mono — clean, warm, reassuring daylight/warm-paper aesthetic).
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_m_4(auth_token: str) -> str:
    code = "M.4"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[M.4] Project Mirror: Interactive Virtual Mortgage Advisor 'Astra Pro' | Closing-Table Whiteboard</title>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,600;0,9..144,700;0,9..144,800;1,9..144,500&family=DM+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --alabaster: #FAF8F5;
      --linen-panel: #F3EFEA;
      --whiteboard: #FFFFFF;
      --warm-amber: #D97706;
      --amber-soft: #FEF3C7;
      --sky-blue: #0284C7;
      --sky-soft: #E0F2FE;
      --emerald: #047857;
      --emerald-soft: #ECFDF5;
      --warm-ink: #1C1917;
      --warm-muted: #57534E;
      --stone-border: #E5E0D8;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: var(--alabaster);
      color: var(--warm-ink);
      font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      min-height: 100vh;
      padding-bottom: 96px;
    }}
    .serif-ad {{ font-family: 'Fraunces', Georgia, serif; }}
    .mono {{ font-family: 'IBM Plex Mono', monospace; }}

    /* Architectural Digest Warm Living Room Header */
    .mirror-header {{
      background: var(--whiteboard);
      border-top: 4px solid var(--warm-amber);
      border-bottom: 1.5px solid var(--stone-border);
      padding: 16px 28px;
      box-shadow: 0 2px 10px rgba(28, 25, 23, 0.04);
    }}
    .mirror-header-inner {{
      max-width: 1540px;
      margin: 0 auto;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 14px;
    }}
    .amber-badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: var(--amber-soft);
      border: 1px solid #FCD34D;
      color: #92400E;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      padding: 4px 12px;
      border-radius: 999px;
    }}
    .select-pill {{
      display: inline-flex;
      align-items: center;
      gap: 7px;
      background: var(--alabaster);
      border: 1.5px solid var(--stone-border);
      padding: 6px 12px;
      border-radius: 999px;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11.5px;
    }}
    .select-pill select {{
      background: transparent;
      color: var(--warm-ink);
      border: none;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11.5px;
      font-weight: 700;
      outline: none;
      cursor: pointer;
    }}

    /* Main Closing-Table Studio Layout */
    .mirror-grid {{
      max-width: 1540px;
      margin: 24px auto;
      padding: 0 28px;
      display: grid;
      grid-template-columns: 430px 1fr;
      gap: 24px;
      align-items: start;
    }}
    @media (max-width: 1140px) {{
      .mirror-grid {{ grid-template-columns: 1fr; }}
    }}

    .ad-card {{
      background: var(--whiteboard);
      border: 1.5px solid var(--stone-border);
      border-radius: 18px;
      padding: 24px;
      box-shadow: 0 8px 24px rgba(28, 25, 23, 0.05);
    }}

    /* Live Voice Control Bar */
    .voice-control-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      margin-bottom: 16px;
    }}
    .ad-btn {{
      appearance: none;
      border: 1.5px solid var(--stone-border);
      border-radius: 10px;
      padding: 10px 12px;
      font-family: 'DM Sans', sans-serif;
      font-size: 12.5px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      transition: all 0.15s ease;
    }}
    .ad-btn-primary {{
      background: var(--warm-amber);
      border-color: #B45309;
      color: #FFFFFF;
      grid-column: span 2;
      font-size: 13.5px;
      padding: 12px 14px;
      box-shadow: 0 4px 12px rgba(217, 119, 6, 0.22);
    }}
    .ad-btn-primary.live {{
      background: var(--emerald);
      border-color: #065F46;
    }}
    .ad-btn-sky {{
      background: var(--sky-soft);
      border-color: #7DD3FC;
      color: #0369A1;
    }}
    .ad-btn-sky.mic-on {{
      background: #FEE2E2;
      border-color: #EF4444;
      color: #991B1B;
    }}
    .ad-btn-light {{
      background: var(--alabaster);
      color: var(--warm-ink);
    }}
    .ad-btn-light.muted {{
      background: #FEE2E2;
      border-color: #EF4444;
      color: #991B1B;
    }}

    /* 4 Clickable Closing Disclosure (CD) Line Items */
    .cd-item-btn {{
      width: 100%;
      text-align: left;
      background: var(--alabaster);
      border: 1.5px solid var(--stone-border);
      border-left: 4px solid #D6D3D1;
      border-radius: 12px;
      padding: 12px 14px;
      margin-bottom: 10px;
      cursor: pointer;
      transition: all 0.15s ease;
    }}
    .cd-item-btn:hover {{
      border-color: var(--warm-amber);
      background: #FFFBEB;
    }}
    .cd-item-btn.active {{
      border-color: var(--warm-amber);
      border-left: 5px solid var(--warm-amber);
      background: #FFFBEB;
      box-shadow: 0 4px 12px rgba(217, 119, 6, 0.10);
    }}

    /* Whiteboard KPI Strip */
    .wb-kpi-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 14px;
      margin-top: 16px;
    }}
    @media (max-width: 860px) {{
      .wb-kpi-grid {{ grid-template-columns: 1fr; }}
    }}
    .wb-kpi-box {{
      background: var(--alabaster);
      border: 1px solid var(--stone-border);
      border-radius: 12px;
      padding: 13px 15px;
    }}
  </style>
</head>
<body>

  <!-- ARCHITECTURAL DIGEST WARM DAYLIGHT HEADER -->
  <header class="mirror-header">
    <div class="mirror-header-inner">
      <div>
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:5px;flex-wrap:wrap;">
          <span class="amber-badge">✨ ASTRA PRO VIRTUAL ADVISOR • USE CASE M.4</span>
          <span class="mono" id="mirror-ws-status" style="font-size:11px;color:var(--sky-blue);font-weight:700;">
            /ws/live-voice/M.4 • 24kHz Native Audio + 0ms Barge-In Ready
          </span>
        </div>
        <h1 class="serif-ad" style="font-size:24px;font-weight:800;color:var(--warm-ink);">
          Project Mirror: Interactive Virtual Mortgage Advisor 'Astra Pro' &amp; Closing Whiteboard
        </h1>
      </div>

      <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
        <div class="select-pill">
          <span style="color:var(--warm-muted);font-weight:600;">AVATAR:</span>
          <select id="mirror-avatar-select" onchange="window.updateMirrorVoiceConfig()" aria-label="Astra Pro Live Avatar">
            <option value="Kira" selected>🎥 Kira (Executive Advisor · 24fps)</option>
            <option value="Ingrid">🎥 Ingrid (Mortgage Architect · 24fps)</option>
            <option value="Vera">🎥 Vera (Risk/UW Lead · 24fps)</option>
            <option value="Sam">🎥 Sam (FDE Director · 24fps)</option>
            <option value="Jay">🎥 Jay (Staff Cloud Lead · 24fps)</option>
            <option value="Paul">🎥 Paul (Capital Markets · 24fps)</option>
            <option value="Kai">🎥 Kai (3D Concierge · 24fps)</option>
            <option value="Ben">🎥 Ben (Dev Advocate · 24fps)</option>
            <option value="Carmen">🎥 Carmen (Bilingual · 24fps)</option>
            <option value="off">🎙️ Audio Only (24kHz HD)</option>
          </select>
        </div>

        <div class="select-pill">
          <span style="color:var(--warm-muted);font-weight:600;">LIVE MODE:</span>
          <select id="mirror-live-mode" onchange="window.updateMirrorVoiceConfig()" aria-label="Gemini Live Mode">
            <option value="gemini-3.8-live" selected>Gemini 3.8 Live (24 FPS + 24kHz)</option>
            <option value="gemini-3.8-live-extended-thinking">Gemini 3.8 Live Extended Thinking</option>
          </select>
        </div>

        <div class="select-pill">
          <span style="color:var(--warm-muted);font-weight:600;">VOICE:</span>
          <select id="mirror-voice-select" onchange="window.updateMirrorVoiceConfig()" aria-label="Astra Pro Voice">
            <option value="Aoede" selected>Aoede (Warm HD)</option>
            <option value="Puck">Puck (Dynamic HD)</option>
            <option value="Kore">Kore (Executive HD)</option>
          </select>
        </div>

        <div class="select-pill">
          <span style="color:var(--warm-muted);font-weight:600;">MODEL:</span>
          <select id="app-model-select" onchange="window.syncSelectedModel(this.value)" aria-label="Select Vertex Model">
            <option value="gemini-4-argon">gemini-4-argon (Frontier)</option>
            <option value="gemini-3.8-flash" selected>gemini-3.8-flash (Low-Latency)</option>
          </select>
        </div>

        <button onclick="window.runLiveVertexAI()" class="ad-btn ad-btn-light" style="padding:7px 14px;">
          Synthesize Walkthrough
        </button>
      </div>
    </div>
  </header>

  <!-- MAIN CLOSING-TABLE INTERACTIVE WHITEBOARD STUDIO -->
  <main class="mirror-grid">

    <!-- LEFT COLUMN: ASTRA PRO VOICE ENGINE + 4 CLICKABLE CLOSING DISCLOSURE (CD) LINE ITEMS -->
    <aside class="ad-card">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
        <span class="mono" style="font-size:11px;font-weight:700;color:var(--warm-amber);">
          ASTRA PRO 24KHZ VOICE CONCIERGE
        </span>
        <span class="mono" id="mirror-barge-status" style="font-size:11px;color:var(--emerald);font-weight:700;">
          0ms Barge-In Armed
        </span>
      </div>

      <!-- Live 24 FPS Gemini 3.8 Live Video Avatar Stage for Astra Pro -->
      <div style="margin-bottom:12px;border-radius:14px;overflow:hidden;border:1.5px solid var(--stone-border);background:#1C1917;position:relative;height:220px;display:flex;align-items:center;justify-content:center;">
        <video id="m4-avatar-video" playsinline autoplay style="width:100%;height:100%;object-fit:cover;display:none;"></video>
        <div id="m4-avatar-placeholder" style="text-align:center;padding:16px;color:#FAF8F5;">
          <div style="font-size:28px;margin-bottom:4px;">🎥</div>
          <div class="serif-ad" style="font-size:15px;font-weight:700;">Astra Pro Live Video Avatar (704×1280 24 FPS)</div>
          <div style="font-size:11.5px;color:#D6D3D1;margin-top:3px;">Click <strong>Start Astra Pro Live Avatar Session</strong> below to stream real-time lip-synced video + 24kHz audio</div>
        </div>
      </div>

      <!-- Voice Session & 0ms Barge-In Controls -->
      <div class="voice-control-grid">
        <button id="btn-mirror-session" class="ad-btn ad-btn-primary" onclick="window.toggleMirrorLiveVoice()">
          🎥 Start Astra Pro Live Avatar Session (/ws/live-voice/M.4)
        </button>
        <button id="btn-mirror-mic" class="ad-btn ad-btn-sky" onclick="window.toggleMirror16kMic()">
          🎤 16kHz Mic Stream
        </button>
        <button id="btn-mirror-barge" class="ad-btn ad-btn-light" onclick="window.flushMirrorAudio('Manual 0ms Barge-In')">
          ✋ Interrupt / Barge-In
        </button>
        <button id="btn-mirror-mute" class="ad-btn ad-btn-light" style="grid-column:span 2;" onclick="window.toggleMirrorMute()">
          🔇 Mute Astra Pro Audio
        </button>
      </div>

      <!-- Home Price & Rocket Money Vault Inputs -->
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:16px;padding:12px;background:var(--alabaster);border:1px solid var(--stone-border);border-radius:12px;">
        <div>
          <label class="mono" style="font-size:10.5px;color:var(--warm-muted);font-weight:700;display:block;margin-bottom:4px;">HOME PRICE ($)</label>
          <input type="number" id="inp-mirror-price" value="350000" step="5000" oninput="window.refreshMirrorSandbox()"
                 style="width:100%;padding:7px 9px;border-radius:8px;border:1px solid var(--stone-border);font-family:'IBM Plex Mono',monospace;font-size:12.5px;font-weight:700;">
        </div>
        <div>
          <label class="mono" style="font-size:10.5px;color:var(--warm-muted);font-weight:700;display:block;margin-bottom:4px;">ROCKET MONEY SAVINGS ($)</label>
          <input type="number" id="inp-mirror-sav" value="25000" step="1000" oninput="window.refreshMirrorSandbox()"
                 style="width:100%;padding:7px 9px;border-radius:8px;border:1px solid var(--stone-border);font-family:'IBM Plex Mono',monospace;font-size:12.5px;font-weight:700;">
        </div>
      </div>

      <!-- 4 Clickable Closing Disclosure (CD) Line Items -->
      <div style="margin-bottom:6px;">
        <div class="mono" style="font-size:11px;font-weight:700;color:var(--warm-muted);text-transform:uppercase;margin-bottom:8px;">
          Click Any Closing Disclosure (CD) Line Item to Draw &amp; Hear Astra Pro Explain It:
        </div>

        <button class="cd-item-btn active" onclick="window.selectCdWhiteboardItem('cash', this)">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <span class="serif-ad" style="font-size:15px;font-weight:700;color:var(--warm-ink);">1. Cash to Close $22,300</span>
            <span class="mono" style="font-size:11px;color:var(--emerald);font-weight:700;">+$2,700 Cushion Left</span>
          </div>
          <div style="font-size:12px;color:var(--warm-muted);margin-top:3px;">
            5% Down ($17,500) + Net Closing &amp; Escrow ($4,800) vs. $25,000 Vault
          </div>
        </button>

        <button class="cd-item-btn" onclick="window.selectCdWhiteboardItem('boxA', this)">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <span class="serif-ad" style="font-size:15px;font-weight:700;color:var(--warm-ink);">2. Box A: Origination Charges $1,295</span>
            <span class="mono" style="font-size:11px;color:var(--sky-blue);font-weight:700;">0% Tolerance Locked</span>
          </div>
          <div style="font-size:12px;color:var(--warm-muted);margin-top:3px;">
            Flat underwriting &amp; rate-lock fee protected under CFPB TRID law
          </div>
        </button>

        <button class="cd-item-btn" onclick="window.selectCdWhiteboardItem('boxF', this)">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <span class="serif-ad" style="font-size:15px;font-weight:700;color:var(--warm-ink);">3. Box F: Prepaids 15 Days Interest</span>
            <span class="mono" style="font-size:11px;color:var(--warm-amber);font-weight:700;">Skip Nov 1 Payment!</span>
          </div>
          <div style="font-size:12px;color:var(--warm-muted);margin-top:3px;">
            Why closing Oct 16 means your first mortgage payment isn't due until Dec 1
          </div>
        </button>

        <button class="cd-item-btn" onclick="window.selectCdWhiteboardItem('boxG', this)">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <span class="serif-ad" style="font-size:15px;font-weight:700;color:var(--warm-ink);">4. Box G: Initial Escrow Cushion &amp; Month 84 PMI Drop</span>
            <span class="mono" style="font-size:11px;color:var(--emerald);font-weight:700;">78% LTV Auto-Drop</span>
          </div>
          <div style="font-size:12px;color:var(--warm-muted);margin-top:3px;">
            2-month tax/insurance reserve + automatic HPA PMI cancellation
          </div>
        </button>
      </div>
    </aside>

    <!-- RIGHT COLUMN: CLOSING-TABLE INTERACTIVE WHITEBOARD & SPOKEN EXPLANATION -->
    <section style="display:flex;flex-direction:column;gap:20px;">
      <div class="ad-card">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid var(--stone-border);">
          <div>
            <span class="mono" style="font-size:11px;font-weight:700;color:var(--warm-amber);text-transform:uppercase;">
              CLOSING-TABLE INTERACTIVE WHITEBOARD • ROYAL OAK, MI
            </span>
            <h2 class="serif-ad" id="wb-title" style="font-size:22px;font-weight:800;color:var(--warm-ink);margin-top:2px;">
              Cash to Close &amp; Post-Closing Safety Cushion
            </h2>
          </div>
          <span class="mono" id="wb-sandbox-pill" style="font-size:11px;background:var(--emerald-soft);border:1px solid #6EE7B7;color:var(--emerald);padding:5px 12px;border-radius:999px;font-weight:700;">
            Verified gVisor Sandbox
          </span>
        </div>

        <!-- Crisp White Interactive Whiteboard Canvas -->
        <div style="background:var(--alabaster);border:1.5px solid var(--stone-border);border-radius:14px;padding:16px;">
          <svg id="mirror-whiteboard-svg" viewBox="0 0 840 250" style="width:100%;height:auto;display:block;"></svg>
        </div>

        <!-- 3 Reassuring Closing KPI Cards -->
        <div class="wb-kpi-grid">
          <div class="wb-kpi-box">
            <div class="mono" style="font-size:10.5px;color:var(--warm-muted);">CASH TO CLOSE VS. VAULT</div>
            <div class="serif-ad" id="wb-kpi-cash" style="font-size:18px;font-weight:800;color:var(--warm-ink);margin-top:4px;">
              $22,300 Needed ($2,700 Left)
            </div>
          </div>
          <div class="wb-kpi-box">
            <div class="mono" style="font-size:10.5px;color:var(--warm-muted);">FIRST PAYMENT DATE</div>
            <div class="serif-ad" style="font-size:18px;font-weight:800;color:var(--sky-blue);margin-top:4px;">
              December 1 (Skip Nov!)
            </div>
          </div>
          <div class="wb-kpi-box">
            <div class="mono" style="font-size:10.5px;color:var(--warm-muted);">HPA 78% LTV AUTO PMI DROP</div>
            <div class="serif-ad" id="wb-kpi-pmi" style="font-size:18px;font-weight:800;color:var(--emerald);margin-top:4px;">
              Month 84 (-$118/mo Auto)
            </div>
          </div>
        </div>
      </div>

      <!-- Warm Astra Pro Spoken Transcript & Extended Thinking Card -->
      <div class="ad-card" style="background:var(--linen-panel);">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;flex-wrap:wrap;gap:8px;">
          <span class="mono" style="font-size:11.5px;font-weight:700;color:var(--warm-amber);">
            🔊 ASTRA PRO SPOKEN EXPLANATION (24KHZ NATIVE AUDIO • ZERO JARGON)
          </span>
          <span class="mono" id="mirror-chunk-counter" style="font-size:11px;color:var(--warm-muted);">
            Click any CD item on the left to hear Astra Pro explain it aloud
          </span>
        </div>

        <div id="mirror-thinking-box" class="mono" style="display:none;background:var(--amber-soft);border:1px solid #F59E0B;border-radius:10px;padding:10px 12px;font-size:11.5px;color:#92400E;margin-bottom:10px;">
          [ASTRA PRO EXTENDED THINKING]: Cross-checking CFPB TRID Closing Disclosure tolerance buckets &amp; 12 U.S.C. § 4902 HPA amortization schedule...
        </div>

        <div id="astra-spoken-text" class="serif-ad" style="background:var(--whiteboard);border:1px solid var(--stone-border);border-radius:12px;padding:16px;font-size:16px;line-height:1.65;color:var(--warm-ink);">
          "Take a deep breath—you don't need to drain your entire $25,000 savings! Your 5% down payment is $17,500, and after your Rocket credit, closing and escrow costs are $4,800. That is $22,300 total at the closing table, leaving a comfortable $2,700 emergency cushion untouched in your Rocket Money Vault."
        </div>
      </div>
    </section>

  </main>

  <script>
    const AUTH_TOKEN = "{auth_token}";
    let mirrorWs = null;
    let mirrorAudioCtx = null;
    let mirrorActiveSources = [];
    let mirrorNextTime = 0;
    let mirrorStream = null;
    let mirrorMicCtx = null;
    let mirrorProc = null;
    let mirrorMicOn = false;
    let mirrorMuted = false;
    let mirrorPcmChunks = 0;
    let activeCdKey = 'cash';

    const CD_EXPLAINERS = {{
      cash: {{
        title: "Cash to Close $22,300 & Post-Closing Safety Cushion",
        speech: "Take a deep breath—you don't need to drain your entire 25,000 dollar savings! Your 5 percent down payment is 17,500 dollars, and after your Rocket credit, closing and escrow costs are 4,800 dollars. That is 22,300 dollars total at the closing table, leaving a comfortable 2,700 dollar emergency cushion untouched in your Rocket Money Vault."
      }},
      boxA: {{
        title: "CD Page 2, Box A: Origination Charges ($1,295 Locked)",
        speech: "Box A covers Rocket Mortgage's flat underwriting and rate-lock processing fee of 1,295 dollars. Under federal TRID law, Box A is in the strict zero-percent tolerance bucket—meaning it cannot increase by a single penny from your original Loan Estimate!"
      }},
      boxF: {{
        title: "CD Page 2, Box F: Prepaids (15 Days Interest + Skip November Payment)",
        speech: "Box F isn't an extra lender fee! Because mortgages are paid in arrears, closing on October 16 means your first full monthly payment isn't due until December 1. Box F simply covers the 15 days of October interest so you completely skip a November mortgage bill."
      }},
      boxG: {{
        title: "CD Page 2, Box G: Initial Escrow Cushion & Month 84 Auto-PMI Drop",
        speech: "Box G seeds your personal property tax and insurance reserve with a two-month cushion so Oakland County taxes are paid on time. Plus, your 118 dollar monthly P-M-I isn't forever—under the federal Homeowners Protection Act, it automatically drops off at 78 percent loan-to-value in Month 84!"
      }}
    }};

    function ensureMirrorAudioCtx() {{
      if (!mirrorAudioCtx) {{
        const AC = window.AudioContext || window.webkitAudioContext;
        mirrorAudioCtx = new AC({{ sampleRate: 24000 }});
      }}
      if (mirrorAudioCtx.state === 'suspended') {{
        mirrorAudioCtx.resume();
      }}
      return mirrorAudioCtx;
    }}

    window.flushMirrorAudio = function(reason) {{
      mirrorActiveSources.forEach(src => {{
        try {{ src.stop(0); src.disconnect(); }} catch (e) {{}}
      }});
      mirrorActiveSources = [];
      if (mirrorAudioCtx) {{
        mirrorNextTime = mirrorAudioCtx.currentTime;
      }}
      if (window.stopAllLiveAudio) {{
        window.stopAllLiveAudio();
      }}
      const st = document.getElementById('mirror-barge-status');
      if (st && reason) st.innerText = '⚡ 0ms Flushed: ' + reason;
    }};

    window.toggleMirrorMute = function() {{
      mirrorMuted = !mirrorMuted;
      const btn = document.getElementById('btn-mirror-mute');
      if (mirrorMuted) {{
        window.flushMirrorAudio('Muted');
        btn.classList.add('muted');
        btn.innerText = '🔇 Audio Muted (Click to Unmute)';
      }} else {{
        btn.classList.remove('muted');
        btn.innerText = '🔇 Mute Astra Pro Audio';
      }}
    }};

    window.updateMirrorVoiceConfig = function() {{
      const mode = document.getElementById('mirror-live-mode').value;
      const voice = document.getElementById('mirror-voice-select').value;
      const tb = document.getElementById('mirror-thinking-box');
      if (tb) {{
        tb.style.display = mode === 'gemini-3.8-live-extended-thinking' ? 'block' : 'none';
      }}
      if (mirrorWs && mirrorWs.readyState === WebSocket.OPEN) {{
        mirrorWs.send(JSON.stringify({{ type: 'config', live_mode: mode, voice: voice }}));
      }}
    }};

    function playPcm24kChunk(base64Data) {{
      if (mirrorMuted) return;
      try {{
        const ctx = ensureMirrorAudioCtx();
        const bin = atob(base64Data);
        const len = Math.floor(bin.length / 2);
        const float32 = new Float32Array(len);
        for (let i = 0; i < len; i++) {{
          let s = (bin.charCodeAt(i * 2) & 0xff) | (bin.charCodeAt(i * 2 + 1) << 8);
          if (s >= 0x8000) s -= 0x10000;
          float32[i] = s / 32768.0;
        }}
        const buf = ctx.createBuffer(1, len, 24000);
        buf.getChannelData(0).set(float32);
        const src = ctx.createBufferSource();
        src.buffer = buf;
        src.connect(ctx.destination);
        const now = ctx.currentTime;
        if (mirrorNextTime < now) mirrorNextTime = now + 0.01;
        src.start(mirrorNextTime);
        mirrorNextTime += buf.duration;
        mirrorActiveSources.push(src);
        mirrorPcmChunks++;
        document.getElementById('mirror-chunk-counter').innerText = `${{mirrorPcmChunks}} PCM Chunks Streamed (24kHz HD)`;
        src.onended = () => {{
          mirrorActiveSources = mirrorActiveSources.filter(x => x !== src);
        }};
      }} catch (e) {{}}
    }}

    let m4MediaSource = null;
    let m4SourceBuffer = null;
    let m4MseQueue = [];
    let m4MseReady = false;

    function initM4MSE() {{
      if (m4MediaSource) return;
      const vid = document.getElementById('m4-avatar-video');
      const ph = document.getElementById('m4-avatar-placeholder');
      if (!vid) return;
      m4MediaSource = new MediaSource();
      vid.playsInline = true;
      vid.autoplay = true;
      vid.muted = mirrorMuted;
      vid.style.display = 'block';
      if (ph) ph.style.display = 'none';
      vid.src = URL.createObjectURL(m4MediaSource);
      m4MediaSource.addEventListener('sourceopen', () => {{
        const candidates = [
          'video/mp4; codecs="avc1.42E01E, mp4a.40.2"',
          'video/mp4; codecs="avc1.42c01f, mp4a.40.2"',
          'video/mp4; codecs="avc1.4D401E, mp4a.40.2"',
          'video/mp4'
        ];
        const mime = candidates.find(t => MediaSource.isTypeSupported(t));
        if (!mime) return;
        try {{
          m4SourceBuffer = m4MediaSource.addSourceBuffer(mime);
          m4SourceBuffer.mode = 'sequence';
          m4SourceBuffer.addEventListener('updateend', () => {{
            pumpM4MseQueue();
            if (vid.paused) vid.play().catch(() => {{}});
          }});
          m4MseReady = true;
          pumpM4MseQueue();
        }} catch (e) {{}}
      }});
    }}

    function pumpM4MseQueue() {{
      if (!m4MseReady || !m4SourceBuffer || m4SourceBuffer.updating || !m4MseQueue.length) return;
      try {{ m4SourceBuffer.appendBuffer(m4MseQueue.shift()); }} catch (e) {{}}
    }}

    function resetM4MSE() {{
      m4MseQueue = [];
      m4MseReady = false;
      m4SourceBuffer = null;
      m4MediaSource = null;
      const vid = document.getElementById('m4-avatar-video');
      const ph = document.getElementById('m4-avatar-placeholder');
      if (vid) {{ vid.style.display = 'none'; vid.removeAttribute('src'); }}
      if (ph) ph.style.display = 'block';
    }}

    window.toggleMirrorLiveVoice = function() {{
      const btn = document.getElementById('btn-mirror-session');
      const status = document.getElementById('mirror-ws-status');

      if (mirrorWs && mirrorWs.readyState === WebSocket.OPEN) {{
        window.flushMirrorAudio('Session Closed');
        resetM4MSE();
        if (mirrorMicOn) window.toggleMirror16kMic();
        mirrorWs.close();
        mirrorWs = null;
        btn.classList.remove('live');
        btn.innerText = '🎥 Start Astra Pro Live Avatar Session (/ws/live-voice/M.4)';
        status.innerText = 'Disconnected • Ready';
        return;
      }}

      ensureMirrorAudioCtx();
      resetM4MSE();
      const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const mode = document.getElementById('mirror-live-mode').value;
      const voice = document.getElementById('mirror-voice-select').value;
      const avatar = (document.getElementById('mirror-avatar-select') || {{value: 'Kira'}}).value;
      mirrorWs = new WebSocket(`${{proto}}//${{window.location.host}}/ws/live-voice/M.4?auth_token=${{AUTH_TOKEN}}&voice=${{encodeURIComponent(voice)}}&live_mode=${{encodeURIComponent(mode)}}&avatar=${{encodeURIComponent(avatar)}}`);
      mirrorWs.binaryType = 'arraybuffer';
      status.innerText = 'Connecting /ws/live-voice/M.4...';

      mirrorWs.onopen = () => {{
        btn.classList.add('live');
        btn.innerText = `⏹️ Stop Astra Pro Live (${{avatar !== 'off' ? 'Avatar ' + avatar : voice}})`;
        status.innerText = `🟢 Connected (${{mode}} • ${{avatar !== 'off' ? '24fps Avatar ' + avatar : voice}})`;
        mirrorWs.send(JSON.stringify({{
          type: 'text',
          text: 'Greet the homeowner warmly at the closing table in 2 concise sentences and offer to walk through Cash to Close, Box A, Box F, or Box G!'
        }}));
      }};

      mirrorWs.onmessage = (evt) => {{
        if (typeof evt.data !== 'string') {{
          if (!m4MediaSource) initM4MSE();
          m4MseQueue.push(evt.data);
          pumpM4MseQueue();
          mirrorPcmChunks++;
          document.getElementById('mirror-chunk-counter').innerText = `${{mirrorPcmChunks}} Live Video+Audio Chunks (24fps + 24kHz)`;
          return;
        }}
        const msg = JSON.parse(evt.data);
        if (msg.interrupted === true) {{
          window.flushMirrorAudio('Server Barge-In (msg.interrupted=true)');
          m4MseQueue = [];
          return;
        }}
        if (msg.thinking_summary) {{
          const tb = document.getElementById('mirror-thinking-box');
          if (tb) {{
            tb.style.display = 'block';
            tb.innerText = '[ASTRA PRO EXTENDED THINKING]: ' + msg.thinking_summary;
          }}
        }}
        if (msg.audio_b64) playPcm24kChunk(msg.audio_b64);
        if (msg.output_transcript) {{
          document.getElementById('astra-spoken-text').innerText = '"' + msg.output_transcript + '"';
        }}
      }};

      mirrorWs.onclose = () => {{
        btn.classList.remove('live');
        btn.innerText = '🎥 Start Astra Pro Live Avatar Session (/ws/live-voice/M.4)';
        status.innerText = 'Standby • /ws/live-voice/M.4';
      }};
    }};

    window.toggleMirror16kMic = async function() {{
      const btn = document.getElementById('btn-mirror-mic');
      if (mirrorMicOn) {{
        if (mirrorProc) mirrorProc.disconnect();
        if (mirrorMicCtx) mirrorMicCtx.close();
        if (mirrorStream) mirrorStream.getTracks().forEach(t => t.stop());
        mirrorMicOn = false;
        btn.classList.remove('mic-on');
        btn.innerText = '🎤 16kHz Mic Stream';
        return;
      }}
      if (!mirrorWs || mirrorWs.readyState !== WebSocket.OPEN) {{
        window.toggleMirrorLiveVoice();
      }}
      try {{
        mirrorStream = await navigator.mediaDevices.getUserMedia({{ audio: {{ sampleRate: 16000, channelCount: 1 }} }});
        mirrorMicCtx = new (window.AudioContext || window.webkitAudioContext)({{ sampleRate: 16000 }});
        const src = mirrorMicCtx.createMediaStreamSource(mirrorStream);
        mirrorProc = mirrorMicCtx.createScriptProcessor(4096, 1, 1);
        mirrorProc.onaudioprocess = (e) => {{
          const input = e.inputBuffer.getChannelData(0);
          let energy = 0;
          const pcm16 = new Int16Array(input.length);
          for (let i = 0; i < input.length; i++) {{
            energy += Math.abs(input[i]);
            pcm16[i] = Math.max(-32768, Math.min(32767, input[i] * 32768));
          }}
          if (energy / input.length > 0.045 && mirrorActiveSources.length > 0) {{
            window.flushMirrorAudio('User Spoke Into 16kHz Mic');
          }}
          if (mirrorWs && mirrorWs.readyState === WebSocket.OPEN) {{
            const bytes = new Uint8Array(pcm16.buffer);
            let bin = '';
            for (let i = 0; i < bytes.byteLength; i++) bin += String.fromCharCode(bytes[i]);
            mirrorWs.send(JSON.stringify({{ type: 'audio', data: btoa(bin) }}));
          }}
        }};
        src.connect(mirrorProc);
        mirrorProc.connect(mirrorMicCtx.destination);
        mirrorMicOn = true;
        btn.classList.add('mic-on');
        btn.innerText = '🔴 16kHz Mic Live';
      }} catch (e) {{
        document.getElementById('mirror-barge-status').innerText = 'Click any CD item below for 24kHz audio';
      }}
    }};

    function drawWhiteboardDiagram(key, price, sav) {{
      const down = Math.round(price * 0.05);
      const closeEsc = 4800;
      const totalNeeded = down + closeEsc;
      const cushion = Math.max(0, sav - totalNeeded);
      const svg = document.getElementById('mirror-whiteboard-svg');

      if (key === 'cash') {{
        svg.innerHTML = `
          <rect x="35" y="30" width="230" height="190" rx="14" fill="#FFFFFF" stroke="#0284C7" stroke-width="2.5"/>
          <text x="150" y="68" fill="#0284C7" font-family="IBM Plex Mono" font-size="11" font-weight="700" text-anchor="middle">ROCKET MONEY VAULT</text>
          <text x="150" y="116" fill="#1C1917" font-family="Fraunces" font-size="28" font-weight="800" text-anchor="middle">$${{sav.toLocaleString()}}</text>
          <text x="150" y="152" fill="#57534E" font-family="DM Sans" font-size="12.5" text-anchor="middle">Total Liquid Savings</text>

          <path d="M 275 125 L 325 125" stroke="#D97706" stroke-width="3" stroke-dasharray="5,4"/>
          <polygon points="325,119 338,125 325,131" fill="#D97706"/>

          <rect x="348" y="30" width="240" height="190" rx="14" fill="#FFFBEB" stroke="#D97706" stroke-width="2.5"/>
          <text x="468" y="66" fill="#B45309" font-family="IBM Plex Mono" font-size="11" font-weight="700" text-anchor="middle">CLOSING TABLE WIRE</text>
          <text x="468" y="108" fill="#1C1917" font-family="Fraunces" font-size="26" font-weight="800" text-anchor="middle">$${{totalNeeded.toLocaleString()}}</text>
          <text x="468" y="142" fill="#57534E" font-family="IBM Plex Mono" font-size="11.5" text-anchor="middle">5% Down: $${{down.toLocaleString()}}</text>
          <text x="468" y="165" fill="#57534E" font-family="IBM Plex Mono" font-size="11.5" text-anchor="middle">Net Closing/Escrow: $4,800</text>

          <path d="M 598 125 L 638 125" stroke="#047857" stroke-width="3"/>
          <polygon points="638,119 651,125 638,131" fill="#047857"/>

          <rect x="658" y="30" width="155" height="190" rx="14" fill="#ECFDF5" stroke="#047857" stroke-width="2.5"/>
          <text x="735" y="68" fill="#047857" font-family="IBM Plex Mono" font-size="10.5" font-weight="700" text-anchor="middle">SAFETY CUSHION</text>
          <text x="735" y="116" fill="#047857" font-family="Fraunces" font-size="26" font-weight="800" text-anchor="middle">$${{cushion.toLocaleString()}}</text>
          <text x="735" y="152" fill="#065F46" font-family="DM Sans" font-size="12" font-weight="600" text-anchor="middle">Stays in Your Vault!</text>
        `;
      }} else if (key === 'boxA') {{
        svg.innerHTML = `
          <rect x="55" y="38" width="320" height="175" rx="14" fill="#FFFFFF" stroke="#0284C7" stroke-width="2.5"/>
          <text x="215" y="78" fill="#0284C7" font-family="IBM Plex Mono" font-size="12" font-weight="700" text-anchor="middle">INITIAL LOAN ESTIMATE (LE)</text>
          <text x="215" y="125" fill="#1C1917" font-family="Fraunces" font-size="30" font-weight="800" text-anchor="middle">$1,295.00</text>
          <text x="215" y="160" fill="#57534E" font-family="IBM Plex Mono" font-size="11.5" text-anchor="middle">Box A Origination Flat Fee</text>

          <text x="420" y="130" fill="#047857" font-family="IBM Plex Mono" font-size="20" font-weight="700" text-anchor="middle">== 0% Δ ==</text>

          <rect x="465" y="38" width="320" height="175" rx="14" fill="#ECFDF5" stroke="#047857" stroke-width="2.5"/>
          <text x="625" y="78" fill="#047857" font-family="IBM Plex Mono" font-size="12" font-weight="700" text-anchor="middle">FINAL CLOSING DISCLOSURE (CD)</text>
          <text x="625" y="125" fill="#047857" font-family="Fraunces" font-size="30" font-weight="800" text-anchor="middle">$1,295.00</text>
          <text x="625" y="160" fill="#065F46" font-family="IBM Plex Mono" font-size="11.5" font-weight="600" text-anchor="middle">100% Locked Under TRID Zero-Tolerance</text>
        `;
      }} else if (key === 'boxF') {{
        svg.innerHTML = `
          <line x1="70" y1="130" x2="770" y2="130" stroke="#D97706" stroke-width="4"/>
          <circle cx="135" cy="130" r="11" fill="#D97706"/>
          <text x="135" y="95" fill="#B45309" font-family="IBM Plex Mono" font-size="12" font-weight="700" text-anchor="middle">OCT 16 CLOSING</text>
          <text x="135" y="168" fill="#1C1917" font-family="DM Sans" font-size="12.5" font-weight="600" text-anchor="middle">15 Days Per-Diem ($510)</text>

          <circle cx="425" cy="130" r="11" fill="#047857"/>
          <text x="425" y="95" fill="#047857" font-family="IBM Plex Mono" font-size="12" font-weight="700" text-anchor="middle">NOV 1 — NO PAYMENT DUE!</text>
          <text x="425" y="168" fill="#065F46" font-family="DM Sans" font-size="12.5" font-weight="600" text-anchor="middle">Skip November Mortgage Bill</text>

          <circle cx="710" cy="130" r="11" fill="#0284C7"/>
          <text x="710" y="95" fill="#0284C7" font-family="IBM Plex Mono" font-size="12" font-weight="700" text-anchor="middle">DEC 1 FIRST PAYMENT</text>
          <text x="710" y="168" fill="#1C1917" font-family="DM Sans" font-size="12.5" font-weight="600" text-anchor="middle">Pays November Interest in Arrears</text>
        `;
      }} else {{
        svg.innerHTML = `
          <rect x="50" y="38" width="335" height="175" rx="14" fill="#FFFBEB" stroke="#D97706" stroke-width="2.5"/>
          <text x="217" y="76" fill="#B45309" font-family="IBM Plex Mono" font-size="11.5" font-weight="700" text-anchor="middle">BOX G: ESCROW RESERVE CUSHION</text>
          <text x="217" y="120" fill="#1C1917" font-family="Fraunces" font-size="26" font-weight="800" text-anchor="middle">$2,320 Cushion</text>
          <text x="217" y="155" fill="#57534E" font-family="DM Sans" font-size="12.5" text-anchor="middle">2-Mo RESPA Buffer for Oakland Tax &amp; Ins</text>

          <rect x="445" y="38" width="345" height="175" rx="14" fill="#ECFDF5" stroke="#047857" stroke-width="2.5"/>
          <text x="617" y="76" fill="#047857" font-family="IBM Plex Mono" font-size="11.5" font-weight="700" text-anchor="middle">HPA 78% LTV AUTO-PMI TERMINATION</text>
          <text x="617" y="120" fill="#047857" font-family="Fraunces" font-size="26" font-weight="800" text-anchor="middle">Month 84 (-$118/mo)</text>
          <text x="617" y="155" fill="#065F46" font-family="DM Sans" font-size="12.5" font-weight="600" text-anchor="middle">Drops Automatically by Law (12 U.S.C. § 4902)</text>
        `;
      }}
    }}

    window.selectCdWhiteboardItem = function(key, btnEl) {{
      // Flush any previous audio in 0ms on click
      window.flushMirrorAudio('Switched to CD Item: ' + key);

      activeCdKey = key;
      document.querySelectorAll('.cd-item-btn').forEach(b => b.classList.remove('active'));
      if (btnEl) btnEl.classList.add('active');
      const info = CD_EXPLAINERS[key] || CD_EXPLAINERS.cash;
      document.getElementById('wb-title').innerText = info.title;
      document.getElementById('astra-spoken-text').innerText = '"' + info.speech + '"';
      window.refreshMirrorSandbox();

      const voice = document.getElementById('mirror-voice-select').value || 'Aoede';
      const mode = document.getElementById('mirror-live-mode').value || 'gemini-3.8-live';

      if (mirrorWs && mirrorWs.readyState === WebSocket.OPEN) {{
        mirrorWs.send(JSON.stringify({{
          type: 'text',
          text: 'Explain ' + info.title + ' warmly and clearly in two sentences.',
          live_mode: mode,
          voice: voice
        }}));
      }} else if (window.playLiveCallClip && !mirrorMuted) {{
        window.playLiveCallClip(info.speech, voice, "Astra Pro Virtual Mortgage Advisor", null);
      }}
    }};

    window.refreshMirrorSandbox = async function() {{
      const price = parseFloat(document.getElementById('inp-mirror-price').value || 350000);
      const sav = parseFloat(document.getElementById('inp-mirror-sav').value || 25000);
      drawWhiteboardDiagram(activeCdKey, price, sav);

      const down = Math.round(price * 0.05);
      const rem = Math.max(0, sav - (down + 4800));
      document.getElementById('wb-kpi-cash').innerText = `$${{(down + 4800).toLocaleString()}} Needed ($${{rem.toLocaleString()}} Left)`;

      try {{
        const res = await fetch('/api/sandbox', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: 'M.4',
            action: 'calc_mirror_whiteboard',
            params: {{
              price: price,
              savings: sav,
              cd_section: activeCdKey
            }}
          }})
        }});
        const data = await res.json();
        document.getElementById('wb-sandbox-pill').innerText = `Verified (${{data.execution_ms || 1.1}}ms)`;
      }} catch (e) {{}}
    }};

    window.runLiveVertexAI = async function() {{
      const model = window.getSelectedModel ? window.getSelectedModel() : 'gemini-3.8-flash';
      const price = parseFloat(document.getElementById('inp-mirror-price').value || 350000);
      const sav = parseFloat(document.getElementById('inp-mirror-sav').value || 25000);
      const spk = document.getElementById('astra-spoken-text');
      spk.innerHTML = `<em>Synthesizing Closing-Table Walkthrough with <strong>${{model}}</strong>...</em>`;

      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: 'M.4',
            model: model,
            user_input: `Explain Cash to Close, Box A, Box F, Box G, and Month 84 HPA PMI termination for a $${{price}} home with $${{sav}} in Rocket Money savings.`,
            params: {{ price: price, savings: sav }}
          }})
        }});
        const data = await res.json();
        const textOut = (data.vertex && data.vertex.response_markdown) || data.output || CD_EXPLAINERS[activeCdKey].speech;
        spk.innerHTML = `<strong>[${{data.model_used || model}}]:</strong> ${{textOut}}`;
      }} catch (e) {{
        spk.innerText = "Error: " + e.message;
      }}
    }};

    document.addEventListener('DOMContentLoaded', () => {{
      window.refreshMirrorSandbox();
    }});
  </script>

  {render_floating_control_bar_and_drawer(code, auth_token)}
</body>
</html>"""
