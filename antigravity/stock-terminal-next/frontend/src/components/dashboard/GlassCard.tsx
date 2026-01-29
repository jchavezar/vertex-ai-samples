import React, { useRef, useState } from 'react';
import clsx from 'clsx';
import { motion } from 'framer-motion';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  delay?: number; // Delay in ms
}

export const GlassCard: React.FC<GlassCardProps> = ({ children, className, delay = 0 }) => {
  const divRef = useRef<HTMLDivElement>(null);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [opacity, setOpacity] = useState(0);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!divRef.current) return;
    const rect = divRef.current.getBoundingClientRect();
    setPosition({ x: e.clientX - rect.left, y: e.clientY - rect.top });
    setOpacity(1);
  };

  const handleMouseLeave = () => {
    setOpacity(0);
  };

  return (
    <motion.div
      ref={divRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        duration: 0.5,
        delay: delay / 1000,
        type: "spring",
        stiffness: 100,
        damping: 15
      }}
      className={clsx(
        "group relative overflow-hidden rounded-2xl transition-all duration-300",
        // Strict Recipe: Dark, semi-transparent base, frosted glass, edge, depth
        "bg-slate-900/50 backdrop-blur-xl border border-white/10 shadow-2xl",
        className
      )}
    >
      {/* Configuration for the spotlight gradient */}
      <div
        className="pointer-events-none absolute -inset-px opacity-0 transition-opacity duration-300 group-hover:opacity-100"
        style={{
          opacity,
          background: `radial-gradient(600px circle at ${position.x}px ${position.y}px, rgba(255,255,255,0.06), transparent 40%)`,
        }}
      />

      {/* Inner Content */}
      <div className="relative z-10 h-full">
        {children}
      </div>
    </motion.div>
  );
};
