/* =========================================================================
 * gcp_strip.js — Dynamic "Built on Google Cloud" strip
 *
 * - Every Google Cloud component chip lives ONLY inside #gcp-arch-strip.
 *   Any .gcp-svc-badge injected into card headers is removed (and hidden by
 *   gcp_strip.css) so cards are never overwritten.
 * - The strip's .gcp-arch-pills is re-rendered per active pillar tab:
 *   "P<N> · <tab name>" context label + that tab's components (SVG icon,
 *   label, rich hover tooltip: API, how it's called, typical latency), with a
 *   staggered fade/slide transition. #btn-gcp-arch-drawer stays at the end.
 * - "Tell which one did you use": window.fetch / WebSocket / EventSource are
 *   wrapped NON-invasively (always pass-through, same return values, statics
 *   and prototypes preserved) and resource timing is observed, so a chip pulses
 *   when its API is actually called and shows calling… / LIVE / "used Xs ago".
 * - Public hooks for other modules (load-order independent):
 *     window.dispatchEvent(new CustomEvent('gcp:used', {detail: {keys: ['maps', 'search']}}))
 *     window.GcpStrip.markUsed(['youtube'])
 *   Keys: p1-forecast p1-dataset tts veo p2-image p2-flash gcs cloudrun
 *         p3-flash maps youtube search live-api avatar audio-vad transcription
 *         vector embeddings judge p5-image leaflet copilot
 *
 * Defensive IIFE: never throws at load and never changes request behaviour.
 * ========================================================================= */
(function () {
  'use strict';
  if (window.__gcpStripLoaded) return;
  window.__gcpStripLoaded = true;

  var LEAVE_MS = 110;
  var FRESH_MS = 6000;          // "just used" highlight window
  var PULSE_THROTTLE_MS = 650;  // per-key pulse throttle (image/tile bursts)

  function warn(msg, err) {
    try { console.warn('[gcp_strip] ' + msg, err || ''); } catch (e) { /* ignore */ }
  }

  // -------------------------------------------------------------------------
  // Icons (stroke = currentColor so chips follow tone + theme)
  // -------------------------------------------------------------------------
  var ICONS = {
    bq: '<path d="M12 2.5 20.5 7.25v9.5L12 21.5 3.5 16.75v-9.5z"/><circle cx="11.2" cy="11.2" r="3.6"/><path d="m13.9 13.9 2.9 2.9"/>',
    db: '<ellipse cx="12" cy="5.5" rx="7.5" ry="2.8"/><path d="M4.5 5.5v13c0 1.55 3.36 2.8 7.5 2.8s7.5-1.25 7.5-2.8v-13"/><path d="M4.5 12c0 1.55 3.36 2.8 7.5 2.8s7.5-1.25 7.5-2.8"/>',
    spark: '<path d="M12 2.5c.6 4.9 4.6 8.9 9.5 9.5-4.9.6-8.9 4.6-9.5 9.5-.6-4.9-4.6-8.9-9.5-9.5 4.9-.6 8.9-4.6 9.5-9.5z"/>',
    film: '<rect x="2.5" y="5" width="19" height="14" rx="3"/><path d="m10 9.2 5 2.8-5 2.8z" fill="currentColor"/>',
    image: '<rect x="3" y="4" width="18" height="16" rx="2.5"/><circle cx="9" cy="9.5" r="1.8"/><path d="m21 16-5-5-8.5 9"/>',
    audio: '<path d="M3.5 10.5v3M7.5 7.5v9M11.5 4v16M15.5 7.5v9M19.5 10.5v3"/>',
    mic: '<rect x="9" y="2.5" width="6" height="12" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3.5"/>',
    avatar: '<rect x="2.5" y="4.5" width="14" height="15" rx="2.5"/><circle cx="9.5" cy="10" r="2.6"/><path d="M5.5 17c.8-2 2.3-3 4-3s3.2 1 4 3"/><path d="m16.5 10 5-3v10l-5-3"/>',
    wave: '<path d="M2.5 12h3l2-5 3 10 3-13 3 11 2-3h3"/>',
    caption: '<rect x="2.5" y="5" width="19" height="14" rx="2.5"/><path d="M6.5 10.5h4M13 10.5h4.5M6.5 14h7M16 14h1.5"/>',
    pin: '<path d="M12 21.5s-7-6.2-7-11.5a7 7 0 1 1 14 0c0 5.3-7 11.5-7 11.5z"/><circle cx="12" cy="10" r="2.5"/>',
    play: '<rect x="2.5" y="5.5" width="19" height="13" rx="4"/><path d="m10.2 9.3 4.6 2.7-4.6 2.7z" fill="currentColor"/>',
    search: '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m15.5 15.5 5 5"/>',
    run: '<path d="M4 4.5 12.5 12 4 19.5z"/><path d="M11.5 4.5 20 12l-8.5 7.5"/>',
    storage: '<rect x="3" y="4" width="18" height="6.5" rx="1.6"/><rect x="3" y="13.5" width="18" height="6.5" rx="1.6"/><path d="M7 7.25h.01M7 16.75h.01"/>',
    map: '<path d="M9 4 3 6.5v13.5L9 17.5l6 2.5 6-2.5V4l-6 2.5z"/><path d="M9 4v13.5M15 6.5V20"/>',
    vector: '<circle cx="6" cy="7" r="2.2"/><circle cx="17.5" cy="5.5" r="2.2"/><circle cx="12" cy="17.5" r="2.2"/><path d="m7 9.1 4 6.3M16.6 7.6l-3.7 7.8M8.2 6.7l7.1-.9"/>',
    cube: '<path d="M12 2.8 20.5 7.5v9L12 21.2 3.5 16.5v-9z"/><path d="M3.5 7.5 12 12l8.5-4.5M12 12v9.2"/>',
    judge: '<path d="M12 2.8 20 6v5.5c0 4.8-3.4 8.6-8 9.7-4.6-1.1-8-4.9-8-9.7V6z"/><path d="m8.5 12 2.4 2.4 4.6-4.8"/>',
    fn: '<path d="M9 4.5c-2 0-3 1-3 3v2c0 1.2-.8 2.5-2.5 2.5C5.2 12 6 13.3 6 14.5v2c0 2 1 3 3 3M15 4.5c2 0 3 1 3 3v2c0 1.2.8 2.5 2.5 2.5-1.7 0-2.5 1.3-2.5 2.5v2c0 2-1 3-3 3"/>',
    arrow: '<path d="M5 12h14M13 6l6 6-6 6"/>'
  };
  function svg(name) {
    return '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">' + (ICONS[name] || ICONS.spark) + '</svg>';
  }

  // -------------------------------------------------------------------------
  // Components per pillar. `keys` = usage keys the chip lights up for.
  // -------------------------------------------------------------------------
  var CLOUD_RUN = {
    id: 'cloudrun', keys: ['cloudrun'], icon: 'run', tone: 'slate', label: 'Cloud Run',
    title: 'Google Cloud Run',
    api: 'gcloud run deploy rocket-polymorphic-search --region us-central1',
    how: 'One autoscaling FastAPI container serves this UI, every /api/* REST call and the /ws/* WebSockets.',
    latency: '< 50 ms request overhead'
  };

  var PILLARS = {
    1: {
      name: 'TimesFM',
      chips: [
        { id: 'p1-forecast', keys: ['p1-forecast'], icon: 'bq', tone: 'blue', label: 'BigQuery ML AI.FORECAST', meta: 'TimesFM 2.0',
          title: 'BigQuery ML · AI.FORECAST (TimesFM 2.0)',
          api: 'SELECT * FROM AI.FORECAST(TABLE portfolio_metrics,\n  horizon => 12, confidence_level => 0.90)',
          how: 'POST /api/pillar1/forecast runs a zero-shot TimesFM 2.0 forecast in Standard SQL — no training, no data movement.',
          latency: '~0.9 s per forecast' },
        { id: 'p1-dataset', keys: ['p1-dataset', 'p1-forecast'], icon: 'db', tone: 'blue', label: 'BigQuery dataset', meta: 'rocket_nextgen_timesfm',
          title: 'BigQuery dataset · vtxdemos.rocket_nextgen_timesfm',
          api: 'vtxdemos.rocket_nextgen_timesfm.portfolio_metrics',
          how: 'Rocket & Mr. Cooper servicing time series, scanned in place by the AI.FORECAST job.',
          latency: 'Scanned inside the forecast job' },
        { id: 'p1-tts', keys: ['tts'], icon: 'audio', tone: 'emerald', label: 'Gemini 3.8 Live TTS', meta: '24 kHz briefing',
          title: 'Gemini 3.8 Live · 24 kHz treasury briefing',
          api: "client.aio.live.connect(model='gemini-3.8-live',\n  config=LiveConnectConfig(response_modalities=['AUDIO']))",
          how: 'WebSocket /ws/live-tts streams native 24 kHz PCM audio of the forecast briefing to the browser.',
          latency: '~0.3–0.6 s to first audio' },
        CLOUD_RUN
      ]
    },
    2: {
      name: 'Veo 3.1 Reels',
      chips: [
        { id: 'veo', keys: ['veo'], icon: 'film', tone: 'red', label: 'Vertex AI Veo 3.1', meta: '9:16 MP4',
          title: 'Vertex AI Veo 3.1 (veo-3.1-generate-001 / -fast)',
          api: "client.models.generate_videos(\n  model='veo-3.1-fast-generate-001', prompt=shot, config=…)",
          how: 'POST /api/pillar2/generate starts a PredictLongRunning job and polls until the vertical 9:16 reel is ready.',
          latency: '~30–90 s per clip (fast tier)' },
        { id: 'p2-image', keys: ['p2-image'], icon: 'image', tone: 'red', label: 'Gemini 3.1 Flash Image', meta: 'keyframes',
          title: 'Gemini 3.1 Flash Image · keyframes',
          api: "client.models.generate_content(\n  model='gemini-3.1-flash-image', contents=[keyframe_prompt])",
          how: 'Generates the photoreal architectural keyframe that seeds each Veo shot.',
          latency: '~4–8 s per image' },
        { id: 'p2-flash', keys: ['p2-flash'], icon: 'spark', tone: 'emerald', label: 'Gemini 3.8 Flash', meta: 'beat sheet',
          title: 'Gemini 3.8 Flash · beat sheet & script',
          api: "client.models.generate_content(\n  model='gemini-3.8-flash', config={'response_mime_type': 'application/json'})",
          how: 'Writes the 4-scene beat sheet and the voiceover script (structured JSON), in parallel with the keyframe.',
          latency: '~1–2 s' },
        { id: 'p2-tts', keys: ['tts'], icon: 'audio', tone: 'emerald', label: 'Gemini 3.8 Live TTS', meta: 'voiceover',
          title: 'Gemini 3.8 Live · 24 kHz voiceover',
          api: "client.aio.live.connect(model='gemini-3.8-live',\n  config=LiveConnectConfig(response_modalities=['AUDIO']))",
          how: 'WebSocket /ws/live-tts reads the reel script with a prebuilt Live voice (Aoede by default).',
          latency: '~0.3–0.6 s to first audio' },
        { id: 'p2-gcs', keys: ['gcs'], icon: 'storage', tone: 'blue', label: 'Cloud Storage CDN', meta: 'reels',
          title: 'Cloud Storage multi-region CDN',
          api: 'gs://vtxdemos-abnb-images · /static/reels/*.mp4',
          how: 'Rendered reels, keyframes and preset assets are delivered from cache close to the viewer.',
          latency: '< 20 ms when cached' },
        CLOUD_RUN
      ]
    },
    3: {
      name: 'Ask Redfin',
      chips: [
        { id: 'p3-flash', keys: ['p3-flash'], icon: 'spark', tone: 'emerald', label: 'Gemini 3.8 Flash', meta: 'grounded chat',
          title: 'Gemini 3.8 Flash · grounded chat',
          api: "client.models.generate_content_stream(\n  model='gemini-3.8-flash', config=GenerateContentConfig(tools=[…]))",
          how: 'Answers each question with citations; Maps, Search and YouTube tools are attached per request.',
          latency: '~1–3 s to first token' },
        { id: 'maps', keys: ['maps'], icon: 'pin', tone: 'blue', label: 'Grounding with Google Maps',
          title: 'Grounding with Google Maps',
          api: 'types.Tool(google_maps=types.GoogleMaps())',
          how: 'Live places, walkability, schools and commute facts from 250M+ Google Maps places.',
          latency: '+0.5–1.5 s' },
        { id: 'youtube', keys: ['youtube'], icon: 'play', tone: 'red', label: 'YouTube video understanding',
          title: 'YouTube video understanding',
          api: "types.Part.from_uri(\n  file_uri='https://www.youtube.com/watch?v=…', mime_type='video/*')",
          how: 'Gemini watches the neighborhood / property tour natively — no transcript scraping.',
          latency: '~5–15 s per video' },
        { id: 'search', keys: ['search'], icon: 'search', tone: 'blue', label: 'Grounding with Google Search',
          title: 'Grounding with Google Search',
          api: 'types.Tool(google_search=types.GoogleSearch())',
          how: 'Fresh web facts (rates, taxes, grants) returned with source links.',
          latency: '+0.5–1.5 s' },
        { id: 'p3-run', keys: ['cloudrun'], icon: 'run', tone: 'slate', label: 'Cloud Run', meta: 'streaming',
          title: 'Cloud Run · streaming responses',
          api: 'FastAPI StreamingResponse on Cloud Run (us-central1)',
          how: 'Tokens and citations stream to the chat as they are generated.',
          latency: 'first byte right after the model' }
      ]
    },
    4: {
      name: 'Live Avatar',
      chips: [
        { id: 'live-api', keys: ['live-api'], icon: 'mic', tone: 'emerald', label: 'Gemini 3.8 Live API', meta: 'BidiGenerateContent',
          title: 'Gemini 3.8 Live API (BidiGenerateContent)',
          api: "client.aio.live.connect(model='gemini-3.8-live',\n  config=LiveConnectConfig(…))",
          how: 'Full-duplex WebSocket /ws/live-avatar ↔ Vertex AI Live API (us-central1) with function calling.',
          latency: '~0.3–0.7 s voice-to-voice' },
        { id: 'avatar', keys: ['avatar'], icon: 'avatar', tone: 'red', label: 'Live Video Avatar', meta: '24 fps H.264',
          title: 'Live Video Avatar (AvatarConfig)',
          api: 'LiveConnectConfig(avatar_config=AvatarConfig(…))',
          how: 'Server-rendered talking avatar streamed as H.264 (MSE) in lip-sync with the 24 kHz audio.',
          latency: '24 fps, synced to audio' },
        { id: 'audio-vad', keys: ['audio-vad'], icon: 'wave', tone: 'emerald', label: 'Native 24 kHz audio', meta: 'VAD barge-in',
          title: 'Native 24 kHz audio + server VAD barge-in',
          api: 'realtime_input_config=RealtimeInputConfig(\n  automatic_activity_detection=…)',
          how: '16 kHz mic PCM up, 24 kHz PCM down; speaking over the avatar interrupts it instantly.',
          latency: 'barge-in < 200 ms' },
        { id: 'transcription', keys: ['transcription'], icon: 'caption', tone: 'blue', label: 'In / out transcription',
          title: 'Input & output audio transcription',
          api: 'input_audio_transcription=AudioTranscriptionConfig(),\noutput_audio_transcription=AudioTranscriptionConfig()',
          how: 'Live captions for both sides of the conversation, streamed alongside the audio.',
          latency: 'streams with the audio' },
        { id: 'p4-run', keys: ['cloudrun'], icon: 'run', tone: 'slate', label: 'Cloud Run', meta: 'WebSockets',
          title: 'Cloud Run · WebSockets',
          api: "@app.websocket('/ws/live-avatar')  # FastAPI on Cloud Run",
          how: 'Session-affine WebSocket bridge between the browser and the Live API.',
          latency: '< 30 ms hop' }
      ]
    },
    5: {
      name: 'Homes & Map',
      chips: [
        { id: 'vector', keys: ['vector'], icon: 'bq', tone: 'blue', label: 'BigQuery Vector Search', meta: 'COSINE + RRF',
          title: 'BigQuery Vector Search · COSINE + RRF',
          api: "VECTOR_SEARCH(TABLE listings, 'embedding', query,\n  distance_type => 'COSINE')  -- fused with RRF",
          how: 'POST /api/pillar5/search fuses text, image and BM25 rankings with Reciprocal Rank Fusion.',
          latency: '~0.3–0.9 s' },
        { id: 'embeddings', keys: ['embeddings'], icon: 'cube', tone: 'emerald', label: 'gemini-embedding-001', meta: '+ multimodal',
          title: 'gemini-embedding-001 + multimodalembedding@001',
          api: "embed_content(model='gemini-embedding-001')      # 3072-D text\nmultimodalembedding@001                         # image + text",
          how: 'The query and every listing photo share one search space, so "walnut library" finds the room.',
          latency: '~0.1–0.25 s per query' },
        { id: 'judge', keys: ['judge'], icon: 'judge', tone: 'emerald', label: 'Gemini 3.8 Flash', meta: 'judge',
          title: 'Gemini 3.8 Flash · match judge',
          api: "client.models.generate_content(\n  model='gemini-3.8-flash', contents=[intent, listing, photos])",
          how: 'POST /api/pillar5/evaluate scores and explains each home against your intent.',
          latency: '~1–2 s' },
        { id: 'p5-image', keys: ['p5-image'], icon: 'image', tone: 'red', label: 'Gemini 3.1 Flash Image',
          title: 'Gemini 3.1 Flash Image',
          api: "client.models.generate_content(model='gemini-3.1-flash-image', …)",
          how: 'Photoreal room and exterior imagery for the 108-home catalog.',
          latency: '~4–8 s per image (pre-generated)' },
        { id: 'p5-gcs', keys: ['gcs'], icon: 'storage', tone: 'blue', label: 'Cloud Storage CDN',
          title: 'Cloud Storage CDN · gs://vtxdemos-abnb-images',
          api: 'https://storage.googleapis.com/vtxdemos-abnb-images/…',
          how: '1,500+ room, exterior and tour assets served from a multi-region bucket.',
          latency: '< 20 ms when cached' },
        { id: 'leaflet', keys: ['leaflet'], icon: 'map', tone: 'slate', label: 'Leaflet map', meta: 'Google tiles',
          title: 'Leaflet map · Google Maps tiles',
          api: "L.tileLayer('https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}')",
          how: 'Results plotted live; markers stay in sync with the vector-search ranking.',
          latency: 'tiles cached, < 16 ms per frame' },
        CLOUD_RUN
      ]
    }
  };

  var COPILOT = {
    id: 'copilot', keys: ['copilot'], icon: 'fn', tone: 'emerald', labelPrefix: 'Gemini 3.8 ', label: 'Live co-pilot · function calling', muted: true,
    title: 'Gemini 3.8 Live co-pilot · function calling',
    api: 'tools=[{function_declarations: [switch_pillar, run_forecast,\n  search_homes, generate_reel, …]}]',
    how: 'The bottom bar turns voice/text into UI actions through Live API tool calls (async sub-agents for multi-intent asks).',
    latency: '~0.5–1 s per action'
  };

  // -------------------------------------------------------------------------
  // Usage state
  // -------------------------------------------------------------------------
  var usage = {};           // key -> { last, inflight, live, pulseAt }
  // Shared infrastructure keys: pulse + "used Xs ago", but never show a pending spinner
  // (Cloud Run serves every request, so a slow call on another tab would look odd).
  var NO_INFLIGHT = { cloudrun: true, gcs: true, leaflet: true };
  function u(key) {
    if (!usage[key]) usage[key] = { last: 0, inflight: 0, live: 0, pulseAt: 0 };
    return usage[key];
  }

  var rendered = { pillar: null, chips: [] };   // chips: [{def, el}]
  var stripEl = null, pillsEl = null, drawerEl = null;

  function chipState(def) {
    var last = 0, inflight = 0, live = 0;
    for (var i = 0; i < def.keys.length; i++) {
      var s = usage[def.keys[i]];
      if (!s) continue;
      if (s.last > last) last = s.last;
      inflight += s.inflight;
      live += s.live;
    }
    return { last: last, inflight: inflight > 0, live: live > 0 };
  }

  function ago(ts) {
    var s = Math.max(0, Math.round((Date.now() - ts) / 1000));
    if (s < 2) return 'now';
    if (s < 60) return s + 's ago';
    var m = Math.round(s / 60);
    if (m < 60) return m + 'm ago';
    return Math.round(m / 60) + 'h ago';
  }

  function paintChip(entry) {
    try {
      var st = chipState(entry.def);
      var el = entry.el;
      var usedEl = el.querySelector('.gstrip-used');
      el.classList.toggle('is-live', st.live);
      el.classList.toggle('is-inflight', st.inflight && !st.live);
      el.classList.toggle('has-used', st.last > 0);
      el.classList.toggle('is-fresh', st.last > 0 && Date.now() - st.last < FRESH_MS);
      var txt = st.live ? 'LIVE' : (st.inflight ? '' : (st.last ? ago(st.last) : ''));
      if (usedEl && usedEl.textContent !== txt) usedEl.textContent = txt;
    } catch (e) { /* ignore */ }
  }

  function paintAll() {
    for (var i = 0; i < rendered.chips.length; i++) paintChip(rendered.chips[i]);
    if (tipFor) fillTip(tipFor);
  }

  function pulse(entry) {
    var el = entry.el;
    el.classList.remove('is-pulse');
    void el.offsetWidth; // restart animation
    el.classList.add('is-pulse');
    clearTimeout(el.__gstripPulseT);
    el.__gstripPulseT = setTimeout(function () { el.classList.remove('is-pulse'); }, 1000);
  }

  function touch(keys, phase, at) {
    // phase: 'start' | 'end' | 'once' | 'live-open' | 'live-close'
    // at: optional real timestamp (ms since epoch), e.g. from resource timing.
    try {
      if (!keys || !keys.length) return;
      var now = Date.now();
      var ts = typeof at === 'number' && at > 0 ? Math.min(at, now) : now;
      var pulsed = {};
      for (var i = 0; i < keys.length; i++) {
        var s = u(keys[i]);
        var trackInflight = !NO_INFLIGHT[keys[i]];
        if (phase === 'start') { if (trackInflight) s.inflight++; else s.last = Math.max(s.last, ts); }
        else if (phase === 'end') { if (trackInflight) s.inflight = Math.max(0, s.inflight - 1); s.last = Math.max(s.last, ts); }
        else if (phase === 'live-open') { s.live++; s.last = Math.max(s.last, ts); }
        else if (phase === 'live-close') { s.live = Math.max(0, s.live - 1); s.last = Math.max(s.last, ts); }
        else s.last = Math.max(s.last, ts);
        if (phase !== 'live-close' && phase !== 'end' && now - ts < 2500 && now - s.pulseAt > PULSE_THROTTLE_MS) {
          s.pulseAt = now;
          pulsed[keys[i]] = true;
        }
      }
      for (var j = 0; j < rendered.chips.length; j++) {
        var entry = rendered.chips[j];
        for (var k = 0; k < entry.def.keys.length; k++) {
          if (pulsed[entry.def.keys[k]]) { pulse(entry); break; }
        }
        paintChip(entry);
      }
      if (tipFor) fillTip(tipFor);
    } catch (e) { warn('touch failed', e); }
  }

  // -------------------------------------------------------------------------
  // URL -> usage keys
  // -------------------------------------------------------------------------
  function activePillar() {
    if (rendered.pillar) return rendered.pillar;
    return detectPillarFromDom() || 5;
  }

  function keysForUrl(url, bodyText, kind) {
    var p = String(url || '');
    var path = p;
    try { path = new URL(p, location.href).pathname + new URL(p, location.href).search; } catch (e) { /* keep raw */ }
    var keys = [];
    var isApi = /\/api\/|\/ws\//.test(path);
    if (/\/api\/pillar1\/forecast/.test(path)) keys.push('p1-forecast', 'p1-dataset');
    else if (/\/api\/pillar2\/generate/.test(path)) keys.push('veo', 'p2-image', 'p2-flash', 'gcs');
    else if (/\/api\/pillar2\/preset/.test(path)) keys.push('gcs');
    else if (/\/api\/pillar3\/ground/.test(path)) keys.push('p3-flash', 'maps', 'youtube', 'search');
    else if (/\/api\/pillar3\//.test(path)) {
      keys.push('p3-flash', 'maps', 'search');
      if (/youtu\.?be|youtube/i.test(bodyText || '')) keys.push('youtube');
    }
    else if (/\/api\/pillar4\//.test(path)) keys.push('live-api', 'audio-vad', 'transcription');
    else if (/\/api\/pillar5\/search/.test(path)) keys.push('vector', 'embeddings');
    else if (/\/api\/pillar5\/evaluate/.test(path)) keys.push('judge');
    else if (/\/api\/pillar5\/listing-video/.test(path)) keys.push('gcs');
    else if (/\/api\/pillar5\/(image|restyle|stage|render)/.test(path)) keys.push('p5-image');
    else if (/\/api\/async-subagent/.test(path)) keys.push('copilot');
    else if (/\/ws\/live-tts/.test(path)) keys.push('tts');
    else if (/\/ws\/live/.test(path)) {
      keys.push('live-api', 'audio-vad', 'transcription');
      if (!/video_avatar=0/.test(path)) keys.push('avatar');
      if (activePillar() !== 4) keys.push('copilot');
    }
    if (isApi) keys.push('cloudrun');
    if (kind === 'resource') {
      if (/storage\.googleapis\.com|storage\.cloud\.google\.com|vtxdemos-abnb-images/.test(p)) keys.push('gcs');
      if (/mt[0-3]\.google\.com\/vt|tile\.openstreetmap|basemaps\.cartocdn|arcgisonline|stadiamaps/i.test(p)) keys.push('leaflet');
    }
    return keys;
  }

  // -------------------------------------------------------------------------
  // Non-invasive network observers
  // -------------------------------------------------------------------------
  function installFetchObserver() {
    try {
      var orig = window.fetch;
      if (typeof orig !== 'function' || orig.__gstripWrapped) return;
      var wrapped = new Proxy(orig, {
        apply: function (target, thisArg, args) {
          var keys = null;
          try {
            var input = args[0];
            var url = typeof input === 'string' ? input : (input && (input.url || input.href)) || String(input);
            var init = args[1];
            var body = init && typeof init.body === 'string' ? init.body : '';
            keys = keysForUrl(url, body, 'fetch');
          } catch (e) { keys = null; }
          var result = Reflect.apply(target, thisArg, args);
          if (keys && keys.length) {
            try {
              touch(keys, 'start');
              var done = function () { touch(keys, 'end'); };
              Promise.resolve(result).then(done, done);
            } catch (e) { /* ignore */ }
          }
          return result;
        }
      });
      wrapped.__gstripWrapped = true;
      window.fetch = wrapped;
    } catch (e) { warn('fetch observer not installed', e); }
  }

  function installSocketObserver(ctorName) {
    try {
      var Orig = window[ctorName];
      if (typeof Orig !== 'function' || Orig.__gstripWrapped) return;
      var proxy = new Proxy(Orig, {
        construct: function (target, args, newTarget) {
          var inst = Reflect.construct(target, args, newTarget === proxy ? target : newTarget);
          try {
            var keys = keysForUrl(String(args[0] || ''), '', 'socket');
            if (keys.length) {
              var opened = false, closed = false;
              touch(keys, 'start');
              inst.addEventListener('open', function () {
                if (opened || closed) return;
                opened = true;
                touch(keys, 'end');
                touch(keys, 'live-open');
              });
              var finish = function () {
                if (closed) return;
                closed = true;
                if (opened) touch(keys, 'live-close');
                else touch(keys, 'end');
              };
              inst.addEventListener('close', finish);
              inst.addEventListener('error', function () {
                // EventSource retries on error; only finish when actually closed.
                if (ctorName !== 'EventSource' || inst.readyState === 2) finish();
              });
            }
          } catch (e) { /* never break the socket */ }
          return inst;
        }
      });
      try { Object.defineProperty(proxy, '__gstripWrapped', { value: true }); } catch (e) { /* ignore */ }
      window[ctorName] = proxy;
    } catch (e) { warn(ctorName + ' observer not installed', e); }
  }

  function installResourceObserver() {
    try {
      if (typeof PerformanceObserver !== 'function') return;
      var po = new PerformanceObserver(function (list) {
        try {
          var entries = list.getEntries();
          var keys = {};
          var origin = (performance && performance.timeOrigin) || 0;
          for (var i = 0; i < entries.length; i++) {
            var en = entries[i];
            if (en.initiatorType === 'fetch' || en.initiatorType === 'xmlhttprequest') continue;
            var ks = keysForUrl(en.name, '', 'resource');
            var at = origin ? Math.round(origin + (en.responseEnd || en.startTime || 0)) : 0;
            for (var j = 0; j < ks.length; j++) {
              if (ks[j] === 'gcs' || ks[j] === 'leaflet') keys[ks[j]] = Math.max(keys[ks[j]] || 0, at);
            }
          }
          for (var k in keys) {
            if (Object.prototype.hasOwnProperty.call(keys, k)) touch([k], 'once', keys[k]);
          }
        } catch (e) { /* ignore */ }
      });
      po.observe({ type: 'resource', buffered: true });
    } catch (e) { /* older browsers: ignore */ }
  }

  // -------------------------------------------------------------------------
  // Rendering
  // -------------------------------------------------------------------------
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function tabName(n) {
    try {
      var tab = document.getElementById('tab-btn-' + n);
      if (tab) {
        var clone = tab.cloneNode(true);
        var drop = clone.querySelectorAll('.pillar-num, svg');
        for (var i = 0; i < drop.length; i++) drop[i].parentNode.removeChild(drop[i]);
        var t = (clone.textContent || '').replace(/\s+/g, ' ').trim();
        if (t) return t;
      }
    } catch (e) { /* ignore */ }
    return (PILLARS[n] && PILLARS[n].name) || ('Pillar ' + n);
  }

  function chipHtml(def, i) {
    var cls = 'gstrip-chip tone-' + (def.tone || 'slate') + (def.muted ? ' gstrip-chip--muted' : '');
    var aria = def.title + '. ' + def.how + ' Typical latency ' + def.latency + '.';
    return '<button type="button" class="' + cls + '" data-gstrip-chip="' + esc(def.id) + '" style="--i:' + i + '" aria-label="' + esc(aria) + '">' +
      '<span class="gstrip-ico">' + svg(def.icon) + '</span>' +
      '<span class="gstrip-lbl">' + (def.labelPrefix ? '<span class="gstrip-wide">' + esc(def.labelPrefix) + '</span>' : '') + esc(def.label) + '</span>' +
      (def.meta ? '<span class="gstrip-meta">' + esc(def.meta) + '</span>' : '') +
      '<span class="gstrip-used" aria-live="off"></span>' +
      '</button>';
  }

  function buildPills(n) {
    var conf = PILLARS[n];
    if (!conf) return false;
    var html = '<span class="gstrip-ctx" title="Components used by this tab"><span class="gstrip-ctx-num">P' + n + '</span>' +
      '<span class="gstrip-ctx-name">' + esc(tabName(n)) + '</span></span>' +
      '<span class="gstrip-arrow" aria-hidden="true">' + svg('arrow') + '</span>';
    var defs = conf.chips.slice();
    for (var i = 0; i < defs.length; i++) html += chipHtml(defs[i], i + 1);
    html += '<span class="gstrip-sep" aria-hidden="true"></span>' + chipHtml(COPILOT, defs.length + 1);
    defs.push(COPILOT);
    pillsEl.innerHTML = html;
    pillsEl.setAttribute('data-gstrip-pillar', String(n));
    rendered.pillar = n;
    rendered.chips = [];
    var els = pillsEl.querySelectorAll('[data-gstrip-chip]');
    for (var j = 0; j < els.length && j < defs.length; j++) {
      rendered.chips.push({ def: defs[j], el: els[j] });
      els[j].__gstripDef = defs[j];
    }
    paintAll();
    return true;
  }

  var leaveTimer = null;
  function render(n, immediate) {
    try {
      n = parseInt(n, 10);
      if (!PILLARS[n] || !ensureDom()) return;
      if (rendered.pillar === n && pillsEl.getAttribute('data-gstrip-pillar') === String(n) && !leaveTimer) return;
      hideTip();
      clearTimeout(leaveTimer);
      if (immediate || rendered.pillar === null) {
        leaveTimer = null;
        pillsEl.classList.remove('is-leaving');
        buildPills(n);
        return;
      }
      pillsEl.classList.add('is-leaving');
      rendered.pillar = n; // claim early so rapid switches settle on the latest
      leaveTimer = setTimeout(function () {
        leaveTimer = null;
        try {
          buildPills(rendered.pillar);
        } catch (e) { warn('render failed', e); }
        pillsEl.classList.remove('is-leaving');
      }, LEAVE_MS);
    } catch (e) { warn('render failed', e); }
  }

  function ensureDom() {
    stripEl = document.getElementById('gcp-arch-strip');
    if (!stripEl) return false;
    pillsEl = stripEl.querySelector('.gcp-arch-pills');
    if (!pillsEl) {
      pillsEl = document.createElement('div');
      pillsEl.className = 'gcp-arch-pills';
      var btn = document.getElementById('btn-gcp-arch-drawer');
      if (btn && btn.parentNode === stripEl) stripEl.insertBefore(pillsEl, btn);
      else stripEl.appendChild(pillsEl);
    }
    pillsEl.classList.add('gstrip-pills');
    pillsEl.setAttribute('role', 'list');
    pillsEl.setAttribute('aria-label', 'Google Cloud components used by the active tab');
    // Keep the drawer toggle as the last element of the strip.
    var drawerBtn = document.getElementById('btn-gcp-arch-drawer');
    if (drawerBtn && drawerBtn.parentNode === stripEl && stripEl.lastElementChild !== drawerBtn) {
      stripEl.appendChild(drawerBtn);
    }
    drawerEl = document.getElementById('gcp-arch-drawer');
    return true;
  }

  // -------------------------------------------------------------------------
  // Tooltip
  // -------------------------------------------------------------------------
  var tipEl = null, tipFor = null;
  function ensureTip() {
    if (tipEl && document.body.contains(tipEl)) return tipEl;
    tipEl = document.createElement('div');
    tipEl.className = 'gstrip-tip';
    tipEl.setAttribute('role', 'tooltip');
    tipEl.id = 'gstrip-tip';
    document.body.appendChild(tipEl);
    return tipEl;
  }

  function fillTip(chipEl) {
    var def = chipEl && chipEl.__gstripDef;
    if (!def || !tipEl) return;
    var st = chipState(def);
    var status = st.live ? '<span class="on">● LIVE now</span>'
      : st.inflight ? '<span class="on">● calling…</span>'
      : st.last ? '<span class="on">● used ' + ago(st.last) + '</span>'
      : '<span>○ not called yet this session</span>';
    var pill = def.muted ? 'All tabs' : ('P' + rendered.pillar + ' · ' + tabName(rendered.pillar));
    tipEl.innerHTML =
      '<div class="gstrip-tip-head"><span class="gstrip-ico" style="color:var(--tone)">' + svg(def.icon) + '</span>' +
        '<span>' + esc(def.title) + '</span><span class="gstrip-tip-pill">' + esc(pill) + '</span></div>' +
      '<div class="gstrip-tip-row"><span class="gstrip-tip-k">API</span><code>' + esc(def.api) + '</code></div>' +
      '<div class="gstrip-tip-row"><span class="gstrip-tip-k">How</span><span>' + esc(def.how) + '</span></div>' +
      '<div class="gstrip-tip-foot"><span>Typical latency · ' + esc(def.latency) + '</span>' + status + '</div>';
    var tone = getComputedStyle(chipEl).getPropertyValue('--tone');
    if (tone) tipEl.style.setProperty('--tone', tone.trim());
  }

  function showTip(chipEl) {
    try {
      ensureTip();
      tipFor = chipEl;
      fillTip(chipEl);
      var r = chipEl.getBoundingClientRect();
      var w = tipEl.offsetWidth || 340, h = tipEl.offsetHeight || 140;
      var left = Math.min(Math.max(8, r.left + r.width / 2 - w / 2), window.innerWidth - w - 8);
      var top = r.bottom + 8;
      if (top + h > window.innerHeight - 8) top = Math.max(8, r.top - h - 8);
      tipEl.style.left = Math.round(left) + 'px';
      tipEl.style.top = Math.round(top) + 'px';
      tipEl.classList.add('is-on');
      chipEl.setAttribute('aria-describedby', 'gstrip-tip');
    } catch (e) { /* ignore */ }
  }

  function hideTip() {
    if (tipFor) { try { tipFor.removeAttribute('aria-describedby'); } catch (e) { /* ignore */ } }
    tipFor = null;
    if (tipEl) tipEl.classList.remove('is-on');
  }

  // Chip click → open the architecture drawer (APIs tab) and highlight this tab's card.
  function openDrawerFor(n) {
    try {
      var dr = document.getElementById('gcp-arch-drawer');
      if (dr && !dr.classList.contains('open') && typeof window.toggleGcpArchDrawer === 'function') window.toggleGcpArchDrawer();
      if (typeof window.switchGcpArchTab === 'function') window.switchGcpArchTab('apis', document.getElementById('arch-tab-btn-apis'));
      if (!dr) return;
      var cards = dr.querySelectorAll('.gcp-svc-card');
      var hit = null;
      for (var i = 0; i < cards.length; i++) {
        cards[i].classList.remove('gstrip-card-hit');
        var oc = cards[i].getAttribute('onclick') || '';
        if (!hit && oc.indexOf('switchPillar(' + n + ')') !== -1) hit = cards[i];
      }
      if (hit) {
        hit.classList.add('gstrip-card-hit');
        setTimeout(function () { hit.classList.remove('gstrip-card-hit'); }, 2200);
        if (hit.scrollIntoView) hit.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
      }
    } catch (e) { warn('drawer open failed', e); }
  }

  function bindStripEvents() {
    if (!stripEl || stripEl.__gstripBound) return;
    stripEl.__gstripBound = true;
    var chipOf = function (t) { return t && t.closest ? t.closest('[data-gstrip-chip]') : null; };
    stripEl.addEventListener('mouseover', function (e) {
      var c = chipOf(e.target);
      if (c && c !== tipFor) showTip(c);
    });
    stripEl.addEventListener('mouseout', function (e) {
      var c = chipOf(e.target);
      if (c && (!e.relatedTarget || !c.contains(e.relatedTarget))) hideTip();
    });
    stripEl.addEventListener('focusin', function (e) { var c = chipOf(e.target); if (c) showTip(c); });
    stripEl.addEventListener('focusout', function () { hideTip(); });
    stripEl.addEventListener('click', function (e) {
      var c = chipOf(e.target);
      if (!c) return;
      e.preventDefault();
      e.stopPropagation();
      hideTip();
      openDrawerFor(rendered.pillar || activePillar());
    });
    window.addEventListener('scroll', hideTip, { passive: true });
    window.addEventListener('resize', hideTip, { passive: true });
  }

  // -------------------------------------------------------------------------
  // Cleanup of stray per-card badges (card headers must never be overwritten)
  // -------------------------------------------------------------------------
  function sweepStrayBadges() {
    try {
      var strip = document.getElementById('gcp-arch-strip');
      var drawer = document.getElementById('gcp-arch-drawer');
      var nodes = document.querySelectorAll('.gcp-svc-badge, [id^="gcp-injected-badge-"]');
      for (var i = 0; i < nodes.length; i++) {
        var el = nodes[i];
        if ((strip && strip.contains(el)) || (drawer && drawer.contains(el))) continue;
        if (el.parentNode) el.parentNode.removeChild(el);
      }
    } catch (e) { /* ignore */ }
  }

  var sweepObserver = null, sweepUntil = 0, sweepQueued = false, sweepStopT = null;
  function watchForStrayBadges(ms) {
    try {
      sweepStrayBadges();
      sweepUntil = Math.max(sweepUntil, Date.now() + ms);
      if (typeof MutationObserver !== 'function' || !document.body) return;
      if (!sweepObserver) {
        sweepObserver = new MutationObserver(function () {
          if (Date.now() > sweepUntil) { sweepObserver.disconnect(); sweepObserver = null; return; }
          if (sweepQueued) return;
          sweepQueued = true;
          (window.requestAnimationFrame || setTimeout)(function () { sweepQueued = false; sweepStrayBadges(); });
        });
        sweepObserver.observe(document.body, { childList: true, subtree: true });
      }
      clearTimeout(sweepStopT);
      sweepStopT = setTimeout(function () {
        if (sweepObserver && Date.now() > sweepUntil) { sweepObserver.disconnect(); sweepObserver = null; }
      }, ms + 50);
    } catch (e) { /* ignore */ }
  }

  // -------------------------------------------------------------------------
  // Active pillar tracking
  // -------------------------------------------------------------------------
  function detectPillarFromDom() {
    try {
      var pane = document.querySelector('.pillar-pane.active');
      if (pane && pane.id) {
        var m = /pillar-(\d+)/.exec(pane.id);
        if (m && PILLARS[+m[1]]) return +m[1];
      }
    } catch (e) { /* ignore */ }
    try {
      // eslint-disable-next-line no-undef
      if (typeof currentActivePillar === 'number' && PILLARS[currentActivePillar]) return currentActivePillar;
    } catch (e) { /* ignore */ }
    return null;
  }

  function wrapSwitchPillar() {
    try {
      var orig = window.switchPillar;
      if (typeof orig !== 'function' || orig.__gstripWrapped) return;
      var wrapped = function (num) {
        var ret = orig.apply(this, arguments);
        try {
          var n = parseInt(num, 10);
          render(PILLARS[n] ? n : (detectPillarFromDom() || n));
          watchForStrayBadges(4000);
        } catch (e) { /* never break navigation */ }
        return ret;
      };
      wrapped.__gstripWrapped = true;
      wrapped.__gstripOriginal = orig;
      window.switchPillar = wrapped;
    } catch (e) { warn('switchPillar wrap failed', e); }
  }

  function observePanes() {
    try {
      if (typeof MutationObserver !== 'function') return;
      var queued = false;
      var mo = new MutationObserver(function () {
        if (queued) return;
        queued = true;
        (window.requestAnimationFrame || setTimeout)(function () {
          queued = false;
          var n = detectPillarFromDom();
          if (n && n !== rendered.pillar) render(n);
        });
      });
      var panes = document.querySelectorAll('.pillar-pane');
      for (var i = 0; i < panes.length; i++) mo.observe(panes[i], { attributes: true, attributeFilter: ['class'] });
    } catch (e) { /* ignore */ }
  }

  // -------------------------------------------------------------------------
  // Public API
  // -------------------------------------------------------------------------
  window.GcpStrip = {
    markUsed: function (keys, opts) {
      var arr = Array.isArray(keys) ? keys : [keys];
      touch(arr.filter(Boolean).map(String), (opts && opts.phase) || 'once');
    },
    render: function (n) { render(n || detectPillarFromDom() || 5, true); },
    pillars: PILLARS,
    usage: usage
  };
  window.addEventListener('gcp:used', function (e) {
    try {
      var d = (e && e.detail) || {};
      window.GcpStrip.markUsed(d.keys || d.key || [], d);
    } catch (err) { /* ignore */ }
  });

  // -------------------------------------------------------------------------
  // Boot
  // -------------------------------------------------------------------------
  installFetchObserver();
  installSocketObserver('WebSocket');
  installSocketObserver('EventSource');
  wrapSwitchPillar();

  function boot() {
    try {
      if (!ensureDom()) return;
      bindStripEvents();
      installResourceObserver();
      observePanes();
      render(detectPillarFromDom() || 5, true);
      watchForStrayBadges(12000);
      setInterval(function () {
        if (rendered.chips.length && !document.hidden) paintAll();
      }, 1000);
    } catch (e) { warn('boot failed', e); }
  }

  if (document.readyState === 'loading') {
    // Render immediately if the strip is already parsed (script sits at end of <body>),
    // then re-sync once the DOM is complete.
    if (document.getElementById('gcp-arch-strip')) boot();
    document.addEventListener('DOMContentLoaded', function () {
      try {
        wrapSwitchPillar();
        if (!stripEl) boot();
        var n = detectPillarFromDom();
        if (n && n !== rendered.pillar) render(n, true);
        watchForStrayBadges(12000);
      } catch (e) { /* ignore */ }
    });
  } else {
    boot();
  }
})();
