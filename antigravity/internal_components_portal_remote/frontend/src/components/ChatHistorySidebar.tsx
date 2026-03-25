import React, { useState, useEffect } from 'react';
import './ChatHistorySidebar.css';

interface Session {
  id: string;
  title: string;
  updated_at: number;
}

interface ChatHistorySidebarProps {
  onSelectSession: (sessionId: string) => void;
  activeSessionId?: string;
}

export const ChatHistorySidebar: React.FC<ChatHistorySidebarProps> = ({ onSelectSession, activeSessionId }) => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const response = await fetch('/api/sessions');
        if (response.ok) {
          const data = await response.json();
          setSessions(data);
        }
      } catch (error) {
        console.error('Error fetching sessions:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSessions();
    
    // Poll for updates every 10 seconds (simplest sync)
    const interval = setInterval(fetchSessions, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="chat-history-sidebar">
      <div className="history-header">
        <h3>Past Conversations</h3>
      </div>
      <div className="history-list">
        {loading && sessions.length === 0 && <div className="history-loading">Loading...</div>}
        {!loading && sessions.length === 0 && <div className="history-empty">No past chats</div>}
        {sessions.map((session) => (
          <div 
            key={session.id} 
            className={`sidebar-history-item ${activeSessionId === session.id ? 'active' : ''}`}
            onClick={() => onSelectSession(session.id)}
          >
            <div className="history-item-title">{session.title}</div>
          </div>
        ))}
      </div>
    </div>
  );
};
