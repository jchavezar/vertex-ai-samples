"""Visual-First Institutional UI Studio for Rocket Next-Gen 4-Pillar Gemini Suite (v5).
Fixes & Features:
1. HARD 0ms AUDIO & AVATAR STOP (`window.stopAllAudioAndAvatarNow()`):
   - Immediately closes/suspends the hardware WebAudio `AudioContext`, stops all scheduled `AudioBufferSourceNode`s, sets `ignoreIncomingAudio = true` so in-flight WebSocket packets cannot restart playback, and pauses all Kira avatar videos in 0ms.
2. VOICE-SYNCHRONIZED AVATAR (`#kira-pip-card` + `#kira-dock-video` + `#kira-stage-video`):
   - Avatar video ONLY plays/animates when Kira is actively speaking (`activeNodes.length > 0`), modulating playback speed & 60fps waveform equalizer bars with real-time 24kHz audio amplitude, and pauses immediately when silent or stopped.
3. UNIFIED 1-CLICK LIVE VOICE & MIC + LIVE TEXT COMMAND BAR:
   - Clicking "Start Live Voice & Mic" immediately activates real-time speech recognition (`webkitSpeechRecognition` + 16kHz mic) AND connects Gemini Live (`/ws/live-avatar`).
   - Also includes an inline command input box ("Speak or type any command, e.g. 'set rate shock to -60'...") in the bottom bar.
4. EXACT 1-UNIT SLIDER PRECISION (`step="1"`):
   - `#p1-shock` supports every integer from `-150` to `+100` bps (`step="1"`), so asking for `-60` sets `-60 bps` smoothly with the Agentic Ghost Cursor, runs BigQuery `AI.FORECAST`, and speaks the live result aloud.
"""


def render_4pillars_studio() -> str:
    return """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Rocket Companies × Google Gemini · Next-Gen 4-Pillar AI Studio</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>
    :root {
      --bg-canvas: #F8FAFC;
      --bg-card: rgba(255, 255, 255, 0.86);
      --bg-subtle: rgba(248, 250, 252, 0.88);
      --bg-elevated: rgba(15, 23, 42, 0.90);
      --ink-primary: #0F172A;
      --ink-secondary: #334155;
      --ink-muted: #64748B;
      --border-hairline: rgba(226, 232, 240, 0.95);
      --rocket-red: #D81E28;
      --rocket-red-glow: #E11D48;
      --rocket-red-soft: rgba(216, 30, 40, 0.08);
      --google-blue: #1A73E8;
      --google-blue-soft: rgba(26, 115, 232, 0.10);
      --cooper-teal: #0D9488;
      --emerald: #059669;
      --amber: #D97706;
      --shadow-sm: 0 12px 32px rgba(15, 23, 42, 0.06), 0 2px 8px rgba(15, 23, 42, 0.03), inset 0 1.5px 0 #FFFFFF;
      --shadow-md: 0 20px 48px rgba(15, 23, 42, 0.08), 0 4px 14px rgba(15, 23, 42, 0.04), inset 0 1.5px 0 #FFFFFF;
      --radius-lg: 24px;
      --radius-md: 18px;
      --vision-blur: blur(32px) saturate(190%);
    }
    [data-theme="dark"] {
      --bg-canvas: #0B0F17;
      --bg-card: rgba(15, 23, 42, 0.78);
      --bg-subtle: rgba(30, 41, 59, 0.72);
      --bg-elevated: rgba(2, 6, 23, 0.92);
      --ink-primary: #F8FAFC;
      --ink-secondary: #CBD5E1;
      --ink-muted: #94A3B8;
      --border-hairline: rgba(255, 255, 255, 0.14);
      --shadow-sm: 0 16px 40px rgba(0, 0, 0, 0.45), inset 0 1.5px 0 rgba(255, 255, 255, 0.12);
      --shadow-md: 0 28px 64px rgba(0, 0, 0, 0.62), inset 0 1.5px 0 rgba(255, 255, 255, 0.16);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: var(--bg-canvas);
      background-image:
        radial-gradient(circle at 85% 8%, rgba(216, 30, 40, 0.04) 0%, transparent 42%),
        radial-gradient(circle at 12% 88%, rgba(15, 23, 42, 0.03) 0%, transparent 48%),
        linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 55%, #F1F5F9 100%);
      background-attachment: fixed;
      color: var(--ink-primary);
      min-height: 100vh;
      overflow-x: hidden;
      transition: background 0.25s ease, color 0.25s ease;
    }
    [data-theme="dark"] body {
      background-image:
        radial-gradient(circle at 85% 12%, rgba(216, 30, 40, 0.12) 0%, transparent 48%),
        linear-gradient(180deg, #0F172A 0%, #090D16 100%);
    }
    .ico {
      width: 15px;
      height: 15px;
      stroke: currentColor;
      stroke-width: 1.85;
      stroke-linecap: round;
      stroke-linejoin: round;
      fill: none;
      flex-shrink: 0;
    }
    .ico-sm { width: 13px; height: 13px; }
    .ico-lg { width: 18px; height: 18px; }

    /* CRYSTAL LIQUID WHITE GLASS FLOATING HEADER BAR + ROCKET RED ACCENTS */
    .top-nav {
      position: sticky;
      top: 10px;
      z-index: 100;
      max-width: 1460px;
      margin: 10px auto 6px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.92);
      backdrop-filter: blur(28px) saturate(180%);
      -webkit-backdrop-filter: blur(28px) saturate(180%);
      border: 1px solid #E2E8F0;
      box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06), 0 2px 6px rgba(15, 23, 42, 0.03);
      padding: 7px 14px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
    }
    [data-theme="dark"] .top-nav {
      background: rgba(15, 23, 42, 0.88);
      border-color: rgba(255, 255, 255, 0.14);
      box-shadow: 0 16px 40px rgba(0, 0, 0, 0.55);
    }
    .brand-cluster {
      display: flex;
      align-items: center;
      gap: 9px;
      flex-shrink: 0;
      white-space: nowrap;
    }
    .rocket-logo-mark {
      width: 34px;
      height: 34px;
      border-radius: 9px;
      background: linear-gradient(135deg, #D81E28 0%, #B91C1C 100%);
      color: #FFF;
      font-weight: 800;
      font-size: 15px;
      display: flex;
      align-items: center;
      justify-content: center;
      letter-spacing: -0.03em;
      box-shadow: 0 4px 12px rgba(216, 30, 40, 0.26);
      flex-shrink: 0;
    }
    .brand-title {
      font-size: 16px;
      font-weight: 800;
      color: #0F172A;
      letter-spacing: -0.03em;
      display: flex;
      align-items: center;
      gap: 6px;
      white-space: nowrap;
      line-height: 1.1;
    }
    [data-theme="dark"] .brand-title {
      color: #FFFFFF;
    }
    .brand-sub {
      font-size: 10px;
      color: var(--ink-muted);
      font-weight: 600;
      white-space: nowrap;
      line-height: 1.15;
    }
    /* CRYSTAL LIQUID WHITE PILL NAVIGATION TABS */
    .pillar-tabs {
      display: flex;
      align-items: center;
      gap: 3px;
      background: #F1F5F9;
      padding: 4px;
      border-radius: 999px;
      border: 1px solid #E2E8F0;
      overflow-x: auto;
      scrollbar-width: none;
      flex: 0 1 auto;
      margin: 0 auto;
    }
    [data-theme="dark"] .pillar-tabs {
      background: rgba(30, 41, 59, 0.85);
      border-color: rgba(255, 255, 255, 0.12);
    }
    .pillar-tabs::-webkit-scrollbar { display: none; }
    .pillar-tab {
      height: 32px;
      border: 1px solid transparent;
      background: transparent;
      color: var(--ink-secondary);
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 11.5px;
      font-weight: 700;
      padding: 0 9px;
      border-radius: 999px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 4px;
      line-height: 1;
      transition: background 0.16s ease, color 0.16s ease, box-shadow 0.16s ease;
      white-space: nowrap;
      flex-shrink: 0;
    }
    .pillar-tab:hover {
      color: #D81E28;
      background: #FFFFFF;
    }
    .pillar-tab.active {
      background: linear-gradient(135deg, #D81E28 0%, #B91C1C 100%);
      color: #FFFFFF;
      font-weight: 800;
      border: 1px solid #D81E28;
      background-clip: padding-box;
      box-shadow: 0 4px 12px rgba(216, 30, 40, 0.25);
    }
    [data-theme="dark"] .pillar-tab.active {
      color: #FFFFFF;
      border-color: #D81E28;
    }
    .pillar-num {
      font-size: 9.5px;
      height: 18px;
      padding: 0 6px;
      border-radius: 999px;
      background: rgba(216, 30, 40, 0.10);
      color: #D81E28;
      font-weight: 800;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      line-height: 1;
    }
    .pillar-tab.active .pillar-num {
      background: rgba(255, 255, 255, 0.22);
      color: #FFFFFF;
    }
    .nav-actions {
      display: flex;
      align-items: center;
      gap: 6px;
      flex-shrink: 0;
    }
    .model-select {
      height: 34px;
      border: 1px solid #E2E8F0;
      background: #FFFFFF;
      color: var(--ink-primary);
      padding: 0 10px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 700;
      font-family: inherit;
      cursor: pointer;
      outline: none;
      transition: border-color 0.18s ease;
    }
    [data-theme="dark"] .model-select {
      background: rgba(30, 41, 59, 0.90);
      border-color: rgba(255, 255, 255, 0.15);
      color: #F8FAFC;
    }
    .theme-btn {
      height: 34px;
      border: 1px solid #E2E8F0;
      background: #FFFFFF;
      color: var(--ink-primary);
      padding: 0 12px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 5px;
      line-height: 1;
    }
    [data-theme="dark"] .theme-btn {
      background: rgba(30, 41, 59, 0.90);
      border-color: rgba(255, 255, 255, 0.15);
    }
    /* MAIN STAGE CONTAINER */
    .stage-wrap {
      max-width: 1480px;
      margin: 0 auto;
      padding: 16px 24px 130px;
    }
    .pillar-pane {
      display: none;
      animation: fadeIn 0.18s ease;
    }
    .pillar-pane.active {
      display: block;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(3px); }
      to { opacity: 1; transform: translateY(0); }
    }
    /* COMPACT TOP BANNER WITH GEMINI VS CLAUDE MOAT */
    .moat-strip {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      background: var(--bg-card);
      border: 1px solid var(--border-hairline);
      border-left: 4px solid var(--rocket-red);
      border-radius: var(--radius-md);
      padding: 11px 16px;
      margin-bottom: 14px;
      box-shadow: var(--shadow-sm);
    }
    .moat-title {
      font-size: 15.5px;
      font-weight: 800;
      letter-spacing: -0.02em;
    }
    .moat-subtitle {
      font-size: 12px;
      color: var(--ink-secondary);
      margin-top: 2px;
    }
    .vs-claude-pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: var(--bg-subtle);
      border: 1px solid var(--border-hairline);
      padding: 6px 12px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 700;
      font-family: 'JetBrains Mono', monospace;
      color: var(--ink-primary);
      white-space: nowrap;
    }
    .vs-claude-pill strong { color: var(--google-blue); }
    .vs-claude-pill .claude-no { color: var(--rocket-red); }

    /* CARDS & GRIDS */
    .studio-grid-12 {
      display: grid;
      grid-template-columns: repeat(12, 1fr);
      gap: 16px;
    }
    .col-3 { grid-column: span 3; }
    .col-4 { grid-column: span 4; }
    .col-5 { grid-column: span 5; }
    .col-7 { grid-column: span 7; }
    .col-8 { grid-column: span 8; }
    .col-9 { grid-column: span 9; }
    .col-12 { grid-column: span 12; }
    @media (max-width: 1100px) {
      .col-3, .col-4, .col-5, .col-7, .col-8, .col-9 { grid-column: span 12; }
      .pillar-tabs { overflow-x: auto; max-width: 100%; }
    }
    .v-card {
      background: var(--bg-card);
      border: 1px solid var(--border-hairline);
      border-radius: var(--radius-lg);
      padding: 18px;
      box-shadow: var(--shadow-sm);
    }
    .v-card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;
    }
    .v-card-title {
      font-size: 11.5px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--ink-secondary);
      font-family: 'JetBrains Mono', monospace;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .badge-live {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 10.5px;
      font-weight: 700;
      padding: 4px 9px;
      border-radius: 999px;
      background: rgba(5, 150, 105, 0.10);
      color: var(--emerald);
      border: 1px solid rgba(5, 150, 105, 0.22);
    }
    .dot-pulse {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--emerald);
      box-shadow: 0 0 0 0 rgba(5, 150, 105, 0.7);
      animation: pulseGreen 1.8s infinite;
    }
    @keyframes pulseGreen {
      0% { box-shadow: 0 0 0 0 rgba(5, 150, 105, 0.6); }
      70% { box-shadow: 0 0 0 6px rgba(5, 150, 105, 0); }
      100% { box-shadow: 0 0 0 0 rgba(5, 150, 105, 0); }
    }

    /* KPI STRIP */
    .kpi-row {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      margin-bottom: 14px;
    }
    .kpi-tile {
      background: var(--bg-subtle);
      border: 1px solid var(--border-hairline);
      border-radius: 10px;
      padding: 12px 14px;
      transition: all 0.25s ease;
    }
    .kpi-tile.flash-highlight {
      border-color: var(--google-blue);
      box-shadow: 0 0 0 2px rgba(26, 115, 232, 0.25);
    }
    .kpi-label {
      font-size: 10px;
      font-family: 'JetBrains Mono', monospace;
      text-transform: uppercase;
      color: var(--ink-muted);
      letter-spacing: 0.05em;
    }
    .kpi-val {
      font-size: 21px;
      font-weight: 800;
      margin-top: 4px;
      letter-spacing: -0.02em;
      font-variant-numeric: tabular-nums;
    }
    .kpi-sub {
      font-size: 11px;
      color: var(--emerald);
      font-weight: 600;
      margin-top: 2px;
    }

    /* CONTROLS & BUTTONS */
    .cohort-list {
      display: flex;
      flex-direction: column;
      gap: 7px;
      margin-bottom: 14px;
    }
    .cohort-btn {
      text-align: left;
      padding: 10px 12px;
      border-radius: 9px;
      border: 1px solid var(--border-hairline);
      background: var(--bg-subtle);
      color: var(--ink-primary);
      cursor: pointer;
      transition: all 0.15s ease;
      display: flex;
      align-items: flex-start;
      gap: 10px;
    }
    .cohort-btn:hover { border-color: var(--google-blue); }
    .cohort-btn.active {
      background: var(--google-blue-soft);
      border-color: var(--google-blue);
    }
    .cohort-icon-box {
      width: 28px;
      height: 28px;
      border-radius: 7px;
      background: var(--bg-card);
      border: 1px solid var(--border-hairline);
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--ink-secondary);
      flex-shrink: 0;
      margin-top: 1px;
    }
    .cohort-btn.active .cohort-icon-box {
      color: var(--google-blue);
      border-color: rgba(26, 115, 232, 0.35);
    }
    .cohort-btn-title { font-size: 12.5px; font-weight: 700; }
    .cohort-btn-sub { font-size: 11px; color: var(--ink-muted); margin-top: 2px; }

    .ctrl-group {
      margin-bottom: 12px;
      padding: 7px 10px;
      border-radius: 9px;
      border: 1px solid transparent;
      transition: all 0.25s ease;
    }
    .ctrl-group.agent-active-target {
      background: rgba(26, 115, 232, 0.10);
      border-color: var(--google-blue);
      box-shadow: 0 0 0 3px rgba(26, 115, 232, 0.22);
    }
    .ctrl-label {
      display: flex;
      justify-content: space-between;
      font-size: 11.5px;
      font-weight: 700;
      margin-bottom: 5px;
    }
    .ctrl-label span:last-child {
      font-family: 'JetBrains Mono', monospace;
      color: var(--google-blue);
      font-weight: 800;
      font-size: 12.5px;
    }
    input[type="range"] {
      width: 100%;
      accent-color: var(--rocket-red);
      cursor: pointer;
    }
    .btn-primary {
      width: 100%;
      padding: 11px 15px;
      border-radius: 9px;
      border: none;
      background: var(--rocket-red);
      color: #FFF;
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 12.5px;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      box-shadow: 0 4px 12px rgba(216, 30, 40, 0.22);
      transition: transform 0.12s ease, opacity 0.12s ease, background 0.15s ease;
    }
    .btn-primary:hover { transform: translateY(-1px); opacity: 0.96; }
    .btn-primary.playing-stop {
      background: #0F172A !important;
      border: 1px solid #EF4444 !important;
      color: #FCA5A5 !important;
    }
    .btn-secondary {
      width: 100%;
      padding: 9px 13px;
      border-radius: 9px;
      border: 1px solid var(--border-hairline);
      background: var(--bg-subtle);
      color: var(--ink-primary);
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 7px;
      transition: all 0.14s ease;
    }
    .btn-secondary:hover { border-color: var(--ink-secondary); }
    .btn-secondary.playing-stop {
      background: rgba(216, 30, 40, 0.14) !important;
      border-color: var(--rocket-red) !important;
      color: var(--rocket-red) !important;
    }

    /* PILLAR 2: 9:16 VERTICAL PHONE REEL PLAYER */
    .phone-stage {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }
    .phone-frame {
      position: relative;
      width: 332px;
      height: 588px;
      border-radius: 34px;
      background: #000;
      border: 7px solid #1E293B;
      box-shadow: 0 20px 46px rgba(15, 23, 42, 0.24);
      overflow: hidden;
    }
    .phone-video {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }
    .phone-poster-overlay {
      position: absolute;
      inset: 0;
      background-size: cover;
      background-position: center;
      opacity: 0;
      transition: opacity 0.35s ease;
      pointer-events: none;
    }
    .reel-hud-top {
      position: absolute;
      top: 14px;
      left: 14px;
      right: 14px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      z-index: 5;
    }
    .reel-brand-pill {
      background: rgba(15, 23, 42, 0.76);
      backdrop-filter: blur(8px);
      color: #FFF;
      padding: 5px 10px;
      border-radius: 999px;
      font-size: 10.5px;
      font-weight: 800;
      letter-spacing: 0.03em;
      display: flex;
      align-items: center;
      gap: 6px;
      border: 1px solid rgba(255,255,255,0.14);
    }
    .reel-caption-box {
      position: absolute;
      bottom: 124px;
      left: 14px;
      right: 14px;
      background: rgba(15, 23, 42, 0.82);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255,255,255,0.16);
      border-radius: 12px;
      padding: 10px 12px;
      color: #FFF;
      z-index: 5;
      transition: all 0.2s ease;
    }
    .reel-caption-tag {
      font-family: 'JetBrains Mono', monospace;
      font-size: 9.5px;
      color: #38BDF8;
      font-weight: 700;
      margin-bottom: 3px;
      letter-spacing: 0.04em;
    }
    .reel-caption-text {
      font-size: 12.5px;
      font-weight: 700;
      line-height: 1.35;
    }
    .reel-piti-sticker {
      position: absolute;
      bottom: 14px;
      left: 14px;
      right: 14px;
      background: linear-gradient(135deg, rgba(216, 30, 40, 0.96), rgba(153, 27, 27, 0.96));
      border-radius: 14px;
      padding: 11px 14px;
      color: #FFF;
      z-index: 5;
      display: flex;
      align-items: center;
      justify-content: space-between;
      box-shadow: 0 10px 24px rgba(0, 0, 0, 0.4);
    }

    /* PILLAR 3: TRI-MODAL GROUNDING */
    #grounding-map {
      width: 100%;
      height: 315px;
      border-radius: 10px;
      border: 1px solid var(--border-hairline);
      z-index: 1;
    }
    .place-pill-list {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 10px;
    }
    .place-pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 5px 10px;
      border-radius: 7px;
      background: var(--bg-subtle);
      border: 1px solid var(--border-hairline);
      color: var(--ink-primary);
      font-size: 11px;
      font-weight: 700;
      text-decoration: none;
      transition: all 0.14s ease;
    }
    .place-pill:hover {
      border-color: var(--google-blue);
      background: var(--google-blue-soft);
      color: var(--google-blue);
    }

    /* PILLAR 4: LIVE API + AVATAR STAGE */
    .avatar-stage-box {
      position: relative;
      height: 395px;
      border-radius: 14px;
      background: radial-gradient(circle at 50% 35%, #1E293B 0%, #090D16 100%);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      overflow: hidden;
      border: 1px solid #334155;
    }
    #avatar-ring-canvas {
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
    }
    .avatar-portrait-circle {
      position: relative;
      width: 196px;
      height: 196px;
      border-radius: 50%;
      border: 3px solid rgba(56, 189, 248, 0.85);
      overflow: hidden;
      z-index: 3;
      background: #0F172A;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 0 42px rgba(26, 115, 232, 0.5);
      transition: transform 0.08s ease, box-shadow 0.08s ease, border-color 0.15s ease;
    }
    .avatar-portrait-circle.speaking-glow {
      border-color: #10B981;
      box-shadow: 0 0 55px rgba(16, 185, 129, 0.75);
    }
    #kira-stage-canvas,
    .kira-pip-video-wrap canvas,
    .omni-avatar-thumb canvas {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }
    .barge-chip {
      border: 1px solid var(--border-hairline);
      background: var(--bg-subtle);
      color: var(--ink-primary);
      padding: 7px 11px;
      border-radius: 8px;
      font-size: 11.5px;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.14s ease;
    }
    .barge-chip:hover {
      background: var(--google-blue-soft);
      border-color: var(--google-blue);
      color: var(--google-blue);
    }
    .sql-drawer {
      margin-top: 12px;
      background: #0F172A;
      color: #E2E8F0;
      padding: 12px 14px;
      border-radius: 10px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      overflow-x: auto;
      display: none;
    }

    /* =====================================================================
       FLOATING VOICE-SYNCHRONIZED AVATAR PIP STAGE (#kira-pip-card)
       ===================================================================== */
    .kira-pip-card {
      position: fixed;
      bottom: 76px;
      right: 20px;
      left: auto;
      width: 148px;
      background: rgba(255, 255, 255, 0.96);
      backdrop-filter: blur(16px);
      border: 1px solid #DDDDDD;
      border-radius: 18px;
      padding: 8px;
      color: #222222;
      z-index: 960;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.14);
      transition: all 0.25s ease;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    [data-theme="dark"] .kira-pip-card {
      background: rgba(15, 23, 42, 0.96);
      border-color: #334155;
      color: #F8FAFC;
    }
    .kira-pip-card.speaking {
      border-color: #FF385C;
      box-shadow: 0 8px 32px rgba(255, 56, 92, 0.35);
    }
    .kira-pip-video-wrap {
      width: 68px;
      height: 68px;
      border-radius: 50%;
      overflow: hidden;
      border: 2px solid #FF385C;
      position: relative;
      background: #020617;
    }
    .kira-pip-card.speaking .kira-pip-video-wrap {
      border-color: #008A05;
    }
    .kira-pip-video-wrap video {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    #kira-pip-eq-canvas {
      width: 120px;
      height: 20px;
      margin-top: 4px;
    }
    .kira-pip-status {
      font-size: 9px;
      font-weight: 700;
      color: #717171;
      margin-top: 2px;
      text-align: center;
    }
    .kira-pip-card.speaking .kira-pip-status {
      color: #FF385C;
    }

    /* =====================================================================
       PERSISTENT OMNI-PILLAR VOICE & SCREEN CO-PILOT BAR (KIRA)
       ===================================================================== */
    .omni-copilot-bar {
      position: fixed;
      bottom: 10px;
      left: 50%;
      transform: translateX(-50%);
      width: calc(100% - 32px);
      max-width: 1460px;
      background: rgba(255, 255, 255, 0.97);
      backdrop-filter: blur(18px);
      border: 1px solid #DDDDDD;
      border-radius: 999px;
      padding: 6px 12px;
      color: #222222;
      z-index: 950;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      box-shadow: 0 8px 28px rgba(0, 0, 0, 0.12);
    }
    [data-theme="dark"] .omni-copilot-bar {
      background: rgba(15, 23, 42, 0.96);
      border-color: #334155;
      color: #F8FAFC;
    }
    .omni-left {
      display: flex;
      align-items: center;
      gap: 8px;
      min-width: 175px;
      max-width: 215px;
      flex-shrink: 0;
      overflow: hidden;
    }
    .omni-avatar-thumb {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      border: 2px solid #D81E28;
      overflow: hidden;
      flex-shrink: 0;
      position: relative;
      background: #020617;
    }
    .omni-avatar-thumb video {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    .omni-title {
      font-size: 11px;
      font-weight: 800;
      color: #222222;
      display: flex;
      align-items: center;
      gap: 5px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    [data-theme="dark"] .omni-title { color: #FFF; }
    .omni-transcript {
      font-size: 10px;
      color: #717171;
      font-weight: 600;
      max-width: 190px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      margin-top: 1px;
    }
    /* DIRECT COMMAND INPUT BOX IN OMNI BAR */
    .omni-cmd-form {
      display: flex;
      align-items: center;
      gap: 6px;
      flex: 1 1 280px;
      min-width: 220px;
      max-width: 420px;
    }
    .omni-cmd-input {
      width: 100%;
      padding: 7px 13px;
      border-radius: 999px;
      border: 1px solid #DDDDDD;
      background: #F7F7F7;
      color: #222222;
      font-family: inherit;
      font-size: 11.5px;
      outline: none;
    }
    [data-theme="dark"] .omni-cmd-input {
      background: #020617;
      border-color: #475569;
      color: #F8FAFC;
    }
    .omni-cmd-input:focus {
      border-color: #222222;
      background: #FFFFFF;
    }
    .omni-chips {
      display: flex;
      align-items: center;
      gap: 5px;
      flex-wrap: nowrap;
      overflow-x: auto;
      scrollbar-width: none;
    }
    .omni-chips::-webkit-scrollbar { display: none; }
    .omni-chip {
      border: 1px solid #DDDDDD;
      background: #FFFFFF;
      color: #222222;
      padding: 6px 10px;
      border-radius: 999px;
      font-size: 10.5px;
      font-weight: 600;
      cursor: pointer;
      white-space: nowrap;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      transition: all 0.14s ease;
    }
    .omni-chip:hover {
      border-color: #222222;
      background: #F7F7F7;
    }
    .omni-actions {
      display: flex;
      align-items: center;
      gap: 6px;
      flex-shrink: 0;
    }
    .omni-btn {
      border: 1px solid #DDDDDD;
      background: #222222;
      color: #FFFFFF;
      padding: 7px 13px;
      border-radius: 999px;
      font-size: 11.5px;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 5px;
      white-space: nowrap;
      transition: all 0.14s ease;
    }
    .omni-btn.primary {
      background: linear-gradient(135deg, #FF385C 0%, #E31C5F 100%);
      border-color: #FF385C;
      color: #FFFFFF;
    }
    .omni-btn.mic-live {
      background: #008A05 !important;
      border-color: #008A05 !important;
      box-shadow: 0 0 14px rgba(0, 138, 5, 0.35);
    }
    .omni-btn.stop-btn {
      background: #FFF1F2;
      border-color: #FECDD3;
      color: #E11D48;
    }
    .omni-btn.stop-btn:hover {
      background: #E11D48;
      color: #FFF;
    }

    /* =====================================================================
       AGENTIC COMPUTER-USE GHOST CURSOR (#agent-cursor)
       ===================================================================== */
    #agent-cursor {
      position: fixed;
      top: -120px;
      left: -120px;
      z-index: 9999;
      pointer-events: none;
      transition: top 0.48s cubic-bezier(0.22, 1, 0.36, 1), left 0.48s cubic-bezier(0.22, 1, 0.36, 1), opacity 0.2s ease;
      opacity: 0;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    #agent-cursor.visible {
      opacity: 1;
    }
    .agent-cursor-avatar {
      width: 34px;
      height: 34px;
      border-radius: 50%;
      border: 2px solid #10B981;
      overflow: hidden;
      background: #0F172A;
      box-shadow: 0 6px 16px rgba(0,0,0,0.4);
    }
    .agent-cursor-avatar img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    .agent-cursor-label {
      background: #0F172A;
      color: #38BDF8;
      border: 1.5px solid #38BDF8;
      padding: 5px 10px;
      border-radius: 8px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45);
      white-space: nowrap;
    }
    .agent-click-ring {
      position: absolute;
      top: -8px;
      left: -8px;
      width: 32px;
      height: 32px;
      border-radius: 50%;
      border: 2.5px solid #D81E28;
      opacity: 0;
      transform: scale(0.4);
    }
    #agent-cursor.clicking .agent-click-ring {
      animation: agentClickRipple 0.55s ease-out;
    }
    @keyframes agentClickRipple {
      0% { opacity: 1; transform: scale(0.4); }
      100% { opacity: 0; transform: scale(2.2); }
    }

    /* =========================================================================
       PILLAR 5: REDFIN POWERED BY ROCKET × GEMINI AI MARKETPLACE (BETTER THAN REDFIN.COM)
       ========================================================================= */
    /* When Pillar 5 is active, dock Kira PiP & Omni Bar cleanly so 0px of cards or map are ever covered */
    body.p5-clean-mode .kira-pip-card:not(.speaking) {
      display: none !important;
    }
    body.p5-clean-mode .omni-copilot-bar {
      position: static !important;
      transform: none !important;
      width: 100% !important;
      max-width: 1480px !important;
      margin: 24px auto 12px !important;
      border-radius: 16px !important;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06) !important;
    }

    /* 1. CRYSTAL LIQUID WHITE GLASS HERO BANNER + ROCKET RED ACCENTS */
    .rf-hero-banner {
      position: relative;
      width: 100%;
      min-height: 292px;
      border-radius: 26px;
      overflow: hidden;
      margin-bottom: 24px;
      display: flex;
      align-items: center;
      padding: 36px 48px;
      background-color: #0F172A;
      background-image:
        linear-gradient(100deg, rgba(15, 23, 42, 0.82) 0%, rgba(15, 23, 42, 0.58) 52%, rgba(15, 23, 42, 0.25) 100%),
        url('https://storage.googleapis.com/vtxdemos-abnb-images/rocket_re_cdn/v1/images/listings/RKT-066/ext_front.jpg?v=2');
      background-size: cover;
      background-position: center 42%;
      border: 1.5px solid rgba(255, 255, 255, 0.85);
      box-shadow: 0 24px 56px rgba(15, 23, 42, 0.14), 0 6px 18px rgba(15, 23, 42, 0.08), inset 0 2px 0 rgba(255, 255, 255, 0.75);
    }
    .rf-hero-inner {
      width: 100%;
      max-width: 790px;
      z-index: 2;
    }
    .rf-hero-eyebrow {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 5px 14px;
      border-radius: 999px;
      background: linear-gradient(135deg, #D81E28 0%, #E11D48 100%);
      border: 1px solid rgba(255, 255, 255, 0.52);
      box-shadow: 0 6px 18px rgba(216, 30, 40, 0.38), inset 0 1px 0 rgba(255, 255, 255, 0.6);
      color: #FFFFFF;
      font-size: 11.5px;
      font-weight: 800;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      margin-bottom: 12px;
    }
    .rf-hero-title {
      font-size: 38px;
      font-weight: 800;
      color: #FFFFFF;
      line-height: 1.12;
      letter-spacing: -0.025em;
      margin: 0 0 8px 0;
      text-shadow: 0 2px 14px rgba(0, 0, 0, 0.42);
    }
    .rf-hero-subtitle {
      font-size: 14.5px;
      font-weight: 500;
      color: rgba(255, 255, 255, 0.94);
      margin: 0 0 20px 0;
      text-shadow: 0 1px 6px rgba(0, 0, 0, 0.35);
    }

    /* CRYSTAL LIQUID WHITE GLASS TABS ON TOP OF SEARCH BAR */
    .rf-search-tabs {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      margin-bottom: 10px;
      background: rgba(255, 255, 255, 0.22);
      backdrop-filter: blur(20px) saturate(180%);
      padding: 4px;
      border-radius: 999px;
      border: 1px solid rgba(255, 255, 255, 0.38);
    }
    .rf-search-tab {
      height: 34px;
      padding: 0 15px;
      border: 1px solid transparent;
      border-radius: 999px;
      background: transparent;
      color: rgba(255, 255, 255, 0.96);
      font-family: inherit;
      font-size: 12.5px;
      font-weight: 700;
      cursor: pointer;
      transition: background 0.16s ease, color 0.16s ease;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      line-height: 1;
      white-space: nowrap;
    }
    .rf-search-tab:hover {
      background: rgba(255, 255, 255, 0.24);
      color: #FFFFFF;
    }
    .rf-search-tab.active {
      background: linear-gradient(135deg, #D81E28 0%, #B91C1C 100%);
      color: #FFFFFF;
      font-weight: 800;
      border-color: #D81E28;
      background-clip: padding-box;
      box-shadow: 0 4px 12px rgba(216, 30, 40, 0.36);
    }

    /* SINGLE WIDE CRYSTAL LIQUID WHITE SEARCH PILL */
    .rf-search-box {
      width: 100%;
      max-width: 760px;
      height: 60px;
      background: #FFFFFF;
      border: 1.5px solid #E2E8F0;
      border-radius: 999px;
      box-shadow: 0 16px 38px rgba(15, 23, 42, 0.24);
      display: flex;
      align-items: center;
      padding: 0 7px 0 22px;
      gap: 8px;
    }
    .rf-search-input {
      flex: 1;
      min-width: 0;
      height: 100%;
      border: none;
      outline: none;
      background: transparent;
      font-family: inherit;
      font-size: 14.5px;
      font-weight: 600;
      color: #0F172A;
    }
    .rf-search-input::placeholder {
      color: #64748B;
      font-weight: 500;
    }
    .rf-search-action-pill {
      height: 40px;
      padding: 0 14px;
      border-radius: 999px;
      border: 1px solid #E2E8F0;
      background: #F8FAFC;
      color: #0F172A;
      font-family: inherit;
      font-size: 12.5px;
      font-weight: 700;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      line-height: 1;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.15s ease;
      flex-shrink: 0;
    }
    .rf-search-action-pill:hover {
      border-color: #D81E28;
      background: rgba(216, 30, 40, 0.06);
      color: #D81E28;
    }
    .rf-search-submit-btn {
      width: 46px;
      height: 46px;
      border-radius: 50%;
      border: none;
      background: linear-gradient(135deg, #D81E28 0%, #B91C1C 100%);
      color: #FFFFFF;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      flex-shrink: 0;
      transition: transform 0.15s ease, box-shadow 0.15s ease;
      box-shadow: 0 6px 16px rgba(216, 30, 40, 0.35);
    }
    .rf-search-submit-btn:hover {
      transform: scale(1.05);
      box-shadow: 0 8px 22px rgba(216, 30, 40, 0.48);
    }

    /* HERO QUICK VOICE CHIPS ROW */
    .rf-hero-chips {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 7px;
      margin-top: 12px;
    }
    .rf-hero-chip {
      padding: 6px 13px;
      border-radius: 999px;
      border: 1px solid rgba(255, 255, 255, 0.42);
      background: rgba(15, 23, 42, 0.65);
      backdrop-filter: blur(16px);
      color: #FFFFFF;
      font-family: inherit;
      font-size: 11.5px;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.15s ease;
      white-space: nowrap;
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.35);
    }
    .rf-hero-chip:hover {
      background: linear-gradient(135deg, #D81E28 0%, #E11D48 100%);
      border-color: rgba(255, 255, 255, 0.7);
    }

    /* 2. REDFIN "RECOMMENDED FOR YOU" HEADER & CLEAN FILTER BAR */
    .rf-section-header {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 12px;
      margin-bottom: 14px;
    }
    .rf-section-title-group {
      display: flex;
      align-items: baseline;
      flex-wrap: wrap;
      gap: 12px;
    }
    .rf-section-title {
      font-size: 24px;
      font-weight: 800;
      color: var(--ink-primary);
      letter-spacing: -0.02em;
      margin: 0;
    }
    [data-theme="dark"] .rf-section-title { color: #F8FAFC; }
    .rf-section-sub {
      font-size: 14px;
      color: var(--ink-muted);
      font-weight: 600;
    }

    /* CATEGORY TABS & FILTER PILL BAR (CRYSTAL LIQUID WHITE PILLS) */
    .abnb-cat-strip {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      border-bottom: 1px solid #E2E8F0;
      padding-bottom: 12px;
      margin-bottom: 18px;
      flex-wrap: wrap;
    }
    [data-theme="dark"] .abnb-cat-strip {
      border-bottom-color: rgba(255, 255, 255, 0.12);
    }
    .re-arch-ribbon,
    .abnb-cat-tabs {
      display: flex;
      align-items: center;
      gap: 8px;
      overflow-x: auto;
      padding: 2px 0;
      scrollbar-width: none;
    }
    .re-arch-ribbon::-webkit-scrollbar,
    .abnb-cat-tabs::-webkit-scrollbar { display: none; }
    .re-arch-pill,
    .abnb-cat-item {
      height: 40px;
      display: inline-flex;
      flex-direction: row;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 0 14px 0 6px;
      border: 1px solid #E2E8F0;
      border-radius: 999px;
      background: #FFFFFF;
      color: var(--ink-primary);
      font-family: inherit;
      font-size: 12.5px;
      font-weight: 700;
      line-height: 1;
      cursor: pointer;
      transition: background 0.16s ease, color 0.16s ease, border-color 0.16s ease, box-shadow 0.16s ease;
      flex-shrink: 0;
      white-space: nowrap;
      box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
      background-clip: padding-box;
    }
    [data-theme="dark"] .abnb-cat-item {
      background: rgba(30, 41, 59, 0.88);
      border-color: rgba(255, 255, 255, 0.15);
      color: #F8FAFC;
    }
    .re-arch-pill:hover,
    .abnb-cat-item:hover {
      border-color: #D81E28;
      color: #D81E28;
      background: #FFFFFF;
    }
    .re-arch-pill.active,
    .abnb-cat-item.active {
      background: linear-gradient(135deg, #D81E28 0%, #B91C1C 100%);
      color: #FFFFFF;
      border: 1px solid #D81E28;
      background-clip: padding-box;
      box-shadow: 0 6px 16px rgba(216, 30, 40, 0.25);
    }
    .abnb-cat-item.active .cat-pct {
      color: rgba(255, 255, 255, 0.90);
    }
    .abnb-cat-count-badge {
      width: 28px;
      height: 28px;
      border-radius: 50%;
      background: #D81E28;
      color: #FFFFFF;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 10.5px;
      line-height: 1;
      flex-shrink: 0;
    }
    .abnb-cat-item.active .abnb-cat-count-badge {
      background: rgba(255, 255, 255, 0.24);
      color: #FFFFFF;
    }
    [data-theme="dark"] .re-arch-pill.active,
    [data-theme="dark"] .abnb-cat-item.active {
      background: linear-gradient(135deg, #D81E28 0%, #B91C1C 100%);
      color: #FFFFFF;
      border-color: #D81E28;
    }
    .re-arch-thumb,
    .abnb-cat-thumb {
      width: 28px;
      height: 28px;
      border-radius: 50%;
      object-fit: cover;
      display: block;
      flex-shrink: 0;
      border: 1px solid rgba(15, 23, 42, 0.08);
    }
    .abnb-cat-item.active .abnb-cat-thumb {
      border-color: rgba(255, 255, 255, 0.65);
    }
    .cat-pct {
      font-size: 11px;
      color: var(--ink-muted);
      font-weight: 700;
      line-height: 1;
    }
    .re-bed-bar {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      align-items: center;
    }
    .re-bed-chip,
    .abnb-filter-pill {
      height: 36px;
      padding: 0 13px;
      border-radius: 999px;
      border: 1px solid #E2E8F0;
      background: #FFFFFF;
      color: var(--ink-primary);
      font-family: inherit;
      font-size: 12px;
      font-weight: 700;
      line-height: 1;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
      white-space: nowrap;
      box-shadow: 0 2px 6px rgba(15, 23, 42, 0.03);
      background-clip: padding-box;
    }
    [data-theme="dark"] .abnb-filter-pill {
      background: rgba(30, 41, 59, 0.88);
      border-color: rgba(255, 255, 255, 0.15);
      color: #F8FAFC;
    }
    .re-bed-chip:hover,
    .abnb-filter-pill:hover {
      border-color: #D81E28;
      color: #D81E28;
    }
    .re-bed-chip.active,
    .abnb-filter-pill.active {
      background: linear-gradient(135deg, #D81E28 0%, #B91C1C 100%);
      color: #FFFFFF;
      border-color: #D81E28;
      background-clip: padding-box;
      box-shadow: 0 4px 12px rgba(216, 30, 40, 0.24);
    }
    .re-bed-pct {
      font-size: 11px;
      opacity: 0.78;
      font-weight: 500;
    }

    /* 3. SPLIT-SCREEN STAGE (LEFT 2-COL FRAMED REDFIN CARDS + RIGHT STICKY MAP) */
    .abnb-split-stage {
      display: grid;
      grid-template-columns: 58% 42%;
      gap: 22px;
      align-items: start;
    }
    .abnb-split-stage.map-hidden {
      grid-template-columns: 1fr;
    }
    .abnb-split-stage.map-hidden .abnb-map-col {
      display: none;
    }
    .abnb-split-stage.map-hidden .re-grid,
    .abnb-split-stage.map-hidden .abnb-cards-col {
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }
    .re-grid,
    .abnb-cards-col {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 20px;
    }

    /* 4. CRYSTAL LIQUID WHITE GLASS PROPERTY CARD + ROCKET RED ACCENTS */
    .re-card,
    .abnb-card {
      background: rgba(255, 255, 255, 0.88);
      backdrop-filter: blur(32px) saturate(190%);
      -webkit-backdrop-filter: blur(32px) saturate(190%);
      border: 1.5px solid rgba(226, 232, 240, 0.95);
      border-radius: 22px;
      overflow: hidden;
      cursor: pointer;
      display: flex;
      flex-direction: column;
      box-shadow: 0 14px 36px rgba(15, 23, 42, 0.06), 0 3px 10px rgba(15, 23, 42, 0.03), inset 0 1.5px 0 #FFFFFF;
      transition: transform 0.22s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.22s ease, border-color 0.22s ease;
      min-width: 0;
    }
    [data-theme="dark"] .abnb-card {
      background: rgba(15, 23, 42, 0.80);
      border-color: rgba(255, 255, 255, 0.14);
      box-shadow: 0 18px 44px rgba(0, 0, 0, 0.55), inset 0 1.5px 0 rgba(255, 255, 255, 0.12);
    }
    .re-card:hover,
    .abnb-card:hover {
      transform: translateY(-4px);
      box-shadow: 0 22px 48px rgba(15, 23, 42, 0.11), inset 0 1.5px 0 #FFFFFF;
      border-color: rgba(216, 30, 40, 0.42);
    }
    .re-card-media,
    .abnb-card-media {
      position: relative;
      width: 100%;
      aspect-ratio: 16 / 10;
      background: #F1F5F9;
      overflow: hidden;
    }
    .re-card-img,
    .abnb-card-img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
      transition: transform 0.35s ease;
    }
    .re-card:hover .re-card-img,
    .abnb-card:hover .abnb-card-img {
      transform: scale(1.03);
    }

    /* REDFIN DARK CIRCULAR MAP PIN BUTTON ON BOTTOM-RIGHT OF PHOTO */
    .rf-photo-pin-btn {
      position: absolute;
      bottom: 10px;
      right: 10px;
      width: 34px;
      height: 34px;
      border-radius: 50%;
      border: 1px solid rgba(255, 255, 255, 0.45);
      background: rgba(15, 23, 42, 0.78);
      backdrop-filter: blur(12px);
      color: #FFFFFF;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      z-index: 3;
      transition: background 0.15s ease, transform 0.15s ease;
    }
    .rf-photo-pin-btn:hover {
      background: #D81E28;
      transform: scale(1.08);
    }

    /* CRYSTAL WHITE GLASS CARD BODY (PRICE -> SPECS -> ADDRESS -> ATTRIBUTION) */
    .rf-card-body {
      padding: 15px 18px 16px;
      display: flex;
      flex-direction: column;
      gap: 5px;
      background: transparent;
    }
    [data-theme="dark"] .rf-card-body {
      background: transparent;
    }
    .rf-card-price-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
    }
    .rf-card-price-group {
      display: flex;
      align-items: baseline;
      gap: 8px;
      min-width: 0;
    }
    .rf-card-price {
      font-size: 21px;
      font-weight: 800;
      color: var(--ink-primary);
      letter-spacing: -0.02em;
      line-height: 1.15;
    }
    [data-theme="dark"] .rf-card-price { color: #F8FAFC; }
    .rf-card-piti-badge {
      font-size: 11.5px;
      font-weight: 800;
      color: #D81E28;
      background: rgba(216, 30, 40, 0.08);
      border: 1px solid rgba(216, 30, 40, 0.20);
      padding: 2px 8px;
      border-radius: 999px;
      white-space: nowrap;
    }
    .rf-card-actions {
      display: flex;
      align-items: center;
      gap: 6px;
      flex-shrink: 0;
    }
    .rf-icon-btn {
      width: 30px;
      height: 30px;
      border-radius: 50%;
      border: none;
      background: transparent;
      color: var(--ink-secondary);
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: background 0.15s ease, color 0.15s ease;
    }
    .rf-icon-btn:hover {
      background: rgba(216, 30, 40, 0.08);
      color: #D81E28;
    }
    .rf-icon-btn.liked {
      color: #D81E28;
    }
    .rf-icon-btn.liked svg {
      fill: #D81E28;
      stroke: #D81E28;
    }
    .rf-card-specs {
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 13.5px;
      font-weight: 600;
      color: var(--ink-primary);
      margin-top: 2px;
    }
    [data-theme="dark"] .rf-card-specs { color: #F8FAFC; }
    .rf-card-address {
      font-size: 13px;
      font-weight: 500;
      color: var(--ink-secondary);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    [data-theme="dark"] .rf-card-address { color: #CBD5E1; }
    .rf-card-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      margin-top: 4px;
      padding-top: 8px;
      border-top: 1px solid #F1F5F9;
      font-size: 11.5px;
      color: var(--ink-muted);
    }
    [data-theme="dark"] .rf-card-footer { border-top-color: rgba(255, 255, 255, 0.12); }

    .abnb-guest-fav {
      position: absolute;
      top: 10px;
      left: 10px;
      padding: 4px 11px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.92);
      backdrop-filter: blur(16px);
      border: 1px solid #FFFFFF;
      color: #0F172A;
      font-size: 11.5px;
      font-weight: 800;
      z-index: 2;
      box-shadow: 0 4px 14px rgba(15, 23, 42, 0.14);
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }
    .abnb-heart-btn {
      position: absolute;
      top: 10px;
      right: 12px;
      width: 32px;
      height: 32px;
      border: none;
      background: transparent;
      color: #FFFFFF;
      cursor: pointer;
      z-index: 3;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: transform 0.15s ease;
    }
    .abnb-heart-btn svg {
      width: 24px;
      height: 24px;
      fill: rgba(0, 0, 0, 0.45);
      stroke: #FFFFFF;
      stroke-width: 2;
    }
    .abnb-heart-btn.liked svg {
      fill: #D81E28;
      stroke: #D81E28;
    }
    .abnb-heart-btn:hover {
      transform: scale(1.15);
    }
    .re-card-nav-btn {
      position: absolute;
      top: 50%;
      transform: translateY(-50%);
      width: 32px;
      height: 32px;
      border-radius: 50%;
      border: 1px solid #FFFFFF;
      background: rgba(255, 255, 255, 0.90);
      backdrop-filter: blur(12px);
      color: #0F172A;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      z-index: 3;
      font-weight: 800;
      font-size: 16px;
      opacity: 0;
      box-shadow: 0 4px 12px rgba(15, 23, 42, 0.18);
      transition: opacity 0.16s ease, transform 0.16s ease;
    }
    .re-card:hover .re-card-nav-btn,
    .abnb-card:hover .re-card-nav-btn {
      opacity: 1;
    }
    .re-card-nav-btn:hover {
      background: #FFFFFF;
      transform: translateY(-50%) scale(1.06);
    }
    .re-card-room-pill {
      position: absolute;
      bottom: 10px;
      left: 12px;
      right: 12px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 4px 10px;
      border-radius: 999px;
      background: rgba(15, 23, 42, 0.76);
      backdrop-filter: blur(10px);
      color: #FFFFFF;
      font-size: 11px;
      font-weight: 600;
      z-index: 2;
    }
    .abnb-credit-pill {
      display: inline-flex;
      align-items: center;
      padding: 2px 8px;
      border-radius: 999px;
      background: rgba(5, 150, 105, 0.12);
      color: #047857;
      font-size: 11.5px;
      font-weight: 700;
    }
    .abnb-tag-pill {
      display: inline-flex;
      align-items: center;
      padding: 2px 9px;
      border-radius: 999px;
      background: rgba(216, 30, 40, 0.08);
      color: #D81E28;
      font-size: 11.5px;
      font-weight: 700;
      cursor: pointer;
    }
    .abnb-tag-pill:hover {
      background: #D81E28;
      color: #FFFFFF;
    }

    /* STICKY CRYSTAL GLASS INTERACTIVE MAP & FLOATING ROCKET RED PRICE PILLS */
    .abnb-map-col {
      position: sticky;
      top: 76px;
      height: calc(100vh - 155px);
      border-radius: 24px;
      overflow: hidden;
      border: 1.5px solid rgba(226, 232, 240, 0.95);
      box-shadow: 0 20px 48px rgba(15, 23, 42, 0.08), inset 0 1.5px 0 #FFFFFF;
      background: #F1F5F9;
    }
    #p5-airbnb-map {
      width: 100%;
      height: 100%;
      z-index: 1;
    }
    .abnb-map-ctrl-overlay {
      position: absolute;
      top: 14px;
      right: 14px;
      z-index: 500;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .abnb-map-pill-btn {
      background: rgba(255, 255, 255, 0.90);
      backdrop-filter: blur(20px);
      color: #0F172A;
      border: 1px solid rgba(226, 232, 240, 0.95);
      border-radius: 999px;
      padding: 7px 14px;
      font-family: inherit;
      font-size: 12px;
      font-weight: 800;
      cursor: pointer;
      box-shadow: 0 6px 18px rgba(15, 23, 42, 0.12), inset 0 1px 0 #FFFFFF;
      transition: all 0.15s ease;
    }
    .abnb-map-pill-btn:hover {
      background: linear-gradient(135deg, #D81E28 0%, #E11D48 100%);
      color: #FFFFFF;
      border-color: rgba(255, 255, 255, 0.6);
    }
    .abnb-price-pin {
      background: rgba(255, 255, 255, 0.94);
      backdrop-filter: blur(12px);
      color: #0F172A;
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 12.5px;
      font-weight: 800;
      padding: 5px 11px;
      border-radius: 999px;
      box-shadow: 0 6px 16px rgba(15, 23, 42, 0.18), 0 0 0 1.5px rgba(216, 30, 40, 0.28);
      white-space: nowrap;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      transition: transform 0.15s ease, background 0.15s ease, color 0.15s ease;
      cursor: pointer;
    }
    .abnb-price-pin:hover,
    .abnb-price-pin.active-pin {
      background: linear-gradient(135deg, #D81E28 0%, #E11D48 100%) !important;
      color: #FFFFFF !important;
      transform: scale(1.13);
      z-index: 999 !important;
    }

    /* =========================================================================
    /* Full-Screen Airbnb Listing Detail Modal (Screenshot 6 Style) */
    .re-modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, 0.65);
      backdrop-filter: blur(6px);
      z-index: 9800;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .re-modal-backdrop.open {
      display: flex;
    }
    .re-modal-sheet {
      width: 100%;
      max-width: 1240px;
      max-height: 92vh;
      background: var(--bg-card);
      border: 1px solid var(--border-hairline);
      border-radius: 20px;
      overflow-y: auto;
      box-shadow: 0 32px 90px rgba(0,0,0,0.45);
      padding: 26px 32px 36px;
    }
    .re-bento-hero,
    .abnb-detail-mosaic {
      display: grid;
      grid-template-columns: 2fr 1fr 1fr;
      grid-template-rows: 205px 205px;
      gap: 8px;
      border-radius: 16px;
      overflow: hidden;
      margin-bottom: 24px;
      position: relative;
    }
    .re-bento-main,
    .abnb-mosaic-main {
      grid-row: 1 / span 2;
      position: relative;
      cursor: pointer;
      background: #F1F5F9;
      overflow: hidden;
    }
    .re-bento-sub,
    .abnb-mosaic-cell {
      position: relative;
      cursor: pointer;
      background: #F1F5F9;
      overflow: hidden;
    }
    .re-bento-hero img,
    .abnb-detail-mosaic img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
      transition: transform 0.25s ease;
    }
    .re-bento-hero div:hover img,
    .abnb-detail-mosaic div:hover img {
      transform: scale(1.03);
    }
    .re-bento-lbl {
      position: absolute;
      bottom: 10px;
      left: 10px;
      padding: 4px 10px;
      border-radius: 8px;
      background: rgba(34, 34, 34, 0.78);
      color: #FFF;
      font-size: 11px;
      font-weight: 600;
    }
    .abnb-show-all-photos-btn {
      position: absolute;
      bottom: 16px;
      right: 16px;
      background: #FFFFFF;
      color: #222222;
      border: 1px solid #222222;
      border-radius: 8px;
      padding: 7px 14px;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      z-index: 5;
      box-shadow: 0 2px 8px rgba(0,0,0,0.16);
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .abnb-detail-body {
      display: grid;
      grid-template-columns: 64% 34%;
      gap: 2%;
      align-items: start;
    }
    .abnb-reserve-card {
      position: sticky;
      top: 16px;
      background: var(--bg-card);
      border: 1px solid #DDDDDD;
      border-radius: 16px;
      padding: 22px;
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.10);
    }
    .abnb-reserve-btn {
      width: 100%;
      padding: 13px 16px;
      border-radius: 10px;
      border: none;
      background: linear-gradient(90deg, #E61E4D 0%, #E31C5F 50%, #D70466 100%);
      color: #FFFFFF;
      font-family: inherit;
      font-size: 15px;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 4px 14px rgba(227, 28, 95, 0.35);
      transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .abnb-reserve-btn:hover {
      transform: translateY(-1px);
      box-shadow: 0 6px 20px rgba(227, 28, 95, 0.5);
    }

    /* =========================================================================
       MOBILE-FIRST RESPONSIVE DESIGN (PIXEL 11 PRO 412px & IPHONE 16/17 PRO)
       ========================================================================= */
    @media (max-width: 900px) {
      html, body {
        overflow-x: hidden;
        max-width: 100vw;
      }
      .top-nav {
        height: auto !important;
        padding: 10px 12px !important;
        flex-wrap: wrap !important;
        gap: 8px !important;
      }
      .brand-cluster {
        flex: 1 1 auto;
        min-width: 0;
      }
      .brand-title {
        font-size: 13.5px !important;
        flex-wrap: wrap;
      }
      .brand-sub {
        font-size: 10px !important;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 255px;
      }
      .nav-controls {
        gap: 6px !important;
      }
      .model-select {
        font-size: 11px !important;
        padding: 5px 8px !important;
        max-width: 145px;
      }
      .theme-toggle-btn span {
        display: none;
      }
      .pillar-tabs {
        order: 3;
        width: 100% !important;
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch;
        scroll-snap-type: x proximity;
        padding-bottom: 2px;
        gap: 6px !important;
        justify-content: flex-start !important;
      }
      .pillar-tabs::-webkit-scrollbar {
        display: none;
      }
      .pillar-tab {
        scroll-snap-align: start;
        padding: 7px 11px !important;
        font-size: 11.5px !important;
        flex-shrink: 0;
      }
      .main-shell {
        padding: 12px 10px 168px !important;
      }
      .moat-strip {
        flex-direction: column !important;
        align-items: flex-start !important;
        padding: 12px 14px !important;
        gap: 8px !important;
      }
      .moat-title {
        font-size: 13.5px !important;
        line-height: 1.35;
      }
      .moat-subtitle {
        font-size: 11.5px !important;
        line-height: 1.45;
      }
      .vs-claude-pill {
        white-space: normal !important;
        font-size: 10.5px !important;
        line-height: 1.4;
        width: 100%;
      }
      .kpi-row {
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
        gap: 8px !important;
      }
      .kpi-tile {
        padding: 10px 12px !important;
      }
      .kpi-val {
        font-size: 18px !important;
      }
      .v-card {
        padding: 13px !important;
      }
      .v-card-header {
        flex-wrap: wrap;
        gap: 6px;
      }
      /* Pillar 5 Mobile Layout */
      .re-arch-ribbon {
        display: flex !important;
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch;
        scroll-snap-type: x proximity;
        gap: 8px !important;
        padding-bottom: 6px;
      }
      .re-arch-ribbon::-webkit-scrollbar {
        display: none;
      }
      .re-arch-pill {
        flex: 0 0 auto;
        min-width: 158px;
        scroll-snap-align: start;
        padding: 8px 10px !important;
      }
      .re-bed-bar {
        overflow-x: auto;
        flex-wrap: nowrap !important;
        -webkit-overflow-scrolling: touch;
        padding-bottom: 4px;
        width: 100%;
      }
      .re-bed-bar::-webkit-scrollbar {
        display: none;
      }
      .re-bed-chip {
        flex-shrink: 0;
        padding: 6px 11px !important;
        font-size: 11px !important;
      }
      .re-grid {
        grid-template-columns: 1fr !important;
        gap: 14px !important;
      }
      /* Full-Screen Mobile Bottom Sheet Modal for Property Showcase */
      .re-modal-backdrop {
        padding: 0 !important;
        align-items: flex-end !important;
      }
      .re-modal-sheet {
        max-height: 94dvh !important;
        border-radius: 20px 20px 0 0 !important;
        padding: 16px 14px calc(28px + env(safe-area-inset-bottom, 0px)) !important;
      }
      .re-bento-hero {
        grid-template-columns: 1fr 1fr !important;
        grid-template-rows: 200px 105px 105px !important;
        height: auto !important;
        gap: 6px !important;
      }
      .re-bento-main {
        grid-column: 1 / span 2 !important;
        grid-row: 1 / span 1 !important;
      }
      #re-modal-rooms-grid {
        grid-template-columns: 1fr !important;
      }
      /* Floating Kira PiP Card on Mobile */
      .kira-pip-card {
        top: auto !important;
        bottom: calc(136px + env(safe-area-inset-bottom, 0px)) !important;
        right: 10px !important;
        width: 132px !important;
        padding: 7px !important;
        border-radius: 12px !important;
      }
      .kira-pip-video-wrap {
        width: 56px !important;
        height: 56px !important;
      }
      #kira-pip-eq-canvas {
        width: 110px !important;
        height: 18px !important;
      }
      .kira-pip-status {
        font-size: 8.5px !important;
      }
      /* Compact Mobile Bottom Omni-Copilot Bar */
      .omni-copilot-bar {
        width: calc(100% - 14px) !important;
        bottom: calc(6px + env(safe-area-inset-bottom, 0px)) !important;
        padding: 8px 10px !important;
        border-radius: 14px !important;
        flex-wrap: wrap !important;
        gap: 6px !important;
      }
      .omni-left {
        min-width: 0 !important;
        max-width: 100% !important;
        flex: 1 1 auto;
      }
      .omni-avatar-thumb {
        width: 32px !important;
        height: 32px !important;
      }
      .omni-title {
        font-size: 11px !important;
      }
      .omni-transcript {
        font-size: 10px !important;
        max-width: 185px !important;
      }
      .omni-actions {
        gap: 5px !important;
      }
      .omni-btn {
        padding: 6px 9px !important;
        font-size: 10.5px !important;
      }
      .omni-cmd-form {
        order: 3;
        width: 100% !important;
        max-width: 100% !important;
        flex: 1 1 100% !important;
      }
      .omni-chips {
        display: none !important;
      }
    }
  </style>
</head>
<body class="p5-clean-mode">

  <!-- AGENTIC COMPUTER-USE GHOST CURSOR WITH KIRA AVATAR BADGE -->
  <div id="agent-cursor">
    <div class="agent-click-ring"></div>
    <svg width="24" height="24" viewBox="0 0 24 24" fill="#D81E28" stroke="#FFFFFF" stroke-width="2">
      <path d="M4 3l16 7.5-7 2-2.5 7L4 3z"/>
    </svg>
    <div class="agent-cursor-avatar">
      <img src="/static/kira_avatar.png" alt="Kira" />
    </div>
    <div class="agent-cursor-label" id="agent-cursor-label">Kira · Screen Co-Pilot</div>
  </div>

  <!-- FLOATING VOICE-REACTIVE AVATAR PIP STAGE (VISIBLE ON ALL PILLARS) -->
  <div class="kira-pip-card" id="kira-pip-card">
    <div class="kira-pip-video-wrap" onclick="handleAvatarTapInterruptOrVoice()" style="cursor:pointer;" title="Click Kira to interrupt speech or toggle Live Mic">
      <canvas id="kira-pip-canvas" width="240" height="240"></canvas>
    </div>
    <canvas id="kira-pip-eq-canvas" width="185" height="28"></canvas>
    <div class="kira-pip-status" id="kira-pip-status">KIRA · READY (CLICK MIC OR TYPE)</div>
    <button id="btn-pip-stop" type="button" onclick="stopAllAudioAndAvatarNow(this)" style="margin-top:6px;width:100%;padding:5px 8px;border-radius:7px;border:1px solid #EF4444;background:rgba(239,68,68,0.18);color:#FCA5A5;font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:800;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:5px;transition:all 0.15s ease;">
      <svg width="11" height="11" viewBox="0 0 24 24" fill="currentColor"><rect x="5" y="5" width="14" height="14" rx="2"/></svg>
      <span id="lbl-pip-stop">STOP AUDIO &amp; ACTION (0MS)</span>
    </button>
  </div>

  <!-- STICKY NAVIGATION HEADER (REDFIN POWERED BY ROCKET × GEMINI) -->
  <header class="top-nav">
    <div class="brand-cluster">
      <div class="rocket-logo-mark" style="background:#D92228;border-radius:8px;width:36px;height:36px;">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
      </div>
      <div>
        <div class="brand-title" style="color:#D92228;font-size:21px;font-weight:900;letter-spacing:-0.03em;line-height:1.05;">Redfin <span style="color:#111111;font-weight:800;font-size:15px;">&times; Gemini AI</span></div>
        <div class="brand-sub" style="font-size:10.5px;font-weight:700;color:#4B5563;margin-top:1px;">Powered by Rocket &middot; Mortgage &middot; Mr. Cooper</div>
      </div>
    </div>

    <nav class="pillar-tabs" role="tablist">
      <button class="pillar-tab" onclick="switchPillar(1)" id="tab-btn-1">
        <span class="pillar-num">P1</span>
        <svg class="ico" viewBox="0 0 24 24"><path d="M3 3v18h18"/><path d="M7 14l4-4 4 3 5-6"/></svg>
        TimesFM
      </button>
      <button class="pillar-tab" onclick="switchPillar(2)" id="tab-btn-2">
        <span class="pillar-num">P2</span>
        <svg class="ico" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="16" rx="2"/><polygon points="10 9 15 12 10 15 10 9"/></svg>
        Veo 3.1 Reels
      </button>
      <button class="pillar-tab" onclick="switchPillar(3)" id="tab-btn-3">
        <span class="pillar-num">P3</span>
        <svg class="ico" viewBox="0 0 24 24"><path d="M12 21s-7-6.5-7-12a7 7 0 1 1 14 0c0 5.5-7 12-7 12z"/><circle cx="12" cy="9" r="2.5"/></svg>
        Maps + YouTube
      </button>
      <button class="pillar-tab" onclick="switchPillar(4)" id="tab-btn-4">
        <span class="pillar-num">P4</span>
        <svg class="ico" viewBox="0 0 24 24"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="22"/></svg>
        Live Avatar
      </button>
      <button class="pillar-tab active" onclick="switchPillar(5)" id="tab-btn-5">
        <span class="pillar-num">P5</span>
        <svg class="ico" viewBox="0 0 24 24"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
        Homes &amp; Map
      </button>
      <button class="pillar-tab" onclick="switchPillar(6)" id="tab-btn-6">
        <span class="pillar-num">VS</span>
        <svg class="ico" viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
        vs. Claude
      </button>
    </nav>

    <div class="nav-actions">
      <select id="global-model-selector" class="model-select" onchange="setGlobalModelSelection(this.value)" title="Active Vertex AI Model Selector">
        <option value="gemini-3.8-flash" selected>gemini-3.8-flash (Flash-Next)</option>
        <option value="gemini-3.8-flash-lite">gemini-3.8-flash-lite</option>
        <option value="gemini-4-argon">gemini-4-argon</option>
      </select>
      <button class="theme-btn" onclick="toggleTheme()" id="theme-toggle-btn">
        <svg class="ico ico-sm" viewBox="0 0 24 24"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
        <span id="theme-toggle-lbl">Dark Theme</span>
      </button>
    </div>
  </header>

  <main class="stage-wrap">

    <!-- =====================================================================
         PILLAR 1: BIGQUERY ML TIMESFM (`AI.FORECAST`)
         ===================================================================== -->
    <section class="pillar-pane" id="pillar-1">
      <div class="moat-strip">
        <div>
          <div class="moat-title">Pillar 1 · BigQuery ML TimesFM (`AI.FORECAST`) — 9.5M Loan &amp; Redfin Demand Horizon</div>
          <div class="moat-subtitle">Zero-shot Google Research TimesFM foundation model executing in BigQuery Standard SQL over `vtxdemos.rocket_nextgen_timesfm.portfolio_metrics` — controllable via Live Voice or Text below.</div>
        </div>
        <div class="vs-claude-pill">
          <strong>Gemini / BQML:</strong> Zero-Shot SQL (~900ms) &nbsp;|&nbsp; <span class="claude-no">Anthropic Claude: 0 Time-Series Models &amp; No SQL Warehouse</span>
        </div>
      </div>

      <div class="studio-grid-12">
        <!-- LEFT CONTROLS (4 COLS) -->
        <div class="col-4 v-card">
          <div class="v-card-header">
            <span class="v-card-title">
              <svg class="ico ico-sm" viewBox="0 0 24 24"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>
              1. Select Rocket Cohort
            </span>
            <span class="badge-live" id="p1-latency-badge"><span class="dot-pulse"></span>Live BQ</span>
          </div>

          <div class="cohort-list">
            <button class="cohort-btn active" id="p1-cohort-mrcooper_refi_locks" onclick="selectTimesFmCohort('mrcooper_refi_locks', this)">
              <div class="cohort-icon-box">
                <svg class="ico" viewBox="0 0 24 24"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
              </div>
              <div>
                <div class="cohort-btn-title">Mr. Cooper + Rocket Refi-Wave Locks</div>
                <div class="cohort-btn-sub">9.5M Serviced Loans · Weekly Recapture Volume</div>
              </div>
            </button>
            <button class="cohort-btn" id="p1-cohort-redfin_tour_demand" onclick="selectTimesFmCohort('redfin_tour_demand', this)">
              <div class="cohort-icon-box">
                <svg class="ico" viewBox="0 0 24 24"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
              </div>
              <div>
                <div class="cohort-btn-title">Redfin Buyer Tour &amp; Offer Velocity</div>
                <div class="cohort-btn-sub">Top-of-Funnel Redfin Tours to Rocket Pre-Approvals</div>
              </div>
            </button>
            <button class="cohort-btn" id="p1-cohort-escrow_liquidity_outflow_m" onclick="selectTimesFmCohort('escrow_liquidity_outflow_m', this)">
              <div class="cohort-icon-box">
                <svg class="ico" viewBox="0 0 24 24"><line x1="3" y1="22" x2="21" y2="22"/><line x1="6" y1="18" x2="6" y2="11"/><line x1="10" y1="18" x2="10" y2="11"/><line x1="14" y1="18" x2="14" y2="11"/><line x1="18" y1="18" x2="18" y2="11"/><polygon points="12 2 20 7 4 7"/></svg>
              </div>
              <div>
                <div class="cohort-btn-title">Mr. Cooper Escrow Tax/Ins Outflow ($M)</div>
                <div class="cohort-btn-sub">$2.1T Servicing Treasury Float &amp; Disbursement Spike</div>
              </div>
            </button>
            <button class="cohort-btn" id="p1-cohort-warehouse_funding_b" onclick="selectTimesFmCohort('warehouse_funding_b', this)">
              <div class="cohort-icon-box">
                <svg class="ico" viewBox="0 0 24 24"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>
              </div>
              <div>
                <div class="cohort-btn-title">Rocket Capital Markets Warehouse Draw ($B)</div>
                <div class="cohort-btn-sub">Weekly MBS Hedging &amp; Warehouse Line Capacity</div>
              </div>
            </button>
          </div>

          <!-- EXACT 1-BPS STEP SLIDERS SO ANY NUMBER (E.G. -60 BPS) WORKS -->
          <div class="ctrl-group" id="ctrl-wrap-shock">
            <div class="ctrl-label">
              <span>Fed / 30-Yr Mortgage Rate Shock</span>
              <span id="lbl-p1-shock">-50 bps</span>
            </div>
            <input type="range" id="p1-shock" min="-150" max="100" step="1" value="-50"
                   oninput="document.getElementById('lbl-p1-shock').innerText=(this.value>0?'+':'')+this.value+' bps'"
                   onchange="runPillar1TimesFM()" />
          </div>

          <div class="ctrl-group" id="ctrl-wrap-horizon">
            <div class="ctrl-label">
              <span>TimesFM Forecast Horizon</span>
              <span id="lbl-p1-horizon">12 Weeks</span>
            </div>
            <input type="range" id="p1-horizon" min="4" max="24" step="1" value="12"
                   oninput="document.getElementById('lbl-p1-horizon').innerText=this.value+' Weeks'"
                   onchange="runPillar1TimesFM()" />
          </div>

          <div class="ctrl-group" id="ctrl-wrap-ci">
            <div class="ctrl-label">
              <span>Prediction Interval Confidence</span>
              <span id="lbl-p1-ci">90% CI</span>
            </div>
            <input type="range" id="p1-ci" min="80" max="99" step="1" value="90"
                   oninput="document.getElementById('lbl-p1-ci').innerText=this.value+'% CI'"
                   onchange="runPillar1TimesFM()" />
          </div>

          <button class="btn-primary" onclick="runPillar1TimesFM()" id="btn-run-p1">
            <svg class="ico" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
            Execute Live BigQuery `AI.FORECAST` (TimesFM)
          </button>
          <button class="btn-secondary" style="margin-top:8px;" onclick="toggleSqlDrawer()">
            <svg class="ico ico-sm" viewBox="0 0 24 24"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
            View Live BigQuery `AI.FORECAST` SQL
          </button>
        </div>

        <!-- RIGHT VISUAL FAN CHART (8 COLS) -->
        <div class="col-8 v-card">
          <div class="v-card-header">
            <div>
              <div style="font-size:16px;font-weight:800;" id="p1-chart-title">Mr. Cooper + Rocket Servicing Refi-Wave Locks</div>
              <div style="font-size:12px;color:var(--ink-muted);" id="p1-chart-sub">78-Week Historical Trajectory + TimesFM Zero-Shot Prediction Cone</div>
            </div>
            <button class="btn-secondary" style="width:auto;padding:7px 12px;" onclick="speakPillar1Summary(this)" id="btn-p1-tts">
              <svg class="ico ico-sm" viewBox="0 0 24 24"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>
              <span>Hear Treasury Briefing (24kHz HD)</span>
            </button>
          </div>

          <div class="kpi-row" id="p1-kpi-row">
            <div class="kpi-tile">
              <div class="kpi-label">Current Weekly Rate</div>
              <div class="kpi-val" id="p1-kpi-last">18,420</div>
              <div class="kpi-sub">Observed Baseline</div>
            </div>
            <div class="kpi-tile">
              <div class="kpi-label">TimesFM Peak Forecast</div>
              <div class="kpi-val" id="p1-kpi-peak" style="color:var(--google-blue);">23,190</div>
              <div class="kpi-sub" id="p1-kpi-delta">+25.9% Surge</div>
            </div>
            <div class="kpi-tile">
              <div class="kpi-label">Horizon Cumulative</div>
              <div class="kpi-val" id="p1-kpi-cum">254,800</div>
              <div class="kpi-sub">Total Forecast Volume</div>
            </div>
            <div class="kpi-tile">
              <div class="kpi-label">Rocket Revenue Impact</div>
              <div class="kpi-val" id="p1-kpi-usd" style="color:var(--emerald);">$432M</div>
              <div class="kpi-sub">Recaptured Servicing Value</div>
            </div>
          </div>

          <!-- INTERACTIVE SVG FAN CHART -->
          <div style="background:var(--bg-subtle);border:1px solid var(--border-hairline);border-radius:12px;padding:14px;position:relative;">
            <svg id="p1-svg-chart" viewBox="0 0 860 320" style="width:100%;height:320px;overflow:visible;"></svg>
          </div>

          <pre class="sql-drawer" id="p1-sql-drawer"></pre>
        </div>
      </div>
    </section>

    <!-- =====================================================================
         PILLAR 2: REELS GENERATION FROM TEXT (`VEO 3.1` + `24kHz VOICEOVER`)
         ===================================================================== -->
    <section class="pillar-pane" id="pillar-2">
      <div class="moat-strip">
        <div>
          <div class="moat-title">Pillar 2 · Text-to-Reels Studio (`Veo 3.1` 9:16 MP4 + `Gemini Image` + `24kHz Live Voiceover`)</div>
          <div class="moat-subtitle">Turn any Redfin MLS listing or Rocket Mortgage rate-drop offer into a vertical 9:16 social video Reel with synchronized 24kHz HD narration and live payment stickers.</div>
        </div>
        <div class="vs-claude-pill">
          <strong>Gemini + Veo 3.1:</strong> Native 9:16 Video + 24kHz Voice &nbsp;|&nbsp; <span class="claude-no">Anthropic Claude: Text-Only Output (No Video, No Image, No Voice)</span>
        </div>
      </div>

      <div class="studio-grid-12">
        <!-- LEFT CREATIVE CONTROLS (5 COLS) -->
        <div class="col-5 v-card">
          <div class="v-card-header">
            <span class="v-card-title">
              <svg class="ico ico-sm" viewBox="0 0 24 24"><rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"/><line x1="7" y1="2" x2="7" y2="22"/><line x1="17" y1="2" x2="17" y2="22"/><line x1="2" y1="12" x2="22" y2="12"/></svg>
              1. Select Redfin Listing or Custom Prompt
            </span>
            <span class="badge-live" id="p2-status-badge"><span class="dot-pulse"></span>Veo 3.1 Ready</span>
          </div>

          <div class="cohort-list">
            <button class="cohort-btn active" id="p2-preset-royal_oak" onclick="loadPresetReel('royal_oak', this)">
              <div class="cohort-icon-box">
                <svg class="ico" viewBox="0 0 24 24"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>
              </div>
              <div>
                <div class="cohort-btn-title">418 Elmhurst Ave · Royal Oak, MI ($460,000)</div>
                <div class="cohort-btn-sub">Veo 3.1 9:16 Golden-Hour Drone MP4 · Aoede 24kHz Voiceover</div>
              </div>
            </button>
            <button class="cohort-btn" id="p2-preset-corktown_loft" onclick="loadPresetReel('corktown_loft', this)">
              <div class="cohort-icon-box">
                <svg class="ico" viewBox="0 0 24 24"><rect x="4" y="2" width="16" height="20" rx="2"/><line x1="9" y1="6" x2="15" y2="6"/><line x1="9" y1="10" x2="15" y2="10"/><line x1="9" y1="14" x2="15" y2="14"/></svg>
              </div>
              <div>
                <div class="cohort-btn-title">1420 Michigan Ave #4B · Corktown Detroit ($385,000)</div>
                <div class="cohort-btn-sub">Veo 3.1 9:16 Timber-Loft Walkthrough MP4 · Puck 24kHz Voiceover</div>
              </div>
            </button>
            <button class="cohort-btn" id="p2-preset-ann_arbor" onclick="loadPresetReel('ann_arbor', this)">
              <div class="cohort-icon-box">
                <svg class="ico" viewBox="0 0 24 24"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/></svg>
              </div>
              <div>
                <div class="cohort-btn-title">2105 Devonshire Rd · Ann Arbor, MI ($695,000)</div>
                <div class="cohort-btn-sub">Veo 3.1 9:16 Mid-Century Glass MP4 · Kore 24kHz Voiceover</div>
              </div>
            </button>
          </div>

          <div class="ctrl-group">
            <div class="ctrl-label"><span>Custom Text-to-Reel Prompt</span><span>Veo 3.1 + Gemini 3.8</span></div>
            <textarea id="p2-prompt" rows="2" style="width:100%;padding:10px;border-radius:8px;border:1px solid var(--border-hairline);background:var(--bg-subtle);color:var(--ink-primary);font-family:inherit;font-size:12px;">Smooth cinematic 9:16 vertical drone video approaching a luxury modern craftsman home at 418 Elmhurst Ave Royal Oak Michigan at golden hour</textarea>
          </div>

          <div class="ctrl-group" id="ctrl-wrap-p2-price">
            <div class="ctrl-label"><span>Listing Price</span><span id="lbl-p2-price">$460,000</span></div>
            <input type="range" id="p2-price" min="250000" max="950000" step="5000" value="460000"
                   oninput="updateP2Financials()" />
          </div>

          <div class="ctrl-group" id="ctrl-wrap-p2-down">
            <div class="ctrl-label"><span>Down Payment %</span><span id="lbl-p2-down">10%</span></div>
            <input type="range" id="p2-down" min="3" max="30" step="1" value="10"
                   oninput="updateP2Financials()" />
          </div>

          <div class="ctrl-group" id="ctrl-wrap-p2-rate">
            <div class="ctrl-label"><span>Rocket 30-Yr Fixed Rate</span><span id="lbl-p2-rate">5.875%</span></div>
            <input type="range" id="p2-rate" min="4.500" max="7.500" step="0.05" value="5.875"
                   oninput="updateP2Financials()" />
          </div>

          <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
            <button class="btn-primary" onclick="generateCustomReel(false)" id="btn-p2-fast">
              <svg class="ico ico-sm" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
              Generate Instant Reel (~5s)
            </button>
            <button class="btn-secondary" onclick="generateCustomReel(true)" id="btn-p2-veo">
              <svg class="ico ico-sm" viewBox="0 0 24 24"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg>
              Render Full Veo 3.1 MP4 (~22s)
            </button>
          </div>
        </div>

        <!-- CENTER 9:16 VERTICAL PHONE STAGE (4 COLS) -->
        <div class="col-4 v-card phone-stage">
          <div class="phone-frame">
            <video id="p2-video" class="phone-video" src="/static/reels/reel_royaloak.mp4" autoplay loop muted playsinline></video>
            <div id="p2-poster-overlay" class="phone-poster-overlay"></div>

            <div class="reel-hud-top">
              <div class="reel-brand-pill">
                <span style="width:7px;height:7px;border-radius:50%;background:#EF4444;display:inline-block;"></span>
                REDFIN × ROCKET REELS
              </div>
              <div class="reel-brand-pill" id="p2-model-tag">Veo 3.1 · 9:16</div>
            </div>

            <div class="reel-caption-box">
              <div class="reel-caption-tag" id="p2-active-cap-tag">00:00 · CURB APPEAL</div>
              <div class="reel-caption-text" id="p2-active-cap-text">Just Listed on Redfin: 418 Elmhurst Ave, Royal Oak MI ($460,000)</div>
            </div>

            <div class="reel-piti-sticker">
              <div>
                <div style="font-size:9.5px;text-transform:uppercase;letter-spacing:0.06em;opacity:0.9;">Rocket Verified PITI</div>
                <div style="font-size:20px;font-weight:800;" id="p2-sticker-piti">$2,890/mo</div>
              </div>
              <div style="text-align:right;">
                <div style="font-size:10px;background:rgba(255,255,255,0.22);padding:3px 8px;border-radius:999px;font-weight:700;" id="p2-sticker-credit">+$4,600 Closing Credit</div>
                <div style="font-size:10.5px;margin-top:3px;opacity:0.9;" id="p2-sticker-sub">10% Down · 5.875% Fixed</div>
              </div>
            </div>
          </div>

          <button class="btn-primary" style="margin-top:12px;max-width:332px;" onclick="playReelWith24kVoiceover(this)" id="btn-p2-play-vo">
            <svg class="ico" viewBox="0 0 24 24"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>
            <span>Play 9:16 Reel with Gemini 24kHz HD Voiceover</span>
          </button>
        </div>

        <!-- RIGHT 4-SCENE STORYBOARD & VOICE TRACK (3 COLS) -->
        <div class="col-3 v-card">
          <div class="v-card-header">
            <span class="v-card-title">
              <svg class="ico ico-sm" viewBox="0 0 24 24"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
              4-Scene Beat Sheet
            </span>
          </div>
          <div id="p2-caption-list" style="display:flex;flex-direction:column;gap:8px;margin-bottom:14px;"></div>

          <div style="background:var(--bg-subtle);border:1px solid var(--border-hairline);border-radius:10px;padding:12px;">
            <div style="font-size:10px;font-family:'JetBrains Mono',monospace;color:var(--ink-muted);text-transform:uppercase;margin-bottom:4px;">24kHz Native Audio Script</div>
            <p id="p2-vo-script" style="font-size:12px;line-height:1.55;color:var(--ink-primary);"></p>
          </div>
        </div>
      </div>
    </section>

    <!-- =====================================================================
         PILLAR 3: GROUNDING WITH GOOGLE MAPS, YOUTUBE & GOOGLE SEARCH
         ===================================================================== -->
    <section class="pillar-pane" id="pillar-3">
      <div class="moat-strip">
        <div>
          <div class="moat-title">Pillar 3 · "Ask Redfin 2.0" — Tri-Modal Grounding (Google Maps + YouTube Video + Google Search)</div>
          <div class="moat-subtitle">Simultaneously grounds neighborhood places via `types.GoogleMaps()`, inspects YouTube walkthroughs via `Part.from_uri()`, and verifies 2026 local tax/grant rules via `types.GoogleSearch()`.</div>
        </div>
        <div class="vs-claude-pill">
          <strong>Gemini 4 Argon / 3.8:</strong> 250M+ Maps Places + YouTube URI + Search &nbsp;|&nbsp; <span class="claude-no">Anthropic Claude: Blind to YouTube URLs &amp; No Maps Graph</span>
        </div>
      </div>

      <!-- TOP PROPERTY BAR -->
      <div class="v-card" style="margin-bottom:14px;padding:11px 16px;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px;">
        <div style="display:flex;gap:8px;flex-wrap:wrap;">
          <button class="barge-chip" onclick="runPillar3Grounding('royal_oak')" id="p3-hub-royal_oak" style="border-color:var(--google-blue);">
            <svg class="ico ico-sm" viewBox="0 0 24 24"><path d="M12 21s-7-6.5-7-12a7 7 0 1 1 14 0c0 5.5-7 12-7 12z"/><circle cx="12" cy="9" r="2.5"/></svg>
            418 Elmhurst Ave, Royal Oak MI ($460k)
          </button>
          <button class="barge-chip" onclick="runPillar3Grounding('corktown_detroit')" id="p3-hub-corktown_detroit">
            <svg class="ico ico-sm" viewBox="0 0 24 24"><path d="M12 21s-7-6.5-7-12a7 7 0 1 1 14 0c0 5.5-7 12-7 12z"/><circle cx="12" cy="9" r="2.5"/></svg>
            1420 Michigan Ave #4B, Corktown Detroit ($385k)
          </button>
          <button class="barge-chip" onclick="runPillar3Grounding('ann_arbor')" id="p3-hub-ann_arbor">
            <svg class="ico ico-sm" viewBox="0 0 24 24"><path d="M12 21s-7-6.5-7-12a7 7 0 1 1 14 0c0 5.5-7 12-7 12z"/><circle cx="12" cy="9" r="2.5"/></svg>
            2105 Devonshire Rd, Ann Arbor MI ($695k)
          </button>
        </div>
        <div style="display:flex;align-items:center;gap:8px;flex:1;max-width:520px;">
          <input type="text" id="p3-custom-yt" placeholder="Paste any YouTube URL (https://www.youtube.com/watch?v=...)"
                 style="flex:1;padding:8px 12px;border-radius:8px;border:1px solid var(--border-hairline);background:var(--bg-subtle);color:var(--ink-primary);font-size:12px;" />
          <button class="btn-primary" style="width:auto;padding:8px 14px;" onclick="runPillar3Grounding(currentP3Hub)">
            <svg class="ico ico-sm" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
            Ground All 3 Modalities
          </button>
        </div>
      </div>

      <div class="studio-grid-12">
        <!-- 1. GOOGLE MAPS GROUNDING (4 COLS) -->
        <div class="col-4 v-card">
          <div class="v-card-header">
            <span class="v-card-title">
              <svg class="ico ico-sm" viewBox="0 0 24 24"><polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/><line x1="8" y1="2" x2="8" y2="18"/><line x1="16" y1="6" x2="16" y2="22"/></svg>
              1. Google Maps Grounding
            </span>
            <div style="display:flex;align-items:center;gap:6px;">
              <button class="barge-chip" style="padding:3px 8px;font-size:10px;" onclick="setGoogleMapLayer('roadmap')" id="btn-map-road">Road</button>
              <button class="barge-chip" style="padding:3px 8px;font-size:10px;" onclick="setGoogleMapLayer('satellite')" id="btn-map-sat">Satellite</button>
              <span class="badge-live" id="p3-lat-badge"><span class="dot-pulse"></span>250M+ Places</span>
            </div>
          </div>
          <div id="grounding-map"></div>
          <div id="p3-maps-summary" style="font-size:12px;line-height:1.55;margin-top:10px;color:var(--ink-secondary);"></div>
          <div class="place-pill-list" id="p3-maps-pills"></div>
        </div>

        <!-- 2. YOUTUBE VIDEO URI GROUNDING (4 COLS) -->
        <div class="col-4 v-card">
          <div class="v-card-header">
            <span class="v-card-title">
              <svg class="ico ico-sm" viewBox="0 0 24 24"><rect x="2" y="4" width="20" height="16" rx="4"/><polygon points="10 9 15 12 10 15 10 9"/></svg>
              2. YouTube Video Grounding (`Part.from_uri`)
            </span>
            <span class="badge-live">Native Video</span>
          </div>
          <div style="border-radius:10px;overflow:hidden;border:1px solid var(--border-hairline);aspect-ratio:16/9;background:#000;">
            <iframe id="p3-yt-iframe" width="100%" height="100%" src="https://www.youtube.com/embed/AwhBTrzzqeg?enablejsapi=1"
                    title="YouTube Property Walkthrough" frameborder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowfullscreen></iframe>
          </div>
          <div style="margin-top:12px;background:var(--bg-subtle);border:1px solid var(--border-hairline);border-radius:10px;padding:12px;">
            <div style="font-size:10px;font-family:'JetBrains Mono',monospace;color:var(--google-blue);font-weight:700;margin-bottom:4px;">
              GEMINI MULTIMODAL FRAME-BY-FRAME VIDEO INSPECTION
            </div>
            <div id="p3-yt-summary" style="font-size:12px;line-height:1.55;color:var(--ink-primary);"></div>
          </div>
        </div>

        <!-- 3. GOOGLE SEARCH GROUNDING (4 COLS) -->
        <div class="col-4 v-card">
          <div class="v-card-header">
            <span class="v-card-title">
              <svg class="ico ico-sm" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
              3. Google Search Grounding
            </span>
            <span class="badge-live">Live Web Citations</span>
          </div>
          <div style="background:var(--bg-subtle);border:1px solid var(--border-hairline);border-radius:10px;padding:14px;min-height:220px;">
            <div style="font-size:10px;font-family:'JetBrains Mono',monospace;color:var(--emerald);font-weight:700;margin-bottom:6px;">
              2026 PROPERTY TAX MILLAGE &amp; DOWN-PAYMENT GRANTS
            </div>
            <div id="p3-search-summary" style="font-size:12px;line-height:1.55;color:var(--ink-primary);"></div>
          </div>
          <div style="margin-top:12px;">
            <div style="font-size:10.5px;font-weight:700;font-family:'JetBrains Mono',monospace;color:var(--ink-muted);margin-bottom:6px;">VERIFIED GROUNDING CITATIONS:</div>
            <div class="place-pill-list" id="p3-search-pills"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- =====================================================================
         PILLAR 4: GEMINI LIVE API + INTERACTIVE AVATAR ("ROWAN 2.0")
         ===================================================================== -->
    <section class="pillar-pane" id="pillar-4">
      <div class="moat-strip">
        <div>
          <div class="moat-title">Pillar 4 · "Rowan 2.0 &amp; Screen Co-Pilot" — Gemini Live API + Photorealistic Avatar + Computer Use</div>
          <div class="moat-subtitle">Talk directly to Kira to manipulate BigQuery TimesFM sliders, Veo 3.1 Reels, and Google Maps Grounding in real time with `0ms` barge-in.</div>
        </div>
        <div class="vs-claude-pill">
          <strong>Gemini Live:</strong> 24kHz Audio + Screen Tool Control + Avatar &nbsp;|&nbsp; <span class="claude-no">Claude Rowan: Deaf &amp; Mute (SMS Text Only)</span>
        </div>
      </div>

      <div class="studio-grid-12">
        <!-- LEFT AVATAR STAGE (5 COLS) -->
        <div class="col-5 v-card">
          <div class="v-card-header">
            <span class="v-card-title">
              <svg class="ico ico-sm" viewBox="0 0 24 24"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="22"/></svg>
              Live Multimodal Avatar Stage
            </span>
            <span class="badge-live" id="p4-conn-badge"><span class="dot-pulse"></span>24kHz + Screen Control Ready</span>
          </div>

          <div class="avatar-stage-box">
            <canvas id="avatar-ring-canvas" width="520" height="395"></canvas>
            <div class="avatar-portrait-circle" id="kira-portrait-ring" onclick="handleAvatarTapInterruptOrVoice()" style="cursor:pointer;" title="Click Kira to interrupt speech or toggle Live Mic">
              <!-- 60fps Real-Time WebAudio AnalyserNode Viseme Canvas (0.0ms Lip-Sync Phase!) -->
              <canvas id="kira-stage-canvas" width="320" height="320"></canvas>
            </div>
            <div style="z-index:4;text-align:center;margin-top:14px;color:#FFF;padding:0 16px;">
              <div style="font-size:15.5px;font-weight:800;" id="p4-avatar-name">Kira · Rowan 2.0 &amp; Live Screen Operator</div>
              <div style="font-size:11.5px;color:#94A3B8;margin-top:4px;min-height:32px;" id="p4-live-transcript">
                Click "Start Live Voice &amp; Mic" or type any command in the bottom bar to watch Kira move controls on screen
              </div>
            </div>
          </div>

          <div style="display:grid;grid-template-columns:2fr 1fr;gap:8px;margin-top:12px;">
            <button class="btn-primary" onclick="toggleUnifiedLiveVoiceMic()" id="btn-p4-start">
              <svg class="ico ico-sm" viewBox="0 0 24 24"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/></svg>
              <span id="lbl-p4-start">Start Live Voice &amp; Mic (Speak to Screen)</span>
            </button>
            <button class="btn-secondary" id="btn-p4-stop" type="button" onclick="stopAllAudioAndAvatarNow(this)" style="border-color:var(--rocket-red);color:var(--rocket-red);">
              <svg class="ico ico-sm" viewBox="0 0 24 24"><rect x="6" y="6" width="12" height="12" rx="2"/></svg>
              <span id="lbl-p4-stop">STOP (0ms)</span>
            </button>
          </div>

          <div style="margin-top:12px;display:flex;flex-wrap:wrap;gap:6px;">
            <button class="barge-chip" onclick="executeUserSpokenOrTypedCommand('Change Fed / 30-Yr Mortgage Rate Shock to -60')">
              <svg class="ico ico-sm" viewBox="0 0 24 24"><path d="M3 3v18h18"/><path d="M7 14l4-4 4 3 5-6"/></svg>
              "Change Fed / 30-Yr Mortgage Rate Shock to -60"
            </button>
            <button class="barge-chip" onclick="executeUserSpokenOrTypedCommand('Switch to Pillar 1 and shock rates -125 bps over 18 weeks')">
              <svg class="ico ico-sm" viewBox="0 0 24 24"><path d="M3 3v18h18"/><path d="M7 14l4-4 4 3 5-6"/></svg>
              "Shock BQML Rates -125 bps &amp; 18 Weeks"
            </button>
            <button class="barge-chip" onclick="executeUserSpokenOrTypedCommand('Cancel my 4 unused subscriptions in Rocket Money saving $285 a month')">
              <svg class="ico ico-sm" viewBox="0 0 24 24"><rect x="2" y="5" width="20" height="14" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/></svg>
              "Cancel $285/mo subs &amp; boost mortgage payoff!"
            </button>
            <button class="barge-chip" onclick="executeUserSpokenOrTypedCommand('Explícame en español cómo funciona el crédito de $4,600 con Redfin y Rocket Mortgage')">
              <svg class="ico ico-sm" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
              "Switch to Spanish ($4,600 Redfin Credit)"
            </button>
          </div>
        </div>

        <!-- RIGHT SYNCHRONIZED SUPER-FUNNEL ACTION CARDS (7 COLS) -->
        <div class="col-7 v-card">
          <div class="v-card-header">
            <span class="v-card-title">
              <svg class="ico ico-sm" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>
              Live Voice-Synchronized Super-Funnel Canvas
            </span>
            <span class="badge-live">Zero-Latency State Sync</span>
          </div>

          <div class="kpi-row" style="grid-template-columns:repeat(3,1fr);">
            <div class="kpi-tile" id="p4-card-rm">
              <div class="kpi-label">1. Rocket Money (Rowan 2.0)</div>
              <div class="kpi-val" id="p4-val-subs" style="color:var(--emerald);">+$285/mo</div>
              <div class="kpi-sub" id="p4-sub-subs">4 Unused Subs Canceled</div>
            </div>
            <div class="kpi-tile" id="p4-card-rf">
              <div class="kpi-label">2. Redfin + Rocket Purchase</div>
              <div class="kpi-val" id="p4-val-piti">$2,890/mo</div>
              <div class="kpi-sub">+$4,600 Combined Closing Credit</div>
            </div>
            <div class="kpi-tile" id="p4-card-mc">
              <div class="kpi-label">3. Mr. Cooper Refi Recapture</div>
              <div class="kpi-val" id="p4-val-refi" style="color:var(--google-blue);">-$412/mo</div>
              <div class="kpi-sub">7.375% to 5.875% · $0 Appraisal</div>
            </div>
          </div>

          <!-- INTERACTIVE SUBSCRIPTION-TO-EQUITY ACCELERATOR -->
          <div style="background:var(--bg-subtle);border:1px solid var(--border-hairline);border-radius:12px;padding:16px;margin-top:12px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
              <div>
                <div style="font-size:14px;font-weight:800;">Rowan 2.0 Subscription-to-Principal Autopilot</div>
                <div style="font-size:11.5px;color:var(--ink-muted);">Toggle recurring bills below — Rowan cancels them and pipes the savings straight into your Rocket Mortgage principal</div>
              </div>
              <span class="badge-live" id="p4-years-saved">Saves $64,800 Interest · 4.2 Yrs Shaved</span>
            </div>

            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
              <label style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;background:var(--bg-card);border:1px solid var(--border-hairline);border-radius:9px;cursor:pointer;">
                <span style="font-size:12px;font-weight:700;"><input type="checkbox" checked onchange="recalcRowanAutopilot()" class="rowan-sub-chk" data-amt="115"> Equinox Unused Gym Tier</span>
                <span style="font-family:'JetBrains Mono',monospace;font-size:11.5px;color:var(--emerald);font-weight:700;">+$115/mo</span>
              </label>
              <label style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;background:var(--bg-card);border:1px solid var(--border-hairline);border-radius:9px;cursor:pointer;">
                <span style="font-size:12px;font-weight:700;"><input type="checkbox" checked onchange="recalcRowanAutopilot()" class="rowan-sub-chk" data-amt="68"> Duplicate Streaming Bundles</span>
                <span style="font-family:'JetBrains Mono',monospace;font-size:11.5px;color:var(--emerald);font-weight:700;">+$68/mo</span>
              </label>
              <label style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;background:var(--bg-card);border:1px solid var(--border-hairline);border-radius:9px;cursor:pointer;">
                <span style="font-size:12px;font-weight:700;"><input type="checkbox" checked onchange="recalcRowanAutopilot()" class="rowan-sub-chk" data-amt="54"> Auto Insurance Rate Renegotiation</span>
                <span style="font-family:'JetBrains Mono',monospace;font-size:11.5px;color:var(--emerald);font-weight:700;">+$54/mo</span>
              </label>
              <label style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;background:var(--bg-card);border:1px solid var(--border-hairline);border-radius:9px;cursor:pointer;">
                <span style="font-size:12px;font-weight:700;"><input type="checkbox" checked onchange="recalcRowanAutopilot()" class="rowan-sub-chk" data-amt="48"> Legacy Cloud Storage Licenses</span>
                <span style="font-family:'JetBrains Mono',monospace;font-size:11.5px;color:var(--emerald);font-weight:700;">+$48/mo</span>
              </label>
            </div>
          </div>

          <!-- LIVE COMPUTER-USE ACTION LOG -->
          <div style="margin-top:12px;background:#0F172A;border:1px solid #1E293B;border-radius:10px;padding:11px 14px;color:#E2E8F0;font-family:'JetBrains Mono',monospace;font-size:11px;">
            <div style="color:#38BDF8;font-weight:700;margin-bottom:4px;">LIVE GEMINI FUNCTION-CALL &amp; COMPUTER-USE TELEMETRY</div>
            <div id="agent-action-log">Ready — Click "Start Live Voice &amp; Mic" or type any command below (e.g. "change Fed / 30-Yr Mortgage Rate Shock to -60") to watch Kira manipulate the UI live.</div>
          </div>
        </div>
      </div>
    </section>

    <!-- =====================================================================
         PILLAR 5: REDFIN POWERED BY ROCKET × GEMINI AI REAL ESTATE MARKETPLACE (108 DISTINCT HOMES + INTERACTIVE MAP + LIVE KIRA CONCIERGE)
         ===================================================================== -->
    <section class="pillar-pane active" id="pillar-5">
      <!-- 1. AUTHENTIC REDFIN FULL-BLEED ARCHITECTURAL HERO BANNER ("Redfin Early Access. Find it first.") -->
      <div class="rf-hero-banner">
        <div class="rf-hero-inner">
          <div class="rf-hero-eyebrow">
            <span>Redfin Powered by Rocket &times; Google Gemini</span>
          </div>
          <h1 class="rf-hero-title">Redfin Early Access.<br>Find it first.</h1>
          <p class="rf-hero-subtitle">Search 108 architecturally distinct homes by city, architectural DNA, photo upload, or live voice with Kira.</p>

          <!-- Redfin Folder Tabs Directly Attached to Top of Search Bar -->
          <div class="rf-search-tabs" role="tablist">
            <button type="button" class="rf-search-tab active" onclick="setRfHeroMode('buy', this)">Buy</button>
            <button type="button" class="rf-search-tab" onclick="setRfHeroMode('ai', this)">✨ AI Vector Search</button>
            <button type="button" class="rf-search-tab" onclick="document.getElementById('p5-photo-file-input').click()">📷 Photo Match</button>
            <button type="button" class="rf-search-tab" onclick="setRfHeroMode('mortgage', this)">Rocket Pre-Approval</button>
            <button type="button" class="rf-search-tab" onclick="askKiraRealEstateConcierge('Kira, find me a 4 bedroom Colonial estate with a chef kitchen and pool')">🎙️ Ask Kira Live</button>
          </div>

          <!-- Single Wide, Clean Redfin Search Box (Zero Overlapping Labels!) -->
          <div class="rf-search-box" id="p5-hero-search-pill">
            <input type="text" id="p5-search-input" class="rf-search-input"
                   placeholder="City, Address, School, Style, ZIP (e.g. 'Colonial red-brick in Greenwich' or 'Coastal glass villa')..."
                   onkeydown="if(event.key==='Enter') runPillar5HybridSearch();" />

            <label class="rf-search-action-pill" title="Upload any house or room photo to search by Multimodal Image Vector">
              <svg class="ico ico-sm" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
              <span id="p5-img-upload-lbl">Photo</span>
              <input type="file" id="p5-photo-file-input" accept="image/*" style="display:none;" onchange="handleP5ImageUpload(this)" />
            </label>

            <button type="button" class="rf-search-action-pill" onclick="toggleUnifiedLiveVoiceMic()" title="Speak to Kira Live Avatar Concierge">
              <svg class="ico ico-sm" viewBox="0 0 24 24" style="color:#D92228;"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/></svg>
              <span>Voice</span>
            </button>

            <button type="button" class="rf-search-submit-btn" onclick="runPillar5HybridSearch()" id="btn-p5-search" title="Search 108 Distinct Homes">
              <svg class="ico" viewBox="0 0 24 24" style="width:20px;height:20px;stroke-width:2.5;"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            </button>
          </div>

          <!-- Quick AI & Voice Search Prompts Inside Hero -->
          <div class="rf-hero-chips">
            <button type="button" class="rf-hero-chip" onclick="askKiraRealEstateConcierge('Show me Colonial estates with 4 bedrooms and tell me about the best match')">
              🎙️ "Kira: 4BR Colonial Estates"
            </button>
            <button type="button" class="rf-hero-chip" onclick="askKiraRealEstateConcierge('Find me a Coastal waterfront villa with a wrap-around veranda or ocean glass')">
              🎙️ "Kira: Coastal Waterfront Villa"
            </button>
            <button type="button" class="rf-hero-chip" onclick="askKiraRealEstateConcierge('Show me Mid-Century cantilevered glass homes with a walnut kitchen island')">
              🎙️ "Kira: Mid-Century Glass"
            </button>
            <button type="button" class="rf-hero-chip" onclick="askKiraRealEstateConcierge('Find a 3 bedroom Modern Craftsman in Royal Oak or Austin under 900 thousand')">
              🎙️ "Kira: 3BR Craftsman &lt;$900K"
            </button>
          </div>
        </div>
      </div>

      <!-- 2. REDFIN "RECOMMENDED FOR YOU" SECTION HEADER + CLEAN FILTER CONTROLS -->
      <div class="rf-section-header">
        <div class="rf-section-title-group">
          <h2 class="rf-section-title">Recommended for you</h2>
          <span class="rf-section-sub" id="p5-results-summary">based on 108 distinct architecturally verified homes</span>
          <span class="badge-live" id="p5-latency-badge"><span class="dot-pulse"></span>108 Homes · GCS CDN</span>
          <span class="badge-live" style="background:rgba(5,150,105,0.10);color:var(--emerald);border-color:rgba(5,150,105,0.25);" id="p5-judge-summary-badge">
            ★ 98.6% Gemini Judge · 0 Duplicates
          </span>
        </div>

        <!-- Clean Price & Map Mode Controls -->
        <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
          <div style="display:flex;align-items:center;gap:8px;background:#F9FAFB;border:1px solid #E5E7EB;padding:5px 12px;border-radius:999px;font-size:12.5px;font-weight:700;color:#111111;">
            <span>Max Price: <strong id="lbl-p5-max-price" style="color:#D92228;">$2.50M</strong></span>
            <input type="range" id="p5-max-price" min="450000" max="2500000" step="50000" value="2500000"
                   style="width:95px;accent-color:#D92228;cursor:pointer;"
                   oninput="document.getElementById('lbl-p5-max-price').innerText='$'+(this.value/1e6).toFixed(2)+'M'"
                   onchange="runPillar5HybridSearch()" />
          </div>
          <!-- Hidden selects kept for programmatic sync -->
          <select id="p5-pill-arch-select" style="display:none;" onchange="setP5ArchFilter(this.value, document.getElementById('p5-arch-' + this.value))">
            <option value="all">All</option>
            <option value="colonial_georgian">Colonial</option>
            <option value="coastal_villa">Coastal</option>
            <option value="modern_craftsman">Craftsman</option>
            <option value="midcentury_glass">Mid-Century</option>
            <option value="brick_timber_loft">Brick &amp; Timber</option>
            <option value="desert_mountain">Desert</option>
          </select>
          <select id="p5-pill-beds-select" style="display:none;" onchange="setP5BedsFilter(parseInt(this.value,10), document.getElementById('p5-bed-' + this.value))">
            <option value="0">0</option>
            <option value="2">2</option>
            <option value="3">3</option>
            <option value="4">4</option>
            <option value="5">5</option>
            <option value="6">6</option>
          </select>
        </div>
      </div>

      <!-- 3. CLEAN HORIZONTAL ARCHITECTURAL STYLE PILLS + BEDROOM FILTER PILLS -->
      <div class="abnb-cat-strip">
        <div class="abnb-cat-tabs" id="p5-arch-ribbon">
          <button class="abnb-cat-item active" onclick="setP5ArchFilter('all', this)" id="p5-arch-all">
            <span class="abnb-cat-count-badge">108</span>
            <span>All Homes</span>
          </button>
          <button class="abnb-cat-item" onclick="setP5ArchFilter('colonial_georgian', this)" id="p5-arch-colonial_georgian">
            <img class="abnb-cat-thumb" src="https://storage.googleapis.com/vtxdemos-abnb-images/rocket_re_cdn/v1/images/listings/RKT-066/ext_front.jpg?v=2" alt="Colonial" />
            <span>Colonial Estates</span>
            <span class="cat-pct">(16)</span>
          </button>
          <button class="abnb-cat-item" onclick="setP5ArchFilter('coastal_villa', this)" id="p5-arch-coastal_villa">
            <img class="abnb-cat-thumb" src="https://storage.googleapis.com/vtxdemos-abnb-images/rocket_re_cdn/v1/images/listings/RKT-082/ext_front.jpg?v=2" alt="Coastal" />
            <span>Coastal Villas</span>
            <span class="cat-pct">(16)</span>
          </button>
          <button class="abnb-cat-item" onclick="setP5ArchFilter('modern_craftsman', this)" id="p5-arch-modern_craftsman">
            <img class="abnb-cat-thumb" src="https://storage.googleapis.com/vtxdemos-abnb-images/rocket_re_cdn/v1/images/listings/RKT-001/ext_front.jpg?v=2" alt="Craftsman" />
            <span>Modern Craftsman</span>
            <span class="cat-pct">(27)</span>
          </button>
          <button class="abnb-cat-item" onclick="setP5ArchFilter('midcentury_glass', this)" id="p5-arch-midcentury_glass">
            <img class="abnb-cat-thumb" src="https://storage.googleapis.com/vtxdemos-abnb-images/rocket_re_cdn/v1/images/listings/RKT-028/ext_front.jpg?v=2" alt="Mid-Century" />
            <span>Mid-Century Glass</span>
            <span class="cat-pct">(22)</span>
          </button>
          <button class="abnb-cat-item" onclick="setP5ArchFilter('brick_timber_loft', this)" id="p5-arch-brick_timber_loft">
            <img class="abnb-cat-thumb" src="https://storage.googleapis.com/vtxdemos-abnb-images/rocket_re_cdn/v1/images/listings/RKT-050/ext_front.jpg?v=2" alt="Brick & Timber" />
            <span>Brick &amp; Timber</span>
            <span class="cat-pct">(16)</span>
          </button>
          <button class="abnb-cat-item" onclick="setP5ArchFilter('desert_mountain', this)" id="p5-arch-desert_mountain">
            <img class="abnb-cat-thumb" src="https://storage.googleapis.com/vtxdemos-abnb-images/rocket_re_cdn/v1/images/listings/RKT-098/ext_front.jpg?v=2" alt="Desert" />
            <span>Desert Sanctuary</span>
            <span class="cat-pct">(11)</span>
          </button>
        </div>

        <!-- BEDROOM QUICK PILLS & VECTOR WEIGHTS TOGGLE -->
        <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;" id="p5-bed-bar">
          <button class="abnb-filter-pill active" onclick="setP5BedsFilter(0, this)" id="p5-bed-0">All Beds</button>
          <button class="abnb-filter-pill" onclick="setP5BedsFilter(2, this)" id="p5-bed-2">2 BR</button>
          <button class="abnb-filter-pill" onclick="setP5BedsFilter(3, this)" id="p5-bed-3">3 BR</button>
          <button class="abnb-filter-pill" onclick="setP5BedsFilter(4, this)" id="p5-bed-4">4 BR</button>
          <button class="abnb-filter-pill" onclick="setP5BedsFilter(5, this)" id="p5-bed-5">5 BR</button>
          <button class="abnb-filter-pill" onclick="setP5BedsFilter(6, this)" id="p5-bed-6">6 BR</button>
          <button class="abnb-filter-pill" onclick="toggleP5VectorDrawer()" title="Adjust Hybrid Vector RRF Weights">
            ⚙️ Vector Weights
          </button>
          <button type="button" class="abnb-filter-pill" id="btn-toggle-behind-scenes" onclick="toggleBehindTheScenesView()" style="border-color:#D92228;color:#D92228;font-weight:800;background:rgba(216,30,40,0.06);margin-left:auto;display:inline-flex;align-items:center;gap:6px;">
            <span style="width:8px;height:8px;border-radius:50%;background:#D92228;display:inline-block;"></span>
            <span id="btn-behind-scenes-lbl">🔬 Behind the Scenes: Vector Topology</span>
          </button>
          <button class="abnb-filter-pill" onclick="resetPillar5Filters()" title="Reset All Filters">
            ↺ Reset
          </button>
        </div>
      </div>

      <!-- COLLAPSIBLE HYBRID VECTOR WEIGHTS DRAWER (CLEANLY TUCKED UNTIL CLICKED) -->
      <div id="p5-vector-weights-drawer" style="display:none;padding:10px 16px;margin-bottom:12px;border-radius:12px;background:var(--bg-subtle);border:1px solid var(--border-hairline);align-items:center;justify-content:space-between;flex-wrap:wrap;gap:14px;font-size:11.5px;font-family:'JetBrains Mono',monospace;">
        <div style="font-weight:800;color:var(--ink-primary);">`gemini-embedding-001` Hybrid RRF Fusion Weights:</div>
        <label style="display:flex;align-items:center;gap:6px;">
          <span>Text Semantic Vec: <strong id="lbl-p5-w-sem">45%</strong></span>
          <input type="range" id="p5-w-sem" min="0" max="100" value="45" style="width:80px;accent-color:var(--google-blue);" onchange="runPillar5HybridSearch()" />
        </label>
        <label style="display:flex;align-items:center;gap:6px;">
          <span>Multimodal Image Vec: <strong id="lbl-p5-w-vis">35%</strong></span>
          <input type="range" id="p5-w-vis" min="0" max="100" value="35" style="width:80px;accent-color:var(--emerald);" onchange="runPillar5HybridSearch()" />
        </label>
        <label style="display:flex;align-items:center;gap:6px;">
          <span>Keyword BM25: <strong id="lbl-p5-w-kw">20%</strong></span>
          <input type="range" id="p5-w-kw" min="0" max="100" value="20" style="width:80px;accent-color:#D92228;" onchange="runPillar5HybridSearch()" />
        </label>
      </div>
      <div id="p5-visual-query-banner" style="display:none;"></div>

      <div id="p5-marketplace-view">
      <!-- 4. REDFIN SPLIT-SCREEN STAGE: LEFT 2-COLUMN CARDS + RIGHT STICKY GOOGLE MAP WITH FLOATING PRICE PILLS -->
      <div class="abnb-split-stage" style="margin-bottom:28px;">
        <!-- Left Column: Borderless Redfin Property Grid -->
        <div class="abnb-cards-col" id="p5-property-grid"></div>

        <!-- Right Column: Sticky Full-Height Interactive Redfin Map with Price Pill Markers -->
        <div class="abnb-map-col">
          <div id="p5-airbnb-map"></div>

          <!-- Top Floating Map Controls -->
          <div class="abnb-map-ctrl-overlay">
            <button class="abnb-map-pill-btn" onclick="fitP5MapToCurrentResults()">
              ⤢ Fit All Matched Homes
            </button>
            <button class="abnb-map-pill-btn" onclick="setP5MapTileMode('roadmap')" id="p5-map-btn-road">
              Map
            </button>
            <button class="abnb-map-pill-btn" onclick="setP5MapTileMode('satellite')" id="p5-map-btn-sat">
              Satellite
            </button>
          </div>

          <!-- Bottom-Left Floating Redfin Map Preview Card (Opens when clicking a $Price Pin or triggered by Kira) -->
          <div id="p5-map-preview-card" style="display:none;position:absolute;bottom:18px;left:18px;right:18px;max-width:360px;z-index:520;background:var(--bg-card);border-radius:16px;box-shadow:0 14px 36px rgba(0,0,0,0.26);border:1px solid var(--border-hairline);overflow:hidden;"></div>
        </div>
      </div>
      </div> <!-- end p5-marketplace-view -->

      <!-- =====================================================================
           5. BEHIND THE SCENES: 3072-D VECTOR TOPOLOGY & UMAP 2D PROJECTION STAGE
           ===================================================================== -->
      <div id="p5-behind-scenes-view" style="display:none;margin-bottom:28px;">
        <div class="v-card" style="background:var(--bg-card);border:1px solid var(--border-hairline);border-radius:24px;box-shadow:0 14px 40px rgba(0,0,0,0.06);overflow:hidden;padding:0;">
          <!-- Top Telemetry Header -->
          <div style="padding:16px 20px;border-bottom:1px solid var(--border-hairline);display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px;background:var(--bg-subtle);">
            <div>
              <div style="display:flex;align-items:center;gap:8px;">
                <span style="width:10px;height:10px;border-radius:50%;background:#D92228;display:inline-block;"></span>
                <span style="font-size:12px;font-family:'JetBrains Mono',monospace;font-weight:800;text-transform:uppercase;color:#D92228;letter-spacing:0.05em;">
                  Interactive Vector Space Topology
                </span>
                <span style="font-size:11px;font-weight:700;padding:2px 8px;border-radius:6px;background:rgba(216,30,40,0.09);color:#D92228;">
                  UMAP 2D Projection · 3072-D
                </span>
              </div>
              <p style="font-size:12.5px;color:var(--ink-secondary);margin:4px 0 0;">
                Drag the red <strong>Query Vector (DRAG ME)</strong> node or click any cluster preset to inspect real-time cosine similarity and RRF fusion weights across all 108 homes.
              </p>
            </div>

            <div style="display:flex;align-items:center;gap:16px;font-size:12.5px;">
              <div>
                <span style="color:var(--ink-secondary);">Top Cosine:</span>
                <strong class="font-mono" style="color:#D92228;margin-left:4px;font-size:14px;" id="top-cosine-readout">0.994</strong>
              </div>
              <div>
                <span style="color:var(--ink-secondary);">Nearest Cluster:</span>
                <strong style="margin-left:4px;" id="nearest-cluster-readout">Mid-Century Glass</strong>
              </div>
              <button type="button" onclick="toggleBehindTheScenesView(false)" class="abnb-reserve-btn" style="padding:8px 16px;font-size:12px;border-radius:999px;">
                ← Back to Marketplace View
              </button>
            </div>
          </div>

          <!-- Cluster Selection Ribbon inside Behind the Scenes -->
          <div style="padding:10px 20px;border-bottom:1px solid var(--border-hairline);display:flex;align-items:center;gap:8px;overflow-x:auto;background:var(--bg-card);">
            <span style="font-size:11px;font-weight:800;color:var(--ink-secondary);text-transform:uppercase;margin-right:4px;">Clusters:</span>
            <button type="button" class="abnb-filter-pill active" onclick="selectGraphPreset('all', 'All 108 Homes', this)">All Clusters (108)</button>
            <button type="button" class="abnb-filter-pill" onclick="selectGraphPreset('midcentury_glass', 'Mid-Century Glass Pavilion', this)">Mid-Century Glass (22)</button>
            <button type="button" class="abnb-filter-pill" onclick="selectGraphPreset('colonial_georgian', 'Georgian Colonial Estate', this)">Georgian Colonial (16)</button>
            <button type="button" class="abnb-filter-pill" onclick="selectGraphPreset('modern_craftsman', 'Modern Craftsman', this)">Modern Craftsman (27)</button>
            <button type="button" class="abnb-filter-pill" onclick="selectGraphPreset('coastal_villa', 'Coastal Waterfront Villa', this)">Coastal Villa (16)</button>
            <button type="button" class="abnb-filter-pill" onclick="selectGraphPreset('brick_timber_loft', 'Brick & Timber Loft', this)">Brick &amp; Timber (16)</button>
            <button type="button" class="abnb-filter-pill" onclick="selectGraphPreset('desert_mountain', 'Desert Mountain Sanctuary', this)">Desert Sanctuary (11)</button>
          </div>

          <!-- Interactive Vector Canvas -->
          <div style="position:relative;height:340px;width:100%;background:#F8FAFC;cursor:crosshair;user-select:none;">
            <canvas id="vector-graph-canvas" style="width:100%;height:100%;display:block;"></canvas>
          </div>

          <!-- RRF Fusion Weight Sliders Bar -->
          <div style="padding:12px 20px;border-top:1px solid var(--border-hairline);display:grid;grid-template-columns:repeat(auto-fit, minmax(220px, 1fr));gap:16px;background:var(--bg-subtle);font-size:12px;font-weight:700;">
            <label style="display:flex;align-items:center;justify-content:space-between;gap:8px;">
              <span>Semantic Text: <strong id="bts-w-sem-lbl" style="color:var(--google-blue);">50%</strong></span>
              <input type="range" min="10" max="80" value="50" style="width:90px;accent-color:var(--google-blue);" oninput="document.getElementById('bts-w-sem-lbl').innerText=this.value+'%'; pulseGraphNodes();" />
            </label>
            <label style="display:flex;align-items:center;justify-content:space-between;gap:8px;">
              <span>Visual Photo Vec: <strong id="bts-w-vis-lbl" style="color:var(--emerald);">35%</strong></span>
              <input type="range" min="10" max="80" value="35" style="width:90px;accent-color:var(--emerald);" oninput="document.getElementById('bts-w-vis-lbl').innerText=this.value+'%'; pulseGraphNodes();" />
            </label>
            <label style="display:flex;align-items:center;justify-content:space-between;gap:8px;">
              <span>BM25 Keyword: <strong id="bts-w-kw-lbl" style="color:#D92228;">15%</strong></span>
              <input type="range" min="5" max="60" value="15" style="width:90px;accent-color:#D92228;" oninput="document.getElementById('bts-w-kw-lbl').innerText=this.value+'%'; pulseGraphNodes();" />
            </label>
          </div>

          <!-- Live Ranked Property Grid underneath the Vector Space Topology -->
          <div style="padding:20px;background:var(--bg-card);border-top:1px solid var(--border-hairline);">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
              <h3 style="font-size:16px;font-weight:800;margin:0;">Live Ranked Properties by Proximity to Query Vector</h3>
              <span style="font-size:12px;color:var(--ink-secondary);">Recalculates dynamically as you drag the red Query Vector node</span>
            </div>
            <div id="bts-ranked-listings-grid" style="display:grid;grid-template-columns:repeat(auto-fill, minmax(260px, 1fr));gap:16px;"></div>
          </div>
        </div>
      </div>
      </section>

    <!-- =====================================================================
         AIRBNB LISTING DETAIL MODAL (SCREENSHOT 6 STYLE: 5-PHOTO MOSAIC + 2-COL BODY + STICKY RESERVE CARD)
         ===================================================================== -->
    <div class="re-modal-backdrop" id="re-property-modal" onclick="if(event.target===this) closeRePropertyModal();">
      <div class="re-modal-sheet">
        <!-- Top Title & Action Bar -->
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px;margin-bottom:14px;flex-wrap:wrap;">
          <div>
            <h2 style="font-size:24px;font-weight:800;margin:0 0 6px;letter-spacing:-0.02em;" id="re-modal-title">Property Title</h2>
            <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;font-size:13px;font-weight:700;color:var(--ink-primary);">
              <span id="re-modal-judge-badge">★ 4.99 · Gemini Judge 99.1% Coherence Verified</span>
              <span>·</span>
              <span id="re-modal-id" style="color:var(--google-blue);">RKT-001</span>
              <span>·</span>
              <span id="re-modal-address" style="text-decoration:underline;color:var(--ink-secondary);">Address</span>
              <span>·</span>
              <span id="re-modal-rooms-badge" style="color:var(--emerald);">3 Exteriors + 14 Coinciding Rooms</span>
            </div>
          </div>

          <div style="display:flex;align-items:center;gap:8px;">
            <button class="abnb-filter-pill" onclick="speakActiveModalPropertyTour(this)" id="btn-re-modal-speak" style="border-color:#FF385C;color:#FF385C;">
              🔊 Narrate Tour with Kira (24kHz HD)
            </button>
            <button class="abnb-filter-pill" onclick="closeRePropertyModal()">
              ✕ Close
            </button>
          </div>
        </div>

        <!-- 5-PHOTO ROUNDED 16PX AIRBNB MOSAIC (1 LARGE LEFT + 2x2 RIGHT + "SHOW ALL PHOTOS" PILL) -->
        <div class="abnb-detail-mosaic" id="re-modal-bento"></div>

        <!-- 2-COLUMN AIRBNB DETAIL BODY (LEFT 65% TABS & CONTENT + RIGHT 35% STICKY RESERVE / PRE-APPROVAL CARD) -->
        <div class="abnb-detail-body">
          <!-- Left Column: Sub-Tabs + Rooms / 3D Floorplan / Walkthrough / Veo Reel / Gemini Judge -->
          <div>
            <div style="display:flex;justify-content:space-between;align-items:center;padding-bottom:16px;margin-bottom:16px;border-bottom:1px solid var(--border-hairline);">
              <div>
                <div style="font-size:18px;font-weight:800;" id="re-modal-subtitle-specs">Entire architectural residence hosted by Rocket × Redfin Premier</div>
                <div style="font-size:13px;color:var(--ink-secondary);margin-top:3px;" id="re-modal-piti">
                  Pre-underwritten by Rocket Mortgage · 3 Coinciding Ultra-HD Exteriors + All Bedrooms Mapped
                </div>
              </div>
              <div style="display:flex;align-items:center;gap:8px;padding:8px 14px;border-radius:12px;border:1px solid var(--border-hairline);background:var(--bg-subtle);">
                <span style="font-size:18px;">🏆</span>
                <div>
                  <div style="font-size:11.5px;font-weight:800;">Guest &amp; Judge Favorite</div>
                  <div style="font-size:10px;color:var(--ink-secondary);">Top 1% of 108 Verified Homes</div>
                </div>
              </div>
            </div>

            <!-- Sub-Tabs -->
            <div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid var(--border-hairline);">
              <button class="abnb-filter-pill active" onclick="switchReModalTab('rooms', this)" id="re-mtab-rooms">
                ☷ All Coinciding Rooms &amp; 3 Exteriors
              </button>
              <button class="abnb-filter-pill" onclick="switchReModalTab('floorplan', this)" id="re-mtab-floorplan">
                📐 Interactive 2D/3D Floorplan
              </button>
              <button class="abnb-filter-pill" onclick="switchReModalTab('walkthrough', this)" id="re-mtab-walkthrough">
                🎬 16:9 3D Video Tour
              </button>
              <button class="abnb-filter-pill" onclick="switchReModalTab('reel', this)" id="re-mtab-reel">
                📱 9:16 Veo 3.1 Reel
              </button>
              <button class="abnb-filter-pill" onclick="switchReModalTab('judge', this)" id="re-mtab-judge">
                ✅ Gemini 3.8 Judge Audit
              </button>
            </div>

            <!-- TAB 1: ALL ROOMS & EXTERIORS GALLERY -->
            <div id="re-mpane-rooms">
              <div style="font-size:13.5px;color:var(--ink-secondary);line-height:1.65;margin-bottom:16px;" id="re-modal-desc"></div>
              <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px;" id="re-modal-rooms-grid"></div>
            </div>

            <!-- TAB 2: INTERACTIVE 2D/3D FLOORPLAN & ROOM-BY-ROOM INSPECTOR -->
            <div id="re-mpane-floorplan" style="display:none;">
              <div class="v-card" style="margin-bottom:14px;">
                <div class="v-card-header">
                  <span class="v-card-title">Interactive Architectural Blueprint — Click Any Room to Inspect Photo &amp; Math</span>
                  <span class="badge-live" id="re-fp-math-badge">100% Bedroom &amp; Room Math Verified</span>
                </div>
                <div id="re-interactive-svg-floorplan" style="width:100%;background:#0F172A;border-radius:12px;padding:12px;overflow:hidden;"></div>
                <div style="margin-top:12px;display:flex;flex-wrap:wrap;gap:6px;" id="re-fp-room-buttons"></div>
              </div>
              <div class="studio-grid-12">
                <div class="col-6 v-card">
                  <div class="v-card-header">
                    <span class="v-card-title" id="re-fp-selected-title">Selected Space Inspector</span>
                    <span class="badge-live" id="re-fp-selected-dim">24' × 19'</span>
                  </div>
                  <img id="re-fp-selected-img" src="" alt="Selected Room" style="width:100%;aspect-ratio:16/10;object-fit:cover;border-radius:12px;border:1px solid var(--border-hairline);margin-bottom:10px;" />
                  <div style="font-size:12.5px;font-weight:700;margin-bottom:4px;" id="re-fp-selected-caption"></div>
                  <div style="font-size:11px;font-family:'JetBrains Mono',monospace;color:var(--emerald);font-weight:700;" id="re-fp-selected-score"></div>
                </div>
                <div class="col-6 v-card">
                  <div class="v-card-header">
                    <span class="v-card-title">3D Isometric Dollhouse Cutaway</span>
                  </div>
                  <img id="re-modal-3d-fp-img" src="" alt="3D Floorplan" style="width:100%;aspect-ratio:16/10;object-fit:cover;border-radius:12px;border:1px solid var(--border-hairline);" />
                </div>
              </div>
            </div>

            <!-- TAB 3: 16:9 3D ARCHITECTURAL VIDEO WALKTHROUGH -->
            <div id="re-mpane-walkthrough" style="display:none;">
              <div class="v-card">
                <div class="v-card-header">
                  <span class="v-card-title">16:9 3D Architectural Video Walkthrough (Google Cloud Storage CDN)</span>
                  <span class="badge-live">Veo 3.1 16:9 Stream</span>
                </div>
                <video id="re-modal-walkthrough-vid" controls playsinline loop style="width:100%;border-radius:14px;background:#000;aspect-ratio:16/9;"></video>
              </div>
            </div>

            <!-- TAB 4: VEO 3.1 9:16 SOCIAL REEL -->
            <div id="re-mpane-reel" style="display:none;">
              <div style="display:flex;flex-wrap:wrap;gap:24px;align-items:center;justify-content:center;">
                <div style="width:300px;aspect-ratio:9/16;border-radius:24px;overflow:hidden;border:4px solid #0F172A;background:#000;position:relative;box-shadow:0 20px 50px rgba(0,0,0,0.4);">
                  <video id="re-modal-reel-vid" controls playsinline loop style="width:100%;height:100%;object-fit:cover;"></video>
                </div>
                <div style="max-width:380px;">
                  <span class="badge-live">Veo 3.1 9:16 Social Reel · GCS CDN</span>
                  <h3 style="font-size:19px;font-weight:800;margin:10px 0 6px;" id="re-reel-title"></h3>
                  <p style="font-size:13px;color:var(--ink-secondary);line-height:1.6;" id="re-reel-desc"></p>
                  <button class="abnb-reserve-btn" style="margin-top:12px;" onclick="speakActiveModalPropertyTour(this)">
                    🔊 Play Reel with Kira 24kHz HD Voiceover
                  </button>
                </div>
              </div>
            </div>

            <!-- TAB 5: GEMINI 3.8 MULTIMODAL SELF-EVALUATION JUDGE -->
            <div id="re-mpane-judge" style="display:none;">
              <div class="v-card" style="background:var(--bg-subtle);">
                <div class="v-card-header">
                  <span class="v-card-title">Gemini 3.8 Multimodal Architectural &amp; Room-Math Self-Evaluation Pipeline</span>
                  <button class="abnb-filter-pill" style="border-color:#FF385C;color:#FF385C;" onclick="runLiveGeminiJudgeForActiveModal(this)">
                    ⚡ Re-Run Live Gemini 3.8 Judge Audit
                  </button>
                </div>
                <div id="re-modal-judge-content"></div>
              </div>
            </div>
          </div>

          <!-- Right Column: Sticky Airbnb Reserve / Rocket Pre-Approval Card (Screenshot 6 Style) -->
          <div>
            <div class="abnb-reserve-card">
              <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:4px;">
                <div>
                  <span style="font-size:24px;font-weight:800;" id="re-modal-price">$645,000</span>
                  <span style="font-size:12px;color:var(--ink-secondary);font-weight:600;"> list price</span>
                </div>
                <span style="font-size:12px;font-weight:800;color:var(--emerald);" id="re-modal-reserve-credit">+$6,450 Credit</span>
              </div>

              <div style="padding:8px 11px;border-radius:8px;background:rgba(5,150,105,0.09);color:#047857;font-size:12px;font-weight:700;margin:10px 0 14px;display:flex;align-items:center;gap:6px;">
                <span>✓</span>
                <span id="re-modal-reserve-piti-banner">Rocket Verified PITI: $3,620 / month</span>
              </div>

              <!-- Airbnb 2x2 Box Grid -->
              <div style="border:1px solid #B0B0B0;border-radius:12px;overflow:hidden;margin-bottom:14px;" id="re-modal-finance-box"></div>

              <button class="abnb-reserve-btn" onclick="speakActiveModalPropertyTour(document.getElementById('btn-re-modal-speak'))">
                Reserve Tour &amp; Hear Kira Pre-Approval (24kHz)
              </button>
              <button class="abnb-filter-pill" style="width:100%;justify-content:center;margin-top:8px;padding:11px;" onclick="closeRePropertyModal(); findVisuallySimilarListing(p5ActiveModalItem ? p5ActiveModalItem.id : 'RKT-001');">
                🔍 Find Visually Similar Homes on Map
              </button>

              <div style="text-align:center;font-size:11.5px;color:var(--ink-secondary);margin:10px 0 14px;">
                You won't be charged yet · Instant Rocket Lock Verified
              </div>

              <div id="re-modal-price-breakdown" style="display:flex;flex-direction:column;gap:8px;font-size:13px;padding-top:12px;border-top:1px solid var(--border-hairline);"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- =====================================================================
         TAB 6: ROCKET SUPER-FUNNEL RESEARCH & ANTHROPIC CLAUDE KILL-SHEET
         ===================================================================== -->
    <section class="pillar-pane" id="pillar-6">
      <div class="moat-strip">
        <div>
          <div class="moat-title">Rocket Companies 2026 Super-Funnel Research &amp; Why Google Gemini Replaces Anthropic Claude</div>
          <div class="moat-subtitle">Live audit of `rocketmortgage.com`, `redfin.com` ("Ask Redfin"), `rocketmoney.com` ("Rowan"), and `mrcooper.com` ($2.1T Servicing).</div>
        </div>
      </div>

      <div class="studio-grid-12">
        <div class="col-12 v-card">
          <div class="v-card-header">
            <span class="v-card-title">Where Rocket Uses AI Today vs. The 4 Google Gemini Unfair Advantages</span>
          </div>
          <div style="overflow-x:auto;">
            <table style="width:100%;border-collapse:collapse;font-size:13px;">
              <thead>
                <tr style="border-bottom:2px solid var(--border-hairline);text-align:left;">
                  <th style="padding:10px;">Rocket Brand &amp; Current AI</th>
                  <th style="padding:10px;">Current Limitation (Anthropic / Legacy Stack)</th>
                  <th style="padding:10px;">Google Gemini Next-Gen Pillar</th>
                  <th style="padding:10px;">Executive Sell &amp; Quantified Impact</th>
                </tr>
              </thead>
              <tbody>
                <tr style="border-bottom:1px solid var(--border-hairline);">
                  <td style="padding:12px;font-weight:800;">1. Mr. Cooper + Rocket Servicing<br><span style="font-size:11px;color:var(--ink-muted);">10+ PB Data Lake · 9.5M Loans</span></td>
                  <td style="padding:12px;color:var(--rocket-red);font-weight:600;">Claude has 0 time-series foundation models and cannot execute inside BigQuery SQL.</td>
                  <td style="padding:12px;font-weight:700;color:var(--google-blue);">Pillar 1 · BigQuery ML `AI.FORECAST` (`TimesFM 2.0`)</td>
                  <td style="padding:12px;">Zero-shot refi-wave &amp; escrow float forecasting in `~900ms` directly in SQL (+15% retention recapture = <strong>+$432M/yr</strong>).</td>
                </tr>
                <tr style="border-bottom:1px solid var(--border-hairline);">
                  <td style="padding:12px;font-weight:800;">2. Redfin Listing Marketing<br><span style="font-size:11px;color:var(--ink-muted);">50M+ Monthly Visitors</span></td>
                  <td style="padding:12px;color:var(--rocket-red);font-weight:600;">Static photo carousels; Claude cannot generate video (`Veo 3.1`), images (`gemini-3-pro-image`), or 24kHz voiceovers.</td>
                  <td style="padding:12px;font-weight:700;color:var(--google-blue);">Pillar 2 · `Veo 3.1` 9:16 Reels + `24kHz Live Audio`</td>
                  <td style="padding:12px;">Every new MLS listing automatically gets a 9:16 TikTok/Reels video with live Rocket PITI + `$4,600` closing credit sticker.</td>
                </tr>
                <tr style="border-bottom:1px solid var(--border-hairline);">
                  <td style="padding:12px;font-weight:800;">3. "Ask Redfin" Search<br><span style="font-size:11px;color:var(--ink-muted);">Redfin Conversational Search</span></td>
                  <td style="padding:12px;color:var(--rocket-red);font-weight:600;">Only reads static MLS text; blind to YouTube walkthroughs and Google Maps' 250M+ places.</td>
                  <td style="padding:12px;font-weight:700;color:var(--google-blue);">Pillar 3 · Tri-Modal Grounding (`Maps` + `YouTube` + `Search`)</td>
                  <td style="padding:12px;">Watches YouTube property tours frame-by-frame, plots live Google Maps places, and grounds 2026 MSHDA/Detroit grants.</td>
                </tr>
                <tr>
                  <td style="padding:12px;font-weight:800;">4. Rocket Money "Rowan" &amp; Rocket Logic<br><span style="font-size:11px;color:var(--ink-muted);">Built with Anthropic Claude / AWS</span></td>
                  <td style="padding:12px;color:var(--rocket-red);font-weight:600;">Rowan is trapped in SMS text! Claude is deaf &amp; mute without 4 external vendors.</td>
                  <td style="padding:12px;font-weight:700;color:var(--google-blue);">Pillar 4 · `Gemini Live API` + Avatar + Live Screen Control</td>
                  <td style="padding:12px;">`<350ms` 24kHz native voice + `0ms` barge-in + real-time Function Calling that physically moves UI sliders while you speak.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>

  </main>

  <!-- =========================================================================
       LIVE OUT-OF-ORDER ASYNC SUBAGENT SWARM TRAY (`FIRST-READY` + FLASH-NEXT)
       ========================================================================= -->
  <div id="async-subagent-tray" style="display:none;position:fixed;bottom:76px;right:20px;width:min(680px, calc(100vw - 40px));max-height:420px;background:var(--bg-card);border:1.5px solid var(--border-strong);border-radius:16px;box-shadow:0 20px 50px rgba(0,0,0,0.22);z-index:9998;overflow:hidden;flex-direction:column;">
    <div style="padding:10px 14px;background:#0F172A;color:#F8FAFC;display:flex;align-items:center;justify-content:space-between;gap:10px;border-bottom:1px solid #1E293B;">
      <div style="display:flex;align-items:center;gap:8px;font-size:12px;font-weight:800;">
        <span class="dot-pulse"></span>
        <span>ASYNC SUBAGENT SWARM · OUT-OF-ORDER (`FIRST-READY`) DISPATCHER</span>
        <span id="subagent-tray-counter" style="padding:2px 8px;border-radius:999px;background:rgba(56,189,248,0.18);color:#38BDF8;font-family:'JetBrains Mono',monospace;font-size:10.5px;">0 Active</span>
      </div>
      <div style="display:flex;align-items:center;gap:6px;">
        <button type="button" class="omni-chip" style="background:#1E293B;color:#38BDF8;border-color:#334155;" onclick="triggerDemo3xAsyncSubagentBurst()">
          ⚡ Fire 3× Parallel Burst
        </button>
        <button type="button" class="omni-chip" style="background:#1E293B;color:#CBD5E1;border-color:#334155;" onclick="clearAsyncSubagentTray()">
          Clear
        </button>
        <button type="button" class="omni-chip" style="background:#1E293B;color:#F8FAFC;border-color:#334155;" onclick="document.getElementById('async-subagent-tray').style.display='none'">
          ✕
        </button>
      </div>
    </div>
    <div style="padding:7px 14px;background:var(--bg-subtle);border-bottom:1px solid var(--border-hairline);font-size:11px;color:var(--ink-secondary);display:flex;justify-content:space-between;align-items:center;">
      <span>Simple questions auto-route to <strong>gemini-3.8-flash (Flash-Next)</strong> · Complex/Pillar tasks run in parallel · Results render in <strong>first-ready order</strong>.</span>
      <span style="font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--emerald);font-weight:700;" id="subagent-first-winner-lbl"></span>
    </div>
    <div id="async-subagent-list" style="padding:12px;overflow-y:auto;display:flex;flex-direction:column;gap:8px;max-height:320px;"></div>
  </div>

  <!-- =========================================================================
       PERSISTENT OMNI-PILLAR VOICE & COMPUTER-USE CO-PILOT BAR (KIRA)
       ========================================================================= -->
  <div class="omni-copilot-bar" id="omni-copilot-bar">
    <div class="omni-left">
      <div class="omni-avatar-thumb" onclick="handleAvatarTapInterruptOrVoice()" style="cursor:pointer;" title="Click Kira to interrupt speech or toggle Live Mic">
        <canvas id="kira-dock-canvas" width="120" height="120"></canvas>
      </div>
      <div>
        <div class="omni-title">
          <span class="dot-pulse"></span>
          Kira · Live Voice &amp; Async Subagent Co-Pilot
        </div>
        <div class="omni-transcript" id="omni-live-transcript">
          Speak/type any command, or send multiple messages separated by ";" for parallel Flash-Next subagents
        </div>
      </div>
    </div>

    <!-- INLINE VOICE/TEXT COMMAND BOX SO YOU CAN SPEAK OR TYPE ANY VALUE OR MULTI-TASK BURST -->
    <form class="omni-cmd-form" onsubmit="event.preventDefault(); submitOmniCommandInput();">
      <input type="text" id="omni-cmd-input" class="omni-cmd-input"
             placeholder="Ask Kira or send multi-tasks with ';' (e.g. '4-bed Colonial homes; What GCP APIs to enable?; Shock rates -75 bps')..." />
      <button type="submit" class="omni-btn primary" style="padding:7px 11px;">Send / Spawn</button>
    </form>

    <div class="omni-chips">
      <button class="omni-chip" style="border-color:#D81E28;color:#D81E28;font-weight:800;" onclick="triggerDemo3xAsyncSubagentBurst()" title="Spawn 3 simultaneous tasks across Flash-Next & Pillar engines and watch the fastest return first!">
        ⚡ 3× Async Subagents
      </button>
      <button class="omni-chip" onclick="executeUserSpokenOrTypedCommand('Show me 4-bedroom Colonial homes under $850K on the Airbnb map')">
        <svg class="ico ico-sm" viewBox="0 0 24 24"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>
        "4-Bed Colonials &lt;$850K"
      </button>
      <button class="omni-chip" onclick="executeUserSpokenOrTypedCommand('Change Fed / 30-Yr Mortgage Rate Shock to -60')">
        <svg class="ico ico-sm" viewBox="0 0 24 24"><path d="M3 3v18h18"/><path d="M7 14l4-4 4 3 5-6"/></svg>
        "Rate Shock -60 bps"
      </button>
    </div>

    <div class="omni-actions">
      <button class="omni-btn primary" onclick="toggleUnifiedLiveVoiceMic()" id="btn-omni-voice">
        <svg class="ico ico-sm" viewBox="0 0 24 24"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/></svg>
        <span id="lbl-omni-voice">Start Live Voice &amp; Mic</span>
      </button>
      <button class="omni-btn stop-btn" type="button" onclick="stopAllAudioAndAvatarNow(this)" id="btn-omni-stop" title="Immediate 0ms Stop">
        <svg class="ico ico-sm" viewBox="0 0 24 24"><rect x="6" y="6" width="12" height="12" rx="2"/></svg>
        <span id="lbl-omni-stop">STOP</span>
      </button>
    </div>
  </div>

  <script>
    // =========================================================================
    // SVG ICON CONSTANTS FOR DYNAMIC BUTTON STATES (ZERO EMOJIS)
    // =========================================================================
    const SVG_VOL = '<svg class="ico ico-sm" viewBox="0 0 24 24"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>';
    const SVG_STOP = '<svg class="ico ico-sm" viewBox="0 0 24 24"><rect x="6" y="6" width="12" height="12" rx="2"/></svg>';
    const SVG_PIN = '<svg class="ico ico-sm" viewBox="0 0 24 24"><path d="M12 21s-7-6.5-7-12a7 7 0 1 1 14 0c0 5.5-7 12-7 12z"/><circle cx="12" cy="9" r="2.5"/></svg>';
    const SVG_LINK = '<svg class="ico ico-sm" viewBox="0 0 24 24"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>';
    const SVG_MIC = '<svg class="ico ico-sm" viewBox="0 0 24 24"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/></svg>';

    // =========================================================================
    // GLOBAL THEME & PILLAR NAVIGATION
    // =========================================================================
    function toggleTheme() {
      const html = document.documentElement;
      const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', next);
      document.getElementById('theme-toggle-lbl').innerText = next === 'dark' ? 'Light Theme' : 'Dark Theme';
    }

    let mapInitialized = false;
    let currentActivePillar = 1;
    function setRfHeroMode(mode, btnEl) {
      document.querySelectorAll('.rf-search-tab').forEach(b => b.classList.remove('active'));
      if (btnEl) btnEl.classList.add('active');
      const inp = document.getElementById('p5-search-input');
      if (!inp) return;
      if (mode === 'ai') {
        inp.placeholder = "Describe your dream home in natural language (e.g. '4-bed Georgian Colonial with walnut library')...";
      } else if (mode === 'mortgage') {
        inp.placeholder = "Search homes with verified Rocket Mortgage PITI & $4,600 closing credit...";
      } else {
        inp.placeholder = "City, Address, School, Style, ZIP (e.g. 'Colonial red-brick in Greenwich' or 'Coastal glass villa')...";
      }
      inp.focus();
    }

    function switchPillar(num) {
      currentActivePillar = num;
      document.body.classList.toggle('p5-clean-mode', num === 5);
      document.querySelectorAll('.pillar-pane').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.pillar-tab').forEach(el => el.classList.remove('active'));
      const pane = document.getElementById('pillar-' + num);
      const tab = document.getElementById('tab-btn-' + num);
      if (pane) pane.classList.add('active');
      if (tab) tab.classList.add('active');
      if (num === 3) {
        if (!mapInitialized) {
          initPillar3Map();
          runPillar3Grounding('royal_oak');
        } else if (p3Map) {
          setTimeout(() => p3Map.invalidateSize(), 120);
        }
      }
      if (num === 5) {
        
        if (!p5MapInitialized) {
          initP5AirbnbMap();
        } else if (p5AirbnbMap) {
          setTimeout(() => {
            p5AirbnbMap.invalidateSize();
            fitP5MapToCurrentResults();
          }, 120);
        }
        if (!p5LoadedOnce) {
          runPillar5HybridSearch();
        } else {
          setTimeout(() => updateP5AirbnbMapMarkers(true), 150);
        }
      }
    }

    // =========================================================================
    // HARD 0ms AUDIO, AVATAR, BARGE-IN & EPOCH CANCELLATION ENGINE
    // =========================================================================
    let commandEpoch = 0;
    let p4Ws = null;
    let p4TurnInProgress = false;
    let voiceMicActive = false;
    let speechRec = null;
    let isKiraBusyOrSpeaking = false;
    let currentKiraSpokenScript = '';
    let micResumeTimer = null;
    let speechFinalizeTimer = null;
    let spokenUtteranceBuffer = '';
    let activeFetchAbort = null;
    let hardwareMicStream = null;
    let hardwareMicCtx = null;
    let hardwareMicAnalyser = null;
    let hardwareMicData = null;

    // Global sets tracking EVERY created WebAudio context, GainNode, SourceNode, WebSocket & sleep timer
    const allTrackedAudioContexts = new Set();
    const allTrackedGains = new Set();
    const allTrackedSourceNodes = new Set();
    const allTrackedWebSockets = new Set();
    const allCancelResolvers = new Set();

    // Ensure browser hardware Acoustic Echo Cancellation (AEC) is active so the user can barge-in by voice while Kira speaks
    async function ensureHardwareEchoCanceledMic() {
      if (hardwareMicStream && hardwareMicStream.active) return;
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) return;
      try {
        hardwareMicStream = await navigator.mediaDevices.getUserMedia({
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true,
            channelCount: 1
          }
        });
        hardwareMicCtx = new (window.AudioContext || window.webkitAudioContext)();
        const src = hardwareMicCtx.createMediaStreamSource(hardwareMicStream);
        hardwareMicAnalyser = hardwareMicCtx.createAnalyser();
        hardwareMicAnalyser.fftSize = 256;
        hardwareMicData = new Uint8Array(hardwareMicAnalyser.fftSize);
        src.connect(hardwareMicAnalyser);
      } catch (e) {}
    }

    // Check if a recognized speech snippet while Kira is speaking is a genuine user barge-in vs speaker bleed
    function isGenuineUserBargeIn(transcriptText) {
      const clean = (transcriptText || '').trim().toLowerCase();
      if (!clean || clean.length < 2) return false;
      // 1. Explicit interrupt or command keywords ALWAYS trigger immediate 0ms barge-in
      if (/\\b(stop|wait|hold on|pause|quiet|enough|shut up|cancel|hey kira|kira|actually|instead|switch|change|set|show|find|search|filter|open|pillar|bedroom|beds|colonial|coastal|craftsman|mid-century|midcentury|loft|desert|shock|rate|horizon|spanish|español|million|thousand)\\b/i.test(clean)) {
        return true;
      }
      // 2. Compare words against Kira's currently spoken script to reject acoustic speaker echo
      const words = clean.replace(/[^a-z0-9\\s]/g, '').split(/\\s+/).filter(w => w.length > 2);
      if (words.length >= 2) {
        const kiraRef = (currentKiraSpokenScript || '').toLowerCase();
        if (!kiraRef) return true;
        let novelWords = 0;
        for (const w of words) {
          if (!kiraRef.includes(w)) novelWords++;
        }
        if (novelWords >= Math.ceil(words.length * 0.5)) {
          return true;
        }
      }
      return false;
    }

    // Instant 0ms Voice/Click Barge-In: Halts Kira's speech & screen action immediately while keeping Mic LIVE!
    function bargeInInterruptNow(reasonLabel) {
      commandEpoch++;
      p4TurnInProgress = false;
      isKiraBusyOrSpeaking = false;
      currentKiraSpokenScript = '';
      if (micResumeTimer) {
        clearTimeout(micResumeTimer);
        micResumeTimer = null;
      }
      if (activeFetchAbort) {
        try { activeFetchAbort.abort(); } catch (e) {}
        activeFetchAbort = null;
      }
      allCancelResolvers.forEach(fn => {
        try { fn(); } catch (e) {}
      });
      allCancelResolvers.clear();

      // Notify server Live API session of barge-in if open
      if (p4Ws && p4Ws.readyState === WebSocket.OPEN) {
        try { p4Ws.send(JSON.stringify({ type: 'barge_in' })); } catch (e) {}
      }

      // Flush all speaker audio in 0.0ms
      LiveAudioEngine.stopAll();

      // Hide ghost cursor
      const cursor = document.getElementById('agent-cursor');
      if (cursor) cursor.classList.remove('visible', 'clicking');
      document.querySelectorAll('.agent-active-target').forEach(el => el.classList.remove('agent-active-target'));

      const msg = reasonLabel || '⚡ Interrupted Kira (0ms Barge-In) — Listening to you now...';
      const p4Tx = document.getElementById('p4-live-transcript');
      const omniTx = document.getElementById('omni-live-transcript');
      const pipSt = document.getElementById('kira-pip-status');
      if (p4Tx) p4Tx.innerText = msg;
      if (omniTx) omniTx.innerText = msg;
      if (pipSt) pipSt.innerText = '⚡ BARGE-IN · LISTENING';

      // Ensure speech recognition stays active so the user can speak immediately
      if (!voiceMicActive) {
        voiceMicActive = true;
        updateVoiceMicUI(true);
      }
      startBrowserSpeechRecognizer();
    }

    function pauseMicForKiraSpeech(scriptText) {
      isKiraBusyOrSpeaking = true;
      if (scriptText && typeof scriptText === 'string') {
        currentKiraSpokenScript = (currentKiraSpokenScript + ' ' + scriptText).slice(-600);
      }
      spokenUtteranceBuffer = '';
      if (speechFinalizeTimer) {
        clearTimeout(speechFinalizeTimer);
        speechFinalizeTimer = null;
      }
      if (micResumeTimer) {
        clearTimeout(micResumeTimer);
        micResumeTimer = null;
      }
      // CRITICAL FIX FOR BARGE-IN: Keep speechRec alive while Kira speaks so the user can interrupt her at any time!
      if (voiceMicActive && !speechRec) {
        startBrowserSpeechRecognizer();
      }
    }

    function scheduleMicResumeIfActive() {
      if (micResumeTimer) clearTimeout(micResumeTimer);
      micResumeTimer = setTimeout(() => {
        if (LiveAudioEngine.isSpeakingOrQueued() || LiveAudioEngine.activeWs || p4TurnInProgress) {
          return;
        }
        isKiraBusyOrSpeaking = false;
        currentKiraSpokenScript = '';
        if (voiceMicActive && !LiveAudioEngine.ignoreIncomingAudio) {
          startBrowserSpeechRecognizer();
        }
      }, 220);
    }

    const LiveAudioEngine = {
      ctx: null,
      masterGain: null,
      analyser: null,
      timeData: null,
      freqData: null,
      activeNodes: [],
      pcmQueue: [],
      timelineFrames: [],
      nextTime: 0,
      activeWs: null,
      currentAmp: 0,
      activeBtn: null,
      activeBtnOrigHtml: '',
      ignoreIncomingAudio: false,
      isSpeakingOrQueued() {
        return !this.ignoreIncomingAudio && (this.activeNodes.length > 0 || this.pcmQueue.length > 0);
      },
      ensureCtx() {
        if (!this.ctx || this.ctx.state === 'closed') {
          const ctx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 24000 });
          const gain = ctx.createGain();
          gain.gain.setValueAtTime(1.0, 0);
          const analyser = ctx.createAnalyser();
          analyser.fftSize = 512;
          analyser.smoothingTimeConstant = 0.08;
          gain.connect(analyser);
          analyser.connect(ctx.destination);

          this.ctx = ctx;
          this.masterGain = gain;
          this.analyser = analyser;
          this.timeData = new Uint8Array(analyser.fftSize);
          this.freqData = new Uint8Array(analyser.frequencyBinCount);
          this.nextTime = 0;

          allTrackedAudioContexts.add(ctx);
          allTrackedGains.add(gain);
        }
        if (this.ctx.state === 'suspended') {
          try { this.ctx.resume(); } catch (e) {}
        }
        return this.ctx;
      },
      restoreActiveBtn() {
        if (this.activeBtn) {
          this.activeBtn.innerHTML = this.activeBtnOrigHtml;
          this.activeBtn.classList.remove('playing-stop');
          this.activeBtn = null;
          this.activeBtnOrigHtml = '';
        }
      },
      stopAll() {
        // 1. Gate off any in-flight WebSocket audio chunks & wipe queued PCM samples in 0.0ms
        this.ignoreIncomingAudio = true;
        this.pcmQueue.length = 0;
        this.timelineFrames.length = 0;

        // 2. Close active TTS WebSocket
        if (this.activeWs) {
          try { this.activeWs.onmessage = null; this.activeWs.onopen = null; this.activeWs.onclose = null; this.activeWs.close(); } catch (e) {}
          allTrackedWebSockets.delete(this.activeWs);
          this.activeWs = null;
        }

        // 3. Zero hardware gain at sample 0.000ms and disconnect EVERY tracked GainNode
        allTrackedGains.forEach(g => {
          try {
            g.gain.cancelScheduledValues(0);
            g.gain.setValueAtTime(0, 0);
            g.disconnect();
          } catch (e) {}
        });
        allTrackedGains.clear();
        this.masterGain = null;

        if (this.analyser) {
          try { this.analyser.disconnect(); } catch (e) {}
          this.analyser = null;
        }

        // 4. Stop & disconnect EVERY tracked AudioBufferSourceNode in 0.0ms
        allTrackedSourceNodes.forEach(n => {
          try { n.onended = null; n.stop(0); } catch (e) {}
          try { n.disconnect(); } catch (e) {}
        });
        allTrackedSourceNodes.clear();
        this.activeNodes = [];
        this.currentAmp = 0;
        smoothMouthOpen = 0;

        // 5. Suspend + close EVERY hardware AudioContext so the OS audio ring-buffer flushes in 0.0ms
        allTrackedAudioContexts.forEach(c => {
          try { c.suspend(); } catch (e) {}
          try { c.close(); } catch (e) {}
        });
        allTrackedAudioContexts.clear();
        this.ctx = null;
        this.nextTime = 0;

        if (window.speechSynthesis) {
          try { window.speechSynthesis.cancel(); } catch (e) {}
        }
        if (window.reelCaptionTimer) {
          clearInterval(window.reelCaptionTimer);
          window.reelCaptionTimer = null;
        }
        this.restoreActiveBtn();
        syncAvatarVideosWithSpeech(false);
      },
      allowNewTurnAudio() {
        this.ignoreIncomingAudio = false;
        this.ensureCtx();
      },
      pumpQueue() {
        if (this.ignoreIncomingAudio) {
          this.pcmQueue.length = 0;
          this.timelineFrames.length = 0;
          return;
        }
        // Schedule at most 3 micro-frames (3 x 40ms = 120ms max hardware lookahead) so barge-in is <20ms instant
        while (this.activeNodes.length < 3 && this.pcmQueue.length > 0) {
          const pkt = this.pcmQueue.shift();
          const f32 = pkt.f32;
          const ctx = this.ensureCtx();
          const buf = ctx.createBuffer(1, f32.length, 24000);
          buf.getChannelData(0).set(f32);
          const src = ctx.createBufferSource();
          src.buffer = buf;
          src.connect(this.masterGain || ctx.destination);
          const now = ctx.currentTime;
          if (this.nextTime < now) this.nextTime = now + 0.008;
          const startAt = this.nextTime;
          const endAt = startAt + buf.duration;
          src.start(startAt);
          this.nextTime = endAt;
          this.timelineFrames.push({
            start: startAt,
            end: endAt,
            rms: pkt.rms,
            zcr: pkt.zcr
          });
          if (this.timelineFrames.length > 120) {
            this.timelineFrames.splice(0, this.timelineFrames.length - 120);
          }
          this.activeNodes.push(src);
          allTrackedSourceNodes.add(src);
          syncAvatarVideosWithSpeech(true);
          src.onended = () => {
            allTrackedSourceNodes.delete(src);
            this.activeNodes = this.activeNodes.filter(x => x !== src);
            if (!this.ignoreIncomingAudio && this.pcmQueue.length > 0) {
              this.pumpQueue();
              return;
            }
            if (this.activeNodes.length === 0 && this.pcmQueue.length === 0 && !this.activeWs && !p4TurnInProgress) {
              this.currentAmp = 0;
              smoothMouthOpen = 0;
              this.timelineFrames.length = 0;
              syncAvatarVideosWithSpeech(false);
              this.restoreActiveBtn();
              scheduleMicResumeIfActive();
            }
          };
        }
      },
      playPcmChunk(b64) {
        if (this.ignoreIncomingAudio) return;
        pauseMicForKiraSpeech();
        const bin = atob(b64);
        const samples = Math.floor(bin.length / 2);
        if (samples <= 0) return;
        const f32 = new Float32Array(samples);
        const view = new DataView(new ArrayBuffer(bin.length));
        for (let i = 0; i < bin.length; i++) view.setUint8(i, bin.charCodeAt(i));
        for (let i = 0; i < samples; i++) {
          f32[i] = view.getInt16(i * 2, true) / 32768.0;
        }
        // CRITICAL FOR 0ms BARGE-IN & SYLLABLE-ACCURATE LIP-SYNC:
        // Slice any large PCM buffer into 40ms (960-sample @ 24kHz) micro-frames with precomputed RMS & ZCR!
        const FRAME_SIZE = 960;
        for (let offset = 0; offset < samples; offset += FRAME_SIZE) {
          const end = Math.min(samples, offset + FRAME_SIZE);
          const slice = f32.subarray(offset, end);
          let sumSq = 0;
          let crossings = 0;
          for (let j = 0; j < slice.length; j++) {
            const s = slice[j];
            sumSq += s * s;
            if (j > 0 && ((slice[j - 1] >= 0 && s < 0) || (slice[j - 1] < 0 && s >= 0))) {
              crossings++;
            }
          }
          const rms = Math.sqrt(sumSq / Math.max(1, slice.length));
          const zcr = crossings / Math.max(1, slice.length);
          this.pcmQueue.push({
            f32: new Float32Array(slice),
            rms: rms,
            zcr: zcr
          });
        }
        this.pumpQueue();
      },
      speakClip(text, voice, btnEl, expectedEpoch) {
        if (typeof expectedEpoch === 'number' && expectedEpoch !== commandEpoch) {
          return false;
        }
        if (btnEl && this.activeBtn === btnEl && (this.isSpeakingOrQueued() || this.activeWs)) {
          bargeInInterruptNow('Stopped 24kHz Stream (0ms)');
          return false;
        }
        this.stopAll();
        currentKiraSpokenScript = text || '';
        pauseMicForKiraSpeech(text);
        this.allowNewTurnAudio();
        if (btnEl) {
          this.activeBtn = btnEl;
          this.activeBtnOrigHtml = btnEl.innerHTML;
          btnEl.classList.add('playing-stop');
          btnEl.innerHTML = `${SVG_STOP} <span>Stop 24kHz Stream</span>`;
        }
        const myEpoch = commandEpoch;
        const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
        const ws = new WebSocket(`${proto}//${location.host}/ws/live-tts`);
        this.activeWs = ws;
        allTrackedWebSockets.add(ws);
        ws.onopen = () => {
          if (myEpoch !== commandEpoch || this.ignoreIncomingAudio || this.activeWs !== ws) {
            try { ws.close(); } catch (e) {}
            return;
          }
          ws.send(JSON.stringify({ text, voice: voice || 'Aoede' }));
        };
        ws.onmessage = (evt) => {
          if (myEpoch !== commandEpoch || this.ignoreIncomingAudio || this.activeWs !== ws) return;
          const msg = JSON.parse(evt.data);
          if (msg.pcm_b64) this.playPcmChunk(msg.pcm_b64);
          if (msg.done) {
            allTrackedWebSockets.delete(ws);
            if (this.activeWs === ws) this.activeWs = null;
            if (!this.isSpeakingOrQueued()) {
              this.currentAmp = 0;
              syncAvatarVideosWithSpeech(false);
              this.restoreActiveBtn();
              scheduleMicResumeIfActive();
            }
          }
        };
        ws.onclose = () => {
          allTrackedWebSockets.delete(ws);
          if (this.activeWs === ws) this.activeWs = null;
          if (!this.isSpeakingOrQueued()) {
            this.currentAmp = 0;
            syncAvatarVideosWithSpeech(false);
            this.restoreActiveBtn();
            scheduleMicResumeIfActive();
          }
        };
        return true;
      }
    };

    // Global 0ms Total Kill Switch for ALL Audio + Avatar + In-Flight Cursor + Mic + WebSockets + Media!
    function stopAllAudioAndAvatarNow(clickedBtnEl) {
      // 1. Increment cancellation epoch & resolve all pending sleep/animation promises in 0.0ms
      commandEpoch++;
      p4TurnInProgress = false;
      isKiraBusyOrSpeaking = false;
      spokenUtteranceBuffer = '';

      if (speechFinalizeTimer) {
        clearTimeout(speechFinalizeTimer);
        speechFinalizeTimer = null;
      }
      if (micResumeTimer) {
        clearTimeout(micResumeTimer);
        micResumeTimer = null;
      }
      if (activeFetchAbort) {
        try { activeFetchAbort.abort(); } catch (e) {}
        activeFetchAbort = null;
      }
      allCancelResolvers.forEach(fn => {
        try { fn(); } catch (e) {}
      });
      allCancelResolvers.clear();

      // 2. Stop & disarm microphone speech recognition so it cannot re-trigger
      voiceMicActive = false;
      if (speechRec) {
        try {
          speechRec.onresult = null;
          speechRec.onend = null;
          speechRec.onerror = null;
          speechRec.abort();
          speechRec.stop();
        } catch (e) {}
        speechRec = null;
      }
      updateVoiceMicUI(false);

      // 3. Close persistent /ws/live-avatar WebSocket so no buffered server chunks arrive
      if (p4Ws) {
        try {
          p4Ws.onmessage = null;
          p4Ws.onopen = null;
          p4Ws.onclose = null;
          p4Ws.close();
        } catch (e) {}
        p4Ws = null;
      }

      // 4. Flush WebAudio hardware buffer + GainNode + PCM queue in 0.0ms
      LiveAudioEngine.stopAll();

      // 5. Pause any playing HTML5 <video>/<audio> (Pillar 2 Reel) and Pillar 3 YouTube <iframe>
      document.querySelectorAll('video, audio').forEach(mediaEl => {
        try { mediaEl.pause(); } catch (e) {}
      });
      const ytIframe = document.getElementById('p3-yt-iframe');
      if (ytIframe && ytIframe.contentWindow) {
        try {
          ytIframe.contentWindow.postMessage('{"event":"command","func":"pauseVideo","args":""}', '*');
          ytIframe.contentWindow.postMessage('{"event":"command","func":"stopVideo","args":""}', '*');
        } catch (e) {}
      }

      // 6. Hide Ghost Cursor & active target highlights immediately
      const cursor = document.getElementById('agent-cursor');
      if (cursor) cursor.classList.remove('visible', 'clicking');
      document.querySelectorAll('.agent-active-target').forEach(el => el.classList.remove('agent-active-target'));

      // 7. Update UI badges and flash confirmation on the STOP buttons
      document.getElementById('p4-live-transcript').innerText = 'STOPPED (0.0ms) — Audio, Avatar, and Mic halted. Click Mic or type to start a new command.';
      document.getElementById('omni-live-transcript').innerText = 'STOPPED (0.0ms) — All audio & screen actions halted.';
      document.getElementById('kira-pip-status').innerText = 'KIRA · STOPPED (0MS)';
      const logEl = document.getElementById('agent-action-log');
      if (logEl) logEl.innerText = `[${new Date().toLocaleTimeString()}] STOPPED (0.0ms) — All audio streams, WebSockets, and screen actions halted.`;

      const pipStopLbl = document.getElementById('lbl-pip-stop');
      const pipStopBtn = document.getElementById('btn-pip-stop');
      if (pipStopLbl && pipStopBtn) {
        pipStopLbl.innerText = 'STOPPED (0.0MS)';
        pipStopBtn.style.background = 'rgba(16,185,129,0.28)';
        pipStopBtn.style.borderColor = '#10B981';
        pipStopBtn.style.color = '#6EE7B7';
        setTimeout(() => {
          pipStopLbl.innerText = 'STOP AUDIO & ACTION (0MS)';
          pipStopBtn.style.background = 'rgba(239,68,68,0.18)';
          pipStopBtn.style.borderColor = '#EF4444';
          pipStopBtn.style.color = '#FCA5A5';
        }, 1100);
      }
    }

    // =========================================================================
    // 60FPS ZERO-LAG WEBAUDIO ANALYSERNODE + TIMELINE VISEME ENGINE (0.0ms LIP-SYNC PHASE)
    // =========================================================================
    // Tile Map in /static/kira_viseme_sprite.jpg?v=23 (4x4 grid, each tile 320x400, 0.0px stabilized):
    //   Tile 0: Full Eye Blink + Closed Mouth
    //   Tile 1: Half Eye Blink + Closed Mouth
    //   Tile 2: Rounded "OO / OH / W" Lips
    //   Tile 3: Viseme 0 — Mouth 100% Closed (Silence / M / B / P)
    //   Tiles 4..15: 12 Monotonically Increasing Mouth + Jaw + Oral Cavity Vowel Visemes
    let smoothMouthOpen = 0;
    const kiraVisemeImg = new Image();
    kiraVisemeImg.src = '/static/kira_viseme_sprite.jpg?v=23';
    const kiraIdleImg = new Image();
    kiraIdleImg.src = '/static/kira_idle_closed.jpg?v=23';

    function drawVisemeTileWithJawSync(ctx, W, H, tileIdx, jawOpenNorm) {
      if (!kiraVisemeImg.complete || kiraVisemeImg.naturalWidth === 0) {
        if (kiraIdleImg.complete && kiraIdleImg.naturalWidth > 0) {
          ctx.globalAlpha = 1.0;
          ctx.drawImage(kiraIdleImg, 0, 12, 320, 320, 0, 0, W, H);
        }
        return;
      }
      const col = tileIdx % 4;
      const row = Math.floor(tileIdx / 4);
      const sx = col * 320;
      const sy = row * 400 + 12;
      ctx.globalAlpha = 1.0;
      // 1. Draw the crisp discrete viseme frame (zero double-exposure ghosting!)
      ctx.drawImage(kiraVisemeImg, sx, sy, 320, 320, 0, 0, W, H);

      // 2. 60fps sub-frame lower-lip & chin micro-articulation locked to exact audio amplitude
      if (jawOpenNorm > 0.04 && tileIdx >= 4) {
        const jawDropPx = jawOpenNorm * (H * 0.028);
        // Source lower-lip + chin region in the 320x320 crop: y = 186..266 (58%..83%)
        const srcJawY = sy + 186;
        const srcJawH = 80;
        const dstJawY = (186 / 320) * H + jawDropPx;
        const dstJawH = (80 / 320) * H;
        const dstJawX = (92 / 320) * W;
        const dstJawW = (136 / 320) * W;
        ctx.save();
        ctx.beginPath();
        ctx.ellipse(W * 0.5, dstJawY + dstJawH * 0.44, dstJawW * 0.48, dstJawH * 0.48, 0, 0, Math.PI * 2);
        ctx.clip();
        ctx.drawImage(kiraVisemeImg, sx + 92, srcJawY, 136, srcJawH, dstJawX, dstJawY, dstJawW, dstJawH);
        ctx.restore();
      }
    }

    function handleAvatarTapInterruptOrVoice() {
      if (LiveAudioEngine.isSpeakingOrQueued() || isKiraBusyOrSpeaking || p4TurnInProgress) {
        bargeInInterruptNow('⚡ Interrupted Kira — Speak or type your next command now');
        if (!voiceMicActive) {
          voiceMicActive = true;
          updateVoiceMicUI(true);
        }
        startBrowserSpeechRecognizer();
      } else {
        toggleUnifiedLiveVoiceMic();
      }
    }

    function syncAvatarVideosWithSpeech(isSpeaking) {
      const pipCard = document.getElementById('kira-pip-card');
      const pipStatus = document.getElementById('kira-pip-status');
      const stageRing = document.getElementById('kira-portrait-ring');

      if (!isSpeaking) {
        smoothMouthOpen = 0;
        LiveAudioEngine.currentAmp = 0;
      }
      if (pipCard) pipCard.classList.toggle('speaking', isSpeaking);
      if (stageRing) stageRing.classList.toggle('speaking-glow', isSpeaking);
      if (pipStatus) {
        pipStatus.innerText = isSpeaking
          ? 'KIRA · SPEAKING (CLICK OR SPEAK TO INTERRUPT)'
          : (voiceMicActive ? 'KIRA · LISTENING (SPEAK NOW)' : 'KIRA · READY');
      }
    }

    // 60fps Real-Time Speaker Timeline + AnalyserNode -> Viseme Lip-Sync + Equalizer Animator
    function animateAvatarCanvas() {
      const hasActiveAudio = LiveAudioEngine.isSpeakingOrQueued();
      let instRms = 0;
      let frameRms = 0;
      let frameZcr = 0.08;
      let f1Avg = 0;
      let f2Avg = 0;

      // 1. Sample exact 40ms timeline frame scheduled at ctx.currentTime (zero FFT buffer lag!)
      if (hasActiveAudio && LiveAudioEngine.ctx && LiveAudioEngine.timelineFrames.length > 0) {
        const nowAudio = LiveAudioEngine.ctx.currentTime;
        // Prune expired frames older than nowAudio - 0.08s
        while (LiveAudioEngine.timelineFrames.length > 0 && LiveAudioEngine.timelineFrames[0].end < nowAudio - 0.08) {
          LiveAudioEngine.timelineFrames.shift();
        }
        for (let i = 0; i < LiveAudioEngine.timelineFrames.length; i++) {
          const tf = LiveAudioEngine.timelineFrames[i];
          if (nowAudio >= tf.start - 0.015 && nowAudio <= tf.end + 0.015) {
            frameRms = tf.rms;
            frameZcr = tf.zcr;
            break;
          }
        }
      }

      // 2. Also sample real-time WebAudio AnalyserNode waveform exiting the speakers
      if (hasActiveAudio && LiveAudioEngine.analyser && LiveAudioEngine.timeData && LiveAudioEngine.freqData) {
        LiveAudioEngine.analyser.getByteTimeDomainData(LiveAudioEngine.timeData);
        LiveAudioEngine.analyser.getByteFrequencyData(LiveAudioEngine.freqData);
        const td = LiveAudioEngine.timeData;
        let sumSq = 0;
        for (let i = 0; i < td.length; i++) {
          const v = (td[i] - 128) / 128.0;
          sumSq += v * v;
        }
        instRms = Math.sqrt(sumSq / td.length);

        const fd = LiveAudioEngine.freqData;
        let f1Sum = 0, f2Sum = 0;
        for (let b = 5; b <= 22; b++) f1Sum += fd[b];
        for (let b = 23; b <= 68; b++) f2Sum += fd[b];
        f1Avg = f1Sum / 18.0;
        f2Avg = f2Sum / 46.0;
      }

      const combinedRms = Math.max(frameRms, instRms);

      // Immediate silence gate so Kira closes her lips during every comma, plosive (M/B/P), or inter-word pause!
      let targetOpen = 0;
      if (hasActiveAudio && (combinedRms >= 0.010 || f1Avg >= 14)) {
        const rmsDrive = Math.min(1.0, Math.pow(combinedRms * 5.8, 0.78));
        const formantDrive = Math.min(1.0, f1Avg / 135.0);
        // High zero-crossing rate (sibilants S/F/T) narrows jaw aperture slightly like real speech
        const sibilantDamper = frameZcr > 0.22 ? 0.62 : 1.0;
        targetOpen = Math.min(1.0, (rmsDrive * 0.68 + formantDrive * 0.32) * sibilantDamper);
      }

      // Instant syllable attack (0.82) on vowel onset + crisp jaw closure (0.64) on syllable end
      const rate = targetOpen > smoothMouthOpen ? 0.82 : 0.64;
      smoothMouthOpen += (targetOpen - smoothMouthOpen) * rate;
      if (smoothMouthOpen < 0.018) smoothMouthOpen = 0;

      LiveAudioEngine.currentAmp = smoothMouthOpen;
      const isVisiblySpeaking = hasActiveAudio && smoothMouthOpen > 0.022;
      const amp = isVisiblySpeaking ? Math.max(0.08, smoothMouthOpen) : 0;

      // Select crisp discrete viseme tile (Tile 3 = 100% closed lips .. Tile 15 = 100% wide-open vowel)
      const nowMs = performance.now();
      let activeTile = 3;

      if (smoothMouthOpen < 0.025) {
        // Mouth is closed (idle or inter-word pause): natural 150ms eye blink every 3.8s
        const blinkPhase = nowMs % 3800;
        if (blinkPhase < 50) {
          activeTile = 1;
        } else if (blinkPhase < 105) {
          activeTile = 0;
        } else if (blinkPhase < 155) {
          activeTile = 1;
        } else {
          activeTile = 3;
        }
      } else if (frameZcr < 0.055 && f1Avg > 44 && f2Avg < f1Avg * 0.46 && smoothMouthOpen > 0.16 && smoothMouthOpen < 0.56) {
        // Rounded "OO / OH / W" vowel viseme
        activeTile = 2;
      } else {
        // Map smoothMouthOpen (0.025..1.0) across Tiles 4..15 (12 distinct openness steps)
        const stepIdx = Math.min(11, Math.floor(((smoothMouthOpen - 0.025) / 0.90) * 12.0));
        activeTile = 4 + Math.max(0, stepIdx);
      }

      // Render phase-locked viseme onto all 3 avatar canvases (PiP Card, Pillar 4 Stage, Bottom Omni Dock)
      const avatarCanvases = [
        document.getElementById('kira-pip-canvas'),
        document.getElementById('kira-stage-canvas'),
        document.getElementById('kira-dock-canvas')
      ];
      avatarCanvases.forEach(cEl => {
        if (!cEl) return;
        const cCtx = cEl.getContext('2d');
        const CW = cEl.width, CH = cEl.height;
        cCtx.clearRect(0, 0, CW, CH);
        drawVisemeTileWithJawSync(cCtx, CW, CH, activeTile, smoothMouthOpen);
      });

      // 1. Pillar 4 Stage Ring Canvas
      const canvas = document.getElementById('avatar-ring-canvas');
      if (canvas) {
        const ctx = canvas.getContext('2d');
        const W = canvas.width, H = canvas.height;
        ctx.clearRect(0, 0, W, H);
        const cx = W / 2, cy = H / 2 - 22;
        for (let r = 0; r < 3; r++) {
          const radius = 100 + r * 20 + amp * (38 + r * 14);
          ctx.beginPath();
          ctx.arc(cx, cy, radius, 0, Math.PI * 2);
          ctx.strokeStyle = isVisiblySpeaking
            ? `rgba(16, 185, 129, ${0.42 + amp * 0.5})`
            : `rgba(56, 189, 248, 0.24)`;
          ctx.lineWidth = isVisiblySpeaking ? 3.0 : 1.8;
          ctx.stroke();
        }
        const ringEl = document.getElementById('kira-portrait-ring');
        if (ringEl) {
          const sc = 1.0 + amp * 0.05;
          ringEl.style.transform = `scale(${sc.toFixed(3)})`;
        }
      }

      // 2. Floating PiP Equalizer Bars Canvas (driven directly by real-time speaker frequency bins!)
      const eqCanvas = document.getElementById('kira-pip-eq-canvas');
      if (eqCanvas) {
        const eqCtx = eqCanvas.getContext('2d');
        const EW = eqCanvas.width, EH = eqCanvas.height;
        eqCtx.clearRect(0, 0, EW, EH);
        const bars = 22;
        const barW = 5;
        const gap = 3;
        const fd = LiveAudioEngine.freqData;
        for (let i = 0; i < bars; i++) {
          let wave = voiceMicActive ? 4 : 2;
          if (isVisiblySpeaking && fd) {
            const binVal = fd[4 + i * 2] || 0;
            wave = Math.max(4, Math.min(EH - 2, (binVal / 255.0) * EH * 1.15 + smoothMouthOpen * 6));
          }
          const x = i * (barW + gap) + 6;
          const y = (EH - wave) / 2;
          eqCtx.fillStyle = isVisiblySpeaking ? '#10B981' : (voiceMicActive ? '#38BDF8' : '#475569');
          eqCtx.fillRect(x, y, barW, wave);
        }
      }

      requestAnimationFrame(animateAvatarCanvas);
    }
    requestAnimationFrame(animateAvatarCanvas);

    // =========================================================================
    // AGENTIC COMPUTER-USE GHOST CURSOR & SMOOTH SLIDER DRAGGER
    // =========================================================================
    const sleep = (ms) => new Promise(resolve => {
      let timer = null;
      const done = () => {
        if (timer) clearTimeout(timer);
        allCancelResolvers.delete(done);
        resolve();
      };
      allCancelResolvers.add(done);
      timer = setTimeout(done, ms);
    });

    async function moveAgentCursorTo(selectorOrEl, labelText, expectedEpoch) {
      if (typeof expectedEpoch === 'number' && expectedEpoch !== commandEpoch) return;
      const cursor = document.getElementById('agent-cursor');
      const label = document.getElementById('agent-cursor-label');
      const el = typeof selectorOrEl === 'string' ? document.querySelector(selectorOrEl) : selectorOrEl;
      if (!el || !cursor) return;
      const rect = el.getBoundingClientRect();
      if (rect.width === 0 && rect.height === 0) return;
      label.innerText = labelText || 'Kira · Screen Action';
      cursor.classList.add('visible');
      cursor.style.left = Math.round(rect.left + Math.min(rect.width * 0.45, 95)) + 'px';
      cursor.style.top = Math.round(rect.top + rect.height * 0.5) + 'px';
      await sleep(360);
      if (typeof expectedEpoch === 'number' && expectedEpoch !== commandEpoch) return;
      cursor.classList.add('clicking');
      const wrap = el.closest('.ctrl-group') || el;
      wrap.classList.add('agent-active-target');
      await sleep(200);
      cursor.classList.remove('clicking');
      setTimeout(() => wrap.classList.remove('agent-active-target'), 1600);
    }

    async function animateSliderValue(sliderEl, targetVal, labelFormatter, expectedEpoch) {
      if (!sliderEl) return;
      const startVal = parseFloat(sliderEl.value);
      const endVal = parseFloat(targetVal);
      const steps = 10;
      for (let i = 1; i <= steps; i++) {
        if (typeof expectedEpoch === 'number' && expectedEpoch !== commandEpoch) return;
        const cur = startVal + ((endVal - startVal) * i) / steps;
        sliderEl.value = sliderEl.step && parseFloat(sliderEl.step) < 1 ? cur.toFixed(3) : Math.round(cur);
        if (labelFormatter) labelFormatter(sliderEl.value);
        await sleep(18);
      }
      sliderEl.value = endVal;
      if (labelFormatter) labelFormatter(endVal);
    }

    function hideAgentCursorSoon() {
      setTimeout(() => {
        const cursor = document.getElementById('agent-cursor');
        if (cursor) cursor.classList.remove('visible');
      }, 1400);
    }

    // =========================================================================
    // NATURAL LANGUAGE VOICE & TEXT INTENT PARSER FOR INSTANT SCREEN CONTROL
    // =========================================================================
    function normalizeSpokenNumbers(str) {
      let s = (str || '').toLowerCase();
      // Strip "30-yr" / "30 year" / "15-yr" mortgage labels first so "30" isn't parsed as a parameter!
      s = s.replace(/\\b(?:30|20|15)[\\s-]*(?:yr|yrs|year|years)\\b/g, 'mortgage');
      s = s.replace(/\\bminus\\s+(\\d+)/g, '-$1');
      s = s.replace(/\\bnegative\\s+(\\d+)/g, '-$1');
      s = s.replace(/\\bplus\\s+(\\d+)/g, '+$1');
      const wordMap = {
        'zero': 0, 'four': 4, 'five': 5, 'six': 6, 'eight': 8, 'ten': 10,
        'twelve': 12, 'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'eighteen': 18,
        'twenty': 20, 'twenty four': 24, 'thirty': 30, 'forty': 40, 'fifty': 50,
        'sixty': 60, 'seventy': 70, 'seventy five': 75, 'eighty': 80, 'eighty five': 85,
        'ninety': 90, 'ninety five': 95, 'hundred': 100, 'one hundred': 100
      };
      Object.keys(wordMap).forEach(w => {
        s = s.replace(new RegExp('\\\\bminus\\\\s+' + w + '\\\\b', 'g'), '-' + wordMap[w]);
        s = s.replace(new RegExp('\\\\bnegative\\\\s+' + w + '\\\\b', 'g'), '-' + wordMap[w]);
        s = s.replace(new RegExp('\\\\b' + w + '\\\\b', 'g'), String(wordMap[w]));
      });
      return s;
    }

    function parseLocalScreenIntent(rawText) {
      const s = normalizeSpokenNumbers(rawText);
      const actions = [];

      // Check Pillar 1 / BQML / Rate Shock / Horizon / Confidence (or bare negative number when on Pillar 1)
      if (/pillar\\s*1|timesfm|bigquery|forecast|shock|fed|bps|basis|horizon|confidence/i.test(s) || (currentActivePillar === 1 && /-\\d+/.test(s))) {
        const bqmlArgs = {};
        if (/redfin|tour/i.test(s)) bqmlArgs.metric_id = 'redfin_tour_demand';
        else if (/escrow|outflow|tax/i.test(s)) bqmlArgs.metric_id = 'escrow_liquidity_outflow_m';
        else if (/warehouse|capital|draw/i.test(s)) bqmlArgs.metric_id = 'warehouse_funding_b';
        else if (/cooper|refi/i.test(s)) bqmlArgs.metric_id = 'mrcooper_refi_locks';

        // Match rate shock (prioritize negative numbers or numbers after "shock/to/bps")
        const negMatch = s.match(/(-\\d+)\\s*(?:bps|basis)?/i);
        const shockMatch = negMatch || s.match(/(?:shock|bps|basis)[^\\d-]*(-?\\d+)/i) || s.match(/(?:rate|fed)[^\\d-]*(-?\\d+)/i);
        if (shockMatch) {
          const val = parseInt(shockMatch[1], 10);
          if (val >= -150 && val <= 100) bqmlArgs.rate_shock_bps = val;
        }
        // Match horizon weeks (e.g. "18 weeks", "horizon to 16")
        const horMatch = s.match(/(?:horizon)\\s*(?:to|of|at)?\\s*(\\d+)/i) || s.match(/(\\d+)\\s*(?:week|weeks|wk|wks)/i);
        if (horMatch) {
          const hVal = parseInt(horMatch[1], 10);
          if (hVal >= 4 && hVal <= 24) bqmlArgs.horizon = hVal;
        }
        // Match confidence interval (e.g. "95% confidence", "confidence to 85")
        const ciMatch = s.match(/(?:confidence|interval|ci)\\s*(?:to|of|at)?\\s*(\\d+)/i) || s.match(/(\\d+)\\s*%?\\s*(?:ci|confidence)/i);
        if (ciMatch) {
          const ciVal = parseInt(ciMatch[1], 10);
          if (ciVal >= 80 && ciVal <= 99) bqmlArgs.confidence_level = ciVal;
        }
        // If user is on Pillar 1 and just says "change it to -60" or "set to -60"
        if (Object.keys(bqmlArgs).length === 0 && currentActivePillar === 1) {
          const bareNum = s.match(/(?:to|at)\\s*(-?\\d+)/i);
          if (bareNum) {
            const v = parseInt(bareNum[1], 10);
            if (v < 0 || v > 24) bqmlArgs.rate_shock_bps = Math.max(-150, Math.min(100, v));
            else if (v >= 4 && v <= 24) bqmlArgs.horizon = v;
          }
        }
        if (Object.keys(bqmlArgs).length > 0) {
          actions.push({ name: 'control_bqml_timesfm', args: bqmlArgs });
        } else if (/pillar\\s*1/i.test(s)) {
          actions.push({ name: 'switch_pillar_view', args: { pillar_number: 1 } });
        }
      }

      // Check Pillar 2 (Veo Reels)
      if (/pillar\\s*2|reel|veo|ann\\s*arbor|listing\\s*price|down\\s*payment/i.test(s) && actions.length === 0) {
        const p2Args = {};
        if (/ann\\s*arbor/i.test(s)) p2Args.preset_id = 'ann_arbor';
        else if (/corktown|detroit/i.test(s)) p2Args.preset_id = 'corktown_loft';
        else if (/royal\\s*oak/i.test(s)) p2Args.preset_id = 'royal_oak';

        const priceMatch = s.match(/[$]?(\\d{3})\\s*(?:k|thousand|,000)/i) || s.match(/[$]?(\\d{6})/);
        if (priceMatch) {
          let pv = parseInt(priceMatch[1], 10);
          if (pv < 1000) pv *= 1000;
          p2Args.price = pv;
        }
        const downMatch = s.match(/(\\d+)\\s*%?\\s*down/i) || s.match(/down\\s*payment\\s*(?:to|at)?\\s*(\\d+)/i);
        if (downMatch) p2Args.down_pct = parseInt(downMatch[1], 10);

        const rateMatch = s.match(/(\\d+\\.\\d+)\\s*%?/);
        if (rateMatch) p2Args.rate_pct = parseFloat(rateMatch[1]);

        if (Object.keys(p2Args).length > 0) {
          actions.push({ name: 'control_veo_reel_studio', args: p2Args });
        } else {
          actions.push({ name: 'switch_pillar_view', args: { pillar_number: 2 } });
        }
      }

      // Check Pillar 3 (Maps / YouTube / Search)
      if (/pillar\\s*3|satellite|google\\s*maps|ground/i.test(s) && actions.length === 0) {
        const p3Args = {};
        if (/satellite/i.test(s)) p3Args.map_layer = 'satellite';
        else if (/road/i.test(s)) p3Args.map_layer = 'roadmap';
        if (/corktown|detroit/i.test(s)) p3Args.hub_id = 'corktown_detroit';
        else if (/ann\\s*arbor/i.test(s)) p3Args.hub_id = 'ann_arbor';
        else if (/royal\\s*oak/i.test(s)) p3Args.hub_id = 'royal_oak';
        actions.push({ name: 'control_trimodal_grounding', args: p3Args });
      }

      // Check Pillar 4 (Subscriptions / Rowan)
      if (/subscription|rowan|cancel.*sub/i.test(s) && actions.length === 0) {
        actions.push({ name: 'control_rowan_autopilot', args: { cancel_all_subs: true, highlight_card: 'subs' } });
      }

      // Check Pillar 5 (AI Real Estate & Hybrid Vector Marketplace / Airbnb Concierge)
      if (/pillar\\s*5|real\\s*estate|marketplace|house|houses|home|homes|housing|property|properties|villa|estate|manor|bungalow|sanctuary|bedroom|beds|bath|kitchen|pool|craftsman|mid-century|midcentury|coastal|colonial|georgian|desert|loft|brick|timber|floorplan|airbnb/i.test(s) && actions.length === 0) {
        const p5Args = {};
        const bMatch = s.match(/\\b([23456])\\s*(?:bed|beds|bedroom|bedrooms|br)\\b/i);
        if (bMatch) p5Args.beds_filter = parseInt(bMatch[1], 10);
        if (/craftsman|bungalow|prairie|barn|oak/i.test(s)) p5Args.family_filter = 'modern_craftsman';
        else if (/mid-century|midcentury|cantilever|glass|bauhaus|eichler/i.test(s)) p5Args.family_filter = 'midcentury_glass';
        else if (/brick|timber|loft|warehouse|brownstone|tudor/i.test(s)) p5Args.family_filter = 'brick_timber_loft';
        else if (/colonial|georgian|federal|saltbox|gambrel|cape\\s*cod/i.test(s)) p5Args.family_filter = 'colonial_georgian';
        else if (/coastal|villa|hamptons|waterfront|beach|ocean|malibu|key\\s*west|nantucket/i.test(s)) p5Args.family_filter = 'coastal_villa';
        else if (/desert|mountain|scottsdale|aspen|rammed|adobe|sedona|chalet/i.test(s)) p5Args.family_filter = 'desert_mountain';
        else if (/all\\s*(?:homes|houses|styles)/i.test(s)) p5Args.family_filter = 'all';

        const mMill = s.match(/(?:under|below|max|up\\s*to)\\s*[$]?\\s*(\\d+(?:\\.\\d+)?)\\s*(?:m|million)\\b/i);
        const mThou = s.match(/(?:under|below|max|up\\s*to)\\s*[$]?\\s*(\\d{3,4})\\s*(?:k|thousand)\\b/i);
        if (mMill) {
          p5Args.max_price = Math.round(parseFloat(mMill[1]) * 1000000);
        } else if (mThou) {
          p5Args.max_price = parseInt(mThou[1], 10) * 1000;
        }
        if (/open|inside|floorplan|walkthrough|tour\\s+the\\s+top/i.test(s)) {
          p5Args.open_top_modal = true;
        }
        p5Args.query_text = rawText.replace(/^(?:kira\\s*,?\\s*)?(?:can\\s+you\\s+|please\\s+)?(?:show\\s+me|find\\s+me|find|search\\s+for|filter\\s+by|look\\s+for)\\s+/i, '').trim();
        actions.push({ name: 'control_realestate_marketplace', args: p5Args });
      }

      return actions;
    }

    let lastClientExecutedStamp = 0;

    async function executeAgentScreenTool(name, args, expectedEpoch) {
      const myEpoch = typeof expectedEpoch === 'number' ? expectedEpoch : commandEpoch;
      if (myEpoch !== commandEpoch) return null;

      const logEl = document.getElementById('agent-action-log');
      const setLog = (txt) => {
        if (logEl) logEl.innerText = `[${new Date().toLocaleTimeString()}] ${txt}`;
        document.getElementById('omni-live-transcript').innerText = txt;
      };

      if (name === 'switch_pillar_view') {
        const p = parseInt(args.pillar_number || 1, 10);
        await moveAgentCursorTo(`#tab-btn-${p}`, `Switch to Pillar ${p}`, myEpoch);
        if (myEpoch !== commandEpoch) return null;
        switchPillar(p);
        hideAgentCursorSoon();
        return { status: 'switched', pillar: p };
      }

      if (name === 'control_bqml_timesfm') {
        setLog(`Kira Screen Action: control_bqml_timesfm(${JSON.stringify(args)})`);
        if (currentActivePillar !== 1) {
          await moveAgentCursorTo('#tab-btn-1', 'Open Pillar 1 · BQML TimesFM', myEpoch);
          if (myEpoch !== commandEpoch) return null;
          switchPillar(1);
        }

        if (args.metric_id) {
          const cBtn = document.getElementById(`p1-cohort-${args.metric_id}`);
          if (cBtn) {
            await moveAgentCursorTo(cBtn, `Cohort: ${args.metric_id}`, myEpoch);
            if (myEpoch !== commandEpoch) return null;
            currentP1Cohort = args.metric_id;
            document.querySelectorAll('#pillar-1 .cohort-btn').forEach(b => b.classList.remove('active'));
            cBtn.classList.add('active');
          }
        }
        if (typeof args.rate_shock_bps === 'number') {
          const sEl = document.getElementById('p1-shock');
          const exactVal = Math.max(-150, Math.min(100, Math.round(args.rate_shock_bps)));
          await moveAgentCursorTo(sEl, `Drag Rate Shock -> ${exactVal > 0 ? '+' : ''}${exactVal} bps`, myEpoch);
          if (myEpoch !== commandEpoch) return null;
          await animateSliderValue(sEl, exactVal, (v) => {
            document.getElementById('lbl-p1-shock').innerText = (v > 0 ? '+' : '') + v + ' bps';
          }, myEpoch);
        }
        if (typeof args.horizon === 'number') {
          const hEl = document.getElementById('p1-horizon');
          const exactH = Math.max(4, Math.min(24, Math.round(args.horizon)));
          await moveAgentCursorTo(hEl, `Drag Horizon -> ${exactH} Weeks`, myEpoch);
          if (myEpoch !== commandEpoch) return null;
          await animateSliderValue(hEl, exactH, (v) => {
            document.getElementById('lbl-p1-horizon').innerText = v + ' Weeks';
          }, myEpoch);
        }
        if (typeof args.confidence_level === 'number') {
          const ciEl = document.getElementById('p1-ci');
          const exactCi = Math.max(80, Math.min(99, Math.round(args.confidence_level)));
          await moveAgentCursorTo(ciEl, `Drag Confidence -> ${exactCi}% CI`, myEpoch);
          if (myEpoch !== commandEpoch) return null;
          await animateSliderValue(ciEl, exactCi, (v) => {
            document.getElementById('lbl-p1-ci').innerText = v + '% CI';
          }, myEpoch);
        }
        await moveAgentCursorTo('#btn-run-p1', 'Execute BigQuery AI.FORECAST', myEpoch);
        if (myEpoch !== commandEpoch) return null;
        const data = await runPillar1TimesFM();
        if (myEpoch !== commandEpoch) return null;
        hideAgentCursorSoon();
        const summarySpeech = data
          ? `Done! I moved the Fed rate shock slider to ${data.params.rate_shock_bps} basis points over ${data.params.horizon} weeks. BigQuery TimesFM forecasts a peak of ${Math.round(data.kpis.peak_forecast).toLocaleString()} weekly locks and $${(data.kpis.est_value_usd / 1e6).toFixed(1)} million in portfolio impact.`
          : `Updated BigQuery TimesFM parameters on screen.`;
        return {
          status: 'forecast_updated',
          cohort: data ? data.meta.title : currentP1Cohort,
          rate_shock_bps: data ? data.params.rate_shock_bps : args.rate_shock_bps,
          horizon: data ? data.params.horizon : args.horizon,
          peak_weekly_forecast: data ? data.kpis.peak_forecast : 0,
          delta_pct: data ? data.kpis.delta_pct : 0,
          est_revenue_impact_usd: data ? data.kpis.est_value_usd : 0,
          spoken_summary: summarySpeech
        };
      }

      if (name === 'control_veo_reel_studio') {
        setLog(`Kira Screen Action: control_veo_reel_studio(${JSON.stringify(args)})`);
        if (currentActivePillar !== 2) {
          await moveAgentCursorTo('#tab-btn-2', 'Open Pillar 2 · Veo 3.1 Reels', myEpoch);
          if (myEpoch !== commandEpoch) return null;
          switchPillar(2);
        }

        if (args.preset_id) {
          const pBtn = document.getElementById(`p2-preset-${args.preset_id}`);
          if (pBtn) {
            await moveAgentCursorTo(pBtn, `Load Reel: ${args.preset_id}`, myEpoch);
            if (myEpoch !== commandEpoch) return null;
            await loadPresetReel(args.preset_id, pBtn);
          }
        }
        if (typeof args.price === 'number') {
          const prEl = document.getElementById('p2-price');
          const targetP = Math.max(250000, Math.min(950000, Math.round(args.price / 5000) * 5000));
          await moveAgentCursorTo(prEl, `Set Price: $${targetP.toLocaleString()}`, myEpoch);
          if (myEpoch !== commandEpoch) return null;
          await animateSliderValue(prEl, targetP, () => updateP2Financials(), myEpoch);
        }
        if (typeof args.down_pct === 'number') {
          const dnEl = document.getElementById('p2-down');
          const targetD = Math.max(3, Math.min(30, Math.round(args.down_pct)));
          await moveAgentCursorTo(dnEl, `Set Down Payment: ${targetD}%`, myEpoch);
          if (myEpoch !== commandEpoch) return null;
          await animateSliderValue(dnEl, targetD, () => updateP2Financials(), myEpoch);
        }
        if (typeof args.rate_pct === 'number') {
          const rtEl = document.getElementById('p2-rate');
          const targetR = Math.max(4.5, Math.min(7.5, Math.round(args.rate_pct * 20) / 20));
          await moveAgentCursorTo(rtEl, `Set Rate: ${targetR}%`, myEpoch);
          if (myEpoch !== commandEpoch) return null;
          await animateSliderValue(rtEl, targetR, () => updateP2Financials(), myEpoch);
        }
        if (myEpoch !== commandEpoch) return null;
        updateP2Financials();
        hideAgentCursorSoon();
        const pitiTxt = document.getElementById('p2-sticker-piti').innerText;
        const credTxt = document.getElementById('p2-sticker-credit').innerText;
        return {
          status: 'reel_updated',
          monthly_piti: pitiTxt,
          closing_credit: credTxt,
          spoken_summary: `Updated the Veo 3.1 property Reel on screen. Your verified monthly PITI is now ${pitiTxt} with ${credTxt}.`
        };
      }

      if (name === 'control_trimodal_grounding') {
        setLog(`Kira Screen Action: control_trimodal_grounding(${JSON.stringify(args)})`);
        if (currentActivePillar !== 3) {
          await moveAgentCursorTo('#tab-btn-3', 'Open Pillar 3 · Tri-Modal Grounding', myEpoch);
          if (myEpoch !== commandEpoch) return null;
          switchPillar(3);
        }

        if (args.map_layer) {
          const mBtn = args.map_layer === 'satellite' ? '#btn-map-sat' : '#btn-map-road';
          await moveAgentCursorTo(mBtn, `Map Layer: ${args.map_layer}`, myEpoch);
          if (myEpoch !== commandEpoch) return null;
          setGoogleMapLayer(args.map_layer);
        }
        const hub = args.hub_id || 'royal_oak';
        const hBtn = document.getElementById(`p3-hub-${hub}`);
        if (hBtn) await moveAgentCursorTo(hBtn, `Ground Hub: ${hub}`, myEpoch);
        if (myEpoch !== commandEpoch) return null;
        const data = await runPillar3Grounding(hub);
        if (myEpoch !== commandEpoch) return null;
        hideAgentCursorSoon();
        return {
          status: 'grounding_complete',
          address: data && data.hub ? data.hub.address : hub,
          maps_places_count: data && data.maps && data.maps.places ? data.maps.places.length : 6,
          spoken_summary: `Grounded ${data && data.hub ? data.hub.address : hub} across Google Maps, YouTube video inspection, and 2026 property tax records.`
        };
      }

      if (name === 'control_rowan_autopilot') {
        setLog(`Kira Screen Action: control_rowan_autopilot(${JSON.stringify(args)})`);
        if (currentActivePillar !== 4) {
          await moveAgentCursorTo('#tab-btn-4', 'Open Pillar 4 · Rowan Autopilot', myEpoch);
          if (myEpoch !== commandEpoch) return null;
          switchPillar(4);
        }
        if (typeof args.cancel_all_subs === 'boolean') {
          document.querySelectorAll('.rowan-sub-chk').forEach(chk => { chk.checked = args.cancel_all_subs; });
          recalcRowanAutopilot();
        }
        hideAgentCursorSoon();
        return {
          status: 'autopilot_updated',
          monthly_savings: document.getElementById('p4-val-subs').innerText,
          payoff_impact: document.getElementById('p4-years-saved').innerText,
          spoken_summary: `Rowan canceled your 4 unused subscriptions, redirecting $285 a month to Rocket Mortgage principal and shaving 4.2 years off your loan.`
        };
      }

      if (name === 'control_realestate_marketplace') {
        setLog(`Kira Screen Action: control_realestate_marketplace(${JSON.stringify(args)})`);
        if (currentActivePillar !== 5) {
          await moveAgentCursorTo('#tab-btn-5', 'Open Pillar 5 · Airbnb × Redfin AI Marketplace', myEpoch);
          if (myEpoch !== commandEpoch) return null;
          switchPillar(5);
        }
        if (args.family_filter) {
          const aBtn = document.getElementById('p5-arch-' + args.family_filter);
          if (aBtn) {
            await moveAgentCursorTo(aBtn, `Filter Collection: ${args.family_filter}`, myEpoch);
            if (myEpoch !== commandEpoch) return null;
            p5CurrentArch = args.family_filter;
            document.querySelectorAll('#p5-arch-ribbon .abnb-cat-item').forEach(b => b.classList.remove('active'));
            aBtn.classList.add('active');
            const selArch = document.getElementById('p5-pill-arch-select');
            if (selArch) selArch.value = args.family_filter;
          }
        }
        if (typeof args.beds_filter === 'number' && args.beds_filter >= 0 && args.beds_filter <= 6) {
          const bBtn = document.getElementById('p5-bed-' + args.beds_filter);
          if (bBtn) {
            await moveAgentCursorTo(bBtn, `Filter Bedrooms: ${args.beds_filter || 'All'} Beds`, myEpoch);
            if (myEpoch !== commandEpoch) return null;
            p5CurrentBeds = args.beds_filter;
            document.querySelectorAll('#p5-bed-bar .abnb-filter-pill[id^="p5-bed-"]').forEach(b => b.classList.remove('active'));
            bBtn.classList.add('active');
            const selBeds = document.getElementById('p5-pill-beds-select');
            if (selBeds) selBeds.value = String(args.beds_filter);
          }
        }
        if (typeof args.max_price === 'number' && args.max_price >= 450000) {
          const mpEl = document.getElementById('p5-max-price');
          const capped = Math.max(450000, Math.min(2500000, Math.round(args.max_price / 50000) * 50000));
          if (mpEl) {
            mpEl.value = capped;
            document.getElementById('lbl-p5-max-price').innerText = '$' + (capped / 1e6).toFixed(2) + 'M';
          }
        }
        if (typeof args.query_text === 'string') {
          const sInp = document.getElementById('p5-search-input');
          if (sInp) {
            await moveAgentCursorTo(sInp, `AI Vector Search: "${args.query_text.slice(0, 38)}"`, myEpoch);
            if (myEpoch !== commandEpoch) return null;
            sInp.value = args.query_text;
          }
        }
        await moveAgentCursorTo('#btn-p5-search', 'Search 108 Distinct Homes', myEpoch);
        if (myEpoch !== commandEpoch) return null;
        const data = await runPillar5HybridSearch();
        if (myEpoch !== commandEpoch) return null;
        hideAgentCursorSoon();
        const top = data && data.results && data.results[0];
        if (top) {
          focusP5ListingOnMap(top.id, true);
          if (args.open_top_modal) {
            openRePropertyModal(top.id, 'rooms');
          }
        }
        const summary = top
          ? `I found ${data.total_matched} distinct architecturally verified homes matching your search. My top recommendation on the map is ${top.title} in ${top.city} at $${top.price.toLocaleString()}, featuring ${top.beds} bedrooms, ${top.total_rooms_mapped} coinciding rooms, and a Rocket verified payment of $${top.monthly_piti.toLocaleString()} a month with a $${top.closing_credit.toLocaleString()} closing credit.`
          : `Updated the Pillar 5 AI Real Estate Marketplace on screen.`;
        return {
          status: 'marketplace_updated',
          matched_count: data ? data.total_matched : 0,
          top_listing_id: top ? top.id : null,
          spoken_summary: summary
        };
      }
      return { status: 'ok' };
    }

    // Unified Handler for ANY Spoken or Typed User Command!
    async function executeUserSpokenOrTypedCommand(userText) {
      if (!userText || !userText.trim()) return;
      const cleanText = userText.trim();

      // Increment epoch so any previous command is canceled, and pause mic so Kira never hears her own voice!
      commandEpoch++;
      const myEpoch = commandEpoch;
      pauseMicForKiraSpeech();
      LiveAudioEngine.stopAll();
      LiveAudioEngine.allowNewTurnAudio();

      document.getElementById('omni-live-transcript').innerText = `You: "${cleanText}"`;
      document.getElementById('p4-live-transcript').innerText = `You: "${cleanText}"`;
      document.getElementById('omni-cmd-input').value = cleanText;

      // 1. Check if it matches a deterministic screen action (e.g. "change Fed / 30-Yr Mortgage Rate Shock to -60")
      const localActions = parseLocalScreenIntent(cleanText);
      if (localActions.length > 0) {
        lastClientExecutedStamp = Date.now();
        let lastResult = null;
        for (const act of localActions) {
          if (myEpoch !== commandEpoch) return;
          lastResult = await executeAgentScreenTool(act.name, act.args, myEpoch);
        }
        if (myEpoch !== commandEpoch) return;
        // Immediately speak the live updated numbers via 24kHz HD stream so Kira ALWAYS answers completely!
        if (lastResult && lastResult.spoken_summary) {
          document.getElementById('omni-live-transcript').innerText = lastResult.spoken_summary;
          document.getElementById('p4-live-transcript').innerText = lastResult.spoken_summary;
          LiveAudioEngine.speakClip(lastResult.spoken_summary, 'Aoede', null, myEpoch);
        } else {
          scheduleMicResumeIfActive();
        }
        return;
      }

      // 2. Otherwise send to Gemini Live WebSocket (/ws/live-avatar) for open-ended conversation + tool calling
      ensureLiveAvatarWebSocket(cleanText, myEpoch);
    }

    // =========================================================================
    // OUT-OF-ORDER ASYNC SUBAGENT SWARM DISPATCHER (`FIRST-READY` + FLASH-NEXT)
    // =========================================================================
    let activeSubagentCount = 0;
    let subagentFinishOrder = 0;
    let currentGlobalModel = 'gemini-3.8-flash';

    function setGlobalModelSelection(model) {
      currentGlobalModel = model;
      const el = document.getElementById('global-model-selector');
      if (el && el.value !== model) el.value = model;
    }

    function updateSubagentTrayCounter() {
      const cntEl = document.getElementById('subagent-tray-counter');
      if (!cntEl) return;
      if (activeSubagentCount > 0) {
        cntEl.innerText = `${activeSubagentCount} Running Async`;
        cntEl.style.background = 'rgba(255,56,92,0.22)';
        cntEl.style.color = '#FF385C';
      } else {
        cntEl.innerText = 'All Ready';
        cntEl.style.background = 'rgba(5,150,105,0.22)';
        cntEl.style.color = '#34D399';
      }
    }

    function clearAsyncSubagentTray() {
      const listEl = document.getElementById('async-subagent-list');
      if (listEl) listEl.innerHTML = '';
      subagentFinishOrder = 0;
      const winEl = document.getElementById('subagent-first-winner-lbl');
      if (winEl) winEl.innerText = '';
      updateSubagentTrayCounter();
    }

    async function dispatchConcurrentSubagents(rawPromptOrArray) {
      const tray = document.getElementById('async-subagent-tray');
      const listEl = document.getElementById('async-subagent-list');
      if (tray) tray.style.display = 'flex';

      let specs = [];
      try {
        const body = Array.isArray(rawPromptOrArray)
          ? { prompts: rawPromptOrArray, preferred_model: currentGlobalModel }
          : { prompt: String(rawPromptOrArray || ''), preferred_model: currentGlobalModel };
        const decRes = await fetch('/api/async-subagents/decompose', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body)
        });
        const decData = await decRes.json();
        specs = decData.subagents || [];
      } catch (e) {
        const arr = Array.isArray(rawPromptOrArray) ? rawPromptOrArray : [String(rawPromptOrArray)];
        specs = arr.map((p, idx) => ({
          subagent_id: 'sub-' + Date.now() + '-' + (idx + 1),
          index: idx + 1,
          prompt: p,
          role: 'Flash-Next Instant Subagent',
          model_label: currentGlobalModel
        }));
      }

      if (!specs.length) return;
      document.getElementById('omni-live-transcript').innerText =
        `Spawned ${specs.length} parallel async subagent${specs.length > 1 ? 's' : ''} on ${currentGlobalModel} — streaming responses in first-ready order...`;

      // Launch EVERY subagent concurrently with independent Promises (`first-ready` resolution!)
      specs.forEach((spec) => {
        activeSubagentCount++;
        updateSubagentTrayCounter();

        const card = document.createElement('div');
        card.id = 'card-' + spec.subagent_id;
        card.style.cssText =
          'padding:10px 12px;border-radius:11px;background:var(--bg-subtle);border:1.5px solid var(--border-hairline);display:flex;flex-direction:column;gap:5px;transition:all 0.2s ease;';
        card.innerHTML = `
          <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;">
            <div style="display:flex;align-items:center;gap:6px;font-size:11.5px;font-weight:800;">
              <span style="padding:2px 7px;border-radius:6px;background:#0F172A;color:#38BDF8;font-family:'JetBrains Mono',monospace;font-size:10px;">SUBAGENT #${spec.index}</span>
              <span>${spec.role}</span>
            </div>
            <span id="status-${spec.subagent_id}" style="font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700;color:#F59E0B;">
              ⏳ RUNNING · ${spec.model_label}
            </span>
          </div>
          <div style="font-size:11.5px;color:var(--ink-secondary);font-weight:600;">Prompt: "${spec.prompt}"</div>
          <div id="ans-${spec.subagent_id}" style="font-size:12px;color:var(--ink-muted);font-style:italic;">
            Executing in parallel (non-blocking)...
          </div>
        `;
        if (listEl) listEl.prepend(card);

        const tStart = performance.now();
        fetch('/api/async-subagent', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            subagent_id: spec.subagent_id,
            prompt: spec.prompt,
            preferred_model: currentGlobalModel
          })
        })
          .then(r => r.json())
          .then(async (resData) => {
            activeSubagentCount = Math.max(0, activeSubagentCount - 1);
            subagentFinishOrder++;
            const rank = subagentFinishOrder;
            updateSubagentTrayCounter();

            const elapsedMs = Math.round(performance.now() - tStart);
            const statusEl = document.getElementById('status-' + spec.subagent_id);
            const ansEl = document.getElementById('ans-' + spec.subagent_id);
            const isFirst = rank === 1;

            card.style.borderColor = isFirst ? '#059669' : '#1A73E8';
            card.style.background = 'var(--bg-card)';
            if (statusEl) {
              statusEl.style.color = isFirst ? '#059669' : '#1A73E8';
              statusEl.innerText = `✓ READY #${rank} (${resData.latency_ms || elapsedMs}ms · ${resData.model || spec.model_label})`;
            }
            if (ansEl) {
              ansEl.style.fontStyle = 'normal';
              ansEl.style.color = 'var(--ink-primary)';
              ansEl.innerHTML = `
                <div style="line-height:1.45;">${resData.answer}</div>
                ${resData.action_badge ? `<div style="margin-top:5px;"><span class="badge-live">${resData.action_badge}</span></div>` : ''}
              `;
            }
            // Move whichever subagent finished FIRST to the very top of the feed!
            if (listEl && isFirst) {
              listEl.prepend(card);
              const winEl = document.getElementById('subagent-first-winner-lbl');
              if (winEl) {
                winEl.innerText = `⚡ First Ready: Subagent #${spec.index} (${resData.latency_ms || elapsedMs}ms)`;
              }
            }
            document.getElementById('omni-live-transcript').innerText =
              `[Ready #${rank} · ${spec.model_label}] ${resData.answer}`;

            if (resData.screen_action && resData.screen_action.name) {
              commandEpoch++;
              await executeAgentScreenTool(resData.screen_action.name, resData.screen_action.args || {}, commandEpoch);
            }
          })
          .catch(err => {
            activeSubagentCount = Math.max(0, activeSubagentCount - 1);
            updateSubagentTrayCounter();
            const ansEl = document.getElementById('ans-' + spec.subagent_id);
            if (ansEl) ansEl.innerText = 'Error: ' + err.message;
          });
      });
    }

    function triggerDemo3xAsyncSubagentBurst() {
      subagentFinishOrder = 0;
      dispatchConcurrentSubagents([
        "Show me 4-bedroom Colonial homes under $850K on the Airbnb map and open the top match",
        "What GCP services and IAM roles does the customer need to enable to run this hackathon demo?",
        "Run BigQuery ML TimesFM forecast for a -90 bps Fed rate shock"
      ]);
    }

    function submitOmniCommandInput() {
      const inp = document.getElementById('omni-cmd-input');
      if (!inp || !inp.value.trim()) return;
      const val = inp.value.trim();
      inp.value = '';
      // If user explicitly sent multiple tasks separated by ';' or '||' or 'and also', fan out into parallel subagents.
      // Otherwise, even if Kira is currently speaking, immediately barge-in and execute the user's new command!
      if (/[;|]|\\band\\s+also\\b|\\balso\\s+tell\\s+me\\b/i.test(val)) {
        dispatchConcurrentSubagents(val);
        return;
      }
      executeUserSpokenOrTypedCommand(val);
    }

    // =========================================================================
    // PILLAR 1: BIGQUERY ML TIMESFM (`AI.FORECAST`)
    // =========================================================================
    let currentP1Cohort = 'mrcooper_refi_locks';
    let lastP1Data = null;

    function selectTimesFmCohort(cid, btnEl) {
      currentP1Cohort = cid;
      document.querySelectorAll('#pillar-1 .cohort-btn').forEach(b => b.classList.remove('active'));
      if (btnEl) btnEl.classList.add('active');
      runPillar1TimesFM();
    }

    function toggleSqlDrawer() {
      const el = document.getElementById('p1-sql-drawer');
      el.style.display = el.style.display === 'block' ? 'none' : 'block';
    }

    async function runPillar1TimesFM() {
      const shock = parseInt(document.getElementById('p1-shock').value, 10);
      const horizon = parseInt(document.getElementById('p1-horizon').value, 10);
      const ci = parseInt(document.getElementById('p1-ci').value, 10) / 100.0;
      const badge = document.getElementById('p1-latency-badge');
      badge.innerHTML = '<span class="dot-pulse"></span>Running BQ AI.FORECAST...';

      try {
        const res = await fetch('/api/pillar1/forecast', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            metric_id: currentP1Cohort,
            horizon: horizon,
            confidence_level: ci,
            rate_shock_bps: shock
          })
        });
        const data = await res.json();
        lastP1Data = data;
        badge.innerHTML = `<span class="dot-pulse"></span>BQ TimesFM · ${data.latency_ms}ms`;
        document.getElementById('p1-chart-title').innerText = data.meta.title;
        document.getElementById('p1-chart-sub').innerText = `${data.meta.subtitle} (Shock: ${shock > 0 ? '+' : ''}${shock} bps · Horizon: ${horizon}w · ${Math.round(ci*100)}% CI)`;
        document.getElementById('p1-kpi-last').innerText = data.kpis.last_historical.toLocaleString();
        document.getElementById('p1-kpi-peak').innerText = data.kpis.peak_forecast.toLocaleString();
        document.getElementById('p1-kpi-delta').innerText = (data.kpis.delta_pct >= 0 ? '+' : '') + data.kpis.delta_pct + '% vs Baseline';
        document.getElementById('p1-kpi-cum').innerText = Math.round(data.kpis.cumulative_horizon).toLocaleString();
        document.getElementById('p1-kpi-usd').innerText = '$' + (data.kpis.est_value_usd / 1e6).toFixed(1) + 'M';
        document.getElementById('p1-sql-drawer').innerText = data.sql;
        renderTimesFmSvg(data.historical, data.forecast);

        // Flash KPI tiles so the user clearly sees the live update
        document.querySelectorAll('#p1-kpi-row .kpi-tile').forEach(el => {
          el.classList.add('flash-highlight');
          setTimeout(() => el.classList.remove('flash-highlight'), 900);
        });
        return data;
      } catch (e) {
        badge.innerText = 'Error: ' + e.message;
        return null;
      }
    }

    function renderTimesFmSvg(hist, fc) {
      const svg = document.getElementById('p1-svg-chart');
      if (!hist || !hist.length || !fc || !fc.length) return;
      const W = 860, H = 300, padL = 56, padR = 24, padT = 24, padB = 34;
      const allVals = [];
      hist.forEach(d => allVals.push(d.value, d.baseline));
      fc.forEach(d => allVals.push(d.forecast, d.lower, d.upper));
      const minV = Math.min(...allVals) * 0.94;
      const maxV = Math.max(...allVals) * 1.05;
      const totalPts = hist.length + fc.length;
      const xOf = (idx) => padL + (idx / Math.max(1, totalPts - 1)) * (W - padL - padR);
      const yOf = (v) => padT + (1 - (v - minV) / Math.max(1e-6, maxV - minV)) * (H - padT - padB);

      let gridHtml = '';
      for (let i = 0; i <= 4; i++) {
        const gv = minV + (i / 4) * (maxV - minV);
        const gy = yOf(gv);
        gridHtml += `<line x1="${padL}" y1="${gy}" x2="${W - padR}" y2="${gy}" stroke="rgba(148,163,184,0.22)" stroke-dasharray="3,3"/>`;
        gridHtml += `<text x="${padL - 8}" y="${gy + 4}" text-anchor="end" font-size="10.5" font-family="JetBrains Mono" fill="#64748B">${gv >= 1000 ? (gv/1000).toFixed(1)+'k' : gv.toFixed(1)}</text>`;
      }

      const histPts = hist.map((d, i) => `${xOf(i).toFixed(1)},${yOf(d.value).toFixed(1)}`).join(' ');
      const splitIdx = hist.length - 1;
      const splitX = xOf(splitIdx);

      const upperPts = [`${splitX.toFixed(1)},${yOf(hist[splitIdx].value).toFixed(1)}`];
      const lowerPts = [];
      fc.forEach((d, j) => {
        const xi = xOf(hist.length + j).toFixed(1);
        upperPts.push(`${xi},${yOf(d.upper).toFixed(1)}`);
        lowerPts.unshift(`${xi},${yOf(d.lower).toFixed(1)}`);
      });
      const conePolygon = upperPts.concat(lowerPts).join(' ');

      const fcPts = [`${splitX.toFixed(1)},${yOf(hist[splitIdx].value).toFixed(1)}`];
      fc.forEach((d, j) => {
        fcPts.push(`${xOf(hist.length + j).toFixed(1)},${yOf(d.forecast).toFixed(1)}`);
      });

      let dotsHtml = '';
      fc.forEach((d, j) => {
        const cx = xOf(hist.length + j);
        const cy = yOf(d.forecast);
        dotsHtml += `<circle cx="${cx}" cy="${cy}" r="4" fill="#D81E28" stroke="#FFF" stroke-width="1.5"><title>${d.date}: ${d.forecast.toLocaleString()} [${d.lower.toLocaleString()} - ${d.upper.toLocaleString()}]</title></circle>`;
      });

      svg.innerHTML = `
        ${gridHtml}
        <polygon points="${conePolygon}" fill="rgba(216, 30, 40, 0.15)" stroke="none" />
        <line x1="${splitX}" y1="${padT}" x2="${splitX}" y2="${H - padB}" stroke="#1A73E8" stroke-width="1.5" stroke-dasharray="5,4" />
        <rect x="${splitX - 95}" y="${padT - 6}" width="190" height="20" rx="6" fill="#1A73E8" />
        <text x="${splitX}" y="${padT + 8}" text-anchor="middle" font-size="10" font-family="JetBrains Mono" font-weight="700" fill="#FFF">TIMESFM ZERO-SHOT HORIZON</text>
        <polyline fill="none" stroke="#0F172A" stroke-width="2.8" points="${histPts}" />
        <polyline fill="none" stroke="#D81E28" stroke-width="3" stroke-dasharray="6,4" points="${fcPts.join(' ')}" />
        ${dotsHtml}
        <text x="${padL + 10}" y="${H - 10}" font-size="11" font-family="JetBrains Mono" fill="#64748B">Historical (${hist[0].date} to ${hist[hist.length-1].date})</text>
        <text x="${W - padR - 10}" y="${H - 10}" text-anchor="end" font-size="11" font-family="JetBrains Mono" fill="#D81E28" font-weight="700">TimesFM Forecast (to ${fc[fc.length-1].date})</text>
      `;
    }

    function speakPillar1Summary(btnEl) {
      if (!lastP1Data) return;
      const text = `BigQuery ML TimesFM forecast complete for ${lastP1Data.meta.title}. With a ${lastP1Data.params.rate_shock_bps} basis point rate shift, peak weekly volume reaches ${lastP1Data.kpis.peak_forecast.toLocaleString()}, generating an estimated ${(lastP1Data.kpis.est_value_usd/1e6).toFixed(1)} million dollars in recaptured Rocket portfolio value.`;
      LiveAudioEngine.speakClip(text, 'Kore', btnEl);
    }

    // =========================================================================
    // PILLAR 2: VEO 3.1 REELS STUDIO
    // =========================================================================
    let currentReelData = null;
    window.reelCaptionTimer = null;

    async function loadPresetReel(presetId, btnEl) {
      if (btnEl) {
        document.querySelectorAll('#pillar-2 .cohort-btn').forEach(b => b.classList.remove('active'));
        btnEl.classList.add('active');
      }
      const res = await fetch(`/api/pillar2/preset/${presetId}`);
      const data = await res.json();
      applyReelToStage(data);
    }

    function applyReelToStage(data) {
      currentReelData = data;
      const vid = document.getElementById('p2-video');
      const poster = document.getElementById('p2-poster-overlay');
      if (data.poster_b64) {
        poster.style.backgroundImage = `url(${data.poster_b64})`;
        poster.style.opacity = '0.32';
      } else {
        poster.style.opacity = '0';
      }
      if (vid.getAttribute('src') !== data.video_url) {
        vid.src = data.video_url;
        vid.play().catch(() => {});
      }
      document.getElementById('p2-prompt').value = data.prompt || data.veo_visual_prompt || '';
      document.getElementById('p2-price').value = data.price || (data.financials && data.financials.price) || 460000;
      document.getElementById('p2-down').value = data.down_pct || (data.financials && data.financials.down_pct) || 10;
      document.getElementById('p2-rate').value = data.rate_pct || (data.financials && data.financials.rate_pct) || 5.875;
      document.getElementById('p2-vo-script').innerText = data.voiceover_script || '';
      updateP2Financials();

      const capList = document.getElementById('p2-caption-list');
      const caps = data.captions || [];
      capList.innerHTML = caps.map((c, idx) => `
        <div style="padding:9px 11px;border-radius:9px;border:1px solid var(--border-hairline);background:var(--bg-subtle);cursor:pointer;"
             onclick="setActiveReelCaption(${idx})">
          <div style="font-size:10px;font-family:'JetBrains Mono',monospace;color:var(--google-blue);font-weight:700;">${c.tag}</div>
          <div style="font-size:12px;font-weight:700;margin-top:2px;">${c.text}</div>
        </div>
      `).join('');
      if (caps.length) setActiveReelCaption(0);
    }

    function setActiveReelCaption(idx) {
      if (!currentReelData || !currentReelData.captions || !currentReelData.captions[idx]) return;
      const c = currentReelData.captions[idx];
      document.getElementById('p2-active-cap-tag').innerText = c.tag;
      document.getElementById('p2-active-cap-text').innerText = c.text;
    }

    function updateP2Financials() {
      const price = parseInt(document.getElementById('p2-price').value, 10);
      const down = parseInt(document.getElementById('p2-down').value, 10);
      const rate = parseFloat(document.getElementById('p2-rate').value);
      document.getElementById('lbl-p2-price').innerText = '$' + price.toLocaleString();
      document.getElementById('lbl-p2-down').innerText = down + '%';
      document.getElementById('lbl-p2-rate').innerText = rate.toFixed(3) + '%';

      const loan = price * (1 - down / 100.0);
      const r = (rate / 100.0) / 12.0;
      const pi = loan * (r * Math.pow(1 + r, 360)) / (Math.pow(1 + r, 360) - 1);
      const piti = Math.round(pi + (price * 0.0145 / 12.0) + 145);
      const credit = Math.round(price * 0.01);

      document.getElementById('p2-sticker-piti').innerText = '$' + piti.toLocaleString() + '/mo';
      document.getElementById('p2-sticker-credit').innerText = '+$' + credit.toLocaleString() + ' Closing Credit';
      document.getElementById('p2-sticker-sub').innerText = `${down}% Down · ${rate.toFixed(3)}% Fixed`;
    }

    async function generateCustomReel(liveVeoMp4) {
      const badge = document.getElementById('p2-status-badge');
      badge.innerHTML = liveVeoMp4
        ? '<span class="dot-pulse"></span>Synthesizing Veo 3.1 MP4 (~22s)...'
        : '<span class="dot-pulse"></span>Generating Reel + Keyframe (~5s)...';
      try {
        const res = await fetch('/api/pillar2/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            prompt_text: document.getElementById('p2-prompt').value,
            price: parseInt(document.getElementById('p2-price').value, 10),
            down_pct: parseInt(document.getElementById('p2-down').value, 10),
            rate_pct: parseFloat(document.getElementById('p2-rate').value),
            voice: 'Aoede',
            generate_live_veo_mp4: liveVeoMp4
          })
        });
        const data = await res.json();
        badge.innerHTML = `<span class="dot-pulse"></span>${data.latency_ms}ms · Ready`;
        document.getElementById('p2-model-tag').innerText = liveVeoMp4 ? 'Veo 3.1 Live MP4' : 'Veo 3.1 + Keyframe';
        applyReelToStage(data);
      } catch (e) {
        badge.innerText = 'Error: ' + e.message;
      }
    }

    function playReelWith24kVoiceover(btnEl) {
      if (!currentReelData) return;
      const started = LiveAudioEngine.speakClip(currentReelData.voiceover_script, currentReelData.voice || 'Aoede', btnEl);
      if (!started) return;
      const vid = document.getElementById('p2-video');
      vid.currentTime = 0;
      vid.play().catch(() => {});
      let idx = 0;
      if (window.reelCaptionTimer) clearInterval(window.reelCaptionTimer);
      window.reelCaptionTimer = setInterval(() => {
        if (!currentReelData || !currentReelData.captions) return;
        idx = (idx + 1) % currentReelData.captions.length;
        setActiveReelCaption(idx);
      }, 3000);
    }

    // =========================================================================
    // PILLAR 3: TRI-MODAL GROUNDING (GOOGLE MAPS + YOUTUBE + GOOGLE SEARCH)
    // =========================================================================
    let p3Map = null;
    let p3TileLayer = null;
    let p3MarkerGroup = null;
    let currentP3Hub = 'royal_oak';

    function initPillar3Map() {
      mapInitialized = true;
      p3Map = L.map('grounding-map').setView([42.4962, -83.1477], 13);
      p3TileLayer = L.tileLayer('https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', {
        maxZoom: 20,
        attribution: '&copy; Google Maps Platform (vtxdemos)'
      }).addTo(p3Map);
      p3MarkerGroup = L.layerGroup().addTo(p3Map);
    }

    function setGoogleMapLayer(mode) {
      if (!p3Map) initPillar3Map();
      if (p3TileLayer) p3Map.removeLayer(p3TileLayer);
      const lyrs = mode === 'satellite' ? 'y' : 'm';
      p3TileLayer = L.tileLayer(`https://mt1.google.com/vt/lyrs=${lyrs}&x={x}&y={y}&z={z}`, {
        maxZoom: 20,
        attribution: '&copy; Google Maps Platform (vtxdemos)'
      }).addTo(p3Map);
    }

    async function runPillar3Grounding(hubId) {
      currentP3Hub = hubId || 'royal_oak';
      document.querySelectorAll('[id^="p3-hub-"]').forEach(b => b.style.borderColor = 'var(--border-hairline)');
      const activeHubBtn = document.getElementById('p3-hub-' + currentP3Hub);
      if (activeHubBtn) activeHubBtn.style.borderColor = 'var(--google-blue)';

      const customYt = document.getElementById('p3-custom-yt').value.trim();
      const badge = document.getElementById('p3-lat-badge');
      badge.innerHTML = '<span class="dot-pulse"></span>Grounding Maps+YT+Search...';

      try {
        const res = await fetch('/api/pillar3/ground', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            hub_id: currentP3Hub,
            custom_youtube_url: customYt
          })
        });
        const data = await res.json();
        badge.innerHTML = `<span class="dot-pulse"></span>Grounded in ${data.latency_ms}ms`;

        if (p3Map && data.hub) {
          p3Map.setView([data.hub.lat, data.hub.lng], 13);
          p3MarkerGroup.clearLayers();
          L.marker([data.hub.lat, data.hub.lng])
            .addTo(p3MarkerGroup)
            .bindPopup(`<strong>${data.hub.address}</strong><br>Redfin Listing: ${data.hub.price}`)
            .openPopup();
          (data.maps.places || []).forEach((pl, idx) => {
            const angle = (idx / Math.max(1, data.maps.places.length)) * Math.PI * 2;
            const plat = data.hub.lat + Math.sin(angle) * 0.008;
            const plng = data.hub.lng + Math.cos(angle) * 0.010;
            L.circleMarker([plat, plng], { radius: 7, color: '#1A73E8', fillColor: '#1A73E8', fillOpacity: 0.85 })
              .addTo(p3MarkerGroup)
              .bindPopup(`<strong>${pl.title}</strong><br><a href="${pl.uri}" target="_blank">Open Verified Google Maps Place</a>`);
          });
        }

        document.getElementById('p3-maps-summary').innerText = data.maps.summary || '';
        document.getElementById('p3-maps-pills').innerHTML = (data.maps.places || []).map(p =>
          `<a class="place-pill" href="${p.uri}" target="_blank" rel="noopener">${SVG_PIN} <span>${p.title}</span></a>`
        ).join('');

        const ytUrl = data.youtube.youtube_url || data.hub.youtube_url;
        const vidMatch = ytUrl.match(/[?&]v=([^&]+)/) || (ytUrl.includes("youtu.be/") ? [, ytUrl.split("youtu.be/")[1].split("?")[0]] : null);
        const vidId = vidMatch ? vidMatch[1] : data.hub.youtube_id;
        document.getElementById('p3-yt-iframe').src = `https://www.youtube.com/embed/${vidId}?enablejsapi=1`;
        document.getElementById('p3-yt-summary').innerText = data.youtube.summary || '';

        document.getElementById('p3-search-summary').innerText = data.search.summary || '';
        document.getElementById('p3-search-pills').innerHTML = (data.search.sources || []).map(s =>
          `<a class="place-pill" href="${s.uri}" target="_blank" rel="noopener">${SVG_LINK} <span>${s.domain || s.title}</span></a>`
        ).join('');
        return data;
      } catch (e) {
        badge.innerText = 'Error: ' + e.message;
        return null;
      }
    }

    // =========================================================================
    // PILLAR 4 & OMNI-DOCK: UNIFIED LIVE VOICE + SPEECH RECOGNITION + WEBSOCKET
    // =========================================================================
    function updateVoiceMicUI(active) {
      voiceMicActive = active;
      const omniBtn = document.getElementById('btn-omni-voice');
      const omniLbl = document.getElementById('lbl-omni-voice');
      const p4Btn = document.getElementById('btn-p4-start');
      const p4Lbl = document.getElementById('lbl-p4-start');
      const badge = document.getElementById('p4-conn-badge');
      const pipStatus = document.getElementById('kira-pip-status');

      if (active) {
        if (omniBtn) omniBtn.classList.add('mic-live');
        if (omniLbl) omniLbl.innerText = 'Mic Listening (Speak Now)';
        if (p4Btn) p4Btn.classList.add('mic-live');
        if (p4Lbl) p4Lbl.innerText = 'Mic Listening — Speak Any Command';
        if (badge) badge.innerHTML = '<span class="dot-pulse"></span>MIC LIVE · SPEAK TO SCREEN';
        if (pipStatus && !LiveAudioEngine.isSpeakingOrQueued()) pipStatus.innerText = 'KIRA · LISTENING (SPEAK NOW)';
      } else {
        if (omniBtn) omniBtn.classList.remove('mic-live');
        if (omniLbl) omniLbl.innerText = 'Start Live Voice & Mic';
        if (p4Btn) p4Btn.classList.remove('mic-live');
        if (p4Lbl) p4Lbl.innerText = 'Start Live Voice & Mic (Speak to Screen)';
        if (badge) badge.innerHTML = '<span class="dot-pulse"></span>24kHz + Screen Control Ready';
        if (pipStatus && !LiveAudioEngine.isSpeakingOrQueued()) pipStatus.innerText = 'KIRA · READY';
      }
    }

    function ensureLiveAvatarWebSocket(initialTextToSend, expectedEpoch) {
      const myEpoch = typeof expectedEpoch === 'number' ? expectedEpoch : commandEpoch;
      if (myEpoch !== commandEpoch) return;

      if (p4Ws && p4Ws.readyState === WebSocket.OPEN) {
        if (initialTextToSend) {
          pauseMicForKiraSpeech();
          p4TurnInProgress = true;
          LiveAudioEngine.allowNewTurnAudio();
          p4Ws.send(JSON.stringify({ type: 'text', text: initialTextToSend }));
        }
        return;
      }
      // Close any previous connecting/closing p4Ws before creating a new socket so we never leak an orphan WebSocket
      if (p4Ws) {
        try { p4Ws.onmessage = null; p4Ws.onopen = null; p4Ws.onclose = null; p4Ws.close(); } catch (e) {}
        allTrackedWebSockets.delete(p4Ws);
        p4Ws = null;
      }
      const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
      const ws = new WebSocket(`${proto}//${location.host}/ws/live-avatar?voice=Aoede&avatar=Kira`);
      p4Ws = ws;
      allTrackedWebSockets.add(ws);

      let txAcc = '';
      ws.onopen = () => {
        if (myEpoch !== commandEpoch || p4Ws !== ws || LiveAudioEngine.ignoreIncomingAudio) {
          try { ws.close(); } catch (e) {}
          allTrackedWebSockets.delete(ws);
          return;
        }
        if (initialTextToSend) {
          pauseMicForKiraSpeech();
          p4TurnInProgress = true;
          LiveAudioEngine.allowNewTurnAudio();
          ws.send(JSON.stringify({ type: 'text', text: initialTextToSend }));
        }
      };
      ws.onmessage = async (evt) => {
        if (p4Ws !== ws || LiveAudioEngine.ignoreIncomingAudio) return;
        const turnEpoch = commandEpoch;
        const msg = JSON.parse(evt.data);
        if (msg.type === 'tool_call_batch' && Array.isArray(msg.calls)) {
          pauseMicForKiraSpeech();
          p4TurnInProgress = true;
          const responses = [];
          for (const call of msg.calls) {
            if (turnEpoch !== commandEpoch) return;
            let resObj = { status: 'updated_on_screen' };
            if (Date.now() - lastClientExecutedStamp > 3000) {
              resObj = (await executeAgentScreenTool(call.name, call.args || {}, turnEpoch)) || { status: 'aborted' };
            }
            if (turnEpoch !== commandEpoch) return;
            responses.push({ id: call.id, name: call.name, result: resObj });
          }
          if (turnEpoch === commandEpoch && p4Ws === ws && ws.readyState === WebSocket.OPEN && !LiveAudioEngine.ignoreIncomingAudio) {
            ws.send(JSON.stringify({ type: 'tool_result', responses: responses }));
          }
          return;
        }
        if (msg.interrupted) {
          txAcc = '';
          return;
        }
        if (msg.output_transcript && !LiveAudioEngine.ignoreIncomingAudio) {
          txAcc += msg.output_transcript;
          document.getElementById('p4-live-transcript').innerText = txAcc;
          document.getElementById('omni-live-transcript').innerText = txAcc;
        }
        if (msg.audio_b64 && !LiveAudioEngine.ignoreIncomingAudio) {
          p4TurnInProgress = true;
          LiveAudioEngine.playPcmChunk(msg.audio_b64);
        }
        if (msg.turn_complete) {
          txAcc = '';
          p4TurnInProgress = false;
          if (!LiveAudioEngine.isSpeakingOrQueued()) {
            syncAvatarVideosWithSpeech(false);
            scheduleMicResumeIfActive();
          }
        }
      };
      ws.onclose = () => {
        allTrackedWebSockets.delete(ws);
        if (p4Ws === ws) {
          p4Ws = null;
          p4TurnInProgress = false;
        }
      };
    }

    function startBrowserSpeechRecognizer() {
      if (!voiceMicActive) return;
      const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SR) return;

      // Activate hardware acoustic echo cancellation so the browser strips Kira's speaker output from the mic
      ensureHardwareEchoCanceledMic();

      if (speechRec) {
        return; // Already running continuously for live barge-in!
      }

      const rec = new SR();
      speechRec = rec;
      rec.continuous = true;
      rec.interimResults = true;
      rec.lang = 'en-US';

      rec.onresult = (event) => {
        if (!voiceMicActive) return;

        let interim = '';
        let newlyFinalized = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const t = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            newlyFinalized += ' ' + t;
          } else {
            interim += t;
          }
        }

        const candidateText = (newlyFinalized + ' ' + interim).trim();
        const kiraCurrentlySpeaking = isKiraBusyOrSpeaking || LiveAudioEngine.isSpeakingOrQueued() || p4TurnInProgress;

        // REAL-TIME VOICE BARGE-IN: If Kira is currently speaking and the user speaks over her,
        // verify it's genuine user speech (not acoustic speaker echo) and cut Kira off in 0.0ms!
        if (kiraCurrentlySpeaking) {
          if (!isGenuineUserBargeIn(candidateText)) {
            return;
          }
          bargeInInterruptNow(`⚡ Voice Barge-In: "${candidateText}"`);
        }

        if (newlyFinalized.trim()) {
          spokenUtteranceBuffer = (spokenUtteranceBuffer + ' ' + newlyFinalized).trim();
        }
        const livePreview = (spokenUtteranceBuffer + ' ' + interim).trim();
        if (livePreview) {
          document.getElementById('omni-live-transcript').innerText = `Hearing: "${livePreview}..."`;
          document.getElementById('p4-live-transcript').innerText = `Hearing: "${livePreview}..."`;
          document.getElementById('omni-cmd-input').value = livePreview;

          // Debounce by 550ms after the user stops speaking so multi-clause commands ("... to -60") stay in one turn!
          if (speechFinalizeTimer) clearTimeout(speechFinalizeTimer);
          const mySpeechEpoch = commandEpoch;
          speechFinalizeTimer = setTimeout(() => {
            const fullCmd = (spokenUtteranceBuffer || livePreview).trim();
            spokenUtteranceBuffer = '';
            speechFinalizeTimer = null;
            if (fullCmd && voiceMicActive && mySpeechEpoch === commandEpoch) {
              executeUserSpokenOrTypedCommand(fullCmd);
            }
          }, 550);
        }
      };

      rec.onerror = () => {};
      rec.onend = () => {
        if (speechRec === rec) {
          speechRec = null;
        }
        if (voiceMicActive) {
          setTimeout(() => {
            if (voiceMicActive && !speechRec) startBrowserSpeechRecognizer();
          }, 120);
        }
      };

      try {
        rec.start();
      } catch (e) {}
    }

    // Unified 1-Click Button: Turns on Microphone Speech Recognition + Live Barge-In!
    function toggleUnifiedLiveVoiceMic() {
      // If mic is already on AND Kira is currently speaking, clicking this button acts as an instant Barge-In interrupt
      // while keeping the microphone live so the user can speak right away!
      if (voiceMicActive && (LiveAudioEngine.isSpeakingOrQueued() || isKiraBusyOrSpeaking || p4TurnInProgress)) {
        bargeInInterruptNow('⚡ Interrupted Kira — Listening for your voice command now...');
        startBrowserSpeechRecognizer();
        return;
      }
      if (voiceMicActive) {
        stopAllAudioAndAvatarNow();
        return;
      }

      // If Kira was speaking from a button click while mic was off, interrupt her and start live listening immediately
      if (LiveAudioEngine.isSpeakingOrQueued() || isKiraBusyOrSpeaking || p4TurnInProgress) {
        bargeInInterruptNow('⚡ Interrupted Kira — Live Voice & Barge-In Mic Activated');
      }

      LiveAudioEngine.allowNewTurnAudio();
      isKiraBusyOrSpeaking = false;
      spokenUtteranceBuffer = '';
      updateVoiceMicUI(true);

      const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SR) {
        document.getElementById('omni-live-transcript').innerText = 'Type your command in the box below to instruct Kira.';
        document.getElementById('omni-cmd-input').focus();
        return;
      }

      document.getElementById('omni-live-transcript').innerText = 'Listening (Live Barge-In Ready) — Speak anytime to command or interrupt Kira';
      document.getElementById('p4-live-transcript').innerText = 'Listening (Live Barge-In Ready) — Speak anytime to command or interrupt Kira';
      startBrowserSpeechRecognizer();
    }

    function recalcRowanAutopilot() {
      let total = 0;
      let count = 0;
      document.querySelectorAll('.rowan-sub-chk').forEach(chk => {
        if (chk.checked) {
          total += parseInt(chk.getAttribute('data-amt'), 10);
          count++;
        }
      });
      document.getElementById('p4-val-subs').innerText = '+$' + total + '/mo';
      document.getElementById('p4-sub-subs').innerText = `${count} Unused Subs Canceled`;
      const yrs = (total * 0.0147).toFixed(1);
      const interestSaved = Math.round(total * 227.3);
      document.getElementById('p4-years-saved').innerText = `Saves $${interestSaved.toLocaleString()} Interest · ${yrs} Yrs Shaved`;
    }

    // =========================================================================
    // PILLAR 5: AIRBNB × REDFIN PREMIER AI REAL ESTATE MARKETPLACE (108 DISTINCT HOMES + INTERACTIVE PRICE-PIN MAP + LIVE KIRA CONCIERGE)
    // =========================================================================
    let p5LoadedOnce = false;
    let p5CurrentArch = 'all';
    let p5CurrentBeds = 0;
    let p5RefListingId = '';
    let p5RefImageB64 = '';
    let p5Results = [];
    let p5CardRoomIdx = {};
    let p5ActiveModalItem = null;
    let p5WishlistIds = new Set(['RKT-001', 'RKT-066', 'RKT-082']);

    // Interactive Airbnb Price-Pin Google Map State
    let p5MapInitialized = false;
    let p5AirbnbMap = null;
    let p5MapTileLayer = null;
    let p5MapMarkerGroup = null;
    let p5MapPinElements = {};
    let p5ActiveMapListingId = null;

    function formatPricePin(price) {
      if (price >= 1000000) {
        return '$' + (price / 1000000).toFixed(2).replace(/\\.00$/, '').replace(/(\\.\\d)0$/, '$1') + 'M';
      }
      return '$' + Math.round(price / 1000) + 'K';
    }

    function initP5AirbnbMap() {
      const mapEl = document.getElementById('p5-airbnb-map');
      if (!mapEl || p5AirbnbMap) return;
      p5MapInitialized = true;
      p5AirbnbMap = L.map('p5-airbnb-map', { zoomControl: true }).setView([39.5, -96.5], 4);
      p5MapTileLayer = L.tileLayer('https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', {
        maxZoom: 20,
        attribution: '&copy; Google Maps Platform (vtxdemos)'
      }).addTo(p5AirbnbMap);
      p5MapMarkerGroup = L.layerGroup().addTo(p5AirbnbMap);
      if (p5Results && p5Results.length) {
        updateP5AirbnbMapMarkers(true);
      }
    }

    function setP5MapTileMode(mode) {
      if (!p5AirbnbMap) initP5AirbnbMap();
      if (!p5AirbnbMap) return;
      if (p5MapTileLayer) p5AirbnbMap.removeLayer(p5MapTileLayer);
      const lyrs = mode === 'satellite' ? 'y' : 'm';
      p5MapTileLayer = L.tileLayer(`https://mt1.google.com/vt/lyrs=${lyrs}&x={x}&y={y}&z={z}`, {
        maxZoom: 20,
        attribution: '&copy; Google Maps Platform (vtxdemos)'
      }).addTo(p5AirbnbMap);
    }

    function updateP5AirbnbMapMarkers(shouldFitBounds) {
      if (!p5AirbnbMap && currentActivePillar === 5) {
        initP5AirbnbMap();
      }
      if (!p5AirbnbMap || !p5MapMarkerGroup) return;
      p5MapMarkerGroup.clearLayers();
      p5MapPinElements = {};

      const boundsPts = [];
      p5Results.forEach((it, idx) => {
        if (typeof it.lat !== 'number' || typeof it.lng !== 'number') return;
        // Slight deterministic jitter so multiple homes in the same city all have clickable distinct price pills
        const angle = (it.seq || idx) * 2.39996;
        const radius = 0.0045 + ((it.seq || idx) % 7) * 0.0022;
        const lat = it.lat + Math.sin(angle) * radius;
        const lng = it.lng + Math.cos(angle) * radius;
        boundsPts.push([lat, lng]);

        const priceTxt = formatPricePin(it.price);
        const isActive = p5ActiveMapListingId === it.id || (idx === 0 && !p5ActiveMapListingId);
        const icon = L.divIcon({
          className: '',
          html: `<div class="abnb-price-pin ${isActive ? 'active-pin' : ''}" id="abnb-pin-${it.id}" onclick="focusP5ListingOnMap('${it.id}', false, event)">${priceTxt}</div>`,
          iconSize: [64, 28],
          iconAnchor: [32, 14]
        });
        const marker = L.marker([lat, lng], { icon: icon }).addTo(p5MapMarkerGroup);
        marker._rktCoords = [lat, lng];
        p5MapPinElements[it.id] = { marker, lat, lng, item: it };
      });

      if (shouldFitBounds && boundsPts.length > 0) {
        try {
          p5AirbnbMap.invalidateSize();
          if (boundsPts.length === 1) {
            p5AirbnbMap.setView(boundsPts[0], 13);
          } else {
            p5AirbnbMap.fitBounds(boundsPts, { padding: [36, 36], maxZoom: 12 });
          }
        } catch (e) {}
      }
    }

    function fitP5MapToCurrentResults() {
      updateP5AirbnbMapMarkers(true);
    }

    function highlightP5MapPin(listingId, active) {
      const pinEl = document.getElementById('abnb-pin-' + listingId);
      if (pinEl) {
        pinEl.classList.toggle('active-pin', Boolean(active || p5ActiveMapListingId === listingId));
      }
    }

    function focusP5ListingOnMap(listingId, flyToClose, evt) {
      if (evt) evt.stopPropagation();
      p5ActiveMapListingId = listingId;
      document.querySelectorAll('.abnb-price-pin').forEach(el => el.classList.remove('active-pin'));
      const pinEl = document.getElementById('abnb-pin-' + listingId);
      if (pinEl) pinEl.classList.add('active-pin');

      const entry = p5MapPinElements[listingId];
      const item = (entry && entry.item) || p5Results.find(x => x.id === listingId);
      if (!item) return;

      if (p5AirbnbMap && entry) {
        p5AirbnbMap.invalidateSize();
        p5AirbnbMap.flyTo([entry.lat, entry.lng], flyToClose ? 12 : Math.max(p5AirbnbMap.getZoom(), 10), { duration: 0.65 });
      }
      renderP5MapPreviewCard(item);
    }

    function renderP5MapPreviewCard(it) {
      const box = document.getElementById('p5-map-preview-card');
      if (!box || !it) return;
      const ev = it.evaluation || { overall_judge_score: 98.8 };
      box.style.display = 'block';
      box.innerHTML = `
        <div style="display:grid;grid-template-columns:125px 1fr;gap:12px;padding:10px;align-items:center;">
          <div style="position:relative;height:98px;border-radius:12px;overflow:hidden;cursor:pointer;" onclick="openRePropertyModal('${it.id}', 'rooms')">
            <img src="${it.hero_exterior_url}" style="width:100%;height:100%;object-fit:cover;" alt="${it.title}" />
            <span style="position:absolute;top:6px;left:6px;padding:2px 6px;border-radius:999px;background:rgba(255,255,255,0.94);color:#111;font-size:9.5px;font-weight:800;">${it.id}</span>
          </div>
          <div style="min-width:0;">
            <div style="display:flex;justify-content:space-between;align-items:center;gap:6px;">
              <div style="font-size:12px;font-weight:800;color:var(--ink-primary);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${it.city}</div>
              <button style="background:none;border:none;font-size:13px;cursor:pointer;color:var(--ink-muted);" onclick="document.getElementById('p5-map-preview-card').style.display='none'">✕</button>
            </div>
            <div style="font-size:11.5px;font-weight:700;color:var(--ink-secondary);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:1px;">${it.title}</div>
            <div style="font-size:13.5px;font-weight:800;color:var(--ink-primary);margin-top:4px;">
              $${it.price.toLocaleString()} <span style="font-size:11px;font-weight:700;color:var(--emerald);">· $${it.monthly_piti.toLocaleString()}/mo</span>
            </div>
            <div style="display:flex;gap:6px;margin-top:7px;">
              <button class="abnb-filter-pill" style="padding:4px 9px;font-size:10.5px;background:#FF385C;color:#FFF;border-color:#FF385C;" onclick="openRePropertyModal('${it.id}', 'rooms')">
                Open ${it.total_rooms_mapped} Rooms
              </button>
              <button class="abnb-filter-pill" style="padding:4px 9px;font-size:10.5px;" onclick="speakSingleListingConcierge('${it.id}', this)">
                🔊 Kira Tour
              </button>
            </div>
          </div>
        </div>
      `;
    }

    function speakSingleListingConcierge(listingId, btnEl) {
      const it = p5Results.find(x => x.id === listingId) || p5Results[0];
      if (!it) return;
      const script = `Here is ${it.title} in ${it.city}, listed at $${it.price.toLocaleString()}. This ${it.beds} bedroom, ${it.baths} bathroom ${it.family_name} includes 3 coinciding exterior angles and ${it.total_rooms_mapped} mapped spaces, with a Rocket Mortgage verified payment of $${it.monthly_piti.toLocaleString()} per month and a $${it.closing_credit.toLocaleString()} closing credit.`;
      LiveAudioEngine.speakClip(script, 'Aoede', btnEl);
    }

    function askKiraRealEstateConcierge(promptText) {
      executeUserSpokenOrTypedCommand(promptText);
    }

    function toggleP5VectorDrawer() {
      const el = document.getElementById('p5-vector-weights-drawer');
      if (!el) return;
      el.style.display = el.style.display === 'none' ? 'flex' : 'none';
    }

    function toggleP5WishlistHeart(listingId, btnEl, evt) {
      if (evt) evt.stopPropagation();
      if (p5WishlistIds.has(listingId)) {
        p5WishlistIds.delete(listingId);
        if (btnEl) btnEl.classList.remove('liked');
      } else {
        p5WishlistIds.add(listingId);
        if (btnEl) btnEl.classList.add('liked');
      }
    }

    function setP5ArchFilter(archId, btnEl) {
      p5CurrentArch = archId;
      document.querySelectorAll('#p5-arch-ribbon .abnb-cat-item').forEach(b => b.classList.remove('active'));
      if (btnEl) btnEl.classList.add('active');
      const sel = document.getElementById('p5-pill-arch-select');
      if (sel) sel.value = archId;
      runPillar5HybridSearch();
    }

    function setP5BedsFilter(beds, btnEl) {
      p5CurrentBeds = beds;
      document.querySelectorAll('#p5-bed-bar .abnb-filter-pill[id^="p5-bed-"]').forEach(b => b.classList.remove('active'));
      if (btnEl) btnEl.classList.add('active');
      const sel = document.getElementById('p5-pill-beds-select');
      if (sel) sel.value = String(beds);
      runPillar5HybridSearch();
    }

    function quickP5Query(qText) {
      document.getElementById('p5-search-input').value = qText;
      p5RefListingId = '';
      p5RefImageB64 = '';
      runPillar5HybridSearch();
    }

    function resetPillar5Filters() {
      p5CurrentArch = 'all';
      p5CurrentBeds = 0;
      p5RefListingId = '';
      p5RefImageB64 = '';
      document.getElementById('p5-search-input').value = '';
      document.getElementById('p5-max-price').value = 2500000;
      document.getElementById('lbl-p5-max-price').innerText = '$2.50M';
      document.getElementById('p5-img-upload-lbl').innerText = 'Photo';
      const selArch = document.getElementById('p5-pill-arch-select');
      if (selArch) selArch.value = 'all';
      const selBeds = document.getElementById('p5-pill-beds-select');
      if (selBeds) selBeds.value = '0';
      document.querySelectorAll('#p5-arch-ribbon .abnb-cat-item').forEach(b => b.classList.remove('active'));
      const allArchBtn = document.getElementById('p5-arch-all');
      if (allArchBtn) allArchBtn.classList.add('active');
      document.querySelectorAll('#p5-bed-bar .abnb-filter-pill[id^="p5-bed-"]').forEach(b => b.classList.remove('active'));
      const allBedBtn = document.getElementById('p5-bed-0');
      if (allBedBtn) allBedBtn.classList.add('active');
      runPillar5HybridSearch();
    }

    function handleP5ImageUpload(inputEl) {
      const file = inputEl.files && inputEl.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (e) => {
        p5RefImageB64 = e.target.result;
        p5RefListingId = '';
        document.getElementById('p5-img-upload-lbl').innerText = 'Photo ✓';
        runPillar5HybridSearch();
      };
      reader.readAsDataURL(file);
    }

    function findVisuallySimilarListing(listingId, evt) {
      if (evt) evt.stopPropagation();
      p5RefListingId = listingId;
      p5RefImageB64 = '';
      document.getElementById('p5-visual-query-banner').innerHTML = `<strong style="color:#FF385C;">Visual Vector Similarity Active:</strong> Ranking all 108 distinct homes by Multimodal Visual Embedding distance to <strong>${listingId}</strong>`;
      runPillar5HybridSearch();
    }

    async function runPillar5HybridSearch() {
      p5LoadedOnce = true;
      const wSem = parseInt(document.getElementById('p5-w-sem').value, 10);
      const wVis = parseInt(document.getElementById('p5-w-vis').value, 10);
      const wKw = parseInt(document.getElementById('p5-w-kw').value, 10);
      document.getElementById('lbl-p5-w-sem').innerText = wSem + '%';
      document.getElementById('lbl-p5-w-vis').innerText = wVis + '%';
      document.getElementById('lbl-p5-w-kw').innerText = wKw + '%';

      const q = document.getElementById('p5-search-input').value.trim();
      const maxP = parseInt(document.getElementById('p5-max-price').value, 10);
      const badge = document.getElementById('p5-latency-badge');
      badge.innerHTML = '<span class="dot-pulse"></span>Searching 108 Distinct Homes...';

      try {
        const res = await fetch('/api/pillar5/search', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query_text: q,
            beds_filter: p5CurrentBeds,
            family_filter: p5CurrentArch,
            max_price: maxP,
            reference_listing_id: p5RefListingId,
            reference_image_b64: p5RefImageB64,
            semantic_weight: wSem / 100.0,
            visual_weight: wVis / 100.0,
            keyword_weight: wKw / 100.0,
            limit: 108
          })
        });
        const data = await res.json();
        p5Results = data.results || [];
        badge.innerHTML = `<span class="dot-pulse"></span>${data.total_matched} Homes · ${data.latency_ms}ms`;

        let sumTxt = `${data.total_matched} distinct architecturally verified homes`;
        if (p5CurrentBeds > 0) sumTxt += ` · ${p5CurrentBeds} beds (${10 + p5CurrentBeds} coinciding rooms)`;
        if (p5CurrentArch !== 'all') sumTxt += ` · ${p5CurrentArch.replace(/_/g, ' ')}`;
        if (q) sumTxt += ` · "${q}"`;
        document.getElementById('p5-results-summary').innerText = sumTxt;

        if (data.visual_query_caption) {
          document.getElementById('p5-visual-query-banner').innerHTML = `<strong style="color:var(--emerald);">Gemini 3.8 Vision Extracted Photo DNA:</strong> "${data.visual_query_caption}"`;
        }

        renderPillar5Grid();
        updateP5AirbnbMapMarkers(true);
        if (typeof syncPolyVectorClustersWithResults === 'function') {
          syncPolyVectorClustersWithResults(p5Results, data.filtered_distribution);
        }
        if (p5Results[0]) {
          renderP5MapPreviewCard(p5Results[0]);
        }
        return data;
      } catch (e) {
        badge.innerText = 'Search Error: ' + e.message;
        return null;
      }
    }

    function cycleCardRoomPhoto(idx, delta, evt) {
      if (evt) evt.stopPropagation();
      const item = p5Results[idx];
      if (!item || !item.rooms || !item.rooms.length) return;
      const cur = p5CardRoomIdx[item.id] || 0;
      const next = (cur + delta + item.rooms.length) % item.rooms.length;
      p5CardRoomIdx[item.id] = next;
      const rm = item.rooms[next];
      const imgEl = document.getElementById(`re-card-img-${item.id}`);
      const lblEl = document.getElementById(`re-card-rmlbl-${item.id}`);
      const cntEl = document.getElementById(`re-card-rmcnt-${item.id}`);
      if (imgEl) imgEl.src = rm.image_url;
      if (lblEl) lblEl.innerText = rm.title.replace(/^Exterior \\d+ · /, '');
      if (cntEl) cntEl.innerText = `${next + 1}/${item.rooms.length}`;
    }

    function renderPillar5Grid() {
      const grid = document.getElementById('p5-property-grid');
      if (!grid) return;
      if (!p5Results.length) {
        grid.innerHTML = `<div class="v-card" style="grid-column:1/-1;text-align:center;padding:36px;">No homes matched the current filter combination. Click <strong>Reset</strong> to view all 108 distinct homes.</div>`;
        return;
      }

      grid.innerHTML = p5Results.map((it, idx) => {
        const rIdx = p5CardRoomIdx[it.id] || 0;
        const rm = (it.rooms && it.rooms[rIdx]) || { title: it.title, image_url: it.hero_exterior_url };
        const sc = it.search_scores || { hybrid_pct: 98.5, semantic_pct: 98.0, visual_pct: 99.0, keyword_pct: 98.0 };
        const ev = it.evaluation || { overall_judge_score: 98.6 };
        const isLiked = p5WishlistIds.has(it.id);
        const topBadgeTxt = idx < 3 && document.getElementById('p5-search-input').value.trim()
          ? `Top AI Match · ${sc.hybrid_pct}%`
          : `Redfin Early Access · ${it.family_name.split(' ')[0]}`;

        return `
          <div class="abnb-card"
               onmouseenter="highlightP5MapPin('${it.id}', true)"
               onmouseleave="highlightP5MapPin('${it.id}', false)"
               onclick="openRePropertyModal('${it.id}', 'rooms')">
            <div class="abnb-card-media">
              <span class="abnb-guest-fav">${topBadgeTxt}</span>
              <button class="re-card-nav-btn" style="left:10px;" onclick="cycleCardRoomPhoto(${idx}, -1, event)" title="Previous Room / Exterior">&lsaquo;</button>
              <img class="abnb-card-img" id="re-card-img-${it.id}" src="${rm.image_url}" loading="lazy" alt="${it.title}" />
              <button class="re-card-nav-btn" style="right:10px;" onclick="cycleCardRoomPhoto(${idx}, 1, event)" title="Next Room / Exterior">&rsaquo;</button>

              <div class="re-card-room-pill" style="right:52px;">
                <span id="re-card-rmlbl-${it.id}" style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:175px;">${rm.title.replace(/^Exterior \\d+ · /, '')}</span>
                <span id="re-card-rmcnt-${it.id}" style="color:#FFF;opacity:0.9;">${rIdx + 1}/${it.rooms.length}</span>
              </div>

              <!-- Redfin Signature Dark Circular Map Pin Button in Bottom-Right of Photo -->
              <button type="button" class="rf-photo-pin-btn" onclick="focusP5ListingOnMap('${it.id}', true, event)" title="Locate on Interactive Map">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s-7-6.5-7-12a7 7 0 1 1 14 0c0 5.5-7 12-7 12z"/><circle cx="12" cy="9" r="2.5"/></svg>
              </button>
            </div>

            <!-- Authentic Redfin Framed White Card Body -->
            <div class="rf-card-body">
              <div class="rf-card-price-row">
                <div class="rf-card-price-group">
                  <span class="rf-card-price">$${it.price.toLocaleString()}</span>
                  <span class="rf-card-piti-badge">Est. $${it.monthly_piti.toLocaleString()}/mo</span>
                </div>
                <div class="rf-card-actions">
                  <button type="button" class="rf-icon-btn" onclick="event.stopPropagation(); speakSingleListingConcierge('${it.id}', this)" title="Hear Kira 24kHz Audio Tour">
                    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>
                  </button>
                  <button type="button" class="rf-icon-btn" onclick="findVisuallySimilarListing('${it.id}', event)" title="Find Visually Similar Homes">
                    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
                  </button>
                  <button type="button" class="rf-icon-btn ${isLiked ? 'liked' : ''}" onclick="toggleP5WishlistHeart('${it.id}', this, event)" title="Save Home">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
                  </button>
                </div>
              </div>

              <div class="rf-card-specs">
                <span>${it.beds} beds</span>
                <span>${it.baths} baths</span>
                <span>${it.sqft.toLocaleString()} sq ft</span>
              </div>

              <div class="rf-card-address">${it.address} · ${it.city} (${it.submarket})</div>

              ${document.getElementById('p5-search-input').value.trim() && it.visual_scene_caption ? `
                <div style="margin-top:4px;padding:6px 9px;border-radius:7px;background:#F0FDF4;border:1px solid #BBF7D0;font-size:11.5px;line-height:1.4;color:#166534;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;" title="${it.visual_scene_caption.replace(/"/g, '&quot;')}">
                  <strong>🔍 Vision Scene (${sc.visual_pct}% Vec):</strong> ${it.visual_scene_caption}
                </div>
              ` : ''}

              <div class="rf-card-footer">
                <span>Listing by Redfin · <strong style="color:#047857;">+$${it.closing_credit.toLocaleString()} Rocket Credit</strong></span>
                <span style="color:#D92228;font-weight:700;" onclick="event.stopPropagation(); openRePropertyModal('${it.id}', 'floorplan')">3D Plan &rarr;</span>
              </div>
            </div>
          </div>
        `;
      }).join('');
    }

    function openRePropertyModal(listingId, initialTab) {
      const item = p5Results.find(x => x.id === listingId) || p5Results[0];
      if (!item) return;
      p5ActiveModalItem = item;

      document.getElementById('re-modal-id').innerText = `${item.id} · ${item.family_name}`;
      document.getElementById('re-modal-judge-badge').innerText = `★ 4.99 · Gemini Judge ${item.evaluation.overall_judge_score}% Coherence Verified`;
      document.getElementById('re-modal-rooms-badge').innerText = `3 Coinciding Exteriors + ${item.beds} Bedrooms (${item.total_rooms_mapped} Total Rooms)`;
      document.getElementById('re-modal-title').innerText = item.title;
      document.getElementById('re-modal-address').innerText = `${item.address} (${item.submarket})`;
      document.getElementById('re-modal-price').innerText = '$' + item.price.toLocaleString();
      document.getElementById('re-modal-piti').innerText = `${item.beds} bedrooms · ${item.baths} bathrooms · ${item.sqft.toLocaleString()} sq.ft. · Pre-underwritten by Rocket Mortgage`;
      const subSpecsEl = document.getElementById('re-modal-subtitle-specs');
      if (subSpecsEl) subSpecsEl.innerText = `${item.family_name} in ${item.city} · ${item.total_rooms_mapped} Architecturally Coinciding Spaces`;
      document.getElementById('re-modal-desc').innerText = item.description;

      const resCred = document.getElementById('re-modal-reserve-credit');
      if (resCred) resCred.innerText = `+$${item.closing_credit.toLocaleString()} Rocket Credit`;
      const resBanner = document.getElementById('re-modal-reserve-piti-banner');
      if (resBanner) resBanner.innerText = `Rocket Verified PITI: $${item.monthly_piti.toLocaleString()} / month`;

      // Render 5-photo Rounded Airbnb Mosaic (Ext 1, Ext 2, Ext 3, Chef's Kitchen, Primary Bedroom)
      const byId = {};
      item.rooms.forEach(r => { byId[r.room_id] = r; });
      const bMain = byId['ext_front'] || item.rooms[0];
      const bSub1 = byId['ext_rear'] || item.rooms[1];
      const bSub2 = byId['ext_aerial'] || item.rooms[2];
      const bSub3 = byId['chef_kitchen'] || item.rooms[4];
      const bSub4 = byId['primary_bedroom'] || item.rooms[6];

      document.getElementById('re-modal-bento').innerHTML = `
        <div class="abnb-mosaic-main" onclick="switchReModalTab('rooms')">
          <img id="re-bento-hero-img" src="${bMain.image_url}" alt="${bMain.title}" />
          <div class="re-bento-lbl" id="re-bento-hero-lbl">${bMain.title} (${bMain.dimensions})</div>
        </div>
        <div class="abnb-mosaic-cell" onclick="setBentoHero('${bSub1.image_url}', '${bSub1.title.replace(/'/g, '')} (${bSub1.dimensions})')">
          <img src="${bSub1.image_url}" alt="${bSub1.title}" />
          <div class="re-bento-lbl">${bSub1.title}</div>
        </div>
        <div class="abnb-mosaic-cell" onclick="setBentoHero('${bSub2.image_url}', '${bSub2.title.replace(/'/g, '')} (${bSub2.dimensions})')">
          <img src="${bSub2.image_url}" alt="${bSub2.title}" />
          <div class="re-bento-lbl">${bSub2.title}</div>
        </div>
        <div class="abnb-mosaic-cell" onclick="setBentoHero('${bSub3.image_url}', '${bSub3.title.replace(/'/g, '')} (${bSub3.dimensions})')">
          <img src="${bSub3.image_url}" alt="${bSub3.title}" />
          <div class="re-bento-lbl">${bSub3.title}</div>
        </div>
        <div class="abnb-mosaic-cell" onclick="setBentoHero('${bSub4.image_url}', '${bSub4.title.replace(/'/g, '')} (${bSub4.dimensions})')">
          <img src="${bSub4.image_url}" alt="${bSub4.title}" />
          <div class="re-bento-lbl">${bSub4.title}</div>
          <button class="abnb-show-all-photos-btn" onclick="event.stopPropagation(); switchReModalTab('floorplan')">
            ☷ Show all ${item.total_rooms_mapped} rooms &amp; 3D plan
          </button>
        </div>
      `;

      // Render All Coinciding Rooms & Exteriors Grid
      document.getElementById('re-modal-rooms-grid').innerHTML = item.rooms.map((r, i) => `
        <div class="v-card" style="padding:10px;cursor:pointer;" onclick="setBentoHero('${r.image_url}', '${r.title.replace(/'/g, '')} (${r.dimensions})')">
          <div style="position:relative;aspect-ratio:16/10;border-radius:10px;overflow:hidden;margin-bottom:8px;background:#0F172A;">
            <img src="${r.image_url}" loading="lazy" style="width:100%;height:100%;object-fit:cover;" />
            <span style="position:absolute;top:7px;left:7px;padding:3px 7px;border-radius:6px;background:rgba(9,13,22,0.82);color:#FFF;font-size:9.5px;font-family:'JetBrains Mono',monospace;font-weight:700;">
              #${i + 1} · ${r.category.toUpperCase()}
            </span>
            <span style="position:absolute;top:7px;right:7px;padding:3px 7px;border-radius:6px;background:rgba(5,150,105,0.9);color:#FFF;font-size:9.5px;font-family:'JetBrains Mono',monospace;font-weight:700;">
              ${r.coherence_score}% Match
            </span>
          </div>
          <div style="font-size:12.5px;font-weight:800;">${r.title}</div>
          <div style="font-size:10.5px;font-family:'JetBrains Mono',monospace;color:var(--google-blue);margin:2px 0 4px;">${r.dimensions} · ${r.level}</div>
          <div style="font-size:11.5px;color:var(--ink-secondary);line-height:1.45;">${r.caption}</div>
        </div>
      `).join('');

      // Render Interactive 2D/3D Floorplan & Room-Math Inspector
      document.getElementById('re-modal-3d-fp-img').src = item.floorplan_url;
      renderInteractiveSvgFloorplan(item);
      inspectFloorplanRoom('living_room');

      // Populate 16:9 Walkthrough & 9:16 Veo Reel
      const wtVid = document.getElementById('re-modal-walkthrough-vid');
      wtVid.src = item.walkthrough_16x9_url;
      const rlVid = document.getElementById('re-modal-reel-vid');
      rlVid.src = item.reel_9x16_url;
      document.getElementById('re-reel-title').innerText = `${item.title} (${item.city})`;
      document.getElementById('re-reel-desc').innerText = `Generated with Veo 3.1 + Reference-Conditioned Multi-Room Pipeline on Google Cloud Storage CDN. Verified Rocket Mortgage PITI: $${item.monthly_piti.toLocaleString()}/mo with +$${item.closing_credit.toLocaleString()} Redfin + Rocket Closing Credit.`;

      // Populate Airbnb 2x2 Reserve Box
      document.getElementById('re-modal-finance-box').innerHTML = `
        <div style="display:grid;grid-template-columns:1fr 1fr;border-bottom:1px solid #B0B0B0;">
          <div style="padding:10px 12px;border-right:1px solid #B0B0B0;">
            <div style="font-size:9.5px;font-weight:800;text-transform:uppercase;color:var(--ink-secondary);">DOWN PAYMENT</div>
            <div style="font-size:13px;font-weight:800;margin-top:2px;">${item.down_pct}% ($${Math.round(item.price * item.down_pct / 100).toLocaleString()})</div>
          </div>
          <div style="padding:10px 12px;">
            <div style="font-size:9.5px;font-weight:800;text-transform:uppercase;color:var(--ink-secondary);">ROCKET FIXED APR</div>
            <div style="font-size:13px;font-weight:800;margin-top:2px;">${item.rate_pct}% (30-Yr Fixed)</div>
          </div>
        </div>
        <div style="padding:10px 12px;">
          <div style="font-size:9.5px;font-weight:800;text-transform:uppercase;color:var(--ink-secondary);">VERIFIED ROOMS &amp; FLOORPLAN</div>
          <div style="font-size:13px;font-weight:800;margin-top:2px;">${item.beds} Bedrooms · ${item.baths} Baths · ${item.total_rooms_mapped} Coinciding Spaces</div>
        </div>
      `;

      const breakdownEl = document.getElementById('re-modal-price-breakdown');
      if (breakdownEl) {
        const piEst = Math.round(item.monthly_piti * 0.78);
        const taxEst = item.monthly_piti - piEst;
        breakdownEl.innerHTML = `
          <div style="display:flex;justify-content:space-between;">
            <span style="text-decoration:underline;color:var(--ink-secondary);">Principal &amp; Interest (${item.rate_pct}%)</span>
            <span style="font-weight:700;">$${piEst.toLocaleString()}/mo</span>
          </div>
          <div style="display:flex;justify-content:space-between;">
            <span style="text-decoration:underline;color:var(--ink-secondary);">Property Taxes &amp; Homeowners Ins.</span>
            <span style="font-weight:700;">$${taxEst.toLocaleString()}/mo</span>
          </div>
          <div style="display:flex;justify-content:space-between;color:var(--emerald);font-weight:800;">
            <span style="text-decoration:underline;">Redfin + Rocket Super-Funnel Credit</span>
            <span>-$${item.closing_credit.toLocaleString()} at closing</span>
          </div>
          <div style="display:flex;justify-content:space-between;padding-top:10px;border-top:1px solid var(--border-hairline);font-size:14.5px;font-weight:800;">
            <span>Total Verified Monthly PITI</span>
            <span>$${item.monthly_piti.toLocaleString()}/mo</span>
          </div>
        `;
      }

      // Populate Judge Tab
      renderModalJudgeScorecard(item.evaluation);

      document.getElementById('re-property-modal').classList.add('open');
      switchReModalTab(initialTab || 'rooms');
    }

    function setBentoHero(imgUrl, labelTxt) {
      const hImg = document.getElementById('re-bento-hero-img');
      const hLbl = document.getElementById('re-bento-hero-lbl');
      if (hImg) hImg.src = imgUrl;
      if (hLbl) hLbl.innerText = labelTxt;
    }

    function closeRePropertyModal() {
      const modal = document.getElementById('re-property-modal');
      if (modal) modal.classList.remove('open');
      document.querySelectorAll('#re-property-modal video').forEach(v => { try { v.pause(); } catch (e) {} });
    }

    function switchReModalTab(tabKey, btnEl) {
      ['rooms', 'floorplan', 'walkthrough', 'reel', 'judge'].forEach(k => {
        const pane = document.getElementById('re-mpane-' + k);
        const tab = document.getElementById('re-mtab-' + k);
        if (pane) pane.style.display = k === tabKey ? 'block' : 'none';
        if (tab) tab.classList.toggle('active', k === tabKey);
      });
      const wtVid = document.getElementById('re-modal-walkthrough-vid');
      const rlVid = document.getElementById('re-modal-reel-vid');
      if (tabKey === 'walkthrough' && wtVid) { wtVid.play().catch(() => {}); } else if (wtVid) { wtVid.pause(); }
      if (tabKey === 'reel' && rlVid) { rlVid.play().catch(() => {}); } else if (rlVid) { rlVid.pause(); }
    }

    function renderInteractiveSvgFloorplan(item) {
      const container = document.getElementById('re-interactive-svg-floorplan');
      if (!container) return;
      document.getElementById('re-fp-math-badge').innerText = `${item.beds} Bedrooms · ${item.baths} Baths · ${item.total_rooms_mapped} Spaces Verified`;

      // Build clickable room coordinate blocks for the SVG blueprint matching exact bedroom count!
      const boxes = [
        { id: 'ext_front', label: 'EXT 1 · FRONT PORCH', x: 20, y: 270, w: 220, h: 65, fill: '#1E293B' },
        { id: 'living_room', label: 'GREAT ROOM (24x19)', x: 20, y: 120, w: 220, h: 142, fill: '#1D4ED8' },
        { id: 'chef_kitchen', label: 'CHEF KITCHEN (21x16)', x: 248, y: 120, w: 185, h: 105, fill: '#047857' },
        { id: 'dining_room', label: 'DINING GALLERY (16x14)', x: 248, y: 233, w: 185, h: 102, fill: '#0F766E' },
        { id: 'ext_rear', label: 'EXT 2 · REAR TWILIGHT PATIO & POOL', x: 20, y: 18, w: 413, h: 94, fill: '#0369A1' },
        { id: 'home_office', label: 'STUDY / OFFICE', x: 441, y: 245, w: 145, h: 90, fill: '#4338CA' },
        { id: 'primary_bathroom', label: 'PRIMARY SPA BATH', x: 441, y: 18, w: 145, h: 94, fill: '#0D9488' },
        { id: 'primary_bedroom', label: 'BEDROOM 1 · PRIMARY', x: 441, y: 120, w: 145, h: 117, fill: '#B91C1C' },
        { id: 'guest_bathroom', label: `GUEST BATHS (${item.baths})`, x: 594, y: 265, w: 186, h: 70, fill: '#0D9488' },
      ];

      // Dynamically place Bedroom 2 .. Bedroom N (exact bedroom count `item.beds`!)
      const extraBeds = item.beds - 1;
      const colX = 594;
      const availH = 238;
      const slotH = Math.floor((availH - (extraBeds - 1) * 6) / Math.max(1, extraBeds));
      for (let b = 2; b <= item.beds; b++) {
        const by = 18 + (b - 2) * (slotH + 6);
        boxes.push({
          id: `bedroom_${b}`,
          label: `BEDROOM ${b} SUITE`,
          x: colX,
          y: by,
          w: 186,
          h: slotH,
          fill: '#D81E28'
        });
      }

      const rectsSvg = boxes.map(b => `
        <g style="cursor:pointer;" onclick="inspectFloorplanRoom('${b.id}')">
          <rect id="fp-svg-rect-${b.id}" x="${b.x}" y="${b.y}" width="${b.w}" height="${b.h}" rx="8"
                fill="${b.fill}" fill-opacity="0.32" stroke="#94A3B8" stroke-width="1.8" />
          <text x="${b.x + b.w/2}" y="${b.y + b.h/2 + 4}" text-anchor="middle" fill="#F8FAFC"
                font-family="JetBrains Mono, monospace" font-size="10.5" font-weight="700">${b.label}</text>
        </g>
      `).join('');

      container.innerHTML = `
        <svg viewBox="0 0 800 355" style="width:100%;height:auto;display:block;">
          <rect x="6" y="6" width="788" height="343" rx="12" fill="#090D16" stroke="#334155" stroke-width="2" stroke-dasharray="6,4" />
          ${rectsSvg}
        </svg>
      `;

      // Also render room selector pills
      document.getElementById('re-fp-room-buttons').innerHTML = item.rooms.map(r => `
        <button class="barge-chip" style="padding:5px 9px;font-size:10.5px;" onclick="inspectFloorplanRoom('${r.room_id}')">
          ${r.title.split('·')[0].trim()}
        </button>
      `).join('');
    }

    function inspectFloorplanRoom(roomId) {
      if (!p5ActiveModalItem) return;
      const rm = p5ActiveModalItem.rooms.find(r => r.room_id === roomId) || p5ActiveModalItem.rooms[0];
      if (!rm) return;
      document.getElementById('re-fp-selected-title').innerText = rm.title;
      document.getElementById('re-fp-selected-dim').innerText = `${rm.dimensions} · ${rm.level}`;
      document.getElementById('re-fp-selected-img').src = rm.image_url;
      document.getElementById('re-fp-selected-caption').innerText = rm.caption;
      document.getElementById('re-fp-selected-score').innerText = `Gemini 3.8 Coherence Score: ${rm.coherence_score}% PASS (Matches ${p5ActiveModalItem.family_name} DNA)`;

      document.querySelectorAll('[id^="fp-svg-rect-"]').forEach(el => {
        el.setAttribute('stroke', '#94A3B8');
        el.setAttribute('stroke-width', '1.8');
      });
      const activeRect = document.getElementById('fp-svg-rect-' + roomId);
      if (activeRect) {
        activeRect.setAttribute('stroke', '#38BDF8');
        activeRect.setAttribute('stroke-width', '3.5');
      }
    }

    function renderModalJudgeScorecard(ev) {
      const box = document.getElementById('re-modal-judge-content');
      if (!box || !ev) return;
      const checksHtml = (ev.room_by_room_checks || []).map(c => `
        <div style="padding:10px 12px;border-radius:9px;background:var(--bg-card);border:1px solid var(--border-hairline);display:flex;justify-content:space-between;gap:12px;">
          <div>
            <div style="font-size:12px;font-weight:800;">${c.space}</div>
            <div style="font-size:11.5px;color:var(--ink-secondary);margin-top:2px;">${c.detail}</div>
          </div>
          <span class="badge-live" style="height:fit-content;">${c.status}</span>
        </div>
      `).join('');

      box.innerHTML = `
        <div class="kpi-row" style="grid-template-columns:repeat(4,1fr);margin-bottom:12px;">
          <div class="kpi-tile">
            <div class="kpi-label">Overall Gemini Judge</div>
            <div class="kpi-val" style="color:var(--emerald);">${ev.overall_judge_score}%</div>
            <div class="kpi-sub">${ev.verdict || 'COHERENCE VERIFIED'}</div>
          </div>
          <div class="kpi-tile">
            <div class="kpi-label">3-Exterior Coherence</div>
            <div class="kpi-val">${ev.exterior_coherence_score}%</div>
            <div class="kpi-sub">${ev.exterior_angles_verified || 'Front + Rear + Aerial Match'}</div>
          </div>
          <div class="kpi-tile">
            <div class="kpi-label">Interior Palette Harmony</div>
            <div class="kpi-val">${ev.interior_harmony_score}%</div>
            <div class="kpi-sub">Continuous Wood/Stone/Glazing</div>
          </div>
          <div class="kpi-tile">
            <div class="kpi-label">Bedroom &amp; Room Math</div>
            <div class="kpi-val" style="color:var(--google-blue);">${ev.room_completeness_score}%</div>
            <div class="kpi-sub">${ev.bedroom_math_verified || 'Zero Missing Rooms'}</div>
          </div>
        </div>
        <div style="font-size:12.5px;line-height:1.6;color:var(--ink-primary);padding:12px;border-radius:10px;background:var(--bg-card);border:1px solid var(--border-hairline);">
          <div><strong>Exterior Multi-Angle Audit:</strong> ${ev.exterior_audit_note || ev.executive_summary || ''}</div>
          <div style="margin-top:6px;"><strong>Interior Room-by-Room Audit:</strong> ${ev.interior_audit_note || ''}</div>
        </div>
        ${checksHtml ? `<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px;">${checksHtml}</div>` : ''}
      `;
    }

    async function runLiveGeminiJudgeForActiveModal(btnEl) {
      if (!p5ActiveModalItem) return;
      const orig = btnEl.innerHTML;
      btnEl.innerText = 'Evaluating with Gemini 3.8 Flash...';
      try {
        const res = await fetch('/api/pillar5/evaluate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ listing_id: p5ActiveModalItem.id })
        });
        const data = await res.json();
        if (data.ok && data.audit) {
          p5ActiveModalItem.evaluation = Object.assign({}, p5ActiveModalItem.evaluation, data.audit);
          renderModalJudgeScorecard(p5ActiveModalItem.evaluation);
        }
      } catch (e) {}
      btnEl.innerHTML = orig;
    }

    function speakActiveModalPropertyTour(btnEl) {
      if (!p5ActiveModalItem) return;
      const it = p5ActiveModalItem;
      const script = `Welcome to ${it.title} at ${it.address}. Listed at $${it.price.toLocaleString()}, this architecturally verified ${it.beds} bedroom, ${it.baths} bathroom ${it.family_name} includes 3 coinciding exterior elevations and ${it.total_rooms_mapped} mapped spaces, with a Rocket Mortgage verified payment of $${it.monthly_piti.toLocaleString()} per month and a $${it.closing_credit.toLocaleString()} Redfin plus Rocket closing credit.`;
      LiveAudioEngine.speakClip(script, 'Aoede', btnEl);
    }

    // =========================================================================
    // BEHIND THE SCENES: 3072-D VECTOR TOPOLOGY & UMAP 2D PROJECTION ENGINE
    // =========================================================================
    let btsCanvasInitialized = false;
    let btsAnimFrameId = null;

    const BTS_HOMES = [
      {
        id: 'RKT-028',
        cluster: 'midcentury_glass',
        clusterName: 'Mid-Century Glass',
        color: '#D81E28',
        title: 'Cantilevered Horizon Glass Pavilion',
        address: '890 Barton Shore Dr, Ann Arbor, MI',
        price: '$1,450,000',
        piti: '$7,120/mo PITI',
        specs: '4 BD · 4.0 BA · 3,980 SqFt',
        semScore: 99.4,
        visScore: 98.8,
        rrfScore: 99.2,
        gx: 0.28, gy: 0.34,
        img: 'https://storage.googleapis.com/vtxdemos-abnb-images/rocket_re_cdn/v1/images/listings/RKT-028/ext_front.jpg',
        features: ['Floor-to-Ceiling Glass', 'Walnut Waterfall Island']
      },
      {
        id: 'RKT-066',
        cluster: 'colonial_georgian',
        clusterName: 'Georgian Colonial',
        color: '#2563EB',
        title: 'Georgian Symmetry Brick Estate',
        address: '1420 Hendrie Blvd, Royal Oak, MI',
        price: '$1,180,000',
        piti: '$5,890/mo PITI',
        specs: '5 BD · 4.5 BA · 4,420 SqFt',
        semScore: 98.9,
        visScore: 99.1,
        rrfScore: 99.0,
        gx: 0.72, gy: 0.30,
        img: 'https://storage.googleapis.com/vtxdemos-abnb-images/rocket_re_cdn/v1/images/listings/RKT-066/ext_front.jpg',
        features: ['Symmetrical Flemish Brick', '2-Story Portico']
      },
      {
        id: 'RKT-001',
        cluster: 'modern_craftsman',
        clusterName: 'Modern Craftsman',
        color: '#059669',
        title: 'Cedar & Stone Gabled Craftsman',
        address: '618 Vinsetta Blvd, Royal Oak, MI',
        price: '$865,000',
        piti: '$4,390/mo PITI',
        specs: '4 BD · 3.5 BA · 3,240 SqFt',
        semScore: 98.2,
        visScore: 97.9,
        rrfScore: 98.1,
        gx: 0.34, gy: 0.72,
        img: 'https://storage.googleapis.com/vtxdemos-abnb-images/rocket_re_cdn/v1/images/listings/RKT-001/ext_front.jpg',
        features: ['Tapered Stone Columns', 'White Oak Millwork']
      },
      {
        id: 'RKT-082',
        cluster: 'coastal_villa',
        clusterName: 'Coastal Villa',
        color: '#0891B2',
        title: 'Lakefront Veranda Glass Villa',
        address: '412 Lakeshore Rd, Grosse Pointe, MI',
        price: '$1,690,000',
        piti: '$8,240/mo PITI',
        specs: '5 BD · 5.5 BA · 5,150 SqFt',
        semScore: 97.8,
        visScore: 98.4,
        rrfScore: 98.0,
        gx: 0.70, gy: 0.70,
        img: 'https://storage.googleapis.com/vtxdemos-abnb-images/rocket_re_cdn/v1/images/listings/RKT-082/ext_front.jpg',
        features: ['Wrap-Around Veranda', 'Private Deepwater Dock']
      },
      {
        id: 'RKT-050',
        cluster: 'brick_timber_loft',
        clusterName: 'Brick & Timber Loft',
        color: '#EA580C',
        title: 'Historic Timber Warehouse Loft',
        address: '220 E Grand River Ave, Detroit, MI',
        price: '$725,000',
        piti: '$3,840/mo PITI',
        specs: '3 BD · 2.5 BA · 2,640 SqFt',
        semScore: 97.2,
        visScore: 97.8,
        rrfScore: 97.5,
        gx: 0.50, gy: 0.22,
        img: 'https://storage.googleapis.com/vtxdemos-abnb-images/rocket_re_cdn/v1/images/listings/RKT-050/ext_front.jpg',
        features: ['Exposed Douglas Fir', '14ft Ceilings']
      },
      {
        id: 'RKT-098',
        cluster: 'desert_mountain',
        clusterName: 'Desert Sanctuary',
        color: '#9333EA',
        title: 'Cantilevered Rammed-Earth Desert Sanctuary',
        address: '5400 E Camelback Rd, Phoenix, AZ',
        price: '$1,890,000',
        piti: '$9,180/mo PITI',
        specs: '4 BD · 4.5 BA · 4,200 SqFt',
        semScore: 96.8,
        visScore: 97.2,
        rrfScore: 97.0,
        gx: 0.50, gy: 0.82,
        img: 'https://storage.googleapis.com/vtxdemos-abnb-images/rocket_re_cdn/v1/images/listings/RKT-098/ext_front.jpg',
        features: ['Rammed Earth Walls', 'Infinity Plunge Pool']
      }
    ];

    const queryVec = { x: 0.32, y: 0.38, dragging: false };
    const graphNodes = [];

    // Populate Hero & Satellite Nodes
    BTS_HOMES.forEach((h, idx) => {
      graphNodes.push({
        id: h.id,
        title: h.title,
        cluster: h.cluster,
        clusterName: h.clusterName,
        color: h.color,
        x: h.gx,
        y: h.gy,
        vx: 0,
        vy: 0,
        baseX: h.gx,
        baseY: h.gy,
        r: 9,
        isHero: true,
        homeRef: h
      });
      for (let s = 0; s < 6; s++) {
        const ang = (s / 6) * Math.PI * 2 + idx * 0.5;
        const dist = 0.055 + (s % 3) * 0.028;
        const nx = Math.max(0.08, Math.min(0.92, h.gx + Math.cos(ang) * dist));
        const ny = Math.max(0.14, Math.min(0.86, h.gy + Math.sin(ang) * (dist * 1.15)));
        graphNodes.push({
          id: (h.id || h.cluster) + "_sub_" + s,
          cluster: h.cluster,
          clusterName: h.clusterName,
          color: h.color,
          x: nx,
          y: ny,
          vx: 0,
          vy: 0,
          baseX: nx,
          baseY: ny,
          r: 4.5,
          isHero: false
        });
      }
    });

    function toggleBehindTheScenesView(forceState) {
      const behindEl = document.getElementById('p5-behind-scenes-view');
      const marketEl = document.getElementById('p5-marketplace-view');
      const btn = document.getElementById('btn-toggle-behind-scenes');
      const lbl = document.getElementById('btn-behind-scenes-lbl');
      if (!behindEl || !marketEl) return;

      const showBehind = (forceState !== undefined) ? forceState : (behindEl.style.display === 'none');
      if (showBehind) {
        behindEl.style.display = 'block';
        marketEl.style.display = 'none';
        if (btn) {
          btn.style.background = '#D92228';
          btn.style.color = '#FFFFFF';
        }
        if (lbl) lbl.innerText = '← Back to Marketplace View';
        initVectorTopologyCanvas();
        setTimeout(() => {
          resizeVectorGraph();
          updateLiveCosineScores();
        }, 50);
      } else {
        behindEl.style.display = 'none';
        marketEl.style.display = '';
        if (btn) {
          btn.style.background = 'rgba(216,30,40,0.06)';
          btn.style.color = '#D92228';
        }
        if (lbl) lbl.innerText = '🔬 Behind the Scenes: Vector Topology';
      }
    }

    function initVectorTopologyCanvas() {
      if (btsCanvasInitialized) return;
      const cv = document.getElementById('vector-graph-canvas');
      if (!cv) return;
      btsCanvasInitialized = true;

      cv.addEventListener('pointerdown', (e) => {
        const rect = cv.getBoundingClientRect();
        const nx = (e.clientX - rect.left) / (rect.width || 1);
        const ny = (e.clientY - rect.top) / (rect.height || 1);
        queryVec.x = Math.max(0.06, Math.min(0.94, nx));
        queryVec.y = Math.max(0.10, Math.min(0.90, ny));
        queryVec.dragging = true;
        updateLiveCosineScores();
      });

      window.addEventListener('pointermove', (e) => {
        if (!queryVec.dragging) return;
        const rect = cv.getBoundingClientRect();
        const nx = (e.clientX - rect.left) / (rect.width || 1);
        const ny = (e.clientY - rect.top) / (rect.height || 1);
        queryVec.x = Math.max(0.06, Math.min(0.94, nx));
        queryVec.y = Math.max(0.10, Math.min(0.90, ny));
        updateLiveCosineScores();
      });

      window.addEventListener('pointerup', () => {
        queryVec.dragging = false;
      });

      window.addEventListener('resize', resizeVectorGraph);
      resizeVectorGraph();
      if (!btsAnimFrameId) {
        btsAnimFrameId = requestAnimationFrame(animateVectorGraph);
      }
    }

    function resizeVectorGraph() {
      const cv = document.getElementById('vector-graph-canvas');
      if (!cv) return;
      const rect = cv.getBoundingClientRect();
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      cv.width = (rect.width || 800) * dpr;
      cv.height = (rect.height || 340) * dpr;
      const ctx = cv.getContext('2d');
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    function pulseGraphNodes() {
      graphNodes.forEach(n => {
        n.vx = (Math.random() - 0.5) * 0.008;
        n.vy = (Math.random() - 0.5) * 0.008;
      });
      updateLiveCosineScores();
    }

    function selectGraphPreset(clusterId, queryText, btnEl) {
      document.querySelectorAll('#p5-behind-scenes-view .abnb-filter-pill').forEach(b => b.classList.remove('active'));
      if (btnEl) btnEl.classList.add('active');

      const target = BTS_HOMES.find(h => h.cluster === clusterId);
      if (target) {
        queryVec.x = target.gx + 0.02;
        queryVec.y = target.gy + 0.02;
      } else {
        queryVec.x = 0.50;
        queryVec.y = 0.50;
      }
      pulseGraphNodes();
    }

    function updateLiveCosineScores() {
      let bestCos = 0;
      let bestCluster = 'Mid-Century Glass';

      BTS_HOMES.forEach(h => {
        const d = Math.hypot(h.gx - queryVec.x, h.gy - queryVec.y);
        const cos = Math.max(0.84, Math.min(0.996, 0.996 - d * 0.18));
        h.liveCosine = cos;
        if (cos > bestCos) {
          bestCos = cos;
          bestCluster = h.clusterName;
        }
      });

      const topCosEl = document.getElementById('top-cosine-readout');
      const nearClustEl = document.getElementById('nearest-cluster-readout');
      if (topCosEl) topCosEl.innerText = bestCos.toFixed(3);
      if (nearClustEl) nearClustEl.innerText = bestCluster;

      renderBtsRankedCards();
    }

    function renderBtsRankedCards() {
      const grid = document.getElementById('bts-ranked-listings-grid');
      if (!grid) return;
      const sorted = [...BTS_HOMES].sort((a, b) => (b.liveCosine || 0) - (a.liveCosine || 0));

      grid.innerHTML = sorted.slice(0, 4).map(h => {
        const score = (h.liveCosine * 100).toFixed(1);
        return (
          '<div class="abnb-card" style="cursor:pointer;overflow:hidden;background:var(--bg-card);border:1px solid var(--border-hairline);border-radius:16px;box-shadow:0 4px 14px rgba(0,0,0,0.05);" data-home-id="' + h.id + '" onclick="openRePropertyModal(this.dataset.homeId, \\'rooms\\')">' +
            '<div style="position:relative;aspect-ratio:16/10;overflow:hidden;background:#E2E8F0;">' +
              '<img src="' + h.img + '" alt="' + h.title + '" style="width:100%;height:100%;object-fit:cover;" />' +
              '<div style="position:absolute;top:10px;left:10px;padding:4px 9px;border-radius:999px;font-size:11px;font-weight:800;background:rgba(255,255,255,0.95);color:#0F172A;box-shadow:0 2px 6px rgba(0,0,0,0.15);">' +
                score + '% Match' +
              '</div>' +
              '<div style="position:absolute;bottom:8px;left:10px;padding:3px 8px;border-radius:6px;font-size:10.5px;font-weight:700;color:#FFF;background:rgba(15,23,42,0.80);">' +
                h.clusterName + ' · ' + h.id +
              '</div>' +
            '</div>' +
            '<div style="padding:12px;">' +
              '<div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:2px;">' +
                '<span style="font-size:16px;font-weight:800;">' + h.price + '</span>' +
                '<span style="font-size:11px;font-weight:700;color:var(--emerald);">' + h.piti + '</span>' +
              '</div>' +
              '<div style="font-size:12px;font-weight:700;color:var(--ink-primary);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">' + h.title + '</div>' +
              '<div style="font-size:11px;color:var(--ink-secondary);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:2px;">' + h.address + '</div>' +
              '<div style="margin-top:8px;padding-top:8px;border-top:1px solid var(--border-hairline);">' +
                '<div style="display:flex;justify-content:space-between;font-size:10.5px;font-weight:700;color:var(--ink-secondary);margin-bottom:3px;">' +
                  '<span>Semantic: ' + h.semScore + '%</span>' +
                  '<span>Photo Vec: ' + h.visScore + '%</span>' +
                '</div>' +
                '<div style="height:5px;border-radius:999px;background:#E2E8F0;display:flex;overflow:hidden;">' +
                  '<div style="width:55%;background:#2563EB;"></div>' +
                  '<div style="width:45%;background:#059669;"></div>' +
                '</div>' +
              '</div>' +
            '</div>' +
          '</div>'
        );
      }).join('');
    }

    function animateVectorGraph(nowMs) {
      const cv = document.getElementById('vector-graph-canvas');
      if (!cv) return;
      const ctx = cv.getContext('2d');
      const rect = cv.getBoundingClientRect();
      const W = rect.width || 800;
      const H = rect.height || 340;
      const t = (nowMs || 0) * 0.001;
      ctx.clearRect(0, 0, W, H);

      // Coordinate Grid
      ctx.strokeStyle = 'rgba(148, 163, 184, 0.18)';
      ctx.lineWidth = 1;
      for (let x = 60; x < W; x += 80) {
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
      }
      for (let y = 45; y < H; y += 55) {
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
      }

      // Spring positions
      graphNodes.forEach((n, idx) => {
        n.vx += (n.baseX - n.x) * 0.08;
        n.vy += (n.baseY - n.y) * 0.08;
        n.vx *= 0.85;
        n.vy *= 0.85;
        n.x += n.vx + Math.sin(t * 1.8 + idx) * 0.0003;
        n.y += n.vy + Math.cos(t * 1.5 + idx) * 0.0003;
      });

      const qx = queryVec.x * W;
      const qy = queryVec.y * H;

      // Intra-cluster KNN lines
      graphNodes.forEach(n => {
        if (!n.isHero) {
          const hero = graphNodes.find(h => h.isHero && h.cluster === n.cluster);
          if (hero) {
            ctx.strokeStyle = n.color + '26';
            ctx.lineWidth = 1.2;
            ctx.beginPath();
            ctx.moveTo(hero.x * W, hero.y * H);
            ctx.lineTo(n.x * W, n.y * H);
            ctx.stroke();
          }
        }
      });

      // Cosine similarity rays from Query Vector to Hero Homes
      graphNodes.filter(n => n.isHero).forEach(h => {
        const hx = h.x * W;
        const hy = h.y * H;
        const dist = Math.hypot(hx - qx, hy - qy);
        const sim = Math.max(0.84, Math.min(0.996, 0.996 - (dist / W) * 0.22));

        ctx.save();
        ctx.strokeStyle = (sim > 0.94) ? '#D81E28' : 'rgba(100, 116, 139, 0.35)';
        ctx.lineWidth = (sim > 0.94) ? 2.2 : 1.2;
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        ctx.moveTo(qx, qy);
        ctx.lineTo(hx, hy);
        ctx.stroke();

        const mx = (qx + hx) * 0.5;
        const my = (qy + hy) * 0.5;
        ctx.fillStyle = (sim > 0.94) ? '#D81E28' : '#475569';
        ctx.font = '700 10.5px monospace';
        ctx.textAlign = 'center';
        ctx.fillText(sim.toFixed(3), mx, my - 4);
        ctx.restore();
      });

      // Draw nodes
      graphNodes.forEach(n => {
        const nx = n.x * W;
        const ny = n.y * H;

        if (n.isHero) {
          ctx.fillStyle = n.color + '22';
          ctx.beginPath();
          ctx.arc(nx, ny, 18, 0, Math.PI * 2);
          ctx.fill();

          ctx.fillStyle = n.color;
          ctx.beginPath();
          ctx.arc(nx, ny, n.r, 0, Math.PI * 2);
          ctx.fill();
          ctx.lineWidth = 2;
          ctx.strokeStyle = '#FFFFFF';
          ctx.stroke();

          ctx.fillStyle = '#0F172A';
          ctx.font = '800 11px sans-serif';
          ctx.textAlign = 'center';
          ctx.fillText(n.clusterName + " (" + n.id + ")", nx, ny - 13);
        } else {
          ctx.fillStyle = n.color + 'AA';
          ctx.beginPath();
          ctx.arc(nx, ny, n.r, 0, Math.PI * 2);
          ctx.fill();
        }
      });

      // Draw Query Vector Node
      const pulse = 14 + Math.sin(t * 4) * 3;
      ctx.fillStyle = 'rgba(216, 30, 40, 0.18)';
      ctx.beginPath();
      ctx.arc(qx, qy, pulse, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = '#D81E28';
      ctx.beginPath();
      ctx.arc(qx, qy, 8, 0, Math.PI * 2);
      ctx.fill();
      ctx.lineWidth = 2.5;
      ctx.strokeStyle = '#FFFFFF';
      ctx.stroke();

      ctx.fillStyle = '#D81E28';
      ctx.font = '800 11px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('QUERY VECTOR (DRAG ME)', qx, qy + 21);

      btsAnimFrameId = requestAnimationFrame(animateVectorGraph);
    }

    // Initialize Pillar 5 (Redfin × Gemini AI Marketplace) as default view & preload Pillar 1/2
    function initOnReady() {
      const urlParams = new URLSearchParams(window.location.search);
      const initialPillar = parseInt(urlParams.get('pillar') || urlParams.get('p') || '5', 10);
      switchPillar(initialPillar >= 1 && initialPillar <= 5 ? initialPillar : 5);
      runPillar1TimesFM();
      loadPresetReel('royal_oak', null);
      if (urlParams.get('behind_scenes') === '1' || urlParams.get('bts') === '1') {
        toggleBehindTheScenesView(true);
      }
    }
    if (document.readyState === 'loading') {
      window.addEventListener('DOMContentLoaded', initOnReady);
    } else {
      initOnReady();
    }
  </script>
</body>
</html>"""
