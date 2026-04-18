/* ===========================================================
   Build a Kit — slide-in side panel.
   Talks to:  POST /api/kit/{datapoint_id}
   Exposes:   window.Kit.open(datapointId, sourceCard?)

   Self-contained: this file does NOT share helpers with app_v2.js
   (app_v2 lives inside an IIFE), so we re-declare tiny `el`/`$`
   utilities under the kit-* namespace.
   =========================================================== */
(function () {
  'use strict';

  // -------- tiny helpers (private to this module) --------
  const $ = (sel, root = document) => root.querySelector(sel);
  const el = (tag, attrs, ...children) => {
    const n = document.createElement(tag);
    if (attrs) {
      for (const [k, v] of Object.entries(attrs)) {
        if (v == null || v === false) continue;
        if (k === 'class') n.className = v;
        else if (k === 'style') n.style.cssText = v;
        else if (k === 'dataset') for (const [dk, dv] of Object.entries(v)) n.dataset[dk] = dv;
        else if (k.startsWith('on') && typeof v === 'function') n.addEventListener(k.slice(2), v);
        else if (v === true) n.setAttribute(k, '');
        else n.setAttribute(k, v);
      }
    }
    for (const c of children.flat()) {
      if (c == null || c === false) continue;
      n.appendChild(c.nodeType ? c : document.createTextNode(String(c)));
    }
    return n;
  };
  const clamp01 = s => Math.max(0, Math.min(1, Number(s) || 0));

  // Lightweight toast — try the global one defined inside app_v2.js's IIFE
  // by pushing a node directly into #toasts (the app already styles `.toast`).
  function toast(title, body, kind = 'info', ms = 2600) {
    const host = $('#toasts');
    if (!host) { console.log(`[kit] ${title}: ${body}`); return; }
    const t = el('div', { class: `toast ${kind}` },
      el('div', {},
        el('div', { class: 'toast__title' }, title),
        body ? el('div', { class: 'toast__body' }, body) : null,
      )
    );
    host.appendChild(t);
    setTimeout(() => {
      t.style.transition = 'opacity .2s ease, transform .2s ease';
      t.style.opacity = 0; t.style.transform = 'translateX(8px)';
      setTimeout(() => t.remove(), 220);
    }, ms);
  }

  // -------- modality presentation --------
  const MOD_META = {
    photo:       { label: 'Photo',   icon: '🖼️' },
    video:       { label: 'Video',   icon: '🎬' },
    audio_music: { label: 'Music',   icon: '🎵' },
    audio_sfx:   { label: 'SFX',     icon: '🔊' },
    graphic:     { label: 'Graphic', icon: '🎨' },
  };
  const MOD_ORDER = ['photo', 'video', 'audio_music', 'audio_sfx', 'graphic'];

  // Single shared <audio> element so opening rows doesn't pile up players.
  let sharedAudio = null;
  function getSharedAudio() {
    if (!sharedAudio) {
      sharedAudio = document.createElement('audio');
      sharedAudio.preload = 'metadata';
    }
    return sharedAudio;
  }

  // -------- panel scaffolding --------
  const panel = $('#kitPanel');
  if (!panel) {
    console.warn('[kit] #kitPanel aside missing — kit feature inert');
    return;
  }

  let currentReq = 0;       // monotonically increasing request id (race-cancel)
  let currentSource = null; // last opened seed (for Esc / reopen)

  function render(seed) {
    panel.innerHTML = '';
    const head = el('header', { class: 'kit-head' },
      el('div', { class: 'kit-head__icon' }, '🧰'),
      el('div', { class: 'kit-head__text' },
        el('div', { class: 'kit-head__title' }, 'Your Kit'),
        el('div', { class: 'kit-head__sub', id: 'kitSub' },
          'Building from: ' + (seed?.caption_text || seed?.title || seed?.datapoint_id || '...')
        ),
      ),
      el('button', {
        class: 'kit-close', title: 'Close', onclick: close,
      }, '×'),
    );
    const body = el('div', { class: 'kit-body', id: 'kitBody' });
    // Skeleton rows for instant feedback.
    for (const m of MOD_ORDER) {
      body.appendChild(skeletonRow(m));
    }
    const status = el('div', { class: 'kit-status', id: 'kitStatus' }, 'Embedding seed and querying 4 modalities...');
    const foot = el('footer', { class: 'kit-foot' },
      el('button', {
        class: 'kit-foot__btn',
        title: 'Download all assets in this kit as a zip',
        onclick: () => toast('Coming soon', 'Bundle download will land before EBC', 'info'),
      }, '⤓ Download all (.zip)'),
      el('span', { class: 'kit-foot__seed', id: 'kitFootSeed' }, ''),
    );
    panel.appendChild(head);
    panel.appendChild(body);
    panel.appendChild(status);
    panel.appendChild(foot);
  }

  function skeletonRow(modality) {
    const meta = MOD_META[modality] || { label: modality, icon: '·' };
    return el('div', { class: 'kit-row', dataset: { mod: modality } },
      el('div', { class: 'kit-row__thumb kit-skel' }),
      el('div', { class: 'kit-row__main' },
        el('div', { class: 'kit-row__top' },
          el('span', { class: 'kit-row__label' }, meta.label),
        ),
        el('div', { class: 'kit-row__title kit-skel', style: 'height:14px;width:60%;' }, ' '),
        el('div', { class: 'kit-row__cap kit-skel', style: 'height:24px;width:90%;margin-top:4px;' }, ' '),
      ),
    );
  }

  function emptyRow(modality) {
    const meta = MOD_META[modality] || { label: modality, icon: '·' };
    return el('div', { class: 'kit-row is-empty', dataset: { mod: modality } },
      el('div', { class: 'kit-row__thumb' },
        el('span', { class: 'kit-row__thumb-icon' }, meta.icon),
      ),
      el('div', { class: 'kit-row__main' },
        el('div', { class: 'kit-row__top' },
          el('span', { class: 'kit-row__label' }, meta.label),
        ),
        el('div', { class: 'kit-row__title' }, 'No match found'),
        el('div', { class: 'kit-row__cap' }, 'No asset in this modality scored close enough to the seed.'),
      ),
    );
  }

  function resultRow(modality, card) {
    const meta = MOD_META[modality] || { label: modality, icon: '·' };
    const cap = card.caption || {};
    const title = cap.title || (card.caption_text || '').slice(0, 80) || 'Untitled';
    const captionSnippet = (card.caption_text || cap.description || '').slice(0, 160);
    const scorePct = (clamp01(card.score) * 100).toFixed(0);

    // Thumb: image for visual modalities, icon for pure audio.
    const thumb = el('div', { class: 'kit-row__thumb' });
    const isAudio = (modality === 'audio_music' || modality === 'audio_sfx');
    if (card.thumbnail_url && !isAudio) {
      thumb.appendChild(el('img', { src: card.thumbnail_url, alt: title, loading: 'lazy' }));
    } else {
      thumb.appendChild(el('span', { class: 'kit-row__thumb-icon' }, meta.icon));
    }

    // Play button — wired up below per modality.
    if (modality === 'video' && card.clip_url) {
      const play = el('button', { class: 'kit-row__play', title: 'Preview' }, '▶');
      play.addEventListener('click', e => {
        e.stopPropagation();
        playVideoInline(thumb, card);
      });
      thumb.appendChild(play);
    } else if (isAudio && card.clip_url) {
      const play = el('button', { class: 'kit-row__play', title: 'Preview' }, '▶');
      play.addEventListener('click', e => {
        e.stopPropagation();
        toggleAudio(card, play);
      });
      thumb.appendChild(play);
    }

    const row = el('div', { class: 'kit-row', dataset: { mod: modality } },
      thumb,
      el('div', { class: 'kit-row__main' },
        el('div', { class: 'kit-row__top' },
          el('span', { class: 'kit-row__label' }, meta.label),
          el('span', { class: 'kit-row__score', title: 'Cosine similarity to seed' },
            `${scorePct}%`),
        ),
        el('div', { class: 'kit-row__title', title }, title),
        el('div', { class: 'kit-row__cap' }, captionSnippet || (card.contributor || '')),
      ),
    );

    // Click anywhere on the row → open the asset's full URL in a new tab so
    // the demo audience sees the actual asset, not just the kit summary.
    row.addEventListener('click', () => {
      const url = card.original_url || card.clip_url || card.thumbnail_url;
      if (url) window.open(url, '_blank', 'noopener');
    });

    return row;
  }

  function playVideoInline(thumb, card) {
    if (thumb.querySelector('video')) return;
    thumb.innerHTML = '';
    const v = el('video', {
      src: card.clip_url, autoplay: true, muted: true,
      loop: true, playsinline: true, controls: false,
    });
    thumb.appendChild(v);
  }

  function toggleAudio(card, btn) {
    const a = getSharedAudio();
    const wantUrl = card.clip_url || card.original_url;
    if (!wantUrl) return;
    // Reset previously-active play button glyph.
    document.querySelectorAll('.kit-row__play.is-on').forEach(b => {
      if (b !== btn) { b.textContent = '▶'; b.classList.remove('is-on'); }
    });
    if (a.src === wantUrl && !a.paused) {
      a.pause();
      btn.textContent = '▶'; btn.classList.remove('is-on');
      return;
    }
    if (a.src !== wantUrl) a.src = wantUrl;
    a.currentTime = 0;
    a.play().then(() => {
      btn.textContent = '❚❚'; btn.classList.add('is-on');
    }).catch(err => {
      console.warn('[kit] audio play failed', err);
      toast('Preview failed', String(err.message || err), 'err');
    });
    a.onended = () => { btn.textContent = '▶'; btn.classList.remove('is-on'); };
  }

  // -------- public API --------
  async function open(datapointId, sourceCard) {
    if (!datapointId) {
      toast('Build a Kit', 'Missing asset id for this card', 'err');
      return;
    }
    currentSource = sourceCard || { datapoint_id: datapointId };
    panel.hidden = false;
    render(currentSource);

    const reqId = ++currentReq;
    const t0 = performance.now();
    let resp, data;
    try {
      // Pass the active search query so the kit inherits scene words the
      // seed caption may lack (e.g. a folk-guitar caption with no "beach"
      // anchor still produces a beach-flavoured kit when q="tropical beach").
      const activeQ = (document.querySelector('#searchInput')?.value || '').trim();
      const url = activeQ
        ? `/api/kit/${encodeURIComponent(datapointId)}?q=${encodeURIComponent(activeQ)}`
        : `/api/kit/${encodeURIComponent(datapointId)}`;
      resp = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      data = await resp.json();
    } catch (err) {
      if (reqId !== currentReq) return; // outdated
      const status = $('#kitStatus');
      if (status) {
        status.textContent = `Kit failed: ${err.message || err}`;
        status.classList.add('is-err');
      }
      return;
    }
    if (reqId !== currentReq) return;
    if (!resp.ok) {
      const status = $('#kitStatus');
      if (status) {
        status.textContent = `Kit failed (${resp.status}): ${data?.detail || 'unknown'}`;
        status.classList.add('is-err');
      }
      return;
    }
    paint(data, performance.now() - t0);
  }

  function paint(data, clientMs) {
    const seed = data.source || {};
    const kit = data.kit || {};

    const sub = $('#kitSub');
    if (sub) {
      const seedText = seed.caption_text || seed.title || seed.datapoint_id || '...';
      sub.textContent = `Built from: ${seedText}`;
    }

    const body = $('#kitBody');
    if (body) {
      body.innerHTML = '';
      // Render in canonical order, but skip the seed's own modality.
      const seedMod = (seed.modality || '').toLowerCase();
      for (const m of MOD_ORDER) {
        if (m === seedMod) continue;
        const card = kit[m];
        body.appendChild(card ? resultRow(m, card) : emptyRow(m));
      }
    }

    const status = $('#kitStatus');
    if (status) {
      const serverMs = Number(data.build_ms || 0);
      const total = Math.round(clientMs);
      const note = data.warning ? ` · ${data.warning}` : '';
      const seedSrc = seed.embedding_source || 'caption_text';
      status.textContent = `Built in ${serverMs}ms (server) · ${total}ms (round-trip) · seeded from ${seedSrc}${note}`;
      status.classList.remove('is-err');
      status.classList.add('is-ok');
    }
    const seedFoot = $('#kitFootSeed');
    if (seedFoot) {
      seedFoot.textContent = `seed: ${(seed.datapoint_id || '').slice(0, 10)}…`;
    }
  }

  function close() {
    panel.hidden = true;
    // Stop any audio that's still playing.
    if (sharedAudio && !sharedAudio.paused) sharedAudio.pause();
    document.querySelectorAll('.kit-row__play.is-on').forEach(b => {
      b.textContent = '▶'; b.classList.remove('is-on');
    });
    currentReq++;
  }

  // Esc closes the panel (matches assetchat ergonomics).
  document.addEventListener('keydown', ev => {
    if (ev.key === 'Escape' && !panel.hidden) close();
  });

  // Initial DOM scaffold so the panel is non-empty if someone inspects it.
  render({});
  panel.hidden = true;

  window.Kit = { open, close };
})();
