import { useEffect, useState } from 'react';
import { useDashboardStore } from '../../store/dashboardStore';
import { Youtube, Trash2, Clock, Play, AlertCircle, RefreshCw, ExternalLink } from 'lucide-react';
import clsx from 'clsx';

interface VideoNews {
  id: string;
  title: string;
  url: string;
  thumbnail: string;
  duration: string;
  summary: string;
  company: string;
  snippet: string;
}

export const NewsHubView = () => {
  const { ticker, theme } = useDashboardStore();
  const [news, setNews] = useState<VideoNews[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const isDark = theme === 'dark';

  const fetchNews = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`http://localhost:8002/news_hub/${ticker}`);
      if (!res.ok) throw new Error("Failed to fetch news hub data");
      const data = await res.json();
      setNews(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const clearSession = async () => {
    if (!confirm("Clear this News Hub session and fetch fresh videos?")) return;

    try {
      await fetch(`http://localhost:8002/news_hub/${ticker}`, { method: 'DELETE' });
      setNews([]);
      fetchNews();
    } catch (err) {
      console.error("Clear Session Error", err);
    }
  };

  useEffect(() => {
    fetchNews();
  }, [ticker]);

  if (loading && news.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center py-20 gap-4">
        <div className="w-12 h-12 rounded-full border-2 border-red-500/30 border-t-red-500 animate-spin" />
        <p className="text-red-500 font-mono text-sm tracking-widest animate-pulse">SYNTHESIZING VIDEO DATA...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center py-20 gap-4 text-center">
        <AlertCircle size={48} className="text-red-500 opacity-50" />
        <p className="text-gray-400 max-w-md">{error}</p>
        <button
          onClick={() => fetchNews()}
          className="px-6 py-2 bg-red-500/10 text-red-500 border border-red-500/50 rounded-full hover:bg-red-500/20 transition-all font-bold"
        >
          Retry Connection
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 animate-fade-in">
      {/* Control Bar */}
      <div className="flex items-center justify-between">
        <h3 className="text-[10px] font-black tracking-[0.2em] uppercase text-gray-500 flex items-center gap-2">
          <Youtube size={12} className="text-red-500" /> SemiAI Video Intelligence
        </h3>
        <div className="flex items-center gap-2">
          <button
            onClick={() => fetchNews()}
            disabled={loading}
            className={clsx(
              "p-2 rounded-lg transition-all",
              isDark ? "hover:bg-white/5 text-gray-400 hover:text-white" : "hover:bg-gray-100 text-gray-600",
              loading && "animate-spin"
            )}
            title="Refresh"
          >
            <RefreshCw size={16} />
          </button>
          <button
            onClick={clearSession}
            className={clsx(
              "p-2 rounded-lg transition-all",
              isDark ? "hover:bg-red-500/10 text-gray-400 hover:text-red-400" : "hover:bg-red-50 hover:text-red-600"
            )}
            title="Clear Session Memory"
          >
            <Trash2 size={16} />
          </button>
        </div>
      </div>

      {news.length === 0 && !loading ? (
        <div className="py-20 flex flex-col items-center justify-center text-gray-500 gap-4 opacity-50">
          <Youtube size={40} />
          <p className="font-mono text-xs tracking-[0.3em]">NO RELEVANT VIDEOS FOUND FOR {ticker}</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
          {news.map((item, idx) => (
            <div
              key={item.id}
              className={clsx(
                "group rounded-3xl border overflow-hidden transition-all duration-500 hover:scale-[1.02] shadow-2xl",
                isDark ? "bg-[#111114] border-white/5 shadow-black/40" : "bg-white border-gray-100 shadow-blue-900/5"
              )}
              style={{ animationDelay: `${idx * 150}ms` }}
            >
              <div className="flex flex-col md:flex-row gap-6 p-6">
                {/* Thumbnail Container */}
                <div className="relative w-full md:w-56 h-36 rounded-2xl overflow-hidden shrink-0 group/img">
                  <img
                    src={item.thumbnail}
                    alt={item.title}
                    className="w-full h-full object-cover transition-transform duration-700 group-hover/img:scale-110"
                  />
                  <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover/img:opacity-100 transition-opacity">
                    <div className="w-12 h-12 rounded-full bg-red-600 flex items-center justify-center shadow-xl shadow-red-900/40">
                      <Play size={24} fill="white" className="ml-1" />
                    </div>
                  </div>
                  <div className="absolute bottom-2 right-2 px-2 py-0.5 bg-black/80 rounded text-[10px] font-bold text-white flex items-center gap-1">
                    <Clock size={10} /> {item.duration}
                  </div>
                  <a
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="absolute inset-0"
                  />
                </div>

                {/* Content */}
                <div className="flex flex-col gap-3 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded bg-red-500/10 text-red-500 text-[9px] font-bold uppercase tracking-widest">
                      {item.company}
                    </span>
                  </div>
                  <h4 className={clsx(
                    "font-bold text-lg leading-snug group-hover:text-red-500 transition-colors line-clamp-2",
                    isDark ? "text-gray-100" : "text-gray-800"
                  )}>
                    {item.title}
                  </h4>
                  <p className={clsx("text-sm line-clamp-3 leading-relaxed", isDark ? "text-gray-400" : "text-gray-600")}>
                    {item.summary}
                  </p>

                  {/* Snippet / Quote Box */}
                  <div className={clsx(
                    "mt-2 p-3 rounded-xl border-l-[3px] border-red-500/50",
                    isDark ? "bg-white/5" : "bg-red-50/30"
                  )}>
                    <p className={clsx("text-xs italic", isDark ? "text-gray-300" : "text-slate-700")}>
                      "{item.snippet}"
                    </p>
                  </div>

                  <div className="mt-auto pt-4 flex items-center justify-between">
                    <div className="flex items-center gap-1.5 opacity-50 group-hover:opacity-100 transition-opacity">
                      <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                      <span className="text-[10px] font-mono tracking-tighter uppercase">AI Synthesized</span>
                    </div>
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-xs font-bold text-red-500 hover:text-red-400 flex items-center gap-1 transition-colors"
                    >
                      Watch Full <ExternalLink size={10} />
                    </a>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
