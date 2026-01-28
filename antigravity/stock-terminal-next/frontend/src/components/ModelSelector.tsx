import React, { useState, useRef, useEffect } from 'react';
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
        className={`
          flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 border
          ${isOpen 
            ? 'bg-blue-500/10 border-blue-500/50 text-blue-400 shadow-[0_0_15px_rgba(59,130,246,0.3)]' 
            : 'bg-[#0a0a0a] border-[#2a2a2a] text-gray-400 hover:text-gray-200 hover:border-[#3a3a3a]'}
        `}
      >
        <Sparkles className="w-3.5 h-3.5 text-purple-400" />
        <span className="bg-gradient-to-r from-gray-200 to-gray-400 bg-clip-text text-transparent">
          {currentModel.name}
        </span>
        <ChevronDown className={`w-3.5 h-3.5 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
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
