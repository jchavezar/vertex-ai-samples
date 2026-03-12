import React, { useEffect } from 'react';
import * as Tabs from '@radix-ui/react-tabs';
import { Database, Image as ImageIcon, Activity } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { IndexedDocuments } from './IndexedDocuments';

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
            <Database size={16} /> Retrieval Logs
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
      </Tabs.Root>
    </div>
  );
};
