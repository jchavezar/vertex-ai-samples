import { LayoutDashboard, Receipt, BarChart3, CreditCard, Lightbulb } from 'lucide-react';
import type { Page } from '../types';

const NAV_ITEMS: { page: Page; label: string; icon: React.ReactNode }[] = [
  { page: 'dashboard', label: 'Dashboard', icon: <LayoutDashboard /> },
  { page: 'transactions', label: 'Transactions', icon: <Receipt /> },
  { page: 'reports', label: 'Reports', icon: <BarChart3 /> },
  { page: 'subscriptions', label: 'Subscriptions', icon: <CreditCard /> },
  { page: 'insights', label: 'Insights', icon: <Lightbulb /> },
];

interface Props {
  activePage: Page;
  onNavigate: (page: Page) => void;
}

export function Sidebar({ activePage, onNavigate }: Props) {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-icon">
          <CreditCard size={18} />
        </div>
        <h1>Amex Dashboard</h1>
      </div>
      <nav className="sidebar-nav">
        {NAV_ITEMS.map(({ page, label, icon }) => (
          <button
            key={page}
            className={`sidebar-item ${activePage === page ? 'active' : ''}`}
            onClick={() => onNavigate(page)}
          >
            {icon}
            <span>{label}</span>
          </button>
        ))}
      </nav>
      <div className="sidebar-footer">
        <p>Powered by Gemini + Firestore</p>
      </div>
    </aside>
  );
}
