import { Share2, Download, Plus, Bell, ChevronDown, TrendingUp, TrendingDown, Sun, Moon } from 'lucide-react';
import { useStockData } from '../hooks/useStockData';

const DashboardHeader = ({ ticker, externalData, loading, theme, onToggleTheme }) => {
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
            <h1 className="company-brand">
              {displayData?.name ? displayData.name.split(' ')[0] : ticker}
              <span className="ticker-badge">{ticker}</span>
            </h1>
            <div className="market-status">
              <div className="status-dot"></div>
              Market Open • {internalData?.lastUpdated ? new Date(internalData.lastUpdated * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Live'}
            </div>
          </div>
        </div>
      </div>

      <div className="header-center">
        <div className="stat-group">
          <div className="current-price">
            {displayData?.price ? `${displayData.currency || '$'} ${displayData.price.toLocaleString()}` : '--'}
          </div>
          <div className={`price-change ${(displayData?.change || 0) >= 0 ? 'positive' : 'negative'}`}>
            {(displayData?.change || 0) >= 0 ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
            {displayData?.change !== undefined && displayData?.change !== null ? `${Number(displayData.change).toFixed(2)}%` : '0.00%'}
          </div>
        </div>

        <div className="stat-group">
          <span className="stat-label">Market Cap</span>
          <span className="stat-value">
            {displayData?.marketCap && !isNaN(displayData.marketCap)
              ? `${(Number(displayData.marketCap) / 1e9).toFixed(2)}B`
              : '--'}
          </span>
        </div>

        <div className="stat-group">
          <span className="stat-label">P/E Ratio</span>
          <span className="stat-value">{internalData?.peRatio ? Number(internalData.peRatio).toFixed(1) : '--'}</span>
        </div>
      </div>

      <div className="header-actions">
        <button className="theme-toggle" onClick={onToggleTheme}>
          {theme === 'dark' ? <Sun size={12} /> : <Moon size={12} />}
          {theme === 'dark' ? 'Light' : 'Dark'}
        </button>
        <button className="action-icon-btn" title="Summary"><Share2 size={14} /></button>
        <button className="action-icon-btn" title="Alerts"><Bell size={14} /></button>
        <button className="action-icon-btn" title="Watchlist"><Plus size={14} /></button>
        <button className="action-icon-btn" title="Download"><Download size={14} /></button>
        <button className="action-icon-btn" title="Settings"><ChevronDown size={14} /></button>
      </div>

      <style jsx="true">{`
        .dashboard-header {
          background: var(--bg-card);
          backdrop-filter: blur(12px);
          border-bottom: 1px solid var(--border);
          padding: 10px 24px;
          display: flex;
          align-items: center;
          gap: 24px;
          z-index: 50;
        }
        .company-info {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        .company-logo {
          width: 36px;
          height: 36px;
          background: var(--brand-gradient);
          color: #fff;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 8px;
          font-weight: 900;
          font-size: 16px;
          box-shadow: 0 4px 12px ${theme === 'dark' ? 'rgba(59, 130, 246, 0.4)' : 'rgba(0, 75, 135, 0.2)'};
        }
        .company-brand {
          font-size: 18px;
          font-weight: 900;
          margin: 0;
          color: var(--text-primary);
          line-height: 1;
          letter-spacing: -0.5px;
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .ticker-badge {
          font-size: 10px;
          background: var(--border-light);
          padding: 2px 6px;
          border-radius: 4px;
          color: var(--text-secondary);
          font-weight: 700;
          border: 1px solid var(--border);
        }
        .market-status {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 9px;
          font-weight: 700;
          text-transform: uppercase;
          color: var(--green);
          margin-top: 4px;
        }
        .status-dot {
          width: 6px;
          height: 6px;
          background: var(--green);
          border-radius: 50%;
          box-shadow: 0 0 8px var(--green);
          animation: status-pulse 2s infinite;
        }
        @keyframes status-pulse {
          0% { opacity: 1; }
          50% { opacity: 0.4; }
          100% { opacity: 1; }
        }
        .header-center {
          display: flex;
          align-items: center;
          gap: 24px;
          border-left: 1px solid var(--border);
          padding-left: 24px;
        }
        .current-price {
          font-size: 20px;
          font-weight: 900;
          color: var(--text-primary);
          line-height: 1;
        }
        .price-change {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 12px;
          font-weight: 800;
          margin-top: 2px;
        }
        .price-change.positive { color: var(--green); }
        .price-change.negative { color: var(--red); }
        
        .stat-group {
          display: flex;
          flex-direction: column;
        }
        .stat-label {
          font-size: 9px;
          color: var(--text-muted);
          text-transform: uppercase;
          font-weight: 700;
          letter-spacing: 0.5px;
        }
        .stat-value {
          font-size: 13px;
          font-weight: 800;
          color: var(--text-primary);
        }

        .header-actions {
          margin-left: auto;
          display: flex;
          gap: 4px;
        }
        .action-icon-btn {
          width: 32px;
          height: 32px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 6px;
          background: var(--bg-app);
          border: 1px solid var(--border);
          color: var(--text-secondary);
          transition: all 0.2s;
        }
        .action-icon-btn:hover {
          background: var(--brand);
          color: #fff;
          border-color: var(--brand);
          transform: translateY(-1px);
        }
        .theme-toggle {
          background: var(--brand-light);
          color: var(--brand);
          border-color: var(--brand);
          font-weight: 700;
          padding: 0 12px;
          height: 32px;
          font-size: 10px;
          display: flex;
          align-items: center;
          gap: 6px;
          border-radius: 6px;
        }
      `}</style>
    </header>
  );
};

export default DashboardHeader;
