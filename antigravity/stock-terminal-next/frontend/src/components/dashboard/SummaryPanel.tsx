import React from 'react';

interface SummaryPanelProps {
  ticker: string;
  externalData?: any;
}

export const SummaryPanel: React.FC<SummaryPanelProps> = ({ externalData }) => {
  return (
    <div className="flex flex-col h-full gap-4">
      {/* Header */}
      <div className="flex justify-between items-center border-b border-[var(--border-subtle)] pb-3">
        <h3 className="text-[10px] font-black text-[var(--text-primary)] tracking-[0.25em] uppercase flex items-center gap-2">
          Company Profile
        </h3>
        <span className="text-[9px] font-bold text-[var(--text-muted)] bg-[var(--bg-app)] px-2 py-0.5 rounded border border-[var(--border-subtle)] tracking-widest">
          {externalData?.currency || "USD"}
        </span>
      </div>

      {/* Description */}
      <p className="text-[12px] text-[var(--text-secondary)] leading-relaxed line-clamp-4 font-medium tracking-tight">
        {externalData?.summary || "FactSet Research Systems Inc. is a global financial digital platform and enterprise solutions provider."}
      </p>

      {/* Data Grid */}
      <div className="grid grid-cols-2 gap-x-4 gap-y-3 mt-auto pt-3 border-t border-[var(--border-subtle)]">
        <div className="flex flex-col min-w-0">
          <span className="text-[8px] uppercase tracking-widest text-[var(--text-muted)] font-bold mb-1 truncate">SECTOR</span>
          <span className="text-[11px] font-bold text-[var(--text-primary)] truncate" title={externalData?.sector}>
            {externalData?.sector || "Financial Services"}
          </span>
        </div>

        <div className="flex flex-col min-w-0">
          <span className="text-[8px] uppercase tracking-widest text-[var(--text-muted)] font-bold mb-1 truncate">INDUSTRY</span>
          <span className="text-[11px] font-bold text-[var(--text-primary)] truncate" title={externalData?.industry}>
            {externalData?.industry || "Fin. Data & Exchanges"}
          </span>
        </div>

        <div className="flex flex-col min-w-0">
          <span className="text-[8px] uppercase tracking-widest text-[var(--text-muted)] font-bold mb-1 truncate">EXCHANGE</span>
          <span className="text-[11px] font-bold text-[var(--text-primary)] font-mono">
            NYSE
          </span>
        </div>

        <div className="flex flex-col min-w-0">
          <span className="text-[8px] uppercase tracking-widest text-[var(--text-muted)] font-bold mb-1 truncate">MARKET CAP</span>
          <span className="text-[11px] font-bold text-[var(--text-primary)] font-mono">
            {(externalData?.marketCap ? (externalData.marketCap / 1e9).toFixed(2) + 'B' : "11.02B")}
          </span>
        </div>
      </div>
    </div>
  );
};

