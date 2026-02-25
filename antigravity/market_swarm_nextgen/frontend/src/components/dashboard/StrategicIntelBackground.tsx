import React from 'react';
import { motion } from 'framer-motion';

const StrategicIntelBackground: React.FC = () => {
  return (
    <div className="absolute inset-0 z-0 pointer-events-none opacity-20">
      {[...Array(8)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute"
          initial={{
            x: Math.random() * 1200 - 600,
            y: Math.random() * 1000 - 500,
            rotate: Math.random() * 360,
            scale: 0.4 + Math.random() * 0.4
          }}
          animate={{
            x: [null, Math.random() * 1200 - 600],
            y: [null, Math.random() * 1000 - 500],
            rotate: [null, Math.random() * 360],
          }}
          transition={{
            duration: 25 + Math.random() * 25,
            repeat: Infinity,
            ease: "linear"
          }}
        >
          <div className="w-56 h-72 border border-blue-500/20 rounded-2xl bg-gradient-to-br from-blue-500/10 via-transparent to-purple-500/10 backdrop-blur-md shadow-2xl p-4 flex flex-col justify-between overflow-hidden">
            <div className="flex justify-between items-start">
              <div className="w-8 h-8 rounded-lg bg-white/5 border border-white/10" />
              <div className="w-12 h-4 rounded-full bg-blue-500/20" />
            </div>
            <div className="space-y-2">
              <div className="h-4 w-24 bg-white/10 rounded" />
              <div className="h-3 w-16 bg-white/5 rounded" />
            </div>
            <div className="h-16 w-full mt-4 flex items-end gap-1">
              {[...Array(12)].map((_, j) => (
                <div
                  key={j}
                  className="flex-1 bg-blue-400/30 rounded-t"
                  style={{ height: `${Math.random() * 100}%` }}
                />
              ))}
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
};

export default React.memo(StrategicIntelBackground);
