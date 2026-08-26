import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { 
  Sparkles, 
  User, 
  Copy, 
  Check, 
  AlertCircle, 
  Search
} from 'lucide-react';
import { Message } from '../types/chat';
import { GroundingCard } from './GroundingCard';

interface MessageItemProps {
  message: Message;
}

export const MessageItem: React.FC<MessageItemProps> = ({ message }) => {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === 'user';

  const copyToClipboard = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (isUser) {
    return (
      <div className="flex justify-end mb-4 animate-fade-in">
        <div className="flex items-start gap-2.5 max-w-[85%] sm:max-w-[75%]">
          <div className="bg-[#e8f0fe] border border-blue-100 rounded-2xl rounded-tr-xs px-4 py-3 text-[#174ea6] shadow-xs">
            <p className="text-sm sm:text-[15px] whitespace-pre-wrap leading-relaxed">
              {message.content}
            </p>
          </div>
          <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center shrink-0 shadow-xs mt-0.5">
            <User className="w-4 h-4" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start mb-5 animate-fade-in group">
      <div className="flex items-start gap-3 w-full max-w-[95%] sm:max-w-[90%]">
        {/* Assistant Avatar */}
        <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 text-white flex items-center justify-center shrink-0 shadow-xs mt-1">
          <Sparkles className="w-4 h-4" />
        </div>

        {/* Assistant Card Body */}
        <div className="flex-1 bg-white border border-[#dadce0] rounded-2xl rounded-tl-xs p-4 sm:p-5 shadow-xs transition hover:border-gray-300">
          {/* Tool execution indicator if active */}
          {message.activeTool && (
            <div className="inline-flex items-center gap-1.5 text-xs bg-amber-50 border border-amber-200 text-amber-800 px-2.5 py-1 rounded-full mb-3 animate-pulse">
              <Search className="w-3.5 h-3.5" />
              <span>Ejecutando herramienta ADK: <strong>{message.activeTool}</strong></span>
            </div>
          )}

          {/* Error Message */}
          {message.error ? (
            <div className="flex items-start gap-2 text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-3">
              <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
              <span>{message.content}</span>
            </div>
          ) : (
            <div className="markdown-content text-sm sm:text-[15px] text-[#202124] leading-relaxed">
              <ReactMarkdown 
                remarkPlugins={[remarkGfm]}
                components={{
                  code({ node, className, children, ...props }) {
                    const match = /language-(\w+)/.exec(className || '');
                    const isInline = !match && !String(children).includes('\n');
                    return isInline ? (
                      <code className="bg-[#f1f3f4] text-[#d93025] px-1.5 py-0.5 rounded text-xs font-mono" {...props}>
                        {children}
                      </code>
                    ) : (
                      <div className="my-3 rounded-xl overflow-hidden border border-[#dadce0] bg-[#f8fafd]">
                        <div className="bg-[#f1f3f4] px-3 py-1.5 text-[11px] font-mono text-[#5f6368] flex items-center justify-between border-b border-[#dadce0]">
                          <span>{match ? match[1] : 'code'}</span>
                        </div>
                        <pre className="p-3 text-xs sm:text-sm text-[#202124] overflow-x-auto font-mono bg-white">
                          <code className={className} {...props}>
                            {children}
                          </code>
                        </pre>
                      </div>
                    );
                  }
                }}
              >
                {message.content || (message.isStreaming ? '▌' : '')}
              </ReactMarkdown>

              {message.isStreaming && message.content && (
                <span className="inline-block w-2 h-4 bg-blue-600 ml-1 animate-pulse" />
              )}
            </div>
          )}

          {/* Grounding web search results */}
          {message.grounding && (
            <GroundingCard grounding={message.grounding} />
          )}

          {/* Message Footer / Copy Action */}
          {!message.isStreaming && message.content && !message.error && (
            <div className="mt-3 pt-2 border-t border-[#f1f3f4] flex items-center justify-between text-xs text-[#5f6368]">
              <span className="text-[11px]">
                {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
              <button
                onClick={copyToClipboard}
                className="flex items-center gap-1 hover:text-blue-600 p-1 rounded hover:bg-[#f1f3f4] transition"
                title="Copiar respuesta"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-green-600" /> : <Copy className="w-3.5 h-3.5" />}
                <span className="text-[11px]">{copied ? 'Copiado' : 'Copiar'}</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
