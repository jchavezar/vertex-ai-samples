import React, { useState, useEffect, useRef } from 'react';
import { Sparkles, MessageSquare, ChevronDown, ChevronUp, ChevronRight, Maximize2, Minimize2, Terminal, AlertCircle, CheckCircle, X, Plus, Upload, Link, Cloud, HardDrive, Youtube, Mic, MicOff, Activity } from 'lucide-react';
import { useLiveAPI } from '../hooks/use-live-api';
import ReasoningChain from './ReasoningChain';
import ErrorBoundary from './ErrorBoundary';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import TraceLog from './TraceLog';

const RightSidebar = ({ dashboardData }) => {
  const [aiSummary, setAiSummary] = useState(null);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const { connected, connect, disconnect, volume } = useLiveAPI();

  // Chat State
  const [selectedModel, setSelectedModel] = useState('gemini-2.5-flash');
  const [messages, setMessages] = useState([
    { role: 'assistant', text: 'How can FactSet help?' }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null); // base64 string
  const [selectedVideoUrl, setSelectedVideoUrl] = useState(null);
  const [isUploadDropdownOpen, setIsUploadDropdownOpen] = useState(false);
  const fileInputRef = useRef(null);
  const dropdownRef = useRef(null);

  // FactSet Auth State
  const [isFactSetConnected, setIsFactSetConnected] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authInput, setAuthInput] = useState('');

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsUploadDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // UI State
  const [isPerformanceExpanded, setIsPerformanceExpanded] = useState(false);
  const [isChatMaximized, setIsChatMaximized] = useState(false);
  const [reasoningSteps, setReasoningSteps] = useState([]);
  const [isReasoningExpanded, setIsReasoningExpanded] = useState(false);
  const [isTraceExpanded, setIsTraceExpanded] = useState(false);

  // Trace Log State
  const [traceLogs, setTraceLogs] = useState([]);
  const [activeTab, setActiveTab] = useState('summary'); // 'summary' | 'trace'
  const [agentConfig, setAgentConfig] = useState(null);
  const [maximizedTab, setMaximizedTab] = useState('chat'); // 'chat' | 'workflow' | 'trace'

  // Performance & Debug State
  const [totalTokens, setTotalTokens] = useState({ prompt: 0, candidates: 0, total: 0 });
  const [allErrors, setAllErrors] = useState([]);
  const [thinkingTime, setThinkingTime] = useState(0); // in ms
  const timerRef = useRef(null);
  const chatEndRef = useRef(null);
  const maximizedChatEndRef = useRef(null);

  // Fetch AI Summary on mount or data change
  useEffect(() => {
    const fetchSummary = async () => {
      if (!dashboardData) return;
      setSummaryLoading(true);
      try {
        const res = await fetch('http://localhost:8001/summarize', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            dashboard_data: dashboardData,
            session_id: "default_summary",
            model: selectedModel
          })
        });
        const data = await res.json();
        setAiSummary(data.summary);
      } catch (err) {
        console.error("Failed to fetch AI summary:", err);
      } finally {
        setSummaryLoading(false);
      }
    };

    fetchSummary();
  }, [dashboardData, selectedModel]); // Added selectedModel to dependencies

  // Fetch Agent Config
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const res = await fetch('http://localhost:8001/agent-config');
        const data = await res.json();
        setAgentConfig(data);
      } catch (err) {
        console.error("Failed to fetch agent config:", err);
      }
    };
    fetchConfig();
  }, []);

  // Thinking Timer Logic
  useEffect(() => {
    if (chatLoading) {
      setThinkingTime(0);
      const start = Date.now();
      timerRef.current = setInterval(() => {
        setThinkingTime(Date.now() - start);
      }, 50);
    } else {
      clearInterval(timerRef.current);
    }
    return () => clearInterval(timerRef.current);
  }, [chatLoading]);

  // Auto-scroll logic
  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, chatLoading]);

  useEffect(() => {
    if (maximizedChatEndRef.current && isChatMaximized) {
      maximizedChatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, chatLoading, isChatMaximized, maximizedTab]);

  // Helper to add trace logs
  const addTraceLog = (type, content, tool = null, args = null, result = null) => {
    setTraceLogs(prev => [...prev, {
      type,
      content,
      tool,
      args,
      result,
      timestamp: new Date().toLocaleTimeString()
    }]);
  };

  const handleSendChat = async () => {
    if (!chatInput.trim() || chatLoading) return;

    const userText = chatInput;
    const userMsg = { role: 'user', text: userText };
    setMessages(prev => [...prev, userMsg]);

    addTraceLog('user', userText);

    setReasoningSteps([]);
    setChatInput('');
    setChatLoading(true);

    // Append an empty assistant message so it doesn't overwrite the user bubble
    const currentImage = selectedImage;
    const currentVideo = selectedVideoUrl;
    if (currentImage) {
      userMsg.image = currentImage;
    }
    if (currentVideo) {
      userMsg.video = currentVideo;
    }
    setMessages(prev => [...prev, { role: 'assistant', text: '' }]);
    setSelectedImage(null);
    setSelectedVideoUrl(null);

    try {
      const response = await fetch('http://localhost:8001/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userText,
          image: currentImage,
          video_url: currentVideo,
          session_id: "default_chat",
          model: selectedModel
        })
      });

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let accumulatedText = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop(); // Keep incomplete line

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const event = JSON.parse(line);

            if (event.type === 'text') {
              accumulatedText += event.content;
              setMessages(prev => {
                const newMsgs = [...prev];
                newMsgs[newMsgs.length - 1] = { role: 'assistant', text: accumulatedText };
                return newMsgs;
              });
            } else if (event.type === 'tool_call') {
              // Optionally show which tool is being used in the thinking indicator
              // For now we just keep the loading state
              setReasoningSteps(prev => [...prev, {
                type: 'call',
                tool: event.tool,
                args: event.args,
                timestamp: new Date().toLocaleTimeString()
              }]);
              addTraceLog('tool_call', null, event.tool, event.args);
            } else if (event.type === 'tool_result') {
              setReasoningSteps(prev => [...prev, {
                type: 'result',
                tool: event.tool,
                result: event.result,
                timestamp: new Date().toLocaleTimeString()
              }]);
              addTraceLog('tool_result', null, event.tool, null, event.result);

              // Check for tool-level data errors to log in Audit Log
              const isError = event.result && (
                (typeof event.result === 'object' && (event.result.error || event.result.status === 'error')) ||
                (typeof event.result === 'string' && event.result.toLowerCase().includes('error'))
              );

              if (isError) {
                const errorMsg = typeof event.result === 'object' ? (event.result.error || event.result.message || 'Unknown tool error') : event.result;
                setAllErrors(prev => [...prev, {
                  message: `[Tool: ${event.tool}] ${errorMsg}`,
                  timestamp: new Date().toLocaleTimeString(),
                  userQuery: userText
                }]);
              }
            } else if (event.type === 'error') {
              addTraceLog('error', event.content);
              const errorText = `**Error:** ${event.content}`;
              setMessages(prev => {
                const newMsgs = [...prev];
                const last = newMsgs[newMsgs.length - 1];
                if (last && last.role === 'assistant') {
                  newMsgs[newMsgs.length - 1] = {
                    role: 'assistant',
                    text: (last.text ? last.text + "\n\n" : "") + errorText
                  };
                }
                return newMsgs;
              });
              setAllErrors(prev => [...prev, {
                message: event.content,
                timestamp: new Date().toLocaleTimeString(),
                userQuery: userText
              }]);
              setReasoningSteps(prev => [...prev, {
                type: 'error',
                content: event.content,
                timestamp: new Date().toLocaleTimeString()
              }]);
            } else if (event.type === 'usage') {
              setTotalTokens(prev => ({
                prompt: prev.prompt + (event.prompt_tokens || 0),
                candidates: prev.candidates + (event.candidates_tokens || 0),
                total: prev.total + (event.total_tokens || 0)
              }));
              addTraceLog('usage', `Tokens used: ${event.total_tokens} (Prompt: ${event.prompt_tokens}, Candidates: ${event.candidates_tokens})`);
            }
          } catch (e) {
            console.error("JSON Parse Error:", e, line);
          }
        }
      }

      if (accumulatedText) {
        addTraceLog('assistant', accumulatedText);
      }

    } catch (err) {
      console.error("Chat failed:", err);
      const errMsg = "Sorry, I encountered a connection error.";
      setMessages(prev => {
        const newMsgs = [...prev];
        newMsgs[newMsgs.length - 1] = { role: 'assistant', text: errMsg };
        return newMsgs;
      });
      addTraceLog('error', errMsg);
    } finally {
      setChatLoading(false);
    }
  };

  const handleYouTubeUrl = () => {
    const url = prompt("Please enter the YouTube video URL:");
    if (url) {
      setSelectedVideoUrl(url);
      setIsUploadDropdownOpen(false);
    }
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Check if it's an image
    if (!file.type.startsWith('image/')) {
      alert("Please select an image file.");
      return;
    }

    const reader = new FileReader();
    reader.onloadend = () => {
      setSelectedImage(reader.result);
      setIsUploadDropdownOpen(false);
    };
    reader.readAsDataURL(file);
    // Reset file input
    e.target.value = '';
  };

  const handleConnectFactSet = async () => {
    try {
      const res = await fetch('http://localhost:8001/auth/factset/url');
      const data = await res.json();
      if (data.auth_url) {
        window.open(data.auth_url, '_blank');
        setShowAuthModal(true);
      }
    } catch (e) {
      console.error("Failed to get auth url:", e);
    }
  };

  const handleAuthSubmit = async () => {
    try {
      const res = await fetch('http://localhost:8001/auth/factset/callback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ redirect_url: authInput, session_id: "default_chat" })
      });
      if (res.ok) {
        setIsFactSetConnected(true);
        setShowAuthModal(false);
        const msg = "Successfully connected to FactSet! I can now access real-time market data.";
        setMessages(prev => [...prev, { role: 'assistant', text: msg }]);
        addTraceLog('system', msg);
      } else {
        alert("Authentication failed. Please check the URL.");
      }
    } catch (e) {
      alert("Error connecting: " + e.message);
    }
  };


  return (
    <aside className={`right-sidebar ${isChatMaximized ? 'maximized' : ''}`}>

      {/* Header and Controls */}
      <div className="right-sidebar-header">
        {isChatMaximized ? (
          /* Maximized Header with Tabs */
          <div style={{ display: 'flex', alignItems: 'center', gap: '20px', flex: 1 }}>
            <h3 style={{ fontSize: '18px', fontWeight: 'bold', color: '#004b87', margin: 0 }}>Stock Terminal Agent</h3>
            <div style={{ display: 'flex', background: '#f0f2f5', padding: '4px', borderRadius: '8px', gap: '4px' }}>
              {['chat', 'workflow', 'trace', 'agent', 'errors'].map(tab => (
                <button
                  key={tab}
                  onClick={() => setMaximizedTab(tab)}
                  style={{
                    padding: '6px 12px',
                    border: 'none',
                    borderRadius: '6px',
                    background: maximizedTab === tab ? '#fff' : 'transparent',
                    color: maximizedTab === tab ? '#004b87' : '#666',
                    fontWeight: maximizedTab === tab ? 600 : 400,
                    fontSize: '12px',
                    cursor: 'pointer',
                    boxShadow: maximizedTab === tab ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
                    textTransform: 'capitalize'
                  }}
                >
                  {tab === 'workflow' ? 'Agent Workflow' : tab === 'agent' ? 'Agent Config' : tab}
                </button>
              ))}
            </div>
          </div>
        ) : (
          /* Standard Sidebar Header - Simplified */
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <h3 style={{ fontSize: '13px', fontWeight: '700', color: '#004b87', margin: 0 }}>Assistant</h3>
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              style={{
                background: '#f0f2f5',
                fontSize: '10px',
                color: '#004b87',
                border: '1px solid #d1d5db',
                borderRadius: '4px',
                padding: '2px 4px',
                cursor: 'pointer'
              }}
            >
              <option value="gemini-2.5-flash">Gemini 2.5 Flash</option>
              <option value="gemini-2.5-pro">Gemini 2.5 Pro</option>
              <option value="gemini-3-flash-preview">Gemini 3 Flash Preview</option>
              <option value="gemini-3-pro-preview">Gemini 3 Pro Preview</option>
            </select>
          </div>
        )}

        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          {allErrors.length > 0 && (
            <button
              onClick={() => {
                setIsChatMaximized(true);
                setMaximizedTab('errors');
              }}
              style={{
                background: '#fff0f0',
                border: '1px solid #ffcccb',
                color: '#dc3545',
                padding: '4px 8px',
                borderRadius: '6px',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                cursor: 'pointer',
                animation: 'pulse 2s infinite'
              }}
            >
              <AlertCircle size={14} />
              <span style={{ fontSize: '11px', fontWeight: 600 }}>{allErrors.length} Errors</span>
            </button>
          )}
          <button
            onClick={connected ? disconnect : connect}
            style={{
              fontSize: '10px',
              padding: '4px 8px',
              borderRadius: '4px',
              border: connected ? '1px solid #dc3545' : '1px solid #004b87',
              background: connected ? '#fff5f5' : 'transparent',
              color: connected ? '#dc3545' : '#004b87',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}
          >
            {connected ? <MicOff size={10} /> : <Mic size={10} />}
            {connected ? 'End Live' : 'Go Live'}
            {connected && (
              <div style={{
                width: '40px',
                height: '10px',
                background: '#eee',
                borderRadius: '2px',
                overflow: 'hidden',
                display: 'flex',
                alignItems: 'flex-end',
                marginLeft: '4px'
              }}>
                <div style={{
                  width: '100%',
                  height: `${Math.min(100, volume * 100)}%`,
                  background: '#dc3545',
                  transition: 'height 0.1s'
                }}></div>
              </div>
            )}
          </button>
          <button
            onClick={handleConnectFactSet}
            disabled={isFactSetConnected}
            style={{
              fontSize: '10px',
              padding: '4px 8px',
              borderRadius: '4px',
              border: isFactSetConnected ? '1px solid #28a745' : '1px solid #004b87',
              background: isFactSetConnected ? '#e6ffea' : 'transparent',
              color: isFactSetConnected ? '#28a745' : '#004b87',
              cursor: isFactSetConnected ? 'default' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}
          >
            <div style={{
              width: '6px',
              height: '6px',
              borderRadius: '50%',
              background: isFactSetConnected ? '#28a745' : '#ccc'
            }}></div>
            {isFactSetConnected ? 'FactSet Active' : 'Connect FactSet'}
          </button>

          <button
            onClick={() => setIsChatMaximized(!isChatMaximized)}
            style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 4, display: 'flex' }}
            title={isChatMaximized ? "Restore" : "Maximize Chat"}
          >
            {isChatMaximized ? <Minimize2 size={18} color="#666" /> : <Maximize2 size={14} color="#666" />}
          </button>
        </div>
      </div>

      <div className="right-content" style={{ display: 'flex', flexDirection: 'column', flex: 1, overflow: 'hidden' }}>

        {/* Render Logic based on Mode */}
        {isChatMaximized ? (
          <>
            {maximizedTab === 'chat' && (
              <>
                <div className="chat-messages maximized" style={{ flex: 1, overflowY: 'auto', padding: '20px' }}>
                  {messages.map((msg, idx) => (
                    <div key={idx} className={`msg ${msg.role}`} style={{
                      fontSize: '14px',
                      padding: '12px 16px',
                      borderRadius: '12px',
                      maxWidth: '70%',
                      marginBottom: '12px',
                      alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                      background: msg.role === 'user' ? '#e6f0ff' : '#f0f2f5',
                      color: msg.role === 'user' ? '#004b87' : 'var(--text-primary)',
                      border: msg.role === 'user' ? '1px solid #cce0ff' : '1px solid #e6ebf1',
                      wordBreak: 'break-word',
                      overflow: 'visible'
                    }}>
                      {msg.image && (
                        <div style={{ marginBottom: '8px' }}>
                          <img src={msg.image} alt="Uploaded" style={{ maxWidth: '100%', borderRadius: '8px', border: '1px solid #ddd' }} />
                        </div>
                      )}
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.text}</ReactMarkdown>
                    </div>
                  ))}
                  {chatLoading && (messages[messages.length - 1]?.role !== 'assistant' || messages[messages.length - 1]?.text === '') && (
                    <div className="small blinking" style={{ fontStyle: 'italic', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      Assistant is thinking... <span>({(thinkingTime / 1000).toFixed(2)}s)</span>
                    </div>
                  )}
                  <div ref={maximizedChatEndRef} />
                </div>
                <div className="chat-input-container maximized" style={{ padding: '20px', borderTop: '1px solid #eee' }}>
                  <div style={{ maxWidth: '800px', margin: '0 auto', width: '100%', display: 'flex', gap: '12px', alignItems: 'center', background: '#f8f9fa', borderRadius: '24px', padding: '12px 20px', border: '1px solid #e0e0e0' }}>

                    <div style={{ position: 'relative' }} ref={dropdownRef}>
                      <button
                        onClick={() => setIsUploadDropdownOpen(!isUploadDropdownOpen)}
                        style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '4px', display: 'flex', alignItems: 'center' }}>
                        <Plus size={20} color="#004b87" />
                      </button>

                      {isUploadDropdownOpen && (
                        <div style={{
                          position: 'absolute',
                          bottom: '100%',
                          left: 0,
                          marginBottom: '12px',
                          background: '#1a1c1e',
                          borderRadius: '12px',
                          boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
                          width: '240px',
                          padding: '8px 0',
                          zIndex: 1000,
                          border: '1px solid #333'
                        }}>
                          <div
                            style={{
                              padding: '12px 16px',
                              cursor: 'pointer',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '12px',
                              color: '#fff',
                              transition: 'background 0.2s',
                              borderRadius: '8px'
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.background = '#333'}
                            onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                            onClick={() => fileInputRef.current.click()}
                          >
                            <Upload size={18} color="#aaa" />
                            <div style={{ textAlign: 'left' }}>
                              <div style={{ fontSize: '14px', fontWeight: 500 }}>Upload</div>
                              <div style={{ fontSize: '12px', color: '#888' }}>Provide local files</div>
                            </div>
                          </div>

                          <div
                            style={{
                              padding: '12px 16px',
                              cursor: 'pointer',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '12px',
                              color: '#fff',
                              transition: 'background 0.2s',
                              borderRadius: '8px'
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.background = '#333'}
                            onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                            onClick={handleYouTubeUrl}
                          >
                            <Youtube size={18} color="#aaa" />
                            <div style={{ textAlign: 'left' }}>
                              <div style={{ fontSize: '14px', fontWeight: 500 }}>YouTube video link</div>
                              <div style={{ fontSize: '12px', color: '#888' }}>Provide a link to a YouTube video</div>
                            </div>
                          </div>

                          <div style={{ padding: '8px 16px', display: 'flex', alignItems: 'center', gap: '12px', color: '#444', opacity: 0.5, cursor: 'not-allowed' }}>
                            <Link size={16} /> <span style={{ fontSize: '13px' }}>By URL</span>
                          </div>
                          <div style={{ padding: '8px 16px', display: 'flex', alignItems: 'center', gap: '12px', color: '#444', opacity: 0.5, cursor: 'not-allowed' }}>
                            <Cloud size={16} /> <span style={{ fontSize: '13px' }}>Google Drive</span>
                          </div>
                        </div>
                      )}
                    </div>

                    <input
                      type="text"
                      placeholder={isFactSetConnected ? "Ask FactSet anything..." : "How can FactSet help?"}
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleSendChat()}
                      style={{ border: 'none', background: 'transparent', flex: 1, fontSize: '14px', outline: 'none' }}
                    />
                    <input
                      type="file"
                      ref={fileInputRef}
                      onChange={handleImageUpload}
                      accept="image/*"
                      style={{ display: 'none' }}
                    />
                  </div>
                  {selectedImage && (
                    <div style={{ maxWidth: '800px', margin: '8px auto', position: 'relative', width: 'fit-content' }}>
                      <img src={selectedImage} style={{ height: '60px', borderRadius: '4px', border: '1px solid #ddd' }} alt="Preview" />
                      <button
                        onClick={() => setSelectedImage(null)}
                        style={{ position: 'absolute', top: '-8px', right: '-8px', background: '#dc3545', color: '#fff', border: 'none', borderRadius: '50%', width: '18px', height: '18px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', padding: 0 }}
                      >
                        <X size={12} />
                      </button>
                    </div>
                  )}
                  {selectedVideoUrl && (
                    <div style={{ maxWidth: '800px', margin: '8px auto', position: 'relative', width: 'fit-content', background: '#f8f9fa', padding: '6px 12px', borderRadius: '6px', border: '1px solid #dee2e6', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Youtube size={16} color="#ff0000" />
                      <span style={{ fontSize: '12px', color: '#004b87', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '300px' }}>{selectedVideoUrl}</span>
                      <button
                        onClick={() => setSelectedVideoUrl(null)}
                        style={{ background: 'none', border: 'none', color: '#666', cursor: 'pointer', padding: 2, display: 'flex' }}
                      >
                        <X size={14} />
                      </button>
                    </div>
                  )}
                </div>
              </>
            )}
            {maximizedTab === 'workflow' && (
              <div style={{ flex: 1, overflowY: 'auto', padding: '20px', background: '#fafafa' }}>
                <ReasoningChain
                  steps={reasoningSteps}
                  isExpanded={true}
                  onToggleExpand={() => { }}
                  thinkingTime={thinkingTime}
                />
              </div>
            )}
            {maximizedTab === 'trace' && (
              <div style={{ flex: 1, overflowY: 'auto', background: '#fff' }}>
                <TraceLog logs={traceLogs} isMaximized={true} />
              </div>
            )}
            {maximizedTab === 'agent' && (
              <div style={{ flex: 1, overflowY: 'auto', padding: '40px', background: '#fafafa' }}>
                <div style={{ maxWidth: '900px', margin: '0 auto' }}>
                  <h2 style={{ fontSize: '24px', color: '#004b87', marginBottom: '24px', borderBottom: '2px solid #004b87', paddingBottom: '8px', display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <Sparkles size={24} />
                    AI Agent Configuration
                  </h2>

                  {!agentConfig ? (
                    <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>Loading configuration...</div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
                      {/* Standard Agent */}
                      <section style={{ background: '#fff', borderRadius: '12px', padding: '24px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)', border: '1px solid #eee' }}>
                        <h3 style={{ fontSize: '18px', color: '#333', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#6c757d' }}></div>
                          Standard Assistant: <span style={{ color: '#004b87' }}>{agentConfig.standard_agent.name}</span>
                        </h3>
                        <div style={{ marginBottom: '20px' }}>
                          <h4 style={{ fontSize: '14px', color: '#666', marginBottom: '8px', fontWeight: 600 }}>System Instructions:</h4>
                          <div style={{ background: '#f8f9fa', padding: '16px', borderRadius: '8px', fontSize: '13px', color: '#444', lineHeight: '1.6', whiteSpace: 'pre-wrap', border: '1px solid #eee' }}>
                            {agentConfig.standard_agent.instruction}
                          </div>
                        </div>
                        <div>
                          <h4 style={{ fontSize: '14px', color: '#666', marginBottom: '8px', fontWeight: 600 }}>Tools & Capabilities:</h4>
                          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '12px' }}>
                            {agentConfig.standard_agent.tools.map((tool, i) => (
                              <div key={i} style={{ background: '#f0f4f8', padding: '12px', borderRadius: '8px', border: '1px solid #dce4ec' }}>
                                <div style={{ fontWeight: 600, color: '#004b87', fontSize: '12px', marginBottom: '4px' }}>{tool.name}</div>
                                <div style={{ fontSize: '11px', color: '#555' }}>{tool.description}</div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </section>

                      {/* FactSet Agent */}
                      <section style={{ background: '#fff', borderRadius: '12px', padding: '24px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)', border: '1px solid #eee' }}>
                        <h3 style={{ fontSize: '18px', color: '#333', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#28a745' }}></div>
                          FactSet Analyst: <span style={{ color: '#28a745' }}>{agentConfig.factset_agent.name}</span>
                        </h3>
                        <div style={{ marginBottom: '20px' }}>
                          <h4 style={{ fontSize: '14px', color: '#666', marginBottom: '8px', fontWeight: 600 }}>System Instructions:</h4>
                          <div style={{ background: '#f8f9fa', padding: '16px', borderRadius: '8px', fontSize: '13px', color: '#444', lineHeight: '1.6', whiteSpace: 'pre-wrap', border: '1px solid #eee' }}>
                            {agentConfig.factset_agent.instruction}
                          </div>
                        </div>
                        <div>
                          <h4 style={{ fontSize: '14px', color: '#666', marginBottom: '8px', fontWeight: 600 }}>Tools & Capabilities:</h4>
                          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '12px' }}>
                            {agentConfig.factset_agent.tools.map((tool, i) => (
                              <div key={i} style={{ background: '#e6ffea', padding: '12px', borderRadius: '8px', border: '1px solid #c3e6cb' }}>
                                <div style={{ fontWeight: 600, color: '#28a745', fontSize: '12px', marginBottom: '4px' }}>{tool.name}</div>
                                <div style={{ fontSize: '11px', color: '#155724' }}>{tool.description}</div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </section>
                    </div>
                  )}
                </div>
              </div>
            )}
            {maximizedTab === 'errors' && (
              <div style={{ flex: 1, overflowY: 'auto', padding: '40px', background: '#fafafa' }}>
                <div style={{ maxWidth: '900px', margin: '0 auto' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', borderBottom: '2px solid #dc3545', paddingBottom: '8px' }}>
                    <h2 style={{ fontSize: '24px', color: '#dc3545', margin: 0, display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <AlertCircle size={24} />
                      System Error Audit Log
                    </h2>
                    <button
                      onClick={() => setAllErrors([])}
                      style={{ padding: '6px 12px', background: '#fff', border: '1px solid #ddd', borderRadius: '6px', fontSize: '12px', cursor: 'pointer' }}
                    >
                      Clear Log
                    </button>
                  </div>

                  {allErrors.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '60px', color: '#999', background: '#fff', borderRadius: '12px', border: '1px dashed #ccc' }}>
                      <CheckCircle size={48} style={{ color: '#28a745', marginBottom: '16px', opacity: 0.5 }} />
                      <p>No errors detected in this session.</p>
                    </div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                      {[...allErrors].reverse().map((err, i) => (
                        <div key={i} style={{ background: '#fff', borderRadius: '12px', padding: '20px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)', borderLeft: '4px solid #dc3545' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                            <span style={{ fontSize: '11px', fontWeight: 600, color: '#dc3545', textTransform: 'uppercase' }}>Error Event</span>
                            <span style={{ fontSize: '11px', color: '#999' }}>{err.timestamp}</span>
                          </div>
                          <div style={{ background: '#fff5f5', padding: '12px', borderRadius: '8px', border: '1px solid #fed7d7', color: '#c53030', fontSize: '13px', fontFamily: 'monospace', marginBottom: '12px', whiteSpace: 'pre-wrap' }}>
                            {err.message}
                          </div>
                          {err.userQuery && (
                            <div style={{ fontSize: '12px', color: '#666', borderTop: '1px solid #eee', paddingTop: '10px' }}>
                              <span style={{ fontWeight: 600 }}>Originating Query:</span> "{err.userQuery}"
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </>
        ) : (
          /* Standard Sidebar Content - Collapsible Widgets */
          <>
            {/* Summary Widget */}
            <div className="reasoning-chain-container" style={{ marginBottom: '12px' }}>
              <div
                className="reasoning-header"
                onClick={() => setIsPerformanceExpanded(!isPerformanceExpanded)}
              >
                <div className="reasoning-title">
                  <Sparkles size={14} className="icon-pulse" />
                  <span>Stock Performance & Summary</span>
                </div>
                {isPerformanceExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
              </div>
              {isPerformanceExpanded && (
                <div className="reasoning-body" style={{ padding: '12px' }}>
                  {summaryLoading ? (
                    <p className="small">Generating AI Summary...</p>
                  ) : aiSummary ? (
                    <div className="summary-section ai-powered">
                      <div className="markdown-content">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>{aiSummary}</ReactMarkdown>
                      </div>
                    </div>
                  ) : (
                    <p className="small">Select a ticker to generate real-time AI insights.</p>
                  )}
                </div>
              )}
            </div>

            {/* Trace Log Widget */}
            <div className="reasoning-chain-container" style={{ marginBottom: '12px' }}>
              <div
                className="reasoning-header"
                onClick={() => setIsTraceExpanded(!isTraceExpanded)}
              >
                <div className="reasoning-title">
                  <Terminal size={14} style={{ color: 'var(--brand)' }} />
                  <span>Session Trace Log <span className="step-count">({traceLogs.length})</span></span>
                </div>
                {isTraceExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
              </div>
              {isTraceExpanded && (
                <div className="reasoning-body" style={{ padding: '0', borderTop: '1px solid #eee' }}>
                  <TraceLog logs={traceLogs} />
                </div>
              )}
            </div>

            <div className="divider" style={{ height: '1px', background: 'var(--border-light)', margin: '16px 0' }}></div>

            {/* Reasoning Visualization Component (Collapsible) */}
            <ErrorBoundary fallback={<div className="small error-msg" style={{ padding: '8px' }}>Unable to display reasoning chain.</div>}>
              <ReasoningChain
                steps={reasoningSteps}
                isExpanded={isReasoningExpanded}
                onToggleExpand={() => setIsReasoningExpanded(!isReasoningExpanded)}
                thinkingTime={thinkingTime}
              />
            </ErrorBoundary>

            {/* Chat Messages Area (Dynamic Height) */}
            <div className="chat-messages" style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '12px',
              flex: 1,
              overflowY: 'auto',
              padding: '8px 4px',
              marginTop: '8px'
            }}>
              {messages.map((msg, idx) => (
                <div key={idx} className={`msg ${msg.role}`} style={{
                  fontSize: '13px',
                  lineHeight: '1.5',
                  padding: '10px 14px',
                  borderRadius: '12px',
                  maxWidth: '92%',
                  alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                  background: msg.role === 'user' ? '#e6f0ff' : '#f0f2f5',
                  color: msg.role === 'user' ? '#004b87' : 'var(--text-primary)',
                  border: msg.role === 'user' ? '1px solid #cce0ff' : '1px solid #e6ebf1',
                  wordBreak: 'break-word',
                  overflow: 'visible',
                  boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
                }}>
                  {msg.image && (
                    <div style={{ marginBottom: '6px' }}>
                      <img src={msg.image} alt="Uploaded" style={{ maxWidth: '100%', borderRadius: '6px', border: '1px solid #ddd' }} />
                    </div>
                  )}
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.text}</ReactMarkdown>
                </div>
              ))}
              {chatLoading && (
                <div className="small blinking" style={{
                  fontStyle: 'italic',
                  color: 'var(--text-muted)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '8px 12px',
                  fontSize: '12px',
                  background: '#fdfdfd',
                  borderRadius: '8px',
                  border: '1px dashed #eee',
                  alignSelf: 'flex-start'
                }}>
                  {messages[messages.length - 1]?.text ? 'Assistant is working...' : 'Assistant is thinking...'}
                  <span>({(thinkingTime / 1000).toFixed(2)}s)</span>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            {/* Input Area (Bottom) */}
            <div className="chat-input-container" style={{ marginTop: 8, gap: 12, display: 'flex', alignItems: 'center', background: '#fff', borderRadius: '12px', padding: '10px 14px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}>

              <div style={{ position: 'relative' }} ref={dropdownRef}>
                <button
                  onClick={() => setIsUploadDropdownOpen(!isUploadDropdownOpen)}
                  style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '4px', display: 'flex', alignItems: 'center' }}>
                  <Plus size={16} color="#004b87" />
                </button>

                {isUploadDropdownOpen && (
                  <div style={{
                    position: 'absolute',
                    bottom: '100%',
                    left: 0,
                    marginBottom: '10px',
                    background: '#1a1c1e',
                    borderRadius: '8px',
                    boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
                    width: '200px',
                    padding: '6px 0',
                    zIndex: 1000,
                    border: '1px solid #333'
                  }}>
                    <div
                      style={{
                        padding: '10px 14px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '10px',
                        color: '#fff',
                        transition: 'background 0.2s'
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.background = '#333'}
                      onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                      onClick={() => fileInputRef.current.click()}
                    >
                      <Upload size={16} color="#aaa" />
                      <div style={{ fontSize: '13px', fontWeight: 500 }}>Upload</div>
                    </div>

                    <div
                      style={{
                        padding: '10px 14px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '10px',
                        color: '#fff',
                        transition: 'background 0.2s'
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.background = '#333'}
                      onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                      onClick={handleYouTubeUrl}
                    >
                      <Youtube size={16} color="#aaa" />
                      <div style={{ fontSize: '13px', fontWeight: 500 }}>YouTube video link</div>
                    </div>
                  </div>
                )}
              </div>

              <input
                type="text"
                placeholder={isFactSetConnected ? "Ask FactSet anything..." : "How can FactSet help?"}
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSendChat()}
                style={{ border: 'none', background: 'transparent', flex: 1, fontSize: '13px', outline: 'none' }}
              />
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleImageUpload}
                accept="image/*"
                style={{ display: 'none' }}
              />
            </div>
            {selectedImage && (
              <div style={{ position: 'relative', width: 'fit-content', marginTop: '4px', marginLeft: '4px' }}>
                <img src={selectedImage} style={{ height: '40px', borderRadius: '4px', border: '1px solid #ddd' }} alt="Preview" />
                <button
                  onClick={() => setSelectedImage(null)}
                  style={{ position: 'absolute', top: '-6px', right: '-6px', background: '#dc3545', color: '#fff', border: 'none', borderRadius: '50%', width: '14px', height: '14px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', padding: 0 }}
                >
                  <X size={10} />
                </button>
              </div>
            )}
            {selectedVideoUrl && (
              <div style={{ position: 'relative', width: 'fit-content', marginTop: '4px', marginLeft: '4px', background: '#f8f9fa', padding: '4px 8px', borderRadius: '4px', border: '1px solid #dee2e6', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Youtube size={14} color="#ff0000" />
                <span style={{ fontSize: '11px', color: '#004b87', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '180px' }}>{selectedVideoUrl}</span>
                <button
                  onClick={() => setSelectedVideoUrl(null)}
                  style={{ background: 'none', border: 'none', color: '#666', cursor: 'pointer', padding: 1, display: 'flex' }}
                >
                  <X size={12} />
                </button>
              </div>
            )}
          </>
        )
        }

        {
          showAuthModal && (
            <div style={{
              position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
              background: 'rgba(255,255,255,0.95)', zIndex: 100,
              display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '20px'
            }}>
              <h3>Authenticate with FactSet</h3>
              <p>Please enter the redirect URL:</p>
              <input
                type="text"
                value={authInput}
                onChange={(e) => setAuthInput(e.target.value)}
                style={{ width: '100%', padding: '8px', marginBottom: '12px', border: '1px solid #ccc' }}
              />
              <div style={{ display: 'flex', gap: '8px' }}>
                <button onClick={() => setShowAuthModal(false)}>Cancel</button>
                <button onClick={handleAuthSubmit} style={{ background: '#004b87', color: '#fff' }}>Connect</button>
              </div>
            </div>
          )
        }
      </div>

      <style jsx="true">{`
        @keyframes blink {
          0% { opacity: 1; }
          50% { opacity: 0.4; }
          100% { opacity: 1; }
        }
        .blinking {
          animation: blink 1.5s linear infinite;
        }
        .right-sidebar {
          width: 450px;
          background: #fff;
          border-left: 1px solid var(--border-light);
          display: flex;
          flex-direction: column;
          padding: 16px;
          transition: width 0.3s ease, position 0ms;
        }
        .right-sidebar.maximized {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: 1000;
            border-left: none;
            padding: 24px;
        }

        .right-sidebar-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }
        .tab {
          background: none;
          border: none;
          padding: 4px 0;
          font-size: 11px;
          font-weight: 600;
          color: #888;
          cursor: pointer;
          border-bottom: 2px solid transparent;
          display: flex;
          align-items: center;
          gap: 6px;
        }
        .tab.active {
          color: #004b87;
          border-bottom-color: #004b87;
        }
        
        .chat-input-container {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 12px;
          background: #f8f9fa;
          border-radius: 20px;
          border: 1px solid #e9ecef;
        }
        .chat-input-container input {
          border: none;
          background: transparent;
          flex: 1;
          font-size: 12px;
          outline: none;
        }
        .summary-section {
          margin-bottom: 16px;
        }
        .summary-section h3 {
          font-size: 12px;
          font-weight: 700;
          color: #495057;
          margin-bottom: 4px;
        }
        .summary-section p, .summary-section li {
          font-size: 11px;
          color: #666;
          line-height: 1.4;
        }
        .insights-list {
          padding-left: 16px;
          margin: 0;
        }
        .link {
          color: #004b87;
          text-decoration: underline;
          cursor: pointer;
        }
        .small { font-size: 10px; color: #888; }
        
        .markdown-content p { margin-bottom: 8px; }
        .markdown-content ul { padding-left: 16px; margin-bottom: 8px; }
        
        /* Table Styles for Chat */
        .msg table {
          border-collapse: collapse;
          width: 100%;
          margin: 8px 0;
          font-size: 10px;
          display: block;
          overflow-x: auto;
        }
        .msg th, .msg td {
          border: 1px solid #e9ecef;
          padding: 6px 8px;
          text-align: left;
          min-width: 80px;
        }
        .msg th {
          background-color: #f8f9fa;
          font-weight: 700;
          color: #004b87;
        }
        .msg tr:nth-child(even) {
          background-color: #fafbfc;
        }
      `}</style>
    </aside >
  );
};

export default RightSidebar;
