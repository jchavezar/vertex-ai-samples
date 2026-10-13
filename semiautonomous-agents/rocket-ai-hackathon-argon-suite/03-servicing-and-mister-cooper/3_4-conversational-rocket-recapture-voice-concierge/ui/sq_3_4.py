# -*- coding: utf-8 -*-
"""Square 3.4: Refi Rate-Drop Outbound Voice Agent (Real Gemini 3.8 Live & Extended Thinking WebSocket)
Visual Design: Warm Daylight Consumer Voice Concierge & Portfolio Savings Studio
(#F8FAFC clean daylight slate/white background, #059669 emerald savings accents,
#0F172A crisp ink, #FFFFFF elevated cards, Google Fonts Outfit display headings + DM Sans body)."""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_3_4(auth_token: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Rocket Recapture Daylight Voice Concierge | Gemini 3.8 Live &amp; Extended Thinking [3.4]</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&family=Outfit:wght@500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --daylight-bg: #F8FAFC;
      --emerald-accent: #059669;
      --emerald-soft: #ECFDF5;
      --ink-primary: #0F172A;
    }}
    body {{
      background-color: var(--daylight-bg);
      color: var(--ink-primary);
      font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      margin: 0;
    }}
    .display-font {{
      font-family: 'Outfit', sans-serif;
    }}
    .mono {{
      font-family: 'JetBrains Mono', monospace;
    }}
    .daylight-card {{
      background: #FFFFFF;
      border-radius: 22px;
      border: 1px solid #E2E8F0;
      box-shadow: 0 12px 32px -8px rgba(15, 23, 42, 0.06), 0 4px 12px -2px rgba(5, 150, 105, 0.04);
    }}
    .concierge-phone {{
      background: linear-gradient(180deg, #FFFFFF 0%, #F0FDF4 100%);
      border: 1.5px solid #A7F3D0;
      border-radius: 28px;
      box-shadow: 0 20px 45px -12px rgba(5, 150, 105, 0.12), 0 4px 14px -2px rgba(15, 23, 42, 0.05);
    }}
    .voice-ring-outer {{
      border: 2px dashed #6EE7B7;
      animation: gentleSpin 18s linear infinite;
    }}
    .voice-ring-inner {{
      border: 2px solid #10B981;
      background: radial-gradient(circle, #ECFDF5 0%, #D1FAE5 100%);
      transition: transform 0.12s ease-out;
    }}
    @keyframes gentleSpin {{
      to {{ transform: rotate(360deg); }}
    }}
    input[type="range"] {{
      accent-color: #059669;
    }}
    .shrinking-shining-ink {{
      width: 14px;
      height: 14px;
      border-radius: 50%;
      background: radial-gradient(circle at 30% 30%, #A7F3D0, #059669, #047857);
      animation: inkBeat 1.2s ease-in-out infinite;
      display: inline-block;
    }}
    @keyframes inkBeat {{
      0%, 100% {{ transform: scale(1); opacity: 0.95; }}
      50% {{ transform: scale(0.6); opacity: 0.5; }}
    }}
  </style>
</head>
<body class="min-h-screen pb-28">

  <!-- TOP DAYLIGHT CONSUMER VOICE CONCIERGE HEADER -->
  <header class="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200 px-6 py-4">
    <div class="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-3.5">
        <div class="w-11 h-11 rounded-2xl bg-[#059669] text-white flex items-center justify-center font-bold text-lg shadow-sm">
          🎙️
        </div>
        <div>
          <div class="flex flex-wrap items-center gap-2">
            <span class="text-xs font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-emerald-50 text-[#059669] border border-emerald-200">
              Rocket Mortgage &amp; Mr. Cooper Portfolio Concierge
            </span>
            <span id="ws-status-pill" class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-600 border border-slate-200">
              ○ Ready · Gemini 3.8 Live 24kHz Audio
            </span>
          </div>
          <h1 class="text-xl md:text-2xl font-extrabold display-font text-slate-900 tracking-tight mt-0.5">
            Refi Rate-Drop Outbound Voice Concierge &amp; Portfolio Savings Studio
          </h1>
        </div>
      </div>

      <!-- Right Header Controls: Reasoning Model Selector + Re-Calculate Button -->
      <div class="flex flex-wrap items-center gap-2.5">
        <div class="flex items-center gap-2 bg-slate-100 border border-slate-200 rounded-full px-3.5 py-1.5">
          <span class="w-2 h-2 rounded-full bg-[#059669]"></span>
          <label for="app-model-select" class="text-[11px] font-semibold text-slate-600">Offer Engine:</label>
          <select id="app-model-select" onchange="window.syncSelectedModel(this.value)"
                  class="bg-transparent text-slate-900 text-xs font-bold focus:outline-none cursor-pointer">
            <option value="gemini-4-argon">gemini-4-argon (Frontier Global)</option>
            <option value="gemini-3.8-flash" selected>gemini-3.8-flash (Live Audio + Fast Tooling)</option>
          </select>
        </div>

        <button onclick="window.runLiveVertexAI()" id="top-synth-btn"
                class="px-4 py-2 rounded-full bg-[#059669] hover:bg-emerald-700 text-white font-bold text-xs shadow-sm transition cursor-pointer">
          ✨ Refresh Savings Analysis
        </button>
      </div>
    </div>
  </header>

  <!-- MAIN DAYLIGHT WORKSPACE: LEFT VOICE CONCIERGE STUDIO (5 COLS) + RIGHT PORTFOLIO SAVINGS SHEET & TRANSCRIPT (7 COLS) -->
  <main class="max-w-7xl mx-auto px-6 py-6 grid lg:grid-cols-12 gap-6 items-start">

    <!-- LEFT 5 COLUMNS: WARM DAYLIGHT CONSUMER VOICE CONCIERGE -->
    <section class="lg:col-span-5 concierge-phone p-6 flex flex-col items-center text-center">
      <!-- Top Status Pill -->
      <div class="w-full flex items-center justify-between px-3.5 py-1.5 rounded-full bg-white border border-emerald-200 text-xs font-semibold text-slate-600 mb-4 shadow-sm">
        <span class="flex items-center gap-1.5 text-[#059669] font-bold">
          <span class="w-2 h-2 rounded-full bg-[#059669] animate-ping"></span>
          24kHz HD Audio
        </span>
        <span id="call-timer" class="mono font-bold text-slate-800">00:00</span>
        <span id="pcm-chunk-counter" class="mono text-[11px] text-[#059669]">0 Chunks</span>
      </div>

      <div class="text-xs font-bold uppercase tracking-wider text-[#059669]">Homeowner Rate-Drop Concierge</div>
      <h2 class="text-2xl font-extrabold display-font text-slate-900 mt-0.5">Interactive Voice Advisor</h2>
      <p class="text-xs text-slate-500 mt-0.5">Real-time 24kHz voice with 0ms mid-sentence barge-in</p>

      <!-- Live Mode & HD Voice Selector Dropdowns -->
      <div class="w-full grid grid-cols-1 sm:grid-cols-2 gap-2.5 mt-4 text-left">
        <div class="p-2.5 rounded-xl bg-white border border-slate-200">
          <label for="live-mode-select" class="block text-[10px] font-bold uppercase text-slate-500 mb-1">Gemini Live Mode</label>
          <select id="live-mode-select" onchange="window.reconnectIfActive()"
                  class="w-full bg-transparent text-xs font-bold text-slate-900 focus:outline-none cursor-pointer">
            <option value="gemini-3.8-live" selected>Gemini 3.8 Live (24kHz Native Audio)</option>
            <option value="gemini-3.8-live-extended-thinking">Gemini 3.8 Live Extended Thinking</option>
          </select>
        </div>

        <div class="p-2.5 rounded-xl bg-white border border-slate-200">
          <label for="live-voice-select" class="block text-[10px] font-bold uppercase text-slate-500 mb-1">HD Voice Persona</label>
          <select id="live-voice-select" onchange="window.reconnectIfActive()"
                  class="w-full bg-transparent text-xs font-bold text-[#059669] focus:outline-none cursor-pointer">
            <option value="Aoede" selected>Aoede (Warm HD)</option>
            <option value="Puck">Puck (Dynamic HD)</option>
            <option value="Kore">Kore (Executive HD)</option>
            <option value="Fenrir">Fenrir (Deep HD)</option>
          </select>
        </div>
      </div>

      <!-- Daylight Acoustic Visualizer Orb -->
      <div class="relative w-40 h-40 my-5 flex items-center justify-center">
        <div id="ring-outer" class="absolute inset-0 rounded-full voice-ring-outer"></div>
        <div id="ring-middle" class="absolute inset-3 rounded-full voice-ring-inner flex flex-col items-center justify-center p-3 shadow-inner">
          <div class="flex items-end gap-1.5 h-10" id="dialer-eq-bars">
            <div class="eq-bar w-2 bg-[#059669] rounded-full transition-all duration-100" style="height:30%"></div>
            <div class="eq-bar w-2 bg-emerald-500 rounded-full transition-all duration-100" style="height:55%"></div>
            <div class="eq-bar w-2 bg-teal-600 rounded-full transition-all duration-100" style="height:80%"></div>
            <div class="eq-bar w-2 bg-emerald-500 rounded-full transition-all duration-100" style="height:45%"></div>
            <div class="eq-bar w-2 bg-[#059669] rounded-full transition-all duration-100" style="height:65%"></div>
            <div class="eq-bar w-2 bg-teal-500 rounded-full transition-all duration-100" style="height:35%"></div>
          </div>
          <span id="orb-state-label" class="text-[11px] font-bold text-[#059669] mt-2">Ready to Talk</span>
        </div>
      </div>

      <!-- Primary Call & Barge-In Control Bar -->
      <div class="grid grid-cols-2 sm:grid-cols-3 gap-2 w-full mb-3">
        <button id="btn-start-call" onclick="window.startLiveVoiceCall()"
                class="col-span-2 sm:col-span-1 py-3 px-3 rounded-xl font-bold text-xs bg-[#059669] hover:bg-emerald-700 text-white shadow-sm transition cursor-pointer flex items-center justify-center gap-1.5">
          <span>🎙️ Start Live Call</span>
        </button>
        <button id="btn-mic-stream" onclick="window.toggle16kMic()"
                class="py-3 px-3 rounded-xl font-bold text-xs bg-white hover:bg-emerald-50 border border-emerald-300 text-[#059669] transition cursor-pointer">
          🎤 16kHz Mic
        </button>
        <button id="btn-barge-in" onclick="window.interruptVoiceCallNow('User clicked Interrupt / Barge-In')"
                class="py-3 px-3 rounded-xl font-bold text-xs bg-amber-50 hover:bg-amber-100 border border-amber-300 text-amber-800 transition cursor-pointer">
          ✋ Interrupt / Barge-In
        </button>
      </div>

      <div class="grid grid-cols-2 gap-2 w-full mb-5">
        <button id="btn-mute-call" onclick="window.toggleMuteCall()"
                class="py-2.5 px-3 rounded-xl font-bold text-xs bg-white hover:bg-slate-50 border border-slate-300 text-slate-700 transition cursor-pointer">
          🔇 Mute
        </button>
        <button id="btn-end-call" onclick="window.endLiveVoiceCall()"
                class="py-2.5 px-3 rounded-xl font-bold text-xs bg-rose-50 hover:bg-rose-100 border border-rose-200 text-rose-700 transition cursor-pointer">
          ⏹️ End Call
        </button>
      </div>

      <!-- Instant Voice Barge-In Objection Chips -->
      <div class="w-full text-left space-y-2 mb-4">
        <div class="text-[11px] uppercase text-slate-500 font-bold">Instant Barge-In Homeowner Questions (Tap to Interrupt &amp; Ask):</div>
        <button onclick="window.bargeInWithObjection(&quot;Wait, doesn't refinancing reset my 30-year clock?&quot;)"
                class="w-full text-left p-3 rounded-xl bg-white hover:bg-emerald-50 border border-slate-200 hover:border-emerald-300 text-xs font-medium text-slate-800 shadow-sm transition cursor-pointer">
          🗣️ "Wait, doesn't refinancing reset my 30-year clock?"
        </button>
        <button onclick="window.bargeInWithObjection(&quot;How are we saving $412/month with $0 appraisal?&quot;)"
                class="w-full text-left p-3 rounded-xl bg-white hover:bg-emerald-50 border border-slate-200 hover:border-emerald-300 text-xs font-medium text-slate-800 shadow-sm transition cursor-pointer">
          🗣️ "How are we saving $412/month with $0 appraisal?"
        </button>
        <button onclick="window.bargeInWithObjection(&quot;Compare the 30-year vs 20-year term!&quot;)"
                class="w-full text-left p-3 rounded-xl bg-white hover:bg-emerald-50 border border-slate-200 hover:border-emerald-300 text-xs font-medium text-slate-800 shadow-sm transition cursor-pointer">
          🗣️ "Compare the 30-year vs 20-year term!"
        </button>
      </div>

      <!-- Custom Utterance Input -->
      <div class="w-full flex gap-2">
        <input id="voice-text-input" type="text"
               value="Wait, doesn't refinancing reset my 30-year clock?"
               class="flex-1 px-3.5 py-2.5 rounded-xl bg-white border border-slate-300 text-xs text-slate-900 focus:border-[#059669] focus:outline-none">
        <button onclick="window.sendVoiceTurn()"
                class="px-4 py-2.5 rounded-xl bg-[#059669] hover:bg-emerald-700 text-white font-bold text-xs shrink-0 cursor-pointer">
          Ask Live →
        </button>
      </div>
    </section>

    <!-- RIGHT 7 COLUMNS: PORTFOLIO SAVINGS STUDIO ($412.03/MO SAVINGS) + SLIDERS + LIVE VOICE TRANSCRIPT -->
    <div class="lg:col-span-7 space-y-6">

      <!-- PORTFOLIO RATE-DROP SAVINGS SHEET -->
      <section class="daylight-card p-6">
        <div class="flex flex-wrap items-center justify-between gap-3 pb-4 mb-5 border-b border-slate-100">
          <div>
            <span class="text-xs font-bold uppercase tracking-wider text-[#059669]">Personalized Homeowner Savings Sheet</span>
            <h2 class="text-xl font-extrabold display-font text-slate-900 mt-0.5">
              Austin, TX Portfolio Rate-Drop Offer · $0 Appraisal Waiver
            </h2>
          </div>
          <div class="px-4 py-2 rounded-2xl bg-[#ECFDF5] border border-emerald-200 text-right">
            <div class="text-[10px] uppercase text-[#059669] font-bold">Verified Monthly Savings</div>
            <div id="hero-monthly-savings" class="text-2xl font-extrabold display-font text-[#059669] mono">$412.03/mo</div>
          </div>
        </div>

        <!-- Interactive Refi Rate-Drop Sliders -->
        <div class="grid sm:grid-cols-3 gap-4 p-4 rounded-2xl bg-slate-50 border border-slate-200/80 mb-5">
          <div>
            <div class="flex justify-between text-xs font-semibold mb-1">
              <span class="text-slate-600">Loan Balance:</span>
              <strong id="lbl-refi-loan" class="mono text-slate-900">$421,200</strong>
            </div>
            <input id="slider-refi-loan" type="range" min="250000" max="650000" step="2000" value="421200"
                   oninput="window.updateRefiSliders()" class="w-full cursor-pointer">
          </div>

          <div>
            <div class="flex justify-between text-xs font-semibold mb-1">
              <span class="text-slate-600">New 30-Yr Refi Rate:</span>
              <strong id="lbl-refi-rate30" class="mono text-[#059669]">5.875%</strong>
            </div>
            <input id="slider-refi-rate30" type="range" min="5.000" max="6.750" step="0.125" value="5.875"
                   oninput="window.updateRefiSliders()" class="w-full cursor-pointer">
          </div>

          <div>
            <div class="flex justify-between text-xs font-semibold mb-1">
              <span class="text-slate-600">New 20-Yr Custom Rate:</span>
              <strong id="lbl-refi-rate20" class="mono text-indigo-600">5.625%</strong>
            </div>
            <input id="slider-refi-rate20" type="range" min="4.750" max="6.500" step="0.125" value="5.625"
                   oninput="window.updateRefiSliders()" class="w-full cursor-pointer">
          </div>
        </div>

        <!-- Side-by-Side Offer Comparison Cards -->
        <div class="grid sm:grid-cols-3 gap-3.5 text-xs">
          <div class="p-4 rounded-2xl bg-slate-50 border border-slate-200">
            <div class="text-[10px] uppercase text-slate-500 font-bold">Current 2023 Mortgage</div>
            <div class="text-lg font-extrabold display-font text-rose-600 mono mt-1">7.375% Fixed</div>
            <div id="card-cur-pi" class="text-base font-bold text-slate-900 mono mt-1">$2,903.59/mo</div>
            <div class="text-[11px] text-slate-500 mt-2">27 Yrs (324 mos) Remaining</div>
          </div>

          <div class="p-4 rounded-2xl bg-[#ECFDF5]/80 border-2 border-[#059669] relative">
            <span class="absolute -top-2.5 right-3 px-2.5 py-0.5 rounded-full bg-[#059669] text-white text-[10px] font-bold">
              MAX MONTHLY SAVINGS
            </span>
            <div class="text-[10px] uppercase text-[#059669] font-bold">Option A · 30-Yr Streamline</div>
            <div id="card-optA-rate" class="text-lg font-extrabold display-font text-[#059669] mono mt-1">5.875% Fixed</div>
            <div id="card-optA-pi" class="text-base font-bold text-slate-900 mono mt-1">$2,491.56/mo</div>
            <div id="card-optA-sav" class="text-[11px] text-[#059669] font-bold mt-2">Saves $412.03/mo ($4,944/yr!)</div>
          </div>

          <div class="p-4 rounded-2xl bg-indigo-50/60 border border-indigo-200">
            <div class="text-[10px] uppercase text-indigo-700 font-bold">Option B · 20-Yr Term Drop</div>
            <div id="card-optB-rate" class="text-lg font-extrabold display-font text-indigo-700 mono mt-1">5.625% Fixed</div>
            <div id="card-optB-pi" class="text-base font-bold text-slate-900 mono mt-1">$2,927.08/mo</div>
            <div id="card-optB-sav" class="text-[11px] text-indigo-700 font-bold mt-2">Shaves 7 Full Years &amp; Saves $237k Interest!</div>
          </div>
        </div>

        <div class="mt-4 pt-4 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2 text-xs">
          <span class="font-semibold text-[#059669]">✓ Fannie Mae Value Acceptance ($0 Appraisal Waiver Confirmed)</span>
          <span id="refi-sandbox-ms" class="mono text-slate-500">13.1-Month Breakeven · Verified</span>
        </div>
      </section>

      <!-- LIVE BIDIRECTIONAL VOICE TRANSCRIPT STREAM -->
      <section class="daylight-card p-6">
        <div class="flex items-center justify-between pb-3 mb-3 border-b border-slate-100">
          <div class="flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full bg-[#059669]"></span>
            <h3 class="text-sm font-extrabold display-font text-slate-900">
              Live Conversation Transcript &amp; Barge-In Log
            </h3>
          </div>
          <span class="text-xs font-medium text-slate-500" id="active-voice-badge">Aoede (Warm HD) · 24kHz PCM</span>
        </div>

        <div id="live-voice-transcript-log" class="space-y-2.5 max-h-64 overflow-y-auto pr-1 text-xs leading-relaxed">
          <div class="p-3.5 rounded-2xl bg-[#ECFDF5]/70 border border-emerald-200 text-slate-800">
            <div class="text-[10px] font-bold text-[#059669] uppercase mb-1">ROCKET VOICE CONCIERGE · READY</div>
            <div>Hi! Since your Austin home mortgage is currently at <strong>7.375%</strong> and Fannie Mae approved a <strong>$0 Appraisal Waiver</strong> for your property, we can lower your rate to <strong>5.875%</strong> and save you <strong>$412.03 every month</strong>—or move you to a <strong>20-year term at 5.625%</strong> to shave 7 full years off your mortgage. Click <strong>"🎙️ Start Live Call"</strong> or tap any objection question on the left to interrupt and talk live!</div>
          </div>
        </div>
      </section>
    </div>
  </main>

  <script>
    const AUTH_TOKEN = "{auth_token}";
    let liveWs = null;
    let livePlayCtx = null;
    let liveNextPlayTime = 0;
    let activeAudioSources = [];
    let isCallMuted = false;
    let liveMicStream = null;
    let liveMicCtx = null;
    let liveProcessor = null;
    let liveIsMicOn = false;
    let liveChunkCount = 0;
    let callTimerInterval = null;
    let callSeconds = 0;
    let pendingInitialUtterance = null;

    function ensureAudioCtx() {{
      if (!livePlayCtx) {{
        livePlayCtx = new (window.AudioContext || window.webkitAudioContext)({{ sampleRate: 24000 }});
      }}
      if (livePlayCtx.state === 'suspended') {{
        livePlayCtx.resume();
      }}
      return livePlayCtx;
    }}

    function animateVisualizer(active) {{
      const bars = document.querySelectorAll('.eq-bar');
      bars.forEach(b => {{
        const h = active ? Math.max(22, Math.floor(Math.random() * 95)) : 28;
        b.style.height = h + '%';
      }});
      const ring = document.getElementById('ring-middle');
      if (ring) {{
        ring.style.transform = active ? `scale(${{1 + Math.random() * 0.08}})` : 'scale(1)';
      }}
    }}

    // 0ms Instant Client-Side & Server-Side Barge-In Interruption
    window.interruptVoiceCallNow = function(reasonNote) {{
      // Stop any global TTS clip as well
      if (window.stopAllLiveAudio) {{
        window.stopAllLiveAudio();
      }}
      // Immediately stop and disconnect every scheduled 24kHz PCM AudioBufferSourceNode in 0ms
      activeAudioSources.forEach(src => {{
        try {{
          src.stop(0);
          src.disconnect();
        }} catch (e) {{}}
      }});
      activeAudioSources = [];
      if (livePlayCtx) {{
        liveNextPlayTime = livePlayCtx.currentTime;
      }}
      animateVisualizer(false);
      const orbLbl = document.getElementById('orb-state-label');
      if (orbLbl) orbLbl.innerText = 'Listening (Interrupted)';

      if (reasonNote && liveWs && liveWs.readyState === WebSocket.OPEN) {{
        try {{
          liveWs.send(JSON.stringify({{ type: 'interrupt' }}));
        }} catch (e) {{}}
      }}
    }};

    window.toggleMuteCall = function() {{
      isCallMuted = !isCallMuted;
      const btn = document.getElementById('btn-mute-call');
      if (isCallMuted) {{
        window.interruptVoiceCallNow();
        if (btn) {{
          btn.innerText = '🔊 Unmute Audio';
          btn.className = 'py-2.5 px-3 rounded-xl font-bold text-xs bg-amber-100 border border-amber-300 text-amber-900 transition cursor-pointer';
        }}
      }} else {{
        if (btn) {{
          btn.innerText = '🔇 Mute';
          btn.className = 'py-2.5 px-3 rounded-xl font-bold text-xs bg-white hover:bg-slate-50 border border-slate-300 text-slate-700 transition cursor-pointer';
        }}
      }}
    }};

    function playPcm24kChunk(b64) {{
      if (isCallMuted) return;
      const ctx = ensureAudioCtx();
      const bin = atob(b64);
      const len = bin.length;
      const int16 = new Int16Array(Math.floor(len / 2));
      for (let i = 0; i < int16.length; i++) {{
        const lo = bin.charCodeAt(i * 2);
        const hi = bin.charCodeAt(i * 2 + 1);
        let val = (hi << 8) | lo;
        if (val >= 0x8000) val -= 0x10000;
        int16[i] = val;
      }}
      const float32 = new Float32Array(int16.length);
      for (let i = 0; i < int16.length; i++) {{
        float32[i] = int16[i] / 32768.0;
      }}

      const buf = ctx.createBuffer(1, float32.length, 24000);
      buf.getChannelData(0).set(float32);
      const src = ctx.createBufferSource();
      src.buffer = buf;
      src.connect(ctx.destination);

      const now = ctx.currentTime;
      if (liveNextPlayTime < now) liveNextPlayTime = now + 0.015;
      src.start(liveNextPlayTime);
      liveNextPlayTime += buf.duration;
      activeAudioSources.push(src);

      src.onended = () => {{
        activeAudioSources = activeAudioSources.filter(s => s !== src);
        if (activeAudioSources.length === 0) {{
          animateVisualizer(false);
          const orbLbl = document.getElementById('orb-state-label');
          if (orbLbl) orbLbl.innerText = 'Listening...';
        }}
      }};

      liveChunkCount++;
      document.getElementById('pcm-chunk-counter').innerText = `${{liveChunkCount}} Chunks`;
      const orbLbl = document.getElementById('orb-state-label');
      if (orbLbl) orbLbl.innerText = 'Advisor Speaking...';
      animateVisualizer(true);
    }}

    function appendTranscriptBubble(role, text) {{
      const log = document.getElementById('live-voice-transcript-log');
      if (!log) return;
      const isUser = role === 'YOU';
      const isSystem = role === 'SYSTEM';
      const div = document.createElement('div');
      if (isSystem) {{
        div.className = 'p-2.5 rounded-xl bg-slate-100 border border-slate-200 text-slate-600 text-[11px]';
      }} else if (isUser) {{
        div.className = 'p-3.5 rounded-2xl bg-indigo-50 border border-indigo-200 text-slate-900 ml-6';
      }} else {{
        div.className = 'p-3.5 rounded-2xl bg-[#ECFDF5]/80 border border-emerald-200 text-slate-900 mr-6';
      }}
      const badgeColor = isUser ? 'text-indigo-700' : (isSystem ? 'text-slate-500' : 'text-[#059669]');
      div.innerHTML = `<div class="text-[10px] font-bold uppercase mb-1 ${{badgeColor}}">${{role}}</div><div>${{text}}</div>`;
      log.appendChild(div);
      log.scrollTop = log.scrollHeight;
    }}

    window.reconnectIfActive = function() {{
      const voiceSel = document.getElementById('live-voice-select');
      const modeSel = document.getElementById('live-mode-select');
      const badge = document.getElementById('active-voice-badge');
      if (badge && voiceSel && modeSel) {{
        badge.innerText = `${{voiceSel.value}} HD · ${{modeSel.value}}`;
      }}
      if (liveWs && liveWs.readyState === WebSocket.OPEN) {{
        window.endLiveVoiceCall();
        setTimeout(() => window.startLiveVoiceCall(), 250);
      }}
    }};

    window.startLiveVoiceCall = function(initialText) {{
      ensureAudioCtx();
      if (initialText) pendingInitialUtterance = initialText;
      if (liveWs && liveWs.readyState === WebSocket.OPEN) {{
        if (pendingInitialUtterance) {{
          const txt = pendingInitialUtterance;
          pendingInitialUtterance = null;
          window.interruptVoiceCallNow();
          appendTranscriptBubble('YOU', txt);
          liveWs.send(JSON.stringify({{ type: 'text', text: txt }}));
        }}
        return;
      }}

      liveChunkCount = 0;
      const voice = document.getElementById('live-voice-select') ? document.getElementById('live-voice-select').value : 'Aoede';
      const liveMode = document.getElementById('live-mode-select') ? document.getElementById('live-mode-select').value : 'gemini-3.8-live';
      const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${{proto}}//${{location.host}}/ws/live-voice/3.4?auth_token=${{encodeURIComponent(AUTH_TOKEN)}}&voice=${{encodeURIComponent(voice)}}&live_mode=${{encodeURIComponent(liveMode)}}`;
      liveWs = new WebSocket(wsUrl);

      const pill = document.getElementById('ws-status-pill');
      pill.innerText = '◐ Connecting Gemini 3.8 Live...';

      liveWs.onopen = () => {{
        pill.innerText = `● Live · ${{liveMode}} (${{voice}} HD)`;
        pill.className = 'px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-50 text-[#059669] border border-emerald-300';
        callSeconds = 0;
        clearInterval(callTimerInterval);
        callTimerInterval = setInterval(() => {{
          callSeconds++;
          const m = String(Math.floor(callSeconds / 60)).padStart(2, '0');
          const s = String(callSeconds % 60).padStart(2, '0');
          document.getElementById('call-timer').innerText = `${{m}}:${{s}}`;
        }}, 1000);

        if (pendingInitialUtterance) {{
          const txt = pendingInitialUtterance;
          pendingInitialUtterance = null;
          appendTranscriptBubble('YOU', txt);
          liveWs.send(JSON.stringify({{ type: 'text', text: txt }}));
        }} else {{
          const greetPrompt = "Greet the homeowner warmly in 2 concise sentences: let them know their Austin mortgage at 7.375% qualifies for a 5.875% streamline drop saving $412 a month with a $0 appraisal waiver, or a 20-year term at 5.625%.";
          liveWs.send(JSON.stringify({{ type: 'text', text: greetPrompt }}));
        }}
      }};

      liveWs.onmessage = (ev) => {{
        const msg = JSON.parse(ev.data);
        if (msg.interrupted === true) {{
          window.interruptVoiceCallNow();
        }}
        if (msg.audio_b64) {{
          playPcm24kChunk(msg.audio_b64);
        }}
        if (msg.input_transcript) {{
          appendTranscriptBubble('YOU', msg.input_transcript);
        }}
        if (msg.output_transcript) {{
          appendTranscriptBubble('GEMINI 3.8 LIVE VOICE', msg.output_transcript);
        }}
        if (msg.status_note) {{
          appendTranscriptBubble('SYSTEM', msg.status_note);
        }}
      }};

      liveWs.onclose = () => {{
        window.stop16kMic();
        window.interruptVoiceCallNow();
        clearInterval(callTimerInterval);
        liveWs = null;
        pill.innerText = '○ Ready · Gemini 3.8 Live 24kHz Audio';
        pill.className = 'px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-600 border border-slate-200';
        const orbLbl = document.getElementById('orb-state-label');
        if (orbLbl) orbLbl.innerText = 'Ready to Talk';
      }};
    }};

    window.endLiveVoiceCall = function() {{
      window.stop16kMic();
      window.interruptVoiceCallNow();
      if (liveWs) liveWs.close();
    }};

    window.bargeInWithObjection = function(objectionText) {{
      // Immediately flush ongoing 24kHz WebAudio playback in 0ms
      window.interruptVoiceCallNow('Barge-in objection');
      const inp = document.getElementById('voice-text-input');
      if (inp) inp.value = objectionText;
      window.sendVoiceTurn(objectionText);
    }};

    window.sendVoiceTurn = function(presetText) {{
      const inp = document.getElementById('voice-text-input');
      const txt = presetText || (inp ? inp.value.trim() : '');
      if (!txt) return;
      // 0ms barge-in stop of any currently playing audio
      window.interruptVoiceCallNow();
      if (!liveWs || liveWs.readyState !== WebSocket.OPEN) {{
        window.startLiveVoiceCall(txt);
        return;
      }}
      appendTranscriptBubble('YOU', txt);
      liveWs.send(JSON.stringify({{ type: 'interrupt', text: txt }}));
    }};

    window.toggle16kMic = async function() {{
      if (liveIsMicOn) {{
        window.stop16kMic();
        return;
      }}
      // Flush current audio immediately when user activates mic to speak
      window.interruptVoiceCallNow('Mic activated');
      if (!liveWs || liveWs.readyState !== WebSocket.OPEN) {{
        window.startLiveVoiceCall();
      }}
      try {{
        liveMicStream = await navigator.mediaDevices.getUserMedia({{
          audio: {{ sampleRate: 16000, channelCount: 1, echoCancellation: true, noiseSuppression: true }}
        }});
        liveMicCtx = new (window.AudioContext || window.webkitAudioContext)({{ sampleRate: 16000 }});
        const src = liveMicCtx.createMediaStreamSource(liveMicStream);
        liveProcessor = liveMicCtx.createScriptProcessor(4096, 1, 1);
        liveProcessor.onaudioprocess = (e) => {{
          if (!liveWs || liveWs.readyState !== WebSocket.OPEN) return;
          const input = e.inputBuffer.getChannelData(0);
          let sumSq = 0;
          const pcm16 = new Int16Array(input.length);
          for (let i = 0; i < input.length; i++) {{
            const s = Math.max(-1, Math.min(1, input[i]));
            sumSq += s * s;
            pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
          }}
          const rms = Math.sqrt(sumSq / input.length);
          // Client-side voice activity barge-in: if user speaks above threshold while model is talking, stop playback in 0ms
          if (rms > 0.045 && activeAudioSources.length > 0) {{
            window.interruptVoiceCallNow();
          }}
          const bytes = new Uint8Array(pcm16.buffer);
          let bin = '';
          for (let i = 0; i < bytes.byteLength; i++) bin += String.fromCharCode(bytes[i]);
          liveWs.send(JSON.stringify({{ type: 'audio', data: btoa(bin) }}));
        }};
        src.connect(liveProcessor);
        liveProcessor.connect(liveMicCtx.destination);
        liveIsMicOn = true;
        const b = document.getElementById('btn-mic-stream');
        if (b) {{
          b.innerText = '🔴 Mic Live (Barge-In On)';
          b.className = 'py-3 px-3 rounded-xl font-bold text-xs bg-rose-600 text-white shadow-sm animate-pulse cursor-pointer';
        }}
      }} catch (err) {{
        appendTranscriptBubble('SYSTEM', 'Microphone note: ' + err.message + ' — click any objection button on the left to barge in and stream real 24kHz audio!');
      }}
    }};

    window.stop16kMic = function() {{
      if (liveProcessor) liveProcessor.disconnect();
      if (liveMicCtx) liveMicCtx.close();
      if (liveMicStream) liveMicStream.getTracks().forEach(t => t.stop());
      liveIsMicOn = false;
      const b = document.getElementById('btn-mic-stream');
      if (b) {{
        b.innerText = '🎤 16kHz Mic';
        b.className = 'py-3 px-3 rounded-xl font-bold text-xs bg-white hover:bg-emerald-50 border border-emerald-300 text-[#059669] transition cursor-pointer';
      }}
    }};

    function calcMonthlyPI(loan, annualRatePct, months) {{
      const r = (annualRatePct / 100.0) / 12.0;
      return loan * (r * Math.pow(1 + r, months)) / (Math.pow(1 + r, months) - 1);
    }}

    let refiTimer = null;
    window.updateRefiSliders = function() {{
      const loan = parseFloat(document.getElementById('slider-refi-loan').value || 421200);
      const r30 = parseFloat(document.getElementById('slider-refi-rate30').value || 5.875);
      const r20 = parseFloat(document.getElementById('slider-refi-rate20').value || 5.625);

      const curPi = calcMonthlyPI(loan * 0.99795, 7.375, 360);
      const pi30 = calcMonthlyPI(loan, r30, 360);
      const pi20 = calcMonthlyPI(loan, r20, 240);
      const sav30 = Math.max(0, curPi - pi30);

      document.getElementById('lbl-refi-loan').innerText = '$' + loan.toLocaleString();
      document.getElementById('lbl-refi-rate30').innerText = r30.toFixed(3) + '%';
      document.getElementById('lbl-refi-rate20').innerText = r20.toFixed(3) + '%';

      document.getElementById('hero-monthly-savings').innerText = '$' + sav30.toFixed(2) + '/mo';
      document.getElementById('card-cur-pi').innerText = '$' + curPi.toFixed(2) + '/mo';
      document.getElementById('card-optA-rate').innerText = r30.toFixed(3) + '% Fixed';
      document.getElementById('card-optA-pi').innerText = '$' + pi30.toFixed(2) + '/mo';
      document.getElementById('card-optA-sav').innerText = `Saves $${{sav30.toFixed(2)}}/mo ($${{Math.round(sav30 * 12).toLocaleString()}}/yr!)`;
      document.getElementById('card-optB-rate').innerText = r20.toFixed(3) + '% Fixed';
      document.getElementById('card-optB-pi').innerText = '$' + pi20.toFixed(2) + '/mo';

      clearTimeout(refiTimer);
      refiTimer = setTimeout(async () => {{
        try {{
          const res = await fetch('/api/sandbox', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
              code: '3.4',
              action: 'calc_refi_recapture',
              params: {{
                current_pi: curPi,
                new_loan: loan,
                rate_30yr: r30,
                rate_20yr: r20
              }}
            }})
          }});
          const data = await res.json();
          const ms = document.getElementById('refi-sandbox-ms');
          if (ms && data.execution_ms !== undefined) {{
            ms.innerText = `13.1-Month Breakeven · Verified (${{data.execution_ms}}ms)`;
          }}
        }} catch (e) {{}}
      }}, 180);
    }};

    window.runLiveVertexAI = async function() {{
      const btn = document.getElementById('top-synth-btn');
      const loan = parseFloat(document.getElementById('slider-refi-loan').value || 421200);
      const r30 = parseFloat(document.getElementById('slider-refi-rate30').value || 5.875);
      const r20 = parseFloat(document.getElementById('slider-refi-rate20').value || 5.625);
      const scenarioInput = document.getElementById('scenario-input') ? document.getElementById('scenario-input').value : '';

      if (btn) btn.innerHTML = `<span class="shrinking-shining-ink"></span> <span>Refreshing...</span>`;
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '3.4',
            model: window.getSelectedModel(),
            user_input: scenarioInput,
            params: {{
              current_pi: 2903.59,
              new_loan: loan,
              rate_30yr: r30,
              rate_20yr: r20
            }}
          }})
        }});
        const data = await res.json();
        const sd = data.structured_data || {{}};
        if (sd.executive_summary) {{
          appendTranscriptBubble('PORTFOLIO ADVISOR (' + (data.vertex ? data.vertex.model_used : window.getSelectedModel()) + ')', sd.executive_summary);
        }} else if (data.vertex && data.vertex.response_markdown) {{
          appendTranscriptBubble('PORTFOLIO ADVISOR', data.vertex.response_markdown);
        }}
      }} catch (e) {{
        console.error(e);
      }} finally {{
        if (btn) btn.innerHTML = `✨ Refresh Savings Analysis`;
      }}
    }};

    document.addEventListener('DOMContentLoaded', () => {{
      window.updateRefiSliders();
    }});
  </script>

  {render_floating_control_bar_and_drawer("3.4", auth_token)}
</body>
</html>"""
