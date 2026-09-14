import asyncio
import json
import os
import certifi
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import vertexai

os.environ.setdefault("SSL_CERT_FILE", certifi.where())
os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())

PROJECT_ID = "vtxdemos"
LOCATION = "us-central1"

RUNTIMES = {
    "buggy": {
        "name": "Runtime 1: ADK 2.7.1 (Unpatched / Buggy)",
        "resource": "projects/254356041555/locations/us-central1/reasoningEngines/434137218425028608",
    },
    "fixed": {
        "name": "Runtime 2: ADK 2.7.1 (Fixed + Wakeup Trigger)",
        "resource": "projects/254356041555/locations/us-central1/reasoningEngines/6983496976528572416",
    },
}

app = FastAPI()

HTML_PAGE = """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <title>ADK Live Voice Tester — Vercel Monochrome Architecture</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      /* Light Mode (Default Vercel Monochrome Architecture) */
      --bg-canvas: #fafafa;
      --bg-grid: #eaeaea;
      --bg-surface: #ffffff;
      --bg-elevated: #f4f4f5;
      --bg-header: #fafafa;
      --bg-thinking: #f8f8f8;
      --bg-log: #ffffff;
      --bg-msg-system: #fafafa;
      --border-subtle: #eaeaea;
      --border-hover: #09090b;
      --text-primary: #09090b;
      --text-secondary: #666666;
      --text-muted: #a1a1aa;
      --btn-primary-bg: #09090b;
      --btn-primary-text: #ffffff;
      --btn-primary-hover: #27272a;
      --btn-secondary-bg: #ffffff;
      --btn-secondary-text: #09090b;
      --btn-secondary-hover: #f4f4f5;
      --shadow-card: 0 12px 36px rgba(0, 0, 0, 0.06);
      --ink-grad-1: radial-gradient(circle at 20% 20%, #52525b, #18181b, #000000);
      --ink-grad-2: radial-gradient(circle at 80% 20%, #71717a, #27272a, #09090b);
      --ink-grad-3: radial-gradient(circle at 40% 80%, #3f3f46, #09090b, #000000);
      --ink-shadow: rgba(0, 0, 0, 0.25);
      --sweep-grad: linear-gradient(90deg, #71717a 0%, #09090b 50%, #71717a 100%);
      --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      --font-mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
    }

    [data-theme="dark"] {
      /* Dark Mode (Vercel OLED Monochrome Architecture) */
      --bg-canvas: #000000;
      --bg-grid: #111111;
      --bg-surface: #0a0a0a;
      --bg-elevated: #111111;
      --bg-header: #050505;
      --bg-thinking: #080808;
      --bg-log: #000000;
      --bg-msg-system: #050505;
      --border-subtle: #222222;
      --border-hover: #ededed;
      --text-primary: #ededed;
      --text-secondary: #888888;
      --text-muted: #52525b;
      --btn-primary-bg: #ffffff;
      --btn-primary-text: #000000;
      --btn-primary-hover: #d4d4d8;
      --btn-secondary-bg: #000000;
      --btn-secondary-text: #ededed;
      --btn-secondary-hover: #111111;
      --shadow-card: 0 24px 60px rgba(0, 0, 0, 0.85);
      --ink-grad-1: radial-gradient(circle at 20% 20%, #ffffff, #a1a1aa, #09090b);
      --ink-grad-2: radial-gradient(circle at 80% 20%, #f4f4f5, #71717a, #18181b);
      --ink-grad-3: radial-gradient(circle at 40% 80%, #e4e4e7, #52525b, #000000);
      --ink-shadow: rgba(255, 255, 255, 0.45);
      --sweep-grad: linear-gradient(90deg, #71717a 0%, #ffffff 50%, #71717a 100%);
    }

    * {
      box-sizing: border-box;
    }

    body {
      font-family: var(--font-sans);
      background-color: var(--bg-canvas);
      background-image:
        linear-gradient(to right, var(--bg-grid) 1px, transparent 1px),
        linear-gradient(to bottom, var(--bg-grid) 1px, transparent 1px);
      background-size: 48px 48px;
      color: var(--text-primary);
      margin: 0;
      padding: 40px 20px;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      transition: background-color 0.2s ease, color 0.2s ease;
      -webkit-font-smoothing: antialiased;
    }

    .container {
      width: 100%;
      max-width: 820px;
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: 6px;
      box-shadow: var(--shadow-card);
      overflow: hidden;
      transition: background-color 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }

    /* Architectural Header Bar */
    .header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 16px 24px;
      border-bottom: 1px solid var(--border-subtle);
      background: var(--bg-header);
      transition: background-color 0.2s ease, border-color 0.2s ease;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .brand-triangle {
      width: 0;
      height: 0;
      border-left: 8px solid transparent;
      border-right: 8px solid transparent;
      border-bottom: 14px solid var(--text-primary);
      transition: border-color 0.2s ease;
    }

    .brand-title {
      font-size: 15px;
      font-weight: 600;
      letter-spacing: -0.02em;
      color: var(--text-primary);
    }

    .brand-sub {
      font-family: var(--font-mono);
      font-size: 11px;
      color: var(--text-secondary);
      padding-left: 10px;
      border-left: 1px solid var(--border-subtle);
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .conn-pill {
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      padding: 5px 10px;
      border-radius: 4px;
      border: 1px solid var(--border-subtle);
      background: var(--bg-elevated);
      color: var(--text-secondary);
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s ease;
    }

    .conn-pill.connected {
      border-color: var(--text-primary);
      color: var(--text-primary);
      background: var(--bg-surface);
    }

    .conn-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--text-muted);
    }

    .conn-pill.connected .conn-dot {
      background: var(--text-primary);
      box-shadow: 0 0 8px var(--text-primary);
    }

    .theme-btn {
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 500;
      padding: 5px 11px;
      border-radius: 4px;
      border: 1px solid var(--border-subtle);
      background: var(--bg-surface);
      color: var(--text-primary);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s ease;
    }

    .theme-btn:hover {
      border-color: var(--border-hover);
      background: var(--bg-elevated);
    }

    /* Control Toolbar */
    .toolbar {
      display: grid;
      grid-template-columns: 1fr auto auto;
      gap: 10px;
      padding: 16px 24px;
      border-bottom: 1px solid var(--border-subtle);
      background: var(--bg-surface);
    }

    select, input {
      font-family: var(--font-sans);
      font-size: 13px;
      padding: 9px 12px;
      border-radius: 4px;
      border: 1px solid var(--border-subtle);
      background: var(--bg-surface);
      color: var(--text-primary);
      outline: none;
      transition: border-color 0.15s ease, background-color 0.15s ease;
    }

    select:focus, input:focus {
      border-color: var(--border-hover);
    }

    button {
      font-family: var(--font-sans);
      font-size: 13px;
      font-weight: 500;
      padding: 9px 16px;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.15s ease;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      white-space: nowrap;
    }

    button.btn-primary {
      background: var(--btn-primary-bg);
      color: var(--btn-primary-text);
      border: 1px solid var(--btn-primary-bg);
    }

    button.btn-primary:hover:not(:disabled) {
      background: var(--btn-primary-hover);
      border-color: var(--btn-primary-hover);
    }

    button.btn-secondary {
      background: var(--btn-secondary-bg);
      color: var(--btn-secondary-text);
      border: 1px solid var(--border-subtle);
    }

    button.btn-secondary:hover:not(:disabled) {
      border-color: var(--border-hover);
      background: var(--btn-secondary-hover);
    }

    button:disabled {
      opacity: 0.35;
      cursor: not-allowed;
    }

    button.mic-active {
      background: var(--btn-primary-bg);
      color: var(--btn-primary-text);
      border-color: var(--btn-primary-bg);
      animation: monochrome-pulse 1.6s ease-in-out infinite;
    }

    @keyframes monochrome-pulse {
      0%, 100% { box-shadow: 0 0 0 0 rgba(120, 120, 120, 0.35); }
      50% { box-shadow: 0 0 0 6px rgba(120, 120, 120, 0); }
    }

    /* Telemetry Grid Bar */
    .telemetry-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      border-bottom: 1px solid var(--border-subtle);
      background: var(--bg-header);
    }

    .telemetry-cell {
      padding: 10px 24px;
      border-right: 1px solid var(--border-subtle);
      display: flex;
      flex-direction: column;
      gap: 3px;
    }

    .telemetry-cell:last-child {
      border-right: none;
    }

    .telemetry-label {
      font-family: var(--font-mono);
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--text-secondary);
    }

    .telemetry-value {
      font-family: var(--font-mono);
      font-size: 12px;
      font-weight: 500;
      color: var(--text-primary);
    }

    /* Claude-Code Shrinking & Shining Ink Thinking Bar */
    .thinking-banner {
      display: none;
      align-items: center;
      gap: 12px;
      padding: 10px 24px;
      border-bottom: 1px solid var(--border-subtle);
      background: var(--bg-thinking);
    }

    .thinking-banner.active {
      display: flex;
    }

    .shrinking-shining-ink {
      width: 16px;
      height: 16px;
      display: inline-block;
      flex-shrink: 0;
      background: var(--ink-grad-1);
      border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%;
      animation:
        ink-morph 5s ease-in-out infinite alternate,
        ink-pulse 1.8s ease-in-out infinite,
        ink-shine 3.5s linear infinite;
      filter: drop-shadow(0 0 6px var(--ink-shadow));
    }

    @keyframes ink-morph {
      0% {
        border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%;
        transform: rotate(0deg);
      }
      50% {
        border-radius: 30% 60% 70% 30% / 50% 60% 30% 60%;
        transform: rotate(180deg);
      }
      100% {
        border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%;
        transform: rotate(360deg);
      }
    }

    @keyframes ink-pulse {
      0%, 100% {
        transform: scale(0.82);
        filter: drop-shadow(0 0 3px var(--ink-shadow));
      }
      50% {
        transform: scale(1.16);
        filter: drop-shadow(0 0 10px var(--ink-shadow));
      }
    }

    @keyframes ink-shine {
      0%, 100% {
        background: var(--ink-grad-1);
      }
      33% {
        background: var(--ink-grad-2);
      }
      66% {
        background: var(--ink-grad-3);
      }
    }

    .sweep-text {
      font-family: var(--font-mono);
      font-size: 12px;
      letter-spacing: 0.02em;
      background: var(--sweep-grad);
      background-size: 200% 100%;
      -webkit-background-clip: text;
      background-clip: text;
      -webkit-text-fill-color: transparent;
      animation: text-sweep 2s linear infinite;
    }

    @keyframes text-sweep {
      0% { background-position: 100% 0; }
      100% { background-position: -100% 0; }
    }

    /* Stream Console Log */
    #log {
      height: 410px;
      overflow-y: auto;
      padding: 20px 24px;
      background: var(--bg-log);
      display: flex;
      flex-direction: column;
      gap: 10px;
      transition: background-color 0.2s ease;
    }

    .msg {
      padding: 10px 14px;
      border-radius: 4px;
      font-size: 13px;
      line-height: 1.5;
      border: 1px solid var(--border-subtle);
      max-width: 88%;
    }

    .msg-meta {
      font-family: var(--font-mono);
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--text-secondary);
      margin-bottom: 4px;
      display: block;
    }

    .msg.user {
      align-self: flex-end;
      background: var(--btn-primary-bg);
      color: var(--btn-primary-text);
      border-color: var(--btn-primary-bg);
    }

    .msg.user .msg-meta {
      color: var(--text-muted);
    }

    .msg.agent {
      align-self: flex-start;
      background: var(--bg-surface);
      color: var(--text-primary);
      border-left: 2px solid var(--text-primary);
    }

    .msg.system {
      align-self: stretch;
      max-width: 100%;
      background: var(--bg-msg-system);
      color: var(--text-secondary);
      font-family: var(--font-mono);
      font-size: 11px;
      border-style: dashed;
      padding: 8px 12px;
    }

    /* Input Footer Bar */
    .footer-bar {
      display: flex;
      gap: 10px;
      padding: 16px 24px;
      border-top: 1px solid var(--border-subtle);
      background: var(--bg-surface);
    }

    .footer-bar input {
      flex: 1;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="brand">
        <div class="brand-triangle"></div>
        <span class="brand-title">ADK Live Voice Architecture</span>
        <span class="brand-sub">Bidi Streaming &amp; Agent Handoff (#5238)</span>
      </div>
      <div class="header-actions">
        <div id="connStatus" class="conn-pill">
          <span class="conn-dot"></span>
          <span id="connText">Disconnected</span>
        </div>
        <button id="themeToggleBtn" class="theme-btn" onclick="toggleTheme()" title="Toggle Light / Dark Theme">
          <span id="themeIcon">🌙</span>
          <span id="themeLabel">Dark</span>
        </button>
      </div>
    </div>

    <div class="toolbar">
      <select id="runtimeSelect">
        <option value="fixed">Runtime 2 · ADK 2.7.1 (Fixed + Wakeup Trigger)</option>
        <option value="buggy">Runtime 1 · ADK 2.7.1 (Unpatched / Buggy)</option>
      </select>
      <button id="connectBtn" class="btn-primary" onclick="toggleConnection()">Connect</button>
      <button id="micBtn" class="btn-secondary" onclick="toggleMic()" disabled>Start Mic (16kHz)</button>
    </div>

    <div class="telemetry-grid">
      <div class="telemetry-cell">
        <span class="telemetry-label">Active Agent Node</span>
        <span id="activeAgent" class="telemetry-value">—</span>
      </div>
      <div class="telemetry-cell">
        <span class="telemetry-label">Voice Output Stream</span>
        <span class="telemetry-value">24kHz PCM · Mono</span>
      </div>
      <div class="telemetry-cell">
        <span class="telemetry-label">Decoded Audio Queue</span>
        <span class="telemetry-value"><span id="audioChunks">0</span> chunks</span>
      </div>
    </div>

    <!-- Claude-Code Shrinking Shining Ink Thinking Indicator -->
    <div id="thinkingBanner" class="thinking-banner">
      <span class="shrinking-shining-ink"></span>
      <span id="thinkingText" class="sweep-text">Agent is formulating response...</span>
    </div>

    <div id="log"></div>

    <div class="footer-bar">
      <input id="textInput" type="text" placeholder="Send prompt over Live Bidi stream (e.g. What's the weather in Miami?)" onkeydown="if(event.key==='Enter') sendText()" />
      <button onclick="sendText()" id="sendBtn" class="btn-primary" disabled>Send</button>
    </div>
  </div>

  <script>
    let ws = null;
    let micStream = null;
    let micContext = null;
    let processor = null;
    let isMicActive = false;

    // 24kHz Output Audio Context
    let playContext = null;
    let nextPlayTime = 0;
    let chunkCount = 0;
    let thinkingTimer = null;

    // Dynamic Light / Dark Theme Switcher (Light by default)
    function toggleTheme() {
      const root = document.documentElement;
      const current = root.getAttribute('data-theme') || 'light';
      const next = current === 'light' ? 'dark' : 'light';
      root.setAttribute('data-theme', next);
      document.getElementById('themeIcon').textContent = next === 'light' ? '🌙' : '☀️';
      document.getElementById('themeLabel').textContent = next === 'light' ? 'Dark' : 'Light';
    }

    function setThinking(active, label = 'Agent is formulating response...') {
      const banner = document.getElementById('thinkingBanner');
      const textEl = document.getElementById('thinkingText');
      if (thinkingTimer) {
        clearTimeout(thinkingTimer);
        thinkingTimer = null;
      }
      if (active) {
        textEl.textContent = label;
        banner.classList.add('active');
      } else {
        banner.classList.remove('active');
      }
    }

    function logMsg(text, cls = 'system', metaLabel = '') {
      const el = document.createElement('div');
      el.className = 'msg ' + cls;
      if (metaLabel) {
        const meta = document.createElement('span');
        meta.className = 'msg-meta';
        meta.textContent = metaLabel;
        el.appendChild(meta);
      }
      const body = document.createElement('div');
      body.textContent = text;
      el.appendChild(body);
      const log = document.getElementById('log');
      log.appendChild(el);
      log.scrollTop = log.scrollHeight;
    }

    function playPcm24k(base64Data) {
      if (!playContext) {
        playContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 24000 });
      }
      if (playContext.state === 'suspended') playContext.resume();

      // Normalize URL-safe base64 (- and _) from google.genai.types.Blob to standard base64
      let normB64 = base64Data.replace(/-/g, '+').replace(/_/g, '/');
      while (normB64.length % 4 !== 0) normB64 += '=';
      const binary = atob(normB64);
      const bytes = new Uint8Array(binary.length);
      for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
      const int16 = new Int16Array(bytes.buffer);
      const float32 = new Float32Array(int16.length);
      for (let i = 0; i < int16.length; i++) float32[i] = int16[i] / 32768.0;

      const buffer = playContext.createBuffer(1, float32.length, 24000);
      buffer.getChannelData(0).set(float32);

      const source = playContext.createBufferSource();
      source.buffer = buffer;
      source.connect(playContext.destination);

      const now = playContext.currentTime;
      if (nextPlayTime < now) nextPlayTime = now + 0.02;
      source.start(nextPlayTime);
      nextPlayTime += buffer.duration;

      chunkCount++;
      document.getElementById('audioChunks').textContent = chunkCount;
    }

    async function toggleConnection() {
      if (ws) {
        ws.close();
        return;
      }
      const rt = document.getElementById('runtimeSelect').value;
      const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
      ws = new WebSocket(`${proto}//${location.host}/ws/${rt}`);

      setThinking(true, 'Establishing Live Bidi WebSocket to Vertex AI Agent Engine...');

      ws.onopen = () => {
        setThinking(false);
        const pill = document.getElementById('connStatus');
        pill.classList.add('connected');
        document.getElementById('connText').textContent = 'Connected · ' + rt.toUpperCase();
        document.getElementById('connectBtn').textContent = 'Disconnect';
        document.getElementById('micBtn').disabled = false;
        document.getElementById('sendBtn').disabled = false;
        logMsg(`Session established with Agent Engine (${rt}). Speak into microphone or type below.`);
      };

      ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.author) {
          document.getElementById('activeAgent').textContent = msg.author;
        }
        if (msg.transfer) {
          setThinking(true, `Handoff in progress: transfer_to_agent -> ${msg.transfer}...`);
          logMsg(`transfer_to_agent -> ${msg.transfer}`, 'system', 'AGENT HANDOFF');
        }
        if (msg.tool_call) {
          setThinking(true, `Executing tool: ${msg.tool_call}...`);
          logMsg(`${msg.tool_call}`, 'system', `TOOL EXECUTION · ${msg.author || 'AGENT'}`);
        }
        if (msg.input_transcript) {
          setThinking(true, 'Agent is synthesizing voice response...');
          logMsg(`${msg.input_transcript}`, 'user', 'YOU · AUDIO TRANSCRIPT');
        }
        if (msg.output_transcript) {
          setThinking(false);
          logMsg(`${msg.output_transcript}`, 'agent', `${msg.author || 'AGENT'} · VOICE TRANSCRIPT`);
        }
        if (msg.audio_b64) {
          setThinking(true, `Streaming 24kHz voice audio from ${msg.author || 'agent'}...`);
          playPcm24k(msg.audio_b64);
          if (thinkingTimer) clearTimeout(thinkingTimer);
          thinkingTimer = setTimeout(() => setThinking(false), 1200);
        }
      };

      ws.onclose = () => {
        setThinking(false);
        stopMic();
        ws = null;
        const pill = document.getElementById('connStatus');
        pill.classList.remove('connected');
        document.getElementById('connText').textContent = 'Disconnected';
        document.getElementById('connectBtn').textContent = 'Connect';
        document.getElementById('micBtn').disabled = true;
        document.getElementById('sendBtn').disabled = true;
        logMsg('Session disconnected from Agent Engine.');
      };
    }

    async function toggleMic() {
      if (isMicActive) {
        stopMic();
      } else {
        await startMic();
      }
    }

    async function startMic() {
      try {
        micStream = await navigator.mediaDevices.getUserMedia({ audio: { sampleRate: 16000, channelCount: 1, echoCancellation: true, noiseSuppression: true } });
        micContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
        const source = micContext.createMediaStreamSource(micStream);
        processor = micContext.createScriptProcessor(4096, 1, 1);

        processor.onaudioprocess = (e) => {
          if (!ws || ws.readyState !== WebSocket.OPEN) return;
          const input = e.inputBuffer.getChannelData(0);
          const pcm16 = new Int16Array(input.length);
          for (let i = 0; i < input.length; i++) {
            const s = Math.max(-1, Math.min(1, input[i]));
            pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
          }
          const bytes = new Uint8Array(pcm16.buffer);
          let binary = '';
          for (let i = 0; i < bytes.byteLength; i++) binary += String.fromCharCode(bytes[i]);
          ws.send(JSON.stringify({ type: 'audio', data: btoa(binary) }));
        };

        source.connect(processor);
        processor.connect(micContext.destination);
        isMicActive = true;
        const btn = document.getElementById('micBtn');
        btn.textContent = 'Stop Mic · Live 16kHz';
        btn.className = 'btn-secondary mic-active';
        logMsg('Microphone live PCM streaming active (16kHz). Speak naturally.');
      } catch (err) {
        logMsg('Microphone access error: ' + err.message, 'system');
      }
    }

    function stopMic() {
      if (processor) processor.disconnect();
      if (micContext) micContext.close();
      if (micStream) micStream.getTracks().forEach(t => t.stop());
      isMicActive = false;
      const btn = document.getElementById('micBtn');
      btn.textContent = 'Start Mic (16kHz)';
      btn.className = 'btn-secondary';
    }

    function sendText() {
      const inp = document.getElementById('textInput');
      const text = inp.value.trim();
      if (!text || !ws) return;
      setThinking(true, 'Agent is formulating response...');
      logMsg(`${text}`, 'user', 'YOU · TEXT STREAM');
      ws.send(JSON.stringify({ type: 'text', text }));
      inp.value = '';
    }
  </script>
</body>
</html>
"""


@app.get("/")
async def index():
    return HTMLResponse(HTML_PAGE)


@app.websocket("/ws/{runtime_key}")
async def websocket_endpoint(websocket: WebSocket, runtime_key: str):
    await websocket.accept()
    rt_info = RUNTIMES.get(runtime_key, RUNTIMES["fixed"])
    client = vertexai.Client(project=PROJECT_ID, location=LOCATION)

    try:
        async with client.aio.live.agent_engines.connect(
            agent_engine=rt_info["resource"],
            config={"class_method": "bidi_stream_query"},
        ) as ae_session:
            # Initialize user session with explicit AUDIO modality + transcriptions
            await ae_session.send({
                "user_id": f"web-voice-{runtime_key}",
                "run_config": {
                    "response_modalities": ["AUDIO"],
                    "input_audio_transcription": {},
                    "output_audio_transcription": {},
                },
            })

            async def browser_to_ae():
                try:
                    while True:
                        msg_raw = await websocket.receive_text()
                        msg = json.loads(msg_raw)
                        if msg.get("type") == "audio":
                            await ae_session.send({
                                "blob": {
                                    "mime_type": "audio/pcm;rate=16000",
                                    "data": msg["data"],
                                }
                            })
                        elif msg.get("type") == "text":
                            await ae_session.send({
                                "content": {
                                    "role": "user",
                                    "parts": [{"text": msg["text"]}],
                                }
                            })
                except WebSocketDisconnect:
                    pass

            async def ae_to_browser():
                try:
                    while True:
                        ev_raw = await ae_session.receive()
                        out = ev_raw.get("bidiStreamOutput", ev_raw)
                        author = out.get("author", "")
                        transfer = out.get("actions", {}).get("transfer_to_agent", "")

                        payload = {}
                        if author:
                            payload["author"] = author
                        if transfer:
                            payload["transfer"] = transfer

                        # Extract audio chunks & function calls
                        for p in out.get("content", {}).get("parts", []):
                            if "inline_data" in p and p["inline_data"].get("data"):
                                await websocket.send_json({
                                    "author": author,
                                    "audio_b64": p["inline_data"]["data"],
                                })
                            if "function_call" in p:
                                payload["tool_call"] = f"{p['function_call']['name']}({p['function_call'].get('args', {})})"

                        # Extract input/output transcriptions
                        in_tx = out.get("input_transcription", {})
                        if in_tx and in_tx.get("text") and in_tx.get("finished"):
                            payload["input_transcript"] = in_tx["text"]

                        out_tx = out.get("output_transcription", {})
                        if out_tx and out_tx.get("text") and out_tx.get("finished"):
                            payload["output_transcript"] = out_tx["text"]

                        if len(payload) > 1 or "transfer" in payload or "tool_call" in payload or "output_transcript" in payload or "input_transcript" in payload:
                            await websocket.send_json(payload)
                except Exception:
                    pass

            await asyncio.gather(browser_to_ae(), ae_to_browser())
    except Exception as e:
        try:
            await websocket.send_json({"output_transcript": f"Error: {e}"})
        except Exception:
            pass


if __name__ == "__main__":
    print("🚀 Starting Voice UI Server at http://127.0.0.1:8080")
    uvicorn.run(app, host="127.0.0.1", port=8080)
