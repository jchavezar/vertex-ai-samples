import React, { useState } from 'react';
import {
  Search,
  Database,
  Code2,
  TrendingUp,
  BarChart3,
  Cpu,
  CheckCircle2,
  Clock,
  ChevronDown,
  ChevronUp,
  AlertCircle
} from 'lucide-react';
import type { ToolExecution } from '../types';

interface ToolTelemetryCardProps {
  tool: ToolExecution;
}

const CATEGORY_STYLES = {
  Search: {
    bg: 'bg-cyan-50/70',
    border: 'border-cyan-200',
    text: 'text-cyan-900',
    badge: 'bg-cyan-100 text-cyan-800 border-cyan-300',
    icon: Search,
  },
  'Database Query': {
    bg: 'bg-indigo-50/70',
    border: 'border-indigo-200',
    text: 'text-indigo-900',
    badge: 'bg-indigo-100 text-indigo-800 border-indigo-300',
    icon: Database,
  },
  'Code Execution': {
    bg: 'bg-emerald-50/70',
    border: 'border-emerald-200',
    text: 'text-emerald-900',
    badge: 'bg-emerald-100 text-emerald-800 border-emerald-300',
    icon: Code2,
  },
  'Financial Modeling': {
    bg: 'bg-amber-50/70',
    border: 'border-amber-200',
    text: 'text-amber-900',
    badge: 'bg-amber-100 text-amber-800 border-amber-300',
    icon: TrendingUp,
  },
  'Dynamic Visualization': {
    bg: 'bg-purple-50/70',
    border: 'border-purple-200',
    text: 'text-purple-900',
    badge: 'bg-purple-100 text-purple-800 border-purple-300',
    icon: BarChart3,
  },
  'System Tool': {
    bg: 'bg-slate-50',
    border: 'border-slate-200',
    text: 'text-slate-900',
    badge: 'bg-slate-100 text-slate-800 border-slate-300',
    icon: Cpu,
  },
};

export const ToolTelemetryCard: React.FC<ToolTelemetryCardProps> = ({ tool }) => {
  const [isExpanded, setIsExpanded] = useState<boolean>(false);
  const style = CATEGORY_STYLES[tool.category] || CATEGORY_STYLES['System Tool'];
  const IconComponent = style.icon;

  const renderSummary = () => {
    if (tool.status === 'running') {
      return (
        <span className="text-slate-500 text-[11px] flex items-center space-x-1">
          <Clock className="w-3 h-3 animate-spin text-cyan-600" />
          <span>Invoking remote ADK execution...</span>
        </span>
      );
    }

    if (tool.category === 'Search' && tool.output?.results) {
      return (
        <span className="text-slate-700 text-[11px]">
          Retrieved {tool.output.result_count || tool.output.results.length} grounded citations
        </span>
      );
    }

    if (tool.category === 'Database Query' && tool.output?.data) {
      const d = tool.output.data;
      return (
        <span className="text-slate-700 text-[11px]">
          Found <span className="font-semibold">{d.metric}</span>: {d.variance_pct || 'Aggregated'}
        </span>
      );
    }

    if (tool.category === 'Financial Modeling' && tool.output) {
      return (
        <span className="text-slate-700 text-[11px]">
          NPV: <span className="font-semibold text-emerald-700">${tool.output.npv?.toLocaleString()}</span> | ROI: {tool.output.roi_pct}%
        </span>
      );
    }

    if (tool.category === 'Code Execution' && tool.output) {
      return (
        <span className="text-slate-700 text-[11px] font-mono">
          Executed in {tool.output.execution_time_ms}ms • {tool.output.sandbox_security || 'SOC2 Isolated'}
        </span>
      );
    }

    if (tool.category === 'Dynamic Visualization' && tool.output?.artifact) {
      return (
        <span className="text-slate-700 text-[11px]">
          Generated chart: <span className="font-semibold">{tool.output.artifact.title}</span>
        </span>
      );
    }

    return (
      <span className="text-slate-600 text-[11px]">
        Execution finished ({tool.status})
      </span>
    );
  };

  return (
    <div className={`mb-2.5 rounded-lg border ${style.border} ${style.bg} overflow-hidden shadow-2xs transition-all`}>
      <div
        onClick={() => setIsExpanded(!isExpanded)}
        className="px-3 py-2 flex items-center justify-between cursor-pointer hover:bg-white/40 transition-colors select-none"
      >
        <div className="flex items-center space-x-2.5 min-w-0">
          <div className="p-1 rounded bg-white border border-slate-200 shadow-2xs text-slate-700 shrink-0">
            <IconComponent className="w-3.5 h-3.5" />
          </div>

          <div className="flex items-center space-x-2 truncate">
            <span className="text-xs font-semibold text-slate-900 font-mono truncate">
              {tool.tool_name}
            </span>
            <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded border ${style.badge} shrink-0`}>
              {tool.category}
            </span>
          </div>
        </div>

        <div className="flex items-center space-x-2 ml-2 shrink-0">
          <div className="hidden sm:block">{renderSummary()}</div>

          {tool.status === 'running' ? (
            <span className="w-2 h-2 rounded-full bg-cyan-500 animate-ping" />
          ) : tool.status === 'success' ? (
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
          ) : (
            <AlertCircle className="w-3.5 h-3.5 text-rose-500" />
          )}

          {isExpanded ? (
            <ChevronUp className="w-3.5 h-3.5 text-slate-400" />
          ) : (
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          )}
        </div>
      </div>

      {/* Expanded Telemetry Inspector */}
      {isExpanded && (
        <div className="p-3 border-t border-slate-200/80 bg-white/90 text-xs space-y-2 font-mono">
          <div>
            <div className="text-[10px] uppercase font-bold text-slate-600 tracking-wider mb-1">
              Input Arguments:
            </div>
            <pre className="p-2 rounded bg-slate-900 text-cyan-300 text-[11px] overflow-x-auto max-h-36">
              {JSON.stringify(tool.arguments, null, 2)}
            </pre>
          </div>

          {tool.output && (
            <div>
              <div className="text-[10px] uppercase font-bold text-slate-600 tracking-wider mb-1">
                Execution Output Payload:
              </div>
              <pre className="p-2 rounded bg-slate-900 text-emerald-300 text-[11px] overflow-x-auto max-h-48">
                {JSON.stringify(tool.output, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
