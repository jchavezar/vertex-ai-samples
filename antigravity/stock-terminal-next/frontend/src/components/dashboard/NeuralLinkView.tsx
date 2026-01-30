
import { useEffect, useState } from 'react';
import { useDashboardStore } from '../../store/dashboardStore';
import { ArrowLeft, Brain, Globe, Clock, ExternalLink, Zap, Activity, Youtube } from 'lucide-react';
import { NewsHubView } from './NewsHubView';
import clsx from 'clsx';

interface NeuralCard {
  title: string;
  snippet: string;
  source: string;
  url: string;
  sentiment: 'Positive' | 'Negative' | 'Neutral';
  timestamp?: string;
}

interface RumorCard {
    source: string;
    content: string;
    impact: 'High' | 'Medium' | 'Low';
    vibe: string;
    url?: string;
}

interface NeuralTrends {
  ticker: string;
  summary: string;
  cards: NeuralCard[];
    rumors: RumorCard[];
    market_vibe: string;
}

export const NeuralLinkView = () => {
  const { ticker, theme, setCurrentView } = useDashboardStore();
  const [data, setData] = useState<NeuralTrends | null>(null);
  const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<'news' | 'pulse' | 'news-hub'>('news');
  const isDark = theme === 'dark';

  useEffect(() => {
    const fetchTrends = async () => {
      try {
        const res = await fetch(`${import.meta.env.VITE_API_URL}/neural_link/trends/${ticker}`);
        const data = await res.json();
        setData(data);
        setLoading(false);
      } catch (e) {
        console.error("Failed to fetch trends", e);
        setLoading(false);
      }
    };
    
    fetchTrends();
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
                                      {data?.market_vibe || "NEUTRAL"}
                         </div>
                    </div>
                    {/* Animated Background Ring */}
                    <div className="absolute inset-0 rounded-full border-[20px] border-cyan-500/5 blur-3xl animate-blob" />
                </div>
            </div>

                      {/* Tabs */}
                      <div className="flex items-center gap-4 border-b border-white/10 pb-4">
                          <button
                              onClick={() => setActiveTab('news')}
                              className={clsx(
                                  "px-4 py-2 rounded-full text-sm font-bold transition-all flex items-center gap-2",
                                  activeTab === 'news'
                                      ? "bg-cyan-500 text-white shadow-lg shadow-cyan-500/20"
                                      : "text-gray-500 hover:text-gray-300 hover:bg-white/5"
                              )}
                          >
                              <Globe size={14} /> Global Signals
                          </button>
                          <button
                              onClick={() => setActiveTab('pulse')}
                              className={clsx(
                                  "px-4 py-2 rounded-full text-sm font-bold transition-all flex items-center gap-2",
                                  activeTab === 'pulse'
                                      ? "bg-purple-600 text-white shadow-lg shadow-purple-500/20"
                                      : "text-gray-500 hover:text-gray-300 hover:bg-white/5"
                              )}
                          >
                              <Zap size={14} /> Social Pulse
                          </button>
                          <button
                              onClick={() => setActiveTab('news-hub')}
                              className={clsx(
                                  "px-4 py-2 rounded-full text-sm font-bold transition-all flex items-center gap-2",
                                  activeTab === 'news-hub'
                                      ? "bg-red-600 text-white shadow-lg shadow-red-500/20"
                                      : "text-gray-500 hover:text-gray-300 hover:bg-white/5"
                              )}
                          >
                              <Youtube size={14} /> SemiAI News Hub
                          </button>
                      </div>

                      {/* Content Logic */}
                      {activeTab === 'news' ? (
                          <div>
                              <h3 className="text-[10px] font-black tracking-[0.2em] uppercase text-gray-500 mb-6 flex items-center gap-2">
                                  <Activity size={12} className="text-cyan-400" /> NEWS SECTOR
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
                                              {card.url && (
                                                  <a
                                                      href={card.url}
                                                      target="_blank"
                                                      rel="noreferrer"
                                                      className="p-2 rounded-full bg-white/5 hover:bg-cyan-500 hover:text-white transition-all text-gray-400"
                                                  >
                                                      <ExternalLink size={14} />
                                                  </a>
                                              )}
                                          </div>
                                      </div>
                                  ))}
                              </div>
                          </div>
                      ) : activeTab === 'pulse' ? (
                          <div className="space-y-6">
                              <h3 className="text-[10px] font-black tracking-[0.2em] uppercase text-gray-500 mb-6 flex items-center gap-2">
                                  <Zap size={12} className="text-purple-400" /> SOCIAL RUMOR MILL
                              </h3>
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                  {data?.rumors && data.rumors.length > 0 ? data.rumors.map((rumor, idx) => (
                                      <div
                                          key={idx}
                                          className={clsx(
                                              "p-5 rounded-2xl border transition-all duration-300 relative group overflow-hidden",
                                              isDark ? "bg-purple-900/5 border-purple-500/10 hover:border-purple-500/30 shadow-xl shadow-purple-900/5" : "bg-white border-purple-100 shadow-lg"
                                          )}
                                      >
                                          <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition-opacity">
                                              <Zap size={40} className="text-purple-500" />
                                          </div>

                                          <div className="flex items-center gap-3 mb-3">
                                              <div className="px-2 py-0.5 rounded bg-purple-500/20 text-purple-400 text-[10px] font-black uppercase tracking-tighter">
                                                  {rumor.source}
                                              </div>
                                              <div className={clsx(
                                                  "px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-tighter",
                                                  rumor.impact === 'High' ? "bg-red-500/20 text-red-500" :
                                                      rumor.impact === 'Medium' ? "bg-orange-500/20 text-orange-500" : "bg-blue-500/20 text-blue-500"
                                              )}>
                                                  IMPACT: {rumor.impact}
                                              </div>
                                              <div className="ml-auto text-[10px] font-bold text-gray-600 flex items-center gap-1 italic">
                                                  #{rumor.vibe}
                                              </div>
                                          </div>

                                          <p className={clsx("text-base leading-relaxed mb-4", isDark ? "text-gray-200 font-medium" : "text-gray-800")}>
                                              "{rumor.content}"
                                          </p>

                                          {rumor.url && (
                                              <a
                                                  href={rumor.url}
                                                  target="_blank"
                                                  rel="noreferrer"
                                                  className="text-xs text-purple-400 hover:text-purple-300 flex items-center gap-1 font-bold group/link"
                                              >
                                                  Inspect Source <ExternalLink size={10} className="group-hover/link:translate-x-0.5 transition-transform" />
                                              </a>
                                          )}
                                      </div>
                                  )) : (
                                      <div className="col-span-full py-20 flex flex-col items-center justify-center text-gray-500 gap-4 opacity-50">
                                          <Zap size={40} />
                                          <p className="font-mono text-xs tracking-[0.3em]">NO ACTIVE RUMORS DETECTED</p>
                                      </div>
                                  )}
                              </div>
                          </div>
                          ) : (
                              <NewsHubView />
                      )}
        </div>
      )}
    </div>
  );
};
