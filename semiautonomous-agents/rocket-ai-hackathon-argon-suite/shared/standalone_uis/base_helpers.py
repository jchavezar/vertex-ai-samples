# -*- coding: utf-8 -*-
"""Clean Human-Centric API Bridge, Security URL Sanitizer, Model Selector (`gemini-4-argon` vs `gemini-3.8-flash`),
Universal `gemini-3.8-live` / `Gemini 3.8 Live Extended Thinking` 24kHz Native Audio & Instant Barge-In Engine,
and Slide-Over Blueprint/Code Drawer for the 33 Standalone Demo Apps.
"""

import json
from shared.auth_and_vertex import get_recommended_model_for_square
from shared.catalog_data import CLOUD_RUN_URLS, PROJECTS_BY_CODE


def build_genai_sdk_snippet(code: str, model_id: str) -> str:
    """Returns the official google-genai SDK snippet."""
    proj = PROJECTS_BY_CODE.get(code, PROJECTS_BY_CODE["1.1"])
    sys_p = proj.get("systemPrompt", "You are a Rocket Companies AI specialist.").replace('"', '\\"')
    sample_in = proj.get("sampleInput", "Analyze this scenario.").replace('"', '\\"').replace("\n", "\\n")
    return f'''# Install SDK: pip install --upgrade google-genai
from google import genai
from google.genai import types
import os

def generate_rocket_solution():
    client = genai.Client(
        vertexai=True,
        project=os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos"),
        location="global",
    )

    model = "{model_id}"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="{sample_in[:220]}...")
            ]
        )
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=0.2,
        max_output_tokens=2048,
        system_instruction=[types.Part.from_text(text="{sys_p[:180]}...")],
    )

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )
    print(response.text)

if __name__ == "__main__":
    generate_rocket_solution()
'''


def render_floating_control_bar_and_drawer(code: str, auth_token: str, badge_style: str = "light") -> str:
    """Renders a clean, non-futuristic human-friendly floating utility bar (Portal link, Use-Case switcher,
    Model Selector Dropdown: gemini-4-argon vs gemini-3.8-flash, Live Voice Co-Pilot trigger, and Code Drawer)
    plus the universal Gemini 3.8 Live 24kHz Audio & Barge-In engine (`window.RocketLiveAudio`)."""
    proj = PROJECTS_BY_CODE.get(code, PROJECTS_BY_CODE["1.1"])
    route = get_recommended_model_for_square(code)
    default_model = route.get("default_model", "gemini-4-argon")
    portal_url = f"{CLOUD_RUN_URLS['portal']}?auth_token={auth_token}"
    docs_url = f"{CLOUD_RUN_URLS['portal']}/docs/{code}?auth_token={auth_token}"
    ge_ui_url = "https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023"

    sel_argon = "selected" if default_model == "gemini-4-argon" else ""
    sel_flash = "selected" if default_model == "gemini-3.8-flash" else ""

    snippet_argon = json.dumps(build_genai_sdk_snippet(code, "gemini-4-argon"))
    snippet_flash = json.dumps(build_genai_sdk_snippet(code, "gemini-3.8-flash"))
    proj_json = json.dumps(proj)

    square_options_html = []
    for sq_code, sq_p in PROJECTS_BY_CODE.items():
        sel = "selected" if sq_code == code else ""
        short_name = sq_p["project"][:36]
        square_options_html.append(
            f'<option value="{sq_code}" {sel} style="background:#FFFFFF;color:#0F172A;">{sq_code} · {short_name}</option>'
        )
    square_options_str = "\n      ".join(square_options_html)

    return f"""
<!-- CLEAN HUMAN-CENTRIC FLOATING UTILITY BAR (LIGHT SURFACE) -->
<div id="rkt-floating-pill" style="position:fixed;bottom:16px;right:16px;z-index:9990;display:flex;align-items:center;gap:8px;padding:7px 14px;border-radius:14px;background:rgba(255,255,255,0.96);backdrop-filter:blur(12px);border:1px solid #CBD5E1;box-shadow:0 10px 30px rgba(15,23,42,0.12);font-family:'Plus Jakarta Sans',-apple-system,BlinkMacSystemFont,sans-serif;font-size:12px;color:#1E293B;flex-wrap:wrap;">
  <a href="{portal_url}" style="color:#334155;text-decoration:none;font-weight:600;padding:5px 10px;border-radius:8px;background:#F1F5F9;border:1px solid #E2E8F0;transition:0.15s;white-space:nowrap;">
    ← All Demos
  </a>
  <div style="display:flex;align-items:center;gap:4px;padding:4px 10px;border-radius:8px;background:#F8FAFC;border:1px solid #E2E8F0;">
    <select onchange="window.location.href='/?case='+encodeURIComponent(this.value)" aria-label="Switch Use Case" style="background:transparent;color:#0F172A;font-weight:600;font-family:inherit;font-size:12px;border:none;outline:none;cursor:pointer;max-width:210px;">
      {square_options_str}
    </select>
  </div>
  <div style="display:flex;align-items:center;gap:6px;padding:4px 10px;border-radius:8px;background:#EFF6FF;border:1px solid #BFDBFE;">
    <span style="color:#1D4ED8;font-size:11px;font-weight:700;">Model:</span>
    <select id="model-select" onchange="window.syncSelectedModel(this.value)" aria-label="Select Gemini Model" style="background:transparent;color:#1E3A8A;font-weight:700;font-family:inherit;font-size:12px;border:none;outline:none;cursor:pointer;">
      <option value="gemini-4-argon" {sel_argon}>Gemini 4 Argon (Frontier)</option>
      <option value="gemini-3.8-flash" {sel_flash}>Gemini 3.8 Flash (Low-Latency)</option>
    </select>
  </div>
  <button onclick="window.toggleBlueprintDrawer()" style="background:#0F172A;color:#FFFFFF;border:none;padding:6px 12px;border-radius:8px;font-family:inherit;font-size:12px;font-weight:600;cursor:pointer;white-space:nowrap;">
    Code & Blueprint
  </button>
</div>

<!-- SLIDE-OVER ARCHITECTURE, GENAI SDK CODE & REPRODUCTION DRAWER -->
<div id="rkt-blueprint-drawer" style="position:fixed;top:0;right:-560px;width:min(540px,95vw);height:100vh;z-index:9999;background:#FFFFFF;color:#0F172A;border-left:1px solid #E2E8F0;box-shadow:-16px 0 48px rgba(15,23,42,0.16);transition:right 0.25s cubic-bezier(0.16,1,0.3,1);display:flex;flex-direction:column;font-family:'Plus Jakarta Sans',-apple-system,sans-serif;">
  <div style="padding:18px 22px;border-bottom:1px solid #E2E8F0;display:flex;align-items:center;justify-content:space-between;background:#F8FAFC;">
    <div>
      <div style="font-size:11px;color:#475569;font-weight:600;">Use Case {code} · Technical Blueprint & Vertex AI SDK</div>
      <div style="font-size:16px;font-weight:700;color:#0F172A;margin-top:2px;">{proj['project']}</div>
    </div>
    <button onclick="window.toggleBlueprintDrawer()" style="background:#E2E8F0;color:#334155;border:none;width:32px;height:32px;border-radius:8px;cursor:pointer;font-weight:700;">✕</button>
  </div>
  <div style="padding:20px 22px;overflow-y:auto;flex:1;display:flex;flex-direction:column;gap:18px;">
    <div style="display:flex;gap:8px;flex-wrap:wrap;">
      <a href="{docs_url}" target="_blank" style="flex:1;text-align:center;padding:10px 12px;border-radius:8px;background:#1D4ED8;color:#FFF;text-decoration:none;font-size:12.5px;font-weight:600;">
        Full Reproduction Guide & SKILL.md ↗
      </a>
      <a href="{ge_ui_url}" target="_blank" style="flex:1;text-align:center;padding:10px 12px;border-radius:8px;background:#F3E8FF;border:1px solid #D8B4FE;color:#6B21A8;text-decoration:none;font-size:12.5px;font-weight:600;">
        Open Gemini Enterprise UI ↗
      </a>
    </div>

    <div>
      <div style="font-size:12px;font-weight:700;color:#0F172A;margin-bottom:6px;">
        1. Vertex AI GenAI SDK Implementation (<span id="drawer-model-label" style="color:#1D4ED8;">{default_model}</span>)
      </div>
      <pre id="drawer-sdk-code" style="background:#0F172A;border:1px solid #1E293B;border-radius:10px;padding:14px;font-family:'IBM Plex Mono',monospace;font-size:11.5px;color:#E2E8F0;overflow-x:auto;line-height:1.5;margin:0;"></pre>
    </div>

    <div>
      <div style="font-size:12px;font-weight:700;color:#0F172A;margin-bottom:6px;">
        2. GCP Reference Architecture
      </div>
      <pre style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;padding:14px;font-family:'IBM Plex Mono',monospace;font-size:11px;color:#1E293B;overflow-x:auto;line-height:1.45;margin:0;">{proj.get('archDiagram', '')}</pre>
    </div>

    <div>
      <div style="font-size:12px;font-weight:700;color:#0F172A;margin-bottom:6px;">
        3. Custom Scenario Prompt Override
      </div>
      <textarea id="scenario-input" rows="4" style="width:100%;background:#FFFFFF;border:1px solid #CBD5E1;border-radius:8px;padding:10px;color:#0F172A;font-family:inherit;font-size:12.5px;">{proj.get('sampleInput', '')}</textarea>
      <button onclick="window.runLiveVertexAI()" style="margin-top:8px;width:100%;padding:10px;border-radius:8px;background:#059669;color:#FFF;border:none;font-family:inherit;font-size:13px;font-weight:600;cursor:pointer;">
        Re-Synthesize with Selected Model
      </button>
    </div>
  </div>
</div>

<script>
  // Scrub ?auth_token=... from URL bar after cookie authentication
  (function() {{
    try {{
      if (window.location.search.includes('auth_token=')) {{
        const url = new URL(window.location.href);
        url.searchParams.delete('auth_token');
        window.history.replaceState({{}}, document.title, url.pathname + url.search);
      }}
    }} catch (e) {{}}
  }})();

  window.SQUARE_CODE = "{code}";
  window.ACTIVE_PROJECT = {proj_json};
  window.SDK_SNIPPETS = {{
    "gemini-4-argon": {snippet_argon},
    "gemini-3.8-flash": {snippet_flash}
  }};

  window.getSelectedModel = function() {{
    const el = document.getElementById('model-select') || document.getElementById('app-model-select');
    return el ? el.value : "{default_model}";
  }};

  window.syncSelectedModel = function(val) {{
    const el = document.getElementById('model-select');
    if (el && el.value !== val) el.value = val;
    const topSel = document.getElementById('app-model-select');
    if (topSel && topSel.value !== val) topSel.value = val;
    const lbl = document.getElementById('drawer-model-label');
    if (lbl) lbl.innerText = val;
    const codeEl = document.getElementById('drawer-sdk-code');
    if (codeEl && window.SDK_SNIPPETS[val]) codeEl.textContent = window.SDK_SNIPPETS[val];
    const badgeEl = document.getElementById('live-model-pill');
    if (badgeEl) badgeEl.innerText = val;
  }};

  window.toggleBlueprintDrawer = function() {{
    const dr = document.getElementById('rkt-blueprint-drawer');
    if (!dr) return;
    dr.style.right = (dr.style.right === '0px') ? '-560px' : '0px';
  }};

  // ============================================================================
  // UNIVERSAL GEMINI 3.8 LIVE 24kHz NATIVE AUDIO & INSTANT BARGE-IN ENGINE
  // Eliminates all robotic browser speechSynthesis TTS across every demo!
  // ============================================================================
  window.RocketLiveAudio = (function() {{
    let audioCtx = null;
    let activeSources = [];
    let nextPlayTime = 0;
    let pcmCache = {{}};
    let currentClipBtn = null;
    let currentClipOrigLabel = "";
    let animFrameId = null;

    function ensureCtx() {{
      if (!audioCtx) {{
        const AC = window.AudioContext || window.webkitAudioContext;
        audioCtx = new AC({{ sampleRate: 24000 }});
      }}
      if (audioCtx.state === 'suspended') {{
        audioCtx.resume();
      }}
      return audioCtx;
    }}

    function stopAll() {{
      activeSources.forEach(src => {{
        try {{ src.stop(0); src.disconnect(); }} catch (e) {{}}
      }});
      activeSources = [];
      if (audioCtx) {{
        nextPlayTime = audioCtx.currentTime;
      }}
      if (animFrameId) {{
        cancelAnimationFrame(animFrameId);
        animFrameId = null;
      }}
      if (currentClipBtn) {{
        currentClipBtn.innerHTML = currentClipOrigLabel;
        currentClipBtn.dataset.playing = "0";
        currentClipBtn = null;
      }}
    }}

    function playPcm24kBase64(b64Data, onAmplitude, onEndedCallback) {{
      const ctx = ensureCtx();
      const bin = atob(b64Data);
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

      if (onAmplitude) {{
        const analyser = ctx.createAnalyser();
        analyser.fftSize = 64;
        src.connect(analyser);
        analyser.connect(ctx.destination);
        const dataArr = new Uint8Array(analyser.frequencyBinCount);
        function tick() {{
          if (!activeSources.includes(src)) return;
          analyser.getByteFrequencyData(dataArr);
          let sum = 0;
          for (let i = 0; i < dataArr.length; i++) sum += dataArr[i];
          onAmplitude(sum / (dataArr.length * 255), dataArr);
          animFrameId = requestAnimationFrame(tick);
        }}
        animFrameId = requestAnimationFrame(tick);
      }} else {{
        src.connect(ctx.destination);
      }}

      const now = ctx.currentTime;
      if (nextPlayTime < now) nextPlayTime = now + 0.01;
      src.start(nextPlayTime);
      nextPlayTime += buf.duration;
      activeSources.push(src);

      src.onended = () => {{
        activeSources = activeSources.filter(s => s !== src);
        if (activeSources.length === 0 && onEndedCallback) {{
          onEndedCallback();
        }}
      }};
      return src;
    }}

    async function playClip(text, voice, speakerRole, btnEl, onAmplitude) {{
      if (btnEl && btnEl.dataset.playing === "1") {{
        stopAll();
        return;
      }}
      stopAll();
      ensureCtx();

      if (btnEl) {{
        currentClipBtn = btnEl;
        currentClipOrigLabel = btnEl.innerHTML;
        btnEl.dataset.playing = "1";
        btnEl.innerHTML = "⏳ Connecting Gemini 3.8 Live Audio...";
      }}

      const cacheKey = (voice || "Aoede") + "::" + text;
      try {{
        let pcmB64 = pcmCache[cacheKey];
        if (!pcmB64) {{
          const res = await fetch('/api/live-tts', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
              text: text,
              voice: voice || "Aoede",
              speaker_role: speakerRole || "Rocket Mortgage Voice Co-Pilot",
              live_mode: "gemini-3.8-live"
            }})
          }});
          const data = await res.json();
          if (!data.ok || !data.pcm_b64) {{
            throw new Error(data.error || "Audio stream unavailable");
          }}
          pcmB64 = data.pcm_b64;
          pcmCache[cacheKey] = pcmB64;
        }}
        if (btnEl && currentClipBtn === btnEl) {{
          btnEl.innerHTML = "⏹ Stop Live Audio (Playing 24kHz HD)";
        }}
        playPcm24kBase64(pcmB64, onAmplitude, () => {{
          if (btnEl && currentClipBtn === btnEl) {{
            btnEl.innerHTML = currentClipOrigLabel;
            btnEl.dataset.playing = "0";
            currentClipBtn = null;
          }}
          if (onAmplitude) onAmplitude(0, null);
        }});
      }} catch (err) {{
        if (btnEl) {{
          btnEl.innerHTML = currentClipOrigLabel;
          btnEl.dataset.playing = "0";
          currentClipBtn = null;
        }}
        console.error("Gemini 3.8 Live TTS error:", err);
      }}
    }}

    return {{
      ensureCtx: ensureCtx,
      stopAll: stopAll,
      playPcm24kBase64: playPcm24kBase64,
      playClip: playClip,
      isPlaying: () => activeSources.length > 0
    }};
  }})();

  window.stopAllLiveAudio = window.RocketLiveAudio.stopAll;
  window.playLiveCallClip = window.RocketLiveAudio.playClip;

  document.addEventListener('DOMContentLoaded', () => {{
    window.syncSelectedModel("{default_model}");
  }});
</script>
"""
