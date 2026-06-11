import React, { useRef, useState, useEffect } from 'react';
import { ArrowRight } from './Icons';

const PROJECTS = [
  {
    id: '01',
    title: '@dr.remina',
    category: 'Social Media · UGC',
    metric: '+417K',
    metricLabel: 'followers',
    desc: 'Featured in Forbes Canada. $100K+ revenue in 90 days.',
    color: '#EC4899', // Pink
    bgGradient: 'from-[#EC4899]/90 via-[#EC4899]/30 to-transparent',
    borderColor: 'border-[#EC4899]/30',
  },
  {
    id: '02',
    title: 'Savants AI',
    category: 'AI SEO · Web Dev',
    metric: '320%',
    metricLabel: 'organic growth',
    desc: 'Ranked #1 for 14 AI-related keywords in 6 months.',
    color: '#22C55E', // Green
    bgGradient: 'from-[#22C55E]/90 via-[#22C55E]/30 to-transparent',
    borderColor: 'border-[#22C55E]/30',
  },
  {
    id: '03',
    title: 'Pongbot',
    category: 'Meta Ads · Branding',
    metric: '5.2×',
    metricLabel: 'ROAS',
    desc: '$6.8M revenue attributed to paid social campaigns.',
    color: '#BFFF00', // Lime
    bgGradient: 'from-[#BFFF00]/90 via-[#BFFF00]/30 to-transparent',
    borderColor: 'border-[#BFFF00]/30',
  },
  {
    id: '04',
    title: 'Slavista',
    category: 'Branding · Identity',
    metric: '0→1',
    metricLabel: 'full brand built',
    desc: "Logo, mascots, packaging & social launch for Miami's Slavic cuisine brand.",
    color: '#F97316', // Orange
    bgGradient: 'from-[#F97316]/90 via-[#F97316]/30 to-transparent',
    borderColor: 'border-[#F97316]/30',
  },
  {
    id: '05',
    title: 'Gateway Counseling',
    category: 'Non-Profit · Google Grants',
    metric: '$120K',
    metricLabel: 'granted',
    desc: 'Secured Google Ad Grant, qualifying traffic and maximizing local reach.',
    color: '#0EA5E9', // Sky Blue
    bgGradient: 'from-[#0EA5E9]/90 via-[#0EA5E9]/30 to-transparent',
    borderColor: 'border-[#0EA5E9]/30',
  }
];

export const Portfolio = () => {
  const scrollContainerRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [startX, setStartX] = useState(0);
  const [scrollLeft, setScrollLeft] = useState(0);

  const handleMouseDown = (e) => {
    setIsDragging(true);
    setStartX(e.pageX - scrollContainerRef.current.offsetLeft);
    setScrollLeft(scrollContainerRef.current.scrollLeft);
  };

  const handleMouseLeave = () => {
    setIsDragging(false);
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleMouseMove = (e) => {
    if (!isDragging) return;
    e.preventDefault();
    const x = e.pageX - scrollContainerRef.current.offsetLeft;
    const walk = (x - startX) * 1.5; // Scroll speed multiplier
    scrollContainerRef.current.scrollLeft = scrollLeft - walk;
  };

  return (
    <section id="portfolio" className="relative py-24 bg-brand-dark overflow-hidden border-t border-white/5">
      <div className="max-w-7xl mx-auto px-6 md:px-16 mb-12 flex justify-between items-end">
        <div>
          <span className="text-[10px] font-black tracking-[0.3em] uppercase text-brand-lime block mb-3">
            PORTFOLIO
          </span>
          <h2 className="text-3xl md:text-5xl font-black text-white tracking-tight">
            CHECK OUT OUR WORK.
          </h2>
        </div>
        <div className="hidden md:block text-white/30 text-sm font-semibold tracking-wider uppercase animate-pulse">
          ← drag to explore →
        </div>
      </div>

      {/* Horizontal Scroll Area */}
      <div 
        ref={scrollContainerRef}
        onMouseDown={handleMouseDown}
        onMouseLeave={handleMouseLeave}
        onMouseUp={handleMouseUp}
        onMouseMove={handleMouseMove}
        className={`flex gap-6 overflow-x-auto px-6 md:px-16 pb-8 cursor-grab active:cursor-grabbing no-scrollbar select-none ${isDragging ? 'scroll-smooth-none' : ''}`}
        style={{ scrollBehavior: isDragging ? 'auto' : 'smooth' }}
      >
        {PROJECTS.map((project) => (
          <div 
            key={project.id}
            className="flex-shrink-0 relative rounded-3xl overflow-hidden bg-brand-dark-alt border border-white/5 group"
            style={{ 
              width: 'clamp(280px, 28vw, 380px)', 
              height: 'clamp(400px, 60vh, 560px)' 
            }}
          >
            {/* Hover Background Glow */}
            <div className={`absolute inset-0 bg-gradient-to-t ${project.bgGradient} opacity-0 group-hover:opacity-100 transition-opacity duration-700 z-0`} />

            {/* Content Container */}
            <div className="relative h-full flex flex-col justify-between p-8 z-10">
              {/* Card Header */}
              <div className="flex items-start justify-between">
                <span className="text-white/40 text-xs font-black tracking-widest">{project.id}</span>
                <span className="text-[10px] font-black tracking-widest uppercase px-3 py-1 rounded-full bg-white/10 backdrop-blur-md text-white border border-white/5">
                  {project.category}
                </span>
              </div>

              {/* Card Body */}
              <div>
                <p 
                  className="text-5xl font-black leading-none mb-1 transition-transform duration-500 group-hover:-translate-y-1"
                  style={{ color: project.color }}
                >
                  {project.metric}
                </p>
                <p className="text-white/50 text-[10px] uppercase tracking-widest mb-4 font-black">
                  {project.metricLabel}
                </p>
                <h3 className="text-white font-black text-2xl mb-2">{project.title}</h3>
                <p className="text-white/55 text-sm leading-relaxed mb-6">
                  {project.desc}
                </p>
                
                {/* Action Link */}
                <a 
                  href={project.link}
                  className="inline-flex items-center gap-2 text-white text-xs font-bold uppercase tracking-widest transition-all duration-300 group-hover:gap-3"
                  style={{ color: project.color }}
                >
                  View project 
                  <ArrowRight className="w-4 h-4" />
                </a>
              </div>
            </div>
            
            {/* Outline Card Bottom Text (Watermark style) */}
            <div className="absolute bottom-0 left-0 right-0 overflow-hidden pointer-events-none select-none z-0">
              <p 
                className="font-black leading-none px-5 pb-2 whitespace-nowrap opacity-10 uppercase transition-all duration-500 group-hover:scale-105"
                style={{ 
                  fontSize: 'clamp(2.5rem, 9vw, 4.5rem)',
                  color: 'transparent',
                  WebkitTextStroke: `1px ${project.color}`,
                  transform: 'translateY(18%)'
                }}
              >
                {project.title}
              </p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};

export default Portfolio;
