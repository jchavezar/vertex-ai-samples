import { useCallback, useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import './AndesiaVoice.css';

/* -----------------------------------------------------------------------------
 * AndesiaVoice — floating voice widget over Gemini Live API (native audio)
 *
 * Wire protocol (matches backend /api/live):
 *   client -> server BIN  : 16kHz PCM16 LE mic chunks
 *   client -> server TEXT : {"type":"text"|"end_turn", ...}
 *   server -> client BIN  : 24kHz PCM16 LE TTS chunks
 *   server -> client TEXT : meta | input_transcript | output_transcript |
 *                           turn_complete | interrupted | error
 *
 * Browser audio gotchas:
 *   - getUserMedia returns whatever sample rate the device gives (usually
 *     48k). We downsample to 16k in JS before sending.
 *   - Output must play at exactly 24000 Hz. We hold a dedicated AudioContext
 *     at 24kHz and queue scheduled AudioBufferSourceNodes back-to-back.
 * -------------------------------------------------------------------------- */

const API_BASE =
  (import.meta.env.VITE_API_BASE as string | undefined) ?? 'http://localhost:8000';

function wsUrlFromBase(base: string, grounding: boolean): string {
  const qs = grounding ? '?grounding=1' : '';
  // empty base => same-origin (Cloud Run prod)
  if (!base) {
    const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${proto}//${window.location.host}/api/live${qs}`;
  }
  // rewrite http(s)://host -> ws(s)://host
  return base.replace(/^http/, 'ws') + '/api/live' + qs;
}

type Status = 'idle' | 'connecting' | 'listening' | 'speaking' | 'error';

interface AndesiaVoiceProps {
  /** controlled visibility from parent */
  open: boolean;
  onClose: () => void;
  /** optional initial seed text (e.g., what user typed in the search bar) */
  seedText?: string;
}

interface DebugStats {
  wsState: string;
  micMuted: boolean;
  inChunks: number;
  inBytes: number;
  outChunks: number;
  outBytes: number;
  turnsComplete: number;
  interrupts: number;
  errors: string[];
  events: string[];
  lastChunkAgo: number;
  reconnects: number;
  sid: string;
}

const DEBUG_DEFAULT =
  typeof window !== 'undefined' &&
  (window.location.search.includes('debug=1') ||
    window.location.hash.includes('debug'));

export default function AndesiaVoice({ open, onClose, seedText }: AndesiaVoiceProps) {
  const [status, setStatus] = useState<Status>('idle');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [userTranscript, setUserTranscript] = useState('');
  const [agentTranscript, setAgentTranscript] = useState('');
  const [meta, setMeta] = useState<{ model?: string; voice?: string; grounding?: boolean } | null>(null);
  const [grounding, setGrounding] = useState<boolean>(false);
  const groundingRef = useRef<boolean>(false);
  groundingRef.current = grounding;
  /* Live grounding trace — populated as the model issues searches and the
     backend forwards chunks. Reset on every new turn so each answer shows
     only its own sources. */
  type GroundingChunk = {
    kind: 'web' | 'corpus';
    uri: string;
    title: string;
    snippet?: string;
    text?: string;
  };
  const [groundingQueries, setGroundingQueries] = useState<string[]>([]);
  const [groundingChunks, setGroundingChunks] = useState<GroundingChunk[]>([]);
  const [groundingActive, setGroundingActive] = useState<boolean>(false);
  const [selectedChunk, setSelectedChunk] = useState<GroundingChunk | null>(null);
  const [debugOpen, setDebugOpen] = useState<boolean>(DEBUG_DEFAULT);
  const [dbg, setDbg] = useState<DebugStats>({
    wsState: 'CLOSED',
    micMuted: false,
    inChunks: 0,
    inBytes: 0,
    outChunks: 0,
    outBytes: 0,
    turnsComplete: 0,
    interrupts: 0,
    errors: [],
    events: [],
    lastChunkAgo: 0,
    reconnects: 0,
    sid: '',
  });
  const dbgRef = useRef<DebugStats>(dbg);
  dbgRef.current = dbg;
  const lastChunkAtRef = useRef<number>(0);
  const logEvent = useCallback((line: string) => {
    setDbg((s) => {
      const now = new Date().toISOString().slice(11, 19);
      const events = [...s.events, `${now} ${line}`].slice(-30);
      return { ...s, events };
    });
    // also mirror to console for easy `?debug=1` capture
    // eslint-disable-next-line no-console
    console.log('[andesia-voice]', line);
  }, []);

  const wsRef = useRef<WebSocket | null>(null);
  const micCtxRef = useRef<AudioContext | null>(null);
  const micStreamRef = useRef<MediaStream | null>(null);
  const micProcRef = useRef<ScriptProcessorNode | null>(null);
  const playCtxRef = useRef<AudioContext | null>(null);
  const playCursorRef = useRef<number>(0);
  const wantOpenRef = useRef<boolean>(false);
  const reconnectAttemptsRef = useRef<number>(0);
  const reconnectTimerRef = useRef<number | null>(null);
  const seedSentRef = useRef<boolean>(false);
  const micMutedRef = useRef<boolean>(false);
  const drainTimerRef = useRef<number | null>(null);

  /* ---------- mic mute helper (echo guard) ----------------------------------
   * Web Audio playback isn't visible to the browser's WebRTC echo canceller,
   * so when Andesia speaks her audio leaks back into the mic and Gemini's VAD
   * thinks the user is speaking — which jams the next turn. We disable the
   * mic track while she's speaking, re-enable once the playback queue drains.
   * ------------------------------------------------------------------------ */
  const setMicMuted = useCallback((muted: boolean) => {
    if (micMutedRef.current === muted) return;
    micMutedRef.current = muted;
    const stream = micStreamRef.current;
    if (stream) {
      stream.getAudioTracks().forEach((t) => { t.enabled = !muted; });
    }
    setDbg((s) => ({ ...s, micMuted: muted }));
    logEvent(`mic ${muted ? 'MUTED' : 'open'}`);
  }, [logEvent]);

  /* ---------- detect when the playback queue is empty -----------------------
   * Polls every 100ms while audio is queued. As soon as currentTime catches up
   * to playCursor, we know Andesia is done speaking — flip status to listening
   * and unmute the mic. We don't rely on `turn_complete` for this because that
   * event arrives BEFORE the audio has finished playing.
   * ------------------------------------------------------------------------ */
  const scheduleDrainCheck = useCallback(() => {
    if (drainTimerRef.current !== null) return; // already polling
    const tick = () => {
      drainTimerRef.current = null;
      const ctx = playCtxRef.current;
      if (!ctx) {
        setMicMuted(false);
        setStatus((s) => (s === 'speaking' ? 'listening' : s));
        return;
      }
      const remaining = playCursorRef.current - ctx.currentTime;
      if (remaining <= 0.05) {
        // 100ms tail to let the room settle before re-opening the mic.
        window.setTimeout(() => {
          // Bail if a new chunk arrived during the tail wait.
          const ctx2 = playCtxRef.current;
          if (ctx2 && playCursorRef.current - ctx2.currentTime > 0.05) {
            scheduleDrainCheck();
            return;
          }
          setMicMuted(false);
          setStatus((s) => (s === 'speaking' ? 'listening' : s));
        }, 100);
        return;
      }
      drainTimerRef.current = window.setTimeout(tick, 120);
    };
    drainTimerRef.current = window.setTimeout(tick, 120);
  }, [setMicMuted]);

  /* ---------- audio output queue ---------- */
  const enqueuePCM24 = useCallback((pcm: Int16Array) => {
    let ctx = playCtxRef.current;
    if (!ctx) {
      // Many browsers don't honor a custom rate — we resample on insert.
      ctx = new AudioContext({ sampleRate: 24000 });
      playCtxRef.current = ctx;
      playCursorRef.current = ctx.currentTime;
    }
    const buf = ctx.createBuffer(1, pcm.length, 24000);
    const ch = buf.getChannelData(0);
    for (let i = 0; i < pcm.length; i++) ch[i] = pcm[i] / 32768;
    const src = ctx.createBufferSource();
    src.buffer = buf;
    src.connect(ctx.destination);
    const startAt = Math.max(playCursorRef.current, ctx.currentTime + 0.02);
    src.start(startAt);
    playCursorRef.current = startAt + buf.duration;
    setMicMuted(true);     // echo guard ON immediately
    setStatus('speaking');  // status reflects what's actually happening
    scheduleDrainCheck();
  }, [setMicMuted, scheduleDrainCheck]);

  /* ---------- mic capture: downsample 48k → 16k, ship Int16 LE ---------- */
  const startMicCapture = useCallback(async (ws: WebSocket) => {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
      },
    });
    micStreamRef.current = stream;

    const ctx = new AudioContext();
    micCtxRef.current = ctx;
    const src = ctx.createMediaStreamSource(stream);
    const proc = ctx.createScriptProcessor(4096, 1, 1);
    micProcRef.current = proc;

    const inRate = ctx.sampleRate;
    const ratio = inRate / 16000;

    proc.onaudioprocess = (ev) => {
      if (ws.readyState !== WebSocket.OPEN) return;
      const input = ev.inputBuffer.getChannelData(0);
      const outLen = Math.floor(input.length / ratio);
      const out = new Int16Array(outLen);
      for (let i = 0; i < outLen; i++) {
        const idx = Math.floor(i * ratio);
        const s = Math.max(-1, Math.min(1, input[idx]));
        out[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
      }
      ws.send(out.buffer);
      // bump debug counters every ~500ms to avoid overwhelming React
      const c = dbgRef.current;
      const inChunks = c.inChunks + 1;
      const inBytes = c.inBytes + out.byteLength;
      if (inChunks % 8 === 0) {
        setDbg((s) => ({ ...s, inChunks, inBytes }));
      } else {
        // mutate ref directly between flushes
        dbgRef.current = { ...c, inChunks, inBytes };
      }
    };

    src.connect(proc);
    proc.connect(ctx.destination);
  }, []);

  const teardownTransport = useCallback(() => {
    if (micProcRef.current) {
      try { micProcRef.current.disconnect(); } catch {}
      micProcRef.current = null;
    }
    if (micCtxRef.current) {
      try { micCtxRef.current.close(); } catch {}
      micCtxRef.current = null;
    }
    if (micStreamRef.current) {
      micStreamRef.current.getTracks().forEach((t) => t.stop());
      micStreamRef.current = null;
    }
    if (wsRef.current) {
      // Detach handlers before closing so the old socket's onclose doesn't
      // re-trigger our auto-reconnect path when WE were the ones tearing down
      // (e.g. user flipped the grounding toggle, or widget is unmounting).
      try { wsRef.current.onopen = null; } catch {}
      try { wsRef.current.onmessage = null; } catch {}
      try { wsRef.current.onerror = null; } catch {}
      try { wsRef.current.onclose = null; } catch {}
      try { wsRef.current.close(); } catch {}
      wsRef.current = null;
    }
  }, []);

  const teardown = useCallback(() => {
    if (reconnectTimerRef.current !== null) {
      window.clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
    if (drainTimerRef.current !== null) {
      window.clearTimeout(drainTimerRef.current);
      drainTimerRef.current = null;
    }
    teardownTransport();
    if (playCtxRef.current) {
      try { playCtxRef.current.close(); } catch {}
      playCtxRef.current = null;
      playCursorRef.current = 0;
    }
  }, [teardownTransport]);

  /* ---------- connect logic with auto-reconnect on upstream timeout ---------- */
  const connect = useCallback(() => {
    if (!wantOpenRef.current) return;
    // Cancel any pending auto-reconnect from a prior socket so we don't end
    // up with two parallel connect attempts when the user toggles grounding.
    if (reconnectTimerRef.current !== null) {
      window.clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
    teardownTransport();
    setStatus('connecting');

    let opened = false;
    const ws = new WebSocket(wsUrlFromBase(API_BASE, groundingRef.current));
    ws.binaryType = 'arraybuffer';
    wsRef.current = ws;

    ws.onopen = async () => {
      if (!wantOpenRef.current) return;
      opened = true;
      reconnectAttemptsRef.current = 0;
      logEvent('ws.open');
      setDbg((s) => ({ ...s, wsState: 'OPEN' }));
      try {
        await startMicCapture(ws);
        micMutedRef.current = false;
        setStatus('listening');
        // Prime with seedText only on the very first open of this widget session.
        if (!seedSentRef.current && seedText && seedText.trim().length > 0) {
          seedSentRef.current = true;
          ws.send(JSON.stringify({ type: 'text', text: seedText.trim() }));
        }
      } catch (err) {
        setStatus('error');
        setErrorMsg(`mic: ${(err as Error).message}`);
      }
    };

    ws.onmessage = (ev) => {
      if (typeof ev.data === 'string') {
        let payload: Record<string, unknown> = {};
        try { payload = JSON.parse(ev.data); } catch { return; }
        const k = payload.type as string;
        if (k === 'meta') {
          setMeta({
            model: payload.model as string,
            voice: payload.voice as string,
            grounding: Boolean(payload.grounding),
          });
          if (payload.sid) setDbg((s) => ({ ...s, sid: String(payload.sid) }));
          logEvent(`meta sid=${payload.sid ?? '?'} grounding=${Boolean(payload.grounding)}`);
        } else if (k === 'input_transcript') {
          setUserTranscript((s) => s + (payload.text as string));
          logEvent(`input_tx "${String(payload.text).slice(0, 40)}"`);
        } else if (k === 'output_transcript') {
          setAgentTranscript((s) => s + (payload.text as string));
        } else if (k === 'tool_call') {
          const q = String(payload.query ?? '').trim();
          if (q) {
            setGroundingActive(true);
            setGroundingQueries((s) => (s.includes(q) ? s : [...s, q]));
            logEvent(`tool_call "${q.slice(0, 60)}"`);
          }
        } else if (k === 'grounding_chunk') {
          const chunk: GroundingChunk = {
            kind: (payload.kind as 'web' | 'corpus') ?? 'web',
            uri: String(payload.uri ?? ''),
            title: String(payload.title ?? payload.uri ?? ''),
            snippet: payload.snippet ? String(payload.snippet) : undefined,
            text: payload.text ? String(payload.text) : undefined,
          };
          setGroundingChunks((s) => {
            // dedup by uri+title
            const key = `${chunk.kind}::${chunk.uri}::${chunk.title}`;
            if (s.some((c) => `${c.kind}::${c.uri}::${c.title}` === key)) return s;
            return [...s, chunk];
          });
          setGroundingActive(false);
        } else if (k === 'turn_complete') {
          setAgentTranscript((s) => s + '\n');
          setUserTranscript((s) => s + '\n');
          setGroundingActive(false);
          // Mic unmute is driven by the drain check, not by this event —
          // turn_complete arrives BEFORE the audio queue finishes playing.
          // If for some reason no audio came back, kick off a drain check
          // so we still flip back to listening.
          scheduleDrainCheck();
          setDbg((s) => ({ ...s, turnsComplete: s.turnsComplete + 1 }));
          logEvent('turn_complete');
        } else if (k === 'interrupted') {
          if (drainTimerRef.current !== null) {
            window.clearTimeout(drainTimerRef.current);
            drainTimerRef.current = null;
          }
          if (playCtxRef.current) {
            try { playCtxRef.current.close(); } catch {}
            playCtxRef.current = null;
            playCursorRef.current = 0;
          }
          setMicMuted(false);
          setStatus('listening');
          setDbg((s) => ({ ...s, interrupts: s.interrupts + 1 }));
          logEvent('interrupted');
        } else if (k === 'error') {
          setStatus('error');
          setErrorMsg((payload.message as string) || 'error');
          setDbg((s) => ({ ...s, errors: [...s.errors, String(payload.message ?? 'error')].slice(-5) }));
          logEvent(`ERROR ${String(payload.message ?? '')}`);
        }
      } else if (ev.data instanceof ArrayBuffer) {
        const pcm = new Int16Array(ev.data);
        enqueuePCM24(pcm);
        const c = dbgRef.current;
        const outChunks = c.outChunks + 1;
        const outBytes = c.outBytes + ev.data.byteLength;
        if (outChunks % 4 === 0) {
          setDbg((s) => ({ ...s, outChunks, outBytes }));
        } else {
          dbgRef.current = { ...c, outChunks, outBytes };
        }
        lastChunkAtRef.current = Date.now();
      }
    };

    ws.onerror = () => {
      // onclose will run next; don't surface a hard error if we're going to reconnect
    };

    ws.onclose = (cev) => {
      logEvent(`ws.close code=${cev.code} reason="${cev.reason || ''}" clean=${cev.wasClean}`);
      setDbg((s) => ({ ...s, wsState: 'CLOSED' }));
      // Clean up mic so a fresh ws/mic pair gets created on reconnect.
      teardownTransport();
      if (!wantOpenRef.current) {
        setStatus('idle');
        return;
      }
      // Auto-reconnect (exp backoff, capped). The Live API session times out
      // during silent gaps between turns — reconnect so the user can keep talking.
      const attempt = reconnectAttemptsRef.current + 1;
      reconnectAttemptsRef.current = attempt;
      if (attempt > 5) {
        setStatus('error');
        setErrorMsg(opened
          ? 'La sesión se reinició demasiadas veces. Cierra y reintenta.'
          : 'No se pudo conectar al backend.');
        return;
      }
      const delay = Math.min(300 * 2 ** (attempt - 1), 3000);
      setStatus('connecting');
      setDbg((s) => ({ ...s, reconnects: s.reconnects + 1 }));
      logEvent(`reconnect #${attempt} in ${delay}ms`);
      reconnectTimerRef.current = window.setTimeout(() => {
        reconnectTimerRef.current = null;
        connect();
      }, delay);
    };
  }, [seedText, startMicCapture, enqueuePCM24, teardownTransport, setMicMuted, scheduleDrainCheck, logEvent]);

  /* ---------- connect / disconnect on open toggle ---------- */
  useEffect(() => {
    wantOpenRef.current = open;
    if (!open) {
      teardown();
      setStatus('idle');
      setUserTranscript('');
      setAgentTranscript('');
      setErrorMsg(null);
      setGroundingQueries([]);
      setGroundingChunks([]);
      setGroundingActive(false);
      setSelectedChunk(null);
      reconnectAttemptsRef.current = 0;
      seedSentRef.current = false;
      return;
    }
    setErrorMsg(null);
    setGroundingQueries([]);
    setGroundingChunks([]);
    setGroundingActive(false);
    setSelectedChunk(null);
    reconnectAttemptsRef.current = 0;
    seedSentRef.current = false;
    connect();
    return () => {
      wantOpenRef.current = false;
      teardown();
    };
  }, [open, connect, teardown]);

  /* ---------- reconnect when grounding toggle flips while open ----------
   * Live API config (incl. tools) is fixed at session start. Toggling
   * grounding requires tearing down the WS and opening a fresh one with
   * ?grounding=1 in the query. Transcripts intentionally persist. */
  const prevGroundingRef = useRef(grounding);
  useEffect(() => {
    if (prevGroundingRef.current === grounding) return;
    prevGroundingRef.current = grounding;
    if (!open) return;
    reconnectAttemptsRef.current = 0;
    seedSentRef.current = true; // don't re-send seed on toggle
    connect();
  }, [grounding, open, connect]);

  if (!open) return null;

  const statusLabel: Record<Status, string> = {
    idle: 'Listo',
    connecting: 'Conectando…',
    listening: 'Escuchando…',
    speaking: 'Andesia hablando…',
    error: 'Error',
  };

  const showGroundingPanel =
    grounding && (groundingActive || groundingQueries.length > 0 || groundingChunks.length > 0);

  // Portal to <body> so the floating panel isn't clipped by ancestors that
  // happen to use transform/overflow (which break `position: fixed`).
  const panel = (
    <>
    {showGroundingPanel && (
      <aside className="andesia-grounding" aria-label="Fuentes de grounding en vivo">
        <header className="andesia-grounding__header">
          <span className="material-symbols-outlined andesia-grounding__icon" aria-hidden>travel_explore</span>
          <div>
            <div className="andesia-grounding__title">Fuentes en vivo</div>
            <div className="andesia-grounding__sub">Live grounding · Google Search + corpus CCLA</div>
          </div>
        </header>

        {groundingQueries.length > 0 && (
          <section className="andesia-grounding__section">
            <div className="andesia-grounding__section-title">
              <span className="material-symbols-outlined" aria-hidden style={{ fontSize: 14 }}>search</span>
              Búsquedas
              {groundingActive && <span className="andesia-grounding__pulse" aria-hidden />}
            </div>
            <ul className="andesia-grounding__queries">
              {groundingQueries.map((q, i) => (
                <li key={`${q}-${i}`} className="andesia-grounding__query">"{q}"</li>
              ))}
            </ul>
          </section>
        )}

        {groundingChunks.length > 0 && (
          <section className="andesia-grounding__section">
            <div className="andesia-grounding__section-title">
              <span className="material-symbols-outlined" aria-hidden style={{ fontSize: 14 }}>menu_book</span>
              Fuentes ({groundingChunks.length})
            </div>
            <ul className="andesia-grounding__chunks">
              {groundingChunks.map((c, i) => {
                const isSelected =
                  selectedChunk &&
                  selectedChunk.uri === c.uri &&
                  selectedChunk.title === c.title;
                const hasFullText = !!(c.text && c.text.length > 0);
                return (
                  <li
                    key={`${c.uri}-${i}`}
                    className={[
                      'andesia-grounding__chunk',
                      `andesia-grounding__chunk--${c.kind}`,
                      isSelected ? 'andesia-grounding__chunk--selected' : '',
                    ].filter(Boolean).join(' ')}
                  >
                    <div className="andesia-grounding__chunk-head">
                      <span className={`andesia-grounding__chunk-kind andesia-grounding__chunk-kind--${c.kind}`}>
                        {c.kind === 'web' ? 'web' : 'corpus'}
                      </span>
                      {c.uri ? (
                        <a
                          href={c.uri}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="andesia-grounding__chunk-title"
                          onClick={(e) => e.stopPropagation()}
                        >
                          {c.title || c.uri}
                        </a>
                      ) : (
                        <span className="andesia-grounding__chunk-title">{c.title}</span>
                      )}
                    </div>
                    {c.snippet && <p className="andesia-grounding__chunk-snippet">{c.snippet}</p>}
                    {hasFullText && (
                      <button
                        type="button"
                        className="andesia-grounding__view-snippet"
                        onClick={() => setSelectedChunk(isSelected ? null : c)}
                        aria-pressed={!!isSelected}
                      >
                        <span className="material-symbols-outlined" aria-hidden style={{ fontSize: 13 }}>
                          {isSelected ? 'close' : 'article'}
                        </span>
                        {isSelected ? 'Cerrar texto' : 'Ver texto usado'}
                      </button>
                    )}
                  </li>
                );
              })}
            </ul>
          </section>
        )}

        {groundingActive && groundingQueries.length === 0 && groundingChunks.length === 0 && (
          <div className="andesia-grounding__empty">
            <span className="andesia-grounding__pulse" aria-hidden />
            Andesia está consultando…
          </div>
        )}
      </aside>
    )}
    <div className="andesia-voice" role="dialog" aria-label="Asistente de voz Andesia">
      <button
        type="button"
        className="andesia-voice__close"
        onClick={onClose}
        aria-label="Cerrar"
      >
        <span className="material-symbols-outlined" aria-hidden>close</span>
      </button>

      <div className={`andesia-voice__orb andesia-voice__orb--${status}`} aria-hidden>
        <span />
        <span />
        <span />
      </div>

      <p className="andesia-voice__status">
        <span className={`andesia-voice__dot andesia-voice__dot--${status}`} aria-hidden />
        {statusLabel[status]}
      </p>

      {meta && (
        <p className="andesia-voice__meta">
          <strong>{meta.voice}</strong> · {meta.model} · es-US
          {meta.grounding ? ' · grounded' : ''}
        </p>
      )}

      <label
        className={`andesia-voice__toggle${grounding ? ' is-on' : ''}`}
        title="Cuando está activo, Andesia consulta cajalosandes.cl + Google Search en cada turno (más preciso, +1-1.5s al primer audio)."
      >
        <input
          type="checkbox"
          checked={grounding}
          onChange={(e) => setGrounding(e.target.checked)}
        />
        <span className="andesia-voice__toggle-track" aria-hidden>
          <span className="andesia-voice__toggle-thumb" />
        </span>
        <span className="andesia-voice__toggle-label">
          Grounding {grounding ? 'ON' : 'OFF'}
        </span>
      </label>

      {errorMsg && <p className="andesia-voice__error">{errorMsg}</p>}

      <div className="andesia-voice__transcripts">
        {userTranscript && (
          <div className="andesia-voice__bubble andesia-voice__bubble--user">
            <span className="andesia-voice__bubble-label">Tú</span>
            <p>{userTranscript.trim()}</p>
          </div>
        )}
        {agentTranscript && (
          <div className="andesia-voice__bubble andesia-voice__bubble--agent">
            <span className="andesia-voice__bubble-label">Andesia</span>
            <p>{agentTranscript.trim()}</p>
          </div>
        )}
      </div>

      <p className="andesia-voice__hint">
        Habla en voz alta. Andesia te responderá con voz natural en tiempo real.
      </p>

      <button
        type="button"
        className="andesia-voice__debug-toggle"
        onClick={() => setDebugOpen((v) => !v)}
        title="Mostrar / ocultar debug"
      >
        {debugOpen ? 'hide debug' : 'debug'}
      </button>

      {debugOpen && (
        <div className="andesia-voice__debug">
          <div className="andesia-voice__debug-row">
            <span>ws</span><b>{dbg.wsState}</b>
            <span>mic</span><b>{dbg.micMuted ? 'MUTED' : 'open'}</b>
            <span>sid</span><b>{dbg.sid || '—'}</b>
          </div>
          <div className="andesia-voice__debug-row">
            <span>in</span><b>{dbg.inChunks}/{Math.round(dbg.inBytes / 1024)}k</b>
            <span>out</span><b>{dbg.outChunks}/{Math.round(dbg.outBytes / 1024)}k</b>
            <span>turns</span><b>{dbg.turnsComplete}</b>
            <span>int</span><b>{dbg.interrupts}</b>
            <span>rc</span><b>{dbg.reconnects}</b>
          </div>
          {dbg.errors.length > 0 && (
            <div className="andesia-voice__debug-err">
              {dbg.errors.map((e, i) => <div key={i}>err: {e}</div>)}
            </div>
          )}
          <div className="andesia-voice__debug-events">
            {dbg.events.slice(-12).map((e, i) => (
              <div key={i}>{e}</div>
            ))}
          </div>
        </div>
      )}
    </div>
    </>
  );

  if (typeof document === 'undefined') return panel;
  return createPortal(panel, document.body);
}
