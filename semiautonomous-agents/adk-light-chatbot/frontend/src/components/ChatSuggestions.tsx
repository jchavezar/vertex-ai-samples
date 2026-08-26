import React from 'react';
import { Sparkles, Code2, Zap, Brain } from 'lucide-react';

interface ChatSuggestionsProps {
  onSelectPrompt: (prompt: string) => void;
}

const SUGGESTIONS = [
  {
    icon: Sparkles,
    title: '¿Cómo funciona Google ADK?',
    subtitle: 'Arquitectura de agentes, runners y herramientas.',
    prompt: '¿Cómo funciona Google ADK (Agent Development Kit) y cuáles son sus ventajas para crear agentes inteligentes?'
  },
  {
    icon: Code2,
    title: 'Agente en Python con ADK',
    subtitle: 'Ejemplo completo con Agent e InMemoryRunner.',
    prompt: 'Escribe un ejemplo de código en Python que use Google ADK (Agent, InMemoryRunner) para crear un asistente con streaming.'
  },
  {
    icon: Zap,
    title: 'Capacidades de Gemini 2.5 Flash',
    subtitle: 'Rendimiento, latencia y razonamiento multimodal.',
    prompt: '¿Cuáles son las principales capacidades y ventajas de Gemini 2.5 Flash en términos de velocidad, latencia y razonamiento?'
  },
  {
    icon: Brain,
    title: 'Sesiones y Memoria en ADK',
    subtitle: 'Gestión de estado con InMemorySessionService.',
    prompt: 'Explica cómo gestiona Google ADK las sesiones conversacionales con InMemorySessionService y la persistencia de estado.'
  }
];

export const ChatSuggestions: React.FC<ChatSuggestionsProps> = ({ onSelectPrompt }) => {
  return (
    <div className="max-w-2xl mx-auto my-auto py-8 px-4 text-center">
      <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center text-white mx-auto shadow-md mb-4">
        <Sparkles className="w-7 h-7" />
      </div>

      <h2 className="text-2xl font-bold text-[#202124] mb-2">
        ¿En qué puedo ayudarte hoy?
      </h2>
      <p className="text-sm text-[#5f6368] mb-8 max-w-md mx-auto">
        Pregunta lo que desees o selecciona una de las siguientes sugerencias para interactuar con el agente <strong>Google ADK</strong>.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-left">
        {SUGGESTIONS.map((item, idx) => {
          const Icon = item.icon;
          return (
            <button
              key={idx}
              onClick={() => onSelectPrompt(item.prompt)}
              className="p-4 rounded-xl border border-[#dadce0] bg-white hover:bg-[#f8fafd] hover:border-blue-300 hover:shadow-xs transition group text-left flex flex-col justify-between"
            >
              <div className="flex items-center gap-2.5 mb-1.5">
                <div className="w-7 h-7 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center shrink-0 group-hover:bg-blue-100 transition">
                  <Icon className="w-4 h-4" />
                </div>
                <div className="font-semibold text-xs sm:text-sm text-[#202124] group-hover:text-blue-600 transition truncate">
                  {item.title}
                </div>
              </div>
              <p className="text-[12px] text-[#5f6368] line-clamp-2">
                {item.subtitle}
              </p>
            </button>
          );
        })}
      </div>
    </div>
  );
};
