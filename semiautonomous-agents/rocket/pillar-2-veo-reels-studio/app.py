"""Standalone FastAPI Microservice for Pillar 2: Veo 3.1 9:16 Vertical Reels Studio.

Exposes:
  - GET  /                         Interactive 9:16 Reel Studio HTML or JSON Health
  - GET  /api/pillar2/presets      Returns 8-preset reel vault
  - GET  /api/pillar2/preset/{id}  Returns single preset reel
  - POST /api/pillar2/generate-reel Synthesizes reel from text prompt + financials
  - POST /api/pillar2/generate     Alias for /api/pillar2/generate-reel
  - GET  /healthz                  Kubernetes / Cloud Run liveness probe
  - Mounted: /static/reels         Serves 9:16 MP4 video assets
  - Mounted: /frontend             Serves p2_reels_player.js
"""

import asyncio
import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from engine import PRESET_REELS, generate_reel_from_text

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Rocket × Pillar 2: Veo 3.1 Reels Studio Microservice",
    description="Standalone 9:16 vertical social reel synthesis microservice powered by Google Veo 3.1 + Gemini 3.8",
    version="2.0.0",
)

STATIC_REELS_DIR = BASE_DIR / "static" / "reels"
STATIC_REELS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static/reels", StaticFiles(directory=str(STATIC_REELS_DIR)), name="static_reels")

FRONTEND_DIR = BASE_DIR / "frontend"
FRONTEND_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")

ASSETS_DIR = BASE_DIR / "assets"
if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Pillar 2 · Veo 3.1 9:16 Reels Studio</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #090D16;
      --card-bg: #111827;
      --border: #1E293B;
      --accent: #D81E28;
      --blue: #1A73E8;
      --text: #F8FAFC;
      --text-muted: #94A3B8;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: 'Plus Jakarta Sans', sans-serif;
      padding: 24px;
    }
    .container { max-width: 1200px; margin: 0 auto; }
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--border);
    }
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 12px;
      border-radius: 9999px;
      font-size: 12px;
      font-weight: 700;
      background: rgba(216, 30, 40, 0.15);
      color: #F87171;
      border: 1px solid rgba(216, 30, 40, 0.3);
    }
    .dot-pulse {
      width: 8px; height: 8px; border-radius: 50%; background: #F87171;
      box-shadow: 0 0 8px #F87171;
    }
    .preset-strip {
      display: flex;
      gap: 10px;
      overflow-x: auto;
      margin-bottom: 20px;
      padding-bottom: 6px;
    }
    .preset-pill {
      padding: 10px 16px;
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      color: var(--text);
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.15s ease;
    }
    .preset-pill.active {
      background: rgba(216, 30, 40, 0.15);
      border-color: var(--accent);
      color: #FFF;
    }
    .layout {
      display: grid;
      grid-template-columns: 340px 1fr 340px;
      gap: 24px;
    }
    @media (max-width: 1080px) {
      .layout { grid-template-columns: 1fr; }
    }
    .card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 20px;
    }
    /* 9:16 Vertical Video Phone Frame */
    .stage-wrapper {
      display: flex;
      justify-content: center;
    }
    .phone-frame {
      width: 320px;
      height: 568px;
      border-radius: 28px;
      background: #000;
      border: 3px solid #334155;
      position: relative;
      overflow: hidden;
      box-shadow: 0 20px 50px rgba(0,0,0,0.7);
    }
    video {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }
    .poster-overlay {
      position: absolute;
      top: 0; left: 0; width: 100%; height: 100%;
      background-size: cover;
      background-position: center;
      pointer-events: none;
      transition: opacity 0.4s ease;
      opacity: 0;
    }
    /* PITI Mortgage Sticker */
    .piti-sticker {
      position: absolute;
      top: 20px;
      left: 16px;
      right: 16px;
      background: rgba(15, 23, 42, 0.88);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255,255,255,0.15);
      border-radius: 16px;
      padding: 12px 14px;
      box-shadow: 0 8px 24px rgba(0,0,0,0.5);
    }
    .piti-sticker-badge {
      font-size: 10px;
      font-weight: 800;
      color: #38BDF8;
      letter-spacing: 0.5px;
      text-transform: uppercase;
    }
    .piti-sticker-amount {
      font-size: 22px;
      font-weight: 800;
      font-family: 'JetBrains Mono', monospace;
      color: #FFF;
      margin: 2px 0;
    }
    .piti-sticker-sub {
      font-size: 11px;
      color: #94A3B8;
    }
    .credit-pill {
      display: inline-block;
      margin-top: 6px;
      background: rgba(5, 150, 105, 0.2);
      border: 1px solid #059669;
      color: #34D399;
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 700;
    }
    .hud-overlay {
      position: absolute;
      top: 0; left: 0; width: 100%; height: 100%;
      background: rgba(9, 13, 22, 0.88);
      backdrop-filter: blur(8px);
      display: none;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 24px;
      text-align: center;
      z-index: 10;
    }
    .progress-bar-bg {
      width: 100%;
      height: 8px;
      background: #1E293B;
      border-radius: 4px;
      overflow: hidden;
      margin: 16px 0;
    }
    .progress-bar-fill {
      height: 100%;
      width: 0%;
      background: var(--accent);
      transition: width 0.3s ease;
    }
    .form-group { margin-bottom: 14px; }
    label { display: block; font-size: 12px; font-weight: 700; color: var(--text-muted); margin-bottom: 5px; }
    input[type=text], textarea {
      width: 100%;
      padding: 10px 12px;
      border-radius: 8px;
      background: #0F172A;
      border: 1px solid var(--border);
      color: #FFF;
      font-size: 13px;
      font-family: inherit;
    }
    input[type=range] { width: 100%; accent-color: var(--accent); }
    .btn-gen {
      width: 100%;
      padding: 12px;
      background: var(--accent);
      border: none;
      border-radius: 10px;
      color: #FFF;
      font-weight: 700;
      font-size: 14px;
      cursor: pointer;
    }
    .caption-list { display: flex; flex-direction: column; gap: 8px; }
    .caption-item {
      padding: 10px 12px;
      border-radius: 10px;
      background: #0F172A;
      border: 1px solid var(--border);
    }
    .cap-tag { font-size: 10px; color: #60A5FA; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
    .cap-text { font-size: 12px; font-weight: 600; margin-top: 2px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div>
        <h1 style="margin:0; font-size:22px; font-weight:800;">Pillar 2 · Veo 3.1 9:16 Social Reels Studio</h1>
        <p style="margin:4px 0 0; font-size:13px; color:var(--text-muted);">
          Automated Text-to-9:16 Video Synthesis with Dynamic PITI Mortgage Underwriting Sticker
        </p>
      </div>
      <div class="badge">
        <span class="dot-pulse"></span>
        <span id="p2-badge-text">Port 8082 · Standalone</span>
      </div>
    </div>

    <div class="preset-strip" id="preset-strip">
      <button class="preset-pill active" data-id="royal_oak">Royal Oak MI Craftsman</button>
      <button class="preset-pill" data-id="corktown_loft">Detroit Corktown Loft</button>
      <button class="preset-pill" data-id="ann_arbor">Ann Arbor Mid-Century</button>
      <button class="preset-pill" data-id="birmingham">Birmingham MI Tudor</button>
      <button class="preset-pill" data-id="austin_lake">Austin TX Waterfront</button>
    </div>

    <div class="layout">
      <!-- Left: Prompt & Underwriting Form -->
      <div class="card">
        <h3 style="margin-top:0; font-size:15px;">Listing &amp; Underwriting</h3>
        <div class="form-group">
          <label>Architectural Prompt</label>
          <textarea id="p2-prompt" rows="4">Modern craftsman home in Royal Oak MI at golden hour, warm interior lights glowing, manicured lawn</textarea>
        </div>
        <div class="form-group">
          <label>Listing Price ($) <span id="disp-price" style="float:right;color:#FFF;font-family:'JetBrains Mono';">$460,000</span></label>
          <input type="range" id="p2-price" min="200000" max="1500000" step="10000" value="460000">
        </div>
        <div class="form-group">
          <label>Down Payment (%) <span id="disp-down" style="float:right;color:#FFF;font-family:'JetBrains Mono';">10%</span></label>
          <input type="range" id="p2-down" min="3" max="30" step="1" value="10">
        </div>
        <div class="form-group">
          <label>30-Yr Fixed Rate (%) <span id="disp-rate" style="float:right;color:#FFF;font-family:'JetBrains Mono';">5.875%</span></label>
          <input type="range" id="p2-rate" min="4.5" max="8.0" step="0.125" value="5.875">
        </div>
        <button class="btn-gen" id="btn-generate">Generate 9:16 Reel (Veo 3.1)</button>
      </div>

      <!-- Center: 9:16 Vertical Video Phone Frame with PITI Sticker Overlay -->
      <div class="stage-wrapper">
        <div class="phone-frame">
          <video id="p2-video" autoplay loop muted playsinline></video>
          <div class="poster-overlay" id="p2-poster"></div>

          <!-- PITI Underwriting Sticker -->
          <div class="piti-sticker">
            <div class="piti-sticker-badge">Rocket Mortgage · Verified PITI</div>
            <div class="piti-sticker-amount" id="sticker-piti">$2,890/mo</div>
            <div class="piti-sticker-sub" id="sticker-sub">10% Down · 5.875% Fixed</div>
            <div class="credit-pill" id="sticker-credit">+$4,600 Closing Credit</div>
          </div>

          <!-- 3-Step Veo Generation HUD -->
          <div class="hud-overlay" id="p2-hud">
            <div class="dot-pulse" style="width:14px;height:14px;margin-bottom:12px;"></div>
            <div class="hud-step-label" style="font-size:11px;font-weight:700;color:#F87171;">Step 1/3</div>
            <div class="hud-title-label" style="font-size:13px;font-weight:700;margin-top:6px;color:#FFF;">Synthesizing Screenplay...</div>
            <div class="progress-bar-bg"><div class="progress-bar-fill"></div></div>
          </div>
        </div>
      </div>

      <!-- Right: Voiceover Script & Captions -->
      <div class="card">
        <h3 style="margin-top:0; font-size:15px;">24kHz Voiceover &amp; Captions</h3>
        <div class="form-group">
          <label>Voiceover Script</label>
          <div id="p2-vo-script" style="background:#0F172A;padding:12px;border-radius:10px;font-size:12.5px;color:#CBD5E1;line-height:1.5;">--</div>
        </div>
        <label>4-Scene Captions</label>
        <div class="caption-list" id="p2-captions"></div>
      </div>
    </div>
  </div>

  <script src="/frontend/p2_reels_player.js"></script>
  <script>
    const stageEls = {
      video: document.getElementById('p2-video'),
      posterOverlay: document.getElementById('p2-poster'),
      stickerPiti: document.getElementById('sticker-piti'),
      stickerCredit: document.getElementById('sticker-credit'),
      stickerSub: document.getElementById('sticker-sub'),
      captionList: document.getElementById('p2-captions')
    };

    const priceEl = document.getElementById('p2-price');
    const downEl = document.getElementById('p2-down');
    const rateEl = document.getElementById('p2-rate');

    function syncFinancials() {
      const p = parseInt(priceEl.value, 10);
      const d = parseInt(downEl.value, 10);
      const r = parseFloat(rateEl.value);
      document.getElementById('disp-price').innerText = '$' + p.toLocaleString();
      document.getElementById('disp-down').innerText = d + '%';
      document.getElementById('disp-rate').innerText = r.toFixed(3) + '%';
      const fin = window.P2ReelsPlayer.calculateFinancials(p, d, r);
      stageEls.stickerPiti.innerText = '$' + fin.monthlyPITI.toLocaleString() + '/mo';
      stageEls.stickerCredit.innerText = '+$' + fin.closingCredit.toLocaleString() + ' Closing Credit';
      stageEls.stickerSub.innerText = d + '% Down · ' + r.toFixed(3) + '% 30-Yr Fixed';
    }

    [priceEl, downEl, rateEl].forEach(el => el.addEventListener('input', syncFinancials));

    // Preset selection
    document.querySelectorAll('.preset-pill').forEach(btn => {
      btn.addEventListener('click', async () => {
        document.querySelectorAll('.preset-pill').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const presetId = btn.dataset.id;
        try {
          const data = await window.P2ReelsPlayer.fetchPreset(presetId);
          loadReelData(data);
        } catch (err) {
          console.error(err);
        }
      });
    });

    function loadReelData(data) {
      window.P2ReelsPlayer.applyReelToStage(stageEls, data);
      document.getElementById('p2-prompt').value = data.prompt || data.veo_visual_prompt || '';
      if (data.price) { priceEl.value = data.price; }
      if (data.down_pct) { downEl.value = data.down_pct; }
      if (data.rate_pct) { rateEl.value = data.rate_pct; }
      document.getElementById('p2-vo-script').innerText = data.voiceover_script || '';
      syncFinancials();
    }

    // Generate reel
    document.getElementById('btn-generate').addEventListener('click', async () => {
      const hud = window.P2ReelsPlayer.showVeoGenerationHUD(document.getElementById('p2-hud'), false);
      try {
        setTimeout(() => hud.toStep2(), 600);
        setTimeout(() => hud.toStep3(), 1200);

        const data = await window.P2ReelsPlayer.generateReel({
          prompt_text: document.getElementById('p2-prompt').value,
          price: parseInt(priceEl.value, 10),
          down_pct: parseInt(downEl.value, 10),
          rate_pct: parseFloat(rateEl.value),
          voice: 'Aoede',
          generate_live_veo_mp4: false
        });

        hud.finish();
        loadReelData(data);
      } catch (err) {
        hud.hide();
        alert('Generation failed: ' + err.message);
      }
    });

    // Boot first preset
    window.addEventListener('DOMContentLoaded', async () => {
      try {
        const presets = await window.P2ReelsPlayer.fetchPresets();
        if (presets && presets.presets && presets.presets.length) {
          loadReelData(presets.presets[0]);
        }
      } catch (e) {
        console.warn(e);
      }
    });
  </script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """Renders standalone interactive 9:16 reel studio, or returns JSON health if requested."""
    accept = request.headers.get("accept", "")
    if "application/json" in accept or request.query_params.get("format") == "json":
        return JSONResponse({
            "ok": True,
            "service": "pillar-2-veo-reels-studio",
            "port": 8082,
            "engine": "Vertex AI Veo 3.1 + Gemini 3.8 Flash + Imagen 4",
            "presets_count": len(PRESET_REELS),
        })
    return HTMLResponse(INDEX_HTML)


@app.get("/api/pillar2/presets")
async def api_p2_presets():
    """Returns the preset reel catalog."""
    return JSONResponse({"ok": True, "count": len(PRESET_REELS), "presets": list(PRESET_REELS.values())})


@app.get("/api/pillar2/preset/{preset_id}")
async def api_p2_preset(preset_id: str):
    """Returns a specific preset reel configuration."""
    preset = PRESET_REELS.get(preset_id, PRESET_REELS.get("royal_oak"))
    if not preset:
        return JSONResponse({"ok": False, "error": f"Preset '{preset_id}' not found"}, status_code=404)
    return JSONResponse(preset)


@app.post("/api/pillar2/generate-reel")
@app.post("/api/pillar2/generate")
async def api_p2_generate(request: Request):
    """Generates a vertical social reel from text prompt + financial underwriting parameters."""
    try:
        body = await request.json()
    except Exception:
        body = {}

    res = await asyncio.to_thread(
        generate_reel_from_text,
        prompt_text=body.get("prompt_text", "Modern home in Royal Oak MI"),
        price=int(body.get("price", 460000)),
        rate_pct=float(body.get("rate_pct", 5.875)),
        down_pct=int(body.get("down_pct", 10)),
        voice=body.get("voice", "Aoede"),
        generate_live_veo_mp4=bool(body.get("generate_live_veo_mp4", False)),
        static_reels_dir=str(STATIC_REELS_DIR),
        current_video_url=str(body.get("current_video_url", "")),
    )
    return JSONResponse(res)


@app.get("/healthz")
async def healthz():
    return JSONResponse({"status": "ok", "service": "pillar-2-veo-reels-studio", "port": 8082})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8082, reload=True)
