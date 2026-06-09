import { useState, useEffect, useRef } from 'react';
import { newsArticles } from './data/news';
import { sendChatMessage } from './services/gemini';
import { formatMarkdown } from './utils/formatter';
import './App.css';

function App() {
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [activeCategory, setActiveCategory] = useState('ALL');
  const [isChatOpen, setIsChatOpen] = useState(true);
  const [chatHistory, setChatHistory] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [liveTime, setLiveTime] = useState(new Date().toLocaleTimeString());
  const [chatWidth, setChatWidth] = useState(400);
  const [currentLatency, setCurrentLatency] = useState(0);

  const chatMessagesContainerRef = useRef(null);
  const isResizingRef = useRef(false);

  const startResize = (e) => {
    isResizingRef.current = true;
    document.addEventListener('mousemove', resize);
    document.addEventListener('mouseup', stopResize);
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
  };

  const resize = (e) => {
    if (!isResizingRef.current) return;
    const newWidth = window.innerWidth - e.clientX;
    if (newWidth > 280 && newWidth < window.innerWidth * 0.6) {
      setChatWidth(newWidth);
    }
  };

  const stopResize = () => {
    isResizingRef.current = false;
    document.removeEventListener('mousemove', resize);
    document.removeEventListener('mouseup', stopResize);
    document.body.style.cursor = 'default';
    document.body.style.userSelect = 'auto';
  };

  useEffect(() => {
    const timer = setInterval(() => {
      setLiveTime(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const container = chatMessagesContainerRef.current;
    if (container) {
      const handleScroll = () => {
        container.scrollTo({
          top: container.scrollHeight,
          behavior: 'smooth'
        });
      };
      // Scroll immediately and queue a retry after layout rendering completes
      handleScroll();
      const timer = setTimeout(handleScroll, 100);
      return () => clearTimeout(timer);
    }
  }, [chatHistory, isGenerating]);

  const filteredArticles = activeCategory === 'ALL'
    ? newsArticles
    : newsArticles.filter(art => art.category === activeCategory);

  const handleSelectArticle = (article) => {
    setSelectedArticle(article);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleDiscussArticle = (article) => {
    setSelectedArticle(article);
    setIsChatOpen(true);
    
    const introMsg = {
      role: 'bot',
      content: `I've loaded the article **"${article.title}"** into my active context. Ask me anything about it! For example, you can ask me to:
* Summarize the main points
* Analyze the author's arguments
* Compare this news to current industry standards`
    };
    
    setChatHistory(prev => [...prev, {
      role: 'system_notification',
      content: `Focused on article: ${article.title}`
    }, introMsg]);
  };

  const handleClearContext = () => {
    setSelectedArticle(null);
    setChatHistory(prev => [...prev, {
      role: 'system_notification',
      content: 'Cleared active article context. Now discussing general homepage news.'
    }]);
  };

  const handleQuickAsk = async (question) => {
    const msgId = `quick-${Date.now()}`;

    // Add user message + loading placeholder
    setChatHistory(prev => [
      ...prev,
      {
        role: 'user',
        content: `/btw ${question}`,
        isQuick: true
      },
      {
        role: 'bot',
        content: '',
        isQuick: true,
        isLoading: true,
        tempId: msgId
      }
    ]);

    const startTime = performance.now();

    try {
      const response = await fetch('http://localhost:8001/api/quick', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: question })
      });

      if (!response.ok) {
        const errJson = await response.json().catch(() => ({}));
        throw new Error(errJson.error?.message || 'Quick response failed');
      }

      const result = await response.json();
      const finalLatency = (performance.now() - startTime) / 1000;

      setChatHistory(prev => prev.map(msg => 
        msg.tempId === msgId
          ? { 
              role: 'bot', 
              content: result.text,
              groundingMetadata: result.groundingMetadata,
              latency: finalLatency,
              isQuick: true,
              isLoading: false
            }
          : msg
      ));
    } catch (error) {
      console.error(error);
      setChatHistory(prev => prev.map(msg => 
        msg.tempId === msgId
          ? { 
              role: 'bot', 
              content: `Quick response failed: ${error.message || 'Server error.'}`,
              isQuick: true,
              isLoading: false,
              isError: true
            }
          : msg
      ));
    }
  };

  const handleSendMessage = async (e) => {
    if (e) e.preventDefault();
    
    const rawInput = chatInput.trim();
    if (!rawInput) return;

    if (rawInput.startsWith('/btw ')) {
      const question = rawInput.slice(5).trim();
      if (!question) return;
      setChatInput('');
      handleQuickAsk(question);
      return;
    }

    if (isGenerating) return;

    const userMessageText = rawInput;
    const newUserMessage = { role: 'user', content: userMessageText };
    
    setChatHistory(prev => [...prev, newUserMessage]);
    setChatInput('');
    setIsGenerating(true);
    setErrorMessage('');
    setCurrentLatency(0);

    const startTime = performance.now();
    const latencyInterval = setInterval(() => {
      setCurrentLatency((performance.now() - startTime) / 1000);
    }, 100);

    try {
      const historyForApi = [...chatHistory, newUserMessage]
        .filter(msg => msg.role === 'user' || msg.role === 'bot');

      const result = await sendChatMessage(
        historyForApi,
        selectedArticle,
        newsArticles
      );

      const endTime = performance.now();
      const finalLatency = (endTime - startTime) / 1000;
      clearInterval(latencyInterval);
      setCurrentLatency(0);

      setChatHistory(prev => [...prev, { 
        role: 'bot', 
        content: result.text,
        groundingMetadata: result.groundingMetadata,
        latency: finalLatency
      }]);
    } catch (error) {
      console.error(error);
      clearInterval(latencyInterval);
      setCurrentLatency(0);
      setErrorMessage(error.message || 'Something went wrong when connecting to Gemini.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleQuickPrompt = (promptText) => {
    setChatInput(promptText);
    setTimeout(() => {
      const inputEl = document.querySelector('.chat-input-field');
      if (inputEl) inputEl.focus();
    }, 50);
  };

  const featuredArticle = newsArticles[0];
  const sideArticles = newsArticles.slice(1, 4);
  const remainingArticles = newsArticles.slice(4);

  return (
    <div className="app-container">
      <header className="verge-header">
        <div className="header-top">
          <div className="verge-logo-container">
            <a href="#" className="logo-main" onClick={() => setSelectedArticle(null)}>
              AETHER
            </a>
            <div className="logo-sub">/ JOURNAL</div>
          </div>

          <div className="header-meta">
            <button 
              className="chat-toggle-btn" 
              onClick={() => setIsChatOpen(!isChatOpen)}
            >
              CHAT {isChatOpen ? '[CLOSE]' : '[OPEN]'}
            </button>
          </div>
        </div>

        <nav className="nav-bar">
          <ul className="nav-links">
            {['ALL', 'MATERIALS', 'SUSTAINABILITY', 'RESIDENTIAL', 'URBANISM', 'DESIGN'].map(cat => (
              <li key={cat}>
                <a 
                  href="#" 
                  className={`nav-link ${activeCategory === cat ? 'active' : ''}`}
                  onClick={(e) => {
                    e.preventDefault();
                    setActiveCategory(cat);
                    setSelectedArticle(null);
                  }}
                >
                  {cat}
                </a>
              </li>
            ))}
          </ul>
        </nav>
      </header>

      <main className={`main-content ${isChatOpen ? 'chat-open' : ''}`}>
        <section className="news-section">
          <div className="news-container">
            {selectedArticle ? (
              <article className="single-article-view" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                <button 
                  className="chat-toggle-btn" 
                  onClick={() => setSelectedArticle(null)}
                  style={{ alignSelf: 'flex-start', borderBottom: '1px solid var(--text-color)' }}
                >
                  ← BACK TO HOMEPAGE
                </button>

                <header className="article-header" style={{ paddingBottom: '1.5rem' }}>
                  <div style={{ color: 'var(--text-muted)', fontWeight: 600, fontSize: '0.7rem', letterSpacing: '2px', marginBottom: '1rem', textTransform: 'uppercase' }}>
                    {selectedArticle.category}
                  </div>
                  <h1 className="article-title" style={{ fontSize: '3rem', fontWeight: 500, lineHeight: 1.1, margin: '0.5rem 0' }}>
                    {selectedArticle.title}
                  </h1>
                  <p className="article-subtitle" style={{ fontSize: '1.1rem', color: 'var(--text-muted)', lineHeight: 1.5, margin: '1.5rem 0 0 0' }}>
                    {selectedArticle.subtitle}
                  </p>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '2rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                    <div>
                      By <strong style={{ color: 'var(--text-color)' }}>{selectedArticle.author}</strong> | {selectedArticle.date}
                    </div>
                    <div>{selectedArticle.readTime}</div>
                  </div>
                </header>

                <div 
                  style={{ 
                    backgroundColor: 'var(--bg-panel)',
                    borderLeft: '2px solid var(--text-color)',
                    padding: '1.5rem', 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center',
                    gap: '1rem'
                  }}
                >
                  <div>
                    <h4 style={{ fontSize: '0.9rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.2rem' }}>Interact with this article</h4>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Ask Aether AI to summarize or critique this project.</p>
                  </div>
                  <button 
                    className="chat-toggle-btn"
                    onClick={() => handleDiscussArticle(selectedArticle)}
                  >
                    DISCUSS PROJECT
                  </button>
                </div>

                <div className="hero-image-placeholder" style={{ height: '450px' }}>
                  {selectedArticle.imageUrl ? (
                    <img src={selectedArticle.imageUrl} alt={selectedArticle.title} className="card-image" />
                  ) : (
                    <div className="card-image-fallback" style={{ background: selectedArticle.imageGradient }}></div>
                  )}
                </div>

                <div className="article-body-content" style={{ fontSize: '1rem', lineHeight: '1.7', color: 'var(--text-color)', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                  {selectedArticle.content.split('\n\n').map((paragraph, idx) => (
                    <p key={idx}>{paragraph}</p>
                  ))}
                </div>
              </article>
            ) : (
              <>
                {activeCategory === 'ALL' ? (
                  <>
                    <div className="hero-grid">
                      <div className="hero-featured" onClick={() => handleSelectArticle(featuredArticle)}>
                        <div className="hero-image-placeholder">
                          {featuredArticle.imageUrl ? (
                            <img src={featuredArticle.imageUrl} alt={featuredArticle.title} className="card-image" />
                          ) : (
                            <div className="card-image-fallback" style={{ background: featuredArticle.imageGradient }}></div>
                          )}
                          <span className="category-tag">
                            {featuredArticle.category}
                          </span>
                        </div>
                        <div className="hero-meta">
                          <span>{featuredArticle.author}</span> • <span>{featuredArticle.date}</span>
                        </div>
                        <h2 className="hero-headline">{featuredArticle.title}</h2>
                        <p className="hero-subtitle">{featuredArticle.summary}</p>
                      </div>
 
                      <div className="hero-side-list">
                        {sideArticles.map(art => (
                          <div key={art.id} className="side-article-item" onClick={() => handleSelectArticle(art)}>
                            <span className="side-item-category">
                              {art.category}
                            </span>
                            <h3 className="side-item-headline">{art.title}</h3>
                            <div className="side-item-meta">
                              <span>{art.author}</span> • <span>{art.date}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
 
                    <div className="news-feed-grid">
                      {remainingArticles.map(art => (
                        <div key={art.id} className="feed-card" onClick={() => handleSelectArticle(art)}>
                          <div className="feed-image">
                            {art.imageUrl ? (
                              <img src={art.imageUrl} alt={art.title} className="card-image" />
                            ) : (
                              <div className="card-image-fallback" style={{ background: art.imageGradient }}></div>
                            )}
                            <span className="category-tag">
                              {art.category}
                            </span>
                          </div>
                          <span className="feed-category">
                            {art.category}
                          </span>
                          <h3 className="feed-headline">{art.title}</h3>
                          <p className="feed-summary">{art.summary}</p>
                          <div className="feed-meta">
                            <span>{art.author}</span> • <span>{art.date}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </>
                ) : (
                  <div className="news-feed-grid">
                    {filteredArticles.map(art => (
                      <div key={art.id} className="feed-card" onClick={() => handleSelectArticle(art)}>
                        <div className="feed-image">
                          {art.imageUrl ? (
                            <img src={art.imageUrl} alt={art.title} className="card-image" />
                          ) : (
                            <div className="card-image-fallback" style={{ background: art.imageGradient }}></div>
                          )}
                          <span className="category-tag">
                            {art.category}
                          </span>
                        </div>
                        <span className="feed-category">
                          {art.category}
                        </span>
                        <h3 className="feed-headline">{art.title}</h3>
                        <p className="feed-summary">{art.summary}</p>
                        <div className="feed-meta">
                          <span>{art.author}</span> • <span>{art.date}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        </section>

        {isChatOpen && (
          <aside className="chat-drawer" style={{ width: `${chatWidth}px` }}>
            <div className="resize-handle" onMouseDown={startResize} />
            <div className="chat-header">
              <div className="chat-header-title">
                <h3>AETHER AI</h3>
                <span className="gemini-badge">GEMINI 2.5 FLASH</span>
              </div>
              <button className="chat-close-btn" onClick={() => setIsChatOpen(false)}>×</button>
            </div>

            <div className="active-context-panel">
              <div className="context-info">
                <span className="context-icon">💡</span>
                {selectedArticle ? (
                  <span className="context-title">Reading: {selectedArticle.title}</span>
                ) : (
                  <span className="context-title">Browsing: Homepage Articles</span>
                )}
              </div>
              {selectedArticle && (
                <button className="clear-context-btn" onClick={handleClearContext}>
                  Clear Context
                </button>
              )}
            </div>

            <div className="chat-messages-container" ref={chatMessagesContainerRef}>
              {chatHistory.length === 0 ? (
                <div className="chat-empty-state">
                  <div className="chat-empty-icon">⌘</div>
                  <div className="chat-empty-text">
                    <h4>Interact with the headlines</h4>
                    <p>Select any project on the left or use the prompts below to chat about modern architecture.</p>
                  </div>

                  <div className="chat-suggestions">
                    <button className="suggestion-btn" onClick={() => handleQuickPrompt("Summarize all the architecture articles on the homepage in 3 bullet points.")}>
                      Summarize today's headlines
                    </button>
                    <button className="suggestion-btn" onClick={() => handleQuickPrompt("What are the main benefits and challenges of building skyscrapers with mass timber?")}>
                      Tell me about mass timber high-rises
                    </button>
                    <button className="suggestion-btn" onClick={() => handleQuickPrompt("How is 3D printing being used to build houses, and what are the benefits?")}>
                      Find articles on 3D printed housing
                    </button>
                  </div>
                </div>
              ) : (
                chatHistory.map((msg, index) => {
                  if (msg.role === 'system_notification') {
                    return (
                      <div key={index} style={{ textAlign: 'center', margin: '1rem 0', fontSize: '0.7rem', color: 'var(--text-muted)', borderTop: '0.5px solid var(--border-color)', paddingTop: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                        {msg.content}
                      </div>
                    );
                  }
                  
                  const isUser = msg.role === 'user';
                  const isQuick = msg.isQuick;
                  const isLoading = msg.isLoading;

                  if (isLoading) {
                    return (
                      <div key={index} className="message-wrapper bot quick">
                        <span className="message-sender">
                          AETHER AI <span className="quick-badge">/btw</span>
                        </span>
                        <div className="message-bubble quick-loading">
                          <span className="yazdani-spinner" /> <span className="sweep-text">Retrieving quick reference...</span>
                        </div>
                      </div>
                    );
                  }
                  
                  return (
                    <div key={index} className={`message-wrapper ${isUser ? 'user' : 'bot'} ${isQuick ? 'quick' : ''}`}>
                      <span className="message-sender">
                        {isUser ? 'USER' : 'AETHER AI'} {isQuick && <span className="quick-badge">/btw</span>}
                      </span>
                      <div className="message-bubble">
                        {msg.role === 'bot' ? formatMarkdown(msg.content) : msg.content}
                        
                        {msg.role === 'bot' && msg.groundingMetadata && (
                          <div className="grounding-info" style={{ marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: '0.5px solid var(--border-color)', fontSize: '0.75rem' }}>
                            {msg.groundingMetadata.webSearchQueries && msg.groundingMetadata.webSearchQueries.length > 0 && (
                              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
                                <span>🔍</span>
                                <span>Searched: <em>"{msg.groundingMetadata.webSearchQueries.join(', ')}"</em></span>
                              </div>
                            )}
                            {msg.groundingMetadata.groundingChunks && msg.groundingMetadata.groundingChunks.length > 0 && (
                              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.2rem' }}>
                                <div style={{ fontWeight: 700, fontSize: '0.65rem', color: 'var(--text-muted)', letterSpacing: '0.5px', textTransform: 'uppercase' }}>Sources & Citations:</div>
                                <ul style={{ listStyle: 'none', paddingLeft: 0, display: 'flex', flexWrap: 'wrap', gap: '0.25rem 0.75rem' }}>
                                  {msg.groundingMetadata.groundingChunks
                                    .filter((chunk, idx, self) => 
                                      chunk.web && self.findIndex(c => c.web && c.web.uri === chunk.web.uri) === idx
                                    )
                                    .map((chunk, cIdx) => (
                                      <li key={cIdx}>
                                        <a href={chunk.web.uri} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--text-color)', textDecoration: 'underline', fontWeight: 500 }}>
                                          {chunk.web.title || "Source link"}
                                        </a>
                                      </li>
                                    ))
                                  }
                                </ul>
                              </div>
                            )}
                          </div>
                        )}
                        {msg.role === 'bot' && (
                          <div className="message-meta-footer">
                            <span>{msg.latency ? `[LATENCY: ${msg.latency.toFixed(2)}s]` : ''}</span>
                            <span>[MODEL: {isQuick ? 'GEMINI 3.1 FLASH LITE' : 'GEMINI 2.5 FLASH'}]</span>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })
              )}

              {isGenerating && (
                <div className="message-wrapper bot">
                  <span className="message-sender">AETHER AI</span>
                  <div className="message-bubble thinking-console">
                    Thinking... <span className="latency-timer">{currentLatency.toFixed(1)}s</span> <span className="blinking-cursor">█</span>
                  </div>
                </div>
              )}

              {errorMessage && (
                <div style={{ backgroundColor: 'var(--bg-color)', color: 'var(--text-color)', padding: '0.8rem', fontSize: '0.8rem', border: '0.5px solid var(--border-color)' }}>
                  <strong>Error:</strong> {errorMessage}
                </div>
              )}
            </div>

            <div className="chat-input-container">
              {(chatInput === '/' || chatInput === '/b' || chatInput === '/bt' || chatInput === '/btw') && (
                <div className="autocomplete-dropdown">
                  <button 
                    type="button" 
                    onClick={() => setChatInput('/btw ')}
                    className="autocomplete-item"
                  >
                    <span className="autocomplete-cmd">/btw</span>
                    <span className="autocomplete-hint">Type <kbd>/btw</kbd> for instant web-grounded response</span>
                  </button>
                </div>
              )}

              <form onSubmit={handleSendMessage} className="chat-input-form">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder={
                    isGenerating 
                      ? "Type /btw for quick answers while waiting..." 
                      : (selectedArticle ? "Ask about this project..." : "Ask about architecture news...")
                  }
                  className={`chat-input-field ${chatInput.startsWith('/btw') ? 'has-command' : ''}`}
                />
                <button 
                  type="submit" 
                  className={`chat-send-btn ${chatInput.startsWith('/btw') ? 'quick-send' : ''}`} 
                  disabled={!chatInput.trim()}
                >
                  {chatInput.startsWith('/btw') ? '⚡ Send' : 'Send'}
                </button>
              </form>
            </div>
          </aside>
        )}
      </main>
    </div>
  );
}

export default App;
