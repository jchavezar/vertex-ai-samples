import React, { useState, useEffect, useRef } from 'react';
import { Search, Globe, ChevronDown, Menu, X, Briefcase, TrendingUp, Shield, Activity, FileText, Building, Cpu, Landmark, ChevronRight, Zap, Loader2, BrainCircuit } from 'lucide-react';
import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import './Header.css';
import GenerativeDashboardModal from './GenerativeDashboardModal';
import SwarmBoardroomModal from './SwarmBoardroomModal';

const Header = ({ isSearchOpen, setIsSearchOpen }) => {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  
  // 3080 Future Labs State
  const [isBoardroomOpen, setIsBoardroomOpen] = useState(false);

  // AI Mega-Menu State
  const [isMegaMenuOpen, setIsMegaMenuOpen] = useState(false);
  const [navQuery, setNavQuery] = useState('');
  const [isGeneratingNav, setIsGeneratingNav] = useState(false);
  const [generatedCategories, setGeneratedCategories] = useState([]);
  const menuRef = useRef(null);

  // Live Policy Pulse State
  const [isInsightMenuOpen, setIsInsightMenuOpen] = useState(false);
  const [pulseQuery, setPulseQuery] = useState('');
  const [isPulsing, setIsPulsing] = useState(false);
  const [pulseContent, setPulseContent] = useState('');
  
  // Generative Dashboard State
  const [isDashboardOpen, setIsDashboardOpen] = useState(false);
  const [selectedDashboardIndustry, setSelectedDashboardIndustry] = useState('');
  const [dashboardNavQuery, setDashboardNavQuery] = useState('');
  
  // Default static categories before AI generation
  const defaultCategories = [
    { title: "Sustainability & ESG", description: "Net-zero transition and carbon reduction strategies.", icon: "Globe" },
    { title: "Future of Work", description: "Unlocking human potential and talent reinvention.", icon: "Briefcase" },
    { title: "Enterprise AI & Cloud", description: "Driving growth with a modern digital core.", icon: "Cpu" },
    { title: "Value Realization", description: "Measuring 360° total enterprise reinvention ROI.", icon: "TrendingUp" }
  ];

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setIsMegaMenuOpen(false);
        setIsInsightMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleNavGenerate = async (e) => {
    e.preventDefault();
    if (!navQuery.trim()) return;

    setIsGeneratingNav(true);
    try {
      const response = await fetch('api/nav/dynamic-industries', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description: navQuery })
      });
      const data = await response.json();
      if (data.categories && data.categories.length > 0) {
        setGeneratedCategories(data.categories);
      }
    } catch (error) {
      console.error("Failed to generate dynamic navigation", error);
      // Fallback
      setGeneratedCategories([
        { title: "Sustainability Hub", description: "Track ESG metrics and carbon footprint.", icon: "Globe" },
        { title: "Talent Analytics", description: "Predictive insights on workforce trends.", icon: "Briefcase" },
        { title: "Value Realization", description: "Measure total enterprise reinvention ROI.", icon: "TrendingUp" },
        { title: "Digital Core", description: "Cloud migration and AI acceleration status.", icon: "Cpu" }
      ]);
    } finally {
      setIsGeneratingNav(false);
    }
  };

  const getIcon = (iconName) => {
    const icons = { Globe, Briefcase, TrendingUp, Shield, Activity, FileText, Building, Cpu, Landmark };
    const IconComponent = icons[iconName] || Globe;
    return <IconComponent size={20} strokeWidth={1.5} />;
  };

  const handlePulseSearch = async (e) => {
    e.preventDefault();
    if (!pulseQuery.trim()) return;

    setIsPulsing(true);
    setPulseContent('');

    try {
      const response = await fetch('api/nav/live-pulse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: pulseQuery })
      });

      if (!response.body) throw new Error("ReadableStream not yet supported.");

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        
        const parts = buffer.split(/\r?\n\r?\n/);
        buffer = parts.pop() || '';
        
        for (const sseEvent of parts) {
          if (!sseEvent.trim()) continue;
          
          const lines = sseEvent.split(/\r?\n/);
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const dataStr = line.substring(6).trim();
              if (dataStr === '[DONE]') break;
              if (dataStr) {
                try {
                  const parsed = JSON.parse(dataStr);
                  const content = parsed.text || parsed.content;
                  if (content) {
                    setPulseContent(prev => prev + content);
                  }
                } catch (err) {
                  console.error("Error parsing SSE JSON:", err);
                }
              }
            }
          }
        }
      }
    } catch (error) {
      console.error("Failed to fetch live pulse:", error);
      setPulseContent("Error retrieving real-time data.");
    } finally {
      setIsPulsing(false);
    }
  };

  return (
    <header className={`header ${scrolled ? 'header-scrolled' : ''}`}>
      <div className="header-top">
        <div className="header-container">
          <button 
            className="navbar-search-trigger" 
            onClick={() => setIsSearchOpen(true)}
            aria-label="Search"
          >
            <Search size={22} />
          </button>

          <div className="logo-container" style={{ display: 'flex', alignItems: 'center' }}>
            <div style={{ position: 'relative', display: 'inline-flex', alignItems: 'center' }}>
              <span style={{ fontSize: '26px', fontWeight: '700', color: '#ffffff', letterSpacing: '-0.5px', fontFamily: "'Inter', sans-serif" }} className="accenture-text">accenture</span>
              <span style={{ position: 'absolute', top: '-6px', right: '31px', color: '#A100FF', fontSize: '18px', fontWeight: '900' }}>&gt;</span>
            </div>
          </div>

          <div className="header-top-links">
            <div className="region-selector">
              <Globe size={14} />
              <span>USA</span>
              <ChevronDown size={14} />
            </div>
            <a href="#" className="hide-mobile">Resources</a>
            <a href="#" className="hide-mobile">Alumni</a>
            <button className="contact-btn">Contact</button>
          </div>
          
          <button className="mobile-menu-btn" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div 
          className="mobile-menu-dropdown"
          style={{
            position: 'absolute',
            top: '70px',
            left: 0,
            right: 0,
            background: 'rgba(10, 10, 15, 0.98)',
            borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
            padding: '1.5rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem',
            zIndex: 1000
          }}
        >
          {['Insights', 'Services', 'Industries', 'How We Work'].map(item => (
            <button 
              key={item}
              className="mobile-nav-link" 
              style={{ background: 'none', border: 'none', color: '#fff', textAlign: 'left', cursor: 'pointer', fontSize: '1.1rem' }}
              onClick={() => setMobileMenuOpen(false)}
            >
              {item}
            </button>
          ))}
          <button 
            className="mobile-nav-link" 
            style={{ 
              background: 'rgba(251,191,36,0.1)', border: '1px solid #fbbf24', color: '#fbbf24', 
              padding: '0.75rem', borderRadius: '8px', cursor: 'pointer', marginTop: '0.5rem' 
            }} 
            onClick={() => { setIsBoardroomOpen(true); setMobileMenuOpen(false); }}
          >
            3080 Labs
          </button>
        </div>
      )}
      
      <div className="header-nav glass-panel" ref={menuRef}>
        <div className="header-container relative">
          <nav className="nav-links">
            <a 
              href="#" 
              onClick={(e) => { e.preventDefault(); setIsInsightMenuOpen(!isInsightMenuOpen); setIsMegaMenuOpen(false); }}
              className={isInsightMenuOpen ? 'active-tab' : ''}
              style={{ display: 'flex', alignItems: 'center', gap: '4px' }}
            >
              Insights <ChevronDown size={14} className={`nav-chevron ${isInsightMenuOpen ? 'rotate' : ''}`} />
            </a>
            <a href="#">Services</a>
            <a 
              href="#" 
              onClick={(e) => { e.preventDefault(); setIsMegaMenuOpen(!isMegaMenuOpen); setIsInsightMenuOpen(false); }}
              className={isMegaMenuOpen ? 'active-tab' : ''}
              style={{ display: 'flex', alignItems: 'center', gap: '4px' }}
            >
              Industries <ChevronDown size={14} className={`nav-chevron ${isMegaMenuOpen ? 'rotate' : ''}`} />
            </a>
            <a href="#">How We Work</a>
            <a 
              href="#" 
              onClick={(e) => { e.preventDefault(); setIsBoardroomOpen(true); setIsMegaMenuOpen(false); setIsInsightMenuOpen(false); }}
              style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#fbbf24', fontWeight: 600, background: 'rgba(251,191,36,0.1)', padding: '6px 12px', borderRadius: '20px', marginLeft: '12px' }}
              className="future-labs-btn"
            >
              <BrainCircuit size={16} /> 3080 Labs
            </a>
          </nav>
          
          {/* Live Policy Pulse Dropdown */}
          <motion.div 
            className="ai-mega-menu"
            initial={{ opacity: 0, y: -10, pointerEvents: 'none' }}
            animate={{ 
              opacity: isInsightMenuOpen ? 1 : 0, 
              y: isInsightMenuOpen ? 0 : -10,
              pointerEvents: isInsightMenuOpen ? 'auto' : 'none'
            }}
            transition={{ duration: 0.3, ease: 'easeOut' }}
            style={{ position: 'absolute', top: '100%', left: 0, right: 0 }}
          >
            <div className="mega-menu-content">
              {/* Left Column: Input */}
              <div className="mega-ai-column">
                <div className="mega-ai-header">
                  <div className="mega-ai-icon-container">
                    <TrendingUp size={20} className="text-accent" />
                  </div>
                  <h3>Live 360° Value Pulse</h3>
                </div>
                <p>Monitor real-time sustainability, talent, and business transformation trends grounded in global search.</p>
                
                <form onSubmit={handlePulseSearch} className="mega-ai-form">
                  <div className="input-wrapper">
                    <input 
                      type="text" 
                      placeholder="e.g. Sustainability reports for Tech retail..." 
                      value={pulseQuery}
                      onChange={(e) => setPulseQuery(e.target.value)}
                      disabled={isPulsing}
                    />
                    <button type="submit" disabled={isPulsing || !pulseQuery.trim()}>
                      {isPulsing ? (
                        <motion.div 
                          animate={{ rotate: 360 }} 
                          transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
                        >
                          <Loader2 size={16} />
                        </motion.div>
                      ) : (
                        <Search size={18} />
                      )}
                    </button>
                  </div>
                </form>

                {isPulsing && (
                  <div className="nav-generation-status">
                     <span className="pulse-dot"></span>
                     <span>Grounding data via Global Search...</span>
                  </div>
                )}
              </div>

              {/* Right Column: Results Stream */}
              <div className="mega-categories-column">
                <div className="categories-header">
                  <h4>Intelligence Feed</h4>
                  {(pulseContent || isPulsing) && <span className="ai-badge">Live Search AI</span>}
                </div>
                
                <div className="pulse-content-display" style={{ padding: '1rem', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)', minHeight: '150px', maxHeight: '300px', overflowY: 'auto' }}>
                  {!pulseContent && !isPulsing && (
                    <div style={{ opacity: 0.5, textAlign: 'center', marginTop: '20px' }}>
                      Enter a topic to activate 360° value and transformation monitoring.
                    </div>
                  )}
                  {pulseContent && (
                    <ReactMarkdown>
                      {pulseContent}
                    </ReactMarkdown>
                  )}
                </div>
              </div>
            </div>
          </motion.div>

          {/* AI Mega-Menu Dropdown */}
          <motion.div 
            className="ai-mega-menu"
            initial={{ opacity: 0, y: -10, pointerEvents: 'none' }}
            animate={{ 
              opacity: isMegaMenuOpen ? 1 : 0, 
              y: isMegaMenuOpen ? 0 : -10,
              pointerEvents: isMegaMenuOpen ? 'auto' : 'none'
            }}
            transition={{ duration: 0.3, ease: 'easeOut' }}
          >
            <div className="mega-menu-content">
              {/* Left Column: AI Input */}
              <div className="mega-ai-column">
                <div className="mega-ai-header">
                  <div className="mega-ai-icon-container">
                    <Zap size={20} className="text-accent" />
                  </div>
                  <h3>Navigational Gemini</h3>
                </div>
                <p>Describe your operating model, expansion plans, or challenges to instantly map your relevant 360° value opportunity surface.</p>
                
                <form onSubmit={handleNavGenerate} className="mega-ai-form">
                  <div className="input-wrapper">
                    <input 
                      type="text" 
                      placeholder="e.g. SaaS startup expanding into LatAm..." 
                      value={navQuery}
                      onChange={(e) => setNavQuery(e.target.value)}
                      disabled={isGeneratingNav}
                    />
                    <button type="submit" disabled={isGeneratingNav || !navQuery.trim()}>
                      {isGeneratingNav ? (
                        <motion.div 
                          animate={{ rotate: 360 }} 
                          transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
                        >
                          <Zap size={16} />
                        </motion.div>
                      ) : (
                        <ChevronRight size={18} />
                      )}
                    </button>
                  </div>
                </form>

                {isGeneratingNav && (
                  <div className="nav-generation-status">
                    <div className="nav-scanning-line"></div>
                    <span>Synthesizing structural pathways...</span>
                  </div>
                )}
              </div>

              {/* Right Column: Dynamic Categories */}
              <div className="mega-categories-column">
                <div className="categories-header">
                  <h4>{generatedCategories.length > 0 ? 'Custom Insights Path' : 'Explore by Sector'}</h4>
                  {generatedCategories.length > 0 && <span className="ai-badge">AI Generated</span>}
                </div>
                
                <div className="categories-grid">
                  {(generatedCategories.length > 0 ? generatedCategories : defaultCategories).map((cat, idx) => (
                    <motion.a 
                      href="#" 
                      key={idx} 
                      className="category-card"
                      initial={{ opacity: 0, x: 10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.1 }}
                      onClick={(e) => {
                        e.preventDefault();
                        setIsMegaMenuOpen(false);
                        setSelectedDashboardIndustry(cat.title);
                        setDashboardNavQuery(navQuery);
                        setIsDashboardOpen(true);
                      }}
                    >
                      <div className="cat-icon">
                        {getIcon(cat.icon)}
                      </div>
                      <div className="cat-content">
                        <h5>{cat.title}</h5>
                        <p>{cat.description}</p>
                      </div>
                    </motion.a>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>

    <GenerativeDashboardModal 
        isOpen={isDashboardOpen} 
        onClose={() => setIsDashboardOpen(false)} 
        industry={selectedDashboardIndustry}
        navQuery={dashboardNavQuery}
      />

      <SwarmBoardroomModal 
        isOpen={isBoardroomOpen} 
        onClose={() => setIsBoardroomOpen(false)} 
      />
    </header>
  );
};

export default Header;
