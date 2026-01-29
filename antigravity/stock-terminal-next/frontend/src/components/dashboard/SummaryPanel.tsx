import React from 'react';

interface SummaryPanelProps {
  ticker: string;
  externalData?: any;
}

export const SummaryPanel: React.FC<SummaryPanelProps> = ({ externalData }) => {
  return (
    <div className="flex flex-col gap-4">
      {/* Header */}
      <div className="flex justify-between items-center border-b border-[var(--border-subtle)] pb-2 mb-0.5">
        <h3 className="text-[10px] font-black text-[var(--text-primary)] tracking-[0.25em] uppercase flex items-center gap-2">
          Company Profile
        </h3>
        <span className="text-[9px] font-bold text-[var(--text-muted)] bg-[var(--bg-app)] px-2 py-0.5 rounded border border-[var(--border-subtle)] tracking-widest">
          {externalData?.currency || "USD"}
        </span>
      </div>

      {/* Description */}
      <div className="flex-1 flex flex-col justify-center">
        <p className="text-[12.5px] leading-snug text-[var(--text-secondary)] font-medium tracking-tight">
          {externalData?.summary || "FactSet Research Systems Inc. is a global financial digital platform and enterprise solutions provider."}
        </p>
      </div>

      {/* Profile Clusters - Shrink Wrapped */}
      <div className="flex flex-col gap-3 mt-auto pt-4 border-t border-[var(--border-subtle)]">
        {/* Cluster 1: Classification */}
        <div className="flex flex-col gap-2.5">
          <div className="flex flex-col gap-0.5 group/item cursor-default">
            <div className="flex items-center gap-2">
              <span className="text-[7.5px] uppercase tracking-[0.25em] text-[var(--text-muted)] font-black opacity-50 group-hover/item:opacity-100 transition-opacity">Sector</span>
              <div className="h-[0.5px] flex-1 bg-[var(--border-subtle)]/20"></div>
            </div>
            <span className="text-[12px] font-bold text-[var(--text-primary)] leading-tight break-words">
              {externalData?.sector || "Financial Services"}
            </span>
          </div>

          <div className="flex flex-col gap-0.5 group/item cursor-default">
            <div className="flex items-center gap-2">
              <span className="text-[7.5px] uppercase tracking-[0.25em] text-[var(--text-muted)] font-black opacity-50 group-hover/item:opacity-100 transition-opacity">Industry</span>
              <div className="h-[0.5px] flex-1 bg-[var(--border-subtle)]/20"></div>
            </div>
            <span className="text-[12px] font-bold text-[var(--text-primary)] leading-tight break-words">
              {externalData?.industry || "Financial Data & Exchanges"}
            </span>
          </div>
        </div>

        {/* Cluster 2: Market Context */}
        <div className="grid grid-cols-2 gap-x-6 gap-y-3 pt-1">
          <div className="flex flex-col gap-0.5 group/item">
            <div className="flex items-center gap-2">
              <span className="text-[7.5px] uppercase tracking-[0.25em] text-[var(--text-muted)] font-black opacity-50">Exchange</span>
              <div className="h-[0.5px] flex-1 bg-[var(--border-subtle)]/20"></div>
            </div>
            <span className="text-[11px] font-bold text-[var(--brand)] font-mono flex items-center gap-1.5 pt-0.5">
              <div className="w-1 h-1 rounded-full bg-[var(--brand)] shadow-[0_0_8px_var(--brand)]"></div>
              {externalData?.exchange || "NYSE"}
            </span>
          </div>
          <div className="flex flex-col gap-0.5 group/item">
            <div className="flex items-center gap-2">
              <span className="text-[7.5px] uppercase tracking-[0.25em] text-[var(--text-muted)] font-black opacity-50">Mkt Cap</span>
              <div className="h-[0.5px] flex-1 bg-[var(--border-subtle)]/20"></div>
            </div>
            <span className="text-[11px] font-bold text-[var(--text-primary)] font-mono pt-0.5">
              {(externalData?.marketCap ? (externalData.marketCap / 1e9).toFixed(2) + 'B' : "11.02B")}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
