import React from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import About from './components/About';
import Clients from './components/Clients';
import Services from './components/Services';
import Pods from './components/Pods';
import Portfolio from './components/Portfolio';
import MayaAI from './components/MayaAI';
import Footer from './components/Footer';
import MascotDog from './components/planets/MascotDog';

function App() {
  return (
    <div className="bg-brand-dark min-h-screen text-white relative font-sans overflow-x-hidden selection:bg-brand-lime selection:text-brand-dark-alt">
      
      {/* Global Header */}
      <Header />

      {/* Hero Section */}
      <Hero />

      {/* More Than An Agency Section (Light BG) */}
      <About />

      {/* Scrolling Client Marquee (Light BG Alt) */}
      <Clients />

      {/* Services Grid (Flip Cards) */}
      <Services />

      {/* Interactive Pods Section (Eye Tracking + Tail Wag Dog) */}
      <Pods />

      {/* Horizontal Drag Portfolio */}
      <Portfolio />

      {/* Maya AI Strategist Chat Section */}
      <MayaAI />

      {/* Footer Contact Section */}
      <Footer />

      {/* Background Easter Egg: Mascot Dog walking infinitely across the bottom of the page */}
      <div 
        className="absolute bottom-10 w-28 h-20 pointer-events-none z-20 overflow-visible"
        style={{
          animation: 'dogWalk 45s linear infinite',
          willChange: 'left',
        }}
      >
        <MascotDog width="100%" height="100%" />
      </div>

    </div>
  );
}

export default App;
