import React, { useRef, useEffect } from 'react';
import { useTerminalChat } from '../../hooks/useTerminalChat';
import { useDashboardStore } from '../../store/dashboardStore';
import { Send, Terminal, Sparkles, Minimize2, PanelRightOpen, PanelLeftOpen } from 'lucide-react';
import clsx from 'clsx';
import { motion, useDragControls } from 'framer-motion';

interface ChatContainerProps {
  docked?: boolean;
}

export const ChatContainer: React.FC<ChatContainerProps> = ({ docked = false }) => {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useTerminalChat();
  const { chatDockPosition, setChatDockPosition, chatPosition, setChatPosition } = useDashboardStore();
  const controls = useDragControls();
  const constraintsRef = useRef(null);

  // Sync internal state with docked prop if needed (handled by parent mostly)

  const handleDragEnd = (_: any, info: any) => {
    // Docking thresholds
    const viewWidth = window.innerWidth;
    if (info.point.x > viewWidth - 150) {
      setChatDockPosition('right');
    } else {
      // Save position if needed
      // setChatPosition({ x: info.point.x, y: info.point.y });
    }
  };

  const isFloating = chatDockPosition === 'floating';
  const isDocked = docked || chatDockPosition !== 'floating';

  // Dynamic Theme Classes
  const theme = isDocked ? {
    container: "bg-white/90 border-l border-gray-200 shadow-none backdrop-blur-xl",
    header: "bg-white/50 border-gray-100 text-slate-700",
    text: "text-slate-800",
    subtext: "text-slate-500",
    inputBg: "bg-gray-100/50 focus:bg-white",
    inputBorder: "border-gray-200 focus:border-blue-500/30",
    inputText: "text-slate-800 placeholder:text-slate-400",
    aiBubble: "bg-gray-100/80 text-slate-700 border-gray-200",
    userBubble: "bg-blue-600 text-white shadow-md shadow-blue-500/10",
    iconColor: "text-slate-500 hover:text-slate-800",
    runBadge: "bg-gray-200/50 text-cyan-700 border-gray-200"
  } : {
    container: "bg-[#050505]/80 border-white/10 shadow-2xl backdrop-blur-xl",
    header: "bg-white/5 border-white/5 text-white",
    text: "text-white",
    subtext: "text-white/40",
    inputBg: "bg-[#0A0A0A] focus:bg-white/5",
    inputBorder: "border-white/5 focus:border-blue-500/40",
    inputText: "text-white placeholder:text-white/20",
    aiBubble: "bg-white/5 text-gray-300 border-white/5",
    userBubble: "bg-blue-600/20 text-blue-100 border-blue-500/30",
    iconColor: "text-white/40 hover:text-white",
    runBadge: "bg-black/30 text-cyan-400/80 border-white/5"
  };

  const getContainerStyles = () => {
    if (!docked) {
      return `fixed bottom-6 right-6 w-[380px] h-[600px] rounded-2xl border ${theme.container.split(' ')[1]}`;
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
      dragElastic={0.1}
      onDragEnd={handleDragEnd}
      layout={true}
      className={clsx(
        "flex flex-col overflow-hidden transition-all duration-300 ease-in-out",
        isFloating ? getContainerStyles() : getContainerStyles(),
        theme.container
      )}
    >
      {/* Header */}
      <div
        onPointerDown={(e) => isFloating && controls.start(e)}
        className={clsx(
          "p-4 border-b flex items-center justify-between backdrop-blur-sm relative z-10 select-none",
          theme.header,
          isFloating ? "cursor-grab active:cursor-grabbing" : "cursor-default"
        )}
      >
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <Terminal size={14} className="text-white" />
          </div>
          <div>
            <h2 className={clsx("font-bold text-xs tracking-wider", theme.text)}>TERMINAL</h2>
          </div>
        </div>

        <div className="flex gap-1">
          {!isFloating ? (
            <button
              onClick={() => setChatDockPosition('floating')}
              className={clsx("p-1.5 rounded-md transition-colors", theme.iconColor)}
              title="Undock"
            >
              <Minimize2 size={14} />
            </button>
          ) : (
            <button
              onClick={() => setChatDockPosition('right')}
              className={clsx("p-1.5 rounded-md transition-colors", theme.iconColor)}
              title="Dock Right"
            >
              <PanelRightOpen size={14} />
            </button>
          )}

          <button
            onClick={() => useDashboardStore.getState().setChatOpen(false)}
            className={clsx("p-1.5 rounded-md transition-colors hover:bg-red-500/10 hover:text-red-400", theme.iconColor)}
            title="Minimize Chat"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6 6 18" /><path d="m6 6 12 12" /></svg>
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-hide">
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 opacity-40">
            <Sparkles size={32} className="mb-3 text-blue-400" />
            <p className={clsx("text-xs", theme.subtext)}>Ready for inputs...</p>
          </div>
        )}

        {messages.map((m) => (
          <motion.div
            layout
            key={m.id}
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            className={clsx(
              "p-3 rounded-xl text-xs relative border",
              m.role === 'user'
                ? clsx("self-end ml-auto", theme.userBubble)
                : clsx("self-start mr-auto", theme.aiBubble)
            )}
            style={{ maxWidth: '90%' }}
          >
            <div className="whitespace-pre-wrap leading-relaxed">{m.content}</div>
            {m.toolInvocations?.map((tool) => (
              <div key={tool.toolCallId} className={clsx("mt-2 text-[10px] p-2 rounded border font-mono flex items-center gap-1.5", theme.runBadge)}>
                <div className="w-1 h-1 bg-cyan-400 rounded-full animate-pulse" />
                <span className="opacity-70">RUN:</span> {tool.toolName}
              </div>
            ))}
          </motion.div>
        ))}
        {isLoading && (
          <div className={clsx("flex items-center gap-2 text-[10px] font-mono pl-2", theme.subtext)}>
            <span className="animate-pulse">Thinking...</span>
          </div>
        )}
      </div>

      {/* Input */}
      <div className={clsx("p-4 border-t", theme.header)}>
        <form onSubmit={handleSubmit} className="relative">
          <input
            value={input}
            onChange={handleInputChange}
            placeholder="Execute command..."
            className={clsx(
              "w-full rounded-lg pl-4 pr-10 py-3 border transition-all duration-200 text-xs font-mono outline-none",
              theme.inputBg,
              theme.inputBorder,
              theme.inputText
            )}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 
                        text-blue-400 hover:text-blue-300 
                        disabled:opacity-30 disabled:cursor-not-allowed
                        transition-colors"
          >
            <Send size={14} />
          </button>
        </form>
      </div>
    </motion.div>
  );
};

