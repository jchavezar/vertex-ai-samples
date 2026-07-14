import React, { useState, useRef, useEffect } from 'react';
import { GcpErrorItem, CloudAssistDiagnostic, ChatMessage } from '../../types';
import { ChatMessageItem } from './ChatMessageItem';
import { ClaudeInkSpinner } from './ClaudeInkSpinner';
import { Bot, Send, Sparkles, HelpCircle, ChevronRight, ChevronLeft, Globe } from 'lucide-react';

interface ChatbotDrawerProps {
  selectedError: GcpErrorItem | null;
  diagnostic: CloudAssistDiagnostic | null;
  messages: ChatMessage[];
  onSendMessage: (text: string) => void;
  isSending: boolean;
}

const QUICK_SUGGESTIONS = [
  "Search Reddit & community tips for this error",
  "Provide step-by-step gcloud fix commands",
  "How can I prevent this error from happening again?"
];

export const ChatbotDrawer: React.FC<ChatbotDrawerProps> = ({
  selectedError,
  diagnostic,
  messages,
  onSendMessage,
  isSending
}) => {
  const [isOpen, setIsOpen] = useState(true);
  const [input, setInput] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isSending]);

  const handleSend = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || isSending) return;
    onSendMessage(input);
    setInput('');
  };

  const handleSuggestionClick = (text: string) => {
    if (isSending) return;
    onSendMessage(text);
  };

  return (
    <aside
      className={`h-full border-l border-slate-800/80 bg-[#0c101a]/95 flex flex-col transition-all duration-300 relative z-30 ${
        isOpen ? 'w-96' : 'w-12'
      }`}
    >
      {/* Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="absolute -left-3 top-6 w-6 h-6 rounded-full bg-slate-900 border border-slate-700 hover:border-cyan-400 text-slate-300 hover:text-cyan-300 flex items-center justify-center shadow-lg transition-colors z-40"
        title={isOpen ? 'Collapse Agent Chatbot' : 'Open Agent Chatbot'}
      >
        {isOpen ? <ChevronRight className="w-3.5 h-3.5" /> : <ChevronLeft className="w-3.5 h-3.5" />}
      </button>

      {/* Collapsed Sidebar Icon State */}
      {!isOpen && (
        <div
          onClick={() => setIsOpen(true)}
          className="flex-1 flex flex-col items-center py-6 space-y-6 cursor-pointer hover:bg-slate-900/40"
        >
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-600 to-blue-700 text-white flex items-center justify-center shadow-md shadow-cyan-500/20">
            <Bot className="w-4 h-4" />
          </div>
          <span className="text-xs font-semibold tracking-widest uppercase text-slate-400 [writing-mode:vertical-lr] rotate-180">
            ADK Remediation Agent
          </span>
        </div>
      )}

      {/* Expanded Sidebar State */}
      {isOpen && (
        <>
          {/* Header */}
          <div className="p-4 border-b border-slate-800/80 bg-[#0a0e17] flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-600 to-blue-700 text-white flex items-center justify-center shadow-md shadow-cyan-500/20">
                <Bot className="w-4 h-4" />
              </div>
              <div>
                <h2 className="text-xs font-bold text-white tracking-tight">ADK Remediation Agent</h2>
                <div className="flex items-center space-x-1.5 text-[10px] text-cyan-400">
                  <Globe className="w-2.5 h-2.5" />
                  <span>Google Search Built-In</span>
                </div>
              </div>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
              gemini-2.5-flash
            </span>
          </div>

          {/* Active Context Banner */}
          {selectedError && (
            <div className="px-3.5 py-2 bg-slate-900/70 border-b border-slate-800/60 flex items-center justify-between text-[11px]">
              <div className="flex items-center space-x-1.5 text-slate-300 truncate">
                <Sparkles className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0" />
                <span className="truncate">Active Context: <strong className="text-cyan-300">{selectedError.serviceName}</strong></span>
              </div>
            </div>
          )}

          {/* Message Stream */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((msg) => (
              <ChatMessageItem key={msg.id} message={msg} />
            ))}

            {isSending && (
              <div className="pt-1">
                <ClaudeInkSpinner />
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Quick Action Chips */}
          <div className="px-3.5 py-2 border-t border-slate-800/60 bg-slate-950/60">
            <div className="text-[10px] font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">
              Quick Inquiries
            </div>
            <div className="flex flex-col gap-1.5">
              {QUICK_SUGGESTIONS.map((sug, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSuggestionClick(sug)}
                  disabled={isSending}
                  className="text-left text-[11px] px-2.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-cyan-500/40 text-slate-300 hover:text-white transition-all truncate"
                >
                  {sug}
                </button>
              ))}
            </div>
          </div>

          {/* Input Bar */}
          <form onSubmit={handleSend} className="p-3.5 border-t border-slate-800/80 bg-[#0e131d]">
            <div className="relative flex items-center">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask ADK Agent for fixes or Reddit search..."
                disabled={isSending}
                className="w-full bg-slate-950/90 border border-slate-800 focus:border-cyan-500/70 rounded-xl py-2.5 pl-3.5 pr-10 text-xs text-slate-100 placeholder-slate-500 focus:outline-none transition-all"
              />
              <button
                type="submit"
                disabled={!input.trim() || isSending}
                className="absolute right-1.5 p-1.5 rounded-lg bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 disabled:opacity-40 text-white transition-all shadow-sm"
              >
                <Send className="w-3.5 h-3.5" />
              </button>
            </div>
          </form>
        </>
      )}
    </aside>
  );
};
