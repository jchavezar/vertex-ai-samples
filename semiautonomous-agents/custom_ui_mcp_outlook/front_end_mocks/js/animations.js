/**
 * ADVANCED ANIMATIONS & INTERACTIVE UX ENGINE
 * Handles Claude Code Ink Loader dynamics, Yazdani Glyph morphing, Token streaming & Barometer
 */

window.AnimationEngine = {
  // Renders the Claude Code Ink Loader element
  createInkLoaderHTML: function(label = "Agent is formulating reasoning trace...") {
    return `
      <div class="ink-loading-wrapper" style="display: flex; align-items: center; gap: 12px; padding: 12px 16px; background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 12px;">
        <span class="shrinking-shining-ink"></span>
        <span class="sweep-text" style="font-family: var(--font-mono); font-size: 0.8rem; font-weight: 500;">
          ${label}
        </span>
      </div>
    `;
  },

  // Renders the Yazdani Morphing Glyph Spinner element
  createYazdaniSpinnerHTML: function(label = "Quantum Multi-Agent Grounding Active...") {
    return `
      <div class="yazdani-loading-wrapper" style="display: flex; align-items: center; gap: 12px; padding: 12px 16px; background: rgba(6, 182, 212, 0.08); border: 1px solid rgba(6, 182, 212, 0.3); border-radius: 12px;">
        <span class="yazdani-spinner"></span>
        <span style="font-family: var(--font-mono); font-size: 0.8rem; font-weight: 600; color: var(--accent-cyan); text-transform: uppercase; letter-spacing: 0.05em;">
          ${label}
        </span>
      </div>
    `;
  },

  // Real-time typewriter / token stream animation
  streamTokens: function(targetElement, fullText, speed = 12, onDone = null) {
    targetElement.innerHTML = '';
    let index = 0;

    const interval = setInterval(() => {
      if (index < fullText.length) {
        const char = fullText.charAt(index);
        if (char === '\n') {
          targetElement.innerHTML += '<br/>';
        } else {
          targetElement.innerHTML += char;
        }
        index++;
      } else {
        clearInterval(interval);
        if (onDone) onDone();
      }
    }, speed);
  },

  // Update token barometer meter
  updateTokenBarometer: function(addedTokens = 350) {
    const currentGauge = document.getElementById('token-barometer-value');
    const fillBar = document.getElementById('token-meter-fill');
    if (!currentGauge || !fillBar) return;

    let currentVal = parseInt(currentGauge.dataset.val || "18420");
    let newVal = currentVal + addedTokens;
    currentGauge.dataset.val = newVal;
    currentGauge.innerText = `${(newVal / 1000).toFixed(1)}k / 200k tokens`;
    
    let pct = Math.min(100, Math.round((newVal / 200000) * 100));
    fillBar.style.width = `${pct}%`;
  }
};
