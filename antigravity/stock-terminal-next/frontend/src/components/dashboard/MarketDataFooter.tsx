interface MarketDataFooterProps {
  tickerData?: any;
}

export const MarketDataFooter: React.FC<MarketDataFooterProps> = ({ tickerData }) => {
  const formatValue = (val: number | undefined, prefix = '', suffix = '', decimals = 2) => {
    if (val === undefined || val === null) return '-';
    return `${prefix}${Number(val).toFixed(decimals)}${suffix}`;
  };

  const formatLargeNumber = (num: number | undefined) => {
    if (!num) return '-';
    if (num >= 1e9) return `${(num / 1e9).toFixed(1)}B`;
    if (num >= 1e6) return `${(num / 1e6).toFixed(1)}M`;
    return num.toLocaleString();
  };

  return (
    <div className="w-full h-full grid grid-cols-12 gap-4 items-center px-4">
      {/* TRADING */}
      <div className="col-span-3 flex flex-col justify-center h-full border-r border-[var(--border-subtle)] pr-4">
        <div className="text-[9px] font-bold text-[var(--text-muted)] tracking-[0.2em] mb-1.5 uppercase opacity-80 flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
          TRADING
        </div>
        <div className="grid grid-cols-2 gap-x-2 gap-y-1">
          <div>
            <span className="block text-[9px] uppercase text-[var(--text-muted)] font-medium">Open</span>
            <span className="block text-sm font-bold text-[var(--text-primary)] font-mono">{formatValue(tickerData?.price, '$')}</span>
          </div>
          <div>
            <span className="block text-[9px] uppercase text-[var(--text-muted)] font-medium">Volume</span>
            <span className="block text-sm font-bold text-[var(--text-primary)] font-mono">1.2M</span>
          </div>
          <div>
            <span className="block text-[9px] uppercase text-[var(--text-muted)] font-medium">High</span>
            <span className="block text-sm font-bold text-[var(--text-secondary)] font-mono">{formatValue(tickerData?.fiftyTwoWeekHigh, '$')}</span>
          </div>
          <div>
            <span className="block text-[9px] uppercase text-[var(--text-muted)] font-medium">Low</span>
            <span className="block text-sm font-bold text-[var(--text-secondary)] font-mono">{formatValue(tickerData?.fiftyTwoWeekLow, '$')}</span>
          </div>
        </div>
      </div>

      {/* VALUATION */}
      <div className="col-span-3 flex flex-col justify-center h-full border-r border-[var(--border-subtle)] pr-4 pl-2">
        <div className="text-[9px] font-bold text-[var(--text-muted)] tracking-[0.2em] mb-1.5 uppercase opacity-80 flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-purple-500"></span>
          VALUATION
        </div>
        <div className="grid grid-cols-2 gap-x-2 gap-y-1">
          <div>
            <span className="block text-[9px] uppercase text-[var(--text-muted)] font-medium">Mkt Cap</span>
            <span className="block text-sm font-bold text-[var(--text-primary)] font-mono">{formatLargeNumber(tickerData?.marketCap)}</span>
          </div>
          <div>
            <span className="block text-[9px] uppercase text-[var(--text-muted)] font-medium">P/E Ratio</span>
            <span className="block text-sm font-bold text-[var(--text-primary)] font-mono">{formatValue(tickerData?.peRatio)}</span>
          </div>
          <div>
            <span className="block text-[9px] uppercase text-[var(--text-muted)] font-medium">Beta</span>
            <span className="block text-sm font-bold text-[var(--text-primary)] font-mono">1.12</span>
          </div>
          <div>
            <span className="block text-[9px] uppercase text-[var(--text-muted)] font-medium">EPS</span>
            <span className="block text-sm font-bold text-[var(--text-primary)] font-mono">14.23</span>
          </div>
        </div>
      </div>

      {/* DIVIDENDS */}
      <div className="col-span-3 flex flex-col justify-center h-full border-r border-[var(--border-subtle)] pr-4 pl-2">
        <div className="text-[9px] font-bold text-[var(--text-muted)] tracking-[0.2em] mb-1.5 uppercase opacity-80 flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
          DIVIDENDS
        </div>
        <div className="grid grid-cols-2 gap-x-2 gap-y-1">
          <div>
            <span className="block text-[9px] uppercase text-[var(--text-muted)] font-medium">Yield</span>
            <span className="block text-sm font-bold text-emerald-400 font-mono">
              {tickerData?.dividendYield ? formatValue(tickerData.dividendYield * 100, '', '%') : '1.48%'}
            </span>
          </div>
          <div>
            <span className="block text-[9px] uppercase text-[var(--text-muted)] font-medium">Payout</span>
            <span className="block text-sm font-bold text-[var(--text-secondary)] font-mono">42%</span>
          </div>
          <div className="col-span-2">
            <span className="block text-[9px] uppercase text-[var(--text-muted)] font-medium">Ex-Div Date</span>
            <span className="block text-xs font-bold text-[var(--text-primary)] font-mono">Feb 14, 2025</span>
          </div>
        </div>
      </div>

      {/* ANALYST CONSENSUS */}
      <div className="col-span-3 flex flex-col justify-center h-full pl-2">
        <div className="bg-[var(--bg-card)]/80 border border-[var(--border)] rounded-lg p-2 flex flex-col justify-center relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-1 opacity-50">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 block animate-pulse"></span>
          </div>

          <div className="flex items-center gap-2 mb-1">
            <div className="text-[9px] font-bold text-[var(--text-muted)] tracking-[0.2em] uppercase">RATING</div>
            <div className="h-1 flex-1 bg-[var(--border-subtle)] rounded-full overflow-hidden max-w-[60px]">
              <div className="h-full w-[85%] bg-emerald-500 rounded-full"></div>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <span className="block text-[9px] uppercase text-[var(--text-muted)] font-medium">Consensus</span>
              <span className="block text-sm font-black text-emerald-400 tracking-wide">BUY (4.2)</span>
            </div>
            <div className="text-right">
              <span className="block text-[9px] uppercase text-[var(--text-muted)] font-medium">Target</span>
              <div className="flex items-baseline gap-1 justify-end">
                <span className="block text-sm font-black text-[var(--text-primary)] font-mono">$314</span>
                <span className="text-[9px] font-bold text-emerald-400 font-mono">+14%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
