import React from 'react';
import { Compass, CheckCircle2 } from 'lucide-react';
import { RichTextRenderer } from '../RichTextRenderer';

interface ExecutiveRecapCardProps {
  recapText: string;
  executionState: string;
}

export const ExecutiveRecapCard: React.FC<ExecutiveRecapCardProps> = ({ recapText, executionState }) => {
  return (
    <div className="rounded-xl bg-gradient-to-br from-slate-900/95 via-[#111726]/95 to-slate-900/95 border border-slate-800/80 p-5 shadow-xl relative overflow-hidden">
      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 via-cyan-400 to-purple-500"></div>
      
      <div className="flex items-center justify-between mb-3.5">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center shadow-md shadow-blue-500/10">
            <Compass className="w-4 h-4 text-cyan-400" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white tracking-tight">Executive Investigation Recap</h2>
            <p className="text-[11px] text-slate-400">Gemini Cloud Assist Diagnostic Synthesis</p>
          </div>
        </div>
        
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>{executionState.replace('INVESTIGATION_EXECUTION_STATE_', '')}</span>
        </span>
      </div>

      <div className="bg-slate-950/70 p-4 rounded-xl border border-slate-800/70">
        <RichTextRenderer text={recapText} />
      </div>
    </div>
  );
};
