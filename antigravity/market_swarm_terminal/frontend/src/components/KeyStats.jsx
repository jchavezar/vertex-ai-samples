import React from 'react';

const KeyStats = ({ section, ticker, externalData }) => {
  const data = {
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
    <div className="card stats-card">
      <div className="section-title">{section}</div>
      <div className="stats-list">
        {currentData.map((item, idx) => (
          <div key={idx} className="stats-item">
            <span className="stats-label">{item.label}</span>
            <span className="stats-value">{item.value}</span>
          </div>
        ))}
      </div>

      <style jsx="true">{`
        .stats-card {
          padding: 10px;
        }
        .stats-list {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }
        .stats-item {
          display: flex;
          justify-content: space-between;
          font-size: 11px;
          border-bottom: 1px dotted var(--border-light);
          padding-bottom: 2px;
        }
        .stats-label {
          color: var(--text-muted);
        }
        .stats-value {
          font-weight: 600;
          color: var(--text-primary);
        }
      `}</style>
    </div>
  );
};

export default KeyStats;
