/**
 * Google Cloud Agent Platform & AI Glossary Controller (`static/glossary_launchpad.js`)
 * Powers both `#tab-pane-glossary` on the Unified Portal (`/`) and standalone `/glossary`.
 */
(function () {
  'use strict';

  var currentDepthMode = 'beginner'; // 'beginner' | 'builder'
  var currentConceptCat = 'all';

  var localAudioCtx = null;
  var localAudioSource = null;
  var localActiveWs = null;
  var localActiveBtn = null;
  var localTtsEpoch = 0;

  var ICON_LISTEN = '<svg class="gl-vec-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.5 8.5a5 5 0 0 1 0 7"/><path d="M19 6a8.5 8.5 0 0 1 0 12"/></svg>';
  var ICON_STOP = '<svg class="gl-vec-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="5" y="5" width="14" height="14" rx="2.5"/></svg>';

  function setGlossaryDepthMode(mode) {
    var m = mode === 'builder' ? 'builder' : 'beginner';
    currentDepthMode = m;

    var root = document.getElementById('gl-launchpad-root');
    if (root) root.setAttribute('data-gl-depth', m);

    var btnBeg = document.getElementById('gl-mode-beginner');
    var btnBld = document.getElementById('gl-mode-builder');
    if (btnBeg) {
      btnBeg.classList.toggle('active', m === 'beginner');
      btnBeg.setAttribute('aria-pressed', m === 'beginner' ? 'true' : 'false');
    }
    if (btnBld) {
      btnBld.classList.toggle('active', m === 'builder');
      btnBld.setAttribute('aria-pressed', m === 'builder' ? 'true' : 'false');
    }

    document.querySelectorAll('.gl-concept-card').forEach(function (card) {
      var vBeg = card.querySelector('.gl-view-beginner');
      var vBld = card.querySelector('.gl-view-builder');
      var lbl = card.querySelector('.gl-flip-btn-lbl');
      if (m === 'builder') {
        if (vBeg) vBeg.style.display = 'none';
        if (vBld) vBld.style.display = 'block';
        if (lbl) lbl.textContent = 'Show Plain English';
      } else {
        if (vBeg) vBeg.style.display = 'block';
        if (vBld) vBld.style.display = 'none';
        if (lbl) lbl.textContent = 'Show SDK / Code';
      }
    });
  }

  function toggleSingleGlossaryCardCode(btnEl) {
    if (!btnEl) return;
    var card = btnEl.closest('.gl-concept-card');
    if (!card) return;
    var vBeg = card.querySelector('.gl-view-beginner');
    var vBld = card.querySelector('.gl-view-builder');
    var lbl = btnEl.querySelector('.gl-flip-btn-lbl');
    if (!vBeg || !vBld) return;
    var showCode = vBld.style.display === 'none';
    vBld.style.display = showCode ? 'block' : 'none';
    vBeg.style.display = showCode ? 'none' : 'block';
    if (lbl) {
      lbl.textContent = showCode ? 'Show Plain English' : 'Show SDK / Code';
    }
  }

  function applyConceptFilterAndSearch() {
    var searchInput = document.getElementById('gl-search-input');
    var q = (searchInput ? searchInput.value : '').trim().toLowerCase();
    var shown = 0;

    document.querySelectorAll('.gl-concept-card').forEach(function (card) {
      var cat = (card.getAttribute('data-gl-cat') || '').trim();
      var text = ((card.getAttribute('data-keywords') || '') + ' ' + (card.textContent || '')).toLowerCase();
      var matchCat = currentConceptCat === 'all' || cat.toLowerCase() === currentConceptCat.toLowerCase();
      var matchText = !q || text.indexOf(q) !== -1;
      var visible = matchCat && matchText;
      card.style.display = visible ? '' : 'none';
      if (visible) shown++;
    });

    var countBadge = document.getElementById('gl-concepts-count');
    if (countBadge) {
      countBadge.textContent = shown + (shown === 1 ? ' Term Shown' : ' Terms Shown');
    }
  }

  function filterGlossaryConcepts(category) {
    currentConceptCat = category || 'all';
    document.querySelectorAll('[data-gl-cat].gl-select-pill').forEach(function (btn) {
      var c = btn.getAttribute('data-gl-cat') || 'all';
      btn.classList.toggle('active', c.toLowerCase() === currentConceptCat.toLowerCase());
    });
    applyConceptFilterAndSearch();
  }

  function searchGlossaryConcepts(queryStr) {
    var searchInput = document.getElementById('gl-search-input');
    if (typeof queryStr === 'string' && searchInput && searchInput.value !== queryStr) {
      searchInput.value = queryStr;
    }
    applyConceptFilterAndSearch();
  }

  function stopGlossaryAudio() {
    localTtsEpoch++;
    if (localActiveWs) {
      try {
        localActiveWs.onmessage = null;
        localActiveWs.onerror = null;
        localActiveWs.onclose = null;
        localActiveWs.close();
      } catch (_) {}
      localActiveWs = null;
    }
    if (localAudioSource) {
      try { localAudioSource.onended = null; localAudioSource.stop(0); } catch (_) {}
      try { localAudioSource.disconnect(); } catch (_) {}
      localAudioSource = null;
    }
    if (localAudioCtx) {
      try { localAudioCtx.close(); } catch (_) {}
      localAudioCtx = null;
    }
    if (localActiveBtn) {
      if (localActiveBtn.dataset.origHtml) {
        localActiveBtn.innerHTML = localActiveBtn.dataset.origHtml;
      }
      localActiveBtn.dataset.isSpeaking = '0';
      localActiveBtn = null;
    }
    if (typeof window.stopPortalAudio === 'function') {
      try { window.stopPortalAudio(); } catch (_) {}
    }
  }

  function speakGlossaryText(text, btnEl) {
    if (!text) return;

    // Clicking the same Listen button while it is already speaking stops it immediately!
    if (btnEl && btnEl.dataset.isSpeaking === '1') {
      stopGlossaryAudio();
      return;
    }

    if (typeof window.speakPortalText === 'function') {
      window.speakPortalText(text, btnEl);
      return;
    }

    stopGlossaryAudio();
    var myEpoch = ++localTtsEpoch;

    if (btnEl) {
      if (!btnEl.dataset.origHtml) {
        btnEl.dataset.origHtml = btnEl.innerHTML;
      }
      btnEl.dataset.isSpeaking = '1';
      btnEl.innerHTML = ICON_STOP + ' <span>Stop Audio</span>';
      localActiveBtn = btnEl;
    }

    try {
      var AC = window.AudioContext || window.webkitAudioContext;
      localAudioCtx = new AC({ sampleRate: 24000 });
      if (localAudioCtx.state === 'suspended') localAudioCtx.resume();
    } catch (_) {}

    var proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
    var token = window.PORTAL_AUTH_TOKEN || '';
    var wsUrl = proto + '//' + location.host + '/ws/live-tts?auth_token=' + encodeURIComponent(token);
    var chunks = [];
    var ws = new WebSocket(wsUrl);
    localActiveWs = ws;

    ws.onopen = function () {
      if (myEpoch !== localTtsEpoch) {
        try { ws.close(); } catch (_) {}
        return;
      }
      ws.send(JSON.stringify({ text: text, voice: 'Aoede' }));
    };

    ws.onmessage = function (ev) {
      if (myEpoch !== localTtsEpoch) return;
      try {
        var msg = JSON.parse(ev.data);
        if (msg.pcm_b64) {
          var bin = atob(msg.pcm_b64);
          var bytes = new Uint8Array(bin.length);
          for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
          chunks.push(bytes);
        }
        if (msg.done) {
          localActiveWs = null;
          if (chunks.length > 0 && localAudioCtx && myEpoch === localTtsEpoch) {
            var totalLen = chunks.reduce(function (acc, c) { return acc + c.length; }, 0);
            var merged = new Uint8Array(totalLen);
            var off = 0;
            chunks.forEach(function (c) { merged.set(c, off); off += c.length; });
            var samples = Math.floor(merged.byteLength / 2);
            var f32 = new Float32Array(samples);
            var dv = new DataView(merged.buffer);
            for (var j = 0; j < samples; j++) {
              f32[j] = dv.getInt16(j * 2, true) / 32768.0;
            }
            var buf = localAudioCtx.createBuffer(1, samples, 24000);
            buf.getChannelData(0).set(f32);
            var src = localAudioCtx.createBufferSource();
            src.buffer = buf;
            src.connect(localAudioCtx.destination);
            localAudioSource = src;
            src.onended = function () {
              if (myEpoch === localTtsEpoch) stopGlossaryAudio();
            };
            src.start(0);
          } else {
            stopGlossaryAudio();
          }
        }
      } catch (_) {
        stopGlossaryAudio();
      }
    };

    ws.onerror = function () {
      if (myEpoch === localTtsEpoch) stopGlossaryAudio();
    };
  }

  // ===========================================================================
  // LIVE SANDBOX MINI-IDE POP-UP CONTROLLER
  // ===========================================================================
  var activeIdeTermId = null;
  var activeIdeOrigCode = '';
  var activeIdeOrigInput = '';
  var activeIdeSpokenSummary = '';
  var ideRunInFlight = false;

  function escapeHtml(str) {
    return String(str || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  function getRegistryItem(termId) {
    var reg = window.GLOSSARY_SANDBOX_REGISTRY || {};
    return reg[termId] || null;
  }

  function onGlossaryCodeEdited() {
    var editor = document.getElementById('gl-ide-code-editor');
    var modBadge = document.getElementById('gl-ide-modified-badge');
    if (!editor || !modBadge) return;
    var isMod = editor.value.trim() !== activeIdeOrigCode.trim();
    if (isMod) {
      modBadge.textContent = 'MODIFIED BUFFER · Click "Run & Send" (or Reset Code)';
      modBadge.style.color = '#F59E0B';
    } else {
      modBadge.textContent = 'Edit code, instruction, or thresholds below';
      modBadge.style.color = '#38BDF8';
    }
  }

  function openGlossarySandboxIde(termId) {
    var item = getRegistryItem(termId);
    var modal = document.getElementById('gl-sandbox-ide-modal');
    if (!modal || !item) return;

    activeIdeTermId = item.id;
    activeIdeOrigCode = item.code || '';
    activeIdeOrigInput = item.test_input || '';
    activeIdeSpokenSummary = '';

    var badgeEl = document.getElementById('gl-ide-badge');
    var titleEl = document.getElementById('gl-ide-title');
    var codeEl = document.getElementById('gl-ide-code-editor');
    var inputEl = document.getElementById('gl-ide-test-input');
    var presetsRow = document.getElementById('gl-ide-presets-row');

    if (badgeEl) badgeEl.textContent = 'LIVE SANDBOX MINI-IDE · ' + (item.badge || item.cat || 'AGENT PLATFORM');
    if (titleEl) titleEl.textContent = (item.index ? item.index + '. ' : '') + item.term;
    if (codeEl) codeEl.value = activeIdeOrigCode;
    if (inputEl) inputEl.value = activeIdeOrigInput;
    onGlossaryCodeEdited();

    if (presetsRow) {
      var presets = item.presets || [];
      presetsRow.innerHTML = presets.map(function (p, i) {
        return '<button type="button" class="gl-ide-preset-chip" data-preset-idx="' + i + '">Scenario ' + (i + 1) + ': ' + escapeHtml(p.slice(0, 54)) + '…</button>';
      }).join('');
      presetsRow.querySelectorAll('.gl-ide-preset-chip').forEach(function (btn) {
        btn.onclick = function () {
          var idx = Number(btn.getAttribute('data-preset-idx') || 0);
          if (inputEl && presets[idx]) {
            inputEl.value = presets[idx];
            runGlossarySandboxCode();
          }
        };
      });
    }

    modal.classList.add('open');
    // Immediately execute an initial live run so the user sees live behavior right away
    runGlossarySandboxCode();
  }

  function closeGlossarySandboxIde() {
    var modal = document.getElementById('gl-sandbox-ide-modal');
    if (modal) modal.classList.remove('open');
    stopGlossaryAudio();
  }

  function resetGlossarySandboxCode() {
    var codeEl = document.getElementById('gl-ide-code-editor');
    var inputEl = document.getElementById('gl-ide-test-input');
    var tempEl = document.getElementById('gl-ide-temp');
    var tempValEl = document.getElementById('gl-ide-temp-val');
    var modelEl = document.getElementById('gl-ide-model');

    if (codeEl) codeEl.value = activeIdeOrigCode;
    if (inputEl) inputEl.value = activeIdeOrigInput;
    if (tempEl) tempEl.value = '0.20';
    if (tempValEl) tempValEl.textContent = '0.20';
    if (modelEl) modelEl.value = 'gemini-3.8-flash';
    onGlossaryCodeEdited();
    runGlossarySandboxCode();
  }

  async function runGlossarySandboxCode() {
    if (ideRunInFlight) return;
    var item = getRegistryItem(activeIdeTermId) || { id: 'term-agent-formula', term: 'Agent Platform Sandbox' };
    var codeEl = document.getElementById('gl-ide-code-editor');
    var inputEl = document.getElementById('gl-ide-test-input');
    var modelEl = document.getElementById('gl-ide-model');
    var tempEl = document.getElementById('gl-ide-temp');
    var statusPill = document.getElementById('gl-ide-status-pill');
    var runLbl = document.getElementById('gl-ide-run-lbl');
    var traceList = document.getElementById('gl-ide-trace-list');
    var outConsole = document.getElementById('gl-ide-output-console');

    var codeStr = codeEl ? codeEl.value : activeIdeOrigCode;
    var testInput = inputEl ? inputEl.value : activeIdeOrigInput;
    var modelId = modelEl ? modelEl.value : 'gemini-3.8-flash';
    var tempVal = tempEl ? Number(tempEl.value) : 0.2;
    var isMod = codeStr.trim() !== activeIdeOrigCode.trim();

    ideRunInFlight = true;
    if (statusPill) {
      statusPill.textContent = 'RUNNING ON VERTEX AI (' + modelId + ')…';
      statusPill.className = 'lg-badge lg-badge-cobalt mono';
    }
    if (runLbl) runLbl.textContent = 'Running…';
    if (outConsole) {
      outConsole.textContent = 'Executing code buffer & dispatching request to Vertex AI (' + modelId + ', temp=' + tempVal.toFixed(2) + ')…';
    }

    try {
      var token = window.PORTAL_AUTH_TOKEN || '';
      var resp = await fetch('/api/glossary-sandbox-run?auth_token=' + encodeURIComponent(token), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          term_id: item.id,
          term_title: item.term,
          code: codeStr,
          test_input: testInput,
          model: modelId,
          temperature: tempVal,
          is_modified: isMod
        })
      });
      var data = await resp.json();
      ideRunInFlight = false;
      if (runLbl) runLbl.textContent = 'Run & Send';

      if (data && data.ok) {
        if (statusPill) {
          statusPill.textContent = '200 OK · ' + (data.model_used || modelId) + ' · ' + (data.latency_ms || 0) + ' ms' + (data.is_modified ? ' · MODIFIED CODE' : '');
          statusPill.className = 'lg-badge lg-badge-emerald mono';
        }
        if (traceList && Array.isArray(data.trace_steps)) {
          traceList.innerHTML = data.trace_steps.map(function (st) {
            return (
              '<div class="gl-ide-trace-item">' +
                '<div class="gl-ide-trace-top mono">' +
                  '<span>' + escapeHtml(st.step) + '</span>' +
                  '<span style="color:#34D399;">' + escapeHtml(st.status) + '</span>' +
                '</div>' +
                '<div class="gl-ide-trace-sub mono">' + escapeHtml(st.detail) + '</div>' +
              '</div>'
            );
          }).join('');
        }
        if (outConsole) {
          outConsole.textContent = data.output || '';
        }
        activeIdeSpokenSummary = data.spoken_summary || data.output || '';
      } else {
        if (statusPill) {
          statusPill.textContent = 'SANDBOX ERROR';
          statusPill.className = 'lg-badge lg-badge-crimson mono';
        }
        if (outConsole) {
          outConsole.textContent = 'Error executing sandbox: ' + ((data && data.error) || 'Unknown error');
        }
      }
    } catch (err) {
      ideRunInFlight = false;
      if (runLbl) runLbl.textContent = 'Run & Send';
      if (statusPill) {
        statusPill.textContent = 'NETWORK ERROR';
        statusPill.className = 'lg-badge lg-badge-crimson mono';
      }
      if (outConsole) {
        outConsole.textContent = 'Failed to reach /api/glossary-sandbox-run: ' + err;
      }
    }
  }

  function speakGlossaryIdeOutput(btnEl) {
    var outConsole = document.getElementById('gl-ide-output-console');
    var txt = activeIdeSpokenSummary || (outConsole ? outConsole.textContent : '');
    if (txt) {
      speakGlossaryText(txt.slice(0, 320), btnEl);
    }
  }

  function copyGlossaryIdeOutput(btnEl) {
    var outConsole = document.getElementById('gl-ide-output-console');
    if (!outConsole || !navigator.clipboard) return;
    navigator.clipboard.writeText(outConsole.textContent || '').then(function () {
      if (btnEl) {
        var orig = btnEl.innerHTML;
        btnEl.innerHTML = '<span>Copied!</span>';
        setTimeout(function () { btnEl.innerHTML = orig; }, 1400);
      }
    });
  }

  document.addEventListener('keydown', function (ev) {
    var modal = document.getElementById('gl-sandbox-ide-modal');
    if (!modal || !modal.classList.contains('open')) return;

    if (ev.key === 'Escape') {
      closeGlossarySandboxIde();
      return;
    }
    if ((ev.ctrlKey || ev.metaKey) && ev.key === 'Enter') {
      ev.preventDefault();
      runGlossarySandboxCode();
      return;
    }
    if (ev.key === 'Tab' && ev.target && ev.target.id === 'gl-ide-code-editor') {
      ev.preventDefault();
      var el = ev.target;
      var start = el.selectionStart;
      var end = el.selectionEnd;
      el.value = el.value.substring(0, start) + '    ' + el.value.substring(end);
      el.selectionStart = el.selectionEnd = start + 4;
      onGlossaryCodeEdited();
    }
  });

  window.setGlossaryDepthMode = setGlossaryDepthMode;
  window.toggleSingleGlossaryCardCode = toggleSingleGlossaryCardCode;
  window.filterGlossaryConcepts = filterGlossaryConcepts;
  window.searchGlossaryConcepts = searchGlossaryConcepts;
  window.speakGlossaryText = speakGlossaryText;
  window.stopGlossaryAudio = stopGlossaryAudio;
  window.openGlossarySandboxIde = openGlossarySandboxIde;
  window.closeGlossarySandboxIde = closeGlossarySandboxIde;
  window.resetGlossarySandboxCode = resetGlossarySandboxCode;
  window.runGlossarySandboxCode = runGlossarySandboxCode;
  window.onGlossaryCodeEdited = onGlossaryCodeEdited;
  window.speakGlossaryIdeOutput = speakGlossaryIdeOutput;
  window.copyGlossaryIdeOutput = copyGlossaryIdeOutput;
})();
