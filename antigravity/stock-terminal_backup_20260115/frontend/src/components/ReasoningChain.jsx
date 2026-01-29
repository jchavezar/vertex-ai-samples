import React, { useState, useEffect, useRef } from 'react';
import { ChevronDown, ChevronRight, CheckCircle, Clock, AlertCircle, Terminal, Sparkles } from 'lucide-react';

const ReasoningChain = ({ steps = [], isExpanded, onToggleExpand, thinkingTime }) => {
  const endRef = useRef(null);

  useEffect(() => {
    if (endRef.current && isExpanded) {
      endRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [steps, isExpanded]);

  // No longer returning null when empty to ensure the header is always visible as a widget

  return (
    <div className="reasoning-chain-container">
      <div
        className="reasoning-header"
        onClick={onToggleExpand}
      >
        <div className="reasoning-title">
          <Sparkles size={14} className="icon-pulse" />
          <span>Agent Workflow <span className="step-count">({steps.length})</span></span>
        </div>
        {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
      </div>

      {isExpanded && (
        <div className="reasoning-body">
          <div className="timeline-line"></div>
          {steps.map((step, idx) => (
            step ? <ReasoningStep
              key={idx}
              step={step}
              isLast={idx === steps.length - 1}
              thinkingTime={idx === steps.length - 1 ? thinkingTime : null}
            /> : null
          ))}
          <div ref={endRef} />
        </div>
      )}
    </div>
  );
};

const ReasoningStep = ({ step, isLast, thinkingTime }) => {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    if (isLast) setIsOpen(true);
  }, [isLast]);

  const getIcon = () => {
    try {
      switch (step.type) {
        case 'call': return <Terminal size={12} color="#fff" />;
        case 'result': return <CheckCircle size={12} color="#fff" />;
        case 'error': return <AlertCircle size={12} color="#fff" />;
        default: return <Clock size={12} color="#fff" />;
      }
    } catch (e) {
      return <Clock size={12} color="#fff" />;
    }
  };

  const getColor = () => {
    switch (step.type) {
      case 'call': return '#004b87';
      case 'result': return '#28a745';
      case 'error': return '#dc3545';
      default: return '#6c757d';
    }
  };

  const color = getColor();

  const safeArgs = () => {
    try {
      if (step.args === null || step.args === undefined) return '{}';
      if (typeof step.args === 'string') return step.args;
      return JSON.stringify(step.args, null, 2);
    } catch (e) {
      return '[Invalid Args]';
    }
  };

  const safeFormatResult = (res) => {
    try {
      return formatResult(res);
    } catch (e) {
      return '[Error displaying result]';
    }
  };

  return (
    <div className={`reasoning-step ${step.type || 'processing'}`}>
      <div className="step-marker" style={{ backgroundColor: color }}>
        {getIcon()}
      </div>

      <div className="step-content">
        <div className="step-header" onClick={() => setIsOpen(!isOpen)}>
          <span className="step-title" style={{ color: color }}>
            {step.type === 'call' ? `Executing: ${step.tool || 'Unknown Tool'}` :
              step.type === 'result' ? `Result: ${step.tool || 'Unknown Tool'}` :
                step.type === 'error' ? 'Error' : 'Thinking'}
            {step.type === 'processing' || !step.type ? (
              <span style={{ marginLeft: '8px', opacity: 0.7, fontSize: '0.9em' }}>
                ({thinkingTime ? (thinkingTime / 1000).toFixed(1) : '0.0'}s)
              </span>
            ) : null}
          </span>
          <span className="step-time">{step.timestamp || ''}</span>
        </div>

        {isOpen && (
          <div className="step-details fade-in">
            {step.type === 'call' && (
              <div className="code-block">
                <span className="label">Input:</span>
                <pre>{safeArgs()}</pre>
              </div>
            )}
            {step.type === 'result' && (
              <div className="code-block">
                <span className="label">Output:</span>
                <pre>{safeFormatResult(step.result)}</pre>
              </div>
            )}
            {step.type === 'error' && (
              <div className="error-msg">{step.content || 'Unknown error'}</div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

// Helper to format/truncate result strings
const formatResult = (result) => {
  if (result === null || result === undefined) return 'null';

  const deepParseJSON = (obj) => {
    if (typeof obj === 'string') {
      const trimmed = obj.trim();
      if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
        try {
          return deepParseJSON(JSON.parse(trimmed));
        } catch (e) { return obj; }
      }
    }
    if (Array.isArray(obj)) {
      return obj.map(deepParseJSON);
    }
    if (obj !== null && typeof obj === 'object') {
      const newObj = {};
      for (const key in obj) {
        newObj[key] = deepParseJSON(obj[key]);
      }
      return newObj;
    }
    return obj;
  };

  try {
    const parsed = deepParseJSON(result);
    if (typeof parsed === 'object') {
      return JSON.stringify(parsed, null, 2);
    }
    const str = String(parsed);
    if (str.length > 1000) return str.substring(0, 1000) + '... (truncated)';
    return str;
  } catch (e) {
    return String(result);
  }
};

export default ReasoningChain;
