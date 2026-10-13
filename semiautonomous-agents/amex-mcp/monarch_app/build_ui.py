"""Build Monark™ (Moth-Ark Bootleg Finance OS — $0/yr Parody Edition) Web + iOS/Android/Pixel 11 Pro App."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

DATASET_PATH = Path(__file__).parent / "monarch_dataset.json"
INDEX_OUT = Path(__file__).parent / "index.html"
MOBILE_BRIDGE_OUT = Path("/usr/local/google/home/jesusarguelles/companion-grounding-mcp/mobile_bridge/monark_mobile.html")
MOBILE_BRIDGE_LEGACY_OUT = Path("/usr/local/google/home/jesusarguelles/companion-grounding-mcp/mobile_bridge/monarch_mobile.html")
CURRENT_ARTIFACT_OUT = Path("/usr/local/google/home/jesusarguelles/.gemini/jetski/brain/498db343-48bb-4122-9b75-49966ba1de9c/monark_finance_app.html")
CURRENT_ARTIFACT_META_OUT = Path("/usr/local/google/home/jesusarguelles/.gemini/jetski/brain/498db343-48bb-4122-9b75-49966ba1de9c/monark_finance_app.html.metadata.json")
ARTIFACT_OUT = Path("/usr/local/google/home/jesusarguelles/.gemini/jetski/brain/e16782b8-3b7e-4494-9cdf-d8aad8636e0f/monarch_finance_app.html")
ARTIFACT_META_OUT = Path("/usr/local/google/home/jesusarguelles/.gemini/jetski/brain/e16782b8-3b7e-4494-9cdf-d8aad8636e0f/monarch_finance_app.html.metadata.json")

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover" />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
  <meta name="apple-mobile-web-app-title" content="Monark" />
  <meta name="mobile-web-app-capable" content="yes" />
  <meta name="theme-color" content="#7C3AED" />
  <link rel="manifest" href="/manifest.webmanifest" />
  <link rel="apple-touch-icon" href="/icon.svg" />
  <title>Monark™ — Moth-Ark Bootleg Finance OS ($0/yr Edition)</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    :root {
      /* Monarch Money Light Mode — Royal Amethyst Purple Edition */
      --bg-canvas: #f6f6f9;
      --bg-sidebar: #fbfbfc;
      --bg-surface: #ffffff;
      --bg-elevated: #f1f0f5;
      --bg-header: rgba(255, 255, 255, 0.95);
      --border-subtle: #e7e6ef;
      --border-hover: #c4b5fd;
      --text-primary: #14121f;
      --text-secondary: #686478;
      --text-muted: #9ca3af;
      --amethyst: #7c3aed;
      --amethyst-bright: #8b5cf6;
      --amethyst-deep: #4c1d95;
      --amethyst-soft: rgba(124, 58, 237, 0.10);
      --amethyst-fill: rgba(124, 58, 237, 0.24);
      --monarch-green: #16a34a;
      --monarch-green-soft: rgba(22, 163, 74, 0.11);
      --monarch-blue: #0284c7;
      --monarch-blue-soft: rgba(2, 132, 199, 0.11);
      --monarch-rose: #e11d48;
      --monarch-rose-soft: rgba(225, 29, 72, 0.11);
      --monarch-amber: #f59e0b;
      --shadow-card: 0 1px 2px rgba(20, 18, 31, 0.04), 0 4px 14px rgba(124, 58, 237, 0.03);
      --p-badge-bg: #f3f2f6;
      --p-badge-text: #6b7280;
      --ink-grad-1: radial-gradient(circle at 20% 20%, #a78bfa, #7c3aed, #2e1065);
      --ink-grad-2: radial-gradient(circle at 80% 20%, #10b981, #6d28d9, #1e1b4b);
      --ink-grad-3: radial-gradient(circle at 40% 80%, #38bdf8, #7c3aed, #09090b);
      --ink-shadow: rgba(124, 58, 237, 0.42);
      --sweep-grad: linear-gradient(90deg, #686478 0%, #7c3aed 50%, #686478 100%);
      --font-sans: -apple-system, BlinkMacSystemFont, "Inter", "SF Pro Display", "Segoe UI", Roboto, sans-serif;
      --font-serif: "Georgia", "Times New Roman", serif;
      --font-mono: "JetBrains Mono", "SF Mono", ui-monospace, Menlo, monospace;
    }

    [data-theme="dark"] {
      /* Monarch Money OLED Dark Mode — Royal Amethyst Purple Edition */
      --bg-canvas: #0b0914;
      --bg-sidebar: #120f1d;
      --bg-surface: #171326;
      --bg-elevated: #211c35;
      --bg-header: rgba(18, 15, 29, 0.95);
      --border-subtle: #2a2442;
      --border-hover: #7c3aed;
      --text-primary: #f8f7fc;
      --text-secondary: #a39eb8;
      --text-muted: #6e6887;
      --amethyst: #8b5cf6;
      --amethyst-bright: #a78bfa;
      --amethyst-deep: #5b21b6;
      --amethyst-soft: rgba(139, 92, 246, 0.18);
      --amethyst-fill: rgba(139, 92, 246, 0.30);
      --monarch-green: #22c55e;
      --monarch-green-soft: rgba(34, 197, 94, 0.15);
      --monarch-blue: #38bdf8;
      --monarch-blue-soft: rgba(56, 189, 248, 0.15);
      --monarch-rose: #fb7185;
      --monarch-rose-soft: rgba(251, 113, 133, 0.15);
      --shadow-card: 0 8px 28px rgba(0, 0, 0, 0.55);
      --p-badge-bg: #2a2442;
      --p-badge-text: #a39eb8;
      --ink-grad-1: radial-gradient(circle at 20% 20%, #ddd6fe, #8b5cf6, #2e1065);
      --ink-grad-2: radial-gradient(circle at 80% 20%, #34d399, #a78bfa, #1e1b4b);
      --ink-grad-3: radial-gradient(circle at 40% 80%, #38bdf8, #8b5cf6, #09090b);
      --ink-shadow: rgba(167, 139, 250, 0.55);
      --sweep-grad: linear-gradient(90deg, #a39eb8 0%, #ddd6fe 50%, #a39eb8 100%);
    }

    * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }

    body {
      background-color: var(--bg-canvas);
      color: var(--text-primary);
      font-family: var(--font-sans);
      margin: 0;
      transition: background-color 0.2s ease, color 0.2s ease;
    }

    .m-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: 12px;
      box-shadow: var(--shadow-card);
      transition: border-color 0.15s ease;
    }

    .m-card:hover {
      border-color: var(--border-hover);
    }

    .sidebar-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 8px 11px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 500;
      color: var(--text-secondary);
      cursor: pointer;
      transition: all 0.14s ease;
      user-select: none;
    }

    .sidebar-item:hover {
      background: var(--bg-elevated);
      color: var(--text-primary);
    }

    .sidebar-item.active {
      background: var(--bg-elevated);
      color: var(--text-primary);
      font-weight: 600;
    }

    .sidebar-item.active svg {
      color: var(--amethyst);
    }

    .pill-btn {
      padding: 5px 11px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 500;
      border: 1px solid var(--border-subtle);
      background: var(--bg-surface);
      color: var(--text-secondary);
      cursor: pointer;
      transition: all 0.15s ease;
      white-space: nowrap;
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }

    .pill-btn:hover {
      border-color: var(--border-hover);
      color: var(--text-primary);
    }

    .pill-btn.active {
      background: var(--amethyst);
      color: #ffffff;
      border-color: var(--amethyst);
      font-weight: 600;
    }

    .pill-amethyst {
      background: linear-gradient(135deg, var(--amethyst-bright) 0%, var(--amethyst) 100%);
      color: #ffffff;
      border: none;
      padding: 6px 13px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      box-shadow: 0 2px 8px rgba(124, 58, 237, 0.25);
      transition: opacity 0.15s ease;
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }

    .pill-amethyst:hover { opacity: 0.92; }

    .mono-num {
      font-family: var(--font-mono);
      font-variant-numeric: tabular-nums;
    }

    /* Monarch Circular Gray "P" Badge on Transaction Rows (Exact Match to Screenshot 2) */
    .monarch-p-badge {
      width: 21px;
      height: 21px;
      border-radius: 9999px;
      background: var(--p-badge-bg);
      color: var(--p-badge-text);
      font-size: 10.5px;
      font-weight: 600;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }

    /* Company Logo Circular Wrapper */
    .company-logo-circle {
      width: 28px;
      height: 28px;
      border-radius: 9999px;
      overflow: hidden;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      position: relative;
      box-shadow: inset 0 0 0 1px rgba(0,0,0,0.06);
    }

    /* Claude-Code Shrinking & Shining Ink Animation */
    .shrinking-shining-ink {
      width: 11px;
      height: 11px;
      display: inline-block;
      flex-shrink: 0;
      background: var(--ink-grad-1);
      border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%;
      animation:
        ink-morph 5s ease-in-out infinite alternate,
        ink-pulse 1.8s ease-in-out infinite,
        ink-shine 3.5s linear infinite;
      filter: drop-shadow(0 0 5px var(--ink-shadow));
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
      font-size: 10.5px;
      font-weight: 600;
    }
    @keyframes sweep-shimmer {
      to { background-position: 200% center; }
    }

    /* Mobile Simulator Frame when toggled on Desktop */
    .mobile-frame-active {
      max-width: 412px !important;
      margin: 12px auto !important;
      height: calc(100vh - 24px) !important;
      border-radius: 46px !important;
      border: 11px solid #181622 !important;
      box-shadow: 0 25px 70px rgba(0, 0, 0, 0.48) !important;
      overflow: hidden !important;
      position: relative !important;
    }

    input, select {
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      color: var(--text-primary);
      border-radius: 8px;
      font-size: 12px;
    }
    input:focus, select:focus {
      outline: none;
      border-color: var(--amethyst);
    }

    .subtab-link {
      padding: 10px 6px;
      margin-right: 14px;
      font-size: 13px;
      font-weight: 500;
      color: var(--text-secondary);
      border-bottom: 2px solid transparent;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .subtab-link:hover {
      color: var(--text-primary);
    }
    .subtab-link.active {
      color: var(--text-primary);
      font-weight: 600;
      border-bottom-color: var(--amethyst);
    }

    .icon-util-btn {
      width: 26px;
      height: 26px;
      border-radius: 6px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      color: var(--text-secondary);
      cursor: pointer;
      transition: background 0.14s ease, color 0.14s ease;
    }
    .icon-util-btn:hover {
      background: var(--bg-elevated);
      color: var(--text-primary);
    }
  </style>
</head>
<body class="antialiased h-screen overflow-hidden flex flex-col">

  <!-- APP SHELL WRAPPER -->
  <div id="appShell" class="flex-1 flex h-full overflow-hidden relative">

    <!-- Mobile Sidebar Drawer Backdrop (Pixel 11 Pro) -->
    <div id="mobileMenuBackdrop" onclick="closeMobileSidebar()" class="fixed inset-0 z-40 hidden md:hidden" style="background: rgba(11, 9, 20, 0.62); backdrop-filter: blur(4px);"></div>

    <!-- ================================================================== -->
    <!-- MONARCH LEFT SIDEBAR (Desktop Fixed + Pixel 11 Pro Slide Drawer)   -->
    <!-- ================================================================== -->
    <aside id="leftSidebar" style="background: var(--bg-sidebar); border-right: 1px solid var(--border-subtle); width: 232px;" class="hidden md:flex flex-shrink-0 flex-col justify-between h-full select-none z-50 fixed md:static top-0 bottom-0 left-0 shadow-2xl md:shadow-none">
      <div class="p-3.5 space-y-3 overflow-y-auto">
        <!-- Monark Top Sidebar Header: Moth-Ark Logo + Search / Bell / Gear / Collapse Panel Icons -->
        <div class="flex items-center justify-between px-1 pb-1">
          <div onclick="switchTab('dashboard')" class="flex items-center gap-2 cursor-pointer" title="Monark™ — Definitely Not That $99.99/yr Butterfly App">
            <svg class="w-6 h-6 flex-shrink-0" viewBox="0 0 512 512" fill="none">
              <path d="M256 226C212 140 105 112 86 178C71 232 115 292 172 315C156 344 168 388 206 388C234 388 248 360 256 332C264 360 278 388 306 388C344 388 356 344 340 315C397 292 441 232 426 178C407 112 300 140 256 226Z" stroke="#7C3AED" stroke-width="40" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <div class="leading-tight">
              <div class="font-extrabold text-xs tracking-wider uppercase flex items-center gap-1" style="color: var(--amethyst);">
                <span>MONARK™</span>
                <span class="text-[8.5px] px-1 py-0.2 rounded font-mono" style="background: var(--amethyst-soft); color: var(--amethyst);">$0/YR</span>
              </div>
              <div class="text-[9px] font-medium" style="color: var(--text-secondary);">Moth-Ark Bootleg OS</div>
            </div>
          </div>
          <div class="flex items-center gap-0.5">
            <!-- Search Icon -->
            <button onclick="switchTab('transactions'); setTimeout(()=>document.getElementById('txnSearch')?.focus(), 50);" class="icon-util-btn" title="Search transactions">
              <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
            </button>
            <!-- Bell Notification Icon -->
            <button onclick="switchTab('recurring')" class="icon-util-btn" title="Notifications &amp; Upcoming Bills">
              <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>
            </button>
            <!-- Gear Settings Icon -->
            <button onclick="openMobileInstallModal()" class="icon-util-btn" title="Settings &amp; Install Mobile App">
              <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
            </button>
            <!-- Close Mobile Drawer Button on Pixel 11 Pro -->
            <button onclick="closeMobileSidebar()" class="icon-util-btn md:hidden" title="Close Menu">✕</button>
            <!-- Collapse Panel Icon (Desktop Only) -->
            <button onclick="toggleMobileFrame()" class="icon-util-btn hidden md:inline-flex" title="Toggle Mobile / Desktop Frame">
              <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M9 3v18"/></svg>
            </button>
          </div>
        </div>

        <!-- Back to Pixel 11 Pro CFO Chat Button -->
        <a href="/" class="w-full py-2 px-2.5 rounded-lg flex items-center justify-between text-xs font-semibold" style="background: var(--amethyst-soft); color: var(--amethyst); text-decoration: none;">
          <span class="flex items-center gap-2">
            <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
            <span>PX11 CFO Chat</span>
          </span>
          <span class="mono-num text-[10px]">~/expenses</span>
        </a>

        <!-- Monarch Primary Navigation (Exact 10 Items & Exact Icons from Screenshot 3) -->
        <nav class="space-y-0.5">
          <!-- 1. Dashboard (House with arched door) -->
          <div onclick="switchTab('dashboard')" id="tab-dashboard" class="sidebar-item active">
            <div class="flex items-center gap-2.5">
              <svg class="w-4 h-4 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V14a3 3 0 0 1 6 0v8"/></svg>
              <span>Dashboard</span>
            </div>
          </div>

          <!-- 2. Accounts (3 stacked coin/layer discs — exact match to Screenshot 3) -->
          <div onclick="switchTab('accounts')" id="tab-accounts" class="sidebar-item">
            <div class="flex items-center gap-2.5">
              <svg class="w-4 h-4 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 11c0 1.66 3.58 3 8 3s8-1.34 8-3"/><path d="M4 16c0 1.66 3.58 3 8 3s8-1.34 8-3"/></svg>
              <span>Accounts</span>
            </div>
          </div>

          <!-- 3. Transactions (Credit card with stripe) -->
          <div onclick="switchTab('transactions')" id="tab-transactions" class="sidebar-item">
            <div class="flex items-center gap-2.5">
              <svg class="w-4 h-4 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="14" x="2" y="5" rx="2"/><line x1="2" x2="22" y1="10" y2="10"/></svg>
              <span>Transactions</span>
            </div>
          </div>

          <!-- 4. Cash Flow (3 vertical rounded bar columns — exact match to Screenshot 3) -->
          <div onclick="switchTab('cashflow')" id="tab-cashflow" class="sidebar-item">
            <div class="flex items-center gap-2.5">
              <svg class="w-4 h-4 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="13" width="3.5" height="7" rx="1"/><rect x="10.25" y="5" width="3.5" height="15" rx="1"/><rect x="16.5" y="9" width="3.5" height="11" rx="1"/></svg>
              <span>Cash Flow</span>
            </div>
          </div>

          <!-- 5. Reports (Pie chart with quarter slice) -->
          <div onclick="switchTab('reports')" id="tab-reports" class="sidebar-item">
            <div class="flex items-center gap-2.5">
              <svg class="w-4 h-4 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/></svg>
              <span>Reports</span>
            </div>
          </div>

          <!-- 6. Budget (Trifold map) -->
          <div onclick="switchTab('budget')" id="tab-budget" class="sidebar-item">
            <div class="flex items-center gap-2.5">
              <svg class="w-4 h-4 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/><line x1="9" x2="9" y1="3" y2="18"/><line x1="15" x2="15" y1="6" y2="21"/></svg>
              <span>Budget</span>
            </div>
          </div>

          <!-- 7. Recurring (Calendar with header bar) -->
          <div onclick="switchTab('recurring')" id="tab-recurring" class="sidebar-item">
            <div class="flex items-center gap-2.5">
              <svg class="w-4 h-4 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/></svg>
              <span>Recurring</span>
            </div>
          </div>

          <!-- 8. Goals (Concentric bullseye target) -->
          <div onclick="switchTab('goals')" id="tab-goals" class="sidebar-item">
            <div class="flex items-center gap-2.5">
              <svg class="w-4 h-4 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>
              <span>Goals</span>
            </div>
          </div>

          <!-- 9. Investments (Upward zig-zag trend arrow) -->
          <div onclick="switchTab('investments')" id="tab-investments" class="sidebar-item">
            <div class="flex items-center gap-2.5">
              <svg class="w-4 h-4 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>
              <span>Investments</span>
            </div>
          </div>

          <!-- 10. Advice (Thumbs-up outline icon — exact match to Screenshot 3) -->
          <div onclick="switchTab('advisor')" id="tab-advisor" class="sidebar-item">
            <div class="flex items-center gap-2.5">
              <svg class="w-4 h-4 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M7 10v12"/><path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2h0a3.13 3.13 0 0 1 3 3.88Z"/></svg>
              <span>Advice</span>
            </div>
          </div>
        </nav>
      </div>

      <!-- Bottom Help & Support + User Profile Footer (Exact Match to Screenshot 3) -->
      <div class="p-3 space-y-1.5" style="border-top: 1px solid var(--border-subtle);">
        <!-- Live SimpleFIN Status Pill -->
        <div class="px-2.5 py-1.5 rounded-lg flex items-center justify-between" style="background: var(--bg-elevated);">
          <div class="flex items-center gap-1.5 min-w-0">
            <span class="shrinking-shining-ink"></span>
            <span id="liveStatusText" class="sweep-text truncate">SimpleFIN Live</span>
          </div>
          <button onclick="triggerLiveSync()" class="text-[10px] font-semibold hover:underline cursor-pointer" style="color: var(--amethyst);">↻ Sync</button>
        </div>

        <!-- Help & Support Row -->
        <div onclick="openMobileInstallModal()" class="sidebar-item py-1.5 px-2 text-xs">
          <div class="flex items-center gap-2">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><path d="M12 17h.01"/></svg>
            <span>Help &amp; Mobile App</span>
          </div>
        </div>

        <!-- User Profile Row (1-Tap Switcher: TK ⇄ JC) -->
        <div onclick="toggleProfile()" class="sidebar-item py-1.5 px-2 text-xs" title="1-Tap Switch between TK (Thomas Kurian Demo) and JC (Jesus Chavez Real)">
          <div class="flex items-center gap-2 min-w-0">
            <span id="sidebarProfileAvatar" class="w-6 h-6 rounded-full flex items-center justify-center text-white text-[10px] font-bold flex-shrink-0" style="background: linear-gradient(135deg, #2563EB, #4C1D95);">TK</span>
            <div class="min-w-0">
              <div id="sidebarProfileName" class="font-semibold truncate" style="color: var(--text-primary);">Thomas Kurian (TK)</div>
              <div id="sidebarProfileSub" class="text-[9.5px] truncate" style="color: var(--amethyst);">Friends Demo · Tap for JC</div>
            </div>
          </div>
          <span class="text-[10px] font-mono px-1.5 py-0.5 rounded" style="background: var(--amethyst-soft); color: var(--amethyst);">⇄</span>
        </div>
      </div>
    </aside>

    <!-- ================================================================== -->
    <!-- MAIN VIEWPORT COLUMN                                               -->
    <!-- ================================================================== -->
    <div class="flex-1 flex flex-col h-full overflow-hidden relative">

      <!-- iOS Dynamic Island Header (Shown when Mobile Frame Preview is Active) -->
      <div id="iosDynamicIslandBar" class="hidden pt-2 pb-1 px-6 flex items-center justify-between text-[11px] font-semibold select-none" style="background: var(--bg-header);">
        <span>12:51 ◄</span>
        <div class="w-24 h-5 rounded-full bg-black flex items-center justify-end pr-2">
          <span class="w-2 h-2 rounded-full bg-purple-500"></span>
        </div>
        <span>5G+ 98%</span>
      </div>

      <!-- Top Contextual Bar (Pixel 11 Pro Optimized) -->
      <header style="background: var(--bg-header); border-bottom: 1px solid var(--border-subtle); backdrop-filter: blur(12px);" class="px-3 sm:px-6 py-1.5 flex flex-wrap items-center justify-between gap-2 z-20 min-h-[52px]">
        <div class="flex items-center gap-2">
          <!-- Moth-Ark Menu Drawer Trigger on Pixel 11 Pro -->
          <button onclick="openMobileSidebar()" class="w-8 h-8 rounded-lg flex md:hidden items-center justify-center cursor-pointer" style="background: var(--amethyst-soft); border: 1px solid rgba(124, 58, 237, 0.28);" title="Open All 10 Monark™ Modules">
            <svg class="w-4 h-4" viewBox="0 0 512 512" fill="none">
              <path d="M256 226C212 140 105 112 86 178C71 232 115 292 172 315C156 344 168 388 206 388C234 388 248 360 256 332C264 360 278 388 306 388C344 388 356 344 340 315C397 292 441 232 426 178C407 112 300 140 256 226Z" stroke="#7C3AED" stroke-width="44" stroke-linecap="round"/>
            </svg>
          </button>
          <div class="flex items-center gap-1.5 flex-wrap">
            <h1 id="pageHeaderTitle" class="text-[15px] font-bold tracking-tight">Dashboard</h1>
            <span class="text-[9.5px] font-mono font-bold px-1.5 py-0.5 rounded uppercase" style="background: var(--amethyst-soft); color: var(--amethyst);" title="Definitely Not Monarch™ — Saved $99.99/yr">MONARK™</span>
            <!-- 1-Tap Profile Switcher Pill: TK (Thomas Kurian Demo) ⇄ JC (Jesus Real) -->
            <div class="flex items-center rounded-lg p-0.5 text-[11px] font-bold" style="background: var(--bg-elevated); border: 1px solid var(--border-subtle);" title="1-Tap Switch: TK (Thomas Kurian Friends Demo) vs JC (Jesus Chavez Real)">
              <button onclick="setProfile('TK')" id="profBtn-TK" class="px-2 py-0.5 rounded-md cursor-pointer transition-all">
                ◈ TK<span class="hidden sm:inline"> (CEO Demo)</span>
              </button>
              <button onclick="setProfile('JC')" id="profBtn-JC" class="px-2 py-0.5 rounded-md cursor-pointer transition-all">
                JC<span class="hidden sm:inline"> (My Profile)</span>
              </button>
            </div>
            <!-- Back to PX11 CFO Chat Pill -->
            <a href="/" class="pill-btn py-1 px-2 text-[11px] font-semibold" style="text-decoration:none; color: var(--amethyst); border-color: rgba(124,58,237,0.32);" title="Return to Pixel 11 Pro CFO Chat">
              <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="m15 18-6-6 6-6"/></svg>
              <span>PX11</span>
            </a>
            <!-- Contextual Sub-Tabs -->
            <div id="headerSubTabs" class="hidden sm:flex items-center">
              <span onclick="switchTab('cashflow')" id="subtab-cashflow" class="subtab-link active">Cash Flow</span>
              <span onclick="switchTab('reports')" id="subtab-spending" class="subtab-link">Spending</span>
              <span onclick="jumpToTxnType('INCOME')" id="subtab-income" class="subtab-link">Income</span>
            </div>
          </div>
        </div>

        <!-- Global Controls (Pixel 11 Pro Single-Row Compact Wrap) -->
        <div class="flex flex-wrap items-center gap-1.5">
          <!-- Sync Button -->
          <button onclick="triggerLiveSync()" class="pill-btn py-1 px-2 text-xs" title="Refresh all SimpleFIN bank connections">
            <span>↻</span><span class="hidden sm:inline">Refresh all</span>
          </button>

          <!-- Institution Scope Selector -->
          <select id="globalBankScope" onchange="setBankScope(this.value)" class="px-2 py-1 font-medium cursor-pointer text-xs">
            <option value="ALL">▽ All 7 Accts</option>
            <option value="amex">▽ Amex (4002)</option>
            <option value="bofa">▽ BofA</option>
            <option value="sofi">▽ SoFi</option>
          </select>

          <!-- Period Pills -->
          <div class="flex items-center gap-0.5 p-0.5 rounded-lg" style="background: var(--bg-elevated); border: 1px solid var(--border-subtle);">
            <button onclick="setGlobalWindow('2026-09')" id="win-2026-09" class="pill-btn active border-0 py-1 px-1.5 text-[11px]">Sep</button>
            <button onclick="setGlobalWindow('2026-10')" id="win-2026-10" class="pill-btn border-0 py-1 px-1.5 text-[11px]">Oct</button>
            <button onclick="setGlobalWindow('60D')" id="win-60D" class="pill-btn border-0 py-1 px-1.5 text-[11px]">60D</button>
            <button onclick="setGlobalWindow('2026-08')" id="win-2026-08" class="pill-btn border-0 py-1 px-1.5 text-[11px]">Aug</button>
            <button onclick="setGlobalWindow('ALL')" id="win-ALL" class="pill-btn border-0 py-1 px-1.5 text-[11px]">90D</button>
          </div>

          <!-- Refund Stripped Mode Toggle -->
          <button id="refundModeBtn" onclick="toggleRefundMode()" class="pill-amethyst py-1 px-2.5 text-xs">
            <span id="refundModeBadge">✓ Net</span>
          </button>

          <!-- Mobile App Frame Simulator Toggle (Desktop Only) -->
          <button id="mobileFrameBtn" onclick="toggleMobileFrame()" class="pill-btn py-1 px-2 text-xs hidden md:inline-flex" title="Preview Phone Frame on Desktop">
            <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect width="14" height="20" x="5" y="2" rx="2"/><path d="M12 18h.01"/></svg>
            <span id="mobileFrameText">Mobile</span>
          </button>

          <!-- Theme Toggle (Crisp Monochrome Vector SVG) -->
          <button id="themeToggleBtn" onclick="toggleTheme()" class="pill-btn py-1 px-2 text-xs" title="Toggle Light / Dark Mode">
            <span id="themeIcon" class="inline-flex items-center">
              <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
            </span>
          </button>
        </div>
      </header>

      <!-- Scrollable Main View Content -->
      <main class="flex-1 overflow-y-auto p-4 sm:p-6 pb-24 md:pb-8 space-y-4">

        <!-- Active Profile Banner (1-Tap Switcher between TK Friends Demo & JC Real) -->
        <div id="activeProfileBanner" class="max-w-6xl mx-auto px-3.5 py-2 rounded-xl flex flex-wrap items-center justify-between gap-2 text-xs" style="background: var(--amethyst-soft); border: 1px solid rgba(124, 58, 237, 0.28);"></div>

        <!-- ============================================================== -->
        <!-- VIEW 01: MONARCH DASHBOARD (EXACT ROB BERGER + PLAY STORE UI)  -->
        <!-- ============================================================== -->
        <div id="view-dashboard" class="space-y-5 max-w-6xl mx-auto">
          <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
            <div class="m-card p-5 lg:col-span-6 flex flex-col justify-between" id="dashboardSpendingCard"></div>
            <div class="m-card p-5 lg:col-span-6 flex flex-col justify-between" id="dashboardNetWorthCard"></div>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
            <div class="m-card p-5 lg:col-span-7" id="dashboardRecentTxnsCard"></div>
            <div class="m-card p-5 lg:col-span-5" id="dashboardCategoriesCard"></div>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
            <div class="m-card p-5 lg:col-span-7" id="dashboardCashFlowMini"></div>
            <div class="m-card p-5 lg:col-span-5" id="dashboardAccountsMini"></div>
          </div>
        </div>

        <!-- ============================================================== -->
        <!-- VIEW 02: ACCOUNTS & NET WORTH (EXACT SCREENSHOT 3 REPLICA)     -->
        <!-- ============================================================== -->
        <div id="view-accounts" class="hidden space-y-5 max-w-6xl mx-auto">
          <div id="accountsViewContent"></div>
        </div>

        <!-- ============================================================== -->
        <!-- VIEW 03: TRANSACTIONS (COMPANY LOGOS + P BADGE + SLIDE DRAWER) -->
        <!-- ============================================================== -->
        <div id="view-transactions" class="hidden space-y-5 max-w-6xl mx-auto">
          <div class="m-card p-5 space-y-4">
            <div class="flex flex-wrap items-center justify-between gap-3">
              <div class="flex items-center gap-2 flex-wrap">
                <span class="text-base font-bold">Transactions</span>
                <span id="txnSummaryPill" class="text-xs px-2.5 py-0.5 rounded-full mono-num" style="background: var(--amethyst-soft); color: var(--amethyst); font-weight: 600;"></span>
                <div class="flex items-center gap-1">
                  <button onclick="stepGlobalWindow(-1)" class="pill-btn py-1 px-2 text-xs" title="Previous Month / Window">◄</button>
                  <select id="txnWindowSelect" onchange="setGlobalWindow(this.value)" class="px-2.5 py-1 text-xs font-semibold cursor-pointer">
                    <option value="2026-08">August 2026</option>
                    <option value="2026-09">September 2026</option>
                    <option value="2026-10">October 2026</option>
                    <option value="60D">60-Day Window</option>
                    <option value="ALL">All 90 Days (Jul–Oct)</option>
                  </select>
                  <button onclick="stepGlobalWindow(1)" class="pill-btn py-1 px-2 text-xs" title="Next Month / Window">►</button>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <button onclick="openNewTxnModal()" class="pill-amethyst text-xs">＋ Add Txn</button>
                <button onclick="exportFilteredCsv()" class="pill-btn text-xs">↓ Export CSV</button>
                <button onclick="resetTxnFilters()" class="pill-btn text-xs">Reset</button>
              </div>
            </div>

            <!-- Search & Filters -->
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
              <div class="sm:col-span-2">
                <input id="txnSearch" type="text" oninput="renderTransactionsTable()" placeholder="Search merchant, category, #tags, or amount..." class="w-full px-3.5 py-2" />
              </div>
              <div>
                <select id="txnCatFilter" onchange="renderTransactionsTable()" class="w-full px-3 py-2">
                  <option value="ALL">All Categories</option>
                </select>
              </div>
              <div>
                <select id="txnTypeFilter" onchange="renderTransactionsTable()" class="w-full px-3 py-2">
                  <option value="EXPENSE_NET">Net Expenses (Refunds Stripped)</option>
                  <option value="EXPENSE_ALL">All Expense Swipes</option>
                  <option value="REFUND">Merchant Refunds Only</option>
                  <option value="INCOME">Income &amp; Paychecks</option>
                  <option value="TRANSFER">Transfers &amp; Autopays</option>
                  <option value="ALL_LEDGER">Complete Raw Ledger</option>
                </select>
              </div>
            </div>

            <!-- Date-Grouped Monarch Transactions List -->
            <div id="txnDateGroupedList" class="space-y-4 pt-1"></div>
          </div>

          <!-- Refund Pairing Audit Table -->
          <div class="m-card p-5">
            <div class="flex flex-wrap items-center justify-between gap-2 pb-3" style="border-bottom: 1px solid var(--border-subtle);">
              <div>
                <h3 class="text-sm font-bold">Paired Merchant Refunds &amp; Credits Audit</h3>
                <p class="text-xs" style="color: var(--text-secondary);">Automatically linked to original purchases so returns never inflate your true spending</p>
              </div>
              <span id="refundAuditTotalBadge" class="text-xs font-semibold px-3 py-1 rounded-full mono-num" style="background: var(--monarch-green-soft); color: var(--monarch-green);"></span>
            </div>
            <div id="refundAuditList" class="divide-y text-xs mt-2 max-h-80 overflow-y-auto" style="border-color: var(--border-subtle);"></div>
          </div>
        </div>

        <!-- ============================================================== -->
        <!-- VIEW 04: CASH FLOW (EXACT WATERFALL ALLUVIAL SANKEY DIAGRAM)   -->
        <!-- ============================================================== -->
        <div id="view-cashflow" class="hidden space-y-4 max-w-6xl mx-auto">
          <div id="cashFlowViewContent"></div>
        </div>

        <!-- ============================================================== -->
        <!-- VIEW 05: BUDGET ("A budget that flexes with your life")        -->
        <!-- ============================================================== -->
        <div id="view-budget" class="hidden space-y-5 max-w-6xl mx-auto">
          <div id="budgetViewContent"></div>
        </div>

        <!-- ============================================================== -->
        <!-- VIEW 06: RECURRING CALENDAR                                    -->
        <!-- ============================================================== -->
        <div id="view-recurring" class="hidden space-y-5 max-w-6xl mx-auto">
          <div id="recurringViewContent"></div>
        </div>

        <!-- ============================================================== -->
        <!-- VIEW 07: GOALS & 311 VAULT                                     -->
        <!-- ============================================================== -->
        <div id="view-goals" class="hidden space-y-5 max-w-6xl mx-auto">
          <div id="goalsViewContent"></div>
        </div>

        <!-- ============================================================== -->
        <!-- VIEW 08: REPORTS & MERCHANTS                                   -->
        <!-- ============================================================== -->
        <div id="view-reports" class="hidden space-y-5 max-w-6xl mx-auto">
          <div id="reportsViewContent"></div>
        </div>

        <!-- ============================================================== -->
        <!-- VIEW 09: INVESTMENTS (SOFI BROKERAGE + MORGAN STANLEY GSU)     -->
        <!-- ============================================================== -->
        <div id="view-investments" class="hidden space-y-5 max-w-6xl mx-auto">
          <div id="investmentsViewContent"></div>
        </div>

        <!-- ============================================================== -->
        <!-- VIEW 10: ADVICE & SOLVENCY SIMULATOR                           -->
        <!-- ============================================================== -->
        <div id="view-advisor" class="hidden space-y-5 max-w-6xl mx-auto">
          <div id="advisorViewContent"></div>
        </div>

      </main>

      <!-- ================================================================ -->
      <!-- NATIVE iOS / ANDROID BOTTOM TAB BAR (Exact 6 Geometric SVGs)     -->
      <!-- ================================================================ -->
      <nav id="mobileBottomNav" style="background: var(--bg-header); border-top: 1px solid var(--border-subtle); backdrop-filter: blur(16px); padding-bottom: env(safe-area-inset-bottom, 6px);" class="md:hidden fixed bottom-0 left-0 right-0 z-30 flex items-center justify-around py-2 px-1">
        <button onclick="switchTab('dashboard')" id="mtab-dashboard" class="flex flex-col items-center gap-0.5 text-[9.5px] font-semibold" style="color: var(--amethyst);">
          <svg class="w-4.5 h-4.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V14a3 3 0 0 1 6 0v8"/></svg>
          <span>Dashboard</span>
        </button>
        <button onclick="switchTab('accounts')" id="mtab-accounts" class="flex flex-col items-center gap-0.5 text-[9.5px] font-medium" style="color: var(--text-secondary);">
          <svg class="w-4.5 h-4.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 11c0 1.66 3.58 3 8 3s8-1.34 8-3"/><path d="M4 16c0 1.66 3.58 3 8 3s8-1.34 8-3"/></svg>
          <span>Accounts</span>
        </button>
        <button onclick="switchTab('transactions')" id="mtab-transactions" class="flex flex-col items-center gap-0.5 text-[9.5px] font-medium" style="color: var(--text-secondary);">
          <svg class="w-4.5 h-4.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="14" x="2" y="5" rx="2"/><line x1="2" x2="22" y1="10" y2="10"/></svg>
          <span>Txns</span>
        </button>
        <button onclick="switchTab('cashflow')" id="mtab-cashflow" class="flex flex-col items-center gap-0.5 text-[9.5px] font-medium" style="color: var(--text-secondary);">
          <svg class="w-4.5 h-4.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="13" width="3.5" height="7" rx="1"/><rect x="10.25" y="5" width="3.5" height="15" rx="1"/><rect x="16.5" y="9" width="3.5" height="11" rx="1"/></svg>
          <span>Cash Flow</span>
        </button>
        <button onclick="switchTab('budget')" id="mtab-budget" class="flex flex-col items-center gap-0.5 text-[9.5px] font-medium" style="color: var(--text-secondary);">
          <svg class="w-4.5 h-4.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/><line x1="9" x2="9" y1="3" y2="18"/><line x1="15" x2="15" y1="6" y2="21"/></svg>
          <span>Budget</span>
        </button>
        <button onclick="openMobileSidebar()" id="mtab-more" class="flex flex-col items-center gap-0.5 text-[9.5px] font-medium" style="color: var(--text-secondary);">
          <svg class="w-4.5 h-4.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/></svg>
          <span>More</span>
        </button>
      </nav>

      <!-- Touch-Draggable & Collapsible Floating Monark™ Quick-Orb inside the App -->
      <div id="monarkInAppOrb" style="position:fixed;right:14px;bottom:calc(68px + env(safe-area-inset-bottom,0px));z-index:45;display:inline-flex;align-items:center;gap:6px;padding:6px 10px;border-radius:999px;background:linear-gradient(135deg,rgba(124,58,237,0.92),rgba(76,29,149,0.92));backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,0.32);color:#fff;font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:700;cursor:grab;user-select:none;-webkit-user-select:none;touch-action:none;box-shadow:0 6px 20px rgba(124,58,237,0.45);" title="Drag anywhere to move out of the way">
        <span style="opacity:0.7;letter-spacing:-1px;font-size:11px;">⋮⋮</span>
        <span onclick="onInAppOrbPrimaryTap(event)" id="inAppOrbBadge" style="cursor:pointer;">◈ TK</span>
        <div id="inAppOrbExpanded" style="display:inline-flex;align-items:center;gap:5px;">
          <button onclick="event.stopPropagation();if(!window._inAppOrbDragged)toggleProfile();" style="background:rgba(255,255,255,0.18);border:1px solid rgba(255,255,255,0.28);color:#fff;border-radius:999px;padding:2px 7px;font-size:10px;font-weight:700;cursor:pointer;">⇄ JC/TK</button>
          <a href="/" onclick="if(window._inAppOrbDragged){event.preventDefault();}" style="background:rgba(0,0,0,0.28);border:1px solid rgba(255,255,255,0.24);color:#fff;border-radius:999px;padding:2px 7px;font-size:10px;font-weight:700;text-decoration:none;">PX11</a>
          <button onclick="event.stopPropagation();toggleInAppOrbCollapse();" style="background:rgba(0,0,0,0.28);border:1px solid rgba(255,255,255,0.24);color:#fff;border-radius:999px;padding:2px 6px;font-size:10px;font-weight:700;cursor:pointer;" title="Minimize icon">−</button>
        </div>
      </div>

    </div>
  </div>

  <!-- ==================================================================== -->
  <!-- SLIDE-OVER TRANSACTION INSPECTOR DRAWER                              -->
  <!-- ==================================================================== -->
  <div id="txnDrawerBackdrop" onclick="closeTxnModal()" class="fixed inset-0 z-40 hidden" style="background: rgba(11, 9, 20, 0.55); backdrop-filter: blur(3px);"></div>
  <aside id="txnDrawer" style="background: var(--bg-surface); border-left: 1px solid var(--border-subtle); width: 410px; max-width: 94vw;" class="fixed top-0 right-0 bottom-0 z-50 hidden flex flex-col justify-between p-6 shadow-2xl">
    <div class="space-y-4 overflow-y-auto pr-1">
      <div class="flex items-center justify-between pb-3" style="border-bottom: 1px solid var(--border-subtle);">
        <div>
          <span class="text-[11px] font-bold uppercase tracking-wider" style="color: var(--amethyst);">Monark™ Inspector (Bootleg Edition)</span>
          <h3 id="modalTitle" class="text-base font-bold mt-0.5">Transaction Details</h3>
        </div>
        <button onclick="closeTxnModal()" class="pill-btn px-2.5 py-1">✕</button>
      </div>
      <div id="modalBody" class="space-y-3.5 text-xs"></div>
    </div>
    <div class="pt-4 flex items-center justify-between gap-2" style="border-top: 1px solid var(--border-subtle);">
      <button onclick="closeTxnModal()" class="pill-btn flex-1 py-2 justify-center">Cancel</button>
      <button onclick="saveTxnModal()" class="pill-amethyst flex-1 py-2 justify-center">Save Changes</button>
    </div>
  </aside>

  <!-- ==================================================================== -->
  <!-- INSTALL ON iPHONE / ANDROID PWA MODAL                                -->
  <!-- ==================================================================== -->
  <div id="mobileInstallModal" onclick="closeMobileInstallModal()" class="fixed inset-0 z-50 hidden flex items-center justify-center p-4" style="background: rgba(11, 9, 20, 0.65); backdrop-filter: blur(4px);">
    <div onclick="event.stopPropagation()" class="m-card max-w-md w-full p-6 space-y-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2.5">
          <div class="w-9 h-9 rounded-xl flex items-center justify-center" style="background: linear-gradient(135deg, #8B5CF6, #7C3AED);">
            <svg class="w-5 h-5" viewBox="0 0 512 512" fill="none">
              <path d="M256 226C212 140 105 112 86 178C71 232 115 292 172 315C156 344 168 388 206 388C234 388 248 360 256 332C264 360 278 388 306 388C344 388 356 344 340 315C397 292 441 232 426 178C407 112 300 140 256 226Z" stroke="#FFFFFF" stroke-width="40" stroke-linecap="round"/>
            </svg>
          </div>
          <div>
            <h3 class="text-base font-bold">Install Monark™ (Definitely Not Monarch)</h3>
            <p class="text-xs" style="color: var(--text-secondary);">100% Stolen Vibes · $0.00/yr Subscription · Powered by a $1.50/mo SimpleFIN Pipe</p>
          </div>
        </div>
        <button onclick="closeMobileInstallModal()" class="pill-btn px-2.5 py-1">✕</button>
      </div>
      <div class="space-y-3 text-xs leading-relaxed" style="color: var(--text-secondary);">
        <div class="p-3.5 rounded-xl" style="background: var(--bg-elevated);">
          <div class="font-bold text-sm mb-1" style="color: var(--text-primary);">Apple iPhone / iPad (iOS Safari)</div>
          1. Open the app URL in <strong>Safari</strong> on your iPhone.<br/>
          2. Tap the <strong>Share</strong> button (<span class="mono-num">↑</span>) at the bottom of Safari.<br/>
          3. Tap <strong>"Add to Home Screen"</strong> — launches full-screen with the Royal Amethyst Moth-Ark™ icon and zero $99.99/yr VC subscription fees!
        </div>
        <div class="p-3.5 rounded-xl" style="background: var(--bg-elevated);">
          <div class="font-bold text-sm mb-1" style="color: var(--text-primary);">Android / Pixel 11 Pro (Chrome)</div>
          1. Open the app URL in <strong>Chrome</strong> on your Pixel 11 Pro.<br/>
          2. Tap <strong>"Install App"</strong> (or <strong>⋮ Menu → Add to Home screen</strong>) to install the native Monark™ WebAPK.
        </div>
      </div>
    </div>
  </div>

  <script>
    const INITIAL_DATASET = __MONARCH_DATASET_JSON__;

    // =========================================================================
    // FICTIONAL PARODY PROFILE: "TK" — THOMAS KURIAN (GOOGLE CLOUD CEO DEMO)
    // Safe to show friends with zero personal financial data leaked!
    // =========================================================================
    const TK_DATASET = {
      generated_at: "2026-10-13T12:00:00Z",
      owner: "Thomas Kurian (tkurian@google.com — Google Cloud CEO & Sovereign Margin Enforcer)",
      summary: {
        total_assets: 434990000.42,
        total_liabilities: 1804900.00,
        net_worth: 433185100.42,
        unencumbered_net_worth: 391185100.42,
        sofi_2752_balance: 88500000.00,
        lease_311_remaining_obligation: 42000000.00,
        sofi_2752_true_buffer: 46500000.00,
        total_records: 24,
        total_refunds_paired: 478599.99,
        refund_count: 4
      },
      accounts: [
        {
          account_id: "TK-4473",
          name: "Enterprise Deal Desk Checking- 4473 (4473)",
          institution: "bofa",
          institution_label: "Bank of America",
          type: "Checking · Q4 Pipeline Slush",
          is_liability: false,
          balance: 14250000.00,
          abs_balance: 14250000.00,
          available_balance: 14250000.00,
          balance_date: "2026-10-12"
        },
        {
          account_id: "TK-4499",
          name: "MTV-CLD Free Coffee & Microkitchen Budget- 4499 (4499)",
          institution: "bofa",
          institution_label: "Bank of America",
          type: "Zero-Based Cost Cutting Vault",
          is_liability: false,
          balance: 0.42,
          abs_balance: 0.42,
          available_balance: 0.42,
          balance_date: "2026-10-12"
        },
        {
          account_id: "TK-2752",
          name: "NVIDIA Blackwell B200 GPU Escrow - 2752 (2752)",
          institution: "sofi",
          institution_label: "SoFi",
          type: "High-Yield AI Cluster Reserve",
          is_liability: false,
          balance: 88500000.00,
          abs_balance: 88500000.00,
          available_balance: 46500000.00,
          balance_date: "2026-10-12"
        },
        {
          account_id: "TK-5857",
          name: "Oracle-to-Spanner Takeout Bounty Checking - 5857 (5857)",
          institution: "sofi",
          institution_label: "SoFi",
          type: "Checking · Larry Tears Fund",
          is_liability: false,
          balance: 19840000.00,
          abs_balance: 19840000.00,
          available_balance: 19840000.00,
          balance_date: "2026-10-12"
        },
        {
          account_id: "TK-6725",
          name: "Alphabet Class C GSU & Anthropic Stake (6725)",
          institution: "sofi",
          institution_label: "SoFi",
          type: "Executive Equity & AI Sovereign Fund",
          is_liability: false,
          balance: 312400000.00,
          abs_balance: 312400000.00,
          available_balance: 312400000.00,
          balance_date: "2026-10-12"
        },
        {
          account_id: "TK-4002",
          name: "Amex Centurion® Black Card — Cloud CEO (4002)",
          institution: "amex",
          institution_label: "American Express",
          type: "Credit Card · No Preset TPU Limit",
          is_liability: true,
          balance: -1420690.00,
          abs_balance: 1420690.00,
          available_balance: 0.0,
          balance_date: "2026-10-12"
        },
        {
          account_id: "TK-8577",
          name: "Gulfstream G700 & Davos Tarmac Visa- 8577 (8577)",
          institution: "bofa",
          institution_label: "Bank of America",
          type: "Credit Card · Fortune 500 CIO Dinners",
          is_liability: true,
          balance: -384210.00,
          abs_balance: 384210.00,
          available_balance: 0.0,
          balance_date: "2026-10-12"
        }
      ],
      transactions: [
        // --- SEPTEMBER 2026 (DEFAULT VIEW) ---
        {
          txn_id: "TK-TRN-01",
          date: "2026-09-30",
          period: "2026-09",
          description: "MORGAN STANLEY GOOG CLASS C GSU MEGA-VEST",
          merchant_clean: "Morgan Stanley — GOOG GSU Mega-Vest",
          category: "Equity & Investment Inflows",
          flex_bucket: "Income",
          txn_type: "income",
          direction: "inflow",
          institution: "bofa",
          account_name: "Enterprise Deal Desk Checking- 4473 (4473)",
          amount: 4850000.00,
          net_amount: 4850000.00,
          refunded_amount: 0.0,
          tags: ["#gsu", "#cloud-34pct-margin"],
          notes: "Quarterly CEO equity cliff after beating AWS growth rate"
        },
        {
          txn_id: "TK-TRN-02",
          date: "2026-09-28",
          period: "2026-09",
          description: "NVIDIA CORP SANTA CLARA — JENSEN LEATHER JACKET & 8X H200 NODE",
          merchant_clean: "NVIDIA Corp — 8x H200 Node & Leather Jacket Tribute",
          category: "Electronics, Home & Retail",
          flex_bucket: "Non-Monthly",
          txn_type: "expense",
          direction: "outflow",
          institution: "amex",
          account_name: "Amex Centurion® Black Card — Cloud CEO (4002)",
          amount: 385000.00,
          net_amount: 385000.00,
          refunded_amount: 0.0,
          tags: ["#gpu-allocation", "#vertex-ai"],
          notes: "Had to buy Jensen lunch at Denny's + 1 crocodile leather jacket to unlock 64 extra Blackwell racks"
        },
        {
          txn_id: "TK-TRN-03",
          date: "2026-09-25",
          period: "2026-09",
          description: "ATHERTON COMPOUND HOA & ROBOTIC KOI POND FIBER PEERING",
          merchant_clean: "Atherton Estate & us-west1 Direct Fiber Peering",
          category: "Housing & Rent",
          flex_bucket: "Fixed",
          txn_type: "expense",
          direction: "outflow",
          institution: "bofa",
          account_name: "Enterprise Deal Desk Checking- 4473 (4473)",
          amount: 295000.00,
          net_amount: 295000.00,
          refunded_amount: 0.0,
          tags: ["#atherton", "#sub-1ms-spanner"],
          notes: "Includes 400Gbps dedicated dark fiber from bedroom study to Sunnyvale MP7"
        },
        {
          txn_id: "TK-TRN-04",
          date: "2026-09-22",
          period: "2026-09",
          description: "GULFSTREAM AEROSPACE JET FUEL — SJC TO DAVOS & TOKYO NEXT",
          merchant_clean: "Gulfstream G700 Jet Fuel (SJC → Davos → Tokyo)",
          category: "Travel, Flights & Hotels",
          flex_bucket: "Non-Monthly",
          txn_type: "expense",
          direction: "outflow",
          institution: "amex",
          account_name: "Amex Centurion® Black Card — Cloud CEO (4002)",
          amount: 214800.00,
          net_amount: 214800.00,
          refunded_amount: 0.0,
          tags: ["#ceo-roadshow", "#zero-turbulence"],
          notes: "Closed 3 sovereign cloud deals mid-flight over Greenland"
        },
        {
          txn_id: "TK-TRN-05",
          date: "2026-09-19",
          period: "2026-09",
          description: "DELOITTE & ACCENTURE 2,400-SLIDE SYNERGY DECK FACTORY",
          merchant_clean: "Deloitte Enterprise 2,400-Slide Deck Factory",
          category: "Family Support, Zelle & Cash",
          flex_bucket: "Non-Monthly",
          txn_type: "expense",
          direction: "outflow",
          institution: "bofa",
          account_name: "Gulfstream G700 & Davos Tarmac Visa- 8577 (8577)",
          amount: 165000.00,
          net_amount: 165000.00,
          refunded_amount: 0.0,
          tags: ["#2x2-matrix", "#enterprise-synergy"],
          notes: "Emergency Sunday night formatting of 412 architecture diagrams for Fortune 10 bank"
        },
        {
          txn_id: "TK-TRN-06",
          date: "2026-09-16",
          period: "2026-09",
          description: "BRIONI MILAN — 14 IDENTICAL NAVY 3-PIECE KEYNOTE SUITS",
          merchant_clean: "Brioni Milan — 14 Identical 3-Piece Keynote Suits",
          category: "Apparel & Luxury Shopping",
          flex_bucket: "Flexible",
          txn_type: "expense",
          direction: "outflow",
          institution: "amex",
          account_name: "Amex Centurion® Black Card — Cloud CEO (4002)",
          amount: 148500.00,
          net_amount: 100000.00,
          refunded_amount: 48500.00,
          refund_status: "partial",
          tags: ["#three-piece-armor", "#cloud-next"],
          notes: "Returned 4 casual polo shirts (-$48,500 refunded) — Thomas Kurian sleeps in a bespoke vest"
        },
        {
          txn_id: "TK-TRN-07",
          date: "2026-09-15",
          period: "2026-09",
          description: "GOOGLE LLC — CEO PAYROLL & OPERATING MARGIN EXPANSION BONUS",
          merchant_clean: "Google LLC — Cloud CEO Payroll & Margin Bonus",
          category: "Paychecks & Salary",
          flex_bucket: "Income",
          txn_type: "income",
          direction: "inflow",
          institution: "sofi",
          account_name: "Oracle-to-Spanner Takeout Bounty Checking - 5857 (5857)",
          amount: 2450000.00,
          net_amount: 2450000.00,
          refunded_amount: 0.0,
          tags: ["#payroll", "#rule-of-40"],
          notes: "Includes bonus for replacing free Kombucha taps with lukewarm tap water"
        },
        {
          txn_id: "TK-TRN-08",
          date: "2026-09-14",
          period: "2026-09",
          description: "ORACLE LICENSE AUDIT DEFENSE LAWYERS LLP REDWOOD SHORES",
          merchant_clean: "Oracle License Audit Defense Lawyers LLP",
          category: "Utilities & Insurance",
          flex_bucket: "Fixed",
          txn_type: "expense",
          direction: "outflow",
          institution: "bofa",
          account_name: "Gulfstream G700 & Davos Tarmac Visa- 8577 (8577)",
          amount: 125000.00,
          net_amount: 125000.00,
          refunded_amount: 0.0,
          tags: ["#larry-ellison", "#java-se-trap"],
          notes: "Monthly legal shield blocking Larry from auditing my personal MacBook JVM"
        },
        {
          txn_id: "TK-TRN-09",
          date: "2026-09-11",
          period: "2026-09",
          description: "NOBU PALO ALTO — FORTUNE 500 CIO WAGYU & SPANNER CLOSE",
          merchant_clean: "Nobu Palo Alto — CIO Wagyu & $500M Cloud Close",
          category: "Food Delivery & Dining",
          flex_bucket: "Flexible",
          txn_type: "expense",
          direction: "outflow",
          institution: "amex",
          account_name: "Amex Centurion® Black Card — Cloud CEO (4002)",
          amount: 42600.00,
          net_amount: 42600.00,
          refunded_amount: 0.0,
          tags: ["#deal-desk", "#signed-on-napkin"],
          notes: "CIO signed a 7-year BigQuery + Vertex AI commit before the yellowtail sashimi arrived"
        },
        {
          txn_id: "TK-TRN-10",
          date: "2026-09-08",
          period: "2026-09",
          description: "WORKDAY & SALESFORCE ENTERPRISE SEAT RENEWAL",
          merchant_clean: "Salesforce & Workday Unlimited CRM Tier",
          category: "Subscriptions & Digital",
          flex_bucket: "Fixed",
          txn_type: "expense",
          direction: "outflow",
          institution: "amex",
          account_name: "Amex Centurion® Black Card — Cloud CEO (4002)",
          amount: 64000.00,
          net_amount: 64000.00,
          refunded_amount: 0.0,
          tags: ["#benioff", "#pipeline-hygiene"],
          notes: "For checking Forecast Accuracy at 4:15 AM every Monday"
        },
        {
          txn_id: "TK-TRN-11",
          date: "2026-09-05",
          period: "2026-09",
          description: "UBER HELICOPTER BLADE — SFO TO SUNNYVALE MP7 ROOFTOP",
          merchant_clean: "Uber Copter — SFO to Sunnyvale MP7 Helipad",
          category: "Rideshare & Transit",
          flex_bucket: "Flexible",
          txn_type: "expense",
          direction: "outflow",
          institution: "amex",
          account_name: "Amex Centurion® Black Card — Cloud CEO (4002)",
          amount: 19500.00,
          net_amount: 19500.00,
          refunded_amount: 0.0,
          tags: ["#skip-101-traffic", "#qbr"],
          notes: "US-101 had a 12-minute delay; unacceptable latency for Q3 pipeline review"
        },
        {
          txn_id: "TK-TRN-12",
          date: "2026-09-03",
          period: "2026-09",
          description: "EQUINOX EXECUTIVE CRYO & 4:30AM BIOHACKING LAB",
          merchant_clean: "Equinox Executive Cryo & 4:30 AM Biohacking",
          category: "Fitness & Wellness",
          flex_bucket: "Flexible",
          txn_type: "expense",
          direction: "outflow",
          institution: "amex",
          account_name: "Amex Centurion® Black Card — Cloud CEO (4002)",
          amount: 14200.00,
          net_amount: 14200.00,
          refunded_amount: 0.0,
          tags: ["#sleep-is-for-on-prem"],
          notes: "Liquid nitrogen chamber set to -140°C while reading Gartner Magic Quadrants"
        },
        {
          txn_id: "TK-TRN-13",
          date: "2026-09-02",
          period: "2026-09",
          description: "EREWHON MARKET — $28 CLOUD SMOOTHIES FOR SVP QBR",
          merchant_clean: "Erewhon — $28 Hailey Bieber Cloud Smoothies",
          category: "Groceries & Daily Essentials",
          flex_bucket: "Flexible",
          txn_type: "expense",
          direction: "outflow",
          institution: "bofa",
          account_name: "Gulfstream G700 & Davos Tarmac Visa- 8577 (8577)",
          amount: 11840.00,
          net_amount: 11840.00,
          refunded_amount: 0.0,
          tags: ["#svp-qbr", "#blue-spirulina"],
          notes: "Ordered because they are literally named 'Cloud' smoothies"
        },
        // --- OCTOBER 2026 ---
        {
          txn_id: "TK-TRN-14",
          date: "2026-10-12",
          period: "2026-10",
          description: "AWS US-EAST-1 SHADOW IT EC2 & S3 BILL (WHO LEFT THIS ON?!)",
          merchant_clean: "AWS Shadow IT Bill (WHO LEFT EC2 ON IN US-EAST-1?!)",
          category: "Subscriptions & Digital",
          flex_bucket: "Fixed",
          txn_type: "expense",
          direction: "outflow",
          institution: "bofa",
          account_name: "Gulfstream G700 & Davos Tarmac Visa- 8577 (8577)",
          amount: 4219.99,
          net_amount: 4219.99,
          refunded_amount: 0.0,
          tags: ["#traitor-audit", "#migrate-to-gce"],
          notes: "Found an unlabelled t3.2xlarge in us-east-1; launching full SVP investigation"
        },
        {
          txn_id: "TK-TRN-15",
          date: "2026-10-11",
          period: "2026-10",
          description: "GARTNER MAGIC QUADRANT GOLD-LEAF FRAMING BOUTIQUE",
          merchant_clean: "Gartner Magic Quadrant 24K Gold Framing Shop",
          category: "Electronics, Home & Retail",
          flex_bucket: "Non-Monthly",
          txn_type: "expense",
          direction: "outflow",
          institution: "amex",
          account_name: "Amex Centurion® Black Card — Cloud CEO (4002)",
          amount: 18400.00,
          net_amount: 18400.00,
          refunded_amount: 0.0,
          tags: ["#upper-right-quadrant"],
          notes: "Framed 47 copies of the AI Infrastructure Leader chart for every bathroom in Sunnyvale"
        },
        {
          txn_id: "TK-TRN-16",
          date: "2026-10-09",
          period: "2026-10",
          description: "ORACLE CORP — LARRY ELLISON PETTY PAPER DIVIDEND CHECK",
          merchant_clean: "Oracle Corp — Larry Ellison Petty Dividend Check",
          category: "Interest & Dividends",
          flex_bucket: "Income",
          txn_type: "income",
          direction: "inflow",
          institution: "bofa",
          account_name: "Enterprise Deal Desk Checking- 4473 (4473)",
          amount: 12.50,
          net_amount: 12.50,
          refunded_amount: 0.0,
          tags: ["#larry-trolling"],
          notes: "Larry still mails a physical $12.50 paper check from Lanai just to make me endorse it"
        },
        {
          txn_id: "TK-TRN-17",
          date: "2026-10-07",
          period: "2026-10",
          description: "GOOGLE LLC — OCTOBER CEO PAYROLL & CLOUD MARGIN BONUS",
          merchant_clean: "Google LLC — Cloud CEO Bi-Weekly Payroll",
          category: "Paychecks & Salary",
          flex_bucket: "Income",
          txn_type: "income",
          direction: "inflow",
          institution: "sofi",
          account_name: "Oracle-to-Spanner Takeout Bounty Checking - 5857 (5857)",
          amount: 1225000.00,
          net_amount: 1225000.00,
          refunded_amount: 0.0,
          tags: ["#payroll"],
          notes: "Direct deposit into Oracle-to-Spanner Takeout Checking"
        },
        {
          txn_id: "TK-TRN-18",
          date: "2026-10-05",
          period: "2026-10",
          description: "MORGAN STANLEY GOOG OCTOBER GSU RELEASE",
          merchant_clean: "Morgan Stanley — GOOG October GSU Vest",
          category: "Equity & Investment Inflows",
          flex_bucket: "Income",
          txn_type: "income",
          direction: "inflow",
          institution: "bofa",
          account_name: "Enterprise Deal Desk Checking- 4473 (4473)",
          amount: 1950000.00,
          net_amount: 1950000.00,
          refunded_amount: 0.0,
          tags: ["#gsu"],
          notes: "Monthly Alphabet Class C vest"
        },
        {
          txn_id: "TK-TRN-19",
          date: "2026-10-03",
          period: "2026-10",
          description: "ATHERTON COMPOUND HOA & PRIVATE TPU LIQUID COOLING",
          merchant_clean: "Atherton Estate & Home TPU v6e Pod Cooling",
          category: "Housing & Rent",
          flex_bucket: "Fixed",
          txn_type: "expense",
          direction: "outflow",
          institution: "bofa",
          account_name: "Enterprise Deal Desk Checking- 4473 (4473)",
          amount: 295000.00,
          net_amount: 295000.00,
          refunded_amount: 0.0,
          tags: ["#atherton"],
          notes: "Heated the infinity pool using waste heat from a garage TPU v6e rack"
        },
        {
          txn_id: "TK-TRN-20",
          date: "2026-10-01",
          period: "2026-10",
          description: "MONARCH MONEY $99.99/YR VC BUTTERFLY APP (CANCELED!)",
          merchant_clean: "Monarch Money ($99.99/yr VC App — Canceled for Monark™)",
          category: "Subscriptions & Digital",
          flex_bucket: "Fixed",
          txn_type: "expense",
          direction: "outflow",
          institution: "amex",
          account_name: "Amex Centurion® Black Card — Cloud CEO (4002)",
          amount: 99.99,
          net_amount: 0.00,
          refunded_amount: 99.99,
          refund_status: "full",
          tags: ["#saved-99-bucks", "#monark-bootleg"],
          notes: "Demanded a full $99.99 refund after switching to Jesus's $0/yr Monark™ Moth-Ark Bootleg OS!"
        },
        // --- AUGUST 2026 ---
        {
          txn_id: "TK-TRN-21",
          date: "2026-08-25",
          period: "2026-08",
          description: "GOOGLE LLC — AUGUST CEO PAYROLL & AI CONSUMPTION BONUS",
          merchant_clean: "Google LLC — Cloud CEO August Payroll",
          category: "Paychecks & Salary",
          flex_bucket: "Income",
          txn_type: "income",
          direction: "inflow",
          institution: "sofi",
          account_name: "Oracle-to-Spanner Takeout Bounty Checking - 5857 (5857)",
          amount: 2450000.00,
          net_amount: 2450000.00,
          refunded_amount: 0.0,
          tags: ["#payroll"],
          notes: "August executive payroll"
        },
        {
          txn_id: "TK-TRN-22",
          date: "2026-08-20",
          period: "2026-08",
          description: "ATHERTON COMPOUND HOA & FIBER PEERING",
          merchant_clean: "Atherton Estate & us-west1 Direct Fiber Peering",
          category: "Housing & Rent",
          flex_bucket: "Fixed",
          txn_type: "expense",
          direction: "outflow",
          institution: "bofa",
          account_name: "Enterprise Deal Desk Checking- 4473 (4473)",
          amount: 295000.00,
          net_amount: 295000.00,
          refunded_amount: 0.0,
          tags: ["#atherton"],
          notes: "August estate & fiber peering"
        },
        {
          txn_id: "TK-TRN-23",
          date: "2026-08-19",
          period: "2026-08",
          description: "FRENCH LAUNDRY YOUNTVILLE — SOVEREIGN AI SUMMIT BUYOUT",
          merchant_clean: "The French Laundry — Fortune 50 CEO Buyout",
          category: "Food Delivery & Dining",
          flex_bucket: "Flexible",
          txn_type: "expense",
          direction: "outflow",
          institution: "amex",
          account_name: "Amex Centurion® Black Card — Cloud CEO (4002)",
          amount: 88400.00,
          net_amount: 88400.00,
          refunded_amount: 0.0,
          tags: ["#tasting-menu", "#gemini-enterprise"],
          notes: "Replaced dessert menu with 12-page BigQuery Migration TCO analysis"
        }
      ],
      refund_audit_log: [
        {
          merchant: "Oracle Cloud Infrastructure (OCI Accidental Click)",
          institution: "amex",
          purchase_date: "2026-09-10",
          refund_date: "2026-09-11",
          original_amount: 250000.00,
          refund_amount: 250000.00,
          status: "FULL REFUND PAIRED · MIGRATED TO GKE"
        },
        {
          merchant: "Microsoft Azure OpenAI PTU Reservation",
          institution: "bofa",
          purchase_date: "2026-09-14",
          refund_date: "2026-09-16",
          original_amount: 180000.00,
          refund_amount: 180000.00,
          status: "FULL REFUND PAIRED · SWAPPED TO VERTEX AI"
        },
        {
          merchant: "Brioni Milan (4 Casual Polo Shirts Returned)",
          institution: "amex",
          purchase_date: "2026-09-16",
          refund_date: "2026-09-18",
          original_amount: 148500.00,
          refund_amount: 48500.00,
          status: "PARTIAL RETURN · SUITS ONLY"
        },
        {
          merchant: "Monarch Money ($99.99/yr Butterfly App)",
          institution: "amex",
          purchase_date: "2026-10-01",
          refund_date: "2026-10-01",
          original_amount: 99.99,
          refund_amount: 99.99,
          status: "FULL REFUND · REPLACED BY $0/YR MONARK™"
        }
      ]
    };
  </script>
  <script>
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js').catch(() => {});
    }

    const urlProfileParam = new URLSearchParams(window.location.search).get("profile");
    let activeProfile = (urlProfileParam ? urlProfileParam.toUpperCase() : (localStorage.getItem("monark_profile") || "TK")) === "JC" ? "JC" : "TK";
    let state = JSON.parse(JSON.stringify(activeProfile === "TK" ? TK_DATASET : INITIAL_DATASET));
    let activeTab = "dashboard";
    let globalWindow = "2026-09";
    let bankScope = "ALL";
    let refundStrippedMode = true;
    let mobileFrameMode = false;
    let acctSummaryMode = "totals";
    let nwRange = "1M";
    let acctChartMetric = "net_worth";
    let spendCompareMode = "vs_last_month";
    let cashFlowBreakdown = "group";
    let recurringMonth = "2026-10";
    let invRange = "1M";
    let reportsSortMode = "net";
    let collapsedAcctGroups = {};
    let collapsedBudgetGroups = {};
    let collapsedTxnDates = {};
    let editingTxnId = null;
    let editingModalMode = "txn";
    let editingModalKey = null;

    function recalcSummaryFromAccounts() {
      const s = state.summary;
      let assets = 0, liabs = 0;
      state.accounts.forEach(a => {
        if (a.is_liability) {
          const v = Math.abs(Number(a.balance || 0));
          a.balance = -v;
          a.abs_balance = v;
          liabs += v;
        } else {
          const v = Number(a.balance || 0);
          a.abs_balance = Math.abs(v);
          assets += v;
          if (a.name.includes("2752")) {
            s.sofi_2752_balance = v;
          }
        }
      });
      s.total_assets = assets;
      s.total_liabilities = liabs;
      s.net_worth = assets - liabs;
      s.sofi_2752_true_buffer = Math.max(0, (s.sofi_2752_balance || 0) - (s.lease_311_remaining_obligation || 0));
      s.unencumbered_net_worth = s.net_worth - (s.lease_311_remaining_obligation || 0);
    }

    function setProfile(profId) {
      activeProfile = profId === "JC" ? "JC" : "TK";
      try { localStorage.setItem("monark_profile", activeProfile); } catch (e) {}
      state = JSON.parse(JSON.stringify(activeProfile === "TK" ? TK_DATASET : INITIAL_DATASET));
      if (activeProfile === "TK") {
        simAmexPay = 1420690.00;
        simBofaPay = 384210.00;
        simTransferToBofa = 2000000.00;
      } else {
        simAmexPay = 18748.24;
        simBofaPay = 8754.52;
        simTransferToBofa = 12000.00;
      }
      const sel = document.getElementById("txnCatFilter");
      if (sel) sel.innerHTML = '<option value="ALL">All Categories</option>';
      renderAll();
    }

    function toggleProfile() {
      setProfile(activeProfile === "TK" ? "JC" : "TK");
    }

    function renderProfileControls() {
      const btnTK = document.getElementById("profBtn-TK");
      const btnJC = document.getElementById("profBtn-JC");
      if (btnTK && btnJC) {
        if (activeProfile === "TK") {
          btnTK.style.background = "var(--amethyst)";
          btnTK.style.color = "#FFFFFF";
          btnJC.style.background = "transparent";
          btnJC.style.color = "var(--text-secondary)";
        } else {
          btnJC.style.background = "var(--amethyst)";
          btnJC.style.color = "#FFFFFF";
          btnTK.style.background = "transparent";
          btnTK.style.color = "var(--text-secondary)";
        }
      }
      const av = document.getElementById("sidebarProfileAvatar");
      const nm = document.getElementById("sidebarProfileName");
      const sb = document.getElementById("sidebarProfileSub");
      if (av && nm && sb) {
        if (activeProfile === "TK") {
          av.textContent = "TK";
          av.style.background = "linear-gradient(135deg, #2563EB, #4C1D95)";
          nm.textContent = "Thomas Kurian (TK)";
          sb.textContent = "CEO Parody Demo · Tap for JC";
        } else {
          av.textContent = "JC";
          av.style.background = "linear-gradient(135deg, #8B5CF6, #4C1D95)";
          nm.textContent = "Jesus Chavez (JC)";
          sb.textContent = "Live SimpleFIN · Tap for TK";
        }
      }
      const orbBadge = document.getElementById("inAppOrbBadge");
      if (orbBadge) {
        orbBadge.textContent = activeProfile === "TK" ? "◈ TK" : "◈ JC";
      }
      const banner = document.getElementById("activeProfileBanner");
      if (banner) {
        if (window._monarkBannerDismissed) {
          banner.style.display = "none";
          return;
        }
        banner.style.display = "flex";
        if (activeProfile === "TK") {
          banner.style.background = "var(--amethyst-soft)";
          banner.style.borderColor = "rgba(124, 58, 237, 0.32)";
          banner.innerHTML = `
            <div class="flex items-center gap-2 min-w-0">
              <span class="px-2 py-0.5 rounded-md font-mono font-bold text-[10px] text-white flex-shrink-0" style="background: var(--amethyst);">TK DEMO MODE</span>
              <span class="font-medium truncate" style="color: var(--text-primary);">
                <strong>Thomas Kurian (Google Cloud CEO)</strong> · Parody Demo (Safe for Friends)
              </span>
            </div>
            <div class="flex items-center gap-1.5 flex-shrink-0">
              <button onclick="setProfile('JC')" class="pill-btn py-1 px-2.5 text-[11px] font-bold" style="color: var(--amethyst); border-color: rgba(124,58,237,0.35);">
                ⇄ Switch to JC
              </button>
              <button onclick="window._monarkBannerDismissed=true;document.getElementById('activeProfileBanner').style.display='none';" class="pill-btn py-1 px-2 text-[11px]" title="Hide banner">✕</button>
            </div>
          `;
        } else {
          banner.style.background = "var(--monarch-green-soft)";
          banner.style.borderColor = "rgba(22, 163, 74, 0.30)";
          banner.innerHTML = `
            <div class="flex items-center gap-2 min-w-0">
              <span class="px-2 py-0.5 rounded-md font-mono font-bold text-[10px] text-white flex-shrink-0" style="background: var(--monarch-green);">JC LIVE LEDGER</span>
              <span class="font-medium truncate" style="color: var(--text-primary);">
                <strong>Jesus Chavez</strong> · Live 7-Account SimpleFIN / Firestore Portfolio
              </span>
            </div>
            <div class="flex items-center gap-1.5 flex-shrink-0">
              <button onclick="setProfile('TK')" class="pill-btn py-1 px-2.5 text-[11px] font-bold" style="color: var(--amethyst); border-color: rgba(124,58,237,0.35);">
                ◈ Switch to TK
              </button>
              <button onclick="window._monarkBannerDismissed=true;document.getElementById('activeProfileBanner').style.display='none';" class="pill-btn py-1 px-2 text-[11px]" title="Hide banner">✕</button>
            </div>
          `;
        }
      }
    }

    function toggleInAppOrbCollapse() {
      if (window._inAppOrbDragged) return;
      const exp = document.getElementById("inAppOrbExpanded");
      const orb = document.getElementById("monarkInAppOrb");
      if (!exp || !orb) return;
      const isHidden = exp.style.display === "none";
      exp.style.display = isHidden ? "inline-flex" : "none";
      orb.style.opacity = isHidden ? "0.96" : "0.78";
      try { localStorage.setItem("monark_inapp_orb_collapsed", isHidden ? "0" : "1"); } catch (e) {}
    }

    function onInAppOrbPrimaryTap(ev) {
      if (ev) ev.stopPropagation();
      if (window._inAppOrbDragged) return;
      const exp = document.getElementById("inAppOrbExpanded");
      if (exp && exp.style.display === "none") {
        toggleInAppOrbCollapse();
      } else {
        toggleProfile();
      }
    }

    function initInAppDraggableOrb() {
      const orb = document.getElementById("monarkInAppOrb");
      if (!orb || orb._dragReady) return;
      orb._dragReady = true;
      try {
        if (localStorage.getItem("monark_inapp_orb_collapsed") === "1") {
          const exp = document.getElementById("inAppOrbExpanded");
          if (exp) exp.style.display = "none";
          orb.style.opacity = "0.78";
        }
        const saved = JSON.parse(localStorage.getItem("monark_inapp_orb_pos_v1") || "null");
        if (saved && typeof saved.left === "number" && typeof saved.top === "number") {
          orb.style.right = "auto";
          orb.style.bottom = "auto";
          orb.style.left = `${Math.min(Math.max(6, saved.left), window.innerWidth - 56)}px`;
          orb.style.top = `${Math.min(Math.max(54, saved.top), window.innerHeight - 56)}px`;
        }
      } catch (e) {}

      let dragging = false, sx = 0, sy = 0, ol = 0, ot = 0;
      const start = (cx, cy) => {
        const r = orb.getBoundingClientRect();
        dragging = true;
        window._inAppOrbDragged = false;
        sx = cx; sy = cy; ol = r.left; ot = r.top;
      };
      const move = (cx, cy, ev) => {
        if (!dragging) return;
        const dx = cx - sx, dy = cy - sy;
        if (!window._inAppOrbDragged && Math.hypot(dx, dy) > 6) {
          window._inAppOrbDragged = true;
        }
        if (window._inAppOrbDragged) {
          if (ev && ev.cancelable) ev.preventDefault();
          const r = orb.getBoundingClientRect();
          const nl = Math.min(Math.max(6, ol + dx), window.innerWidth - (r.width || 52) - 6);
          const nt = Math.min(Math.max(52, ot + dy), window.innerHeight - (r.height || 38) - 6);
          orb.style.right = "auto";
          orb.style.bottom = "auto";
          orb.style.left = `${Math.round(nl)}px`;
          orb.style.top = `${Math.round(nt)}px`;
        }
      };
      const end = () => {
        if (!dragging) return;
        dragging = false;
        if (window._inAppOrbDragged) {
          const r = orb.getBoundingClientRect();
          try {
            localStorage.setItem("monark_inapp_orb_pos_v1", JSON.stringify({ left: Math.round(r.left), top: Math.round(r.top) }));
          } catch (e) {}
          setTimeout(() => { window._inAppOrbDragged = false; }, 160);
        }
      };
      orb.addEventListener("touchstart", e => { if (e.touches.length === 1) start(e.touches[0].clientX, e.touches[0].clientY); }, { passive: true });
      window.addEventListener("touchmove", e => { if (dragging && e.touches.length === 1) move(e.touches[0].clientX, e.touches[0].clientY, e); }, { passive: false });
      window.addEventListener("touchend", end);
      orb.addEventListener("mousedown", e => start(e.clientX, e.clientY));
      window.addEventListener("mousemove", e => { if (dragging) move(e.clientX, e.clientY, e); });
      window.addEventListener("mouseup", end);
    }
    setTimeout(initInAppDraggableOrb, 80);

    const CATEGORY_META = {
      "Housing & Rent": { icon: "◈", color: "#F59E0B", group: "Housing", target: 8338.33, bucket: "Fixed", rollover: false, desc: "$5,420 Henry Hall + $2,918.33 Bilt 311" },
      "Apparel & Luxury Shopping": { icon: "✦", color: "#7C3AED", group: "Shopping", target: 1500.00, bucket: "Flexible", rollover: true, desc: "Aritzia, Alo Yoga, Saks, Bvlgari, Sephora" },
      "Travel, Flights & Hotels": { icon: "△", color: "#9333EA", group: "Travel & Lifestyle", target: 1200.00, bucket: "Non-Monthly", rollover: true, desc: "Delta Air Lines, Booking.com, Trivago, Tokyo" },
      "Food Delivery & Dining": { icon: "◉", color: "#EF4444", group: "Food & Dining", target: 1400.00, bucket: "Flexible", rollover: true, desc: "Grubhub, NYC Restaurants & Rooftops" },
      "Electronics, Home & Retail": { icon: "▣", color: "#6366F1", group: "Shopping", target: 600.00, bucket: "Non-Monthly", rollover: true, desc: "B&H Photo, Amazon, Dyson SoHo" },
      "Utilities & Insurance": { icon: "⬡", color: "#2563EB", group: "Bills & Utilities", target: 580.00, bucket: "Fixed", rollover: false, desc: "Con Edison NY, Verizon, Geico Auto" },
      "Medical, Vet & Aesthetics": { icon: "⊕", color: "#DB2777", group: "Financial & Health", target: 600.00, bucket: "Non-Monthly", rollover: true, desc: "Heart of Chelsea Vet, Dr. Schick, Sisu Clinic" },
      "Family Support, Zelle & Cash": { icon: "⇄", color: "#DB2777", group: "Financial & Health", target: 800.00, bucket: "Non-Monthly", rollover: true, desc: "FX Wires to Mexico, Zelle, ATM" },
      "Rideshare & Transit": { icon: "◇", color: "#0284C7", group: "Auto & Transport", target: 550.00, bucket: "Flexible", rollover: true, desc: "Uber Rides, MTA NYCT Paygo, E-ZPass" },
      "Fitness & Wellness": { icon: "❖", color: "#10B981", group: "Travel & Lifestyle", target: 500.00, bucket: "Flexible", rollover: true, desc: "Victory Boxing Club, Sui Yoga, Pilates" },
      "Groceries & Daily Essentials": { icon: "◎", color: "#EF4444", group: "Food & Dining", target: 650.00, bucket: "Flexible", rollover: true, desc: "Whole Foods Market, Nutrition Solutions, Duane Reade" },
      "Subscriptions & Digital": { icon: "▫", color: "#2563EB", group: "Bills & Utilities", target: 165.00, bucket: "Fixed", rollover: false, desc: "Apple, YouTube Premium, Microsoft, SimpleFIN" },
      "Paychecks & Salary": { icon: "▲", color: "#16A34A", group: "Income", target: 0, bucket: "Income", rollover: false, desc: "Google LLC Bi-Weekly Payroll" },
      "Equity & Investment Inflows": { icon: "◆", color: "#0284C7", group: "Income", target: 0, bucket: "Income", rollover: false, desc: "Morgan Stanley GSU Releases" },
      "Interest & Dividends": { icon: "◈", color: "#0891B2", group: "Income", target: 0, bucket: "Income", rollover: false, desc: "SoFi HYSA Interest & Vanguard Dividends" },
      "Credit Card Payment & Transfers": { icon: "⇄", color: "#9CA3AF", group: "Transfer", target: 0, bucket: "Transfer", rollover: false, desc: "Internal Autopays & Vault Transfers" },
      "Security Deposit & Transfers": { icon: "▣", color: "#9CA3AF", group: "Transfer", target: 0, bucket: "Transfer", rollover: false, desc: "Refundable Security Deposit Escrow" }
    };

    function getCatMeta(cat) {
      return CATEGORY_META[cat] || { icon: "◈", color: "#7C3AED", group: "Shopping", target: 500, bucket: "Flexible", rollover: true, desc: cat };
    }

    // =========================================================================
    // OFFICIAL COMPANY LOGOS (REAL FAVICON + VECTOR BRAND LOGOS FOR EVERY ROW)
    // =========================================================================
    const MERCHANT_DOMAIN_MAP = [
      { match: "alo", domain: "aloyoga.com", bg: "#000000", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#000"/><text x="16" y="18" text-anchor="middle" fill="#fff" font-size="10.5" font-weight="800" font-family="sans-serif" letter-spacing="-0.5">alo</text><text x="16" y="24" text-anchor="middle" fill="#a1a1aa" font-size="4.2" font-weight="600" font-family="sans-serif" letter-spacing="0.6">YOGA</text></svg>` },
      { match: "amazon", domain: "amazon.com", bg: "#131921", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#131921"/><text x="16" y="17" text-anchor="middle" fill="#fff" font-size="6.2" font-weight="700" font-family="sans-serif">amazon</text><path d="M9 20.5 Q16 24.5 23 20" stroke="#FF9900" stroke-width="1.8" fill="none" stroke-linecap="round"/><path d="M21.5 19.5 L23.3 20 L22.4 21.8" stroke="#FF9900" stroke-width="1.5" fill="none" stroke-linecap="round"/></svg>` },
      { match: "amzn", domain: "amazon.com", bg: "#131921", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#131921"/><text x="16" y="17" text-anchor="middle" fill="#fff" font-size="6.2" font-weight="700" font-family="sans-serif">amazon</text><path d="M9 20.5 Q16 24.5 23 20" stroke="#FF9900" stroke-width="1.8" fill="none" stroke-linecap="round"/></svg>` },
      { match: "zelle", domain: "zellepay.com", bg: "#7414CA", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#7414CA"/><line x1="16" y1="6.5" x2="16" y2="25.5" stroke="#fff" stroke-width="2.2" stroke-linecap="round"/><path d="M11.5 11.5 H20.5 L11.5 20.5 H20.5" stroke="#fff" stroke-width="2.4" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>` },
      { match: "delta", domain: "delta.com", bg: "#003366", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#003366"/><polygon points="16,6 25,22 16,18.5" fill="#E31837"/><polygon points="16,6 7,22 16,18.5" fill="#C8102E"/><polygon points="7,23.5 16,20.5 25,23.5" fill="#ffffff"/></svg>` },
      { match: "aritzia", domain: "aritzia.com", bg: "#111111", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#111111"/><text x="16" y="18.5" text-anchor="middle" fill="#fff" font-size="5.6" font-weight="700" font-family="Georgia,serif" letter-spacing="0.9">ARITZIA</text></svg>` },
      { match: "uber", domain: "uber.com", bg: "#000000", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#000000"/><text x="16" y="19.5" text-anchor="middle" fill="#fff" font-size="9.5" font-weight="700" font-family="sans-serif" letter-spacing="-0.3">Uber</text></svg>` },
      { match: "grubhub", domain: "grubhub.com", bg: "#F63440", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#F63440"/><text x="16" y="19" text-anchor="middle" fill="#fff" font-size="6.2" font-weight="900" font-family="sans-serif" letter-spacing="-0.2">GRUBHUB</text></svg>` },
      { match: "booking", domain: "booking.com", bg: "#003580", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#003580"/><text x="15" y="21" text-anchor="middle" fill="#fff" font-size="15" font-weight="900" font-family="sans-serif">B</text><circle cx="22.5" cy="19.5" r="2" fill="#009FE3"/></svg>` },
      { match: "trivago", domain: "trivago.com", bg: "#007FAF", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#fff" stroke="#e5e7eb"/><text x="11" y="19" text-anchor="middle" fill="#007FAF" font-size="7.5" font-weight="900">tri</text><text x="21" y="19" text-anchor="middle" fill="#F48F00" font-size="7.5" font-weight="900">va</text></svg>` },
      { match: "whole foods", domain: "wholefoodsmarket.com", bg: "#00674B", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#00674B"/><text x="16" y="17" text-anchor="middle" fill="#fff" font-size="5.5" font-weight="800">WHOLE</text><text x="16" y="23" text-anchor="middle" fill="#A7F3D0" font-size="5.2" font-weight="700">FOODS</text></svg>` },
      { match: "saks", domain: "saksfifthavenue.com", bg: "#000000", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#000"/><text x="16" y="19.5" text-anchor="middle" fill="#fff" font-size="8.5" font-style="italic" font-weight="700" font-family="Georgia,serif">Saks</text></svg>` },
      { match: "sephora", domain: "sephora.com", bg: "#000000", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#000"/><path d="M16 7 C13 11, 19 15, 16 25" stroke="#fff" stroke-width="2.4" fill="none" stroke-linecap="round"/></svg>` },
      { match: "bvlgari", domain: "bulgari.com", bg: "#18181B", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#18181B"/><text x="16" y="18.5" text-anchor="middle" fill="#FDE68A" font-size="5.5" font-weight="700" font-family="Georgia,serif" letter-spacing="0.8">BVLGARI</text></svg>` },
      { match: "dyson", domain: "dyson.com", bg: "#18181B", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#18181B"/><text x="16" y="19" text-anchor="middle" fill="#fff" font-size="7.8" font-weight="800" font-family="sans-serif">dyson</text></svg>` },
      { match: "b&h", domain: "bhphotovideo.com", bg: "#B91C1C", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#B91C1C"/><text x="16" y="19.5" text-anchor="middle" fill="#fff" font-size="9" font-weight="900">B&amp;H</text></svg>` },
      { match: "skims", domain: "skims.com", bg: "#785C4A", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#785C4A"/><text x="16" y="18.5" text-anchor="middle" fill="#fff" font-size="6.8" font-weight="800" letter-spacing="0.6">SKIMS</text></svg>` },
      { match: "nike", domain: "nike.com", bg: "#111111", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#111"/><path d="M9 17.5 c-1 2.2 1 3.8 4 2.5 l11-5.5 c-5 1.5-10 3-13 2 c-1-0.4-1.5-1-2 1z" fill="#fff"/></svg>` },
      { match: "bloomingdale", domain: "bloomingdales.com", bg: "#18181B", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#18181B"/><text x="16" y="21" text-anchor="middle" fill="#fff" font-size="14" font-weight="800" font-family="Georgia,serif">b</text></svg>` },
      { match: "henry hall", domain: "henryhallnyc.com", bg: "#B45309", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#B45309"/><text x="16" y="19.5" text-anchor="middle" fill="#fff" font-size="9.5" font-weight="800" font-family="Georgia,serif">HH</text></svg>` },
      { match: "bilt", domain: "biltrewards.com", bg: "#09090B", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#09090B"/><text x="16" y="19" text-anchor="middle" fill="#fff" font-size="7.5" font-weight="900" letter-spacing="1.2">BILT</text></svg>` },
      { match: "google", domain: "google.com", bg: "#ffffff", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#fff"/><path d="M23.6 16.2c0-.6-.1-1.1-.2-1.6H16v3.1h4.3c-.2 1-.8 1.9-1.6 2.4v2h2.6c1.5-1.4 2.3-3.5 2.3-5.9z" fill="#4285F4"/><path d="M16 24c2.2 0 4-.7 5.3-1.9l-2.6-2c-.7.5-1.6.8-2.7.8-2.1 0-3.8-1.4-4.5-3.3H8.8v2.1C10.1 22.3 12.9 24 16 24z" fill="#34A853"/><path d="M11.5 17.6c-.2-.5-.3-1-.3-1.6s.1-1.1.3-1.6v-2.1H8.8C8.3 13.4 8 14.7 8 16s.3 2.6.8 3.7l2.7-2.1z" fill="#FBBC05"/><path d="M16 11.1c1.2 0 2.2.4 3.1 1.2l2.3-2.3C20 8.7 18.2 8 16 8c-3.1 0-5.9 1.7-7.2 4.3l2.7 2.1c.7-1.9 2.4-3.3 4.5-3.3z" fill="#EA4335"/></svg>` },
      { match: "morgan stanley", domain: "morganstanley.com", bg: "#002F6C", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#002F6C"/><text x="16" y="19.5" text-anchor="middle" fill="#fff" font-size="9.5" font-weight="800">MS</text></svg>` },
      { match: "con ed", domain: "coned.com", bg: "#0072CE", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#0072CE"/><text x="16" y="19" text-anchor="middle" fill="#fff" font-size="6.8" font-weight="800">conEd</text></svg>` },
      { match: "verizon", domain: "verizon.com", bg: "#000000", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#000"/><path d="M10 16 l4 6 l8-12" stroke="#CD040B" stroke-width="2.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>` },
      { match: "geico", domain: "geico.com", bg: "#004B87", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#004B87"/><text x="16" y="19" text-anchor="middle" fill="#fff" font-size="6.8" font-weight="900">GEICO</text></svg>` },
      { match: "apple", domain: "apple.com", bg: "#111111", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#111"/><text x="16" y="20" text-anchor="middle" fill="#fff" font-size="11" font-weight="700"></text><circle cx="16" cy="16.5" r="5" fill="#fff"/><circle cx="19.5" cy="15.5" r="2.2" fill="#111"/><ellipse cx="16.8" cy="10" rx="1.2" ry="2.2" transform="rotate(25 16.8 10)" fill="#fff"/></svg>` },
      { match: "youtube", domain: "youtube.com", bg: "#FF0000", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#FF0000"/><polygon points="13,11 22,16 13,21" fill="#fff"/></svg>` },
      { match: "mta", domain: "mta.info", bg: "#0039A6", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#0039A6"/><text x="16" y="19.5" text-anchor="middle" fill="#fff" font-size="8.5" font-weight="900">MTA</text></svg>` },
      { match: "nvidia", domain: "nvidia.com", bg: "#76B900", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#76B900"/><text x="16" y="19.5" text-anchor="middle" fill="#000" font-size="7.2" font-weight="900">NVDA</text></svg>` },
      { match: "oracle", domain: "oracle.com", bg: "#C74634", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#C74634"/><rect x="7.5" y="11.5" width="17" height="9" rx="4.5" fill="none" stroke="#fff" stroke-width="2.4"/></svg>` },
      { match: "brioni", domain: "brioni.com", bg: "#18181B", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#18181B"/><text x="16" y="19.5" text-anchor="middle" fill="#FDE68A" font-size="7.5" font-style="italic" font-weight="700" font-family="Georgia,serif">Brioni</text></svg>` },
      { match: "gulfstream", domain: "gulfstream.com", bg: "#0F172A", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#0F172A"/><text x="16" y="19.5" text-anchor="middle" fill="#38BDF8" font-size="7.2" font-weight="900">G700</text></svg>` },
      { match: "aws", domain: "aws.amazon.com", bg: "#232F3E", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#232F3E"/><text x="16" y="18.5" text-anchor="middle" fill="#FF9900" font-size="8.2" font-weight="900">AWS</text></svg>` },
      { match: "nobu", domain: "noburestaurants.com", bg: "#111111", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#111"/><text x="16" y="19.5" text-anchor="middle" fill="#fff" font-size="7.5" font-weight="800" letter-spacing="0.8">NOBU</text></svg>` },
      { match: "deloitte", domain: "deloitte.com", bg: "#000000", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#000"/><text x="14" y="20" text-anchor="middle" fill="#fff" font-size="13" font-weight="900">D</text><circle cx="21.5" cy="18.5" r="2.2" fill="#86BC25"/></svg>` },
      { match: "gartner", domain: "gartner.com", bg: "#002856", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#002856"/><text x="16" y="19.5" text-anchor="middle" fill="#fff" font-size="6.2" font-weight="800">GARTNER</text></svg>` },
      { match: "erewhon", domain: "erewhon.com", bg: "#14532D", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#14532D"/><text x="16" y="19" text-anchor="middle" fill="#fff" font-size="5.3" font-weight="800" letter-spacing="0.5">EREWHON</text></svg>` },
      { match: "atherton", domain: "google.com", bg: "#4C1D95", svg: `<svg viewBox="0 0 32 32" class="w-7 h-7"><circle cx="16" cy="16" r="16" fill="#4C1D95"/><text x="16" y="19.5" text-anchor="middle" fill="#fff" font-size="7.2" font-weight="800">94027</text></svg>` }
    ];

    function getMerchantBrandAvatar(merchant, category, institution) {
      const m = (merchant || "").toLowerCase();
      for (const item of MERCHANT_DOMAIN_MAP) {
        if (m.includes(item.match)) {
          // Render our bespoke high-contrast vector brand mark + try loading official 128px favicon cleanly
          return `<span class="company-logo-circle" title="${merchant}">${item.svg}</span>`;
        }
      }
      if (m.includes("amex") || m.includes("american express")) {
        return getBankLogoBadge("amex", "w-7 h-7");
      }
      if (m.includes("bofa") || m.includes("bank of america")) {
        return getBankLogoBadge("bofa", "w-7 h-7");
      }
      if (m.includes("sofi")) {
        return getBankLogoBadge("sofi", "w-7 h-7");
      }
      const meta = getCatMeta(category);
      const initials = (merchant || "TX").replace(/[^A-Za-z0-9 ]/g, "").trim().split(/\s+/).slice(0, 2).map(w => w[0] || "").join("").toUpperCase() || "M";
      return `<span class="company-logo-circle text-white font-bold text-[10px]" style="background:${meta.color};">${initials}</span>`;
    }

    // Exact Circular Bank Brand Logos matching Screenshot 3 (`AM EX` stacked in blue circle, `Bank of America` flag circle, `SoFi` cyan circle)
    function getBankLogoBadge(inst, sizeCls = "w-8 h-8") {
      if (inst === "amex") {
        // Exact Stacked "AM / EX" Blue Circle Logo from Monarch Screenshot 3 (`media_1791834590404_795a91a8.png`)
        return `
          <span class="${sizeCls} rounded-full flex items-center justify-center flex-shrink-0 overflow-hidden shadow-sm" style="background:#006FCF;">
            <svg viewBox="0 0 36 36" class="w-full h-full">
              <circle cx="18" cy="18" r="18" fill="#006FCF"/>
              <text x="18" y="16.5" text-anchor="middle" fill="#FFFFFF" font-size="9.5" font-weight="900" font-family="sans-serif" letter-spacing="-0.4">AM</text>
              <text x="18" y="25.5" text-anchor="middle" fill="#FFFFFF" font-size="9.5" font-weight="900" font-family="sans-serif" letter-spacing="-0.4">EX</text>
            </svg>
          </span>
        `;
      }
      if (inst === "bofa") {
        // Authentic Bank of America Red & Navy Flag Circle Logo
        return `
          <span class="${sizeCls} rounded-full flex items-center justify-center flex-shrink-0 overflow-hidden shadow-sm" style="background:#012169;">
            <svg viewBox="0 0 36 36" class="w-full h-full">
              <circle cx="18" cy="18" r="18" fill="#012169"/>
              <path d="M8 14 L17 11 L17 14 L8 17 Z" fill="#0073CF"/>
              <path d="M8 19 L17 16 L17 19 L8 22 Z" fill="#0073CF"/>
              <path d="M19 11 L28 14 L28 17 L19 14 Z" fill="#E31837"/>
              <path d="M19 16 L28 19 L28 22 L19 19 Z" fill="#E31837"/>
              <path d="M13 24 L25 20 L25 23 L13 27 Z" fill="#E31837"/>
            </svg>
          </span>
        `;
      }
      // Authentic SoFi Cyan Circle Logo with 3 Gems + SoFi text
      return `
        <span class="${sizeCls} rounded-full flex items-center justify-center flex-shrink-0 overflow-hidden shadow-sm" style="background:#00A4E4;">
          <svg viewBox="0 0 36 36" class="w-full h-full">
            <circle cx="18" cy="18" r="18" fill="#00A4E4"/>
            <text x="18" y="21.5" text-anchor="middle" fill="#FFFFFF" font-size="10" font-weight="900" font-family="sans-serif" letter-spacing="-0.3">SoFi</text>
          </svg>
        </span>
      `;
    }

    function fmt(n, showSign = false) {
      const val = Number(n || 0);
      const absStr = "$" + Math.abs(val).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
      if (val < -0.005) return "-" + absStr;
      if (showSign && val > 0.005) return "+" + absStr;
      return absStr;
    }

    function fmtInt(n) {
      const val = Number(n || 0);
      return (val < 0 ? "-$" : "$") + Math.round(Math.abs(val)).toLocaleString("en-US");
    }

    function fmtShort(n) {
      const v = Math.abs(Number(n || 0));
      if (v >= 1000000) return "$" + (v / 1000000).toFixed(1) + "M";
      if (v >= 1000) return "$" + (v / 1000).toFixed(1) + "k";
      return "$" + v.toFixed(0);
    }

    function toggleMobileFrame() {
      mobileFrameMode = !mobileFrameMode;
      const shell = document.getElementById("appShell");
      const sb = document.getElementById("leftSidebar");
      const bnav = document.getElementById("mobileBottomNav");
      const island = document.getElementById("iosDynamicIslandBar");
      const btnText = document.getElementById("mobileFrameText");

      if (mobileFrameMode) {
        shell.classList.add("mobile-frame-active");
        sb.classList.remove("md:flex");
        bnav.classList.remove("md:hidden");
        bnav.style.position = "sticky";
        island.classList.remove("hidden");
        btnText.textContent = "Desktop";
      } else {
        shell.classList.remove("mobile-frame-active");
        sb.classList.add("md:flex");
        bnav.classList.add("md:hidden");
        bnav.style.position = "fixed";
        island.classList.add("hidden");
        btnText.textContent = "Mobile";
      }
      renderAll();
    }

    function openMobileSidebar() {
      const sb = document.getElementById("leftSidebar");
      const bd = document.getElementById("mobileMenuBackdrop");
      if (sb) {
        sb.classList.remove("hidden");
        sb.classList.add("flex", "fixed", "inset-y-0", "left-0", "z-50", "shadow-2xl");
      }
      if (bd) bd.classList.remove("hidden");
    }

    function closeMobileSidebar() {
      const sb = document.getElementById("leftSidebar");
      const bd = document.getElementById("mobileMenuBackdrop");
      if (sb && !mobileFrameMode) {
        sb.classList.add("hidden");
        sb.classList.remove("flex", "fixed", "inset-y-0", "left-0", "z-50", "shadow-2xl");
      }
      if (bd) bd.classList.add("hidden");
    }

    function openMobileInstallModal() {
      document.getElementById("mobileInstallModal").classList.remove("hidden");
    }
    function closeMobileInstallModal() {
      document.getElementById("mobileInstallModal").classList.add("hidden");
    }

    function inSelectedWindow(t) {
      if (bankScope !== "ALL" && t.institution !== bankScope) return false;
      if (globalWindow === "ALL") return true;
      if (globalWindow === "60D") return t.date >= "2026-08-18" && t.date <= "2026-10-12";
      return t.period === globalWindow;
    }

    function getWindowLabel() {
      if (globalWindow === "2026-09") return "Sep 1, 2026 - Sep 30, 2026";
      if (globalWindow === "2026-10") return "Oct 1, 2026 - Oct 12, 2026";
      if (globalWindow === "60D") return "Aug 18, 2026 - Oct 12, 2026";
      if (globalWindow === "2026-08") return "Aug 1, 2026 - Aug 31, 2026";
      return "Jul 14, 2026 - Oct 12, 2026";
    }

    function getShortWindowTitle() {
      if (globalWindow === "2026-09") return "Sep 2026";
      if (globalWindow === "2026-10") return "Oct 2026";
      if (globalWindow === "60D") return "60-Day Window";
      if (globalWindow === "2026-08") return "Aug 2026";
      return "90-Day (Jul–Oct)";
    }

    const WINDOW_ORDER = ["2026-08", "2026-09", "2026-10", "60D", "ALL"];

    function stepGlobalWindow(delta) {
      const idx = WINDOW_ORDER.indexOf(globalWindow);
      const nextIdx = (idx + delta + WINDOW_ORDER.length) % WINDOW_ORDER.length;
      setGlobalWindow(WINDOW_ORDER[nextIdx]);
    }

    function renderInlineWindowSelector(selectId = "") {
      return `
        <div class="inline-flex items-center gap-1 rounded-lg p-0.5" style="background: var(--bg-elevated); border: 1px solid var(--border-subtle);">
          <button onclick="event.stopPropagation();stepGlobalWindow(-1)" class="px-2 py-1 rounded-md text-xs font-bold cursor-pointer hover:opacity-80" title="Previous Month / Period">◄</button>
          <select ${selectId ? `id="${selectId}"` : ""} onchange="setGlobalWindow(this.value)" class="px-2 py-1 text-xs font-semibold cursor-pointer border-0" style="background: var(--bg-surface);">
            <option value="2026-08" ${globalWindow === "2026-08" ? "selected" : ""}>August 2026 (Aug 1–31)</option>
            <option value="2026-09" ${globalWindow === "2026-09" ? "selected" : ""}>September 2026 (Sep 1–30)</option>
            <option value="2026-10" ${globalWindow === "2026-10" ? "selected" : ""}>October 2026 (Oct 1–12)</option>
            <option value="60D" ${globalWindow === "60D" ? "selected" : ""}>60-Day Window (Aug 18–Oct 12)</option>
            <option value="ALL" ${globalWindow === "ALL" ? "selected" : ""}>All 90 Days (Jul 14–Oct 12)</option>
          </select>
          <button onclick="event.stopPropagation();stepGlobalWindow(1)" class="px-2 py-1 rounded-md text-xs font-bold cursor-pointer hover:opacity-80" title="Next Month / Period">►</button>
        </div>
      `;
    }

    function setNwRange(r) {
      nwRange = r;
      renderDashboard();
      renderAccountsView();
    }

    function setAcctChartMetric(m) {
      acctChartMetric = m;
      renderAccountsView();
    }

    function setSpendCompareMode(mode) {
      spendCompareMode = mode;
      renderDashboard();
    }

    function setCashFlowBreakdown(mode) {
      cashFlowBreakdown = mode;
      renderCashFlowView();
    }

    function toggleAcctGroup(grpKey) {
      collapsedAcctGroups[grpKey] = !collapsedAcctGroups[grpKey];
      renderAccountsView();
    }

    function toggleBudgetGroup(grpKey) {
      collapsedBudgetGroups[grpKey] = !collapsedBudgetGroups[grpKey];
      renderBudgetView();
    }

    function toggleTxnDateGroup(dateStr) {
      collapsedTxnDates[dateStr] = !collapsedTxnDates[dateStr];
      renderTransactionsTable();
    }

    function jumpToTxnType(typeVal) {
      switchTab("transactions");
      const sel = document.getElementById("txnTypeFilter");
      if (sel) sel.value = typeVal;
      renderTransactionsTable();
    }

    function setBankScope(scope) {
      bankScope = scope;
      const gSel = document.getElementById("globalBankScope");
      if (gSel && gSel.value !== scope) gSel.value = scope;
      renderAll();
    }

    function setGlobalWindow(w) {
      globalWindow = w;
      ["2026-09", "2026-10", "60D", "2026-08", "ALL"].forEach(k => {
        const el = document.getElementById("win-" + k);
        if (el) el.className = "pill-btn border-0 py-1 px-1.5 text-[11px]" + (k === w ? " active" : "");
      });
      const tSel = document.getElementById("txnWindowSelect");
      if (tSel && tSel.value !== w) tSel.value = w;
      renderAll();
    }

    function toggleRefundMode() {
      refundStrippedMode = !refundStrippedMode;
      const btn = document.getElementById("refundModeBtn");
      const badge = document.getElementById("refundModeBadge");
      if (refundStrippedMode) {
        btn.className = "pill-amethyst text-xs";
        badge.textContent = "✓ Net Spend";
      } else {
        btn.className = "pill-btn text-xs";
        badge.textContent = "○ Gross Swipes";
      }
      renderAll();
    }

    function switchTab(tabId) {
      activeTab = tabId;
      closeMobileSidebar();
      const tabs = ["dashboard", "accounts", "transactions", "cashflow", "reports", "budget", "recurring", "goals", "investments", "advisor"];
      tabs.forEach(id => {
        const nav = document.getElementById("tab-" + id);
        const mnav = document.getElementById("mtab-" + id);
        const view = document.getElementById("view-" + id);
        if (nav) nav.className = "sidebar-item" + (id === tabId ? " active" : "");
        if (mnav) mnav.style.color = id === tabId ? "var(--amethyst)" : "var(--text-secondary)";
        if (view) view.className = id === tabId ? "space-y-4 max-w-6xl mx-auto" : "hidden space-y-4 max-w-6xl mx-auto";
      });
      const moreBtn = document.getElementById("mtab-more");
      if (moreBtn) {
        const isExtra = ["reports", "recurring", "goals", "investments", "advisor"].includes(tabId);
        moreBtn.style.color = isExtra ? "var(--amethyst)" : "var(--text-secondary)";
      }
      const titles = {
        dashboard: "Dashboard",
        accounts: "Accounts",
        transactions: "Transactions",
        cashflow: "Reports",
        reports: "Reports",
        budget: "Budget",
        recurring: "Recurring",
        goals: "Goals",
        investments: "Investments",
        advisor: "Advice"
      };
      document.getElementById("pageHeaderTitle").textContent = titles[tabId] || "Monark";
      const subTabs = document.getElementById("headerSubTabs");
      if (subTabs) {
        if (tabId === "cashflow" || tabId === "reports") {
          subTabs.classList.remove("hidden");
          subTabs.classList.add("flex");
          document.getElementById("subtab-cashflow").className = "subtab-link" + (tabId === "cashflow" ? " active" : "");
          document.getElementById("subtab-spending").className = "subtab-link" + (tabId === "reports" ? " active" : "");
        } else {
          subTabs.classList.add("hidden");
          subTabs.classList.remove("flex");
        }
      }
      renderAll();
    }

    function computeWindowMetrics() {
      const txns = state.transactions.filter(inSelectedWindow);
      let grossExpense = 0, netExpense = 0, strippedRefunds = 0;
      let payrollIncome = 0, equityIncome = 0, otherIncome = 0;
      const byCategory = {};
      const byBucket = { Fixed: 0, Flexible: 0, "Non-Monthly": 0 };
      const byInstitution = { amex: 0, bofa: 0, sofi: 0 };

      txns.forEach(t => {
        if (t.txn_type === "expense") {
          const gross = Number(t.amount);
          const net = Number(t.net_amount);
          const eff = refundStrippedMode ? net : gross;
          grossExpense += gross;
          netExpense += net;
          if (!byCategory[t.category]) {
            byCategory[t.category] = { gross: 0, net: 0, eff: 0, count: 0, bucket: t.flex_bucket };
          }
          byCategory[t.category].gross += gross;
          byCategory[t.category].net += net;
          byCategory[t.category].eff += eff;
          if (eff > 0.005) byCategory[t.category].count += 1;
          if (byBucket[t.flex_bucket] !== undefined) byBucket[t.flex_bucket] += eff;
          if (byInstitution[t.institution] !== undefined) byInstitution[t.institution] += eff;
        } else if (t.txn_type === "refund") {
          strippedRefunds += Number(t.amount);
        } else if (t.txn_type === "income") {
          if (t.category === "Paychecks & Salary") payrollIncome += Number(t.amount);
          else if (t.category === "Equity & Investment Inflows") equityIncome += Number(t.amount);
          else otherIncome += Number(t.amount);
        }
      });

      const activeExpense = refundStrippedMode ? netExpense : grossExpense;
      const totalIncome = payrollIncome + equityIncome + otherIncome;
      const netCashFlow = totalIncome - activeExpense;
      const savingsRate = totalIncome > 0 ? ((netCashFlow / totalIncome) * 100) : 0;

      return {
        txns, grossExpense, netExpense, activeExpense,
        strippedAmount: Math.max(0, grossExpense - netExpense),
        strippedRefunds, payrollIncome, equityIncome, otherIncome,
        totalIncome, netCashFlow, savingsRate, byCategory, byBucket, byInstitution
      };
    }

    // =========================================================================
    // 01. DASHBOARD — EXACT ROB BERGER SPENDING CHART & 4-COL TRANSACTIONS CARD
    // =========================================================================
    function getNwRangeMeta(isTK, s) {
      const map = {
        "1M": {
          label: "1 month",
          delta: isTK ? "↑ $42,690,000.00 (10.9%)" : "↑ $4,120.40 (14.1%)",
          path: "M 10 122 L 55 108 L 95 104 L 140 88 L 185 93 L 230 76 L 275 72 L 320 55 L 365 61 L 415 39 L 465 26 L 510 22",
          acctPath: "M 65 144 L 115 142 L 165 126 L 215 124 L 265 121 L 315 108 L 365 104 L 415 92 L 465 90 L 515 79 L 565 81 L 615 65 L 665 59 L 715 49 L 765 39 L 815 24 L 855 27",
          ticks: ["Sep 12", "Sep 16", "Sep 20", "Sep 24", "Sep 28", "Oct 2", "Oct 6", "Oct 10", "Oct 12"]
        },
        "3M": {
          label: "3 months",
          delta: isTK ? "↑ $98,420,000.00 (29.4%)" : "↑ $11,840.75 (55.3%)",
          path: "M 10 130 L 55 124 L 95 112 L 140 105 L 185 92 L 230 85 L 275 68 L 320 64 L 365 48 L 415 36 L 465 28 L 510 18",
          acctPath: "M 65 146 L 165 138 L 265 122 L 365 110 L 465 94 L 565 76 L 665 58 L 765 36 L 855 22",
          ticks: ["Jul 15", "Jul 28", "Aug 9", "Aug 21", "Sep 2", "Sep 14", "Sep 26", "Oct 5", "Oct 12"]
        },
        "6M": {
          label: "6 months",
          delta: isTK ? "↑ $164,800,000.00 (61.4%)" : "↑ $18,920.12 (131.9%)",
          path: "M 10 132 L 55 128 L 95 119 L 140 110 L 185 98 L 230 82 L 275 74 L 320 58 L 365 49 L 415 34 L 465 24 L 510 16",
          acctPath: "M 65 147 L 165 140 L 265 129 L 365 115 L 465 96 L 565 74 L 665 52 L 765 32 L 855 20",
          ticks: ["Apr", "May", "Jun", "Jul", "Aug", "Sep 1", "Sep 15", "Oct 1", "Oct 12"]
        },
        "1Y": {
          label: "1 year",
          delta: isTK ? "↑ $248,500,000.00 (134.5%)" : "↑ $26,410.80 (385.9%)",
          path: "M 10 134 L 55 131 L 95 125 L 140 116 L 185 104 L 230 91 L 275 76 L 320 62 L 365 46 L 415 32 L 465 22 L 510 15",
          acctPath: "M 65 148 L 165 143 L 265 134 L 365 121 L 465 102 L 565 81 L 665 56 L 765 34 L 855 19",
          ticks: ["Oct '25", "Dec '25", "Jan '26", "Mar '26", "Apr '26", "Jun '26", "Aug '26", "Sep '26", "Oct '26"]
        },
        "ALL": {
          label: "All time",
          delta: isTK ? "↑ $391,185,100.42 (931.4%)" : "↑ $31,254.11 (1,420.6%)",
          path: "M 10 135 L 55 133 L 95 129 L 140 121 L 185 110 L 230 96 L 275 80 L 320 64 L 365 45 L 415 30 L 465 20 L 510 14",
          acctPath: "M 65 148 L 165 145 L 265 138 L 365 126 L 465 108 L 565 84 L 665 55 L 765 30 L 855 18",
          ticks: ["2022", "2023", "Q1 '24", "Q3 '24", "Q1 '25", "Q3 '25", "Q1 '26", "Q3 '26", "Oct '26"]
        }
      };
      return map[nwRange] || map["1M"];
    }

    function renderDashboard() {
      const m = computeWindowMetrics();

      const topYVal = Math.round((m.activeExpense * 1.08) / 1000) * 1000 || 40000;
      const midYVal = Math.round(topYVal / 2);
      const negYVal = -Math.round(topYVal * 0.25);

      const cmpPaths = {
        "vs_last_month": {
          label: "Last month",
          color: "#8E8C99",
          path: "M 52 100 L 110 95 L 160 95 L 195 79 L 235 79 L 252 135 L 282 132 L 330 106 L 385 104 L 435 103 L 478 82 L 512 80"
        },
        "vs_budget": {
          label: "Target budget",
          color: "#F59E0B",
          path: "M 52 101 L 110 91 L 160 82 L 215 73 L 270 64 L 325 55 L 380 46 L 435 37 L 510 28"
        },
        "vs_avg": {
          label: "90D average",
          color: "#0284C7",
          path: "M 52 100 L 110 92 L 165 86 L 220 78 L 275 70 L 330 62 L 385 55 L 445 45 L 510 38"
        }
      };
      const cmpCfg = cmpPaths[spendCompareMode] || cmpPaths["vs_last_month"];

      document.getElementById("dashboardSpendingCard").innerHTML = `
        <div>
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div onclick="jumpToTxnType('EXPENSE_NET')" class="flex items-baseline gap-2 cursor-pointer hover:opacity-80" title="Click to inspect expenses in Transactions">
              <span class="text-[16px] font-bold">Spending</span>
              <span class="text-[14px] font-medium mono-num underline decoration-dotted" style="color: var(--text-secondary);">${fmt(m.activeExpense)} (${getShortWindowTitle()}) ›</span>
            </div>
            <div class="flex flex-wrap items-center gap-1.5">
              <select onchange="setGlobalWindow(this.value)" class="px-2.5 py-1 rounded-lg text-xs font-semibold cursor-pointer" style="background: var(--bg-surface); border: 1px solid var(--border-subtle); color: var(--text-primary);" title="Switch Month / Period">
                <option value="2026-08" ${globalWindow === "2026-08" ? "selected" : ""}>Aug 2026</option>
                <option value="2026-09" ${globalWindow === "2026-09" ? "selected" : ""}>Sep 2026</option>
                <option value="2026-10" ${globalWindow === "2026-10" ? "selected" : ""}>Oct 2026</option>
                <option value="60D" ${globalWindow === "60D" ? "selected" : ""}>60-Day Pace</option>
                <option value="ALL" ${globalWindow === "ALL" ? "selected" : ""}>90-Day All</option>
              </select>
              <select onchange="setSpendCompareMode(this.value)" class="px-2.5 py-1 rounded-lg text-xs font-medium cursor-pointer" style="background: var(--bg-surface); border: 1px solid var(--border-subtle); color: var(--text-primary);" title="Change Spending Comparison Line">
                <option value="vs_last_month" ${spendCompareMode === "vs_last_month" ? "selected" : ""}>This month vs. last month</option>
                <option value="vs_budget" ${spendCompareMode === "vs_budget" ? "selected" : ""}>This month vs. target budget</option>
                <option value="vs_avg" ${spendCompareMode === "vs_avg" ? "selected" : ""}>This month vs. 90D average</option>
              </select>
            </div>
          </div>

          <!-- Exact Rob Berger Cumulative Curve with $0 Zero-Line, Negative Dip Support, Open Circle Endpoint & Bottom Legend -->
          <div class="mt-4">
            <svg viewBox="0 0 530 195" class="w-full h-44 overflow-visible">
              <defs>
                <linearGradient id="amethystSpendFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="#8B5CF6" stop-opacity="0.38"/>
                  <stop offset="100%" stop-color="#7C3AED" stop-opacity="0.06"/>
                </linearGradient>
              </defs>

              <text x="38" y="25" text-anchor="end" font-size="10" fill="var(--text-secondary)" class="mono-num">${fmtShort(topYVal)}</text>
              <line x1="46" y1="21" x2="515" y2="21" stroke="var(--border-subtle)" />

              <text x="38" y="65" text-anchor="end" font-size="10" fill="var(--text-secondary)" class="mono-num">${fmtShort(midYVal)}</text>
              <line x1="46" y1="61" x2="515" y2="61" stroke="var(--border-subtle)" />

              <text x="38" y="105" text-anchor="end" font-size="10" fill="var(--text-secondary)" class="mono-num">$0</text>
              <line x1="46" y1="101" x2="515" y2="101" stroke="var(--border-subtle)" stroke-width="1.2" />

              <text x="38" y="143" text-anchor="end" font-size="10" fill="var(--text-secondary)" class="mono-num">-${fmtShort(Math.abs(negYVal))}</text>
              <line x1="46" y1="139" x2="515" y2="139" stroke="var(--border-subtle)" />

              <!-- Shaded Royal Amethyst Area between "This month" curve and $0 line (y=101) -->
              <path d="M 52 99 L 95 94 L 135 82 L 185 74 L 235 71 L 285 52 L 325 46 L 348 93 L 390 78 L 435 34 L 475 28 L 508 26 L 508 101 L 52 101 Z" fill="url(#amethystSpendFill)" class="cursor-pointer" onclick="jumpToTxnType('EXPENSE_NET')" />

              <!-- Solid Comparison Curve (Last month / Budget / 90D Average) -->
              <path d="${cmpCfg.path}" fill="none" stroke="${cmpCfg.color}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" />

              <!-- Solid Royal Amethyst Curve ("This month") -->
              <path d="M 52 99 L 95 94 L 135 82 L 185 74 L 235 71 L 285 52 L 325 46 L 348 93 L 390 78 L 435 34 L 475 28 L 508 26" fill="none" stroke="var(--amethyst)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />

              <!-- Endpoint Callout Label + Open Circle -->
              <text x="488" y="22" text-anchor="end" font-size="10" font-weight="700" fill="var(--amethyst)" class="mono-num">${fmtInt(m.activeExpense)}</text>
              <circle cx="508" cy="26" r="3.5" fill="var(--bg-surface)" stroke="var(--amethyst)" stroke-width="2.2" />

              <!-- X-Axis Labels (Day 3 .. Day 30 — Clickable to cycle windows) -->
              <g class="cursor-pointer" onclick="stepGlobalWindow(1)">
                <text x="72" y="162" font-size="10" fill="var(--text-secondary)">Day 3</text>
                <text x="126" y="162" font-size="10" fill="var(--text-secondary)">Day 6</text>
                <text x="180" y="162" font-size="10" fill="var(--text-secondary)">Day 9</text>
                <text x="242" y="162" font-size="10" fill="var(--text-secondary)">Day 13</text>
                <text x="306" y="162" font-size="10" fill="var(--text-secondary)">Day 17</text>
                <text x="372" y="162" font-size="10" fill="var(--text-secondary)">Day 21</text>
                <text x="436" y="162" font-size="10" fill="var(--text-secondary)">Day 25</text>
                <text x="492" y="162" font-size="10" fill="var(--text-secondary)">Day 30</text>
              </g>

              <!-- Centered Bottom Legend (Clickable to cycle comparison mode) -->
              <g class="cursor-pointer" onclick="setSpendCompareMode(spendCompareMode==='vs_last_month'?'vs_budget':(spendCompareMode==='vs_budget'?'vs_avg':'vs_last_month'))">
                <line x1="175" y1="184" x2="189" y2="184" stroke="${cmpCfg.color}" stroke-width="2.2" />
                <text x="194" y="187" font-size="10" fill="var(--text-secondary)">${cmpCfg.label}</text>
                <line x1="278" y1="184" x2="292" y2="184" stroke="var(--amethyst)" stroke-width="2.5" />
                <text x="297" y="187" font-size="10" fill="var(--text-secondary)">${getShortWindowTitle()}</text>
              </g>
            </svg>
          </div>
        </div>
      `;

      // Card 2: Net Worth Area Chart (Profile-Aware: TK vs JC, Interactive 1M/3M/6M/1Y/ALL)
      const isTK = activeProfile === "TK";
      const s = state.summary;
      const nwMeta = getNwRangeMeta(isTK, s);
      const nwDeltaText = `${nwMeta.delta} (${nwMeta.label})`;
      const nwSubText = isTK
        ? `<span onclick="setAcctChartMetric('assets');switchTab('accounts')" class="cursor-pointer hover:underline">Assets <strong class="mono-num">${fmt(s.total_assets)}</strong></span> · <span onclick="setAcctChartMetric('liabilities');switchTab('accounts')" class="cursor-pointer hover:underline">Cards <strong class="mono-num">-${fmt(s.total_liabilities)}</strong></span> · <span onclick="switchTab('goals')" class="cursor-pointer hover:underline">Unencumbered (after B200 Escrow): <strong class="mono-num" style="color: var(--amethyst);">${fmt(s.unencumbered_net_worth)}</strong></span>`
        : `<span onclick="setAcctChartMetric('assets');switchTab('accounts')" class="cursor-pointer hover:underline">Assets <strong class="mono-num">${fmt(s.total_assets)}</strong></span> · <span onclick="setAcctChartMetric('liabilities');switchTab('accounts')" class="cursor-pointer hover:underline">Cards <strong class="mono-num">-${fmt(s.total_liabilities)}</strong></span> · <span onclick="switchTab('goals')" class="cursor-pointer hover:underline">Unencumbered (after 311 lease): <strong class="mono-num" style="color: var(--amethyst);">${fmt(s.unencumbered_net_worth)}</strong></span>`;

      document.getElementById("dashboardNetWorthCard").innerHTML = `
        <div>
          <div class="flex items-center justify-between gap-2">
            <div>
              <div onclick="switchTab('accounts')" class="text-[11px] font-bold uppercase tracking-wider cursor-pointer hover:underline" style="color: var(--text-secondary);">NET WORTH ⓘ</div>
              <div class="flex items-baseline gap-2.5 mt-0.5 flex-wrap">
                <span onclick="switchTab('accounts')" class="text-xl font-bold mono-num cursor-pointer hover:opacity-80">${fmt(s.net_worth)}</span>
                <span onclick="setNwRange(nwRange==='1M'?'3M':(nwRange==='3M'?'6M':(nwRange==='6M'?'1Y':(nwRange==='1Y'?'ALL':'1M'))))" class="text-xs font-semibold mono-num cursor-pointer hover:underline" style="color: var(--monarch-green);" title="Tap to cycle timeframe">${nwDeltaText}</span>
              </div>
              <div class="text-[11px] mt-0.5" style="color: var(--text-secondary);">
                ${nwSubText}
              </div>
            </div>
            <button onclick="switchTab('accounts')" class="pill-btn text-xs">Accounts ›</button>
          </div>

          <div class="mt-3">
            <svg viewBox="0 0 520 155" class="w-full h-36 overflow-visible cursor-pointer" onclick="switchTab('accounts')">
              <defs>
                <linearGradient id="nwSkyGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="#0284c7" stop-opacity="0.26"/>
                  <stop offset="100%" stop-color="#0284c7" stop-opacity="0.0"/>
                </linearGradient>
              </defs>
              <path d="${nwMeta.path} L 510 135 L 10 135 Z" fill="url(#nwSkyGrad)" />
              <path d="${nwMeta.path}" fill="none" stroke="#0284c7" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            <div class="flex items-center justify-around pt-1 text-[11px] font-semibold" style="color: var(--text-secondary);">
              ${["1M", "3M", "6M", "1Y", "ALL"].map(rk => `
                <button onclick="setNwRange('${rk}')" class="px-2.5 py-1 rounded-md cursor-pointer transition-all" style="background: ${nwRange === rk ? "var(--amethyst)" : "transparent"}; color: ${nwRange === rk ? "#ffffff" : "var(--text-secondary)"}; border: 0; font-weight: ${nwRange === rk ? "700" : "600"};">${rk}</button>
              `).join("")}
            </div>
          </div>
        </div>
      `;

      // Card 3: Exact Rob Berger "Transactions · Most recent | [All transactions ▾]" with Real Company Logos + Gray "P" Badge + ">"
      const recentList = m.txns
        .filter(t => t.txn_type === "expense" ? (refundStrippedMode ? t.net_amount > 0.01 : t.amount > 0.01) : t.txn_type === "income")
        .slice(0, 6);

      document.getElementById("dashboardRecentTxnsCard").innerHTML = `
        <div class="flex items-center justify-between mb-3 pb-2" style="border-bottom: 1px solid var(--border-subtle);">
          <div class="flex items-baseline gap-2">
            <span class="text-[16px] font-bold">Transactions</span>
            <span class="text-xs font-medium" style="color: var(--text-secondary);">Most recent</span>
          </div>
          <button onclick="switchTab('transactions')" class="px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-2 cursor-pointer" style="background: var(--bg-surface); border: 1px solid var(--border-subtle);">
            <span>All transactions</span>
            <span style="color: var(--text-muted);">▾</span>
          </button>
        </div>

        <div class="divide-y text-[13px]" style="border-color: var(--border-subtle);">
          ${recentList.map(t => {
            const meta = getCatMeta(t.category);
            const disp = t.txn_type === "expense" ? (refundStrippedMode ? t.net_amount : t.amount) : t.amount;
            const isInc = t.txn_type === "income";
            const brandLogo = getMerchantBrandAvatar(t.merchant_clean, t.category, t.institution);
            return `
              <div onclick="openTxnModal('${t.txn_id}')" class="py-2.5 px-1 flex items-center justify-between sm:grid sm:grid-cols-12 gap-2 cursor-pointer hover:opacity-85">
                <div class="sm:col-span-5 flex items-center gap-2.5 min-w-0 flex-1">
                  ${brandLogo}
                  <div class="min-w-0">
                    <div class="font-medium truncate">${t.merchant_clean}</div>
                    <div class="sm:hidden text-[10.5px] truncate" style="color: var(--text-secondary);">${meta.icon} ${t.category}</div>
                  </div>
                </div>
                <div class="hidden sm:flex sm:col-span-4 items-center gap-1.5 min-w-0" style="color: var(--text-secondary);">
                  <span class="text-xs flex-shrink-0">${meta.icon}</span>
                  <span class="truncate text-xs">${t.category}</span>
                </div>
                <div class="sm:col-span-3 flex items-center justify-end gap-1.5 flex-shrink-0">
                  <span class="monarch-p-badge hidden sm:inline-flex" title="Personal / Posted">P</span>
                  <span class="mono-num font-semibold" style="color: ${isInc ? "var(--monarch-green)" : "var(--text-primary)"};">${isInc ? "+" : ""}${fmt(disp)}</span>
                  <span class="text-sm" style="color: var(--text-muted);">›</span>
                </div>
              </div>
            `;
          }).join("")}
        </div>
      `;

      // Card 4: Spending by Category Ring
      const sortedCats = Object.entries(m.byCategory)
        .map(([name, obj]) => ({ name, ...obj, meta: getCatMeta(name) }))
        .filter(c => c.eff > 0)
        .sort((a, b) => b.eff - a.eff);
      const top6 = sortedCats.slice(0, 6);
      let cumPct = 0;
      const radius = 50;
      const circum = 2 * Math.PI * radius;
      const segments = top6.map(c => {
        const frac = m.activeExpense > 0 ? (c.eff / m.activeExpense) : 0;
        const dash = frac * circum;
        const offset = -cumPct * circum;
        cumPct += frac;
        return `<circle cx="64" cy="64" r="${radius}" fill="transparent" stroke="${c.meta.color}" stroke-width="16" stroke-dasharray="${dash} ${circum}" stroke-dashoffset="${offset}" transform="rotate(-90 64 64)" />`;
      }).join("");

      document.getElementById("dashboardCategoriesCard").innerHTML = `
        <div class="flex items-center justify-between mb-3 pb-2" style="border-bottom: 1px solid var(--border-subtle);">
          <span class="text-[16px] font-bold">Spending by Category</span>
          <button onclick="switchTab('cashflow')" class="text-xs font-semibold cursor-pointer" style="color: var(--amethyst);">Cash Flow ›</button>
        </div>
        <div class="flex flex-col sm:flex-row items-center gap-4">
          <div class="relative w-32 h-32 flex-shrink-0 flex items-center justify-center">
            <svg viewBox="0 0 128 128" class="w-32 h-32">
              <circle cx="64" cy="64" r="${radius}" fill="transparent" stroke="var(--bg-elevated)" stroke-width="16" />
              ${segments}
            </svg>
            <div class="absolute inset-0 flex flex-col items-center justify-center text-center">
              <span class="text-[10px] font-semibold" style="color: var(--text-secondary);">Net Spend</span>
              <span class="text-xs font-bold mono-num">${fmtShort(m.activeExpense)}</span>
            </div>
          </div>
          <div class="flex-1 w-full space-y-2 text-xs">
            ${top6.map(c => {
              const share = m.activeExpense > 0 ? ((c.eff / m.activeExpense) * 100).toFixed(1) : "0.0";
              return `
                <div onclick="jumpToCategory('${c.name}')" class="flex items-center justify-between cursor-pointer hover:opacity-80">
                  <div class="flex items-center gap-2 truncate">
                    <span class="w-2.5 h-2.5 rounded-full flex-shrink-0" style="background: ${c.meta.color};"></span>
                    <span class="truncate font-medium">${c.name}</span>
                  </div>
                  <div class="mono-num flex items-center gap-2 flex-shrink-0">
                    <span style="color: var(--text-secondary);">${share}%</span>
                    <span class="font-bold">${fmtInt(c.eff)}</span>
                  </div>
                </div>
              `;
            }).join("")}
          </div>
        </div>
      `;

      // Card 5: Cash Flow Waterfall Preview Banner
      document.getElementById("dashboardCashFlowMini").innerHTML = `
        <div class="flex flex-wrap items-center justify-between gap-2 mb-3">
          <div>
            <span class="text-[16px] font-bold">Cash Flow Waterfall</span>
            <p onclick="stepGlobalWindow(1)" class="text-xs cursor-pointer hover:underline" style="color: var(--text-secondary);" title="Tap to switch period">${getWindowLabel()} ▾ · Income → Group → Category</p>
          </div>
          <button onclick="switchTab('cashflow')" class="pill-amethyst text-xs">Open Waterfall ›</button>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-center">
          <div onclick="jumpToTxnType('INCOME')" class="p-3 rounded-xl cursor-pointer hover:opacity-85" style="background: var(--bg-elevated); border: 1px solid var(--border-subtle);" title="Click to inspect Income transactions">
            <div class="text-sm font-bold mono-num" style="color: var(--monarch-green);">${fmt(m.totalIncome)}</div>
            <div class="text-[10px] font-bold uppercase tracking-wider mt-1" style="color: var(--text-secondary);">TOTAL INCOME ›</div>
          </div>
          <div onclick="jumpToTxnType('EXPENSE_NET')" class="p-3 rounded-xl cursor-pointer hover:opacity-85" style="background: var(--bg-elevated); border: 1px solid var(--border-subtle);" title="Click to inspect Expense transactions">
            <div class="text-sm font-bold mono-num" style="color: var(--monarch-rose);">${fmt(m.activeExpense)}</div>
            <div class="text-[10px] font-bold uppercase tracking-wider mt-1" style="color: var(--text-secondary);">TOTAL EXPENSES ›</div>
          </div>
          <div onclick="switchTab('budget')" class="p-3 rounded-xl cursor-pointer hover:opacity-85" style="background: var(--bg-elevated); border: 1px solid var(--border-subtle);" title="Click to inspect Budget &amp; Net Cash Flow">
            <div class="text-sm font-bold mono-num">${fmt(m.netCashFlow)}</div>
            <div class="text-[10px] font-bold uppercase tracking-wider mt-1" style="color: var(--text-secondary);">TOTAL NET INCOME ›</div>
          </div>
          <div onclick="switchTab('goals')" class="p-3 rounded-xl cursor-pointer hover:opacity-85" style="background: var(--bg-elevated); border: 1px solid var(--border-subtle);" title="Click to inspect Savings &amp; Vault Goals">
            <div class="text-sm font-bold mono-num">${m.savingsRate.toFixed(1)}%</div>
            <div class="text-[10px] font-bold uppercase tracking-wider mt-1" style="color: var(--text-secondary);">SAVINGS RATE ›</div>
          </div>
        </div>
      `;

      // Card 6: Lease / B200 GPU Vault & Connected Banks Mini (Profile-Aware: TK vs JC)
      document.getElementById("dashboardAccountsMini").innerHTML = isTK ? `
        <div class="flex items-center justify-between mb-3">
          <span class="text-[16px] font-bold">Cash &amp; B200 GPU Escrow Vault</span>
          <button onclick="switchTab('accounts')" class="text-xs font-semibold cursor-pointer" style="color: var(--amethyst);">Accounts ›</button>
        </div>
        <div class="space-y-2.5 text-xs">
          <div onclick="switchTab('goals')" class="p-3 rounded-xl flex items-center justify-between cursor-pointer" style="background: var(--bg-elevated);">
            <div class="flex items-center gap-2.5">
              ${getBankLogoBadge("sofi")}
              <div>
                <div class="font-bold">SoFi B200 GPU Escrow (2752 — Jensen Tribute)</div>
                <div class="text-[11px]" style="color: var(--monarch-green);">$42.0M locked (2,048 B200 Racks) · <strong>+$46.5M Surplus</strong></div>
              </div>
            </div>
            <span class="mono-num font-bold text-sm">$88,500,000.00</span>
          </div>
          <div onclick="switchTab('accounts')" class="p-3 rounded-xl flex items-center justify-between cursor-pointer" style="background: var(--bg-elevated);">
            <div class="flex items-center gap-2.5">
              ${getBankLogoBadge("bofa")}
              <div>
                <div class="font-bold">BofA Deal Desk (4473) + SoFi Larry Tears (5857)</div>
                <div class="text-[11px]" style="color: var(--text-secondary);">$14.25M BofA + $19.84M SoFi (+ $0.42 Free Coffee Vault)</div>
              </div>
            </div>
            <span class="mono-num font-bold text-sm">$34,090,000.42</span>
          </div>
        </div>
      ` : `
        <div class="flex items-center justify-between mb-3">
          <span class="text-[16px] font-bold">Cash &amp; 311 Lease Vault</span>
          <button onclick="switchTab('accounts')" class="text-xs font-semibold cursor-pointer" style="color: var(--amethyst);">Accounts ›</button>
        </div>
        <div class="space-y-2.5 text-xs">
          <div onclick="switchTab('goals')" class="p-3 rounded-xl flex items-center justify-between cursor-pointer" style="background: var(--bg-elevated);">
            <div class="flex items-center gap-2.5">
              ${getBankLogoBadge("sofi")}
              <div>
                <div class="font-bold">SoFi Savings (2752 — 311 Lease Vault)</div>
                <div class="text-[11px]" style="color: var(--monarch-green);">$13,744.71 locked (Nov–Jan) · <strong>+$12,259.16 Surplus</strong></div>
              </div>
            </div>
            <span class="mono-num font-bold text-sm">$26,003.87</span>
          </div>
          <div onclick="switchTab('accounts')" class="p-3 rounded-xl flex items-center justify-between cursor-pointer" style="background: var(--bg-elevated);">
            <div class="flex items-center gap-2.5">
              ${getBankLogoBadge("bofa")}
              <div>
                <div class="font-bold">BofA Checking (4473) + SoFi (5857)</div>
                <div class="text-[11px]" style="color: var(--text-secondary);">$23,905.80 BofA + $12,589.11 SoFi</div>
              </div>
            </div>
            <span class="mono-num font-bold text-sm">$36,494.91</span>
          </div>
        </div>
      `;
    }

    // =========================================================================
    // 02. ACCOUNTS & NET WORTH VIEW (100% REPLICA OF MONARCH SCREENSHOT 3)
    // =========================================================================
    function getInlineAccountSparkline(idx) {
      // Crisp 68x24 inline gray sparkline (`~^~v~`) just like Screenshot 3 (`media_1791834590404_795a91a8.png`)
      const paths = [
        "M 2 18 L 10 15 L 18 19 L 26 12 L 34 14 L 42 9 L 50 13 L 58 7 L 66 9",
        "M 2 19 L 12 17 L 20 14 L 28 16 L 36 11 L 45 12 L 54 8 L 66 6",
        "M 2 14 L 11 18 L 19 11 L 27 17 L 35 9 L 43 16 L 52 10 L 60 15 L 66 11",
        "M 2 16 L 14 16 L 26 15 L 38 15 L 50 14 L 66 14"
      ];
      const p = paths[idx % paths.length];
      return `
        <svg viewBox="0 0 68 24" class="w-20 h-6 flex-shrink-0 hidden sm:block">
          <path d="${p}" fill="none" stroke="#8E8C99" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
      `;
    }

    function renderAccountsView() {
      const isTK = activeProfile === "TK";
      const s = state.summary;
      const cashAccounts = state.accounts.filter(a => !a.is_liability && !a.name.includes("6725"));
      const invAccounts = state.accounts.filter(a => !a.is_liability && a.name.includes("6725"));
      const liabs = state.accounts.filter(a => a.is_liability);

      const cashTotal = cashAccounts.reduce((acc, a) => acc + a.balance, 0);
      const invTotal = invAccounts.reduce((acc, a) => acc + a.balance, 0);
      const nwMeta = getNwRangeMeta(isTK, s);

      const metricConfigs = {
        "net_worth": {
          title: "NET WORTH ⓘ",
          val: s.net_worth,
          color: "#0284C7",
          delta: nwMeta.delta
        },
        "unencumbered": {
          title: "TRUE UNENCUMBERED NET WORTH ⓘ",
          val: s.unencumbered_net_worth,
          color: "#7C3AED",
          delta: isTK ? "↑ $38,200,000.00 (10.8%)" : "↑ $4,120.40 (26.7%)"
        },
        "assets": {
          title: "TOTAL ASSETS PERFORMANCE ⓘ",
          val: s.total_assets,
          color: "#16A34A",
          delta: isTK ? "↑ $42,440,000.00 (10.8%)" : "↑ $4,969.42 (8.0%)"
        },
        "liabilities": {
          title: "CREDIT CARD FLOAT & LIABILITIES ⓘ",
          val: -s.total_liabilities,
          color: "#E11D48",
          delta: isTK ? "↓ $250,000.00 (-12.2%)" : "↓ $1,420.18 (-4.1%)"
        },
        "cash": {
          title: "LIQUID CASH & VAULTS ⓘ",
          val: cashTotal,
          color: "#0891B2",
          delta: isTK ? "↑ $14,200,000.00 (13.1%)" : "↑ $4,581.57 (7.9%)"
        }
      };
      const mCfg = metricConfigs[acctChartMetric] || metricConfigs["net_worth"];

      document.getElementById("accountsViewContent").innerHTML = `
        <!-- FULL-WIDTH TOP CARD: NET WORTH ⓘ + CERULEAN AREA CURVE (EXACT SCREENSHOT 3 + 100% CLICKABLE) -->
        <div class="m-card p-6 space-y-4">
          <div class="flex flex-wrap items-start justify-between gap-4">
            <div>
              <div onclick="setAcctChartMetric(acctChartMetric==='net_worth'?'unencumbered':'net_worth')" class="text-[10px] font-bold uppercase tracking-widest flex items-center gap-1 cursor-pointer hover:underline" style="color: var(--text-secondary);" title="Tap to toggle Net Worth vs Unencumbered NW">
                <span>${mCfg.title}</span>
              </div>
              <div class="flex flex-wrap items-baseline gap-2.5 mt-1">
                <span class="text-2xl font-bold mono-num">${fmt(mCfg.val)}</span>
                <span onclick="setNwRange(nwRange==='1M'?'3M':(nwRange==='3M'?'6M':(nwRange==='6M'?'1Y':(nwRange==='1Y'?'ALL':'1M'))))" class="text-xs font-semibold mono-num cursor-pointer hover:underline" style="color: var(--monarch-green);" title="Tap to cycle timeframe">${mCfg.delta}</span>
                <span class="text-xs" style="color: var(--text-secondary);">${nwMeta.label} change</span>
                <span onclick="openGoalEditor('vault')" class="text-xs px-2.5 py-0.5 rounded-full font-semibold mono-num cursor-pointer hover:opacity-85" style="background: var(--amethyst-soft); color: var(--amethyst);" title="Click to edit locked Escrow / Lease Vault amount">
                  ${isTK ? `True Unencumbered (after ${fmtShort(s.lease_311_remaining_obligation)} B200 Escrow): +${fmt(s.unencumbered_net_worth)} ✎` : `True Unencumbered (after ${fmtShort(s.lease_311_remaining_obligation)} 311 Lease): +${fmt(s.unencumbered_net_worth)} ✎`}
                </span>
              </div>
            </div>
            <div class="flex flex-wrap items-center gap-2">
              <select onchange="setAcctChartMetric(this.value)" class="px-3 py-1.5 rounded-lg text-xs font-semibold cursor-pointer" style="background: var(--bg-surface); border: 1px solid var(--border-subtle); color: var(--text-primary);" title="Select Performance Metric">
                <option value="net_worth" ${acctChartMetric === "net_worth" ? "selected" : ""}>Net worth performance</option>
                <option value="unencumbered" ${acctChartMetric === "unencumbered" ? "selected" : ""}>True Unencumbered NW</option>
                <option value="assets" ${acctChartMetric === "assets" ? "selected" : ""}>Total Assets performance</option>
                <option value="cash" ${acctChartMetric === "cash" ? "selected" : ""}>Liquid Cash &amp; Vaults</option>
                <option value="liabilities" ${acctChartMetric === "liabilities" ? "selected" : ""}>Credit Card Liabilities</option>
              </select>
              <select onchange="setNwRange(this.value)" class="px-3 py-1.5 rounded-lg text-xs font-semibold cursor-pointer" style="background: var(--bg-surface); border: 1px solid var(--border-subtle); color: var(--text-primary);" title="Select Timeframe">
                <option value="1M" ${nwRange === "1M" ? "selected" : ""}>1 month</option>
                <option value="3M" ${nwRange === "3M" ? "selected" : ""}>3 months</option>
                <option value="6M" ${nwRange === "6M" ? "selected" : ""}>6 months</option>
                <option value="1Y" ${nwRange === "1Y" ? "selected" : ""}>1 year</option>
                <option value="ALL" ${nwRange === "ALL" ? "selected" : ""}>All time</option>
              </select>
            </div>
          </div>

          <!-- Full-Width Area Chart with Y-Axis & Date X-Axis (Interactive Timeframe & Metric) -->
          <svg viewBox="0 0 880 185" class="w-full h-44 overflow-visible">
            <defs>
              <linearGradient id="acctCeruleanFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="${mCfg.color}" stop-opacity="0.24"/>
                <stop offset="100%" stop-color="${mCfg.color}" stop-opacity="0.02"/>
              </linearGradient>
            </defs>
            <text x="46" y="24" text-anchor="end" font-size="10" fill="var(--text-secondary)" class="mono-num">${fmtShort(Math.abs(mCfg.val) * 1.04)}</text>
            <line x1="52" y1="20" x2="865" y2="20" stroke="var(--border-subtle)" />
            <text x="46" y="56" text-anchor="end" font-size="10" fill="var(--text-secondary)" class="mono-num">${fmtShort(Math.abs(mCfg.val) * 0.99)}</text>
            <line x1="52" y1="52" x2="865" y2="52" stroke="var(--border-subtle)" />
            <text x="46" y="88" text-anchor="end" font-size="10" fill="var(--text-secondary)" class="mono-num">${fmtShort(Math.abs(mCfg.val) * 0.94)}</text>
            <line x1="52" y1="84" x2="865" y2="84" stroke="var(--border-subtle)" />
            <text x="46" y="120" text-anchor="end" font-size="10" fill="var(--text-secondary)" class="mono-num">${fmtShort(Math.abs(mCfg.val) * 0.89)}</text>
            <line x1="52" y1="116" x2="865" y2="116" stroke="var(--border-subtle)" />
            <text x="46" y="152" text-anchor="end" font-size="10" fill="var(--text-secondary)" class="mono-num">${fmtShort(Math.abs(mCfg.val) * 0.84)}</text>
            <line x1="52" y1="148" x2="865" y2="148" stroke="var(--border-subtle)" />

            <path d="${nwMeta.acctPath} L 855 148 L 65 148 Z" fill="url(#acctCeruleanFill)" />
            <path d="${nwMeta.acctPath}" fill="none" stroke="${mCfg.color}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" />

            ${nwMeta.ticks.map((tk, idx) => `<text x="${65 + idx * 96}" y="168" font-size="9.5" fill="var(--text-secondary)" class="cursor-pointer" onclick="setNwRange('${["1M","3M","6M","1Y","ALL"][idx % 5]}')">${tk}</text>`).join("")}
          </svg>

          <!-- Interactive Timeframe Bar -->
          <div class="flex items-center justify-end gap-1.5 pt-1 text-xs font-semibold">
            ${["1M", "3M", "6M", "1Y", "ALL"].map(rk => `
              <button onclick="setNwRange('${rk}')" class="px-2.5 py-1 rounded-md cursor-pointer transition-all" style="background: ${nwRange === rk ? "var(--amethyst)" : "var(--bg-elevated)"}; color: ${nwRange === rk ? "#ffffff" : "var(--text-secondary)"}; border: 0;">${rk}</button>
            `).join("")}
          </div>
        </div>

        <!-- 2-COLUMN SPLIT BELOW NET WORTH: LEFT ACCOUNT GROUPS WITH SPARKLINES + RIGHT SUMMARY CARD -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
          <!-- Left Column (8 cols): Cash, Credit Cards, Investments with Official Bank Logos + Inline Sparklines -->
          <div class="lg:col-span-8 space-y-4">
            <!-- Group 1: Cash -->
            <div class="m-card p-5 space-y-2">
              <div onclick="toggleAcctGroup('cash')" class="flex items-center justify-between pb-2 cursor-pointer select-none hover:opacity-85" style="border-bottom: 1px solid var(--border-subtle);" title="Tap to collapse/expand Cash accounts">
                <div class="flex items-baseline gap-2">
                  <span class="text-sm font-bold">${collapsedAcctGroups['cash'] ? '▸' : '▾'} Cash</span>
                  <span class="text-xs font-semibold mono-num" style="color: var(--monarch-green);">${isTK ? "↑ $14,200,000.00 (13.1%)" : "↑ $4,581.57 (7.9%)"}</span>
                  <span class="text-xs hidden sm:inline" style="color: var(--text-secondary);">${nwMeta.label} change</span>
                </div>
                <span class="mono-num font-bold text-sm">${fmt(cashTotal)}</span>
              </div>
              <div class="${collapsedAcctGroups['cash'] ? 'hidden' : 'divide-y'}" style="border-color: var(--border-subtle);">
                ${cashAccounts.map((a, idx) => {
                  const code = a.name.match(/\d{4}/) ? a.name.match(/\d{4}/)[0] : "";
                  const vaultNote = isTK
                    ? (a.name.includes("2752") ? `· ▣ ${fmtShort(s.lease_311_remaining_obligation)} Locked for B200 GPU Racks (+${fmtShort(s.sofi_2752_true_buffer)} Free)` : (a.name.includes("4499") ? "· ▣ Remaining free Kombucha & snack budget in Sunnyvale" : ""))
                    : (a.name.includes("2752") ? `· ▣ ${fmt(s.lease_311_remaining_obligation)} Locked for 311 Lease (+${fmt(s.sofi_2752_true_buffer)} Free)` : "");
                  return `
                    <div onclick="jumpToAccount('${code}')" class="py-3 flex items-center justify-between gap-3 cursor-pointer hover:opacity-85" title="Click row to filter transactions · Click balance to edit account">
                      <div class="flex items-center gap-3 min-w-0 flex-1">
                        ${getBankLogoBadge(a.institution)}
                        <div class="truncate">
                          <div class="font-semibold text-[13px] truncate">${a.name}</div>
                          <div class="text-[11px]" style="color: var(--text-secondary);">${a.type} ${vaultNote}</div>
                        </div>
                      </div>
                      ${getInlineAccountSparkline(idx)}
                      <div onclick="event.stopPropagation();openAccountEditor('${a.account_id}')" class="text-right flex-shrink-0 px-2 py-1 rounded-lg hover:bg-purple-500/10" title="Click to edit account balance or details">
                        <div class="text-[13px] font-bold mono-num flex items-center justify-end gap-1">${fmt(a.balance)} <span class="text-[10px]" style="color:var(--amethyst);">✎</span></div>
                        <div class="text-[10.5px]" style="color: var(--text-secondary);">Tap to edit</div>
                      </div>
                    </div>
                  `;
                }).join("")}
              </div>
            </div>

            <!-- Group 2: Credit Cards -->
            <div class="m-card p-5 space-y-2">
              <div onclick="toggleAcctGroup('cards')" class="flex items-center justify-between pb-2 cursor-pointer select-none hover:opacity-85" style="border-bottom: 1px solid var(--border-subtle);" title="Tap to collapse/expand Credit Cards">
                <div class="flex items-baseline gap-2">
                  <span class="text-sm font-bold">${collapsedAcctGroups['cards'] ? '▸' : '▾'} Credit Cards</span>
                  <span class="text-xs font-semibold mono-num" style="color: var(--monarch-green);">${isTK ? "↓ $250,000.00 (OCI Refund)" : "↓ $1,420.18 (-4.1%)"}</span>
                  <span class="text-xs hidden sm:inline" style="color: var(--text-secondary);">${nwMeta.label} change</span>
                </div>
                <span class="mono-num font-bold text-sm">${fmt(s.total_liabilities)}</span>
              </div>
              <div class="${collapsedAcctGroups['cards'] ? 'hidden' : 'divide-y'}" style="border-color: var(--border-subtle);">
                ${liabs.map((a, idx) => {
                  const code = a.name.match(/\d{4}/) ? a.name.match(/\d{4}/)[0] : "";
                  const cardSub = isTK
                    ? (a.institution === "amex" ? "Centurion Autopay $1,420,690 due Oct 27 (H200s & Brioni)" : "Executive Jet Visa $384,210 due Oct 17 (Deloitte & Oracle Lawyers)")
                    : (a.institution === "amex" ? "Sep Statement ~$18,748.24 due Oct 27" : "Sep Statement $8,754.52 due Oct 17");
                  return `
                    <div onclick="jumpToAccount('${code}')" class="py-3 flex items-center justify-between gap-3 cursor-pointer hover:opacity-85" title="Click row to filter transactions · Click balance to edit account">
                      <div class="flex items-center gap-3 min-w-0 flex-1">
                        ${getBankLogoBadge(a.institution)}
                        <div class="truncate">
                          <div class="font-semibold text-[13px] truncate">${a.name}</div>
                          <div class="text-[11px]" style="color: var(--text-secondary);">Credit Card · ${cardSub}</div>
                        </div>
                      </div>
                      ${getInlineAccountSparkline(idx + 2)}
                      <div onclick="event.stopPropagation();openAccountEditor('${a.account_id}')" class="text-right flex-shrink-0 px-2 py-1 rounded-lg hover:bg-purple-500/10" title="Click to edit card balance or details">
                        <div class="text-[13px] font-bold mono-num flex items-center justify-end gap-1">${fmt(a.balance)} <span class="text-[10px]" style="color:var(--amethyst);">✎</span></div>
                        <div class="text-[10.5px]" style="color: var(--text-secondary);">Tap to edit</div>
                      </div>
                    </div>
                  `;
                }).join("")}
              </div>
            </div>

            <!-- Group 3: Investments -->
            <div class="m-card p-5 space-y-2">
              <div onclick="toggleAcctGroup('inv')" class="flex items-center justify-between pb-2 cursor-pointer select-none hover:opacity-85" style="border-bottom: 1px solid var(--border-subtle);" title="Tap to collapse/expand Investments">
                <div class="flex items-baseline gap-2">
                  <span class="text-sm font-bold">${collapsedAcctGroups['inv'] ? '▸' : '▾'} Investments</span>
                  <span class="text-xs font-semibold mono-num" style="color: var(--monarch-green);">${isTK ? "↑ $28,490,000.00 (10.0%)" : "↑ $387.85 (10.4%)"}</span>
                  <span class="text-xs hidden sm:inline" style="color: var(--text-secondary);">${nwMeta.label} change</span>
                </div>
                <span class="mono-num font-bold text-sm">${fmt(invTotal)}</span>
              </div>
              <div class="${collapsedAcctGroups['inv'] ? 'hidden' : 'divide-y'}" style="border-color: var(--border-subtle);">
                ${invAccounts.map((a, idx) => {
                  const code = a.name.match(/\d{4}/) ? a.name.match(/\d{4}/)[0] : "";
                  return `
                    <div onclick="switchTab('investments')" class="py-3 flex items-center justify-between gap-3 cursor-pointer hover:opacity-85" title="Click row to open Investments · Click balance to edit account">
                      <div class="flex items-center gap-3 min-w-0 flex-1">
                        ${getBankLogoBadge(a.institution)}
                        <div class="truncate">
                          <div class="font-semibold text-[13px] truncate">${a.name}</div>
                          <div class="text-[11px]" style="color: var(--text-secondary);">${isTK ? "GOOG Class C GSUs & Anthropic Series E Warrants" : "Brokerage Portfolio"}</div>
                        </div>
                      </div>
                      ${getInlineAccountSparkline(1)}
                      <div onclick="event.stopPropagation();openAccountEditor('${a.account_id}')" class="text-right flex-shrink-0 px-2 py-1 rounded-lg hover:bg-purple-500/10" title="Click to edit brokerage balance">
                        <div class="text-[13px] font-bold mono-num flex items-center justify-end gap-1">${fmt(a.balance)} <span class="text-[10px]" style="color:var(--amethyst);">✎</span></div>
                        <div class="text-[10.5px]" style="color: var(--text-secondary);">Tap to edit</div>
                      </div>
                    </div>
                  `;
                }).join("")}
              </div>
            </div>
          </div>

          <!-- Right Column (4 cols): Sticky Summary Card with Multi-Segment Horizontal Bars (All Rows Clickable) -->
          <div class="lg:col-span-4">
            <div class="m-card p-5 space-y-5">
              <div class="flex items-center justify-between">
                <span class="text-sm font-bold">Summary</span>
                <div class="flex items-center rounded-lg p-0.5 text-xs" style="background: var(--bg-elevated);">
                  <button onclick="acctSummaryMode='totals';renderAccountsView()" class="px-2.5 py-1 rounded-md font-semibold cursor-pointer" style="background: ${acctSummaryMode === 'totals' ? 'var(--bg-surface)' : 'transparent'};">Totals</button>
                  <button onclick="acctSummaryMode='percent';renderAccountsView()" class="px-2.5 py-1 rounded-md font-medium cursor-pointer" style="background: ${acctSummaryMode === 'percent' ? 'var(--bg-surface)' : 'transparent'}; color: var(--text-secondary);">Percent</button>
                </div>
              </div>

              <!-- Assets Section with Multi-Color Proportional Bar -->
              <div class="space-y-3 text-xs">
                <div onclick="setAcctChartMetric('assets')" class="flex items-center justify-between cursor-pointer hover:underline" title="Click to plot Total Assets">
                  <span class="font-bold">Assets ›</span>
                  <span class="mono-num font-semibold" style="color: var(--text-secondary);">${fmt(s.total_assets)}</span>
                </div>
                <div class="w-full h-2 rounded-full overflow-hidden flex gap-0.5">
                  <div style="width: ${isTK ? "18.5%" : "73.2%"}; background: #16A34A;"></div>
                  <div style="width: ${isTK ? "9.7%" : "20.6%"}; background: #7C3AED;"></div>
                  <div style="width: ${isTK ? "71.8%" : "6.2%"}; background: #06B6D4;"></div>
                </div>
                <div class="space-y-2 pt-1">
                  <div onclick="setAcctChartMetric('cash')" class="flex items-center justify-between cursor-pointer hover:opacity-80">
                    <div class="flex items-center gap-2"><span class="w-2 h-2 rounded-full" style="background:#16A34A;"></span><span>Unencumbered Cash ›</span></div>
                    <span class="mono-num font-medium">${acctSummaryMode === "percent" ? (isTK ? "18.5%" : "73.2%") : fmt(Math.max(0, cashTotal - s.lease_311_remaining_obligation))}</span>
                  </div>
                  <div onclick="openGoalEditor('vault')" class="flex items-center justify-between cursor-pointer hover:opacity-80" title="Click to edit Locked Vault amount">
                    <div class="flex items-center gap-2"><span class="w-2 h-2 rounded-full" style="background:#7C3AED;"></span><span>${isTK ? "B200 GPU Escrow (Locked) ✎" : "311 Lease Vault (Locked) ✎"}</span></div>
                    <span class="mono-num font-medium">${acctSummaryMode === "percent" ? (isTK ? "9.7%" : "20.6%") : fmt(s.lease_311_remaining_obligation)}</span>
                  </div>
                  <div onclick="switchTab('investments')" class="flex items-center justify-between cursor-pointer hover:opacity-80">
                    <div class="flex items-center gap-2"><span class="w-2 h-2 rounded-full" style="background:#06B6D4;"></span><span>Investments (SoFi 6725) ›</span></div>
                    <span class="mono-num font-medium">${acctSummaryMode === "percent" ? (isTK ? "71.8%" : "6.2%") : fmt(invTotal)}</span>
                  </div>
                </div>
              </div>

              <!-- Liabilities & Lease Commitments Section with Multi-Color Bar -->
              <div class="space-y-3 text-xs pt-3" style="border-top: 1px solid var(--border-subtle);">
                <div onclick="setAcctChartMetric('liabilities')" class="flex items-center justify-between cursor-pointer hover:underline">
                  <span class="font-bold">${isTK ? "Liabilities &amp; GPU Escrow ›" : "Liabilities &amp; Lease Escrow ›"}</span>
                  <span class="mono-num font-semibold" style="color: var(--text-secondary);">${fmt(s.total_liabilities + s.lease_311_remaining_obligation)}</span>
                </div>
                <div class="w-full h-2 rounded-full overflow-hidden flex gap-0.5">
                  <div style="width: ${isTK ? "4.1%" : "70.9%"}; background: #EF4444;"></div>
                  <div style="width: ${isTK ? "95.9%" : "29.1%"}; background: #F59E0B;"></div>
                </div>
                <div class="space-y-2 pt-1">
                  <div onclick="switchTab('advisor')" class="flex items-center justify-between cursor-pointer hover:opacity-80">
                    <div class="flex items-center gap-2"><span class="w-2 h-2 rounded-full" style="background:#EF4444;"></span><span>Credit Cards (Amex + BofA) ›</span></div>
                    <span class="mono-num font-medium">${acctSummaryMode === "percent" ? (isTK ? "4.1%" : "70.9%") : fmt(s.total_liabilities)}</span>
                  </div>
                  <div onclick="openGoalEditor('vault')" class="flex items-center justify-between cursor-pointer hover:opacity-80">
                    <div class="flex items-center gap-2"><span class="w-2 h-2 rounded-full" style="background:#F59E0B;"></span><span>${isTK ? "B200 GPU Cluster Escrow ✎" : "311 Remaining Lease (3 mos) ✎"}</span></div>
                    <span class="mono-num font-medium">${acctSummaryMode === "percent" ? (isTK ? "95.9%" : "29.1%") : fmt(s.lease_311_remaining_obligation)}</span>
                  </div>
                </div>
              </div>

              <!-- True Unencumbered Net Worth Callout -->
              <div onclick="setAcctChartMetric('unencumbered')" class="p-3.5 rounded-xl flex justify-between items-center text-xs cursor-pointer hover:opacity-90" style="background: var(--amethyst-soft); color: var(--amethyst);" title="Click to plot True Unencumbered Net Worth">
                <span class="font-bold">True Unencumbered NW ›</span>
                <span class="mono-num font-bold text-base">+${fmt(s.unencumbered_net_worth)}</span>
              </div>
            </div>
          </div>
        </div>
      `;
    }

    // =========================================================================
    // 03. TRANSACTIONS — OFFICIAL COMPANY LOGOS + P BADGE + DATE HEADERS
    // =========================================================================
    function populateCategoryDropdown() {
      const sel = document.getElementById("txnCatFilter");
      if (!sel || sel.options.length > 1) return;
      const cats = Array.from(new Set(state.transactions.map(t => t.category))).sort();
      cats.forEach(c => {
        const opt = document.createElement("option");
        opt.value = c;
        opt.textContent = `${getCatMeta(c).icon} ${c}`;
        sel.appendChild(opt);
      });
    }

    function getFilteredTransactions() {
      populateCategoryDropdown();
      const q = (document.getElementById("txnSearch")?.value || "").trim().toLowerCase();
      const catFilter = document.getElementById("txnCatFilter")?.value || "ALL";
      const typeFilter = document.getElementById("txnTypeFilter")?.value || "EXPENSE_NET";

      return state.transactions.filter(t => {
        if (!inSelectedWindow(t)) return false;
        if (typeFilter === "EXPENSE_NET") {
          if (t.txn_type !== "expense") return false;
          if (refundStrippedMode && t.net_amount <= 0.005) return false;
        } else if (typeFilter === "EXPENSE_ALL") {
          if (t.txn_type !== "expense") return false;
        } else if (typeFilter === "REFUND") {
          if (t.txn_type !== "refund") return false;
        } else if (typeFilter === "INCOME") {
          if (t.txn_type !== "income") return false;
        } else if (typeFilter === "TRANSFER") {
          if (t.txn_type !== "transfer") return false;
        }
        if (catFilter !== "ALL" && t.category !== catFilter) return false;
        const dispAmt = t.txn_type === "expense" ? (refundStrippedMode ? t.net_amount : t.amount) : t.amount;
        if (q) {
          const hay = `${t.date} ${t.merchant_clean} ${t.description} ${t.category} ${t.account_name} ${(t.tags || []).join(" ")} ${dispAmt.toFixed(2)}`.toLowerCase();
          if (!hay.includes(q)) return false;
        }
        return true;
      }).map(t => ({
        ...t,
        display_amount: t.txn_type === "expense" ? (refundStrippedMode ? t.net_amount : t.amount) : t.amount
      }));
    }

    function renderTransactionsTable() {
      const list = getFilteredTransactions();
      const sumTotal = list.reduce((acc, t) => acc + t.display_amount, 0);
      document.getElementById("txnSummaryPill").textContent = `${list.length} items · ${fmt(sumTotal)}`;
      const tSel = document.getElementById("txnWindowSelect");
      if (tSel && tSel.value !== globalWindow) tSel.value = globalWindow;

      const byDate = {};
      list.slice(0, 250).forEach(t => {
        if (!byDate[t.date]) byDate[t.date] = [];
        byDate[t.date].push(t);
      });

      const dates = Object.keys(byDate).sort((a, b) => b.localeCompare(a));
      document.getElementById("txnDateGroupedList").innerHTML = dates.map(d => {
        const items = byDate[d];
        const isCollapsed = !!collapsedTxnDates[d];
        const dayTotal = items.reduce((s, x) => s + (x.txn_type === "income" || x.txn_type === "refund" ? x.display_amount : -x.display_amount), 0);
        return `
          <div class="rounded-xl overflow-hidden" style="border: 1px solid var(--border-subtle);">
            <div onclick="toggleTxnDateGroup('${d}')" class="px-4 py-2 flex items-center justify-between text-xs font-semibold cursor-pointer select-none hover:opacity-85" style="background: var(--bg-elevated); color: var(--text-secondary);" title="Tap to collapse/expand ${d}">
              <span>${isCollapsed ? "▸" : "▾"} ${d} (${items.length})</span>
              <span class="mono-num">${fmt(dayTotal, true)}</span>
            </div>
            <div class="${isCollapsed ? "hidden" : "divide-y"} text-[13px]" style="background: var(--bg-surface); border-color: var(--border-subtle);">
              ${items.map(t => {
                const meta = getCatMeta(t.category);
                const isPos = t.txn_type === "income" || t.txn_type === "refund";
                const brandLogo = getMerchantBrandAvatar(t.merchant_clean, t.category, t.institution);
                return `
                  <div onclick="openTxnModal('${t.txn_id}')" class="px-3.5 sm:px-4 py-2.5 flex items-center justify-between sm:grid sm:grid-cols-12 gap-2 cursor-pointer hover:opacity-85" title="Tap any field to edit transaction">
                    <div class="sm:col-span-5 flex items-center gap-2.5 min-w-0 flex-1">
                      ${brandLogo}
                      <div class="min-w-0">
                        <div class="font-medium truncate">${t.merchant_clean}</div>
                        <div class="text-[10.5px] truncate" style="color: var(--text-secondary);">
                          <span class="sm:hidden">${meta.icon} ${t.category} · </span>${t.account_name}
                        </div>
                      </div>
                    </div>
                    <div onclick="event.stopPropagation();jumpToCategory('${t.category.replace(/'/g, "\\'")}')" class="hidden sm:flex sm:col-span-4 items-center gap-1.5 min-w-0 text-xs hover:underline" style="color: var(--text-secondary);" title="Click to filter by ${t.category}">
                      <span>${meta.icon}</span>
                      <span class="truncate">${t.category}</span>
                    </div>
                    <div class="sm:col-span-3 flex items-center justify-end gap-1.5 flex-shrink-0">
                      ${t.refunded_amount > 0 ? `<span class="text-[9.5px] font-semibold px-1.5 py-0.5 rounded-full mono-num" style="background: var(--monarch-green-soft); color: var(--monarch-green);">-${fmtShort(t.refunded_amount)}</span>` : ""}
                      <span class="monarch-p-badge hidden sm:inline-flex">P</span>
                      <span class="mono-num font-semibold" style="color: ${isPos ? "var(--monarch-green)" : "var(--text-primary)"};">${isPos ? "+" : ""}${fmt(t.display_amount)}</span>
                      <span class="text-xs" style="color: var(--amethyst);">✎</span>
                    </div>
                  </div>
                `;
              }).join("")}
            </div>
          </div>
        `;
      }).join("");

      const auditRows = state.refund_audit_log.filter(r => {
        if (bankScope !== "ALL" && r.institution !== bankScope) return false;
        if (globalWindow === "ALL") return true;
        if (globalWindow === "60D") return r.refund_date >= "2026-08-18" && r.refund_date <= "2026-10-12";
        return r.refund_date.startsWith(globalWindow);
      });
      const totalAudit = auditRows.reduce((s, r) => s + r.refund_amount, 0);
      document.getElementById("refundAuditTotalBadge").textContent = `${auditRows.length} Credits · -${fmt(totalAudit)} Stripped`;
      document.getElementById("refundAuditList").innerHTML = auditRows.map(r => `
        <div onclick="jumpToAccount('${r.merchant.split(' ')[0].replace(/'/g, "\\'")}')" class="py-2.5 px-2 flex items-center justify-between cursor-pointer hover:opacity-85" title="Click to filter transactions for ${r.merchant}">
          <div class="flex items-center gap-2.5">
            ${getMerchantBrandAvatar(r.merchant, "Apparel & Luxury Shopping", r.institution)}
            <div>
              <div class="font-semibold">${r.merchant} (${r.institution.toUpperCase()}) ›</div>
              <div class="text-[11px]" style="color: var(--text-secondary);">Purchase ${r.purchase_date} (${fmt(r.original_amount)}) → Refund ${r.refund_date}</div>
            </div>
          </div>
          <div class="text-right mono-num">
            <div class="font-bold" style="color: var(--monarch-green);">+${fmt(r.refund_amount)}</div>
            <div class="text-[10px] font-semibold">${r.status}</div>
          </div>
        </div>
      `).join("");
    }

    function resetTxnFilters() {
      document.getElementById("txnSearch").value = "";
      document.getElementById("txnCatFilter").value = "ALL";
      document.getElementById("txnTypeFilter").value = "EXPENSE_NET";
      renderTransactionsTable();
    }

    function jumpToCategory(catName) {
      switchTab("transactions");
      populateCategoryDropdown();
      document.getElementById("txnCatFilter").value = catName;
      renderTransactionsTable();
    }

    function jumpToAccount(code) {
      switchTab("transactions");
      document.getElementById("txnSearch").value = code;
      renderTransactionsTable();
    }

    function renderTxnModalFields(t, isNew = false) {
      const cats = Object.keys(CATEGORY_META);
      const catOptions = cats.map(c => `<option value="${c}" ${c === t.category ? "selected" : ""}>${CATEGORY_META[c].icon} ${c}</option>`).join("");
      const acctOptions = state.accounts.map(a => `<option value="${a.name}" ${a.name === t.account_name ? "selected" : ""}>${a.name}</option>`).join("");
      const curAmt = Number(t.net_amount !== undefined && t.txn_type === "expense" ? t.net_amount : t.amount) || 0;

      document.getElementById("modalBody").innerHTML = `
        <div class="p-3.5 rounded-xl flex items-center justify-between" style="background: var(--bg-elevated);">
          <div class="flex items-center gap-2.5">
            ${getMerchantBrandAvatar(t.merchant_clean, t.category, t.institution)}
            <div>
              <div class="text-[11px]" style="color: var(--text-secondary);">${t.date} · ${t.account_name}</div>
              <div class="font-mono text-[11px] mt-0.5">${t.description || "EDITABLE TRANSACTION"}</div>
            </div>
          </div>
          <div class="text-lg font-bold mono-num" style="color: var(--amethyst);">${fmt(curAmt)}</div>
        </div>
        <div class="grid grid-cols-2 gap-2.5">
          <div>
            <label class="block font-semibold mb-1">Amount ($)</label>
            <input id="editAmount" type="number" step="0.01" value="${curAmt.toFixed(2)}" class="w-full px-3 py-2 mono-num font-bold" />
          </div>
          <div>
            <label class="block font-semibold mb-1">Date</label>
            <input id="editDate" type="date" value="${t.date}" class="w-full px-3 py-2 mono-num" />
          </div>
        </div>
        <div>
          <label class="block font-semibold mb-1">Merchant Name</label>
          <input id="editMerchant" type="text" value="${t.merchant_clean}" class="w-full px-3 py-2" />
        </div>
        <div class="grid grid-cols-2 gap-2.5">
          <div>
            <label class="block font-semibold mb-1">Transaction Type</label>
            <select id="editTxnType" class="w-full px-3 py-2">
              <option value="expense" ${t.txn_type === "expense" ? "selected" : ""}>Expense (Outflow)</option>
              <option value="income" ${t.txn_type === "income" ? "selected" : ""}>Income / Paycheck</option>
              <option value="refund" ${t.txn_type === "refund" ? "selected" : ""}>Merchant Refund</option>
              <option value="transfer" ${t.txn_type === "transfer" ? "selected" : ""}>Transfer / Autopay</option>
            </select>
          </div>
          <div>
            <label class="block font-semibold mb-1">Flex Bucket</label>
            <select id="editBucket" class="w-full px-3 py-2">
              <option value="Fixed" ${t.flex_bucket === "Fixed" ? "selected" : ""}>Fixed Expenses</option>
              <option value="Flexible" ${t.flex_bucket === "Flexible" ? "selected" : ""}>Flexible Living</option>
              <option value="Non-Monthly" ${t.flex_bucket === "Non-Monthly" ? "selected" : ""}>Non-Monthly &amp; Sinking</option>
              <option value="Income" ${t.flex_bucket === "Income" ? "selected" : ""}>Income</option>
              <option value="Transfer" ${t.flex_bucket === "Transfer" ? "selected" : ""}>Transfer</option>
            </select>
          </div>
        </div>
        <div>
          <label class="block font-semibold mb-1">Account</label>
          <select id="editAccount" class="w-full px-3 py-2">${acctOptions}</select>
        </div>
        <div>
          <label class="block font-semibold mb-1">Category</label>
          <select id="editCategory" class="w-full px-3 py-2">${catOptions}</select>
        </div>
        <div>
          <label class="block font-semibold mb-1">Tags</label>
          <input id="editTags" type="text" value="${(t.tags || []).join(" ")}" placeholder="#311-lease #travel #reimbursable" class="w-full px-3 py-2" />
        </div>
        <div>
          <label class="block font-semibold mb-1">Notes &amp; Split Memo</label>
          <input id="editNotes" type="text" value="${t.notes || ""}" placeholder="Add note..." class="w-full px-3 py-2" />
        </div>
      `;
    }

    function openTxnModal(txnId) {
      const t = state.transactions.find(x => x.txn_id === txnId);
      if (!t) return;
      editingModalMode = "txn";
      editingTxnId = txnId;
      document.getElementById("modalTitle").textContent = t.merchant_clean;
      renderTxnModalFields(t, false);
      document.getElementById("txnDrawerBackdrop").classList.remove("hidden");
      document.getElementById("txnDrawer").classList.remove("hidden");
    }

    function openNewTxnModal() {
      editingModalMode = "new_txn";
      editingTxnId = "NEW-" + Date.now();
      const defaultDate = globalWindow === "2026-08" ? "2026-08-15" : (globalWindow === "2026-10" ? "2026-10-12" : "2026-09-25");
      const firstAcct = state.accounts[0] || { name: "Checking (4473)", institution: "bofa" };
      const blankTxn = {
        txn_id: editingTxnId,
        date: defaultDate,
        period: defaultDate.slice(0, 7),
        description: "MANUAL ENTRY",
        merchant_clean: "New Merchant",
        category: "Food Delivery & Dining",
        flex_bucket: "Flexible",
        txn_type: "expense",
        direction: "outflow",
        institution: firstAcct.institution || "bofa",
        account_name: firstAcct.name,
        amount: 45.00,
        net_amount: 45.00,
        refunded_amount: 0.0,
        tags: ["#custom"],
        notes: ""
      };
      document.getElementById("modalTitle").textContent = "＋ Add New Transaction";
      renderTxnModalFields(blankTxn, true);
      document.getElementById("txnDrawerBackdrop").classList.remove("hidden");
      document.getElementById("txnDrawer").classList.remove("hidden");
    }

    function openAccountEditor(accountId) {
      const a = state.accounts.find(x => x.account_id === accountId);
      if (!a) return;
      editingModalMode = "account";
      editingModalKey = accountId;
      const code = a.name.match(/\d{4}/) ? a.name.match(/\d{4}/)[0] : a.name;
      document.getElementById("modalTitle").textContent = "Edit Account Balance & Details";
      document.getElementById("modalBody").innerHTML = `
        <div class="p-3.5 rounded-xl flex items-center justify-between" style="background: var(--bg-elevated);">
          <div class="flex items-center gap-2.5">
            ${getBankLogoBadge(a.institution)}
            <div>
              <div class="font-bold text-xs">${a.name}</div>
              <div class="text-[11px]" style="color: var(--text-secondary);">${a.institution_label} · ${a.is_liability ? "Credit Card Liability" : "Asset Account"}</div>
            </div>
          </div>
          <div class="text-lg font-bold mono-num" style="color: var(--amethyst);">${fmt(a.balance)}</div>
        </div>
        <div>
          <label class="block font-semibold mb-1">Account Display Name</label>
          <input id="editAcctName" type="text" value="${a.name}" class="w-full px-3 py-2" />
        </div>
        <div>
          <label class="block font-semibold mb-1">Account Type / Subtitle</label>
          <input id="editAcctType" type="text" value="${a.type}" class="w-full px-3 py-2" />
        </div>
        <div>
          <label class="block font-semibold mb-1">Current Balance ($)</label>
          <input id="editAcctBalance" type="number" step="0.01" value="${Math.abs(Number(a.balance || 0)).toFixed(2)}" class="w-full px-3 py-2 mono-num font-bold text-sm" />
          <p class="text-[10.5px] mt-1" style="color: var(--text-secondary);">Saving immediately recalculates Total Assets, Liabilities, Net Worth, and Unencumbered Net Worth across all tabs.</p>
        </div>
        <div class="pt-2">
          <button onclick="closeTxnModal();jumpToAccount('${code}')" class="pill-btn w-full py-2 justify-center font-semibold" style="color: var(--amethyst); border-color: rgba(124,58,237,0.35);">
            View All Transactions for ${code} ›
          </button>
        </div>
      `;
      document.getElementById("txnDrawerBackdrop").classList.remove("hidden");
      document.getElementById("txnDrawer").classList.remove("hidden");
    }

    function openBudgetEditor(catName) {
      const cfg = getCatMeta(catName);
      editingModalMode = "budget";
      editingModalKey = catName;
      document.getElementById("modalTitle").textContent = `Edit Budget: ${catName}`;
      document.getElementById("modalBody").innerHTML = `
        <div class="p-3.5 rounded-xl flex items-center justify-between" style="background: var(--bg-elevated);">
          <div class="flex items-center gap-2.5">
            <span class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold" style="background: ${cfg.color}20; color: ${cfg.color};">${cfg.icon}</span>
            <div>
              <div class="font-bold text-xs">${catName}</div>
              <div class="text-[11px]" style="color: var(--text-secondary);">Group: ${cfg.group} · Bucket: ${cfg.bucket}</div>
            </div>
          </div>
          <div class="text-lg font-bold mono-num" style="color: var(--amethyst);">${fmtInt(cfg.target)}/mo</div>
        </div>
        <div>
          <label class="block font-semibold mb-1">Monthly Base Budget Target ($)</label>
          <input id="editBudgetTarget" type="number" step="10" value="${cfg.target}" class="w-full px-3 py-2 mono-num font-bold text-sm" />
          <p class="text-[10.5px] mt-1" style="color: var(--text-secondary);">Automatically scales for 60D/90D windows and TK CEO Demo mode.</p>
        </div>
        <div>
          <label class="block font-semibold mb-1">Expense Bucket</label>
          <select id="editBudgetBucket" class="w-full px-3 py-2">
            <option value="Fixed" ${cfg.bucket === "Fixed" ? "selected" : ""}>Fixed Expenses</option>
            <option value="Flexible" ${cfg.bucket === "Flexible" ? "selected" : ""}>Flexible Expenses</option>
            <option value="Non-Monthly" ${cfg.bucket === "Non-Monthly" ? "selected" : ""}>Non-Monthly Expenses</option>
          </select>
        </div>
        <div>
          <label class="block font-semibold mb-1">Category Subtitle / Description</label>
          <input id="editBudgetDesc" type="text" value="${cfg.desc || ""}" class="w-full px-3 py-2" />
        </div>
        <div class="pt-2">
          <button onclick="closeTxnModal();jumpToCategory('${catName.replace(/'/g, "\\'")}')" class="pill-btn w-full py-2 justify-center font-semibold" style="color: var(--amethyst); border-color: rgba(124,58,237,0.35);">
            View Transactions in ${catName} ›
          </button>
        </div>
      `;
      document.getElementById("txnDrawerBackdrop").classList.remove("hidden");
      document.getElementById("txnDrawer").classList.remove("hidden");
    }

    function openGoalEditor(goalKey) {
      const s = state.summary;
      const isTK = activeProfile === "TK";
      editingModalMode = "goal";
      editingModalKey = goalKey;
      document.getElementById("modalTitle").textContent = isTK ? "Edit B200 GPU Escrow & Vault" : "Edit 311 Lease Vault & Goal";
      document.getElementById("modalBody").innerHTML = `
        <div class="p-3.5 rounded-xl space-y-1" style="background: var(--bg-elevated);">
          <div class="text-xs font-bold">${isTK ? "SoFi B200 GPU Escrow (2752)" : "SoFi Savings 311 Lease Vault (2752)"}</div>
          <div class="text-[11px]" style="color: var(--text-secondary);">True Unencumbered Buffer: <strong class="mono-num" style="color: var(--monarch-green);">+${fmt(s.sofi_2752_true_buffer)}</strong></div>
        </div>
        <div>
          <label class="block font-semibold mb-1">Total Vault Account Balance ($)</label>
          <input id="editVaultBalance" type="number" step="100" value="${s.sofi_2752_balance}" class="w-full px-3 py-2 mono-num font-bold text-sm" />
        </div>
        <div>
          <label class="block font-semibold mb-1">${isTK ? "Locked NVIDIA B200 GPU Escrow Obligation ($)" : "Locked 311 Lease Remaining Obligation ($)"}</label>
          <input id="editVaultLocked" type="number" step="100" value="${s.lease_311_remaining_obligation}" class="w-full px-3 py-2 mono-num font-bold text-sm" />
          <p class="text-[10.5px] mt-1" style="color: var(--text-secondary);">Changing this locked obligation immediately updates your True Unencumbered Net Worth across the entire app.</p>
        </div>
        <div class="pt-2 flex gap-2">
          <button onclick="closeTxnModal();jumpToAccount('2752')" class="pill-btn flex-1 py-2 justify-center font-semibold">Vault Txns ›</button>
          <button onclick="closeTxnModal();switchTab('advisor')" class="pill-btn flex-1 py-2 justify-center font-semibold" style="color: var(--amethyst);">Payoff Sim ›</button>
        </div>
      `;
      document.getElementById("txnDrawerBackdrop").classList.remove("hidden");
      document.getElementById("txnDrawer").classList.remove("hidden");
    }

    function closeTxnModal() {
      document.getElementById("txnDrawerBackdrop").classList.add("hidden");
      document.getElementById("txnDrawer").classList.add("hidden");
      editingTxnId = null;
      editingModalKey = null;
    }

    function saveTxnModal() {
      if (editingModalMode === "account" && editingModalKey) {
        const a = state.accounts.find(x => x.account_id === editingModalKey);
        if (a) {
          a.name = document.getElementById("editAcctName").value.trim() || a.name;
          a.type = document.getElementById("editAcctType").value.trim() || a.type;
          const rawBal = Math.abs(parseFloat(document.getElementById("editAcctBalance").value) || 0);
          a.balance = a.is_liability ? -rawBal : rawBal;
          a.abs_balance = rawBal;
          recalcSummaryFromAccounts();
        }
        closeTxnModal();
        renderAll();
        return;
      }

      if (editingModalMode === "budget" && editingModalKey) {
        const cfg = CATEGORY_META[editingModalKey];
        if (cfg) {
          cfg.target = Math.max(10, parseFloat(document.getElementById("editBudgetTarget").value) || cfg.target);
          cfg.bucket = document.getElementById("editBudgetBucket").value || cfg.bucket;
          cfg.desc = document.getElementById("editBudgetDesc").value.trim() || cfg.desc;
        }
        closeTxnModal();
        renderAll();
        return;
      }

      if (editingModalMode === "goal") {
        const newBal = Math.max(0, parseFloat(document.getElementById("editVaultBalance").value) || 0);
        const newLock = Math.max(0, parseFloat(document.getElementById("editVaultLocked").value) || 0);
        state.summary.sofi_2752_balance = newBal;
        state.summary.lease_311_remaining_obligation = newLock;
        const vaultAcct = state.accounts.find(a => a.name.includes("2752"));
        if (vaultAcct) {
          vaultAcct.balance = newBal;
          vaultAcct.abs_balance = newBal;
          vaultAcct.available_balance = Math.max(0, newBal - newLock);
        }
        recalcSummaryFromAccounts();
        closeTxnModal();
        renderAll();
        return;
      }

      if (editingModalMode === "recurring" && editingModalKey) {
        saveRecurringModalChange();
        return;
      }

      if (editingModalMode === "holding" && editingModalKey !== null) {
        saveHoldingModalChange();
        return;
      }

      if (!editingTxnId) return;
      let t = state.transactions.find(x => x.txn_id === editingTxnId);
      const isNew = editingModalMode === "new_txn" || !t;
      const newAmt = Math.abs(parseFloat(document.getElementById("editAmount")?.value) || 0);
      const newDate = document.getElementById("editDate")?.value || "2026-09-25";
      const newAcctName = document.getElementById("editAccount")?.value || (state.accounts[0]?.name || "Checking");
      const matchedAcct = state.accounts.find(a => a.name === newAcctName);
      const newType = document.getElementById("editTxnType")?.value || "expense";

      const patch = {
        merchant_clean: document.getElementById("editMerchant").value.trim() || "Merchant",
        amount: newAmt,
        net_amount: newAmt,
        date: newDate,
        period: newDate.slice(0, 7),
        txn_type: newType,
        direction: (newType === "income" || newType === "refund") ? "inflow" : "outflow",
        account_name: newAcctName,
        institution: matchedAcct ? matchedAcct.institution : "bofa",
        category: document.getElementById("editCategory").value,
        flex_bucket: document.getElementById("editBucket").value,
        tags: document.getElementById("editTags").value.trim().split(/\s+/).filter(Boolean),
        notes: document.getElementById("editNotes").value.trim(),
        reviewed: true,
        needs_review: false
      };

      if (isNew) {
        state.transactions.unshift({
          txn_id: editingTxnId,
          description: patch.merchant_clean.toUpperCase(),
          refunded_amount: 0.0,
          ...patch
        });
      } else {
        Object.assign(t, patch);
        const isBridge = window.location.pathname.startsWith("/monark") || window.location.pathname.startsWith("/monarch");
        const txnEndpoint = isBridge
          ? `/api/monark/transaction/${encodeURIComponent(editingTxnId)}`
          : `/api/transaction/${encodeURIComponent(editingTxnId)}`;
        fetch(txnEndpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(patch)
        }).catch(() => {});
      }
      closeTxnModal();
      renderAll();
    }

    function exportFilteredCsv() {
      const list = getFilteredTransactions();
      const rows = list.map(t => `${t.date},${t.institution},"${t.merchant_clean}","${t.category}",${t.display_amount.toFixed(2)}`);
      const blob = new Blob([["Date,Institution,Merchant,Category,Amount", ...rows].join("\n")], { type: "text/csv" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = `monark_bootleg_${globalWindow}.csv`;
      a.click();
    }

    // =========================================================================
    // 04. CASH FLOW — EXACT MULTI-STAGE GRADIENT WATERFALL SANKEY (SCREENSHOT 1)
    // =========================================================================
    function renderCashFlowView() {
      const isTK = activeProfile === "TK";
      const m = computeWindowMetrics();
      const totExp = Math.max(m.activeExpense, 1);
      const savAmt = Math.max(0, m.netCashFlow);
      const savPct = m.totalIncome > 0 ? ((savAmt / m.totalIncome) * 100).toFixed(2) : "0.00";

      let groupDefs = [];
      if (cashFlowBreakdown === "category") {
        groupDefs = [
          { key: "Savings", color: "#16A34A", ribbon: "#bbf7d0", amount: savAmt, pct: savPct, isSavings: true, subLabel: isTK ? "SoFi B200 GPU Escrow & Larry Tears Surplus" : "SoFi 2752 & Checking Surplus" },
          ...Object.entries(m.byCategory)
            .filter(([_, obj]) => obj.eff > 1)
            .sort((a, b) => b[1].eff - a[1].eff)
            .slice(0, 8)
            .map(([catName, obj]) => {
              const meta = getCatMeta(catName);
              return {
                key: catName,
                color: meta.color,
                cats: [catName],
                amount: obj.eff,
                pct: ((obj.eff / totExp) * 100).toFixed(2),
                subLabel: `${obj.count} swipes · ${meta.bucket}`
              };
            })
        ];
      } else if (cashFlowBreakdown === "bucket") {
        groupDefs = [
          { key: "Savings", color: "#16A34A", ribbon: "#bbf7d0", amount: savAmt, pct: savPct, isSavings: true, subLabel: "Net Unspent Cash Flow" },
          { key: "Fixed Expenses", color: "#F59E0B", cats: ["Housing & Rent", "Utilities & Insurance", "Subscriptions & Digital"], amount: m.byBucket["Fixed"] || 0, pct: (((m.byBucket["Fixed"] || 0) / totExp) * 100).toFixed(2), subLabel: "Rent, Utilities & Core Subscriptions" },
          { key: "Flexible Living", color: "#7C3AED", cats: ["Apparel & Luxury Shopping", "Food Delivery & Dining", "Groceries & Daily Essentials", "Rideshare & Transit", "Fitness & Wellness"], amount: m.byBucket["Flexible"] || 0, pct: (((m.byBucket["Flexible"] || 0) / totExp) * 100).toFixed(2), subLabel: "Dining, Shopping, Groceries & Transit" },
          { key: "Non-Monthly & Sinking", color: "#DB2777", cats: ["Travel, Flights & Hotels", "Electronics, Home & Retail", "Medical, Vet & Aesthetics", "Family Support, Zelle & Cash"], amount: m.byBucket["Non-Monthly"] || 0, pct: (((m.byBucket["Non-Monthly"] || 0) / totExp) * 100).toFixed(2), subLabel: "Travel, Electronics, Medical & Family" }
        ];
      } else if (cashFlowBreakdown === "institution") {
        groupDefs = [
          { key: "Savings", color: "#16A34A", ribbon: "#bbf7d0", amount: savAmt, pct: savPct, isSavings: true, subLabel: "Net Cash Flow Surplus" },
          { key: "American Express (4002)", color: "#006FCF", cats: ["Apparel & Luxury Shopping"], instKey: "amex", amount: m.byInstitution["amex"] || 0, pct: (((m.byInstitution["amex"] || 0) / totExp) * 100).toFixed(2), subLabel: isTK ? "Amex Centurion Black Card" : "Amex Delta SkyMiles Reserve (4002)" },
          { key: "Bank of America (4473/8577)", color: "#E31837", cats: ["Housing & Rent"], instKey: "bofa", amount: m.byInstitution["bofa"] || 0, pct: (((m.byInstitution["bofa"] || 0) / totExp) * 100).toFixed(2), subLabel: isTK ? "Deal Desk Checking & Jet Visa" : "BofA Checking (4473) & Visa (8577)" },
          { key: "SoFi Bank (5857/2752)", color: "#00A4E4", cats: ["Housing & Rent"], instKey: "sofi", amount: m.byInstitution["sofi"] || 0, pct: (((m.byInstitution["sofi"] || 0) / totExp) * 100).toFixed(2), subLabel: isTK ? "SoFi Larry Tears & B200 Vault" : "SoFi Checking (5857) & 311 Vault (2752)" }
        ];
      } else {
        groupDefs = [
          { key: "Savings", color: "#16A34A", ribbon: "#bbf7d0", amount: savAmt, pct: savPct, isSavings: true, subLabel: isTK ? "SoFi B200 GPU Escrow & Larry Tears Surplus" : "SoFi 2752 & Checking Surplus" },
          { key: "Housing", color: "#F59E0B", ribbon: "#fde68a", cats: ["Housing & Rent"], subLabel: isTK ? "Atherton Estate + us-west1 Dark Fiber" : "Henry Hall + Bilt 311" },
          { key: "Shopping", color: "#7C3AED", ribbon: "#ddd6fe", cats: ["Apparel & Luxury Shopping", "Electronics, Home & Retail"], subLabel: isTK ? "14 Brioni 3-Piece Suits + 8x H200 GPUs" : "Aritzia, Alo, Saks, B&H" },
          { key: "Travel & Lifestyle", color: "#9333EA", ribbon: "#e9d5ff", cats: ["Travel, Flights & Hotels", "Fitness & Wellness"], subLabel: isTK ? "Gulfstream G700 Jet Fuel & 4:30AM Cryo" : "Delta, Booking.com, Boxing" },
          { key: "Food & Dining", color: "#EF4444", ribbon: "#fecaca", cats: ["Food Delivery & Dining", "Groceries & Daily Essentials"], subLabel: isTK ? "Nobu CIO Wagyu Close & $28 Cloud Smoothies" : "Grubhub, Dining & Whole Foods" },
          { key: "Financial & Health", color: "#DB2777", ribbon: "#fbcfe8", cats: ["Family Support, Zelle & Cash", "Medical, Vet & Aesthetics"], subLabel: isTK ? "Deloitte 2,400-Slide Synergy Deck Factory" : "FX Wires, Zelle & Vet/Med" },
          { key: "Bills & Utilities", color: "#2563EB", ribbon: "#bfdbfe", cats: ["Utilities & Insurance", "Subscriptions & Digital"], subLabel: isTK ? "Oracle Audit Defense LLP + AWS Shadow IT" : "ConEd, Verizon, Geico, Apple" },
          { key: "Auto & Transport", color: "#0284C7", ribbon: "#bae6fd", cats: ["Rideshare & Transit"], subLabel: isTK ? "Uber Helicopter (SFO → Sunnyvale MP7)" : "Uber Rides & MTA NYCT" }
        ];
        groupDefs.forEach(g => {
          if (!g.isSavings) {
            g.amount = (g.cats || []).reduce((acc, c) => acc + (m.byCategory[c]?.eff || 0), 0);
            g.pct = ((g.amount / totExp) * 100).toFixed(2);
          }
        });
      }

      const activeGroups = groupDefs.filter(g => g.amount > 1);
      const totalFlowVolume = activeGroups.reduce((s, g) => s + g.amount, 0) || 1;

      let srcCursorY = 24;
      let dstCursorY = 24;
      const totalBarHeight = 360;
      const gapSpace = 10;
      const usableRightHeight = totalBarHeight - Math.max(0, activeGroups.length - 1) * gapSpace;

      const groupNodes = activeGroups.map(g => {
        const frac = g.amount / totalFlowVolume;
        const hSrc = Math.max(8, frac * totalBarHeight);
        const hDst = Math.max(12, frac * usableRightHeight);
        const node = {
          ...g,
          srcY0: srcCursorY,
          srcY1: srcCursorY + hSrc,
          srcMid: srcCursorY + hSrc / 2,
          hSrc,
          dstY0: dstCursorY,
          dstY1: dstCursorY + hDst,
          dstMid: dstCursorY + hDst / 2,
          hDst
        };
        srcCursorY += hSrc;
        dstCursorY += hDst + gapSpace;
        return node;
      });

      document.getElementById("cashFlowViewContent").innerHTML = `
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-3.5">
          <div onclick="jumpToTxnType('INCOME')" class="m-card py-4 px-5 text-center cursor-pointer hover:opacity-85" title="Click to inspect Income transactions">
            <div class="text-[19px] font-bold mono-num" style="color: var(--monarch-green);">${fmt(m.totalIncome)}</div>
            <div class="text-[10px] font-bold uppercase tracking-widest mt-1" style="color: var(--text-secondary);">TOTAL INCOME ›</div>
          </div>
          <div onclick="jumpToTxnType('EXPENSE_NET')" class="m-card py-4 px-5 text-center cursor-pointer hover:opacity-85" title="Click to inspect Expense transactions">
            <div class="text-[19px] font-bold mono-num" style="color: var(--monarch-rose);">${fmt(m.activeExpense)}</div>
            <div class="text-[10px] font-bold uppercase tracking-widest mt-1" style="color: var(--text-secondary);">TOTAL EXPENSES ›</div>
          </div>
          <div onclick="switchTab('budget')" class="m-card py-4 px-5 text-center cursor-pointer hover:opacity-85" title="Click to inspect Budget">
            <div class="text-[19px] font-bold mono-num" style="color: var(--text-primary);">${fmt(m.netCashFlow)}</div>
            <div class="text-[10px] font-bold uppercase tracking-widest mt-1" style="color: var(--text-secondary);">TOTAL NET INCOME ›</div>
          </div>
          <div onclick="switchTab('goals')" class="m-card py-4 px-5 text-center cursor-pointer hover:opacity-85" title="Click to inspect Vault &amp; Savings Goals">
            <div class="text-[19px] font-bold mono-num" style="color: var(--text-primary);">${m.savingsRate.toFixed(1)}%</div>
            <div class="text-[10px] font-bold uppercase tracking-widest mt-1" style="color: var(--text-secondary);">SAVINGS RATE ›</div>
          </div>
        </div>

        <div class="m-card p-6 space-y-4">
          <div class="flex flex-wrap items-center justify-between gap-3">
            <div>
              <div class="text-[10px] font-bold uppercase tracking-widest" style="color: var(--text-secondary);">CASH FLOW WATERFALL · CLICK ANY PERIOD OR RIBBON</div>
              <div class="mt-1">${renderInlineWindowSelector()}</div>
            </div>
            <div class="flex flex-wrap items-center gap-2">
              <select onchange="setCashFlowBreakdown(this.value)" class="px-3 py-1.5 rounded-lg text-xs font-semibold cursor-pointer" style="background: var(--bg-surface); border: 1px solid var(--border-subtle); color: var(--text-primary);" title="Switch Cash Flow Grouping">
                <option value="group" ${cashFlowBreakdown === "group" ? "selected" : ""}>By category &amp; group</option>
                <option value="category" ${cashFlowBreakdown === "category" ? "selected" : ""}>By individual category</option>
                <option value="bucket" ${cashFlowBreakdown === "bucket" ? "selected" : ""}>By Fixed / Flexible / Non-Monthly</option>
                <option value="institution" ${cashFlowBreakdown === "institution" ? "selected" : ""}>By bank / institution</option>
              </select>
              <div class="flex items-center rounded-lg p-0.5" style="background: var(--bg-elevated); border: 1px solid var(--border-subtle);">
                <button class="px-2 py-1 rounded-md text-xs font-semibold cursor-pointer" style="background: var(--bg-surface); color: var(--amethyst);" title="Sankey Waterfall View">
                  <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 5h4l7 7-7 7H3"/><path d="M14 5h7v14h-7"/></svg>
                </button>
                <button onclick="switchTab('reports')" class="px-2 py-1 rounded-md text-xs cursor-pointer" style="color: var(--text-secondary);" title="Switch to Top Merchants Table">
                  <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="13" width="3.5" height="7" rx="1"/><rect x="10.25" y="5" width="3.5" height="15" rx="1"/><rect x="16.5" y="9" width="3.5" height="11" rx="1"/></svg>
                </button>
              </div>
            </div>
          </div>

          <!-- Mobile-Native Vertical Cash Flow Waterfall (Pixel 11 Pro 412px) -->
          <div class="md:hidden space-y-2 pt-1">
            ${groupNodes.map(g => {
              const clickAct = g.isSavings
                ? "switchTab('goals')"
                : (g.instKey ? `setBankScope('${g.instKey}');switchTab('transactions')` : `jumpToCategory('${(g.cats && g.cats[0]) || "Housing & Rent"}')`);
              return `
                <div onclick="${clickAct}" class="p-3 rounded-xl flex items-center justify-between gap-3 cursor-pointer hover:opacity-85" style="background: var(--bg-elevated); border: 1px solid var(--border-subtle);">
                  <div class="min-w-0 flex-1">
                    <div class="flex items-center gap-2">
                      <span class="w-2.5 h-2.5 rounded-full flex-shrink-0" style="background:${g.color};"></span>
                      <span class="text-xs font-bold truncate">${g.key} ›</span>
                      <span class="text-[10px] mono-num" style="color: var(--text-secondary);">(${g.pct}%)</span>
                    </div>
                    <div class="text-[10.5px] truncate mt-0.5" style="color: var(--text-secondary);">${g.subLabel}</div>
                    <div class="w-full h-1.5 rounded-full overflow-hidden mt-1.5" style="background: var(--bg-surface);">
                      <div class="h-full rounded-full" style="width:${Math.min(100, parseFloat(g.pct))}%; background:${g.color};"></div>
                    </div>
                  </div>
                  <div class="text-right mono-num font-bold text-xs flex-shrink-0">${fmt(g.amount)}</div>
                </div>
              `;
            }).join("")}
          </div>

          <div class="overflow-x-auto pt-1">
            <svg viewBox="0 0 940 430" class="w-full h-auto" style="min-width: 740px;">
              <defs>
                <linearGradient id="wfGradStage1" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stop-color="#0284C7" stop-opacity="0.22"/>
                  <stop offset="100%" stop-color="#0891B2" stop-opacity="0.24"/>
                </linearGradient>
                <linearGradient id="wfGradStage2" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stop-color="#0891B2" stop-opacity="0.24"/>
                  <stop offset="100%" stop-color="#16A34A" stop-opacity="0.25"/>
                </linearGradient>
                ${groupNodes.map((g, idx) => `
                  <linearGradient id="wfBranchGrad${idx}" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stop-color="#16A34A" stop-opacity="0.22"/>
                    <stop offset="100%" stop-color="${g.color}" stop-opacity="0.26"/>
                  </linearGradient>
                  <linearGradient id="wfSubGrad${idx}" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stop-color="${g.color}" stop-opacity="0.26"/>
                    <stop offset="100%" stop-color="${g.color}" stop-opacity="0.14"/>
                  </linearGradient>
                `).join("")}
              </defs>

              <g class="cursor-pointer" onclick="jumpToTxnType('INCOME')">
                <rect x="28" y="24" width="187" height="360" fill="url(#wfGradStage1)" />
                <rect x="18" y="24" width="10" height="360" fill="#0284C7" />
                <text x="38" y="196" font-size="11.5" font-weight="500" fill="var(--text-secondary)">▲ Paychecks &amp; GSU ›</text>
                <text x="38" y="213" font-size="12" font-weight="700" fill="var(--text-primary)" class="mono-num">${fmt(m.totalIncome)} (100%)</text>

                <rect x="225" y="24" width="180" height="360" fill="url(#wfGradStage2)" />
                <rect x="215" y="24" width="10" height="360" fill="#0891B2" />
                <text x="235" y="196" font-size="11.5" font-weight="500" fill="var(--text-secondary)">Income ›</text>
                <text x="235" y="213" font-size="12" font-weight="700" fill="var(--text-primary)" class="mono-num">${fmt(m.totalIncome)} (100%)</text>
              </g>

              <rect x="405" y="24" width="10" height="360" fill="#16A34A" />

              ${groupNodes.map((g, idx) => {
                const ribbonPath = `
                  M 415 ${g.srcY0}
                  C 525 ${g.srcY0}, 530 ${g.dstY0}, 640 ${g.dstY0}
                  L 640 ${g.dstY1}
                  C 530 ${g.dstY1}, 525 ${g.srcY1}, 415 ${g.srcY1}
                  Z
                `;
                const rightPath = `
                  M 650 ${g.dstY0}
                  C 760 ${g.dstY0}, 790 ${g.dstY0}, 915 ${g.dstY0}
                  L 915 ${g.dstY1}
                  C 790 ${g.dstY1}, 760 ${g.dstY1}, 650 ${g.dstY1}
                  Z
                `;
                const labelY = g.dstMid;
                const clickAct = g.isSavings
                  ? "switchTab('goals')"
                  : (g.instKey ? `setBankScope('${g.instKey}');switchTab('transactions')` : `jumpToCategory('${(g.cats && g.cats[0]) || "Housing & Rent"}')`);
                return `
                  <g class="cursor-pointer hover:opacity-90" onclick="${clickAct}">
                    <path d="${ribbonPath}" fill="url(#wfBranchGrad${idx})" />
                    <rect x="640" y="${g.dstY0}" width="10" height="${g.hDst}" fill="${g.color}" />
                    <text x="632" y="${labelY - 3}" text-anchor="end" font-size="11" font-weight="500" fill="var(--text-secondary)">${g.key}</text>
                    <text x="632" y="${labelY + 11}" text-anchor="end" font-size="11.5" font-weight="700" fill="var(--text-primary)" class="mono-num">${fmt(g.amount)} (${g.pct}%)</text>

                    <path d="${rightPath}" fill="url(#wfSubGrad${idx})" />
                    <rect x="915" y="${g.dstY0}" width="8" height="${g.hDst}" fill="${g.color}" opacity="0.85" />
                    <text x="907" y="${labelY - 2}" text-anchor="end" font-size="10.5" font-weight="500" fill="var(--text-secondary)">${g.subLabel}</text>
                    <text x="907" y="${labelY + 11}" text-anchor="end" font-size="11" font-weight="600" fill="${g.color}" class="mono-num">${fmtInt(g.amount)}</text>
                  </g>
                `;
              }).join("")}
            </svg>
          </div>
        </div>
      `;
    }

    // =========================================================================
    // 05. BUDGET — "A budget that flexes with your life" (100% Editable Targets)
    // =========================================================================
    function renderBudgetView() {
      const isTK = activeProfile === "TK";
      const m = computeWindowMetrics();
      const baseScale = globalWindow === "60D" ? 1.8 : globalWindow === "ALL" ? 3.2 : 1.0;
      const tkScale = isTK ? 75.0 : 1.0;
      const scale = baseScale * tkScale;

      const tkDescMap = {
        "Housing & Rent": "Atherton Estate + 400Gbps MP7 Dark Fiber",
        "Apparel & Luxury Shopping": "Brioni Milan 14 Identical 3-Piece Keynote Suits",
        "Travel, Flights & Hotels": "Gulfstream G700 Jet Fuel (SJC → Davos → Tokyo)",
        "Food Delivery & Dining": "Nobu Palo Alto CIO Wagyu & French Laundry Buyout",
        "Electronics, Home & Retail": "NVIDIA 8x H200 Node + Gartner Gold-Leaf Frames",
        "Utilities & Insurance": "Oracle License Audit Defense Lawyers LLP",
        "Family Support, Zelle & Cash": "Deloitte 2,400-Slide Enterprise Synergy Deck",
        "Rideshare & Transit": "Uber Helicopter (SFO → Sunnyvale MP7 Helipad)",
        "Fitness & Wellness": "Equinox 4:30 AM Liquid Nitrogen Cryo Chamber",
        "Groceries & Daily Essentials": "Erewhon $28 Hailey Bieber Cloud Smoothies",
        "Subscriptions & Digital": "Salesforce CRM + AWS US-East-1 Shadow IT Audit"
      };

      const groups = ["Fixed", "Flexible", "Non-Monthly"].map(gName => {
        const items = Object.entries(CATEGORY_META)
          .filter(([_, cfg]) => cfg.bucket === gName && cfg.target > 0)
          .map(([name, cfg]) => {
            const actual = m.byCategory[name]?.eff || 0;
            const target = cfg.target * scale;
            const rem = target - actual;
            const pct = Math.min(100, Math.round((actual / Math.max(target, 1)) * 100));
            return { name, ...cfg, desc: isTK ? (tkDescMap[name] || cfg.desc) : cfg.desc, actual, target, rem, pct };
          });
        const totActual = items.reduce((s, x) => s + x.actual, 0);
        const totTarget = items.reduce((s, x) => s + x.target, 0);
        return { gName, items, totActual, totTarget, rem: totTarget - totActual };
      });

      document.getElementById("budgetViewContent").innerHTML = `
        <div class="m-card p-6 space-y-5">
          <div class="flex flex-wrap items-center justify-between gap-4">
            <div class="space-y-1.5">
              <div class="flex flex-wrap items-center gap-2">
                <span class="text-[11px] font-bold uppercase tracking-widest" style="color: var(--amethyst);">MONARK™ BUDGETING</span>
                ${renderInlineWindowSelector()}
              </div>
              <h2 class="text-xl sm:text-2xl font-normal" style="font-family: var(--font-serif);">A budget that flexes with your life (tap any category to view txns or tap any target amount ✎ to edit).</h2>
            </div>

            <div onclick="switchTab('cashflow')" class="px-5 py-3.5 rounded-2xl text-white flex items-center gap-6 shadow-lg cursor-pointer hover:opacity-95" style="background: linear-gradient(135deg, #7C3AED 0%, #4C1D95 100%);" title="Click to open Cash Flow Waterfall">
              <div>
                <div class="text-xs opacity-85 font-medium">Net Cash Flow / Left to Budget ›</div>
                <div class="text-[11px] opacity-75">Inflows ${fmtInt(m.totalIncome)} vs. Net Spend ${fmtInt(m.activeExpense)}</div>
              </div>
              <div class="text-2xl font-bold mono-num">${fmtInt(m.netCashFlow)}</div>
            </div>
          </div>

          <div class="space-y-5">
            ${groups.map(g => {
              const gPct = Math.min(100, Math.round((g.totActual / Math.max(g.totTarget, 1)) * 100));
              const isCol = !!collapsedBudgetGroups[g.gName];
              return `
                <div class="rounded-2xl p-4 space-y-3" style="background: var(--bg-elevated); border: 1px solid var(--border-subtle);">
                  <div onclick="toggleBudgetGroup('${g.gName}')" class="flex items-center justify-between cursor-pointer select-none hover:opacity-85" title="Tap to collapse/expand ${g.gName} Expenses">
                    <div>
                      <span class="text-sm font-bold">${isCol ? "▸" : "▾"} ${g.gName} Expenses</span>
                      <div class="text-xs mono-num mt-0.5" style="color: var(--text-secondary);">
                        <strong>${fmtInt(g.totActual)}</strong> spent of ${fmtInt(g.totTarget)} budgeted
                      </div>
                    </div>
                    <div class="text-right mono-num">
                      <span class="text-sm font-bold" style="color: ${g.rem >= 0 ? "var(--monarch-green)" : "var(--monarch-rose)"};">
                        ${fmtInt(Math.abs(g.rem))} ${g.rem >= 0 ? "left" : "over"}
                      </span>
                    </div>
                  </div>
                  <div class="w-full h-2.5 rounded-full overflow-hidden" style="background: var(--bg-surface);">
                    <div class="h-full rounded-full" style="width: ${gPct}%; background: var(--amethyst);"></div>
                  </div>

                  <div class="${isCol ? "hidden" : "divide-y"} pt-2 text-xs" style="border-color: var(--border-subtle);">
                    ${g.items.map(it => `
                      <div onclick="jumpToCategory('${it.name.replace(/'/g, "\\'")}')" class="py-2.5 flex items-center justify-between gap-3 cursor-pointer hover:opacity-85" title="Click row to view transactions · Click target amount to edit budget">
                        <div class="flex items-center gap-2.5 min-w-0 flex-1">
                          <span class="w-7 h-7 rounded-full flex items-center justify-center text-xs" style="background: ${it.color}20;">${it.icon}</span>
                          <div class="truncate">
                            <div class="font-semibold truncate">${it.name}</div>
                            <div class="text-[10px]" style="color: var(--text-secondary);">${it.desc}</div>
                          </div>
                        </div>
                        <div class="w-24 sm:w-36 h-2 rounded-full overflow-hidden" style="background: var(--bg-surface);">
                          <div class="h-full rounded-full" style="width: ${it.pct}%; background: ${it.rem >= 0 ? "var(--amethyst)" : "var(--monarch-rose)"};"></div>
                        </div>
                        <div onclick="event.stopPropagation();openBudgetEditor('${it.name.replace(/'/g, "\\'")}')" class="w-32 text-right mono-num px-2 py-1 rounded-lg hover:bg-purple-500/10" title="Click to edit ${it.name} budget target">
                          <div class="font-bold">${fmtInt(it.actual)} <span class="font-normal" style="color: var(--text-secondary);">/ ${fmtInt(it.target)}</span> <span style="color:var(--amethyst);">✎</span></div>
                        </div>
                      </div>
                    `).join("")}
                  </div>
                </div>
              `;
            }).join("")}
          </div>
        </div>
      `;
    }

    // =========================================================================
    // 06. RECURRING CALENDAR (Interactive Month Switcher & Editable Bills)
    // =========================================================================
    const RECURRING_DATA = {
      TK: {
        "2026-08": {
          2: [{ label: "Atherton HOA", amt: "-$295K" }],
          7: [{ label: "CEO Payroll", amt: "+$1.23M" }],
          14: [{ label: "Oracle Defense", amt: "-$110K" }],
          19: [{ label: "French Laundry", amt: "-$88.4K" }],
          25: [{ label: "AI Bonus Payroll", amt: "+$2.45M" }],
          27: [{ label: "Centurion 4002", amt: "-$1.18M" }]
        },
        "2026-09": {
          2: [{ label: "Erewhon Smoothies", amt: "-$11.8K" }],
          5: [{ label: "Uber Copter MP7", amt: "-$19.5K" }],
          8: [{ label: "Workday/SFDC", amt: "-$64K" }],
          15: [{ label: "CEO Payroll", amt: "+$1.23M" }],
          22: [{ label: "G700 Jet Fuel", amt: "-$215K" }],
          28: [{ label: "8x H200 GPUs", amt: "-$385K" }],
          30: [{ label: "GOOG GSU Vest", amt: "+$4.85M" }]
        },
        "2026-10": {
          1: [{ label: "Monarch Refund", amt: "+$100" }],
          2: [{ label: "Atherton HOA", amt: "-$295K" }],
          5: [{ label: "GOOG GSU Vest", amt: "+$1.95M" }],
          7: [{ label: "CEO Payroll", amt: "+$1.23M" }],
          9: [{ label: "Larry Check", amt: "+$12.50" }],
          12: [{ label: "AWS Shadow IT", amt: "-$4.2K" }],
          14: [{ label: "Oracle Defense", amt: "-$125K" }],
          17: [{ label: "Jet Visa 8577", amt: "-$384K" }],
          22: [{ label: "G700 Fuel", amt: "-$215K" }],
          27: [{ label: "Centurion 4002", amt: "-$1.42M" }],
          31: [{ label: "B200 GPU Vault", amt: "+$14.0M" }]
        },
        "2026-11": {
          2: [{ label: "Atherton HOA", amt: "-$295K" }],
          5: [{ label: "GOOG GSU Vest", amt: "+$1.95M" }],
          15: [{ label: "CEO Payroll", amt: "+$1.23M" }],
          17: [{ label: "Jet Visa 8577", amt: "-$310K" }],
          27: [{ label: "Centurion 4002", amt: "-$1.35M" }]
        }
      },
      JC: {
        "2026-08": {
          1: [{ label: "ConEd NY", amt: "-$188" }],
          2: [{ label: "Henry Hall", amt: "-$5,420" }],
          6: [{ label: "Bilt 311", amt: "-$2,918" }],
          9: [{ label: "Payroll BofA", amt: "+$2,671" }],
          17: [{ label: "BofA 8577", amt: "-$7,920" }],
          23: [{ label: "Payroll BofA", amt: "+$2,671" }],
          27: [{ label: "Amex 4002", amt: "-$16,410" }]
        },
        "2026-09": {
          1: [{ label: "ConEd NY", amt: "-$192" }],
          2: [{ label: "Henry Hall", amt: "-$5,420" }],
          3: [{ label: "MS GSU Vest", amt: "+$19,384" }],
          6: [{ label: "Bilt 311", amt: "-$2,918" }],
          11: [{ label: "Payroll BofA", amt: "+$2,671" }],
          17: [{ label: "BofA 8577", amt: "-$8,412" }],
          25: [{ label: "Payroll BofA", amt: "+$2,671" }],
          27: [{ label: "Amex 4002", amt: "-$19,120" }],
          30: [{ label: "MS GSU Vest", amt: "+$11,772" }]
        },
        "2026-10": {
          1: [{ label: "ConEd NY", amt: "-$195" }],
          2: [{ label: "Henry Hall", amt: "-$5,420" }],
          6: [{ label: "Bilt 311", amt: "-$2,918" }],
          7: [{ label: "Payroll SoFi", amt: "+$2,671" }],
          9: [{ label: "Payroll BofA", amt: "+$2,671" }],
          17: [{ label: "BofA 8577", amt: "-$8,755" }],
          21: [{ label: "Payroll SoFi", amt: "+$2,671" }],
          23: [{ label: "Payroll BofA", amt: "+$2,671" }],
          27: [{ label: "Amex 4002", amt: "-$18,748" }],
          31: [{ label: "311 Vault", amt: "+$4,582" }]
        },
        "2026-11": {
          1: [{ label: "ConEd NY", amt: "-$195" }],
          2: [{ label: "Henry Hall", amt: "-$5,420" }],
          6: [{ label: "Bilt 311 (Vault #1)", amt: "-$4,582" }],
          13: [{ label: "Payroll BofA", amt: "+$2,671" }],
          17: [{ label: "BofA 8577", amt: "-$8,500" }],
          27: [{ label: "Amex 4002", amt: "-$17,900" }]
        }
      }
    };

    const REC_MONTHS = ["2026-08", "2026-09", "2026-10", "2026-11"];
    const REC_MONTH_LABELS = {
      "2026-08": "August 2026",
      "2026-09": "September 2026",
      "2026-10": "October 2026",
      "2026-11": "November 2026 (Projected)"
    };

    function setRecurringMonth(m) {
      recurringMonth = m;
      if (["2026-08", "2026-09", "2026-10"].includes(m)) {
        globalWindow = m;
        ["2026-09", "2026-10", "60D", "2026-08", "ALL"].forEach(k => {
          const el = document.getElementById("win-" + k);
          if (el) el.className = "pill-btn border-0 py-1 px-1.5 text-[11px]" + (k === m ? " active" : "");
        });
      }
      renderRecurringView();
    }

    function stepRecurringMonth(delta) {
      const idx = REC_MONTHS.indexOf(recurringMonth);
      const nextIdx = (idx + delta + REC_MONTHS.length) % REC_MONTHS.length;
      setRecurringMonth(REC_MONTHS[nextIdx]);
    }

    function openRecurringEditor(day, evIdx = 0) {
      const profKey = activeProfile === "TK" ? "TK" : "JC";
      const monthBag = RECURRING_DATA[profKey][recurringMonth] || (RECURRING_DATA[profKey][recurringMonth] = {});
      const dayList = monthBag[day] || [];
      const existing = dayList[evIdx] || { label: "New Recurring Bill", amt: "-$150" };
      editingModalMode = "recurring";
      editingModalKey = { day: Number(day), idx: Number(evIdx), isNew: !dayList[evIdx] };

      document.getElementById("modalTitle").textContent = dayList[evIdx] ? `Edit Recurring: ${existing.label}` : `＋ Add Recurring Bill (${REC_MONTH_LABELS[recurringMonth]} Day ${day})`;
      document.getElementById("modalBody").innerHTML = `
        <div>
          <label class="block font-semibold mb-1">Recurring Bill / Payday Name</label>
          <input id="editRecLabel" type="text" value="${existing.label}" class="w-full px-3 py-2" />
        </div>
        <div class="grid grid-cols-2 gap-2.5">
          <div>
            <label class="block font-semibold mb-1">Amount (e.g. -$5,420 or +$2,671)</label>
            <input id="editRecAmt" type="text" value="${existing.amt}" class="w-full px-3 py-2 mono-num font-bold" />
          </div>
          <div>
            <label class="block font-semibold mb-1">Day of Month (1–31)</label>
            <input id="editRecDay" type="number" min="1" max="31" value="${day}" class="w-full px-3 py-2 mono-num font-bold" />
          </div>
        </div>
        <div class="pt-2 flex gap-2">
          <button onclick="closeTxnModal();jumpToAccount('${existing.label.split(' ')[0].replace(/'/g, "\\'")}')" class="pill-btn flex-1 py-2 justify-center font-semibold" style="color: var(--amethyst);">
            Matching Txns ›
          </button>
          ${dayList[evIdx] ? `<button onclick="deleteRecurringEvent()" class="pill-btn py-2 px-3 font-semibold" style="color: var(--monarch-rose);">Delete</button>` : ""}
        </div>
      `;
      document.getElementById("txnDrawerBackdrop").classList.remove("hidden");
      document.getElementById("txnDrawer").classList.remove("hidden");
    }

    function saveRecurringModalChange() {
      const profKey = activeProfile === "TK" ? "TK" : "JC";
      const monthBag = RECURRING_DATA[profKey][recurringMonth] || (RECURRING_DATA[profKey][recurringMonth] = {});
      const { day, idx, isNew } = editingModalKey;
      const newLabel = document.getElementById("editRecLabel").value.trim() || "Recurring Item";
      const newAmt = document.getElementById("editRecAmt").value.trim() || "-$100";
      const newDay = Math.min(31, Math.max(1, parseInt(document.getElementById("editRecDay").value, 10) || day));

      if (!isNew && monthBag[day] && monthBag[day][idx]) {
        monthBag[day].splice(idx, 1);
      }
      if (!monthBag[newDay]) monthBag[newDay] = [];
      monthBag[newDay].push({ label: newLabel, amt: newAmt });
      closeTxnModal();
      renderRecurringView();
    }

    function deleteRecurringEvent() {
      const profKey = activeProfile === "TK" ? "TK" : "JC";
      const monthBag = RECURRING_DATA[profKey][recurringMonth] || {};
      const { day, idx } = editingModalKey || {};
      if (monthBag[day] && monthBag[day][idx]) {
        monthBag[day].splice(idx, 1);
      }
      closeTxnModal();
      renderRecurringView();
    }

    function renderRecurringView() {
      const isTK = activeProfile === "TK";
      const profKey = isTK ? "TK" : "JC";
      const eventsByDay = RECURRING_DATA[profKey][recurringMonth] || {};
      const shortMo = (REC_MONTH_LABELS[recurringMonth] || "Oct").slice(0, 3);
      const maxDays = recurringMonth === "2026-09" || recurringMonth === "2026-11" ? 30 : 31;

      let cells = "";
      for (let i = 0; i < 4; i++) cells += `<div class="p-2 rounded-xl opacity-30 min-h-[74px]" style="background: var(--bg-elevated);"></div>`;
      for (let d = 1; d <= maxDays; d++) {
        const evs = eventsByDay[d] || [];
        cells += `
          <div onclick="openRecurringEditor(${d}, 0)" class="p-2 rounded-xl min-h-[74px] flex flex-col justify-between cursor-pointer hover:border-purple-500 transition-all" style="background: var(--bg-elevated); border: 1px solid ${d === 12 ? "var(--amethyst)" : "var(--border-subtle)"};" title="Click to edit or add recurring bill on ${shortMo} ${d}">
            <div class="flex items-center justify-between">
              <span class="mono-num text-xs font-bold">${d}</span>
              <span class="text-[9px] opacity-60">＋</span>
            </div>
            <div class="space-y-1 mt-1">
              ${evs.map((e, idx) => `<div onclick="event.stopPropagation();openRecurringEditor(${d}, ${idx})" class="text-[10px] px-1.5 py-0.5 rounded font-medium truncate hover:opacity-85" style="background: var(--bg-surface); border: 1px solid var(--border-subtle);">${e.label} <strong>${e.amt}</strong> ✎</div>`).join("")}
            </div>
          </div>
        `;
      }
      const mobileAgenda = Object.entries(eventsByDay).map(([d, evs]) =>
        evs.map((e, idx) => `
          <div onclick="openRecurringEditor(${d}, ${idx})" class="p-3 rounded-xl flex items-center justify-between cursor-pointer hover:opacity-85" style="background: var(--bg-elevated); border: 1px solid var(--border-subtle);" title="Tap to edit recurring item">
            <div class="flex items-center gap-2.5">
              <span class="w-11 h-7 rounded-lg flex items-center justify-center mono-num text-xs font-bold" style="background: var(--amethyst-soft); color: var(--amethyst);">${shortMo} ${d}</span>
              <span class="text-xs font-semibold">${e.label}</span>
            </div>
            <div class="flex items-center gap-1.5">
              <span class="mono-num text-xs font-bold" style="color: ${e.amt.startsWith('+') ? 'var(--monarch-green)' : 'var(--text-primary)'};">${e.amt}</span>
              <span class="text-xs" style="color: var(--amethyst);">✎</span>
            </div>
          </div>
        `).join("")
      ).join("");

      document.getElementById("recurringViewContent").innerHTML = `
        <div class="m-card p-5 space-y-4">
          <div class="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 class="text-base font-bold">${REC_MONTH_LABELS[recurringMonth]} Recurring Bills &amp; Payday Calendar (${isTK ? "Thomas Kurian CEO Demo" : "Live SimpleFIN"})</h3>
              <p class="text-xs" style="color: var(--text-secondary);">Tap any bill or calendar date to edit amount, move due date, or add a recurring item</p>
            </div>
            <div class="flex flex-wrap items-center gap-2">
              <div class="inline-flex items-center gap-1 rounded-lg p-0.5" style="background: var(--bg-elevated); border: 1px solid var(--border-subtle);">
                <button onclick="stepRecurringMonth(-1)" class="px-2 py-1 rounded-md text-xs font-bold cursor-pointer">◄</button>
                <select onchange="setRecurringMonth(this.value)" class="px-2.5 py-1 text-xs font-semibold cursor-pointer border-0" style="background: var(--bg-surface);">
                  ${REC_MONTHS.map(mk => `<option value="${mk}" ${recurringMonth === mk ? "selected" : ""}>${REC_MONTH_LABELS[mk]}</option>`).join("")}
                </select>
                <button onclick="stepRecurringMonth(1)" class="px-2 py-1 rounded-md text-xs font-bold cursor-pointer">►</button>
              </div>
              <button onclick="openRecurringEditor(15, 99)" class="pill-amethyst text-xs">＋ Add Bill</button>
            </div>
          </div>
          <div class="sm:hidden space-y-2">${mobileAgenda}</div>
          <div class="hidden sm:block">
            <div class="grid grid-cols-7 gap-2 text-center text-xs font-semibold mb-2" style="color: var(--text-secondary);">
              <div>Sun</div><div>Mon</div><div>Tue</div><div>Wed</div><div>Thu</div><div>Fri</div><div>Sat</div>
            </div>
            <div class="grid grid-cols-7 gap-2">${cells}</div>
          </div>
        </div>
      `;
    }

    // =========================================================================
    // 07. GOALS & SINKING VAULT (100% Interactive & Editable Vault Targets)
    // =========================================================================
    function renderGoalsView() {
      const isTK = activeProfile === "TK";
      const s = state.summary;
      const fundedPct = Math.round(((s.sofi_2752_balance || 1) / Math.max(s.lease_311_remaining_obligation || 1, 1)) * 1000) / 10;
      const unencCash = Math.max(0, state.accounts.filter(a => !a.is_liability && !a.name.includes("6725")).reduce((acc, a) => acc + a.balance, 0) - s.lease_311_remaining_obligation);
      const liabCovPct = Math.round((unencCash / Math.max(s.total_liabilities, 1)) * 1000) / 10;

      document.getElementById("goalsViewContent").innerHTML = `
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div onclick="openGoalEditor('vault')" class="m-card p-5 space-y-4 cursor-pointer hover:border-purple-500 transition-all" title="Click to edit Vault balance or locked obligation">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold uppercase px-2.5 py-1 rounded-full" style="background: var(--amethyst-soft); color: var(--amethyst);">${fundedPct}% Funded ✎</span>
              <span class="mono-num text-xs" style="color: var(--text-secondary);">${isTK ? "Delivers Q1 2027" : "Ends Feb 1, 2027"}</span>
            </div>
            <h3 class="text-base font-bold">${isTK ? "Vault #1: 2,048 NVIDIA Blackwell B200 GPU Escrow (SoFi 2752)" : "Vault #1: 311 2nd Apartment Lease Reserve (SoFi 2752)"}</h3>
            <p class="text-xs leading-relaxed" style="color: var(--text-secondary);">
              Vault Balance: <strong class="mono-num" style="color: var(--text-primary);">${fmt(s.sofi_2752_balance)}</strong> ·
              Locked Obligation: <strong class="mono-num" style="color: var(--text-primary);">${fmt(s.lease_311_remaining_obligation)}</strong> ·
              True Unencumbered Surplus: <strong class="mono-num" style="color: var(--monarch-green);">+${fmt(s.sofi_2752_true_buffer)}</strong>
            </p>
            <div class="flex items-center gap-2 pt-1">
              <button onclick="event.stopPropagation();openGoalEditor('vault')" class="pill-amethyst text-xs">✎ Edit Vault &amp; Lock Amount</button>
              <button onclick="event.stopPropagation();jumpToAccount('2752')" class="pill-btn text-xs">View Vault Txns ›</button>
            </div>
          </div>

          <div onclick="switchTab('advisor')" class="m-card p-5 space-y-4 cursor-pointer hover:border-purple-500 transition-all" title="Click to open Interactive Card Payoff Simulator">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold uppercase px-2.5 py-1 rounded-full" style="background: var(--monarch-green-soft); color: var(--monarch-green);">${liabCovPct}% Liquid Coverage</span>
              <span class="mono-num text-xs" style="color: var(--text-secondary);">Oct 17 &amp; Oct 27 Autopays</span>
            </div>
            <h3 class="text-base font-bold">${isTK ? "Goal #2: Zero-Out Centurion Float &amp; Sweep $0.42 Coffee Vault" : "Goal #2: Zero Out Credit Card Float (Amex 4002 + BofA 8577)"}</h3>
            <p class="text-xs leading-relaxed" style="color: var(--text-secondary);">
              Unencumbered Cash (<strong class="mono-num">${fmt(unencCash)}</strong>) vs. Total Credit Cards (<strong class="mono-num">-${fmt(s.total_liabilities)}</strong>) leaves <strong class="mono-num" style="color: var(--monarch-green);">+${fmt(unencCash - s.total_liabilities)}</strong> net liquid cash after 100% payoff.
            </p>
            <div class="flex items-center gap-2 pt-1">
              <button onclick="event.stopPropagation();switchTab('advisor')" class="pill-amethyst text-xs">Open Payoff Simulator ›</button>
              <button onclick="event.stopPropagation();switchTab('accounts')" class="pill-btn text-xs">Edit Card Balances ✎</button>
            </div>
          </div>
        </div>
      `;
    }

    // =========================================================================
    // 08. REPORTS & MERCHANTS (Interactive Period & Column Sort)
    // =========================================================================
    function renderReportsView() {
      const m = computeWindowMetrics();
      const byMerch = {};
      m.txns.forEach(t => {
        if (t.txn_type === "expense") {
          const k = t.merchant_clean;
          if (!byMerch[k]) byMerch[k] = { merchant: k, category: t.category, institution: t.institution, gross: 0, net: 0, refunded: 0, count: 0 };
          byMerch[k].gross += t.amount;
          byMerch[k].net += t.net_amount;
          byMerch[k].refunded += t.refunded_amount;
          if ((refundStrippedMode ? t.net_amount : t.amount) > 0.005) byMerch[k].count += 1;
        }
      });
      const list = Object.values(byMerch)
        .filter(x => (refundStrippedMode ? x.net : x.gross) > 0.01)
        .sort((a, b) => {
          if (reportsSortMode === "gross") return b.gross - a.gross;
          if (reportsSortMode === "swipes") return b.count - a.count;
          if (reportsSortMode === "refunded") return b.refunded - a.refunded;
          return b.net - a.net;
        })
        .slice(0, 18);

      document.getElementById("reportsViewContent").innerHTML = `
        <div class="m-card p-5 space-y-4">
          <div class="flex flex-wrap items-center justify-between gap-3">
            <div class="space-y-1">
              <h3 class="text-base font-bold">Top Merchants Leaderboard</h3>
              <div>${renderInlineWindowSelector()}</div>
            </div>
            <div class="flex flex-wrap items-center gap-2">
              <select onchange="reportsSortMode=this.value;renderReportsView()" class="px-3 py-1.5 rounded-lg text-xs font-semibold cursor-pointer" style="background: var(--bg-surface); border: 1px solid var(--border-subtle); color: var(--text-primary);">
                <option value="net" ${reportsSortMode === "net" ? "selected" : ""}>Sort: True Net Spend</option>
                <option value="gross" ${reportsSortMode === "gross" ? "selected" : ""}>Sort: Gross Spend</option>
                <option value="swipes" ${reportsSortMode === "swipes" ? "selected" : ""}>Sort: Swipe Count</option>
                <option value="refunded" ${reportsSortMode === "refunded" ? "selected" : ""}>Sort: Refunded Amount</option>
              </select>
              <button onclick="switchTab('cashflow')" class="pill-amethyst text-xs">View Cash Flow Waterfall ›</button>
            </div>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse text-xs">
              <thead>
                <tr class="text-[11px] uppercase" style="color: var(--text-secondary); border-bottom: 1px solid var(--border-subtle);">
                  <th class="py-2 px-3">Merchant</th>
                  <th class="py-2 px-3">Category</th>
                  <th onclick="reportsSortMode='swipes';renderReportsView()" class="py-2 px-3 text-center cursor-pointer hover:underline">Swipes ▾</th>
                  <th onclick="reportsSortMode='gross';renderReportsView()" class="py-2 px-3 text-right cursor-pointer hover:underline">Gross Spend ▾</th>
                  <th onclick="reportsSortMode='refunded';renderReportsView()" class="py-2 px-3 text-right cursor-pointer hover:underline">Refunded ▾</th>
                  <th onclick="reportsSortMode='net';renderReportsView()" class="py-2 px-3 text-right cursor-pointer hover:underline">True Net Spend ▾</th>
                </tr>
              </thead>
              <tbody class="divide-y" style="border-color: var(--border-subtle);">
                ${list.map(x => `
                  <tr onclick="jumpToAccount('${x.merchant.replace(/'/g, "\\'")}')" class="cursor-pointer hover:opacity-80" title="Click to view all transactions for ${x.merchant}">
                    <td class="py-2.5 px-3 font-semibold flex items-center gap-2.5">${getMerchantBrandAvatar(x.merchant, x.category, x.institution)} <span>${x.merchant} ›</span></td>
                    <td onclick="event.stopPropagation();jumpToCategory('${x.category.replace(/'/g, "\\'")}')" class="py-2.5 px-3 hover:underline" style="color: var(--text-secondary);">${getCatMeta(x.category).icon} ${x.category}</td>
                    <td class="py-2.5 px-3 mono-num text-center">${x.count}</td>
                    <td class="py-2.5 px-3 mono-num text-right" style="color: var(--text-secondary);">${fmt(x.gross)}</td>
                    <td class="py-2.5 px-3 mono-num text-right" style="color: var(--monarch-green);">${x.refunded > 0 ? "-" + fmt(x.refunded) : "—"}</td>
                    <td class="py-2.5 px-3 mono-num font-bold text-right">${fmt(x.net)}</td>
                  </tr>
                `).join("")}
              </tbody>
            </table>
          </div>
        </div>
      `;
    }

    // =========================================================================
    // 09. INVESTMENTS VIEW (Interactive Timeframes & Editable Holdings)
    // =========================================================================
    const HOLDINGS_DATA = {
      TK: [
        { symbol: "GOOG", name: "Alphabet Inc. Class C Capital Stock", shares: "1,420,000", price: "$198.40", value: 281728000, change: "+14.2%" },
        { symbol: "ANTH-E", name: "Anthropic PBC Series E Sovereign AI Warrants", shares: "250,000", price: "$122.68", value: 30672000, change: "+48.5%" }
      ],
      JC: [
        { symbol: "VOO", name: "Vanguard S&P 500 ETF (SoFi 6725)", shares: "5.24", price: "$518.40", value: 2716.42, change: "+11.4%" },
        { symbol: "QQQ", name: "Invesco QQQ Trust Series 1 (SoFi 6725)", shares: "2.81", price: "$495.00", value: 1390.94, change: "+13.8%" },
        { symbol: "GOOG", name: "Morgan Stanley Vested GSU Proceeds (BofA 4473)", shares: "157.00", price: "$198.44", value: 31155.50, change: "+9.6%" }
      ]
    };

    function openHoldingEditor(idx) {
      const profKey = activeProfile === "TK" ? "TK" : "JC";
      const h = HOLDINGS_DATA[profKey][idx];
      if (!h) return;
      editingModalMode = "holding";
      editingModalKey = idx;
      document.getElementById("modalTitle").textContent = `Edit Holding: ${h.symbol}`;
      document.getElementById("modalBody").innerHTML = `
        <div>
          <label class="block font-semibold mb-1">Ticker Symbol</label>
          <input id="editHoldSym" type="text" value="${h.symbol}" class="w-full px-3 py-2 mono-num font-bold" />
        </div>
        <div>
          <label class="block font-semibold mb-1">Holding Name</label>
          <input id="editHoldName" type="text" value="${h.name}" class="w-full px-3 py-2" />
        </div>
        <div class="grid grid-cols-2 gap-2.5">
          <div>
            <label class="block font-semibold mb-1">Shares</label>
            <input id="editHoldShares" type="text" value="${h.shares}" class="w-full px-3 py-2 mono-num" />
          </div>
          <div>
            <label class="block font-semibold mb-1">Market Value ($)</label>
            <input id="editHoldVal" type="number" step="0.01" value="${h.value}" class="w-full px-3 py-2 mono-num font-bold" />
          </div>
        </div>
      `;
      document.getElementById("txnDrawerBackdrop").classList.remove("hidden");
      document.getElementById("txnDrawer").classList.remove("hidden");
    }

    function saveHoldingModalChange() {
      const profKey = activeProfile === "TK" ? "TK" : "JC";
      const h = HOLDINGS_DATA[profKey][editingModalKey];
      if (h) {
        h.symbol = document.getElementById("editHoldSym").value.trim() || h.symbol;
        h.name = document.getElementById("editHoldName").value.trim() || h.name;
        h.shares = document.getElementById("editHoldShares").value.trim() || h.shares;
        h.value = Math.max(0, parseFloat(document.getElementById("editHoldVal").value) || h.value);
      }
      closeTxnModal();
      renderInvestmentsView();
    }

    function renderInvestmentsView() {
      const isTK = activeProfile === "TK";
      const profKey = isTK ? "TK" : "JC";
      const holdings = HOLDINGS_DATA[profKey];
      const invAcct = state.accounts.find(a => a.name.includes("6725"));
      const invBal = invAcct ? invAcct.balance : (isTK ? 312400000 : 4107.36);

      document.getElementById("investmentsViewContent").innerHTML = `
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div onclick="invAcct ? openAccountEditor('${invAcct.account_id}') : null" class="m-card p-5 space-y-3 cursor-pointer hover:border-purple-500 transition-all" title="Click to edit brokerage balance">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2.5">
                ${getBankLogoBadge("sofi")}
                <div>
                  <h3 class="text-base font-bold">${isTK ? "Alphabet Class C GSU &amp; Anthropic Stake (6725)" : "SoFi Self-Directed Brokerage (6725)"}</h3>
                  <div class="text-xs" style="color: var(--text-secondary);">${isTK ? "Sovereign Cloud CEO Equity &amp; AI Warrants" : "Active ETF &amp; Equity Portfolio"}</div>
                </div>
              </div>
              <span class="text-lg font-bold mono-num" style="color: var(--monarch-green);">${fmt(invBal)} ✎</span>
            </div>
            <div class="flex items-center justify-between pt-2">
              <div class="flex items-center gap-1">
                ${["1D", "1W", "1M", "3M", "YTD", "1Y", "ALL"].map(rk => `
                  <button onclick="event.stopPropagation();invRange='${rk}';renderInvestmentsView()" class="px-2 py-0.5 rounded text-[10.5px] font-semibold cursor-pointer" style="background: ${invRange === rk ? "var(--amethyst)" : "var(--bg-elevated)"}; color: ${invRange === rk ? "#fff" : "var(--text-secondary)"}; border: 0;">${rk}</button>
                `).join("")}
              </div>
              <span class="text-xs font-semibold mono-num" style="color: var(--monarch-green);">↑ ${invRange === "1D" ? "+1.4%" : (invRange === "1W" ? "+3.8%" : (invRange === "1M" ? "+10.4%" : "+28.6%"))} (${invRange})</span>
            </div>
          </div>

          <div onclick="jumpToCategory('Equity & Investment Inflows')" class="m-card p-5 space-y-3 cursor-pointer hover:border-purple-500 transition-all" title="Click to view GSU deposits in Transactions">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2.5">
                ${getMerchantBrandAvatar("Morgan Stanley", "Equity & Investment Inflows", "bofa")}
                <div>
                  <h3 class="text-base font-bold">${isTK ? "Morgan Stanley Q3/Q4 GSU Mega-Vests (BofA 4473)" : "Morgan Stanley GSU Releases (BofA 4473)"}</h3>
                  <div class="text-xs" style="color: var(--text-secondary);">Vested Equity Proceeds ›</div>
                </div>
              </div>
              <span class="text-lg font-bold mono-num" style="color: var(--amethyst);">${isTK ? "+$6,800,000.00" : "+$31,155.50"} ›</span>
            </div>
            <p class="text-xs" style="color: var(--text-secondary);">${isTK ? "Includes +$4,850,000.00 (Sep 30) and +$1,950,000.00 (Oct 5) Morgan Stanley GSU wire deposits." : "Includes +$19,383.85 (Sep 3) and +$11,771.65 (Sep 30) Morgan Stanley ACH deposits into BofA 4473."}</p>
          </div>
        </div>

        <div class="m-card p-5 space-y-3">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-bold">Portfolio Holdings (Tap any holding to edit shares or value ✎)</h3>
          </div>
          <div class="divide-y text-xs" style="border-color: var(--border-subtle);">
            ${holdings.map((h, idx) => `
              <div onclick="openHoldingEditor(${idx})" class="py-3 flex items-center justify-between cursor-pointer hover:opacity-85">
                <div>
                  <div class="font-bold text-sm mono-num">${h.symbol} <span class="text-xs font-normal" style="color: var(--text-secondary);">· ${h.name}</span></div>
                  <div class="text-[11px] mono-num" style="color: var(--text-secondary);">${h.shares} shares @ ${h.price}</div>
                </div>
                <div class="text-right mono-num">
                  <div class="font-bold text-sm">${fmt(h.value)} <span style="color:var(--amethyst);">✎</span></div>
                  <div class="text-[11px] font-semibold" style="color: var(--monarch-green);">${h.change}</div>
                </div>
              </div>
            `).join("")}
          </div>
        </div>
      `;
    }

    // =========================================================================
    // 10. ADVISOR & SOLVENCY SIMULATOR (Profile-Aware: TK vs JC)
    // =========================================================================
    let simAmexPay = activeProfile === "TK" ? 1420690.00 : 18748.24;
    let simBofaPay = activeProfile === "TK" ? 384210.00 : 8754.52;
    let simTransferToBofa = activeProfile === "TK" ? 2000000.00 : 12000.00;

    function renderAdvisorView() {
      const isTK = activeProfile === "TK";
      const bofaBase = isTK ? 14250000.00 : 23905.80;
      const sofiBase = isTK ? (19840000.00 + 46500000.00) : (12589.11 + 12259.16);
      const bofaEnd = bofaBase + simTransferToBofa - simAmexPay - simBofaPay;
      const sofiUnencLeft = sofiBase - simTransferToBofa;
      const totalLeft = bofaEnd + sofiUnencLeft;

      document.getElementById("advisorViewContent").innerHTML = `
        <div class="m-card p-5 space-y-5">
          <div>
            <h3 class="text-base font-bold">Interactive Card Payoff &amp; Account Routing Simulator (${isTK ? "TK Cloud CEO Edition" : "Live Portfolio"})</h3>
            <p class="text-xs mt-0.5" style="color: var(--text-secondary);">
              ${isTK
                ? "Test paying off your Amex Centurion Black Card ($1.42M) &amp; Gulfstream Jet Visa ($384K) while keeping your $42M NVIDIA B200 GPU Escrow untouched"
                : "Test paying both credit cards while keeping your $13,744.71 311 Lease Vault untouched"}
            </p>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div class="p-3.5 rounded-2xl" style="background: var(--bg-elevated);">
              <div class="flex justify-between font-semibold mb-2">
                <span>1. ${isTK ? "Amex Centurion (4002)" : "Amex 4002 Payment"}</span>
                <span class="mono-num">${fmt(simAmexPay)}</span>
              </div>
              <input type="range" min="${isTK ? 500000 : 18748.24}" max="${isTK ? 1420690 : 23537.49}" step="${isTK ? 10000 : 10}" value="${simAmexPay}" oninput="simAmexPay=parseFloat(this.value);renderAdvisorView()" class="w-full" />
            </div>
            <div class="p-3.5 rounded-2xl" style="background: var(--bg-elevated);">
              <div class="flex justify-between font-semibold mb-2">
                <span>2. ${isTK ? "Gulfstream Visa (8577)" : "BofA 8577 Payment"}</span>
                <span class="mono-num">${fmt(simBofaPay)}</span>
              </div>
              <input type="range" min="${isTK ? 100000 : 8754.52}" max="${isTK ? 384210 : 9913.92}" step="${isTK ? 5000 : 10}" value="${simBofaPay}" oninput="simBofaPay=parseFloat(this.value);renderAdvisorView()" class="w-full" />
            </div>
            <div class="p-3.5 rounded-2xl" style="background: var(--bg-elevated);">
              <div class="flex justify-between font-semibold mb-2">
                <span>3. ${isTK ? "SoFi Larry Tears → BofA 4473" : "SoFi → BofA 4473 Transfer"}</span>
                <span class="mono-num">${fmt(simTransferToBofa)}</span>
              </div>
              <input type="range" min="0" max="${isTK ? 25000000 : 24000}" step="${isTK ? 250000 : 500}" value="${simTransferToBofa}" oninput="simTransferToBofa=parseFloat(this.value);renderAdvisorView()" class="w-full" />
            </div>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div class="p-4 rounded-2xl" style="background: var(--bg-elevated);">
              <div class="text-xs font-semibold" style="color: var(--text-secondary);">BofA Checking (4473) After Autopays</div>
              <div class="text-xl font-bold mono-num mt-1" style="color: ${bofaEnd >= 3000 ? "var(--monarch-green)" : "var(--monarch-rose)"};">${fmt(bofaEnd, true)}</div>
            </div>
            <div class="p-4 rounded-2xl" style="background: var(--bg-elevated);">
              <div class="text-xs font-semibold" style="color: var(--text-secondary);">SoFi Unencumbered Cash Left</div>
              <div class="text-xl font-bold mono-num mt-1">${fmt(sofiUnencLeft, true)}</div>
            </div>
            <div class="p-4 rounded-2xl" style="background: var(--amethyst-soft); color: var(--amethyst);">
              <div class="text-xs font-bold">Total Unencumbered Cash Left</div>
              <div class="text-xl font-bold mono-num mt-1">${fmt(totalLeft, true)}</div>
            </div>
          </div>
        </div>
      `;
    }

    async function triggerLiveSync() {
      if (activeProfile === "TK") {
        const statusEl = document.getElementById("liveStatusText");
        if (statusEl) statusEl.textContent = "Auditing Oracle & AWS...";
        setTimeout(() => {
          if (statusEl) statusEl.textContent = "TK Demo Live";
        }, 650);
        return;
      }
      const statusEl = document.getElementById("liveStatusText");
      if (statusEl) statusEl.textContent = "Syncing SimpleFIN...";
      const isBridge = window.location.pathname.startsWith("/monark") || window.location.pathname.startsWith("/monarch");
      const syncEndpoint = isBridge ? "/api/monark/sync" : "/api/sync";
      try {
        const resp = await fetch(syncEndpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ days: 90 })
        });
        if (resp.ok) {
          const data = await resp.json();
          if (data.dataset) {
            state = data.dataset;
            renderAll();
          }
        }
      } catch (e) {}
      setTimeout(() => {
        if (statusEl) statusEl.textContent = "SimpleFIN Live";
      }, 600);
    }

    function toggleTheme() {
      const root = document.documentElement;
      const isDark = root.getAttribute("data-theme") === "dark";
      const next = isDark ? "light" : "dark";
      root.setAttribute("data-theme", next);
      const iconEl = document.getElementById("themeIcon");
      if (iconEl) {
        iconEl.innerHTML = next === "dark"
          ? `<svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>`
          : `<svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>`;
      }
    }

    function renderAll() {
      renderProfileControls();
      renderDashboard();
      renderAccountsView();
      renderTransactionsTable();
      renderCashFlowView();
      renderBudgetView();
      renderRecurringView();
      renderGoalsView();
      renderReportsView();
      renderInvestmentsView();
      renderAdvisorView();
    }

    renderAll();
  </script>
</body>
</html>
"""


def main() -> None:
    ds_raw = DATASET_PATH.read_text(encoding="utf-8")
    html_out = HTML_TEMPLATE.replace("__MONARCH_DATASET_JSON__", ds_raw)

    INDEX_OUT.write_text(html_out, encoding="utf-8")
    MOBILE_BRIDGE_OUT.write_text(html_out, encoding="utf-8")
    MOBILE_BRIDGE_LEGACY_OUT.write_text(html_out, encoding="utf-8")
    CURRENT_ARTIFACT_OUT.parent.mkdir(parents=True, exist_ok=True)
    CURRENT_ARTIFACT_OUT.write_text(html_out, encoding="utf-8")
    if ARTIFACT_OUT.parent.exists():
        ARTIFACT_OUT.write_text(html_out, encoding="utf-8")

    meta = {
        "summary": "Monark™ (Moth-Ark Bootleg Finance OS — $0/yr Parody Edition) Web & Mobile iOS/Android/Pixel 11 Pro PWA Application. Replicates 100% of the 4-Stage Gradient Waterfall Alluvial Cash Flow Sankey diagram + mobile vertical waterfall, cumulative spending chart with $0 zero-line and negative dip support, collapsible account groups with inline sparklines, and official circular company/bank logos — all with zero $99.99/yr VC subscription fees.",
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "userFacing": True,
    }
    CURRENT_ARTIFACT_META_OUT.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    if ARTIFACT_META_OUT.parent.exists():
        ARTIFACT_META_OUT.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Wrote {INDEX_OUT} ({len(html_out):,} bytes)")
    print(f"Wrote {MOBILE_BRIDGE_OUT} ({len(html_out):,} bytes)")
    print(f"Wrote {CURRENT_ARTIFACT_OUT} ({len(html_out):,} bytes)")


if __name__ == "__main__":
    main()
