import { useState } from 'react';
import axios from 'axios';
import { IconPlus, IconSearch, IconMessage, IconBuildingEnterprise } from '@tabler/icons-react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import './index.css';

interface Message {
  id: string;
  role: 'user' | 'ai';
  content: string;
  sources?: { title: string; url: string; snippet: string }[];
}

interface ChatHistory {
  id: string;
  title: string;
  messages: Message[];
}

function App() {
  const [history, setHistory] = useState<ChatHistory[]>([]);
  const [currentChatId, setCurrentChatId] = useState<string | null>(null);
  const [inputVal, setInputVal] = useState('');
  const [loading, setLoading] = useState(false);

  const currentChat = history.find(c => c.id === currentChatId) || null;

  const startNewChat = () => {
    setCurrentChatId(null);
  };

  const handleSend = async () => {
    if (!inputVal.trim()) return;

    let chatId = currentChatId;
    let newHistory = [...history];
    let chatIndex = history.findIndex(c => c.id === chatId);

    const userMessage: Message = { id: Date.now().toString(), role: 'user', content: inputVal };

    if (!chatId || chatIndex === -1) {
      chatId = Date.now().toString();
      const newChat: ChatHistory = {
        id: chatId,
        title: inputVal.slice(0, 30) + '...',
        messages: [userMessage]
      };
      newHistory = [newChat, ...newHistory];
      chatIndex = 0;
      setCurrentChatId(chatId);
    } else {
      newHistory[chatIndex].messages.push(userMessage);
    }
    
    setHistory(newHistory);
    setInputVal('');
    setLoading(true);

    try {
      // Connect to local backend proxying StreamAssist
      const res = await axios.post('http://localhost:8000/api/search', {
        query: userMessage.content
      });

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'ai',
        content: res.data.answer || "I couldn't find an answer.",
        sources: res.data.sources
      };

      newHistory = [...history];
      chatIndex = newHistory.findIndex(c => c.id === chatId);
      newHistory[chatIndex].messages.push(aiMessage);
      setHistory(newHistory);

    } catch (error) {
      console.error(error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'ai',
        content: 'Error communicating with StreamAssist Engine. Please ensure the backend is running.'
      };
      newHistory = [...history];
      chatIndex = newHistory.findIndex(c => c.id === chatId);
      newHistory[chatIndex].messages.push(errorMessage);
      setHistory(newHistory);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">
          <IconBuildingEnterprise size={28} color="#A100FF" />
          <h1>Stream Assist</h1>
        </div>
        
        <button className="new-chat-btn" onClick={startNewChat}>
          <IconPlus size={20} />
          <span>New Query</span>
        </button>

        <div className="history-list">
          {history.map(chat => (
            <div 
              key={chat.id} 
              className={`history-item ${chat.id === currentChatId ? 'active' : ''}`}
              onClick={() => setCurrentChatId(chat.id)}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <IconMessage size={16} />
                <span>{chat.title}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main View */}
      <div className="main-view">
        {!currentChat ? (
          <div className="empty-state">
            <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ duration: 0.5 }}>
              <h2>Accenture Discovery</h2>
              <p>Search enterprise documents securely via Stream Assist. Powered by Zero-Leak architecture.</p>
            </motion.div>
          </div>
        ) : (
          <div className="chat-container">
            <AnimatePresence>
              {currentChat.messages.map((msg) => (
                <motion.div 
                  key={msg.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`message-wrapper ${msg.role}`}
                >
                  <div className={`message ${msg.role}`}>
                    {msg.role === 'user' ? (
                      msg.content
                    ) : (
                      <div className="markdown-body">
                        <ReactMarkdown>{msg.content}</ReactMarkdown>
                        {msg.sources && msg.sources.length > 0 && (
                          <div className="sources-container">
                            <strong>Sources:</strong>
                            {msg.sources.map((s, i) => (
                              <a key={i} href={s.url} target="_blank" rel="noreferrer" className="source-item">
                                {i+1}. {s.title}
                              </a>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
              {loading && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="message-wrapper ai">
                  <div className="message ai">
                    <div className="loading-dots">
                      <div className="dot"></div>
                      <div className="dot"></div>
                      <div className="dot"></div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}

        <div className="input-area">
          <div className="input-box">
            <input 
              type="text" 
              placeholder="Query enterprise knowledge..." 
              value={inputVal}
              onChange={(e) => setInputVal(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              disabled={loading}
            />
            <button className="send-btn" onClick={handleSend} disabled={loading || !inputVal.trim()}>
              <IconSearch size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
