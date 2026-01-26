import React, { useRef, useEffect } from 'react';
import { Terminal } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface LogEntry {
  type: 'user' | 'assistant' | 'tool_call' | 'tool_result' | 'error' | 'system' | 'debug' | 'system_status';
  content?: string;
  tool?: string;
  args?: any;
  result?: any;
  duration?: number | string;
  timestamp: string;
}

interface TraceLogProps {
  logs: LogEntry[];
  isMaximized?: boolean;
  selectedModel?: string; // Add selectedModel prop
}

import { useDashboardStore } from '../../store/dashboardStore';

const TraceLog: React.FC<TraceLogProps> = ({ logs = [], isMaximized = false, selectedModel }) => {
  const endRef = useRef<HTMLDivElement>(null);
  const { theme } = useDashboardStore();
  const isDark = theme === 'dark';

  // Group logs by session or just list them? 
  // For now, simple list but correctly styled.
  
  useEffect(() => {
    if (endRef.current) {
      endRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  if (!logs || logs.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-[var(--text-muted)] gap-4 opacity-50">
        <Terminal size={48} color="#e6ebf1" />
        <p>No activity recorded yet.</p>
      </div>
    );
  }

  return (
    <div className="p-4 font-mono text-[11px] bg-transparent min-h-full space-y-4">
      {/* Session/Model Header if active */}
      {selectedModel && logs.length > 0 && (
         <div className="flex items-center justify-center mb-6 opacity-70">
            <div className="px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-[10px]">
               Session with <span className="font-bold">{selectedModel}</span>
            </div>
         </div>
      )}

      {logs.map((log, idx) => {
        // Error Detection Logic
        let visualType: string = log.type;
        let isError = false;

        if (log.type === 'tool_result') {
             const str = typeof log.result === 'string' ? log.result : JSON.stringify(log.result);
             if (str && (str.startsWith('Error') || str.includes('"error":') || str.includes('Error:'))) {
                 visualType = 'tool_error';
                 isError = true;
             }
        } else if (log.type === 'error') {
            isError = true;
        }

        const isTool = log.type === 'tool_call' || log.type === 'tool_result';
        
        return (
          <div key={idx} className={`relative pl-4 border-l-2 transition-all duration-300 ${getBorderColorClass(visualType)}`}>
            {/* Timeline Dot */}
            <div className={`absolute -left-[5px] top-0.5 w-2 h-2 rounded-full ring-4 ring-[var(--bg-app)] ${getDotColorClass(visualType)}`} />
            
            <div className="flex flex-col gap-1.5">
               {/* Header: Timestamp + Badge */}
               <div className="flex items-center gap-2 opacity-80 hover:opacity-100 transition-opacity">
                 <span className="text-[10px] font-medium font-sans text-[var(--text-muted)]">{log.timestamp}</span>
                 <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider ${getBadgeColorClass(visualType)}`}>
                   {visualType.replace('tool_', '').replace('_', ' ')}
                 </span>
                 {/* Show Model Tag on System Status */}
                 {log.type === 'system_status' && log.args?.model && (
                    <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-blue-900/30 text-blue-300 border border-blue-800/50">
                        {log.args.model}
                    </span>
                 )}
               </div>

               {/* Content Card */}
               <div className={`rounded-lg overflow-hidden ${getContentBgClass(visualType, isDark)} border ${getContentBorderClass(visualType)}`}>
                 {renderContent(log, isMaximized, isDark, isError)}
               </div>
            </div>
          </div>
        );
      })}
      <div ref={endRef} />
    </div>
  );
};

// Helper Functions
const getDotColorClass = (type: string) => {
    switch (type) {
      case 'user': return 'bg-[var(--brand)]';
      case 'tool_call': return 'bg-purple-500';
      case 'tool_result': return 'bg-emerald-500';
      case 'tool_error': return 'bg-red-500 animate-pulse';
      case 'error': return 'bg-red-600';
      default: return 'bg-gray-500';
    }
};

const getBorderColorClass = (type: string) => {
  switch (type) {
    case 'user': return 'border-[var(--brand)]';
    case 'tool_call': return 'border-purple-500/30';
    case 'tool_result': return 'border-emerald-500/30';
    case 'tool_error': return 'border-red-500/50';
    case 'error': return 'border-red-500/50';
    default: return 'border-gray-700/30';
  }
};

const getBadgeColorClass = (type: string) => {
  switch (type) {
    case 'user': return 'text-[var(--brand)]';
    case 'assistant': return 'text-slate-400';
    case 'tool_call': return 'text-purple-400';
    case 'tool_result': return 'text-emerald-400';
    case 'tool_error': return 'text-red-400 font-bold';
    case 'error': return 'text-red-500 font-bold';
    case 'debug': return 'text-blue-600 font-medium';
    case 'system_status': return 'text-slate-600 font-medium italic'; 
    default: return 'text-gray-500';
  }
};

const getContentBgClass = (type: string, isDark: boolean) => {
    switch(type) {
        case 'tool_call': return isDark ? 'bg-purple-900/10' : 'bg-purple-50';
        case 'tool_result': return isDark ? 'bg-emerald-900/10' : 'bg-emerald-50';
        case 'tool_error': return isDark ? 'bg-red-900/20' : 'bg-red-50';
        case 'error': return isDark ? 'bg-red-900/20' : 'bg-red-50';
        default: return 'bg-transparent';
    }
}

const getContentBorderClass = (type: string) => {
    switch(type) {
        case 'tool_call': return 'border-purple-500/10';
        case 'tool_result': return 'border-emerald-500/10';
        case 'tool_error': return 'border-red-500/20';
        case 'error': return 'border-red-500/20';
        default: return 'border-transparent';
    }
}

const deepParseJSON = (obj: any): any => {
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
    const newObj: any = {};
    for (const key in obj) {
      newObj[key] = deepParseJSON(obj[key]);
    }
    return newObj;
  }
  return obj;
};

const renderContent = (log: LogEntry, isMaximized: boolean, isDark: boolean, isError: boolean = false) => {
  switch (log.type) {
    case 'user':
      return <div className="font-semibold p-1">{log.content}</div>;
    case 'assistant':
      return <div className="p-1"><ReactMarkdown remarkPlugins={[remarkGfm]}>{log.content || ''}</ReactMarkdown></div>;
    case 'tool_call':
      let argsDisplay = '';
      try {
        argsDisplay = JSON.stringify(deepParseJSON(log.args), null, 2);
      } catch (e) {
        argsDisplay = String(log.args);
      }
      return (
        <div className="p-2">
          <div className="flex items-center gap-2 mb-2">
             <span className="text-purple-400">⚡</span>
             <strong>Executing:</strong> <span className={`${isDark ? 'text-purple-300' : 'text-purple-600'} font-bold`}>{log.tool}</span>
          </div>
          <div className="p-2.5 rounded-md overflow-x-auto border border-black/5 bg-white/50">
            <pre className={`text-[11px] ${isDark ? 'text-gray-100' : 'text-slate-900 font-semibold'} font-mono`}>{argsDisplay}</pre>
          </div>
        </div>
      );
    case 'tool_result':
      let resultDisplay = '';
      try {
        resultDisplay = JSON.stringify(deepParseJSON(log.result), null, 2);
      } catch (e) {
        resultDisplay = String(log.result);
      }
      
      return (
        <div className="p-2">
          <div className="flex items-center gap-2 mb-2">
            {isError ? <span className="text-red-500 font-bold">⚠️ FAILED</span> : <span className="text-emerald-400">✓</span>}
            <strong>{isError ? 'Error from:' : 'Result from:'}</strong> <span className={`${isError ? 'text-red-400' : (isDark ? 'text-emerald-300' : 'text-emerald-700')} font-bold`}>{log.tool}</span> 
            {log.duration && <span className="text-[9px] text-gray-500 bg-black/10 px-1.5 py-0.5 rounded-full ml-auto font-mono">{typeof log.duration === 'number' ? log.duration.toFixed(3) + 's' : log.duration}</span>}
          </div>
          <div className={`p-2.5 rounded-md overflow-x-auto border ${isError ? 'bg-red-50 border-red-200' : 'bg-white/50 border-black/5'}`}>
            <pre className={`text-[11px] ${isError ? 'text-red-800' : (isDark ? 'text-gray-100' : 'text-slate-900 font-semibold')} ${isMaximized ? 'max-h-[600px]' : 'max-h-[300px]'} overflow-y-auto custom-scrollbar font-mono`}>{resultDisplay}</pre>
          </div>
        </div>
      );
    case 'error':
      return <div className="text-red-600 font-extrabold p-2 bg-red-100/10 rounded">{log.content}</div>;
    case 'system':
      return <div className="italic text-[var(--text-muted)] p-1">{log.content}</div>;
    case 'system_status':
    case 'debug':
      return (
        <div className="text-[var(--text-secondary)] italic p-1">{log.content}</div>
      );
    default:
      return <div className="text-[var(--text-primary)] p-1">{String(log.content || '')}</div>;
  }
};

export default TraceLog;
