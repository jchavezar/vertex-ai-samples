import React from 'react';
import { ActiveModule } from '../types';
import { Mic, Film, Network, ShieldCheck, Sparkles, MonitorPlay } from 'lucide-react';

interface HeaderProps {
  activeModule: ActiveModule;
  onSelectModule: (module: ActiveModule) => void;
}

export const Header: React.FC<HeaderProps> = ({ activeModule, onSelectModule }) => {
  return (
    <header className="sticky top-0 z-40 w-full bg-white/90 backdrop-blur-md border-b border-slate-200 shadow-sm">
      <div className="max-w-[1720px] mx-auto px-6 py-4">
        <div className="flex flex-col xl:flex-row items-center justify-between gap-4">
          
          {/* Brand & Title */}
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-blue-700 via-indigo-600 to-cyan-500 flex items-center justify-center shadow-md text-white">
              <Sparkles className="w-7 h-7" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider bg-blue-50 text-blue-700 border border-blue-200">
                  Google Cloud EBC
                </span>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  Vertex AI Enterprise
                </span>
                <span className="text-xs font-medium text-slate-500 hidden sm:inline">
                  • Pantalla Directiva 100"
                </span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2 mt-0.5">
                EBC Executive AI Transformation Showcase
              </h1>
            </div>
          </div>

          {/* Module Navigation Buttons */}
          <nav className="flex items-center bg-slate-100 p-1.5 rounded-2xl border border-slate-200 shadow-inner">
            <button
              onClick={() => onSelectModule('voice')}
              className={`flex items-center gap-2.5 px-5 py-3 rounded-xl font-bold text-base transition-all duration-200 ${
                activeModule === 'voice'
                  ? 'bg-white text-blue-700 shadow-md border border-slate-200/80 scale-[1.02]'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'
              }`}
            >
              <div className={`p-1.5 rounded-lg ${activeModule === 'voice' ? 'bg-blue-100 text-blue-700' : 'bg-slate-200 text-slate-600'}`}>
                <Mic className="w-5 h-5" />
              </div>
              <div className="text-left">
                <span className="block text-xs uppercase tracking-wider font-extrabold text-blue-600">Módulo A</span>
                <span className="block font-bold">Asistente de Voz Live</span>
              </div>
            </button>

            <button
              onClick={() => onSelectModule('creative')}
              className={`flex items-center gap-2.5 px-5 py-3 rounded-xl font-bold text-base transition-all duration-200 ${
                activeModule === 'creative'
                  ? 'bg-white text-fuchsia-700 shadow-md border border-slate-200/80 scale-[1.02]'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'
              }`}
            >
              <div className={`p-1.5 rounded-lg ${activeModule === 'creative' ? 'bg-fuchsia-100 text-fuchsia-700' : 'bg-slate-200 text-slate-600'}`}>
                <Film className="w-5 h-5" />
              </div>
              <div className="text-left">
                <span className="block text-xs uppercase tracking-wider font-extrabold text-fuchsia-600">Módulo B</span>
                <span className="block font-bold">Estudio Creativo & Reels</span>
              </div>
            </button>

            <button
              onClick={() => onSelectModule('swarm')}
              className={`flex items-center gap-2.5 px-5 py-3 rounded-xl font-bold text-base transition-all duration-200 ${
                activeModule === 'swarm'
                  ? 'bg-white text-emerald-700 shadow-md border border-slate-200/80 scale-[1.02]'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'
              }`}
            >
              <div className={`p-1.5 rounded-lg ${activeModule === 'swarm' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-200 text-slate-600'}`}>
                <Network className="w-5 h-5" />
              </div>
              <div className="text-left">
                <span className="block text-xs uppercase tracking-wider font-extrabold text-emerald-600">Módulo C</span>
                <span className="block font-bold">Enjambre Autónomo (4 Lanes)</span>
              </div>
            </button>
          </nav>

          {/* Executive Display Mode Badge */}
          <div className="hidden 2xl:flex items-center gap-3 pl-4 border-l border-slate-200">
            <div className="w-3 h-3 rounded-full bg-emerald-500 animate-ping"></div>
            <div className="text-right">
              <span className="block text-xs font-bold uppercase tracking-wider text-slate-500">Estado de Transmisión</span>
              <span className="block text-sm font-semibold text-slate-800 flex items-center gap-1">
                <MonitorPlay className="w-4 h-4 text-blue-600" />
                Sala C-Suite Activa
              </span>
            </div>
          </div>

        </div>
      </div>
    </header>
  );
};
