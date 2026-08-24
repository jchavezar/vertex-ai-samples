import React, { useState } from 'react';
import {
  Database,
  FileSpreadsheet,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Sparkles,
  Zap,
  RefreshCw,
} from 'lucide-react';

interface MultiDepartmentQueryChainProps {
  onTriggerRefactor: () => void;
}

export const MultiDepartmentQueryChain: React.FC<MultiDepartmentQueryChainProps> = ({
  onTriggerRefactor,
}) => {
  const [step1State, setStep1State] = useState<'idle' | 'running' | 'done'>('idle');
  const [step2State, setStep2State] = useState<'idle' | 'running' | 'done'>('idle');
  const [step3State, setStep3State] = useState<'idle' | 'running' | 'done'>('idle');
  const [step4State, setStep4State] = useState<'idle' | 'running' | 'done'>('idle');

  const [activeTab, setActiveTab] = useState<1 | 2 | 3 | 4>(1);

  const runStep1 = () => {
    setStep1State('running');
    setTimeout(() => {
      setStep1State('done');
      setActiveTab(2);
    }, 1400);
  };

  const runStep2 = () => {
    setStep2State('running');
    setTimeout(() => {
      setStep2State('done');
      setActiveTab(3);
    }, 1100);
  };

  const runStep3 = () => {
    setStep3State('running');
    setTimeout(() => {
      setStep3State('done');
      setActiveTab(4);
    }, 950);
  };

  const runStep4 = () => {
    setStep4State('running');
    setTimeout(() => {
      setStep4State('done');
    }, 1500);
  };

  const runAllSteps = () => {
    setStep1State('running');
    setTimeout(() => {
      setStep1State('done');
      setStep2State('running');
      setTimeout(() => {
        setStep2State('done');
        setStep3State('running');
        setTimeout(() => {
          setStep3State('done');
          setStep4State('running');
          setTimeout(() => {
            setStep4State('done');
            setActiveTab(4);
          }, 1500);
        }, 950);
      }, 1100);
    }, 1400);
  };

  const resetAll = () => {
    setStep1State('idle');
    setStep2State('idle');
    setStep3State('idle');
    setStep4State('idle');
    setActiveTab(1);
  };

  return (
    <div className="bg-[#f0f3f6] border-2 border-[#7f8c8d] rounded-xl p-4 mb-5 shadow-lg font-sans text-slate-800">
      {/* Top Scenario Banner */}
      <div className="bg-[#2c3e50] text-white p-3.5 rounded-lg flex flex-col md:flex-row items-start md:items-center justify-between gap-3 shadow-md">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-amber-500/20 border border-amber-400/50 rounded-lg text-amber-300">
            <AlertTriangle className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h4 className="font-bold text-xs uppercase tracking-wider text-amber-300">
                La Realidad Tradicional: Cadena Manual de Consultas SQL y Cruce en Excel (3 Días)
              </h4>
              <span className="bg-red-900/80 text-red-200 text-[10px] font-mono px-2 py-0.5 rounded border border-red-700 font-bold">
                ENFOQUE LEGACY
              </span>
            </div>
            <p className="text-[11px] text-slate-200 font-mono mt-0.5">
              Pregunta de Negocio: <strong>&ldquo;Si nuestro proveedor principal en Taiwán sufre un bloqueo de 90 días, ¿cuál es nuestro impacto en flujo de caja, qué contratos FX están expuestos y qué crédito debemos activar?&rdquo;</strong>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <button
            type="button"
            onClick={runAllSteps}
            className="bg-amber-600 hover:bg-amber-700 text-white text-[11px] font-bold px-3 py-1.5 rounded-lg shadow flex items-center gap-1.5 transition-all cursor-pointer"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            <span>Simular Ciclo Completo (3 Días)</span>
          </button>
          <button
            type="button"
            onClick={resetAll}
            className="bg-slate-700 hover:bg-slate-600 text-slate-200 text-[11px] font-semibold px-2.5 py-1.5 rounded-lg transition-all cursor-pointer"
          >
            Reiniciar
          </button>
        </div>
      </div>

      {/* 4-Step Chain Tabs with Business Questions */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2 my-3">
        {/* Step 1 Tab */}
        <button
          type="button"
          onClick={() => setActiveTab(1)}
          className={`p-3 rounded-lg border text-left transition-all cursor-pointer ${
            activeTab === 1
              ? 'bg-white border-blue-600 shadow-md ring-2 ring-blue-500/40'
              : 'bg-[#e2e8f0] border-slate-300 hover:bg-slate-100'
          }`}
        >
          <div className="flex items-center justify-between text-[11px] font-bold">
            <span className="text-slate-800 font-bold">1. Compras (Oracle RAC)</span>
            {step1State === 'done' && <CheckCircle2 className="h-4 w-4 text-emerald-600" />}
            {step1State === 'running' && <RefreshCw className="h-4 w-4 text-amber-600 animate-spin" />}
          </div>
          <p className="text-[10px] text-slate-600 mt-1 font-medium line-clamp-1">
            ¿Cuáles son las órdenes abiertas con Taiwán?
          </p>
        </button>

        {/* Step 2 Tab */}
        <button
          type="button"
          onClick={() => setActiveTab(2)}
          className={`p-3 rounded-lg border text-left transition-all cursor-pointer ${
            activeTab === 2
              ? 'bg-white border-blue-600 shadow-md ring-2 ring-blue-500/40'
              : 'bg-[#e2e8f0] border-slate-300 hover:bg-slate-100'
          }`}
        >
          <div className="flex items-center justify-between text-[11px] font-bold">
            <span className="text-slate-800 font-bold">2. Almacén (SAP HANA)</span>
            {step2State === 'done' && <CheckCircle2 className="h-4 w-4 text-emerald-600" />}
            {step2State === 'running' && <RefreshCw className="h-4 w-4 text-amber-600 animate-spin" />}
          </div>
          <p className="text-[10px] text-slate-600 mt-1 font-medium line-clamp-1">
            ¿Cuántos días de inventario de seguridad quedan?
          </p>
        </button>

        {/* Step 3 Tab */}
        <button
          type="button"
          onClick={() => setActiveTab(3)}
          className={`p-3 rounded-lg border text-left transition-all cursor-pointer ${
            activeTab === 3
              ? 'bg-white border-blue-600 shadow-md ring-2 ring-blue-500/40'
              : 'bg-[#e2e8f0] border-slate-300 hover:bg-slate-100'
          }`}
        >
          <div className="flex items-center justify-between text-[11px] font-bold">
            <span className="text-slate-800 font-bold">3. Tesorería (SQL Server)</span>
            {step3State === 'done' && <CheckCircle2 className="h-4 w-4 text-emerald-600" />}
            {step3State === 'running' && <RefreshCw className="h-4 w-4 text-amber-600 animate-spin" />}
          </div>
          <p className="text-[10px] text-slate-600 mt-1 font-medium line-clamp-1">
            ¿Qué contratos de cobertura FX están expuestos?
          </p>
        </button>

        {/* Step 4 Tab */}
        <button
          type="button"
          onClick={() => setActiveTab(4)}
          className={`p-3 rounded-lg border text-left transition-all cursor-pointer ${
            activeTab === 4
              ? 'bg-white border-amber-600 shadow-md ring-2 ring-amber-500/40'
              : 'bg-[#e2e8f0] border-slate-300 hover:bg-slate-100'
          }`}
        >
          <div className="flex items-center justify-between text-[11px] font-bold">
            <span className="text-slate-900 font-bold">4. Cruce en Excel</span>
            {step4State === 'done' && <CheckCircle2 className="h-4 w-4 text-emerald-600" />}
            {step4State === 'running' && <RefreshCw className="h-4 w-4 text-amber-600 animate-spin" />}
          </div>
          <p className="text-[10px] text-amber-700 font-bold mt-1">
            BUSCARV y PPT (Demora 3 Días)
          </p>
        </button>
      </div>

      {/* Active Step Panel */}
      <div className="bg-white border border-[#bdc3c7] rounded-lg p-4 shadow-sm">
        {activeTab === 1 && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Database className="h-4 w-4 text-blue-700" />
                <span className="font-bold text-xs text-slate-800 uppercase">
                  Paso 1: Consulta a Compras // Base de Datos Oracle RAC (erp-prod-db04.corp)
                </span>
              </div>
              <span className="text-[11px] font-mono text-slate-500 font-bold">Pregunta: &ldquo;Órdenes abiertas con Taiwán&rdquo;</span>
            </div>

            <div className="bg-[#1e272e] text-[#d2dae2] p-3 rounded font-mono text-[11px] leading-relaxed border border-slate-700 overflow-x-auto">
              <code>
                SELECT po.po_id, v.vendor_name, po.part_code, SUM(po.notional_usd) AS total_committed<br />
                FROM po_headers po JOIN vendor_master v ON po.vendor_id = v.vendor_id<br />
                WHERE v.country_code = 'TW' AND po.status = 'OPEN'<br />
                GROUP BY po.po_id, v.vendor_name, po.part_code;
              </code>
            </div>

            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pt-1">
              <button
                type="button"
                disabled={step1State === 'running'}
                onClick={runStep1}
                className="bg-blue-700 hover:bg-blue-800 text-white font-bold text-xs px-4 py-2 rounded-lg shadow flex items-center gap-2 transition-all disabled:opacity-50 cursor-pointer"
              >
                {step1State === 'running' ? (
                  <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <Database className="h-3.5 w-3.5" />
                )}
                <span>{step1State === 'running' ? 'Ejecutando Consulta en Oracle (1,400ms)...' : 'Ejecutar Consulta 1 (Oracle)'}</span>
              </button>

              {step1State === 'done' && (
                <div className="bg-emerald-50 border border-emerald-300 text-emerald-800 text-xs px-3 py-1.5 rounded-lg flex items-center gap-2 font-mono">
                  <FileSpreadsheet className="h-4 w-4 text-emerald-600" />
                  <span>✓ Resultado Generado: <strong>PO_Commitments_APAC.csv</strong> (1,240 registros &bull; $320M comprometidos en 12 órdenes abiertas)</span>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 2 && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Database className="h-4 w-4 text-indigo-700" />
                <span className="font-bold text-xs text-slate-800 uppercase">
                  Paso 2: Consulta a Almacén // Base de Datos SAP HANA (sap-hana-wh02.corp)
                </span>
              </div>
              <span className="text-[11px] font-mono text-slate-500 font-bold">Pregunta: &ldquo;Stock de seguridad y consumo&rdquo;</span>
            </div>

            <div className="bg-[#1e272e] text-[#d2dae2] p-3 rounded font-mono text-[11px] leading-relaxed border border-slate-700 overflow-x-auto">
              <code>
                SELECT part_sku, safety_stock_days, daily_burn_rate, line_stoppage_risk<br />
                FROM inventory_positions<br />
                WHERE supplier_id IN ('V-8821', 'V-9942') AND safety_stock_days &lt; 90;
              </code>
            </div>

            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pt-1">
              <button
                type="button"
                disabled={step2State === 'running'}
                onClick={runStep2}
                className="bg-indigo-700 hover:bg-indigo-800 text-white font-bold text-xs px-4 py-2 rounded-lg shadow flex items-center gap-2 transition-all disabled:opacity-50 cursor-pointer"
              >
                {step2State === 'running' ? (
                  <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <Database className="h-3.5 w-3.5" />
                )}
                <span>{step2State === 'running' ? 'Ejecutando Consulta en SAP HANA (1,100ms)...' : 'Ejecutar Consulta 2 (SAP HANA)'}</span>
              </button>

              {step2State === 'done' && (
                <div className="bg-emerald-50 border border-emerald-300 text-emerald-800 text-xs px-3 py-1.5 rounded-lg flex items-center gap-2 font-mono">
                  <FileSpreadsheet className="h-4 w-4 text-emerald-600" />
                  <span>✓ Resultado Generado: <strong>Warehouse_Runout_Risk.csv</strong> (840 registros &bull; Alerta: Solo 42 días de stock antes de paro de planta)</span>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 3 && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Database className="h-4 w-4 text-purple-700" />
                <span className="font-bold text-xs text-slate-800 uppercase">
                  Paso 3: Consulta a Tesorería // SQL Server (treasury-mssql-01.corp)
                </span>
              </div>
              <span className="text-[11px] font-mono text-slate-500 font-bold">Pregunta: &ldquo;Coberturas cambiarias y forwards expuestos&rdquo;</span>
            </div>

            <div className="bg-[#1e272e] text-[#d2dae2] p-3 rounded font-mono text-[11px] leading-relaxed border border-slate-700 overflow-x-auto">
              <code>
                SELECT deal_id, ccy_pair, notional_amount, maturity_date, hedge_status<br />
                FROM fx_forward_contracts<br />
                WHERE maturity_date BETWEEN '2026-06-01' AND '2026-09-01' AND hedge_status = 'UNHEDGED';
              </code>
            </div>

            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pt-1">
              <button
                type="button"
                disabled={step3State === 'running'}
                onClick={runStep3}
                className="bg-purple-700 hover:bg-purple-800 text-white font-bold text-xs px-4 py-2 rounded-lg shadow flex items-center gap-2 transition-all disabled:opacity-50 cursor-pointer"
              >
                {step3State === 'running' ? (
                  <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <Database className="h-3.5 w-3.5" />
                )}
                <span>{step3State === 'running' ? 'Ejecutando Consulta en SQL Server (950ms)...' : 'Ejecutar Consulta 3 (SQL Server)'}</span>
              </button>

              {step3State === 'done' && (
                <div className="bg-emerald-50 border border-emerald-300 text-emerald-800 text-xs px-3 py-1.5 rounded-lg flex items-center gap-2 font-mono">
                  <FileSpreadsheet className="h-4 w-4 text-emerald-600" />
                  <span>✓ Resultado Generado: <strong>Treasury_FX_Exposure.csv</strong> (310 contratos &bull; 2 forwards sin cobertura por $14.2M expuestos)</span>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 4 && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileSpreadsheet className="h-4 w-4 text-amber-700" />
                <span className="font-bold text-xs text-slate-800 uppercase">
                  Paso 4: Consolidación Manual en Excel (BUSCARV, Tablas Dinámicas y Correos)
                </span>
              </div>
              <span className="text-[11px] font-mono text-amber-800 font-bold bg-amber-100 px-2 py-0.5 rounded border border-amber-300">
                ⏳ Demora del Proceso Humano: 2.5 a 3 Días Hábiles
              </span>
            </div>

            <div className="bg-amber-50/80 border border-amber-300 rounded-lg p-3 text-xs text-slate-700 space-y-2">
              <div className="flex items-center gap-2 text-amber-900 font-bold">
                <AlertTriangle className="h-4 w-4 text-amber-600" />
                <span>Puntos de fricción del proceso tradicional:</span>
              </div>
              <ul className="list-disc list-inside space-y-1 text-[11px] font-mono text-slate-700">
                <li>El analista debe cruzar manualmente los 3 CSVs con fórmulas de <code>=BUSCARV(A2, PO_Commitments!A:A, Inventory!C:C)</code>.</li>
                <li>Los códigos de SKU no coinciden exactamente, requiriendo 4 hilos de correos entre Compras y Tesorería.</li>
                <li>La presentación para el Director General y el Consejo se debe armar a mano en PowerPoint con gráficas estáticas.</li>
              </ul>
            </div>

            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pt-1">
              <button
                type="button"
                disabled={step4State === 'running'}
                onClick={runStep4}
                className="bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs px-4 py-2 rounded-lg shadow flex items-center gap-2 transition-all disabled:opacity-50 cursor-pointer"
              >
                {step4State === 'running' ? (
                  <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <FileSpreadsheet className="h-3.5 w-3.5" />
                )}
                <span>{step4State === 'running' ? 'Conciliando Spreadsheets en Excel...' : '📊 Consolidar en Excel (Tarda 3 Días)'}</span>
              </button>

              {step4State === 'done' && (
                <div className="bg-emerald-100 border border-emerald-400 text-emerald-950 text-xs px-3.5 py-2 rounded-lg font-mono font-bold space-y-1 shadow-sm">
                  <div className="text-emerald-900 font-bold">✓ Resultado Consolidado (Listo después de 3 días):</div>
                  <div className="text-[11px] text-emerald-800">
                    Riesgo Total de Portafolio: <strong>$105.6M</strong> &bull; Impacto en EBITDA: <strong>-$100.8M</strong> &bull; Faltante de Cobertura: <strong>$14.2M</strong>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* The Antigravity Modernization Superpower CTA Banner */}
      <div className="mt-4 bg-gradient-to-r from-[#0f172a] via-[#1e1b4b] to-[#0f172a] text-white p-4 rounded-xl border border-cyan-500/60 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-xl">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Zap className="h-4 w-4 text-cyan-400 animate-pulse" />
            <span className="text-xs font-bold text-cyan-300 uppercase tracking-wider">
              La Transformación Agéntica con IA // Cero Fricción Humana
            </span>
          </div>
          <p className="text-xs text-slate-200 font-medium">
            En lugar de 4 consultas manuales y 3 días de Excel, <strong>Antigravity ejecuta todas las herramientas en 35ms</strong> y entrega el Canvas Interactivo 2026 en automático con una sola pregunta.
          </p>
        </div>

        <button
          type="button"
          onClick={onTriggerRefactor}
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-extrabold text-xs shadow-lg shadow-cyan-500/30 flex items-center gap-2 shrink-0 transition-all cursor-pointer"
        >
          <Sparkles className="h-4 w-4 text-slate-950" />
          <span>Resolver Todo en Automático (3.5s)</span>
          <ArrowRight className="h-4 w-4 text-slate-950" />
        </button>
      </div>
    </div>
  );
};
