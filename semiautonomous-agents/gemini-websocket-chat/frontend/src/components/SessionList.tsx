import { useChatStore } from '../stores/chatStore';

function formatTime(ts: number): string {
  const d = new Date(ts * 1000);
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hours = String(d.getHours()).padStart(2, '0');
  const mins = String(d.getMinutes()).padStart(2, '0');
  return `${month}-${day} ${hours}:${mins}`;
}

function SessionList() {
  const sessions = useChatStore((s) => s.sessions);
  const currentSessionId = useChatStore((s) => s.currentSessionId);
  const selectSession = useChatStore((s) => s.selectSession);
  const sidebarOpen = useChatStore((s) => s.sidebarOpen);
  const toggleSidebar = useChatStore((s) => s.toggleSidebar);

  return (
    <nav className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
      <div className="sidebar-header">
        <span>~/sessions $ ls -la</span>
        <button className="sidebar-close" onClick={toggleSidebar}>
          [x]
        </button>
      </div>
      <div className="session-list">
        {sessions.length === 0 ? (
          <div className="session-empty">
            total 0
            <br />
            no sessions yet
          </div>
        ) : (
          sessions.map((s) => (
            <div
              key={s.id}
              className={`session-item ${s.id === currentSessionId ? 'active' : ''}`}
              onClick={() => selectSession(s.id)}
            >
              <span className="session-title">{s.title}</span>
              <span className="session-meta">
                <span>{formatTime(s.updated_at)}</span>
                <span>{s.message_count} msg</span>
                <span>{s.model}</span>
              </span>
            </div>
          ))
        )}
      </div>
    </nav>
  );
}

export default SessionList;
