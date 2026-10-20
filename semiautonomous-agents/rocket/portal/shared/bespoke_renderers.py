# -*- coding: utf-8 -*-
"""Client-side JavaScript Renderer for all 33 Bespoke Use-Case App Archetypes,
Real Gemini Multimodal Live API WebSocket Audio (`gemini-live-2.5-flash-native-audio`),
and Real Gemini Enterprise Discovery Engine `streamAssist` UI + Console Links."""

BESPOKE_RENDERER_JS = r"""
// ============================================================================
// 1. REAL GEMINI MULTIMODAL LIVE API WEBSOCKET CLIENT (16kHz Mic -> 24kHz PCM)
// ============================================================================
let liveWs = null;
let livePlayCtx = null;
let liveNextPlayTime = 0;
let liveMicStream = null;
let liveMicCtx = null;
let liveProcessor = null;
let liveIsMicOn = false;
let liveAudioChunkCount = 0;
let eqInterval = null;

function ensureLiveAudioContext() {
  if (!livePlayCtx) {
    livePlayCtx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 24000 });
  }
  if (livePlayCtx.state === 'suspended') {
    livePlayCtx.resume();
  }
}

function playLivePcm24k(base64Data) {
  ensureLiveAudioContext();
  const bin = atob(base64Data);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  const int16 = new Int16Array(bytes.buffer);
  const float32 = new Float32Array(int16.length);
  for (let i = 0; i < int16.length; i++) float32[i] = int16[i] / 32768.0;

  const buffer = livePlayCtx.createBuffer(1, float32.length, 24000);
  buffer.getChannelData(0).set(float32);

  const src = livePlayCtx.createBufferSource();
  src.buffer = buffer;
  src.connect(livePlayCtx.destination);

  const now = livePlayCtx.currentTime;
  if (liveNextPlayTime < now) liveNextPlayTime = now + 0.02;
  src.start(liveNextPlayTime);
  liveNextPlayTime += buffer.duration;

  liveAudioChunkCount++;
  const badge = document.getElementById('live-audio-chunks-badge');
  if (badge) badge.textContent = `${liveAudioChunkCount} PCM Chunks (24kHz)`;
  animateEqBars(true);
}

function animateEqBars(active) {
  const bars = document.querySelectorAll('.live-eq-bar');
  bars.forEach((b, i) => {
    const h = active ? Math.max(15, Math.floor(Math.random() * 96)) : 18;
    b.style.height = `${h}%`;
  });
}

function appendLiveTranscript(role, text) {
  const log = document.getElementById('live-voice-transcript-log');
  if (!log) return;
  const div = document.createElement('div');
  const isUser = role === 'YOU';
  div.className = `p-3 rounded-xl border text-xs mono mb-2 ${isUser ? 'bg-cyan-950/40 border-cyan-500/40 text-cyan-200 ml-6' : 'bg-slate-900/90 border-teal-500/40 text-white mr-6'}`;
  div.innerHTML = `<div class="text-[10px] font-bold uppercase mb-1 ${isUser ? 'text-cyan-400' : 'text-teal-400'}">${role} • LIVE AUDIO STREAM</div><div>${text}</div>`;
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
}

function toggleGeminiLiveSession(code) {
  if (liveWs && liveWs.readyState === WebSocket.OPEN) {
    liveWs.close();
    return;
  }
  ensureLiveAudioContext();
  liveAudioChunkCount = 0;
  const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
  liveWs = new WebSocket(`${proto}//${location.host}/ws/live-voice/${code}?auth_token=${AUTH_TOKEN}`);

  const statusBtn = document.getElementById('live-connect-btn');
  const statusPill = document.getElementById('live-conn-pill');
  if (statusBtn) statusBtn.textContent = 'Connecting WebSocket...';

  liveWs.onopen = () => {
    if (statusBtn) {
      statusBtn.textContent = '⏹ Disconnect Live Voice Session';
      statusBtn.className = 'px-4 py-2.5 rounded-xl font-bold text-xs mono bg-rose-600 text-white shadow-lg';
    }
    if (statusPill) {
      statusPill.textContent = '● CONNECTED: gemini-live-2.5-flash-native-audio (24kHz PCM)';
      statusPill.className = 'px-2.5 py-1 rounded-full text-[11px] font-bold mono bg-emerald-500/20 text-emerald-300 border border-emerald-500/40';
    }
    const micBtn = document.getElementById('live-mic-btn');
    if (micBtn) micBtn.disabled = false;
    appendLiveTranscript('SYSTEM', `Connected to Vertex AI Live API (gemini-live-2.5-flash-native-audio) for Square [${code}]. Click "Speak or Send Utterance" or enable 16kHz Mic!`);
  };

  liveWs.onmessage = (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.audio_b64) {
      playLivePcm24k(msg.audio_b64);
    }
    if (msg.input_transcript) {
      appendLiveTranscript('YOU', msg.input_transcript);
    }
    if (msg.output_transcript) {
      appendLiveTranscript('GEMINI LIVE VOICE', msg.output_transcript);
      setTimeout(() => animateEqBars(false), 600);
    }
    if (msg.status_note) {
      appendLiveTranscript('SYSTEM', msg.status_note);
    }
  };

  liveWs.onclose = () => {
    stopLiveMic();
    liveWs = null;
    if (statusBtn) {
      statusBtn.textContent = '🎙️ Connect Real Gemini Live Audio WebSocket';
      statusBtn.className = 'px-4 py-2.5 rounded-xl font-bold text-xs mono bg-gradient-to-r from-teal-500 to-cyan-600 text-white shadow-lg';
    }
    if (statusPill) {
      statusPill.textContent = '○ Standby (gemini-live-2.5-flash-native-audio)';
      statusPill.className = 'px-2.5 py-1 rounded-full text-[11px] font-bold mono bg-slate-800 text-slate-400 border border-slate-700';
    }
    animateEqBars(false);
  };
}

function sendLiveVoicePrompt(promptText) {
  const inp = document.getElementById('live-voice-prompt-input');
  const txt = promptText || (inp ? inp.value.trim() : '');
  if (!txt) return;
  if (!liveWs || liveWs.readyState !== WebSocket.OPEN) {
    toggleGeminiLiveSession(activeProject.code);
    setTimeout(() => {
      if (liveWs && liveWs.readyState === WebSocket.OPEN) {
        appendLiveTranscript('YOU', txt);
        liveWs.send(JSON.stringify({ type: 'text', text: txt }));
      }
    }, 1300);
    return;
  }
  liveAudioChunkCount = 0;
  appendLiveTranscript('YOU', txt);
  liveWs.send(JSON.stringify({ type: 'text', text: txt }));
  if (inp && !promptText) inp.value = '';
}

async function toggleLiveMic() {
  if (liveIsMicOn) {
    stopLiveMic();
    return;
  }
  if (!liveWs || liveWs.readyState !== WebSocket.OPEN) {
    alert('Connect the Gemini Live Audio WebSocket first!');
    return;
  }
  try {
    liveMicStream = await navigator.mediaDevices.getUserMedia({ audio: { sampleRate: 16000, channelCount: 1, echoCancellation: true, noiseSuppression: true } });
    liveMicCtx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
    const src = liveMicCtx.createMediaStreamSource(liveMicStream);
    liveProcessor = liveMicCtx.createScriptProcessor(4096, 1, 1);
    liveProcessor.onaudioprocess = (e) => {
      if (!liveWs || liveWs.readyState !== WebSocket.OPEN) return;
      const input = e.inputBuffer.getChannelData(0);
      const pcm16 = new Int16Array(input.length);
      for (let i = 0; i < input.length; i++) {
        const s = Math.max(-1, Math.min(1, input[i]));
        pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
      }
      const bytes = new Uint8Array(pcm16.buffer);
      let bin = '';
      for (let i = 0; i < bytes.byteLength; i++) bin += String.fromCharCode(bytes[i]);
      liveWs.send(JSON.stringify({ type: 'audio', data: btoa(bin) }));
      animateEqBars(true);
    };
    src.connect(liveProcessor);
    liveProcessor.connect(liveMicCtx.destination);
    liveIsMicOn = true;
    const micBtn = document.getElementById('live-mic-btn');
    if (micBtn) {
      micBtn.textContent = '🔴 Stop Live 16kHz Mic';
      micBtn.className = 'px-3.5 py-2.5 rounded-xl font-bold text-xs mono bg-rose-600 text-white animate-pulse';
    }
    appendLiveTranscript('SYSTEM', '🎙️ Live 16kHz Microphone PCM streaming active — speak naturally into your microphone!');
  } catch (err) {
    appendLiveTranscript('SYSTEM', 'Mic permission note: ' + err.message + ' (You can use the instant Barge-In Voice Chips below to stream real 24kHz audio from Vertex AI!)');
  }
}

function stopLiveMic() {
  if (liveProcessor) liveProcessor.disconnect();
  if (liveMicCtx) liveMicCtx.close();
  if (liveMicStream) liveMicStream.getTracks().forEach(t => t.stop());
  liveIsMicOn = false;
  const micBtn = document.getElementById('live-mic-btn');
  if (micBtn) {
    micBtn.textContent = '🎤 Start 16kHz Mic';
    micBtn.className = 'px-3.5 py-2.5 rounded-xl font-bold text-xs mono bg-slate-800 text-teal-300 border border-teal-500/40';
  }
}

// ============================================================================
// 2. REAL GEMINI ENTERPRISE DISCOVERY ENGINE streamAssist RUNNER
// ============================================================================
async function executeRealStreamAssist(code, customQuery) {
  const qBox = document.getElementById('ge-streamassist-query');
  const query = customQuery || (qBox ? qBox.value : activeProject.sampleInput);
  const outDiv = document.getElementById('ge-streamassist-live-result');
  if (outDiv) {
    outDiv.innerHTML = `<div class="p-4 rounded-xl border border-purple-500/40 bg-purple-950/20 flex items-center gap-3 text-xs mono text-purple-200">
      <span class="shrinking-shining-ink"></span>
      <span>Calling live Discovery Engine v1alpha <code>streamAssist</code> on <code>projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023</code>...</span>
    </div>`;
  }
  try {
    const res = await fetch('/api/stream-assist', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code: code, query: query })
    });
    const data = await res.json();
    if (outDiv) {
      outDiv.innerHTML = `
        <div class="p-4 rounded-xl border border-purple-500/40 bg-slate-950/90 space-y-3">
          <div class="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-slate-800 text-[11px] mono">
            <span class="text-emerald-400 font-bold">✅ LIVE STREAMASSIST v1alpha RESPONSE (${data.chunks_count || 1} Stream Chunks • ${data.latency_ms}ms)</span>
            <span class="text-purple-300">Session: <code>${(data.session_path || '').split('/').slice(-2).join('/')}</code></span>
          </div>
          <div class="text-xs leading-relaxed prose prose-invert max-w-none">${formatMarkdown(data.answer_markdown || '')}</div>
        </div>`;
    }
  } catch (e) {
    if (outDiv) outDiv.innerHTML = `<div class="text-rose-400 text-xs mono">Error: ${e.message}</div>`;
  }
}

// ============================================================================
// 3. BESPOKE 33-ARCHETYPE VISUAL APPLICATION RENDERER
// ============================================================================
function renderBespokeAppCanvas(code, art, sandboxData) {
  const container = document.getElementById('domain-bespoke-visualizer');
  if (!container || !art) return;
  const a = art.archetype || '';

  // --------------------------------------------------------------------------
  // [3.4, M.1, M.4] REAL GEMINI MULTIMODAL LIVE API VOICE STUDIO
  // --------------------------------------------------------------------------
  if (code === '3.4' || code === 'M.1' || code === 'M.4') {
    const defaultPrompts = {
      '3.4': "Wait, doesn't refinancing reset my 30-year clock and cost me thousands upfront?",
      'M.1': "Siren, what if we round up $265.75 every month and throw our $9,000 March tax refund at principal?",
      'M.4': "Astra, if we buy this $350,000 Royal Oak house with 5% down, how much cash is left in Rocket Money and when does PMI drop?"
    };
    const extraVisual = code === 'M.1' ? `
      <div class="grid grid-cols-3 gap-2.5 my-3 text-xs mono">
        <div class="p-3 rounded-xl bg-slate-900/90 border border-slate-800">
          <div class="text-[10px] text-slate-400">BASELINE 30Y</div>
          <div class="text-rose-400 font-bold mt-0.5">${art.baseline || '30.0 Yrs ($534k Int)'}</div>
        </div>
        <div class="p-3 rounded-xl bg-cyan-950/50 border border-cyan-500/40">
          <div class="text-[10px] text-cyan-300">SIREN OVERRIDE</div>
          <div class="text-emerald-400 font-bold mt-0.5">${art.accelerated || '18.2 Yrs (-11.8 Yrs!)'}</div>
        </div>
        <div class="p-3 rounded-xl bg-emerald-950/40 border border-emerald-500/40">
          <div class="text-[10px] text-emerald-300">INTEREST CRUSHED</div>
          <div class="text-white font-bold mt-0.5">${art.saved || '$241,840 Saved'}</div>
        </div>
      </div>` : (code === 'M.4' ? `
      <div class="grid grid-cols-3 gap-2.5 my-3 text-xs mono">
        <div class="p-3 rounded-xl bg-sky-950/40 border border-sky-500/30">
          <div class="text-[10px] text-sky-300">WHITEBOARD CASH TO CLOSE</div>
          <div class="text-white font-bold mt-0.5">${art.cash_to_close || '$22,300 ($2,700 Left)'}</div>
        </div>
        <div class="p-3 rounded-xl bg-indigo-950/40 border border-indigo-500/30">
          <div class="text-[10px] text-indigo-300">MONTHLY PITI + PMI</div>
          <div class="text-emerald-400 font-bold mt-0.5">${art.monthly_piti || '$2,633.18/mo'}</div>
        </div>
        <div class="p-3 rounded-xl bg-purple-950/40 border border-purple-500/30">
          <div class="text-[10px] text-purple-300">HPA 78% LTV AUTO-DROP</div>
          <div class="text-amber-300 font-bold mt-0.5">${art.pmi_drop || 'Month 84 ($118/mo Drops)'}</div>
        </div>
      </div>` : `
      <div class="grid grid-cols-3 gap-2.5 my-3 text-xs mono">
        <div class="p-3 rounded-xl bg-teal-950/40 border border-teal-500/30">
          <div class="text-[10px] text-teal-300">MONTHLY REFI DROP</div>
          <div class="text-emerald-400 font-bold mt-0.5">${art.monthly_savings || '$298.44/mo Saved'}</div>
        </div>
        <div class="p-3 rounded-xl bg-cyan-950/40 border border-cyan-500/30">
          <div class="text-[10px] text-cyan-300">BREAKEVEN HORIZON</div>
          <div class="text-white font-bold mt-0.5">${art.breakeven || '13.1 Months'}</div>
        </div>
        <div class="p-3 rounded-xl bg-indigo-950/40 border border-indigo-500/30">
          <div class="text-[10px] text-indigo-300">TERM INTEREST SAVED</div>
          <div class="text-amber-300 font-bold mt-0.5">${art.lifetime_saved || '$89,412 Saved'}</div>
        </div>
      </div>`);

    container.innerHTML = `
      <div class="p-5 rounded-2xl border-2 border-teal-500/50 bg-gradient-to-br from-slate-950 via-teal-950/30 to-slate-950 shadow-2xl space-y-4">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <div class="flex items-center gap-2">
            <span class="w-3 h-3 rounded-full bg-teal-400 animate-ping"></span>
            <span class="text-xs font-extrabold mono uppercase text-teal-300">🎙️ REAL VERTEX AI GEMINI LIVE AUDIO WEBSOCKET STUDIO</span>
          </div>
          <span id="live-conn-pill" class="px-2.5 py-1 rounded-full text-[11px] font-bold mono bg-slate-800 text-slate-300 border border-slate-700">
            ○ Standby (gemini-live-2.5-flash-native-audio)
          </span>
        </div>

        <!-- 32-Bar Real-Time PCM Acoustic Waveform -->
        <div class="p-4 rounded-xl bg-black/60 border border-teal-500/30 flex items-center justify-between gap-4">
          <div class="flex items-end gap-1 h-12 flex-grow" id="live-eq-container">
            ${Array.from({length: 32}, (_, i) => `<div class="live-eq-bar flex-1 bg-gradient-to-t from-teal-500 to-cyan-300 rounded-t transition-all duration-100" style="height:${18 + (i*13)%45}%"></div>`).join('')}
          </div>
          <div class="text-right shrink-0 mono">
            <div id="live-audio-chunks-badge" class="text-xs font-bold text-teal-300">0 PCM Chunks (24kHz)</div>
            <div class="text-[10px] text-slate-400">Bidi WebSocket • us-central1</div>
          </div>
        </div>

        ${extraVisual}

        <!-- Live Controls: Connect WebSocket + 16kHz Mic + Instant Barge-In Utterance -->
        <div class="flex flex-wrap items-center gap-2.5">
          <button id="live-connect-btn" onclick="toggleGeminiLiveSession('${code}')"
                  class="px-4 py-2.5 rounded-xl font-bold text-xs mono bg-gradient-to-r from-teal-500 to-cyan-600 text-white shadow-lg hover:opacity-95">
            🎙️ Connect Real Gemini Live Audio WebSocket
          </button>
          <button id="live-mic-btn" onclick="toggleLiveMic()" disabled
                  class="px-3.5 py-2.5 rounded-xl font-bold text-xs mono bg-slate-800 text-teal-300 border border-teal-500/40 disabled:opacity-40">
            🎤 Start 16kHz Mic
          </button>
          <button onclick="sendLiveVoicePrompt('${defaultPrompts[code].replace(/'/g, "\\'")}')"
                  class="px-3.5 py-2.5 rounded-xl font-bold text-xs mono bg-amber-500/20 text-amber-300 border border-amber-500/40 hover:bg-amber-500/30">
            ⚡ Trigger Live 24kHz Voice Barge-In Turn Now
          </button>
        </div>

        <div class="flex gap-2">
          <input id="live-voice-prompt-input" type="text" value="${defaultPrompts[code]}"
                 placeholder="Speak into mic or type an interruption for Gemini Live Audio..."
                 class="flex-grow px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs mono text-white">
          <button onclick="sendLiveVoicePrompt()" class="px-4 py-2 rounded-xl bg-teal-600 text-white font-bold text-xs mono">Send to Live Audio →</button>
        </div>

        <!-- Live Audio Transcript & Stream Log -->
        <div id="live-voice-transcript-log" class="max-h-48 overflow-y-auto p-3 rounded-xl bg-black/50 border border-slate-800 space-y-2">
          <div class="text-[11px] mono text-slate-400">👉 Click <strong>"⚡ Trigger Live 24kHz Voice Barge-In Turn Now"</strong> or <strong>"🎙️ Connect Real Gemini Live Audio WebSocket"</strong> to stream real 24kHz native audio directly from <code>gemini-live-2.5-flash-native-audio</code>!</div>
        </div>
      </div>`;
    return;
  }

  // --------------------------------------------------------------------------
  // [1.3, 2.1, 2.5, 3.1, 5.1] REAL GEMINI ENTERPRISE streamAssist + REAL UI LINKS
  // --------------------------------------------------------------------------
  const geBannerHtml = ['1.3', '2.1', '2.5', '3.1', '5.1'].includes(code) ? `
    <div class="p-4 rounded-xl border border-purple-500/40 bg-gradient-to-r from-purple-950/40 via-indigo-950/40 to-slate-950 mb-4">
      <div class="flex flex-wrap items-center justify-between gap-2 mb-2">
        <div class="flex items-center gap-2">
          <span class="px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/40 text-[10px] font-bold mono">REAL GEMINI ENTERPRISE (DISCOVERY ENGINE v1alpha)</span>
          <span class="text-xs font-bold mono text-white">Engine: <code>gemini-enterprise-17877637_1787763712023</code></span>
        </div>
        <div class="flex flex-wrap gap-2">
          <a href="https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023" target="_blank"
             class="px-3 py-1 rounded-lg bg-purple-600 hover:bg-purple-500 text-white font-bold text-[11px] mono shadow">
            🚀 Open Real Gemini Enterprise Web UI ↗
          </a>
          <a href="https://gemini.google.com/work" target="_blank"
             class="px-3 py-1 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-[11px] mono shadow">
            ✨ Open Sobi / Spark (/work) ↗
          </a>
          <a href="https://console.cloud.google.com/gen-app-builder/engines?project=vtxdemos" target="_blank"
             class="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-[11px] mono border border-slate-700">
            ⚙️ GCP Console Engine ↗
          </a>
        </div>
      </div>
      <div class="flex gap-2 mt-2">
        <input id="ge-streamassist-query" type="text" value="Compare Fannie Mae HomeReady 95% LTV vs FHA 3.5% down guidelines and compliance rules for this scenario"
               class="flex-grow px-3 py-1.5 rounded-lg bg-slate-950 border border-purple-500/30 text-xs mono text-white">
        <button onclick="executeRealStreamAssist('${code}')"
                class="px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold text-xs mono shrink-0">
          ⚡ Test Live streamAssist API
        </button>
      </div>
      <div id="ge-streamassist-live-result" class="mt-2"></div>
    </div>` : '';

  // --------------------------------------------------------------------------
  // [1.1] FORM 1003 PRE-QUAL & CRM INTAKE COCKPIT
  // --------------------------------------------------------------------------
  if (code === '1.1') {
    container.innerHTML = `
      <div class="p-5 rounded-2xl border border-emerald-500/40 bg-slate-950/90 space-y-4">
        <div class="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-3">
          <div>
            <div class="text-[10px] mono uppercase text-emerald-400 font-bold">FORM 1003 UNIFORM RESIDENTIAL LOAN APPLICATION // LIVE COCKPIT</div>
            <div class="text-base font-extrabold text-white">${art.borrower} • FICO: <span class="text-emerald-400">${art.fico_pair}</span></div>
          </div>
          <span class="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-xs font-bold mono">DU APPROVE / ELIGIBLE</span>
        </div>
        <!-- DTI Gauges -->
        <div class="grid sm:grid-cols-2 gap-4">
          <div class="p-3.5 rounded-xl bg-slate-900 border border-slate-800">
            <div class="flex justify-between text-xs mono mb-1"><span>Front-End Housing Ratio (PITI)</span><span class="text-emerald-400 font-bold">${art.front_dti}% / 36% Max</span></div>
            <div class="w-full h-2.5 bg-slate-800 rounded-full overflow-hidden"><div class="h-full bg-emerald-500" style="width:${Math.min(100, (art.front_dti/45)*100)}%"></div></div>
          </div>
          <div class="p-3.5 rounded-xl bg-slate-900 border border-slate-800">
            <div class="flex justify-between text-xs mono mb-1"><span>Back-End Total DTI Ratio</span><span class="text-cyan-400 font-bold">${art.back_dti}% / 45% DU Cap</span></div>
            <div class="w-full h-2.5 bg-slate-800 rounded-full overflow-hidden"><div class="h-full bg-cyan-500" style="width:${Math.min(100, (art.back_dti/45)*100)}%"></div></div>
          </div>
        </div>
        <!-- Qualifying Income Table -->
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs mono border-collapse">
            <thead><tr class="border-b border-slate-800 text-slate-400"><th class="py-2">Income Source</th><th class="py-2">Qualifying Monthly</th><th class="py-2">Fannie Mae Rule</th></tr></thead>
            <tbody>
              ${(art.income_rows || []).map(r => `<tr class="border-b border-slate-900"><td class="py-2 text-white font-semibold">${r.source}</td><td class="py-2 text-emerald-400 font-bold">${r.monthly}</td><td class="py-2 text-slate-400">${r.rule}</td></tr>`).join('')}
            </tbody>
          </table>
        </div>
      </div>`;
    return;
  }

  // --------------------------------------------------------------------------
  // [1.2] MICROSOFT OUTLOOK 365 RATE-LOCK ADD-IN COMPOSER
  // --------------------------------------------------------------------------
  if (code === '1.2') {
    container.innerHTML = `
      <div class="rounded-2xl border border-sky-500/40 bg-slate-950 overflow-hidden shadow-2xl">
        <div class="bg-[#0078D4] px-4 py-2.5 flex items-center justify-between text-white text-xs mono font-bold">
          <span>📧 Microsoft Outlook 365 // Rocket Pro Rate-Lock & Verified Approval Add-In</span>
          <span class="px-2 py-0.5 rounded bg-white/20">Cert #${art.certificate_id}</span>
        </div>
        <div class="p-4 space-y-3 text-xs">
          <div class="p-2.5 rounded bg-slate-900 border border-slate-800 mono space-y-1">
            <div><span class="text-slate-400">To:</span> <span class="text-white">${art.email_to}</span></div>
            <div><span class="text-slate-400">Subject:</span> <span class="text-sky-300 font-bold">${art.email_subject}</span></div>
          </div>
          <div class="grid sm:grid-cols-3 gap-3">
            ${(art.rate_matrix || []).map(o => `
              <div class="p-3.5 rounded-xl border ${o.badge.includes('Recommended') ? 'border-emerald-500 bg-emerald-950/20' : 'border-slate-800 bg-slate-900'}">
                <div class="text-[10px] mono font-bold text-sky-400 uppercase">${o.badge}</div>
                <div class="text-sm font-extrabold text-white mt-1">${o.tier}</div>
                <div class="text-lg font-extrabold text-emerald-400 mono mt-1">${o.pi}</div>
                <div class="text-[11px] mono text-slate-300 mt-1">Rate: <strong>${o.rate}</strong></div>
                <div class="text-[11px] mono text-slate-400">Cost: ${o.upfront} • Breakeven: ${o.breakeven}</div>
              </div>`).join('')}
          </div>
        </div>
      </div>`;
    return;
  }

  // --------------------------------------------------------------------------
  // [1.3] GEMINI ENTERPRISE STREAMASSIST & BATTLECARD MATRIX
  // --------------------------------------------------------------------------
  if (code === '1.3') {
    container.innerHTML = `
      ${geBannerHtml}
      <div class="p-5 rounded-2xl border border-purple-500/40 bg-slate-950 space-y-3">
        <div class="flex items-center justify-between">
          <span class="text-xs font-extrabold mono uppercase text-purple-300">⚔️ LIVE COMPETITOR BROKER VS. ROCKET GSE BATTLECARD</span>
          <span class="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-xs font-bold mono">${art.winner_banner}</span>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs mono border-collapse">
            <thead>
              <tr class="border-b border-slate-800 text-slate-400">
                <th class="py-2">Feature / Guideline</th>
                <th class="py-2 text-rose-400">Wholesale Broker (Std Conv 95%)</th>
                <th class="py-2 text-sky-400">Rocket Option A (HomeReady 95%)</th>
                <th class="py-2 text-emerald-400">Rocket Option B (FHA 96.5% Winner)</th>
              </tr>
            </thead>
            <tbody>
              ${(art.battlecard_rows || []).map(r => `
                <tr class="border-b border-slate-900">
                  <td class="py-2.5 font-bold text-white">${r.metric}</td>
                  <td class="py-2.5 text-rose-300">${r.broker_conv}</td>
                  <td class="py-2.5 text-sky-300">${r.homeready}</td>
                  <td class="py-2.5 text-emerald-300 font-bold">${r.fha}</td>
                </tr>`).join('')}
            </tbody>
          </table>
        </div>
      </div>`;
    return;
  }

  // --------------------------------------------------------------------------
  // [1.4] MONARK™ x ROCKET MONEY PERSONAL CFO WEALTH & LTV SIMULATOR
  // --------------------------------------------------------------------------
  if (code === '1.4') {
    container.innerHTML = `
      <div class="rounded-2xl border-2 border-emerald-500/50 bg-[#050C0A] p-5 shadow-2xl space-y-4">
        <div class="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-emerald-900/60">
          <div class="flex items-center gap-2">
            <span class="px-2.5 py-1 rounded bg-emerald-500 text-black font-extrabold text-xs mono">MONARK™ // ROCKET MONEY CFO OS</span>
            <span class="text-xs font-bold text-emerald-300 mono">Connected via SimpleFIN / Plaid FDX</span>
          </div>
          <div class="text-right mono">
            <span class="text-[11px] text-slate-400">Household Liquid + Retirement Net Worth:</span>
            <span class="text-base font-extrabold text-emerald-400 ml-2">${art.net_worth_total}</span>
          </div>
        </div>
        <!-- Connected Accounts Ledger -->
        <div class="grid sm:grid-cols-3 gap-3">
          ${(art.accounts || []).map(a => `
            <div class="p-3 rounded-xl bg-slate-900/90 border border-emerald-500/30 mono">
              <div class="flex justify-between text-[10px] text-slate-400"><span>${a.name}</span><span>${a.acct}</span></div>
              <div class="text-base font-extrabold text-white my-1">${a.bal}</div>
              <div class="text-[10px] text-emerald-400">${a.action}</div>
            </div>`).join('')}
        </div>
        <!-- Interactive LTV Tier Comparison -->
        <div class="space-y-2">
          <div class="text-xs font-bold mono uppercase text-amber-400">📊 LTV Capital Allocation Matrix (${art.five_yr_savings})</div>
          <div class="grid sm:grid-cols-3 gap-3">
            ${(art.ltv_tiers || []).map(t => `
              <div class="p-3.5 rounded-xl border ${t.tag.includes('Optimal') ? 'border-emerald-400 bg-emerald-950/30' : 'border-slate-800 bg-slate-900/60'} mono">
                <div class="text-[10px] font-bold text-amber-300">${t.tag}</div>
                <div class="text-xs font-bold text-white mt-1">${t.tier}</div>
                <div class="text-sm font-extrabold text-emerald-400 mt-1">${t.total}</div>
                <div class="text-[10px] text-slate-400 mt-1">Rate: ${t.rate} • PMI: ${t.pmi}</div>
              </div>`).join('')}
          </div>
        </div>
      </div>`;
    return;
  }

  // --------------------------------------------------------------------------
  // [1.5] ANTIGRAVITY MCP WEBHOOK ROUTER & CALENDAR DISPATCH BOARD
  // --------------------------------------------------------------------------
  if (code === '1.5') {
    container.innerHTML = `
      <div class="p-5 rounded-2xl border border-cyan-500/40 bg-slate-950 space-y-4">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <span class="text-xs font-extrabold mono text-cyan-400">🔌 ANTIGRAVITY 4-SERVER MCP EVENT ROUTING PIPELINE (135ms Total)</span>
          <span class="px-3 py-1 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/40 text-xs font-bold mono">${art.urgency}</span>
        </div>
        <div class="space-y-2">
          ${(art.mcp_nodes || []).map((n, idx) => `
            <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between gap-3 mono text-xs">
              <div class="flex items-center gap-2.5">
                <span class="w-6 h-6 rounded-full bg-cyan-500/20 text-cyan-300 flex items-center justify-center font-bold">${idx+1}</span>
                <div>
                  <div class="font-bold text-amber-300">${n.server}</div>
                  <div class="text-slate-300 text-[11px]">${n.event}</div>
                </div>
              </div>
              <span class="px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 text-[10px] font-bold shrink-0">${n.latency}</span>
            </div>`).join('')}
        </div>
        <div class="p-3.5 rounded-xl bg-emerald-950/30 border border-emerald-500/40 flex flex-wrap items-center justify-between gap-2 text-xs mono">
          <div><span class="text-slate-400">Routed Banker:</span> <strong class="text-white">${art.banker}</strong></div>
          <div><span class="text-slate-400">O365 Calendar Slot:</span> <strong class="text-emerald-400">${art.slot}</strong></div>
        </div>
      </div>`;
    return;
  }

  // --------------------------------------------------------------------------
  // [2.1, 2.2, 2.3, 2.4, 2.5] EXECUTIVE LIGHT PAPER AUDIT WORKBENCH
  // --------------------------------------------------------------------------
  if (code.startsWith('2.')) {
    let innerBody = '';
    if (code === '2.1') {
      innerBody = `
        <div class="text-xs font-bold uppercase mono text-sky-700 mb-2">📑 Grounded Fannie Mae B3-3.1 & Freddie Mac Section 5303 Income Ledger</div>
        <table class="w-full text-left text-xs mono border-collapse">
          <thead><tr class="border-b-2 border-slate-300 text-slate-600"><th class="py-2">Income Component</th><th class="py-2">Formula</th><th class="py-2">Qualifying Monthly</th><th class="py-2">GSE Selling Guide Citation</th><th class="py-2">Status</th></tr></thead>
          <tbody>
            ${(art.citations || []).map(c => `<tr class="border-b border-slate-200"><td class="py-2.5 font-bold text-slate-900">${c.component}</td><td class="py-2.5 text-slate-600">${c.math}</td><td class="py-2.5 font-extrabold text-emerald-700">${c.monthly}</td><td class="py-2.5 text-indigo-700 underline">${c.ref}</td><td class="py-2.5"><span class="px-2 py-0.5 rounded font-bold ${c.status.includes('CAPPED') ? 'bg-amber-100 text-amber-800 border border-amber-300' : 'bg-emerald-100 text-emerald-800'}">${c.status}</span></td></tr>`).join('')}
          </tbody>
        </table>`;
    } else if (code === '2.2') {
      innerBody = `
        <div class="flex flex-wrap items-center justify-between gap-2 mb-3">
          <span class="px-3 py-1 rounded-full bg-emerald-100 text-emerald-900 font-bold text-xs mono">Google ADK + Agent Engine Runtime (gemini-3.8-flash)</span>
          <span class="px-3 py-1 rounded-full bg-rose-100 text-rose-800 border border-rose-300 font-bold text-xs mono">RUNTIME_STAGE_BLOCKING CEL Gate Armed</span>
        </div>
        <table class="w-full text-left text-xs mono border-collapse">
          <thead><tr class="border-b-2 border-slate-300 text-slate-600"><th class="py-2">Date</th><th class="py-2">Chase Statement Description</th><th class="py-2">Amount</th><th class="py-2">Fannie Mae B3-4.2-02 Disposition</th></tr></thead>
          <tbody>
            ${(art.ledger || []).map(l => `<tr class="border-b border-slate-200"><td class="py-2 text-slate-600">${l.date}</td><td class="py-2 font-bold text-slate-900">${l.desc}</td><td class="py-2 font-extrabold text-slate-900">${l.amt}</td><td class="py-2"><span class="px-2 py-0.5 rounded font-bold ${l.status.includes('FLAGGED') ? 'bg-rose-100 text-rose-800 border border-rose-300' : 'bg-emerald-100 text-emerald-800'}">${l.status}</span></td></tr>`).join('')}
          </tbody>
        </table>
        <div class="mt-3 p-3 rounded-xl bg-amber-50 border border-amber-300 text-amber-950 text-xs mono font-semibold">
          🔒 <strong>Auto-Staged Encompass Condition:</strong> ${art.condition_staged}
        </div>`;
    } else if (code === '2.3') {
      innerBody = `
        <div class="flex flex-wrap items-center justify-between gap-2 mb-3">
          <span class="text-xs font-bold mono text-blue-800">🔍 Document AI Lending OCR Bounding-Box Extraction</span>
          <span class="px-3 py-1 rounded-full bg-rose-100 text-rose-800 border border-rose-300 font-bold text-xs mono">${art.variance}</span>
        </div>
        <div class="grid sm:grid-cols-2 gap-2.5">
          ${(art.ocr_boxes || []).map(b => `
            <div class="p-3 rounded-xl border ${b.conf.includes('BREACH') ? 'border-rose-400 bg-rose-50' : 'border-slate-200 bg-white'} flex items-center justify-between mono text-xs">
              <div><div class="text-[10px] text-slate-500">${b.box} • ${b.field}</div><div class="font-extrabold text-slate-900 mt-0.5">${b.val}</div></div>
              <span class="px-2 py-0.5 rounded font-bold text-[10px] ${b.conf.includes('BREACH') ? 'bg-rose-600 text-white' : 'bg-emerald-100 text-emerald-800'}">${b.conf}</span>
            </div>`).join('')}
        </div>`;
    } else if (code === '2.4') {
      innerBody = `
        <div class="flex items-center justify-between mb-3">
          <span class="text-xs font-bold mono text-indigo-900">📊 Official Fannie Mae Form 1084 Cash-Flow Worksheet (Schedule C)</span>
          <span class="px-3 py-1 rounded-full bg-emerald-100 text-emerald-900 font-bold text-xs mono">Qualifying: ${art.qualifying_mo}</span>
        </div>
        <table class="w-full text-left text-xs mono border-collapse">
          <thead><tr class="border-b-2 border-slate-300 text-slate-600"><th class="py-2">IRS Form Line</th><th class="py-2">Description</th><th class="py-2">2024 Tax Return</th><th class="py-2">2025 Tax Return</th><th class="py-2">Form 1084 Rule</th></tr></thead>
          <tbody>
            ${(art.rows || []).map(r => `<tr class="border-b border-slate-200"><td class="py-2 font-bold text-indigo-800">${r.line}</td><td class="py-2 text-slate-900">${r.item}</td><td class="py-2 text-slate-700">${r.y24}</td><td class="py-2 font-bold text-slate-900">${r.y25}</td><td class="py-2 text-emerald-800 font-semibold">${r.op}</td></tr>`).join('')}
          </tbody>
        </table>`;
    } else {
      innerBody = `
        <div class="flex items-center justify-between mb-3">
          <span class="text-xs font-bold mono text-teal-900">🏛️ Rocket Close (Amrock) Schedule B-II Title Commitment Curative Matrix</span>
          <span class="px-3 py-1 rounded-full bg-amber-100 text-amber-900 font-bold text-xs mono">${art.status}</span>
        </div>
        <div class="space-y-2.5">
          ${(art.exceptions || []).map(ex => `
            <div class="p-3.5 rounded-xl border border-slate-200 bg-white flex flex-wrap items-center justify-between gap-2 text-xs mono">
              <div>
                <div class="font-extrabold text-slate-900">${ex.item}: ${ex.defect}</div>
                <div class="text-slate-600 mt-0.5">${ex.resolution}</div>
              </div>
              <span class="px-2.5 py-1 rounded-full font-bold text-[10px] ${ex.state === 'CLEARED' ? 'bg-emerald-100 text-emerald-800' : 'bg-blue-100 text-blue-800'}">${ex.state}</span>
            </div>`).join('')}
        </div>`;
    }
    container.innerHTML = `
      ${geBannerHtml}
      <div class="p-5 rounded-2xl border-2 border-slate-300 bg-[#F8FAFC] text-slate-900 shadow-xl">
        ${innerBody}
      </div>`;
    return;
  }

  // --------------------------------------------------------------------------
  // [3.1, 3.2, 3.3, 3.5] MR. COOPER x ROCKET SERVICING BESPOKE APPS
  // --------------------------------------------------------------------------
  if (code === '3.1') {
    container.innerHTML = `
      ${geBannerHtml}
      <div class="p-5 rounded-2xl border border-teal-500/40 bg-slate-950 space-y-4">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <span class="text-xs font-extrabold mono text-teal-300">📊 MR. COOPER ESCROW SHORTAGE WATERFALL VISUALIZER</span>
          <span class="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-xs font-bold mono">${art.pi_locked}</span>
        </div>
        <div class="space-y-2.5">
          ${(art.bars || []).map(b => `
            <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs mono">
              <div class="flex justify-between mb-1"><span class="font-bold text-white">${b.label}</span><span>Old: $${b.old}/mo → <strong class="text-teal-300">New: $${b.new}/mo (+$${b.new - b.old}/mo)</strong></span></div>
              <div class="w-full h-2.5 bg-slate-800 rounded-full overflow-hidden"><div class="h-full" style="width:${Math.min(100, (b.new/2000)*100)}%; background:${b.color};"></div></div>
            </div>`).join('')}
        </div>
        <div class="grid sm:grid-cols-2 gap-3 text-xs mono">
          <div class="p-3.5 rounded-xl bg-teal-950/40 border border-teal-500/40"><div class="text-teal-300 font-bold mb-1">OPTION A · LUMP SUM REPAYMENT</div><div class="text-white">${art.option_a}</div></div>
          <div class="p-3.5 rounded-xl bg-cyan-950/40 border border-cyan-500/40"><div class="text-cyan-300 font-bold mb-1">OPTION B · 12-MONTH 0% SPREAD</div><div class="text-white">${art.option_b}</div></div>
        </div>
      </div>`;
    return;
  }

  if (code === '3.2') {
    container.innerHTML = `
      <div class="p-5 rounded-2xl border-2 border-cyan-500/40 bg-slate-950 space-y-4">
        <div class="flex items-center justify-between border-b border-slate-800 pb-3">
          <div>
            <div class="text-[10px] mono uppercase text-cyan-400 font-bold">GOOGLE ADK + AGENT ENGINE (gemini-3.8-flash) // OFFICIAL SERVICING DOCUMENT</div>
            <div class="text-base font-extrabold text-white">Certified Payoff Statement & IRS Form 1098</div>
          </div>
          <span class="px-3 py-1 rounded-lg bg-emerald-500/20 text-emerald-300 font-bold text-xs mono">1098 Box 1: ${art.form_1098_box1}</span>
        </div>
        <div class="grid sm:grid-cols-2 gap-2.5 text-xs mono">
          ${(art.certificate_fields || []).map(f => `
            <div class="p-3 rounded-xl bg-slate-900 border border-slate-800">
              <div class="text-[10px] text-slate-400">${f.label}</div>
              <div class="font-bold text-white mt-0.5">${f.val}</div>
            </div>`).join('')}
        </div>
      </div>`;
    return;
  }

  if (code === '3.3' || code === '3.5') {
    container.innerHTML = `
      <div class="p-5 rounded-2xl border border-teal-500/40 bg-slate-950 space-y-3">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <span class="text-xs font-extrabold mono text-teal-300">${code === '3.3' ? '🎧 ROCKET LOGIC SYNOPSIS // LIVE CCAI AGENT ASSIST & REG X WATERFALL' : '🏡 MR. COOPER + REDFIN + ROCKET MOVE-UP BRIDGE COMPARATOR'}</span>
          <span class="px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-300 text-xs font-bold mono">${code === '3.3' ? art.reg_x_gate : art.usable_equity}</span>
        </div>
        ${code === '3.3' ? (art.waterfall || []).map(w => `
          <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between gap-3 text-xs mono">
            <div><span class="text-amber-400 font-bold">${w.rank} · ${w.program}:</span> <span class="text-slate-200">${w.detail}</span></div>
            <span class="px-2 py-0.5 rounded bg-teal-500/20 text-teal-300 text-[10px] font-bold shrink-0">${w.status}</span>
          </div>`).join('') : `
          <div class="grid sm:grid-cols-2 gap-3 text-xs mono">
            <div class="p-4 rounded-xl bg-slate-900 border border-emerald-500/40"><div class="text-emerald-400 font-bold mb-1">SCENARIO A · KEEP 3.25% 1ST MORTGAGE</div><div class="text-white">${art.option_a}</div></div>
            <div class="p-4 rounded-xl bg-slate-900 border border-purple-500/40"><div class="text-purple-400 font-bold mb-1">SCENARIO B · REDFIN MOVE-UP + ROCKET CREDIT</div><div class="text-white">${art.option_b}</div></div>
          </div>`}
      </div>`;
    return;
  }

  // --------------------------------------------------------------------------
  // [4.2, 4.4, M.2] REAL GENERATED ARCHITECTURAL IMAGES (GEMPIX-2 / IMAGEN 3)
  // --------------------------------------------------------------------------
  if (code === '4.2' || code === '4.4' || code === 'M.2') {
    if (code === '4.2') {
      container.innerHTML = `
        <div class="p-5 rounded-2xl border-2 border-rose-500/50 bg-slate-950 space-y-4">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <span class="text-xs font-extrabold mono text-rose-400">🎨 REAL GEMPIX-2 / IMAGEN 3 VIRTUAL STAGING STUDIO (CORKTOWN DETROIT LOFT)</span>
            <div class="flex gap-1.5">
              <button onclick="document.getElementById('stage-main-img').src='${art.before_img}'" class="px-2.5 py-1 rounded bg-slate-800 text-slate-200 text-[11px] mono font-bold">1. Raw Empty Loft</button>
              <button onclick="document.getElementById('stage-main-img').src='${art.after_industrial}'" class="px-2.5 py-1 rounded bg-rose-600 text-white text-[11px] mono font-bold">2. Detroit Industrial Loft</button>
              <button onclick="document.getElementById('stage-main-img').src='${art.after_midcentury}'" class="px-2.5 py-1 rounded bg-purple-600 text-white text-[11px] mono font-bold">3. Mid-Century Modern</button>
            </div>
          </div>
          <div class="grid sm:grid-cols-2 gap-4 items-center">
            <div class="relative rounded-xl overflow-hidden border border-slate-700">
              <img src="${art.before_img}" class="w-full h-56 object-cover" alt="Before Empty Loft">
              <div class="absolute top-2 left-2 px-2.5 py-1 rounded bg-black/80 text-slate-200 text-[10px] mono font-bold">BEFORE · RAW REDFIN MLS #MI-884120</div>
            </div>
            <div class="relative rounded-xl overflow-hidden border-2 border-rose-500 shadow-xl">
              <img id="stage-main-img" src="${art.after_industrial}" class="w-full h-56 object-cover" alt="After Virtually Staged Loft">
              <div class="absolute top-2 left-2 px-2.5 py-1 rounded bg-rose-600 text-white text-[10px] mono font-bold">✨ AFTER · GEMPIX-2 VIRTUALLY STAGED</div>
              <div class="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black via-black/85 to-transparent p-3">
                <div class="text-xs font-extrabold text-white">${art.headline}</div>
                <div class="text-[9px] mono text-slate-300 mt-0.5">${art.tila_footer}</div>
              </div>
            </div>
          </div>
        </div>`;
      return;
    }
    if (code === '4.4') {
      container.innerHTML = `
        <div class="p-5 rounded-2xl border border-purple-500/40 bg-slate-950 space-y-3">
          <div class="text-xs font-extrabold mono text-purple-300">🎬 VEO 3.1 + GEMPIX-2 // 4-FRAME 9:16 VERTICAL SOCIAL REEL STORYBOARD</div>
          <div class="grid sm:grid-cols-4 gap-3">
            ${(art.frames || []).map(f => `
              <div class="rounded-xl overflow-hidden border border-purple-500/30 bg-slate-900 flex flex-col">
                <img src="${f.img}" class="w-full h-36 object-cover" alt="${f.time}">
                <div class="p-2.5 flex-grow flex flex-col justify-between text-[11px] mono">
                  <div>
                    <div class="text-purple-400 font-bold">${f.time}</div>
                    <div class="text-slate-300 text-[10px] mt-0.5">${f.scene}</div>
                  </div>
                  <div class="mt-2 p-1.5 rounded bg-rose-600/20 border border-rose-500/40 text-rose-200 font-bold text-[10px] text-center">${f.overlay}</div>
                </div>
              </div>`).join('')}
          </div>
        </div>`;
      return;
    }
    if (code === 'M.2') {
      container.innerHTML = `
        <div class="p-5 rounded-2xl border-2 border-pink-500/40 bg-slate-950 space-y-4">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <span class="text-xs font-extrabold mono text-pink-400">🏗️ PROJECT SPATIAL CLOSE // FANNIE MAE HOMESTYLE RENOVATION + 3D SOLAR HUB</span>
            <span class="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-xs font-bold mono">${art.aiv_equity}</span>
          </div>
          <div class="grid sm:grid-cols-12 gap-4 items-center">
            <div class="sm:col-span-6 relative rounded-xl overflow-hidden border-2 border-cyan-500/50">
              <img src="${art.kitchen_img}" class="w-full h-52 object-cover" alt="Remodeled Chef Kitchen">
              <div class="absolute top-2 left-2 px-2.5 py-1 rounded bg-black/80 text-cyan-300 text-[10px] mono font-bold">✨ $55k ESCROWED CHEF KITCHEN & SUNROOM REMODEL</div>
            </div>
            <div class="sm:col-span-6 space-y-2.5 text-xs mono">
              <div class="p-3 rounded-xl bg-slate-900 border border-slate-800"><div class="text-[10px] text-slate-400">ACQUISITION + RENOVATION ESCROW</div><div class="text-white font-bold mt-0.5">${art.acq_total}</div></div>
              <div class="p-3 rounded-xl bg-emerald-950/30 border border-emerald-500/40"><div class="text-[10px] text-emerald-300">AFTER-IMPROVED VALUE (AIV)</div><div class="text-emerald-400 font-bold mt-0.5">${art.aiv_equity}</div></div>
              <div class="p-3 rounded-xl bg-cyan-950/30 border border-cyan-500/40"><div class="text-[10px] text-cyan-300">SINGLE-CLOSE HOMESTYLE VS. HELOC</div><div class="text-white font-bold mt-0.5">${art.payment}</div></div>
            </div>
          </div>
        </div>`;
      return;
    }
  }

  // --------------------------------------------------------------------------
  // [4.1, 4.3, 4.5] MARKETING HEATMAP, ROAS FUNNEL & CROSS-BRAND FLYWHEEL
  // --------------------------------------------------------------------------
  if (code === '4.1' || code === '4.3' || code === '4.5') {
    if (code === '4.1') {
      container.innerHTML = `
        <div class="p-5 rounded-2xl border border-rose-500/40 bg-slate-950 space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-xs font-extrabold mono text-rose-400">🗺️ REDFIN 50-METRO LIVE INVENTORY & SELLER CONCESSION PULSE</span>
            <span class="px-2.5 py-1 rounded bg-purple-500/20 text-purple-300 text-[10px] font-bold mono">Google ADK Runtime (gemini-3.8-flash)</span>
          </div>
          <div class="grid sm:grid-cols-2 gap-3 text-xs mono">
            ${(art.metros || []).map(m => `
              <div class="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
                <div class="flex justify-between font-bold text-white"><span>${m.city}</span><span class="text-emerald-400">${m.median}</span></div>
                <div class="text-[11px] text-rose-300">Inventory: ${m.inv} • Seller Concessions: ${m.concessions}</div>
                <div class="text-[11px] text-slate-300 italic">"${m.hook}"</div>
              </div>`).join('')}
          </div>
        </div>`;
      return;
    }
    if (code === '4.3') {
      container.innerHTML = `
        <div class="p-5 rounded-2xl border border-pink-500/40 bg-slate-950 space-y-3">
          <div class="text-xs font-extrabold mono text-pink-400">📈 MULTI-TOUCH FUNDED-LOAN ROAS ATTRIBUTION DECK (gemini-3.8-flash)</div>
          <div class="space-y-2 text-xs mono">
            ${(art.channels || []).map(c => `
              <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 flex flex-wrap items-center justify-between gap-2">
                <div><div class="font-bold text-white">${c.name}</div><div class="text-[11px] text-slate-400">CPL: ${c.cpl} • Funded ROAS: <strong class="text-emerald-400">${c.funded_roas}</strong> • Sentiment: ${c.sentiment}</div></div>
                <span class="px-2.5 py-1 rounded font-bold text-[10px] ${c.action.includes('SCALE') ? 'bg-emerald-500/20 text-emerald-300' : 'bg-rose-500/20 text-rose-300'}">${c.action}</span>
              </div>`).join('')}
          </div>
        </div>`;
      return;
    }
    if (code === '4.5') {
      container.innerHTML = `
        <div class="p-5 rounded-2xl border border-emerald-500/40 bg-slate-950 space-y-3">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <span class="text-xs font-extrabold mono text-emerald-400">🔄 ROCKET MONEY → REDFIN → ROCKET MORTGAGE → MR. COOPER FLYWHEEL</span>
            <span class="px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-300 text-xs font-bold mono">${art.bundle_savings}</span>
          </div>
          <div class="grid sm:grid-cols-4 gap-2.5 text-xs mono">
            ${(art.stages || []).map(s => `
              <div class="p-3 rounded-xl bg-slate-900 border border-slate-800">
                <div class="text-[10px] font-bold text-rose-400">${s.brand}</div>
                <div class="text-[11px] text-white font-semibold my-1">${s.signal}</div>
                <span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[9px] font-bold">${s.status}</span>
              </div>`).join('')}
          </div>
        </div>`;
      return;
    }
  }

  // --------------------------------------------------------------------------
  // [5.1, 5.2, 5.3, 5.4, 5.5] RISK, CFPB, TRID, MODEL ARMOR & FAIR LENDING VAULT
  // --------------------------------------------------------------------------
  if (code.startsWith('5.')) {
    let body5 = '';
    if (code === '5.1') {
      body5 = (art.clauses || []).map(c => `
        <div class="p-3.5 rounded-xl bg-slate-900 border border-amber-500/30 text-xs mono space-y-1">
          <div class="font-bold text-amber-400">${c.statute}</div>
          <div class="text-rose-300">❌ Defect: ${c.defect}</div>
          <div class="text-emerald-300">✅ Mandatory Safe-Harbor Fix: ${c.fix}</div>
        </div>`).join('');
    } else if (code === '5.2') {
      body5 = (art.raw_vs_sanitized || []).map(r => `
        <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 flex flex-wrap items-center justify-between gap-2 text-xs mono">
          <div><span class="text-amber-400 font-bold">${r.type}:</span> <span class="line-through text-rose-400 ml-2">${r.raw}</span></div>
          <span class="px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-300 font-bold text-[11px]">${r.masked}</span>
        </div>`).join('');
    } else if (code === '5.3') {
      body5 = `
        <table class="w-full text-left text-xs mono border-collapse">
          <thead><tr class="border-b border-slate-800 text-slate-400"><th class="py-2">Closing Fee Line Item</th><th class="py-2">TRID Bucket</th><th class="py-2">LE Disclosed</th><th class="py-2">CD Actual</th><th class="py-2">Section J Cure</th></tr></thead>
          <tbody>
            ${(art.rows || []).map(r => `<tr class="border-b border-slate-900"><td class="py-2 font-bold text-white">${r.fee}</td><td class="py-2 text-amber-300">${r.bucket}</td><td class="py-2">${r.le}</td><td class="py-2">${r.cd}</td><td class="py-2 font-bold ${r.cure.includes('CURE') ? 'text-rose-400' : 'text-emerald-400'}">${r.cure}</td></tr>`).join('')}
          </tbody>
        </table>`;
    } else if (code === '5.4') {
      body5 = (art.redlines || []).map(r => `
        <div class="p-3.5 rounded-xl bg-slate-900 border border-slate-800 text-xs mono space-y-1">
          <div class="font-bold text-sky-400">${r.clause}</div>
          <div class="text-rose-300 line-through">Vendor Draft: "${r.vendor_text}"</div>
          <div class="text-emerald-300 font-semibold">Rocket GLBA Redline: "${r.rocket_fix}"</div>
        </div>`).join('');
    } else {
      body5 = (art.cohorts || []).map(c => `
        <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 flex flex-wrap items-center justify-between gap-2 text-xs mono">
          <div class="font-bold text-white">${c.pair}</div>
          <div class="text-emerald-400 font-bold">${c.rate_a} vs ${c.rate_b} → ${c.ratio}</div>
        </div>`).join('');
    }
    container.innerHTML = `
      ${geBannerHtml}
      <div class="p-5 rounded-2xl border border-amber-500/40 bg-slate-950 space-y-3">
        <div class="text-xs font-extrabold mono uppercase text-amber-400">⚖️ SOVEREIGN COMPLIANCE & MODEL ARMOR VERIFICATION VAULT</div>
        ${body5}
      </div>`;
    return;
  }

  // --------------------------------------------------------------------------
  // [6.1, 6.2, 6.3] SDLC, CODEMENDER & ANTIGRAVITY IDE
  // --------------------------------------------------------------------------
  if (code.startsWith('6.')) {
    let body6 = '';
    if (code === '6.1') {
      body6 = (art.patches || []).map(p => `
        <div class="p-3.5 rounded-xl bg-black border border-slate-800 text-xs mono space-y-1.5">
          <div class="flex justify-between"><span class="text-rose-400 font-bold">🛡️ ${p.cwe}</span><span class="text-slate-400">${p.loc}</span></div>
          <div class="p-2 rounded bg-rose-950/30 border border-rose-500/30 text-rose-300">- ${p.vuln}</div>
          <div class="p-2 rounded bg-emerald-950/30 border border-emerald-500/30 text-emerald-300">+ ${p.fix}</div>
        </div>`).join('');
    } else if (code === '6.2') {
      body6 = `
        <div class="grid sm:grid-cols-2 gap-2.5 text-xs mono">
          ${(art.lanes || []).map(l => `
            <div class="p-3 rounded-xl bg-black border border-purple-500/30">
              <div class="flex justify-between font-bold text-purple-300"><span>🤖 ${l.agent}</span><span class="text-emerald-400">${l.status}</span></div>
              <div class="text-[11px] text-slate-400 mt-1">Branch: <code>${l.branch}</code></div>
              <div class="text-[11px] text-white">Artifact: <code>${l.artifact}</code></div>
            </div>`).join('')}
        </div>`;
    } else {
      body6 = (art.diff_pairs || []).map(d => `
        <div class="p-3 rounded-xl bg-black border border-slate-800 text-xs mono space-y-1.5">
          <div class="p-2 rounded bg-rose-950/30 text-rose-300">- [Legacy .NET 4.8 WCF]: ${d.legacy}</div>
          <div class="p-2 rounded bg-emerald-950/30 text-emerald-300">+ [Modern .NET 9 Cloud Run]: ${d.modern}</div>
        </div>`).join('');
    }
    container.innerHTML = `
      <div class="p-5 rounded-2xl border border-green-500/40 bg-[#030604] space-y-3">
        <div class="text-xs font-extrabold mono text-green-400">💻 GOOGLE ANTIGRAVITY 2.0 & DEEPMIND CODEMENDER gVISOR IDE</div>
        ${body6}
      </div>`;
    return;
  }

  // --------------------------------------------------------------------------
  // [M.3, M.5] MOONSHOT SWARM TOPOLOGY & SELF-HEALING PIPELINE
  // --------------------------------------------------------------------------
  if (code === 'M.3' || code === 'M.5') {
    if (code === 'M.3') {
      container.innerHTML = `
        <div class="p-5 rounded-2xl border-2 border-purple-500/50 bg-slate-950 space-y-3">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <span class="text-xs font-extrabold mono text-purple-300">🐝 PROJECT HIVEMIND // 4-AGENT ADK SWARM TOPOLOGY (gemini-3.8-flash)</span>
            <span class="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-xs font-bold mono">${art.volume}</span>
          </div>
          <div class="grid sm:grid-cols-2 gap-3 text-xs mono">
            ${(art.swarm_nodes || []).map(n => `
              <div class="p-3.5 rounded-xl bg-slate-900 border border-purple-500/30">
                <div class="flex justify-between font-bold text-purple-300"><span>${n.id}</span><span class="text-cyan-300">${n.model}</span></div>
                <div class="text-[11px] text-slate-200 mt-1">${n.task}</div>
              </div>`).join('')}
          </div>
        </div>`;
      return;
    }
    if (code === 'M.5') {
      container.innerHTML = `
        <div class="p-5 rounded-2xl border-2 border-emerald-500/50 bg-slate-950 space-y-3">
          <div class="text-xs font-extrabold mono text-emerald-400">🛡️ PROJECT AIR-TIGHT // 4-STAGE AUTONOMOUS SELF-HEALING CLOSING PIPELINE</div>
          <div class="grid sm:grid-cols-2 gap-3 text-xs mono">
            <div class="p-3 rounded-xl bg-slate-900 border border-rose-500/30"><div class="text-rose-400 font-bold">STAGE 1 · DOCAI DEFECT SCAN</div><div class="text-slate-200 mt-1">${art.stage1}</div></div>
            <div class="p-3 rounded-xl bg-slate-900 border border-amber-500/30"><div class="text-amber-400 font-bold">STAGE 2 · TRID CURE COMPUTATION</div><div class="text-slate-200 mt-1">${art.stage2}</div></div>
            <div class="p-3 rounded-xl bg-slate-900 border border-cyan-500/30"><div class="text-cyan-400 font-bold">STAGE 3 · PLAYWRIGHT LOS PATCH</div><div class="text-slate-200 mt-1">${art.stage3}</div></div>
            <div class="p-3 rounded-xl bg-emerald-950/30 border border-emerald-500/40"><div class="text-emerald-400 font-bold">STAGE 4 · CLEAR TO CLOSE</div><div class="text-white font-bold mt-1">${art.stage4}</div></div>
          </div>
        </div>`;
      return;
    }
  }
}
"""
