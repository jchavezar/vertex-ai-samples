import React, { useState, useEffect, useRef } from 'react';
import { Search, Globe, ChevronDown, Menu, X, Briefcase, TrendingUp, Shield, Activity, FileText, Building, Cpu, Landmark, ChevronRight, Zap } from 'lucide-react';
import { motion } from 'framer-motion';
import './Header.css';

const Header = () => {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  
  // AI Mega-Menu State
  const [isMegaMenuOpen, setIsMegaMenuOpen] = useState(false);
  const [navQuery, setNavQuery] = useState('');
  const [isGeneratingNav, setIsGeneratingNav] = useState(false);
  const [generatedCategories, setGeneratedCategories] = useState([]);
  const menuRef = useRef(null);
  
  // Default static categories before AI generation
  const defaultCategories = [
    { title: "Financial Services", description: "Tax strategies for banking, insurance, and asset management.", icon: "Landmark" },
    { title: "Technology", description: "Navigating digital economy taxes and IP structuring.", icon: "Cpu" },
    { title: "Healthcare", description: "Compliance for pharma, devices, and care providers.", icon: "Activity" },
    { title: "Infrastructure", description: "Tax modeling for energy, real estate, and public projects.", icon: "Building" }
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
      const response = await fetch('/api/nav/dynamic-industries', {
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
        { title: "Global Compliance Engine", description: "Automated cross-border tax analysis", icon: "Globe" },
        { title: "Transfer Pricing Nexus", "description": "Intercompany agreement insights", icon: "FileText" },
        { title: "M&A Structuring", description: "Risk assessment for global transactions", icon: "Briefcase" },
        { title: "Digital Service Taxes", description: "Evaluating digital product exposure", icon: "Cpu" }
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

  return (
    <header className={`header ${scrolled ? 'header-scrolled' : ''}`}>
      <div className="header-top">
        <div className="header-container">
          <div className="logo-container" style={{ display: 'flex', alignItems: 'center' }}>
            <span style={{ fontSize: '28px', fontWeight: '800', color: '#ffffff', letterSpacing: '1px', fontFamily: '"Inter", Arial, sans-serif', marginRight: '8px' }}>KPMG</span>
            <span style={{ fontSize: '14px', fontWeight: '400', color: 'rgba(255,255,255,0.8)', borderLeft: '1px solid rgba(255,255,255,0.4)', paddingLeft: '8px', lineHeight: '1.1' }}>Global Tax<br/>Intelligence</span>
          </div>

          <div className="header-top-links">
            <div className="region-selector">
              <Globe size={14} />
              <span>Global</span>
              <ChevronDown size={14} />
            </div>
            <a href="#">Resources</a>
            <a href="#">Alumni</a>
            <a href="#">Media</a>
            <a href="#">Subscribe</a>
            <button className="contact-btn">Contact Us</button>
          </div>
          
          <button className="mobile-menu-btn" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>
      
      <div className="header-nav glass-panel" ref={menuRef}>
        <div className="header-container relative">
          <nav className="nav-links">
            <a href="#">Insights</a>
            <a href="#">Services</a>
            <a 
              href="#" 
              onClick={(e) => { e.preventDefault(); setIsMegaMenuOpen(!isMegaMenuOpen); }}
              className={isMegaMenuOpen ? 'active-tab' : ''}
              style={{ display: 'flex', alignItems: 'center', gap: '4px' }}
            >
              Industries <ChevronDown size={14} className={`nav-chevron ${isMegaMenuOpen ? 'rotate' : ''}`} />
            </a>
            <a href="#">How We Work</a>
            <a href="#">Careers & Culture</a>
          </nav>
          
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
                  <h3>Navigational Copilot</h3>
                </div>
                <p>Describe your operating model, expansion plans, or challenges to instantly map your relevant global tax risk surface.</p>
                
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

          <div className="search-container">
            <Search size={18} />
            <span>Search</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
