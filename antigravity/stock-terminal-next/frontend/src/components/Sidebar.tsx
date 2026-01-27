import React from 'react';
import {
  LayoutDashboard,
  BarChart3,
  Users,
  TrendingUp,
  FileText,
  PieChart,
  Globe,
  Search,
  Sparkles
} from 'lucide-react';
import { useDashboardStore } from '../store/dashboardStore';
import clsx from 'clsx';

export const Sidebar: React.FC = () => {
  const { ticker, setTicker, activeView, setActiveView, isSidebarOpen, chatDockPosition, currentView, setCurrentView } = useDashboardStore();
  const [inputValue, setInputValue] = React.useState(ticker);

  const handleSearch = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      setTicker(inputValue.toUpperCase());
    }
  };

  const handleItemClick = (label: string) => {
    if (label === 'Advanced Search') {
      setCurrentView('advanced_search');
    } else if (label === 'Reports Generator') {
      setCurrentView('report_generator');
    } else {
      setCurrentView('dashboard');
      setActiveView(label);
    }
  };

  const menuItems = [
    { label: 'Advanced Search', icon: Sparkles, isNew: true },
    { label: 'Reports Generator', icon: FileText, isNew: true },
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

  if (!isSidebarOpen || chatDockPosition === 'left') return null;

  return (
    <aside className="w-[var(--sidebar-width)] bg-[var(--bg-card)] border-r border-[var(--border)] flex flex-col z-[100] h-full overflow-hidden backdrop-blur-xl">
      <div className="p-6 border-b border-[var(--border)] bg-transparent">
        <div className="mb-6 flex flex-col items-start">
          <img src="/factset-logo-final.png" alt="FACTSET" className="h-12 object-contain dark:brightness-0 dark:invert transition-all" />
          <div className="flex items-center gap-1.5 ml-1 -mt-1 bg-white/5 backdrop-blur-md px-2.5 py-1 rounded-full border border-white/10 shadow-sm transition-all hover:bg-white/10">
            <Sparkles size={10} className="text-cyan-400" />
            <span className="text-[10px] font-semibold tracking-wider uppercase select-none">
              <span className="text-gray-400">Powered by</span>{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#4E80FF] via-[#9C80FF] to-[#FF809C] font-bold">
                Gemini
              </span>
            </span>
          </div>

          {/* Auth Status & Connect Button */}
          <AuthStatus />
        </div>
        <div className="flex items-center bg-white/5 border border-white/10 px-4 py-2 rounded-full focus-within:border-blue-500/50 focus-within:bg-white/10 transition-all">
          <Search size={14} className="text-[var(--text-muted)]" />
          <input
            type="text"
            placeholder="Search Ticker..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleSearch}
            className="bg-transparent border-none outline-none w-full ml-2 text-sm text-[var(--text-primary)]"
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto py-4">
        <div className="mb-6">
          <p className="px-4 text-[var(--text-muted)] font-bold text-[10px] mb-2 uppercase tracking-widest">REPORTS</p>
          {menuItems.map((item, idx) => (
            <div
              key={idx}
              className={clsx(
                "flex items-center px-4 py-2 mx-3 cursor-pointer gap-3 rounded-full transition-all text-sm",
                (currentView === 'advanced_search' && item.label === 'Advanced Search') ||
                  (currentView === 'report_generator' && item.label === 'Reports Generator') ||
                  (currentView === 'dashboard' && activeView === item.label)
                  ? "text-[var(--brand)] bg-blue-500/10 font-bold shadow-lg"
                  : "text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-white/5 hover:translate-x-1"
              )}
              onClick={() => handleItemClick(item.label)}
            >
              <item.icon size={16} />
              <span>{item.label}</span>
              {item.isNew && (
                <span className="text-[9px] bg-blue-600 px-2 py-0.5 rounded-full text-white font-bold ml-auto shadow-sm">
                  NEW
                </span>
              )}
            </div>
          ))}
        </div>

        {sections.map((section, idx) => (
          <div key={idx} className="mb-6">
            <p className="px-4 text-[var(--text-muted)] font-bold text-[10px] mb-2 uppercase tracking-widest">{section.name}</p>
            {section.items.map((item, i) => (
              <div
                key={i}
                className={clsx(
                  "flex items-center py-1.5 px-4 mx-3 pl-11 cursor-pointer rounded-full transition-all text-xs",
                  currentView === 'dashboard' && activeView === item
                    ? "text-[var(--brand)] bg-blue-500/10 font-bold"
                    : "text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-white/5"
                )}
                onClick={() => handleItemClick(item)}
              >
                <span>{item}</span>
              </div>
            ))}
          </div>
        ))}
      </div>
    </aside>
  );
};

const AuthStatus: React.FC = () => {
  const [status, setStatus] = React.useState<{ connected: boolean; message?: string }>({ connected: false });
  const [loading, setLoading] = React.useState(false);

  const checkStatus = async () => {
    try {
      const res = await fetch('http://localhost:8001/auth/factset/status');
      const data = await res.json();
      setStatus(data);
    } catch (e) {
      console.error("Auth check failed", e);
    }
  };

  React.useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, []);

  const handleConnect = async () => {
    setLoading(true);
    try {
      // Fetch the Auth URL from backend
      const res = await fetch('http://localhost:8001/auth/factset/url');
      const data = await res.json();
      if (data.auth_url) {
        window.location.href = data.auth_url;
      } else {
        console.error("No auth_url returned");
        setLoading(false);
      }
    } catch (e) {
      console.error("Failed to get auth url", e);
      setLoading(false);
    }
  };

  if (status.connected) {
    return (
      <div className="mt-2 flex items-center gap-1.5 px-2 py-1 rounded-md bg-green-500/10 border border-green-500/20 text-green-400 text-[10px] font-bold uppercase tracking-wide">
        <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
        Connected
      </div>
    );
  }

  return (
    <button
      onClick={handleConnect}
      disabled={loading}
      className="mt-2 w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white text-[10px] font-bold uppercase py-1.5 rounded-md transition-colors shadow-lg shadow-blue-900/20"
    >
      {loading ? 'Connecting...' : 'Connect FactSet'}
    </button>
  );
};
