import React from 'react';

interface MarketDataFooterProps {
  tickerData?: any;
  layout?: 'horizontal' | 'vertical';
}

const formatValue = (val: number | undefined, prefix = '', suffix = '', decimals = 2) => {
  if (val === undefined || val === null) return '-';
  const num = Number(val);
  return `${prefix}${num.toLocaleString(undefined, { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}${suffix}`;
};

const getDirectionalColor = (val: number | undefined) => {
  if (val === undefined || val === null || val === 0) return 'text-[var(--text-primary)]';
  return val > 0 ? 'text-emerald-500' : 'text-rose-500';
};

const formatLargeNumber = (num: number | undefined) => {
  if (!num) return '-';
  if (num >= 1e9) return `${(num / 1e9).toFixed(1)}B`;
  if (num >= 1e6) return `${(num / 1e6).toFixed(1)}M`;
  return num.toLocaleString();
};

/**
 * Reusable component for a single data point
 */
const DataItem: React.FC<{
  label: string;
  value: string;
  dimmed?: boolean;
  color?: string;
  small?: boolean;
}> = ({ label, value, dimmed, color, small }) => (
  <div className="flex flex-col gap-0.5 group/item transition-all duration-300">
    <div className="flex items-center gap-2">
      <span className="text-[7.5px] font-black text-[var(--text-muted)] tracking-[0.25em] uppercase leading-none opacity-50 group-hover/item:opacity-100 transition-opacity whitespace-nowrap">
        {label}
      </span>
      <div className="h-[0.5px] flex-1 bg-[var(--border-subtle)]/20 group-hover/item:bg-[var(--border-subtle)]/50 transition-colors"></div>
    </div>
    <span className={`
      ${small ? 'text-[11px]' : 'text-[14px]'} 
      font-bold font-mono leading-tight tracking-tight break-words pt-1
      ${color ? color : dimmed ? 'text-[var(--text-secondary)]' : 'text-[var(--text-primary)]'}
    `}>
      {value}
    </span>
  </div>
  );

/**
 * Standard container for a stat section
 */
const StatSection: React.FC<{
  title: string;
  isVertical?: boolean;
  children: React.ReactNode;
}> = ({ title, isVertical, children }) => (
  <div className="flex flex-col gap-2.5">
    <div className="flex items-center gap-2 border-b border-[var(--border-subtle)]/50 pb-1 mb-0.5 bg-white/[0.01]">
      <div className="w-1.5 h-1.5 rounded-full bg-[var(--brand)] shadow-[0_0_8px_rgba(59,130,246,0.3)]"></div>
      <span className="text-[9px] font-black text-[var(--text-primary)] tracking-[0.3em] uppercase opacity-100">{title}</span>
    </div>
    <div className={`grid ${isVertical ? 'grid-cols-2 gap-x-12 gap-y-2.5' : 'flex flex-row items-center gap-10'} px-0.5`}>
      {children}
    </div>
  </div>
  );

export const TradingStats: React.FC<{ tickerData: any; layout?: 'horizontal' | 'vertical' }> = ({ tickerData, layout = 'horizontal' }) => {
  const change = tickerData?.regularMarketChangePercent || 0.45;
  const color = getDirectionalColor(change);

  return (
    <StatSection title="Trading" isVertical={layout === 'vertical'}>
      <DataItem label="PRICE" value={formatValue(tickerData?.price, '$')} color={color} />
      <DataItem label="CHG %" value={formatValue(change, change > 0 ? '+' : '', '%')} color={color} />
      <DataItem label="VOL" value="1.2M" />
      <DataItem label="52W HI" value={formatValue(tickerData?.fiftyTwoWeekHigh, '$')} dimmed />
    </StatSection>
  );
};

export const ValuationStats: React.FC<{ tickerData: any; layout?: 'horizontal' | 'vertical' }> = ({ tickerData, layout = 'horizontal' }) => (
  <StatSection title="Valuation" isVertical={layout === 'vertical'}>
    <DataItem label="MKT CAP" value={formatLargeNumber(tickerData?.marketCap)} />
    <DataItem label="P/E" value={formatValue(tickerData?.peRatio)} />
    <DataItem label="BETA" value="1.12" />
    <DataItem label="EPS" value="14.23" />
  </StatSection>
);

export const DividendStats: React.FC<{ tickerData: any; layout?: 'horizontal' | 'vertical' }> = ({ tickerData, layout = 'horizontal' }) => (
  <StatSection title="Dividends" isVertical={layout === 'vertical'}>
    <DataItem
      label="YIELD"
      value={tickerData?.dividendYield ? formatValue(tickerData.dividendYield * 100, '', '%') : '1.48%'}
    />
    <DataItem label="PAYOUT" value="42%" />
    <DataItem label="EX-DIV" value="FEB 14" small />
  </StatSection>
);

export const ConsensusStats: React.FC<{ tickerData?: any; layout?: 'horizontal' | 'vertical' }> = ({ layout = 'horizontal' }) => (
  <StatSection title="Consensus" isVertical={layout === 'vertical'}>
    <div className="col-span-2 space-y-4">
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between gap-2">
          <span className="text-[8px] font-bold text-[var(--text-muted)] tracking-widest uppercase">SENTIMENT</span>
          <span className="text-[10px] font-bold text-[var(--text-primary)] uppercase">BUY (4.2)</span>
        </div>
        <div className="h-1 w-full bg-[var(--border-subtle)] rounded-full overflow-hidden">
          <div className="h-full w-[84%] bg-[var(--text-primary)] rounded-full"></div>
        </div>
      </div>
      <div className="flex items-center justify-between pt-1 border-t border-[var(--border-subtle)]/50">
        <span className="text-[8px] font-bold text-[var(--text-muted)] tracking-widest uppercase">PT TARGET</span>
        <span className="text-[13px] font-bold text-[var(--text-primary)] font-mono">$314.00</span>
      </div>
    </div>
  </StatSection>
);

export const MarketDataFooter: React.FC<MarketDataFooterProps> = ({ tickerData, layout = 'horizontal' }) => {
  const isVertical = layout === 'vertical';

  return (
    <div className={`flex ${isVertical ? 'flex-col gap-8' : 'flex-row items-center justify-between'} p-5`}>
      <TradingStats tickerData={tickerData} layout={layout} />
      {!isVertical && <div className="w-px h-10 bg-[var(--border-subtle)]" />}
      <ValuationStats tickerData={tickerData} layout={layout} />
      {!isVertical && <div className="w-px h-10 bg-[var(--border-subtle)]" />}
      <DividendStats tickerData={tickerData} layout={layout} />
      {!isVertical && <div className="w-px h-10 bg-[var(--border-subtle)]" />}
      <ConsensusStats tickerData={tickerData} layout={layout} />
    </div>
  );
};
