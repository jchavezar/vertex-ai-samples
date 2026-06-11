import React, { useState, useRef, useEffect } from 'react';
import MascotBear from './planets/MascotBear';
import { Send, Sparkles } from './Icons';

const MOCK_ANSWERS = {
  default: "I'd love to help with that! At Up Digital, we customize SEO, Meta Ads, and AI Assistant strategies for your specific business. Would you like to schedule a quick call to discuss?",
  seo: "Our AI SEO strategy focuses on semantic authority. We analyze search intent using LLMs to cluster keywords, then build high-quality content at scale to outrank competitors. Average organic growth is 320%!",
  ads: "For Meta and Google Ads, we use custom models to test thousands of copy and design variations, achieving an average 5.2x ROAS for e-commerce brands.",
  maya: "I am Maya, Up Digital's AI Marketing Strategist! I'm trained on all our case studies, frameworks, and growth playbooks to help qualify leads and design strategies.",
  cost: "Our projects are custom-tailored. We usually start with a discovery phase. You can click 'Start Your Project' at the top to give us details and get a proposal!",
};

export const MayaAI = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'maya',
      text: "Hi! I'm Maya, Up Digital's AI marketing strategist. How can I help grow your business today?",
      time: 'Just now'
    }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleSend = (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = {
      id: messages.length + 1,
      sender: 'user',
      text: input,
      time: 'Just now'
    };

    setMessages(prev => [...prev, userMessage]);
    const query = input.toLowerCase();
    setInput('');
    setIsTyping(true);

    // Simulate Maya thinking
    setTimeout(() => {
      let replyText = MOCK_ANSWERS.default;
      if (query.includes('seo') || query.includes('search') || query.includes('rank')) {
        replyText = MOCK_ANSWERS.seo;
      } else if (query.includes('ad') || query.includes('facebook') || query.includes('google') || query.includes('roas')) {
        replyText = MOCK_ANSWERS.ads;
      } else if (query.includes('who are you') || query.includes('name') || query.includes('maya')) {
        replyText = MOCK_ANSWERS.maya;
      } else if (query.includes('price') || query.includes('cost') || query.includes('budget') || query.includes('charge')) {
        replyText = MOCK_ANSWERS.cost;
      }

      setMessages(prev => [...prev, {
        id: prev.length + 1,
        sender: 'maya',
        text: replyText,
        time: 'Just now'
      }]);
      setIsTyping(false);
    }, 1500);
  };

  return (
    <section id="ai-employees" className="relative py-24 bg-brand-dark border-t border-white/5 overflow-hidden">
      {/* Background Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full bg-brand-lime/5 filter blur-[100px] pointer-events-none z-0" />

      <div className="max-w-7xl mx-auto px-6 md:px-16 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          
          {/* Left: Mascot & Info */}
          <div className="lg:col-span-5 flex flex-col items-center lg:items-start text-center lg:text-left">
            <span className="text-[10px] font-black tracking-[0.3em] uppercase text-brand-lime block mb-3">
              Meet Maya
            </span>
            <h2 className="text-3xl md:text-5xl font-black text-white leading-[1.15] tracking-tight mb-6 uppercase">
              YOUR AI MARKETING STRATEGIST.
            </h2>
            
            {/* Mascot Wrapper with Floating Animation */}
            <div className="w-full max-w-[280px] md:max-w-[340px] aspect-[480/520] mb-6 animate-[llama-float_5s_ease-in-out_infinite_alternate] filter drop-shadow-[0_10px_30px_rgba(191,255,0,0.1)]">
              <MascotBear width="100%" height="100%" />
            </div>

            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-brand-lime/10 border border-brand-lime/20 text-brand-lime text-xs font-bold uppercase tracking-wider mb-4">
              <span className="w-2 h-2 rounded-full bg-brand-lime animate-ping" />
              Live Now · Available 24/7
            </div>
            <p className="text-white/60 text-sm leading-relaxed max-w-sm">
              Trained on all of Up Digital's marketing playbooks. Ask Maya about SEO growth, ad optimizations, or social media strategy.
            </p>
          </div>

          {/* Right: Chat Interface */}
          <div className="lg:col-span-7 w-full">
            <div className="bg-brand-dark-alt/50 border border-white/5 rounded-3xl overflow-hidden shadow-2xl flex flex-col h-[520px] backdrop-blur-xl">
              {/* Chat Header */}
              <div className="px-6 py-4 border-b border-white/5 flex items-center justify-between bg-black/40">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-brand-dark border border-white/10 overflow-hidden p-1">
                    <MascotBear width="100%" height="100%" />
                  </div>
                  <div>
                    <h4 className="text-white font-bold text-sm">Maya AI</h4>
                    <p className="text-brand-lime text-[10px] uppercase tracking-wider font-bold">Marketing Strategist</p>
                  </div>
                </div>
                <div className="p-2 bg-white/5 rounded-lg border border-white/5 text-white/40">
                  <Sparkles className="w-4 h-4 text-brand-lime" />
                </div>
              </div>

              {/* Chat Messages */}
              <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-4 no-scrollbar">
                {messages.map((msg) => (
                  <div 
                    key={msg.id}
                    className={`flex gap-3 max-w-[85%] ${msg.sender === 'user' ? 'self-end flex-row-reverse' : 'self-start'}`}
                  >
                    {msg.sender === 'maya' && (
                      <div className="w-8 h-8 rounded-full bg-brand-dark border border-white/10 overflow-hidden p-0.5 shrink-0">
                        <MascotBear width="100%" height="100%" />
                      </div>
                    )}
                    <div className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${msg.sender === 'user' ? 'bg-brand-lime text-brand-dark-alt font-medium rounded-tr-none' : 'bg-white/5 border border-white/5 text-white/80 rounded-tl-none'}`}>
                      {msg.text}
                    </div>
                  </div>
                ))}
                
                {isTyping && (
                  <div className="flex gap-3 max-w-[85%] self-start">
                    <div className="w-8 h-8 rounded-full bg-brand-dark border border-white/10 overflow-hidden p-0.5 shrink-0">
                      <MascotBear width="100%" height="100%" />
                    </div>
                    <div className="bg-white/5 border border-white/5 rounded-2xl rounded-tl-none px-4 py-3 flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-white/40 animate-bounce" style={{ animationDelay: '0ms' }} />
                      <span className="w-1.5 h-1.5 rounded-full bg-white/40 animate-bounce" style={{ animationDelay: '150ms' }} />
                      <span className="w-1.5 h-1.5 rounded-full bg-white/40 animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>

              {/* Chat Input */}
              <form onSubmit={handleSend} className="p-4 bg-black/40 border-t border-white/5 flex gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask Maya about SEO, Ads, or Strategy..."
                  className="flex-1 bg-white/5 border border-white/5 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-brand-lime/50 focus:bg-white/10 transition-all"
                />
                <button
                  type="submit"
                  className="p-3 bg-brand-lime hover:bg-brand-lime-hover text-brand-dark-alt rounded-xl transition-colors font-bold"
                >
                  <Send className="w-4 h-4" />
                </button>
              </form>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
};

export default MayaAI;
