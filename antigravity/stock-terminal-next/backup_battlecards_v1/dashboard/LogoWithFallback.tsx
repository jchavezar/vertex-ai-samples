import React from 'react';
import { Banana, Zap } from 'lucide-react';

interface LogoWithFallbackProps {
  ticker: string;
  className?: string;
}

const LogoWithFallback: React.FC<LogoWithFallbackProps> = ({ ticker, className }) => {
  const [error, setError] = React.useState(false);

  if (error) {
    return (
      <div className={`${className} flex flex-col items-center justify-center bg-gradient-to-br from-emerald-500/20 via-yellow-500/20 to-emerald-500/20 rounded-2xl border border-yellow-500/40 overflow-hidden relative group/logo shadow-[0_0_30px_rgba(234,179,8,0.2)] backdrop-blur-xl`}>
        <div className="absolute inset-0 bg-gradient-to-tr from-yellow-400/10 to-transparent animate-pulse" />
        <div className="relative flex flex-col items-center gap-1">
          <div className="relative p-3 rounded-full bg-black/40 border border-yellow-500/30 group-hover/logo:scale-110 transition-transform duration-500">
            <Banana className="text-yellow-400 w-12 h-12 filter drop-shadow-[0_0_12px_rgba(234,179,8,0.6)]" />
            <div className="absolute top-0 right-0 p-1 bg-emerald-500 rounded-full animate-bounce shadow-[0_0_10px_rgba(16,185,129,0.5)]">
              <Zap size={8} className="text-white" />
            </div>
          </div>
          <div className="flex flex-col items-center">
            <span className="text-[8px] font-black text-white tracking-[0.3em] uppercase opacity-90">Nanobanana</span>
            <span className="text-[6px] font-bold text-emerald-400 tracking-widest uppercase opacity-60">Architect v2.1</span>
          </div>
        </div>
        <div className="absolute -inset-full bg-gradient-to-r from-transparent via-white/10 to-transparent skew-x-12 animate-shimmer" />
      </div>
    );
  }

  return (
    <img
      src={`/assets/${ticker.toLowerCase()}_3d_icon.png`}
      onError={() => setError(true)}
      className={className}
      alt={ticker}
    />
  );
};

export default React.memo(LogoWithFallback);
