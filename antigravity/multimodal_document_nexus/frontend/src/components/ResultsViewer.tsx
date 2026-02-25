import React from 'react';
import * as Tabs from '@radix-ui/react-tabs';
import { Database, Image as ImageIcon, Activity } from 'lucide-react';

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
  activeHighlight: string | null;
  onHighlightClick: (chunkId: string) => void;
  activeTab: string;
  onTabChange: (value: string) => void;
}

export const ResultsViewer: React.FC<ResultsViewerProps> = ({
  data, annotatedImages, traces, activeHighlight, onHighlightClick, activeTab, onTabChange
}) => {
  if (!data || data.length === 0) return null;

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
        </Tabs.List>

        <Tabs.Content className="tabs-content" value="bigquery">
          <div className="bq-table-container">
            <table className="bq-table">
              <thead>
                <tr>
                  <th>Chunk ID</th>
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
                // Find all chunks associated with this page
                const pageChunks = data.filter(d => d.page_number === idx + 1);

                return (
                  <div key={idx} className="bb-image-wrapper" style={{ position: 'relative' }}>
                    <img src={imgSrc} alt={`Annotated Page ${idx + 1}`} loading="lazy" style={{ display: 'block', width: '100%', height: 'auto' }} />

                    {/* Render Highlight Overlays */}
                    {pageChunks.map(chunk => {
                      // Ensure the chunk has box_2d data extending off the PipelineEntity
                      // Default bounding box logic uses (ymin, xmin, ymax, xmax) 0-1000 normalized.
                      // For this dynamic UI, we'd theoretically need box_2d exposed in PipelineEntity. 
                      // Assuming the backend has been updated to pass `box_2d` in `pipeline_data`.
                      const bb = (chunk as any).box_2d;
                      if (!bb || bb.length !== 4) return null;

                      const [ymin, xmin, ymax, xmax] = bb;
                      const top = `${ymin / 10}%`;
                      const left = `${xmin / 10}%`;
                      const height = `${(ymax - ymin) / 10}%`;
                      const width = `${(xmax - xmin) / 10}%`;

                      const isHighlighted = activeHighlight === chunk.chunk_id;

                      return (
                        <div
                          key={chunk.chunk_id}
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
            <div className="placeholder-tab">
              <ImageIcon size={48} className="text-accent-cyan" style={{ opacity: 0.5, marginBottom: '1rem' }} />
              <h3>Visual Document Viewer</h3>
              <p className="text-text-secondary">Render bounding boxes and interactive highlights on the document pages.</p>
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
      </Tabs.Root>
    </div>
  );
};
