import React, { useRef } from 'react';
import { useDashboardStore } from '../../store/dashboardStore';
import { clsx } from 'clsx';
import { motion, useDragControls } from 'framer-motion';
import AdvancedPanel from './AdvancedPanel';

interface ChatContainerProps {
  docked?: boolean;
}

export const ChatContainer: React.FC<ChatContainerProps> = ({ docked = false }) => {
  const { chatDockPosition, setChatDockPosition, isChatMaximized, theme: globalTheme } = useDashboardStore();
  const controls = useDragControls();
  const constraintsRef = useRef(null);

  // Sync internal state with docked prop if needed (handled by parent mostly)

  const handleDragEnd = (_: any, info: any) => {
    // Docking thresholds
    const viewWidth = window.innerWidth;
    if (info.point.x > viewWidth - 50) {
    // Snap to dock if dragged near right edge
      setChatDockPosition('right');
    }
  };

  const isFloating = chatDockPosition === 'floating';
  const isDocked = docked || !isFloating;

  // Dynamic Theme Classes based on Global Theme (not docked state)
  const isDark = globalTheme === 'dark';

  const theme = !isDark ? {
    container: "bg-white/80 border-l border-white/50 shadow-2xl shadow-blue-900/10 backdrop-blur-2xl ring-1 ring-white/50",
    header: "bg-white/50 border-b border-white/20 text-slate-800 backdrop-blur-md",
    text: "text-slate-800",
    subtext: "text-slate-500",
    inputBg: "bg-white/60 border border-white/40 focus:bg-white/90 focus:border-blue-300 focus:ring-4 focus:ring-blue-400/10 transition-all backdrop-blur-sm",
    inputBorder: "border-white/40",
    inputText: "text-slate-800 placeholder:text-slate-400",
    aiBubble: "bg-white/80 border border-white/60 text-slate-700 shadow-sm backdrop-blur-sm",
    userBubble: "bg-gradient-to-br from-blue-600 to-blue-700 text-white shadow-md shadow-blue-600/20",
    iconColor: "text-slate-400 hover:text-blue-600 transition-colors",
    runBadge: "bg-blue-50/80 text-blue-700 border border-blue-100 backdrop-blur-sm"
  } : {
      // True Void Theme with Premium Depth
      container: "bg-[#050505]/80 border border-white/5 shadow-2xl shadow-black/50 backdrop-blur-3xl ring-1 ring-white/5 bg-gradient-to-b from-gray-900/30 to-black/80",
      header: "bg-black/40 border-b border-white/5 text-gray-100 backdrop-blur-xl",
      text: "text-gray-200",
      subtext: "text-gray-500",
      inputBg: "bg-white/5 border border-white/10 focus:border-white/20 focus:bg-white/10 transition-all backdrop-blur-md",
      inputBorder: "border-white/10",
      inputText: "text-gray-200 placeholder:text-gray-600",
      aiBubble: "bg-white/5 border border-white/10 text-gray-300 shadow-sm backdrop-blur-md",
      userBubble: "bg-blue-600/90 text-white border border-blue-500/30 shadow-lg shadow-blue-900/20 backdrop-blur-sm",
      iconColor: "text-gray-500 hover:text-white transition-colors",
      runBadge: "bg-white/5 text-cyan-400 border border-white/10 backdrop-blur-sm"
  };

  const getContainerStyles = () => {
    if (!docked) {
      if (isChatMaximized) {
        // Centered large modal-like dimensions or just larger
        return `fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[90vw] h-[90vh] max-w-[1200px] rounded-2xl border ${theme.container.split(' ')[1]}`;
      }
      return `fixed bottom-6 right-6 w-[480px] h-[700px] rounded-2xl border ${theme.container.split(' ')[1]}`;
    }
    return "w-full h-full"; // Docked styles handled by parent flex, but we add theme classes in render
  };

  return (
    <motion.div
      ref={constraintsRef}
      drag={isFloating}
      dragControls={controls}
      dragListener={false}
      dragMomentum={false}
      dragElastic={0}
      onDragEnd={handleDragEnd}
      layout={true}
      className={clsx(
        "flex flex-col overflow-hidden transition-all duration-300 ease-in-out z-50",
        isFloating ? getContainerStyles() : getContainerStyles(),
        theme.container
      )}
    >
      <AdvancedPanel
        dashboardData={useDashboardStore.getState().tickerData}
        onClose={() => useDashboardStore.getState().setChatOpen(false)}
        onDragStart={(e) => isFloating && controls.start(e)}
      />
    </motion.div>
  );
};
