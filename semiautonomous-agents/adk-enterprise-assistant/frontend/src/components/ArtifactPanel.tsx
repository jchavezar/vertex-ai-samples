import React, { useState } from 'react';
import {
  X,
  Download,
  Copy,
  Check,
  BarChart3,
  FileText,
  Code2,
  Sparkles,
  Maximize2,
  Minimize2
} from 'lucide-react';
import type { ArtifactData } from '../types';
import { InteractiveChart } from './InteractiveChart';

interface ArtifactPanelProps {
  artifacts: ArtifactData[];
  selectedArtifactId: string | null;
  onSelectArtifact: (id: string) => void;
  onClose: () => void;
}

export const ArtifactPanel: React.FC<ArtifactPanelProps> = ({
  artifacts,
  selectedArtifactId,
  onSelectArtifact,
  onClose,
}) => {
  const [copied, setCopied] = useState<boolean>(false);
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);

  const currentArtifact =
    artifacts.find((a) => a.artifact_id === selectedArtifactId) || artifacts[artifacts.length - 1];

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadJson = () => {
    if (!currentArtifact) return;
    const blob = new Blob([JSON.stringify(currentArtifact, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${currentArtifact.title.toLowerCase().replace(/\s+/g, '_')}_artifact.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!artifacts || artifacts.length === 0) {
    return (
      <aside className="w-96 border-l border-slate-200 bg-slate-50/70 p-6 flex flex-col items-center justify-center text-center text-slate-400 select-none">
        <div className="w-12 h-12 rounded-xl bg-slate-100 flex items-center justify-center mb-3">
          <Sparkles className="w-6 h-6 text-slate-400" />
        </div>
        <h4 className="text-sm font-semibold text-slate-700">No Artifacts Generated Yet</h4>
        <p className="text-xs text-slate-500 mt-1 max-w-[240px]">
          Ask the assistant to model scenarios, analyze metrics, or create visualizations to render live artifacts here.
        </p>
      </aside>
    );
  }

  return (
    <aside
      className={`${
        isFullscreen
          ? 'fixed inset-4 z-50 rounded-2xl shadow-2xl border'
          : 'w-full lg:w-[560px] xl:w-[620px] shrink-0 border-l'
      } border-slate-200 bg-white flex flex-col h-[calc(100vh-3.5rem)] transition-all duration-300 select-none overflow-hidden`}
    >
      {/* Header Bar */}
      <div className="p-3.5 border-b border-slate-200 bg-slate-50/80 flex items-center justify-between">
        <div className="flex items-center space-x-2 min-w-0">
          <div className="w-6 h-6 rounded bg-cyan-100 text-cyan-800 flex items-center justify-center shrink-0">
            <BarChart3 className="w-3.5 h-3.5" />
          </div>
          <div className="truncate">
            <h3 className="text-xs font-bold text-slate-900 truncate">
              Executive Artifact Preview
            </h3>
            <span className="text-[10px] text-slate-500 font-mono">
              {artifacts.length} total artifact{artifacts.length > 1 ? 's' : ''}
            </span>
          </div>
        </div>

        <div className="flex items-center space-x-1">
          <button
            onClick={handleDownloadJson}
            className="p-1.5 text-slate-500 hover:text-slate-900 hover:bg-slate-200/60 rounded transition-colors cursor-pointer"
            title="Download JSON definition"
          >
            <Download className="w-4 h-4" />
          </button>
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-1.5 text-slate-500 hover:text-slate-900 hover:bg-slate-200/60 rounded transition-colors cursor-pointer"
            title={isFullscreen ? 'Collapse' : 'Expand full-screen'}
          >
            {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-500 hover:text-slate-900 hover:bg-slate-200/60 rounded transition-colors cursor-pointer"
            title="Close panel"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Artifact Tabs Selector */}
      {artifacts.length > 1 && (
        <div className="px-3 pt-2 pb-1 border-b border-slate-100 flex items-center space-x-1.5 overflow-x-auto bg-slate-50/40">
          {artifacts.map((art) => (
            <button
              key={art.artifact_id}
              onClick={() => onSelectArtifact(art.artifact_id)}
              className={`text-xs px-2.5 py-1 rounded-md font-medium whitespace-nowrap transition-all border cursor-pointer ${
                currentArtifact?.artifact_id === art.artifact_id
                  ? 'bg-white text-slate-900 border-slate-300 shadow-2xs'
                  : 'bg-transparent text-slate-500 border-transparent hover:text-slate-800'
              }`}
            >
              {art.title.length > 22 ? `${art.title.slice(0, 22)}...` : art.title}
            </button>
          ))}
        </div>
      )}

      {/* Artifact Body */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {currentArtifact && (
          <div>
            {currentArtifact.artifact_type === 'interactive_chart' && (
              <InteractiveChart artifact={currentArtifact} />
            )}

            {currentArtifact.artifact_type === 'code_snippet' && currentArtifact.content && (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-800 flex items-center space-x-1.5">
                    <Code2 className="w-3.5 h-3.5 text-emerald-600" />
                    <span>{currentArtifact.title}</span>
                  </span>
                  <button
                    onClick={() => handleCopy(currentArtifact.content || '')}
                    className="text-xs text-slate-500 hover:text-slate-900 flex items-center space-x-1 px-2 py-1 bg-slate-100 rounded border border-slate-200 cursor-pointer"
                  >
                    {copied ? <Check className="w-3 h-3 text-emerald-600" /> : <Copy className="w-3 h-3" />}
                    <span>{copied ? 'Copied' : 'Copy'}</span>
                  </button>
                </div>
                <pre className="p-3 bg-slate-900 text-emerald-300 rounded-lg text-xs font-mono overflow-x-auto">
                  <code>{currentArtifact.content}</code>
                </pre>
              </div>
            )}

            {currentArtifact.artifact_type === 'executive_summary' && currentArtifact.content && (
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
                <div className="flex items-center justify-between border-b border-slate-200 pb-2">
                  <span className="text-xs font-bold text-slate-900 flex items-center space-x-1.5">
                    <FileText className="w-3.5 h-3.5 text-indigo-600" />
                    <span>{currentArtifact.title}</span>
                  </span>
                  <button
                    onClick={() => handleCopy(currentArtifact.content || '')}
                    className="text-xs text-slate-500 hover:text-slate-900 flex items-center space-x-1 cursor-pointer"
                  >
                    {copied ? <Check className="w-3 h-3 text-emerald-600" /> : <Copy className="w-3 h-3" />}
                  </button>
                </div>
                <div className="text-xs text-slate-700 leading-relaxed whitespace-pre-wrap">
                  {currentArtifact.content}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer Info */}
      <div className="p-2.5 border-t border-slate-200 bg-slate-50 text-[10px] text-slate-500 font-mono flex items-center justify-between">
        <span>Artifact ID: {currentArtifact?.artifact_id}</span>
        <span>Render Engine: Native SVG / ADK Telemetry</span>
      </div>
    </aside>
  );
};
