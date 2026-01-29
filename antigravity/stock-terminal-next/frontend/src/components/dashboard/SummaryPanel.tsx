import React from 'react';

interface SummaryPanelProps {
  ticker: string;
  externalData?: any;
}

export const SummaryPanel: React.FC<SummaryPanelProps> = ({ externalData }) => {
  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Header - Fixed */}
      <div className="flex justify-between items-center border-b border-[var(--border-subtle)] pb-2 mb-2 shrink-0">
        <h3 className="text-[10px] font-black text-[var(--text-primary)] tracking-[0.25em] uppercase flex items-center gap-2">
          Company Profile
        </h3>
        <span className="text-[10px] font-bold text-[var(--text-muted)] bg-[var(--bg-app)] px-2 py-0.5 rounded border border-[var(--border-subtle)] tracking-widest">
          {externalData?.currency || "USD"}
        </span>
      </div>

      {/* Scrollable Content Area */}
      <div className="flex-1 overflow-y-auto no-scrollbar flex flex-col gap-3">
        {/* Description */}
        <div className="py-1">
          <p className="text-[13px] leading-relaxed text-[var(--text-secondary)] font-medium tracking-normal">
            {externalData?.summary || "FactSet Research Systems Inc. is a global financial digital platform and enterprise solutions provider."}
          </p>
        </div>

        {/* Profile Clusters - Higher Visibility */}
        <div className="flex flex-col gap-4 mt-auto pt-3 border-t border-[var(--border-subtle)]">
          {/* Cluster 1: Classification */}
          <div className="flex flex-col gap-2.5">
            <div className="flex flex-col gap-1 group/item cursor-default">
              <div className="flex items-center gap-2">
                <span className="text-[10px] uppercase tracking-[0.2em] text-[var(--text-muted)] font-black group-hover/item:text-[var(--text-primary)] transition-colors">Sector</span>
                <div className="h-[1px] flex-1 bg-[var(--border-subtle)]"></div>
              </div>
              <span className="text-[14px] font-bold text-[var(--text-primary)] leading-tight break-words">
                {externalData?.sector || "Financial Services"}
              </span>
            </div>

            <div className="flex flex-col gap-1 group/item cursor-default">
              <div className="flex items-center gap-2">
                <span className="text-[10px] uppercase tracking-[0.2em] text-[var(--text-muted)] font-black group-hover/item:text-[var(--text-primary)] transition-colors">Industry</span>
                <div className="h-[1px] flex-1 bg-[var(--border-subtle)]"></div>
              </div>
              <span className="text-[14px] font-bold text-[var(--text-primary)] leading-tight break-words">
                {externalData?.industry || "Financial Data & Exchanges"}
              </span>
            </div>
          </div>

          {/* Cluster 2: Market Context */}
          <div className="grid grid-cols-2 gap-x-8 gap-y-3 pb-1">
            <div className="flex flex-col gap-1 group/item">
              <div className="flex items-center gap-2">
                <span className="text-[10px] uppercase tracking-[0.2em] text-[var(--text-muted)] font-black">Exchange</span>
                <div className="h-[1px] flex-1 bg-[var(--border-subtle)]"></div>
              </div>
              <span className="text-[13px] font-bold text-[var(--brand)] font-mono flex items-center gap-2 pt-0.5">
                <div className="w-1.5 h-1.5 rounded-full bg-[var(--brand)] shadow-[0_0_8px_var(--brand)]"></div>
                {externalData?.exchange || "NYSE"}
              </span>
            </div>
            <div className="flex flex-col gap-1 group/item">
              <div className="flex items-center gap-2">
                <span className="text-[10px] uppercase tracking-[0.2em] text-[var(--text-muted)] font-black">Mkt Cap</span>
                <div className="h-[1px] flex-1 bg-[var(--border-subtle)]"></div>
              </div>
              <span className="text-[13px] font-bold text-[var(--text-primary)] font-mono pt-0.5">
                {(externalData?.marketCap ? (externalData.marketCap / 1e9).toFixed(2) + 'B' : "10.10B")}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
