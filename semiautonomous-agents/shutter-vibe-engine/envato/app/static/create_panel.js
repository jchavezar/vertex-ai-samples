/* ===========================================================
   Create with AI — slide-in side panel (Nano Banana prototype).
   Talks to:  POST /api/create/image  (gemini-2.5-flash-image)
   Exposes:   window.Create.open(toolKey, toolMeta?)
   =========================================================== */
(function () {
  'use strict';

  const $ = (sel) => document.querySelector(sel);
  const panel    = $('#createPanel');
  const titleEl  = $('#createPanelTitle');
  const modelEl  = $('#createPanelModel');
  const promptEl = $('#createPanelPrompt');
  const goBtn    = $('#createPanelGo');
  const demoBtn  = $('#createPanelDemo');
  const statusEl = $('#createPanelStatus');
  const outEl    = $('#createPanelOutput');
  const closeBtn = $('#createPanelClose');
  const tabsEl   = $('#createPanelTabs');
  const voiceOpts = $('#createPanelVoiceOpts');
  const voiceSel  = $('#createPanelVoice');

  if (!panel) { console.warn('[create] #createPanel missing'); return; }

  // Gemini 3.1 Flash TTS prebuilt voices (30 total). Grouped by gender.
  const VOICES_F = [
    ['Kore',         'Firm'],
    ['Aoede',        'Breezy'],
    ['Leda',         'Youthful'],
    ['Zephyr',       'Bright'],
    ['Autonoe',      'Bright'],
    ['Callirrhoe',   'Easygoing'],
    ['Despina',      'Smooth'],
    ['Erinome',      'Clear'],
    ['Laomedeia',    'Upbeat'],
    ['Achernar',     'Soft'],
    ['Gacrux',       'Mature'],
    ['Pulcherrima',  'Forward'],
    ['Vindemiatrix', 'Gentle'],
    ['Sulafar',      'Warm'],
  ];
  const VOICES_M = [
    ['Charon',         'Informative'],
    ['Puck',           'Upbeat'],
    ['Fenrir',         'Excitable'],
    ['Orus',           'Firm'],
    ['Enceladus',      'Breathy'],
    ['Iapetus',        'Clear'],
    ['Umbriel',        'Easygoing'],
    ['Algieba',        'Smooth'],
    ['Algenib',        'Gravelly'],
    ['Rasalgethi',     'Informative'],
    ['Alnilam',        'Firm'],
    ['Schedar',        'Even'],
    ['Achird',         'Friendly'],
    ['Zubenelgenubi',  'Casual'],
    ['Sadachbia',      'Lively'],
    ['Sadaltager',     'Knowledgeable'],
  ];

  function buildVoiceOptions() {
    if (!voiceSel || voiceSel.options.length) return;
    const mk = (label, list) => {
      const og = document.createElement('optgroup');
      og.label = label;
      for (const [name, desc] of list) {
        const o = document.createElement('option');
        o.value = name; o.textContent = `${name} — ${desc}`;
        og.appendChild(o);
      }
      voiceSel.appendChild(og);
    };
    mk('Female', VOICES_F);
    mk('Male', VOICES_M);
    voiceSel.value = 'Kore';
  }

  // Per-tool demo prompts (one-click fill).
  const DEMO_PROMPT = {
    voice: '[excited] Welcome to the next generation of Gemini Text-to-Speech! [amazed] Watch how these tags transform the tone. [whispers] We can drop into a dark, suspenseful whisper... [panicked] Or speed things up to absolute panic mode because we\'re running out of time! [sighs] The model breathes. It even laughs! [laughs] The best part is being able to [delighted] mix and match emotions, all from a single API call.',
    image: 'cinematic photograph of a lo-fi coffee shop at golden hour, soft window light, ceramic mug steaming, 35mm film grain, shallow depth of field',
    music: '90s grunge rock, distorted guitars, raw vocals, melancholic, mid-tempo, 110 BPM',
    video: 'a slow drone shot over a misty mountain lake at dawn, soft golden light, gentle wind on the water',
  };

  const TOOL_META = {
    imagegen: { title: 'ImageGen',  icon: '🖼️', model: 'Nano Banana · gemini-3.1-flash-image-preview',         placeholder: 'cinematic photograph of a lo-fi coffee shop, soft morning light, 35mm…', kind: 'image' },
    imageedit:{ title: 'ImageEdit', icon: '✏️', model: 'Nano Banana — coming soon',                            placeholder: 'change the sky to sunset, keep everything else…',                       kind: null },
    videogen: { title: 'VideoGen',  icon: '🎬', model: 'Veo 3.1 lite · veo-3.1-lite-generate-001 · 8s 720p +audio', placeholder: 'a slow drone shot over a misty mountain lake at dawn…',              kind: 'video' },
    musicgen: { title: 'MusicGen',  icon: '🎵', model: 'Lyria 3 · lyria-3-clip-preview',                        placeholder: 'lo-fi hip hop, mellow piano, vinyl crackle, 90 BPM…',                    kind: 'music' },
    voicegen: { title: 'VoiceGen',  icon: '🎙️', model: 'Gemini 3.1 Flash TTS · Kore · audio-tag aware (preview)', placeholder: 'Say cheerfully: Welcome to Envato. Twenty-seven million assets, indexed by Vertex AI.', kind: 'voice' },
    soundgen: { title: 'SoundGen',  icon: '🔊', model: 'Lyria SFX — coming soon',                              placeholder: 'thunder rolling over a wet city street at night…',                       kind: null },
  };
  const TOOL_ORDER = ['imagegen','imageedit','videogen','musicgen','voicegen','soundgen'];
  let currentKind = null;
  let currentKey  = null;

  function renderTabs() {
    if (!tabsEl) return;
    tabsEl.innerHTML = '';
    for (const key of TOOL_ORDER) {
      const m = TOOL_META[key];
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'create-panel__tab' + (m.kind ? '' : ' is-disabled') + (key === currentKey ? ' is-active' : '');
      btn.dataset.key = key;
      btn.title = m.model;
      btn.innerHTML = `<span class="create-panel__tab-icon">${m.icon}</span><span class="create-panel__tab-lbl">${m.title}</span>`;
      btn.addEventListener('click', () => open(key));
      tabsEl.appendChild(btn);
    }
  }

  function setStatus(msg, kind) {
    statusEl.textContent = msg || '';
    statusEl.dataset.kind = kind || '';
  }

  function open(toolKey) {
    const meta = TOOL_META[toolKey] || TOOL_META.imagegen;
    currentKind = meta.kind;
    currentKey  = toolKey in TOOL_META ? toolKey : 'imagegen';
    titleEl.textContent = meta.title;
    modelEl.textContent = meta.model;
    promptEl.placeholder = meta.placeholder;
    promptEl.value = '';
    outEl.innerHTML = '';
    setStatus(currentKind ? 'Idle' : 'Coming soon — not yet wired to a model', currentKind ? '' : 'warn');
    goBtn.disabled = !currentKind;
    if (voiceOpts) {
      const showVoice = currentKind === 'voice';
      voiceOpts.hidden = !showVoice;
      if (showVoice) buildVoiceOptions();
    }
    if (demoBtn) {
      demoBtn.hidden = !(currentKind && DEMO_PROMPT[currentKind]);
    }
    renderTabs();
    panel.hidden = false;
    requestAnimationFrame(() => promptEl.focus());
  }

  function close() {
    panel.hidden = true;
  }

  const ENDPOINT_BY_KIND = {
    image: '/api/create/image',
    music: '/api/create/music',
    video: '/api/create/video',
    voice: '/api/create/voice',
  };
  const LABEL_BY_KIND = {
    image: 'Nano Banana',
    music: 'Lyria 3',
    video: 'Veo 3',
    voice: 'Gemini 3.1 Flash TTS',
  };

  async function generate() {
    const prompt = (promptEl.value || '').trim();
    if (!prompt || !currentKind) { promptEl.focus(); return; }
    const endpoint = ENDPOINT_BY_KIND[currentKind];
    const label = LABEL_BY_KIND[currentKind] || 'AI';
    goBtn.disabled = true;
    const longRun = currentKind === 'video';
    setStatus(longRun ? `Generating with ${label}… (Veo can take 1–2 min)` : `Generating with ${label}…`, 'busy');
    outEl.innerHTML = (currentKind === 'music' || currentKind === 'voice')
      ? '<div class="create-panel__skel create-panel__skel--audio"></div>'
      : '<div class="create-panel__skel"></div>';
    const t0 = performance.now();
    try {
      const body = { prompt };
      if (currentKind === 'voice' && voiceSel && voiceSel.value) body.voice = voiceSel.value;
      const r = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!r.ok) {
        const txt = await r.text();
        throw new Error(friendlyError(r.status, txt, currentKind));
      }
      const data = await r.json();
      const dt = Math.round(performance.now() - t0);
      const meta = `${escapeHtml(prompt)} <span class="create-panel__meta">· ${data.model} · ${dt}ms</span>`;
      if (currentKind === 'image') {
        outEl.innerHTML =
          `<figure class="create-panel__fig">
             <img src="data:${data.mime};base64,${data.image_b64}" alt="generated"/>
             <figcaption>${meta}</figcaption>
           </figure>`;
      } else if (currentKind === 'music') {
        const cap = data.caption ? `<details class="create-panel__cap"><summary>Auto-generated caption</summary><p>${escapeHtml(data.caption)}</p></details>` : '';
        outEl.innerHTML =
          `<figure class="create-panel__fig">
             <audio controls src="data:${data.mime};base64,${data.audio_b64}"></audio>
             <figcaption>${meta}</figcaption>
             ${cap}
           </figure>`;
      } else if (currentKind === 'voice') {
        outEl.innerHTML =
          `<figure class="create-panel__fig">
             <audio controls src="data:${data.mime};base64,${data.audio_b64}"></audio>
             <figcaption>${meta}</figcaption>
           </figure>`;
      } else if (currentKind === 'video') {
        outEl.innerHTML =
          `<figure class="create-panel__fig">
             <video controls playsinline src="data:${data.mime};base64,${data.video_b64}"></video>
             <figcaption>${meta}</figcaption>
           </figure>`;
      }
      setStatus(`Done in ${dt} ms`, 'ok');
    } catch (err) {
      console.error(err);
      outEl.innerHTML = `<div class="create-panel__err">${escapeHtml(String(err.message || err))}</div>`;
      setStatus('Failed', 'err');
    } finally {
      goBtn.disabled = !currentKind;
    }
  }

  function friendlyError(status, txt, kind) {
    const t = String(txt || '');
    if (/sensitive words|Prohibited Use policy|safety|blocked|PROHIBITED_CONTENT/i.test(t)) {
      if (kind === 'music') return 'Lyria refused this prompt. Avoid artist or band names — describe genre, mood, instruments, tempo instead (e.g. "90s grunge rock, distorted guitars, melancholic, mid-tempo, 110 BPM").';
      if (kind === 'image') return 'Nano Banana refused this prompt for safety. Try removing names of real people or sensitive terms.';
      if (kind === 'video') return 'Veo refused this prompt for safety. Try removing names of real people or sensitive terms.';
      if (kind === 'voice') return 'Gemini TTS preview blocked this text. The Vertex preview safety filter is over-eager on bracketed audio tags — try plain prose like "Say cheerfully: Welcome to Envato." or use only known-good tags ([whispers], [short pause]).';
      return 'The model refused this prompt for safety reasons. Try rephrasing.';
    }
    if (status === 429) return 'Rate limited. Wait a moment and try again.';
    if (status >= 500) return `Server error (${status}). Try again in a moment.`;
    return `HTTP ${status}: ${t.slice(0, 240)}`;
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }

  goBtn.addEventListener('click', generate);
  closeBtn.addEventListener('click', close);
  if (demoBtn) {
    demoBtn.addEventListener('click', () => {
      const dp = DEMO_PROMPT[currentKind];
      if (!dp) return;
      promptEl.value = dp;
      promptEl.focus();
      promptEl.scrollTop = 0;
    });
  }
  promptEl.addEventListener('keydown', e => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) { e.preventDefault(); generate(); }
  });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && !panel.hidden) close(); });

  window.Create = { open, close };
})();
