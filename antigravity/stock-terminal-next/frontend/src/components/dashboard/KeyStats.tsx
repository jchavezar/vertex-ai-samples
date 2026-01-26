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
    <div className="card h-full hover:shadow-lg hover:border-blue-500/30 transition-all duration-300">
      <div className="text-[12px] font-bold text-[var(--text-secondary)] tracking-widest uppercase mb-4">
        {section}
      </div>
      <div className="flex flex-col gap-3">
        {currentData.map((item, idx) => (
          <div key={idx} className="flex justify-between items-center text-[11px] border-b border-[var(--border)] pb-2 last:border-0 last:pb-0">
            <span className="text-[var(--text-muted)] font-medium">{item.label}</span>
            <span className="font-bold text-[var(--text-primary)] text-right">{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
