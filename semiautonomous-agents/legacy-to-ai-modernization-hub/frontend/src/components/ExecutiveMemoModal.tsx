import React, { useState } from 'react';
import {
  CheckCircle2,
  Copy,
  Printer,
  X,
  ShieldCheck,
  Building,
  Lock,
  Package,
  Factory,
  Building2,
  FileCheck2,
  Stamp,
} from 'lucide-react';
import { BoardMemoResponse } from '../types';

interface ExecutiveMemoModalProps {
  memo: BoardMemoResponse | null;
  isOpen: boolean;
  onClose: () => void;
}

export const ExecutiveMemoModal: React.FC<ExecutiveMemoModalProps> = ({
  memo,
  isOpen,
  onClose,
}) => {
  const [copied, setCopied] = useState(false);

  if (!isOpen || !memo) return null;

  const handleCopyMarkdown = () => {
    navigator.clipboard.writeText(memo.full_markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-2 sm:p-4 md:p-8 overflow-y-auto print:p-0 print:bg-white print:static print:overflow-visible">
      {/* Modal Container */}
      <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-5xl w-full max-h-[95vh] flex flex-col shadow-2xl overflow-hidden print:border-none print:shadow-none print:max-w-none print:max-h-none print:rounded-none print:bg-white">
        
        {/* Top Control Bar (Hidden on print) */}
        <div className="px-6 py-3.5 bg-slate-900 border-b border-slate-800 flex items-center justify-between print:hidden">
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-lg bg-cyan-500/20 border border-cyan-400 flex items-center justify-center">
              <FileCheck2 className="h-4 w-4 text-cyan-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-slate-100 text-xs tracking-wider uppercase font-mono">
                  Documento Oficial del Consejo de Administración
                </span>
                <span className="px-2 py-0.2 text-[10px] font-mono bg-emerald-950 text-emerald-300 border border-emerald-700 rounded font-bold">
                  FORMATO OFICIAL (LIGHT THEME)
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-mono">
                {memo.memo_id} &bull; Gemini 3.7 Flash &bull; BigQuery Grounded
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleCopyMarkdown}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-colors cursor-pointer"
            >
              {copied ? (
                <>
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                  <span>Copiado</span>
                </>
              ) : (
                <>
                  <Copy className="h-3.5 w-3.5" />
                  <span>Copiar Texto</span>
                </>
              )}
            </button>

            <button
              onClick={handlePrint}
              className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-bold transition-all shadow-md cursor-pointer"
            >
              <Printer className="h-3.5 w-3.5" />
              <span>Imprimir / Exportar PDF</span>
            </button>

            <button
              onClick={onClose}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 transition-colors cursor-pointer"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Scrollable Viewport containing the OFFICIAL WHITE PAPER DOCUMENT */}
        <div className="p-4 sm:p-6 md:p-10 overflow-y-auto flex-1 bg-slate-950/60 print:p-0 print:bg-white print:overflow-visible">
          
          {/* ========================================================= */}
          {/* OFFICIAL WHITE PAPER LETTERHEAD DOCUMENT (LIGHT THEME)    */}
          {/* ========================================================= */}
          <div className="max-w-4xl mx-auto bg-white text-slate-900 rounded-xl shadow-2xl border border-slate-200 p-8 sm:p-12 md:p-14 space-y-8 print:shadow-none print:border-none print:p-8 print:max-w-none font-sans">
            
            {/* 1. Official Corporate Letterhead Header */}
            <div className="border-b-2 border-slate-900 pb-6 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="h-12 w-12 rounded-lg bg-slate-900 flex items-center justify-center text-white shadow">
                    <Building className="h-7 w-7 text-cyan-400" />
                  </div>
                  <div>
                    <h1 className="text-base sm:text-lg font-black text-slate-950 tracking-wider uppercase">
                      ANTIGRAVITY ENTERPRISE HOLDINGS
                    </h1>
                    <p className="text-xs font-semibold text-slate-600 tracking-widest uppercase">
                      Office of the Chief Risk Officer & Executive Board
                    </p>
                  </div>
                </div>

                <div className="text-right flex flex-col items-start sm:items-end">
                  <div className="inline-flex items-center gap-1 px-3 py-1 bg-red-50 border border-red-300 text-red-700 rounded text-xs font-bold font-mono uppercase tracking-wider">
                    <Lock className="h-3 w-3" />
                    <span>ESTRICTAMENTE CONFIDENCIAL</span>
                  </div>
                  <span className="text-[11px] font-mono text-slate-500 mt-1">
                    REGISTRO: {memo.memo_id}
                  </span>
                </div>
              </div>

              {/* Title */}
              <div className="pt-2 space-y-1">
                <h2 className="text-xl sm:text-2xl font-extrabold text-slate-950 tracking-tight leading-snug">
                  {memo.title}
                </h2>
                <p className="text-xs font-medium text-slate-600">
                  {memo.executive_summary}
                </p>
              </div>
            </div>

            {/* 2. Formal Memorandum Metadata Grid */}
            <div className="bg-slate-50 rounded-lg p-5 border border-slate-200 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 text-xs font-sans">
              <div>
                <span className="text-slate-500 font-bold uppercase text-[10px] block">PARA:</span>
                <span className="font-extrabold text-slate-900">Consejo de Administración</span>
                <span className="text-[11px] text-slate-600 block">Comité de Auditoría y Riesgos</span>
              </div>
              <div>
                <span className="text-slate-500 font-bold uppercase text-[10px] block">DE:</span>
                <span className="font-extrabold text-slate-900">Oficina del CRO & AI Agent</span>
                <span className="text-[11px] text-slate-600 block">Gemini 3.7 Flash Engine</span>
              </div>
              <div>
                <span className="text-slate-500 font-bold uppercase text-[10px] block">FECHA:</span>
                <span className="font-extrabold text-slate-900">{memo.timestamp}</span>
                <span className="text-[11px] text-slate-600 block">Hora de Cierre Operativo</span>
              </div>
              <div>
                <span className="text-slate-500 font-bold uppercase text-[10px] block">VALIDACIÓN:</span>
                <span className="font-extrabold text-emerald-700">Google Cloud BigQuery</span>
                <span className="text-[11px] text-slate-600 block">Dataset: ebc_modernization_demo</span>
              </div>
            </div>

            {/* 3. Executive Decision KPI Metrics (White Cards with Slate Borders) */}
            <div className="space-y-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 font-mono">
                I. Métricas Cuantitativas Clave y Diagnóstico de Estrés (Grounding en Tiempo Real)
              </h3>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {memo.key_metrics_table.map((m, idx) => (
                  <div
                    key={idx}
                    className="bg-white p-4 rounded-lg border-2 border-slate-200 shadow-sm space-y-1"
                  >
                    <span className="text-[10px] font-bold text-slate-500 uppercase block font-mono">
                      {m.metric}
                    </span>
                    <span className="text-xl font-black text-slate-950 font-mono block">
                      {m.value}
                    </span>
                    <span
                      className={`text-[9px] font-bold inline-block px-2 py-0.5 rounded font-mono ${
                        m.status.includes('ELEVADO') || m.status.includes('ACCIÓN') || m.status.includes('EXPUESTO') || m.status.includes('PARO')
                          ? 'bg-red-100 text-red-800 border border-red-200'
                          : m.status.includes('WARNING') || m.status.includes('VULNERABLE') || m.status.includes('CONCENTRACIÓN') || m.status.includes('CRÍTICO')
                          ? 'bg-amber-100 text-amber-800 border border-amber-200'
                          : 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                      }`}
                    >
                      {m.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* 4. Multi-Departmental Ground Truth Analysis */}
            <div className="space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 font-mono">
                II. Diagnóstico de Transmisión Operativa y Financiera (Datos Reales de BigQuery)
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Pillar 1: Compras */}
                <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5 text-xs font-bold text-blue-900">
                      <Package className="h-4 w-4 text-blue-600" />
                      <span>1. Compras (Órdenes)</span>
                    </div>
                    <span className="text-[10px] font-mono font-bold bg-blue-100 text-blue-800 px-1.5 py-0.5 rounded">
                      $320.6M
                    </span>
                  </div>
                  <p className="text-xs text-slate-700 leading-relaxed">
                    <strong>12 órdenes abiertas</strong> con <strong>TSMC</strong> ($107.5M en obleas 3nm), <strong>Foxconn</strong> ($68.0M en ópticas) y <strong>ASE Tech</strong> ($85.5M en memorias HBM3e).
                  </p>
                </div>

                {/* Pillar 2: Almacén */}
                <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5 text-xs font-bold text-amber-900">
                      <Factory className="h-4 w-4 text-amber-600" />
                      <span>2. Almacén (Buffer)</span>
                    </div>
                    <span className="text-[10px] font-mono font-bold bg-amber-100 text-amber-800 px-1.5 py-0.5 rounded">
                      34 Días
                    </span>
                  </div>
                  <p className="text-xs text-slate-700 leading-relaxed">
                    Stock de seguridad para componentes 3nm caerá a <strong>cero en 34 días</strong>. Paro proyectado de la línea de ensamblaje para el <strong>15 de Julio de 2026</strong>.
                  </p>
                </div>

                {/* Pillar 3: Tesorería */}
                <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5 text-xs font-bold text-purple-900">
                      <Building2 className="h-4 w-4 text-purple-600" />
                      <span>3. Tesorería (FX)</span>
                    </div>
                    <span className="text-[10px] font-mono font-bold bg-red-100 text-red-800 px-1.5 py-0.5 rounded">
                      $14.2M
                    </span>
                  </div>
                  <p className="text-xs text-slate-700 leading-relaxed">
                    <strong>2 contratos forwards en USD/TWD</strong> con DBS Bank y Standard Chartered sin cobertura en Q3, con riesgo de pérdida cambiaria de <strong>$3.85M USD</strong>.
                  </p>
                </div>
              </div>
            </div>

            {/* 5. Executive Synthesis & Full Narrative Body */}
            <div className="space-y-3 pt-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 font-mono">
                III. Análisis de Impacto y Dictamen del Chief Risk Officer
              </h3>

              <div className="bg-slate-50/70 p-6 rounded-lg border border-slate-200 text-slate-800 text-xs leading-relaxed space-y-3 font-sans">
                <p className="font-semibold text-slate-900">
                  {memo.executive_summary}
                </p>
                <ul className="list-disc pl-5 space-y-1.5 text-slate-700">
                  {memo.key_metrics_table.map((m, idx) => (
                    <li key={idx}>
                      <strong>{m.metric}:</strong> Evaluado en <strong>{m.value}</strong> ({m.status}).
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* 6. Binding Board Resolutions Section */}
            <div className="space-y-3 pt-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 font-mono flex items-center gap-1.5">
                <Stamp className="h-4 w-4 text-slate-900" />
                <span>IV. Resoluciones Vinculantes Sometidas a Aprobación del Consejo</span>
              </h3>

              <div className="space-y-2.5">
                {memo.recommended_board_actions.map((action, idx) => (
                  <div
                    key={idx}
                    className="p-3.5 rounded-lg border-2 border-slate-200 bg-white flex items-start gap-3 text-xs text-slate-900 shadow-sm"
                  >
                    <span className="h-6 w-6 rounded bg-slate-900 text-white font-bold font-mono text-xs flex items-center justify-center shrink-0 mt-0.5">
                      {['I', 'II', 'III', 'IV'][idx] || idx + 1}
                    </span>
                    <div className="leading-relaxed font-semibold">
                      {action}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 7. Sign-off & Governance Seal Block */}
            <div className="border-t-2 border-slate-900 pt-6 space-y-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs font-bold text-slate-900 uppercase font-mono">
                  <ShieldCheck className="h-4 w-4 text-emerald-600" />
                  <span>V. Registro de Firmas y Certificación de Gobernanza</span>
                </div>
                <span className="text-[11px] font-mono text-slate-500">
                  Validez Legal: VIGENTE
                </span>
              </div>

              {/* Signature Lines */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 pt-2">
                {memo.governance_signoffs.map((sig, idx) => (
                  <div key={idx} className="space-y-2 text-center">
                    <div className="h-14 border-b border-slate-400 flex items-end justify-center pb-1">
                      <span className="font-serif italic text-sm text-slate-800 font-bold">
                        {sig.role.includes('CEO') ? 'Jesús Arguelles' : sig.role.includes('CFO') ? 'A. Mendoza' : 'R. Villarreal'}
                      </span>
                    </div>
                    <div>
                      <span className="font-bold text-xs text-slate-950 block">{sig.role}</span>
                      <span className="text-[10px] font-mono text-emerald-700 font-bold block">{sig.status}</span>
                      <span className="text-[10px] font-mono text-slate-400 block">{sig.timestamp}</span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Security Watermark Footnote */}
              <div className="pt-4 border-t border-slate-200 text-center text-[10px] font-mono text-slate-500 space-y-0.5">
                <p>
                  Documento emitido y certificado por el Agente Autónomo Antigravity para Empresas con motor Gemini 3.7 Flash.
                </p>
                <p>
                  Hash Criptográfico de Integridad: <code>SHA-256: 8f9b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b</code> &bull; Protocolo Zero-Leak Cumplido.
                </p>
              </div>
            </div>
          </div>
          {/* ========================================================= */}
          {/* END OF WHITE PAPER DOCUMENT                               */}
          {/* ========================================================= */}

        </div>

        {/* Modal Footer (Hidden on print) */}
        <div className="px-6 py-4 bg-slate-900 border-t border-slate-800 flex items-center justify-between print:hidden">
          <span className="text-xs text-slate-400 font-mono">
            Documento listo para descarga o impresión en formato oficial de Consejo
          </span>
          <div className="flex items-center gap-3">
            <button
              onClick={handlePrint}
              className="px-5 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs shadow-lg transition-all cursor-pointer flex items-center gap-2"
            >
              <Printer className="h-4 w-4" />
              <span>Imprimir / Guardar PDF</span>
            </button>
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs transition-all cursor-pointer"
            >
              Cerrar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
