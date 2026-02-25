import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { NewsItem } from '../../store/dashboardStore';

interface NewsCardProps {
  item: NewsItem;
  onClick: () => void;
}

const NewsCard: React.FC<NewsCardProps> = ({ item, onClick }) => {
  const [isHovered, setIsHovered] = useState(false);
  const isPositive = item.sentiment === 'positive';
  const isNegative = item.sentiment === 'negative';
  
  // Color mapping based on sentiment
  const borderColor = isPositive ? 'border-emerald-500/30' : isNegative ? 'border-red-500/30' : 'border-slate-500/30';
  const glowColor = isPositive ? 'shadow-[0_0_20px_rgba(16,185,129,0.1)]' : isNegative ? 'shadow-[0_0_20px_rgba(239,68,68,0.1)]' : '';
  const accentColor = isPositive ? 'bg-emerald-500' : isNegative ? 'bg-red-500' : 'bg-slate-500';

  return (
    <motion.div
      layout
      whileHover={{ y: -2, scale: 1.01 }}
      className={`relative cursor-pointer group rounded-xl overflow-hidden border bg-[#0A0C11]/80 backdrop-blur-md transition-all duration-300 ${borderColor} ${glowColor}`}
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="absolute inset-0 pointer-events-none opacity-[0.05] group-hover:opacity-[0.1] transition-opacity duration-500"
        style={{
          backgroundImage: 'url(/assets/grid_texture.png)',
          backgroundSize: '20px 20px'
        }}
      />

      <div className="p-4 flex flex-col h-full relative z-10">
        <div className="flex justify-between items-start mb-3">
            <span className="text-[10px] font-black uppercase tracking-widest text-slate-400 border border-white/10 px-2 py-0.5 rounded-full">
                {item.source}
            </span>
            <span className="text-[10px] font-mono text-slate-500">
            {item.date || 'Just now'}
            </span>
        </div>

        <h4 className="text-sm font-bold text-white leading-tight mb-2 line-clamp-3">
            {item.headline}
        </h4>

        <div className="mt-auto pt-3 border-t border-white/5 flex items-center justify-between">
            <div className="flex items-center gap-2">
                <div className={`w-1.5 h-1.5 rounded-full ${accentColor} animate-pulse`} />
                <span className={`text-[10px] font-bold uppercase ${isPositive ? 'text-emerald-400' : isNegative ? 'text-red-400' : 'text-slate-400'}`}>
              {(item.sentiment || 'neutral').toUpperCase()}
                </span>
            </div>
            <div className="flex items-center gap-1">
                 <div className="h-1 w-12 bg-white/10 rounded-full overflow-hidden">
                    <div 
                        className={`h-full ${accentColor}`} 
                style={{ width: `${(item.engagement_metrics?.likes || 0) > 100 ? 100 : (item.engagement_metrics?.likes || 50)}%` }} 
                    />
                 </div>
            <span className="text-[9px] font-mono text-slate-500">{(item.engagement_metrics?.likes || 0)}IMP</span>
            </div>
        </div>
      </div>

      {/* Hover Overlay with Summary */}
      <AnimatePresence>
        {isHovered && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="absolute inset-0 z-20 bg-[#0A0C11]/95 p-4 flex flex-col justify-center backdrop-blur-xl"
          >
             <div className="text-[10px] font-black uppercase tracking-widest text-white/40 mb-2">
                AI Summary
             </div>
             <p className="text-xs text-slate-300 leading-relaxed font-medium">
                {item.summary}
             </p>
             <div className="mt-2 text-[10px] text-blue-400 font-bold uppercase tracking-wider flex items-center gap-1">
                Read Full Story <span className="text-lg">›</span>
             </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default React.memo(NewsCard);
