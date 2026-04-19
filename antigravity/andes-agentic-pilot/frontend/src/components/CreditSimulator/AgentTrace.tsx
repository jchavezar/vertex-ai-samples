/* AgentTrace — "entrañas" del agente Andesia Crédito en vivo.
 *
 * Layered view that turns every WebSocket event into something visible:
 *   1. Phase ribbon: 4 pills (Discovery → Reasoning → Compute → Synthesize)
 *      with elapsed-ms badges that count up while active and freeze when done.
 *   2. Live KPI strip: TTFT, total elapsed, code runs, sources cited.
 *   3. Token waterfall: micro horizontal timeline showing when each phase
 *      started and how long it took (real backend timestamps, no fakery).
 *   4. Trace stream: chronological list of agent_stamp events, color-coded
 *      by kind (search · rate · ttft · code · grounding · turn). Each row
 *      shows phase chip, Δms from the previous event, and the label.
 *   5. Source cards: corpus & web chunks, deduped, with hover snippet preview.
 *   6. Code blocks: every executable_code from the model rendered with
 *      syntax-aware monospaced styling + outcome badge.
 *
 * Data source: the CreditEvent[] array already aggregated by CreditSimulator.
 * This component is purely derived — no WS handling, no state of its own
 * beyond a "now" tick that drives the active-phase counter. */
import { useEffect, useMemo, useState } from 'react';
import './AgentTrace.css';
import type { AgentPhase, CreditEvent } from './types';

interface Props {
  events: CreditEvent[];
  /** When true, the agent is mid-turn; counter ticks. */
  busy: boolean;
}

const PHASE_DEFS: { id: AgentPhase; label: string; icon: string; hint: string }[] = [
  { id: 'discovery', label: 'Discovery', icon: 'travel_explore', hint: 'Vertex AI Search · CCLA corpus' },
  { id: 'reasoning', label: 'Reasoning', icon: 'psychology', hint: 'Gemini 3 decide qué hacer' },
  { id: 'compute',   label: 'Compute',   icon: 'function',     hint: 'Sandbox Python (BuiltInCodeExecutor)' },
  { id: 'synthesize',label: 'Synthesize',icon: 'auto_awesome', hint: 'Stream del texto final + chart' },
];

const KIND_STYLE: Record<string, { color: string; icon: string }> = {
  search_start:    { color: '#1ec8d6', icon: 'travel_explore' },
  search_end:      { color: '#1ec8d6', icon: 'check_circle' },
  rate_extracted:  { color: '#34a853', icon: 'percent' },
  rate_referencial:{ color: '#f5a524', icon: 'help' },
  model_call:      { color: '#7c4dff', icon: 'psychology' },
  stream_open:     { color: '#7c4dff', icon: 'bolt' },
  ttft:            { color: '#ff7ab6', icon: 'arrow_forward' },
  code_emit:       { color: '#b14dff', icon: 'code' },
  code_result:     { color: '#b14dff', icon: 'play_arrow' },
  grounding:       { color: '#5a9eff', icon: 'link' },
  turn_end:        { color: '#34a853', icon: 'flag' },
  log:             { color: '#7888a8', icon: 'subject' },
};

function fmtMs(ms: number): string {
  if (ms < 1000) return `${Math.round(ms)} ms`;
  return `${(ms / 1000).toFixed(2)} s`;
}

export function AgentTrace({ events, busy }: Props) {
  /* Tick every 100ms while busy so the active-phase counter feels alive. */
  const [now, setNow] = useState(Date.now());
  useEffect(() => {
    if (!busy) return;
    const i = setInterval(() => setNow(Date.now()), 100);
    return () => clearInterval(i);
  }, [busy]);

  const trace = useMemo(() => deriveTrace(events, busy, now), [events, busy, now]);

  return (
    <div className="at-root">
      <PhaseRibbon trace={trace} />
      <KPIStrip trace={trace} />
      <Waterfall trace={trace} />
      <Stream events={events} />
      <Sources trace={trace} />
      <CodeBlocks trace={trace} />
    </div>
  );
}

/* ---------------------------------------------------------------------------
 * Trace derivation
 * --------------------------------------------------------------------------- */

interface PhaseSpan {
  id: AgentPhase;
  startMs: number;
  endMs: number | null; // null = still active
  events: number;
}

interface SourceChip {
  kind: 'web' | 'corpus';
  uri: string;
  title: string;
  snippet?: string;
}

interface CodeChip {
  callId: string;
  source: string;
  language: string;
  result?: string;
  outcome?: string;
}

interface DerivedTrace {
  phases: PhaseSpan[];
  activePhase: AgentPhase | null;
  totalMs: number;
  ttftMs: number | null;
  totalAtMs: number; // last seen tMs (for total even after stream end)
  toolCalls: { tool: string; callId: string }[];
  codeRuns: number;
  sources: SourceChip[];
  codes: CodeChip[];
  startWallMs: number; // wallclock when first event arrived (for live counter)
}

function deriveTrace(events: CreditEvent[], busy: boolean, now: number): DerivedTrace {
  const phases: PhaseSpan[] = [];
  let totalAtMs = 0;
  let ttftMs: number | null = null;
  const toolCalls: { tool: string; callId: string }[] = [];
  const sourcesMap = new Map<string, SourceChip>();
  const codesMap = new Map<string, CodeChip>();
  let startWallMs = 0;

  for (const e of events) {
    if (e.type === 'agent_phase') {
      // Close the previous open phase
      const open = phases[phases.length - 1];
      if (open && open.endMs === null) open.endMs = e.tMs;
      phases.push({ id: e.phase, startMs: e.tMs, endMs: null, events: 0 });
      totalAtMs = Math.max(totalAtMs, e.tMs);
      if (!startWallMs) startWallMs = now;
    } else if (e.type === 'agent_stamp') {
      const open = phases[phases.length - 1];
      if (open) open.events += 1;
      totalAtMs = Math.max(totalAtMs, e.tMs);
      if (e.kind === 'ttft' && ttftMs === null) ttftMs = e.tMs;
      if (e.kind === 'turn_end' && open) open.endMs = e.tMs;
    } else if (e.type === 'tool_call_start') {
      toolCalls.push({ tool: e.tool, callId: e.callId });
    } else if (e.type === 'grounding_chunk') {
      if (!sourcesMap.has(e.uri)) {
        sourcesMap.set(e.uri, {
          kind: e.kind,
          uri: e.uri,
          title: e.title,
          snippet: e.snippet,
        });
      }
    } else if (e.type === 'code') {
      const cur = codesMap.get(e.callId);
      codesMap.set(e.callId, {
        callId: e.callId,
        source: e.source,
        language: e.language,
        result: cur?.result,
        outcome: cur?.outcome,
      });
    } else if (e.type === 'code_result') {
      const cur = codesMap.get(e.callId) ?? {
        callId: e.callId, source: '', language: 'PYTHON',
      };
      codesMap.set(e.callId, { ...cur, result: e.output, outcome: e.outcome });
    } else if (e.type === 'turn_complete') {
      const open = phases[phases.length - 1];
      if (open && open.endMs === null) open.endMs = totalAtMs;
    }
  }

  // Active phase = last phase still open
  let activePhase: AgentPhase | null = null;
  const lastOpen = phases[phases.length - 1];
  if (lastOpen && lastOpen.endMs === null && busy) activePhase = lastOpen.id;

  // Live total — for the active phase, extrapolate using wallclock
  let totalMs = totalAtMs;
  if (activePhase && startWallMs) {
    const wallElapsed = now - startWallMs;
    totalMs = Math.max(totalMs, wallElapsed);
  }

  return {
    phases,
    activePhase,
    totalMs,
    ttftMs,
    totalAtMs,
    toolCalls,
    codeRuns: codesMap.size,
    sources: Array.from(sourcesMap.values()),
    codes: Array.from(codesMap.values()),
    startWallMs,
  };
}

/* ---------------------------------------------------------------------------
 * Phase ribbon (top)
 * --------------------------------------------------------------------------- */

function PhaseRibbon({ trace }: { trace: DerivedTrace }) {
  const phaseEnd: Record<AgentPhase, number | null> = {
    discovery: null, reasoning: null, compute: null, synthesize: null,
  };
  const phaseStart: Record<AgentPhase, number | null> = {
    discovery: null, reasoning: null, compute: null, synthesize: null,
  };
  for (const p of trace.phases) {
    if (phaseStart[p.id] === null) phaseStart[p.id] = p.startMs;
    phaseEnd[p.id] = p.endMs ?? trace.totalMs;
  }

  return (
    <div className="at-ribbon" role="list">
      {PHASE_DEFS.map((def, i) => {
        const start = phaseStart[def.id];
        const end = phaseEnd[def.id];
        const seen = start !== null;
        const active = trace.activePhase === def.id;
        const dur = seen && end !== null ? end - (start ?? 0) : null;
        return (
          <div
            key={def.id}
            role="listitem"
            className={`at-phase${active ? ' is-active' : ''}${seen && !active ? ' is-done' : ''}`}
          >
            <div className="at-phase__icon">
              <span className="material-symbols-outlined" aria-hidden>{def.icon}</span>
            </div>
            <div className="at-phase__body">
              <strong>{def.label}</strong>
              <small>{def.hint}</small>
            </div>
            <div className="at-phase__meta">
              {dur !== null
                ? <span className="at-phase__dur">{fmtMs(dur)}</span>
                : active
                  ? <span className="at-phase__live">en curso</span>
                  : <span className="at-phase__pending">—</span>}
            </div>
            {i < PHASE_DEFS.length - 1 && <span className="at-phase__arrow">›</span>}
          </div>
        );
      })}
    </div>
  );
}

/* ---------------------------------------------------------------------------
 * KPI strip
 * --------------------------------------------------------------------------- */

function KPIStrip({ trace }: { trace: DerivedTrace }) {
  const items: { label: string; value: string; accent: string; icon: string }[] = [
    {
      label: 'Tiempo total',
      value: trace.totalMs > 0 ? fmtMs(trace.totalMs) : '—',
      accent: 'cyan', icon: 'timer',
    },
    {
      label: 'TTFT (primer token)',
      value: trace.ttftMs !== null ? fmtMs(trace.ttftMs) : '—',
      accent: 'pink', icon: 'flash_on',
    },
    {
      label: 'Ejecuciones de código',
      value: String(trace.codeRuns),
      accent: 'purple', icon: 'function',
    },
    {
      label: 'Fuentes citadas',
      value: String(trace.sources.length),
      accent: 'blue', icon: 'link',
    },
  ];
  return (
    <div className="at-kpis">
      {items.map((k) => (
        <div key={k.label} className={`at-kpi at-kpi--${k.accent}`}>
          <span className="material-symbols-outlined" aria-hidden>{k.icon}</span>
          <div>
            <strong>{k.value}</strong>
            <small>{k.label}</small>
          </div>
        </div>
      ))}
    </div>
  );
}

/* ---------------------------------------------------------------------------
 * Waterfall — one bar per phase, x-axis = elapsed ms
 * --------------------------------------------------------------------------- */

function Waterfall({ trace }: { trace: DerivedTrace }) {
  if (trace.phases.length === 0) {
    return (
      <div className="at-wf">
        <div className="at-wf__title">
          <span className="material-symbols-outlined" aria-hidden>view_timeline</span>
          Línea de tiempo
        </div>
        <div className="at-wf__empty">El waterfall aparece cuando el agente arranca.</div>
      </div>
    );
  }
  const total = Math.max(trace.totalMs, 1);
  return (
    <div className="at-wf">
      <div className="at-wf__title">
        <span className="material-symbols-outlined" aria-hidden>view_timeline</span>
        Línea de tiempo · cada barra = duración real reportada por el backend
      </div>
      <div className="at-wf__grid">
        {trace.phases.map((p, i) => {
          const end = p.endMs ?? trace.totalMs;
          const left = (p.startMs / total) * 100;
          const width = Math.max(0.5, ((end - p.startMs) / total) * 100);
          const dur = end - p.startMs;
          return (
            <div key={i} className="at-wf__row" aria-label={`${p.id}: ${dur.toFixed(0)} ms`}>
              <span className={`at-wf__chip at-wf__chip--${p.id}`}>{p.id}</span>
              <div className="at-wf__track">
                <div
                  className={`at-wf__bar at-wf__bar--${p.id}${p.endMs === null ? ' is-live' : ''}`}
                  style={{ left: `${left}%`, width: `${width}%` }}
                >
                  <span className="at-wf__dur">{fmtMs(dur)}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
      <div className="at-wf__axis">
        <span>0</span>
        <span>{fmtMs(total / 4)}</span>
        <span>{fmtMs(total / 2)}</span>
        <span>{fmtMs((total / 4) * 3)}</span>
        <span>{fmtMs(total)}</span>
      </div>
    </div>
  );
}

/* ---------------------------------------------------------------------------
 * Stream — chronological agent_stamp list
 * --------------------------------------------------------------------------- */

function Stream({ events }: { events: CreditEvent[] }) {
  const stamps = events.filter((e): e is Extract<CreditEvent, { type: 'agent_stamp' }> =>
    e.type === 'agent_stamp',
  );
  return (
    <div className="at-stream">
      <div className="at-stream__title">
        <span className="material-symbols-outlined" aria-hidden>terminal</span>
        Trazas del agente · live <span className="at-stream__count">{stamps.length}</span>
      </div>
      <div className="at-stream__scroll">
        {stamps.length === 0 && (
          <div className="at-stream__empty">Sin trazas aún. Lanza una simulación.</div>
        )}
        {stamps.map((s, i) => {
          const style = KIND_STYLE[s.kind] ?? KIND_STYLE.log;
          return (
            <div key={i} className="at-row" style={{ borderLeftColor: style.color }}>
              <span className={`at-row__phase at-row__phase--${s.phase}`}>{s.phase}</span>
              <span className="at-row__icon" aria-hidden>
                <span className="material-symbols-outlined" style={{ color: style.color }}>
                  {style.icon}
                </span>
              </span>
              <span className="at-row__label">{s.label}</span>
              <span className="at-row__dt">+{Math.round(s.dtMs)} ms</span>
              <span className="at-row__t">{fmtMs(s.tMs)}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ---------------------------------------------------------------------------
 * Sources & code blocks (compact cards)
 * --------------------------------------------------------------------------- */

function Sources({ trace }: { trace: DerivedTrace }) {
  if (trace.sources.length === 0) return null;
  return (
    <div className="at-sources">
      <div className="at-sources__title">
        <span className="material-symbols-outlined" aria-hidden>menu_book</span>
        Evidencia · {trace.sources.length} fuente{trace.sources.length === 1 ? '' : 's'}
      </div>
      <div className="at-sources__grid">
        {trace.sources.map((s) => (
          <a
            key={s.uri}
            href={s.uri}
            target="_blank"
            rel="noreferrer"
            className={`at-source at-source--${s.kind}`}
            title={s.snippet || s.title}
          >
            <span className="at-source__kind">{s.kind === 'web' ? 'web' : 'corpus'}</span>
            <strong>{s.title || s.uri}</strong>
            <small>{tryHost(s.uri)}</small>
            {s.snippet && <p>{s.snippet.slice(0, 140)}…</p>}
          </a>
        ))}
      </div>
    </div>
  );
}

function tryHost(uri: string): string {
  try { return new URL(uri).host; } catch { return uri.slice(0, 40); }
}

function CodeBlocks({ trace }: { trace: DerivedTrace }) {
  if (trace.codes.length === 0) return null;
  return (
    <div className="at-codes">
      <div className="at-codes__title">
        <span className="material-symbols-outlined" aria-hidden>terminal</span>
        Código que ejecutó el agente · {trace.codes.length}
      </div>
      <div className="at-codes__list">
        {trace.codes.map((c, i) => (
          <details key={c.callId} className="at-code" open={i === trace.codes.length - 1}>
            <summary>
              <span className="at-code__lang">{c.language}</span>
              <span className="at-code__id">{c.callId}</span>
              {c.outcome && (
                <span className={`at-code__outcome at-code__outcome--${(c.outcome || '').toLowerCase().includes('ok') ? 'ok' : 'err'}`}>
                  {c.outcome}
                </span>
              )}
            </summary>
            <pre className="at-code__src">{c.source}</pre>
            {c.result && <pre className="at-code__out">{c.result.slice(0, 1200)}</pre>}
          </details>
        ))}
      </div>
    </div>
  );
}
