import React, { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { clsx } from 'clsx';
import { useDashboardStore } from '../../store/dashboardStore';

interface ReasoningTabProps {
  sessionId?: string;
  isActive: boolean;
}

export const ReasoningTab: React.FC<ReasoningTabProps> = ({ sessionId = "default_chat", isActive }) => {
  const [narrative, setNarrative] = useState<string | null>(null);
  const [status, setStatus] = useState<'pending' | 'complete'>('pending');
  const { theme } = useDashboardStore();
  const isDark = theme === 'dark';

  useEffect(() => {
    if (!isActive) return;

    // Poll for reasoning
    let isMounted = true;
    const poll = async () => {
      try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/session/${sessionId}/reasoning`);
        if (res.ok) {
          const data = await res.json();
          if (isMounted) {
            setNarrative(data.narrative);
            setStatus(data.status);
            if (data.status === 'pending') {
              // Continue polling
              setTimeout(poll, 2000);
            }
          }
        } else {
          setTimeout(poll, 5000); // Retry slow
        }
      } catch (e) {
        console.error("Reasoning poll error", e);
        setTimeout(poll, 5000);
      }
    };

    poll();
    return () => { isMounted = false; };
  }, [isActive, sessionId]);

  if (!narrative && status === 'pending') {
    return (
      <div className={clsx("h-full flex flex-col items-center justify-center p-8 text-center", isDark ? "text-[var(--text-muted)]" : "text-slate-500")}>
        <div className="w-8 h-8 rounded-full border-2 border-[var(--brand)] border-t-transparent animate-spin mb-4" />
        <p className="font-medium animate-pulse">Analyzing Execution Trace...</p>
        <p className="text-xs opacity-70 mt-2">The Observation Agent is reviewing the logs to explain the performance.</p>
      </div>
    );
  }

  return (
    <div className={clsx("h-full overflow-y-auto p-6 prose prose-sm max-w-none", isDark ? "prose-invert" : "")}>
      {narrative ? (
        <>
          <div className="flex justify-end mb-4">
            <button
              onClick={() => setNarrative(null)}
              className={clsx(
                "text-xs px-2 py-1 rounded hover:bg-black/5 transition-colors flex items-center gap-1",
                isDark ? "text-slate-400 hover:bg-white/10" : "text-slate-500"
              )}
            >
              Clear Analysis
            </button>
          </div>
          <ReactMarkdown>{narrative}</ReactMarkdown>
        </>
      ) : (
        <div className="text-center opacity-50 mt-20">No reasoning data available yet.</div>
      )}
    </div>
  );
};
