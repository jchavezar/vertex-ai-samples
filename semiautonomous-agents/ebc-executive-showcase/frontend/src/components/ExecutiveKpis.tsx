import React from 'react';
import { TrendingUp, DollarSign, ShieldCheck, Cpu } from 'lucide-react';

export const ExecutiveKpis: React.FC = () => {
  return (
    <section className="w-full max-w-[1720px] mx-auto px-6 pt-4 pb-2">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* KPI 1 */}
        <div className="bg-white/90 backdrop-blur-md p-4 rounded-2xl border border-slate-200/80 shadow-xs border-l-4 border-l-blue-600 transition-all hover:shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Impacto Económico Proyectado
            </span>
            <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center">
              <DollarSign className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight">
              $4.8M
            </span>
            <span className="text-xs font-semibold text-slate-500">USD</span>
          </div>
          <p className="mt-1 text-xs text-slate-600 font-medium flex items-center gap-1">
            <span className="text-emerald-600 font-bold flex items-center">
              <TrendingUp className="w-3.5 h-3.5 inline mr-0.5" /> +28%
            </span>
            vs. analítica tradicional
          </p>
        </div>

        {/* KPI 2 */}
        <div className="bg-white/90 backdrop-blur-md p-4 rounded-2xl border border-slate-200/80 shadow-xs border-l-4 border-l-emerald-600 transition-all hover:shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Retorno de Inversión (ROI)
            </span>
            <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-3xl sm:text-4xl font-black text-emerald-700 tracking-tight">
              +340%
            </span>
            <span className="text-xs font-semibold text-slate-500">24 meses</span>
          </div>
          <p className="mt-1 text-xs text-slate-600 font-medium truncate">
            Payback proyectado en <span className="font-bold text-slate-900">7.2 meses</span>
          </p>
        </div>

        {/* KPI 3 */}
        <div className="bg-white/90 backdrop-blur-md p-4 rounded-2xl border border-slate-200/80 shadow-xs border-l-4 border-l-indigo-600 transition-all hover:shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Gobernanza & Soberanía
            </span>
            <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-700 flex items-center justify-center">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight">
              99.8%
            </span>
            <span className="text-xs font-semibold text-slate-500">Compliance</span>
          </div>
          <p className="mt-1 text-xs text-slate-600 font-medium truncate">
            Protocolo <span className="font-bold text-slate-900">Zero-Leak</span> en Google Cloud
          </p>
        </div>

        {/* KPI 4 */}
        <div className="bg-white/90 backdrop-blur-md p-4 rounded-2xl border border-slate-200/80 shadow-xs border-l-4 border-l-fuchsia-600 transition-all hover:shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Orquestación de Agentes
            </span>
            <div className="w-8 h-8 rounded-lg bg-fuchsia-50 text-fuchsia-700 flex items-center justify-center">
              <Cpu className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-3xl sm:text-4xl font-black text-fuchsia-700 tracking-tight">
              4 Lanes
            </span>
            <span className="text-xs font-semibold text-slate-500">Paralelos</span>
          </div>
          <p className="mt-1 text-xs text-slate-600 font-medium truncate">
            Estrategia, Creatividad, Finanzas y Auditoría
          </p>
        </div>

      </div>
    </section>
  );
};
