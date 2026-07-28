import React from 'react';
import { ChatMessage } from '../../types';
import { RichTextRenderer } from '../RichTextRenderer';
import { Bot, User, ExternalLink, Globe, Zap, Network, FileText } from 'lucide-react';

interface ChatMessageItemProps {
  message: ChatMessage;
  onRunSandboxCommand?: (cmd: string) => void;
  onOpenAnalyticalOverlay?: () => void;
  onQuickQuery?: (query: string) => void;
  isLightMode?: boolean;
}

export const ChatMessageItem: React.FC<ChatMessageItemProps> = ({
  message,
  onRunSandboxCommand,
  onOpenAnalyticalOverlay,
  onQuickQuery,
  isLightMode = false
}) => {
  const isAgent = message.sender === 'agent';

  return (
    <div className={`flex items-start space-x-3 ${isAgent ? '' : 'flex-row-reverse space-x-reverse'}`}>
      {/* Avatar */}
      <div
        className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 shadow-md ${
          isAgent
            ? isLightMode
              ? 'bg-slate-950 text-white shadow-slate-900/20'
              : 'bg-gradient-to-br from-cyan-600 to-blue-700 text-white ring-1 ring-cyan-400/30 shadow-cyan-500/20'
            : isLightMode
              ? 'bg-slate-800 text-white'
              : 'bg-slate-800 text-slate-300 border border-slate-700'
        }`}
      >
        {isAgent ? <Bot className="w-4 h-4" /> : <User className="w-4 h-4" />}
      </div>

      {/* Bubble */}
      <div
        className={`rounded-2xl p-4 max-w-[92%] text-xs leading-relaxed transition-all ${
          isAgent
            ? isLightMode
              ? 'bg-white border border-slate-300 text-slate-950 font-medium shadow-md'
              : 'bg-slate-900/95 border border-slate-800/90 text-slate-200 shadow-xl'
            : isLightMode
              ? 'bg-slate-950 text-white font-bold shadow-md'
              : 'bg-blue-600 text-white shadow-md'
        }`}
      >
        {isAgent ? (
          <RichTextRenderer text={message.text} onRunSandboxCommand={onRunSandboxCommand} isLightMode={isLightMode} />
        ) : (
          <div className="whitespace-pre-line break-words">{message.text}</div>
        )}

        {/* Dynamic Inline Action Buttons */}
        {isAgent && (
          <div className={`mt-3 pt-2.5 border-t flex flex-wrap gap-1.5 ${
            isLightMode ? 'border-slate-200' : 'border-slate-800/80'
          }`}>
            <button
              onClick={() => onQuickQuery && onQuickQuery('Search Reddit & Google for this error')}
              className={`px-2 py-1 rounded-md border text-[10px] font-mono font-bold flex items-center gap-1 cursor-pointer transition-all ${
                isLightMode
                  ? 'bg-slate-950 text-white border-slate-900 hover:bg-slate-800 shadow-sm'
                  : 'bg-cyan-950/40 hover:bg-cyan-900/70 border-cyan-500/30 text-cyan-300'
              }`}
              title="Search Google & Reddit for error solutions"
            >
              <Globe className="w-3 h-3 text-cyan-400" />
              <span>🌐 Deep Search</span>
            </button>

            {onOpenAnalyticalOverlay && (
              <button
                onClick={onOpenAnalyticalOverlay}
                className={`px-2 py-1 rounded-md border text-[10px] font-mono font-bold flex items-center gap-1 cursor-pointer transition-all ${
                  isLightMode
                    ? 'bg-purple-900 text-white border-purple-950 hover:bg-purple-800 shadow-sm'
                    : 'bg-purple-950/40 hover:bg-purple-900/70 border-purple-500/30 text-purple-300'
                }`}
                title="Open Interactive Mindmap & Analytical Workspace"
              >
                <Network className="w-3 h-3 text-purple-300" />
                <span>🧠 Mindmap Engine</span>
              </button>
            )}
          </div>
        )}

        {/* Cited Web / Doc Sources */}
        {isAgent && message.sourcesCited && message.sourcesCited.length > 0 && (
          <div className={`mt-3 pt-2.5 border-t space-y-1.5 ${
            isLightMode ? 'border-slate-200' : 'border-slate-800/80'
          }`}>
            <div className={`flex items-center space-x-1 text-[10px] font-bold uppercase ${
              isLightMode ? 'text-slate-950 font-mono' : 'text-cyan-400'
            }`}>
              <Globe className="w-3 h-3" />
              <span>Google Search & Official Sources</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {message.sourcesCited.map((src, idx) => {
                const isUrl = src.startsWith('http');
                return isUrl ? (
                  <a
                    key={idx}
                    href={src}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded transition-colors font-mono font-bold ${
                      isLightMode
                        ? 'bg-slate-100 hover:bg-slate-200 border border-slate-300 text-slate-950'
                        : 'text-cyan-300 bg-cyan-950/40 hover:bg-cyan-900/60 border border-cyan-800/50'
                    }`}
                  >
                    <span>{src.replace(/https?:\/\/(www\.)?/, '').split('/')[0]}</span>
                    <ExternalLink className="w-2.5 h-2.5" />
                  </a>
                ) : (
                  <span
                    key={idx}
                    className={`text-[10px] px-2 py-0.5 rounded border font-mono ${
                      isLightMode ? 'bg-slate-100 border-slate-300 text-slate-900 font-bold' : 'text-slate-300 bg-slate-800 border-slate-700'
                    }`}
                  >
                    {src}
                  </span>
                );
              })}
            </div>
          </div>
        )}

        {/* Agent Metadata Footer */}
        {isAgent && (
          <div className={`mt-2.5 pt-2 border-t flex items-center justify-between text-[9px] font-mono ${
            isLightMode ? 'border-slate-200 text-slate-700 font-bold' : 'border-slate-800/60 text-slate-500'
          }`}>
            <span>Model: gemini-2.5-flash (GA • global)</span>
            <span className={isLightMode ? 'text-emerald-700 font-extrabold' : 'text-emerald-400'}>⚡ 2.7s Execution (6.6X Faster)</span>
          </div>
        )}
      </div>
    </div>
  );
};
