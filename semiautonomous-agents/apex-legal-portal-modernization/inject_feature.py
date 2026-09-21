#!/usr/bin/env python3
"""
inject_feature.py
Modular Feature Injection Engine for Apex Global Law LLP Portal Modernization Showcase.
Enables instant live toggling between:
- reset: Pristine baseline corporate portal (legacy enterprise CMS layout)
- modern_header_ux: Glassmorphic Global Deal Mega-Menu & Interactive Precedent Bar
- modern_header_ai: Intelligent Precedent Navigator (Dynamic Dock 480px -> 760px, <10ms autocomplete & Gemini 3.8 Flash)
- ai_advisor: Floating 24/7 Apex Deal Intelligence AI Advisor in bottom-right corner
- ai_multimodal_deal: Multimodal Term Sheet & Credit Agreement Covenant Analyzer
"""

import sys
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
SITE_DIR = BASE_DIR / "site"
INDEX_HTML = SITE_DIR / "index.html"
PRISTINE_HTML = SITE_DIR / "index.pristine.html"


# ---------------------------------------------------------------------------
# Feature Snippet: Modern UX/UI Header & Deal Navigation
# ---------------------------------------------------------------------------
SNIPPET_MODERN_UX = """
<!-- APEX MODERNIZED EXECUTIVE DEAL COCKPIT (UX/UI ACT) -->
<style>
  .apex-legacy-masthead {
    display: none !important;
  }
  .apex-modern-nav {
    position: sticky;
    top: 0;
    z-index: 9999;
    background: rgba(10, 25, 47, 0.94);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-bottom: 1px solid rgba(212, 175, 55, 0.28);
    box-shadow: 0 10px 30px -10px rgba(2, 12, 27, 0.7);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #e6f1ff;
    padding: 14px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 24px;
    transition: all 0.3s ease;
  }
  .apex-brand {
    display: flex;
    align-items: center;
    gap: 14px;
    text-decoration: none;
    flex-shrink: 0;
  }
  .apex-logo-text {
    font-size: 19px;
    font-weight: 800;
    letter-spacing: 2px;
    color: #ffffff;
    text-transform: uppercase;
  }
  .apex-gold-badge {
    background: linear-gradient(135deg, #d4af37 0%, #aa820a 100%);
    color: #0a192f;
    font-size: 11px;
    font-weight: 800;
    padding: 3px 9px;
    border-radius: 999px;
    text-transform: uppercase;
    letter-spacing: 1px;
  }
  .apex-nav-links {
    display: flex;
    gap: 20px;
    align-items: center;
    list-style: none;
    margin: 0;
    padding: 0;
  }
  .apex-nav-item {
    position: relative;
    cursor: pointer;
  }
  .apex-nav-btn {
    color: #ccd6f6;
    font-size: 14px;
    font-weight: 600;
    letter-spacing: 0.4px;
    text-decoration: none;
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 12px;
    border-radius: 6px;
    transition: all 0.2s ease;
  }
  .apex-nav-btn:hover {
    color: #d4af37;
    background: rgba(212, 175, 55, 0.08);
  }
  .apex-mega-dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    width: 330px;
    background: #0b1d3a;
    border: 1px solid rgba(212, 175, 55, 0.24);
    border-radius: 10px;
    padding: 16px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.55);
    display: none;
    flex-direction: column;
    gap: 10px;
    z-index: 10000;
  }
  .apex-nav-item:hover .apex-mega-dropdown {
    display: flex;
  }
  .apex-drop-item {
    padding: 9px 12px;
    border-radius: 6px;
    text-decoration: none;
    transition: background 0.2s;
  }
  .apex-drop-item:hover {
    background: rgba(212, 175, 55, 0.12);
  }
  .apex-drop-title {
    color: #ffffff;
    font-size: 13px;
    font-weight: 700;
  }
  .apex-drop-desc {
    color: #8892b0;
    font-size: 11px;
    margin-top: 2px;
  }
  .apex-cta-group {
    display: flex;
    gap: 12px;
    align-items: center;
    flex-shrink: 0;
  }
  .apex-action-btn {
    background: linear-gradient(135deg, #1e3a8a, #0d214d);
    border: 1px solid #d4af37;
    color: #d4af37;
    font-size: 12px;
    font-weight: 700;
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
  }
  .apex-action-btn:hover {
    background: #d4af37;
    color: #0a192f;
    box-shadow: 0 0 15px rgba(212, 175, 55, 0.4);
  }
  .apex-ticker-bar {
    background: #071326;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    padding: 9px 32px;
    display: flex;
    gap: 32px;
    font-size: 12px;
    color: #8892b0;
    overflow-x: auto;
    white-space: nowrap;
  }
  .apex-ticker-item {
    display: flex;
    gap: 8px;
    align-items: center;
  }
  .apex-ticker-highlight {
    color: #d4af37;
    font-weight: 700;
  }
</style>

<div class="apex-modern-nav">
  <a href="/" class="apex-brand">
    <span class="apex-logo-text">APEX GLOBAL LAW</span>
    <span class="apex-gold-badge">Deal Cockpit</span>
  </a>

  <ul class="apex-nav-links">
    <li class="apex-nav-item">
      <a href="/practices/banking-and-finance" class="apex-nav-btn">Banking &amp; Finance &#9662;</a>
      <div class="apex-mega-dropdown">
        <a href="/practices/banking-and-finance" class="apex-drop-item">
          <div class="apex-drop-title">Syndicated Loans &amp; Debt Facilities</div>
          <div class="apex-drop-desc">Cross-border credit facilities &amp; investment-grade debt.</div>
        </a>
        <a href="/practices/private-credit" class="apex-drop-item">
          <div class="apex-drop-title">Private Credit &amp; Direct Lending</div>
          <div class="apex-drop-desc">Unitranche, mezzanine, and alternative capital financings.</div>
        </a>
      </div>
    </li>
    <li class="apex-nav-item">
      <a href="/practices/mergers-and-acquisitions" class="apex-nav-btn">M&amp;A &amp; Private Equity &#9662;</a>
      <div class="apex-mega-dropdown">
        <a href="/practices/mergers-and-acquisitions" class="apex-drop-item">
          <div class="apex-drop-title">Public &amp; Private Takeovers</div>
          <div class="apex-drop-desc">Delaware Chancery tested cross-border mergers.</div>
        </a>
        <a href="/practices/private-equity" class="apex-drop-item">
          <div class="apex-drop-title">Sponsor Leveraged Buyouts</div>
          <div class="apex-drop-desc">Full lifecycle fund sponsor advisory and portfolio exits.</div>
        </a>
      </div>
    </li>
    <li class="apex-nav-item">
      <a href="/practices/restructuring" class="apex-nav-btn">Restructuring &amp; Special Situations &#9662;</a>
      <div class="apex-mega-dropdown">
        <a href="/practices/restructuring" class="apex-drop-item">
          <div class="apex-drop-title">Chapter 11 Reorganizations</div>
          <div class="apex-drop-desc">Market-defining debtor and creditor committee counsel.</div>
        </a>
        <a href="/practices/liability-management" class="apex-drop-item">
          <div class="apex-drop-title">Liability Management &amp; Debt Exchanges</div>
          <div class="apex-drop-desc">Out-of-court consensual restructuring and uptiers.</div>
        </a>
      </div>
    </li>
  </ul>

  <div class="apex-cta-group">
    <a href="/precedents/biopharma-carveout" class="apex-action-btn">Precedent Vault</a>
    <button class="apex-action-btn" style="background:#d4af37; color:#0a192f;" onclick="if(window.openMultimodalModal){openMultimodalModal();}else{alert('Run Step 5 (inject ai_multimodal_deal) to enable Multimodal Term Sheet Pre-Clearance.');}">Pre-Clear Term Sheet</button>
  </div>
</div>

<div class="apex-ticker-bar">
  <div class="apex-ticker-item">
    <span>LATEST CLOSING:</span>
    <span class="apex-ticker-highlight">$12.4B Biopharma Carve-Out (Apex / Helios BioSciences)</span>
  </div>
  <div class="apex-ticker-item">
    <span>SYNDICATED FACILITY:</span>
    <span class="apex-ticker-highlight">$8.5B Multi-Currency Cov-Lite Credit Agreement</span>
  </div>
  <div class="apex-ticker-item">
    <span>DELAWARE CHANCERY:</span>
    <span class="apex-ticker-highlight">MAE Benchmark Clearance Confirmed</span>
  </div>
  <div class="apex-ticker-item">
    <span>AI GOVERNANCE:</span>
    <span class="apex-ticker-highlight">Schrems II + Zero-Retention Standard Adopted</span>
  </div>
</div>
<!-- END APEX MODERNIZED EXECUTIVE DEAL COCKPIT -->
"""


# ---------------------------------------------------------------------------
# Feature Snippet: Intelligent Precedent Navigator (AI Search + Gemini 3.8 Flash)
# ---------------------------------------------------------------------------
SNIPPET_MODERN_AI = """
<!-- APEX INTELLIGENT PRECEDENT NAVIGATOR (AI ACT) -->
<style>
  .apex-ai-dock-container {
    display: flex;
    justify-content: center;
    position: relative;
    margin-top: 18px;
    margin-bottom: 10px;
    z-index: 10001;
  }
  .apex-ai-dock {
    width: 480px;
    background: rgba(15, 23, 42, 0.96);
    border: 1.5px solid #d4af37;
    border-radius: 999px;
    padding: 9px 18px;
    display: flex;
    align-items: center;
    gap: 12px;
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.6), 0 0 20px rgba(212, 175, 55, 0.25);
    transition: width 0.35s cubic-bezier(0.16, 1, 0.3, 1), border-radius 0.35s ease;
  }
  .apex-ai-dock.expanded {
    width: 760px;
    border-radius: 20px;
  }
  .apex-ai-input {
    flex: 1;
    background: transparent;
    border: none;
    outline: none;
    color: #ffffff;
    font-size: 14px;
    font-weight: 500;
  }
  .apex-ai-input::placeholder {
    color: #94a3b8;
  }
  .apex-ai-badge {
    background: rgba(212, 175, 55, 0.18);
    color: #fbbf24;
    border: 1px solid rgba(212, 175, 55, 0.4);
    font-size: 10px;
    font-weight: 800;
    padding: 4px 8px;
    border-radius: 6px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    white-space: nowrap;
  }
  .apex-ai-results-panel {
    position: absolute;
    top: 56px;
    width: 760px;
    background: #0f172a;
    border: 1px solid rgba(212, 175, 55, 0.32);
    border-radius: 14px;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.85);
    padding: 20px;
    display: none;
    flex-direction: column;
    gap: 14px;
    color: #f1f5f9;
  }
  .apex-ai-synthesis-box {
    background: rgba(30, 41, 59, 0.75);
    border-left: 3px solid #d4af37;
    padding: 12px 16px;
    border-radius: 6px;
    font-size: 13px;
    line-height: 1.6;
    color: #e2e8f0;
  }
  .apex-ai-card-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }
  .apex-ai-card {
    background: #1e293b;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 12px;
    text-decoration: none;
    display: flex;
    flex-direction: column;
    gap: 4px;
    transition: transform 0.2s, border-color 0.2s;
  }
  .apex-ai-card:hover {
    transform: translateY(-2px);
    border-color: #d4af37;
  }
  .apex-ai-card-title {
    color: #ffffff;
    font-size: 13px;
    font-weight: 700;
  }
  .apex-ai-card-meta {
    color: #d4af37;
    font-size: 11px;
    font-weight: 600;
  }
  .apex-ai-card-desc {
    color: #94a3b8;
    font-size: 11px;
    line-height: 1.4;
  }
</style>

<div class="apex-ai-dock-container">
  <div id="apexDock" class="apex-ai-dock">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#d4af37" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
    <input
      type="text"
      id="apexSearchInput"
      class="apex-ai-input"
      placeholder="Search Apex precedents (e.g. 'carve-out', 'Schrems II', 'syndicated facility', 'MAE clause')..."
      onfocus="expandDock()"
      oninput="handleSearchInput(this.value)"
    />
    <span class="apex-ai-badge">Gemini 3.8 Flash</span>
  </div>

  <div id="apexSearchResults" class="apex-ai-results-panel">
    <div style="display:flex; justify-content:space-between; align-items:center;">
      <span style="font-size:12px; font-weight:700; color:#d4af37; text-transform:uppercase; letter-spacing:1px;">
        Apex Grounded Precedent Intelligence
      </span>
      <span id="apexLatencyBadge" style="font-size:11px; color:#94a3b8;">Latency: &lt;10ms autocomplete</span>
    </div>

    <div id="apexSynthesis" class="apex-ai-synthesis-box">
      Type a deal term or precedent topic to activate real-time grounded search...
    </div>

    <div id="apexCards" class="apex-ai-card-grid"></div>
  </div>
</div>

<script>
  let searchTimeout = null;

  function expandDock() {
    document.getElementById('apexDock').classList.add('expanded');
    document.getElementById('apexSearchResults').style.display = 'flex';
  }

  function handleSearchInput(val) {
    if (!val || val.trim().length === 0) {
      document.getElementById('apexSearchResults').style.display = 'none';
      document.getElementById('apexDock').classList.remove('expanded');
      return;
    }
    expandDock();

    fetch('/api/suggest?q=' + encodeURIComponent(val))
      .then(r => r.json())
      .then(data => {
        renderSuggestions(data.suggestions || []);
      })
      .catch(e => console.error(e));

    document.getElementById('apexSynthesis').innerHTML = `
      <div style="display:flex; align-items:center; gap:10px; color:#d4af37;">
        <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#d4af37; box-shadow:0 0 8px #d4af37;"></span>
        <span style="font-size:12.5px;"><strong>Gemini 3.8 Flash</strong> is analyzing Apex Global Law deal precedents...</span>
      </div>
    `;

    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      document.getElementById('apexLatencyBadge').innerText = 'Querying Gemini 3.8 Flash...';
      fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: val })
      })
      .then(r => r.json())
      .then(data => {
        document.getElementById('apexLatencyBadge').innerText = 'Grounded Synthesis Complete (' + (data.latency_ms || '320') + 'ms)';
        document.getElementById('apexSynthesis').innerHTML = `
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
            <span style="color:#d4af37; font-weight:700; font-size:11.5px; text-transform:uppercase; letter-spacing:0.8px;">
              Executive Precedent Brief (Gemini 3.8 Flash)
            </span>
            <span style="color:#10b981; font-size:11px; font-weight:600;">
              Verified Grounding
            </span>
          </div>
          <div style="color:#f8fafc; font-size:13px; line-height:1.6; font-weight:400;">
            ${data.synthesis}
          </div>
        `;
      })
      .catch(e => {
        console.error(e);
        document.getElementById('apexSynthesis').innerHTML = '<strong>Executive Brief:</strong> Apex Global Law LLP consistently acts as lead counsel on transformative cross-border M&amp;A, syndicated finance, and corporate restructuring mandates.';
      });
    }, 280);
  }

  function renderSuggestions(items) {
    const grid = document.getElementById('apexCards');
    grid.innerHTML = '';
    items.forEach(it => {
      const card = document.createElement('a');
      card.className = 'apex-ai-card';
      card.href = it.url;
      card.innerHTML = `
        <div class="apex-ai-card-meta">${it.category || 'Practice'}</div>
        <div class="apex-ai-card-title">${it.label || it.title}</div>
        <div class="apex-ai-card-desc">Grounded Apex Global Law precedent and deal authority benchmark.</div>
      `;
      grid.appendChild(card);
    });
  }

  document.addEventListener('click', (e) => {
    if (!e.target.closest('.apex-ai-dock-container')) {
      const panel = document.getElementById('apexSearchResults');
      const dock = document.getElementById('apexDock');
      if (panel) panel.style.display = 'none';
      if (dock) dock.classList.remove('expanded');
    }
  });
</script>
<!-- END APEX INTELLIGENT PRECEDENT NAVIGATOR -->
"""


# ---------------------------------------------------------------------------
# Feature Snippet: Floating 24/7 Apex Deal AI Advisor (Advisor Act)
# ---------------------------------------------------------------------------
SNIPPET_AI_ADVISOR = r"""
<!-- APEX 24/7 DEAL INTELLIGENCE ADVISOR (ADVISOR ACT) -->
<style>
  .apex-floating-btn {
    position: fixed;
    bottom: 28px;
    right: 28px;
    z-index: 10002;
    background: linear-gradient(135deg, #0a192f 0%, #172a45 100%);
    border: 2px solid #d4af37;
    color: #d4af37;
    border-radius: 999px;
    padding: 12px 22px;
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 0.5px;
    display: flex;
    align-items: center;
    gap: 10px;
    cursor: pointer;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5), 0 0 15px rgba(212, 175, 55, 0.3);
    transition: all 0.25s ease;
  }
  .apex-floating-btn:hover {
    transform: scale(1.05);
    background: #d4af37;
    color: #0a192f;
  }
  .apex-advisor-drawer {
    position: fixed;
    bottom: 90px;
    right: 28px;
    width: 420px;
    height: 560px;
    background: #0b1526;
    border: 1.5px solid rgba(212, 175, 55, 0.4);
    border-radius: 16px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.85);
    z-index: 10003;
    display: none;
    flex-direction: column;
    overflow: hidden;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }
  .apex-advisor-header {
    background: #07101e;
    padding: 14px 18px;
    border-bottom: 1px solid rgba(212, 175, 55, 0.25);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .apex-advisor-title {
    color: #ffffff;
    font-size: 14px;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .apex-status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #10b981;
    box-shadow: 0 0 8px #10b981;
  }
  .apex-advisor-messages {
    flex: 1;
    padding: 16px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  .apex-msg-bubble {
    max-width: 86%;
    padding: 10px 14px;
    border-radius: 10px;
    font-size: 13px;
    line-height: 1.5;
  }
  .apex-msg-bot {
    align-self: flex-start;
    background: #1e293b;
    color: #e2e8f0;
    border: 1px solid rgba(255, 255, 255, 0.08);
  }
  .apex-msg-user {
    align-self: flex-end;
    background: #1e3a8a;
    color: #ffffff;
  }
  .apex-chips-bar {
    display: flex;
    gap: 8px;
    overflow-x: auto;
    padding: 10px 16px;
    background: #091322;
    border-top: 1px solid rgba(212, 175, 55, 0.15);
    scrollbar-width: none;
  }
  .apex-chips-bar::-webkit-scrollbar {
    display: none;
  }
  .apex-chip {
    background: rgba(212, 175, 55, 0.12);
    color: #d4af37;
    border: 1px solid rgba(212, 175, 55, 0.35);
    font-size: 11.5px;
    font-weight: 600;
    padding: 6px 12px;
    border-radius: 999px;
    white-space: nowrap;
    cursor: pointer;
    user-select: none;
    transition: all 0.2s ease;
  }
  .apex-chip:hover {
    background: #d4af37;
    color: #0a192f;
    box-shadow: 0 0 10px rgba(212, 175, 55, 0.35);
  }
  .apex-chip.disabled {
    opacity: 0.45;
    pointer-events: none;
  }
  .apex-advisor-inputbar {
    padding: 12px 16px;
    background: #07101e;
    border-top: 1px solid rgba(212, 175, 55, 0.2);
    display: flex;
    gap: 10px;
  }
  .apex-chat-input {
    flex: 1;
    background: #131f33;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    color: #ffffff;
    padding: 8px 12px;
    font-size: 13px;
    outline: none;
  }
  .apex-chat-send {
    background: #d4af37;
    border: none;
    border-radius: 8px;
    color: #0a192f;
    font-weight: 700;
    padding: 8px 16px;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  .apex-chat-send:hover {
    background: #f3ce5a;
  }
</style>

<button class="apex-floating-btn" onclick="toggleAdvisor()">
  <span class="apex-status-dot"></span>
  <span>Apex Deal Advisor 24/7</span>
</button>

<div id="apexAdvisorDrawer" class="apex-advisor-drawer">
  <div class="apex-advisor-header">
    <div class="apex-advisor-title">
      <span class="apex-status-dot"></span>
      <span>Apex Deal &amp; Regulatory AI Advisor</span>
    </div>
    <button onclick="toggleAdvisor()" style="background:none; border:none; color:#94a3b8; font-size:18px; cursor:pointer;">&#10005;</button>
  </div>

  <div id="apexAdvisorMessages" class="apex-advisor-messages">
    <div class="apex-msg-bubble apex-msg-bot">
      Welcome to the <strong>Apex Deal Intelligence AI Advisor</strong> (Gemini 3.8 Flash).<br><br>
      How can I assist your transaction today? Query M&amp;A carve-out precedents, credit agreement covenants, or cross-border antitrust clearance timetables.
    </div>
  </div>

  <div class="apex-chips-bar">
    <span class="apex-chip" onclick="askChip('Analyze Delaware MAE standards for pending buyout')">Delaware MAE Standards</span>
    <span class="apex-chip" onclick="askChip('Check Schrems II cross-border data transfer clause')">Schrems II Transfer</span>
    <span class="apex-chip" onclick="askChip('Summarize cov-lite syndicated debt protections')">Cov-Lite Facilities</span>
  </div>

  <div class="apex-advisor-inputbar">
    <input type="text" id="apexChatInput" class="apex-chat-input" placeholder="Ask about deals, covenants, precedents..." onkeypress="if(event.key==='Enter') sendAdvisorMsg()" />
    <button id="apexChatSendBtn" class="apex-chat-send" onclick="sendAdvisorMsg()">Send</button>
  </div>
</div>

<script>
  let advisorPending = false;

  function toggleAdvisor() {
    const d = document.getElementById('apexAdvisorDrawer');
    d.style.display = d.style.display === 'flex' ? 'none' : 'flex';
  }

  function askChip(txt) {
    if (advisorPending) return;
    document.getElementById('apexChatInput').value = txt;
    sendAdvisorMsg();
  }

  function formatAdvisorMarkdown(text) {
    if (!text) return '';
    return text
      .replace(/^### (.*$)/gim, '<div style="font-weight:700; color:#d4af37; font-size:13px; margin:6px 0 2px;">$1</div>')
      .replace(/^## (.*$)/gim, '<div style="font-weight:700; color:#d4af37; font-size:13.5px; margin:8px 0 3px;">$1</div>')
      .replace(/\*\*(.*?)\*\*/g, '<strong style="color:#ffffff;">$1</strong>')
      .replace(/\*(.*?)\*/g, '<em style="color:#d4af37;">$1</em>')
      .replace(/^\s*[\*\-]\s+(.*$)/gim, '<li style="margin-left:14px; margin-bottom:5px; line-height:1.45;">$1</li>')
      .replace(/^\s*\d+\.\s+(.*$)/gim, '<li style="margin-left:14px; margin-bottom:5px; line-height:1.45;">$1</li>')
      .replace(/\n\n/g, '<div style="height:6px;"></div>')
      .replace(/\n/g, '<br>');
  }

  function sendAdvisorMsg() {
    if (advisorPending) return;
    const inp = document.getElementById('apexChatInput');
    const sendBtn = document.getElementById('apexChatSendBtn');
    const chips = document.querySelectorAll('.apex-chip');
    const val = inp.value.trim();
    if (!val) return;

    inp.value = '';
    advisorPending = true;
    inp.disabled = true;
    if (sendBtn) {
      sendBtn.disabled = true;
      sendBtn.innerText = '...';
    }
    chips.forEach(c => c.classList.add('disabled'));

    const container = document.getElementById('apexAdvisorMessages');
    const userBubble = document.createElement('div');
    userBubble.className = 'apex-msg-bubble apex-msg-user';
    userBubble.innerText = val;
    container.appendChild(userBubble);

    const botLoading = document.createElement('div');
    botLoading.className = 'apex-msg-bubble apex-msg-bot';
    botLoading.innerHTML = `
      <div style="display:flex; align-items:center; gap:8px; color:#d4af37;">
        <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#d4af37; box-shadow:0 0 8px #d4af37;"></span>
        <span style="font-size:12.5px;">Analyzing precedents with Gemini 3.8 Flash...</span>
      </div>
    `;
    container.appendChild(botLoading);
    container.scrollTop = container.scrollHeight;

    fetch('/api/advisor', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: val })
    })
    .then(r => r.json())
    .then(data => {
      botLoading.innerHTML = formatAdvisorMarkdown(data.reply);
      container.scrollTop = container.scrollHeight;
    })
    .catch(() => {
      botLoading.innerText = 'Error connecting to Apex Deal AI Advisor.';
    })
    .finally(() => {
      advisorPending = false;
      inp.disabled = false;
      if (sendBtn) {
        sendBtn.disabled = false;
        sendBtn.innerText = 'Send';
      }
      chips.forEach(c => c.classList.remove('disabled'));
      inp.focus();
    });
  }
</script>
<!-- END APEX 24/7 DEAL INTELLIGENCE ADVISOR -->
"""


# ---------------------------------------------------------------------------
# Feature Snippet: Multimodal Term Sheet & Credit Analyzer (Multimodal Act)
# ---------------------------------------------------------------------------
SNIPPET_MULTIMODAL = """
<!-- APEX MULTIMODAL TERM SHEET & CREDIT ANALYZER (ACT 5) -->
<style>
  .apex-modal-backdrop {
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(4, 9, 20, 0.88);
    backdrop-filter: blur(12px);
    z-index: 10005;
    display: none;
    align-items: center;
    justify-content: center;
  }
  .apex-modal-card {
    width: 820px;
    max-width: 94vw;
    max-height: 85vh;
    background: #0b172a;
    border: 2px solid #d4af37;
    border-radius: 16px;
    box-shadow: 0 30px 80px rgba(0, 0, 0, 0.9);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    color: #f1f5f9;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }
  .apex-modal-header {
    background: #060d1a;
    padding: 18px 24px;
    border-bottom: 1px solid rgba(212, 175, 55, 0.3);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .apex-modal-body {
    padding: 24px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 20px;
  }
  .apex-laser-scan-box {
    border: 2px dashed rgba(212, 175, 55, 0.5);
    background: rgba(15, 23, 42, 0.6);
    border-radius: 10px;
    padding: 24px;
    text-align: center;
    position: relative;
    overflow: hidden;
  }
  .apex-laser-beam {
    position: absolute;
    top: 0; left: 0; width: 100%; height: 3px;
    background: linear-gradient(90deg, transparent, #d4af37, #ffffff, #d4af37, transparent);
    box-shadow: 0 0 15px #d4af37;
    animation: laserScan 2.4s infinite ease-in-out;
  }
  @keyframes laserScan {
    0% { top: 0; opacity: 0.2; }
    50% { top: 100%; opacity: 1; }
    100% { top: 0; opacity: 0.2; }
  }
  .apex-covenant-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
  }
  .apex-covenant-table th {
    background: #0f223d;
    color: #d4af37;
    padding: 10px 14px;
    text-align: left;
    border-bottom: 1px solid rgba(212, 175, 55, 0.3);
  }
  .apex-covenant-table td {
    padding: 10px 14px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  }
  .apex-status-pill {
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 700;
  }
  .pill-pass { background: rgba(16, 185, 129, 0.2); color: #10b981; }
  .pill-flag { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }
</style>

<div id="apexMultimodalModal" class="apex-modal-backdrop">
  <div class="apex-modal-card">
    <div class="apex-modal-header">
      <div>
        <h3 style="margin:0; font-size:16px; color:#ffffff; font-weight:700;">
          Multimodal Term Sheet &amp; Credit Covenant Analyzer
        </h3>
        <span style="font-size:12px; color:#d4af37;">Gemini 3.8 Flash Vision &bull; Ethical Wall Clearance Harness</span>
      </div>
      <button onclick="closeMultimodalModal()" style="background:none; border:none; color:#94a3b8; font-size:20px; cursor:pointer;">&#10005;</button>
    </div>

    <div class="apex-modal-body">
      <div class="apex-laser-scan-box">
        <div class="apex-laser-beam"></div>
        <div style="font-weight:700; color:#ffffff; font-size:14px;">Term Sheet: Helios Global Biopharma Acquisition Corp</div>
        <div style="font-size:12px; color:#94a3b8; margin-top:4px;">$850,000,000 Senior Secured Credit Facility &bull; 14 Pages Scanned</div>
      </div>

      <div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
          <h4 style="margin:0; font-size:13px; color:#d4af37; text-transform:uppercase; letter-spacing:1px;">
            Extracted Key Covenants &amp; Ethical Wall Status
          </h4>
          <span class="apex-status-pill pill-pass">ETHICAL WALL: CLEARED (MATTER-APEX-9042)</span>
        </div>

        <table class="apex-covenant-table">
          <thead>
            <tr>
              <th>Covenant Name</th>
              <th>Extracted Threshold</th>
              <th>Compliance Status</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Total Net Leverage Ratio</strong></td>
              <td>Max 4.75x (0.50x acquisition holiday)</td>
              <td><span class="apex-status-pill pill-pass">COMPLIANT</span></td>
            </tr>
            <tr>
              <td><strong>Interest Coverage Ratio</strong></td>
              <td>Min 3.00x Consolidated EBITDA</td>
              <td><span class="apex-status-pill pill-pass">COMPLIANT</span></td>
            </tr>
            <tr>
              <td><strong>Negative Pledge / Debt Incurrence</strong></td>
              <td>Restricted (15% general basket allowance)</td>
              <td><span class="apex-status-pill pill-flag">FLAG FOR PARTNER REVIEW</span></td>
            </tr>
            <tr>
              <td><strong>Change of Control Put</strong></td>
              <td>101% redemption offer below 50.1% sponsor voting</td>
              <td><span class="apex-status-pill pill-pass">MARKET STANDARD</span></td>
            </tr>
          </tbody>
        </table>
      </div>

      <div style="background:#071224; border:1px solid rgba(212,175,55,0.2); border-radius:8px; padding:14px; display:flex; justify-content:space-between; align-items:center;">
        <div>
          <div style="font-size:12px; color:#94a3b8;">Deterministic Clearance Token</div>
          <div style="font-family:monospace; color:#d4af37; font-size:13px; font-weight:700;">APEX-NY-2026-CLEARANCE-PASS</div>
        </div>
        <button class="apex-action-btn" onclick="alert('Digital Certificate exported to /workspace/apex_clearance.pdf')">Export PDF Brief</button>
      </div>
    </div>
  </div>
</div>

<script>
  function openMultimodalModal() {
    document.getElementById('apexMultimodalModal').style.display = 'flex';
  }
  function closeMultimodalModal() {
    document.getElementById('apexMultimodalModal').style.display = 'none';
  }
</script>
<!-- END APEX MULTIMODAL TERM SHEET & CREDIT ANALYZER -->
"""


def reset():
    print("Restoring pristine synthetic corporate portal baseline (index.html)...")
    if not PRISTINE_HTML.exists():
        print(f"Error: {PRISTINE_HTML} not found.")
        sys.exit(1)
    shutil.copy2(PRISTINE_HTML, INDEX_HTML)
    print("Successfully restored pristine baseline.")


def inject(feature_name: str):
    if not INDEX_HTML.exists():
        reset()

    content = INDEX_HTML.read_text(encoding="utf-8")

    if feature_name == "modern_header_ux":
        print("Injecting Modern UX Deal Header & Precedent Ticker...")
        slot = "<!-- FEATURE_SLOT: HEADER_SLOT -->"
        slot_end = "<!-- FEATURE_SLOT_END: HEADER_SLOT -->"
        if slot in content and slot_end in content:
            pre = content.split(slot)[0]
            post = content.split(slot_end)[1]
            new_content = f"{pre}{slot}\n{SNIPPET_MODERN_UX}\n{slot_end}{post}"
            INDEX_HTML.write_text(new_content, encoding="utf-8")
            print("Modern UX header injected.")
        else:
            INDEX_HTML.write_text(SNIPPET_MODERN_UX + content, encoding="utf-8")

    elif feature_name == "modern_header_ai":
        print("Injecting Intelligent Precedent Navigator (AI Search + Gemini 3.8 Flash)...")
        inject("modern_header_ux")
        content = INDEX_HTML.read_text(encoding="utf-8")
        if "<!-- APEX INTELLIGENT PRECEDENT NAVIGATOR" not in content:
            marker = "<!-- END APEX MODERNIZED EXECUTIVE DEAL COCKPIT -->"
            if marker in content:
                parts = content.split(marker)
                new_content = parts[0] + marker + "\n" + SNIPPET_MODERN_AI + parts[1]
                INDEX_HTML.write_text(new_content, encoding="utf-8")
                print("Intelligent AI Navigator dock injected.")
            else:
                INDEX_HTML.write_text(content.replace("</body>", f"{SNIPPET_MODERN_AI}\n</body>"), encoding="utf-8")

    elif feature_name == "ai_advisor":
        print("Injecting Floating 24/7 Apex Deal AI Advisor...")
        slot = "<!-- FEATURE_SLOT: FLOATING_ASSISTANT -->"
        slot_end = "<!-- FEATURE_SLOT_END: FLOATING_ASSISTANT -->"
        if slot in content and slot_end in content:
            pre = content.split(slot)[0]
            post = content.split(slot_end)[1]
            new_content = f"{pre}{slot}\n{SNIPPET_AI_ADVISOR}\n{slot_end}{post}"
            INDEX_HTML.write_text(new_content, encoding="utf-8")
            print("24/7 Deal AI Advisor injected.")
        else:
            INDEX_HTML.write_text(content.replace("</body>", f"{SNIPPET_AI_ADVISOR}\n</body>"), encoding="utf-8")

    elif feature_name == "ai_multimodal_deal":
        print("Injecting Multimodal Term Sheet Analyzer Modal...")
        if "<!-- APEX MODERNIZED EXECUTIVE DEAL COCKPIT" not in content:
            inject("modern_header_ux")
            content = INDEX_HTML.read_text(encoding="utf-8")
        slot = "<!-- FEATURE_SLOT: MULTIMODAL_MODAL -->"
        slot_end = "<!-- FEATURE_SLOT_END: MULTIMODAL_MODAL -->"
        if slot in content and slot_end in content:
            pre = content.split(slot)[0]
            post = content.split(slot_end)[1]
            new_content = f"{pre}{slot}\n{SNIPPET_MULTIMODAL}\n{slot_end}{post}"
            INDEX_HTML.write_text(new_content, encoding="utf-8")
            print("Multimodal Term Sheet Analyzer injected.")
        else:
            INDEX_HTML.write_text(content.replace("</body>", f"{SNIPPET_MULTIMODAL}\n</body>"), encoding="utf-8")
    else:
        print(f"Unknown feature: {feature_name}")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: inject_feature.py [reset | inject <feature_name>]")
        print("Features: modern_header_ux, modern_header_ai, ai_advisor, ai_multimodal_deal")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "reset":
        reset()
    elif cmd == "inject":
        if len(sys.argv) < 3:
            print("Error: Specify feature to inject.")
            sys.exit(1)
        inject(sys.argv[2])
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
