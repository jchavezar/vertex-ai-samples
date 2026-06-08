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

  const chatBottomRef = useRef(null);

  useEffect(() => {
    const timer = setInterval(() => {
      setLiveTime(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    if (chatBottomRef.current) {
      chatBottomRef.current.scrollIntoView({ behavior: 'smooth' });
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

  const handleSendMessage = async (e) => {
    if (e) e.preventDefault();
    if (!chatInput.trim() || isGenerating) return;

    const userMessageText = chatInput.trim();
    const newUserMessage = { role: 'user', content: userMessageText };
    
    setChatHistory(prev => [...prev, newUserMessage]);
    setChatInput('');
    setIsGenerating(true);
    setErrorMessage('');

    try {
      const historyForApi = [...chatHistory, newUserMessage]
        .filter(msg => msg.role === 'user' || msg.role === 'bot');

      const result = await sendChatMessage(
        historyForApi,
        selectedArticle,
        newsArticles
      );

      setChatHistory(prev => [...prev, { 
        role: 'bot', 
        content: result.text,
        groundingMetadata: result.groundingMetadata
      }]);
    } catch (error) {
      console.error(error);
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
              THE VERGE<span>.</span>
            </a>
            <div className="logo-sub">Chat Portal</div>
          </div>

          <div className="header-meta">
            <div className="meta-item">
              <strong>EST. 2011</strong>
            </div>
            <div className="meta-item">
              <span>⏰</span> {liveTime}
            </div>
            <button 
              className="chat-toggle-btn" 
              onClick={() => setIsChatOpen(!isChatOpen)}
              style={{ backgroundColor: isChatOpen ? '#222' : 'var(--accent-verge)' }}
            >
              💬 {isChatOpen ? 'Close Chat' : 'Open Chat'}
            </button>
          </div>
        </div>

        <nav className="nav-bar">
          <ul className="nav-links">
            {['ALL', 'TECH', 'REVIEWS', 'SCIENCE', 'GAMING', 'DESIGN'].map(cat => (
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
              <article className="single-article-view" style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                <button 
                  className="modal-btn-secondary" 
                  onClick={() => setSelectedArticle(null)}
                  style={{ alignSelf: 'flex-start', display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 1rem', cursor: 'pointer' }}
                >
                  ← Back to Homepage
                </button>

                <header className="article-header" style={{ borderBottom: '1px solid var(--border-light)', paddingBottom: '1.5rem' }}>
                  <div style={{ color: selectedArticle.accentColor, fontWeight: 800, fontSize: '0.8rem', letterSpacing: '2px', marginBottom: '0.5rem' }}>
                    {selectedArticle.category}
                  </div>
                  <h1 className="article-title" style={{ fontFamily: 'var(--font-serif)', fontSize: '3rem', fontWeight: 900, lineHeight: 1.1, margin: '0.5rem 0' }}>
                    {selectedArticle.title}
                  </h1>
                  <p className="article-subtitle" style={{ fontSize: '1.25rem', color: 'var(--text-sub)', lineHeight: 1.4, margin: '1rem 0' }}>
                    {selectedArticle.subtitle}
                  </p>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1.5rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    <div>
                      By <strong style={{ color: 'var(--text-main)' }}>{selectedArticle.author}</strong> | {selectedArticle.date}
                    </div>
                    <div>{selectedArticle.readTime}</div>
                  </div>
                </header>

                <div 
                  style={{ 
                    background: `linear-gradient(90deg, ${selectedArticle.accentColor}22, rgba(0,0,0,0))`,
                    borderLeft: `4px solid ${selectedArticle.accentColor}`,
                    padding: '1.2rem', 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center',
                    gap: '1rem'
                  }}
                >
                  <div>
                    <h4 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '0.2rem' }}>Want to interact with this article?</h4>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-sub)' }}>Ask Verge AI to summarize, explain technical concepts, or critique the ideas.</p>
                  </div>
                  <button 
                    className="chat-toggle-btn"
                    style={{ backgroundColor: selectedArticle.accentColor, whiteSpace: 'nowrap' }}
                    onClick={() => handleDiscussArticle(selectedArticle)}
                  >
                    💬 Discuss Article
                  </button>
                </div>

                <div className="hero-image-placeholder" style={{ height: '350px' }}>
                  <div className="card-image-gradient" style={{ background: selectedArticle.imageGradient }}></div>
                </div>

                <div className="article-body-content" style={{ fontFamily: 'var(--font-sans)', fontSize: '1.1rem', lineHeight: '1.7', color: 'var(--text-main)', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
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
                          <div className="card-image-gradient" style={{ background: featuredArticle.imageGradient }}></div>
                          <span className="category-tag" style={{ backgroundColor: featuredArticle.accentColor }}>
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
                            <span className="side-item-category" style={{ color: art.accentColor }}>
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
                            <div className="card-image-gradient" style={{ background: art.imageGradient }}></div>
                            <span className="category-tag" style={{ backgroundColor: art.accentColor }}>
                              {art.category}
                            </span>
                          </div>
                          <span className="feed-category" style={{ color: art.accentColor }}>
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
                          <div className="card-image-gradient" style={{ background: art.imageGradient }}></div>
                          <span className="category-tag" style={{ backgroundColor: art.accentColor }}>
                            {art.category}
                          </span>
                        </div>
                        <span className="feed-category" style={{ color: art.accentColor }}>
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
          <aside className="chat-drawer">
            <div className="chat-header">
              <div className="chat-header-title">
                <h3>VERGE AI</h3>
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

            <div className="chat-messages-container">
              {chatHistory.length === 0 ? (
                <div className="chat-empty-state">
                  <div className="chat-empty-icon">⌘</div>
                  <div className="chat-empty-text">
                    <h4>Interact with the news</h4>
                    <p>Select any article on the left or use the prompts below to chat about today's headlines.</p>
                  </div>

                  <div className="chat-suggestions">
                    <button className="suggestion-btn" onClick={() => handleQuickPrompt("Summarize all the news articles on the homepage in 3 bullet points.")}>
                      📝 Summarize today's headlines
                    </button>
                    <button className="suggestion-btn" onClick={() => handleQuickPrompt("What are the key details of Google's new Gemini 3 autonomous agents?")}>
                      🤖 Tell me about Gemini 3 agents
                    </button>
                    <button className="suggestion-btn" onClick={() => handleQuickPrompt("Which article has the biggest impact on clean energy?")}>
                      ⚡ Find articles on green tech
                    </button>
                  </div>
                </div>
              ) : (
                chatHistory.map((msg, index) => {
                  if (msg.role === 'system_notification') {
                    return (
                      <div key={index} style={{ textAlign: 'center', margin: '0.5rem 0', fontSize: '0.7rem', color: 'var(--text-muted)', borderTop: '1px dotted var(--border-light)', paddingTop: '0.5rem' }}>
                        {msg.content}
                      </div>
                    );
                  }
                  
                  return (
                    <div key={index} className={`message-wrapper ${msg.role === 'user' ? 'user' : 'bot'}`}>
                      <span className="message-sender">
                        {msg.role === 'user' ? 'YOU' : 'VERGE AI'}
                      </span>
                      <div className="message-bubble">
                        {msg.role === 'bot' ? formatMarkdown(msg.content) : msg.content}
                        
                        {msg.role === 'bot' && msg.groundingMetadata && (
                          <div className="grounding-info" style={{ marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: '1px dotted var(--border-light)', fontSize: '0.75rem' }}>
                            {msg.groundingMetadata.webSearchQueries && msg.groundingMetadata.webSearchQueries.length > 0 && (
                              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-sub)', marginBottom: '0.4rem' }}>
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
                                        <a href={chunk.web.uri} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent-purple)', textDecoration: 'underline', fontWeight: 500 }}>
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
                      </div>
                    </div>
                  );
                })
              )}

              {isGenerating && (
                <div className="message-wrapper bot">
                  <span className="message-sender">VERGE AI</span>
                  <div className="loading-bubble">
                    <span className="dot"></span>
                    <span className="dot"></span>
                    <span className="dot"></span>
                  </div>
                </div>
              )}

              {errorMessage && (
                <div style={{ backgroundColor: 'rgba(255, 0, 91, 0.1)', color: 'var(--accent-verge)', padding: '0.8rem', borderRadius: '4px', fontSize: '0.8rem', border: '1px solid rgba(255, 0, 91, 0.3)' }}>
                  <strong>Error:</strong> {errorMessage}
                </div>
              )}
              <div ref={chatBottomRef} />
            </div>

            <div className="chat-input-container">
              <form onSubmit={handleSendMessage} className="chat-input-form">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder={selectedArticle ? "Ask about this article..." : "Ask about today's tech..."}
                  className="chat-input-field"
                  disabled={isGenerating}
                />
                <button type="submit" className="chat-send-btn" disabled={!chatInput.trim() || isGenerating}>
                  Send
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
