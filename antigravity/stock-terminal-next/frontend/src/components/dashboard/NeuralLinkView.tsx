
import React, { useEffect, useState } from 'react';
import { useDashboardStore } from '../../store/dashboardStore';
import { ArrowLeft, Brain, TrendingUp, Globe, Clock, ExternalLink, Zap, Activity } from 'lucide-react';
import clsx from 'clsx';
import { SimpleChart } from '../dashboard/SimpleChart'; // Reuse existing simple chart if available or similar

interface NeuralCard {
  title: string;
  snippet: string;
  source: string;
  url: string;
  sentiment: 'Positive' | 'Negative' | 'Neutral';
  timestamp?: string;
}

interface NeuralTrends {
  ticker: string;
  summary: string;
  cards: NeuralCard[];
}

export const NeuralLinkView = () => {
  const { ticker, theme, setCurrentView } = useDashboardStore();
  const [data, setData] = useState<NeuralTrends | null>(null);
  const [loading, setLoading] = useState(true);
  const isDark = theme === 'dark';

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const res = await fetch(`http://localhost:8001/neural_link/trends/${ticker}`);
        const json = await res.json();
        setData(json);
      } catch (err) {
        console.error("Neural Link Fetch Error", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [ticker]);

  return (
    <div className={clsx("min-h-full p-8 flex flex-col gap-6", isDark ? "bg-[#0A0A0B]" : "bg-gray-50")}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4 animate-fade-in-down">
        <div className="flex items-center gap-4">
            <button 
                onClick={() => setCurrentView('dashboard')}
                className={clsx(
                    "p-2 rounded-xl transition-all duration-300 hover:scale-105",
                    isDark ? "bg-white/5 hover:bg-white/10 text-gray-300" : "bg-white hover:bg-gray-100 text-gray-600 shadow-sm"
                )}
            >
                <ArrowLeft size={20} />
            </button>
            <div>
                <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-500 flex items-center gap-2">
                    <Brain className="text-cyan-400" />
                    Neural Link <span className="text-sm font-normal text-gray-500 ml-2 uppercase tracking-widest">Global Intelligence</span>
                </h1>
                <p className={clsx("text-sm mt-1 flex items-center gap-2", isDark ? "text-gray-400" : "text-gray-500")}>
                    <Activity size={14} className="text-green-400" />
                    Live Analysis for <span className="font-bold text-white bg-blue-600 px-2 py-0.5 rounded-md mx-1">{ticker}</span>
                </p>
            </div>
        </div>
      </div>

      {loading ? (
        <div className="flex-1 flex flex-col items-center justify-center gap-4 animate-pulse">
            <div className="w-16 h-16 rounded-full border-4 border-cyan-500/30 border-t-cyan-500 animate-spin" />
            <p className="text-cyan-400 font-mono text-sm tracking-widest">ESTABLISHING NEURAL LINK...</p>
        </div>
      ) : (
        <div className="flex flex-col gap-8 animate-fade-in-up">
            {/* Top Section: Summary & Chart Placeholder */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* AI Summary Card */}
                <div className={clsx(
                    "col-span-1 lg:col-span-2 p-6 rounded-3xl border backdrop-blur-xl relative overflow-hidden group",
                    isDark ? "bg-white/5 border-white/10" : "bg-white border-white/40 shadow-xl shadow-blue-900/5"
                )}>
                    <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-purple-500/5 group-hover:opacity-100 transition-opacity opacity-50" />
                    <div className="relative z-10">
                        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                            <Zap size={18} className="text-yellow-400" />
                            Trend Synthesis
                        </h2>
                        <p className={clsx("text-lg leading-relaxed", isDark ? "text-gray-200" : "text-slate-700")}>
                            {data?.summary}
                        </p>
                    </div>
                </div>

                 {/* Sentiment Gauge (Visual Only) */}
                 <div className={clsx(
                    "col-span-1 p-6 rounded-3xl border backdrop-blur-xl flex flex-col items-center justify-center relative overflow-hidden",
                    isDark ? "bg-white/5 border-white/10" : "bg-white border-white/40 shadow-xl shadow-blue-900/5"
                )}>
                    <div className="text-center z-10">
                         <span className="text-xs font-bold tracking-widest uppercase text-gray-500 mb-2 block animate-pulse">Market Vibe</span>
                         <div className="text-5xl font-black bg-clip-text text-transparent bg-gradient-to-tr from-green-400 to-cyan-500">
                            {data?.cards?.[0]?.sentiment || "NEUTRAL"}
                         </div>
                    </div>
                    {/* Animated Background Ring */}
                    <div className="absolute inset-0 rounded-full border-[20px] border-cyan-500/5 blur-3xl animate-blob" />
                </div>
            </div>

            {/* Cards Grid */}
            <div>
                 <h3 className="text-sm font-bold tracking-widest uppercase text-gray-500 mb-6 flex items-center gap-2">
                    <Globe size={14} /> Global Signals
                 </h3>
                 <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                    {data?.cards.map((card, idx) => (
                        <div 
                            key={idx}
                            className={clsx(
                                "p-6 rounded-2xl border backdrop-blur-md transition-all duration-500 hover:-translate-y-2 hover:shadow-2xl group flex flex-col justify-between h-full",
                                isDark ? "bg-white/5 border-white/10 hover:shadow-cyan-900/20 hover:border-cyan-500/30" : "bg-white border-gray-100 hover:shadow-blue-200/50"
                            )}
                            style={{ animationDelay: `${idx * 100}ms` }}
                        >
                            <div>
                                <div className="flex justify-between items-start mb-4">
                                    <span className={clsx(
                                        "px-2 py-1 rounded-md text-[10px] font-bold uppercase tracking-wide",
                                        card.sentiment === 'Positive' ? "bg-green-500/20 text-green-400" :
                                        card.sentiment === 'Negative' ? "bg-red-500/20 text-red-400" : "bg-gray-500/20 text-gray-400"
                                    )}>
                                        {card.sentiment}
                                    </span>
                                    <span className="text-[10px] text-gray-500 flex items-center gap-1">
                                        <Clock size={10} />
                                        {card.timestamp || 'Just now'}
                                    </span>
                                </div>
                                <h4 className={clsx("font-bold text-lg mb-3 line-clamp-2 group-hover:text-cyan-400 transition-colors", isDark ? "text-gray-100" : "text-gray-800")}>
                                    {card.title}
                                </h4>
                                <p className={clsx("text-sm line-clamp-3 mb-4", isDark ? "text-gray-400" : "text-gray-600")}>
                                    {card.snippet}
                                </p>
                            </div>
                            
                            <div className="flex items-center justify-between pt-4 border-t border-white/5 mt-auto">
                                <span className={clsx("text-xs font-semibold", isDark ? "text-gray-500" : "text-slate-500")}>
                                    {card.source}
                                </span>
                                <a 
                                    href={card.url} 
                                    target="_blank" 
                                    rel="noreferrer"
                                    className="p-2 rounded-full bg-white/5 hover:bg-cyan-500 hover:text-white transition-all text-gray-400"
                                >
                                    <ExternalLink size={14} />
                                </a>
                            </div>
                        </div>
                    ))}
                 </div>
            </div>
        </div>
      )}
    </div>
  );
};
