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
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>ADK Live Voice Tester — Agent Engine</title>
  <style>
    :root { --bg: #0f172a; --card: #1e293b; --accent: #38bdf8; --green: #22c55e; --red: #ef4444; --text: #f8fafc; }
    body { font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 24px; display: flex; flex-direction: column; align-items: center; }
    .container { width: 100%; max-width: 760px; background: var(--card); border-radius: 14px; padding: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.4); }
    h2 { margin-top: 0; display: flex; align-items: center; justify-content: space-between; }
    .controls { display: flex; gap: 12px; align-items: center; margin-bottom: 16px; flex-wrap: wrap; }
    select, button, input { padding: 10px 14px; border-radius: 8px; border: 1px solid #334155; background: #0f172a; color: white; font-size: 14px; }
    button { cursor: pointer; font-weight: 600; transition: 0.15s; }
    button.primary { background: var(--accent); color: #0f172a; border: none; }
    button.mic-active { background: var(--red); color: white; border: none; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.65; } 100% { opacity: 1; } }
    .status-bar { display: flex; justify-content: space-between; padding: 10px 14px; background: #0f172a; border-radius: 8px; margin-bottom: 16px; font-size: 13px; }
    .badge { padding: 3px 8px; border-radius: 6px; font-weight: 600; background: #334155; }
    .badge.agent { background: #0284c7; }
    .badge.transfer { background: #d97706; }
    #log { height: 380px; overflow-y: auto; background: #090d16; padding: 14px; border-radius: 8px; font-family: ui-monospace, monospace; font-size: 13px; display: flex; flex-direction: column; gap: 8px; }
    .msg { padding: 8px 12px; border-radius: 6px; line-height: 1.4; }
    .msg.user { background: #1e3a8a; align-self: flex-end; }
    .msg.agent { background: #1e293b; border-left: 3px solid var(--accent); }
    .msg.system { background: #334155; color: #cbd5e1; font-size: 12px; }
  </style>
</head>
<body>
  <div class="container">
    <h2>
      <span>🎙️ ADK Live Voice Tester</span>
      <span id="connStatus" class="badge">Disconnected</span>
    </h2>

    <div class="controls">
      <select id="runtimeSelect">
        <option value="fixed">Runtime 2: ADK 2.7.1 (Fixed + Wakeup Trigger)</option>
        <option value="buggy">Runtime 1: ADK 2.7.1 (Unpatched / Buggy)</option>
      </select>
      <button id="connectBtn" class="primary" onclick="toggleConnection()">Connect</button>
      <button id="micBtn" onclick="toggleMic()" disabled>🎤 Start Mic</button>
    </div>

    <div class="controls">
      <input id="textInput" type="text" placeholder="Or type a message over Live Bidi stream (e.g. What's the weather in Miami?)" style="flex:1" onkeydown="if(event.key==='Enter') sendText()" />
      <button onclick="sendText()" id="sendBtn" disabled>Send</button>
    </div>

    <div class="status-bar">
      <span>Active Agent: <span id="activeAgent" class="badge agent">-</span></span>
      <span>Audio Queue: <span id="audioChunks">0</span> chunks</span>
    </div>

    <div id="log"></div>
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

    function logMsg(text, cls = 'system') {
      const el = document.createElement('div');
      el.className = 'msg ' + cls;
      el.textContent = text;
      const log = document.getElementById('log');
      log.appendChild(el);
      log.scrollTop = log.scrollHeight;
    }

    function playPcm24k(base64Data) {
      if (!playContext) {
        playContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 24000 });
      }
      if (playContext.state === 'suspended') playContext.resume();

      const binary = atob(base64Data);
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

      ws.onopen = () => {
        document.getElementById('connStatus').textContent = 'Connected (' + rt.toUpperCase() + ')';
        document.getElementById('connStatus').style.background = '#16a34a';
        document.getElementById('connectBtn').textContent = 'Disconnect';
        document.getElementById('micBtn').disabled = false;
        document.getElementById('sendBtn').disabled = false;
        logMsg(`Connected to Agent Engine (${rt}). Speak into mic or type below!`);
      };

      ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.author) {
          document.getElementById('activeAgent').textContent = msg.author;
        }
        if (msg.transfer) {
          logMsg(`⚡ Handoff: transfer_to_agent -> ${msg.transfer}`, 'system');
        }
        if (msg.tool_call) {
          logMsg(`🛠️ [${msg.author}] Tool Call: ${msg.tool_call}`, 'system');
        }
        if (msg.input_transcript) {
          logMsg(`🎤 You: ${msg.input_transcript}`, 'user');
        }
        if (msg.output_transcript) {
          logMsg(`🔊 [${msg.author}]: ${msg.output_transcript}`, 'agent');
        }
        if (msg.audio_b64) {
          playPcm24k(msg.audio_b64);
        }
      };

      ws.onclose = () => {
        stopMic();
        ws = null;
        document.getElementById('connStatus').textContent = 'Disconnected';
        document.getElementById('connStatus').style.background = '#334155';
        document.getElementById('connectBtn').textContent = 'Connect';
        document.getElementById('micBtn').disabled = true;
        document.getElementById('sendBtn').disabled = true;
        logMsg('Disconnected from Agent Engine.');
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
        btn.textContent = '🛑 Stop Mic (Streaming 16kHz)';
        btn.className = 'mic-active';
        logMsg('🎙️ Microphone live streaming started (16kHz PCM)...');
      } catch (err) {
        logMsg('Mic error: ' + err.message, 'system');
      }
    }

    function stopMic() {
      if (processor) processor.disconnect();
      if (micContext) micContext.close();
      if (micStream) micStream.getTracks().forEach(t => t.stop());
      isMicActive = false;
      const btn = document.getElementById('micBtn');
      btn.textContent = '🎤 Start Mic';
      btn.className = '';
    }

    function sendText() {
      const inp = document.getElementById('textInput');
      const text = inp.value.trim();
      if (!text || !ws) return;
      logMsg(`⌨️ You: ${text}`, 'user');
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
            # Initialize user session
            await ae_session.send({"user_id": f"web-voice-{runtime_key}"})

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
