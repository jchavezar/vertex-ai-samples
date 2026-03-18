import React from 'react';
import Header from './components/Header';
import HeroRadar from './components/HeroRadar';
import ChiefTaxGemini from './components/ChiefTaxGemini';
import TransferPricingAnalyzer from './components/TransferPricingAnalyzer';
import ZeroLeakShield from './components/ZeroLeakShield';
import './App.css';

function App() {
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

      <footer className="footer-replica">
        <div className="footer-content">
          <div className="footer-links">
            <a href="#">Legal</a>
            <a href="#">Privacy</a>
            <a href="#">Accessibility</a>
            <a href="#">Cookies</a>
          </div>
          <p>© 2030 KPMG Global Tax Intelligence (Replica). All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
