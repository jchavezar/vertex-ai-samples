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
    <div className="w-full h-full grid grid-cols-12 gap-8 items-center px-6">
      {/* TRADING */}
      <div className="col-span-3 flex flex-col justify-center h-full border-r border-[var(--border-subtle)] pr-6">
        <div className="text-[10px] font-bold text-[var(--text-muted)] tracking-[0.2em] mb-1.5 uppercase opacity-80 flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
          TRADING ACTIVITY
        </div>
        <div className="grid grid-cols-2 gap-x-4 gap-y-1">
          <div>
            <span className="block text-[10px] uppercase text-[var(--text-muted)] font-medium mb-0.5">Open</span>
            <span className="block text-base font-bold text-[var(--text-primary)] font-mono">{formatValue(tickerData?.price, '$')}</span>
          </div>
          <div>
            <span className="block text-[10px] uppercase text-[var(--text-muted)] font-medium mb-0.5">Volume</span>
            <span className="block text-base font-bold text-[var(--text-primary)] font-mono">1.2M</span>
          </div>
          <div>
            <span className="block text-[10px] uppercase text-[var(--text-muted)] font-medium mb-0.5">High</span>
            <span className="block text-base font-bold text-[var(--text-secondary)] font-mono">{formatValue(tickerData?.fiftyTwoWeekHigh, '$')}</span>
          </div>
          <div>
            <span className="block text-[10px] uppercase text-[var(--text-muted)] font-medium mb-0.5">Low</span>
            <span className="block text-base font-bold text-[var(--text-secondary)] font-mono">{formatValue(tickerData?.fiftyTwoWeekLow, '$')}</span>
          </div>
        </div>
      </div>

      {/* VALUATION */}
      <div className="col-span-3 flex flex-col justify-center h-full border-r border-[var(--border-subtle)] pr-6">
        <div className="text-[10px] font-bold text-[var(--text-muted)] tracking-[0.2em] mb-1.5 uppercase opacity-80 flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-purple-500"></span>
          VALUATION METRICS
        </div>
        <div className="grid grid-cols-2 gap-x-4 gap-y-1">
          <div>
            <span className="block text-[10px] uppercase text-[var(--text-muted)] font-medium mb-0.5">Mkt Cap</span>
            <span className="block text-base font-bold text-[var(--text-primary)] font-mono">{formatLargeNumber(tickerData?.marketCap)}</span>
          </div>
          <div>
            <span className="block text-[10px] uppercase text-[var(--text-muted)] font-medium mb-0.5">P/E Ratio</span>
            <span className="block text-base font-bold text-[var(--text-primary)] font-mono">{formatValue(tickerData?.peRatio)}</span>
          </div>
          <div>
            <span className="block text-[10px] uppercase text-[var(--text-muted)] font-medium mb-0.5">Beta</span>
            <span className="block text-base font-bold text-[var(--text-primary)] font-mono">1.12</span>
          </div>
          <div>
            <span className="block text-[10px] uppercase text-[var(--text-muted)] font-medium mb-0.5">EPS</span>
            <span className="block text-base font-bold text-[var(--text-primary)] font-mono">14.23</span>
          </div>
        </div>
      </div>

      {/* DIVIDENDS */}
      <div className="col-span-3 flex flex-col justify-center h-full border-r border-[var(--border-subtle)] pr-6">
        <div className="text-[10px] font-bold text-[var(--text-muted)] tracking-[0.2em] mb-1.5 uppercase opacity-80 flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
          DIVIDENDS & RETURNS
        </div>
        <div className="grid grid-cols-2 gap-x-4 gap-y-1">
          <div>
            <span className="block text-[10px] uppercase text-[var(--text-muted)] font-medium mb-0.5">Yield</span>
            <span className="block text-base font-bold text-emerald-400 font-mono">{tickerData?.dividendYield ? `${(tickerData.dividendYield * 100).toFixed(2)}%` : '1.48%'}</span>
          </div>
          <div>
            <span className="block text-[10px] uppercase text-[var(--text-muted)] font-medium mb-0.5">Payout</span>
            <span className="block text-base font-bold text-[var(--text-secondary)] font-mono">42%</span>
          </div>
          <div className="col-span-2">
            <span className="block text-[10px] uppercase text-[var(--text-muted)] font-medium mb-0.5">Ex-Div Date</span>
            <span className="block text-sm font-bold text-[var(--text-primary)] font-mono">Feb 14, 2025</span>
          </div>
        </div>
      </div>

      {/* ANALYST CONSENSUS */}
      <div className="col-span-3 flex flex-col justify-center h-full pl-2">
        <div className="h-full bg-[var(--bg-card)]/80 border border-[var(--border)] rounded-lg p-4 flex flex-col justify-center relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-2 opacity-50">
            <span className="w-2 h-2 rounded-full bg-emerald-500 block animate-pulse"></span>
          </div>

          <div className="flex items-center gap-3 mb-2">
            <div className="text-[10px] font-bold text-[var(--text-muted)] tracking-[0.2em] uppercase">ANALYST RATING</div>
            <div className="h-1 flex-1 bg-[var(--border-subtle)] rounded-full overflow-hidden max-w-[100px]">
              <div className="h-full w-[85%] bg-emerald-500 rounded-full"></div>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <span className="block text-[10px] uppercase text-[var(--text-muted)] font-medium mb-0.5">Consensus</span>
              <span className="block text-base font-black text-emerald-400 tracking-wide">BUY (4.2)</span>
            </div>
            <div className="text-right">
              <span className="block text-[10px] uppercase text-[var(--text-muted)] font-medium mb-0.5">Target</span>
              <div className="flex items-baseline gap-2 justify-end">
                <span className="block text-base font-black text-[var(--text-primary)] font-mono">$314</span>
                <span className="text-[10px] font-bold text-emerald-400 font-mono">+14%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
