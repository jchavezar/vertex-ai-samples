import React from 'react';
import { Sliders, RotateCcw, TrendingUp, Ship, DollarSign, Percent, ShieldAlert } from 'lucide-react';
import { ShockParameters } from '../types';

interface ShockSimulatorSlidersProps {
  params: ShockParameters;
  onChange: (params: ShockParameters) => void;
  latencyMs: number;
}

export const ShockSimulatorSliders: React.FC<ShockSimulatorSlidersProps> = ({
  params,
  onChange,
  latencyMs,
}) => {
  const updateField = (field: keyof ShockParameters, val: number) => {
    onChange({
      ...params,
      [field]: val,
    });
  };

  const applyPreset = (preset: 'banxico_rate' | 'puertos_bloqueo' | 'dolar_stress' | 'baseline') => {
    switch (preset) {
      case 'banxico_rate':
        onChange({
          interest_rate_bps: 150,
          inflation_rate_pct: 4.8,
          supply_chain_stress_index: 35,
          tariff_volatility_pct: 12,
          supplier_default_risk_pct: 2.5,
        });
        break;
      case 'puertos_bloqueo':
        onChange({
          interest_rate_bps: 50,
          inflation_rate_pct: 5.5,
          supply_chain_stress_index: 85,
          tariff_volatility_pct: 20,
          supplier_default_risk_pct: 4.5,
        });
        break;
      case 'dolar_stress':
        onChange({
          interest_rate_bps: 175,
          inflation_rate_pct: 7.2,
          supply_chain_stress_index: 70,
          tariff_volatility_pct: 25,
          supplier_default_risk_pct: 6.0,
        });
        break;
      case 'baseline':
        onChange({
          interest_rate_bps: 0,
          inflation_rate_pct: 3.2,
          supply_chain_stress_index: 20,
          tariff_volatility_pct: 5.0,
          supplier_default_risk_pct: 1.0,
        });
        break;
    }
  };

  return (
    <div className="cyber-glass rounded-2xl p-5 border border-cyan-500/30">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4 pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Sliders className="h-4 w-4 text-cyan-400" />
          <h3 className="font-extrabold text-sm text-slate-100 uppercase tracking-wide font-sans">
            SIMULADOR DE CHOQUE & ESTRÉS MACROECONÓMICO (MÉXICO)
          </h3>
        </div>
        <div className="flex items-center gap-2 text-xs font-mono">
          <span className="text-slate-400">Latencia de Cálculo:</span>
          <span className="px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-800/60 font-bold">
            {latencyMs > 0 ? `${latencyMs.toFixed(1)} ms` : '< 5 ms'}
          </span>
        </div>
      </div>

      {/* Preset Buttons in Spanish tailored for Mexico C-Suite */}
      <div className="flex flex-wrap items-center gap-2 mb-5">
        <span className="text-[11px] font-mono font-semibold text-slate-400 mr-1">
          Escenarios Macroeconómicos Rápidos:
        </span>
        <button
          type="button"
          onClick={() => applyPreset('banxico_rate')}
          className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-amber-300 border border-amber-500/30 font-medium transition-all cursor-pointer"
        >
          ⚡ Alza Banxico +150 bps (TIIE)
        </button>
        <button
          type="button"
          onClick={() => applyPreset('puertos_bloqueo')}
          className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-rose-300 border border-rose-500/30 font-medium transition-all cursor-pointer"
        >
          🚢 Bloqueo Portuario (Veracruz & Manzanillo)
        </button>
        <button
          type="button"
          onClick={() => applyPreset('dolar_stress')}
          className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-purple-300 border border-purple-500/30 font-medium transition-all cursor-pointer"
        >
          💵 Dólar USD/MXN a $21.20 (Retail & Devaluación)
        </button>
        <button
          type="button"
          onClick={() => applyPreset('baseline')}
          className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 border border-slate-600 font-medium flex items-center gap-1 transition-all cursor-pointer"
        >
          <RotateCcw className="h-3 w-3 text-slate-400" />
          Restablecer Línea Base
        </button>
      </div>

      {/* Sliders Grid in Spanish */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 text-xs font-mono">
        {/* Slider 1: Movimiento Tasa Banxico (TIIE) */}
        <div className="bg-slate-900/70 p-3.5 rounded-xl border border-slate-800 space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-slate-300 font-medium flex items-center gap-1.5 font-sans">
              <TrendingUp className="h-3.5 w-3.5 text-cyan-400" />
              Movimiento Tasa Banxico (TIIE):
            </span>
            <span className="text-cyan-300 font-bold bg-cyan-950/80 px-2 py-0.5 rounded border border-cyan-800">
              {params.interest_rate_bps > 0 ? `+${params.interest_rate_bps}` : params.interest_rate_bps} bps
            </span>
          </div>
          <input
            type="range"
            min="-100"
            max="300"
            step="25"
            value={params.interest_rate_bps}
            onChange={(e) => updateField('interest_rate_bps', Number(e.target.value))}
            className="w-full accent-cyan-400 cursor-pointer h-1.5 bg-slate-700 rounded-lg"
          />
          <div className="flex justify-between text-[10px] text-slate-500">
            <span>-100 bps (Recorte Banxico)</span>
            <span>+300 bps (Estrés Monetario)</span>
          </div>
        </div>

        {/* Slider 2: Estrés de Cadena Portuaria & Fletes */}
        <div className="bg-slate-900/70 p-3.5 rounded-xl border border-slate-800 space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-slate-300 font-medium flex items-center gap-1.5 font-sans">
              <Ship className="h-3.5 w-3.5 text-rose-400" />
              Estrés Portuario & Fletes (CICE):
            </span>
            <span className="text-rose-300 font-bold bg-rose-950/80 px-2 py-0.5 rounded border border-rose-800">
              {params.supply_chain_stress_index.toFixed(0)} / 100
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="100"
            step="5"
            value={params.supply_chain_stress_index}
            onChange={(e) => updateField('supply_chain_stress_index', Number(e.target.value))}
            className="w-full accent-rose-500 cursor-pointer h-1.5 bg-slate-700 rounded-lg"
          />
          <div className="flex justify-between text-[10px] text-slate-500">
            <span>0 (Flujo Portuario Normal)</span>
            <span>100 (Bloqueo Total Veracruz/Mzn)</span>
          </div>
        </div>

        {/* Slider 3: Inflación INPC México */}
        <div className="bg-slate-900/70 p-3.5 rounded-xl border border-slate-800 space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-slate-300 font-medium flex items-center gap-1.5 font-sans">
              <Percent className="h-3.5 w-3.5 text-yellow-400" />
              Inflación Proyectada INPC:
            </span>
            <span className="text-yellow-300 font-bold bg-yellow-950/80 px-2 py-0.5 rounded border border-yellow-800">
              {params.inflation_rate_pct.toFixed(1)}%
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="10"
            step="0.5"
            value={params.inflation_rate_pct}
            onChange={(e) => updateField('inflation_rate_pct', Number(e.target.value))}
            className="w-full accent-yellow-400 cursor-pointer h-1.5 bg-slate-700 rounded-lg"
          />
          <div className="flex justify-between text-[10px] text-slate-500">
            <span>0.0% (Meta 3.0% Banxico)</span>
            <span>10.0% (Pico Inflacionario)</span>
          </div>
        </div>

        {/* Slider 4: Volatilidad Cambiaria USD/MXN */}
        <div className="bg-slate-900/70 p-3.5 rounded-xl border border-slate-800 space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-slate-300 font-medium flex items-center gap-1.5 font-sans">
              <DollarSign className="h-3.5 w-3.5 text-purple-400" />
              Volatilidad Cambiaria USD/MXN:
            </span>
            <span className="text-purple-300 font-bold bg-purple-950/80 px-2 py-0.5 rounded border border-purple-800">
              {params.tariff_volatility_pct.toFixed(1)}%
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="30"
            step="1"
            value={params.tariff_volatility_pct}
            onChange={(e) => updateField('tariff_volatility_pct', Number(e.target.value))}
            className="w-full accent-purple-400 cursor-pointer h-1.5 bg-slate-700 rounded-lg"
          />
          <div className="flex justify-between text-[10px] text-slate-500">
            <span>0% (Tipo de Cambio Estable)</span>
            <span>30% (Depreciación Dólar $22.00)</span>
          </div>
        </div>

        {/* Slider 5: Riesgo de Crédito y Proveedores */}
        <div className="bg-slate-900/70 p-3.5 rounded-xl border border-slate-800 space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-slate-300 font-medium flex items-center gap-1.5 font-sans">
              <ShieldAlert className="h-3.5 w-3.5 text-indigo-400" />
              Riesgo de Cartera y Proveedores:
            </span>
            <span className="text-indigo-300 font-bold bg-indigo-950/80 px-2 py-0.5 rounded border border-indigo-800">
              {params.supplier_default_risk_pct.toFixed(1)}%
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="15"
            step="0.5"
            value={params.supplier_default_risk_pct}
            onChange={(e) => updateField('supplier_default_risk_pct', Number(e.target.value))}
            className="w-full accent-indigo-400 cursor-pointer h-1.5 bg-slate-700 rounded-lg"
          />
          <div className="flex justify-between text-[10px] text-slate-500">
            <span>0.0% (Solvencia Plena)</span>
            <span>15.0% (Contagio Cartera Vencida)</span>
          </div>
        </div>
      </div>
    </div>
  );
};
