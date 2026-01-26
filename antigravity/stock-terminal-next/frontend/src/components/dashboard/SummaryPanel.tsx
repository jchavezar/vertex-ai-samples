import React from 'react';

interface SummaryPanelProps {
  ticker: string;
  externalData?: any;
}

export const SummaryPanel: React.FC<SummaryPanelProps> = ({ externalData }) => {
  return (
    <div className="h-full flex flex-col gap-4 rounded-xl">
      {/* Profile Card */}
      <div className="card flex-1">
        <h3 className="text-[12px] font-bold text-[var(--text-secondary)] tracking-widest uppercase mb-4">PROFILE</h3>
        <p className="text-[12px] text-[var(--text-secondary)] leading-relaxed mb-6 line-clamp-4">
          {externalData?.summary || "FactSet Research Systems Inc. is a global financial digital platform and enterprise solutions provider."}
        </p>

        <div className="space-y-3">
          <div className="flex justify-between items-center text-[11px] border-b border-[var(--border)] pb-2 last:border-0">
            <span className="text-[var(--text-muted)] font-medium">Sector</span>
            <span className="text-[var(--text-primary)] font-semibold text-right">{externalData?.sector || "Software and Consulting"}</span>
          </div>
          <div className="flex justify-between items-center text-[11px] border-b border-[var(--border)] pb-2 last:border-0">
            <span className="text-[var(--text-muted)] font-medium">Industry</span>
            <span className="text-[var(--text-primary)] font-semibold text-right">{externalData?.industry || "Professional Content Providers"}</span>
          </div>
          <div className="flex justify-between items-center text-[11px] border-b border-[var(--border)] pb-2 last:border-0">
            <span className="text-[var(--text-muted)] font-medium">Exchange</span>
            <span className="text-[var(--text-primary)] font-semibold text-right">NYSE</span>
          </div>
        </div>
      </div>

      {/* Value Bridge Card */}
      <div className="card">
        <h3 className="text-[12px] font-bold text-[var(--text-secondary)] tracking-widest uppercase mb-4">VALUE BRIDGE</h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center text-[11px] border-b border-[var(--border)] pb-2">
            <span className="text-[var(--text-primary)] font-bold">Market Cap (M)</span>
            <span className="text-[var(--text-primary)] font-bold">{externalData?.marketCap ? (externalData.marketCap / 1e6).toFixed(2) : "11,015.51"}</span>
          </div>
          <div className="flex justify-between items-center text-[11px]">
            <span className="text-[var(--text-muted)] font-medium">Currency</span>
            <span className="text-[var(--text-primary)] font-semibold">{externalData?.currency || "USD"}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
