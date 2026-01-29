import React from 'react';

interface KeyStatsProps {
  section: string;
  ticker: string;
  externalData?: any;
  variant?: 'card' | 'clean' | 'ticker';
}

export const KeyStats: React.FC<KeyStatsProps> = ({ section, externalData, variant = 'card' }) => {
  const data: Record<string, { label: string; value: string | number }[]> = {
    Trading: [
      { label: 'Open', value: externalData?.price ? `${externalData.currency || '$'} ${externalData.price}` : '$296.94' },
      { label: '52W High', value: externalData?.fiftyTwoWeekHigh ? `${externalData.currency || '$'} ${externalData.fiftyTwoWeekHigh}` : '$477.92' },
      { label: '52W Low', value: externalData?.fiftyTwoWeekLow ? `${externalData.currency || '$'} ${externalData.fiftyTwoWeekLow}` : '$250.50' },
      { label: 'Volume', value: '1.2M' },
    ],
    Valuation: [
      { label: 'Market Cap', value: externalData?.marketCap ? `${(externalData.marketCap / 1e9).toFixed(1)}B` : '11.0B' },
      { label: 'P/E (LTM)', value: externalData?.peRatio ? externalData.peRatio.toFixed(2) : '18.89' },
      { label: 'Sector', value: externalData?.sector || 'Industrial' },
      { label: 'Industry', value: externalData?.industry || 'Business Svcs' },
    ],
    Dividends: [
      { label: 'Yield', value: externalData?.dividendYield ? (externalData.dividendYield * 100).toFixed(2) + '%' : '1.48%' },
      { label: 'Currency', value: externalData?.currency || 'USD' },
      { label: 'Beta', value: '1.12' },
      { label: 'EPS', value: '14.23' },
    ],
    Estimates: [
      { label: 'Next Earnings', value: 'Mar 19' },
      { label: 'Rating', value: 'Hold (2.0)' },
      { label: 'Target', value: '$314.87' },
      { label: 'Consensus', value: 'Overweight' },
    ]
  };

  const currentData = data[section] || [];

  const content = (
    <>
      <div className="text-[12px] font-bold text-[var(--text-secondary)] tracking-widest uppercase mb-4">
        {section}
      </div>
      <div className="flex flex-col gap-3">
        {currentData.map((item, idx) => (
          <div key={idx} className="flex justify-between items-center text-[11px] border-b border-[var(--border)] pb-2 last:border-0 last:pb-0">
            <span className="text-[var(--text-muted)] font-medium">{item.label}</span>
            <span className="font-bold text-[var(--text-primary)] text-right text-2xl">{item.value}</span>
          </div>
        ))}
      </div>
    </>
  );

  if (variant === 'clean') {
    return (
      <div className="h-full w-full flex flex-col justify-center">
        <div className="grid grid-cols-2 gap-x-8 gap-y-4">
          {currentData.map((item, idx) => (
            <div key={idx} className="flex flex-col">
              <span className="text-sm text-[var(--text-muted)] font-bold tracking-wide uppercase truncate mb-1">{item.label}</span>
              <span className="text-xl font-bold text-[var(--text-primary)] font-mono-numbers truncate">{item.value}</span>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (variant === 'ticker') {
    return (
      <div className="flex items-center gap-6 h-full w-full overflow-x-auto no-scrollbar">
        {currentData.map((item, idx) => (
          <div key={idx} className="flex flex-col min-w-[100px]">
            <span className="text-[10px] uppercase tracking-wider text-[var(--text-muted)] font-medium mb-1">{item.label}</span>
            <span className="text-xl font-bold text-white whitespace-nowrap">{item.value}</span>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="card h-full hover:shadow-lg hover:border-blue-500/30 transition-all duration-300">
      {content}
    </div>
  );
};
