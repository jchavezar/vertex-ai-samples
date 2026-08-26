import React from 'react';
import { Sparkles, Menu, CheckCircle2, Globe, Cpu } from 'lucide-react';
import { ModelInfo } from '../types/chat';

interface HeaderProps {
  onToggleSidebar: () => void;
  activeModel?: ModelInfo;
  isSearchEnabled: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  onToggleSidebar,
  activeModel,
  isSearchEnabled
}) => {
  return (
    <header className="sticky top-0 z-10 bg-white/90 backdrop-blur-md border-b border-[#dadce0] px-4 py-3 sm:px-6 flex items-center justify-between transition-all">
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="p-2 rounded-full hover:bg-[#f1f3f4] text-[#5f6368] transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
          title="Alternar Menú"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white shadow-sm">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-semibold text-base text-[#202124] leading-tight">
                Google ADK Chatbot
              </h1>
              <span className="hidden sm:inline-flex items-center gap-1 text-[11px] font-medium bg-[#e6f4ea] text-[#137333] px-2 py-0.5 rounded-full border border-[#ceead6]">
                <CheckCircle2 className="w-3 h-3" />
                ADK 2.1.0 Activo
              </span>
            </div>
            <p className="text-xs text-[#5f6368] hidden sm:block">
              {activeModel ? activeModel.name : 'Gemini 2.5 Flash'} • Vertex AI
            </p>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-2">
        {isSearchEnabled && (
          <span className="inline-flex items-center gap-1.5 text-xs font-medium text-blue-700 bg-blue-50 border border-blue-200 px-2.5 py-1 rounded-full animate-fade-in">
            <Globe className="w-3.5 h-3.5" />
            <span className="hidden md:inline">Google Search Activo</span>
          </span>
        )}

        <div className="flex items-center gap-1.5 text-xs text-[#5f6368] bg-[#f8fafd] border border-[#dadce0] px-3 py-1.5 rounded-lg">
          <Cpu className="w-3.5 h-3.5 text-blue-600" />
          <span className="font-medium text-[#202124]">
            {activeModel ? activeModel.name : 'Gemini'}
          </span>
        </div>
      </div>
    </header>
  );
};
