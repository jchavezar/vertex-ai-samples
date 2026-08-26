import React, { useState } from 'react';
import { Send, Bot, User, Sparkles, Loader2 } from 'lucide-react';

export default function AskAIAssistant() {
  const [messages, setMessages] = useState([
    {
      sender: 'ai',
      text: "Hello! I'm your Gemini 2.5 Expense Intelligence Assistant. Ask me anything about your July spending, cardholder comparisons, top delivery apps, luxury purchases, or budget optimization!"
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async (e) => {
    e?.preventDefault();
    if (!input.trim() || loading) return;

    const userText = input.trim();
    setInput('');
    setMessages(prev => [...prev, { sender: 'user', text: userText }]);
    setLoading(true);

    try {
      const res = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userText })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { sender: 'ai', text: data.reply || "I analyzed your dataset and processed your query." }]);
    } catch (err) {
      setMessages(prev => [...prev, { sender: 'ai', text: "Sorry, I couldn't reach the AI backend server. Make sure port 8001 is running!" }]);
    } finally {
      setLoading(false);
    }
  };

  const sampleQuestions = [
    "How much did we spend on food delivery apps?",
    "Compare Alexander vs Elena vs Marcus spending breakdown",
    "What were our top 3 single largest purchases?",
    "Analyze our total fashion & luxury spending",
    "How much money was returned in refunds?"
  ];

  return (
    <div className="max-w-4xl mx-auto h-[650px] flex flex-col rounded-2xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-xl overflow-hidden">
      {/* Header */}
      <div className="p-4 bg-slate-950/80 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              Gemini Expense Assistant
              <span className="px-2 py-0.5 text-[10px] font-semibold rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">Live AI</span>
            </h3>
            <p className="text-xs text-slate-400">Natural language spending analytics & Q&A</p>
          </div>
        </div>
      </div>

      {/* Suggested Questions */}
      <div className="p-3 bg-slate-950/40 border-b border-slate-800/60 flex items-center gap-2 overflow-x-auto">
        <span className="text-[11px] font-semibold text-slate-400 whitespace-nowrap">Try asking:</span>
        {sampleQuestions.map((q, idx) => (
          <button
            key={idx}
            onClick={() => { setInput(q); }}
            className="text-[11px] bg-slate-800/60 hover:bg-slate-800 text-slate-300 px-2.5 py-1 rounded-lg border border-slate-700/50 whitespace-nowrap transition-colors cursor-pointer"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 p-4 overflow-y-auto space-y-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex items-start gap-3 ${msg.sender === 'user' ? 'flex-row-reverse' : ''}`}>
            <div className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 text-xs font-bold ${
              msg.sender === 'user' ? 'bg-indigo-600 text-white' : 'bg-amber-500/10 border border-amber-500/20 text-amber-400'
            }`}>
              {msg.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>

            <div className={`p-4 rounded-2xl max-w-xl text-xs leading-relaxed ${
              msg.sender === 'user'
                ? 'bg-indigo-600/30 text-slate-100 border border-indigo-500/40 rounded-tr-none'
                : 'bg-slate-950/80 text-slate-200 border border-slate-800/80 rounded-tl-none whitespace-pre-line'
            }`}>
              {msg.text}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center">
              <Loader2 className="w-4 h-4 animate-spin" />
            </div>
            <div className="p-3 rounded-2xl bg-slate-950/80 border border-slate-800 text-xs text-slate-400 animate-pulse">
              Gemini 2.5 is thinking and querying expense records...
            </div>
          </div>
        )}
      </div>

      {/* Input Form */}
      <form onSubmit={handleSend} className="p-4 bg-slate-950/80 border-t border-slate-800 flex items-center gap-2">
        <input
          type="text"
          placeholder="Ask AI anything about your expenses..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 bg-slate-900 text-xs text-slate-200 px-4 py-3 rounded-xl border border-slate-800 focus:outline-none focus:border-amber-500/50"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="px-5 py-3 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-slate-950 font-bold text-xs flex items-center gap-1.5 disabled:opacity-50 transition-all cursor-pointer"
        >
          <Send className="w-4 h-4" /> Send
        </button>
      </form>
    </div>
  );
}
