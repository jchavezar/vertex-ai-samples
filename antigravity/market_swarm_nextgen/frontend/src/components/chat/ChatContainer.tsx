import React, { useRef } from 'react';
import { useDashboardStore } from '../../store/dashboardStore';
import { clsx } from 'clsx';
import { motion, useDragControls, AnimatePresence } from 'framer-motion';
import AdvancedPanel from './AdvancedPanel';
import { AnalysisOverlay } from './AnalysisOverlay';

interface ChatContainerProps {
  docked?: boolean;
}

export const ChatContainer: React.FC<ChatContainerProps> = ({ docked: _docked = false }) => {
  const {
    chatDockPosition,
    setChatDockPosition,
    isChatMaximized,
    theme: globalTheme,
    activeAnalysisData
  } = useDashboardStore();
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


  // Resize State
  const [floatingSize, setFloatingSize] = React.useState({ width: 480, height: 650 });

  return (
    <motion.div
      ref={constraintsRef}
      drag={isFloating}
      dragControls={controls}
      dragListener={false}
      dragMomentum={false}
      dragElastic={0}
      onDragEnd={handleDragEnd}
      className={clsx(
        "flex",
        (isChatMaximized || !isFloating) ? "w-full h-full" : "w-auto h-auto"
      )}
    >
      <motion.div
        className={clsx(
          "flex overflow-visible ease-in-out w-full h-full relative group", // Changed overflow-hidden to visible to allow resize handle
          theme.container,
          (isChatMaximized || isFloating) ? "fixed z-[1000]" : "relative z-[100]"
        )}
        style={{
          width: isChatMaximized ? '100vw' : (isFloating ? floatingSize.width : '100%'),
          height: isChatMaximized ? '100vh' : (isFloating ? floatingSize.height : '100%'),
          borderRadius: isChatMaximized ? '0px' : (isFloating ? '24px' : '0px'),
          border: isChatMaximized ? 'none' : (isFloating ? '2px solid black' : undefined),
          inset: isChatMaximized ? '0px' : undefined,
          right: isFloating ? '20px' : undefined,
          bottom: isFloating ? '100px' : undefined,
          boxShadow: isChatMaximized ? 'none' : (isFloating ? '0 25px 50px -12px rgba(0,0,0,0.5)' : undefined),
          fontSize: isFloating ? `${Math.max(16, 16 * (floatingSize.width / 480))}px` : undefined // Dynamic Font Scaling
        }}
        initial={false}
      >
        <div className={clsx(
          "flex flex-1 overflow-hidden h-full w-full bg-inherit rounded-[inherit]", // Added rounded-inherit to clip inner content
          activeAnalysisData && isChatMaximized ? "flex-row shrink-0" : "flex-col"
        )}>
          <div className={clsx(
            "flex flex-col transition-all duration-500 h-full overflow-hidden shrink-0",
            activeAnalysisData && isChatMaximized ? "w-1/2" : "w-full flex-1"
          )}>
            <AdvancedPanel
              onClose={() => useDashboardStore.getState().setChatOpen(false)}
              onDragStart={(e) => isFloating && controls.start(e)}
            />
          </div>

          <AnimatePresence mode="wait">
            {activeAnalysisData && isChatMaximized && (
              <motion.div
                initial={{ width: 0, opacity: 0 }}
                animate={{ width: "50%", opacity: 1 }}
                exit={{ width: 0, opacity: 0 }}
                transition={{ duration: 0.4, ease: "easeInOut" }}
                className="border-l border-white/10 overflow-hidden h-full flex flex-col bg-inherit shrink-0"
              >
                <AnalysisOverlay />
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Resize Handle */}
        {isFloating && (
          <motion.div
            drag
            dragMomentum={false}
            dragElastic={0}
            onDrag={(_, info) => {
              setFloatingSize(prev => ({
                width: Math.max(300, prev.width + info.delta.x),
                height: Math.max(300, prev.height + info.delta.y)
              }));
            }}
            className="absolute bottom-1 right-1 w-6 h-6 cursor-nwse-resize z-50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
          >
            {/* Visual Grip */}
            <div className="w-1.5 h-1.5 bg-gray-400/50 rounded-full mb-0.5 ml-0.5" />
            <svg width="6" height="6" viewBox="0 0 6 6" fill="none" className="absolute bottom-1.5 right-1.5">
              <path d="M6 6H0L6 0V6Z" fill="currentColor" className="text-gray-400" />
            </svg>
          </motion.div>
        )}
      </motion.div>
    </motion.div>
  );
};
