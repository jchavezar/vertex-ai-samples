import React, { useState } from 'react';
import { Activity, Brain, Wrench, Zap, Search, FileText, ChevronRight, Settings2, Trash2, BarChart2, Loader2 } from 'lucide-react';
import type { TelemetryEvent, TokenUsage, TelemetrySession } from '../hooks/useTerminalChat';
import { MarkdownRenderer } from './MarkdownRenderer';
import './TelemetryTab.css';

interface TelemetryTabProps {
  telemetry: TelemetryEvent[];
  reasoningSteps: string[];
  tokenUsage: TokenUsage | null;
  telemetryHistory: TelemetrySession[];
  setTelemetryHistory: React.Dispatch<React.SetStateAction<TelemetrySession[]>>;
  currentQuery: string;
  selectedModel: string;
  routerMode: string;
}

const renderStepContent = (step: string) => {
  // Clean up the bracketed prefixes like [Enterprise Proxy] since they are redundant in the hierarchical view
  const cleanStep = step.replace(/^\[(Router|Discovery Engine|Action|Action Setup|Enterprise Proxy|Public Web|Redaction|SYSTEM).*?\]\s*/i, '');
  
  // Unified label set for vibrant color-coding
  const labelRegex = /^(INTENT|TOOL|TOOL CALL|TOOL RESPONSE|API EVIDENCE|ARGS|RESPONSE|RESULT|SYNTHESIS|THOUGHT|ANALYSIS|STEP|DATASOURCE|EVALUATION|OPTIMIZATION)/i;
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
    if (label.includes('OPTIMIZATION')) Icon = Settings2;
    
    // Dynamically assign a CSS class based on the label for color-coding
    const labelClass = label.toLowerCase().replace(' ', '-'); // e.g., 'tool-call', 'thought'

    let parsedContent;
    if (content.startsWith('{') || content.startsWith('[')) {
      try {
        parsedContent = JSON.parse(content);
        return (
          <div className={`trace-step-card card-label-${labelClass}`}>
            <div className="step-card-header">
              <Icon size={14} className={`step-icon icon-label-${labelClass}`} />
              <span className={`trace-label-compact label-${labelClass}`}>{label}</span>
            </div>
            <pre className="json-pretty-compact">{JSON.stringify(parsedContent, null, 2)}</pre>
          </div>
        );
      } catch { /* Fallback */ }
    }

    return (
      <div className={`trace-step-card card-label-${labelClass}`}>
        <div className="step-card-header">
          <Icon size={14} className={`step-icon icon-label-${labelClass}`} />
          <span className={`trace-label-compact label-${labelClass}`}>{label}</span>
        </div>
        <p className="step-card-text">{content}</p>
      </div>
    );
  }

  // Default rendering for steps without a specific label
  return (
    <div className="trace-step-card card-label-general">
      <div className="step-card-header">
        <ChevronRight size={14} className="step-icon" />
      </div>
      <p className="step-card-text">{cleanStep}</p>
    </div>
  );
};

export const TelemetryTab: React.FC<TelemetryTabProps> = ({ 
  telemetry, 
  reasoningSteps, 
  tokenUsage,
  telemetryHistory,
  setTelemetryHistory,
  currentQuery,
  selectedModel,
  routerMode
}) => {

  const [selectedSessionId, setSelectedSessionId] = useState<string>('current');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<string | null>(null);

  const currentSession: TelemetrySession = {
    id: 'current',
    timestamp: new Date().toISOString(),
    query: currentQuery || 'Active Query',
    model: selectedModel,
    mode: routerMode,
    telemetry: telemetry,
    reasoningSteps: reasoningSteps,
    tokenUsage: tokenUsage ? { ...tokenUsage } : null
  };

  const allSessions = [...telemetryHistory, currentSession].filter(s => s.telemetry.length > 0);

  const handleClearHistory = () => {
    setTelemetryHistory([]);
    setSelectedSessionId('current');
    setAnalysisResult(null);
  };

  const handleAnalyze = async () => {
    if (allSessions.length === 0) return;
    
    setIsAnalyzing(true);
    setAnalysisResult(null);
    setSelectedSessionId('analysis'); // Special virtual ID to show analysis

    try {
      const token = localStorage.getItem('access_token');
      const apiEndpoint = import.meta.env.VITE_BACKEND_URL || (typeof window !== 'undefined' && window.location.hostname !== 'localhost' ? '' : 'http://localhost:8008');
      const response = await fetch(`${apiEndpoint}/api/latency/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ history: allSessions })
      });

      if (!response.ok) {
        throw new Error(`Failed to analyze latency: ${response.statusText}`);
      }

      const data = await response.json();
      setAnalysisResult(data.analysis);
    } catch (err) {
      console.error("Error analyzing latency:", err);
      setAnalysisResult(`**Error**: Failed to generate analysis report. ${err instanceof Error ? err.message : ''}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  if (allSessions.length === 0) {
    return (
      <div className="telemetry-empty-state">
        <Activity size={48} color="#ccc" />
        <h2>No Telemetry Data Available</h2>
        <p>Run a query in the Secure Enterprise Proxy to generate an execution latency profile.</p>
      </div>
    );
  }

  // Determine active view payload
  const activeSession = selectedSessionId === 'analysis' 
    ? null 
    : allSessions.find(s => s.id === selectedSessionId) || currentSession;

  const totalTime = activeSession ? (activeSession.telemetry.find((t) => t.step.includes('Total'))?.duration_s || 0) : 0;

  return (
    <div className="telemetry-wrapper telemetry-with-sidebar">
      
      {/* Sidebar for History Navigation */}
      <div className="telemetry-history-sidebar">
        <div className="history-sidebar-header">
          <Activity size={20} className="telemetry-icon" />
          <h3>Sessions</h3>
        </div>
        
        <div className="history-list">
          {telemetryHistory.map(session => (
            <div 
              key={session.id} 
              className={`history-item ${selectedSessionId === session.id ? 'active' : ''}`}
              onClick={() => setSelectedSessionId(session.id)}
            >
              <div className="history-item-query">{session.query}</div>
              <div className="history-item-meta">
                <span className="meta-badge model">{session.model}</span>
                <span className="meta-badge mode">{session.mode}</span>
              </div>
            </div>
          ))}

          {telemetry.length > 0 && (
            <div 
              className={`history-item current ${selectedSessionId === 'current' ? 'active' : ''}`}
              onClick={() => setSelectedSessionId('current')}
            >
              <div className="history-item-query">{currentQuery || 'Active Query'}</div>
              <div className="history-item-meta">
                <span className="meta-badge model">{selectedModel}</span>
                <span className="meta-badge mode">{routerMode === 'ge_mcp' ? "GE + MCP" : "All MCP"}</span>
                <span className="meta-badge active-tag">Current</span>
              </div>
            </div>
          )}

          {analysisResult && (
             <div 
               className={`history-item analysis ${selectedSessionId === 'analysis' ? 'active' : ''}`}
               onClick={() => setSelectedSessionId('analysis')}
             >
               <div className="history-item-query">Latency Analysis Report</div>
               <div className="history-item-meta">
                 <span className="meta-badge ai-insight">AI Insight</span>
               </div>
             </div>
          )}
        </div>

        <div className="history-sidebar-actions">
           <button 
             className="analyze-button" 
             onClick={handleAnalyze} 
             disabled={isAnalyzing || allSessions.length === 0}
           >
             {isAnalyzing ? <Loader2 size={16} className="animate-spin" /> : <BarChart2 size={16} />}
             Analyze All
           </button>
           <button 
             className="clear-button" 
             onClick={handleClearHistory}
             disabled={telemetryHistory.length === 0 && telemetry.length === 0}
           >
             <Trash2 size={16} />
             Clear History
           </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="telemetry-main-content">
        
        {selectedSessionId === 'analysis' ? (
          <div className="telemetry-analysis-view">
             <div className="analysis-header">
               <Brain className="analysis-icon" size={24} />
               <h2>Cross-Session Latency Insights</h2>
             </div>
             <div className="analysis-body">
               {isAnalyzing ? (
                 <div className="analysis-loading">
                   <Loader2 className="animate-spin text-blue-500" size={32} />
                   <p>Generating deep analysis across your executions...</p>
                 </div>
               ) : analysisResult ? (
                 <div className="markdown-container">
                   <MarkdownRenderer content={analysisResult} />
                 </div>
               ) : (
                 <p className="no-result">No analysis result generated yet.</p>
               )}
             </div>
          </div>
        ) : activeSession ? (
          <>
            <div className="telemetry-header">
              <Zap size={24} className="telemetry-icon" />
              <h2>{activeSession.id === 'current' ? 'Live Execution Trace' : 'Historical Trace'}</h2>
            </div>
            <div className="telemetry-board">
              <div className="telemetry-summary" id="telemetry-summary">
                <div className="summary-stat">
                  <span className="stat-label">Model Engine</span>
                  <span className="stat-value text-blue-400">{activeSession.model}</span>
                </div>
                <div className="summary-stat">
                  <span className="stat-label">Total Turnaround</span>
                  <span className="stat-value">{totalTime}s</span>
                </div>
                <div className="summary-stat">
                  <span className="stat-label">Steps Logged</span>
                  <span className="stat-value">{activeSession.telemetry.length - 1}</span>
                </div>
                {activeSession.tokenUsage && (
                  <div className="summary-stat">
                    <span className="stat-label">Total Tokens (I/O)</span>
                    <span className="stat-value">{activeSession.tokenUsage.total.toLocaleString()}</span>
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
                    {activeSession.telemetry.map((event, idx) => {
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
                    const localTotalTime = activeSession.telemetry.find((t) => t.step.includes('Total'))?.duration_s || 1;
                    
                    return activeSession.telemetry.map((event, idx) => {
                      if (event.step.includes('Total')) return null;

                      const percentage = (event.duration_s / localTotalTime) * 100;
                      
                      // Determine which reasoning steps belong to this latency phase
                      let relevantSteps: string[] = [];
                      const stepLower = event.step.toLowerCase();
                      
                      if (stepLower.includes('system-atomic') || stepLower.includes('handshake') || stepLower.includes('intent')) {
                        relevantSteps = activeSession.reasoningSteps.filter(s => s.startsWith('[Router]') || s.startsWith('[SYSTEM]'));
                      } else if (stepLower.includes('enterprise-atomic')) {
                        relevantSteps = activeSession.reasoningSteps.filter(s => 
                          s.startsWith('[Enterprise Proxy]') || 
                          s.startsWith('[Discovery Engine]') || 
                          s.startsWith('[Action]') ||
                          s.startsWith('[Redaction]')
                        );
                      } else if (stepLower.includes('public-atomic')) {
                        relevantSteps = activeSession.reasoningSteps.filter(s => s.startsWith('[Public Web]'));
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
                    const orphanSteps = activeSession.reasoningSteps.filter(step => 
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
          </>
        ) : null}
      </div>
    </div>
  );
};
