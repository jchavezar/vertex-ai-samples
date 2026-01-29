import React from 'react';

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
    <div className="w-full h-full flex items-center justify-between px-6">
      {/* TRADING SECTION */}
      <div className="flex items-center gap-6 border-r border-[var(--border-subtle)] pr-8">
        <div className="flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]"></div>
          <span className="text-[10px] font-black text-[var(--text-muted)] tracking-[0.15em] uppercase">TRADING</span>
        </div>
        <div className="flex items-center gap-5">
          <DataItem label="OPEN" value={formatValue(tickerData?.price, '$')} />
          <DataItem label="VOL" value="1.2M" />
          <DataItem label="52W H" value={formatValue(tickerData?.fiftyTwoWeekHigh, '$')} dimmed />
          <DataItem label="52W L" value={formatValue(tickerData?.fiftyTwoWeekLow, '$')} dimmed />
        </div>
      </div>

      {/* VALUATION SECTION */}
      <div className="flex items-center gap-6 border-r border-[var(--border-subtle)] pr-8 pl-4">
        <div className="flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full bg-purple-500 shadow-[0_0_8px_rgba(168,85,247,0.5)]"></div>
          <span className="text-[10px] font-black text-[var(--text-muted)] tracking-[0.15em] uppercase">VALUATION</span>
        </div>
        <div className="flex items-center gap-5">
          <DataItem label="MKT CAP" value={formatLargeNumber(tickerData?.marketCap)} />
          <DataItem label="P/E" value={formatValue(tickerData?.peRatio)} />
          <DataItem label="BETA" value="1.12" />
          <DataItem label="EPS" value="14.23" />
        </div>
      </div>

      {/* DIVIDENDS SECTION */}
      <div className="flex items-center gap-6 border-r border-[var(--border-subtle)] pr-8 pl-4">
        <div className="flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></div>
          <span className="text-[10px] font-black text-[var(--text-muted)] tracking-[0.15em] uppercase">DIVIDENDS</span>
        </div>
        <div className="flex items-center gap-5">
          <DataItem
            label="YIELD"
            value={tickerData?.dividendYield ? formatValue(tickerData.dividendYield * 100, '', '%') : '1.48%'}
            color="text-emerald-400"
          />
          <DataItem label="PAYOUT" value="42%" />
          <DataItem label="EX-DIV" value="FEB 14" small />
        </div>
      </div>

      {/* RATING SECTION */}
      <div className="flex items-center gap-4 pl-4 min-w-[200px]">
        <div className="arch-card bg-[var(--bg-app)] border-emerald-500/30 rounded-lg px-3 py-1.5 flex flex-col gap-0.5 min-w-[140px]">
          <div className="flex items-center justify-between">
            <span className="text-[8px] font-black text-[var(--text-muted)] tracking-widest uppercase">CONSENSUS</span>
            <span className="text-[9px] font-black text-emerald-400 uppercase">BUY (4.2)</span>
          </div>
          <div className="h-1 w-full bg-emerald-500/10 rounded-full overflow-hidden">
            <div className="h-full w-[84%] bg-emerald-500 rounded-full"></div>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-[8px] font-black text-[var(--text-muted)] tracking-widest uppercase">TARGET</span>
            <span className="text-[9px] font-black text-[var(--text-primary)] font-mono">$314 <span className="text-emerald-400">+14%</span></span>
          </div>
        </div>
      </div>
    </div>
  );
};

const DataItem: React.FC<{ label: string; value: string; dimmed?: boolean; color?: string; small?: boolean }> = ({
  label, value, dimmed, color, small
}) => (
  <div className="flex flex-col">
    <span className="text-[8px] font-black text-[var(--text-muted)] tracking-wider uppercase leading-none mb-1">{label}</span>
    <span className={`
      ${small ? 'text-xs' : 'text-sm'} 
      font-black font-mono leading-none tracking-tight
      ${color ? color : dimmed ? 'text-[var(--text-secondary)]' : 'text-[var(--text-primary)]'}
    `}>
      {value}
    </span>
  </div>
);
