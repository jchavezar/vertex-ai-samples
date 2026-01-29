import React from 'react';

interface SummaryPanelProps {
  ticker: string;
  externalData?: any;
}

export const SummaryPanel: React.FC<SummaryPanelProps> = ({ externalData }) => {
  return (
    <div className="card h-full flex flex-col p-4 bg-[var(--bg-card)] border-[var(--border)] overflow-hidden">
      {/* Header */}
      <div className="flex justify-between items-start mb-3 border-b border-[var(--border)] pb-2">
        <div>
          <h3 className="text-sm font-black text-[var(--text-primary)] tracking-tight uppercase flex items-center gap-2">
            <div className="w-1 h-3.5 bg-[var(--accent)]"></div>
            Corporate Profile
          </h3>
        </div>
        <span className="text-[10px] font-mono text-[var(--text-muted)] bg-[var(--bg-panel)] px-2 py-1 rounded border border-[var(--border-subtle)]">
          {externalData?.currency || "USD"}
        </span>
      </div>

      {/* Description */}
      <p className="text-sm text-[var(--text-secondary)] leading-relaxed mb-4 line-clamp-3 font-medium">
        {externalData?.summary || "FactSet Research Systems Inc. is a global financial digital platform and enterprise solutions provider."}
      </p>

      {/* Data Grid */}
      <div className="grid grid-cols-2 gap-x-4 gap-y-2 mt-auto bg-[var(--bg-panel)] rounded-lg p-2 border border-[var(--border-subtle)]">
        <div className="flex flex-col">
          <span className="text-[10px] uppercase tracking-wider text-[var(--text-muted)] font-bold mb-1">Sector</span>
          <span className="text-xs font-bold text-[var(--text-primary)] truncate" title={externalData?.sector}>
            {externalData?.sector || "Financial Services"}
          </span>
        </div>

        <div className="flex flex-col">
          <span className="text-[10px] uppercase tracking-wider text-[var(--text-muted)] font-bold mb-1">Industry</span>
          <span className="text-xs font-bold text-[var(--text-primary)] truncate" title={externalData?.industry}>
            {externalData?.industry || "Fin. Data & Exchanges"}
          </span>
        </div>

        <div className="flex flex-col">
          <span className="text-[10px] uppercase tracking-wider text-[var(--text-muted)] font-bold mb-1">Exchange</span>
          <span className="text-xs font-bold text-[var(--text-primary)] font-mono">
            NYSE
          </span>
        </div>

        <div className="flex flex-col">
          <span className="text-[10px] uppercase tracking-wider text-[var(--text-muted)] font-bold mb-1">Market Cap</span>
          <span className="text-xs font-bold text-[var(--text-primary)] font-mono">
            {(externalData?.marketCap ? (externalData.marketCap / 1e9).toFixed(2) + 'B' : "11.02B")}
          </span>
        </div>
      </div>
    </div>
  );
};

