import React, { useState } from 'react';
import {
  Layers,
  Truck,
  Factory,
  Building2,
  ShieldCheck,
  Database,
  Sliders,
  Sparkles,
  Code2,
} from 'lucide-react';
import { GroundedTableData, ShockImpactData } from '../../types';

interface ConsolidadoMultiEmpresaViewProps {
  tableData?: GroundedTableData;
  shockImpact: ShockImpactData;
}

export const ConsolidadoMultiEmpresaView: React.FC<ConsolidadoMultiEmpresaViewProps> = ({
  tableData,
  shockImpact,
}) => {
  const [activeTab, setActiveTab] = useState<'matrix' | 'table' | 'sql'>('matrix');
  const [stressFactor, setStressFactor] = useState(100);
  const [mitigationsActive, setMitigationsActive] = useState({
    ferromex: true,
    queretaro: true,
    forward: true,
  });

  // Dynamic calculations based on stress slider
  const multiplier = stressFactor / 100;
  const ciceTeus = Math.round(1420 * multiplier);
  const ciceCostM = (4.85 * multiplier).toFixed(2);
  const bufferDays = Math.max(7, Math.round(21 / multiplier));
  const retailExposureM = (85.0 * multiplier).toFixed(1);
  const totalVarM = (shockImpact.value_at_risk_99_m * multiplier).toFixed(2);
  const totalEbitdaM = (shockImpact.ebitda_impact_m * multiplier).toFixed(2);

  // Total savings with all mitigations active
  const totalMitigationSavingsM = (
    (mitigationsActive.ferromex ? 1.46 : 0) +
    (mitigationsActive.queretaro ? 2.10 : 0) +
    (mitigationsActive.forward ? 3.60 : 0)
  ).toFixed(2);

  return (
    <div className="space-y-6 animate-zoom-entrance">
      {/* Top Header Banner & View Switcher */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-gradient-to-r from-cyan-950/90 via-slate-900 to-blue-950/90 p-5 rounded-2xl border-2 border-cyan-500/50 shadow-xl">
        <div className="flex items-center gap-3.5">
          <div className="h-12 w-12 rounded-xl bg-cyan-500/20 border-2 border-cyan-400 flex items-center justify-center shadow-lg shadow-cyan-500/30">
            <Layers className="h-6 w-6 text-cyan-300 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base sm:text-lg font-black text-slate-100 font-sans tracking-wide">
                DIAGNÓSTICO INTEGRAL MULTI-EMPRESA EBC (3 PILARES CONSOLIDADOS)
              </h3>
              <span className="text-[10px] font-mono px-2.5 py-0.5 rounded-full bg-cyan-900 text-cyan-200 border border-cyan-600 font-bold">
                BIGQUERY GROUND TRUTH
              </span>
            </div>
            <p className="text-xs sm:text-sm text-slate-300">
              Correlación de impacto sistémico entre Logística (CICE), Manufactura (Silanes/Gloria) y Finanzas (Boxito/HR Ratings).
            </p>
          </div>
        </div>

        {/* BigQuery Inspector & View Switcher Buttons */}
        <div className="flex items-center gap-1.5 bg-slate-950/90 p-1.5 rounded-xl border border-slate-800 self-stretch sm:self-auto justify-center">
          <button
            type="button"
            onClick={() => setActiveTab('matrix')}
            className={`px-3.5 py-2 rounded-lg font-mono text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
              activeTab === 'matrix'
                ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Sparkles className="h-3.5 w-3.5" />
            Matriz Visual Cross-Empresa
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('table')}
            className={`px-3.5 py-2 rounded-lg font-mono text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
              activeTab === 'table'
                ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Database className="h-3.5 w-3.5" />
            Tabla BigQuery ({tableData?.total_rows || 285})
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('sql')}
            className={`px-3.5 py-2 rounded-lg font-mono text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
              activeTab === 'sql'
                ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Code2 className="h-3.5 w-3.5" />
            SQL BigQuery (28ms)
          </button>
        </div>
      </div>

      {/* 1. TAB: INTERACTIVE MULTI-EMPRESA DYNAMIC MATRIX */}
      {activeTab === 'matrix' && (
        <div className="bg-slate-950/90 rounded-3xl p-6 sm:p-8 border-2 border-cyan-500/40 shadow-2xl space-y-6 relative overflow-hidden">
          {/* Section Heading with Real-Time Total Metrics */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between border-b border-slate-800 pb-4 gap-3">
            <span className="text-xs sm:text-sm font-mono font-bold text-cyan-300 uppercase tracking-wider flex items-center gap-2">
              <ShieldCheck className="h-4 w-4 text-cyan-400" />
              Mapeo de Transmisión de Choque en las 16 Empresas del Auditorio
            </span>
            <div className="flex flex-wrap items-center gap-3 text-xs font-mono">
              <span className="text-slate-400">
                VaR Total: <strong className="text-rose-400 font-black">${totalVarM}M USD</strong>
              </span>
              <span className="text-slate-400">
                Arrastre EBITDA: <strong className="text-rose-400 font-black">-${totalEbitdaM}M USD</strong>
              </span>
              <span className="text-slate-400">
                Ahorro Mitigaciones: <strong className="text-emerald-400 font-black">+${totalMitigationSavingsM}M USD</strong>
              </span>
            </div>
          </div>

          {/* 3 Bespoke Enterprise Pillars Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {/* Pillar 1: Logística y Puertos (Grupo CICE & Senda) */}
            <div className="bg-slate-900/90 p-5 rounded-2xl border-2 border-blue-500/60 flex flex-col justify-between space-y-4 shadow-xl relative group hover:border-blue-400 transition-all">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-sm text-blue-300 flex items-center gap-2">
                    <Truck className="h-4 w-4 text-blue-400" />
                    1. Logística & Puertos
                  </span>
                  <span className="text-[10px] font-mono bg-blue-950 text-blue-300 px-2.5 py-0.5 rounded-full border border-blue-700 font-black">
                    CICE & SENDA
                  </span>
                </div>
                <div className="space-y-1">
                  <div className="text-2xl font-mono font-black text-slate-100">
                    {ciceTeus} TEUs <span className="text-xs font-normal text-slate-400 font-sans">Varados</span>
                  </div>
                  <div className="text-xs text-rose-400 font-mono font-bold">
                    Sobrecosto Fletes: ${ciceCostM}M USD
                  </div>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Terminales de <strong>Grupo CICE Veracruz</strong> y <strong>Manzanillo</strong> con saturación de muelles y retraso aduanal de +18 días.
                </p>
              </div>

              {/* Action Trigger in Pillar 1 */}
              <div className="pt-3 border-t border-slate-800 space-y-2">
                <button
                  type="button"
                  onClick={() => setMitigationsActive(prev => ({ ...prev, ferromex: !prev.ferromex }))}
                  className={`w-full py-2.5 px-3 rounded-xl font-mono text-[11px] font-black flex items-center justify-between transition-all cursor-pointer ${
                    mitigationsActive.ferromex
                      ? 'bg-blue-600/90 text-white border border-blue-400 shadow-md shadow-blue-600/30'
                      : 'bg-slate-800 text-slate-400 border border-slate-700'
                  }`}
                >
                  <span>Ferromex Intermodal a MTY</span>
                  <span className="text-[10px] bg-black/40 px-2 py-0.5 rounded">
                    {mitigationsActive.ferromex ? '+$1.46M Activo' : 'Inactivo'}
                  </span>
                </button>
              </div>
            </div>

            {/* Pillar 2: Manufactura y Farma (Laboratorios Silanes & Cremería Gloria) */}
            <div className="bg-slate-900/90 p-5 rounded-2xl border-2 border-amber-500/60 flex flex-col justify-between space-y-4 shadow-xl relative group hover:border-amber-400 transition-all">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-sm text-amber-300 flex items-center gap-2">
                    <Factory className="h-4 w-4 text-amber-400" />
                    2. Manufactura & Farma
                  </span>
                  <span className="text-[10px] font-mono bg-amber-950 text-amber-300 px-2.5 py-0.5 rounded-full border border-amber-700 font-black">
                    SILANES & GLORIA
                  </span>
                </div>
                <div className="space-y-1">
                  <div className="text-2xl font-mono font-black text-amber-400">
                    {bufferDays} Días <span className="text-xs font-normal text-slate-400 font-sans">Buffer Restante</span>
                  </div>
                  <div className="text-xs text-amber-300 font-mono font-bold">
                    Paro de Envasado: 16 de Julio 2026
                  </div>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Insumos críticos de <strong>APIs Farma (Silanes Toluca)</strong> y <strong>Grasa Butírica (Cremería Gloria GDL)</strong> en nivel crítico.
                </p>
              </div>

              {/* Action Trigger in Pillar 2 */}
              <div className="pt-3 border-t border-slate-800 space-y-2">
                <button
                  type="button"
                  onClick={() => setMitigationsActive(prev => ({ ...prev, queretaro: !prev.queretaro }))}
                  className={`w-full py-2.5 px-3 rounded-xl font-mono text-[11px] font-black flex items-center justify-between transition-all cursor-pointer ${
                    mitigationsActive.queretaro
                      ? 'bg-amber-600/90 text-slate-950 border border-amber-400 shadow-md shadow-amber-600/30'
                      : 'bg-slate-800 text-slate-400 border border-slate-700'
                  }`}
                >
                  <span>Stock Regulador Querétaro</span>
                  <span className="text-[10px] bg-black/40 px-2 py-0.5 rounded text-white">
                    {mitigationsActive.queretaro ? '+14d Activo' : 'Inactivo'}
                  </span>
                </button>
              </div>
            </div>

            {/* Pillar 3: Retail, Margen & Calificación (Boxito, Macropay & HR Ratings) */}
            <div className="bg-slate-900/90 p-5 rounded-2xl border-2 border-purple-500/60 flex flex-col justify-between space-y-4 shadow-xl relative group hover:border-purple-400 transition-all">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-sm text-purple-300 flex items-center gap-2">
                    <Building2 className="h-4 w-4 text-purple-400" />
                    3. Retail, FX & Solvencia
                  </span>
                  <span className="text-[10px] font-mono bg-purple-950 text-purple-300 px-2.5 py-0.5 rounded-full border border-purple-700 font-black">
                    BOXITO & HR RATINGS
                  </span>
                </div>
                <div className="space-y-1">
                  <div className="text-2xl font-mono font-black text-slate-100">
                    ${retailExposureM}M <span className="text-xs font-normal text-slate-400 font-sans">Compras Expuestas</span>
                  </div>
                  <div className="text-xs text-purple-300 font-mono font-bold">
                    Rating HR Ratings: HR AA+ (Solvente)
                  </div>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Importaciones de <strong>Boxito</strong> ($28.5M) y <strong>Macropay</strong> ($36.2M) expuestas al tipo de cambio USD/MXN a $20.80.
                </p>
              </div>

              {/* Action Trigger in Pillar 3 */}
              <div className="pt-3 border-t border-slate-800 space-y-2">
                <button
                  type="button"
                  onClick={() => setMitigationsActive(prev => ({ ...prev, forward: !prev.forward }))}
                  className={`w-full py-2.5 px-3 rounded-xl font-mono text-[11px] font-black flex items-center justify-between transition-all cursor-pointer ${
                    mitigationsActive.forward
                      ? 'bg-purple-600/90 text-white border border-purple-400 shadow-md shadow-purple-600/30'
                      : 'bg-slate-800 text-slate-400 border border-slate-700'
                  }`}
                >
                  <span>Forward USD/MXN @ $19.40</span>
                  <span className="text-[10px] bg-black/40 px-2 py-0.5 rounded">
                    {mitigationsActive.forward ? '+$3.60M Activo' : 'Inactivo'}
                  </span>
                </button>
              </div>
            </div>
          </div>

          {/* Interactive Multi-Stress Simulation Slider */}
          <div className="bg-slate-900/90 rounded-2xl p-5 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between text-xs sm:text-sm font-mono font-bold text-slate-200">
              <span className="flex items-center gap-2">
                <Sliders className="h-4 w-4 text-cyan-400" />
                Simulador de Severidad del Choque Multivariado (Bloqueo Portuario + Dólar a $21.00):
              </span>
              <span className="text-cyan-300 bg-cyan-950 px-3 py-1 rounded-lg border border-cyan-800 font-black">
                {stressFactor}% Severidad
              </span>
            </div>

            <input
              type="range"
              min={50}
              max={150}
              step={5}
              value={stressFactor}
              onChange={(e) => setStressFactor(Number(e.target.value))}
              className="w-full accent-cyan-400 h-2 bg-slate-800 rounded-lg cursor-pointer"
            />

            <div className="flex items-center justify-between text-[11px] font-mono text-slate-400">
              <span>50% (Choque Moderado &bull; Dólar $19.80)</span>
              <span>100% (Choque Base EBC &bull; Dólar $20.80 &bull; 1,420 TEUs)</span>
              <span>150% (Escenario Extremo &bull; Dólar $21.80 &bull; 2,130 TEUs)</span>
            </div>
          </div>
        </div>
      )}

      {/* 2. TAB: RAW BIGQUERY GROUNDED DATA TABLE */}
      {activeTab === 'table' && tableData && (
        <div className="bg-slate-950/90 rounded-2xl border-2 border-cyan-500/40 overflow-hidden shadow-2xl animate-fade-in">
          <div className="bg-gradient-to-r from-slate-900 to-cyan-950/60 px-5 py-3.5 flex items-center justify-between border-b border-slate-800">
            <div className="flex items-center gap-2.5">
              <Database className="h-4 w-4 text-cyan-400" />
              <span className="font-bold text-sm text-cyan-300 font-mono uppercase">
                {tableData.title}
              </span>
            </div>
            <span className="text-xs font-mono bg-cyan-950 text-cyan-300 px-3 py-1 rounded-lg border border-cyan-700 font-bold">
              {tableData.total_rows} Registros Consolidados en BigQuery
            </span>
          </div>

          <div className="overflow-x-auto max-h-80 overflow-y-auto">
            <table className="w-full text-left border-collapse whitespace-nowrap text-xs sm:text-sm font-mono">
              <thead>
                <tr className="bg-slate-900 text-slate-300 border-b border-slate-800 text-xs font-bold uppercase">
                  {tableData.headers.map((h: string, i: number) => (
                    <th key={i} className="p-3.5 border-r border-slate-800/80">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {tableData.rows.map((row: any, i: number) => (
                  <tr key={i} className={i % 2 === 0 ? 'bg-slate-950/60' : 'bg-slate-900/60'}>
                    {Object.values(row).map((val: any, cIdx: number) => (
                      <td key={cIdx} className="p-3.5 text-slate-200 border-r border-slate-800/60">
                        {typeof val === 'number' ? `$${val.toLocaleString()}` : String(val)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 3. TAB: RAW SQL QUERY & BIGQUERY EXECUTION TRACE */}
      {activeTab === 'sql' && (
        <div className="bg-slate-950/90 rounded-2xl border-2 border-cyan-500/40 p-6 shadow-2xl space-y-4 font-mono text-xs animate-fade-in">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <span className="text-cyan-300 font-bold flex items-center gap-2">
              <Code2 className="h-4 w-4" />
              Consulta SQL BigQuery Ejecutada en Vivo (Grounded Pipeline)
            </span>
            <div className="flex items-center gap-2">
              <span className="bg-emerald-950 text-emerald-300 px-2.5 py-0.5 rounded border border-emerald-700">
                Latencia: 28 ms
              </span>
              <span className="bg-cyan-950 text-cyan-300 px-2.5 py-0.5 rounded border border-cyan-700">
                Bytes Procesados: 1.42 MB
              </span>
            </div>
          </div>

          <pre className="bg-slate-900 p-4 rounded-xl text-cyan-200 overflow-x-auto border border-slate-800 leading-relaxed text-xs">
{`-- Consulta Consolidada Multi-Empresa EBC en Google Cloud BigQuery
WITH logistica_cice AS (
  SELECT 
    'Logística y Puertos' AS dominio,
    'Grupo CICE, Senda, Promologistics' AS empresas,
    SUM(teus_varados) AS volumen_teus,
    SUM(sobrecosto_usd) AS sobrecosto_usd
  FROM \`vtxdemos.ebc_modernization_demo.logistica_portuaria_live\`
),
farma_alimentos AS (
  SELECT 
    'Manufactura y Farma' AS dominio,
    'Cremería Americana, Lab. Silanes' AS empresas,
    MIN(dias_buffer_restante) AS buffer_dias,
    DATE_ADD(CURRENT_DATE(), INTERVAL MIN(dias_buffer_restante) DAY) AS fecha_paro_estimada
  FROM \`vtxdemos.ebc_modernization_demo.manufactura_inventarios_live\`
),
retail_solvencia AS (
  SELECT 
    'Retail y Finanzas' AS dominio,
    'Boxito, Macropay, HR Ratings' AS empresas,
    SUM(compras_importadas_usd) AS exposicion_usd,
    AVG(var_99_10d_m) AS var_portafolio_m
  FROM \`vtxdemos.ebc_modernization_demo.retail_fx_coberturas_live\`
)
SELECT * FROM logistica_cice
CROSS JOIN farma_alimentos
CROSS JOIN retail_solvencia;`}
          </pre>

          <div className="flex items-center justify-between text-slate-400 text-[11px] pt-2 border-t border-slate-800">
            <span>Motor: BigQuery SQL v2.0 (Vector Grounding Enabled)</span>
            <span>Partición: Ingestión Diaria (Streaming Buffer)</span>
          </div>
        </div>
      )}
    </div>
  );
};
