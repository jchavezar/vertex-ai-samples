import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { ANDESIA_DEMO_CONVERSATION } from '../../mocks';
import type { Citation, ReasoningStep, ToolCall, Turn, TurnRole } from '../../mocks';
import AndesiaInspector from './AndesiaInspector';
import type { InspectorState } from './AndesiaInspector';
import './AndesiaChat.css';

/* ===========================================================================
 * AndesiaChat
 *   Floating multi-agent assistant for Caja Los Andes (Andesia).
 *   - FAB bottom-right opens a slide-up panel (chat) with a left-side
 *     "Inspector" panel showing reasoning / tool calls / citations live.
 *   - Demo mode plays the canned ANDESIA_DEMO_CONVERSATION transcript with
 *     realistic per-word typing, sequential reasoning steps, animated tool
 *     execution and citations appearing in real time.
 *   - The text input is intentionally disabled — this is a pre-recorded demo.
 *
 * Mount: <AndesiaChat />  (no props required)
 * =========================================================================== */

/* ---------- Types -------------------------------------------------------- */

type DisplayMessage =
  | {
      kind: 'agent';
      id: string;
      role: TurnRole;
      label: string;
      color: string;
      text: string; // current rendered text (animating word by word)
      fullText: string;
      citations?: Citation[];
      uiCard?: { type: string; payload: Record<string, unknown> };
      isStreaming: boolean;
    }
  | {
      kind: 'user';
      id: string;
      text: string;
    }
  | {
      kind: 'system';
      id: string;
      label: string;
      icon: string;
    }
  | {
      kind: 'typing';
      id: string;
      role: TurnRole;
      label: string;
      color: string;
    };

/* ---------- Constants ---------------------------------------------------- */

// 1 word ≈ 200ms typing pace requested in the spec, scaled a bit for keynote
const WORD_DELAY_MS = 80; // we keep it snappy: ~5 words/sec
const STEP_REASONING_GAP_MS = 320; // gap between reasoning steps
const TOOL_RUNNING_TIME_MS = 520; // visual "running" time before flipping to success
const HANDOFF_PAUSE_MS = 350;
const SYSTEM_EVENT_PAUSE_MS = 400;

const SYSTEM_EVENT_LABEL: Record<string, { label: string; icon: string }> = {
  session_start: { label: 'Sesión iniciada · SSO Keycloak', icon: 'login' },
  memory_loaded: { label: 'Memory Bank cargada (5 hechos del afiliado)', icon: 'psychology' },
  document_uploaded: { label: 'Documento adjunto · liquidación pensión', icon: 'upload_file' },
  voice_session_open: { label: 'Modo voz activado · Gemini Live (es-CL)', icon: 'graphic_eq' },
  session_close: { label: 'Sesión cerrada · trace en Cloud Trace', icon: 'task_alt' },
};

const COLOR_MAP: Record<string, string> = {
  azul: '#0076a9',
  amarillo: '#d59608',
  verde: '#008744',
  gris: '#586264',
  rojo: '#b21e27',
  morado: '#873299',
};

/* ---------- Helpers ------------------------------------------------------ */

function colorFor(color: string | undefined, fallback = '#0076a9'): string {
  if (!color) return fallback;
  return COLOR_MAP[color] ?? fallback;
}

function avatarInitials(label: string): string {
  // "Andesia · Concierge" -> "AC", "CreditoAgent" -> "CA"
  const cleaned = label.replace('·', ' ').replace(/[^a-zA-ZÀ-ÿ\s]/g, '').trim();
  const parts = cleaned.split(/\s+/).filter(Boolean);
  if (parts.length === 0) return 'A';
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[1][0]).toUpperCase();
}

function formatCLP(n: number): string {
  return n.toLocaleString('es-CL');
}

/* ---------- Component ---------------------------------------------------- */

export default function AndesiaChat() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [hasFinished, setHasFinished] = useState(false);

  // Inspector state — replaced fully on each new agent turn,
  // mutated incrementally as reasoning/tool calls/citations animate in.
  const [inspectorState, setInspectorState] = useState<InspectorState>({
    activeRole: null,
    recentRoles: [],
    reasoning: [],
    toolCalls: [],
    citations: [],
    toolCount: 0,
    handoffCount: 0,
  });

  const bodyRef = useRef<HTMLDivElement>(null);
  const cancelRef = useRef(false);

  /* ---- auto-scroll on new content -------------------------------------- */
  useEffect(() => {
    const el = bodyRef.current;
    if (!el) return;
    el.scrollTop = el.scrollHeight;
  }, [messages]);

  /* ---- cancel any pending playback when widget closes ------------------ */
  useEffect(() => {
    if (!open) {
      cancelRef.current = true;
    } else {
      cancelRef.current = false;
    }
  }, [open]);

  /* ---- ESC closes panel ------------------------------------------------ */
  useEffect(() => {
    if (!open) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false);
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [open]);

  /* ---- Sleep helper that respects cancel ------------------------------ */
  const sleep = (ms: number): Promise<boolean> =>
    new Promise((resolve) => {
      const t = setTimeout(() => resolve(!cancelRef.current), ms);
      // ensure we don't leak if cancelled mid-flight
      if (cancelRef.current) {
        clearTimeout(t);
        resolve(false);
      }
    });

  /* ---- Reset state -------------------------------------------------- */
  const resetState = useCallback(() => {
    setMessages([]);
    setHasFinished(false);
    setInspectorState({
      activeRole: null,
      recentRoles: [],
      reasoning: [],
      toolCalls: [],
      citations: [],
      toolCount: 0,
      handoffCount: 0,
    });
  }, []);

  /* ---- The big playback engine ----------------------------------------- */
  const playConversation = useCallback(async () => {
    if (isPlaying) return;
    cancelRef.current = false;
    resetState();
    setIsPlaying(true);

    const transcript: Turn[] = ANDESIA_DEMO_CONVERSATION;

    for (const turn of transcript) {
      if (cancelRef.current) break;

      if (turn.kind === 'system_event') {
        const meta = SYSTEM_EVENT_LABEL[turn.event] ?? {
          label: turn.event,
          icon: 'info',
        };
        setMessages((m) => [
          ...m,
          { kind: 'system', id: `sys-${turn.turn_index}`, label: meta.label, icon: meta.icon },
        ]);
        if (!(await sleep(SYSTEM_EVENT_PAUSE_MS))) break;
        continue;
      }

      if (turn.kind === 'user_message') {
        setMessages((m) => [
          ...m,
          { kind: 'user', id: `u-${turn.turn_index}`, text: turn.text },
        ]);
        if (!(await sleep(550))) break;
        continue;
      }

      // === agent_message =================================================
      const t = turn;

      // 1. show typing indicator
      const typingId = `typ-${t.turn_index}`;
      setMessages((m) => [
        ...m,
        {
          kind: 'typing',
          id: typingId,
          role: t.role,
          label: t.agent_label,
          color: colorFor(t.agent_color),
        },
      ]);

      // 2. set inspector active agent + reset its panels
      setInspectorState((prev) => ({
        ...prev,
        activeRole: t.role,
        recentRoles: prev.recentRoles.includes(t.role) ? prev.recentRoles : [...prev.recentRoles, t.role],
        reasoning: [],
        toolCalls: [],
      }));

      // 3. animate reasoning steps one by one
      if (t.reasoning && t.reasoning.length > 0) {
        for (const step of t.reasoning) {
          if (cancelRef.current) break;
          setInspectorState((prev) => ({
            ...prev,
            reasoning: appendIfNew<ReasoningStep>(prev.reasoning, step, (r) => r.step_index),
          }));
          if (!(await sleep(STEP_REASONING_GAP_MS))) break;
        }
      }
      if (cancelRef.current) break;

      // 4. animate tool calls (running -> success)
      if (t.tool_calls && t.tool_calls.length > 0) {
        for (const tc of t.tool_calls) {
          if (cancelRef.current) break;
          // insert in "running" state first
          const runningTc: ToolCall = { ...tc, status: 'running' };
          setInspectorState((prev) => ({
            ...prev,
            toolCalls: appendIfNew<ToolCall>(prev.toolCalls, runningTc, (x) => x.id),
          }));
          if (!(await sleep(TOOL_RUNNING_TIME_MS))) break;
          // flip to its real final status
          setInspectorState((prev) => ({
            ...prev,
            toolCalls: prev.toolCalls.map((x) => (x.id === tc.id ? tc : x)),
            toolCount: prev.toolCount + 1,
          }));
          if (!(await sleep(180))) break;
        }
      }
      if (cancelRef.current) break;

      // 5. record handoffs
      if (t.handoffs && t.handoffs.length > 0) {
        setInspectorState((prev) => ({
          ...prev,
          handoffCount: prev.handoffCount + (t.handoffs?.length ?? 0),
        }));
        if (!(await sleep(HANDOFF_PAUSE_MS))) break;
      }

      // 6. swap typing indicator for the streaming bubble
      const messageId = `m-${t.turn_index}`;
      setMessages((m) =>
        m
          .filter((x) => x.id !== typingId)
          .concat({
            kind: 'agent',
            id: messageId,
            role: t.role,
            label: t.agent_label,
            color: colorFor(t.agent_color),
            text: '',
            fullText: t.text,
            citations: t.citations,
            uiCard: t.ui_card,
            isStreaming: true,
          }),
      );

      // 7. type the words progressively
      const words = t.text.split(/(\s+)/); // keep whitespace as separate tokens
      let acc = '';
      for (let i = 0; i < words.length; i++) {
        if (cancelRef.current) break;
        acc += words[i];
        setMessages((m) =>
          m.map((x) => (x.id === messageId && x.kind === 'agent' ? { ...x, text: acc } : x)),
        );
        // skip pure whitespace tokens for delay
        if (words[i].trim().length > 0) {
          if (!(await sleep(WORD_DELAY_MS))) break;
        }
      }
      if (cancelRef.current) break;

      // 8. add citations to inspector
      if (t.citations && t.citations.length > 0) {
        for (const c of t.citations) {
          setInspectorState((prev) => ({
            ...prev,
            citations: appendIfNew<Citation>(prev.citations, c, (x) => x.id),
          }));
          if (!(await sleep(160))) break;
        }
      }

      // 9. mark message as done
      setMessages((m) =>
        m.map((x) =>
          x.id === messageId && x.kind === 'agent' ? { ...x, isStreaming: false } : x,
        ),
      );

      if (!(await sleep(420))) break;
    }

    setIsPlaying(false);
    setHasFinished(true);
    setInspectorState((prev) => ({ ...prev, activeRole: null }));
  }, [isPlaying, resetState]);

  const handleClose = useCallback(() => {
    cancelRef.current = true;
    setOpen(false);
  }, []);

  const handleOpen = useCallback(() => {
    setOpen(true);
  }, []);

  const handleReset = useCallback(() => {
    cancelRef.current = true;
    // give pending awaits a tick to bail
    setTimeout(() => {
      resetState();
      setIsPlaying(false);
    }, 30);
  }, [resetState]);

  // memoize whether we have any non-system messages (to decide empty state)
  const hasContent = useMemo(
    () => messages.some((m) => m.kind === 'user' || m.kind === 'agent' || m.kind === 'typing'),
    [messages],
  );

  return (
    <>
      {/* ---- FAB ------------------------------------------------------- */}
      <button
        type="button"
        className={`andesia-fab ${open ? 'is-hidden' : ''}`}
        onClick={handleOpen}
        aria-label="Abrir Andesia, asistente IA de Caja Los Andes"
      >
        <span className="material-symbols-outlined andesia-fab__icon">auto_awesome</span>
        <span className="andesia-fab__badge">IA</span>
      </button>

      {/* ---- Backdrop -------------------------------------------------- */}
      <div
        className={`andesia-backdrop ${open ? 'is-open' : ''}`}
        onClick={handleClose}
        aria-hidden="true"
      />

      {/* ---- Surface (chat panel + inspector) ------------------------- */}
      <div className={`andesia-surface ${open ? 'is-open' : ''}`} role="dialog" aria-label="Andesia">
        {/* The chat panel sits on the right (flex-direction: row-reverse) */}
        <section className="andesia-panel">
          <header className="andesia-panel__header">
            <div className="andesia-panel__avatar">
              <span className="material-symbols-outlined">auto_awesome</span>
            </div>
            <div className="andesia-panel__title">
              <span className="andesia-panel__name">Andesia · IA Caja Los Andes</span>
              <span className="andesia-panel__sub">
                <span className="material-symbols-outlined">bolt</span>
                powered by Vertex AI · ADK
              </span>
            </div>
            <div className="andesia-panel__actions">
              <button
                type="button"
                className="andesia-icon-btn"
                onClick={handleClose}
                aria-label="Cerrar Andesia"
              >
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>
          </header>

          <div className="andesia-panel__body" ref={bodyRef}>
            {!hasContent ? (
              <EmptyLauncher onPlay={playConversation} disabled={isPlaying} />
            ) : (
              <>
                {messages.map((m) => (
                  <MessageView key={m.id} msg={m} />
                ))}
                {hasFinished && !isPlaying && (
                  <div style={{ display: 'flex', justifyContent: 'center', marginTop: 8 }}>
                    <button
                      type="button"
                      className="andesia-replay-btn andesia-replay-btn--ghost"
                      onClick={handleReset}
                    >
                      <span className="material-symbols-outlined">restart_alt</span>
                      Iniciar nueva consulta
                    </button>
                  </div>
                )}
              </>
            )}
          </div>

          <footer className="andesia-panel__footer">
            <form
              className="andesia-input"
              onSubmit={(e) => {
                e.preventDefault();
              }}
            >
              <input
                className="andesia-input__field"
                placeholder={isPlaying ? 'Andesia está respondiendo…' : 'Escribe tu consulta (demo · solo lectura)'}
                disabled
                aria-disabled="true"
              />
              <button
                type="submit"
                className="andesia-input__send"
                disabled
                aria-label="Enviar"
              >
                <span className="material-symbols-outlined">send</span>
              </button>
            </form>
            <div className="andesia-footer__hint">
              <span className="material-symbols-outlined">shield_lock</span>
              Conversación demo · datos sintéticos · keynote 20-abril-2026
            </div>
          </footer>
        </section>

        <AndesiaInspector state={inspectorState} isPlaying={isPlaying} />
      </div>
    </>
  );
}

/* =========================================================================
 * Subcomponents
 * ========================================================================= */

function EmptyLauncher({ onPlay, disabled }: { onPlay: () => void; disabled: boolean }) {
  return (
    <div className="andesia-empty">
      <div className="andesia-empty__hero">
        <span className="material-symbols-outlined">auto_awesome</span>
      </div>
      <div className="andesia-empty__title">Hola, soy Andesia</div>
      <div className="andesia-empty__sub">
        Asistente multi-agente de Caja Los Andes. Coordino crédito, beneficios,
        documentos y voz para resolverte en una sola conversación.
      </div>
      <button
        type="button"
        className="andesia-replay-btn"
        onClick={onPlay}
        disabled={disabled}
      >
        <span className="material-symbols-outlined">play_arrow</span>
        Reproducir conversación demo
      </button>
      <div className="andesia-empty__chips">
        <span className="andesia-empty__chip">consolidación deuda</span>
        <span className="andesia-empty__chip">bono bodas de oro</span>
        <span className="andesia-empty__chip">document AI</span>
        <span className="andesia-empty__chip">voz live</span>
      </div>
    </div>
  );
}

function MessageView({ msg }: { msg: DisplayMessage }) {
  if (msg.kind === 'system') {
    return (
      <div className="andesia-sys">
        <span className="material-symbols-outlined">{msg.icon}</span>
        {msg.label}
      </div>
    );
  }

  if (msg.kind === 'user') {
    return (
      <div className="andesia-msg andesia-msg--user">
        <div className="andesia-msg__head">
          <span style={{ marginRight: 4 }}>Tú</span>
          <span
            className="andesia-msg__avatar"
            style={{ background: '#326295' }}
            aria-hidden="true"
          >
            T
          </span>
        </div>
        <div className="andesia-msg__bubble">{msg.text}</div>
      </div>
    );
  }

  if (msg.kind === 'typing') {
    return (
      <div className="andesia-msg andesia-msg--agent">
        <div className="andesia-msg__head">
          <span
            className="andesia-msg__avatar"
            style={{ background: msg.color }}
            aria-hidden="true"
          >
            {avatarInitials(msg.label)}
          </span>
          <span>{msg.label}</span>
        </div>
        <div className="andesia-typing" aria-label="Escribiendo">
          <span className="andesia-typing__dot" />
          <span className="andesia-typing__dot" />
          <span className="andesia-typing__dot" />
        </div>
      </div>
    );
  }

  // agent
  return (
    <div className="andesia-msg andesia-msg--agent">
      <div className="andesia-msg__head">
        <span
          className="andesia-msg__avatar"
          style={{ background: msg.color }}
          aria-hidden="true"
        >
          {avatarInitials(msg.label)}
        </span>
        <span>{msg.label}</span>
      </div>
      <div className="andesia-msg__bubble">
        <RichText text={msg.text} />
        {msg.isStreaming && <span className="andesia-msg__caret" aria-hidden="true" />}
      </div>

      {!msg.isStreaming && msg.uiCard && <UiCard card={msg.uiCard} />}
      {!msg.isStreaming && msg.citations && msg.citations.length > 0 && (
        <div className="andesia-msg__citations">
          {msg.citations.map((c) => (
            <span key={c.id} className="andesia-cite-pill" title={c.paragraph_excerpt}>
              <span className="material-symbols-outlined">menu_book</span>
              {truncateMid(c.source_title, 32)}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

/* Render **bold** segments inline */
function RichText({ text }: { text: string }) {
  const parts: Array<{ b: boolean; v: string }> = [];
  let rest = text;
  const re = /\*\*([^*]+)\*\*/;
  let m: RegExpExecArray | null;
  while ((m = re.exec(rest))) {
    if (m.index > 0) parts.push({ b: false, v: rest.slice(0, m.index) });
    parts.push({ b: true, v: m[1] });
    rest = rest.slice(m.index + m[0].length);
  }
  if (rest.length > 0) parts.push({ b: false, v: rest });
  return (
    <>
      {parts.map((p, i) =>
        p.b ? <strong key={i}>{p.v}</strong> : <span key={i}>{p.v}</span>,
      )}
    </>
  );
}

function UiCard({ card }: { card: { type: string; payload: Record<string, unknown> } }) {
  const { type, payload } = card;

  if (type === 'producto_credito') {
    return (
      <div className="andesia-card">
        <div className="andesia-card__head">
          <span className="material-symbols-outlined">credit_score</span>
          <span>Simulación crédito</span>
        </div>
        <div className="andesia-card__title">{String(payload.producto ?? 'Crédito')}</div>
        <div className="andesia-card__rows">
          <Row label="Monto" value={`$${formatCLP(Number(payload.monto_clp ?? 0))}`} />
          <Row label="Cuota / mes" value={`$${formatCLP(Number(payload.cuota_mensual_clp ?? 0))}`} />
          <Row label="CAE" value={`${payload.cae_anual_pct}%`} />
          <Row label="Plazo" value={`${payload.plazo_meses} meses`} />
        </div>
        <button type="button" className="andesia-card__cta">Ver detalle</button>
        {payload.disclaimer ? (
          <div className="andesia-card__disclaimer">{String(payload.disclaimer)}</div>
        ) : null}
      </div>
    );
  }

  if (type === 'beneficio') {
    return (
      <div className="andesia-card">
        <div className="andesia-card__head">
          <span className="material-symbols-outlined">volunteer_activism</span>
          <span>Beneficio</span>
        </div>
        <div className="andesia-card__title">{String(payload.beneficio ?? 'Beneficio')}</div>
        <div className="andesia-card__rows">
          <Row label="Beneficiario" value={String(payload.beneficiario ?? '—')} />
          <Row label="Monto" value={`$${formatCLP(Number(payload.monto_clp ?? 0))}`} />
          <Row label="Marco legal" value={String(payload.ley ?? '—')} />
          <Row label="Pago est." value={String(payload.fecha_pago_estimada ?? '—')} />
        </div>
        <button type="button" className="andesia-card__cta">Iniciar trámite</button>
      </div>
    );
  }

  if (type === 'formulario') {
    return (
      <div className="andesia-card">
        <div className="andesia-card__head">
          <span className="material-symbols-outlined">draft</span>
          <span>Solicitud auto-generada</span>
        </div>
        <div className="andesia-card__title">{String(payload.numero_solicitud ?? 'SOL-XXXX')}</div>
        <div className="andesia-card__rows" style={{ gridTemplateColumns: '1fr' }}>
          {Array.isArray(payload.campos_autollenados) &&
            (payload.campos_autollenados as Array<{ campo: string; valor: string }>)
              .slice(0, 4)
              .map((f, i) => <Row key={i} label={f.campo} value={String(f.valor)} />)}
        </div>
        <button type="button" className="andesia-card__cta">
          {String(payload.cta ?? 'Continuar')}
        </button>
      </div>
    );
  }

  if (type === 'comparativa') {
    return (
      <div className="andesia-card">
        <div className="andesia-card__head">
          <span className="material-symbols-outlined">travel_explore</span>
          <span>Recomendación proactiva</span>
        </div>
        <div className="andesia-card__title">{String(payload.hotel ?? 'Oferta')}</div>
        <div className="andesia-card__rows">
          <Row label="Tarifa pública" value={`$${formatCLP(Number(payload.precio_publico_clp ?? 0))}`} />
          <Row label="Tarifa afiliada" value={`$${formatCLP(Number(payload.precio_afiliada_clp ?? 0))}`} />
          <Row label="Ventana" value={String(payload.ventana ?? '—')} />
          <Row label="Cupos" value={String(payload.cupos ?? '—')} />
        </div>
        <button type="button" className="andesia-card__cta">Apartar 24h</button>
      </div>
    );
  }

  return null;
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="andesia-card__row">
      <span className="andesia-card__row-label">{label}</span>
      <span className="andesia-card__row-value">{value}</span>
    </div>
  );
}

function truncateMid(s: string, max: number): string {
  if (s.length <= max) return s;
  const head = Math.ceil(max * 0.6);
  const tail = max - head - 1;
  return `${s.slice(0, head)}…${s.slice(s.length - tail)}`;
}

/* ---- helpers ----------------------------------------------------------- */

function appendIfNew<T>(arr: T[], item: T, getKey: (x: T) => string | number): T[] {
  const k = getKey(item);
  if (arr.some((x) => getKey(x) === k)) return arr;
  return [...arr, item];
}
