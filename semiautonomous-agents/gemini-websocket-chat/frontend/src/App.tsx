import { useEffect } from 'react';
import { useChatStore } from './stores/chatStore';
import ModelPicker from './components/ModelPicker';
import ChatView from './components/ChatView';
import InputBar from './components/InputBar';
import SessionList from './components/SessionList';

function App() {
  const initWebSocket = useChatStore((s) => s.initWebSocket);
  const loadSessions = useChatStore((s) => s.loadSessions);
  const toggleSidebar = useChatStore((s) => s.toggleSidebar);
  const sidebarOpen = useChatStore((s) => s.sidebarOpen);
  const newSession = useChatStore((s) => s.newSession);

  useEffect(() => {
    initWebSocket();
    loadSessions();
  }, [initWebSocket, loadSessions]);

  return (
    <div className="app">
      {/* Sidebar */}
      {sidebarOpen && (
        <div className="sidebar-overlay" onClick={toggleSidebar} />
      )}
      <SessionList />

      {/* Header */}
      <header className="header">
        <div className="header-left">
          <button className="menu-btn" onClick={toggleSidebar}>
            :::
          </button>
          <span className="logo">sockagent</span>
        </div>
        <button className="new-session-btn" onClick={newSession}>
          [new]
        </button>
      </header>

      {/* Model tabs */}
      <ModelPicker />

      {/* Chat thread */}
      <ChatView />

      {/* Input */}
      <InputBar />
    </div>
  );
}

export default App;
