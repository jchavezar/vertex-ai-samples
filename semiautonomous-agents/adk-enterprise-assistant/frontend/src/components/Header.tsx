import React from 'react';
import { Sparkles, Shield, Cpu, Activity, PanelRightClose, PanelRightOpen, RefreshCw } from 'lucide-react';
import type { HealthStatus } from '../types';

interface HeaderProps {
  health: HealthStatus | null;
  sessionId: string;
  isStreaming: boolean;
  artifactCount: number;
  isArtifactPanelOpen: boolean;
  onToggleArtifactPanel: () => void;
  onNewSession: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  health,
  sessionId,
  isStreaming,
  artifactCount,
  isArtifactPanelOpen,
  onToggleArtifactPanel,
  onNewSession,
}) => {
  return (
    <header className="h-14 border-b border-slate-200 bg-white/90 backdrop-blur-md px-4 flex items-center justify-between sticky top-0 z-30 select-none">
      {/* Brand Identity */}
      <div className="flex items-center space-x-3 shrink-0">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-slate-900 via-indigo-950 to-cyan-600 flex items-center justify-center shadow-sm shrink-0">
          <Sparkles className="w-4 h-4 text-cyan-300" />
        </div>
        <div className="shrink-0">
          <div className="flex items-center space-x-2 whitespace-nowrap">
            <span className="font-semibold text-slate-900 text-sm tracking-tight">ADK Enterprise Assistant</span>
            <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-cyan-50 text-cyan-700 border border-cyan-200 shrink-0">
              Track 2
            </span>
          </div>
          <p className="text-[11px] text-slate-500 font-mono whitespace-nowrap">Google ADK 2.7 • Gemini 3.7 Flash</p>
        </div>
      </div>

      {/* Center Telemetry Badges */}
      <div className="hidden md:flex items-center space-x-2 shrink-0">
        {/* Model Badge */}
        <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-slate-50 border border-slate-200 text-xs text-slate-700 whitespace-nowrap shrink-0">
          <Cpu className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
          <span className="font-medium font-mono">{health?.model || 'gemini-3.7-flash'}</span>
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse shrink-0" />
        </div>

        {/* Runner Badge */}
        <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-slate-50 border border-slate-200 text-xs text-slate-700 whitespace-nowrap shrink-0">
          <Activity className="w-3.5 h-3.5 text-cyan-500 shrink-0" />
          <span className="text-slate-500">Runner:</span>
          <span className="font-medium font-mono">{health?.runner || 'InMemoryRunner'}</span>
        </div>

        {/* Security / Compliance */}
        <div className="flex items-center space-x-1 px-2 py-1 rounded-md bg-slate-50 border border-slate-200 text-[11px] text-slate-600 whitespace-nowrap shrink-0">
          <Shield className="w-3 h-3 text-slate-400 shrink-0" />
          <span>Zero-Leak Protocol</span>
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center space-x-2">
        {/* Session ID Pill */}
        <div className="hidden lg:block text-[11px] text-slate-600 bg-slate-50 border border-slate-200 px-2 py-1 rounded font-mono">
          sid: <span className="text-slate-800 font-medium">{sessionId.slice(0, 10)}...</span>
        </div>

        {/* Reset / New Session */}
        <button
          onClick={onNewSession}
          disabled={isStreaming}
          className="p-1.5 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-md transition-colors disabled:opacity-40 cursor-pointer"
          title="New Enterprise Session"
        >
          <RefreshCw className={`w-4 h-4 ${isStreaming ? 'animate-spin' : ''}`} />
        </button>

        {/* Artifact Preview Toggle */}
        <button
          onClick={onToggleArtifactPanel}
          className={`flex items-center space-x-1.5 px-2.5 py-1.5 rounded-md text-xs font-medium border transition-all cursor-pointer ${
            isArtifactPanelOpen
              ? 'bg-cyan-50 border-cyan-300 text-cyan-900 shadow-xs'
              : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
          }`}
        >
          {isArtifactPanelOpen ? (
            <PanelRightClose className="w-4 h-4 text-cyan-600" />
          ) : (
            <PanelRightOpen className="w-4 h-4 text-slate-500" />
          )}
          <span className="hidden sm:inline">Artifacts</span>
          {artifactCount > 0 && (
            <span className="px-1.5 py-0.2 rounded-full bg-cyan-600 text-white text-[10px] font-mono font-bold">
              {artifactCount}
            </span>
          )}
        </button>
      </div>
    </header>
  );
};
