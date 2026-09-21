import React from 'react';
import { ExternalLink, Maximize2 } from 'lucide-react';

export function Constellation3DView() {
  return (
    <div className="w-full flex-1 h-[calc(100vh-125px)] min-h-[640px] rounded-2xl overflow-hidden border border-slate-800 bg-slate-950 relative shadow-2xl flex flex-col">
      <div className="absolute top-4 right-4 z-20 flex items-center gap-2">
        <a
          href="/constellation.html"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900/90 hover:bg-slate-800 text-xs font-mono text-slate-200 border border-slate-700 backdrop-blur-md transition shadow-lg hover:text-white cursor-pointer"
        >
          <Maximize2 className="w-3.5 h-3.5 text-blue-400" />
          <span>Open Fullscreen</span>
          <ExternalLink className="w-3 h-3 text-slate-400 ml-0.5" />
        </a>
      </div>
      <iframe
        src="/constellation.html"
        title="3D Architecture Universe"
        className="w-full h-full flex-1 border-0"
      />
    </div>
  );
}
