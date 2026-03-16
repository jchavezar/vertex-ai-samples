import React from 'react';
import { Activity, Brain, Wrench, Zap, Search, FileText, ChevronRight } from 'lucide-react';
import type { TelemetryEvent, TokenUsage } from '../hooks/useTerminalChat';
import './TelemetryTab.css';

interface TelemetryTabProps {
  telemetry: TelemetryEvent[];
  reasoningSteps: string[];
  tokenUsage: TokenUsage | null;
}

const renderStepContent = (step: string) => {
  // Clean up the bracketed prefixes like [Enterprise Proxy] since they are redundant in the hierarchical view
  const cleanStep = step.replace(/^\[(Router|Discovery Engine|Action|Action Setup|Enterprise Proxy|Public Web|Redaction)\]\s*/i, '');
  
  // Unified label set for vibrant color-coding
  const labelRegex = /^(INTENT|TOOL|TOOL CALL|TOOL RESPONSE|API EVIDENCE|ARGS|RESPONSE|RESULT|SYNTHESIS|THOUGHT|ANALYSIS|STEP|DATASOURCE|EVALUATION)/i;
  const labelMatch = cleanStep.match(labelRegex);
  
  if (labelMatch) {
    const label = labelMatch[1].toUpperCase();
    const content = cleanStep.replace(labelRegex, '').replace(/^[:\s\-\]\[]+/, '').trim();

    // Choose icon based on label
    let Icon = Activity;
    if (label.includes('THOUGHT') || label.includes('ANALYSIS') || label.includes('SYNTHESIS')) Icon = Brain;
    if (label.includes('TOOL')) Icon = Wrench;
    if (label.includes('INTENT')) Icon = Zap;
    if (label.includes('EVIDENCE') || label.includes('DATASOURCE')) Icon = Search;
    if (label.includes('RESPONSE') || label.includes('RESULT') || label.includes('STEP')) Icon = FileText;
    
    // Dynamically assign a CSS class based on the label for color-coding
    const labelClass = label.toLowerCase().replace(' ', '-'); // e.g., 'tool-call', 'thought'

    let parsedContent;
    if (content.startsWith('{') || content.startsWith('[')) {
      try {
        parsedContent = JSON.parse(content);
        return (
          <div className={`trace-step-card card-label-${labelClass}`}> {/* New class for CSS targeting */}
            <div className="step-card-header">
              <Icon size={14} className={`step-icon icon-label-${labelClass}`} /> {/* New class for CSS targeting */}
              <span className={`trace-label-compact label-${labelClass}`}>{label}</span>
            </div>
            <pre className="json-pretty-compact">{JSON.stringify(parsedContent, null, 2)}</pre>
          </div>
        );
      } catch { /* Fallback */ }
    }

    return (
      <div className={`trace-step-card card-label-${labelClass}`}> {/* New class for CSS targeting */}
        <div className="step-card-header">
          <Icon size={14} className={`step-icon icon-label-${labelClass}`} /> {/* New class for CSS targeting */}
          <span className={`trace-label-compact label-${labelClass}`}>{label}</span>
        </div>
        <p className="step-card-text">{content}</p>
      </div>
    );
  }

  // Default rendering for steps without a specific label
  return (
    <div className="trace-step-card card-label-general"> {/* New class for general steps */}
      <div className="step-card-header">
        <ChevronRight size={14} className="step-icon" />
      </div>
      <p className="step-card-text">{cleanStep}</p>
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
        <div className="telemetry-summary" id="telemetry-summary">
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

        <div className="telemetry-main-layout">
          <div className="telemetry-index-sidebar">
            <div className="index-title">Step Index</div>
            <div className="index-list">
              <a href="#telemetry-summary" className="index-item summary-index-item">
                <span className="index-name">Detailed Summary</span>
                <span className="index-latency">{totalTime}s</span>
              </a>
              {telemetry.map((event, idx) => {
                if (event.step.includes('Total')) return null;
                return (
                  <a key={idx} href={`#phase-${idx}`} className="index-item">
                    <span className="index-name">{event.step.replace(/^\[.*?\]\s*/, '')}</span>
                    <span className="index-latency">{event.duration_s}s</span>
                  </a>
                );
              })}
            </div>
          </div>

          <div className="telemetry-consolidated-view">
            <div className="consolidated-column">
            <h3>Unified Execution Trace</h3>
            {(() => {
              const totalTime = telemetry.find((t) => t.step.includes('Total'))?.duration_s || 1;
              
              return telemetry.map((event, idx) => {
                if (event.step.includes('Total')) return null;

                const percentage = (event.duration_s / totalTime) * 100;
                
                // Determine which reasoning steps belong to this latency phase
                let relevantSteps: string[] = [];
                const stepLower = event.step.toLowerCase();
                
                if (stepLower.includes('system-atomic') || stepLower.includes('handshake') || stepLower.includes('intent')) {
                  relevantSteps = reasoningSteps.filter(s => s.startsWith('[Router]'));
                } else if (stepLower.includes('enterprise-atomic')) {
                  relevantSteps = reasoningSteps.filter(s => 
                    s.startsWith('[Enterprise Proxy]') || 
                    s.startsWith('[Discovery Engine]') || 
                    s.startsWith('[Action]') ||
                    s.startsWith('[Redaction]')
                  );
                } else if (stepLower.includes('public-atomic')) {
                  relevantSteps = reasoningSteps.filter(s => s.startsWith('[Public Web]'));
                }

                return (
                  <div key={idx} id={`phase-${idx}`} className="consolidated-phase">
                    <div className="phase-header">
                      <div className="phase-info">
                        <span className="phase-name">{event.step}</span>
                        <span className="phase-duration">{event.duration_s}s</span>
                      </div>
                      <div className="phase-progress-container">
                        <div 
                          className="phase-progress-fill" 
                          style={{ width: `${Math.max(percentage, 2)}%` }}
                        />
                      </div>
                    </div>
                    
                    {relevantSteps.length > 0 && (
                      <div className="phase-subtasks">
                        {relevantSteps.map((step, sIdx) => (
                          <div key={sIdx} className="subtask-item">
                            {renderStepContent(step)}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                );
              });
            })()}
            
            {/* Catch-all for any reasoning steps that weren't captured by the categorizer */}
            {(() => {
              const usedPrefixes = ['[Router]', '[Enterprise Proxy]', '[Discovery Engine]', '[Action]', '[Redaction]', '[Public Web]'];
              const orphanSteps = reasoningSteps.filter(step => 
                !usedPrefixes.some(p => step.startsWith(p))
              );

              if (orphanSteps.length > 0) {
                return (
                  <div className="consolidated-phase orphan-phase">
                    <div className="phase-header">
                      <div className="phase-info">
                        <span className="phase-name">Additional Execution Context</span>
                      </div>
                    </div>
                    <div className="phase-subtasks">
                      {orphanSteps.map((step, idx) => (
                        <div key={idx} className="subtask-item">
                          {renderStepContent(step)}
                        </div>
                      ))}
                    </div>
                  </div>
                );
              }
              return null;
            })()}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};
