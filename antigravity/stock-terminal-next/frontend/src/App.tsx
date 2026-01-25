import React from 'react';
import { Sidebar } from './components/Sidebar';
import { DashboardHeader } from './components/DashboardHeader';
import { ChatContainer } from './components/chat/ChatContainer';
import { DashboardView } from './components/dashboard/DashboardView';
import { useDashboardStore } from './store/dashboardStore';
import clsx from 'clsx';
import { AdvancedSearchView } from './components/search/AdvancedSearchView';

export const App = () => {
  const { isSidebarOpen, toggleSidebar, chatDockPosition, activeView, currentView, isChatOpen, setChatOpen } = useDashboardStore();

  // Auto-minimize chat when entering Advanced Search
  React.useEffect(() => {
    if (currentView === 'advanced_search') {
      setChatOpen(false);
    } else {
      setChatOpen(true);
    }
  }, [currentView, setChatOpen]);

  return (
    <div className="flex h-screen w-screen bg-[var(--bg-app)] text-[var(--text-primary)] font-sans overflow-hidden">
      <Sidebar />

      <div
        className="w-[12px] bg-[var(--bg-app)] border-r border-[var(--border)] border-l flex items-center justify-center cursor-pointer z-10 relative transition-all duration-200 hover:bg-white/5"
        style={{ borderLeft: isSidebarOpen ? 'none' : '1px solid var(--border)' }}
        onClick={toggleSidebar}
        title={isSidebarOpen ? "Collapse Sidebar" : "Expand Sidebar"}
      >
        <div className="h-6 w-1 bg-white/10 rounded-full" />
      </div>

      <main className="flex-1 flex flex-col overflow-hidden relative">
        <DashboardHeader />

        <div className="flex-1 overflow-y-auto p-0 scrollbar-hide">
          {currentView === 'advanced_search' ? <AdvancedSearchView /> : <DashboardView />}
        </div>

        {/* Floating Chat Wrapper */}
        {isChatOpen && chatDockPosition === 'floating' && <ChatContainer docked={false} />}

        {/* Floating Agent Chatbot Icon (When Minimized) */}
        {!isChatOpen && (
          <button
            onClick={() => setChatOpen(true)}
            className="absolute bottom-6 right-6 w-14 h-14 rounded-full bg-gradient-to-tr from-blue-600 to-cyan-500 shadow-2xl shadow-blue-500/30 flex items-center justify-center text-white hover:scale-110 transition-transform z-50 group"
            title="Open Stock Agent"
          >
            <div className="absolute inset-0 rounded-full bg-white/20 animate-ping opacity-20 group-hover:opacity-40" />
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect width="18" height="18" x="3" y="3" rx="2" />
              <path d="m16 15-4-4-4 4" />
            </svg>
          </button>
        )}
      </main>

      {/* Right Docked Chat */}
      <div
        className={clsx(
          "transition-all duration-300 ease-in-out border-l border-[var(--border)] bg-[var(--bg-app)]",
          (chatDockPosition === 'right' && isChatOpen) ? "w-[400px] opacity-100" : "w-0 opacity-0 overflow-hidden"
        )}
      >
        {(chatDockPosition === 'right' && isChatOpen) && <ChatContainer docked />}
      </div>
    </div>
  );
};
