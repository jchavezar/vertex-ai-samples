import React from 'react';
import { TrendingUp, TrendingDown, Target, Zap } from 'lucide-react';
import { clsx } from 'clsx';

interface PeerData {
  ticker: string;
  name: string;
  sentiment: string;
  rating: string;
  price: number;
  target: number;
  upside: number;
}

interface PeerPackGridProps {
  peers: PeerData[];
  theme?: 'light' | 'dark';
}

export const PeerPackGrid: React.FC<PeerPackGridProps> = ({ peers, theme }) => {
  const isDark = theme === 'dark';

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6 animate-in slide-in-from-bottom-4 duration-700">
      {peers.map((peer, idx) => {
        const isPositive = peer.upside > 15;
        const progress = Math.min((peer.price / peer.target) * 100, 100);

        return (
          <div
            key={peer.ticker}
            className={clsx(
              "group relative overflow-hidden rounded-2xl border transition-all duration-300 hover:scale-[1.02] hover:shadow-xl",
              isDark 
                ? "bg-white/5 border-white/10 hover:bg-white/10 hover:border-blue-500/50" 
                : "bg-white border-slate-200 hover:border-blue-300 shadow-sm",
               `animate-in fade-in duration-500 delay-[${idx * 100}ms]`
            )}
          >
            {/* Sentiment Ring Background */}
            <div className={clsx(
              "absolute -right-4 -top-4 w-20 h-20 rounded-full blur-2xl opacity-20 transition-opacity group-hover:opacity-40",
              isPositive ? "bg-emerald-500" : "bg-blue-500"
            )} />

            <div className="p-4 relative">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h3 className={clsx("font-black tracking-tight text-lg leading-none", isDark ? "text-white" : "text-slate-900")}>
                    {peer.ticker}
                  </h3>
                  <p className="text-[10px] uppercase tracking-widest font-bold opacity-50 mt-1">{peer.name}</p>
                </div>
                <div className={clsx(
                  "px-2 py-1 rounded-full text-[9px] font-black uppercase tracking-tighter",
                  isPositive ? "bg-emerald-500/10 text-emerald-500" : "bg-blue-500/10 text-blue-500"
                )}>
                  {peer.sentiment}
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between text-xs items-end">
                  <div className="flex flex-col">
                    <span className="text-[10px] opacity-50 font-bold">Consensus</span>
                    <span className="font-bold flex items-center gap-1 group-hover:text-blue-400 transition-colors">
                        <Zap size={10} className="text-amber-400" /> {peer.rating}
                    </span>
                  </div>
                  <div className="text-right flex flex-col items-end">
                    <span className="text-[10px] opacity-50 font-bold">Upside</span>
                    <span className={clsx("font-black text-sm flex items-center gap-0.5", isPositive ? "text-emerald-500" : "text-blue-500")}>
                      {isPositive ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                      {peer.upside}%
                    </span>
                  </div>
                </div>

                {/* Price Target Bar */}
                <div className="space-y-1">
                  <div className="flex justify-between text-[9px] font-bold opacity-40 uppercase">
                    <span>${peer.price}</span>
                    <span>Target: ${peer.target}</span>
                  </div>
                  <div className={clsx("h-1.5 w-full rounded-full overflow-hidden", isDark ? "bg-white/10" : "bg-slate-100")}>
                    <div 
                      className={clsx("h-full rounded-full transition-all duration-1000", isPositive ? "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" : "bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]")} 
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};
