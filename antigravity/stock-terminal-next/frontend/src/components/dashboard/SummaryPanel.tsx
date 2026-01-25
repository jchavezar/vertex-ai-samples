import React from 'react';

interface SummaryPanelProps {
  ticker: string;
  externalData?: any;
}

export const SummaryPanel: React.FC<SummaryPanelProps> = ({ ticker, externalData }) => {
  return (
    <div className="card h-full flex flex-col">
      <div className="flex items-center justify-between mb-3 text-[13px] uppercase tracking-wide text-[var(--text-secondary)]">Profile</div>
      <div className="flex-1 flex flex-col">
        <p className="text-[11px] text-[var(--text-secondary)] leading-[1.4] mb-5 line-clamp-5 overflow-hidden">
          {externalData?.summary || "FactSet Research Systems Inc. is a global financial digital platform and enterprise solutions provider."}
        </p>

        <div className="flex flex-col gap-2 mb-auto">
          <div className="grid grid-cols-[100px_1fr] text-[11px]">
            <span className="text-[var(--text-muted)]">Sector</span>
            <span className="text-[var(--text-primary)] font-medium">{externalData?.sector || "Software and Consulting"}</span>
          </div>
          <div className="grid grid-cols-[100px_1fr] text-[11px]">
            <span className="text-[var(--text-muted)]">Industry</span>
            <span className="text-[var(--text-primary)] font-medium">{externalData?.industry || "Professional Content Providers"}</span>
          </div>
          <div className="grid grid-cols-[100px_1fr] text-[11px]">
            <span className="text-[var(--text-muted)]">Exchange</span>
            <span className="text-[var(--text-primary)] font-medium">NYSE</span>
          </div>
        </div>

        <div className="mt-6">
          <div className="flex items-center justify-between mb-3 text-[13px] uppercase tracking-wide text-[var(--text-secondary)]">Value Bridge</div>
          <div className="flex flex-col gap-1">
            <div className="flex justify-between text-[11px] py-1 border-b border-dotted border-[var(--border-light)] font-bold">
              <span>Market Cap (M)</span> 
              <span>{externalData?.marketCap ? (externalData.marketCap / 1e6).toFixed(2) : "11,015.51"}</span>
            </div>
            <div className="flex justify-between text-[11px] py-1 border-b border-dotted border-[var(--border-light)]">
              <span>Currency</span> 
              <span>{externalData?.currency || "USD"}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
