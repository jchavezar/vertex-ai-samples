import React from 'react';
import { 
  X, 
  RotateCcw, 
  Globe, 
  Bot, 
  BrainCircuit, 
  Sliders, 
  Info,
  ShieldCheck
} from 'lucide-react';
import { ModelInfo, ChatConfig } from '../types/chat';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  models: ModelInfo[];
  config: ChatConfig;
  onChangeConfig: (newConfig: Partial<ChatConfig>) => void;
  onResetSession: () => void;
  messageCount: number;
  sessionId: string;
}

const PRESET_PERSONAS: Record<string, string> = {
  'Asistente General': 'Eres un asistente virtual inteligente, empático, preciso y profesional creado con Google ADK (Agent Development Kit). Responde siempre de forma estructurada, clara y con un tono amable.',
  'Experto en Código Python': 'Eres un ingeniero de software senior experto en Python, Google ADK y Vertex AI. Proporciona código limpio, tipado, modular y bien documentado.',
  'Analista de Datos': 'Eres un consultor analítico de datos senior. Explica hallazgos cuantitativos con rigor, sugiere visualizaciones y sintetiza información clave.',
  'Tutor Didáctico': 'Eres un profesor universitario paciente y amigable. Explica conceptos paso a paso con analogías sencillas y preguntas de verificación.'
};

export const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  onClose,
  models,
  config,
  onChangeConfig,
  onResetSession,
  messageCount,
  sessionId
}) => {
  const currentModel = models.find(m => m.id === config.model) || models[0];

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/20 backdrop-blur-xs z-20 md:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed md:static inset-y-0 left-0 z-30 w-80 bg-[#f8fafd] border-r border-[#dadce0] flex flex-col transition-transform duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        {/* Sidebar Header */}
        <div className="p-4 border-b border-[#dadce0] flex items-center justify-between bg-white">
          <div className="flex items-center gap-2 text-sm font-semibold text-[#202124]">
            <Sliders className="w-4 h-4 text-blue-600" />
            <span>Configuración del Agente</span>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-full hover:bg-[#f1f3f4] text-[#5f6368] md:hidden"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Configuration Body */}
        <div className="flex-1 overflow-y-auto p-4 space-y-5 text-sm">
          {/* 1. Model Selector */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-[#5f6368] mb-2 flex items-center gap-1.5">
              <Bot className="w-3.5 h-3.5 text-blue-600" />
              Modelo Gemini (Vertex AI)
            </label>
            <select
              value={config.model}
              onChange={(e) => onChangeConfig({ model: e.target.value })}
              className="w-full bg-white border border-[#dadce0] rounded-lg px-3 py-2 text-[#202124] text-xs sm:text-sm font-medium focus:ring-2 focus:ring-blue-500 focus:outline-none transition shadow-xs"
            >
              {models.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.name} ({m.badge})
                </option>
              ))}
            </select>

            {currentModel && (
              <div className="mt-2 bg-blue-50/60 border border-blue-100 rounded-lg p-2.5 text-xs text-[#174ea6] flex items-start gap-2">
                <Info className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                <span>{currentModel.description}</span>
              </div>
            )}
          </div>

          {/* 2. ADK Tools Toggle */}
          <div className="pt-2 border-t border-[#dadce0]">
            <label className="block text-xs font-semibold uppercase tracking-wider text-[#5f6368] mb-2 flex items-center gap-1.5">
              <Globe className="w-3.5 h-3.5 text-blue-600" />
              Herramientas Google ADK
            </label>

            <div className="bg-white border border-[#dadce0] rounded-xl p-3 shadow-xs">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium text-xs text-[#202124]">Grounding con Google Search</div>
                  <div className="text-[11px] text-[#5f6368]">
                    Búsqueda web en vivo mediante ADK
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={config.enableSearch}
                    onChange={(e) => onChangeConfig({ enableSearch: e.target.checked })}
                    className="sr-only peer"
                  />
                  <div className="w-10 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
            </div>
          </div>

          {/* 3. System Persona / Prompt */}
          <div className="pt-2 border-t border-[#dadce0]">
            <label className="block text-xs font-semibold uppercase tracking-wider text-[#5f6368] mb-2 flex items-center gap-1.5">
              <BrainCircuit className="w-3.5 h-3.5 text-blue-600" />
              Instrucción del Sistema
            </label>

            <select
              onChange={(e) => {
                const val = PRESET_PERSONAS[e.target.value];
                if (val) onChangeConfig({ instruction: val });
              }}
              className="w-full bg-white border border-[#dadce0] rounded-lg px-3 py-1.5 text-xs text-[#5f6368] mb-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            >
              <option value="">-- Seleccionar Plantilla --</option>
              {Object.keys(PRESET_PERSONAS).map((name) => (
                <option key={name} value={name}>{name}</option>
              ))}
            </select>

            <textarea
              value={config.instruction}
              onChange={(e) => onChangeConfig({ instruction: e.target.value })}
              rows={4}
              className="w-full bg-white border border-[#dadce0] rounded-lg p-2.5 text-xs text-[#202124] focus:ring-2 focus:ring-blue-500 focus:outline-none leading-relaxed resize-none shadow-xs"
              placeholder="Directivas que rigen el comportamiento del agente..."
            />
          </div>

          {/* Security & Protocol Notice */}
          <div className="bg-[#e6f4ea] border border-[#ceead6] rounded-xl p-3 text-xs text-[#137333]">
            <div className="flex items-center gap-1.5 font-semibold mb-1">
              <ShieldCheck className="w-4 h-4 text-[#137333]" />
              <span>Zero-Leak Protocol Activo</span>
            </div>
            <p className="text-[11px] leading-tight text-[#137333]/90">
              Autenticación gestionada de forma segura mediante Vertex AI Application Default Credentials.
            </p>
          </div>
        </div>

        {/* Sidebar Footer / Session Controls */}
        <div className="p-4 border-t border-[#dadce0] bg-white space-y-3">
          <div className="flex items-center justify-between text-xs text-[#5f6368]">
            <span>Mensajes: <strong>{messageCount}</strong></span>
            <span className="font-mono text-[11px] text-[#5f6368] truncate max-w-[120px]" title={sessionId}>
              {sessionId}
            </span>
          </div>

          <button
            onClick={onResetSession}
            className="w-full flex items-center justify-center gap-2 bg-white hover:bg-[#f1f3f4] text-[#202124] border border-[#dadce0] py-2 px-4 rounded-lg font-medium text-xs transition shadow-xs hover:border-gray-400 active:scale-[0.99]"
          >
            <RotateCcw className="w-3.5 h-3.5 text-[#5f6368]" />
            <span>Nueva Conversación</span>
          </button>
        </div>
      </aside>
    </>
  );
};
