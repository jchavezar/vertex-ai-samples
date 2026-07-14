import React, { useState, useEffect } from 'react';
import { Sparkles } from 'lucide-react';

const THINKING_PHRASES = [
  "Analyzing Cloud Logging stack trace...",
  "Consulting Gemini Cloud Assist diagnostic tree...",
  "Searching Google Cloud docs & community solutions...",
  "Formulating verified remediation plan..."
];

export const ClaudeInkSpinner: React.FC = () => {
  const [phraseIdx, setPhraseIdx] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setPhraseIdx((prev) => (prev + 1) % THINKING_PHRASES.length);
    }, 2400);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="flex flex-col items-start p-4 rounded-xl bg-slate-900/80 border border-cyan-500/30 shadow-lg shadow-cyan-500/10 space-y-3 max-w-[280px]">
      {/* Claude Code "Ink" Wave Bar Graphic */}
      <div className="flex items-center space-x-1.5 h-6">
        {[0, 1, 2, 3, 4, 5, 6, 7].map((bar) => (
          <div
            key={bar}
            className="w-1 bg-gradient-to-t from-blue-600 via-cyan-400 to-purple-400 rounded-full animate-ink-wave shadow-sm shadow-cyan-400/40"
            style={{
              animationDelay: `${bar * 0.12}s`,
              height: '20px'
            }}
          ></div>
        ))}
      </div>

      <div className="flex items-center space-x-2 text-xs font-medium text-cyan-300">
        <Sparkles className="w-3.5 h-3.5 text-cyan-400 animate-spin" />
        <span className="animate-pulse">{THINKING_PHRASES[phraseIdx]}</span>
      </div>
    </div>
  );
};
