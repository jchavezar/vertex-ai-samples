import React from 'react';


interface MarketDataFooterProps {
  tickerData?: any;
}

export const MarketDataFooter: React.FC<MarketDataFooterProps> = ({ tickerData }) => {
  const formatValue = (val: number | undefined, prefix = '', suffix = '') => {
    if (val === undefined || val === null) return '-';
    return `${prefix}${val}${suffix}`;
  };

  const formatLargeNumber = (num: number | undefined) => {
    if (!num) return '-';
    if (num >= 1e9) return `${(num / 1e9).toFixed(1)}B`;
    if (num >= 1e6) return `${(num / 1e6).toFixed(1)}M`;
    return num.toLocaleString();
  };

  return (
    <div className="w-full h-full grid grid-cols-12 gap-4 items-center">
      {/* TRADING */}
      <div className="col-span-3 flex flex-col justify-center h-full border-r border-[var(--border-subtle)] px-4">
        <div className="text-[10px] font-bold text-[var(--text-muted)] tracking-[0.2em] mb-2 uppercase opacity-70">
          TRADING
        </div>
        <div className="grid grid-cols-2 gap-x-4 gap-y-1">
          <div>
            <span className="block text-[10px] uppercase text-[var(--text-muted)] font-medium">Open</span>
            <span className="block text-lg font-bold text-[var(--text-primary)] font-mono">{formatValue(tickerData?.price, '$')}</span>
          </div>
          <div>
            <span className="block text-[10px] uppercase text-[var(--text-muted)] font-medium">Vol</span>
            <span className="block text-lg font-bold text-[var(--text-primary)] font-mono">1.2M</span>
          </div>
          <div>
            <span className="block text-[10px] uppercase text-[var(--text-muted)] font-medium">High</span>
            <span className="block text-base font-bold text-[var(--text-secondary)] font-mono">{formatValue(tickerData?.fiftyTwoWeekHigh, '$')}</span>
          </div>
          <div>
            <span className="block text-[10px] uppercase text-[var(--text-muted)] font-medium">Low</span>
            <span className="block text-base font-bold text-[var(--text-secondary)] font-mono">{formatValue(tickerData?.fiftyTwoWeekLow, '$')}</span>
          </div>
        </div>
      </div>

      {/* VALUATION */}
      <div className="col-span-3 flex flex-col justify-center h-full border-r border-[var(--border-subtle)] px-4">
        <div className="text-[10px] font-bold text-[var(--text-muted)] tracking-[0.2em] mb-2 uppercase opacity-70">
          VALUATION
        </div>
        <div className="grid grid-cols-2 gap-x-4 gap-y-1">
          <div>
            <span className="block text-[10px] uppercase text-[var(--text-muted)] font-medium">Mkt Cap</span>
            <span className="block text-lg font-bold text-[var(--text-primary)] font-mono">{formatLargeNumber(tickerData?.marketCap)}</span>
          </div>
          <div>
            <span className="block text-[10px] uppercase text-[var(--text-muted)] font-medium">P/E</span>
            <span className="block text-lg font-bold text-[var(--text-primary)] font-mono">{formatValue(tickerData?.peRatio)}</span>
          </div>
          <div>
            <span className="block text-[10px] uppercase text-[var(--text-muted)] font-medium">Beta</span>
            <span className="block text-lg font-bold text-[var(--text-primary)] font-mono">1.12</span>
          </div>
          <div>
            <span className="block text-[10px] uppercase text-[var(--text-muted)] font-medium">EPS</span>
            <span className="block text-lg font-bold text-[var(--text-primary)] font-mono">14.23</span>
          </div>
        </div>
      </div>

      {/* DIVIDENDS */}
      <div className="col-span-3 flex flex-col justify-center h-full border-r border-[var(--border-subtle)] px-4">
        <div className="text-[10px] font-bold text-[var(--text-muted)] tracking-[0.2em] mb-2 uppercase opacity-70">
          DIVIDENDS
        </div>
        <div className="grid grid-cols-2 gap-x-4 gap-y-1">
          <div>
            <span className="block text-[10px] uppercase text-[var(--text-muted)] font-medium">Yield</span>
            <span className="block text-xl font-bold text-emerald-400 font-mono">{tickerData?.dividendYield ? `${(tickerData.dividendYield * 100).toFixed(2)}%` : '1.48%'}</span>
          </div>
          <div>
            <span className="block text-[10px] uppercase text-[var(--text-muted)] font-medium">Payout</span>
            <span className="block text-base font-bold text-[var(--text-secondary)] font-mono">42%</span>
          </div>
          <div className="col-span-2 flex items-baseline gap-2">
            <span className="block text-[10px] uppercase text-[var(--text-muted)] font-medium">Ex-Date:</span>
            <span className="block text-sm font-bold text-[var(--text-primary)] font-mono">Feb 14, 2025</span>
          </div>
        </div>
      </div>

      {/* ANALYST CONSENSUS */}
      <div className="col-span-3 flex flex-col justify-center h-full px-4 bg-[var(--bg-card)]/50">
        <div className="flex items-center gap-2 mb-2">
          <div className="text-[10px] font-bold text-[var(--text-muted)] tracking-[0.2em] uppercase opacity-70">
            CONSENSUS
          </div>
          <div className="h-1 flex-1 bg-[var(--border-subtle)] rounded-full overflow-hidden">
            <div className="h-full w-[80%] bg-emerald-500 rounded-full"></div>
          </div>
        </div>
        <div className="flex items-center justify-between">
          <div>
            <span className="block text-[10px] uppercase text-[var(--text-muted)] font-medium">Rating</span>
            <span className="block text-xl font-black text-emerald-400">BUY (4.2)</span>
          </div>
          <div>
            <span className="block text-[10px] uppercase text-[var(--text-muted)] font-medium text-right">Target</span>
            <span className="block text-xl font-black text-[var(--text-primary)] font-mono">$314.00</span>
          </div>
          <div>
            <span className="block text-[10px] uppercase text-[var(--text-muted)] font-medium text-right">Upside</span>
            <span className="block text-xl font-black text-emerald-400 font-mono">+14%</span>
          </div>
        </div>
      </div>
    </div>
  );
};
