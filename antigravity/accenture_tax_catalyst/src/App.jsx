import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Header from './components/Header';
import HeroRadar from './components/HeroRadar';
import ChiefTaxGemini from './components/ChiefTaxGemini';
import TransferPricingAnalyzer from './components/TransferPricingAnalyzer';
import ZeroLeakShield from './components/ZeroLeakShield';
import './App.css';

function App() {
  const [isAtBottom, setIsAtBottom] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const scrollHeight = document.documentElement.scrollHeight;
      const scrollTop = document.documentElement.scrollTop;
      const clientHeight = document.documentElement.clientHeight;
      
      // If we are within 100px of the bottom
      if (scrollTop + clientHeight >= scrollHeight - 100) {
        setIsAtBottom(true);
      } else {
        setIsAtBottom(false);
      }
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

      {/* Floating Space Badge */}
      <AnimatePresence>
        {!isAtBottom && (
          <motion.div 
            className="floating-creator-badge"
            initial={{ opacity: 0, y: 50, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 30, scale: 0.8 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            whileHover={{ scale: 1.05 }}
          >
            <div className="badge-glow"></div>
            <a href="https://www.linkedin.com/in/jchavezar/" target="_blank" rel="noopener noreferrer">
              <div className="creator-identity">
                <span>Jesus Chavez</span>
                <span className="creator-handle" style={{ color: 'rgba(255, 255, 255, 0.4)', fontSize: '0.65rem' }}>@jesusarguelles</span>
              </div> 
              <span className="sparkle">✨</span>
            </a>
          </motion.div>
        )}
      </AnimatePresence>

      <footer className="footer-replica">
        <div className="footer-content">
          <div className="footer-links">
            <a href="#">Legal</a>
            <a href="#">Privacy</a>
            <a href="#">Accessibility</a>
            <a href="#">Cookies</a>
          </div>
          <div className="footer-credits">
            <p className="copyright">© 2030 Accenture Tax Catalyst (Replica). All rights reserved.</p>
            <div className="creator-badge">
              <span>Manufactured with ☕ by </span>
              <div className="creator-identity">
                <a href="https://www.linkedin.com/in/jchavezar/" target="_blank" rel="noopener noreferrer" className="creator-link">
                  Jesus Chavez
                </a>
                <span className="creator-handle">@jesusarguelles</span>
              </div>
              <span className="creator-title">| AI Engineer at Google</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
