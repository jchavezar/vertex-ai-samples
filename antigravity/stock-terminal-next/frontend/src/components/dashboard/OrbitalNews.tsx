import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { NewsItem } from './types';
import { Zap, ExternalLink, Timer } from 'lucide-react';

interface OrbitalNewsProps {
  items: NewsItem[];
  centerRef: React.RefObject<HTMLDivElement>;
}

export const OrbitalNews: React.FC<OrbitalNewsProps> = ({ items, centerRef }) => {
  if (!items || items.length === 0) return null;

  // We'll take the top 6 news items for the orbital effect
  const orbitalItems = items.slice(0, 6);

  // Constants for orbital distribution
  const RADIUS_X = 400; // Horizontal radius
  const RADIUS_Y = 220; // Vertical radius

  return (
    <div
      className="absolute inset-0 pointer-events-none z-10 overflow-visible"
      style={{
        // Just acknowledging the ref exists to satisfy lint, 
        // real centering is handled by relative parent and absolute offsets
        transition: centerRef.current ? 'opacity 0.3s' : 'none'
      }}
    >
      <AnimatePresence>
        {orbitalItems.map((item, index) => {
          // Calculate initial angle and position
          const angle = (index / orbitalItems.length) * 2 * Math.PI;
          const x = Math.cos(angle) * RADIUS_X;
          const y = Math.sin(angle) * RADIUS_Y;

          return (
            <motion.div
              key={item.id || index}
              initial={{ opacity: 0, scale: 0.5, x: 0, y: 0 }}
              animate={{
                opacity: 1,
                scale: 1,
                x: x,
                y: y,
                transition: {
                  type: 'spring',
                  stiffness: 50,
                  damping: 15,
                  delay: index * 0.1
                }
              }}
              exit={{ opacity: 0, scale: 0.5 }}
              whileHover={{ scale: 1.05, zIndex: 50 }}
              className="absolute left-1/2 top-1/2 -ml-32 -mt-20 w-64 pointer-events-auto"
            >
              <div className="relative group bg-[var(--bg-card)]/40 backdrop-blur-xl border border-white/10 rounded-2xl p-4 shadow-2xl shadow-black/50 overflow-hidden transition-all duration-300 hover:border-blue-500/50 hover:bg-[var(--bg-card)]/60">
                {/* Glow Effect */}
                <div className="absolute -inset-1 bg-gradient-to-r from-blue-500/20 to-cyan-500/20 rounded-2xl blur opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                <div className="relative">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-blue-500/20 border border-blue-500/30">
                      <Zap size={10} className="text-blue-400" />
                      <span className="text-[9px] font-black text-blue-400 uppercase tracking-tighter">Impact {item.sentiment === 'positive' ? 'High' : 'Neutral'}</span>
                    </div>
                    <div className="flex items-center gap-1 text-[9px] text-[var(--text-muted)] font-medium">
                      <Timer size={10} />
                      {item.time}
                    </div>
                  </div>

                  <h4 className="text-[11px] font-bold text-[var(--text-primary)] leading-relaxed line-clamp-2 mb-2 group-hover:text-blue-400 transition-colors">
                    {item.headline}
                  </h4>

                  <div className="flex items-center justify-between mt-auto pt-2 border-t border-white/5">
                    <span className="text-[9px] font-bold text-[var(--text-secondary)] uppercase tracking-widest">{item.source}</span>
                    <ExternalLink size={10} className="text-[var(--text-muted)] group-hover:text-blue-400 transition-colors" />
                  </div>
                </div>

                {/* Micro-drifting animation */}
                <motion.div
                  animate={{
                    x: [0, 5, -5, 0],
                    y: [0, -5, 5, 0],
                  }}
                  transition={{
                    duration: 10 + index * 2,
                    repeat: Infinity,
                    ease: "easeInOut"
                  }}
                  className="absolute inset-0 pointer-events-none"
                />
              </div>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
};
