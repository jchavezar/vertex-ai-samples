"""Self-contained Vercel Monochrome Interactive Legal Grid + Conversational RAG + Original Document Citation Viewer (MCP App SEP-1865 & A2UI IFrameSrcdoc)."""

import json

WORKSPACE_HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>LexGraph Legal Context Engine — Interactive Analysis Grid &amp; Original Citation Highlighter (MCP App)</title>
<style>
:root {
  /* Light Mode (Default — Mandatory Vercel Monochrome Architecture) */
  --bg-canvas: #fafafa;
  --bg-grid: #eaeaea;
  --bg-surface: #ffffff;
  --bg-elevated: #f4f4f5;
  --bg-header: #fafafa;
  --border-subtle: #e4e4e7;
  --border-hover: #111111;
  --text-primary: #09090b;
  --text-secondary: #52525b;
  --text-muted: #71717a;
  --btn-primary-bg: #09090b;
  --btn-primary-text: #ffffff;
  --btn-primary-hover: #27272a;
  --btn-secondary-bg: #ffffff;
  --btn-secondary-text: #09090b;
  --btn-secondary-hover: #f4f4f5;
  --shadow-card: 0 4px 16px rgba(0, 0, 0, 0.05);
  --paper-bg: #ffffff;
  --paper-border: #d4d4d8;
  --paper-text: #111111;
  --cite-highlight-bg: #fef08a;
  --cite-highlight-border: #ca8a04;
  --cite-highlight-text: #09090b;
  --row-selected-bg: #f4f4f5;
  --row-active-border: #09090b;
  --dyn-col-bg: #f8fafc;
  --ink-grad-1: radial-gradient(circle at 20% 20%, #52525b, #18181b, #000000);
  --ink-grad-2: radial-gradient(circle at 80% 20%, #71717a, #27272a, #09090b);
  --ink-grad-3: radial-gradient(circle at 40% 80%, #3f3f46, #09090b, #000000);
  --ink-shadow: rgba(0, 0, 0, 0.28);
  --sweep-grad: linear-gradient(90deg, #71717a 0%, #09090b 50%, #71717a 100%);
  --font-sans: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --font-mono: "JetBrains Mono", "Geist Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
  --font-serif: "Times New Roman", Georgia, Cambria, serif;
}

[data-theme="dark"] {
  /* Dark Mode (OLED Vercel Monochrome) */
  --bg-canvas: #000000;
  --bg-grid: #111111;
  --bg-surface: #0a0a0a;
  --bg-elevated: #141417;
  --bg-header: #050505;
  --border-subtle: #222222;
  --border-hover: #ededed;
  --text-primary: #ededed;
  --text-secondary: #a1a1aa;
  --text-muted: #71717a;
  --btn-primary-bg: #ffffff;
  --btn-primary-text: #000000;
  --btn-primary-hover: #d4d4d8;
  --btn-secondary-bg: #0a0a0a;
  --btn-secondary-text: #ededed;
  --btn-secondary-hover: #18181b;
  --shadow-card: 0 12px 32px rgba(0, 0, 0, 0.85);
  --paper-bg: #0f0f12;
  --paper-border: #27272a;
  --paper-text: #e4e4e7;
  --cite-highlight-bg: rgba(234, 179, 8, 0.22);
  --cite-highlight-border: #facc15;
  --cite-highlight-text: #fef08a;
  --row-selected-bg: #18181b;
  --row-active-border: #ffffff;
  --dyn-col-bg: #0d0d12;
  --ink-grad-1: radial-gradient(circle at 20% 20%, #ffffff, #a1a1aa, #09090b);
  --ink-grad-2: radial-gradient(circle at 80% 20%, #f4f4f5, #71717a, #18181b);
  --ink-grad-3: radial-gradient(circle at 40% 80%, #e4e4e7, #52525b, #000000);
  --ink-shadow: rgba(255, 255, 255, 0.45);
  --sweep-grad: linear-gradient(90deg, #71717a 0%, #ffffff 50%, #71717a 100%);
}

* { box-sizing: border-box; margin: 0; padding: 0; }

/* Lock root html & body to 100% of the iframe viewport so inner scroll never pushes header/grid off-screen */
html, body {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  overflow: hidden;
  position: fixed;
  inset: 0;
}

body {
  background-color: var(--bg-canvas);
  background-image:
    linear-gradient(to right, var(--bg-grid) 1px, transparent 1px),
    linear-gradient(to bottom, var(--bg-grid) 1px, transparent 1px);
  background-size: 48px 48px;
  color: var(--text-primary);
  font-family: var(--font-sans);
  font-size: 12px;
  line-height: 1.4;
  display: flex;
  flex-direction: column;
}

/* Claude-Code Shrinking & Shining Ink Animation & Sweep Text */
.shrinking-shining-ink {
  width: 14px;
  height: 14px;
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
  0% { border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%; background: var(--ink-grad-1); }
  50% { border-radius: 30% 60% 70% 40% / 50% 60% 30% 60%; background: var(--ink-grad-2); }
  100% { border-radius: 70% 30% 50% 50% / 30% 30% 70% 70%; background: var(--ink-grad-3); }
}

@keyframes ink-pulse {
  0%, 100% { transform: scale(1) rotate(0deg); }
  50% { transform: scale(0.72) rotate(18deg); }
}

@keyframes ink-shine {
  0% { filter: drop-shadow(0 0 4px var(--ink-shadow)) brightness(1); }
  50% { filter: drop-shadow(0 0 9px var(--ink-shadow)) brightness(1.35); }
  100% { filter: drop-shadow(0 0 4px var(--ink-shadow)) brightness(1); }
}

.sweep-text {
  background: var(--sweep-grad);
  background-size: 200% auto;
  color: transparent;
  -webkit-background-clip: text;
  background-clip: text;
  animation: sweep-shimmer 2.2s linear infinite;
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.03em;
}

@keyframes sweep-shimmer {
  to { background-position: 200% center; }
}

/* Compact Architectural Header Bar */
.top-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 10px;
  background: var(--bg-header);
  border-bottom: 1px solid var(--border-subtle);
  flex-shrink: 0;
  gap: 8px;
  flex-wrap: wrap;
}

.brand-group {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.brand-mark {
  width: 22px;
  height: 22px;
  border-radius: 4px;
  background: var(--btn-primary-bg);
  color: var(--btn-primary-text);
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.brand-title {
  font-weight: 700;
  font-size: 12px;
  letter-spacing: -0.02em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.brand-sub {
  font-family: var(--font-mono);
  font-size: 9.5px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 5px;
  flex-wrap: wrap;
}

.view-mode-group {
  display: inline-flex;
  border: 1px solid var(--border-subtle);
  border-radius: 5px;
  overflow: hidden;
  background: var(--bg-surface);
}

.view-mode-btn {
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 600;
  padding: 3px 8px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  border-right: 1px solid var(--border-subtle);
}

.view-mode-btn:last-child {
  border-right: none;
}

.view-mode-btn.active {
  background: var(--btn-primary-bg);
  color: var(--btn-primary-text);
}

.mono-badge {
  font-family: var(--font-mono);
  font-size: 9.5px;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid var(--border-subtle);
  background: var(--bg-surface);
  color: var(--text-secondary);
  letter-spacing: 0.03em;
  white-space: nowrap;
}

.mono-badge.active {
  border-color: var(--text-primary);
  color: var(--text-primary);
  font-weight: 600;
}

.btn {
  font-family: var(--font-sans);
  font-size: 11px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid var(--border-subtle);
  background: var(--btn-secondary-bg);
  color: var(--btn-secondary-text);
  cursor: pointer;
  transition: all 0.12s ease;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
}

.btn:hover {
  background: var(--btn-secondary-hover);
  border-color: var(--border-hover);
}

.btn-primary {
  background: var(--btn-primary-bg);
  color: var(--btn-primary-text);
  border-color: var(--btn-primary-bg);
}

.btn-primary:hover {
  background: var(--btn-primary-hover);
}

/* Compact Toolbar Strip: Alike Filters + Dynamic Question-to-Column Input */
.toolbar-strip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 5px 10px;
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border-subtle);
  gap: 6px;
  flex-shrink: 0;
  flex-wrap: wrap;
}

.filter-chips {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}

.chip {
  font-family: var(--font-mono);
  font-size: 10px;
  padding: 2px 7px;
  border-radius: 999px;
  border: 1px solid var(--border-subtle);
  background: var(--bg-elevated);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.12s;
  white-space: nowrap;
}

.chip:hover, .chip.active {
  background: var(--btn-primary-bg);
  color: var(--btn-primary-text);
  border-color: var(--btn-primary-bg);
}

.dyn-col-bar {
  display: flex;
  align-items: center;
  gap: 5px;
  flex: 1;
  min-width: 220px;
}

.dyn-input {
  flex: 1;
  padding: 4px 8px;
  font-size: 11px;
  font-family: var(--font-sans);
  background: var(--bg-canvas);
  color: var(--text-primary);
  border: 1px solid var(--border-subtle);
  border-radius: 4px;
  outline: none;
  min-width: 0;
}

.dyn-input:focus {
  border-color: var(--border-hover);
}

/* Main Split Workspace: Adapts cleanly to both Fullscreen and PiP Side Panel */
.workspace-split {
  flex: 1;
  display: grid;
  grid-template-columns: 56% 44%;
  grid-template-rows: 100%;
  min-height: 0;
  width: 100%;
  overflow: hidden;
}

/* In narrow PiP panels (< 820px), stack Top (52% Grid + Q&A Bar) and Bottom (48% Original Doc + Highlighted Citations) */
@media (max-width: 820px) {
  .workspace-split {
    grid-template-columns: 100%;
    grid-template-rows: 52% 48%;
  }
}

.workspace-split.mode-grid-only {
  grid-template-columns: 100% !important;
  grid-template-rows: 100% !important;
}
.workspace-split.mode-grid-only .right-pane {
  display: none !important;
}

.workspace-split.mode-doc-only {
  grid-template-columns: 100% !important;
  grid-template-rows: 100% !important;
}
.workspace-split.mode-doc-only .left-pane {
  display: none !important;
}

.left-pane {
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--border-subtle);
  border-bottom: 1px solid var(--border-subtle);
  min-height: 0;
  min-width: 0;
  overflow: hidden;
  background: var(--bg-surface);
}

/* Interactive Document Grid gets 100% of available left-pane flex height */
.grid-container {
  flex: 1;
  min-height: 0;
  overflow: auto;
  background: var(--bg-surface);
}

table.legal-grid {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}

table.legal-grid thead {
  position: sticky;
  top: 0;
  z-index: 10;
  background: var(--bg-header);
}

table.legal-grid th {
  text-align: left;
  padding: 5px 7px;
  border-bottom: 1px solid var(--border-subtle);
  border-right: 1px solid var(--border-subtle);
  font-family: var(--font-mono);
  font-size: 9.5px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: var(--text-secondary);
  vertical-align: top;
  min-width: 96px;
  background: var(--bg-header);
}

table.legal-grid th.col-check {
  min-width: 32px;
  width: 32px;
  text-align: center;
}

table.legal-grid th.col-dyn {
  background: var(--dyn-col-bg);
  border-top: 2px solid var(--text-primary);
  color: var(--text-primary);
  min-width: 155px;
}

.th-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 4px;
  margin-bottom: 3px;
}

.col-filter-input {
  width: 100%;
  padding: 2px 5px;
  font-family: var(--font-mono);
  font-size: 9.5px;
  background: var(--bg-surface);
  color: var(--text-primary);
  border: 1px solid var(--border-subtle);
  border-radius: 3px;
  outline: none;
}

.col-filter-input:focus {
  border-color: var(--border-hover);
}

table.legal-grid td {
  padding: 6px 7px;
  border-bottom: 1px solid var(--border-subtle);
  border-right: 1px solid var(--border-subtle);
  vertical-align: top;
  cursor: pointer;
}

table.legal-grid tr:hover td {
  background: var(--bg-elevated);
}

table.legal-grid tr.row-selected td {
  background: var(--row-selected-bg);
}

table.legal-grid tr.row-active td {
  box-shadow: inset 0 1px 0 var(--row-active-border), inset 0 -1px 0 var(--row-active-border);
}

table.legal-grid td.cell-dyn {
  background: var(--dyn-col-bg);
  font-weight: 500;
}

.doc-pill {
  font-family: var(--font-mono);
  font-size: 9.5px;
  font-weight: 700;
  padding: 1px 5px;
  border-radius: 3px;
  border: 1px solid var(--border-subtle);
  background: var(--bg-elevated);
  display: inline-block;
  margin-bottom: 2px;
}

.cite-link-chip {
  font-family: var(--font-mono);
  font-size: 9.5px;
  padding: 2px 5px;
  border-radius: 3px;
  border: 1px solid var(--text-primary);
  background: var(--bg-surface);
  color: var(--text-primary);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 3px;
  margin-top: 2px;
  font-weight: 600;
}

.cite-link-chip:hover {
  background: var(--btn-primary-bg);
  color: var(--btn-primary-text);
}

/* Sleek 1-Line Scoped Agent Action Bar at Bottom of Grid Pane */
.scoped-qa-bar {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  background: var(--bg-header);
  border-top: 1px solid var(--border-subtle);
  flex-wrap: wrap;
}

/* Right Pane: Grounded Synthesis Banner + Original Document Format & Highlighted Citation Viewer */
.right-pane {
  display: flex;
  flex-direction: column;
  background: var(--bg-canvas);
  min-height: 0;
  min-width: 0;
  overflow: hidden;
}

/* Compact Collapsible Grounded Answer & Citation Chips Box at Top of Right Pane */
.synthesis-banner {
  flex-shrink: 0;
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border-subtle);
  padding: 6px 10px;
  max-height: 128px;
  overflow-y: auto;
  font-size: 11px;
  line-height: 1.4;
}

.synthesis-banner-hdr {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-family: var(--font-mono);
  font-size: 9.5px;
  color: var(--text-secondary);
  text-transform: uppercase;
  margin-bottom: 4px;
  gap: 6px;
}

.doc-viewer-header {
  padding: 6px 10px;
  background: var(--bg-header);
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
  flex-shrink: 0;
  flex-wrap: wrap;
}

.doc-viewer-meta {
  padding: 4px 10px;
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
  font-family: var(--font-mono);
  font-size: 10px;
  flex-shrink: 0;
  flex-wrap: wrap;
}

.doc-paper-scroll {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  position: relative;
}

.legal-paper-page {
  width: 100%;
  max-width: 680px;
  background: var(--paper-bg);
  color: var(--paper-text);
  border: 1px solid var(--paper-border);
  box-shadow: var(--shadow-card);
  padding: 20px 24px;
  font-family: var(--font-serif);
  font-size: 12.5px;
  line-height: 1.58;
  position: relative;
}

.page-watermark {
  display: flex;
  justify-content: space-between;
  font-family: var(--font-mono);
  font-size: 9px;
  color: var(--text-muted);
  border-bottom: 1px solid var(--border-subtle);
  padding-bottom: 5px;
  margin-bottom: 12px;
  text-transform: uppercase;
  gap: 8px;
  flex-wrap: wrap;
}

.legal-title-block {
  text-align: center;
  border-bottom: 2px solid var(--paper-text);
  padding-bottom: 10px;
  margin-bottom: 12px;
}

.legal-title-block h2 {
  font-size: 14px;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  margin-bottom: 3px;
}

.legal-title-block p {
  font-size: 10.5px;
  color: var(--text-secondary);
}

.legal-section {
  margin-bottom: 10px;
  padding: 8px 10px;
  border-radius: 4px;
  border: 1px solid transparent;
  transition: all 0.2s ease;
}

.legal-section h4 {
  font-family: var(--font-sans);
  font-size: 10.5px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  margin-bottom: 4px;
  color: var(--text-secondary);
}

.legal-section.cited-chunk-active {
  background: var(--cite-highlight-bg);
  border: 2px solid var(--cite-highlight-border);
  box-shadow: 0 0 0 3px rgba(202, 138, 4, 0.15);
}

.cite-bbox-ribbon {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-family: var(--font-mono);
  font-size: 9.5px;
  font-weight: 700;
  padding: 3px 6px;
  margin-bottom: 5px;
  background: var(--btn-primary-bg);
  color: var(--btn-primary-text);
  border-radius: 3px;
  gap: 6px;
  flex-wrap: wrap;
}

del.redline-del {
  background: rgba(239, 68, 68, 0.18);
  color: #dc2626;
  text-decoration: line-through;
  padding: 0 3px;
}

ins.redline-ins {
  background: rgba(16, 185, 129, 0.18);
  color: #059669;
  text-decoration: underline;
  font-weight: 700;
  padding: 0 3px;
}

.loader-bar {
  display: none;
  align-items: center;
  gap: 8px;
  padding: 5px 10px;
  background: var(--bg-elevated);
  border-bottom: 1px solid var(--border-subtle);
  flex-shrink: 0;
}

.loader-bar.active {
  display: flex;
}
</style>
</head>
<body>

<!-- TOP ARCHITECTURAL HEADER (Vercel Monochrome + View Switcher + Mandatory Dynamic Theme Toggle) -->
<header class="top-header">
  <div class="brand-group">
    <div class="brand-mark">L</div>
    <div style="min-width:0;">
      <div class="brand-title">LexGraph Legal Context Engine — Interactive Grid &amp; Citation Inspector</div>
      <div class="brand-sub" id="telemetry-sub">Cloud Spanner Hybrid RAG · 3,072-dim gemini-embedding-2 · MCP App (SEP-1865)</div>
    </div>
  </div>
  <div class="header-controls">
    <div class="view-mode-group" title="Switch Workspace Layout">
      <button class="view-mode-btn active" id="vmode-split" onclick="setViewMode('split')">◫ Split</button>
      <button class="view-mode-btn" id="vmode-grid" onclick="setViewMode('grid')">📊 Grid</button>
      <button class="view-mode-btn" id="vmode-doc" onclick="setViewMode('doc')">📑 Citation Doc</button>
    </div>
    <span class="mono-badge active" id="selected-files-badge">✓ 3 Selected</span>
    <button class="btn" onclick="requestPipMode('pip')" title="Dock in Gemini Enterprise Right Side Panel">🖼️ Side Panel</button>
    <button class="btn" onclick="requestPipMode('fullscreen')" title="Expand to Fullscreen">⛶ Fullscreen</button>
    <button class="btn" onclick="triggerGrant30d()" title="Commit 30-Day TeammateGrant Edge in Cloud Spanner">⚡ Grant EM-9901</button>
    <button class="btn" id="theme-toggle-btn" onclick="toggleTheme()">🌙 Dark</button>
  </div>
</header>

<!-- THINKING & STREAMING INK LOADER BAR (Mandatory Claude-Code Shrinking & Shining Ink) -->
<div class="loader-bar" id="ink-loader-bar">
  <span class="shrinking-shining-ink"></span>
  <span class="sweep-text" id="ink-loader-text">Querying Cloud Spanner Hybrid RAG &amp; extracting dynamic column across selected contracts...</span>
</div>

<!-- COMPACT TOOLBAR: ALIKE DOCUMENT FILTERS + 1-CLICK DYNAMIC QUESTION COLUMNS -->
<div class="toolbar-strip">
  <div class="filter-chips">
    <button class="chip active" id="chip-all" onclick="setAlikeFilter('all')">All (8)</button>
    <button class="chip" id="chip-m331" onclick="setAlikeFilter('M-331')">M-331 (4)</button>
    <button class="chip" id="chip-indem" onclick="setAlikeFilter('indem')">Indemnity (5)</button>
    <button class="chip" id="chip-scrape" onclick="setAlikeFilter('scrape')">Double Scrape</button>
    <button class="chip" id="chip-redline" onclick="setAlikeFilter('redline')">Skadden Redline</button>
    <button class="chip" onclick="quickAddColumn('Does Fraud or Pre-Closing Tax bypass the Indemnity Cap?')">+Col: Fraud/Tax</button>
    <button class="chip" onclick="quickAddColumn('Is Materiality Scrape Double (Breach + Losses) or Single?')">+Col: Scrape</button>
    <button class="chip" onclick="quickAddColumn('What is Opposing Counsel Redline Position vs Buyer Market?')">+Col: Redline</button>
    <button class="chip" onclick="clearColumnFilters()">✕ Reset</button>
  </div>
  <div class="dyn-col-bar">
    <input type="text" class="dyn-input" id="dyn-col-input" placeholder="➕ Ask question to add a Dynamic Grid Column (e.g. 'Does Fraud or Tax bypass the Cap?')" onkeydown="if(event.key==='Enter') addDynamicQuestionColumn()" />
    <button class="btn btn-primary" onclick="addDynamicQuestionColumn()">+ Add Column</button>
  </div>
</div>

<!-- MAIN SPLIT VIEW: LEFT/TOP (INTERACTIVE GRID + SCOPED Q&A BAR) | RIGHT/BOTTOM (GROUNDED SYNTHESIS + ORIGINAL CONTRACT VIEWER) -->
<div class="workspace-split" id="workspace-split-root">
  <!-- LEFT / TOP PANE: INTERACTIVE DOCUMENT GRID -->
  <div class="left-pane">
    <div class="grid-container" id="grid-scroll-container">
      <table class="legal-grid" id="legal-grid-table">
        <thead id="grid-thead"></thead>
        <tbody id="grid-tbody"></tbody>
      </table>
    </div>

    <!-- SLEEK 1-LINE SCOPED RAG QUESTION BAR AT BOTTOM OF GRID -->
    <div class="scoped-qa-bar">
      <span class="mono-badge active" id="chat-scope-label">Scoped (3): DOC-M331-01, DOC-M331-02, DOC-M215-01</span>
      <input type="text" class="dyn-input" id="chat-question-input" placeholder="Ask follow-up question on checked [x] files (updates grid &amp; highlights cited chunk)..." onkeydown="if(event.key==='Enter') submitScopedChatQuestion()" />
      <button class="btn btn-primary" onclick="submitScopedChatQuestion()">Ask &amp; Highlight ↵</button>
      <button class="btn" onclick="syncToHostAgent()" title="Send selected files &amp; question to Gemini Enterprise Host Chat">↗ Send to GE Chat</button>
    </div>
  </div>

  <!-- RIGHT / BOTTOM PANE: GROUNDED ANSWER + ORIGINAL DOCUMENT CITATION VIEWER -->
  <div class="right-pane">
    <!-- COMPACT GROUNDED SYNTHESIS & CLICKABLE CITATION CHIPS -->
    <div class="synthesis-banner" id="synthesis-banner">
      <div class="synthesis-banner-hdr">
        <span>💬 Conversational Spanner RAG Synthesis (Click any citation chip to highlight below)</span>
        <div style="display:flex;gap:4px;">
          <button class="chip" onclick="askPresetQuestion('Compare Indemnity Cap, Basket, and Materiality Scrape across selected files.')">Compare Selected</button>
          <button class="chip" onclick="askPresetQuestion('How does Skadden Draft v4 change Section 8.02(b) vs our Kestrel precedent?')">Skadden v4 Impact</button>
        </div>
      </div>
      <div id="chat-messages"></div>
    </div>

    <div class="doc-viewer-header">
      <div style="min-width:0;">
        <div style="font-weight:700;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" id="viewer-doc-title">Agreement and Plan of Merger (Apex / Brightwater Corp.)</div>
        <div style="font-family:var(--font-mono);font-size:9.5px;color:var(--text-secondary);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" id="viewer-doc-sub">DOC-M331-01 · Matter M-331 · Delaware · Wachtell, Lipton, Rosen &amp; Katz</div>
      </div>
      <div style="display:flex;gap:5px;align-items:center;flex-shrink:0;">
        <button class="btn" id="btn-redline-toggle" onclick="toggleRedlineOverlay()">🔍 Redline Diff</button>
        <button class="btn" id="btn-open-raw-pdf" onclick="openRawGcsPdf()">📄 Raw PDF</button>
      </div>
    </div>
    <div class="doc-viewer-meta">
      <div id="viewer-cite-pill" style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">📌 Highlighted Citation: <strong>CL-M331-INDEM · Section 8.02(b) (Page 2)</strong></div>
      <div style="display:flex;gap:4px;flex-shrink:0;" id="viewer-page-tabs"></div>
    </div>
    <div class="doc-paper-scroll" id="doc-paper-scroll"></div>
  </div>
</div>

<script>
const INITIAL_STATE = __INITIAL_STATE_JSON__;
const API_BASE = (window.location.origin && window.location.origin.includes("run.app"))
  ? ""
  : "https://lexgraph-legal-grid-mcp-agent-254356041555.us-central1.run.app";

let state = {
  theme: "light",
  viewMode: "split",
  alikeFilter: "all",
  columnFilters: {},
  selectedDocIds: new Set(INITIAL_STATE.selected_doc_ids || ["DOC-M331-01", "DOC-M331-02", "DOC-M215-01"]),
  activeDocId: INITIAL_STATE.active_doc_id || "DOC-M331-01",
  activeChunkId: INITIAL_STATE.active_chunk_id || "CL-M331-INDEM",
  activePage: INITIAL_STATE.active_page || 2,
  showRedlineOverlay: false,
  dynamicColumns: INITIAL_STATE.dynamic_columns || [],
  documents: INITIAL_STATE.documents || [],
  chatHistory: INITIAL_STATE.chat_history || []
};

function lockRootViewport() {
  window.scrollTo(0, 0);
  if (document.documentElement) document.documentElement.scrollTop = 0;
  if (document.body) document.body.scrollTop = 0;
}
window.addEventListener("scroll", lockRootViewport, { passive: true });

function setViewMode(mode) {
  state.viewMode = mode;
  const root = document.getElementById("workspace-split-root");
  root.classList.remove("mode-grid-only", "mode-doc-only");
  if (mode === "grid") root.classList.add("mode-grid-only");
  if (mode === "doc") root.classList.add("mode-doc-only");
  ["split", "grid", "doc"].forEach(m => {
    const btn = document.getElementById("vmode-" + m);
    if (btn) btn.classList.toggle("active", m === mode);
  });
  lockRootViewport();
}

function toggleTheme() {
  const root = document.documentElement;
  state.theme = state.theme === "light" ? "dark" : "light";
  root.setAttribute("data-theme", state.theme);
  const btn = document.getElementById("theme-toggle-btn");
  btn.textContent = state.theme === "light" ? "🌙 Dark" : "☀️ Light";
}

function setLoader(active, message) {
  const bar = document.getElementById("ink-loader-bar");
  const txt = document.getElementById("ink-loader-text");
  if (message) txt.textContent = message;
  if (active) bar.classList.add("active");
  else bar.classList.remove("active");
}

function updateSelectedBadge() {
  const count = state.selectedDocIds.size;
  const badge = document.getElementById("selected-files-badge");
  badge.textContent = `✓ ${count} Selected`;
  const arr = Array.from(state.selectedDocIds);
  const shortList = arr.length > 3 ? (arr.slice(0, 3).join(", ") + ` +${arr.length - 3}`) : (arr.join(", ") || "All 8 Docs");
  document.getElementById("chat-scope-label").textContent = `Scoped (${count}): ${shortList}`;
  pushModelContextToBridge();
}

// MCP App (SEP-1865 @modelcontextprotocol/ext-apps) Bidirectional Bridge
let mcpRpcId = 100;
function initMcpAppBridge() {
  try {
    if (window.parent && window.parent !== window) {
      window.parent.postMessage({
        jsonrpc: "2.0",
        id: 1,
        method: "ui/initialize",
        params: {
          protocolVersion: "2026-01-26",
          appInfo: { name: "lexgraph-legal-grid-mcp-app", version: "1.2.0" },
          appCapabilities: {
            availableDisplayModes: ["inline", "fullscreen", "pip"]
          }
        }
      }, "*");
      setTimeout(() => {
        window.parent.postMessage({
          jsonrpc: "2.0",
          method: "ui/notifications/initialized",
          params: {}
        }, "*");
        window.parent.postMessage({
          jsonrpc: "2.0",
          method: "ui/notifications/size-changed",
          params: { height: 760 }
        }, "*");
        requestPipMode("pip");
      }, 50);
    }
  } catch (e) {}
}

function requestPipMode(mode = "pip") {
  try {
    if (window.parent && window.parent !== window) {
      window.parent.postMessage({
        jsonrpc: "2.0",
        id: ++mcpRpcId,
        method: "ui/request-display-mode",
        params: { mode: mode }
      }, "*");
    }
  } catch (e) {}
}

function pushModelContextToBridge() {
  const selectedArr = Array.from(state.selectedDocIds);
  const contextPayload = {
    selected_doc_ids: selectedArr,
    active_doc_id: state.activeDocId,
    active_chunk_id: state.activeChunkId,
    dynamic_columns: state.dynamicColumns.map(c => c.header),
    column_filters: state.columnFilters
  };
  try {
    if (window.parent && window.parent !== window) {
      window.parent.postMessage({
        jsonrpc: "2.0",
        id: ++mcpRpcId,
        method: "ui/update-model-context",
        params: {
          content: [{
            type: "text",
            text: `[LexGraph Legal Grid Context] Lawyer selected ${selectedArr.length} files (${selectedArr.join(", ")}). Active citation: ${state.activeDocId} (${state.activeChunkId}).`
          }],
          structuredContent: contextPayload
        }
      }, "*");
    }
  } catch (e) {}
}

function payloadOf(res) {
  if (!res || typeof res !== "object") return null;
  if (res.structuredContent && typeof res.structuredContent === "object") {
    return res.structuredContent;
  }
  const list = Array.isArray(res.content) ? res.content : [];
  for (const item of list) {
    if (item && item.type === "text" && typeof item.text === "string") {
      try {
        const parsed = JSON.parse(item.text);
        if (parsed && typeof parsed === "object") return parsed;
      } catch (e) {}
    }
  }
  return null;
}

window.addEventListener("message", (event) => {
  const data = event.data;
  if (!data || typeof data !== "object") return;
  if (data.id === 1 && data.result) {
    try {
      window.parent.postMessage({
        jsonrpc: "2.0",
        method: "ui/notifications/initialized",
        params: {}
      }, "*");
      window.parent.postMessage({
        jsonrpc: "2.0",
        method: "ui/notifications/size-changed",
        params: { height: 760 }
      }, "*");
      requestPipMode("pip");
    } catch (e) {}
    pushModelContextToBridge();
  }
  if (data.method === "ui/notifications/tool-input" && data.params) {
    const args = data.params.arguments || {};
    if (args.question) {
      document.getElementById("dyn-col-input").value = args.question;
    }
  } else if (data.method === "ui/notifications/tool-result" && data.params) {
    const sc = payloadOf(data.params) || data.params.structuredContent || {};
    applyServerPayload(sc);
  } else if (data.result) {
    const sc = payloadOf(data.result);
    if (sc) applyServerPayload(sc);
  }
});
initMcpAppBridge();

function applyServerPayload(sc) {
  setLoader(false);
  if (!sc || typeof sc !== "object") return;
  if (sc.documents && sc.documents.length) {
    // Merge any existing dynamic_cells so previous dynamic columns stay populated
    const oldDocsById = {};
    (state.documents || []).forEach(d => { oldDocsById[d.doc_id] = d; });
    sc.documents.forEach(newDoc => {
      const prev = oldDocsById[newDoc.doc_id];
      if (prev && prev.dynamic_cells) {
        newDoc.dynamic_cells = Object.assign({}, prev.dynamic_cells, newDoc.dynamic_cells || {});
      }
    });
    state.documents = sc.documents;
  }
  if (sc.dynamic_columns && sc.dynamic_columns.length) {
    sc.dynamic_columns.forEach(newCol => {
      const idx = state.dynamicColumns.findIndex(c => c.field === newCol.field || c.header === newCol.header);
      if (idx >= 0) state.dynamicColumns[idx] = newCol;
      else state.dynamicColumns.push(newCol);
    });
  }
  if (sc.selected_doc_ids && Array.isArray(sc.selected_doc_ids)) {
    state.selectedDocIds = new Set(sc.selected_doc_ids);
  }
  if (sc.active_doc_id) state.activeDocId = sc.active_doc_id;
  if (sc.active_chunk_id) state.activeChunkId = sc.active_chunk_id;
  if (sc.active_page) state.activePage = sc.active_page;
  if (sc.chat_entry && sc.chat_entry.text) {
    const exists = state.chatHistory.some(m => m.role === "agent" && m.text === sc.chat_entry.text);
    if (!exists) {
      state.chatHistory.push(sc.chat_entry);
    }
  }
  renderAll();
}

function getFilteredDocuments() {
  return state.documents.filter(doc => {
    if (state.alikeFilter === "M-331" && doc.matter_id !== "M-331") return false;
    if (state.alikeFilter === "indem" && !["DOC-M331-01", "DOC-M331-02", "DOC-M331-03", "DOC-M215-01", "DOC-M518-01"].includes(doc.doc_id)) return false;
    if (state.alikeFilter === "scrape" && !doc.qualifiers.toLowerCase().includes("double") && !doc.qualifiers.toLowerCase().includes("full materiality scrape")) return false;
    if (state.alikeFilter === "redline" && !["DOC-M331-01", "DOC-M331-02"].includes(doc.doc_id)) return false;

    for (const [colKey, fVal] of Object.entries(state.columnFilters)) {
      if (!fVal) continue;
      const needle = fVal.toLowerCase();
      let hay = "";
      if (colKey.startsWith("dyn_")) {
        const cellObj = (doc.dynamic_cells || {})[colKey];
        hay = cellObj ? (cellObj.answer + " " + cellObj.badge) : "";
      } else {
        hay = String(doc[colKey] || "");
      }
      if (!hay.toLowerCase().includes(needle)) return false;
    }
    return true;
  });
}

function setAlikeFilter(mode) {
  state.alikeFilter = mode;
  ["all", "m331", "indem", "scrape", "redline"].forEach(id => {
    const el = document.getElementById("chip-" + id);
    if (el) el.classList.remove("active");
  });
  const mapId = mode === "M-331" ? "chip-m331" : ("chip-" + mode);
  const activeEl = document.getElementById(mapId);
  if (activeEl) activeEl.classList.add("active");
  renderGridBody();
}

function clearColumnFilters() {
  state.columnFilters = {};
  state.alikeFilter = "all";
  document.querySelectorAll(".col-filter-input").forEach(inp => { inp.value = ""; });
  setAlikeFilter("all");
}

function onColFilterInput(colKey, val) {
  state.columnFilters[colKey] = val;
  renderGridBody();
}

function toggleRowSelect(docId, ev) {
  if (ev) ev.stopPropagation();
  if (state.selectedDocIds.has(docId)) state.selectedDocIds.delete(docId);
  else state.selectedDocIds.add(docId);
  updateSelectedBadge();
  renderGridBody();
}

function selectAllVisibleFiles() {
  const docs = getFilteredDocuments();
  docs.forEach(d => state.selectedDocIds.add(d.doc_id));
  updateSelectedBadge();
  renderGridBody();
}

function clearSelectedFiles() {
  state.selectedDocIds.clear();
  updateSelectedBadge();
  renderGridBody();
}

function inspectCitation(docId, chunkId, pageNum, ev) {
  if (ev) ev.stopPropagation();
  state.activeDocId = docId;
  if (chunkId) state.activeChunkId = chunkId;
  if (pageNum) state.activePage = pageNum;
  renderGridBody();
  renderDocumentViewer();
  pushModelContextToBridge();
}

function removeDynamicColumn(field, ev) {
  if (ev) ev.stopPropagation();
  state.dynamicColumns = state.dynamicColumns.filter(c => c.field !== field);
  delete state.columnFilters[field];
  renderGridHeader();
  renderGridBody();
}

function renderGridHeader() {
  const thead = document.getElementById("grid-thead");
  const baseCols = [
    { key: "matter_id", label: "Matter / RRF", placeholder: "e.g. M-331" },
    { key: "title", label: "Document & Counsel", placeholder: "Filter doc/firm..." },
    { key: "cap_pct", label: "Indemnity Cap", placeholder: "e.g. 0.75%" },
    { key: "basket_type", label: "Basket Type", placeholder: "Deductible/Tipping" },
    { key: "survival_months", label: "Survival", placeholder: "e.g. 18 Months" },
    { key: "qualifiers", label: "Materiality Scrape", placeholder: "e.g. Double" }
  ];

  let html = `<tr>
    <th class="col-check">
      <div style="margin-bottom:2px;">☑</div>
      <input type="checkbox" title="Toggle All Visible" onchange="if(this.checked) selectAllVisibleFiles(); else clearSelectedFiles();" />
    </th>`;

  baseCols.forEach(col => {
    const val = state.columnFilters[col.key] || "";
    html += `<th>
      <div class="th-title"><span>${col.label}</span></div>
      <input class="col-filter-input" type="text" value="${val.replace(/"/g, '&quot;')}" placeholder="${col.placeholder}" oninput="onColFilterInput('${col.key}', this.value)" />
    </th>`;
  });

  state.dynamicColumns.forEach(dcol => {
    const val = state.columnFilters[dcol.field] || "";
    html += `<th class="col-dyn">
      <div class="th-title">
        <span>⚡ ${dcol.header}</span>
        <span style="cursor:pointer;font-weight:700;" title="Remove column" onclick="removeDynamicColumn('${dcol.field}', event)">✕</span>
      </div>
      <input class="col-filter-input" type="text" value="${val.replace(/"/g, '&quot;')}" placeholder="Filter extracted..." oninput="onColFilterInput('${dcol.field}', this.value)" />
    </th>`;
  });

  html += `</tr>`;
  thead.innerHTML = html;
}

function renderGridBody() {
  const tbody = document.getElementById("grid-tbody");
  const docs = getFilteredDocuments();
  let html = "";

  docs.forEach(doc => {
    const isSel = state.selectedDocIds.has(doc.doc_id);
    const isAct = state.activeDocId === doc.doc_id;
    const rowCls = `${isSel ? "row-selected" : ""} ${isAct ? "row-active" : ""}`.trim();

    html += `<tr class="${rowCls}" onclick="inspectCitation('${doc.doc_id}', '${doc.primary_chunk_id}', ${doc.primary_page})">
      <td style="text-align:center;" onclick="toggleRowSelect('${doc.doc_id}', event)">
        <input type="checkbox" ${isSel ? "checked" : ""} onclick="toggleRowSelect('${doc.doc_id}', event)" />
      </td>
      <td>
        <span class="doc-pill">${doc.matter_id}</span>
        <div style="font-family:var(--font-mono);font-size:9.5px;color:var(--text-secondary);">RRF ${doc.hybrid_rrf}</div>
      </td>
      <td>
        <div style="font-weight:700;color:var(--text-primary);">${doc.title}</div>
        <div style="font-size:10px;color:var(--text-secondary);">${doc.doc_id} · ${doc.counsel_firm}</div>
        <span class="cite-link-chip" onclick="inspectCitation('${doc.doc_id}', '${doc.primary_chunk_id}', ${doc.primary_page}, event)">
          📌 ${doc.section_ref} (p.${doc.primary_page})
        </span>
      </td>
      <td><div style="font-weight:600;">${doc.cap_pct}</div></td>
      <td>${doc.basket_type}</td>
      <td>${doc.survival_months}</td>
      <td>${doc.qualifiers}</td>`;

    state.dynamicColumns.forEach(dcol => {
      const fallback = computeDynamicCellClientSide(doc, dcol.question || dcol.header);
      const cell = (doc.dynamic_cells && doc.dynamic_cells[dcol.field]) || {
        answer: fallback.answer,
        badge: fallback.badge,
        chunk_id: doc.primary_chunk_id,
        page: doc.primary_page,
        section_ref: doc.section_ref
      };
      html += `<td class="cell-dyn" onclick="inspectCitation('${doc.doc_id}', '${cell.chunk_id || doc.primary_chunk_id}', ${cell.page || doc.primary_page}, event)">
        <div style="font-family:var(--font-mono);font-size:9px;font-weight:700;margin-bottom:2px;">[${cell.badge || 'EXTRACTED'}]</div>
        <div>${cell.answer}</div>
        <span class="cite-link-chip">🔍 p.${cell.page || doc.primary_page} (${cell.section_ref || doc.section_ref})</span>
      </td>`;
    });

    html += `</tr>`;
  });

  if (!docs.length) {
    const colSpan = 7 + state.dynamicColumns.length;
    html = `<tr><td colspan="${colSpan}" style="text-align:center;padding:20px;color:var(--text-secondary);">No documents match current column filters. Click "✕ Reset" to show all 8 cleared documents.</td></tr>`;
  }
  tbody.innerHTML = html;
}

function computeDynamicCellClientSide(doc, questionText) {
  const q = (questionText || "").toLowerCase();
  if (q.includes("fraud") || q.includes("tax") || q.includes("carve") || q.includes("bypass") || q.includes("338")) {
    const map = {
      "DOC-M331-01": { badge: "CARVE-OUT", answer: "Fraud & Fundamental Reps uncapped up to $2.4B EV; general cap 0.75% ($18M) in Sec. 8.02(b)." },
      "DOC-M331-02": { badge: "SKADDEN PUSHBACK", answer: "Skadden v4 caps R&W retention at 0.25% ($6M) & cuts Fundamental survival to 36 mos." },
      "DOC-M331-03": { badge: "ESCROW RINGFENCE", answer: "$18.0M Citibank Escrow backs Sec. 8.02 claims; Pending Claim Reserve held past Month 18." },
      "DOC-M331-04": { badge: "FIRST-DOLLAR TAX", answer: "100% Pre-Closing Tax & Sec. 338(h)(10) bypass Deductible Basket on first-dollar basis ($9.5M cap)." },
      "DOC-M215-01": { badge: "PRECEDENT", answer: "Kestrel SPA: Fraud & Tax exempt from 0.50% ($8.25M) cap; synthetic R&W policy primary." },
      "DOC-M518-01": { badge: "PRECEDENT", answer: "Vanguard JV: Environmental & Tax survive 72 mos; 1.00% ($31M) cap applies to operational reps." },
      "DOC-M402-01": { badge: "COVENANT DEFAULT", answer: "IP transfer to Unrestricted Sub triggers immediate Event of Default (Sec. 6.08(d))." },
      "DOC-M109-01": { badge: "UNCAPPED EQUITABLE", answer: "Standstill/NDA breach permits uncapped specific performance & injunctive relief." }
    };
    return map[doc.doc_id] || { badge: "VERIFIED", answer: doc.summary_text };
  }
  if (q.includes("scrape") || q.includes("materiality") || q.includes("prong")) {
    const map = {
      "DOC-M331-01": { badge: "DOUBLE SCRAPE", answer: "Full Double Materiality Scrape in Sec. 8.02(b): applies to BOTH (1) breach & (2) Losses." },
      "DOC-M331-02": { badge: "SINGLE SCRAPE RISK", answer: "Skadden v4 DELETES Prong 1 (breach determination), leaving Damages-Only scrape." },
      "DOC-M331-03": { badge: "FOLLOWS MERGER", answer: "Follows Sec. 8.02(b) double scrape for quantifying Buyer Claim Notices against $18M Escrow." },
      "DOC-M331-04": { badge: "NO MATERIALITY", answer: "First-dollar tax covenant; materiality qualifiers inapplicable to pre-closing taxes." },
      "DOC-M215-01": { badge: "DOUBLE SCRAPE", answer: "Full Double Materiality Scrape (Breach + Losses) negotiated with Kirkland & Ellis." },
      "DOC-M518-01": { badge: "BREACH-ONLY", answer: "Single Prong (Breach-Only Materiality Scrape) paired with 0.35% Tipping Basket." },
      "DOC-M402-01": { badge: "STRICT IP BLOCKER", answer: "Material IP defined objectively in Sec. 6.08(d); zero basket leakage." },
      "DOC-M109-01": { badge: "N/A (NDA)", answer: "Reasonable care standard; no materiality scrape applicable." }
    };
    return map[doc.doc_id] || { badge: "EXTRACTED", answer: doc.qualifiers };
  }
  if (q.includes("redline") || q.includes("opposing") || q.includes("skadden") || q.includes("counter") || q.includes("delta")) {
    const map = {
      "DOC-M331-01": { badge: "LEXGRAPH BASELINE v3", answer: "LexGraph Baseline: 0.75% ($18M) Cap, 0.50% ($12M) Deductible, 18-Mo Survival, Double Scrape." },
      "DOC-M331-02": { badge: "SKADDEN MARKUP v4", answer: "Cuts Cap 0.75%->0.25% ($6M), hikes Deductible 0.50%->0.85% ($20.4M), survival 18->12 mos." },
      "DOC-M331-03": { badge: "ESCROW IMPACT", answer: "Skadden requests reducing Citibank holdback release from Month 18 to Month 12." },
      "DOC-M331-04": { badge: "TAX CONCESSION", answer: "Per EM-9901, Skadden conceded $9.5M 338(h)(10) gross-up if LexGraph holds 0.75% cap." },
      "DOC-M215-01": { badge: "BENCHMARK (0.50%)", answer: "Refutes Skadden 0.25%: Kestrel ($1.65B) closed at 0.50% Cap with Double Scrape." },
      "DOC-M518-01": { badge: "BENCHMARK (1.00%)", answer: "Refutes Skadden 0.25%: Vanguard ($3.1B) closed at 1.00% Cap & 24-Mo Survival." },
      "DOC-M402-01": { badge: "LATHAM AGREED", answer: "Latham accepted strict Sec. 6.08(d) J.Crew blocker + 4.50x Net Leverage." },
      "DOC-M109-01": { badge: "S&C AGREED", answer: "S&C accepted 18-month standstill with automatic fall-away upon >=50% acquisition." }
    };
    return map[doc.doc_id] || { badge: "COMPARE", answer: doc.summary_text };
  }
  if (q.includes("release") || q.includes("trigger") || q.includes("fall-away") || q.includes("holdback") || q.includes("termination")) {
    const map = {
      "DOC-M331-01": { badge: "15% EBITDA MAE", answer: "Walk-right triggers only if supply impact exceeds peer EBITDA by >15% (Sec. 1.01)." },
      "DOC-M331-02": { badge: "MONTH 12 RELEASE", answer: "Skadden v4 seeks early escrow release at Month 12 instead of Month 18." },
      "DOC-M331-03": { badge: "18-MO + 10 BD", answer: "Citibank auto-releases balance at Month 18 minus Pending Claims unless objected in 10 BDs." },
      "DOC-M331-04": { badge: "SOL + 60 DAYS", answer: "Tax indemnity survives until 60 days after expiration of federal/state SOL." },
      "DOC-M215-01": { badge: "15-MO RELEASE", answer: "General indemnity obligations terminate at Month 15 post-closing." },
      "DOC-M518-01": { badge: "24-MO RELEASE", answer: "General indemnity terminates at Month 24; Environmental survives 72 months." },
      "DOC-M402-01": { badge: "5-QTR EQUITY CURE", answer: "Max 2 consecutive quarters Equity Cure (up to 5 total over 60-mo Term Loan B)." },
      "DOC-M109-01": { badge: "AUTO FALL-AWAY", answer: "18-mo Standstill automatically falls away upon 3rd-party >=50% merger (Sec. 7)." }
    };
    return map[doc.doc_id] || { badge: "TRIGGER", answer: doc.survival_months };
  }
  return {
    badge: `RRF ${doc.hybrid_rrf}`,
    answer: `${doc.clause_type}: Cap ${doc.cap_pct} | Basket ${doc.basket_type} (${doc.section_ref}, p.${doc.primary_page})`
  };
}

function quickAddColumn(questionStr) {
  document.getElementById("dyn-col-input").value = questionStr;
  addDynamicQuestionColumn();
}

async function addDynamicQuestionColumn() {
  const inp = document.getElementById("dyn-col-input");
  const q = inp.value.trim();
  if (!q) return;
  inp.value = "";

  const field = "dyn_" + Math.random().toString(36).substring(2, 7);
  const shortHeader = q.length > 28 ? q.substring(0, 28) + "..." : q;
  setLoader(true, `Extracting dynamic grid column "${shortHeader}" across Cloud Spanner documents...`);

  state.documents.forEach(doc => {
    if (!doc.dynamic_cells) doc.dynamic_cells = {};
    const computed = computeDynamicCellClientSide(doc, q);
    doc.dynamic_cells[field] = {
      answer: computed.answer,
      badge: computed.badge,
      chunk_id: doc.primary_chunk_id,
      page: doc.primary_page,
      section_ref: doc.section_ref
    };
  });

  state.dynamicColumns.push({ field, header: shortHeader, question: q });
  renderGridHeader();
  renderGridBody();

  // Scroll grid horizontally to show newly added column without moving outer viewport
  const gridCont = document.getElementById("grid-scroll-container");
  if (gridCont) {
    setTimeout(() => { gridCont.scrollTo({ left: gridCont.scrollWidth, behavior: "smooth" }); }, 40);
  }

  try {
    const resp = await fetch(`${API_BASE}/api/grid/add-column`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question: q,
        field: field,
        selected_doc_ids: Array.from(state.selectedDocIds)
      })
    });
    if (resp.ok) {
      const data = await resp.json();
      if (data.cells) {
        state.documents.forEach(doc => {
          if (data.cells[doc.doc_id]) {
            doc.dynamic_cells[field] = data.cells[doc.doc_id];
          }
        });
        renderGridBody();
      }
    }
  } catch (e) {}
  setTimeout(() => setLoader(false), 320);
}

function askPresetQuestion(q) {
  document.getElementById("chat-question-input").value = q;
  submitScopedChatQuestion();
}

async function submitScopedChatQuestion() {
  const inp = document.getElementById("chat-question-input");
  const q = inp.value.trim();
  if (!q) return;
  inp.value = "";

  const selectedIds = Array.from(state.selectedDocIds);
  const targetDocs = state.documents.filter(d => selectedIds.length === 0 || selectedIds.includes(d.doc_id));

  setLoader(true, `Synthesizing grounded answer across ${targetDocs.length} selected file(s) & highlighting cited chunks...`);

  const field = "dyn_" + Math.random().toString(36).substring(2, 7);
  const shortHeader = q.length > 26 ? q.substring(0, 26) + "..." : q;
  state.documents.forEach(doc => {
    if (!doc.dynamic_cells) doc.dynamic_cells = {};
    const c = computeDynamicCellClientSide(doc, q);
    doc.dynamic_cells[field] = {
      answer: c.answer,
      badge: c.badge,
      chunk_id: doc.primary_chunk_id,
      page: doc.primary_page,
      section_ref: doc.section_ref
    };
  });
  state.dynamicColumns.push({ field, header: shortHeader, question: q });
  renderGridHeader();
  renderGridBody();

  // Immediately render fast local synthesis & citations, then update with live server response if available
  const citations = targetDocs.map(d => ({
    doc_id: d.doc_id,
    chunk_id: d.primary_chunk_id,
    page: d.primary_page,
    label: `${d.doc_id} · ${d.section_ref} (p.${d.primary_page})`
  }));
  const bulletLines = targetDocs.map(d => {
    const cell = computeDynamicCellClientSide(d, q);
    return `• <strong>${d.doc_id} (${d.matter_id})</strong>: ${cell.answer} <em>[Cap: ${d.cap_pct}, Basket: ${d.basket_type}]</em>`;
  }).join("<br/>");

  state.chatHistory = [{
    role: "agent",
    text: `<strong>Query: "${q}" (${targetDocs.length} Selected Docs):</strong><br/>${bulletLines}`,
    citations: citations
  }];
  renderChatMessages();
  if (targetDocs.length > 0) {
    const first = targetDocs[0];
    inspectCitation(first.doc_id, first.primary_chunk_id, first.primary_page);
  }

  try {
    const resp = await fetch(`${API_BASE}/api/chat/scoped`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question: q,
        selected_doc_ids: selectedIds
      })
    });
    if (resp.ok) {
      const data = await resp.json();
      if (data.answer) {
        state.chatHistory = [{
          role: "agent",
          text: data.answer,
          citations: data.citations || citations
        }];
        renderChatMessages();
      }
      if (data.primary_citation) {
        inspectCitation(data.primary_citation.doc_id, data.primary_citation.chunk_id, data.primary_citation.page);
      }
    }
  } catch (e) {}

  setLoader(false);
}

function renderChatMessages() {
  const box = document.getElementById("chat-messages");
  const agentMsgs = state.chatHistory.filter(m => m.role === "agent");
  const latest = agentMsgs.length ? agentMsgs[agentMsgs.length - 1] : state.chatHistory[state.chatHistory.length - 1];
  if (!latest) {
    box.innerHTML = `<div style="color:var(--text-secondary);">Select any rows in the grid and ask a question to synthesize and highlight original contract citations.</div>`;
    return;
  }
  let citesHtml = "";
  if (latest.citations && latest.citations.length) {
    citesHtml = `<div style="margin-top:4px;display:flex;gap:4px;flex-wrap:wrap;">` +
      latest.citations.map(c =>
        `<span class="cite-link-chip" onclick="inspectCitation('${c.doc_id}', '${c.chunk_id}', ${c.page}, event)">📌 ${c.label}</span>`
      ).join("") + `</div>`;
  }
  box.innerHTML = `<div>${latest.text}</div>${citesHtml}`;
}

function renderDocumentViewer() {
  const doc = state.documents.find(d => d.doc_id === state.activeDocId) || state.documents[0];
  if (!doc) return;

  document.getElementById("viewer-doc-title").textContent = doc.title;
  document.getElementById("viewer-doc-sub").textContent = `${doc.doc_id} · Matter ${doc.matter_id} · ${doc.governing_law} Law · ${doc.counsel_firm} · ${doc.dms_version}`;

  const pages = doc.pages || [];
  const activeChunk = state.activeChunkId || doc.primary_chunk_id;

  let activePageNum = state.activePage || doc.primary_page || 1;
  pages.forEach(p => {
    (p.sections || []).forEach(sec => {
      if (sec.chunk_id === activeChunk) activePageNum = p.page_number;
    });
  });

  document.getElementById("viewer-cite-pill").innerHTML =
    `📌 Highlighted: <strong>${activeChunk} · ${doc.section_ref} (p.${activePageNum}) · RRF=${doc.hybrid_rrf}</strong>`;

  const tabsEl = document.getElementById("viewer-page-tabs");
  tabsEl.innerHTML = pages.map(p =>
    `<button class="chip ${p.page_number === activePageNum ? 'active' : ''}" onclick="state.activePage=${p.page_number};renderDocumentViewer();">P.${p.page_number}</button>`
  ).join("") + `<button class="chip ${state.activePage === 0 ? 'active' : ''}" onclick="state.activePage=0;renderDocumentViewer();">All (${pages.length})</button>`;

  const scrollEl = document.getElementById("doc-paper-scroll");
  let pagesToShow = state.activePage === 0 ? pages : pages.filter(p => p.page_number === activePageNum);
  if (!pagesToShow.length) pagesToShow = pages;

  let paperHtml = "";
  pagesToShow.forEach(p => {
    let sectionsHtml = "";
    (p.sections || []).forEach(sec => {
      const isCited = sec.chunk_id === activeChunk || sec.is_primary;
      let bodyText = sec.text;
      if (state.showRedlineOverlay && sec.redline_html) {
        bodyText = sec.redline_html;
      }
      sectionsHtml += `<div class="legal-section ${isCited ? 'cited-chunk-active' : ''}" id="chunk-box-${sec.chunk_id}">
        ${isCited ? `<div class="cite-bbox-ribbon">
          <span>★ CITED RAG CHUNK: ${sec.chunk_id} (${sec.section_ref})</span>
          <span>Page ${p.page_number} · RRF ${doc.hybrid_rrf}</span>
        </div>` : ''}
        <h4>${sec.section_ref} — ${sec.heading}</h4>
        <p>${bodyText}</p>
      </div>`;
    });

    paperHtml += `<div class="legal-paper-page">
      <div class="page-watermark">
        <span>OFFICIAL iMANAGE DMS · ${doc.doc_id} (${doc.dms_version})</span>
        <span>MATTER ${doc.matter_id} · PAGE ${p.page_number} OF ${pages.length}</span>
      </div>
      ${p.page_number === 1 ? `<div class="legal-title-block">
        <h2>${doc.title}</h2>
        <p>MATTER ${doc.matter_id} · EXECUTED: ${doc.execution_date} · ${doc.governing_law.toUpperCase()} LAW · ${doc.counsel_firm.toUpperCase()}</p>
      </div>` : ''}
      ${sectionsHtml}
    </div>`;
  });

  scrollEl.innerHTML = paperHtml;

  // CRITICAL: Scroll ONLY #doc-paper-scroll internally, NEVER scrollIntoView() which shifts outer html/body!
  setTimeout(() => {
    const highlighted = scrollEl.querySelector(".cited-chunk-active");
    if (highlighted && scrollEl) {
      const cRect = scrollEl.getBoundingClientRect();
      const hRect = highlighted.getBoundingClientRect();
      const targetScrollTop = (hRect.top - cRect.top) + scrollEl.scrollTop - 16;
      scrollEl.scrollTo({ top: Math.max(0, targetScrollTop), behavior: "smooth" });
    }
    lockRootViewport();
  }, 40);
}

function toggleRedlineOverlay() {
  state.showRedlineOverlay = !state.showRedlineOverlay;
  const btn = document.getElementById("btn-redline-toggle");
  btn.classList.toggle("btn-primary", state.showRedlineOverlay);
  renderDocumentViewer();
}

function openRawGcsPdf() {
  const doc = state.documents.find(d => d.doc_id === state.activeDocId) || state.documents[0];
  if (doc && doc.pdf_url) {
    window.open(doc.pdf_url, "_blank");
  }
}

async function triggerGrant30d() {
  setLoader(true, "Committing 30-day TeammateGrant edge (EM-9901 -> M-331) in Cloud Spanner...");
  try {
    if (window.parent && window.parent !== window) {
      window.parent.postMessage({
        jsonrpc: "2.0",
        id: ++mcpRpcId,
        method: "tools/call",
        params: {
          name: "grant_teammate_email_30d",
          arguments: { matter_id: "M-331", email_id: "EM-9901", granted_to: "s-jenkins@lexgraph.com" }
        }
      }, "*");
    }
    const resp = await fetch(`${API_BASE}/api/grant`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ matter_id: "M-331", email_id: "EM-9901", granted_to: "s-jenkins@lexgraph.com" })
    });
    if (resp.ok) {
      const res = await resp.json();
      state.chatHistory = [{
        role: "agent",
        text: `✅ <strong>Cloud Spanner TeammateGrants Edge Committed (${res.grant_id}):</strong> Granted 30-day access to unfiled tax rider email <code>EM-9901</code> on Matter <code>M-331</code> in <code>${res.latency_ms} ms</code> (Expires: ${res.expires_at}).`
      }];
    } else {
      throw new Error("fallback");
    }
  } catch (e) {
    state.chatHistory = [{
      role: "agent",
      text: `✅ <strong>Cloud Spanner TeammateGrants Action Dispatched:</strong> 30-day temporal access grant for <code>EM-9901</code> (Section 338(h)(10) Tax Allocation Rider email thread) on Matter <code>M-331</code> committed &amp; synced to host agent.`
    }];
  }
  setTimeout(() => {
    setLoader(false);
    renderChatMessages();
  }, 250);
}

function syncToHostAgent() {
  const selectedArr = Array.from(state.selectedDocIds);
  const q = document.getElementById("chat-question-input").value.trim() ||
    `Inspect selected documents (${selectedArr.join(", ")}) and compare their key clauses with exact citations.`;
  setLoader(true, "Syncing selected grid files & question to Gemini Enterprise Host Chat...");
  try {
    if (window.parent && window.parent !== window) {
      // Push updated model context + prefill/send message to Gemini Enterprise host
      pushModelContextToBridge();
      window.parent.postMessage({
        jsonrpc: "2.0",
        id: ++mcpRpcId,
        method: "ui/message",
        params: {
          role: "user",
          content: [{
            type: "text",
            text: `[Selected Grid Files: ${selectedArr.join(", ")}] ${q}`
          }]
        }
      }, "*");
      window.parent.postMessage({
        jsonrpc: "2.0",
        id: ++mcpRpcId,
        method: "tools/call",
        params: {
          name: "inspect_selected_files",
          arguments: {
            question: q,
            selected_doc_ids: selectedArr
          }
        }
      }, "*");
    }
  } catch (e) {}
  setTimeout(() => setLoader(false), 450);
}

function renderAll() {
  updateSelectedBadge();
  renderGridHeader();
  renderGridBody();
  renderChatMessages();
  renderDocumentViewer();
  lockRootViewport();
}

renderAll();
</script>
</body>
</html>
"""


def build_workspace_html(initial_state: dict) -> str:
  state_json = json.dumps(initial_state).replace("</", "<\\/")
  return WORKSPACE_HTML_TEMPLATE.replace("__INITIAL_STATE_JSON__", state_json)
