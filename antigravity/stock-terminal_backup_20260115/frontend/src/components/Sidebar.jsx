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
          <Search size={14} />
          <input
            type="text"
            placeholder="FDS-US"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleSearch}
            onFocus={(e) => e.target.select()}
          />
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
          background: #f8f9fa;
          border-right: 1px solid var(--border);
          display: flex;
          flex-direction: column;
          font-size: 11px;
        }
        .sidebar-logo {
          padding: 12px;
          border-bottom: 1px solid var(--border);
        }
        .logo-text {
          font-weight: 800;
          font-size: 16px;
          color: #004b87;
          display: block;
          margin-bottom: 8px;
        }
        .search-bar-sidebar {
          display: flex;
          align-items: center;
          background: #fff;
          border: 1px solid var(--border);
          padding: 4px 8px;
          border-radius: 4px;
        }
        .search-bar-sidebar input {
          border: none;
          outline: none;
          width: 100%;
          margin-left: 6px;
          font-size: 11px;
          font-weight: 600;
        }
        .sidebar-scroll {
          flex: 1;
          overflow-y: auto;
          padding: 8px 0;
        }
        .sidebar-section {
          margin-bottom: 16px;
        }
        .sidebar-label {
          padding: 0 12px;
          color: var(--text-muted);
          font-weight: 700;
          font-size: 10px;
          margin-bottom: 4px;
        }
        .sidebar-item {
          display: flex;
          align-items: center;
          padding: 6px 16px;
          cursor: pointer;
          color: var(--text-primary);
          gap: 12px;
        }
        .sidebar-item:hover {
          background: #eef1f4;
        }
        .sidebar-item.active {
          background: #e6f0ff;
          color: var(--brand);
          border-left: 3px solid var(--brand);
          padding-left: 13px;
        }
        .sidebar-item.mini {
          padding: 4px 16px;
          color: var(--text-secondary);
        }
      `}</style>
    </aside>
  );
};

export default Sidebar;
