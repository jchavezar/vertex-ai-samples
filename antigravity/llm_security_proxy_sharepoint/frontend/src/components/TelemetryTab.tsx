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
            {reasoningSteps.length === 0 ? (
              <p className="no-reasoning-text">No intermediate reasoning steps captured for this request.</p>
            ) : (
              <div className="reasoning-list">
                {reasoningSteps.map((step, idx) => (
                  <div key={idx} className="reasoning-item">
                    <div className="reasoning-indicator"></div>
                    <div className="reasoning-content">
                      {renderStepContent(step)}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
