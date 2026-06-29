import React from 'react';
import { useDashboardStore, CompanyMetrics } from '../store/dashboardStore';

export function FinancialGridCard({ company }: { company: CompanyMetrics }) {
  const { activeCompany, setActiveCompany } = useDashboardStore();
  const isActive = activeCompany?.ticker === company.ticker;

  return (
    <div 
      onClick={() => setActiveCompany(company)}
      className={`group flex flex-col gap-4 border-b border-[#d8d6d0] pb-8 cursor-pointer rounded-none p-6 transition-all ${isActive ? 'bg-[#f4f3ef]' : 'hover:bg-[#f4f3ef]/50'}`}
    >
      {/* Black Void Technical Header Container */}
      <div className="relative h-40 w-full overflow-hidden border border-[#d8d6d0] rounded-none bg-[#111111] flex flex-col justify-end p-6">
        <div className="absolute inset-0 bg-gradient-to-t from-[#111111] via-[#111111]/80 to-transparent z-10" />
        <div className="absolute top-4 left-4 z-20 border border-[#d8d6d0] bg-[#faf9f6] text-[#1a1a19] px-2 py-0.5 text-[10px] font-semibold tracking-wider uppercase rounded-none">
          {company.sector}
        </div>
        <div className="absolute top-4 right-4 z-20 border border-[#d8d6d0] bg-[#faf9f6] text-[#1a1a19] px-2 py-0.5 text-[10px] font-mono font-semibold tracking-wider uppercase rounded-none">
          {company.ticker}
        </div>
        <div className="z-20 relative text-[#faf9f6]">
          <span className="text-xs font-mono tracking-widest text-[#d8d6d0] uppercase block mb-1">
            CFO: {company.cfo}
          </span>
          <h3 className="text-2xl font-medium leading-snug group-hover:underline decoration-1 underline-offset-4">
            {company.name}
          </h3>
        </div>
      </div>
      
      {/* Key Financial Metrics Table */}
      <div className="grid grid-cols-3 gap-4 border-t border-[#d8d6d0] pt-4 mt-2 font-mono text-xs">
        <div className="flex flex-col border-r border-[#d8d6d0] pr-4">
          <span className="text-[#7c7a75] text-[10px] uppercase mb-1">Revenue</span>
          <span className="text-[#1a1a19] font-bold">{company.revenue}</span>
        </div>
        <div className="flex flex-col border-r border-[#d8d6d0] pr-4">
          <span className="text-[#7c7a75] text-[10px] uppercase mb-1">YoY Growth</span>
          <span className="text-[#1a1a19] font-bold">{company.yoyGrowth}</span>
        </div>
        <div className="flex flex-col">
          <span className="text-[#7c7a75] text-[10px] uppercase mb-1">Cash Position</span>
          <span className="text-[#1a1a19] font-bold">{company.cashPosition}</span>
        </div>
      </div>

      {/* Due Diligence Summary */}
      <div className="text-sm text-[#1a1a19] leading-relaxed border-t border-[#d8d6d0] pt-4">
        {company.summary}
      </div>

      {/* Grounded Clickable Citations */}
      <div className="flex flex-col gap-2 border-t border-[#d8d6d0] pt-4">
        <span className="text-[10px] font-mono tracking-wider text-[#7c7a75] uppercase">
          SharePoint Online Grounding Sources (sockcop site)
        </span>
        <div className="flex flex-col gap-1">
          {company.sources.map((source, idx) => (
            <a 
              key={idx} 
              href={source.url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="text-xs font-mono text-[#1a1a19] hover:text-[#7c7a75] underline decoration-1 underline-offset-4 py-0.5 truncate block"
            >
              📎 {source.title}
            </a>
          ))}
        </div>
      </div>
    </div>
  );
}
