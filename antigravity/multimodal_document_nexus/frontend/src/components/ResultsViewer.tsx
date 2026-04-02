import React, { useEffect, useState } from 'react';
import * as Tabs from '@radix-ui/react-tabs';
import { Database, Image as ImageIcon, Activity, Search, Trophy, AlertTriangle, CheckCircle, XCircle, Table, Filter, Download, ChevronDown, ChevronRight } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { IndexedDocuments } from './IndexedDocuments';

// Types for deep evaluation
interface GroundedSpan {
  text: string;
  is_grounded: boolean;
  source_id: string | null;
  confidence: number;
}

interface EvaluationScores {
  faithfulness: number;
  groundedness: number;
  completeness: number;
  answer_relevance: number;
  context_precision: number;
  total: number;
}

interface GroundingAnalysis {
  grounded_percentage: number;
  ungrounded_percentage: number;
  grounded_spans: GroundedSpan[];
  hallucination_count: number;
  hallucination_examples: string[];
}

interface RAGResult {
  answer: string;
  context: any[];
  context_chars: number;
  scores: EvaluationScores;
  grounding: GroundingAnalysis;
  reasoning: string;
}

interface DeepEvaluation {
  query: string;
  hierarchical: RAGResult;
  simple: RAGResult;
  winner: string;
  winner_reasoning: string;
  eval_time_seconds: number;
}

export interface PipelineEntity {
  chunk_id: string;
  document_name: string;
  entity_type: string;
  page_number: number;
  content: string;
  embedding?: number[];
}

export interface ADKTrace {
  agent_name: string;
  page_number: number;
  start_time: string;
  end_time: string;
  duration_seconds: number;
  entities_extracted: number;
}

interface ResultsViewerProps {
  data: PipelineEntity[];
  annotatedImages?: string[];
  traces?: ADKTrace[];
  evaluatorLogs?: string;
  latestQuery?: string;
  latestAnswer?: string;
  latestRetrieval?: any[];
  llmPrompt?: string;
  activeHighlight: string | null;
  onHighlightClick: (chunkId: string) => void;
  activeTab: string;
  onTabChange: (value: string) => void;
  onSelectDocument?: (docName: string) => void;
  isIndexedLoading?: boolean;
}

export const ResultsViewer: React.FC<ResultsViewerProps> = ({
  data, annotatedImages, traces, evaluatorLogs, latestQuery, latestAnswer, latestRetrieval, llmPrompt, activeHighlight, onHighlightClick, activeTab, onTabChange, onSelectDocument, isIndexedLoading
}) => {
  useEffect(() => {
    if (activeHighlight && activeTab === 'bounding-boxes') {
      const activeChunk = data?.find((c: PipelineEntity) => c.chunk_id === activeHighlight);
      if (activeChunk) {
        let attempts = 0;
        const scrollInterval = setInterval(() => {
          const boxElement = document.getElementById(`box-${activeChunk.chunk_id}`) as HTMLElement;
          const pageElement = document.getElementById(`annotated-page-${activeChunk.page_number}`) as HTMLElement;
          
          if (boxElement) {
            clearInterval(scrollInterval);
            boxElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
          } else if (pageElement) {
            clearInterval(scrollInterval);
            pageElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
          
          attempts++;
          if (attempts > 10) {
            clearInterval(scrollInterval);
          }
        }, 100);
      }
    }
  }, [activeHighlight, activeTab, data]);

  if (!data && !latestRetrieval && !evaluatorLogs && !llmPrompt) return null;

  return (
    <div className="results-viewer">
      <Tabs.Root className="tabs-root" value={activeTab} onValueChange={onTabChange}>
        <Tabs.List className="tabs-list" aria-label="Processing Results">
          <Tabs.Trigger className="tabs-trigger" value="bigquery">
            <Database size={16} /> BigQuery Preview
          </Tabs.Trigger>
          <Tabs.Trigger className="tabs-trigger" value="bounding-boxes">
            <ImageIcon size={16} /> Document Viewer
          </Tabs.Trigger>
          <Tabs.Trigger className="tabs-trigger" value="tracing">
            <Activity size={16} /> ADK Tracing
          </Tabs.Trigger>
          <Tabs.Trigger className="tabs-trigger" value="logs">
            <Database size={16} /> Logs
          </Tabs.Trigger>
          <Tabs.Trigger className="tabs-trigger" value="retrieval">
            <Search size={16} /> Retrieval
          </Tabs.Trigger>
          <Tabs.Trigger className="tabs-trigger" value="explorer">
            <Table size={16} /> Explorer
          </Tabs.Trigger>
        </Tabs.List>

        <Tabs.Content className="tabs-content" value="bigquery">
          <div className="bq-table-container">
            <table className="bq-table">
              <thead>
                <tr>
                  <th>Chunk ID</th>
                  <th>Document</th>
                  <th>Page</th>
                  <th>Type</th>
                  <th>Content Overview</th>
                  <th>Vector</th>
                </tr>
              </thead>
              <tbody>
                {data.map((row) => (
                  <tr
                    key={row.chunk_id}
                    className={activeHighlight === row.chunk_id ? 'highlighted-row' : ''}
                    onClick={() => onHighlightClick(row.chunk_id)}
                    style={{ cursor: 'pointer' }}
                  >
                    <td style={{ fontFamily: 'monospace', color: 'var(--accent-cyan)' }}>
                      {row.chunk_id}
                    </td>
                    <td>{row.document_name || "Unknown"}</td>
                    <td>{row.page_number}</td>
                    <td>
                      <span className={`entity-badge ${row.entity_type.toLowerCase()}`}>
                        {row.entity_type}
                      </span>
                    </td>
                    <td className="content-cell">
                      <div className="content-truncate" title={row.content}>{row.content}</div>
                    </td>
                    <td className="embedding-cell">
                      {row.embedding ? `Yes (3072d)` : 'No'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Tabs.Content>

        <Tabs.Content className="tabs-content" value="bounding-boxes">
          {annotatedImages && annotatedImages.length > 0 ? (
            <div className="bb-gallery">
              {annotatedImages.map((imgSrc, idx) => {
                const pageChunks = data.filter(d => d.page_number === idx + 1);

                return (
                  <div key={idx} id={`annotated-page-${idx + 1}`} className="bb-image-wrapper" style={{ position: 'relative' }}>
                    <img 
                      src={imgSrc} 
                      alt={`Annotated Page ${idx + 1}`} 
                      style={{ display: 'block', width: '100%', height: 'auto' }} 
                    />

                    {/* Render Highlight Overlays */}
                    {pageChunks.map(chunk => {
                      const bb = (chunk as any).box_2d;
                      if (!bb || bb.length !== 4) return null;

                      const type = chunk.entity_type.toLowerCase();
                      const isTargetBox = ['chart', 'image', 'table'].includes(type);
                      const isHighlighted = activeHighlight === chunk.chunk_id;

                      const [ymin, xmin, ymax, xmax] = bb;
                      const top = `${ymin / 10}%`;
                      const left = `${xmin / 10}%`;
                      const height = `${(ymax - ymin) / 10}%`;
                      const width = `${(xmax - xmin) / 10}%`;

                      if (!isTargetBox) {
                        return (
                          <div
                            key={chunk.chunk_id}
                            id={`box-${chunk.chunk_id}`}
                            style={{
                              position: 'absolute',
                              top, left, height, width,
                              pointerEvents: 'none',
                              border: isHighlighted ? '2px solid var(--accent-cyan)' : 'none',
                              backgroundColor: isHighlighted ? 'rgba(0, 255, 255, 0.1)' : 'transparent',
                              zIndex: isHighlighted ? 10 : 1,
                              transition: 'all 0.2s ease-in-out',
                            }}
                          />
                        );
                      }

                      return (
                        <div
                          key={chunk.chunk_id}
                          id={`box-${chunk.chunk_id}`}
                          title={`Chunk: ${chunk.chunk_id}\nType: ${chunk.entity_type}`}
                          onClick={() => onHighlightClick(chunk.chunk_id)}
                          style={{
                            position: 'absolute',
                            top, left, height, width,
                            border: isHighlighted ? '3px solid var(--accent-magenta)' : '2px solid transparent',
                            backgroundColor: isHighlighted ? 'rgba(255, 0, 255, 0.2)' : 'rgba(0, 255, 255, 0.05)',
                            cursor: 'pointer',
                            transition: 'all 0.2s ease-in-out',
                            zIndex: isHighlighted ? 10 : 1
                          }}
                          onMouseEnter={(e) => {
                            if (!isHighlighted) e.currentTarget.style.border = '2px solid var(--accent-cyan)';
                          }}
                          onMouseLeave={(e) => {
                            if (!isHighlighted) e.currentTarget.style.border = '2px solid transparent';
                          }}
                        />
                      );
                    })}
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="placeholder-tab" style={{ flex: 1, padding: '2rem', display: 'flex', flexDirection: 'column', gap: '2rem', overflowY: 'auto' }}>
              <div className="upload-view-title" style={{ textAlign: 'center', marginBottom: 0 }}>
                <ImageIcon size={48} className="text-accent-cyan" style={{ opacity: 0.5, marginBottom: '1rem', display: 'inline-block' }} />
                <h3 style={{ fontSize: '1.5rem', marginBottom: '0.5rem', color: 'var(--text-primary)' }}>Visual Document Viewer</h3>
                <p style={{ maxWidth: '100%', color: 'var(--text-secondary)' }}>Select a document from the index to view its contents.</p>
              </div>
              
              {isIndexedLoading && (
                <div style={{ padding: '1rem', background: 'rgba(34, 211, 238, 0.1)', border: '1px solid var(--accent-cyan)', borderRadius: '8px', textAlign: 'center', marginBottom: '1rem' }}>
                  <div className="pulsing-text" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                    <Activity className="animate-spin" />
                    <span style={{ fontWeight: 600, color: 'var(--accent-cyan)' }}>Loading document data...</span>
                  </div>
                </div>
              )}
              
              {onSelectDocument && <IndexedDocuments onSelectDocument={onSelectDocument} />}
            </div>
          )}
        </Tabs.Content>

        <Tabs.Content className="tabs-content" value="tracing">
          {traces && traces.length > 0 ? (
            <div className="bq-table-container">
              <table className="bq-table">
                <thead>
                  <tr>
                    <th>Agent</th>
                    <th>Page</th>
                    <th>Duration</th>
                    <th>Extracted</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {traces.map((trace, idx) => (
                    <tr key={idx}>
                      <td style={{ fontFamily: 'monospace', color: 'var(--accent-orange)' }}>
                        {trace.agent_name}
                      </td>
                      <td>{trace.page_number}</td>
                      <td>{trace.duration_seconds}s</td>
                      <td>
                        <span className="entity-badge text">{trace.entities_extracted} items</span>
                      </td>
                      <td>
                        <span style={{ color: 'var(--accent-green)', fontSize: '0.8rem', fontWeight: 600 }}>SUCCESS</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="placeholder-tab">
              <Activity size={48} className="text-accent-orange" style={{ opacity: 0.5, marginBottom: '1rem' }} />
              <h3>ADK Execution Traces</h3>
              <p className="text-text-secondary">View the timeline of Google ADK agent execution and tool calls.</p>
            </div>
          )}
        </Tabs.Content>

        <Tabs.Content className="tabs-content" value="logs" style={{ height: '100%', overflowY: 'auto' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', paddingRight: '0.5rem', paddingBottom: '2rem' }}>
            {/* 1. Original Query */}
            {latestQuery && (
              <div className="evaluator-card" style={{ background: 'rgba(56, 189, 248, 0.05)', border: '1px solid rgba(56, 189, 248, 0.3)', borderRadius: '12px', padding: '1.5rem' }}>
                <h3 style={{ color: 'var(--accent-cyan)', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', marginTop: 0 }}>
                  Original Query
                </h3>
                <div style={{ color: 'var(--text-primary)', lineHeight: 1.6, fontSize: '0.95rem', fontWeight: 500 }}>
                  {latestQuery}
                </div>
              </div>
            )}

            {/* 2. Vector Search Retrieval */}
            {latestRetrieval && latestRetrieval.length > 0 && (
              <div className="evaluator-card" style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid rgba(255, 255, 255, 0.1)', borderRadius: '12px', padding: '1.5rem' }}>
                <h3 style={{ color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', marginTop: 0 }}>
                  Vector Search Extraction
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {latestRetrieval.map((chunk, idx) => (
                    <div key={chunk.chunk_id || idx} style={{ background: 'rgba(0,0,0,0.2)', padding: '1rem', borderRadius: '8px', borderLeft: '3px solid var(--accent-orange)' }}>
                      <div style={{ fontSize: '0.8rem', color: 'var(--accent-orange)', marginBottom: '0.5rem', fontFamily: 'monospace' }}>
                        Source: {chunk.document_name} | Page {chunk.page_number} | Score: {chunk.embedding ? (chunk as any).distance?.toFixed(4) || 'N/A' : ((chunk as any).distance ? (chunk as any).distance.toFixed(4) : 'Exact/LLM')}
                      </div>
                      <div style={{ color: 'var(--text-primary)', fontSize: '0.9rem', lineHeight: 1.5 }}>
                        {chunk.content}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 3. Full LLM Prompt */}
            {llmPrompt && (
              <div className="evaluator-card" style={{ background: 'rgba(245, 158, 11, 0.05)', border: '1px solid rgba(245, 158, 11, 0.3)', borderRadius: '12px', padding: '1.5rem' }}>
                <h3 style={{ color: 'var(--accent-orange)', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', marginTop: 0 }}>
                  LLM Prompt Sent to Gemini
                </h3>
                <div style={{ color: 'var(--text-primary)', lineHeight: 1.6, fontSize: '0.9rem', whiteSpace: 'pre-wrap', fontFamily: 'monospace', background: 'rgba(0,0,0,0.3)', padding: '1rem', borderRadius: '8px' }}>
                  {llmPrompt}
                </div>
              </div>
            )}

            {/* 4. LLM Answer */}
            {latestAnswer && (
              <div className="evaluator-card" style={{ background: 'rgba(192, 132, 252, 0.05)', border: '1px solid rgba(192, 132, 252, 0.3)', borderRadius: '12px', padding: '1.5rem' }}>
                <h3 style={{ color: 'var(--accent-purple)', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', marginTop: 0 }}>
                  LLM Answer
                </h3>
                <div style={{ color: 'var(--text-primary)', lineHeight: 1.6, fontSize: '0.95rem' }}>
                  <ReactMarkdown>{latestAnswer}</ReactMarkdown>
                </div>
              </div>
            )}

            {/* 5. Evaluator Analysis */}
            {evaluatorLogs && (
               <div className="evaluator-card" style={{ background: 'rgba(34, 197, 94, 0.05)', border: '1px solid rgba(34, 197, 94, 0.3)', borderRadius: '12px', padding: '1.5rem' }}>
                 <h3 style={{ color: 'var(--accent-green)', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', marginTop: 0 }}>
                   <Activity size={18} /> Asynchronous ADK Evaluator Analysis
                 </h3>
                 <div style={{ color: 'var(--text-primary)', lineHeight: 1.6, fontSize: '0.95rem' }}>
                    <ReactMarkdown>{evaluatorLogs}</ReactMarkdown>
                 </div>
               </div>
            )}
            
            {!latestQuery && !latestRetrieval?.length && !llmPrompt && !latestAnswer && !evaluatorLogs && (
                <div className="placeholder-tab" style={{ padding: '1.5rem', minHeight: 'auto' }}>
                   No retrieval logs available yet.
                </div>
            )}
          </div>
        </Tabs.Content>

        <Tabs.Content className="tabs-content" value="retrieval" style={{ height: '100%', overflowY: 'auto' }}>
          <DeepEvaluationPanel query={latestQuery || ""} />
        </Tabs.Content>

        <Tabs.Content className="tabs-content" value="explorer" style={{ height: '100%', overflowY: 'auto' }}>
          <DataExplorerPanel />
        </Tabs.Content>
      </Tabs.Root>
    </div>
  );
};

// Deep Evaluation Panel Component
const DeepEvaluationPanel: React.FC<{ query: string }> = ({ query }) => {
  const [evaluation, setEvaluation] = useState<DeepEvaluation | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runDeepEvaluation = async () => {
    if (!query.trim()) {
      setError("Please enter a query first");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('query', query);

      const response = await fetch('/api/compare-rag', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Evaluation failed');
      }

      const data = await response.json();
      setEvaluation(data);
    } catch (e) {
      setError(`Evaluation failed: ${e}`);
    } finally {
      setIsLoading(false);
    }
  };

  const renderScoreBar = (score: number, max: number = 5, label: string) => {
    const percentage = (score / max) * 100;
    const color = percentage >= 80 ? 'var(--accent-green)' :
                  percentage >= 60 ? 'var(--accent-cyan)' :
                  percentage >= 40 ? 'var(--accent-orange)' : 'var(--accent-magenta)';

    return (
      <div style={{ marginBottom: '0.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.25rem' }}>
          <span style={{ color: 'var(--text-secondary)' }}>{label}</span>
          <span style={{ color, fontWeight: 600 }}>{score}/{max}</span>
        </div>
        <div style={{ background: 'rgba(255,255,255,0.1)', borderRadius: '4px', height: '6px', overflow: 'hidden' }}>
          <div style={{ width: `${percentage}%`, height: '100%', background: color, transition: 'width 0.5s ease' }} />
        </div>
      </div>
    );
  };

  const renderGroundingVisualization = (result: RAGResult) => {
    const { grounding } = result;

    return (
      <div style={{ marginTop: '1rem' }}>
        <h4 style={{ color: 'var(--text-primary)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Activity size={16} /> Grounding Analysis
        </h4>

        {/* Percentage bars */}
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
          <div style={{ flex: 1, background: 'rgba(34, 197, 94, 0.1)', border: '1px solid rgba(34, 197, 94, 0.3)', borderRadius: '8px', padding: '1rem', textAlign: 'center' }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--accent-green)' }}>{grounding.grounded_percentage.toFixed(1)}%</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.25rem' }}>
              <CheckCircle size={12} /> Grounded
            </div>
          </div>
          <div style={{ flex: 1, background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '8px', padding: '1rem', textAlign: 'center' }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#ef4444' }}>{grounding.ungrounded_percentage.toFixed(1)}%</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.25rem' }}>
              <AlertTriangle size={12} /> Ungrounded
            </div>
          </div>
        </div>

        {/* Highlighted spans */}
        {grounding.grounded_spans && grounding.grounded_spans.length > 0 && (
          <div style={{ background: 'rgba(0,0,0,0.2)', borderRadius: '8px', padding: '1rem', marginBottom: '1rem' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Answer with grounding highlights:</div>
            <div style={{ lineHeight: 1.8 }}>
              {grounding.grounded_spans.map((span, idx) => (
                <span
                  key={idx}
                  style={{
                    background: span.is_grounded ? 'rgba(34, 197, 94, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                    borderBottom: span.is_grounded ? '2px solid var(--accent-green)' : '2px solid #ef4444',
                    padding: '2px 4px',
                    borderRadius: '2px',
                    marginRight: '2px',
                    cursor: 'help',
                  }}
                  title={span.is_grounded ? `Source: [${span.source_id}] (${(span.confidence * 100).toFixed(0)}% confidence)` : 'Not found in context - potential hallucination'}
                >
                  {span.text}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Hallucination examples */}
        {grounding.hallucination_count > 0 && grounding.hallucination_examples.length > 0 && (
          <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '8px', padding: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#ef4444', fontWeight: 600, marginBottom: '0.5rem' }}>
              <XCircle size={16} /> {grounding.hallucination_count} Potential Hallucination(s) Detected
            </div>
            <ul style={{ margin: 0, paddingLeft: '1.25rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
              {grounding.hallucination_examples.map((ex, idx) => (
                <li key={idx} style={{ marginBottom: '0.25rem' }}>{ex}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  };

  const renderRAGResult = (result: RAGResult, title: string, isWinner: boolean) => (
    <div style={{
      flex: 1,
      background: isWinner ? 'rgba(34, 197, 94, 0.05)' : 'rgba(255,255,255,0.02)',
      border: isWinner ? '2px solid var(--accent-green)' : '1px solid rgba(255,255,255,0.1)',
      borderRadius: '12px',
      padding: '1.25rem',
      position: 'relative'
    }}>
      {isWinner && (
        <div style={{ position: 'absolute', top: '-12px', left: '50%', transform: 'translateX(-50%)', background: 'var(--accent-green)', color: '#000', padding: '2px 12px', borderRadius: '10px', fontSize: '0.7rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '4px' }}>
          <Trophy size={12} /> WINNER
        </div>
      )}

      <h3 style={{ color: 'var(--accent-cyan)', marginBottom: '1rem', marginTop: '0.5rem' }}>{title}</h3>

      {/* Scores */}
      <div style={{ marginBottom: '1rem' }}>
        {renderScoreBar(result.scores.faithfulness, 5, 'Faithfulness')}
        {renderScoreBar(result.scores.groundedness, 5, 'Groundedness')}
        {renderScoreBar(result.scores.completeness, 5, 'Completeness')}
        {renderScoreBar(result.scores.answer_relevance, 5, 'Answer Relevance')}
        {renderScoreBar(Math.round(result.scores.context_precision * 10), 10, 'Context Precision')}
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.75rem', background: 'rgba(0,0,0,0.3)', borderRadius: '8px', marginBottom: '1rem' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>{result.scores.total}/30</div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>Total Score</div>
        </div>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)' }}>{result.context_chars.toLocaleString()}</div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>Context Chars</div>
        </div>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)' }}>{result.context.length}</div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>Chunks</div>
        </div>
      </div>

      {/* Grounding Visualization */}
      {renderGroundingVisualization(result)}

      {/* Reasoning */}
      <div style={{ marginTop: '1rem', padding: '0.75rem', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', fontSize: '0.85rem', color: 'var(--text-secondary)', fontStyle: 'italic' }}>
        {result.reasoning}
      </div>
    </div>
  );

  return (
    <div style={{ padding: '1.5rem' }}>
      {/* Header with Run button */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h2 style={{ color: 'var(--text-primary)', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Search size={20} /> Deep RAG Evaluation
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', margin: '0.25rem 0 0' }}>
            Compare Hierarchical RAG vs Simple RAG with detailed grounding analysis
          </p>
        </div>
        <button
          onClick={runDeepEvaluation}
          disabled={isLoading || !query}
          style={{
            background: 'linear-gradient(135deg, var(--accent-cyan), var(--accent-purple))',
            color: '#000',
            border: 'none',
            padding: '0.75rem 1.5rem',
            borderRadius: '8px',
            fontWeight: 600,
            cursor: isLoading || !query ? 'not-allowed' : 'pointer',
            opacity: isLoading || !query ? 0.5 : 1,
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}
        >
          {isLoading ? (
            <>
              <Activity className="animate-spin" size={16} /> Evaluating...
            </>
          ) : (
            <>
              <Trophy size={16} /> Compare RAG Approaches
            </>
          )}
        </button>
      </div>

      {/* Query display */}
      {query && (
        <div style={{ background: 'rgba(56, 189, 248, 0.05)', border: '1px solid rgba(56, 189, 248, 0.3)', borderRadius: '8px', padding: '1rem', marginBottom: '1.5rem' }}>
          <span style={{ color: 'var(--accent-cyan)', fontWeight: 600 }}>Query: </span>
          <span style={{ color: 'var(--text-primary)' }}>{query}</span>
        </div>
      )}

      {/* Error state */}
      {error && (
        <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '8px', padding: '1rem', color: '#ef4444', marginBottom: '1.5rem' }}>
          {error}
        </div>
      )}

      {/* Results */}
      {evaluation && (
        <>
          {/* Winner banner */}
          <div style={{
            background: 'linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(34, 211, 238, 0.1))',
            border: '1px solid var(--accent-green)',
            borderRadius: '12px',
            padding: '1.25rem',
            marginBottom: '1.5rem',
            textAlign: 'center'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <Trophy size={20} style={{ color: 'var(--accent-green)' }} />
              <span style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--accent-green)', textTransform: 'uppercase' }}>
                Winner: {evaluation.winner === 'hierarchical' ? 'Hierarchical RAG' : evaluation.winner === 'simple' ? 'Simple RAG' : 'Tie'}
              </span>
            </div>
            <p style={{ color: 'var(--text-secondary)', margin: 0, fontSize: '0.9rem' }}>{evaluation.winner_reasoning}</p>
            <div style={{ marginTop: '0.75rem', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              Evaluation completed in <span style={{ color: 'var(--accent-cyan)', fontWeight: 600 }}>{evaluation.eval_time_seconds.toFixed(1)}s</span>
            </div>
          </div>

          {/* Side by side comparison */}
          <div style={{ display: 'flex', gap: '1.5rem' }}>
            {renderRAGResult(evaluation.hierarchical, "Hierarchical RAG", evaluation.winner === 'hierarchical')}
            {renderRAGResult(evaluation.simple, "Simple RAG", evaluation.winner === 'simple')}
          </div>
        </>
      )}

      {/* Empty state */}
      {!evaluation && !isLoading && !error && (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-secondary)' }}>
          <Search size={48} style={{ opacity: 0.3, marginBottom: '1rem' }} />
          <p>Run a comparison to see detailed evaluation metrics</p>
          <p style={{ fontSize: '0.85rem' }}>Compares Hierarchical RAG (parent-child context) vs Simple RAG (flat chunks)</p>
        </div>
      )}
    </div>
  );
}

// Data Explorer Panel Component
interface ChunkData {
  chunk_id: string;
  document_name: string;
  page_number: number;
  entity_type: string;
  content: string;
  is_parent?: boolean;
  is_child?: boolean;
  parent_id?: string;
}

interface ExplorerStats {
  total_chunks: number;
  total_documents: number;
  parents: number;
  children: number;
  by_type: Record<string, number>;
}

const DataExplorerPanel: React.FC = () => {
  const [chunks, setChunks] = useState<ChunkData[]>([]);
  const [filteredChunks, setFilteredChunks] = useState<ChunkData[]>([]);
  const [stats, setStats] = useState<ExplorerStats | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [filterDocument, setFilterDocument] = useState<string>('all');
  const [filterType, setFilterType] = useState<string>('all');
  const [filterChunkType, setFilterChunkType] = useState<string>('all'); // all, parents, children
  const [searchText, setSearchText] = useState<string>('');
  const [expandedChunks, setExpandedChunks] = useState<Set<string>>(new Set());

  // Pagination
  const [page, setPage] = useState(0);
  const pageSize = 50;

  const loadData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/explorer/chunks');
      if (!response.ok) throw new Error('Failed to load chunks');

      const data = await response.json();
      setChunks(data.chunks || []);
      setStats(data.stats || null);
      setFilteredChunks(data.chunks || []);
    } catch (e) {
      setError(`Failed to load data: ${e}`);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Apply filters
  useEffect(() => {
    let filtered = [...chunks];

    // Document filter
    if (filterDocument !== 'all') {
      filtered = filtered.filter(c => c.document_name === filterDocument);
    }

    // Entity type filter
    if (filterType !== 'all') {
      filtered = filtered.filter(c => c.entity_type.toLowerCase() === filterType.toLowerCase());
    }

    // Chunk type filter (parent/child)
    if (filterChunkType === 'parents') {
      filtered = filtered.filter(c => !c.chunk_id.includes('_c'));
    } else if (filterChunkType === 'children') {
      filtered = filtered.filter(c => c.chunk_id.includes('_c'));
    }

    // Text search
    if (searchText.trim()) {
      const search = searchText.toLowerCase();
      filtered = filtered.filter(c =>
        c.content.toLowerCase().includes(search) ||
        c.chunk_id.toLowerCase().includes(search) ||
        c.entity_type.toLowerCase().includes(search)
      );
    }

    setFilteredChunks(filtered);
    setPage(0);
  }, [chunks, filterDocument, filterType, filterChunkType, searchText]);

  const uniqueDocuments = [...new Set(chunks.map(c => c.document_name))];
  const uniqueTypes = [...new Set(chunks.map(c => c.entity_type))];

  const paginatedChunks = filteredChunks.slice(page * pageSize, (page + 1) * pageSize);
  const totalPages = Math.ceil(filteredChunks.length / pageSize);

  const toggleExpand = (chunkId: string) => {
    const newExpanded = new Set(expandedChunks);
    if (newExpanded.has(chunkId)) {
      newExpanded.delete(chunkId);
    } else {
      newExpanded.add(chunkId);
    }
    setExpandedChunks(newExpanded);
  };

  const isParent = (chunkId: string) => !chunkId.includes('_c');
  const isChild = (chunkId: string) => chunkId.includes('_c');

  const exportToJSON = () => {
    const dataStr = JSON.stringify(filteredChunks, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'rag_chunks_export.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div style={{ padding: '1.5rem', height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h2 style={{ color: 'var(--text-primary)', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Table size={20} /> RAG Data Explorer
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', margin: '0.25rem 0 0' }}>
            Browse and query all chunks in your vector index
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            onClick={loadData}
            disabled={isLoading}
            style={{
              background: 'rgba(255,255,255,0.1)',
              color: 'var(--text-primary)',
              border: '1px solid rgba(255,255,255,0.2)',
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
          >
            <Activity size={14} className={isLoading ? 'animate-spin' : ''} /> Refresh
          </button>
          <button
            onClick={exportToJSON}
            disabled={filteredChunks.length === 0}
            style={{
              background: 'var(--accent-cyan)',
              color: '#000',
              border: 'none',
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              fontWeight: 600
            }}
          >
            <Download size={14} /> Export JSON
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
          <div style={{ background: 'rgba(34, 211, 238, 0.1)', border: '1px solid rgba(34, 211, 238, 0.3)', borderRadius: '8px', padding: '1rem', textAlign: 'center' }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>{stats.total_chunks}</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Total Chunks</div>
          </div>
          <div style={{ background: 'rgba(139, 92, 246, 0.1)', border: '1px solid rgba(139, 92, 246, 0.3)', borderRadius: '8px', padding: '1rem', textAlign: 'center' }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--accent-purple)' }}>{stats.total_documents}</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Documents</div>
          </div>
          <div style={{ background: 'rgba(34, 197, 94, 0.1)', border: '1px solid rgba(34, 197, 94, 0.3)', borderRadius: '8px', padding: '1rem', textAlign: 'center' }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--accent-green)' }}>{stats.parents}</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Parent Chunks</div>
          </div>
          <div style={{ background: 'rgba(251, 146, 60, 0.1)', border: '1px solid rgba(251, 146, 60, 0.3)', borderRadius: '8px', padding: '1rem', textAlign: 'center' }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--accent-orange)' }}>{stats.children}</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Child Chunks</div>
          </div>
          <div style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', padding: '1rem', textAlign: 'center' }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)' }}>{Object.keys(stats.by_type).length}</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Entity Types</div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Filter size={14} style={{ color: 'var(--text-secondary)' }} />
          <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Filters:</span>
        </div>

        <select
          value={filterDocument}
          onChange={(e) => setFilterDocument(e.target.value)}
          style={{ background: 'rgba(255,255,255,0.05)', color: 'var(--text-primary)', border: '1px solid rgba(255,255,255,0.1)', padding: '0.5rem', borderRadius: '6px', fontSize: '0.85rem' }}
        >
          <option value="all">All Documents</option>
          {uniqueDocuments.map(doc => (
            <option key={doc} value={doc}>{doc}</option>
          ))}
        </select>

        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          style={{ background: 'rgba(255,255,255,0.05)', color: 'var(--text-primary)', border: '1px solid rgba(255,255,255,0.1)', padding: '0.5rem', borderRadius: '6px', fontSize: '0.85rem' }}
        >
          <option value="all">All Entity Types</option>
          {uniqueTypes.map(type => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>

        <select
          value={filterChunkType}
          onChange={(e) => setFilterChunkType(e.target.value)}
          style={{ background: 'rgba(255,255,255,0.05)', color: 'var(--text-primary)', border: '1px solid rgba(255,255,255,0.1)', padding: '0.5rem', borderRadius: '6px', fontSize: '0.85rem' }}
        >
          <option value="all">All Chunks</option>
          <option value="parents">Parents Only (Large)</option>
          <option value="children">Children Only (Small)</option>
        </select>

        <input
          type="text"
          placeholder="Search content..."
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          style={{ background: 'rgba(255,255,255,0.05)', color: 'var(--text-primary)', border: '1px solid rgba(255,255,255,0.1)', padding: '0.5rem 1rem', borderRadius: '6px', fontSize: '0.85rem', flex: 1, minWidth: '200px' }}
        />

        <span style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
          Showing {filteredChunks.length} of {chunks.length} chunks
        </span>
      </div>

      {/* Error state */}
      {error && (
        <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '8px', padding: '1rem', color: '#ef4444', marginBottom: '1rem' }}>
          {error}
        </div>
      )}

      {/* Chunks Table */}
      <div style={{ flex: 1, overflow: 'auto', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
          <thead style={{ position: 'sticky', top: 0, background: 'rgba(15, 23, 42, 0.95)', zIndex: 10 }}>
            <tr>
              <th style={{ padding: '0.75rem', textAlign: 'left', borderBottom: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-secondary)', fontWeight: 600 }}>Chunk ID</th>
              <th style={{ padding: '0.75rem', textAlign: 'left', borderBottom: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-secondary)', fontWeight: 600 }}>Type</th>
              <th style={{ padding: '0.75rem', textAlign: 'left', borderBottom: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-secondary)', fontWeight: 600 }}>Document</th>
              <th style={{ padding: '0.75rem', textAlign: 'center', borderBottom: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-secondary)', fontWeight: 600 }}>Page</th>
              <th style={{ padding: '0.75rem', textAlign: 'center', borderBottom: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-secondary)', fontWeight: 600 }}>Size</th>
              <th style={{ padding: '0.75rem', textAlign: 'left', borderBottom: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-secondary)', fontWeight: 600 }}>Content Preview</th>
            </tr>
          </thead>
          <tbody>
            {paginatedChunks.map((chunk) => {
              const isExpanded = expandedChunks.has(chunk.chunk_id);
              const chunkIsParent = isParent(chunk.chunk_id);

              return (
                <tr
                  key={chunk.chunk_id}
                  onClick={() => toggleExpand(chunk.chunk_id)}
                  style={{
                    cursor: 'pointer',
                    background: isExpanded ? 'rgba(34, 211, 238, 0.05)' : 'transparent',
                    borderLeft: chunkIsParent ? '3px solid var(--accent-green)' : '3px solid var(--accent-orange)'
                  }}
                >
                  <td style={{ padding: '0.75rem', borderBottom: '1px solid rgba(255,255,255,0.05)', fontFamily: 'monospace', fontSize: '0.75rem', color: 'var(--accent-cyan)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                      {chunk.chunk_id}
                    </div>
                  </td>
                  <td style={{ padding: '0.75rem', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <span style={{
                        padding: '2px 8px',
                        borderRadius: '4px',
                        fontSize: '0.7rem',
                        fontWeight: 600,
                        background: chunkIsParent ? 'rgba(34, 197, 94, 0.2)' : 'rgba(251, 146, 60, 0.2)',
                        color: chunkIsParent ? 'var(--accent-green)' : 'var(--accent-orange)'
                      }}>
                        {chunkIsParent ? 'PARENT' : 'CHILD'}
                      </span>
                      <span style={{
                        padding: '2px 8px',
                        borderRadius: '4px',
                        fontSize: '0.7rem',
                        background: 'rgba(139, 92, 246, 0.2)',
                        color: 'var(--accent-purple)'
                      }}>
                        {chunk.entity_type}
                      </span>
                    </div>
                  </td>
                  <td style={{ padding: '0.75rem', borderBottom: '1px solid rgba(255,255,255,0.05)', color: 'var(--text-primary)', fontSize: '0.8rem' }}>
                    {chunk.document_name}
                  </td>
                  <td style={{ padding: '0.75rem', borderBottom: '1px solid rgba(255,255,255,0.05)', textAlign: 'center', color: 'var(--text-primary)' }}>
                    {chunk.page_number}
                  </td>
                  <td style={{ padding: '0.75rem', borderBottom: '1px solid rgba(255,255,255,0.05)', textAlign: 'center', color: 'var(--text-secondary)', fontSize: '0.75rem' }}>
                    {chunk.content.length} chars
                  </td>
                  <td style={{ padding: '0.75rem', borderBottom: '1px solid rgba(255,255,255,0.05)', color: 'var(--text-secondary)', maxWidth: '400px' }}>
                    {isExpanded ? (
                      <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.6, color: 'var(--text-primary)', background: 'rgba(0,0,0,0.3)', padding: '1rem', borderRadius: '6px', marginTop: '0.5rem' }}>
                        {chunk.content}
                      </div>
                    ) : (
                      <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {chunk.content.substring(0, 150)}...
                      </div>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {paginatedChunks.length === 0 && !isLoading && (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-secondary)' }}>
            <Database size={48} style={{ opacity: 0.3, marginBottom: '1rem' }} />
            <p>No chunks found matching your filters</p>
          </div>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '1rem', marginTop: '1rem' }}>
          <button
            onClick={() => setPage(p => Math.max(0, p - 1))}
            disabled={page === 0}
            style={{ background: 'rgba(255,255,255,0.1)', color: 'var(--text-primary)', border: 'none', padding: '0.5rem 1rem', borderRadius: '6px', cursor: page === 0 ? 'not-allowed' : 'pointer', opacity: page === 0 ? 0.5 : 1 }}
          >
            Previous
          </button>
          <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
            Page {page + 1} of {totalPages}
          </span>
          <button
            onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
            disabled={page >= totalPages - 1}
            style={{ background: 'rgba(255,255,255,0.1)', color: 'var(--text-primary)', border: 'none', padding: '0.5rem 1rem', borderRadius: '6px', cursor: page >= totalPages - 1 ? 'not-allowed' : 'pointer', opacity: page >= totalPages - 1 ? 0.5 : 1 }}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
