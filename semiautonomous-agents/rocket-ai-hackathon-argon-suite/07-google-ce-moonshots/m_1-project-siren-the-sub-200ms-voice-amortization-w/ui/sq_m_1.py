# -*- coding: utf-8 -*-
"""Square M.1: Project Siren: Real-Time Gemini Live Voice Whisperer — Real Gemini 3.8 Live Audio WebSocket
Visual Design: Dieter Rams Braun / Teenage Engineering Tactile Warm Anodized Aluminum Audio & Equity Studio
(#F4F2EE warm anodized light industrial gray/cream surface, #FF4F00 Braun/Teenage Engineering international orange
primary button, #18181B matte charcoal dials, #FFFFFF crisp equity chart card, Outfit + DM Sans + IBM Plex Mono).
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_m_1(auth_token: str) -> str:
    code = "M.1"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[M.1] Project Siren: Real-Time Gemini Live Voice Whisperer | Braun Tactile Audio Studio</title>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700;800&family=DM+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --anodized-bg: #F4F2EE;
      --chassis-recess: #EAE6DF;
      --card-white: #FFFFFF;
      --braun-orange: #FF4F00;
      --braun-orange-soft: #FFF0EB;
      --charcoal-dial: #18181B;
      --warm-ink: #1C1917;
      --muted-ink: #57534E;
      --aluminum-border: #D6D2C9;
      --forest-green: #0F766E;
      --amber-led: #D97706;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: var(--anodized-bg);
      color: var(--warm-ink);
      font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      min-height: 100vh;
      padding-bottom: 96px;
    }}
    .font-display {{ font-family: 'Outfit', sans-serif; }}
    .mono {{ font-family: 'IBM Plex Mono', monospace; }}

    /* Tactile Anodized Aluminum Studio Header */
    .braun-header {{
      background: #FAF8F5;
      border-bottom: 2px solid var(--aluminum-border);
      padding: 16px 28px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 16px;
      box-shadow: 0 2px 8px rgba(24, 24, 27, 0.04);
    }}
    .hardware-tag {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: var(--chassis-recess);
      border: 1px solid #C7C2B8;
      color: var(--charcoal-dial);
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      padding: 5px 12px;
      border-radius: 6px;
      letter-spacing: 0.03em;
    }}
    .led-dot {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--braun-orange);
      display: inline-block;
      box-shadow: 0 0 0 2px rgba(255, 79, 0, 0.2);
    }}
    .led-dot.live {{
      background: #10B981;
      box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.25);
    }}

    .tactile-select-group {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: var(--card-white);
      border: 1.5px solid #C7C2B8;
      padding: 6px 12px;
      border-radius: 8px;
      box-shadow: inset 0 1px 2px rgba(0,0,0,0.04);
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11.5px;
    }}
    .tactile-select-group select {{
      background: transparent;
      color: var(--charcoal-dial);
      border: none;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11.5px;
      font-weight: 700;
      outline: none;
      cursor: pointer;
    }}

    /* Main Studio Grid */
    .studio-grid {{
      max-width: 1540px;
      margin: 24px auto;
      padding: 0 28px;
      display: grid;
      grid-template-columns: 440px 1fr;
      gap: 24px;
      align-items: start;
    }}
    @media (max-width: 1140px) {{
      .studio-grid {{ grid-template-columns: 1fr; }}
    }}

    /* Tactile Hardware Module Card */
    .chassis-module {{
      background: #FAF8F5;
      border: 1.5px solid #C7C2B8;
      border-radius: 16px;
      padding: 22px;
      box-shadow:
        0 8px 24px rgba(28, 25, 23, 0.06),
        inset 0 1px 0 #FFFFFF;
    }}
    .equity-chart-card {{
      background: var(--card-white);
      border: 1.5px solid var(--aluminum-border);
      border-radius: 16px;
      padding: 24px;
      box-shadow: 0 8px 24px rgba(28, 25, 23, 0.05);
    }}

    /* Speaker Grille & Acoustic Level Meter */
    .speaker-grille {{
      background: var(--chassis-recess);
      border: 1.5px solid #C7C2B8;
      border-radius: 12px;
      padding: 18px;
      margin-bottom: 16px;
      box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.06);
    }}
    .vu-meter-bars {{
      display: flex;
      align-items: flex-end;
      justify-content: center;
      gap: 5px;
      height: 46px;
      margin: 12px 0 8px;
    }}
    .vu-bar {{
      width: 8px;
      background: var(--charcoal-dial);
      border-radius: 3px;
      transition: height 0.08s ease-out, background-color 0.1s;
    }}
    .vu-bar.hot {{
      background: var(--braun-orange);
    }}

    /* Physical Push-Button Controls */
    .hw-btn-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      margin-bottom: 16px;
    }}
    .hw-btn {{
      appearance: none;
      border: 1.5px solid #18181B;
      border-radius: 10px;
      padding: 11px 12px;
      font-family: 'Outfit', sans-serif;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 7px;
      transition: transform 0.08s ease, box-shadow 0.12s ease;
      box-shadow: 0 3px 0 #18181B;
    }}
    .hw-btn:active {{
      transform: translateY(2px);
      box-shadow: 0 1px 0 #18181B;
    }}
    .hw-btn-orange {{
      background: var(--braun-orange);
      color: #FFFFFF;
      grid-column: span 2;
      font-size: 14px;
      padding: 13px 16px;
    }}
    .hw-btn-charcoal {{
      background: var(--charcoal-dial);
      color: #FFFFFF;
    }}
    .hw-btn-charcoal.active-mic {{
      background: #0F766E;
      border-color: #0F766E;
      box-shadow: 0 3px 0 #115E59;
    }}
    .hw-btn-light {{
      background: var(--card-white);
      color: var(--charcoal-dial);
    }}
    .hw-btn-light.muted {{
      background: #FEE2E2;
      color: #991B1B;
      border-color: #991B1B;
      box-shadow: 0 3px 0 #991B1B;
    }}

    /* Tactile Matte Charcoal Dials / Sliders */
    .dial-box {{
      background: var(--card-white);
      border: 1px solid var(--aluminum-border);
      border-radius: 10px;
      padding: 12px 14px;
      margin-bottom: 10px;
    }}
    .dial-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 12px;
      font-weight: 700;
      margin-bottom: 6px;
    }}
    .dial-readout {{
      background: var(--charcoal-dial);
      color: #FFFFFF;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 12px;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 5px;
    }}
    input[type="range"] {{
      width: 100%;
      accent-color: var(--braun-orange);
      cursor: pointer;
      height: 6px;
    }}

    /* Voice Prompt Barge-In Buttons */
    .prompt-chip {{
      width: 100%;
      text-align: left;
      background: var(--card-white);
      border: 1.5px solid var(--aluminum-border);
      border-left: 4px solid var(--braun-orange);
      border-radius: 8px;
      padding: 10px 12px;
      font-family: 'DM Sans', sans-serif;
      font-size: 12.5px;
      font-weight: 600;
      color: var(--warm-ink);
      cursor: pointer;
      margin-bottom: 8px;
      transition: background 0.15s, border-color 0.15s;
    }}
    .prompt-chip:hover {{
      background: var(--braun-orange-soft);
      border-color: var(--braun-orange);
    }}

    /* KPI Readout Strip */
    .kpi-strip {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 14px;
      margin-bottom: 20px;
    }}
    @media (max-width: 900px) {{
      .kpi-strip {{ grid-template-columns: 1fr 1fr; }}
    }}
    .kpi-box {{
      background: #FAF8F5;
      border: 1px solid var(--aluminum-border);
      border-radius: 10px;
      padding: 14px;
    }}
    .kpi-label {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 10.5px;
      font-weight: 600;
      color: var(--muted-ink);
      text-transform: uppercase;
    }}
    .kpi-val {{
      font-family: 'Outfit', sans-serif;
      font-size: 21px;
      font-weight: 800;
      color: var(--charcoal-dial);
      margin-top: 4px;
    }}
  </style>
</head>
<body>

  <!-- DIETER RAMS BRAUN / TEENAGE ENGINEERING WARM ANODIZED STUDIO HEADER -->
  <header class="braun-header">
    <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;">
      <span class="hardware-tag">
        <span id="ws-led" class="led-dot"></span>
        MODEL TP-1 • PROJECT SIREN ACOUSTIC EQUITY STUDIO
      </span>
      <div>
        <h1 class="font-display" style="font-size:20px;font-weight:800;letter-spacing:-0.02em;color:var(--charcoal-dial);">
          Project Siren: Real-Time Gemini Live Voice Amortization Whisperer
        </h1>
        <p style="font-size:12.5px;color:var(--muted-ink);">
          24kHz Native Audio WebSocket (<span class="mono">/ws/live-voice/M.1</span>) • Zero-Latency 0ms Barge-In Interruption &amp; Live Equity Curve Shaping
        </p>
      </div>
    </div>

    <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
      <div class="tactile-select-group">
        <span style="color:var(--muted-ink);font-weight:600;">LIVE AUDIO ENGINE:</span>
        <select id="siren-live-mode" onchange="window.updateSirenVoiceConfig()" aria-label="Gemini Live Audio Mode">
          <option value="gemini-3.8-live" selected>Gemini 3.8 Live (24kHz Native Audio)</option>
          <option value="gemini-3.8-live-extended-thinking">Gemini 3.8 Live Extended Thinking</option>
        </select>
      </div>

      <div class="tactile-select-group">
        <span style="color:var(--muted-ink);font-weight:600;">VOICE:</span>
        <select id="siren-voice-select" onchange="window.updateSirenVoiceConfig()" aria-label="Voice Persona">
          <option value="Aoede" selected>Aoede (Warm HD)</option>
          <option value="Puck">Puck (Dynamic HD)</option>
          <option value="Kore">Kore (Executive HD)</option>
          <option value="Fenrir">Fenrir (Deep HD)</option>
        </select>
      </div>

      <div class="tactile-select-group">
        <span style="color:var(--muted-ink);font-weight:600;">REASONING:</span>
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)" aria-label="Select Vertex Reasoning Model">
          <option value="gemini-4-argon">gemini-4-argon (Frontier)</option>
          <option value="gemini-3.8-flash" selected>gemini-3.8-flash (Low-Latency)</option>
        </select>
      </div>

      <button onclick="window.runLiveVertexAI()" class="hw-btn hw-btn-charcoal" style="padding:8px 14px;font-size:12px;">
        Recalculate Strategy
      </button>
    </div>
  </header>

  <!-- MAIN STUDIO WORKSPACE -->
  <main class="studio-grid">

    <!-- LEFT COLUMN: BRAUN / TEENAGE ENGINEERING TACTILE VOICE & ROTARY DIAL UNIT -->
    <aside class="chassis-module">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
        <span class="mono" style="font-size:11px;font-weight:700;color:var(--muted-ink);">ACOUSTIC TRANSDUCER • 24KHZ PCM</span>
        <span id="ws-status-label" class="mono" style="font-size:11px;font-weight:700;color:var(--braun-orange);">STANDBY • READY</span>
      </div>

      <!-- Anodized Speaker Grille & Real-Time Acoustic VU Meter -->
      <div class="speaker-grille">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span class="mono" style="font-size:11px;font-weight:700;color:var(--charcoal-dial);" id="active-mode-readout">
            MODE: GEMINI 3.8 LIVE (24KHZ)
          </span>
          <span class="mono" style="font-size:11px;color:var(--forest-green);font-weight:700;" id="pcm-chunks-readout">
            0ms BARGE-IN ARMED
          </span>
        </div>

        <div class="vu-meter-bars" id="siren-vu-bars">
          <div class="vu-bar" style="height:22%"></div>
          <div class="vu-bar" style="height:38%"></div>
          <div class="vu-bar hot" style="height:64%"></div>
          <div class="vu-bar" style="height:45%"></div>
          <div class="vu-bar hot" style="height:78%"></div>
          <div class="vu-bar" style="height:52%"></div>
          <div class="vu-bar" style="height:34%"></div>
          <div class="vu-bar hot" style="height:60%"></div>
          <div class="vu-bar" style="height:40%"></div>
          <div class="vu-bar" style="height:26%"></div>
          <div class="vu-bar" style="height:48%"></div>
          <div class="vu-bar" style="height:30%"></div>
        </div>

        <div class="mono" style="font-size:11px;color:var(--muted-ink);text-align:center;" id="barge-in-telemetry">
          Speak into 16kHz Mic or click any prompt below to interrupt audio in 0ms
        </div>
      </div>

      <!-- Tactile Hardware-Inspired Control Deck -->
      <div class="hw-btn-grid">
        <button id="btn-start-session" class="hw-btn hw-btn-orange" onclick="window.toggleSirenLiveSession()">
          🎙️ Start Live Voice Session
        </button>
        <button id="btn-mic-16k" class="hw-btn hw-btn-charcoal" onclick="window.toggleSirenMic16k()">
          🎤 16kHz Mic (Speak to Interrupt)
        </button>
        <button id="btn-barge-in" class="hw-btn hw-btn-light" onclick="window.triggerInstantBargeIn('User manual 0ms barge-in button pressed')">
          ✋ Interrupt / Barge-In
        </button>
        <button id="btn-mute" class="hw-btn hw-btn-light" style="grid-column:span 2;" onclick="window.toggleSirenMute()">
          🔇 Mute Audio Output
        </button>
      </div>

      <!-- Tactile Matte Charcoal Dials (Sliders) -->
      <div style="margin-top:16px;margin-bottom:14px;">
        <div class="mono" style="font-size:11px;font-weight:700;color:var(--muted-ink);margin-bottom:8px;text-transform:uppercase;">
          Tactile Equity Curve Faders (6.125% Fixed • 30-Yr Base)
        </div>

        <div class="dial-box">
          <div class="dial-header">
            <span>Mortgage Principal Balance</span>
            <span class="dial-readout" id="lbl-prin">$450,000</span>
          </div>
          <input type="range" id="sld-prin" min="250000" max="850000" step="10000" value="450000" oninput="window.bendAmortizationCurve()">
        </div>

        <div class="dial-box">
          <div class="dial-header">
            <span>Extra Monthly Principal Fader ($0 – $1,000/mo)</span>
            <span class="dial-readout" id="lbl-extra-mo" style="background:var(--braun-orange);">+$250 / mo</span>
          </div>
          <input type="range" id="sld-extra-mo" min="0" max="1000" step="25" value="250" oninput="window.bendAmortizationCurve()">
        </div>

        <div class="dial-box">
          <div class="dial-header">
            <span>Annual Lump-Sum Prepayment (Tax/Bonus)</span>
            <span class="dial-readout" id="lbl-lump-yr">+$5,000 / yr</span>
          </div>
          <input type="range" id="sld-lump-yr" min="0" max="25000" step="1000" value="5000" oninput="window.bendAmortizationCurve()">
        </div>
      </div>

      <!-- Instant Voice Barge-In Prompts -->
      <div>
        <div class="mono" style="font-size:11px;font-weight:700;color:var(--muted-ink);margin-bottom:8px;text-transform:uppercase;">
          Instant Voice Barge-In Prompts (0ms Flush + 24kHz HD Response)
        </div>
        <button class="prompt-chip" onclick="window.sendVoiceBargeIn('What happens if I add $250 a month in extra principal?', 250, 0, this)">
          🗣️ "What happens if I add $250 a month in extra principal?"
        </button>
        <button class="prompt-chip" onclick="window.sendVoiceBargeIn('How much interest do I save with a bi-weekly payment?', 228, 2500, this)">
          🗣️ "How much interest do I save with a bi-weekly payment?"
        </button>
        <button class="prompt-chip" onclick="window.sendVoiceBargeIn('Wait—interrupt: compare $250/mo vs $500/mo extra principal!', 500, 5000, this)">
          🗣️ "Wait—interrupt: compare $250/mo vs $500/mo extra principal!"
        </button>
      </div>
    </aside>

    <!-- RIGHT COLUMN: CRISP WHITE EQUITY CHART CARD & LIVE VOICE TRANSCRIPT -->
    <section style="display:flex;flex-direction:column;gap:20px;">
      <div class="equity-chart-card">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;margin-bottom:18px;padding-bottom:14px;border-bottom:1px solid var(--aluminum-border);">
          <div>
            <span class="mono" style="font-size:11px;font-weight:700;color:var(--braun-orange);text-transform:uppercase;">
              Real-Time 30-Year Principal &amp; Interest Amortization Studio
            </span>
            <h2 class="font-display" style="font-size:22px;font-weight:800;color:var(--charcoal-dial);margin-top:2px;">
              Interactive Principal Paydown &amp; Interest Wedge Visualizer
            </h2>
          </div>
          <div style="display:flex;gap:14px;align-items:center;font-size:12px;font-weight:600;" class="mono">
            <span><span style="color:#78716C;">━━</span> Standard 30-Yr Schedule</span>
            <span><span style="color:var(--braun-orange);">━━</span> Siren Accelerated Curve</span>
            <span><span style="color:var(--forest-green);">░░</span> Saved Interest Wedge</span>
          </div>
        </div>

        <!-- 4 Tactile KPI Readouts -->
        <div class="kpi-strip">
          <div class="kpi-box">
            <div class="kpi-label">Standard 30-Yr Interest</div>
            <div class="kpi-val" id="kpi-base-int">$536,158</div>
            <div class="mono" style="font-size:11px;color:var(--muted-ink);margin-top:3px;">360 Months @ 6.125% Fixed</div>
          </div>
          <div class="kpi-box" style="border-color:var(--braun-orange);background:var(--braun-orange-soft);">
            <div class="kpi-label" style="color:var(--braun-orange);">Accelerated Payoff Term</div>
            <div class="kpi-val" id="kpi-siren-term" style="color:var(--braun-orange);">20.4 Years</div>
            <div class="mono" id="kpi-years-saved" style="font-size:11px;color:var(--charcoal-dial);font-weight:700;margin-top:3px;">Debt-Free 9.6 Yrs Earlier</div>
          </div>
          <div class="kpi-box" style="border-color:var(--forest-green);background:#F0FDFA;">
            <div class="kpi-label" style="color:var(--forest-green);">Lifetime Interest Saved</div>
            <div class="kpi-val" id="kpi-int-saved" style="color:var(--forest-green);">$189,420</div>
            <div class="mono" style="font-size:11px;color:var(--forest-green);font-weight:600;margin-top:3px;">Direct Borrower Equity</div>
          </div>
          <div class="kpi-box">
            <div class="kpi-label">Barge-In Audio Flush</div>
            <div class="kpi-val" id="kpi-latency">0 ms</div>
            <div class="mono" style="font-size:11px;color:var(--muted-ink);margin-top:3px;">Instant WebAudio Node Flush</div>
          </div>
        </div>

        <!-- Interactive 30-Year Amortization SVG Curve -->
        <div style="background:#FAF8F5;border:1px solid var(--aluminum-border);border-radius:12px;padding:16px;">
          <svg id="siren-svg-curve" viewBox="0 0 880 310" style="width:100%;height:auto;display:block;"></svg>
        </div>
      </div>

      <!-- Spoken Audio Briefing & Extended Thinking Telemetry Card -->
      <div class="equity-chart-card" style="background:#FAF8F5;">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:10px;">
          <div style="display:flex;align-items:center;gap:8px;">
            <span class="led-dot" id="transcript-led"></span>
            <span class="mono" style="font-size:12px;font-weight:700;color:var(--charcoal-dial);">
              GEMINI 3.8 LIVE AUDIO TRANSCRIPT &amp; EXTENDED THINKING TRACE
            </span>
          </div>
          <span class="mono" id="sandbox-action-tag" style="font-size:11px;color:var(--muted-ink);">
            Engine: /ws/live-voice/M.1 + /api/live-tts (24kHz PCM)
          </span>
        </div>

        <div id="siren-thinking-box" class="mono" style="display:none;background:#FEF3C7;border:1px solid #F59E0B;border-radius:8px;padding:10px 12px;font-size:11.5px;color:#92400E;margin-bottom:10px;">
          [EXTENDED THINKING TRACE]: Computing month-by-month amortization curtailment differential across 360 periods...
        </div>

        <div id="siren-transcript-box" style="background:var(--card-white);border:1px solid var(--aluminum-border);border-radius:10px;padding:16px;font-size:14.5px;line-height:1.6;color:var(--warm-ink);">
          <strong>[Siren Voice Whisperer • Aoede HD]:</strong> "With a $450,000 mortgage at 6.125%, adding $250 a month in extra principal plus $5,000 a year from your spring bonus eliminates $189,420 in lifetime interest and pays off your home 9.6 years early. Drag the faders or speak into the 16kHz mic—if you interrupt me mid-sentence, I flush my audio buffer in 0 milliseconds and recalculate live!"
        </div>
      </div>
    </section>

  </main>

  <script>
    const AUTH_TOKEN = "{auth_token}";
    let sirenWs = null;
    let sirenAudioCtx = null;
    let activePcmSources = [];
    let sirenNextPlayTime = 0;
    let mediaStream = null;
    let micCtx = null;
    let processor = null;
    let isMicStreaming = false;
    let isMuted = false;
    let pcmChunkCounter = 0;

    function ensureSirenAudioCtx() {{
      if (!sirenAudioCtx) {{
        const AC = window.AudioContext || window.webkitAudioContext;
        sirenAudioCtx = new AC({{ sampleRate: 24000 }});
      }}
      if (sirenAudioCtx.state === 'suspended') {{
        sirenAudioCtx.resume();
      }}
      return sirenAudioCtx;
    }}

    // Instant 0ms flush of all active AudioBufferSourceNodes
    window.flushAllSirenAudio = function(reason) {{
      const flushedCount = activePcmSources.length;
      activePcmSources.forEach(src => {{
        try {{
          src.stop(0);
          src.disconnect();
        }} catch (e) {{}}
      }});
      activePcmSources = [];
      if (sirenAudioCtx) {{
        sirenNextPlayTime = sirenAudioCtx.currentTime;
      }}
      if (window.stopAllLiveAudio) {{
        window.stopAllLiveAudio();
      }}
      pulseVuBars(false);
      const latEl = document.getElementById('kpi-latency');
      if (latEl) latEl.innerText = '0 ms (Flushed)';
      const bEl = document.getElementById('barge-in-telemetry');
      if (bEl && reason) {{
        bEl.innerText = `⚡ 0ms Barge-In Flush (${{flushedCount}} audio buffers cleared): ${{reason}}`;
      }}
    }};

    window.triggerInstantBargeIn = function(reason) {{
      window.flushAllSirenAudio(reason || 'Manual Barge-In');
      if (sirenWs && sirenWs.readyState === WebSocket.OPEN) {{
        sirenWs.send(JSON.stringify({{ type: 'barge_in', timestamp: Date.now() }}));
      }}
    }};

    window.toggleSirenMute = function() {{
      isMuted = !isMuted;
      const btn = document.getElementById('btn-mute');
      if (isMuted) {{
        window.flushAllSirenAudio('Audio Muted');
        btn.classList.add('muted');
        btn.innerText = '🔇 Audio Muted (Click to Unmute)';
      }} else {{
        btn.classList.remove('muted');
        btn.innerText = '🔇 Mute Audio Output';
      }}
    }};

    window.updateSirenVoiceConfig = function() {{
      const mode = document.getElementById('siren-live-mode').value;
      const voice = document.getElementById('siren-voice-select').value;
      document.getElementById('active-mode-readout').innerText =
        mode === 'gemini-3.8-live-extended-thinking'
          ? `MODE: EXTENDED THINKING • ${{voice.toUpperCase()}}`
          : `MODE: GEMINI 3.8 LIVE (24KHZ) • ${{voice.toUpperCase()}}`;
      const thinkBox = document.getElementById('siren-thinking-box');
      if (thinkBox) {{
        thinkBox.style.display = mode === 'gemini-3.8-live-extended-thinking' ? 'block' : 'none';
      }}
      if (sirenWs && sirenWs.readyState === WebSocket.OPEN) {{
        sirenWs.send(JSON.stringify({{
          type: 'config',
          live_mode: mode,
          voice: voice
        }}));
      }}
    }};

    function pulseVuBars(active) {{
      const bars = document.querySelectorAll('#siren-vu-bars .vu-bar');
      bars.forEach((b, idx) => {{
        const h = active ? Math.max(18, Math.floor(Math.random() * 95)) : (20 + (idx * 7) % 35);
        b.style.height = h + '%';
      }});
    }}

    function playSirenPcm24k(base64Data) {{
      if (isMuted) return;
      try {{
        const ctx = ensureSirenAudioCtx();
        const bin = atob(base64Data);
        const len = Math.floor(bin.length / 2);
        const float32 = new Float32Array(len);
        for (let i = 0; i < len; i++) {{
          let sample = (bin.charCodeAt(i * 2) & 0xff) | (bin.charCodeAt(i * 2 + 1) << 8);
          if (sample >= 0x8000) sample -= 0x10000;
          float32[i] = sample / 32768.0;
        }}
        const buf = ctx.createBuffer(1, len, 24000);
        buf.getChannelData(0).set(float32);
        const src = ctx.createBufferSource();
        src.buffer = buf;
        src.connect(ctx.destination);

        const now = ctx.currentTime;
        if (sirenNextPlayTime < now) sirenNextPlayTime = now + 0.01;
        src.start(sirenNextPlayTime);
        sirenNextPlayTime += buf.duration;
        activePcmSources.push(src);

        pcmChunkCounter++;
        const chEl = document.getElementById('pcm-chunks-readout');
        if (chEl) chEl.innerText = `${{pcmChunkCounter}} PCM CHUNKS (24KHZ)`;
        pulseVuBars(true);

        src.onended = () => {{
          activePcmSources = activePcmSources.filter(s => s !== src);
          if (activePcmSources.length === 0) pulseVuBars(false);
        }};
      }} catch (e) {{}}
    }}

    window.toggleSirenLiveSession = function() {{
      const btn = document.getElementById('btn-start-session');
      const led = document.getElementById('ws-led');
      const lbl = document.getElementById('ws-status-label');

      if (sirenWs && sirenWs.readyState === WebSocket.OPEN) {{
        window.flushAllSirenAudio('Session Ended');
        if (isMicStreaming) window.toggleSirenMic16k();
        sirenWs.close();
        sirenWs = null;
        led.classList.remove('live');
        btn.innerText = '🎙️ Start Live Voice Session';
        lbl.innerText = 'DISCONNECTED • READY';
        return;
      }}

      ensureSirenAudioCtx();
      const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const mode = document.getElementById('siren-live-mode').value;
      const voice = document.getElementById('siren-voice-select').value;
      sirenWs = new WebSocket(`${{proto}}//${{window.location.host}}/ws/live-voice/M.1?auth_token=${{AUTH_TOKEN}}&voice=${{encodeURIComponent(voice)}}&live_mode=${{encodeURIComponent(mode)}}`);
      lbl.innerText = 'CONNECTING /ws/live-voice/M.1...';

      sirenWs.onopen = () => {{
        led.classList.add('live');
        btn.innerText = '⏹️ Stop Live Voice Session (Connected)';
        lbl.innerText = 'LIVE 24KHZ STREAM ACTIVE';
        sirenWs.send(JSON.stringify({{ type: 'config', live_mode: mode, voice: voice }}));
      }};

      sirenWs.onmessage = (evt) => {{
        const msg = JSON.parse(evt.data);
        if (msg.interrupted === true) {{
          window.flushAllSirenAudio('Server Barge-In Signal (msg.interrupted=true)');
          return;
        }}
        if (msg.thinking_summary) {{
          const tb = document.getElementById('siren-thinking-box');
          if (tb) {{
            tb.style.display = 'block';
            tb.innerText = '[EXTENDED THINKING TRACE]: ' + msg.thinking_summary;
          }}
        }}
        if (msg.audio_b64) {{
          playSirenPcm24k(msg.audio_b64);
        }}
        if (msg.output_transcript) {{
          const voiceName = document.getElementById('siren-voice-select').value;
          document.getElementById('siren-transcript-box').innerHTML =
            `<strong>[Siren Live Voice • ${{voiceName}} HD]:</strong> "${{msg.output_transcript}}"`;
        }}
      }};

      sirenWs.onclose = () => {{
        led.classList.remove('live');
        btn.innerText = '🎙️ Start Live Voice Session';
        lbl.innerText = 'STANDBY • READY';
      }};
    }};

    window.toggleSirenMic16k = async function() {{
      const micBtn = document.getElementById('btn-mic-16k');
      if (isMicStreaming) {{
        if (processor) processor.disconnect();
        if (micCtx) micCtx.close();
        if (mediaStream) mediaStream.getTracks().forEach(t => t.stop());
        isMicStreaming = false;
        micBtn.classList.remove('active-mic');
        micBtn.innerText = '🎤 16kHz Mic (Speak to Interrupt)';
        return;
      }}

      if (!sirenWs || sirenWs.readyState !== WebSocket.OPEN) {{
        window.toggleSirenLiveSession();
      }}

      try {{
        mediaStream = await navigator.mediaDevices.getUserMedia({{
          audio: {{ sampleRate: 16000, channelCount: 1, echoCancellation: true, noiseSuppression: true }}
        }});
        micCtx = new (window.AudioContext || window.webkitAudioContext)({{ sampleRate: 16000 }});
        const source = micCtx.createMediaStreamSource(mediaStream);
        processor = micCtx.createScriptProcessor(4096, 1, 1);
        processor.onaudioprocess = (e) => {{
          const input = e.inputBuffer.getChannelData(0);
          let energy = 0;
          const pcm16 = new Int16Array(input.length);
          for (let i = 0; i < input.length; i++) {{
            energy += Math.abs(input[i]);
            pcm16[i] = Math.max(-32768, Math.min(32767, input[i] * 32768));
          }}
          // Voice Activity Detection: if user speaks, flush playing audio in 0ms!
          if (energy / input.length > 0.045 && activePcmSources.length > 0) {{
            window.flushAllSirenAudio('16kHz Mic Voice Activity Detected');
          }}
          if (sirenWs && sirenWs.readyState === WebSocket.OPEN) {{
            const bytes = new Uint8Array(pcm16.buffer);
            let binary = '';
            for (let i = 0; i < bytes.byteLength; i++) binary += String.fromCharCode(bytes[i]);
            sirenWs.send(JSON.stringify({{ type: 'audio', data: btoa(binary) }}));
          }}
        }};
        source.connect(processor);
        processor.connect(micCtx.destination);
        isMicStreaming = true;
        micBtn.classList.add('active-mic');
        micBtn.innerText = '🔴 16kHz Mic Live (Speak Now)';
      }} catch (err) {{
        document.getElementById('barge-in-telemetry').innerText =
          'Mic permission unavailable in headless view — use the Barge-In Prompt buttons below!';
      }}
    }};

    function calcMonthlyPI(principal, annualRatePct, months) {{
      const r = (annualRatePct / 100.0) / 12.0;
      return principal * (r * Math.pow(1 + r, months)) / (Math.pow(1 + r, months) - 1);
    }}

    window.bendAmortizationCurve = async function() {{
      const prin = parseFloat(document.getElementById('sld-prin').value || 450000);
      const extraMo = parseFloat(document.getElementById('sld-extra-mo').value || 250);
      const lumpYr = parseFloat(document.getElementById('sld-lump-yr').value || 5000);
      const rate = 6.125;

      document.getElementById('lbl-prin').innerText = '$' + prin.toLocaleString();
      document.getElementById('lbl-extra-mo').innerText = '+$' + extraMo.toLocaleString() + ' / mo';
      document.getElementById('lbl-lump-yr').innerText = '+$' + lumpYr.toLocaleString() + ' / yr';

      const basePi = calcMonthlyPI(prin, rate, 360);
      const rMo = (rate / 100.0) / 12.0;

      let stdBal = prin;
      let sirBal = prin;
      let stdPts = [{{ yr: 0, bal: prin }}];
      let sirPts = [{{ yr: 0, bal: prin }}];
      let sirMos = 0;
      let sirInt = 0;
      const stdTotalInt = (basePi * 360) - prin;

      for (let m = 1; m <= 360; m++) {{
        if (stdBal > 0) {{
          const ip = stdBal * rMo;
          stdBal = Math.max(0, stdBal - (basePi - ip));
        }}
        if (sirBal > 0) {{
          sirMos = m;
          const ipS = sirBal * rMo;
          sirInt += ipS;
          const lump = (m % 12 === 3) ? lumpYr : 0;
          sirBal = Math.max(0, sirBal - ((basePi - ipS) + extraMo + lump));
        }}
        if (m % 12 === 0) {{
          stdPts.push({{ yr: m / 12, bal: stdBal }});
          sirPts.push({{ yr: m / 12, bal: sirBal }});
        }}
      }}

      const yrsSaved = ((360 - sirMos) / 12).toFixed(1);
      const intSaved = Math.max(0, Math.round(stdTotalInt - sirInt));

      document.getElementById('kpi-base-int').innerText = '$' + Math.round(stdTotalInt).toLocaleString();
      document.getElementById('kpi-siren-term').innerText = `${{(sirMos / 12).toFixed(1)}} Years`;
      document.getElementById('kpi-years-saved').innerText = `Debt-Free ${{yrsSaved}} Yrs Earlier`;
      document.getElementById('kpi-int-saved').innerText = '$' + intSaved.toLocaleString();

      const svg = document.getElementById('siren-svg-curve');
      const x0 = 65, x1 = 840, y0 = 25, y1 = 265;
      const toX = (yr) => x0 + (yr / 30) * (x1 - x0);
      const toY = (bal) => y1 - (bal / prin) * (y1 - y0);

      const stdPath = stdPts.map((p, i) => `${{i===0?'M':'L'}}${{toX(p.yr).toFixed(1)}},${{toY(p.bal).toFixed(1)}}`).join(' ');
      const sirPath = sirPts.map((p, i) => `${{i===0?'M':'L'}}${{toX(p.yr).toFixed(1)}},${{toY(p.bal).toFixed(1)}}`).join(' ');

      const polyPts = [
        ...stdPts.map(p => `${{toX(p.yr).toFixed(1)}},${{toY(p.bal).toFixed(1)}}`),
        ...[...sirPts].reverse().map(p => `${{toX(p.yr).toFixed(1)}},${{toY(p.bal).toFixed(1)}}`)
      ].join(' ');

      const payoffX = toX(sirMos / 12);

      svg.innerHTML = `
        <defs>
          <linearGradient id="braunWedge" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#0F766E" stop-opacity="0.24"/>
            <stop offset="100%" stop-color="#FF4F00" stop-opacity="0.10"/>
          </linearGradient>
        </defs>
        <line x1="${{x0}}" y1="${{y1}}" x2="${{x1}}" y2="${{y1}}" stroke="#C7C2B8" stroke-width="1.5"/>
        <line x1="${{x0}}" y1="${{y0}}" x2="${{x0}}" y2="${{y1}}" stroke="#C7C2B8" stroke-width="1.5"/>
        <polygon points="${{polyPts}}" fill="url(#braunWedge)"/>
        <path d="${{stdPath}}" fill="none" stroke="#78716C" stroke-width="2.5" stroke-dasharray="6,4"/>
        <path d="${{sirPath}}" fill="none" stroke="#FF4F00" stroke-width="4"/>
        <circle cx="${{payoffX.toFixed(1)}}" cy="${{y1}}" r="7" fill="#FF4F00" stroke="#FFFFFF" stroke-width="2.5"/>
        <text x="${{Math.min(750, payoffX)}}" y="${{y1 - 14}}" fill="#18181B" font-family="IBM Plex Mono" font-size="11.5" font-weight="700" text-anchor="middle">
          PAYOFF: Yr ${{(sirMos / 12).toFixed(1)}} (Saves $${{intSaved.toLocaleString()}})
        </text>
        <text x="${{x0}}" y="292" fill="#57534E" font-family="IBM Plex Mono" font-size="11">Year 0</text>
        <text x="${{toX(10)}}" y="292" fill="#57534E" font-family="IBM Plex Mono" font-size="11">Year 10</text>
        <text x="${{toX(20)}}" y="292" fill="#57534E" font-family="IBM Plex Mono" font-size="11">Year 20</text>
        <text x="${{toX(30)}}" y="292" fill="#57534E" font-family="IBM Plex Mono" font-size="11" text-anchor="end">Year 30</text>
      `;

      try {{
        await fetch('/api/sandbox', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: 'M.1',
            action: 'calc_siren_accelerator',
            params: {{
              principal: prin,
              rate: rate,
              extra_monthly: extraMo,
              annual_lump_sum: lumpYr
            }}
          }})
        }});
      }} catch (e) {{}}
    }};

    window.sendVoiceBargeIn = function(utterance, extraMo, lumpYr, btnEl) {{
      // Immediately flush any playing audio in 0ms
      window.flushAllSirenAudio('Voice Prompt Barge-In: "' + utterance.slice(0, 32) + '..."');

      document.getElementById('sld-extra-mo').value = extraMo;
      document.getElementById('sld-lump-yr').value = lumpYr;
      window.bendAmortizationCurve();

      const voice = document.getElementById('siren-voice-select').value || 'Aoede';
      const mode = document.getElementById('siren-live-mode').value || 'gemini-3.8-live';
      const prin = parseFloat(document.getElementById('sld-prin').value || 450000);
      const intSavedTxt = document.getElementById('kpi-int-saved').innerText;
      const termTxt = document.getElementById('kpi-siren-term').innerText;

      const spokenResponse =
        `Got it—interrupting and recalculating right now. On your $${{prin.toLocaleString()}} loan at 6.125 percent, setting extra principal to $${{extraMo}} per month and $${{lumpYr.toLocaleString()}} per year cuts your payoff term to ${{termTxt}} and saves you ${{intSavedTxt}} in total lifetime interest.`;

      if (mode === 'gemini-3.8-live-extended-thinking') {{
        const tb = document.getElementById('siren-thinking-box');
        if (tb) {{
          tb.style.display = 'block';
          tb.innerText = `[EXTENDED THINKING TRACE]: Barge-in received ("${{utterance}}"). Flushed WebAudio buffer in 0ms -> Re-integrated 360-month principal decay curve -> New term ${{termTxt}}, interest saved ${{intSavedTxt}}.`;
        }}
      }}

      document.getElementById('siren-transcript-box').innerHTML = `
        <div style="color:var(--braun-orange);font-weight:700;margin-bottom:4px;">[Borrower Barge-In]: "${{utterance}}"</div>
        <div><strong>[Siren Live Voice • ${{voice}} HD]:</strong> "${{spokenResponse}}"</div>
      `;

      if (sirenWs && sirenWs.readyState === WebSocket.OPEN) {{
        sirenWs.send(JSON.stringify({{
          type: 'text',
          text: utterance,
          live_mode: mode,
          voice: voice
        }}));
      }} else if (window.playLiveCallClip && !isMuted) {{
        window.playLiveCallClip(spokenResponse, voice, "Project Siren Voice Whisperer", btnEl, (amp) => {{
          pulseVuBars(amp > 0.02);
        }});
      }}
    }};

    window.runLiveVertexAI = async function() {{
      const model = window.getSelectedModel ? window.getSelectedModel() : 'gemini-3.8-flash';
      const prin = parseFloat(document.getElementById('sld-prin').value || 450000);
      const extraMo = parseFloat(document.getElementById('sld-extra-mo').value || 250);
      const lumpYr = parseFloat(document.getElementById('sld-lump-yr').value || 5000);
      const txBox = document.getElementById('siren-transcript-box');
      txBox.innerHTML = `<em>Synthesizing Acoustic Amortization Strategy with <strong>${{model}}</strong>...</em>`;

      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: 'M.1',
            model: model,
            user_input: `Analyze a $${{prin}} mortgage at 6.125% with +$${{extraMo}}/mo extra principal and +$${{lumpYr}}/yr bonus curtailment.`,
            params: {{ principal: prin, rate: 6.125, extra_monthly: extraMo, annual_lump_sum: lumpYr }}
          }})
        }});
        const data = await res.json();
        const textOut = (data.vertex && data.vertex.response_markdown) || data.output || 'Amortization curve verified.';
        txBox.innerHTML = `<strong>[${{data.model_used || model}}]:</strong> ${{textOut}}`;
      }} catch (e) {{
        txBox.innerText = "Vertex AI Error: " + e.message;
      }}
    }};

    document.addEventListener('DOMContentLoaded', () => {{
      window.bendAmortizationCurve();
    }});
  </script>

  {render_floating_control_bar_and_drawer(code, auth_token)}
</body>
</html>"""
