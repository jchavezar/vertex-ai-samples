/**
 * Pillar 2: Text-to-Reels Studio Frontend Module (9:16 Vertical Reel Player + PITI Sticker Overlay + Veo Generation HUD)
 */

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define([], factory);
  } else if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.P2ReelsPlayer = factory();
  }
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  /**
   * Fetches the 8-preset reel vault.
   */
  async function fetchPresets() {
    const res = await fetch('/api/pillar2/presets');
    if (!res.ok) throw new Error('Failed to fetch reel presets');
    return await res.json();
  }

  /**
   * Fetches a specific preset reel.
   */
  async function fetchPreset(presetId) {
    const res = await fetch('/api/pillar2/preset/' + encodeURIComponent(presetId));
    if (!res.ok) throw new Error('Failed to fetch reel preset ' + presetId);
    return await res.json();
  }

  /**
   * Generates a custom 9:16 vertical reel from text.
   */
  async function generateReel(params) {
    const endpoint = '/api/pillar2/generate-reel';
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params || {})
    });
    if (!res.ok) throw new Error('Failed to generate reel: HTTP ' + res.status);
    return await res.json();
  }

  /**
   * Calculates monthly PITI mortgage payment and closing credit.
   */
  function calculateFinancials(price, downPct, ratePct) {
    const p = Math.max(100000, Number(price) || 450000);
    const d = Math.max(0, Math.min(100, Number(downPct) || 10));
    const r = Math.max(0.1, Number(ratePct) || 5.875);

    const loan = p * (1 - d / 100.0);
    const monthlyRate = (r / 100.0) / 12.0;
    const n = 360; // 30-year fixed
    const pi =
      monthlyRate > 0
        ? loan * (monthlyRate * Math.pow(1 + monthlyRate, n)) / (Math.pow(1 + monthlyRate, n) - 1)
        : loan / n;

    // Property taxes (~1.45% annual) + insurance (~$145/mo)
    const taxesAndIns = (p * 0.0145 / 12.0) + 145;
    const piti = Math.round(pi + taxesAndIns);
    const credit = Math.round(p * 0.01); // 1% Rocket + Redfin closing credit

    return {
      price: p,
      downPct: d,
      ratePct: r,
      loanAmount: Math.round(loan),
      monthlyPITI: piti,
      closingCredit: credit
    };
  }

  /**
   * Applies reel data to the 9:16 stage DOM elements.
   */
  function applyReelToStage(stageElements, data) {
    if (!data || !stageElements) return;

    const vid = stageElements.video;
    const poster = stageElements.posterOverlay;
    const stickerPiti = stageElements.stickerPiti;
    const stickerCredit = stageElements.stickerCredit;
    const stickerSub = stageElements.stickerSub;
    const captionList = stageElements.captionList;

    if (vid && data.video_url) {
      vid.src = data.video_url;
      vid.currentTime = 0;
      vid.play().catch(function () {});
    }

    if (poster) {
      if (data.poster_b64) {
        poster.style.backgroundImage = 'url(' + data.poster_b64 + ')';
        poster.style.opacity = '0.35';
      } else {
        poster.style.opacity = '0';
      }
    }

    const fin = data.financials || calculateFinancials(data.price, data.down_pct, data.rate_pct);

    if (stickerPiti) {
      stickerPiti.innerText = '$' + (fin.monthlyPITI || fin.monthly_piti).toLocaleString() + '/mo';
    }
    if (stickerCredit) {
      stickerCredit.innerText = '+$' + (fin.closingCredit || fin.closing_credit).toLocaleString() + ' Closing Credit';
    }
    if (stickerSub) {
      stickerSub.innerText = fin.downPct + '% Down · ' + Number(fin.ratePct).toFixed(3) + '% 30-Yr Fixed';
    }

    if (captionList && Array.isArray(data.captions)) {
      captionList.innerHTML = data.captions
        .map(function (c, idx) {
          return (
            '<div class="caption-item" data-caption-idx="' +
            idx +
            '">' +
            '<div class="cap-tag">' +
            escapeHtml(c.tag) +
            '</div>' +
            '<div class="cap-text">' +
            escapeHtml(c.text) +
            '</div>' +
            '</div>'
          );
        })
        .join('');
    }
  }

  function escapeHtml(str) {
    return String(str || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  /**
   * Drives the 3-step Veo Generation HUD:
   * Step 1: Script + 4-Scene Plan (gemini-3.8-flash)
   * Step 2: Photorealistic Architectural Keyframe (gemini-3.1-flash-image / Imagen 4)
   * Step 3: Veo 3.1 9:16 Video Synthesis
   */
  function showVeoGenerationHUD(hudEl, isFullVeo) {
    if (!hudEl) return { updateStep: function () {}, hide: function () {} };

    hudEl.style.display = 'flex';
    const bar = hudEl.querySelector('.progress-bar-fill');
    const stepLabel = hudEl.querySelector('.hud-step-label');
    const titleLabel = hudEl.querySelector('.hud-title-label');

    function setStep(stepNum, label, title, pct) {
      if (bar) bar.style.width = pct + '%';
      if (stepLabel) stepLabel.innerText = 'Step ' + stepNum + '/3 · ' + label;
      if (titleLabel) titleLabel.innerText = title;
    }

    setStep(1, 'LLM Screenplay', 'Synthesizing 4-Scene Architectural Beat Sheet...', 25);

    return {
      toStep2: function () {
        setStep(2, 'Keyframe Synthesis', 'Rendering Ultra-HD Architectural Keyframe...', 55);
      },
      toStep3: function () {
        setStep(
          3,
          isFullVeo ? 'Veo 3.1 Video Generation' : 'Veo Reel Vault Assembling',
          isFullVeo ? 'Executing Vertex AI veo-3.1-generate-001 (9:16 MP4)...' : 'Assembling 9:16 Vertical Reel with PITI Overlay...',
          85
        );
      },
      finish: function () {
        if (bar) bar.style.width = '100%';
        setTimeout(function () {
          hudEl.style.display = 'none';
        }, 400);
      },
      hide: function () {
        hudEl.style.display = 'none';
      }
    };
  }

  return {
    fetchPresets: fetchPresets,
    fetchPreset: fetchPreset,
    generateReel: generateReel,
    calculateFinancials: calculateFinancials,
    applyReelToStage: applyReelToStage,
    showVeoGenerationHUD: showVeoGenerationHUD
  };
});
