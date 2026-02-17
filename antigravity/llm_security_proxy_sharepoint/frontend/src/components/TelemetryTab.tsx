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
  try {
    const parsed = JSON.parse(step);
    return (
      <pre className="json-pretty">
        {JSON.stringify(parsed, null, 2)}
      </pre>
    );
  } catch (e) {
    return <p>{step}</p>;
  }
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
              const generalSteps = reasoningSteps.filter(step => !step.startsWith('[Public Web]') && !step.startsWith('[Enterprise Proxy]'));

              return (
                <div className="workflows-container">
                  {enterpriseSteps.length > 0 && (
                    <div className="reasoning-workflow-section">
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
                      {enterpriseSteps.length > 0 && <div className="workflow-divider" />}
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

                  {generalSteps.length > 0 && (
                    <div className="reasoning-workflow-section">
                      {(enterpriseSteps.length > 0 || publicSteps.length > 0) && <div className="workflow-divider" />}
                      <h4 className="workflow-title general-title">⚙️ Main Execution Trace</h4>
                      <div className="reasoning-list">
                        {generalSteps.map((step, idx) => (
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
