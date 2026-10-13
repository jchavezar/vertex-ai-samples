# -*- coding: utf-8 -*-
"""Square 4.4 — Automated Multi-Format Video Tour & Rate-Drop Producer (Veo 3.1 + Gempix-2).
Visual Design: CapCut / Premiere Pro 9:16 Vertical Reels & TikTok NLE Video Studio.
Palette: #0E0E12 studio carbon, #FACC15 cyber yellow playhead, #A855F7 track purple.
Typography: Google Fonts 'Archivo' + 'JetBrains Mono'.
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_4_4(auth_token: str) -> str:
    floating_drawer = render_floating_control_bar_and_drawer("4.4", auth_token)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>4.4 Veo 3.1 + Gempix-2 Vertical NLE Video Studio | Rocket × Redfin</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --carbon: #0E0E12;
      --panel: #15151C;
      --panel-elev: #1E1E28;
      --track-bg: #111117;
      --cyber-yellow: #FACC15;
      --track-purple: #A855F7;
      --crimson: #E11D48;
      --emerald: #10B981;
      --cyan: #06B6D4;
      --text: #F8FAFC;
      --muted: #9CA3AF;
      --border: #272736;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: var(--carbon);
      color: var(--text);
      font-family: 'Archivo', sans-serif;
      min-height: 100vh;
      overflow-x: hidden;
      padding-bottom: 92px;
      display: flex;
      flex-direction: column;
    }}
    .mono {{ font-family: 'JetBrains Mono', monospace; }}

    /* Top Premiere / CapCut Studio Header */
    .nle-header {{
      background: #09090D;
      border-bottom: 1px solid var(--border);
      padding: 10px 22px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 12px;
    }}
    .nle-left {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}
    .veo-badge {{
      background: linear-gradient(135deg, var(--track-purple), var(--crimson));
      color: #FFF;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 800;
      padding: 5px 10px;
      border-radius: 6px;
      letter-spacing: 0.05em;
    }}
    .project-title {{
      font-size: 15px;
      font-weight: 800;
      letter-spacing: -0.01em;
    }}
    .project-meta {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      color: var(--muted);
    }}
    .nle-right {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .model-box {{
      display: flex;
      align-items: center;
      gap: 8px;
      background: var(--panel-elev);
      border: 1px solid var(--border);
      padding: 5px 10px;
      border-radius: 6px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
    }}
    #app-model-select {{
      background: transparent;
      color: var(--cyber-yellow);
      border: none;
      outline: none;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
    }}
    #app-model-select option {{
      background: var(--panel);
      color: #FFF;
    }}
    .btn-export-reel {{
      background: var(--cyber-yellow);
      color: #09090D;
      border: none;
      padding: 8px 16px;
      border-radius: 6px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      cursor: pointer;
      box-shadow: 0 4px 16px rgba(250, 204, 21, 0.3);
      transition: 0.15s;
    }}
    .btn-export-reel:hover {{
      transform: translateY(-1px);
      background: #FDE047;
    }}

    /* Upper NLE Workspace: Left Media Bin, Center 9:16 Phone Monitor, Right Inspector */
    .nle-upper-grid {{
      display: grid;
      grid-template-columns: 290px 1fr 410px;
      gap: 14px;
      padding: 14px 20px;
      flex: 1;
    }}
    @media (max-width: 1200px) {{
      .nle-upper-grid {{ grid-template-columns: 1fr; }}
    }}
    .nle-pane {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 16px;
      display: flex;
      flex-direction: column;
    }}
    .pane-head {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
      padding-bottom: 10px;
      margin-bottom: 12px;
      border-bottom: 1px solid var(--border);
    }}

    /* Scene Clips in Media Bin */
    .clip-card {{
      background: var(--panel-elev);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 10px 12px;
      margin-bottom: 10px;
      cursor: pointer;
      transition: 0.15s;
    }}
    .clip-card:hover {{
      border-color: var(--track-purple);
    }}
    .clip-card.active {{
      border: 1.5px solid var(--cyber-yellow);
      background: rgba(250, 204, 21, 0.07);
    }}
    .clip-time {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
      color: var(--cyber-yellow);
      margin-bottom: 3px;
    }}
    .clip-name {{
      font-size: 13px;
      font-weight: 700;
      margin-bottom: 2px;
    }}
    .clip-motion {{
      font-size: 11px;
      color: var(--muted);
    }}

    /* Center 9:16 Vertical Smartphone Preview Monitor */
    .monitor-stage {{
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      background: #0A0A0E;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 16px;
      position: relative;
    }}
    .phone-9-16 {{
      width: 292px;
      height: 518px;
      border-radius: 34px;
      border: 6px solid #2A2A38;
      background: #14141D;
      position: relative;
      overflow: hidden;
      box-shadow: 0 24px 60px rgba(0,0,0,0.85), 0 0 0 1px rgba(168,85,247,0.3);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}
    .phone-notch {{
      position: absolute;
      top: 8px;
      left: 50%;
      transform: translateX(-50%);
      width: 84px;
      height: 18px;
      background: #07070A;
      border-radius: 999px;
      z-index: 15;
    }}
    .reel-canvas-bg {{
      position: absolute;
      inset: 0;
      z-index: 1;
      transition: all 0.45s ease;
    }}
    /* Animated Top HUD inside Phone */
    .reel-top-hud {{
      position: relative;
      z-index: 10;
      padding: 34px 14px 10px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-family: 'JetBrains Mono', monospace;
      font-size: 9px;
    }}
    .synthid-chip {{
      background: rgba(0,0,0,0.65);
      border: 1px solid rgba(255,255,255,0.25);
      padding: 3px 7px;
      border-radius: 999px;
      color: #E2E8F0;
    }}
    /* Lower-Third Rate Drop & Caption Overlay inside Phone */
    .reel-lower-third {{
      position: relative;
      z-index: 10;
      padding: 12px;
      background: linear-gradient(180deg, transparent 0%, rgba(7,7,11,0.92) 32%, rgba(7,7,11,0.98) 100%);
    }}
    .rate-drop-banner {{
      background: linear-gradient(90deg, var(--crimson), #9F1239);
      border: 1.5px solid var(--cyber-yellow);
      border-radius: 8px;
      padding: 8px 10px;
      margin-bottom: 8px;
      box-shadow: 0 6px 20px rgba(225, 29, 72, 0.5);
    }}
    .rate-drop-kicker {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 9px;
      font-weight: 700;
      color: var(--cyber-yellow);
      text-transform: uppercase;
    }}
    .rate-drop-nums {{
      font-size: 16px;
      font-weight: 900;
      color: #FFF;
      letter-spacing: -0.02em;
    }}
    .reel-caption-box {{
      background: rgba(255,255,255,0.1);
      backdrop-filter: blur(8px);
      border-left: 3px solid var(--cyber-yellow);
      padding: 7px 9px;
      border-radius: 4px;
      font-size: 11.5px;
      font-weight: 700;
      line-height: 1.35;
      color: #FFF;
      margin-bottom: 8px;
    }}
    .reel-regz-micro {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 7.5px;
      line-height: 1.3;
      color: #9CA3AF;
    }}

    /* Transport Play/Pause Controls Below Phone */
    .transport-bar {{
      margin-top: 12px;
      display: flex;
      align-items: center;
      gap: 12px;
      background: var(--panel);
      padding: 7px 16px;
      border-radius: 999px;
      border: 1px solid var(--border);
    }}
    .btn-play {{
      background: var(--cyber-yellow);
      color: #09090D;
      border: none;
      width: 32px;
      height: 32px;
      border-radius: 50%;
      font-weight: 900;
      cursor: pointer;
    }}
    .timecode-readout {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      font-weight: 700;
      color: var(--cyber-yellow);
    }}

    /* Bottom 4-Track Multi-Scene Timeline Scrubber */
    .timeline-dock {{
      margin: 0 20px 16px;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 14px 18px;
      position: relative;
    }}
    .timeline-ruler {{
      display: flex;
      justify-content: space-between;
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
      color: var(--muted);
      padding-left: 170px;
      margin-bottom: 8px;
      border-bottom: 1px solid var(--border);
      padding-bottom: 6px;
    }}
    .tracks-wrapper {{
      position: relative;
    }}
    .playhead-line {{
      position: absolute;
      top: -18px;
      bottom: 0;
      left: calc(170px + 18%);
      width: 2px;
      background: var(--cyber-yellow);
      z-index: 25;
      pointer-events: none;
      box-shadow: 0 0 10px var(--cyber-yellow);
      transition: left 0.2s linear;
    }}
    .playhead-cap {{
      width: 12px;
      height: 12px;
      background: var(--cyber-yellow);
      transform: translateX(-5px) rotate(45deg);
    }}
    .track-row {{
      display: grid;
      grid-template-columns: 160px 1fr;
      gap: 10px;
      align-items: center;
      margin-bottom: 8px;
    }}
    .track-label {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 10.5px;
      font-weight: 700;
      color: #E2E8F0;
      background: var(--panel-elev);
      padding: 7px 10px;
      border-radius: 6px;
      border-left: 3px solid var(--track-purple);
    }}
    .track-lane {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 6px;
      background: var(--track-bg);
      padding: 4px;
      border-radius: 6px;
      border: 1px solid var(--border);
    }}
    .track-block {{
      padding: 6px 8px;
      border-radius: 4px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      cursor: pointer;
    }}
  </style>
</head>
<body>

  <!-- TOP PREMIERE / CAPCUT NLE BAR -->
  <header class="nle-header">
    <div class="nle-left">
      <span class="veo-badge">VEO 3.1 × GEMPIX-2 NLE</span>
      <div>
        <div class="project-title">MI-772190_HuntingtonWoods_RateDrop_9x16.prproj</div>
        <div class="project-meta">1080×1920 Vertical Reel • 60 FPS • SynthID Watermarked • TILA Reg Z Track Locked</div>
      </div>
    </div>
    <div class="nle-right">
      <div class="model-box">
        <span style="color:var(--muted);">DIRECTOR MODEL:</span>
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)">
          <option value="gemini-4-argon" selected>gemini-4-argon (Frontier Storyboard)</option>
          <option value="gemini-3.8-flash">gemini-3.8-flash (Fast Omni Sync)</option>
        </select>
      </div>
      <button class="btn-export-reel" id="btn-produce-reel" onclick="window.runLiveVertexAI()">
        ⚡ Produce Veo 3.1 Multi-Scene Reel & Script
      </button>
    </div>
  </header>

  <!-- UPPER 3-PANE STUDIO -->
  <div class="nle-upper-grid">
    <!-- LEFT: 4 SCENE CLIPS BIN -->
    <aside class="nle-pane">
      <div class="pane-head">
        <span>VEO 3.1 SCENE BIN (4 CLIPS)</span>
        <span style="color:var(--cyber-yellow);">15.0s TOTAL</span>
      </div>

      <div class="clip-card active" data-scene="0" onclick="window.selectScene(0)">
        <div class="clip-time">SCENE 01 • 00:00.0 – 00:03.5</div>
        <div class="clip-name">Autumn Maple Curb Dolly</div>
        <div class="clip-motion">Camera: Fast Dolly Zoom In • 24mm f/1.8</div>
      </div>

      <div class="clip-card" data-scene="1" onclick="window.selectScene(1)">
        <div class="clip-time">SCENE 02 • 00:03.5 – 00:07.5</div>
        <div class="clip-name">Vaulted Quartz Chef Kitchen</div>
        <div class="clip-motion">Camera: Smooth Orbital Pan • Sunburst</div>
      </div>

      <div class="clip-card" data-scene="2" onclick="window.selectScene(2)">
        <div class="clip-time">SCENE 03 • 00:07.5 – 00:11.5</div>
        <div class="clip-name">Sunlit Primary Suite & Cedar Deck</div>
        <div class="clip-motion">Camera: Gimbal Push Through Glass Doors</div>
      </div>

      <div class="clip-card" data-scene="3" onclick="window.selectScene(3)">
        <div class="clip-time">SCENE 04 • 00:11.5 – 00:15.0</div>
        <div class="clip-name">Redfin × Rocket 1-Tap Pre-Approval</div>
        <div class="clip-motion">Overlay: Gempix-2 End-Card + Reg Z Lock</div>
      </div>

      <div style="margin-top:auto;padding-top:12px;border-top:1px solid var(--border);font-family:'JetBrains Mono',monospace;font-size:10.5px;color:var(--muted);line-height:1.5;">
        <div><strong style="color:var(--emerald);">● SynthID™:</strong> Imperceptible Frame Watermark Active</div>
        <div><strong style="color:var(--cyber-yellow);">● Lyria Beat Sync:</strong> 124 BPM Lo-Fi Architectural House</div>
      </div>
    </aside>

    <!-- CENTER: 9:16 VERTICAL SMARTPHONE VIDEO PREVIEW FRAME -->
    <section class="monitor-stage">
      <div class="phone-9-16">
        <div class="phone-notch"></div>

        <!-- Animated Scene Vector Canvas Inside Phone -->
        <div class="reel-canvas-bg" id="phone-scene-svg"></div>

        <!-- Top HUD inside Phone -->
        <div class="reel-top-hud">
          <span class="synthid-chip">🔴 LIVE REDFIN REEL • MI-772190</span>
          <span class="synthid-chip" id="phone-scene-pill">SCENE 1/4</span>
        </div>

        <!-- Lower-Third Rate Drop Banner + Voiceover Subtitles + Reg Z -->
        <div class="reel-lower-third">
          <div class="rate-drop-banner">
            <div class="rate-drop-kicker">⚡ ROCKET INTRADAY RATE-DROP ALERT</div>
            <div class="rate-drop-nums" id="phone-rate-banner">6.125% → 5.750% ($2,448/mo P&I)</div>
          </div>

          <div class="reel-caption-box" id="phone-vo-caption">
            “Huntington Woods Mid-Century Modern just dropped to $2,448/mo P&I after today’s 37.5 bps rate dip!”
          </div>

          <div class="reel-regz-micro">
            Rocket Mortgage, LLC NMLS #3030 • $525k List • 20% Down ($420k Loan) • 5.750% Rate (5.918% APR) • 360 Mos • Equal Housing Lender.
          </div>
        </div>
      </div>

      <!-- Play / Pause & Scrubber Slider -->
      <div class="transport-bar">
        <button class="btn-play" id="btn-play-toggle" onclick="window.togglePlayback()">▶</button>
        <span class="timecode-readout" id="timecode-label">00:02.4 / 00:15.0</span>
        <input type="range" id="scrubber-range" min="0" max="150" value="24" style="width:180px;accent-color:var(--cyber-yellow);cursor:pointer;" oninput="window.scrubTimeline(this.value)">
      </div>
    </section>

    <!-- RIGHT: SCENE INSPECTOR, RATE-DROP SLIDER & VOICEOVER SCRIPT GENERATOR -->
    <aside class="nle-pane">
      <div class="pane-head">
        <span>SCENE INSPECTOR & VOICEOVER GENERATOR</span>
        <span style="color:var(--track-purple);" id="live-model-pill">gemini-4-argon</span>
      </div>

      <div style="margin-bottom:14px;">
        <label class="mono" style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:5px;">
          <span>PROMO NOTE RATE DROP (6.125% → X%)</span>
          <strong style="color:var(--cyber-yellow);" id="lbl-promo-rate">5.750%</strong>
        </label>
        <input type="range" id="inp-promo-rate" min="5.25" max="6.00" step="0.125" value="5.75" style="width:100%;accent-color:var(--track-purple);" oninput="window.updateRateDropBanner()">
      </div>

      <div style="background:var(--panel-elev);border:1px solid var(--border);border-radius:8px;padding:12px;margin-bottom:12px;">
        <div class="mono" style="font-size:10px;color:var(--cyber-yellow);margin-bottom:4px;">ACTIVE VEO 3.1 CAMERA MOTION PROMPT</div>
        <div id="insp-camera-prompt" style="font-size:12px;line-height:1.45;color:#E2E8F0;">
          Fast dolly zoom toward 4-bed Mid-Century Modern home in Huntington Woods MI framed by vibrant crimson autumn maples, golden hour volumetric rays, 60fps gimbal stabilization.
        </div>
      </div>

      <div style="background:var(--panel-elev);border:1px solid var(--border);border-radius:8px;padding:12px;margin-bottom:14px;flex:1;">
        <div class="mono" style="font-size:10px;color:var(--emerald);margin-bottom:6px;">SYNCHRONIZED TTS VOICEOVER SCRIPT (0.0s – 15.0s)</div>
        <div id="insp-vo-script" style="font-size:12px;line-height:1.55;color:#F8FAFC;">
          <p style="margin-bottom:8px;"><strong>[0.0–3.5s]:</strong> “Huntington Woods Mid-Century Modern just dropped to $2,448/mo P&I after today’s 37.5 bps rate dip!”</p>
          <p style="margin-bottom:8px;"><strong>[3.5–7.5s]:</strong> “Step inside a vaulted waterfall-quartz chef’s kitchen—saving $198 every month vs last week’s 6.125% rate.”</p>
          <p style="margin-bottom:8px;"><strong>[7.5–11.5s]:</strong> “Sunlit primary suite opening onto a private cedar deck with Rocket Rate-Drop Protector included.”</p>
          <p><strong>[11.5–15.0s]:</strong> “Tap below to book your Saturday Redfin tour and lock your 1-Tap Rocket Verified Approval!”</p>
        </div>
      </div>

      <button class="btn-export-reel" style="width:100%;padding:11px;" onclick="window.runLiveVertexAI()">
        [⚡ Regenerate Veo 3.1 Storyboard & Voiceover via Vertex AI]
      </button>
    </aside>
  </div>

  <!-- BOTTOM: 4-TRACK MULTI-SCENE TIMELINE SCRUBBER -->
  <footer class="timeline-dock">
    <div class="timeline-ruler">
      <span>00:00.0</span>
      <span>00:03.5</span>
      <span>00:07.5</span>
      <span>00:11.5</span>
      <span>00:15.0 (END)</span>
    </div>

    <div class="tracks-wrapper">
      <div class="playhead-line" id="timeline-playhead">
        <div class="playhead-cap"></div>
      </div>

      <!-- Track 1: Veo 3.1 Video Track -->
      <div class="track-row">
        <div class="track-label" style="border-left-color:var(--track-purple);">🎥 VEO 3.1 VIDEO</div>
        <div class="track-lane">
          <div class="track-block" style="background:rgba(168,85,247,0.3);border:1px solid #A855F7;" onclick="window.selectScene(0)">S1: Autumn Exterior Dolly</div>
          <div class="track-block" style="background:rgba(168,85,247,0.3);border:1px solid #A855F7;" onclick="window.selectScene(1)">S2: Quartz Chef Kitchen Pan</div>
          <div class="track-block" style="background:rgba(168,85,247,0.3);border:1px solid #A855F7;" onclick="window.selectScene(2)">S3: Primary Suite & Deck</div>
          <div class="track-block" style="background:rgba(168,85,247,0.3);border:1px solid #A855F7;" onclick="window.selectScene(3)">S4: Redfin+Rocket End Card</div>
        </div>
      </div>

      <!-- Track 2: Gempix-2 Lower-Third Overlays -->
      <div class="track-row">
        <div class="track-label" style="border-left-color:var(--cyber-yellow);">✨ GEMPIX-2 OVERLAYS</div>
        <div class="track-lane">
          <div class="track-block" style="background:rgba(250,204,21,0.18);border:1px solid var(--cyber-yellow);color:#FEF08A;">Rate Drop: 6.125% → 5.75%</div>
          <div class="track-block" style="background:rgba(250,204,21,0.18);border:1px solid var(--cyber-yellow);color:#FEF08A;">Badge: $2,448/mo P&I (-$198/m)</div>
          <div class="track-block" style="background:rgba(250,204,21,0.18);border:1px solid var(--cyber-yellow);color:#FEF08A;">Rate-Drop Protector Shield</div>
          <div class="track-block" style="background:rgba(250,204,21,0.18);border:1px solid var(--cyber-yellow);color:#FEF08A;">1-Tap Tour + Pre-Approval CTA</div>
        </div>
      </div>

      <!-- Track 3: TTS Voiceover & Lyria Beat -->
      <div class="track-row">
        <div class="track-label" style="border-left-color:var(--cyan);">🎙️ TTS VOICEOVER</div>
        <div class="track-lane">
          <div class="track-block" style="background:rgba(6,182,212,0.2);border:1px solid var(--cyan);color:#A5F3FC;">VO_Hook_37bps_Drop.wav</div>
          <div class="track-block" style="background:rgba(6,182,212,0.2);border:1px solid var(--cyan);color:#A5F3FC;">VO_Kitchen_Payment.wav</div>
          <div class="track-block" style="background:rgba(6,182,212,0.2);border:1px solid var(--cyan);color:#A5F3FC;">VO_Suite_Protector.wav</div>
          <div class="track-block" style="background:rgba(6,182,212,0.2);border:1px solid var(--cyan);color:#A5F3FC;">VO_Book_Redfin_CTA.wav</div>
        </div>
      </div>

      <!-- Track 4: TILA Reg Z Legal Disclaimer -->
      <div class="track-row" style="margin-bottom:0;">
        <div class="track-label" style="border-left-color:var(--emerald);">⚖️ TILA REG Z LEGAL</div>
        <div class="track-lane" style="grid-template-columns:1fr;">
          <div class="track-block" style="background:rgba(16,185,129,0.18);border:1px solid var(--emerald);color:#6EE7B7;text-align:center;">
            LOCKED CONTINUOUS OVERLAY (0.0s–15.0s): 12 CFR § 1026.24 APR (5.918% APR) + Down Payment + NMLS #3030 Equal Housing Lender
          </div>
        </div>
      </div>
    </div>
  </footer>

  <script>
    const SCENES = [
      {{
        idx: 0,
        timecode: "00:01.8",
        scrubVal: 18,
        cameraPrompt: "Fast dolly zoom toward 4-bed Mid-Century Modern home in Huntington Woods MI framed by vibrant crimson autumn maples, golden hour volumetric rays, 60fps gimbal stabilization.",
        caption: "“Huntington Woods Mid-Century Modern just dropped to $2,448/mo P&I after today’s 37.5 bps rate dip!”",
        svg: `<svg viewBox="0 0 300 520" width="100%" height="100%" preserveAspectRatio="none">
          <defs><linearGradient id="sky1" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#1E1B4B"/><stop offset="60%" stop-color="#7C2D12"/><stop offset="100%" stop-color="#1F2937"/></linearGradient></defs>
          <rect width="300" height="520" fill="url(#sky1)"/>
          <circle cx="230" cy="110" r="42" fill="#FACC15" opacity="0.75"/>
          <!-- Mid Century Roofline -->
          <polygon points="20,250 180,185 285,235 20,265" fill="#27272A"/>
          <rect x="35" y="245" width="230" height="105" fill="#451A03" stroke="#FDE68A" stroke-width="1.5"/>
          <rect x="55" y="260" width="85" height="65" fill="#FDE047" opacity="0.75"/>
          <rect x="160" y="260" width="85" height="65" fill="#FDE047" opacity="0.65"/>
          <!-- Autumn Maple Foliage -->
          <circle cx="45" cy="195" r="45" fill="#DC2626" opacity="0.85"/>
          <circle cx="80" cy="175" r="35" fill="#EA580C" opacity="0.85"/>
        </svg>`
      }},
      {{
        idx: 1,
        timecode: "00:05.2",
        scrubVal: 52,
        cameraPrompt: "Smooth orbital pan across vaulted chef's kitchen with waterfall Calacatta quartz island, walnut cabinetry, and brushed brass pendants.",
        caption: "“Step inside a vaulted waterfall-quartz chef’s kitchen—saving $198 every month vs last week’s 6.125% rate.”",
        svg: `<svg viewBox="0 0 300 520" width="100%" height="100%" preserveAspectRatio="none">
          <rect width="300" height="520" fill="#27201C"/>
          <rect x="20" y="90" width="260" height="180" fill="#452719"/>
          <!-- Quartz Island -->
          <polygon points="30,290 270,290 290,380 10,380" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="2"/>
          <!-- Brass Pendants -->
          <line x1="100" y1="40" x2="100" y2="170" stroke="#FACC15" stroke-width="2"/>
          <circle cx="100" cy="175" r="14" fill="#FEF08A"/>
          <line x1="200" y1="40" x2="200" y2="170" stroke="#FACC15" stroke-width="2"/>
          <circle cx="200" cy="175" r="14" fill="#FEF08A"/>
        </svg>`
      }},
      {{
        idx: 2,
        timecode: "00:09.4",
        scrubVal: 94,
        cameraPrompt: "Gimbal push through floor-to-ceiling glass sliders from sunlit primary suite onto private backyard cedar deck with firepit.",
        caption: "“Sunlit primary suite opening onto a private cedar deck with Rocket Rate-Drop Protector included.”",
        svg: `<svg viewBox="0 0 300 520" width="100%" height="100%" preserveAspectRatio="none">
          <rect width="300" height="520" fill="#0F172A"/>
          <rect x="25" y="100" width="250" height="220" fill="#065F46" opacity="0.65" stroke="#FDE68A" stroke-width="3"/>
          <polygon points="0,320 300,320 300,520 0,520" fill="#78350F"/>
          <circle cx="150" cy="365" r="26" fill="#EA580C"/>
          <circle cx="150" cy="365" r="14" fill="#FACC15"/>
        </svg>`
      }},
      {{
        idx: 3,
        timecode: "00:13.6",
        scrubVal: 136,
        cameraPrompt: "Gempix-2 high-contrast end card with Redfin Saturday 11 AM Tour badge + Rocket 1-Tap Verified Approval shield.",
        caption: "“Tap below to book your Saturday Redfin tour and lock your 1-Tap Rocket Verified Approval!”",
        svg: `<svg viewBox="0 0 300 520" width="100%" height="100%" preserveAspectRatio="none">
          <rect width="300" height="520" fill="#18091E"/>
          <rect x="28" y="125" width="244" height="145" rx="14" fill="#E11D48" stroke="#FACC15" stroke-width="2"/>
          <text x="150" y="175" text-anchor="middle" fill="#FFF" font-family="Archivo" font-size="16" font-weight="bold">REDFIN × ROCKET</text>
          <text x="150" y="205" text-anchor="middle" fill="#FEF08A" font-family="JetBrains Mono" font-size="12" font-weight="bold">1-TAP TOUR + PRE-APPROVAL</text>
          <text x="150" y="235" text-anchor="middle" fill="#FFF" font-family="JetBrains Mono" font-size="11">$3,500 BUY+BORROW CREDIT</text>
        </svg>`
      }}
    ];

    window.activeSceneIdx = 0;
    window.playingTimer = null;

    window.selectScene = function(idx) {{
      window.activeSceneIdx = idx;
      const sc = SCENES[idx] || SCENES[0];
      document.querySelectorAll('.clip-card').forEach((el, i) => {{
        el.classList.toggle('active', i === idx);
      }});
      document.getElementById('phone-scene-svg').innerHTML = sc.svg;
      document.getElementById('phone-scene-pill').innerText = `SCENE ${{idx + 1}}/4`;
      document.getElementById('phone-vo-caption').innerText = sc.caption;
      document.getElementById('insp-camera-prompt').innerText = sc.cameraPrompt;
      document.getElementById('scrubber-range').value = sc.scrubVal;
      document.getElementById('timecode-label').innerText = `${{sc.timecode}} / 00:15.0`;
      const pct = (sc.scrubVal / 150) * 76;
      document.getElementById('timeline-playhead').style.left = `calc(170px + ${{pct}}%)`;
    }};

    window.scrubTimeline = function(val) {{
      const v = parseInt(val || 0, 10);
      const sec = (v / 10).toFixed(1).padStart(4, '0');
      document.getElementById('timecode-label').innerText = `00:${{sec}} / 00:15.0`;
      const pct = (v / 150) * 76;
      document.getElementById('timeline-playhead').style.left = `calc(170px + ${{pct}}%)`;
      const sceneIdx = v < 35 ? 0 : (v < 75 ? 1 : (v < 115 ? 2 : 3));
      if (sceneIdx !== window.activeSceneIdx) {{
        window.selectScene(sceneIdx);
      }}
    }};

    window.togglePlayback = function() {{
      const btn = document.getElementById('btn-play-toggle');
      if (window.playingTimer) {{
        clearInterval(window.playingTimer);
        window.playingTimer = null;
        if (btn) btn.innerText = '▶';
        return;
      }}
      if (btn) btn.innerText = '⏸';
      window.playingTimer = setInterval(() => {{
        const rng = document.getElementById('scrubber-range');
        let next = parseInt(rng.value || 0, 10) + 5;
        if (next > 150) next = 0;
        rng.value = next;
        window.scrubTimeline(next);
      }}, 250);
    }};

    window.updateRateDropBanner = function() {{
      const rate = parseFloat(document.getElementById('inp-promo-rate').value || 5.75);
      document.getElementById('lbl-promo-rate').innerText = rate.toFixed(3) + '%';
      const loan = 420000;
      const r = (rate / 100) / 12;
      const pi = Math.round(loan * (r * Math.pow(1 + r, 360)) / (Math.pow(1 + r, 360) - 1));
      document.getElementById('phone-rate-banner').innerText = `6.125% → ${{rate.toFixed(3)}}% ($${{pi.toLocaleString()}}/mo P&I)`;
    }};

    window.runLiveVertexAI = async function() {{
      const btn = document.getElementById('btn-produce-reel');
      const orig = btn ? btn.innerText : '';
      if (btn) {{
        btn.innerText = '⏳ Veo 3.1 + Vertex AI Producing...';
        btn.disabled = true;
      }}
      const rate = parseFloat(document.getElementById('inp-promo-rate').value || 5.75);
      const scenarioEl = document.getElementById('scenario-input');
      const promptText = scenarioEl && scenarioEl.value
        ? scenarioEl.value
        : `Produce a 15-second 9:16 vertical Reel for Huntington Woods MI ($525,000) featuring a rate drop from 6.125% to ${{rate.toFixed(3)}}% and TILA Reg Z compliance.`;

      try {{
        const resp = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '4.4',
            model: window.getSelectedModel(),
            user_input: promptText,
            params: {{ duration_sec: 15, scenes: 4, list_price: 525000, promo_rate: rate }}
          }})
        }});
        const res = await resp.json();
        if (res && res.ok) {{
          const sd = res.structured_data || {{}};
          if (Array.isArray(sd.storyboard_frames) && sd.storyboard_frames.length > 0) {{
            document.getElementById('insp-vo-script').innerHTML = sd.storyboard_frames.map(f =>
              `<p style="margin-bottom:8px;"><strong>[${{f.timecode || 'SCENE'}}]:</strong> “${{f.voiceover_line || f.on_screen_typography || ''}}”</p>`
            ).join('');
            const first = sd.storyboard_frames[0];
            if (first.voiceover_line) {{
              document.getElementById('phone-vo-caption').innerText = `“${{first.voiceover_line}}”`;
            }}
            if (first.camera_motion) {{
              document.getElementById('insp-camera-prompt').innerText = first.camera_motion;
            }}
          }} else if (res.output) {{
            document.getElementById('insp-vo-script').innerHTML = `<p>${{res.output}}</p>`;
          }}
        }}
      }} catch (e) {{
        console.error(e);
      }} finally {{
        if (btn) {{
          btn.innerText = orig;
          btn.disabled = false;
        }}
      }}
    }};

    document.addEventListener('DOMContentLoaded', () => {{
      window.selectScene(0);
      window.updateRateDropBanner();
    }});
  </script>

  {floating_drawer}
</body>
</html>"""
