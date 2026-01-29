import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { useDashboardStore } from '../store/dashboardStore';
import { ModelSelector } from './ModelSelector';
import { ThemeToggle } from './ui/ThemeToggle';
import clsx from 'clsx';

export const DashboardHeader: React.FC = () => {
  const { ticker, tickerData } = useDashboardStore();
  
  const displayData = tickerData || {
    name: ticker,
    price: 0,
    currency: '$',
    change: 0,
    marketCap: 0,
    peRatio: 0,
    changePercent: 0
  };

  const name = displayData.name || ticker;
  const price = displayData.price || 0;
  const change = displayData.change || 0;
  const marketCap = displayData.marketCap || 0;
  const peRatio = displayData.peRatio || 0;
  const currency = displayData.currency || '$';

  return (
    <header className="bg-[var(--bg-card)] backdrop-blur-3xl border-b border-[var(--border)] px-6 py-3 grid grid-cols-3 items-center z-50 min-w-0">
      {/* Left: Ticker Identity */}
      <div className="flex items-center gap-3 justify-self-start">
        <div>
          <h1 className="text-2xl font-black leading-none flex items-baseline gap-2 tracking-tighter text-[var(--text-primary)]">
            {name.split(' ')[0]}
            {name.split(' ')[0] !== ticker && (
              <span className="text-xs bg-white/10 px-1.5 py-0.5 rounded-md text-[var(--text-secondary)] font-bold border border-white/10 translate-y-[-3px]">
                {ticker}
              </span>
            )}
          </h1>
          <div className="flex items-center gap-2 text-xs font-bold uppercase text-[var(--text-secondary)] mt-1 tracking-widest">
            <div className="w-2 h-2 bg-white rounded-full shadow-[0_0_8px_rgba(255,255,255,0.5)] animate-pulse" />
            Market Open • {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        </div>
      </div>

      {/* Center: Financial Data */}
      <div className="flex items-center gap-8 justify-self-center">
        <div>
          <div className="flex items-baseline justify-end gap-1 leading-none tracking-tighter text-right drop-shadow-sm">
            <span className="text-base font-bold text-[var(--text-muted)] translate-y-[-2px]">{currency}</span>
            <span className="text-3xl font-black text-[var(--text-primary)]">{price.toLocaleString()}</span>
          </div>
          <div className={clsx(
            "flex items-center justify-end gap-1.5 text-sm font-black mt-0.5",
            change > 0 ? "text-[var(--text-primary)]" : change < 0 ? "text-[var(--text-muted)]" : "text-[var(--text-muted)] opacity-50"
          )}>
            {change > 0 ? <TrendingUp size={16} /> : change < 0 ? <TrendingDown size={16} /> : <div className="w-3 h-px bg-current opacity-30" />}
            {displayData.changePercent !== undefined ? Math.abs(displayData.changePercent).toFixed(2) : '0.00'}%
          </div>
        </div>

        <div className="h-7 w-px bg-[var(--border)]" />

        <div className="flex flex-col">
          <span className="text-[9px] text-[var(--text-muted)] uppercase font-black tracking-widest mb-0.5">Market Cap</span>
          <span className="text-base font-black text-[var(--text-primary)]">
            {(marketCap / 1e9).toFixed(2)}B
          </span>
        </div>

        <div className="h-7 w-px bg-[var(--border)]" />

        <div className="flex flex-col">
          <span className="text-[9px] text-[var(--text-muted)] uppercase font-black tracking-widest mb-0.5">P/E Ratio</span>
          <span className="text-base font-black text-[var(--text-primary)]">
            {peRatio ? peRatio.toFixed(1) : '--'}
          </span>
        </div>
      </div>

      {/* Right: Model Selector & Theme Toggle */}
      <div className="justify-self-end flex items-center gap-3">
        <ThemeToggle />
        <ModelSelector />
      </div>
    </header>
  );
};