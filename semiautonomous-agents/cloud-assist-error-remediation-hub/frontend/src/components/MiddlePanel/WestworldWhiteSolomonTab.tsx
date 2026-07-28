import React, { useState } from 'react';
import {
  Eye,
  Activity,
  AlertTriangle,
  Zap,
  Sparkles,
  Search,
  Maximize2,
  Terminal,
  Cpu,
  Layers,
  CheckCircle2,
  X,
  ExternalLink,
  ShieldAlert
} from 'lucide-react';

interface AnomalyCallout {
  date: string;
  divergenceType: string;
  location: string;
  incidentName: string;
  service: string;
  status: string;
  riskScore: number;
}

export const WestworldWhiteSolomonTab: React.FC = () => {
  const [activeCallout, setActiveCallout] = useState<AnomalyCallout | null>(null);
  const [divergenceActive, setDivergenceActive] = useState<boolean>(false);
  const [solomonStream, setSolomonStream] = useState<string[]>([
    "04.17.39 SYSTEM INITIATED UNDISCLOSED LOCATION 'SOLOMON' BUILD 0.06",
    "10.09.25 DIVERGENCE : VTXDEMOS CLOUD RUN INCIDENT DETECTED",
    "RE-ROUTING CANONICAL TRAFFIC VIA GEMINI 3.5 FLASH LITE RECOVERY HARNESS",
    "SYSTEM EQUILIBRIUM STABILIZED AT 98.6% PROBABILITY INDEX"
  ]);

  const callouts: AnomalyCallout[] = [
    {
      date: "04.17.39",
      divergenceType: "DIVERGENCE : FINTECH LEDGER",
      location: "SECRET MANAGER",
      incidentName: "KEYERROR: 'JWT_SECRET_KEY' IN /API/AUTH/TOKEN",
      service: "cyberpunk-ledger-dashboard",
      status: "HEALED",
      riskScore: 0.76
    },
    {
      date: "10.09.25",
      divergenceType: "DIVERGENCE : STOREFRONT",
      location: "US-CENTRAL1",
      incidentName: "ZERODIVISIONERROR IN /API/CART/CHECKOUT",
      service: "envato-vibe-storefront",
      status: "REMEDIATED",
      riskScore: 0.88
    },
    {
      date: "08.12.44",
      divergenceType: "DIVERGENCE : MEDICAL PORTAL",
      location: "CONTAINER HEAP",
      incidentName: "MEMORYERROR: OOMKILLED 512MB LIMIT EXCEEDED",
      service: "healthcare-patient-portal",
      status: "STABILIZED",
      riskScore: 0.94
    },
    {
      date: "12.01.02",
      divergenceType: "DIVERGENCE : FLEET TRACKER",
      location: "POSTGRES POOL",
      incidentName: "CONNECTIONREFUSEDERROR IN CLOUD SQL POOL",
      service: "realtime-logistics-tracker",
      status: "ACTIVE",
      riskScore: 0.65
    }
  ];

  const triggerDivergence = () => {
    setDivergenceActive(!divergenceActive);
    const newLog = `[${new Date().toLocaleTimeString()}] DIVERGENCE EVENT INJECTED: REHOBOAM WAVEFORM AMPLITUDE SPIKE DETECTED`;
    setSolomonStream((prev) => [newLog, ...prev]);
  };

  return (
    <div className="min-h-screen bg-[#fafafa] text-[#0f172a] p-6 space-y-8 font-sans border border-slate-200 rounded-3xl shadow-2xl">
      {/* WESTWORLD WHITE REHOBOAM HEADER */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-900/10 pb-6">
        <div className="space-y-1">
          <div className="text-[11px] font-mono tracking-[0.25em] text-slate-500 uppercase font-extrabold">
            04.17.39 SYSTEM INITIATED • 'SOLOMON' BUILD 0.06
          </div>
          <h1 className="text-2xl font-black tracking-tight text-slate-950 uppercase font-mono flex items-center gap-3">
            <span>SOLOMON WHITE EDITION</span>
            <span className="text-xs font-mono font-bold px-3 py-1 bg-slate-900 text-white rounded-full">
              PROBABILISTIC SYSTEMIC DIVERGENCE ENGINE
            </span>
          </h1>
          <p className="text-xs text-slate-600 font-mono">
            Omniscient Telemetry Monitor • Pure Alabaster & Ink Particle Matrix
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={triggerDivergence}
            className={`px-5 py-2.5 rounded-full font-mono text-xs font-bold uppercase tracking-wider border transition-all cursor-pointer shadow-md ${
              divergenceActive
                ? 'bg-red-600 text-white border-red-700 animate-pulse'
                : 'bg-slate-950 hover:bg-slate-800 text-white border-slate-900'
            }`}
          >
            {divergenceActive ? '🔴 DIVERGENCE EVENT ACTIVE' : '⚡ TRIGGER ANOMALY DIVERGENCE'}
          </button>

          <div className="px-4 py-2 bg-slate-100 border border-slate-300 rounded-full font-mono text-xs text-slate-800 font-bold">
            EQUILIBRIUM: <span className={divergenceActive ? 'text-red-600 font-black' : 'text-slate-900'}>
              {divergenceActive ? '12.4% (CRITICAL DIVERGENCE)' : '98.6% (STABLE)'}
            </span>
          </div>
        </div>
      </div>

      {/* IMAGE 2 HOMAGE: UNCLUTTERED REHOBOAM BLACK INK ANOMALY CIRCLE WITH NON-OVERLAPPING CORNER CALLOUTS */}
      <div className="bg-white rounded-3xl border border-slate-300 p-8 shadow-xl relative overflow-hidden space-y-6">
        <div className="flex justify-between items-center border-b border-slate-200 pb-3">
          <span className="text-xs font-mono font-bold tracking-widest text-slate-900 uppercase">
            REHOBOAM INK PARTICLE ANOMALY CIRCLE • SYSTEMIC DIVERGENCE RADAR
          </span>
          <span className="text-[10px] font-mono text-slate-500">PROJECT VTXDEMOS</span>
        </div>

        {/* 2D Interactive SVG Canvas with 520px Height for Zero Overlapping */}
        <div className="relative w-full h-[520px] flex items-center justify-center bg-[#fdfdfd] rounded-2xl border border-slate-200 overflow-hidden">
          {/* Hairline Callout Leader Lines pointing to Central Ring */}
          <svg className="w-full h-full absolute inset-0 pointer-events-none z-10">
            {/* Top-Left Line */}
            <line x1="26%" y1="20%" x2="42%" y2="40%" stroke="#0f172a" strokeWidth="1.5" strokeDasharray="4 4" />
            <circle cx="42%" cy="40%" r="4" fill="#0f172a" />

            {/* Top-Right Line */}
            <line x1="74%" y1="20%" x2="58%" y2="40%" stroke="#0f172a" strokeWidth="1.5" strokeDasharray="4 4" />
            <circle cx="58%" cy="40%" r="4" fill="#0f172a" />

            {/* Bottom-Left Line */}
            <line x1="26%" y1="80%" x2="42%" y2="60%" stroke="#0f172a" strokeWidth="1.5" strokeDasharray="4 4" />
            <circle cx="42%" cy="60%" r="4" fill="#0f172a" />

            {/* Bottom-Right Line */}
            <line x1="74%" y1="80%" x2="58%" y2="60%" stroke="#0f172a" strokeWidth="1.5" strokeDasharray="4 4" />
            <circle cx="58%" cy="60%" r="4" fill="#0f172a" />
          </svg>

          {/* Central Concentric Ink Ring (Clean & Unobstructed) */}
          <div className="relative w-64 h-64 rounded-full border-4 border-slate-900 flex items-center justify-center shadow-[0_0_50px_rgba(0,0,0,0.12)] z-0 bg-white">
            <div className={`absolute inset-0 rounded-full border-2 border-dashed ${divergenceActive ? 'border-red-600 animate-[spin_6s_linear_infinite]' : 'border-slate-400 animate-[spin_20s_linear_infinite]'}`}></div>
            <div className={`absolute inset-3 rounded-full border ${divergenceActive ? 'border-red-500 animate-ping' : 'border-slate-300'}`}></div>
            
            {/* Center Westworld Solomon Inscription */}
            <div className="text-center font-mono space-y-1 p-3 bg-white/95 rounded-full shadow-inner border border-slate-300 z-10">
              <div className="text-[10px] text-slate-500 tracking-widest uppercase font-bold">04.17.39</div>
              <div className="text-xs font-black tracking-tight text-slate-950">SYSTEM INITIATED</div>
              <div className="text-[9px] text-slate-600 uppercase font-semibold">UNDISCLOSED LOCATION</div>
              <div className="text-[9px] font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded border border-slate-300">
                'SOLOMON' BUILD 0.06
              </div>
            </div>
          </div>

          {/* 4 NON-OVERLAPPING CORNER CALLOUT CARDS */}
          {/* Top-Left Card */}
          <div
            onClick={() => setActiveCallout(callouts[0])}
            className="absolute top-4 left-4 z-20 font-mono text-left cursor-pointer transition-all hover:scale-105"
          >
            <div className="bg-white border-2 border-slate-900 p-3.5 rounded-xl shadow-xl space-y-1.5 w-64 backdrop-blur-sm">
              <div className="text-[10px] font-black text-slate-500">{callouts[0].date}</div>
              <div className="text-xs font-black tracking-tight text-slate-950 uppercase">{callouts[0].divergenceType}</div>
              <div className="text-[10px] font-bold text-red-600 uppercase">{callouts[0].incidentName}</div>
              <div className="flex justify-between items-center text-[9px] text-slate-600 pt-1.5 border-t border-slate-200">
                <span>{callouts[0].service}</span>
                <span className="font-bold text-slate-950">RISK: {callouts[0].riskScore}</span>
              </div>
            </div>
          </div>

          {/* Top-Right Card */}
          <div
            onClick={() => setActiveCallout(callouts[1])}
            className="absolute top-4 right-4 z-20 font-mono text-left cursor-pointer transition-all hover:scale-105"
          >
            <div className="bg-white border-2 border-slate-900 p-3.5 rounded-xl shadow-xl space-y-1.5 w-64 backdrop-blur-sm">
              <div className="text-[10px] font-black text-slate-500">{callouts[1].date}</div>
              <div className="text-xs font-black tracking-tight text-slate-950 uppercase">{callouts[1].divergenceType}</div>
              <div className="text-[10px] font-bold text-red-600 uppercase">{callouts[1].incidentName}</div>
              <div className="flex justify-between items-center text-[9px] text-slate-600 pt-1.5 border-t border-slate-200">
                <span>{callouts[1].service}</span>
                <span className="font-bold text-slate-950">RISK: {callouts[1].riskScore}</span>
              </div>
            </div>
          </div>

          {/* Bottom-Left Card */}
          <div
            onClick={() => setActiveCallout(callouts[2])}
            className="absolute bottom-4 left-4 z-20 font-mono text-left cursor-pointer transition-all hover:scale-105"
          >
            <div className="bg-white border-2 border-slate-900 p-3.5 rounded-xl shadow-xl space-y-1.5 w-64 backdrop-blur-sm">
              <div className="text-[10px] font-black text-slate-500">{callouts[2].date}</div>
              <div className="text-xs font-black tracking-tight text-slate-950 uppercase">{callouts[2].divergenceType}</div>
              <div className="text-[10px] font-bold text-red-600 uppercase">{callouts[2].incidentName}</div>
              <div className="flex justify-between items-center text-[9px] text-slate-600 pt-1.5 border-t border-slate-200">
                <span>{callouts[2].service}</span>
                <span className="font-bold text-slate-950">RISK: {callouts[2].riskScore}</span>
              </div>
            </div>
          </div>

          {/* Bottom-Right Card */}
          <div
            onClick={() => setActiveCallout(callouts[3])}
            className="absolute bottom-4 right-4 z-20 font-mono text-left cursor-pointer transition-all hover:scale-105"
          >
            <div className="bg-white border-2 border-slate-900 p-3.5 rounded-xl shadow-xl space-y-1.5 w-64 backdrop-blur-sm">
              <div className="text-[10px] font-black text-slate-500">{callouts[3].date}</div>
              <div className="text-xs font-black tracking-tight text-slate-950 uppercase">{callouts[3].divergenceType}</div>
              <div className="text-[10px] font-bold text-red-600 uppercase">{callouts[3].incidentName}</div>
              <div className="flex justify-between items-center text-[9px] text-slate-600 pt-1.5 border-t border-slate-200">
                <span>{callouts[3].service}</span>
                <span className="font-bold text-slate-950">RISK: {callouts[3].riskScore}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* IMAGE 1 HOMAGE: HORIZON ANOMALY DIVERGENCE WAVEFORM CURVE */}
      <div className="bg-white rounded-3xl border border-slate-300 p-6 shadow-xl space-y-4">
        <div className="flex justify-between items-center border-b border-slate-200 pb-3">
          <div className="space-y-0.5">
            <div className="text-xs font-mono font-bold text-slate-950 uppercase tracking-wider">
              10.09.25 DIVERGENCE : PARIS / THERMONUCLEAR & GCP CLOUD RUN WAVEFORM HORIZON
            </div>
            <div className="text-[11px] text-slate-500 font-mono">Particle Noise Horizon Waveform Analysis</div>
          </div>
          <span className="text-xs font-mono font-bold px-3 py-1 bg-slate-900 text-white rounded">
            PARTICLE HORIZON SCANNER
          </span>
        </div>

        {/* Particle Noise Horizon Curve */}
        <div className="h-44 w-full bg-[#f8fafc] rounded-2xl border border-slate-300 p-4 flex items-end justify-between gap-1 relative overflow-hidden">
          <div className="absolute inset-0 bg-[radial-gradient(#000000_1px,transparent_1px)] [background-size:16px_16px] opacity-10 pointer-events-none"></div>
          {[
            12, 14, 18, 22, 35, 48, 92, 120, 85, 45, 30, 24, 20, 18, 16,
            14, 18, 25, 40, 75, 110, 60, 32, 22, 18, 16, 14, 12, 10, 8
          ].map((val, i) => {
            const h = divergenceActive ? Math.min(100, val + 25) : val;
            const isSpike = val > 70;
            return (
              <div key={i} className="flex-1 flex flex-col items-center h-full justify-end z-10">
                <div
                  style={{ height: `${h}%` }}
                  className={`w-full rounded-t transition-all duration-300 ${
                    isSpike || divergenceActive
                      ? 'bg-slate-950 shadow-[0_0_10px_rgba(0,0,0,0.5)]'
                      : 'bg-slate-400 opacity-60'
                  }`}
                ></div>
              </div>
            );
          })}
        </div>
      </div>

      {/* CREATIVE ADDITION: SOLOMON THOUGHT-STREAM NARRATIVE TERMINAL */}
      <div className="bg-slate-950 text-white rounded-3xl p-6 shadow-2xl space-y-3 font-mono">
        <div className="flex justify-between items-center border-b border-slate-800 pb-3">
          <div className="flex items-center space-x-2">
            <Terminal className="w-4 h-4 text-cyan-400" />
            <span className="text-xs font-bold uppercase tracking-wider">SOLOMON THOUGHT-STREAM & RECOVERING LOOP TERMINAL</span>
          </div>
          <span className="text-[10px] text-cyan-400">GEMINI 3.5 FLASH LITE NARRATIVE HARNESS</span>
        </div>

        <div className="space-y-1.5 text-xs text-slate-300">
          {solomonStream.map((line, idx) => (
            <div key={idx} className="flex items-start gap-2">
              <span className="text-cyan-400 font-bold">›</span>
              <span className="leading-relaxed">{line}</span>
            </div>
          ))}
        </div>
      </div>

      {/* INSPECTOR MODAL FOR ANOMALY CALLOUT */}
      {activeCallout && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
          <div className="bg-white border-2 border-slate-900 rounded-3xl max-w-xl w-full p-6 space-y-4 shadow-2xl font-mono">
            <div className="flex justify-between items-center border-b border-slate-200 pb-3">
              <div>
                <span className="text-[10px] text-slate-500 font-bold">{activeCallout.date}</span>
                <h3 className="text-sm font-black text-slate-950 uppercase">{activeCallout.divergenceType}</h3>
              </div>
              <button
                onClick={() => setActiveCallout(null)}
                className="p-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-900 cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
              <div className="text-xs font-bold text-red-600">{activeCallout.incidentName}</div>
              <div className="text-[11px] text-slate-600">Service: <strong>{activeCallout.service}</strong></div>
              <div className="text-[11px] text-slate-600">Location: <strong>{activeCallout.location}</strong></div>
              <div className="text-[11px] text-slate-600">Divergence Risk: <strong>{activeCallout.riskScore}</strong></div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setActiveCallout(null)}
                className="px-5 py-2.5 rounded-full bg-slate-950 hover:bg-slate-800 text-white font-bold text-xs shadow-lg cursor-pointer"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
