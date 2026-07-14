import React from 'react';
import { Wrench, CheckCircle2, ShieldCheck, ArrowRight, Zap } from 'lucide-react';

interface RemediationStepsCardProps {
  recommendationText: string;
}

interface ParsedStep {
  number: number;
  title: string;
  description: string;
}

export const RemediationStepsCard: React.FC<RemediationStepsCardProps> = ({ recommendationText }) => {
  if (!recommendationText) return null;

  // Parse structured steps like "1. **Scale Container Memory**: Double..." or plain paragraphs
  const lines = recommendationText
    .split('\n')
    .map(l => l.trim())
    .filter(l => l.length > 0);

  const steps: ParsedStep[] = [];
  let currentStepNum = 1;

  lines.forEach((line) => {
    const match = line.match(/^(\d+)[\.\)]\s*(?:\*\*(.*?)\*\*[:\s]*|([^:]+):\s*)(.*)$/);
    if (match) {
      const num = parseInt(match[1], 10);
      const title = (match[2] || match[3] || 'Action Step').trim();
      const description = match[4].trim();
      steps.push({ number: num, title, description });
      currentStepNum = num + 1;
    } else if (steps.length > 0) {
      steps[steps.length - 1].description += ' ' + line;
    } else {
      // Fallback first step if no numeric numbering found
      steps.push({
        number: currentStepNum++,
        title: line.split(':')[0] || 'Remediation Instruction',
        description: line
      });
    }
  });

  const renderHighlightedText = (text: string) => {
    // Highlight inline code `text` with distinct styled pills
    const parts = text.split(/(`[^`]+`)/g);
    return parts.map((part, idx) => {
      if (part.startsWith('`') && part.endsWith('`')) {
        return (
          <code
            key={idx}
            className="text-cyan-300 bg-cyan-950/60 border border-cyan-800/60 px-1.5 py-0.5 rounded font-mono text-[11px] font-semibold mx-0.5"
          >
            {part.slice(1, -1)}
          </code>
        );
      }
      return part;
    });
  };

  return (
    <div className="rounded-xl bg-[#111622]/90 border border-slate-800/80 p-5 shadow-lg space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
            <Wrench className="w-4 h-4 text-emerald-400" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white tracking-tight">Proactive Remediation Action Roadmap</h2>
            <p className="text-[11px] text-slate-400">Structured execution steps verified by Gemini Cloud Assist</p>
          </div>
        </div>
        <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
          {steps.length} {steps.length === 1 ? 'Action Step' : 'Action Steps'}
        </span>
      </div>

      <div className="space-y-3">
        {steps.map((step) => (
          <div
            key={step.number}
            className="p-4 rounded-xl bg-slate-950/80 border border-slate-800/90 hover:border-emerald-500/40 transition-all duration-200 space-y-2"
          >
            <div className="flex items-center space-x-2.5">
              <span className="w-6 h-6 rounded-md bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center text-[11px] font-mono font-bold">
                {step.number < 10 ? `0${step.number}` : step.number}
              </span>
              <h3 className="text-xs font-bold text-white tracking-wide">
                {step.title}
              </h3>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed pl-8.5">
              {renderHighlightedText(step.description)}
            </p>
          </div>
        ))}
      </div>

      <div className="pt-2 flex items-center justify-between border-t border-slate-800/70">
        <div className="flex items-center space-x-2 text-[11px] text-emerald-400">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Self-healing roadmap ready to execute or delegate to Sandbox Subagent</span>
        </div>
      </div>
    </div>
  );
};
