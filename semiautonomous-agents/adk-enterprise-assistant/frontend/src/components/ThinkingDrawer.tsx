import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Brain, Sparkles, Copy, Check } from 'lucide-react';

interface ThinkingDrawerProps {
  thoughts: string[];
  isStreaming?: boolean;
  thoughtTokenCount?: number;
}

export const ThinkingDrawer: React.FC<ThinkingDrawerProps> = ({
  thoughts,
  isStreaming = false,
  thoughtTokenCount,
}) => {
  const [isOpen, setIsOpen] = useState<boolean>(true);
  const [copied, setCopied] = useState<boolean>(false);

  if (!thoughts || thoughts.length === 0) return null;

  const fullThoughtText = thoughts.join('\n');

  const handleCopy = () => {
    navigator.clipboard.writeText(fullThoughtText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="mb-3 rounded-lg border border-slate-200 bg-slate-50/90 overflow-hidden shadow-2xs transition-all">
      {/* Header Bar */}
      <div
        onClick={() => setIsOpen(!isOpen)}
        className="px-3 py-2 bg-slate-100/70 border-b border-slate-200/80 flex items-center justify-between cursor-pointer hover:bg-slate-100 transition-colors select-none"
      >
        <div className="flex items-center space-x-2">
          <div className="w-5 h-5 rounded bg-indigo-100 text-indigo-700 flex items-center justify-center">
            <Brain className={`w-3.5 h-3.5 ${isStreaming ? 'animate-pulse text-indigo-600' : ''}`} />
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-semibold text-slate-800">
              Gemini 3.7 Reasoning Stream
            </span>
            {isStreaming ? (
              <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-cyan-100 text-cyan-800 border border-cyan-300 animate-cold-pulse">
                <Sparkles className="w-2.5 h-2.5 mr-1" />
                Synthesizing
              </span>
            ) : (
              <span className="text-[10px] text-slate-500 font-mono">
                {thoughtTokenCount ? `${thoughtTokenCount} thought tokens` : 'Completed Reasoning'}
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleCopy();
            }}
            className="p-1 text-slate-500 hover:text-slate-800 hover:bg-white rounded transition-colors text-[10px] flex items-center space-x-1 cursor-pointer"
            title="Copy reasoning trace"
          >
            {copied ? <Check className="w-3 h-3 text-emerald-600" /> : <Copy className="w-3 h-3" />}
          </button>
          {isOpen ? (
            <ChevronUp className="w-3.5 h-3.5 text-slate-500" />
          ) : (
            <ChevronDown className="w-3.5 h-3.5 text-slate-500" />
          )}
        </div>
      </div>

      {/* Expanded Reasoning Body */}
      {isOpen && (
        <div className="p-3 text-xs font-mono text-slate-700 max-h-60 overflow-y-auto leading-relaxed bg-white/70 space-y-1.5 whitespace-pre-wrap selection:bg-cyan-100">
          {thoughts.map((chunk, idx) => (
            <div key={idx} className="border-l-2 border-indigo-200 pl-2 text-slate-600">
              {chunk}
            </div>
          ))}
          {isStreaming && (
            <div className="flex items-center space-x-1 text-cyan-600 text-[11px] pt-1">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-500 animate-ping" />
              <span>Streaming dynamic thoughts...</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
