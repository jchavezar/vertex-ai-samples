import React, { useState, useRef, useEffect } from 'react';
import EyeIcon from './planets/EyeIcon';
import MascotDog from './planets/MascotDog';
import { Radio, Terminal } from './Icons';

export const Pods = () => {
  // Eye tracking state
  const eyeContainerRef = useRef(null);
  const [pupilOffset, setPupilOffset] = useState({ x: 0, y: 0 });

  const handleMouseMove = (e) => {
    if (!eyeContainerRef.current) return;
    const rect = eyeContainerRef.current.getBoundingClientRect();
    
    // Find center of eyeball relative to viewport
    const eyeCenterX = rect.left + rect.width / 2;
    const eyeCenterY = rect.top + rect.height / 2;
    
    // Vector from center to mouse
    const dx = e.clientX - eyeCenterX;
    const dy = e.clientY - eyeCenterY;
    const distance = Math.sqrt(dx * dx + dy * dy);
    
    // Max translation distance for pupil (eyeball radius - pupil radius)
    // Eyeball is ~88% of 200px container, so radius is ~88px. Pupil is ~28px radius.
    // Max movement is ~12px to stay inside eyeball safely.
    const maxTranslate = 16;
    
    if (distance === 0) {
      setPupilOffset({ x: 0, y: 0 });
    } else {
      const angle = Math.atan2(dy, dx);
      // Bound the distance
      const boundedDist = Math.min(distance * 0.15, maxTranslate);
      setPupilOffset({
        x: Math.cos(angle) * boundedDist,
        y: Math.sin(angle) * boundedDist
      });
    }
  };

  const handleMouseLeave = () => {
    // Return pupil to center slowly
    setPupilOffset({ x: 0, y: 0 });
  };

  return (
    <section className="relative py-24 bg-[#050507] overflow-hidden border-t border-white/5">
      <div className="max-w-7xl mx-auto px-6 md:px-16">
        
        {/* Section Header */}
        <div className="mb-16 text-center">
          <span className="text-[10px] font-black tracking-[0.3em] uppercase text-brand-lime block mb-3">
            Our Portfolio · Interactive Pods
          </span>
          <h2 className="text-3xl md:text-5xl font-black text-white tracking-tight uppercase">
            Systems Nominal.
          </h2>
          <p className="text-white/40 text-sm max-w-md mx-auto mt-4 leading-relaxed">
            Hover to activate systems. Explore our interactive pods built to demonstrate advanced animations.
          </p>
        </div>

        {/* Pods Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          
          {/* Pod 1: SEO Pod (Eye Tracking) */}
          <div 
            ref={eyeContainerRef}
            onMouseMove={handleMouseMove}
            onMouseLeave={handleMouseLeave}
            className="relative h-[360px] bg-brand-dark-alt/30 border border-white/5 rounded-3xl p-8 flex flex-col justify-between overflow-hidden group hover:border-brand-lime/20 transition-all duration-300"
          >
            {/* Background elements */}
            <div className="absolute inset-0 bg-gradient-to-br from-brand-lime/5 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-all duration-500" />
            
            {/* Swirl grids inside the eyeball background */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 rounded-full border border-white/5 opacity-40 pointer-events-none" />
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-36 h-36 rounded-full border border-white/5 opacity-60 pointer-events-none" />

            <div className="flex justify-between items-start z-10">
              <span className="text-[10px] font-black tracking-widest text-brand-lime/70 uppercase">
                POD · SEO-01
              </span>
              <div className="flex gap-2">
                <span className="px-2 py-0.5 rounded text-[8px] font-black bg-brand-lime/10 border border-brand-lime/20 text-brand-lime uppercase tracking-widest animate-pulse">
                  Active
                </span>
              </div>
            </div>

            {/* Interactive Eye Visual */}
            <div className="relative w-40 h-40 mx-auto z-10 pointer-events-none select-none">
              {/* Scanlines overlay on eye */}
              <div className="absolute inset-0 rounded-full bg-[repeating-linear-gradient(to_bottom,transparent_0px,transparent_3px,rgba(191,255,0,0.08)_3px,rgba(191,255,0,0.08)_4px)] z-20 pointer-events-none mix-blend-screen" />
              <EyeIcon 
                pupilStyle={{ 
                  transform: `translate(${pupilOffset.x}px, ${pupilOffset.y}px)`,
                  transition: 'transform 0.1s ease-out'
                }} 
              />
            </div>

            <div className="z-10 mt-auto">
              <h3 className="text-white font-bold text-lg mb-2 flex items-center gap-2">
                <Radio className="w-4 h-4 text-brand-lime" />
                Topical Authority Tracker
              </h3>
              <p className="text-white/55 text-xs leading-relaxed">
                Interact with the eye to align the semantic parser. Simulated indexing engines track targeting parameters live.
              </p>
            </div>
          </div>

          {/* Pod 2: Dev Pod (Mascot Dog) */}
          <div 
            className="relative h-[360px] bg-brand-dark-alt/30 border border-white/5 rounded-3xl p-8 flex flex-col justify-between overflow-hidden group hover:border-brand-lime/20 transition-all duration-300"
          >
            {/* Background elements */}
            <div className="absolute inset-0 bg-gradient-to-br from-brand-lime/5 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-all duration-500" />

            <div className="flex justify-between items-start z-10">
              <span className="text-[10px] font-black tracking-widest text-brand-lime/70 uppercase">
                POD · DEV-02
              </span>
              <span className="px-2 py-0.5 rounded text-[8px] font-black bg-brand-lime/10 border border-brand-lime/20 text-brand-lime uppercase tracking-widest animate-pulse">
                Online
              </span>
            </div>

            {/* Animated Mascot Dog */}
            <div className="relative w-36 h-28 mx-auto z-10 pointer-events-none select-none">
              <MascotDog width="100%" height="100%" />
            </div>

            <div className="z-10 mt-auto">
              <h3 className="text-white font-bold text-lg mb-2 flex items-center gap-2">
                <Terminal className="w-4 h-4 text-brand-lime" />
                Mascot Space Sandbox
              </h3>
              <p className="text-white/55 text-xs leading-relaxed">
                Space Cadet Rover is deployed in isolation. Watch tail-wag and limb physics running via hardware-accelerated CSS keyframes.
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
};

export default Pods;
