import React, { useState } from 'react';
import { Globe, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react';
import { GroundingData } from '../types/chat';

interface GroundingCardProps {
  grounding: GroundingData;
}

export const GroundingCard: React.FC<GroundingCardProps> = ({ grounding }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const sources = grounding.sources || [];
  const queries = grounding.queries || [];

  if (sources.length === 0 && queries.length === 0) return null;

  return (
    <div className="mt-3 border border-[#dadce0] rounded-xl bg-[#f8fafd] overflow-hidden text-xs transition-all">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-3 py-2 flex items-center justify-between hover:bg-[#f1f3f4] transition text-[#202124] font-medium"
      >
        <div className="flex items-center gap-2">
          <Globe className="w-3.5 h-3.5 text-blue-600" />
          <span>Fuentes de Google Search ({sources.length})</span>
        </div>
        <div className="text-[#5f6368] flex items-center gap-1">
          <span className="text-[11px]">{isExpanded ? 'Ocultar' : 'Ver fuentes'}</span>
          {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </div>
      </button>

      {isExpanded && (
        <div className="p-3 border-t border-[#dadce0] bg-white space-y-2">
          {queries.length > 0 && (
            <div className="mb-2">
              <span className="text-[11px] text-[#5f6368] font-medium uppercase tracking-wider block mb-1">
                Consultas de Búsqueda:
              </span>
              <div className="flex flex-wrap gap-1.5">
                {queries.map((q, i) => (
                  <span
                    key={i}
                    className="bg-[#f1f3f4] text-[#3c4043] px-2 py-0.5 rounded-md font-mono text-[11px]"
                  >
                    "{q}"
                  </span>
                ))}
              </div>
            </div>
          )}

          {sources.length > 0 && (
            <div className="space-y-1.5">
              <span className="text-[11px] text-[#5f6368] font-medium uppercase tracking-wider block mb-1">
                Enlaces Citados:
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {sources.map((src, i) => (
                  <a
                    key={i}
                    href={src.uri}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center justify-between p-2 rounded-lg border border-[#dadce0] bg-[#f8fafd] hover:bg-[#f1f6fd] hover:border-blue-300 transition text-[#1a73e8] group"
                  >
                    <span className="truncate text-xs font-medium text-[#202124] group-hover:text-blue-600">
                      {src.title || src.uri}
                    </span>
                    <ExternalLink className="w-3 h-3 text-[#5f6368] group-hover:text-blue-600 shrink-0 ml-1.5" />
                  </a>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
