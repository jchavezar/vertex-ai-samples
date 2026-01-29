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
  Sparkles,
  Zap,
  Cpu
} from 'lucide-react';
import { useDashboardStore } from '../store/dashboardStore';
import clsx from 'clsx';

export const Sidebar: React.FC = () => {
  const { ticker, setTicker, activeView, setActiveView, isSidebarOpen, chatDockPosition, currentView, setCurrentView, setAdkOverlayOpen } = useDashboardStore();
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
    <aside className="w-[var(--sidebar-width)] flex-shrink-0 bg-[var(--bg-card)] border-r border-[var(--border)] flex flex-col z-[100] h-full overflow-hidden backdrop-blur-xl">
      <div className="p-4 border-b border-[var(--border)] bg-transparent">
        <div className="mb-6 flex flex-col items-start">
          <img src="/factset-logo-final.png" alt="FACTSET" className="h-12 object-contain dark:brightness-0 dark:invert transition-all" />
          <div className="flex flex-col items-start gap-0.5 ml-1 mt-1 p-3 rounded-xl bg-white/5 border border-white/10 backdrop-blur-md transition-all hover:bg-white/10 hover:border-white/20 hover:shadow-[0_0_20px_rgba(66,133,244,0.15)] group">
            <span className="text-[10px] text-gray-400 font-semibold uppercase tracking-[0.2em] leading-none ml-0.5 group-hover:text-gray-300 transition-colors">Powered by</span>
            <span className="text-2xl font-black bg-gradient-to-r from-[#4285F4] via-[#9B72CB] to-[#D96570] bg-clip-text text-transparent tracking-tighter filter drop-shadow-sm group-hover:brightness-110 transition-all">Gemini</span>
          </div>

          {/* Auth Status & Connect Button */}
          <AuthStatus />
        </div>
        <div className="flex items-center bg-white/5 border border-white/20 px-4 py-3 rounded-full focus-within:border-blue-500/50 focus-within:bg-white/10 transition-all shadow-inner">
          <Search size={18} className="text-gray-400" />
          <input
            type="text"
            placeholder="Search Ticker..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleSearch}
            className="bg-transparent border-none outline-none w-full ml-2 text-sm text-[var(--text-primary)] placeholder-gray-500"
          />
        </div>

        {/* Toggle & System Controls */}
        <div className="flex flex-col gap-4 mt-8">
          {/* Neural Link Toggle - Liquid Glass Design */}
          <div className="bg-black/20 backdrop-blur-xl border border-white/10 rounded-2xl p-1.5 flex items-center relative gap-1 shadow-[inset_0_2px_4px_rgba(0,0,0,0.3)] group/toggle">
            <button
              onClick={() => setCurrentView('dashboard')}
              className={clsx(
                "flex-1 py-3 text-xs font-bold uppercase tracking-wider rounded-xl transition-all duration-300 relative overflow-hidden",
                currentView !== 'neural_link'
                  ? "text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.1),0_2px_4px_rgba(0,0,0,0.2)] bg-gradient-to-b from-white/10 to-white/5 border border-white/10"
                  : "text-gray-500 hover:text-gray-300 hover:bg-white/5"
              )}
            >
              Standard
            </button>
            <button
              onClick={() => setCurrentView('neural_link')}
              className={clsx(
                "flex-1 py-3 text-xs font-bold uppercase tracking-wider rounded-xl transition-all duration-500 flex items-center justify-center gap-1.5 relative overflow-hidden",
                currentView === 'neural_link' 
                  ? "text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.2),0_4px_12px_rgba(0,0,0,0.5)] bg-gradient-to-b from-slate-600 via-slate-700 to-slate-800 border border-white/20 ring-1 ring-white/10"
                  : "text-gray-500 hover:text-cyan-400 hover:bg-white/5"
              )}
            >
              {currentView === 'neural_link' && <div className="absolute inset-x-0 top-0 h-[1px] bg-white/40 blur-[1px]" />}

              <Zap size={14} className={clsx("transition-colors duration-300", currentView === 'neural_link' ? "text-cyan-200 fill-cyan-200 shadow-cyan-500/50 drop-shadow-sm" : "")} />
              <span className="relative z-10 text-shadow-sm">Neural Link</span>
            </button>
          </div>

          {/* ADK Overlay Trigger */}
          <button
            onClick={() => setAdkOverlayOpen(true)}
            className="w-full flex items-center justify-center gap-2 py-3 rounded-xl text-xs font-bold uppercase tracking-wider bg-purple-500/10 hover:bg-purple-500/20 text-purple-400 border border-purple-500/20 transition-all hover:shadow-[0_0_15px_rgba(168,85,247,0.3)] hover:scale-[1.02] group duration-300"
          >
            <Cpu size={16} className="group-hover:rotate-180 transition-transform duration-700" />
            <span>View System Architecture</span>
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto py-4">
        <div className="mb-8">
          <p className="px-4 text-[var(--text-muted)] font-bold text-xs mb-3 uppercase tracking-widest">REPORTS</p>
          {menuItems.map((item, idx) => (
            <div
              key={idx}
              className={clsx(
                "flex items-center px-3 py-2 mx-2 cursor-pointer gap-3 rounded-full transition-all text-sm",
                (currentView === 'advanced_search' && item.label === 'Advanced Search') ||
                  (currentView === 'report_generator' && item.label === 'Reports Generator') ||
                  (currentView === 'dashboard' && activeView === item.label)
                  ? "text-[var(--brand)] bg-blue-500/10 font-bold shadow-lg"
                  : "text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-white/5 hover:translate-x-1"
              )}
              onClick={() => handleItemClick(item.label)}
            >
              <item.icon size={18} />
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
          <div key={idx} className="mb-8">
            <p className="px-4 text-[var(--text-muted)] font-bold text-xs mb-3 uppercase tracking-widest">{section.name}</p>
            {section.items.map((item, i) => (
              <div
                key={i}
                className={clsx(
                  "flex items-center py-2 px-3 mx-2 pl-10 cursor-pointer rounded-full transition-all text-xs",
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
