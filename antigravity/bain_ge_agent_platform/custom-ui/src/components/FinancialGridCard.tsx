import { useDashboardStore, CompanyMetrics } from '../store/dashboardStore';

export function FinancialGridCard({ company }: { company: CompanyMetrics }) {
  const { activeCompany, setActiveCompany } = useDashboardStore();
  const isActive = activeCompany?.ticker === company.ticker;

  return (
    <div 
      onClick={() => setActiveCompany(company)}
      className={`group flex flex-col gap-4 border-b border-slate-200 pb-6 cursor-pointer rounded-2xl p-5 transition-all ${isActive ? 'bg-slate-100' : 'hover:bg-slate-50'}`}
    >
      <div className="relative h-36 w-full overflow-hidden border border-slate-800 rounded-xl bg-slate-900 flex flex-col justify-end p-5 shadow-sm">
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-900/80 to-transparent z-10" />
        <div className="absolute top-3 left-3 z-20 bg-slate-800 text-slate-200 px-2 py-0.5 text-[10px] font-semibold tracking-wider uppercase rounded-md border border-slate-700">
          {company.sector}
        </div>
        <div className="absolute top-3 right-3 z-20 bg-white text-slate-900 px-2 py-0.5 text-[10px] font-mono font-bold tracking-wider uppercase rounded-md">
          {company.ticker}
        </div>
        <div className="z-20 relative text-white">
          <span className="text-[11px] font-mono tracking-wider text-slate-400 uppercase block mb-0.5">
            CFO: {company.cfo}
          </span>
          <h3 className="text-xl font-bold tracking-tight">
            {company.name}
          </h3>
        </div>
      </div>
      
      <div className="grid grid-cols-3 gap-3 border-t border-slate-200/80 pt-3 font-mono text-xs">
        <div className="flex flex-col border-r border-slate-200 pr-3">
          <span className="text-slate-400 text-[10px] uppercase mb-0.5">Revenue</span>
          <span className="text-slate-900 font-bold">{company.revenue}</span>
        </div>
        <div className="flex flex-col border-r border-slate-200 pr-3">
          <span className="text-slate-400 text-[10px] uppercase mb-0.5">YoY Growth</span>
          <span className="text-slate-900 font-bold">{company.yoyGrowth}</span>
        </div>
        <div className="flex flex-col">
          <span className="text-slate-400 text-[10px] uppercase mb-0.5">Cash Position</span>
          <span className="text-slate-900 font-bold">{company.cashPosition}</span>
        </div>
      </div>

      <div className="text-xs text-slate-600 leading-relaxed border-t border-slate-200/80 pt-3">
        {company.summary}
      </div>

      <div className="flex flex-col gap-1.5 border-t border-slate-200/80 pt-3">
        <span className="text-[10px] font-mono tracking-wider text-slate-400 uppercase">
          SharePoint Grounding Sources (sockcop site)
        </span>
        <div className="flex flex-col gap-1">
          {company.sources.map((source, idx) => (
            <a 
              key={idx} 
              href={source.url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="text-xs font-mono text-slate-800 hover:text-cyan-600 underline py-0.5 truncate block"
            >
              📎 {source.title}
            </a>
          ))}
        </div>
      </div>
    </div>
  );
}
