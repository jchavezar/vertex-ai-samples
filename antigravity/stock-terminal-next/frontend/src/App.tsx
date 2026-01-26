import React from 'react';
import { Sidebar } from './components/Sidebar';
import { DashboardHeader } from './components/DashboardHeader';
import { ChatContainer } from './components/chat/ChatContainer';
import { DashboardView } from './components/dashboard/DashboardView';
import { useDashboardStore } from './store/dashboardStore';
import clsx from 'clsx';
import { AdvancedSearchView } from './components/search/AdvancedSearchView';
import { GraphOverlay } from './components/chat/GraphOverlay';

import { ChatProvider } from './context/ChatContext';

export const App = () => {
  const { isSidebarOpen, toggleSidebar, chatDockPosition, currentView, isChatOpen, setChatOpen, isChatMaximized, chatSidebarWidth, setChatSidebarWidth } = useDashboardStore();
  const resizingRef = React.useRef(false);

  // Auto-minimize chat when entering Advanced Search
  React.useEffect(() => {
    if (currentView === 'advanced_search') {
      setChatOpen(false);
    } else {
      setChatOpen(true);
    }
  }, [currentView, setChatOpen]);

  // Auto-hide sidebar when Graph Overlay is open
  const previousSidebarState = React.useRef(isSidebarOpen);
  const { isGraphOverlayOpen } = useDashboardStore();

  React.useEffect(() => {
    if (isGraphOverlayOpen) {
      // Save current state
      previousSidebarState.current = isSidebarOpen;
      // Close sidebar if it's open
      if (isSidebarOpen) toggleSidebar();
    } else {
      // Restore previous state if it was open
      if (previousSidebarState.current && !isSidebarOpen) {
        toggleSidebar();
      }
    }
  }, [isGraphOverlayOpen]);

  const [isResizing, setIsResizing] = React.useState(false);

  // Handle Resize
  React.useEffect(() => {
    let animationFrameId: number;

    const handleMouseMove = (e: MouseEvent) => {
      if (!resizingRef.current) return;

      const newWidth = window.innerWidth - e.clientX;
      // Constraints
      if (newWidth > 300 && newWidth < 1200) {
        // Optimize with RAF
        cancelAnimationFrame(animationFrameId);
        animationFrameId = requestAnimationFrame(() => {
          setChatSidebarWidth(newWidth);
        });
      }
    };

    const handleMouseUp = () => {
      resizingRef.current = false;
      setIsResizing(false);
      document.body.style.cursor = 'default';
      document.body.classList.remove('select-none'); // Re-enable selection
      // Ensure specific iframe/heavy elements have pointer events back if we disabled them
    };

    if (isChatOpen && chatDockPosition === 'right') {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
      cancelAnimationFrame(animationFrameId);
    };
  }, [isChatOpen, chatDockPosition, setChatSidebarWidth]);

  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    resizingRef.current = true;
    setIsResizing(true);
    document.body.style.cursor = 'col-resize';
    document.body.classList.add('select-none'); // Prevent text selection while dragging
  };

  return (
    <ChatProvider>
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

          {/* Graph Overlay */}
          <GraphOverlay />
        </main>

        {/* Right Docked Chat */}
        <div
          className={clsx(
            "relative flex border-l border-[var(--border)] bg-[var(--bg-app)]",
            // Only apply transition if NOT resizing
            !isResizing && "transition-[width,opacity] duration-300 ease-in-out",
            (chatDockPosition === 'right' && isChatOpen)
              ? "opacity-100"
              : "w-0 opacity-0 overflow-hidden"
          )}
          style={{
            width: (chatDockPosition === 'right' && isChatOpen)
              ? (isChatMaximized ? '55vw' : `${chatSidebarWidth}px`)
              : 0
          }}
        >
          {/* Drag Handle */}
          {(chatDockPosition === 'right' && isChatOpen && !isChatMaximized) && (
            <div
              onMouseDown={handleMouseDown}
              className="absolute left-0 top-0 bottom-0 w-[4px] cursor-col-resize hover:bg-blue-500/50 z-50 transition-colors"
              title="Drag to resize"
            />
          )}
          {(chatDockPosition === 'right' && isChatOpen) && <ChatContainer docked />}
        </div>
      </div>
    </ChatProvider>
  );
};
