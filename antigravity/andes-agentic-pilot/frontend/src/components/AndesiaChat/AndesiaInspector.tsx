import { Fragment, useEffect, useState } from 'react';
import type {
  AgentColor,
  Citation,
  ReasoningStep,
  ToolCall,
  TurnRole,
} from '../../mocks';

/* ---------------------------------------------------------------------------
 * AndesiaInspector — explainability side-panel
 *   Renders to the LEFT of the chat panel. Dark theme for visual contrast.
 *   Shows in real-time:
 *     - Active agent constellation (Concierge / Credito / Beneficios / etc.)
 *     - Reasoning trace (chain-of-thought, animated step by step)
 *     - Tool calls (pill cards with args, status, result preview, latency)
 *     - Citations (clickable, opens excerpt drawer)
 * -------------------------------------------------------------------------- */

interface NodeDef {
  role: TurnRole;
  short: string;
  full: string;
  color: AgentColor;
}

const AGENT_NODES: NodeDef[] = [
  { role: 'concierge', short: 'C', full: 'Concierge', color: 'gris' },
  { role: 'credito_agent', short: 'CR', full: 'CreditoAgent', color: 'azul' },
  { role: 'beneficios_agent', short: 'B', full: 'BeneficiosAgent', color: 'amarillo' },
  { role: 'document_ai_agent', short: 'D', full: 'DocumentAI', color: 'morado' },
  { role: 'voice_agent', short: 'V', full: 'VozLive', color: 'rojo' },
];

interface InspectorState {
  activeRole: TurnRole | null;
  recentRoles: TurnRole[]; // history of which agents have been activated (for arrows)
  reasoning: ReasoningStep[]; // visible steps so far for the active agent
  toolCalls: ToolCall[]; // visible tool calls so far
  citations: Citation[]; // visible citations so far
  toolCount: number; // total tool calls executed across the session
  handoffCount: number; // total handoffs across the session
}

export interface AndesiaInspectorProps {
  state: InspectorState;
  isPlaying: boolean;
}

export type { InspectorState };

function formatJsonPretty(obj: Record<string, unknown> | string): string {
  if (typeof obj === 'string') return obj;
  try {
    return JSON.stringify(obj, null, 2);
  } catch {
    return String(obj);
  }
}

function truncate(s: string, max: number): string {
  if (s.length <= max) return s;
  return s.slice(0, max - 1) + '…';
}

function shortType(t: Citation['source_type']): string {
  switch (t) {
    case 'ley': return 'Ley';
    case 'reglamento_ccla': return 'Reglamento CCLA';
    case 'circular_suseso': return 'Circular SUSESO';
    case 'cdn_pdf': return 'PDF';
    default: return 'Fuente';
  }
}

export default function AndesiaInspector({ state, isPlaying }: AndesiaInspectorProps) {
  const { activeRole, recentRoles, reasoning, toolCalls, citations, toolCount, handoffCount } = state;
  const [openCitation, setOpenCitation] = useState<Citation | null>(null);

  // Clear drawer when conversation resets
  useEffect(() => {
    if (citations.length === 0) setOpenCitation(null);
  }, [citations.length]);

  return (
    <aside className="andesia-inspector" aria-label="Panel de explicabilidad de Andesia">
      <header className="andesia-inspector__header">
        <div className="andesia-inspector__title">
          <span className="material-symbols-outlined">network_intelligence</span>
          <span>Andesia Inspector</span>
        </div>
        <div className="andesia-inspector__live">
          <span className={`andesia-inspector__live-dot ${isPlaying ? '' : 'is-idle'}`} />
          {isPlaying ? 'Live trace' : 'Idle'}
        </div>
      </header>

      <div className="andesia-inspector__body">
        {/* === Constellation =============================================== */}
        <section>
          <h4 className="andesia-section__title">
            <span className="andesia-section__title-icon">★</span> Constelación de agentes
          </h4>
          <div className="andesia-constellation">
            <div className="andesia-constellation__row">
              {AGENT_NODES.map((node, i) => {
                const isActive = activeRole === node.role || recentRoles.includes(node.role);
                const isCurrent = activeRole === node.role;
                return (
                  <Fragment key={node.role}>
                    <div
                      className={`andesia-node ${isActive ? 'is-active' : ''}`}
                      title={node.full}
                    >
                      <span className={`andesia-node__dot andesia-color--${node.color}`}>
                        {node.short}
                      </span>
                      <span>{node.full}</span>
                    </div>
                    {i < AGENT_NODES.length - 1 && (
                      <span
                        className={`andesia-arrow ${
                          isCurrent || (recentRoles.includes(node.role) && recentRoles.includes(AGENT_NODES[i + 1].role))
                            ? 'is-lit'
                            : ''
                        }`}
                      >
                        ━▶
                      </span>
                    )}
                  </Fragment>
                );
              })}
            </div>
          </div>
        </section>

        {/* === Reasoning trace ============================================ */}
        <section>
          <h4 className="andesia-section__title">
            <span className="andesia-section__title-icon">🧠</span> Razonamiento
          </h4>
          <div className="andesia-trace" role="log" aria-live="polite">
            {reasoning.length === 0 ? (
              <div className="andesia-trace__empty">
                Esperando turno del agente…
              </div>
            ) : (
              reasoning.map((step) => (
                <div key={step.step_index} className="andesia-trace__step">
                  <span className="andesia-trace__idx">{`#${step.step_index}`}</span>
                  {step.text}
                  <span className="andesia-trace__dur">{`${step.duration_ms}ms`}</span>
                </div>
              ))
            )}
          </div>
        </section>

        {/* === Tool calls ================================================= */}
        <section>
          <h4 className="andesia-section__title">
            <span className="andesia-section__title-icon">🔧</span>
            Tool calls {toolCalls.length > 0 && `(${toolCalls.length})`}
          </h4>
          {toolCalls.length === 0 ? (
            <div className="andesia-trace__empty" style={{ padding: '8px 0' }}>
              Sin llamadas activas.
            </div>
          ) : (
            <div className="andesia-tools">
              {toolCalls.map((tc) => (
                <div
                  key={tc.id}
                  className={`andesia-tool is-${tc.status}`}
                >
                  <div className="andesia-tool__head">
                    <span className="andesia-tool__name">{tc.name}()</span>
                    <span className={`andesia-tool__status andesia-tool__status--${tc.status}`}>
                      {tc.status === 'running' ? <span className="andesia-tool__spin" /> : null}
                      {tc.status === 'success' ? '✓' : null}
                      {tc.status === 'error' ? '!' : null}
                      {tc.status}
                    </span>
                  </div>
                  <pre className="andesia-tool__args">
                    {truncate(formatJsonPretty(tc.args), 320)}
                  </pre>
                  {tc.status === 'success' && (
                    <pre className="andesia-tool__result">
                      {truncate(formatJsonPretty(tc.result), 220)}
                    </pre>
                  )}
                  <span className="andesia-tool__latency">
                    {`⏱ ${tc.latency_ms}ms`}
                  </span>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* === Citations ================================================== */}
        <section>
          <h4 className="andesia-section__title">
            <span className="andesia-section__title-icon">📑</span>
            Citaciones {citations.length > 0 && `(${citations.length})`}
          </h4>
          {citations.length === 0 ? (
            <div className="andesia-trace__empty" style={{ padding: '8px 0' }}>
              Las fuentes citadas aparecerán aquí.
            </div>
          ) : (
            <div className="andesia-cite-list">
              {citations.map((c) => (
                <button
                  key={c.id}
                  type="button"
                  className="andesia-cite-row"
                  onClick={() => setOpenCitation(c)}
                  style={{ textAlign: 'left', font: 'inherit', cursor: 'pointer' }}
                >
                  <div className="andesia-cite-row__head">
                    <span className="andesia-cite-row__src">{c.source_title}</span>
                    <span className="andesia-cite-row__score">
                      {`${(c.similarity_score * 100).toFixed(0)}%`}
                    </span>
                  </div>
                  <div className="andesia-cite-row__body">{c.paragraph_excerpt}</div>
                  <div className="andesia-cite-row__type">{shortType(c.source_type)}</div>
                </button>
              ))}
            </div>
          )}
        </section>
      </div>

      <footer className="andesia-inspector__footer">
        <span>tools: <b>{toolCount}</b></span>
        <span>handoffs: <b>{handoffCount}</b></span>
        <span>cites: <b>{citations.length}</b></span>
        <span>vertex-ai/adk</span>
      </footer>

      {/* === Citation drawer =============================================== */}
      {openCitation && (
        <div
          className="andesia-cite-drawer"
          role="dialog"
          aria-label="Detalle de la citación"
        >
          <div className="andesia-cite-drawer__head">
            <div className="andesia-cite-drawer__title">{openCitation.source_title}</div>
            <button
              type="button"
              className="andesia-icon-btn"
              onClick={() => setOpenCitation(null)}
              aria-label="Cerrar"
              style={{ color: '#fff' }}
            >
              <span className="material-symbols-outlined">close</span>
            </button>
          </div>
          <div className="andesia-cite-drawer__excerpt">
            {openCitation.paragraph_excerpt}
          </div>
          <div className="andesia-cite-drawer__meta">
            <span>chunk: {openCitation.chunk_id}</span>
            <span>score: {openCitation.similarity_score.toFixed(2)}</span>
            <span>tipo: {shortType(openCitation.source_type)}</span>
          </div>
          <a
            className="andesia-cite-drawer__link"
            href={openCitation.source_url}
            target="_blank"
            rel="noreferrer"
          >
            Abrir fuente original
            <span className="material-symbols-outlined" style={{ fontSize: 14 }}>
              open_in_new
            </span>
          </a>
        </div>
      )}
    </aside>
  );
}

