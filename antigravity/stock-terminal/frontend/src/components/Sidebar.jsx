import React from 'react';
import {
  LayoutDashboard,
  BarChart3,
  Newspaper,
  Users,
  TrendingUp,
  FileText,
  PieChart,
  Globe,
  Search,
  MoreHorizontal
} from 'lucide-react';

const Sidebar = ({ setTicker, activeView, setActiveView }) => {
  const [inputValue, setInputValue] = React.useState('FDS-US');

  const handleSearch = (e) => {
    if (e.key === 'Enter') {
      setTicker(inputValue);
    }
  };

  const menuItems = [
    { label: 'Snapshot', icon: LayoutDashboard },
    { label: 'Entity Structure', icon: Users },
    { label: 'Event Calendar', icon: TrendingUp },
    { label: 'Comps Analysis', icon: BarChart3 },
    { label: 'Supply Chain', icon: Globe },
    { label: 'Capital Structure', icon: PieChart },
    { label: 'RBICS with Revenue', icon: FileText },
    { label: 'Geographic Revenue', icon: Globe },
    { label: 'Reference', icon: FileText },
    { label: 'ESG', icon: LayoutDashboard },
  ];

  const sections = [
    { name: 'Charts', items: ['Price', 'Performance', 'Technical'] },
    { name: 'News, Research, and Filings', items: ['Summary', 'StreetAccount', 'Press Releases'] },
    { name: 'Financials', items: ['Income Statement', 'Balance Sheet', 'Cash Flow'] },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <span className="logo-text">FACTSET</span>
        <div className="search-bar-sidebar">
          <Search size={14} className="search-icon" />
          <input
            type="text"
            placeholder="Search Ticker..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value.toUpperCase())}
            onKeyDown={handleSearch}
            onFocus={(e) => e.target.select()}
          />
          {inputValue && (
            <button className="clear-btn" onClick={() => setInputValue('')} tabIndex="-1">
              <MoreHorizontal size={14} />
            </button>
          )}
        </div>
      </div>

      <div className="sidebar-scroll">
        <div className="sidebar-section">
          <p className="sidebar-label">REPORTS</p>
          {menuItems.map((item, idx) => (
            <div
              key={idx}
              className={`sidebar-item ${activeView === item.label ? 'active' : ''}`}
              onClick={() => setActiveView(item.label)}
            >
              <item.icon size={16} />
              <span>{item.label}</span>
            </div>
          ))}
        </div>

        {sections.map((section, idx) => (
          <div key={idx} className="sidebar-section">
            <p className="sidebar-label">{section.name.toUpperCase()}</p>
            {section.items.map((item, i) => (
              <div
                key={i}
                className={`sidebar-item mini ${activeView === item ? 'active' : ''}`}
                onClick={() => setActiveView(item)}
              >
                <span>{item}</span>
              </div>
            ))}
          </div>
        ))}
      </div>

      <style jsx="true">{`
        .sidebar {
          width: var(--sidebar-width);
          background: var(--bg-card);
          backdrop-filter: blur(20px);
          border-right: 1px solid var(--border);
          display: flex;
          flex-direction: column;
          font-size: 13px;
          z-index: 100;
        }
        .sidebar-logo {
          padding: 24px 16px;
          border-bottom: 1px solid var(--border);
        }
        .logo-text {
          font-weight: 900;
          font-size: 18px;
          color: var(--text-primary);
          display: block;
          margin-bottom: 16px;
          letter-spacing: -0.5px;
          background: var(--brand-gradient);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }
        .search-bar-sidebar {
          display: flex;
          align-items: center;
          background: var(--border-light);
          border: 1px solid var(--border);
          padding: 8px 12px;
          border-radius: 8px;
          transition: border-color 0.2s, background 0.2s;
        }
        .search-bar-sidebar:focus-within {
          border-color: var(--brand);
          background: var(--bg-card);
        }
        .search-icon {
          color: var(--text-muted);
        }
        .search-bar-sidebar input {
          background: transparent;
          border: none;
          outline: none;
          width: 100%;
          margin-left: 10px;
          font-size: 13px;
          color: var(--text-primary);
          font-family: var(--font-sans);
        }
        .clear-btn {
          color: var(--text-muted);
          padding: 2px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 4px;
        }
        .clear-btn:hover {
          background: var(--border);
          color: var(--text-primary);
        }
        .sidebar-scroll {
          flex: 1;
          overflow-y: auto;
          padding: 16px 0;
        }
        .sidebar-section {
          margin-bottom: 24px;
        }
        .sidebar-label {
          padding: 0 16px;
          color: var(--text-muted);
          font-weight: 700;
          font-size: 11px;
          margin-bottom: 8px;
          text-transform: uppercase;
          letter-spacing: 1px;
        }
        .sidebar-item {
          display: flex;
          align-items: center;
          padding: 8px 16px;
          cursor: pointer;
          color: var(--text-secondary);
          gap: 12px;
          transition: all 0.2s ease;
          position: relative;
        }
        .sidebar-item:hover {
          color: var(--text-primary);
          background: var(--border-light);
        }
        .sidebar-item.active {
          color: var(--brand);
          background: var(--brand-light);
          font-weight: 600;
        }
        .sidebar-item.active::after {
          content: '';
          position: absolute;
          left: 0;
          top: 8px;
          bottom: 8px;
          width: 3px;
          background: var(--brand);
          border-radius: 0 4px 4px 0;
        }
        .sidebar-item.mini {
          padding: 6px 16px 6px 44px;
          font-size: 12px;
        }
      `}</style>
    </aside>
  );
};

export default Sidebar;
