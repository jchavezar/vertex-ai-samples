/* Architecture topology — DAG of the Andesia Crédito agent.
 *
 * Layout (horizontal, left → right):
 *
 *   USUARIO ─┐                                                ┌─► RESPUESTA
 *            │                                                │
 *            ▼                                                │
 *         WIZARD ──► LlmAgent (Gemini 3 Flash)                │
 *                       │  │  │  │                            │
 *           Discovery ──┘  │  │  └─► Synthesize ──► CHART ────┘
 *           ┌──────────────┘  │
 *           │   Reasoning ────┤
 *           │                 │
 *  Discovery Engine (CCLA)    Compute  ──► Sandbox Python
 *           │                 │              │
 *           │                 │              └─► amortization
 *           ▼                 ▼
 *      45 docs            __CHART__{...}
 *
 * Each node sits in a phase column; edges are coloured by the phase they
 * belong to and pulse when that phase is currently active. Idle state still
 * shows ambient particle flow so the diagram never looks dead. */
import { useEffect, useMemo, useRef, useState } from 'react';
import './CreditAgentArchitecture.css';
import type { AgentPhase, CreditEvent, CreditTool } from './types';

/* Map agent_stamp.kind → which edge the packet should traverse.
 * This is what turns abstract events into a physical signal flow. */
const KIND_EDGE: Record<string, string> = {
  search_start:    'agent→discovery',
  search_end:      'discovery→agent',
  rate_extracted:  'discovery→agent',
  rate_referencial:'discovery→agent',
  grounding:       'corpus→discovery',
  model_call:      'agent→reasoning',
  stream_open:     'agent→reasoning',
  ttft:            'reasoning→agent',
  code_emit:       'agent→compute',
  code_result:     'compute→agent',
  turn_end:        'synth→response',
};
/* Phase boundary → broadcast a heavier wave on the agent→<phaseTool> edge. */
const PHASE_EDGE: Record<AgentPhase, string> = {
  discovery:  'agent→discovery',
  reasoning:  'agent→reasoning',
  compute:    'agent→compute',
  synthesize: 'agent→synth',
};
const PACKET_TTL_MS = 1700;

interface ArchProps {
  open: boolean;
  onClose: () => void;
  events?: CreditEvent[];
}

/* ── Geometry ───────────────────────────────────────────────────────────── */
const VB = { w: 1200, h: 640 };

interface NodeDef {
  id: string;
  x: number; y: number; w: number; h: number;
  kind: 'input' | 'agent' | 'tool' | 'corpus' | 'sink';
  phase?: AgentPhase;
  title: string;
  subtitle?: string;
  icon: string;
  hint?: string;
}

const NODES: NodeDef[] = [
  // Column 1 — Input
  { id: 'user',     x:  90, y: 220, w: 160, h: 78, kind: 'input', title: 'Usuario',          subtitle: 'wizard 3 pasos',   icon: 'person' },

  // Column 2 — Agent core
  { id: 'agent',    x: 410, y: 280, w: 220, h: 120, kind: 'agent', title: 'LlmAgent · ADK',  subtitle: 'andesia_credito · Gemini 3 Flash', icon: 'hub', hint: 'Orquestador único — decide qué tool llamar y cuándo' },

  // Column 3 — Tools (one per phase)
  { id: 'discovery',x: 760, y: 110, w: 230, h: 88, kind: 'tool', phase: 'discovery',  title: 'Discovery Engine', subtitle: 'caja-los-andes_1776511935295 · 45 docs', icon: 'travel_explore' },
  { id: 'reasoning',x: 760, y: 240, w: 230, h: 88, kind: 'tool', phase: 'reasoning',  title: 'Reasoning · model', subtitle: 'thinking_budget=0 · TTFT mín.',           icon: 'psychology' },
  { id: 'compute',  x: 760, y: 370, w: 230, h: 88, kind: 'tool', phase: 'compute',    title: 'Code Sandbox',     subtitle: 'BuiltInCodeExecutor · Python',           icon: 'function' },
  { id: 'synth',    x: 760, y: 500, w: 230, h: 88, kind: 'tool', phase: 'synthesize', title: 'Synthesize',       subtitle: 'stream SSE · markdown + __CHART__',      icon: 'auto_awesome' },

  // Column 4 — Corpus + sink
  { id: 'corpus',   x:1070, y: 110, w: 110, h: 88, kind: 'corpus', title: 'cajalosandes.cl', subtitle: '6 sub-sitios indexados', icon: 'language' },
  { id: 'response', x:1070, y: 500, w: 110, h: 88, kind: 'sink', title: 'Respuesta',       subtitle: 'chat + dashboard',       icon: 'chat_bubble' },
];

interface EdgeDef {
  id: string;
  from: string;
  to: string;
  /** Where on the source node the edge exits: e.g. 'right', 'top-right', 'bottom-right'. */
  fromAnchor?: string;
  toAnchor?: string;
  phase?: AgentPhase;
  label?: string;
  /** Curve bend: 0 = straight, +/- shifts the control point. */
  bend?: number;
  /** Direction the edge "points" — affects label placement. */
  reverse?: boolean;
}

const EDGES: EdgeDef[] = [
  { id: 'user→agent',       from: 'user',     to: 'agent',     fromAnchor: 'right',         toAnchor: 'left',           label: 'pregunta + ctx' },
  { id: 'agent→discovery',  from: 'agent',    to: 'discovery', fromAnchor: 'top-right',     toAnchor: 'left', phase: 'discovery',  label: 'tasa anual' },
  { id: 'discovery→corpus', from: 'discovery',to: 'corpus',    fromAnchor: 'right',         toAnchor: 'left', phase: 'discovery',  label: 'REST' },
  { id: 'corpus→discovery', from: 'corpus',   to: 'discovery', fromAnchor: 'bottom-left',   toAnchor: 'top-right', phase: 'discovery', label: 'snippets', bend: -30 },
  { id: 'discovery→agent',  from: 'discovery',to: 'agent',     fromAnchor: 'bottom-left',   toAnchor: 'top-right', phase: 'reasoning', label: 'corpus_block', bend: 30 },
  { id: 'agent→reasoning',  from: 'agent',    to: 'reasoning', fromAnchor: 'right-mid-up',  toAnchor: 'left', phase: 'reasoning', label: 'plan' },
  { id: 'reasoning→agent',  from: 'reasoning',to: 'agent',     fromAnchor: 'left',          toAnchor: 'right-mid-up',   phase: 'reasoning', label: 'rate', bend: 25, reverse: true },
  { id: 'agent→compute',    from: 'agent',    to: 'compute',   fromAnchor: 'right-mid-down',toAnchor: 'left', phase: 'compute',  label: 'exec(python)' },
  { id: 'compute→agent',    from: 'compute',  to: 'agent',     fromAnchor: 'left',          toAnchor: 'right-mid-down', phase: 'compute',  label: 'cuota+CAE', bend: 25, reverse: true },
  { id: 'agent→synth',      from: 'agent',    to: 'synth',     fromAnchor: 'bottom-right',  toAnchor: 'left', phase: 'synthesize', label: 'tokens' },
  { id: 'synth→response',   from: 'synth',    to: 'response',  fromAnchor: 'right',         toAnchor: 'left', phase: 'synthesize', label: 'stream' },
];

const PHASE_COLOR: Record<AgentPhase, { from: string; to: string }> = {
  discovery:  { from: '#1ec8d6', to: '#2b6df0' },
  reasoning:  { from: '#2b6df0', to: '#7c4dff' },
  compute:    { from: '#7c4dff', to: '#b14dff' },
  synthesize: { from: '#b14dff', to: '#ff7ab6' },
};

/* ── Anchor math ────────────────────────────────────────────────────────── */
function anchorXY(n: NodeDef, side?: string): { x: number; y: number } {
  const left = n.x;
  const right = n.x + n.w;
  const top = n.y;
  const bottom = n.y + n.h;
  const cx = n.x + n.w / 2;
  const cy = n.y + n.h / 2;
  switch (side) {
    case 'left':            return { x: left, y: cy };
    case 'right':           return { x: right, y: cy };
    case 'top':             return { x: cx, y: top };
    case 'bottom':          return { x: cx, y: bottom };
    case 'top-left':        return { x: left + n.w * 0.2, y: top };
    case 'top-right':       return { x: left + n.w * 0.8, y: top };
    case 'bottom-left':     return { x: left + n.w * 0.2, y: bottom };
    case 'bottom-right':    return { x: left + n.w * 0.8, y: bottom };
    case 'right-mid-up':    return { x: right, y: top + n.h * 0.33 };
    case 'right-mid-down':  return { x: right, y: top + n.h * 0.67 };
    case 'left-mid-up':     return { x: left, y: top + n.h * 0.33 };
    case 'left-mid-down':   return { x: left, y: top + n.h * 0.67 };
    default:                return { x: cx, y: cy };
  }
}

function edgePath(e: EdgeDef, nodes: Record<string, NodeDef>): string {
  const a = anchorXY(nodes[e.from], e.fromAnchor);
  const b = anchorXY(nodes[e.to],   e.toAnchor);
  const bend = e.bend ?? 0;
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  // Smooth cubic bezier with control points along the dominant axis
  const horizontal = Math.abs(dx) >= Math.abs(dy);
  let c1x: number, c1y: number, c2x: number, c2y: number;
  if (horizontal) {
    c1x = a.x + dx * 0.45;
    c1y = a.y + bend;
    c2x = a.x + dx * 0.55;
    c2y = b.y - bend;
  } else {
    c1x = a.x + bend;
    c1y = a.y + dy * 0.45;
    c2x = b.x - bend;
    c2y = a.y + dy * 0.55;
  }
  return `M ${a.x} ${a.y} C ${c1x} ${c1y}, ${c2x} ${c2y}, ${b.x} ${b.y}`;
}

function midpoint(e: EdgeDef, nodes: Record<string, NodeDef>): { x: number; y: number } {
  const a = anchorXY(nodes[e.from], e.fromAnchor);
  const b = anchorXY(nodes[e.to],   e.toAnchor);
  return { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 + (e.bend ?? 0) * 0.4 };
}

/* ── Component ──────────────────────────────────────────────────────────── */
export function CreditAgentArchitecture({ open, onClose, events = [] }: ArchProps) {
  const [activePhase, setActivePhase] = useState<AgentPhase | null>(null);
  const [counts, setCounts] = useState<Record<AgentPhase, number>>({
    discovery: 0, reasoning: 0, compute: 0, synthesize: 0,
  });
  const [toolCounts, setToolCounts] = useState<Record<CreditTool, number>>({
    vertex_search: 0, code_execution: 0, google_search: 0,
  });
  const [pulseId, setPulseId] = useState<number>(0);
  /* Packets in flight on the topology — every agent_stamp emits one. */
  interface Packet {
    id: string;
    edgeId: string;
    color: string;
    targetNodeId: string;
    bornAt: number;
  }
  const [packets, setPackets] = useState<Packet[]>([]);
  /* Per-node arrival pulses — nodeId → expiresAt timestamp. */
  const [nodePulses, setNodePulses] = useState<Record<string, number>>({});
  const packetSeqRef = useRef(0);
  const lastIdxRef = useRef(0);

  /* GC packets after their TTL so the SVG doesn't grow forever. */
  useEffect(() => {
    if (packets.length === 0) return;
    const t = setTimeout(() => {
      const now = Date.now();
      setPackets((prev) => prev.filter((p) => now - p.bornAt < PACKET_TTL_MS));
      setNodePulses((prev) => {
        const next: Record<string, number> = {};
        for (const [k, v] of Object.entries(prev)) if (v > now) next[k] = v;
        return next;
      });
    }, 250);
    return () => clearTimeout(t);
  }, [packets]);

  /* Consume new events to drive the active phase + counters + packets. */
  useEffect(() => {
    if (!open) { lastIdxRef.current = events.length; return; }
    const fresh = events.slice(lastIdxRef.current);
    lastIdxRef.current = events.length;
    if (fresh.length === 0) return;
    let nextActive = activePhase;
    let nextCounts: Record<AgentPhase, number> | null = null;
    let nextTools: Record<CreditTool, number> | null = null;
    let pulsed = false;
    const newPackets: Packet[] = [];
    const arrivalUpdates: Record<string, number> = {};
    const now = Date.now();
    const arriveAt = now + PACKET_TTL_MS - 200;
    const edgeMap = new Map(EDGES.map((e) => [e.id, e]));

    const emitOnEdge = (edgeId: string, color: string) => {
      const edge = edgeMap.get(edgeId);
      if (!edge) return;
      packetSeqRef.current += 1;
      newPackets.push({
        id: `pk-${packetSeqRef.current}`,
        edgeId,
        color,
        targetNodeId: edge.to,
        bornAt: now,
      });
      arrivalUpdates[edge.to] = arriveAt;
    };

    for (const e of fresh) {
      if (e.type === 'agent_phase') {
        nextActive = e.phase;
        pulsed = true;
        const edgeId = PHASE_EDGE[e.phase];
        if (edgeId) {
          // Wave of 3 staggered packets to mark the phase boundary.
          for (let i = 0; i < 3; i++) {
            setTimeout(() => emitOnEdge(edgeId, PHASE_COLOR[e.phase].to), i * 90);
          }
          emitOnEdge(edgeId, PHASE_COLOR[e.phase].from);
        }
      } else if (e.type === 'agent_stamp') {
        nextCounts ??= { ...counts };
        nextCounts[e.phase] = (nextCounts[e.phase] ?? 0) + 1;
        const edgeId = KIND_EDGE[e.kind];
        if (edgeId) emitOnEdge(edgeId, PHASE_COLOR[e.phase].to);
      } else if (e.type === 'tool_call_start') {
        nextTools ??= { ...toolCounts };
        nextTools[e.tool] = (nextTools[e.tool] ?? 0) + 1;
      } else if (e.type === 'turn_complete') {
        nextActive = null;
        pulsed = true;
        emitOnEdge('synth→response', PHASE_COLOR.synthesize.to);
      }
    }
    if (nextActive !== activePhase) setActivePhase(nextActive);
    if (nextCounts) setCounts(nextCounts);
    if (nextTools) setToolCounts(nextTools);
    if (pulsed) setPulseId((p) => p + 1);
    if (newPackets.length) setPackets((prev) => [...prev, ...newPackets]);
    if (Object.keys(arrivalUpdates).length) {
      setNodePulses((prev) => ({ ...prev, ...arrivalUpdates }));
    }
  }, [events, open, activePhase, counts, toolCounts]);

  /* Reset when modal closes. */
  useEffect(() => {
    if (!open) {
      setActivePhase(null);
      setCounts({ discovery: 0, reasoning: 0, compute: 0, synthesize: 0 });
      setToolCounts({ vertex_search: 0, code_execution: 0, google_search: 0 });
      lastIdxRef.current = 0;
    }
  }, [open]);

  const nodesById = useMemo(() => {
    const m: Record<string, NodeDef> = {};
    for (const n of NODES) m[n.id] = n;
    return m;
  }, []);

  if (!open) return null;

  return (
    <div className="ca-root" role="dialog" aria-modal="true" aria-label="Arquitectura del agente">
      <div className="ca-backdrop" onClick={onClose} />
      <div className="ca-shell">
        <header className="ca-header">
          <div className="ca-header__title">
            <span className="ca-eyebrow">Topología en vivo</span>
            <h2>Anatomía de Andesia Crédito</h2>
            <p>
              DAG en 4 fases — Discovery · Reasoning · Compute · Synthesize.
              Las aristas se iluminan según la fase activa del agente real.
            </p>
          </div>
          <PhaseLegend active={activePhase} counts={counts} />
          <button type="button" className="ca-close" onClick={onClose} aria-label="Cerrar">
            <span className="material-symbols-outlined" aria-hidden>close</span>
          </button>
        </header>

        <div className="ca-stage">
          <svg
            viewBox={`0 0 ${VB.w} ${VB.h}`}
            className="ca-pipeline"
            preserveAspectRatio="xMidYMid meet"
          >
            <defs>
              {/* Per-phase gradients */}
              {(Object.entries(PHASE_COLOR) as [AgentPhase, { from: string; to: string }][]).map(([phase, c]) => (
                <linearGradient key={phase} id={`gr-${phase}`} x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor={c.from} />
                  <stop offset="100%" stopColor={c.to} />
                </linearGradient>
              ))}
              <linearGradient id="gr-base" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#5a6378" />
                <stop offset="100%" stopColor="#7888a8" />
              </linearGradient>
              <filter id="caGlow" x="-30%" y="-30%" width="160%" height="160%">
                <feGaussianBlur stdDeviation="3" />
                <feMerge>
                  <feMergeNode />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
              <filter id="caGlowStrong" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="6" />
                <feMerge>
                  <feMergeNode />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
              {/* Path defs for animateMotion */}
              {EDGES.map((e) => (
                <path key={e.id} id={`p-${e.id}`} d={edgePath(e, nodesById)} />
              ))}
              {/* Arrowheads per phase */}
              {(Object.keys(PHASE_COLOR) as AgentPhase[]).map((phase) => (
                <marker
                  key={phase}
                  id={`arrow-${phase}`}
                  viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6"
                  orient="auto-start-reverse"
                >
                  <path d="M 0 0 L 10 5 L 0 10 z" fill={PHASE_COLOR[phase].to} />
                </marker>
              ))}
              <marker id="arrow-base" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#7888a8" />
              </marker>
            </defs>

            {/* Phase column backdrops */}
            <PhaseColumns active={activePhase} />

            {/* Edges (under nodes) */}
            {EDGES.map((e) => (
              <Edge
                key={e.id}
                edge={e}
                d={edgePath(e, nodesById)}
                mid={midpoint(e, nodesById)}
                active={!!e.phase && e.phase === activePhase}
                pulseId={pulseId}
              />
            ))}

            {/* Nodes */}
            {NODES.map((n) => (
              <NodeBox
                key={n.id}
                node={n}
                active={!!n.phase && n.phase === activePhase}
                arriving={(nodePulses[n.id] ?? 0) > Date.now()}
                badgeCount={
                  n.id === 'discovery' ? toolCounts.vertex_search :
                  n.id === 'compute'   ? toolCounts.code_execution :
                  n.id === 'reasoning' ? counts.reasoning :
                  n.id === 'synth'     ? counts.synthesize :
                  undefined
                }
              />
            ))}

            {/* Token packets — overlay on top of nodes for max visibility */}
            <g className="ca-packets">
              {packets.map((p) => (
                <g key={p.id} className="ca-packet">
                  <circle r="6" fill={p.color} opacity="0.35" filter="url(#caGlowStrong)">
                    <animateMotion dur={`${PACKET_TTL_MS}ms`} fill="freeze" rotate="auto">
                      <mpath href={`#p-${p.edgeId}`} />
                    </animateMotion>
                  </circle>
                  <circle r="3.2" fill="#fff">
                    <animateMotion dur={`${PACKET_TTL_MS}ms`} fill="freeze">
                      <mpath href={`#p-${p.edgeId}`} />
                    </animateMotion>
                    <animate attributeName="opacity" values="0;1;1;0"
                      keyTimes="0;0.1;0.85;1" dur={`${PACKET_TTL_MS}ms`} fill="freeze" />
                  </circle>
                </g>
              ))}
            </g>
          </svg>

          {/* Right rail: live status */}
          <aside className="ca-rail">
            <RailStatus active={activePhase} counts={counts} toolCounts={toolCounts} />
            <RailHint />
          </aside>
        </div>
      </div>
    </div>
  );
}

/* ── Sub-components ─────────────────────────────────────────────────────── */

function PhaseColumns({ active }: { active: AgentPhase | null }) {
  /* Subtle vertical bands behind the diagram — one per phase column.
   * The active column gets a brighter wash so the eye lands there. */
  const cols: { phase: AgentPhase; x: number; w: number }[] = [
    { phase: 'discovery',  x: 740, w: 270 },
    { phase: 'reasoning',  x: 740, w: 270 },
    { phase: 'compute',    x: 740, w: 270 },
    { phase: 'synthesize', x: 740, w: 270 },
  ];
  // Each column overlay only for the row of its phase — we use horizontal bands.
  const rows: { phase: AgentPhase; y: number; h: number }[] = [
    { phase: 'discovery',  y:  90, h: 130 },
    { phase: 'reasoning',  y: 220, h: 130 },
    { phase: 'compute',    y: 350, h: 130 },
    { phase: 'synthesize', y: 480, h: 130 },
  ];
  void cols;
  return (
    <g className="ca-bands">
      {rows.map((r) => (
        <rect
          key={r.phase}
          x="730" y={r.y} width="290" height={r.h}
          rx="14"
          className={`ca-band ca-band--${r.phase}${active === r.phase ? ' is-active' : ''}`}
        />
      ))}
    </g>
  );
}

function PhaseLegend({
  active,
  counts,
}: {
  active: AgentPhase | null;
  counts: Record<AgentPhase, number>;
}) {
  const items: { id: AgentPhase; label: string }[] = [
    { id: 'discovery', label: 'Discovery' },
    { id: 'reasoning', label: 'Reasoning' },
    { id: 'compute',   label: 'Compute' },
    { id: 'synthesize',label: 'Synthesize' },
  ];
  return (
    <div className="ca-legend">
      {items.map((it) => (
        <div key={it.id} className={`ca-legend__item ca-legend__item--${it.id}${active === it.id ? ' is-on' : ''}`}>
          <span className="ca-legend__dot" />
          <span className="ca-legend__label">{it.label}</span>
          <span className="ca-legend__count">{counts[it.id]}</span>
        </div>
      ))}
    </div>
  );
}

function Edge({
  edge,
  d,
  mid,
  active,
  pulseId,
}: {
  edge: EdgeDef;
  d: string;
  mid: { x: number; y: number };
  active: boolean;
  pulseId: number;
}) {
  const stroke = edge.phase ? `url(#gr-${edge.phase})` : 'url(#gr-base)';
  const arrow = edge.phase ? `arrow-${edge.phase}` : 'arrow-base';
  return (
    <g className={`ca-edge ca-edge--${edge.phase ?? 'base'}${active ? ' is-active' : ''}`}>
      {/* Halo */}
      <path
        d={d}
        fill="none"
        stroke={stroke}
        strokeWidth={active ? 10 : 5}
        strokeLinecap="round"
        opacity={active ? 0.3 : 0.08}
        filter="url(#caGlowStrong)"
      />
      {/* Main line */}
      <path
        d={d}
        fill="none"
        stroke={stroke}
        strokeWidth={active ? 2.6 : 1.6}
        strokeLinecap="round"
        strokeDasharray={active ? '0' : '4 6'}
        markerEnd={`url(#${arrow})`}
        className="ca-edge__line"
        opacity={active ? 1 : 0.55}
      />
      {/* Idle particle (always-on, slow) */}
      <circle r="2.5" fill="#fff" opacity="0.45" className="ca-edge__dot">
        <animateMotion dur="5s" repeatCount="indefinite">
          <mpath href={`#p-${edge.id}`} />
        </animateMotion>
      </circle>
      {/* Burst particles when phase becomes active — re-key on pulseId */}
      {active && [0, 0.18, 0.36, 0.54].map((delay) => (
        <circle
          key={`b-${pulseId}-${delay}`}
          r="3.5"
          fill="#fff"
          opacity="1"
          className="ca-edge__dot ca-edge__dot--burst"
        >
          <animateMotion dur="1.2s" begin={`${delay}s`} repeatCount="3" fill="freeze">
            <mpath href={`#p-${edge.id}`} />
          </animateMotion>
        </circle>
      ))}
      {/* Edge label */}
      {edge.label && (
        <g transform={`translate(${mid.x} ${mid.y})`} className="ca-edge__label-grp">
          <rect x="-44" y="-10" width="88" height="20" rx="6"
            fill={active ? `url(#gr-${edge.phase ?? 'base'})` : 'rgba(8, 12, 24, 0.85)'}
            stroke={active ? 'rgba(255,255,255,0.4)' : 'rgba(120, 140, 200, 0.35)'}
            strokeWidth="1"
          />
          <text textAnchor="middle" y="4" className="ca-edge__label">
            {edge.label}
          </text>
        </g>
      )}
    </g>
  );
}

function NodeBox({
  node,
  active,
  arriving,
  badgeCount,
}: {
  node: NodeDef;
  active: boolean;
  arriving?: boolean;
  badgeCount?: number;
}) {
  const phaseColor = node.phase ? PHASE_COLOR[node.phase] : null;
  return (
    <g
      transform={`translate(${node.x} ${node.y})`}
      className={`ca-node ca-node--${node.kind}${active ? ' is-active' : ''}${arriving ? ' is-arriving' : ''}${node.phase ? ` ca-node--${node.phase}` : ''}`}
    >
      {active && (
        <rect
          x="-8" y="-8" width={node.w + 16} height={node.h + 16}
          rx="14" fill="none"
          stroke={phaseColor ? `url(#gr-${node.phase})` : 'rgba(255,255,255,0.5)'}
          strokeWidth="2"
          className="ca-node__ripple"
        />
      )}
      {arriving && (
        <rect
          x="-4" y="-4" width={node.w + 8} height={node.h + 8}
          rx="14" fill="none"
          stroke={phaseColor ? `url(#gr-${node.phase})` : 'rgba(255,255,255,0.85)'}
          strokeWidth="2.5"
          className="ca-node__arrival"
        />
      )}
      <rect width={node.w} height={node.h} rx="12" className="ca-node__bg" />
      <foreignObject x="0" y="0" width={node.w} height={node.h}>
        <div className="ca-node__body" {...({ xmlns: 'http://www.w3.org/1999/xhtml' } as React.HTMLAttributes<HTMLDivElement>)}>
          <span className="material-symbols-outlined ca-node__icon" aria-hidden>
            {node.icon}
          </span>
          <div className="ca-node__text">
            <strong>{node.title}</strong>
            {node.subtitle && <small>{node.subtitle}</small>}
          </div>
        </div>
      </foreignObject>
      {typeof badgeCount === 'number' && badgeCount > 0 && (
        <g transform={`translate(${node.w - 14} 14)`}>
          <circle r="14" className="ca-node__badge-bg" />
          <text textAnchor="middle" y="5" className="ca-node__badge-num">{badgeCount}</text>
        </g>
      )}
    </g>
  );
}

function RailStatus({
  active,
  counts,
  toolCounts,
}: {
  active: AgentPhase | null;
  counts: Record<AgentPhase, number>;
  toolCounts: Record<CreditTool, number>;
}) {
  return (
    <div className="ca-rail__card">
      <div className="ca-rail__head">
        <span className={`ca-rail__pulse${active ? ' is-on' : ''}`} />
        <strong>{active ? `Fase activa: ${active}` : 'Agente en reposo'}</strong>
      </div>
      <ul className="ca-rail__list">
        <li>
          <span>Tool calls (Discovery)</span>
          <strong>{toolCounts.vertex_search}</strong>
        </li>
        <li>
          <span>Ejecuciones de código</span>
          <strong>{toolCounts.code_execution}</strong>
        </li>
        <li>
          <span>Eventos de razonamiento</span>
          <strong>{counts.reasoning}</strong>
        </li>
        <li>
          <span>Tokens en sintetización</span>
          <strong>{counts.synthesize}</strong>
        </li>
      </ul>
    </div>
  );
}

function RailHint() {
  return (
    <div className="ca-rail__hint">
      <span className="material-symbols-outlined" aria-hidden>tips_and_updates</span>
      <p>
        Las aristas <strong>siempre están conectadas</strong>. Las fases inactivas
        muestran un punto gris recorriendo el camino; cuando el backend emite un
        <code> agent_phase</code>, la fase entera se enciende y dispara una ráfaga.
      </p>
    </div>
  );
}
