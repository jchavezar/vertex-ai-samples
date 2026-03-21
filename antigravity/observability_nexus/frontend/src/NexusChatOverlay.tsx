import React, { useState, useRef, useEffect } from 'react';
import { Bot, X, Send, Network, Maximize2, Minimize2, Minus } from 'lucide-react';

interface ComponentProps {
  logs: any[];
}

export default function NexusChatOverlay({ logs }: ComponentProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [isMaximized, setIsMaximized] = useState(false);
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant', content: string }[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Dragging state
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const dragStartRef = useRef({ x: 0, y: 0 });
  const positionRef = useRef({ x: 0, y: 0 });

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isOpen, isMinimized, isMaximized]);

  // Reset position if closed
  useEffect(() => {
    if (!isOpen) {
      setPosition({ x: 0, y: 0 });
      positionRef.current = { x: 0, y: 0 };
      setIsMaximized(false);
      setIsMinimized(false);
    }
  }, [isOpen]);

  // Pointer event handlers for native dragging
  const handlePointerDown = (e: React.PointerEvent) => {
    if ((e.target as HTMLElement).closest('button')) return;
    if (isMaximized) return;

    setIsDragging(true);
    dragStartRef.current = {
      x: e.clientX - positionRef.current.x,
      y: e.clientY - positionRef.current.y
    };
    (e.target as HTMLElement).setPointerCapture(e.pointerId);
  };
  
  const handlePointerMove = (e: React.PointerEvent) => {
    if (!isDragging || isMaximized) return;
    const newX = e.clientX - dragStartRef.current.x;
    const newY = e.clientY - dragStartRef.current.y;
    positionRef.current = { x: newX, y: newY };
    setPosition({ x: newX, y: newY });
  };
  
  const handlePointerUp = (e: React.PointerEvent) => {
    setIsDragging(false);
    (e.target as HTMLElement).releasePointerCapture(e.pointerId);
  };

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
        <div 
          className={`fixed z-50 overflow-hidden flex flex-col transition-[width,height,inset,border-radius] duration-200 
            ${isMaximized ? 'inset-4 w-auto h-auto rounded-2xl' : 'bottom-6 right-6 rounded-2xl'} 
            ${!isMaximized && isMinimized ? 'w-[28rem] h-[58px] min-h-0' : (!isMaximized ? 'w-[28rem] h-[40rem] min-w-[24rem] min-h-[30rem] max-w-[90vw] max-h-[90vh] resize' : 'resize-none')} 
            bg-[#0a101d]/90 border border-white/20 shadow-2xl backdrop-blur-3xl animate-in fade-in slide-in-from-bottom-8`}
          style={!isMaximized ? { transform: `translate(${position.x}px, ${position.y}px)` } : {}}
        >
          
          {/* Header */}
          <div 
            className={`p-4 border-b border-white/10 flex items-center justify-between bg-white/5 shrink-0 select-none ${!isMaximized ? (isDragging ? 'cursor-grabbing' : 'cursor-grab') : 'cursor-default'}`}
            onPointerDown={handlePointerDown}
            onPointerMove={handlePointerMove}
            onPointerUp={handlePointerUp}
          >
            <div className="flex items-center space-x-2 pointer-events-none">
              <Bot className="text-emerald-400" size={20} />
              <h3 className="text-white font-medium text-sm tracking-wide">Nexus Analytics Agent</h3>
            </div>
            <div className="flex items-center space-x-2">
               <button onClick={() => { setIsMinimized(!isMinimized); setIsMaximized(false); }} className="text-slate-400 hover:text-white transition-colors p-1" title="Minimize">
                 <Minus size={16} />
               </button>
               {!isMinimized && (
                 <button onClick={() => setIsMaximized(!isMaximized)} className="text-slate-400 hover:text-white transition-colors p-1" title={isMaximized ? "Restore" : "Maximize"}>
                   {isMaximized ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
                 </button>
               )}
               <button onClick={() => setIsOpen(false)} className="text-slate-400 hover:text-red-400 transition-colors p-1 ml-1" title="Close">
                 <X size={18} />
               </button>
            </div>
          </div>

          {!isMinimized && (
            <>
              {/* Chat History */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar bg-[#050a14]/50">
                {messages.length === 0 && (
                  <div className="h-full flex flex-col items-center justify-center text-slate-500 opacity-50 space-y-3">
                    <Network size={32} />
                    <p className="text-xs text-center px-6">Ask me anything about the raw logs and incidents currently tracking in the system. I have access to search grounding.</p>
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
            </>
          )}

        </div>
      )}
    </>
  );
}
