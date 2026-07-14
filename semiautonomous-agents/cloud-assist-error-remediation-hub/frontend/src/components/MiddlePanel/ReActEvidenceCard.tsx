import React from 'react';
import { EvidenceItem } from '../../types';
import { Terminal, CheckCircle2, XCircle, Activity } from 'lucide-react';

interface ReActEvidenceCardProps {
  evidence: EvidenceItem[];
}

export const ReActEvidenceCard: React.FC<ReActEvidenceCardProps> = ({ evidence }) => {
  if (evidence.length === 0) return null;

  return (
    <div className="rounded-xl bg-[#111622]/90 border border-slate-800/80 p-5 shadow-lg space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
            <Activity className="w-4 h-4 text-cyan-400" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white tracking-tight">Autonomous ReAct Diagnostic Trace</h2>
            <p className="text-[11px] text-slate-400">Live checks & gcloud queries executed by Cloud Assist</p>
          </div>
        </div>
        <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
          {evidence.length} Checks Executed
        </span>
      </div>

      <div className="space-y-2.5">
        {evidence.map((ev, idx) => {
          const isHealthy = ev.normalOperation === true;
          const isAnomaly = ev.normalOperation === false;

          return (
            <div
              key={ev.id || idx}
              className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80 space-y-2"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  {isHealthy ? (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                  ) : isAnomaly ? (
                    <XCircle className="w-3.5 h-3.5 text-rose-400 flex-shrink-0" />
                  ) : (
                    <Terminal className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0" />
                  )}
                  <span className="text-xs font-semibold text-slate-200">{ev.title}</span>
                </div>

                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800">
                  {ev.checkType}
                </span>
              </div>

              {ev.commandExecuted && (
                <div className="bg-black/70 p-2 rounded border border-slate-800 font-mono text-[10px] text-cyan-300 overflow-x-auto">
                  $ {ev.commandExecuted}
                </div>
              )}

              <p className="text-xs text-slate-300 leading-relaxed whitespace-pre-line">
                {ev.text}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
};
