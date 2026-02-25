import { useState, useRef, useEffect } from 'react';
import clsx from 'clsx';
import { useWorkstationChat } from '../context/ChatContext';
import { ChevronDown, Sparkles, Check } from 'lucide-react';

const MODELS = [
  { id: 'gemini-3-flash-preview', name: 'Gemini 3.0 Flash (Global)', tag: 'FASTEST' },
  { id: 'gemini-3-pro-preview', name: 'Gemini 3.0 Pro (Global)', tag: 'SMARTEST' },
  { id: 'claude-3-5-sonnet-v2', name: 'Claude 3.5 Sonnet v2', tag: 'ANTHROPIC' },
  { id: 'gemini-2.5-flash', name: 'Gemini 2.5 Flash', tag: 'STABLE' },
  { id: 'gemini-2.5-flash-lite', name: 'Gemini 2.5 Flash-Lite', tag: 'EFFICIENT' },
  { id: 'gemini-2.5-pro', name: 'Gemini 2.5 Pro', tag: 'BALANCED' },
];

export function ModelSelector() {
  const { selectedModel, setSelectedModel } = useWorkstationChat();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const currentModel = MODELS.find(m => m.id === selectedModel) || MODELS[0];

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={(e) => {
          e.stopPropagation();
          setIsOpen(!isOpen);
        }}
        className={clsx(
          "flex items-center gap-3 px-5 py-2.5 rounded-full transition-all duration-300 relative overflow-hidden group shadow-md hover:shadow-lg",
          // Light Mode: High contrast slate/white with blue accent
          "bg-white border-2 border-slate-100 text-slate-700",
          // Dark Mode: Deep titanium
          "dark:bg-white/5 dark:border-white/10 dark:text-white",
          // Hover state
          "hover:border-blue-400/50 dark:hover:border-blue-400/50 hover:scale-[1.02]",
          // Open state
          isOpen && "ring-2 ring-blue-500/20 border-blue-500 shadow-blue-500/10"
        )}
      >
        {/* Animated sheen effect */}
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:animate-shimmer" />

        <div className={clsx("p-1.5 rounded-full bg-blue-50 text-blue-600 dark:bg-blue-500/20 dark:text-blue-400")}>
          <Sparkles size={14} className="fill-current" />
        </div>

        <div className="flex flex-col items-start leading-none mr-2">
          <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-0.5">Model</span>
          <span className="text-sm font-black tracking-tight group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
            {currentModel.name.replace(' (Global)', '')}
          </span>
        </div>

        <ChevronDown size={16} className={clsx("text-slate-400 transition-transform duration-300", isOpen && "rotate-180 text-blue-500")} />
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute top-full right-0 mt-2 w-72 bg-[#0a0a0a]/95 backdrop-blur-xl border border-[#2a2a2a] rounded-xl shadow-[0_10px_40px_-10px_rgba(0,0,0,0.5)] z-[100] overflow-hidden transform animate-in fade-in zoom-in-95 duration-100 origin-top-right">
          <div className="p-1.5 space-y-0.5">
            <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">
              Select Model Version
            </div>
            
            {MODELS.map((model) => {
              const isSelected = selectedModel === model.id;
              return (
                <button
                  key={model.id}
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedModel(model.id);
                    setIsOpen(false);
                  }}
                  className={`
                    w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-left transition-all duration-150 group
                    ${isSelected 
                      ? 'bg-blue-500/10 text-blue-400' 
                      : 'hover:bg-[#1a1a1a] text-gray-400 hover:text-gray-200'}
                  `}
                >
                  <div className="flex flex-col gap-0.5">
                    <span className={`text-sm font-medium ${isSelected ? 'text-blue-400' : 'text-gray-300'}`}>
                      {model.name}
                    </span>
                    <span className="text-[10px] text-gray-600 group-hover:text-gray-500">
                      {model.id}
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    {model.tag && (
                      <span className={`
                        text-[10px] px-1.5 py-0.5 rounded border font-semibold tracking-wide
                        ${isSelected 
                          ? 'bg-blue-500/20 border-blue-500/30 text-blue-300' 
                          : 'bg-[#1a1a1a] border-[#333] text-gray-500'}
                      `}>
                        {model.tag}
                      </span>
                    )}
                    {isSelected && <Check className="w-4 h-4 text-blue-400" />}
                  </div>
                </button>
              );
            })}
          </div>
          
          <div className="px-3 py-2 bg-[#050505] border-t border-[#1a1a1a] text-[10px] text-gray-600">
            Preview models require global region access.
          </div>
        </div>
      )}
    </div>
  );
}
