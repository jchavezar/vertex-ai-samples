import React from 'react';
import { useStockData } from '../hooks/useStockData';

const FinancialsView = ({ ticker }) => {
  const { data, loading } = useStockData(ticker);

  const metrics = [
    { label: 'Revenue', value: data?.marketCap ? `$${(data.marketCap * 0.1).toFixed(2)}B` : '--' },
    { label: 'Gross Profit', value: '--' },
    { label: 'Operating Income', value: '--' },
    { label: 'Net Income', value: '--' },
    { label: 'EBITDA', value: '--' },
    { label: 'EPS (Basic)', value: data?.peRatio ? `$${(data.price / data.peRatio).toFixed(2)}` : '--' },
  ];

  if (loading) return <div className="card">Loading Financials...</div>;

  return (
    <div className="financials-view fade-in">
      <div className="card">
        <h3 className="section-title">Income Statement (Summary)</h3>
        <table className="financials-table">
          <thead>
            <tr>
              <th>Metric</th>
              <th>Current (LTM)</th>
              <th>Trend</th>
            </tr>
          </thead>
          <tbody>
            {metrics.map((m, idx) => (
              <tr key={idx}>
                <td className="metric-label">{m.label}</td>
                <td className="metric-value">{m.value}</td>
                <td>
                   <div className="sparkline-placeholder"></div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <style jsx="true">{`
        .financials-view {
          padding: 24px;
          max-width: 1000px;
          margin: 0 auto;
        }
        .financials-table {
          width: 100%;
          border-collapse: collapse;
          margin-top: 16px;
        }
        .financials-table th {
          text-align: left;
          padding: 12px;
          color: var(--text-muted);
          border-bottom: 1px solid var(--border);
          font-size: 11px;
          text-transform: uppercase;
        }
        .financials-table td {
          padding: 16px 12px;
          border-bottom: 1px solid var(--border-light);
        }
        .metric-label {
          font-weight: 700;
          color: var(--text-primary);
        }
        .metric-value {
          font-family: var(--font-mono);
          color: var(--brand);
          font-weight: 700;
        }
        .sparkline-placeholder {
          height: 20px;
          width: 60px;
          background: var(--brand-light);
          border-radius: 4px;
        }
      `}</style>
    </div>
  );
};

export default FinancialsView;
