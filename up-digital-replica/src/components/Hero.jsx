import React from 'react';
import PlanetPongbot from './planets/PlanetPongbot';
import PlanetGateway from './planets/PlanetGateway';
import PlanetSlavista from './planets/PlanetSlavista';
import PlanetBrothers from './planets/PlanetBrothers';
import PlanetRemina from './planets/PlanetRemina';

const PLANET_DATA = [
  {
    id: 'pongbot',
    name: 'Pongbot',
    category: 'Meta Ads · Branding',
    metric: '5.2× ROAS',
    position: { left: '68%', top: '28%' },
    size: 132,
    orbitSize: 211,
    animationClass: 'animate-planet-0',
    orbitAnimation: 'animate-orbit-0',
    Component: PlanetPongbot,
    color: '#BFFF00',
    link: '#work-pongbot'
  },
  {
    id: 'gateway',
    name: 'Gateway Counseling',
    category: 'Non-Profit · Google Grants',
    metric: '$120K granted',
    position: { left: '83%', top: '54%' },
    size: 148,
    orbitSize: 236,
    animationClass: 'animate-planet-1',
    orbitAnimation: 'animate-orbit-1',
    Component: PlanetGateway,
    color: '#0EA5E9',
    link: '#work-non-profits'
  },
  {
    id: 'slavista',
    name: 'Slavista',
    category: 'Branding · Identity',
    metric: '0→1',
    position: { left: '63%', top: '66%' },
    size: 110,
    orbitSize: 176,
    animationClass: 'animate-planet-2',
    orbitAnimation: 'animate-orbit-2',
    Component: PlanetSlavista,
    color: '#F97316',
    link: '#work-slavista'
  },
  {
    id: 'brothers',
    name: 'Brothers Desserts',
    category: 'Social Media · UGC',
    metric: '5M+',
    position: { left: '74%', top: '80%' },
    size: 100,
    orbitSize: 160,
    animationClass: 'animate-planet-3',
    orbitAnimation: 'animate-orbit-3',
    Component: PlanetBrothers,
    color: '#F472B6',
    link: '#work-brothers'
  },
  {
    id: 'remina',
    name: '@dr.remina',
    category: 'Social Media · UGC',
    metric: '$100K+ Rev',
    position: { left: '82%', top: '16%' },
    size: 120,
    orbitSize: 192,
    animationClass: 'animate-planet-4',
    orbitAnimation: 'animate-orbit-4',
    Component: PlanetRemina,
    color: '#EC4899',
    link: '#work-remina'
  }
];

export const Hero = () => {
  return (
    <section className="relative min-h-[90vh] lg:min-h-screen bg-black flex flex-col justify-center items-start overflow-hidden pt-20 px-6 md:px-16">
      {/* Background Gradients (Nebulae) */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden z-0">
        <div className="absolute left-[18%] top-[28%] w-[520px] h-[520px] rounded-full bg-brand-lime/5 filter blur-[60px] animate-nebula-0 will-change-transform" />
        <div className="absolute left-[78%] top-[18%] w-[460px] h-[460px] rounded-full bg-sky-500/3 filter blur-[60px] animate-nebula-1 will-change-transform" />
        <div className="absolute left-[62%] top-[78%] w-[580px] h-[580px] rounded-full bg-pink-500/3 filter blur-[60px] animate-nebula-2 will-change-transform" />
        <div className="absolute left-[12%] top-[82%] w-[420px] h-[420px] rounded-full bg-purple-500/3 filter blur-[60px] animate-nebula-3 will-change-transform" />
      </div>

      {/* Twinkling Stars */}
      <div className="absolute inset-0 pointer-events-none z-0 opacity-40">
        {[...Array(30)].map((_, i) => (
          <div
            key={i}
            className="absolute rounded-full bg-white animate-star-twinkle"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              width: `${Math.random() * 1.5 + 0.5}px`,
              height: `${Math.random() * 1.5 + 0.5}px`,
              animationDelay: `${Math.random() * 5}s`,
            }}
          />
        ))}
      </div>

      {/* Shooting Stars */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden z-0">
        <div className="absolute top-[12%] left-[-10%] w-[3px] h-[3px] rounded-full bg-white shadow-[0_0_8px_#fff] animate-shoot-star-1">
          <div className="absolute top-1/2 right-full w-[140px] h-[1.5px] bg-gradient-to-l from-white/95 via-white/40 to-transparent -translate-y-1/2 blur-[0.3px]" />
        </div>
        <div className="absolute top-[32%] left-[-10%] w-[3px] h-[3px] rounded-full bg-white shadow-[0_0_8px_#fff] animate-shoot-star-2">
          <div className="absolute top-1/2 right-full w-[140px] h-[1.5px] bg-gradient-to-l from-white/95 via-white/40 to-transparent -translate-y-1/2 blur-[0.3px]" />
        </div>
      </div>

      {/* Hero Content */}
      <div className="max-w-4xl relative z-10 select-none">
        <h1 className="text-4xl md:text-6xl font-black text-white leading-[1.1] tracking-tight mb-8">
          Up Digital — <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-lime to-sky-400">
            AI Marketing Agency
          </span> in Miami.
        </h1>
        <p className="text-white/60 text-lg md:text-xl max-w-2xl leading-relaxed mb-12">
          SEO, Meta & Google Ads, Social Media, Branding, Web Design and Custom AI Assistants that bring growth to brands. We build your future.
        </p>
        <div className="flex flex-wrap gap-4">
          <a
            href="#contact"
            className="px-8 py-4 rounded-xl bg-brand-lime text-brand-dark-alt font-bold hover:bg-brand-lime-hover transition-colors shadow-lg shadow-brand-lime/10"
          >
            Start Your Project
          </a>
          <a
            href="#portfolio"
            className="px-8 py-4 rounded-xl border border-white/10 text-white font-bold hover:bg-white/5 transition-colors"
          >
            Check Our Work
          </a>
        </div>
      </div>

      {/* Floating Planets */}
      <div className="hidden lg:block absolute inset-0 z-10 pointer-events-none">
        {PLANET_DATA.map((planet) => {
          const { Component } = planet;
          return (
            <div
              key={planet.id}
              className="absolute pointer-events-auto"
              style={{
                left: planet.position.left,
                top: planet.position.top,
                width: planet.size,
                height: planet.size,
                transform: 'translate(-50%, -50%)',
              }}
            >
              <div className={`relative w-full h-full group ${planet.animationClass}`}>
                {/* Orbiting Moon */}
                <div
                  className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full border border-white/5 pointer-events-none ${planet.orbitAnimation}`}
                  style={{
                    width: planet.orbitSize,
                    height: planet.orbitSize,
                  }}
                >
                  <div
                    className="absolute top-1/2 right-0 w-2 h-2 rounded-full bg-white/80 -translate-y-1/2"
                    style={{
                      boxShadow: `0 0 6px rgba(255,255,255,0.5), 0 0 12px ${planet.color}88`,
                    }}
                  />
                </div>

                {/* Tooltip / Details on Hover */}
                <div className="absolute top-[calc(100%+12px)] left-1/2 -translate-x-1/2 translate-y-2 opacity-0 group-hover:opacity-100 group-hover:translate-y-0 transition-all duration-300 bg-brand-dark-alt/90 backdrop-blur-md border border-white/10 rounded-xl p-4 min-w-[180px] z-30 pointer-events-none shadow-2xl">
                  <div 
                    className="text-[9px] font-black tracking-widest uppercase mb-1"
                    style={{ color: planet.color }}
                  >
                    {planet.category}
                  </div>
                  <div className="text-white font-bold text-sm mb-1">{planet.name}</div>
                  <div 
                    className="text-2xl font-black mb-2"
                    style={{ color: planet.color }}
                  >
                    {planet.metric}
                  </div>
                  <div className="text-white/40 text-[9px] font-bold tracking-widest uppercase">
                    View project →
                  </div>
                </div>

                {/* Planet SVG wrapper */}
                <div
                  className="w-full h-full rounded-full cursor-pointer transition-transform duration-500 group-hover:scale-105"
                  style={{
                    boxShadow: `0 0 24px ${planet.color}15`,
                  }}
                >
                  <Component width="100%" height="100%" />
                  {/* Overlay text on planet */}
                  <div className="absolute bottom-2 right-2 text-white/30 text-[9px] font-bold tracking-widest select-none z-5">
                    {planet.id === 'pongbot' ? '02' : planet.id === 'gateway' ? '04' : planet.id === 'slavista' ? '05' : planet.id === 'brothers' ? '06' : '01'}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
};

export default Hero;

