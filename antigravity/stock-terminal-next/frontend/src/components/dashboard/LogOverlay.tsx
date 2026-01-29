import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Terminal } from 'lucide-react';
import clsx from 'clsx';

interface LogEntry {
  id: number;
  type: 'log' | 'warn' | 'error' | 'info';
  message: string;
  timestamp: string;
}

interface LogOverlayProps {
  isOpen: boolean;
  onClose: () => void;
}

export const LogOverlay: React.FC<LogOverlayProps> = ({ isOpen, onClose }) => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isOpen) return;

    // Capture console methods
    const originalLog = console.log;
    const originalWarn = console.warn;
    const originalError = console.error;
    const originalInfo = console.info;

    const addLog = (type: LogEntry['type'], ...args: unknown[]) => {
      const message = args.map(arg =>
        typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
      ).join(' ');

      setLogs(prev => [
        ...prev,
        {
          id: Date.now() + Math.random(),
          type,
          message,
          timestamp: new Date().toLocaleTimeString(),
        }
      ].slice(-50)); // Keep last 50
    };

    console.log = (...args) => { originalLog(...args); addLog('log', ...args); };
    console.warn = (...args) => { originalWarn(...args); addLog('warn', ...args); };
    console.error = (...args) => { originalError(...args); addLog('error', ...args); };
    console.info = (...args) => { originalInfo(...args); addLog('info', ...args); };

    return () => {
      console.log = originalLog;
      console.warn = originalWarn;
      console.error = originalError;
      console.info = originalInfo;
    };
  }, [isOpen]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0, x: 100, scale: 0.9 }}
          animate={{ opacity: 1, x: 0, scale: 1 }}
          exit={{ opacity: 0, x: 100, scale: 0.9 }}
          className="fixed bottom-24 right-10 w-[450px] h-[500px] bg-black/40 backdrop-blur-[40px] border border-white/10 rounded-3xl shadow-[0_40px_100px_rgba(0,0,0,0.8)] z-[2000] flex flex-col overflow-hidden"
        >
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-5 border-b border-white/5 bg-white/5 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-cyan-500/10 to-transparent animate-scan" style={{ width: '50px' }} />
            <div className="flex items-center gap-3">
              <div className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse shadow-[0_0_10px_rgba(34,211,238,0.8)]" />
              <span className="text-[10px] uppercase tracking-[0.3em] font-black text-white/60">Neural Log Stream</span>
            </div>
            <button
              onClick={onClose}
              className="w-8 h-8 flex items-center justify-center bg-white/5 hover:bg-white/10 rounded-xl transition-all duration-300 text-white/40 hover:text-white"
            >
              <X size={16} />
            </button>
          </div>

          {/* Log Area */}
          <div
            ref={scrollRef}
            className="flex-1 overflow-y-auto p-6 space-y-3 font-mono text-[10px] custom-scrollbar selection:bg-cyan-500/30"
          >
            {logs.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-white/20 space-y-4">
                <Terminal size={40} strokeWidth={1} className="animate-pulse" />
                <p className="uppercase tracking-[0.2em] font-bold">Awaiting telemetry...</p>
              </div>
            ) : (
              logs.map((log) => (
                <div key={log.id} className="flex gap-4 group animate-in fade-in slide-in-from-right-2 duration-500 border-l-2 border-transparent hover:border-cyan-500/30 pl-2 transition-all">
                  <span className="text-white/10 shrink-0 font-black">
                    {log.timestamp.split(' ')[0]}
                  </span>
                  <span className={clsx(
                    "break-all leading-relaxed",
                    log.type === 'error' && "text-rose-400 font-bold",
                    log.type === 'warn' && "text-amber-300",
                    log.type === 'info' && "text-cyan-400",
                    log.type === 'log' && "text-white/70"
                  )}>
                    <span className="opacity-50 mr-2">»</span>
                    {log.message}
                  </span>
                </div>
              ))
            )}
          </div>

          {/* Footer */}
          <div className="px-6 py-4 border-t border-white/5 bg-black/20 flex justify-between items-center text-[9px] font-black uppercase tracking-widest">
            <div className="flex items-center gap-2 text-white/20">
              <span className="w-1 h-1 rounded-full bg-cyan-500/50" />
              Intelligence Synchronized
            </div>
            <button
              onClick={() => setLogs([])}
              className="text-cyan-400/60 hover:text-cyan-400 transition-colors"
            >
              Flush Buffer
            </button>
          </div>


        </motion.div>
      )}
    </AnimatePresence>
  );
};

