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
  isLightMode?: boolean;
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
  isSending,
  isLightMode = false
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
      className={`h-full border-l flex flex-col transition-all duration-300 relative z-30 ${
        isOpen ? 'w-96' : 'w-12'
      } ${
        isLightMode
          ? 'bg-white border-slate-200 text-slate-900 shadow-xl'
          : 'bg-[#0c101a]/95 border-slate-800/80 text-white'
      }`}
    >
      {/* Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`absolute -left-3 top-6 w-6 h-6 rounded-full border flex items-center justify-center shadow-lg transition-colors z-40 cursor-pointer ${
          isLightMode
            ? 'bg-slate-950 text-white border-slate-900'
            : 'bg-slate-900 border-slate-700 text-slate-300 hover:text-cyan-300'
        }`}
        title={isOpen ? 'Collapse Agent Chatbot' : 'Open Agent Chatbot'}
      >
        {isOpen ? <ChevronRight className="w-3.5 h-3.5" /> : <ChevronLeft className="w-3.5 h-3.5" />}
      </button>

      {/* Collapsed Sidebar Icon State */}
      {!isOpen && (
        <div
          onClick={() => setIsOpen(true)}
          className={`flex-1 flex flex-col items-center py-6 space-y-6 cursor-pointer ${isLightMode ? 'hover:bg-slate-100' : 'hover:bg-slate-900/40'}`}
        >
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center shadow-md ${isLightMode ? 'bg-slate-950 text-white' : 'bg-gradient-to-br from-cyan-600 to-blue-700 text-white'}`}>
            <Bot className="w-4 h-4" />
          </div>
          <span className={`text-xs font-semibold tracking-widest uppercase [writing-mode:vertical-lr] rotate-180 ${isLightMode ? 'text-slate-800 font-mono font-bold' : 'text-slate-400'}`}>
            ADK Remediation Agent
          </span>
        </div>
      )}

      {/* Expanded Sidebar State */}
      {isOpen && (
        <>
          {/* Header */}
          <div className={`p-4 border-b flex items-center justify-between ${
            isLightMode
              ? 'bg-slate-50 border-slate-200'
              : 'bg-[#0a0e17] border-slate-800/80'
          }`}>
            <div className="flex items-center space-x-2.5">
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center shadow-md ${isLightMode ? 'bg-slate-950 text-white' : 'bg-gradient-to-br from-cyan-600 to-blue-700 text-white'}`}>
                <Bot className="w-4 h-4" />
              </div>
              <div>
                <h2 className={`text-xs font-bold tracking-tight ${isLightMode ? 'text-slate-950 font-mono' : 'text-white'}`}>ADK Remediation Agent</h2>
                <div className={`flex items-center space-x-1.5 text-[10px] ${isLightMode ? 'text-slate-700 font-mono font-bold' : 'text-cyan-400'}`}>
                  <Globe className="w-2.5 h-2.5" />
                  <span>Google Search Built-In</span>
                </div>
              </div>
            </div>
            <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${
              isLightMode
                ? 'bg-slate-200 text-slate-900 border-slate-400 font-bold'
                : 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30'
            }`}>
              gemini-3.5-flash
            </span>
          </div>

          {/* Active Context Banner */}
          {selectedError && (
            <div className={`px-3.5 py-2 border-b flex items-center justify-between text-[11px] ${
              isLightMode
                ? 'bg-slate-100 border-slate-200 text-slate-900'
                : 'bg-slate-900/70 border-slate-800/60 text-slate-300'
            }`}>
              <div className="flex items-center space-x-1.5 truncate">
                <Sparkles className={`w-3.5 h-3.5 flex-shrink-0 ${isLightMode ? 'text-slate-900' : 'text-cyan-400'}`} />
                <span className="truncate">Active Context: <strong className={isLightMode ? 'text-slate-950 font-bold' : 'text-cyan-300'}>{selectedError.serviceName}</strong></span>
              </div>
            </div>
          )}

          {/* Message Stream */}
          <div className={`flex-1 overflow-y-auto p-4 space-y-4 ${isLightMode ? 'bg-white' : ''}`}>
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
          <div className={`px-3.5 py-2 border-t ${
            isLightMode
              ? 'bg-slate-50 border-slate-200'
              : 'bg-slate-950/60 border-slate-800/60'
          }`}>
            <div className={`text-[10px] font-semibold mb-1.5 uppercase tracking-wider ${isLightMode ? 'text-slate-700 font-mono font-bold' : 'text-slate-400'}`}>
              Quick Inquiries
            </div>
            <div className="flex flex-col gap-1.5">
              {QUICK_SUGGESTIONS.map((sug, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSuggestionClick(sug)}
                  disabled={isSending}
                  className={`text-left text-[11px] px-2.5 py-1.5 rounded-lg border transition-all truncate cursor-pointer ${
                    isLightMode
                      ? 'bg-white hover:bg-slate-100 border-slate-300 text-slate-900 font-medium'
                      : 'bg-slate-900 hover:bg-slate-800 border-slate-800 text-slate-300 hover:text-white'
                  }`}
                >
                  {sug}
                </button>
              ))}
            </div>
          </div>

          {/* Input Bar */}
          <form onSubmit={handleSend} className={`p-3.5 border-t ${
            isLightMode
              ? 'bg-white border-slate-200'
              : 'bg-[#0e131d] border-slate-800/80'
          }`}>
            <div className="relative flex items-center">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask ADK Agent for fixes or Reddit search..."
                disabled={isSending}
                className={`w-full border rounded-xl py-2.5 pl-3.5 pr-10 text-xs focus:outline-none transition-all ${
                  isLightMode
                    ? 'bg-slate-50 border-slate-300 text-slate-950 placeholder-slate-500 focus:border-slate-950 font-medium'
                    : 'bg-slate-950/90 border-slate-800 text-slate-100 placeholder-slate-500 focus:border-cyan-500/70'
                }`}
              />
              <button
                type="submit"
                disabled={!input.trim() || isSending}
                className={`absolute right-1.5 p-1.5 rounded-lg text-white transition-all shadow-sm cursor-pointer ${
                  isLightMode
                    ? 'bg-slate-950 hover:bg-slate-800 disabled:opacity-40'
                    : 'bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 disabled:opacity-40'
                }`}
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
