import React, { useState } from 'react';
import {
  Bot,
  User,
  Sparkles,
  BarChart3,
  Copy,
  Check,
  Cpu,
  Clock,
  ExternalLink
} from 'lucide-react';
import type { ChatMessage as ChatMessageType, ArtifactData } from '../types';
import { ThinkingDrawer } from './ThinkingDrawer';
import { ToolTelemetryCard } from './ToolTelemetryCard';

interface ChatMessageProps {
  message: ChatMessageType;
  onOpenArtifact?: (artifact: ArtifactData) => void;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message, onOpenArtifact }) => {
  const [copied, setCopied] = useState<boolean>(false);
  const isAssistant = message.role === 'assistant';

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      className={`py-4 px-4 sm:px-6 transition-colors ${
        isAssistant ? 'bg-white/60' : 'bg-transparent'
      }`}
    >
      <div className="max-w-4xl mx-auto flex items-start space-x-3.5">
        {/* Avatar */}
        <div
          className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 shadow-2xs ${
            isAssistant
              ? 'bg-slate-900 text-cyan-400 border border-slate-700'
              : 'bg-slate-200 text-slate-700 border border-slate-300'
          }`}
        >
          {isAssistant ? <Bot className="w-4 h-4" /> : <User className="w-4 h-4" />}
        </div>

        {/* Content Body */}
        <div className="flex-1 min-w-0">
          {/* Header info */}
          <div className="flex items-center justify-between mb-1.5">
            <div className="flex items-center space-x-2">
              <span className="text-xs font-bold text-slate-900">
                {isAssistant ? 'ADK Enterprise Assistant' : 'You (Enterprise Operator)'}
              </span>
              {isAssistant && (
                <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-indigo-50 text-indigo-700 border border-indigo-200">
                  gemini-3.7-flash
                </span>
              )}
            </div>

            {isAssistant && message.content && (
              <button
                onClick={handleCopy}
                className="text-slate-400 hover:text-slate-700 p-1 rounded hover:bg-slate-100 transition-colors cursor-pointer"
                title="Copy response text"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
            )}
          </div>

          {/* Thinking Drawer */}
          {isAssistant && message.thoughts && message.thoughts.length > 0 && (
            <ThinkingDrawer
              thoughts={message.thoughts}
              isStreaming={message.isStreaming}
              thoughtTokenCount={message.usage?.thought_tokens}
            />
          )}

          {/* Live Tool Execution Telemetry Cards */}
          {isAssistant && message.tools && message.tools.length > 0 && (
            <div className="my-2 space-y-1">
              {message.tools.map((tool) => (
                <ToolTelemetryCard key={tool.tool_call_id} tool={tool} />
              ))}
            </div>
          )}

          {/* Rendered Markdown Text */}
          {message.content ? (
            <div className="prose-enterprise text-sm text-slate-800 leading-relaxed break-words">
              {message.content.split('\n\n').map((paragraph, pIdx) => {
                if (paragraph.startsWith('### ')) {
                  return (
                    <h3 key={pIdx} className="text-sm font-bold text-slate-900 mt-3 mb-1.5">
                      {paragraph.replace('### ', '')}
                    </h3>
                  );
                }
                if (paragraph.startsWith('## ')) {
                  return (
                    <h2 key={pIdx} className="text-base font-bold text-slate-900 mt-4 mb-2">
                      {paragraph.replace('## ', '')}
                    </h2>
                  );
                }
                if (paragraph.startsWith('# ')) {
                  return (
                    <h1 key={pIdx} className="text-lg font-bold text-slate-900 mt-4 mb-2">
                      {paragraph.replace('# ', '')}
                    </h1>
                  );
                }
                if (paragraph.startsWith('* ') || paragraph.startsWith('- ')) {
                  const items = paragraph.split('\n');
                  return (
                    <ul key={pIdx} className="list-disc list-inside space-y-1 my-2 text-slate-700 text-xs sm:text-sm">
                      {items.map((item, iIdx) => (
                        <li key={iIdx}>{item.replace(/^(\*|-)\s+/, '')}</li>
                      ))}
                    </ul>
                  );
                }
                return (
                  <p key={pIdx} className="mb-2 text-xs sm:text-sm text-slate-800 leading-relaxed whitespace-pre-wrap">
                    {paragraph}
                  </p>
                );
              })}
            </div>
          ) : isAssistant && message.isStreaming ? (
            <div className="flex items-center space-x-2 text-xs text-slate-500 py-1">
              <span className="w-2 h-2 rounded-full bg-cyan-600 animate-pulse" />
              <span>Synthesizing response stream...</span>
            </div>
          ) : null}

          {/* Artifact Buttons */}
          {message.artifacts && message.artifacts.length > 0 && onOpenArtifact && (
            <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center space-x-2 flex-wrap gap-y-1.5">
              <span className="text-[11px] font-semibold text-slate-500 flex items-center space-x-1">
                <Sparkles className="w-3 h-3 text-cyan-600" />
                <span>Generated Artifacts:</span>
              </span>
              {message.artifacts.map((art) => (
                <button
                  key={art.artifact_id}
                  onClick={() => onOpenArtifact(art)}
                  className="px-2.5 py-1 rounded-md bg-cyan-50 hover:bg-cyan-100/80 border border-cyan-200 text-cyan-900 text-xs font-medium flex items-center space-x-1.5 transition-all shadow-2xs cursor-pointer"
                >
                  <BarChart3 className="w-3 h-3 text-cyan-700" />
                  <span>{art.title}</span>
                  <ExternalLink className="w-2.5 h-2.5 text-cyan-600" />
                </button>
              ))}
            </div>
          )}

          {/* Usage & Latency Metadata Footer */}
          {isAssistant && message.usage && !message.isStreaming && (
            <div className="mt-3 pt-2 border-t border-slate-100 flex items-center space-x-4 text-[10px] text-slate-600 font-mono">
              <div className="flex items-center space-x-1">
                <Clock className="w-3 h-3 text-slate-400" />
                <span>{message.elapsedSeconds || 0}s</span>
              </div>
              <div className="flex items-center space-x-1">
                <Cpu className="w-3 h-3 text-slate-400" />
                <span>{message.usage.total_tokens} total tokens</span>
              </div>
              {message.usage.thought_tokens > 0 && (
                <span className="text-indigo-600 font-medium">
                  {message.usage.thought_tokens} reasoning tokens
                </span>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
