import React from 'react';
import { Share2, Download, Plus, Bell, ChevronDown, TrendingUp, TrendingDown } from 'lucide-react';
import { useStockData } from '../hooks/useStockData';

const DashboardHeader = ({ ticker, externalData, loading }) => {
  const { data: internalData, loading: internalLoading, error } = useStockData(ticker);

  const displayData = externalData || internalData;
  const isDataLoading = loading || (internalLoading && !externalData);

  if (isDataLoading && !displayData) return <div className="dashboard-header">Loading...</div>;

  return (
    <header className="dashboard-header">
      <div className="header-left">
        <div className="company-info">
          <div className="company-logo">
            {displayData?.name?.charAt(0) || ticker.charAt(0)}
          </div>
          <div>
            <div className="company-name-row">
              <h1 className="company-name">{displayData?.name || ticker}</h1>
              <span className="ticker-badge">{ticker}</span>
            </div>
            <div className="last-updated">
              Last Updated: {internalData?.lastUpdated || 'Fetching...'}
            </div>
          </div>
        </div>
      </div>

      <div className="header-center">
        <div className="price-info">
          <div className="current-price">
            {displayData?.price ? `${displayData.currency || '$'} ${displayData.price.toLocaleString()}` : '--'}
          </div>
          <div className={`price-change ${(displayData?.change || 0) >= 0 ? 'positive' : 'negative'}`}>
            {(displayData?.change || 0) >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
            {displayData?.change !== undefined && displayData?.change !== null ? `${Number(displayData.change).toFixed(2)}%` : '0.00%'}
          </div>
        </div>
        <div className="market-cap">
          <span className="label">Mkt Cap:</span>
          <span className="value">
            {displayData?.marketCap && !isNaN(displayData.marketCap)
              ? `${(Number(displayData.marketCap) / 1e9).toFixed(2)}B`
              : '--'}
          </span>
        </div>
      </div>

      <div className="header-actions">
        <button className="action-btn"><Share2 size={14} /> Summary</button>
        <button className="action-btn">Currency: LOCAL <ChevronDown size={14} /></button>
        <button className="action-btn"><Bell size={14} /> Feedback</button>
        <button className="action-btn"><Download size={14} /> Download</button>
        <button className="action-btn"><Plus size={14} /> Watchlist</button>
        <button className="action-btn"><Bell size={14} /> News/Events</button>
      </div>

      <style jsx="true">{`
        .dashboard-header {
          background: #fff;
          border-bottom: 1px solid var(--border);
          padding: 12px 16px;
          display: flex;
          align-items: center;
          gap: 32px;
        }
        .company-info {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        .company-logo {
          width: 32px;
          height: 32px;
          background: #004b87;
          color: #fff;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 4px;
          font-weight: 700;
          font-size: 18px;
        }
        .company-name-row {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .company-name {
          font-size: 18px;
          margin: 0;
        }
        .ticker-badge {
          font-size: 10px;
          background: #f0f2f5;
          padding: 2px 4px;
          border-radius: 2px;
          color: var(--text-muted);
        }
        .last-updated {
          font-size: 10px;
          color: var(--text-muted);
        }
        .header-center {
          display: flex;
          align-items: center;
          gap: 24px;
          border-left: 1px solid var(--border-light);
          padding-left: 24px;
        }
        .price-info {
          display: flex;
          flex-direction: column;
        }
        .current-price {
          font-size: 20px;
          font-weight: 700;
        }
        .price-change {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 12px;
          font-weight: 600;
        }
        .price-change.positive { color: var(--green); }
        .price-change.negative { color: var(--red); }
        .market-cap {
          display: flex;
          flex-direction: column;
        }
        .market-cap .label {
          font-size: 10px;
          color: var(--text-muted);
        }
        .market-cap .value {
          font-size: 14px;
          font-weight: 700;
          color: #004b87;
        }
        .header-actions {
          margin-left: auto;
          display: flex;
          gap: 12px;
        }
        .action-btn {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 11px;
          color: var(--text-secondary);
          padding: 4px 8px;
          border-radius: 4px;
          background: none;
          border: 1px solid transparent;
          cursor: pointer;
        }
        .action-btn:hover {
          background: #f0f2f5;
          border-color: var(--border-light);
        }
      `}</style>
    </header>
  );
};

export default DashboardHeader;
