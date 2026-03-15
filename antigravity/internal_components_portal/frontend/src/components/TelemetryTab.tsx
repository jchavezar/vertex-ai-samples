import React from 'react';
import { Activity } from 'lucide-react';
import type { TelemetryEvent, TokenUsage } from '../hooks/useTerminalChat';
import './TelemetryTab.css';

interface TelemetryTabProps {
  telemetry: TelemetryEvent[];
  reasoningSteps: string[];
  tokenUsage: TokenUsage | null;
}

const renderStepContent = (step: string) => {
  // Enhanced regex to handle headers like [Router], [Discovery Engine], [Action]
  const headerMatch = step.match(/^\[(Router|Discovery Engine|Action|Action Setup)\]\s*(.*)/is);
  let header = "";
  let body = step;

  if (headerMatch) {
    header = headerMatch[1];
    body = headerMatch[2];
  }

  // Check for internal labels like INTENT:, TOOL:, ARGS:, RESPONSE:, RESULT:
  // Also tolerate optional bracketed states like THOUGHT [IN_PROGRESS]:
  const labelMatch = body.match(/^(INTENT|TOOL|TOOL CALL|TOOL RESPONSE|API EVIDENCE|ARGS|RESPONSE|RESULT|SYNTHESIS|THOUGHT|ANALYSIS|STEP|DATASOURCE)(?:\s*\[[^\]]+\])?:\s*(.*)/is);
  
  if (labelMatch) {
    const label = labelMatch[1] ? labelMatch[1].toUpperCase() : "UNKNOWN";
    const labelClass = labelMatch[1] ? labelMatch[1].toLowerCase().replace(' ', '-') : "unknown";
    const content = labelMatch[2] ? labelMatch[2].trim() : "";
    let parsedContent;
    
    // Try to parse as JSON if it looks like one
    if (content.startsWith('{') || content.startsWith('[')) {
      try {
        parsedContent = JSON.parse(content);
        return (
          <div className="trace-step">
            {header && <div className="trace-header-tag">{header}</div>}
            <span className={`trace-label label-${labelClass}`}>{label}</span>
            <pre className="json-pretty">{JSON.stringify(parsedContent, null, 2)}</pre>
          </div>
        );
      } catch {
        // Fallback to text if JSON parse fails
      }
    }

    return (
      <div className="trace-step">
        {header && <div className="trace-header-tag">{header}</div>}
        <span className={`trace-label label-${labelClass}`}>{label}</span>
        <p style={{ whiteSpace: 'pre-wrap' }}>{content}</p>
      </div>
    );
  }

  // Default rendering for unknown formats
  return (
    <div className="trace-step">
      {header && <div className="trace-header-tag">{header}</div>}
      <p style={{ whiteSpace: 'pre-wrap' }}>{body}</p>
    </div>
  );
};

export const TelemetryTab: React.FC<TelemetryTabProps> = ({ telemetry, reasoningSteps, tokenUsage }) => {
  if (!telemetry || telemetry.length === 0) {
    return (
      <div className="telemetry-empty-state">
        <Activity size={48} color="#ccc" />
        <h2>No Telemetry Data Available</h2>
        <p>Run a query in the Secure Enterprise Proxy to generate an execution latency profile.</p>
      </div>
    );
  }

  const totalTime = telemetry.find((t) => t.step.includes('Total'))?.duration_s || 0;

  return (
    <div className="telemetry-wrapper">
      <div className="telemetry-header">
        <Activity size={28} className="telemetry-icon" />
        <h2>Execution Latency Profile</h2>
      </div>

      <div className="telemetry-board">
        <div className="telemetry-summary">
          <div className="summary-stat">
            <span className="stat-label">Total Turnaround</span>
            <span className="stat-value">{totalTime}s</span>
          </div>
          <div className="summary-stat">
            <span className="stat-label">Steps Logged</span>
            <span className="stat-value">{telemetry.length - 1}</span>
          </div>
          {tokenUsage && (
            <div className="summary-stat">
              <span className="stat-label">Total Tokens (I/O)</span>
              <span className="stat-value">{tokenUsage.total.toLocaleString()}</span>
            </div>
          )}
        </div>

        <div className="telemetry-body-grid">
          <div className="telemetry-timeline">
            <h3>Latency Timeline</h3>
            {telemetry.map((event, idx) => {
              if (event.step.includes('Total')) return null;

              const percentage = totalTime > 0 ? (event.duration_s / totalTime) * 100 : 0;

              return (
                <div key={idx} className="timeline-event">
                  <div className="timeline-info">
                    <span className="event-name">{event.step}</span>
                    <span className="event-time">{event.duration_s}s</span>
                  </div>
                  <div className="timeline-bar-bg">
                    <div
                      className="timeline-bar-fill"
                      style={{
                        width: `${Math.max(percentage, 1)}%`,
                      }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="telemetry-reasoning">
            <h3>Agent Reasoning Trace</h3>
            {(() => {
              if (reasoningSteps.length === 0) {
                return <p className="no-reasoning-text">No intermediate reasoning steps captured for this request.</p>;
              }

              const publicSteps = reasoningSteps.filter(step => step.startsWith('[Public Web]'));
              const enterpriseSteps = reasoningSteps.filter(step => step.startsWith('[Enterprise Proxy]'));
              const routerSteps = reasoningSteps.filter(step => step.startsWith('[Router]'));
              const geSteps = reasoningSteps.filter(step => step.startsWith('[Discovery Engine]'));
              const actionSteps = reasoningSteps.filter(step => step.startsWith('[Action]'));
              const redactionSteps = reasoningSteps.filter(step => step.startsWith('[Redaction]'));
              
              const otherSteps = reasoningSteps.filter(step => 
                !step.startsWith('[Public Web]') && 
                !step.startsWith('[Enterprise Proxy]') &&
                !step.startsWith('[Router]') &&
                !step.startsWith('[Discovery Engine]') &&
                !step.startsWith('[Action]') &&
                !step.startsWith('[Redaction]')
              );

              return (
                <div className="workflows-container">
                  {routerSteps.length > 0 && (
                    <div className="reasoning-workflow-section">
                      <h4 className="workflow-title router-title">🔀 Intent Router Analysis</h4>
                      <div className="reasoning-list">
                        {routerSteps.map((step, idx) => (
                          <div key={`router-${idx}`} className="reasoning-item router-item">
                            <div className="reasoning-indicator router-indicator"></div>
                            <div className="reasoning-content">{renderStepContent(step)}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {geSteps.length > 0 && (
                    <div className="reasoning-workflow-section">
                      <div className="workflow-divider" />
                      <h4 className="workflow-title ge-title">🔍 Discovery Engine (GE) Execution</h4>
                      <div className="reasoning-list">
                        {geSteps.map((step, idx) => (
                          <div key={`ge-${idx}`} className="reasoning-item ge-item">
                            <div className="reasoning-indicator ge-indicator"></div>
                            <div className="reasoning-content">{renderStepContent(step)}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {actionSteps.length > 0 && (
                    <div className="reasoning-workflow-section">
                      <div className="workflow-divider" />
                      <h4 className="workflow-title action-title">⚡ MCP Tool Orchestration</h4>
                      <div className="reasoning-list">
                        {actionSteps.map((step, idx) => (
                          <div key={`action-${idx}`} className="reasoning-item action-item">
                            <div className="reasoning-indicator action-indicator"></div>
                            <div className="reasoning-content">{renderStepContent(step)}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {redactionSteps.length > 0 && (
                    <div className="reasoning-workflow-section">
                      <div className="workflow-divider" />
                      <h4 className="workflow-title enterprise-title" style={{ color: '#00D1FF' }}>🛡️ Zero-Leak Shield (Redaction)</h4>
                      <div className="reasoning-list">
                        {redactionSteps.map((step, idx) => (
                          <div key={`redact-${idx}`} className="reasoning-item enterprise-item">
                            <div className="reasoning-indicator enterprise-indicator" style={{ background: '#00D1FF' }}></div>
                            <div className="reasoning-content">{renderStepContent(step)}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {enterpriseSteps.length > 0 && (
                    <div className="reasoning-workflow-section">
                      <div className="workflow-divider" />
                      <h4 className="workflow-title enterprise-title">🛡️ Secure Enterprise Proxy Workflow</h4>
                      <div className="reasoning-list">
                        {enterpriseSteps.map((step, idx) => (
                          <div key={`ent-${idx}`} className="reasoning-item enterprise-item">
                            <div className="reasoning-indicator enterprise-indicator"></div>
                            <div className="reasoning-content">
                              {renderStepContent(step.replace('[Enterprise Proxy] ', ''))}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {publicSteps.length > 0 && (
                    <div className="reasoning-workflow-section">
                      <div className="workflow-divider" />
                      <h4 className="workflow-title public-title">🌐 Public Web Intelligence Workflow</h4>
                      <div className="reasoning-list">
                        {publicSteps.map((step, idx) => (
                          <div key={`pub-${idx}`} className="reasoning-item public-item">
                            <div className="reasoning-indicator public-indicator"></div>
                            <div className="reasoning-content">
                              {renderStepContent(step.replace('[Public Web] ', ''))}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {otherSteps.length > 0 && (
                    <div className="reasoning-workflow-section">
                      <div className="workflow-divider" />
                      <h4 className="workflow-title general-title">⚙️ Main Execution Trace</h4>
                      <div className="reasoning-list">
                        {otherSteps.map((step, idx) => (
                          <div key={`gen-${idx}`} className="reasoning-item">
                            <div className="reasoning-indicator"></div>
                            <div className="reasoning-content">
                              {renderStepContent(step)}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              );
            })()}
          </div>
        </div>
      </div>
    </div>
  );
};
