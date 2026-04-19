/* Andesia Crédito — agent-driven credit simulator overlay.
 *
 * Layout: full-viewport modal split into a left chat-wizard and a right
 * dashboard. The agent does the canonical first computation (BuiltInCode +
 * VertexAiSearch). Subsequent slider tweaks recompute client-side via
 * credit_math.ts so the dashboard stays at 0ms latency.
 *
 * Events from the WebSocket bubble to two consumers:
 *   1. Chat panel — text deltas + grounding chips
 *   2. Architecture pipeline (when open) — tool_call_start/end animations
 */
import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';
import './CreditSimulator.css';
import { AgentTrace } from './AgentTrace';
import {
  amortize,
  compareBank,
  formatCLP,
  projectSavings,
  type AmortizationResult,
} from './credit_math';
import type { CreditEvent, CreditTool } from './types';

const API_BASE =
  (import.meta.env.VITE_API_BASE as string | undefined) ?? '';

function wsUrl(): string {
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  if (API_BASE) {
    const u = new URL(API_BASE);
    const proto2 = u.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${proto2}//${u.host}/api/credit/chat`;
  }
  return `${proto}//${window.location.host}/api/credit/chat`;
}

interface ChatMsg {
  role: 'user' | 'assistant' | 'system';
  text: string;
  /** When true, the bubble is the live-streaming one (last assistant). */
  streaming?: boolean;
}

interface CitationChip {
  uri: string;
  title: string;
  kind: 'web' | 'corpus';
}

interface CodeBlock {
  source: string;
  language: string;
  result?: string;
  outcome?: string;
}

/** Wizard quick-pick presets — each step shows chips so the demo flows fast. */
const PRESETS = {
  monto: [
    { label: '$1.000.000', value: 1_000_000 },
    { label: '$3.000.000', value: 3_000_000 },
    { label: '$5.000.000', value: 5_000_000 },
    { label: '$8.000.000', value: 8_000_000 },
  ],
  proposito: [
    { label: 'Imprevistos', value: 'imprevistos' },
    { label: 'Consolidar deudas', value: 'consolidacion' },
    { label: 'Salud', value: 'salud' },
    { label: 'Educación', value: 'educacion' },
  ],
  plazo: [
    { label: '12 meses', value: 12 },
    { label: '24 meses', value: 24 },
    { label: '36 meses', value: 36 },
    { label: '48 meses', value: 48 },
  ],
} as const;

interface SimState {
  monto: number;
  plazoMeses: number;
  tasaAnual: number;
  seguroMensualPct: number;
  comisionApertura: number;
  bankAnual: number;
}

const DEFAULT_SIM: SimState = {
  monto: 3_000_000,
  plazoMeses: 24,
  tasaAnual: 17.5, // CMR aproximado para crédito universal CCLA
  seguroMensualPct: 0.0007,
  comisionApertura: 0,
  bankAnual: 22, // banco promedio retail
};

export interface CreditSimulatorProps {
  open: boolean;
  onClose: () => void;
  onOpenArchitecture: () => void;
  /** Optional: forward events to the architecture modal. */
  onEvents?: (events: CreditEvent[]) => void;
}

export function CreditSimulator({
  open,
  onClose,
  onOpenArchitecture,
  onEvents,
}: CreditSimulatorProps) {
  const [step, setStep] = useState<0 | 1 | 2 | 3>(0);
  const [monto, setMonto] = useState(DEFAULT_SIM.monto);
  const [proposito, setProposito] = useState<string>('imprevistos');
  const [chat, setChat] = useState<ChatMsg[]>([
    {
      role: 'assistant',
      text:
        '¡Hola! Soy **Andesia Crédito**. Te voy a armar una simulación con la tasa publicada de Caja Los Andes y comparar contra la banca. ¿Cuánto necesitas?',
    },
  ]);
  const [citations, setCitations] = useState<CitationChip[]>([]);
  const [codeBlocks, setCodeBlocks] = useState<CodeBlock[]>([]);
  const [agentBusy, setAgentBusy] = useState(false);
  const [hasResult, setHasResult] = useState(false);
  const [sim, setSim] = useState<SimState>(DEFAULT_SIM);
  const [eventsLog, setEventsLog] = useState<CreditEvent[]>([]);

  const wsRef = useRef<WebSocket | null>(null);
  const sessionIdRef = useRef<string>(`sim-${Date.now()}-${Math.floor(Math.random() * 1e6)}`);
  const codeByCallRef = useRef<Map<string, CodeBlock>>(new Map());

  const pushEvent = useCallback(
    (e: CreditEvent) => {
      setEventsLog((prev) => {
        const next = [...prev, e];
        onEvents?.(next);
        return next;
      });
    },
    [onEvents],
  );

  /* ------------------------------------------------------------------
   * WS lifecycle
   * ------------------------------------------------------------------ */
  useEffect(() => {
    if (!open) return;
    let alive = true;
    const ws = new WebSocket(wsUrl());
    wsRef.current = ws;

    ws.onopen = () => {
      if (!alive) return;
      // Tell backend the session id so it can keep multi-turn state.
      ws.send(JSON.stringify({ type: 'hello', sessionId: sessionIdRef.current }));
    };

    ws.onmessage = (ev) => {
      if (!alive) return;
      let payload: CreditEvent | null = null;
      try {
        payload = JSON.parse(ev.data);
      } catch {
        return;
      }
      if (!payload) return;
      pushEvent(payload);
      switch (payload.type) {
        case 'text_delta':
          setChat((prev) => {
            const next = [...prev];
            const last = next[next.length - 1];
            if (last && last.role === 'assistant' && last.streaming) {
              next[next.length - 1] = {
                ...last,
                text: last.text + payload.text,
              };
            } else {
              next.push({
                role: 'assistant',
                text: payload.text,
                streaming: true,
              });
            }
            return next;
          });
          break;
        case 'turn_complete':
          setChat((prev) =>
            prev.map((m) => (m.streaming ? { ...m, streaming: false } : m)),
          );
          setAgentBusy(false);
          break;
        case 'tool_call_start':
          // Pipeline modal handles the visual; chat shows a tiny "running" hint.
          break;
        case 'tool_call_end':
          break;
        case 'code': {
          const block: CodeBlock = {
            source: payload.source,
            language: payload.language,
            result: codeByCallRef.current.get(payload.callId)?.result,
            outcome: codeByCallRef.current.get(payload.callId)?.outcome,
          };
          codeByCallRef.current.set(payload.callId, block);
          setCodeBlocks(Array.from(codeByCallRef.current.values()));
          break;
        }
        case 'code_result': {
          const prev = codeByCallRef.current.get(payload.callId) ?? {
            source: '',
            language: 'PYTHON',
          };
          const block: CodeBlock = {
            ...prev,
            result: payload.output,
            outcome: payload.outcome,
          };
          codeByCallRef.current.set(payload.callId, block);
          setCodeBlocks(Array.from(codeByCallRef.current.values()));
          break;
        }
        case 'grounding_chunk':
          setCitations((prev) => {
            if (prev.some((c) => c.uri === payload.uri)) return prev;
            return [...prev, { uri: payload.uri, title: payload.title, kind: payload.kind }];
          });
          break;
        case 'chart_data':
          setSim((cur) => ({
            ...cur,
            monto: payload.payload.monto ?? cur.monto,
            plazoMeses: payload.payload.plazoMeses ?? cur.plazoMeses,
            tasaAnual: payload.payload.tasaAnual ?? cur.tasaAnual,
            seguroMensualPct:
              payload.payload.seguroMensualPct ?? cur.seguroMensualPct,
            comisionApertura:
              payload.payload.comisionApertura ?? cur.comisionApertura,
            bankAnual: payload.payload.bankAnual ?? cur.bankAnual,
          }));
          setHasResult(true);
          break;
        case 'error':
          setChat((prev) => [
            ...prev,
            { role: 'system', text: `⚠️ ${payload.message}` },
          ]);
          setAgentBusy(false);
          break;
        case 'agent_phase':
        case 'agent_stamp':
          // Consumed by AgentTrace via the events log; nothing to mutate here.
          break;
      }
    };

    ws.onerror = () => {
      if (!alive) return;
      setChat((prev) => [
        ...prev,
        {
          role: 'system',
          text: '⚠️ No pude conectar al agente. Verifica que el backend esté corriendo.',
        },
      ]);
      setAgentBusy(false);
    };

    ws.onclose = () => {
      // No auto-reconnect — the simulator overlay is short-lived.
    };

    return () => {
      alive = false;
      try {
        ws.onopen = null;
        ws.onmessage = null;
        ws.onerror = null;
        ws.onclose = null;
        ws.close();
      } catch {
        /* ignore */
      }
      wsRef.current = null;
      setChat([
        {
          role: 'assistant',
          text:
            '¡Hola! Soy **Andesia Crédito**. Te voy a armar una simulación con la tasa publicada de Caja Los Andes y comparar contra la banca. ¿Cuánto necesitas?',
        },
      ]);
      setCitations([]);
      setCodeBlocks([]);
      setHasResult(false);
      setStep(0);
      setSim(DEFAULT_SIM);
      setEventsLog([]);
      codeByCallRef.current.clear();
      sessionIdRef.current = `sim-${Date.now()}-${Math.floor(Math.random() * 1e6)}`;
    };
  }, [open, pushEvent]);

  /* ------------------------------------------------------------------
   * Send message helpers
   * ------------------------------------------------------------------ */
  const sendUser = useCallback(
    (text: string, payload?: Record<string, unknown>) => {
      const ws = wsRef.current;
      if (!ws || ws.readyState !== WebSocket.OPEN) return;
      setChat((prev) => [...prev, { role: 'user', text }]);
      setAgentBusy(true);
      ws.send(
        JSON.stringify({
          type: 'user_message',
          text,
          context: payload ?? {},
          sessionId: sessionIdRef.current,
        }),
      );
    },
    [],
  );

  const requestSimulation = useCallback(
    (m: number, p: number, prop: string) => {
      sendUser(
        `Necesito ${formatCLP(m)} para ${prop}, en ${p} cuotas. Calcula la cuota mensual, CAE y compara con la banca.`,
        { monto: m, plazoMeses: p, proposito: prop, simulate: true },
      );
    },
    [sendUser],
  );

  /* ------------------------------------------------------------------
   * Wizard advancement
   * ------------------------------------------------------------------ */
  const advance = useCallback(
    (k: 'monto' | 'proposito' | 'plazo', value: number | string, label: string) => {
      // Append the user's pick to the chat locally — DO NOT send to the agent
      // yet. Otherwise the LLM treats each pick as a full request and fires the
      // simulation before we've collected all three answers (human-in-the-loop
      // gets bypassed).
      setChat((prev) => [...prev, { role: 'user', text: label }]);

      if (k === 'monto') {
        setMonto(value as number);
        setStep(1);
        setTimeout(
          () =>
            setChat((prev) => [
              ...prev,
              {
                role: 'assistant',
                text: `Perfecto — **${label}**. ¿Para qué lo necesitas? Esto me ayuda a recomendarte el producto correcto (Universal, Salud, Consolidación).`,
              },
            ]),
          300,
        );
      } else if (k === 'proposito') {
        setProposito(value as string);
        setStep(2);
        setTimeout(
          () =>
            setChat((prev) => [
              ...prev,
              {
                role: 'assistant',
                text: `Anotado: **${label}**. Última pregunta — ¿en cuántas cuotas te acomoda pagarlo?`,
              },
            ]),
          300,
        );
      } else if (k === 'plazo') {
        const p = value as number;
        setStep(3);
        // Only NOW we actually invoke the agent — with the full context.
        setTimeout(() => requestSimulation(monto, p, proposito), 250);
      }
    },
    [monto, proposito, requestSimulation],
  );

  /* ------------------------------------------------------------------
   * Derived: amortization (live recompute on slider change)
   * ------------------------------------------------------------------ */
  const result: AmortizationResult = useMemo(() => {
    return amortize({
      monto: sim.monto,
      tasaAnual: sim.tasaAnual,
      plazoMeses: sim.plazoMeses,
      seguroMensualPct: sim.seguroMensualPct,
      comisionApertura: sim.comisionApertura,
    });
  }, [sim]);

  const bank = useMemo(
    () => compareBank(sim.monto, sim.plazoMeses, sim.bankAnual),
    [sim.monto, sim.plazoMeses, sim.bankAnual],
  );

  const projection = useMemo(
    () =>
      projectSavings(
        Math.max(0, bank.cuota - result.cuotaMensual),
        10,
        5,
      ),
    [bank.cuota, result.cuotaMensual],
  );

  if (!open) return null;

  return (
    <div className="cs-root" role="dialog" aria-modal="true" aria-label="Simulador de crédito Andesia">
      <div className="cs-backdrop" onClick={onClose} />
      <div className="cs-shell">
        <header className="cs-header">
          <div className="cs-header__brand">
            <span className="cs-header__orb" aria-hidden>
              <svg viewBox="0 0 24 24">
                <path d="M12 2 L13.5 9.2 L20.7 10.5 L13.5 11.8 L12 19 L10.5 11.8 L3.3 10.5 L10.5 9.2 Z" />
              </svg>
            </span>
            <div>
              <h2>Andesia Crédito</h2>
              <p>Agente con búsqueda en tiempo real + cálculo nativo</p>
            </div>
          </div>
          <div className="cs-header__actions">
            <button
              type="button"
              className="cs-arch-btn"
              onClick={onOpenArchitecture}
              title="Ver arquitectura del agente"
            >
              <span className="material-symbols-outlined" aria-hidden>
                schema
              </span>
              Arquitectura del agente
            </button>
            <button type="button" className="cs-close" onClick={onClose} aria-label="Cerrar">
              <span className="material-symbols-outlined" aria-hidden>
                close
              </span>
            </button>
          </div>
        </header>

        <div className="cs-grid">
          {/* === LEFT: Chat wizard ============================================ */}
          <section className="cs-chat">
            <div className="cs-chat__scroll">
              {chat.map((m, i) => (
                <div
                  key={i}
                  className={`cs-msg cs-msg--${m.role}${m.streaming ? ' is-streaming' : ''}`}
                >
                  {m.role === 'assistant' && (
                    <span className="cs-msg__avatar" aria-hidden>
                      <svg viewBox="0 0 24 24">
                        <path d="M12 2 L13.5 9.2 L20.7 10.5 L13.5 11.8 L12 19 L10.5 11.8 L3.3 10.5 L10.5 9.2 Z" />
                      </svg>
                    </span>
                  )}
                  <div className="cs-msg__bubble">{renderMd(m.text)}</div>
                </div>
              ))}
              {agentBusy && (
                <div className="cs-typing">
                  <span /> <span /> <span />
                </div>
              )}
            </div>

            {/* Wizard controls */}
            <div className="cs-wizard">
              {step === 0 && (
                <WizardStep
                  label="Selecciona un monto"
                  presets={PRESETS.monto.map((p) => ({ ...p }))}
                  onPick={(v, l) => advance('monto', v, l)}
                />
              )}
              {step === 1 && (
                <WizardStep
                  label="¿Para qué lo necesitas?"
                  presets={PRESETS.proposito.map((p) => ({ ...p }))}
                  onPick={(v, l) => advance('proposito', v, l)}
                />
              )}
              {step === 2 && (
                <WizardStep
                  label="Plazo en cuotas"
                  presets={PRESETS.plazo.map((p) => ({ ...p }))}
                  onPick={(v, l) => advance('plazo', v, l)}
                />
              )}
              {step === 3 && (
                <div className="cs-wizard__done">
                  <span className="material-symbols-outlined" aria-hidden>
                    check_circle
                  </span>
                  Mueve los sliders del panel para explorar variantes en vivo
                </div>
              )}
            </div>

            {/* Citations + code drawer */}
            {(citations.length > 0 || codeBlocks.length > 0) && (
              <div className="cs-evidence">
                {citations.length > 0 && (
                  <details className="cs-evidence__group" open>
                    <summary>
                      <span className="material-symbols-outlined" aria-hidden>
                        link
                      </span>
                      Fuentes citadas ({citations.length})
                    </summary>
                    <ul>
                      {citations.map((c) => (
                        <li key={c.uri}>
                          <span className={`cs-evidence__kind cs-evidence__kind--${c.kind}`}>
                            {c.kind === 'web' ? 'web' : 'corpus'}
                          </span>
                          <a href={c.uri} target="_blank" rel="noreferrer">
                            {c.title}
                          </a>
                        </li>
                      ))}
                    </ul>
                  </details>
                )}
                {codeBlocks.length > 0 && (
                  <details className="cs-evidence__group">
                    <summary>
                      <span className="material-symbols-outlined" aria-hidden>
                        code
                      </span>
                      Código ejecutado por el agente ({codeBlocks.length})
                    </summary>
                    {codeBlocks.map((b, i) => (
                      <div key={i} className="cs-code">
                        <pre className="cs-code__src">{b.source}</pre>
                        {b.result && (
                          <pre className="cs-code__out">{b.result.slice(0, 800)}</pre>
                        )}
                      </div>
                    ))}
                  </details>
                )}
              </div>
            )}
          </section>

          {/* === RIGHT: Dashboard ============================================ */}
          <section className="cs-dash">
            {!hasResult && !agentBusy && (
              <div className="cs-dash__placeholder">
                <div className="cs-dash__placeholder-orb">
                  <svg viewBox="0 0 64 64" aria-hidden>
                    <circle cx="32" cy="32" r="28" fill="none" stroke="url(#csGrad1)" strokeWidth="2" />
                    <circle cx="32" cy="32" r="18" fill="none" stroke="url(#csGrad1)" strokeWidth="1.5" opacity="0.6" />
                    <defs>
                      <linearGradient id="csGrad1" x1="0" y1="0" x2="64" y2="64">
                        <stop offset="0%" stopColor="#2b6df0" />
                        <stop offset="100%" stopColor="#7c4dff" />
                      </linearGradient>
                    </defs>
                  </svg>
                </div>
                <h3>Tu plan aparecerá aquí</h3>
                <p>
                  Contesta las preguntas del wizard. El agente buscará la tasa
                  vigente en cajalosandes.cl y calculará tu plan en tiempo real.
                </p>
              </div>
            )}

            {!hasResult && agentBusy && (
              <AgentTrace events={eventsLog} busy={agentBusy} />
            )}

            {hasResult && (
              <>
                <Dashboard
                  sim={sim}
                  onSimChange={setSim}
                  result={result}
                  bank={bank}
                  projection={projection}
                />
                <AgentTrace events={eventsLog} busy={agentBusy} />
              </>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}

/* === Wizard step ====================================================== */

function WizardStep({
  label,
  presets,
  onPick,
}: {
  label: string;
  presets: { label: string; value: number | string }[];
  onPick: (value: number | string, label: string) => void;
}) {
  return (
    <div className="cs-wstep">
      <span className="cs-wstep__label">{label}</span>
      <div className="cs-wstep__chips">
        {presets.map((p) => (
          <button
            key={p.label}
            type="button"
            className="cs-chip"
            onClick={() => onPick(p.value, p.label)}
          >
            {p.label}
          </button>
        ))}
      </div>
    </div>
  );
}

/* === Dashboard ======================================================== */

function Dashboard({
  sim,
  onSimChange,
  result,
  bank,
  projection,
}: {
  sim: SimState;
  onSimChange: (s: SimState) => void;
  result: AmortizationResult;
  bank: { cuota: number; totalPagado: number; diff: number };
  projection: { year: number; value: number }[];
}) {
  const ahorroTotal = Math.max(0, bank.totalPagado - result.totalPagado);

  return (
    <div className="cs-dashboard">
      {/* Top KPIs */}
      <div className="cs-kpis">
        <KpiCard
          label="Cuota mensual"
          value={formatCLP(result.cuotaMensual)}
          accent="primary"
          sub={`incluye seguro desgravamen`}
        />
        <KpiCard
          label="CAE estimada"
          value={`${result.cae.toFixed(1)}%`}
          accent="info"
          sub={`tasa anual ${sim.tasaAnual.toFixed(1)}% nominal`}
        />
        <KpiCard
          label="Total a pagar"
          value={formatCLP(result.totalPagado)}
          accent="muted"
          sub={`${sim.plazoMeses} cuotas · interés ${formatCLP(result.totalInteres)}`}
        />
        <KpiCard
          label="Ahorro vs banca"
          value={formatCLP(ahorroTotal)}
          accent="success"
          sub={`banco promedio ${sim.bankAnual}% anual`}
        />
      </div>

      {/* Sliders */}
      <div className="cs-sliders">
        <SliderRow
          label="Monto"
          min={500_000}
          max={15_000_000}
          step={100_000}
          value={sim.monto}
          format={(v) => formatCLP(v)}
          onChange={(v) => onSimChange({ ...sim, monto: v })}
        />
        <SliderRow
          label="Plazo"
          min={6}
          max={60}
          step={1}
          value={sim.plazoMeses}
          format={(v) => `${v} cuotas`}
          onChange={(v) => onSimChange({ ...sim, plazoMeses: v })}
        />
        <SliderRow
          label="Tasa anual CCLA"
          min={6}
          max={28}
          step={0.1}
          value={sim.tasaAnual}
          format={(v) => `${v.toFixed(1)}%`}
          onChange={(v) => onSimChange({ ...sim, tasaAnual: v })}
        />
      </div>

      {/* Charts */}
      <div className="cs-charts">
        <ChartCard title="Cuota: capital vs interés" sub="proyección mes a mes (sistema francés)">
          <AmortizationLineChart
            schedule={result.schedule}
            primaryColor="#2b6df0"
            secondaryColor="#7c4dff"
          />
        </ChartCard>
        <ChartCard title="Composición de tu cuota" sub={`mes 1 de ${sim.plazoMeses}`}>
          <CuotaDonut row={result.schedule[0] ?? null} />
        </ChartCard>
        <ChartCard title="Caja Los Andes vs Banca" sub="costo total del crédito">
          <ComparisonBars
            ccla={result.totalPagado}
            bank={bank.totalPagado}
          />
        </ChartCard>
        <ChartCard title="Si inviertes el ahorro a 10 años" sub="rentabilidad supuesta 5% anual">
          <ProjectionArea data={projection} />
        </ChartCard>
      </div>
    </div>
  );
}

function KpiCard({
  label,
  value,
  sub,
  accent,
}: {
  label: string;
  value: string;
  sub?: string;
  accent: 'primary' | 'info' | 'muted' | 'success';
}) {
  return (
    <div className={`cs-kpi cs-kpi--${accent}`}>
      <span className="cs-kpi__label">{label}</span>
      <span className="cs-kpi__value">{value}</span>
      {sub && <span className="cs-kpi__sub">{sub}</span>}
    </div>
  );
}

function SliderRow({
  label,
  min,
  max,
  step,
  value,
  format,
  onChange,
}: {
  label: string;
  min: number;
  max: number;
  step: number;
  value: number;
  format: (v: number) => string;
  onChange: (v: number) => void;
}) {
  return (
    <label className="cs-slider">
      <div className="cs-slider__row">
        <span className="cs-slider__label">{label}</span>
        <span className="cs-slider__value">{format(value)}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
      />
    </label>
  );
}

function ChartCard({
  title,
  sub,
  children,
}: {
  title: string;
  sub?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="cs-chartcard">
      <div className="cs-chartcard__head">
        <h4>{title}</h4>
        {sub && <span>{sub}</span>}
      </div>
      <div className="cs-chartcard__body">{children}</div>
    </div>
  );
}

/* === Custom SVG charts ===============================================
 * Pure SVG so we get full control over animated entrances + glow filters
 * without pulling in a chart library. Every chart re-renders on slider
 * change at native frame rate. */

function AmortizationLineChart({
  schedule,
  primaryColor,
  secondaryColor,
}: {
  schedule: { mes: number; capital: number; interes: number }[];
  primaryColor: string;
  secondaryColor: string;
}) {
  if (schedule.length === 0) return null;
  const w = 480;
  const h = 200;
  const padX = 32;
  const padY = 18;
  const innerW = w - padX * 2;
  const innerH = h - padY * 2;
  const max = Math.max(...schedule.map((r) => Math.max(r.capital, r.interes)));
  const sx = (i: number) => padX + (i / (schedule.length - 1)) * innerW;
  const sy = (v: number) => padY + innerH - (v / max) * innerH;
  const linePath = (key: 'capital' | 'interes') =>
    schedule.map((r, i) => `${i === 0 ? 'M' : 'L'} ${sx(i)} ${sy(r[key])}`).join(' ');
  const areaPath = (key: 'capital' | 'interes') =>
    `${linePath(key)} L ${sx(schedule.length - 1)} ${padY + innerH} L ${sx(0)} ${padY + innerH} Z`;

  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="cs-svg cs-svg--line" preserveAspectRatio="none">
      <defs>
        <linearGradient id="amCap" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={primaryColor} stopOpacity="0.45" />
          <stop offset="100%" stopColor={primaryColor} stopOpacity="0" />
        </linearGradient>
        <linearGradient id="amInt" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={secondaryColor} stopOpacity="0.35" />
          <stop offset="100%" stopColor={secondaryColor} stopOpacity="0" />
        </linearGradient>
        <filter id="amGlow" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="2" />
        </filter>
      </defs>
      {/* Grid */}
      {[0.25, 0.5, 0.75].map((g) => (
        <line
          key={g}
          x1={padX}
          x2={w - padX}
          y1={padY + innerH * g}
          y2={padY + innerH * g}
          stroke="rgba(255,255,255,0.06)"
          strokeDasharray="2 4"
        />
      ))}
      {/* Areas */}
      <path d={areaPath('capital')} fill="url(#amCap)" />
      <path d={areaPath('interes')} fill="url(#amInt)" />
      {/* Lines */}
      <path
        d={linePath('interes')}
        fill="none"
        stroke={secondaryColor}
        strokeWidth="2"
        filter="url(#amGlow)"
      />
      <path
        d={linePath('capital')}
        fill="none"
        stroke={primaryColor}
        strokeWidth="2.4"
        filter="url(#amGlow)"
      />
      {/* Legend */}
      <g transform={`translate(${padX} ${h - 6})`} className="cs-svg__legend">
        <circle cx="0" cy="-4" r="4" fill={primaryColor} />
        <text x="9" y="0">capital</text>
        <circle cx="80" cy="-4" r="4" fill={secondaryColor} />
        <text x="89" y="0">interés</text>
      </g>
    </svg>
  );
}

function CuotaDonut({
  row,
}: {
  row: { capital: number; interes: number; seguro: number } | null;
}) {
  if (!row) return null;
  const total = row.capital + row.interes + row.seguro;
  if (total <= 0) return null;
  const pct = (v: number) => v / total;
  const segs = [
    { v: pct(row.capital), color: '#2b6df0', label: 'capital' },
    { v: pct(row.interes), color: '#7c4dff', label: 'interés' },
    { v: pct(row.seguro), color: '#1ec8d6', label: 'seguro' },
  ];
  const r = 60;
  const cx = 90;
  const cy = 90;
  const c = 2 * Math.PI * r;
  let offset = 0;
  return (
    <svg viewBox="0 0 320 180" className="cs-svg cs-svg--donut">
      <g transform={`translate(0 0)`}>
        <circle cx={cx} cy={cy} r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="22" />
        {segs.map((s, i) => {
          const len = s.v * c;
          const dash = `${len} ${c - len}`;
          const dashOffset = -offset;
          offset += len;
          return (
            <circle
              key={i}
              cx={cx}
              cy={cy}
              r={r}
              fill="none"
              stroke={s.color}
              strokeWidth="22"
              strokeDasharray={dash}
              strokeDashoffset={dashOffset}
              transform={`rotate(-90 ${cx} ${cy})`}
              style={{ transition: 'stroke-dasharray 0.4s ease' }}
            />
          );
        })}
        <text x={cx} y={cy - 4} textAnchor="middle" className="cs-svg__donut-num">
          {formatCLP(row.capital + row.interes + row.seguro)}
        </text>
        <text x={cx} y={cy + 14} textAnchor="middle" className="cs-svg__donut-sub">
          cuota mes 1
        </text>
      </g>
      <g transform="translate(190 40)" className="cs-svg__legend">
        {segs.map((s, i) => (
          <g key={s.label} transform={`translate(0 ${i * 22})`}>
            <rect width="10" height="10" fill={s.color} rx="2" />
            <text x="16" y="9">
              {s.label} · {(s.v * 100).toFixed(1)}%
            </text>
          </g>
        ))}
      </g>
    </svg>
  );
}

function ComparisonBars({ ccla, bank }: { ccla: number; bank: number }) {
  const max = Math.max(ccla, bank, 1);
  const w = 480;
  const h = 180;
  const barH = 38;
  const gap = 30;
  const cclaW = (ccla / max) * (w - 140);
  const bankW = (bank / max) * (w - 140);
  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="cs-svg">
      <defs>
        <linearGradient id="cmpCCLA" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#1ec8d6" />
          <stop offset="100%" stopColor="#2b6df0" />
        </linearGradient>
        <linearGradient id="cmpBank" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#3a4254" />
          <stop offset="100%" stopColor="#5a6378" />
        </linearGradient>
      </defs>
      <text x="0" y="22" className="cs-svg__bar-label">Caja Los Andes</text>
      <rect x="120" y="6" width={cclaW} height={barH} rx="6" fill="url(#cmpCCLA)" style={{ transition: 'width 0.4s ease' }} />
      <text x={120 + cclaW + 8} y="30" className="cs-svg__bar-val">{formatCLP(ccla)}</text>

      <text x="0" y={22 + barH + gap} className="cs-svg__bar-label">Banca promedio</text>
      <rect
        x="120"
        y={6 + barH + gap}
        width={bankW}
        height={barH}
        rx="6"
        fill="url(#cmpBank)"
        style={{ transition: 'width 0.4s ease' }}
      />
      <text x={120 + bankW + 8} y={30 + barH + gap} className="cs-svg__bar-val">{formatCLP(bank)}</text>
    </svg>
  );
}

function ProjectionArea({ data }: { data: { year: number; value: number }[] }) {
  if (data.length === 0) return null;
  const w = 480;
  const h = 180;
  const padX = 28;
  const padY = 14;
  const innerW = w - padX * 2;
  const innerH = h - padY * 2;
  const max = Math.max(...data.map((d) => d.value), 1);
  const sx = (i: number) => padX + (i / (data.length - 1)) * innerW;
  const sy = (v: number) => padY + innerH - (v / max) * innerH;
  const linePath = data.map((d, i) => `${i === 0 ? 'M' : 'L'} ${sx(i)} ${sy(d.value)}`).join(' ');
  const areaPath = `${linePath} L ${sx(data.length - 1)} ${padY + innerH} L ${sx(0)} ${padY + innerH} Z`;
  const last = data[data.length - 1];
  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="cs-svg">
      <defs>
        <linearGradient id="prjArea" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#1ec8d6" stopOpacity="0.55" />
          <stop offset="100%" stopColor="#1ec8d6" stopOpacity="0" />
        </linearGradient>
      </defs>
      <path d={areaPath} fill="url(#prjArea)" />
      <path d={linePath} fill="none" stroke="#1ec8d6" strokeWidth="2.4" />
      {data.map((d, i) =>
        i % 2 === 0 ? (
          <text key={i} x={sx(i)} y={h - 2} textAnchor="middle" className="cs-svg__axis">
            año {d.year}
          </text>
        ) : null,
      )}
      <text x={sx(data.length - 1)} y={sy(last.value) - 8} textAnchor="end" className="cs-svg__bar-val">
        {formatCLP(last.value)}
      </text>
    </svg>
  );
}

/* === Tiny markdown renderer (bold + line breaks) ====================== */
function renderMd(text: string): React.ReactNode {
  const parts: React.ReactNode[] = [];
  const lines = text.split('\n');
  lines.forEach((line, li) => {
    const segs = line.split(/(\*\*[^*]+\*\*)/g);
    segs.forEach((s, si) => {
      if (s.startsWith('**') && s.endsWith('**')) {
        parts.push(<strong key={`${li}-${si}`}>{s.slice(2, -2)}</strong>);
      } else {
        parts.push(<span key={`${li}-${si}`}>{s}</span>);
      }
    });
    if (li < lines.length - 1) parts.push(<br key={`br-${li}`} />);
  });
  return <>{parts}</>;
}

// silence unused-warning for CreditTool re-export type alignment
export type { CreditTool };
