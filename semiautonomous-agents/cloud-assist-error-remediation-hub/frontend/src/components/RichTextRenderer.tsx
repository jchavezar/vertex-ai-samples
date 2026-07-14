import React, { useState } from 'react';
import {
  Sparkles,
  CheckCircle2,
  Terminal,
  Copy,
  Check,
  Zap,
  Bookmark,
  ChevronRight,
  HelpCircle,
  Globe
} from 'lucide-react';

interface RichTextRendererProps {
  text: string;
  onRunSandboxCommand?: (cmd: string) => void;
}

export const RichTextRenderer: React.FC<RichTextRendererProps> = ({
  text,
  onRunSandboxCommand
}) => {
  const [copiedCode, setCopiedCode] = useState<string | null>(null);

  const handleCopy = (code: string) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(code);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  if (!text) return null;

  // Split text into line blocks and process code blocks and markdown structures
  const lines = text.split('\n');
  const renderedElements: React.ReactNode[] = [];
  let inCodeBlock = false;
  let codeBuffer: string[] = [];
  let codeLang = 'bash';

  const renderInlineFormats = (str: string, keyPrefix: string) => {
    // Replace **bold** and `code` with styled React components
    const parts = str.split(/(\*\*.*?\*\*|`.*?`)/g);
    return parts.map((part, idx) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return (
          <strong
            key={`${keyPrefix}-bold-${idx}`}
            className="text-white font-bold bg-cyan-950/40 px-1 py-0.5 rounded border border-cyan-800/40 mx-0.5"
          >
            {part.slice(2, -2)}
          </strong>
        );
      }
      if (part.startsWith('`') && part.endsWith('`')) {
        return (
          <code
            key={`${keyPrefix}-code-${idx}`}
            className="text-cyan-300 bg-cyan-950/70 border border-cyan-800/60 px-1.5 py-0.5 rounded font-mono text-[11px] font-semibold mx-0.5"
          >
            {part.slice(1, -1)}
          </code>
        );
      }
      return <span key={`${keyPrefix}-txt-${idx}`}>{part}</span>;
    });
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Check for fenced code blocks
    if (line.trim().startsWith('```')) {
      if (inCodeBlock) {
        // End of code block -> Render interactive Code Box
        const fullCode = codeBuffer.join('\n').trim();
        renderedElements.push(
          <div
            key={`code-block-${i}`}
            className="my-3 rounded-xl bg-[#080b11] border border-slate-800/90 overflow-hidden shadow-lg"
          >
            <div className="flex items-center justify-between px-3.5 py-2 bg-slate-900/90 border-b border-slate-800/80 text-[10px] font-mono text-slate-400">
              <div className="flex items-center space-x-1.5">
                <Terminal className="w-3.5 h-3.5 text-cyan-400" />
                <span className="uppercase font-bold text-slate-300">{codeLang || 'terminal'}</span>
              </div>

              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleCopy(fullCode)}
                  className="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 transition-colors flex items-center gap-1 text-[10px]"
                >
                  {copiedCode === fullCode ? (
                    <>
                      <Check className="w-3 h-3 text-emerald-400" />
                      <span className="text-emerald-400">Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3 h-3" />
                      <span>Copy</span>
                    </>
                  )}
                </button>

                {onRunSandboxCommand && (
                  <button
                    onClick={() => onRunSandboxCommand(fullCode)}
                    className="px-2.5 py-0.5 rounded bg-gradient-to-r from-emerald-600 to-cyan-600 hover:from-emerald-500 hover:to-cyan-500 text-white font-bold transition-all flex items-center gap-1 text-[10px] shadow-sm"
                  >
                    <Zap className="w-3 h-3 text-amber-300 fill-amber-300" />
                    <span>Run in Sandbox</span>
                  </button>
                )}
              </div>
            </div>

            <div className="p-3.5 font-mono text-[11px] text-emerald-300 overflow-x-auto whitespace-pre">
              {fullCode}
            </div>
          </div>
        );
        inCodeBlock = false;
        codeBuffer = [];
      } else {
        inCodeBlock = true;
        codeLang = line.trim().replace('```', '') || 'bash';
      }
      continue;
    }

    if (inCodeBlock) {
      codeBuffer.push(line);
      continue;
    }

    // Process Headings (### or ## or #)
    const headingMatch = line.match(/^(#{1,4})\s+(.*)$/);
    if (headingMatch) {
      const headingText = headingMatch[2].trim();
      renderedElements.push(
        <div
          key={`heading-${i}`}
          className="mt-4 mb-2 first:mt-1 flex items-center space-x-2 pb-1.5 border-b border-slate-800/80"
        >
          <span className="w-6 h-6 rounded-lg bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center flex-shrink-0">
            <Bookmark className="w-3.5 h-3.5 text-cyan-300" />
          </span>
          <h4 className="text-xs font-bold text-white tracking-tight uppercase">
            {renderInlineFormats(headingText, `h-${i}`)}
          </h4>
        </div>
      );
      continue;
    }

    // Process Numbered List Steps (1. **Step**: Desc)
    const stepMatch = line.match(/^(\d+)[\.\)]\s*(.*)$/);
    if (stepMatch) {
      const num = stepMatch[1];
      const stepContent = stepMatch[2];
      renderedElements.push(
        <div
          key={`step-${i}`}
          className="my-2 p-3 rounded-xl bg-slate-950/70 border border-slate-800/80 hover:border-cyan-500/30 transition-all flex items-start space-x-2.5"
        >
          <span className="w-5 h-5 rounded-md bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 flex items-center justify-center text-[10px] font-mono font-bold flex-shrink-0 mt-0.5">
            {num.length === 1 ? `0${num}` : num}
          </span>
          <div className="text-xs text-slate-200 leading-relaxed flex-1">
            {renderInlineFormats(stepContent, `st-${i}`)}
          </div>
        </div>
      );
      continue;
    }

    // Process Bullet list items (- or *)
    const bulletMatch = line.match(/^[\-\*]\s+(.*)$/);
    if (bulletMatch) {
      renderedElements.push(
        <div
          key={`bullet-${i}`}
          className="my-1.5 flex items-start space-x-2 pl-1"
        >
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0 mt-0.5" />
          <div className="text-xs text-slate-300 leading-relaxed">
            {renderInlineFormats(bulletMatch[1], `bl-${i}`)}
          </div>
        </div>
      );
      continue;
    }

    // Normal paragraph text
    if (line.trim().length > 0) {
      renderedElements.push(
        <p key={`p-${i}`} className="my-2 text-xs text-slate-300 leading-relaxed">
          {renderInlineFormats(line, `p-${i}`)}
        </p>
      );
    }
  }

  return <div className="space-y-1">{renderedElements}</div>;
};
