import React from 'react';
import { Share2, Download, Plus, Bell, ChevronDown, TrendingUp, TrendingDown, Sun, Moon } from 'lucide-react';
import { useDashboardStore } from '../store/dashboardStore';
import { ModelSelector } from './ModelSelector';
import clsx from 'clsx';

export const DashboardHeader: React.FC = () => {
  const { ticker, tickerData, theme, toggleTheme } = useDashboardStore();
  
  const displayData = tickerData || {
    name: ticker,
    price: 0,
    currency: '$',
    change: 0,
    marketCap: 0,
    peRatio: 0
  };

  const name = displayData.name || ticker;
  const price = displayData.price || 0;
  const change = displayData.change || 0;
  const marketCap = displayData.marketCap || 0;
  const peRatio = displayData.peRatio || 0;
  const currency = displayData.currency || '$';

  return (
    <header className="bg-[var(--bg-card)] backdrop-blur-3xl border-b border-[var(--border)] px-6 py-3 flex items-center gap-6 z-50">
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 bg-[var(--brand-gradient)] text-white flex items-center justify-center rounded-full font-black text-base shadow-lg">
          {name.charAt(0)}
        </div>
        <div>
          <h1 className="text-lg font-black leading-none flex items-center gap-2 tracking-tighter text-[var(--text-primary)]">
            {name.split(' ')[0]}
            <span className="text-[10px] bg-white/5 px-3 py-0.5 rounded-full text-[var(--text-secondary)] font-bold border border-white/10">
              {ticker}
            </span>
          </h1>
          <div className="flex items-center gap-2 text-[9px] font-extrabold uppercase text-[var(--green)] mt-1.5 tracking-wider">
            <div className="w-2 h-2 bg-[var(--green)] rounded-full shadow-[0_0_10px_var(--green)] animate-pulse" />
            Market Open • {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        </div>
      </div>

      <div className="flex items-center gap-8 border-l border-[var(--border)] pl-8">
        <div>
          <div className="text-2xl font-black leading-none tracking-tighter text-[var(--text-primary)]">
            {currency} {price.toLocaleString()}
          </div>
          <div className={clsx(
            "flex items-center gap-1.5 text-xs font-black mt-1",
            change >= 0 ? "text-[var(--green)]" : "text-[var(--red)]"
          )}>
            {change >= 0 ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
            {change !== undefined ? change.toFixed(2) : '0.00'}%
          </div>
        </div>

        <div className="flex flex-col">
          <span className="text-[9px] text-[var(--text-muted)] uppercase font-black tracking-widest">Market Cap</span>
          <span className="text-sm font-black text-[var(--text-primary)]">
            {(marketCap / 1e9).toFixed(2)}B
          </span>
        </div>

        <div className="flex flex-col">
          <span className="text-[9px] text-[var(--text-muted)] uppercase font-black tracking-widest">P/E Ratio</span>
          <span className="text-sm font-black text-[var(--text-primary)]">
            {peRatio ? peRatio.toFixed(1) : '--'}
          </span>
        </div>
      </div>

      <div className="ml-auto flex gap-2">
        <div className="mr-4">
          <ModelSelector />
        </div>
        <button 
          onClick={toggleTheme}
          className="bg-blue-500/10 text-[var(--brand)] border border-blue-500/20 px-5 h-9 text-[10px] uppercase font-black tracking-wider flex items-center gap-2 rounded-full hover:bg-blue-500/20 transition-all"
        >
          {theme === 'dark' ? <Sun size={12} /> : <Moon size={12} />}
          {theme === 'dark' ? 'Light' : 'Dark'}
        </button>
        {[Share2, Bell, Plus, Download, ChevronDown].map((Icon, i) => (
          <button key={i} className="w-9 h-9 flex items-center justify-center rounded-full bg-white/5 border border-white/10 text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-white/10 hover:-translate-y-0.5 transition-all shadow-lg">
            <Icon size={14} />
          </button>
        ))}
      </div>
    </header>
  );
};