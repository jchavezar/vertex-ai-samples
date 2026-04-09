import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import HeroRadar from './components/HeroRadar';
import ChiefTaxGemini from './components/ChiefTaxGemini';
import DocumentAnalyzer from './components/DocumentAnalyzer';
import ZeroLeakShield from './components/ZeroLeakShield';
import ResearchInsights from './components/ResearchInsights';
import PillarTwoEngine from './components/PillarTwoEngine';
import JurisdictionHeatmap from './components/JurisdictionHeatmap';
import TransformationRoadmap from './components/TransformationRoadmap';
import RegulatoryHorizon from './components/RegulatoryHorizon';
import TreatyNavigator from './components/TreatyNavigator';
import AuditSimulator from './components/AuditSimulator';
import './App.css';

function App() {
  const [isScrolledToBottom, setIsScrolledToBottom] = useState(false);
  const [isAuditOpen, setIsAuditOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const position = window.pageYOffset;
      const winHeight = window.innerHeight;
      const docHeight = document.documentElement.scrollHeight;
      setIsScrolledToBottom(position + winHeight >= docHeight - 50);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="app-container">
      <Header />

      <main>
        <HeroRadar />
        <ZeroLeakShield />

        <div className="section-divider"></div>
        <ResearchInsights />

        <div className="section-divider"></div>
        <ChiefTaxGemini />

        <div className="section-divider"></div>
        <DocumentAnalyzer onOpenAudit={() => setIsAuditOpen(true)} />

        <div className="section-divider"></div>
        <PillarTwoEngine />

        <div className="section-divider"></div>
        <JurisdictionHeatmap />

        <div className="section-divider"></div>
        <TransformationRoadmap />

        <div className="section-divider"></div>
        <RegulatoryHorizon />

        <div className="section-divider"></div>
        <TreatyNavigator />
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
            <p>Manufactured with precision by Jesus Chavez, AI Engineer at Google</p>
            <p className="handle">@jesusarguelles</p>
            <a href="https://www.linkedin.com/in/jchavezar/" target="_blank" rel="noopener noreferrer" className="linkedin-link">
              Connect on LinkedIn
            </a>
          </div>
          <p>&copy; 2030 Nexus Tax Intelligence. All rights reserved.</p>
        </div>
      </footer>

      {!isScrolledToBottom && (
        <a href="https://www.linkedin.com/in/jchavezar/" target="_blank" rel="noopener noreferrer" className="floating-creator-badge">
          <div className="badge-content">
            <span className="badge-text">Creator: Jesus Chavez</span>
            <span className="badge-handle">@jesusarguelles</span>
          </div>
        </a>
      )}

      <AuditSimulator isOpen={isAuditOpen} onClose={() => setIsAuditOpen(false)} />
    </div>
  );
}

export default App;
