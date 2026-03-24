import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import HeroRadar from './components/HeroRadar';
import ChiefTaxGemini from './components/ChiefTaxGemini';
import TransferPricingAnalyzer from './components/TransferPricingAnalyzer';
import ZeroLeakShield from './components/ZeroLeakShield';
import './App.css';

function App() {
  const [scrollPosition, setScrollPosition] = useState(0);
  const [isScrolledToBottom, setIsScrolledToBottom] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const position = window.pageYOffset;
      setScrollPosition(position);

      const winHeight = window.innerHeight;
      const docHeight = document.documentElement.scrollHeight;
      const scrolledToBottom = position + winHeight >= docHeight - 50; 
      setIsScrolledToBottom(scrolledToBottom);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="app-container">
      <Header />
      
      <main>
        {/* Core AI Hero Section */}
        <HeroRadar />
        
        {/* Security / Trust Banner */}
        <ZeroLeakShield />

        {/* Gemini Section taking up the narrative space */}
        <div className="section-divider"></div>
        <ChiefTaxGemini />
        
        {/* Multimodal Drag and Drop */}
        <div className="section-divider"></div>
        <TransferPricingAnalyzer />
      </main>

      <footer className={`footer-replica ${isScrolledToBottom ? 'expanded' : ''}`}>
        <div className="footer-content">
          <div className="footer-links">
            <a href="#">Legal</a>
            <a href="#">Privacy</a>
            <a href="#">Accessibility</a>
            <a href="#">Cookies</a>
          </div>
          <div className="footer-creator">
            <p>Manufactured with ☕ by Jesus Chavez, AI Engineer at Google</p>
            <p className="handle">@jesusarguelles</p>
            <a href="https://www.linkedin.com/in/jchavezar/" target="_blank" rel="noopener noreferrer" className="linkedin-link">
              Connect on LinkedIn
            </a>
          </div>
          <p>© 2030 KPMG Global Tax Intelligence (Replica). All rights reserved.</p>
        </div>
      </footer>

      {/* Floating Badge (anchored to bottom-right during scroll) */}
      {!isScrolledToBottom && (
        <a href="https://www.linkedin.com/in/jchavezar/" target="_blank" rel="noopener noreferrer" className="floating-creator-badge">
          <div className="badge-content">
            <span className="badge-text">Creator: Jesus Chavez</span>
            <span className="badge-handle">@jesusarguelles</span>
            <span className="badge-glow"></span>
          </div>
        </a>
      )}
    </div>
  );
}

export default App;
