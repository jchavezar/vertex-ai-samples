import React, { useState, useRef, useEffect } from 'react';
import { Bot, X, Send, Network } from 'lucide-react';

interface ComponentProps {
  logs: any[];
}

export default function NexusChatOverlay({ logs }: ComponentProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant', content: string }[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: userMessage,
          logs: logs
        })
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      setMessages(prev => [...prev, { role: 'assistant', content: '' }]);
      
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let assistantMessage = '';

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          
          const chunk = decoder.decode(value, { stream: true });
          assistantMessage += chunk;
          
          setMessages(prev => {
            const newMessages = [...prev];
            newMessages[newMessages.length - 1].content = assistantMessage;
            return newMessages;
          });
        }
      }

    } catch (error) {
      console.error('Error during chat stream:', error);
      setMessages(prev => [...prev, { role: 'assistant', content: 'Connection error while communicating with Nexus Intelligence.'}]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* Floating Action Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 p-4 rounded-full bg-emerald-500 hover:bg-emerald-400 shadow-[0_0_20px_rgba(16,185,129,0.4)] transition-all transform hover:scale-105 z-50 flex items-center justify-center group"
        >
          <Bot size={24} className="text-[#050a14]" />
        </button>
      )}

      {/* Expanded Chat Overlay */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 w-[28rem] h-[40rem] min-w-[24rem] min-h-[30rem] max-w-[90vw] max-h-[90vh] resize bg-[#0a101d] border border-white/10 rounded-2xl shadow-2xl flex flex-col z-50 overflow-hidden backdrop-blur-3xl animate-in slide-in-from-bottom-8">
          
          {/* Header */}
          <div className="p-4 border-b border-white/10 flex items-center justify-between bg-white/5 shrink-0">
            <div className="flex items-center space-x-2">
              <Bot className="text-emerald-400" size={20} />
              <h3 className="text-white font-medium text-sm tracking-wide">Nexus Analytics Agent</h3>
            </div>
            <button 
              onClick={() => setIsOpen(false)}
              className="text-slate-400 hover:text-white transition-colors p-1"
            >
              <X size={18} />
            </button>
          </div>

          {/* Chat History */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar bg-[#050a14]/50">
            {messages.length === 0 && (
              <div className="h-full flex flex-col items-center justify-center text-slate-500 opacity-50 space-y-3">
                <Network size={32} />
                <p className="text-xs text-center">Ask me anything about the raw logs and incidents currently tracking in the system.</p>
              </div>
            )}
            
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div 
                  className={`max-w-[85%] rounded-lg p-3 text-sm ${
                    msg.role === 'user' 
                    ? 'bg-emerald-500/20 text-emerald-100 border border-emerald-500/30' 
                    : 'bg-white/10 text-slate-200 border border-white/5'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            ))}
            {isLoading && messages[messages.length - 1]?.role !== 'assistant' && (
              <div className="flex justify-start">
                  <div className="bg-white/10 border border-white/5 rounded-lg py-2 px-4 shadow-sm">
                    <div className="flex space-x-1.5 items-center h-4">
                      <div className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-bounce"></div>
                      <div className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-bounce" style={{animationDelay: '150ms'}}></div>
                      <div className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-bounce" style={{animationDelay: '300ms'}}></div>
                    </div>
                  </div>
                </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-4 border-t border-white/10 bg-[#0a101d] shrink-0">
            <form onSubmit={handleSubmit} className="relative flex items-center">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Query telemetry feed (context & search)..."
                className="w-full bg-[#050a14] border border-white/10 rounded-lg pl-3 pr-10 py-2.5 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500/50 transition-colors"
                disabled={isLoading}
              />
              <button 
                type="submit"
                disabled={!input.trim() || isLoading}
                className="absolute right-2 text-slate-400 hover:text-emerald-400 transition-colors disabled:opacity-50 disabled:hover:text-slate-400"
              >
                <Send size={18} />
              </button>
            </form>
          </div>

        </div>
      )}
    </>
  );
}
