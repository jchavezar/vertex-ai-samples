import React, { useState } from 'react';
import { ExecutiveDeliverable } from '../types';
import {
  ShieldCheck,
  TrendingUp,
  Sparkles,
  Target,
  CheckCircle2,
  Copy,
  Check,
  FileCheck
} from 'lucide-react';

interface ExecutiveSynthesisCardProps {
  deliverable: ExecutiveDeliverable;
}

export const ExecutiveSynthesisCard: React.FC<ExecutiveSynthesisCardProps> = ({ deliverable }) => {
  const [copied, setCopied] = useState<boolean>(false);

  const handleCopy = () => {
    const fullText = `
${deliverable.title}
MANDATO: ${deliverable.mandate}
DICTAMEN DEL CONSEJO: ${deliverable.board_verdict}
PRESUPUESTO APROBADO: ${deliverable.approved_budget}
PAYBACK ESTIMADO: ${deliverable.expected_payback}

1. ESTRATEGIA: ${deliverable.strategy_summary}
2. CREATIVIDAD & EXPERIENCIA: ${deliverable.creative_vision}
3. FINANZAS & ROI: ${deliverable.financial_roi_summary}
4. AUDITORÍA & GOBERNANZA: ${deliverable.audit_governance_summary}

ACCIONES INMEDIATAS:
${deliverable.action_items.map((it, i) => `${i + 1}. ${it}`).join('\n')}
    `.trim();

    navigator.clipboard.writeText(fullText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="glass-panel-elevated p-8 rounded-3xl border-2 border-emerald-200 bg-gradient-to-br from-white via-emerald-50/20 to-slate-50/60 shadow-xl space-y-6">
      
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider bg-emerald-600 text-white flex items-center gap-1.5 shadow-sm">
              <FileCheck className="w-4 h-4" /> Dossier Ejecutivo C-Suite
            </span>
            <span className="text-xs font-bold text-slate-500">Resolución Oficial de la Junta</span>
          </div>
          <h3 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
            {deliverable.title}
          </h3>
          <p className="text-sm font-semibold text-slate-600">
            Mandato: "{deliverable.mandate}"
          </p>
        </div>

        {/* Board Verdict Banner */}
        <div className="flex items-center gap-2">
          <div className="p-3 px-5 rounded-2xl bg-emerald-700 text-white font-black text-sm uppercase tracking-wider shadow-md flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5" />
            {deliverable.board_verdict}
          </div>
          <button
            onClick={handleCopy}
            className="p-3 rounded-xl bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 shadow-sm"
            title="Copiar Dossier Completo"
          >
            {copied ? <Check className="w-5 h-5 text-emerald-600" /> : <Copy className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Big Number Metrics for 100" Display */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="p-5 rounded-2xl bg-emerald-50 border border-emerald-200">
          <span className="text-xs font-bold uppercase tracking-wider text-emerald-800 block">
            Presupuesto Asignado Aprobado
          </span>
          <span className="text-4xl sm:text-5xl font-black text-emerald-800 tracking-tight">
            {deliverable.approved_budget}
          </span>
          <span className="text-xs text-emerald-700 font-medium block mt-1">
            Financiación en fases con hitos de rendimiento
          </span>
        </div>

        <div className="p-5 rounded-2xl bg-blue-50 border border-blue-200">
          <span className="text-xs font-bold uppercase tracking-wider text-blue-800 block">
            Periodo de Recuperación (Payback)
          </span>
          <span className="text-4xl sm:text-5xl font-black text-blue-800 tracking-tight">
            {deliverable.expected_payback}
          </span>
          <span className="text-xs text-blue-700 font-medium block mt-1">
            Punto de equilibrio financiero proyectado
          </span>
        </div>
      </div>

      {/* 4 Specialized Synthesis Pillars */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        
        {/* Strategy */}
        <div className="p-5 rounded-2xl bg-indigo-50/70 border border-indigo-200 space-y-2">
          <div className="flex items-center gap-2 text-indigo-700 font-bold text-sm uppercase">
            <Target className="w-4 h-4" />
            <span>1. Dictamen Estratégico</span>
          </div>
          <p className="text-slate-800 text-sm sm:text-base font-semibold leading-relaxed">
            {deliverable.strategy_summary}
          </p>
        </div>

        {/* Creative */}
        <div className="p-5 rounded-2xl bg-fuchsia-50/70 border border-fuchsia-200 space-y-2">
          <div className="flex items-center gap-2 text-fuchsia-700 font-bold text-sm uppercase">
            <Sparkles className="w-4 h-4" />
            <span>2. Narrativa & Experiencia</span>
          </div>
          <p className="text-slate-800 text-sm sm:text-base font-semibold leading-relaxed">
            {deliverable.creative_vision}
          </p>
        </div>

        {/* Financial */}
        <div className="p-5 rounded-2xl bg-emerald-50/70 border border-emerald-200 space-y-2">
          <div className="flex items-center gap-2 text-emerald-700 font-bold text-sm uppercase">
            <TrendingUp className="w-4 h-4" />
            <span>3. Evaluación Financiera & ROI</span>
          </div>
          <p className="text-slate-800 text-sm sm:text-base font-semibold leading-relaxed">
            {deliverable.financial_roi_summary}
          </p>
        </div>

        {/* Audit & Governance */}
        <div className="p-5 rounded-2xl bg-blue-50/70 border border-blue-200 space-y-2">
          <div className="flex items-center gap-2 text-blue-700 font-bold text-sm uppercase">
            <ShieldCheck className="w-4 h-4" />
            <span>4. Auditoría & Gobernanza</span>
          </div>
          <p className="text-slate-800 text-sm sm:text-base font-semibold leading-relaxed">
            {deliverable.audit_governance_summary}
          </p>
        </div>

      </div>

      {/* Action Items List */}
      <div className="p-6 rounded-2xl bg-slate-50 border border-slate-200 space-y-3">
        <h4 className="text-xs font-black uppercase tracking-wider text-slate-600 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          Plan de Acción Inmediato para la Junta Directiva
        </h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {deliverable.action_items.map((item, idx) => (
            <div key={idx} className="p-3 rounded-xl bg-white border border-slate-200 flex items-start gap-2.5 shadow-sm">
              <span className="w-6 h-6 rounded-full bg-emerald-100 text-emerald-800 font-bold text-xs flex items-center justify-center shrink-0 mt-0.5">
                {idx + 1}
              </span>
              <p className="text-xs sm:text-sm font-bold text-slate-800">
                {item}
              </p>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};
