import React from 'react';

interface KeyStatsProps {
  section: string;
  ticker: string;
  externalData?: any;
}

export const KeyStats: React.FC<KeyStatsProps> = ({ section, ticker, externalData }) => {
  const data: Record<string, { label: string; value: string | number }[]> = {
    Trading: [
      { label: 'Primary Ticker', value: ticker },
      { label: 'Open', value: externalData?.price ? `${externalData.currency || '$'} ${externalData.price}` : '$296.94' },
      { label: '52 Week High', value: externalData?.fiftyTwoWeekHigh ? `${externalData.currency || '$'} ${externalData.fiftyTwoWeekHigh}` : '$477.92' },
      { label: '52 Week Low', value: externalData?.fiftyTwoWeekLow ? `${externalData.currency || '$'} ${externalData.fiftyTwoWeekLow}` : '$250.50' },
      { label: 'History Count', value: externalData?.history?.length || '0' },
    ],
    Valuation: [
      { label: 'Market Cap (M)', value: externalData?.marketCap ? `${(externalData.marketCap / 1e6).toFixed(2)}` : '$11,015.51' },
      { label: 'P/E (LTM)', value: externalData?.peRatio ? externalData.peRatio.toFixed(2) : '18.89' },
      { label: 'Sector', value: externalData?.sector || 'Industrial Services' },
      { label: 'Industry', value: externalData?.industry || 'Business Services' },
    ],
    Dividends: [
      { label: 'Dividend Yield (%)', value: externalData?.dividendYield ? (externalData.dividendYield * 100).toFixed(2) : '1.48' },
      { label: 'Currency', value: externalData?.currency || 'USD' },
    ],
    Estimates: [
      { label: 'Next Earnings', value: 'Mar 19, 2026' },
      { label: 'Avg Rating', value: 'Hold (2.02)' },
      { label: 'Target Price', value: '$314.87' },
    ]
  };

  const currentData = data[section] || [];

  return (
    <div className="card p-3 h-full">
      <div className="flex items-center justify-between mb-3 text-[13px] uppercase tracking-wide text-[var(--text-secondary)]">
        {section}
      </div>
      <div className="flex flex-col gap-1.5">
        {currentData.map((item, idx) => (
          <div key={idx} className="flex justify-between items-center text-[11px] pb-0.5 border-b border-dotted border-[var(--border-light)] last:border-b-0">
            <span className="text-[var(--text-muted)]">{item.label}</span>
            <span className="font-semibold text-[var(--text-primary)]">{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
